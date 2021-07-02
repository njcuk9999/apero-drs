
.. _recipes_spirou_mktemp:


################################################################################
apero_mk_template_spirou.py Recipe
################################################################################


********************************************************************************
1. Description
********************************************************************************


SHORTNAME: MKTEMP


No description set


********************************************************************************
2. Schematic
********************************************************************************


No schematic set


********************************************************************************
3. Usage
********************************************************************************


.. code-block:: bash

    apero_mk_template_spirou.py.py {objname}[STRING] {options}


********************************************************************************
4. Optional Arguments
********************************************************************************


.. code-block:: bash

     --filetype[
     --fiber[
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
   :file: /data/spirou/bin/apero-drs-full/documentation/working/dev/recipe_definitions/spirou_rout_mktemp_.csv
   :header-rows: 1
   :class: csvtable


********************************************************************************
8. Debug plots
********************************************************************************


.. code-block:: bash

    EXTRACT_S1D
    MKTEMP_BERV_COV


********************************************************************************
9. Summary plots
********************************************************************************


.. code-block:: bash

    SUM_EXTRACT_S1D
    SUM_MKTEMP_BERV_COV

