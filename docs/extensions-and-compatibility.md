# Extend .rlab and state compatibility precisely

An expandable ecosystem needs a stable shared meaning and room for
independent implementation. Keep the common core small. Publish new
capabilities as named, versioned contracts, and make host-specific
requirements explicit.

Independent hosts can use their own identity, broker, adapters and customer
permissions. Supporting `.rlab` does not require an RME purchase or a central
RateHighway service. Access to a particular operated service remains a
separate admission, entitlement and authorization decision.

## Separate the contracts

| Contract | What its version describes |
| --- | --- |
| Repository release | A particular collection of published specifications, schemas, tools and examples |
| Standard version | The package format and common rules, such as `"0.2"` |
| Profile | A bounded grammar and required behavior, such as `RLAB-PAGE-READONLY-0.2` |
| Host API | The runtime conversation an application implements, such as `0.2.0` |
| Service or UI contract | The meaning of a named operation or component |
| Page version | The builder's own package release |

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

## Publish evidence that others can reproduce

State compatibility for a named host release and exact profile. Identify the
suite version or source commit, artifact digest, date, results and tested
limitations. Distinguish these claims:

| Claim | What it establishes |
| --- | --- |
| Offline validation passed | The particular checker accepted the archive or design documents under the rules it implements |
| Host compatibility tested | A specified package worked with a specified host release and contract set in documented tests |
| Cross-host portability demonstrated | The same immutable artifact and fixtures produced matching relevant results and denials in identified independent hosts |
| Certification issued | A designated issuer separately assessed and issued a scoped record under an actual certification process |

A schema pass does not prove tenant isolation, correct business calculations,
runtime behavior, publisher identity or a secure deployment. A certification
concept or badge image does not issue a certificate. Describe self-published
evidence as such, and use certification wording only when actually authorized.

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
