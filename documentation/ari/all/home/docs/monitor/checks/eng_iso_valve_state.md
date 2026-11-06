---
card_label: 'ENG: Isolation Valve State'
card_icon: fa-solid fa-gear
---

# raw: ENG: Isolation Valve State

## Overview

This engineering sub-test checks the isolation valve state is nominal.

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
| Etienne Artigau * | etienne.artigau@umontreal.ca |
| Lison Malo | lison.malo@umontreal.ca |
| Neil Cook | neil.cook@umontreal.ca |

## Check logic

### generic

Performs the following test

```python
np.all(status_key == target)
```

#### Resolved values

| Key | Value |
| --- | --- |
| TEST_KEY | isolation_valve_state |
| ENABLED | True |
| STATUS_KEY | status_key |
| TARGET | target |

### aprofile_instrument/nirps_ha_rali.yaml, aprofile_instrument/nirps_he_rali.yaml

Performs the following test

```python
np.all(HIERARCH ESO INS SENS100 STAT == False)
```

#### Resolved values

| Key | Value |
| --- | --- |
| TEST_KEY | isolation_valve_state |
| ENABLED | True |
| STATUS_KEY | HIERARCH ESO INS SENS100 STAT |
| TARGET | False |
