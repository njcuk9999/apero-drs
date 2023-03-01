==================================
Extraction
==================================

The extraction recipe takes any preprocessed file (as many as given by the user but in general just one single file).
The files are combined (if requested) and are calibrated using our standard image calibration technique. Once
calibrated, the correct (closest in time) order profile (`ORDERP`), positions of the orders (`LOCO`), `SHAPELOCAL`,
shape reference (x and y maps), and wavelength solution are loaded for each fiber (AB, A, B, and C). The order profiles
and input image are transformed to the reference FP grid using the affine transformation, and using the shape x and y
maps the image is corrected for the slicer geometry, the tilt and the bending due to the echelle orders.

The extraction recipe then extracts the flux (using optimal extraction), calculates the barycentric correction,
corrects contamination from the reference fiber (if an FP is present in the reference fiber), corrects for the flat,
corrects for the thermal contribution and generates the 1D spectrum.


Optimal extraction
----------------------------------

Once the image and the order profile (from localization) have been corrected for the slicer geometry and curvature of
the echelle orders we extract out the combined flux in the science channels (fibers A and B) to create a fiber AB,
as well as extracting out the flux in A and B (for polarization work) and C separately (for the reference fiber
calibrations). As the orders are already straightened we use just the localization coefficient value at the center of
the image to extract vertically along each order. We then divide the image by the order profile to provide a weighting
across the order (i.e., an optimal extraction, Horne et al. 1986}). The final step of the optimal extraction is to sum
vertically across the columns accounting for cosmic rays by using a sigma clip :math:`|flux|>10\sigma` away from the
median value for that column. This creates our `E2DS` (extracted 2D spectrum) and for SPIRou, this leads to images
with 49 orders and 4088 pixels along the orders.


BERV correction
----------------------------------

Ideally, any stellar spectrum observed would be measured from a point stationary with respect to the barycenter of the
Solar System (Wright et al. 2014). However, ground-based observations are subject to: the orbit of the Earth, the
rotation of the Earth, precession and other Earth motions, and to a lesser extent gravitation time dilation,
leap-second offsets, and factors affecting the star itself (i.e., parallax, proper motions, etc). We use the term BERV
(Barycentric Earth Radial Velocity) hereinafter to collect all these terms into a single measurement which can be used
to correct a specific spectrum at a specific point in time. We calculate the BERV using the barycorrpy package, which
uses the astrometric parameters fed in at the preprocessing level. The calculation from barycorrpy includes the
estimate for the BERV itself and the corrected or barycentric Julian Date (BJD) at the mid-exposure time. barycorrpy
has a precision better than the :math:`cm s^{-1}` level. We also estimate the maximum BERV value for this object
across the year. If for any reason the BERV calculation fails with barycorrpy we calculate an estimate of the BERV
(precise to :math:`\sim`10:math:`m s^{-1}`, modified from PyAstronomy.pyasl.baryvel; a python implementation of helcorr)
and flag that an estimated BERV correction was calculated. This estimated BERV is not precise enough for PRV work but
is sufficient to allow for acceptable telluric correction.


Leak Correction
----------------------------------

For scientific observations, the reference fiber either has a DARK or an FP illuminating the pixels in this fiber.
For PRV an FP allows a simultaneous RV measurement of an FP alongside the measurement of the stellar RV; this allows
precise tracking of the instrumental drift when the simultaneous FP is compared to the `FP_FP` from the nightly
wavelength solution calibration. However, light from the FP has been shown to slightly contaminate the science fibers
and thus we provide a correction for such calibration.

During the reference sequence  many `DARK_FP` are combined (and extracted) to form a model of the light seen in the
science fibers when no light (other than the contribution from the DARK) was present as well as an extracted reference
fiber measurement of the FP flux that caused said contamination in the science fibers. Using these models, the
contamination measured in the science channels of the reference leak recipe is then scaled to the flux of the
simultaneous FP of the observation (using the extracted flux from this scientific observation we are trying to correct).
Then, this model is subtracted from the original science observation for each of the science fibers (AB or A or B),
order-by-order:

.. math::

     \begin{array}{cc}
        ratio_{i} = \frac{\Sigma(L[C]_{i}S[C]_{i})}{\Sigma(S[C]_{i}^2)} \\
        \\
        scale_{i} = \frac{L[AB,A,B]_{i}}{ratio_{i}} \\
        \\
        S[AB,A,B]_{i,corr} = S[AB,A,B]_{i} - scale_{i} \\

    \end{array}

where L[C] is the model of the FP from the leak reference recipe, S[C] is the 2D extracted spectrum in the reference
fiber (fiber C), L[AB,A,B] is the model of the contamination from the FP from the leak reference recipe in the science
fibers (either AB or A or B), S[AB,A,B] is the 2D extracted flux in the science fibers (either AB or A or B),
S[AB,A,B]_{corr} denotes the leak-corrected 2D extracted spectrum in the science fibers (either AB or A or B) and
i denotes that this is done order-by-order.


