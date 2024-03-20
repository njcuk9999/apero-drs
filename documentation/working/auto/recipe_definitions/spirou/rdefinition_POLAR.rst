
.. _recipes_spirou_polar:


################################################################################
apero_pol_spirou
################################################################################


1. Description
================================================================================


SHORTNAME: POLAR


.. include:: ../../../resources/spirou/descriptions/apero_pol_spirou.rst


2. Schematic
================================================================================


No schematic set


3. Usage
================================================================================


.. code-block:: 

    apero_pol_spirou.py {obs_dir}[STRING] {options}


.. code-block:: 

     {obs_dir}[STRING] // OBS_DIR_HELP


4. Optional Arguments
================================================================================


.. code-block:: 

     --exposures[FILE:EXT_E2DS_FF,TELLU_OBJ] // List of exposures to add (order determined by recipe)
     --exp1[FILE:EXT_E2DS_FF,TELLU_OBJ] // Override input exposure 1
     --exp2[FILE:EXT_E2DS_FF,TELLU_OBJ] // Override input exposure 2
     --exp3[FILE:EXT_E2DS_FF,TELLU_OBJ] // Override input exposure 3
     --exp4[FILE:EXT_E2DS_FF,TELLU_OBJ] // Override input exposure 4
     --objrv[FLOAT] // Object radial velocity [km/s]
     --lsdmask[STRING] // LSD mask
     --output[STRING] // Output file
     --output_lsd[STRING] // Output LSD file
     --lsd // Run LSD analysis
     --noqccheck // Do not check quality control of inputs
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
   :file: rout_POLAR.csv
   :header-rows: 1
   :class: csvtable


8. Debug plots
================================================================================


.. code-block:: 

    POLAR_FIT_CONT
    POLAR_CONTINUUM
    POLAR_RESULTS
    POLAR_STOKES_I
    POLAR_LSD
    EXTRACT_S1D_WEIGHT
    EXTRACT_S1D


9. Summary plots
================================================================================


.. code-block:: 

    SUM_EXTRACT_S1D

