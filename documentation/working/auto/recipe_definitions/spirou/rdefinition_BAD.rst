
.. _recipes_spirou_bad:


################################################################################
apero_badpix_spirou
################################################################################



Contents
================================================================================

* :ref:`1. Description <desc_spirou_BAD>`
* :ref:`2. Schematic <schematic_spirou_BAD>`
* :ref:`3. Usage <usage_spirou_BAD>`
* :ref:`4. Optional Arguments <optargs_spirou_BAD>`
* :ref:`5. Special Arguments <spargs_spirou_BAD>`
* :ref:`6. Output directory <outdir_spirou_BAD>`
* :ref:`7. Output files <outfiles_spirou_BAD>`
* :ref:`8. Debug plots <debugplots_spirou_BAD>`
* :ref:`9. Summary plots <summaryplots_spirou_BAD>`


1. Description
================================================================================


.. _desc_spirou_BAD:


SHORTNAME: BAD


.. include:: ../../../resources/spirou/descriptions/apero_badpix_spirou.rst


2. Schematic
================================================================================


.. _schematic_spirou_BAD:


.. only:: html

    .. figure:: ../../../_static/yed/spirou/apero_badpix_spirou_schematic.jpg
        :figwidth: 100%
        :width: 100%
        :align: center

.. only:: latex

    This section can only currently be viewed in the html documentation.

3. Usage
================================================================================


.. _usage_spirou_BAD:


.. code-block:: 

    apero_badpix_spirou.py {obs_dir}[STRING] --flatfiles[FILE:FLAT_FLAT] --darkfiles[FILE:DARK_DARK_TEL,DARK_DARK_INT] {options}


.. code-block:: 

     {obs_dir}[STRING] // [STRING] The directory to find the data files in. Most of the time this is organised by nightly observation directory
     --flatfiles[FILE:FLAT_FLAT] // Current allowed types: FLAT_FLAT
     --darkfiles[FILE:DARK_DARK_TEL,DARK_DARK_INT] // Current allowed types: DARK_DARK


4. Optional Arguments
================================================================================


.. _optargs_spirou_BAD:


.. code-block:: 

     --database[True/False] // [BOOLEAN] Whether to add outputs to calibration database
     --combine[True/False] // [BOOLEAN] Whether to combine fits files in file list or to process them separately
     --flipimage[None,x,y,both] // [BOOLEAN] Whether to flip fits image
     --fluxunits[ADU/s,e-] // [STRING] Output units for flux
     --plot[0>INT>4] // [INTEGER] Plot level. 0 = off, 1 = interactively, 2 = save to file
     --resize[True/False] // [BOOLEAN] Whether to resize image
     --no_in_qc // Disable checking the quality control of input files


5. Special Arguments
================================================================================


.. _spargs_spirou_BAD:


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


.. _outdir_spirou_BAD:


.. code-block:: 

    DRS_DATA_REDUC // Default: "red" directory


7. Output files
================================================================================


.. _outfiles_spirou_BAD:


.. csv-table:: Outputs
   :file: rout_BAD.csv
   :header-rows: 1
   :class: csvtable


8. Debug plots
================================================================================


.. _debugplots_spirou_BAD:


.. code-block:: 

    BADPIX_MAP


9. Summary plots
================================================================================


.. _summaryplots_spirou_BAD:


.. code-block:: 

    SUM_BADPIX_MAP

