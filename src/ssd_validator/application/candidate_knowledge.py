"""Explicit, non-authoritative multi-document candidate builds and review diffs.

No candidate here is a RequirementRule and no device verdict can be produced.
Original definitions remain visible even when an overlap needs human review.
"""

import json
import re
from hashlib import sha256
from pathlib import Path

from pydantic import ValidationError

from ssd_validator.errors import KnowledgeError
from ssd_validator.knowledge.yaml_loader import validation_message
from ssd_validator.models.candidates import CandidateCatalog, RequirementCandidates, StructureCandidates
from ssd_validator.spec_builder.delta import match_guard
from ssd_validator.spec_builder.manifest import git_commit
from ssd_validator.spec_builder.version_graph import version_order
from ssd_validator.storage.artifacts import write_artifacts
from ssd_validator.storage.serialization import canonical_bytes

COMPILER_VERSION = "1.0.0"


def _unique_pairs(pairs, label):
    result = {}
    for key, value in pairs:
        if key in result:
            raise KnowledgeError("DUPLICATE_CANDIDATE", f"{label}: {key}")
        result[key] = value
    return result


def _object(pairs):
    return _unique_pairs(pairs, "JSON key")


def _read(path, model):
    if path.is_symlink():
        raise KnowledgeError("SOURCE_SYMLINK", str(path))
    try:
        raw = path.read_bytes()
        data = json.loads(raw.decode("utf-8"), object_pairs_hook=_object)
        # Content hash ignores line endings and formatting; the byte hash only honours older pins.
        return model.model_validate(data), sha256(canonical_bytes(data)).hexdigest(), sha256(raw).hexdigest()
    except (UnicodeError, json.JSONDecodeError, ValidationError) as error:
        message = validation_message(error) if isinstance(error, ValidationError) else str(error)
        raise KnowledgeError("CANDIDATE_FORMAT", message, source=path.name) from error


def _anchors(value):
    if isinstance(value, dict):
        if "pdf_page" in value and "section" in value and "document_id" in value:
            yield value
        else:
            for child in value.values():
                yield from _anchors(child)
    elif isinstance(value, list):
        for child in value:
            yield from _anchors(child)


