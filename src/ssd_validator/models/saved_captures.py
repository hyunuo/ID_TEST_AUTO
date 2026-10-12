"""Transport for saved responses; absent collection metadata is never inferred."""
import base64
from typing import Literal
from pydantic import Field, StrictInt, model_validator
from .common import DomainModel, Identifier, Text


class SavedCapture(DomainModel):
    capture_id: Identifier
    filename: Text
    content_base64: Text
    command: Literal['id-ctrl', 'id-ns', 'identify']
    source_format: Literal['text', 'json', 'raw'] = 'text'
    dut_id: Text | None = None
    session_id: Text | None = None
    collected_at: Text | None = None
    cns: StrictInt | None = Field(default=None, ge=0, le=255)
    csi: StrictInt | None = Field(default=None, ge=0, le=255)
    nsid: StrictInt | None = Field(default=None, ge=0, le=0xffffffff)
    tool_name: Text = 'UNKNOWN'
    tool_version: Text = 'UNKNOWN'
    tool_commit: Text | None = None

    def data(self):
        return base64.b64decode(self.content_base64, validate=True)

    @model_validator(mode='after')
    def size(self):
        if len(self.data()) > 1024 * 1024:
            raise ValueError('Each saved response must be at most 1 MiB')
        return self


class SavedCaptureSet(DomainModel):
    format: Literal['ssd-validator-captures-v1'] = 'ssd-validator-captures-v1'
    captures: tuple[SavedCapture, ...] = Field(min_length=1, max_length=16)

    @model_validator(mode='after')
    def unique(self):
        if len({c.capture_id for c in self.captures}) != len(self.captures):
            raise ValueError('Duplicate capture_id')
        return self
