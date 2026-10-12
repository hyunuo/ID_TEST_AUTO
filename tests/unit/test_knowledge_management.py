"""Management uses temporary DBs; no real specification or policy value is added."""
import copy
import json
import sqlite3
from contextlib import closing
from pathlib import Path

import pytest

from ssd_validator.application.database_workflow import DatabaseWorkflow
from ssd_validator.storage.knowledge_db import KnowledgeDatabase

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = 'nvme-2.1-nvm-1.1'
LOG = b'NVME Identify Controller:\nsqes:0x66\ncqes:0x44\nnpss:4\nawun:0\nawupf:0\noacs:6\n'


@pytest.fixture
def workflow(tmp_path):
    return DatabaseWorkflow(ROOT,tmp_path/'source.sqlite3')


def item(workflow,kind,identity=None):
    items=workflow.entity_search(kind=kind,bundle_id='' if kind=='document' else BUNDLE)['items']
    return next(e for e in items if identity is None or e['entity_id']==identity)


def request(workflow,entity,payload=None,**kwargs):
    return {'kind':entity['kind'],'bundle_id':entity['bundle_id'],'original_id':entity['entity_id'],
            'expected_revision':workflow.repository.head(),'reason':'TEST management edit',
            'payload':payload if payload is not None else copy.deepcopy(entity['payload']),**kwargs}


def save(workflow,body):
    preview=workflow.preview_change(body)
    return workflow.save_change({**body,'preview_hash':preview['preview_hash']})


def test_search_preview_save_and_revert_preserve_old_run(workflow):
    old=workflow.analyze(LOG,'TEST.txt',BUNDLE,experimental=True)
    entity=item(workflow,'rule','EXPERIMENTAL.POWER_STATE_LIMIT')
    payload=copy.deepcopy(entity['payload']); payload['check']['value']=3
    body=request(workflow,entity,payload)
    preview=workflow.preview_change(body)
    assert workflow.repository.head()==1
    assert preview['changes'] and preview['preview_hash']
    with pytest.raises(ValueError,match='PREVIEW_CHANGED'):
        workflow.save_change({**body,'preview_hash':'bad'})
    save(workflow,body)
    assert workflow.analyze(LOG,'TEST.txt',BUNDLE,experimental=True)['validation']['status']=='FAIL'
    assert workflow.load_run(old['run_id'])==old
    assert workflow.replay(old['run_id'])['validation']==old['validation']
    with pytest.raises(ValueError,match='REVISION_CONFLICT'):
        workflow.preview_change(body)
    save(workflow,{'expected_revision':2,'target_revision':1,'reason':'TEST revert'})
    assert workflow.repository.head()==3
    assert workflow.analyze(LOG,'TEST.txt',BUNDLE,experimental=True)['validation']['status']=='PASS'
    assert workflow.entity_search(kind='field',bundle_id=BUNDLE,search='awupf')['items']
    assert not workflow.entity_search(search="' OR 1=1 --")['items']


def test_field_bit_array_forms_roundtrip_and_invalid_references(workflow):
    entity=item(workflow,'field','NVME.CNS01.OACS')
    payload=copy.deepcopy(entity['payload'])
    payload['schema']['bits']=[{'bit':0,'state':'reserved'}]
    body=request(workflow,entity,payload,review={'reviewer':'TEST_REVIEWER','reviewed_date':'2026-10-12','basis':'Synthetic regression review only'})
    save(workflow,body)
    current=item(workflow,'field',entity['entity_id'])
    assert current['payload']['schema']['bits'][0]['state']=='reserved'
    assert 'validation' not in current['payload']['schema']['bits'][0]
    assert current['reviews'][0]['reviewer']=='TEST_REVIEWER'
    renamed=copy.deepcopy(current['payload']); renamed['schema']['name']='TEST label change only'
    save(workflow,request(workflow,current,renamed))
    assert not item(workflow,'field',entity['entity_id'])['reviews']
    # Synthetic, unused array: no claim that a real NVMe scalar became an array.
    array=copy.deepcopy(current['payload'])
    array['schema'].update(field_id='TEST.ARRAY',name='TEST FIXTURE ONLY',offset=300)
    array['binding'].update(array_count=2,array_stride=2)
    array['evidence']['description']='Synthetic mapping regression fixture, not NVMe specification knowledge'
    body={'kind':'field','bundle_id':BUNDLE,'expected_revision':3,'reason':'TEST unused array','payload':array}
    save(workflow,body)
    assert item(workflow,'field','TEST.ARRAY')['payload']['binding']['array_count']==2
    bad=copy.deepcopy(array); bad['binding']['array_stride']=1
    with pytest.raises(ValueError,match='stride'):
        workflow.preview_change(request(workflow,item(workflow,'field','TEST.ARRAY'),bad))
    before=workflow.repository.head()
    with pytest.raises(ValueError):
        workflow.preview_change(request(workflow,item(workflow,'field',entity['entity_id']),delete=True))
    assert workflow.repository.head()==before


