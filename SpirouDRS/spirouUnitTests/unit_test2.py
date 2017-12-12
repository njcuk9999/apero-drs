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
import sys

import cal_DARK_spirou
import cal_loc_RAW_spirou
import cal_SLIT_spirou
import cal_FF_RAW_spirou
import cal_extract_RAW_spirou
import cal_DRIFT_RAW_spirou
import cal_BADPIX_spirou
import matplotlib.pyplot as plt

if sys.version_info.major == 2:
    from collections import OrderedDict as dict

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
    # test cal_extract_RAW_spirou - fp_fp02a203.fits
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_extract_RAW_spirou (fp_fp02a203.fits AB A B C)'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # set up files
    files = ['fp_fp02a203.fits']
    # start timer
    starttime = time.time()
    # run cal_dark_spirou
    cal_extract_RAW_spirou.main(NIGHT_NAME, files)
    # end timer
    endtime = time.time()
    # add time to output
    times[name] = endtime - starttime
    plt.close('all')
    test += 1

    # ----------------------------------------------------------------------
    # test cal_extract_RAW_spirou - fp_fp03a203.fits
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_extract_RAW_spirou (fp_fp03a203.fits AB A B C)'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # set up files
    files = ['fp_fp03a203.fits']
    # start timer
    starttime = time.time()
    # run cal_dark_spirou
    cal_extract_RAW_spirou.main(NIGHT_NAME, files)
    # end timer
    endtime = time.time()
    # add time to output
    times[name] = endtime - starttime
    plt.close('all')
    test += 1


    # ----------------------------------------------------------------------
    # test cal_extract_RAW_spirou - fp_fp04a203.fits
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_extract_RAW_spirou (fp_fp04a203.fits AB A B C)'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # set up files
    files = ['fp_fp04a203.fits']
    # start timer
    starttime = time.time()
    # run cal_dark_spirou
    cal_extract_RAW_spirou.main(NIGHT_NAME, files)
    # end timer
    endtime = time.time()
    # add time to output
    times[name] = endtime - starttime
    plt.close('all')
    test += 1


    # ----------------------------------------------------------------------
    # test cal_DRIFT_E2DS_spirou
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_DRIFT_E2DS_spirou'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # set up files
    files = ['fp_fp02a203_e2ds_AB.fits']
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
    # test cal_DRIFT_E2DS_spirou
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_BADPIX_spirou'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # set up files
    flatfile = 'flat_flat02f10.fits'
    darkfile = 'dark_dark02d406.fits'
    # start timer
    starttime = time.time()
    # run cal_dark_spirou
    cal_BADPIX_spirou.main(NIGHT_NAME, darkfile=darkfile, flatfile=flatfile)
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
