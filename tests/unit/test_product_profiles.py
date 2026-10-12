"""All product values below are TEST fixtures, registered only in temporary databases."""
import base64
import copy
import json
from pathlib import Path
import pytest
from ssd_validator.application.database_workflow import DatabaseWorkflow
from ssd_validator.application.knowledge_management import change_entity
from ssd_validator.application.product_profiles import FirmwareComparison,ProductProfile,match_profile,PRODUCTS

ROOT=Path(__file__).resolve().parents[2]
BUNDLE='nvme-2.1-nvm-1.1'
PROV={'source_type':'fixture','source_document':'TEST_PRODUCT_DOC','source_version':'v1','source_section':'Synthetic product test only','status':'provisional'}

def profile(identity='TEST_PROFILE',**kwargs):
    return dict(profile_id=identity,title='Synthetic TEST only',bundle_id=BUNDLE,policy_ids=['TEST_POLICY'],context_id='TEST_CONTEXT',
        conditions=[{'source':'observed','path':'model','value':'TEST_MODEL'}],provenance=PROV,**kwargs)

def package(support=6,fw='1.2.0',nsids=()):
    raw=f'NVME Identify Controller:\nmn:TEST_MODEL\nfr:{fw}\nsn:TEST_SERIAL\nsqes:0x66\ncqes:0x44\nnpss:4\nawun:0\nawupf:0\noacs:{support}\n'.encode()
    captures=[{'capture_id':'TEST_CTRL','filename':'TEST_CTRL.txt','command':'id-ctrl','dut_id':'TEST_DUT','session_id':'TEST_SESSION','content_base64':base64.b64encode(raw).decode()}]
    captures.extend({'capture_id':'TEST_NS'+str(n),'filename':'TEST_NS.txt','command':'id-ns','dut_id':'TEST_DUT','session_id':'TEST_SESSION','nsid':n,'content_base64':base64.b64encode(b'NVME Identify Namespace:\nnsze:100\n').decode()} for n in nsids)
    return {'captures':captures}

@pytest.fixture
def workflow(tmp_path):
    w=DatabaseWorkflow(ROOT,tmp_path/'test.sqlite3')
    sources=w.repository.sources()
    sources=change_entity(sources,kind='document',payload={**{k:PROV[k] for k in ('source_type','source_document','source_version')},'title':'Synthetic TEST only'})
    original=next(r for r in w.knowledge(BUNDLE)['rules'] if r['check']['type']=='CAPABILITY')
    rule=copy.deepcopy(original);rule.update(rule_id='TEST.PRODUCT.REQUIRED',condition=None,provenance=PROV)
    reg={'format_version':1,'profiles':[profile()],
        'contexts':[{'context_id':'TEST_CONTEXT','title':'TEST context','bundle_id':BUNDLE,'facts':{'logical_block_atomic_parameters_applicable':False,'TEST.feature':True},'fact_kinds':{'logical_block_atomic_parameters_applicable':'assumption','TEST.feature':'declared'},'provenance':PROV}],
        'policies':[{'policy_id':'TEST_POLICY','title':'TEST required feature','bundle_id':BUNDLE,'rules':[rule],'provenance':PROV}]}
    sources[PRODUCTS]=json.dumps(reg)
    w.import_sources({'format':'ssd-validator-source-v1','sources':sources},expected_revision=1,reason='TEST synthetic product registry')
    return w

def save(w,kind,identity,payload,bundle=BUNDLE):
    body={'kind':kind,'bundle_id':bundle,'original_id':identity,'payload':payload,'expected_revision':w.repository.head(),'reason':'TEST edit'}
    preview=w.preview_change(body)
    return w.save_change({**body,'preview_hash':preview['preview_hash']})

