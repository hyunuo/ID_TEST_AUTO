"""Collect review-only Identify requirement passages; never emit executable rules.

Usage: python tools/extract_identify_requirements.py --pdf-dir ../
Requires pypdfium2 (available in the bundled Codex Python runtime).
The output deliberately retains unresolved context and table-layout limitations.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


DOCUMENTS = {
    "BASE_2_0E": "NVM-Express-Base-Specification-2.0e-2024.07.29-Ratified.pdf",
    "BASE_2_1": "NVM-Express-Base-Specification-Revision-2.1-2024.08.05-Ratified.pdf",
    "NVM_1_0E": "NVM-Express-NVM-Command-Set-Specification-1.0e-2024.07.29-Ratified.pdf",
    "NVM_1_1": "NVM-Express-NVM-Command-Set-Specification-Revision-1.1-2024.08.05-Ratified.pdf",
}
CATALOG = Path(__file__).resolve().parents[1] / "candidates" / "nvme" / "catalog.json"
# Inclusive physical PDF pages, verified against source headings. Shared boundary
# pages intentionally name both structures and require passage-level review.
CORE = {
    "BASE_2_0E": [(262, 288, "01", "5.17.2.1"), (291, 291, "05", "5.17.2.5"),
                   (291, 291, "06", "5.17.2.6"), (291, 294, "08", "5.17.2.8")],
    "BASE_2_1": [(321, 353, "01", "5.1.13.2.1"), (355, 356, "05", "5.1.13.2.5"),
                  (356, 356, "06", "5.1.13.2.6"), (356, 360, "08", "5.1.13.2.8")],
    "NVM_1_0E": [(56, 65, "00", "4.1.5.1"), (65, 66, "01", "4.1.5.2"),
                  (66, 68, "05", "4.1.5.3"), (68, 70, "06", "4.1.5.4")],
    "NVM_1_1": [(79, 90, "00", "4.1.5.1"), (90, 92, "01", "4.1.5.2"),
                 (92, 98, "05", "4.1.5.3"), (98, 103, "06", "4.1.5.4")],
}
IDENTIFY = re.compile(r"Identify\s+(?:Controller|Namespace)|(?:I/O Command Set|Command Set)\s+(?:Independent|specific)\s+Identify", re.I)
ACRONYM = re.compile(r"\(([A-Z][A-Z0-9_]{1,15})\)")
REFERENCE = re.compile(r"\b(?:section|Figure)\s+\d+(?:\.\d+)*", re.I)
MODAL = re.compile(r"\b(?:shall|must|should|may|required|reserved)\b", re.I)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def classify(statement: str) -> str:
    """Conservative lexical triage, not a semantic or normative decision."""
    modes = []
    if re.search(r"\b(?:shall|must)\b", statement, re.I):
        modes.append("mandatory")
    if re.search(r"\b(?:should|recommended)\b", statement, re.I):
        modes.append("recommendation")
    if re.search(r"\bmay\b", statement, re.I):
        modes.append("permission")
    return modes[0] if len(modes) == 1 else "unresolved" if modes else "description"


def passages(text: str) -> list[str]:
    # Keep source wording, punctuation, tables and modality; do not paraphrase or
    # manufacture expressions. Adjacent sentences provide conservative context.
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z•])", normalize(text))
    result: list[str] = []
    current = ""
    for sentence in sentences:
        if current and len(current) + len(sentence) > 1700:
            result.append(current)
            current = ""
        current = (current + " " + sentence).strip()
    if current:
        result.append(current)
    return result


def focused_candidates() -> list[dict]:
    """Small source-read pilot alongside the broad, mechanically collected queue.

    These interpretations still require independent human review. They are not
    promoted by inclusion here and do not establish reference closure.
    """
    records = []
    for document_id, namespace_page, ana_page, format_page, figure in [
        ("NVM_1_0E", 10, 11, 65, "98"),
        ("NVM_1_1", 12, 13, 90, "116"),
    ]:
        items = [
            ("CAPACITY_ORDER", ["NSZE", "NCAP", "NUSE"], "mandatory",
             "Namespace Size >= Namespace Capacity >= Namespace Utilization.", None,
             namespace_page, "2.1.1", None, ["Identify namespace response context"]),
            ("THINP_ZERO_NCAP", ["NSFEAT.THINP", "NCAP", "NSZE"], "mandatory",
             "The controller shall report Namespace Capacity equal to Namespace Size.",
             "THINP is cleared to 0", namespace_page, "2.1.1", None, ["NSFEAT.THINP"]),
            ("THINP_ZERO_NUSE_PERMISSION", ["NSFEAT.THINP", "NUSE", "NCAP"], "permission",
             "The controller may report Namespace Utilization always equal to Namespace Capacity.",
             "THINP is cleared to 0", namespace_page, "2.1.1", None, ["NSFEAT.THINP"]),
            ("THINP_TRACKING", ["NSFEAT.THINP", "NUSE"], "behavior",
             "The controller shall track the number of allocated blocks in Namespace Utilization.",
             "THINP is set to 1", namespace_page, "2.1.1", None,
             ["NSFEAT.THINP", "Allocation state/history; cannot establish from one Identify response"]),
            ("ANA_ZERO_REPORTING", ["CMIC", "NUSE", "NVMCAP"], "mandatory",
             "NUSE and NVMCAP are cleared to 0h in the specified ANA states.",
             "Controller supports ANA reporting and controller/namespace relationship is ANA Inaccessible or ANA Persistent Loss",
             ana_page, "2.1.1", None, ["Base CMIC ANA reporting support", "Base ANA state definitions", "Current controller/namespace ANA state"]),
            ("METADATA_ABSENT", ["LBAF.MS"], "mandatory",
             "If there is no metadata supported, this field shall be cleared to 0h.",
             "No metadata supported for the LBA format", format_page, "4.1.5.1", figure,
             ["LBA format instance and metadata support"]),
            ("LBADS_NONZERO_MINIMUM", ["LBAF.LBADS"], "mandatory",
             "A non-zero value less than 9 is not supported; 0h means the LBA format is not currently available.",
             None, format_page, "4.1.5.1", figure, ["LBA format instance", "Exponent encoding and unavailable sentinel"]),
        ]
        for suffix, fields, classification, statement, condition, page, section, fig, dependencies in items:
            records.append({"requirement_id": f"{document_id}.CURATED.{suffix}",
                "document_id": document_id, "structure_ids": ["NVME.CNS00"],
                "field_names": fields, "classification": classification, "statement": statement,
                "condition": condition, "dependencies": dependencies,
                "evidence": [{"document_id": document_id, "section": section, "figure": fig,
                              "pdf_page": page, "printed_page": str(page)}],
                "review_status": "candidate", "evaluation_status": "unresolved",
                "unresolved": ["Source-read interpretation requires independent human review.",
                               "No executable expression or approved reference closure; retain version-specific response context."]})
    for document_id, page, modal in [("NVM_1_0E", 56, "shall"), ("NVM_1_1", 80, "may")]:
        records.append({"requirement_id": f"{document_id}.CURATED.ALL_NS_UNSUPPORTED",
            "document_id": document_id, "structure_ids": ["NVME.CNS00"], "field_names": ["NSID"],
            "classification": "behavior" if modal == "shall" else "permission",
            "statement": f"The controller {modal} abort the command with a status code of Invalid Namespace or Format.",
            "condition": "Namespace Management not supported and NSID is FFFFFFFFh",
            "dependencies": ["Namespace Management capability", "Identify CNS/NSID query context"],
            "evidence": [{"document_id": document_id, "section": "4.1.5.1", "figure": None,
                          "pdf_page": page, "printed_page": str(page)}],
            "review_status": "candidate", "evaluation_status": "unresolved",
            "unresolved": ["Version-specific SHALL/MAY difference must be preserved; requires independent review.",
                           "Command behavior cannot be validated from Identify structure bytes alone."]})
    for document_id, page, section in [("NVM_1_0E", 12, "2.1.4"), ("NVM_1_1", 14, "2.1.4.1")]:
        for suffix, fields, statement in [
            ("AWUPF_BOUND", ["AWUPF", "AWUN"], "AWUPF shall be less than or equal to AWUN."),
            ("NAWUN_BASELINE", ["NAWUN", "AWUN"], "NAWUN shall be greater than or equal to AWUN."),
        ]:
            records.append({"requirement_id": f"{document_id}.CURATED.{suffix}",
                "document_id": document_id, "structure_ids": ["NVME.CNS01"] if suffix == "AWUPF_BOUND" else ["NVME.CNS00", "NVME.CNS01"],
                "field_names": fields, "classification": "mandatory", "statement": statement,
                "condition": "Parameter is supported" + ("; Single Atomicity Mode" if document_id == "NVM_1_1" else ""),
                "dependencies": ["Parameter support", "Encoded atomicity values and applicable namespace format"] + (["Atomicity mode"] if document_id == "NVM_1_1" else []),
                "evidence": [{"document_id": document_id, "section": section, "figure": "4",
                              "pdf_page": page, "printed_page": str(page)}],
                "review_status": "candidate", "evaluation_status": "unresolved",
                "unresolved": ["Table footnote applicability and source interpretation require independent human review.",
                               "NVM 1.1 Single/Multiple Atomicity Mode scope must not be flattened into an unconditional cross-version rule."]})
    return records


def source_hashes(pdf_dir: Path, catalog_path: Path = CATALOG) -> dict[str, str]:
    """Bind fixed-page extraction to the explicitly registered document bytes."""
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    entries = catalog["documents"]
    documents = {entry["document_id"]: entry for entry in entries}
    if len(documents) != len(entries):
        raise ValueError("Duplicate document identity in source registry")
    hashes = {}
    for identity, filename in DOCUMENTS.items():
        entry = documents.get(identity)
        if entry is None or entry["filename"] != filename:
            raise ValueError(f"Source registry does not match fixed-page extraction: {identity}")
        digest = hashlib.sha256((pdf_dir / filename).read_bytes()).hexdigest()
        if digest != entry["sha256"]:
            raise ValueError(f"Source SHA256 mismatch: {identity}; review source change before extraction")
        hashes[identity] = digest
    return hashes


def validate_output(output: Path, pdf_dir: Path, catalog_path: Path = CATALOG) -> None:
    if output.is_symlink() or any(parent.is_symlink() for parent in output.parents):
        raise ValueError("Candidate output must not traverse symbolic links")
    resolved = output.resolve()
    if any(part.casefold() == "generated" for part in resolved.parts):
        raise ValueError("Candidate extraction cannot write generated artifacts")
    protected = {(pdf_dir / filename).resolve() for filename in DOCUMENTS.values()}
    protected.add(catalog_path.resolve())
    if resolved in protected or output.suffix.casefold() != ".json":
        raise ValueError("Candidate output must be a JSON file separate from source PDFs and registry")


def extract(pdf_dir: Path, catalog_path: Path = CATALOG) -> dict:
    hashes = source_hashes(pdf_dir, catalog_path)
    import pypdfium2 as pdfium

    result = {"kind": "requirement_candidates", "format_version": 1, "document_hashes": hashes,
              "requirements": [], "coverage": [], "unresolved": [
                  "All passages are unreviewed candidates, never executable or confirmed rules.",
                  "Lexical classification, field links and structure links require source review.",
                  "Sentence/page boundaries may split applicability, exceptions or table rows.",
                  "Keyword screening cannot establish exhaustive normative coverage or reference closure.",
                  "Reserved must not be converted to expected=0 without the applicable conventions and context.",
                  "No Samsung/product policy or product expected value is supplied by this extraction.",
              ]}
    for document_id, filename in DOCUMENTS.items():
        source = pdf_dir / filename
        doc = pdfium.PdfDocument(source)
        pages = []
        for page in doc:
            textpage = page.get_textpage()
            pages.append(textpage.get_text_range())
            textpage.close()
            page.close()
        doc.close()
        field_names: set[str] = set()
        referenced_sections: set[str] = set()
        for start, end, _, _ in CORE[document_id]:
            for text in pages[start - 1:end]:
                field_names.update(ACRONYM.findall(text))
                referenced_sections.update(re.findall(r"\bsection\s+(\d+(?:\.\d+)+)", text, re.I))
        # Long acronyms limit common-word false positives; links remain candidate.
        field_pattern = re.compile(r"\b(?:" + "|".join(sorted(re.escape(x) for x in field_names if len(x) >= 4)) + r")\b")
        active_section = "UNKNOWN"
        for page_number, raw in enumerate(pages, 1):
            lines = raw.splitlines()
            headings = [m.group(1) for line in lines if (m := re.match(r"^\s*(\d+\.\d+(?:\.\d+)*)\s+[A-Za-z]", line))]
            if headings:
                active_section = headings[-1]
            core = [(cns, section) for start, end, cns, section in CORE[document_id]
                    if start <= page_number <= end]
            forward_match = any(active_section == s or active_section.startswith(s + ".") for s in referenced_sections)
            relevant = bool(IDENTIFY.search(raw) or field_pattern.search(raw) or forward_match)
            if not core and (not relevant or page_number < (23 if document_id == "BASE_2_1" else 8)):
                result["coverage"].append({"document_id": document_id, "pdf_page": page_number,
                    "status": "excluded", "reason": "Front matter or no Identify/known-field lexical match; not a semantic no-requirement finding."})
                continue
            printed = next((line.strip() for line in lines[:7] if re.fullmatch(r"\d+", line.strip())), None)
            sections = sorted({s for _, s in core})
            # Outside fixed verified ranges, headings from flattened PDF text are
            # a search aid, not reliable evidence anchors.
            section = "; ".join(sections) if sections else "UNKNOWN"
            structures = sorted({"NVME.CNS" + cns for cns, _ in core})
            chunks = passages(raw)
            captured = 0
            for index, statement in enumerate(chunks, 1):
                if not core and not (IDENTIFY.search(statement) or field_pattern.search(statement) or forward_match):
                    continue
                names = sorted(set(field_pattern.findall(statement)) | set(ACRONYM.findall(statement)))
                references = sorted(set(REFERENCE.findall(statement)))
                figures = sorted(set(re.findall(r"Figure\s+(\d+)\s*:", statement)))
                unresolved = ["Human source review and exact applicability/exception boundaries required.",
                              "PDF table columns and continuation context have not been visually verified."]
                if not core:
                    unresolved.append("Forward/reverse-reference search hit; section anchor and relation to scoped structures are not established.")
                if len(core) > 1:
                    unresolved.append("Shared page: structure ownership must be resolved per passage.")
                if references:
                    unresolved.append("Referenced clauses require explicit closure review; lexical capture is not resolution.")
                if re.search(r"\bif\b|\bwhen\b|\bunless\b", statement, re.I):
                    unresolved.append("Conditional text retained verbatim; condition/dependency expression not resolved.")
                if "Base Specification" in statement or "Command Set specification" in statement:
                    references.append("Cross-document reference: select exact registered bundle member during review")
                result["requirements"].append({
                    "requirement_id": f"{document_id}.P{page_number:04d}.EXCERPT{index:02d}",
                    "document_id": document_id, "structure_ids": structures,
                    "field_names": names, "classification": classify(statement),
                    "statement": statement, "condition": None, "dependencies": references,
                    "evidence": [{"document_id": document_id, "section": section,
                                  "figure": figures[0] if len(figures) == 1 else None,
                                  "pdf_page": page_number, "printed_page": printed}],
                    "review_status": "candidate", "evaluation_status": "unresolved",
                    "unresolved": unresolved,
                })
                captured += 1
            result["coverage"].append({"document_id": document_id, "pdf_page": page_number,
                "status": "unresolved", "reason": f"{'Core structure page' if core else 'Forward/reverse-reference search hit'}: {captured} source passages captured; semantic/visual review pending."})
        digest = hashes[document_id]
        result["unresolved"].append(f"Source pin {document_id}: SHA256={digest}; {len(pages)} PDF pages screened. Re-extraction must use these exact bytes or explicitly review source change.")
    result["requirements"].extend(focused_candidates())
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("candidates/nvme/requirements.json"))
    args = parser.parse_args()
    validate_output(args.output, args.pdf_dir)
    data = extract(args.pdf_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"Captured {len(data['requirements'])} review-only passages; screened {len(data['coverage'])} pages.")


if __name__ == "__main__":
    main()
