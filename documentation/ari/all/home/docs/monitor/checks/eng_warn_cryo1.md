---
card_label: 'ENG: Warning Cryo1 State'
card_icon: fa-solid fa-gear
---

# raw: ENG: Warning Cryo1 State

## Overview

This engineering sub-test checks cryocooler 1 warning flag activity.

## Requirements

- [BLANK](checks/blank.md)
- [HAS_OBSDIR](checks/has_obsdir.md)
- [CALIB_TEST](checks/calib_test.md)

## What to do

If FALSE please [re-run the check](how_to/run_check.md) with
--test=ENG_TEST.

If still FALSE, report the failing ENG_TEST details and contact
[Contact list C1](#contact-list-c1).

## Contact

### Contact list C1
<a id="contact-list-c1"></a>

| Name | Email |
| --- | --- |
| Lison Malo * | lison.malo@umontreal.ca |
| Philippe Vallee | philippe.vallee@umontreal.ca |
| Neil Cook | neil.cook@umontreal.ca |
| Etienne Artigau | etienne.artigau@umontreal.ca |

## Check logic

### generic

Performs the following test

```python
np.all(np.char.strip(status_key) == 'target')
```

#### Resolved values

| Key | Value |
| --- | --- |
| TEST_KEY | warning_cryo1_state |
| ENABLED | True |
| STATUS_KEY | status_key |
| TARGET | target |

### aprofile_instrument/nirps_he_rali.yaml

Performs the following test

```python
np.all(np.char.strip(HIERARCH ESO INS SENS144 STAT) == '')
```

#### Resolved values

| Key | Value |
| --- | --- |
| TEST_KEY | warning_cryo1_state |
| ENABLED | True |
| STATUS_KEY | HIERARCH ESO INS SENS144 STAT |
| TARGET | None |
