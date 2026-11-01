# Get started with .rlab

`.rlab` is a draft package format for user-created pages in compatible
applications. A page declares its identity, supported profile and requested
capabilities. The application, called the **host**, decides whether it can
support the page and what the page is permitted to do.

The shared goal is independent adoption: a rental operations application,
fleet application or another suitable host can support its own builders.
RevenueLab Pages is the generic name. Inside RateMonitor Elite, such pages
are called RME Custom Pages. Supporting the format does not grant access to
RateHighway services or another organization's records.

## Choose the right starting point

There are two separate draft profiles in this repository. They are not
interchangeable, and the higher version number does not mean a production
runtime is included.

| Starting point | Included material | What you can do now | What you must implement |
| --- | --- | --- | --- |
| [Browser read-only 0.2](../profiles/browser-readonly-0.2/README.md) | Manifest and host schemas, compiled HTML/CSS/JavaScript example, offline archive validator, packer and tests | Inspect and package the example; check its archive, manifest and declared compatibility | An isolated browser-page host, installation approval, protocol and operational controls; a gateway if data services are added |
| [Declarative design 0.3](../profiles/declarative-design-0.3/README.md) | Closed design schemas, four synthetic Level 1–4 examples, document checker and tests | Edit and check a Compose design and its contract references | An explicitly versioned executable profile and renderer; data, action, workflow or scheduling services as required |

The 0.2 example contains actual browser output. It deliberately stays
disconnected when opened without its development host. The 0.3 examples carry
`stage: "design-only"`; they do not run reads, writes, workflows or schedules.
Neither kit supplies a deployed host, production credentials or a certified
implementation.

## Run the source checks

Use Python 3.11 or newer and Git for the full test suite. The Python tools use
the standard library and need no third-party package installation. Online
central admission also requires authenticated GitHub CLI access to the private
central repository. From the repository
root, run the repository checks:

```sh
python -B tools/check_repository.py
```

These are offline source checks, not host admission. For official host use,
every page package and source archive must be retained centrally, and each
application placement must pass [central admission](central-registration.md)
before it is enabled or displayed.

To inspect one profile separately, change into its directory. For the browser
example:

```sh
cd profiles/browser-readonly-0.2
python -B -m unittest discover -s tests -v
python -B tools/rlab.py pack examples/fleet-pressure tutorial-output/fleet-pressure-0.1.1.rlab
python -B tools/rlab.py validate tutorial-output/fleet-pressure-0.1.1.rlab --host examples/host-capabilities.json
```

The packer refuses to replace an existing output. Choose a new output name if
you have already run the example, and use that same name in the validation
command. Generated output is a new local artifact, not a published release.

For the declarative design examples, start again from the repository root:

```sh
cd profiles/declarative-design-0.3
python -B tools/check_design.py examples/level-1
python -B tools/check_design.py examples/level-2
python -B tools/check_design.py examples/level-3
python -B tools/check_design.py examples/level-4
python -B -m unittest discover -s tests -v
```

A passed check establishes only the rules implemented by that checker. It
does not establish browser behavior, business correctness, secure hosting,
publisher identity, data rights or certification.

## Build one useful page

Choose a question with an answer you can verify. For example: "How much of
the rentable fleet is committed in this daily snapshot?" Start with synthetic
data, one location and read-only behavior.

1. Obtain the intended host's implemented profile and capability documentation.
2. Choose the corresponding example and keep its required version fields.
3. Describe your inputs, expected result, assumptions and limitations.
4. Request only the capabilities the page needs.
5. Run the appropriate offline checks.
6. Test the exact artifact in a compatible synthetic development host before
   requesting installation with real data.

The [creation guide](create-a-page.md) follows this sequence. The
[host integration guide](host-integration.md) explains the application work.

## Understand the four levels

| Level | Meaning | Example |
| --- | --- | --- |
| 1 Read | Authorized reads and analysis | A fleet snapshot table opened by a person |
| 2 Act | A person initiates a specific controlled operation | A reviewed task-creation request |
| 3 Orchestrate | A person starts a durable bounded sequence | A review workflow with approval checkpoints |
| 4 Automate | A schedule or event initiates work under a separate mandate | A scheduled read-only report |

Levels describe execution abilities. They are separate from trust, permissions
and certification. An asynchronous operation started by a person can remain
Level 2. A recurring report can be Level 4 even when it performs no writes.

## Use a release consistently

For reproducible work, obtain a specific repository release or source commit
and use its schemas, examples and tools together. Verify published artifact
digests against trusted release metadata. A digest identifies bytes; it does
not establish who published them.

Schema identifiers inside manifests are contract identifiers. Their presence
does not prove that a web server is serving a schema at that address. The
supplied tools use the local pinned schemas. Consult the release index and
actual downloadable files when integrating other validators.

The repository's [license](../LICENSE) describes rights in supplied material.
Your original application and page code retain their own ownership, subject
to any obligations arising from reused material. Service admission, customer
authorization and certification are separate decisions.
