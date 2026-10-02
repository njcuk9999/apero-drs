---
card_label: lbl_seq
card_icon: fa-solid fa-diagram-project
related:
  - apero/instruments/spirou
  - apero/instruments/spirou/recipes/
  - apero/instruments/spirou/file_definitions/
  - glossary
---

# lbl_seq

**Instrument:** SPIROU

Run the lbl recipes inside apero.

Note this is slightly different to other apero recipes in that although we
process individual files in some lbl recipes, we actually send object names
(similarly to `apero_mk_template`) to the apero-lbl recipes.

This means that `SKIP_XXXX = True` skips entire object names, NOT individual files for an object.
The consequence of this is that if you skip an object name, you will not be able to process any new files for that object name.
Use `apero_reset.py --only_lbl` to reset the lbl directory completely (without reseting other apero products).
Or use `apero_remove.py --block=lbl --objname={objname}` to remove the files for a specific object name.


This must be run after the telluric correction steps have been completed for all science targets.

The following recipes are run:

    - LBLREF: Generates symlinks in the lbl directory (in the way LBL expects files to be)
    - LBLMASK_FP: Generates the FP mask file from extract FP files
    - LBLCOMPUTE_FP: Runs lbl compute on FP files
    - LBLCOMPUTE_FP: Runs lbl compile on FP files
    - LBLMASK_SCI: Generates the mask file from apero templates for each science target DRSOBJN (object) name
    - LBLCOMPUTE_SCI: Runs lbl compute on science target DRSOBJN (objname) name
    - LBLCOMPILE_SCI: Runs lbl compile on science target DRSOBJN (objname) name

## Recipes in this sequence

| ORDER | RECIPE | SHORTNAME | RECIPE KIND | REF RECIPE | FILTERS |
| --- | --- | --- | --- | --- | --- |
| 1 | apero_lbl_ref_spirou.py | LBLREF | lbl-ref | No | -- |
| 2 | apero_lbl_mask_spirou.py | LBLMASK_FP | lbl-mask-fp | No | -- |
| 3 | apero_lbl_compute_spirou.py | LBLCOMPUTE_FP | lbl-compute-fp | No | -- |
| 4 | apero_lbl_compile_spirou.py | LBLCOMPILE_FP | lbl-compile-fp | No | -- |
| 5 | apero_lbl_mask_spirou.py | LBLMASK_SCI | lbl-mask-sci | No | KW_OBJNAME: SCIENCE_TARGETS |
| 6 | apero_lbl_compute_spirou.py | LBLCOMPUTE_SCI | lbl-compute-sci | No | KW_OBJNAME: SCIENCE_TARGETS |
| 7 | apero_lbl_compile_spirou.py | LBLCOMPILE_SCI | lbl-compile-sci | No | KW_OBJNAME: SCIENCE_TARGETS |
