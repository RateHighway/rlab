# .rlab: user-created pages for independent applications

`.rlab` is a public, extensible package format developed by RateHighway
RevenueLab for applications that support custom, user-created pages.

Builders create focused tools, such as fleet summaries or rental operations
views. Host applications supply identity, permissions, data adapters and the
runtime. Use this repository to understand the contracts, create and check
packages, and implement a supported profile in your own application.

Independent hosting requires no RME purchase, RateHighway account or central
RateHighway service. Pages can use a host's own data and capabilities through
explicit, versioned contracts.

**Draft Standard.** This repository contains specifications, synthetic examples
and offline reference tools. It does not contain a production host, SDK,
service gateway, workflow runner or scheduler. No host is certified by the
presence of these files.

## Choose your path

| Goal | Start here |
| --- | --- |
| Understand the format and run the tools | [Getting started](docs/getting-started.md) |
| Create and package a page | [Create a page](docs/create-a-page.md) |
| Support user-created pages in your application | [Host integration](docs/host-integration.md) |
| Add capabilities while preserving compatibility | [Extensions and compatibility](docs/extensions-and-compatibility.md) |
| Implement with an AI coding agent | [Agent quickstart](docs/agent-quickstart.md) and [catalog.json](catalog.json) |
| Understand rights and participation | [Licensing](docs/licensing.md), [governance](GOVERNANCE.md) and [contributing](CONTRIBUTING.md) |

## What is implemented

| Profile | Included | Runtime status |
| --- | --- | --- |
| [`RLAB-PAGE-READONLY-0.2`](profiles/browser-readonly-0.2/README.md) | Closed manifest/host schemas, compiled synthetic browser page, archive packer and offline validator | Page code is supplied; an isolated HTTPS host and its protocol implementation are still required. |
| [`RLAB-DECLARATIVE-DESIGN-0.3`](profiles/declarative-design-0.3/README.md) | Closed document schemas, four synthetic designs, design checker and host catalogue fixture | Design-only. No rendering, actions, workflow execution or scheduling. |

The declarative design is the direction for a future host-rendered page path.
The browser profile is a separate, more isolated integration path. The highest
draft number is not automatically the right implementation target.

Levels describe behavior: **Read** uses authorized information; **Act** performs
a human-initiated operation; **Orchestrate** coordinates a bounded human-started
sequence; **Automate** starts unattended work. Levels do not grant permission.
Current executable browser sample tooling covers the read-only profile.

## Run locally

Use Python 3.11 or newer. The reference tools use the standard library only.
Run these commands from this repository's root:

```sh
python -B tools/check_repository.py
python -B tools/build_release.py --output build/release-0.1.0
```

The first command checks documentation links, catalog hashes, schemas,
examples and the tests. The second builds five newly licensed example
packages, their check reports, a source ZIP and a digest manifest into a new
directory. Choose a fresh output path on every build; existing output is
never replaced. Neither command deploys a host or contacts business services.

For one design:

```sh
python -B profiles/declarative-design-0.3/tools/check_design.py profiles/declarative-design-0.3/examples/level-1
```

`design-checked` means that the supplied document checks passed. It does not
mean the page ran. See [conformance and testing](docs/conformance.md).

## Public contracts and agent access

[catalog.json](catalog.json) maps profile IDs and historical schema identifiers
to actual files and SHA-256 digests in this repository. Pin a Git commit before
downloading those files. An HTTPS schema identifier is not a promise that a
web server currently serves it. The local tools resolve the bundled schemas.

Repository source version **0.1.0** is separate from standard versions `0.2`
and `0.3`, host API versions and example page versions. Published source
snapshots are identified by Git commit. Numbered artifacts follow the
[release process](docs/releases.md).

Canonical source: [RateHighway/rlab](https://github.com/RateHighway/rlab).
For an implementation, pin the chosen commit and read its catalog, schemas
and examples together. Contributions are welcome through
[issues](https://github.com/RateHighway/rlab/issues) and pull requests.

## Rights and commercial use

The technical material in this repository is licensed under
[Apache License 2.0](LICENSE), except the verbatim [DCO](DCO), which carries its
own notice. See [NOTICE](NOTICE) and [licensing details](docs/licensing.md).
Independent applications and original pages keep their own ownership and
distribution terms, subject to licenses for any material they reuse.

Supporting `.rlab` does not grant access to RateHighway services, customer
data or certification marks. Accurate compatibility claims are welcome;
branding and certification are covered by [TRADEMARKS.md](TRADEMARKS.md).
All examples use synthetic car rental data.
