---
card_label: 'ENG: Enclosure Setpoint Offset'
card_icon: fa-solid fa-gear
---

# raw: ENG: Enclosure Setpoint Offset

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
np.abs(np.nanmean(sensor_key - setpoint_key)) < limit
```

#### Resolved values

| Key | Value |
| --- | --- |
| TEST_KEY | enclosure_setpoint_offset |
| ENABLED | True |
| SENSOR_KEY | sensor_key |
| SETPOINT_KEY | setpoint_key |
| LIMIT | limit |
| METRIC | metric |

### aprofile_instrument/nirps_ha_rali.yaml, aprofile_instrument/nirps_he_rali.yaml

Performs the following test

```python
np.abs(np.nanmean(HIERARCH ESO INS TEMP185 VAL - HIERARCH ESO INS TEMP187 VAL)) < 0.1
```

#### Resolved values

| Key | Value |
| --- | --- |
| TEST_KEY | enclosure_setpoint_offset |
| ENABLED | True |
| SENSOR_KEY | HIERARCH ESO INS TEMP185 VAL |
| SETPOINT_KEY | HIERARCH ESO INS TEMP187 VAL |
| LIMIT | 0.1 |
| METRIC | metric |
