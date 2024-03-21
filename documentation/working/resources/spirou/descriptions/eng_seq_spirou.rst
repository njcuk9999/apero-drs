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