
.. _recipes_spirou_ccf:


################################################################################
apero_ccf_spirou
################################################################################


********************************************************************************
1. Description
********************************************************************************


SHORTNAME: CCF


No description set


********************************************************************************
2. Schematic
********************************************************************************


No schematic set


********************************************************************************
3. Usage
********************************************************************************


.. code-block:: 

    apero_ccf_spirou.py {obs_dir}[STRING] [FILE:EXT_E2DS,EXT_E2DS_FF,TELLU_OBJ] {options}


.. code-block:: 

     {obs_dir}[STRING] // OBS_DIR_HELP
     [FILE:EXT_E2DS,EXT_E2DS_FF,TELLU_OBJ] // [STRING/STRINGS] A list of fits files to use separated by spaces. CCF_FILES_HELP


********************************************************************************
4. Optional Arguments
********************************************************************************


.. code-block:: 

     --mask[FILE:CCF_MASK] // CCF_MASK_HELP
     --rv[FLOAT] // CCF_RV_HELP
     --width[FLOAT] // CCF_WIDTH_HELP
     --step[FLOAT] // CCF_STEP_HELP
     --masknormmode[None,all,order] // CCF_MASK_NORM_HELP
     --database[True/False] // [BOOLEAN] Whether to add outputs to calibration database
     --blazefile[FILE:FF_BLAZE] // BLAZEFILE_HELP
     --plot[-1>INT>2] // [INTEGER] Plot level. 0 = off, 1 = interactively, 2 = save to file


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
   :file: rout_CCF.csv
   :header-rows: 1
   :class: csvtable


********************************************************************************
8. Debug plots
********************************************************************************


.. code-block:: 

    CCF_RV_FIT
    CCF_RV_FIT_LOOP
    CCF_SWAVE_REF
    CCF_PHOTON_UNCERT


********************************************************************************
9. Summary plots
********************************************************************************


.. code-block:: 

    SUM_CCF_PHOTON_UNCERT
    SUM_CCF_RV_FIT

