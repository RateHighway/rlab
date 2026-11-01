# Central registration and host admission

The official RevenueLab ecosystem uses **`RLAB-CENTRAL-ADMISSION-1`** as a
mandatory admission policy for governed hosts. Before a host installs,
enables or renders a page, its exact package must be registered centrally and
the host must have a current approved deployment record for that use.

The public `RateHighway/rlab` repository holds the format, schemas, reference
tools and guides. The private **`RateHighway/rlab-pages`** repository is the
central source/package archive and deployment inventory. These are separate
repositories with separate access controls. Public access to the specification
does not grant read or write access to the private archive.

This policy changes the earlier operational direction that a host could join
the official ecosystem without central registration. An RME purchase is still
unnecessary. Hosts keep their own application stack, identity, broker,
customer authorization and business rules, while central registration and
deployment reporting are required for official participation.

Apache-2.0 reuse rights remain in force. The policy can govern official and
RateHighway-approved hosts; it cannot make every independent implementation
or fork report its activity. Central records provide visibility into reporting
hosts, not universal observation of every use of the format.

## Two layers of validation

Structural checking and central admission answer different questions:

| Layer | Question |
| --- | --- |
| Profile checks | Does this archive or design satisfy the implemented checks for its declared profile? |
| Central admission | Are these exact bytes registered, currently permitted for this host and bound to an approved, active, unexpired deployment for the requested purpose? |

`RLAB-CENTRAL-ADMISSION-1` is an overlay. It adds no fields to the closed
Draft 0.2 or 0.3 page manifests and does not weaken unknown-field rejection.
Existing `offline-passed` and `design-checked` results remain structural
evidence. They do not grant admission.

Draft 0.3 remains design-only. A centrally registered and approved 0.3 package
can be admitted for **design review**, never for **display** under this
overlay. Registration does not create an executable renderer or change
`stage: "design-only"`.

For the browser profile, central admission accepts **bundled delivery only**.
The legacy structural schema also describes remote-URL delivery, but that
mode is denied by this overlay: hashing a manifest or wrapper does not bind
the executable bytes that a URL may serve later. Serve executable assets from
the exact centrally approved package digest.

The host must use enforced response policies, including CSP, to prevent
external executable code, dynamic `eval`/`Function` execution and remote code
imports. Do not fetch replacement scripts after approval. Dynamic business
data remains data obtained through the host's authorized adapters; customer
records, returned query results and page-view activity do not belong in the
central source/package archive.

## Register immutable package and source bytes

The central archive uses these paths:

```text
registrations/<pageId>/<pageVersion>.json
packages/<packageSha256>.rlab
sources/<sourceSha256>.zip
deployments/<deploymentId>.json
```

Angle-bracket values describe path components, not literal filenames. A
registration identifies one page ID/version and binds it to exact compiled
`.rlab` package bytes, exact source ZIP bytes and a profile. Keep those digest
bindings immutable. Changed package or source bytes need a new page version
and registration rather than replacement under an existing identity.

| Registration field | Meaning |
| --- | --- |
| `recordVersion` | Central registration record format, currently `1` |
| `pageId`, `pageVersion` | Identity and version matching the package manifest |
| `profile`, `standardVersion` | Declared profile and standard version matching that package |
| `packagePath`, `packageSha256` | Content-addressed compiled package path and SHA-256 |
| `sourcePath`, `sourceSha256` | Content-addressed source ZIP path and SHA-256 |
| `status` | `registered` or `revoked` |
| `allowedHosts` | Specific host installation identifiers permitted to use the registration |
| `registeredAt` | Registration timestamp in UTC |

Record timestamps use whole-second UTC form `YYYY-MM-DDTHH:MM:SSZ`, without
fractional seconds or numeric timezone offsets.

Status and host permissions are mutable policy maintained through reviewed
Git commits. Revocation and host removal must remain possible without
changing the immutable artifact bindings. An empty `allowedHosts` list grants
no host permission.

