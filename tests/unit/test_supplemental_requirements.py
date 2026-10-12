"""TEST product associations only; no real policy or reviewer is fabricated."""
import base64
import copy
import json
from pathlib import Path
import pytest
from ssd_validator.application.database_workflow import DatabaseWorkflow
from ssd_validator.application.knowledge_management import change_entity,dump,METADATA,metadata
from ssd_validator.application.nvme_expansion import prepare_sources as prepare_nvme,PACK_PATH
from ssd_validator.application.product_profiles import PRODUCTS
from ssd_validator.application.supplemental_requirements import CANDIDATE_PATH,REGISTRY_PATH,parse,prepare_sources,register,overview
from ssd_validator.models.runtime import EffectiveExpectedProfile,ActualFact
from ssd_validator.resolver import evaluate

ROOT=Path(__file__).resolve().parents[2]
PACK=parse((ROOT/CANDIDATE_PATH).read_text(encoding='utf-8'))
P={'source_type':'fixture','source_document':'TEST_PRODUCT','source_version':'v1','source_section':'Synthetic TEST only','status':'provisional'}
CONF={**P,'status':'confirmed','verified_by':'TEST_REVIEWER','verified_date':'2026-10-12'}

@pytest.fixture(scope='module')
def w(tmp_path_factory):
    workflow=DatabaseWorkflow(ROOT,tmp_path_factory.mktemp('supplemental')/'TEST.sqlite3')
    sources=prepare_nvme(workflow.repository.sources(),json.loads((ROOT/PACK_PATH).read_text(encoding='utf-8')))
    sources=prepare_sources(sources,PACK)
    sources=change_entity(sources,kind='document',payload={k:P[k] for k in ('source_type','source_document','source_version')})
    products=json.loads(sources[PRODUCTS])
    for b in PACK.bundles:
        products['profiles'].append({'profile_id':'TEST.'+b.bundle_id,'title':'Synthetic test binding only','bundle_id':b.bundle_id,
            'policy_ids':[b.policy.policy_id],'conditions':[],'provenance':P})
    sources[PRODUCTS]=dump(products)
    workflow.import_sources({'format':'ssd-validator-source-v1','sources':sources},expected_revision=1,reason='TEST supplemental bindings')
    return workflow

def captures(namespace=True,oacs=94):
    ctrl=f'NVME Identify Controller:\nsqes:0x66\ncqes:0x44\nnpss:0\nawun:1\nawupf:1\noacs:{oacs}\nfuses:1\nacwu:0\nhmpre:0\nhmmin:0\ndsto:0\nrpmbs:0\n'.encode()
    caps=[{'capture_id':'TEST_CTRL','filename':'TEST.txt','command':'id-ctrl','dut_id':'TEST','session_id':'TEST','content_base64':base64.b64encode(ctrl).decode()}]
    if namespace:
        ns=b'NVME Identify Namespace:\nnsze:100\nncap:100\nnuse:50\nnsfeat:16\nnlbaf:0\nlbaf 0 : ms:0 lbads:9 rp:0\n'
        caps.append({'capture_id':'TEST_NS','filename':'TEST_NS.txt','command':'id-ns','dut_id':'TEST','session_id':'TEST','nsid':1,'content_base64':base64.b64encode(ns).decode()})
    return {'captures':caps}

CTX={'ocp.datacenter_product':True,'ocp.version':'2.6','host.lbaf_extension_enabled':False,'namespace.lbaf.0.metadata_supported':False}

@pytest.fixture(scope='module')
def reports(w):
    return {b.bundle_id:w.analyze_captures(captures(),b.bundle_id,profile_id='TEST.'+b.bundle_id,context_facts=CTX) for b in PACK.bundles}

