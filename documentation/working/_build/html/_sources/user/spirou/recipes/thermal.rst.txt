.. _recipes_spirou_thermal:


******************************************
Thermal Correction Recipe
******************************************

Extracts dark frames in order to provide correction for the thermal background
after extraction of science / calibration frames.

===========================================
Schematic
===========================================

.. only:: html

    .. image:: ../../../_static/yed/spirou/cal_thermal_spirou_schematic.jpg

.. only:: latex

    This section can only currently be viewed in the html documentation.

===========================================
Run
===========================================

.. code-block:: bash

    cal_thermal_spirou.py [DIRECTORY] [DARK_DARK_INT]
    cal_thermal_spirou.py [DIRECTORY] [DARK_DARK_TEL]

===========================================
Optional Arguments
===========================================

.. code-block:: bash

    --database, --badpixfile, --badcorr, --backsub, --combine,
    --darkfile, --darkcorr,  --fiber, --flipimage, --fluxunits,
    --locofile, --orderpfile, --plot, --resize,
    --shapex, --shapey, --shapel, --wavefile,
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

    THERMALT_{FIBER} {NIGHT_NAME} {FILENAME} {HUMAN DATE} {UNIX DATE}
    THERMALI_{FIBER} {NIGHT_NAME} {FILENAME} {HUMAN DATE} {UNIX DATE}

===========================================
Output files
===========================================

.. code-block:: bash

    {ODOMETER_CODE}_pp_e2ds_{FIBER}.fits              \\ extracted + flat field file (49x4088)
    {ODOMETER_CODE}_pp_e2dsff_{FIBER}.fits            \\ extracted + flat field file (49x4088)
    {ODOMETER_CODE}_pp_s1d_w_{FIBER}.fits             \\ s1d constant in pixel space (FITS-TABLE)
    {ODOMETER_CODE}_pp_s1d_v_{FIBER}.fits             \\ s1d constant in velocity space (FITS-TABLE)
    DEBUG_{ODOMETER_CODE}_pp_e2dsll_{FIBER}.fits      \\ debug pre extract file (7x3100x4088)
    DEBUG_{ODOMETER_CODE}_pp_background.fits       \\ debug background file (7x3100x4088)
    {ODOMETER_CODE}_pp_thermal_e2ds_int_{FIBER}.fits  \\ extracted thermal for dark_dark_int (49x4088)
    {ODOMETER_CODE}_pp_thermal_e2ds_tel_{FIBER}.fits  \\ extracted thermal for dark_dark_tel (49x4088)


===========================================
Plots
===========================================

.. code-block:: bash

    None