@pytest.mark.parametrize('method,params,actual,bound,state',[
    ('exact',{},'FW10','FW2','FALSE'),
    ('exact',{},'FW2','FW2','TRUE'),
    ('numeric_components',{'component_count':3},'1.10.0','1.2.0','TRUE'),
    ('numeric_components',{'component_count':3},'1.2.0','1.2.0','TRUE'),
    ('numeric_components',{'component_count':3},'1.1.9','1.2.0','FALSE'),
    ('numeric_components',{'component_count':3},'FW1.2.0','1.2.0','UNKNOWN'),
    ('numeric_components',{'component_count':3},'1.2','1.2.0','UNKNOWN'),
    ('ordered_labels',{'labels':['FW2','FW10','FW3']},'FW10','FW2','TRUE'),
    ('ordered_labels',{'labels':['FW2','FW10','FW3']},'UNLISTED','FW2','UNKNOWN')])
def test_registered_fw_modes_and_boundaries(method,params,actual,bound,state):
    p=ProductProfile.model_validate({**profile(),'firmware_comparison':{'method':method,**params},
        'conditions':[{'source':'observed','path':'firmware','operator':'EQ','value':bound} if method=='exact' else
                      {'source':'observed','path':'firmware','operator':'FW_RANGE','minimum':bound}]})
    result=match_profile(p,{'firmware':actual},{})
    assert result['state']==state and result['trace'][0]['actual']==actual

def test_missing_fw_definition_and_condition_never_inferred():
    p=ProductProfile.model_validate({**profile(),'conditions':[{'source':'observed','path':'firmware','value':'1.2.0'}]})
    assert match_profile(p,{'firmware':'1.2.0'},{})['state']=='UNKNOWN'
    assert match_profile(p,{}, {})['state']=='UNKNOWN'
    p=ProductProfile.model_validate({**profile(),'conditions':[{'source':'user','path':'TEST.feature','value':True}]})
    assert match_profile(p,{}, {'TEST.feature':1})['state']=='FALSE'
    with pytest.raises(ValueError):FirmwareComparison(method='numeric_components')
    with pytest.raises(ValueError):FirmwareComparison(method='ordered_labels',labels=['same','same'])

def test_explicit_profile_policy_context_origins_and_capability_bypass(workflow):
    w=workflow
    r=w.analyze_captures(package(),BUNDLE,profile_id='TEST_PROFILE',context_facts={'TEST.user':'INPUT'})
    s=r['scopes'][0];selected=s['product_selection']
    assert r['validation']['status']=='PASS'
    assert selected['observed']['firmware']=='1.2.0'
    assert selected['user_inputs']=={'TEST.user':'INPUT'}
    assert selected['assumptions']=={'logical_block_atomic_parameters_applicable':False}
    assert selected['declared_context']=={'TEST.feature':True}
    assert selected['profile']['profile_id']=='TEST_PROFILE' and selected['policy_requirements']
    assert s['validation']['profile']['context']['facts']['TEST.user']=='INPUT'
    assert not r['assumptions'] # Legacy LAB policy/default assumptions do not leak into selected Profile.
    bad=w.analyze_captures(package(support=0),BUNDLE,profile_id='TEST_PROFILE')
    result=next(r for r in bad['validation']['results'] if r['rule']['rule_id'].startswith('TEST.PRODUCT.REQUIRED'))
    assert result['status']=='FAIL' and bad['validation']['status']=='FAIL'
    with pytest.raises(ValueError,match='BUNDLE_MISMATCH'):
        w.analyze_captures(package(),'nvme-2.0e-nvm-1.0e',profile_id='TEST_PROFILE')
    with pytest.raises(ValueError,match='not user-overridable'):
        w.analyze_captures(package(),BUNDLE,profile_id='TEST_PROFILE',context_facts={'product.profile_applicable':True})

