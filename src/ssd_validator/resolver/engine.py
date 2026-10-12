"""Deterministic offline TEST/FIXTURE resolver; no implicit specification authority."""

from collections import defaultdict
from operator import eq, ge, gt, le, lt, ne

from ssd_validator.errors import KnowledgeError
from ssd_validator.knowledge.validation import literal_constraints_compatible
from ssd_validator.models.effective import EffectiveSnapshot
from ssd_validator.models.provenance import KnowledgeStatus
from ssd_validator.models.rules import ExactCheck, RequirementRule
from ssd_validator.models.identifiers import TargetRef
from ssd_validator.models.runtime import (
    ActualFact, Condition, EffectiveExpectedProfile, ExpectedEntry, FactRef,
    FieldCompare, FieldRef, InputError, Observation, PilotMappings, RuleResult, RuntimeContext,
    RuntimeRule, ValidationReport,
)


class _FactError(ValueError):
    pass


def _registration(ref, fields):
    if ref.field_id not in fields:
        raise _FactError(f"Unregistered field: {ref.field_id}")
    item = fields[ref.field_id]
    schema = item.schema_definition
    if schema.lifecycle != "active":
        raise _FactError(f"Deprecated field: {ref.field_id}")
    if item.array_count is None and ref.index is not None:
        raise _FactError(f"Scalar field cannot have an index: {ref.key}")
    if item.array_count is not None and (ref.index is None or ref.index >= item.array_count):
        raise _FactError(f"Array needs an in-range index: {ref.key}")
    if ref.bit is not None:
        if schema.value_type != "bitmask" or ref.bit >= schema.length * 8:
            raise _FactError(f"Invalid bit reference: {ref.key}")
        if any(b.bit == ref.bit and b.lifecycle != "active" for b in schema.bits):
            raise _FactError(f"Deprecated bit: {ref.key}")
    return item


def _read(ref, context, actual, fields, observations):
    if ref.source == "context":
        found, value = ref.path in context.facts, context.facts.get(ref.path)
    else:
        registration = _registration(ref.field, fields)
        key = (ref.field.field_id, ref.field.index)
        found, value = key in actual, actual.get(key)
        observations.append(Observation(reference=ref, found=found, value=value))
        if not found:
            return False, None
        schema = registration.schema_definition
        if schema.value_type in {"integer", "bitmask"}:
            if type(value) is not int or not 0 <= value < 1 << (schema.length * 8):
                raise _FactError(f"Expected unsigned {schema.length * 8}-bit integer: {ref.field.key}")
        elif schema.value_type == "string":
            if type(value) is not str:
                raise _FactError(f"Expected string: {ref.field.key}")
        else:
            raise _FactError(f"Bytes normalization is unsupported: {ref.field.key}")
        if ref.field.bit is not None:
            value = (value >> ref.field.bit) & 1
        return True, value
    observations.append(Observation(reference=ref, found=found, value=value))
    return found, value


def _condition(node, context, actual, fields, observations, *, resolving=False):
    if node is None:
        return "TRUE"
    if node.op in {"AND", "OR", "NOT"}:
        states = [_condition(c, context, actual, fields, observations, resolving=resolving)
                  for c in node.children]
        # Invalid input is never hidden by Boolean short-circuiting.
        if "ERROR" in states:
            return "ERROR"
        if node.op == "NOT":
            return {"TRUE": "FALSE", "FALSE": "TRUE"}.get(states[0], states[0])
        decisive = "FALSE" if node.op == "AND" else "TRUE"
        if decisive in states:
            return decisive
        if "UNKNOWN" in states:
            return "UNKNOWN"
        if "DEFERRED" in states:
            return "DEFERRED"
        return "TRUE" if node.op == "AND" else "FALSE"
    try:
        if resolving and node.ref.source == "actual":
            _registration(node.ref.field, fields)
            return "DEFERRED"
        found, value = _read(node.ref, context, actual, fields, observations)
        if not found:
            return "UNKNOWN"
        if node.op == "EQ":
            if type(value) is not type(node.value):
                raise _FactError("Condition equality operands must have the same type")
            passed = value == node.value
        elif node.op=='GE':
            if type(value) is not int or type(node.value) is not int:
                raise _FactError('GE condition requires integer operands without coercion')
            passed=value>=node.value
        else:
            if type(value) is not int or value < 0:
                raise _FactError("Bit condition requires an unsigned integer")
            if node.ref.source == "actual":
                schema = fields[node.ref.field.field_id].schema_definition
                width = 1 if node.ref.field.bit is not None else schema.length * 8
                if node.bit >= width:
                    raise _FactError("Condition bit is outside field width")
            passed = bool(value & (1 << node.bit)) == (node.op == "BIT_SET")
        return "TRUE" if passed else "FALSE"
    except _FactError:
        return "ERROR"


