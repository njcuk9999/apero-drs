---
card_label: 'ENG: FP Interior RMS'
card_icon: fa-solid fa-gear
---

# raw: ENG: FP Interior RMS

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
np.nanstd(metric_key) < limit
```

#### Resolved values

| Key | Value |
| --- | --- |
| TEST_KEY | fp_interior_rms |
| ENABLED | True |
| METRIC_KEY | metric_key |
| LIMIT | limit |
| METRIC | metric |

### aprofile_instrument/nirps_he_rali.yaml

Performs the following test

```python
np.nanstd(HIERARCH ESO INS TEMP14 VAL) < 0.01
```

#### Resolved values

| Key | Value |
| --- | --- |
| TEST_KEY | fp_interior_rms |
| ENABLED | True |
| METRIC_KEY | HIERARCH ESO INS TEMP14 VAL |
| LIMIT | 0.01 |
| METRIC | metric |
