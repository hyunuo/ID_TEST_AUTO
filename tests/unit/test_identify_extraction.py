"""Source-read regression anchors for shipped, explicitly unapproved candidates.

These tests intentionally need neither the private/local PDFs nor a PDF library.
They protect modality/context and known layout observations, not spec approval.
"""
import importlib.util
from pathlib import Path

import pytest

from ssd_validator.application.candidate_knowledge import compile_candidates


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "identify_requirement_extractor", ROOT / "tools" / "extract_identify_requirements.py"
)
EXTRACTOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EXTRACTOR)


@pytest.fixture(scope="module")
def compiled():
    return compile_candidates(ROOT / "candidates" / "nvme")


@pytest.fixture(scope="module")
def curated(compiled):
    return {r.requirement_id: r for r in compiled[3].requirements if ".CURATED." in r.requirement_id}


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("The controller shall report the field.", "mandatory"),
        ("The controller may report the field.", "permission"),
        ("The host should use this value.", "recommendation"),
        ("The controller shall support A and may support B.", "unresolved"),
        ("The host should use A; the controller shall report B.", "unresolved"),
        ("Bits 7:5 are reserved.", "description"),
    ],
)
def test_lexical_triage_preserves_modality_without_making_rules(text, expected):
    assert EXTRACTOR.classify(text) == expected


@pytest.mark.parametrize("document", ["NVM_1_0E", "NVM_1_1"])
def test_thinp_capacity_obligation_is_not_utilization_obligation(curated, document):
    capacity = curated[f"{document}.CURATED.THINP_ZERO_NCAP"]
    utilization = curated[f"{document}.CURATED.THINP_ZERO_NUSE_PERMISSION"]
    assert capacity.classification == "mandatory"
    assert utilization.classification == "permission"
    assert capacity.condition == utilization.condition == "THINP is cleared to 0"
    assert "shall" in capacity.statement
    assert "may" in utilization.statement
    assert "NUSE" not in capacity.field_names
    assert "NUSE" in utilization.field_names
    ordering = curated[f"{document}.CURATED.CAPACITY_ORDER"]
    assert ordering.statement == "Namespace Size >= Namespace Capacity >= Namespace Utilization."
    assert set(ordering.field_names) == {"NSZE", "NCAP", "NUSE"}


def test_no_namespace_management_abort_changes_from_shall_to_may(curated):
    old = curated["NVM_1_0E.CURATED.ALL_NS_UNSUPPORTED"]
    new = curated["NVM_1_1.CURATED.ALL_NS_UNSUPPORTED"]
    assert old.condition == new.condition
    assert "FFFFFFFFh" in old.condition
    assert "shall abort" in old.statement
    assert "may abort" in new.statement
    assert new.classification == "permission"
    assert (old.evidence[0].pdf_page, new.evidence[0].pdf_page) == (56, 80)
    assert old.evidence[0].document_id != new.evidence[0].document_id


@pytest.mark.parametrize("suffix", ["AWUPF_BOUND", "NAWUN_BASELINE"])
def test_new_atomicity_mode_applicability_survives_version_comparison(curated, suffix):
    old = curated[f"NVM_1_0E.CURATED.{suffix}"]
    new = curated[f"NVM_1_1.CURATED.{suffix}"]
    assert old.statement == new.statement
    assert "supported" in old.condition and "supported" in new.condition
    assert "Single Atomicity Mode" not in old.condition
    assert "Single Atomicity Mode" in new.condition
    assert "Atomicity mode" in new.dependencies
    assert old.evidence[0].section == "2.1.4"
    assert new.evidence[0].section == "2.1.4.1"


def test_ana_rule_retains_runtime_dependency_instead_of_constant_expected(curated):
    for document in ("NVM_1_0E", "NVM_1_1"):
        rule = curated[f"{document}.CURATED.ANA_ZERO_REPORTING"]
        assert "ANA Inaccessible" in rule.condition
        assert "ANA Persistent Loss" in rule.condition
        assert "Current controller/namespace ANA state" in rule.dependencies
        assert set(rule.field_names) == {"CMIC", "NUSE", "NVMCAP"}
        assert rule.evaluation_status == "unresolved"


def test_shipped_curated_data_matches_source_read_extractor():
    # Protect manually curated text from diverging from reproducible extraction.
    import json

    shipped = json.loads((ROOT / "candidates/nvme/requirements.json").read_text(encoding="utf-8"))
    by_id = {r["requirement_id"]: r for r in shipped["requirements"]}
    for candidate in EXTRACTOR.focused_candidates():
        assert by_id[candidate["requirement_id"]] == candidate


def test_catalog_has_independent_components_and_explicit_pairs(compiled):
    catalog, bundles, manifest, _ = compiled
    assert {(b.base_document, b.nvm_document) for b in catalog.bundles} == {
        ("BASE_2_0E", "NVM_1_0E"), ("BASE_2_1", "NVM_1_1")
    }
    documents = {d.document_id: d for d in catalog.documents}
    assert documents["BASE_2_1"].inherits == "BASE_2_0E"
    assert documents["NVM_1_1"].inherits == "NVM_1_0E"
    assert manifest["documents_verified"] is False
    assert manifest["authoritative"] is False
    for snapshot in bundles.values():
        assert snapshot["review_status"] == "candidate"
        assert snapshot["authoritative"] is False
        assert {s["cns"] for s in snapshot["structures"]} == {0, 1, 5, 6, 8}


def test_shipped_requirement_source_hashes_are_bound_to_registry(compiled):
    catalog, _, _, requirements = compiled
    assert requirements.document_hashes == {d.document_id: d.sha256 for d in catalog.documents}


