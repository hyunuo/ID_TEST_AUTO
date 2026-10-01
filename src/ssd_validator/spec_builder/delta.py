"""Guarded, non-mutating changes. Guards always examine the unmodified parent."""

from copy import deepcopy

from pydantic import ValidationError

from ssd_validator.errors import KnowledgeError
from ssd_validator.knowledge.yaml_loader import LoadedSource, validation_message
from ssd_validator.models.effective import EffectiveField, EffectiveRule, EffectiveSnapshot
from ssd_validator.models.provenance import ChangeRecord
from ssd_validator.models.rules import RequirementRule
from ssd_validator.models.schema import BitSchema, FieldSchema
from ssd_validator.models.specs import DeltaAction, DeltaSpec


def match_guard(previous: dict, actual: dict, path: str) -> None:
    """A nonempty object guard matches specified keys; arrays and scalars match exactly."""
    for key, expected in previous.items():
        location = f"{path}.{key}"
        if key not in actual:
            raise KnowledgeError("GUARD_MISMATCH", f"{location}: parent has no such property")
        value = actual[key]
        if isinstance(expected, dict) and expected:
            if not isinstance(value, dict):
                raise KnowledgeError("GUARD_MISMATCH", f"{location}: expected an object")
            match_guard(expected, value, location)
        elif type(expected) is not type(value) or expected != value:
            raise KnowledgeError("GUARD_MISMATCH", f"{location}: expected {expected!r}, parent has {value!r}")


def merge_patch(actual: dict, current: dict) -> dict:
    result = deepcopy(actual)
    for key, value in current.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge_patch(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def change_record(source: LoadedSource, target: str, action: str, provenance=None) -> ChangeRecord:
    document = source.document
    return ChangeRecord(
        action=action, spec=document.spec, target=target,
        provenance=provenance or document.provenance,
        source_file=source.path, source_hash=source.sha256,
    )


def _schema_payload(field: EffectiveField | None, target) -> dict | None:
    if field is None:
        return None
    if target.command is not None and target.command != field.schema.command:
        raise KnowledgeError("TARGET_COMMAND", f"Command mismatch for {target.key}")
    if target.bit is None:
        return field.schema.model_dump(mode="json")
    for bit in field.schema.bits:
        if bit.bit == target.bit:
            return bit.model_dump(mode="json")
    return None


def _check_existence(action: DeltaAction, previous, actual, target: str) -> None:
    if action == DeltaAction.ADD:
        if actual is not None:
            raise KnowledgeError("DUPLICATE_TARGET", f"ADD target already exists: {target}")
    else:
        if actual is None:
            raise KnowledgeError("MISSING_TARGET", f"{action} target does not exist: {target}")
        match_guard(previous, actual, target)


def apply_delta(parent: EffectiveSnapshot, source: LoadedSource) -> EffectiveSnapshot:
    delta = source.document
    if not isinstance(delta, DeltaSpec):
        raise KnowledgeError("NOT_DELTA", "Expected a delta document")
    if parent.spec.spec_family != delta.spec_family or parent.spec.version != delta.inherits:
        raise KnowledgeError("WRONG_PARENT", f"{delta.spec.key} cannot inherit {parent.spec.key}")
    if parent.data_kind != delta.data_kind:
        raise KnowledgeError("DATA_KIND_MISMATCH", "Cannot mix fixture and production in inheritance")
    fields = {field.schema.field_id: field for field in parent.fields}
    rules = {rule.rule.rule_id: rule for rule in parent.rules}
    # Validate every guard against the same parent before making any change.
    for change in delta.schema_changes:
        if change.target.bit is not None and change.target.field_id not in fields:
            raise KnowledgeError("MISSING_TARGET", f"Bit owner missing: {change.target.field_id}")
        _check_existence(change.action, change.previous,
                         _schema_payload(fields.get(change.target.field_id), change.target), change.target.key)
    for change in delta.changes:
        previous = rules.get(change.rule_id)
        _check_existence(change.action, change.previous,
                         previous.rule.model_dump(mode="json") if previous else None, change.rule_id)

    events = []
    try:
        for change in sorted(delta.schema_changes, key=lambda change: change.target.key):
            target = change.target
            old = fields.get(target.field_id)
            event = change_record(source, target.key, change.action.value, change.provenance)
            events.append(event)
            if target.bit is None:
                if change.action == DeltaAction.REMOVE:
                    del fields[target.field_id]
                    continue
                payload = change.current if change.action in {DeltaAction.ADD, DeltaAction.REDEFINE} else merge_patch(
                    old.schema.model_dump(mode="json"), change.current)
                schema = FieldSchema.model_validate(payload)
                if schema.field_id != target.field_id or (target.command and schema.command != target.command):
                    raise KnowledgeError("TARGET_IDENTITY", f"Current field identity differs from {target.key}")
            else:
                payload = old.schema.model_dump(mode="json")
                bits = {bit.bit: bit.model_dump(mode="json") for bit in old.schema.bits}
                if change.action == DeltaAction.REMOVE:
                    del bits[target.bit]
                else:
                    current = change.current if change.action in {DeltaAction.ADD, DeltaAction.REDEFINE} else merge_patch(
                        bits[target.bit], change.current)
                    bit = BitSchema.model_validate({"bit": target.bit, **current})
                    if bit.bit != target.bit:
                        raise KnowledgeError("TARGET_IDENTITY", f"Current bit differs from {target.key}")
                    bits[target.bit] = bit.model_dump(mode="json")
                payload["bits"] = [bits[bit] for bit in sorted(bits)]
                schema = FieldSchema.model_validate(payload)
            fields[target.field_id] = EffectiveField(
                schema=schema, introduced_in=old.introduced_in if old else delta.spec,
                last_changed_in=delta.spec, history=(*old.history, event) if old else (event,),
            )
        for change in sorted(delta.changes, key=lambda change: change.rule_id):
            old = rules.get(change.rule_id)
            event = change_record(source, change.rule_id, change.action.value, change.provenance)
            events.append(event)
            if change.action == DeltaAction.REMOVE:
                del rules[change.rule_id]
                continue
            payload = change.current if change.action in {DeltaAction.ADD, DeltaAction.REDEFINE} else merge_patch(
                old.rule.model_dump(mode="json"), change.current)
            # New source evidence is explicit, never guessed from rule order.
            payload = deepcopy(payload)
            if "provenance" not in (change.current or {}) or payload.get("provenance") is None:
                payload["provenance"] = event.provenance.model_dump(mode="json")
            rule = RequirementRule.model_validate(payload)
            if rule.rule_id != change.rule_id:
                raise KnowledgeError("TARGET_IDENTITY", f"Current rule identity differs from {change.rule_id}")
            rules[change.rule_id] = EffectiveRule(
                rule=rule, introduced_in=old.introduced_in if old else delta.spec,
                last_changed_in=delta.spec, history=(*old.history, event) if old else (event,),
            )
    except ValidationError as error:
        raise KnowledgeError("DELTA_MODEL_ERROR", validation_message(error), source=source.path) from error
    return EffectiveSnapshot(
        spec=delta.spec, data_kind=delta.data_kind, parent=parent.spec, schema_ref=parent.schema_ref,
        fields=tuple(fields[key] for key in sorted(fields)), rules=tuple(rules[key] for key in sorted(rules)),
        changes=(*parent.changes, *events),
    )
