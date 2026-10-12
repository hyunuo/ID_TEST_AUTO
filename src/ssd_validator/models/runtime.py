"""Offline rule pilot contracts. These are not device collectors or approved specs."""

from typing import Literal

from pydantic import Field, StrictInt, field_validator, model_validator

from .common import DomainModel, Identifier, Text, require_unique
from .effective import EffectiveSnapshot, SourceFile
from .provenance import ChangeRecord, Provenance
from .rules import CheckSpec, OverrideSpec, Value
from .schema import FieldSchema


class FieldRef(DomainModel):
    field_id: Identifier
    index: StrictInt | None = Field(default=None, ge=0)
    bit: StrictInt | None = Field(default=None, ge=0)

    @property
    def key(self) -> str:
        index = f"[{self.index}]" if self.index is not None else ""
        bit = f".bit[{self.bit}]" if self.bit is not None else ""
        return f"{self.field_id}{index}{bit}"


class FactRef(DomainModel):
    source: Literal["context", "actual"]
    path: Text | None = None
    field: FieldRef | None = None

    @field_validator("path", mode="before")
    @classmethod
    def exact_path(cls, value):
        if isinstance(value, str) and value != value.strip():
            raise ValueError("Context paths cannot contain surrounding whitespace")
        return value

    @model_validator(mode="after")
    def shape(self):
        if (self.source == "context" and (self.path is None or self.field is not None)
                or self.source == "actual" and (self.field is None or self.path is not None)):
            raise ValueError("Context references need path; Actual references need field")
        return self


class Condition(DomainModel):
    op: Literal["EQ", "GE", "BIT_SET", "BIT_CLEAR", "AND", "OR", "NOT"]
    ref: FactRef | None = None
    value: Value | None = None
    bit: StrictInt | None = Field(default=None, ge=0)
    children: tuple["Condition", ...] = ()

    @model_validator(mode="after")
    def shape(self):
        if self.op in {"AND", "OR", "NOT"}:
            if self.ref is not None or self.value is not None or self.bit is not None:
                raise ValueError("Logical conditions only accept children")
            if not self.children or self.op == "NOT" and len(self.children) != 1:
                raise ValueError("NOT needs one child; AND/OR need at least one")
        elif self.ref is None or self.children:
            raise ValueError("Leaf condition needs ref and no children")
        elif self.op in {"EQ","GE"}:
            if self.value is None or self.bit is not None:
                raise ValueError("Comparison needs value and no bit")
            if self.op=='GE' and type(self.value) is not int:
                raise ValueError('GE condition requires an integer threshold')
        elif self.bit is None or self.value is not None:
            raise ValueError("Bit condition needs bit and no value")
        return self


class FieldCompare(DomainModel):
    type: Literal["FIELD_COMPARE"]
    operator: Literal["=", "!=", "<", "<=", ">", ">="]
    other: FieldRef


class RuntimeRule(DomainModel):
    rule_id: Identifier
    target: FieldRef
    check: CheckSpec | FieldCompare
    condition: Condition | None = None
    modality: Literal["mandatory", "recommendation", "permission", "description", "behavior"] = "mandatory"
    provenance: Provenance
    history: tuple[ChangeRecord, ...] = ()
    supporting_evidence: tuple[Provenance, ...] = ()
    override: OverrideSpec | None = None
    origin: Literal["snapshot", "fixture", "mapping", "schema"] = "fixture"
    origin_rule_id: Identifier | None = None


class FieldRegistration(DomainModel):
    schema_definition: FieldSchema
    cns: StrictInt = Field(ge=0, le=255)
    csi: StrictInt = Field(ge=0, le=255)
    array_count: StrictInt | None = Field(default=None, gt=0)
    provenance: Provenance
    history: tuple[ChangeRecord, ...] = ()


