.. _recipes_spirou_shape_master:

******************************************
Shape Master Recipe
******************************************

Creates a master FP image from all FPs processed. Uses this to work out the
required shifts due to the FP master image, slicer pupil geometry and the
bending of the orders (found in localisation).

The shape master requires a 'reference' pre-processed HC_HC file and FP_FP file.
These are normally a set of HC_HC files and FP_FP files from one single night
(i.e. the master night).

The first step is to check that the FP files are valid (details
:ref:`here <science_calib_check_fp>`).

After this the reference HC_HC files and reference FP_FP files are combined.
We then get the localisation cofficients (from the calibration database)
and look for a wave solution (either from the calibration database - from a
previous solution - or if that does not exist from the default master
wave solution).

We then calibration the combined reference HC_HC and combined reference FP_FP
using the :ref:`pre-processing calibration function <science_calib_calibrate_pp_files>`.

Next we find all FP_FP files that have currently been pre-processed - this
means all FP_FP files from all nights (or as many as possible) should have
been preprocessed by this point.

If the user defiend a master fp (via --fpmaster) we load this master FP otherwise
we load all FP_FP file headers and generate a table of key header parameters and
then construct the master FP (using a median - in such a way that we do not have
too many FP_FP files open at once).

Once the master FP map is loaded (or generated) we calculate the dx shift map
(correction due to the slicer profile and tilt) and calculate the dy shift map
(due to the arching of the orders). There is also a check at this point that
the dx map was generated correction - if not the recipe ends (QC failure).

After calculating the dx shift map and dy shift map we then have to shift
the dx shift map by the dy shift map (so that all dx shifts are applied after
a dy shift). We then transform the combined reference HC_HC and combined reference
FP_FP files using the dx shift map and dy shift map.

After quality control the shape master files are then written to disk and if the
data passed the quality control files are added to the calibration database.


===========================================
Schematic
===========================================

.. only:: html

    .. image:: ../../../_static/yed/spirou/cal_shape_master_spirou_schematic.jpg

.. only:: latex

    This section can only currently be viewed in the html documentation.

===========================================
Run
===========================================

.. code-block:: bash

    cal_shape_master_spirou.py [DIRECTORY] -hcfiles [HCONE_HCONE] -fpfiles [FP_FP]

===========================================
Optional Arguments
===========================================

.. code-block:: bash

    --database, --badpixfile, --badcorr, --backsub, --combine,
    --darkfile, --darkcorr,  --flipimage, --fluxunits, --locofile,
    --plot, --resize,
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

    SHAPEX {NIGHT_NAME} {FILENAME} {HUMAN DATE} {UNIX DATE}
    SHAPEY {NIGHT_NAME} {FILENAME} {HUMAN DATE} {UNIX DATE}
    FPMASTER {NIGHT_NAME} {FILENAME} {HUMAN DATE} {UNIX DATE}

===========================================
Output files
===========================================

.. code-block:: bash

    {ODOMETER_CODE}_pp_shapex.fits            \\ dx shape map (3100x4088)
    {ODOMETER_CODE}_pp_shapey.fits            \\ dy shape map (3100x4088)
    {ODOMETER_CODE}_pp_fpmaster.fits          \\ fp master file (3100x4088) + FITS-TABLE
    DEBUG_{ODOMETER_CODE}_shape_out_bdx.fits  \\ dx map before dy map (3100x4088)
    DEBUG_{ODOMETER_CODE}_shape_in_fp.fits    \\ input fp before shape corr (3100x4088)
    DEBUG_{ODOMETER_CODE}_shape_out_fp.fits   \\ input fp after shape corr (3100x4088)
    DEBUG_{ODOMETER_CODE}_shape_in_hc.fits    \\ input hc before shape corr (3100x4088)
    DEBUG_{ODOMETER_CODE}_shape_out_hc.fits   \\ input hc after shape corr (3100x4088)
    DEBUG_{ODOMETER_CODE}_pp_background.fits \\ debug background file (7x3100x4088)


===========================================
Plots
===========================================

.. code-block:: bash

    SHAPE_DX, SHAPE_ANGLE_OFFSET_ALL, SHAPE_ANGLE_OFFSET, SHAPE_LINEAR_TPARAMS
