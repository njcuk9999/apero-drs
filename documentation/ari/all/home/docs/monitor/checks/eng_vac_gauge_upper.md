---
card_label: 'ENG: Vacuum Gauge Upper'
card_icon: fa-solid fa-gear
---

# raw: ENG: Vacuum Gauge Upper

## Overview

This engineering sub-test checks that vacuum gauge pressure stays below
limit.

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
| Etienne Artigau * | etienne.artigau@umontreal.ca |
| Lison Malo | lison.malo@umontreal.ca |
| Neil Cook | neil.cook@umontreal.ca |

## Check logic

### generic

Performs the following test

```python
np.nanmax(metric_key) < limit
```

#### Resolved values

| Key | Value |
| --- | --- |
| TEST_KEY | vacuum_gauge_upper |
| ENABLED | True |
| METRIC_KEY | metric_key |
| LIMIT | limit |
| METRIC | metric |

### aprofile_instrument/nirps_ha_rali.yaml, aprofile_instrument/nirps_he_rali.yaml

Performs the following test

```python
np.nanmax(HIERARCH ESO INS PRES104 VAL) < 0.0001
```

#### Resolved values

| Key | Value |
| --- | --- |
| TEST_KEY | vacuum_gauge_upper |
| ENABLED | True |
| METRIC_KEY | HIERARCH ESO INS PRES104 VAL |
| LIMIT | 0.0001 |
| METRIC | metric |
