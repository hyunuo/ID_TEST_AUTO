"""Synthetic candidate-source contracts; these fixtures assert no real NVMe values."""

from copy import deepcopy
from hashlib import sha256
import json

import pytest

from ssd_validator.application.candidate_knowledge import (
    apply_candidate_changes,
    build_candidates,
    compile_candidates,
    diff_bundles,
    load_candidates,
)
from ssd_validator.errors import KnowledgeError
from ssd_validator.storage.serialization import canonical_bytes


def anchor(document="TEST.BASE.OLD", page=1):
    return {"document_id": document, "section": "TEST section", "figure": "TEST figure",
            "pdf_page": page, "printed_page": "TEST 1"}


def field(identity="TEST.FLAGS", document="TEST.BASE.OLD", **updates):
    value = {"field_id": identity, "name": identity, "byte_offset": 0,
             "byte_length": 4, "state": "defined", "evidence": [anchor(document)],
             "description": "Synthetic test field", "review_status": "candidate"}
    value.update(updates)
    return value


@pytest.fixture
def candidate_source(tmp_path):
    source, pdfs = tmp_path / "sources", tmp_path / "pdfs"
    source.mkdir()
    pdfs.mkdir()
    documents, structures, requirements = [], [], []
    for component in ("BASE", "NVM"):
        for revision in ("OLD", "NEW"):
            identity = f"TEST.{component}.{revision}"
            filename = f"{identity}.pdf"
            # The compiler verifies registered bytes; PDF parsing is a separate extraction step.
            raw = f"Synthetic document {identity}".encode()
            (pdfs / filename).write_bytes(raw)
            documents.append({"document_id": identity, "component": f"NVME_{component}",
                              "revision": revision, "filename": filename,
                              "sha256": sha256(raw).hexdigest(), "pages": 2,
                              "inherits": f"TEST.{component}.OLD" if revision == "NEW" else None})
            if component == "BASE":
                structures.append({"structure_id": "TEST.CTRL", "document_id": identity,
                                   "cns": 1, "csi": None, "size_bytes": 4,
                                   "fields": [field(document=identity)], "evidence": [anchor(identity)],
                                   "coverage_status": "complete", "unresolved": []})
                requirements.append({"requirement_id": f"TEST.REQ.{revision}", "document_id": identity,
                                     "structure_ids": ["TEST.CTRL"], "field_names": ["TEST.FLAGS"],
                                     "classification": "mandatory", "statement": "TEST flags shall satisfy a condition.",
                                     "condition": "TEST feature enabled", "dependencies": ["TEST feature state"],
                                     "evidence": [anchor(identity)], "review_status": "candidate",
                                     "evaluation_status": "not_executable", "unresolved": []})
    catalog = {"kind": "candidate_catalog", "format_version": 1, "documents": documents,
               "bundles": [{"bundle_id": revision.lower(), "base_document": f"TEST.BASE.{revision}",
                            "nvm_document": f"TEST.NVM.{revision}", "structure_ids": ["TEST.CTRL"]}
                           for revision in ("OLD", "NEW")]}
    structure_data = {"kind": "structure_candidates", "format_version": 1, "structures": structures}
    requirement_data = {"kind": "requirement_candidates", "format_version": 1, "requirements": requirements,
                        "coverage": [{"document_id": "TEST.BASE.OLD", "pdf_page": 2,
                                      "status": "unresolved", "reason": "TEST unreviewed reference"}],
                        "unresolved": ["TEST reference requires review"]}
    structure_data["document_hashes"] = {d["document_id"]: d["sha256"] for d in documents}
    requirement_data["document_hashes"] = dict(structure_data["document_hashes"])

    def save():
        for filename, payload in (("catalog.json", catalog), ("structures.json", structure_data),
                                  ("requirements.json", requirement_data)):
            (source / filename).write_text(json.dumps(payload), encoding="utf-8")

    save()
    return source, pdfs, catalog, structure_data, requirement_data, save


@pytest.mark.parametrize("replacement", ["TEST.ABSENT", "TEST.NVM.OLD"])
def test_bundle_requires_existing_correct_component(candidate_source, replacement):
    source, _, catalog, _, _, save = candidate_source
    catalog["bundles"][0]["base_document"] = replacement
    save()
    with pytest.raises(KnowledgeError, match="BUNDLE_COMPONENT"):
        compile_candidates(source)


