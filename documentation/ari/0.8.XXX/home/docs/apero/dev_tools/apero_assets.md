---
card_label: apero_assets
card_icon: fa-solid fa-code
---

# apero_assets

Checks, updates, and synchronizes APERO data-asset checksums.

After an assets archive is extracted, `version.txt` in the local
`apero-assets` directory records its filename without `_assets.tar.gz`.
An assets reset copies this file to the profile's `PATH.ASSETS` directory.
For example, `1794397857_110257_assets.tar.gz` produces
`1794397857_110257`. This is an archive identifier, not a content checksum;
it does not track subsequent manual changes to the extracted assets.

If the local marker is missing, the next assets reset extracts the archive
selected by the installed checksum manifest, downloading it if necessary.
This establishes provenance for the new reset, not earlier resets.

**Source:** `apero-drs/apero/tools/recipes/dev/apero_assets.py`

This script is catalogued from its source file because it does not have a `DrsRecipe` entry. Add recipe metadata when it needs generated usage, argument, or output tables.
