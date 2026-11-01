# Contributing to .rlab

Builders, independent host developers and connector maintainers can propose
improvements without buying a RateHighway service. Begin with a focused issue
describing the problem, affected profile and expected behavior. Submit a pull
request with the smallest complete change and synthetic test fixtures.

## Reuse rights and sign-off

Contributions use the license applicable to the changed files. Contributors
retain ownership; no copyright assignment is required. Read [DCO](DCO) and
sign off only when you can truthfully certify it. A sign-off records your
submission rights and becomes part of the public record.

```sh
git commit -s
```

Use your own identity. AI-assisted contributions need a responsible person's
review of correctness, provenance and rights. Agents must not fabricate a
human sign-off. Do not submit private code, secrets or customer data.

## Technical changes

1. Select the affected profile and read its normative source documents.
2. Describe the compatibility impact and migration path. Keep existing profile
   semantics stable; a new extension does not become an accepted field merely
   because a tool can parse JSON.
3. Include positive and negative fixtures for changed behavior. Keep example
   manifest versions synchronized with executable assets where applicable.
4. Refresh the generated catalog and run the checks from the repository root:

   ```sh
   python -B tools/update_catalog.py
   python -B tools/check_repository.py
   ```

5. Update the guides and [CHANGELOG.md](CHANGELOG.md). State what the tests
   establish and what remains untested.

For core proposals, use [GOVERNANCE.md](GOVERNANCE.md). Changes expanding
permissions, remote destinations, action effects or execution modes require
explicit review. Do not weaken unknown-field rejection to add flexibility.

Report vulnerabilities through [SECURITY.md](SECURITY.md), not a public issue
containing exploit details or sensitive data.
