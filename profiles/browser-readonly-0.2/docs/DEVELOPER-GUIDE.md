# Create and validate a RevenueLab Page

**Official host admission:** apply [RLAB-CENTRAL-ADMISSION-1](../../../docs/central-registration.md) in addition to this profile. Centrally retain every page package and source, record its host placements, and verify current central admission before display. The existing closed manifest grammar is unchanged; design-only content remains non-executable.

**Draft Standard 0.2 | Audience: developers and AI-assisted builders**

## Start with a useful question

Example: "Which locations have high fleet pressure over the selected rental period, and is the data complete enough to act on?" Build an informative read-only page. Make the denominator, time coverage and limitations visible. Do not connect rate publishing to this first exercise.

## 1. Choose the host and inspect its capabilities

Obtain its authenticated developer documentation and `rlab-host.json` capability document. The path is a proposed discovery convention, not a deployed endpoint. Verify supported standard and host API versions, bundle/remote support, context keys, services, scope vocabulary, package ceilings, support channel and approval process. The host catalogue describes potential capability; it does not confer access to any tenant.

Use `examples/host-capabilities.json` for offline checks. All its hosts and support URLs use reserved example domains and are illustrations. No RME API URL is supplied or claimed live.

## 2. Copy the example and make one change

Copy `examples/fleet-pressure/` to a new folder. Choose your own page ID and publisher ID. Set real ownership/support details before submitting outside a sandbox. Describe purpose, inputs, outputs, assumptions, dependencies, licence and support in README.

The included example displays fixed synthetic fleet pressure with explicit reserved/available assumptions. It has no pricing algorithm, production data or backend. Its small JavaScript demonstrates the draft handshake. It requires a conforming host to supply the reviewed parent-origin configuration; opening the HTML alone deliberately shows an unconnected state.

## 3. Build the page

Use any frontend framework, or plain HTML/CSS/JS. Compile locally or in your own isolated CI. Ship only browser output and allowed assets. Keep all scripts/styles in separate files so strict CSP does not need inline execution or `eval`. Do not load fonts, trackers or code from public CDNs by default.

Read host context; do not scrape the parent DOM. Use approved semantic services, with page-scoped access and minimum scopes. Treat remote responses as untrusted input; render text with safe DOM APIs. Handle loading, empty, partial, stale, permission-denied, service-unavailable and expired-session states. Abort in-flight requests and discard old results when contextVersion changes. Data from a previous tenant must never remain on screen after a switch.

For proprietary server-side calculations, use a separately reviewed customer backend. Declare external processing and retention accurately. Do not place secrets or proprietary processing that must stay secret into the browser bundle.

## 4. Write the manifest

Start from the included `rlab-page.json`. Keep requested scopes narrow; required scopes are a subset. Declare required service contracts and context honestly. Request optional capabilities only when the page has a tested fallback. `network.connect: []` means no additional external destination beyond a host-issued gateway. Do not hardcode a gateway or live host origin in a portable package.

Keep `support.url` and `license` truthful. `unspecified` does not grant rights; a real installation must resolve rights separately. A `.rlab` download or paid purchase does not grant data access. Do not put certification or administrator grants in the package.

## 5. Pack and run offline checks

From the kit root, using Python 3 (no third-party dependencies required):

```sh
python -B tools/rlab.py pack examples/fleet-pressure build/fleet-pressure-0.1.1.rlab
python -B tools/rlab.py validate build/fleet-pressure-0.1.1.rlab --host examples/host-capabilities.json
python -B -m unittest discover -s tests -v
```

Choose a fresh output path on each build; the packer refuses to replace an existing archive. The packer writes a ZIP under the `.rlab` extension and validates it before reporting success. The validator does not extract or execute package contents. Output is JSON, including digest, errors, warnings and checks not performed. Exit 1 means invalid; exit 2 means a tool/dependency failure. A passed report is `offline-passed`, never `certified`.

| Code | Corrective action |
|---|---|
| RL001 | Put exactly one valid `rlab-page.json` at archive root |
| RL002 | Correct the manifest/schema field identified |
| RL003 | Remove unsafe, duplicate or conflicting archive paths |
| RL004 | Supply a supported delivery mode and an existing HTML entry |
| RL005 | Use exact HTTPS origins and consistent remote URL/origin |
| RL006 | Remove unknown/write scopes or correct required/requested lists |
| RL007 | Match host versions, capabilities, services and limits |
| RL008 | Remove prohibited file types or obvious unsafe content |
| RL009 | Correct runtime handshake (host acceptance test, not offline test) |
| RL010 | Investigate digest mismatch; never replace approved bytes silently |
| RL011 | Reduce package size/count or repair malformed ZIP data |

Static text screening is deliberately limited. It is not a malware detector or complete JavaScript analyser. The schema checker supports only the keywords used in the pinned schemas and rejects unknown schema keywords; it is not a general JSON Schema implementation. Its URI/email checks are deliberately narrow. Independently run a maintained Draft 2020-12 validator with format checks before production adoption. A successful offline report still requires dependency/SBOM review, robust secret scanning, browser tests and host authorisation.

## 6. Preview and test behaviour

Import into the host's development environment with synthetic data. Test origin/source rejection, protocol mismatch, handshake timeout, missing required capability, optional permission denial, context updates, stale asynchronous results, token expiry, suspension and blocked external destinations. Test keyboard-only use, visible focus, meaningful title, zoom to 200%, 320 CSS-pixel narrow layout, readable tables, contrast and reduced motion. Do not label these completed without evidence.

For a fleet page: zero fleet must not divide by zero; unavailable units must not count as rentable; utilisation above 100% must produce a visible data warning; missing interval coverage must not be described as availability for the entire rental. For market pages: currency, taxes/fees, class mappings and rental dates must align before comparison.

## 7. Submit and operate

Submit the immutable archive, validator report, dependency inventory, functional tests, known limitations, screenshots, ownership evidence and support/licence details. The host reviews the actual digest. Administrator approval is required before using authorised customer data. Recheck entitlement and permissions on every launch and request.

Publish fixes as new versions. Test rollback and settings compatibility. Report vulnerabilities through the host's channel; do not post customer data in a public issue. A developer supports the page's calculations and UI unless a contract assigns that responsibility elsewhere.

## Build prompt

> Build a RevenueLab Page using Draft Standard 0.2 from this developer kit. First inspect the manifest schema and the selected host's capabilities. Use synthetic data and a full-page, read-only workspace. Ask for no unnecessary scopes. Keep scripts and CSS local. Implement exact-origin and source-checked handshake, session shutdown, context changes and clear error states. Make rental-period coverage, fleet denominator and data freshness visible. Provide the compiled app, manifest, README, dependency and licence notices, `.rlab` archive and validation output. Do not invent API endpoints, credentials, host support, certification or production functionality. Make one small change at a time and test it.
