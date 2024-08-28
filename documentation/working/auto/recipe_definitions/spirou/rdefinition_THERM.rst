
.. _recipes_spirou_therm:


################################################################################
apero_thermal_spirou
################################################################################



Contents
================================================================================

* :ref:`1. Description <desc_spirou_THERM>`
* :ref:`2. Schematic <schematic_spirou_THERM>`
* :ref:`3. Usage <usage_spirou_THERM>`
* :ref:`4. Optional Arguments <optargs_spirou_THERM>`
* :ref:`5. Special Arguments <spargs_spirou_THERM>`
* :ref:`6. Output directory <outdir_spirou_THERM>`
* :ref:`7. Output files <outfiles_spirou_THERM>`
* :ref:`8. Debug plots <debugplots_spirou_THERM>`
* :ref:`9. Summary plots <summaryplots_spirou_THERM>`


1. Description
================================================================================


.. _desc_spirou_THERM:


SHORTNAME: THERM


.. include:: ../../../resources/spirou/descriptions/apero_thermal_spirou.rst


2. Schematic
================================================================================


.. _schematic_spirou_THERM:


.. only:: html

    .. figure:: ../../../_static/yed/spirou/apero_thermal_spirou_schematic.jpg
        :figwidth: 100%
        :width: 100%
        :align: center

.. only:: latex

    This section can only currently be viewed in the html documentation.

3. Usage
================================================================================


.. _usage_spirou_THERM:


.. code-block:: 

    apero_thermal_spirou.py {obs_dir}[STRING] [FILE:DARK_DARK_INT,DARK_DARK_TEL] {options}


.. code-block:: 

     {obs_dir}[STRING] // [STRING] The directory to find the data files in. Most of the time this is organised by nightly observation directory
     [FILE:DARK_DARK_INT,DARK_DARK_TEL] // [STRING/STRINGS] A list of fits files to use separated by spaces. Current accepts all preprocessed filetypes. All files used will be combined into a single frame.


4. Optional Arguments
================================================================================


.. _optargs_spirou_THERM:


.. code-block:: 

     --database[True/False] // [BOOLEAN] Whether to add outputs to calibration database
     --badpixfile[FILE:BADPIX] // [STRING] Define a custom file to use for bad pixel correction. Checks for an absolute path and then checks 'directory'
     --badcorr[True/False] // [BOOLEAN] Whether to correct for the bad pixel file
     --backsub[True/False] // [BOOLEAN] Whether to do background subtraction
     --combine[True/False] // [BOOLEAN] Whether to combine fits files in file list or to process them separately
     --darkfile[FILE:DARKREF] // [STRING] The Dark file to use (CALIBDB=DARKM)
     --darkcorr[True/False] // [BOOLEAN] Whether to correct for the dark file
     --fiber[ALL,AB,A,B,C] // [STRING] Define which fibers to extract
     --flipimage[None,x,y,both] // [BOOLEAN] Whether to flip fits image
     --fluxunits[ADU/s,e-] // [STRING] Output units for flux
     --locofile[FILE:LOC_LOCO] // [STRING] Sets the LOCO file used to get the coefficients (CALIBDB=LOC_{fiber})
     --orderpfile[FILE:LOC_ORDERP] // [STRING] Sets the Order Profile file used to get the coefficients (CALIBDB=ORDER_PROFILE_{fiber}
     --plot[0>INT>4] // [INTEGER] Plot level. 0 = off, 1 = interactively, 2 = save to file
     --resize[True/False] // [BOOLEAN] Whether to resize image
     --shapex[FILE:SHAPE_X] // [STRING] Sets the SHAPE DXMAP file used to get the dx correction map (CALIBDB=SHAPEX)
     --shapey[FILE:SHAPE_Y] // [STRING] Sets the SHAPE DYMAP file used to get the dy correction map (CALIBDB=SHAPEY)
     --shapel[FILE:SHAPEL] // [STRING] Sets the SHAPE local file used to get the local transforms (CALIBDB = SHAPEL)
     --wavefile[FILE:WAVESOL_REF,WAVE_NIGHT,WAVESOL_DEFAULT] // [STRING] Define a custom file to use for the wave solution. If unset uses closest file from header or calibDB (depending on setup). Checks for an absolute path and then checks 'directory'
     --no_in_qc // Disable checking the quality control of input files
     --forceext[True/False] // [BOOLEAN] Sets whether to extract input files if files found on disk (defaults to THERMAL_ALWAYS_EXTRACT)


5. Special Arguments
================================================================================


.. _spargs_spirou_THERM:


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


.. _outdir_spirou_THERM:


.. code-block:: 

    DRS_DATA_REDUC // Default: "red" directory


7. Output files
================================================================================


.. _outfiles_spirou_THERM:


.. csv-table:: Outputs
   :file: rout_THERM.csv
   :header-rows: 1
   :class: csvtable


8. Debug plots
================================================================================


.. _debugplots_spirou_THERM:


No debug plots.


9. Summary plots
================================================================================


.. _summaryplots_spirou_THERM:


No summary plots.

