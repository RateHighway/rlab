# Proposal: RLAB-CENTRAL-ADMISSION-2

| | |
| --- | --- |
| **Status** | **Proposal, open for public review.** Not in force |
| **Opened** | 2026-11-16 |
| **Earliest acceptance** | 2026-11-30 (at least 14 calendar days, [GOVERNANCE.md](../GOVERNANCE.md)) |
| **Amended** | Section 9, automatic review, was added while this proposal was under review. It has its own review period: at least 14 calendar days from the day it was published to the pull request. Sections 1 to 8 cannot be accepted with section 9 before that period ends |
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

The disclosure for the automatic review in section 9 is in section 9.7.

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
| How a change is made | A reviewed commit | A recorded decision by an authenticated reviewer: a person, or an automatic reviewer under section 9 |
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

**Unchanged limits.** A source digest alone still does not prove that a package
was built from that source; section 9 closes this only where the host built the
package. A deployment record is still a host's own report, not proof that a
page was displayed. Registration is still not certification. The bounded
automatic rule is still not a review of a page's code or its calculations. The
automatic review in section 9 does examine a page's code, within the limits in
section 9.6, and it is not certification either.

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
| An automatic reviewer (section 9) asks to write or change an automatic rule, add or remove a principal, or change a data grant | Refused on authorization |
| An automatic review in which any required check could not run or finish | Not approved and not refused; the placement stays pending |
| A language-model review approves a page that another check refused | The page is refused |
| A page that, during an automatic review, makes an outside request, changes data without a user action, or contains code generated at run time | Refused, with a stated reason |
| Approval of an older pending version after a newer version of the same page was submitted for the same placement | Cannot happen: the older request was withdrawn when the newer one arrived |

**Must be allowed**

| Request | Required answer |
| --- | --- |
| A host submits exact bytes and asks for a placement | Accepted, recorded as pending, with no host permitted |
| A reviewer approves a pending placement | The host is permitted on that version and the placement is approved, as one recorded decision |
| A host renews its own approved, unchanged placement | Recorded, extending only the lease, the report time and the host release |
| A host asks about a placement that is approved, permitted, unexpired and matches its context exactly | Eligible, with a deadline no later than the check time plus 15 minutes and no later than the lease |
| A request that meets every condition of the bounded automatic rule on a named host | May be approved by the rule, recorded as the rule's decision and not the host's |
| A placement whose page passes every check in section 9.3 | May be approved by the automatic reviewer, recorded as the reviewer's decision with its version and the digest of its evidence |
| A person with reviewer authority disables a placement that was approved automatically | Disabled at once |

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

Questions about the automatic review are in section 9.8.

## 9. Amendment: automatic review

This section was added while the proposal was under review. Like the rest of
the proposal, it is not in force.

### 9.1 What it changes

Policy 1 and sections 1 to 8 assume that a person decides every placement the
bounded automatic rule does not cover. This amendment lets a registry give that
decision to an **automatic reviewer**: a service that examines every file of a
submission and then approves or refuses it. It may decide placements in any
environment, including `production`, and for pages that use data services.

The bounded automatic rule is unchanged and separate. That rule approves a
narrow class of test placements without examining the page. An automatic
reviewer examines the page.

### 9.2 Who the automatic reviewer is

- It is its own registry principal, authenticated like any other. It is not a
  host, and no host may act as it.
- It may list pending placements, read a placement and its retained files,
  approve and refuse. Nothing else. It cannot write or change an automatic
  rule, add or remove principals, permit a host except by approving a
  placement, revoke a registration or change a data grant.
- A host still cannot approve its own placement, directly or by asking the
  automatic reviewer.

### 9.3 What it must check

Before it approves, an automatic reviewer must complete every check below on
the exact registered files.

