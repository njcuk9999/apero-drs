
.. _recipes_nirps_ha_shapem:


################################################################################
apero_shape_master_nirps_ha
################################################################################


********************************************************************************
1. Description
********************************************************************************


SHORTNAME: SHAPEM


No description set


********************************************************************************
2. Schematic
********************************************************************************


No schematic set


********************************************************************************
3. Usage
********************************************************************************


.. code-block:: 

    apero_shape_master_nirps_ha.py {obs_dir}[STRING] --fpfiles[FILE:FP_FP] {options}


.. code-block:: 

     {obs_dir}[STRING] // OBS_DIR_HELP
     --fpfiles[FILE:FP_FP] // SHAPE_FPFILES_HELP


********************************************************************************
4. Optional Arguments
********************************************************************************


.. code-block:: 

     --database[True/False] // [BOOLEAN] Whether to add outputs to calibration database
     --badpixfile[FILE:BADPIX] // BADFILE_HELP
     --badcorr[True/False] // DOBAD_HELP
     --backsub[True/False] // BACKSUB_HELP
     --combine[True/False] // COMBINE_HELP
     --darkfile[FILE:DARKM] // DARKFILE_HELP
     --darkcorr[True/False] // DODARK_HELP
     --flipimage[None,x,y,both] // FLIPIMAGE_HELP
     --fluxunits[ADU/s,e-] // FLUXUNITS_HELP
     --locofile[FILE:LOC_LOCO] // LOCOFILE_HELP
     --plot[-1>INT>2] // [INTEGER] Plot level. 0 = off, 1 = interactively, 2 = save to file
     --resize[True/False] // RESIZE_HELP
     --fpmaster[FILE:MASTER_FP] // SHAPE_FPMASTER_HELP


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
     --master[STRING] // If set then recipe is a master recipe (e.g. master recipes write to calibration database as master calibrations)
     --crunfile[STRING] // Set a run file to override default arguments
     --quiet[STRING] // Run recipe without start up text
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
   :file: rout_SHAPEM.csv
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

