# Host RevenueLab Pages in your system

**Draft Standard 0.2 | For RateHighway and other software companies**

## 1. What your company implements

Implement an import/approval console, artifact registry, isolated page server, workspace shell, message protocol, scoped gateway, audit service and operational controls. These can reuse your identity, API and support infrastructure. An iframe by itself is not a RevenueLab host.

For RateHighway, the host product is RME Custom Pages; RME remains authoritative for identity, tenant rights, business rules, integrations, approvals and audit. Other companies enforce equivalent boundaries within their own systems. They do not need to buy or embed RME to host a page. They cannot claim RME data access or operational equivalence simply by supporting `.rlab`.

| Layer | Host responsibility | Page responsibility |
|---|---|---|
| Identity | Authenticate user, derive tenant and assignments server-side | Receive opaque context only |
| Installation | Verify publisher, licence, digest, compatibility and administrator approval | Declare needs and support owner |
| Runtime | Isolate, bootstrap, theme and suspend | Render accessible page, follow context and shutdown |
| Data | Authorise each request and apply row/field/location restrictions | Request only granted services and handle denial |
| Operations | Monitor, audit, rollback and revoke | Support calculations, UI and own backend |

Pages MUST NOT bypass the host gateway to call downstream business systems directly. Host adapters may use their existing authorised data infrastructure; the page gets neither database access nor general downstream credentials.

## 2. Publish capabilities

Use `schemas/rlab-host-0.2.schema.json` and the sample capability document. Serve a versioned document through authenticated developer tooling; `/rlab-host.json` is a proposed convention. Include host identity, exact standard versions, profiles, supported protocol version, modes, scopes, context keys, service contract versions, limits and documentation/support URLs.

This public/developer document is an upper bound. The session contains the smaller effective capability set. Do not include credentials, tenants, user records or an unearned badge status. A live host can support only bundle delivery and `context.read`, but must still implement all core governance/runtime controls. Disclose the supported profile in the badge evidence record.

Required service contract comparison is by exact ID and numeric version range. Before a data service is advertised, publish its request and response schemas, scope mapping, units, freshness, pagination, allowed filters, quotas, error codes and business meaning. Do not falsely map an incompatible vendor dataset to a shared service. Missing required services stop launch; optional services produce a supported fallback.

## 3. Secure import and deployment

Use offline checks as the first gate, not the last. Verify archive structure in a restricted worker; scan secrets, malware and dependency inventory; reject package build scripts. Resolve publisher identity through onboarding or a trusted distribution account, not a reverse-domain ID typed into JSON. Bind the submitted archive digest to that account and audit the association. Package signing remains a separate design decision; SHA-256 detects change but not authorship.

Store bytes immutably outside the main application server. Deploy compiled app files only, with fixed MIME mapping and no executable server-side handlers. Deploy each tenant/page installation on its own untrusted-content origin, separate from the host and from other tenants/pages. Versions may use separate origins as an additional boundary. An independent registrable domain is preferred to avoid parent-domain cookie exposure; never send host cookies to page origins. Host sessions should use host-only cookies.

No approved artifact changes in place. A host-generated configuration endpoint is outside the package digest and controlled by the deployment service. This draft uses `GET /__rlab/host-config.json` on each installation origin to return exactly `allowedHostOrigins`, `pageId` and `pageVersion`. The host verifies the configuration against the approved registry before launch. It contains no token or tenant data. The publisher supplies equivalent reviewed configuration for remote pages. Packages cannot overwrite this reserved route. This solves parent-origin discovery without trusting an arbitrary URL parameter or referrer.

## 4. Isolation and browser policy

Use `<iframe sandbox="allow-scripts allow-same-origin" title="...">` ONLY on the separate untrusted page origin. `allow-same-origin` preserves a real origin for exact-origin messaging; it does not make that different origin equal to the parent. Never use this combination for page content hosted on the main application origin. Do not add forms, popups, downloads, top navigation or storage-access privileges in this profile.

Example response policy for a bundle (replace both example origins with reviewed values; this is a template, not a universal header):

```http
Content-Security-Policy: default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; font-src 'self'; connect-src 'self' https://gateway.host.example; base-uri 'none'; object-src 'none'; frame-src 'none'; worker-src 'none'; form-action 'none'; frame-ancestors https://app.host.example; sandbox allow-scripts allow-same-origin
Referrer-Policy: no-referrer
X-Content-Type-Options: nosniff
Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=()
```

