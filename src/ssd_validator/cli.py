"""Knowledge builds, candidate review and offline fixture rules; no device execution."""

from pathlib import Path
from typing import Annotated

import typer
import sys
import sqlite3
import base64
import json

from ssd_validator.analyzer.spec_diff import diff_snapshots
from ssd_validator.application.build_knowledge import compile_knowledge, run_build
from ssd_validator.application.candidate_knowledge import build_candidates, compile_candidates, diff_bundles
from ssd_validator.application.rule_pilot import run_pilot
from ssd_validator.application.normalize_actual import run_normalization
from ssd_validator.errors import KnowledgeError
from ssd_validator.models.identifiers import SpecFamily
from ssd_validator.storage.serialization import canonical_bytes

app = typer.Typer(no_args_is_help=True, help="Build knowledge, compare snapshots and evaluate offline fixture rules.")
knowledge = typer.Typer(no_args_is_help=True)
spec = typer.Typer(no_args_is_help=True)
app.add_typer(knowledge, name="knowledge")
app.add_typer(spec, name="spec")
pilot = typer.Typer(no_args_is_help=True, help="Offline TEST/FIXTURE rule execution only.")
app.add_typer(pilot, name="pilot")
actual = typer.Typer(no_args_is_help=True, help="Normalize saved Identify data using an explicit target Bundle.")
app.add_typer(actual, name="actual")
database_app = typer.Typer(no_args_is_help=True, help='Protect the authoritative SQLite database and saved runs.')
app.add_typer(database_app, name='database')


def _family(value: str | None) -> SpecFamily | None:
    if value is None:
        return None
    try:
        return SpecFamily(value.upper())
    except ValueError as error:
        raise KnowledgeError("UNKNOWN_FAMILY", value) from error


def _fail(error):
    typer.echo(str(error), err=True)
    raise typer.Exit(code=1)


def _emit_json(value):
    """Write UTF-8 JSON bytes so Windows console code pages cannot corrupt results."""
    sys.stdout.buffer.write(canonical_bytes(value))
    sys.stdout.buffer.flush()


@knowledge.command("build")
def build(
    source: Annotated[Path, typer.Option(help="Human-managed source YAML root.")] = Path("knowledge"),
    output: Annotated[Path, typer.Option(help="Owned generated artifact directory.")] = Path("generated"),
    family: Annotated[str | None, typer.Option("--spec", help="Optional spec family selection.")] = None,
    version: Annotated[str | None, typer.Option(help="Selected version, including its dependencies.")] = None,
    clean: Annotated[bool, typer.Option(help="Rebuild managed artifacts; all Phase 1 builds are full rebuilds.")] = False,
    candidate: Annotated[bool, typer.Option(help="Explicitly compile non-authoritative PDF extraction candidates.")] = False,
    documents_root: Annotated[Path | None, typer.Option(help="Local source PDF directory; required for candidate builds.")] = None,
):
    """Validate source knowledge and generate complete effective snapshots."""
    try:
        if candidate:
            if documents_root is None or family is not None or version is not None:
                raise KnowledgeError("CANDIDATE_OPTIONS", "--candidate requires --documents-root and does not accept --spec/--version")
            bundles = build_candidates(source, output, documents_root)
            typer.echo(f"Built {len(bundles)} CANDIDATE bundles in {output}; not authoritative, human review required")
            return
        if documents_root is not None:
            raise KnowledgeError("CANDIDATE_OPTIONS", "--documents-root requires --candidate")
        result = run_build(source, output, family=_family(family), version=version)
    except (KnowledgeError, OSError) as error:
        _fail(error)
    typer.echo(f"Built {len(result.snapshots)} snapshots in {output}; knowledge hash {result.manifest.knowledge_hash}")


@spec.command("diff")
def diff(
    family: Annotated[str, typer.Option("--family")],
    from_version: Annotated[str, typer.Option("--from")],
    to_version: Annotated[str, typer.Option("--to")],
    source: Annotated[Path, typer.Option()] = Path("knowledge"),
):
    """Rebuild from YAML and emit a structural JSON diff with provenance."""
    try:
        result = compile_knowledge(source)
        selected_family = _family(family)
        comparison = diff_snapshots(result.get(selected_family, from_version), result.get(selected_family, to_version))
    except (KnowledgeError, OSError) as error:
        _fail(error)
    _emit_json(comparison)


