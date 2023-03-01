=========================================
Nightly wavelength solution calibration
=========================================

Considering that the wavelength solution is central in the anchoring of PRV measurement and that the instrument will
drift through time, one needs to obtain a wavelength solution as close as possible in time to the science exposures,
ideally on a nightly basis. The nightly wavelength solution captures sub-:math:`\mu m` level motions within the
optical train and high-order changes in the focal plane that are not captured by the affine transform used to
register frames as described in sections \ref{subsec:ref_shape} and \ref{subsec:night_shape}. The nightly wavelength
solution recipe takes preprocessed `FP_FP` files and `HC_HC` files (as many as given by the user or as many as occur on
each of the nights being used via `apero_processing`). It combines the `FP_FP` and  `HC_HC` files into a single`FP_FP`
and a single `HC_HC` file (via a median combination of the images). These combined `FP_FP` and `HC_HC` files are then
extracted.

The rest of the process is similar to the reference wavelength solution. The wavelength solution is determined as
follows:

    - Under the assumption that the reference wavelength solution is correct at the pixel level, identify HC lines
      (catalog wavelength) and FP peaks (FP order).
    - By combining the reference chromatic FP cavity length and position of FP peaks of known FP order,  fit a
      per-order wavelength solution.
    - Using that wavelength solution, measure the velocity offset in the position of HC lines
      (:math:`\Delta v_{\rm HC}`) and derive an achromatic increment to be applied to the FP cavity
    - Scale the 0th order term of the Nth order cavity polynomial by :math:`1-\frac{\Delta v_{\rm HC}}{c}`, where c
      is the speed of light in the units of :math:`\Delta v_{\rm HC}`.
    - Iterate the last two steps until :math:`\Delta v_{\rm HC}` is consistent with zero.

The main difference with the reference wavelength solution for fiber AB is that while we start the calculation of the
wavelength solution with the cavity fit and wavelength solution from the reference wavelength solution calibration,
we only allow for changes in the achromatic term. This is because the chromatic dependence of the cavity width is
related to the coating of the FP etalon, and is therefore not expected to change rapidly. An achromatic shift, on the
other hand, corresponds to a change in the cavity length of the FP, due in part to pressure or temperature variations,
which may happen between nights. Meanwhile, for fibers A, B, and C we fit nothing and use the fiber AB wavelength
cavity coefficients. The FP mask for quality control is also not re-generated. Therefore all cross-correlations
between fibers AB and A, B, and C are done relative to the reference night wavelength solution (however we only check
quality control on AB-A, AB-B, and AB-C). As with the reference wavelength solution recipe, a wavelength
solution for each fiber, and the FP and HC lines founds during the process, are then saved to the calibration database
for use throughout APERO.