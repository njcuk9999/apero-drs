
.. _recipes_spirou_loc:


################################################################################
apero_loc_spirou.py Recipe
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


.. code-block:: bash

    apero_loc_spirou.py.py {obs_dir}[STRING] [FILE:DARK_FLAT,FLAT_DARK] {options}


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
   :file: /data/spirou/bin/apero-drs-full/documentation/working/dev/recipe_definitions/spirou_rout_loc_.csv
   :header-rows: 1
   :class: csvtable


********************************************************************************
8. Debug plots
********************************************************************************


.. code-block:: bash

    LOC_WIDTH_REGIONS
    LOC_FIBER_DOUBLET_PARITY
    LOC_GAP_ORDERS
    LOC_IMAGE_FIT
    LOC_IM_CORNER


********************************************************************************
9. Summary plots
********************************************************************************


.. code-block:: bash

    SUM_LOC_IM_FIT
    SUM_LOC_IM_CORNER

