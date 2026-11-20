'use strict';
// RLAB-PAGE-0.4 teaching sample. Not a complete SDK or a production runtime.
// Opened directly, it shows invented sample groups and saves nothing.
// In a 0.4 host session it shows the write pattern: one idempotency key per
// intended change, the service's message and next step shown unchanged, no
// silent retry, and the access token kept in memory only.
const pageId = 'com.example.group-manager';
const pageVersion = '0.1.0';
const serviceId = 'com.ratehighway.utilization4.query';
const requiredPermissions = ['context.read', 'utilization.read', 'utilization.manage'];

const statusNode = document.getElementById('status');
const carBody = document.getElementById('car-groups');
const locationList = document.getElementById('location-groups');
const logList = document.getElementById('change-log');
const addForm = document.getElementById('add-car');

// Invented sample data. Location AAA and every group name are fictional.
const sample = {
  carGroups: [
    {name: 'Economy and Compact', classes: ['ECAR', 'CCAR']},
    {name: 'Midsize', classes: ['ICAR', 'SCAR']},
    {name: 'SUV', classes: ['IFAR', 'SFAR', 'FFAR']},
    {name: 'Premium', classes: ['PCAR', 'LCAR']}
  ],
  locationGroups: [
    {name: 'Sample West Region', locations: ['AAA', 'AAB', 'AAC']},
    {name: 'Sample Airport Locations', locations: ['AAA', 'AAD']}
  ]
};

let mode = 'sample'; // sample | waiting | active | closed
let config = null;
let session = null;
let hostOrigin = null;
let service = null;
let auth = null; // memory only: never stored, logged or put in a URL
let contextVersion = 0;
let incoming = 0;
let outgoing = 0;
let windowStart = Date.now();
let messageCount = 0;
const uuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const exactKeys = (o, keys) => o && typeof o === 'object' && !Array.isArray(o) &&
  Object.keys(o).length === keys.length && keys.every(k => Object.prototype.hasOwnProperty.call(o, k));

function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text) node.textContent = text;
  if (className) node.className = className;
  return node;
}

function render() {
  carBody.replaceChildren(...sample.carGroups.map((group, index) => {
    const row = element('tr');
    row.append(element('th', group.name), element('td', group.classes.join(', ')));
    const cell = element('td');
    const remove = element('button', 'Delete', 'secondary');
    remove.type = 'button';
    remove.setAttribute('aria-label', 'Delete ' + group.name);
    remove.addEventListener('click', () => requestChange({kind: 'car-group.delete', index, name: group.name}));
    cell.append(remove); row.append(cell);
    row.querySelector('th').scope = 'row';
    return row;
  }));
  locationList.replaceChildren(...sample.locationGroups.map(group => {
    const item = element('li');
    item.append(element('strong', group.name), element('span', group.locations.join(', ')));
    return item;
  }));
}

function logChange(summary, outcome, nextStep) {
  const item = element('li');
  item.append(element('strong', summary), element('span', outcome));
  if (nextStep) item.append(element('span', 'Next step: ' + nextStep, 'next'));
  logList.prepend(item);
}

// The group-change call belongs to the host's service contract, not to the
// .rlab standard. This sample deliberately does not invent one. Replace this
// function with the call your host publishes, sending the idempotency key and
// returning the service's own {code, message, nextStep} on refusal.
function sendGroupChange(change, idempotencyKey) {
  void change; void idempotencyKey;
  return Promise.resolve({ok: false, code: 'SAMPLE_NO_SERVICE_CALL',
    message: 'This sample does not call a group-change service, so nothing was saved.',
    nextStep: 'Use a page built for your host\'s published group-change call.'});
}

function applyLocally(change) {
  if (change.kind === 'car-group.delete') sample.carGroups.splice(change.index, 1);
  if (change.kind === 'car-group.create') sample.carGroups.push({name: change.name, classes: change.classes});
  render();
}

function describe(change) {
  return change.kind === 'car-group.delete' ? 'Delete car group ' + change.name :
    'Add car group ' + change.name + ' (' + change.classes.join(', ') + ')';
}

function requestChange(change) {
  const summary = describe(change);
  if (mode === 'sample') {
    applyLocally(change);
    logChange(summary, 'Shown here only. Not saved: this is sample data without a host session.');
    return;
  }
  if (mode !== 'active' || !auth) {
    logChange(summary, 'Not saved: the host session is not active.', 'Reopen this page from your host.');
    return;
  }
  // One key per intended change. Reuse it only to retry this same change.
  const idempotencyKey = crypto.randomUUID();
  sendGroupChange(change, idempotencyKey).then(result => {
    if (result.ok) {applyLocally(change); logChange(summary, result.message || 'Saved.'); return;}
    // Show the service's words unchanged and never retry a refusal silently.
    logChange(summary, result.message, result.nextStep);
  });
}

addForm.addEventListener('submit', event => {
  event.preventDefault();
  const name = addForm.elements.name.value.trim();
  const classes = addForm.elements.classes.value.split(',').map(c => c.trim().toUpperCase()).filter(Boolean);
  if (!name || classes.length === 0 || !classes.every(c => /^[A-Z]{4}$/.test(c))) {
    statusNode.textContent = 'Enter a group name and one or more four-letter car class codes, such as CCAR.';
    return;
  }
  addForm.reset();
  requestChange({kind: 'car-group.create', name, classes});
});

function stop(message) {
  mode = 'closed'; session = null; auth = null; service = null;
  statusNode.textContent = message;
}

