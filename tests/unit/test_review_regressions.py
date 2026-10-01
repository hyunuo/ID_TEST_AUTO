"""Independent semantic regressions for the senior review; TEST/FIXTURE only."""

from copy import deepcopy
from dataclasses import replace
from hashlib import sha256

import pytest

from ssd_validator.errors import KnowledgeError
from pydantic import ValidationError
from ssd_validator.models.rules import LookupCheck
from ssd_validator.models.identifiers import SpecVersion
from ssd_validator.spec_builder.builder import build_knowledge
from ssd_validator.spec_builder.delta import match_guard
from ssd_validator.storage.serialization import canonical_bytes
from ssd_validator.storage.artifacts import write_build


def edited(sources, path, edit):
    source = next(source for source in sources if source.path == path)
    payload = deepcopy(source.document.model_dump(mode="json"))
    edit(payload)
    document = type(source.document).model_validate(payload)
    return replace(source, document=document, sha256=sha256(canonical_bytes(document)).hexdigest())


def minimal(sources, *updates):
    selected = {s.path: s for s in sources if s.path in {"catalog.yaml", "schema/base.yaml"}}
    selected.update({s.path: s for s in updates})
    return build_knowledge(tuple(selected.values()), git_commit="TEST_FIXTURE_COMMIT")


def reviewed(document):
    return document["provenance"] | {
        "status": "confirmed", "verified_by": "TEST_NEW_REVIEWER", "verified_date": "2000-01-02",
    }


def confirm_base(document):
    document["rules"][0]["provenance"] = reviewed(document)


def rule_delta(document):
    document["inherits"] = "fixture-v1"
    document["schema_changes"] = []


@pytest.mark.parametrize("partial", [{"source_section": "TEST_UNREVIEWED"}, {"status": "confirmed"}, {}])
def test_partial_provenance_cannot_reuse_parent_approval(sources, partial):
    def change(document):
        rule_delta(document)
        document["changes"][0]["current"]["provenance"] = partial
    with pytest.raises(KnowledgeError, match="DELTA_MODEL_ERROR"):
        minimal(sources, edited(sources, "schema/base.yaml", confirm_base),
                edited(sources, "schema/modify.yaml", change))


def test_candidate_change_does_not_inherit_confirmed_evidence(sources):
    result = minimal(sources, edited(sources, "schema/base.yaml", confirm_base),
                     edited(sources, "schema/modify.yaml", rule_delta))
    item = result.get("TEST", "fixture-v3").rules[0]
    assert item.rule.check.value == 5
    assert item.rule.provenance.status == "candidate"
    assert item.rule.provenance.verified_by is None
    assert item.rule.provenance.verified_date is None
    assert item.history[0].provenance.status == "confirmed"
    assert item.history[-1].provenance == item.rule.provenance


def test_explicit_review_is_preserved_in_rule_and_history(sources):
    def change(document):
        rule_delta(document)
        document["changes"][0]["current"]["provenance"] = reviewed(document)
    result = minimal(sources, edited(sources, "schema/modify.yaml", change))
    item = result.get("TEST", "fixture-v3").rules[0]
    assert item.rule.provenance.status == "confirmed"
    assert item.rule.provenance.source_version == "fixture-v3"
    assert item.history[-1].provenance == item.rule.provenance


def test_two_explicit_rule_sources_cannot_silently_override(sources):
    def change(document):
        rule_delta(document)
        document["changes"][0]["provenance"] = document["provenance"]
        document["changes"][0]["current"]["provenance"] = reviewed(document)
    with pytest.raises(KnowledgeError, match="PROVENANCE_CONFLICT"):
        minimal(sources, edited(sources, "schema/modify.yaml", change))


def test_deprecation_uses_delta_evidence(built):
    item = next(r for r in built.get("TEST", "fixture-v4").rules if r.rule.rule_id == "TEST.BASE.ADDED")
    assert item.rule.provenance.status == "deprecated"
    assert item.rule.provenance.source_version == "fixture-v4"
    assert item.history[-1].provenance == item.rule.provenance


def test_lookup_preserves_typed_keys_through_build_and_json(sources):
    def change(document):
        document["rules"][0]["check"] = {
            "type": "LOOKUP", "key": "hardware.capacity_tb", "values": {1: 2, "1": 3},
        }
    result = minimal(sources, edited(sources, "schema/base.yaml", change))
    check = result.snapshots[0].rules[0].rule.check
    assert [(type(entry.key), entry.key, entry.value) for entry in check.values] == [(int, 1, 2), (str, "1", 3)]
    assert LookupCheck.model_validate_json(check.model_dump_json()) == check
    reverse = LookupCheck(type="LOOKUP", key="hardware.capacity_tb", values={"1": 3, 1: 2})
    assert canonical_bytes(reverse) == canonical_bytes(check)


