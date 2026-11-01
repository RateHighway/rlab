"""Offline reference checks for the pinned RevenueLab 0.2 schemas.

No code execution, extraction, network access or third-party dependencies.
This is not a production security scanner or generic JSON Schema engine.
"""
import argparse
import hashlib
import json
import pathlib
import re
import stat
import sys
import zipfile
from urllib.parse import urlsplit

ROOT = pathlib.Path(__file__).resolve().parents[1]
LIMITS = dict(compressedBytes=25000000, expandedBytes=100000000,
              fileBytes=25000000, entries=2000, pathCharacters=240)
ALLOWED = {'.json', '.html', '.css', '.js', '.mjs', '.png', '.jpg', '.jpeg',
           '.webp', '.gif', '.ico', '.woff', '.woff2', '.txt', '.md', '.csv'}
NOT_PERFORMED = ['Browser/runtime conformance', 'Publisher identity or licence verification',
                 'Malware/dependency/complete secret scanning', 'Remote URL/header/deployment checks',
                 'Gateway authorisation and cross-tenant tests', 'Certification assessment']


class Invalid(Exception):
    def __init__(self, code, path, message):
        self.code, self.path, self.message = code, path, message
        super().__init__(message)


def fail(code, path, message):
    raise Invalid(code, path, message)


def pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            fail('RL002', 'JSON', 'Duplicate object key')
        result[key] = value
    return result


def parse_json(data):
    return json.loads(data.decode('utf-8'), object_pairs_hook=pairs,
                      parse_constant=lambda _: fail('RL002', 'JSON', 'Non-finite number'))


def load_json(path):
    return parse_json(pathlib.Path(path).read_bytes())


def schema_check(value, schema, root=None, path='$'):
    """Evaluate only keywords used by the pinned schemas; fail on unknown keywords."""
    root = schema if root is None else root
    supported = {'$schema', '$id', '$defs', '$ref', 'title', 'description', 'default',
                 'type', 'const', 'enum', 'required', 'properties', 'additionalProperties',
                 'propertyNames', 'oneOf', 'items', 'uniqueItems', 'minItems', 'maxItems',
                 'minLength', 'maxLength', 'pattern', 'format', 'minimum', 'maximum'}
    if set(schema) - supported:
        raise RuntimeError('Unsupported keyword in pinned schema')
    if '$ref' in schema:
        ref = schema['$ref']
        if not ref.startswith('#/$defs/'):
            raise RuntimeError('Only pinned local definition references are supported')
        schema_check(value, root['$defs'][ref.split('/')[-1]], root, path)
    if 'oneOf' in schema:
        valid = 0
        for variant in schema['oneOf']:
            try:
                schema_check(value, variant, root, path)
                valid += 1
            except Invalid:
                pass
        if valid != 1:
            fail('RL002', path, 'Expected exactly one schema variant')
    types = {'object': lambda v: isinstance(v, dict), 'array': lambda v: isinstance(v, list),
             'string': lambda v: isinstance(v, str), 'boolean': lambda v: type(v) is bool,
             'integer': lambda v: type(v) is int}
    if 'type' in schema and not types[schema['type']](value):
        fail('RL002', path, 'Wrong value type')
    if 'const' in schema and (type(value) is not type(schema['const']) or value != schema['const']):
        fail('RL002', path, 'Wrong constant')
    if 'enum' in schema and not any(type(value) is type(x) and value == x for x in schema['enum']):
        fail('RL002', path, 'Unsupported enum value')
    if isinstance(value, dict):
        if set(schema.get('required', [])) - set(value):
            fail('RL002', path, 'Missing required fields')
        props = schema.get('properties', {})
        for key, item in value.items():
            if 'propertyNames' in schema:
                schema_check(key, schema['propertyNames'], root, path)
            if key in props:
                schema_check(item, props[key], root, path + '.' + key)
            elif schema.get('additionalProperties') is False:
                fail('RL002', path, 'Unknown property')
    if isinstance(value, list):
        if len(value) < schema.get('minItems', 0) or len(value) > schema.get('maxItems', float('inf')):
            fail('RL002', path, 'Array length out of bounds')
        if schema.get('uniqueItems') and len({json.dumps(x, sort_keys=True) for x in value}) != len(value):
            fail('RL002', path, 'Duplicate array items')
        for i, item in enumerate(value):
            if 'items' in schema:
                schema_check(item, schema['items'], root, path + '[' + str(i) + ']')
    if isinstance(value, str):
        if len(value) < schema.get('minLength', 0) or len(value) > schema.get('maxLength', float('inf')):
            fail('RL002', path, 'String length out of bounds')
        if 'pattern' in schema and not re.search(schema['pattern'], value):
            fail('RL002', path, 'String pattern mismatch')
        if schema.get('format') == 'uri':
            try:
                u = urlsplit(value)
                if not u.scheme or re.search(r'\s', value):
                    raise ValueError()
            except ValueError:
                fail('RL002', path, 'Invalid URI')
        if schema.get('format') == 'email' and not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', value):
            fail('RL002', path, 'Invalid email')
    if type(value) is int:
        if value < schema.get('minimum', -float('inf')) or value > schema.get('maximum', float('inf')):
            fail('RL002', path, 'Number out of bounds')