CASES=[(b.bundle_id,r.rule_id) for b in PACK.bundles for r in b.policy.rules]
@pytest.mark.parametrize('bundle,rid',CASES)
def test_each_requirement_normal_violation_boundary_condition_missing_and_source(reports,bundle,rid):
    report=reports[bundle];scope=report['scopes'][0];full=EffectiveExpectedProfile.model_validate(scope['validation']['profile'])
    entry=next(e for e in full.entries if e.rule.rule_id==rid or e.rule.origin_rule_id==rid)
    p=full.model_copy(update={'entries':(entry,)})
    facts=[ActualFact.model_validate(f) for f in scope['actual_facts']]
    assert evaluate(p,tuple(facts)).results[0].status=='PASS'
    assert entry.rule.provenance.source_document=='OCP_DSSD_2_6' and entry.rule.provenance.status=='candidate'
    if entry.rule.origin=='mapping':assert entry.rule.supporting_evidence[0].source_document.startswith(('BASE_','NVM_'))
    def changed(value):return tuple(f.model_copy(update={'value':value}) if f.field.field_id==entry.rule.target.field_id else f for f in facts)
    original=next(f.value for f in facts if f.field.field_id==entry.rule.target.field_id)
    bad=original^(1<<entry.rule.target.bit) if entry.rule.target.bit is not None else original^0x10 if entry.rule.check.type=='MASK' else 1
    assert evaluate(p,changed(bad)).results[0].status=='FAIL'
    boundary=(original&(1<<entry.rule.target.bit)) if entry.rule.target.bit is not None else original
    assert evaluate(p,changed(boundary)).results[0].status=='PASS'
    if bundle=='nvme-2.1-nvm-1.1' and entry.rule.target.field_id=='NVME.CNS00.NSFEAT':
        assert evaluate(p,changed(0x30)).results[0].status=='PASS' # OPTPERF=11b preserves bit5.
        assert evaluate(p,changed(0x20)).results[0].status=='FAIL' # OPTPERF=10b nonzero is not OCP bit4 support.
    missing=tuple(f for f in facts if f.field.field_id!=entry.rule.target.field_id)
    assert evaluate(p,missing).results[0].status=='UNKNOWN'
    for ctx,state in [({**CTX,'product.profile_applicable':True,'ocp.datacenter_product':False},'N/A'),
        ({'product.profile_applicable':True,'ocp.datacenter_product':True},'UNKNOWN'),
        ({**CTX,'product.profile_applicable':True,'ocp.version':'2.5'},'N/A')]:
        ctx.update({'input.has_namespace':True,'namespace.query_is_specific':True})
        profile=p.model_copy(update={'context':p.context.model_copy(update={'facts':ctx})})
        assert evaluate(profile,tuple(facts)).results[0].status==state
    trace=next(r for r in scope['supplemental_trace']['requirements'] if r['requirement']['rule_id']==rid)
    assert trace['execution']=='evaluated' and trace['outcomes'][0]['status']=='PASS'
    assert scope['supplemental_trace']['registry_source']['sha256']

def test_support_bits_do_not_disable_mandatory_requirements(w):
    bundle=PACK.bundles[0].bundle_id
    r=w.analyze_captures(captures(oacs=0),bundle,profile_id='TEST.'+bundle,context_facts=CTX)
    caps=[r for r in r['validation']['results'] if (r['rule'].get('origin_rule_id') or '').startswith('OCP.')]
    assert any(x['status']=='FAIL' for x in caps)
    no_profile=w.analyze_captures(captures(),bundle,context_facts=CTX)
    assert not any(r['rule']['rule_id'].startswith('OCP.') for r in no_profile['validation']['results'])
    assert all(r['execution']=='not_selected' for r in no_profile['scopes'][0]['supplemental_trace']['requirements'])
    assert w.replay(r['run_id'])['scopes']==r['scopes']
    review=w.analyze_captures(captures(),bundle,profile_id='TEST.'+bundle,context_facts=CTX,experimental=False)
    assert all(q['execution']=='review_only' and not q['outcomes'] for q in review['scopes'][0]['supplemental_trace']['requirements'])

