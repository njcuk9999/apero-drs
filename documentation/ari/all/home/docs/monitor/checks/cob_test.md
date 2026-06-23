---
card_label: Calibration OB Name Check
card_icon: fa-solid fa-gear
---

# raw: Calibration OB Name Check

## Overview

This check verifies that required calibration OB names appear in the
configured MJD spans. It scans all raw-file headers, enables each rule
only inside its configured MJD range, and then checks that matching OB
names occur at least once while the rule is active.

## Requirements

- [BLANK](checks/blank.md)
- [HAS_OBSDIR](checks/has_obsdir.md)

## What to do

If FALSE please [re-run the check](how_to/run_check.md) with
--test=COB_TEST.

If HAS_OBSDIR or CALIB_TEST is FALSE, resolve these first.

If still FALSE, verify whether missing calibration OBs are expected
timing-wise ([observation timeline](how_to/obs_timeline.md)) and compare
local files with [ESO archives](how_to/eso_archives.md).

If the calibration OBs are abnormally late or missing, contact
[Contact list C1](#contact-list-c1) and include which OB name is missing.

## Contact

### Contact list C1
<a id="contact-list-c1"></a>

| Name | Email |
| --- | --- |
| The current observer * | See observer guide: sec:how_to:find_observer |
| La Silla Day and Night Staff | ls-dnos@eso.org |
| Lison Malo | lison.malo@umontreal.ca |
| Etienne Artigau | etienne.artigau@umontreal.ca |
| Neil Cook | neil.cook@umontreal.ca |
| Frederique Baron | frederique.baron@umontreal.ca |
| Gaspare Lo Curto | glocurto@eso.org |

## Check logic

This check verifies that required calibration OB names appear in the
configured MJD spans. It scans all raw-file headers, enables each rule
only inside its configured MJD range, and then checks that matching OB
names occur at least once while the rule is active.
