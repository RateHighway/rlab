"""Shared source inventory and metadata for the .rlab technical repository."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
VERSION = '0.2.0'
PROFILES = (
    ('browser-readonly-0.2', 'RLAB-PAGE-READONLY-0.2', '0.2',
     'browser-page-source; host implementation required', ('fleet-pressure',),
     ('rlab.py',)),
    ('declarative-design-0.3', 'RLAB-DECLARATIVE-DESIGN-0.3', '0.3',
     'design-only; no runtime', tuple('level-' + str(n) for n in range(1, 5)),
     ('check_design.py', 'schema_subset.py')),
)
OMIT = {'.git', '.venv', '__pycache__', 'build', 'tutorial-output'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n',
                    encoding='utf-8', newline='\n')


def source_files(root=ROOT):
    """Inventory the source tree, excluding local build and environment output."""
    found = []
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in OMIT)
        for name in dirs + sorted(files):
            path = Path(current) / name
            if path.is_symlink():
                raise ValueError('Source tree contains a symbolic link')
        found.extend(Path(current) / name for name in sorted(files)
                     if not name.endswith(('.pyc', '.pyo')))
    return sorted(found, key=lambda p: p.relative_to(root).as_posix())


def make_catalog(root=ROOT):
    profiles = []
    for folder, profile_id, standard, runtime, examples, tool_names in PROFILES:
        base = root / 'profiles' / folder
        def entry(path):
            return {'path': path.relative_to(root).as_posix(), 'sha256': digest(path)}
        schemas = []
        for path in sorted((base / 'schemas').glob('*.json')):
            schema = json.loads(path.read_text(encoding='utf-8'))
            document_id = schema.get('properties', {}).get('$schema', {}).get('const')
            schemas.append(dict(entry(path), id=schema.get('$id'),
                                documentSchemaIdentifier=document_id))
        pages = []
        for name in examples:
            path = base / 'examples' / name / 'rlab-page.json'
            manifest = json.loads(path.read_text(encoding='utf-8'))
            pages.append(dict(entry(path), pageId=manifest['id'],
                              pageVersion=manifest['version'],
                              schemaIdentifier=manifest['$schema']))
        profiles.append({
            'id': profile_id, 'standardVersion': standard, 'maturity': 'draft',
            'runtimeStatus': runtime, 'root': base.relative_to(root).as_posix(),
            'schemas': schemas, 'examples': pages,
            'tools': [entry(base / 'tools' / name) for name in tool_names],
            'files': [entry(p) for p in source_files(base)],
        })
    central = {
        'id': 'RLAB-CENTRAL-ADMISSION-1',
        'requiredFor': 'official registered-host admission',
        'repository': 'https://github.com/RateHighway/rlab-pages',
        'visibility': 'private',
        'branch': 'master',
        'validator': {'path': 'tools/validate_registered_page.py',
                      'sha256': digest(root / 'tools/validate_registered_page.py')},
        'schemas': [{'path': p.relative_to(root).as_posix(), 'sha256': digest(p)}
                    for p in sorted((root / 'schemas').glob('*-record.schema.json'))],
    }
    return {'catalogVersion': 2, 'repositoryVersion': VERSION, 'centralAdmission': central,
            'revisionBinding': 'enclosing-git-commit', 'license': 'Apache-2.0',
            'maturity': 'draft', 'profiles': profiles}


def run_json(script, *args):
    result = subprocess.run([sys.executable, '-B', str(script), *map(str, args)],
                            cwd=ROOT, text=True, capture_output=True, check=True)
    return json.loads(result.stdout)


def own_git_revision():
    """Return only a clean dedicated source commit; Git is optional offline."""
    if shutil.which('git') is None:
        return None
    result = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', '--show-toplevel'],
                            text=True, capture_output=True)
    if result.returncode or Path(result.stdout.strip()).resolve() != ROOT:
        return None
    status = subprocess.check_output(['git', '-C', str(ROOT), 'status', '--porcelain'],
                                     text=True)
    if status.strip():
        return None
    return subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'],
                                   text=True).strip()
