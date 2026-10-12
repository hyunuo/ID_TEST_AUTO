"""Source-linked candidate matrix; all Actual values below are synthetic TEST data."""
import base64
import copy
import json
from hashlib import sha256
from pathlib import Path
import pytest
from ssd_validator.application.database_workflow import DatabaseWorkflow
from ssd_validator.application.desktop_workflow import DesktopWorkflow
from ssd_validator.application.nvme_expansion import PACK_PATH,prepare_sources,validate_recipe,register
from ssd_validator.models.runtime import ActualFact,Condition,EffectiveExpectedProfile
from ssd_validator.resolver import evaluate

ROOT=Path(__file__).resolve().parents[2]
PACK=json.loads((ROOT/PACK_PATH).read_text(encoding='utf-8'))
NS='NVME.CNS00.';CTRL='NVME.CNS01.'

@pytest.fixture(scope='module')
def prepared(tmp_path_factory):
    w=DatabaseWorkflow(ROOT,tmp_path_factory.mktemp('stage5')/'test.sqlite3')
    sources=prepare_sources(w.repository.sources(),PACK)
    w.import_sources({'format':'ssd-validator-source-v1','sources':sources},expected_revision=1,reason='TEST stage5 only')
    return w

def contexts():
    return {'input.has_controller':True,'input.has_namespace':True,'namespace.query_is_specific':True,
        'namespace.nsid':1,'host.lbaf_extension_enabled':True,
        **{f'namespace.lbaf.{i}.metadata_supported':False for i in range(64)}}

@pytest.fixture(scope='module')
def profiles(prepared):
    result={}
    with prepared.repository.project(prepared.repository.sources()) as root:
        for b in PACK['bundles']:
            report=DesktopWorkflow(root).analyze(b'NVME Identify Controller:\nsn:TEST\n','TEST.txt',b['bundle_id'],
                experimental=True,context_facts=contexts(),scope_context=True)
            result[b['bundle_id']]=EffectiveExpectedProfile.model_validate(report['validation']['profile'])
    return result

def values(profile):
    scalar={'OACS':7,'SQES':102,'CQES':68,'NPSS':4,'AWUN':2,'AWUPF':1,'HMPRE':4,'HMMIN':2,
        'RPMBS':1,'FUSES':0,'ACWU':0,'DSTO':0,'NSZE':100,'NCAP':100,'NUSE':50,'NSFEAT':3,
        'NLBAF':63,'NAWUN':9,'NAWUPF':3,'NABSN':16,'NABSPF':16,'NABO':2}
    result={}
    for f in profile.fields:
        identity=f.schema_definition.field_id
        for index in range(f.array_count or 1):
            key=(identity,index if f.array_count else None)
            result[key]=9 if identity.endswith('.LBADS') else 0 if identity.endswith('.MS') else scalar[identity.split('.')[-1]]
    return result

def set_ref(data,ref,value):
    key=(ref.field_id,ref.index)
    data[key]=value if ref.bit is None else (data.get(key,0)&~(1<<ref.bit))|(value<<ref.bit)

def witness(node,data,ctx,wanted=True):
    if node is None:return
    if node.op=='AND':
        for i,child in enumerate(node.children):witness(child,data,ctx,wanted if wanted or i==0 else True)
    elif node.op=='OR':
        for i,child in enumerate(node.children):witness(child,data,ctx,wanted if i==0 else False)
    elif node.op=='NOT':witness(node.children[0],data,ctx,not wanted)
    else:
        ref=node.ref
        if node.op=='EQ':value=node.value if wanted else (not node.value if type(node.value) is bool else node.value+1 if type(node.value) is int else 'TEST_OTHER')
        elif node.op=='GE':value=node.value if wanted else node.value-1
        else:
            key=(ref.field.field_id,ref.field.index)
            current=data.get(key,0) if ref.source=='actual' else ctx.get(ref.path,0)
            want_set=wanted==(node.op=='BIT_SET');value=current|(1<<node.bit) if want_set else current&~(1<<node.bit)
        if ref.source=='actual':set_ref(data,ref.field,value)
        else:ctx[ref.path]=value

