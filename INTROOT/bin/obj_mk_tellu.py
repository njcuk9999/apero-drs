#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
obj_mk_tellu [night_directory] [files]

Creates a flattened transmission spectrum from a hot star observation.
The continuum is set to 1 and regions with too many tellurics for continuum
estimates are set to NaN and should not used for RV. Overall, the domain with
a valid transmission mask corresponds to the YJHK photometric bandpasses.
The transmission maps have the same shape as e2ds files. Ultimately, we will
want to retrieve a transmission profile for the entire nIR domain for generic
science that may be done in the deep water bands. The useful domain for RV
measurements will (most likely) be limited to the domain without very strong
absorption, so the output transmission files meet our pRV requirements in
terms of wavelength coverage. Extension of the transmission maps to the
domain between photometric bandpasses is seen as a low priority item.

Usage:
  obj_mk_tellu night_name telluric_file_name.fits


Outputs:
  telluDB: TELL_MAP file - telluric transmission map for input file
        file also saved in the reduced folder
        input file + '_trans.fits'

  telluDB: TELL_CONV file - convolved molecular file (for specific
                            wavelength solution) if it doesn't already exist
        file also saved in the reduced folder
        wavelength solution + '_tapas_convolved.npy'

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
from SpirouDRS.spirouCore.spirouMath import nanpolyfit


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
    wout = spirouImage.GetWaveSolution(p, image=loc['DATA'], hdr=loc['DATAHDR'],
                                       return_wavemap=True,
                                       return_filename=True)
    _, loc['WAVE'], loc['WAVEFILE'], _ = wout
    loc.set_sources(['WAVE', 'WAVEFILE'], main_name)
    # get the wave keys
    loc = spirouImage.GetWaveKeys(p, loc, loc['DATAHDR'])

    # ------------------------------------------------------------------
    # Get and Normalise the blaze
    # ------------------------------------------------------------------
    p, loc = spirouTelluric.GetNormalizedBlaze(p, loc, loc['DATAHDR'])

    # ------------------------------------------------------------------
    # Construct convolution kernels
    # ------------------------------------------------------------------
    loc = spirouTelluric.ConstructConvKernel1(p, loc)
    loc = spirouTelluric.ConstructConvKernel2(p, loc, vsini=p['TELLU_VSINI'])

    # ------------------------------------------------------------------
    # Get molecular telluric lines
    # ------------------------------------------------------------------
    loc = spirouTelluric.GetMolecularTellLines(p, loc)
    # if TAPAS FNAME is not None we generated a new file so should add to tellDB
    if loc['TAPAS_FNAME'] is not None:
        # add to the telluric database
        spirouDB.UpdateDatabaseTellConv(p, loc['TAPAS_FNAME'], loc['DATAHDR'])
        # put file in telluDB
        spirouDB.PutTelluFile(p, loc['TAPAS_ABSNAME'])

    # ------------------------------------------------------------------
    # Get master wave solution map
    # ------------------------------------------------------------------
    # get master wave map
    masterwavefile = spirouDB.GetDatabaseMasterWave(p)
    # log process
    wmsg1 = 'Shifting transmission map on to master wavelength grid'
    wmsg2 = '\tFile = {0}'.format(os.path.basename(masterwavefile))
    WLOG(p, '', [wmsg1, wmsg2])
    # Force A and B to AB solution
    if p['FIBER'] in ['A', 'B']:
        wave_fiber = 'AB'
    else:
        wave_fiber = p['FIBER']
    # read master wave map
    mout = spirouImage.GetWaveSolution(p, filename=masterwavefile,
                                       return_wavemap=True, quiet=True,
                                       return_header=True, fiber=wave_fiber)
    masterwavep, masterwave, masterwaveheader, mwsource = mout
    # get wave acqtimes
    master_acqtimes = spirouDB.GetTimes(p, masterwaveheader)

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

        # ------------------------------------------------------------------
        # Get the wave solution
        # ------------------------------------------------------------------
        wout = spirouImage.GetWaveSolution(p, image=sp, hdr=shdr,
                                           return_wavemap=True,
                                           return_filename=True)
        _, loc['WAVE_IT'], loc['WAVEFILE_IT'], _ = wout
        loc.set_sources(['WAVE_IT', 'WAVEFILE_IT'], main_name)

        # ------------------------------------------------------------------
        # Shift data to master wave file
        # ------------------------------------------------------------------
        # shift map
        wargs = [p, sp, loc['WAVE_IT'], masterwave]
        sp = spirouTelluric.Wave2Wave(*wargs)
        loc['SP'] = np.array(sp)
        loc.set_source('SP', main_name)

        # ------------------------------------------------------------------
        # get output transmission filename
        outfile, tag1 = spirouConfig.Constants.TELLU_TRANS_MAP_FILE(p, filename)
        outfilename = os.path.basename(outfile)
        loc['OUTPUTFILES'].append(outfile)

        # if we already have the file skip it
        if outfile in tellu_db_files:
            wmsg = 'File {0} exists in telluDB, skipping'
            WLOG(p, '', wmsg.format(outfilename))
            continue
        else:
            # log processing file
            wmsg = 'Processing file {0}'
            WLOG(p, '', wmsg.format(outfilename))

        # Get object name and airmass
        loc['OBJNAME'] = spirouImage.GetObjName(p, shdr)
        loc['AIRMASS'] = spirouImage.GetAirmass(p, shdr)
        # set source
        source = main_name + '+ spirouImage.ReadParams()'
        loc.set_sources(['OBJNAME', 'AIRMASS'], source)

        # ------------------------------------------------------------------
        # Check that basefile is not in blacklist
        # ------------------------------------------------------------------
        blacklist_check = spirouTelluric.CheckBlackList(loc['OBJNAME'])
        if blacklist_check:
            # log black list file found
            wmsg = 'File {0} is blacklisted (OBJNAME={1}). Skipping'
            wargs = [basefilename, loc['OBJNAME']]
            WLOG(p, 'warning', wmsg.format(*wargs))
            # skip this file
            continue

        # ------------------------------------------------------------------
        # loop around the orders
        # ------------------------------------------------------------------
        # define storage for the transmission map
        transmission_map = np.zeros_like(loc['DATA'])
        # define storage for measured rms within expected clean domains
        exp_clean_rms = np.zeros(loc['DATA'].shape[0])
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
            ww = None
            for it in range(p['N_ITER_SED_HOTSTAR']):
                # copy the spectrum
                sp2 = np.array(sp[order_num, :])
                # flag Nans
                nanmask = ~np.isfinite(sp2)
                # set all NaNs to zero so that it does not propagate when
                #     we convlve by KER2 - must set sp2[bad] to zero as
                #     NaN * 0.0 = NaN and we want 0.0!
                sp2[nanmask] = 0.0
                # trace the invalid points
                fmask[nanmask] = 0.0
                # multiple by the float mask
                sp2 *= fmask
                # convolve with the second kernel
                sp2b = np.convolve(sp2 / sed, loc['KER2'], mode='same')
                # convolve with mask to get weights
                ww = np.convolve(fmask, loc['KER2'], mode='same')
                # normalise the spectrum by the weights
                with warnings.catch_warnings(record=True) as w:
                    sp2bw = sp2b / ww
                # set zero pixels to 1
                sp2bw[sp2b == 0] = 1
                # recalculate the mask using the deviation from original
                with warnings.catch_warnings(record=True) as _:
                    dev = (sp2bw - sp[order_num, :] / sed)
                    dev /= np.nanmedian(np.abs(dev))
                    mask = mask1 * (np.abs(dev) < p['TELLU_SIGMA_DEV'])
                # update the SED with the corrected spectrum
                sed *= sp2bw
            # identify bad pixels
            with warnings.catch_warnings(record=True) as _:
                bad = (sp[order_num, :] / sed[:] > 1.2)
                sed[bad] = np.nan

            # debug plot
            if p['DRS_PLOT'] and (p['DRS_DEBUG'] > 1) and FORCE_PLOT_ON:
                # start non-interactive plot
                sPlt.plt.ioff()
                # plot the transmission map plot
                pargs = [order_num, mask1, sed, trans, sp, ww, outfilename]
                sPlt.tellu_trans_map_plot(p, loc, *pargs)
                # show and close
                sPlt.plt.show()
                sPlt.plt.close()

            # set all values below a threshold to NaN
            sed[ww < p['TELLU_NAN_THRESHOLD']] = np.nan
            # save the spectrum (normalised by the SED) to the tranmission map
            transmission_map[order_num, :] = sp[order_num, :] / sed

            # get expected clean rms
            fmaskb = np.array(fmask).astype(bool)
            with warnings.catch_warnings(record=True):
                zerotrans = np.abs(transmission_map[order_num, fmaskb]-1)
                ec_rms = np.nanmedian(zerotrans)
                exp_clean_rms[order_num] = ec_rms

            # log the rms
            wmsg = 'Order {0}: Fractional RMS in telluric free domain = {1:.3f}'
            wargs = [order_num, ec_rms]
            WLOG(p, '', wmsg.format(*wargs))

        # ---------------------------------------------------------------------
        # Quality control
        # ---------------------------------------------------------------------
        # set passed variable and fail message list
        passed, fail_msg = True, []
        qc_values, qc_names, qc_logic, qc_pass = [], [], [], []
        # ----------------------------------------------------------------------
        # get SNR for each order from header
        nbo = loc['DATA'].shape[0]
        snr_order = p['QC_MK_TELLU_SNR_ORDER']
        snr = spirouImage.Read1Dkey(p, shdr, p['kw_E2DS_SNR'][0], nbo)
        # check that SNR is high enough
        if snr[snr_order] < p['QC_MK_TELLU_SNR_MIN']:
            fmsg = 'low SNR in order {0}: ({1:.2f} < {2:.2f})'
            fargs = [snr_order, snr[snr_order], p['QC_MK_TELLU_SNR_MIN']]
            fail_msg.append(fmsg.format(*fargs))
            passed = False
            # add to qc header lists
            qc_values.append(snr[snr_order])
            qc_name_str = 'SNR[{0}]'.format(snr_order)
            qc_names.append(qc_name_str)
            qc_logic.append('{0} < {1:.2f}'.format(qc_name_str,
                                                   p['QC_MK_TELLU_SNR_ORDER']))
            qc_pass.append(0)
        else:
            qc_pass.append(1)
        # ----------------------------------------------------------------------
        # check that the RMS is not too low
        if exp_clean_rms[snr_order] > p['QC_TELLU_CLEAN_RMS_MAX']:
            fmsg = ('Expected clean RMS is too high in order {0} '
                    '({1:.3f} > {2:.3f})')
            fargs = [snr_order, exp_clean_rms[snr_order],
                     p['QC_TELLU_CLEAN_RMS_MAX']]
            fail_msg.append(fmsg.format(*fargs))
            passed = False
            # add to qc header lists
            qc_values.append(exp_clean_rms[snr_order])
            qc_name_str = 'exp_clean_rms[{0}]'.format(snr_order)
            qc_names.append(qc_name_str)
            qc_logic.append('{0} > {1:.2f}'.format(qc_name_str,
                                                   p['QC_TELLU_CLEAN_RMS_MAX']))
            qc_pass.append(0)
        else:
            qc_pass.append(1)
        # ----------------------------------------------------------------------
        # finally log the failed messages and set QC = 1 if we pass the
        # quality control QC = 0 if we fail quality control
        if passed:
            WLOG(p, 'info',
                 'QUALITY CONTROL SUCCESSFUL - Well Done -')
            p['QC'] = 1
            p.set_source('QC', __NAME__ + '/main()')
        else:
            for farg in fail_msg:
                wmsg = 'QUALITY CONTROL FAILED: {0}'
                WLOG(p, 'warning', wmsg.format(farg))
            p['QC'] = 0
            p.set_source('QC', __NAME__ + '/main()')
        # store in qc_params
        qc_params = [qc_names, qc_values, qc_logic, qc_pass]

        # ------------------------------------------------------------------
        # Save transmission map to file
        # ------------------------------------------------------------------
        # get raw file name
        raw_in_file = os.path.basename(p['FITSFILENAME'])
        # copy original keys
        hdict = spirouImage.CopyOriginalKeys(loc['DATAHDR'], loc['DATACDR'])
        # add version number
        hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_PID'], value=p['PID'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag1)
        # set the input files
        hdict = spirouImage.AddKey(p, hdict, p['KW_CDBBLAZE'],
                                   value=p['BLAZFILE'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_CDBWAVE'],
                                   value=os.path.basename(masterwavefile))
        hdict = spirouImage.AddKey(p, hdict, p['KW_WAVESOURCE'],
                                   value=mwsource)
        hdict = spirouImage.AddKey1DList(p, hdict, p['KW_INFILE1'],
                                         dim1name='file',
                                         values=p['ARG_FILE_NAMES'])
        # add qc parameters
        hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_QC'], value=p['QC'])
        hdict = spirouImage.AddQCKeys(p, hdict, qc_params)
        # add wave solution date
        hdict = spirouImage.AddKey(p, hdict, p['KW_WAVE_TIME1'],
                                   value=master_acqtimes[0])
        hdict = spirouImage.AddKey(p, hdict, p['KW_WAVE_TIME2'],
                                   value=master_acqtimes[1])
        # add wave solution number of orders
        hdict = spirouImage.AddKey(p, hdict, p['KW_WAVE_ORD_N'],
                                   value=masterwavep.shape[0])
        # add wave solution degree of fit
        hdict = spirouImage.AddKey(p, hdict, p['KW_WAVE_LL_DEG'],
                                   value=masterwavep.shape[1] - 1)
        # add wave solution coefficients
        hdict = spirouImage.AddKey2DList(p, hdict, p['KW_WAVE_PARAM'],
                                         values=masterwavep)
        # write to file
        p = spirouImage.WriteImage(p, outfile, transmission_map, hdict)

        # ------------------------------------------------------------------
        # Generate the absorption map
        # ------------------------------------------------------------------
        # set up storage for the absorption
        abso = np.array(transmission_map)
        # set values less than low threshold to low threshold
        # set values higher than high threshold to 1
        low, high = p['TELLU_ABSO_LOW_THRES'], p['TELLU_ABSO_HIGH_THRES']
        with warnings.catch_warnings(record=True) as w:
            abso[abso < low] = low
            abso[abso > high] = 1.0
        # write to loc
        loc['RECON_ABSO'] = abso.reshape(np.product(loc['DATA'].shape))
        loc.set_source('RECON_ABSO', main_name)

        # ------------------------------------------------------------------
        # Get molecular absorption
        # ------------------------------------------------------------------
        loc = spirouTelluric.CalcMolecularAbsorption(p, loc)
        # add molecular absorption to file
        for it, molecule in enumerate(p['TELLU_ABSORBERS'][1:]):
            # get molecule keyword store and key
            molkey = '{0}_{1}'.format(p['KW_TELLU_ABSO'][0], molecule.upper())
            # add water col
            if molecule == 'h2o':
                loc['WATERCOL'] = loc[molkey]
                # set source
                loc.set_source('WATERCOL', main_name)

        # ------------------------------------------------------------------
        # Add transmission map to telluDB
        # ------------------------------------------------------------------
        if p['QC']:
            # copy tellu file to the telluDB folder
            spirouDB.PutTelluFile(p, outfile)
            # update the master tellu DB file with transmission map
            targs = [p, outfilename, loc['OBJNAME'], loc['AIRMASS'],
                     loc['WATERCOL']]
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
        # get file name
        abso_map_file, tag2 = spirouConfig.Constants.TELLU_ABSO_MAP_FILE(p)
        # get raw file name
        raw_in_file = os.path.basename(p['FITSFILENAME'])
        # write the map to file
        hdict = spirouImage.CopyOriginalKeys(loc['DATAHDR'], loc['DATACDR'])
        # add version number
        hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag2)
        # set the input files
        hdict = spirouImage.AddKey(p, hdict, p['KW_CDBBLAZE'],
                                   value=p['BLAZFILE'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_CDBWAVE'],
                                   value=loc['WAVEFILE'])

        # write to file
        p = spirouImage.WriteImage(p, abso_map_file, abso_e2ds, hdict)

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
                part1 = np.nansum(rowvalue[goodpix] * abso_med[goodpix])
                part2 = np.nansum(abso_med[goodpix] ** 2)
                ratio = part1 / part2
                # store normalised absol back on to log_abso
                log_abso[jt, :] = log_abso[jt, :] / ratio

        # unlog log_abso
        abso_out = np.exp(log_abso)

        # calculate the median of the log_abso
        abso_med_out = np.exp(np.nanmedian(log_abso, axis=0))
        # reshape the median
        abso_map_n = abso_med_out.reshape(loc['DATA'].shape)

        # save the median absorption map to file
        abso_med_file, tag3 = spirouConfig.Constants.TELLU_ABSO_MEDIAN_FILE(p)
        hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag3)
        p = spirouImage.WriteImage(p, abso_med_file, abso_med_out, hdict)

        # save the normalized absorption map to file
        abso_map_file, tag4 = spirouConfig.Constants.TELLU_ABSO_NORM_MAP_FILE(p)
        hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag4)
        p = spirouImage.WriteImage(p, abso_map_file, abso_map_n, hdict)

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
        dvpixels = np.arange(-np.floor(size / 2), np.ceil(size / 2), 1)
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
                part1 = np.nansum(rowvalue[goodpix] * abso_med2[goodpix])
                part2 = np.nansum(abso_med2[goodpix] ** 2)
                cc[jt] = part1 / part2
            # fit the ratio across the points
            cfit = nanpolyfit(dvpixels, cc, fitdeg)
            # work out the dv pix
            dvpix = -0.5 * (cfit[1] / cfit[0])
            # log stats
            wmsg = 'File: "{0}", dv={1}'
            WLOG(p, '', wmsg.format(filename, dvpix))

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    p = spirouStartup.End(p)
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
