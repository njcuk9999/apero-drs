.. _recipes_spirou_bad_pixels:


******************************************
Bad Pixel Correction Recipe
******************************************

Creates a bad pixel mask for identifying and deal with bad pixels.

===========================================
Schematic
===========================================

.. only:: html

    .. image:: ../../../_static/yed/spirou/cal_badpix_spirou_schematic.jpg

.. only:: latex

    This section can only currently be viewed in the html documentation.

===========================================
Run
===========================================

.. code-block:: bash

    cal_badpix_spirou.py [DIRECTORY] -flatfiles [FLAT_FLAT] -darkfiles [DARK_DARK_TEL]
    cal_badpix_spirou.py [DIRECTORY] -flatfiles [FLAT_FLAT] -darkfiles [DARK_DARK_INT]

===========================================
Optional Arguments
===========================================

.. code-block:: bash

    --database, --combine, --flipimage, --fluxunits, --plot, --resize,
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

    BADPIX {NIGHT_NAME} {FILENAME} {HUMAN DATE} {UNIX DATE}
    BKGRDMAP {NIGHT_NAME} {FILENAME} {HUMAN DATE} {UNIX DATE}

===========================================
Output files
===========================================

.. code-block:: bash

    {ODOMETER_CODE}_pp_badpixel.fits  \\ bad pixel map file (3100x4088)
    {ODOMETER_CODE}_pp_bmap.fits      \\ background mask file (3100x4088)
    DEBUG_{ODOMETER_CODE}_pp_background.fits \\ debug background file (7x3100x4088)


===========================================
Plots
===========================================

.. code-block:: bash

    BADPIX_MAP