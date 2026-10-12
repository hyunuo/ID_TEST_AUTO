"""Revisioned product data and conservative suggestions; no invented product definitions."""
import json
import re
from hashlib import sha256
from typing import Literal
from pydantic import Field, StrictInt, model_validator
from ssd_validator.models.common import DomainModel, Identifier, Text, require_unique
from ssd_validator.models.provenance import Provenance
from ssd_validator.models.runtime import RuntimeRule

PRODUCTS='knowledge/products.json'


class FirmwareComparison(DomainModel):
    method: Literal['exact','numeric_components','ordered_labels']
    component_count: StrictInt | None = Field(default=None, ge=1, le=8)
    labels: tuple[Text,...] = ()

    @model_validator(mode='after')
    def shape(self):
        if self.method=='numeric_components' and self.component_count is None:
            raise ValueError('Numeric FW comparison needs an explicit component count')
        if self.method!='numeric_components' and self.component_count is not None:
            raise ValueError('Component count is only for numeric FW')
        if self.method=='ordered_labels' and not self.labels or self.method!='ordered_labels' and self.labels:
            raise ValueError('Ordered FW comparison needs its explicit label sequence only')
        require_unique(list(self.labels),'FW label')
        return self

    def key(self,value):
        if not isinstance(value,str):
            return None
        if self.method=='exact':
            return value
        if self.method=='ordered_labels':
            return self.labels.index(value) if value in self.labels else None
        if not re.fullmatch(r'[0-9]+(?:\.[0-9]+)*',value):
            return None
        parts=value.split('.')
        try:
            return tuple(int(p) for p in parts) if len(parts)==self.component_count else None
        except ValueError:
            return None


class ProfileCriterion(DomainModel):
    source: Literal['observed','user']
    path: Text
    operator: Literal['EQ','FW_RANGE'] = 'EQ'
    value: object = None
    minimum: Text | None = None
    maximum: Text | None = None

    @model_validator(mode='after')
    def shape(self):
        if self.operator=='FW_RANGE':
            if self.path!='firmware' or self.minimum is None and self.maximum is None or self.value is not None:
                raise ValueError('FW_RANGE requires firmware and at least one bound')
        elif self.minimum is not None or self.maximum is not None or self.value is None or type(self.value) not in {str,int,bool}:
            raise ValueError('EQ requires one typed scalar value')
        return self


class ProductProfile(DomainModel):
    profile_id: Identifier
    title: Text
    bundle_id: Identifier
    policy_ids: tuple[Identifier,...] = ()
    context_id: Identifier | None = None
    conditions: tuple[ProfileCriterion,...] = ()
    firmware_comparison: FirmwareComparison | None = None
    provenance: Provenance

    @model_validator(mode='after')
    def unique(self):
        require_unique(list(self.policy_ids),'profile policy')
        return self


class ProductPolicy(DomainModel):
    policy_id: Identifier
    title: Text
    bundle_id: Identifier
    rules: tuple[RuntimeRule,...] = Field(min_length=1)
    provenance: Provenance

    @model_validator(mode='after')
    def unique(self):
        require_unique([r.rule_id for r in self.rules],'policy rule')
        return self


class ProductContext(DomainModel):
    context_id: Identifier
    title: Text
    bundle_id: Identifier
    facts: dict[str,object] = Field(default_factory=dict)
    fact_kinds: dict[str,Literal['declared','assumption']] = Field(default_factory=dict)
    provenance: Provenance

    @model_validator(mode='after')
    def shape(self):
        if self.facts.keys()!=self.fact_kinds.keys() or any(type(v) not in {str,int,bool} for v in self.facts.values()):
            raise ValueError('Each Context fact needs a typed scalar and declared/assumption origin')
        if any(k.startswith(('product.','input.')) or k in {'namespace.nsid','namespace.query_is_specific'} for k in self.facts):
            raise ValueError('Product selection and observed NSID cannot be preset Context')
        return self


class ProductRegistry(DomainModel):
    format_version: StrictInt = Field(default=1,ge=1,le=1)
    profiles: tuple[ProductProfile,...] = ()
    policies: tuple[ProductPolicy,...] = ()
    contexts: tuple[ProductContext,...] = ()

    @model_validator(mode='after')
    def unique(self):
        for collection,key in [(self.profiles,'profile_id'),(self.policies,'policy_id'),(self.contexts,'context_id')]:
            require_unique([getattr(item,key) for item in collection],key)
        return self


def registry(sources):
    from ssd_validator.application.rule_pilot import _unique_object
    return ProductRegistry.model_validate(json.loads(sources.get(PRODUCTS,'{}'),object_pairs_hook=_unique_object))


