Run all nightly science target steps.

This should be run after preprocessing of (at least) all science stars hot star files for all nights being reduced.

Include the following recipes:

    - EXTOBJ: Extracts all science target files
    - FTFIT1: Correct for telluric absorption in all science target files (without template)
    - FTTEMP1: Make a template for all science targets (using science files from FTFIT1)
    - FTFIT2: Correct for telluric absorption in all science target files (with template)
    - FTTEMP2: Make a template for all science targets (using science files from FTFIT2)
    - CCF: Calculate an estimate of RV based on the CCF for all science target files
    - POLAR: Calculate the polarization for all science target files (only calculated for those in polarimetry mode)
    - SCIPOST: Post-process all science target files