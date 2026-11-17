# Proposal: RLAB-CENTRAL-ADMISSION-2

| | |
| --- | --- |
| **Status** | **Proposal, open for public review.** Not in force |
| **Opened** | 2026-11-16 |
| **Earliest acceptance** | 2026-11-30 (at least 14 calendar days, [GOVERNANCE.md](../GOVERNANCE.md)) |
| **In force today** | [`RLAB-CENTRAL-ADMISSION-1`](central-registration.md), unchanged, for every host |
| **Proposed by** | RateHighway |

Comments belong on the pull request or issue that carries this proposal, so
that the decision and its reason are recorded with it.

## Disclosure

**RateHighway has already moved its own host, `RevenueLab.build`, to this
policy**, on 2026-11-16, before this review. It is said here plainly because a
reviewer should know it, and because it affects how the proposal should be
read: RateHighway is not describing an idea, it is describing something it
runs, and it has an interest in the answer being yes.

That deployment does not shorten this review, does not make the policy
accepted, and does not oblige any other host. If the review rejects the
proposal or changes it materially, RateHighway's host follows the outcome.
Until then, no other host is governed by anything but policy 1.

## 1. The problem, and the bounded use case

Policy 1 makes a GitHub repository the central authority. A host reads the
current `master` head of the archive and the result of its checks, and every
change to the archive is a reviewed commit — in practice a branch, a pull
request and a merge, for each registration, each placement, each renewal and
each removal.

That has four consequences, observed in operation:

1. **A person must work in a source-control tool to publish a page.** Every
   placement, including routine ones, waits on someone opening a web page and
   pressing a button.
2. **Leases make it continuous.** A deployment lease may span at most 24
   hours, so each active placement needs a renewal, which under policy 1 is
   another pull request that does nothing until it is merged.
3. **Availability of the authority is availability of the pages.** A host must
   refresh within 15 minutes and fail closed. An outage of the hosting service
   therefore closes conforming pages, for a reason unrelated to the page, the
   host or the customer.
4. **The archive accumulates binaries.** Each page version adds its package and
   source to repository history permanently.

The bounded use case is the one policy 1 already governs: an official or
RateHighway-approved host that must register exact page bytes centrally and
hold an approved, unexpired deployment record before it displays a page. This
proposal changes **where those records live and how a change to them is
made**, and nothing else.

## 2. Exact contract and schema changes

**No schema changes.** `registration-record.schema.json` and
`deployment-record.schema.json` are unchanged, field for field. A record
written under policy 2 is readable by a policy 1 reader, and the reverse.

**No manifest or profile changes.** This is an admission overlay, as policy 1
is. It adds no field to a page manifest, does not weaken unknown-field
rejection, and does not change `RLAB-PAGE-READONLY-0.2` or
`RLAB-DECLARATIVE-DESIGN-0.3`.

What changes is the definition of central authority:

| | Policy 1 | Policy 2 |
| --- | --- | --- |
| Authority | The current `master` head of the archive repository | The registry's current **signed head** |
| Evidence that the authority is sound | The latest successful `push` run of `registry-check.yml` on that head | The registry's scheduled audit: it recomputes the history's hash chain, verifies the head's signature, and compares every record and retained artifact |
| How a change is made | A reviewed commit | A recorded decision by an authenticated reviewer |
| How a host asks | A branch and a pull request | A request from an authenticated host that carries no permission and no approval |
| How a host reads | The repository, through the hosting service's API | The registry, as itself |

A **signed head** is the newest entry of an append-only history in which each
entry carries the hash of the entry before it, signed with a key that only the
registry may sign with. A host receives it with every answer and may record it
as evidence of what it was told and when.

The deadline rule is unchanged: the earlier of the check time plus 15 minutes
and the deployment lease expiry, and a host may not extend it locally.

## 3. Compatibility, permissions and security effects

**Compatibility.** A host enforces exactly one policy version at a time.
Reading whichever of the two answers is more permissive is an implementation
of neither. Policy 1 remains published and supported for as long as any host
enforces it; this proposal does not withdraw it.

**Permissions.** No new page permission, no new host permission, and no change
to what a page may do. Central permission still grants no access to any
organization's data.

**What is strengthened.**

- *Identity is enforced rather than conventional.* Under policy 1 the rule
  that a host cannot approve its own placement rests on repository write
  permissions and branch protection. Policy 2 requires the registry to decide
  what a caller may do from the caller's authenticated identity alone, never
  from a field in the request, and requires that a host principal cannot reach
  any action that grants permission or approval.
- *Immutability is enforced at write time.* Package and source bytes are
  stored under their own digest with a create-only write and object retention,
  so registered bytes cannot be replaced or removed rather than merely should
  not be.
- *A decision is one transaction.* A record and the history entry that
  explains it are written together or not at all, so the two cannot diverge.

**What is weakened, and what answers it.**

- *The history is no longer kept by an independent party.* Policy 2 therefore
  recommends copying records to an independent system under separate control
  and comparing the two on a schedule (section 6).
