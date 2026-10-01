"""Source loading, complete validation, optional selection, and artifact storage."""

from pathlib import Path

from ssd_validator.errors import KnowledgeError
from ssd_validator.knowledge.yaml_loader import load_knowledge
from ssd_validator.models.identifiers import SpecFamily
from ssd_validator.spec_builder.builder import BuildResult, build_knowledge
from ssd_validator.spec_builder.manifest import git_commit
from ssd_validator.storage.artifacts import write_build


def compile_knowledge(source: Path) -> BuildResult:
    return build_knowledge(load_knowledge(source), git_commit=git_commit(source))


def select_build(result: BuildResult, family: SpecFamily | None, version: str | None) -> BuildResult:
    if version and family is None:
        raise KnowledgeError("SELECTION_ERROR", "--version requires --spec")
    if family is None:
        return result
    by_key = {snapshot.spec.key: snapshot for snapshot in result.snapshots}
    selected = [snapshot for snapshot in result.snapshots if snapshot.spec.spec_family == family and (version is None or snapshot.spec.version == version)]
    if not selected:
        raise KnowledgeError("UNKNOWN_VERSION", f"{family.value}:{version or '*'}")
    keys, pending = set(), list(selected)
    while pending:
        snapshot = pending.pop()
        if snapshot.spec.key in keys:
            continue
        keys.add(snapshot.spec.key)
        for reference in (snapshot.parent, snapshot.schema_ref):
            if reference:
                pending.append(by_key[reference.key])
    snapshots = tuple(by_key[key] for key in sorted(keys))
    manifest = result.manifest.model_copy(update={"snapshots": tuple(snapshot.spec for snapshot in snapshots)})
    return BuildResult(snapshots, manifest)


def run_build(source: Path, output: Path, *, family: SpecFamily | None = None, version: str | None = None) -> BuildResult:
    result = select_build(compile_knowledge(source), family, version)
    write_build(result, output, source_root=source)
    return result
