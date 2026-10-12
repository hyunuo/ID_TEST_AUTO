import json
import shutil
from pathlib import Path

import pytest

from ssd_validator.application.desktop_workflow import DesktopWorkflow
from ssd_validator.application.build_knowledge import compile_knowledge
from ssd_validator.errors import KnowledgeError
from ssd_validator.models.runtime import PilotMappings
from ssd_validator.resolver import resolve

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = 'nvme-2.1-nvm-1.1'
LOG = b'NVME Identify Controller:\nmn:TEST_MODEL\nsqes:0x66\ncqes:0x44\nnpss:4\nawun:0\nawupf:0\noacs:0x6\n'


def run(log=LOG, root=ROOT, bundle=BUNDLE):
    return DesktopWorkflow(root).analyze(log, 'TEST_LOG.txt', bundle, experimental=True)['validation']


def edit_config(tmp_path, change):
    shutil.copytree(ROOT / 'knowledge/experimental', tmp_path / 'knowledge/experimental')
    shutil.copytree(ROOT / 'candidates', tmp_path / 'candidates')
    path = tmp_path / 'knowledge/experimental/id_ctrl' / f'{BUNDLE}.json'
    payload = json.loads(path.read_text(encoding='utf-8'))
    change(payload)
    path.write_text(json.dumps(payload), encoding='utf-8')
    return tmp_path


def test_saved_log_pass_has_unreviewed_provenance_and_actual_source():
    for bundle in (BUNDLE, 'nvme-2.0e-nvm-1.0e'):
        report = run(bundle=bundle)
        assert report['status'] == 'PASS'
        assert len(report['results']) == 6
        assert report['kind'] == 'experimental_validation_report'
        assert report['authoritative'] is False
        assert report['profile']['data_kind'] == 'production'
        assert report['profile']['execution_mode'] == 'experimental'
        assert {r['rule']['provenance']['status'] for r in report['results']} == {'candidate','provisional'}
        assert all(f['source']['sha256'] for f in report['actual_facts'])
        assert report['assumptions'] and report['field_evidence'] and report['build_manifest']


@pytest.mark.parametrize('old,new,rule',[
    (b'awupf:0',b'awupf:1','ATOMIC_POWER_FAIL_BOUND'),
    (b'sqes:0x66',b'sqes:0x67','SQES_REQUIRED'),
    (b'cqes:0x44',b'cqes:0x43','CQES_REQUIRED'),
    (b'npss:4',b'npss:32','POWER_STATE_LIMIT'),
])
def test_violations_use_existing_rule_evaluator(old,new,rule):
    report = run(LOG.replace(old,new))
    assert report['status'] == 'FAIL'
    assert next(r for r in report['results'] if r['rule']['rule_id'].endswith(rule))['status'] == 'FAIL'


def test_actual_cannot_disable_assumed_capability_requirement():
    report = run(LOG.replace(b'oacs:0x6',b'oacs:0'))
    assert [r['status'] for r in report['results'] if '.POLICY.' in r['rule']['rule_id']] == ['FAIL','FAIL']


def test_missing_duplicate_and_bad_type_do_not_become_zero():
    assert run(LOG.replace(b'oacs:0x6\n',b''))['status'] == 'UNKNOWN'
    assert run(LOG+b'awupf:0\n')['status'] == 'ERROR'
    assert run(LOG.replace(b'awupf:0',b'awupf:invalid'))['status'] == 'ERROR'


def test_missing_assumption_and_false_condition(tmp_path):
    root = edit_config(tmp_path, lambda c: c['context']['facts'].clear())
    assert run(root=root)['status'] == 'UNKNOWN'
    path = root / 'knowledge/experimental/id_ctrl' / f'{BUNDLE}.json'
    config = json.loads(path.read_text(encoding='utf-8'))
    config['context']['facts']['logical_block_atomic_parameters_applicable'] = False
    path.write_text(json.dumps(config),encoding='utf-8')
    report = run(LOG.replace(b'awupf:0',b'awupf:1'), root=root)
    assert next(r for r in report['results'] if r['rule']['rule_id'].endswith('ATOMIC_POWER_FAIL_BOUND'))['status'] == 'N/A'


def test_experimental_conflict_is_not_last_write_wins(tmp_path):
    def change(config):
        for name,kind,value in [('LOW','MIN',3),('HIGH','MAX',2)]:
            original = next(r for r in config['rules'] if r['target']['field_id'].endswith('.NPSS'))
            config['rules'].append({**original,'rule_id':'EXPERIMENTAL.'+name,'check':{'type':kind,'value':value}})
    root = edit_config(tmp_path, change)
    assert run(root=root)['status'] == 'CONFLICT'


def test_strict_execution_still_rejects_production_profile():
    report = run()
    from ssd_validator.models.runtime import RuntimeContext, FieldRegistration, RuntimeRule, BundleSelection
    p = report['profile']
    mappings = PilotMappings(bundle=BundleSelection.model_validate(p['bundle']),
        fields=tuple(FieldRegistration.model_validate(f) for f in p['fields']),
        rules=tuple(RuntimeRule.model_validate(e['rule']) for e in p['entries']))
    snapshots = compile_knowledge(ROOT / 'knowledge/experimental/id_ctrl' / BUNDLE).snapshots
    with pytest.raises(KnowledgeError, match='PILOT_FIXTURE_ONLY'):
        resolve(RuntimeContext.model_validate(p['context']), snapshots, mappings)


def test_permission_is_not_automatically_mandatory(tmp_path):
    def change(config):
        config['rules'][0]['modality'] = 'permission'
    root = edit_config(tmp_path, change)
    result = run(root=root)
    assert next(r for r in result['results'] if r['rule']['rule_id'].endswith('SQES_REQUIRED'))['status'] == 'REVIEW'
