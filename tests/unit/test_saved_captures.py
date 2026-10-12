"""Synthetic input routing; all editable test knowledge stays in temporary SQLite."""
import base64
import copy
import json
from pathlib import Path
import pytest
from ssd_validator.application.database_workflow import DatabaseWorkflow
from ssd_validator.models.saved_captures import SavedCaptureSet

ROOT=Path(__file__).resolve().parents[2]
BUNDLE='nvme-2.1-nvm-1.1'
CTRL=b'NVME Identify Controller:\nsqes:0x66\ncqes:0x44\nnpss:4\nawun:0\nawupf:0\noacs:6\n'
NS=b'NVME Identify Namespace 1:\nnsze:100\nncap:90\nnuse:80\nlbaf 0 : ms:0 lbads:9 rp:0\nlbaf 1 : ms:0 lbads:12 rp:1\nfuture_field:77\n'

def capture(identity,data=CTRL,command='id-ctrl',**kwargs):
    return dict(capture_id=identity,filename=identity+'.txt',command=command,
        content_base64=base64.b64encode(data).decode('ascii'),**kwargs)

def package(*caps):
    return {'format':'ssd-validator-captures-v1','captures':list(caps)}

@pytest.fixture
def workflow(tmp_path):
    return DatabaseWorkflow(ROOT,tmp_path/'test.sqlite3')

def run(workflow,*caps,**kwargs):
    return workflow.analyze_captures(package(*caps),BUNDLE,**kwargs)

def save(workflow,body):
    body.update(expected_revision=workflow.repository.head(),reason='TEST synthetic only')
    preview=workflow.preview_change(body)
    return workflow.save_change({**body,'preview_hash':preview['preview_hash']})

def add_namespace_fixture(workflow):
    original=next(e for e in workflow.entity_search(kind='field',bundle_id=BUNDLE)['items'] if e['entity_id']=='NVME.CNS01.OACS')
    for name,offset,count in [('NSIZE',300,None),('ARRAY',320,2)]:
        value=copy.deepcopy(original['payload'])
        value['schema'].update(field_id='TEST.'+name,name=name,command='id-ns',offset=offset,value_type='integer')
        value['binding'].update(cns=0,csi=0,array_count=count,array_stride=2 if count else None)
        value['evidence']['description']='TEST FIXTURE ONLY, not actual specification knowledge'
        save(workflow,dict(kind='field',bundle_id=BUNDLE,payload=value))
    original=next(e for e in workflow.entity_search(kind='rule',bundle_id=BUNDLE)['items'] if e['entity_id']=='EXPERIMENTAL.POWER_STATE_LIMIT')
    for name,index,limit in [('NSIZE',None,100),('ARRAY',0,10),('ARRAY',1,20)]:
        value=copy.deepcopy(original['payload'])
        value.update(rule_id='TEST.'+name+str(index))
        value['provenance']['source_section']='TEST FIXTURE ONLY; temporary routing test, not specification requirement'
        value['target']={'field_id':'TEST.'+name,'index':index}
        value['check']={'type':'MAX','value':limit}
        save(workflow,dict(kind='rule',bundle_id=BUNDLE,payload=value))
    value=copy.deepcopy(original['payload'])
    value.update(rule_id='TEST.CROSS_RESPONSE',target={'field_id':'TEST.NSIZE'},
        check={'type':'FIELD_COMPARE','operator':'>=','other':{'field_id':'NVME.CNS01.NPSS'}})
    value['provenance']['source_section']='TEST synthetic cross-response relation only'
    save(workflow,dict(kind='rule',bundle_id=BUNDLE,payload=value))

