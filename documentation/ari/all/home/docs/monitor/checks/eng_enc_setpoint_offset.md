---
card_label: 'ENG: Enclosure Setpoint Offset'
card_icon: fa-solid fa-gear
---

# raw: ENG: Enclosure Setpoint Offset

## Overview

This engineering sub-test checks mean enclosure temperature offset from
setpoint.

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
| Gaspare Lo Curto * | glocurto@eso.org |
| Lison Malo | lison.malo@umontreal.ca |
| Neil Cook | neil.cook@umontreal.ca |
| Etienne Artigau | etienne.artigau@umontreal.ca |

## Check logic

### generic

Performs the following test

```python
np.abs(np.nanmean(sensor_key - setpoint_key)) < limit
```

#### Resolved values

| Key | Value |
| --- | --- |
| TEST_KEY | enclosure_setpoint_offset |
| ENABLED | True |
| SENSOR_KEY | sensor_key |
| SETPOINT_KEY | setpoint_key |
| LIMIT | limit |
| METRIC | metric |

### aprofile_instrument/nirps_he_rali.yaml

Performs the following test

```python
np.abs(np.nanmean(HIERARCH ESO INS TEMP185 VAL - HIERARCH ESO INS TEMP187 VAL)) < 0.1
```

#### Resolved values

| Key | Value |
| --- | --- |
| TEST_KEY | enclosure_setpoint_offset |
| ENABLED | True |
| SENSOR_KEY | HIERARCH ESO INS TEMP185 VAL |
| SETPOINT_KEY | HIERARCH ESO INS TEMP187 VAL |
| LIMIT | 0.1 |
| METRIC | metric |
