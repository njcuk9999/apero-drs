#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-01-08 at 12:36

@author: cook



Version 0.0.0
"""
from __future__ import division
import time
import matplotlib.pyplot as plt

import cal_BADPIX_spirou
import cal_CCF_E2DS_spirou
import cal_DARK_spirou
import cal_DRIFT_RAW_spirou
import cal_DRIFT_E2DS_spirou
import cal_DRIFTPEAK_E2DS_spirou
import cal_extract_RAW_spirou
import cal_FF_RAW_spirou
import cal_loc_RAW_spirou
import cal_SLIT_spirou


# =============================================================================
# Define variables
# =============================================================================
NIGHT_NAME = '20170710'

UNITTEST = '{0}{1}{2}UNIT TEST {3}: {4}{2}{1}{0}'
# -----------------------------------------------------------------------------


# =============================================================================
# Define functions
# =============================================================================
def UNIT_TEST_CAL_BADPIX(log=False, plot=False):
    """
    test cal_BADPIX_spirou

    :param log: bool, whether to print test log messages during run
    :param plot: bool, whether to automatically close all plots after run
    :return timing: float, the time in seconds taken to run test
    """
    # set name and print progress
    name = 'cal_BADPIX_spirou'
    if log:
        print(UNITTEST.format('\n'*3, '='*50, '\n', name))
    # set up files
    darkfile = 'dark_dark02d406.fits'
    flatfile = 'flat_flat02f10.fits'
    # start timer
    starttime = time.time()
    # run cal_dark_spirou
    cal_BADPIX_spirou.main(NIGHT_NAME, darkfile, flatfile)
    # end timer
    endtime = time.time()
    if not plot:
        plt.close('all')
    # return timing
    return endtime - starttime


def UNIT_TEST_CAL_DARK(log=False, plot=False):
    """
    test cal_dark_spirou

    :param log: bool, whether to print test log messages during run
    :param plot: bool, whether to automatically close all plots after run
    :return timing: float, the time in seconds taken to run test
    """
    # set name and print progress
    name = 'cal_DARK_spirou'
    if log:
        print(UNITTEST.format('\n'*3, '='*50, '\n', name))
    # set up files
    files = ['dark_dark02d406.fits']
    # start timer
    starttime = time.time()
    # run cal_dark_spirou
    cal_DARK_spirou.main(NIGHT_NAME, files)
    # end timer
    endtime = time.time()
    if not plot:
        plt.close('all')
    # return timing
    return endtime - starttime


def UNIT_TEST_CAL_LOC_RAW(kind='flat_dark', log=False, plot=False):
    """
    test cal_loc_RAW_spirou

    :param kind: string, a switch to enable multiple file tests
                 kinds allowed are:
                        - flat_dark
                        - dark_flat
    :param log: bool, whether to print test log messages during run
    :param plot: bool, whether to automatically close all plots after run
    :return timing: float, the time in seconds taken to run test
    """
    # set name and print progress
    name = 'cal_loc_RAW_spirou ({0})'.format(kind)
    if log:
        print(UNITTEST.format('\n' * 3, '=' * 50, '\n', name))
    # set up files
    if kind == 'flat_dark':
        files = ['flat_dark02f10.fits', 'flat_dark03f10.fits',
                 'flat_dark04f10.fits', 'flat_dark05f10.fits',
                 'flat_dark06f10.fits']
    elif kind == 'dark_flat':
        files = ['dark_flat02f10.fits', 'dark_flat03f10.fits',
                 'dark_flat04f10.fits', 'dark_flat05f10.fits',
                 'dark_flat06f10.fits']
    else:
        emsg = 'kind={0} not understood for test of {1}'
        raise ValueError(emsg.format(kind, name))
    # start timer
    starttime = time.time()
    # run cal_dark_spirou
    cal_loc_RAW_spirou.main(NIGHT_NAME, files)
    # end timer
    endtime = time.time()
    if not plot:
        plt.close('all')
    # return timing
    return endtime - starttime


def UNIT_TEST_CAL_SLIT(log=False, plot=False):
    """
    test cal_SLIT_spirou

    :param log: bool, whether to print test log messages during run
    :param plot: bool, whether to automatically close all plots after run
    :return timing: float, the time in seconds taken to run test
    """
    # set name and print progress
    name = 'cal_SLIT_spirou'
    if log:
        print(UNITTEST.format('\n' * 3, '=' * 50, '\n', name))
    # set up files
    files = ['fp_fp02a203.fits', 'fp_fp03a203.fits', 'fp_fp04a203.fits']
    # start timer
    starttime = time.time()
    # run cal_dark_spirou
    cal_SLIT_spirou.main(NIGHT_NAME, files)
    # end timer
    endtime = time.time()
    if not plot:
        plt.close('all')
    # return timing
    return endtime - starttime


def UNIT_TEST_CAL_FF_RAW(kind='flat_dark', log=False, plot=False):
    """
    test cal_FF_RAW_spirou

    :param kind: string, a switch to enable multiple file tests
                 kinds allowed are:
                        - flat_dark
                        - dark_flat
    :param log: bool, whether to print test log messages during run
    :param plot: bool, whether to automatically close all plots after run
    :return timing: float, the time in seconds taken to run test
    """
    # set name and print progress
    name = 'cal_FF_RAW_spirou ({0})'.format(kind)
    if log:
        print(UNITTEST.format('\n' * 3, '=' * 50, '\n', name))
    # set up files
    if kind == 'flat_dark':
        files = ['flat_dark02f10.fits', 'flat_dark03f10.fits',
                 'flat_dark04f10.fits', 'flat_dark05f10.fits',
                 'flat_dark06f10.fits']
    elif kind == 'dark_flat':
        files = ['dark_flat02f10.fits', 'dark_flat03f10.fits',
                 'dark_flat04f10.fits', 'dark_flat05f10.fits',
                 'dark_flat06f10.fits']
    else:
        emsg = 'kind={0} not understood for test of {1}'
        raise ValueError(emsg.format(kind, name))
    # start timer
    starttime = time.time()
    # run cal_dark_spirou
    cal_FF_RAW_spirou.main(NIGHT_NAME, files)
    # end timer
    endtime = time.time()
    if not plot:
        plt.close('all')
    # return timing
    return endtime - starttime


def UNIT_TEST_CAL_EXTRACT(kind='fp_fp', fiber=None, log=False, plot=False,
                          files=None):
    """
    test cal_FF_RAW_spirou

    :param kind: string, a switch to enable multiple file tests
                 kinds allowed are:
                        - hcone_dark
                        - dark_hcone
                        - hcone_hcone
                        - dark_dark_ach1
                        - hctwo_dark
                        - dark_hctwo
                        - hctwo-hctwo
                        - dark_dark_ach2
                        - fp_fp

    :param fiber: string, fiber type
                fibers allowed are:
                        - "AB"
                        - "A"
                        - "B"
                        - "C"
                        - "ALL" (or None)
    :param log: bool, whether to print test log messages during run
    :param plot: bool, whether to automatically close all plots after run
    :param files: None or list of strings, set the list of files manually

    :return timing: float, the time in seconds taken to run test
    """
    if fiber is not None:
        # make fiber uppercase
        fiber = fiber.upper()
    # make kind lowercase
    kind = kind.lower()
    # set name and print progress
    name = 'cal_extract_RAW_spirou ({0} {1})'.format(kind, fiber)
    if log:
        print(UNITTEST.format('\n' * 3, '=' * 50, '\n', name))
    # set up files
    if files is not None:
        files = list(files)
    elif 'hcone_dark' in kind:
        files = ['hcone_dark02c61.fits', 'hcone_dark03c61.fits',
                 'hcone_dark04c61.fits', 'hcone_dark05c61.fits',
                 'hcone_dark06c61.fits']
    elif 'dark_hcone' in kind:
        files = ['dark_hcone02c61.fits', 'dark_hcone03c61.fits',
                 'dark_hcone04c61.fits', 'dark_hcone05c61.fits',
                 'dark_hcone06c61.fits']
    elif 'hcone_hcone' in kind:
        files = ['hcone_hcone02c61.fits', 'hcone_hcone03c61.fits',
                 'hcone_hcone04c61.fits', 'hcone_hcone05c61.fits',
                 'hcone_hcone06c61.fits']
    elif 'dark_dark_ahc1' in kind:
        files = ['dark_dark_AHC102d61.fits', 'dark_dark_AHC103d61.fits',
                 'dark_dark_AHC104d61.fits', 'dark_dark_AHC105d61.fits',
                 'dark_dark_AHC106d61.fits']
    elif 'hctwo_dark' in kind:
        files = ['hctwo_dark02c61.fits', 'hctwo_dark03c61.fits',
                 'hctwo_dark04c61.fits', 'hctwo_dark05c61.fits',
                 'hctwo_dark06c61.fits']
    elif 'dark_hctwo' in kind:
        files = ['dark_hctwo02c61.fits', 'dark_hctwo03c61.fits',
                 'dark_hctwo04c61.fits', 'dark_hctwo05c61.fits',
                 'dark_hctwo06c61.fits']
    elif 'hctwo-hctwo' in kind:
        files = ['hctwo-hctwo02c61.fits', 'hctwo-hctwo03c61.fits',
                 'hctwo-hctwo04c61.fits', 'hctwo-hctwo05c61.fits',
                 'hctwo-hctwo06c61.fits']
    elif 'dark_dark_ahc2' in kind:
        files = ['dark_dark_AHC202d61.fits', 'dark_dark_AHC203d61.fits',
                 'dark_dark_AHC204d61.fits', 'dark_dark_AHC205d61.fits',
                 'dark_dark_AHC206d61.fits']
    elif 'fp_fp' in kind:
        files = ['fp_fp02a203.fits', 'fp_fp03a203.fits', 'fp_fp04a203.fits']
    else:
        emsg = 'kind={0} not understood for test of {1}'
        raise ValueError(emsg.format(kind, name))

    # start timer
    starttime = time.time()
    # run cal_dark_spirou
    cal_extract_RAW_spirou.main(NIGHT_NAME, files, fiber)
    # end timer
    endtime = time.time()
    if not plot:
        plt.close('all')
    # return timing
    return endtime - starttime


def UNIT_TEST_CAL_DRIFT_RAW(log=False, plot=False):
    """
    test cal_SLIT_spirou

    :param log: bool, whether to print test log messages during run
    :param plot: bool, whether to automatically close all plots after run
    :return timing: float, the time in seconds taken to run test
    """
    # set name and print progress
    name = 'cal_DRIFT_RAW_spirou'
    if log:
        print(UNITTEST.format('\n' * 3, '=' * 50, '\n', name))
    # set up files
    files = ['fp_fp02a203.fits']
    # start timer
    starttime = time.time()
    # run cal_dark_spirou
    cal_DRIFT_RAW_spirou.main(NIGHT_NAME, files)
    # end timer
    endtime = time.time()
    if not plot:
        plt.close('all')
    # return timing
    return endtime - starttime


def UNIT_TEST_CAL_DRIFT_E2DS(log=False, plot=False):
    """
    test cal_SLIT_spirou

    :param log: bool, whether to print test log messages during run
    :param plot: bool, whether to automatically close all plots after run
    :return timing: float, the time in seconds taken to run test
    """
    # set name and print progress
    name = 'cal_DRIFT_E2DS_spirou'
    if log:
        print(UNITTEST.format('\n' * 3, '=' * 50, '\n', name))
    # set up files
    files = ['fp_fp02a203.fits']
    # start timer
    starttime = time.time()
    # run cal_dark_spirou
    cal_DRIFT_E2DS_spirou.main(NIGHT_NAME, files)
    # end timer
    endtime = time.time()
    if not plot:
        plt.close('all')
    # return timing
    return endtime - starttime


def UNIT_TEST_CAL_DRIFTPEAK_E2DS(log=False, plot=False):
    """
    test cal_SLIT_spirou

    :param log: bool, whether to print test log messages during run
    :param plot: bool, whether to automatically close all plots after run
    :return timing: float, the time in seconds taken to run test
    """
    # set name and print progress
    name = 'cal_DRIFT_E2DS_spirou'
    if log:
        print(UNITTEST.format('\n' * 3, '=' * 50, '\n', name))
    # set up files
    files = ['fp_fp02a203.fits']
    # start timer
    starttime = time.time()
    # run cal_dark_spirou
    cal_DRIFTPEAK_E2DS_spirou.main(NIGHT_NAME, files)
    # end timer
    endtime = time.time()
    if not plot:
        plt.close('all')
    # return timing
    return endtime - starttime


def UNIT_TEST_CAL_CCF_E2DS(log=False, plot=False):
    """
    test cal_CCF_E2DS_spirou

    :param log: bool, whether to print test log messages during run
    :param plot: bool, whether to automatically close all plots after run
    :return timing: float, the time in seconds taken to run test
    """
    # set name and print progress
    name = 'cal_CCF_E2DS_spirou'
    if log:
        print(UNITTEST.format('\n' * 3, '=' * 50, '\n', name))
    # set up files
    reffile = 'fp_fp02a203_e2ds_AB.fits'
    mask, rv, width, step = 'UrNe.mas', 0, 10, 0.1
    # start timer
    starttime = time.time()
    # run cal_dark_spirou
    cal_CCF_E2DS_spirou.main(NIGHT_NAME, reffile, mask, rv, width, step)
    # end timer
    endtime = time.time()
    if not plot:
        plt.close('all')
    # return timing
    return endtime - starttime


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
