# Car Group Manager (Sample)

Sample 0.1.0 for RevenueLab Draft Standard 0.4 (`RLAB-PAGE-0.4`, in
development). The publisher, support address, Location AAA and every group
name are invented. No host supports 0.4 yet.

**Purpose.** Show how a 0.4 page lists and changes the car groups of one
Utilization 4 location. A car group is a named set of car class codes (for
example `CCAR`) that Utilization 4 reports together. The page also lists the
location groups that contain Location AAA. In this sample only car groups can
be changed; location groups are shown, not edited.

**Inputs.** Fixed sample data in `app/assets/page.js`: four car groups and two
location groups. **Outputs.** The groups on screen and a list of the changes
made in this session.

**Opened directly** (double-click `app/index.html`): the page shows the sample
data and says so. You can add and delete groups on screen. Nothing is saved:
saving needs a host session with permission to change groups.

**In a 0.4 host session** the page shows the write pattern the standard
requires: it accepts the session only with `context.read`, `utilization.read`
and `utilization.manage` and a `com.ratehighway.utilization4.query` service
descriptor; it makes one idempotency key per intended change; it shows the
service's message and next step unchanged; it never retries a refusal on its
own; it keeps the access token in memory only. The group-change call itself
belongs to the host's service contract, not to the standard, so this sample
does not invent it. `sendGroupChange` answers every change with the refusal
`SAMPLE_NO_SERVICE_CALL`. Replace that one function with the call your host
publishes. For RevenueLab.build that contract is the Utilization 4 service
contract; its write routes are being added and are not live.

**Manifest.** Requests and requires `context.read`, `utilization.read` and
`utilization.manage`; requires the service `com.ratehighway.utilization4.query`
from version 1.0.0 up to (not including) 2.0.0; no extra network destinations;
no retention; no personal data. The `preview` field declares the two images
below.

**Preview images.** `app/assets/preview/mockup.png` (1600 x 900) and
`thumbnail.png` (640 x 360) were captured from this page opened directly in
headless Microsoft Edge at twice the size (3200 x 1800), then reduced to
1600 x 900. The thumbnail is a crop of the same capture showing the car group
table, reduced to 640 x 360. Capture new images when a version changes how the
page looks.

**Check it.** From `profiles/browser-0.4`:

```sh
python -B tools/rlab.py pack examples/group-manager build/group-manager-0.1.0.rlab
python -B tools/rlab.py validate build/group-manager-0.1.0.rlab --host examples/host-capabilities.json
```

**Limitations.** Fixed sample data; no service call; no undo button (undo is
offered by the host, which logs every change); no editing of location groups
or of an existing car group's classes. Browser, accessibility and host tests
must be run separately.

**Approval.** Changing real groups needs a host that supports 0.4, an
administrator who sets the change level on the service grant, and a viewer
the host allows to change data on that site. Passing the checker grants none
of these. Licence: Apache-2.0, in `LICENSE.txt`.
