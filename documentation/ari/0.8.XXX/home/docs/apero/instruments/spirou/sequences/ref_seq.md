---
card_label: ref_seq
card_icon: fa-solid fa-diagram-project
related:
  - apero/instruments/spirou
  - apero/instruments/spirou/recipes/
  - apero/instruments/spirou/file_definitions/
  - glossary
---

# ref_seq

**Instrument:** SPIROU

Run all reference calibration steps.

This should be run after preprocessing of (at least) calibrations for all nights
that are required to be used as part of the reference calibrations.

Include the following recipes:

    - DARKREF: dark reference calibration (using all DARKs)
    - BADREF: bad pixel calibration files for the reference night
    - LOCREFCAL: localisation reference file for calibration fiber
    - LOCREFSCI: localisation reference file for science fiber
    - SHAPEREF: shape reference file
    - SHAPELREF: local shape reference file for the reference night
    - FLATREF: flat calibration for the reference night
    - THERM_REFI: thermal calibration for the reference night (internal dark)
    - LEAKREF: leak correction calibration for the reference night
    - WAVEREF: reference wavelength calibration
    - THERM_REFT: thermal calibration for the reference night (telescope dark)

## Recipes in this sequence

| ORDER | RECIPE | SHORTNAME | RECIPE KIND | REF RECIPE | ARGS | KWARGS |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | apero_dark_ref_spirou.py | DARKREF | calib-reference | Yes |  |  |
| 2 | apero_badpix_spirou.py | BADREF | calib-reference | Yes |  |  |
| 3 | apero_loc_spirou.py | LOCREF | calib-reference | Yes | {files}=[DARK_FLAT, FLAT_DARK] |  |
| 4 | apero_shape_ref_spirou.py | SHAPEREF | calib-reference | Yes |  |  |
| 5 | apero_shape_spirou.py | SHAPELREF | calib-reference | Yes |  |  |
| 6 | apero_flat_spirou.py | FLATREF | calib-reference | Yes |  |  |
| 7 | apero_thermal_spirou.py | THERM_REFI | calib-reference-I | Yes | {files}=[DARK_DARK_INT] |  |
| 8 | apero_leak_ref_spirou.py | LEAKREF | calib-reference | Yes |  |  |
| 9 | apero_wave_ref_spirou.py | WAVEREF | calib-reference | Yes |  | --hcfiles=[HCONE_HCONE] \|br\| --fpfiles=[FP_FP] |
| 10 | apero_thermal_spirou.py | THERM_REFT | calib-reference-T | Yes | {files}=[DARK_DARK_TEL] |  |
