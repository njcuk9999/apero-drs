---
card_label: 'ENG: Enclosure Heater Power Max'
card_icon: fa-solid fa-gear
---

# raw: ENG: Enclosure Heater Power Max

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
np.nanmax(metric_key) < limit
```

#### Resolved values

| Key | Value |
| --- | --- |
| TEST_KEY | enclosure_heater_power_max |
| ENABLED | True |
| METRIC_KEY | metric_key |
| LIMIT | limit |
| METRIC | metric |

### aprofile_instrument/nirps_he_rali.yaml

Performs the following test

```python
np.nanmax(HIERARCH ESO INS SENS121 VAL) < 90.0
```

#### Resolved values

| Key | Value |
| --- | --- |
| TEST_KEY | enclosure_heater_power_max |
| ENABLED | True |
| METRIC_KEY | HIERARCH ESO INS SENS121 VAL |
| LIMIT | 90.0 |
| METRIC | metric |
