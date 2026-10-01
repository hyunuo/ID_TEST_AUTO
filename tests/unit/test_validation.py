"""Build-time integrity and conflict checks use TEST/FIXTURE-only knowledge."""

from copy import deepcopy

import pytest
from ruamel.yaml import YAML

from conftest import build_from, edit_yaml
from ssd_validator.errors import KnowledgeError
from ssd_validator.knowledge.validation import _literal_compatible
from ssd_validator.models.rules import RequirementRule


@pytest.mark.parametrize("file,mutate,code", [
    ("schema/base.yaml", lambda d: d["fields"].append(deepcopy(d["fields"][0])), "MODEL_ERROR"),
    ("schema/base.yaml", lambda d: d["rules"].append(deepcopy(d["rules"][0])), "MODEL_ERROR"),
    ("schema/base.yaml", lambda d: d["fields"][0]["bits"][0].update(feature="TEST.MISSING"), "UNKNOWN_FEATURE"),
    ("schema/base.yaml", lambda d: d["provenance"].update(source_document="TEST_MISSING_SOURCE"), "DANGLING_PROVENANCE"),
    ("schema/base.yaml", lambda d: d["fields"][0].update(field_id="UNMARKED.FIELD"), "UNMARKED_FIXTURE"),
    ("schema/base.yaml", lambda d: d.update(data_kind="production"), "TEST_IS_FIXTURE"),
    ("schema/base.yaml", lambda d: d["provenance"].update(status="confirmed"), "UNVERIFIED_CONFIRMED"),
    ("ocp/base.yaml", lambda d: d["rules"][0]["target"].update(field_id="TEST.MISSING"), "UNKNOWN_FIELD"),
    ("ocp/base.yaml", lambda d: d["rules"][0]["target"].update(command="id-ns"), "TARGET_COMMAND"),
    ("mfnd/base.yaml", lambda d: d["rules"][0]["target"].update(bit=7), "UNKNOWN_BIT"),
    ("ocp/base.yaml", lambda d: d["rules"][0].update(applies_when={"hardware.capcity_tb": 4}), "UNKNOWN_CONDITION_KEY"),
    ("ocp/base.yaml", lambda d: d["schema_ref"].update(version="TEST_MISSING"), "UNKNOWN_SCHEMA"),
    ("ocp/base.yaml", lambda d: d["schema_ref"].update(spec_family="MFND"), "INVALID_SCHEMA_REF"),
    ("catalog.yaml", lambda d: d["sources"].append(deepcopy(d["sources"][0])), "MODEL_ERROR"),
    ("catalog.yaml", lambda d: d["features"].append(deepcopy(d["features"][0])), "MODEL_ERROR"),
])
def test_invalid_knowledge_fails(editable_knowledge, file, mutate, code):
    edit_yaml(editable_knowledge, file, mutate)
    with pytest.raises(KnowledgeError, match=code):
        build_from(editable_knowledge)


def test_duplicate_base_fragments_fail(editable_knowledge):
    original = editable_knowledge / "schema/base.yaml"
    (editable_knowledge / "schema/duplicate.yaml").write_bytes(original.read_bytes())
    with pytest.raises(KnowledgeError, match="DUPLICATE_FIELD"):
        build_from(editable_knowledge)


def test_disjoint_base_fragments_are_combined(editable_knowledge):
    yaml = YAML(typ="safe", pure=True)
    path = editable_knowledge / "schema/base.yaml"
    payload = yaml.load(path.read_text())
    second = deepcopy(payload)
    second["fields"], second["rules"] = [payload["fields"].pop()], []
    with path.open("w") as stream:
        yaml.dump(payload, stream)
    with (path.parent / "namespace.yaml").open("w") as stream:
        yaml.dump(second, stream)
    assert len(build_from(editable_knowledge).get("TEST", "fixture-v1").fields) == 4


def test_duplicate_delta_version_fails(editable_knowledge):
    path = editable_knowledge / "schema/add.yaml"
    (path.parent / "duplicate_delta.yaml").write_bytes(path.read_bytes())
    with pytest.raises(KnowledgeError, match="DUPLICATE_VERSION"):
        build_from(editable_knowledge)


def test_non_linear_inheritance_is_explicitly_rejected(editable_knowledge):
    edit_yaml(editable_knowledge, "schema/remove.yaml", lambda d: d.update(inherits="fixture-v2"))
    with pytest.raises(KnowledgeError, match="NON_LINEAR_INHERITANCE"):
        build_from(editable_knowledge)


