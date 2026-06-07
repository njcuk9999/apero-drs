---
card_label: Low SNR in Science Spectra
card_icon: fa-solid fa-gear
---

# red: Low SNR in Science Spectra

## Overview

Checks whether any science files have SNR < 10 in extracted order 15 and 60
(header keys EXTSN015 and EXTSN060).

## Requirements

- [BLANK](checks/blank.md)
- [HAS_OBSDIR](checks/has_obsdir.md)
- [MANUAL_START](checks/manual_start.md)
- [APERO_START](checks/apero_start.md)
- [APERO_END](checks/apero_end.md)

## What to do

If FALSE please [re-run the check](how_to/run_check.md) with --test=LOW_SNR.

If still FALSE check ARI for previous observations of this object.

First check the APERO object flags spreadsheet. If the object is in this list
with CHECK=LOW_SNR then you can override the value with the APERO check
override code with --test=LOW_SNR.

If the previous observations are always below or around 10, you should bring
this up at the next meeting but override the value and note the object name.

If the weather was terrible or another issue was mentioned in the log that
could explain the low SNR you should bring this up at the next meeting but
override the value, state the object name and the weather-related reason.
Please then reject this file so it is not used in future reductions.

If the previous observations are usually well above 10 and the weather was
not terrible, please report to [Contact list C1](#contact-list-c1) stating that the SNR was flagged
as being well below average (give the object name and the SNR usually found
and the SNR for this observation). Please then reject this file.

## Contact

### Contact list C1
<a id="contact-list-c1"></a>

| Name | Email |
| --- | --- |
| The current observer * | See observer guide: sec:how_to:find_observer |
| 3.6m Telescope | 3P6@eso.org |
| La Silla Day and Night Staff | ls-dnos@eso.org |
| Neil Cook | neil.cook@umontreal.ca |
| Lison Malo | lison.malo@umontreal.ca |
| Frederique Baron | frederique.baron@umontreal.ca |
| Etienne Artigau | etienne.artigau@umontreal.ca |
| Lucile Mignon | lucile.mignon@univ-grenoble-alpes.fr |
| Romain Allart | romain.allart@umontreal.ca |

## Check logic

Checks whether any science files have SNR < 10 in extracted order 15 and 60
(header keys EXTSN015 and EXTSN060).
