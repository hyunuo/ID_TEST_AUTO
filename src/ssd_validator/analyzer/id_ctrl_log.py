"""Saved id-ctrl text adapter. No specification requirements are synthesized."""

import re
from hashlib import sha256

HEADER = re.compile(r"^\s*NVME\s+Identify\s+Controller\s*:\s*$", re.I)
FIELD = re.compile(r"^\s*([A-Za-z][A-Za-z0-9_]*)\s*:\s*(.*?)\s*$")
POWER = re.compile(r"^\s*ps\s+(\d+)\s*:\s*(.*)$", re.I)
NUMBER = re.compile(r"^(?:0[xX][0-9a-fA-F]+|[0-9]+)$")
# Printed identifiers remain strings (leading zeroes and punctuation are meaningful).
TEXT_FIELDS = {"sn", "mn", "fr", "subnqn", "fguid", "ieee"}


def _number(value):
    return int(value, 16 if value.lower().startswith("0x") else 10)


def analyze_id_ctrl(data: bytes, filename: str) -> dict:
    """Preserve printed observations; requirements are evaluated by the existing Resolver."""
    if len(data) > 1024 * 1024:
        raise ValueError("Log size exceeds 1 MiB")
    text = data.decode("utf-8-sig")
    rows, by_name, powers, issues = [], {}, [], []
    current_power = None
    header_seen = False
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        if HEADER.fullmatch(line):
            if header_seen:
                raise ValueError("Only one Identify Controller response is supported per file")
            header_seen = True
            continue
        if not header_seen:
            issues.append({"line": line_number, "text": line, "reason": "Text before Identify header"})
            continue
        power = POWER.fullmatch(line)
        if power:
            index = int(power.group(1))
            current_power = {"index": index, "lines": [line_number], "text": power.group(2)}
            if any(p["index"] == index for p in powers):
                issues.append({"line": line_number, "text": line, "reason": "Duplicate Power State index"})
            powers.append(current_power)
            continue
        if current_power is not None and line[:1].isspace():
            current_power["text"] += "\n" + line.strip()
            current_power["lines"].append(line_number)
            continue
        current_power = None
        field = FIELD.fullmatch(line)
        if field is None:
            issues.append({"line": line_number, "text": line, "reason": "Unrecognized line"})
            continue
        name, raw_value = field.groups()
        numeric = name not in TEXT_FIELDS and NUMBER.fullmatch(raw_value) is not None
        value = _number(raw_value) if numeric else raw_value
        row = {"field": name, "raw_value": raw_value, "value": value,
               "value_type": "integer" if numeric else "string", "line": line_number,
               "expected": None, "status": "UNKNOWN", "reason": "기대값 미지정"}
        if name in by_name:
            row["status"] = "ERROR"
            row["reason"] = "중복 필드: 값을 선택하지 않음"
            by_name[name]["status"] = "ERROR"
            by_name[name]["reason"] = row["reason"]
            issues.append({"line": line_number, "text": line, "reason": "Duplicate field: " + name})
        else:
            by_name[name] = row
        rows.append(row)
    if not header_seen or not rows:
        raise ValueError("No readable NVME Identify Controller response found")
    counts = {s: sum(row["status"] == s for row in rows) for s in ("PASS", "FAIL", "UNKNOWN", "ERROR")}
    version = by_name.get("ver", {}).get("value")
    version_text = f"{version >> 16}.{(version >> 8) & 255}.{version & 255}" if type(version) is int else None
    return {"kind": "id_ctrl_observations", "comparison_basis": "observations_only",
            "source": {"filename": filename, "sha256": sha256(data).hexdigest()},
            "identity": {name: by_name.get(name, {}).get("value") for name in ("mn", "sn", "fr")},
            "advertised_nvme_version": version_text, "fields": rows, "power_states": powers,
            "issues": issues, "counts": counts, "raw_text": text}
