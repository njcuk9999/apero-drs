.. _recipes_spirou_dark_master:

******************************************
Dark Master Recipe
******************************************

Collects all dark files and creates a master dark image to use for correction.


First step is to locate all pre-processed DARK_DARK files. Thus one needs to
run :ref:`preprocessing <recipes_spirou_preprocessing>` on all DARK_DARK files
before running the dark master recipe.

Next a table of key header values from the DARK_DARK headers is constructed and
a master dark is made by combining all valid DARK frames (using a median - in
such a way that we do not have too many DARK_DARK files open at once).

Then quality control is done (currently there are no quality control for the
master dark - just the individual darks).

Then the master dark file is saved to disk and added to the calibration database.

===========================================
Schematic
===========================================

.. only:: html

    .. image:: ../../../_static/yed/spirou/cal_dark_master_spirou_schematic.jpg

.. only:: latex

    This section can only currently be viewed in the html documentation.

===========================================
Run
===========================================

.. code-block:: bash

    apero_dark_master_spirou.py

===========================================
Optional Arguments
===========================================

.. code-block:: bash

    --filetype, --database, --plot,
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

    DARKM {NIGHT_NAME} {FILENAME} {HUMAN DATE} {UNIX DATE}

===========================================
Output files
===========================================

.. code-block:: bash

    {ODOMETER_CODE}_pp_dark_master.fits  \\ dark master file (4096x4096) + FITS-TABLE


===========================================
Plots
===========================================

.. code-block:: bash

    None

===========================================
Notes
===========================================

Does not require a master night choice - finds darks from all preprocessed nights.