"""Pinned supplemental requirements linked to existing Profile policies and mappings."""
import json
from hashlib import sha256
from pathlib import Path
from uuid import uuid4
from typing import Literal
from pydantic import Field,StrictInt
from ssd_validator.models.common import DomainModel,Text,Identifier,require_unique
from ssd_validator.models.candidates import DocumentAnchor
from ssd_validator.models.runtime import Condition,CapabilityMapping
from ssd_validator.application.product_profiles import ProductPolicy,registry,PRODUCTS
from ssd_validator.application.knowledge_management import METADATA,metadata,bundle_path,dump,yaml_read,yaml_write
from ssd_validator.application.rule_pilot import _unique_object

CANDIDATE_PATH='candidates/ocp/requirements.json'
REGISTRY_PATH='knowledge/supplemental_requirements.json'

class Document(DomainModel):
    source_type: Literal['spec']
    source_document: Identifier
    source_version: Text
    title: Text
    filename: Text
    sha256: str=Field(pattern=r'^[a-f0-9]{64}$')
    pages: StrictInt=Field(gt=0)

class Requirement(DomainModel):
    requirement_id: Identifier
    rule_id: Identifier
    summary: Text
    modality: Literal['mandatory']
    review_status: Literal['candidate']
    evidence: DocumentAnchor
    capability_id: Identifier | None
    mapping_evidence: DocumentAnchor | None
    remaining: tuple[Text,...]
    condition: Condition
    product_scope: Text
    validation_scope: Text

class Bundle(DomainModel):
    bundle_id: Identifier
    policy: ProductPolicy
    mappings: tuple[CapabilityMapping,...]
    requirements: tuple[Requirement,...]

class Pending(DomainModel):
    item: Text
    status: Literal['excluded','awaiting_source','additional_information','behavior_required','unimplemented']
    required_inputs: tuple[Text,...]
    reason: Text

class Package(DomainModel):
    kind: Literal['supplemental_requirement_candidates']
    format_version: StrictInt=Field(ge=1,le=1)
    document: Document
    product_scope: Text
    bundles: tuple[Bundle,...]=Field(min_length=1)
    pending: tuple[Pending,...]

def parse(text):return Package.model_validate(json.loads(text,object_pairs_hook=_unique_object))

def validate_package(package,sources):
    catalog=json.loads(sources['candidates/nvme/catalog.json']);bundles={b['bundle_id']:b for b in catalog['bundles']};docs={d['document_id']:d for d in catalog['documents']}
    doc=package.document
    if Path(doc.filename).name!=doc.filename or any(c in doc.filename for c in ('/','\\',':')):raise ValueError('PDF filename must be a basename')
    require_unique([b.bundle_id for b in package.bundles],'supplemental Bundle')
    for b in package.bundles:
        if b.bundle_id not in bundles or b.policy.bundle_id!=b.bundle_id:raise ValueError('Supplemental Bundle/policy mismatch')
        require_unique([r.rule_id for r in b.requirements],'supplemental requirement-rule link')
        require_unique([c.capability_id+':'+c.target.key for c in b.mappings],'supplemental mapping')
        rules={r.rule_id:r for r in b.policy.rules}
        if set(rules)!={r.rule_id for r in b.requirements}:raise ValueError('Each policy rule needs a requirement link')
        for p in [b.policy.provenance,*[r.provenance for r in rules.values()]]:
            if p.status!='candidate' or p.source_document!=doc.source_document or p.source_version!=doc.source_version:raise ValueError('Extracted supplemental policy must remain candidate and version pinned')
        for r in b.requirements:
            rule=rules[r.rule_id]
            if r.evidence.document_id!=doc.source_document or r.evidence.pdf_page>doc.pages or r.condition!=rule.condition or rule.modality!=r.modality:raise ValueError('Requirement source/condition/modality mismatch')
            if r.product_scope!=package.product_scope:raise ValueError('Requirement product scope mismatch')
            if r.capability_id:
                maps=[c for c in b.mappings if c.capability_id==r.capability_id]
                if not maps or rule.check.type!='CAPABILITY' or rule.check.capability_id!=r.capability_id or rule.target.field_id not in {m.target.field_id for m in maps}:raise ValueError('Missing or mismatched Capability mapping')
                a=r.mapping_evidence;paired=bundles[b.bundle_id]
                if a is None or a.document_id not in (paired['base_document'],paired['nvm_document']) or a.pdf_page>docs[a.document_id]['pages']:raise ValueError('Mapping anchor outside selected NVMe Bundle')
                if any(c.provenance.status!='candidate' or c.provenance.source_document!=a.document_id or c.provenance.source_version!=docs[a.document_id]['revision'] for c in maps):raise ValueError('Mapping provenance/version mismatch')
            elif rule.check.type=='CAPABILITY':raise ValueError('Capability requirement needs a mapping link')
    return package

