---
card_label: Critical Science Check
card_icon: fa-solid fa-gear
---

# raw: Critical Science Check

## Overview

Checks science-critical status flags for this observation night using the
critical-check CSV file (PATH.CRITICAL_CHECK / critical csv file).  Each flag
listed in the description CSV that has type "sci" must be True for this check
to pass.

If PATH.CRITICAL_CHECK is not configured, the check passes automatically.

## Requirements

- [BLANK](checks/blank.md)
- [HAS_OBSDIR](checks/has_obsdir.md)

## What to do

If FALSE please [re-run the check](how_to/run_check.md) with
--test=CRITICAL_SCI_TEST.

Review the critical check CSV for the failing night and identify which
science flag is False.  Contact the appropriate support team.

If still FALSE after investigation, please contact [Contact list C1](#contact-list-c1).

## Contact

### Contact list C1
<a id="contact-list-c1"></a>

| Name | Email |
| --- | --- |
| Neil Cook * | neil.cook@umontreal.ca |
| Lison Malo | lison.malo@umontreal.ca |
| Etienne Artigau | etienne.artigau@umontreal.ca |

## Check logic

Checks science-critical status flags for this observation night using the
critical-check CSV file (PATH.CRITICAL_CHECK / critical csv file).  Each flag
listed in the description CSV that has type "sci" must be True for this check
to pass.

If PATH.CRITICAL_CHECK is not configured, the check passes automatically.
