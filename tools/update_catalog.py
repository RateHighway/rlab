"""Refresh generated catalog metadata after an intentional profile source edit."""
from repository import ROOT, make_catalog, write_json


if __name__ == '__main__':
    write_json(ROOT / 'catalog.json', make_catalog())
    print('Updated catalog.json from the current profile source files.')
