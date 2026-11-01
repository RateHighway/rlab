# Design rationale, migration and sources

**Draft Standard 0.2. Public source edition prepared 2026-10-31.**

## Why a separate host contract

RevenueLab Pages is the generic name for user-created pages packaged to the
`.rlab` format in independent applications. A page inside RateMonitor Elite
is an RME Custom Page. An independent host does not need an RME deployment.

The package declares its identity, requirements, browser entry point and data
handling. The host controls identity, installation, approved artifact digest,
effective permissions, origin isolation and lifecycle. Business access runs
through authorized host adapters rather than broad credentials inside a page.

This draft deliberately separates a small public bootstrap from the later
session message. Exact frame-source/origin checks, session binding, independent
message sequences and context versions make those boundaries explicit. They
are requirements for an implementation, not proof that a host already meets
them.

The reference validator keeps a closed read-only grammar and exact decimal
limits. It checks archive and declared compatibility properties offline.
Runtime isolation, application authorization, publisher trust and operational
conformance require separate evidence.

## Updating a page

1. Preserve the previous artifact, manifest, digest and installation record.
2. Modify source against an explicitly selected profile and host API range.
3. Review context, permissions, services and network changes. Implement their
   runtime behavior rather than only changing declarations.
4. Increase the page version, retain its identity for the same product, and
   build a fresh archive with a new digest.
5. Run offline validation and relevant browser/host tests. Obtain any required
   rights, installation approval and expanded permission authorization.
6. Stage beside the previous version, switch atomically where supported, and
   verify rollback under current policy. Revoked rights must not return.

Migration from a different package format or profile is an explicit conversion,
not a filename change. Preserve the old bytes and review the complete new
contract. The strict 0.2 validator does not accept legacy aliases or 0.3
declarative designs.

## Public source edition

This edition preserves the 0.2 schema and protocol identifiers. Public sample
version `0.1.1` adds explicit Apache-2.0 licensing and updated documentation;
the browser's `pageVersion` matches the manifest.

Future production hosts still need a runtime, secure adapter contracts,
publisher review, actual capability discovery, accessibility/security tests
and operating procedures. Certification remains a separate proposed process.
No operational service or approval is created by publishing source files.

## Primary technical references

The profile's design was informed by these public references. They are not
endorsements or claims that a particular implementation is secure:

- [MDN iframe](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/iframe)
- [MDN postMessage](https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage)
- [MDN Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy)
- [OAuth security best current practice, RFC 9700](https://www.rfc-editor.org/info/rfc9700/)
- [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12)

Use the pinned local schemas and the exact profile specification for validation.
Browser security guidance and third-party standards do not certify a
RevenueLab host or create customer data access.