def load_candidates(source: Path, documents_root: Path | None = None):
    if source.is_symlink() or any(p.is_symlink() for p in source.parents):
        raise KnowledgeError("SOURCE_SYMLINK", str(source))
    source = source.resolve()
    if "generated" in source.parts:
        raise KnowledgeError("GENERATED_IS_NOT_SOURCE", str(source))
    catalog, c_hash, c_bytes = _read(source / "catalog.json", CandidateCatalog)
    structures, s_hash, s_bytes = _read(source / "structures.json", StructureCandidates)
    requirements, r_hash, r_bytes = _read(source / "requirements.json", RequirementCandidates)
    documents = {d.document_id: d for d in catalog.documents}
    pins = {d.document_id: d.sha256 for d in catalog.documents}
    if structures.document_hashes != pins or requirements.document_hashes != pins:
        raise KnowledgeError("EXTRACTION_HASH", "Extraction document hashes must equal the registered PDF hashes")
    # Reuse the explicit inheritance graph checker; each document component has its own chain.
    keys = {d.document_id: f"{d.component}:{d.revision}" for d in catalog.documents}
    _unique_pairs(((key, doc) for doc, key in keys.items()), "component revision")
    for doc in catalog.documents:
        if doc.inherits:
            parent = documents.get(doc.inherits)
            if parent is None or parent.component != doc.component:
                raise KnowledgeError("DOCUMENT_PARENT", doc.document_id)
    version_order({keys[d.document_id]: keys[d.inherits] if d.inherits else None for d in catalog.documents})
    for bundle in catalog.bundles:
        for identity, component in ((bundle.base_document, "NVME_BASE"), (bundle.nvm_document, "NVME_NVM")):
            if identity not in documents or documents[identity].component != component:
                raise KnowledgeError("BUNDLE_COMPONENT", f"{bundle.bundle_id}: {identity}")
        if len(set(bundle.structure_ids)) != len(bundle.structure_ids):
            raise KnowledgeError("DUPLICATE_CANDIDATE", bundle.bundle_id)
    by_structure = _unique_pairs((((s.document_id, s.structure_id), s) for s in structures.structures), "structure")
    templates = _unique_pairs(((t.template_id, t) for t in structures.nested_templates), "template")
    def validate_fields(fields):
        for field in fields:
            if field.nested_template_id:
                template = templates.get(field.nested_template_id)
                if template is None or field.array is None or template.size_bytes != field.array.stride_bytes:
                    raise KnowledgeError("NESTED_TEMPLATE", field.field_id)
            validate_fields(field.children)
    for structure in structures.structures:
        validate_fields(structure.fields)
    _unique_pairs(((r.requirement_id, r) for r in requirements.requirements), "requirement")
    _unique_pairs((((e.document_id, e.pdf_page), e) for e in requirements.coverage), "coverage page")
    for payload in (structures, requirements):
        for anchor in _anchors(payload.model_dump(mode="json")):
            doc = documents.get(anchor["document_id"])
            if doc is None or anchor["pdf_page"] > doc.pages:
                raise KnowledgeError("DOCUMENT_ANCHOR", str(anchor))
    for structure in structures.structures:
        if structure.document_id not in documents:
            raise KnowledgeError("UNKNOWN_DOCUMENT", structure.document_id)
        if not any(e.document_id == structure.document_id for e in structure.evidence):
            raise KnowledgeError("DOCUMENT_ANCHOR", structure.structure_id)
    selected_ids = {i for b in catalog.bundles for i in b.structure_ids}
    for requirement in requirements.requirements:
        if requirement.document_id not in documents:
            raise KnowledgeError("UNKNOWN_DOCUMENT", requirement.document_id)
        if set(requirement.structure_ids) - selected_ids:
            raise KnowledgeError("UNKNOWN_STRUCTURE", requirement.requirement_id)
        if not any(e.document_id == requirement.document_id for e in requirement.evidence):
            raise KnowledgeError("DOCUMENT_ANCHOR", requirement.requirement_id)
        for bundle in catalog.bundles:
            if requirement.document_id in {bundle.base_document, bundle.nvm_document}:
                if any(i not in bundle.structure_ids or not any((d, i) in by_structure for d in
                    (bundle.base_document, bundle.nvm_document)) for i in requirement.structure_ids):
                    raise KnowledgeError("UNKNOWN_STRUCTURE", f"{bundle.bundle_id}: {requirement.requirement_id}")
    for entry in requirements.coverage:
        if entry.document_id not in documents or entry.pdf_page > documents[entry.document_id].pages:
            raise KnowledgeError("DOCUMENT_ANCHOR", f"coverage: {entry}")
    # PDF validation is required for publishing, optional for portable source-only review/diff.
    if documents_root is not None:
        for doc in catalog.documents:
            path = documents_root / doc.filename
            if path.is_symlink() or any(p.is_symlink() for p in path.parents):
                raise KnowledgeError("SOURCE_SYMLINK", str(path))
            if sha256(path.read_bytes()).hexdigest() != doc.sha256:
                raise KnowledgeError("DOCUMENT_HASH", doc.document_id)
    sources = {"catalog.json": c_hash, "structures.json": s_hash, "requirements.json": r_hash}
    byte_sources = {"catalog.json": c_bytes, "structures.json": s_bytes, "requirements.json": r_bytes}
    return catalog, by_structure, requirements, sources, byte_sources, templates


def _segments(fragments):
    """Conservative interval composition: never choose an overlapping winner."""
    size = fragments[0].size_bytes
    if (any(s.size_bytes != size or s.cns != fragments[0].cns for s in fragments)
            or len({s.csi for s in fragments if s.csi is not None}) > 1):
        raise KnowledgeError("STRUCTURE_IDENTITY", fragments[0].structure_id)
    definitions = [(s.document_id, f) for s in fragments for f in s.fields]
    edges = sorted({0, size, *(n for _, f in definitions for n in (f.byte_offset, f.byte_offset + f.byte_length))})
    result = []
    for start, end in zip(edges, edges[1:]):
        entries = [(doc, f) for doc, f in definitions if f.byte_offset <= start and f.byte_offset + f.byte_length >= end]
        concrete = [(d, f) for d, f in entries if f.state not in {"delegated", "unknown"}]
        if not entries:
            state = "UNKNOWN"
        elif not concrete:
            state = "UNRESOLVED"
        elif len(concrete) > 1:
            # Even matching byte ranges may have different semantics. Keep both for review.
            state = "CONFLICT"
        elif any(f.state == "unknown" for _, f in entries):
            state = "UNRESOLVED"
        else:
            state = "SUPPLEMENT" if len(entries) > 1 else "CANDIDATE"
        result.append({"byte_offset": start, "byte_length": end - start, "state": state,
                       "definitions": [{"document_id": d, "field_id": f.field_id} for d, f in entries]})
    return result


