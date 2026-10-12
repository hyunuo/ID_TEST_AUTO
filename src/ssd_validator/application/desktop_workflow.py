"""GUI orchestration over existing Builder, Resolver and candidate knowledge services."""

import re
from pathlib import Path

from ssd_validator.analyzer.id_ctrl_log import analyze_id_ctrl
from ssd_validator.application.build_knowledge import compile_knowledge
from ssd_validator.application.candidate_knowledge import compile_candidates, diff_bundles
from ssd_validator.application.normalize_actual import run_normalization
from ssd_validator.application.rule_pilot import run_pilot


class DesktopWorkflow:
    def __init__(self, root: Path):
        self.root = root

    def candidates(self):
        return compile_candidates(self.root / 'candidates/nvme')

    def analyze(self, data: bytes, filename: str, bundle_id: str, *, experimental: bool = False,
                context_facts: dict | None = None, policy_mode: str = 'assumed-development', extra_rules=(), context_base=None,scope_context=False):
        report = analyze_id_ctrl(data, filename)
        _, bundles, manifest, _ = self.candidates()
        if bundle_id not in bundles:
            raise ValueError('Unknown Bundle')
        bundle = bundles[bundle_id]
        structures = [s for s in bundle['structures'] if s['cns'] == 1]
        # Explicitly managed Builder fields can be added without re-extracting all PDF structures.
        from ssd_validator.application.knowledge_management import base_path, yaml_read
        path = self.root / base_path(bundle_id)
        managed = yaml_read(path.read_text(encoding='utf-8'))['fields'] if path.exists() else []
        for row in report['fields']:
            definitions = []
            for structure in structures:
                for definition in structure['definitions']:
                    for field in definition['fields']:
                        aliases = {field['field_id'].split('.')[-1].casefold(), field['name'].casefold()}
                        aliases.update(a.casefold() for a in re.findall(r'\b[A-Z][A-Z0-9]{1,}\b', field['name']))
                        if row['field'].casefold() in aliases:
                            definitions.append({'document_id': definition['document_id'], **field})
            ids = {d['field_id'] for d in definitions}
            for field in managed:
                if field.get('command')!='id-ctrl':
                    continue
                if row['field'].casefold() in {field['field_id'].split('.')[-1].casefold(),field['name'].casefold()} and field['field_id'] not in ids:
                    definitions.append({'field_id':field['field_id'],'name':field['name'],
                        'byte_offset':field['offset'],'byte_length':field['length'],
                        'review_status':'candidate','origin':'managed_builder_source'})
            ids = {d['field_id'] for d in definitions}
            row['definitions'] = definitions
            row['requirements'] = [r for r in bundle['requirements'] if any(
                m['field_id'] in ids and m['structure_id'] == 'NVME.CNS01'
                for link in r['field_links'] for m in link['matches'])]
            conflicting = any(segment['state'] == 'CONFLICT' and any(
                d['field_id'] in ids for d in segment['definitions'])
                for structure in structures for segment in structure['segments'])
            if row['status'] != 'ERROR':
                if len(ids) > 1 or conflicting:
                    row.update(status='CONFLICT', reason='복수 필드 매핑: 자동 선택하지 않음')
                elif definitions:
                    row.update(status='REVIEW', reason='규격 후보 연결됨; 승인된 기대값은 아직 없음')
                else:
                    row.update(status='UNKNOWN', reason='선택 Bundle에서 필드 매핑을 확인하지 못함')
        report['counts'] = {s: sum(r['status'] == s for r in report['fields']) for s in ('PASS','FAIL','REVIEW','UNKNOWN','CONFLICT','ERROR')}
        report.update(bundle=bundle['bundle'], knowledge_manifest=manifest,
                      validation_scope='candidate_review_only', authoritative=False)
        if experimental:
            from ssd_validator.application.experimental_validation import evaluate_log
            report['validation'] = evaluate_log(self.root, report, data, context_facts=context_facts, policy_mode=policy_mode,
                extra_rules=extra_rules,context_base=context_base,scope_context=scope_context)
            report['actual_data'] = report['validation']['actual_data']
            report['validation_scope'] = 'experimental_unreviewed_rules'
            for row in report['fields']:
                ids = {d['field_id'] for d in row['definitions']}
                row['knowledge_status'] = row['status']
                row['rule_results'] = [r for r in report['validation']['results'] if r['rule']['target']['field_id'] in ids]
                row['expected'] = [r['rule'] for r in row['rule_results']]
                row['dependency_results'] = [r for r in report['validation']['results'] if any(
                    o['reference'].get('field') and o['reference']['field']['field_id'] in ids
                    for o in r['observations']) and r not in row['rule_results']]
                normalized = [f for f in report['actual_data']['normalization']['fields'] if f['definition']['field']['field_id'] in ids]
                row['normalization'] = normalized
                blocks = [b for b in report['actual_data']['blocked_inputs'] if ids & set(b['field_ids'])]
                if row['status'] not in {'ERROR', 'CONFLICT'}:
                    if blocks:
                        row.update(status='ERROR' if any(b['status'] == 'ERROR' for b in blocks) else 'CONFLICT',
                                   reason=' / '.join(b['reason'] for b in blocks))
                    elif any(f['status'] == 'ERROR' for f in normalized):
                        row.update(status='ERROR', reason='Actual 정규화 타입/범위 오류')
                    elif row['rule_results']:
                        row['status'] = next(s for s in ('ERROR','CONFLICT','FAIL','UNKNOWN','REVIEW','PASS','N/A')
                                             if any(r['status'] == s for r in row['rule_results']))
                        row['reason'] = ' / '.join(r['reason'] for r in row['rule_results'])
                    elif row['definitions']:
                        row['reason'] = '값과 근거 보존; 이 필드의 실행 규칙 없음'
            present_ids = {d['field_id'] for row in report['fields'] for d in row['definitions']}
            for registration in report['validation']['profile']['fields']:
                if (registration['cns'],registration['csi'])!=(1,0):
                    continue # Single controller adapter never manufactures missing Namespace rows.
                identity = registration['schema_definition']['field_id']
                results = [r for r in report['validation']['results'] if r['rule']['target']['field_id'] == identity]
                if identity not in present_ids:
                    report['fields'].append({'field': identity.split('.')[-1].lower(), 'raw_value': None, 'value': None,
                        'value_type': registration['schema_definition']['value_type'], 'line': None, 'status': 'UNKNOWN',
                        'knowledge_status': 'UNKNOWN', 'reason': '로그에 필요한 입력 필드 없음',
                        'definitions': [report['validation']['field_evidence'][identity]], 'requirements': [],
                        'expected': [r['rule'] for r in results], 'rule_results': results, 'dependency_results': [],
                        'normalization': [f for f in report['actual_data']['normalization']['fields']
                                          if f['definition']['field']['field_id'] == identity]})
            report['knowledge_counts'] = report['counts']
            report['counts'] = {s: sum(r['status'] == s for r in report['fields'])
                                for s in ('PASS','FAIL','N/A','REVIEW','UNKNOWN','CONFLICT','ERROR')}
        if 'validation' in report:
            from ssd_validator.application.supplemental_requirements import trace
            supplemental=trace(self.root,report['validation'],bundle_id)
            if supplemental is not None:report['supplemental_trace']=supplemental
        return report

    def operation(self, name: str):
        fixture = self.root / 'tests/fixtures'
        if name == 'pilot':
            return run_pilot(fixture / 'rule_pilot/knowledge', fixture / 'rule_pilot/input.json').model_dump(mode='json')
        if name == 'builder':
            build = compile_knowledge(fixture / 'rule_pilot/knowledge')
            return {'data_kind': 'fixture', 'manifest': build.manifest.model_dump(mode='json'),
                    'snapshots': [s.model_dump(mode='json') for s in build.snapshots]}
        if name == 'normalize':
            folder = fixture / 'actual_normalization'
            return run_normalization(folder / 'layout.json', folder / 'capture.json', raw_path=folder / 'response.raw').model_dump(mode='json')
        if name == 'bundle-diff':
            _, bundles, _, _ = self.candidates()
            return diff_bundles(bundles['nvme-2.0e-nvm-1.0e'], bundles['nvme-2.1-nvm-1.1'])
        raise ValueError('Unknown operation')
