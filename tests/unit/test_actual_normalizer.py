"""Synthetic version mismatches; no real 2.3 release or SSD policy is asserted."""

import json
from hashlib import sha256
from pathlib import Path

import pytest
from pydantic import ValidationError

from ssd_validator.analyzer.actual_normalizer import evaluate_normalized, layout_from_profile, normalize_json, normalize_raw
from ssd_validator.application.normalize_actual import run_normalization
from ssd_validator.application.rule_pilot import run_pilot
from ssd_validator.errors import KnowledgeError
from ssd_validator.models.actual_data import CaptureMetadata, IdentifyQuery, NormalizationLayout, WireField
from ssd_validator.resolver import evaluate

ROOT = Path(__file__).parents[1] / "fixtures" / "actual_normalization"
PILOT = ROOT.parent / "rule_pilot"


@pytest.fixture
def inputs():
    layout = NormalizationLayout.model_validate_json((ROOT / "layout.json").read_text(encoding="utf-8"))
    capture = CaptureMetadata.model_validate_json((ROOT / "capture.json").read_text(encoding="utf-8"))
    return layout, capture, (ROOT / "response.raw").read_bytes()


def test_newer_tool_and_advertised_version_never_select_target_spec(inputs):
    layout, capture, raw = inputs
    old = normalize_raw(layout, capture.model_copy(update={"tool_version": "TEST.old", "advertised_nvme_version": "TEST.old"}), raw)
    new = normalize_raw(layout, capture.model_copy(update={"tool_version": "TEST.new", "advertised_nvme_version": "TEST.new"}), raw)
    assert old.layout == new.layout == layout
    assert old.fields == new.fields
    assert [f.value for f in new.actual_facts] == [80, 12, 0, 100, 40]
    assert new.status == "OBSERVED"  # Never a device PASS verdict.


def test_raw_bytes_and_source_hash_are_losslessly_preserved(inputs):
    layout, capture, raw = inputs
    report = normalize_raw(layout, capture, raw)
    reconstructed = bytearray(len(raw))
    for item in report.fields:
        reconstructed[item.definition.offset:item.definition.offset + item.definition.length] = bytes.fromhex(item.raw_hex)
    for item in report.unmapped_bytes:
        reconstructed[item.offset:item.offset + item.length] = bytes.fromhex(item.raw_hex)
        assert item.state == "unmapped"
    assert bytes(reconstructed) == raw
    assert report.source.sha256 == sha256(raw).hexdigest()
    assert all(f.source == report.source and f.capture_id == capture.capture_id for f in report.actual_facts)


def test_selected_layout_semantics_override_latest_tool_labels(inputs):
    layout, capture, raw = inputs
    definition = layout.fields[0].model_dump()
    definition.update(field={"field_id": "TEST.OLDER_RESERVED"}, offset=100, length=1, semantic_state="reserved", json_path=["latest_feature"])
    older = WireField.model_validate(definition)
    old_layout = layout.model_copy(update={"fields": (older,)})
    newer = older.model_copy(update={"semantic_state": "defined"})
    new_layout = layout.model_copy(update={"bundle_id": "TEST.newer-bundle", "fields": (newer,)})
    old_report = normalize_raw(old_layout, capture, raw)
    new_report = normalize_raw(new_layout, capture, raw)
    assert old_report.fields[0].definition.semantic_state == "reserved"
    assert new_report.fields[0].definition.semantic_state == "defined"
    assert old_report.fields[0].value == new_report.fields[0].value == 0xa5
    assert old_report.status == "OBSERVED"  # Reserved is not an implicit zero check.
    json_report = normalize_json(old_layout, capture, {"latest_feature": 0xa5})
    assert json_report.fields[0].definition.semantic_state == "reserved"


@pytest.mark.parametrize("length", [0, 4095, 4097])
def test_invalid_raw_length_is_error_not_padded_or_truncated(inputs, length):
    layout, capture, _ = inputs
    report = normalize_raw(layout, capture, bytes(length))
    assert report.status == "ERROR"
    assert not report.actual_facts and not report.fields
    assert "no padding/truncation" in report.errors[0]


