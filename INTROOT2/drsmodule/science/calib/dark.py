#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-03-25 at 12:29

@author: cook
"""
from __future__ import division
import traceback
import os
from astropy.io import fits
from astropy.table import Table
import numpy as np

from drsmodule import constants
from drsmodule.config import drs_log
from drsmodule import locale
from drsmodule.config import drs_file

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'io.drs_path.py'
__INSTRUMENT__ = None
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# get param dict
ParamDict = constants.ParamDict
DrsFitsFile = drs_file.DrsFitsFile
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
ErrorEntry = locale.drs_text.ErrorEntry
ErrorText = locale.drs_text.ErrorText


# =============================================================================
# Define functions
# =============================================================================
def measure_dark(params, image, entry_key):
    """
    Measure the dark pixels in "image"

    :param params: parameter dictionary, ParamDict containing constants
        Must contain at least:
                log_opt: string, log option, normally the program name
                DARK_QMIN: int, The lower percentile (0 - 100)
                DARK_QMAX: int, The upper percentile (0 - 100)
                HISTO_BINS: int,  The number of bins in dark histogram
                HISTO_RANGE_LOW: float, the lower extent of the histogram
                                 in ADU/s
                HISTO_RANGE_HIGH: float, the upper extent of the histogram
                                  in ADU/s

    :param image: numpy array (2D), the image
    :param entry_key: string, the entry key (for logging)

    :return: hist numpy.histogram tuple (hist, bin_edges),
             med: float, the median value of the non-Nan image values,
             dadead: float, the fraction of dead pixels as a percentage

          where:
              hist : numpy array (1D) The values of the histogram.
              bin_edges : numpy array (1D) of floats, the bin edges
    """
    func_name = __NAME__ + '.measure_dark()'
    # get the errortext
    errortext = ErrorText(params['INSTRUMENT'], params['LANGUAGE'])
    image_name = errortext[entry_key]
    # make sure image is a numpy array
    # noinspection PyBroadException
    try:
        image = np.array(image)
    except Exception as e:
        eargs = [type(e), e, func_name]
        WLOG(params, 'error', ErrorEntry('00-001-00026', args=eargs))
    # check that params contains required parameters
    dark_qmin = drs_log.find_param(params, 'DARK_QMIN', func_name)
    dark_qmax = drs_log.find_param(params, 'DARK_QMAX', func_name)
    hbins = drs_log.find_param(params, 'HISTO_BINS', func_name)
    hrangelow = drs_log.find_param(params, 'HISTO_RANGE_LOW', func_name)
    hrangehigh = drs_log.find_param(params, 'HISTO_RANGE_HIGH', func_name)
    # flatten the image
    fimage = image.flat
    # get the finite (non-NaN) mask
    fimage = fimage[np.isfinite(fimage)]
    # get the number of NaNs
    imax = image.size - len(fimage)
    # get the median value of the non-NaN data
    med = np.median(fimage)
    # get the 5th and 95th percentile qmin
    qmin, qmax = np.percentile(fimage, [dark_qmin, dark_qmax])
    # get the histogram for flattened data
    histo = np.histogram(fimage, bins=hbins, range=(hrangelow, hrangehigh),
                         density=True)
    # get the fraction of dead pixels as a percentage
    dadead = imax * 100 / np.product(image.shape)
    # log the dark statistics
    wargs = [image_name, dadead, med, dark_qmin, dark_qmax, qmin, qmax]
    WLOG(params, 'info', ErrorEntry('40-011-00002', args=wargs))
    # return the parameter dictionary with new values
    return np.array(histo), float(med), float(dadead)


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
