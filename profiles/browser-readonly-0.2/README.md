# Browser read-only profile 0.2

**Draft Standard:** `RLAB-PAGE-READONLY-0.2`, standard version `0.2`, host API
`0.2.0`. This profile packages an isolated browser page for a full-page
workspace. It defines no operational writes.

The included HTML/CSS/JavaScript sample and Python tooling are usable source
artifacts. A conforming host implementation is still required to launch the
sample in an authorized session. Opening its HTML directly intentionally shows
an unconnected state. No RME service, host runtime or production SDK is included.

## Read in this order

1. [Format and structure](docs/RLAB-PAGE-STANDARD.md)
2. [Create and validate a page](docs/DEVELOPER-GUIDE.md)
3. [Implement a host](docs/HOST-INTEGRATION-GUIDE.md)
4. [Conformance evidence and certification proposal](docs/HOST-CERTIFICATION.md)
5. [Design rationale and migration](docs/DECISIONS-AND-SOURCES.md)

The profile includes strict local manifest/host schemas, the synthetic Fleet
Pressure Summary sample, an offline archive validator and packer, and positive
and negative tests. Schema identifiers are preserved contract identifiers;
validators load the pinned files from `schemas/` rather than fetching an
untrusted package-selected URL.

## Run the tools

Use a supported Python 3 release. There are no third-party Python dependencies.
From this profile directory:

```sh
python -B tools/rlab.py pack examples/fleet-pressure build/fleet-pressure-0.1.1.rlab
python -B tools/rlab.py validate build/fleet-pressure-0.1.1.rlab --host examples/host-capabilities.json
python -B -m unittest discover -s tests -v
```

Choose a fresh output path for each local build. The packer refuses to replace
an existing destination. The example is version `0.1.1`, with explicit
Apache-2.0 rights and a self-contained license file; this is a new artifact
identity, separate from prior review samples.

For a complete repository artifact set, run `python -B tools/build_release.py
--output build/first-release` from the repository root, choosing a fresh
directory.

Exit 0 means only the implemented offline checks passed. The reference checker
implements the schema keywords used by these pinned schemas, not arbitrary
JSON Schema. It does not verify a browser runtime, publisher identity,
licenses, malware absence, host permissions or certification.

The sample displays fixed synthetic 40 committed / 50 rentable = 80% fleet
pressure. It requests only `context.read`, uses no business data service and
does not recalculate when host filters change. No real credentials or
production data are needed for offline commands. Independent hosts may
implement this profile without an RME purchase or RateHighway-operated gateway.
