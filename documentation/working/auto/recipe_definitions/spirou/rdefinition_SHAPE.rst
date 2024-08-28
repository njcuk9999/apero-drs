
.. _recipes_spirou_shape:


################################################################################
apero_shape_spirou
################################################################################



Contents
================================================================================

* :ref:`1. Description <desc_spirou_SHAPE>`
* :ref:`2. Schematic <schematic_spirou_SHAPE>`
* :ref:`3. Usage <usage_spirou_SHAPE>`
* :ref:`4. Optional Arguments <optargs_spirou_SHAPE>`
* :ref:`5. Special Arguments <spargs_spirou_SHAPE>`
* :ref:`6. Output directory <outdir_spirou_SHAPE>`
* :ref:`7. Output files <outfiles_spirou_SHAPE>`
* :ref:`8. Debug plots <debugplots_spirou_SHAPE>`
* :ref:`9. Summary plots <summaryplots_spirou_SHAPE>`


1. Description
================================================================================


.. _desc_spirou_SHAPE:


SHORTNAME: SHAPE


.. include:: ../../../resources/spirou/descriptions/apero_shape_spirou.rst


2. Schematic
================================================================================


.. _schematic_spirou_SHAPE:


.. only:: html

    .. figure:: ../../../_static/yed/spirou/apero_shape_spirou_schematic.jpg
        :figwidth: 100%
        :width: 100%
        :align: center

.. only:: latex

    This section can only currently be viewed in the html documentation.

3. Usage
================================================================================


.. _usage_spirou_SHAPE:


.. code-block:: 

    apero_shape_spirou.py {obs_dir}[STRING] [FILE:FP_FP] {options}


.. code-block:: 

     {obs_dir}[STRING] // [STRING] The directory to find the data files in. Most of the time this is organised by nightly observation directory
     [FILE:FP_FP] // Current allowed types: FP_FP


4. Optional Arguments
================================================================================


.. _optargs_spirou_SHAPE:


.. code-block:: 

     --database[True/False] // [BOOLEAN] Whether to add outputs to calibration database
     --badpixfile[FILE:BADPIX] // [STRING] Define a custom file to use for bad pixel correction. Checks for an absolute path and then checks 'directory'
     --badcorr[True/False] // [BOOLEAN] Whether to correct for the bad pixel file
     --backsub[True/False] // [BOOLEAN] Whether to do background subtraction
     --combine[True/False] // [BOOLEAN] Whether to combine fits files in file list or to process them separately
     --darkfile[FILE:DARKREF] // [STRING] The Dark file to use (CALIBDB=DARKM)
     --darkcorr[True/False] // [BOOLEAN] Whether to correct for the dark file
     --flipimage[None,x,y,both] // [BOOLEAN] Whether to flip fits image
     --fluxunits[ADU/s,e-] // [STRING] Output units for flux
     --fpref[FILE:REF_FP] // [STRING] Sets the FP reference file to use (CALIBDB = FPREF)
     --plot[0>INT>4] // [INTEGER] Plot level. 0 = off, 1 = interactively, 2 = save to file
     --resize[True/False] // [BOOLEAN] Whether to resize image
     --shapex[FILE:SHAPE_X] // [STRING] Sets the SHAPE DXMAP file used to get the dx correction map (CALIBDB=SHAPEX)
     --shapey[FILE:SHAPE_Y] // [STRING] Sets the SHAPE DYMAP file used to get the dy correction map (CALIBDB=SHAPEY)
     --no_in_qc // Disable checking the quality control of input files


5. Special Arguments
================================================================================


.. _spargs_spirou_SHAPE:


.. code-block:: 

     --xhelp[STRING] // Extended help menu (with all advanced arguments)
     --debug[STRING] // Activates debug mode (Advanced mode [INTEGER] value must be an integer greater than 0, setting the debug level)
     --listing[STRING] // Lists the night name directories in the input directory if used without a 'directory' argument or lists the files in the given 'directory' (if defined). Only lists up to 15 files/directories
     --listingall[STRING] // Lists ALL the night name directories in the input directory if used without a 'directory' argument or lists the files in the given 'directory' (if defined)
     --version[STRING] // Displays the current version of this recipe.
     --info[STRING] // Displays the short version of the help menu
     --program[STRING] // [STRING] The name of the program to display and use (mostly for logging purpose) log becomes date | {THIS STRING} | Message
     --recipe_kind[STRING] // [STRING] The recipe kind for this recipe run (normally only used in apero_processing.py)
     --parallel[STRING] // [BOOL] If True this is a run in parellel - disable some features (normally only used in apero_processing.py)
     --shortname[STRING] // [STRING] Set a shortname for a recipe to distinguish it from other runs - this is mainly for use with apero processing but will appear in the log database
     --idebug[STRING] // [BOOLEAN] If True always returns to ipython (or python) at end (via ipdb or pdb)
     --ref[STRING] // If set then recipe is a reference recipe (e.g. reference recipes write to calibration database as reference calibrations)
     --crunfile[STRING] // Set a run file to override default arguments
     --quiet[STRING] // Run recipe without start up text
     --nosave // Do not save any outputs (debug/information run). Note some recipes require other recipesto be run. Only use --nosave after previous recipe runs have been run successfully at least once.
     --force_indir[STRING] // [STRING] Force the default input directory (Normally set by recipe)
     --force_outdir[STRING] // [STRING] Force the default output directory (Normally set by recipe)


6. Output directory
================================================================================


.. _outdir_spirou_SHAPE:


.. code-block:: 

    DRS_DATA_REDUC // Default: "red" directory


7. Output files
================================================================================


.. _outfiles_spirou_SHAPE:


.. csv-table:: Outputs
   :file: rout_SHAPE.csv
   :header-rows: 1
   :class: csvtable


8. Debug plots
================================================================================


.. _debugplots_spirou_SHAPE:


.. code-block:: 

    SHAPEL_ZOOM_SHIFT
    SHAPE_LINEAR_TPARAMS


9. Summary plots
================================================================================


.. _summaryplots_spirou_SHAPE:


.. code-block:: 

    SUM_SHAPEL_ZOOM_SHIFT

