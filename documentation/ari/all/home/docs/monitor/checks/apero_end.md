---
card_label: APERO Processing Finished
card_icon: fa-solid fa-gear
---

# red: APERO Processing Finished

## Overview

If FALSE this normally means the manual trigger has crashed before APERO
processing finished.

## Requirements

- [BLANK](checks/blank.md)
- [HAS_OBSDIR](checks/has_obsdir.md)
- [MANUAL_START](checks/manual_start.md)
- [APERO_START](checks/apero_start.md)

## What to do

If FALSE please [re-run the check](how_to/run_check.md) with
--test=APERO_END.

If still FALSE please try re-running the manual trigger with
--only_apero_process=True and look for errors in the running code.

Please then locate the log file for apero_processing.py and email
[Contact list C1](#contact-list-c1) with a copy of the log (and/or the location of the log file on
disk).

## Contact

### Contact list C1
<a id="contact-list-c1"></a>

| Name | Email |
| --- | --- |
| Neil Cook * | neil.cook@umontreal.ca |
| Lison Malo | lison.malo@umontreal.ca |
| Etienne Artigau | etienne.artigau@umontreal.ca |

## Check logic

If FALSE this normally means the manual trigger has crashed before APERO
processing finished.