def facts(data):
    return tuple(ActualFact(field={'field_id':key[0],'index':key[1]},value=value,
        source={'path':'FIXTURE.synthetic','sha256':sha256(b'TEST').hexdigest()},capture_id='FIXTURE') for key,value in data.items())

CASES=[(b['bundle_id'],r['rule']['rule_id']) for b in PACK['bundles'] for r in b['rules']]
CASES += [(b['bundle_id'],r['replacement']['rule_id']) for b in PACK['bundles'] for r in b['replacements']]

@pytest.mark.parametrize('bundle,identity',CASES)
def test_every_registered_candidate_normal_violation_boundary_false_missing(profiles,bundle,identity):
    full=profiles[bundle];entry=next(e for e in full.entries if e.rule.rule_id==identity)
    rule=entry.rule;data=values(full);ctx=dict(full.context.facts);witness(rule.condition,data,ctx)
    check=rule.check
    if check.type=='FIELD_COMPARE':
        set_ref(data,check.other,10)
        good={'<=':9,'>=':11,'=':10}[check.operator];boundary=10;bad={'<=':11,'>=':9,'=':11}[check.operator]
    elif check.type=='MIN':good=check.value+1;boundary=check.value;bad=check.value-1
    elif check.type=='MAX':good=check.value-1;boundary=check.value;bad=check.value+1
    elif check.type=='EXACT':good=boundary=check.value;bad=check.value+1
    elif check.type=='BIT_SET':good=boundary=1<<check.bit;bad=0
    elif check.type=='BIT_CLEAR':good=boundary=0;bad=1<<check.bit
    else:raise AssertionError(check.type)
    profile=full.model_copy(update={'entries':(entry,), 'context':full.context.model_copy(update={'facts':ctx})})
    target=(rule.target.field_id,rule.target.index)
    for value,status in [(good,'PASS'),(boundary,'PASS'),(bad,'FAIL')]:
        sample=dict(data);set_ref(sample,rule.target,value)
        report=evaluate(profile,facts(sample))
        assert report.results[0].status==status,(identity,value,report.results[0])
        assert not report.authoritative and report.results[0].rule.provenance.status=='candidate'
        assert report.results[0].observations and report.profile.input_source.sha256
    missing=dict(data);missing.pop(target)
    assert evaluate(profile,facts(missing)).results[0].status=='UNKNOWN'
    if check.type=='FIELD_COMPARE':
        missing=dict(data);missing.pop((check.other.field_id,check.other.index))
        assert evaluate(profile,facts(missing)).results[0].status=='UNKNOWN'
    if rule.condition:
        ctx_false=dict(ctx);sample=dict(data);witness(rule.condition,sample,ctx_false,False)
        p=profile.model_copy(update={'context':profile.context.model_copy(update={'facts':ctx_false})})
        assert evaluate(p,facts(sample)).results[0].status=='N/A'
        # Missing one required condition is never replaced by zero/false.
        def first_leaf(node):return node if node.ref is not None else first_leaf(node.children[0])
        leaf=first_leaf(rule.condition);sample=dict(data);ctx_missing=dict(ctx)
        if leaf.ref.source=='context':ctx_missing.pop(leaf.ref.path,None)
        else:sample.pop((leaf.ref.field.field_id,leaf.ref.field.index),None)
        p=profile.model_copy(update={'context':profile.context.model_copy(update={'facts':ctx_missing})})
        assert evaluate(p,facts(sample)).results[0].status=='UNKNOWN'

def test_ge_condition_types_missing_and_no_coercion(profiles):
    full=next(iter(profiles.values()));entry=next(e for e in full.entries if '.LBADS.0.' in e.rule.rule_id)
    data=values(full)
    for value,state in [(0,'TRUE'),(1,'TRUE'),(-1,'ERROR'),(False,'ERROR'),('0','ERROR')]:
        data[(NS+'NLBAF',None)]=value
        p=full.model_copy(update={'entries':(entry,)})
        report=evaluate(p,facts(data))
        assert report.results[0].condition_state==state
    with pytest.raises(ValueError):Condition(op='GE',ref={'source':'context','path':'n'},value=False)

