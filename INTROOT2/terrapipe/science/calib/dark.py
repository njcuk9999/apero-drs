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
from terrapipe import locale
from terrapipe import config
from terrapipe.config import drs_log
from terrapipe.config.core import drs_file
from terrapipe.config.core import drs_database
from terrapipe.io import drs_fits
from terrapipe.io import drs_path
from terrapipe.io import drs_table

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
# alias pcheck
pcheck = config.pcheck


# =============================================================================
# Define dark functions
# =============================================================================
def measure_dark(params, image, entry_key, **kwargs):
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
    # check that params contains required parameters
    dark_qmin = pcheck(params, 'DARK_QMIN', 'dark_qmin', kwargs, func_name)
    dark_qmax = pcheck(params, 'DARK_QMAX', 'dark_qmax', kwargs, func_name)
    hbins = pcheck(params, 'HISTO_BINS', 'hbins', kwargs, func_name)
    hrangelow = pcheck(params, 'HISTO_RANGE_LOW', 'hlow', kwargs, func_name)
    hrangehigh = pcheck(params, 'HISTO_RANGE_HIGH', 'hhigh', kwargs, func_name)
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


def measure_dark_badpix(params, image, nanmask, **kwargs):
    """
    Measure the bad pixels (non-dark pixels and NaN pixels)

    :param params: parameter dictionary, ParamDict containing constants
            Must contain at least:
                DARK_CUT_LIMIT
    :param image: numpy array (2D), the image
    :param nanmask: numpy array (2D), the make of non-finite values
    :return:
    """
    func_name = __NAME__ + '.measure_dark_badpix()'
    # get constants from params/kwargs
    darkcutlimit = pcheck(params, 'DARK_CUTLIMIT', 'darkcutlimit', kwargs,
                           func_name)
    # get number of bad dark pixels (as a fraction of total pixels)
    with warnings.catch_warnings(record=True) as w:
        baddark = 100.0 * np.sum(image > darkcutlimit)
        baddark /= np.product(image.shape)
    # log the fraction of bad dark pixels
    wargs = [darkcutlimit, baddark]
    WLOG(params, 'info', TextEntry('', args=wargs))
    # define mask for values above cut limit or NaN
    with warnings.catch_warnings(record=True) as w:
        datacutmask = ~((image > darkcutlimit) | nanmask)
    # get number of pixels above cut limit or NaN
    n_bad_pix = np.product(image.shape) - np.sum(datacutmask)
    # work out fraction of dead pixels + dark > cut, as percentage
    dadeadall = n_bad_pix * 100 / np.product(image.shape)
    # log fraction of dead pixels + dark > cut
    wargs = [darkcutlimit, dadeadall]
    WLOG(params, 'info', TextEntry('40-011-00007', args=wargs))
    # return dadeadall
    return baddark, dadeadall


def correction(params, image, header, nfiles=1, return_dark=False, **kwargs):
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
    # get constants from params/kwargs
    use_sky = pcheck(params, 'USE_SKYDARK_CORRECTION', 'use_sky', kwargs,
                     func_name)
    skydark_only = pcheck(params, 'USE_SKYDARK_ONLY', 'skydark_only', kwargs,
                          func_name)
    comptype = pcheck(params, 'CALIB_DB_MATCH', 'comptype', kwargs, func_name)
    # create the text dictionary
    textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
    # -------------------------------------------------------------------------
    # get calibDB
    cdb = drs_database.get_full_database(params, 'calibration')
    # get filename col
    filecol, timecol = cdb.file_col, cdb.time_col

    # TODO: check whether we have bad pixel file set from input arguments

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
# Define master dark functions
# =============================================================================
def construct_dark_table(params, filenames):
    # define storage for table columns
    dark_time, dark_exp, dark_pp_version = [], [], []
    basenames, nightnames = [], []
    dark_wt_temp, dark_cass_temp, dark_humidity = [], [], []
    # log that we are reading all dark files
    WLOG(params, '', TextEntry('40-011-10001'))
    # loop through file headers
    for it in range(len(filenames)):
        # get the basename from filenames
        basename = os.path.basename(filenames[it])
        # get the night name
        nightname = drs_path.get_nightname(params, filenames[it])
        # read the header
        hdr = drs_fits.read_header(params, filenames[it])
        # get keys from hdr
        acqtime = drs_fits.header_time(params, hdr, 'mjd')
        exptime = hdr[params['KW_EXPTIME'][0]]
        ppversion = hdr[params['KW_PPVERSION'][0]]
        wt_temp = hdr[params['KW_WEATHER_TOWER_TEMP'][0]]
        cass_temp = hdr[params['KW_CASS_TEMP'][0]]
        humidity = hdr[params['KW_HUMIDITY'][0]]
        # append to lists
        dark_time.append(float(acqtime))
        dark_exp.append(float(exptime))
        dark_pp_version.append(ppversion)
        basenames.append(basename)
        nightnames.append(nightname)
        dark_wt_temp.append(float(wt_temp))
        dark_cass_temp.append(float(cass_temp))
        dark_humidity.append(float(humidity))
    # convert lists to table
    columns = ['NIGHTNAME', 'BASENAME', 'FILENAME', 'MJDATE', 'EXPTIME',
               'PPVERSION', 'WT_TEMP', 'CASS_TEMP', 'HUMIDITY']
    values = [nightnames, basenames, filenames, dark_time, dark_exp,
              dark_pp_version, dark_wt_temp, dark_cass_temp, dark_humidity]
    # make table using columns and values
    dark_table = drs_table.make_table(params, columns, values)
    # return table
    return dark_table