def _bundle(bundle, structures, requirements, templates):
    doc_ids = (bundle.base_document, bundle.nvm_document)
    output = []
    for identity in sorted(bundle.structure_ids):
        fragments = [structures[(d, identity)] for d in doc_ids if (d, identity) in structures]
        if not fragments:
            raise KnowledgeError("MISSING_STRUCTURE", f"{bundle.bundle_id}: {identity}")
        segments = _segments(fragments)
        output.append({"structure_id": identity, "cns": fragments[0].cns,
                       "csi": next((s.csi for s in fragments if s.csi is not None), None),
                       "size_bytes": fragments[0].size_bytes,
                       "definitions": [s.model_dump(mode="json") for s in fragments], "segments": segments,
                       "coverage_status": "partial" if any(s.coverage_status == "partial" for s in fragments)
                       or any(s["state"] in {"UNKNOWN", "UNRESOLVED", "CONFLICT"} for s in segments) else "complete"})
    selected_requirements = [r.model_dump(mode="json") for r in sorted(requirements.requirements, key=lambda r: r.requirement_id)
                             if r.document_id in doc_ids]
    def names(field):
        return {field["name"].casefold(), field["field_id"].split(".")[-1].casefold(),
                *(m.casefold() for m in re.findall(r"\(([A-Z][A-Z0-9_]*)\)", field["name"]))}

    def targets(structure, definition, fields, prefix=""):
        for field in fields:
            path = f"{prefix}.{field['field_id']}" if prefix else field["field_id"]
            yield names(field), {"structure_id": structure["structure_id"], "document_id": definition["document_id"], "field_id": path}
            yield from targets(structure, definition, field.get("children", []), path)

    for requirement in selected_requirements:
        links = []
        for name in requirement["field_names"]:
            matches = [target for s in output if s["structure_id"] in requirement["structure_ids"]
                       for d in s["definitions"] for aliases, target in targets(s, d, d["fields"])
                       if name.casefold() in aliases]
            links.append({"name": name, "status": "AMBIGUOUS" if len(matches) > 1 else "CANDIDATE" if matches else "UNRESOLVED", "matches": matches})
        requirement["field_links"] = links
    used_templates = {f.nested_template_id for (d, i), s in structures.items() if d in doc_ids and i in bundle.structure_ids
                      for f in s.fields if f.nested_template_id}
    return {"kind": "candidate_bundle_snapshot", "format_version": 1, "review_status": "candidate",
            "authoritative": False, "bundle": bundle.model_dump(mode="json"), "structures": output,
            "nested_templates": [templates[key].model_dump(mode="json") for key in sorted(used_templates)],
            "requirements": selected_requirements,
            "unresolved": sorted(requirements.unresolved)}


def compile_candidates(source: Path, documents_root: Path | None = None):
    catalog, structures, requirements, sources, byte_sources, templates = load_candidates(source, documents_root)
    bundles = {b.bundle_id: _bundle(b, structures, requirements, templates) for b in sorted(catalog.bundles, key=lambda b: b.bundle_id)}
    manifest = {"format_version": 1, "candidate_compiler_version": COMPILER_VERSION,
                "review_status": "candidate", "authoritative": False,
                "git_commit": git_commit(source), "knowledge_hash": sha256(canonical_bytes(sources)).hexdigest(),
                "byte_knowledge_hash": sha256(canonical_bytes(byte_sources)).hexdigest(),
                "sources": sources, "documents": [d.model_dump(mode="json") for d in catalog.documents],
                "documents_verified": documents_root is not None, "bundles": sorted(bundles)}
    return catalog, bundles, manifest, requirements


