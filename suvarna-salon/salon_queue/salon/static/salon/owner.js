(()=>{
let R='day',D=null;
async function poll(){const r=await fetch('/api/owner/?range='+R);if(!r.ok)return;D=await r.json();draw()}
function bars(data){const W=Math.max(data.length*38,360),H=190,mx=Math.max(...data.map(d=>d.value),1),bw=W/data.length;
$('#chart').innerHTML=`<svg viewBox="0 0 ${W} ${H+26}" role="img">${data.map((d,i)=>{const h=(H-22)*d.value/mx,x=i*bw;
return `<rect x="${x+bw*.2}" y="${H-h}" width="${bw*.6}" height="${h}" rx="3" fill="var(--gold)"/><text x="${x+bw/2}" y="${H-h-5}" text-anchor="middle" class="cv">${d.value}</text><text x="${x+bw/2}" y="${H+16}" text-anchor="middle" class="cl">${d.label}</text>`}).join('')}</svg>`}
function spark(v){const mx=Math.max(...v,1),pts=v.map((n,i)=>`${i*20+4},${30-n/mx*26}`).join(' ');return `<svg viewBox="0 0 128 34" width="128" height="34"><polyline points="${pts}" fill="none" stroke="var(--gold)" stroke-width="2"/></svg>`}
const table=(head,rows)=>rows.length?`<div class="tw"><table class="tbl"><thead><tr>${head.map(h=>`<th>${t(h)}</th>`).join('')}</tr></thead><tbody>${rows.map(r=>`<tr>${r.map(c=>`<td>${c}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`:`<p class="empty">${t('none_t')}</p>`;
function draw(){
$('#kpis').innerHTML=[['kpi_total','total'],['kpi_done','done'],['kpi_cancel','cancelled'],['kpi_walk','walkins']].map(([k,f])=>`<div class="kpi"><span class="sm">${t(k)}</span><b>${D.kpi[f]}</b></div>`).join('');
$('#ct').textContent=t(R==='day'?'flow_today':'flow_month');bars(D.chart);
$('#perf').innerHTML=D.perf.map(s=>`<div class="card"><h3 class="serif">${s.name}</h3>
<div class="row"><span>${t('today_t')}</span><span><b>${s.today}</b></span></div><div class="row"><span>${t('this_month')}</span><span><b>${s.month}</b></span></div>
<div class="row"><span>${t('avg_time')}</span><span>${s.avg===null?'—':s.avg+' '+t('mins')}</span></div><p class="sm">${t('last7')}</p>${spark(s.spark)}</div>`).join('');
$('#up').innerHTML=table(['token','client','service','stylist','time'],D.upcoming.map(u=>[u.token,u.name,nm(u.services),u.stylist,u.time]));
$('#cx').innerHTML=table(['cancelled_at','service','assigned'],D.cancels.map(c=>[c.at,nm(c.services),c.stylist]))}
document.querySelectorAll('.seg button').forEach(b=>b.onclick=()=>{R=b.dataset.r;document.querySelectorAll('.seg button').forEach(x=>x.classList.toggle('on',x===b));poll()});
window.addEventListener('langchange',()=>{if(D)draw()});poll();setInterval(poll,5000);
})();