Upload only material the submitter has rights to place in the central archive.
Include build instructions, dependency versions and applicable licenses in
the source submission. The source ZIP must include a root `rlab-page.json`
whose page identity, version, profile and standard version match the package.
Exclude credentials, customer records, personal data
and environment secrets from both archives. Storing source centrally does not
relicense an author's independent work.

A source ZIP digest identifies the archived source bytes. It does **not**
prove that the compiled package was built from them. Source-to-package build
correspondence needs separate build provenance or a reproduced build and
review. The central validator must not advertise that unperformed assurance.

## Report each deployment

Registration alone does not identify where a page is being used. A governed
host also writes a deployment record for each installation and placement.
`hostId` identifies a specific host installation, not merely the software
vendor or product family.

| Deployment field | Meaning |
| --- | --- |
| `recordVersion`, `deploymentId` | Record format `1` and the identifier matching its deployment path |
| `hostId`, `hostRelease` | Specific installation and its application/runtime release |
| `applicationName`, `environment` | Application and operating environment reported by the host |
| `placement.route`, `placement.slot` | Stable route and display or review slot within that application |
| `pageId`, `pageVersion`, `packageSha256` | Exact registered page identity, version and package SHA-256 |
| `purpose` | `display` or `design-review` |
| `status` | `active` or `disabled` |
| `approval` | `approved`, `pending` or `denied` |
| `reportedAt`, `leaseExpiresAt` | UTC report time and lease expiry; the lease may span at most 24 hours |

Use stable operational placement identifiers. Do not put customer-specific
routes, reservation identifiers, query-string data or user identities into
these records. This inventory reports application deployment, not individual
visitors or page views.

Hosts report enable, update and disable transitions centrally and renew active
leases. A page version update must bind the new digest and obtain the required
approval before activation. Pending or denied approval cannot authorize use.
An expired lease cannot be treated as evidence of an active deployment.

Authorized central reviewers control registration permission and deployment
approval. A host report or proposed record does not authorize the host to add
itself to `allowedHosts` or approve its own use. The validator needs read
access to the central archive; reporting writes need a separately controlled
workflow. No per-host write enforcement or reporting API is supplied merely
by defining these JSON records.

The central archive initially contains five reference registrations with no
allowed hosts and no deployment records. These are reference artifacts, not
evidence of live host installations or active pages.

## Run the central validator

An authorized operator obtains a checkout of the private archive and has
Git and authenticated GitHub CLI available to read the official repository.
Run the validator from the public specification repository:

```sh
python -B tools/validate_registered_page.py PACKAGE --registry PATH --host-id ID --deployment-id ID --host-release RELEASE --environment ENV --route ROUTE --slot SLOT --purpose display
```

Replace the capitalized values with the actual package, private registry
checkout, specific host installation, deployment record, runtime release,
environment, route and slot. `ENV` must be `development`, `staging` or
`production`; `ROUTE` is a path such as `/tools/fleet-pressure`. These are
command syntax variables, not supplied live records. Derive context from
host-controlled release identity and routing, not from a page's assertions.
For a design-only 0.3 package, request `--purpose design-review` instead.

By default the tool checks the current official `master` head of
`RateHighway/rlab-pages` through the GitHub API. The latest `push` run of
`registry-check.yml` for that same commit on `master` must be completed with
conclusion `success`. A missing, pending or unsuccessful run denies online
admission. The registry workflow checks retention policy and immutable
registration history using pinned policy tooling; an older successful
revision cannot approve the current head.

The tool verifies that the clean checkout and relevant files correspond to
that commit using Git with `--no-replace-objects`, so local replacement refs
cannot substitute a different tree for the official commit. It then
checks package and source digests, registration state, host scope, deployment
binding, exact release/environment/route/slot context, approval and lease.
A local folder named like the official repository
or a copied record by itself is not current central authority.

Read the result's `centralPolicy`, `purpose`, `admissionEligible` and
`designReviewEligible` fields,
along with the profile and reasons. For a per-package check, exit `0` can represent a successful online
display check or a successful design review. Online design-review success has
`designReviewEligible: true` and `admissionEligible: false`; it does not make a
0.3 design eligible for display. Exit `1` denies the requested check. Exit `2` is offline
review evidence only.

