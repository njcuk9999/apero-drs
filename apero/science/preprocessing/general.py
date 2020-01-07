#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-12-12 at 09:45

@author: cook
"""
import numpy as np

from apero.core import constants
from apero.core import math as mp
from apero import core
from apero import locale


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'preprocessing.general.py'
__INSTRUMENT__ = 'None'
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# Get Logging function
WLOG = core.wlog
# Get the text types
TextEntry = locale.drs_text.TextEntry
# get param dict
ParamDict = constants.ParamDict


# =============================================================================
# Define functions
# =============================================================================
def quality_control(params, snr_hotpix, infile, rms_list):
    # set passed variable and fail message list
    fail_msg, qc_values, qc_names, qc_logic, qc_pass = [], [], [], [], []
    # ----------------------------------------------------------------------
    # print out SNR hotpix value
    WLOG(params, '', TextEntry('40-010-00006', args=[snr_hotpix]))
    # get snr_threshold
    snr_threshold = params['PP_CORRUPT_SNR_HOTPIX']
    # deal with printing corruption message
    if snr_hotpix < snr_threshold:
        # add failed message to fail message list
        fargs = [snr_hotpix, snr_threshold, infile.filename]
        fail_msg.append(TextEntry('40-010-00007', args=fargs))
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(snr_hotpix)
    qc_names.append('snr_hotpix')
    qc_logic.append('snr_hotpix < {0:.5e}'.format(snr_threshold))
    # ----------------------------------------------------------------------
    # get rms threshold
    rms_threshold = params['PP_CORRUPT_RMS_THRES']
    # check
    if mp.nanmax(rms_list) > rms_threshold:
        # add failed message to fail message list
        fargs = [mp.nanmax(rms_list), rms_threshold, infile.filename]
        fail_msg.append(TextEntry('40-010-00008', args=fargs))
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(mp.nanmax(rms_list))
    qc_names.append('max(rms_list)')
    qc_logic.append('max(rms_list) > {0:.4e}'.format(rms_threshold))
    # ----------------------------------------------------------------------
    # finally log the failed messages and set QC = 1 if we pass the
    # quality control QC = 0 if we fail quality control
    if np.sum(qc_pass) == len(qc_pass):
        WLOG(params, 'info', TextEntry('40-005-10001'))
        passed = 1
    else:
        for farg in fail_msg:
            WLOG(params, 'warning', TextEntry('40-005-10002') + farg)
        passed = 0
    # store in qc_params
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]
    # return qc_params and passed
    return qc_params, passed


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
