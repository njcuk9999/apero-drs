---
card_label: 'ENG: Vacuum Gauge Upper'
card_icon: fa-solid fa-gear
---

# raw: ENG: Vacuum Gauge Upper

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
| TEST_KEY | vacuum_gauge_upper |
| ENABLED | True |
| METRIC_KEY | metric_key |
| LIMIT | limit |
| METRIC | metric |

### aprofile_instrument/nirps_he_rali.yaml

Performs the following test

```python
np.nanmax(HIERARCH ESO INS PRES104 VAL) < 0.0001
```

#### Resolved values

| Key | Value |
| --- | --- |
| TEST_KEY | vacuum_gauge_upper |
| ENABLED | True |
| METRIC_KEY | HIERARCH ESO INS PRES104 VAL |
| LIMIT | 0.0001 |
| METRIC | metric |