def test_lookup_rejects_duplicate_typed_entries():
    with pytest.raises(ValidationError, match="Duplicate typed LOOKUP key"):
        LookupCheck(type="LOOKUP", key="hardware.capacity_tb", values=[
            {"key": 1, "value": 2}, {"key": 1, "value": 3},
        ])


def test_case_colliding_versions_fail_before_publication(sources):
    def base(document):
        document["version"] = "v1"
    def delta(document):
        rule_delta(document)
        document["version"], document["inherits"] = "V1", "v1"
    with pytest.raises(KnowledgeError, match="ARTIFACT_PATH_COLLISION"):
        minimal(sources, edited(sources, "schema/base.yaml", base),
                edited(sources, "schema/modify.yaml", delta))


@pytest.mark.parametrize("version", ["v1.", "CON", "nul", "COM1.extra", "LPT9"])
def test_nonportable_version_names_are_rejected(version):
    with pytest.raises(ValidationError, match="portable file name"):
        SpecVersion(spec_family="TEST", version=version)


def test_writer_rejects_duplicate_paths_without_touching_existing_output(built, tmp_path, source_root):
    output = tmp_path / "output"
    write_build(built, output, source_root=source_root)
    before = {p.relative_to(output): p.read_bytes() for p in output.rglob("*") if p.is_file()}
    duplicate = replace(built, snapshots=(*built.snapshots, built.snapshots[0]))
    with pytest.raises(KnowledgeError, match="ARTIFACT_PATH_COLLISION"):
        write_build(duplicate, output, source_root=source_root)
    assert before == {p.relative_to(output): p.read_bytes() for p in output.rglob("*") if p.is_file()}


@pytest.mark.parametrize("field", ["applies_when", "applicable_when"])
def test_inherited_rule_conditions_cannot_mutate_parent_or_child(built, field):
    parent = built.get("TEST", "fixture-v1")
    child = built.get("TEST", "fixture-v2")
    before = [canonical_bytes(parent), canonical_bytes(child), canonical_bytes(built.manifest)]
    rule = parent.rules[0].rule
    with pytest.raises(TypeError, match="immutable"):
        getattr(rule, field)["product.model"] = "TEST_MUTATION"
    with pytest.raises(TypeError, match="immutable"):
        getattr(rule, field).update({"product.model": "TEST_MUTATION"})
    assert before == [canonical_bytes(parent), canonical_bytes(child), canonical_bytes(built.manifest)]


def test_source_delta_collections_and_copy_updates_are_immutable(sources):
    delta = next(s.document for s in sources if s.path == "schema/modify.yaml")
    with pytest.raises(TypeError, match="immutable"):
        delta.changes[0].current["check"]["value"] = 99
    copied = delta.changes[0].model_copy(update={"current": {"check": {"values": [1, 2]}}})
    with pytest.raises(TypeError, match="immutable"):
        copied.current["check"]["values"].append(3)
    dumped = copied.model_dump(mode="json")
    dumped["current"]["check"]["values"].append(3)
    assert copied.current["check"]["values"] == [1, 2]


@pytest.mark.parametrize("action", ["MODIFY", "REDEFINE"])
def test_rule_cannot_move_to_another_field(sources, action):
    def change(document):
        rule_delta(document)
        payload = next(s.document for s in sources if s.path == "schema/base.yaml").rules[0].model_dump(mode="json")
        payload["target"]["field_id"] = "TEST.ID_CTRL.OBSOLETE"
        document["changes"][0].update(action=action, current=payload)
    with pytest.raises(KnowledgeError, match="TARGET_IDENTITY"):
        minimal(sources, edited(sources, "schema/modify.yaml", change))


def test_bit_check_cannot_move_its_implicit_target(sources):
    def base(document):
        document["rules"][0]["target"]["field_id"] = "TEST.ID_CTRL.FLAGS"
        document["rules"][0]["check"] = {"type": "BIT_SET", "bit": 0}
    def delta(document):
        rule_delta(document)
        document["changes"][0].update(previous={"check": {"bit": 0}}, current={"check": {"bit": 1}})
    with pytest.raises(KnowledgeError, match="TARGET_IDENTITY"):
        minimal(sources, edited(sources, "schema/base.yaml", base), edited(sources, "schema/modify.yaml", delta))


