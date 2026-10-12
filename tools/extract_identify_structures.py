"""Reproducible, conservative extraction of unapproved Identify structure candidates.

Run with pypdf installed. Source PDFs are never changed. Table text is retained
so extraction gaps remain inspectable rather than silently becoming knowledge.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from pypdf import PdfReader
import pdfplumber

DOCS = {
    "BASE_2_0E": ("NVM-Express-Base-Specification-2.0e-2024.07.29-Ratified.pdf", 0),
    "BASE_2_1": ("NVM-Express-Base-Specification-Revision-2.1-2024.08.05-Ratified.pdf", 22),
    "NVM_1_0E": ("NVM-Express-NVM-Command-Set-Specification-1.0e-2024.07.29-Ratified.pdf", 0),
    "NVM_1_1": ("NVM-Express-NVM-Command-Set-Specification-Revision-1.1-2024.08.05-Ratified.pdf", 0),
}
# Actual body captions, not the sometimes stale list of figures.
TABLES = [
    ("BASE_2_0E", 1, 280, 262, 287, "5.17.2.1", None),
    ("BASE_2_0E", 8, 285, 292, 294, "5.17.2.8", None),
    ("BASE_2_1", 1, 312, 321, 350, "5.1.13.2.1", None),
    ("BASE_2_1", 8, 319, 357, 360, "5.1.13.2.8", None),
    ("NVM_1_0E", 0, 97, 57, 64, "4.1.5.1", 0),
    ("NVM_1_0E", 1, 99, 65, 66, "4.1.5.2", 0),
    ("NVM_1_0E", 5, 100, 67, 67, "4.1.5.3", 0),
    ("NVM_1_0E", 6, 102, 69, 70, "4.1.5.4", 0),
    ("NVM_1_1", 0, 114, 80, 89, "4.1.5.1", 0),
    ("NVM_1_1", 1, 117, 90, 92, "4.1.5.2", 0),
    ("NVM_1_1", 5, 118, 93, 97, "4.1.5.3", 0),
    ("NVM_1_1", 6, 120, 99, 103, "4.1.5.4", 0),
]
NESTED = [
    ("BASE_2_0E", "PSD", 281, 287, 288, "5.17.2.1", 32),
    ("BASE_2_1", "PSD", 313, 350, 353, "5.1.13.2.1", 32),
    ("NVM_1_0E", "LBAF", 98, 64, 65, "4.1.5.1", 4),
    ("NVM_1_0E", "ELBAF", 101, 68, 68, "4.1.5.3", 4),
    ("NVM_1_1", "LBAF", 116, 90, 90, "4.1.5.1", 4),
    ("NVM_1_1", "ELBAF", 119, 97, 98, "4.1.5.3", 4),
]


def evidence(doc, section, figure, page):
    return {"document_id": doc, "section": section, "figure": str(figure),
            "pdf_page": page, "printed_page": str(page - DOCS[doc][1])}


def table_lines(reader, figure, first, last):
    active = False
    for page in range(first, last + 1):
        text = reader.pages[page - 1].extract_text() or ""
        for line in text.splitlines():
            line = line.strip()
            caption = re.match(r"Figure (\d+):", line)
            if caption:
                active = int(caption[1]) == figure
                continue
            if re.match(r"\d+(?:\.\d+){2,}\s+(?:Identify|I/O |Active |Allocated|Namespace |NVM )", line):
                active = False
            if active and line and not re.match(r"NVM Express|^Bytes\b|^Bits Description", line):
                yield page, line


def name_state(text, offset):
    if text.startswith("Reserved"):
        return f"RESERVED_{offset}", "Reserved", "reserved"
    if text.startswith("Vendor Specific"):
        return f"VENDOR_SPECIFIC_{offset}", "Vendor Specific", "vendor_specific"
    head = text.split(":", 1)[0].strip()
    acronyms = re.findall(r"\(\s*([A-Z][A-Z0-9_]*)\s*\)", head)
    key = acronyms[-1] if acronyms else f"FIELD_{offset}"
    state = "delegated" if re.search(r"This field is as defined|Refer to the applicable I/O Command Set|This field is specific to", text) else "defined"
    return key, head, state


def bit_candidates(lines, ev, max_bits):
    lines=[(p,part.strip()) for p,text in lines for part in text.splitlines()]
    result = []
    occupied=set()
    for i, (_, line) in enumerate(lines):
        match = re.match(r"(?:Bits?\s+)?(\d+):(\d+)\s*(.*)", line, re.I)
        if not match:
            single=re.match(r'^Bit\s+(\d+)\s+(.*)',line,re.I)
            if single:
                high=low=int(single[1])
                tail=single[2]
            elif re.fullmatch(r'\d+',line) and i+1<len(lines) and re.match(r'^[A-Z].+\([A-Z0-9]+\):',lines[i+1][1]):
                high=low=int(line)
                tail=lines[i+1][1]
            else:
                continue
        else:
            high, low = int(match[1]), int(match[2])
            tail = match[3] or (lines[i + 1][1] if i + 1 < len(lines) else "")
        if not 0 <= low <= high < max_bits:
            continue
        bits=set(range(low,high+1))
        if occupied & bits:
            continue
        # Unlabelled single-bit rows and enum values are not guessed.
        result.append({"name": tail.split(":", 1)[0][:160], "lsb": low, "msb": high,
                       "state": "reserved" if "reserved" in tail.lower() else "defined",
                       "evidence": [dict(ev, pdf_page=lines[i][0], printed_page=str(lines[i][0] - DOCS[ev['document_id']][1]))]})
        occupied |= bits
    return result


def extract(reader, config, layout):
    doc, cns, fig, first, last, section, csi = config
    lines = list(table_lines(reader, fig, first, last))
    fields = []
    current = None
    for page in range(first,last+1):
        for table in layout.pages[page-1].find_tables():
            rows=table.extract()
            if table.bbox[0] > 100 or not rows:
                continue
            header=' '.join(str(c or '') for c in rows[0])
            has_header='Bytes' in header
            if not has_header and not re.fullmatch(r'\d+(?::\d+)?',(rows[0][0] or '').strip()):
                continue
            for cells in (rows[1:] if has_header else rows):
                first_cell=(cells[0] or '').strip()
                match=re.fullmatch(r'(\d+)(?::(\d+))?', first_cell)
                contents=[c for c in cells[1:] if c and not re.fullmatch(r'(?:[1-5]\s*)?[MOR][1-5]?',c.strip())]
                text='\n'.join(contents)
                if match:
                    high,low=int(match[1]),int(match[2] or match[1])
                    if high < low or high > 4095: continue
                    current={'offset':low,'length':high-low+1,'lines':[(page,text)],'page':page}
                    fields.append(current)
                elif current and not first_cell:
                    current['lines'].append((page,text))
    output = []
    for field in fields:
        text = "\n".join(t for _, t in field["lines"]).strip()
        key, name, state = name_state(text, field["offset"])
        ev = evidence(doc, section, fig, field["page"])
        item = {"field_id": f"NVME.CNS{cns:02X}.{key}", "name": name,
                "byte_offset": field["offset"], "byte_length": field["length"], "state": state,
                "evidence": [evidence(doc,section,fig,p) for p in sorted({p for p,_ in field['lines']})], "bit_fields": bit_candidates(field["lines"], ev, field["length"]*8),
                "array": None, "description": text, "review_status": "candidate"}
        if key == 'CMIC':
            # Pilot source comparison: Base2.0e p262 / Base2.1 printed299.
            # 2.0e uses prose labels; 2.1 adds the acronyms.
            names={0:'Multiple Ports',1:'Multiple Controllers',2:'Function Type',3:'Asymmetric Namespace Access Reporting Support'}
            item['bit_fields']=[{'name':label,'lsb':bit,'msb':bit,'state':'defined','evidence':[ev]}
                                for bit,label in names.items()]
            item['bit_fields'].append({'name':'Reserved','lsb':4,'msb':7,'state':'reserved','evidence':[ev]})
        output.append(item)
    # Ellipses are defined fixed repetitions, with endpoints retained as evidence.
    for prefix, count, stride in [("PSD", 32, 32), ("LBAF", 64, 4), ("ELBAF", 64, 4)]:
        members = [f for f in output if re.search(rf"\.{prefix}\d+$", f["field_id"])]
        if len(members) >= 2:
            start = min(members, key=lambda x:x['byte_offset'])
            end = max(members, key=lambda x:x['byte_offset'])
            if end['byte_offset'] - start['byte_offset'] == (count-1)*stride:
                array = dict(start, field_id=f"NVME.CNS{cns:02X}.{prefix}", name=f"{prefix} descriptors",
                             byte_length=count*stride, array={"count": count, "stride_bytes": stride},
                             nested_template_id=f"{doc}.{prefix}", bit_fields=[],
                             evidence=start['evidence']+end['evidence'],
                             description="\n".join(m['description'] for m in members))
                output = [f for f in output if f not in members] + [array]
    output.sort(key=lambda f:f['byte_offset'])
    occupied = set()
    overlap = set()
    for f in output:
        span=set(range(f['byte_offset'], f['byte_offset']+f['byte_length']))
        overlap |= span & occupied
        occupied |= span
    unresolved = ["Candidate extraction: human source comparison required; bit-field coverage is not complete.",
                  "Applicability columns, footnotes, value encodings and inherited definitions remain in source text for review."]
    missing = sorted(set(range(4096))-occupied)
    if missing:
        unresolved.append(f"Unparsed or intentionally delegated byte coverage: {len(missing)} bytes; see coverage_gaps.")
    if overlap:
        unresolved.append(f"Extracted byte overlap: {len(overlap)} bytes; requires review.")
    return {"structure_id": f"NVME.CNS{cns:02X}", "document_id": doc, "cns": cns, "csi": csi,
            "size_bytes":4096, "fields":output, "evidence":[evidence(doc, section, fig, p) for p in range(first,last+1)],
            "unresolved":unresolved, "coverage_status":"partial", "byte_coverage_complete":not missing and not overlap,
            "coverage_gaps": ranges(missing), "coverage_overlaps":ranges(sorted(overlap)),
            "source_rows":[{"pdf_page":p,"text":t} for p,t in lines]}


def ranges(values):
    out=[]
    for value in values:
        if out and value == out[-1][1]+1:
            out[-1][1]=value
        else:
            out.append([value,value])
    return out


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=Path('candidates/nvme/structures.json'))
    args=parser.parse_args()
    project_root=Path(__file__).resolve().parents[1]
    output=args.output.resolve()
    inputs={doc:(args.source_dir / filename).resolve() for doc,(filename,_) in DOCS.items()}
    if output.suffix.lower() != '.json' or output in inputs.values() or output.is_relative_to(project_root/'generated'):
        parser.error('Output must be JSON outside generated/ and must not overwrite any input PDF')
    catalog=json.loads((project_root/'candidates/nvme/catalog.json').read_text(encoding='utf-8'))
    pinned={d['document_id']:d for d in catalog['documents']}
    hashes={doc:hashlib.sha256(path.read_bytes()).hexdigest() for doc,path in inputs.items()}
    for doc,path in inputs.items():
        if pinned[doc]['filename'] != path.name or pinned[doc]['sha256'] != hashes[doc]:
            parser.error(f'Source identity/hash mismatch: {doc}; fixed page extraction refused')
    readers={doc:PdfReader(args.source_dir / filename) for doc,(filename,_) in DOCS.items()}
    layouts={doc:pdfplumber.open(args.source_dir / filename) for doc,(filename,_) in DOCS.items()}
    structures=[extract(readers[c[0]], c, layouts[c[0]]) for c in TABLES]
    nested=[]
    for doc,name,fig,first,last,section,size in NESTED:
        lines=list(table_lines(readers[doc],fig,first,last))
        ev=evidence(doc,section,fig,first)
        nested.append({"template_id":f"{doc}.{name}","size_bytes":size,
                       "coordinate_system":"bit offsets relative to each array element; lsb=0",
                       "bit_fields":bit_candidates(lines,ev,size*8),
                       "source_rows":[{"pdf_page":p,"text":t} for p,t in lines],
                       "evidence":[evidence(doc,section,fig,p) for p in range(first,last+1)],
                       "review_status":"candidate", "coverage_status":"partial"})
    payload={"kind":"structure_candidates","format_version":1,"document_hashes":hashes,"structures":structures,"nested_templates":nested,
             "review_status":"candidate","extraction_note":"Conservative machine candidates; source rows are authoritative review evidence, not approved knowledge."}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({"structures":len(structures),"nested_templates":len(nested),"fields":sum(len(s['fields']) for s in structures),
                      "byte_complete":sum(s['byte_coverage_complete'] for s in structures)}))


if __name__ == '__main__':
    main()
