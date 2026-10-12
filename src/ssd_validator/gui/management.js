let knowledge = null, editingRule = null, managerGeneration = 0;
const renderOriginal=render;
render=function(r){renderOriginal(r);if(r.repository)el('identity').textContent+=` · DB r${r.repository.revision} · 검사 #${r.run_id}`;};
function downloadJSON(value, filename) {
  const url=URL.createObjectURL(new Blob([JSON.stringify(value,null,2)],{type:'application/json'}));
  const a=document.createElement('a');a.href=url;a.download=filename;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
function conditionLabel(c) {
  if(!c)return '항상 적용';
  if(c.op==='EQ')return `${c.ref.source==='context'?c.ref.path:c.ref.field.field_id} = ${JSON.stringify(c.value)}`;
  return `${c.op} (${(c.children||[]).map(conditionLabel).join(', ')||c.ref?.field?.field_id||c.ref?.path||''})`;
}
async function loadKnowledge(){
  const generation=++managerGeneration;el('ruleform').hidden=true;editingRule=null;
  try{const value=await api('/api/knowledge',{bundle_id:el('managebundle').value});if(generation!==managerGeneration)return;
    knowledge=value;el('manageerror').textContent='';el('dbrevision').textContent=`원본 DB 리비전 ${value.revision}`;
    el('managedrules').replaceChildren();el('rulefield').replaceChildren();el('exportrevision').replaceChildren();
    for(const f of value.fields){const o=document.createElement('option');o.value=f;o.textContent=f;el('rulefield').append(o);}
    for(const v of value.revisions){const o=document.createElement('option');o.value=v.id;o.textContent=`r${v.id} · ${v.reason}`;el('exportrevision').append(o);}
    for(const rule of value.rules){const tr=document.createElement('tr');
      for(const text of [`${rule.rule_id} / ${rule.target.field_id}${rule.target.bit==null?'':` bit ${rule.target.bit}`}`,
        `${conditionLabel(rule.condition)} / ${constraint(rule)}`,
        `${rule.provenance.source_type}: ${rule.provenance.source_document} ${rule.provenance.source_section} / ${rule.provenance.status}`]){
        const td=document.createElement('td');td.textContent=text;tr.append(td);}
      tr.onclick=()=>openRule(rule);el('managedrules').append(tr);}
  }catch(e){el('manageerror').textContent=e.message;}
}
function integer(value){if(!/^(?:-?\d+|0x[\da-f]+)$/i.test(value.trim()))throw Error('정수 또는 0x16진수를 입력하세요.');const n=Number(value);if(!Number.isSafeInteger(n))throw Error('정수가 너무 큽니다.');return n;}
function valueInput(value){if(/^(?:-?\d+|0x[\da-f]+)$/i.test(value.trim()))return integer(value);if(value==='true'||value==='false')return value==='true';if(!value.length)throw Error('값을 입력하세요.');return value;}
function makeInput(id,label,value=''){const l=document.createElement('label');l.style.display='inline-flex';l.style.marginRight='10px';l.textContent=label;const i=document.createElement('input');i.id=id;i.value=value;l.append(i);el('checkinputs').append(l);}
function checkInputs(c={}){
  el('checkinputs').replaceChildren();const type=el('checktype').value;
  if(['EXACT','MIN','MAX','MASK'].includes(type))makeInput('checkvalue','값',c.value??'');
  if(type==='MASK')makeInput('checkmask','마스크',c.mask??'');
  if(type==='RANGE'){makeInput('checkmin','최솟값',c.min??'');makeInput('checkmax','최댓값',c.max??'');}
  if(type==='ENUM')makeInput('checkvalues','허용값 JSON 배열',JSON.stringify(c.values||[]));
  if(['BIT_SET','BIT_CLEAR'].includes(type))makeInput('checkbit','검사 비트',c.bit??'');
  if(type==='CAPABILITY'){
    makeInput('capabilityid','Capability ID',c.capability_id||'');
    const l=document.createElement('label');l.style.display='inline-flex';l.textContent='요구';
    const s=document.createElement('select');s.id='capabilitysupport';for(const [key,label] of [['supported','지원 요구'],['unsupported','미지원 요구']]){const o=document.createElement('option');o.value=key;o.textContent=label;s.append(o);}s.value=c.support||'supported';l.append(s);el('checkinputs').append(l);
  }
  if(type==='FIELD_COMPARE'){
    const l=document.createElement('label');l.style.display='inline-flex';l.textContent='비교';const s=document.createElement('select');s.id='compareoperator';for(const op of ['=','!=','<','<=','>','>=']){const o=document.createElement('option');o.value=op;o.textContent=op;s.append(o);}s.value=c.operator||'<=';l.append(s);el('checkinputs').append(l);
    makeInput('comparefield','상대 필드',c.other?.field_id||'');makeInput('compareindex','상대 배열 인덱스',c.other?.index??'');makeInput('comparebit','상대 비트',c.other?.bit??'');}
}
function openRule(rule){
  editingRule=rule?structuredClone(rule):null;el('ruleform').reset();el('ruleform').hidden=false;
  el('ruleid').value=rule?.rule_id||'';el('rulefield').value=rule?.target.field_id||knowledge.fields[0];
  el('rulebit').value=rule?.target.bit??'';el('ruleindex').value=rule?.target.index??'';
  el('checktype').value=rule?.check.type||'EXACT';checkInputs(rule?.check);
  el('modality').value=rule?.modality||'mandatory';el('conditionmode').value=rule?'keep':'none';
  el('conditionjson').value=JSON.stringify(rule?.condition||null,null,2);
  el('sourcetype').value=rule?.provenance.source_type||'spec';
  for(const [id,key] of [['sourcedocument','source_document'],['sourceversion','source_version'],['sourcesection','source_section']])el(id).value=rule?.provenance[key]||'';
  el('reviewstatus').value=rule?.provenance.status==='provisional'?'provisional':'candidate';el('deleterule').disabled=!rule;
}
function optionalInt(id){return el(id).value===''?null:integer(el(id).value);}
function readCheck(){
  const type=el('checktype').value,c={type};
  if(['EXACT','MIN','MAX','MASK'].includes(type))c.value=type==='EXACT'?valueInput(el('checkvalue').value):integer(el('checkvalue').value);
  if(type==='MASK')c.mask=integer(el('checkmask').value);
  if(type==='RANGE'){c.min=integer(el('checkmin').value);c.max=integer(el('checkmax').value);}
  if(type==='ENUM')c.values=JSON.parse(el('checkvalues').value);
  if(['BIT_SET','BIT_CLEAR'].includes(type))c.bit=optionalInt('checkbit');
  if(type==='CAPABILITY'){c.capability_id=el('capabilityid').value;c.support=el('capabilitysupport').value;}
  if(type==='FIELD_COMPARE'){c.operator=el('compareoperator').value;c.other={field_id:el('comparefield').value,index:optionalInt('compareindex'),bit:optionalInt('comparebit')};}
  return c;
}
async function saveRule(deleting=false){
  if(!knowledge)return;el('manageerror').textContent='';
  try{if(!el('changereason').value.trim())throw Error('변경 사유를 입력하세요.');
    const rule=editingRule?structuredClone(editingRule):{};
    if(!deleting){rule.rule_id=el('ruleid').value;rule.target={field_id:el('rulefield').value,bit:optionalInt('rulebit'),index:optionalInt('ruleindex')};rule.check=readCheck();rule.modality=el('modality').value;
      const mode=el('conditionmode').value;
      if(mode==='none')rule.condition=null;
      if(mode==='true'||mode==='false')rule.condition={op:'EQ',ref:{source:'context',path:'logical_block_atomic_parameters_applicable'},value:mode==='true'};
      if(mode==='advanced')rule.condition=JSON.parse(el('conditionjson').value);
      rule.provenance={source_type:el('sourcetype').value,source_document:el('sourcedocument').value,source_version:el('sourceversion').value,source_section:el('sourcesection').value,status:el('reviewstatus').value};
    }
    await api('/api/rule',{bundle_id:knowledge.bundle.bundle_id,expected_revision:knowledge.revision,
      reason:el('changereason').value,original_rule_id:editingRule?.rule_id||null,delete:deleting,rule:deleting?null:rule});
    await loadKnowledge();if(input)await analyze();
  }catch(e){el('manageerror').textContent=e.message;}
}
async function exportSources(revision){try{downloadJSON(await api('/api/sources/export',revision?{revision}:{}),`knowledge-r${revision||knowledge?.revision||'latest'}.json`);}catch(e){el('manageerror').textContent=e.message;}}
async function loadHistory(){try{const value=await api('/api/history',{});el('historyerror').textContent='';el('historyrows').replaceChildren();
  for(const item of value.runs){const tr=document.createElement('tr');for(const text of [`#${item.id} / ${item.created_at}`,item.filename,`r${item.revision} / ${item.status||'후보 검토'}`]){const td=document.createElement('td');td.textContent=text;tr.append(td);}
    const td=document.createElement('td');for(const [label,path] of [['결과 열기','/api/run'],['동일 조건 재실행','/api/replay']]){const b=document.createElement('button');b.textContent=label;b.onclick=async()=>{try{++requestGeneration;input=null;const r=await api(path,{run_id:item.id});render(r.report);el('bundle').value=r.report.bundle.bundle_id;el('experimental').checked=!!r.report.validation;
      if(r.report.validation){el('policy').value=r.report.validation.selection.policy_mode;el('atomic').value=JSON.stringify(r.report.validation.selection.context.facts.logical_block_atomic_parameters_applicable??null);}
      if(path==='/api/replay')await loadHistory();}catch(e){el('historyerror').textContent=e.message;}};td.append(b);}tr.append(td);el('historyrows').append(tr);}
  }catch(e){el('historyerror').textContent=e.message;}}
el('management').ontoggle=()=>{if(el('management').open)loadKnowledge();};
el('historypanel').ontoggle=()=>{if(el('historypanel').open)loadHistory();};
el('loadknowledge').onclick=loadKnowledge;el('managebundle').onchange=loadKnowledge;el('newrule').onclick=()=>{if(knowledge)openRule(null);};
el('checktype').onchange=()=>checkInputs();el('ruleform').onsubmit=e=>{e.preventDefault();saveRule();};
el('deleterule').onclick=()=>saveRule(true);el('canceledit').onclick=()=>el('ruleform').hidden=true;
el('sourceexport').onclick=()=>exportSources();el('oldexport').onclick=()=>exportSources(Number(el('exportrevision').value));
el('sourceimport').onclick=async()=>{try{if(!knowledge)throw Error('목록을 먼저 불러오세요.');const file=el('sourceimportfile').files[0];if(!file)throw Error('원본 패키지를 선택하세요.');if(file.size>32*1024*1024)throw Error('원본 패키지는 32 MiB 이하여야 합니다.');
  const packageValue=JSON.parse(await file.text());await api('/api/sources/import',{package:packageValue,expected_revision:knowledge.revision,reason:el('importreason').value});await loadKnowledge();if(input)await analyze();
  }catch(e){el('manageerror').textContent=e.message;}};
el('loadhistory').onclick=loadHistory;
let databaseStatus=null;
async function refreshDatabaseStatus(){try{databaseStatus=await api('/api/database/status',{});el('dbstatus').textContent=`스키마 v${databaseStatus.schema_version} · 원본 r${databaseStatus.revision} · 보존 리비전 ${databaseStatus.revisions}개 · 검사 ${databaseStatus.runs}개`;el('dberror').textContent='';}catch(e){el('dberror').textContent=e.message;}}
el('databasepanel').ontoggle=()=>{if(el('databasepanel').open)refreshDatabaseStatus();};
el('dbstatusrefresh').onclick=refreshDatabaseStatus;
el('dbbackup').onclick=async()=>{try{const b=await api('/api/database/backup',{});const raw=Uint8Array.from(atob(b.content_base64),c=>c.charCodeAt(0));const url=URL.createObjectURL(new Blob([raw],{type:'application/octet-stream'}));const a=document.createElement('a');a.href=url;a.download=b.filename;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);el('dberror').textContent=`백업 ${b.bytes} bytes · SHA256 ${b.sha256}`;}catch(e){el('dberror').textContent=e.message;}};
el('dbrestore').onclick=async()=>{try{if(!databaseStatus)throw Error('상태를 먼저 불러오세요.');const file=el('dbrestorefile').files[0];if(!file)throw Error('DB 백업을 선택하세요.');if(file.size>64*1024*1024)throw Error('DB 백업은 64 MiB 이하여야 합니다.');const reader=new FileReader();reader.onload=async()=>{try{const result=await api('/api/database/restore',{content_base64:reader.result.split(',')[1],expected_revision:databaseStatus.revision});++requestGeneration;input=null;clear();knowledge=null;editingRule=null;el('ruleform').hidden=true;await refreshDatabaseStatus();await loadKnowledge();await loadHistory();el('dberror').textContent=`복원 완료 · 복원 전 백업: ${result.pre_restore_backup}`;}catch(e){el('dberror').textContent=e.message;}};reader.onerror=()=>el('dberror').textContent='백업 파일을 읽지 못했습니다.';reader.readAsDataURL(file);}catch(e){el('dberror').textContent=e.message;}};
