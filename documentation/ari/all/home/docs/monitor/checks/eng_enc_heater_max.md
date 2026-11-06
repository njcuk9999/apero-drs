---
card_label: 'ENG: Enclosure Heater Power Max'
card_icon: fa-solid fa-gear
---

# raw: ENG: Enclosure Heater Power Max

## Overview

This engineering sub-test checks enclosure heater power stays below
maximum.

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
np.nanmax(metric_key) < limit
```

#### Resolved values

| Key | Value |
| --- | --- |
| TEST_KEY | enclosure_heater_power_max |
| ENABLED | True |
| METRIC_KEY | metric_key |
| LIMIT | limit |
| METRIC | metric |

### aprofile_instrument/nirps_ha_rali.yaml, aprofile_instrument/nirps_he_rali.yaml

Performs the following test

```python
np.nanmax(HIERARCH ESO INS SENS121 VAL) < 90.0
```

#### Resolved values

| Key | Value |
| --- | --- |
| TEST_KEY | enclosure_heater_power_max |
| ENABLED | True |
| METRIC_KEY | HIERARCH ESO INS SENS121 VAL |
| LIMIT | 90.0 |
| METRIC | metric |
