
.. _recipes_spirou_wave:


################################################################################
apero_wave_night_old_spirou.py Recipe
################################################################################


********************************************************************************
1. Description
********************************************************************************


SHORTNAME: WAVE


No description set


********************************************************************************
2. Schematic
********************************************************************************


No schematic set


********************************************************************************
3. Usage
********************************************************************************


.. code-block:: bash

    apero_wave_night_old_spirou.py.py {obs_dir}[STRING] --hcfiles[FILE:HCONE_HCONE] --fpfiles[FILE:FP_FP] {options}


********************************************************************************
4. Optional Arguments
********************************************************************************


.. code-block:: bash

     --database[True/False]
     --badpixfile[FILE:BADPIX]
     --badcorr[True/False]
     --backsub[True/False]
     --blazefile[FILE:FF_BLAZE]
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
     --wavefile[FILE:WAVE_HC,WAVE_FP,WAVEM_D]
     --forceext[True/False]


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
   :file: /data/spirou/bin/apero-drs-full/documentation/working/dev/recipe_definitions/spirou_rout_wave_.csv
   :header-rows: 1
   :class: csvtable


********************************************************************************
8. Debug plots
********************************************************************************


.. code-block:: bash

    WAVENIGHT_ITERPLOT
    WAVENIGHT_HISTPLOT
    WAVEREF_EXPECTED
    CCF_RV_FIT
    CCF_RV_FIT_LOOP
    EXTRACT_S1D
    EXTRACT_S1D_WEIGHT


********************************************************************************
9. Summary plots
********************************************************************************


.. code-block:: bash

    SUM_WAVENIGHT_ITERPLOT
    SUM_WAVENIGHT_HISTPLOT
    SUM_CCF_RV_FIT