def safe_path(name):
    if not name or len(name) > 240 or not re.fullmatch(r'[A-Za-z0-9._/-]+', name):
        fail('RL003', 'archive', 'Invalid path characters or length')
    pieces = name.split('/')
    for piece in pieces:
        if not piece or piece in ('.', '..') or piece.endswith('.'):
            fail('RL003', 'archive', 'Unsafe path component')
        if re.fullmatch(r'(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])', piece.split('.')[0], re.I):
            fail('RL003', 'archive', 'Reserved device path')
    if name.startswith('/'):
        fail('RL003', 'archive', 'Absolute path')


def https_url(value, origin=False):
    try:
        u = urlsplit(value)
        if (u.scheme != 'https' or not u.hostname or u.username or u.password or u.query or u.fragment
                or re.search(r'[\s\\*%]', value) or '#' in value or '?' in value):
            raise ValueError()
        if u.port is not None and not 1 <= u.port <= 65535:
            raise ValueError()
        canonical = 'https://' + u.hostname.lower() + ((':' + str(u.port)) if u.port and u.port != 443 else '')
        # Narrow DNS-name origin profile; no IP literals, uppercase or default-port aliases.
        if not re.fullmatch(r'[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?', u.hostname):
            raise ValueError()
        if u.netloc != canonical[len('https://'):]:
            raise ValueError()
        if origin and value != canonical:
            raise ValueError()
        return canonical
    except ValueError:
        fail('RL005', 'URL', 'Use a canonical exact HTTPS origin/URL without credentials, query or fragment')


def version(v):
    return tuple(int(x) for x in v.split('.'))


def compatible(actual, bounds):
    return version(bounds['minimum']) <= version(actual) < version(bounds['maximumExclusive'])


