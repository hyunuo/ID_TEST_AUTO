"""Schema meaning is independent of expected values and validation behavior."""

from enum import StrEnum
from typing import Literal

from pydantic import Field, StrictInt, model_validator

from .common import DomainModel, Identifier, Text, require_unique


class SemanticState(StrEnum):
    RESERVED = "reserved"
    DEFINED = "defined"


class ValidationBehavior(DomainModel):
    behavior: Literal["must_be_zero"]


class BitSchema(DomainModel):
    bit: StrictInt = Field(ge=0)
    state: SemanticState
    feature: Identifier | None = None
    validation: ValidationBehavior | None = None
    lifecycle: Literal["active", "deprecated"] = "active"


class FieldSchema(DomainModel):
    field_id: Identifier
    name: Text
    command: Text
    offset: StrictInt = Field(ge=0)
    length: StrictInt = Field(gt=0)
    endian: Literal["little", "big", "not_applicable"]
    value_type: Literal["integer", "bitmask", "string", "bytes"]
    state: SemanticState | None = None
    validation: ValidationBehavior | None = None
    bits: tuple[BitSchema, ...] = ()
    lifecycle: Literal["active", "deprecated"] = "active"

    @model_validator(mode="after")
    def validate_bits(self):
        require_unique([str(bit.bit) for bit in self.bits], "bit index")
        if self.bits and self.value_type != "bitmask":
            raise ValueError("Bit definitions require value_type=bitmask")
        if any(bit.bit >= self.length * 8 for bit in self.bits):
            raise ValueError("Bit index outside the declared field length")
        return self