def test_explicit_link_and_unknown_metadata_preserved(workflow):
    r=run(workflow,capture('ctrl',dut_id='TEST_DUT',session_id='TEST_SESSION',tool_version='2.3'),
        capture('ns',NS,'id-ns',dut_id='TEST_DUT',session_id='TEST_SESSION',nsid=1))
    assert len(r['scopes'])==1 and r['scopes'][0]['nsid']==1
    assert r['validation']['status']=='PASS' and len(r['validation']['results'])==6
    assert r['authoritative'] is False
    assert r['captures'][0]['metadata']['cns']=='UNKNOWN'
    assert r['captures'][1]['metadata']['csi']=='UNKNOWN'
    assert r['captures'][0]['metadata']['tool_version']=='2.3'
    assert r['bundle']['bundle_id']==BUNDLE
    assert len([o for o in r['captures'][1]['observations'] if o['field']=='lbads'])==2
    assert any(o['field']=='future_field' for o in r['captures'][1]['observations'])
    assert r['captures'][1]['original_content_base64']==base64.b64encode(NS).decode()
    assert workflow.replay(r['run_id'])['scopes']==r['scopes']
    assert workflow.database_status()['schema_version']=='3'
    generic=run(workflow,capture('generic',b'{"sqes":102,"cqes":68,"npss":4,"awun":0,"awupf":0,"oacs":6}',
        'identify',source_format='json',cns=1,csi=0,dut_id='A',session_id='S'),
        capture('ns',NS,'id-ns',dut_id='A',session_id='S',nsid=1))
    assert len(generic['scopes'])==1 and generic['validation']['status']=='PASS'

def test_dut_session_and_unknown_namespace_isolation(workflow):
    caps=[capture('ctrl',dut_id='A',session_id='S'),capture('ns1',NS,'id-ns',dut_id='A',session_id='S',nsid=1),
        capture('ns2',NS,'id-ns',dut_id='A',session_id='S',nsid=2),capture('other',NS,'id-ns',dut_id='B',session_id='S',nsid=1),
        capture('newsession',NS,'id-ns',dut_id='A',session_id='NEW',nsid=1),
        capture('unknown1',NS,'id-ns',dut_id='A',session_id='S'),capture('unknown2',NS,'id-ns',dut_id='A',session_id='S'),
        capture('anonymous',NS,'id-ns')]
    r=run(workflow,*caps)
    assert len(r['scopes'])==7
    for scope in r['scopes']:
        if scope['dut_id']!='A' or scope['session_id']!='S':
            assert 'ctrl' not in scope['capture_ids']
    assert sum(s['nsid']=='UNKNOWN' for s in r['scopes'])==3

def test_namespace_array_relations_json_raw_and_missing(workflow):
    add_namespace_fixture(workflow)
    shared=dict(dut_id='TEST',session_id='S',cns=0,csi=0)
    first=capture('ns1',b'NVME Identify Namespace:\nNSIZE:100\nARRAY[0]:10\nARRAY[1]:20\n','id-ns',nsid=1,**shared)
    second=capture('ns2',json.dumps({'NSIZE':101,'ARRAY':[10,21],'extra':{'x':[1,2]}}).encode(),'id-ns',nsid=2,source_format='json',**shared)
    r=run(workflow,capture('ctrl',dut_id='TEST',session_id='S'),first,second)
    assert len(r['scopes'])==2
    target=lambda scope:[v for v in scope['validation']['results'] if v['rule']['rule_id'].startswith('TEST.')]
    assert [v['status'] for v in target(r['scopes'][0])]==['PASS']*4
    assert sum(v['status']=='FAIL' for v in target(r['scopes'][1]))==2
    assert r['captures'][2]['tool_output']['extra']=={'x':[1,2]}
    refs=[f['field'] for f in r['scopes'][1]['actual_facts'] if f['field']['field_id']=='TEST.ARRAY']
    assert {ref['index'] for ref in refs}=={0,1}
    raw=bytearray(4096); raw[300:302]=(100).to_bytes(2,'little');raw[320:322]=(10).to_bytes(2,'little');raw[322:324]=(20).to_bytes(2,'little');raw[1000]=99
    raw_report=run(workflow,capture('ctrl',dut_id='TEST',session_id='S'),capture('raw',bytes(raw),'id-ns',source_format='raw',nsid=1,**shared))
    assert all(v['status']=='PASS' for v in target(raw_report['scopes'][0]))
    assert raw_report['captures'][1]['normalization']['unmapped_bytes']
    missing=run(workflow,capture('missing',b'NVME Identify Namespace:\nNSIZE:99\n','id-ns',nsid=1,**shared))
    assert sum(v['status']=='UNKNOWN' for v in target(missing['scopes'][0]))==3