def _condition_refs(node):
    if node is None:
        return
    if node.ref is not None:
        yield node
    for child in node.children:
        yield from _condition_refs(child)


def _validate_rule(rule, fields, *, experimental=False):
    evidence = [rule.provenance, *rule.supporting_evidence]
    if rule.override and rule.override.enabled:
        evidence.append(rule.override.provenance)
    for item in evidence:
        if item.status == KnowledgeStatus.CONFIRMED:
            if item.verified_by is None or item.verified_date is None:
                raise _FactError("Confirmed evidence requires reviewer and review date")
            if item.source_type != "fixture" and not experimental:
                raise _FactError("Pilot authoritative evidence must be TEST/FIXTURE")
    target = _registration(rule.target, fields)
    schema = target.schema_definition
    for leaf in _condition_refs(rule.condition):
        if leaf.ref.source == "actual":
            registration = _registration(leaf.ref.field, fields)
            width = 1 if leaf.ref.field.bit is not None else registration.schema_definition.length * 8
            if leaf.op=='GE' and registration.schema_definition.value_type not in {'integer','bitmask'}:
                raise _FactError('GE condition requires a numeric field')
            if leaf.op in {'BIT_SET','BIT_CLEAR'} and (registration.schema_definition.value_type not in {"integer", "bitmask"}
                                     or leaf.bit >= width):
                raise _FactError("Invalid condition bit operand")
    check = rule.check
    if isinstance(check, FieldCompare):
        other = _registration(check.other, fields)
        if schema.value_type not in {"integer", "bitmask"} or other.schema_definition.value_type not in {"integer", "bitmask"}:
            raise _FactError("Field comparisons require numeric fields")
        return
    kind = check.type
    if kind not in {"EXACT", "MIN", "MAX", "RANGE", "ENUM", "BIT_SET", "BIT_CLEAR", "MASK"}:
        raise _FactError(f"Unsupported executable check: {kind}")
    numeric = schema.value_type in {"integer", "bitmask"}
    width = 1 if rule.target.bit is not None else schema.length * 8
    values = ([check.value] if kind in {"EXACT", "MIN", "MAX", "MASK"} else
              list(check.values) if kind == "ENUM" else [check.min, check.max] if kind == "RANGE" else [])
    if kind in {"BIT_SET", "BIT_CLEAR"}:
        bit = check.bit if check.bit is not None else rule.target.bit
        if schema.value_type != "bitmask" or bit is None or bit >= schema.length * 8:
            raise _FactError("Invalid bit check")
        if rule.target.bit is not None and check.bit is not None and rule.target.bit != check.bit:
            raise _FactError("Target bit and check bit disagree")
    if kind == "MASK" and (not numeric or check.mask >= 1 << width):
        raise _FactError("Invalid mask width/type")
    if kind in {"MIN", "MAX", "RANGE"} and not numeric:
        raise _FactError("Bounds require a numeric field")
    for value in values:
        if numeric and (type(value) is not int or not 0 <= value < 1 << width):
            raise _FactError("Check value is outside numeric field type/width")
        if not numeric and (schema.value_type != "string" or type(value) is not str):
            raise _FactError("Unsupported check value type")


