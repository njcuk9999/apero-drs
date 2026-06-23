---
card_label: 'ENG: Enclosure Temperature RMS'
card_icon: fa-solid fa-gear
---

# raw: ENG: Enclosure Temperature RMS

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

### aprofile_instrument/nirps_ha_rali.yaml, aprofile_instrument/nirps_he_rali.yaml

Performs the following test

```python
np.nanstd(HIERARCH ESO INS TEMP185 VAL - HIERARCH ESO INS TEMP187 VAL) < 0.1
```

#### Resolved values

| Key | Value |
| --- | --- |
| TEST_KEY | enclosure_temperature_rms |
| ENABLED | True |
| SENSOR_KEY | HIERARCH ESO INS TEMP185 VAL |
| REFERENCE_KEY | HIERARCH ESO INS TEMP187 VAL |
| LIMIT | 0.1 |
| METRIC | metric |
