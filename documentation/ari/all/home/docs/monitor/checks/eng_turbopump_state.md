---
card_label: 'ENG: Turbopump State'
card_icon: fa-solid fa-gear
---

# raw: ENG: Turbopump State

## Overview

No overview available.

## Requirements

- [BLANK](checks/blank.md)
- [HAS_OBSDIR](checks/has_obsdir.md)
- [CALIB_TEST](checks/calib_test.md)

## What to do

No instructions provided.

## Contact

No contacts.

## Check logic

### generic

Performs the following test

```python
np.all(status_key == target)
```

#### Resolved values

| Key | Value |
| --- | --- |
| TEST_KEY | turbopump_status_state |
| ENABLED | True |
| STATUS_KEY | status_key |
| TARGET | target |

### aprofile_instrument/nirps_ha_rali.yaml, aprofile_instrument/nirps_he_rali.yaml

Performs the following test

```python
np.all(HIERARCH ESO INS SENS102 STAT == False)
```

#### Resolved values

| Key | Value |
| --- | --- |
| TEST_KEY | turbopump_status_state |
| ENABLED | True |
| STATUS_KEY | HIERARCH ESO INS SENS102 STAT |
| TARGET | False |
