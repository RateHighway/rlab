"""Check design documents only. No execution, network or production approval."""
import argparse
import json
import pathlib
import re
import sys
from schema_subset import Invalid, load_json, schema_check, fail

ROOT = pathlib.Path(__file__).resolve().parents[1]


def read_doc(folder, name, schema_name):
    if not isinstance(name, str) or not re.fullmatch(r'[A-Za-z0-9._/-]+', name):
        fail('D01', 'path', 'Invalid path')
    if any(part in ('', '.', '..') for part in name.split('/')) or name.startswith('/'):
        fail('D01', 'path', 'Unsafe path')
    p = folder / name
    if folder not in p.resolve().parents or p.is_symlink():
        fail('D01', 'path', 'File must be inside the design folder')
    if p.stat().st_size > 262144:
        fail('D01', 'path', 'Design document exceeds 256 KiB')
    value = load_json(p)
    schema_check(value, load_json(ROOT / 'schemas' / schema_name))
    return value


def v(value):
    if not isinstance(value, str) or not re.fullmatch(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)', value):
        fail('D02', 'version', 'Expected numeric semantic version')
    return tuple(int(x) for x in value.split('.'))


def in_range(actual, request):
    lo, hi = v(request['minimum']), v(request['maximumExclusive'])
    if lo >= hi:
        fail('D02', 'version', 'Empty version range')
    return lo <= v(actual) < hi


def unique(items, key, where):
    values = [x[key] for x in items]
    if len(values) != len(set(values)):
        fail('D03', where, 'Duplicate identifier')
    return {x[key]: x for x in items}