def _flatten(snapshot):
    result = {}
    for structure in snapshot["structures"]:
        result[f"STRUCTURE:{structure['structure_id']}"] = {k: structure[k] for k in ("structure_id", "cns", "csi", "size_bytes")}
        for definition in structure["definitions"]:
            # Compare the two independent document components, never conflate Base with NVM.
            component = "BASE" if definition["document_id"] == snapshot["bundle"]["base_document"] else "NVM"
            for field in definition["fields"]:
                key = f"{component}:{structure['structure_id']}:{field['field_id']}"
                result[key] = field
    for template in snapshot.get("nested_templates", []):
        document_id = next((d for d in sorted((snapshot["bundle"]["base_document"], snapshot["bundle"]["nvm_document"]), key=len, reverse=True)
                            if template["template_id"].startswith(d + ".")), None)
        if document_id is None:
            raise KnowledgeError("NESTED_TEMPLATE", template["template_id"])
        local_id = template["template_id"][len(document_id) + 1:]
        component = "BASE" if document_id == snapshot["bundle"]["base_document"] else "NVM"
        result[f"TEMPLATE:{component}:{local_id}"] = {k: v for k, v in template.items() if k not in {"template_id", "source_rows"}}
    return result


def _semantic(value):
    if isinstance(value, dict):
        return {k: _semantic(v) for k, v in value.items() if k not in {"evidence", "review_status"}}
    if isinstance(value, list):
        return [_semantic(v) for v in value]
    return value


def diff_bundles(before, after):
    old, new = _flatten(before), _flatten(after)
    changes = []
    for key in sorted(old.keys() | new.keys()):
        previous, current = old.get(key), new.get(key)
        if previous is None or current is None or _semantic(previous) != _semantic(current):
            changes.append({"target": key, "action": "ADD" if previous is None else "REMOVE" if current is None else "MODIFY",
                            "previous": previous, "current": current})
    def curated(snapshot):
        return {r["requirement_id"].split(".CURATED.", 1)[1]: r for r in snapshot["requirements"] if ".CURATED." in r["requirement_id"]}
    old_pairs, new_pairs = curated(before), curated(after)
    pairs = [{"topic": key, "status": "REVIEW", "previous": old_pairs.get(key), "current": new_pairs.get(key)}
             for key in sorted(old_pairs.keys() | new_pairs.keys())]
    return {"kind": "candidate_bundle_diff", "review_status": "candidate", "authoritative": False,
            "from": before["bundle"]["bundle_id"], "to": after["bundle"]["bundle_id"], "schema_changes": changes,
            "requirement_review_pairs": pairs,
            # Text candidates do not have approved semantic identities across revisions.
            # Report both sets rather than implying that unchanged wording proves equivalence.
            "requirements": {"comparison_status": "REVIEW", "previous": before["requirements"],
                             "current": after["requirements"]}}


def apply_candidate_changes(parent: dict, changes: list[dict]) -> dict:
    """Replay reviewable structural changes with the existing Builder's guard semantics."""
    result = dict(parent)
    seen = set()
    for change in changes:
        key = change["target"]
        if key in seen:
            raise KnowledgeError("DUPLICATE_TARGET", key)
        seen.add(key)
        action, previous, current = change["action"], change["previous"], change["current"]
        if action == "ADD":
            if key in parent or previous is not None or current is None:
                raise KnowledgeError("INVALID_DELTA", key)
        elif action in {"MODIFY", "REMOVE"}:
            if key not in parent or not previous or (action == "REMOVE") != (current is None):
                raise KnowledgeError("INVALID_DELTA", key)
            match_guard(previous, parent[key], key)
        else:
            raise KnowledgeError("INVALID_DELTA", action)
    for change in changes:
        if change["action"] == "REMOVE":
            result.pop(change["target"])
        else:
            result[change["target"]] = change["current"]
    return result


