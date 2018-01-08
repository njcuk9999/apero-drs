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

from SpirouDRS import spirouConfig
from . import unit_test_functions as utf

if sys.version_info.major == 2:
    from collections import OrderedDict as dict


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouUnitTests.unit_test1.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# define night name constant
NIGHT_NAME = '20170710'
# define format for unit test logging
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
    # run test
    times[name] = utf.UNIT_TEST_CAL_DARK()
    test += 1

    # ----------------------------------------------------------------------
    # test cal_BADPIX_spirou
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_BADPIX_spirou'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # run test
    times[name] = utf.UNIT_TEST_CAL_BADPIX()
    test += 1

    # ----------------------------------------------------------------------
    # test cal_loc_RAW_spirou - flat_dark
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_loc_RAW_spirou (flat_dark)'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # run test
    times[name] = utf.UNIT_TEST_CAL_LOC_RAW(kind='flat_dark')
    test += 1

    # ----------------------------------------------------------------------
    # test cal_loc_RAW_spirou - dark_flat
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_loc_RAW_spirou (dark_flat)'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # run test
    times[name] = utf.UNIT_TEST_CAL_LOC_RAW(kind='dark_flat')
    test += 1

    # ----------------------------------------------------------------------
    # test cal_SLIT_spirou
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_SLIT_spirou'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # run test
    times[name] = utf.UNIT_TEST_CAL_SLIT()
    test += 1

    # ----------------------------------------------------------------------
    # test cal_FF_RAW_spirou - flat_dark
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_FF_RAW_spirou (flat_dark)'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # run test
    times[name] = utf.UNIT_TEST_CAL_FF_RAW(kind='flat_dark')
    test += 1

    # ----------------------------------------------------------------------
    # test cal_FF_RAW_spirou - dark_flat
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_FF_RAW_spirou (dark_flat)'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # run test
    times[name] = utf.UNIT_TEST_CAL_FF_RAW(kind='dark_flat')
    test += 1

    # ----------------------------------------------------------------------
    # test cal_extract_RAW_spirou - fp_fp02a203.fits
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_extract_RAW_spirou (fp_fp02a203.fits AB A B C)'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # set up files
    files = ['fp_fp02a203.fits']
    # run test
    times[name] = utf.UNIT_TEST_CAL_EXTRACT(files=files, fiber=None)
    test += 1

    # ----------------------------------------------------------------------
    # test cal_extract_RAW_spirou - fp_fp03a203.fits
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_extract_RAW_spirou (fp_fp03a203.fits AB A B C)'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # set up files
    files = ['fp_fp03a203.fits']
    # run test
    times[name] = utf.UNIT_TEST_CAL_EXTRACT(files=files, fiber=None)
    test += 1

    # ----------------------------------------------------------------------
    # test cal_extract_RAW_spirou - fp_fp04a203.fits
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_extract_RAW_spirou (fp_fp04a203.fits AB A B C)'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # set up files
    files = ['fp_fp04a203.fits']
    # run test
    times[name] = utf.UNIT_TEST_CAL_EXTRACT(files=files, fiber=None)
    test += 1

    # ----------------------------------------------------------------------
    # test cal_DRIFT_E2DS_spirou
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_DRIFT_E2DS_spirou'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # run test
    times[name] = utf.UNIT_TEST_CAL_DRIFT_E2DS()
    test += 1

    # ----------------------------------------------------------------------
    # test cal_CCF_E2DS_spirou
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_CCF_E2DS_spirou'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # run test
    times[name] = utf.UNIT_TEST_CAL_CCF_E2DS()
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