Thermal correction
----------------------------------

The reference dark, applied during the standard image calibration phase, removes the high-frequency components of the
dark; however, the thermal contribution still remains (and varies on a night-by-night basis). For this reason, we use
nightly extracted `DARK_DARK` files to model the thermal contribution present in an observation during the night.
The thermal correction model comes in two flavors, one for science observations where we assume there is some sort of
continuum to the spectrum and telluric contamination as well as a small contribution arising from the Earth's
atmosphere itself, and one for HC or FP extractions where these assumptions are not true.

In the case where we have a scientific observation, a `DARK_DARK_TEL` (where the calibration fiber sees the cold source
and the science fibers see the mirror covers) is used. The extracted `DARK_DARK_TEL`  is then median filtered with a
width of 101 pixels (on a per-order basis). This width was chosen to be big enough to capture large-scale structures
in the dark and not be significantly affected by readout noise. A fit is then made to the red most orders
(:math:`>2450 nm`) using only flux lower than 0.01 from a transmission spectrum from the Transmissions of the
AtmosPhere for AStromomical data tool (TAPAS) -- i.e., a domain where transmission is basically zero. We assume that
we can safely use any flux with a transmission of order zero to scale the thermal background to this zero transmission
value.

.. math::

        mask = \left\{ \begin{array}{cl}
        1: & TAPAS < 0.01  \\
        0: & \text{otherwise} \\
        \end{array} \right. \\
        \\
        ratio = median\left( \frac{TT[AB,A,B,C]\times mask}{S[AB,A,B,C] \times mask} \right) \\
        \\
        S[AB,A,B,C]_{corr} = S[AB,A,B,C] - \frac{TT[AB,A,B,C]}{ratio} \\
        \end{array}

where TAPAS is the TAPAS spectrum, TT[AB,A,B,C] is a nightly extracted `DARK_DARK_TEL` spectrum, S[AB,A,B,C] denotes
the 2D extracted spectrum prior to correction and :math:`S[AB,A,B]_{corr}` denotes the thermally corrected 2D extracted
spectrum.

In the case where we have an HC or an FP observation, a `DARK_DARK_INT` (where all three fibers see only the cold source,
not the sky nor the mirror covers) is used. The extracted `DARK_DARK_INT` is then median filtered (again with a width
of 101 pixels on a per-order basis) and a fit is made using an envelope to measure the thermal background in the
reddest orders (:math:`>2450\, nm`). The envelope is constructed by using the flux below the 10th percentile (i.e.,
not in the HC or FP peaks). This is then converted into a ratio and scaled to the observation we are correcting.


.. math::

    \begin{array}{cc}
        ratio = median\left( \frac{TI[AB,A,B,C]}{P_{10}(TI[AB,A,B,C])} \right) \\
        \\
        S[AB,A,B,C]_{corr} = S[AB,A,B,C] - \frac{TI[AB,A,B,C]}{ratio} \\
    \end{array}

where :math:`P_{10}` is the 10th percentile value, TI[AB,A,B,C] is a nightly extracted `DARK_DARK_INT` spectrum
(median filtered with a width of 101 pixels), S[AB,A,B,C] denotes the 2D extracted spectrum prior to correction and
:math:`S[AB,A,B]_{corr}` denotes the thermally corrected 2D extracted spectrum.


S1D generation
----------------------------------

The `E2DS` and `E2DSFF` formats are not necessarily the most convenient for science analysis, having duplicated
wavelength coverage at order overlap and slightly varying velocity sampling with each order and between orders.
We therefore transform the `E2DSFF` file into the `S1D` format. The `S1D` is sampled on a constant grid for all
objects. We have two differing `S1D` formats, one with a uniform step in wavelength (0.05 nm/pixel) and one with a
constant step in velocity (1 :math:`km s^{-1}`/pixel), both being sampled between 965 nm and 2500 nm. Numerically,
to construct the `S1D`, we use as an input the `E2DSFF` file prior to blaze correction and the blaze file as inputs.
We create two `S1D` vectors, one corresponding to the total flux and one corresponding to the total blaze on the
destination wavelength grid. We use a 5th order polynomial spline to project the flux of a given order onto the flux
grid and perform the same operation with the blaze onto the weight vector. We do not consider the blaze below 20% of
the peak blaze value and values on the destination wavelength grids that are out of the order's range are set to zero.
We loop through orders and sum the contribution of each order onto the respective destination grids for the `E2DSFF`
science flux and blaze. Note that the `S1D` generation only depends on the blaze calibration. As such any spectrum
(regardless of emission lines, low flux, or strong bands) can be converted to `S1D` format and we generate `S1D` for
`HC_HC` and `FP_FP` as well as science targets.