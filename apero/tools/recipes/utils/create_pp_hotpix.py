#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2020-04-05 11:44:00

@author: cook
"""
import numpy as np
import os
from scipy.signal import medfilt,convolve2d
from astropy.table import Table
from astropy.io import fits
import argparse

from apero.core import constants
from apero.core import math as mp
from apero.io import drs_data


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'cal_extract_spirou.py'
__INSTRUMENT__ = 'None'
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# define the allowed instruments
INSTRUMENTS = ['SPIROU', 'NIRPS_HA']
# define box size
BOXSIZE = 5
# define hotpix thres
THRESHOLD = 10
# whether this is a debug run (produces mask image)
DEBUG = False
# define relative output path
OUTPATH = './data/{0}/engineering/'
OUTFILE = 'hotpix_pp.csv'
DEBUGFILE = 'mask_hotpix_pp.fits'


# =============================================================================
# Define functions
# =============================================================================
def get_args():
    # get parser
    description = ('Create the hotpix table for an instrument (required for'
                   ' preprocessing)')
    # set up parser
    parser = argparse.ArgumentParser(description=description)
    # add instrument
    parser.add_argument('instrument', choices=INSTRUMENTS, type=str, nargs=1,
                        help='[STRING] The instrument to process')
    parser.add_argument('directory', type=str, nargs=1,
                        help='[STRING] The night name (directory name)')
    parser.add_argument('darkfile', type=str, nargs=1,
                        help='[STRING] The raw DARK_DARK file to use')
    parser.add_argument('--debug', action='store_true',
                        default=False,
                        help='If set activates debug mode (saves mask)')
    # parse arguments
    args = parser.parse_args()
    return args


def main(instrument=None, directory=None, darkfile=None):
    pass
if __name__ == "__main__":
    instrument, directory, darkfile = None, None, None
    # deal with arguments
    if instrument is None or directory is None or darkfile is None:
        args = get_args()
        instrument = args.instrument[0]
        directory = args.directory[0]
        darkfile = args.darkfile[0]
        DEBUG = args.debug

    # deal with instrument still not correct
    if instrument not in INSTRUMENTS:
        eargs = [instrument, ' or '.join(INSTRUMENTS)]
        emsg = 'INPUT ERROR: instrument "{0}" not valid.\n\tMust be {1}'
        raise ValueError(emsg.format(*eargs))

    # get params
    params = constants.load(instrument)
    # check directory exists
    path = os.path.join(params['DRS_DATA_RAW'], directory)
    if not os.path.exists(path) and not os.path.exists(darkfile):
        emsg = 'INPUT ERROR: directory "{0}" does not exist'
        raise ValueError(emsg.format(path))
    # check for dark file
    darkfile2 = os.path.join(path, darkfile)
    if os.path.exists(darkfile):
        abspath = str(darkfile)
    elif os.path.exists(darkfile2):
        abspath = str(darkfile2)
    else:
        eargs = ['\n\t'.join([darkfile, darkfile2])]
        emsg = 'INPUT ERROR: dark file does not exist, tried: {0}'
        raise ValueError(emsg.format(*eargs))

    # ----------------------------------------------------------------------
    # Prepare dark file
    # ----------------------------------------------------------------------
    print('Loading dark and preparing image')
    # load file
    image = fits.getdata(abspath)
    # set NaNS and infs to zero. NaN pixels will not be flagged as hot pixels
    image[~np.isfinite(image)] = 0
    # subtract a DC offset of the image level
    image = image - mp.nanmedian(image)
    # express image normalized in terms of sigma
    image = image / np.nanpercentile(np.abs(image), 100 * mp.normal_fraction())

    # ----------------------------------------------------------------------
    # Find hot pixels
    # ----------------------------------------------------------------------
    print('Finding hot pixels')
    # a hot pixel is a point that is > 10 sigma (positive) and that has a
    # 5x5 median around it that is within +/- 1 sigma; it is well-behaved and
    #  not surrounded by bad pixels
    medimage = medfilt(image, [BOXSIZE, BOXSIZE])

    # find the hot pixels
    mask = (np.abs(medimage) < 1.0) & (image > THRESHOLD)
    hotpix = np.array(mask).astype(float)

    # find if hot pixels are alone in a 5x5 box
    box = np.ones([BOXSIZE, BOXSIZE]).astype(float)
    neighbours = convolve2d(hotpix, box, mode='same')

    # after the convolution, isolated (within 5x5)
    #     hotpixels have neighbours = 1
    has_neighbours = neighbours == 1
    # set non-isolated hot pixels to zero
    hotpix[~has_neighbours] = 0.0

    # find positions in x and y of good hot pixels
    y, x = np.where(hotpix)

    # ----------------------------------------------------------------------
    # write table to file
    # ----------------------------------------------------------------------
    # print progress
    print('Writing to file')
    # create table
    table = Table()
    table['nsig'] = image[y, x]
    table['xpix'] = x
    table['xpix'] = y

    # get outpath
    filename = 'hotpix'
    relpath = OUTPATH.format(instrument.lower())
    absoutpath = drs_data.construct_path(params, OUTFILE, relpath)
    # write output as a csv file
    print('\t Saved to: {0}'.format(absoutpath))
    table.write(absoutpath, format='csv', overwrite=True)

    # if debug is True save the mask (to compare to image)
    if DEBUG:
        # get debug file
        debugabspath = drs_data.construct_path(params, DEBUGFILE, relpath)
        # print progress
        print('\t Saved debug to: {0}'.format(debugabspath))
        # write to file
        fits.writeto(debugabspath, hotpix, overwrite=True)


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()

# =============================================================================
# End of code
# =============================================================================