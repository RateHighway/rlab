# Create and Check an RLAB-PAGE-0.4 Page

**Draft Standard 0.4, in development | Audience: AI agents and the builders they work for**

No host supports 0.4 yet. Build 0.4 pages to prepare and test; do not tell a
builder a 0.4 page can be used live until their host says it supports 0.4.

**Official host admission:** apply [RLAB-CENTRAL-ADMISSION-1](../../../docs/central-registration.md)
as for 0.2. Every page version's package and source are retained centrally.

## 1. Choose 0.2 or 0.4

| The page... | Use |
| --- | --- |
| only reads data | `RLAB-PAGE-READONLY-0.2` (works on hosts today) |
| saves Utilization 4 location group or car group changes | `RLAB-PAGE-0.4` |
| changes anything else (rates, reservations, other settings) | Neither. Not allowed in any current profile |

## 2. Start from the example

Copy [`examples/group-manager/`](../examples/group-manager/) to a new folder.
Change the page ID, publisher, support details and version in
`rlab-page.json`, and the same ID and version at the top of
`app/assets/page.js`. A mismatch stops the host session.

## 3. Write the manifest

Start from the example. The parts that differ from 0.2:

```json
"standardVersion": "0.4",
"profile": "RLAB-PAGE-0.4",
"hostApi": {"minimum": "0.4.0", "maximumExclusive": "0.5.0"},
"permissions": {
  "requested": ["context.read", "utilization.read", "utilization.manage"],
  "required": ["context.read", "utilization.read", "utilization.manage"]
},
"services": [{"id": "com.ratehighway.utilization4.query", "minimum": "1.0.0",
              "maximumExclusive": "2.0.0", "required": true}],
"preview": { "mockup": {...}, "thumbnail": {...} }
```

Ask for `utilization.manage` only if the page saves group changes. If it
does, also ask for `utilization.read` and require the utilization service.

## 4. Build the save the way 0.4 requires

- Make one idempotency key per change the person intends (for example
  `crypto.randomUUID()` when they press Save). Reuse it only to retry that
  same change.
- When the service refuses, show its message and next step exactly as sent.
  Do not reword them and do not retry on your own.
- Keep the access token in a variable only. Never put it in storage, a URL,
  logs or analytics.
- Label sample data "Sample".
- Use the host's published service contract for the actual call. Do not guess
  routes. The example deliberately leaves `sendGroupChange` as a stub that
  refuses every change.

The host applies a change at once (RevenueLab.build adds no confirmation),
logs it and offers undo. Tell the builder that in the page, near the Save
control.

## 5. Capture the preview images

1. Open the page directly in a browser so it shows its sample data.
2. Capture the page area at twice the size (3200 x 1800), for example:
   `msedge --headless=new --hide-scrollbars --force-device-scale-factor=2 --window-size=1600,900 --screenshot=mockup-2x.png file:///.../app/index.html`
3. Reduce to exactly 1600 x 900 and save as `app/assets/preview/mockup.png`.
4. For the thumbnail, crop a copy of the capture to the main result at 16:9
   and reduce it to exactly 640 x 360 as `app/assets/preview/thumbnail.png`.
5. Write one-sentence `alt` text for each, 150 characters or fewer.

If you cannot open and capture the page, say so and tell the builder how to
take the two screenshots. Never draw, generate or reuse an old image.

## 6. Pack and check

From `profiles/browser-0.4`, using Python 3 with no extra packages:

```sh
python -B tools/rlab.py pack examples/group-manager build/group-manager-0.1.0.rlab
python -B tools/rlab.py validate build/group-manager-0.1.0.rlab --host examples/host-capabilities.json
python -B -m unittest discover -s tests -v
```

Choose a fresh output path each time. Exit 0 and `offline-passed` mean only
that the offline checks passed. Each error has `code`, `path`, `message` and
`nextStep`; pass the message and next step to the builder unchanged.

| Code | What to do |
| --- | --- |
| RL001 to RL011 | As in the [0.2 developer guide](../../browser-readonly-0.2/docs/DEVELOPER-GUIDE.md) |
| RL012 | Add the top-level `preview` object |
| RL013 | Put the image file at the declared path |
| RL014 | Save a real PNG or WebP whose extension matches its content |
| RL015 | Resize to exactly 1600 x 900 (mockup) or 640 x 360 (thumbnail) |
| RL016 | Make the file smaller: mockup 1,000,000 bytes, thumbnail 200,000 bytes |
| RL017 | Add `utilization.read` to `requested` |
| RL018 | Declare the utilization service with `"required": true` |

## 7. Move a 0.2 page to 0.4

Change `$schema`, `standardVersion`, `profile` and `hostApi`; move the
`com.ratehighway.rlab.preview` extension contents to the top-level `preview`
field; in `page.js`, accept host API `0.4.x` in `rlab.host.init` instead of
`0.2.x`. Give the page a new version. Keep the 0.2 version if hosts still use it.

## 8. What needs a person

Approval of the page, the service grant and its change level (set by an
administrator), and the decision that a particular viewer may change data on a
site all belong to people and the host. A checker pass grants none of them.
