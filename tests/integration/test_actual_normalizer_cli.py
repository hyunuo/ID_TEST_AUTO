"""Normalize saved synthetic captures, without device/network execution."""

import json
from pathlib import Path

from typer.testing import CliRunner

from ssd_validator.cli import app

ROOT = Path(__file__).parents[1] / "fixtures" / "actual_normalization"
runner = CliRunner()


def args():
    return ["actual", "normalize", "--layout", str(ROOT / "layout.json"), "--capture", str(ROOT / "capture.json")]


def test_offline_raw_cli_and_determinism():
    first = runner.invoke(app, [*args(), "--raw", str(ROOT / "response.raw")])
    second = runner.invoke(app, [*args(), "--raw", str(ROOT / "response.raw")])
    assert first.exit_code == 0, first.output
    assert first.stdout == second.stdout
    report = json.loads(first.stdout)
    assert report["status"] == "OBSERVED"
    assert report["capture"]["tool_version"] == "TEST.newer-decoder"
    assert report["layout"]["base_revision"] == "TEST_BASE.fixture-v1"


def test_json_cli_retains_unknown_newer_fields():
    result = runner.invoke(app, [*args(), "--json", str(ROOT / "response.json")])
    assert result.exit_code == 0, result.output
    report = json.loads(result.stdout)
    assert report["unmapped_json_keys"] == ["test_newer_only_feature"]
    assert "test_newer_only_feature" in report["tool_output"]


def test_invalid_capture_length_and_options(tmp_path):
    path = tmp_path / "short.raw"
    path.write_bytes(b"\x00")
    result = runner.invoke(app, [*args(), "--raw", str(path)])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["status"] == "ERROR"
    result = runner.invoke(app, args())
    assert result.exit_code == 1
    assert "ACTUAL_INPUT" in result.output