def construct_master_dark(params, dark_table, **kwargs):
    func_name = __NAME__ + '.construct_master_dark'
    # get constants from p
    time_thres = pcheck(params, 'DARK_MASTER_MATCH_TIME', 'time_thres', kwargs,
                        func_name)
    med_size = pcheck(params, 'DARK_MASTER_MED_SIZE', 'med_size', kwargs,
                      func_name)

    # get col data from dark_table
    filenames = dark_table['FILENAME']
    dark_times = dark_table['MJDATE']

    # ----------------------------------------------------------------------
    # match files by date
    # ----------------------------------------------------------------------
    # log progress
    WLOG(params, '', TextEntry('40-011-10002', args=[time_thres]))
    # match files by time
    matched_id = drs_path.group_files_by_time(params, dark_times, time_thres)
    # get the most recent position
    lastpos = np.argmax(dark_times)
    # load up the most recent dark
    data_ref, hdr_ref = drs_fits.read(params, filenames[lastpos], gethdr=True)
    # ge the reference image shape
    dim1, dim2 = data_ref.shape

    # -------------------------------------------------------------------------
    # Read individual files and sum groups
    # -------------------------------------------------------------------------
    # log process
    WLOG(params, '', TextEntry('40-011-10003'))
    # Find all unique groups
    u_groups = np.unique(matched_id)
    # currently number of bins == number of groups
    num_bins = len(u_groups)
    # storage of dark cube
    dark_cube = np.zeros([num_bins, dim1, dim2])
    bin_cube = np.zeros(num_bins)
    # loop through groups
    for g_it, group_num in enumerate(u_groups):
        # log progress
        wargs = [g_it + 1, len(u_groups)]
        WLOG(params, '', TextEntry('40-011-10004', args=wargs))
        # find all files for this group
        dark_ids = filenames[matched_id == group_num]
        # load this groups files into a cube
        cube = []
        for filename in dark_ids:
            # read data
            data_it = drs_fits.read(params, filename)
            # add to cube
            cube.append(data_it)
        # median dark cube
        groupdark = np.nanmedian(cube, axis=0)
        # sum within each bin
        dark_cube[g_it % num_bins] += groupdark
        # record the number of cubes that are going into this bin
        bin_cube[g_it % num_bins] += 1
    # need to normalize if we have more than 1 cube per bin
    for bin_it in range(num_bins):
        dark_cube[bin_it] /= bin_cube[bin_it]

    # -------------------------------------------------------------------------
    # we perform a median filter over a +/- "med_size" pixel box
    # -------------------------------------------------------------------------
    # log process
    WLOG(params, '', TextEntry('40-011-10005', args=[num_bins]))
    # storage of output dark cube
    dark_cube1 = np.zeros([num_bins, dim1, dim2])
    # loop around the bins
    for bin_it in range(num_bins):
        # get the dark for this bin
        bindark = dark_cube[bin_it]
        # performing a median filter of the image with [-med_size, med_size]
        #     box in x and 1 pixel wide in y. Skips the pixel considered,
        #     so this is equivalent of a 2*med_size boxcar
        tmp = []
        for jt in range(-med_size, med_size + 1):
            if jt != 0:
                tmp.append(np.roll(bindark, [0, jt]))
        # low frequency image
        lf_dark = np.nanmedian(tmp, axis=0)
        # high frequency image
        dark_cube1[bin_it] = bindark - lf_dark
    # -------------------------------------------------------------------------
    # median the dark cube to create the master dark
    master_dark = np.nanmedian(dark_cube1, axis=0)

    # -------------------------------------------------------------------------
    # get infile from filetype
    infile = config.get_file_definition(params['FILETYPE'],
                                        params['INSTRUMENT'])
    # set infile filename and read data
    infile.set_filename(filenames[lastpos])
    infile.read()
    # -------------------------------------------------------------------------
    # return master dark and the reference file
    return master_dark, infile


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
