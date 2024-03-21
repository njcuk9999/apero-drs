
.. _user_tools_default_reset:


################################################################################
apero_reset
################################################################################



Contents
================================================================================

* :ref:`1. Description <desc_default_RESET>`
* :ref:`2. Schematic <schematic_default_RESET>`
* :ref:`3. Usage <usage_default_RESET>`
* :ref:`4. Optional Arguments <optargs_default_RESET>`
* :ref:`5. Special Arguments <spargs_default_RESET>`
* :ref:`6. Output directory <outdir_default_RESET>`
* :ref:`7. Output files <outfiles_default_RESET>`
* :ref:`8. Debug plots <debugplots_default_RESET>`
* :ref:`9. Summary plots <summaryplots_default_RESET>`


1. Description
================================================================================


.. _desc_default_RESET:


SHORTNAME: RESET


.. include:: ../../../resources/default/descriptions/apero_reset.rst


2. Schematic
================================================================================


.. _schematic_default_RESET:


No schematic set


3. Usage
================================================================================


.. _usage_default_RESET:


.. code-block:: 

    apero_reset.py {options}


No optional arguments


4. Optional Arguments
================================================================================


.. _optargs_default_RESET:


.. code-block:: 

     --nolog // [BOOLEAN] If True logs the reset else is quite
     --nowarn // [BOOLEAN] If True asks for user to type 'YES' before each reset
     --database_timeout[INT] // [INTEGER] Set the database timeout number of tries
     --only_assets // Reset only the assets directory
     --only_tmp // Reset only the tmp directory
     --only_red // Reset only the reduced directory
     --only_calib // Reset only the calibration directory
     --only_tellu // Reset only the telluric directory
     --only_log // Reset only the log directory
     --only_plot // Reset only the plot directory
     --only_run // Reset only the run directory
     --only_lbl // Reset only the lbl directory
     --only_out // Reset only the out directory
     --only_other // Reset only the other directory


5. Special Arguments
================================================================================


.. _spargs_default_RESET:


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


.. _outdir_default_RESET:


.. code-block:: 

    DRS_DATA_REDUC // Default: "red" directory


7. Output files
================================================================================


.. _outfiles_default_RESET:



N/A



8. Debug plots
================================================================================


.. _debugplots_default_RESET:


No debug plots.


9. Summary plots
================================================================================


.. _summaryplots_default_RESET:


No summary plots.