@pytest.mark.parametrize('data,format',[(b'NVME Identify Controller:\nsqes:0x66\nsqes:0x77\n','text'),
    (b'{"sqes":102,"sqes":119}','json'),(b'{"sqes":102,"SQES":119}','json')])
def test_duplicates_preserved_no_winner(workflow,data,format):
    r=run(workflow,capture('duplicate',data,source_format=format))
    assert r['validation']['status']=='CONFLICT'
    assert not any(f['field']['field_id'].endswith('.SQES') for f in r['scopes'][0]['actual_facts'])
    assert r['captures'][0]['original_content_base64']==base64.b64encode(data).decode()

def test_multiple_responses_conflict_and_types_query_errors(workflow):
    common=dict(dut_id='A',session_id='S')
    r=run(workflow,capture('one',**common),capture('two',**common))
    assert r['validation']['status']=='CONFLICT' and r['scopes'][0]['conflicts']
    assert not r['scopes'][0]['actual_facts']
    r=run(workflow,capture('bad',b'{"sqes":"102"}',source_format='json'))
    assert r['validation']['status']=='ERROR'
    r=run(workflow,capture('badquery',cns=0,csi=0))
    assert r['validation']['status']=='ERROR' and not r['scopes'][0]['actual_facts']
    r=run(workflow,capture('raw',bytes(4096),source_format='raw'))
    assert r['captures'][0]['metadata']['cns']=='UNKNOWN' and not r['scopes'][0]['actual_facts']
    with pytest.raises(ValueError):
        SavedCaptureSet.model_validate(package(capture('x',cns=True)))
    with pytest.raises(ValueError,match='Duplicate capture_id'):
        SavedCaptureSet.model_validate(package(capture('x'),capture('x')))
    assert SavedCaptureSet.model_validate(package(capture('zero',nsid=0))).captures[0].nsid==0

def test_old_and_multi_history_pinned_revision_backup_restore(workflow,tmp_path):
    old=workflow.analyze(CTRL,'old.txt',BUNDLE,experimental=True)
    multi=run(workflow,capture('ctrl'))
    rule=next(e for e in workflow.knowledge(BUNDLE)['rules'] if e['rule_id']=='EXPERIMENTAL.POWER_STATE_LIMIT')
    rule['check']['value']=3
    workflow.edit_rule(BUNDLE,expected_revision=1,reason='TEST edit',rule=rule,original_rule_id=rule['rule_id'])
    assert run(workflow,capture('new'))['validation']['status']=='FAIL'
    backup=workflow.backup_database()
    other=DatabaseWorkflow(ROOT,tmp_path/'restored.sqlite3')
    other.restore_database(backup['content_base64'],expected_revision=1)
    assert other.replay(old['run_id'])['validation']==old['validation']
    assert other.replay(multi['run_id'])['scopes']==multi['scopes']

def test_extra_nested_json_is_not_a_known_scalar_alias(workflow):
    r=run(workflow,capture('extra',b'{"extensions":{"sqes":102},"future":[{"sqes":102}]}',source_format='json'))
    assert not r['scopes'][0]['actual_facts']
    assert all(not o['field_ids'] for o in r['captures'][0]['observations'])
    assert r['captures'][0]['tool_output']['extensions']['sqes']==102
    assert r['validation']['status']=='UNKNOWN'

def test_real_controller_regression_when_supplied(workflow):
    path=ROOT.parent/'id-ctrl_test.txt'
    if not path.exists():
        pytest.skip('User supplied real controller log unavailable')
    old=workflow.analyze(path.read_bytes(),path.name,BUNDLE,experimental=True)
    new=run(workflow,capture('real_ctrl',path.read_bytes()))
    assert old['validation']['status']==new['validation']['status']=='PASS'
    assert [v['status'] for v in old['validation']['results']]==[v['status'] for v in new['validation']['results']]
