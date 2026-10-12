let registry=null, entityItems=[], selectedEntity=null, pendingChange=null, entityGeneration=0, entityKnowledge=null,entityRevision=null;
function options(element,items,selected){element.replaceChildren();for(const item of items){const o=document.createElement('option');o.value=item.value??item;o.textContent=item.label??item;element.append(o);}if([...element.options].some(o=>o.value===selected))element.value=selected;}
async function refreshRegistry(){
  registry=await api('/api/bundles',{});
  const choices=registry.bundles.map(b=>({value:b.bundle_id,label:`Base ${b.base_revision} + NVM ${b.nvm_revision} · ${b.bundle_id}`}));
  for(const id of ['bundle','managebundle','entitybundle'])options(el(id),choices,el(id).value);
  const history=await api('/api/history',{});
  options(el('revertrevision'),history.revisions.map(r=>({value:String(r.id),label:`r${r.id}: ${r.reason}`})),el('revertrevision').value);
}
function reviewInput(prefix){
  const reviewer=el(prefix+'reviewer').value.trim(),reviewed_date=el(prefix+'reviewdate').value,basis=el(prefix+'reviewbasis').value.trim();
  if(!reviewer&&!reviewed_date&&!basis)return null;
  if(!reviewer||!reviewed_date||!basis)throw Error('검토자·검토일·근거를 모두 입력하세요.');
  return {reviewer,reviewed_date,basis};
}
async function showPreview(request){
  pendingChange=null;el('previewcommit').disabled=true;el('previewerror').textContent='';
  const value=await api(request.target_revision?'/api/revision/preview':'/api/entity/preview',request);
  pendingChange={...request,preview_hash:value.preview_hash};el('changepreview').hidden=false;
  el('previewsummary').textContent=`r${value.revision} 기준 · 변경 ${value.changes.length}개 · 저장 후 새 리비전 생성`;
  el('previewrows').replaceChildren();
  function diff(a,b,path=''){
    if(JSON.stringify(a)===JSON.stringify(b))return [];
    if(a&&b&&typeof a==='object'&&typeof b==='object')return [...new Set([...Object.keys(a),...Object.keys(b)])].flatMap(key=>diff(a[key],b[key],path?path+'.'+key:key));
    return [{path,before:a,after:b}];
  }
  function text(value){return value===undefined?'없음':value===null?'미지정':typeof value==='object'?JSON.stringify(value):String(value);}
  for(const item of value.changes){
    const changes=diff(item.before?.payload,item.after?.payload);
    if(JSON.stringify(item.before?.reviews)!==JSON.stringify(item.after?.reviews))changes.push({path:'검토 기록',before:item.before?.reviews?.map(r=>r.reviewer+': '+r.basis).join(' / '),after:item.after?.reviews?.map(r=>r.reviewer+': '+r.basis).join(' / ')});
    for(const change of changes){const tr=document.createElement('tr');for(const v of [`${item.kind} / ${item.entity_id} / ${change.path}`,text(change.before),text(change.after)]){const td=document.createElement('td');td.textContent=v;tr.append(td);}el('previewrows').append(tr);}}
  el('previewcommit').disabled=false;el('changepreview').scrollIntoView({behavior:'smooth',block:'start'});
}
el('previewcommit').onclick=async()=>{if(!pendingChange)return;el('previewcommit').disabled=true;try{
  await api(pendingChange.target_revision?'/api/revision/revert':'/api/entity/save',pendingChange);
  pendingChange=null;el('changepreview').hidden=true;el('entityform').hidden=true;el('ruleform').hidden=true;
  await refreshRegistry();await loadKnowledge();await loadEntities();await loadHistory();if(input)await analyze();
  }catch(e){el('previewerror').textContent=e.message;el('previewcommit').disabled=false;}};
el('previewcancel').onclick=()=>{pendingChange=null;el('changepreview').hidden=true;};
el('revertpreview').onclick=async()=>{try{await showPreview({expected_revision:registry.revision,
  target_revision:Number(el('revertrevision').value),reason:el('revertreason').value});}catch(e){el('entityerror').textContent=e.message;}};
