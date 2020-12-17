.. _recipes_spirou_localisation:

******************************************
Localisation Recipe
******************************************

Finds the orders on the image.

Needs to be run twice - once with FLAT_DARK files (to create the localisation
for fiber AB) and once with DARK_FLAT (to create the localisation for fiber C).

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

.. code-block:: bash

    ORDER_PROFILE_{FIBER} {NIGHT_NAME} {FILENAME} {HUMAN DATE} {UNIX DATE}
    LOC_{FIBER} {NIGHT_NAME} {FILENAME} {HUMAN DATE} {UNIX DATE}

===========================================
Output files
===========================================

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
