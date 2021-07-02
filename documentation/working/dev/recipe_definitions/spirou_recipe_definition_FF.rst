
.. _recipes_spirou_ff:


################################################################################
apero_flat_spirou.py Recipe
################################################################################


********************************************************************************
1. Description
********************************************************************************


SHORTNAME: FF


No description set


********************************************************************************
2. Schematic
********************************************************************************


No schematic set


********************************************************************************
3. Usage
********************************************************************************


.. code-block:: bash

    apero_flat_spirou.py.py {obs_dir}[STRING] [FILE:FLAT_FLAT] {options}


********************************************************************************
4. Optional Arguments
********************************************************************************


.. code-block:: bash

     --database[True/False]
     --badpixfile[FILE:BADPIX]
     --badcorr[True/False]
     --backsub[True/False]
     --combine[True/False]
     --darkfile[FILE:DARKM]
     --darkcorr[True/False]
     --fiber[
     --flipimage[
     --fluxunits[
     --locofile[FILE:LOC_LOCO]
     --orderpfile[FILE:LOC_ORDERP]
     --plot[
     --resize[True/False]
     --shapex[FILE:SHAPE_X]
     --shapey[FILE:SHAPE_Y]
     --shapel[FILE:SHAPEL]


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
   :file: /data/spirou/bin/apero-drs-full/documentation/working/dev/recipe_definitions/spirou_rout_ff_.csv
   :header-rows: 1
   :class: csvtable


********************************************************************************
8. Debug plots
********************************************************************************


.. code-block:: bash

    FLAT_ORDER_FIT_EDGES1
    FLAT_ORDER_FIT_EDGES2
    FLAT_BLAZE_ORDER1
    FLAT_BLAZE_ORDER2


********************************************************************************
9. Summary plots
********************************************************************************


.. code-block:: bash

    SUM_FLAT_ORDER_FIT_EDGES
    SUM_FLAT_BLAZE_ORDER