def _authority(rule, fields):
    evidence = [rule.provenance, *rule.supporting_evidence]
    refs = [rule.target]
    if isinstance(rule.check, FieldCompare):
        refs.append(rule.check.other)
    refs.extend(leaf.ref.field for leaf in _condition_refs(rule.condition) if leaf.ref.source == "actual")
    evidence.extend(fields[ref.field_id].provenance for ref in refs)
    return all(e.status == KnowledgeStatus.CONFIRMED for e in evidence)


def _legacy_rule(item):
    rule = item.rule
    leaves = [Condition(op="EQ", ref=FactRef(source="context", path=k), value=v)
              for conditions in (rule.applies_when, rule.applicable_when) for k, v in sorted(conditions.items())]
    return RuntimeRule(rule_id=rule.rule_id,
                       target=FieldRef(field_id=rule.target.field_id, bit=rule.target.bit),
                       check=rule.check, condition=Condition(op="AND", children=tuple(leaves)) if leaves else None,
                       provenance=rule.provenance or item.history[-1].provenance,
                       history=item.history, override=rule.override, origin="snapshot")


def _schema_rules(fields):
    for registration in fields.values():
        schema = registration.schema_definition
        if schema.lifecycle != "active":
            continue
        for bit, validation in [(None, schema.validation), *[(b.bit, b.validation) for b in schema.bits if b.lifecycle == "active"]]:
            if validation is None:
                continue
            target = schema.field_id if bit is None else f"{schema.field_id}[{bit}]"
            history = tuple(h for h in registration.history if h.target in {schema.field_id, target})
            evidence = history[-1].provenance if history else registration.provenance
            for index in range(registration.array_count or 1):
                yield RuntimeRule(rule_id=f"SCHEMA.VALIDATION.{schema.field_id}.{bit if bit is not None else 'FIELD'}.{index}",
                                  target=FieldRef(field_id=schema.field_id, bit=bit,
                                                  index=index if registration.array_count else None),
                                  check=ExactCheck(type="EXACT", value=0), provenance=evidence,
                                  history=history, origin="schema")


def _expand(rule, capabilities):
    if rule.check.type != "CAPABILITY":
        return [rule]
    matches = sorted((m for m in capabilities if m.capability_id == rule.check.capability_id), key=lambda m: m.target.key)
    if not matches or rule.override is not None:
        return [rule]  # Unsupported/absent mapping is reported as ERROR, never guessed.
    return [RuntimeRule(rule_id=f"{rule.rule_id}.MAP.{i}", target=m.target,
                        check=ExactCheck(type="EXACT", value=m.supported if rule.check.support == "supported" else m.unsupported),
                        condition=rule.condition, modality=rule.modality, provenance=rule.provenance,
                        supporting_evidence=(*rule.supporting_evidence, m.provenance), history=rule.history,
                        origin="mapping", origin_rule_id=rule.rule_id) for i, m in enumerate(matches)]


def _override_errors(rules):
    by_id = {r.rule_id: r for r in rules}
    errors = {}
    for rule in rules:
        override = rule.override
        if override is None or not override.enabled:
            continue
        if override.provenance.status != KnowledgeStatus.CONFIRMED or rule.provenance.status != KnowledgeStatus.CONFIRMED:
            errors[rule.rule_id] = "Override needs confirmed rule and override evidence"
        for identity in override.overrides:
            other = by_id.get(identity)
            if other is None or identity == rule.rule_id:
                errors[rule.rule_id] = "Override target is absent or self-referencing"
            elif (other.target.field_id, other.target.index) != (rule.target.field_id, rule.target.index):
                errors[rule.rule_id] = "Override must target the same field instance"
            elif other.origin == "schema":
                errors[rule.rule_id] = "Schema validation cannot be overridden"
            elif other.override and other.override.enabled:
                errors[rule.rule_id] = "Override chains/cycles are unsupported"
                errors[other.rule_id] = "Override chains/cycles are unsupported"
    return errors


