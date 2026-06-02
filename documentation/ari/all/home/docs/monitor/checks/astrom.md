---
card_label: Astrometric Object Name Check
card_icon: fa-solid fa-gear
---

# raw: Astrometric Object Name Check

## Overview

This test checks that every raw FITS file whose header contains an object
name can be resolved in the APERO astrometric database (by exact name,
registered alias, or cleaned name variant).  Files that carry no object
name in any of the configured header keys are skipped.

## Requirements

- [BLANK](checks/blank.md)
- [HAS_OBSDIR](checks/has_obsdir.md)

## What to do

If FALSE please [re-run the check](how_to/run_check.md) with --test=ASTROM.

For each failing file, the object name listed in the report was not found
in the astrometric database.

Go to the ARI astrometrics resolve page, search for the name, and either:
  - Add a new entry for the target if it is genuinely absent.
  - Add the raw header name as an alias to an existing entry.

Contact [Contact list C1](#contact-list-c1) if you need help determining the correct target, or
[Contact list C2](#contact-list-c2) if you need help adding the entry to the database.

## Contact

### Contact list C1
<a id="contact-list-c1"></a>

| Name | Email |
| --- | --- |
| Neil Cook * | neil.cook@umontreal.ca |
| Etienne Artigau | etienne.artigau@umontreal.ca |
| Lison Malo | lison.malo@umontreal.ca |

### Contact list C2
<a id="contact-list-c2"></a>

| Name | Email |
| --- | --- |
| Neil Cook * | neil.cook@umontreal.ca |

## Check logic

This test checks that every raw FITS file whose header contains an object
name can be resolved in the APERO astrometric database (by exact name,
registered alias, or cleaned name variant).  Files that carry no object
name in any of the configured header keys are skipped.
