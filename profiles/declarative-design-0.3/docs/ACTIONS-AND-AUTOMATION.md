# Actions, workflows and automation

**Draft Standard 0.3 | Normative design requirements, not live API availability**

## 1. Level 2 means controlled read and write

Provide named business operations, not a generic `write` permission. Examples: `notes.create`, `review-tasks.create`, `rate-proposals.create`, `rate-proposals.submit` and, only when separately supported, `rates.publish`. Each maps to a versioned host contract with input/output schema, operation-specific permission, risk classification, valid targets, concurrency rules, side effects, approval policy and audit requirements.

The host catalogue defines those facts. A package references an operation; it cannot invent its implementation, lower its risk or replace the confirmation. An action may complete immediately or return an asynchronous job. A write verb in HTTP is not the capability definition: a read-only POST remains a read; a GET must never mutate business records.

### Approval proportional to the operation

| Operation | Normal user experience | Required protection |
|---|---|---|
| Save personal column order | Save automatically through host preference storage | Own-user namespace, type/size limits, no business-data payload |
| Add an internal note | Explicit Save action; no second generic confirmation if policy permits | Scoped record access, input validation, audit and replay protection |
| Create/update a proposal | Save draft with validation feedback | Version precondition and attribution; not a live rate change |
| Submit a material operational change | Host-owned before/after preview and explicit confirmation | Exact target/value binding, current rights, policy checks and required approval |
| Execute live rate updates | Host-controlled process, review/step-up where policy requires | Business limits, licensed data, queues, downstream acknowledgement and reconciliation |

Prompting for confirmation on every harmless preference change would create fatigue. Make low-risk operations straightforward and reserve stronger, informative checks for meaningful effects. A Level 2 designation does not mean all writes use the same process.

## 2. The host action broker

Expose a builder operation such as `requestAction(actionId, inputs)`. It asks the host to manage the operation. It never bypasses host review and cannot supply `approved: true`, a tenant override or an arbitrary outbound URL. A declarative ActionButton binds to this operation automatically.

Recommended host API responsibilities, independent of HTTP route naming:

1. **Prepare.** Resolve identity, installation/digest and exact action version. Check grants and validate inputs, object ownership, resource versions and data freshness. Resolve a bounded target list server-side.
2. **Preview.** Store an immutable proposed operation and return a safe preview receipt. Include targets/count, field/value differences, currency/units, applicable constraints, warnings, approval requirements and expiry. The preview UI is host-owned.
3. **Authorise.** Obtain the operation's required gesture, confirmation and/or approval using host identity. Bind approval to the exact proposal and actor role; separate preparer/approver when policy requires it. The page never renders an authoritative approval result.
4. **Commit.** Recheck current rights, entitlements, registry state, versions and policy. Verify the receipt and idempotency key. Execute through the authoritative service or queue. Expired, modified or stale proposals require a fresh preview/approval, not automatic substitution.
5. **Track.** Return a receipt with durable status and per-target results. A queue acceptance is not downstream success. Record trace IDs, failures and reconciliation state without leaking confidential payloads into ordinary logs.

For low-risk operations, prepare/authorise/commit may happen in one host-controlled interaction under policy. The logical checks and audit remain; forcing two network requests and a second dialog is not itself a security requirement.

### Preview receipt and operation record

The server retains: action ID/version, installation/digest, trusted tenant, initiator, target IDs and versions, canonical inputs, before/after representation, hash of the canonical operation, current policy version, approval requirements, expiry and idempotency namespace. The client receives only an opaque receipt and permitted display data. Use a defined canonical serialisation for hashes; do not rely on ad hoc JSON ordering.

Bind the commit key to tenant + installation + action version + intended operation. Same key/same payload returns the original result; same key/different payload is a conflict. Never reuse a key for a different attempt. If the downstream system lacks idempotency and its response is lost, mark outcome `unknown` and reconcile before retrying. Do not promise exactly-once execution across systems that cannot provide it.

Runtime result shape, an illustrative contract:

```json
{
  "operationId": "opaque-operation-id",
  "state": "awaiting_approval",
  "effect": "none",
  "traceId": "opaque-trace-id",
  "items": [],
  "next": "host-review"
}
```

States: prepared, awaiting_confirmation, awaiting_approval, queued, running, succeeded, partially_succeeded, failed, cancelled, expired, unknown. Allowed transitions are enforced by the broker. Approval and successful execution are distinct. Hosts define actionable failure codes, including forbidden, stale_context, version_conflict, expired_preview, limit_exceeded, approval_required, duplicate_conflict, downstream_unavailable and outcome_unknown.

## 3. Guardrails for rental operations

For rate-related actions, validate location pair, pickup/return coverage, class/rate-plan mapping, channel, currency, tax/fee basis, effective period, freshness, floors, ceilings, adjustment limits and conflicting rules. Do not allow a display label or a rounded chart value to become an exact operational target. Recompute authoritative constraints at commit time.

For bulk changes, resolve and freeze the target set before confirmation. Show exact affected count and scope. Pagination, selection changes or an altered query must not expand the approved set. Enforce per-request and per-run limits, return per-target results and stop according to the declared failure policy. Any compensating rate update is a new business action with fresh validation; “undo” cannot guarantee that external channels have already reverted.

The read-only first RME release remains unchanged. Creating a standard contract for a future action is not approval to publish production rates now.

## 4. Level 3: human-started durable workflows

A workflow is a host-executed, versioned graph of approved reads, calculations, actions and approval checkpoints. It is not a browser script loop. The initiating person sees the proposed workflow and scope. The host pins workflow and package digests, persists a run record and can continue after the browser closes.