def check_semantics(m, names, host, measured, warnings):
    if version(m['hostApi']['minimum']) >= version(m['hostApi']['maximumExclusive']):
        fail('RL007', 'hostApi', 'Empty version interval')
    if not set(m['permissions']['required']) <= set(m['permissions']['requested']):
        fail('RL006', 'permissions.required', 'Required scopes must also be requested')
    if set(m['context']['required']) & set(m['context']['optional']):
        fail('RL002', 'context', 'Required and optional keys must be disjoint')
    service_ids = [s['id'] for s in m['services']]
    if len(set(service_ids)) != len(service_ids):
        fail('RL002', 'services', 'Duplicate service ID')
    for service in m['services']:
        if version(service['minimum']) >= version(service['maximumExclusive']):
            fail('RL007', 'services', 'Empty service version interval')
    for origin in m['network']['connect']:
        https_url(origin, True)
    https_url(m['support']['url'])
    delivery = m['delivery']
    if delivery['mode'] == 'bundle':
        safe_path(delivery['entry'])
        if delivery['entry'] not in names:
            fail('RL004', 'delivery.entry', 'HTML entry is absent')
    else:
        if https_url(delivery['url']) != https_url(delivery['origin'], True):
            fail('RL005', 'delivery', 'Remote URL and origin differ')
        if delivery['origin'] in m['network']['connect']:
            fail('RL005', 'network.connect', 'Do not repeat remote delivery origin')
        warnings.append('Remote deployment requires separate review; no URL was fetched.')
    if m['network']['connect'] and not m['dataHandling']['externalProcessing']:
        fail('RL002', 'dataHandling', 'Additional network destinations require external-processing disclosure')
    if m['dataHandling']['retention'] == 'customer-controlled' and not m['dataHandling']['externalProcessing']:
        fail('RL002', 'dataHandling', 'Customer-controlled retention needs external-processing review')
    if m['dataHandling']['externalProcessing']:
        warnings.append('External processing requires administrator and host policy review.')
    if 'file' in m['license']:
        safe_path(m['license']['file'])
        if m['license']['file'] not in names:
            fail('RL002', 'license.file', 'Referenced licence file is absent')
    if m['license']['status'] == 'unspecified':
        warnings.append('Licence rights are unspecified; resolve before real installation/distribution.')
    if host is None:
        warnings.append('No target host supplied; compatibility not checked.')
        return
    schema_check(host, load_json(ROOT / 'schemas/rlab-host-0.2.schema.json'))
    https_url(host['documentationUrl']); https_url(host['supportUrl'])
    if (m['standardVersion'] not in host['standardVersions'] or m['profile'] not in host['profiles']
            or not compatible(host['hostApiVersion'], m['hostApi'])
            or delivery['mode'] not in host['deliveryModes']):
        fail('RL007', 'host', 'Unsupported standard, profile, host API or delivery mode')
    if not set(m['permissions']['required']) <= set(host['permissions']):
        fail('RL007', 'host.permissions', 'Missing required scopes')
    if not set(m['context']['required']) <= set(host['contextKeys']):
        fail('RL007', 'host.contextKeys', 'Missing required context')
    hs = {s['id']: s['version'] for s in host['services']}
    if len(hs) != len(host['services']):
        fail('RL007', 'host.services', 'Duplicate host service IDs')
    for service in m['services']:
        present = service['id'] in hs and compatible(hs[service['id']], service)
        if not present and service['required']:
            fail('RL007', 'host.services', 'Required service unavailable/incompatible')
        if not present:
            warnings.append('An optional service is unavailable; runtime fallback must be tested.')
    if set(m['permissions']['requested']) - set(host['permissions']):
        warnings.append('Some optional requested scopes are unavailable on this host.')
    for key, actual in measured.items():
        if actual > host['limits'][key]:
            fail('RL007', 'host.limits', 'Package exceeds target host limit')


