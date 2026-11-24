(()=>{
const B=JSON.parse(document.getElementById('boot').textContent),$=s=>document.querySelector(s);
const csrf=$('meta[name=csrf]').content,LOC={en:'en-IN',hi:'hi-IN',gu:'gu-IN'};
const fmt=d=>`${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
const S={step:1,sel:new Set(),date:fmt(new Date()),time:null,tlabel:'',stylist:null,sdata:[],slots:null};
const svc=id=>B.services.find(s=>s.id===id);
const tot=()=>{let m=0,p=0;S.sel.forEach(i=>{m+=svc(i).minutes;p+=svc(i).price});return{m,p}};
const stName=()=>(S.sdata.find(x=>x.id===S.stylist)||{}).name||'';

function go(n){S.step=n;document.querySelectorAll('.step').forEach(e=>e.hidden=+e.dataset.step!==n);
document.querySelectorAll('.dots i').forEach((d,i)=>d.classList.toggle('on',i<n));
if(n===2)loadSlots();if(n===3)loadStylists();render();scrollTo(0,0)}

function renderServices(){$('#svcs').innerHTML=B.services.map(s=>`<article class="card svc${S.sel.has(s.id)?' sel':''}"><div class="ph">${s.glyph}</div><div class="bd">
<h3>${L(s,'name')}</h3><p class="sm">${s.minutes} ${t('min')} · ₹${s.price}</p><div class="btns">
<button class="ghost" data-d="${s.id}">${t('show_details')}</button><button class="pick" data-p="${s.id}">${S.sel.has(s.id)?t('selected'):t('select')}</button></div></div></article>`).join('')}

function detail(id){const s=svc(id);$('#sheet').innerHTML=`<h3>${L(s,'name')}</h3><p>${L(s,'desc')}</p>
<p class="sm">${t('duration')}: ${s.minutes} ${t('min')} · ₹${s.price}</p><ul class="sl">${B.stylists.map(x=>`<li><i class="av">${x.name[0]}</i>${x.name}<span class="pill ${x.status}">${t(x.status)}</span></li>`).join('')}</ul>
<button class="cta" id="bs">${t('book_slot')}</button>`;$('#modal').classList.add('on');
$('#bs').onclick=()=>{S.sel.add(id);$('#modal').classList.remove('on');go(2)}}

function renderDates(){const b=new Date();$('#dates').innerHTML=[...Array(14)].map((_,i)=>{const d=new Date(b);d.setDate(b.getDate()+i);const iso=fmt(d),l=LOC[lang];
return`<button class="day${S.date===iso?' on':''}" data-d="${iso}"><b>${d.toLocaleDateString(l,{weekday:'short'})}</b><span>${d.getDate()}</span><em>${d.toLocaleDateString(l,{month:'short'})}</em></button>`}).join('')}

async function loadSlots(){S.slots=await (await fetch(`/api/slots/?date=${S.date}`)).json();renderSlots()}
function renderSlots(){if(!S.slots)return;renderDates();const n=$('#closedNote'),free=S.slots.slots.some(x=>x.ok);
n.hidden=free;n.textContent=S.slots.closed?t('online_closed'):t('no_slots');
$('#slots').innerHTML=S.slots.slots.map(x=>`<button class="slot${S.time===x.time?' on':''}" data-t="${x.time}" data-l="${x.label}"${x.ok?'':' disabled'}>${x.label}</button>`).join('')}

async function loadStylists(){S.sdata=await (await fetch(`/api/stylists/?date=${S.date}&time=${S.time}`)).json();renderStylists()}
function renderStylists(){$('#stys').innerHTML=S.sdata.map(x=>`<button class="sty${S.stylist===x.id?' on':''}" data-s="${x.id}"${x.booked?' disabled':''}>
<i class="av">${x.name[0]}</i><span class="nm"><b>${x.name}</b>${x.status==='break'?`<small>${t('is_on_break',{n:x.name})}</small>`:''}</span>
<span class="pill ${x.booked?'cancelled':x.status}">${x.booked?t('booked_t'):t(x.status)}</span></button>`).join('')}

function renderSummary(){const T=tot(),d=new Date(S.date+'T00:00');
$('#sumry').innerHTML=[...S.sel].map(i=>`<div class="row"><span>${L(svc(i),'name')}</span><span>₹${svc(i).price}</span></div>`).join('')+
`<div class="row"><span>${d.toLocaleDateString(LOC[lang],{weekday:'short',day:'numeric',month:'short'})} · ${S.tlabel}</span><span>${stName()}</span></div>
<div class="row"><span>${t('total')} · ${T.m} ${t('min')}</span><span>₹${T.p}</span></div>`}

function render(){renderServices();renderSlots();if(S.sdata.length)renderStylists();if(S.step===4)renderSummary();
const T=tot(),nx=$('#next');$('#tot').textContent=S.sel.size?`${T.m} ${t('min')} · ₹${T.p}`:'';
$('#back').style.visibility=S.step>1?'visible':'hidden';
nx.textContent=[0,t('next'),t('choose_stylist'),t('next'),t('confirm')][S.step];
nx.disabled=!((S.step===1&&S.sel.size)||(S.step===2&&S.time)||(S.step===3&&S.stylist)||S.step===4);
$('.bar').hidden=false}

$('#svcs').onclick=e=>{const b=e.target.closest('button');if(!b)return;
if(b.dataset.d)detail(+b.dataset.d);if(b.dataset.p){const i=+b.dataset.p;S.sel.has(i)?S.sel.delete(i):S.sel.add(i);render()}};
$('#modal').onclick=e=>{if(e.target.id==='modal')e.target.classList.remove('on')};
$('#dates').onclick=e=>{const b=e.target.closest('.day');if(b){S.date=b.dataset.d;S.time=null;S.stylist=null;loadSlots();render()}};
$('#slots').onclick=e=>{const b=e.target.closest('.slot');if(b){S.time=b.dataset.t;S.tlabel=b.dataset.l;S.stylist=null;renderSlots();render()}};
$('#stys').onclick=e=>{const b=e.target.closest('.sty');if(b){S.stylist=+b.dataset.s;renderStylists();render()}};
$('#back').onclick=()=>go(S.step-1);
$('#next').onclick=async()=>{if(S.step<4)return go(S.step+1);
const nm=$('#nm').value.trim(),ph=$('#ph').value.trim(),er=$('#err');
if(!nm||!ph){er.textContent=t('fill');er.hidden=false;return}
const r=await fetch('/api/book/',{method:'POST',headers:{'Content-Type':'application/json','X-CSRFToken':csrf},
body:JSON.stringify({services:[...S.sel],date:S.date,time:S.time,stylist:S.stylist,name:nm,phone:ph})});
const j=await r.json();if(r.ok)location.href=`/status/${j.id}/`;else{er.textContent=t('err_book');er.hidden=false}};
$('#nm').value=B.name;$('#ph').value=B.phone;
window.addEventListener('langchange',()=>{$('#modal').classList.remove('on');render()});
render();
})();
