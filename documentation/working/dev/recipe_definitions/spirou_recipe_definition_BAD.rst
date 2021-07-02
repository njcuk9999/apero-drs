
.. _recipes_spirou_bad:


################################################################################
apero_badpix_spirou.py Recipe
################################################################################


********************************************************************************
1. Description
********************************************************************************


SHORTNAME: BAD


No description set


********************************************************************************
2. Schematic
********************************************************************************


No schematic set


********************************************************************************
3. Usage
********************************************************************************


.. code-block:: bash

    apero_badpix_spirou.py.py {obs_dir}[STRING] --flatfiles[FILE:FLAT_FLAT] --darkfiles[FILE:DARK_DARK_TEL,DARK_DARK_INT] {options}


********************************************************************************
4. Optional Arguments
********************************************************************************


.. code-block:: bash

     --database[True/False]
     --combine[True/False]
     --flipimage[
     --fluxunits[
     --plot[
     --resize[True/False]


********************************************************************************
5. Special Arguments
********************************************************************************


.. code-block:: bash

     --debug[STRING]
     --listing[STRING]
     --listingall[STRING]
     --version[STRING]
     --info[STRING]
     --program[STRING]
     --recipe_kind[STRING]
     --parallel[STRING]
     --shortname[STRING]
     --idebug[STRING]
     --master[STRING]
     --quiet[STRING]
     --force_indir[STRING]
     --force_outdir[STRING]


********************************************************************************
6. Output directory
********************************************************************************


.. code-block:: bash

    DRS_DATA_REDUC \ Default: "red" directory


********************************************************************************
7. Output files
********************************************************************************


.. csv-table:: Outputs
   :file: /data/spirou/bin/apero-drs-full/documentation/working/dev/recipe_definitions/spirou_rout_bad_.csv
   :header-rows: 1
   :class: csvtable


********************************************************************************
8. Debug plots
********************************************************************************


.. code-block:: bash

    BADPIX_MAP


********************************************************************************
9. Summary plots
********************************************************************************


.. code-block:: bash

    SUM_BADPIX_MAP