def validate(path, host=None):
    result = dict(status='invalid', standardVersion='0.2', sha256=None, errors=[], warnings=[],
                  notPerformed=NOT_PERFORMED, validator='rlab-reference-0.2.0')
    try:
        path = pathlib.Path(path)
        size = path.stat().st_size
        if size > LIMITS['compressedBytes']:
            fail('RL011', 'archive', 'Compressed package exceeds limit')
        if path.suffix.lower() != '.rlab':
            fail('RL001', 'archive', 'Expected .rlab extension')
        raw = path.read_bytes()
        result['sha256'] = hashlib.sha256(raw).hexdigest()
        import io
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            infos = z.infolist()
            if len(infos) > LIMITS['entries']:
                fail('RL011', 'archive', 'Too many entries')
            seen, files, paths, expanded = set(), {}, [], 0
            for info in infos:
                name = info.filename
                # zipfile truncates NULs; reject the original spelling too.
                if info.orig_filename != name:
                    fail('RL003', 'archive', 'NUL-containing name')
                directory = name.endswith('/')
                clean = name[:-1] if directory else name
                safe_path(clean)
                lower = clean.lower()
                if lower in seen:
                    fail('RL003', 'archive', 'Duplicate or case-colliding path')
                seen.add(lower); paths.append((lower, directory))
                mode = info.external_attr >> 16
                kind = stat.S_IFMT(mode)
                if kind not in (0, stat.S_IFDIR if directory else stat.S_IFREG):
                    fail('RL003', 'archive', 'Link or special entry')
                if info.flag_bits & 1 or info.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
                    fail('RL003', 'archive', 'Encrypted or unsupported compression')
                if info.file_size > LIMITS['fileBytes']:
                    fail('RL011', 'archive', 'File too large')
                if clean == 'rlab-page.json' and info.file_size > 262144:
                    fail('RL011', 'manifest', 'Manifest too large')
                data = bytearray()
                with z.open(info) as f:
                    while True:
                        chunk = f.read(65536)
                        if not chunk:
                            break
                        expanded += len(chunk); data.extend(chunk)
                        if expanded > LIMITS['expandedBytes'] or len(data) > LIMITS['fileBytes']:
                            fail('RL011', 'archive', 'Actual expanded size exceeds limits')
                if directory:
                    if data:
                        fail('RL003', 'archive', 'Directory contains data')
                    continue
                suffix = pathlib.PurePosixPath(clean).suffix.lower()
                if suffix not in ALLOWED or clean.lower().endswith(('.env', '.pem', '.key')):
                    fail('RL008', 'archive', 'Unsupported file type')
                if bytes(data[:4]) in (b'PK\x03\x04', b'\x7fELF', b'\x00asm') or data[:2] == b'MZ':
                    fail('RL008', 'archive', 'Archive, native executable or WASM signature')
                if suffix in {'.js', '.mjs', '.html', '.json', '.txt', '.md', '.css'}:
                    text = bytes(data).decode('utf-8')
                    if re.search(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----', text):
                        fail('RL008', 'archive', 'Private key marker; details suppressed')
                    if suffix in {'.js', '.mjs', '.html'} and re.search(r'\beval\s*\(|\bnew\s+Function\s*\(|serviceWorker\s*\.\s*register', text):
                        fail('RL008', 'archive', 'Prohibited dynamic execution or service worker marker')
                files[clean] = bytes(data)
            non_dirs = {name for name, is_dir in paths if not is_dir}
            for name, _ in paths:
                parts = name.split('/')
                if any('/'.join(parts[:i]) in non_dirs for i in range(1, len(parts))):
                    fail('RL003', 'archive', 'File/directory collision')
            if 'rlab-page.json' not in files:
                fail('RL001', 'archive', 'Root manifest missing')
            if any(n.lower().endswith('/rlab-page.json') for n in files):
                fail('RL001', 'archive', 'Nested manifest is not permitted')
            m = parse_json(files['rlab-page.json'])
            schema_check(m, load_json(ROOT / 'schemas/rlab-page-manifest-0.2.schema.json'))
            measured = dict(compressedBytes=size, expandedBytes=expanded, entries=len(infos),
                            fileBytes=max([len(v) for v in files.values()] or [0]),
                            pathCharacters=max([len(n) for n, _ in paths] or [0]))
            check_semantics(m, set(files), host, measured, result['warnings'])
            result['status'] = 'offline-passed'
            result['pageId'], result['pageVersion'], result['measured'] = m['id'], m['version'], measured
    except Invalid as e:
        result['errors'].append(dict(code=e.code, path=e.path, message=e.message))
    except (OSError, ValueError, UnicodeError, zipfile.BadZipFile, RuntimeError, NotImplementedError, RecursionError) as e:
        result['errors'].append(dict(code='RL011', path='archive', message='Cannot safely read package: ' + type(e).__name__))
    return result


def pack(source, destination):
    source, destination = pathlib.Path(source).resolve(), pathlib.Path(destination).resolve()
    if not source.is_dir():
        raise ValueError('Source folder does not exist')
    if destination == source or source in destination.parents:
        raise ValueError('Output must be outside the source directory')
    if destination.suffix != '.rlab':
        raise ValueError('Output must have .rlab extension')
    if destination.exists():
        raise ValueError('Output already exists; choose a new path or deliberately remove the old local build')
    destination.parent.mkdir(parents=True, exist_ok=True)
    items = sorted(source.rglob('*'))
    if any(p.is_symlink() for p in items):
        raise ValueError('Source contains a symbolic link')
    with zipfile.ZipFile(str(destination), 'w', zipfile.ZIP_DEFLATED) as z:
        for p in items:
            if p.is_file():
                name = p.relative_to(source).as_posix()
                safe_path(name)
                info = zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = (stat.S_IFREG | 0o644) << 16
                z.writestr(info, p.read_bytes())
    return validate(destination)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    v = sub.add_parser('validate'); v.add_argument('package'); v.add_argument('--host')
    b = sub.add_parser('pack'); b.add_argument('source'); b.add_argument('destination')
    args = p.parse_args()
    try:
        r = pack(args.source, args.destination) if args.command == 'pack' else validate(args.package, load_json(args.host) if args.host else None)
        print(json.dumps(r, indent=2))
        return 0 if r['status'] == 'offline-passed' else 1
    except Exception as e:
        print(json.dumps({'status': 'tool-error', 'errorType': type(e).__name__}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
