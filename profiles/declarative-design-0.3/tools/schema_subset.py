# Limited checker for the pinned schema subset.
import json
import pathlib
import re
from urllib.parse import urlsplit

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
