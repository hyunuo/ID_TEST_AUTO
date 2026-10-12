"""Version-separated offline capture contracts; tool versions never select specs."""

from typing import Literal

from pydantic import Field, StrictInt, StrictStr, model_validator

from .common import DomainModel, Identifier, Text, require_unique
from .effective import SourceFile
from .provenance import ChangeRecord, Provenance
from .runtime import ActualFact, FieldRef, Status, ValidationReport


class IdentifyQuery(DomainModel):
    cns: StrictInt = Field(ge=0, le=255)
    csi: StrictInt | None = Field(default=None, ge=0, le=255)
    nsid: StrictInt | None = Field(default=None, ge=0, le=0xffffffff)
    controller_id: StrictInt | None = Field(default=None, ge=0, le=65535)


class CaptureMetadata(DomainModel):
    capture_id: Identifier
    tool_name: Text
    tool_version: Text
    tool_commit: Text | None = None
    device_id: Text
    query: IdentifyQuery
    # Diagnostic metadata only; never changes the selected product Bundle.
    advertised_nvme_version: Text | None = None


class WireField(DomainModel):
    field: FieldRef
    offset: StrictInt = Field(ge=0)
    length: StrictInt = Field(gt=0)
    value_type: Literal["integer", "bitmask", "string", "bytes"]
    endian: Literal["little", "big", "not_applicable"]
    semantic_state: Literal["defined", "reserved", "unknown"] = "unknown"
    json_path: tuple[StrictStr | StrictInt, ...] | None = None
    provenance: Provenance
    history: tuple[ChangeRecord, ...] = ()

    @model_validator(mode="after")
    def shape(self):
        if self.field.bit is not None:
            raise ValueError("Wire fields decode whole fields; rules decode bits")
        if self.value_type in {"integer", "bitmask"} and self.endian == "not_applicable":
            raise ValueError("Numeric fields need an explicit endian")
        if self.json_path is not None and (not self.json_path or any(
                (type(part) is int and part < 0) or (type(part) is str and not part) for part in self.json_path)):
            raise ValueError("JSON paths must be nonempty with nonnegative array indexes")
        return self


class NormalizationLayout(DomainModel):
    kind: Literal["identify_normalization_layout"] = "identify_normalization_layout"
    data_kind: Literal["fixture", "candidate"]
    bundle_id: Identifier
    base_revision: Text
    nvm_revision: Text
    query: IdentifyQuery
    response_size: StrictInt = Field(gt=0)
    fields: tuple[WireField, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def layout(self):
        require_unique([f.field.key for f in self.fields], "wire field")
        paths = [repr(f.json_path) for f in self.fields if f.json_path is not None]
        require_unique(paths, "JSON field path")
        end = 0
        for item in sorted(self.fields, key=lambda f: (f.offset, f.field.key)):
            if item.offset < end or item.offset + item.length > self.response_size:
                raise ValueError("Overlapping/out-of-bounds wire field")
            end = item.offset + item.length
            if self.data_kind == "fixture":
                if not item.field.field_id.startswith(("TEST.", "FIXTURE.")) or item.provenance.source_type != "fixture":
                    raise ValueError("Fixture layouts need marked fixture fields/evidence")
            if item.provenance.status == "confirmed" and (item.provenance.verified_by is None or item.provenance.verified_date is None):
                raise ValueError("Confirmed field evidence needs reviewer and date")
        return self


class DecodedField(DomainModel):
    definition: WireField
    status: Literal["OBSERVED", "UNKNOWN", "REVIEW", "ERROR"]
    value: object = None
    raw_hex: str | None = None
    reason: Text


class UnmappedBytes(DomainModel):
    offset: StrictInt
    length: StrictInt
    raw_hex: str
    # No normative conclusion: an unmapped gap is not a Reserved region.
    state: Literal["unmapped"] = "unmapped"


class NormalizationReport(DomainModel):
    kind: Literal["identify_normalization_report"] = "identify_normalization_report"
    layout: NormalizationLayout
    capture: CaptureMetadata
    source: SourceFile
    source_format: Literal["raw", "json", "text"]
    layout_source: SourceFile | None = None
    capture_source: SourceFile | None = None
    status: Literal["OBSERVED", "UNKNOWN", "REVIEW", "ERROR"]
    fields: tuple[DecodedField, ...] = ()
    actual_facts: tuple[ActualFact, ...] = ()
    unmapped_bytes: tuple[UnmappedBytes, ...] = ()
    # Preserve the complete tool interpretation without treating it as spec knowledge.
    tool_output: dict[str, object] | None = None
    unmapped_json_keys: tuple[str, ...] = ()
    errors: tuple[Text, ...] = ()


class OfflineValidationReport(DomainModel):
    kind: Literal["offline_fixture_validation"] = "offline_fixture_validation"
    status: Status
    captures: tuple[NormalizationReport, ...]
    validation: ValidationReport | None = None
    errors: tuple[Text, ...] = ()