def test_document_inheritance_must_stay_within_component(candidate_source):
    source, _, catalog, _, _, save = candidate_source
    catalog["documents"][1]["inherits"] = "TEST.NVM.OLD"
    save()
    with pytest.raises(KnowledgeError, match="DOCUMENT_PARENT"):
        load_candidates(source)


def test_bundle_missing_structure_is_rejected(candidate_source):
    source, _, catalog, _, _, save = candidate_source
    catalog["bundles"][0]["structure_ids"].append("TEST.MISSING")
    save()
    with pytest.raises(KnowledgeError, match="MISSING_STRUCTURE"):
        compile_candidates(source)


@pytest.mark.parametrize("kind", ["field", "nested_bit", "coverage"])
def test_invalid_anchors_are_checked_at_every_depth(candidate_source, kind):
    source, _, _, structures, requirements, save = candidate_source
    first = structures["structures"][0]["fields"][0]
    if kind == "field":
        first["evidence"][0]["document_id"] = "TEST.MISSING"
    elif kind == "nested_bit":
        first["children"] = [field("TEST.CHILD", byte_length=1,
                                   bit_fields=[{"name": "TEST bit", "lsb": 0, "msb": 1,
                                                "state": "defined", "evidence": [anchor(page=3)]}])]
    else:
        requirements["coverage"][0]["pdf_page"] = 3
    save()
    with pytest.raises(KnowledgeError, match="DOCUMENT_ANCHOR"):
        compile_candidates(source)


@pytest.mark.parametrize("target", ["structure", "requirement"])
def test_owner_document_must_appear_in_record_evidence(candidate_source, target):
    source, _, _, structures, requirements, save = candidate_source
    payload = structures["structures"][0] if target == "structure" else requirements["requirements"][0]
    payload["evidence"] = [anchor("TEST.NVM.OLD")]
    save()
    with pytest.raises(KnowledgeError, match="DOCUMENT_ANCHOR"):
        compile_candidates(source)


@pytest.mark.parametrize("status", ["confirmed", "provisional"])
@pytest.mark.parametrize("target", ["field", "requirement"])
def test_extraction_cannot_promote_knowledge(candidate_source, target, status):
    source, _, _, structures, requirements, save = candidate_source
    payload = structures["structures"][0]["fields"][0] if target == "field" else requirements["requirements"][0]
    payload["review_status"] = status
    save()
    with pytest.raises(KnowledgeError, match="CANDIDATE_FORMAT"):
        compile_candidates(source)


def test_partial_structure_exposes_unknown_bytes_and_cannot_claim_complete(candidate_source):
    source, _, _, structures, _, save = candidate_source
    first = structures["structures"][0]
    first["fields"][0].update(byte_offset=1, byte_length=2)
    first["coverage_status"] = "partial"
    save()
    snapshot = compile_candidates(source)[1]["old"]["structures"][0]
    assert [(s["byte_offset"], s["byte_length"], s["state"]) for s in snapshot["segments"]] == [
        (0, 1, "UNKNOWN"), (1, 2, "CANDIDATE"), (3, 1, "UNKNOWN")]
    assert snapshot["coverage_status"] == "partial"
    first["coverage_status"] = "complete"
    save()
    with pytest.raises(KnowledgeError, match="CANDIDATE_FORMAT"):
        compile_candidates(source)


@pytest.mark.parametrize("problem", ["overlap", "outside", "unresolved"])
def test_full_coverage_rejects_false_completeness(candidate_source, problem):
    source, _, _, structures, _, save = candidate_source
    first = structures["structures"][0]
    if problem == "overlap":
        first["fields"].append(field("TEST.OVERLAP", byte_offset=3, byte_length=1))
    elif problem == "outside":
        first["fields"][0]["byte_length"] = 5
    else:
        first["unresolved"] = ["TEST bit meaning not reviewed"]
    save()
    with pytest.raises(KnowledgeError, match="CANDIDATE_FORMAT"):
        compile_candidates(source)


