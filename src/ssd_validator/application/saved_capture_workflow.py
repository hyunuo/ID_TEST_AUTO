"""One saved inspection, isolated DUT/session/namespace scopes, existing core engines."""
import base64
import json
import re
from collections import defaultdict
from hashlib import sha256

from ssd_validator.analyzer.actual_normalizer import layout_from_profile, normalize_json, normalize_raw
from ssd_validator.analyzer.saved_response import text_rows, json_rows
from ssd_validator.application.desktop_workflow import DesktopWorkflow
from ssd_validator.application.knowledge_management import METADATA
from ssd_validator.models.actual_data import CaptureMetadata, IdentifyQuery
from ssd_validator.models.runtime import ActualFact, EffectiveExpectedProfile, FieldRef
from ssd_validator.models.effective import SourceFile
from ssd_validator.models.saved_captures import SavedCaptureSet
from ssd_validator.resolver import evaluate

PRIORITY = ('ERROR','CONFLICT','FAIL','UNKNOWN','REVIEW','PASS','N/A')


def worst(states, default='UNKNOWN'):
    return next((s for s in PRIORITY if s in states), default)


def controller_capture(capture):
    return capture.command=='id-ctrl' or capture.command=='identify' and capture.cns==1


def normalize_capture(capture, profile, bundle, bindings):
    data = capture.data()
    source = {'path':capture.filename,'sha256':sha256(data).hexdigest()}
    common = {'capture_id':capture.capture_id,'source':source,
        'metadata':{k:('UNKNOWN' if v is None else v) for k,v in capture.model_dump(mode='json').items() if k!='content_base64'},
        'original_content_base64':base64.b64encode(data).decode('ascii'),
        'observations':[], 'actual_facts':[], 'issues':[], 'normalization':None,'validation_facts':[], 'status':'UNKNOWN'}
    expected_cns = {'id-ctrl':1,'id-ns':0}.get(capture.command)
    if expected_cns is not None and capture.cns is not None and capture.cns != expected_cns:
        common.update(status='ERROR', issues=[{'reason':'Command and explicit CNS disagree; no automatic substitution'}])
        return common, ()
    cns = capture.cns if capture.cns is not None else expected_cns
    csi = capture.csi if capture.csi is not None else (0 if expected_cns is not None else None)
    common['interpretation'] = {'cns':cns,'csi':csi,'basis':'Explicit query where supplied; named command adapter otherwise. Collection metadata remains UNKNOWN.'}
    rows, payload, blocked = [], {}, set()
    try:
        if capture.source_format == 'text':
            if capture.command == 'identify':
                raise ValueError('Generic identify text needs a verified command adapter')
            rows, issues, parsed = text_rows(data,capture.filename,capture.command)
            common.update(issues=issues, parsed=parsed)
            if any('Duplicate' in item.get('reason','') for item in issues):
                common['status']='CONFLICT'
        elif capture.source_format == 'json':
            rows, duplicates, original = json_rows(data)
            common['tool_output'] = original
            if duplicates:
                common.update(status='CONFLICT',issues=[{'reason':'Duplicate JSON keys; entire capture excluded','duplicates':duplicates}])
                common['observations'] = rows
                return common, ()
        elif capture.cns is None or capture.csi is None:
            common['issues'] = [{'reason':'Raw bytes require explicit CNS and CSI; no query inferred'}]
            return common, ()
    except (ValueError,UnicodeError) as error:
        common.update(status='ERROR',issues=[{'reason':str(error)}])
        return common, ()
    definitions = []
    for structure in bundle['structures']:
        if structure['cns'] == cns:
            for definition in structure['definitions']:
                definitions.extend(definition['fields'])
    registrations = [f for f in profile.fields if (f.cns,f.csi)==(cns,csi)]
    definitions.extend({'field_id':f.schema_definition.field_id,'name':f.schema_definition.name} for f in registrations)
    seen_names = set()
    for observation in rows:
        name, index = observation['field'], observation.get('index')
        name_key = (name.casefold(),index)
        ids = set()
        for definition in definitions:
            aliases = {definition['field_id'].casefold(),definition['field_id'].split('.')[-1].casefold(),definition['name'].casefold()}
            aliases.update(a.casefold() for a in re.findall(r'\b[A-Z][A-Z0-9]{1,}\b',definition['name']))
            if name.casefold() in aliases:
                ids.add(definition['field_id'])
        if 'json_path' in observation:
            path=observation['json_path']
            simple=(len(path)==1 or len(path)==2 and type(path[1]) is int)
            if not simple:
                # A future nested extension named like a known scalar is not its registered JSON path.
                # One array of structures is allowed only with a named container in the field ID.
                ids={identity for identity in ids if len(path)==3 and type(path[1]) is int and
                    path[0].casefold().rstrip('s') in {p.casefold().rstrip('s') for p in identity.split('.')[2:-1]}}
                if not ids:
                    observation['mapping_reason']='Nested JSON path has no verified field/container mapping; preserved only'
        observation.update(field_ids=sorted(ids),status='REVIEW' if len(ids)==1 else 'CONFLICT' if ids else 'UNKNOWN')
        if len(ids)>1 or name_key in seen_names:
            common['status']='CONFLICT'
            observation['status']='CONFLICT'
            common['issues'].append({'reason':'Duplicate observation or ambiguous field mapping','field':name,'index':index})
            blocked.update(identity+(f'[{index}]' if index is not None else '') for identity in ids)
        seen_names.add(name_key)
        if len(ids)==1:
            identity=next(iter(ids))+(f'[{index}]' if index is not None else '')
            observation['field_key']=identity
            if identity in payload:
                blocked.add(identity)
                common['status']='CONFLICT'
            else:
                payload[identity]=observation['value']
    for key in blocked:
        payload.pop(key,None)
    for observation in rows:
        if observation.get('field_key') in blocked:
            observation['status']='CONFLICT'
    common['observations']=rows
    common['actual_facts']=[ActualFact(field=FieldRef(field_id=o['field_ids'][0],index=o.get('index')),
        value=o['value'],source=SourceFile.model_validate(source),capture_id=capture.capture_id).model_dump(mode='json')
        for o in rows if len(o['field_ids'])==1 and o.get('field_key') not in blocked]
    if not registrations:
        common['issues'].append({'reason':'No executable fields registered for this response in selected Bundle; observations retained'})
        return common, ()
    query=IdentifyQuery(cns=cns,csi=csi,nsid=None if controller_capture(capture) else capture.nsid)
    sizes={bindings.get(f.schema_definition.field_id,{}).get('response_size',4096) for f in registrations}
    if len(sizes)!=1:
        raise ValueError('Inconsistent registered response sizes')
    paths={f.schema_definition.field_id+(f'[{i}]' if f.array_count is not None else ''):
        (f.schema_definition.field_id+(f'[{i}]' if f.array_count is not None else ''),)
        for f in registrations for i in range(f.array_count or 1)}
    layout=layout_from_profile(profile,query,response_size=next(iter(sizes)),json_paths=paths,
        array_strides={k:v['array_stride'] for k,v in bindings.items() if v.get('array_stride')})
    adapter=CaptureMetadata(capture_id=capture.capture_id,tool_name=capture.tool_name,tool_version=capture.tool_version,
        tool_commit=capture.tool_commit,device_id=capture.dut_id or 'UNKNOWN',query=query)
    normalized=(normalize_raw(layout,adapter,data,source_path=capture.filename) if capture.source_format=='raw' else
        normalize_json(layout,adapter,payload,source_path=capture.filename,source_bytes=data))
    dump=normalized.model_dump(mode='json')
    dump['source_format']=capture.source_format
    dump['interpretation_capture']=dump.pop('capture')
    common['normalization']=dump
    if normalized.status=='ERROR':
        common['status']='ERROR'
    elif common['status']!='CONFLICT':
        common['status']=normalized.status
    facts=tuple(ActualFact(field=f.definition.field,value=f.value,source=normalized.source,capture_id=capture.capture_id)
        for f in normalized.fields if f.status in {'OBSERVED','REVIEW'} and f.definition.value_type!='bytes')
    common['validation_facts']=[f.model_dump(mode='json') for f in facts]
    if capture.source_format=='raw':
        common['actual_facts']=common['validation_facts']
    return common,facts


