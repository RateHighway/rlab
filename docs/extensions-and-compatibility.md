# Extend .rlab and state compatibility precisely

An expandable ecosystem needs a stable shared meaning and room for
independent implementation. Keep the common core small. Publish new
capabilities as named, versioned contracts, and make host-specific
requirements explicit.

Independent hosts can use their own identity, broker, adapters and customer
permissions. An RME purchase remains unnecessary. The official ecosystem now
requires central registration and deployment reporting through
[`RLAB-CENTRAL-ADMISSION-1`](central-registration.md), including official and
RateHighway-approved hosts. This changes the earlier decentralized operational
direction. Access to business data and operated services remains a separate
entitlement and authorization decision.

Apache-2.0 reuse rights are unchanged. This operational policy cannot require
every independent implementation or fork to report, or establish visibility
into unreported use.

## Separate the contracts

| Contract | What its version describes |
| --- | --- |
| Repository release | A particular collection of published specifications, schemas, tools and examples |
| Standard version | The package format and common rules, such as `"0.2"` |
| Profile | A bounded grammar and required behavior, such as `RLAB-PAGE-READONLY-0.2` |
| Host API | The runtime conversation an application implements, such as `0.2.0` |
| Service or UI contract | The meaning of a named operation or component |
| Page version | The builder's own package release |
| Central admission overlay | Registration, current host permission, deployment purpose/approval and lease requirements for official participation |

The browser bridge's protocol string `"0.2"` and host API version `"0.2.0"`
are different fields. Preserve the supplied values and compare according to
the selected contract. Changing a filename or standard version does not
convert a package into another profile.

## Respect current extension boundaries

Draft 0.2 allows dotted, namespaced keys in its `extensions` metadata object.
That metadata is nonessential: it cannot add permissions, hidden execution
requirements or required runtime behavior. The manifest is otherwise closed,
and unknown scopes are rejected. Versioned service declarations are a
separate mechanism.

Draft 0.3 uses a closed `design-only` manifest and component grammar. It can
refer to versioned named query/action contracts in the synthetic catalogue.
It has no generic manifest extension field, arbitrary custom components or
general expression language. Every declared placement is required in this
preview. Its bounded workflow design supports query, action and approval
steps in a directed acyclic graph, not arbitrary loops or branching.

These boundaries prevent a host from silently interpreting unknown data as
code or authority. Do not weaken a schema or put executable behavior inside
metadata to bypass them. A new runtime feature requires an explicitly
versioned profile/schema and corresponding implementation tests.

The central overlay does not amend either existing manifest schema. Keep
registration and deployment records in their central paths instead of adding
admission fields to `rlab-page.json`. A central record cannot make an
unsupported capability portable or turn the design-only 0.3 profile into an
executable display profile.

The overlay also narrows browser admission to bundled delivery. Legacy
remote-URL delivery can pass structural checks but is denied centrally because
its manifest/package hash does not bind future executable responses. Official
hosts serve approved package assets and enforce CSP against external code,
dynamic evaluation and remote imports. Dynamic business data remains under
the host's authorized data contracts and is not retained as page source.

## Specify a reusable capability

For a proposed fleet-summary capability, publish:

- A stable identifier, independent namespace and accountable maintainer.
- A version and compatibility range, with its business meaning.
- Request and response schemas, allowed filters, pagination and limits.
- Permission vocabulary, tenant/location boundaries and data classifications.
- Rentable/committed fleet definitions, coverage and observation-time rules.
- Failure codes, partial/stale behavior and any permitted fallback.
- Synthetic positive and negative fixtures with expected results.
- Rights, support ownership, migration and retirement policy.

Those are requirements for a contract document, not new fields accepted by
the current `.rlab` schemas. A namespace avoids collisions; it does not prove
publisher identity, safety or access rights.

An adapter may map two different backends to the same contract only when
their meanings match. For example, one backend's total fleet may include
out-of-service vehicles while another's rentable fleet excludes them. A
matching `units` field does not resolve that difference.

## Handle required and optional features

Reject a package when a required profile, contract version, permission or
placement is unsupported. Report the missing requirement clearly before
activation.

Optional behavior is permitted only where the selected profile defines its
negotiation and the page has a tested fallback. Absence must not silently
change a calculation, omit a required approval or broaden access. Do not
assume that the current preview grammar expresses the complete future
optional-extension model.

A private extension can remain private, subject to its own distribution
rights. A page requiring it is compatible only with hosts implementing that
contract. Independent implementation is valuable even when a particular page
does not target every host.

For use in a governed host, the page still needs central registration of its
exact compiled package and source ZIP and a matching approved deployment.
Private central storage does not grant permission to upload someone else's
proprietary source. Archive only material the submitter has rights to provide.

## Publish evidence that others can reproduce

State compatibility for a named host release and exact profile. Identify the
suite version or source commit, artifact digest, date, results and tested
limitations. Distinguish these claims:

| Claim | What it establishes |
| --- | --- |
| Offline validation passed | The particular checker accepted the archive or design documents under the rules it implements |
| Central admission checked | Current official registration and deployment records permit the requested host, artifact and purpose within the policy's freshness and lease limits |
| Host compatibility tested | A specified package worked with a specified host release and contract set in documented tests |
| Cross-host portability demonstrated | The same immutable artifact and fixtures produced matching relevant results and denials in identified independent hosts |
| Certification issued | A designated issuer separately assessed and issued a scoped record under an actual certification process |

A schema pass does not prove tenant isolation, correct business calculations,
runtime behavior, publisher identity or a secure deployment. A certification
concept or badge image does not issue a certificate. Describe self-published
evidence as such, and use certification wording only when actually authorized.

An offline central review is not central admission and always leaves
`admissionEligible: false`. Host-reported deployment inventory is evidence of
what cooperating hosts report, not every independent page view. Source and
package hashes also do not by themselves prove a reproducible build between
the two archives.

Online admission additionally requires a successful latest same-commit
`registry-check.yml` push run on official `master`. Git reads disable local
replacement objects. An online display result includes its bounded
`admissionExpiresAt`; consumer caches cannot extend that deadline or substitute
an older successful workflow revision for the current authority check.

## Evolve without replacing released bytes

Publish a proposal with exact contract changes, compatibility analysis,
migration instructions and tests. Seek review from implementers whose
applications differ from the first host. Independent review helps uncover
assumptions hidden in a single adapter or UI.

Keep released specifications, schemas and archives immutable. Correct them
through a new identified release, and publish what changed. Agents should pin
the release or commit and verify artifact digests rather than build against
a moving default branch. A checksum verifies bytes against a chosen record;
trust in the publisher requires provenance as well.

Draft versions remain development contracts. Define stable compatibility and
support promises explicitly when a future profile becomes stable. Keep
current design-only examples identifiable as design-only throughout that
transition.
