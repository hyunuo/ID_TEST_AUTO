"""Reviewed-by-humans later: PDF extraction contracts are never authoritative rules."""

from typing import Literal

from pydantic import Field, StrictBool, StrictInt, model_validator

from .common import DomainModel, Identifier, Text, VersionLabel, require_unique

State = Literal["defined", "reserved", "vendor_specific", "delegated", "unknown"]


class DocumentAnchor(DomainModel):
    document_id: Identifier
    section: Text
    figure: Text | None = None
    pdf_page: StrictInt = Field(ge=1)
    printed_page: Text | None = None


class SpecDocument(DomainModel):
    document_id: Identifier
    component: Literal["NVME_BASE", "NVME_NVM"]
    revision: VersionLabel
    filename: Text
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    pages: StrictInt = Field(gt=0)
    inherits: Identifier | None = None

    @model_validator(mode="after")
    def filename_only(self):
        if any(c in self.filename for c in ("/", "\\", ":")) or self.filename in {".", ".."}:
            raise ValueError("Document filename must be a basename")
        return self


class SpecBundle(DomainModel):
    bundle_id: VersionLabel
    base_document: Identifier
    nvm_document: Identifier
    structure_ids: tuple[Identifier, ...] = Field(min_length=1)


class CandidateCatalog(DomainModel):
    kind: Literal["candidate_catalog"]
    format_version: Literal[1]
    documents: tuple[SpecDocument, ...] = Field(min_length=1)
    bundles: tuple[SpecBundle, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def identities(self):
        require_unique([d.document_id for d in self.documents], "document")
        require_unique([b.bundle_id.casefold() for b in self.bundles], "bundle")
        return self


class CandidateBitField(DomainModel):
    name: Text
    lsb: StrictInt = Field(ge=0)
    msb: StrictInt = Field(ge=0)
    state: State
    evidence: tuple[DocumentAnchor, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def ordered(self):
        if self.msb < self.lsb:
            raise ValueError("Reversed bit range")
        return self


class CandidateArray(DomainModel):
    count: StrictInt = Field(gt=0)
    stride_bytes: StrictInt = Field(gt=0)


class CandidateField(DomainModel):
    field_id: Identifier
    name: Text
    byte_offset: StrictInt = Field(ge=0)
    byte_length: StrictInt = Field(gt=0)
    state: State
    evidence: tuple[DocumentAnchor, ...] = Field(min_length=1)
    bit_fields: tuple[CandidateBitField, ...] = ()
    array: CandidateArray | None = None
    nested_template_id: Identifier | None = None
    children: tuple["CandidateField", ...] = ()
    description: str
    review_status: Literal["candidate"]

    @model_validator(mode="after")
    def bounds(self):
        # Children are relative to one array element, otherwise the enclosing field.
        limit = self.array.stride_bytes if self.array else self.byte_length
        if self.array and self.array.count * limit > self.byte_length:
            raise ValueError("Array extends beyond field storage")
        if any(bit.msb >= limit * 8 for bit in self.bit_fields):
            raise ValueError("Bit range outside field/element")
        occupied = set()
        for bit in self.bit_fields:
            indices = set(range(bit.lsb, bit.msb + 1))
            if occupied & indices:
                raise ValueError("Overlapping bit ranges")
            occupied |= indices
        require_unique([f.field_id for f in self.children], "child field")
        end = 0
        for child in sorted(self.children, key=lambda f: f.byte_offset):
            if child.byte_offset < end or child.byte_offset + child.byte_length > limit:
                raise ValueError("Overlapping/out-of-bounds child field")
            end = child.byte_offset + child.byte_length
        return self


class SourceRow(DomainModel):
    pdf_page: StrictInt = Field(ge=1)
    text: Text


class CandidateTemplate(DomainModel):
    template_id: Identifier
    size_bytes: StrictInt = Field(gt=0)
    coordinate_system: Text
    bit_fields: tuple[CandidateBitField, ...]
    source_rows: tuple[SourceRow, ...]
    evidence: tuple[DocumentAnchor, ...] = Field(min_length=1)
    review_status: Literal["candidate"]
    coverage_status: Literal["partial", "complete"]

    @model_validator(mode="after")
    def bounds(self):
        end = 0
        for bit in sorted(self.bit_fields, key=lambda b: b.lsb):
            if bit.lsb < end or bit.msb >= self.size_bytes * 8:
                raise ValueError("Overlapping/out-of-bounds template bits")
            if self.coverage_status == "complete" and bit.lsb != end:
                raise ValueError("Complete template has gaps")
            end = bit.msb + 1
        if self.coverage_status == "complete" and end != self.size_bytes * 8:
            raise ValueError("Complete template has gaps")
        return self


class CandidateStructure(DomainModel):
    structure_id: Identifier
    document_id: Identifier
    cns: StrictInt = Field(ge=0, le=255)
    csi: StrictInt | None = Field(default=None, ge=0, le=255)
    size_bytes: StrictInt = Field(gt=0)
    fields: tuple[CandidateField, ...]
    evidence: tuple[DocumentAnchor, ...] = Field(min_length=1)
    unresolved: tuple[Text, ...] = ()
    coverage_status: Literal["complete", "partial"]
    byte_coverage_complete: StrictBool = False
    coverage_gaps: tuple[tuple[StrictInt, StrictInt], ...] = ()
    coverage_overlaps: tuple[tuple[StrictInt, StrictInt], ...] = ()
    source_rows: tuple[SourceRow, ...] = ()

    @model_validator(mode="after")
    def bounds(self):
        require_unique([f.field_id for f in self.fields], "field")
        end = 0
        gaps = []
        for field in sorted(self.fields, key=lambda f: f.byte_offset):
            if field.byte_offset < end or field.byte_offset + field.byte_length > self.size_bytes:
                raise ValueError("Overlapping/out-of-bounds fields within source structure")
            if self.coverage_status == "complete" and field.byte_offset != end:
                raise ValueError("Complete structure has a byte gap")
            if field.byte_offset > end:
                gaps.append((end, field.byte_offset - 1))
            end = field.byte_offset + field.byte_length
        if end < self.size_bytes:
            gaps.append((end, self.size_bytes - 1))
        if self.byte_coverage_complete and gaps:
            raise ValueError("Byte coverage claimed complete despite gaps")
        if self.coverage_gaps and tuple(gaps) != self.coverage_gaps:
            raise ValueError("Declared coverage gaps disagree with layout")
        if self.coverage_overlaps:
            raise ValueError("Resolve within-document extraction overlaps before compiling")
        if self.coverage_status == "complete" and (end != self.size_bytes or self.unresolved):
            raise ValueError("Complete structure has gaps or unresolved details")
        return self


class StructureCandidates(DomainModel):
    kind: Literal["structure_candidates"]
    format_version: Literal[1]
    structures: tuple[CandidateStructure, ...]
    nested_templates: tuple[CandidateTemplate, ...] = ()
    review_status: Literal["candidate"] = "candidate"
    extraction_note: str = ""
    document_hashes: dict[Identifier, str] = Field(default_factory=dict)


class CandidateRequirement(DomainModel):
    requirement_id: Identifier
    document_id: Identifier
    structure_ids: tuple[Identifier, ...]
    field_names: tuple[Text, ...]
    classification: Literal["mandatory", "recommendation", "permission", "description", "behavior", "unresolved"]
    statement: Text
    condition: Text | None
    dependencies: tuple[Text, ...]
    evidence: tuple[DocumentAnchor, ...] = Field(min_length=1)
    review_status: Literal["candidate"]
    evaluation_status: Literal["not_executable", "unresolved"]
    unresolved: tuple[Text, ...]


class CoverageEntry(DomainModel):
    document_id: Identifier
    pdf_page: StrictInt = Field(ge=1)
    status: Literal["extracted", "unresolved", "excluded"]
    reason: Text


class RequirementCandidates(DomainModel):
    kind: Literal["requirement_candidates"]
    format_version: Literal[1]
    requirements: tuple[CandidateRequirement, ...]
    coverage: tuple[CoverageEntry, ...]
    unresolved: tuple[Text, ...]
    document_hashes: dict[Identifier, str] = Field(default_factory=dict)
