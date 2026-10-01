"""Semantic diffs and guarded generated-artifact storage."""

from datetime import datetime, timezone
from pathlib import Path

import pytest

from ssd_validator.analyzer.spec_diff import diff_snapshots
from ssd_validator.application.build_knowledge import select_build
from ssd_validator.errors import KnowledgeError
from ssd_validator.models.identifiers import SpecFamily
from ssd_validator.storage.artifacts import write_build


def test_spec_version_diff(built):
    diff = diff_snapshots(built.get("TEST", "fixture-v1"), built.get("TEST", "fixture-v4"))
    assert any(change.target == "TEST.ID_CTRL.ADDED" and change.action == "added" for change in diff.changes)
    assert any(change.target == "TEST.ID_CTRL.OBSOLETE" and change.action == "removed" for change in diff.changes)
    state_changes = {change.target: (change.previous, change.current) for change in diff.changes if change.property == "state"}
    assert state_changes["TEST.ID_CTRL.FLAGS[0]"] == ("defined", "reserved")
    assert state_changes["TEST.ID_CTRL.FLAGS[1]"] == ("reserved", "defined")


def test_diff_preserves_removal_evidence(built):
    diff = diff_snapshots(built.get("TEST", "fixture-v3"), built.get("TEST", "fixture-v4"))
    removed = next(change for change in diff.changes if change.target == "TEST.ID_CTRL.OBSOLETE")
    assert removed.current_provenance[-1].action == "REMOVE"
    assert removed.current_provenance[-1].provenance.source_section == "TEST_REMOVE"


def test_diff_same_version_and_cross_family(built):
    snapshot = built.get("TEST", "fixture-v1")
    assert not diff_snapshots(snapshot, snapshot).changes
    with pytest.raises(KnowledgeError, match="DIFF_FAMILY_MISMATCH"):
        diff_snapshots(snapshot, built.get("OCP", "fixture-v1"))


def test_requirement_status_change_is_not_hidden(built):
    diff = diff_snapshots(built.get("TEST", "fixture-v3"), built.get("TEST", "fixture-v4"))
    assert any(change.category == "requirement" and change.property == "status" and change.current == "deprecated" for change in diff.changes)


def test_selection_includes_parent_and_schema_dependencies(built):
    selected = select_build(built, SpecFamily.OCP, "fixture-v2")
    assert {item.spec.key for item in selected.snapshots} == {"OCP:fixture-v1", "OCP:fixture-v2", "TEST:fixture-v1"}
    assert selected.manifest.snapshots == tuple(item.spec for item in selected.snapshots)


def test_invalid_selection_fails(built):
    with pytest.raises(KnowledgeError, match="SELECTION_ERROR"):
        select_build(built, None, "fixture-v1")
    with pytest.raises(KnowledgeError, match="UNKNOWN_VERSION"):
        select_build(built, SpecFamily.TEST, "TEST_MISSING")


def file_bytes(root):
    return {path.relative_to(root).as_posix(): path.read_bytes() for path in root.rglob("*") if path.is_file()}


def test_output_repeatability_and_timestamp_separation(tmp_path, source_root, built):
    left, right = tmp_path / "left", tmp_path / "right"
    write_build(built, left, source_root=source_root, generated_at=datetime(2000, 1, 1, tzinfo=timezone.utc))
    write_build(built, right, source_root=source_root, generated_at=datetime(2001, 1, 1, tzinfo=timezone.utc))
    a, b = file_bytes(left), file_bytes(right)
    assert a.keys() == b.keys()
    for key in a:
        if key not in {"manifests/execution.json", "artifact_index.json"}:
            assert a[key] == b[key]
    assert a["manifests/execution.json"] != b["manifests/execution.json"]
    write_build(built, left, source_root=source_root)
    assert (left / "effective/test/fixture-v4.json").is_file()


def test_marker_files_are_preserved(tmp_path, source_root, built):
    output = tmp_path / "generated"
    (output / "effective/test").mkdir(parents=True)
    (output / "effective/test/.gitkeep").touch()
    write_build(built, output, source_root=source_root)
    assert (output / "effective/test/.gitkeep").is_file()


@pytest.mark.parametrize("relation", ["same", "ancestor", "descendant"])
def test_source_output_overlap_rejected(tmp_path, built, relation):
    source = tmp_path / "source"
    source.mkdir()
    output = {"same": source, "ancestor": tmp_path, "descendant": source / "generated"}[relation]
    with pytest.raises(KnowledgeError, match="SOURCE_OUTPUT_OVERLAP"):
        write_build(built, output, source_root=source)


def test_unmanaged_or_modified_artifacts_are_not_overwritten(tmp_path, source_root, built):
    output = tmp_path / "generated"
    output.mkdir()
    user_file = output / "user.txt"
    user_file.write_text("TEST user content")
    with pytest.raises(KnowledgeError, match="UNSAFE_OUTPUT"):
        write_build(built, output, source_root=source_root)
    assert user_file.read_text() == "TEST user content"
    user_file.unlink()
    write_build(built, output, source_root=source_root)
    snapshot = output / "effective/test/fixture-v1.json"
    snapshot.write_text("TEST manual edit")
    with pytest.raises(KnowledgeError, match="UNSAFE_OUTPUT"):
        write_build(built, output, source_root=source_root)
    assert snapshot.read_text() == "TEST manual edit"


def test_output_symlink_rejected(tmp_path, source_root, built):
    real = tmp_path / "real"
    real.mkdir()
    linked = tmp_path / "linked"
    linked.symlink_to(real, target_is_directory=True)
    with pytest.raises(KnowledgeError, match="UNSAFE_OUTPUT"):
        write_build(built, linked, source_root=source_root)


def test_handled_directory_swap_failure_rolls_back(tmp_path, source_root, built, monkeypatch):
    import os
    from ssd_validator.storage import artifacts

    output = tmp_path / "generated"
    write_build(built, output, source_root=source_root)
    before = file_bytes(output)
    real_replace = os.replace

    def fail_stage_once(source, target):
        if Path(source).name.startswith(".knowledge-stage-"):
            raise OSError("TEST injected stage failure")
        return real_replace(source, target)

    monkeypatch.setattr(artifacts.os, "replace", fail_stage_once)
    with pytest.raises(OSError, match="TEST injected stage failure"):
        write_build(built, output, source_root=source_root)
    assert file_bytes(output) == before
    assert not list(tmp_path.glob(".knowledge-stage-*"))
    assert not list(tmp_path.glob(".knowledge-backup-*"))
