"""Central retention, provenance, revocation, deployment and lease checks."""
from datetime import datetime, timedelta, timezone
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import validate_registered_page as gate


def stamp(value):
    return value.strftime('%Y-%m-%dT%H:%M:%SZ')


class RegistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.assets = tempfile.TemporaryDirectory()
        cls.package = Path(cls.assets.name) / 'page.rlab'
        report = gate.BROWSER.pack(
            ROOT / 'profiles/browser-readonly-0.2/examples/fleet-pressure', cls.package)
        assert report['status'] == 'offline-passed'
        cls.browser_bytes = cls.package.read_bytes()
        output = io.BytesIO()
        folder = ROOT / 'profiles/declarative-design-0.3/examples/level-1'
        with zipfile.ZipFile(output, 'w') as archive:
            for path in folder.rglob('*'):
                if path.is_file():
                    archive.writestr(path.relative_to(folder).as_posix(), path.read_bytes())
        cls.design_bytes = output.getvalue()

    @classmethod
    def tearDownClass(cls):
        cls.assets.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.registry = Path(self.temp.name) / 'registry'
        self.registry.mkdir()
        self.git('init', '-b', 'master')
        self.git('remote', 'add', 'origin', 'https://github.com/RateHighway/rlab-pages.git')
        self.context = {'hostRelease': '0.1.0', 'environment': 'development',
                        'route': '/fleet', 'slot': 'workspace'}
        self.install(self.browser_bytes)

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.registry), *args],
                                       stderr=subprocess.DEVNULL)

    def commit(self):
        self.git('add', '--all')
        self.git('-c', 'user.name=Registry Fixture', '-c', 'user.email=fixture@example.com',
                 'commit', '-m', 'Synthetic registry fixture')
        return self.git('rev-parse', 'HEAD').decode().strip()

    def save(self, path, value):
        path = self.registry / path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding='utf-8')

    def install(self, data, profile=None):
        self.input = Path(self.temp.name) / 'input.rlab'
        self.input.write_bytes(data)
        manifest = gate.archive_manifest(data)
        self.sha = hashlib.sha256(data).hexdigest()
        (self.registry / 'packages').mkdir(exist_ok=True)
        (self.registry / 'sources').mkdir(exist_ok=True)
        (self.registry / f'packages/{self.sha}.rlab').write_bytes(data)
        (self.registry / f'sources/{self.sha}.zip').write_bytes(data)
        now = datetime.now(timezone.utc).replace(microsecond=0)
        self.registration = {
            'recordVersion': 1, 'pageId': manifest['id'], 'pageVersion': manifest['version'],
            'profile': manifest['profile'], 'standardVersion': manifest['standardVersion'],
            'packagePath': f'packages/{self.sha}.rlab', 'packageSha256': self.sha,
            'sourcePath': f'sources/{self.sha}.zip', 'sourceSha256': self.sha,
            'status': 'registered', 'allowedHosts': ['com.example.host'], 'registeredAt': stamp(now),
        }
        self.registration_path = f"registrations/{manifest['id']}/{manifest['version']}.json"
        self.deployment = {
            'recordVersion': 1, 'deploymentId': 'com.example.host.fleet',
            'pageId': manifest['id'], 'pageVersion': manifest['version'],
            'packageSha256': self.sha, 'hostId': 'com.example.host', 'hostRelease': '0.1.0',
            'applicationName': 'Example Rental App', 'environment': 'development',
            'placement': {'route': '/fleet', 'slot': 'workspace'}, 'purpose': 'display',
            'status': 'active', 'approval': 'approved', 'reportedAt': stamp(now),
            'leaseExpiresAt': stamp(now + timedelta(hours=2)),
        }
        self.save(self.registration_path, self.registration)
        self.save('deployments/com.example.host.fleet.json', self.deployment)
        self.commit()

    def check(self, **kwargs):
        current = self.git('rev-parse', 'HEAD').decode().strip()
        with patch.object(gate, 'verify_remote_head', return_value=current):
            return gate.validate(self.input, self.registry, 'com.example.host',
                                 'com.example.host.fleet', kwargs.pop('context', self.context), **kwargs)

    def change_registration(self, **changes):
        self.registration.update(changes)
        self.save(self.registration_path, self.registration)
        self.commit()

    def change_deployment(self, **changes):
        self.deployment.update(changes)
        self.save('deployments/com.example.host.fleet.json', self.deployment)
        self.commit()

    def assert_denied(self, report, code=None):
        self.assertFalse(report['admissionEligible'])
        self.assertTrue(report['errors'])
        if code:
            self.assertEqual(report['errors'][0]['code'], code)

    def test_current_registered_package_and_approved_deployment(self):
        result = self.check()
        self.assertEqual(result['status'], 'admission-checked')
        self.assertTrue(result['admissionEligible'])
        self.assertTrue(result['remoteVerified'])
        self.assertEqual(result['placement'], {'route': '/fleet', 'slot': 'workspace'})
        self.assertLessEqual(gate.utc(result['admissionExpiresAt']),
                             gate.utc(result['checkedAt']) + timedelta(minutes=15))

    def test_admission_deadline_cannot_exceed_deployment_lease(self):
        self.change_deployment(leaseExpiresAt=stamp(datetime.now(timezone.utc) + timedelta(minutes=5)))
        result = self.check()
        self.assertTrue(result['admissionEligible'])
        self.assertEqual(result['admissionExpiresAt'], self.deployment['leaseExpiresAt'])

    def test_offline_evidence_never_grants_admission(self):
        with patch.object(gate, 'verify_remote_head', side_effect=AssertionError('network called')):
            result = gate.validate(self.input, self.registry, 'com.example.host',
                                   'com.example.host.fleet', self.context, offline=True)
        self.assertEqual(result['status'], 'registry-evidence-checked')
        self.assertFalse(result['admissionEligible'])
        self.assertFalse(result['remoteVerified'])

    def test_wrong_origin_is_rejected(self):
        self.git('remote', 'set-url', 'origin', 'https://github.com/example/fake-registry.git')
        self.assert_denied(self.check(), 'REG001')

    def test_origin_label_does_not_prove_current_remote(self):
        with patch.object(gate, 'verify_remote_head', return_value='0' * 40):
            report = gate.validate(self.input, self.registry, 'com.example.host', 'com.example.host.fleet', self.context)
        self.assert_denied(report, 'REG001')

    def test_unavailable_official_registry_fails_closed(self):
        with patch.object(gate, 'verify_remote_head', side_effect=OSError('offline')):
            result = gate.validate(self.input, self.registry, 'com.example.host', 'com.example.host.fleet', self.context)
        self.assert_denied(result)

    def test_dirty_registry_is_not_admissible(self):
        self.save(self.registration_path, self.registration)
        (self.registry / 'uncommitted.txt').write_text('unreviewed', encoding='utf-8')
        self.assert_denied(self.check(), 'REG001')

    def test_local_git_replace_cannot_forge_authoritative_registration(self):
        self.change_registration(allowedHosts=[])
        official = self.git('rev-parse', 'HEAD').decode().strip()
        self.change_registration(allowedHosts=['com.example.host'])
        forged = self.git('rev-parse', 'HEAD').decode().strip()
        self.git('replace', official, forged)
        self.git('reset', '--hard', official)
        authoritative = gate.BROWSER.parse_json(gate.committed_blob(
            self.registry, official, self.registration_path, 262144))
        self.assertEqual(authoritative['allowedHosts'], [])
        self.assert_denied(self.check())

    def test_revoked_registration(self):
        self.change_registration(status='revoked')
        self.assert_denied(self.check(), 'REG006')

    def test_empty_allowed_hosts_is_not_approval(self):
        self.change_registration(allowedHosts=[])
        self.assert_denied(self.check(), 'REG006')

    def test_missing_registration(self):
        self.git('rm', self.registration_path)
        self.commit()
        self.assert_denied(self.check(), 'REG002')

    def test_registration_digest_mismatch(self):
        self.change_registration(packageSha256='0' * 64)
        self.assert_denied(self.check(), 'REG004')

    def test_source_archive_is_required(self):
        self.git('rm', self.registration['sourcePath'])
        self.commit()
        self.assert_denied(self.check(), 'REG002')

    def test_source_manifest_identity_is_bound(self):
        with zipfile.ZipFile(io.BytesIO(self.browser_bytes)) as original:
            contents = {i.filename: original.read(i) for i in original.infolist()}
        manifest = json.loads(contents['rlab-page.json'])
        manifest['version'] = '9.9.9'
        contents['rlab-page.json'] = json.dumps(manifest).encode()
        output = io.BytesIO()
        with zipfile.ZipFile(output, 'w') as archive:
            for name, data in contents.items():
                archive.writestr(name, data)
        source = output.getvalue()
        source_sha = hashlib.sha256(source).hexdigest()
        (self.registry / f'sources/{source_sha}.zip').write_bytes(source)
        self.change_registration(sourcePath=f'sources/{source_sha}.zip', sourceSha256=source_sha)
        self.assert_denied(self.check(), 'REG005')

    def test_unknown_record_field_is_rejected(self):
        self.change_registration(automaticallyApproved=True)
        self.assert_denied(self.check())

    def test_pending_approval_is_not_admissible(self):
        self.change_deployment(approval='pending')
        self.assert_denied(self.check(), 'REG007')

    def test_deployment_host_and_digest_are_bound(self):
        self.change_deployment(hostId='com.example.other')
        self.assert_denied(self.check(), 'REG007')

    def test_actual_route_must_match_approved_placement(self):
        self.assert_denied(self.check(context=dict(self.context, route='/elsewhere')), 'REG007')

    def test_actual_slot_must_match_approved_placement(self):
        self.assert_denied(self.check(context=dict(self.context, slot='sidebar')), 'REG007')

    def test_actual_environment_must_match_approved_deployment(self):
        self.assert_denied(self.check(context=dict(self.context, environment='production')), 'REG007')

    def test_actual_host_release_must_match_approved_deployment(self):
        self.assert_denied(self.check(context=dict(self.context, hostRelease='2.0.0')), 'REG007')

    def test_missing_actual_context_cannot_be_inferred(self):
        self.assert_denied(self.check(context={}), 'REG007')

    def test_expired_deployment_lease_is_rejected(self):
        now = datetime.now(timezone.utc)
        self.change_deployment(reportedAt=stamp(now - timedelta(hours=2)),
                               leaseExpiresAt=stamp(now - timedelta(hours=1)))
        self.assert_denied(self.check(), 'REG008')

    def test_long_or_future_lease_is_rejected(self):
        now = datetime.now(timezone.utc)
        self.change_deployment(leaseExpiresAt=stamp(now + timedelta(days=2)))
        self.assert_denied(self.check(), 'REG008')

    def test_future_report_is_rejected(self):
        now = datetime.now(timezone.utc)
        self.change_deployment(reportedAt=stamp(now + timedelta(hours=1)),
                               leaseExpiresAt=stamp(now + timedelta(hours=2)))
        self.assert_denied(self.check(), 'REG008')

    def test_design_only_cannot_be_admitted_for_display(self):
        self.install(self.design_bytes)
        self.assert_denied(self.check(), 'REG009')

    def test_remote_delivery_cannot_be_admitted_even_if_registered(self):
        with zipfile.ZipFile(io.BytesIO(self.browser_bytes)) as original:
            contents = {i.filename: original.read(i) for i in original.infolist()}
        manifest = json.loads(contents['rlab-page.json'])
        manifest['delivery'] = {'mode': 'remote', 'url': 'https://one.example/v1/index.html',
                                'origin': 'https://one.example'}
        contents['rlab-page.json'] = json.dumps(manifest).encode()
        output = io.BytesIO()
        with zipfile.ZipFile(output, 'w') as archive:
            for name, data in contents.items():
                archive.writestr(name, data)
        self.install(output.getvalue())
        self.assert_denied(self.check(), 'REG010')

    def test_registered_design_review_never_grants_display(self):
        self.install(self.design_bytes)
        self.change_deployment(purpose='design-review')
        report = self.check(purpose='design-review')
        self.assertEqual(report['status'], 'registered-design-checked')
        self.assertFalse(report['admissionEligible'])
        self.assertTrue(report['designReviewEligible'])

    def test_audit_allows_unapproved_reference_and_expired_inventory(self):
        now = datetime.now(timezone.utc)
        self.change_registration(allowedHosts=[], status='revoked')
        self.change_deployment(status='disabled', approval='denied',
                               reportedAt=stamp(now - timedelta(days=2)),
                               leaseExpiresAt=stamp(now - timedelta(days=1, hours=12)))
        report = gate.audit_registry(self.registry)
        self.assertEqual(report['status'], 'registry-audited')
        self.assertEqual((report['registrations'], report['deployments']), (1, 1))
        self.assertFalse(report['admissionEligible'])

    def test_audit_detects_missing_source_without_host_grants(self):
        self.change_registration(allowedHosts=[])
        self.git('rm', self.registration['sourcePath'])
        self.commit()
        report = gate.audit_registry(self.registry)
        self.assertTrue(report['errors'])
        self.assertFalse(report['admissionEligible'])


