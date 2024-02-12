==================================
Shape reference calibration
==================================

In PRV measurements, constraining the exact position of orders on the science array, both in the spectral and
spatial dimensions, is key as the position of our spectra on this science array encodes the sought-after velocity of
the star. The diffraction orders of SPIRou, and nearly all PRV spectrographs, follow curved lines, and the image
slicer has a 4-point structure that is not parallel to the pixel grid.

Within the APERO framework, we decided to split the problem into two parts: a reference shape calibration and a
nightly shape calibration. For the reference step, we constrain the bulk motion, as defined through an affine
transformation and register all frames to a common pixel grid to well below the equivalent of 1 :math:`ms^{-1}`.
We perform the order localization and subsequent steps on a nightly basis as it has the significant advantage that
registered frames have all orders at the same position to a very small fraction of a pixel. Furthermore, having
registered frames allows for better error handling within APERO; one does not expect pixel-level motions between
calibrations after this step.

The reference shape recipe takes preprocessed `FP_FP` and `HC_HC` files (as many as given by the user or as many as
occur on the nights being used via `apero_processing`). The reference shape recipe combines the `FP_FP` files into a
single `FP_FP` file and the `HC_HC` files into a single `HC_HC` file (via a median combination of the images).
After combining, the `FP_FP` and `HC_HC` images are calibrated using our standard image calibration technique.
In addition to the combined `FP_FP` and `HC_HC`, we create a reference FP image. This reference FP image is created
by selecting a subset of 100 `FP_FP` files (uniformly distributed across nights) and combining these with a median.
This reference FP image is then saved to the calibration database for use throughout APERO.

The registration through affine transformations is done using the`FP_FP` calibrations. We take the combined `FP_FP`
files and localize in the 2D frame the position of each FP peak and measure the position of the peak maxima.
Considering the 3 SPIRou fibers and 4 slices (i.e., 12 2D peaks per FP line), this means there are >100000 peaks on
the science array. These are taken as reference positions. For each calibration sequence, we then find the affine
transformation that minimizes the RMS between the position of the FP and the FP reference image calibration.
The resulting affine transformation consists of a bulk shift in dx, dy, and a :math:`2\times2` matrix that encodes
rotation, scale, and shear. These values are kept and can be useful to identify shifts in the optics (e.g., after
earthquakes or thermal cycles) as well as very slight changes in plate scale and angular position of the array which
can be of interest in understanding the impact of engineering work onto the science data products.
For example, we can readily measure a :math:`10^{-5}` fractional change in the SPIRou plate scale following a
maintenance thermal cycle of the instrument; the ratio of the point-to-point RMS to the median of the plate scale
value is at the :math:`1.7\times10^{-7}` level. The interpolations between pixel grids are done with a 3rd
order spline.  We note that changes in the FP cavity length arise from a number of reasons such as gas leakage and
temperature and will lead to a motion of FP peaks on the array that is not due to a physical motion of the array or
optical elements within the cryostat. Considering that typical drifts are at the :math:`\sim0.3`\,m/s/day level,
to first order this leads to a typical :math:`10^{-9}`/day fractional increase in the plate scale along the dispersion
direction. This effectively leads to a minute change in the effective dispersion of the extracted file wavelength
solution. As this change is common to both the FP, the HC, and the science data, it is accounted for when computing
the wavelength solution and cavity length change.

Once the affine transformation has been applied, images are registered to a common grid (the reference FP image).
We then construct a transform that makes the orders straight and corrects for slicer structure in the dispersion
direction. This leads to the construction of two maps corresponding to x and y offsets that need to be applied to an
image to transform it into a rectified image from which a trace extraction can be performed directly through a 1-D
collapse in the direction perpendicular to the dispersion of a rectangular box around the order. The y direction map
is computed from the order-localization polynomials. The x direction map is determined by first collapsing the
straightened orders of a `FP_FP` calibration and cross-correlating each of the spectral direction pixel rows to find
its offset relative to the collapsed-extracted spectrum. The x and y offsets are then saved to the calibration
database for use throughout APERO.
