---
card_label: 'ENG: FP Interior RMS'
card_icon: fa-solid fa-gear
---

# raw: ENG: FP Interior RMS

## Overview

This engineering sub-test checks Fabry-Perot interior temperature stability.

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
| Philippe Vallee | philippe.vallee@umontreal.ca |
| Neil Cook | neil.cook@umontreal.ca |
| Etienne Artigau | etienne.artigau@umontreal.ca |

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
