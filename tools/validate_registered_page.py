"""Check central page retention and deployment admission. No page execution.

Online checks require Git and authenticated GitHub CLI access to the private
RateHighway/rlab-pages repository. Offline evidence never authorizes display.
"""
import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import stat
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
POLICY = 'RLAB-CENTRAL-ADMISSION-1'
REGISTRY = 'RateHighway/rlab-pages'
ID = re.compile(r'[A-Za-z0-9][A-Za-z0-9._-]{0,127}')
VERSION = re.compile(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)')
spec = importlib.util.spec_from_file_location(
    'rlab_browser_reference', ROOT / 'profiles/browser-readonly-0.2/tools/rlab.py')
BROWSER = importlib.util.module_from_spec(spec)
spec.loader.exec_module(BROWSER)


class RegistryError(ValueError):
    def __init__(self, code, message):
        self.code = code
        super().__init__(message)


def require(condition, code, message):
    if not condition:
        raise RegistryError(code, message)


def git(folder, *args):
    return subprocess.check_output(['git', '--no-replace-objects', '-C', str(folder), *args],
                                   stderr=subprocess.DEVNULL)


def verify_remote_head():
    """Use authenticated official GitHub API provenance, not an origin label."""
    result = subprocess.check_output(
        ['gh', 'api', '--hostname', 'github.com',
         f'repos/{REGISTRY}/git/ref/heads/master'], stderr=subprocess.DEVNULL)
    sha = json.loads(result)['object']['sha']
    require(re.fullmatch(r'[a-f0-9]{40}', sha), 'REG001', 'Invalid official registry revision')
    runs = json.loads(subprocess.check_output(
        ['gh', 'api', '--hostname', 'github.com',
         f'repos/{REGISTRY}/actions/workflows/registry-check.yml/runs?head_sha={sha}&event=push&per_page=100'],
        stderr=subprocess.DEVNULL))['workflow_runs']
    matching = [run for run in runs if run.get('head_sha') == sha and
                run.get('head_branch') == 'master' and run.get('event') == 'push']
    require(matching, 'REG001', 'Current registry revision has no policy audit run')
    latest = max(matching, key=lambda run: (run['id'], run.get('run_attempt', 1)))
    require(latest.get('status') == 'completed' and latest.get('conclusion') == 'success',
            'REG001', 'Current registry revision has not passed its latest policy audit')
    return sha


def committed_blob(folder, commit, name, maximum):
    key = f'{commit}:{name}'
    try:
        size = int(git(folder, 'cat-file', '-s', key))
        require(size <= maximum, 'REG002', 'Committed registry content exceeds its limit')
        return git(folder, 'show', key)
    except subprocess.CalledProcessError:
        raise RegistryError('REG002', 'Required committed registry content is missing') from None


def record(folder, commit, name, schema):
    value = BROWSER.parse_json(committed_blob(folder, commit, name, 262144))
    BROWSER.schema_check(value, BROWSER.load_json(ROOT / 'schemas' / schema))
    return value


def utc(value):
    result = datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
    return result


def registry_head(registry):
    require(Path(git(registry, 'rev-parse', '--show-toplevel').decode().strip()).resolve() == registry,
            'REG001', 'Registry must be a dedicated Git checkout')
    origin = git(registry, 'remote', 'get-url', 'origin').decode().strip()
    require(origin in (f'https://github.com/{REGISTRY}', f'https://github.com/{REGISTRY}.git'),
            'REG001', 'Registry origin is not the central RateHighway repository')
    require(not git(registry, 'status', '--porcelain', '--untracked-files=all').strip(),
            'REG001', 'Registry checkout has uncommitted changes')
    return git(registry, 'rev-parse', 'HEAD').decode().strip()


