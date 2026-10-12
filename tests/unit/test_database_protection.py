import base64
import json
import sqlite3
from contextlib import closing
from pathlib import Path

import pytest

from ssd_validator.application.database_workflow import DatabaseWorkflow, validate_sources
from ssd_validator.storage.knowledge_db import KnowledgeDatabase

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = 'nvme-2.1-nvm-1.1'
LOG = b'NVME Identify Controller:\nsqes:0x66\ncqes:0x44\nnpss:4\nawun:0\nawupf:0\noacs:6\n'


@pytest.fixture
def workflow(tmp_path):
    return DatabaseWorkflow(ROOT, tmp_path / 'source.sqlite3')


def make_v1(path, data):
    path.write_bytes(data)
    with closing(sqlite3.connect(path)) as db, db:
        db.execute('DROP TABLE database_migration')
        db.execute('DROP TABLE entity_index')
        db.execute("UPDATE repository_meta SET value='1' WHERE key='schema_version'")
    return path.read_bytes()


def test_online_backup_preserves_sources_revisions_inputs_and_results(workflow, tmp_path):
    old = workflow.analyze(LOG, 'test.txt', BUNDLE, experimental=True)
    backup = workflow.backup_database()
    raw = base64.b64decode(backup['content_base64'])
    path = tmp_path / 'backup.sqlite3'
    path.write_bytes(raw)
    copied = DatabaseWorkflow(tmp_path, path)
    assert copied.export_sources() == workflow.export_sources()
    assert copied.load_run(old['run_id']) == old
    assert copied.repository.run(old['run_id'])['input'] == LOG
    assert copied.replay(old['run_id'])['validation'] == old['validation']
    assert workflow.database_status()['runs'] == 1


def test_restore_retains_pre_restore_backup_and_invalidates_stale_revision(workflow):
    old = workflow.analyze(LOG, 'test.txt', BUNDLE, experimental=True)
    backup = workflow.backup_database()
    rule = workflow.knowledge(BUNDLE)['rules'][0]
    rule['modality'] = 'recommendation'
    workflow.edit_rule(BUNDLE, expected_revision=1, reason='TEST change', rule=rule, original_rule_id=rule['rule_id'])
    changed_sources = workflow.export_sources()['sources']
    restored = workflow.restore_database(backup['content_base64'], expected_revision=2)
    assert restored['revision'] == 3
    assert workflow.load_run(old['run_id']) == old
    assert workflow.replay(old['run_id'])['validation'] == old['validation']
    archive = KnowledgeDatabase(Path(restored['pre_restore_backup']))
    assert archive.head() == 2 and archive.sources() == changed_sources
    with pytest.raises(ValueError, match='REVISION_CONFLICT'):
        workflow.edit_rule(BUNDLE, expected_revision=2, reason='stale form', rule=rule, original_rule_id=rule['rule_id'])


def test_corrupt_tampered_and_stale_restore_leave_live_database_unchanged(workflow, tmp_path):
    good = workflow.repository.backup()
    original = workflow.repository.path.read_bytes()
    with pytest.raises(sqlite3.DatabaseError):
        workflow.repository.restore(b'not a SQLite database', expected_revision=1, validate=validate_sources)
    assert workflow.repository.path.read_bytes() == original
    path = tmp_path / 'tampered.sqlite3'
    path.write_bytes(good)
    with closing(sqlite3.connect(path)) as db, db:
        db.execute("UPDATE source_blob SET content='{}' WHERE hash=(SELECT hash FROM source_blob LIMIT 1)")
    with pytest.raises(ValueError, match='hash mismatch'):
        workflow.repository.restore(path.read_bytes(), expected_revision=1, validate=validate_sources)
    assert workflow.repository.path.read_bytes() == original
    with pytest.raises(ValueError, match='REVISION_CONFLICT'):
        workflow.repository.restore(good, expected_revision=999, validate=validate_sources)
    assert workflow.repository.path.read_bytes() == original


def test_known_migration_backs_up_before_change_and_preserves_history(workflow, tmp_path):
    old = workflow.analyze(LOG, 'test.txt', BUNDLE, experimental=True)
    path = tmp_path / 'legacy.sqlite3'
    raw = make_v1(path, workflow.repository.backup())
    migrated = KnowledgeDatabase(path)
    status = migrated.status()
    assert status['schema_version'] == '3'
    assert status['runs'] == 1 and status['revision'] == 1
    assert migrated.sources() == workflow.repository.sources()
    assert migrated.run(old['run_id'])['input'] == LOG
    archive = Path(status['migrations'][0]['backup_path'])
    assert archive.is_file()
    with closing(sqlite3.connect(archive)) as db, db:
        assert db.execute("SELECT value FROM repository_meta WHERE key='schema_version'").fetchone() == ('1',)
        assert db.execute('SELECT input FROM validation_run WHERE id=?', (old['run_id'],)).fetchone()[0] == LOG
        assert db.execute('SELECT COUNT(*) FROM revision').fetchone()[0] == 1


def test_unknown_version_and_failed_migration_do_not_modify_original(workflow, tmp_path):
    path = tmp_path / 'future.sqlite3'
    path.write_bytes(workflow.repository.backup())
    with closing(sqlite3.connect(path)) as db, db:
        db.execute("UPDATE repository_meta SET value='999' WHERE key='schema_version'")
    original = path.read_bytes()
    with pytest.raises(ValueError, match='Unsupported database schema'):
        KnowledgeDatabase(path)
    assert path.read_bytes() == original
    # A conflicting migration table forces DDL failure after backup; transaction rolls back.
    path.write_bytes(workflow.repository.backup())
    with closing(sqlite3.connect(path)) as db, db:
        db.execute("UPDATE repository_meta SET value='1' WHERE key='schema_version'")
    original = path.read_bytes()
    with pytest.raises(sqlite3.OperationalError):
        KnowledgeDatabase(path)
    assert path.read_bytes() == original


def test_restore_v1_backup_migrates_staged_database(workflow, tmp_path):
    old = workflow.analyze(LOG, 'test.txt', BUNDLE, experimental=True)
    raw = make_v1(tmp_path / 'old.sqlite3', workflow.repository.backup())
    result = workflow.repository.restore(raw, expected_revision=1, validate=validate_sources)
    assert result['revision'] == 2
    assert workflow.database_status()['schema_version'] == '3'
    assert workflow.load_run(old['run_id']) == old


def test_empty_unknown_or_invalid_knowledge_backup_is_rejected(workflow, tmp_path):
    original = workflow.repository.path.read_bytes()
    path = tmp_path / 'invalid.sqlite3'
    path.write_bytes(workflow.repository.backup())
    with closing(sqlite3.connect(path)) as db, db:
        db.execute("UPDATE repository_meta SET value='99' WHERE key='schema_version'")
    with pytest.raises(ValueError, match='Unsupported backup schema'):
        workflow.repository.restore(path.read_bytes(), expected_revision=1, validate=validate_sources)
    assert workflow.repository.path.read_bytes() == original
