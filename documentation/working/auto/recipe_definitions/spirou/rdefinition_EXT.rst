
.. _recipes_spirou_ext:


################################################################################
apero_extract_spirou
################################################################################


********************************************************************************
1. Description
********************************************************************************


SHORTNAME: EXT


No description set


********************************************************************************
2. Schematic
********************************************************************************


No schematic set


********************************************************************************
3. Usage
********************************************************************************


.. code-block:: 

    apero_extract_spirou.py.py {obs_dir}[STRING] [FILE:DRS_PP] {options}


.. code-block:: 

     {obs_dir}[STRING] // OBS_DIR_HELP
     [FILE:DRS_PP] // [STRING/STRINGS] A list of fits files to use separated by spaces. EXTRACT_FILES_HELP


********************************************************************************
4. Optional Arguments
********************************************************************************


.. code-block:: 

     --quicklook[True/False] // QUICK_LOOK_EXT_HELP
     --badpixfile[FILE:BADPIX] // BADFILE_HELP
     --badcorr[True/False] // DOBAD_HELP
     --backsub[True/False] // BACKSUB_HELP
     --blazefile[FILE:FF_BLAZE] // BLAZEFILE_HELP
     --combine[True/False] // COMBINE_HELP
     --combine_method[STRING] // Method to combine files (if --combine=True)
     --objname[STRING] // OBJNAME_HELP
     --dprtype[STRING] // DPRTYPE_HELP
     --darkfile[FILE:DARKM] // DARKFILE_HELP
     --darkcorr[True/False] // DODARK_HELP
     --fiber[ALL,AB,A,B,C] // EXTFIBER_HELP
     --flipimage[None,x,y,both] // FLIPIMAGE_HELP
     --fluxunits[ADU/s,e-] // FLUXUNITS_HELP
     --flatfile[FILE:FF_FLAT] // FLATFILE_HELP
     --locofile[FILE:LOC_LOCO] // LOCOFILE_HELP
     --orderpfile[FILE:LOC_ORDERP] // ORDERPFILE_HELP
     --plot[-1>INT>2] // [INTEGER] Plot level. 0 = off, 1 = interactively, 2 = save to file
     --resize[True/False] // RESIZE_HELP
     --shapex[FILE:SHAPE_X] // SHAPEXFILE_HELP
     --shapey[FILE:SHAPE_Y] // SHAPEYFILE_HELP
     --shapel[FILE:SHAPEL] // SHAPELFILE_HELP
     --leakcorr[True/False] // LEAKCORR_HELP
     --thermal[True/False] // THERMAL_HELP
     --thermalfile[FILE:THERMALI_E2DS,THERMALT_E2DS] // THERMALFILE_HELP
     --wavefile[FILE:WAVESOL_MASTER,WAVE_NIGHT,WAVESOL_DEFAULT] // WAVEFILE_HELP


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
   :file: rout_EXT.csv
   :header-rows: 1
   :class: csvtable


********************************************************************************
8. Debug plots
********************************************************************************


.. code-block:: 

    FLAT_ORDER_FIT_EDGES1
    FLAT_ORDER_FIT_EDGES2
    FLAT_BLAZE_ORDER1
    FLAT_BLAZE_ORDER2
    THERMAL_BACKGROUND
    EXTRACT_SPECTRAL_ORDER1
    EXTRACT_SPECTRAL_ORDER2
    EXTRACT_S1D
    EXTRACT_S1D_WEIGHT


********************************************************************************
9. Summary plots
********************************************************************************


.. code-block:: 

    SUM_FLAT_ORDER_FIT_EDGES
    SUM_EXTRACT_SP_ORDER
    SUM_EXTRACT_S1D

