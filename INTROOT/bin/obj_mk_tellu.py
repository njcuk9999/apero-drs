#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2018-07-12 07:49
@author: ncook
Version 0.0.1
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
import numpy as np
import os
from scipy.interpolate import InterpolatedUnivariateSpline as IUVSpline

# TODO: Remove
from astropy.io import fits
import matplotlib.pyplot as plt

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS.spirouImage import spirouFile
from SpirouDRS import spirouStartup


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
# Get Path Exception
PathException = spirouFile.PathException
# Get sigma FWHM
SIG_FWHM = spirouCore.spirouMath.fwhm
# Get plotting functions
sPlt = spirouCore.sPlt


# =============================================================================
# Define functions
# =============================================================================
def get_normalized_blaze(p, loc):
    func_name = __NAME__ + '.get_normalized_blaze()'
    # Get the blaze
    blaze = np.zeros(49, 4088)
    # we mask domains that have <20% of the peak blaze of their respective order
    blaze_norm =np.array(blaze)
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
    NPIX_ker = int(np.ceil(3 * p['FWHM_PIXEL_LSF'] * 1.5 / 2) * 2 + 1)
    # set up the kernel exponent
    ker = np.arange(NPIX_ker) - NPIX_ker // 2
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
    # TODO: Don't have data (and therefore size) at this point
    ydim, xdim = loc['DATA'].shape
    # representative atmospheric transmission
    # tapas = pyfits.getdata('tapas_model.fits')
    # TODO: Use Spirou to open file
    # TODO: Get file name from TELLUDB
    tapas = Table.read(file_tapas_spectra)
    # tapas spectra resampled onto our data wavelength vector
    tapas_all_species = np.zeros([len(p['TELLU_ABSORBERS']), xdim * ydim])
    # TODO: Get tapas_file_name from SpirouConstants
    tapas_file_name = wave_file.replace('.fits', '_tapas_convolved.npy')
    # if we already have a file for this wavelength just open it
    try:
        # load with numpy
        tapas_all_species = np.load(tapas_file_name)
        # log loading
        wmsg = 'Loading Tapas convolve file: {0}'
        WLOG('', p['LOG_OPT'], tapas_file_name)
    # if we don't have a tapas file for this wavelength soltuion calculate it
    except:
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


