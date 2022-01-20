
.. _recipes_spirou_bad:


################################################################################
apero_badpix_spirou
################################################################################


********************************************************************************
1. Description
********************************************************************************


SHORTNAME: BAD


No description set


********************************************************************************
2. Schematic
********************************************************************************


.. only:: html

    .. image:: ../../../_static/yed/spirou/apero_badpix_spirou_schematic.jpg
        :width: 100%
        :align: center

.. only:: latex

    This section can only currently be viewed in the html documentation.

********************************************************************************
3. Usage
********************************************************************************


.. code-block:: 

    apero_badpix_spirou.py.py {obs_dir}[STRING] --flatfiles[FILE:FLAT_FLAT] --darkfiles[FILE:DARK_DARK_TEL,DARK_DARK_INT] {options}


.. code-block:: 

     {obs_dir}[STRING] // OBS_DIR_HELP
     --flatfiles[FILE:FLAT_FLAT] // BADPIX_FLATFILE_HELP
     --darkfiles[FILE:DARK_DARK_TEL,DARK_DARK_INT] // BADPIX_DARKFILE_HELP


********************************************************************************
4. Optional Arguments
********************************************************************************


.. code-block:: 

     --database[True/False] // [BOOLEAN] Whether to add outputs to calibration database
     --combine[True/False] // COMBINE_HELP
     --flipimage[None,x,y,both] // FLIPIMAGE_HELP
     --fluxunits[ADU/s,e-] // FLUXUNITS_HELP
     --plot[-1>INT>2] // [INTEGER] Plot level. 0 = off, 1 = interactively, 2 = save to file
     --resize[True/False] // RESIZE_HELP


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
   :file: rout_BAD.csv
   :header-rows: 1
   :class: csvtable


********************************************************************************
8. Debug plots
********************************************************************************


.. code-block:: 

    BADPIX_MAP


********************************************************************************
9. Summary plots
********************************************************************************


.. code-block:: 

    SUM_BADPIX_MAP

