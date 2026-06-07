---
card_label: Previous Reduction Check
card_icon: fa-solid fa-gear
---

# red: Previous Reduction Check

## Overview

Checks whether there are any raw files without any reduced products.

Every raw file must have a corresponding preprocessed (pp) file for the
previous 7 days.  Every subsequent day (up to 7 days after the failure) will
also fail until the missing file is processed.

## Requirements

- [BLANK](checks/blank.md)
- [HAS_OBSDIR](checks/has_obsdir.md)
- [MANUAL_START](checks/manual_start.md)
- [APERO_START](checks/apero_start.md)
- [APERO_END](checks/apero_end.md)

## What to do

If FALSE please [re-run the check](how_to/run_check.md) with
--test=PREV_REDUC.

If still FALSE you should get a list of files that are missing.

Please try re-running the manual trigger on this specific observation
directory.

If still FALSE after re-running the manual trigger please check the DPR TYPE
of the files that are missing (e.g. dfits {filename} | fitsort dpr.type).

Please locate the preprocessing log for these files (under the APERO
msg/processing/ directory, search for the file identifier in the relevant
apero_preprocess log files).

After re-running the manual trigger and locating the log files, please email
[Contact list C1](#contact-list-c1) with the list of missing files and the relevant log content.

## Contact

### Contact list C1
<a id="contact-list-c1"></a>

| Name | Email |
| --- | --- |
| Neil Cook * | neil.cook@umontreal.ca |
| Etienne Artigau | etienne.artigau@umontreal.ca |
| Lison Malo | lison.malo@umontreal.ca |

## Check logic

Checks whether there are any raw files without any reduced products.

Every raw file must have a corresponding preprocessed (pp) file for the
previous 7 days.  Every subsequent day (up to 7 days after the failure) will
also fail until the missing file is processed.
