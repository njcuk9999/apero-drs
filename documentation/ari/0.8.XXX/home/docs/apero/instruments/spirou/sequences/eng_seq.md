---
card_label: eng_seq
card_icon: fa-solid fa-diagram-project
related:
  - apero/instruments/spirou
  - apero/instruments/spirou/recipes/
  - apero/instruments/spirou/file_definitions/
  - glossary
---

# eng_seq

**Instrument:** SPIROU

Run apero_extract on specific files (based on DPRTYPE)

This should be run after preprocessing of all this type of files (usually this is done using `pp_seq_opt`).
This should also be run after all calibration (reference and nightly) steps have been done.

    - `EXT_HC1HC1` will only extract files with DPRTYPE `HC1_HC1` (i.e. UNe in both fibers)
    - `EXT_FPFP` will only extract files with DPRTYPE `FP_FP` (i.e. FP in both fibers)
    - `EXT_FF` will only extract files with DPRTYPE `FLAT_FLAT` (i.e. FLAT in both fibers)
    - `EXT_DFP` will only extract files with DPRTYPE `DARK_FP` (i.e. DARK in science fiber and FP in the reference fiber)
    - `EXT_FPD` will only extract files with DPRTYPE `FP_DARK` (i.e. FP in science fiber and DARK in the reference fiber)
    - `EXT_SKY` will only extract files with DPRTYPE `DARK_DARK_SKY` (i.e. files identified as sky in science fiber and DARK in reference fiber)
    - `EXT_LFC` will only extract files with DPRTYPE `LFC_LFC` (i.e. LFC in both fibers)
    - `EXT_LFCFP` will only extract files with DPRTYPE `LFC_FP` (i.e. LFC in science fiber and FP in reference fiber)
    - `EXT_FPLFC` will only extract files with DPRTYPE `FP_LFC` (i.e. FP in science fiber and LFC in reference fiber)
    - `EXT_EVERY` will extract all files

## Recipes in this sequence

| ORDER | RECIPE | SHORTNAME | RECIPE KIND | REF RECIPE | ARGS |
| --- | --- | --- | --- | --- | --- |
| 1 | apero_extract_spirou.py | EXT_HC1HC1 | extract-hchc | No | {files}=[HCONE_HCONE] |
| 2 | apero_extract_spirou.py | EXT_FPFP | extract-fpfp | No | {files}=[FP_FP] |
| 3 | apero_extract_spirou.py | EXT_FF | extract-ff | No | {files}=[FLAT_FLAT] |
| 4 | apero_extract_spirou.py | EXT_DFP | extract-dfp | No | {files}=[DARK_FP] |
| 5 | apero_extract_spirou.py | EXT_FPD | extract-fpd | No | {files}=[FP_DARK] |
| 6 | apero_extract_spirou.py | EXT_SKY | extract-sky | No | {files}=[DARK_DARK_SKY] |
| 7 | apero_extract_spirou.py | EXT_LFC | extract-lfc | No | {files}=[LFC_LFC] |
| 8 | apero_extract_spirou.py | EXT_LFCFP | extract-lfcfp | No | {files}=[LFC_FP] |
| 9 | apero_extract_spirou.py | EXT_FPLFC | extract-fplfc | No | {files}=[FP_LFC] |
| 10 | apero_extract_spirou.py | EXT_FPHC1 | extract-fphc1 | No | {files}=[FP_HCONE] |
| 11 | apero_extract_spirou.py | EXT_HC1FP | extract-hc1fp | No | {files}=[HCONE_FP] |
| 12 | apero_extract_spirou.py | EXT_EVERY | extract-everything | No | {files}=[DRS_PP] |
| 13 | apero_extract_spirou.py | EXTQUICK_HC | extract-quick | No | {files}=[HCONE_HCONE] |
| 14 | apero_extract_spirou.py | EXTQUICK_FP | extract-quick | No | {files}=[FP_FP] |