async function loadEntities(){
  const generation=++entityGeneration;selectedEntity=null;el('entityform').hidden=true;
  el('entityrows').replaceChildren();
  try{const kind=el('entitykind').value;const value=await api('/api/entities',{kind,bundle_id:kind==='document'? '':kind==='bundle'?null:el('entitybundle').value,search:el('entitysearch').value});
    if(['field','capability'].includes(kind))entityKnowledge=await api('/api/knowledge',{bundle_id:el('entitybundle').value});
    if(generation!==entityGeneration)return;entityRevision=value.revision;entityItems=value.items;el('entitystatus').textContent=`원본 r${value.revision} · ${value.items.length}개`;el('entityerror').textContent='';el('entityrows').replaceChildren();
    for(const item of value.items){const p=item.payload,tr=document.createElement('tr');
      const detail=item.kind==='field'?`${p.schema.name} · ${p.schema.offset}+${p.schema.length} bytes · CNS ${p.binding.cns}, CSI ${p.binding.csi} · 배열 ${p.binding.array_count??'없음'}`:
        item.kind==='capability'?`${p.target.field_id} bit ${p.target.bit??'전체'} · 지원 ${p.supported} / 미지원 ${p.unsupported}`:
        item.kind==='bundle'?`${p.base_document} + ${p.nvm_document}`:`${p.source_type} · ${p.source_version} · ${p.filename||p.title||''}`;
      for(const text of [item.entity_id,detail,item.reviews.length?item.reviews.map(r=>`${r.reviewer} ${r.reviewed_date}: ${r.basis}`).join(' / '):'현재 내용의 검토 기록 없음']){const td=document.createElement('td');td.textContent=text;tr.append(td);}tr.onclick=()=>openEntity(item);el('entityrows').append(tr);}
  }catch(e){el('entityerror').textContent=e.message;}
}
function control(id,label,value='',choices=null,required=false){
  const l=document.createElement('label');l.textContent=label;const i=document.createElement(choices?'select':'input');i.id='e_'+id;
  if(choices)options(i,choices,String(value??''));else i.value=value??'';i.required=required;l.append(i);el('entityinputs').append(l);return i;
}
function val(id){return el('e_'+id).value;}
function number(id){return integer(val(id));}
function nullableNumber(id){return val(id)===''?null:number(id);}
function typedControls(id,label,value){control(id,label,value??'');control(id+'type','값 타입',typeof value==='boolean'?'boolean':typeof value==='string'?'string':'integer',['integer','string','boolean']);}
function typed(id){const type=val(id+'type');if(type==='integer')return number(id);if(type==='boolean'){if(!['true','false'].includes(val(id)))throw Error('bool 값은 true/false입니다.');return val(id)==='true';}return val(id);}
function docOptions(){return registry.documents.map(d=>({value:d.document_id||d.source_document,label:`${d.document_id||d.source_document} (${d.source_version})`}));}
function openEntity(item){
  selectedEntity=item;const kind=el('entitykind').value,p=item?.payload||{};
  el('entityform').reset();el('entityform').hidden=false;el('entityinputs').replaceChildren();el('bitrows').replaceChildren();el('anchorrows').replaceChildren();
  el('entitytitle').textContent=`${kind} ${item?'편집':'추가'}`;el('entitydelete').disabled=!item;el('bitadd').hidden=kind!=='field';el('anchoradd').hidden=kind!=='field';
  if(kind==='field'){
    const s=p.schema||{},b=p.binding||{};
    for(const [id,label] of [['field_id','필드 ID'],['name','이름'],['command','응답 명령'],['offset','byte offset'],['length','요소 byte 길이']])control(id,label,s[id],null,true);
    control('endian','Endian',s.endian||'little',['little','big','not_applicable']);control('value_type','자료형',s.value_type||'integer',['integer','bitmask','string','bytes']);
    control('state','의미 상태',s.state||'',['','defined','reserved']);control('zero','명시적 zero 제약',s.validation?'yes':'no',[{value:'no',label:'없음'},{value:'yes',label:'must_be_zero (명시적 요구)'}]);
    for(const [id,label] of [['cns','CNS'],['csi','CSI'],['response_size','응답 byte 크기'],['array_count','배열 개수'],['array_stride','배열 stride bytes']])control(id,label,b[id],null,['cns','csi','response_size'].includes(id));
    for(const bit of s.bits||[])addBit(bit);
    for(const anchor of p.evidence?.evidence||[])addAnchor(anchor);if(!p.evidence?.evidence?.length)addAnchor();
  }else if(kind==='capability'){
    control('capability_id','Capability ID',p.capability_id,null,true);control('target','대상 필드',p.target?.field_id,entityKnowledge?.fields||[]);
    control('bit','비트',p.target?.bit);control('index','배열 인덱스',p.target?.index);typedControls('supported','지원 값',p.supported);typedControls('unsupported','미지원 값',p.unsupported);
    provenanceControls(p.provenance);
  }else if(kind==='document'){
    const pinned=p.catalog_document;control('pinned','문서 종류',pinned?'pinned':'source',[{value:'source',label:'규격/정책 출처 등록'},{value:'pinned',label:'PDF 추출 원문 등록'}]).disabled=!!item;
    for(const [id,label] of [['document_id','문서 ID'],['source_version','버전'],['filename','파일 이름'],['title','설명']])control(id,label,p[id]??(id==='document_id'?p.source_document:''),null,['document_id','source_version'].includes(id));
    control('source_type','출처 종류',p.source_type||'spec',['spec','policy','fixture']);
    if(pinned){for(const key of ['component','sha256','pages','inherits'])control(key,key,p[key]);for(const key of ['document_id','source_version','component','sha256','pages','inherits'])el('e_'+key).disabled=true;}
  }else if(kind==='bundle'){
    control('bundle_id','Bundle ID',p.bundle_id,null,true);if(item)el('e_bundle_id').disabled=true;
    const template=control('template_bundle','명시적 복제 원본',item?item.bundle_id:el('entitybundle').value,registry.bundles.map(b=>b.bundle_id));template.disabled=!!item;
    control('base_document','Base 문서',p.base_document,registry.documents.filter(d=>d.component==='NVME_BASE').map(d=>d.document_id));
    control('nvm_document','NVM 문서',p.nvm_document,registry.documents.filter(d=>d.component==='NVME_NVM').map(d=>d.document_id));
    control('structure_ids','Structure IDs (쉼표 구분)',(p.structure_ids||[]).join(','),null,true);
    const selectTemplate=()=>{const b=registry.bundles.find(b=>b.bundle_id===template.value);if(b){el('e_base_document').value=b.base_document;el('e_nvm_document').value=b.nvm_document;el('e_structure_ids').value=b.structure_ids.join(',');}};
    template.onchange=selectTemplate;if(!item)selectTemplate();
  }
}
function provenanceControls(p={}){
  control('source_type','출처 종류',p.source_type||'spec',['spec','policy','fixture']);control('source_document','출처 문서',p.source_document,docOptions());control('source_version','출처 버전',p.source_version,null,true);control('source_section','절 / 근거',p.source_section,null,true);
  control('status','지식 상태',p.status||'candidate',['candidate','provisional','confirmed']);
}
function addBit(bit={}){
  const row=document.createElement('div');row.className='toolbar bitrow';row.style.marginTop='12px';
  for(const [key,label,choices] of [['bit','비트 번호',null],['state','상태',['defined','reserved']],['feature','Feature ID (선택)',null],['zero','명시적 zero',['no','yes']]]){
    const l=document.createElement('label');l.textContent=label;const i=document.createElement(choices?'select':'input');i.dataset.key=key;if(choices)options(i,choices,key==='zero'?(bit.validation?'yes':'no'):bit[key]||'defined');else i.value=bit[key]??'';l.append(i);row.append(l);}
  const remove=document.createElement('button');remove.type='button';remove.textContent='비트 삭제';remove.onclick=()=>row.remove();row.append(remove);el('bitrows').append(row);
}
function addAnchor(anchor={}){
  const row=document.createElement('div');row.className='toolbar anchorrow';row.style.marginTop='12px';
  for(const [key,label] of [['document_id','문서'],['section','절'],['figure','Figure (선택)'],['pdf_page','PDF 페이지'],['printed_page','인쇄 페이지 (선택)']]){
    const l=document.createElement('label');l.textContent=label;const i=document.createElement(key==='document_id'?'select':'input');i.dataset.key=key;if(key==='document_id')options(i,docOptions(),anchor[key]);else i.value=anchor[key]??'';l.append(i);row.append(l);}
  const remove=document.createElement('button');remove.type='button';remove.textContent='근거 삭제';remove.onclick=()=>row.remove();row.append(remove);el('anchorrows').append(row);
}
function rowValues(row){return Object.fromEntries([...row.querySelectorAll('[data-key]')].map(i=>[i.dataset.key,i.value]));}
function readEntity(){
  const kind=el('entitykind').value,p=structuredClone(selectedEntity?.payload||{});
  if(kind==='field'){
    const schema={...(p.schema||{}),field_id:val('field_id'),name:val('name'),command:val('command'),offset:number('offset'),length:number('length'),endian:val('endian'),value_type:val('value_type'),state:val('state')||null};
    delete schema.validation;if(val('zero')==='yes')schema.validation={behavior:'must_be_zero'};
    schema.bits=[...el('bitrows').children].map(row=>{const v=rowValues(row);return {bit:integer(v.bit),state:v.state,...(v.feature?{feature:v.feature}:{}),...(v.zero==='yes'?{validation:{behavior:'must_be_zero'}}:{})};});
    const binding={cns:number('cns'),csi:number('csi'),response_size:number('response_size'),array_count:nullableNumber('array_count'),array_stride:nullableNumber('array_stride')};
    const anchors=[...el('anchorrows').children].map(row=>{const v=rowValues(row);return {document_id:v.document_id,section:v.section,pdf_page:integer(v.pdf_page),figure:v.figure||null,printed_page:v.printed_page||null};});
    return {schema,binding,evidence:{...(p.evidence||{}),evidence:anchors}};
  }
  if(kind==='capability')return {capability_id:val('capability_id'),target:{field_id:val('target'),bit:nullableNumber('bit'),index:nullableNumber('index')},supported:typed('supported'),unsupported:typed('unsupported'),provenance:readProvenance()};
  if(kind==='bundle')return {bundle_id:val('bundle_id'),base_document:val('base_document'),nvm_document:val('nvm_document'),structure_ids:val('structure_ids').split(',').map(s=>s.trim()).filter(Boolean),template_bundle:val('template_bundle')};
  if(val('pinned')==='pinned')return {...p,document_id:val('document_id'),filename:val('filename')};
  return {source_type:val('source_type'),source_document:val('document_id'),source_version:val('source_version'),filename:val('filename'),title:val('title')};
}
function readProvenance(){const p={source_type:val('source_type'),source_document:val('source_document'),source_version:val('source_version'),source_section:val('source_section'),status:val('status')};if(p.status==='confirmed'){const r=reviewInput('entity');if(!r)throw Error('confirmed에는 검토 근거가 필요합니다.');p.verified_by=r.reviewer;p.verified_date=r.reviewed_date;}return p;}
async function previewEntity(deleting){try{const kind=el('entitykind').value;
  await showPreview({kind,bundle_id:kind==='document'?'':kind==='bundle'?(selectedEntity?.bundle_id||''):el('entitybundle').value,
    original_id:selectedEntity?.entity_id||null,expected_revision:entityRevision,reason:el('entityreason').value,
    payload:deleting?null:readEntity(),delete:deleting,review:deleting?null:reviewInput('entity')});
  }catch(e){el('entityerror').textContent=e.message;}}