def read_registry(root):
    path=root/PRODUCTS
    return registry({PRODUCTS:path.read_text(encoding='utf-8')} if path.exists() else {})


def product_entities(sources):
    data=registry(sources)
    return [(kind,item.bundle_id,getattr(item,key),item.model_dump(mode='json'))
        for kind,collection,key in [('profile',data.profiles,'profile_id'),('product_policy',data.policies,'policy_id'),('context',data.contexts,'context_id')]
        for item in collection]


def validate_products(root,sources):
    from ssd_validator.application.knowledge_management import config, yaml_read, bundle_ids
    data=registry(sources)
    policies={p.policy_id:p for p in data.policies};contexts={c.context_id:c for c in data.contexts}
    for item in [*data.profiles,*data.policies,*data.contexts]:
        if item.bundle_id not in bundle_ids(sources):
            raise ValueError('Product entity references unknown Bundle')
        docs=yaml_read(sources[f'knowledge/experimental/id_ctrl/{item.bundle_id}/catalog.yaml'])['sources']
        known={(d['source_type'],d['source_document'],d['source_version']) for d in docs}
        evidence=[item.provenance]
        if isinstance(item,ProductPolicy):
            cfg=config(sources,item.bundle_id)
            if set(r.rule_id for r in item.rules)&set(r['rule_id'] for r in cfg['rules']):
                raise ValueError('Product rule ID collides with Bundle rule')
            for rule in item.rules:
                evidence.extend([rule.provenance,*rule.supporting_evidence])
                if rule.override:
                    evidence.append(rule.override.provenance)
        for provenance in evidence:
            if provenance.key not in known:
                raise ValueError('Product provenance document/version is not registered')
            if provenance.status=='confirmed' and (not provenance.verified_by or not provenance.verified_date):
                raise ValueError('Confirmed product data requires reviewer/date')
        if isinstance(item,ProductProfile):
            if any(p not in policies or policies[p].bundle_id!=item.bundle_id for p in item.policy_ids):
                raise ValueError('Profile policy references unknown or different Bundle')
            if item.context_id and (item.context_id not in contexts or contexts[item.context_id].bundle_id!=item.bundle_id):
                raise ValueError('Profile Context references unknown or different Bundle')
            ids=[r.rule_id for p in item.policy_ids for r in policies[p].rules]
            require_unique(ids,'combined product rule')
            for condition in item.conditions:
                if condition.path=='firmware' and item.firmware_comparison:
                    fw=item.firmware_comparison
                    if condition.operator=='FW_RANGE' and fw.method=='exact':
                        raise ValueError('Exact FW comparison does not define a range/order')
                    for bound in ([condition.value] if condition.operator=='EQ' else [condition.minimum,condition.maximum]):
                        if bound is not None and fw.key(bound) is None:
                            raise ValueError('FW bound is not defined by registered comparison')
                    if condition.minimum is not None and condition.maximum is not None and fw.key(condition.minimum)>fw.key(condition.maximum):
                        raise ValueError('FW minimum exceeds maximum')
        if isinstance(item,ProductPolicy):
            from ssd_validator.application.desktop_workflow import DesktopWorkflow
            result=DesktopWorkflow(root).analyze(b'NVME Identify Controller:\nsn:SOURCE_VALIDATION\n','validation.txt',item.bundle_id,
                experimental=True,policy_mode='spec-only',extra_rules=item.rules,context_base={})
            if any(e['state']=='ERROR' for e in result['validation']['profile']['entries']):
                raise ValueError('Product policy contains invalid field/Capability/condition references')


def match_profile(profile,observed,user):
    trace=[]
    for criterion in profile.conditions:
        values=observed if criterion.source=='observed' else user
        present=criterion.path in values and values[criterion.path] is not None
        actual=values.get(criterion.path)
        state='UNKNOWN'
        reason='Required selection fact missing'
        if present:
            if criterion.path=='firmware':
                fw=profile.firmware_comparison
                if fw is None:
                    reason='No registered FW comparison; no numeric or lexical inference'
                else:
                    key=fw.key(actual)
                    if key is None:
                        reason='Observed FW is outside the registered encoding/labels'
                    elif criterion.operator=='EQ':
                        wanted=fw.key(criterion.value)
                        state='TRUE' if wanted is not None and key==wanted else 'FALSE' if wanted is not None else 'UNKNOWN'
                        reason='Registered FW comparison'
                    else:
                        lo=fw.key(criterion.minimum) if criterion.minimum is not None else None
                        hi=fw.key(criterion.maximum) if criterion.maximum is not None else None
                        if fw.method=='exact' or criterion.minimum is not None and lo is None or criterion.maximum is not None and hi is None:
                            reason='FW ordering/bound unavailable'
                        else:
                            state='TRUE' if (lo is None or key>=lo) and (hi is None or key<=hi) else 'FALSE'
                            reason='Inclusive bounds using registered FW comparison'
            else:
                state='TRUE' if type(actual) is type(criterion.value) and actual==criterion.value else 'FALSE'
                reason='Typed equality; no value coercion'
        trace.append({'criterion':criterion.model_dump(mode='json'),'found':present,'actual':actual,'state':state,'reason':reason})
    states={x['state'] for x in trace}
    return {'profile_id':profile.profile_id,'state':'FALSE' if 'FALSE' in states else 'UNKNOWN' if 'UNKNOWN' in states else 'TRUE',
        'trace':trace,'provenance':profile.provenance.model_dump(mode='json')}


