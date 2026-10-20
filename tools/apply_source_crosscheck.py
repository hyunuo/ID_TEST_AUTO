"""Cross-check Base 2.1 CNS 01h candidates against the nvme-id-ctrl-ko catalog and the Markdown original.

Only bits on which the external catalog and the Markdown witness agree are written back into
structures.json (still review_status=candidate). Everything else stays a review row in the report.
Re-run after tools/extract_identify_structures.py, which regenerates structures.json from PDFs.

    python tools/apply_source_crosscheck.py --catalog ../nvme-id-ctrl-ko/source/catalog.json [--write]
"""
import argparse
import json
import sys
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from ssd_validator.analyzer.source_crosscheck import (  # noqa: E402
    candidate_view, catalog_view, crosscheck, markdown_witness, summary)
from ssd_validator.models.candidates import StructureCandidates  # noqa: E402

DOCUMENT = 'BASE_2_1'
STRUCTURE = 'NVME.CNS01'
MARKDOWN = 'NVM-Express-Base-Specification-Revision-2.1-2024.08.05-Ratified.md'
FIGURE = ('**Figure 312: Identify – Identify Controller', '**Figure 313:')
STRUCTURES = ROOT / 'candidates/nvme/structures.json'
REPORT = ROOT / 'candidates/nvme/crosscheck/base21_cns01.json'


def bit_bounds(text):
    high, _, low = text.partition(':')
    return int(low or high), int(high)


def catalog_bits(catalog):
    return {(f['id'], b['range']): b for f in catalog['fields'] for b in f['bits']}


def anchor(source):
    return {'document_id': DOCUMENT, 'section': source['section'], 'figure': str(source['figure']),
            'pdf_page': source['pdf_page'], 'printed_page': str(source['page'])}


def apply(structures, rows, catalog):
    """Return structures with witnessed catalog bits added or renamed, plus the applied/skipped log."""
    bits = catalog_bits(catalog)
    structure = next(s for s in structures['structures']
                     if s['document_id'] == DOCUMENT and s['structure_id'] == STRUCTURE)
    fields = {f['field_id'].rsplit('.', 1)[-1]: f for f in structure['fields']}
    applied, skipped = [], []
    for row in rows:
        if row['kind'] != 'bit' or row['status'] not in ('CATALOG_ONLY', 'MISMATCH') or not row['markdown_witness']:
            continue
        field = fields.get(row['field'])
        source = bits[(row['field'], row['bits'])]
        lsb, msb = bit_bounds(row['bits'])
        name = source['english'].split(':', 1)[0].strip()
        entry = {'field': row['field'], 'bits': row['bits'], 'name': name, 'action': 'add' if row['status'] == 'CATALOG_ONLY' else 'rename'}
        if field is None:
            skipped.append({**entry, 'reason': 'field not in candidate structure'})
            continue
        current = [b for b in field['bit_fields'] if (b['lsb'], b['msb']) == (lsb, msb)]
        overlap = [b for b in field['bit_fields'] if b not in current and not (b['msb'] < lsb or b['lsb'] > msb)]
        if overlap:
            skipped.append({**entry, 'reason': 'overlaps existing candidate bits: ' + ', '.join(
                f"{b['msb']}:{b['lsb']} {b['name']}" for b in overlap)})
            continue
        replacement = {'name': name, 'lsb': lsb, 'msb': msb, 'state': 'defined', 'evidence': [anchor(source['source'])]}
        if current:
            entry['previous_name'] = current[0]['name']
            field['bit_fields'][field['bit_fields'].index(current[0])] = replacement
        else:
            field['bit_fields'].append(replacement)
            field['bit_fields'].sort(key=lambda b: b['lsb'])
        applied.append(entry)
    StructureCandidates.model_validate(structures)
    return structures, applied, skipped


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--catalog', type=Path, required=True, help='nvme-id-ctrl-ko source/catalog.json')
    parser.add_argument('--write', action='store_true', help='update structures.json and the report')
    args = parser.parse_args()
    catalog_bytes = args.catalog.read_bytes()
    catalog = json.loads(catalog_bytes)
    markdown_path = ROOT / 'spec' / MARKDOWN
    witness = markdown_witness(markdown_path.read_text(encoding='utf-8'), *FIGURE)
    structures = json.loads(STRUCTURES.read_text(encoding='utf-8'))
    rows = crosscheck(candidate_view(structures, DOCUMENT, STRUCTURE), catalog_view(catalog), witness)
    structures, applied, skipped = apply(structures, rows, catalog)
    report = {'kind': 'source_crosscheck', 'format_version': 1, 'document_id': DOCUMENT, 'structure_id': STRUCTURE,
              'review_status': 'candidate',
              'sources': {'candidate': 'candidates/nvme/structures.json (before apply)',
                          'catalog': {'name': 'nvme-id-ctrl-ko source/catalog.json', 'sha256': sha256(catalog_bytes).hexdigest()},
                          'markdown': {'name': f'spec/{MARKDOWN}', 'sha256': sha256(markdown_path.read_bytes()).hexdigest()}},
              'rule': 'Bits are written only when the catalog and the Markdown witness agree; other rows await human review.',
              'summary': summary(rows), 'applied': applied, 'skipped': skipped,
              'review_rows': [r for r in rows if r['status'] != 'AGREE' or not r['markdown_witness']]}
    print(json.dumps({'summary': report['summary'], 'applied': len(applied), 'skipped': len(skipped)}, indent=2))
    if args.write:
        STRUCTURES.write_text(json.dumps(structures, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
        REPORT.parent.mkdir(exist_ok=True)
        REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
