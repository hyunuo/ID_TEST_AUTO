"""Lossless saved text/JSON observations. No specification requirements generated."""
import json
import re
from .id_ctrl_log import analyze_id_ctrl, NUMBER, TEXT_FIELDS, _number


def text_rows(data, filename, command):
    if command == 'id-ctrl':
        parsed = analyze_id_ctrl(data, filename)
        return parsed['fields'], parsed['issues'], parsed
    text = data.decode('utf-8-sig')
    header = re.compile(r'^\s*NVME\s+Identify\s+Namespace(?:\s+\d+)?\s*:\s*$', re.I)
    rows, issues, seen = [], [], False
    for line_no, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        if header.fullmatch(line):
            if seen:
                raise ValueError('Only one Namespace response per capture')
            seen = True
            continue
        if not seen:
            issues.append({'line':line_no, 'text':line, 'reason':'Before Namespace header'})
            continue
        array = re.fullmatch(r'\s*lbaf\s+(\d+)\s*:\s*(.*)', line, re.I)
        if array:
            matches = list(re.finditer(r'([A-Za-z][A-Za-z0-9_]*)\s*:\s*(0[xX][0-9a-fA-F]+|\d+)', array[2]))
            for item in matches:
                rows.append(row(item[1], item[2], line_no, int(array[1]), line))
            issues.append({'line':line_no,'text':line,'reason':'Original LBAF expression retained'})
            continue
        match = re.fullmatch(r'\s*([A-Za-z][A-Za-z0-9_.]*)(?:\[(\d+)\])?\s*:\s*(.*?)\s*',line)
        if match:
            rows.append(row(match[1],match[3],line_no,int(match[2]) if match[2] else None,line))
        else:
            issues.append({'line':line_no,'text':line,'reason':'Unrecognized line'})
    if not seen or not rows:
        raise ValueError('No readable NVME Identify Namespace response')
    return rows, issues, {'raw_text':text}


def row(name, value, line, index=None, original=None):
    numeric = name.casefold() not in TEXT_FIELDS and NUMBER.fullmatch(value)
    return {'field':name,'index':index,'raw_value':value,'value':_number(value) if numeric else value,
            'line':line,'original_line':original}


def json_rows(data):
    duplicates = []
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                duplicates.append({'key':key,'values':[result[key],value]})
            result[key] = value
        return result
    payload = json.loads(data.decode('utf-8-sig'), object_pairs_hook=pairs)
    if not isinstance(payload,dict):
        raise ValueError('Saved JSON must be an object')
    rows = []
    def walk(value, path=(), index=None):
        if isinstance(value,dict):
            for key, child in value.items():
                walk(child,path+(key,),index)
        elif isinstance(value,list):
            for i,child in enumerate(value):
                walk(child,path+(i,),i)
        else:
            name = next((p for p in reversed(path) if isinstance(p,str)), '')
            indexed = re.fullmatch(r'(.+)\[(\d+)\]',name)
            rows.append({'field':indexed[1] if indexed else name,'index':int(indexed[2]) if indexed else index,
                         'value':value,'raw_value':json.dumps(value,ensure_ascii=False),'line':None,'json_path':list(path)})
    walk(payload)
    return rows, duplicates, payload
