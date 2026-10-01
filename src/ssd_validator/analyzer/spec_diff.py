"""Structural schema/requirement diffs with evidence for each affected target."""

from typing import Literal

from pydantic import JsonValue

from ssd_validator.errors import KnowledgeError
from ssd_validator.models.common import DomainModel, Text
from ssd_validator.models.identifiers import SpecVersion
from ssd_validator.models.provenance import ChangeRecord


class DiffEntry(DomainModel):
    category: Literal["schema", "requirement", "provenance"]
    action: Literal["added", "removed", "modified"]
    target: Text
    property: Text
    previous: JsonValue
    current: JsonValue
    previous_provenance: tuple[ChangeRecord, ...]
    current_provenance: tuple[ChangeRecord, ...]


class SpecDiff(DomainModel):
    from_spec: SpecVersion
    to_spec: SpecVersion
    changes: tuple[DiffEntry, ...]


def _entities(snapshot):
    items = {}
    for item in snapshot.fields:
        payload = item.schema.model_dump(mode="json")
        bits = payload.pop("bits")
        items[("schema", item.schema.field_id)] = (payload, item.history)
        for bit in bits:
            target = f"{item.schema.field_id}[{bit['bit']}]"
            history = tuple(record for record in item.history if record.target in {target, item.schema.field_id})
            items[("schema", target)] = (bit, history)
    for item in snapshot.rules:
        payload = item.rule.model_dump(mode="json")
        payload.pop("provenance")
        payload["status"] = item.rule.provenance.status.value
        items[("requirement", item.rule.rule_id)] = (payload, item.history)
    return items


def _properties(old, new, prefix=""):
    for key in sorted(set(old) | set(new)):
        path = f"{prefix}.{key}" if prefix else key
        if key not in old:
            yield "added", path, None, new[key]
        elif key not in new:
            yield "removed", path, old[key], None
        elif isinstance(old[key], dict) and isinstance(new[key], dict):
            yield from _properties(old[key], new[key], path)
        elif type(old[key]) is not type(new[key]) or old[key] != new[key]:
            yield "modified", path, old[key], new[key]


def diff_snapshots(old, new) -> SpecDiff:
    if old.spec.spec_family != new.spec.spec_family:
        raise KnowledgeError("DIFF_FAMILY_MISMATCH", "Snapshots must belong to the same spec family")
    before, after, changes = _entities(old), _entities(new), []
    for identity in sorted(set(before) | set(after)):
        category, target = identity
        left, left_history = before.get(identity, ({}, ()))
        right, right_history = after.get(identity, ({}, ()))
        if identity not in after:
            owner = target.split("[")[0]
            right_history = tuple(record for record in new.changes if record.target in {target, owner})
        if identity not in before:
            differences = [("added", "<entity>", None, right)]
        elif identity not in after:
            differences = [("removed", "<entity>", left, None)]
        else:
            differences = list(_properties(left, right))
        for action, path, previous, current in differences:
            changes.append(DiffEntry(
                category=category, action=action, target=target, property=path,
                previous=previous, current=current,
                previous_provenance=left_history, current_provenance=right_history,
            ))
        if not differences and left_history != right_history:
            changes.append(DiffEntry(
                category="provenance", action="modified", target=target, property="history",
                previous=[item.model_dump(mode="json") for item in left_history],
                current=[item.model_dump(mode="json") for item in right_history],
                previous_provenance=left_history, current_provenance=right_history,
            ))
    return SpecDiff(from_spec=old.spec, to_spec=new.spec, changes=tuple(changes))
