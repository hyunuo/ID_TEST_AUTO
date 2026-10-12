from hashlib import sha256
from pathlib import Path

from ssd_validator.application.desktop_workflow import DesktopWorkflow

ROOT = Path(__file__).resolve().parents[2]
LOG = b'NVME Identify Controller:\nsn:0000123\nsqes:0x66\ncqes:0x44\nnpss:4\nawun:0\nawupf:0\noacs:6\nunknown_extra:12\n'
BUNDLE = 'nvme-2.1-nvm-1.1'


def run(log=LOG, **options):
    return DesktopWorkflow(ROOT).analyze(log, 'TEST_LOG.txt', BUNDLE, experimental=True, **options)


def test_original_bytes_shared_normalizer_and_resolver_receive_same_facts():
    data = b'\xef\xbb\xbf' + LOG
    report = run(data)
    common = report['actual_data']
    normalization = common['normalization']
    assert common['kind'] == 'actual_data_set'
    assert normalization['source_format'] == 'text'
    assert normalization['layout']['data_kind'] == 'candidate'
    assert normalization['source']['sha256'] == sha256(data).hexdigest()
    assert common['validation_facts'] == report['validation']['actual_facts']
    assert len(common['validation_facts']) == 6
    assert next(f['value'] for f in common['actual_facts'] if f['field']['field_id'].endswith('.SN')) == '0000123'
    assert any(f['field'] == 'unknown_extra' for f in common['unmapped_fields'])
    assert all(f['raw_hex'] is None for f in normalization['fields'])


def test_field_verdict_expected_and_dependency_evidence_are_joined():
    report = run()
    oacs = next(r for r in report['fields'] if r['field'] == 'oacs')
    assert oacs['status'] == 'PASS' and oacs['knowledge_status'] == 'REVIEW'
    assert len(oacs['expected']) == len(oacs['rule_results']) == 2
    awun = next(r for r in report['fields'] if r['field'] == 'awun')
    assert awun['status'] == 'REVIEW' and awun['dependency_results']
    assert not awun['rule_results']


def test_missing_and_invalid_values_surface_in_field_table():
    report = run(LOG.replace(b'cqes:0x44\n', b''))
    row = next(r for r in report['fields'] if r['field'] == 'cqes')
    assert row['status'] == 'UNKNOWN' and row['value'] is None and row['expected']
    report = run(LOG.replace(b'awupf:0', b'awupf:65536'))
    assert report['validation']['status'] == 'ERROR'
    assert next(r for r in report['fields'] if r['field'] == 'awupf')['status'] == 'ERROR'
    assert next(f for f in report['actual_data']['normalization']['fields']
                if f['definition']['field']['field_id'].endswith('.AWUPF'))['status'] == 'ERROR'


def test_context_and_policy_selection_affect_same_dut_log():
    log = LOG.replace(b'oacs:6', b'oacs:0').replace(b'awupf:0', b'awupf:1')
    assert run(log)['validation']['status'] == 'FAIL'
    report = run(log, policy_mode='spec-only', context_facts={'logical_block_atomic_parameters_applicable': False})
    assert report['validation']['status'] == 'PASS'
    assert len(report['validation']['results']) == 4
    assert next(r for r in report['fields'] if r['field'] == 'awupf')['status'] == 'N/A'
    assert not any(a['id'].startswith('LAB.') for a in report['validation']['assumptions'])
    report = run(LOG, context_facts={'logical_block_atomic_parameters_applicable': None})
    assert report['validation']['status'] == 'UNKNOWN'
    assert report['validation']['assumptions'][0]['value'] == 'UNKNOWN'


def test_gui_home_contains_one_workflow_and_no_fixture_buttons():
    html = (ROOT / 'src/ssd_validator/gui/index.html').read_text(encoding='utf-8')
    assert '필드별 검사 결과' in html and 'Expected / 제약' in html
    assert 'data-op=' not in html and 'TEST/FIXTURE' not in html
    assert 'Builder 실행</button>' not in html
    assert 'policy_mode:' in html and 'context_facts:' in html
