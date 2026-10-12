"""Offline CLI integration with Source-built fixture snapshots."""

import json
from pathlib import Path

from typer.testing import CliRunner

from ssd_validator.cli import app

ROOT = Path(__file__).parents[1] / "fixtures" / "rule_pilot"
runner = CliRunner()


def test_pilot_cli_fixture_output_is_deterministic():
    args = ["pilot", "run", "--source", str(ROOT / "knowledge"), "--input", str(ROOT / "input.json")]
    first = runner.invoke(app, args)
    second = runner.invoke(app, args)
    assert first.exit_code == second.exit_code == 0, first.output
    assert first.stdout == second.stdout
    report = json.loads(first.stdout)
    assert report["kind"] == "fixture_validation_report"
    assert report["status"] == "PASS"
    assert report["profile"]["data_kind"] == "fixture"
    assert report["profile"]["bundle"]["base_revision"].startswith("TEST_")


def test_pilot_cli_preserves_missing_and_invalid_results(tmp_path):
    data = json.loads((ROOT / "input.json").read_text(encoding="utf-8"))
    data["actual_facts"] = []
    path = tmp_path / "input.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    result = runner.invoke(app, ["pilot", "run", "--source", str(ROOT / "knowledge"), "--input", str(path)])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["status"] == "UNKNOWN"
    path.write_text('{"context": {}, "context": {}}', encoding="utf-8")
    result = runner.invoke(app, ["pilot", "run", "--source", str(ROOT / "knowledge"), "--input", str(path)])
    assert result.exit_code == 1
    assert "Duplicate JSON key" in result.output