def _active_sets(entries, fields):
    """Resolve overrides only among authoritative, applicable, valid rules."""
    active = [e.rule for e in entries if e.state == "READY"]
    excluded = defaultdict(list)
    for rule in active:
        if rule.override and rule.override.enabled:
            for identity in rule.override.overrides:
                excluded[identity].append(rule.rule_id)
    groups = defaultdict(list)
    for rule in active:
        if rule.rule_id not in excluded and not isinstance(rule.check, FieldCompare):
            groups[(rule.target.field_id, rule.target.index)].append(rule)
    conflicts = {}
    for (field_id, _), group in groups.items():
        legacy = []
        for rule in group:
            check = rule.check
            # MASK on a decoded bit is relative to that bit, whereas Builder MASK
            # operates on a whole field. Convert to a bit EXACT (mask=0 is tautology).
            if check.type == "MASK" and rule.target.bit is not None:
                if check.mask == 0:
                    continue
                check = ExactCheck(type="EXACT", value=check.value)
            legacy.append(RequirementRule(rule_id=rule.rule_id,
                                          target=TargetRef(command=fields[field_id].schema_definition.command,
                                                           field_id=field_id, bit=rule.target.bit),
                                          check=check, provenance=rule.provenance))
        schema = fields[field_id].schema_definition
        # Numeric normalization is unsigned/width bounded, including integer fields.
        if schema.value_type == "integer":
            schema = schema.model_copy(update={"value_type": "bitmask"})
        if not literal_constraints_compatible(legacy, schema):
            identities = tuple(sorted(r.rule_id for r in group))
            conflicts.update({r.rule_id: identities for r in group})
    return excluded, conflicts


