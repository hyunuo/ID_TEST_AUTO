"""Text adapter into shared normalization and ActualFact contracts; no invented raw bytes."""

from ssd_validator.analyzer.actual_normalizer import layout_from_profile, normalize_json
from ssd_validator.models.actual_data import CaptureMetadata, IdentifyQuery
from ssd_validator.models.effective import SourceFile
from ssd_validator.models.runtime import ActualFact, FieldRef


def normalize_id_ctrl(profile, report: dict, source_bytes: bytes, *, bindings=None):
    bindings = bindings or {}
    source = SourceFile(path=report['source']['filename'], sha256=report['source']['sha256'])
    payload, observed, blocked, lines = {}, [], [], {}
    for row in report['fields']:
        ids = {d['field_id'] for d in row['definitions']}
        if row['status'] in {'ERROR', 'CONFLICT'}:
            blocked.append({'field': row['field'], 'field_ids': sorted(ids), 'status': row['status'], 'line': row['line'], 'reason': row['reason']})
            continue
        if len(ids) != 1:
            continue
        identity = next(iter(ids))
        if identity in payload:
            # Different printed aliases must never overwrite a field silently.
            blocked.append({'field': row['field'], 'field_ids': [identity], 'status': 'CONFLICT', 'line': row['line'], 'reason': 'Multiple log names map to one field'})
            payload.pop(identity)
            continue
        payload[identity] = row['value']
        lines[identity] = {'field': row['field'], 'line': row['line'], 'raw_value': row['raw_value']}
    blocked_ids = {d['field_id'] for r in report['fields'] for d in r['definitions']
                   if any(b['field'] == r['field'] for b in blocked)}
    for identity in blocked_ids:
        payload.pop(identity, None)
    for identity, value in sorted(payload.items()):
        observed.append(ActualFact(field=FieldRef(field_id=identity), value=value, source=source,
                                   capture_id='SAVED_ID_CTRL_LOG'))
    query = IdentifyQuery(cns=1, csi=0)
    if not any((f.cns,f.csi)==(1,0) for f in profile.fields):
        return {'kind':'actual_data_set','bundle_id':profile.bundle.bundle_id,
                'source':source.model_dump(mode='json'),'source_format':'text',
                'actual_facts':[f.model_dump(mode='json') for f in observed], 'validation_facts':[],
                'normalization':{'status':'UNKNOWN','fields':[],'errors':[],
                    'reason':'No CNS01 fields registered; observations retained without decoding'},
                'source_lines':lines,'blocked_inputs':blocked,'capture_assumptions':[],
                'unmapped_fields':[r for r in report['fields'] if not r['definitions']],
                'power_states':report['power_states']}, ()
    paths = {f.schema_definition.field_id + (f'[{i}]' if f.array_count else ''):
             (f.schema_definition.field_id + (f'[{i}]' if f.array_count else ''),)
             for f in profile.fields for i in range(f.array_count or 1)}
    layout = layout_from_profile(profile, query, response_size=4096,
                                array_strides={key:item['array_stride'] for key,item in bindings.items() if item.get('array_stride')},
                                json_paths=paths)
    capture = CaptureMetadata(capture_id='SAVED_ID_CTRL_LOG', tool_name='saved-id-ctrl-text', tool_version='UNKNOWN',
                              device_id=str(report['identity'].get('sn') or 'UNKNOWN'), query=query,
                              advertised_nvme_version=report['advertised_nvme_version'])
    normalized = normalize_json(layout, capture, payload, source_path=source.path, source_bytes=source_bytes)
    # The intermediate object came from text parsing, not an nvme-cli JSON response.
    normalized = normalized.model_copy(update={'source_format': 'text'})
    facts = tuple(ActualFact(field=f.definition.field, value=f.value, source=normalized.source,
                            capture_id=capture.capture_id) for f in normalized.fields if f.status in {'OBSERVED', 'REVIEW'})
    common = {'kind': 'actual_data_set', 'bundle_id': profile.bundle.bundle_id,
              'source': source.model_dump(mode='json'), 'source_format': 'text',
              'actual_facts': [f.model_dump(mode='json') for f in observed],
              'validation_facts': [f.model_dump(mode='json') for f in facts],
              'normalization': normalized.model_dump(mode='json'), 'source_lines': lines, 'blocked_inputs': blocked,
              'capture_assumptions': ['CNS01 from text header; CSI0 selected NVM profile, original query flags unknown',
                                      'Original nvme-cli version and commit are UNKNOWN; raw response bytes are not reconstructed'],
              'unmapped_fields': [r for r in report['fields'] if not r['definitions']],
              'power_states': report['power_states']}
    return common, facts
