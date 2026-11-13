import { createServer } from 'node:http';
import { createHmac, randomBytes } from 'node:crypto';
import { pathToFileURL } from 'node:url';

const previewOrigin = 'https://iconex-global-forum-preview.onrender.com';
const officialForm = 'https://iconexglobal.com/subscribe';
const officialOrigin = new URL(officialForm).origin;
const flashPages = new Set(['/', '/contact', '/contact/']);
const minute = 60_000;
const jsonType = 'application/json; charset=utf-8';

function result(response, code, status) {
  response.writeHead(code, {'Content-Type': jsonType, 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff'});
  response.end(JSON.stringify({status}));
}

async function readBounded(stream, limit) {
  let bytes = 0;
  const chunks = [];
  for await (const chunk of stream) {
    bytes += chunk.length;
    if (bytes > limit) throw new Error('Body too large');
    chunks.push(chunk);
  }
  return Buffer.concat(chunks).toString('utf8');
}

const affirmativePhrases = [
  /^(?:thank you|thanks) for subscribing(?: to (?:the |our |iCONEX )?(?:newsletter|updates))?[.!]?$/i,
  /^(?:(?:you(?: have|['’]ve)? )?(?:successfully subscribed|subscribed successfully)|you are now subscribed|(?:newsletter )?subscription successful)(?: to (?:our |the |iCONEX )?(?:newsletter|updates))?[.!]?$/i,
  /^(?:(?:your|this|the) e-?mail(?: address)? (?:is |was )?already subscribed|you (?:are |have )?already subscribed|already subscribed)[.!]?$/i
];

function affirmative(line) {
  return affirmativePhrases.some(expression => expression.test(line.replace(/\s+/g, ' ').trim()));
}

// A normal form page, HTTP 200, redirect, or unknown JSON never proves opt-in.
export function confirmsSubscription(contentType, body) {
  if (contentType.includes('application/json')) {
    let data;
    try { data = JSON.parse(body); } catch { return false; }
    if (!data || data.success === false || data.error || data.status === 'error') return false;
    return data.status === 'subscribed' || (typeof data.message === 'string' && affirmative(data.message));
  }
  if (contentType.includes('text/plain')) return affirmative(body);
  if (!contentType.includes('text/html')) return false;
  // Read rendered flash/receipt text, excluding scripts, comments and templates.
  const display = body.replace(/<!--[^]*?-->|<(script|style|template|noscript)\b[^>]*>[^]*?<\/\1\s*>/gi, ' ');
  const flashes = display.matchAll(/<(div|p|span)\b([^>]*(?:class\s*=\s*["'][^"']*\b(?:alert-success|success-message|toast-success)\b[^"']*["']|role\s*=\s*["'](?:status|alert)["'])[^>]*)>([^]*?)<\/\1\s*>/gi);
  for (const flash of flashes) {
    if (/\bhidden\b|(?:display\s*:\s*none|visibility\s*:\s*hidden)/i.test(flash[2])) continue;
    const message = flash[3].replace(/<button\b[^>]*>[^]*?<\/button\s*>/gi, '').replace(/<[^>]+>/g, ' ');
    if (affirmative(message)) return true;
  }
  return false;
}

async function receiveOfficialResult(fetchImpl, email) {
  const signal = AbortSignal.timeout(12_000);
  const request = {
    method: 'POST', redirect: 'manual', signal,
    headers: {'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'text/html, application/json;q=0.9'},
    body: new URLSearchParams({email, subscribe: 'Subscribe'})
  };
  let reply = await fetchImpl(officialForm, request);
  if ([301, 302, 303].includes(reply.status)) {
    const location = reply.headers.get('location');
    const cookies = reply.headers.getSetCookie?.() || [];
    await reply.body?.cancel();
    if (!location) return false;
    const target = new URL(location, officialForm);
    if (target.origin !== officialOrigin || target.username || target.password || !flashPages.has(target.pathname)) return false;
    const options = {method: 'GET', redirect: 'manual', signal, headers: {}};
    // One-request flash cookies stay on their issuing origin and are discarded.
    const cookie = cookies.map(value => value.split(';', 1)[0]).filter(value => /^[\w-]+=[\w%+~.:=_/-]*$/.test(value)).join('; ');
    if (cookie && cookie.length <= 4096) options.headers.Cookie = cookie;
    reply = await fetchImpl(target, options);
  }
  if (!reply.ok || !reply.body) {
    await reply.body?.cancel();
    return false;
  }
  const content = await readBounded(reply.body, 512 * 1024);
  return confirmsSubscription(reply.headers.get('content-type') || '', content);
}

export function createNewsletterServer({fetchImpl = fetch, now = Date.now} = {}) {
  const attempts = new Map();
  const key = randomBytes(32);
  let windowStart = now(), count = 0, inflight = 0;

  const server = createServer(async (request, response) => {
    if (request.method === 'GET' && request.url === '/health') return result(response, 200, 'ready');
    if (request.url !== '/subscribe') return result(response, 404, 'not-found');
    response.setHeader('Vary', 'Origin');
    if (request.headers.origin !== previewOrigin) return result(response, 403, 'forbidden');
    response.setHeader('Access-Control-Allow-Origin', previewOrigin);
    if (request.method === 'OPTIONS') {
      response.writeHead(204, {'Access-Control-Allow-Methods': 'POST', 'Access-Control-Allow-Headers': 'Content-Type', 'Access-Control-Max-Age': '600'});
      return response.end();
    }
    if (request.method !== 'POST') return result(response, 405, 'method-not-allowed');
    if (request.headers['content-type']?.split(';')[0].trim().toLowerCase() !== 'application/json') return result(response, 415, 'invalid');
    if (Number(request.headers['content-length'] || 0) > 2048) return result(response, 413, 'invalid');
    let email;
    try { email = JSON.parse(await readBounded(request, 2048)).email?.trim(); }
    catch { return result(response, 400, 'invalid'); }
    if (typeof email !== 'string' || email.length > 254 || !/^[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+$/.test(email)) return result(response, 400, 'invalid');
    const time = now();
    if (time - windowStart >= minute) { windowStart = time; count = 0; }
    const id = createHmac('sha256', key).update(email.toLowerCase()).digest('hex');
    for (const [entry, attempt] of attempts) if (attempt.until <= time) attempts.delete(entry);
    const previous = attempts.get(id);
    if (previous) return result(response, previous.code, previous.status);
    if (inflight >= 8 || count >= 40) {
      response.setHeader('Retry-After', '60');
      return result(response, 429, 'busy');
    }
    count++;
    inflight++;
    // A second simultaneous request must not forward the same address twice.
    attempts.set(id, {until: time + minute, code: 409, status:'pending'});
    let accepted = false;
    try { accepted = await receiveOfficialResult(fetchImpl, email); } catch { /* Upstream may have received the POST. */ }
    finally { inflight--; }
    const code = accepted ? 200 : 502;
    const status = accepted ? 'subscribed' : 'unconfirmed';
    attempts.set(id, {until: now() + (accepted ? 10 : 1) * minute, code, status});
    return result(response, code, status);
  });
  server.requestTimeout = 15_000;
  server.headersTimeout = 10_000;
  server.keepAliveTimeout = 5_000;
  return server;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  createNewsletterServer().listen(Number(process.env.PORT || 10000), '0.0.0.0');
}