def build_candidates(source: Path, destination: Path, documents_root: Path):
    catalog, bundles, manifest, requirements = compile_candidates(source, documents_root)
    if destination.resolve() == documents_root.resolve() or destination.resolve() in documents_root.resolve().parents:
        raise KnowledgeError("SOURCE_OUTPUT_OVERLAP", "Output would replace original PDFs")
    if destination.name != "candidate":
        raise KnowledgeError("CANDIDATE_OUTPUT", "Candidate build output must be a dedicated directory named candidate")
    payloads = {f"bundles/{key}.json": canonical_bytes(value) for key, value in bundles.items()}
    payloads["manifests/build.json"] = canonical_bytes(manifest)
    coverage = [e.model_dump(mode="json") for e in requirements.coverage]
    report = {"review_status": "candidate", "authoritative": False, "coverage": coverage,
              "pages_missing_coverage": {d.document_id: sorted(set(range(1, d.pages + 1)) -
                 {e.pdf_page for e in requirements.coverage if e.document_id == d.document_id}) for d in catalog.documents},
              "unresolved": list(requirements.unresolved), "bundles": {}}
    for key, snapshot in bundles.items():
        report["bundles"][key] = {"structures": [{"structure_id": s["structure_id"], "coverage_status": s["coverage_status"],
             "unresolved": [issue for d in s["definitions"] for issue in d["unresolved"]],
             "segments_needing_review": [i for i in s["segments"] if i["state"] in {"UNKNOWN", "UNRESOLVED", "CONFLICT"}]}
             for s in snapshot["structures"]], "requirement_candidates": len(snapshot["requirements"])}
    payloads["review.json"] = canonical_bytes(report)
    lines = ["# Identify candidate review", "", "All content is candidate, non-authoritative and not executable.",
             "PDF hashes were verified. Byte coverage does not establish semantic completeness.", "",
             "| Bundle | Structure | Source fields | Unresolved layout segments | Semantic coverage |",
             "| --- | --- | ---: | ---: | --- |"]
    for key, snapshot in bundles.items():
        for structure in snapshot["structures"]:
            unresolved_segments = sum(s["state"] in {"UNKNOWN", "UNRESOLVED", "CONFLICT"} for s in structure["segments"])
            lines.append(f"| {key} | {structure['structure_id']} | {sum(len(d['fields']) for d in structure['definitions'])} | {unresolved_segments} | {structure['coverage_status']} |")
    lines.extend(["", "## Requirement review queue", ""])
    for key, snapshot in bundles.items():
        curated_count = sum(".CURATED." in r["requirement_id"] for r in snapshot["requirements"])
        lines.append(f"- {key}: {len(snapshot['requirements'])} candidate records, including {curated_count} curated review candidates.")
    lines.extend(["", "Raw excerpts may contain several requirements, mixed table columns or incomplete conditions.",
                  "See review.json for page screening and unresolved layout details; bundle snapshots preserve every source definition.",
                  "Permission/recommendation is never a mandatory expectation. Reserved does not imply expected zero.", ""])
    for old in catalog.bundles:
        for new in catalog.bundles:
            docs = {d.document_id: d for d in catalog.documents}
            if (docs[new.base_document].inherits == old.base_document and docs[new.nvm_document].inherits == old.nvm_document):
                diff = diff_bundles(bundles[old.bundle_id], bundles[new.bundle_id])
                replayed = apply_candidate_changes(_flatten(bundles[old.bundle_id]), diff["schema_changes"])
                if _semantic(replayed) != _semantic(_flatten(bundles[new.bundle_id])):
                    raise KnowledgeError("DELTA_REPLAY", "Candidate delta did not reconstruct the new layout")
                payloads[f"diffs/{old.bundle_id}--{new.bundle_id}.json"] = canonical_bytes(diff)
                lines.extend([f"## {old.bundle_id} -> {new.bundle_id}", "",
                              f"{len(diff['schema_changes'])} structural/description changes; evidence-only changes excluded.",
                              "Curated topic pairs are review aids, not approved semantic equivalence:", ""])
                for pair in diff["requirement_review_pairs"]:
                    lines.append(f"- {pair['topic']}: REVIEW")
                    for label in ("previous", "current"):
                        if pair[label]:
                            lines.append(f"  - {label}: {pair[label]['statement']}")
                lines.append("")
    payloads["review.md"] = ("\n".join(lines) + "\n").encode("utf-8")
    write_artifacts(payloads, destination, source_root=source, artifact_kind="candidate_knowledge_build")
    return bundles
