# RevenueLab extension standard 0.3

**Official host admission:** apply [RLAB-CENTRAL-ADMISSION-1](../../../docs/central-registration.md) in addition to this profile. Centrally retain every page package and source, record its host placements, and verify current central admission before display. The existing closed manifest grammar is unchanged; design-only content remains non-executable.

**Draft Standard | 2026-10-02**

## 1. Product promise and boundary

**Build the tools and workflows your business needs, inside the systems you already use.**

A RevenueLab extension is a portable, versioned set of views, data bindings and approved business operations. The `.rlab` file remains its installation unit. “RevenueLab Pages” remains useful customer language for visible pages; “extension” describes the broader technical object, not a mandated product rename. In RateMonitor Elite the product remains RME Custom Pages.

The builder controls the useful experience and business logic they author. The host supplies identity, authorised data, standard components, storage where granted, approvals, audit and operations. RME remains authoritative over its pricing rules and downstream integrations. An independent host governs its own operations through its own authorised interfaces. Hosting RevenueLab extensions does not require an RME purchase.

The core standard stays API-first, agent-accessible, framework-independent and host-neutral. An AI assistant can discover contracts, generate a package and explain validation errors through an MCP adapter. MCP never substitutes for application permissions or the host's execution checks. Private customer logic may remain in a separately approved backend; browser source is not secret.

## 2. Four capability levels

| Level | Meaning | Car-rental example | Extra host duty |
|---|---|---|---|
| **1 • Read** | Read authorised data, filter, compare and calculate; no business-record writes | Fleet Pressure Calendar or comparable Market Position Board | Field/location/tenant filters, freshness, safe rendering and read quotas |
| **2 • Act** | A person initiates a specific permitted write through a host action | Add an exception note; create a rate proposal; submit an approved operation if separately supported | Validate, show impact, apply action-specific confirmation/approval, commit and audit |
| **3 • Orchestrate** | A person starts a durable sequence that can continue after the page closes | Build a proposal, send it through review, then submit the approved version and track the result | Durable state, checkpoints, run identity, step authorisation, conflict/failure handling |
| **4 • Automate** | A schedule or event starts work without a person initiating each run, within an administrator-approved mandate | Review stale shops each morning and create review tasks; later, explicitly bounded pricing operations | Delegated service identity, event verification, budgets, expiry, shadow runs, monitoring and kill switch |

Levels are cumulative runtime facilities when a host advertises the full level. They are not cumulative grants. Every package declares a ceiling and the exact capabilities it requests. A host supporting Level 4 must support the control semantics below it but need not offer any particular business API. A package that needs Level 2 is not automatically compatible with every Level 4 host: required services, surfaces, versions and grants must also match.

**Level is determined by execution semantics.** A workflow waiting for approval after a human starts it is Level 3; its continuation is part of that same bounded run. A recurring read-only report is Level 4 because it starts unattended. A click that queues one action is Level 2 even if its backend result is asynchronous. Multiple independent button clicks do not make a Level 3 workflow. A browser timer must not be used to imitate an authorised scheduler.

Level 1 can keep host-managed personal presentation preferences such as a column order. That facility has a separate narrow permission and cannot store business records, cross-user notes or reusable strategies. Export, external processing and personal data are separate permissions at every level; read access does not imply any of them. A user can still copy information already shown to them, so minimise disclosed data.

## 3. Separate level, risk, trust and runtime

| Axis | Examples | Who determines it |
|---|---|---|
| Capability level | 1 Read; 2 Act; 3 Orchestrate; 4 Automate | Requested by publisher; verified from actual features and enforced by host |
| Action risk | Routine note, reversible configuration, live rate publication | Host's domain policy, never a publisher's self-rating |
| Provenance/review | Private, publisher verified, reviewed package | Registry and reviewer |
| Rendering/runtime | Declarative host UI, isolated coded UI, custom web view | Host capabilities and installation approval |
| Data/execution rights | Locations, fields, operation limits and environments | Current user/admin/domain policy |

A trusted publisher cannot bypass tenant permissions. A certified host does not certify the calculations in every extension. A Level 4 badge is not a security superiority badge. Host-native appearance must not make a third-party extension appear to be first-party functionality: show publisher identity in the surface header or details affordance, and reserve host approval UI visibly outside the extension's controlled area.

## 4. Three builder paths

### A. Compose: declarative host-rendered UI, the default

The builder or AI produces a small JSON document describing approved components, named data queries, typed inputs and action bindings. The host renders its own controls and connects those bindings to authorised services. The extension supplies no arbitrary JavaScript or HTML in this path. No iframe is needed for the declared view.

This removes routine layout, accessibility, token handling, context synchronisation and approval implementation from the builder's task. A standard DataTable automatically receives loading, empty, error and stale-data states; a host action automatically receives the correct confirmation. Builders can inspect and edit the source, keep it in Git, or use a visual editor over the same contract.

