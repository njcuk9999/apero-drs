---
card_label: limited_seq
card_icon: fa-solid fa-diagram-project
related:
  - apero/instruments/nirps_ha
  - apero/instruments/nirps_ha/recipes/
  - apero/instruments/nirps_ha/file_definitions/
  - glossary
---

# limited_seq

**Instrument:** NIRPS_HA

!!! warning "Undocumented"

    No description has been written for `limited_seq` yet.

## Flow

<!-- Replace the diagram below with the real steps. -->

```mermaid
flowchart TD
    A[Inputs] --> B[TODO: describe the steps]
    B --> C[Outputs]
```

## Recipes in this sequence

| ORDER | RECIPE | SHORTNAME | RECIPE KIND | REF RECIPE | FIBER | FILTERS | ARGS | KWARGS |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | apero_pp_ref_nirps_ha.py | PPREF | pre-reference | Yes | -- | -- |  |  |
| 2 | apero_preprocess_nirps_ha.py | PP | pre-all | No | -- | -- |  |  |
| 3 | apero_dark_ref_nirps_ha.py | DARKREF | calib-reference | Yes | -- | -- |  |  |
| 4 | apero_badpix_nirps_ha.py | BADREF | calib-reference | Yes | -- | -- |  |  |
| 5 | apero_loc_nirps_ha.py | LOCREF | calib-reference | Yes | -- | -- | {files}=[DARK_FLAT, CALIB_DARK_FLAT, FLAT_DARK, CALIB_FLAT_DARK] |  |
| 6 | apero_shape_ref_nirps_ha.py | SHAPEREF | calib-reference | Yes | -- | -- |  |  |
| 7 | apero_shape_nirps_ha.py | SHAPELREF | calib-reference | Yes | -- | -- |  |  |
| 8 | apero_flat_nirps_ha.py | FLATREF | calib-reference | Yes | -- | -- |  |  |
| 9 | apero_leak_ref_nirps_ha.py | LEAKREF | calib-reference | Yes | -- | -- |  |  |
| 10 | apero_wave_ref_nirps_ha.py | WAVEREF | calib-reference | Yes | -- | -- |  | --hcfiles=[HCONE_HCONE] \|br\| --fpfiles=[FP_FP] |
| 11 | apero_badpix_nirps_ha.py | BAD | calib-night | No | -- | -- |  |  |
| 12 | apero_loc_nirps_ha.py | LOC | calib-night | No | -- | -- | {files}=[DARK_FLAT, CALIB_DARK_FLAT, FLAT_DARK, CALIB_FLAT_DARK] |  |
| 13 | apero_shape_nirps_ha.py | SHAPE | calib-night | No | -- | -- |  |  |
| 14 | apero_flat_nirps_ha.py | FF | calib-night | No | -- | -- | {files}=[FLAT_FLAT, DARK_FLAT, FLAT_DARK, CALIB_FLAT_DARK, CALIB_DARK_FLAT] |  |
| 15 | apero_wave_night_nirps_ha.py | WAVE | calib-night | No | -- | -- |  |  |
| 16 | apero_extract_nirps_ha.py | EXTTELL | extract-hotstar | No | -- | KW_OBJNAME: TELLURIC_TARGETS | {files}=[OBJ_DARK, OBJ_FP, OBJ_SKY, OBJ_TUN, FLUXSTD_SKY, TELLU_SKY] |  |
| 17 | apero_extract_nirps_ha.py | EXTOBJ | extract-science | No | -- | KW_OBJNAME: SCIENCE_TARGETS | {files}=[OBJ_DARK, OBJ_FP, OBJ_SKY, OBJ_TUN, FLUXSTD_SKY, TELLU_SKY] |  |
| 18 | apero_mk_tellu_nirps_ha.py | MKTELLU1 | tellu-hotstar | No | A | KW_OBJNAME: TELLURIC_TARGETS \|br\| KW_DPRTYPE: OBJ_DARK, OBJ_FP, OBJ_SKY, OBJ_TUN, FLUXSTD_SKY, TELLU_SKY | {files}=[EXT_E2DS_FF] |  |
| 19 | apero_mk_model_nirps_ha.py | MKTMOD1 | tellu-hotstar | No | -- | -- |  |  |
| 20 | apero_fit_tellu_nirps_ha.py | MKTFIT1 | tellu-hotstar | No | A | KW_OBJNAME: TELLURIC_TARGETS \|br\| KW_DPRTYPE: OBJ_DARK, OBJ_FP, OBJ_SKY, OBJ_TUN, FLUXSTD_SKY, TELLU_SKY | {files}=[EXT_E2DS_FF] |  |
| 21 | apero_mk_template_nirps_ha.py | MKTEMP1 | tellu-hotstar | No | A | KW_OBJNAME: TELLURIC_TARGETS \|br\| KW_DPRTYPE: OBJ_DARK, OBJ_FP, OBJ_SKY, OBJ_TUN, FLUXSTD_SKY, TELLU_SKY |  |  |
| 22 | apero_mk_tellu_nirps_ha.py | MKTELLU2 | tellu-hotstar | No | A | KW_OBJNAME: TELLURIC_TARGETS \|br\| KW_DPRTYPE: OBJ_DARK, OBJ_FP, OBJ_SKY, OBJ_TUN, FLUXSTD_SKY, TELLU_SKY | {files}=[EXT_E2DS_FF] |  |
| 23 | apero_mk_model_nirps_ha.py | MKTMOD2 | tellu-hotstar | No | -- | -- |  |  |
| 24 | apero_fit_tellu_nirps_ha.py | MKTFIT2 | tellu-hotstar | No | A | KW_OBJNAME: TELLURIC_TARGETS \|br\| KW_DPRTYPE: OBJ_DARK, OBJ_FP, OBJ_SKY, OBJ_TUN, FLUXSTD_SKY, TELLU_SKY | {files}=[EXT_E2DS_FF] |  |
| 25 | apero_mk_template_nirps_ha.py | MKTEMP2 | tellu-hotstar | No | A | KW_OBJNAME: TELLURIC_TARGETS \|br\| KW_DPRTYPE: OBJ_DARK, OBJ_FP, OBJ_SKY, OBJ_TUN, FLUXSTD_SKY, TELLU_SKY |  |  |
| 26 | apero_fit_tellu_nirps_ha.py | FTFIT1 | tellu-science | No | A | KW_OBJNAME: SCIENCE_TARGETS \|br\| KW_DPRTYPE: OBJ_DARK, OBJ_FP, OBJ_SKY, OBJ_TUN, FLUXSTD_SKY, TELLU_SKY | {files}=[EXT_E2DS_FF] |  |
| 27 | apero_mk_template_nirps_ha.py | FTTEMP1 | tellu-science | No | A | KW_OBJNAME: SCIENCE_TARGETS \|br\| KW_DPRTYPE: OBJ_DARK, OBJ_FP, OBJ_SKY, OBJ_TUN, FLUXSTD_SKY, TELLU_SKY |  |  |
| 28 | apero_fit_tellu_nirps_ha.py | FTFIT2 | tellu-science | No | A | KW_OBJNAME: SCIENCE_TARGETS \|br\| KW_DPRTYPE: OBJ_DARK, OBJ_FP, OBJ_SKY, OBJ_TUN, FLUXSTD_SKY, TELLU_SKY | {files}=[EXT_E2DS_FF] |  |
| 29 | apero_mk_template_nirps_ha.py | FTTEMP2 | tellu-science | No | A | KW_OBJNAME: SCIENCE_TARGETS \|br\| KW_DPRTYPE: OBJ_DARK, OBJ_FP, OBJ_SKY, OBJ_TUN, FLUXSTD_SKY, TELLU_SKY |  |  |
| 30 | apero_ccf_nirps_ha.py | CCF | rv-tcorr | No | A | KW_DPRTYPE: OBJ_DARK, OBJ_FP, OBJ_SKY, OBJ_TUN, FLUXSTD_SKY, TELLU_SKY \|br\| KW_OBJNAME: SCIENCE_TARGETS | {files}=[TELLU_OBJ] |  |
| 31 | apero_lbl_ref_nirps_ha.py | LBLREF | lbl-ref | No | -- | -- |  |  |
| 32 | apero_lbl_mask_nirps_ha.py | LBLMASK_SCI | lbl-mask-sci | No | -- | KW_OBJNAME: SCIENCE_TARGETS |  |  |
| 33 | apero_lbl_compute_nirps_ha.py | LBLCOMPUTE_SCI | lbl-compute-sci | No | -- | KW_OBJNAME: SCIENCE_TARGETS |  |  |
| 34 | apero_lbl_compile_nirps_ha.py | LBLCOMPILE_SCI | lbl-compile-sci | No | -- | KW_OBJNAME: SCIENCE_TARGETS |  |  |
| 35 | apero_postprocess_nirps_ha.py | SCIPOST | post-science | No | -- | KW_DPRTYPE: OBJ_DARK, OBJ_FP, OBJ_SKY, OBJ_TUN, FLUXSTD_SKY, TELLU_SKY \|br\| KW_OBJNAME: SCIENCE_TARGETS | {files}=[DRS_PP] |  |
