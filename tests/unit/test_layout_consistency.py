"""Executable field offsets must equal the cross-checked candidate structures (no second, hand-typed truth)."""

import json
from pathlib import Path

import pytest

from ssd_validator.application.knowledge_management import yaml_read

ROOT = Path(__file__).resolve().parents[2]
BUNDLE_DOCUMENTS = {"nvme-2.0e-nvm-1.0e": {"CNS01": ("BASE_2_0E", "NVM_1_0E"), "CNS00": ("NVM_1_0E",)},
                    "nvme-2.1-nvm-1.1": {"CNS01": ("BASE_2_1", "NVM_1_1"), "CNS00": ("NVM_1_1",)}}


def structure_layout():
    data = json.loads((ROOT / "candidates/nvme/structures.json").read_text(encoding="utf-8"))
    templates = {t["template_id"]: t for t in data["nested_templates"]}
    layout = {}
    for structure in data["structures"]:
        for field in structure["fields"]:
            key = (structure["document_id"], field["field_id"])
            layout[key] = (field["byte_offset"], field["byte_length"])
            template = templates.get(field.get("nested_template_id"))
            for bit in template["bit_fields"] if template else ():
                if bit["state"] == "defined" and bit["lsb"] % 8 == 0 and (bit["msb"] + 1) % 8 == 0:
                    name = bit["name"].rsplit("(", 1)[-1].rstrip(")")
                    layout[(structure["document_id"], f"{field['field_id']}.{name}")] = (
                        field["byte_offset"] + bit["lsb"] // 8, (bit["msb"] - bit["lsb"] + 1) // 8)
    return layout


def executable_fields():
    pack = json.loads((ROOT / "candidates/nvme/executable_requirements.json").read_text(encoding="utf-8"))
    for bundle in pack["bundles"]:
        for field in bundle["fields"]:
            yield "executable_requirements", bundle["bundle_id"], field["schema"]
    for bundle in BUNDLE_DOCUMENTS:
        base = yaml_read((ROOT / f"knowledge/experimental/id_ctrl/{bundle}/base.yaml").read_text(encoding="utf-8"))
        for schema in base["fields"]:
            yield "experimental base.yaml", bundle, schema


@pytest.mark.parametrize("origin,bundle,schema", list(executable_fields()),
                         ids=lambda v: v if isinstance(v, str) else v.get("field_id") if isinstance(v, dict) else None)
def test_executable_field_matches_structure(origin, bundle, schema):
    layout = structure_layout()
    cns = schema["field_id"].split(".")[1]
    found = [layout[(doc, schema["field_id"])] for doc in BUNDLE_DOCUMENTS[bundle][cns] if (doc, schema["field_id"]) in layout]
    assert found, f"{origin}: {schema['field_id']} absent from candidate structures"
    assert (schema["offset"], schema["length"]) in found, f"{origin}: {schema['field_id']} {schema['offset']}/{schema['length']} vs {found}"
