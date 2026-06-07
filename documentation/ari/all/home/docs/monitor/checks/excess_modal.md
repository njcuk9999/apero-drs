---
card_label: Excess Modal Noise
card_icon: fa-solid fa-gear
---

# red: Excess Modal Noise

## Overview

Tests for excess modal noise in telluric-standard stars.

For each tcorr file belonging to a vetted telluric star, it computes the
pixel-to-pixel RMS (photon noise proxy) and the RMS with a 20-pixel stride
(photon + modal noise proxy) on a sample H-band order.  The test passes when
the modal component (quadratic subtraction of the two) does not exceed a
mode-specific threshold.

This test is True by default when no vetted telluric stars were observed.

## Requirements

- [BLANK](checks/blank.md)
- [HAS_OBSDIR](checks/has_obsdir.md)
- [MANUAL_START](checks/manual_start.md)
- [APERO_START](checks/apero_start.md)
- [APERO_END](checks/apero_end.md)

## What to do

If FALSE please [re-run the check](how_to/run_check.md) with
--test=EXCESS_MODAL.

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

Tests for excess modal noise in telluric-standard stars.

For each tcorr file belonging to a vetted telluric star, it computes the
pixel-to-pixel RMS (photon noise proxy) and the RMS with a 20-pixel stride
(photon + modal noise proxy) on a sample H-band order.  The test passes when
the modal component (quadratic subtraction of the two) does not exceed a
mode-specific threshold.

This test is True by default when no vetted telluric stars were observed.
