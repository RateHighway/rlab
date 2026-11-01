'use strict';
// Context-only teaching sample. Not a complete SDK or a production runtime.
const pageId = 'com.example.fleet-pressure';
const pageVersion = '0.1.1';
const statusNode = document.getElementById('status');
const resultsNode = document.getElementById('results');
let config = null;
let session = null;
let contextVersion = 0;
let state = 'waiting';
let incoming = 0;
let outgoing = 0;
let hostOrigin = null;
let windowStart = Date.now();
let messageCount = 0;
const uuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const exactKeys = (o, keys) => o && typeof o === 'object' && !Array.isArray(o) &&
  Object.keys(o).length === keys.length && keys.every(k => Object.prototype.hasOwnProperty.call(o, k));

function stop(message) {
  state = 'closed'; session = null;
  resultsNode.hidden = true;
  statusNode.textContent = message;
}

function send(type, payload) {
  window.parent.postMessage({protocolVersion:'0.2',type,id:crypto.randomUUID(),
    timestamp:new Date().toISOString(),sessionId:session,sequence:++outgoing,payload}, hostOrigin);
}

function showContext(payload) {
  if (!Number.isSafeInteger(payload.contextVersion) || payload.contextVersion <= contextVersion ||
      !payload.context || typeof payload.context.environment !== 'string') return false;
  contextVersion = payload.contextVersion;
  // No requests exist here; an API page must abort requests and discard old results.
  statusNode.textContent = 'Connected. Fixed synthetic data only; host environment: ' + payload.context.environment;
  resultsNode.hidden = false;
  return true;
}

window.addEventListener('message', event => {
  if (!config || state === 'closed' || event.source !== window.parent ||
      !config.allowedHostOrigins.includes(event.origin)) return;
  const now = Date.now();
  if (now - windowStart >= 1000) {windowStart = now; messageCount = 0;}
  if (++messageCount > 20) {stop('Host message limit exceeded. Reopen this page.'); return;}
  const m = event.data;
  try {
    if (new TextEncoder().encode(JSON.stringify(m)).length > 262144) return;
  } catch (_) {return;}
  if (!exactKeys(m,['protocolVersion','type','id','timestamp','sessionId','sequence','payload']) ||
      m.protocolVersion !== '0.2' || !uuid.test(m.id) || !uuid.test(m.sessionId) ||
      typeof m.timestamp !== 'string' || !Number.isFinite(Date.parse(m.timestamp)) ||
      !Number.isSafeInteger(m.sequence)) return;
  if (m.type === 'rlab.host.init') {
    if (state !== 'waiting' || m.sequence !== 0 ||
        !exactKeys(m.payload,['pageId','pageVersion','hostApiVersion']) ||
        m.payload.pageId !== pageId || m.payload.pageVersion !== pageVersion ||
        !/^0\.2\.(0|[1-9][0-9]*)$/.test(m.payload.hostApiVersion)) return;
    session = m.sessionId; hostOrigin = event.origin; incoming = 0; outgoing = 0; state = 'ready';
    send('rlab.page.ready',{pageId,pageVersion});
    return;
  }
  if (m.sessionId !== session || event.origin !== hostOrigin || m.sequence <= incoming) return;
  if (m.type === 'rlab.host.shutdown') {
    if (!exactKeys(m.payload,['reason']) || !['logout','expired','revoked','suspended','context-switch','update'].includes(m.payload.reason)) return;
    incoming = m.sequence;
    stop('Host session ended. Reopen this page to continue.');
    return;
  }
  if (m.type === 'rlab.host.session' && state === 'ready') {
    if (!exactKeys(m.payload,['grantedPermissions','contextVersion','context','services','theme']) ||
        !Array.isArray(m.payload.grantedPermissions) ||
        m.payload.grantedPermissions.length !== 1 || m.payload.grantedPermissions[0] !== 'context.read' ||
        !Array.isArray(m.payload.services) || m.payload.services.length !== 0) {
      stop('Unexpected permissions or service configuration.'); return;
    }
    if (!showContext(m.payload)) {stop('Required context is missing.'); return;}
    incoming = m.sequence; state = 'active';
    send('rlab.page.active',{contextVersion});
    return;
  }
  if (m.type === 'rlab.host.context.changed' && state === 'active') {
    if (!exactKeys(m.payload,['contextVersion','context'])) return;
    if (showContext(m.payload)) incoming = m.sequence;
  }
});

fetch('/__rlab/host-config.json',{credentials:'omit',cache:'no-store',redirect:'error'})
  .then(response => {if (!response.ok) throw new Error('Configuration missing'); return response.json();})
  .then(value => {
    if (!exactKeys(value,['allowedHostOrigins','pageId','pageVersion']) ||
        value.pageId !== pageId || value.pageVersion !== pageVersion ||
        !Array.isArray(value.allowedHostOrigins) || value.allowedHostOrigins.length === 0 ||
        !value.allowedHostOrigins.every(origin => {
          try {const u=new URL(origin);return u.protocol==='https:' && u.origin===origin &&
            !u.username && !u.password && origin!==window.location.origin;} catch (_) {return false;}
        })) throw new Error('Invalid configuration');
    config = value;
  })
  .catch(() => stop('Host configuration unavailable. Import this sample into a development host.'));

setTimeout(() => {if (state !== 'active' && state !== 'closed') stop('Host connection timed out. Reopen this page.');},10000);
