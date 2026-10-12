"""Explicit candidate recipe registration into SQLite; no bootstrap auto-upgrade or LWW."""
import json
from hashlib import sha256
from pathlib import Path
from uuid import uuid4
from pydantic import Field, StrictInt
from ssd_validator.models.common import DomainModel, Text
from ssd_validator.models.runtime import RuntimeRule, Condition
from ssd_validator.models.schema import FieldSchema
from ssd_validator.models.candidates import DocumentAnchor
from ssd_validator.application.knowledge_management import Binding, METADATA, dump, yaml_read, yaml_write, base_path,bundle_path,metadata
from ssd_validator.application.rule_pilot import _unique_object

PACK_PATH='candidates/nvme/executable_requirements.json'

class Review(DomainModel):
    statement: Text
    modality: Text
    evidence: tuple[DocumentAnchor,...] = Field(min_length=1)
    conditions: Condition | None = None
    exceptions: tuple[Text,...] = ()
    dependencies: tuple[Text,...] = ()
    unresolved: tuple[Text,...] = ()
    review_status: Text

def validate_recipe(value,catalog):
    if not isinstance(value,dict) or set(value)!={'kind','format_version','document_hashes','bundles'} or value['kind']!='nvme_requirement_expansion' or type(value['format_version']) is not int or value['format_version']!=1:
        raise ValueError('Unsupported NVMe requirement recipe')
    docs={d['document_id']:d for d in catalog['documents']}
    if value['document_hashes']!={k:d['sha256'] for k,d in docs.items()}:
        raise ValueError('Recipe PDF hashes do not match the pinned catalog')
    selected={b['bundle_id']:b for b in catalog['bundles']}
    seen=set()
    for item in value['bundles']:
        if set(item)!={'bundle_id','fields','rules','replacements','coverage'} or item['bundle_id'] not in selected or item['bundle_id'] in seen:
            raise ValueError('Unknown or duplicate recipe Bundle')
        seen.add(item['bundle_id']);bundle=selected[item['bundle_id']]
        documents={bundle['base_document'],bundle['nvm_document']}
        fields=set();rules=set()
        for f in item['fields']:
            schema=FieldSchema.model_validate(f['schema']);binding=Binding.model_validate(f['binding'])
            if schema.field_id in fields or f'NVME.CNS{binding.cns:02X}' not in bundle['structure_ids']:
                raise ValueError('Duplicate or unregistered recipe field query')
            fields.add(schema.field_id)
            for a in f['evidence']['evidence']:
                anchor=DocumentAnchor.model_validate(a)
                if anchor.document_id not in documents or anchor.pdf_page>docs[anchor.document_id]['pages']:
                    raise ValueError('Field anchor outside selected Bundle/document')
        for record in [*item['rules'],*({'rule':r['replacement'],'review':r['review']} for r in item['replacements'])]:
            rule=RuntimeRule.model_validate(record['rule']);review=Review.model_validate(record['review'])
            if rule.rule_id in rules or rule.provenance.status!='candidate' or review.review_status!='candidate' or rule.modality!=review.modality:
                raise ValueError('Recipe must preserve distinct candidate rules and modality')
            if rule.provenance.source_document not in documents or rule.provenance.source_version!=docs[rule.provenance.source_document]['revision']:
                raise ValueError('Rule document/version outside selected Bundle')
            if review.conditions!=rule.condition:
                raise ValueError('Review conditions and executable rule must match')
            for a in review.evidence:
                if a.document_id not in documents or a.pdf_page>docs[a.document_id]['pages']:
                    raise ValueError('Rule anchor outside selected Bundle/document')
            rules.add(rule.rule_id)
    return value

