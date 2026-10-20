/* Verdict visuals: overall status, rule/field share bars, attention list and the selected field's bit map.
   Status colours always travel with an icon and a label; text stays in ink colours. */
const STATUS={FAIL:{color:'#d03b3b',icon:'✕',name:'위반'},ERROR:{color:'#d03b3b',icon:'!',name:'입력 오류'},
 CONFLICT:{color:'#ec835a',icon:'⇄',name:'충돌'},UNKNOWN:{color:'#fab219',icon:'?',name:'판단 불가'},
 REVIEW:{color:'#8a94a6',icon:'…',name:'검토 대상'},PASS:{color:'#0ca30c',icon:'✓',name:'만족'},'N/A':{color:'#c9ced8',icon:'–',name:'적용 안 됨'}};
const STATUS_ORDER=['FAIL','ERROR','CONFLICT','UNKNOWN','REVIEW','PASS','N/A'];
const tip=document.createElement('div');tip.className='viz-tip';tip.hidden=true;document.body.append(tip);
function node(tag,cls,text){const n=document.createElement(tag);if(cls)n.className=cls;if(text!=null)n.textContent=text;return n;}
function hoverTip(target,text){target.onmousemove=e=>{tip.textContent=text;tip.hidden=false;
 tip.style.left=Math.min(e.clientX+14,innerWidth-tip.offsetWidth-8)+'px';tip.style.top=(e.clientY+14)+'px';};target.onmouseleave=()=>tip.hidden=true;}
function chip(status){const s=STATUS[status]||STATUS.UNKNOWN;const c=node('span','viz-chip');const dot=node('span','viz-dot',s.icon);dot.style.background=s.color;
 c.append(dot,document.createTextNode(`${status} ${s.name}`));return c;}
function shareBar(title,counts,note){
 const box=node('div','viz-bar-box');const total=Object.values(counts).reduce((a,b)=>a+b,0);
 box.append(node('div','viz-bar-title',`${title} ${total}개`+(note?` · ${note}`:'')));
 const bar=node('div','viz-bar');bar.setAttribute('role','img');
 bar.setAttribute('aria-label',title+': '+STATUS_ORDER.filter(s=>counts[s]).map(s=>`${s} ${counts[s]}`).join(', '));
 const legend=node('div','viz-legend');
 for(const s of STATUS_ORDER){const n=counts[s]||0;if(!n)continue;
  const seg=node('span','viz-seg');seg.style.flexGrow=n;seg.style.background=STATUS[s].color;
  hoverTip(seg,`${s} ${STATUS[s].name}: ${n}개 (${(100*n/total).toFixed(1)}%)`);bar.append(seg);
  const item=chip(s);item.append(document.createTextNode(` ${n}`));legend.append(item);}
 if(!total)bar.append(node('span','viz-empty','결과 없음'));
 box.append(bar,legend);return box;}
function tally(items){const out={};for(const i of items)out[i.status]=(out[i.status]||0)+1;return out;}
function openRuleField(ruleId){
 const row=(report?.fields||[]).find(f=>(f.rule_results||[]).some(r=>r.rule.rule_id===ruleId));
 if(!row){el('reason').textContent=`${ruleId}: 이 규칙의 대상 필드가 입력에 없습니다.`;return;}
 el('search').value='';rows();show(row);el('detailtitle').scrollIntoView({behavior:'smooth',block:'start'});}
function renderVerdictVisuals(r){
 const box=el('verdictviz');box.replaceChildren();const v=r.validation;if(!v)return;
 const results=v.results||[];const applied=results.filter(x=>x.status!=='N/A');
 const hero=node('div','viz-hero');const s=STATUS[v.status]||STATUS.UNKNOWN;const mark=node('span','viz-hero-mark',s.icon);mark.style.background=s.color;
 const failing=applied.filter(x=>['FAIL','ERROR','CONFLICT'].includes(x.status)).length;
 hero.append(mark,node('strong',null,`${v.status} ${s.name}`),node('span','muted',
  failing?`문제 규칙 ${failing}개 · 적용 규칙 ${applied.length}개 중`:`적용 규칙 ${applied.length}개`+(r.validation_scope==='experimental_unreviewed_rules'?' · 검토 전 규칙 판정':'')));
 box.append(hero,shareBar('적용된 규칙',tally(applied),`적용 조건 불충족(N/A) ${results.length-applied.length}개 제외`),shareBar('필드',tally(r.fields||[])));
 const attention=applied.filter(x=>x.status!=='PASS').sort((a,b)=>STATUS_ORDER.indexOf(a.status)-STATUS_ORDER.indexOf(b.status));
 if(!attention.length)return;
 const table=node('table','viz-attention');table.append(node('caption',null,'확인이 필요한 규칙 — 행을 누르면 해당 필드로 이동'));
 const head=node('tr');for(const h of ['판정','제약','대상 필드','근거'])head.append(node('th',null,h));table.append(head);
 for(const x of attention){const tr=node('tr');const st=node('td');st.append(chip(x.status));
  const t=x.rule.target;tr.append(st,node('td',null,constraint(x.rule)),node('td',null,t.field_id.split('.').slice(1).join('.')+(t.index==null?'':`[${t.index}]`)+(t.bit==null?'':` bit ${t.bit}`)),
   node('td','muted',`${x.rule.provenance.source_document} · ${x.rule.provenance.source_section}`));
  tr.title=x.reason;tr.onclick=()=>openRuleField(x.rule.rule_id);table.append(tr);}
 box.append(table);}
