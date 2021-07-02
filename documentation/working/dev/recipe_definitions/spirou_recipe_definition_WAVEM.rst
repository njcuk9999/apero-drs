
.. _recipes_spirou_wavem:


################################################################################
apero_wave_master_old_spirou.py Recipe
################################################################################


********************************************************************************
1. Description
********************************************************************************


SHORTNAME: WAVEM


No description set


********************************************************************************
2. Schematic
********************************************************************************


No schematic set


********************************************************************************
3. Usage
********************************************************************************


.. code-block:: bash

    apero_wave_master_old_spirou.py.py {obs_dir}[STRING] --hcfiles[FILE:HCONE_HCONE] --fpfiles[FILE:FP_FP] {options}


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
     --hcmode[
     --fpmode[


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
   :file: /data/spirou/bin/apero-drs-full/documentation/working/dev/recipe_definitions/spirou_rout_wavem_.csv
   :header-rows: 1
   :class: csvtable


********************************************************************************
8. Debug plots
********************************************************************************


.. code-block:: bash

    WAVE_HC_GUESS
    WAVE_HC_BRIGHTEST_LINES
    WAVE_HC_TFIT_GRID
    WAVE_HC_RESMAP
    WAVE_LITTROW_CHECK1
    WAVE_LITTROW_EXTRAP1
    WAVE_LITTROW_CHECK2
    WAVE_LITTROW_EXTRAP2
    WAVE_FP_FINAL_ORDER
    WAVE_FP_LWID_OFFSET
    WAVE_FP_WAVE_RES
    WAVE_FP_M_X_RES
    WAVE_FP_IPT_CWID_1MHC
    WAVE_FP_IPT_CWID_LLHC
    WAVE_FP_LL_DIFF
    WAVE_FP_MULTI_ORDER
    WAVE_FP_SINGLE_ORDER
    CCF_RV_FIT
    CCF_RV_FIT_LOOP
    WAVEREF_EXPECTED
    EXTRACT_S1D
    EXTRACT_S1D_WEIGHT
    WAVE_FIBER_COMPARISON
    WAVE_FIBER_COMP
    WAVENIGHT_ITERPLOT
    WAVENIGHT_HISTPLOT


********************************************************************************
9. Summary plots
********************************************************************************


.. code-block:: bash

    SUM_WAVE_FP_IPT_CWID_LLHC
    SUM_WAVE_LITTROW_CHECK
    SUM_WAVE_LITTROW_EXTRAP
    SUM_CCF_RV_FIT
    SUM_WAVE_FIBER_COMP
    SUM_WAVENIGHT_ITERPLOT
    SUM_WAVENIGHT_HISTPLOT

