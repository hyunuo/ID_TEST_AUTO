"""Exercise the installed application commands and preserve failure outcomes."""

import json

from typer.testing import CliRunner

from conftest import edit_yaml
from ssd_validator.cli import app

runner = CliRunner()


def test_cli_knowledge_build(source_root, tmp_path):
    output = tmp_path / "generated"
    result = runner.invoke(app, ["knowledge", "build", "--source", str(source_root), "--output", str(output)])
    assert result.exit_code == 0, result.output
    assert "Built 7 snapshots" in result.output
    final = json.loads((output / "effective/test/fixture-v4.json").read_text())
    assert final["kind"] == "effective_snapshot" and final["data_kind"] == "fixture"
    assert len(final["fields"]) == 4


def test_cli_selection(source_root, tmp_path):
    result = runner.invoke(app, ["knowledge", "build", "--source", str(source_root), "--output", str(tmp_path / "output"),
                                 "--spec", "ocp", "--version", "fixture-v2", "--clean"])
    assert result.exit_code == 0, result.output
    assert "Built 3 snapshots" in result.output


def test_cli_spec_diff(source_root):
    result = runner.invoke(app, ["spec", "diff", "--source", str(source_root), "--family", "test",
                                 "--from", "fixture-v1", "--to", "fixture-v4"])
    assert result.exit_code == 0, result.output
    diff = json.loads(result.stdout)
    assert any(change["target"] == "TEST.ID_CTRL.OBSOLETE" and change["action"] == "removed" for change in diff["changes"])


def test_invalid_delta_creates_no_artifacts(editable_knowledge, tmp_path):
    edit_yaml(editable_knowledge, "schema/modify.yaml", lambda d: d["schema_changes"][0]["previous"].update(state="defined"))
    output = tmp_path / "output"
    result = runner.invoke(app, ["knowledge", "build", "--source", str(editable_knowledge), "--output", str(output)])
    assert result.exit_code != 0
    assert "GUARD_MISMATCH" in result.output
    assert not output.exists()


def test_failed_build_preserves_previous_artifacts(editable_knowledge, tmp_path):
    output = tmp_path / "output"
    args = ["knowledge", "build", "--source", str(editable_knowledge), "--output", str(output)]
    assert runner.invoke(app, args).exit_code == 0
    before = {path.relative_to(output): path.read_bytes() for path in output.rglob("*") if path.is_file()}
    edit_yaml(editable_knowledge, "schema/modify.yaml", lambda d: d["schema_changes"][0]["previous"].update(state="defined"))
    result = runner.invoke(app, args + ["--clean"])
    assert result.exit_code != 0
    after = {path.relative_to(output): path.read_bytes() for path in output.rglob("*") if path.is_file()}
    assert before == after


def test_unknown_family_and_version_fail(source_root, tmp_path):
    args = ["knowledge", "build", "--source", str(source_root), "--output", str(tmp_path / "output")]
    assert runner.invoke(app, args + ["--spec", "NOT_A_FAMILY"]).exit_code != 0
    assert runner.invoke(app, args + ["--spec", "TEST", "--version", "TEST_MISSING"]).exit_code != 0


def test_empty_production_knowledge_is_not_a_success(tmp_path):
    source = tmp_path / "knowledge"
    source.mkdir()
    result = runner.invoke(app, ["knowledge", "build", "--source", str(source), "--output", str(tmp_path / "output")])
    assert result.exit_code != 0 and "NO_SOURCE" in result.output


def test_cli_exposes_only_phase1_commands():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0 and "knowledge" in result.output and "spec" in result.output
    assert runner.invoke(app, ["run"]).exit_code != 0