@pytest.mark.parametrize("change", [{"cns": 1}, {"csi": 1}, {"nsid": 2}, {"controller_id": 1}])
def test_query_identity_is_exact(inputs, change):
    layout, capture, raw = inputs
    capture = capture.model_copy(update={"query": capture.query.model_copy(update=change)})
    assert normalize_raw(layout, capture, raw).status == "ERROR"
    assert normalize_json(layout, capture, {}).status == "ERROR"


def test_missing_json_is_unknown_and_extra_latest_keys_are_preserved(inputs):
    layout, capture, _ = inputs
    payload = json.loads((ROOT / "response.json").read_text(encoding="utf-8"))
    good = normalize_json(layout, capture, payload)
    assert good.status == "OBSERVED"
    assert good.unmapped_json_keys == ("test_newer_only_feature",)
    assert good.tool_output["test_newer_only_feature"] == 999
    del payload["test_capacity"]
    payload["test_formats"] = [{"size": 12}]
    missing = normalize_json(layout, capture, payload)
    missing_fields = {f.definition.field.key for f in missing.fields if f.status == "UNKNOWN"}
    assert missing_fields == {"TEST.CAPACITY", "TEST.LBADS[1]"}
    assert "TEST.CAPACITY" not in {f.field.key for f in missing.actual_facts}
    assert missing.status == "UNKNOWN"


@pytest.mark.parametrize("value", [True, "100", -1, 65536, None])
def test_json_types_not_coerced(inputs, value):
    layout, capture, _ = inputs
    report = normalize_json(layout, capture, {"test_size": value})
    field = next(f for f in report.fields if f.definition.field.field_id == "TEST.SIZE")
    assert field.status == "ERROR"
    assert report.status == "ERROR"


def test_json_path_shape_errors_and_no_implicit_aliases(inputs):
    layout, capture, _ = inputs
    report = normalize_json(layout, capture, {"test_formats": {"0": {"size": 12}}})
    assert report.status == "ERROR"
    fields = tuple(f.model_copy(update={"json_path": None}) for f in layout.fields)
    report = normalize_json(layout.model_copy(update={"fields": fields}), capture, {"TEST.SIZE": 100})
    assert report.status == "UNKNOWN"
    assert not report.actual_facts


def test_candidate_or_unconfirmed_layout_never_feeds_authoritative_facts(inputs):
    layout, capture, raw = inputs
    report = normalize_raw(layout.model_copy(update={"data_kind": "candidate"}), capture, raw)
    assert report.status == "REVIEW"
    assert not report.actual_facts
    assert all(f.value is not None for f in report.fields)
    fields = tuple(f.model_copy(update={"provenance": f.provenance.model_copy(update={"status": "provisional"})}) for f in layout.fields)
    report = normalize_raw(layout.model_copy(update={"fields": fields}), capture, raw)
    assert report.status == "REVIEW" and not report.actual_facts


def test_layout_guard_overlap_bounds_bit_paths_and_review_metadata(inputs):
    layout, _, _ = inputs
    data = layout.model_dump()
    data["fields"][1]["offset"] = 0
    with pytest.raises(ValidationError, match="Overlapping"):
        NormalizationLayout.model_validate(data)
    data = layout.model_dump()
    data["fields"][0]["offset"] = 4096
    with pytest.raises(ValidationError, match="out-of-bounds"):
        NormalizationLayout.model_validate(data)
    data = layout.fields[0].model_dump()
    data["field"]["bit"] = 0
    with pytest.raises(ValidationError, match="whole fields"):
        WireField.model_validate(data)
    data = layout.model_dump()
    data["fields"][0]["provenance"]["verified_date"] = None
    with pytest.raises(ValidationError, match="reviewer"):
        NormalizationLayout.model_validate(data)


