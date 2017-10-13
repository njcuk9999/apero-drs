#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cal_DARK_spirou.py [night_directory] [fitsfilename]

Prepares the dark files for SPIRou

Created on 2017-10-11 at 10:45

@author: cook

Version 0.0.1

Last modified: 2017-10-11 at 10:49
"""
import sys
import numpy as np

import startup
import general_functions as gf

# =============================================================================
# Define variables
# =============================================================================
WLOG = startup.log.logger
# -----------------------------------------------------------------------------


# =============================================================================
# Define functions
# =============================================================================
def measure_dark(pp, image, image_name):
    """
    Measure the dark pixels in "image"

    :param pp: dictionary, parameter dictionary
    :param image: numpy array (2D), the image
    :param image_name: string, the name of the image (for logging and parameter
                       naming - parmaeters added to pp with suffix)
    :return pp: dictionary, parameter dictionary
    """

    # flatten the image
    fimage = image.flat
    # get the finite (non-NaN) mask
    fimage = fimage[np.isfinite(fimage)]
    # get the number of NaNs
    imax = image.size - len(fimage)
    # get the median value of the non-NaN data
    med = np.median(fimage)
    # get the 5th and 95h percentile qmin
    qmin, qmax = np.percentile(fimage, [pp['DARK_QMIN'], pp['DARK_QMAX']])
    # get the histogram for flattened data
    histo = np.histogram(fimage, bins=p['HISTO_BINS'],
                         range=(pp['HISTO_RANGE_LOW'], pp['HISTO_RANGE_HIGH']))
    # get the fraction of dead pixels as a percentage
    dadead = imax * 100 / np.product(image.shape)
    # log the dark statistics
    logargs = ['In {0}'.format(image_name), dadead, med, pp['DARK_QMIN'],
               pp['DARK_QMAX'], qmin, qmax]
    WLOG('info', pp['log_opt'], ('{0:12s}: Frac dead pixels= {1:.1f} % - '
                                 'Median= {2:.2f} ADU/s - '
                                 'Percent[{3}:{4}]= {5:.2f}-{6:.2f} ADU/s'
                                 '').format(*logargs))
    # add required variables to pp
    pp['histo {0}'.format(image_name)] = histo

    return pp

# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from configuration files and run time arguments
    p = startup.RunInitialStartup()
    # run specific start up
    p = startup.RunStartup(p, kind='dark', prefixes=['dark_dark'])

    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read the image data
    data, hdr, nx, ny = gf.ReadImage(p, framemath='average')
    # get ccd sig det value
    p['ccdsigdet'] = float(gf.GetKey(p, hdr, 'RDNOISE', hdr['@@@hname']))
    # get exposure time
    p['exptime'] = float(gf.GetKey(p, hdr, 'EXPTIME', hdr['@@@hname']))
    # get gain
    p['gain'] = float(gf.GetKey(p, hdr, 'GAIN', hdr['@@@hname']))
    # log the Dark exposure time
    WLOG('info', p['log_opt'], 'Dark Time = {0:.3f} [s]'.format(p['exptime']))
    # Quality control: make sure the exposure time is longer than qc_dark_time
    if p['exptime'] < p['QC_DARK_TIME']:
        WLOG('error', p['log_opt'], 'Dark exposure time too short')
        sys.exit(1)

    # ----------------------------------------------------------------------
    # Resize image
    # ----------------------------------------------------------------------
    # convert NaN to zeros
    data0 = np.where(~np.isfinite(data), 0.0, data)
    # resize blue image
    bkwargs = dict(xlow=p['IC_CCDX_BLUE_LOW'], xhigh=p['IC_CCDX_BLUE_HIGH'],
                   ylow=p['IC_CCDY_BLUE_LOW'], yhigh=p['IC_CCDY_BLUE_HIGH'])
    datablue, nx2, ny2 = gf.ResizeImage(data, **bkwargs)
    # Make sure we have data in the blue image
    if nx2 == 0 or ny2 == 0:
        WLOG('error', p['log_opt'], ('IC_CCD(X/Y)_BLUE_(LOW/HIGH) remove '
                                     'all pixels from image.'))
        sys.exit(1)
    # resize red image
    rkwargs = dict(xlow=p['IC_CCDX_RED_LOW'], xhigh=p['IC_CCDX_RED_HIGH'],
                   ylow=p['IC_CCDY_RED_LOW'], yhigh=p['IC_CCDY_RED_HIGH'])
    datared, nx3, ny3 = gf.ResizeImage(data, **rkwargs)
    # Make sure we have data in the red image
    if nx3 == 0 or ny3 == 0:
        WLOG('error', p['log_opt'], ('IC_CCD(X/Y)_RED_(LOW/HIGH) remove '
                                     'all pixels from image.'))
        sys.exit(1)

    # ----------------------------------------------------------------------
    # Dark Measurement
    # ----------------------------------------------------------------------
    # Log that we are doing dark measurement
    WLOG('', p['log_opt'], 'Doing Dark measurement')
    # measure dark for whole frame
    p = measure_dark(p, data, 'Whole det')
    # measure dark for blue part
    p = measure_dark(p, datablue, 'Blue part')
    # measure dark for rede part
    p = measure_dark(p, datared, 'Red part')

    # ----------------------------------------------------------------------
    # Identification of bad pixels
    # ----------------------------------------------------------------------
    # define mask for values above cut limit or NaN
    datacutmask = data[np.isfinite(data)] <= p['DARK_CUTLIMIT']
    # get number of pixels above cut limit or NaN
    n_bad_pix = np.product(data.shape) - np.sum(datacutmask)
    # work out fraction of dead pixels + dark > cut, as percentage
    dadeadall = n_bad_pix * 100 / np.product(data.shape)
    # log fraction of dead pixels + dark > cut
    logargs = [p['DARK_CUTLIMIT'], dadeadall]
    WLOG('info', p['log_opt'], ('Total Frac dead pixels (N.A.N) + DARK > '
                                '{0:.1f} ADU/s = {1:.1f} %').format(*logargs))

    # ----------------------------------------------------------------------
    # Plots
    # ----------------------------------------------------------------------
    # TODO: code

    # ----------------------------------------------------------------------
    # Quality control
    # ----------------------------------------------------------------------
    # TODO: code

    # ----------------------------------------------------------------------
    # Save dark to calibDB
    # ----------------------------------------------------------------------
    # TODO: code

    # ----------------------------------------------------------------------
    # Save bad pixel mask
    # ----------------------------------------------------------------------
    # TODO: code

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    WLOG('info', p['log_opt'], ('Recipe {0} has been succesfully completed'
                                '').format(p['program']))

# =============================================================================
# End of code
# =============================================================================
