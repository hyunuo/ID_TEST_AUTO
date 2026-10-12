"""Execute editable unreviewed rules against saved observations using the existing core."""

import json
from hashlib import sha256
from pathlib import Path

from pydantic import Field

from ssd_validator.application.build_knowledge import compile_knowledge
from ssd_validator.application.rule_pilot import _unique_object
from ssd_validator.analyzer.id_ctrl_actual import normalize_id_ctrl
from ssd_validator.errors import KnowledgeError
from ssd_validator.models.common import DomainModel
from ssd_validator.models.effective import SourceFile
from ssd_validator.models.runtime import (
    BundleSelection, CapabilityMapping, FieldRegistration,
    PilotMappings, RuntimeContext, RuntimeRule,
)
from ssd_validator.resolver import resolve, evaluate
from ssd_validator.application.knowledge_management import bundle_path, Binding, METADATA


class ExperimentalConfiguration(DomainModel):
    bundle: BundleSelection
    context: RuntimeContext
    rules: tuple[RuntimeRule, ...]
    capabilities: tuple[CapabilityMapping, ...] = ()
    field_evidence: dict[str, dict] = Field(default_factory=dict)
    assumptions: tuple[dict, ...] = ()
    candidate_knowledge_hash: str


def evaluate_log(root: Path, observation_report: dict, source_bytes: bytes, *, context_facts: dict | None = None,
                 policy_mode: str = 'assumed-development', extra_rules=(), context_base=None,scope_context=False) -> dict:
    folder = root / 'knowledge/experimental/id_ctrl'
    bundle_id = observation_report['bundle']['bundle_id']
    # IDs originate from the registered Bundle selector, never arbitrary request paths.
    catalog = json.loads((root / 'candidates/nvme/catalog.json').read_text(encoding='utf-8'))
    if bundle_id not in {b['bundle_id'] for b in catalog['bundles']}:
        raise KnowledgeError('UNKNOWN_BUNDLE', bundle_id)
    input_path = root / bundle_path(bundle_id)
    buffer = input_path.read_bytes()
    config = ExperimentalConfiguration.model_validate(json.loads(buffer.decode('utf-8'), object_pairs_hook=_unique_object))
    if policy_mode not in {'assumed-development', 'spec-only'}:
        raise KnowledgeError('POLICY_SELECTION', 'Choose a registered policy profile')
    context_values = dict(config.context.facts if context_base is None else context_base)
    if context_facts is not None:
        if not isinstance(context_facts, dict):
            raise ValueError('Context must be an object')
        for key, value in context_facts.items():
            if value is None:
                context_values.pop(key, None)
            else:
                context_values[key] = value
    if not scope_context and any(r.rule_id.startswith('NVME.STAGE5.') for r in config.rules):
        if any(k.startswith('input.') or k=='namespace.query_is_specific' for k in (context_facts or {})):
            raise ValueError('Input/query applicability facts are derived from captures, not user-overridable')
        context_values.update({'input.has_namespace':False,'input.has_controller':True})
        context_values.pop('namespace.query_is_specific',None)
    context = RuntimeContext(bundle_id=config.context.bundle_id, facts=context_values)
    if config.bundle.bundle_id != bundle_id or config.context.bundle_id != bundle_id:
        raise KnowledgeError('BUNDLE_MISMATCH', 'Experimental configuration must match the selected DUT Bundle')
    if config.candidate_knowledge_hash != observation_report['knowledge_manifest']['knowledge_hash']:
        raise KnowledgeError('CANDIDATE_SOURCE_CHANGED', 'Reconcile experimental references with current candidate knowledge')
    build = compile_knowledge(folder / bundle_id)
    snapshots = tuple(s for s in build.snapshots if s.spec.key in config.bundle.snapshot_keys)
    registrations = []
    meta_path = root / METADATA
    binding_values = json.loads(meta_path.read_text(encoding='utf-8')).get('bindings', {}).get(bundle_id, {}) if meta_path.exists() else {}
    for snapshot in snapshots:
        for item in snapshot.fields:
            binding = Binding.model_validate(binding_values.get(item.schema.field_id, {}))
            registrations.append(FieldRegistration(schema_definition=item.schema, cns=binding.cns, csi=binding.csi, array_count=binding.array_count,
                provenance=item.history[-1].provenance, history=item.history))
    mappings = PilotMappings(execution_mode='experimental', bundle=config.bundle, fields=tuple(registrations),
        rules=tuple(r for r in config.rules if policy_mode != 'spec-only' or r.provenance.source_type != 'policy')+tuple(extra_rules),
        capabilities=config.capabilities,
        input_source=SourceFile(path=input_path.as_posix(), sha256=sha256(buffer).hexdigest()))
    profile = resolve(context, snapshots, mappings)
    common, facts = normalize_id_ctrl(profile, observation_report, source_bytes, bindings=binding_values)
    blocked = common['blocked_inputs']
    result = evaluate(profile, facts).model_dump(mode='json')
    assumptions = []
    for item in config.assumptions:
        if context_base is not None:
            continue
        assumption = dict(item)
        if assumption['id'].startswith('LAB.') and policy_mode == 'spec-only':
            continue
        if assumption['id'] in config.context.facts:
            assumption['configured_value'] = assumption['value']
            assumption['value'] = context.facts.get(assumption['id'], 'UNKNOWN')
        assumptions.append(assumption)
    result.update(assumptions=assumptions, field_evidence=config.field_evidence, actual_data=common,
                  selection={'policy_mode': policy_mode, 'context': context.model_dump(mode='json')},
                  build_manifest=build.manifest.model_dump(mode='json'), blocked_inputs=blocked)
    # Malformed or ambiguous observations must remain visible in the aggregate.
    if blocked:
        result['status'] = 'ERROR' if any(b['status'] == 'ERROR' for b in blocked) else 'CONFLICT'
    if common['normalization']['status'] == 'ERROR':
        result['status'] = 'ERROR'
    return result
