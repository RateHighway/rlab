# What the checks establish

Conformance means meeting a defined profile's requirements. Compatibility
means that a stated package and host release work together for their declared
contracts. Certification is a separate issued assurance record. These are
different claims.

## Checks supplied here

| Check | Evidence | Does not establish |
| --- | --- | --- |
| Repository check | Local documentation targets, catalog hashes, JSON parsing, source fixture checks and unit tests | External URLs, public GitHub settings or deployed runtime behavior |
| 0.2 archive validator | Implemented package structure, resource/manifest checks and fixture-based host compatibility | Publisher identity, complete secret/malware scanning, browser isolation or data authorization |
| 0.3 design checker | Closed document schemas, bindings, supported synthetic contracts and bounded graph structure | UI rendering, actions, workflow execution, scheduler behavior or automation mandate |
| Online central validator | Current official head with successful latest same-commit registry policy run, registration/deployment binding, digest, permitted host, context, purpose, approval and bounded admission deadline | Customer-data authority, source-to-package build correspondence, host enforcement or certification |
| Offline central review | Evidence from a saved registry snapshot, with `admissionEligible: false` | Installation, enablement or rendering admission |
| Registry retention audit | Committed registration/package/source bindings and deployment inventory consistency | Current remote authority or any host admission; success remains `admissionEligible: false` |
| Release builder | Fresh package artifacts and check reports; source and artifact digests | A public release, a signature from an external trust authority or a certified host |

The profile checkers implement the pinned schema subsets they need. They are
not general-purpose JSON Schema engines. `offline-passed` and `design-checked`
describe those specific checks.

The full repository suite requires Git for local central-registry integration
tests. The profile checkers themselves use Python's standard library only.
Online central admission additionally requires authenticated GitHub CLI access.

The mandatory official-ecosystem overlay
[`RLAB-CENTRAL-ADMISSION-1`](central-registration.md) keeps structural checks
separate from central admission. It does not add fields to existing 0.2/0.3
manifests. A successful design review cannot authorize a design-only 0.3
package for display. Inspect the requested purpose and result fields rather
than treating every exit `0` as display approval.

`--audit-registry --offline` exits `0` on successful retention audit with
`status: "registry-audited"` and admission false. It can inspect historical,
revoked or expired records without approving active use. Successful normal
per-package `--offline` review exits `2` and also leaves admission false.

Online checks require the latest `push` run of `registry-check.yml` for the
official `master` head to be completed successfully. Missing, pending and
failed runs deny admission. Git reads use `--no-replace-objects` so local
replacement refs cannot substitute a different tree for that head.

Browser admission is bundle-only. The legacy schema's remote-URL mode may
pass structural checks but is denied by the central overlay. Hosts must also
enforce CSP against external executable code, dynamic evaluation and remote
imports while serving the exact centrally approved package bytes. Authorized
business data remains separate from retained source/package archives.

## Host implementation evidence

Before accepting real data or actions, a host team must demonstrate the
requirements of its selected profile in its own environment. For the browser
profile, test exact origin and frame-source checks, bootstrap ordering,
session/sequence handling, context changes, resource isolation and denied
requests. Test the deployed response headers and alternate serving paths.

A governed host must also demonstrate admission enforcement before install,
enablement and rendering. Test missing/revoked registrations, package/source
digest mismatch, host allowlist denial, wrong deployment identity or purpose,
host release/environment/route/slot mismatch,
pending/denied approval, disabled deployments, expired leases and failure to
refresh the current official head within 15 minutes. Leases may span at most
24 hours and cannot override the shorter policy refresh bound. Prove that
revocation stops active use and that `--offline` cannot bypass admission.

Check returned `checkedAt` and `admissionExpiresAt` values. Online display
admission expires at the earlier of the authority check time plus 15 minutes
and deployment lease expiry. A consumer cache must not restart that period.
Offline and design-review results contain no display admission expiry.

The private central archive initially holds reference registrations with no
allowed hosts and no deployments. Those records must not be described as live
host installations. Hosts report lifecycle changes; central inventory does
not independently observe every browser render or every fork of the format.

For a future executable declarative profile, establish the actual runtime
contract before implementing it. Use typed host components and named bounded
operations. Permissions must be checked at execution, across tenant boundaries
and after revocation. Human approval, durable recovery and unattended mandates
need separate tests for the levels a host advertises. The design-only profile
does not supply these implementations.

Use synthetic fixtures to compare two independent hosts for a shared profile:
the same artifact digest, expected outputs, permission denials, context changes
and unsupported capability failures. That comparison supports only the tested
scope. It does not prove universal portability.

## Claims

An implementer report identifies the product release, exact profile, package
digest, suite commit, environment, date, results and limitations. Self-testing
is welcome and does not require a paid assessment. Do not label it RateHighway
certification without an actual separately issued certificate.

No host browser, screen-reader, tenant-isolation or production-service tests
are asserted by this repository's source checks. CI runs become evidence only
when the published workflow actually runs and its results are inspected.
