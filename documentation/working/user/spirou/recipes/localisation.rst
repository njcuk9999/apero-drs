.. _recipes_spirou_localisation:

******************************************
Localisation Recipe
******************************************

Finds the orders on the image.

Needs to be run twice - once with FLAT_DARK files (to create the localisation
for fiber AB) and once with DARK_FLAT (to create the localisation for fiber C).

The first step is to combine the FLAT_DARK (or DARK_FLAT) into a single file.
These files are then :ref:`calibrated <science_calib_calibrate_pp_files>`.

After calibration we then calculate the order profile (used for optimal extraction)
and then find the orders - by first selecting a set of rows around the central
column and fitting peaks to locate the order centers. For each order we then
find the center in steps towards the left and right of the detector. Polynomials
are then fit to each order for the position centers and the width of each order.

The polynomial coefficients are then checked and continuity is forced between the
orders. Once a final set of polynomial coefficients is calculated (for both
position centers and width) for each order the localisation map is constructed.

After quality control the localisation files are written and if the data passed
the quality control files are added to the calibration database.


===========================================
Schematic
===========================================

.. only:: html

    .. image:: ../../../_static/yed/spirou/cal_loc_spirou_schematic.jpg

.. only:: latex

    This section can only currently be viewed in the html documentation.

===========================================
Run
===========================================

.. code-block:: bash

    cal_loc_spirou.py [DIRECTORY] [FLAT_DARK]
    cal_loc_spirou.py [DIRECTORY] [DARK_FLAT]

===========================================
Optional Arguments
===========================================

.. code-block:: bash

    --database, --badpixfile, --badcorr, --backsub, --combine,
    --darkfile, --darkcorr,  --flipimage, --fluxunits, --plot, --resize,
    --debug, --listing, --listingall, --version, --info,
    --program, --idebug, --breakpoints, --quiet, --help

===========================================
Output Dir
===========================================

.. code-block:: bash

    DRS_DATA_REDUC   \\ default "reduced" directory

===========================================
Calibration database entry
===========================================

Note using FLAT_DARK inputs gives FIBER = AB,
using DARK_FLAT inputs gives FIBER = C

.. code-block:: bash

    ORDER_PROFILE_{FIBER} {NIGHT_NAME} {FILENAME} {HUMAN DATE} {UNIX DATE}
    LOC_{FIBER} {NIGHT_NAME} {FILENAME} {HUMAN DATE} {UNIX DATE}

===========================================
Output files
===========================================

Note using FLAT_DARK inputs gives FIBER = AB,
using DARK_FLAT inputs gives FIBER = C

.. code-block:: bash

    {ODOMETER_CODE}_pp_order_profile_{FIBER}.fits  \\ order profile file (3100x4088)
    {ODOMETER_CODE}_pp_loco_{FIBER}.fits           \\ localisation centers map file (49x4088)
    {ODOMETER_CODE}_pp_fwhm-order_{FIBER}.fits     \\ localisation widths map file (49x4088)
    {ODOMETER_CODE}_pp_with-order_{FIBER}.fits     \\ localisation superposition file (3100x4088)
    DEBUG_{ODOMETER_CODE}_pp_background.fits \\ debug background file (7x3100x4088)


===========================================
Plots
===========================================

.. code-block:: bash

    LOC_MINMAX_CENTS, LOC_MIN_CENTS_THRES, LOC_FINDING_ORDERS, LOC_IM_SAT_THRES,
    LOC_ORD_VS_RMS, LOC_CHECK_COEFFS, LOC_FIT_RESIDUALS
