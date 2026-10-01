"""Source contracts reject ambiguous and malformed inputs rather than filling facts."""

from copy import deepcopy

import pytest
from pydantic import ValidationError

from conftest import build_from, edit_yaml, make_symlink
from ssd_validator.errors import KnowledgeError
from ssd_validator.knowledge.yaml_loader import load_document, load_knowledge
from ssd_validator.models.identifiers import SpecFamily, SpecVersion
from ssd_validator.models.rules import RequirementRule
from ssd_validator.models.schema import BitSchema, FieldSchema
from ssd_validator.models.specs import BaseSpec, DeltaSpec


def test_spec_identity_is_not_numeric():
    assert SpecVersion(spec_family="TEST", version="fixture-v10").key == "TEST:fixture-v10"
    assert SpecFamily.NVME.value == "NVME"
    with pytest.raises(ValidationError):
        SpecVersion(spec_family="TEST", version=2.1)


@pytest.mark.parametrize("version", ["../outside", "/tmp", "", "v/1"])
def test_version_labels_cannot_be_paths(version):
    with pytest.raises(ValidationError):
        SpecVersion(spec_family="TEST", version=version)


def test_reserved_does_not_invent_zero_check():
    bit = BitSchema(bit=1, state="reserved")
    assert bit.validation is None
    assert "expected" not in bit.model_dump()


@pytest.mark.parametrize("changes", [
    {"offset": True}, {"offset": -1}, {"length": 0}, {"length": "1"},
    {"bits": [{"bit": 8, "state": "reserved"}]},
    {"bits": [{"bit": 1, "state": "reserved"}, {"bit": 1, "state": "defined"}]},
    {"unexpected": "TEST"},
])
def test_invalid_field_schema(sources, changes):
    base = next(source.document for source in sources if source.path == "schema/base.yaml")
    payload = base.fields[0].model_dump(mode="json") | changes
    with pytest.raises(ValidationError):
        FieldSchema.model_validate(payload)


def test_explicit_base_command_is_supported(sources):
    base = next(source.document for source in sources if source.path == "schema/base.yaml")
    payload = base.model_dump(mode="json")
    payload["fields"] = [deepcopy(payload["fields"][0])]
    payload["command"] = payload["fields"][0].pop("command")
    assert BaseSpec.model_validate(payload).fields[0].command == "id-ctrl"


@pytest.mark.parametrize("payload", [
    {"check": {"type": "RANGE", "min": 4, "max": 1}},
    {"check": {"type": "NOT_SUPPORTED"}},
    {"check": {"type": "MASK", "mask": 1, "value": 2}},
    {"check": {"type": "BIT_SET"}},
    {"target": {"command": "id-ctrl", "field_id": "TEST.ID_CTRL.FLAGS", "bit": 0},
     "check": {"type": "BIT_SET", "bit": 1}},
])
def test_invalid_rule_models(payload):
    baseline = {"rule_id": "TEST.RULE", "target": {"command": "id-ctrl", "field_id": "TEST.ID_CTRL.COUNT"},
                "check": {"type": "EXACT", "value": 1}}
    with pytest.raises(ValidationError):
        RequirementRule.model_validate(baseline | payload)


@pytest.mark.parametrize("body", [
    "kind: base\nkind: delta\n", "kind: [broken\n", "!!python/object:builtins.object {}\n", "[]\n",
    "kind: effective_snapshot\n", "---\nkind: catalog\nsources: []\n---\nkind: catalog\nsources: []\n",
])
def test_yaml_rejects_bad_or_generated_documents(tmp_path, body):
    path = tmp_path / "bad.yaml"
    path.write_text(body)
    with pytest.raises(KnowledgeError) as error:
        load_document(path)
    assert "bad.yaml" in str(error.value)


def test_empty_and_generated_source_roots_fail(tmp_path):
    with pytest.raises(KnowledgeError, match="NO_SOURCE"):
        load_knowledge(tmp_path)
    generated = tmp_path / "generated"
    generated.mkdir()
    with pytest.raises(KnowledgeError, match="GENERATED_IS_NOT_SOURCE"):
        load_knowledge(generated)


def test_source_symlink_rejected(tmp_path, source_root):
    make_symlink(tmp_path / "linked.yaml", source_root / "catalog.yaml")
    with pytest.raises(KnowledgeError, match="SOURCE_SYMLINK"):
        load_knowledge(tmp_path)


@pytest.mark.parametrize("mutation", [
    lambda d: d["schema_changes"][0].pop("previous"),
    lambda d: d["schema_changes"].append(deepcopy(d["schema_changes"][0])),
    lambda d: d["schema_changes"].append({"action": "MODIFY", "target": {"field_id": "TEST.ID_CTRL.FLAGS"},
                                          "previous": {"name": "TEST_FLAGS"}, "current": {"name": "TEST_OTHER"}}),
])
def test_guard_required_and_overlapping_changes_rejected(editable_knowledge, mutation):
    edit_yaml(editable_knowledge, "schema/modify.yaml", mutation)
    with pytest.raises(KnowledgeError, match="MODEL_ERROR"):
        build_from(editable_knowledge)


def test_unknown_review_fields_are_null(sources):
    base = next(source.document for source in sources if isinstance(source.document, BaseSpec))
    assert base.provenance.status == "candidate"
    assert base.provenance.verified_by is None
    assert base.provenance.verified_date is None


def test_delta_action_case_is_normalized(sources):
    delta = next(source.document for source in sources if source.path == "schema/modify.yaml")
    assert isinstance(delta, DeltaSpec)
    assert delta.schema_changes[0].action.value == "MODIFY"
