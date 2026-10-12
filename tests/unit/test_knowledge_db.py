import copy
import json
from pathlib import Path

import pytest

from ssd_validator.application.database_workflow import DatabaseWorkflow
from ssd_validator.application.desktop_workflow import DesktopWorkflow

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = 'nvme-2.1-nvm-1.1'
LOG = b'NVME Identify Controller:\nsqes:0x66\ncqes:0x44\nnpss:4\nawun:0\nawupf:0\noacs:6\n'


@pytest.fixture
def workflow(tmp_path):
    return DatabaseWorkflow(ROOT, tmp_path / 'source.sqlite3')


def policy(workflow):
    return next(rule for rule in workflow.knowledge(BUNDLE)['rules'] if rule['provenance']['source_type'] == 'policy')


def test_migration_preserves_rules_and_results_and_database_is_original(workflow, tmp_path):
    old = DesktopWorkflow(ROOT).analyze(LOG, 'test.txt', BUNDLE, experimental=True)
    new = workflow.analyze(LOG, 'test.txt', BUNDLE, experimental=True)
    assert new['validation']['results'] == old['validation']['results']
    assert new['counts'] == old['counts']
    assert new['repository']['revision'] == 1
    assert 'sqlite://knowledge/revisions/1/' in new['validation']['profile']['input_source']['path']
    # Existing DB operates without the legacy source files.
    reopened = DatabaseWorkflow(tmp_path, workflow.repository.path)
    assert reopened.analyze(LOG, 'again.txt', BUNDLE, experimental=True)['counts'] == old['counts']


def test_edit_policy_changes_new_result_keeps_old_result_and_replays_old_revision(workflow):
    old = workflow.analyze(LOG, 'test.txt', BUNDLE, experimental=True)
    rule = policy(workflow)
    rule['check']['support'] = 'unsupported'
    saved = workflow.edit_rule(BUNDLE, expected_revision=1, reason='TEST explicit unsupported policy',
                               rule=rule, original_rule_id=rule['rule_id'])
    assert saved['revision'] == 2
    new = workflow.analyze(LOG, 'test.txt', BUNDLE, experimental=True)
    assert new['validation']['status'] == 'FAIL'
    assert workflow.load_run(old['run_id']) == old
    replay = workflow.replay(old['run_id'])
    assert replay['validation'] == old['validation']
    assert replay['repository']['revision'] == 1
    assert workflow.repository.head() == 2
    assert workflow.knowledge('nvme-2.0e-nvm-1.0e')['rules'] != workflow.knowledge(BUNDLE)['rules']


def test_stale_edit_blank_reason_and_invalid_rule_do_not_change_head(workflow):
    rule = policy(workflow)
    rule['check']['support'] = 'unsupported'
    workflow.edit_rule(BUNDLE, expected_revision=1, reason='TEST', rule=rule, original_rule_id=rule['rule_id'])
    with pytest.raises(ValueError, match='REVISION_CONFLICT'):
        workflow.edit_rule(BUNDLE, expected_revision=1, reason='stale', rule=rule, original_rule_id=rule['rule_id'])
    with pytest.raises(ValueError, match='reason'):
        workflow.edit_rule(BUNDLE, expected_revision=2, reason='', rule=rule, original_rule_id=rule['rule_id'])
    rule['check'] = {'type': 'RANGE', 'min': 5, 'max': 1}
    with pytest.raises(ValueError):
        workflow.edit_rule(BUNDLE, expected_revision=2, reason='bad', rule=rule, original_rule_id=rule['rule_id'])
    assert workflow.repository.head() == 2


