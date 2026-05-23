---
card_label: 'ENG: Stretcher Status State'
card_icon: fa-solid fa-gear
---

# raw: ENG: Stretcher Status State

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
np.all(np.char.upper(np.char.strip(status_key)) == np.char.upper('target'))
```

#### Resolved values

| Key | Value |
| --- | --- |
| TEST_KEY | stretcher_status_state |
| ENABLED | True |
| STATUS_KEY | status_key |
| TARGET | target |

### aprofile_instrument/nirps_he_rali.yaml

Performs the following test

```python
np.all(np.char.upper(np.char.strip(HIERARCH ESO INS OPTI10 STAT)) == np.char.upper(True))
```

#### Resolved values

| Key | Value |
| --- | --- |
| TEST_KEY | stretcher_status_state |
| ENABLED | True |
| STATUS_KEY | HIERARCH ESO INS OPTI10 STAT |
| TARGET | True |
