"""Offline file adapter: explicit target layout and recorded capture metadata."""

import json
from hashlib import sha256
from pathlib import Path

from ssd_validator.analyzer.actual_normalizer import normalize_json, normalize_raw
from ssd_validator.application.rule_pilot import _unique_object
from ssd_validator.errors import KnowledgeError
from ssd_validator.models.actual_data import CaptureMetadata, NormalizationLayout
from ssd_validator.models.effective import SourceFile


def _constant(value):
    raise ValueError(f"Non-JSON numeric constant: {value}")


def _read(path):
    buffer = path.read_bytes()
    payload = json.loads(buffer.decode("utf-8"), object_pairs_hook=_unique_object, parse_constant=_constant)
    return payload, buffer


def run_normalization(layout_path: Path, capture_path: Path, *, raw_path: Path | None = None,
                      json_path: Path | None = None):
    if (raw_path is None) == (json_path is None):
        raise KnowledgeError("ACTUAL_INPUT", "Choose exactly one saved --raw or --json response; no automatic fallback")
    layout_data, layout_bytes = _read(layout_path)
    capture_data, capture_bytes = _read(capture_path)
    layout = NormalizationLayout.model_validate(layout_data)
    capture = CaptureMetadata.model_validate(capture_data)
    if raw_path is not None:
        report = normalize_raw(layout, capture, raw_path.read_bytes(), source_path=raw_path.as_posix())
    else:
        payload, buffer = _read(json_path)
        if not isinstance(payload, dict):
            raise KnowledgeError("ACTUAL_JSON_SHAPE", "Expected a JSON object")
        report = normalize_json(layout, capture, payload, source_path=json_path.as_posix(), source_bytes=buffer)
    return report.model_copy(update={
        "layout_source": SourceFile(path=layout_path.as_posix(), sha256=sha256(layout_bytes).hexdigest()),
        "capture_source": SourceFile(path=capture_path.as_posix(), sha256=sha256(capture_bytes).hexdigest()),
    })
