
.. _recipes_spirou_mktell:


################################################################################
apero_mk_tellu_spirou
################################################################################


********************************************************************************
1. Description
********************************************************************************


SHORTNAME: MKTELL


No description set


********************************************************************************
2. Schematic
********************************************************************************


No schematic set


********************************************************************************
3. Usage
********************************************************************************


.. code-block:: 

    apero_mk_tellu_spirou.py.py {obs_dir}[STRING] [FILE:EXT_E2DS,EXT_E2DS_FF] {options}


.. code-block:: 

     {obs_dir}[STRING] // OBS_DIR_HELP
     [FILE:EXT_E2DS,EXT_E2DS_FF] // [STRING/STRINGS] A list of fits files to use separated by spaces. Currently  allowed types: E2DS, E2DSFF


********************************************************************************
4. Optional Arguments
********************************************************************************


.. code-block:: 

     --database[True/False] // [BOOLEAN] Whether to add outputs to calibration database
     --blazefile[FILE:FF_BLAZE] // [STRING] Define a custom file to use for blaze correction. If unset uses closest file from calibDB. Checks for an absolute path and then checks directory (CALIBDB=BADPIX)
     --plot[-1>INT>2] // [INTEGER] Plot level. 0 = off, 1 = interactively, 2 = save to file
     --wavefile[FILE:WAVE_HC,WAVE_FP,WAVEM_D] // [STRING] Define a custom file to use for the wave solution. If unset uses closest file from header or calibDB (depending on setup). Checks for an absolute path and then checks directory
     --use_template[True/False] // Whether to use the template provided from the telluric database
     --template[FILE:TELLU_TEMP] // Filename of the custom template to use (instead of from telluric database)


********************************************************************************
5. Special Arguments
********************************************************************************


.. code-block:: 

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
   :file: /data/spirou/bin/apero-drs-full/documentation/working/dev/recipe_definitions/spirou_rout_mktell_.csv
   :header-rows: 1
   :class: csvtable


********************************************************************************
8. Debug plots
********************************************************************************


.. code-block:: 

    MKTELLU_WAVE_FLUX1
    MKTELLU_WAVE_FLUX2
    TELLUP_WAVE_TRANS
    TELLUP_ABSO_SPEC
    TELLUP_CLEAN_OH


********************************************************************************
9. Summary plots
********************************************************************************


.. code-block:: 

    SUM_MKTELLU_WAVE_FLUX
    SUM_TELLUP_WAVE_TRANS
    SUM_TELLUP_ABSO_SPEC

