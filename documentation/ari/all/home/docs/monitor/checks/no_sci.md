---
card_label: Science Presence Check
card_icon: fa-solid fa-gear
---

# raw: Science Presence Check

## Overview

Check whether any science observations are present for the observation
night.

## Requirements

- [BLANK](checks/blank.md)
- [HAS_OBSDIR](checks/has_obsdir.md)

## What to do

If FALSE please [re-run the check](how_to/run_check.md) with
--test=NO_SCI.

If still FALSE, verify whether science data should exist and then check
[ESO archives](how_to/eso_archives.md).

If there is a good reason for no science data, override the check.

If there is science data on ESO archives but not locally, contact
[Contact list C1](#contact-list-c1).

If there is no science data on ESO archives and no clear reason, contact
[Contact list C2](#contact-list-c2).

## Contact

### Contact list C1
<a id="contact-list-c1"></a>

| Name | Email |
| --- | --- |
| Thomas Vandal * | thomas.vandal@umontreal.ca |
| Lison Malo | lison.malo@umontreal.ca |
| Neil Cook | neil.cook@umontreal.ca |

### Contact list C2
<a id="contact-list-c2"></a>

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

Check whether any science observations are present for the observation
night.
