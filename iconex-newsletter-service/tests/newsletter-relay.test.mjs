import { test } from 'node:test';
import assert from 'node:assert/strict';
import { once } from 'node:events';
import { createNewsletterServer, confirmsSubscription } from '../server.mjs';
const origin = 'https://iconex-global-forum-preview.onrender.com';
const testEmail = 'gallery-qa@example.invalid';

async function fixture(t, implementation) {
  const calls = [];
  const server = createNewsletterServer({
    fetchImpl: (...args) => { calls.push(args); return implementation(...args); }
  });
  server.listen(0, '127.0.0.1');
  await once(server, 'listening');
  t.after(() => new Promise(resolve => server.close(resolve)));
  const endpoint = 'http://127.0.0.1:' + server.address().port;
  function send(email, custom = {}) {
    return fetch(endpoint + '/subscribe', {method: 'POST', headers: {Origin:origin, 'Content-Type':'application/json'}, body:JSON.stringify({email}), ...custom});
  }
  return {send, calls, endpoint};
}

test('receipt parsing rejects generic pages, template examples, failures and non-receipt JSON', () => {
  for (const html of [
    '<h1>Contact</h1><p>Subscribe our newsletter</p>',
    '<script>alert("Thank you for subscribing.")</script>',
    '<div role="status" hidden>Thank you for subscribing.</div>',
    '<div class="alert-success">Thank you for contacting us.</div>',
    '<template><p role="alert">Thank you for subscribing.</p></template>',
    '<p role="alert">Subscription unsuccessful</p>'
  ]) assert.equal(confirmsSubscription('text/html', html), false, html);
  for (const obj of [{status:true},{status:'ok'}, {success:true},{success:false,message:'Thank you for subscribing.'}]) {
    assert.equal(confirmsSubscription('application/json', JSON.stringify(obj)), false);
  }
  assert.equal(confirmsSubscription('text/html', '<div class="alert alert-success">Thank you for subscribing.</div>'),true);
  assert.equal(confirmsSubscription('application/json', '{"message":"Your email is already subscribed."}'), true);
});

test('origin, validation and health do not submit addresses', async t => {
  const {send, calls, endpoint} = await fixture(t,()=>{ throw Error('unexpected upstream call'); });
  assert.equal((await fetch(endpoint+'/health')).status, 200);
  assert.equal((await send('invalid')).status, 400);
  assert.equal((await send(testEmail, {headers:{Origin:'https://other.example','Content-Type':'application/json'}})).status, 403);
  assert.equal((await send(testEmail, {headers:{Origin:origin,'Content-Type':'text/plain'}})).status, 415);
  const preflight = await fetch(endpoint+'/subscribe',{method:'OPTIONS', headers:{Origin:origin}});
  assert.equal(preflight.status, 204);
  assert.equal(preflight.headers.get('access-control-allow-origin'), origin);
  assert.equal(calls.length,0);
});

test('official POST and flash-cookie redirect preserve exact form fields and require receipt', async t => {
  const {send,calls} = await fixture(t,(url,opts)=>{
    if (opts.method === 'POST') return new Response(null, {status:303,headers:{Location:'/contact','Set-Cookie':'ci_session=abc123; Path=/; HttpOnly'}});
    assert.equal(opts.headers.Cookie,'ci_session=abc123');
    return new Response('<div class="alert alert-success">Thank you for subscribing.</div>',{headers:{'content-type':'text/html'}});
  });
  assert.deepEqual(await (await send(testEmail)).json(),{status:'subscribed'});
  assert.equal(calls[0][0],'https://iconexglobal.com/subscribe');
  assert.equal(calls[0][1].body.get('email'), testEmail);
  assert.equal(calls[0][1].body.get('subscribe'),'Subscribe');
  assert.equal(String(calls[1][0]),'https://iconexglobal.com/contact');
  assert.deepEqual(await (await send(testEmail)).json(),{status:'subscribed'});
  assert.equal(calls.length,2);
});

test('ambiguous result neither confirms the email nor sends a second immediate POST', async t=>{
  const {send,calls}=await fixture(t,()=>new Response('<h1>Contact</h1>',{headers:{'content-type':'text/html'}}));
  for(let i=0;i<2;i++) {const response=await send(testEmail);assert.equal(response.status,502);assert.deepEqual(await response.json(),{status:'unconfirmed'});}
  assert.equal(calls.length,1);
});

test('unexpected redirects cannot forward credentials or subscriber data', async t=>{
  const {send,calls}=await fixture(t,()=>new Response(null,{status:303,headers:{location:'https://example.invalid/admin','set-cookie':'session=private'}}));
  assert.equal((await send(testEmail)).status,502);
  assert.equal(calls.length,1);
});

test('redirect to generic contact HTML and failed follow-up GET each remain unconfirmed', async t => {
  for (const secondary of [new Response('<h1>Contact</h1>',{headers:{'content-type':'text/html'}}),new Response('',{status:503})]) {
    const {send,calls}=await fixture(t,(url,opts)=>opts.method === 'POST' ? new Response(null,{status:302,headers:{Location:'/contact'}}) : secondary);
    assert.equal((await send(testEmail)).status,502);
    assert.equal(calls.length,2);
  }
  for (const path of ['/gallery','https://www.iconexglobal.com/contact']) {
    const {send,calls}=await fixture(t,()=>new Response(null,{status:302,headers:{Location:path}}));
    assert.equal((await send(testEmail)).status,502);
    assert.equal(calls.length,1);
  }
});

test('only explicit affirmative subscription phrases qualify', () => {
  for(const line of ['Subscribed successfully.', 'Your email address is already subscribed.', 'Thank you for subscribing to our newsletter!', 'Already subscribed']) {
    assert.equal(confirmsSubscription('text/html','<div class="alert-success">'+line+'</div>'),true,line);
  }
  for(const line of ['Thank you for your interest!', 'Your form has been submitted.', 'We could not subscribe you.', 'Not subscribed successfully.']) {
    assert.equal(confirmsSubscription('text/html','<div class="alert-success">'+line+'</div>'),false,line);
  }
});
