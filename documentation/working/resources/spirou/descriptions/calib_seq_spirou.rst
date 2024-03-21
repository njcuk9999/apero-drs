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