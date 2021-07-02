
.. _recipes_spirou_ext:


################################################################################
apero_extract_spirou.py Recipe
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


.. code-block:: bash

    apero_extract_spirou.py.py {obs_dir}[STRING] [FILE:DRS_PP] {options}


********************************************************************************
4. Optional Arguments
********************************************************************************


.. code-block:: bash

     --quicklook[True/False]
     --badpixfile[FILE:BADPIX]
     --badcorr[True/False]
     --backsub[True/False]
     --blazefile[FILE:FF_BLAZE]
     --combine[True/False]
     --objname[STRING]
     --dprtype[STRING]
     --darkfile[FILE:DARKM]
     --darkcorr[True/False]
     --fiber[
     --flipimage[
     --fluxunits[
     --flatfile[FILE:FF_FLAT]
     --locofile[FILE:LOC_LOCO]
     --orderpfile[FILE:LOC_ORDERP]
     --plot[
     --resize[True/False]
     --shapex[FILE:SHAPE_X]
     --shapey[FILE:SHAPE_Y]
     --shapel[FILE:SHAPEL]
     --thermal[True/False]
     --thermalfile[FILE:THERMALI_E2DS,THERMALT_E2DS]
     --wavefile[FILE:WAVE_HC,WAVE_FP,WAVEM_D]


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
   :file: /data/spirou/bin/apero-drs-full/documentation/working/dev/recipe_definitions/spirou_rout_ext_.csv
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
    THERMAL_BACKGROUND
    EXTRACT_SPECTRAL_ORDER1
    EXTRACT_SPECTRAL_ORDER2
    EXTRACT_S1D
    EXTRACT_S1D_WEIGHT


********************************************************************************
9. Summary plots
********************************************************************************


.. code-block:: bash

    SUM_FLAT_ORDER_FIT_EDGES
    SUM_EXTRACT_SP_ORDER
    SUM_EXTRACT_S1D

