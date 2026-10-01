"""Compare actual builder output with explicitly regenerated, reviewed fixture artifacts."""

from pathlib import Path

from ssd_validator.analyzer.spec_diff import diff_snapshots
from ssd_validator.storage.serialization import canonical_bytes

GOLDEN = Path(__file__).parents[1] / "golden" / "fixture_build"


def test_all_version_golden_snapshots(built):
    actual = {f"{snapshot.spec.spec_family.value.lower()}/{snapshot.spec.version}.json": canonical_bytes(snapshot)
              for snapshot in built.snapshots}
    expected = {path.relative_to(GOLDEN / "effective").as_posix(): path.read_bytes()
                for path in (GOLDEN / "effective").rglob("*.json")}
    assert actual.keys() == expected.keys()
    assert actual == expected


def test_golden_manifest(built):
    assert canonical_bytes(built.manifest) == (GOLDEN / "manifest.json").read_bytes()


def test_golden_spec_diff(built):
    diff = diff_snapshots(built.get("TEST", "fixture-v1"), built.get("TEST", "fixture-v4"))
    assert canonical_bytes(diff) == (GOLDEN / "spec_diff.json").read_bytes()