A component registry specifies types, properties, events, accessibility rules and versioned behaviour. Unknown components, executable expressions, raw HTML, arbitrary CSS, external images and unrecognised URLs fail validation. Escape all text, validate schema before rendering and put limits on nodes, strings, rows, nesting and query cost. A declarative file is untrusted input; a renderer can still contain security bugs.

Recommended shared component set: Text, Metric, DataTable, Chart, DateRange, LocationPicker, VehicleClassPicker, Form, ActionButton, Status, EvidencePanel and WorkflowProgress. Car-rental components should understand currency/tax basis, rental-period coverage, comparability, fleet denominators and data freshness. The executable reference schemas in this kit intentionally cover only Text, DataTable, ActionButton and WorkflowButton; other components need published contracts before implementation.

### B. Code: isolated logic with host-rendered components

Experienced builders write components and calculations against a typed SDK. Their code executes in a separately hardened sandbox and sends an allowlisted component tree and typed events to the host. The host renders the visible UI. This preserves native styling and accessibility while supporting richer interaction.

A remote component renderer is a transport, not a security boundary. A plain same-origin Worker, Web Component, Shadow DOM, JavaScript module or module-federation bundle is insufficient isolation for untrusted code. The host must separately enforce the execution sandbox, network restrictions, memory/CPU budgets, API capability bridge and provenance. Merely hiding `fetch` or relying on a closed Shadow DOM is not a security control. The sandbox may itself use an isolated frame internally; the builder should not manage it.

Design an SDK with `defineExtension`, `useContext`, `useQuery`, host components and `requestAction`. Those names are proposed interfaces, not an installed `@revenuelab` package. React/Preact helpers may be provided, but the underlying tree/event contract must not require one framework. Limit messages, property sizes, depth and update frequency, reject unknown handlers and never turn a property into executable HTML or CSS.

### C. Custom: isolated web application

Retain a sandboxed custom web view for specialist charts, existing apps and frameworks outside the component catalogue. The host SDK handles handshake, context, resize, theme, service calls and action requests. The separate-origin isolation and CSP requirements from 0.2 still apply. It may use an iframe, but installation remains a governed extension, not an arbitrary embed URL.

A remote hosted custom view has more deployment and data-processing obligations. It is optional host support. Core installation should work with bundled declarative views without builders purchasing hosting or configuring infrastructure. Pricing for managed hosting is a separate commercial decision.

### Options assessment

| Approach | Builder benefit | Limitation | Decision |
|---|---|---|---|
| Declarative host components | Fastest route, no app server or browser bridge to build | Less freedom until component catalogue grows | Default, implement first |
| Sandboxed code with remote components | Rich interaction with host appearance | Real sandbox and protocol engineering required | Advanced path after core proof |
| SDK-managed custom web view | Reuse existing browser apps | More UX/performance/security work | Keep as supported escape route |
| Arbitrary same-origin JS/microfrontend | Maximum access | Shares the host's privilege and failure boundary | Exclude for third-party packages |
| Web Components/Shadow DOM alone | Useful style encapsulation | Not permission or code isolation | Only for host-owned components behind the boundary |
| Sandboxed server function/WASM | Private computation and background jobs | Resource, supply-chain and egress controls needed | Optional later runtime profile; not implied by Level 4 |

This recommendation adapts established host-component and isolated-extension patterns; it is not a claim of compatibility with Shopify, Atlassian or Adaptive Cards. Source notes are in the assurance document.

## 5. Multiple surfaces, one business extension

Allow a package to contribute to published extension points: full workspace, dashboard card, record panel, list action and command entry. A host declares which it supports and the context each supplies. A builder declares required versus optional placements and explicit fallbacks. There is no silent rewriting of a page into an unsuitable surface.

A fleet-risk tool could show a summary on the dashboard, its evidence beside a location record, and a review action in a selected-row menu. All share the same approved queries and action contracts. Reusable widgets and calculators can be bundled dependencies, pinned by digest; privileges must include the union of their needs and be reviewed. Installation of one module cannot silently expand another's authority.

Use a governed host event bus and typed capability calls for communication between extensions. No cross-frame DOM access, shared global variables, direct access to another extension's storage, raw credentials or unfiltered tenant-wide event stream. A recipient must independently have access to the data referenced by an event.

## 6. Versioned .rlab package

The ZIP container, safe path rules, immutable artifact digest, byte ceilings, publisher/rights review and lifecycle from 0.2 remain. Draft 0.3 packages use `standardVersion: "0.3"` and a new manifest schema; old validators must reject them. `rlab-page.json` is retained for continuity despite the broader extension purpose. IDs stay stable; permissions and protocol migration are explicit. The sibling [0.2 browser profile](../../browser-readonly-0.2/docs/RLAB-PAGE-STANDARD.md) and [host integration guide](../../browser-readonly-0.2/docs/HOST-INTEGRATION-GUIDE.md) provide the baseline. This 0.3 document describes successor designs; only the included narrow design profile is machine-checked, and no 0.3 execution runtime is supplied.

