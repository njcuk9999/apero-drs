================================================
Water and dry component models (mkmodel)
================================================

During the pre-cleaning process (Artigau in prep.) for the hot stars (done as part of Amktellu) we calculate the
water and dry exponents of absorption. Once we have observed a sufficiently large library of telluric hot stars,
typically a few tens under varying airmass and water column conditions, we take all of the residual transmission
maps that passed quality control and calculate a linear minimization of the parameters. The linear minimization is
done per pixel per order, across all transmission maps (removing outliers with a sigma clipping approach) against a
three-vector sample (the bias level of the residual, the water absorption exponent, and the dry absorption exponent).
The output is three vectors each the same size as the input 2D spectrum (:math:`49\times4088`), one for each of the
three vector samples. These are used in every ftellu recipe run to correct the telluric
residuals after telluric cleaning. The three vectors are saved and added to the telluric database.