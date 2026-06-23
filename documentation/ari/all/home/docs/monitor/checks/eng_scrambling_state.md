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
np.all(status_key == status_value) on dprtypes ['dprtypes']
```

#### Resolved values

| Key | Value |
| --- | --- |
| TEST_KEY | scrambling_status_science |
| ENABLED | True |
| STATUS_KEY | status_key |
| STATUS_VALUE | status_value |
| DPRTYPES | dprtypes |

### aprofile_instrument/nirps_ha_rali.yaml

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
| STATUS_VALUE | True |
| DPRTYPES | OBJECT,FP, OBJECT,SKY, TELLURIC,SKY |

### aprofile_instrument/nirps_he_rali.yaml

Performs the following test

```python
np.all(HIERARCH ESO INS2 AOS SCRAMB ST == ON) on dprtypes ['OBJECT,FP', 'OBJECT,SKY', 'TELLURIC,SKY']
```

#### Resolved values

| Key | Value |
| --- | --- |
| TEST_KEY | scrambling_status_science |
| ENABLED | True |
| STATUS_KEY | HIERARCH ESO INS2 AOS SCRAMB ST |
| STATUS_VALUE | ON |
| DPRTYPES | OBJECT,FP, OBJECT,SKY, TELLURIC,SKY |
