
.. _recipes_spirou_pp:


################################################################################
apero_preprocess_spirou
################################################################################


********************************************************************************
1. Description
********************************************************************************


SHORTNAME: PP


No description set


********************************************************************************
2. Schematic
********************************************************************************


.. only:: html

    .. image:: ../../_static/yed/spirou/apero_preproces_spirou_schematic.jpg
        :width: 100%
        :align: center

.. only:: latex

    This section can only currently be viewed in the html documentation.

********************************************************************************
3. Usage
********************************************************************************


.. code-block:: 

    apero_preprocess_spirou.py.py {obs_dir}[STRING] [FILE:DRS_RAW] {options}


.. code-block:: 

     {obs_dir}[STRING] // OBS_DIR_HELP
     [FILE:DRS_RAW] // Any raw files are currently allowed. Multiple files inputted are handled separately (one after the other).


********************************************************************************
4. Optional Arguments
********************************************************************************


.. code-block:: 

     --skip[True/False] // [BOOLEAN] If True skips preprocessed files that are already found


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

    DRS_DATA_WORKING // Default: "tmp" directory


********************************************************************************
7. Output files
********************************************************************************


.. csv-table:: Outputs
   :file: /data/spirou/bin/apero-drs-full/documentation/working/dev/recipe_definitions/spirou_rout_pp_.csv
   :header-rows: 1
   :class: csvtable


********************************************************************************
8. Debug plots
********************************************************************************


No debug plots.


********************************************************************************
9. Summary plots
********************************************************************************


No summary plots.