def prepare_sources(sources,package):
    validate_package(package,sources);changed=dict(sources);meta=metadata(changed);products=registry(changed).model_dump(mode='json');doc=package.document.model_dump(mode='json')
    old=next((d for d in meta['documents'] if d['source_document']==doc['source_document']),None)
    if old and old!=doc:raise ValueError('DOCUMENT_EDIT_CONFLICT: pinned source already differs')
    if not old:meta['documents'].append(doc)
    for b in package.bundles:
        cfg=json.loads(changed[bundle_path(b.bundle_id)])
        for mapping in b.mappings:
            old=next((m for m in cfg['capabilities'] if m['capability_id']==mapping.capability_id and m['target']==mapping.model_dump(mode='json')['target']),None)
            if old and CapabilityMapping.model_validate(old)!=mapping:raise ValueError('MAPPING_EDIT_CONFLICT')
            # A new target for an existing capability is an explicit conflict, never a silent append.
            if not old and any(m['capability_id']==mapping.capability_id for m in cfg['capabilities']):raise ValueError('MAPPING_TARGET_CONFLICT')
            if not old:cfg['capabilities'].append(mapping.model_dump(mode='json'))
        old=next((p for p in products['policies'] if p['policy_id']==b.policy.policy_id),None)
        if old and ProductPolicy.model_validate(old)!=b.policy:raise ValueError('POLICY_EDIT_CONFLICT')
        if not old:products['policies'].append(b.policy.model_dump(mode='json'))
        path=f'knowledge/experimental/id_ctrl/{b.bundle_id}/catalog.yaml';catalog=yaml_read(changed[path])
        source={k:doc[k] for k in ('source_type','source_document','source_version')}
        if not any(d==source for d in catalog['sources']):catalog['sources'].append(source)
        changed[path]=yaml_write(catalog);changed[bundle_path(b.bundle_id)]=dump(cfg)
    changed[PRODUCTS]=dump(products);changed[METADATA]=dump(meta);changed[REGISTRY_PATH]=package.model_dump_json()
    changed[CANDIDATE_PATH]=package.model_dump_json()
    return changed

def validate_registry(sources):
    if REGISTRY_PATH not in sources:return None
    package=validate_package(parse(sources[REGISTRY_PATH]),sources)
    doc=next((d for d in metadata(sources)['documents'] if d['source_document']==package.document.source_document),None)
    if doc!=package.document.model_dump(mode='json'):raise ValueError('Registered supplemental document no longer matches pinned evidence')
    products=registry(sources)
    for b in package.bundles:
        policy=next((p for p in products.policies if p.policy_id==b.policy.policy_id and p.bundle_id==b.bundle_id),None)
        if policy is None or not {r.rule_id for r in b.requirements}<={r.rule_id for r in policy.rules}:raise ValueError('Dangling supplemental policy/rule reference')
        caps=[CapabilityMapping.model_validate(c) for c in json.loads(sources[bundle_path(b.bundle_id)])['capabilities']]
        if any(not any(m.capability_id==c.capability_id and m.target==c.target for m in caps) for c in b.mappings):raise ValueError('Dangling supplemental mapping reference')
    return package

def register(workflow,recipe_path,pdf_directory,*,expected_revision,reason):
    package=parse(Path(recipe_path).read_text(encoding='utf-8'))
    with workflow.repository.lock:
        if workflow.repository.head()!=expected_revision:raise ValueError('REVISION_CONFLICT: reload before registration')
        sources=workflow.repository.sources(expected_revision);validate_package(package,sources)
        pdf=Path(pdf_directory)/package.document.filename
        if sha256(pdf.read_bytes()).hexdigest()!=package.document.sha256:raise ValueError('Original supplemental PDF hash differs')
        changed=prepare_sources(sources,package)
        if changed==sources:return {'revision':expected_revision,'changed':False}
        from ssd_validator.application.database_workflow import validate_sources
        with workflow.repository.project(changed) as root:validate_sources(root)
        directory=workflow.repository.path.parent/'backups';directory.mkdir(exist_ok=True)
        backup=directory/f'pre-stage6-r{expected_revision}-{uuid4().hex}.sqlite3'
        with backup.open('xb') as stream:stream.write(workflow.repository.backup())
        revision=workflow.repository.commit(changed,expected_revision=expected_revision,reason=reason,validate=validate_sources)
        return {'revision':revision,'changed':True,'status':'candidate','pre_change_backup':str(backup),'product_profiles_created':0}

