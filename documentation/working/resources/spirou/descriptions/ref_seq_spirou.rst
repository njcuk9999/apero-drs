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