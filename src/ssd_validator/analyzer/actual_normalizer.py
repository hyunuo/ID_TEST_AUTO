"""Decode saved Identify bytes using the selected Bundle, independently of CLI age."""

from hashlib import sha256

from ssd_validator.errors import KnowledgeError
from ssd_validator.models.actual_data import (
    CaptureMetadata, DecodedField, IdentifyQuery, NormalizationLayout,
    NormalizationReport, OfflineValidationReport, UnmappedBytes, WireField,
)
from ssd_validator.models.effective import SourceFile
from ssd_validator.models.runtime import ActualFact, EffectiveExpectedProfile, FieldRef
from ssd_validator.resolver import evaluate
from ssd_validator.storage.serialization import canonical_bytes


def layout_from_profile(profile: EffectiveExpectedProfile, query: IdentifyQuery, *, response_size: int,
                        array_strides: dict[str, int] | None = None,
                        json_paths: dict[str, tuple[str | int, ...]] | None = None) -> NormalizationLayout:
    """Reuse Source-built fields. Array strides must be explicitly supplied, not guessed."""
    strides, paths = array_strides or {}, json_paths or {}
    fields = []
    for registration in profile.fields:
        if (registration.cns, registration.csi) != (query.cns, query.csi):
            continue
        schema = registration.schema_definition
        count = registration.array_count or 1
        if registration.array_count is not None:
            stride = strides.get(schema.field_id)
            if type(stride) is not int or stride < schema.length:
                raise KnowledgeError("ARRAY_STRIDE_REQUIRED", schema.field_id)
        else:
            stride = 0
        for index in range(count):
            ref = FieldRef(field_id=schema.field_id, index=index if registration.array_count else None)
            fields.append(WireField(field=ref, offset=schema.offset + index * stride, length=schema.length,
                                    value_type=schema.value_type, endian=schema.endian,
                                    semantic_state=schema.state.value if schema.state else "unknown",
                                    json_path=paths.get(ref.key), provenance=registration.provenance,
                                    history=registration.history))
    if not fields:
        raise KnowledgeError("NO_RESPONSE_FIELDS", "No fields registered for this CNS/CSI")
    return NormalizationLayout(data_kind="fixture" if profile.data_kind == 'fixture' else 'candidate', bundle_id=profile.bundle.bundle_id,
                               base_revision=profile.bundle.base_revision, nvm_revision=profile.bundle.nvm_revision,
                               query=query, response_size=response_size, fields=tuple(sorted(fields, key=lambda f: f.field.key)))


def _observed(layout, field):
    return "OBSERVED" if layout.data_kind == "fixture" and field.provenance.status == "confirmed" else "REVIEW"


def _finish(layout, capture, source, source_format, fields, *, gaps=(), tool_output=None, unmapped_keys=(), errors=()):
    states = {f.status for f in fields}
    status = "ERROR" if errors or "ERROR" in states else "UNKNOWN" if "UNKNOWN" in states else "REVIEW" if "REVIEW" in states else "OBSERVED"
    # Candidate interpretations can be inspected but never enter authoritative fixture evaluation.
    facts = tuple(ActualFact(field=f.definition.field, value=f.value, source=source, capture_id=capture.capture_id)
                  for f in fields if f.status == "OBSERVED" and f.definition.value_type != "bytes")
    return NormalizationReport(layout=layout, capture=capture, source=source, source_format=source_format,
                               status=status, fields=tuple(fields), actual_facts=facts, unmapped_bytes=tuple(gaps),
                               tool_output=tool_output, unmapped_json_keys=tuple(unmapped_keys), errors=tuple(errors))


def normalize_raw(layout: NormalizationLayout, capture: CaptureMetadata, raw: bytes, *, source_path="memory.raw") -> NormalizationReport:
    source = SourceFile(path=source_path, sha256=sha256(raw).hexdigest())
    errors = []
    if capture.query != layout.query:
        errors.append("Capture query differs from selected layout (CNS/CSI/NSID/controller)")
    if len(raw) != layout.response_size:
        errors.append(f"Response length {len(raw)} differs from declared {layout.response_size}; no padding/truncation")
    if errors:
        return _finish(layout, capture, source, "raw", (), errors=errors)
    fields = []
    for definition in sorted(layout.fields, key=lambda f: f.field.key):
        buffer = raw[definition.offset:definition.offset + definition.length]
        try:
            if definition.value_type in {"integer", "bitmask"}:
                value = int.from_bytes(buffer, byteorder=definition.endian)
            elif definition.value_type == "string":
                # Explicit fixed-width ASCII convention; raw bytes remain in trace.
                value = buffer.decode("ascii").rstrip("\x00 ")
            else:
                value = buffer.hex()
            fields.append(DecodedField(definition=definition, status=_observed(layout, definition), value=value,
                                       raw_hex=buffer.hex(), reason="Decoded using target Bundle layout; no expected-value verdict"))
        except UnicodeDecodeError:
            fields.append(DecodedField(definition=definition, status="ERROR", raw_hex=buffer.hex(),
                                       reason="Fixed-width ASCII field contains non-ASCII bytes"))
    gaps, end = [], 0
    for definition in sorted(layout.fields, key=lambda f: f.offset):
        if definition.offset > end:
            gaps.append(UnmappedBytes(offset=end, length=definition.offset-end, raw_hex=raw[end:definition.offset].hex()))
        end = definition.offset + definition.length
    if end < len(raw):
        gaps.append(UnmappedBytes(offset=end, length=len(raw)-end, raw_hex=raw[end:].hex()))
    return _finish(layout, capture, source, "raw", fields, gaps=gaps)