Set policies as response headers, not just HTML meta tags. Only serve approved assets/configuration on the page origin; `self` is not permission to expose arbitrary storage or credential endpoints. For approved external processing, derive extra `connect-src` entries from the reviewed installation, never untrusted runtime input. Remote pages require equivalent publisher-controlled response headers and ongoing checks. Do not claim an embedding host can enforce arbitrary response headers on someone else's server.

CSP and sandboxing reduce attack surface; they do not prove that hostile code cannot leak data, including through navigation. Use minimal data disclosure, reviewed code, monitored remote deployments and contractual controls. No cross-browser universal egress guarantee is claimed. Suspension/revocation protects future requests; it cannot recall data already delivered.

## 5. Host/page protocol 0.2

All envelopes contain `protocolVersion: "0.2"`, `type`, UUID `id`, ISO UTC `timestamp`, a cryptographically random `sessionId` (at least 128 bits), and a payload. After init, each sender includes its own strictly increasing integer `sequence` starting at 1. Initialise sequence to 0 for init. Receivers reject unknown message shapes, wrong session, duplicate/out-of-order sequence, unknown types and messages over 256 KiB. Limit ingress to 20 messages/second per page; sustained violation closes the session. Enforce state transitions rather than trusting timestamps for replay prevention.

| Message | Direction/state | Required payload |
|---|---|---|
| `rlab.host.init` | Host → loaded page | `pageId`, `pageVersion`, `hostApiVersion`; no token or business data |
| `rlab.page.ready` | Page → host after verified init | Exact `pageId`, `pageVersion` |
| `rlab.host.session` | Host → ready page | `grantedPermissions`, `contextVersion`, `context`, `services`, `theme`; optional `auth` only for authorised API use |
| `rlab.page.active` | Page → host after validating session | Accepted `contextVersion` |
| `rlab.host.context.changed` | Host → active page | New `contextVersion`, full permitted context snapshot |
| `rlab.page.auth.refresh` | Active page → host | Empty object; existing session identity is authoritative |
| `rlab.host.auth` | Host → active page | Fresh restricted auth object after server-side reauthorisation |
| `rlab.page.error` | Page → host | Safe `code`, `message`, `traceId`; no data or tokens |
| `rlab.host.shutdown` | Host → page | `reason` enum: logout, expired, revoked, suspended, context-switch, update |

Only `context.changed` is a manifest business/context subscription. Auth and shutdown messages are compulsory control-plane messages regardless of manifest event declarations. A no-API page does not receive an access token and need not request refresh. A host must support refresh for authorised API pages.

Sequence:

1. Host authorises launch, creates iframe and binds expected origin, window reference, digest and random session ID.
2. Page loads trusted deployment configuration and registers its message listener. The host sends init after frame load. If configuration is still loading the page queues only an init candidate, then validates it against configuration before accepting it. Alternatively the host retries the same non-sensitive init until ready. Duplicated init must not reset an established session.
3. Page checks `event.source === window.parent`, exact `event.origin` against deployment allowlist, expected page ID/version and protocol. Host checks page messages with `event.source === iframe.contentWindow` and exact installed origin. Both validate fields before use. No `*` target origin and no acceptance of `null` origin.
4. Page returns ready to the verified host origin. Host checks ready payload and sends the initial authorised session. A page must refuse a session missing its required permissions or context. After accepting it, the page sends `rlab.page.active` with the accepted contextVersion; the host verifies it matches the issued context.
5. Host ends bootstrap after 10 seconds if `rlab.page.active` is not received. Show a recoverable error outside the frame. Do not send repeated credentials to an unready page.
6. Context changes abort outstanding requests, clear stale displays and increment contextVersion. Tag outgoing requests and responses with contextVersion; discard old responses. A change of tenant/user terminates the old session and recreates the frame and authorisation instead of patching identifiers in place.
7. On logout, expiry, navigation, suspension or revocation, invalidate the gateway session before sending shutdown, then destroy the iframe. A malicious page may ignore shutdown; server enforcement is mandatory. On frame navigation/load after activation, revoke the session and reauthorise, never reuse the token.

Bootstrap example (identifiers illustrative):

```json
{"protocolVersion":"0.2","type":"rlab.host.init","id":"77ee2d7b-9dba-4608-8877-de06d84953c0","timestamp":"2026-10-02T00:00:00Z","sessionId":"9775fc86-408c-4a1e-94e0-737a654b5506","sequence":0,"payload":{"pageId":"com.example.fleet-pressure","pageVersion":"0.1.1","hostApiVersion":"0.2.0"}}
```

