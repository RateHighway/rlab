# Changelog

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