el('entityform').onsubmit=e=>{e.preventDefault();previewEntity(false);};el('entitydelete').onclick=()=>previewEntity(true);
el('entitycancel').onclick=()=>el('entityform').hidden=true;el('bitadd').onclick=()=>addBit();el('anchoradd').onclick=()=>addAnchor();
el('entitynew').onclick=()=>openEntity(null);el('entityrefresh').onclick=loadEntities;el('entitykind').onchange=loadEntities;el('entitybundle').onchange=loadEntities;
el('entitysearch').oninput=loadEntities;el('entitypanel').ontoggle=async()=>{if(el('entitypanel').open){try{await refreshRegistry();await loadKnowledge();await loadEntities();}catch(e){el('entityerror').textContent=e.message;}}};
el('revisionpanel').ontoggle=async()=>{if(el('revisionpanel').open){try{await refreshRegistry();}catch(e){el('entityerror').textContent=e.message;}}};
const openRuleOriginal=openRule;
openRule=function(rule){openRuleOriginal(rule);options(el('conditionfield'),knowledge.fields,rule?.condition?.ref?.field?.field_id);
  if(rule?.condition&&['EQ','GE','BIT_SET','BIT_CLEAR'].includes(rule.condition.op)){const c=rule.condition;el('conditionmode').value='leaf';el('conditionop').value=c.op;el('conditionsource').value=c.ref.source;el('conditionpath').value=c.ref.path||'';el('conditionindex').value=c.ref.field?.index??'';el('conditiontargetbit').value=c.ref.field?.bit??'';el('conditionvalue').value=c.value??'';el('conditionvaluetype').value=typeof c.value==='boolean'?'boolean':typeof c.value==='string'?'string':'integer';el('conditionbit').value=c.bit??'';}
  el('simplecondition').hidden=el('conditionmode').value!=='leaf';};
