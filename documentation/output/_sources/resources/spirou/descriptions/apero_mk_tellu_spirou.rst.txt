================================================
Residual transmission of hot stars (mktellu)
================================================

The residual transmission recipe takes a single hot star observation (an extracted, flat-fielded 2D spectrum).
The first step is a pre-cleaning correction which essentially removes the bulk of the telluric absorption, producing
a corrected 2D spectrum as well as an absorption spectrum, sky model, and an estimate of the water and dry components
of the absorption (Artigau in prep). The pre-cleaning uses a stellar template, if available, to better measure the
water and dry components. The corrected 2D spectrum is then normalized by the 95$^{th}$ percentile of the blaze per
order and the residual transmission map is created by using a low-pass filter (per order) on the hot star (and
dividing by a template if present).

We make sure the pre-cleaning was successful (i.e., the water component exponent is between 0.1 and 15 and the dry
component exponent is between 0.8 and 3.0) and check that the SNR for each order is above a $100$; subsequently, the
hot star residual transmission maps are added to the telluric database.