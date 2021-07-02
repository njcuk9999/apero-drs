
.. _recipes_spirou_shape:


################################################################################
apero_shape_spirou.py Recipe
################################################################################


********************************************************************************
1. Description
********************************************************************************


SHORTNAME: SHAPE


No description set


********************************************************************************
2. Schematic
********************************************************************************


No schematic set


********************************************************************************
3. Usage
********************************************************************************


.. code-block:: bash

    apero_shape_spirou.py.py {obs_dir}[STRING] [FILE:FP_FP] {options}


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
     --fpmaster[FILE:MASTER_FP]
     --plot[
     --resize[True/False]
     --shapex[FILE:SHAPE_X]
     --shapey[FILE:SHAPE_Y]


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
   :file: /data/spirou/bin/apero-drs-full/documentation/working/dev/recipe_definitions/spirou_rout_shape_.csv
   :header-rows: 1
   :class: csvtable


********************************************************************************
8. Debug plots
********************************************************************************


.. code-block:: bash

    SHAPEL_ZOOM_SHIFT
    SHAPE_LINEAR_TPARAMS


********************************************************************************
9. Summary plots
********************************************************************************


.. code-block:: bash

    SUM_SHAPEL_ZOOM_SHIFT