def main(night_name=None, files=None):
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)
    p = spirouStartup.LoadArguments(p, night_name, files)
    p = spirouStartup.InitialFileSetup(p, skipcheck=True)
    # set up data storage
    loc = ParamDict()

    # ------------------------------------------------------------------
    # Load first file
    # ------------------------------------------------------------------
    # TODO: Need to get a first file
    #
    data = fits.getdata(p['FITSFILENAME'])
    ydim, xdim = data.shape

    # TODO ============================
    # TODO FOR CONSTANT FILES
    # TODO ============================
    p['TELLU_FIBER'] = 'AB'
    p['TELLU_SUFFIX'] = 'e2dsff'
    p['TELLU_BLAZE_PERCENTILE'] = 95
    # level above which the blaze is high enough to accurately measure telluric
    p['CUT_BLAZE_NORM'] = 0.2
    # mean line width expressed in pix
    p['FWHM_PIXEL_LSF'] = 2.1
    # list of absorbers in the tapas fits table
    p['TELLU_ABSORBERS'] = ['combined','h2o','o3','n2o','o2','co2','ch4']
    # min transmission in tapas models to consider an element part of continuum
    p['TRANSMISSION_CUT'] = 0.98
    # number of iterations to find the SED of hot stars + sigma clipping
    p['N_ITER_SED_HOTSTAR'] = 5
    # smoothing parameter for the interpolation of the hot star continuum.
    #     Needs to be reasonably matched to the true width
    p['TELLU_VSINI'] = 250.0
    # median sampling expressed in km/s / pix
    p['TELLU_MED_SAMPLING'] = 2.2
    #
    p['TELLU_SIGMA_DEV'] = 5
    #
    p['TELLU_BAD_THRESHOLD'] = 1.2

    p['TELLU_NAN_THRESHOLD'] = 0.2

    p['TELLU_ABSO_MAPS'] = False

    p['TELLU_ABSO_LOW_THRES'] = 0.01
    p['TELLU_ABSO_HIGH_THRES'] = 1.05

    p['TELLU_ABSO_SIG_N_ITER'] = 5

    p['TELLU_ABSO_SIG_THRESH'] = -1

    p['TELLU_ABSO_DV_ORDER'] = 33

    p['TELLU_ABSO_DV_SIZE'] = 5

    p['TELLU_ABSO_DV_GOOD_THRES'] = 0.2

    # ------------------------------------------------------------------
    # Get the wave solution
    # ------------------------------------------------------------------
    wave = np.zeros(49, 4088)

    # ------------------------------------------------------------------
    # Get and Normalise the blaze
    # ------------------------------------------------------------------
    loc = get_normalized_blaze(p, loc)

    # ------------------------------------------------------------------
    # Construct convolution kernel
    # ------------------------------------------------------------------
    loc = construct_convolution_kernal1(p, loc)

    # ------------------------------------------------------------------
    # Get molecular telluric lines
    # ------------------------------------------------------------------
    loc = get_molecular_tell_lines(p, loc)

    # ------------------------------------------------------------------
    # Loop around the files
    # ------------------------------------------------------------------
    # construct extension
    tellu_ext = '{0}_{1}.fits'
    # storage for valid output files
    loc['OUTPUTFILES'] = []
    # loop around the files
    for basefilename in p['ARG_FILE_NAMES']:
        # ------------------------------------------------------------------
        # TODO: Move to recipe control
        # Check that we can process file
        # ------------------------------------------------------------------
        filename = os.path.join(p['ARG_FILE_DIR'], basefilename)
        # check if ufile exists
        if not os.path.exists(filename):
            wmsg = 'File {0} does not exist... skipping'
            WLOG('warning', p['LOG_OPT'], wmsg.format(basefilename))
            continue
        elif tellu_ext not in basefilename:
            wmsg = 'Incorrect File {0} type... skipping'
            WLOG('warning', p['LOG_OPT'], wmsg.format(basefilename))
            continue

        # ------------------------------------------------------------------
        # Read obj telluric file and correct for blaze
        # ------------------------------------------------------------------
        # TODO: Open with SPIROU DRS
        sp = fits.getdata(filename) / loc['BLAZE']

        # get output transmission filename
        # TODO: Move to spirouConfig
        outfilename = basefilename.replace('_trans.fits', '.fits')
        outfile = os.path.join(p['ARG_FILE_DIR'], outfilename)
        loc['OUTPUTFILES'].append(outfile)

        # if we already have the file skip it
        if os.path.exists(outfile):
            wmsg = 'File {0} exists, skipping'
            WLOG('', p['LOG_OPT'], wmsg.format(outfilename))
            continue

        # ------------------------------------------------------------------
        # loop around the orders
        # ------------------------------------------------------------------

        # define storage for the transmission map
        transmission_map = np.zeros_like(data)
        # loop around the orders
        for order_num in range(loc['DATA'].shape[0]):
            # start and end
            start = order_num * xdim
            end = (order_num * xdim) + xdim
            # get this orders combined tapas transmission
            trans = loc['TAPAS_ALL_SPECIES'][0, start:end]
            # keep track of the pixels that are considered valid for the SED
            #    determination
            mask1 = trans > p['TRANSMISSION_CUT']
            mask1 &= np.isfinite((p['NBLAZE'][order_num]))
            # normalise the spectrum
            sp[order_num, :] /= np.nanmedian(sp[order_num, :])
            # create a float mask
            fmask = np.array(mask1, dtype=float)
            # set up an SED to fill
            sed = np.ones(xdim)
            # sigma clip until limit
            for it in range(p['N_ITER_SED_HOTSTAR']):
                # copy the spectrum
                sp2 = np.array(sp[order_num, :])
                # multiple by the float mask
                sp2 *= fmask
                # convolve with the second kernel
                sp2b = np.convolve(sp2/sed, loc['KER2'], mode='same')
                # convolve with mask to get weights
                ww = np.convolve(fmask, loc['KER2'], mode='same')
                # normalise the spectrum by the weights
                sp2bw = sp2b / ww
                # set zero pixels to 1
                sp2bw[sp2b == 0] = 1
                # recalculate the mask using the deviation from original
                dev = (sp2bw - sp[order_num, :] / sed)
                dev /= np.nanmedian(np.abs(dev))
                mask = mask1 * (np.abs(dev) < p['TELLU_SIGMA_DEV'])
                # update the SED with the corrected spectrum
                sed *= sp2bw
            # identify bad pixels
            bad = (sp[order_num, :] / sed[:] > 1.2)
            sed[bad] = np.nan

            # debug plot
            if p['DRS_DEBUG'] > 1:
                # TODO add plot to spirouPLOT
                wave = loc['WAVE'][order_num, :]
                plt.plot(wave, sp[order_num, :], 'r.')
                plt.plot(wave, sp[order_num, fmask], 'b.')
                plt.plot(wave, sed, 'r-')
                plt.plot(wave, trans, 'c-')
                plt.plot(wave, sp[order_num, :] / sed[:], 'g-')
                plt.plot(wave, np.ones_like(sed), 'r-')
                plt.plot(wave, ww, 'k-')
                plt.title(outfilename)
                plt.show()
                plt.close()

            # set all values below a threshold to NaN
            sed[ww < p['TELLU_NAN_THRESHOLD']] = np.nan
            # save the spectrum (normalised by the SED) to the tranmission map
            transmission_map[order_num, :] = sp[order_num, :] / sed

        # ------------------------------------------------------------------
        # Save transmission map to file
        # ------------------------------------------------------------------
        # TODO: Use SPIROU DRS (and copy header keys!)
        fits.writeto(outfilename, transmission_map, clobber=True)

        # ------------------------------------------------------------------
        # Add transmission map to telluDB
        # ------------------------------------------------------------------
        # TODO

    # ----------------------------------------------------------------------
    # Optional Absorption maps
    # ----------------------------------------------------------------------
    if p['TELLU_ABSO_MAPS']:
        # ------------------------------------------------------------------
        # Generate the absorption map
        # ------------------------------------------------------------------
        # get number of files
        nfiles = len(p['OUTPUTFILES'])
        # set up storage for the absorption
        abso = np.zeros([nfiles, ydim*xdim])
        # loop around outputfiles and add them to abso
        for it, filename in enumerate(p['OUTPUTFILES']):
            # push data into array
            # TODO: Open with SPIROU DRS
            abso[it, :] = fits.getdata(filename).reshape(xdim * ydim)
        # set values less than low threshold to low threshold
        # set values higher than high threshold to 1
        low, high = p['TELLU_ABSO_LOW_THRES'], p['TELLU_ABSO_HIGH_THRES']
        abso[abso < low] = low
        abso[abso > high] = 1.0
        # set values less than CUT_BLAZE_NORM threshold to NaN
        abso[loc['NBLAZE'] < p['CUT_BLAZE_NORM']] = np.nan
        # write thie map to file
        # TODO: Save with SPIROU DRS
        fits.writeto('abso_map.fits', abso.reshape(nfiles,ydim,xdim),
                     clobber=True)
        # ------------------------------------------------------------------
        # Generate the median and normalized absorption maps
        # ------------------------------------------------------------------
        # copy the absorption cube
        abso2 = np.array(abso)
        # log the absorption cube
        log_abso = np.log(abso)
        # get the threshold from p
        threshold = p['TELLU_ABSO_SIG_THRESH']
        # calculate the abso_med
        abso_med = np.nanmedian(log_abso, axis=0)
        # sigma clip around the median
        for it in range(p['TELLU_ABSO_SIG_N_ITER']):
            # recalculate the abso_med
            abso_med = np.nanmedian(log_abso, axis=0)
            # loop around each file
            for jt in range(nfiles):
                # get this iterations row
                rowvalue = log_abso[jt, :]
                # get the mask of those values above threshold
                goodpix = (rowvalue > threshold) & (abso_med > threshold)
                # apply the mask of good pixels to work out ratio
                part1 = np.sum(rowvalue[goodpix] * abso_med[goodpix])
                part2 = np.sum(abso_med[goodpix] ** 2)
                ratio = part1/part2
                # store normalised absol back on to log_abso
                log_abso[jt, :] = log_abso[jt, :] / ratio

        # unlog log_abso
        abso_out = np.exp(log_abso)

        # calculate the median of the log_abso
        abso_med_out = np.exp(np.nanmedian(log_abso, axis=0))
        # reshape the median
        abso_map_n = abso_med_out.reshape(ydim, xdim)

        # finally save the maps to file
        # TODO: Move file to spirouConst
        abso_med_file = 'abso_median.fits'
        abso_map_n_file = 'abso_map_norm.fits'
        fits.writeto(abso_med_file, abso_med_out, clobber=True)
        fits.writeto(abso_map_n_file, abso_map_n, clobber=True)
        # ------------------------------------------------------------------
        # calculate dv statistic
        # ------------------------------------------------------------------
        # get the order for dv calculation
        dvselect = p['TELLU_ABSO_DV_ORDER']
        size = p['TELLU_ABSO_DV_SIZE']
        threshold2 = p['TELLU_ABSO_DV_GOOD_THRES']
        fitdeg = p['TELLU_ABSO_FIT_DEG']
        # get the start and end points of this order
        start, end = xdim * dvselect + size, xdim * dvselect - size + xdim
        # get the median for selected order
        abso_med2 = np.exp(abso_med[start:end])
        # get the dv pixels to extract
        dvpixels = np.arange(-np.floor(size/2), np.ceil(size/2), 1)
        # loop around files
        for it, filename in enumerate(p['OUTPUTFILES']):
            # storage for the extracted abso ratios for this file
            cc = np.zeros(size)
            # loop around a box of size="size"
            for jt, dv in dvpixels:
                # get the start and end position
                start = xdim * dvselect + size + dv
                end = xdim * dvselect + xdim - size + dv
                # get the log abso for this iteration
                rowvalue = np.exp(log_abso[it, start:end])
                # find the good pixels
                goodpix = (rowvalue > threshold2) & (abso_med2 > threshold2)
                # get the ratio
                part1 = np.sum(rowvalue[goodpix] * abso_med2[goodpix])
                part2 = np.sum(abso_med2[goodpix] ** 2)
                cc[jt] = part1/part2
            # fit the ratio across the points
            cfit = np.polyfit(dvpixels, cc, fitdeg)
            # work out the dv pix
            # TODO: Is this related to the derivative?
            dvpix = -0.5 * (cfit[1] / cfit[0])
            # log stats
            wmsg = 'File: "{0}", dv={1}'
            WLOG('', p['LOG_OPT'], wmsg.format(filename, dvpix))


    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    wmsg = 'Recipe {0} has been successfully completed'
    WLOG('info', p['LOG_OPT'], wmsg.format(p['PROGRAM']))
    # return a copy of locally defined variables in the memory
    return dict(locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()
    # exit message if in debug mode
    spirouStartup.Exit(ll)

# =============================================================================
# End of code
# =============================================================================






# =============================================================================