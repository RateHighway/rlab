# Adoption, certification, migration and evidence

**Draft Standard 0.3 | 2026-10-02**

## 1. Why builders and hosts would adopt it

| Audience | Useful outcome | Standard feature that delivers it |
|---|---|---|
| Operator/builder | A useful extension without becoming a hosting/security specialist | Templates, host components, existing login, connections and safe default data |
| Experienced developer | More time on domain value and less repeated integration code | Typed service/action contracts, SDK, emulator and automated checks |
| Software host | Customer customisation with controlled upgrade/support risk | Versioned extension points, authorisation broker, immutable releases and revocation |
| Service provider | A repeatable supported product across compatible installations | Packaged source/builds, declared dependencies, capability discovery and support ownership |
| RateHighway | Complementary customer experiences and a stronger platform role | RME-native host services, shared standards and preserved customer-built tools |

The adoption case is a product hypothesis to test. Do not claim measured time savings or guaranteed portability. Useful learning tools remain public; independent builders are a successful outcome. Commercial hosting, paid support and marketplace distribution can be added without making a basic page artificially weak.

### Make security convenient

Use reviewed presets, narrow automatic permission derivation, accurate plain-language summaries, built-in test data and automatic safe-state handling. Save current context and personal view preferences through host services. Present one clear review flow for meaningful effects, rather than repeated generic warnings. Give errors a fix: “This host does not expose rental-period fleet coverage. Use daily snapshot mode or install a compatible adapter.”

The low-friction path works because shared controls are implemented once, reviewed and reused. Keep source export, framework independence, customer-owned logic and a route to custom views. Templates should be editable rather than a locked vendor-only catalogue.

### Measures for a pilot

Track time to first useful synthetic view, time to authorised installation, manual support interventions, validation errors by type, second-build rate, active repeat usage, permission-expansion rate, rejected stale/replayed actions and recovery time. For hosts, track renderer/adapter implementation effort, number of reusable contracts and updates requiring code changes. Set targets after a baseline; none are claimed achieved here.

Run a comparative pilot: one simple report and one task-creation extension built through the existing custom-web route and through Compose. Measure both builder effort and host operating effort, and ask builders to explain the generated code/manifest and permissions. Ease of use that hides misunderstanding is not sufficient.

## 2. Level-aware certification

Retain the badge headline **“This system hosts RevenueLab Pages.”** Replace a universal “Read-only host” line with a scope line tied to verified support, such as **“Levels 1–2 · Read + Act”**. Display **“Vendor tested”** for a self-declaration and **“Certified”** only after the actual programme reviews and issues a record. New artwork is not itself an award.

The linked record identifies host/product, runtime release, supported standard versions, level semantics, UI runtimes, surfaces, data/action contracts, delivery modes, test-suite version, evidence digest, assessment date and current status. Do not display “Level 4 certified” when only an isolated scheduler was tested without the underlying Level 1–3 controls. Contract and surface support must be visible even when a level is supported.

| Certification scope | Added evidence over the prior level |
|---|---|
| Level 1 Read | Safe packages/renderer, tenant and field filtering, context correctness, egress disclosures and accessible state handling |
| Level 2 Act | Trusted previews, operation/target binding, approvals, optimistic concurrency, idempotency and audit |
| Level 3 Orchestrate | Run authority, step rechecks, durable restart, deadlines, approval checkpoints and partial recovery |
| Level 4 Automate | Dedicated principal, finite mandate, shadow/live separation, authenticated triggers, quotas, expiry and emergency stop |

Component runtimes and custom-web/remote modes have separate endorsement tests. A host may certify Compose with bundle delivery first. Package review, publisher identity and a host certificate remain separate. Self-issued risk/approval/certification claims in package manifests are rejected.

Issuer governance, review independence, trademark licence, renewal intervals, fees if any and incident/revocation procedures still need formal decisions. Do not imply an active certification programme or certify a named partner based on this design.

## 3. Migration from 0.2

The delivered 0.2 draft remains available as historical reference. This 0.3 design supersedes its full-page/read-only-only framing, not its security principles. Existing 0.2 artifacts and validators remain unchanged. Hosts can keep an explicit legacy profile.

For an existing custom web page, wrap the same approved bundle with the future 0.3 custom-web profile once that profile is specified and supported. It can remain a useful Level 1 page. No automatic Level 2 grant accompanies conversion. Introduce named action bindings only after the host publishes and approves those operations.