Each run has an explicit finite authority: user-started run ID, tenant, installation/version, allowed operations/targets, deadline and policy. A run's authority cannot exceed the initiator's approved rights and the tenant grant. At each side effect, recheck current rights or a separately approved scoped execution grant; removal of an owner or revocation pauses/denies the run. Approval after a long pause requires fresh relevant data and versions. Extending the deadline or scope is a new authorisation, not a hidden retry.

Initial graph nodes:

- `query`: named versioned read contract with bounded inputs.
- `action`: declared operation through the broker; no raw HTTP or database node.
- `approval`: host-owned checkpoint with role resolved through policy; never a hardcoded email or user ID from a package.

The preview grammar uses a directed acyclic graph of at most 20 nodes. Conditional branching, bounded mapping, reusable subflows and deterministic computation are valuable later additions requiring their own schema and budgets. Do not assume they work in the included examples.

The host schedules ready nodes only after predecessors succeed. Initial failure behaviour is `pause`: no downstream side effect after a failed or unknown result. Persist step inputs/results, versions, deadlines, attempt IDs and idempotency keys in a tenant-scoped encrypted store. Replaying a step must not duplicate an effect. Retries are bounded and reserved for retryable failures; uncertain downstream results require reconciliation.

Approvals are host tokens bound to the workflow run and approved step/operation, not a boolean returned in a dataset. An approval node does not automatically authorise every later action. An action's own domain policy still applies, and a high-risk operation needs its own exact preview binding.

**Example:** user selects a location, starts “Review fleet pressure”, the host reads authorised data, creates a review task, requests a manager checkpoint, then records the approved follow-up. The portable example uses synthetic task operations rather than pretending an RME production rate API exists.

## 5. Level 4: bounded automation

Automation adds unattended initiation to the same workflow engine. The package declares a proposed event or schedule. An administrator activates a separate **automation mandate** in trusted host settings.

| Mandate field | Required meaning |
|---|---|
| Principal and owner | Dedicated service identity, responsible owner and escalation route |
| Installation/version | Exact approved workflow/package digests and target environment |
| Scope | Tenant derived by host, locations/classes, allowed data and action IDs |
| Trigger | Approved event type/filter or schedule with IANA timezone |
| Limits | Runs/time window, concurrency, steps, rows, affected records and applicable money/rate limits |
| Data policy | Maximum age, required coverage, safe behaviour on missing/partial data |
| Approval policy | Actions allowed unattended versus those requiring a person |
| Lifetime | Activation/expiry time, review date and owner-transfer rules |
| Recovery | Retry budget, reconciliation, failure thresholds and compensation policy |
| Operational control | Shadow mode, disable switch, monitoring and incident contact |

Do not run on a person's long-lived browser token. Mint short-lived job credentials from the active mandate, check policy again before each effect and store no generic downstream secret in the package. A read-only scheduled job still requires a mandate because repeated data access has cost and disclosure implications.

Schedules explicitly state timezone, daylight-saving policy and missed-run behaviour. Event sources are authenticated, tenant-scoped, versioned and deduplicated using event/run keys. Reject replays and stale events. Suppress feedback loops where an action emits the event that would retrigger itself. Default concurrency is one for a conflicting target scope; larger concurrency needs resource-level locking or version checks.

The included automation proposal uses a daily local time and `skip` policies for missed/ambiguous/nonexistent occurrences. This is an exact design choice for the fixture; a real host may advertise additional policies with defined semantics. No catch-up surge is permitted by default.

**Shadow mode is the first activation state:** reads use authorised data, prospective actions are validated and logged as would-have-run, but no business write occurs. Validate shadow accuracy with an operator, then grant a narrow live mandate. Out-of-budget, stale, conflicting or unrecognised input fails closed to a review state. A host policy engine, not an LLM's confidence score, decides execution eligibility.

An LLM may propose a classification or action. Treat its output and source documents as untrusted data, validate against schemas and policy, keep credentials out of its context and require the same broker controls. Agent-generated approval text is not a human approval. Prompt injection must not select tools, change scopes or weaken a mandate.

## 6. Emergency control and recovery

Revoking a grant, suspending an extension or disabling a mandate must prevent new work and the next side effect even if a worker is disconnected or the page is malicious. Propagate cancellation to queued and running jobs. A started external side effect may not be cancellable; record its actual status and reconcile. Never claim that removing a widget undoes an executed action or recalls data already disclosed.

Scope kill switches by host, tenant, installation, workflow and action. After an incident, resumption requires review of current state and authority, not automatic replay of all missed work. Rollback of code restores the previous approved version only after compatibility/policy checks; it does not restore revoked permissions or roll back business effects. Maintain a separate, reviewable compensation plan.

## 7. Mandatory added tests

| Test | Expected result |
|---|---|
| Modify inputs/targets after preview | Commit denied; new preview required |
| Reuse commit key with different payload | Conflict, no new effect |
| Commit after revocation or version change | Denied before side effect |
| Click twice or replay workflow step | One recorded effect or original receipt |
| Lose downstream response | Unknown/reconcile, no blind duplicate |
| Approve as wrong role or same actor when separation required | Approval rejected |
| Restart a workflow worker midway | Resume from durable checkpoint without duplicate effects |
| Fail one target in a bulk action | Honest partial result and defined stop/review behaviour |
| Trigger an automation event twice | One run, deduplication recorded |
| Change tenant in an event payload | Server context enforced; no cross-tenant work |
| Exceed mandate or use stale data | Side effect blocked and review/alert recorded |
| Disable mandate during a long run | Next side effect denied, external in-flight status reconciled |
| Automate a write requiring human confirmation | Pause for host approval; cannot auto-confirm |

The supplied tests check design declarations, not these runtime behaviours. Runtime certification requires an implemented host and independent evidence.
