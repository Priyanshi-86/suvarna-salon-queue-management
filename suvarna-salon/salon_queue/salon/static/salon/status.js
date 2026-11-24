(()=>{
const id=document.querySelector('main').dataset.id,$=s=>document.querySelector(s),C=2*Math.PI*54;
const csrf=$('meta[name=csrf]').content;let D=null,max=1;
const ord=n=>{const s=['th','st','nd','rd'],v=n%100;return n+(s[(v-20)%10]||s[v]||s[0])};
async function poll(){try{D=await (await fetch(`/api/status/${id}/`)).json();draw()}catch(e){}}
function draw(){if(!D)return;const q=D.state==='booked'||D.state==='waiting';
$('#tok').textContent=D.token;max=Math.max(max,D.wait,1);
$('.ringw').hidden=!q;$('#pos').hidden=!q;$('#cancelBtn').hidden=!q;
$('#pos').textContent=q?t('pos',{n:lang==='en'?ord(D.position):D.position}):'';
$('#wait').textContent=D.wait;$('#waitl').textContent=`${t('about')} · ${t('mins')}`;
$('#rf').style.strokeDashoffset=C*(D.wait/max);
const ban=$('#banner');ban.hidden=!(q&&D.position===2);ban.textContent=t('come_soon');
const m=$('#msg'),txt={serving:'serving_now',done:'done_msg',cancelled:'cancelled_msg'}[D.state];
m.hidden=!txt;if(txt)m.textContent=t(txt);
$('#turn').hidden=D.state!=='called';$('#goto').textContent=t('go_to',{n:D.stylist});
$('#info').textContent=D.services.map(s=>L(s,'name')).join(', ')+` · ${D.minutes} ${t('mins')} · ₹${D.price}`+(D.stylist?` · ${D.stylist}`:'')}
$('#cancelBtn').onclick=()=>$('#cm').classList.add('on');
$('#keep').onclick=()=>$('#cm').classList.remove('on');
$('#yes').onclick=async()=>{await fetch(`/api/cancel/${id}/`,{method:'POST',headers:{'X-CSRFToken':csrf}});$('#cm').classList.remove('on');poll()};
window.addEventListener('langchange',draw);poll();setInterval(poll,5000);
})();
