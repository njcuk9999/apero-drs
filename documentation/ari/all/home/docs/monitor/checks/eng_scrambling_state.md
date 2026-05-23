---
card_label: 'ENG: Scrambling Status Science'
card_icon: fa-solid fa-gear
---

# raw: ENG: Scrambling Status Science

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

### aprofile_instrument/nirps_he_rali.yaml

Performs the following test

```python
np.all(HIERARCH ESO INS2 AOS SCRAMB ST == True) on dprtypes ['OBJECT,FP', 'OBJECT,SKY', 'TELLURIC,SKY']
```

#### Resolved values

| Key | Value |
| --- | --- |
| TEST_KEY | scrambling_status_science |
| ENABLED | True |
| STATUS_KEY | HIERARCH ESO INS2 AOS SCRAMB ST |
| TARGET | True |
| DPRTYPES | OBJECT,FP, OBJECT,SKY, TELLURIC,SKY |
