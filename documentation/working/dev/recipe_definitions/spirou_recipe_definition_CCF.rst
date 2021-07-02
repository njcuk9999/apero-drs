
.. _recipes_spirou_ccf:


################################################################################
apero_ccf_spirou.py Recipe
################################################################################


********************************************************************************
1. Description
********************************************************************************


SHORTNAME: CCF


No description set


********************************************************************************
2. Schematic
********************************************************************************


No schematic set


********************************************************************************
3. Usage
********************************************************************************


.. code-block:: bash

    apero_ccf_spirou.py.py {obs_dir}[STRING] [FILE:EXT_E2DS,EXT_E2DS_FF,TELLU_OBJ] {options}


********************************************************************************
4. Optional Arguments
********************************************************************************


.. code-block:: bash

     --mask[FILE:CCF_MASK]
     --rv[
     --width[
     --step[
     --masknormmode[
     --database[True/False]
     --blazefile[FILE:FF_BLAZE]
     --plot[


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
   :file: /data/spirou/bin/apero-drs-full/documentation/working/dev/recipe_definitions/spirou_rout_ccf_.csv
   :header-rows: 1
   :class: csvtable


********************************************************************************
8. Debug plots
********************************************************************************


.. code-block:: bash

    CCF_RV_FIT
    CCF_RV_FIT_LOOP
    CCF_SWAVE_REF
    CCF_PHOTON_UNCERT


********************************************************************************
9. Summary plots
********************************************************************************


.. code-block:: bash

    SUM_CCF_PHOTON_UNCERT
    SUM_CCF_RV_FIT

