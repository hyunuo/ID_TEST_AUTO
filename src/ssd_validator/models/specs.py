"""Human-managed base, delta and reference-catalog contracts."""

from enum import StrEnum
from typing import Literal

from pydantic import Field, JsonValue, field_validator, model_validator

from .common import DomainModel, Identifier, Text, VersionLabel, require_unique
from .identifiers import SpecFamily, SpecVersion, TargetRef
from .provenance import Provenance, SourceDocument
from .rules import RequirementRule
from .schema import FieldSchema


class DeltaAction(StrEnum):
    ADD = "ADD"
    MODIFY = "MODIFY"
    REMOVE = "REMOVE"
    REDEFINE = "REDEFINE"
    DEPRECATE = "DEPRECATE"
    REQUIREMENT_CHANGE = "REQUIREMENT_CHANGE"


class SchemaChange(DomainModel):
    action: DeltaAction
    target: TargetRef
    previous: dict[str, JsonValue] | None = None
    current: dict[str, JsonValue] | None = None
    provenance: Provenance | None = None

    @field_validator("action", mode="before")
    @classmethod
    def action_label(cls, value):
        return value.upper() if isinstance(value, str) else value

    @model_validator(mode="after")
    def validate_payload(self):
        validate_change_payload(self.action, self.previous, self.current)
        if self.action == DeltaAction.REQUIREMENT_CHANGE:
            raise ValueError("REQUIREMENT_CHANGE applies to rules, not schema")
        if self.action == DeltaAction.DEPRECATE and self.current != {"lifecycle": "deprecated"}:
            raise ValueError("Schema DEPRECATE requires current.lifecycle=deprecated only")
        return self


class RuleChange(DomainModel):
    action: DeltaAction
    rule_id: Identifier
    previous: dict[str, JsonValue] | None = None
    current: dict[str, JsonValue] | None = None
    provenance: Provenance | None = None

    @field_validator("action", mode="before")
    @classmethod
    def action_label(cls, value):
        return value.upper() if isinstance(value, str) else value

    @model_validator(mode="after")
    def validate_payload(self):
        validate_change_payload(self.action, self.previous, self.current)
        if self.action == DeltaAction.REQUIREMENT_CHANGE:
            if set(self.current or {}) != {"requirement"}:
                raise ValueError("REQUIREMENT_CHANGE only updates requirement")
        if self.action == DeltaAction.DEPRECATE and self.current != {"provenance": {"status": "deprecated"}}:
            raise ValueError("Rule DEPRECATE requires current.provenance.status=deprecated only")
        return self


def validate_change_payload(action, previous, current) -> None:
    if action == DeltaAction.ADD:
        if previous is not None or not current:
            raise ValueError("ADD requires current and an absent previous")
    else:
        if not previous:
            raise ValueError(f"{action} requires a nonempty previous guard")
        if action == DeltaAction.REMOVE:
            if current is not None:
                raise ValueError("REMOVE requires an absent current")
        elif not current:
            raise ValueError(f"{action} requires current")


class SpecSource(DomainModel):
    spec_family: SpecFamily
    version: VersionLabel
    data_kind: Literal["fixture", "production"]
    provenance: Provenance

    @property
    def spec(self) -> SpecVersion:
        return SpecVersion(spec_family=self.spec_family, version=self.version)


class BaseSpec(SpecSource):
    kind: Literal["base"]
    command: Text | None = None
    schema_ref: SpecVersion | None = None
    fields: tuple[FieldSchema, ...] = ()
    rules: tuple[RequirementRule, ...] = ()

    @model_validator(mode="before")
    @classmethod
    def explicit_command(cls, value):
        if isinstance(value, dict) and value.get("command"):
            value = dict(value)
            value["fields"] = [
                {"command": value["command"], **field} if isinstance(field, dict) else field
                for field in value.get("fields", [])
            ]
        return value

    @model_validator(mode="after")
    def validate_base(self):
        require_unique([field.field_id for field in self.fields], "field_id")
        require_unique([rule.rule_id for rule in self.rules], "rule_id")
        if self.spec_family in {SpecFamily.OCP, SpecFamily.MFND} and self.fields:
            raise ValueError("OCP/MFND requirements must reference a schema, not define fields")
        if self.spec_family in {SpecFamily.NVME, SpecFamily.TEST} and self.schema_ref is not None:
            raise ValueError("Schema bases do not inherit fields through schema_ref; use an explicit delta")
        if self.spec_family in {SpecFamily.OCP, SpecFamily.MFND} and self.rules and self.schema_ref is None:
            raise ValueError("Requirement bases with rules require an explicit schema_ref")
        if self.command and any(field.command != self.command for field in self.fields):
            raise ValueError("Base command and field command disagree")
        return self


class SchemaReferenceChange(DomainModel):
    previous: SpecVersion | None = Field(...)
    current: SpecVersion
    provenance: Provenance | None = None


class DeltaSpec(SpecSource):
    kind: Literal["delta"]
    inherits: VersionLabel
    schema_changes: tuple[SchemaChange, ...] = ()
    changes: tuple[RuleChange, ...] = ()
    schema_ref_change: SchemaReferenceChange | None = None

    @model_validator(mode="after")
    def validate_delta(self):
        if self.schema_ref_change is not None and self.spec_family not in {SpecFamily.OCP, SpecFamily.MFND}:
            raise ValueError("Only requirement deltas can change schema_ref")
        if self.spec_family in {SpecFamily.OCP, SpecFamily.MFND} and self.schema_changes:
            raise ValueError("OCP/MFND deltas change requirements, not field schemas")
        require_unique([change.rule_id for change in self.changes], "delta rule target")
        by_field: dict[str, set[int | None]] = {}
        for change in self.schema_changes:
            bits = by_field.setdefault(change.target.field_id, set())
            if change.target.bit in bits or None in bits or (bits and change.target.bit is None):
                raise ValueError("Overlapping schema changes in one delta")
            bits.add(change.target.bit)
        return self


class FeatureDefinition(DomainModel):
    feature_id: Identifier
    aliases: tuple[Text, ...] = ()
    provenance: Provenance


class KnowledgeCatalog(DomainModel):
    kind: Literal["catalog"]
    sources: tuple[SourceDocument, ...]
    features: tuple[FeatureDefinition, ...] = ()
    capabilities: tuple[Identifier, ...] = ()
    derived_functions: tuple[Identifier, ...] = ()

    @model_validator(mode="after")
    def validate_catalog(self):
        require_unique([str(source.key) for source in self.sources], "source document")
        require_unique([feature.feature_id for feature in self.features], "feature_id")
        require_unique(list(self.capabilities), "capability_id")
        require_unique(list(self.derived_functions), "derived function")
        return self