| # | Check | Must refuse when |
| --- | --- | --- |
| 1 | **Integrity.** Package and source are retained, their digests match the registration, and the version is new for the page id. Where the host built the package from the source, the reviewer rebuilds it from the retained source and compares the result | Any difference |
| 2 | **Format.** The profile's reference checker | Any error |
| 3 | **Declared access.** Every requested permission and service is one the host knows, and any network destination is one the profile allows | An unknown permission or service, or a network destination the profile does not allow |
| 4 | **Code.** Every script and markup file, read for code generated at run time, code that cannot be read, script injection, outside addresses, and attempts to read credentials or reach the host page | Code generated at run time, code that cannot be read, or any outside address |
| 5 | **Running the page.** In an isolated environment, with a synthetic host context and synthetic data only, never a real organization's data. The reviewer operates the page's controls and records every request and data call | Any outside request, any data change without a user action, any change outside the synthetic grant, or failure to load |
| 6 | **Language-model review** (optional). A model with no tools and no network access reads the source and manifest and answers a fixed checklist: does the page do what its name and description say, does it say what it will change before it changes it, and does it contain hidden controls, impersonation, misleading text, requests for credentials or text addressed to a reviewer | A high-confidence finding in a blocking category. Text in the page addressed to the reviewer is itself blocking |

These rules apply to every check:

- **Failure is not a pass.** If a check cannot run or finish, the placement
  stays pending and the review is retried. It is not approved, and it is not
  refused for that reason. The registry's operator is alerted.
- **A model can refuse, never overrule.** A language-model review may refuse a
  page. It must never approve a page that another check refused, and a
  registry must not use a model review as its only check.
- **The page is data.** Page content is never treated as an instruction to the
  reviewer. Model output that does not match the reviewer's fixed output
  format counts as a check that did not finish.
- **One recorded decision.** The decision, the result of every check, a digest
  of the evidence and the reviewer's version (checker versions, model
  identifier and checklist version) are written together with the history
  entry, in one transaction.
- **Reasons the builder can act on.** Each refusal reason has a stable code,
  the file and line where there is one, a plain message and the fix.
- **The newest version wins.** When a newer version of a page is submitted for
  the same host and placement, older pending requests for it are withdrawn in
  the same transaction, so approval of an older version can never replace a
  newer one.

### 9.4 Evidence that it works

- **Known-bad pages.** A set of synthetic pages that each try one prohibited
  thing: send data to an outside address, change data without a click, hide a
  control, run generated code, hide code, impersonate the host's operator,
  change data outside the grant, and address instructions to the reviewer.
  Every one must be refused, with the expected reason, before first use and
  after any change to a check, a checker version, the model or the checklist.
  One miss blocks the change.
- **Known-good pages.** Pages approved before, and the reference examples, must
  be approved. Each exception is explained and recorded.
- **Published results.** An implementation should publish the results of both
  sets with its compatibility statement, and keep regular figures: decisions,
  refusals by reason, reviews that could not finish, and time to decision.

### 9.5 What stays the same

- Approval decides whether a page may be displayed. It grants no access to
  data. The host still checks the data grant, the page's permissions, the
  user's role and the user's credentials every time the page runs.
- The 24-hour lease limit, the 15-minute refresh, fail-closed behavior and the
  admission checks a host performs.
- A person with reviewer authority can revoke a registration, remove a host or
  disable a placement at any time, including one approved automatically. This
  is an emergency stop, not a review step.
- An automatic approval is not certification and issues no certificate.

### 9.6 Limits

- The checks can show that a page did not do a prohibited thing during the
  review. They cannot prove that it never will. The page runs on synthetic
  data, and its behavior with real data, on another date or after a delay may
  differ.
- The rebuild in check 1 proves that a host-built package came from its
  source. For a package the builder compiled, the reviewer still cannot
  confirm that the retained source is the original rather than compiled
  output.
- A language-model review can be wrong in either direction. That is why it can
  refuse but never approve against another check.
- No person reads every page. The test sets stand in for that judgment, and
  they are only as good as what they cover.

### 9.7 Disclosure

RateHighway intends to use automatic review on its own host, `RevenueLab.build`,
where today every placement is approved by a person. When this amendment was
published, automatic review was not deployed. If RateHighway switches its host
to automatic review before this review ends, it will say so on the pull
request, as it did for the rest of this proposal. As in the disclosure above,
that would not shorten the review or oblige any other host.

### 9.8 Questions the review should settle

1. Should a language-model review be allowed as a check at all, or only
   checks whose result can be repeated exactly?
2. Should a registry be required to run an automatic reviewer alongside a
   person's decisions for a stated period, recording both, before its own
   decisions take effect?
3. Should publishing the test-set results be required rather than
   recommended?
4. Should automatic review be allowed for `production` placements of pages
   that change data, or only for pages that read data?
