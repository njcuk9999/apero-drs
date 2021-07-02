
.. _recipes_spirou_ftellu:


################################################################################
apero_fit_tellu_spirou.py Recipe
################################################################################


********************************************************************************
1. Description
********************************************************************************


SHORTNAME: FTELLU


No description set


********************************************************************************
2. Schematic
********************************************************************************


No schematic set


********************************************************************************
3. Usage
********************************************************************************


.. code-block:: bash

    apero_fit_tellu_spirou.py.py {obs_dir}[STRING] [FILE:EXT_E2DS,EXT_E2DS_FF] {options}


********************************************************************************
4. Optional Arguments
********************************************************************************


.. code-block:: bash

     --use_template[True/False]
     --template[FILE:TELLU_TEMP]
     --database[True/False]
     --blazefile[FILE:FF_BLAZE]
     --plot[
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
   :file: /data/spirou/bin/apero-drs-full/documentation/working/dev/recipe_definitions/spirou_rout_ftellu_.csv
   :header-rows: 1
   :class: csvtable


********************************************************************************
8. Debug plots
********************************************************************************


.. code-block:: bash

    EXTRACT_S1D
    EXTRACT_S1D_WEIGHT
    FTELLU_PCA_COMP1
    FTELLU_PCA_COMP2
    FTELLU_RECON_SPLINE1
    FTELLU_RECON_SPLINE2
    FTELLU_WAVE_SHIFT1
    FTELLU_WAVE_SHIFT2
    FTELLU_RECON_ABSO1
    FTELLU_RECON_ABSO2
    TELLUP_WAVE_TRANS
    TELLUP_ABSO_SPEC
    TELLUP_CLEAN_OH


********************************************************************************
9. Summary plots
********************************************************************************


.. code-block:: bash

    SUM_EXTRACT_S1D
    SUM_FTELLU_RECON_ABSO
    SUM_TELLUP_WAVE_TRANS
    SUM_TELLUP_ABSO_SPEC

