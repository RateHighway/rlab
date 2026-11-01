# Host RevenueLab Pages in your application

An independent `.rlab` host lets users build tools against contracts your
application publishes. Your application supplies identity, permissions,
supported display surfaces and authorized data or actions. Its implementation
can use your existing stack; RME and a RateHighway-operated gateway are not
technical prerequisites.

Start with one useful read-only path and synthetic data. This repository
provides contracts and checking tools, not a ready-to-deploy host.

## Choose an explicit profile

The 0.2 browser profile contains a compiled teaching page and an offline
archive validator. It needs an importer, registry, isolated page deployment,
message bridge and operational controls. The context-only sample needs no
data token or gateway query.

The 0.3 declarative profile is design-only. Its `Text`, `DataTable`,
`ActionButton` and `WorkflowButton` documents are checked against a narrow
grammar. To execute a Compose design, define a separate versioned runtime
profile and implement its semantics. Renaming `stage: "design-only"` does not
complete that work.

Publish your actual standard/profile support, host API versions, runtime
modes, context keys, components, query/action contracts and limits. Advertise
only implemented behavior. The effective permissions in a session are a
smaller set than the capabilities a host could potentially provide.

## Build the reusable host layers

| Layer | Responsibility |
| --- | --- |
| Capability catalogue | Describe supported profiles, versions, contracts, limits and meanings |
| Importer | Inspect untrusted archives without running their code |
| Installation registry | Store immutable digests, approvals, assignments and lifecycle state |
| Runtime | Render supported native components or launch an isolated browser page |
| Data/action broker | Recheck current authority and call known adapters |
| Operations | Audit changes, diagnose safely, suspend releases and restore service |

An iframe or JSON renderer implements only one part of this system. Reuse
your existing identity and operational foundations, and keep host-owned
approval controls outside extension-controlled content.

## Import before activation

Receive an archive into a bounded quarantine worker. Calculate its digest;
validate structure, the pinned manifest schema and the exact profile; compare
declared requirements with implemented capabilities. Verify publisher identity
and applicable rights separately. A reverse-domain ID and SHA-256 digest do
not establish authorship.

The draft archive ceilings are 25,000,000 compressed bytes, 100,000,000
expanded bytes, 25,000,000 bytes per file, 2,000 entries, 240-character paths
and a 262,144-byte manifest. A host may publish stricter limits. Enforce
actual expanded-byte, memory, CPU and time limits while reading.

Reject unsafe paths, duplicates, case collisions, links, encrypted entries,
file/directory collisions and prohibited content. Never execute an archive's
build or installation scripts. Offline validation precedes dependency review,
secret/malware checks, browser tests and installation approval.

Preview the exact digest with synthetic data. Store approval for those bytes,
then activate an immutable installation atomically. Stage updates alongside
the current release. Rollback must honor current permissions; it must not
restore revoked authority merely because an older artifact is restored.

## Enforce authority at execution

Derive user and organization identity from the trusted application session.
A tenant identifier supplied by a page is input, not authorization.

Effective access is the intersection of package declarations, installation
grants, current user rights, organization entitlements, location restrictions
and host policy. Evaluate it for every protected request and effect. A
publisher approval or certification cannot grant customer authority.

Map named query/action contracts to known adapters. Define allowed methods,
input/output schemas, filters, limits, errors, units and business meaning.
Do not expose arbitrary URL forwarding, SQL execution or downstream
credentials. Keep service credentials behind your broker.

For rental data, define rentable and committed fleet, observation times,
coverage, vehicle-class mapping, time zones, currency, taxes and fees.
Matching field names do not establish equivalent business semantics. Return
coverage, freshness and warnings with the result; response generation time
does not make old source observations current.

## Render declarative views safely

Validate a component tree before rendering. Accept only implemented types
and properties, escape text, and bound tree depth, node counts, string sizes,
row counts and query cost. Reject raw HTML, executable expressions, arbitrary
CSS and unknown destinations unless a future explicit profile safely defines
them.

The current 0.3 binding grammar accepts supported context keys or literal
strings. It does not compute formulas or reference selected rows and earlier
workflow outputs. Keep required calculations in defined, tested host logic.

Give components loading, empty, denied, partial, stale and error states.
Preserve keyboard navigation, focus, status announcements, zoom and narrow
layouts. Keep publisher identity and the page's limitations understandable.

## Integrate the 0.2 browser sample

Deploy each installation's compiled browser assets on an untrusted-content
origin separate from the main application and other installations. A separate
registrable domain is preferable to avoid parent-domain cookie exposure.
Host cookies must not reach page origins. The teaching sample requires a
distinct HTTPS parent origin.

