---
card_label: 'ENG: Backend Device Error State'
card_icon: fa-solid fa-gear
---

# raw: ENG: Backend Device Error State

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
np.all(np.char.upper(np.char.strip(status_key)) != np.char.upper('blocked_value'))
```

#### Resolved values

| Key | Value |
| --- | --- |
| TEST_KEY | backend_device_error_state |
| ENABLED | True |
| STATUS_KEY | status_key |
| BLOCKED_VALUE | blocked_value |

### aprofile_instrument/nirps_ha_rali.yaml, aprofile_instrument/nirps_he_rali.yaml

Performs the following test

```python
np.all(np.char.upper(np.char.strip(HIERARCH ESO INS SENS129 STAT)) != np.char.upper('NOK'))
```

#### Resolved values

| Key | Value |
| --- | --- |
| TEST_KEY | backend_device_error_state |
| ENABLED | True |
| STATUS_KEY | HIERARCH ESO INS SENS129 STAT |
| BLOCKED_VALUE | NOK |