def _json_value(payload, path):
    current = payload
    for part in path:
        if type(part) is str:
            if not isinstance(current, dict):
                raise ValueError("JSON key path crosses a non-object")
            if part not in current:
                return False, None
            current = current[part]
        else:
            if not isinstance(current, (list, tuple)):
                raise ValueError("JSON index path crosses a non-array")
            if part >= len(current):
                return False, None
            current = current[part]
    return True, current


def normalize_json(layout: NormalizationLayout, capture: CaptureMetadata, payload: dict[str, object], *,
                   source_path="memory.json", source_bytes: bytes | None = None) -> NormalizationReport:
    source = SourceFile(path=source_path, sha256=sha256(source_bytes if source_bytes is not None else canonical_bytes(payload)).hexdigest())
    if capture.query != layout.query:
        return _finish(layout, capture, source, "json", (), tool_output=payload,
                       errors=("Capture query differs from selected layout (CNS/CSI/NSID/controller)",))
    fields, used = [], set()
    for definition in sorted(layout.fields, key=lambda f: f.field.key):
        try:
            if definition.json_path is None:
                found, value = False, None
            else:
                used.add(definition.json_path[0])
                found, value = _json_value(payload, definition.json_path)
            if not found:
                fields.append(DecodedField(definition=definition, status="UNKNOWN", reason="JSON field/path missing; no zero substituted"))
                continue
            if definition.value_type in {"integer", "bitmask"}:
                if type(value) is not int or not 0 <= value < 1 << (definition.length * 8):
                    raise ValueError("JSON numeric value must be an unsigned integer of the declared width")
            elif definition.value_type == "string":
                if type(value) is not str:
                    raise ValueError("JSON string value must be a string")
            else:
                raise ValueError("JSON bytes normalization needs a release-specific encoding adapter")
            fields.append(DecodedField(definition=definition, status=_observed(layout, definition), value=value,
                                       reason="Explicit target Bundle JSON path; no spec inferred from tool labels"))
        except ValueError as error:
            fields.append(DecodedField(definition=definition, status="ERROR", reason=str(error)))
    return _finish(layout, capture, source, "json", fields, tool_output=payload,
                   unmapped_keys=sorted(k for k in payload if k not in used))


def evaluate_normalized(profile: EffectiveExpectedProfile, reports: tuple[NormalizationReport, ...]) -> OfflineValidationReport:
    """Fixture bridge: never combine devices, namespaces or different target Bundles."""
    errors = []
    fields = {r.schema_definition.field_id: r for r in profile.fields}
    if len({r.capture.capture_id for r in reports}) != len(reports):
        errors.append("Duplicate capture identity")
    if len({r.capture.device_id for r in reports}) > 1:
        errors.append("Captures from different devices cannot be combined")
    nsids = {r.capture.query.nsid for r in reports if r.capture.query.nsid is not None}
    if len(nsids) > 1:
        errors.append("Current FieldRef cannot combine multiple namespace identities")
    nsid = profile.context.facts.get("namespace.nsid")
    if nsid is not None and (type(nsid) is not int or not 0 <= nsid <= 0xffffffff):
        errors.append("Context namespace.nsid must be an unsigned 32-bit integer")
    if nsid is not None and any(r.capture.query.nsid is not None and r.capture.query.nsid != nsid for r in reports):
        errors.append("Capture NSID differs from explicit Context")
    for report in reports:
        layout = report.layout
        if (layout.bundle_id, layout.base_revision, layout.nvm_revision) != (
                profile.bundle.bundle_id, profile.bundle.base_revision, profile.bundle.nvm_revision):
            errors.append("Capture layout differs from Expected Profile Bundle")
        if report.status == "ERROR":
            errors.append(f"Normalization ERROR: {report.capture.capture_id}")
        for definition in layout.fields:
            registration = fields.get(definition.field.field_id)
            if registration is None:
                errors.append(f"Capture field is not registered: {definition.field.key}")
                continue
            schema = registration.schema_definition
            if ((registration.cns, registration.csi) != (layout.query.cns, layout.query.csi)
                    or (schema.length, schema.value_type, schema.endian) != (definition.length, definition.value_type, definition.endian)
                    or definition.provenance != registration.provenance or definition.history != registration.history):
                errors.append(f"Capture field differs from Source-built registry: {definition.field.key}")
            index = definition.field.index
            if registration.array_count is None:
                if index is not None or definition.offset != schema.offset:
                    errors.append(f"Scalar capture mapping differs from registry: {definition.field.key}")
            elif index is None or index >= registration.array_count or definition.offset < schema.offset + index * schema.length:
                errors.append(f"Invalid array capture mapping: {definition.field.key}")
    ordered = tuple(sorted(reports, key=lambda r: r.capture.capture_id))
    if errors:
        return OfflineValidationReport(status="ERROR", captures=ordered, errors=tuple(sorted(set(errors))))
    if any(r.layout.data_kind != "fixture" or r.status == "REVIEW" for r in reports):
        return OfflineValidationReport(status="REVIEW", captures=ordered,
                                       errors=("Candidate/unconfirmed captures are not authoritative fixture input",))
    facts = tuple(f for report in reports for f in report.actual_facts)
    try:
        validation = evaluate(profile, facts)
    except KnowledgeError as error:
        return OfflineValidationReport(status="ERROR", captures=ordered, errors=(str(error),))
    statuses = {validation.status, *("UNKNOWN" for r in reports if r.status == "UNKNOWN")}
    overall = next((s for s in ("ERROR", "CONFLICT", "FAIL", "UNKNOWN", "REVIEW", "PASS", "N/A") if s in statuses))
    return OfflineValidationReport(status=overall, captures=ordered, validation=validation)
