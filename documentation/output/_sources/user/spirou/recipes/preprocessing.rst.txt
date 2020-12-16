.. _recipes_spirou_preprocessing:

******************************************
Preprocessing Recipe
******************************************

Cleans file of detector effects, fixes headers and produces 'pre-processed'
files.

The inputs to this code are SPIRou RAMP files (i.e. {odometer code}.fits
e.g. 1234567o.fits, 1234568a.fits, 1234569c.fits

The first step in preprocessing is to fix the header. Details of this are
provided :ref:`here <science_preprocessing_header_fixes>`.

After the header is fixed for APERO use the raw file is checked to be of
known type. The identification of raw files can be read about
:ref:`here <science_preprocessing_file_identification>`.

If we are dealing with an astrophysical object observation (OBJ_DARK or OBJ_FP)
we must make sure the object name / gaia id are identified as being valid by APERO.
Read about this :ref:`here <science_preprocessing_object_finding>`

Next we test for corrupted files.

Then we correct for top/bottom pixels.

Then we median filter using the unilliminated amplifiers.

Then we correct the 1/f noise and apply it to the image.

Our final step is to rotate the image into the standard APERO
:term:`pre-processing-coordinate-system`.

We then save the image with the "{odometer code}_pp.fits" suffix.

===========================================
Schematic
===========================================

.. only:: html

    .. image:: ../../../_static/yed/spirou/cal_preproces_spirou_schematic.jpg
        :width: 100%
        :align: center

.. only:: latex

    This section can only currently be viewed in the html documentation.

===========================================
Run
===========================================

.. code-block:: bash

    cal_preprocess_spirou.py [DIRECTORY] [RAW_FILES]

===========================================
Optional Arguments
===========================================

.. code-block:: bash

    --skip, --debug, --listing, --listingall, --version, --info, 
    --program, --idebug, --breakpoints, --quiet, --help 


===========================================
Output Dir:
===========================================

.. code-block:: bash

    DRS_DATA_WORKING   \\ default: "tmp" directory


===========================================
Output files
===========================================

.. code-block:: bash

    {ODOMETER_CODE}_pp.fits  \\ preprocessed files (4096x4096)

===========================================
Plots
===========================================

.. code-block:: bash

    None
