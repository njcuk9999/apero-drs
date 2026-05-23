---
card_label: 'ENG: FP Setpoint RMS'
card_icon: fa-solid fa-gear
---

# raw: ENG: FP Setpoint RMS

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
np.nanstd(sensor_key - setpoint_key) < limit
```

#### Resolved values

| Key | Value |
| --- | --- |
| TEST_KEY | fp_setpoint_rms |
| ENABLED | True |
| SENSOR_KEY | sensor_key |
| SETPOINT_KEY | setpoint_key |
| LIMIT | limit |
| METRIC | metric |

### aprofile_instrument/nirps_he_rali.yaml

Performs the following test

```python
np.nanstd(HIERARCH ESO INS TEMP14 VAL - HIERARCH ESO INS TEMP188 VAL) < 0.005
```

#### Resolved values

| Key | Value |
| --- | --- |
| TEST_KEY | fp_setpoint_rms |
| ENABLED | True |
| SENSOR_KEY | HIERARCH ESO INS TEMP14 VAL |
| SETPOINT_KEY | HIERARCH ESO INS TEMP188 VAL |
| LIMIT | 0.005 |
| METRIC | metric |
