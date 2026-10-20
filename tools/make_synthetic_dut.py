"""Generate a synthetic TEST DUT (no real device) as consistent raw / nvme-cli text / nvme-cli JSON captures.

One value table per variant is encoded into 4096-byte Identify responses using the candidate
layouts in candidates/nvme/structures.json (Base 2.1 CNS 01h, NVM 1.1 CNS 00h). Text and JSON are
rendered from the same values in nvme-cli's print style, so every format describes the same
device. The 'violations' variant changes listed values to break known rules on purpose.

    python tools/make_synthetic_dut.py   # rewrites tests/fixtures/synthetic_dut/
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'tests/fixtures/synthetic_dut'
ABBR = re.compile(r'\(([A-Z][A-Z0-9_]*)\)')

# nvme-cli field order; values are synthetic and only need to be self-consistent.
CONTROLLER = {
    'vid': 0xFFFF, 'ssvid': 0xFFFF, 'sn': 'TESTSYN0000000000001', 'mn': 'TEST SYNTHETIC NVME SSD NOT A REAL DUT',
    'fr': 'TEST0001', 'rab': 2, 'ieee': 0x001234, 'cmic': 0, 'mdts': 5, 'cntlid': 1, 'ver': 0x20100,
    'rtd3r': 8000000, 'rtd3e': 8000000, 'oaes': 0x200, 'ctratt': 0, 'rrls': 0, 'bpcap': 0, 'nssl': 0, 'plsi': 0,
    'cntrltype': 1, 'crdt1': 0, 'crdt2': 0, 'crdt3': 0, 'crcap': 0, 'nvmsr': 0, 'vwci': 0, 'mec': 0,
    'oacs': 0x5E, 'acl': 3, 'aerl': 7, 'frmw': 0x16, 'lpa': 0x1E, 'elpe': 63, 'npss': 0, 'avscc': 1, 'apsta': 0,
    'wctemp': 343, 'cctemp': 353, 'mtfa': 0, 'hmpre': 0, 'hmmin': 0, 'tnvmcap': 3840755982336, 'unvmcap': 0,
    'rpmbs': 0, 'edstt': 30, 'dsto': 0, 'fwug': 0, 'kas': 0, 'hctma': 0, 'mntmt': 0, 'mxtmt': 0, 'sanicap': 0x3,
    'hmminds': 0, 'hmmaxd': 0, 'nsetidmax': 0, 'endgidmax': 0, 'anatt': 0, 'anacap': 0, 'anagrpmax': 0,
    'nanagrpid': 0, 'pels': 0, 'domainid': 0, 'kpioc': 0, 'mptfawr': 0, 'megcap': 0, 'tmpthha': 0, 'cqt': 0,
    'sqes': 0x66, 'cqes': 0x44, 'maxcmd': 0, 'nn': 128, 'oncs': 0x5F, 'fuses': 1, 'fna': 0x4, 'vwc': 0x6,
    'awun': 255, 'awupf': 0, 'icsvscc': 0, 'nwpc': 0, 'acwu': 0, 'ocfs': 0, 'sgls': 0, 'mnan': 0, 'maxdna': 0,
    'maxcna': 0, 'oaqd': 0, 'subnqn': 'nqn.2026-10.test.synthetic:nvme:TESTSYN0000000000001',
    'ioccsz': 0, 'iorcsz': 0, 'icdoff': 0, 'fcatt': 0, 'msdbd': 0, 'ofcs': 0,
}
POWER_STATES = [{'MP': 2500, 'MXPS': 0, 'NOPS': 0, 'ENLAT': 0, 'EXLAT': 0, 'RRT': 0, 'RRL': 0, 'RWT': 0, 'RWL': 0}]
NAMESPACE = {
    'nsze': 7501476528, 'ncap': 7501476528, 'nuse': 7501476528, 'nsfeat': 0x10, 'nlbaf': 1, 'flbas': 0, 'mc': 0,
    'dpc': 0, 'dps': 0, 'nmic': 0, 'rescap': 0, 'fpi': 0, 'dlfeat': 9, 'nawun': 0, 'nawupf': 0, 'nacwu': 0,
    'nabsn': 0, 'nabo': 0, 'nabspf': 0, 'noiob': 0, 'nvmcap': 3840755982336, 'npwg': 7, 'npwa': 7, 'npdg': 7,
    'npda': 7, 'nows': 7, 'mssrl': 0, 'mcl': 0, 'msrc': 0, 'nulbaf': 0, 'anagrpid': 0, 'nsattr': 0, 'nvmsetid': 0,
    'endgid': 0, 'nguid': 0x7E57000000000000000000000000ABCD, 'eui64': 0x0012340000005678,
}
LBA_FORMATS = [{'MS': 0, 'LBADS': 9, 'RP': 1}, {'MS': 0, 'LBADS': 12, 'RP': 0}]
VIOLATIONS = {
    'controller': {'sqes': 0x55, 'cqes': 0x33, 'hmpre': 10, 'hmmin': 20, 'awun': 4, 'awupf': 8},
    'namespace': {'ncap': 7501476529, 'nuse': 7501476530},
}
TEXT_HEX = {'vid', 'ssvid', 'cntlid', 'ver', 'rtd3r', 'rtd3e', 'oaes', 'ctratt', 'oacs', 'frmw', 'lpa', 'avscc',
            'apsta', 'sanicap', 'sqes', 'cqes', 'oncs', 'fuses', 'fna', 'vwc', 'sgls', 'nsfeat', 'nsze', 'ncap', 'nuse'}
SPEC_NAMES = {'domainid': 'DID', 'ocfs': 'CDFS'}  # nvme-cli name -> specification abbreviation


def label(name):
    found = ABBR.findall(name.split(':', 1)[0]) or ABBR.findall(name)
    return found[-1] if found else None


def layout(document_id, structure_id):
    data = json.loads((ROOT / 'candidates/nvme/structures.json').read_text(encoding='utf-8'))
    structure = next(s for s in data['structures'] if s['document_id'] == document_id and s['structure_id'] == structure_id)
    templates = {t['template_id']: t for t in data['nested_templates']}
    fields = {label(f['name']) or f['field_id'].rsplit('.', 1)[-1]: f for f in structure['fields']}
    return fields, templates


def put(buffer, offset, length, value):
    if isinstance(value, str):
        encoded = value.encode('ascii')
        pad = b'\0' if length > 40 else b' '  # SUBNQN is NUL padded; SN/MN/FR are space padded.
        buffer[offset:offset + length] = encoded.ljust(length, pad)[:length]
    else:
        buffer[offset:offset + length] = value.to_bytes(length, 'little')


def put_elements(buffer, field, template, elements):
    bits = {label(b['name']): b for b in template['bit_fields'] if b['state'] == 'defined'}
    stride = field['array']['stride_bytes']
    for index, element in enumerate(elements):
        word = 0
        for name, value in element.items():
            bit = bits[name]
            if value >= 1 << (bit['msb'] - bit['lsb'] + 1):
                raise ValueError(f'{name} does not fit')
            word |= value << bit['lsb']
        start = field['byte_offset'] + index * stride
        buffer[start:start + stride] = word.to_bytes(stride, 'little')


def encode(values, elements, document_id, structure_id, array_field, template_id):
    fields, templates = layout(document_id, structure_id)
    buffer = bytearray(4096)
    for name, value in values.items():
        field = fields[SPEC_NAMES.get(name, name.upper())]
        put(buffer, field['byte_offset'], field['byte_length'], value)
    put_elements(buffer, fields[array_field], templates[template_id], elements)
    return bytes(buffer)


def controller_text(values, powers):
    lines = ['NVME Identify Controller:']
    for name, value in values.items():
        if name == 'ieee':
            shown = f'{value:06x}'
        elif isinstance(value, str):
            shown = value
        else:
            shown = f'{value:#x}' if name in TEXT_HEX and value else str(value)
        lines.append(f'{name:<10}: {shown}')
    for index, ps in enumerate(powers):
        lines.append(f'ps {index:>4} : mp:{ps["MP"] / 100:.2f}W operational enlat:{ps["ENLAT"]} exlat:{ps["EXLAT"]} '
                     f'rrt:{ps["RRT"]} rrl:{ps["RRL"]}')
        lines.append(f'          rwt:{ps["RWT"]} rwl:{ps["RWL"]} idle_power:- active_power:-')
    return '\n'.join(lines) + '\n'


def namespace_text(values, formats):
    lines = ['NVME Identify Namespace 1:']
    for name, value in values.items():
        if name in ('nguid', 'eui64'):
            shown = f'{value:0{32 if name == "nguid" else 16}x}'
        else:
            shown = f'{value:#x}' if name in TEXT_HEX and value else str(value)
        lines.append(f'{name:<8}: {shown}')
    for index, lbaf in enumerate(formats):
        in_use = ' (in use)' if index == values['flbas'] & 0xF else ''
        lines.append(f'lbaf {index:>2} : ms:{lbaf["MS"]:<3} lbads:{lbaf["LBADS"]:<2} rp:{lbaf["RP"]:#x}{in_use}'.rstrip())
    return '\n'.join(lines) + '\n'


def controller_json(values, powers):
    out = {k: v for k, v in values.items()}
    out['psds'] = [{'max_power': p['MP'], 'max_power_scale': p['MXPS'], 'non-operational_state': p['NOPS'],
                    'entry_lat': p['ENLAT'], 'exit_lat': p['EXLAT'], 'read_tput': p['RRT'], 'read_lat': p['RRL'],
                    'write_tput': p['RWT'], 'write_lat': p['RWL']} for p in powers]
    return json.dumps(out, indent=2) + '\n'


def namespace_json(values, formats):
    out = {k: (f'{v:032x}' if k == 'nguid' else v) for k, v in values.items()}
    out['lbafs'] = [{'ms': f['MS'], 'ds': f['LBADS'], 'rp': f['RP']} for f in formats]  # nvme-cli names LBADS "ds"
    return json.dumps(out, indent=2) + '\n'


def write(variant, controller, namespace):
    files = {
        f'{variant}-id-ctrl.bin': encode(controller, POWER_STATES, 'BASE_2_1', 'NVME.CNS01', 'PSD', 'BASE_2_1.PSD'),
        f'{variant}-id-ns.bin': encode(namespace, LBA_FORMATS, 'NVM_1_1', 'NVME.CNS00', 'LBAF', 'NVM_1_1.LBAF'),
        f'{variant}-id-ctrl.txt': controller_text(controller, POWER_STATES).encode(),
        f'{variant}-id-ns.txt': namespace_text(namespace, LBA_FORMATS).encode(),
        f'{variant}-id-ctrl.json': controller_json(controller, POWER_STATES).encode(),
        f'{variant}-id-ns.json': namespace_json(namespace, LBA_FORMATS).encode(),
    }
    for name, content in files.items():
        (OUTPUT / name).write_bytes(content)


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    write('TEST-good', CONTROLLER, NAMESPACE)
    write('TEST-violations', {**CONTROLLER, **VIOLATIONS['controller']}, {**NAMESPACE, **VIOLATIONS['namespace']})
    (OUTPUT / 'violations.json').write_text(json.dumps(VIOLATIONS, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(f'wrote {OUTPUT}')


if __name__ == '__main__':
    sys.exit(main())
