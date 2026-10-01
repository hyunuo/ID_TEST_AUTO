"""Immutable-by-contract generated snapshots, not human-managed source knowledge."""

from typing import Literal

from pydantic import Field

from .common import DomainModel, Text
from .identifiers import SpecVersion
from .provenance import ChangeRecord
from .rules import RequirementRule
from .schema import FieldSchema


class EffectiveField(DomainModel):
    field_schema: FieldSchema = Field(alias="schema")
    introduced_in: SpecVersion
    last_changed_in: SpecVersion
    history: tuple[ChangeRecord, ...]

    @property
    def schema(self) -> FieldSchema:
        return self.field_schema


class EffectiveRule(DomainModel):
    rule: RequirementRule
    introduced_in: SpecVersion
    last_changed_in: SpecVersion
    history: tuple[ChangeRecord, ...]


class EffectiveSnapshot(DomainModel):
    kind: Literal["effective_snapshot"] = "effective_snapshot"
    spec: SpecVersion
    data_kind: Literal["fixture", "production"]
    parent: SpecVersion | None = None
    schema_ref: SpecVersion | None = None
    fields: tuple[EffectiveField, ...] = ()
    rules: tuple[EffectiveRule, ...] = ()
    changes: tuple[ChangeRecord, ...] = ()


class SourceFile(DomainModel):
    path: Text
    sha256: Text


class BuildManifest(DomainModel):
    format_version: Literal[1] = 1
    builder_version: Text
    git_commit: Text | None
    knowledge_hash: Text
    sources: tuple[SourceFile, ...]
    snapshots: tuple[SpecVersion, ...]
