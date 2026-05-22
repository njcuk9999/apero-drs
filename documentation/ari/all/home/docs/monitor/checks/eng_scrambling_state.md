---
card_label: 'ENG: Scrambling Status Science'
card_icon: fa-solid fa-gear
---

# raw: ENG: Scrambling Status Science

## Overview

No overview available.

## Check logic

### generic

Performs the following test

```python
np.all(status_key == target) on dprtypes ['dprtypes']
```

#### Resolved values

| Key | Value |
| --- | --- |
| TEST_KEY | scrambling_status_science |
| ENABLED | True |
| STATUS_KEY | status_key |
| TARGET | target |
| DPRTYPES | dprtypes |

## Requirements

- [BLANK](checks/blank.md)
- [HAS_OBSDIR](checks/has_obsdir.md)
- [CALIB_TEST](checks/calib_test.md)

## What to do

No instructions provided.

## Contact

No contacts.