def reviewed_fixture_evidence(document):
    return document["provenance"] | {"status": "confirmed", "verified_by": "TEST_FIXTURE_REVIEWER", "verified_date": "2000-01-01"}


def set_test_rules(document, checks, *, field="TEST.ID_CTRL.COUNT", conditions=None):
    document["rules"] = [
        {"rule_id": f"TEST.CONSTRAINT.{index}", "target": {"command": "id-ctrl", "field_id": field},
         "check": check, "provenance": reviewed_fixture_evidence(document),
         "applies_when": (conditions or [{}] * len(checks))[index]}
        for index, check in enumerate(checks)
    ]


@pytest.mark.parametrize("checks", [
    [{"type": "EXACT", "value": 4}, {"type": "EXACT", "value": 5}],
    [{"type": "MIN", "value": 4}, {"type": "MAX", "value": 3}],
    [{"type": "ENUM", "values": [1, 2]}, {"type": "ENUM", "values": [2, 3]}, {"type": "ENUM", "values": [1, 3]}],
])
def test_confirmed_literal_conflicts_fail(editable_knowledge, checks):
    edit_yaml(editable_knowledge, "ocp/base.yaml", lambda d: set_test_rules(d, checks))
    # The OCP delta's original target was deliberately replaced by test rules.
    (editable_knowledge / "ocp/delta.yaml").unlink()
    with pytest.raises(KnowledgeError, match="EXPLICIT_CONFLICT"):
        build_from(editable_knowledge)


def test_compatible_constraints_preserved(editable_knowledge):
    edit_yaml(editable_knowledge, "ocp/base.yaml", lambda d: set_test_rules(d, [{"type": "MIN", "value": 4}, {"type": "EXACT", "value": 5}]))
    (editable_knowledge / "ocp/delta.yaml").unlink()
    rules = build_from(editable_knowledge).get("OCP", "fixture-v1").rules
    assert len(rules) == 2 and {item.rule.check.type for item in rules} == {"MIN", "EXACT"}


def test_mutually_exclusive_conditions_are_not_a_conflict(editable_knowledge):
    edit_yaml(editable_knowledge, "ocp/base.yaml", lambda d: set_test_rules(
        d, [{"type": "EXACT", "value": 4}, {"type": "EXACT", "value": 5}],
        conditions=[{"product.model": "TEST_PRODUCT_A"}, {"product.model": "TEST_PRODUCT_B"}],
    ))
    (editable_knowledge / "ocp/delta.yaml").unlink()
    assert len(build_from(editable_knowledge).get("OCP", "fixture-v1").rules) == 2


def test_broad_and_specific_conditions_do_not_silently_override(editable_knowledge):
    edit_yaml(editable_knowledge, "ocp/base.yaml", lambda d: set_test_rules(
        d, [{"type": "EXACT", "value": 4}, {"type": "EXACT", "value": 5}],
        conditions=[{}, {"hardware.capacity_tb": 4}],
    ))
    (editable_knowledge / "ocp/delta.yaml").unlink()
    with pytest.raises(KnowledgeError, match="EXPLICIT_CONFLICT"):
        build_from(editable_knowledge)


def test_explicit_override_is_preserved(editable_knowledge):
    def change(document):
        set_test_rules(document, [{"type": "EXACT", "value": 4}, {"type": "EXACT", "value": 5}])
        document["rules"][1]["override"] = {
            "enabled": True, "overrides": ["TEST.CONSTRAINT.0"], "reason": "TEST fixture override",
            "provenance": reviewed_fixture_evidence(document),
        }
    edit_yaml(editable_knowledge, "ocp/base.yaml", change)
    (editable_knowledge / "ocp/delta.yaml").unlink()
    rules = build_from(editable_knowledge).get("OCP", "fixture-v1").rules
    assert len(rules) == 2
    assert rules[1].rule.override.overrides == ("TEST.CONSTRAINT.0",)


def test_unknown_override_fails(editable_knowledge):
    def change(document):
        document["rules"][0]["override"] = {
            "enabled": True, "overrides": ["TEST.MISSING"], "reason": "TEST fixture",
            "provenance": document["provenance"],
        }
    edit_yaml(editable_knowledge, "ocp/base.yaml", change)
    with pytest.raises(KnowledgeError, match="UNKNOWN_OVERRIDE"):
        build_from(editable_knowledge)