- *A running service replaces a static repository.* Its availability now
  matters. This is a change of dependency rather than an addition: the host
  already had to reach the authority every 15 minutes.
- *The reviewer's screen is implementation-defined.* Policy 1 inherited a
  review interface; policy 2 requires implementations to supply one and to
  keep "may approve" apart from "may submit".

**Unchanged limits.** A source digest still does not prove that a package was
built from that source. A deployment record is still a host's own report, not
proof that a page was displayed. Registration is still not certification, and
automatic approval is still not a review of a page's code or its calculations.

## 4. Migration

1. Deploy the registry and import the archive's records **unchanged**. An
   import is a move, not a re-decision: a record that was pending stays
   pending, a revoked registration stays revoked.
2. Run both authorities side by side and compare the admission answer for
   every page until the comparison is convincing.
3. Give the host an identity the registry knows, **before** switching it. A
   host that is switched first fails closed at its next refresh, which is
   correct behaviour and a closed page.
4. Switch the host in one change, so it reads one authority at a time and
   never falls between them.
5. Stop writes to the archive repository except from the copy in section 6.
6. State in the host's compatibility statement which policy version it
   enforces, and from which date.

A host that cannot complete step 2 should say so in its compatibility
statement rather than describe the comparison as done.

## 5. Fixtures

A conforming registry must produce these outcomes. Each is stated as a request
and the only acceptable answer.

**Must be refused**

| Request | Required answer |
| --- | --- |
| A host asks to approve any placement, including its own | Refused on authorization, before any record is read |
| A host asks to add any host to `allowedHosts` | Refused on authorization |
| A host names a different `hostId` in its request | The caller's own identity is used; the field cannot take effect |
| A host asks to renew or disable a placement belonging to another host | Refused |
| A submission names a page id and version already registered with different bytes | Refused; a new version is required |
| A submission's package manifest names a different page id, version or profile than the submission | Refused |
| A caller the registry does not know asks anything | Refused |
| A principal that has been removed asks anything | Refused |
| An automatic approval rule whose conditions differ from the authorized conditions | The rule is refused, not obeyed |
| A `staging` or `production` placement under the bounded automatic rule | Not approved automatically |
| A page requesting more than the rule's permissions, declaring a service, or declaring a network destination | Not approved automatically |
| An admission request whose release, environment, route, slot or digest differs from the approved placement | Not eligible |
| An admission request against a revoked registration, a removed host permission, a disabled placement or an expired lease | Not eligible |

**Must be allowed**

| Request | Required answer |
| --- | --- |
| A host submits exact bytes and asks for a placement | Accepted, recorded as pending, with no host permitted |
| A reviewer approves a pending placement | The host is permitted on that version and the placement is approved, as one recorded decision |
| A host renews its own approved, unchanged placement | Recorded, extending only the lease, the report time and the host release |
| A host asks about a placement that is approved, permitted, unexpired and matches its context exactly | Eligible, with a deadline no later than the check time plus 15 minutes and no later than the lease |
| A request that meets every condition of the bounded automatic rule on a named host | May be approved by the rule, recorded as the rule's decision and not the host's |

**Must be detected by the audit**

| Condition | Required outcome |
| --- | --- |
| A record changed without a corresponding history entry | Reported |
| A history entry altered or removed | Reported, by the broken chain |
| A head that does not verify against its signature | Reported |
| A retained artifact missing, or not matching its registered digest | Reported |
| An independent copy that disagrees, or is too far behind | Reported |

An implementation should publish the results of these fixtures with its
compatibility statement.

## 6. Evidence held outside the service

An implementation **should** copy each change's records to an independent
system under separate control, compare the two on a schedule, and raise an
alarm on any difference.

Such a copy is **evidence, never authority**. It must not be read to decide
admission, and an implementation must not treat a copy that is stale,
unreachable or missing as a reason either to deny or to allow anything.

RateHighway's implementation copies records to the repository that was the
authority under policy 1.

## 7. Maintainer and support responsibilities

**RateHighway, as maintainer of this policy**, undertakes to: keep the record
schemas and the published conditions of any automatic rule accurate; publish a
change to either as a proposal under `GOVERNANCE.md`; and record the decision
on this proposal, with its reason, where the proposal is held.

**An implementation's own maintainer** is responsible for its registry, its
reviewers, its identities and its audit, and for stating which policy version
its host enforces. Publishing this policy does not make RateHighway
responsible for another operator's registry, nor does implementing it imply
RateHighway endorsement — see
[extensions and compatibility](extensions-and-compatibility.md).

**Support.** Questions and defects against this proposal belong in the public
repository, as issues. Nothing in this proposal creates a service commitment,
an availability target or a support contract.

## 8. Questions the review should settle

1. Should a signed head be **required**, or should the requirement be that the
   history is tamper-evident and compared with an independent copy, leaving
   the mechanism open?
2. Should the independent copy in section 6 be **required** for an official
   host rather than recommended?
3. Does a registry's answer need a signature of its own, or is the signed head
   it carries sufficient for a host that already trusts its transport?
4. Should this policy supersede policy 1 on acceptance, or should both remain
   in force with hosts stating which they enforce?