Online display success returns `checkedAt` and `admissionExpiresAt`. The
deadline is the earlier of the authority check time plus 15 minutes and the
deployment lease expiry. Hosts must honor the returned deadline; a cache hit,
page reload or local retry cannot restart or extend it. Offline checks issue
no admission expiry or display grant. Design-review success remains
`admissionEligible: false` and supplies no display admission expiry.

```sh
python -B tools/validate_registered_page.py PACKAGE --registry PATH --host-id ID --deployment-id ID --host-release RELEASE --environment ENV --route ROUTE --slot SLOT --purpose design-review --offline
```

`--offline` always reports `admissionEligible: false`. It can support review
of a saved snapshot but cannot approve installation, enablement or rendering.
Do not turn an unavailable network check into an offline admission bypass.

### Audit retained records without requesting admission

To audit the archive and inventory as retention evidence, omit the package
and deployment arguments:

```sh
python -B tools/validate_registered_page.py --registry PATH --audit-registry --offline
```

A successful audit exits `0` with `status: "registry-audited"`, record counts
and `admissionEligible: false`. It checks committed registration identities,
retained package/source bindings and deployment record consistency. It can
include revoked registrations and historical or expired deployment records.
The counts are retained records, not a claim that those pages are active.

This audit does not verify the current official remote head or request a
particular host's admission. Its success cannot replace the online per-package
check. Normal per-package `--offline` review still exits `2` on successful
evidence checking and always leaves admission false.

GitHub credentials belong on the host server or authorized operator's machine.
Never put them in page packages, source ZIPs, browser host configuration,
iframes, query strings or client-side bundles. A specification download and a
structural fixture check do not require private-registry credentials.

## Enforce admission in the host

The command-line validator supplies reference checking; it is not the host's
runtime gate. A governed host must implement enforcement at installation,
enablement and render admission and must keep checking active deployments.

1. Quarantine the exact package and run its structural/profile checks.
2. Verify current central authority and the matching registration, host
   permission, deployment record, purpose, approval and lease.
3. Apply the host's publisher review, isolation and customer authorization.
   Central permission cannot grant access to an organization's data.
4. Supply trusted host release/environment/route/slot context for exact
   comparison with the deployment record, and verify its `applicationName`
   against the actual application. Activate only the approved immutable digest
   in that context. The CLI compares supplied context with the stored record;
   it cannot independently observe the application's actual running state.
5. Refresh the current official head and its successful current policy run
   before `admissionExpiresAt`, and at least every 15 minutes. Cached central
   authority must not remain valid for more than 15 minutes without a
   successful refresh. Do not extend a returned deadline locally. The
   deployment lease must also remain valid; its maximum 24-hour span does not
   extend this shorter refresh limit.
6. Stop use on revocation, removed host permission, disabled or unapproved
   deployment, digest mismatch or lease expiry. Fail closed when central
   authority cannot be refreshed within the 15-minute limit. Deny new
   admissions and stop affected active rendering and protected operations.
7. Report lifecycle changes and renew leases through the central workflow.

Use server-side enforcement and terminate page sessions when authority ends.
An uncooperative browser page can ignore a shutdown message; that message
cannot be the access-control boundary. Revocation also cannot recall data
already delivered.

The private repository and its reviewed commits provide an initial record and
control mechanism. Publication of these contracts and tools does not deploy
that host enforcement, a central service API or automatic lifecycle reporting
inside another application.

## Visibility and evidence

The central inventory can answer which registered page bytes are reported by
which cooperating host installations, at which routes/slots, for which
purposes and with which current lease and approval state. Keep archived
history separate from current active status.

These are host-reported deployment records. They are not proof that every
page view occurred, that every independent fork reports usage, that a source
archive produced the compiled bytes, or that a host passed a security or
certification assessment. Publish claims with those limits.

See [host integration](host-integration.md), [conformance](conformance.md) and
[extensions and compatibility](extensions-and-compatibility.md) for the other
requirements that remain necessary after central admission.