@spec.command("bundle-diff")
def bundle_diff(
    from_bundle: Annotated[str, typer.Option("--from")],
    to_bundle: Annotated[str, typer.Option("--to")],
    source: Annotated[Path, typer.Option()] = Path("candidates/nvme"),
    documents_root: Annotated[Path | None, typer.Option(help="Optionally verify original PDF hashes.")] = None,
):
    """Compare source-derived candidate bundles; this is not a device validation."""
    try:
        _, bundles, _, _ = compile_candidates(source, documents_root)
        if from_bundle not in bundles or to_bundle not in bundles:
            raise KnowledgeError("UNKNOWN_BUNDLE", f"{from_bundle} -> {to_bundle}")
        comparison = diff_bundles(bundles[from_bundle], bundles[to_bundle])
    except (KnowledgeError, OSError) as error:
        _fail(error)
    _emit_json(comparison)


@pilot.command("run")
def pilot_run(
    source: Annotated[Path, typer.Option(help="TEST/FIXTURE knowledge YAML directory.")],
    input_path: Annotated[Path, typer.Option("--input", help="Offline fixture Context, rules, mappings and Actual JSON.")],
):
    """Build Source, resolve conditional expectations and emit a fixture report."""
    try:
        report = run_pilot(source, input_path)
    except (KnowledgeError, OSError, ValueError) as error:
        _fail(error)
    _emit_json(report)


@actual.command("normalize")
def actual_normalize(
    layout: Annotated[Path, typer.Option(help="Fixture/candidate target Bundle field layout JSON.")],
    capture: Annotated[Path, typer.Option(help="Recorded tool version, device and Identify query JSON.")],
    raw: Annotated[Path | None, typer.Option(help="Saved raw response; never launches nvme-cli.")] = None,
    json_path: Annotated[Path | None, typer.Option("--json", help="Saved JSON with explicit field paths.")] = None,
):
    """Emit observations and source trace, not production PASS/FAIL."""
    try:
        report = run_normalization(layout, capture, raw_path=raw, json_path=json_path)
    except (KnowledgeError, OSError, ValueError) as error:
        _fail(error)
    _emit_json(report)


@app.command("gui")
def gui(
    sample: Annotated[Path | None, typer.Option(help="Optional saved id-ctrl text log to open as sample.")] = None,
    port: Annotated[int, typer.Option(min=1, max=65535, help="Local browser UI port.")] = 8765,
    database: Annotated[Path | None, typer.Option(help='SQLite source database; defaults to data/validator.sqlite3.')] = None,
):
    """Open http://127.0.0.1:8765/ for the minimal Identify log workflow."""
    from ssd_validator.gui.server import serve
    try:
        serve(port, sample, database)
    except (OSError, ValueError, KnowledgeError, sqlite3.Error) as error:
        _fail(error)


@actual.command('review-log')
def review_log(
    input_path: Annotated[Path, typer.Option('--input', help='Saved id-ctrl text log.')],
    bundle: Annotated[str, typer.Option(help='Explicit Base + NVM Bundle.')] = 'nvme-2.1-nvm-1.1',
    experimental: Annotated[bool, typer.Option(help='Execute unreviewed rules and explicit policy assumptions.')] = False,
    database: Annotated[Path | None, typer.Option(help='SQLite source database; defaults to data/validator.sqlite3.')] = None,
    profile: Annotated[str | None, typer.Option(help='Explicit registered Product Profile ID; Bundle must match.')] = None,
):
    """Review saved DUT observations, optionally executing editable experimental rules."""
    from ssd_validator.application.database_workflow import DatabaseWorkflow
    try:
        report = DatabaseWorkflow(Path.cwd(), database).analyze(input_path.read_bytes(), input_path.name, bundle,
                                                   experimental=experimental,profile_id=profile)
    except (KnowledgeError, OSError, ValueError, sqlite3.Error) as error:
        _fail(error)
    _emit_json(report)


@database_app.command('status')
def database_status(database: Annotated[Path | None, typer.Option(help='Source database path.')] = None):
    from ssd_validator.application.database_workflow import DatabaseWorkflow
    try:
        _emit_json(DatabaseWorkflow(Path.cwd(), database).database_status())
    except (ValueError, OSError, KnowledgeError, sqlite3.Error) as error:
        _fail(error)


