"""spec/ originals must be the exact documents pinned by candidate knowledge."""

from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "spec"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def pinned_documents():
    pins = {d["filename"]: d["sha256"] for d in load(ROOT / "candidates/nvme/catalog.json")["documents"]}
    ocp = load(ROOT / "candidates/ocp/requirements.json")["document"]
    pins[ocp["filename"]] = ocp["sha256"]
    return pins


def test_manifest_matches_candidate_pins():
    manifest = load(SPEC / "manifest.json")
    listed = {d["pdf"]: d["pdf_sha256"] for d in manifest["documents"] + manifest["missing"]}
    assert listed == pinned_documents()


def test_present_files_match_manifest_hashes():
    manifest = load(SPEC / "manifest.json")
    for document in manifest["documents"]:
        for name, digest in ((document["pdf"], document["pdf_sha256"]), (document["markdown"], document["markdown_sha256"])):
            if name is not None:
                assert sha256((SPEC / name).read_bytes()).hexdigest() == digest, name
    for document in manifest["missing"]:
        path = SPEC / document["pdf"]
        if path.exists():
            assert sha256(path.read_bytes()).hexdigest() == document["pdf_sha256"], document["pdf"]