def test_schema_command_cannot_change_when_target_omits_command(sources):
    def change(document):
        rule_delta(document)
        document["changes"] = []
        document["schema_changes"] = [{"action": "MODIFY", "target": {"field_id": "TEST.ID_CTRL.OBSOLETE"},
                                       "previous": {"command": "id-ctrl"}, "current": {"command": "id-ns"}}]
    with pytest.raises(KnowledgeError, match="TARGET_IDENTITY"):
        minimal(sources, edited(sources, "schema/modify.yaml", change))


@pytest.mark.parametrize("implicit", [False, True])
@pytest.mark.parametrize("status", ["confirmed", "candidate", "deprecated"])
def test_deprecated_bit_rejects_active_rules(sources, implicit, status):
    def change(document):
        document["fields"][0]["bits"][0]["lifecycle"] = "deprecated"
        document["rules"] = [{"rule_id": "TEST.DEPRECATED_BIT",
                               "target": {"command": "id-ctrl", "field_id": "TEST.ID_CTRL.FLAGS"},
                               "check": {"type": "BIT_SET"}, "provenance": reviewed(document) | {"status": status}}]
        document["rules"][0]["check" if implicit else "target"]["bit"] = 0
    source = edited(sources, "schema/base.yaml", change)
    if status == "deprecated":
        assert minimal(sources, source).snapshots[0].rules[0].rule.provenance.status == "deprecated"
    else:
        with pytest.raises(KnowledgeError, match="DEPRECATED_TARGET"):
            minimal(sources, source)


def test_production_snapshot_cannot_use_fixture_evidence(sources):
    def change(document):
        document.update(spec_family="NVME", data_kind="production")
        confirm_base(document)
    with pytest.raises(KnowledgeError, match="FIXTURE_IN_PRODUCTION"):
        minimal(sources, edited(sources, "schema/base.yaml", change))


@pytest.mark.parametrize("zero_behavior,status,expect_conflict", [
    (True, "confirmed", True), (False, "confirmed", False), (True, "candidate", False),
])
def test_explicit_schema_zero_conflicts_without_inferring_reserved_zero(sources, zero_behavior, status, expect_conflict):
    def change(document):
        document["provenance"] = reviewed(document) | {"status": status}
        if not zero_behavior:
            document["fields"][0]["bits"][1].pop("validation")
        document["rules"] = [{"rule_id": "TEST.ZERO_CONFLICT", "target": {
            "command": "id-ctrl", "field_id": "TEST.ID_CTRL.FLAGS", "bit": 1},
            "check": {"type": "BIT_SET"}, "provenance": reviewed(document)}]
    source = edited(sources, "schema/base.yaml", change)
    if expect_conflict:
        with pytest.raises(KnowledgeError, match="EXPLICIT_CONFLICT.*SCHEMA.VALIDATION"):
            minimal(sources, source)
    else:
        assert minimal(sources, source).snapshots


def test_schema_reference_upgrade_is_guarded_and_visible_in_diff(sources):
    from ssd_validator.analyzer.spec_diff import diff_snapshots
    from ssd_validator.application.build_knowledge import select_build
    from ssd_validator.models.identifiers import SpecFamily
    def change(document):
        document["schema_ref_change"] = {
            "previous": {"spec_family": "TEST", "version": "fixture-v1"},
            "current": {"spec_family": "TEST", "version": "fixture-v2"},
        }
        document["changes"].append({"action": "ADD", "rule_id": "TEST.NEW_SCHEMA_FIELD", "current": {
            "rule_id": "TEST.NEW_SCHEMA_FIELD", "target": {"command": "id-ctrl", "field_id": "TEST.ID_CTRL.ADDED"},
            "check": {"type": "EXACT", "value": 1}}})
    delta = edited(sources, "ocp/delta.yaml", change)
    result = build_knowledge(tuple(delta if s.path == delta.path else s for s in sources))
    old, new = result.get("OCP", "fixture-v1"), result.get("OCP", "fixture-v2")
    assert old.schema_ref.version == "fixture-v1"
    assert new.schema_ref.version == "fixture-v2"
    reference = next(c for c in diff_snapshots(old, new).changes if c.category == "schema_reference")
    assert reference.current_provenance[-1].target == "@schema_ref"
    assert reference.current_provenance[-1].provenance.source_version == "fixture-v2"
    assert {s.spec.key for s in select_build(result, SpecFamily.OCP, "fixture-v2").snapshots} == {
        "OCP:fixture-v1", "OCP:fixture-v2", "TEST:fixture-v1", "TEST:fixture-v2",
    }


