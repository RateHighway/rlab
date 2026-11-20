# RevenueLab Page Package Standard, Browser Profile 0.4

**Draft Standard 0.4, in development | 2026-11-19 | Profile `RLAB-PAGE-0.4`**

No host supports this profile yet. `RLAB-PAGE-READONLY-0.2` is unchanged and
stays supported. `RLAB-DECLARATIVE-DESIGN-0.3` is a separate design-only
profile; 0.4 is the next browser-page version, not a successor to 0.3.

MUST and MUST NOT are requirements of this draft. SHOULD allows a documented
equivalent control.

## 1. What 0.4 is for

Use 0.4 for a browser page that **saves Utilization 4 location group and car
group changes**. Use 0.2 for a page that only reads. A 0.4 page may also be
read only; it then differs from 0.2 only by its required preview images.

## 2. Everything is as in 0.2 except these items

The container, archive safety rules, size limits, delivery modes, lifecycle,
context keys, bridge messages, isolation and gateway rules are those of the
[0.2 standard](../../browser-readonly-0.2/docs/RLAB-PAGE-STANDARD.md) and the
[0.2 host guide](../../browser-readonly-0.2/docs/HOST-INTEGRATION-GUIDE.md).
The differences:

| # | Item | 0.4 rule |
| --- | --- | --- |
| 1 | Identity | `standard` `rlab.page`, `standardVersion` `"0.4"`, `profile` `RLAB-PAGE-0.4`, `$schema` and schema `$id` `https://revenuelab.ratehighway.com/schemas/rlab-page/0.4/schema.json` |
| 2 | Host API | `0.4.0`. A 0.4 page declares `hostApi` `minimum` `0.4.0`, `maximumExclusive` `0.5.0`. Bridge messages are unchanged, including the envelope's `protocolVersion` `"0.2"`. The session's `grantedPermissions` may hold `utilization.manage` |
| 3 | `preview` | Required top-level object with a mockup and a thumbnail. Replaces the 0.2 extension key `com.ratehighway.rlab.preview` |
| 4 | `utilization.manage` | New permission. Lets the page ask the host's utilization service to create, update and delete location groups and car groups, and to undo a change. Nothing else |
| 5 | Host duties for a write | Section 5 |
| 6 | Page duties for a write | Section 6 |
| 7 | Not in 0.4 | Section 7 |

The machine-readable contract is
[`schemas/rlab-page-manifest-0.4.schema.json`](../schemas/rlab-page-manifest-0.4.schema.json)
and [`schemas/rlab-host-0.4.schema.json`](../schemas/rlab-host-0.4.schema.json).
Both stay closed: unknown fields are refused.

## 3. Preview images

```json
"preview": {
  "mockup": {"path": "app/assets/preview/mockup.png", "width": 1600, "height": 900,
             "alt": "Car group manager for sample Location AAA listing four car groups, sample data."},
  "thumbnail": {"path": "app/assets/preview/thumbnail.png", "width": 640, "height": 360,
                "alt": "Four sample car groups for Location AAA with their car classes."}
}
```

- `path` MUST be exactly `app/assets/preview/mockup.png` or `.webp`, and
  `app/assets/preview/thumbnail.png` or `.webp`.
- The file MUST be in the package, MUST be a real PNG or WebP matching its
  extension, and MUST be exactly 1600 x 900 (mockup) or 640 x 360 (thumbnail).
- The mockup MUST be at most 1,000,000 bytes; the thumbnail at most 200,000.
- `alt` MUST be 1 to 150 characters.
- Content rules are those of [page preview images](../../../docs/preview-images.md):
  captured from the real page with synthetic data, page area only, no added
  logos. A preview MUST NOT be drawn or generated.

The images are untrusted page content. They grant nothing and are not evidence
that the page works.

## 4. The `utilization.manage` permission

A page that requests `utilization.manage`:

- MUST also request `utilization.read` (checker code RL017);
- MUST declare at least one service with `"required": true` (RL018), the
  utilization service its changes go through;
- if it lists `utilization.manage` in `required`, MUST also list it in
  `requested` (RL006, the 0.2 rule).

Requesting the permission is a request, not a grant. A host MUST NOT send
`utilization.manage` in a session for a 0.2 page.

## 5. What a host MUST do for a write

For every change a page asks for, the host:

1. MUST decide, per viewer and per request, whether this viewer may change
   data here. A launch grant is not enough on its own.
2. MUST check that its own service grant for this page allows changes, not
   only reads.
3. MUST apply the change immediately or refuse it. A refusal carries a stable
   code, a plain-language message and a next step the page can show unchanged.
4. MUST record who made the change, when, the exact before and after, and how
   to reverse it.
5. MUST offer undo of a recorded change.

A host MAY add its own confirmation step before applying a change.
RevenueLab.build does not: the page saves directly, and every change is logged
and can be undone. A host MUST NOT let a page widen its access: the effective
access is the intersection of the page's request, the administrator's grant,
the viewer's rights and the host's policy, checked on every request.

## 6. What a page MUST do for a write

- MUST send one idempotency key per intended change, and reuse that key only
  to retry that same change.
- MUST show the service's message and next step unchanged.
- MUST NOT retry a refusal silently.
- MUST label sample data as sample.
- MUST NOT store the access token: memory only, never in storage, a URL, a log
  or analytics.

## 7. Not in 0.4

Any other write, rate changes, personal reservation data and server execution.
A page that needs any of these needs a later, separately versioned profile.

## 8. The service contract is separate

The standard names the permission and the duties. The HTTP routes, request and
response shapes of a utilization service belong to that service's own versioned
contract, declared in `services` by `id` and version range. The RevenueLab.build
Utilization 4 service (`com.ratehighway.utilization4.query`) publishes its own
contract; its write routes are in development and not live.

## 9. Offline checker codes added in 0.4

| Code | Meaning |
| --- | --- |
| RL012 | The manifest has no `preview` field |
| RL013 | A declared preview file is not in the package |
| RL014 | A preview file is not a real PNG or WebP, or its content does not match its extension |
| RL015 | A preview file's pixel size is not exactly 1600 x 900 or 640 x 360 |
| RL016 | A preview file is too large on disk |
| RL017 | `utilization.manage` requested without `utilization.read` |
| RL018 | `utilization.manage` requested with no required service |

Codes RL001 to RL011 keep their 0.2 meaning. Every 0.4 error also carries a
`nextStep`. A passing report is `offline-passed`, never approval, admission or
certification.
