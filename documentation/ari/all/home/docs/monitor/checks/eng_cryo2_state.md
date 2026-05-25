---
card_label: 'ENG: Cryo2 State'
card_icon: fa-solid fa-gear
---

# raw: ENG: Cryo2 State

## Overview

This engineering sub-test checks cryocooler 2 status for alarm state.

## Requirements

- [BLANK](checks/blank.md)
- [HAS_OBSDIR](checks/has_obsdir.md)
- [CALIB_TEST](checks/calib_test.md)

## What to do

If FALSE please [re-run the check](how_to/run_check.md) with
--test=ENG_TEST.

If fewer than 3 events are reported, monitor and continue.

If persistent, report the ENG_TEST details and contact
[Contact list C1](#contact-list-c1).

## Contact

### Contact list C1
<a id="contact-list-c1"></a>

| Name | Email |
| --- | --- |
| Lison Malo * | lison.malo@umontreal.ca |
| Gaspare Lo Curto | glocurto@eso.org |
| Philippe Vallee | philippe.vallee@umontreal.ca |
| Neil Cook | neil.cook@umontreal.ca |
| Etienne Artigau | etienne.artigau@umontreal.ca |

## Check logic

### generic

Performs the following test

```python
np.all(status_key == target)
```

#### Resolved values

| Key | Value |
| --- | --- |
| TEST_KEY | cryo2_status_state |
| ENABLED | True |
| STATUS_KEY | status_key |
| TARGET | target |

### aprofile_instrument/nirps_he_rali.yaml

Performs the following test

```python
np.all(HIERARCH ESO INS SENS127 == False)
```

#### Resolved values

| Key | Value |
| --- | --- |
| TEST_KEY | cryo2_status_state |
| ENABLED | True |
| STATUS_KEY | HIERARCH ESO INS SENS127 |
| TARGET | False |
