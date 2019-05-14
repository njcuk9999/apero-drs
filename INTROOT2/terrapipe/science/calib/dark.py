#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-03-25 at 12:29

@author: cook
"""
from __future__ import division
import numpy as np
import os
import warnings

from terrapipe import constants
from terrapipe.config import drs_log
from terrapipe import locale
from terrapipe.config import drs_file
from terrapipe.config.core import drs_database
from terrapipe.io import drs_fits

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.calib.dark.py'
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
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict


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
    # get the textdict
    textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
    image_name = textdict[entry_key]
    # make sure image is a numpy array
    # noinspection PyBroadException
    try:
        image = np.array(image)
    except Exception as e:
        eargs = [type(e), e, func_name]
        WLOG(params, 'error', TextEntry('00-001-00026', args=eargs))
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
    WLOG(params, 'info', TextEntry('40-011-00002', args=wargs))
    # return the parameter dictionary with new values
    return np.array(histo), float(med), float(dadead)


def measure_dark_badpix(params, image, nanmask):
    """
    Measure the bad pixels (non-dark pixels and NaN pixels)

    :param params: parameter dictionary, ParamDict containing constants
    :param image: numpy array (2D), the image
    :param nanmask: numpy array (2D), the make of non-finite values
    :return:
    """
    # get number of bad dark pixels (as a fraction of total pixels)
    with warnings.catch_warnings(record=True) as w:
        baddark = 100.0 * np.sum(image > params['DARK_CUTLIMIT'])
        baddark /= np.product(image.shape)
    # log the fraction of bad dark pixels
    wargs = [params['DARK_CUTLIMIT'], baddark]
    WLOG(params, 'info', TextEntry('', args=wargs))
    # define mask for values above cut limit or NaN
    with warnings.catch_warnings(record=True) as w:
        datacutmask = ~((image > params['DARK_CUTLIMIT']) | nanmask)
    # get number of pixels above cut limit or NaN
    n_bad_pix = np.product(image.shape) - np.sum(datacutmask)
    # work out fraction of dead pixels + dark > cut, as percentage
    dadeadall = n_bad_pix * 100 / np.product(image.shape)
    # log fraction of dead pixels + dark > cut
    wargs = [params['DARK_CUTLIMIT'], dadeadall]
    WLOG(params, 'info', TextEntry('40-011-00007', args=wargs))
    # return dadeadall
    return baddark, dadeadall


def correction(params, image, header, nfiles=1, return_dark=False):
    """
    Corrects "image" for "dark" using calibDB file (header must contain
    value of p['ACQTIME_KEY'] as a keyword)

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                nbframes: int, the number of frames/files (usually the length
                          of "arg_file_names")
                calibDB: dictionary, the calibration database dictionary
                         (if not in "p" we construct it and need "max_time_unix"
                max_time_unix: float, the unix time to use as the time of
                                reference (used only if calibDB is not defined)
                log_opt: string, log option, normally the program name
                DRS_CALIB_DB: string, the directory that the calibration
                              files should be saved to/read from

    :param image: numpy array (2D), the image
    :param header: dictionary, the header dictionary created by
                   spirouFITS.ReadImage
    :param nfiles: int or None, number of files that created image (need to
                   multiply by this to get the total dark) if None uses
                   p['NBFRAMES']
    :param return_dark: bool, if True returns corrected_image and dark
                        if False (default) returns corrected_image

    :return corrected_image: numpy array (2D), the dark corrected image
                             only returned if return_dark = True:
    :return darkimage: numpy array (2D), the dark
    """
    func_name = __NAME__ + '.correct_for_dark()'
    # get constants from p
    use_sky = params['USE_SKYDARK_CORRECTION']
    skydark_only = params['USE_SKYDARK_ONLY']
    textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])

    # -------------------------------------------------------------------------
    # get calibDB
    cdb = drs_database.get_full_database(params, 'calibration')

    # get filename col
    filecol, timecol = cdb.file_col, cdb.time_col

    # get the dark entries
    darkentries = drs_database.get_key_from_db(params, 'DARK', cdb, header,
                                               n_ent=1, required=False)
    # get the sky entries
    skyentries = drs_database.get_key_from_db(params, 'SKYDARK', cdb, header,
                                              n_ent=1, required=False)
    # get the time used from header
    usetime = drs_database.get_header_time(params, cdb, header)

    # -------------------------------------------------------------------------
    # try to read 'DARK' from cdb
    if len(darkentries) > 0:
        darkfilename = darkentries[filecol][0]
        darkfile = os.path.join(params['DRS_CALIB_DB'], darkfilename)
        darktime = darkentries[timecol][0]
    else:
        darkfile = None
        darktime = None
    # try to read 'SKYDARK' from cdb
    if len(skyentries) > 0:
        skydarkfilename = skyentries[filecol][0]
        skydarkfile = os.path.join(params['DRS_CALIB_DB'], skydarkfilename)
        skytime = skyentries[timecol][0]
    else:
        skydarkfile = None
        skytime = None

    # -------------------------------------------------------------------------
    # load the correct dark image
    # -------------------------------------------------------------------------
    # setup logic used in multiple
    cond1 = skydarkfile is not None
    cond2 = darkfile is not None
    # if we have both darkfile and skydarkfile use the closest
    if use_sky and cond1 and cond2 and (not skydark_only):
        # find closest to obs time
        pos = np.argmin(abs(np.array([skytime, darktime]) - usetime))
        if pos == 0:
            use_file, use_type = str(skydarkfile), 'SKY'
        else:
            use_file, use_type = str(darkfile),  'DARK'
    # else if we only have sky
    elif use_sky and cond1:
        use_file, use_type = str(skydarkfile), 'SKY'
    # else if only have a dark
    elif cond2:
        use_file, use_type = str(darkfile), 'DARK'
    # else we don't have either --> error
    else:
        # deal with extra constrain on file from "closer/older"
        comptype = params.get('CALIB_DB_MATCH', None)
        if comptype == 'older':
            extstr = textdict['00-011-00004'].format(usetime)
        else:
            extstr = ''
        # log error
        eargs = [cdb.abspath, extstr, func_name]
        if use_sky and (not skydark_only):
            emsg1 = TextEntry('00-011-00001', args=eargs)
        elif use_sky and skydark_only:
            emsg1 = TextEntry('00-011-00003', args=eargs)
        else:
            emsg1 = TextEntry('00-011-00002', args=eargs)
        WLOG(params, 'error', emsg1)
        use_file, use_type = None, None
    # -------------------------------------------------------------------------
    # do dark using correct file
    darkimage, dhdr = drs_fits.read(params, use_file, gethdr=True)
    # Read dark file
    wargs = [use_type, use_file]
    WLOG(params, '', TextEntry('40-011-00011', args=wargs))
    corrected_image = image - (darkimage * nfiles)
    # -------------------------------------------------------------------------
    # get the dark filename (from header)
    params['DARKFILE'] = os.path.basename(use_file)
    params.set_source('DARKFILE', func_name)

    # finally return datac
    if return_dark:
        return params, corrected_image, darkimage
    else:
        return params, corrected_image


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
