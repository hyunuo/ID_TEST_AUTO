"""Load only human-managed YAML, retaining relative paths and original-byte hashes."""

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Annotated

from pydantic import Field, TypeAdapter, ValidationError
from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

from ssd_validator.errors import KnowledgeError
from ssd_validator.models.specs import BaseSpec, DeltaSpec, KnowledgeCatalog

Document = BaseSpec | DeltaSpec | KnowledgeCatalog
DOCUMENT_ADAPTER = TypeAdapter(Annotated[Document, Field(discriminator="kind")])


@dataclass(frozen=True)
class LoadedSource:
    document: Document
    path: str
    sha256: str


def validation_message(error: ValidationError) -> str:
    return "; ".join(
        f"{'.'.join(map(str, item['loc'])) or '<document>'}: {item['msg']}"
        for item in error.errors(include_input=False)
    )


def load_document(path: Path, *, root: Path | None = None) -> LoadedSource:
    label = path.relative_to(root).as_posix() if root else path.name
    if path.is_symlink():
        raise KnowledgeError("SOURCE_SYMLINK", "Source symlinks are not supported", source=label)
    try:
        raw = path.read_bytes()
        yaml = YAML(typ="safe", pure=True)
        yaml.version = (1, 2)
        yaml.allow_duplicate_keys = False
        payload = yaml.load(raw.decode("utf-8"))
    except (OSError, UnicodeError, YAMLError) as error:
        raise KnowledgeError("YAML_ERROR", str(error), source=label) from error
    try:
        document = DOCUMENT_ADAPTER.validate_python(payload)
    except ValidationError as error:
        raise KnowledgeError("MODEL_ERROR", validation_message(error), source=label) from error
    return LoadedSource(document, label, sha256(raw).hexdigest())


def load_knowledge(root: Path) -> tuple[LoadedSource, ...]:
    root = root.resolve()
    if not root.is_dir():
        raise KnowledgeError("SOURCE_DIRECTORY", f"Not a directory: {root}")
    if root.name == "generated":
        raise KnowledgeError("GENERATED_IS_NOT_SOURCE", "generated/ cannot be a knowledge source")
    paths = sorted(
        (path for path in root.rglob("*") if path.suffix.lower() in {".yaml", ".yml"}
         and not any(part.startswith(".") or part == "generated" for part in path.relative_to(root).parts)),
        key=lambda path: path.relative_to(root).as_posix(),
    )
    if not paths:
        raise KnowledgeError("NO_SOURCE", "No source YAML documents found")
    return tuple(load_document(path, root=root) for path in paths)
