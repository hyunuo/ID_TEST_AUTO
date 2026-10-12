"""Typed, revisioned management over the same source documents consumed by the core."""
import copy
import json
import re
from datetime import date
from hashlib import sha256
from io import StringIO

from pydantic import Field, StrictInt, model_validator
from ruamel.yaml import YAML

from ssd_validator.models.common import DomainModel, Text, VersionLabel
from ssd_validator.models.candidates import CandidateCatalog, SpecBundle
from ssd_validator.models.provenance import SourceDocument
from ssd_validator.models.runtime import CapabilityMapping
from ssd_validator.models.schema import FieldSchema

METADATA = 'knowledge/management.json'


def dump(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)


def yaml_read(content):
    yaml = YAML(typ='safe', pure=True)
    yaml.allow_duplicate_keys = False
    return yaml.load(content)


def yaml_write(value):
    stream = StringIO()
    yaml = YAML()
    yaml.dump(value, stream)
    return stream.getvalue()


def bundle_path(bundle):
    # Portable identifiers only; validity/registration is checked against the DB catalog.
    from pydantic import TypeAdapter
    label = TypeAdapter(VersionLabel).validate_python(bundle)
    return f'knowledge/experimental/id_ctrl/{label}.json'


def bundle_ids(sources):
    return [b['bundle_id'] for b in json.loads(sources['candidates/nvme/catalog.json'])['bundles']]


def config(sources, bundle):
    if bundle not in bundle_ids(sources):
        raise ValueError('Unknown Bundle')
    return json.loads(sources[bundle_path(bundle)])


class Binding(DomainModel):
    cns: StrictInt = Field(default=1, ge=0, le=255)
    csi: StrictInt = Field(default=0, ge=0, le=255)
    array_count: StrictInt | None = Field(default=None, gt=0, le=4096)
    array_stride: StrictInt | None = Field(default=None, gt=0)
    response_size: StrictInt = Field(default=4096, gt=0)

    @model_validator(mode='after')
    def array(self):
        if (self.array_count is None) != (self.array_stride is None):
            raise ValueError('Array needs both count and stride')
        return self


def metadata(sources):
    return json.loads(sources.get(METADATA, '{"format_version":1,"bindings":{},"documents":[],"reviews":[]}'))


def base_path(bundle):
    bundle_path(bundle)
    return f'knowledge/experimental/id_ctrl/{bundle}/base.yaml'


def entities(sources):
    """Pure source projection used to rebuild DB indexes, including older revisions."""
    result = []
    catalog = json.loads(sources['candidates/nvme/catalog.json'])
    meta = metadata(sources)
    def add(kind, bundle, identity, payload):
        digest = sha256(dump(payload).encode()).hexdigest()
        reviews = [r for r in meta['reviews'] if (r['kind'], r['bundle_id'], r['entity_id'], r['target_hash']) ==
                   (kind, bundle, identity, digest)]
        result.append({'kind': kind, 'bundle_id': bundle, 'entity_id': identity,
                       'payload': payload, 'hash': digest, 'reviews': reviews})
    for doc in catalog['documents']:
        add('document', '', doc['document_id'], {**doc, 'source_type': 'spec', 'source_version': doc['revision'], 'catalog_document': True})
    docs = {d['document_id']: d for d in catalog['documents']}
    for doc in meta['documents']:
        add('document', '', doc['source_document'], {**doc, 'catalog_document': False})
    seen_docs = {d['document_id'] for d in catalog['documents']} | {d['source_document'] for d in meta['documents']}
    for bundle in catalog['bundles']:
        path = f'knowledge/experimental/id_ctrl/{bundle["bundle_id"]}/catalog.yaml'
        for doc in yaml_read(sources[path])['sources']:
            if doc['source_document'] not in seen_docs:
                add('document','',doc['source_document'],{**doc,'catalog_document':False,'from_builder_catalog':True})
                seen_docs.add(doc['source_document'])
    for item in catalog['bundles']:
        bundle = item['bundle_id']
        cfg = config(sources, bundle)
        add('bundle', bundle, bundle, {**item, 'base_revision': docs[item['base_document']]['revision'],
                                     'nvm_revision': docs[item['nvm_document']]['revision']})
        base = yaml_read(sources[base_path(bundle)])
        for field in base['fields']:
            binding = Binding.model_validate(meta['bindings'].get(bundle, {}).get(field['field_id'], {})).model_dump(mode='json')
            evidence = cfg['field_evidence'].get(field['field_id'], {})
            add('field', bundle, field['field_id'], {'schema': field, 'binding': binding, 'evidence': evidence})
        for rule in cfg['rules']:
            add('rule', bundle, rule['rule_id'], rule)
        for cap in cfg.get('capabilities', []):
            from ssd_validator.models.runtime import FieldRef
            add('capability', bundle, cap['capability_id'] + ':' + FieldRef.model_validate(cap['target']).key, cap)
    from ssd_validator.application.product_profiles import product_entities
    for kind,bundle,identity,payload in product_entities(sources):
        add(kind,bundle,identity,payload)
    return result


