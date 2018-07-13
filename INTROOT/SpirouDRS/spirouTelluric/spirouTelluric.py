#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2018-07-12 16:28
@author: ncook
Version 0.0.1
"""
from __future__ import division
import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline as IUVSpline

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouDB
from SpirouDRS import spirouImage

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'obj_mk_tellu.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# Custom parameter dictionary
ParamDict = spirouConfig.ParamDict
# Get sigma FWHM
SIG_FWHM = spirouCore.spirouMath.fwhm


# =============================================================================
# Define functions
# =============================================================================
def get_normalized_blaze(p, loc):
    func_name = __NAME__ + '.get_normalized_blaze()'
    # Get the blaze
    blaze = np.zeros(49, 4088)
    # we mask domains that have <20% of the peak blaze of their respective order
    blaze_norm = np.array(blaze)
    for iord in range(blaze.shape[0]):
        blaze_norm[iord, :] /= np.percentile(blaze_norm[iord, :],
                                             p['TELLU_BLAZE_PERCENTILE'])
    blaze_norm[blaze_norm < p['CUT_BLAZE_NORM']] = np.nan
    # add to loc
    loc['BLAZE'] = blaze
    loc['NBLAZE'] = blaze_norm
    loc.set_sources(['BLAZE', 'NBLAZE'], func_name)
    # return loc
    return loc


def construct_convolution_kernal1(p, loc):
    func_name = __NAME__ + '.construct_convolution_kernal()'
    # get the number of kernal pixels
    npix_ker = int(np.ceil(3 * p['FWHM_PIXEL_LSF'] * 1.5 / 2) * 2 + 1)
    # set up the kernel exponent
    ker = np.arange(npix_ker) - npix_ker // 2
    # kernal is the a gaussian
    ker = np.exp(-0.5 * (ker / (p['FWHM_PIXEL_LSF'] / SIG_FWHM)) ** 2)
    # we only want an approximation of the absorption to find the continuum
    #    and estimate chemical abundances.
    #    there's no need for a varying kernel shape
    ker /= np.sum(ker)
    # add to loc
    loc['KER'] = ker
    loc.set_source('KER', func_name)
    # return loc
    return loc


def get_molecular_tell_lines(p, loc):
    func_name = __NAME__ + '.get_molecular_tell_lines()'
    # get x and y dimension
    ydim, xdim = loc['DATA'].shape
    # representative atmospheric transmission
    # tapas = pyfits.getdata('tapas_model.fits')
    tapas_file = spirouDB.GetDatabaseTellMole(p)
    tdata = spirouImage.ReadImage(p, tapas_file, kind='FLAT')
    tapas, thdr, tcmt, _, _ = tdata
    # tapas spectra resampled onto our data wavelength vector
    tapas_all_species = np.zeros([len(p['TELLU_ABSORBERS']), xdim * ydim])
    # TODO: Get tapas_file_name from SpirouConstants
    # TODO: where do we get wave file from now constants are from E2DS file???
    tapas_file_name = wave_file.replace('.fits', '_tapas_convolved.npy')
    # if we already have a file for this wavelength just open it
    try:
        # load with numpy
        tapas_all_species = np.load(tapas_file_name)
        # log loading
        wmsg = 'Loading Tapas convolve file: {0}'
        WLOG('', p['LOG_OPT'], wmsg.format(tapas_file_name))
    # if we don't have a tapas file for this wavelength soltuion calculate it
    except Exception:
        # loop around each molecule in the absorbers list
        #    (must be in
        for n_species, molecule in enumerate(p['TELLU_ABSORBERS']):
            print('molecule --> ' + molecule)
            # log process
            wmsg = 'Processing molecule: {0}'
            WLOG('', p['LOG_OPT'], wmsg.format(molecule))
            # get wavelengths
            lam = tapas['wavelength']
            # get molecule transmission
            trans = tapas['trans_{0}'.format(molecule)]
            # interpolate with Univariate Spline
            tapas_spline = IUVSpline(lam, trans)
            # log the mean transmission level
            wmsg = 'Mean Trans level: {0}'.format(np.mean(trans))
            WLOG('', p['LOG_OPT'], wmsg)
            # convolve all tapas absorption to the SPIRou approximate resolution
            for iord in range(49):
                # get the order position
                start = iord * xdim
                end = (iord * xdim) + xdim
                # interpolate the values at these points
                svalues = tapas_spline(loc['WAVE'][iord, :])
                # convolve with a gaussian function
                cvalues = np.convolve(svalues, loc['KER'], mode='same')
                # add to storage
                tapas_all_species[n_species, start: end] = cvalues
        # deal with non-real values (must be between 0 and 1
        tapas_all_species[tapas_all_species > 1] = 1
        tapas_all_species[tapas_all_species < 0] = 0
        # save the file
        np.save(tapas_file_name, tapas_all_species)
    # finally add all species to loc
    loc['TAPAS_ALL_SPECIES'] = tapas_all_species
    loc.set_sourceS('TAPAS_ALL_SPECIES', func_name)
    # return loc
    return loc


def construct_convolution_kernal2(p, loc):
    func_name = __NAME__ + '.construct_convolution_kernal2()'

    # gaussian ew for vinsi km/s
    ew = p['TELLU_VSINI'] / p['TELLU_MED_SAMPLING'] / 2.354
    # set up the kernel exponent
    xx = np.arange(ew * 6) - ew * 3
    # kernal is the a gaussian
    ker2 = np.exp(-.5 * (xx / ew) ** 2)

    ker2 /= np.sum(ker2)
    # add to loc
    loc['KER2'] = ker2
    loc.set_source('KER2', func_name)
    # return loc
    return loc


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # Main code here
    pass

# =============================================================================
# End of code
# =============================================================================
