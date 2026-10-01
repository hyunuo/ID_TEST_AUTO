"""Required Phase 1 base/delta, guard, inheritance and lineage tests."""

from copy import deepcopy
from dataclasses import replace

import pytest

from conftest import build_from, edit_yaml
from ssd_validator.errors import KnowledgeError
from ssd_validator.models.specs import DeltaSpec
from ssd_validator.spec_builder.builder import build_knowledge
from ssd_validator.spec_builder.delta import apply_delta, match_guard
from ssd_validator.storage.serialization import canonical_bytes


def fields(snapshot):
    return {item.schema.field_id: item for item in snapshot.fields}


def bits(snapshot):
    return {item.bit: item for item in fields(snapshot)["TEST.ID_CTRL.FLAGS"].schema.bits}


def test_base_spec_build(built):
    base = built.get("TEST", "fixture-v1")
    assert base.parent is None
    assert len(base.fields) == 4
    assert base.rules[0].rule.check.value == 2
    assert all(item.introduced_in == base.spec for item in base.fields)


def test_add_delta(built):
    old, new = built.get("TEST", "fixture-v1"), built.get("TEST", "fixture-v2")
    assert "TEST.ID_CTRL.ADDED" not in fields(old)
    assert fields(new)["TEST.ID_CTRL.ADDED"].schema.name == "TEST_ADDED"
    assert 2 not in bits(old) and bits(new)[2].state == "reserved"
    assert any(item.rule.rule_id == "TEST.BASE.ADDED" for item in new.rules)


def test_modify_delta(built):
    old, new = built.get("TEST", "fixture-v2"), built.get("TEST", "fixture-v3")
    assert fields(old)["TEST.ID_CTRL.COUNT"].schema.offset == 1
    assert fields(new)["TEST.ID_CTRL.COUNT"].schema.offset == 4
    assert next(item.rule for item in new.rules if item.rule.rule_id == "TEST.BASE.COUNT").check.value == 5


def test_remove_delta_preserves_history(built):
    old, new = built.get("TEST", "fixture-v3"), built.get("TEST", "fixture-v4")
    assert "TEST.ID_CTRL.OBSOLETE" in fields(old)
    assert "TEST.ID_CTRL.OBSOLETE" not in fields(new)
    assert any(record.action == "REMOVE" and record.target == "TEST.ID_CTRL.OBSOLETE" for record in new.changes)


def test_reserved_to_defined(built):
    assert bits(built.get("TEST", "fixture-v2"))[1].state == "reserved"
    changed = bits(built.get("TEST", "fixture-v3"))[1]
    assert changed.state == "defined"
    assert changed.feature == "TEST.FEATURE_BETA"
    assert changed.validation is None


def test_defined_to_reserved(built):
    assert bits(built.get("TEST", "fixture-v3"))[0].state == "defined"
    changed = bits(built.get("TEST", "fixture-v4"))[0]
    assert changed.state == "reserved" and changed.feature is None
    assert changed.validation.behavior == "must_be_zero"


def test_previous_guard_mismatch_fails(editable_knowledge):
    edit_yaml(editable_knowledge, "schema/modify.yaml", lambda d: d["schema_changes"][0]["previous"].update(state="defined"))
    with pytest.raises(KnowledgeError, match="GUARD_MISMATCH") as error:
        build_from(editable_knowledge)
    assert "schema/modify.yaml" in str(error.value)


def test_missing_parent_fails(editable_knowledge):
    edit_yaml(editable_knowledge, "schema/add.yaml", lambda d: d.update(inherits="TEST_MISSING_VERSION"))
    with pytest.raises(KnowledgeError, match="MISSING_PARENT"):
        build_from(editable_knowledge)


def test_circular_inheritance_fails(editable_knowledge):
    edit_yaml(editable_knowledge, "schema/add.yaml", lambda d: d.update(inherits="fixture-v3"))
    with pytest.raises(KnowledgeError, match="CIRCULAR_INHERITANCE"):
        build_from(editable_knowledge)


def test_full_snapshot_generation(built):
    assert len(built.snapshots) == 7
    final = built.get("TEST", "fixture-v4")
    assert "TEST.ID_NS.DUMMY_SIZE" in fields(final)
    assert len(final.fields) == 4
    assert len(final.rules) == 2
    assert len(built.manifest.snapshots) == 7


def test_provenance_preservation(built):
    final = fields(built.get("TEST", "fixture-v4"))["TEST.ID_CTRL.FLAGS"]
    assert final.introduced_in.version == "fixture-v1"
    assert final.last_changed_in.version == "fixture-v4"
    assert [record.spec.version for record in final.history] == ["fixture-v1", "fixture-v2", "fixture-v3", "fixture-v4"]
    assert [record.provenance.source_section for record in final.history] == ["TEST_BASE", "TEST_ADD", "TEST_MODIFY", "TEST_REMOVE"]
    assert all(record.source_file and len(record.source_hash) == 64 for record in final.history)
    assert final.history[0].provenance.status == "candidate"


def test_deterministic_build_output(sources, built):
    reverse = build_knowledge(tuple(reversed(sources)), git_commit="TEST_FIXTURE_COMMIT")
    assert canonical_bytes(reverse.manifest) == canonical_bytes(built.manifest)
    assert [canonical_bytes(item) for item in reverse.snapshots] == [canonical_bytes(item) for item in built.snapshots]