def test_cross_source_conflict_and_confirmed_override_preserves_both(w,tmp_path):
    sources=w.repository.sources();bundle=PACK.bundles[1].bundle_id
    products=json.loads(sources[PRODUCTS]);policy=next(p for p in products['policies'] if p['bundle_id']==bundle)
    # Synthetic contrary product value, never a Samsung or OCP policy claim.
    test_rule={'rule_id':'TEST.PRODUCT.CONTRARY','target':{'field_id':'NVME.CNS01.SQES'},'check':{'type':'EXACT','value':0x76},'provenance':P}
    policy['rules'].append(test_rule);sources[PRODUCTS]=dump(products)
    local=DatabaseWorkflow(ROOT,tmp_path/'TEST-conflict.sqlite3');local.import_sources({'format':'ssd-validator-source-v1','sources':sources},expected_revision=1,reason='TEST conflict')
    result=local.analyze_captures(captures(),bundle,profile_id='TEST.'+bundle,context_facts=CTX)
    assert result['validation']['status']=='CONFLICT'
    assert any(any(r['provenance']['source_document']=='OCP_DSSD_2_6' for r in c['rules']) and any(r['provenance']['source_document']=='TEST_PRODUCT' for r in c['rules']) for c in result['scopes'][0]['supplemental_trace']['conflicts'])
    assert any(any(r['provenance']['source_document']=='BASE_2_1' for r in c['rules']) for c in result['scopes'][0]['supplemental_trace']['conflicts'])
    original=next(r for r in policy['rules'] if r['rule_id']=='OCP.2_6.NVMe-CFG-14.SQES')
    test_rule['provenance']=CONF;test_rule['override']={'enabled':True,'overrides':[original['rule_id']],'reason':'Synthetic TEST approved exception; not real override permission','provenance':CONF}
    sources[PRODUCTS]=dump(products)
    from ssd_validator.application.product_profiles import ProductPolicy
    from hashlib import sha256
    meta=metadata(sources);meta['reviews'].append({'kind':'product_policy','bundle_id':bundle,'entity_id':policy['policy_id'],'target_hash':sha256(dump(ProductPolicy.model_validate(policy).model_dump(mode='json')).encode()).hexdigest(),'reviewer':'TEST_REVIEWER','reviewed_date':'2026-10-12','basis':'Synthetic TEST override evidence; no real policy permission'})
    meta['reviews'].append({**meta['reviews'][-1],'target_hash':'0'*64,'basis':'Obsolete TEST review must not be attached'})
    sources[METADATA]=dump(meta)
    local.import_sources({'format':'ssd-validator-source-v1','sources':sources},expected_revision=2,reason='TEST reviewed override')
    result=local.analyze_captures(captures(),bundle,profile_id='TEST.'+bundle,context_facts=CTX)
    tr=result['scopes'][0]['supplemental_trace']['overrides'][0]
    assert tr['applied'] and tr['originals'][0]['status']=='N/A' and tr['replacement']['status']=='FAIL'
    assert len(tr['review_records'])==1 and tr['review_records'][0]['basis'].startswith('Synthetic TEST')
    assert tr['review_evidence']['verified_by']=='TEST_REVIEWER' and tr['originals'][0]['rule']['rule_id']==original['rule_id']
    assert local.replay(result['run_id'])['scopes']==result['scopes']

def test_registration_guards_and_reference_validation(w,tmp_path):
    sources=w.repository.sources();bad=copy.deepcopy(json.loads((ROOT/CANDIDATE_PATH).read_text(encoding='utf-8')))
    bad['bundles'][0]['policy']['provenance']['status']='confirmed'
    with pytest.raises(ValueError,match='candidate'):prepare_sources(sources,parse(json.dumps(bad)))
    changed=dict(sources);prod=json.loads(changed[PRODUCTS]);prod['policies'][0]['rules'][0]['check']['value']=0x70;changed[PRODUCTS]=dump(prod)
    with pytest.raises(ValueError,match='POLICY_EDIT_CONFLICT'):prepare_sources(changed,PACK)
    assert overview(changed)['bundles'][0]['registration_state']=='edited_review_needed'
    assert all(p.status=='excluded' for p in PACK.pending if p.item=='MFND')
    assert not any('Samsung' in p.title for p in __import__('ssd_validator.application.product_profiles',fromlist=['registry']).registry(sources).profiles)
    local=DatabaseWorkflow(ROOT,tmp_path/'TEST-register.sqlite3')
    nvme=prepare_nvme(local.repository.sources(),json.loads((ROOT/PACK_PATH).read_text(encoding='utf-8')))
    local.import_sources({'format':'ssd-validator-source-v1','sources':nvme},expected_revision=1,reason='TEST prerequisite')
    if not (ROOT.parent/'OCP2_6.pdf').exists():pytest.skip('Optional OCP original not supplied on this host')
    before=local.analyze(b'NVME Identify Controller:\noacs:6\n','TEST.txt',PACK.bundles[0].bundle_id,experimental=True)
    result=register(local,ROOT/CANDIDATE_PATH,ROOT.parent,expected_revision=2,reason='TEST source verification')
    assert result['revision']==3 and Path(result['pre_change_backup']).exists() and result['product_profiles_created']==0
    assert local.load_run(before['run_id'])==before
    assert register(local,ROOT/CANDIDATE_PATH,ROOT.parent,expected_revision=3,reason='TEST repeat')['changed'] is False
    with pytest.raises(ValueError,match='REVISION_CONFLICT'):register(local,ROOT/CANDIDATE_PATH,ROOT.parent,expected_revision=2,reason='TEST stale')
