import json
from pathlib import Path

from typer.testing import CliRunner

from ssd_validator.application.database_workflow import DatabaseWorkflow
from ssd_validator.cli import app

ROOT = Path(__file__).resolve().parents[2]


def test_database_status_backup_restore_and_no_overwrite(tmp_path):
    source = tmp_path / 'source.sqlite3'
    workflow = DatabaseWorkflow(ROOT, source)
    runner = CliRunner()
    status = runner.invoke(app, ['database', 'status', '--database', str(source)])
    assert status.exit_code == 0, status.output
    assert json.loads(status.output)['schema_version'] == '3'
    output = tmp_path / 'backup.sqlite3'
    args = ['database', 'backup', '--database', str(source), '--output', str(output)]
    result = runner.invoke(app, args)
    assert result.exit_code == 0 and output.is_file(), result.output
    before = output.read_bytes()
    assert runner.invoke(app, args).exit_code != 0
    assert output.read_bytes() == before
    restored = runner.invoke(app, ['database', 'restore', '--database', str(source), '--input', str(output),
                                   '--expected-revision', '1'])
    assert restored.exit_code == 0, restored.output
    assert json.loads(restored.output)['revision'] == 2
    assert workflow.repository.head() == 2