def trace(root,validation,bundle_id,selection=None):
    path=Path(root)/REGISTRY_PATH
    if not path.exists():return None
    text=path.read_text(encoding='utf-8');package=parse(text);b=next((b for b in package.bundles if b.bundle_id==bundle_id),None)
    reviews=metadata({METADATA:(Path(root)/METADATA).read_text(encoding='utf-8')})['reviews']
    results=validation['results'];rows=[]
    cfg=json.loads((Path(root)/bundle_path(bundle_id)).read_text(encoding='utf-8'))
    if b:
        for link in b.requirements:
            matches=[r for r in results if r['rule']['rule_id']==link.rule_id or r['rule'].get('origin_rule_id')==link.rule_id]
            rows.append({'requirement':link.model_dump(mode='json'),'policy_id':b.policy.policy_id,'candidate_rule':next(r.model_dump(mode='json') for r in b.policy.rules if r.rule_id==link.rule_id),'effective_mappings':[m for m in cfg['capabilities'] if m['capability_id']==link.capability_id],'outcomes':matches,'execution':'evaluated' if matches else 'review_only' if selection and any(p['policy_id']==b.policy.policy_id for p in selection.get('policies',[])) else 'not_selected'})
    conflicts=[];overrides=[];by_id={r['rule']['rule_id']:r for r in results}
    seen=set()
    for r in results:
        if r['status']=='CONFLICT':
            ids=tuple(sorted(r['related_rules']))
            if ids not in seen:
                seen.add(ids);conflicts.append({'rule_ids':ids,'rules':[by_id[i]['rule'] for i in ids if i in by_id],'analysis':'active_literal_constraints_only'})
        ov=r['rule'].get('override')
        if ov and ov['enabled']:
            originals=[by_id[i] for i in ov['overrides'] if i in by_id]
            overrides.append({'replacement':r,'originals':originals,'reason':ov['reason'],'review_evidence':ov['provenance'],
                'review_records':[v for v in reviews if (v['kind']=='rule' and v['entity_id']==r['rule']['rule_id'] and any(q['rule_id']==v['entity_id'] and v['target_hash']==sha256(dump(q).encode()).hexdigest() for q in cfg['rules'])) or (v['kind']=='product_policy' and any(p['policy_id']==v['entity_id'] and any(q['rule_id']==r['rule']['rule_id'] for q in p['rules']) and v['target_hash']==sha256(dump(p).encode()).hexdigest() for p in (selection or {}).get('policies',[])))],'applied':any(o['status']=='N/A' and r['rule']['rule_id'] in o['related_rules'] for o in originals)})
    return {'registry_source':{'path':path.as_posix(),'sha256':sha256(text.encode()).hexdigest()},
        'document':package.document.model_dump(mode='json'),'requirements':rows,'conflicts':conflicts,'overrides':overrides,
        'pending':[p.model_dump(mode='json') for p in package.pending],
        'scope':'Only selected Profile policies execute; no product or OCP applicability inferred'}

def overview(sources):
    package=validate_registry(sources)
    if package is None:return {'registered':False,'bundles':[],'pending':[{'item':'MFND','status':'excluded'},{'item':'OCP/product requirements','status':'awaiting_source_registration'}]}
    products=registry(sources);bundles=[]
    for b in package.bundles:
        policy=next(p for p in products.policies if p.policy_id==b.policy.policy_id)
        caps=[CapabilityMapping.model_validate(c) for c in json.loads(sources[bundle_path(b.bundle_id)])['capabilities']]
        bundles.append({**b.model_dump(mode='json'),'registration_state':'matches_candidate' if policy==b.policy and all(c in caps for c in b.mappings) else 'edited_review_needed',
            'bound_profiles':[p.profile_id for p in products.profiles if b.policy.policy_id in p.policy_ids], 'current_policy':policy.model_dump(mode='json')})
    return {'registered':True,'document':package.document.model_dump(mode='json'),'bundles':bundles,'pending':[p.model_dump(mode='json') for p in package.pending]}
