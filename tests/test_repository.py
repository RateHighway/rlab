"""Release integrity and overwrite protections beyond the profile test suites."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from build_release import build
from repository import make_catalog


class ReleaseTests(unittest.TestCase):
    def test_catalog_matches_current_files(self):
        actual = json.loads((ROOT / 'catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(actual, make_catalog())

    def test_existing_output_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'existing'
            output.mkdir()
            marker = output / 'keep.txt'
            marker.write_text('keep', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'already exists'):
                build(output)
            self.assertEqual(marker.read_text(encoding='utf-8'), 'keep')

    def test_every_manifest_identifier_resolves_in_catalog(self):
        for profile in make_catalog()['profiles']:
            identifiers = {s[field] for s in profile['schemas']
                           for field in ('id', 'documentSchemaIdentifier') if s[field]}
            for example in profile['examples']:
                self.assertIn(example['schemaIdentifier'], identifiers)

    def test_source_directory_cannot_be_output(self):
        with self.assertRaisesRegex(ValueError, 'outside the source tree'):
            build(ROOT / 'profiles')

    def test_source_zip_build_does_not_require_git(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch('repository.shutil.which', return_value=None):
                report = build(Path(tmp) / 'without-git')
            self.assertIsNone(report['sourceCommit'])

    def test_repeated_builds_and_bundled_rights(self):
        with tempfile.TemporaryDirectory() as tmp:
            first, second = Path(tmp) / 'first', Path(tmp) / 'second'
            a, b = build(first), build(second)
            self.assertEqual(a, b)
            self.assertEqual({p.name: p.read_bytes() for p in first.iterdir()},
                             {p.name: p.read_bytes() for p in second.iterdir()})
            packages = list(first.glob('*.rlab'))
            self.assertEqual(len(packages), 5)
            source_archives = list(first.glob('*-source.zip'))
            self.assertEqual(len(source_archives), 5)
            for source in source_archives:
                with zipfile.ZipFile(source) as archive:
                    self.assertIn('rlab-page.json', archive.namelist())
                    self.assertEqual(json.loads(archive.read('rlab-page.json'))['version'], '0.1.1')
            self.assertIs(a['admissionEligible'], False)
            for package in packages:
                with zipfile.ZipFile(package) as archive:
                    self.assertEqual(archive.read('LICENSE.txt'), (ROOT / 'LICENSE').read_bytes())
                    self.assertIn('NOTICE.txt', archive.namelist())
                    manifest = json.loads(archive.read('rlab-page.json'))
                    self.assertEqual(manifest['version'], '0.1.1')
                    self.assertEqual(manifest['license']['status'], 'open-source')
                    if manifest['standardVersion'] == '0.3':
                        self.assertEqual(manifest['stage'], 'design-only')
            for line in (first / 'SHA256SUMS').read_text(encoding='utf-8').splitlines():
                expected, name = line.split('  ', 1)
                self.assertEqual(expected, hashlib.sha256((first / name).read_bytes()).hexdigest())


if __name__ == '__main__':
    unittest.main()
