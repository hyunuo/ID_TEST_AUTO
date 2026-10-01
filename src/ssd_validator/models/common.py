"""Strict, closed data contracts shared by source and generated models."""

from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, StringConstraints, model_validator

Text = Annotated[str, StringConstraints(strict=True, min_length=1, strip_whitespace=True)]
Identifier = Annotated[Text, StringConstraints(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]*$")]


def portable_version(value: str) -> str:
    reserved = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)),
                *(f"LPT{i}" for i in range(1, 10))}
    if value.endswith(".") or value.split(".", 1)[0].upper() in reserved:
        raise ValueError("Version label is not a portable file name")
    return value


VersionLabel = Annotated[Text, StringConstraints(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]*$"),
                         AfterValidator(portable_version)]


def _immutable(*args, **kwargs):
    raise TypeError("Domain collections are immutable")


class FrozenDict(dict):
    __setitem__ = __delitem__ = clear = pop = popitem = setdefault = update = __ior__ = _immutable

    def __deepcopy__(self, memo):
        return self


class FrozenList(list):
    __setitem__ = __delitem__ = append = clear = extend = insert = pop = remove = reverse = sort = _immutable
    __iadd__ = __imul__ = _immutable

    def __deepcopy__(self, memo):
        return self


def freeze(value):
    if isinstance(value, (FrozenDict, FrozenList)):
        return value
    if isinstance(value, dict):
        return FrozenDict({key: freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return FrozenList(freeze(item) for item in value)
    if isinstance(value, tuple):
        return tuple(freeze(item) for item in value)
    return value


def thaw(value):
    """Create a mutable work buffer without altering immutable domain inputs."""
    if isinstance(value, dict):
        return {key: thaw(item) for key, item in value.items()}
    if isinstance(value, list):
        return [thaw(item) for item in value]
    if isinstance(value, tuple):
        return tuple(thaw(item) for item in value)
    return value


class DomainModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, validate_default=True,
                              populate_by_name=True, serialize_by_alias=True)

    @model_validator(mode="after")
    def freeze_collections(self):
        for name in type(self).model_fields:
            object.__setattr__(self, name, freeze(getattr(self, name)))
        return self

    def model_copy(self, *, update=None, deep=False):
        updates = {key: freeze(value) for key, value in update.items()} if update else None
        return super().model_copy(update=updates, deep=deep)


def require_unique(values: list[str], label: str) -> None:
    if len(values) != len(set(values)):
        raise ValueError(f"Duplicate {label}")