@pytest.mark.parametrize("problem", ["array", "child", "bits_outside", "bits_overlap"])
def test_nested_array_and_bit_boundaries(candidate_source, problem):
    source, _, _, structures, _, save = candidate_source
    first = structures["structures"][0]["fields"][0]
    first["array"] = {"count": 2, "stride_bytes": 2}
    if problem == "array":
        first["array"]["count"] = 3
    elif problem == "child":
        first["children"] = [field("TEST.CHILD", byte_offset=1, byte_length=2)]
    elif problem == "bits_outside":
        first["bit_fields"] = [{"name": "TEST flag", "lsb": 0, "msb": 16,
                                "state": "defined", "evidence": [anchor()]}]
    else:
        first["bit_fields"] = [{"name": f"TEST {start}", "lsb": start, "msb": start + 3,
                                "state": "defined", "evidence": [anchor()]} for start in (0, 3)]
    save()
    with pytest.raises(KnowledgeError, match="CANDIDATE_FORMAT"):
        compile_candidates(source)


def test_valid_array_retains_relative_children_and_multibit_evidence(candidate_source):
    source, _, _, structures, _, save = candidate_source
    first = structures["structures"][0]["fields"][0]
    first["array"] = {"count": 2, "stride_bytes": 2}
    first["children"] = [field("TEST.CHILD", byte_offset=1, byte_length=1,
                               bit_fields=[{"name": "TEST value", "lsb": 2, "msb": 4,
                                            "state": "defined", "evidence": [anchor()]}])]
    save()
    result = compile_candidates(source)[1]["old"]["structures"][0]["definitions"][0]["fields"][0]
    assert result["array"] == {"count": 2, "stride_bytes": 2}
    assert result["children"][0]["byte_offset"] == 1
    assert result["children"][0]["bit_fields"][0]["msb"] == 4


@pytest.mark.parametrize("base_state, expected", [("defined", "CONFLICT"), ("reserved", "CONFLICT"),
                                                  ("delegated", "SUPPLEMENT"), ("unknown", "UNRESOLVED")])
def test_cross_document_overlap_never_silently_selects_winner(candidate_source, base_state, expected):
    source, _, _, structures, _, save = candidate_source
    first = structures["structures"][0]
    first["fields"][0]["state"] = base_state
    supplement = deepcopy(first)
    supplement.update(document_id="TEST.NVM.OLD", evidence=[anchor("TEST.NVM.OLD")])
    supplement["fields"] = [field("TEST.NVM.FLAGS", document="TEST.NVM.OLD")]
    structures["structures"].append(supplement)
    save()
    result = compile_candidates(source)[1]["old"]["structures"][0]
    assert result["segments"][0]["state"] == expected
    assert {d["document_id"] for d in result["definitions"]} == {"TEST.BASE.OLD", "TEST.NVM.OLD"}
    assert len(result["segments"][0]["definitions"]) == 2
    if expected in {"CONFLICT", "UNRESOLVED"}:
        assert result["coverage_status"] == "partial"


def test_reserved_region_does_not_synthesize_zero_requirement(candidate_source):
    source, _, _, structures, _, save = candidate_source
    structures["structures"][0]["fields"][0]["state"] = "reserved"
    save()
    result = compile_candidates(source)[1]["old"]
    assert len(result["requirements"]) == 1
    assert result["requirements"][0]["statement"] == "TEST flags shall satisfy a condition."
    assert not result["authoritative"]


@pytest.mark.parametrize("modality", ["mandatory", "recommendation", "permission", "description", "behavior", "unresolved"])
def test_requirement_modality_conditions_and_evidence_survive(candidate_source, modality):
    source, _, _, _, requirements, save = candidate_source
    original = requirements["requirements"][0]
    original["classification"] = modality
    save()
    result = compile_candidates(source)[1]["old"]["requirements"][0]
    assert {key: result[key] for key in original} == original
    assert result["evaluation_status"] == "not_executable"


def test_hash_verification_is_distinct_from_portable_source_review(candidate_source, tmp_path):
    source, pdfs, catalog, _, _, _ = candidate_source
    assert not compile_candidates(source)[2]["documents_verified"]
    assert compile_candidates(source, pdfs)[2]["documents_verified"]
    (pdfs / catalog["documents"][0]["filename"]).write_bytes(b"changed original")
    with pytest.raises(KnowledgeError, match="DOCUMENT_HASH"):
        build_candidates(source, tmp_path / "candidate", pdfs)
    assert not (tmp_path / "candidate").exists()


