---
card_label: quick_seq
card_icon: fa-solid fa-diagram-project
related:
  - apero/instruments/nirps_ha
  - apero/instruments/nirps_ha/recipes/
  - apero/instruments/nirps_ha/file_definitions/
  - glossary
---

# quick_seq

**Instrument:** NIRPS_HA

!!! warning "Undocumented"

    No description has been written for `quick_seq` yet.

## Flow

<!-- Replace the diagram below with the real steps. -->

```mermaid
flowchart TD
    A[Inputs] --> B[TODO: describe the steps]
    B --> C[Outputs]
```

## Recipes in this sequence

| ORDER | RECIPE | SHORTNAME | RECIPE KIND | REF RECIPE | FILTERS | ARGS |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | apero_extract_nirps_ha.py | EXTQUICK | extract-quick | No | KW_OBJNAME: SCIENCE_TARGETS \|br\| KW_DPRTYPE: OBJ_DARK, OBJ_FP, OBJ_SKY, OBJ_TUN, FLUXSTD_SKY, TELLU_SKY | {files}=[OBJ_DARK, OBJ_FP, OBJ_SKY, OBJ_TUN, FLUXSTD_SKY, TELLU_SKY] |