@database_app.command('backup')
def database_backup(
    output: Annotated[Path, typer.Option('--output', help='New backup file; existing files are not overwritten.')],
    database: Annotated[Path | None, typer.Option(help='Source database path.')] = None,
):
    from ssd_validator.application.database_workflow import DatabaseWorkflow
    try:
        if output.exists():
            raise ValueError('Backup output already exists; choose a new filename')
        result = DatabaseWorkflow(Path.cwd(), database).backup_database()
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open('xb') as stream:
            stream.write(base64.b64decode(result.pop('content_base64')))
        _emit_json({**result, 'output': str(output)})
    except (ValueError, OSError, KnowledgeError, sqlite3.Error) as error:
        _fail(error)


@database_app.command('restore')
def database_restore(
    input_path: Annotated[Path, typer.Option('--input', help='Complete SQLite backup.')],
    expected_revision: Annotated[int, typer.Option(min=1, help='Current head revision shown by database status.')],
    database: Annotated[Path | None, typer.Option(help='Source database path.')] = None,
):
    from ssd_validator.application.database_workflow import DatabaseWorkflow
    try:
        data = input_path.read_bytes()
        result = DatabaseWorkflow(Path.cwd(), database).restore_database(base64.b64encode(data).decode('ascii'),
                    expected_revision=expected_revision)
        _emit_json(result)
    except (ValueError, OSError, KnowledgeError, sqlite3.Error) as error:
        _fail(error)


@actual.command('review-captures')
def review_captures(
    input_path: Annotated[Path, typer.Option('--input', help='ssd-validator-captures-v1 JSON envelope with original base64 responses.')],
    bundle: Annotated[str, typer.Option(help='Explicit target Bundle.')] = 'nvme-2.1-nvm-1.1',
    experimental: Annotated[bool, typer.Option(help='Execute unreviewed rules.')] = False,
    database: Annotated[Path | None, typer.Option(help='SQLite source database.')] = None,
    profile: Annotated[str | None, typer.Option(help='Explicit registered Product Profile ID.')] = None,
):
    """Inspect saved multi-command inputs without executing device commands."""
    from ssd_validator.application.database_workflow import DatabaseWorkflow
    from ssd_validator.application.rule_pilot import _unique_object
    try:
        if input_path.stat().st_size > 24 * 1024 * 1024:
            raise ValueError('Capture envelope exceeds 24 MiB')
        package = json.loads(input_path.read_text(encoding='utf-8'),object_pairs_hook=_unique_object)
        _emit_json(DatabaseWorkflow(Path.cwd(), database).analyze_captures(package,bundle,experimental=experimental,profile_id=profile))
    except (KnowledgeError,OSError,ValueError,sqlite3.Error) as error:
        _fail(error)


@knowledge.command('expand-nvme')
def expand_nvme(
    recipe: Annotated[Path,typer.Option(help='Source-read candidate requirement recipe JSON.')],
    pdf_dir: Annotated[Path,typer.Option(help='Directory containing the pinned original PDFs.')],
    expected_revision: Annotated[int,typer.Option(min=1,help='Current SQLite head; stale updates are rejected.')],
    reason: Annotated[str,typer.Option(help='Explicit registration reason.')],
    database: Annotated[Path | None,typer.Option(help='SQLite source database.')] = None,
):
    """Verify PDFs, back up, and register candidate rules in a new revision."""
    from ssd_validator.application.database_workflow import DatabaseWorkflow
    from ssd_validator.application.nvme_expansion import register
    try:
        _emit_json(register(DatabaseWorkflow(Path.cwd(),database),recipe,pdf_dir,expected_revision=expected_revision,reason=reason))
    except (KnowledgeError,OSError,ValueError,sqlite3.Error) as error:_fail(error)


@knowledge.command('register-supplemental')
def register_supplemental(
    recipe: Annotated[Path,typer.Option(help='Pinned supplemental candidate recipe.')],
    pdf_dir: Annotated[Path,typer.Option(help='Original PDF directory.')],
    expected_revision: Annotated[int,typer.Option(min=1)],
    reason: Annotated[str,typer.Option()],
    database: Annotated[Path | None,typer.Option()] = None,
):
    from ssd_validator.application.database_workflow import DatabaseWorkflow
    from ssd_validator.application.supplemental_requirements import register
    try:_emit_json(register(DatabaseWorkflow(Path.cwd(),database),recipe,pdf_dir,expected_revision=expected_revision,reason=reason))
    except (KnowledgeError,OSError,ValueError,sqlite3.Error) as error:_fail(error)


if __name__ == "__main__":
    app()
