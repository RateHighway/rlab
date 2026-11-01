# RevenueLab Page Package Standard

**Draft Standard 0.2 | 2026-10-02 | Public source edition 2026-10-31**

## 1. Contract and scope

A RevenueLab Page is a versioned micro-application installed into an authorised host. A `.rlab` file is its portable installation package. Installation is a reviewed registry transaction, never execution of an installer script. The page declares its requirements; it cannot grant itself access.

The standard defines packaging and a host contract. APIs provide services. MCP makes documentation, schemas and approved workflows accessible to agents. RevenueLab teaches and distributes building patterns. A host supplies the governed runtime. Any company may implement the draft; commercial access, API rights and badge authorisation are separate.

MUST/MUST NOT are requirements of this draft. SHOULD allows a documented equivalent control. First profile: `RLAB-PAGE-READONLY-0.2`. Full-page workspace only; no rate changes, operational writes, personal reservation data, arbitrary server execution or direct database access. Any future action profile needs its own contract and conformance tests.

## 2. Versions and compatibility

Keep three versions separate: `standardVersion` (package contract), `hostApi` (runtime protocol range), and `version` (publisher's page release). This draft uses standard `0.2` and host API `0.2.0`. Draft revisions may break compatibility; exact supported standard versions must be advertised. Do not interpret every `0.x` as compatible.

Page releases use numeric `MAJOR.MINOR.PATCH` in this profile. Prerelease and build suffixes are deliberately excluded to keep ordering unambiguous in the reference validator. Never replace bytes for the same publisher/page/version. Use a new version and SHA-256 digest. An increase in permissions, external processing, required data or network origins always triggers fresh approval regardless of version number.

## 3. Container

ZIP with extension `.rlab`. Working media type `application/vnd.ratehighway.rlab+zip`, not an assertion of IANA registration; `application/zip` is a fallback. UTF-8 JSON and relative POSIX paths; this narrow profile accepts ASCII filenames for predictable cross-platform validation.

| Path | Requirement |
|---|---|
| `rlab-page.json` | Exactly one manifest at archive root |
| `app/index.html` | Example entry; bundle mode must point to an existing HTML file under `app/` |
| `app/assets/` | Bundled CSS, JS and passive assets; no CDN executable dependencies |
| `README.md` | Purpose, inputs, outputs, limitations and support |
| `LICENSE.txt` | Actual applicable terms or an explicit rights-pending notice for samples |
| `NOTICE.md` | Third-party attribution when required |
| `docs/` | Optional operating notes |
| `samples/` | Optional synthetic data only |
| `tests/` | Optional inert fixtures; never executed by an importing host |

An authoring repository may contain source code, build scripts, lockfiles, automated tests and screenshots. Ship compiled browser output in `.rlab`; do not ship `node_modules`, `.env`, private keys, build commands or server runtimes. Provide source separately when licensing or customer arrangements require it. Browser code is visible to users.

Limits inherited and made byte-explicit: compressed archive 25,000,000 bytes; total expanded data 100,000,000; single file 25,000,000; 2,000 entries; path 240 characters. Manifest ceiling 262,144 bytes. Hosts may publish stricter limits, not silently weaken the profile.

Reject encrypted entries, links, special files, nested archives, absolute paths, empty/dot/dot-dot path segments, backslashes, duplicate or case-colliding paths, file/directory collisions, drive prefixes, Windows reserved device names and trailing dots/spaces. Allow ZIP stored or deflated entries only. Measure actual bytes while reading and verify CRC. Validate before extraction; never execute package code during validation. Use quarantined workers with CPU, memory, wall-clock and network limits for untrusted archives. A valid ZIP CRC or hash is not proof of a trusted publisher.

## 4. Manifest

`schemas/rlab-page-manifest-0.2.schema.json` is the normative machine-readable manifest definition bundled with this draft. Its schema URI is a proposed identifier, not a working download service. Validators load the pinned local schema; never fetch a package-selected schema URL.

| Field | Meaning |
|---|---|
| `$schema`, `standard`, `standardVersion`, `profile` | Exact contract identifiers |
| `id`, `name`, `description`, `version` | Stable reverse-domain page ID and release metadata |
| `publisher` | Claimed publisher ID/name; identity must be verified outside the archive |
| `hostApi` | Inclusive minimum and exclusive maximum protocol versions |
| `delivery` | `bundle` plus entry, or `remote` plus URL and origin |
| `display` | `workspace`, with declared theme awareness |
| `permissions.requested` | Read scopes the page would like to use |
| `permissions.required` | Subset that must be granted for the page to launch |
| `context.required`, `context.optional` | Supported keys; disjoint lists |
| `services` | Versioned semantic contracts the page uses, each marked required/optional |
| `events` | Subscribe to `context.changed`; no business-event publication |
| `network.connect` | Additional exact HTTPS origins, subject to host approval |
| `dataHandling` | External processing, retention and personal-data declarations |
| `support`, `license` | Accountable owner, URL and declared usage rights |
| `extensions` | Namespaced nonessential metadata; cannot introduce new permissions |

No tenant IDs, user grants, tokens, purchased entitlements, approval status, trust level or certification claims belong in this manifest. These belong to host-controlled records.

Initial scope vocabulary carries forward: `context.read`, `locations.read`, `vehicle-classes.read`, `rate-observations.read`, `own-rates.read`, `utilization.read`, `rate-change-history.read`, `reservation-pace.read`, `alerts.read`. A host need not expose all scopes. It MUST refuse any requested scope unknown to the profile. Known optional but unavailable scopes can be omitted, with a clear install disclosure. Missing required scopes prevent installation/launch. Effective access intersects requested scope, administrator grant, current user rights, tenant entitlement, location restrictions and environment policy on every request.

Service objects use `id`, `minimum`, `maximumExclusive`, `required`. Matching scope names alone is insufficient: a service also needs a versioned data schema and documented semantics. A host MAY provide namespaced services in a separate profile; this draft does not make those services portable or approved. No central service catalogue is claimed to exist yet.

## 5. Delivery

**Bundle:** host validates and stores immutable compiled assets, then serves them from a dedicated untrusted-content origin. No package build/install hooks. Assets are relative. Only allowlisted media are served, with explicit content types and `nosniff`. Root documentation is not an executable application surface.

**Remote:** package registers an HTTPS URL and its exact origin; it does not deploy a backend. URL credentials, query strings, fragments and redirects are prohibited by this profile. Approve a version-specific path and record the publisher's deployment identifier. A URL alone cannot prove immutable code. Remote mode is an optional host capability and requires a separate evidence review for deployment control, headers, data destinations and change detection. Drift suspends the installation pending review. Bundle certification does not imply remote certification.

External backend processing is an optional reviewed extension to the read-only profile. Declare `externalProcessing: true`, origins and actual retention. Authorisation must specify allowed datasets and contractual processing boundaries. A customer's private algorithm can live in its controlled backend; credentials stay server-side. The core sample uses no external processing and no retention. Never imply CSP controls what an authorised backend does after receiving data.

## 6. Install and lifecycle

1. Upload/register to quarantine. Compute whole-archive SHA-256.
2. Validate archive, schema, semantics, dependencies, secrets and policy.
3. Resolve host API, delivery support, required services/context/scopes and licensing.
4. Preview with synthetic or approved test data; complete handshake and failure tests.
5. Show verified publisher, version, digest, permissions, external hosts, retention, support and cost/entitlement if applicable. No price is defined by this standard.
6. Obtain host-operator and tenant-administrator approval under their policy.
7. Atomically activate an immutable deployment with assignments and grants. Audit actor/time/evidence.

Registry states: `draft`, `validated`, `preview`, `approved`, `active`, `rejected`, `suspended`, `retired`. Only approved artifacts can become active. Suspension blocks new sessions and data access immediately at the gateway. Resumption needs a new policy decision; no automatic recovery from security suspension.

Installation key includes host, tenant and page ID. Bind approved digest, publisher identity, page version, grants, locations, users/roles, environment, audit history, data-processing approval and licence entitlement. Updates stage alongside the active version. Rollback rechecks current policy and entitlement; revoked permissions do not return. Uninstall revokes access and removes deployment references and settings according to documented retention, while preserving necessary audit records.

## 7. Portable operating context

Host-supplied keys preserve 0.1 names: tenant, user, roles, locations, rental-period, vehicle-classes, channel, currency, locale, timezone, environment, capabilities. Each message also has a monotonically increasing `contextVersion`. Required keys must exist; optional keys may be absent. Arrays may be empty only when the page supports an unselected state. Opaque IDs have meaning only within a host/tenant. Page-supplied identifiers never select an authoritative tenant.

For rental analysis, use explicit pickup and return timestamps with offsets and IANA timezone, location pair, class mapping, channel, currency, total-versus-daily basis, tax/fee inclusion and observation freshness. Utilization contracts must define numerator, denominator, unavailable units and rental-period coverage. Missing and stale data must remain visible. A field named `rate` or `utilization` is not enough to establish comparability.

## 8. Runtime and certification separation

The host protocol, CSP, gateway and support requirements are in `HOST-INTEGRATION-GUIDE.md`. Package validation, installation permission, commercial entitlement, host certification and page review are five different decisions. None implies the others. RateHighway-maintained, community, compatible, tested and verified must remain distinct labels.
