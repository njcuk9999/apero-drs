
.. _recipes_spirou_shapem:


################################################################################
apero_shape_master_spirou.py Recipe
################################################################################


********************************************************************************
1. Description
********************************************************************************


SHORTNAME: SHAPEM


No description set


********************************************************************************
2. Schematic
********************************************************************************


No schematic set


********************************************************************************
3. Usage
********************************************************************************


.. code-block:: bash

    apero_shape_master_spirou.py.py {obs_dir}[STRING] --fpfiles[FILE:FP_FP] --hcfiles[FILE:HCONE_HCONE] {options}


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
     --locofile[FILE:LOC_LOCO]
     --plot[
     --resize[True/False]
     --fpmaster[FILE:MASTER_FP]


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
   :file: /data/spirou/bin/apero-drs-full/documentation/working/dev/recipe_definitions/spirou_rout_shapem_.csv
   :header-rows: 1
   :class: csvtable


********************************************************************************
8. Debug plots
********************************************************************************


.. code-block:: bash

    SHAPE_DX
    SHAPE_ANGLE_OFFSET_ALL
    SHAPE_ANGLE_OFFSET
    SHAPE_LINEAR_TPARAMS


********************************************************************************
9. Summary plots
********************************************************************************


.. code-block:: bash

    SUM_SHAPE_ANGLE_OFFSET

