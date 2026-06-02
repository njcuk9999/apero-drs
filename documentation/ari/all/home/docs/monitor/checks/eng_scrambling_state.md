---
card_label: 'ENG: Scrambling Status Science'
card_icon: fa-solid fa-gear
---

# raw: ENG: Scrambling Status Science

## Overview

This engineering sub-test checks AO scrambling status remains enabled.

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

### aprofile_instrument/nirps_ha_rali.yaml, aprofile_instrument/nirps_he_rali.yaml

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