@pytest.mark.parametrize("payload_name", ["structures", "requirements"])
def test_extraction_hashes_are_pinned_independently_of_document_catalog(candidate_source, payload_name):
    source, _, _, structures, requirements, save = candidate_source
    payload = structures if payload_name == "structures" else requirements
    payload["document_hashes"]["TEST.BASE.OLD"] = "0" * 64
    save()
    with pytest.raises(KnowledgeError, match="EXTRACTION_HASH"):
        compile_candidates(source)


def test_failed_validation_preserves_previous_build(candidate_source, tmp_path):
    source, pdfs, _, structures, _, save = candidate_source
    output = tmp_path / "candidate"
    build_candidates(source, output, pdfs)
    before = {p.relative_to(output): p.read_bytes() for p in output.rglob("*") if p.is_file()}
    structures["structures"][0]["fields"][0]["byte_length"] = 5
    save()
    with pytest.raises(KnowledgeError):
        build_candidates(source, output, pdfs)
    assert before == {p.relative_to(output): p.read_bytes() for p in output.rglob("*") if p.is_file()}


def test_failed_publish_rolls_back_previous_build(candidate_source, tmp_path, monkeypatch):
    source, pdfs, _, _, _, _ = candidate_source
    output = tmp_path / "candidate"
    build_candidates(source, output, pdfs)
    before = {p.relative_to(output): p.read_bytes() for p in output.rglob("*") if p.is_file()}
    import ssd_validator.storage.artifacts as artifacts

    original_replace = artifacts.os.replace

    def fail_stage_replace(src, dst):
        if src.name.startswith(".knowledge-stage-"):
            raise OSError("TEST publishing failure")
        return original_replace(src, dst)

    monkeypatch.setattr(artifacts.os, "replace", fail_stage_replace)
    with pytest.raises(OSError, match="TEST publishing failure"):
        build_candidates(source, output, pdfs)
    assert before == {p.relative_to(output): p.read_bytes() for p in output.rglob("*") if p.is_file()}


def test_unmanaged_output_cannot_be_overwritten(candidate_source, tmp_path):
    source, pdfs, _, _, _, _ = candidate_source
    output = tmp_path / "candidate"
    output.mkdir()
    marker = output / "human-notes.txt"
    marker.write_text("keep me", encoding="utf-8")
    with pytest.raises(KnowledgeError, match="UNSAFE_OUTPUT"):
        build_candidates(source, output, pdfs)
    assert marker.read_text(encoding="utf-8") == "keep me"


@pytest.mark.parametrize("where", ["source_child", "pdf_directory", "wrong_name"])
def test_output_cannot_replace_inputs_or_escape_candidate_namespace(candidate_source, tmp_path, where):
    source, pdfs, _, _, _, _ = candidate_source
    output = {"source_child": source / "candidate", "pdf_directory": pdfs,
              "wrong_name": tmp_path / "production"}[where]
    expected = "CANDIDATE_OUTPUT" if where == "wrong_name" else "SOURCE_OUTPUT_OVERLAP"
    with pytest.raises(KnowledgeError, match=expected):
        build_candidates(source, output, pdfs)
    assert (source / "catalog.json").exists()


def test_generated_directory_cannot_be_source(candidate_source, tmp_path):
    source, _, _, _, _, _ = candidate_source
    generated = tmp_path / "generated"
    source.rename(generated)
    with pytest.raises(KnowledgeError, match="GENERATED_IS_NOT_SOURCE"):
        compile_candidates(generated)


def test_duplicate_json_keys_are_not_last_write_wins(candidate_source):
    source, _, _, _, _, _ = candidate_source
    (source / "catalog.json").write_text('{"kind":"candidate_catalog","kind":"other"}', encoding="utf-8")
    with pytest.raises(KnowledgeError, match="DUPLICATE_CANDIDATE"):
        compile_candidates(source)