def resolve(context: RuntimeContext, snapshots: tuple[EffectiveSnapshot, ...], mappings: PilotMappings) -> EffectiveExpectedProfile:
    """Resolve an explicit fixture Bundle, preserving Actual-dependent constraints."""
    if context.bundle_id != mappings.bundle.bundle_id:
        raise KnowledgeError("BUNDLE_MISMATCH", context.bundle_id)
    by_key = {s.spec.key: s for s in snapshots}
    if len(by_key) != len(snapshots) or set(by_key) != set(mappings.bundle.snapshot_keys):
        raise KnowledgeError("SNAPSHOT_SELECTION", "Supply exactly the explicitly selected snapshots")
    experimental = mappings.execution_mode == 'experimental'
    if any(s.data_kind != "fixture" for s in snapshots) and not experimental:
        raise KnowledgeError("PILOT_FIXTURE_ONLY", "Production snapshot execution is not enabled")
    if len({s.data_kind for s in snapshots}) != 1:
        raise KnowledgeError('MIXED_DATA_KIND', 'Do not mix fixture and production snapshots')
    if any(s.schema_ref is not None and s.schema_ref.key not in by_key for s in snapshots):
        raise KnowledgeError("SCHEMA_SELECTION", "Select each layer's explicit schema reference")
    fields = {f.schema_definition.field_id: f for f in mappings.fields}
    snapshot_fields = {f.schema.field_id for s in snapshots for f in s.fields}
    if set(fields) != snapshot_fields:
        raise KnowledgeError("REGISTRY_SELECTION", "Register exactly the selected snapshot fields")
    rules = list(mappings.rules)
    for snapshot in sorted(snapshots, key=lambda s: s.spec.key):
        for item in snapshot.fields:
            field_id = item.schema.field_id
            if field_id not in fields or fields[field_id].schema_definition != item.schema:
                raise KnowledgeError("REGISTRY_MISMATCH", field_id)
            if fields[field_id].history != item.history:
                raise KnowledgeError("REGISTRY_LINEAGE", field_id)
            history = [h for h in item.history if h.target == field_id]
            evidence = history[-1].provenance if history else item.history[-1].provenance
            if fields[field_id].provenance != evidence:
                raise KnowledgeError("REGISTRY_EVIDENCE", field_id)
        rules.extend(_legacy_rule(r) for r in snapshot.rules)
    rules.extend(_schema_rules(fields))
    rules = [expanded for rule in rules for expanded in _expand(rule, mappings.capabilities)]
    if len({r.rule_id for r in rules}) != len(rules):
        raise KnowledgeError("DUPLICATE_RUNTIME_RULE", "Rule IDs must be unique across selected layers")
    override_errors = _override_errors(rules)
    entries = []
    for rule in sorted(rules, key=lambda r: r.rule_id):
        observations = []
        try:
            _validate_rule(rule, fields, experimental=experimental)
            if rule.rule_id in override_errors:
                raise _FactError(override_errors[rule.rule_id])
            state = _condition(rule.condition, context, {}, fields, observations, resolving=True)
            evidence = [rule.provenance, *rule.supporting_evidence]
            refs = [rule.target]
            if isinstance(rule.check, FieldCompare):
                refs.append(rule.check.other)
            refs.extend(leaf.ref.field for leaf in _condition_refs(rule.condition) if leaf.ref.source == 'actual')
            evidence.extend(fields[ref.field_id].provenance for ref in refs)
            exploratory = experimental and all(e.status in {KnowledgeStatus.CANDIDATE, KnowledgeStatus.PROVISIONAL,
                                                            KnowledgeStatus.CONFIRMED} for e in evidence)
            if (not _authority(rule, fields) and not exploratory) or rule.modality != "mandatory":
                result, reason = "REVIEW", "Unconfirmed evidence or non-mandatory/behavioral statement"
            else:
                result = {"TRUE": "READY", "FALSE": "N/A", "UNKNOWN": "UNKNOWN", "DEFERRED": "CONDITIONAL", "ERROR": "ERROR"}[state]
                reason = {"READY": "Applicable constraint", "N/A": "Condition is false", "UNKNOWN": "Context dependency missing",
                          "CONDITIONAL": "Actual dependency deferred", "ERROR": "Invalid condition operand"}[result]
        except _FactError as error:
            result, state, reason = "ERROR", "ERROR", str(error)
        entries.append(ExpectedEntry(rule=rule, state=result, reason=reason, condition_state=state, observations=tuple(observations)))
    excluded, conflicts = _active_sets(entries, fields)
    entries = [e.model_copy(update={"state": "N/A", "reason": "Explicit override: " + ", ".join(sorted(excluded[e.rule.rule_id]))})
               if e.rule.rule_id in excluded else
               e.model_copy(update={"state": "CONFLICT", "reason": "Incompatible active literal constraints: " + ", ".join(conflicts[e.rule.rule_id])})
               if e.rule.rule_id in conflicts else e for e in entries]
    return EffectiveExpectedProfile(bundle=mappings.bundle, context=context, execution_mode=mappings.execution_mode,
                                    data_kind=snapshots[0].data_kind,
                                    fields=tuple(fields[k] for k in sorted(fields)), entries=tuple(entries),
                                    input_source=mappings.input_source)


def _check(rule, value, context, actual, fields, observations):
    check = rule.check
    if isinstance(check, FieldCompare):
        found, other = _read(FactRef(source="actual", field=check.other), context, actual, fields, observations)
        if not found:
            return None
        return {"=": eq, "!=": ne, "<": lt, "<=": le, ">": gt, ">=": ge}[check.operator](value, other)
    if check.type == "EXACT":
        return type(value) is type(check.value) and value == check.value
    if check.type == "MIN":
        return value >= check.value
    if check.type == "MAX":
        return value <= check.value
    if check.type == "RANGE":
        return check.min <= value <= check.max
    if check.type == "ENUM":
        return any(type(value) is type(v) and value == v for v in check.values)
    if check.type == "MASK":
        return value & check.mask == check.value
    bit = check.bit if check.bit is not None else rule.target.bit
    # A target bit was already decoded by _read.
    selected = bool(value) if rule.target.bit is not None else bool(value & (1 << bit))
    return selected == (check.type == "BIT_SET")


