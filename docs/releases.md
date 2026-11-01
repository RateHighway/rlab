# Releases and reproducible consumption

The central-registration source snapshot is repository version `0.2.0`. It includes
standard version `0.2`, standard version `0.3` and synthetic example page
version `0.1.1`. These versions identify different contracts.

Current standards are drafts. 0.3 remains design-only, and publishing a
repository release does not promote it into an executable or stable profile.
Future stable public interfaces follow Semantic Versioning. Incompatible
changes require a major version; compatible additions a minor version; fixes
a patch version. Released bytes are immutable.

## Prepare artifacts

From a reviewed source checkout:

```sh
python -B tools/check_repository.py
python -B tools/build_release.py --output build/release-0.2.0
```

Use a new output directory for every attempt. The builder refuses an existing
directory and never deletes prior artifacts. It checks the catalog, packages
the five examples and writes:

- The read-only browser example `.rlab` archive.
- Four declarative design `.rlab` archives, which remain non-executable.
- A source ZIP for each page, with its manifest at the archive root, for
  submission to the central repository alongside the exact `.rlab` package.
- Profile check reports and `rlab-source-0.2.0.zip`.
- `release-manifest.json` containing digests, source-file hashes and the
  source commit when building from this repository's clean, dedicated Git root.
- `SHA256SUMS` for all other files in that output directory.

ZIP entry ordering and timestamps are fixed. Compare repeated-build digests
in the same tested environment; compression-library differences can affect
compressed bytes. The manifest records the Python and zlib versions. A
checksum binds bytes; it is not an independent publisher signature.

Building an artifact does not register it or authorize a host to display it.
Follow [central registration](central-registration.md): retain the package and
source in `RateHighway/rlab-pages`, then obtain an authorized host placement.
Source retention alone does not establish that a binary was built from it.

`catalog.json` is generated from profile sources. After an intentional source
change, run `python -B tools/update_catalog.py`, review its diff and commit it
with that change. CI checks for drift; it does not silently regenerate a
changed catalog.

## Publish separately

Publishing source, issuing a release and deploying a host are separate actions.
Create the public repository with fresh history containing only this technical
tree. Do not import private repository history, operational records or website
assets. Run checks on the published checkout and inspect CI before calling
them successful on GitHub.

For a numbered public release, bind the tag to a reviewed source commit and
build from a clean checkout of that commit. Upload the resulting artifacts,
manifest and checksums. Confirm anonymous retrieval of the actual source,
schemas and release files before advertising download links. Do not claim
that historical schema-ID URLs have become reachable simply because the
schemas are in Git.

Agents should pin the commit or release artifact digest. A moving branch or
tag name alone does not fix bytes. Never replace an existing release asset
with different bytes under the same identity.

Support for each draft is limited to its published source and actual test
evidence; no response-time or production support promise is made. Stable
interfaces will publish their supported versions and retirement dates before
adoption. Commercial support is a separate agreement.
