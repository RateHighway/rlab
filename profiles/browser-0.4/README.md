# Browser Page Profile 0.4

**Draft Standard 0.4, in development:** `RLAB-PAGE-0.4`, standard version
`0.4`, host API `0.4.0`. No host supports it yet.

0.4 is the 0.2 browser page with two additions:

1. **Required preview images.** A top-level `preview` field declares a mockup
   (1600 x 900) and a thumbnail (640 x 360) captured from the real page.
2. **`utilization.manage`.** A page may ask the host's utilization service to
   create, update and delete Utilization 4 location groups and car groups, and
   to undo a change. Nothing else is writable.

`RLAB-PAGE-READONLY-0.2` is unchanged and stays supported. Use 0.2 for pages
that only read; use 0.4 for pages that save group changes.

## Read in this order

1. [Standard: what changed from 0.2 and the write rules](docs/RLAB-PAGE-STANDARD.md)
2. [Create and check a 0.4 page](docs/DEVELOPER-GUIDE.md)
3. [Host 0.4 pages beside 0.2 pages](docs/HOST-INTEGRATION-GUIDE.md)

The profile includes closed manifest and host schemas, the synthetic Car Group
Manager example with real captured preview images, an offline packer and
checker, and tests.

## Run the tools

Python 3, no third-party packages. From this directory:

```sh
python -B tools/rlab.py pack examples/group-manager build/group-manager-0.1.0.rlab
python -B tools/rlab.py validate build/group-manager-0.1.0.rlab --host examples/host-capabilities.json
python -B -m unittest discover -s tests -v
```

Exit 0 means only that the offline checks passed. The checker reads the
preview images' headers for type and pixel size; it does not judge what they
show. It does not test a browser runtime, the host's write handling,
permissions or certification. The host fixture uses reserved example domains
and is not a live service.
