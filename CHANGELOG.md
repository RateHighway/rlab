# Changelog

## Page preview images - 2026-11-19

- Added [page preview images](docs/preview-images.md): a mockup
  (1600 x 900) and a thumbnail (640 x 360) under `app/assets/preview/`,
  declared in `extensions` under `com.ratehighway.rlab.preview` with exact
  sizes and alt text, captured from the real page with synthetic data.
- Recommended for every `RLAB-PAGE-READONLY-0.2` page and planned to be
  required in the next browser page profile. The 0.2 schema, the reference
  validator and every existing page are unchanged; no checker refuses a page
  without preview images.

## RevenueLab.build upload guide - 2026-11-17

- Explained the one-ZIP builder upload in the creation, getting-started and
  agent guides, including compiled files, source retention, limits and the
  builder's file-selection step.
- Kept this workflow specific to RevenueLab.build. Profile contracts,
  independent-host tooling, central retention and admission policy are
  unchanged. No host or service is deployed by these documentation edits.

## Central policy amendment - 2026-11-13

- `RLAB-CENTRAL-ADMISSION-1` now states that central reviewers may delegate
  routine approval to a policy workflow they control in the central archive,
  and records the first authorized rule: low-risk `development` display
  placements on a named RateHighway test host installation, for bundled
  `RLAB-PAGE-READONLY-0.2` pages that pass the checks and request only
  `context.read`, no services and no network destinations.
- A host still cannot permit or approve its own records. The policy
  identifier, record schemas, admission checker, lease limit and refresh
  limit are unchanged. No workflow or host is deployed by this text.

## Public repository maintenance - 2026-10-31

- Removed internal maintenance and infrastructure records from the public
  source tree and navigation; retained technical and contributor guidance.
- Limited release source ZIPs to the declared public root files and source
  directories. Local root notes and working directories are excluded.

## 0.2.0 - Central registration and host admission

- Required `RLAB-CENTRAL-ADMISSION-1` for official host admission, with centrally
  archived page packages/source and leased host placement records.
- Registration/deployment schemas, an authoritative-head admission checker and
  offline central-repository audit. Existing structural checks explicitly
  report that central admission was not performed.
- Per-page source archives in release builds. Existing page profile IDs,
  closed manifest grammars and 0.1.1 reference package versions are preserved.
- Public implementation rights remain Apache-2.0; host operation under the
  official central policy now requires registration. No runtime host is added.

## 0.1.0 - Initial public source snapshot

- Public technical source for the Draft 0.2 read-only browser profile and
  Draft 0.3 declarative design profile.
- Independent host, builder, extension and agent guides.
- Apache-2.0 technical material and newly licensed 0.1.1 synthetic examples.
- Offline validators, packer, unit tests, catalog and fresh-output release
  builder. No production host, SDK or runtime service is included.

This is the repository source version, not a renumbering of either Draft
Standard. Source publication does not imply a numbered GitHub release or a
deployed host.
