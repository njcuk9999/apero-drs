---
card_label: Detector Pixel Shifts
card_icon: fa-solid fa-gear
---

# red: Detector Pixel Shifts

## Overview

Checks for detector pixel shifts in the preprocessed (pp) files.

Specifically checks the DETOFFDX and DETOFFDY header keys for any non-zero
values.

## Requirements

- [BLANK](checks/blank.md)
- [HAS_OBSDIR](checks/has_obsdir.md)
- [MANUAL_START](checks/manual_start.md)
- [APERO_START](checks/apero_start.md)
- [APERO_END](checks/apero_end.md)

## What to do

If FALSE please [re-run the check](how_to/run_check.md) with
--test=PIXEL_SHIFTS.

If still FALSE please email [Contact list C1](#contact-list-c1).

## Contact

### Contact list C1
<a id="contact-list-c1"></a>

| Name | Email |
| --- | --- |
| Etienne Artigau * | etienne.artigau@umontreal.ca |
| Neil Cook | neil.cook@umontreal.ca |
| Lison Malo | lison.malo@umontreal.ca |

## Check logic

Checks for detector pixel shifts in the preprocessed (pp) files.

Specifically checks the DETOFFDX and DETOFFDY header keys for any non-zero
values.
