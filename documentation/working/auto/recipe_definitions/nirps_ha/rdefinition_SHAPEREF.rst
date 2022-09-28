
.. _recipes_nirps_ha_shaperef:


################################################################################
apero_shape_ref_nirps_ha
################################################################################


********************************************************************************
1. Description
********************************************************************************


SHORTNAME: SHAPEREF


No description set


********************************************************************************
2. Schematic
********************************************************************************


No schematic set


********************************************************************************
3. Usage
********************************************************************************


.. code-block:: 

    apero_shape_ref_nirps_ha.py {obs_dir}[STRING] --fpfiles[FILE:FP_FP] {options}


.. code-block:: 

     {obs_dir}[STRING] // OBS_DIR_HELP
     --fpfiles[FILE:FP_FP] // Current allowed types: FP_FP


********************************************************************************
4. Optional Arguments
********************************************************************************


.. code-block:: 

     --database[True/False] // [BOOLEAN] Whether to add outputs to calibration database
     --badpixfile[FILE:BADPIX] // [STRING] Define a custom file to use for bad pixel correction. Checks for an absolute path and then checks directory
     --badcorr[True/False] // [BOOLEAN] Whether to correct for the bad pixel file
     --backsub[True/False] // [BOOLEAN] Whether to do background subtraction
     --combine[True/False] // [BOOLEAN] Whether to combine fits files in file list or to process them separately
     --darkfile[FILE:DARKREF] // [STRING] The Dark file to use (CALIBDB=DARKM)
     --darkcorr[True/False] // [BOOLEAN] Whether to correct for the dark file
     --flipimage[None,x,y,both] // [BOOLEAN] Whether to flip fits image
     --fluxunits[ADU/s,e-] // [STRING] Output units for flux
     --locofile[FILE:LOC_LOCO] // [STRING] Sets the LOCO file used to get the coefficients (CALIBDB=LOC_{fiber})
     --plot[0>INT>3] // [INTEGER] Plot level. 0 = off, 1 = interactively, 2 = save to file
     --resize[True/False] // [BOOLEAN] Whether to resize image
     --fpref[FILE:REF_FP] // [STRING] Define a custom file to use for the FP reference (skips the FP reference step) - this file must have been produced by a previous run of cal_shape_reference


********************************************************************************
5. Special Arguments
********************************************************************************


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
     --nosave[STRING] // Do not save any outputs (debug/information run). Note some recipes require other recipesto be run. Only use --nosave after previous recipe runs have been run successfully at least once.
     --force_indir[STRING] // [STRING] Force the default input directory (Normally set by recipe)
     --force_outdir[STRING] // [STRING] Force the default output directory (Normally set by recipe)


********************************************************************************
6. Output directory
********************************************************************************


.. code-block:: 

    DRS_DATA_REDUC // Default: "red" directory


********************************************************************************
7. Output files
********************************************************************************


.. csv-table:: Outputs
   :file: rout_SHAPEREF.csv
   :header-rows: 1
   :class: csvtable


********************************************************************************
8. Debug plots
********************************************************************************


.. code-block:: 

    SHAPE_DX
    SHAPE_ANGLE_OFFSET_ALL
    SHAPE_ANGLE_OFFSET
    SHAPE_LINEAR_TPARAMS


********************************************************************************
9. Summary plots
********************************************************************************


.. code-block:: 

    SUM_SHAPE_ANGLE_OFFSET