def observed_identity(captures):
    values={}; conflicts=[{'capture_id':c['capture_id'],'reason':'Ambiguous controller capture'} for c in captures
        if c.get('status')=='CONFLICT' and c.get('metadata',{}).get('command') in {'id-ctrl','identify'}]
    for path,name in [('model','mn'),('firmware','fr'),('serial','sn')]:
        found=[]
        for capture in captures:
            if capture.get('metadata',{}).get('command') not in {'id-ctrl','identify'} or capture.get('status') in {'ERROR','CONFLICT'}:
                continue
            for row in capture.get('observations',[]):
                if row['field'].casefold()==name and row.get('index') is None and row.get('status') not in {'ERROR','CONFLICT'} and row.get('json_path',[name])==[name]:
                    found.append((row['value'],capture['capture_id'],capture['source']))
        if found and all(type(v[0]) is str and v[0]==found[0][0] for v in found):
            values[path]=found[0][0]
        elif found:
            conflicts.append({'path':path,'observations':found})
    return values,conflicts


def selection_for_scope(data,profile_id,bundle_id,captures,user,namespace=None):
    profile=next((p for p in data.profiles if p.profile_id==profile_id),None)
    if profile is None:
        raise ValueError('Unknown Product Profile')
    if profile.provenance.status=='deprecated':
        raise ValueError('Deprecated Profile cannot be selected')
    if profile.bundle_id!=bundle_id:
        raise ValueError('PROFILE_BUNDLE_MISMATCH: explicitly choose the Profile Bundle')
    observed,conflicts=observed_identity(captures)
    if type(namespace) is int:
        observed['namespace.nsid']=namespace
    matching=match_profile(profile,observed,user or {})
    if conflicts:
        matching['state']='CONFLICT'
    preset=next((c for c in data.contexts if c.context_id==profile.context_id),None)
    base=dict(preset.facts) if preset else {}
    merged=dict(base)
    for key,value in (user or {}).items():
        if key.startswith('product.'):
            raise ValueError('Product applicability is derived from selection, not user-overridable')
        if value is None:
            merged.pop(key,None)
        else:
            merged[key]=value
    merged['product.profile_applicable']=True if matching['state']=='TRUE' else False if matching['state']=='FALSE' else None
    policies=[p for identity in profile.policy_ids for p in data.policies if p.policy_id==identity]
    from ssd_validator.models.runtime import Condition
    gate={'op':'EQ','ref':{'source':'context','path':'product.profile_applicable'},'value':True}
    rules=[]
    for policy in policies:
        for rule in policy.rules:
            condition=Condition.model_validate({'op':'AND','children':[gate,rule.condition.model_dump(mode='json')]} if rule.condition else gate)
            rules.append(rule.model_copy(update={'condition':condition}))
    snapshot={'profile':profile.model_dump(mode='json'),'profile_hash':sha256(profile.model_dump_json().encode()).hexdigest(),
        'policies':[p.model_dump(mode='json') for p in policies],'context_preset':preset.model_dump(mode='json') if preset else None,
        'applicability':matching,'observed':observed,'observation_sources':[{k:c[k] for k in ('capture_id','source','metadata')} for c in captures],
        'observation_conflicts':conflicts,'user_inputs':user or {},
        'declared_context':{k:v for k,v in base.items() if preset.fact_kinds[k]=='declared'} if preset else {},
        'assumptions':{k:v for k,v in base.items() if preset.fact_kinds[k]=='assumption'} if preset else {},
        'effective_context_inputs':merged,
        'policy_requirements':[r.model_dump(mode='json') for p in policies for r in p.rules]}
    return snapshot,merged,tuple(rules)
