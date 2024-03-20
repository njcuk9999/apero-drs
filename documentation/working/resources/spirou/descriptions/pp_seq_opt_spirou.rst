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