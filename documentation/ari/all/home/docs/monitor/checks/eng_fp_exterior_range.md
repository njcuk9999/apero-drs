---
card_label: 'ENG: FP Exterior Range'
card_icon: fa-solid fa-gear
---

# raw: ENG: FP Exterior Range

## Overview

This engineering sub-test checks Fabry-Perot exterior temperature stays
in range.

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
| Neil Cook | neil.cook@umontreal.ca |
| Etienne Artigau | etienne.artigau@umontreal.ca |

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

### aprofile_instrument/nirps_ha_rali.yaml, aprofile_instrument/nirps_he_rali.yaml

Performs the following test

```python
np.nanmin(HIERARCH ESO INS TEMP13 VAL) > 23.496 and np.nanmax(HIERARCH ESO INS TEMP13 VAL) < 24.504
```

#### Resolved values

| Key | Value |
| --- | --- |
| TEST_KEY | fp_exterior_range |
| ENABLED | True |
| METRIC_KEY | HIERARCH ESO INS TEMP13 VAL |
| LOWER_LIMIT | 23.496 |
| UPPER_LIMIT | 24.504 |
| XMIN | xmin |
| XMAX | xmax |