function send(type, payload) {
  window.parent.postMessage({protocolVersion: '0.2', type, id: crypto.randomUUID(),
    timestamp: new Date().toISOString(), sessionId: session, sequence: ++outgoing, payload}, hostOrigin);
}

function acceptContext(payload) {
  if (!Number.isSafeInteger(payload.contextVersion) || payload.contextVersion <= contextVersion ||
      !payload.context || typeof payload.context.environment !== 'string') return false;
  contextVersion = payload.contextVersion;
  statusNode.textContent = 'Connected to the host (' + payload.context.environment +
    '). Sample groups shown. Changes go to the host\'s utilization service.';
  return true;
}

window.addEventListener('message', event => {
  if (!config || mode === 'closed' || event.source !== window.parent ||
      !config.allowedHostOrigins.includes(event.origin)) return;
  const now = Date.now();
  if (now - windowStart >= 1000) {windowStart = now; messageCount = 0;}
  if (++messageCount > 20) {stop('Host message limit exceeded. Reopen this page.'); return;}
  const m = event.data;
  try {
    if (new TextEncoder().encode(JSON.stringify(m)).length > 262144) return;
  } catch (_) {return;}
  if (!exactKeys(m, ['protocolVersion', 'type', 'id', 'timestamp', 'sessionId', 'sequence', 'payload']) ||
      m.protocolVersion !== '0.2' || !uuid.test(m.id) || !uuid.test(m.sessionId) ||
      typeof m.timestamp !== 'string' || !Number.isFinite(Date.parse(m.timestamp)) ||
      !Number.isSafeInteger(m.sequence)) return;
  if (m.type === 'rlab.host.init') {
    if (mode !== 'waiting' || m.sequence !== 0 ||
        !exactKeys(m.payload, ['pageId', 'pageVersion', 'hostApiVersion']) ||
        m.payload.pageId !== pageId || m.payload.pageVersion !== pageVersion ||
        !/^0\.4\.(0|[1-9][0-9]*)$/.test(m.payload.hostApiVersion)) return;
    session = m.sessionId; hostOrigin = event.origin; incoming = 0; outgoing = 0; mode = 'ready';
    send('rlab.page.ready', {pageId, pageVersion});
    return;
  }
  if (m.sessionId !== session || event.origin !== hostOrigin || m.sequence <= incoming) return;
  if (m.type === 'rlab.host.shutdown') {
    if (!exactKeys(m.payload, ['reason']) ||
        !['logout', 'expired', 'revoked', 'suspended', 'context-switch', 'update'].includes(m.payload.reason)) return;
    incoming = m.sequence;
    stop('Host session ended. Nothing more can be saved. Reopen this page to continue.');
    return;
  }
  if (m.type === 'rlab.host.session' && mode === 'ready') {
    const p = m.payload;
    const keys = ['grantedPermissions', 'contextVersion', 'context', 'services', 'theme', 'auth'];
    if (!exactKeys(p, keys) || !Array.isArray(p.grantedPermissions) ||
        !requiredPermissions.every(s => p.grantedPermissions.includes(s)) || !Array.isArray(p.services)) {
      stop('This page needs permission to read and change Utilization 4 groups. Ask the site owner or an administrator.');
      return;
    }
    const found = p.services.find(s => s && s.id === serviceId && /^1\.\d+\.\d+$/.test(s.version) &&
      typeof s.url === 'string' && s.url.startsWith('https://'));
    if (!found || !p.auth || typeof p.auth.accessToken !== 'string') {
      stop('The Utilization 4 service is not available to this page. Ask the site owner to check the service grant.');
      return;
    }
    if (!acceptContext(p)) {stop('Required context is missing.'); return;}
    service = found; auth = p.auth;
    incoming = m.sequence; mode = 'active';
    send('rlab.page.active', {contextVersion});
    return;
  }
  if (m.type === 'rlab.host.auth' && mode === 'active') {
    if (m.payload && typeof m.payload.accessToken === 'string') {auth = m.payload; incoming = m.sequence;}
    return;
  }
  if (m.type === 'rlab.host.context.changed' && mode === 'active') {
    if (!exactKeys(m.payload, ['contextVersion', 'context'])) return;
    if (acceptContext(m.payload)) incoming = m.sequence;
  }
});

render();

// A host serves its reviewed configuration at this reserved path. When the
// file is absent (the page was opened directly), stay in sample mode.
fetch('/__rlab/host-config.json', {credentials: 'omit', cache: 'no-store', redirect: 'error'})
  .then(response => {if (!response.ok) throw new Error('Configuration missing'); return response.json();})
  .then(value => {
    if (!exactKeys(value, ['allowedHostOrigins', 'pageId', 'pageVersion']) ||
        value.pageId !== pageId || value.pageVersion !== pageVersion ||
        !Array.isArray(value.allowedHostOrigins) || value.allowedHostOrigins.length === 0 ||
        !value.allowedHostOrigins.every(origin => {
          try {const u = new URL(origin); return u.protocol === 'https:' && u.origin === origin &&
            !u.username && !u.password && origin !== window.location.origin;} catch (_) {return false;}
        })) throw new Error('Invalid configuration');
    config = value; mode = 'waiting';
    statusNode.textContent = 'Connecting to the host. Sample groups shown until the session starts.';
    setTimeout(() => {
      if (mode === 'waiting' || mode === 'ready') stop('Host connection timed out. Reopen this page.');
    }, 10000);
  })
  .catch(() => {mode = 'sample';});
