---
card_label: pp_seq_opt
card_icon: fa-solid fa-diagram-project
---

# pp_seq_opt

**Instrument:** SPIROU

Run apero_preprocess on specific files (based on DPRTYPE)

    - `PP_CAL` will only preprocess the calibration files
    - `PP_SCI` will only preprocess the science files (non telluric hot star files)
    - `PP_TELL` will only preprocess the telluric hot star files
    - `PP_HC1HC1` will only preprocess files with DPRTYPE `HC1_HC1` (i.e. UNe in both fibers)
    - `PP_FPFP` will only preprocess files with DPRTYPE `FP_FP` (i.e. FP in both fibers)
    - `PP_DFP` will only preprocess files with DPRTYPE `DARK_FP` (i.e. DARK in science fiber and FP in the reference fiber)
    - `PP_FPD` will only preprocess files with DPRTYPE `FP_DARK` (i.e. FP in science fiber and DARK in the reference fiber)
    - `PP_SKY` will only preprocess files with DPRTYPE `DARK_DARK_SKY` (i.e. files identified as sky in science fiber and DARK in reference fiber)
    - `PP_LFC` will only preprocess files with DPRTYPE `LFC_LFC` (i.e. LFC in both fibers)
    - `PP_LFCFP` will only preprocess files with DPRTYPE `LFC_FP` (i.e. LFC in science fiber and FP in reference fiber)
    - `PP_FPLFC` will only preprocess files with DPRTYPE `FP_LFC` (i.e. FP in science fiber and LFC in reference fiber)
    - `PP_EVERY` will preprocess all files (similarly to using `pp_seq`)

## Recipes in this sequence

| ORDER | RECIPE | SHORTNAME | RECIPE KIND | REF RECIPE | FILTERS | ARGS |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | apero_preprocess_spirou.py | PP_CAL | pre-cal | No | KW_OBJNAME: CALIB |  |
| 2 | apero_preprocess_spirou.py | PP_SCI | pre-sci | No | KW_OBJNAME: SCIENCE_TARGETS \|br\| KW_DPRTYPE: OBJ_DARK, OBJ_FP, POLAR_DARK, POLAR_FP |  |
| 3 | apero_preprocess_spirou.py | PP_TEL | pre-tel | No | KW_OBJNAME: TELLURIC_TARGETS |  |
| 4 | apero_preprocess_spirou.py | PP_HC1HC1 | pre-hc1hc1 | No | -- | {files}=[RAW_HCONE_HCONE] |
| 5 | apero_extract_spirou.py | PP_HC2HC2 | pre-hc2hc2 | No | -- | {files}=[RAW_HCTWO_HCTWO] |
| 6 | apero_preprocess_spirou.py | PP_FPFP | pre-fpfp | No | -- | {files}=[RAW_FP_FP] |
| 7 | apero_preprocess_spirou.py | PP_FF | pre-ff | No | -- | {files}=[RAW_FLAT_FLAT] |
| 8 | apero_preprocess_spirou.py | PP_DFP | pre-dfp | No | -- | {files}=[RAW_DARK_FP] |
| 9 | apero_preprocess_spirou.py | PP_FPD | pre-fpd | No | -- | {files}=[RAW_FP_DARK] |
| 10 | apero_preprocess_spirou.py | PP_SKY | pre-sky | No | -- | {files}=[RAW_DARK_DARK_SKY] |
| 11 | apero_preprocess_spirou.py | PP_LFC | pre-lfc | No | -- | {files}=[RAW_LFC_LFC] |
| 12 | apero_preprocess_spirou.py | PP_LFCFP | pre-lfcfp | No | -- | {files}=[RAW_LFC_FP] |
| 13 | apero_preprocess_spirou.py | PP_FPLFC | pre-fplfc | No | -- | {files}=[RAW_FP_LFC] |
| 14 | apero_preprocess_spirou.py | PP_FPHC1 | pre-fphc1 | No | -- | {files}=[RAW_FP_HCONE] |
| 15 | apero_preprocess_spirou.py | PP_HC1FP | pre-hc1fp | No | -- | {files}=[RAW_HCONE_FP] |
| 16 | apero_preprocess_spirou.py | PP_EVERY | pre | No | -- | {files}=[DRS_RAW] |
