import copy
import struct
import importlib.util
import json
import pathlib
import stat
import tempfile
import unittest
import warnings
import zipfile
import zlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('rlab', ROOT / 'tools/rlab.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


def png(width, height, padding=0):
    """A real, blank RGB PNG made with the standard library."""
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data))
    rows = (b'\x00' + b'\xff' * (width * 3)) * height
    body = (chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(rows, 9)))
    if padding:
        body += chunk(b'tEXt', b'Comment\x00' + b'x' * padding)
    return b'\x89PNG\r\n\x1a\n' + body + chunk(b'IEND', b'')


def webp_header(width, height):
    """WebP VP8X header fixture: enough for the size check, not a decodable image."""
    payload = (b'VP8X' + struct.pack('<I', 10) + b'\x00' * 4
               + (width - 1).to_bytes(3, 'little') + (height - 1).to_bytes(3, 'little'))
    return b'RIFF' + struct.pack('<I', 4 + len(payload)) + b'WEBP' + payload


MOCKUP, THUMB = png(1600, 900), png(640, 360)


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = pathlib.Path(self.tmp.name) / 'test.rlab'
        self.manifest = r.load_json(ROOT / 'examples/group-manager/rlab-page.json')
        self.host = r.load_json(ROOT / 'examples/host-capabilities.json')

    def tearDown(self):
        self.tmp.cleanup()

    def run_package(self, mutate=None, extras=None, omit=None, manifest_bytes=None, host=None, replace=None):
        m = copy.deepcopy(self.manifest)
        if mutate:
            mutate(m)
        files = {'rlab-page.json': manifest_bytes or json.dumps(m).encode(),
                 'app/index.html': b'<!doctype html><title>Fixture</title>',
                 'LICENSE.txt': b'Fixture rights unspecified',
                 'app/assets/preview/mockup.png': MOCKUP,
                 'app/assets/preview/thumbnail.png': THUMB}
        files.update(dict(replace or {}))
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
        error = result['errors'][0]
        self.assertTrue(error['message'] and error['nextStep'], error)

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
    def test_required_not_requested(self): self.bad(self.run_package(lambda m:m['permissions']['required'].append('alerts.read')), 'RL006')
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
        self.host['hostApiVersion']='0.2.0'; self.bad(self.run_package(), 'RL007')
    def test_missing_required_scope(self):
        self.host['permissions']=[]; self.bad(self.run_package(), 'RL007')
    def test_missing_required_context(self):
        self.host['contextKeys']=[]; self.bad(self.run_package(), 'RL007')
    def test_missing_service(self):
        self.bad(self.run_package(lambda m:m['services'].append({'id':'org.example.fleet','minimum':'1.0.0','maximumExclusive':'2.0.0','required':True})), 'RL007')
    def test_optional_scope(self):
        self.assertEqual(self.run_package(lambda m:m['permissions']['requested'].append('alerts.read'))['status'],'offline-passed')
    def test_lower_host_limit(self):
        self.host['limits']['entries']=2; self.bad(self.run_package(), 'RL007')
    def test_manifest_size(self): self.bad(self.run_package(manifest_bytes=b' ' * 262145), 'RL011')
    def test_nonfinite(self): self.bad(self.run_package(manifest_bytes=b'{"x": NaN}'), 'RL002')
    # RLAB-PAGE-0.4 additions: preview images and utilization.manage.
    def test_missing_preview(self): self.bad(self.run_package(lambda m:m.pop('preview')), 'RL012')
    def test_preview_missing_thumbnail_object(self): self.bad(self.run_package(lambda m:m['preview'].pop('thumbnail')), 'RL002')
    def test_preview_wrong_declared_size(self): self.bad(self.run_package(lambda m:m['preview']['mockup'].update(width=1920)), 'RL002')
    def test_preview_bad_path(self): self.bad(self.run_package(lambda m:m['preview']['mockup'].update(path='app/mockup.png')), 'RL002')
    def test_preview_long_alt(self): self.bad(self.run_package(lambda m:m['preview']['thumbnail'].update(alt='x'*151)), 'RL002')
    def test_preview_file_missing(self): self.bad(self.run_package(omit='app/assets/preview/thumbnail.png'), 'RL013')
    def test_preview_wrong_type(self):
        self.bad(self.run_package(replace={'app/assets/preview/mockup.png': b'not an image'}), 'RL014')
    def test_preview_extension_mismatch(self):
        self.bad(self.run_package(replace={'app/assets/preview/mockup.png': webp_header(1600, 900)}), 'RL014')
    def test_preview_wrong_pixel_size(self):
        self.bad(self.run_package(replace={'app/assets/preview/thumbnail.png': png(320, 180)}), 'RL015')
    def test_preview_oversize(self):
        self.bad(self.run_package(replace={'app/assets/preview/thumbnail.png': png(640, 360, padding=200000)}), 'RL016')
    def test_preview_webp_accepted(self):
        def use_webp(m): m['preview']['mockup']['path']='app/assets/preview/mockup.webp'
        out=self.run_package(use_webp, extras=[('app/assets/preview/mockup.webp', webp_header(1600, 900))],
                             omit='app/assets/preview/mockup.png')
        self.assertEqual(out['status'],'offline-passed', out['errors'])
    def test_preview_webp_wrong_size(self):
        def use_webp(m): m['preview']['mockup']['path']='app/assets/preview/mockup.webp'
        self.bad(self.run_package(use_webp, extras=[('app/assets/preview/mockup.webp', webp_header(1280, 720))]), 'RL015')
    def test_old_preview_extension_warns(self):
        out=self.run_package(lambda m:m['extensions'].update({'com.ratehighway.rlab.preview':{}}))
        self.assertEqual(out['status'],'offline-passed')
        self.assertTrue(any('replaces' in w for w in out['warnings']))
    def test_manage_without_read(self):
        def mutate(m):
            for k in ('requested','required'): m['permissions'][k].remove('utilization.read')
        self.bad(self.run_package(mutate), 'RL017')
    def test_manage_without_required_service(self):
        self.bad(self.run_package(lambda m:m['services'][0].update(required=False)), 'RL018')
    def test_manage_without_any_service(self):
        self.bad(self.run_package(lambda m:m.update(services=[])), 'RL018')
    def test_manage_required_not_requested(self):
        self.bad(self.run_package(lambda m:m['permissions']['requested'].remove('utilization.manage')), 'RL006')
    def test_read_only_04_page(self):
        def mutate(m):
            m['permissions']={'requested':['context.read'],'required':['context.read']}; m['services']=[]
        self.assertEqual(self.run_package(mutate)['status'],'offline-passed')
    def test_host_without_manage(self):
        self.host['permissions']=['context.read','utilization.read']; self.bad(self.run_package(), 'RL007')
    def test_02_page_refused(self):
        self.bad(self.run_package(lambda m:m.update(profile='RLAB-PAGE-READONLY-0.2')), 'RL002')
    def test_02_host_document_refused(self):
        self.host['standardVersions']=['0.2']; self.host['profiles']=['RLAB-PAGE-READONLY-0.2']
        self.bad(self.run_package(), 'RL002')
    def test_example_previews_are_real_and_exact(self):
        for name, size in (('mockup',(1600,900)),('thumbnail',(640,360))):
            data=(ROOT/'examples/group-manager/app/assets/preview'/(name+'.png')).read_bytes()
            self.assertEqual(r.image_size(data), ('png',)+size)
    def test_pack_sample(self):
        out=r.pack(ROOT/'examples/group-manager',self.path)
        self.assertEqual(out['status'],'offline-passed')
        self.assertEqual(r.validate(self.path,self.host)['status'],'offline-passed')
    def test_packer_preserves_existing_output(self):
        self.path.write_bytes(b'preserve')
        with self.assertRaises(ValueError): r.pack(ROOT/'examples/group-manager',self.path)
        self.assertEqual(self.path.read_bytes(),b'preserve')


if __name__ == '__main__': unittest.main()
