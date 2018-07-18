#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
obj_mk_tellu [night_directory] [files]

Creates the transmission maps for a file (or individually for a set of files)
(saved into telluDB under "TELL_MAP" keys)


Created on 2018-07-12 07:49
@author: ncook
"""
from __future__ import division
import numpy as np
import os
import warnings

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouDB
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup
from SpirouDRS import spirouTelluric

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
# Get plotting functions
sPlt = spirouCore.sPlt

FORCE_PLOT_ON = False

# =============================================================================
# Define functions
# =============================================================================
def main(night_name=None, files=None):

    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)
    p = spirouStartup.LoadArguments(p, night_name, files,
                                    mainfitsdir='reduced')
    p = spirouStartup.InitialFileSetup(p, calibdb=True)
    # set up function name
    main_name = __NAME__ + '.main()'
    # ------------------------------------------------------------------
    # Load first file
    # ------------------------------------------------------------------
    loc = ParamDict()
    rd = spirouImage.ReadImage(p, p['FITSFILENAME'])
    loc['DATA'], loc['DATAHDR'], loc['DATACDR'], loc['YDIM'], loc['XDIM'] = rd
    loc.set_sources(['DATA', 'DATAHDR', 'DATACDR', 'XDIM', 'YDIM'], main_name)

    # ------------------------------------------------------------------
    # Get the wave solution
    # ------------------------------------------------------------------
    loc['WAVE'] = spirouImage.GetWaveSolution(p, loc['DATA'], loc['DATAHDR'])
    # set source
    loc.set_source('WAVE', main_name)

    # ------------------------------------------------------------------
    # Get and Normalise the blaze
    # ------------------------------------------------------------------
    loc = spirouTelluric.GetNormalizedBlaze(p, loc, loc['DATAHDR'])

    # ------------------------------------------------------------------
    # Construct convolution kernels
    # ------------------------------------------------------------------
    loc = spirouTelluric.ConstructConvKernel1(p, loc)
    loc = spirouTelluric.ConstructConvKernel2(p, loc, vsini=p['TELLU_VSINI'])

    # ------------------------------------------------------------------
    # Get molecular telluric lines
    # ------------------------------------------------------------------
    loc = spirouTelluric.GetMolecularTellLines(p, loc)

    # ------------------------------------------------------------------
    # Loop around the files
    # ------------------------------------------------------------------
    # construct extension
    tellu_ext = '{0}_{1}.fits'
    # get current telluric maps from telluDB
    tellu_db_data = spirouDB.GetDatabaseTellMap(p, required=False)
    tellu_db_files = tellu_db_data[0]
    # storage for valid output files
    loc['OUTPUTFILES'] = []
    # loop around the files
    for basefilename in p['ARG_FILE_NAMES']:
        # ------------------------------------------------------------------
        # Get absolute path of filename
        # ------------------------------------------------------------------
        filename = os.path.join(p['ARG_FILE_DIR'], basefilename)

        # ------------------------------------------------------------------
        # Read obj telluric file and correct for blaze
        # ------------------------------------------------------------------
        # get image
        sp, shdr, scdr, _, _ = spirouImage.ReadImage(p, filename)
        # divide my blaze
        sp = sp / loc['BLAZE']

        # get output transmission filename
        outfile = spirouConfig.Constants.TELLU_TRANS_MAP_FILE(p, filename)
        outfilename = os.path.basename(outfile)
        loc['OUTPUTFILES'].append(outfile)

        # if we already have the file skip it
        if outfile in tellu_db_files:
            wmsg = 'File {0} exists in telluDB, skipping'
            WLOG('', p['LOG_OPT'], wmsg.format(outfilename))
            continue

        # ------------------------------------------------------------------
        # loop around the orders
        # ------------------------------------------------------------------
        # define storage for the transmission map
        transmission_map = np.zeros_like(loc['DATA'])
        # loop around the orders
        for order_num in range(loc['DATA'].shape[0]):
            # start and end
            start = order_num * loc['XDIM']
            end = (order_num * loc['XDIM']) + loc['XDIM']
            # get this orders combined tapas transmission
            trans = loc['TAPAS_ALL_SPECIES'][0, start:end]
            # keep track of the pixels that are considered valid for the SED
            #    determination
            mask1 = trans > p['TRANSMISSION_CUT']
            mask1 &= np.isfinite(loc['NBLAZE'][order_num, :])
            # normalise the spectrum
            sp[order_num, :] /= np.nanmedian(sp[order_num, :])
            # create a float mask
            fmask = np.array(mask1, dtype=float)
            # set up an SED to fill
            sed = np.ones(loc['XDIM'])
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
                with warnings.catch_warnings(record=True) as w:
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
            if p['DRS_PLOT'] and (p['DRS_DEBUG'] > 1) and FORCE_PLOT_ON:
                # start non-interactive plot
                sPlt.plt.ioff()
                # plot the transmission map plot
                pargs = [order_num, mask1, sed, trans, sp, ww, outfilename]
                sPlt.tellu_trans_map_plot(loc, *pargs)
                # show and close
                sPlt.plt.show()
                sPlt.plt.close()


            # set all values below a threshold to NaN
            sed[ww < p['TELLU_NAN_THRESHOLD']] = np.nan
            # save the spectrum (normalised by the SED) to the tranmission map
            transmission_map[order_num, :] = sp[order_num, :] / sed

        # ------------------------------------------------------------------
        # Save transmission map to file
        # ------------------------------------------------------------------
        hdict = spirouImage.CopyOriginalKeys(loc['DATAHDR'], loc['DATACDR'])
        spirouImage.WriteImage(outfile, transmission_map, hdict)

        # ----------------------------------------------------------------------
        # Quality control
        # ----------------------------------------------------------------------
        # set passed variable and fail message list
        passed, fail_msg = True, []
        if passed:
            WLOG('info', p['LOG_OPT'],
                 'QUALITY CONTROL SUCCESSFUL - Well Done -')
            p['QC'] = 1
            p.set_source('QC', __NAME__ + '/main()')
        else:
            for farg in fail_msg:
                wmsg = 'QUALITY CONTROL FAILED: {0}'
                WLOG('warning', p['LOG_OPT'], wmsg.format(farg))
            p['QC'] = 0
            p.set_source('QC', __NAME__ + '/main()')

        # ------------------------------------------------------------------
        # Add transmission map to telluDB
        # ------------------------------------------------------------------
        if p['QC']:
            # copy tellu file to the telluDB folder
            spirouDB.PutTelluFile(p, outfile)
            # TODO: work out these values (placeholders currently)
            airmass = loc['DATAHDR'][p['KW_AIRMASS'][0]]
            watercol = -9999.0
            # TODO: Can't figured out where to get watercol from
            # TODO: Airmass from header? Which key?
            name = loc['DATAHDR'][p['KW_OBJNAME'][0]]
            # update the master tellu DB file with transmission map
            targs = [p, outfilename, name, airmass, watercol]
            spirouDB.UpdateDatabaseTellMap(*targs)

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
        abso = np.zeros([nfiles, np.product(loc['DATA'].shape)])
        # loop around outputfiles and add them to abso
        for it, filename in enumerate(p['OUTPUTFILES']):
            # push data into array
            data_it, _, _, _, _ = spirouImage.ReadImage(p, filename)
            abso[it, :] = data_it.reshape(np.product(loc['DATA'].shape))
        # set values less than low threshold to low threshold
        # set values higher than high threshold to 1
        low, high = p['TELLU_ABSO_LOW_THRES'], p['TELLU_ABSO_HIGH_THRES']
        abso[abso < low] = low
        abso[abso > high] = 1.0
        # set values less than TELLU_CUT_BLAZE_NORM threshold to NaN
        abso[loc['NBLAZE'] < p['TELLU_CUT_BLAZE_NORM']] = np.nan
        # reshape data (back to E2DS)
        abso_e2ds = abso.reshape(nfiles, loc['YDIM'], loc['XDIM'])
        # write thie map to file
        hdict = spirouImage.CopyOriginalKeys(loc['DATAHDR'], loc['DATACDR'])
        abso_map_file = spirouConfig.Constants.TELLU_ABSO_MAP_FILE(p)
        spirouImage.WriteImage(abso_map_file, abso_e2ds, hdict)

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
        abso_map_n = abso_med_out.reshape(loc['DATA'].shape)

        # save the median absorption map to file
        abso_med_file = spirouConfig.Constants.TELLU_ABSO_MEDIAN_FILE(p)
        spirouImage.WriteImage(abso_med_file, abso_med_out, hdict)

        # save the normalized absorption map to file
        abso_map_n_file = spirouConfig.Constants.TELLU_ABSO_NORM_MAP_FILE(p)
        spirouImage.WriteImage(abso_map_n_file, abso_map_n, hdict)

        # ------------------------------------------------------------------
        # calculate dv statistic
        # ------------------------------------------------------------------
        # get the order for dv calculation
        dvselect = p['TELLU_ABSO_DV_ORDER']
        size = p['TELLU_ABSO_DV_SIZE']
        threshold2 = p['TELLU_ABSO_DV_GOOD_THRES']
        fitdeg = p['TELLU_ABSO_FIT_DEG']
        ydim, xdim = loc['DATA'].shape
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
    spirouStartup.Exit(ll, has_plots=False)

# =============================================================================
# End of code
# =============================================================================
