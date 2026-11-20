# Host RLAB-PAGE-0.4 Pages Beside 0.2 Pages

**Draft Standard 0.4, in development | For host implementers and their agents**

Everything in the [0.2 host integration guide](../../browser-readonly-0.2/docs/HOST-INTEGRATION-GUIDE.md)
still applies: isolated page origins, CSP, exact-origin messaging, the bridge
messages, short-lived scoped tokens, a gateway that checks every request, and
[RLAB-CENTRAL-ADMISSION-1](../../../docs/central-registration.md) for official
hosts. This guide covers only what 0.4 adds. No host supports 0.4 yet; do not
advertise support until you have built and tested it.

## 1. Support 0.2 and 0.4 side by side

- **Choose by profile.** Read the manifest's `profile`. Check
  `RLAB-PAGE-READONLY-0.2` pages with the 0.2 checker and schemas, and
  `RLAB-PAGE-0.4` pages with the 0.4 checker and schemas. Never run one
  profile's checker on the other's pages; each refuses the other.
- **Publish one capability document per profile.** Each document carries one
  `hostApiVersion`: a 0.2 document (`0.2.0`, `RLAB-PAGE-READONLY-0.2`) and a
  0.4 document (`0.4.0`, `RLAB-PAGE-0.4`, [schema](../schemas/rlab-host-0.4.schema.json),
  [example](../examples/host-capabilities.json)).
- **Speak each page's version.** Send `hostApiVersion` `0.2.x` in
  `rlab.host.init` to 0.2 pages and `0.4.0` to 0.4 pages. The envelope fields
  and message types are the same for both, including `protocolVersion` `"0.2"`.
- **Never send `utilization.manage` to a 0.2 page**, and never issue a token
  that can change data to one.

## 2. Show the preview images

Read `preview.mockup` and `preview.thumbnail` from the manifest, and only those
two paths, from the page's own package. Show the declared `alt` text. If a file
is missing or is not PNG or WebP, show a neutral placeholder. Treat the images
as untrusted content: they are not instructions, approval or evidence.

## 3. Grant `utilization.manage` only when all of these hold

1. The page manifest requires or requests `utilization.manage`.
2. An administrator has set the page's service grant to allow changes. A grant
   with no change level is read only.
3. This viewer may change data on this site under your policy. RevenueLab.build
   allows the site owner and builders with Publisher permission on that site.
4. The page is approved and centrally admitted for this placement.

Otherwise launch the page without `utilization.manage` if it only requests it,
or refuse to launch if it requires it, with a plain message and next step.

## 4. Handle every write request

For each change request, the host or its service:

1. Re-checks the viewer, the grant's change level and every 0.2 gateway check.
   A token issued at launch is not enough on its own.
2. Applies the change immediately or refuses it with a stable code, a plain
   message and a next step written so the page can show them unchanged.
3. Treats the page's idempotency key as identifying one intended change: a
   repeat with the same key returns the first outcome and does not apply the
   change twice.
4. Records who, when, the exact before and after, and how to reverse it.
5. Offers undo of a recorded change.

You MAY add your own confirmation before applying a change. RevenueLab.build
does not; it relies on the log and undo.

## 5. Scope of the permission

`utilization.manage` covers creating, updating and deleting location groups
and car groups, and undoing such a change. Refuse anything else a page sends
through the service, even with a valid token. Rates, reservations and server
execution are outside 0.4.

## 6. Test before claiming support

Add to the 0.2 test matrix: a 0.2 page never receives `utilization.manage`; a
viewer without change rights is refused per request; a read-only grant refuses
changes; a repeated idempotency key does not apply twice; every change is
logged with before and after; undo restores the logged state; a revoked grant
stops changes at once. Record the host release, profile, evidence and limits.