Common archive ceilings: 25,000,000 compressed bytes, 100,000,000 expanded bytes, 25,000,000 bytes per file, 2,000 entries and 240 path characters. Manifest maximum is 262,144 bytes; this preview profile also limits each referenced JSON document to that size. Reject traversal, absolute paths, backslashes, links, device names, encryption, duplicate/case-colliding paths and file/directory collisions before extraction. Measure actual expanded bytes and enforce worker resource limits. No import-time execution or build hooks. Production importers must scan and authorise the immutable artifact; the supplied source-document checker does not perform these archive gates.

| File | Purpose |
|---|---|
| `rlab-page.json` | Identity, versions, capability level, runtime, surfaces and declarations |
| `ui/main.json` | Host component tree for the Compose path |
| `workflows/main.json` | Optional durable graph for Levels 3–4 |
| `automation/main.json` | Optional proposed trigger for Level 4; never the actual authority grant |
| `README.md` | Purpose, inputs/outputs, limitations, setup and support |
| `LICENSE.txt` | Applicable rights or truthful unresolved status |
| `samples/`, `tests/` | Synthetic examples and inert fixtures |
| `app/` | Compiled browser output only for the separately advertised custom-web runtime |

New manifest fields: `capabilityLevel`, `runtime`, `surfaces`, `queries`, `actions`, `workflow`, `automation`. `hostApi` is still an inclusive minimum/exclusive maximum numeric version range; the semantic operation catalogues and UI contract have independent versions. All command syntax and schema URLs in this release are draft interfaces, not live services.

The preview schemas in this kit use `runtime.kind: "declarative"`, `uiContract: "0.3.0"` and `stage: "design-only"`. Levels 3 and 4 can therefore be validated as design documents without implying a workflow engine exists. For this narrow profile the declared level must equal the minimum inferred from its features, and all declared placements are required. Arbitrary coded/remote manifests are not accepted by this narrow checker. Their production profiles require additional runtime schemas, not permissive unknown fields.

### Authority never travels in the package

Packages contain requests and intent, not tenant assignments, tokens, purchased entitlement, trusted risk classifications, approval results or certificates. Automation declarations propose a schedule/event and refer to a workflow. The active mandate, tenant, allowed locations, budgets and execution identity reside only in the host registry and require administrator approval.

Separate the host's general capability catalogue from the installed extension's effective capabilities. Preflight evaluates the exact standard/UI/runtime versions, placements, named query/action versions and their permission requirements. Unknown mandatory capabilities block installation. Missing optional capabilities must have an authored and tested fallback, not a fake success state.

## 7. Service and data bindings

A named query binds to a host-reviewed service contract with request/response schemas, minimum scopes and field semantics. The builder selects a business concept, not an arbitrary URL or SQL query. The host broker attaches trusted tenant/user/session context and checks authorisation on every request. Normal declarative views never receive a broad API token or connection credential.

Bindings in the preview grammar can reference only a named host `context` key or a literal string. They cannot evaluate JavaScript. Selected-record and prior-step output bindings are useful next additions that require typed schemas; they are not implemented by this kit. The host independently validates record ownership and current versions; a record ID selected in the UI is not proof of access. Query results must carry snapshot freshness, domain observation/coverage times, partial-data warnings and contextVersion. Async results from older context are discarded.

For richer calculation support, publish a bounded expression AST with typed arithmetic, comparisons and explicit null handling. No loops, arbitrary function names, reflection, network, SQL or `eval`; define CPU/row budgets and decimal money operations. That evaluator is a future contract, not implemented by this kit. Proprietary heavy computation can use separately authorised host jobs or a private backend, with declared data processing and egress.

## 8. Security inherited and strengthened

Default deny, tenant isolation, server-side policy, scoped services, reviewable external processing, immutable releases, audit, revocation and rollback remain mandatory at all levels. Risk-sensitive actions add server-issued previews bound to exact data; workflows add durable identities and checkpoints; automation adds a bounded mandate and operational supervision.

Lower-friction building is achieved by centralising reusable controls in the host. It is never achieved by running third-party code in the host's privileged document or giving a builder a general-purpose API key. Controls must remain effective when the UI is bypassed, a client is modified, a token expires or the page refuses to close.

The standard does not permit direct access to RME databases or page-to-vendor rate execution. RME's existing authorised integration and queue mechanisms remain the operational route. Naming an action `publish` in a manifest neither creates the action nor authorises its execution.
