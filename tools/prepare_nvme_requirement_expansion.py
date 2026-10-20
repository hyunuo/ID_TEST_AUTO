"""Source-read stage 5 candidate recipe; verifies original PDF bytes before writing.

This is a focused reviewed-by-AI interpretation, not approval or full extraction.
Run with the bundled PDF Python: --pdf-dir .. ; default output is a candidate source.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
NS='NVME.CNS00.'
CTRL='NVME.CNS01.'

def ref(identity,index=None,bit=None):
    return {'field_id':identity,**({'index':index} if index is not None else {}),**({'bit':bit} if bit is not None else {})}

def eq(identity,value,index=None):
    return {'op':'EQ','ref':{'source':'actual','field':ref(identity,index)},'value':value}

def bit(identity,n,set=True):
    return {'op':'BIT_SET' if set else 'BIT_CLEAR','ref':{'source':'actual','field':ref(identity)},'bit':n}

def nonzero(identity,index=None):
    return {'op':'NOT','children':[eq(identity,0,index)]}

def ctx(path,value):
    return {'op':'EQ','ref':{'source':'context','path':path},'value':value}

def both(*conditions):
    return {'op':'AND','children':list(conditions)}

def recipe(catalog):
    documents={d['document_id']:d for d in catalog['documents']}
    output={'kind':'nvme_requirement_expansion','format_version':1,
        'document_hashes':{k:d['sha256'] for k,d in documents.items()},'bundles':[]}
    for bundle in catalog['bundles']:
        if bundle['bundle_id'] not in {'nvme-2.0e-nvm-1.0e','nvme-2.1-nvm-1.1'}:continue
        newer=bundle['nvm_document']=='NVM_1_1'
        base=bundle['base_document'];nvm=bundle['nvm_document']
        base_section='5.1.13.2.1' if newer else '5.17.2.1'
        base_figure='312' if newer else '280'
        ns_figure='114' if newer else '97'
        item={'bundle_id':bundle['bundle_id'],'fields':[],'rules':[],'replacements':[],'coverage':[]}
        def anchor(doc,page,section,figure=None):
            return {'document_id':doc,'pdf_page':page,'printed_page':str(page-22 if doc=='BASE_2_1' else page),
                'section':section,'figure':figure}
        def evidence(doc,page,section=None,figure=None):
            return anchor(doc,page,section or (base_section if doc==base else '4.1.5.1'),figure if figure is not None else
                (None if section in {'2.1.1','5.5'} else base_figure if doc==base else ns_figure))
        def field(identity,name,offset,length,value_type,doc,page,*,array=None,bits=()):
            item['fields'].append({'schema':{'field_id':identity,'name':name,'command':'id-ns' if identity.startswith(NS) else 'id-ctrl',
                'offset':offset,'length':length,'endian':'little','value_type':value_type,'state':'defined',
                'bits':[{'bit':n,'state':'defined'} for n in bits]},
                'binding':{'cns':0 if identity.startswith(NS) else 1,'csi':0,'response_size':4096,
                    'array_count':array,'array_stride':4 if array else None},
                'evidence':{'review_status':'candidate','description':name+'; source-read focused mapping, independent review pending',
                    'evidence':[evidence(doc,page)]}})
        def rule(name,target,check,doc,page,condition=None,*,section=None,figure=None,exceptions=(),dependencies=(),statement='',index=None):
            a=evidence(doc,page,section,figure)
            r={'rule_id':'NVME.STAGE5.'+name,'target':ref(target,index),'check':check,'modality':'mandatory',
                'provenance':{'source_type':'spec','source_document':doc,'source_version':documents[doc]['revision'],
                    'source_section':f"{a['section']} PDF page {page}"+(f" Figure {a['figure']}" if a['figure'] else ''),'status':'candidate'}}
            if condition:r['condition']=condition
            item['rules'].append({'rule':r,'review':{'statement':statement,'modality':'mandatory','evidence':[a],
                'conditions':condition,'exceptions':list(exceptions),'dependencies':list(dependencies),
                'unresolved':['Independent human review pending'],'review_status':'candidate'}})
        def compare(other,op):return {'type':'FIELD_COMPARE','operator':op,'other':ref(other)}
        # These are fixed width fields actually used by executable rules, not a full structure extraction.
        for suffix,name,offset,length,kind,page in [
            ('HMPRE','Host Memory Buffer Preferred Size (HMPRE)',272,4,'integer',334 if newer else 274),
            ('HMMIN','Host Memory Buffer Minimum Size (HMMIN)',276,4,'integer',334 if newer else 274),
            ('RPMBS','Replay Protected Memory Block Support (RPMBS)',312,4,'bitmask',334 if newer else 275),
            ('FUSES','Fused Operation Support (FUSES)',522,2,'bitmask',341 if newer else 281),
            ('ACWU','Atomic Compare and Write Unit (ACWU)',532,2,'integer',92 if newer else 66)]:
            field(CTRL+suffix,name,offset,length,kind,nvm if suffix=='ACWU' else base,page)
            if suffix=='ACWU':item['fields'][-1]['evidence']['evidence']=[evidence(nvm,page,'4.1.5.2','117' if newer else '99')]
        if newer:field(CTRL+'DSTO','Device Self-test Options (DSTO)',318,1,'bitmask',base,335,bits=(0,1))
        for suffix,name,offset,length,kind,page in [
            ('NSZE','Namespace Size (NSZE)',0,8,'integer',80 if newer else 57),
            ('NCAP','Namespace Capacity (NCAP)',8,8,'integer',80 if newer else 57),
            ('NUSE','Namespace Utilization (NUSE)',16,8,'integer',80 if newer else 57),
            ('NSFEAT','Namespace Features (NSFEAT)',24,1,'bitmask',81 if newer else 57),
            ('NLBAF','Number of LBA Formats (NLBAF)',25,1,'integer',81 if newer else 58),
            ('NAWUN','Namespace Atomic Write Unit Normal (NAWUN)',34,2,'integer',84 if newer else 60),
            ('NAWUPF','Namespace Atomic Write Unit Power Fail (NAWUPF)',36,2,'integer',84 if newer else 60),
            ('NABSN','Namespace Atomic Boundary Size Normal (NABSN)',40,2,'integer',85 if newer else 61),
            ('NABO','Namespace Atomic Boundary Offset (NABO)',42,2,'integer',85 if newer else 61),
            ('NABSPF','Namespace Atomic Boundary Size Power Fail (NABSPF)',44,2,'integer',85 if newer else 61)]:
            field(NS+suffix,name,offset,length,kind,nvm,page,bits=(0,1,6) if suffix=='NSFEAT' and newer else (0,1) if suffix=='NSFEAT' else ())
        field(NS+'LBAF.MS','Metadata Size (MS)',128,2,'integer',nvm,90 if newer else 65,array=64)
        field(NS+'LBAF.LBADS','LBA Data Size (LBADS)',130,1,'integer',nvm,90 if newer else 65,array=64)
        for f in item['fields'][-2:]:f['evidence']['evidence']=[evidence(nvm,90 if newer else 65,'4.1.5.1','116' if newer else '98'),evidence(nvm,89 if newer else 64)]
        ns_gate=both(ctx('input.has_namespace',True),ctx('namespace.query_is_specific',True))
        rule('CAPACITY.NCAP_LE_NSZE',NS+'NCAP',compare(NS+'NSZE','<='),nvm,12 if newer else 10,ns_gate,
            section='2.1.1',statement='Namespace capacity cannot exceed size',dependencies=('CNS00 specific namespace response','NCAP','NSZE'))
        rule('CAPACITY.NUSE_LE_NCAP',NS+'NUSE',compare(NS+'NCAP','<='),nvm,12 if newer else 10,ns_gate,
            section='2.1.1',statement='Utilization cannot exceed capacity',dependencies=('NUSE','NCAP'))
        rule('THINP.ZERO_NCAP',NS+'NCAP',compare(NS+'NSZE','='),nvm,12 if newer else 10,both(ns_gate,bit(NS+'NSFEAT',0,False)),
            section='2.1.1',statement='Without thin provisioning capacity equals size',exceptions=('NUSE=NCAP is MAY, not mandatory',),dependencies=('NSFEAT.THINP','NCAP','NSZE'))
        rule('NLBAF.COMMON_MAX63',NS+'NLBAF',{'type':'MAX','value':63},nvm,150 if newer else 58,ns_gate,
            section='5.5' if newer else '4.1.5.1',statement='Common-format count cannot exceed physical 64-entry storage',
            exceptions=('NVM1.1 total NLBAF+1+NULBAF check is not implemented',),dependencies=('NLBAF',))
        rule('NLBAF.HOST_NO_EXTENSION_MAX15',NS+'NLBAF',{'type':'MAX','value':15},nvm,150 if newer else 58,
            both(ns_gate,ctx('host.lbaf_extension_enabled',False)),section='5.5' if newer else '4.1.5.1',
            statement='Without Host LBAFEE, common format count is at most 16',exceptions=('Host feature must be recorded; not inferred from tool version',),dependencies=('Host Behavior Support.LBAFEE','NLBAF'))
        for index in range(64):
            valid=both(ns_gate,{'op':'GE','ref':{'source':'actual','field':ref(NS+'NLBAF')},'value':index})
            rule(f'LBADS.{index}.NONZERO_MIN9',NS+'LBAF.LBADS',{'type':'MIN','value':9},nvm,90 if newer else 65,
                both(valid,nonzero(NS+'LBAF.LBADS',index)),figure='116' if newer else '98',index=index,
                statement='Available common-prefix LBA formats encode at least 512 bytes',
                exceptions=('Zero means unavailable; no error or expected zero','Only common format prefix 0..NLBAF checked; NVM1.1 unique formats pending'),dependencies=('NLBAF',f'LBAF[{index}].LBADS'))
            rule(f'METADATA.{index}.ABSENT_ZERO',NS+'LBAF.MS',{'type':'EXACT','value':0},nvm,90 if newer else 65,
                both(valid,ctx(f'namespace.lbaf.{index}.metadata_supported',False)),figure='116' if newer else '98',index=index,
                statement='Explicit absence of format metadata requires MS=0',exceptions=('Metadata support must be supplied; not inferred from Reserved or LBADS=0',),
                dependencies=('NLBAF',f'namespace.lbaf.{index}.metadata_supported',f'LBAF[{index}].MS'))
        atomic=both(ns_gate,bit(NS+'NSFEAT',1),*([bit(NS+'NSFEAT',6,False)] if newer else []))
        atom_page=14 if newer else 12;atom_section='2.1.4.1' if newer else '2.1.4'
        for name,target,other,op,guards in [
            ('NAWUN_BASELINE',NS+'NAWUN',CTRL+'AWUN','>=',[nonzero(NS+'NAWUN')]),
            ('NAWUPF_BASELINE',NS+'NAWUPF',CTRL+'AWUPF','>=',[nonzero(NS+'NAWUPF')]),
            ('NAWUPF_LE_NAWUN',NS+'NAWUPF',NS+'NAWUN','<=',[nonzero(NS+'NAWUPF'),nonzero(NS+'NAWUN')]),
            ('NAWUPF_LE_INHERITED_AWUN',NS+'NAWUPF',CTRL+'AWUN','<=',[nonzero(NS+'NAWUPF'),eq(NS+'NAWUN',0)]),
            ('NAWUN_GE_INHERITED_AWUPF',NS+'NAWUN',CTRL+'AWUPF','>=',[eq(NS+'NAWUPF',0),nonzero(NS+'NAWUN')])]:
            rule('ATOMIC.'+name,target,compare(other,op),nvm,atom_page,both(atomic,*guards),section=atom_section,figure='4',
                statement='Compare supported single-atomicity parameters with zero-inheritance handled explicitly',
                exceptions=('NSABP=0 means reserved: never expected=0','NVM1.1 MAM=1 excluded from this Figure4 subset'),dependencies=('NSFEAT.NSABP','NSFEAT.MAM' if newer else 'NVM1.0e atomic parameters',target,other))
            item['rules'][-1]['review']['evidence'].append(evidence(nvm,84 if newer else 60))
        rule('ATOMIC.NO_BOUNDARIES_NABO_ZERO',NS+'NABO',{'type':'EXACT','value':0},nvm,85 if newer else 61,
            both(atomic,eq(NS+'NABSN',0),eq(NS+'NABSPF',0)),statement='Both boundary sizes zero require offset zero',dependencies=('NSABP','NABSN','NABSPF','NABO'))
        for other in ('NABSN','NABSPF'):
            rule('ATOMIC.NABO_LE_'+other,NS+'NABO',compare(NS+other,'<='),nvm,atom_page,
                both(atomic,nonzero(NS+'NABSN'),nonzero(NS+'NABSPF')),section=atom_section,figure='4',
                statement='Offset within both supported nonzero atomic boundaries',exceptions=('One-sided zero boundary interpretation requires review; not evaluated by this subset',),dependencies=('NABSN','NABSPF','NABO'))
        for boundary,unit,baseline in [('NABSN','NAWUN','AWUN'),('NABSPF','NAWUPF','AWUPF')]:
            for inherited in (False,True):
                other=CTRL+baseline if inherited else NS+unit
                rule('ATOMIC.'+boundary+'_GE_'+('INHERITED_' if inherited else '')+baseline if inherited else 'ATOMIC.'+boundary+'_GE_'+unit,
                    NS+boundary,compare(other,'>='),nvm,atom_page,both(atomic,nonzero(NS+boundary),eq(NS+unit,0) if inherited else nonzero(NS+unit)),
                    section=atom_section,figure='4',statement='Supported boundary accommodates effective atomic unit',
                    exceptions=('Zero atomic unit inherits baseline; zero boundary means unsupported',),dependencies=(boundary,unit,baseline))
        queue_page=340 if newer else 280
        for name,value in [('SQES',96),('CQES',64)]:
            rule('QUEUE.'+name+'_MAX_REQUIRED',CTRL+name,{'type':'MIN','value':value},base,queue_page,
                statement='Maximum nibble accommodates the mandatory minimum exponent',exceptions=('Combined with required low-nibble MASK; larger maxima are allowed, recommended equality is not mandatory',),dependencies=(name,))
        rule('FEATURE.RPMB_SECURITY',CTRL+'OACS',{'type':'BIT_SET','bit':0},base,334 if newer else 275,
            {'op':'OR','children':[bit(CTRL+'RPMBS',n) for n in range(3)]},
            statement='Nonzero RPMB unit count requires Security Send/Receive',exceptions=('Optional feature consistency does not remove independent product support requirements',),dependencies=('RPMBS[2:0]','OACS.SECURITY'))
        item['rules'][-1]['review']['evidence'].append(evidence(base,330 if newer else 270))
        rule('FEATURE.ACWU_UNSUPPORTED_ZERO',CTRL+'ACWU',{'type':'EXACT','value':0},nvm,92 if newer else 66,bit(CTRL+'FUSES',0,False),
            section='4.1.5.2',figure='117' if newer else '99',statement='Unsupported Compare-and-Write explicitly requires ACWU=0',dependencies=('FUSES.COMPARE_WRITE','ACWU'))
        item['rules'][-1]['review']['evidence'].append(evidence(base,341 if newer else 281))
        rule('HMB.PREFERRED_GE_MINIMUM',CTRL+'HMPRE',compare(CTRL+'HMMIN','>='),base,334 if newer else 274,
            statement='Preferred host memory size is at least minimum',dependencies=('HMPRE','HMMIN'))
        if newer:
            rule('FEATURE.HIR_REQUIRES_DST',CTRL+'DSTO',{'type':'BIT_CLEAR','bit':1},base,335,bit(CTRL+'OACS',4,False),
                statement='Host-initiated refresh support is clear without Device Self-test',exceptions=('Not applied to Base2.0e where bit1 is reserved',),dependencies=('OACS.DSTS','DSTO.HIRS'))
        old=json.loads((ROOT/f'knowledge/experimental/id_ctrl/{bundle["bundle_id"]}.json').read_text(encoding='utf-8'))
        atomic_old=next(r for r in old['rules'] if r['rule_id']=='EXPERIMENTAL.ATOMIC_POWER_FAIL_BOUND')
        replacement={**atomic_old};replacement.pop('condition',None)
        item['replacements'].append({'expected':atomic_old,'replacement':replacement,
            'review':{'statement':'CNS01 AWUPF <= AWUN is explicitly mandatory in the field definition in both revisions; legacy application-context gate removed',
                'evidence':[evidence(nvm,91 if newer else 66,'4.1.5.2','117' if newer else '99')],
                'modality':'mandatory','exceptions':['Does not establish real write/power-failure behavior'],'dependencies':['AWUN','AWUPF'],'review_status':'candidate'}})
        item['coverage']=[
            {'topic':'Capacity / THINP','status':'executable','scope':'Specific CNS00 namespace; NSID unknown -> UNKNOWN','dependencies':['NSZE','NCAP','NUSE','NSFEAT']},
            {'topic':'NUSE = NCAP with THINP=0','status':'not_mandatory','scope':'MAY; no required equality rule','dependencies':[]},
            {'topic':'Thin provisioning allocation tracking','status':'behavior_required','scope':'Single saved response cannot prove allocations/deallocations','dependencies':['Writes/deallocation history']},
            {'topic':'ANA cleared NUSE/NVMCAP','status':'additional_information','scope':'ANA state + CMIC + NVMCAP required; not executed','dependencies':['Current ANA state','ANA source closure']},
            {'topic':'LBADS / MS / common format count','status':'executable_with_information','scope':'Common format prefix only; metadata support and Host LBAFEE missing -> UNKNOWN','dependencies':['NLBAF','LBAF index','metadata support','Host Behavior Support']},
            {'topic':'Active FLBAS lookup / unique formats','status':'unimplemented','scope':'Dynamic format lookup; '+('NLBAF+1+NULBAF totals and unique attributes not executed' if newer else 'no NVM1.1 unique-format fields backported'),'dependencies':['FLBAS']+(['NULBAF','CNS09/0A for unique format attributes'] if newer else [])},
            {'topic':'Atomic encoded parameter relationships','status':'executable','scope':'Explicit NSABP/sentinel branches; NVM1.1 Figure4 subset excludes MAM=1','dependencies':['Controller + namespace','Atomic format/session association']},
            {'topic':'One-sided zero atomic boundary','status':'review_required','scope':'NABO range subset requires both sizes positive; no implicit zero comparison','dependencies':['Boundary applicability review']},
            {'topic':'Atomicity under writes / power failure','status':'behavior_required','scope':'Data-field relationships do not prove real atomic writes','dependencies':['Command workload','Power failure observations']},
            {'topic':'Queue entry / RPMB / fused consistency','status':'executable','scope':'Both mandatory low nibble and required maximum; feature consistency independent from product policy','dependencies':['SQES','CQES','RPMBS','OACS','FUSES','ACWU']},
            {'topic':'Multiple Atomicity Mode new fields','status':'unimplemented' if newer else 'not_applicable','scope':'Version-specific rules beyond conservative Single Atomicity subset','dependencies':['NVM1.1 section 2.1.4.5']},
        ]
        output['bundles'].append(item)
    return output

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--pdf-dir',type=Path,required=True)
    parser.add_argument('--output',type=Path,default=ROOT/'candidates/nvme/executable_requirements.json');args=parser.parse_args()
    catalog=json.loads((ROOT/'candidates/nvme/catalog.json').read_text(encoding='utf-8'))
    for d in catalog['documents']:
        if hashlib.sha256((args.pdf_dir/d['filename']).read_bytes()).hexdigest()!=d['sha256']:
            raise ValueError('Original PDF hash differs: '+d['document_id'])
    target=args.output.resolve()
    protected={(ROOT/'candidates/nvme'/name).resolve() for name in ('catalog.json','structures.json','requirements.json')}
    if target.suffix!='.json' or 'generated' in target.parts or 'knowledge' in target.parts or target in protected or target in {(args.pdf_dir/d['filename']).resolve() for d in catalog['documents']}:
        raise ValueError('Output must be a separate candidate JSON, never generated or original PDF')
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(recipe(catalog),indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
    print('Candidate recipe only; human review pending:',target)

if __name__=='__main__':main()