For a Compose conversion, recreate the view in the published component grammar and move data access to named broker queries. Preserve the page ID, increase its version, create a new digest and test behaviour/permissions. Add Level 2 operations as separate versioned changes. Level 3/4 designs require explicit run/mandate authorisation and a production engine; no filename or manifest-only upgrade creates them.

Never silently interpret a 0.2 permission as a broader 0.3 capability. Do not copy old session tokens, administrator grants or approval results into an artifact. Show clear per-host support so builders can choose compatible paths rather than discover limitations only after installation.

## 4. Decisions and recommended sequence

| Decision | Recommendation | Remaining evidence/dependency |
|---|---|---|
| Public model | Four levels, with risk and trust separate | Product acceptance and examples understood by operators |
| Default builder path | Compose with host components | Renderer security/accessibility and a real beginner pilot |
| Advanced UI | Isolated coded components plus custom-web SDK | Sandbox threat model and benchmarked operating cost |
| First write | Tasks/notes and proposal creation | Actual host domain contracts, approval and audit behaviour |
| Workflow/automation | Durable host service, mandates for unattended runs | Runtime conformance, recovery and accountable ownership |
| Portability | Semantic contracts and explicit capability matching | Same digest working against two independently implemented hosts |
| Licensing | Apache-2.0 for this repository; independently authored pages keep their applicable terms | Preserve license and required notices in distributions |
| Certification | Versioned evidence and revocable linked record | Named issuer/reviewers and operating process |

No deadlines, prices, partner availability or staffing commitments are created by this document. The architecture is designed for adoption, but the issuer, host SDKs, CLI/MCP tools, public schemas and Level 2–4 execution services are not made live by writing the standard.

## 5. What this delivery implements

- A complete written successor design for Levels 1–4 and three UI paths.
- Strict draft schemas for a small declarative preview grammar, action references, workflow graphs and automation proposals.
- Four synthetic examples and offline cross-reference/compatibility tests.
- A packer producing **design-only** `.rlab` artifacts and a report stating exactly what was checked.

It does not implement a renderer, production SDK, action broker, workflow runner, scheduler, publisher signing service or certificate issuer. The checker is deliberately not a general JSON Schema engine or production security scanner. Run the included test suite and design checker for current execution evidence. Reports must state which checks ran and preserve the listed runtime/security limitations. Source publication does not deploy a host.

## 6. Sources and design rationale

This public source edition preserves the original draft design and its closed
machine-checked profile. The public examples use version `0.1.1` and include
Apache-2.0 licenses. The profile schemas, capability meanings and
`design-only` restriction remain unchanged. Private planning records and
historical delivery reports are outside this technical distribution.

The [sibling 0.2 profile](../../browser-readonly-0.2/README.md) provides the
separate browser-package baseline. This 0.3 design expands the vocabulary
for future implementations; it does not upgrade a 0.2 host or deliver an
execution service. An independently implemented host needs its own evidence
for each contract it claims.

Primary technical references checked on 2026-10-02:

- **Shopify remote rendering:** https://shopify.engineering/remote-rendering-ui-extensibility explains separating extension execution from host rendering and using a restricted bridge. The relevant inference is that native appearance and isolated execution can coexist; it is not proof a particular library alone secures RevenueLab.
- **Shopify current UI components:** https://shopify.dev/docs/api/checkout-ui-extensions/latest/web-components documents host design-system components and extension targets. RevenueLab should similarly describe supported placement and components explicitly, without requiring Shopify's framework or APIs.
- **Atlassian UI Kit:** https://developer.atlassian.com/platform/forge/ui-kit/overview/ and **Custom UI:** https://developer.atlassian.com/platform/forge/extend-ui-with-custom-options/ distinguish a host-component development route and a custom interface route. This supports offering both paths instead of making every builder own a bespoke web app.
- **Adaptive Cards renderer:** https://learn.microsoft.com/en-us/adaptive-cards/rendering-cards/implement-a-renderer describes host rendering, handling actions and host-specific styling. RevenueLab's declarative design is an independent contract, not an assertion of full Adaptive Cards compatibility.
- **OWASP transaction authorisation:** https://cheatsheetseries.owasp.org/cheatsheets/Transaction_Authorization_Cheat_Sheet.html informs server-enforced approval, integrity of reviewed transaction data and a final execution check. The detailed `.rlab` action flow is this draft's design choice.
- **MDN Shadow DOM:** https://developer.mozilla.org/en-US/docs/Web/API/Web_components/Using_shadow_DOM explains encapsulation. It should not be treated as the authorisation boundary for arbitrary extension code.

These are architecture references, not endorsements, partner claims or dependency decisions. Any selected implementation library still needs licence, maintenance and security review.
