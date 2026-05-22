---
card_label: 'ENG: Enclosure Temperature RMS'
card_icon: fa-solid fa-gear
---

# raw: ENG: Enclosure Temperature RMS

## Overview

No overview available.

## Check logic

### generic

Performs the following test

```python
np.nanstd(sensor_key - reference_key) < limit
```

#### Resolved values

| Key | Value |
| --- | --- |
| TEST_KEY | enclosure_temperature_rms |
| ENABLED | True |
| SENSOR_KEY | sensor_key |
| REFERENCE_KEY | reference_key |
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
