"""Check repository sources and run the offline reference suites. No deployment."""
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from urllib.parse import unquote, urlsplit

from repository import ROOT, make_catalog, run_json, source_files


def check_sources():
    expected = make_catalog()
    actual = json.loads((ROOT / 'catalog.json').read_text(encoding='utf-8'))
    if actual != expected:
        raise ValueError('Catalog drift: review source edits, then run tools/update_catalog.py')
    license_bytes = (ROOT / 'LICENSE').read_bytes()
    files = source_files()
    link_count = json_count = 0
    for path in files:
        if path.suffix == '.json':
            json.loads(path.read_text(encoding='utf-8'))
            json_count += 1
        if path.suffix == '.md':
            text = path.read_text(encoding='utf-8')
            text = re.sub(r'^```[^\n]*\n.*?^```[^\n]*$', '', text,
                          flags=re.MULTILINE | re.DOTALL)
            for target in re.findall(r'\[[^\]]*\]\(([^\s)]+)\)', text):
                target = target.strip('<>')
                parsed = urlsplit(target)
                if parsed.scheme or target.startswith(('#', '//')):
                    continue
                resolved = (path.parent / unquote(parsed.path)).resolve()
                if not resolved.is_relative_to(ROOT) or not resolved.exists():
                    raise ValueError(f'Broken local link: {path.relative_to(ROOT)} -> {target}')
                link_count += 1
    for profile in expected['profiles']:
        for sample in profile['examples']:
            folder = (ROOT / sample['path']).parent
            manifest = json.loads((folder / 'rlab-page.json').read_text(encoding='utf-8'))
            if (folder / 'LICENSE.txt').read_bytes() != license_bytes:
                raise ValueError('An example must carry the complete repository license')
            if manifest['license']['status'] != 'open-source' or not (folder / 'NOTICE.txt').is_file():
                raise ValueError('An example is missing its explicit license status or notice')
    return {'files': len(files), 'jsonDocuments': json_count, 'localLinks': link_count}


def check_examples():
    browser = ROOT / 'profiles/browser-readonly-0.2'
    with tempfile.TemporaryDirectory(prefix='rlab-check-') as tmp:
        package = Path(tmp) / 'fleet-pressure.rlab'
        run_json(browser / 'tools/rlab.py', 'pack', browser / 'examples/fleet-pressure', package)
        report = run_json(browser / 'tools/rlab.py', 'validate', package,
                          '--host', browser / 'examples/host-capabilities.json')
        if report['status'] != 'offline-passed':
            raise ValueError('Browser example did not pass offline checks')
    design = ROOT / 'profiles/declarative-design-0.3'
    for level in range(1, 5):
        report = run_json(design / 'tools/check_design.py', design / f'examples/level-{level}')
        if report['status'] != 'design-checked':
            raise ValueError('Declarative fixture did not pass design checks')


def main():
    summary = check_sources()
    check_examples()
    for suite in ('profiles/browser-readonly-0.2/tests',
                  'profiles/declarative-design-0.3/tests', 'tests'):
        subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover',
                        '-s', suite, '-v'], cwd=ROOT, check=True)
    print(json.dumps(dict(summary, status='repository-checked', runtimeExecuted=False)))


if __name__ == '__main__':
    main()
