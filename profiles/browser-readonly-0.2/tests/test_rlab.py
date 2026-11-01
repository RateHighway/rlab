import copy
import importlib.util
import json
import pathlib
import stat
import tempfile
import unittest
import warnings
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('rlab', ROOT / 'tools/rlab.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = pathlib.Path(self.tmp.name) / 'test.rlab'
        self.manifest = r.load_json(ROOT / 'examples/fleet-pressure/rlab-page.json')
        self.host = r.load_json(ROOT / 'examples/host-capabilities.json')

    def tearDown(self):
        self.tmp.cleanup()

    def run_package(self, mutate=None, extras=None, omit=None, manifest_bytes=None, host=None):
        m = copy.deepcopy(self.manifest)
        if mutate:
            mutate(m)
        files = {'rlab-page.json': manifest_bytes or json.dumps(m).encode(),
                 'app/index.html': b'<!doctype html><title>Fixture</title>',
                 'LICENSE.txt': b'Fixture rights unspecified'}
        if omit:
            files.pop(omit)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            with zipfile.ZipFile(str(self.path), 'w', zipfile.ZIP_DEFLATED) as z:
                for k, v in files.items(): z.writestr(k, v)
                for k, v in (extras or []): z.writestr(k, v)
        return r.validate(self.path, self.host if host is None else host)

    def bad(self, result, code=None):
        self.assertEqual(result['status'], 'invalid')
        if code: self.assertEqual(result['errors'][0]['code'], code)

    def test_valid(self):
        out = self.run_package()
        self.assertEqual(out['status'], 'offline-passed')
        self.assertEqual(len(out['sha256']), 64)
        self.assertTrue(out['notPerformed'])

    def test_missing_manifest(self): self.bad(self.run_package(omit='rlab-page.json'), 'RL001')
    def test_bad_json(self): self.bad(self.run_package(manifest_bytes=b'{'), 'RL011')
    def test_duplicate_json_key(self): self.bad(self.run_package(manifest_bytes=b'{"id":1,"id":2}'), 'RL002')
    def test_unknown_field(self): self.bad(self.run_package(lambda m:m.update(certified=True)), 'RL002')
    def test_wrong_standard(self): self.bad(self.run_package(lambda m:m.update(standard='vibe.page')), 'RL002')
    def test_wrong_version(self): self.bad(self.run_package(lambda m:m.update(version='01.0.0')), 'RL002')
    def test_missing_entry(self): self.bad(self.run_package(omit='app/index.html'), 'RL004')
    def test_write_scope(self): self.bad(self.run_package(lambda m:m['permissions']['requested'].append('rates.execute')), 'RL002')
    def test_unknown_read(self): self.bad(self.run_package(lambda m:m['permissions']['requested'].append('secrets.read')), 'RL002')
    def test_required_not_requested(self): self.bad(self.run_package(lambda m:m['permissions']['required'].append('utilization.read')), 'RL006')
    def test_context_overlap(self): self.bad(self.run_package(lambda m:m['context']['optional'].append('environment')), 'RL002')
    def test_traversal(self): self.bad(self.run_package(extras=[('../escape.txt',b'x')]), 'RL003')
    def test_absolute(self): self.bad(self.run_package(extras=[('/escape.txt',b'x')]), 'RL003')
    def test_backslash(self):
        # Windows ZIP writers normalise separators; mutate both stored names
        # to test a real unsafe incoming archive rather than a repaired fixture.
        self.run_package(extras=[('app/escape.txt',b'x')])
        self.path.write_bytes(self.path.read_bytes().replace(b'app/escape.txt',b'app\\escape.txt'))
        self.bad(r.validate(self.path,self.host), 'RL003')
    def test_device(self): self.bad(self.run_package(extras=[('app/CON.txt',b'x')]), 'RL003')
    def test_case_collision(self): self.bad(self.run_package(extras=[('APP/INDEX.HTML',b'x')]), 'RL003')
    def test_duplicate_entry(self): self.bad(self.run_package(extras=[('rlab-page.json',b'{}')]), 'RL003')
    def test_file_dir_collision(self): self.bad(self.run_package(extras=[('LICENSE.txt/child.txt',b'x')]), 'RL003')
    def test_nested_manifest(self): self.bad(self.run_package(extras=[('app/rlab-page.json',b'{}')]), 'RL001')
    def test_symlink(self):
        z = zipfile.ZipInfo('app/link.txt'); z.create_system=3
        z.external_attr=(stat.S_IFLNK | 0o777) << 16
        self.bad(self.run_package(extras=[(z,b'/etc/passwd')]), 'RL003')
    def test_nested_archive(self): self.bad(self.run_package(extras=[('app/a.txt',b'PK\x03\x04data')]), 'RL008')
    def test_private_key(self): self.bad(self.run_package(extras=[('app/key.txt',b'-----BEGIN PRIVATE KEY-----')]), 'RL008')
    def test_server_file(self): self.bad(self.run_package(extras=[('app/server.py',b'print(1)')]), 'RL008')
    def test_dynamic_eval(self): self.bad(self.run_package(extras=[('app/a.js',b'eval("x")')]), 'RL008')
    def test_service_worker(self): self.bad(self.run_package(extras=[('app/a.js',b'navigator.serviceWorker.register("sw.js")')]), 'RL008')
    def test_wildcard(self): self.bad(self.run_package(lambda m:m['network']['connect'].append('https://*.example.com')), 'RL002')
    def test_url_userinfo(self): self.bad(self.run_package(lambda m:m['network']['connect'].append('https://a@evil.example')), 'RL005')
    def test_origin_trailing_slash(self): self.bad(self.run_package(lambda m:m['network']['connect'].append('https://example.com/')), 'RL002')
    def test_network_disclosure(self): self.bad(self.run_package(lambda m:m['network']['connect'].append('https://example.com')), 'RL002')
    def test_license_reference(self): self.bad(self.run_package(omit='LICENSE.txt'), 'RL002')
    def test_remote_origin_mismatch(self): self.bad(self.run_package(lambda m:m.update(delivery={'mode':'remote','url':'https://one.example/v1/index.html','origin':'https://two.example'})), 'RL005')
    def test_remote_valid_structurally(self):
        self.host['deliveryModes'].append('remote')
        out=self.run_package(lambda m:m.update(delivery={'mode':'remote','url':'https://one.example/v1/index.html','origin':'https://one.example'}))
        self.assertEqual(out['status'],'offline-passed')
        self.assertTrue(any('Remote' in w for w in out['warnings']))
    def test_incompatible_host(self):
        self.host['hostApiVersion']='0.3.0'; self.bad(self.run_package(), 'RL007')
    def test_missing_required_scope(self):
        self.host['permissions']=[]; self.bad(self.run_package(), 'RL007')
    def test_missing_required_context(self):
        self.host['contextKeys']=[]; self.bad(self.run_package(), 'RL007')
    def test_missing_service(self):
        self.bad(self.run_package(lambda m:m['services'].append({'id':'org.example.fleet','minimum':'1.0.0','maximumExclusive':'2.0.0','required':True})), 'RL007')
    def test_optional_scope(self):
        self.assertEqual(self.run_package(lambda m:m['permissions']['requested'].append('utilization.read'))['status'],'offline-passed')
    def test_lower_host_limit(self):
        self.host['limits']['entries']=2; self.bad(self.run_package(), 'RL007')
    def test_manifest_size(self): self.bad(self.run_package(manifest_bytes=b' ' * 262145), 'RL011')
    def test_nonfinite(self): self.bad(self.run_package(manifest_bytes=b'{"x": NaN}'), 'RL002')
    def test_pack_sample(self):
        out=r.pack(ROOT/'examples/fleet-pressure',self.path)
        self.assertEqual(out['status'],'offline-passed')
        self.assertEqual(r.validate(self.path,self.host)['status'],'offline-passed')
    def test_packer_preserves_existing_output(self):
        self.path.write_bytes(b'preserve')
        with self.assertRaises(ValueError): r.pack(ROOT/'examples/fleet-pressure',self.path)
        self.assertEqual(self.path.read_bytes(),b'preserve')


if __name__ == '__main__': unittest.main()
