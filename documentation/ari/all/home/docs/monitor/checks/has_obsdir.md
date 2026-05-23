---
card_label: Observation Directory Check
card_icon: fa-solid fa-gear
---

# raw: Observation Directory Check

## Overview

This test checks whether an observation night directory exists in the 
raw directory.

## Requirements

- [BLANK](checks/blank.md)

## What to do

If FALSE please [re-run the check](how_to/run_check.md) with --test=HAS_OBSDIR.

If still FALSE then the directory for that day/night has not been 
created on our machine.

Please check [here for when you should expect files on 
our machines])[how_to/obs_timeline.md].

Then you need to [check the ESO archives for data](how_to/eso_archives.md).

### If there is no data on the ESO archive for that night

This means that either:
- No data was taken
- No data was transferred from La Silla to the ESO Archive

If there is no data on the ESO archive either no data was taken or no data was 
transferred from La Silla to the ESO archive.

Check the observation log if there is a good reason for no data you can report 
this FALSE and ignore it - you can always email [Contact list C1](#contact-list-c1) to ask if the
reason is good enough to ignore there being no data.

If you are ignoring the data please update the monitoring comment on ARI 
monitoring.

If there was no good reason please contact [Contact list C2](#contact-list-c2) the following
people stating there was no data on the ESO archive.

Note that even if confirmed that there is expected to be no data please still 
run the manual trigger. In the APERO processing step you will be prompted to 
continue you can say “No” (this will just skip the processing step) but all 
the other manual trigger steps should still run.


### If there is data on the ESO archive

This means that we have a problem downloading the data from the ESO archive.

Please contact the [Contact list C3](#contact-list-c3) stating that there was no data on our 
machines but was data on the ESO archive.

## Contact

### Contact list C1
<a id="contact-list-c1"></a>

| Name | Email |
| --- | --- |
| Neil Cook * | neil.cook@umontreal.ca |
| Lison Malo | lison.malo@umontreal.ca |
| Frederique Baron | frederique.baron@umontreal.ca |
| Etienne Artigau | etienne.artigau@umontreal.ca |

### Contact list C2
<a id="contact-list-c2"></a>

| Name | Email |
| --- | --- |
| ESO CL Service Desk * | cl-servicedesk@eso.org |
| The current observer | See observer guide: sec:how_to:find_observer |
| 3.6m Telescope | 3P6@eso.org |
| La Silla Day and Night Staff | ls-dnos@eso.org |
| Gaspare Lo Curto | glocurto@eso.org |
| Neil Cook | neil.cook@umontreal.ca |
| Lison Malo | lison.malo@umontreal.ca |
| Frederique Baron | frederique.baron@umontreal.ca |
| Etienne Artigau | etienne.artigau@umontreal.ca |
| Xavier Dumusque | xavier.dumusque@unige.ch |

### Contact list C3
<a id="contact-list-c3"></a>

| Name | Email |
| --- | --- |
| Thomas Vandal * | thomas.vandal@umontreal.ca |
| Lison Malo | lison.malo@umontreal.ca |
| Neil Cook | neil.cook@umontreal.ca |

## Check logic

This test checks whether an observation night directory exists in the 
raw directory.
