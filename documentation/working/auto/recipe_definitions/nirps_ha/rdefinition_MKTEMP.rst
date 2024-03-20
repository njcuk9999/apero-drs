
.. _recipes_nirps_ha_mktemp:


################################################################################
apero_mk_template_nirps_ha
################################################################################


1. Description
================================================================================


SHORTNAME: MKTEMP


No description set


2. Schematic
================================================================================


No schematic set


3. Usage
================================================================================


.. code-block:: 

    apero_mk_template_nirps_ha.py {objname}[STRING] {options}


.. code-block:: 

     {objname}[STRING] // MKTEMP_OBJNAME_HELP


4. Optional Arguments
================================================================================


.. code-block:: 

     --filetype[EXT_E2DS,EXT_E2DS_FF] // MKTEMP_FILETYPE
     --fiber[A,B] // MKTEMP_FIBER
     --database[True/False] // [BOOLEAN] Whether to add outputs to calibration database
     --blazefile[FILE:FF_BLAZE] // BLAZEFILE_HELP
     --plot[0>INT>4] // [INTEGER] Plot level. 0 = off, 1 = interactively, 2 = save to file
     --wavefile[FILE:WAVESOL_REF,WAVE_NIGHT,WAVESOL_DEFAULT] // WAVEFILE_HELP
     --no_in_qc // Disable checking the quality control of input files


5. Special Arguments
================================================================================


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


.. code-block:: 

    DRS_DATA_REDUC // Default: "red" directory


7. Output files
================================================================================


.. csv-table:: Outputs
   :file: rout_MKTEMP.csv
   :header-rows: 1
   :class: csvtable


8. Debug plots
================================================================================


.. code-block:: 

    EXTRACT_S1D
    MKTEMP_BERV_COV
    MKTEMP_S1D_DECONV


9. Summary plots
================================================================================


.. code-block:: 

    SUM_EXTRACT_S1D
    SUM_MKTEMP_BERV_COV