def test_build_content_is_deterministic_and_diff_keeps_both_requirement_sets(candidate_source, tmp_path):
    source, pdfs, _, structures, requirements, save = candidate_source
    structures["structures"][1]["fields"][0]["description"] = "TEST changed meaning"
    requirements["requirements"][1]["classification"] = "permission"
    save()
    first = compile_candidates(source, pdfs)
    second = compile_candidates(source, pdfs)
    assert canonical_bytes(first[1]) == canonical_bytes(second[1])
    assert canonical_bytes(first[2]) == canonical_bytes(second[2])
    difference = diff_bundles(first[1]["old"], first[1]["new"])
    assert len(difference["schema_changes"]) == 1
    change = difference["schema_changes"][0]
    assert change["previous"]["description"] == "Synthetic test field"
    assert change["current"]["description"] == "TEST changed meaning"
    assert difference["requirements"]["previous"][0]["classification"] == "mandatory"
    assert difference["requirements"]["current"][0]["classification"] == "permission"
    assert difference["requirements"]["comparison_status"] == "REVIEW"
    parent = {change["target"]: change["previous"]}
    assert apply_candidate_changes(parent, [change]) == {change["target"]: change["current"]}
    assert parent[change["target"]] == change["previous"]
    output = tmp_path / "candidate"
    build_candidates(source, output, pdfs)
    assert json.loads((output / "diffs/old--new.json").read_bytes()) == difference


def test_revision_only_evidence_changes_do_not_imply_layout_changes(candidate_source):
    source, _, _, _, _, _ = candidate_source
    bundles = compile_candidates(source)[1]
    assert diff_bundles(bundles["old"], bundles["new"])["schema_changes"] == []


@pytest.mark.parametrize("property_name,new_value", [("cns", 5), ("csi", 0), ("size_bytes", 8)])
def test_structure_identity_changes_are_reported_even_when_fields_match(candidate_source, property_name, new_value):
    source, _, _, structures, _, save = candidate_source
    structures["structures"][1][property_name] = new_value
    if property_name == "size_bytes":
        structures["structures"][1]["coverage_status"] = "partial"
    save()
    bundles = compile_candidates(source)[1]
    changes = diff_bundles(bundles["old"], bundles["new"])["schema_changes"]
    change = next(c for c in changes if c["target"] == "STRUCTURE:TEST.CTRL")
    assert change["current"][property_name] == new_value
    assert change["previous"][property_name] != new_value


def test_requirement_cannot_target_structure_only_in_other_bundle(candidate_source):
    source, _, catalog, structures, requirements, save = candidate_source
    extra = deepcopy(structures["structures"][1])
    extra["structure_id"] = "TEST.NEW_ONLY"
    structures["structures"].append(extra)
    catalog["bundles"][1]["structure_ids"].append("TEST.NEW_ONLY")
    requirements["requirements"][0]["structure_ids"] = ["TEST.NEW_ONLY"]
    save()
    with pytest.raises(KnowledgeError, match="UNKNOWN_STRUCTURE"):
        compile_candidates(source)


def test_unresolved_external_field_reference_is_visible(candidate_source):
    source, _, _, _, requirements, save = candidate_source
    requirements["requirements"][0]["field_names"].append("TEST external feature state")
    save()
    result = compile_candidates(source)[1]["old"]["requirements"][0]
    links = {link["name"]: link for link in result["field_links"]}
    assert links["TEST.FLAGS"]["status"] == "CANDIDATE"
    assert links["TEST external feature state"] == {"name": "TEST external feature state",
                                                    "status": "UNRESOLVED", "matches": []}
    assert result["evaluation_status"] == "not_executable"


def test_field_links_respect_response_scope_and_find_nested_fields(candidate_source):
    source, _, catalog, structures, requirements, save = candidate_source
    structures["structures"][0]["fields"][0]["children"] = [field("TEST.CHILD", byte_length=1)]
    unrelated = deepcopy(structures["structures"][0])
    unrelated.update(structure_id="TEST.OTHER", cns=5)
    unrelated["fields"] = [field("TEST.UNRELATED")]
    structures["structures"].append(unrelated)
    catalog["bundles"][0]["structure_ids"].append("TEST.OTHER")
    requirements["requirements"][0]["field_names"] = ["TEST.CHILD", "TEST.UNRELATED"]
    save()
    result = compile_candidates(source)[1]["old"]["requirements"][0]
    links = {link["name"]: link for link in result["field_links"]}
    assert links["TEST.CHILD"]["status"] == "CANDIDATE"
    assert links["TEST.CHILD"]["matches"][0]["structure_id"] == "TEST.CTRL"
    assert links["TEST.UNRELATED"]["status"] == "UNRESOLVED"


