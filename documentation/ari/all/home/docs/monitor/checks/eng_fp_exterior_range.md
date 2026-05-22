---
card_label: 'ENG: FP Exterior Range'
card_icon: fa-solid fa-gear
---

# raw: ENG: FP Exterior Range

## Overview

No overview available.

## Check logic

### generic

Performs the following test

```python
np.nanmin(metric_key) > lower_limit and np.nanmax(metric_key) < upper_limit
```

#### Resolved values

| Key | Value |
| --- | --- |
| TEST_KEY | fp_exterior_range |
| ENABLED | True |
| METRIC_KEY | metric_key |
| LOWER_LIMIT | lower_limit |
| UPPER_LIMIT | upper_limit |
| XMIN | xmin |
| XMAX | xmax |

## Requirements

- [BLANK](checks/blank.md)
- [HAS_OBSDIR](checks/has_obsdir.md)
- [CALIB_TEST](checks/calib_test.md)

## What to do

No instructions provided.

## Contact

No contacts.