def prepare_sources(sources,recipe):
    catalog=json.loads(sources['candidates/nvme/catalog.json']);validate_recipe(recipe,catalog)
    changed=dict(sources);meta=metadata(changed)
    for item in recipe['bundles']:
        bundle=item['bundle_id'];base=yaml_read(changed[base_path(bundle)]);cfg=json.loads(changed[bundle_path(bundle)])
        existing={f['field_id']:f for f in base['fields']}
        for entry in item['fields']:
            field=entry['schema'];identity=field['field_id']
            if identity in existing:
                if any(existing[identity].get(k)!=field.get(k) for k in ('offset','length','endian','value_type','state','command')):
                    raise ValueError('FIELD_EDIT_CONFLICT: '+identity)
                if identity in meta['bindings'].get(bundle,{}) and Binding.model_validate(meta['bindings'][bundle][identity])!=Binding.model_validate(entry['binding']):
                    raise ValueError('BINDING_EDIT_CONFLICT: '+identity)
                old_bits={b['bit']:b for b in existing[identity].get('bits',[])}
                if any(b['bit'] in old_bits and old_bits[b['bit']]['state']!=b['state'] for b in field.get('bits',[])):
                    raise ValueError('FIELD_BIT_CONFLICT: '+identity)
                continue # Existing labels/bits/evidence are not silently overwritten.
            base['fields'].append(field)
            meta['bindings'].setdefault(bundle,{})[identity]=entry['binding']
            cfg['field_evidence'][identity]={**entry['evidence'],'field_id':identity,'name':field['name'],
                'byte_offset':field['offset'],'byte_length':field['length'],'review_status':'candidate'}
        for record in item['rules']:
            rule=record['rule'];old=next((r for r in cfg['rules'] if r['rule_id']==rule['rule_id']),None)
            if old:
                if RuntimeRule.model_validate(old)!=RuntimeRule.model_validate(rule):
                    raise ValueError('RULE_EDIT_CONFLICT: '+rule['rule_id'])
            else:cfg['rules'].append(rule)
        for record in item['replacements']:
            old=next((r for r in cfg['rules'] if r['rule_id']==record['replacement']['rule_id']),None)
            if old is None or RuntimeRule.model_validate(old) not in (RuntimeRule.model_validate(record['expected']),RuntimeRule.model_validate(record['replacement'])):
                raise ValueError('RULE_EDIT_CONFLICT: explicit legacy replacement no longer matches')
            cfg['rules'][cfg['rules'].index(old)]=record['replacement']
        changed[base_path(bundle)]=yaml_write(base);changed[bundle_path(bundle)]=dump(cfg)
    changed[METADATA]=dump(meta);changed[PACK_PATH]=dump(recipe)
    return changed

def register(workflow,recipe_path,pdf_directory,*,expected_revision,reason):
    recipe=json.loads(Path(recipe_path).read_text(encoding='utf-8'),object_pairs_hook=_unique_object)
    with workflow.repository.lock:
        if workflow.repository.head()!=expected_revision:
            raise ValueError('REVISION_CONFLICT: reload before registering candidates')
        sources=workflow.repository.sources(expected_revision);catalog=json.loads(sources['candidates/nvme/catalog.json'])
        validate_recipe(recipe,catalog)
        for d in catalog['documents']:
            if sha256((Path(pdf_directory)/d['filename']).read_bytes()).hexdigest()!=d['sha256']:
                raise ValueError('Original PDF bytes differ: '+d['document_id'])
        changed=prepare_sources(sources,recipe)
        if changed==sources:return {'revision':expected_revision,'changed':False}
        from ssd_validator.application.database_workflow import validate_sources
        with workflow.repository.project(changed) as root:validate_sources(root)
        directory=workflow.repository.path.parent/'backups';directory.mkdir(exist_ok=True)
        backup=directory/f'pre-stage5-r{expected_revision}-{uuid4().hex}.sqlite3'
        with backup.open('xb') as stream:stream.write(workflow.repository.backup())
        revision=workflow.repository.commit(changed,expected_revision=expected_revision,reason=reason,validate=validate_sources)
        return {'revision':revision,'changed':True,'pre_change_backup':str(backup),'status':'candidate',
            'bundles':[{'bundle_id':b['bundle_id'],'new_rule_instances':len(b['rules']),'corrected_rule_instances':len(b['replacements']),
                'focused_fields':len(b['fields'])} for b in recipe['bundles']]}

def coverage(sources):
    if PACK_PATH not in sources:return []
    pack=json.loads(sources[PACK_PATH],object_pairs_hook=_unique_object)
    validate_recipe(pack,json.loads(sources['candidates/nvme/catalog.json']))
    for bundle in pack['bundles']:
        cfg=json.loads(sources[bundle_path(bundle['bundle_id'])]);current={r['rule_id']:r for r in cfg['rules']}
        for record in [*bundle['rules'],*bundle['replacements']]:
            proposed=record.get('rule',record.get('replacement'));identity=proposed['rule_id'];actual=current.get(identity)
            record['registration_state']='not_registered' if actual is None else 'matches_candidate' if RuntimeRule.model_validate(actual)==RuntimeRule.model_validate(proposed) else 'edited_review_needed'
            record['current_rule']=actual
    return pack['bundles']
