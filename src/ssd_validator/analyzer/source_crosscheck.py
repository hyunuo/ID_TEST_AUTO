"""Independent-source cross-check for one Identify structure.

Two field/bit extractions (this project's PDF candidates and an external catalog) are
compared item by item, and a Markdown conversion of the original is used as a third
witness. Nothing here picks a winner: disagreements become review rows.
"""

import re

ABBR = re.compile(r"\(([A-Z][A-Z0-9_]*)\)")
RANGE_CELL = re.compile(r"^\s*(\d+)(?:\s*:\s*(\d+))?\s*$")
INLINE_BIT = re.compile(r"<br>(\d+(?::\d+)?)\s*<br>\s*\*\*([^*]+)\*\*")
RESERVED = re.compile(r"^\s*reserved\b", re.IGNORECASE)
AVAILABILITY = re.compile(r"^(?:[MOR]\d?|P)?$")


def bit_range(msb, lsb=None):
    lsb = msb if lsb is None else lsb
    return str(msb) if msb == lsb else f"{msb}:{lsb}"


def parse_range(text):
    match = RANGE_CELL.match(text)
    if not match:
        return None
    high, low = int(match.group(1)), match.group(2)
    return bit_range(high, int(low) if low is not None else None)


def label(name):
    """Abbreviation when the definition has one, otherwise the folded title."""
    head = name.split(":", 1)[0]
    found = ABBR.findall(head) or ABBR.findall(name[:160])
    if found:
        return found[-1] if head.rstrip().endswith(")") else found[0]
    return title(name)


def title(name):
    head = ABBR.sub("", name.split(":", 1)[0])
    return re.sub(r"\s+", " ", head).strip(" *.").casefold()


def candidate_view(structures, document_id, structure_id):
    structure = next(s for s in structures["structures"]
                     if s["document_id"] == document_id and s["structure_id"] == structure_id)
    view = {}
    for field in structure["fields"]:
        if field["state"] == "reserved":
            continue
        start = field["byte_offset"]
        view[label(field["name"])] = {
            "bytes": bit_range(start + field["byte_length"] - 1, start), "state": field["state"],
            "bits": {bit_range(b["msb"], b["lsb"]): (label(b["name"]), title(b["name"])) for b in field["bit_fields"]
                     if b["state"] == "defined" and not RESERVED.match(b["name"])}}
    return view


def catalog_view(catalog):
    view = {}
    for field in catalog["fields"]:
        if field["id"].startswith("PSD") or RESERVED.match(field["name"]):
            continue
        view[field["id"]] = {
            "bytes": bit_range(field["end"], field["start"]), "state": "defined",
            "bits": {b["range"]: (label(b["english"]), title(b["english"])) for b in field["bits"]
                     if not RESERVED.match(b["english"]) and not RESERVED.match(b.get("title", ""))}}
    return view


def markdown_witness(text, start_marker, end_marker):
    """(range, label) pairs that appear as table rows or inline bit lists in one figure."""
    start = text.index(start_marker)
    region = text[start:text.index(end_marker, start)]
    pairs = set()
    for line in region.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")] if line.startswith("|") else []
        for index, cell in enumerate(cells):
            value = parse_range(cell)
            if value is None:
                continue
            following = next((c for c in cells[index + 1:] if not AVAILABILITY.match(c)), "")
            if following and not parse_range(following):
                pairs.add((value, label(following.replace("**", ""))))
                break
        for raw, name in INLINE_BIT.findall(line):
            pairs.add((parse_range(raw), label(name)))
    return pairs


def crosscheck(candidate, catalog, witness):
    """Rows for every field/bit present in either extraction; status never resolves a conflict."""
    rows = []
    for field in sorted(set(candidate) | set(catalog), key=lambda k: _first_byte(candidate, catalog, k)):
        a, b = candidate.get(field), catalog.get(field)
        values = {"candidate": a and a["bytes"], "catalog": b and b["bytes"]}
        rows.append(_row("field", field, None, values, (values["catalog"] or values["candidate"], field) in witness,
                         a and a["state"]))
        bits_a, bits_b = (a or {}).get("bits", {}), (b or {}).get("bits", {})
        for key in sorted(set(bits_a) | set(bits_b), key=lambda r: -int(r.split(":")[0])):
            pair_a, pair_b = bits_a.get(key), bits_b.get(key)
            # A title-only extraction agrees with an abbreviated one when the titles match.
            same_title = pair_a is not None and pair_b is not None and pair_a[1] == pair_b[1]
            values = {"candidate": pair_b[0] if same_title else pair_a and pair_a[0], "catalog": pair_b and pair_b[0]}
            rows.append(_row("bit", field, key, values, (key, values["catalog"] or values["candidate"]) in witness))
    return rows


def summary(rows):
    counts = {}
    for row in rows:
        key = f"{row['kind']}:{row['status']}:{'witnessed' if row['markdown_witness'] else 'unwitnessed'}"
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _row(kind, field, bits, values, witnessed, state=None):
    a, b = values["candidate"], values["catalog"]
    if a is not None and b is not None:
        status = "AGREE" if a == b else "MISMATCH"
    else:
        status = "CATALOG_ONLY" if a is None else "CANDIDATE_ONLY"
    row = {"kind": kind, "field": field, "bits": bits, "status": status,
           "candidate": a, "catalog": b, "markdown_witness": witnessed}
    if state not in (None, "defined"):
        row["candidate_state"] = state
    return row


def _first_byte(candidate, catalog, key):
    item = candidate.get(key) or catalog.get(key)
    return int(item["bytes"].split(":")[-1])