@pytest.mark.parametrize("relative", ["generated/requirements.json", "GENERATED/requirements.json", "result.pdf"])
def test_extractor_refuses_generated_or_pdf_outputs(tmp_path, relative):
    with pytest.raises(ValueError):
        EXTRACTOR.validate_output(tmp_path / relative, tmp_path)


def test_extractor_refuses_registry_overwrite(tmp_path):
    registry = tmp_path / "catalog.json"
    with pytest.raises(ValueError):
        EXTRACTOR.validate_output(registry, tmp_path, registry)
    EXTRACTOR.validate_output(tmp_path / "candidates" / "requirements.json", tmp_path, registry)


def test_source_pin_failure_precedes_pdf_parsing(tmp_path):
    import hashlib
    import json

    entries = []
    for identity, filename in EXTRACTOR.DOCUMENTS.items():
        content = b"fixture bytes; deliberately not a real PDF"
        (tmp_path / filename).write_bytes(content)
        entries.append({"document_id": identity, "filename": filename,
                        "sha256": hashlib.sha256(content).hexdigest()})
    registry = tmp_path / "catalog.json"
    registry.write_text(json.dumps({"documents": entries}), encoding="utf-8")
    assert EXTRACTOR.source_hashes(tmp_path, registry) == {e["document_id"]: e["sha256"] for e in entries}
    (tmp_path / entries[0]["filename"]).write_bytes(b"replaced source")
    # A parser would reject all four fixtures. A hash error proves it never gets
    # that far and fixed page offsets cannot be applied to these changed bytes.
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        EXTRACTOR.extract(tmp_path, registry)


def test_namespace_layout_anchors_from_figures_97_and_114(compiled):
    # These offsets/lengths were read in the supplied source figures, not invented
    # TEST values. They remain candidate knowledge despite regression protection.
    for snapshot in compiled[1].values():
        namespace = next(s for s in snapshot["structures"] if s["structure_id"] == "NVME.CNS00")
        definition = next(d for d in namespace["definitions"] if d["document_id"].startswith("NVM_"))
        fields = {f["field_id"].split(".")[-1]: f for f in definition["fields"]}
        for name, offset, length in [("NSZE", 0, 8), ("NCAP", 8, 8), ("NUSE", 16, 8), ("NSFEAT", 24, 1)]:
            assert (fields[name]["byte_offset"], fields[name]["byte_length"]) == (offset, length)
            assert fields[name]["review_status"] == "candidate"
            assert all(e["document_id"] == definition["document_id"] for e in fields[name]["evidence"])


def test_identify_controller_preserves_base_and_nvm_source_definitions(compiled):
    for snapshot in compiled[1].values():
        controller = next(s for s in snapshot["structures"] if s["structure_id"] == "NVME.CNS01")
        sources = {d["document_id"] for d in controller["definitions"]}
        assert sources == {snapshot["bundle"]["base_document"], snapshot["bundle"]["nvm_document"]}
        nvm = next(d for d in controller["definitions"] if d["document_id"] == snapshot["bundle"]["nvm_document"])
        awun = next(f for f in nvm["fields"] if f["field_id"].endswith(".AWUN"))
        assert (awun["byte_offset"], awun["byte_length"]) == (526, 2)


def test_every_page_is_accounted_for_without_claiming_semantic_completion(compiled):
    catalog, _, _, requirements = compiled
    seen = [(e.document_id, e.pdf_page) for e in requirements.coverage]
    assert len(seen) == len(set(seen))
    expected = {(d.document_id, p) for d in catalog.documents for p in range(1, d.pages + 1)}
    assert set(seen) == expected
    assert all(e.status in {"excluded", "unresolved"} and e.reason for e in requirements.coverage)
    by_page = {(e.document_id, e.pdf_page): e for e in requirements.coverage}
    for doc, ranges in EXTRACTOR.CORE.items():
        for first, last, _, _ in ranges:
            assert all(by_page[doc, p].status == "unresolved" for p in range(first, last + 1))


def test_all_requirements_are_candidates_with_no_executable_expectations(compiled):
    requirements = compiled[3]
    assert requirements.unresolved
    ids = [r.requirement_id for r in requirements.requirements]
    assert len(ids) == len(set(ids))
    for rule in requirements.requirements:
        assert rule.review_status == "candidate"
        assert rule.evaluation_status in {"not_executable", "unresolved"}
        assert rule.unresolved
        assert any(e.document_id == rule.document_id for e in rule.evidence)
        assert "expected" not in rule.model_dump()


def test_nested_templates_keep_element_bounds_and_review_limitations(compiled):
    for snapshot in compiled[1].values():
        templates = {t["template_id"]: t for t in snapshot["nested_templates"]}
        assert templates
        for template in templates.values():
            assert template["review_status"] == "candidate"
            assert template["evidence"]
            occupied = set()
            for bit in template["bit_fields"]:
                assert 0 <= bit["lsb"] <= bit["msb"] < template["size_bytes"] * 8
                indices = set(range(bit["lsb"], bit["msb"] + 1))
                assert not occupied & indices
                occupied |= indices
        for structure in snapshot["structures"]:
            for definition in structure["definitions"]:
                if definition["unresolved"]:
                    assert definition["coverage_status"] == "partial"
                for field in definition["fields"]:
                    identity = field.get("nested_template_id")
                    if identity:
                        assert field["array"]["stride_bytes"] == templates[identity]["size_bytes"]
                        assert field["array"]["count"] * field["array"]["stride_bytes"] <= field["byte_length"]