def test_unknown_derived_function_remains_unsupported(editable_knowledge):
    edit_yaml(editable_knowledge, "ocp/base.yaml", lambda d: d["rules"][0].update(
        check={"type": "DERIVED", "function": "TEST_UNKNOWN_FUNCTION", "inputs": ["hardware.capacity_tb"]}))
    with pytest.raises(KnowledgeError, match="UNKNOWN_FUNCTION"):
        build_from(editable_knowledge)


def test_impossible_conditions_fail(editable_knowledge):
    edit_yaml(editable_knowledge, "ocp/base.yaml", lambda d: d["rules"][0].update(
        applies_when={"controller.role": "parent"}, applicable_when={"controller.role": "child"}))
    with pytest.raises(KnowledgeError, match="IMPOSSIBLE_CONDITION"):
        build_from(editable_knowledge)


def literal_rule(index, check, bit=None):
    return RequirementRule.model_validate({
        "rule_id": f"TEST.RULE.{index}", "target": {"command": "id-ctrl", "field_id": "TEST.ID_CTRL.FLAGS", "bit": bit},
        "check": check,
    })


@pytest.mark.parametrize("checks,bits", [
    ([{"type": "BIT_SET"}, {"type": "BIT_CLEAR"}], [0, 0]),
    ([{"type": "MASK", "mask": 3, "value": 1}, {"type": "MASK", "mask": 1, "value": 0}], [None, None]),
    ([{"type": "EXACT", "value": 0}, {"type": "BIT_SET"}], [None, 0]),
    ([{"type": "ENUM", "values": [1]}, {"type": "BIT_CLEAR"}], [0, 0]),
])
def test_bit_conflicts_cover_full_and_partial_constraints(built, checks, bits):
    field = next(item.schema for item in built.get("TEST", "fixture-v1").fields if item.schema.field_id == "TEST.ID_CTRL.FLAGS")
    rules = [literal_rule(index, check, bit) for index, (check, bit) in enumerate(zip(checks, bits))]
    assert not _literal_compatible(rules, field)


def test_mask_range_consistency_against_exhaustive_fixture_oracle(built):
    field = next(item.schema for item in built.get("TEST", "fixture-v1").fields if item.schema.field_id == "TEST.ID_CTRL.FLAGS")
    for mask in range(8):
        for value in range(8):
            if value & ~mask:
                continue
            mask_rule = literal_rule(0, {"type": "MASK", "mask": mask, "value": value})
            for low in range(16):
                for high in range(low, 16):
                    rules = [mask_rule, literal_rule(1, {"type": "RANGE", "min": low, "max": high})]
                    expected = any(candidate & mask == value for candidate in range(low, high + 1))
                    assert _literal_compatible(rules, field) == expected, (mask, value, low, high)


def test_requirement_delta_cannot_define_schema_fields(editable_knowledge):
    edit_yaml(editable_knowledge, "ocp/delta.yaml", lambda d: d.update(schema_changes=[
        {"action": "MODIFY", "target": {"field_id": "TEST.ID_CTRL.COUNT"},
         "previous": {"offset": 1}, "current": {"offset": 2}}]))
    with pytest.raises(KnowledgeError, match="MODEL_ERROR"):
        build_from(editable_knowledge)


def test_unconnected_base_versions_are_not_implicitly_ordered(editable_knowledge):
    yaml = YAML(typ="safe", pure=True)
    path = editable_knowledge / "schema/base.yaml"
    payload = yaml.load(path.read_text())
    payload["version"] = "fixture-unconnected"
    with (path.parent / "unconnected.yaml").open("w") as stream:
        yaml.dump(payload, stream)
    with pytest.raises(KnowledgeError, match="MULTIPLE_BASE_VERSIONS"):
        build_from(editable_knowledge)


def test_candidate_override_cannot_suppress_confirmed_requirements(editable_knowledge):
    def change(document):
        set_test_rules(document, [{"type": "EXACT", "value": 4}, {"type": "EXACT", "value": 5}])
        document["rules"][1]["override"] = {
            "enabled": True, "overrides": ["TEST.CONSTRAINT.0"], "reason": "TEST candidate override",
            "provenance": document["provenance"],
        }
    edit_yaml(editable_knowledge, "ocp/base.yaml", change)
    (editable_knowledge / "ocp/delta.yaml").unlink()
    with pytest.raises(KnowledgeError, match="UNCONFIRMED_OVERRIDE"):
        build_from(editable_knowledge)