def archive_manifest(data):
    """Inspect bounded ZIP contents without extraction or execution."""
    require(len(data) <= 25000000, 'REG004', 'Archive exceeds the compressed-size limit')
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        entries = archive.infolist()
        require(len(entries) <= 2000, 'REG004', 'Archive has too many entries')
        require(len({i.filename.casefold() for i in entries}) == len(entries),
                'REG004', 'Archive has duplicate or colliding entries')
        require(sum(i.file_size for i in entries) <= 100000000,
                'REG004', 'Archive exceeds the expanded-size limit')
        for info in entries:
            BROWSER.safe_path(info.filename.rstrip('/'))
            kind = stat.S_IFMT(info.external_attr >> 16)
            require(kind in (0, stat.S_IFDIR if info.is_dir() else stat.S_IFREG),
                    'REG004', 'Archive contains a link or special entry')
            require(info.file_size <= 25000000 and not info.flag_bits & 1,
                    'REG004', 'Archive contains an oversized or encrypted entry')
        entry = archive.getinfo('rlab-page.json')
        require(entry.file_size <= 262144, 'REG004', 'Manifest exceeds its size limit')
        require(archive.testzip() is None, 'REG004', 'Archive failed its CRC check')
        return BROWSER.parse_json(archive.read(entry))