def validate_metadata(sources):
    meta = metadata(sources)
    if (not isinstance(meta,dict) or set(meta) != {'format_version', 'bindings', 'documents', 'reviews'}
            or type(meta['format_version']) is not int or meta['format_version'] != 1
            or not isinstance(meta['bindings'],dict) or not isinstance(meta['documents'],list) or not isinstance(meta['reviews'],list)):
        raise ValueError('Invalid management metadata format')
    ids = bundle_ids(sources)
    if any(b not in ids for b in meta['bindings']):
        raise ValueError('Binding references unknown Bundle')
    catalog = json.loads(sources['candidates/nvme/catalog.json'])
    for bundle in catalog['bundles']:
        for field in yaml_read(sources[base_path(bundle['bundle_id'])])['fields']:
            binding = Binding.model_validate(meta['bindings'].get(bundle['bundle_id'],{}).get(field['field_id'],{}))
            structure = f'NVME.CNS{binding.cns:02X}'
            if structure not in bundle['structure_ids']:
                raise ValueError('Bundle excludes a registered field query/structure')
            if field['field_id'].startswith('NVME.CNS') and not field['field_id'].startswith(structure+'.'):
                raise ValueError('Field ID CNS and explicit query binding disagree')
    for bundle, bindings in meta['bindings'].items():
        if not isinstance(bindings,dict):
            raise ValueError('Bindings must be field objects')
        base = yaml_read(sources[base_path(bundle)])
        fields = {f['field_id']: FieldSchema.model_validate(f) for f in base['fields']}
        if not set(bindings) <= set(fields):
            raise ValueError('Binding references unknown field')
        for identity, item in bindings.items():
            binding = Binding.model_validate(item)
            schema = fields[identity]
            if binding.array_stride is not None and binding.array_stride < schema.length:
                raise ValueError('Array stride is smaller than element size')
            end = schema.offset + ((binding.array_count or 1) - 1) * (binding.array_stride or 0) + schema.length
            if end > binding.response_size:
                raise ValueError('Field/array extends beyond response size')
    catalog_docs = {d['document_id'] for d in json.loads(sources['candidates/nvme/catalog.json'])['documents']}
    seen = set(catalog_docs)
    for document in meta['documents']:
        parsed = SourceDocument.model_validate({k: document[k] for k in ('source_type','source_document','source_version')})
        if parsed.source_document in seen:
            raise ValueError('Duplicate document ID')
        seen.add(parsed.source_document)
    for review in meta['reviews']:
        if not isinstance(review,dict) or set(review) != {'kind','bundle_id','entity_id','target_hash','reviewer','reviewed_date','basis'} or any(not isinstance(v,str) for v in review.values()):
            raise ValueError('Invalid review record')
        if not review['reviewer'].strip() or not review['basis'].strip():
            raise ValueError('Review requires reviewer and basis')
        date.fromisoformat(review['reviewed_date'])
        if not re.fullmatch('[a-f0-9]{64}', review['target_hash']):
            raise ValueError('Invalid reviewed content hash')