def test_proposals_none_multiple_pending_and_explicit_unknown_gates(workflow):
    w=workflow
    suggestion=w.suggest_profiles(package(),BUNDLE)
    assert suggestion['scopes'][0]['status']=='CANDIDATE' and suggestion['automatic_selection'] is False
    assert suggestion['scopes'][0]['selected_profile_id'] is None
    other=profile('TEST_OTHER');save(w,'profile',None,other)
    assert w.suggest_profiles(package(),BUNDLE)['scopes'][0]['status']=='AMBIGUOUS'
    unknown=profile('TEST_UNKNOWN');unknown['conditions']=[{'source':'user','path':'missing','value':True}]
    save(w,'profile',None,unknown)
    r=w.analyze_captures(package(),BUNDLE,profile_id='TEST_UNKNOWN')
    assert r['validation']['status']=='UNKNOWN'
    assert next(v for v in r['validation']['results'] if v['rule']['rule_id'].startswith('TEST.PRODUCT.REQUIRED'))['status']=='UNKNOWN'
    data=package();raw=base64.b64decode(data['captures'][0]['content_base64']).replace(b'TEST_MODEL',b'DIFFERENT');data['captures'][0]['content_base64']=base64.b64encode(raw).decode()
    none=w.suggest_profiles(data,BUNDLE)['scopes'][0]
    assert none['status']=='UNKNOWN' and not none['candidates'] and none['pending']==['TEST_UNKNOWN']
    mismatch=w.analyze_captures(data,BUNDLE,profile_id='TEST_PROFILE')
    assert mismatch['validation']['status']=='N/A'

def test_revision_replay_namespaces_backup_and_reference_guards(workflow,tmp_path):
    w=workflow
    original=w.analyze_captures(package(nsids=(1,2)),BUNDLE,profile_id='TEST_PROFILE')
    assert len(original['scopes'])==2
    for scope in original['scopes']:
        assert scope['product_selection']['effective_context']['facts']['namespace.nsid']==scope['nsid']
        assert scope['product_selection']['observed']['namespace.nsid']==scope['nsid']
    policy=w.products()['policies'][0];policy['rules'][0]['check']['support']='unsupported'
    save(w,'product_policy','TEST_POLICY',policy)
    assert w.analyze_captures(package(),BUNDLE,profile_id='TEST_PROFILE')['validation']['status']=='FAIL'
    assert w.load_run(original['run_id'])==original
    assert w.replay(original['run_id'])['scopes']==original['scopes']
    p=w.products()['profiles'][0];p['context_id']='MISSING'
    with pytest.raises(ValueError,match='Context references'):
        save(w,'profile','TEST_PROFILE',p)
    p=w.products()['profiles'][0];p['policy_ids']=['MISSING']
    with pytest.raises(ValueError,match='policy references'):
        save(w,'profile','TEST_PROFILE',p)
    body={'kind':'context','bundle_id':BUNDLE,'original_id':'TEST_CONTEXT','delete':True,'expected_revision':w.repository.head(),'reason':'TEST delete referenced'}
    with pytest.raises(ValueError):w.preview_change(body)
    restored=DatabaseWorkflow(ROOT,tmp_path/'restored.sqlite3')
    restored.restore_database(w.backup_database()['content_base64'],expected_revision=1)
    assert restored.replay(original['run_id'])['scopes']==original['scopes']
    assert restored.database_status()['schema_version']=='3'

def test_management_search_review_cas_and_context_override(workflow):
    w=workflow
    assert w.entity_search(kind='profile',search='TEST')['items']
    context=w.products()['contexts'][0]
    r=w.analyze_captures(package(),BUNDLE,profile_id='TEST_PROFILE',context_facts={'TEST.feature':None,'logical_block_atomic_parameters_applicable':True})
    selection=r['scopes'][0]['product_selection']
    assert 'TEST.feature' not in selection['effective_context']['facts']
    assert selection['assumptions']['logical_block_atomic_parameters_applicable'] is False
    assert selection['effective_context']['facts']['logical_block_atomic_parameters_applicable'] is True
    body={'kind':'context','bundle_id':BUNDLE,'original_id':'TEST_CONTEXT','payload':context,'expected_revision':w.repository.head(),'reason':'TEST change'}
    context['title']='TEST renamed';preview=w.preview_change(body)
    w.save_change({**body,'preview_hash':preview['preview_hash']})
    with pytest.raises(ValueError,match='REVISION_CONFLICT'):w.save_change({**body,'preview_hash':preview['preview_hash']})
    context['provenance']={**PROV,'status':'confirmed','verified_by':'TEST_REVIEWER','verified_date':'2026-10-12'}
    with pytest.raises(ValueError,match='review'):save(w,'context','TEST_CONTEXT',context)
