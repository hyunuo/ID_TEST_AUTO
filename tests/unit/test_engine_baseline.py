"""Refactoring guard: verdicts on synthetic TEST inputs must match the stored engine baseline."""

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SPEC = json.loads((ROOT / "spec/manifest.json").read_text(encoding="utf-8"))


def load_tool():
    spec = importlib.util.spec_from_file_location("capture_baseline", ROOT / "tools/capture_baseline.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_verdicts_match_stored_baseline():
    if not all((ROOT / "spec" / d["pdf"]).is_file() for d in SPEC["documents"]):
        pytest.skip("Registration needs the original PDFs in spec/")
    tool = load_tool()
    current = json.dumps(tool.run(), ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    assert current == tool.BASELINE.read_text(encoding="utf-8"), "Run tools/capture_baseline.py to see the change"