def validate(package, registry, host_id, deployment_id, context, purpose='display', offline=False, _audit=False):
    result = {'centralPolicy': POLICY, 'status': 'admission-denied',
              'purpose': purpose, 'admissionEligible': False, 'designReviewEligible': False,
              'registryRepository': REGISTRY, 'remoteVerified': False,
              'runtimeExecuted': False, 'errors': [],
              'notPerformed': ['Host rendering/isolation and business authorization',
                               'Source-to-package reproducible-build proof',
                               'Full declarative design checks', 'Certification assessment']}
    try:
        require(purpose in ('display', 'design-review'), 'REG007', 'Unsupported purpose')
        require(ID.fullmatch(host_id) and ID.fullmatch(deployment_id),
                'REG007', 'Invalid host or deployment identifier')
        if not _audit:
            require(isinstance(context, dict) and set(context) == {'hostRelease', 'environment', 'route', 'slot'},
                    'REG007', 'Actual host release, environment, route and slot are required')
        registry = Path(registry).resolve()
        commit = registry_head(registry)
        result['registryCommit'] = commit
        if not offline and not _audit:
            require(commit == verify_remote_head(), 'REG001', 'Registry checkout is not the current official revision')
            result['remoteVerified'] = True
            verified_at = datetime.now(timezone.utc)
        package = Path(package)
        require(package.stat().st_size <= 25000000, 'REG004', 'Package exceeds its size limit')
        data = package.read_bytes()
        manifest = archive_manifest(data)
        page_id, version = manifest['id'], manifest['version']
        require(ID.fullmatch(page_id) and VERSION.fullmatch(version), 'REG004', 'Invalid package identity')
        profile = manifest['profile']
        if profile == 'RLAB-PAGE-READONLY-0.2':
            require(manifest['delivery']['mode'] == 'bundle', 'REG010',
                    'Central admission requires bundled page code; remote delivery is not digest-bound')
            with tempfile.TemporaryDirectory(prefix='rlab-registration-package-') as tmp:
                frozen = Path(tmp) / 'page.rlab'
                frozen.write_bytes(data)
                require(BROWSER.validate(frozen)['status'] == 'offline-passed',
                        'REG010', 'Browser package failed its offline checks')
        elif profile == 'RLAB-DECLARATIVE-DESIGN-0.3':
            BROWSER.schema_check(manifest, BROWSER.load_json(
                ROOT / 'profiles/declarative-design-0.3/schemas/manifest.schema.json'))
            require(purpose == 'design-review', 'REG009', 'The declarative profile is design-only and cannot be admitted for display')
        else:
            raise RegistryError('REG010', 'Unsupported package profile')
        registration = record(registry, commit, f'registrations/{page_id}/{version}.json',
                              'registration-record.schema.json')
        sha = hashlib.sha256(data).hexdigest()
        result.update(pageId=page_id, pageVersion=version, packageSha256=sha)
        require(all(registration[k] == manifest[v] for k, v in
                    [('pageId', 'id'), ('pageVersion', 'version'), ('profile', 'profile'),
                     ('standardVersion', 'standardVersion')]), 'REG004', 'Registration identity does not match the package')
        if not _audit:
            require(registration['status'] == 'registered' and host_id in registration['allowedHosts'],
                    'REG006', 'Registration is revoked or does not allow this host')
        require(registration['packageSha256'] == sha and registration['packagePath'] == f'packages/{sha}.rlab',
                'REG004', 'Package bytes do not match the central registration')
        central_package = committed_blob(registry, commit, registration['packagePath'], 25000000)
        require(hashlib.sha256(central_package).hexdigest() == sha,
                'REG004', 'Central package is missing or has different bytes')
        source_sha = registration['sourceSha256']
        require(registration['sourcePath'] == f'sources/{source_sha}.zip',
                'REG005', 'Source path is not bound to its digest')
        source = committed_blob(registry, commit, registration['sourcePath'], 25000000)
        require(hashlib.sha256(source).hexdigest() == source_sha,
                'REG005', 'Central source archive does not match its digest')
        source_manifest = archive_manifest(source)
        require(all(source_manifest[k] == manifest[k] for k in ('id', 'version', 'profile', 'standardVersion')),
                'REG005', 'Source snapshot identity does not match the package')
        utc(registration['registeredAt'])
        if _audit:
            result['status'] = 'registration-audited'
            return result
        deployment = record(registry, commit, f'deployments/{deployment_id}.json', 'deployment-record.schema.json')
        require(all(deployment[k] == value for k, value in
                    [('deploymentId', deployment_id), ('pageId', page_id), ('pageVersion', version),
                     ('packageSha256', sha), ('hostId', host_id), ('purpose', purpose)]) and
                deployment['status'] == 'active' and deployment['approval'] == 'approved',
                'REG007', 'Deployment is unapproved, inactive or bound to different content or host')
        require(context['hostRelease'] == deployment['hostRelease'] and
                context['environment'] == deployment['environment'] and
                context['route'] == deployment['placement']['route'] and
                context['slot'] == deployment['placement']['slot'],
                'REG007', 'Actual host release, environment or placement differs from the approved deployment')
        reported, expiry = utc(deployment['reportedAt']), utc(deployment['leaseExpiresAt'])
        now = datetime.now(timezone.utc)
        require(reported <= now + timedelta(minutes=5) and reported < expiry <= reported + timedelta(hours=24)
                and now < expiry, 'REG008', 'Deployment report or lease is invalid or expired')
        result.update(hostId=host_id, hostRelease=deployment['hostRelease'], deploymentId=deployment_id,
                      environment=deployment['environment'], placement=deployment['placement'],
                      leaseExpiresAt=deployment['leaseExpiresAt'])
        if offline:
            result['status'] = 'registry-evidence-checked'
        elif purpose == 'design-review':
            result.update(status='registered-design-checked', designReviewEligible=True,
                          checkedAt=verified_at.strftime('%Y-%m-%dT%H:%M:%SZ'))
        else:
            deadline = min(verified_at + timedelta(minutes=15), expiry)
            require(datetime.now(timezone.utc) < deadline, 'REG008', 'Registry admission check has expired')
            result.update(status='admission-checked', admissionEligible=True,
                          checkedAt=verified_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
                          admissionExpiresAt=deadline.strftime('%Y-%m-%dT%H:%M:%SZ'))
    except RegistryError as error:
        result['errors'].append({'code': error.code, 'message': str(error)})
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, subprocess.CalledProcessError,
            zipfile.BadZipFile, BROWSER.Invalid) as error:
        result['errors'].append({'code': 'REG000', 'message': 'Central validation failed: ' + type(error).__name__})
    return result


