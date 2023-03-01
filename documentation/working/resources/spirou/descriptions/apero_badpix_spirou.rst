================================
Bad pixel calibration
================================


The bad pixel recipe takes preprocessed `DARK_DARK` and `FLAT_FLAT` files (as many as given by the user or as many as
occur on the nights being used via pre-processing). It combines all `DARK_DARK` files and all `FLAT_FLAT` files into a
single `DARK_DARK` and a single `FLAT_FLAT` (via a median combination of the images). Bad pixels are then identified
in the `FLAT_FLAT` by using Equation:

.. math::

    M_{\text{flat } i,j} = \left\{ \begin{array}
      1 : & FLAT_{i,j} \text{ is not finite} \\
      1 : & \mid (FLAT_{i,j} / FLAT_{\text{med } i,j}) - 1 \mid > \text{cut_ratio} \\
      1 : & FLAT_{\text{med } i,j} < \text{illum_cut} \\
      0 : & \text{otherwise} \\
    \end{array} \right.

where :math:`FLAT_{i,j}` is the flux in ith row jth column of the `FLAT_FLAT` image;
:math:`FLAT_{\text{med }}` is the median filtered flat image (using a filtering width of 7 pixels)
and :math:`M_{\text{flat } i,j}` is 1 to flag a bad pixel or 0 otherwise, cut_ratio is 0.5 (flagging pixels
with a response less than 50 percent of their neighbors or unphysically brighter than neighbors) and
illum\_cut is 0.05 (flagging pixels at the edge of the blaze response). `FLAT` and :math:`FLAT_{\text{med }}`
have first been normalized by the $90^{\rm th}$ percentile of flux in the median filtered flat image.
Thus :math:`M_{\text{flat}}` is a Boolean flag map of bad pixels on the flat image.
For the `DARK_DARK` image, bad pixels are identified using Equation:

.. math::

    M_{\text{dark } i,j} = \left\{ \begin{array}
      1 : & DARK_{i,j} \text{ is not finite} \\
      1 : & DARK_{i,j} > 5.0 \text{ADU/s}  \\
      0 : & \text{otherwise} \\
    \end{array} \right.

where :math:`DARK_{i,j}` is the flux in the ith row jth column of the dark image.
Thus :math:`M_{\text{dark}}` is a Boolean flag map of bad pixels on the dark image.
We choose a value of 5.0 ADU/s as it is representative of the pixel flux of a typical science target.
Including pixels with a brighter level of dark current than this leads to a loss in SNR rather than a gain.
We note that this threshold could be target-dependent but for simplicity we use a single value.

In addition to this bad pixels in a full detector engineering flat (FULLFLAT taken during commissioning)
are also identified using Equation:

.. math::

    M_{\text{full-flat } i,j} = \left\{ \begin{array}
      1 : & \mid FULLFLAT_{i,j} - 1 \mid > 0.3  \\
      0 : & \text{otherwise} \\
    \end{array} \right.

where :math:`FULLFLAT_{i,j}` is the flux in ith row jth column of the full detector engineering flat.
Thus :math:`M_{\text{full-flat}}` is a Boolean flag map of bad pixels on the full detector engineering flat image.
We chose 0.3 as this flagged the defective regions identified manually on the detector.
The 1:math:`\sigma` dispersion of the full detector engineering flat image is 2 percent.

These three bad pixel maps are then combined into a single bad pixel map.