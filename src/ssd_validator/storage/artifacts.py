"""Stage a complete validated build and replace only an owned artifact directory."""

import json
import os
import shutil
import tempfile
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

from ssd_validator.errors import KnowledgeError
from ssd_validator.spec_builder.manifest import runtime_toolchain
from .serialization import canonical_bytes

INDEX = "artifact_index.json"


def _check_destination(destination: Path) -> list[Path]:
    if destination.is_symlink():
        raise KnowledgeError("UNSAFE_OUTPUT", "Output must not be a symlink")
    if not destination.exists():
        return []
    if not destination.is_dir():
        raise KnowledgeError("UNSAFE_OUTPUT", "Output is not a directory")
    if any(path.is_symlink() for path in destination.rglob("*")):
        raise KnowledgeError("UNSAFE_OUTPUT", "Output contains a symlink")
    files = {path.relative_to(destination).as_posix(): path for path in destination.rglob("*") if path.is_file()}
    markers = [path for name, path in files.items() if path.name == ".gitkeep"]
    actual = {name for name, path in files.items() if path.name != ".gitkeep"}
    if not actual:
        return markers
    try:
        index = json.loads((destination / INDEX).read_text())
        if index["artifact_kind"] != "knowledge_build" or set(index["files"]) | {INDEX} != actual:
            raise ValueError("Unmanaged files or invalid artifact index")
        for name, digest in index["files"].items():
            if sha256(files[name].read_bytes()).hexdigest() != digest:
                raise ValueError(f"Modified generated artifact: {name}")
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise KnowledgeError("UNSAFE_OUTPUT", str(error)) from error
    return markers


def write_build(result, destination: Path, *, source_root: Path, generated_at: datetime | None = None) -> None:
    # Validate every planned path before creating staging directories or touching
    # existing output. Case folding also guarantees portable builds on Linux.
    payloads, portable_paths = {}, set()
    for snapshot in result.snapshots:
        name = f"effective/{snapshot.spec.spec_family.value.lower()}/{snapshot.spec.version}.json"
        if name.casefold() in portable_paths:
            raise KnowledgeError("ARTIFACT_PATH_COLLISION", name)
        portable_paths.add(name.casefold())
        payloads[name] = canonical_bytes(snapshot)
    original_destination = destination.absolute()
    if original_destination.is_symlink():
        raise KnowledgeError("UNSAFE_OUTPUT", "Output must not be a symlink")
    destination, source_root = destination.resolve(), source_root.resolve()
    if destination == source_root or destination in source_root.parents or source_root in destination.parents:
        raise KnowledgeError("SOURCE_OUTPUT_OVERLAP", "Output must be separate from source knowledge")
    markers = _check_destination(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".knowledge-stage-", dir=destination.parent))
    backup = None
    try:
        payloads["manifests/build.json"] = canonical_bytes(result.manifest)
        now = generated_at or datetime.now(timezone.utc)
        payloads["manifests/execution.json"] = canonical_bytes({
            "generated_at": now.isoformat(), "toolchain": runtime_toolchain(),
        })
        for marker in markers:
            target = stage / marker.relative_to(destination)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(marker.read_bytes())
        for name, contents in payloads.items():
            target = stage / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(contents)
        (stage / INDEX).write_bytes(canonical_bytes({
            "artifact_kind": "knowledge_build",
            "files": {name: sha256(contents).hexdigest() for name, contents in sorted(payloads.items())},
        }))
        if destination.exists():
            backup = Path(tempfile.mkdtemp(prefix=".knowledge-backup-", dir=destination.parent))
            backup.rmdir()
            os.replace(destination, backup)
        try:
            os.replace(stage, destination)
        except OSError:
            if backup is not None:
                os.replace(backup, destination)
                backup = None
            raise
        if backup is not None:
            shutil.rmtree(backup)
            backup = None
    finally:
        if stage.exists():
            shutil.rmtree(stage)
