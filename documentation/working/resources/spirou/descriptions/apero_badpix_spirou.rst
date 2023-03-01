========================
Bad pixel calibration
========================


The bad pixel recipe takes preprocessed `DARK_DARK` and `FLAT_FLAT` files (as many as given by the user or as many as
occur on the nights being used via pre-processing). It combines all `DARK_DARK` files and all `FLAT_FLAT` files into a
single `DARK_DARK` and a single `FLAT_FLAT` (via a median combination of the images). Bad pixels are then identified
in the `FLAT_FLAT` by using Equation:

.. math::

