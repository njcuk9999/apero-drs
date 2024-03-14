
.. _user_tools_spirou_get:


################################################################################
apero_get
################################################################################


1. Description
================================================================================


SHORTNAME: GET


.. include:: ../../../resources/spirou/descriptions/apero_get.rst


2. Schematic
================================================================================


No schematic set


3. Usage
================================================================================


.. code-block:: 

    apero_get.py {options}


No optional arguments


4. Optional Arguments
================================================================================


.. code-block:: 

     --assets // Download the assets to the github directory
     --gui // Use a gui to filter files (Currently not ready)
     --outpath[STRING] // This is the directory where copied files will be placed. Must be a valid path and must have permission be able to write.
     --symlinks // Create symlinks to the file instead of copying
     --tar // Whether to create a tar instead of copying files.Must also provide the --tarfile argument
     --tarfile[STRING] // The name of the tar file to create. Must also provide the --tar argument
     --objnames[STRING] // The object names separated by a comma. Use '' for objects with whitespaces i.e 'obj1,obj2,obj 3'
     --dprtypes[STRING] // The DPRTYPES to use (multiple dprtypes combined with OR logic) separate dprtypes with commas. Leaving blank will not use DPRTYPE to filter files.
     --outtypes[STRING] // The drs output file types to use (multiple output type combined  with OR logic) separate output types with commas. Leaving blank will not use output type to filter files.
     --fibers[STRING] // The fibres to use (multiple output type combined  with OR logic) separate fibers with commas. Leaving blank will not use fiber to filter files.
     --since[STRING] // Only get files processed since a certain date YYYY-MM-DD hh:mm:ss
     --latest[STRING] // Only get files processed since a certain date YYYY-MM-DD hh:mm:ss
     --timekey[processed,observed] // Whether to use the processed or observed time in the since and latest arguments (applies to both)
     --obsdir[STRING] // Only get files from a certain observation directory
     --pi_name[STRING] // Only get files from a certain PI
     --runid[STRING] // Only get files from certain run ids
     --failedqc // Include files that failed QC. Highly unrecommended.
     --nosubdir // Do not put files into a sub-directory. Only use thes outpath
     --test // Does not copy files - prints copy as a debug test. Recommended for first time use.
     --sizelimit[INT] // Limit the size of output tarfile (in GB)


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

