"""Versioned local source repository; no generated snapshot is imported as source."""

import json
import sqlite3
import os
import threading
from contextlib import contextmanager, closing
from hashlib import sha256
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
from uuid import uuid4

_LOCKS = {}
_LOCKS_GUARD = threading.Lock()
SCHEMA_VERSION = '3'
SUPPORTED_BACKUPS = {'1', '2', SCHEMA_VERSION}


def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)


def source_path(value):
    if not isinstance(value, str) or '\\' in value or ':' in value:
        raise ValueError('Invalid source path')
    path = PurePosixPath(value)
    if (path.is_absolute() or '..' in path.parts or 'generated' in path.parts
            or any(part.startswith('.') for part in path.parts) or path.as_posix() != value):
        raise ValueError('Invalid source path')
    if not path.parts or path.parts[0] not in {'knowledge', 'candidates'} or path.suffix not in {'.json', '.yaml', '.yml'}:
        raise ValueError('Only knowledge/candidates JSON/YAML sources may be imported')
    return value


class KnowledgeDatabase:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with _LOCKS_GUARD:
            self.lock = _LOCKS.setdefault(os.path.normcase(str(self.path.resolve())), threading.RLock())
        with self.connect() as db:
            if db.execute("SELECT 1 FROM sqlite_master WHERE name='repository_meta'").fetchone():
                version = db.execute("SELECT value FROM repository_meta WHERE key='schema_version'").fetchone()
                if version is None or version[0] not in SUPPORTED_BACKUPS:
                    raise ValueError('Unsupported database schema version; original database was not modified')
                tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                required = {'revision', 'source_blob', 'revision_source', 'rule_index', 'validation_run'}
                if version[0] in {'2', SCHEMA_VERSION}:
                    required.add('database_migration')
                if version[0] == SCHEMA_VERSION:
                    required.add('entity_index')
                if not required <= tables:
                    raise ValueError('Incomplete database schema; original database was not modified')
                if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok' or db.execute('PRAGMA foreign_key_check').fetchall():
                    raise ValueError('Database integrity check failed; original database was not modified')
                if version[0] == '1':
                    self._migrate_v1(db)
                if version[0] in {'1','2'}:
                    self._migrate_v2(db)
            elif db.execute("SELECT 1 FROM sqlite_master WHERE type='table'").fetchone():
                raise ValueError('Not a validator database; original file was not modified')
            db.executescript('''
                CREATE TABLE IF NOT EXISTS repository_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS revision (
                    id INTEGER PRIMARY KEY, parent INTEGER REFERENCES revision(id),
                    reason TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')));
                CREATE TABLE IF NOT EXISTS source_blob (hash TEXT PRIMARY KEY, content TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS revision_source (
                    revision INTEGER NOT NULL REFERENCES revision(id), path TEXT NOT NULL,
                    hash TEXT NOT NULL REFERENCES source_blob(hash), PRIMARY KEY(revision,path));
                CREATE TABLE IF NOT EXISTS rule_index (
                    revision INTEGER NOT NULL REFERENCES revision(id), bundle TEXT NOT NULL,
                    rule_id TEXT NOT NULL, field_id TEXT NOT NULL, source_type TEXT NOT NULL,
                    review_status TEXT NOT NULL, payload TEXT NOT NULL,
                    PRIMARY KEY(revision,bundle,rule_id));
                CREATE TABLE IF NOT EXISTS validation_run (
                    id INTEGER PRIMARY KEY, revision INTEGER NOT NULL REFERENCES revision(id),
                    filename TEXT NOT NULL, input_hash TEXT NOT NULL, input BLOB NOT NULL,
                    options TEXT NOT NULL, result TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')));
                CREATE TABLE IF NOT EXISTS database_migration (
                    id INTEGER PRIMARY KEY, source_version TEXT NOT NULL, target_version TEXT NOT NULL,
                    backup_path TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')));
                CREATE TABLE IF NOT EXISTS entity_index (
                    revision INTEGER NOT NULL REFERENCES revision(id), kind TEXT NOT NULL,
                    bundle TEXT NOT NULL, entity_id TEXT NOT NULL, payload TEXT NOT NULL,
                    PRIMARY KEY(revision,kind,bundle,entity_id));
            ''')
            version = db.execute("SELECT value FROM repository_meta WHERE key='schema_version'").fetchone()
            if version and version[0] != SCHEMA_VERSION:
                raise ValueError('Unsupported database schema version')
            db.execute("INSERT OR IGNORE INTO repository_meta VALUES ('schema_version',?)", (SCHEMA_VERSION,))

    def _migrate_v1(self, db):
        """Only an explicit, known migration is allowed; back up before the transaction."""
        required = {'revision', 'source_blob', 'revision_source', 'rule_index', 'validation_run'}
        tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if not required <= tables or db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            raise ValueError('Invalid schema v1 database; migration was not attempted')
        backup_dir = self.path.parent / 'backups'
        backup_dir.mkdir(exist_ok=True)
        backup_path = backup_dir / f'pre-migration-v1-{uuid4().hex}.sqlite3'
        with closing(sqlite3.connect(backup_path)) as target:
            db.backup(target)
        db.execute('BEGIN IMMEDIATE')
        try:
            db.execute('''CREATE TABLE database_migration (
                id INTEGER PRIMARY KEY, source_version TEXT NOT NULL, target_version TEXT NOT NULL,
                backup_path TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')))''')
            db.execute("UPDATE repository_meta SET value='2' WHERE key='schema_version'")
            db.execute('INSERT INTO database_migration(source_version,target_version,backup_path) VALUES (?,?,?)',
                       ('1', '2', str(backup_path.resolve())))
            db.commit()
        except BaseException:
            db.rollback()
            raise

    def _migrate_v2(self, db):
        from ssd_validator.application.knowledge_management import entities
        backup_dir = self.path.parent / 'backups'
        backup_dir.mkdir(exist_ok=True)
        backup_path = backup_dir / f'pre-migration-v2-{uuid4().hex}.sqlite3'
        with closing(sqlite3.connect(backup_path)) as target:
            db.backup(target)
        db.execute('BEGIN IMMEDIATE')
        try:
            db.execute('''CREATE TABLE entity_index (
                revision INTEGER NOT NULL REFERENCES revision(id), kind TEXT NOT NULL,
                bundle TEXT NOT NULL, entity_id TEXT NOT NULL, payload TEXT NOT NULL,
                PRIMARY KEY(revision,kind,bundle,entity_id))''')
            for row in db.execute('SELECT id FROM revision').fetchall():
                sources = {p:c for p,c in db.execute('SELECT path,content FROM revision_source JOIN source_blob USING(hash) WHERE revision=?',(row[0],))}
                self._index_entities(db, row[0], entities(sources))
            db.execute("UPDATE repository_meta SET value=? WHERE key='schema_version'", (SCHEMA_VERSION,))
            db.execute('INSERT INTO database_migration(source_version,target_version,backup_path) VALUES (?,?,?)',
                       ('2', SCHEMA_VERSION, str(backup_path.resolve())))
            db.commit()
        except BaseException:
            db.rollback()
            raise

    @staticmethod
    def _index_entities(db, revision, items):
        for item in items:
            db.execute('INSERT INTO entity_index VALUES (?,?,?,?,?)',
                       (revision,item['kind'],item['bundle_id'],item['entity_id'],encode(item)))

    def entity_list(self, *, revision=None, kind=None, bundle=None, search=''):
        revision = self.head() if revision is None else revision
        clauses, values = ['revision=?'], [revision]
        for column, value in (('kind',kind),('bundle',bundle)):
            if value is not None:
                clauses.append(f'{column}=?'); values.append(value)
        with self.connect() as db:
            items = [json.loads(row[0]) for row in db.execute('SELECT payload FROM entity_index WHERE '+
                ' AND '.join(clauses)+' ORDER BY kind,bundle,entity_id', values)]
        return [item for item in items if search.casefold() in encode(item).casefold()]

    def status(self):
        with self.connect() as db:
            return {'schema_version': db.execute("SELECT value FROM repository_meta WHERE key='schema_version'").fetchone()[0],
                    'revision': db.execute('SELECT MAX(id) FROM revision').fetchone()[0],
                    'revisions': db.execute('SELECT COUNT(*) FROM revision').fetchone()[0],
                    'runs': db.execute('SELECT COUNT(*) FROM validation_run').fetchone()[0],
                    'migrations': [dict(row) for row in db.execute('SELECT * FROM database_migration ORDER BY id')]}

    @contextmanager
    def connect(self):
        with self.lock:
            db = sqlite3.connect(self.path, timeout=15)
            db.row_factory = sqlite3.Row
            db.execute('PRAGMA foreign_keys=ON')
            try:
                yield db
                db.commit()
            except BaseException:
                db.rollback()
                raise
            finally:
                db.close()

    def backup(self):
        """Online consistent backup, including source revisions and saved input/results."""
        with TemporaryDirectory(prefix='ssd-backup-') as directory:
            path = Path(directory) / 'backup.sqlite3'
            with self.connect() as source:
                with closing(sqlite3.connect(path)) as target:
                    source.backup(target)
                    if target.execute('PRAGMA integrity_check').fetchone()[0] != 'ok' or target.execute('PRAGMA foreign_key_check').fetchall():
                        raise ValueError('Backup integrity check failed')
            return path.read_bytes()

    def restore(self, data, *, expected_revision, validate):
        """Validate first; retain a pre-restore backup and atomically replace at rest."""
        if type(expected_revision) is not int or expected_revision < 1:
            raise ValueError('Invalid expected revision')
        with TemporaryDirectory(prefix='ssd-restore-') as directory:
            candidate = Path(directory) / 'candidate.sqlite3'
            candidate.write_bytes(data)
            with closing(sqlite3.connect(f'{candidate.as_uri()}?mode=ro', uri=True)) as db:
                if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok' or db.execute('PRAGMA foreign_key_check').fetchall():
                    raise ValueError('Invalid database backup')
                version = db.execute("SELECT value FROM repository_meta WHERE key='schema_version'").fetchone()
                if version is None or version[0] not in SUPPORTED_BACKUPS:
                    raise ValueError('Unsupported backup schema version')
                revisions = [row[0] for row in db.execute('SELECT id FROM revision ORDER BY id')]
                if not revisions:
                    raise ValueError('Backup has no knowledge revisions')
                source_sets = [{p: content for p, content in db.execute('SELECT path,content FROM revision_source JOIN source_blob USING(hash) WHERE revision=?', (revision,))}
                               for revision in revisions]
                for digest, content in db.execute('SELECT hash,content FROM source_blob'):
                    if sha256(content.encode('utf-8')).hexdigest() != digest:
                        raise ValueError('Backup source hash mismatch')
                for raw, digest, options, result in db.execute('SELECT input,input_hash,options,result FROM validation_run'):
                    if sha256(raw).hexdigest() != digest:
                        raise ValueError('Backup input hash mismatch')
                    json.loads(options); json.loads(result)
            for sources in source_sets:
                with self.project(sources) as root:
                    validate(root)
            with self.lock:
                if self.head() != expected_revision:
                    raise ValueError('REVISION_CONFLICT: Reload before restoring')
                backup_dir = self.path.parent / 'backups'
                backup_dir.mkdir(exist_ok=True)
                before = backup_dir / f'pre-restore-{uuid4().hex}.sqlite3'
                before.write_bytes(self.backup())
                staged = self.path.with_name(f'restore-{uuid4().hex}.sqlite3')
                try:
                    staged.write_bytes(data)
                    # Older backups are migrated while staged, before touching the live DB.
                    restored = KnowledgeDatabase(staged)
                    # New head prevents stale forms from saving across a restore even
                    # when the backup reused the same numeric revision IDs.
                    restored_head = restored.head()
                    new_head = max(expected_revision, restored_head) + 1
                    with restored.connect() as staged_db:
                        staged_db.execute('INSERT INTO revision(id,parent,reason) VALUES (?,?,?)',
                                          (new_head, restored_head, 'Database restore; original backup revisions retained'))
                        staged_db.execute('INSERT INTO revision_source SELECT ?,path,hash FROM revision_source WHERE revision=?',
                                          (new_head, restored_head))
                        staged_db.execute('INSERT INTO rule_index SELECT ?,bundle,rule_id,field_id,source_type,review_status,payload FROM rule_index WHERE revision=?',
                                          (new_head, restored_head))
                        staged_db.execute('INSERT INTO entity_index SELECT ?,kind,bundle,entity_id,payload FROM entity_index WHERE revision=?',
                                          (new_head, restored_head))
                    os.replace(staged, self.path)
                finally:
                    staged.unlink(missing_ok=True)
                return {'revision': self.head(), 'pre_restore_backup': str(before)}

    def head(self):
        with self.connect() as db:
            return db.execute('SELECT MAX(id) FROM revision').fetchone()[0]

    def sources(self, revision=None):
        revision = self.head() if revision is None else revision
        with self.connect() as db:
            if not db.execute('SELECT 1 FROM revision WHERE id=?', (revision,)).fetchone():
                raise ValueError('Unknown database revision')
            rows = db.execute('''SELECT path,hash,content FROM revision_source JOIN source_blob USING(hash)
                WHERE revision=? ORDER BY path''', (revision,)).fetchall()
            if any(sha256(row['content'].encode('utf-8')).hexdigest() != row['hash'] for row in rows):
                raise ValueError('Database source hash mismatch')
            return {row['path']: row['content'] for row in rows}

    @staticmethod
    @contextmanager
    def project(sources):
        with TemporaryDirectory(prefix='ssd-knowledge-') as directory:
            root = Path(directory)
            for path, content in sources.items():
                destination = root / source_path(path)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(content.encode('utf-8'))
            yield root

    def commit(self, sources, *, expected_revision, reason, validate):
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError('A change reason is required')
        if expected_revision is not None and (type(expected_revision) is not int or expected_revision < 1):
            raise ValueError('Invalid expected revision')
        if not isinstance(sources, dict) or not sources:
            raise ValueError('Sources must be a nonempty object')
        for path, content in sources.items():
            source_path(path)
            if not isinstance(content, str):
                raise ValueError('Source content must be UTF-8 text')
        # Validate complete prospective knowledge before acquiring the write lock.
        with self.project(sources) as root:
            index_items = validate(root)
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            head = db.execute('SELECT MAX(id) FROM revision').fetchone()[0]
            if head != expected_revision:
                raise ValueError('REVISION_CONFLICT: Reload before saving; another edit has been committed')
            if head is not None and sources == self.sources(head):
                raise ValueError('No source changes to save')
            revision = db.execute('INSERT INTO revision(parent,reason) VALUES (?,?)',
                                  (head, reason.strip())).lastrowid
            for path, content in sorted(sources.items()):
                digest = sha256(content.encode('utf-8')).hexdigest()
                db.execute('INSERT OR IGNORE INTO source_blob VALUES (?,?)', (digest, content))
                db.execute('INSERT INTO revision_source VALUES (?,?,?)', (revision, path, digest))
                if path.startswith('knowledge/experimental/id_ctrl/') and path.count('/') == 3 and path.endswith('.json'):
                    config = json.loads(content)
                    for rule in config['rules']:
                        db.execute('INSERT INTO rule_index VALUES (?,?,?,?,?,?,?)',
                            (revision, config['bundle']['bundle_id'], rule['rule_id'], rule['target']['field_id'],
                             rule['provenance']['source_type'], rule['provenance']['status'], encode(rule)))
            self._index_entities(db, revision, index_items or [])
            return revision

    def bootstrap(self, root, validate):
        if self.head() is not None:
            return
        sources = {}
        for name in ('knowledge', 'candidates'):
            for path in sorted((root / name).rglob('*')):
                if path.suffix in {'.json', '.yaml', '.yml'} and path.is_file():
                    if path.is_symlink():
                        raise ValueError('Symlink source cannot be imported')
                    sources[path.relative_to(root).as_posix()] = path.read_bytes().decode('utf-8')
        try:
            self.commit(sources, expected_revision=None, reason='Initial migration from legacy JSON/YAML sources', validate=validate)
        except ValueError as error:
            if 'REVISION_CONFLICT' not in str(error):
                raise

    def rules(self, bundle, revision=None):
        revision = self.head() if revision is None else revision
        with self.connect() as db:
            return [json.loads(row[0]) for row in db.execute(
                'SELECT payload FROM rule_index WHERE revision=? AND bundle=? ORDER BY rule_id', (revision, bundle))]

    def revisions(self):
        with self.connect() as db:
            return [dict(row) for row in db.execute('SELECT * FROM revision ORDER BY id DESC')]

    def save_run(self, revision, filename, data, options, report):
        with self.connect() as db:
            return db.execute('''INSERT INTO validation_run(revision,filename,input_hash,input,options,result)
                VALUES (?,?,?,?,?,?)''', (revision, filename, sha256(data).hexdigest(), data,
                                        encode(options), encode(report))).lastrowid

    def runs(self):
        with self.connect() as db:
            return [dict(row) for row in db.execute('''SELECT id,revision,filename,input_hash,created_at,
                json_extract(result,'$.validation.status') AS status FROM validation_run ORDER BY id DESC LIMIT 100''')]

    def run(self, identity):
        if type(identity) is not int:
            raise ValueError('Invalid run ID')
        with self.connect() as db:
            row = db.execute('SELECT * FROM validation_run WHERE id=?', (identity,)).fetchone()
            if row is None:
                raise ValueError('Unknown validation run')
            return dict(row)
