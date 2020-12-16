.. _recipes_spirou_wave_master:

******************************************
Master wavelength solution Recipe
******************************************

Creates a wavelength solution and measures drifts (via CCF) of the FP relative
to the FP master

===========================================
Schematic
===========================================

.. only:: html

    .. image:: ../../../_static/yed/spirou/cal_wave_master_spirou_schematic.jpg

.. only:: latex

    This section can only currently be viewed in the html documentation.

===========================================
Run
===========================================

.. code-block:: bash

    cal_wave_master_spirou.py [DIRECTORY] -hcfiles [HCONE_HCONE] -fpfiles [FP_FP]

===========================================
Optional Arguments
===========================================

.. code-block:: bash

    --database, --badpixfile, --badcorr, --backsub, --blazefile,
    --combine, --darkfile, --darkcorr,  --fiber, --flipimage,
    --fluxunits,  --locofile, --orderpfile, --plot, --resize,
    --shapex, --shapey, --shapel, --wavefile, -hcmode, -fpmode,
    --forceext,
    --debug, --listing, --listingall, --version, --info,
    --program, --idebug, --breakpoints, --quiet, --help

===========================================
Output Dir
===========================================

.. code-block:: bash

    DRS_DATA_REDUC   \\ default "reduced" directory

===========================================
Calibration database entry
===========================================

.. code-block:: bash

    WAVEM_{FIBER} {NIGHT_NAME} {FILENAME} {HUMAN DATE} {UNIX DATE}
    WAVEHCL_{FIBER} {NIGHT_NAME} {FILENAME} {HUMAN DATE} {UNIX DATE}
    WAVEFPL_{FIBER} {NIGHT_NAME} {FILENAME} {HUMAN DATE} {UNIX DATE}

===========================================
Output files
===========================================

.. code-block:: bash

    {ODOMETER_CODE}_pp_e2ds_{FIBER}.fits              \\ extracted + flat field file (49x4088)
    {ODOMETER_CODE}_pp_e2dsff_{FIBER}.fits            \\ extracted + flat field file (49x4088)
    {ODOMETER_CODE}_pp_s1d_w_{FIBER}.fits             \\ s1d constant in pixel space (FITS-TABLE)
    {ODOMETER_CODE}_pp_s1d_v_{FIBER}.fits             \\ s1d constant in velocity space (FITS-TABLE)
    DEBUG_{ODOMETER_CODE}_pp_e2dsll_{FIBER}.fits      \\ debug pre extract file (7x3100x4088)
    DEBUG_{ODOMETER_CODE}_pp_background.fits          \\ debug background file (7x3100x4088)

    {ODOMETER_CODE}_pp_e2dsff_linelist_{FIBER}.dat      \\ wave stats hc line list
    {ODOMETER_CODE}_pp_e2dsff_wavemres_{FIBER}.fits     \\ wave res table (multi extension fits)
    {ODOMETER_CODE}_pp_e2dsff_wavem_hc_{FIBER}.fits     \\ wave solution from hc only (49x4088)
    {ODOMETER_CODE}_pp_e2dsff_wavem_fp_{FIBER}.fits     \\ wave solution from hc + fp (49x4088)
    cal_wave_results.tbl                                \\ wave res table (ASCII-table)
    {ODOMETER_CODE}_pp_e2dsff_mhc_lines_{FIBER}.tbl     \\ wave hc lines (ASCII-table)
    {ODOMETER_CODE}_pp_wavem_hclines_{FIBER}.fits       \\ wave hc ref/measured lines table (FITS-TABLE)
    {ODOMETER_CODE}_pp_wavem_fplines_{FIBER}.fits      \\ wave fp ref/measured lines table (FITS-TABLE)
    {ODOMETER_CODE}_pp_e2dsff_ccf_{FIBER}.fits          \\ ccf code [FITS-TABLE]


===========================================
Plots
===========================================

.. code-block:: bash

    WAVE_HC_GUESS, WAVE_HC_BRIGHTEST_LINES, WAVE_HC_TFIT_GRID, WAVE_HC_RESMAP, WAVE_LITTROW_CHECK1,
    WAVE_LITTROW_EXTRAP1, WAVE_LITTROW_CHECK2, WAVE_LITTROW_EXTRAP2, WAVE_FP_FINAL_ORDER,
    WAVE_FP_LWID_OFFSET, WAVE_FP_WAVE_RES, WAVE_FP_M_X_RES, WAVE_FP_IPT_CWID_1MHC, WAVE_FP_IPT_CWID_LLHC,
    WAVE_FP_LL_DIFF, WAVE_FP_MULTI_ORDER, WAVE_FP_SINGLE_ORDER, CCF_RV_FIT, CCF_RV_FIT_LOOP, WAVEREF_EXPECTED,
    EXTRACT_S1D, EXTRACT_S1D_WEIGHT, WAVE_FIBER_COMPARISON, WAVE_FIBER_COMP, WAVENIGHT_ITERPLOT, WAVENIGHT_HISTPLOT
