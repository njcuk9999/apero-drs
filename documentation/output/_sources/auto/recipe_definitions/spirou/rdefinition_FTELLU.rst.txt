
.. _recipes_spirou_ftellu:


################################################################################
apero_fit_tellu_spirou
################################################################################


********************************************************************************
1. Description
********************************************************************************


SHORTNAME: FTELLU


No description set


********************************************************************************
2. Schematic
********************************************************************************


No schematic set


********************************************************************************
3. Usage
********************************************************************************


.. code-block:: 

    apero_fit_tellu_spirou.py {obs_dir}[STRING] [FILE:EXT_E2DS,EXT_E2DS_FF] {options}


.. code-block:: 

     {obs_dir}[STRING] // OBS_DIR_HELP
     [FILE:EXT_E2DS,EXT_E2DS_FF] // [STRING/STRINGS] A list of fits files to use separated by spaces. FTELLU_FILES_HELP


********************************************************************************
4. Optional Arguments
********************************************************************************


.. code-block:: 

     --use_template[True/False] // USE_TEMP_HELP
     --template[FILE:TELLU_TEMP] // TEMPLATE_FILE_HELP
     --database[True/False] // [BOOLEAN] Whether to add outputs to calibration database
     --blazefile[FILE:FF_BLAZE] // BLAZEFILE_HELP
     --plot[-1>INT>2] // [INTEGER] Plot level. 0 = off, 1 = interactively, 2 = save to file
     --wavefile[FILE:WAVESOL_MASTER,WAVE_NIGHT,WAVESOL_DEFAULT] // WAVEFILE_HELP


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
   :file: rout_FTELLU.csv
   :header-rows: 1
   :class: csvtable


********************************************************************************
8. Debug plots
********************************************************************************


.. code-block:: 

    EXTRACT_S1D
    EXTRACT_S1D_WEIGHT
    FTELLU_PCA_COMP1
    FTELLU_PCA_COMP2
    FTELLU_RECON_SPLINE1
    FTELLU_RECON_SPLINE2
    FTELLU_WAVE_SHIFT1
    FTELLU_WAVE_SHIFT2
    FTELLU_RECON_ABSO1
    FTELLU_RECON_ABSO2
    TELLUP_WAVE_TRANS
    TELLUP_ABSO_SPEC
    TELLUP_CLEAN_OH
    FTELLU_RES_MODEL


********************************************************************************
9. Summary plots
********************************************************************************


.. code-block:: 

    SUM_EXTRACT_S1D
    SUM_FTELLU_RECON_ABSO
    SUM_TELLUP_WAVE_TRANS
    SUM_TELLUP_ABSO_SPEC
    SUM_FTELLU_RES_MODEL

