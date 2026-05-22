---
card_label: 'ENG: Isolation Valve State'
card_icon: fa-solid fa-gear
---

# raw: ENG: Isolation Valve State

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
| TEST_KEY | isolation_valve_state |
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
