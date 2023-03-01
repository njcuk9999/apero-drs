================================
Flat and Blaze calibration
================================

An essential part of the extraction process is calibrating the flat field response (removing the effect of the
pixel-to-pixel sensitivity variations) and calculating the blaze function. The blaze can be seen visually in the raw
and preprocessed images as a darkening of the orders, especially at the blue end, towards the sides of the detector
(in the along-order direction).

The nightly flat recipe takes preprocessed `FLAT_FLAT` files (as many as given by the user or as many as occur on
each night being used via `apero_processing`). It combines the `FLAT_FLAT` files into a single `FLAT_FLAT` per night
(via a median combination of the images). After combining, the `FLAT_FLAT` images are calibrated using our standard
image calibration technique. The combined, calibrated `FLAT_FLAT` file is then extracted (using the same extraction
algorithms presented in Section \ref{sec:extraction}). The rest of the flat and blaze recipe is handled per order.
Once extracted, the `E2DS` (:math:`49\times4088`) is median filtered (with a width of 25 pixels) and all pixels with
flux less than 0.05 the 95th percentile flux value or greater than 2 times the 95th percentile flux value are
removed. Each `FLAT_FLAT` `E2DS` order is then fit with a sinc function:

.. math::
        \text{B}_i = AS(sin(\theta)/\theta)^2

.. math::
        S = 1 + s(x_i - L)

.. math::
        \theta = \pi \bar{x_i} / P

.. math::
        \bar{x_i} = (x_i - L) + Q(x_i - L)^2 + C(x_i - L)^3


where :math:`\text{B}_i` is the blaze model for the ith `E2DS` order, A is the amplitude of the sinc function, P is
the period of the sinc function, s is the slope of the sinc function, :math:`x_i` is the flux vector of the `E2DS`
order, L is the linear center of the sinc function, Q is a quadratic scale term, and C is a cubic scale term.
The terms fit in the sinc function are A, P, L, Q, C and s as a function of :math:`x_i`.

Once we have a set of parameters the blaze function for this order is :math:`\text{B}_i` for all values of the flux
for this order. The original `E2DS` order is then divided by the blaze function and this is used as the flat profile.
A standard deviation of the flat is also calculated for quality control purposes. This process is repeated for each
order producing a full blaze and flat profile (:math:`49\times4088`) for the input `FLAT_FLAT` files. To avoid
erroneous contributions to the flat any outlier pixels (outside 10:math:`\sigma` or within :math:`\pm`0.2 of unity)
are set to NaN. Note that the multiplication of the blaze and the flat is equivalent to the full response function of
the detector. For some orders (#34 and #74), there is a large residual at one edge of the blaze falloff.
This is due to the mismatch between the analytical function used and the actual profile; the flat-field correction
accounts for this mismatch.

For quality control, we check that the standard deviation of the flat for each order is less than 0.05. The flat
(`FLAT`) and blaze (`BLAZE`) profiles are then saved to the calibration database (if the quality control criteria are
met) for use throughout APERO.