Serve `GET /__rlab/host-config.json` on that page origin, outside package
control. Derive its exact contents from the approved installation registry:

```json
{
  "allowedHostOrigins": ["https://app.host.example"],
  "pageId": "com.example.fleet-pressure",
  "pageVersion": "0.1.1"
}
```

These are reserved example values, not live endpoints. Replace them with the
reviewed installation values. Include no token, tenant record or business
data. Packages cannot overwrite the reserved configuration route.

Use an iframe with `sandbox="allow-scripts allow-same-origin"` only on the
separate untrusted origin. Set a meaningful frame title and restrictive
response policies. The full [0.2 host protocol and browser
policy](../profiles/browser-readonly-0.2/docs/HOST-INTEGRATION-GUIDE.md)
specifies CSP, framing, MIME, referrer and browser-permission requirements.
Do not grant forms, popups, downloads or top navigation in this profile.

Bootstrap proceeds through four messages:

```text
host -> rlab.host.init
page -> rlab.page.ready
host -> rlab.host.session
page -> rlab.page.active
```

Use protocol string `"0.2"`, the compatible host API version, exact page
identity/version, UUID message IDs and a cryptographically random session ID.
Init has sequence `0`; each sender's subsequent sequence begins at `1` and
strictly increases. Initial `contextVersion` is `1`.

Both sides validate the exact message origin and expected frame-window
source before accepting payloads. Never use `*` as the target origin or accept
`null` origins. Validate envelope shapes, state transitions and replay rules.
Apply a 256 KiB message ceiling, 20 messages per second and a 10-second
bootstrap deadline.

The sample fetches its configuration asynchronously and ignores init while
that configuration is unavailable. The host may retry the same non-sensitive
init until ready, then stop. An init retry must never reset an established
session or resend credentials to an unready frame.

For this specific sample, issue exactly `context.read`, an empty `services`
array, the required environment context, context version and theme. Omit
`auth`: it has no API calls and accepts no token in its initial session.
The sample's exact session shape is implemented in
[`app/assets/page.js`](../profiles/browser-readonly-0.2/examples/fleet-pressure/app/assets/page.js).

For later data-enabled pages, implement the full protocol and scoped gateway.
Keep any page access token short-lived, in memory, restricted to the gateway
audience and bound to installation, digest, session, user, tenant and effective
grants. Never provide a general host login token. Recheck active registry and
session state on every gateway request so revocation does not wait for expiry.

## Manage context and lifecycle

Increment `contextVersion` on a working-context change. Cancel outstanding
requests, clear inappropriate results and discard responses for the old
version. A user or tenant change terminates the old session and requires fresh
authorization and isolation.

Suspension denies future launch and protected requests at the server. Revoke
the session before sending shutdown and removing the frame. Unexpected frame
navigation also ends the session. A malicious page can ignore shutdown; it
cannot be the enforcement mechanism. Revocation cannot recall data already
delivered.

Audit installation, grants, activation, launch, denial, update, rollback,
suspension and uninstall using safe identifiers and trace IDs. Avoid tokens,
personal records and unnecessary business payloads in logs. Define support,
incident response, emergency disable, retention and tested recovery.

## Add higher levels as separate engineering work

Level 2 needs host-owned preparation, impact preview and approval where
required, followed by commit and result tracking. Bind approval to exact
inputs and targets; reauthorize at commit; make retries idempotent. Queue
acceptance is not completion.

Level 3 needs durable state, checkpoints, deadlines, recovery after worker
restarts and reauthorization at each effect. Unknown outcomes pause for
reconciliation. Level 4 adds verified unattended triggers and a separate
mandate with an accountable owner, bounded scope, limits, expiry and disable
controls. Begin with shadow execution. A browser timer is not an authorized
scheduler.

The supplied 0.3 examples describe these abilities but implement none of
those runtime facilities.

## Prove the integration

Test allowed and restricted users in two synthetic tenants. Attempt forged
IDs, location escalation, stale grants, wrong token audiences, changed
digests, revoked sessions and cache leakage. Test wrong frame sources and
origins, repeated sequences, context races and a noncooperating suspended
page. Include accessibility and operational recovery.

Record the host release, exact profile, package digest, test suite and known
limitations. Use two independently authored pages to check that your host's
contract is sufficient. To demonstrate cross-host portability, test the same
immutable package and synthetic fixtures in a second independently
implemented host. Matching results and denials support the tested scope;
they do not establish universal portability or issue certification.
