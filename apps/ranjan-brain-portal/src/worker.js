const API_ORIGIN = 'https://ideasforgeai-api.onrender.com';

async function proxyBrain(request, url) {
  const suffix = url.pathname.replace('/api/brain', '');
  const target = new URL('/api/founder-brain/v1' + suffix, API_ORIGIN);
  target.search = url.search;
  const headers = new Headers({ accept: 'application/json' });
  const init = { method: request.method, headers, redirect: 'follow' };
  if (!['GET', 'HEAD'].includes(request.method)) {
    headers.set('content-type', request.headers.get('content-type') || 'application/json');
    init.body = await request.arrayBuffer();
  }
  const response = await fetch(target, init);
  const out = new Headers(response.headers);
  out.set('cache-control', 'no-store');
  out.set('x-forgebrain-proxy', 'ranjan-forgebrain');
  return new Response(response.body, { status: response.status, headers: out });
}
const page = `<!doctype html>
<html lang="en"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Ranjan - ForgeBrain 2.0</title>
<meta name="theme-color" content="#071018"/>
<style>
:root{--bg:#071018;--panel:#0b1620;--line:#1c3140;--text:#edf7fb;--muted:#8da3b0;--cyan:#4bd6f2;--green:#5ae38b}
*{box-sizing:border-box}body{margin:0;background:linear-gradient(180deg,#071018,#050b10);color:var(--text);font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,sans-serif}
button,input{font:inherit}.app{min-height:100vh;display:grid;grid-template-columns:240px 1fr}
.side{border-right:1px solid var(--line);padding:22px 18px;background:#08131b;position:sticky;top:0;height:100vh}
.brand{font-size:18px;font-weight:700}.brand small{display:block;color:var(--cyan);font-size:11px;margin-top:4px}.nav{margin-top:28px;display:grid;gap:8px}
.nav button{background:transparent;border:0;color:var(--muted);text-align:left;padding:10px 12px;border-radius:10px}.nav button.active,.nav button:hover{background:#10212c;color:var(--text)}
.main{padding:26px;max-width:1500px;width:100%;margin:auto}.top{display:flex;align-items:center;justify-content:space-between;gap:16px}
.kicker{color:var(--cyan);font-size:12px;text-transform:uppercase;letter-spacing:.12em}.title{font-size:30px;font-weight:700;margin:4px 0}.sub{color:var(--muted)}
.status{display:flex;align-items:center;gap:8px;color:var(--muted);font-size:13px}.dot{width:9px;height:9px;background:var(--green);border-radius:50%;box-shadow:0 0 12px #5ae38b80}
.grid{display:grid;grid-template-columns:1.3fr .7fr;gap:18px;margin-top:22px}.card{background:linear-gradient(180deg,#0d1b25,#0a151d);border:1px solid var(--line);border-radius:16px;padding:18px}.card h3{margin:0 0 12px;font-size:15px}
.metric{font-size:34px;font-weight:700}.muted{color:var(--muted)}.capgrid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}
.cap{border:1px solid #1c3444;background:#0c1821;border-radius:12px;padding:12px}.cap b{display:block;font-size:13px}.cap small{color:var(--muted)}
.pill{display:inline-block;margin-top:8px;padding:4px 7px;border-radius:999px;background:#0e2b2b;color:#75efad;font-size:10px}
.chat{display:grid;grid-template-rows:1fr auto;min-height:330px}.messages{display:grid;align-content:start;gap:10px;max-height:390px;overflow:auto;padding-right:4px}
.msg{padding:11px 13px;border-radius:12px;line-height:1.45;font-size:13px}.ai{background:#0d2230;border:1px solid #173b4c}.you{background:#13241b;border:1px solid #254d35}
.composer{display:flex;gap:8px;margin-top:12px}.composer input{flex:1;background:#071119;color:var(--text);border:1px solid var(--line);border-radius:11px;padding:12px}.composer button{border:0;background:var(--cyan);color:#041016;font-weight:700;padding:0 16px;border-radius:11px;cursor:pointer}
.row{display:flex;gap:10px;flex-wrap:wrap}.mini{flex:1;min-width:130px;padding:12px;border:1px solid var(--line);border-radius:12px}.mini b{display:block;font-size:17px}.mini span{font-size:11px;color:var(--muted)}
.notice{margin-top:16px;border:1px solid #3a3420;background:#211d10;color:#eadb99;padding:11px 13px;border-radius:12px;font-size:12px}.error{color:#ff8f8f}
@media(max-width:900px){.app{grid-template-columns:1fr}.side{display:none}.main{padding:16px}.grid{grid-template-columns:1fr}.capgrid{grid-template-columns:repeat(2,minmax(0,1fr))}.title{font-size:24px}}
@media(max-width:520px){.capgrid{grid-template-columns:1fr}.top{align-items:flex-start;flex-direction:column}}
</style></head><body><div class="app">
<aside class="side"><div class="brand">FORGEBRAIN <small>PRIVATE FOUNDER WORKSPACE</small></div><div class="nav"><button class="active">Brain</button><button>Memory</button><button>Decisions</button><button>Projects</button><button>Review</button><button>Capabilities</button></div></aside>
<main class="main"><div class="top"><div><div class="kicker">Ranjan - Cognitive Operating Layer</div><div class="title">ForgeBrain 2.0</div><div class="sub" id="phase">Connecting to brain...</div></div><div class="status"><span class="dot"></span><span id="live">Checking live API</span></div></div>
<div class="grid"><section class="card"><h3>Brain console</h3><div class="chat"><div class="messages" id="messages"><div class="msg ai">ForgeBrain is connected in read-only mode. Ask about current state, mission, plans, or current capabilities.</div></div><form class="composer" id="chat"><input id="prompt" autocomplete="off" placeholder="Ask ForgeBrain..."/><button>Ask</button></form></div></section>
<section class="card"><h3>Current state</h3><div class="metric" id="state">--</div><div class="muted" id="mission">Loading mission...</div><div class="row" style="margin-top:16px"><div class="mini"><b id="caps">--</b><span>Cognitive capabilities</span></div><div class="mini"><b id="mode">--</b><span>Operating mode</span></div></div><div class="notice">Persistent personal memory is not yet connected to Supabase. This live portal currently exposes governed, read-only ForgeBrain capabilities and planning.</div></section></div>
<section class="card" style="margin-top:18px"><h3>FB-2.1 cognitive capabilities</h3><div class="capgrid" id="capgrid"><div class="muted">Loading capability manifestâ€¦</div></div></section>
</main></div><script>
const api='https://ideasforgeai-api.onrender.com/api/founder-brain/v1', byId=id=>document.getElementById(id);
async function json(path,options){const r=await fetch(api+path,options);if(!r.ok)throw new Error('HTTP '+r.status);return r.json();}
function esc(v){return String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
async function load(){try{const [manifest,state,mission]=await Promise.all([json('/cognitive/manifest'),json('/state'),json('/mission')]);const m=manifest.data||{},s=state.data||{},ms=mission.data||{};byId('phase').textContent=m.phase||'ForgeBrain 2.0';byId('live').textContent='Live API connected';byId('state').textContent=s.operating_state||'ready';byId('mode').textContent=(s.operating_mode||'read_only').replace('_',' ');byId('mission').textContent=ms.mission||s.mission||'Build IdeasForgeAI';byId('caps').textContent=m.capability_count??0;const items=m.capabilities||[];byId('capgrid').innerHTML=items.map(x=>'<div class="cap"><b>'+esc(x.title)+'</b><small>'+esc(x.capability_id)+' - '+esc(x.version)+'</small><span class="pill">'+esc(x.status)+'</span></div>').join('')||'<div class="muted">No capabilities returned.</div>';}catch(e){byId('live').textContent='API unavailable';byId('live').className='error';byId('phase').textContent='ForgeBrain connection unavailable';}}
function add(text,cls){const d=document.createElement('div');d.className='msg '+cls;d.textContent=text;byId('messages').appendChild(d);byId('messages').scrollTop=byId('messages').scrollHeight;}
byId('chat').addEventListener('submit',async e=>{e.preventDefault();const input=byId('prompt'),text=input.value.trim();if(!text)return;add(text,'you');input.value='';try{const res=await json('/chat/plan',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({message:text})});const d=res.data||{};let out=d.response||d.summary||d.recommended_next_action||'';if(!out)out='Intent understood. This portal is currently read-only; execution remains governed.';add(out,'ai');}catch(err){add('ForgeBrain could not complete that planning request: '+err.message,'ai');}});
load();
</script></body></html>`;

export default {async fetch(request){const url=new URL(request.url);if(url.pathname.startsWith('/api/brain/'))return proxyBrain(request,url);if(url.pathname==='/health')return Response.json({ok:true,service:'ranjan-forgebrain',mode:'read_only'});return new Response(page,{headers:{'content-type':'text/html; charset=utf-8','cache-control':'no-store','x-content-type-options':'nosniff','referrer-policy':'no-referrer'}});}};
