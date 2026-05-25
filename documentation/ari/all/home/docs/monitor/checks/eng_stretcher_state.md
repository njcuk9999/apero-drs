---
card_label: 'ENG: Stretcher Status State'
card_icon: fa-solid fa-gear
---

# raw: ENG: Stretcher Status State

## Overview

This engineering sub-test checks stretcher status remains enabled.

## Requirements

- [BLANK](checks/blank.md)
- [HAS_OBSDIR](checks/has_obsdir.md)
- [CALIB_TEST](checks/calib_test.md)

## What to do

If FALSE please [re-run the check](how_to/run_check.md) with
--test=ENG_TEST.

If still FALSE, report the failing ENG_TEST details and contact
[Contact list C1](#contact-list-c1).

## Contact

### Contact list C1
<a id="contact-list-c1"></a>

| Name | Email |
| --- | --- |
| Lison Malo * | lison.malo@umontreal.ca |
| Gaspare Lo Curto | glocurto@eso.org |
| Neil Cook | neil.cook@umontreal.ca |
| Etienne Artigau | etienne.artigau@umontreal.ca |

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