def check(folder, host=None):
    report = {'status':'invalid', 'errors':[], 'warnings':[], 'checkedFiles':[],
              'notTested':['Package extraction/security', 'UI renderer/browser accessibility',
                           'Action execution/authorisation', 'Workflow runner/recovery',
                           'Scheduler/mandates', 'Host certification']}
    try:
        folder = pathlib.Path(folder).resolve()
        host = load_json(ROOT/'fixtures/host-catalog.json') if host is None else host
        m = read_doc(folder, 'rlab-page.json', 'manifest.schema.json')
        report['checkedFiles'].append('rlab-page.json')
        level = m['capabilityLevel']
        if m['standardVersion'] not in host['standardVersions'] or level > host['maxLevel']:
            fail('D04', 'host', 'Standard/level unsupported')
        if not in_range(host['hostApiVersion'],m['hostApi']):
            fail('D04', 'hostApi', 'Host API incompatible')
        if m['runtime']['kind'] not in host['runtimes'] or m['runtime']['uiContract'] not in host['uiContracts']:
            fail('D04', 'runtime', 'Runtime/UI contract unsupported')
        if not set(m['permissions']['requested']) <= set(host['permissions']):
            fail('D05', 'permissions', 'Unknown permission')
        if 'workflow' in m and level < 3:
            fail('D06', 'workflow', 'Workflow requires Level 3 or 4')
        if 'automation' in m and level != 4:
            fail('D06', 'automation', 'Automation requires Level 4')
        if level == 1 and m['actions']:
            fail('D06', 'actions', 'Level 1 cannot declare actions')
        if level == 1 and any(not p.endswith('.read') for p in m['permissions']['requested']):
            fail('D06', 'permissions', 'Level 1 cannot request business writes')
        inferred = 4 if 'automation' in m else 3 if 'workflow' in m else 2 if m['actions'] else 1
        if level != inferred:
            fail('D06', 'capabilityLevel', 'Preview profile requires the minimum level needed by declared features')
        if level == 4 and 'workflow' not in m:
            fail('D06', 'automation', 'Automation needs a workflow')
        queries = unique(m['queries'],'name','queries')
        actions = unique(m['actions'],'name','actions')
        hqueries = unique(host['queries'],'id','host.queries')
        hactions = unique(host['actions'],'id','host.actions')
        required_permissions = set()
        for kind, bindings, contracts in [('queries',queries,hqueries),('actions',actions,hactions)]:
            for name, binding in bindings.items():
                if binding['contract'] not in contracts:
                    fail('D07', kind+'.'+name, 'Host contract missing')
                contract = contracts[binding['contract']]
                if not in_range(contract['version'],binding):
                    fail('D07', kind+'.'+name, 'Contract version mismatch')
                required_permissions.update(contract['requiredPermissions'])
                if set(binding['inputBindings']) != set(contract['requiredInputs']):
                    fail('D08', kind+'.'+name, 'Inputs differ from required contract keys')
                for value in binding['inputBindings'].values():
                    schema_check(value,load_json(ROOT/'schemas/binding.schema.json'))
                    if 'context' in value and value['context'] not in host['contextKeys']:
                        fail('D08', kind+'.'+name, 'Context key unavailable')
        grants = set(m['permissions']['requested'])
        if not required_permissions <= grants:
            fail('D05', 'permissions', 'Required contract permission missing')
        if grants - required_permissions:
            report['warnings'].append('Unused declared permissions: remove or justify before installation.')
        seen_surfaces = set()
        manual_workflow = False
        for surface in m['surfaces']:
            if surface['slot'] in seen_surfaces:
                fail('D03', 'surfaces', 'Duplicate surface slot')
            seen_surfaces.add(surface['slot'])
            if surface['slot'] not in host['surfaces']:
                fail('D04', 'surfaces', 'Required surface unsupported')
            ui = read_doc(folder,surface['entry'],'ui.schema.json')
            report['checkedFiles'].append(surface['entry'])
            for component in ui['components']:
                if component['type']=='DataTable':
                    if component['query'] not in queries:
                        fail('D09','ui','Unknown query binding')
                    c = hqueries[queries[component['query']]['contract']]
                    if 'user' not in c['modes']:
                        fail('D09','ui','Query disallows interactive use')
                    if not set(component['columns']) <= set(c['fields']):
                        fail('D09','ui','Unsupported display field')
                if component['type']=='ActionButton':
                    if component['action'] not in actions or level<2:
                        fail('D09','ui','Unknown or disallowed action')
                    c=hactions[actions[component['action']]['contract']]
                    if 'user' not in c['modes']:
                        fail('D09','ui','Action disallows user initiation')
                if component['type']=='WorkflowButton':
                    if 'workflow' not in m:
                        fail('D09','ui','Workflow binding absent')
                    manual_workflow = True
        if 'workflow' in m:
            wf=read_doc(folder,m['workflow'],'workflow.schema.json')
            report['checkedFiles'].append(m['workflow'])
            steps=unique(wf['steps'],'id','workflow.steps')
            for step in steps.values():
                if step['id'] in step['dependsOn'] or not set(step['dependsOn']) <= set(steps):
                    fail('D10','workflow','Invalid step dependency')
                if step['type']=='approval':
                    if step['policyRef'] not in host['approvalPolicies']:
                        fail('D10','workflow','Unknown host approval policy')
                else:
                    binds, catalog = (queries,hqueries) if step['type']=='query' else (actions,hactions)
                    if step['binding'] not in binds:
                        fail('D10','workflow','Unknown step binding')
                    contract=catalog[binds[step['binding']]['contract']]
                    modes_needed={'automation'} if level==4 else {'workflow'}
                    if manual_workflow:
                        modes_needed.add('workflow')
                    if not modes_needed <= set(contract['modes']):
                        fail('D10','workflow','Contract disallows this execution mode')
            completed=set()
            while len(completed)<len(steps):
                ready={k for k,s in steps.items() if k not in completed and set(s['dependsOn'])<=completed}
                if not ready:
                    fail('D10','workflow','Workflow graph has a cycle')
                completed.update(ready)
        if 'automation' in m:
            auto=read_doc(folder,m['automation'],'automation.schema.json')
            report['checkedFiles'].append(m['automation'])
            if auto['workflow']!=m['workflow']:
                fail('D11','automation','Workflow reference mismatch')
            trigger=auto['trigger']
            if trigger['kind']=='daily':
                if trigger['timezone'] not in host['timezones']:
                    fail('D11','automation','Timezone not advertised by host fixture')
            else:
                events=unique(host['events'],'id','host.events')
                if trigger['contract'] not in events or not in_range(events[trigger['contract']]['version'],trigger):
                    fail('D11','automation','Event contract unavailable')
            report['warnings'].append('Automation proposal only. No mandate exists and no job was scheduled.')
        if m['license']['status']=='unspecified':
            report['warnings'].append('Licence rights must be resolved before distribution or installation.')
        report.update(status='design-checked',capabilityLevel=level,pageId=m['id'],
                      hostEvidence=host.get('status','unspecified'))
    except Invalid as e:
        report['errors'].append({'code':e.code,'path':e.path,'message':e.message})
    except (ValueError,KeyError,TypeError,OSError,RuntimeError,RecursionError) as e:
        report['errors'].append({'code':'D00','path':'document','message':'Cannot check design: '+type(e).__name__})
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder'); parser.add_argument('--host')
    a=parser.parse_args()
    result=check(a.folder,load_json(a.host) if a.host else None)
    print(json.dumps(result,indent=2))
    return 0 if result['status']=='design-checked' else 1


if __name__=='__main__': sys.exit(main())
