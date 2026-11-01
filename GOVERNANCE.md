# .rlab governance

RateHighway initially stewards the shared core and appoints its maintainers.
This is a company-stewarded public Draft Standard, not a claim of independent
standards-body approval. Independent hosts, proprietary applications and
private extensions are valid participants.

The published license governs reuse rights. A listing, service admission or
certification decision does not revoke those rights. Customer authorization
and RateHighway-operated service admission remain separate from implementing
the format.

## Required central page and deployment records

The official registered-host ecosystem applies `RLAB-CENTRAL-ADMISSION-1`.
Every page release must retain its source archive and exact package in the
private `RateHighway/rlab-pages` repository. Every host placement must have an
approved, current central deployment record before display. See
[central registration](docs/central-registration.md) for the validation and
lifecycle contract.

Maintainers control merges to the central authoritative branch. A submitted
record is not approved merely because it exists in a contributor's checkout.
Package/source digest bindings for one page ID and version cannot change;
revocation, host permissions and deployment state change through reviewed
commits. New bytes require a new page version. Source access and rights remain
limited to the submitting parties' grants; private storage is not a public
license or a certification award.

Hosts report each enable, update and disable, renew bounded deployment leases,
and enforce current central authorization. No customer data, credentials or
individual visitor tracking belongs in those records. Revocation prevents
admission under this policy; it does not cancel Apache-2.0 reuse rights.

This operational requirement supersedes the earlier direction that official
host operation could omit a central record. Independent format implementation
rights remain unchanged. Unmanaged forks cannot be compelled to report by
publishing this specification alone.

## Core decisions

Submit a public proposal for changes to profile semantics. Include:

- The problem and bounded use case.
- Exact contract/schema changes and business meanings.
- Compatibility, permissions and security effects.
- Migration instructions and positive/negative fixtures.
- Maintainer and support responsibilities.

Ordinary proposals affecting core behavior receive at least 14 calendar days
of public review before acceptance. Maintainers record the decision and
reason in the issue or pull request. Anyone can request reconsideration with
new technical evidence; maintainers record the outcome. Emergency security
measures may precede public review, followed by an explanation that avoids
premature disclosure of an exploit.

A shared profile becomes stable only after published semantics and tests,
including the same immutable package tested in two independent host
implementations against the same synthetic fixtures. No current profile is
promoted to stable by this repository's initial publication.

## Independent extensions

Maintainers control shared profile identifiers. Independent teams may develop
public or private namespaced contracts with their own support and ownership.
They must describe host-specific behavior accurately and must not present it
as shared portability or RateHighway endorsement. See
[extensions and compatibility](docs/extensions-and-compatibility.md).

## Assurance and services

Conformance evidence, commercial arrangements, service access and optional
certification are separate decisions. Publish the tested scope and limitations
of a compatibility claim. No certification programme, certificate price,
service response time or supported host release is established here.

Any future certification must publish its issuer, criteria, evidence scope,
expiry, suspension and appeal process. Equivalent technical rules should
apply to RateHighway and independent implementations.