def evaluate(expected_profile: EffectiveExpectedProfile, actual_facts: tuple[ActualFact, ...]) -> ValidationReport:
    """Evaluate saved normalized facts. No device commands or knowledge promotion."""
    actual = {}
    for fact in actual_facts:
        key = (fact.field.field_id, fact.field.index)
        if key in actual:
            raise KnowledgeError("DUPLICATE_ACTUAL_FACT", fact.field.key)
        actual[key] = fact.value
    fields = {f.schema_definition.field_id: f for f in expected_profile.fields}
    input_errors = []
    for fact in sorted(actual_facts, key=lambda f: f.field.key):
        try:
            _read(FactRef(source="actual", field=fact.field), expected_profile.context, actual, fields, [])
        except _FactError as error:
            input_errors.append(InputError(field=fact.field, value=fact.value, reason=str(error)))
    entries = []
    results = {}
    for entry in expected_profile.entries:
        observations = []
        rule = entry.rule
        # Recompute authoritative applicability: previously overridden/conflicting
        # rules must remain present for Actual-dependent override/conflict decisions.
        if entry.state in {"REVIEW", "ERROR"}:
            results[rule.rule_id] = RuleResult(rule=rule, status=entry.state, reason=entry.reason,
                                              condition_state=entry.condition_state, observations=entry.observations)
            continue
        state = _condition(rule.condition, expected_profile.context, actual, fields, observations)
        result_state = {"TRUE": "READY", "FALSE": "N/A", "UNKNOWN": "UNKNOWN", "ERROR": "ERROR"}[state]
        entries.append(ExpectedEntry(rule=rule, state=result_state, reason=f"Condition: {state}",
                                     condition_state=state, observations=tuple(observations)))
    excluded, conflicts = _active_sets(entries, fields)
    for entry in entries:
        rule = entry.rule
        observations = list(entry.observations)
        related = ()
        if entry.state != "READY":
            status, reason = entry.state, entry.reason
        elif rule.rule_id in excluded:
            status, reason = "N/A", "Explicit override"
            related = tuple(sorted(excluded[rule.rule_id]))
        elif rule.rule_id in conflicts:
            status, reason = "CONFLICT", "Incompatible active literal constraints"
            related = conflicts[rule.rule_id]
        else:
            try:
                found, value = _read(FactRef(source="actual", field=rule.target), expected_profile.context, actual, fields, observations)
                passed = _check(rule, value, expected_profile.context, actual, fields, observations) if found else None
                status = "UNKNOWN" if passed is None else "PASS" if passed else "FAIL"
                reason = "Required Actual field missing" if passed is None else "Constraint satisfied" if passed else "Constraint violated"
            except _FactError as error:
                status, reason = "ERROR", str(error)
        results[rule.rule_id] = RuleResult(rule=rule, status=status, reason=reason,
                                          condition_state=entry.condition_state, observations=tuple(observations), related_rules=related)
    ordered = tuple(results[k] for k in sorted(results))
    statuses = {r.status for r in ordered}
    overall = "ERROR" if input_errors else next((s for s in ("ERROR", "CONFLICT", "FAIL", "UNKNOWN", "REVIEW", "PASS") if s in statuses), "N/A")
    return ValidationReport(kind='experimental_validation_report' if expected_profile.execution_mode == 'experimental'
                            else 'fixture_validation_report', profile=expected_profile, status=overall, results=ordered, input_errors=tuple(input_errors),
                            actual_facts=tuple(sorted(actual_facts, key=lambda f: f.field.key)))
