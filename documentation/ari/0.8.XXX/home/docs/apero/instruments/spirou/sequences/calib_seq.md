---
card_label: calib_seq
card_icon: fa-solid fa-diagram-project
related:
  - apero/instruments/spirou
  - apero/instruments/spirou/recipes/
  - apero/instruments/spirou/file_definitions/
  - glossary
---

# calib_seq

**Instrument:** SPIROU

Run all nightly calibration steps.

This should be run after preprocessing of (at least) calibrations for all nights being reduced.
This should also be run after all reference calibration steps have been done.

Include the following recipes:

    - BAD: bad pixel calibration files for every night
    - LOCCAL: localisation file for calibration fiber for every night
    - LOCSCI: localisation file for science fiber for every night
    - SHAPEL: local shape file for every night
    - FLAT: flat calibration for every night
    - THERM_I: thermal calibration for every night (internal dark)
    - WAVEREF: wavelength calibration for every night
    - THERM_T: thermal calibration for every night (telescope dark)

## Recipes in this sequence

| ORDER | RECIPE | SHORTNAME | RECIPE KIND | REF RECIPE | ARGS |
| --- | --- | --- | --- | --- | --- |
| 1 | apero_badpix_spirou.py | BAD | calib-night | No |  |
| 2 | apero_loc_spirou.py | LOC | calib-night | No | {files}=[DARK_FLAT, FLAT_DARK] |
| 3 | apero_shape_spirou.py | SHAPE | calib-night | No |  |
| 4 | apero_flat_spirou.py | FF | calib-night | No | {files}=[FLAT_FLAT, DARK_FLAT, FLAT_DARK] |
| 5 | apero_thermal_spirou.py | THERM_I | calib-night-I | No | {files}=[DARK_DARK_INT] |
| 6 | apero_wave_night_spirou.py | WAVE | calib-night | No |  |
| 7 | apero_thermal_spirou.py | THERM_T | calib-night-T | No | {files}=[DARK_DARK_TEL] |