def audit_registry(registry):
    """Audit committed retention evidence and inventory, never authorize display."""
    result = {'centralPolicy': POLICY, 'status': 'registry-audit-failed',
              'admissionEligible': False, 'remoteVerified': False, 'runtimeExecuted': False,
              'registrations': 0, 'deployments': 0, 'errors': []}
    try:
        registry = Path(registry).resolve()
        commit = registry_head(registry)
        result['registryCommit'] = commit
        files = git(registry, 'ls-tree', '-r', '--name-only', commit).decode().splitlines()
        registrations = {}
        with tempfile.TemporaryDirectory(prefix='rlab-registry-audit-') as tmp:
            for name in files:
                if not name.startswith('registrations/') or not name.endswith('.json'):
                    continue
                item = record(registry, commit, name, 'registration-record.schema.json')
                require(name == f"registrations/{item['pageId']}/{item['pageVersion']}.json",
                        'REG003', 'Registration filename does not match its identity')
                package = Path(tmp) / 'page.rlab'
                package.write_bytes(committed_blob(registry, commit, item['packagePath'], 25000000))
                check = validate(package, registry, 'audit', 'audit', {}, 'design-review', True, _audit=True)
                require(not check['errors'], 'REG003', 'A retained registration failed validation')
                registrations[(item['pageId'], item['pageVersion'])] = item
                result['registrations'] += 1
        for name in files:
            if not name.startswith('deployments/') or not name.endswith('.json'):
                continue
            item = record(registry, commit, name, 'deployment-record.schema.json')
            require(name == f"deployments/{item['deploymentId']}.json",
                    'REG003', 'Deployment filename does not match its identity')
            page = registrations.get((item['pageId'], item['pageVersion']))
            require(page is not None and item['packageSha256'] == page['packageSha256'],
                    'REG007', 'Deployment references an absent or different package')
            reported, expiry = utc(item['reportedAt']), utc(item['leaseExpiresAt'])
            require(reported < expiry <= reported + timedelta(hours=24),
                    'REG008', 'Deployment lease duration is invalid')
            require(not (item['purpose'] == 'display' and page['profile'] == 'RLAB-DECLARATIVE-DESIGN-0.3'),
                    'REG009', 'Design-only page cannot be recorded for display')
            result['deployments'] += 1
        result['status'] = 'registry-audited'
    except RegistryError as error:
        result['errors'].append({'code': error.code, 'message': str(error)})
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, subprocess.CalledProcessError,
            zipfile.BadZipFile, BROWSER.Invalid) as error:
        result['errors'].append({'code': 'REG000', 'message': 'Registry audit failed: ' + type(error).__name__})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package', type=Path, nargs='?')
    parser.add_argument('--registry', required=True, type=Path)
    parser.add_argument('--host-id')
    parser.add_argument('--deployment-id')
    parser.add_argument('--host-release')
    parser.add_argument('--environment', choices=('development', 'staging', 'production'))
    parser.add_argument('--route')
    parser.add_argument('--slot')
    parser.add_argument('--purpose', choices=('display', 'design-review'), default='display')
    parser.add_argument('--offline', action='store_true', help='Evidence only; cannot authorize admission')
    parser.add_argument('--audit-registry', action='store_true', help='Audit retention and inventory only; cannot authorize admission')
    args = parser.parse_args()
    if args.audit_registry:
        if any((args.package, args.host_id, args.deployment_id, args.host_release,
                args.environment, args.route, args.slot)):
            parser.error('--audit-registry cannot be combined with a package or deployment request')
        result = audit_registry(args.registry)
    else:
        if not all((args.package, args.host_id, args.deployment_id, args.host_release,
                    args.environment, args.route, args.slot)):
            parser.error('A package and all actual host, deployment, release, environment and placement arguments are required')
        context = {'hostRelease': args.host_release, 'environment': args.environment,
                   'route': args.route, 'slot': args.slot}
        result = validate(args.package, args.registry, args.host_id, args.deployment_id,
                          context, args.purpose, args.offline)
    print(json.dumps(result, indent=2))
    if result['errors']:
        return 1
    return 2 if args.offline and not args.audit_registry else 0


if __name__ == '__main__':
    raise SystemExit(main())