`theme` contains only allowlisted primitive tokens (`mode`, `surface`, `text`, `accent`), with mode light/dark and colours restricted to six-digit hex. Never inject arbitrary CSS/HTML from messages. `services` contains only reviewed endpoint descriptors and exact schema versions. `auth` contains `accessToken`, `expiresAt`, `audience`, `gatewayOrigin`; keep it in memory, never URLs, storage, logs or analytics. Business data is not transferred in error messages.

## 6. Gateway and data contracts

Reuse host authentication server-side. Issue short-lived tokens restricted to the gateway audience and installation, digest/version, session, tenant, user, effective scopes and locations. Initial design target: at most five minutes, with refresh through the host session. Gateway checks an active registry/session record every request so revocation does not wait for token expiry. If authoritative policy cannot be checked, deny rather than use stale grants. Do not pass a general host login token to the page.

Validate issuer, signature/key rotation, audience, expiry and current grants. A tenant ID in a query or opaque page context never overrides trusted server claims. Enforce object-level, field-level and location access in the service itself. CORS allowlists exact page origins, but CORS is not authorisation. Browser requests use bearer tokens with credentials omitted; no ambient session cookies. Set sensitive response cache policy to `no-store`; internal caches must key tenant, user/grants, installation and filters.

A service descriptor specifies contract ID/version and a reviewed HTTPS query URL on the authorised gateway. The gateway maps a contract to its adapter; do not build an arbitrary URL forwarding proxy. Each contract must pin the allowed HTTP method, request schema and read-only meaning. Using POST for a read query is not permission to perform a write. Native database schemas and credentials stay behind the adapter.

Minimum successful response envelope:

```json
{"schemaVersion":"0.2","contextVersion":1,"asOf":"2026-10-02T00:00:00Z","data":[],"meta":{"partial":false,"warnings":[],"nextCursor":null},"traceId":"opaque-trace-id"}
```

`asOf` is a response snapshot time; domain records carry source observation/coverage times. Never silently re-label stale data as current. Use bounded opaque cursors bound to tenant and filters. Default query limits to publish in the selected service contract: 100 rows/page, maximum 1,000; 10-second interactive timeout; 1 MiB response cap; 60 requests/minute per installation/user. These are draft defaults, not a promised SLA. Larger work needs a separately defined asynchronous export contract.

Error envelope: `{ "error": { "code": "FORBIDDEN", "message": "This data is unavailable for this page.", "retryable": false }, "traceId": "..." }`. Use 400 invalid input, 401 expired/invalid token, 403 policy denial, 409 stale context, 429 quota with Retry-After, 503 unavailable. Do not leak other tenants' object existence. Retry only safe read queries, with bounded backoff and cancellation.

## 7. Host evidence and operations

Test a matrix with tenant A/user A, tenant A/restricted user and tenant B. Attempt forged IDs, location escalation, stale grants, wrong token audience, old version/digest, revoked session and cache leakage. Every attempt must be denied server-side. Test wrong parent/frame origin, sibling frame spoofing, repeated init, stale sequence, unexpected navigation, blocked network and a noncooperating page after suspension.

Record installation, approval, permission changes, launch, service calls, denial, update, rollback, suspension and uninstall with host/tenant/page/version/user references, trace and timestamp. Avoid request bodies, personal data and confidential calculations in logs. Restrict publisher diagnostics to their installations and redact customer identifiers.

Maintain emergency disable, incident contact, tested restore/rollback, key rotation, patch management and retention policy. Show publisher support separately from host support. Billing outages and licence expiry must not leave undocumented data access or silently remove customers' authorised exports; define those outcomes in commercial terms, outside the package standard.

## 8. Implementation sequence and release gates

| Phase | Deliverable | Exit evidence |
|---|---|---|
| Contract | Adopt draft, threat model and ownership; pin schemas | Architecture/security review; named service contracts |
| Local alpha | Importer, registry, two-origin shell and synthetic page | Package and protocol negative tests |
| Authorised pilot | Scoped gateway, admin consent, audit and revocation | Cross-tenant denial and rollback demonstrated |
| Host conformance | Two independently built pages; support and accessibility | All mandatory host tests pass, evidence reviewed |
| Remote extension | Publisher hosting review, drift detection and suspension | Remote controls tested separately |
| Production | Operational review and explicitly authorised release | No unresolved critical control failures |

RateHighway and another independent vendor should run the same page artifact against compatible mock contracts to prove portability. Until then, portability is the design target, not a demonstrated product capability. No dates, partner commitments or implementation estimates are implied.
