
.. _recipes_spirou_ftelldb:


################################################################################
apero_fit_tellu_db_spirou
################################################################################


********************************************************************************
1. Description
********************************************************************************


SHORTNAME: FTELLDB


No description set


********************************************************************************
2. Schematic
********************************************************************************


No schematic set


********************************************************************************
3. Usage
********************************************************************************


.. code-block:: 

    apero_fit_tellu_db_spirou.py {options}


No optional arguments


********************************************************************************
4. Optional Arguments
********************************************************************************


.. code-block:: 

     --cores[INT] // [INTEGER] The number of cores to use
     --filetype[STRING] // [STRING] optional, the filetype (KW_OUTPUT) to use when processing files
     --fiber[STRING] // [STRING] optional, the fiber type to use when processing files
     --objname[STRING] // [STRING] the object name to process (optional if not set will do all non-telluric objects)
     --dprtype[STRING] // [STRING] the DPRTYPE (i.e. OBJ_FP or OBJ_DARK) used for telluric database. Can be a list (separate by commas)
     --test[True,False,1,0,None] // [BOOLEAN] If True does not process any files just prints an output of what recipes would be run
     --database[True/False] // [BOOLEAN] Whether to add outputs to calibration database
     --plot[0>INT>3] // [INTEGER] Plot level. 0 = off, 1 = interactively, 2 = save to file
     --wavefile[FILE:WAVESOL_REF,WAVE_NIGHT,WAVESOL_DEFAULT] // [STRING] Define a custom file to use for the wave solution. If unset uses closest file from header or calibDB (depending on setup). Checks for an absolute path and then checks directory


********************************************************************************
5. Special Arguments
********************************************************************************


.. code-block:: 

     --xhelp[STRING] // EXTENDED_HELP
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
     --crunfile[STRING] // SET_RUNFILE_HELP
     --quiet[STRING] // Run recipe without start up text
     --nosave[STRING] // SET_NOSAVE_HELP
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



N/A



********************************************************************************
8. Debug plots
********************************************************************************


No debug plots.


********************************************************************************
9. Summary plots
********************************************************************************


No summary plots.

