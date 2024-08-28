
.. _recipes_nirps_ha_ppref:


################################################################################
apero_pp_ref_nirps_ha
################################################################################



Contents
================================================================================

* :ref:`1. Description <desc_nirps_ha_PPREF>`
* :ref:`2. Schematic <schematic_nirps_ha_PPREF>`
* :ref:`3. Usage <usage_nirps_ha_PPREF>`
* :ref:`4. Optional Arguments <optargs_nirps_ha_PPREF>`
* :ref:`5. Special Arguments <spargs_nirps_ha_PPREF>`
* :ref:`6. Output directory <outdir_nirps_ha_PPREF>`
* :ref:`7. Output files <outfiles_nirps_ha_PPREF>`
* :ref:`8. Debug plots <debugplots_nirps_ha_PPREF>`
* :ref:`9. Summary plots <summaryplots_nirps_ha_PPREF>`


1. Description
================================================================================


.. _desc_nirps_ha_PPREF:


SHORTNAME: PPREF


No description set


2. Schematic
================================================================================


.. _schematic_nirps_ha_PPREF:


No schematic set


3. Usage
================================================================================


.. _usage_nirps_ha_PPREF:


.. code-block:: 

    apero_pp_ref_nirps_ha.py {obs_dir}[STRING] {options}


.. code-block:: 

     {obs_dir}[STRING] // [STRING] The directory to find the data files in. Most of the time this is organised by nightly observation directory


4. Optional Arguments
================================================================================


.. _optargs_nirps_ha_PPREF:


.. code-block:: 

     --filetype[STRING] // PP_REF_FILETYPE_HELP


5. Special Arguments
================================================================================


.. _spargs_nirps_ha_PPREF:


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


.. _outdir_nirps_ha_PPREF:


.. code-block:: 

    DRS_DATA_REDUC // Default: "red" directory


7. Output files
================================================================================


.. _outfiles_nirps_ha_PPREF:


.. csv-table:: Outputs
   :file: rout_PPREF.csv
   :header-rows: 1
   :class: csvtable


8. Debug plots
================================================================================


.. _debugplots_nirps_ha_PPREF:


No debug plots.


9. Summary plots
================================================================================


.. _summaryplots_nirps_ha_PPREF:


No summary plots.

