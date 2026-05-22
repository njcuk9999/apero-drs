---
card_label: 'ENG: Enclosure Setpoint Offset'
card_icon: fa-solid fa-gear
---

# raw: ENG: Enclosure Setpoint Offset

## Overview

No overview available.

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

## Requirements

- [BLANK](checks/blank.md)
- [HAS_OBSDIR](checks/has_obsdir.md)
- [CALIB_TEST](checks/calib_test.md)

## What to do

No instructions provided.

## Contact

No contacts.
