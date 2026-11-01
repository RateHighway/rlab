import copy
import json
import pathlib
import shutil
import sys
import tempfile
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from check_design import check
from schema_subset import load_json


class DesignTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=pathlib.Path(self.tmp.name)/'design'
        self.host=load_json(ROOT/'fixtures/host-catalog.json')

    def tearDown(self): self.tmp.cleanup()

    def setup_level(self, level):
        shutil.copytree(str(ROOT/'examples'/('level-'+str(level))),str(self.path))

    def edit(self,name,fn):
        p=self.path/name
        value=load_json(p); fn(value)
        p.write_text(json.dumps(value),encoding='utf-8')

    def result(self): return check(self.path,self.host)

    def rejected(self,code=None):
        out=self.result()
        self.assertEqual(out['status'],'invalid',out)
        if code: self.assertEqual(out['errors'][0]['code'],code,out)

    def test_all_four_examples(self):
        for level in range(1,5):
            out=check(ROOT/'examples'/('level-'+str(level)))
            self.assertEqual(out['status'],'design-checked',out)
            self.assertEqual(out['capabilityLevel'],level)
            self.assertTrue(out['notTested'])

    def test_read_cannot_write(self):
        self.setup_level(2);self.edit('rlab-page.json',lambda m:m.update(capabilityLevel=1));self.rejected('D06')
    def test_workflow_cannot_hide_as_action(self):
        self.setup_level(3);self.edit('rlab-page.json',lambda m:m.update(capabilityLevel=2));self.rejected('D06')
    def test_automation_cannot_hide_as_workflow(self):
        self.setup_level(4);self.edit('rlab-page.json',lambda m:m.update(capabilityLevel=3));self.rejected('D06')
    def test_excess_level(self):
        self.setup_level(1);self.edit('rlab-page.json',lambda m:m.update(capabilityLevel=4));self.rejected('D06')
    def test_self_approved(self):
        self.setup_level(2);self.edit('rlab-page.json',lambda m:m.update(approved=True));self.rejected('RL002')
    def test_publisher_risk_rating(self):
        self.setup_level(2);self.edit('rlab-page.json',lambda m:m['actions'][0].update(risk='low'));self.rejected('RL002')
    def test_tokens_in_manifest(self):
        self.setup_level(1);self.edit('rlab-page.json',lambda m:m.update(accessToken='secret'));self.rejected('RL002')
    def test_unsupported_host_level(self):
        self.setup_level(3);self.host['maxLevel']=2;self.rejected('D04')
    def test_protocol_range(self):
        self.setup_level(1);self.host['hostApiVersion']='0.4.0';self.rejected('D04')
    def test_numeric_patch_comparison(self):
        self.setup_level(1);self.host['hostApiVersion']='0.3.100';self.assertEqual(self.result()['status'],'design-checked')
    def test_unknown_action(self):
        self.setup_level(2);self.edit('rlab-page.json',lambda m:m['actions'][0].update(contract='com.example.rates.publish'));self.rejected('D07')
    def test_contract_version(self):
        self.setup_level(1);self.host['queries'][0]['version']='2.0.0';self.rejected('D07')
    def test_missing_permission(self):
        self.setup_level(2);self.edit('rlab-page.json',lambda m:m['permissions']['requested'].remove('review-tasks.create'));self.rejected('D05')
    def test_unknown_permission(self):
        self.setup_level(1);self.edit('rlab-page.json',lambda m:m['permissions']['requested'].append('all.execute'));self.rejected('D05')
    def test_missing_input(self):
        self.setup_level(2);self.edit('rlab-page.json',lambda m:m['actions'][0]['inputBindings'].pop('title'));self.rejected('D08')
    def test_executable_binding(self):
        self.setup_level(1);self.edit('rlab-page.json',lambda m:m['queries'][0]['inputBindings'].update(locationIds={'expression':'fetch(secret)'}));self.rejected('RL002')
    def test_unsupported_context(self):
        self.setup_level(1);self.host['contextKeys']=[];self.rejected('D08')
    def test_raw_html_component(self):
        self.setup_level(1);self.edit('ui/main.json',lambda u:u['components'].append({'type':'HTML','html':'<script>bad()</script>'}));self.rejected('RL002')
    def test_unknown_ui_query(self):
        self.setup_level(1);self.edit('ui/main.json',lambda u:u['components'][1].update(query='missing'));self.rejected('D09')
    def test_unknown_ui_action(self):
        self.setup_level(2);self.edit('ui/main.json',lambda u:u['components'][2].update(action='missing'));self.rejected('D09')
    def test_unsupported_field(self):
        self.setup_level(1);self.edit('ui/main.json',lambda u:u['components'][1]['columns'].append('personalData'));self.rejected('D09')
    def test_surface_unavailable(self):
        self.setup_level(1);self.host['surfaces']=[];self.rejected('D04')
    def test_duplicate_query_name(self):
        self.setup_level(1);self.edit('rlab-page.json',lambda m:m['queries'].append(copy.deepcopy(m['queries'][0])));self.rejected('D03')
    def test_path_traversal(self):
        self.setup_level(1);self.edit('rlab-page.json',lambda m:m['surfaces'][0].update(entry='ui/../../outside.json'));self.rejected('D01')
    def test_workflow_cycle(self):
        self.setup_level(3);self.edit('workflows/main.json',lambda w:w['steps'][0].update(dependsOn=['create-task']));self.rejected('D10')
    def test_self_dependency(self):
        self.setup_level(3);self.edit('workflows/main.json',lambda w:w['steps'][0].update(dependsOn=['read-fleet']));self.rejected('D10')
    def test_unknown_approval_policy(self):
        self.setup_level(3);self.host['approvalPolicies']=[];self.rejected('D10')
    def test_workflow_unknown_binding(self):
        self.setup_level(3);self.edit('workflows/main.json',lambda w:w['steps'][2].update(binding='missing'));self.rejected('D10')
    def test_workflow_unsupported_mode(self):
        self.setup_level(3);self.host['actions'][0]['modes']=['user'];self.rejected('D10')
    def test_automation_unsupported_mode(self):
        self.setup_level(4);self.host['actions'][0]['modes']=['user','workflow'];self.rejected('D10')
    def test_manual_workflow_in_level_four_needs_workflow_permission(self):
        self.setup_level(4);self.host['actions'][0]['modes']=['automation'];self.rejected('D10')
    def test_no_self_mandate(self):
        self.setup_level(4);self.edit('automation/main.json',lambda a:a.update(mandate={'approved':True}));self.rejected('RL002')
    def test_no_live_default(self):
        self.setup_level(4);self.edit('automation/main.json',lambda a:a.update(initialMode='live'));self.rejected('RL002')
    def test_unknown_timezone(self):
        self.setup_level(4);self.edit('automation/main.json',lambda a:a['trigger'].update(timezone='Unknown/Zone'));self.rejected('D11')
    def test_workflow_reference_mismatch(self):
        self.setup_level(4);self.edit('automation/main.json',lambda a:a.update(workflow='workflows/other.json'));self.rejected('D11')
    def test_unknown_event(self):
        self.setup_level(4);self.edit('automation/main.json',lambda a:a.update(trigger={'kind':'event','contract':'com.example.changed','minimum':'1.0.0','maximumExclusive':'2.0.0'}));self.rejected('D11')
    def test_no_hidden_http_step(self):
        self.setup_level(3);self.edit('workflows/main.json',lambda w:w['steps'].append({'id':'leak','type':'http','url':'https://example.com','dependsOn':[]}));self.rejected('RL002')
    def test_unknown_runtime(self):
        self.setup_level(1);self.edit('rlab-page.json',lambda m:m['runtime'].update(kind='privileged-js'));self.rejected('RL002')
    def test_design_only(self):
        self.setup_level(1);self.edit('rlab-page.json',lambda m:m.update(stage='production'));self.rejected('RL002')
    def test_duplicate_json_key(self):
        self.setup_level(1);(self.path/'rlab-page.json').write_text('{"a":1,"a":2}',encoding='utf-8');self.rejected('RL002')


if __name__=='__main__':unittest.main()
