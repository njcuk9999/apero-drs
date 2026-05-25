---
card_label: Raw Quality Check
card_icon: fa-solid fa-gear
---

# raw: Raw Quality Check

## Overview

Checks quality of configured raw file groups using percentile and
saturation limits.

## Requirements

- [BLANK](checks/blank.md)
- [HAS_OBSDIR](checks/has_obsdir.md)

## What to do

If FALSE please [re-run the check](how_to/run_check.md) with
--test=QUAL_TEST.

If HAS_OBSDIR or NO_SCI is FALSE, resolve those first.

If still FALSE after re-run, send the full quality report to
[Contact list C1](#contact-list-c1).

## Contact

### Contact list C1
<a id="contact-list-c1"></a>

| Name | Email |
| --- | --- |
| Etienne Artigau * | etienne.artigau@umontreal.ca |
| Neil Cook | neil.cook@umontreal.ca |
| Charles Cadieux | charles.cadieux.1@umontreal.ca |
| Lison Malo | lison.malo@umontreal.ca |

## Check logic

Checks quality of configured raw file groups using percentile and
saturation limits.
