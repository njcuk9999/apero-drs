
.. _user_tools_default_precheck:


################################################################################
apero_precheck
################################################################################



Contents
================================================================================

* :ref:`1. Description <desc_default_PRECHECK>`
* :ref:`2. Schematic <schematic_default_PRECHECK>`
* :ref:`3. Usage <usage_default_PRECHECK>`
* :ref:`4. Optional Arguments <optargs_default_PRECHECK>`
* :ref:`5. Special Arguments <spargs_default_PRECHECK>`
* :ref:`6. Output directory <outdir_default_PRECHECK>`
* :ref:`7. Output files <outfiles_default_PRECHECK>`
* :ref:`8. Debug plots <debugplots_default_PRECHECK>`
* :ref:`9. Summary plots <summaryplots_default_PRECHECK>`


1. Description
================================================================================


.. _desc_default_PRECHECK:


SHORTNAME: PRECHECK


.. include:: ../../../resources/default/descriptions/apero_precheck.rst


2. Schematic
================================================================================


.. _schematic_default_PRECHECK:


No schematic set


3. Usage
================================================================================


.. _usage_default_PRECHECK:


.. code-block:: 

    apero_precheck.py {runfile}[STRING] {options}


.. code-block:: 

     {runfile}[STRING] // [STRING] The run file to use in reprocessing


4. Optional Arguments
================================================================================


.. _optargs_default_PRECHECK:


.. code-block:: 

     --obs_dir[STRING] // PROCESS_OBS_DIR_HELP
     --exclude_obs_dirs[STRING] // PROCESS_EXCLUDE_OBS_DIRS_HELP
     --include_obs_dirs[STRING] // PROCESS_INCLUDE_OBS_DIRS_HELP
     --no_file_check // Don’t check the number of files on disk and don’t flag these errors
     --no_obj_check // Don’t check object database with current set of raw files and don’t flag these errors


5. Special Arguments
================================================================================


.. _spargs_default_PRECHECK:


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


.. _outdir_default_PRECHECK:


.. code-block:: 

    DRS_DATA_REDUC // Default: "red" directory


7. Output files
================================================================================


.. _outfiles_default_PRECHECK:



N/A



8. Debug plots
================================================================================


.. _debugplots_default_PRECHECK:


No debug plots.


9. Summary plots
================================================================================


.. _summaryplots_default_PRECHECK:


No summary plots.

