==================================
Thermal calibration
==================================

The nightly thermal recipe takes preprocessed `DARK_DARK_INT` files or `DARK_DARK_TEL` files (as many as given by
the user or as many as occur on each of the nights being used via `apero_processing`). It combines the `DARK_DARK_INT`
or `DARK_DARK_TEL` files into a single `DARK_DARK_INT` or `DARK_DARK_TEL` respectively (via a median combination of
the images). These combined `DARK_DARK_INT` or `DARK_DARK_TEL` files are then extracted.

The thermal background seen by SPIRou in a science exposure is the sum of the black body contribution of the sky, the
Cassegrain unit (at the temperature of the telescope), the calibration unit (for the reference channel), and the
thermal emission of the hermetic feedthroughs that connect the fibers into the cryostat. A small contribution also
arises from the Earth's atmosphere itself. This emissivity is proportional to one minus the telluric transmission at
the corresponding wavelength and if left unaccounted for in the thermal model would lead to emission-like features in
the thermal-corrected spectrum in the strongest absorption lines. From a series of sky-dark frames, we measured that
the median additional emissivity from the saturated absorption line is at the 4% level of the black body envelope.
We account for the additional contribution by using a median sky absorption spectrum and adding a small contribution
proportional to the excess emissivity due to the Earth's atmosphere in strong absorption lines. Note this contribution
is only added for the `DARK_DARK_TEL` files (as the `DARK_DARK_INT` images do not see the sky). For this reason, we
split generating the thermal calibration files into two steps: we generate the `DARK_DARK_INT` thermal calibration
files, then after a wavelength solution has been generated we generate the `DARK_DARK_TEL` thermal calibration files
(which require a nightly wavelength solution to add the contribution due to the emission-like features).

Considering that the telescope and front-end temperature change through the night, one needs to apply a thermal
correction that is adjusted per frame (this is done as part of the extraction recipe). While the slope of the black
body contribution changes very little over the :math:`2.1-2.5 \mu m` domain, within which the thermal background is
significant, the amplitude of the contribution varies by a factor of >2 between nights (typically a factor 2 for
every :math:`8^\circ`C) and needs to be adjusted for individual observations. While we have no external measurement of
the thermal background, there are a number of completely saturated telluric water absorption features
:math:`2.4-2.5 \mu m` that provide a measure of the total thermal emission seen by SPIRou. These regions are used to
scale the thermal background model such that they have a median flux of zero.

The thermal calibration files (`THERMALI` and `THERMALT`) are then saved to the calibration database for use
throughout APERO. The `THERMALI` calibrations are used for correcting internal lamp spectra (i.e., other calibrations)
and `THERMALT` calibrations are used to correct all science spectra.