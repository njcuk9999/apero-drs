
.. _recipes_nirps_he_ccf:


################################################################################
apero_ccf_nirps_he
################################################################################



Contents
================================================================================

* :ref:`1. Description <desc_nirps_he_CCF>`
* :ref:`2. Schematic <schematic_nirps_he_CCF>`
* :ref:`3. Usage <usage_nirps_he_CCF>`
* :ref:`4. Optional Arguments <optargs_nirps_he_CCF>`
* :ref:`5. Special Arguments <spargs_nirps_he_CCF>`
* :ref:`6. Output directory <outdir_nirps_he_CCF>`
* :ref:`7. Output files <outfiles_nirps_he_CCF>`
* :ref:`8. Debug plots <debugplots_nirps_he_CCF>`
* :ref:`9. Summary plots <summaryplots_nirps_he_CCF>`


1. Description
================================================================================


.. _desc_nirps_he_CCF:


SHORTNAME: CCF


No description set


2. Schematic
================================================================================


.. _schematic_nirps_he_CCF:


No schematic set


3. Usage
================================================================================


.. _usage_nirps_he_CCF:


.. code-block:: 

    apero_ccf_nirps_he.py {obs_dir}[STRING] [FILE:EXT_E2DS,EXT_E2DS_FF,TELLU_OBJ] {options}


.. code-block:: 

     {obs_dir}[STRING] // [STRING] The directory to find the data files in. Most of the time this is organised by nightly observation directory
     [FILE:EXT_E2DS,EXT_E2DS_FF,TELLU_OBJ] // [STRING/STRINGS] A list of fits files to use separated by spaces. Currently allowed types: E2DS, E2DSFF, TELLU_OBJ (For dprtype = OBJ_FP, OBJ_DARK)


4. Optional Arguments
================================================================================


.. _optargs_nirps_he_CCF:


.. code-block:: 

     --mask[FILE:CCF_MASK] // [STRING] Define the filename to the CCF mask to use. Can be full path or a file in the ./data/spirou/ccf/ folder
     --rv[FLOAT] // [FLOAT] The target RV to use as a center for the CCF fit (in km/s)
     --width[FLOAT] // [FLOAT] The CCF width to use for the CCF fit (in km/s)
     --step[FLOAT] // [FLOAT] The CCF step to use for the CCF fit (in km/s)
     --masknormmode[None,all,order] // [STRING] Define the type of normalization to apply to ccf masks, 'all' normalized across all orders, 'order' normalizes independently for each order, 'None' applies no mask normalization
     --database[True/False] // [BOOLEAN] Whether to add outputs to calibration database
     --blazefile[FILE:FF_BLAZE] // [STRING] Define a custom file to use for blaze correction. If unset uses closest file from calibDB. Checks for an absolute path and then checks 'directory' (CALIBDB=BADPIX)
     --plot[0>INT>4] // [INTEGER] Plot level. 0 = off, 1 = interactively, 2 = save to file
     --no_in_qc // Disable checking the quality control of input files


5. Special Arguments
================================================================================


.. _spargs_nirps_he_CCF:


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


.. _outdir_nirps_he_CCF:


.. code-block:: 

    DRS_DATA_REDUC // Default: "red" directory


7. Output files
================================================================================


.. _outfiles_nirps_he_CCF:


.. csv-table:: Outputs
   :file: rout_CCF.csv
   :header-rows: 1
   :class: csvtable


8. Debug plots
================================================================================


.. _debugplots_nirps_he_CCF:


.. code-block:: 

    CCF_RV_FIT
    CCF_RV_FIT_LOOP
    CCF_SWAVE_REF
    CCF_PHOTON_UNCERT


9. Summary plots
================================================================================


.. _summaryplots_nirps_he_CCF:


.. code-block:: 

    SUM_CCF_PHOTON_UNCERT
    SUM_CCF_RV_FIT

