.. _recipes_spirou_shape_local:

******************************************
Shape (per night) Recipe
******************************************

Takes the shape master outputs (shapex, shapey and fpmaster) and applies
these transformations to shift the image to the master fp frame, unbend images
and shift to correct for slicer pupil geometry.

===========================================
Schematic
===========================================

.. only:: html

    .. image:: ../../../_static/yed/spirou/cal_shape_spirou_schematic.jpg

.. only:: latex

    This section can only currently be viewed in the html documentation.

===========================================
Run
===========================================

.. code-block:: bash

    cal_shape_spirou.py [DIRECTORY] [FP_FP]

===========================================
Optional Arguments
===========================================

.. code-block:: bash

    --database, --badpixfile, --badcorr, --backsub, --combine,
    --darkfile, --darkcorr,  --flipimage, --fluxunits, --fpmaster,
    --plot, --resize, --shapex, --shapey,
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

    SHAPEL {NIGHT_NAME} {FILENAME} {HUMAN DATE} {UNIX DATE}

===========================================
Output files
===========================================

.. code-block:: bash

    {ODOMETER_CODE}_pp_shapel.fits            \\ local shape map (3100x4088)
    DEBUG_{ODOMETER_CODE}_shape_in_fp.fits    \\ input fp before shape corr (3100x4088)
    DEBUG_{ODOMETER_CODE}_shape_out_fp.fits   \\ input fp after shape corr (3100x4088)
    DEBUG_{ODOMETER_CODE}_pp_background.fits \\ debug background file (7x3100x4088)


===========================================
Plots
===========================================

.. code-block:: bash

    SHAPE_DX, SHAPE_ANGLE_OFFSET_ALL, SHAPE_ANGLE_OFFSET, SHAPE_LINEAR_TPARAMS

