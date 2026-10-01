"""Spec and target identity; version labels are never numerically ordered."""

from enum import StrEnum

from pydantic import Field, StrictInt

from .common import DomainModel, Identifier, Text, VersionLabel


class SpecFamily(StrEnum):
    NVME = "NVME"
    OCP = "OCP"
    MFND = "MFND"
    TEST = "TEST"


class SpecVersion(DomainModel):
    spec_family: SpecFamily
    version: VersionLabel

    @property
    def key(self) -> str:
        return f"{self.spec_family.value}:{self.version}"


class TargetRef(DomainModel):
    field_id: Identifier
    command: Text | None = None
    bit: StrictInt | None = Field(default=None, ge=0)

    @property
    def key(self) -> str:
        suffix = f"[{self.bit}]" if self.bit is not None else ""
        return f"{self.field_id}{suffix}"
