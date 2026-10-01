"""Strict, closed data contracts shared by source and generated models."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

Text = Annotated[str, StringConstraints(strict=True, min_length=1, strip_whitespace=True)]
Identifier = Annotated[Text, StringConstraints(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]*$")]
VersionLabel = Annotated[Text, StringConstraints(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]*$")]


class DomainModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, validate_default=True,
                              populate_by_name=True, serialize_by_alias=True)


def require_unique(values: list[str], label: str) -> None:
    if len(values) != len(set(values)):
        raise ValueError(f"Duplicate {label}")
