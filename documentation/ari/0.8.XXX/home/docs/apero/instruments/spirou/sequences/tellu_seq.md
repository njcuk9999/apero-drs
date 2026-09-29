---
card_label: tellu_seq
card_icon: fa-solid fa-diagram-project
---

# tellu_seq

**Instrument:** SPIROU

Run all nightly hot star telluric calibrations steps.

This should be run after preprocessing of (at least) all telluric hot star files for all nights being reduced.
This should also be run after all calibration (reference and nightly) steps have been done.

Include the following recipes:

    - EXTTELL: Extracts all hot star files
    - MKTELLU1: First pass at making hot star trans files
    - MKTMOD1: Combines all hot star trans files from MKTELLU1 into a telluric model
    - MKFIT1: Correct for telluric absorption in the hot star files (without template)
    - MKTEMP1: Make a template for the hot star files (using hot stars from MKFIT1)
    - MKTELLU2: Second pass at making hot star trans files (with corrected hot stars + template)
    - MKTMOD2: Combines all hot star trans files from MKTELLU2 into a telluric model
    - MKTFIT2: Correct for telluric absorption in the hot star files (with template)
    - MKTEMP2: Make a template for the hot star files (with corrected hot stars from MKTFIT2)

## Recipes in this sequence

| ORDER | RECIPE | SHORTNAME | RECIPE KIND | REF RECIPE | FIBER | FILTERS | ARGS |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | apero_extract_spirou.py | EXTTELL | extract-hotstar | No | -- | KW_OBJNAME: TELLURIC_TARGETS \|br\| KW_DPRTYPE: OBJ_DARK, OBJ_FP, POLAR_DARK, POLAR_FP | {files}=[OBJ_DARK, OBJ_FP, POLAR_DARK, POLAR_FP] |
| 2 | apero_mk_tellu_spirou.py | MKTELLU1 | tellu-hotstar | No | AB | KW_OBJNAME: TELLURIC_TARGETS \|br\| KW_DPRTYPE: OBJ_DARK, OBJ_FP, POLAR_DARK, POLAR_FP | {files}=[EXT_E2DS_FF] |
| 3 | apero_mk_model_spirou.py | MKTMOD1 | tellu-hotstar | No | -- | -- |  |
| 4 | apero_fit_tellu_spirou.py | MKTFIT1 | tellu-hotstar | No | AB | KW_OBJNAME: TELLURIC_TARGETS \|br\| KW_DPRTYPE: OBJ_DARK, OBJ_FP, POLAR_DARK, POLAR_FP | {files}=[EXT_E2DS_FF] |
| 5 | apero_mk_template_spirou.py | MKTEMP1 | tellu-hotstar | No | AB | KW_OBJNAME: TELLURIC_TARGETS \|br\| KW_DPRTYPE: OBJ_DARK, OBJ_FP, POLAR_DARK, POLAR_FP | {files}=[EXT_E2DS_FF] |
| 6 | apero_mk_tellu_spirou.py | MKTELLU2 | tellu-hotstar | No | AB | KW_OBJNAME: TELLURIC_TARGETS \|br\| KW_DPRTYPE: OBJ_DARK, OBJ_FP, POLAR_DARK, POLAR_FP | {files}=[EXT_E2DS_FF] |
| 7 | apero_mk_model_spirou.py | MKTMOD2 | tellu-hotstar | No | -- | -- |  |
| 8 | apero_fit_tellu_spirou.py | MKTFIT2 | tellu-hotstar | No | AB | KW_OBJNAME: TELLURIC_TARGETS \|br\| KW_DPRTYPE: OBJ_DARK, OBJ_FP, POLAR_DARK, POLAR_FP | {files}=[EXT_E2DS_FF] |
| 9 | apero_mk_template_spirou.py | MKTEMP2 | tellu-hotstar | No | AB | KW_OBJNAME: TELLURIC_TARGETS \|br\| KW_DPRTYPE: OBJ_DARK, OBJ_FP, POLAR_DARK, POLAR_FP | {files}=[EXT_E2DS_FF] |
