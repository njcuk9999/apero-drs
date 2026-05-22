---
card_label: 'ENG: Cryo2 State'
card_icon: fa-solid fa-gear
---

# raw: ENG: Cryo2 State

## Overview

No overview available.

## Check logic

### generic

Performs the following test

```python
np.all(status_key == target)
```

#### Resolved values

| Key | Value |
| --- | --- |
| TEST_KEY | cryo2_status_state |
| ENABLED | True |
| STATUS_KEY | status_key |
| TARGET | target |

## Requirements

- [BLANK](checks/blank.md)
- [HAS_OBSDIR](checks/has_obsdir.md)
- [CALIB_TEST](checks/calib_test.md)

## What to do

No instructions provided.

## Contact

No contacts.
