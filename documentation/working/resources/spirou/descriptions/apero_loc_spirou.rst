================================
Localization calibration
================================

The localization recipe takes preprocessed `DARK_FLAT` or `FLAT_DARK` files (as many as given by the user or as many as
occur on the nights being used via \Aprocessing). It is run twice, once for the C fiber localization (with a set of
`DARK_FLAT`) and once for the AB fiber localization (with a set of `FLAT_DARK`). It combines the `DARK_FLAT` files or the
`FLAT_DARK` files into a single `DARK_FLAT` or `FLAT_DARK` (via a median combination of the images). After combining, the
images are calibrated using our standard image calibration technique.

The first step in the localization code is to take the combined and calibrated `DARK_FLAT` or `FLAT_DARK` and apply a
weighted box median, shown in equation:

.. math::

    IM_{\text{orderp } j} = \left\{ \begin{array}
      \text{MED}(IM_{j=0:j=k+1}):     & k < 5            \\
      \text{MED}(IM_{j=k-5:j=4088}):  & k > 4088 - 5     \\
      \text{MED}(IM_{j=k-5:j=k+5+1}): & \text{otherwise} \\
    \end{array} \right.

where :math:`IM_{\text{orderp } j}` is the order profile flux for all rows in the jth column,
:math:`IM_{j=x:j=y}` is the combined, calibrated `DARK_FLAT` or `FLAT_DARK`, that spans all columns from
:math:`j=x` to :math:`j=y`, and k is the column index number and ranges from :math:`j=0` to :math:`j=4088`.

This produces the order profile image of the `DARK_FLAT` or `FLAT_DARK` which is used for the optimal extraction
and to locate the orders.

To locate the orders we use the scikit `measure.label` algorithm which labels connected regions.
Two pixels are defined as connected when both themselves and their neighbors have the same value.
We use a connectivity value of 2 meaning that any of the 8 surrounding pixels can be neighbors if they share
the same value.

In order to facilitate the labeling we first perform a 95th percentile of a box (of size :math:`25\times25` pixels)
across the whole image, as true illuminated pixels' flux is location-dependent. We set a threshold at half that value
and label all pixels above this threshold as one and all pixels below this to a value of zero. We then perform the
`measure.label` on this Boolean map (referred to from this point on as :math:`Mask_{orders}`).
This is just a first guess of the order positions and usually returns many labeled regions that are not true orders.

To remove bad labels we first remove any labeled region with less than 500 pixels. We then remove any pixel within a
labeled region that has a flux value less than 0.05 times the 95th percentile of all pixels in that given labeled
region and remove this pixel from :math:`Mask_{orders}`. We then median filter each row of :math:`Mask_{orders}` to
clean up the labeled edges and apply a binary dilation (scipy `ndimage.binary_dilation`) algorithm.
This binary dilation essentially merges labeled regions that are close to each other together by expanding regions
marked with ones around the edges of these regions. After :math:`Mask_{orders}` has been updated we re-run the
labeling algorithm. As a final filtering step, we remove any region center that does not overlap with the central
part of the image in the along-order direction (i.e., the center :math:`\pm` half the width of the detector,
2044 :math:`\pm` 1022 pixels).

Once we have the final set of labeled regions we use :math:`Mask_{orders} on each order to fit a polynomial fit
(of degree 3) to the pixel positions in that labeled region forcing continuity between orders by fitting each
coefficient across the orders. We also use the :math:`Mask_{orders} pixel positions to linearly fit the width of
each order.

For a `DARK_FLAT`, this produces polynomial fits and coefficients for 49 orders for the C fiber.
For a `FLAT_DARK` input, this produces polynomial fits and coefficients for 98 orders (49 orders for A and 49 orders
for B). These polynomial coefficients for the positions of the orders and the widths of the orders are then converted
into values as a function of position across each order.

As part of quality control we check that:

 - the number of orders is consistent with the required number of orders (49 for fiber C, 98 for fibers A+B).
 - the across-order value at the center of the detector is always larger than the value of the previous order

The order profile (ORDERP), locations of the orders (LOCO), and widths of the orders are saved to the calibration
database (if both quality control criteria are met) for use throughout APERO.