"""Phase 1 CLI. No device execution or SSD verdicts are exposed."""

from pathlib import Path
from typing import Annotated

import typer

from ssd_validator.analyzer.spec_diff import diff_snapshots
from ssd_validator.application.build_knowledge import compile_knowledge, run_build
from ssd_validator.errors import KnowledgeError
from ssd_validator.models.identifiers import SpecFamily
from ssd_validator.storage.serialization import canonical_bytes

app = typer.Typer(no_args_is_help=True, help="Build versioned knowledge and compare specification snapshots.")
knowledge = typer.Typer(no_args_is_help=True)
spec = typer.Typer(no_args_is_help=True)
app.add_typer(knowledge, name="knowledge")
app.add_typer(spec, name="spec")


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


@knowledge.command("build")
def build(
    source: Annotated[Path, typer.Option(help="Human-managed source YAML root.")] = Path("knowledge"),
    output: Annotated[Path, typer.Option(help="Owned generated artifact directory.")] = Path("generated"),
    family: Annotated[str | None, typer.Option("--spec", help="Optional spec family selection.")] = None,
    version: Annotated[str | None, typer.Option(help="Selected version, including its dependencies.")] = None,
    clean: Annotated[bool, typer.Option(help="Rebuild managed artifacts; all Phase 1 builds are full rebuilds.")] = False,
):
    """Validate source knowledge and generate complete effective snapshots."""
    try:
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
    typer.echo(canonical_bytes(comparison).decode("utf-8"), nl=False)


if __name__ == "__main__":
    app()