def test_sentinels_reserved_may_and_version_separation(profiles):
    old=profiles['nvme-2.0e-nvm-1.0e'];new=profiles['nvme-2.1-nvm-1.1']
    for full in (old,new):
        data=values(full);data[(NS+'NAWUN',None)]=0;data[(NS+'NAWUPF',None)]=0
        report=evaluate(full,facts(data))
        assert not any(r.status=='FAIL' for r in report.results)
        data[(NS+'NSFEAT',None)]=0;data[(NS+'NUSE',None)]=50
        report=evaluate(full,facts(data))
        assert not any(r.status=='FAIL' for r in report.results) # NUSE<NCAP is legal when THINP=0.
        assert all(r.status=='N/A' for r in report.results if r.rule.rule_id.startswith('NVME.STAGE5.ATOMIC.'))
        data=values(full);data[(NS+'LBAF.LBADS',0)]=0
        report=evaluate(full,facts(data))
        assert next(r for r in report.results if '.LBADS.0.' in r.rule.rule_id).status=='N/A'
    assert not any('HIR_REQUIRES' in e.rule.rule_id for e in old.entries)
    assert any('HIR_REQUIRES' in e.rule.rule_id for e in new.entries)
    for full,expected in [(old,'PASS'),(new,'N/A')]:
        data=values(full);data[(NS+'NSFEAT',None)]=67
        report=evaluate(full,facts(data))
        assert next(r for r in report.results if r.rule.rule_id=='NVME.STAGE5.ATOMIC.NAWUN_BASELINE').status==expected

def captured(ns=True,nsid=1):
    ctrl=b'NVME Identify Controller:\nsqes:0x66\ncqes:0x44\nnpss:4\nawun:2\nawupf:1\noacs:7\nhmpre:4\nhmmin:2\nrpmbs:1\nfuses:0\nacwu:0\ndsto:0\n'
    caps=[{'capture_id':'FIXTURE_CTRL','filename':'FIXTURE_CTRL.txt','command':'id-ctrl','dut_id':'TEST_DUT','session_id':'TEST',
        'content_base64':base64.b64encode(ctrl).decode()}]
    if ns:
        text=b'NVME Identify Namespace:\nnsze:100\nncap:100\nnuse:50\nnsfeat:3\nnlbaf:1\nnawun:9\nnawupf:3\nnabsn:16\nnabspf:16\nnabo:2\nlbaf 0 : ms:0 lbads:9 rp:0\nlbaf 1 : ms:0 lbads:12 rp:1\n'
        caps.append({'capture_id':'FIXTURE_NS','filename':'FIXTURE_NS.txt','command':'id-ns','dut_id':'TEST_DUT','session_id':'TEST',
            'nsid':nsid,'content_base64':base64.b64encode(text).decode()})
    return {'captures':caps}

def test_existing_normalizer_resolver_and_pipeline_unknown_scope(prepared):
    ctx={'host.lbaf_extension_enabled':False,'namespace.lbaf.0.metadata_supported':False,'namespace.lbaf.1.metadata_supported':False}
    for bundle in profiles_from_pack():
        report=prepared.analyze_captures(captured(),bundle,context_facts=ctx)
        assert report['validation']['status']=='PASS'
        assert report['scopes'][0]['input_context']['facts']['namespace.query_is_specific'] is True
        assert any(f['field']['field_id']==NS+'LBAF.LBADS' and f['field']['index']==1 for f in report['scopes'][0]['actual_facts'])
        missing=prepared.analyze_captures(captured(nsid=None),bundle,context_facts=ctx)
        assert missing['validation']['status']=='UNKNOWN'
        ctrl=prepared.analyze_captures(captured(ns=False),bundle)
        assert ctrl['validation']['status']=='PASS'
        assert all(r['status']=='N/A' for r in ctrl['validation']['results'] if r['rule']['target']['field_id'].startswith(NS))
        assert prepared.replay(report['run_id'])['scopes']==report['scopes']

