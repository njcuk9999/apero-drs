
.. _recipes_nirps_he_shape:


################################################################################
apero_shape_nirps_he
################################################################################



Contents
================================================================================

* :ref:`1. Description <desc_nirps_he_SHAPE>`
* :ref:`2. Schematic <schematic_nirps_he_SHAPE>`
* :ref:`3. Usage <usage_nirps_he_SHAPE>`
* :ref:`4. Optional Arguments <optargs_nirps_he_SHAPE>`
* :ref:`5. Special Arguments <spargs_nirps_he_SHAPE>`
* :ref:`6. Output directory <outdir_nirps_he_SHAPE>`
* :ref:`7. Output files <outfiles_nirps_he_SHAPE>`
* :ref:`8. Debug plots <debugplots_nirps_he_SHAPE>`
* :ref:`9. Summary plots <summaryplots_nirps_he_SHAPE>`


1. Description
================================================================================


.. _desc_nirps_he_SHAPE:


SHORTNAME: SHAPE


No description set


2. Schematic
================================================================================


.. _schematic_nirps_he_SHAPE:


No schematic set


3. Usage
================================================================================


.. _usage_nirps_he_SHAPE:


.. code-block:: 

    apero_shape_nirps_he.py {obs_dir}[STRING] [FILE:FP_FP] {options}


.. code-block:: 

     {obs_dir}[STRING] // OBS_DIR_HELP
     [FILE:FP_FP] // SHAPE_FPFILES_HELP


4. Optional Arguments
================================================================================


.. _optargs_nirps_he_SHAPE:


.. code-block:: 

     --database[True/False] // [BOOLEAN] Whether to add outputs to calibration database
     --badpixfile[FILE:BADPIX] // BADFILE_HELP
     --badcorr[True/False] // DOBAD_HELP
     --backsub[True/False] // BACKSUB_HELP
     --combine[True/False] // COMBINE_HELP
     --darkfile[FILE:DARKREF] // DARKFILE_HELP
     --darkcorr[True/False] // DODARK_HELP
     --flipimage[None,x,y,both] // FLIPIMAGE_HELP
     --fluxunits[ADU/s,e-] // FLUXUNITS_HELP
     --fpref[FILE:REF_FP] // FPREFFILE_HELP
     --plot[0>INT>4] // [INTEGER] Plot level. 0 = off, 1 = interactively, 2 = save to file
     --resize[True/False] // RESIZE_HELP
     --shapex[FILE:SHAPE_X] // SHAPEXFILE_HELP
     --shapey[FILE:SHAPE_Y] // SHAPEYFILE_HELP
     --no_in_qc // Disable checking the quality control of input files


5. Special Arguments
================================================================================


.. _spargs_nirps_he_SHAPE:


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


.. _outdir_nirps_he_SHAPE:


.. code-block:: 

    DRS_DATA_REDUC // Default: "red" directory


7. Output files
================================================================================


.. _outfiles_nirps_he_SHAPE:


.. csv-table:: Outputs
   :file: rout_SHAPE.csv
   :header-rows: 1
   :class: csvtable


8. Debug plots
================================================================================


.. _debugplots_nirps_he_SHAPE:


.. code-block:: 

    SHAPEL_ZOOM_SHIFT
    SHAPE_LINEAR_TPARAMS


9. Summary plots
================================================================================


.. _summaryplots_nirps_he_SHAPE:


.. code-block:: 

    SUM_SHAPEL_ZOOM_SHIFT

