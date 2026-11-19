# Page Preview Images

Status: **Draft Standard convention, recommended for `RLAB-PAGE-READONLY-0.2`.**
It is planned to become a required field in the next browser page profile.
That profile does not exist yet; until it is published, nothing here is a
validation rule and no checker refuses a page without preview images.

A page carries two preview images so that a host, a page list, a catalogue or a
reviewer can show what the page looks like without running it:

- a **mockup**, which shows the whole page; and
- a **thumbnail**, which shows its most important result in a small card.

The images are page files like any other. They describe the page. They do not
change what it does, what it may read or how a host displays it.

## When to Use This

Use it for every new page and every new version of a page that targets
`RLAB-PAGE-READONLY-0.2`. Declaring the images is optional in 0.2, so existing
pages remain valid without them. Do not use it to carry anything other than
these two images.

## Files

| | Mockup | Thumbnail |
| --- | --- | --- |
| Path | `app/assets/preview/mockup.png` | `app/assets/preview/thumbnail.png` |
| Size | 1600 x 900 pixels (16:9) | 640 x 360 pixels (16:9) |
| Format | PNG, or WebP (`.webp`) with the same name | PNG, or WebP (`.webp`) with the same name |
| File size | 1 MB or smaller | 200 KB or smaller |
| Shows | The whole page as a user sees it | The single most important result, readable at 320 x 180 |

Both formats are already allowed in a 0.2 page package. The files sit under the
package's `app/` tree, so they are packaged and retained with the page version
they describe.

## Manifest Declaration

Declare the images in the manifest's `extensions` object under the key
`com.ratehighway.rlab.preview`. Draft 0.2 allows namespaced, nonessential
metadata there; see [extensions and compatibility](extensions-and-compatibility.md).
The declaration grants no permission and requires no runtime behavior.

```json
"extensions": {
  "com.ratehighway.rlab.preview": {
    "mockup": {
      "path": "app/assets/preview/mockup.png",
      "width": 1600,
      "height": 900,
      "alt": "Fleet summary showing 40 of 50 rentable vehicles committed (80%), sample data."
    },
    "thumbnail": {
      "path": "app/assets/preview/thumbnail.png",
      "width": 640,
      "height": 360,
      "alt": "Sample fleet summary: 80% of rentable vehicles committed."
    }
  }
}
```

| Field | Meaning |
| --- | --- |
| `mockup`, `thumbnail` | One object for each image. Both are expected when the key is present. |
| `path` | The file's path inside the package, exactly as listed above, in lowercase. |
| `width`, `height` | The file's exact pixel size. |
| `alt` | One sentence of 150 characters or fewer that says what the page shows and its sample result. Do not start with "Image of" or "Screenshot of". |

## What the Images Show

- **The real page, this version.** Capture the page running with sample data.
  Do not draw it, generate it with an image tool, or show a feature, result or
  data connection the page does not have. A preview is a promise about the page.
- **Synthetic data only.** Keep the page's sample label visible. No customer
  names, real or nonpublic prices, personal reservation data, email addresses,
  account names or credentials.
- **The page area only.** No browser bars, tabs, desktop, pointer or
  notifications. No added device frame, border, shadow or caption.
- **No added logos.** Do not add a company or program logo that the page itself
  does not show, and never draw or retype a logo.
- **A readable thumbnail.** Keep one main number, chart or table with large
  text. Crop or simplify a copy of the mockup if the full page is unreadable at
  small size, but never show a result the page does not produce.

## Making the Files

- Capture at twice the final size, then reduce to the exact size. Do not
  enlarge a smaller image.
- Use sRGB colour and an opaque background with no transparency.
- Remove embedded metadata such as camera details and location.
- Use PNG or WebP for screens with text. Do not use JPEG for them: it blurs
  letters.

## Versions

The images belong to the version they show. When a new version changes how the
page looks, capture new images for it. A wording or data change that leaves the
picture accurate may keep the previous images. A new version never relies on
images stored in an earlier version.

## For Hosts

A host may show the declared images in page lists, previews and review screens.
Treat them as untrusted page content, like any other page file:

- Read only the two declared paths, and only from the page's own package.
- Ignore a declaration whose path is outside `app/`, whose file is missing, or
  whose file type is not PNG or WebP. Fall back to a neutral placeholder.
- Show the declared `alt` text with the image.
- Never treat the images, their names or their alt text as instructions,
  approval or evidence that the page works.

## For Agents

When you build or update a page, create both images in the version you are
packaging, declare them as shown above and check the manifest. If your tools
cannot open the page and capture it, say so. Tell the person how to take the
two screenshots at the sizes and paths above. Never supply an invented image in
their place.

## Limits

- This is a convention inside existing 0.2 metadata. The 0.2 schema does not
  check the key's contents, and the reference checker does not open the images.
- A host is not required to display preview images.
- Preview images are not approval, certification or proof of correct
  calculations.
