#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-02-07 at 17:20

@author: cook
"""
import numpy as np
import os
from astropy.table import Table
import matplotlib.pyplot as plt

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'check_for_corrupt_files.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt
# Get parameter dictionary
ParamDict = spirouConfig.ParamDict

EXTS = ['a.fits', 'c.fits', 'd.fits', 'f.fits', 'o.fits']
OUTPATH = '/spirou/cook/corrupt_files/corruption_list.fits'

# =============================================================================
# Define functions
# =============================================================================
def get_full_flat(p):
    # get parameters from p
    filename = p['BADPIX_FULL_FLAT']
    threshold = p['BADPIX_FULL_THRESHOLD']
    # construct filepath
    package = spirouConfig.Constants.PACKAGE()
    relfolder = spirouConfig.Constants.BADPIX_DIR()
    datadir = spirouConfig.GetAbsFolderPath(package, relfolder)
    absfilename = os.path.join(datadir, filename)
    # check that filepath exists
    if not os.path.exists(absfilename):
        emsg = 'badpix full flat ({0}) not found in {1}. Please correct.'
        WLOG(p, 'error', emsg.format(filename, datadir))
    # read image
    mdata, _, _, _ = spirouImage.ReadImage(p, absfilename, kind='FULLFLAT')
    # return image
    return mdata


def get_full_flat_hotpix(p):
    # get full badpixel file
    full_badpix = get_full_flat(p)
    # get shape of full badpixel file
    dim1, dim2 = full_badpix.shape

    # get the med_size
    med_size = p['PP_CORRUPT_MED_SIZE']
    # get the hot pix threshold
    hot_thres = p['PP_CORRUPT_HOT_THRES']

    # get size of dark region
    pixels_per_amp = dim2 // p['TOTAL_AMP_NUM']
    dark_size = p['NUMBER_DARK_AMP'] * pixels_per_amp

    # mask the full_badpix (do not include dark area or edges)
    full_badpix[:, dark_size:] = np.nan
    full_badpix[:med_size, :] = np.nan
    full_badpix[:, :med_size] = np.nan
    full_badpix[-med_size:, :] = np.nan
    full_badpix[:, -med_size:] = np.nan

    for ix in range(med_size,dark_size):
        full_badpix[:,ix] -= np.nanmedian(full_badpix[:,ix])
    for iy in range(dim1):
        full_badpix[iy,:] -= np.nanmedian(full_badpix[iy,:])

    full_badpix[~np.isfinite(full_badpix)] = 0.0

    # locate hot pixels in the full bad pix
    yhot, xhot = np.where(full_badpix > hot_thres)

    # return the hot pixel indices
    return yhot, xhot


def get_all_fits_files(p, path):
    fitsfiles = []
    # walk through all sub-directories
    for root, dirs, files in os.walk(path):
        # loop around files in each sub-directory
        for filename in files:
            # check if file has valid extension
            valid = False
            for ext in EXTS:
                if filename.endswith(ext) :
                    valid = True
            if not valid:
                continue
            else:
                fitsfiles.append(os.path.join(root, filename))
    # log found files
    WLOG(p, '', 'Found {0} valid fits files'.format(len(fitsfiles)))

    # return list of files
    return fitsfiles


def find_hotpix_offset(p, filename, yhot, xhot):
    # get the med_size
    med_size = p['PP_CORRUPT_MED_SIZE']
    # get data
    try:
        data, hdr, _, _ = spirouImage.ReadImage(p, filename, kind='None',
                                                log=False)
    except SystemExit:
        return np.nan

    if p['KW_EXPTIME'][0] in hdr:
        exptime = hdr[p['KW_EXPTIME'][0]]
    else:
        exptime = np.nan

    # get median hot pixel box
    med_hotpix = np.zeros([2 * med_size + 1, 2 * med_size + 1])
    # loop around x
    for dx in range(-med_size, med_size + 1):
        # loop around y
        for dy in range(-med_size, med_size + 1):
            # define position in median box
            posx = dx + med_size
            posy = dy + med_size
            # get the hot pixel values at position in median box
            data_hot = np.array(data[yhot + dx, xhot + dy])
            # median the data_hot for this box position
            med_hotpix[posx, posy] = np.nanmedian(data_hot)
    # work out an rms
    res = med_hotpix - np.nanmedian(med_hotpix)

    rms = np.nanmedian(np.abs(res))

    snr_hotpix = res[med_size, med_size] / rms

    # return rms
    return snr_hotpix, exptime


def update_table(path, outtable, file_values, snr_values, exp_values):

    if os.path.exists(path) and (outtable is None):
        oldtable = Table.read(path)
        file_values = list(oldtable['FILENAME']) + file_values
        snr_values = list(oldtable['SNR_HOTPIX']) + snr_values
        exp_values = list(oldtable['EXP_TIME']) + exp_values

    # make new table with updated values
    outtable = Table()
    outtable['FILENAME'] = file_values
    outtable['SNR_HOTPIX'] = snr_values
    outtable['EXP_TIME'] = exp_values
    outtable.write(path, format='fits', overwrite=True)
    return outtable


def plot(outtable):
    plt.close()
    fig, frame = plt.subplots(ncols=1, nrows=1)
    x, y = outtable['EXP_TIME'], outtable['SNR_HOTPIX']
    mask = np.isfinite(y) & np.isfinite(x)
    frame.scatter(x[mask], y[mask])

    ylim = [-np.nanpercentile(y[mask], 2),
            np.nanpercentile(y[mask], 99) + np.nanpercentile(y[mask], 2)]

    frame.set(xlabel='Exposure time', ylabel='SNR hot pix',
              ylim=ylim)
    plt.show()
    plt.close()


# main function
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    p = spirouStartup.Begin(recipe=__NAME__)
    p = spirouStartup.LoadArguments(p, None, require_night_name=None)

    # ----------------------------------------------------------------------
    # define constants for constants file
    # ----------------------------------------------------------------------
    # Defines the size around badpixels that is considered part of the bad pixel
    p['PP_CORRUPT_MED_SIZE'] = 2
    # Defines the threshold (above the full engineering flat) that selects bad
    # (hot) pixels
    p['PP_CORRUPT_HOT_THRES'] = 2

    # ----------------------------------------------------------------------
    # get the x and y locations of the hot pixels
    yhot, xhot = get_full_flat_hotpix(p)
    # ----------------------------------------------------------------------
    # get the file list
    filelist = get_all_fits_files(p, p['DRS_DATA_RAW'])
    # ----------------------------------------------------------------------
    # load outfile/outtable
    outtable = update_table(OUTPATH, None, [], [], [])

    # ----------------------------------------------------------------------
    # store rms values
    snr_array = list(outtable['SNR_HOTPIX'])
    exp_array = list(outtable['EXP_TIME'])
    file_array = list(outtable['FILENAME'])

    current_dir = ''
    # loop around files and save RMS value
    for it, filename in enumerate(filelist):

        # print current dir when it changes
        dirname = os.path.dirname(filename)
        if current_dir != dirname:
            current_dir = str(dirname)
            wmsg = 'Current directory: {0}'.format(dirname)
            WLOG(p, 'info', wmsg)

        # skip if we already have entry
        if filename in outtable['FILENAME']:
            wmsg = '\tSkipping file {0} of {1}'.format(it +1, len(filelist))
            WLOG(p, '', wmsg)
            continue
        # print progress
        wmsg = '\tAnalysing file {0} of {1}'.format(it + 1, len(filelist))
        WLOG(p, '', wmsg)
        # get the  snr of the hotpix
        try:
            snr_hot, exp_time = find_hotpix_offset(p, filename, yhot, xhot)
        except Exception as e:
            print('\tError caught')
            print('\tError {0}: {1}'.format(type(e), e))
            snr_hot = np.nan
            exp_time = np.nan

        # add to array
        snr_array.append(snr_hot)
        file_array.append(filename)
        exp_array.append(exp_time)
        # write to output table
        outtable = update_table(OUTPATH, outtable, file_array, snr_array,
                                exp_array)


    threshold = 100

    bad_files = np.array(snr_array) < threshold

    outtable[bad_files].pprint(max_lines=999)


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