def test_profile_reuses_builder_layout_and_raw_facts_reach_resolver():
    profile = run_pilot(PILOT / "knowledge", PILOT / "input.json").profile
    ns_query = IdentifyQuery(cns=0, csi=0, nsid=1)
    with pytest.raises(KnowledgeError, match="ARRAY_STRIDE_REQUIRED"):
        layout_from_profile(profile, ns_query, response_size=4096)
    ns_layout = layout_from_profile(profile, ns_query, response_size=4096, array_strides={"TEST.LBADS": 1})
    capture = CaptureMetadata(capture_id="TEST.raw.ns", tool_name="TEST.CLI", tool_version="TEST.latest", device_id="TEST.DUT", query=ns_query)
    ns_report = normalize_raw(ns_layout, capture, (ROOT / "response.raw").read_bytes())
    ctrl_query = IdentifyQuery(cns=1, csi=0)
    ctrl_layout = layout_from_profile(profile, ctrl_query, response_size=4096)
    ctrl_raw = bytearray(4096)
    ctrl_raw[0] = 1
    ctrl_raw[1:3] = (10).to_bytes(2, "little")
    ctrl_raw[3:5] = (5).to_bytes(2, "little")
    ctrl_report = normalize_raw(ctrl_layout, capture.model_copy(update={"capture_id": "TEST.raw.ctrl", "query": ctrl_query}), bytes(ctrl_raw))
    report = evaluate(profile, (*ns_report.actual_facts, *ctrl_report.actual_facts))
    assert report.status == "PASS"
    assert all(f.source and f.capture_id for f in report.actual_facts)
    assert all(d.definition.history[0].source_hash for d in ns_report.fields)
    combined = evaluate_normalized(profile, (ns_report, ctrl_report))
    assert combined.status == "PASS"
    assert combined.validation.actual_facts == report.actual_facts
    bad_tool_input = normalize_raw(ns_layout, capture, b"\x00")
    assert evaluate_normalized(profile, (bad_tool_input, ctrl_report)).status == "ERROR"
    other_device = ns_report.model_copy(update={"capture": capture.model_copy(update={"device_id": "TEST.other-device"})})
    assert evaluate_normalized(profile, (other_device, ctrl_report)).status == "ERROR"
    assert evaluate_normalized(profile, (ns_report, ns_report)).status == "ERROR"
    other_bundle = ns_report.model_copy(update={"layout": ns_layout.model_copy(update={"base_revision": "TEST.other-version"})})
    assert evaluate_normalized(profile, (other_bundle, ctrl_report)).status == "ERROR"
    ctx = profile.context.model_copy(update={"facts": {"namespace.nsid": 2}})
    assert evaluate_normalized(profile.model_copy(update={"context": ctx}), (ns_report, ctrl_report)).status == "ERROR"
    unknown = normalize_json(ns_layout, capture, {})
    assert evaluate(profile, (*unknown.actual_facts, *ctrl_report.actual_facts)).status == "UNKNOWN"
    assert evaluate_normalized(profile, (unknown, ctrl_report)).status == "UNKNOWN"


def test_big_endian_ascii_and_opaque_bytes(inputs):
    layout, capture, _ = inputs
    original = layout.fields[0]
    big = original.model_copy(update={"endian": "big"})
    short = layout.model_copy(update={"response_size": 2, "fields": (big,)})
    assert normalize_raw(short, capture, b"\x01\x02").fields[0].value == 258
    string = big.model_copy(update={"value_type": "string", "endian": "not_applicable"})
    short = short.model_copy(update={"fields": (string,)})
    assert normalize_raw(short, capture, b"A ").fields[0].value == "A"
    assert normalize_raw(short, capture, b"\xff\x00").status == "ERROR"
    opaque = string.model_copy(update={"value_type": "bytes"})
    short = short.model_copy(update={"fields": (opaque,)})
    report = normalize_raw(short, capture, b"\xff\x00")
    assert report.fields[0].value == "ff00"
    assert not report.actual_facts


def test_file_inputs_pinned_and_no_automatic_raw_json_fallback():
    report = run_normalization(ROOT / "layout.json", ROOT / "capture.json", raw_path=ROOT / "response.raw")
    assert report.layout_source.sha256 == sha256((ROOT / "layout.json").read_bytes()).hexdigest()
    assert report.capture_source.sha256 == sha256((ROOT / "capture.json").read_bytes()).hexdigest()
    with pytest.raises(KnowledgeError, match="ACTUAL_INPUT"):
        run_normalization(ROOT / "layout.json", ROOT / "capture.json", raw_path=ROOT / "response.raw", json_path=ROOT / "response.json")


def test_duplicate_keys_and_nonstandard_json_numbers_rejected(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text('{"test_size": 1, "test_size": 2}', encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate"):
        run_normalization(ROOT / "layout.json", ROOT / "capture.json", json_path=path)
    path.write_text('{"test_size": NaN}', encoding="utf-8")
    with pytest.raises(ValueError, match="Non-JSON"):
        run_normalization(ROOT / "layout.json", ROOT / "capture.json", json_path=path)