def test_capability_edit_affects_same_resolver_and_requires_review(workflow):
    entity=item(workflow,'capability')
    payload=copy.deepcopy(entity['payload'])
    payload['supported']=0; payload['unsupported']=1
    save(workflow,request(workflow,entity,payload))
    assert workflow.analyze(LOG,'TEST.txt',BUNDLE,experimental=True)['validation']['status']=='FAIL'
    entity=item(workflow,'capability',entity['entity_id'])
    payload=copy.deepcopy(entity['payload']); payload['provenance'].update(status='confirmed',verified_by='TEST_REVIEWER',verified_date='2026-10-12')
    with pytest.raises(ValueError,match='review'):
        workflow.preview_change(request(workflow,entity,payload))
    save(workflow,request(workflow,entity,payload,review={'reviewer':'TEST_REVIEWER','reviewed_date':'2026-10-12','basis':'Synthetic test approval only'}))
    assert item(workflow,'capability',entity['entity_id'])['reviews']


def test_documents_and_bundle_clone_are_data_driven(workflow):
    body={'kind':'document','bundle_id':'','expected_revision':1,'reason':'TEST source registration',
          'payload':{'source_type':'policy','source_document':'TEST_POLICY_DOC','source_version':'v1','title':'TEST ONLY'}}
    save(workflow,body)
    assert item(workflow,'document','TEST_POLICY_DOC')
    original=item(workflow,'bundle')
    invalid=copy.deepcopy(original['payload']); invalid['structure_ids'].remove('NVME.CNS01')
    with pytest.raises(ValueError,match='excludes|UNKNOWN_STRUCTURE'):
        workflow.preview_change(request(workflow,original,invalid))
    payload=copy.deepcopy(original['payload']); payload['bundle_id']='test-copy'; payload['template_bundle']=BUNDLE
    body={'kind':'bundle','expected_revision':2,'reason':'TEST clone','payload':payload}
    save(workflow,body)
    assert any(b['bundle_id']=='test-copy' for b in workflow.bundles()['bundles'])
    assert workflow.analyze(LOG,'TEST.txt','test-copy',experimental=True)['validation']['status']=='PASS'
    cloned=next(e for e in workflow.entity_search(kind='bundle')['items'] if e['entity_id']=='test-copy')
    save(workflow,request(workflow,cloned,delete=True))
    assert all(b['bundle_id']!='test-copy' for b in workflow.bundles()['bundles'])
    pinned=item(workflow,'document','BASE_2_1'); changed=copy.deepcopy(pinned['payload']); changed['sha256']='0'*64
    with pytest.raises(ValueError,match='pinned'):
        workflow.preview_change(request(workflow,pinned,changed))
    unused=item(workflow,'document','TEST_POLICY_DOC')
    save(workflow,request(workflow,unused,delete=True))
    assert not workflow.entity_search(kind='document',search='TEST_POLICY_DOC')['items']
    referenced=item(workflow,'document','LAB_ASSUMED_DEVELOPMENT_PROFILE')
    with pytest.raises(ValueError):
        workflow.preview_change(request(workflow,referenced,delete=True))


def test_v2_migration_builds_indexes_without_touching_sources_or_runs(workflow,tmp_path):
    old=workflow.analyze(LOG,'TEST.txt',BUNDLE,experimental=True)
    path=tmp_path/'v2.sqlite3'; path.write_bytes(workflow.repository.backup())
    with closing(sqlite3.connect(path)) as db,db:
        db.execute('DROP TABLE entity_index'); db.execute("UPDATE repository_meta SET value='2' WHERE key='schema_version'")
    migrated=DatabaseWorkflow(tmp_path,path)
    assert migrated.database_status()['schema_version']=='3'
    assert migrated.export_sources()==workflow.export_sources()
    assert migrated.load_run(old['run_id'])==old
    assert migrated.entity_search()['items']
    assert migrated.replay(old['run_id'])['validation']==old['validation']
