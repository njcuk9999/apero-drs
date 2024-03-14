
.. _user_tools_default_remove:


################################################################################
apero_remove
################################################################################


1. Description
================================================================================


SHORTNAME: REMOVE


No description set


2. Schematic
================================================================================


No schematic set


3. Usage
================================================================================


.. code-block:: 

    apero_remove.py {options}


No optional arguments


4. Optional Arguments
================================================================================


.. code-block:: 

     --obsdir[STRING] // Delete all instances of a certain observation directory from disk and databases
     --file_prefix[STRING] // Delete all instances of a certain file prefix from disk and databases
     --file_suffix[STRING] // Delete all instances of a certain file suffix from disk and databases
     --test[True,False,1,0,None] // Whether to run in test mode (recommended first time)
     --warn[True/False] // Whether to warn the user we are not in test mode.


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
     --nosave[STRING] // Do not save any outputs (debug/information run). Note some recipes require other recipesto be run. Only use --nosave after previous recipe runs have been run successfully at least once.
     --force_indir[STRING] // [STRING] Force the default input directory (Normally set by recipe)
     --force_outdir[STRING] // [STRING] Force the default output directory (Normally set by recipe)


6. Output directory
================================================================================


.. code-block:: 

    DRS_DATA_REDUC // Default: "red" directory


7. Output files
================================================================================



N/A



8. Debug plots
================================================================================


No debug plots.


9. Summary plots
================================================================================


No summary plots.

