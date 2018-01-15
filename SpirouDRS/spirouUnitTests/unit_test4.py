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
import numpy as np

from SpirouDRS import spirouConfig

try:
    from . import unit_test_functions as utf
    from . import unit_test_comp_functions as utc
except ImportError:
    import unit_test_functions as utf
    import unit_test_comp_functions as utc

if sys.version_info.major == 2:
    from collections import OrderedDict as dict


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouUnitTests.unit_test4.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# define night name constant
NIGHT_NAME = '20170710'
# define format for unit test logging
UNITTEST = '{0}{1}{2}UNIT TEST {3}: {4}{2}{1}{0}'
# define old version reduced path
OLDPATH = '/scratch/Projects/SPIRou_Pipeline/data/reduced/20170710'
# plot path
RESULTSPATH = '/scratch/Projects/spirou_py3/unit_test_graphs/unit_test4/'
# threshold for difference pass
THRESHOLD = -8


# =============================================================================
# Define functions
# =============================================================================
def compare(name, ll, newoutputs, oldoutputs, errors):

    print('\n\n Comparing files...')
    # define new output files from ll
    newfiles = ll['outputs']
    # define new path from p['reduced_dir']
    newpath = ll['p']['reduced_dir']
    # get old output locations (that should be the same as new output files)
    lists = utc.create_oldfiles(newfiles, OLDPATH, newpath)
    newoutputs[name], oldoutputs[name] = lists
    # get any differences between old and new
    e0 = utc.comparison_wrapper(name, oldoutputs[name], newoutputs[name],
                                    path=RESULTSPATH)
    errors += e0

    # return dicts
    return newoutputs, oldoutputs, errors

# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # set up time dictionary
    times = dict()
    newoutputs = dict()
    oldoutputs = dict()
    errors = []
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
    ll = utf.UNIT_TEST_CAL_DARK(return_locals=True)
    times[name] = ll['timer']
    # deal with comparison
    newoutputs, oldoutputs, errors = compare(name, ll, newoutputs,
                                             oldoutputs, errors)
    # append test
    test += 1

    # ----------------------------------------------------------------------
    # test cal_BADPIX_spirou
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_BADPIX_spirou'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # run test
    ll = utf.UNIT_TEST_CAL_BADPIX(return_locals=True)
    times[name] = ll['timer']
    # deal with comparison
    newoutputs, oldoutputs, errors = compare(name, ll, newoutputs,
                                             oldoutputs, errors)
    # append test
    test += 1

    # ----------------------------------------------------------------------
    # test cal_loc_RAW_spirou - flat_dark
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_loc_RAW_spirou (flat_dark)'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # run test
    ll = utf.UNIT_TEST_CAL_LOC_RAW(kind='flat_dark', return_locals=True)
    times[name] = ll['timer']
    # deal with comparison
    newoutputs, oldoutputs, errors = compare(name, ll, newoutputs,
                                             oldoutputs, errors)
    # append test
    test += 1

    # ----------------------------------------------------------------------
    # test cal_loc_RAW_spirou - dark_flat
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_loc_RAW_spirou (dark_flat)'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # run test
    ll = utf.UNIT_TEST_CAL_LOC_RAW(kind='dark_flat', return_locals=True)
    times[name] = ll['timer']
    # deal with comparison
    newoutputs, oldoutputs, errors = compare(name, ll, newoutputs,
                                             oldoutputs, errors)
    # append test
    test += 1

    # ----------------------------------------------------------------------
    # test cal_SLIT_spirou
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_SLIT_spirou'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # run test
    ll = utf.UNIT_TEST_CAL_SLIT(return_locals=True)
    times[name] = ll['timer']
    # deal with comparison
    newoutputs, oldoutputs, errors = compare(name, ll, newoutputs,
                                             oldoutputs, errors)
    # append test
    test += 1

    # ----------------------------------------------------------------------
    # test cal_FF_RAW_spirou - flat_dark
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_FF_RAW_spirou (flat_dark)'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # run test
    ll = utf.UNIT_TEST_CAL_FF_RAW(kind='flat_dark', return_locals=True)
    times[name] = ll['timer']
    # deal with comparison
    newoutputs, oldoutputs, errors = compare(name, ll, newoutputs,
                                             oldoutputs, errors)
    # append test
    test += 1

    # ----------------------------------------------------------------------
    # test cal_FF_RAW_spirou - dark_flat
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_FF_RAW_spirou (dark_flat)'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # run test
    ll = utf.UNIT_TEST_CAL_FF_RAW(kind='dark_flat', return_locals=True)
    times[name] = ll['timer']
    # deal with comparison
    newoutputs, oldoutputs, errors = compare(name, ll, newoutputs,
                                             oldoutputs, errors)
    # append test
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
    ll = utf.UNIT_TEST_CAL_EXTRACT(files=files, fiber=None, return_locals=True)
    times[name] = ll['timer']
    # deal with comparison
    newoutputs, oldoutputs, errors = compare(name, ll, newoutputs,
                                             oldoutputs, errors)
    # append test
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
    ll = utf.UNIT_TEST_CAL_EXTRACT(files=files, fiber=None, return_locals=True)
    times[name] = ll['timer']
    # deal with comparison
    newoutputs, oldoutputs, errors = compare(name, ll, newoutputs,
                                             oldoutputs, errors)
    # append test
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
    ll = utf.UNIT_TEST_CAL_EXTRACT(files=files, fiber=None, return_locals=True)
    times[name] = ll['timer']
    # deal with comparison
    newoutputs, oldoutputs, errors = compare(name, ll, newoutputs,
                                             oldoutputs, errors)
    # append test
    test += 1

    # ----------------------------------------------------------------------
    # test cal_DRIFT_RAW_spirou
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_DRIFT_RAW_spirou'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # run test
    ll = utf.UNIT_TEST_CAL_DRIFT_RAW(return_locals=True)
    times[name] = ll['timer']
    # deal with comparison
    newoutputs, oldoutputs, errors = compare(name, ll, newoutputs,
                                             oldoutputs, errors)
    # append test
    test += 1

    # ----------------------------------------------------------------------
    # test cal_DRIFT_E2DS_spirou
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_DRIFT_E2DS_spirou'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # run test
    ll = utf.UNIT_TEST_CAL_DRIFT_E2DS(return_locals=True)
    times[name] = ll['timer']
    # deal with comparison
    newoutputs, oldoutputs, errors = compare(name, ll, newoutputs,
                                             oldoutputs, errors)
    # append test
    test += 1

    # ----------------------------------------------------------------------
    # test cal_DRIFTPEAK_E2DS_spirou
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_DRIFTPEAK_E2DS_spirou'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # run test
    ll = utf.UNIT_TEST_CAL_DRIFTPEAK_E2DS(return_locals=True)
    times[name] = ll['timer']
    # deal with comparison
    newoutputs, oldoutputs, errors = compare(name, ll, newoutputs,
                                             oldoutputs, errors)
    # append test
    test += 1

    # ----------------------------------------------------------------------
    # test cal_CCF_E2DS_spirou
    # ----------------------------------------------------------------------
    # set name and print progress
    name = 'cal_CCF_E2DS_spirou'
    print(UNITTEST.format('\n'*3, '='*50, '\n', test, name))
    # run test
    ll = utf.UNIT_TEST_CAL_CCF_E2DS(return_locals=True)
    times[name] = ll['timer']
    # deal with comparison
    newoutputs, oldoutputs, errors = compare(name, ll, newoutputs,
                                             oldoutputs, errors)
    # append test
    test += 1

    # ----------------------------------------------------------------------
    # end total timer
    times['Total'] = np.sum(list(times.values()))

    # ----------------------------------------------------------------------
    # Timing stats
    # ----------------------------------------------------------------------
    print('\n\n\n TIMING STATS \n\n\n')
    # Now print the stats for this test:
    for key in list(times.keys()):
        print('{0} Time taken = {1} s'.format(key, times[key]))

    # ----------------------------------------------------------------------
    # Analyse results + save to table
    # ----------------------------------------------------------------------
    print('\n\n Constructing error table...')
    utc.construct_error_table(errors, THRESHOLD, RESULTSPATH)

    # print starting unit tests
    print('\n\n\n END OF UNIT TESTS \n\n\n')

# =============================================================================
# End of code
# =============================================================================