function ruleBits(row){
 const marks={};
 for(const result of row.rule_results||[]){const rule=result.rule,c=rule.check;let bits=[];
  if(rule.target.bit!=null)bits=[rule.target.bit];else if(c.type==='MASK')for(let b=0;b<64;b++){if(Number(BigInt(c.mask)>>BigInt(b)&1n))bits.push(b);}
  for(const b of bits){const prior=marks[b];if(!prior||STATUS_ORDER.indexOf(result.status)<STATUS_ORDER.indexOf(prior.status))marks[b]={status:result.status,rule:rule.rule_id};}}
 return marks;}
function renderBitMap(row){
 const box=el('bitmap');box.replaceChildren();const def=(row.definitions||[]).find(d=>d.byte_length);
 if(!def)return;const width=def.byte_length*8;
 const head=node('p','muted',`바이트 ${def.byte_offset}${def.byte_length>1?`–${def.byte_offset+def.byte_length-1}`:''} · ${def.byte_length}바이트 · ${def.document_id}`);box.append(head);
 if(typeof row.value!=='number'&&typeof row.value!=='bigint'||width>64){box.append(node('p','muted',width>64?'64비트를 넘는 필드는 비트 지도를 생략합니다.':'숫자가 아닌 값은 비트 지도를 생략합니다.'));return;}
 const value=BigInt(row.value);const bit=b=>Number(value>>BigInt(b)&1n);const marks=ruleBits(row);
 const owner={};for(const f of def.bit_fields||[])for(let b=f.lsb;b<=f.msb;b++)owner[b]=f;
 const grid=node('div','viz-bits');grid.setAttribute('role','img');grid.setAttribute('aria-label',`${row.field} 비트 지도, 값 ${row.raw_value}`);
 for(let byte=def.byte_length-1;byte>=0;byte--){const line=node('div','viz-byte');line.append(node('span','viz-byte-label',`+${byte}`));
  for(let b=byte*8+7;b>=byte*8;b--){const f=owner[b];const cell=node('span','viz-bit'+(bit(b)?' on':'')+(f?.state==='reserved'?' reserved':'')+(f?'':' undefined'));
   cell.append(node('small',null,b),node('b',null,bit(b)));const m=marks[b];
   if(m){cell.style.outlineColor=STATUS[m.status].color;cell.classList.add('ruled');cell.append(node('i',null,STATUS[m.status].icon));}
   const anchor=f?.evidence?.[0];hoverTip(cell,`bit ${b} = ${bit(b)} · ${f?f.name:'정의 정보 없음'}`+(anchor?` · ${anchor.document_id} p.${anchor.pdf_page}`:'')+(m?` · ${m.rule} ${m.status}`:''));
   line.append(cell);}
  grid.append(line);}
 box.append(grid);
 if(!(def.bit_fields||[]).length){box.append(node('p','muted','이 필드는 비트 단위 정의 없이 값 전체로 해석합니다.'));return;}
 const table=node('table','viz-bitlist');const header=node('tr');for(const h of ['비트','정의','값','규칙'])header.append(node('th',null,h));table.append(header);
 for(const f of [...def.bit_fields].sort((a,b)=>b.msb-a.msb)){const raw=(value>>BigInt(f.lsb))&((1n<<BigInt(f.msb-f.lsb+1))-1n);
  const tr=node('tr',f.state==='reserved'?'muted':null);const rule=node('td');
  const hit=Object.entries(marks).filter(([b])=>b>=f.lsb&&b<=f.msb).map(([,m])=>m);
  if(hit.length)rule.append(chip(hit.sort((a,b)=>STATUS_ORDER.indexOf(a.status)-STATUS_ORDER.indexOf(b.status))[0].status));
  tr.append(node('td',null,f.msb===f.lsb?`${f.lsb}`:`${f.msb}:${f.lsb}`),node('td',null,f.name),node('td',null,f.msb===f.lsb?String(raw):`${raw} (0x${raw.toString(16)})`),rule);table.append(tr);}
 box.append(table);}