@pytest.mark.parametrize("previous,current,code", [
    ("fixture-v2", "fixture-v2", "GUARD_MISMATCH"),
    ("fixture-v1", "TEST_MISSING", "UNKNOWN_SCHEMA"),
])
def test_invalid_schema_reference_upgrade_fails(sources, previous, current, code):
    def change(document):
        document["schema_ref_change"] = {
            "previous": {"spec_family": "TEST", "version": previous},
            "current": {"spec_family": "TEST", "version": current},
        }
    delta = edited(sources, "ocp/delta.yaml", change)
    with pytest.raises(KnowledgeError, match=code):
        build_knowledge(tuple(delta if s.path == delta.path else s for s in sources))


def test_execution_manifest_records_runtime_without_changing_snapshot(built, source_root, tmp_path):
    import json
    import platform
    from importlib.metadata import version
    output = tmp_path / "output"
    write_build(built, output, source_root=source_root)
    execution = json.loads((output / "manifests/execution.json").read_text(encoding="utf-8"))
    assert execution["toolchain"]["python"] == platform.python_version()
    assert execution["toolchain"]["pydantic"] == version("pydantic")
    assert (output / "effective/test/fixture-v1.json").read_bytes() == canonical_bytes(built.get("TEST", "fixture-v1"))


@pytest.mark.parametrize("where", ["rule", "override", "feature", "delta"])
def test_fixture_evidence_is_rejected_at_each_production_boundary(sources, where):
    # Invented contract-test source metadata only; this is not approved Spec data.
    declared_source = {"source_type": "spec", "source_document": "TEST_DECLARED_SOURCE", "source_version": "TEST_REV"}
    fixture_evidence = next(s.document for s in sources if s.path == "schema/base.yaml").provenance.model_dump(mode="json")
    def catalog(document):
        document["sources"].append(declared_source)
    def base(document):
        document.update(spec_family="NVME", data_kind="production")
        document["provenance"] = fixture_evidence | declared_source
        for bit in document["fields"][0]["bits"]:
            bit["feature"] = None
        if where == "feature":
            document["fields"][0]["bits"][0]["feature"] = "TEST.FEATURE_ALPHA"
        document["rules"][0]["provenance"] = fixture_evidence if where == "rule" else document["provenance"]
        if where == "override":
            other = deepcopy(document["rules"][0])
            other["rule_id"] = "TEST.BASELINE"
            document["rules"].append(other)
            document["rules"][0]["override"] = {
                "enabled": True, "overrides": ["TEST.BASELINE"], "reason": "TEST_CONTRACT_ONLY",
                "provenance": fixture_evidence | {"status": "confirmed", "verified_by": "TEST_REVIEWER",
                                                    "verified_date": "2000-01-01"},
            }
    updates = [edited(sources, "catalog.yaml", catalog), edited(sources, "schema/base.yaml", base)]
    if where == "delta":
        def delta(document):
            rule_delta(document)
            document.update(spec_family="NVME", data_kind="production")
        updates.append(edited(sources, "schema/modify.yaml", delta))
    with pytest.raises(KnowledgeError, match="FIXTURE_IN_PRODUCTION"):
        minimal(sources, *updates)


def test_lookup_keys_survive_delta_guards_and_snapshot_roundtrip(sources):
    from ssd_validator.models.effective import EffectiveSnapshot
    def base(document):
        document["rules"][0]["check"] = {
            "type": "LOOKUP", "key": "hardware.capacity_tb", "values": {1: 2, "1": 3},
        }
    def delta(document):
        rule_delta(document)
        document["changes"][0].update(previous={"check": {"values": [
            {"key": 1, "value": 2}, {"key": "1", "value": 3}]}}, current={"check": {"values": [
            {"key": 1, "value": 4}, {"key": "1", "value": 5}]}})
    result = minimal(sources, edited(sources, "schema/base.yaml", base), edited(sources, "schema/modify.yaml", delta))
    snapshot = result.get("TEST", "fixture-v3")
    restored = EffectiveSnapshot.model_validate_json(canonical_bytes(snapshot))
    assert restored == snapshot
    assert [(e.key, e.value) for e in restored.rules[0].rule.check.values] == [(1, 4), ("1", 5)]


@pytest.mark.parametrize("expected,actual", [([True], [1]), ([{"value": True}], [{"value": 1}])])
def test_array_guards_compare_nested_scalar_types(expected, actual):
    with pytest.raises(KnowledgeError, match="GUARD_MISMATCH"):
        match_guard({"values": expected}, {"values": actual}, "TEST_ARRAY")


@pytest.mark.parametrize("scope", ["applies_when", "applicable_when"])
def test_condition_keys_cannot_collapse_after_whitespace_normalization(sources, scope):
    def change(document):
        document["rules"][0][scope] = {"product.model": "TEST_A", " product.model ": "TEST_B"}
    with pytest.raises(ValidationError, match="surrounding whitespace"):
        edited(sources, "schema/base.yaml", change)
