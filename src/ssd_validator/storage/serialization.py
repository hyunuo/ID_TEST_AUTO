"""Canonical semantic artifacts have stable ordering and no wall-clock fields."""

import json

from pydantic import BaseModel


def canonical_bytes(value: BaseModel | dict) -> bytes:
    payload = value.model_dump(mode="json") if isinstance(value, BaseModel) else value
    return (json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
