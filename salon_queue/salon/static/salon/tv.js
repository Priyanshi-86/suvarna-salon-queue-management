(()=>{
let D=null;const LOC={en:'en-IN',hi:'hi-IN',gu:'gu-IN'};
async function poll(){try{D=await (await fetch('/api/tv/')).json();draw()}catch(e){}}
function draw(){if(!D)return;
$('#rows').innerHTML=D.rows.length?D.rows.map((r,i)=>{const chair=r.status==='called'||r.status==='serving',nxt=!chair&&r.pos===1;
return `<tr class="${chair?'gold':nxt?'sage':i%2?'alt':''}"><td>${chair?t('at_chair'):r.pos}</td><td>${r.token}</td><td>${r.name}</td><td>${nm(r.services)}</td><td>${r.stylist||'—'}</td><td>${chair?'—':r.est}</td></tr>`}).join(''):`<tr><td colspan="6" class="empty">${t('no_wait')}</td></tr>`}
const clock=()=>$('#clock').textContent=new Date().toLocaleTimeString(LOC[lang],{hour:'numeric',minute:'2-digit'});
setInterval(clock,1000);clock();
setInterval(()=>{const k=['en','hi','gu'];lang=k[(k.indexOf(lang)+1)%3];applyLang()},8000);  // rotate languages on the TV
window.addEventListener('langchange',()=>{draw();clock()});poll();setInterval(poll,5000);
})();
