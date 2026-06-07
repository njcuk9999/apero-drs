---
card_label: Manual Trigger Finished
card_icon: fa-solid fa-gear
---

# red: Manual Trigger Finished

## Overview

If FALSE this normally means the manual trigger crashed before finishing
completely.

## Requirements

- [BLANK](checks/blank.md)
- [HAS_OBSDIR](checks/has_obsdir.md)
- [MANUAL_START](checks/manual_start.md)

## What to do

If FALSE please [re-run the check](how_to/run_check.md) with
--test=MANUAL_END.

Please try re-running the manual trigger and look for errors in the running
code.

If still FALSE and all requirements above are satisfied, please contact
[Contact list C1](#contact-list-c1) stating that you have re-run the manual trigger and the
MANUAL_END reduced check is still failing.

## Contact

### Contact list C1
<a id="contact-list-c1"></a>

| Name | Email |
| --- | --- |
| Neil Cook * | neil.cook@umontreal.ca |
| Lison Malo | lison.malo@umontreal.ca |
| Etienne Artigau | etienne.artigau@umontreal.ca |

## Check logic

If FALSE this normally means the manual trigger crashed before finishing
completely.
