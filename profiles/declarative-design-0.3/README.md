# Declarative design profile 0.3

**Draft Standard:** `RLAB-DECLARATIVE-DESIGN-0.3`, standard version `0.3`,
`stage: "design-only"`. These documents and fixtures describe a narrow
declarative contract. They are not an execution runtime or a production
archive/security validator.

| Level | Name | Execution ability being designed |
| --- | --- | --- |
| 1 | Read | Authorized data and interactive views |
| 2 | Act | User-initiated controlled operations |
| 3 | Orchestrate | Person-started durable workflows |
| 4 | Automate | Unattended event/schedule initiation under a separate mandate |

Levels are capability ceilings, not trust scores or permission grants. A
scheduled read-only report is still Level 4. This kit does not execute any of
these levels: it checks the supplied design documents and cross-references.

## Documents

- [Standard design](docs/STANDARD-0.3.md)
- [Builder and host implementation guide](docs/BUILDER-AND-HOST-GUIDE.md)
- [Action, workflow and automation controls](docs/ACTIONS-AND-AUTOMATION.md)
- [Adoption, assurance and migration](docs/ADOPTION-AND-ASSURANCE.md)

The broader prose includes proposed future interfaces. Only the small grammar
in `schemas/` is accepted by the checker. It has Text, DataTable, ActionButton
and WorkflowButton components; bounded query/action contracts; constrained
bindings; and acyclic query/action/approval workflow designs. It has no
generic manifest extension field, arbitrary component code, expression
evaluator, branching workflow engine or live automation service.

## Check the examples

From this profile directory, using a supported Python 3 release:

```sh
python -B tools/check_design.py examples/level-1
python -B tools/check_design.py examples/level-2
python -B tools/check_design.py examples/level-3
python -B tools/check_design.py examples/level-4
python -B -m unittest discover -s tests -v
```

No third-party Python dependency is needed. `fixtures/host-catalog.json` is a
synthetic catalogue, not a live host capability statement or service.
Successful checks report `design-checked`. They do not render UI, read data,
create tasks, run workflows, schedule jobs or authorize a mandate.

For design-only archives, run `python -B tools/build_release.py --output
build/first-release` from the repository root, choosing a fresh directory.
Each supplied example is version `0.1.1` and includes a complete Apache-2.0
license. The closed manifest license object records only `status`; the README
and LICENSE.txt state the actual license. No unsupported fields are added.

The sibling [browser read-only profile](../browser-readonly-0.2/README.md)
supplies the separate 0.2 archive and browser contract. A higher draft number
does not make this 0.3 design executable or automatically compatible with 0.2.
No host, SDK, workflow runner, scheduler or certification service is supplied.
