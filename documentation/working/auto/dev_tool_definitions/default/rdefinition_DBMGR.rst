
.. _dev_tools_default_dbmgr:


################################################################################
apero_database
################################################################################


********************************************************************************
1. Description
********************************************************************************


SHORTNAME: DBMGR


.. include:: ../../../resources/default/descriptions/apero_database.rst


********************************************************************************
2. Schematic
********************************************************************************


No schematic set


********************************************************************************
3. Usage
********************************************************************************


.. code-block:: 

    apero_database.py {options}


No optional arguments


********************************************************************************
4. Optional Arguments
********************************************************************************


.. code-block:: 

     --kill // Use this when database is stuck and you have no other opens (mysql only)
     --objdb[STRING] // [True] or [str Path to dfits output]. Update the object reset database using raw directory [True] or a dfits output [str]
     --update // Use this to update the database based on files on disk in the correct directories (Currently updates calib/tellu/log and index databases)
     --csv[STRING] // Path to csv file. For --importdb this is the csv file you wish to add. For --exportdb this is the csv file that will be saved.
     --exportdb[calib,tellu,index,log,object,lang] // Export a database to a csv file
     --importdb[calib,tellu,index,log,object,lang] // Import a csv file into a database
     --join[replace,append] // How to add the csv file to database: append adds all lines to the end of current database, replace removes all previous lines from database. Default is replace.
     --delete // Load up the delete table GUI (MySQL only)


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



N/A



********************************************************************************
8. Debug plots
********************************************************************************


No debug plots.


********************************************************************************
9. Summary plots
********************************************************************************


No summary plots.

