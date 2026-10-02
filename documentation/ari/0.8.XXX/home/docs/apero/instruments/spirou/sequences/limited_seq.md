---
card_label: limited_seq
card_icon: fa-solid fa-diagram-project
related:
  - apero/instruments/spirou
  - apero/instruments/spirou/recipes/
  - apero/instruments/spirou/file_definitions/
  - glossary
---

# limited_seq

**Instrument:** SPIROU

Run a limited set of files through the full process.

Equivlent to running the following sequences:

    - pp_seq
    - ref_seq
    - calib_seq
    - tellu_seq
    - science_seq
    - lbl_seq


But only on the targets set in `SCIENCE_TARGETS`.

See individual sequences for more information.

## Recipes in this sequence

| ORDER | RECIPE | SHORTNAME | RECIPE KIND | REF RECIPE | FIBER | FILTERS | ARGS | KWARGS |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | apero_preprocess_spirou.py | PP | pre-all | No | -- | -- |  |  |
| 2 | apero_dark_ref_spirou.py | DARKREF | calib-reference | Yes | -- | -- |  |  |
| 3 | apero_badpix_spirou.py | BADREF | calib-reference | Yes | -- | -- |  |  |
| 4 | apero_loc_spirou.py | LOCREF | calib-reference | Yes | -- | -- | {files}=[DARK_FLAT, FLAT_DARK] |  |
| 5 | apero_shape_ref_spirou.py | SHAPEREF | calib-reference | Yes | -- | -- |  |  |
| 6 | apero_shape_spirou.py | SHAPELREF | calib-reference | Yes | -- | -- |  |  |
| 7 | apero_flat_spirou.py | FLATREF | calib-reference | Yes | -- | -- |  |  |
| 8 | apero_thermal_spirou.py | THERM_REFI | calib-reference-I | Yes | -- | -- | {files}=[DARK_DARK_INT] |  |
| 9 | apero_leak_ref_spirou.py | LEAKREF | calib-reference | Yes | -- | -- |  |  |
| 10 | apero_wave_ref_spirou.py | WAVEREF | calib-reference | Yes | -- | -- |  | --hcfiles=[HCONE_HCONE] \|br\| --fpfiles=[FP_FP] |
| 11 | apero_thermal_spirou.py | THERM_REFT | calib-reference-T | Yes | -- | -- | {files}=[DARK_DARK_TEL] |  |
| 12 | apero_badpix_spirou.py | BAD | calib-night | No | -- | -- |  |  |
| 13 | apero_loc_spirou.py | LOC | calib-night | No | -- | -- | {files}=[DARK_FLAT, FLAT_DARK] |  |
| 14 | apero_shape_spirou.py | SHAPE | calib-night | No | -- | -- |  |  |
| 15 | apero_flat_spirou.py | FF | calib-night | No | -- | -- | {files}=[FLAT_FLAT, DARK_FLAT, FLAT_DARK] |  |
| 16 | apero_thermal_spirou.py | THERM_I | calib-night-I | No | -- | -- | {files}=[DARK_DARK_INT] |  |
| 17 | apero_wave_night_spirou.py | WAVE | calib-night | No | -- | -- |  |  |
| 18 | apero_thermal_spirou.py | THERM_T | calib-night-T | No | -- | -- | {files}=[DARK_DARK_TEL] |  |
| 19 | apero_extract_spirou.py | EXTTELL | extract-hotstar | No | -- | KW_OBJNAME: TELLURIC_TARGETS | {files}=[OBJ_DARK, OBJ_FP, POLAR_DARK, POLAR_FP] |  |
| 20 | apero_extract_spirou.py | EXTOBJ | extract-science | No | -- | KW_OBJNAME: SCIENCE_TARGETS | {files}=[OBJ_DARK, OBJ_FP, POLAR_DARK, POLAR_FP] |  |
| 21 | apero_mk_tellu_spirou.py | MKTELLU1 | tellu-hotstar | No | AB | KW_OBJNAME: TELLURIC_TARGETS \|br\| KW_DPRTYPE: OBJ_DARK, OBJ_FP, POLAR_DARK, POLAR_FP | {files}=[EXT_E2DS_FF] |  |
| 22 | apero_mk_model_spirou.py | MKTMOD1 | tellu-hotstar | No | -- | -- |  |  |
| 23 | apero_fit_tellu_spirou.py | MKTFIT1 | tellu-hotstar | No | AB | KW_OBJNAME: TELLURIC_TARGETS \|br\| KW_DPRTYPE: OBJ_DARK, OBJ_FP, POLAR_DARK, POLAR_FP | {files}=[EXT_E2DS_FF] |  |
| 24 | apero_mk_template_spirou.py | MKTEMP1 | tellu-hotstar | No | AB | KW_OBJNAME: TELLURIC_TARGETS \|br\| KW_DPRTYPE: OBJ_DARK, OBJ_FP, POLAR_DARK, POLAR_FP |  |  |
| 25 | apero_mk_tellu_spirou.py | MKTELLU2 | tellu-hotstar | No | AB | KW_OBJNAME: TELLURIC_TARGETS \|br\| KW_DPRTYPE: OBJ_DARK, OBJ_FP, POLAR_DARK, POLAR_FP | {files}=[EXT_E2DS_FF] |  |
| 26 | apero_mk_model_spirou.py | MKTMOD2 | tellu-hotstar | No | -- | -- |  |  |
| 27 | apero_fit_tellu_spirou.py | MKTFIT2 | tellu-hotstar | No | AB | KW_OBJNAME: TELLURIC_TARGETS \|br\| KW_DPRTYPE: OBJ_DARK, OBJ_FP, POLAR_DARK, POLAR_FP | {files}=[EXT_E2DS_FF] |  |
| 28 | apero_mk_template_spirou.py | MKTEMP2 | tellu-hotstar | No | AB | KW_OBJNAME: TELLURIC_TARGETS \|br\| KW_DPRTYPE: OBJ_DARK, OBJ_FP, POLAR_DARK, POLAR_FP |  |  |
| 29 | apero_fit_tellu_spirou.py | FTFIT1 | tellu-science | No | AB | KW_OBJNAME: SCIENCE_TARGETS \|br\| KW_DPRTYPE: OBJ_DARK, OBJ_FP, POLAR_DARK, POLAR_FP | {files}=[EXT_E2DS_FF] |  |
| 30 | apero_mk_template_spirou.py | FTTEMP1 | tellu-science | No | AB | KW_OBJNAME: SCIENCE_TARGETS \|br\| KW_DPRTYPE: OBJ_DARK, OBJ_FP, POLAR_DARK, POLAR_FP |  |  |
| 31 | apero_fit_tellu_spirou.py | FTFIT2 | tellu-science | No | AB | KW_OBJNAME: SCIENCE_TARGETS \|br\| KW_DPRTYPE: OBJ_DARK, OBJ_FP, POLAR_DARK, POLAR_FP | {files}=[EXT_E2DS_FF] |  |
| 32 | apero_mk_template_spirou.py | FTTEMP2 | tellu-science | No | AB | KW_OBJNAME: SCIENCE_TARGETS \|br\| KW_DPRTYPE: OBJ_DARK, OBJ_FP, POLAR_DARK, POLAR_FP |  |  |
| 33 | apero_ccf_spirou.py | CCF | rv-tcorr | No | AB | KW_DPRTYPE: OBJ_DARK, OBJ_FP, POLAR_DARK, POLAR_FP \|br\| KW_OBJNAME: SCIENCE_TARGETS | {files}=[TELLU_OBJ] |  |
| 34 | apero_pol_spirou.py | POLAR | polar-tcorr | No | AB | KW_DPRTYPE: POLAR_FP, POLAR_DARK \|br\| KW_OBJNAME: SCIENCE_TARGETS |  | --exposures=[TELLU_OBJ] |
| 35 | apero_lbl_ref_spirou.py | LBLREF | lbl-ref | No | -- | -- |  |  |
| 36 | apero_lbl_mask_spirou.py | LBLMASK_FP | lbl-mask-fp | No | -- | -- |  |  |
| 37 | apero_lbl_compute_spirou.py | LBLCOMPUTE_FP | lbl-compute-fp | No | -- | -- |  |  |
| 38 | apero_lbl_compile_spirou.py | LBLCOMPILE_FP | lbl-compile-fp | No | -- | -- |  |  |
| 39 | apero_lbl_mask_spirou.py | LBLMASK_SCI | lbl-mask-sci | No | -- | KW_OBJNAME: SCIENCE_TARGETS |  |  |
| 40 | apero_lbl_compute_spirou.py | LBLCOMPUTE_SCI | lbl-compute-sci | No | -- | KW_OBJNAME: SCIENCE_TARGETS |  |  |
| 41 | apero_lbl_compile_spirou.py | LBLCOMPILE_SCI | lbl-compile-sci | No | -- | KW_OBJNAME: SCIENCE_TARGETS |  |  |
| 42 | apero_postprocess_spirou.py | SCIPOST | post-science | No | -- | KW_DPRTYPE: OBJ_DARK, OBJ_FP, POLAR_DARK, POLAR_FP \|br\| KW_OBJNAME: SCIENCE_TARGETS | {files}=[DRS_PP] |  |
