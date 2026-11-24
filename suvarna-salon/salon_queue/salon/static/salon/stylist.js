(()=>{
const id=$('main').dataset.id;let D=null,hold=null,seen=null;
const gd=g=>g?t('g_'+g):'';
async function poll(){try{D=await (await fetch(`/api/stylist/${id}/`)).json();notify();draw()}catch(e){}}
function notify(){const ids=new Set(D.schedule.map(b=>b.id));if(seen&&[...ids].some(i=>!seen.has(i)))toast(t('new_booking_toast'));seen=ids}
function draw(){if(!D)return;const c=hold||D.current;let h='';
if(!c)h=`<p class="sm">${t('served_today')}: ${D.done}</p><p>${t('no_client')}</p>`;
else{const st=hold?'done':c.status==='serving'?'serving':'start';
h=`<p class="sm">${t('current_client')}</p><div class="tk">${c.token}</div><h2 class="serif">${c.name}</h2>
<p class="sm">${[c.age,gd(c.gender),c.phone].filter(Boolean).join(' · ')}</p><p>${nm(c.services)}</p><p class="sm">${c.minutes} ${t('mins')} · ₹${c.price}</p>
<button class="act ${st}" id="act"${hold?' disabled':''}>${t({start:'start',serving:'serving_btn',done:'done_btn'}[st])}</button>`}
$('#cur').innerHTML=h;
$('#sched').innerHTML=D.schedule.length?D.schedule.map(b=>`<div class="sch"><b class="tk">${b.token}</b><div><b>${b.name}</b><span class="sm">${nm(b.services)}</span></div><span class="sm">${b.time}</span><span class="pill ${b.status}">${t('st_'+b.status)}</span></div>`).join(''):`<p class="empty">${t('none_yet')}</p>`}
document.addEventListener('click',async e=>{if(e.target.id!=='act'||hold)return;const c=D.current,a=c.status==='called'?'start':'done';
const r=await post(`/api/stylist/${id}/act/`,{action:a});if(!r.ok)return toast(errMsg(r.j.error));
if(a==='done'){hold={...c,status:'done'};draw();setTimeout(()=>{hold=null;poll()},3000)}else poll()});
window.addEventListener('langchange',draw);poll();setInterval(poll,5000);
})();
