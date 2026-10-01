"""Explicitly regenerate TEST/FIXTURE golden artifacts through the real builder.

Run from the project root: python tests/regenerate_fixture_goldens.py --write
Never invoked automatically by tests. Review diffs before accepting new baselines.
"""

import argparse
from pathlib import Path

from ssd_validator.analyzer.spec_diff import diff_snapshots
from ssd_validator.knowledge.yaml_loader import load_knowledge
from ssd_validator.spec_builder.builder import build_knowledge
from ssd_validator.storage.serialization import canonical_bytes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", required=True)
    parser.parse_args()
    tests = Path(__file__).parent
    result = build_knowledge(load_knowledge(tests / "fixtures/knowledge"), git_commit="TEST_FIXTURE_COMMIT")
    root = tests / "golden/fixture_build"
    outputs = {f"effective/{snapshot.spec.spec_family.value.lower()}/{snapshot.spec.version}.json": canonical_bytes(snapshot)
               for snapshot in result.snapshots}
    outputs["manifest.json"] = canonical_bytes(result.manifest)
    outputs["spec_diff.json"] = canonical_bytes(diff_snapshots(result.get("TEST", "fixture-v1"), result.get("TEST", "fixture-v4")))
    for name, contents in outputs.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(contents)
    stale = {path.relative_to(root).as_posix() for path in root.rglob("*.json")} - outputs.keys()
    for name in stale:
        (root / name).unlink()
    print(f"Generated {len(outputs)} TEST/FIXTURE golden artifacts. Review every change.")


if __name__ == "__main__":
    main()
