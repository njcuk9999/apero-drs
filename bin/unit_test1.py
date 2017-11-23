#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-11-23 at 12:14

@author: cook



Version 0.0.0
"""
from __future__ import division
import time

import cal_DARK_spirou
import cal_loc_RAW_spirou
import cal_SLIT_spirou
import cal_FF_RAW_spirou
import cal_extract_RAW_spirou
import cal_DRIFT_RAW_spirou
import matplotlib.pyplot as plt

# =============================================================================
# Define variables
# =============================================================================
NIGHT_NAME = '20170710'

UNITTEST = '{0}{1}{2}UNIT TEST {3}: {4}{2}{1}{0}'

# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # set up time dictionary
    times = dict()
    # start total timer
    starttotaltime = time.time()
    # iterator
    test = 1
    # print starting unit tests
    print('\n\n\n START OF UNIT TESTS \n\n\n')
    # ----------------------------------------------------------------------
    # test cal_dark_spirou
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_DARK_spirou'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # set up files
    files = ['dark_dark02d406.fits']
    # start timer
    starttime = time.time()
    # run cal_dark_spirou
    cal_DARK_spirou.main(NIGHT_NAME, files)
    # end timer
    endtime = time.time()
    # add time to output
    times[name] = endtime - starttime
    plt.close('all')
    test += 1

    # ----------------------------------------------------------------------
    # test cal_loc_RAW_spirou - flat_dark
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_loc_RAW_spirou (flat_dark)'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # set up files
    files = ['flat_dark02f10.fits', 'flat_dark03f10.fits',
             'flat_dark04f10.fits', 'flat_dark05f10.fits',
             'flat_dark06f10.fits']
    # start timer
    starttime = time.time()
    # run cal_dark_spirou
    cal_loc_RAW_spirou.main(NIGHT_NAME, files)
    # end timer
    endtime = time.time()
    # add time to output
    times[name] = endtime - starttime
    plt.close('all')
    test += 1

    # ----------------------------------------------------------------------
    # test cal_loc_RAW_spirou - dark_flat
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_loc_RAW_spirou (dark_flat)'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # set up files
    files = ['dark_flat02f10.fits', 'dark_flat03f10.fits',
             'dark_flat04f10.fits', 'dark_flat05f10.fits',
             'dark_flat06f10.fits']
    # start timer
    starttime = time.time()
    # run cal_dark_spirou
    cal_loc_RAW_spirou.main(NIGHT_NAME, files)
    # end timer
    endtime = time.time()
    # add time to output
    times[name] = endtime - starttime
    plt.close('all')
    test += 1

    # ----------------------------------------------------------------------
    # test cal_SLIT_spirou
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_SLIT_spirou'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # set up files
    files = ['fp_fp02a203.fits', 'fp_fp03a203.fits', 'fp_fp04a203.fits']
    # start timer
    starttime = time.time()
    # run cal_dark_spirou
    cal_SLIT_spirou.main(NIGHT_NAME, files)
    # end timer
    endtime = time.time()
    # add time to output
    times[name] = endtime - starttime
    plt.close('all')
    test += 1

    # ----------------------------------------------------------------------
    # test cal_FF_RAW_spirou - flat_dark
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_FF_RAW_spirou (flat_dark)'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # set up files
    files = ['flat_dark02f10.fits', 'flat_dark03f10.fits',
             'flat_dark04f10.fits', 'flat_dark05f10.fits',
             'flat_dark06f10.fits']
    # start timer
    starttime = time.time()
    # run cal_dark_spirou
    cal_FF_RAW_spirou.main(NIGHT_NAME, files)
    # end timer
    endtime = time.time()
    # add time to output
    times[name] = endtime - starttime
    plt.close('all')
    test += 1

    # ----------------------------------------------------------------------
    # test cal_FF_RAW_spirou - dark_flat
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_FF_RAW_spirou (dark_flat)'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # set up files
    files = ['dark_flat02f10.fits', 'dark_flat03f10.fits',
             'dark_flat04f10.fits', 'dark_flat05f10.fits',
             'dark_flat06f10.fits']
    # start timer
    starttime = time.time()
    # run cal_dark_spirou
    cal_FF_RAW_spirou.main(NIGHT_NAME, files)
    # end timer
    endtime = time.time()
    # add time to output
    times[name] = endtime - starttime
    plt.close('all')
    test += 1

    # ----------------------------------------------------------------------
    # test cal_extract_RAW_spirou - hcone_dark
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_FF_RAW_spirou (dark_flat)'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # start timer
    starttime = time.time()
    # run cal_dark_spirou
    cal_extract_RAW_spirou.main(NIGHT_NAME, files, 'AB')
    # end timer
    endtime = time.time()
    # add time to output
    times[name] = endtime - starttime
    plt.close('all')
    test += 1

    # ----------------------------------------------------------------------
    # test cal_extract_RAW_spirou - hcone_dark
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_extract_RAW_spirou (hcone_dark)'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # set up files
    files = ['hcone_dark02c61.fits', 'hcone_dark03c61.fits',
             'hcone_dark04c61.fits', 'hcone_dark05c61.fits',
             'hcone_dark06c61.fits']
    # start timer
    starttime = time.time()
    # run cal_dark_spirou
    cal_extract_RAW_spirou.main(NIGHT_NAME, files, 'AB')
    # end timer
    endtime = time.time()
    # add time to output
    times[name] = endtime - starttime
    plt.close('all')
    test += 1

    # ----------------------------------------------------------------------
    # test cal_extract_RAW_spirou - dark_hcone
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_extract_RAW_spirou (dark_hcone)'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # set up files
    files = ['dark_hcone02c61.fits', 'dark_hcone03c61.fits',
             'dark_hcone04c61.fits', 'dark_hcone05c61.fits',
             'dark_hcone06c61.fits']
    # start timer
    starttime = time.time()
    # run cal_dark_spirou
    cal_extract_RAW_spirou.main(NIGHT_NAME, files, 'C')
    # end timer
    endtime = time.time()
    # add time to output
    times[name] = endtime - starttime
    plt.close('all')
    test += 1

    # ----------------------------------------------------------------------
    # test cal_extract_RAW_spirou - hcone_hcone AB
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_extract_RAW_spirou (hcone_hcone AB)'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # set up files
    files = ['hcone_hcone02c61.fits', 'hcone_hcone03c61.fits',
             'hcone_hcone04c61.fits', 'hcone_hcone05c61.fits',
             'hcone_hcone06c61.fits']
    # start timer
    starttime = time.time()
    # run cal_dark_spirou
    cal_extract_RAW_spirou.main(NIGHT_NAME, files, 'AB')
    # end timer
    endtime = time.time()
    # add time to output
    times[name] = endtime - starttime
    plt.close('all')
    test += 1

    # ----------------------------------------------------------------------
    # test cal_extract_RAW_spirou - hcone_hcone C
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_extract_RAW_spirou (hcone_hcone C)'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # set up files
    files = ['hcone_hcone02c61.fits', 'hcone_hcone03c61.fits',
             'hcone_hcone04c61.fits', 'hcone_hcone05c61.fits',
             'hcone_hcone06c61.fits']
    # start timer
    starttime = time.time()
    # run cal_dark_spirou
    cal_extract_RAW_spirou.main(NIGHT_NAME, files, 'C')
    # end timer
    endtime = time.time()
    # add time to output
    times[name] = endtime - starttime
    plt.close('all')
    test += 1

    # ----------------------------------------------------------------------
    # test cal_extract_RAW_spirou - dark_dark_AHC1 AB
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_extract_RAW_spirou (dark_dark_AHC1 AB)'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # set up files
    files = ['dark_dark_AHC102d61.fits', 'dark_dark_AHC103d61.fits',
             'dark_dark_AHC104d61.fits', 'dark_dark_AHC105d61.fits',
             'dark_dark_AHC106d61.fits']
    # start timer
    starttime = time.time()
    # run cal_dark_spirou
    cal_extract_RAW_spirou.main(NIGHT_NAME, files, 'AB')
    # end timer
    endtime = time.time()
    # add time to output
    times[name] = endtime - starttime
    plt.close('all')
    test += 1

    # ----------------------------------------------------------------------
    # test cal_extract_RAW_spirou - dark_dark_AHC1 C
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_extract_RAW_spirou (dark_dark_AHC1 C)'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # set up files
    files = ['dark_dark_AHC102d61.fits', 'dark_dark_AHC103d61.fits',
             'dark_dark_AHC104d61.fits', 'dark_dark_AHC105d61.fits',
             'dark_dark_AHC106d61.fits']
    # start timer
    starttime = time.time()
    # run cal_dark_spirou
    cal_extract_RAW_spirou.main(NIGHT_NAME, files, 'C')
    # end timer
    endtime = time.time()
    # add time to output
    times[name] = endtime - starttime
    plt.close('all')
    test += 1

    # ----------------------------------------------------------------------
    # test cal_extract_RAW_spirou - hctwo_dark AB
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_extract_RAW_spirou (hctwo_dark AB)'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # set up files
    files = ['hctwo_dark02c61.fits', 'hctwo_dark03c61.fits',
             'hctwo_dark04c61.fits', 'hctwo_dark05c61.fits',
             'hctwo_dark06c61.fits']
    # start timer
    starttime = time.time()
    # run cal_dark_spirou
    cal_extract_RAW_spirou.main(NIGHT_NAME, files, 'AB')
    # end timer
    endtime = time.time()
    # add time to output
    times[name] = endtime - starttime
    plt.close('all')
    test += 1

    # ----------------------------------------------------------------------
    # test cal_extract_RAW_spirou - hctwo_dark C
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_extract_RAW_spirou (hctwo_dark C)'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # set up files
    files = ['hctwo_dark02c61.fits', 'hctwo_dark03c61.fits',
             'hctwo_dark04c61.fits', 'hctwo_dark05c61.fits',
             'hctwo_dark06c61.fits']
    # start timer
    starttime = time.time()
    # run cal_dark_spirou
    cal_extract_RAW_spirou.main(NIGHT_NAME, files, 'C')
    # end timer
    endtime = time.time()
    # add time to output
    times[name] = endtime - starttime
    plt.close('all')
    test += 1

    # ----------------------------------------------------------------------
    # test cal_extract_RAW_spirou - dark_hctwo AB
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_extract_RAW_spirou (dark_hctwo AB)'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # set up files
    files = ['dark_hctwo02c61.fits', 'dark_hctwo03c61.fits',
             'dark_hctwo04c61.fits', 'dark_hctwo05c61.fits',
             'dark_hctwo06c61.fits']
    # start timer
    starttime = time.time()
    # run cal_dark_spirou
    cal_extract_RAW_spirou.main(NIGHT_NAME, files, 'AB')
    # end timer
    endtime = time.time()
    # add time to output
    times[name] = endtime - starttime
    plt.close('all')
    test += 1

    # ----------------------------------------------------------------------
    # test cal_extract_RAW_spirou - dark_hctwo C
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_extract_RAW_spirou (dark_hctwo C)'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # set up files
    files = ['dark_hctwo02c61.fits', 'dark_hctwo03c61.fits',
             'dark_hctwo04c61.fits', 'dark_hctwo05c61.fits',
             'dark_hctwo06c61.fits']
    # start timer
    starttime = time.time()
    # run cal_dark_spirou
    cal_extract_RAW_spirou.main(NIGHT_NAME, files, 'C')
    # end timer
    endtime = time.time()
    # add time to output
    times[name] = endtime - starttime
    plt.close('all')
    test += 1

    # ----------------------------------------------------------------------
    # test cal_extract_RAW_spirou - hctwo_hctwo AB
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_extract_RAW_spirou (hctwo-hctwo AB)'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # set up files
    files = ['hctwo-hctwo02c61.fits', 'hctwo-hctwo03c61.fits',
             'hctwo-hctwo04c61.fits', 'hctwo-hctwo05c61.fits',
             'hctwo-hctwo06c61.fits']
    # start timer
    starttime = time.time()
    # run cal_dark_spirou
    cal_extract_RAW_spirou.main(NIGHT_NAME, files, 'AB')
    # end timer
    endtime = time.time()
    # add time to output
    times[name] = endtime - starttime
    plt.close('all')
    test += 1

    # ----------------------------------------------------------------------
    # test cal_extract_RAW_spirou - hctwo_hctwo AB
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_extract_RAW_spirou (hctwo-hctwo C)'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # set up files
    files = ['hctwo-hctwo02c61.fits', 'hctwo-hctwo03c61.fits',
             'hctwo-hctwo04c61.fits', 'hctwo-hctwo05c61.fits',
             'hctwo-hctwo06c61.fits']
    # start timer
    starttime = time.time()
    # run cal_dark_spirou
    cal_extract_RAW_spirou.main(NIGHT_NAME, files, 'C')
    # end timer
    endtime = time.time()
    # add time to output
    times[name] = endtime - starttime
    plt.close('all')
    test += 1

    # ----------------------------------------------------------------------
    # test cal_extract_RAW_spirou - dark_dark_AHC2 AB
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_extract_RAW_spirou (dark_dark_AHC2 AB)'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # set up files
    files = ['dark_dark_AHC202d61.fits', 'dark_dark_AHC203d61.fits',
             'dark_dark_AHC204d61.fits', 'dark_dark_AHC205d61.fits',
             'dark_dark_AHC206d61.fits']
    # start timer
    starttime = time.time()
    # run cal_dark_spirou
    cal_extract_RAW_spirou.main(NIGHT_NAME, files, 'AB')
    # end timer
    endtime = time.time()
    # add time to output
    times[name] = endtime - starttime
    plt.close('all')
    test += 1

    # ----------------------------------------------------------------------
    # test cal_extract_RAW_spirou - dark_dark_AHC2 C
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_extract_RAW_spirou (dark_dark_AHC2 C)'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # set up files
    files = ['dark_dark_AHC202d61.fits', 'dark_dark_AHC203d61.fits',
             'dark_dark_AHC204d61.fits', 'dark_dark_AHC205d61.fits',
             'dark_dark_AHC206d61.fits']
    # start timer
    starttime = time.time()
    # run cal_dark_spirou
    cal_extract_RAW_spirou.main(NIGHT_NAME, files, 'C')
    # end timer
    endtime = time.time()
    # add time to output
    times[name] = endtime - starttime
    plt.close('all')
    test += 1

    # ----------------------------------------------------------------------
    # test cal_extract_RAW_spirou - fp_fp AB
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_extract_RAW_spirou (fp_fp AB)'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # set up files
    files = ['fp_fp02a203.fits', 'fp_fp03a203.fits', 'fp_fp04a203.fits']
    # start timer
    starttime = time.time()
    # run cal_dark_spirou
    cal_extract_RAW_spirou.main(NIGHT_NAME, files, 'AB')
    # end timer
    endtime = time.time()
    # add time to output
    times[name] = endtime - starttime
    plt.close('all')
    test += 1

    # ----------------------------------------------------------------------
    # test cal_extract_RAW_spirou - fp_fp C
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_extract_RAW_spirou (fp_fp C)'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # set up files
    files = ['fp_fp02a203.fits', 'fp_fp03a203.fits', 'fp_fp04a203.fits']
    # start timer
    starttime = time.time()
    # run cal_dark_spirou
    cal_extract_RAW_spirou.main(NIGHT_NAME, files, 'C')
    # end timer
    endtime = time.time()
    # add time to output
    times[name] = endtime - starttime
    plt.close('all')
    test += 1

    # ----------------------------------------------------------------------
    # test cal_DRIFT_RAW_spirou
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_DRIFT_RAW_spirou'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # set up files
    files = ['fp_fp02a203.fits', 'fp_fp03a203.fits', 'fp_fp04a203.fits']
    # start timer
    starttime = time.time()
    # run cal_dark_spirou
    cal_DRIFT_RAW_spirou.main(NIGHT_NAME, files)
    # end timer
    endtime = time.time()
    # add time to output
    times[name] = endtime - starttime
    plt.close('all')
    test += 1

    # ----------------------------------------------------------------------
    # end total timer
    endtotaltime = time.time()
    times['Total'] = endtotaltime - starttotaltime

    # ----------------------------------------------------------------------
    # Timing stats
    # ----------------------------------------------------------------------
    print('\n\n\n TIMING STATS \n\n\n')
    # Now print the stats for this test:
    for key in list(times.keys()):
        print('{0} Time taken = {1} s'.format(key, times[key]))

    # print starting unit tests
    print('\n\n\n END OF UNIT TESTS \n\n\n')

# =============================================================================
# End of code
# =============================================================================
