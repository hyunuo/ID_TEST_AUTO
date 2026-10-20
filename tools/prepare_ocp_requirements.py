"""Reproduce source-read OCP candidate subset; never infer a product's applicability."""
import json
import hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PDF=ROOT/'spec'/'OCP2_6.pdf'
HASH='44ccfd8c1b40eae70fa292a231379448182c5987456fe75e0d54fe6befd96872'
DOC='OCP_DSSD_2_6'

def recipe():
    catalog=json.loads((ROOT/'candidates/nvme/catalog.json').read_text(encoding='utf-8'))
    data={'kind':'supplemental_requirement_candidates','format_version':1,
        'document':{'source_type':'spec','source_document':DOC,'source_version':'2.6','title':'OCP Datacenter NVMe SSD Specification Version 2.6 (09252024)',
            'filename':'OCP2_6.pdf','sha256':HASH,'pages':211},
        'product_scope':'PCIe-attached Datacenter NVMe SSD; explicit product/application declaration required',
        'bundles':[], 'pending':[
            {'item':'MFND','status':'excluded','required_inputs':[],'reason':'Explicitly excluded by user; private specification'},
            {'item':'Actual product policies / FW / OCP device profile','status':'awaiting_source','required_inputs':['Product policy document/version','Product applicability and OCP device profile','Exceptions and review basis'],'reason':'No product policy values or product identifiers provided'},
            {'item':'OCP NVMe-1 full compliance','status':'additional_information','required_inputs':['PCIe Transport specification and compliance report'],'reason':'Only focused Base/NVM Identify subset; full compliance not inferred'},
            {'item':'OCP NVMe-AD-19 sanitize override','status':'behavior_required','required_inputs':['TP4152 applicability','Sanitize result and data observations','Independent source review'],'reason':'Behavioral exception is not an Identify field override'},
            {'item':'OCP MDTS / queues / logs / power / security / device profiles','status':'unimplemented','required_inputs':['Relevant registers/logs/features and scoped OCP clauses'],'reason':'Focused first subset, not whole OCP extraction'}]}
    for b in catalog['bundles']:
        if b['bundle_id'] not in ('nvme-2.0e-nvm-1.0e','nvme-2.1-nvm-1.1'):continue
        newer=b['base_document']=='BASE_2_1';base=b['base_document'];nvm=b['nvm_document']
        policy_id='OCP.2_6.'+b['bundle_id']
        gate={'op':'AND','children':[{'op':'EQ','ref':{'source':'context','path':'ocp.datacenter_product'},'value':True},
            {'op':'EQ','ref':{'source':'context','path':'ocp.version'},'value':'2.6'}]}
        def prov(doc,version,section):return {'source_type':'spec','source_document':doc,'source_version':version,'source_section':section,'status':'candidate'}
        policy={'policy_id':policy_id,'title':'OCP 2.6 Identify subset (candidate)','bundle_id':b['bundle_id'],
            'provenance':prov(DOC,'2.6','Sections 3, 4.1 and focused requirements'),'rules':[]}
        item={'bundle_id':b['bundle_id'],'policy':policy,'mappings':[],'requirements':[]}
        def add(req,target,check,page,section,summary,remaining=(),capability=None,bit=None):
            rule={'rule_id':'OCP.2_6.'+req+'.'+target.split('.')[-1], 'target':{'field_id':target},
                'check':check,'condition':gate,'modality':'mandatory','provenance':prov(DOC,'2.6',f'{section} {req} PDF page {page}')}
            if target.startswith('NVME.CNS00.'):
                rule['condition']={'op':'AND','children':[gate,{'op':'EQ','ref':{'source':'context','path':'input.has_namespace'},'value':True},
                    {'op':'EQ','ref':{'source':'context','path':'namespace.query_is_specific'},'value':True}]}
            if capability:
                rule['check']={'type':'CAPABILITY','capability_id':capability,'support':'supported'}
                anchor={'document_id':base if target.startswith('NVME.CNS01.') else nvm,'pdf_page':(341 if newer else 281) if target.endswith('FUSES') else (330 if newer else 270) if target.endswith('OACS') else (81 if newer else 57),
                    'printed_page':str((319 if newer else 281) if target.endswith('FUSES') else (308 if newer else 270) if target.endswith('OACS') else (81 if newer else 57)),
                    'section':('5.1.13.2.1' if newer else '5.17.2.1') if target.startswith('NVME.CNS01.') else '4.1.5.1',
                    'figure':('312' if newer else '280') if target.startswith('NVME.CNS01.') else ('114' if newer else '97')}
                mapping={'capability_id':capability,'target':{'field_id':target,'bit':bit},'supported':1,'unsupported':0,
                    'provenance':prov(anchor['document_id'], ('2.1' if newer else '2.0e') if target.startswith('NVME.CNS01.') else ('1.1' if newer else '1.0e'), f"{anchor['section']} Figure {anchor['figure']} PDF page {anchor['pdf_page']}")}
                if mapping not in item['mappings']:item['mappings'].append(mapping)
            else:anchor=None
            policy['rules'].append(rule)
            item['requirements'].append({'requirement_id':req,'rule_id':rule['rule_id'],'summary':summary,'modality':'mandatory','review_status':'candidate',
                'evidence':{'document_id':DOC,'section':section,'pdf_page':page,'printed_page':str(page)},
                'capability_id':capability,'mapping_evidence':anchor,'remaining':list(remaining),'condition':rule['condition'],
                'product_scope':data['product_scope'],'validation_scope':'Identify advertised values only; command behavior not proven'})
        for req,target,value in [('NVMe-CFG-14','SQES',0x60),('NVMe-CFG-15','CQES',0x40)]:
            add(req,'NVME.CNS01.'+target,{'type':'MASK','mask':0xf0,'value':value},10,'4.3','Exact upper queue-entry exponent; additional to NVMe minimum')
        for field in ('HMPRE','HMMIN'):add('NVMe-CFG-19','NVME.CNS01.'+field,{'type':'EXACT','value':0},10,'4.3','Host memory buffer shall not be supported')
        for req,bit,name,page in [('NVMe-AD-3',3,'NAMESPACE_MANAGEMENT',10),('NVMe-AD-4',3,'NAMESPACE_MANAGEMENT',10),
            ('NVMe-AD-5',1,'FORMAT_NVM',10),('NVMe-AD-6',6,'NVME_MI',10),('NVMe-AD-12',4,'DEVICE_SELF_TEST',11)]:
            add(req,'NVME.CNS01.OACS',{},page,'4.4','Required command advertised support',('Command execution and full clause behavior require separate verification',),capability='OCP.ADVERTISED.'+name,bit=bit)
        add('NVMe-IO-9','NVME.CNS01.FUSES',{},15,'4.5','Required Compare-and-Write fused support',('Actual fused command behavior/atomicity not proven',),capability='OCP.ADVERTISED.COMPARE_WRITE',bit=0)
        add('NVMe-AD-2','NVME.CNS00.NSFEAT',{},10,'4.4','OPTPERF bit required in the NVM Namespace response',('FPI progress and I/O hint values are not implemented in this subset',),capability='OCP.ADVERTISED.OPTPERF',bit=4)
        data['bundles'].append(item)
    return data

if __name__=='__main__':
    if hashlib.sha256(PDF.read_bytes()).hexdigest()!=HASH:raise ValueError('Original OCP PDF changed; re-review before extraction')
    output=ROOT/'candidates/ocp/requirements.json';output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(recipe(),ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Candidate subset only:',output)
