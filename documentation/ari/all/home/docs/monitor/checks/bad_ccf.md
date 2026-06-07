---
card_label: Outlier CCF Files
card_icon: fa-solid fa-gear
---

# red: Outlier CCF Files

## Overview

Detects outlier CCF (Cross-Correlation Function) files in science targets.

For each science object observed in this obsdir, the check queries the APERO
FileIndex database for CCF_RV files, reads the RV_OBJ and CCFMFWHM header
values, and flags files that are more than a configurable number of sigma
away from the nightly median using a robust (MAD-based) distance metric.

## Requirements

- [BLANK](checks/blank.md)
- [HAS_OBSDIR](checks/has_obsdir.md)
- [MANUAL_START](checks/manual_start.md)
- [APERO_START](checks/apero_start.md)
- [APERO_END](checks/apero_end.md)

## What to do

If FALSE please [re-run the check](how_to/run_check.md) with --test=BAD_CCF.

If still FALSE, inspect the flagged CCF files in the reduced directory and
compare the RV and FWHM against previous nights for the same target.

If the outlier is caused by bad weather or instrument issues please reject
the affected file and override the check.

Please contact [Contact list C1](#contact-list-c1) if you are unsure how to proceed.

## Contact

### Contact list C1
<a id="contact-list-c1"></a>

| Name | Email |
| --- | --- |
| Neil Cook * | neil.cook@umontreal.ca |
| Etienne Artigau | etienne.artigau@umontreal.ca |
| Lison Malo | lison.malo@umontreal.ca |

## Check logic

Detects outlier CCF (Cross-Correlation Function) files in science targets.

For each science object observed in this obsdir, the check queries the APERO
FileIndex database for CCF_RV files, reads the RV_OBJ and CCFMFWHM header
values, and flags files that are more than a configurable number of sigma
away from the nightly median using a robust (MAD-based) distance metric.
