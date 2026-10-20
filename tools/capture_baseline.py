"""Record the current engine's verdicts on synthetic TEST inputs as a refactoring baseline.

A temporary database registers the NVMe expansion pack and the OCP 2.6 candidates (originals
verified from spec/), binds a TEST profile for OCP, and analyses the fixtures under
tests/fixtures/baseline and tests/fixtures/saved_captures. Only verdict-relevant fields are kept,
so storage/representation changes can be checked for unchanged results.

    python tools/capture_baseline.py           # compare with the stored baseline
    python tools/capture_baseline.py --write   # replace it (intended verdict changes only)
"""
import argparse
import base64
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from ssd_validator.application import nvme_expansion, supplemental_requirements as ocp  # noqa: E402
from ssd_validator.application.database_workflow import DatabaseWorkflow  # noqa: E402
from ssd_validator.application.product_profiles import PRODUCTS  # noqa: E402
from ssd_validator.application.knowledge_management import change_entity, dump  # noqa: E402

BASELINE = ROOT / 'tests/golden/baseline/engine_baseline.json'
FIXTURES = ROOT / 'tests/fixtures'
TEST_PROVENANCE = {'source_type': 'fixture', 'source_document': 'TEST_PRODUCT', 'source_version': 'v1',
                   'source_section': 'Synthetic TEST only', 'status': 'provisional'}
OCP_CONTEXT = {'ocp.datacenter_product': True, 'ocp.version': '2.6', 'host.lbaf_extension_enabled': False,
               'namespace.lbaf.0.metadata_supported': False}


def database(directory):
    workflow = DatabaseWorkflow(ROOT, directory / 'TEST-baseline.sqlite3')
    nvme_expansion.register(workflow, ROOT / nvme_expansion.PACK_PATH, ROOT / 'spec', expected_revision=1, reason='TEST baseline')
    pack = ocp.parse((ROOT / ocp.CANDIDATE_PATH).read_text(encoding='utf-8'))
    ocp.register(workflow, ROOT / ocp.CANDIDATE_PATH, ROOT / 'spec', expected_revision=2, reason='TEST baseline')
    sources = change_entity(workflow.repository.sources(), kind='document',
                            payload={k: TEST_PROVENANCE[k] for k in ('source_type', 'source_document', 'source_version')})
    products = json.loads(sources[PRODUCTS])
    for bundle in pack.bundles:
        products['profiles'].append({'profile_id': 'TEST.' + bundle.bundle_id, 'title': 'Synthetic test binding only',
                                     'bundle_id': bundle.bundle_id, 'policy_ids': [bundle.policy.policy_id],
                                     'conditions': [], 'provenance': TEST_PROVENANCE})
    sources[PRODUCTS] = dump(products)
    workflow.import_sources({'format': 'ssd-validator-source-v1', 'sources': sources}, expected_revision=3, reason='TEST baseline profile')
    return workflow, [b.bundle_id for b in pack.bundles]


def capture(capture_id, path, command, nsid=None):
    item = {'capture_id': capture_id, 'filename': path.name, 'command': command, 'dut_id': 'TEST', 'session_id': 'TEST',
            'content_base64': base64.b64encode(path.read_bytes()).decode('ascii')}
    return {**item, 'nsid': nsid} if nsid is not None else item


def scenarios():
    baseline, saved = FIXTURES / 'baseline', FIXTURES / 'saved_captures'
    good = json.loads((saved / 'TEST-input.json').read_text(encoding='utf-8'))
    bad = {'captures': [capture('TEST_CTRL', baseline / 'TEST-ctrl-violations.txt', 'id-ctrl'),
                        capture('TEST_NS', baseline / 'TEST-ns-violations.txt', 'id-ns', nsid=1)]}
    for policy in ('assumed-development', 'spec-only'):
        yield f'ctrl-log/{policy}', 'log', (saved / 'TEST-id-ctrl.txt').read_bytes(), {'policy_mode': policy}
        yield f'ctrl-violations-log/{policy}', 'log', (baseline / 'TEST-ctrl-violations.txt').read_bytes(), {'policy_mode': policy}
    yield 'captures-good', 'captures', good, {}
    yield 'captures-violations', 'captures', bad, {}
    yield 'captures-good/ocp-profile', 'captures', good, {'profile': True, 'context_facts': OCP_CONTEXT}
    yield 'captures-violations/ocp-profile', 'captures', bad, {'profile': True, 'context_facts': OCP_CONTEXT}


def project(value):
    """Keep verdicts, observed values and provenance; drop run ids, hashes and storage details."""
    if isinstance(value, dict):
        if 'rule' in value and 'status' in value and isinstance(value['rule'], dict) and 'rule_id' in value['rule']:
            rule = value['rule']
            return {'rule_id': rule['rule_id'], 'status': value['status'], 'condition_state': value.get('condition_state'),
                    'source': [rule['provenance'].get('source_document'), rule['provenance'].get('source_section')],
                    'observed': [[o['reference'].get('field') and o['reference']['field']['field_id'] or o['reference'].get('path'),
                                  o.get('found'), o.get('value')] for o in value.get('observations', [])]}
        if 'field' in value and 'status' in value and 'value' in value and isinstance(value['field'], str):
            return {'field': value['field'], 'value': value['value'], 'status': value['status']}
        kept = {}
        for key in ('status', 'counts', 'results', 'fields', 'scopes', 'validation', 'scope', 'scope_id', 'input_errors'):
            if key in value:
                kept[key] = project(value[key])
        return kept
    if isinstance(value, list):
        return [project(v) for v in value]
    return value


def run():
    with tempfile.TemporaryDirectory() as directory:
        workflow, bundles = database(Path(directory))
        result = {}
        for bundle in bundles:
            for name, kind, payload, options in scenarios():
                options = dict(options)
                profile = 'TEST.' + bundle if options.pop('profile', False) else None
                if kind == 'log':
                    report = workflow.analyze(payload, 'TEST.txt', bundle, experimental=True, **options)
                else:
                    report = workflow.analyze_captures(payload, bundle, profile_id=profile, **options)
                result[f'{bundle}/{name}'] = project(report)
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    current = json.dumps(run(), ensure_ascii=False, indent=1, sort_keys=True) + '\n'
    if args.write:
        BASELINE.parent.mkdir(parents=True, exist_ok=True)
        BASELINE.write_text(current, encoding='utf-8', newline='\n')
        print(f'wrote {BASELINE.relative_to(ROOT)}')
        return
    stored = BASELINE.read_text(encoding='utf-8') if BASELINE.exists() else ''
    print('baseline unchanged' if stored == current else 'BASELINE CHANGED')
    sys.exit(0 if stored == current else 1)


if __name__ == '__main__':
    main()
