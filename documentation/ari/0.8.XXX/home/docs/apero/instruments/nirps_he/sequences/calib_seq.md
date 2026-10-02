---
card_label: calib_seq
card_icon: fa-solid fa-diagram-project
related:
  - apero/instruments/nirps_he
  - apero/instruments/nirps_he/recipes/
  - apero/instruments/nirps_he/file_definitions/
  - glossary
---

# calib_seq

**Instrument:** NIRPS_HE

!!! warning "Undocumented"

    No description has been written for `calib_seq` yet.

## Flow

<!-- Replace the diagram below with the real steps. -->

```mermaid
flowchart TD
    A[Inputs] --> B[TODO: describe the steps]
    B --> C[Outputs]
```

## Recipes in this sequence

| ORDER | RECIPE | SHORTNAME | RECIPE KIND | REF RECIPE | ARGS |
| --- | --- | --- | --- | --- | --- |
| 1 | apero_badpix_nirps_he.py | BAD | calib-night | No |  |
| 2 | apero_loc_nirps_he.py | LOC | calib-night | No | {files}=[DARK_FLAT, CALIB_DARK_FLAT, FLAT_DARK, CALIB_FLAT_DARK] |
| 3 | apero_shape_nirps_he.py | SHAPE | calib-night | No |  |
| 4 | apero_flat_nirps_he.py | FF | calib-night | No | {files}=[FLAT_FLAT, DARK_FLAT, FLAT_DARK, CALIB_FLAT_DARK, CALIB_DARK_FLAT] |
| 5 | apero_wave_night_nirps_he.py | WAVE | calib-night | No |  |
