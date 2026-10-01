"""Shared paths and copies of clearly identified TEST/FIXTURE source data."""

from pathlib import Path
from shutil import copytree
import os

import pytest
from ruamel.yaml import YAML

from ssd_validator.knowledge.yaml_loader import load_knowledge
from ssd_validator.spec_builder.builder import build_knowledge

FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "knowledge"


def make_symlink(link, target, *, directory=False):
    try:
        link.symlink_to(target, target_is_directory=directory)
    except OSError as error:
        if getattr(error, "winerror", None) != 1314:
            raise
        if os.environ.get("SSD_REQUIRE_SYMLINK_TESTS") == "1":
            pytest.fail("Symlink tests require Windows symlink privilege or Developer Mode")
        pytest.skip("Windows symlink privilege unavailable; required in CI")


@pytest.fixture
def source_root():
    return FIXTURE_ROOT


@pytest.fixture
def sources(source_root):
    return load_knowledge(source_root)


@pytest.fixture
def built(sources):
    return build_knowledge(sources, git_commit="TEST_FIXTURE_COMMIT")


@pytest.fixture
def editable_knowledge(tmp_path, source_root):
    root = tmp_path / "knowledge"
    copytree(source_root, root)
    return root


def edit_yaml(root, relative, edit):
    path = root / relative
    yaml = YAML(typ="safe", pure=True)
    document = yaml.load(path.read_text())
    edit(document)
    with path.open("w") as stream:
        yaml.dump(document, stream)


def build_from(root):
    return build_knowledge(load_knowledge(root), git_commit="TEST_FIXTURE_COMMIT")