def analyze_captures(root, package, bundle_id, *, experimental=True, context_facts=None, policy_mode='assumed-development',profile_id=None):
    inputs=SavedCaptureSet.model_validate(package)
    workflow=DesktopWorkflow(root)
    baseline=workflow.analyze(b'NVME Identify Controller:\nsn:SOURCE_VALIDATION\n','profile-only.txt',bundle_id,
        experimental=True,context_facts=context_facts,policy_mode=policy_mode)
    profile=EffectiveExpectedProfile.model_validate(baseline['validation']['profile'])
    _,bundles,_,_=workflow.candidates()
    meta=root/METADATA
    bindings=json.loads(meta.read_text(encoding='utf-8')).get('bindings',{}).get(bundle_id,{}) if meta.exists() else {}
    normalized={c.capture_id:normalize_capture(c,profile,bundles[bundle_id],bindings) for c in inputs.captures}
    from ssd_validator.application.product_profiles import read_registry,selection_for_scope
    products=read_registry(root) if profile_id else None
    if products is not None:
        from ssd_validator.application.product_profiles import PRODUCTS
        product_source={'path':(root/PRODUCTS).as_posix(),'sha256':sha256((root/PRODUCTS).read_bytes()).hexdigest()}
    groups=defaultdict(list)
    for c in inputs.captures:
        # Missing identity/session never implies co-ownership, even if filenames or serials match.
        groups[(c.dut_id,c.session_id) if c.dut_id and c.session_id else ('isolated',c.capture_id)].append(c)
    scopes=[]
    for group in sorted(groups,key=str):
        controllers=[c for c in groups[group] if controller_capture(c)]
        namespaces=defaultdict(list)
        for c in groups[group]:
            if not controller_capture(c):
                namespaces[c.nsid if c.nsid is not None else 'UNKNOWN:'+c.capture_id].append(c)
        selections=[(ns,controllers+caps) for ns,caps in sorted(namespaces.items(),key=lambda x:str(x[0]))] or [(None,controllers)]
        for ns,caps in selections:
            scope_id='scope-'+str(len(scopes)+1)
            scoped_context=dict(context_facts or {})
            if type(ns) is int:
                if 'namespace.nsid' in scoped_context and scoped_context['namespace.nsid'] != ns:
                    raise ValueError('Context NSID disagrees with capture scope')
                scoped_context['namespace.nsid']=ns
            elif scoped_context.get('namespace.nsid') is not None:
                raise ValueError('Unknown capture NSID cannot be filled from Context')
            product_selection=None
            extra_rules=()
            selected_policy_mode=policy_mode
            context_base=None
            if profile_id:
                product_selection,scoped_context,extra_rules=selection_for_scope(products,profile_id,bundle_id,
                    [normalized[c.capture_id][0] for c in caps],context_facts,ns)
                product_selection['registry_source']=product_source
                if type(ns) is int:
                    scoped_context['namespace.nsid']=ns
                context_base={}
                selected_policy_mode='spec-only'
            input_context=None
            if any(e.rule.rule_id.startswith('NVME.STAGE5.') for e in profile.entries):
                input_context={'input.has_controller':bool(controllers),
                    'input.has_namespace':any(normalized[c.capture_id][0].get('interpretation',{}).get('cns')==0 for c in caps)}
                if type(ns) is int:
                    input_context['namespace.query_is_specific']=0<ns<0xffffffff
                scoped_context.pop('namespace.query_is_specific',None)
                scoped_context.update(input_context)
            scoped=workflow.analyze(b'NVME Identify Controller:\nsn:SOURCE_VALIDATION\n','profile-only.txt',bundle_id,
                experimental=True,context_facts=scoped_context,policy_mode=selected_policy_mode,
                context_base=context_base,extra_rules=extra_rules,scope_context=True)['validation']
            scope_profile=EffectiveExpectedProfile.model_validate(scoped['profile'])
            facts_by_key=defaultdict(list)
            query_groups=defaultdict(list)
            for c in caps:
                query_groups[(c.command,c.cns,c.csi)].append(c.capture_id)
                for fact in normalized[c.capture_id][1]:
                    facts_by_key[fact.field.key].append(fact)
            conflicts=[{'field':key,'capture_ids':[f.capture_id for f in facts]} for key,facts in sorted(facts_by_key.items()) if len(facts)>1]
            conflicts.extend({'query':list(key),'capture_ids':ids} for key,ids in query_groups.items() if len(ids)>1)
            facts=tuple(values[0] for key,values in sorted(facts_by_key.items()) if len(values)==1)
            result=evaluate(scope_profile,facts).model_dump(mode='json') if experimental else {'status':'REVIEW','results':[],'profile':scoped['profile']}
            states=[normalized[c.capture_id][0]['status'] for c in caps]
            # UNKNOWN normalization for an unregistered response limits coverage, not a rule FAIL.
            if conflicts or 'CONFLICT' in states:
                result['status']='CONFLICT'
            if 'ERROR' in states:
                result['status']='ERROR'
            if product_selection:
                state=product_selection['applicability']['state']
                if state!='TRUE' and result['status'] not in {'ERROR','CONFLICT'}:
                    result['status']='N/A' if state=='FALSE' else state
            scope={'scope_id':scope_id,'dut_id':caps[0].dut_id or 'UNKNOWN','session_id':caps[0].session_id or 'UNKNOWN',
                'nsid':ns if type(ns) is int else 'UNKNOWN','capture_ids':[c.capture_id for c in caps],
                'conflicts':conflicts,'actual_facts':[f.model_dump(mode='json') for f in facts],
                'observed_actual_facts':[f for c in caps for f in normalized[c.capture_id][0]['actual_facts']],
                'validation':result,'selection':scoped['selection']}
            if input_context is not None:
                scope['input_context']={'facts':input_context,'basis':'Selected response adapters and explicitly recorded NSID; no collection flags or activity status inferred'}
            if product_selection:
                scope['product_selection']=product_selection
                scope['selection']['policy_mode']='product-profile'
                scope['product_selection']['effective_context']=scoped['profile']['context']
            from ssd_validator.application.supplemental_requirements import trace
            supplemental=trace(root,result,bundle_id,product_selection)
            if supplemental is not None:scope['supplemental_trace']=supplemental
            scopes.append(scope)
    captures=[normalized[c.capture_id][0] for c in inputs.captures]
    return {'kind':'saved_capture_inspection','bundle':baseline['bundle'],'authoritative':False,
        'validation_scope':'experimental_unreviewed_rules' if experimental else 'candidate_review_only',
        'captures':captures,'scopes':scopes,
        'validation':{'status':worst([s['validation']['status'] for s in scopes]),'results':[r for s in scopes for r in s['validation']['results']]},
        'assumptions':[] if profile_id else baseline['validation']['assumptions'],
        'coverage_note':'추가 실제 id-ns 형식과 Namespace 규칙은 원본 로그·검토가 필요합니다. 일부 Controller 규칙의 PASS는 전체 Namespace 적합성 판정이 아닙니다.'}
