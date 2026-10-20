# Engine baseline inputs

Synthetic TEST inputs only; no value here describes a real DUT. `tools/capture_baseline.py`
runs them through the registered NVMe/OCP candidates and stores the verdict projection in
`tests/golden/baseline/engine_baseline.json`. Simplification changes must keep that file
unchanged unless a verdict change is intended and reviewed.
