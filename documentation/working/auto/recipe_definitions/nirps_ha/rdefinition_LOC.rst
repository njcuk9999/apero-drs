
.. _recipes_nirps_ha_loc:


################################################################################
apero_loc_nirps_ha
################################################################################


********************************************************************************
1. Description
********************************************************************************


SHORTNAME: LOC


No description set


********************************************************************************
2. Schematic
********************************************************************************


No schematic set


********************************************************************************
3. Usage
********************************************************************************


.. code-block:: 

    apero_loc_nirps_ha.py {obs_dir}[STRING] [FILE:DARK_FLAT,FLAT_DARK] {options}


.. code-block:: 

     {obs_dir}[STRING] // OBS_DIR_HELP
     [FILE:DARK_FLAT,FLAT_DARK] // [STRING/STRINGS] A list of fits files to use separated by spaces. Current allowed types: DARK_FLAT OR FLAT_DARK but not both (exclusive)


********************************************************************************
4. Optional Arguments
********************************************************************************


.. code-block:: 

     --database[True/False] // [BOOLEAN] Whether to add outputs to calibration database
     --badpixfile[FILE:BADPIX] // [STRING] Define a custom file to use for bad pixel correction. Checks for an absolute path and then checks directory
     --badcorr[True/False] // [BOOLEAN] Whether to correct for the bad pixel file
     --backsub[True/False] // [BOOLEAN] Whether to do background subtraction
     --combine[True/False] // [BOOLEAN] Whether to combine fits files in file list or to process them separately
     --darkfile[FILE:DARKREF] // [STRING] The Dark file to use (CALIBDB=DARKM)
     --darkcorr[True/False] // [BOOLEAN] Whether to correct for the dark file
     --flipimage[None,x,y,both] // [BOOLEAN] Whether to flip fits image
     --fluxunits[ADU/s,e-] // [STRING] Output units for flux
     --plot[0>INT>3] // [INTEGER] Plot level. 0 = off, 1 = interactively, 2 = save to file
     --resize[True/False] // [BOOLEAN] Whether to resize image


********************************************************************************
5. Special Arguments
********************************************************************************


.. code-block:: 

     --xhelp[STRING] // EXTENDED_HELP
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
     --crunfile[STRING] // SET_RUNFILE_HELP
     --quiet[STRING] // Run recipe without start up text
     --nosave[STRING] // SET_NOSAVE_HELP
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
   :file: rout_LOC.csv
   :header-rows: 1
   :class: csvtable


********************************************************************************
8. Debug plots
********************************************************************************


.. code-block:: 

    LOC_WIDTH_REGIONS
    LOC_FIBER_DOUBLET_PARITY
    LOC_GAP_ORDERS
    LOC_IMAGE_FIT
    LOC_IM_CORNER
    LOC_IM_REGIONS


********************************************************************************
9. Summary plots
********************************************************************************


.. code-block:: 

    SUM_LOC_IM_FIT
    SUM_LOC_IM_CORNER

