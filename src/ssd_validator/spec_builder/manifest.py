"""Reproducible source identity; wall-clock metadata is stored separately."""

import json
import subprocess
import platform
from importlib.metadata import version
from hashlib import sha256
from pathlib import Path

from ssd_validator.models.effective import BuildManifest, SourceFile

BUILDER_VERSION = "0.2.0"


def runtime_toolchain() -> dict[str, str]:
    return {"python": platform.python_version(), "platform": platform.system(),
            **{name: version(name) for name in ("pydantic", "ruamel.yaml", "typer")}}


def git_commit(root: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, check=False,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except OSError:
        return None


def build_manifest(sources, snapshots, commit: str | None) -> BuildManifest:
    entries = tuple(SourceFile(path=source.path, sha256=source.sha256) for source in sorted(sources, key=lambda source: source.path))
    serialized = json.dumps([entry.model_dump() for entry in entries], sort_keys=True, separators=(",", ":"))
    return BuildManifest(
        builder_version=BUILDER_VERSION, git_commit=commit,
        knowledge_hash=sha256(serialized.encode()).hexdigest(), sources=entries,
        snapshots=tuple(snapshot.spec for snapshot in sorted(snapshots, key=lambda snapshot: snapshot.spec.key)),
    )
