"""Synthetic behavior tests, never assertions of actual NVMe/OCP/MFND policy."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from ssd_validator.application.build_knowledge import compile_knowledge
from ssd_validator.application.rule_pilot import run_pilot
from ssd_validator.errors import KnowledgeError
from ssd_validator.models.provenance import Provenance
from ssd_validator.models.runtime import (
    ActualFact, Condition, FactRef, FieldRef, FieldRegistration, PilotInput,
    PilotMappings, RuntimeContext, RuntimeRule,
)
from ssd_validator.resolver import evaluate, resolve
from ssd_validator.storage.serialization import canonical_bytes

ROOT = Path(__file__).parents[1] / "fixtures" / "rule_pilot"
P = Provenance(source_type="fixture", source_document="TEST_RULE_PILOT", source_version="fixture-v1",
               source_section="SYNTHETIC_TEST", status="confirmed", verified_by="TEST_FIXTURE_REVIEWER",
               verified_date="2026-10-11")


@pytest.fixture
def setup():
    config = PilotInput.model_validate_json((ROOT / "input.json").read_text(encoding="utf-8"))
    snapshots = compile_knowledge(ROOT / "knowledge").snapshots
    fields = {f.schema.field_id: f for s in snapshots for f in s.fields}
    registry = tuple(FieldRegistration(schema_definition=fields[b.field_id].schema,
                                      cns=b.cns, csi=b.csi, array_count=b.array_count,
                                      provenance=fields[b.field_id].history[-1].provenance,
                                      history=fields[b.field_id].history) for b in config.bindings)
    mappings = PilotMappings(bundle=config.bundle, fields=registry)
    return config.context, snapshots, mappings


def rule(check=None, *, identity="TEST.RULE", target="TEST.SIZE", condition=None, **extra):
    return RuntimeRule(rule_id=identity, target=FieldRef(field_id=target), check=check or {"type": "EXACT", "value": 5},
                       provenance=P, condition=condition, **extra)


def fact(field_id, value, index=None):
    return ActualFact(field=FieldRef(field_id=field_id, index=index), value=value)


def leaf(value=True, path="gate"):
    return Condition(op="EQ", ref=FactRef(source="context", path=path), value=value)


def execute(setup, rules, facts=(), *, context=None, **mapping_updates):
    ctx, snapshots, mappings = setup
    mappings = mappings.model_copy(update={"rules": tuple(rules), **mapping_updates})
    return evaluate(resolve(context or ctx, snapshots, mappings), tuple(facts))


@pytest.mark.parametrize("check,value,status", [
    ({"type": "EXACT", "value": 5}, 5, "PASS"),
    ({"type": "EXACT", "value": 5}, 6, "FAIL"),
    ({"type": "MIN", "value": 5}, 5, "PASS"),
    ({"type": "MAX", "value": 5}, 6, "FAIL"),
    ({"type": "RANGE", "min": 3, "max": 5}, 3, "PASS"),
    ({"type": "ENUM", "values": [3, 5]}, 4, "FAIL"),
    ({"type": "MASK", "mask": 3, "value": 1}, 5, "PASS"),
    ({"type": "BIT_SET", "bit": 2}, 4, "PASS"),
    ({"type": "BIT_CLEAR", "bit": 2}, 4, "FAIL"),
])
def test_literal_checks(setup, check, value, status):
    target = "TEST.FLAGS" if check["type"].startswith("BIT") else "TEST.SIZE"
    report = execute(setup, [rule(check, target=target)], [fact(target, value)])
    assert report.results[0].status == status
    assert report.results[0].observations[0].value == value
    assert report.results[0].rule.provenance == P


@pytest.mark.parametrize("operator,left,right,status", [
    ("=", 5, 5, "PASS"), ("!=", 5, 5, "FAIL"), ("<", 4, 5, "PASS"),
    ("<=", 5, 5, "PASS"), (">", 5, 5, "FAIL"), (">=", 5, 5, "PASS"),
])
def test_relational_checks(setup, operator, left, right, status):
    r = rule({"type": "FIELD_COMPARE", "operator": operator, "other": {"field_id": "TEST.CAPACITY"}})
    report = execute(setup, [r], [fact("TEST.SIZE", left), fact("TEST.CAPACITY", right)])
    assert report.results[0].status == status
    assert len(report.results[0].observations) == 2


@pytest.mark.parametrize("op,known,expected", [("AND", False, "N/A"), ("AND", True, "UNKNOWN"),
                                             ("OR", True, "PASS"), ("OR", False, "UNKNOWN")])
def test_three_valued_logic(setup, op, known, expected):
    ctx = RuntimeContext(bundle_id=setup[0].bundle_id, facts={"gate": known})
    condition = Condition(op=op, children=(leaf(), leaf(path="missing")))
    report = execute(setup, [rule(condition=condition)], [fact("TEST.SIZE", 5)], context=ctx)
    assert report.results[0].status == expected
    assert {o.reference.path for o in report.results[0].observations if o.reference.source == "context"} == {"gate", "missing"}


def test_not_missing_stays_unknown_and_type_errors_not_short_circuited(setup):
    condition = Condition(op="NOT", children=(leaf(),))
    assert execute(setup, [rule(condition=condition)]).status == "UNKNOWN"
    ctx = RuntimeContext(bundle_id=setup[0].bundle_id, facts={"gate": "wrong", "other": False})
    condition = Condition(op="AND", children=(leaf(), leaf(path="other")))
    assert execute(setup, [rule(condition=condition)], context=ctx).status == "ERROR"


def test_actual_condition_deferred_and_missing(setup):
    condition = Condition(op="BIT_SET", ref=FactRef(source="actual", field=FieldRef(field_id="TEST.FLAGS")), bit=0)
    ctx, snapshots, mappings = setup
    profile = resolve(ctx, snapshots, mappings.model_copy(update={"rules": (rule(condition=condition),)}))
    assert profile.entries[0].state == "CONDITIONAL"
    assert evaluate(profile, ()).status == "UNKNOWN"
    assert evaluate(profile, (fact("TEST.FLAGS", 0),)).status == "N/A"
    assert evaluate(profile, (fact("TEST.FLAGS", 1), fact("TEST.SIZE", 5))).status == "PASS"


@pytest.mark.parametrize("value", [True, "5", -1, 65536, None, {"bad": 1}])
def test_malformed_actual_is_error_with_observation(setup, value):
    report = execute(setup, [rule()], [fact("TEST.SIZE", value)])
    assert report.status == "ERROR"
    assert report.results[0].observations[0].value == value


def test_missing_operands(setup):
    assert execute(setup, [rule()]).status == "UNKNOWN"
    r = rule({"type": "FIELD_COMPARE", "operator": "<=", "other": {"field_id": "TEST.CAPACITY"}})
    assert execute(setup, [r], [fact("TEST.SIZE", 5)]).status == "UNKNOWN"


@pytest.mark.parametrize("status", ["candidate", "provisional", "deprecated"])
def test_unconfirmed_never_authoritative(setup, status):
    r = rule().model_copy(update={"provenance": P.model_copy(update={"status": status})})
    report = execute(setup, [r], [fact("TEST.SIZE", 5)])
    assert report.status == "REVIEW"
    assert report.results[0].rule.provenance.status == status


@pytest.mark.parametrize("modality", ["permission", "recommendation", "description", "behavior"])
def test_may_should_and_behavior_not_mandatory(setup, modality):
    assert execute(setup, [rule(modality=modality)], [fact("TEST.SIZE", 1)]).status == "REVIEW"


def test_unsupported_execution_and_invalid_bit(setup):
    assert execute(setup, [rule({"type": "DERIVED", "function": "TEST.F", "inputs": ["x"]})]).status == "ERROR"
    assert execute(setup, [rule({"type": "LOOKUP", "key": "x", "values": [{"key": 1, "value": 2}]})]).status == "ERROR"
    assert execute(setup, [rule({"type": "BIT_SET", "bit": 8}, target="TEST.FLAGS")]).status == "ERROR"
    assert execute(setup, [rule({"type": "EXACT", "value": True})]).status == "ERROR"


def test_arrays_indexed_independently(setup):
    r = rule(target="TEST.LBADS").model_copy(update={"target": FieldRef(field_id="TEST.LBADS", index=1)})
    assert execute(setup, [r], [fact("TEST.LBADS", 5, 0)]).status == "UNKNOWN"
    assert execute(setup, [r], [fact("TEST.LBADS", 4, 0), fact("TEST.LBADS", 5, 1)]).status == "PASS"
    assert execute(setup, [rule(target="TEST.LBADS")]).status == "ERROR"
    assert execute(setup, [r.model_copy(update={"target": FieldRef(field_id="TEST.LBADS", index=2)})]).status == "ERROR"


@pytest.mark.parametrize("checks", [
    ({"type": "EXACT", "value": 1}, {"type": "EXACT", "value": 2}),
    ({"type": "MIN", "value": 5}, {"type": "MAX", "value": 4}),
    ({"type": "MASK", "mask": 1, "value": 1}, {"type": "MASK", "mask": 1, "value": 0}),
    ({"type": "EXACT", "value": 2}, {"type": "MASK", "mask": 1, "value": 1}),
])
def test_literal_conflicts_and_order_independence(setup, checks):
    rules = [rule(checks[0], identity="TEST.A"), rule(checks[1], identity="TEST.B")]
    report = execute(setup, rules, [fact("TEST.SIZE", 2)])
    assert report.status == "CONFLICT"
    assert all(r.related_rules == ("TEST.A", "TEST.B") for r in report.results)
    assert canonical_bytes(report) == canonical_bytes(execute(setup, list(reversed(rules)), [fact("TEST.SIZE", 2)]))


def test_conditional_conflicts_only_when_active(setup):
    gate = Condition(op="BIT_SET", ref=FactRef(source="actual", field=FieldRef(field_id="TEST.FLAGS")), bit=0)
    rules = [rule(identity="TEST.A"), rule({"type": "EXACT", "value": 6}, identity="TEST.B", condition=gate)]
    assert execute(setup, rules, [fact("TEST.FLAGS", 0), fact("TEST.SIZE", 5)]).status == "PASS"
    assert execute(setup, rules, [fact("TEST.FLAGS", 1), fact("TEST.SIZE", 5)]).status == "CONFLICT"
    assert execute(setup, rules, [fact("TEST.SIZE", 5)]).status == "UNKNOWN"


def test_override_is_explicit_traced_and_conditioned(setup):
    old = rule(identity="TEST.OLD")
    gate = Condition(op="BIT_SET", ref=FactRef(source="actual", field=FieldRef(field_id="TEST.FLAGS")), bit=0)
    new = rule({"type": "EXACT", "value": 6}, identity="TEST.NEW", condition=gate,
               override={"enabled": True, "overrides": ["TEST.OLD"], "reason": "Synthetic test exception", "provenance": P})
    report = execute(setup, [old, new], [fact("TEST.FLAGS", 1), fact("TEST.SIZE", 6)])
    assert report.status == "PASS"
    assert {r.rule.rule_id: r.status for r in report.results} == {"TEST.NEW": "PASS", "TEST.OLD": "N/A"}
    assert report.results[1].related_rules == ("TEST.NEW",)
    assert execute(setup, [old, new], [fact("TEST.FLAGS", 0), fact("TEST.SIZE", 5)]).status == "PASS"
    assert execute(setup, [old, new], [fact("TEST.SIZE", 5)]).status == "UNKNOWN"


def test_invalid_override_chain_and_unconfirmed_override(setup):
    override = {"enabled": True, "overrides": ["TEST.A"], "reason": "Test", "provenance": P}
    a = rule(identity="TEST.A")
    b = rule(identity="TEST.B", override=override)
    c = rule(identity="TEST.C", override={**override, "overrides": ["TEST.B"]})
    assert execute(setup, [a, b, c]).status == "ERROR"
    b = rule(identity="TEST.B", override={**override, "provenance": P.model_copy(update={"status": "candidate"})})
    assert execute(setup, [a, b]).status == "ERROR"


def test_reserved_does_not_create_zero_but_explicit_behavior_does(setup):
    ctx, snapshots, mappings = setup
    assert resolve(ctx, snapshots, mappings).entries == ()
    registrations = list(mappings.fields)
    flags = next(f for f in registrations if f.schema_definition.field_id == "TEST.FLAGS")
    schema = flags.schema_definition
    data = schema.model_dump()
    for bit in data["bits"]:
        if bit["bit"] == 1:
            bit["validation"] = {"behavior": "must_be_zero"}
    schema = type(schema).model_validate(data)
    registration = flags.model_copy(update={"schema_definition": schema})
    registrations = tuple(registration if f == flags else f for f in registrations)
    fields = tuple(f.model_copy(update={"field_schema": schema}) if f.schema.field_id == "TEST.FLAGS" else f for f in snapshots[0].fields)
    snapshot = snapshots[0].model_copy(update={"fields": fields})
    profile = resolve(ctx, (snapshot,), mappings.model_copy(update={"fields": registrations}))
    assert len(profile.entries) == 1
    assert evaluate(profile, (fact("TEST.FLAGS", 2),)).status == "FAIL"


def test_capability_support_cannot_be_bypassed_and_mapping_evidence_retained(tmp_path):
    config = json.loads((ROOT / "input.json").read_text(encoding="utf-8"))
    config["actual_facts"][0]["value"] = 0
    path = tmp_path / "input.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    report = run_pilot(ROOT / "knowledge", path)
    cap = next(r for r in report.results if r.rule.origin == "mapping")
    assert cap.status == "FAIL"
    assert cap.rule.supporting_evidence[0].source_section == "SYNTHETIC_CAPABILITY_MAPPING"
    assert cap.rule.provenance.source_section == "SYNTHETIC_RULES_NOT_SPEC_KNOWLEDGE"


def test_fixture_demo_and_lineage():
    from hashlib import sha256
    report = run_pilot(ROOT / "knowledge", ROOT / "input.json")
    assert report.status == "PASS"
    assert len(report.results) == 6
    assert all(f.history[0].source_hash for f in report.profile.fields)
    assert all(f.history[0].source_file.endswith("base.yaml") for f in report.profile.fields)
    assert report.profile.input_source.sha256 == sha256((ROOT / "input.json").read_bytes()).hexdigest()


def test_bundle_selection_and_production_guards(setup):
    ctx, snapshots, mappings = setup
    with pytest.raises(KnowledgeError, match="BUNDLE_MISMATCH"):
        resolve(ctx.model_copy(update={"bundle_id": "TEST.other"}), snapshots, mappings)
    with pytest.raises(KnowledgeError, match="SNAPSHOT_SELECTION"):
        resolve(ctx, (), mappings)
    with pytest.raises(KnowledgeError, match="PILOT_FIXTURE_ONLY"):
        resolve(ctx, (snapshots[0].model_copy(update={"data_kind": "production"}),), mappings)
    with pytest.raises(KnowledgeError, match="DUPLICATE_ACTUAL_FACT"):
        evaluate(resolve(ctx, snapshots, mappings), (fact("TEST.SIZE", 1), fact("TEST.SIZE", 2)))


def test_closed_conditions_and_reference_contracts():
    with pytest.raises(ValidationError):
        Condition(op="NOT", children=())
    with pytest.raises(ValidationError):
        Condition(op="EQ", ref=FactRef(source="context", path="x"), value=True, children=(leaf(),))
    with pytest.raises(ValidationError):
        FactRef(source="actual", path="x")


def test_duplicate_json_keys_rejected(tmp_path):
    path = tmp_path / "input.json"
    path.write_text('{"context": {}, "context": {}}', encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate JSON"):
        run_pilot(ROOT / "knowledge", path)


def test_mask_on_decoded_bit_is_shifted_for_conflict_check(setup):
    whole = rule({"type": "EXACT", "value": 4}, identity="TEST.WHOLE", target="TEST.FLAGS")
    bit = rule({"type": "MASK", "mask": 1, "value": 1}, identity="TEST.BIT", target="TEST.FLAGS")
    bit = bit.model_copy(update={"target": FieldRef(field_id="TEST.FLAGS", bit=2)})
    assert execute(setup, [whole, bit], [fact("TEST.FLAGS", 4)]).status == "PASS"
    bit = bit.model_copy(update={"check": type(bit.check)(type="MASK", mask=1, value=0)})
    assert execute(setup, [whole, bit], [fact("TEST.FLAGS", 4)]).status == "CONFLICT"


def test_invalid_unused_actual_is_not_hidden(setup):
    report = execute(setup, [rule()], [fact("TEST.SIZE", 5), fact("TEST.CAPACITY", "bad")])
    assert report.status == "ERROR"
    assert report.results[0].status == "PASS"
    assert report.input_errors[0].field.field_id == "TEST.CAPACITY"


def test_unverified_confirmed_and_missing_mapping_are_errors(setup):
    r = rule().model_copy(update={"provenance": P.model_copy(update={"verified_by": None})})
    assert execute(setup, [r]).status == "ERROR"
    cap = rule({"type": "CAPABILITY", "capability_id": "TEST.ABSENT", "support": "supported"})
    assert execute(setup, [cap]).status == "ERROR"


def test_unconfirmed_mapping_cannot_emit_pass(tmp_path):
    config = json.loads((ROOT / "input.json").read_text(encoding="utf-8"))
    config["capabilities"][0]["provenance"]["status"] = "candidate"
    path = tmp_path / "input.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    report = run_pilot(ROOT / "knowledge", path)
    cap = next(r for r in report.results if r.rule.origin == "mapping")
    assert cap.status == "REVIEW"
    assert report.status == "REVIEW"


def test_selected_bundle_does_not_load_other_revision(setup):
    ctx, snapshots, mappings = setup
    old = rule(identity="TEST.V1")
    new = rule({"type": "EXACT", "value": 6}, identity="TEST.V2")
    old_report = execute(setup, [old], [fact("TEST.SIZE", 5)])
    v2_spec = snapshots[0].spec.model_copy(update={"version": "fixture-v2"})
    v2 = snapshots[0].model_copy(update={"spec": v2_spec})
    bundle = mappings.bundle.model_copy(update={"bundle_id": "TEST.bundle-v2", "base_revision": "TEST_BASE.fixture-v2",
                                                "nvm_revision": "TEST_NVM.fixture-v2", "snapshot_keys": (v2_spec.key,)})
    ctx2 = ctx.model_copy(update={"bundle_id": bundle.bundle_id})
    report = evaluate(resolve(ctx2, (v2,), mappings.model_copy(update={"bundle": bundle, "rules": (new,)})), (fact("TEST.SIZE", 5),))
    assert old_report.status == "PASS"
    assert report.status == "FAIL"
    assert [r.rule.rule_id for r in report.results] == ["TEST.V2"]
    with pytest.raises(KnowledgeError, match="SNAPSHOT_SELECTION"):
        resolve(ctx2, snapshots, mappings.model_copy(update={"bundle": bundle}))


def test_legacy_builder_rules_preserve_history_and_conditions(tmp_path):
    from shutil import copytree
    from ruamel.yaml import YAML

    source = tmp_path / "knowledge"
    copytree(ROOT / "knowledge", source)
    yaml = YAML(typ="safe")
    data = yaml.load((source / "base.yaml").read_text(encoding="utf-8"))
    data["rules"] = [{"rule_id": "TEST.SOURCE_RULE", "target": {"command": "fixture-id-ns", "field_id": "TEST.SIZE"},
                      "check": {"type": "EXACT", "value": 100}, "applies_when": {"controller.role": "parent"},
                      "applicable_when": {"controller.mode": "SPF"}}]
    with (source / "base.yaml").open("w", encoding="utf-8") as stream:
        yaml.dump(data, stream)
    config = json.loads((ROOT / "input.json").read_text(encoding="utf-8"))
    config["context"]["facts"].update({"controller.role": "parent", "controller.mode": "MPF"})
    path = tmp_path / "input.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    report = run_pilot(source, path)
    result = next(r for r in report.results if r.rule.rule_id == "TEST.SOURCE_RULE")
    assert result.status == "N/A"
    assert len(result.rule.condition.children) == 2
    assert result.rule.history[0].source_file == "base.yaml"
    assert result.rule.history[0].source_hash


def test_fixture_cross_family_capability_layer(setup):
    from ssd_validator.models.effective import EffectiveRule, EffectiveSnapshot
    from ssd_validator.models.identifiers import SpecFamily, SpecVersion
    from ssd_validator.models.rules import RequirementRule

    ctx, snapshots, mappings = setup
    config = PilotInput.model_validate_json((ROOT / "input.json").read_text(encoding="utf-8"))
    requirement = RequirementRule(rule_id="TEST.MFND.REQUIRED", target={"command": "fixture-id-ctrl", "field_id": "TEST.FLAGS"},
                                  check={"type": "CAPABILITY", "capability_id": "TEST.REQUIRED_FEATURE", "support": "supported"},
                                  provenance=P)
    spec = SpecVersion(spec_family=SpecFamily.MFND, version="fixture-v1")
    policy = EffectiveSnapshot(spec=spec, schema_ref=snapshots[0].spec, data_kind="fixture",
                               rules=(EffectiveRule(rule=requirement, introduced_in=spec, last_changed_in=spec, history=()),))
    bundle = mappings.bundle.model_copy(update={"snapshot_keys": (*mappings.bundle.snapshot_keys, spec.key)})
    mappings = mappings.model_copy(update={"bundle": bundle, "capabilities": config.capabilities})
    report = evaluate(resolve(ctx, (*snapshots, policy), mappings), (fact("TEST.FLAGS", 0),))
    assert report.status == "FAIL"
    assert report.results[0].rule.origin_rule_id == "TEST.MFND.REQUIRED"
    # This is a synthetic family-labeled fixture, not real MFND knowledge.
    with pytest.raises(KnowledgeError, match="SCHEMA_SELECTION"):
        resolve(ctx, (policy,), mappings.model_copy(update={"bundle": bundle.model_copy(update={"snapshot_keys": (spec.key,)})}))


def test_context_whitespace_cannot_collapse_distinct_keys():
    with pytest.raises(ValidationError, match="surrounding whitespace"):
        RuntimeContext(bundle_id="TEST.bundle", facts={"gate": True, " gate ": False})
    with pytest.raises(ValidationError, match="surrounding whitespace"):
        FactRef(source="context", path=" gate ")