class OfficialHeadTests(unittest.TestCase):
    sha = 'a' * 40

    def verify(self, runs):
        payloads = [json.dumps({'object': {'sha': self.sha}}).encode(),
                    json.dumps({'workflow_runs': runs}).encode()]
        with patch.object(gate.subprocess, 'check_output', side_effect=payloads):
            return gate.verify_remote_head()

    def run_record(self, **changes):
        value = {'id': 1, 'head_sha': self.sha, 'head_branch': 'master', 'event': 'push',
                 'status': 'completed', 'conclusion': 'success', 'run_attempt': 1}
        value.update(changes)
        return value

    def test_current_head_with_successful_policy_audit(self):
        self.assertEqual(self.verify([self.run_record()]), self.sha)

    def test_missing_policy_audit_is_denied(self):
        with self.assertRaises(gate.RegistryError):
            self.verify([])

    def test_pending_or_failed_policy_audit_is_denied(self):
        for changes in ({'status': 'in_progress', 'conclusion': None}, {'conclusion': 'failure'}):
            with self.subTest(changes=changes), self.assertRaises(gate.RegistryError):
                self.verify([self.run_record(**changes)])

    def test_other_revision_or_event_cannot_supply_audit(self):
        for changes in ({'head_sha': 'b' * 40}, {'head_branch': 'other'}, {'event': 'pull_request'}):
            with self.subTest(changes=changes), self.assertRaises(gate.RegistryError):
                self.verify([self.run_record(**changes)])

    def test_latest_failed_attempt_blocks_older_success(self):
        with self.assertRaises(gate.RegistryError):
            self.verify([self.run_record(), self.run_record(id=2, conclusion='failure')])


if __name__ == '__main__':
    unittest.main()
