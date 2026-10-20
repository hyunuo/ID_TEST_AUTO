"""Synthetic TEST sources: three-way cross-check never resolves a disagreement by itself."""

from ssd_validator.analyzer.source_crosscheck import (
    candidate_view, catalog_view, crosscheck, label, markdown_witness, parse_range, summary)

MARKDOWN = """intro
**Figure 9: TEST structure**
|1:0|M|M|R|**Test Flags (TFLAGS):**This field<br>**Bits**<br>3 <br>Reserved<br>2 <br>**Inline Bit (INB):**If set|
|01:00|**Two Bit Field (TWOB):** value|
|7|**Ranged Bit (RNG)**|
**Figure 10: next**
|5|**Outside Figure (OUT)**|
"""


def structures(bits):
    return {"structures": [{"document_id": "TEST.DOC", "structure_id": "TEST.S", "fields": [
        {"field_id": "TEST.S.TFLAGS", "name": "Test Flags (TFLAGS)", "byte_offset": 0, "byte_length": 2,
         "state": "defined", "bit_fields": bits}]}]}


def bit(name, msb, lsb=None):
    return {"name": name, "msb": msb, "lsb": msb if lsb is None else lsb, "state": "defined"}


def catalog(bits):
    return {"fields": [{"id": "TFLAGS", "name": "Test Flags", "start": 0, "end": 1,
                        "bits": [{"range": r, "english": e} for r, e in bits]}]}


def test_ranges_and_labels_are_normalised():
    assert parse_range("01:00") == "1:0" and parse_range("7") == "7" and parse_range("M") is None
    assert label("Inline Bit (INB): If set") == "INB"
    assert label("Multiple Ports") == "multiple ports"


def test_markdown_witness_reads_rows_and_inline_bits_inside_one_figure():
    witness = markdown_witness(MARKDOWN, "**Figure 9:", "**Figure 10:")
    assert {("1:0", "TFLAGS"), ("2", "INB"), ("1:0", "TWOB"), ("7", "RNG")} <= witness
    assert ("5", "OUT") not in witness


def test_rows_report_each_disagreement_without_choosing():
    witness = markdown_witness(MARKDOWN, "**Figure 9:", "**Figure 10:")
    candidate = candidate_view(structures([bit("Inline Bit (INB)", 2), bit("value definition", 1, 0)]), "TEST.DOC", "TEST.S")
    external = catalog_view(catalog([("2", "Inline Bit (INB): x"), ("1:0", "Two Bit Field (TWOB): y"),
                                     ("7", "Ranged Bit (RNG)"), ("3", "Reserved")]))
    rows = {(r["kind"], r["bits"]): r for r in crosscheck(candidate, external, witness)}
    assert rows[("field", None)]["status"] == "AGREE" and rows[("field", None)]["markdown_witness"]
    assert rows[("bit", "2")]["status"] == "AGREE"
    assert rows[("bit", "1:0")]["status"] == "MISMATCH" and rows[("bit", "1:0")]["candidate"] == "value definition"
    assert rows[("bit", "7")]["status"] == "CATALOG_ONLY" and rows[("bit", "7")]["markdown_witness"]
    assert ("bit", "3") not in rows
    assert summary(rows.values())["bit:MISMATCH:witnessed"] == 1


def test_title_only_name_agrees_with_abbreviated_name():
    candidate = candidate_view(structures([bit("Multiple Ports", 0)]), "TEST.DOC", "TEST.S")
    external = catalog_view(catalog([("0", "Multiple Ports (MPORTS): x")]))
    [_, row] = crosscheck(candidate, external, set())
    assert row["status"] == "AGREE" and row["catalog"] == "MPORTS"
