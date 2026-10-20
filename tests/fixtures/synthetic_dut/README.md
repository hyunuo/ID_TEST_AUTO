# Synthetic TEST DUT

Not a real device. `tools/make_synthetic_dut.py` encodes one value table into 4096-byte Identify
responses (Base 2.1 CNS 01h, NVM 1.1 CNS 00h) from `candidates/nvme/structures.json`, then renders
nvme-cli style text and JSON from the same values. `TEST-violations-*` changes the values listed in
`violations.json`. `tests/unit/test_synthetic_dut.py` requires identical verdicts for all three
formats and exactly the intended failures. These files prove pipeline consistency, not the
correctness of verdicts on real products.
