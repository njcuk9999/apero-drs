---
card_label: File definitions
card_icon: fa-solid fa-file-lines
related:
  - apero/instruments/nirps_he
  - apero/instruments/nirps_he/recipes/
  - apero/instruments/nirps_he/sequences/
  - glossary
---

# File definitions (NIRPS_HE)

This is the complete file catalogue for NIRPS_HE. APERO uses these definitions to identify raw inputs, connect processed products to their inputs, and describe the files written by recipes.

The **Stage** column groups the full table by processing stage. `HDR[XXX]` denotes a value read from a FITS header.

| Stage | name | description | HDR[TRG_TYPE] | HDR[HIERARCH ESO DPR TYPE] | HDR[HIERARCH ESO DPR CATG] | HDR[INSTRUME] | HDR[HIERARCH ESO INS MODE] | HDR[DPRTYPE] | file type | suffix | input file | HDR[DRSOUTID] | basename | fibers | dbname | dbkey | HDR[KW_DPRTYPE] | ext name | ext input | col names | col input |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Raw files | RAW_DARK_DARK | Raw sci=DARK calib=DARK file | -- | DARK | CALIB | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_EFF_SKY_SKY | Raw sci=SKY calib=SKY file (eff) | -- | EFF,SKY,SKY | CALIB | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_NIGHT_SKY_SKY | Raw sci=SKY calib=SKY file (night) | NIGHT-SKY | OBJECT,SKY | -- | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_DAY_SKY_SKY | Raw sci=SKY calib=SKY file (day) | SKY | OBJECT,SKY | -- | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_DARK_FLAT | Raw sci=DARK calib=FP file | -- | ORDERDEF,DARK,LAMP | CALIB | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_FLAT_DARK | Raw sci=FLAT calib=DARK file | -- | ORDERDEF,LAMP,DARK | CALIB | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_FLAT_FLAT | Raw sci=FLAT calib=FLAT file | -- | FLAT,LAMP,LAMP | CALIB | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_DARK_FP | Raw sci=DARK calib=FP file | -- | CONTAM,DARK,FP | CALIB | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_FP_DARK | Raw sci=FP calib=DARK file | -- | CONTAM,FP,DARK | CALIB | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_FP_FP | Raw sci=FP calib=FP file | -- | WAVE,FP,FP | CALIB | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_LFC_LFC | Raw sci=LFC calib=LFC file | -- | WAVE,LFC,LFC | CALIB | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_LFC_FP | Raw sci=LFC calib=FP file | -- | WAVE,LFC,FP | CALIB | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_FP_LFC | Raw sci=FP calib=LFC file | -- | WAVE,FP,LFC | CALIB | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_LFC_HCONE | Raw sci=LFC calib=HC1 file | -- | WAVE,LFC,UN1 | CALIB | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_HCONE_LFC | Raw sci=HC1 calib=LFC file | -- | WAVE,UN1,LFC | CALIB | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_LED_LED | -- | -- | LED,LAMP | CALIB | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_FLAT_LED | -- | -- | FLAT,LED | CALIB | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_OBJ_DARK | Raw sci=OBJ calib=DARK file | TARGET | OBJECT,DARK | -- | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_OBJ_FP | Raw sci=OBJ calib=FP file | TARGET | OBJECT,FP | -- | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_OBJ_HCONE | Raw sci=OBJ calib=Hollow Cathode file, Uranium Neon lamp | TARGET | OBJECT,UN1 | -- | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_OBJ_SKY | Raw sci=OBJ calib=Sky file | TARGET | OBJECT,SKY | -- | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_OBJ_TUN | -- | TARGET | OBJECT,TUN | -- | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_SUN_FP | Raw sci=SUN calib=FP file | -- | SUN,FP,G2V | -- | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_SUN_DARK | Raw sci=SUN calib=DARK file | -- | SUN,DARK,G2V | -- | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_FLUXSTD_SKY | Raw sci=flux standard star calib=DARK file | -- | FLUX,STD,SKY | -- | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_TELLU_SKY | Raw sci=hot star calib=DARK file | -- | TELLURIC,SKY | -- | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_DARK_HCONE | Raw sci=DARK calib=Hollow Cathode file, where dark is an internal dark, Uranium Neon lamp | -- | WAVE,DARK,UN1 | CALIB | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_FP_HCONE | Raw sci=FP calib=Hollow Cathode file, Uranium Neon lamp | -- | WAVE,FP,UN1 | CALIB | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_HCONE_FP | Raw sci=Hollow Cathode calib=FP file, Uranium Neion lamp | -- | WAVE,UN1,FP | CALIB | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_HCONE_HCONE | Raw sci=Hollow Cathode calib=Hollow Cathode file, Uranium Neon lamp | -- | WAVE,UN1,UN1 | CALIB | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_HCONE_DARK | Raw sci=Hollow Cathode calib=DARK file, where dark is an internal dark, Uranium Neon lamp | -- | WAVE,UN1,DARK | CALIB | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_DARK_HCTWO | Raw sci=DARK calib=Hollow Cathode file, where dark is an internal dark, Uranium Neon lamp | -- | WAVE,DARK,UN2 | CALIB | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_FP_HCTWO | Raw sci=FP calib=Hollow Cathode file, Uranium Neon lamp | -- | WAVE,FP,UN2 | CALIB | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_HCTWO_FP | Raw sci=Hollow Cathode calib=FP file, Uranium Neion lamp | -- | WAVE,UN2,FP | CALIB | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_HCTWO_HCTWO | Raw sci=Hollow Cathode calib=Hollow Cathode file, Uranium Neon lamp | -- | WAVE,UN2,UN2 | CALIB | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_HCTWO_DARK | Raw sci=Hollow Cathode calib=DARK file, where dark is an internal dark, Uranium Neon lamp | -- | WAVE,UN2,DARK | CALIB | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_HCONE_HCTWO | Raw sci=Hollow Cathode calib=Hollow Cathode file, Uranium Neon lamp | -- | WAVE,UN1,UN2 | CALIB | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_HCTWO_HCONE | Raw sci=Hollow Cathode calib=Hollow Cathode file, Uranium Neon lamp | -- | WAVE,UN2,UN1 | CALIB | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_HCONE_LFC | Raw sci=Hollow Cathode calib=LFC file, Uranium Neon lamp | -- | WAVE,UN1,LFC | CALIB | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_HCTWO_LFC | Raw sci=Hollow Cathode calib=LFC file, Uranium Neon lamp | -- | WAVE,UN2,LFC | CALIB | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_CALIB_DARK_FLAT | Raw sci=DARK calib=FLAT test file | -- | FLAT,DARK,LAMP | CALIB | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_CALIB_FLAT_DARK | Raw sci=FLAT calib=DARK test file | -- | FLAT,LAMP,DARK | CALIB | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_TEST_DARK_FP | Raw sci=DARK calib=FP test file | -- | CONTAM,DARK,FP | TEST | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_TEST_DARK_FLAT | Raw sci=DARK calib=FLAT test file | -- | FLAT,DARK,LAMP | TEST | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_TEST_FLAT_DARK | Raw sci=FLAT calib=DARK test file | -- | FLAT,LAMP,DARK | TEST | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_TEST_FP_FP | Raw sci=FP calib=FP test file | -- | WAVE,FP,FP | TEST | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_TEST_LED_LED | Raw sci=LED calib=LED test file | -- | LED,LAMP | TEST | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_TEST_HCONE_HCONE | Raw sci=Hollow Cathode calib=Hollow Cathode test file | -- | WAVE,UN1,UN1 | TEST | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_TEST_FP_HCONE | Raw sci=FP calib=Hollow Cathode test file | -- | WAVE,FP,UN1 | TEST | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_TEST_HCONE_FP | Raw sci=Hollow Cathode calib=FP test file | -- | WAVE,UN1,FP | TEST | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_TEST_HCTWO_HCTWO | Raw sci=Hollow Cathode calib=Hollow Cathode test file | -- | WAVE,UN2,UN2 | TEST | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_TEST_FP_HCTWO | Raw sci=FP calib=Hollow Cathode test file | -- | WAVE,FP,UN2 | TEST | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_TEST_HCTWO_FP | Raw sci=Hollow Cathode calib=FP test file | -- | WAVE,UN2,FP | TEST | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_TEST_EFF_SKY_SKY | Raw sci=SKY calib=SKY test file (eff) | -- | EFF,SKY,SKY | TEST | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_TEST_NIGHT_SKY_SKY | Raw sci=SKY calib=SKY test file (night) | NIGHT-SKY | OBJECT,SKY | -- | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_TEST_DARK | Raw sci=DARK calib=DARK test file | -- | DARK | TEST | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Raw files | RAW_TEST_FP_DARK | Raw sci=FP calib=DARK test file | -- | CONTAM,FP,DARK | TEST | NIRPS | HE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | DARK_DARK | Preprocessed sci=DARK calib=DARK file | -- | -- | -- | -- | -- | DARK_DARK | .fits | _pp | RAW_DARK_DARK | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | EFF_SKY_SKY | Preprocessed sci=SKY calib=SKY file | -- | -- | -- | -- | -- | EFF_SKY_SKY | .fits | _pp | RAW_EFF_SKY_SKY | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | NIGHT_SKY_SKY | Preprocessed sci=SKY calib=SKY file | -- | -- | -- | -- | -- | NIGHT_SKY_SKY | .fits | _pp | RAW_NIGHT_SKY_SKY | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | DAY_SKY_SKY | Preprocessed sci=SKY calib=SKY file | -- | -- | -- | -- | -- | DAY_SKY_SKY | .fits | _pp | RAW_DAY_SKY_SKY | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | FLAT_DARK | Preprocessed sci=FLAT calib=DARK file | -- | -- | -- | -- | -- | FLAT_DARK | .fits | _pp | RAW_FLAT_DARK | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | DARK_FLAT | Preprocessed sci=DARK calib=FLAT file | -- | -- | -- | -- | -- | DARK_FLAT | .fits | _pp | RAW_DARK_FLAT | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | FLAT_FLAT | Preprocessed sci=FLAT calib=FLAT file | -- | -- | -- | -- | -- | FLAT_FLAT | .fits | _pp | RAW_FLAT_FLAT | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | DARK_FP | Preprocessed sci=DARK calib=FP file | -- | -- | -- | -- | -- | DARK_FP | .fits | _pp | RAW_DARK_FP | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | FP_DARK | Preprocessed sci=FP calib=DARK file | -- | -- | -- | -- | -- | FP_DARK | .fits | _pp | RAW_FP_DARK | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | FP_FP | Preprocessed sci=FP calib=FP file | -- | -- | -- | -- | -- | FP_FP | .fits | _pp | RAW_FP_FP | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | LFC_LFC | Preprocessed sci=LFC calib=LFC file | -- | -- | -- | -- | -- | LFC_LFC | .fits | _pp | RAW_LFC_LFC | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | LFC_FP | Preprocessed sci=LFC calib=FP file | -- | -- | -- | -- | -- | LFC_FP | .fits | _pp | RAW_LFC_FP | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | FP_LFC | Preprocessed sci=FP calib=LFC file | -- | -- | -- | -- | -- | FP_LFC | .fits | _pp | RAW_FP_LFC | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | LFC_HCONE | Preprocessed sci=LFC calib=HC file | -- | -- | -- | -- | -- | LFC_HCONE | .fits | _pp | RAW_LFC_HCONE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | HCONE_LFC | Preprocessed sci=HC calib=LFC file | -- | -- | -- | -- | -- | HCONE_LFC | .fits | _pp | RAW_HCONE_LFC | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | LED_LED | Preprocessed sci=LED calib=LED file | -- | -- | -- | -- | -- | LED_LED | .fits | _pp | RAW_LED_LED | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | FLAT_LED | Preprocessed sci=FLAT calib=LED file | -- | -- | -- | -- | -- | FLAT_LED | .fits | _pp | RAW_FLAT_LED | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | OBJ_DARK | Preprocessed sci=OBJ calib=DARK file | -- | -- | -- | -- | -- | OBJ_DARK | .fits | _pp | RAW_OBJ_DARK | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | OBJ_FP | Preprocessed sci=OBJ calib=FP file | -- | -- | -- | -- | -- | OBJ_FP | .fits | _pp | RAW_OBJ_FP | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | OBJ_HCONE | Preprocessed sci=OBJ calib=Hollow Cathode | -- | -- | -- | -- | -- | OBJ_HCONE | .fits | _pp | RAW_OBJ_HCONE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | OBJ_SKY | Preprocessed sci=OBJ calib=SKY | -- | -- | -- | -- | -- | OBJ_SKY | .fits | _pp | RAW_OBJ_SKY | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | OBJ_TUN | Preprocessed sci=OBJ calib=Tungston lamp | -- | -- | -- | -- | -- | OBJ_TUN | .fits | _pp | RAW_OBJ_TUN | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | SUN_FP | Preprocessed sci=SUN calib=FP | -- | -- | -- | -- | -- | SUN_FP | .fits | _pp | RAW_SUN_FP | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | SUN_DARK | Preprocessed sci=SUN calib=DARK | -- | -- | -- | -- | -- | SUN_DARK | .fits | _pp | RAW_SUN_DARK | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | FLUXSTD_SKY | Preprocessed sci=Flux standard star calib=SKY | -- | -- | -- | -- | -- | FLUXSTD_SKY | .fits | _pp | RAW_FLUXSTD_SKY | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | TELLU_SKY | Preprocessed sci=Telluric hot star calib=SKY | -- | -- | -- | -- | -- | TELLU_SKY | .fits | _pp | RAW_TELLU_SKY | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | DARK_HCONE | Preprocessed sci=DARK calib=Hollow Cathode file, Uranium Neon lamp | -- | -- | -- | -- | -- | DARK_HCONE | .fits | _pp | RAW_DARK_HCONE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | FP_HCONE | Preprocessed sci=FP calib=Hollow Cathode file, Uranium Neon lamp | -- | -- | -- | -- | -- | FP_HCONE | .fits | _pp | RAW_FP_HCONE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | HCONE_FP | Preprocessed sci=Hollow Cathode calib=FP file, Uranium Neion lamp | -- | -- | -- | -- | -- | HCONE_FP | .fits | _pp | RAW_HCONE_FP | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | HCONE_HCONE | Preprocessed sci=Hollow Cathode calib=Hollow Cathode file, Uranium Neon lamp | -- | -- | -- | -- | -- | HCONE_HCONE | .fits | _pp | RAW_HCONE_HCONE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | HCONE_DARK | -- | -- | -- | -- | -- | -- | HCONE_DARK | .fits | _pp | RAW_HCONE_DARK | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | DARK_HCTWO | Preprocessed sci=DARK calib=Hollow Cathode file, Uranium Neon lamp | -- | -- | -- | -- | -- | DARK_HCOTWO | .fits | _pp | RAW_DARK_HCTWO | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | FP_HCTWO | Preprocessed sci=FP calib=Hollow Cathode file, Uranium Neon lamp | -- | -- | -- | -- | -- | FP_HCTWO | .fits | _pp | RAW_FP_HCTWO | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | HCTWO_FP | Preprocessed sci=Hollow Cathode calib=FP file, Uranium Neion lamp | -- | -- | -- | -- | -- | HCTWO_FP | .fits | _pp | RAW_HCTWO_FP | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | HCTWO_HCTWO | Preprocessed sci=Hollow Cathode calib=Hollow Cathode file, Uranium Neon lamp | -- | -- | -- | -- | -- | HCTWO_HCTWO | .fits | _pp | RAW_HCTWO_HCTWO | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | HCTWO_DARK | -- | -- | -- | -- | -- | -- | HCTWO_DARK | .fits | _pp | RAW_HCTWO_DARK | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | HCONE_HCTWO | Preprocessed sci=Hollow Cathode calib=Hollow Cathode file, Uranium Neon lamp | -- | -- | -- | -- | -- | HCONE_HCTWO | .fits | _pp | RAW_HCONE_HCTWO | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | HCTWO_HCONE | Preprocessed sci=Hollow Cathode calib=Hollow Cathode file, Uranium Neon lamp | -- | -- | -- | -- | -- | HCTWO_HCONE | .fits | _pp | RAW_HCTWO_HCONE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | HCONE_LFC | Preprocessed sci=Hollow Cathode calib=LFC file, Uranium Neon lamp | -- | -- | -- | -- | -- | HCONE_LFC | .fits | _pp | RAW_HCONE_LFC | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | HCTWO_LFC | Preprocessed sci=Hollow Cathode calib=LFC file, Uranium Neon lamp | -- | -- | -- | -- | -- | HCTWO_LFC | .fits | _pp | RAW_HCTWO_LFC | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | CALIB_DARK_FLAT | Preprocessed sci=DARK calib=FLAT test file | -- | -- | -- | -- | -- | CALIB_DARK_FLAT | .fits | _pp | RAW_CALIB_DARK_FLAT | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | CALIB_FLAT_DARK | Preprocessed sci=FLAT calib=DARK test file | -- | -- | -- | -- | -- | CALIB_FLAT_DARK | .fits | _pp | RAW_CALIB_FLAT_DARK | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | TEST_DARK_FLAT | Preprocessed sci=DARK calib=FLAT test file | -- | -- | -- | -- | -- | TEST_DARK_FLAT | .fits | _pp | RAW_TEST_DARK_FLAT | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | TEST_FLAT_DARK | Preprocessed sci=FLAT calib=DARK test file | -- | -- | -- | -- | -- | TEST_FLAT_DARK | .fits | _pp | RAW_TEST_FLAT_DARK | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | TEST_DARK_FP | Preprocessed sci=DARK calib=FP test file | -- | -- | -- | -- | -- | TEST_DARK_FP | .fits | _pp | RAW_TEST_DARK_FP | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | TEST_FP_FP | Preprocessed sci=FP calib=FP test file | -- | -- | -- | -- | -- | TEST_FP_FP | .fits | _pp | RAW_TEST_FP_FP | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | TEST_LED_LED | Preprocessed sci=LED calib=LED test file | -- | -- | -- | -- | -- | TEST_LED_LED | .fits | _pp | RAW_TEST_LED_LED | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | TEST_HCONE_HCONE | Preprocessed sci=Hollow Cathode calib=Hollow Cathode test file | -- | -- | -- | -- | -- | TEST_HCONE_HCONE | .fits | _pp | RAW_TEST_HCONE_HCONE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | TEST_FP_HCONE | Preprocessed sci=FP calib=Hollow Cathode test file | -- | -- | -- | -- | -- | TEST_FP_HCONE | .fits | _pp | RAW_TEST_FP_HCONE | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | TEST_HCONE_FP | Preprocessed sci=Hollow Cathode calib=FP test file | -- | -- | -- | -- | -- | TEST_HCONE_FP | .fits | _pp | RAW_TEST_HCONE_FP | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | TEST_HCTWO_HCTWO | Preprocessed sci=Hollow Cathode calib=Hollow Cathode test file | -- | -- | -- | -- | -- | TEST_HCTWO_HCTWO | .fits | _pp | RAW_TEST_HCTWO_HCTWO | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | TEST_FP_HCTWO | Preprocessed sci=FP calib=Hollow Cathode test file | -- | -- | -- | -- | -- | TEST_FP_HCTWO | .fits | _pp | RAW_TEST_FP_HCTWO | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | TEST_HCTWO_FP | Preprocessed sci=Hollow Cathode calib=FP test file | -- | -- | -- | -- | -- | TEST_HCTWO_FP | .fits | _pp | RAW_TEST_HCTWO_FP | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | TEST_DARK_DARK_SKY | Preprocessed sci=SKY calib=SKY test file | -- | -- | -- | -- | -- | TEST_DARK_DARK_SKY | .fits | _pp | RAW_TEST_EFF_SKY_SKY | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | TEST_DARK | Preprocessed sci=DARK calib=DARK test file | -- | -- | -- | -- | -- | TEST_DARK | .fits | _pp | RAW_TEST_DARK | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Pre-processed files | TEST_FP_DARK | Preprocessed sci=FP calib=DARK test file | -- | -- | -- | -- | -- | TEST_FP_DARK | .fits | _pp | RAW_TEST_FP_DARK | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | PP_REF | PP Reference flat calibration file | -- | -- | -- | -- | -- | -- | .fits | _ppref | RAW_FLAT_FLAT | PP_REF | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | PP_LED_FLAT | Reference LED flat calibration file | -- | -- | -- | -- | -- | -- | .fits | _led_flat | RAW_LED_LED | PP_LED_FLAT | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | DARKI | Internal dark calibration file | -- | -- | -- | -- | -- | -- | .fits | _darki | DARK_DARK | DARKI | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | DARKES | Eff Sky dark calibration file | -- | -- | -- | -- | -- | -- | .fits | _dark_es | EFF_SKY_SKY | DARKES | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | DARKNS | Night Sky dark calibration file | -- | -- | -- | -- | -- | -- | .fits | _dark_ns | NIGHT_SKY_SKY | DARKNS | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | DARKREF | Reference dark calibration file | -- | -- | -- | -- | -- | -- | .fits | _dark_ref | DARK_DARK | DARKREF | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | BADPIX | Bad pixel map | -- | -- | -- | -- | -- | -- | .fits | _badpixel | FLAT_FLAT | BADPIX | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | BKGRD_MAP | Bad pixel background map | -- | -- | -- | -- | -- | -- | .fits | _bmap.fits | FLAT_FLAT | BKGRD_MAP | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | DEBUG_BACK | Individual file background map | -- | -- | -- | -- | -- | -- | .fits | _background.fits | DRS_PP | DEBUG_BACK | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | LOC_LOCO | Localisation: combined order profile + position/width polynomial calibration file (all fibers) | -- | -- | -- | -- | -- | -- | .fits | _loco | FLAT_DARK, DARK_FLAT | LOC_LOCO | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | SHAPE_X | Reference shape dx calibration file | -- | -- | -- | -- | -- | -- | .fits | _shapex | FP_FP | SHAPE_X | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | SHAPE_Y | Reference shape dy calibration file | -- | -- | -- | -- | -- | -- | .fits | _shapey | FP_FP | SHAPE_Y | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | REF_FP | Reference shape master FP calibration file | -- | -- | -- | -- | -- | -- | .fits | _fpref | FP_FP | REF_FP | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | SHAPE_IN_FP | Input FP file for shape comparison | -- | -- | -- | -- | -- | -- | .fits | _shape_in_fp | FP_FP | SHAPE_IN_FP | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | SHAPE_OUT_FP | Output FP file for shape comparison | -- | -- | -- | -- | -- | -- | .fits | _shape_out_fp | FP_FP | SHAPE_OUT_FP | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | SHAPE_BDX | Shape transformed dx comparison file | -- | -- | -- | -- | -- | -- | .fits | _shape_out_bdx | FP_FP | SHAPE_BDX | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | SHAPEL | Nightly shape calibration files | -- | -- | -- | -- | -- | -- | .fits | _shapel | FP_FP | SHAPEL | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | SHAPEL_IN_FP | Input FP file for nightly shape comparison | -- | -- | -- | -- | -- | -- | .fits | _shapel_in_fp.fits | FP_FP | SHAPEL_IN_FP | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | SHAPEL_OUT_FP | Output FP file for nightly shape comparison | -- | -- | -- | -- | -- | -- | .fits | _shapel_out_fp.fits | FP_FP | SHAPEL_OUT_FP | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | FF_BLAZE | Blaze calibration file | -- | -- | -- | -- | -- | -- | .fits | _blaze | FLAT_FLAT | FF_BLAZE | -- | A, B | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | FF_FLAT | Flat calibration file | -- | -- | -- | -- | -- | -- | .fits | _flat | FLAT_FLAT | FF_FLAT | -- | A, B | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | ORDERP_STRAIGHT | Straightened order profile for an individual image | -- | -- | -- | -- | -- | -- | .fits | _orderps | SHAPEL | ORDERP_STRAIGHT | -- | A, B | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | EXT_E2DS_FF | Extracted + flat-fielded 2D spectrum | -- | -- | -- | -- | -- | -- | .fits | _e2dsff | DRS_PP | EXT_E2DS_FF | -- | A, B | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | FLAT_RESPONSE | Per-order flat-field response profile from the convolve_irregular resampling algorithm | -- | -- | -- | -- | -- | -- | .fits | _flat_response | EXT_E2DS_FF, EXT_E2DS_FF, QL_E2DS_FF, QL_E2DS_FF | FLAT_RESPONSE | -- | A, B | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | EXT_LOCO | Straightened localisation file | -- | -- | -- | -- | -- | -- | .fits | _e2dsloco | DRS_PP | EXT_LOCO | -- | A, B | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | EXT_S1D_W | 1D stitched spectrum (constant wavelength binning) | -- | -- | -- | -- | -- | -- | .fits | _s1d_w | DRS_PP | EXT_S1D_W | -- | A, B | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | EXT_S1D_V | 1D stitched spectrum (constant velocity binning) | -- | -- | -- | -- | -- | -- | .fits | _s1d_v | DRS_PP | EXT_S1D_V | -- | A, B | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | EXT_FPLIST | FP lines identified from extracted FP fiber | -- | -- | -- | -- | -- | -- | .fits | _ext_fplines | EXT_E2DS_FF, EXT_E2DS_FF | EXT_FPLIST | -- | A, B | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | LEAKREF_E2DS | Reference leak correction calibration file | -- | -- | -- | -- | -- | -- | .fits | _leak_ref | EXT_E2DS_FF, EXT_E2DS_FF | LEAKREF_E2DS | -- | A, B | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | WAVESOL_REF | Reference wavelength solution calibration file | -- | -- | -- | -- | -- | -- | .fits | _wavesol_ref | EXT_E2DS_FF, EXT_E2DS_FF | WAVESOL_REF | -- | A, B | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | WAVE_HCLIST_REF | Reference list of Hollow cathode lines calibration file | -- | -- | -- | -- | -- | -- | .fits | _waveref_hclines | EXT_E2DS_FF, EXT_E2DS_FF | WAVE_HCLIST_REF | -- | A, B | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | WAVE_FPLIST_REF | -- | -- | -- | -- | -- | -- | -- | .fits | _waveref_fplines | EXT_E2DS_FF, EXT_E2DS_FF | WAVE_FPLIST_REF | -- | A, B | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | WAVEREF_CAV | Reference wavelength cavity width polynomial calibration file | -- | -- | -- | -- | -- | -- | .fits | _waveref_cav_ | EXT_E2DS_FF, EXT_E2DS_FF | WAVEREF_CAV | -- | A | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | WAVESOL_DEFAULT | Default wavelength solution calibration file | -- | -- | -- | -- | -- | -- | .fits | _wave_d_ref | EXT_E2DS_FF, EXT_E2DS_FF | WAVESOL_DEFAULT | -- | A, B | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | WAVERES | Reference wavelength resolution map file | -- | -- | -- | -- | -- | -- | .fits | _waveref_resmap | EXT_E2DS_FF, EXT_E2DS_FF | WAVE_RES | -- | A, B | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | WAVE_FPRESTAB | Reference wavelength resolution table | -- | -- | -- | -- | -- | -- | .tbl | -- | EXT_E2DS_FF, EXT_E2DS_FF | -- | apero_wave_results | A, B | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | WAVE_FPLLTABL | Reference wavelength FP line-list table | -- | -- | -- | -- | -- | -- | .tbl | _mhc_lines | EXT_E2DS_FF, EXT_E2DS_FF | -- | -- | A, B | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | WAVEM_RES_E2DS | Reference wavelength resolution e2ds file | -- | -- | -- | -- | -- | -- | .fits | _waveref_res_e2ds | EXT_E2DS_FF, EXT_E2DS_FF | WAVEM_RES_E2DS | -- | A, B | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | WAVE_NIGHT | Nightly wavelength solution calibration file | -- | -- | -- | -- | -- | -- | .fits | _wave_night | EXT_E2DS_FF, EXT_E2DS_FF | WAVE_NIGHT | -- | A, B | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | WAVEHCLL | Nightly HC line list calibration file | -- | -- | -- | -- | -- | -- | .dat | _linelist | EXT_E2DS_FF, EXT_E2DS_FF | -- | -- | A, B | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | WAVERES | Nightly wavelength resolution map file | -- | -- | -- | -- | -- | -- | .fits | _wave_res | EXT_E2DS_FF, EXT_E2DS_FF | WAVE_RES | -- | A, B | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | WAVE_FPRESTAB | Nightly wavelength resolutiontable | -- | -- | -- | -- | -- | -- | .tbl | -- | EXT_E2DS_FF, EXT_E2DS_FF | -- | apero_wave_results | A, B | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | WAVE_FPLLTABL | Nightly wavelength FP line-list table | -- | -- | -- | -- | -- | -- | .tbl | _hc_lines | EXT_E2DS_FF, EXT_E2DS_FF | -- | -- | A, B | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | WAVE_HCLIST | Nightly wavelength Hollow cathodeline-list table | -- | -- | -- | -- | -- | -- | .fits | _wave_hclines | EXT_E2DS_FF, EXT_E2DS_FF | WAVE_HCLIST | -- | A, B | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | WAVE_FPLIST | Nightly wavelength FP line-list calibration file | -- | -- | -- | -- | -- | -- | .fits | _wave_fplines | EXT_E2DS_FF, EXT_E2DS_FF | WAVE_FPLIST | -- | A, B | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | SKY_MODEL | Telluric sky model file | -- | -- | -- | -- | -- | -- | .fits | _sky_model | EXT_E2DS_FF | SKY_MODEL | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | TELLU_SCLEAN | Sky-cleaning file | -- | -- | -- | -- | -- | -- | .fits | _tellu_sclean | EXT_E2DS_FF | TELLU_SCLEAN | -- | A | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | TELLU_PCLEAN | Telluric pre-cleaning file | -- | -- | -- | -- | -- | -- | .fits | _tellu_pclean | EXT_E2DS_FF | TELLU_PCLEAN | -- | A | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | TELLU_CONV | Telluric convolution file | -- | -- | -- | -- | -- | -- | .npy | _tellu_conv | WAVESOL_REF, WAVE_NIGHT, WAVESOL_DEFAULT | -- | -- | A | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | TELLU_TRANS | Telluric transmission file | -- | -- | -- | -- | -- | -- | .fits | _tellu_trans | EXT_E2DS_FF | TELLU_TRANS | -- | A | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | TELLU_TAPAS | Telluric TAPAS spline file | -- | -- | -- | -- | -- | -- | .npy | -- | -- | -- | tapas_spl.npy | -- | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | TRANS_MODEL | Telluric transmission model file | -- | -- | -- | -- | -- | -- | .fits | -- | -- | TRANS_MODEL | trans_model_{0} | A | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | ABSO_NPY | Telluric absorption temporary file 1 | -- | -- | -- | -- | -- | -- | .npy | -- | -- | -- | tellu_save.npy | -- | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | TELLU_OBJ | Telluric corrected extracted 2D spectrum | -- | -- | -- | -- | -- | -- | .fits | _e2dsff_tcorr | EXT_E2DS_FF | TELLU_OBJ | -- | A | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | SC1D_W_FILE | Telluric corrected extracted 1D spectrum (constant wavelength binning) | -- | -- | -- | -- | -- | -- | .fits | _s1d_w_tcorr | EXT_E2DS_FF | SC1D_W_FILE | -- | A | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | SC1D_V_FILE | Telluric corrected extracted 1D spectrum (constant velocity binning) | -- | -- | -- | -- | -- | -- | .fits | _s1d_v_tcorr | EXT_E2DS_FF | SC1D_V_FILE | -- | A | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | TELLU_RECON | Telluric reconstructed 2D absorption file | -- | -- | -- | -- | -- | -- | .fits | _e2dsff_recon | EXT_E2DS_FF | TELLU_RECON | -- | A | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | RC1D_W_FILE | Telluric reconstructed 1D absorption file (constant wavelength binning) | -- | -- | -- | -- | -- | -- | .fits | _s1d_w_recon | EXT_E2DS_FF | RC1D_W_FILE | -- | A | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | RC1D_V_FILE | Telluric reconstructed 1D absorption file (constant velocity binning) | -- | -- | -- | -- | -- | -- | .fits | _s1d_v_recon | EXT_E2DS_FF | RC1D_V_FILE | -- | A | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | TELLU_TEMP | Telluric 2D template file | -- | -- | -- | -- | -- | -- | .fits | -- | EXT_E2DS_FF, TELLU_OBJ | TELLU_TEMP | Template | A | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | TELLU_BIGCUBE | Telluric object 2D stack file (star frame) | -- | -- | -- | -- | -- | -- | .fits | -- | EXT_E2DS_FF, TELLU_OBJ | TELLU_BIGCUBE | BigCube | A | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | TELLU_BIGCUBE0 | Telluric object  2D stack file (Earth frame) | -- | -- | -- | -- | -- | -- | .fits | -- | EXT_E2DS_FF, TELLU_OBJ | TELLU_BIGCUBE0 | BigCube0 | A | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | TELLU_TEMP_S1DW | Telluric 1D template file | -- | -- | -- | -- | -- | -- | .fits | -- | EXT_E2DS_FF, TELLU_OBJ | TELLU_TEMP_S1DW | Template_s1dw | A | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | TELLU_TEMP_S1DV | Telluric 1D template file | -- | -- | -- | -- | -- | -- | .fits | -- | EXT_E2DS_FF, TELLU_OBJ | TELLU_TEMP_S1DV | Template_s1dv | A | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | TELLU_BIGCUBE_S1D | Telluric object 1D stack file (Earth frame) | -- | -- | -- | -- | -- | -- | .fits | -- | EXT_E2DS_FF, TELLU_OBJ | TELLU_BIGCUBE_S1D | BigCube_s1d | A | -- | -- | -- | -- | -- | -- | -- |
| Reduced files | CCF_RV | Cross-correlation RV results file | -- | -- | -- | -- | -- | -- | .fits | _ccf | EXT_E2DS_FF, TELLU_OBJ | CCF_RV | -- | A, B | -- | -- | -- | -- | -- | -- | -- |
| Calibration files | PP_REF | PP Reference flat calibration file | -- | -- | -- | -- | -- | -- | .fits | _ppref | RAW_FLAT_FLAT | PP_REF | -- | -- | calibration | PP_REF | -- | -- | -- | -- | -- |
| Calibration files | PP_LED_FLAT | Reference LED flat calibration file | -- | -- | -- | -- | -- | -- | .fits | _led_flat | RAW_LED_LED | PP_LED_FLAT | -- | -- | calibration | PP_LED | -- | -- | -- | -- | -- |
| Calibration files | DARKI | Internal dark calibration file | -- | -- | -- | -- | -- | -- | .fits | _darki | DARK_DARK | DARKI | -- | -- | calibration | DARKI | -- | -- | -- | -- | -- |
| Calibration files | DARKES | Eff Sky dark calibration file | -- | -- | -- | -- | -- | -- | .fits | _dark_es | EFF_SKY_SKY | DARKES | -- | -- | calibration | DARK_ES | -- | -- | -- | -- | -- |
| Calibration files | DARKNS | Night Sky dark calibration file | -- | -- | -- | -- | -- | -- | .fits | _dark_ns | NIGHT_SKY_SKY | DARKNS | -- | -- | calibration | DARK_NS | -- | -- | -- | -- | -- |
| Calibration files | DARKREF | Reference dark calibration file | -- | -- | -- | -- | -- | -- | .fits | _dark_ref | DARK_DARK | DARKREF | -- | -- | calibration | DARKREF | -- | -- | -- | -- | -- |
| Calibration files | BADPIX | Bad pixel map | -- | -- | -- | -- | -- | -- | .fits | _badpixel | FLAT_FLAT | BADPIX | -- | -- | calibration | BADPIX | -- | -- | -- | -- | -- |
| Calibration files | BKGRD_MAP | Bad pixel background map | -- | -- | -- | -- | -- | -- | .fits | _bmap.fits | FLAT_FLAT | BKGRD_MAP | -- | -- | calibration | BKGRDMAP | -- | -- | -- | -- | -- |
| Calibration files | LOC_LOCO | Localisation: combined order profile + position/width polynomial calibration file (all fibers) | -- | -- | -- | -- | -- | -- | .fits | _loco | FLAT_DARK, DARK_FLAT | LOC_LOCO | -- | -- | calibration | LOC | -- | -- | -- | -- | -- |
| Calibration files | SHAPE_X | Reference shape dx calibration file | -- | -- | -- | -- | -- | -- | .fits | _shapex | FP_FP | SHAPE_X | -- | -- | calibration | SHAPEX | -- | -- | -- | -- | -- |
| Calibration files | SHAPE_Y | Reference shape dy calibration file | -- | -- | -- | -- | -- | -- | .fits | _shapey | FP_FP | SHAPE_Y | -- | -- | calibration | SHAPEY | -- | -- | -- | -- | -- |
| Calibration files | REF_FP | Reference shape master FP calibration file | -- | -- | -- | -- | -- | -- | .fits | _fpref | FP_FP | REF_FP | -- | -- | calibration | FPREF | -- | -- | -- | -- | -- |
| Calibration files | SHAPEL | Nightly shape calibration files | -- | -- | -- | -- | -- | -- | .fits | _shapel | FP_FP | SHAPEL | -- | -- | calibration | SHAPEL | -- | -- | -- | -- | -- |
| Calibration files | FF_BLAZE | Blaze calibration file | -- | -- | -- | -- | -- | -- | .fits | _blaze | FLAT_FLAT | FF_BLAZE | -- | A, B | calibration | BLAZE | -- | -- | -- | -- | -- |
| Calibration files | FF_FLAT | Flat calibration file | -- | -- | -- | -- | -- | -- | .fits | _flat | FLAT_FLAT | FF_FLAT | -- | A, B | calibration | FLAT | -- | -- | -- | -- | -- |
| Calibration files | FLAT_RESPONSE | Per-order flat-field response profile from the convolve_irregular resampling algorithm | -- | -- | -- | -- | -- | -- | .fits | _flat_response | EXT_E2DS_FF, EXT_E2DS_FF, QL_E2DS_FF, QL_E2DS_FF | FLAT_RESPONSE | -- | A, B | calibration | FLAT_RES | -- | -- | -- | -- | -- |
| Calibration files | LEAKREF_E2DS | Reference leak correction calibration file | -- | -- | -- | -- | -- | -- | .fits | _leak_ref | EXT_E2DS_FF, EXT_E2DS_FF | LEAKREF_E2DS | -- | A, B | calibration | LEAKREF | -- | -- | -- | -- | -- |
| Calibration files | WAVESOL_REF | Reference wavelength solution calibration file | -- | -- | -- | -- | -- | -- | .fits | _wavesol_ref | EXT_E2DS_FF, EXT_E2DS_FF | WAVESOL_REF | -- | A, B | calibration | WAVESOL_REF | -- | -- | -- | -- | -- |
| Calibration files | WAVE_HCLIST_REF | Reference list of Hollow cathode lines calibration file | -- | -- | -- | -- | -- | -- | .fits | _waveref_hclines | EXT_E2DS_FF, EXT_E2DS_FF | WAVE_HCLIST_REF | -- | A, B | calibration | WAVEHCL | -- | -- | -- | -- | -- |
| Calibration files | WAVE_FPLIST_REF | -- | -- | -- | -- | -- | -- | -- | .fits | _waveref_fplines | EXT_E2DS_FF, EXT_E2DS_FF | WAVE_FPLIST_REF | -- | A, B | calibration | WAVEFPL | -- | -- | -- | -- | -- |
| Calibration files | WAVEREF_CAV | Reference wavelength cavity width polynomial calibration file | -- | -- | -- | -- | -- | -- | .fits | _waveref_cav_ | EXT_E2DS_FF, EXT_E2DS_FF | WAVEREF_CAV | -- | A | calibration | WAVECAV | -- | -- | -- | -- | -- |
| Calibration files | WAVESOL_DEFAULT | Default wavelength solution calibration file | -- | -- | -- | -- | -- | -- | .fits | _wave_d_ref | EXT_E2DS_FF, EXT_E2DS_FF | WAVESOL_DEFAULT | -- | A, B | calibration | WAVESOL_DEFAULT | -- | -- | -- | -- | -- |
| Calibration files | WAVEM_RES_E2DS | Reference wavelength resolution e2ds file | -- | -- | -- | -- | -- | -- | .fits | _waveref_res_e2ds | EXT_E2DS_FF, EXT_E2DS_FF | WAVEM_RES_E2DS | -- | A, B | calibration | WAVR_E2DS | -- | -- | -- | -- | -- |
| Calibration files | WAVE_NIGHT | Nightly wavelength solution calibration file | -- | -- | -- | -- | -- | -- | .fits | _wave_night | EXT_E2DS_FF, EXT_E2DS_FF | WAVE_NIGHT | -- | A, B | calibration | WAVE | -- | -- | -- | -- | -- |
| Telluric files | SKY_MODEL | Telluric sky model file | -- | -- | -- | -- | -- | -- | .fits | _sky_model | EXT_E2DS_FF | SKY_MODEL | -- | -- | telluric | SKY_MODEL | -- | -- | -- | -- | -- |
| Telluric files | TELLU_SCLEAN | Sky-cleaning file | -- | -- | -- | -- | -- | -- | .fits | _tellu_sclean | EXT_E2DS_FF | TELLU_SCLEAN | -- | A | -- | -- | -- | -- | -- | -- | -- |
| Telluric files | TELLU_PCLEAN | Telluric pre-cleaning file | -- | -- | -- | -- | -- | -- | .fits | _tellu_pclean | EXT_E2DS_FF | TELLU_PCLEAN | -- | A | telluric | TELLU_PCLEAN | -- | -- | -- | -- | -- |
| Telluric files | TELLU_CONV | Telluric convolution file | -- | -- | -- | -- | -- | -- | .npy | _tellu_conv | WAVESOL_REF, WAVE_NIGHT, WAVESOL_DEFAULT | -- | -- | A | telluric | TELLU_CONV | -- | -- | -- | -- | -- |
| Telluric files | TELLU_TRANS | Telluric transmission file | -- | -- | -- | -- | -- | -- | .fits | _tellu_trans | EXT_E2DS_FF | TELLU_TRANS | -- | A | telluric | TELLU_TRANS | -- | -- | -- | -- | -- |
| Telluric files | TELLU_TAPAS | Telluric TAPAS spline file | -- | -- | -- | -- | -- | -- | .npy | -- | -- | -- | tapas_spl.npy | -- | telluric | TELLU_TAPAS | -- | -- | -- | -- | -- |
| Telluric files | TRANS_MODEL | Telluric transmission model file | -- | -- | -- | -- | -- | -- | .fits | -- | -- | TRANS_MODEL | trans_model_{0} | A | telluric | TELLU_MODEL | -- | -- | -- | -- | -- |
| Telluric files | TELLU_OBJ | Telluric corrected extracted 2D spectrum | -- | -- | -- | -- | -- | -- | .fits | _e2dsff_tcorr | EXT_E2DS_FF | TELLU_OBJ | -- | A | telluric | TELLU_OBJ | -- | -- | -- | -- | -- |
| Telluric files | TELLU_RECON | Telluric reconstructed 2D absorption file | -- | -- | -- | -- | -- | -- | .fits | _e2dsff_recon | EXT_E2DS_FF | TELLU_RECON | -- | A | telluric | TELLU_RECON | -- | -- | -- | -- | -- |
| Telluric files | TELLU_TEMP | Telluric 2D template file | -- | -- | -- | -- | -- | -- | .fits | -- | EXT_E2DS_FF, TELLU_OBJ | TELLU_TEMP | Template | A | telluric | TELLU_TEMP | -- | -- | -- | -- | -- |
| Telluric files | TELLU_TEMP_S1DW | Telluric 1D template file | -- | -- | -- | -- | -- | -- | .fits | -- | EXT_E2DS_FF, TELLU_OBJ | TELLU_TEMP_S1DW | Template_s1dw | A | telluric | TELLU_TEMP_S1DW | -- | -- | -- | -- | -- |
| Telluric files | TELLU_TEMP_S1DV | Telluric 1D template file | -- | -- | -- | -- | -- | -- | .fits | -- | EXT_E2DS_FF, TELLU_OBJ | TELLU_TEMP_S1DV | Template_s1dv | A | telluric | TELLU_TEMP_S1DV | -- | -- | -- | -- | -- |
| Post-processed files | DRS_POST_E | Post process 2D extracted spectrum collection | -- | -- | -- | -- | -- | -- | -- | e.fits | -- | -- | -- | -- | -- | -- | OBJ_FP \|br\| OBJ_DARK \|br\| POLAR_FP \|br\| POLAR_DARK | \|br\| Primary: PP \|br\| FluxA \|br\| FluxB \|br\| WaveA \|br\| WaveB \|br\| BlazeA \|br\| BlazeB | \|br\| DRS_PP \|br\| EXT_E2DS_FF \|br\| EXT_E2DS_FF \|br\| WAVE_FILES \|br\| WAVE_FILES \|br\| FF_BLAZE \|br\| FF_BLAZE | \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- | \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- |
| Post-processed files | DRS_POST_S | Post process 1D spectrum collection | -- | -- | -- | -- | -- | -- | -- | s.fits | -- | -- | -- | -- | -- | -- | OBJ_FP \|br\| OBJ_DARK \|br\| POLAR_FP \|br\| POLAR_DARK | \|br\| Primary: PP \|br\| UniformWavelength \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| UniformVelocity \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- | \|br\| DRS_PP \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- | \|br\| -- \|br\| Wave \|br\| FluxA \|br\| FluxErrA \|br\| FluxB \|br\| FluxErrB \|br\| FluxATelluCorrected \|br\| FluxErrATelluCorrected \|br\| Recon \|br\| ReconErr \|br\| SkyCorr \|br\| SkyCorrErr \|br\| FiniteRes \|br\| FiniteResErr \|br\| Recon \|br\| ReconErr \|br\| Wave \|br\| FluxA \|br\| FluxErrA \|br\| FluxB \|br\| FluxErrB \|br\| FluxATelluCorrected \|br\| FluxErrATelluCorrected \|br\| SkyCorr \|br\| SkyCorrErr \|br\| FiniteRes \|br\| FiniteResErr | \|br\| -- \|br\| EXT_S1D_W \|br\| EXT_S1D_W \|br\| EXT_S1D_W \|br\| EXT_S1D_W \|br\| EXT_S1D_W \|br\| SC1D_W_FILE \|br\| SC1D_W_FILE \|br\| RC1D_W_FILE \|br\| RC1D_W_FILE \|br\| RC1D_W_FILE \|br\| RC1D_W_FILE \|br\| RC1D_W_FILE \|br\| RC1D_W_FILE \|br\| RC1D_V_FILE \|br\| RC1D_V_FILE \|br\| EXT_S1D_V \|br\| EXT_S1D_V \|br\| EXT_S1D_V \|br\| EXT_S1D_V \|br\| EXT_S1D_V \|br\| SC1D_V_FILE \|br\| SC1D_V_FILE \|br\| RC1D_V_FILE \|br\| RC1D_V_FILE \|br\| RC1D_V_FILE \|br\| RC1D_V_FILE |
| Post-processed files | DRS_POST_T | Post process 2D telluric corrected collection | -- | -- | -- | -- | -- | -- | -- | t.fits | -- | -- | -- | -- | -- | -- | OBJ_FP \|br\| OBJ_DARK \|br\| POLAR_FP \|br\| POLAR_DARK | \|br\| Primary: PP \|br\| FluxA \|br\| WaveA \|br\| BlazeA \|br\| Recon \|br\| SKYCORR_SCI \|br\| SKYCORR_CAL | \|br\| DRS_PP \|br\| TELLU_OBJ \|br\| WAVE_FILES \|br\| FF_BLAZE \|br\| TELLU_RECON \|br\| TELLU_PCLEAN \|br\| TELLU_PCLEAN | \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- | \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- \|br\| -- |
| Post-processed files | DRS_POST_V | Post process radial velocity collection | -- | -- | -- | -- | -- | -- | -- | v.fits | -- | -- | -- | -- | -- | -- | OBJ_FP \|br\| OBJ_DARK \|br\| POLAR_FP \|br\| POLAR_DARK | \|br\| Primary: PP \|br\| CCF | \|br\| DRS_PP \|br\| CCF_RV | \|br\| -- \|br\| -- | \|br\| -- \|br\| -- |
