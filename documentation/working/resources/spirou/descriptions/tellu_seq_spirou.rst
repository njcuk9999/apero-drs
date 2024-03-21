Run all nightly hot star telluric calibrations steps.

This should be run after preprocessing of (at least) all telluric hot star files for all nights being reduced.
This should also be run after all calibration (reference and nightly) steps have been done.

Include the following recipes:

    - EXTTELL: Extracts all hot star files
    - MKTELLU1: First pass at making hot star trans files
    - MKTMOD1: Combines all hot star trans files from MKTELLU1 into a telluric model
    - MKFIT1: Correct for telluric absorption in the hot star files (without template)
    - MKTEMP1: Make a template for the hot star files (using hot stars from MKFIT1)
    - MKTELLU2: Second pass at making hot star trans files (with corrected hot stars + template)
    - MKTMOD2: Combines all hot star trans files from MKTELLU2 into a telluric model
    - MKTFIT2: Correct for telluric absorption in the hot star files (with template)
    - MKTEMP2: Make a template for the hot star files (with corrected hot stars from MKTFIT2)
