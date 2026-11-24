(()=>{
let Q=null;const N={sel:new Set(),time:null,gender:'',sty:[],slots:[]};
const gd=g=>g?t('g_'+g):'';
const tabs=k=>{document.querySelectorAll('[data-tab]').forEach(b=>b.classList.toggle('on',b.dataset.tab===k));$('#tab-q').hidden=k!=='q';$('#tab-n').hidden=k!=='n';if(k==='n')loadSlots()};
async function poll(){try{Q=await (await fetch('/api/reception/queue/')).json();draw()}catch(e){}}
function actions(b){const c=(a,k,cls)=>`<button class="${cls||'ghost'}" data-a="${a}" data-id="${b.id}">${t(k)}</button>`;
if(b.status==='booked')return c('verify','verify','pick')+c('cancel','cancel');
if(b.status==='waiting')return `<button class="pick" data-a="call" data-id="${b.id}"${b.can_call?'':' disabled'}>${t('call_chair')}</button>`+c('cancel','cancel')+(b.why?`<small class="why">${t('err_'+b.why)}</small>`:'');
if(b.status==='called')return c('cancel','cancel');
if(b.status==='serving')return c('done','mark_done','pick');return ''}
function card(b){const q=b.status==='booked'||b.status==='waiting';
return `<article class="bk ${b.status}"><div class="bt"><b class="tk">${b.token}</b><div><b>${b.name}</b><span class="sm">${[b.age,gd(b.gender),b.phone].filter(Boolean).join(' · ')}</span></div>
<span class="pill ${b.status}">${t('st_'+b.status)}</span><span class="pill">${t(b.walkin?'walkin':'online')}</span></div>
<p class="sm">${nm(b.services)} · ${b.minutes} ${t('mins')} · ₹${b.price}</p>
<p class="sm">${b.time} · ${b.stylist||'—'}${q?` · ${t('about')} ${b.wait} ${t('mins')}`:''}</p><div class="btns">${actions(b)}</div></article>`}
function draw(){const R=Q.rows,by=s=>R.filter(b=>s.includes(b.status)),
sec=(k,rows)=>rows.length?`<div class="sec"><h3 class="serif">${t(k)} <span class="pill">${rows.length}</span></h3>${rows.map(card).join('')}</div>`:'';
$('#queue').innerHTML=(sec('at_chair',by(['called','serving']))+sec('waiting_room',by(['waiting']))+sec('not_arrived',by(['booked']))+sec('recently_done',by(['done'])))||`<p class="empty">${t('empty_queue')}</p>`;
$('#stl').innerHTML=Q.stylists.map(s=>`<div class="bk"><div class="bt"><i class="av">${s.name[0]}</i><div><b>${s.name}</b><span class="sm">${s.occupied?`${t('at_chair')}: ${s.occupied}`:''}</span></div><span class="pill ${s.status}">${t(s.status)}</span></div>
<div class="btns"><button class="ghost" data-brk="${s.id}" data-to="${s.status==='break'?'available':'break'}"${s.occupied?' disabled':''}>${t(s.status==='break'?'back_work':'go_break')}</button></div></div>`).join('');drawForm()}
function drawForm(){if(!Q)return;let m=0,p=0;
$('#svcs').innerHTML=Q.services.map(s=>{if(N.sel.has(s.id)){m+=s.minutes;p+=s.price}return `<button class="chip${N.sel.has(s.id)?' on':''}" data-sv="${s.id}">${L(s,'name')}<small>${s.minutes}${t('min')} · ₹${s.price}</small></button>`}).join('');
$('#total').textContent=N.sel.size?`${t('total')}: ${m} ${t('min')} · ₹${p}`:'';
document.querySelectorAll('#gen .chip').forEach(c=>c.classList.toggle('on',c.dataset.g===N.gender));renderSlots();renderSty()}
async function loadSlots(){N.slots=(await (await fetch(`/api/reception/slots/?date=${$('#dt').value}`)).json()).slots;renderSlots()}
function renderSlots(){$('#slots').innerHTML=N.slots.map(x=>`<button class="slot${N.time===x.time?' on':''}" data-time="${x.time}"${x.ok?'':' disabled'}>${x.label==='now'?t('now'):x.label}</button>`).join('')}
async function loadSty(){N.sty=await (await fetch(`/api/stylists/?date=${$('#dt').value}&time=${N.time}`)).json();renderSty()}
function renderSty(){$('#stys').innerHTML=N.time?N.sty.map(x=>`<button class="sty${N.stylist===x.id?' on':''}" data-s="${x.id}"${x.booked?' disabled':''}><i class="av">${x.name[0]}</i>
<span class="nm"><b>${x.name}</b>${x.status==='break'?`<small>${t('is_on_break',{n:x.name})}</small>`:''}</span><span class="pill ${x.booked?'cancelled':x.status}">${x.booked?t('booked_t'):t(x.status)}</span></button>`).join(''):''}
document.addEventListener('click',async e=>{const b=e.target.closest('button');if(!b)return;const d=b.dataset;
if(d.tab)tabs(d.tab);
else if(d.a){if(d.a==='cancel'&&!confirm(t('cancel_q')))return;const r=await post(`/api/reception/act/${d.id}/`,{action:d.a});if(!r.ok)toast(errMsg(r.j.error));poll()}
else if(d.brk){const r=await post(`/api/reception/stylist/${d.brk}/`,{status:d.to});if(!r.ok)toast(errMsg(r.j.error));poll()}
else if(d.g){N.gender=d.g;drawForm()}
else if(d.sv){const i=+d.sv;N.sel.has(i)?N.sel.delete(i):N.sel.add(i);drawForm()}
else if(d.time){N.time=d.time;N.stylist=null;renderSlots();loadSty()}
else if(d.s){N.stylist=+d.s;renderSty()}});
$('#dt').onchange=()=>{N.time=null;N.stylist=null;loadSlots();renderSty()};
$('#book').onclick=async()=>{const p={name:$('#nm').value.trim(),age:$('#age').value,gender:N.gender,phone:$('#ph').value.trim(),services:[...N.sel],date:$('#dt').value,time:N.time,stylist:N.stylist};
if(!p.name||!p.phone||!N.sel.size||!N.time||!N.stylist)return toast(t('fill_all'));
const r=await post('/api/reception/book/',p);if(!r.ok){loadSlots();return toast(errMsg(r.j.error))}
toast(`${t('created_ok')} · ${r.j.token}`);['#nm','#age','#ph'].forEach(s=>$(s).value='');N.sel.clear();N.time=null;N.stylist=null;N.gender='';tabs('q');poll()};
$('#dt').value=fmtD(new Date());$('#dt').min=$('#dt').value;
window.addEventListener('langchange',()=>{if(Q)draw()});poll();setInterval(poll,5000);
})();
