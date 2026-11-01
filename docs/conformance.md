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
| Release builder | Fresh package artifacts and check reports; source and artifact digests | A public release, a signature from an external trust authority or a certified host |

The profile checkers implement the pinned schema subsets they need. They are
not general-purpose JSON Schema engines. `offline-passed` and `design-checked`
describe those specific checks.

## Host implementation evidence

Before accepting real data or actions, a host team must demonstrate the
requirements of its selected profile in its own environment. For the browser
profile, test exact origin and frame-source checks, bootstrap ordering,
session/sequence handling, context changes, resource isolation and denied
requests. Test the deployed response headers and alternate serving paths.

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