def test_multiple_textual_field_matches_remain_ambiguous(candidate_source):
    source, _, _, structures, _, save = candidate_source
    other = deepcopy(structures["structures"][0])
    other.update(document_id="TEST.NVM.OLD", evidence=[anchor("TEST.NVM.OLD")])
    other["fields"] = [field(document="TEST.NVM.OLD")]
    structures["structures"].append(other)
    save()
    link = compile_candidates(source)[1]["old"]["requirements"][0]["field_links"][0]
    assert link["status"] == "AMBIGUOUS"
    assert len(link["matches"]) == 2


def test_missing_page_coverage_remains_visible_and_duplicates_are_rejected(candidate_source, tmp_path):
    source, pdfs, _, _, requirements, save = candidate_source
    output = tmp_path / "candidate"
    build_candidates(source, output, pdfs)
    report = json.loads((output / "review.json").read_bytes())
    assert report["pages_missing_coverage"]["TEST.BASE.OLD"] == [1]
    assert report["pages_missing_coverage"]["TEST.NVM.NEW"] == [1, 2]
    requirements["coverage"].append(deepcopy(requirements["coverage"][0]))
    save()
    with pytest.raises(KnowledgeError, match="DUPLICATE_CANDIDATE"):
        compile_candidates(source)


def test_nested_template_diff_uses_explicit_document_identity(candidate_source):
    source, _, _, structures, _, save = candidate_source
    templates = []
    for structure in structures["structures"]:
        doc = structure["document_id"]
        identity = f"{doc}.TEST_ARRAY_ELEMENT"
        structure["fields"][0].update(array={"count": 2, "stride_bytes": 2}, nested_template_id=identity)
        templates.append({"template_id": identity, "size_bytes": 2,
                          "coordinate_system": "TEST element-relative bits", "source_rows": [],
                          "bit_fields": [{"name": "TEST value", "lsb": 0, "msb": 15,
                                          "state": "defined", "evidence": [anchor(doc)]}],
                          "evidence": [anchor(doc)], "review_status": "candidate", "coverage_status": "complete"})
    templates[1]["bit_fields"][0]["name"] = "TEST revised meaning"
    structures["nested_templates"] = templates
    save()
    bundles = compile_candidates(source)[1]
    assert len(bundles["old"]["nested_templates"]) == 1
    changes = diff_bundles(bundles["old"], bundles["new"])["schema_changes"]
    change = next(change for change in changes if change["target"] == "TEMPLATE:BASE:TEST_ARRAY_ELEMENT")
    assert change["action"] == "MODIFY"
    assert change["previous"]["bit_fields"][0]["name"] == "TEST value"
    assert change["current"]["bit_fields"][0]["name"] == "TEST revised meaning"


@pytest.mark.parametrize("case", ["guard", "duplicate", "add_existing", "remove_missing", "bool_guard"])
def test_candidate_delta_replay_rejects_stale_or_ambiguous_changes(case):
    parent = {"TEST.FIELD": {"value": 1}}
    changes = [{"target": "TEST.FIELD", "action": "MODIFY", "previous": {"value": 1}, "current": {"value": 2}}]
    expected = "INVALID_DELTA"
    if case == "guard":
        changes[0]["previous"] = {"value": 99}
        expected = "GUARD_MISMATCH"
    elif case == "duplicate":
        changes.append(deepcopy(changes[0]))
        expected = "DUPLICATE_TARGET"
    elif case == "add_existing":
        changes[0].update(action="ADD", previous=None)
    elif case == "remove_missing":
        changes[0].update(action="REMOVE", target="TEST.MISSING", current=None)
    else:
        changes[0]["previous"] = {"value": True}
        expected = "GUARD_MISMATCH"
    with pytest.raises(KnowledgeError, match=expected):
        apply_candidate_changes(parent, changes)
    assert parent == {"TEST.FIELD": {"value": 1}}
