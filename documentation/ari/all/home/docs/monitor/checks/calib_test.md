---
card_label: Calibration Presence Check
card_icon: fa-solid fa-gear
---

# raw: Calibration Presence Check

## Overview

This test checks for at least one file from each required calibration
DPR type in the observation directory.

## Requirements

- [BLANK](checks/blank.md)
- [HAS_OBSDIR](checks/has_obsdir.md)

## What to do

If FALSE please [re-run the check](how_to/run_check.md) with
--test=CALIB_TEST.

If HAS_OBSDIR is FALSE, resolve that first.

Then [check the ESO archives](how_to/eso_archives.md) and compare archive
files with the local observation directory.

If calibrations are missing on the archive with a good reason, contact
[Contact list C1](#contact-list-c1) and ask whether additional calibrations should be rejected.

If calibrations are missing on the archive with no good reason, contact
[Contact list C2](#contact-list-c2).

If calibrations exist on the archive but not on local disks, contact
[Contact list C3](#contact-list-c3).

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

### Contact list C2
<a id="contact-list-c2"></a>

| Name | Email |
| --- | --- |
| The current observer * | See observer guide: sec:how_to:find_observer |
| 3.6m Telescope | 3P6@eso.org |
| La Silla Day and Night Staff | ls-dnos@eso.org |
| Lison Malo | lison.malo@umontreal.ca |
| Etienne Artigau | etienne.artigau@umontreal.ca |
| Neil Cook | neil.cook@umontreal.ca |
| Gaspare Lo Curto | glocurto@eso.org |
| Xavier Dumusque | xavier.dumusque@unige.ch |

### Contact list C3
<a id="contact-list-c3"></a>

| Name | Email |
| --- | --- |
| Thomas Vandal * | thomas.vandal@umontreal.ca |
| Lison Malo | lison.malo@umontreal.ca |
| Neil Cook | neil.cook@umontreal.ca |
| Etienne Artigau | etienne.artigau@umontreal.ca |

## Check logic

This test checks for at least one file from each required calibration
DPR type in the observation directory.