el('conditionmode').onchange=()=>el('simplecondition').hidden=el('conditionmode').value!=='leaf';
function conditionFromForm(){const op=el('conditionop').value,source=el('conditionsource').value;
  const ref=source==='context'?{source,path:el('conditionpath').value}:{source,field:{field_id:el('conditionfield').value,index:optionalInt('conditionindex'),bit:optionalInt('conditiontargetbit')}};
  if(op==='BIT_SET'||op==='BIT_CLEAR')return {op,ref,bit:integer(el('conditionbit').value)};
  const raw=el('conditionvalue').value,type=el('conditionvaluetype').value;
  const value=type==='integer'?integer(raw):type==='string'?raw:raw==='true'?true:raw==='false'?false:(()=>{throw Error('bool 값은 true/false입니다.');})();return {op,ref,value};
}
saveRule=async function(deleting=false){if(!knowledge)return;try{
  const rule=editingRule?structuredClone(editingRule):{};
  if(!deleting){rule.rule_id=el('ruleid').value;rule.target={field_id:el('rulefield').value,bit:optionalInt('rulebit'),index:optionalInt('ruleindex')};rule.check=readCheck();rule.modality=el('modality').value;
    const mode=el('conditionmode').value;if(mode==='none')rule.condition=null;if(mode==='leaf')rule.condition=conditionFromForm();
    if(mode==='true'||mode==='false')rule.condition={op:'EQ',ref:{source:'context',path:'logical_block_atomic_parameters_applicable'},value:mode==='true'};
    if(mode==='advanced')rule.condition=JSON.parse(el('conditionjson').value);
    rule.provenance={source_type:el('sourcetype').value,source_document:el('sourcedocument').value,source_version:el('sourceversion').value,source_section:el('sourcesection').value,status:el('reviewstatus').value};
    if(rule.provenance.status==='confirmed'){const review=reviewInput('rule');if(!review)throw Error('confirmed에는 검토 근거가 필요합니다.');rule.provenance.verified_by=review.reviewer;rule.provenance.verified_date=review.reviewed_date;}
  }
  await showPreview({kind:'rule',bundle_id:knowledge.bundle.bundle_id,expected_revision:knowledge.revision,reason:el('changereason').value,
    original_id:editingRule?.rule_id||null,payload:deleting?null:rule,delete:deleting,review:deleting?null:reviewInput('rule')});
  }catch(e){el('manageerror').textContent=e.message;}};
const confirmed=document.createElement('option');confirmed.value='confirmed';confirmed.textContent='confirmed (검토 근거 필요)';el('reviewstatus').append(confirmed);
const checkInputsOriginal=checkInputs;
checkInputs=function(c={}){checkInputsOriginal(c);if(el('checktype').value==='EXACT'){
  const l=document.createElement('label');l.textContent='기대값 타입';const s=document.createElement('select');s.id='checkvaluetype';options(s,['integer','string','boolean'],typeof c.value==='string'?'string':typeof c.value==='boolean'?'boolean':'integer');l.append(s);el('checkinputs').append(l);}};
el('checktype').onchange=()=>checkInputs();
const readCheckOriginal=readCheck;
readCheck=function(){if(el('checktype').value==='EXACT'){
  const raw=el('checkvalue').value,type=el('checkvaluetype').value;
  return {type:'EXACT',value:type==='integer'?integer(raw):type==='string'?raw:raw==='true'?true:raw==='false'?false:(()=>{throw Error('bool 값은 true/false입니다.');})()};
}return readCheckOriginal();};
refreshRegistry().catch(e=>{el('error').textContent=e.message;});
