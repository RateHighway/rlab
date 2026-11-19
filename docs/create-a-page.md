# Create a RevenueLab Page

Official host use requires [central registration](central-registration.md).
The host's registration workflow must arrange central retention of the exact
page package and source archive, plus an authorized placement and successful
admission check before display. A local `offline-passed` or `design-checked`
report does not grant that permission. For a registered RevenueLab.build
builder, use the [one-ZIP upload workflow](#upload-to-revenuelabbuild) below;
the builder does not need a GitHub account or direct access to the private
central archive.

A useful first page answers one small business question, explains its limits
and asks for little access. This guide uses a synthetic fleet snapshot. It
offers two paths: a checked declarative design and the separate compiled
browser-page example.

## 1. Define the answer before building

Suppose Example Airport has 50 rentable Compact vehicles and 40 are already
committed in a daily snapshot. The committed fleet share is
`40 / 50 × 100 = 80%`, leaving 10 uncommitted units under these definitions.
Out-of-service vehicles are excluded from the rentable denominator.

That calculation does not establish demand, recommend a price or guarantee
availability throughout a future rental. Specify coverage, source observation
time and exclusions next to the result. Plan how zero capacity, missing data,
restricted locations and stale observations will appear.

Use invented records for examples and development. Do not include customer
records, personal reservation data, credentials or current nonpublic prices.

## 2. Confirm the host contract

Ask the host operator for the exact profiles, host API versions, components,
context keys, query contracts, permissions, limits and installation process it
implements. A `.rlab` filename alone does not establish compatibility.

The repository's host catalogue and capability files are synthetic fixtures.
They are useful for offline tests, not evidence of a live application or data
service. When no runtime exists, your result remains a checked design.

## 3. Use the declarative design path

The 0.3 Compose design describes a view in JSON. A future compatible renderer
would supply its own components and authorize named queries. The supplied
checker checks the design documents; it does not render or run them.

Start with
[`profiles/declarative-design-0.3/examples/level-1`](../profiles/declarative-design-0.3/examples/level-1/).
Copy it to a new working directory within that profile before editing. The
full `rlab-page.json` supplies required identity, publisher, support, surfaces,
permissions and contract references. Preserve these profile fields:

```json
{
  "standardVersion": "0.3",
  "profile": "RLAB-DECLARATIVE-DESIGN-0.3",
  "stage": "design-only",
  "capabilityLevel": 1,
  "runtime": {
    "kind": "declarative",
    "uiContract": "0.3.0"
  }
}
```

This is an excerpt, not a complete manifest. Changing `stage` does not create
an executable runtime. Use a new page ID for your own work and provide truthful
publisher and support details before submitting it outside a sandbox.

The example's `fleet` query binds to the synthetic
`com.example.fleet-summary` contract. Its location input comes from permitted
host context. It is not an arbitrary URL, SQL statement or permission grant.
Its view uses the supported `Text` and `DataTable` components:

```json
{
  "uiVersion": "0.3.0",
  "title": "Fleet Pressure View",
  "components": [
    {
      "type": "Text",
      "text": "Design preview with synthetic contracts. No live connection or action."
    },
    {
      "type": "DataTable",
      "query": "fleet",
      "columns": ["location", "class", "rentableUnits", "committedUnits"]
    }
  ]
}
```

The closed preview grammar also supports `ActionButton` and `WorkflowButton`
for the corresponding higher-level designs. It has no general formula
language, arbitrary HTML, custom JavaScript or unrestricted component system.
Current bindings use supported context keys or literal strings; they cannot
bind a selected table row or an earlier workflow step's output.

Run these commands from `profiles/declarative-design-0.3` for the supplied
example. Substitute your working directory when checking your own copy:

```sh
python -B tools/check_design.py examples/level-1
python -B -m unittest discover -s tests -v
```

Read the reported file, property and contract errors. Do not loosen a closed
schema to make an unsupported feature pass. Propose a versioned extension
when a new capability is needed.

To package the supplied examples, run the release tool from the repository
root, choosing a fresh output directory:

```sh
python -B tools/build_release.py --output build/tutorial-release
```

Design archives remain design-only. The public examples use version `0.1.1`
and include the applicable Apache-2.0 license; package metadata and the
bundled license changed from the earlier reference artifacts.

## 4. Use the separate browser-page path

The 0.2 example is compiled browser output: `app/index.html`, local CSS and
JavaScript, a manifest, README and license. It requests only `context.read`
and has no data service. The fleet values are fixed at 40 committed and 50
rentable units for a synthetic snapshot dated 2 October 2026. Host filter
changes do not recalculate those figures.

Copy
[`profiles/browser-readonly-0.2/examples/fleet-pressure`](../profiles/browser-readonly-0.2/examples/fleet-pressure/)
for your own page. If you change the page ID or version, update the constants
in `app/assets/page.js` as well as the manifest. A mismatch should prevent a
host session from starting.

You may use plain browser files or compile a frontend framework in your own
build environment. Package the compiled output. Keep scripts and styles in
separate local files so the host can enforce a strict content policy. Do not
ship credentials, installation grants, build hooks or a general host token.

From `profiles/browser-readonly-0.2`, package and validate the supplied example:

```sh
python -B tools/rlab.py pack examples/fleet-pressure tutorial-output/fleet-pressure-0.1.1.rlab
python -B tools/rlab.py validate tutorial-output/fleet-pressure-0.1.1.rlab --host examples/host-capabilities.json
python -B -m unittest discover -s tests -v
```

The output path must be outside the source directory and must not already
exist. Use a fresh filename for another build. The packer creates the parent
directory, writes the archive and checks it before reporting success.

`offline-passed` means the implemented checks passed. The reference validator
supports the schema keywords used by its pinned schemas; it is not a general
JSON Schema engine or a malware detector. Its host fixture does not prove
compatibility with an installed application.

Opening the example HTML directly deliberately fails to establish a session.
The host must supply reviewed origin configuration and the protocol described
in the [integration guide](host-integration.md).

## Upload to RevenueLab.build

This section applies only to RevenueLab.build, the RateHighway-operated host.
You need a RevenueLab account to upload or manage a page. Access is available
to registered members. Independent hosts choose their own upload workflow.
The package commands above remain useful for profile development; a builder
using RevenueLab.build does not need to make or upload a `.rlab` file.

Prepare **one `.zip` file, no larger than 25 MB**, with this layout:

```text
rlab-page.json
app/
  index.html
  assets/
README.md
LICENSE.txt
```

The **manifest**, `rlab-page.json`, describes the page, its version, entry
file and requested access. Keep it at the top of the ZIP. Set the entry to
an HTML file under `app/`, such as `app/index.html`, and keep the page ID and
version in `app/assets/page.js` equal to the manifest. Use separate local
script and style files. The host blocks inline scripts, inline styles and
assets loaded from another website.

For a compiled page, include original editable source and build instructions beside these files. Source is retained centrally for review and audit for every page version, with no exception or waiver, including staff and test pages. The checks confirm a matching source ZIP exists and is retained; they cannot prove original-source completeness or that the package was built from it.
RevenueLab.build does not compile code or run commands from the ZIP. If the
page uses React, Vite or another build tool, compile it first and place the
ready-to-run output under `app/`. Do not include passwords, keys, tokens or
customer records anywhere in the ZIP. Secret scanning covers source-only
files too.

RevenueLab.build builds the page package from the manifest, the files under
`app/`, the license file named by the manifest, and top-level `README.md`
and files whose names start with `LICENSE`, `LICENCE` or `NOTICE`. Other
files stay in the retained source ZIP and are not served as page files.
The same ZIP produces the same page package.

The page package accepts `.json`, `.html`, `.css`, `.js`, `.mjs`, `.png`,
`.jpg`, `.jpeg`, `.webp`, `.gif`, `.ico`, `.woff`, `.woff2`, `.txt`, `.md`
and `.csv`. Its limits are 2,000 files, 25 MB per file and
100 MB expanded. Archive files, native programs, WebAssembly,
`.env`, `.pem` and `.key` files are refused inside the package. Do not bundle
`__rlab/host-config.json`; the host supplies that file.

An assistant that can create files can provide the completed ZIP for the
builder to download. The builder selects it in the signed-in workspace's
Upload step or the upload step opened by an assistant reservation. A
reservation needs the exact ZIP's byte size and SHA-256 digest, a fingerprint
of its bytes; selecting a changed file will fail that match. Do not promise
that a particular assistant can create or transfer a file without testing
that client.

A passed upload check does not approve display, verify the page's calculations
or issue a certificate. Central retention still includes both the generated
page package and the source ZIP. The host's central admission, placement
approval, permissions and service grants still apply. A changed page needs a
new version; an existing registered version cannot be replaced with different
files.

## 5. Test behavior in the real development host

Use synthetic accounts and data. Record the exact package digest, host
release, profile, test inputs, expected outputs and observed results. Include:

- Correct results and visible assumptions for the chosen fleet definitions.
- Empty, denied, unavailable, partial and stale responses, where implemented.
- Context changes that cancel requests and discard old responses.
- Logout, suspension, expiry and restricted-user access.
- Keyboard use, visible focus, readable tables, 200% zoom and a 320 CSS-pixel
  layout.
- For browser pages, wrong origins, wrong frame sources, invalid sessions,
  repeated messages and failed bootstrap.

The supplied fixed browser example does not implement a dynamic fleet service
or every calculation edge case above. These are acceptance requirements for
your own page and its host. Do not report them as tested without evidence.

## 6. Submit an immutable release

Give the host operator the artifact, its purpose, requested access, inputs,
limits, dependency inventory, rights information, support route and test
evidence. The host reviews the actual bytes, checks compatibility and obtains
installation authority. Administrator approval does not grant rights beyond
the administrator's own authority.

Choose a new package version for a change and preserve the old artifact.
Describe permission expansions and behavior changes explicitly. Adding a
write, durable workflow or unattended trigger needs the corresponding host
implementation and additional review. Earlier read access does not authorize
those operations.

Your original page remains yours. Supplied examples and reused code retain
their applicable license obligations. A package validation report does not
issue a certificate or entitle the page to customer data.