def test_export_import_roundtrip_and_path_traversal_rejected(workflow, tmp_path):
    exported = workflow.export_sources()
    other = DatabaseWorkflow(ROOT, tmp_path / 'other.sqlite3')
    edited = copy.deepcopy(exported)
    path = f'knowledge/experimental/id_ctrl/{BUNDLE}.json'
    value = json.loads(edited['sources'][path])
    value['context']['facts']['logical_block_atomic_parameters_applicable'] = False
    edited['sources'][path] = json.dumps(value)
    workflow.import_sources(edited, expected_revision=1, reason='TEST context change')
    other.import_sources(workflow.export_sources(), expected_revision=1, reason='TEST import')
    assert other.export_sources()['sources'] == workflow.export_sources()['sources']
    for path in ['../escape.json', 'knowledge/../../escape.json', 'generated/source.json',
                 'knowledge/generated/source.json', 'C:/escape.json', 'knowledge\\escape.json']:
        bad = copy.deepcopy(exported)
        bad['sources'][path] = '{}'
        with pytest.raises(ValueError):
            workflow.import_sources(bad, expected_revision=2, reason='TEST traversal')
    assert workflow.repository.head() == 2


def test_new_delete_duplicate_and_unsupported_rules_are_validated(workflow):
    rule = policy(workflow)
    with pytest.raises(ValueError, match='Duplicate rule'):
        workflow.edit_rule(BUNDLE, expected_revision=1, reason='duplicate', rule=rule)
    rule['rule_id'] = 'TEST.NEW_POLICY'
    workflow.edit_rule(BUNDLE, expected_revision=1, reason='TEST new rule', rule=rule)
    assert len(workflow.knowledge(BUNDLE)['rules']) == 7
    workflow.edit_rule(BUNDLE, expected_revision=2, reason='TEST remove', rule=None, original_rule_id=rule['rule_id'], delete=True)
    assert len(workflow.knowledge(BUNDLE)['rules']) == 6
    rule['check'] = {'type': 'DERIVED', 'function': 'TEST', 'inputs': ['NVME.CNS01.OACS']}
    with pytest.raises(ValueError, match='Unsupported'):
        workflow.edit_rule(BUNDLE, expected_revision=3, reason='unsupported', rule=rule)
    assert workflow.repository.head() == 3


def test_missing_context_and_candidate_status_preserved(workflow):
    report = workflow.analyze(LOG, 'test.txt', BUNDLE, experimental=True,
        context_facts={'logical_block_atomic_parameters_applicable': None}, policy_mode='spec-only')
    assert report['validation']['status'] == 'UNKNOWN'
    assert len(report['validation']['results']) == 4
    assert report['authoritative'] is False
    assert all(rule['provenance']['status'] == 'candidate' for rule in workflow.knowledge(BUNDLE)['rules']
               if rule['provenance']['source_type'] == 'spec')
    assert workflow.load_run(report['run_id']) == report


def test_conflicting_rules_are_preserved_without_last_write_wins(workflow):
    rule = policy(workflow)
    rule['rule_id'] = 'TEST.CONTRADICTORY_POLICY'
    rule['check']['support'] = 'unsupported'
    workflow.edit_rule(BUNDLE, expected_revision=1, reason='TEST conflict preservation', rule=rule)
    report = workflow.analyze(LOG, 'test.txt', BUNDLE, experimental=True)
    assert report['validation']['status'] == 'CONFLICT'
    assert len(workflow.knowledge(BUNDLE)['rules']) == 7
    assert any(r['status'] == 'CONFLICT' for r in report['validation']['results'])


def test_invalid_import_does_not_overwrite_or_approve_sources(workflow):
    exported = workflow.export_sources()
    path = f'knowledge/experimental/id_ctrl/{BUNDLE}.json'
    bad = copy.deepcopy(exported)
    config = json.loads(bad['sources'][path])
    config['candidate_knowledge_hash'] = '0' * 64
    bad['sources'][path] = json.dumps(config)
    with pytest.raises(Exception, match='CANDIDATE_SOURCE_CHANGED'):
        workflow.import_sources(bad, expected_revision=1, reason='TEST invalid source pin')
    assert workflow.repository.head() == 1
    assert workflow.export_sources() == exported
    rule = policy(workflow)
    rule['provenance']['status'] = 'confirmed'
    with pytest.raises(ValueError):
        workflow.edit_rule(BUNDLE, expected_revision=1, reason='TEST cannot manufacture approval', rule=rule,
                           original_rule_id=rule['rule_id'])
    assert workflow.repository.head() == 1