def profiles_from_pack():return [b['bundle_id'] for b in PACK['bundles']]

def test_source_conflicts_hashes_and_candidate_only(prepared):
    sources=prepared.repository.sources();catalog=json.loads(sources['candidates/nvme/catalog.json'])
    bad=copy.deepcopy(PACK);bad['document_hashes']['NVM_1_1']='0'*64
    with pytest.raises(ValueError,match='hash'):validate_recipe(bad,catalog)
    bad=copy.deepcopy(PACK);bad['bundles'][0]['rules'][0]['rule']['provenance']['status']='confirmed'
    with pytest.raises(ValueError,match='candidate'):validate_recipe(bad,catalog)
    changed=dict(sources);path='knowledge/experimental/id_ctrl/nvme-2.0e-nvm-1.0e.json';config=json.loads(changed[path]);next(r for r in config['rules'] if r['rule_id']=='NVME.STAGE5.QUEUE.SQES_MAX_REQUIRED')['check']['value']=97;changed[path]=json.dumps(config)
    with pytest.raises(ValueError,match='RULE_EDIT_CONFLICT'):prepare_sources(changed,PACK)
    assert all(r['registration_state']=='matches_candidate' for b in prepared.nvme_coverage()['bundles'] for r in b['rules'])
    assert prepared.database_status()['schema_version']=='3'


def test_queue_maximum_recommendations_are_not_equalities(profiles):
    for full in profiles.values():
        data=values(full)
        for sq,cq,state in [(0x76,0x54,'PASS'),(0x66,0x44,'PASS'),(0x56,0x34,'FAIL')]:
            data[(CTRL+'SQES',None)]=sq;data[(CTRL+'CQES',None)]=cq
            report=evaluate(full,facts(data))
            selected=[r for r in report.results if r.rule.rule_id.startswith('NVME.STAGE5.QUEUE.')]
            assert {r.status for r in selected}=={state}

def test_scope_facts_cannot_be_forged(prepared):
    with pytest.raises(ValueError,match='not user-overridable'):
        prepared.analyze(b'NVME Identify Controller:\nsqes:0x66\n','TEST.txt',profiles_from_pack()[0],experimental=True,
            context_facts={'input.has_namespace':True})

def test_explicit_registration_backup_replay_cas_and_idempotence(tmp_path):
    pdf_directory=ROOT.parent
    if not all((pdf_directory/d['filename']).is_file() for d in json.loads((ROOT/'candidates/nvme/catalog.json').read_text())['documents']):
        pytest.skip('Optional original PDFs are not available on this host')
    w=DatabaseWorkflow(ROOT,tmp_path/'TEST.sqlite3')
    old=w.analyze(b'NVME Identify Controller:\nsqes:0x66\ncqes:0x44\nnpss:0\nawun:0\nawupf:0\noacs:6\n','TEST.txt',profiles_from_pack()[1],experimental=True)
    assert w.repository.head()==1
    result=register(w,ROOT/PACK_PATH,pdf_directory,expected_revision=1,reason='TEST candidate registration')
    assert result['revision']==2 and result['status']=='candidate'
    backup=DatabaseWorkflow(ROOT,Path(result['pre_change_backup']))
    assert backup.repository.head()==1 and backup.load_run(old['run_id'])==old
    assert w.load_run(old['run_id'])==old
    replay=w.replay(old['run_id']);replay.pop('run_id');original=dict(old);original.pop('run_id')
    assert replay==original
    assert register(w,ROOT/PACK_PATH,pdf_directory,expected_revision=2,reason='TEST repeat')['changed'] is False
    with pytest.raises(ValueError,match='REVISION_CONFLICT'):
        register(w,ROOT/PACK_PATH,pdf_directory,expected_revision=1,reason='TEST stale')
    assert w.repository.head()==2