def change_entity(sources, *, kind, bundle_id='', original_id=None, payload=None, delete=False, review=None):
    if type(delete) is not bool:
        raise ValueError('delete must be Boolean')
    changed = copy.deepcopy(sources)
    meta = metadata(changed)
    before = next((e for e in entities(sources) if (e['kind'], e['bundle_id'], e['entity_id']) ==
                  (kind, bundle_id, original_id)), None) if original_id else None
    if original_id and before is None:
        raise ValueError('Unknown entity ID')
    if delete and before is None:
        raise ValueError('Select an entity to delete')
    if kind in {'profile','product_policy','context'}:
        from ssd_validator.application.product_profiles import registry, PRODUCTS, ProductProfile, ProductPolicy, ProductContext
        data=registry(changed).model_dump(mode='json')
        model,key,collection={'profile':(ProductProfile,'profile_id','profiles'),
            'product_policy':(ProductPolicy,'policy_id','policies'),'context':(ProductContext,'context_id','contexts')}[kind]
        value=None if delete else model.model_validate(payload).model_dump(mode='json')
        if value is not None and value['bundle_id']!=bundle_id:
            raise ValueError('Product entity Bundle must match the explicit edit scope')
        require_review(value,before,review)
        if kind=='product_policy' and value:
            old_rules={r['rule_id']:r for r in before['payload']['rules']} if before else {}
            for rule in value['rules']:
                prior={'payload':old_rules[rule['rule_id']]} if rule['rule_id'] in old_rules else None
                require_review(rule,prior,review)
                if rule.get('override'):
                    old_override=prior['payload'].get('override') if prior else None
                    require_review(rule['override'],{'payload':old_override} if old_override else None,review)
        replace(data[collection],key,original_id,value,delete)
        changed[PRODUCTS]=dump(data)
        identity=original_id if delete else value[key]
    elif kind == 'rule':
        from ssd_validator.models.runtime import RuntimeRule
        cfg = config(changed, bundle_id)
        value = None if delete else RuntimeRule.model_validate(payload).model_dump(mode='json', exclude_none=True)
        collection = cfg['rules']
        require_review(value, before, review)
        replace(collection, 'rule_id', original_id, value, delete)
        cfg['assumptions'] = [a for a in cfg['assumptions'] if not a['id'].startswith('LAB.')]
        for rule in cfg['rules']:
            if rule['provenance']['source_type'] == 'policy' and rule['check']['type'] == 'CAPABILITY':
                cfg['assumptions'].append({'id':rule['check']['capability_id'], 'value':rule['check']['support'],
                    'rule_id':rule['rule_id'], 'reason':'해당 정책 규칙의 조건에서 적용하는 Capability 요구; 실제 제품 정책으로 확인되지 않음.'})
        changed[bundle_path(bundle_id)] = dump(cfg)
        identity = original_id if delete else value['rule_id']
    elif kind == 'capability':
        cfg = config(changed, bundle_id)
        value = None if delete else CapabilityMapping.model_validate(payload).model_dump(mode='json', exclude_none=True)
        collection = cfg['capabilities']
        require_review(value, before, review)
        if before:
            collection.remove(before['payload'])
        if value is not None:
            collection.append(value)
        changed[bundle_path(bundle_id)] = dump(cfg)
        from ssd_validator.models.runtime import FieldRef
        identity = original_id if delete else value['capability_id'] + ':' + FieldRef.model_validate(value['target']).key
    elif kind == 'field':
        cfg = config(changed, bundle_id)
        base = yaml_read(changed[base_path(bundle_id)])
        value = None if delete else FieldSchema.model_validate(payload['schema']).model_dump(mode='json', exclude_none=True)
        identity = original_id if delete else value['field_id']
        replace(base['fields'], 'field_id', original_id, value, delete)
        bindings = meta['bindings'].setdefault(bundle_id, {})
        if original_id:
            bindings.pop(original_id, None)
            cfg['field_evidence'].pop(original_id, None)
        if value is not None:
            bindings[identity] = Binding.model_validate(payload['binding']).model_dump(mode='json')
            evidence = payload.get('evidence', {})
            if not evidence.get('evidence'):
                raise ValueError('Field mapping requires a document/section/page anchor')
            from ssd_validator.models.candidates import DocumentAnchor
            for anchor in evidence['evidence']:
                DocumentAnchor.model_validate(anchor)
            cfg['field_evidence'][identity] = {**evidence, 'field_id': identity, 'name': value['name'],
                'byte_offset': value['offset'], 'byte_length': value['length'], 'review_status': 'candidate'}
        changed[base_path(bundle_id)] = yaml_write(base)
        changed[bundle_path(bundle_id)] = dump(cfg)
    elif kind == 'document':
        if before and before['payload'].get('catalog_document'):
            catalog = json.loads(changed['candidates/nvme/catalog.json'])
            if not delete:
                from ssd_validator.models.candidates import SpecDocument
                value = SpecDocument.model_validate({k: v for k,v in payload.items() if k not in {'source_type','source_version','catalog_document'}}).model_dump(mode='json')
                # Replacing PDF identity would invalidate existing extracted anchors.
                if any(value[k] != before['payload'][k] for k in ('document_id','component','revision','sha256','pages','inherits')):
                    raise ValueError('PDF identity is pinned by extraction; import matching extraction before changing it')
            else:
                value = None
            replace(catalog['documents'], 'document_id', original_id, value, delete)
            changed['candidates/nvme/catalog.json'] = dump(catalog)
            identity = original_id if delete else value['document_id']
        else:
            value = None if delete else dict(payload)
            if value is not None:
                value.pop('catalog_document', None)
                value.pop('from_builder_catalog', None)
                SourceDocument.model_validate({k:value[k] for k in ('source_type','source_document','source_version')})
            if before and before['payload'].get('from_builder_catalog'):
                if not delete:
                    meta['documents'].append(value)
                old_source = {k:before['payload'][k] for k in ('source_type','source_document','source_version')}
                for b in bundle_ids(changed):
                    path = f'knowledge/experimental/id_ctrl/{b}/catalog.yaml'
                    catalog = yaml_read(changed[path])
                    catalog['sources'] = [s for s in catalog['sources'] if s != old_source]
                    changed[path] = yaml_write(catalog)
            else:
                replace(meta['documents'], 'source_document', original_id, value, delete)
            identity = original_id if delete else value['source_document']
        # Remove the old registration as well, so dependent references block deletion/version edits.
        if before and (delete or not before['payload'].get('catalog_document')):
            old = before['payload']
            old_source = {'source_type':old['source_type'],
                          'source_document':old.get('source_document',old.get('document_id')),
                          'source_version':old['source_version']}
            for b in bundle_ids(changed):
                path = f'knowledge/experimental/id_ctrl/{b}/catalog.yaml'
                catalog = yaml_read(changed[path])
                catalog['sources'] = [s for s in catalog['sources'] if s != old_source]
                changed[path] = yaml_write(catalog)
        # Register new identities; the core validates all remaining references.
        if not delete:
            source = {'source_type': payload.get('source_type','spec'),
                      'source_document': payload.get('source_document', payload.get('document_id')),
                      'source_version': payload.get('source_version', payload.get('revision'))}
            for b in bundle_ids(changed):
                path = f'knowledge/experimental/id_ctrl/{b}/catalog.yaml'
                catalog = yaml_read(changed[path])
                if source not in catalog['sources']:
                    catalog['sources'].append(source)
                changed[path] = yaml_write(catalog)
    elif kind == 'bundle':
        catalog = json.loads(changed['candidates/nvme/catalog.json'])
        value = None if delete else SpecBundle.model_validate({k:payload[k] for k in ('bundle_id','base_document','nvm_document','structure_ids')}).model_dump(mode='json')
        identity = original_id if delete else value['bundle_id']
        if before and not delete:
            if identity != original_id:
                raise ValueError('Bundle IDs are stable; clone then delete instead of renaming')
            if any(value[k] != before['payload'][k] for k in ('base_document','nvm_document')):
                raise ValueError('Changing the spec pair requires a separately reviewed Bundle; clone matching source data explicitly')
        if not before and not delete:
            template = payload.get('template_bundle')
            parent = next((b for b in catalog['bundles'] if b['bundle_id'] == template), None)
            if parent is None or any(value[k] != parent[k] for k in ('base_document','nvm_document','structure_ids')):
                raise ValueError('A new Bundle must explicitly clone matching document/structure bindings; no implicit latest definitions')
            oldcfg = config(changed, template)
            oldcfg['bundle']['bundle_id'] = identity
            oldcfg['context']['bundle_id'] = identity
            changed[bundle_path(identity)] = dump(oldcfg)
            prefix = f'knowledge/experimental/id_ctrl/{template}/'
            for path, content in sources.items():
                if path.startswith(prefix):
                    changed[path.replace(prefix, f'knowledge/experimental/id_ctrl/{identity}/',1)] = content
            meta['bindings'][identity] = copy.deepcopy(meta['bindings'].get(template, {}))
        if delete:
            if len(catalog['bundles']) == 1:
                raise ValueError('Keep at least one Bundle')
            changed.pop(bundle_path(original_id))
            for path in list(changed):
                if path.startswith(f'knowledge/experimental/id_ctrl/{original_id}/'):
                    changed.pop(path)
            meta['bindings'].pop(original_id, None)
        replace(catalog['bundles'], 'bundle_id', original_id, value, delete)
        changed['candidates/nvme/catalog.json'] = dump(catalog)
    else:
        raise ValueError('Unsupported entity kind')
    if review is not None:
        if delete:
            raise ValueError('Cannot review a deleted entity')
        changed[METADATA] = dump(meta)
        scope = identity if kind == 'bundle' else bundle_id
        item = next(e for e in entities(changed) if (e['kind'],e['bundle_id'],e['entity_id']) == (kind,scope,identity))
        record = {'kind':kind, 'bundle_id':scope, 'entity_id':identity, 'target_hash':item['hash'], **review}
        if set(record) != {'kind','bundle_id','entity_id','target_hash','reviewer','reviewed_date','basis'}:
            raise ValueError('Review accepts reviewer/date/basis only')
        meta['reviews'].append(record)
    changed[METADATA] = dump(meta)
    return changed


def require_review(value, before, review):
    if value is None or value['provenance']['status'] != 'confirmed':
        return
    if before and before['payload'] == value:
        return
    provenance = value['provenance']
    if (not review or not review.get('basis','').strip() or review.get('reviewer') != provenance.get('verified_by')
            or review.get('reviewed_date') != provenance.get('verified_date')):
        raise ValueError('Confirmed changes require matching reviewer/date and review basis')


def replace(collection, key, original, value, delete):
    existing = next((item for item in collection if item[key] == original), None) if original else None
    if original and existing is None:
        raise ValueError('Unknown referenced entity')
    if value is not None and any(item[key] == value[key] and item is not existing for item in collection):
        raise ValueError('Duplicate entity ID')
    if existing:
        collection.remove(existing)
    if not delete:
        collection.append(value)
