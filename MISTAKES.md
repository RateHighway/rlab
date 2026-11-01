# Maintenance lessons

Record meaningful findings as: what happened, root cause, cost and rule.
## 2026-10-31 - Central identity needs an immutable execution boundary

**Found:** Admission design review identified three ways that a matching-looking
registration could fail to bind actual page code: local Git replacement
objects, a remote URL whose served code changes, and an official branch update
whose required registry checks have not passed.

**Root cause:** A repository label or package URL was being treated as enough
evidence of immutable, approved bytes.

**Cost:** One pre-publication review and regression-test pass; no host or
customer deployment used the unfinished admission path.

**Rule:** Read commit objects with replacements disabled, admit only bundled
browser code under the central policy, and verify the current official commit's
successful registry workflow. Registration tests cover each denial path.