def test_parent_and_source_are_not_mutated(sources, built):
    parent = built.get("TEST", "fixture-v2")
    delta = next(source for source in sources if source.path == "schema/modify.yaml")
    before_parent = canonical_bytes(parent)
    before_source = delta.document.model_dump(mode="json")
    apply_delta(parent, delta)
    assert canonical_bytes(parent) == before_parent
    assert delta.document.model_dump(mode="json") == before_source


def test_requirement_change_and_deprecate(built):
    final = built.get("TEST", "fixture-v4")
    rules = {entry.rule.rule_id: entry.rule for entry in final.rules}
    assert rules["TEST.BASE.COUNT"].requirement == "required"
    assert rules["TEST.BASE.ADDED"].provenance.status == "deprecated"
    assert fields(final)["TEST.ID_CTRL.ADDED"].schema.lifecycle == "deprecated"
    assert built.get("OCP", "fixture-v2").rules[0].rule.requirement == "required"


def test_redefine_is_full_replacement(sources, built):
    source = next(source for source in sources if source.path == "schema/modify.yaml")
    payload = source.document.model_dump(mode="json")
    replacement = fields(built.get("TEST", "fixture-v2"))["TEST.ID_CTRL.COUNT"].schema.model_dump(mode="json")
    replacement["name"] = "TEST_REDEFINED"
    payload["schema_changes"] = [{"action": "REDEFINE", "target": {"field_id": replacement["field_id"]},
                                  "previous": {"name": "TEST_COUNT"}, "current": replacement}]
    payload["changes"] = []
    delta = replace(source, document=DeltaSpec.model_validate(payload))
    result = apply_delta(built.get("TEST", "fixture-v2"), delta)
    assert fields(result)["TEST.ID_CTRL.COUNT"].schema.name == "TEST_REDEFINED"
    payload["schema_changes"][0]["current"] = {"name": "TEST_INCOMPLETE"}
    with pytest.raises(KnowledgeError, match="DELTA_MODEL_ERROR"):
        apply_delta(built.get("TEST", "fixture-v2"), replace(source, document=DeltaSpec.model_validate(payload)))


@pytest.mark.parametrize("mutate,code", [
    (lambda d: d["schema_changes"][0]["target"].update(field_id="TEST.ID_CTRL.UNKNOWN"), "MISSING_TARGET"),
    (lambda d: d["schema_changes"][1]["current"].update(field_id="TEST.RENAMED"), "TARGET_IDENTITY"),
    (lambda d: d["schema_changes"][0]["target"].update(command="id-ns"), "TARGET_COMMAND"),
])
def test_bad_delta_targets(editable_knowledge, mutate, code):
    edit_yaml(editable_knowledge, "schema/modify.yaml", mutate)
    with pytest.raises(KnowledgeError, match=code):
        build_from(editable_knowledge)


def test_guard_compares_types_and_nested_properties():
    match_guard({"check": {"value": 2}}, {"check": {"type": "EXACT", "value": 2}}, "TEST")
    with pytest.raises(KnowledgeError, match="GUARD_MISMATCH"):
        match_guard({"value": True}, {"value": 1}, "TEST")
    with pytest.raises(KnowledgeError, match="GUARD_MISMATCH"):
        match_guard({"unknown": None}, {}, "TEST")


def test_source_hash_changes_when_source_changes(editable_knowledge, built):
    with (editable_knowledge / "catalog.yaml").open("a") as stream:
        stream.write("\n# TEST fixture comment change\n")
    assert build_from(editable_knowledge).manifest.knowledge_hash != built.manifest.knowledge_hash


def test_bit_remove_preserves_diff_evidence(editable_knowledge):
    from ssd_validator.analyzer.spec_diff import diff_snapshots

    edit_yaml(editable_knowledge, "schema/modify.yaml", lambda d: d["schema_changes"].append(
        {"action": "REMOVE", "target": {"field_id": "TEST.ID_CTRL.FLAGS", "bit": 2}, "previous": {"state": "reserved"}}))
    result = build_from(editable_knowledge)
    assert 2 not in bits(result.get("TEST", "fixture-v3"))
    diff = diff_snapshots(result.get("TEST", "fixture-v2"), result.get("TEST", "fixture-v3"))
    removal = next(change for change in diff.changes if change.target == "TEST.ID_CTRL.FLAGS[2]")
    assert removal.action == "removed" and removal.current_provenance[-1].action == "REMOVE"


def test_rule_remove_preserves_history(editable_knowledge):
    edit_yaml(editable_knowledge, "ocp/delta.yaml", lambda d: d.update(changes=[
        {"action": "REMOVE", "rule_id": "TEST.OCP.COUNT", "previous": {"requirement": "optional"}}]))
    result = build_from(editable_knowledge)
    assert not result.get("OCP", "fixture-v2").rules
    assert result.get("OCP", "fixture-v2").changes[-1].action == "REMOVE"


def test_null_rule_provenance_uses_explicit_delta_source(editable_knowledge):
    edit_yaml(editable_knowledge, "schema/modify.yaml", lambda d: d["changes"][0]["current"].update(provenance=None))
    rule = build_from(editable_knowledge).get("TEST", "fixture-v3").rules[1].rule
    assert rule.rule_id == "TEST.BASE.COUNT"
    assert rule.provenance.source_version == "fixture-v3" and rule.provenance.status == "candidate"