class BundleSelection(DomainModel):
    bundle_id: Identifier
    base_revision: Text
    nvm_revision: Text
    snapshot_keys: tuple[Text, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def unique(self):
        require_unique(list(self.snapshot_keys), "selected snapshot")
        return self


class RuntimeContext(DomainModel):
    bundle_id: Identifier
    facts: dict[Text, Value] = Field(default_factory=dict)

    @field_validator("facts", mode="before")
    @classmethod
    def exact_keys(cls, values):
        if isinstance(values, dict) and any(isinstance(k, str) and k != k.strip() for k in values):
            raise ValueError("Context fact keys cannot contain surrounding whitespace")
        return values


class ActualFact(DomainModel):
    field: FieldRef
    # Malformed observed values are retained so evaluation can emit ERROR with trace.
    value: object
    source: SourceFile | None = None
    capture_id: Identifier | None = None

    @model_validator(mode="after")
    def whole_field(self):
        if self.field.bit is not None:
            raise ValueError("Actual facts carry whole fields, not decoded bits")
        return self


class CapabilityMapping(DomainModel):
    capability_id: Identifier
    target: FieldRef
    supported: Value
    unsupported: Value
    provenance: Provenance


class PilotMappings(DomainModel):
    execution_mode: Literal['strict', 'experimental'] = 'strict'
    bundle: BundleSelection
    fields: tuple[FieldRegistration, ...]
    rules: tuple[RuntimeRule, ...] = ()
    capabilities: tuple[CapabilityMapping, ...] = ()
    input_source: SourceFile | None = None

    @model_validator(mode="after")
    def unique(self):
        require_unique([f.schema_definition.field_id for f in self.fields], "registered field")
        require_unique([r.rule_id for r in self.rules], "runtime rule")
        require_unique([f"{m.capability_id}:{m.target.key}" for m in self.capabilities], "capability mapping")
        return self


class Observation(DomainModel):
    reference: FactRef
    found: bool
    value: object = None


class ExpectedEntry(DomainModel):
    rule: RuntimeRule
    state: Literal["READY", "CONDITIONAL", "N/A", "UNKNOWN", "REVIEW", "ERROR", "CONFLICT"]
    reason: Text
    condition_state: Literal["TRUE", "FALSE", "UNKNOWN", "DEFERRED", "ERROR"]
    observations: tuple[Observation, ...] = ()


class EffectiveExpectedProfile(DomainModel):
    kind: Literal["effective_expected_profile"] = "effective_expected_profile"
    data_kind: Literal["fixture", "production"] = "fixture"
    execution_mode: Literal['strict', 'experimental'] = 'strict'
    bundle: BundleSelection
    context: RuntimeContext
    fields: tuple[FieldRegistration, ...]
    entries: tuple[ExpectedEntry, ...]
    input_source: SourceFile | None = None
    conflict_analysis: Literal["active_literal_constraints_only"] = "active_literal_constraints_only"


Status = Literal["PASS", "FAIL", "N/A", "REVIEW", "UNKNOWN", "CONFLICT", "ERROR"]


class RuleResult(DomainModel):
    rule: RuntimeRule
    status: Status
    reason: Text
    condition_state: Literal["TRUE", "FALSE", "UNKNOWN", "DEFERRED", "ERROR"]
    observations: tuple[Observation, ...] = ()
    related_rules: tuple[Identifier, ...] = ()


class InputError(DomainModel):
    field: FieldRef
    value: object
    reason: Text


class ValidationReport(DomainModel):
    kind: Literal["fixture_validation_report", "experimental_validation_report"] = "fixture_validation_report"
    authoritative: Literal[False] = False
    profile: EffectiveExpectedProfile
    status: Status
    results: tuple[RuleResult, ...]
    input_errors: tuple[InputError, ...] = ()
    actual_facts: tuple[ActualFact, ...] = ()


class PilotRequest(DomainModel):
    context: RuntimeContext
    snapshots: tuple[EffectiveSnapshot, ...]
    mappings: PilotMappings
    actual_facts: tuple[ActualFact, ...] = ()


class FieldBinding(DomainModel):
    field_id: Identifier
    cns: StrictInt = Field(ge=0, le=255)
    csi: StrictInt = Field(ge=0, le=255)
    array_count: StrictInt | None = Field(default=None, gt=0)


class PilotInput(DomainModel):
    """Human-managed fixture configuration; snapshots are always built from YAML."""
    context: RuntimeContext
    bundle: BundleSelection
    bindings: tuple[FieldBinding, ...]
    rules: tuple[RuntimeRule, ...] = ()
    capabilities: tuple[CapabilityMapping, ...] = ()
    actual_facts: tuple[ActualFact, ...] = ()

    @model_validator(mode="after")
    def unique(self):
        require_unique([b.field_id for b in self.bindings], "field binding")
        return self
