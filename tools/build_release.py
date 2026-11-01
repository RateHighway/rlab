"""Build licensed examples and a source snapshot in a new output directory."""
import argparse
import json
from pathlib import Path
import platform
import zipfile
import zlib

from check_repository import check_sources
from repository import (ROOT, VERSION, digest, own_git_revision, run_json,
                        source_files, write_json)


def zip_files(destination, files):
    with zipfile.ZipFile(destination, 'x', zipfile.ZIP_DEFLATED) as archive:
        for name, path in sorted(files):
            info = zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    with zipfile.ZipFile(destination) as archive:
        if archive.testzip() is not None:
            raise ValueError('Output archive failed its CRC check')


def build(output):
    output = Path(output).resolve()
    if output.is_relative_to(ROOT) and not output.is_relative_to(ROOT / 'build'):
        raise ValueError('Output must be outside the source tree or within build/')
    if output.exists():
        raise ValueError('Output directory already exists; choose a fresh path')
    check_sources()
    sources = source_files()
    output.mkdir(parents=True, exist_ok=False)
    reports = []
    browser = ROOT / 'profiles/browser-readonly-0.2'
    folder = browser / 'examples/fleet-pressure'
    page = json.loads((folder / 'rlab-page.json').read_text(encoding='utf-8'))
    artifact = output / f"fleet-pressure-{page['version']}.rlab"
    run_json(browser / 'tools/rlab.py', 'pack', folder, artifact)
    report = run_json(browser / 'tools/rlab.py', 'validate', artifact,
                      '--host', browser / 'examples/host-capabilities.json')
    reports.append(dict(report, artifact=artifact.name, runtimeExecuted=False))
    design = ROOT / 'profiles/declarative-design-0.3'
    for level in range(1, 5):
        folder = design / f'examples/level-{level}'
        report = run_json(design / 'tools/check_design.py', folder)
        if report['status'] != 'design-checked':
            raise ValueError('Cannot package an invalid design')
        page = json.loads((folder / 'rlab-page.json').read_text(encoding='utf-8'))
        artifact = output / f"fleet-review-level-{level}-{page['version']}-design.rlab"
        names = set(report['checkedFiles']) | {'README.md', 'LICENSE.txt', 'NOTICE.txt'}
        zip_files(artifact, [(name, folder / name) for name in names])
        reports.append(dict(report, artifact=artifact.name, sha256=digest(artifact),
                            runtimeExecuted=False))
    write_json(output / 'check-reports.json', reports)
    zip_files(output / f'rlab-source-{VERSION}.zip',
              [(p.relative_to(ROOT).as_posix(), p) for p in sources])
    artifacts = [{'path': p.name, 'sha256': digest(p), 'bytes': p.stat().st_size}
                 for p in sorted(output.iterdir())]
    manifest = {
        'manifestVersion': 1, 'repositoryVersion': VERSION, 'maturity': 'draft',
        'sourceCommit': own_git_revision(), 'runtimeExecuted': False,
        'environment': {'python': platform.python_version(), 'zlib': zlib.ZLIB_RUNTIME_VERSION},
        'sourceFiles': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': digest(p)}
                        for p in sources],
        'artifacts': artifacts,
    }
    write_json(output / 'release-manifest.json', manifest)
    sums = ''.join(f'{digest(p)}  {p.name}\n' for p in sorted(output.iterdir()))
    (output / 'SHA256SUMS').write_text(sums, encoding='utf-8', newline='\n')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    result = build(args.output)
    print(json.dumps({'status': 'release-built', 'repositoryVersion': VERSION,
                      'artifacts': len(result['artifacts']), 'runtimeExecuted': False}))


if __name__ == '__main__':
    main()
