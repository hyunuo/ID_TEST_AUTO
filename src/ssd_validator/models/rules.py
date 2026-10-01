"""Typed requirement payloads. This phase preserves rules; it does not run a DUT resolver."""

from typing import Annotated, Literal

from pydantic import Field, StrictBool, StrictInt, StrictStr, model_validator

from .common import DomainModel, Identifier, Text
from .identifiers import TargetRef
from .provenance import Provenance

Value = StrictInt | StrictStr | StrictBool


class ExactCheck(DomainModel):
    type: Literal["EXACT"]
    value: Value


class BoundCheck(DomainModel):
    type: Literal["MIN", "MAX"]
    value: StrictInt


class RangeCheck(DomainModel):
    type: Literal["RANGE"]
    min: StrictInt
    max: StrictInt

    @model_validator(mode="after")
    def valid_range(self):
        if self.min > self.max:
            raise ValueError("Impossible range: min exceeds max")
        return self


class EnumCheck(DomainModel):
    type: Literal["ENUM"]
    values: tuple[Value, ...] = Field(min_length=1)


class BitCheck(DomainModel):
    type: Literal["BIT_SET", "BIT_CLEAR"]
    bit: StrictInt | None = Field(default=None, ge=0)


class MaskCheck(DomainModel):
    type: Literal["MASK"]
    mask: StrictInt = Field(ge=0)
    value: StrictInt = Field(ge=0)

    @model_validator(mode="after")
    def valid_mask(self):
        if self.value & ~self.mask:
            raise ValueError("MASK value contains bits outside mask")
        return self


class LookupCheck(DomainModel):
    type: Literal["LOOKUP"]
    key: Text
    values: dict[StrictInt | StrictStr, Value] = Field(min_length=1)


class DerivedCheck(DomainModel):
    type: Literal["DERIVED"]
    function: Identifier
    inputs: tuple[Text, ...] = Field(min_length=1)


class ApplicabilityCheck(DomainModel):
    type: Literal["OPTIONAL", "NOT_APPLICABLE"]


class CapabilityCheck(DomainModel):
    type: Literal["CAPABILITY"]
    capability_id: Identifier
    support: Literal["supported", "unsupported"]


CheckSpec = Annotated[
    ExactCheck | BoundCheck | RangeCheck | EnumCheck | BitCheck | MaskCheck
    | LookupCheck | DerivedCheck | ApplicabilityCheck | CapabilityCheck,
    Field(discriminator="type"),
]


class OverrideSpec(DomainModel):
    enabled: StrictBool
    overrides: tuple[Identifier, ...] = Field(min_length=1)
    reason: Text
    provenance: Provenance


class RequirementRule(DomainModel):
    rule_id: Identifier
    target: TargetRef
    check: CheckSpec
    requirement: Literal["required", "optional"] | None = None
    applies_when: dict[Text, Value] = Field(default_factory=dict)
    applicable_when: dict[Text, Value] = Field(default_factory=dict)
    provenance: Provenance | None = None
    override: OverrideSpec | None = None

    @model_validator(mode="after")
    def validate_target(self):
        if self.target.command is None:
            raise ValueError("Requirement target must include command")
        if isinstance(self.check, BitCheck):
            target_bit, check_bit = self.target.bit, self.check.bit
            if target_bit is None and check_bit is None:
                raise ValueError("Bit check requires a target or check bit")
            if target_bit is not None and check_bit is not None and target_bit != check_bit:
                raise ValueError("target.bit and check.bit disagree")
        return self
