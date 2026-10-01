"""Source evidence and build-derived lineage; unknown review metadata stays null."""

from datetime import date
from enum import StrEnum
from typing import Literal

from .common import DomainModel, Text
from .identifiers import SpecVersion


class KnowledgeStatus(StrEnum):
    CONFIRMED = "confirmed"
    PROVISIONAL = "provisional"
    CANDIDATE = "candidate"
    DEPRECATED = "deprecated"


class SourceDocument(DomainModel):
    source_type: Literal["spec", "policy", "fixture"]
    source_document: Text
    source_version: Text

    @property
    def key(self) -> tuple[str, str, str]:
        return self.source_type, self.source_document, self.source_version


class Provenance(SourceDocument):
    source_section: Text
    status: KnowledgeStatus
    verified_by: Text | None = None
    verified_date: date | None = None


class ChangeRecord(DomainModel):
    action: Literal["BASE", "ADD", "MODIFY", "REMOVE", "REDEFINE", "DEPRECATE", "REQUIREMENT_CHANGE"]
    spec: SpecVersion
    target: Text
    provenance: Provenance
    source_file: Text
    source_hash: Text
