"""One synthetic TEST device in raw, nvme-cli text and nvme-cli JSON form must get identical verdicts."""

import base64
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests/fixtures/synthetic_dut"
BUNDLE = "nvme-2.1-nvm-1.1"
EXTENSIONS = {"text": "txt", "json": "json", "raw": "bin"}
INTENDED_FAILURES = {
    "EXPERIMENTAL.ATOMIC_POWER_FAIL_BOUND", "EXPERIMENTAL.CQES_REQUIRED", "EXPERIMENTAL.SQES_REQUIRED",
    "NVME.STAGE5.CAPACITY.NCAP_LE_NSZE", "NVME.STAGE5.CAPACITY.NUSE_LE_NCAP", "NVME.STAGE5.HMB.PREFERRED_GE_MINIMUM",
    "NVME.STAGE5.QUEUE.CQES_MAX_REQUIRED", "NVME.STAGE5.QUEUE.SQES_MAX_REQUIRED", "NVME.STAGE5.THINP.ZERO_NCAP",
    "OCP.2_6.NVMe-CFG-14.SQES", "OCP.2_6.NVMe-CFG-15.CQES", "OCP.2_6.NVMe-CFG-19.HMMIN", "OCP.2_6.NVMe-CFG-19.HMPRE",
}


def tool(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"tools/{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def package(variant, source_format):
    captures = []
    for command, cns, nsid in (("id-ctrl", 1, None), ("id-ns", 0, 1)):
        path = FIXTURES / f"{variant}-{command}.{EXTENSIONS[source_format]}"
        item = {"capture_id": command.replace("-", "_").upper(), "filename": path.name, "command": command,
                "source_format": source_format, "dut_id": "TEST", "session_id": "TEST",
                "content_base64": base64.b64encode(path.read_bytes()).decode("ascii")}
        if source_format == "raw":
            item.update(cns=cns, csi=0)
        if nsid:
            item["nsid"] = nsid
        captures.append(item)
    return {"captures": captures}


def verdicts(report):
    found = {}
    def walk(value):
        if isinstance(value, dict):
            if isinstance(value.get("rule"), dict) and "status" in value:
                found[value["rule"]["rule_id"]] = value["status"]
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)
    walk(report)
    return found


@pytest.fixture(scope="module")
def results(tmp_path_factory):
    manifest = json.loads((ROOT / "spec/manifest.json").read_text(encoding="utf-8"))
    if not all((ROOT / "spec" / d["pdf"]).is_file() for d in manifest["documents"]):
        pytest.skip("Registration needs the original PDFs in spec/")
    baseline = tool("capture_baseline")
    workflow, _ = baseline.database(tmp_path_factory.mktemp("synthetic"))
    return {(variant, fmt): verdicts(workflow.analyze_captures(package(variant, fmt), BUNDLE, profile_id="TEST." + BUNDLE,
                                                               context_facts=baseline.OCP_CONTEXT))
            for variant in ("TEST-good", "TEST-violations") for fmt in EXTENSIONS}


def test_fixtures_are_reproducible(tmp_path, monkeypatch):
    generator = tool("make_synthetic_dut")
    monkeypatch.setattr(generator, "OUTPUT", tmp_path)
    generator.main()
    for path in tmp_path.iterdir():
        assert path.read_bytes() == (FIXTURES / path.name).read_bytes(), path.name


@pytest.mark.parametrize("variant", ["TEST-good", "TEST-violations"])
def test_formats_agree(results, variant):
    text, json_, raw = (results[(variant, fmt)] for fmt in EXTENSIONS)
    assert text == json_ == raw


def test_good_device_has_no_failure(results):
    assert not {k for k, v in results[("TEST-good", "raw")].items() if v in {"FAIL", "ERROR", "CONFLICT"}}


def test_violations_fail_exactly_the_intended_rules(results):
    assert {k for k, v in results[("TEST-violations", "raw")].items() if v == "FAIL"} == INTENDED_FAILURES
