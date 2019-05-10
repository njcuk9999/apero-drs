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
    loc['DATA'], loc['DATAHDR'], loc['YDIM'], loc['XDIM'] = rd
    loc.set_sources(['DATA', 'DATAHDR', 'XDIM', 'YDIM'], main_name)

    # ------------------------------------------------------------------
    # Get the wave solution
    # ------------------------------------------------------------------
    masterwavefile = spirouDB.GetDatabaseMasterWave(p)
    # Force A and B to AB solution
    if p['FIBER'] in ['A', 'B']:
        wave_fiber = 'AB'
    else:
        wave_fiber = p['FIBER']
    # read master wave map
    wout = spirouImage.GetWaveSolution(p, filename=masterwavefile,
                                       return_wavemap=True, quiet=True,
                                       return_header=True, fiber=wave_fiber)
    _, loc['WAVE'], loc['WAVEFILE'], _ = wout
    loc.set_sources(['WAVE', 'WAVEFILE'], main_name)
    # get the wave keys
    loc = spirouImage.GetWaveKeys(p, loc, loc['DATAHDR'])

    # ------------------------------------------------------------------
    # Construct convolution kernels (used in GetMolecularTellLines)
    # ------------------------------------------------------------------
    loc = spirouTelluric.ConstructConvKernel1(p, loc)

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

    # ----------------------------------------------------------------------
    # load the expected atmospheric transmission
    # ----------------------------------------------------------------------
    # read filename from telluDB
    tapas_file_names = spirouDB.GetDatabaseTellConv(p)
    tapas_file_name = tapas_file_names[-1]
    # load atmospheric transmission
    sp_tapas = np.load(tapas_file_name)
    loc['TAPAS_ALL_SPECIES'] = sp_tapas
    # extract the water and other line-of-sight optical depths
    loc['TAPAS_WATER'] = sp_tapas[1, :]
    loc['TAPAS_OTHERS'] = np.prod(sp_tapas[2:, :], axis=0)
    loc.set_sources(['TAPAS_ALL_SPECIES', 'TAPAS_WATER', 'TAPAS_OTHERS'],
                    main_name)

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
    # tellu_db_data = spirouDB.GetDatabaseTellMap(p, required=False)
    # tellu_db_files = tellu_db_data[0]
    # storage for valid output files
    loc['OUTPUTFILES'] = []
    # loop around the files
    for basefilename in p['ARG_FILE_NAMES']:

        # ------------------------------------------------------------------
        # Get absolute path of filename
        # ------------------------------------------------------------------
        filename = os.path.join(p['ARG_FILE_DIR'], basefilename)

        # ------------------------------------------------------------------
        # Read obj telluric file and correct blaze (per order)
        # ------------------------------------------------------------------
        # get image
        sp, shdr, _, _ = spirouImage.ReadImage(p, filename)

        # get blaze
        p, blaze = spirouImage.ReadBlazeFile(p, shdr)

        # get the blaze percentile
        blaze_p = p['MKTELLU_BLAZE_PERCENTILE']
        # loop through blaze orders, normalize blaze by its peak amplitude
        for order_num in range(sp.shape[0]):
            # normalize the spectrum
            spo, bzo = sp[order_num], blaze[order_num]

            sp[order_num] = spo / np.nanpercentile(spo, blaze_p)
            # normalize the blaze
            blaze[order_num] = bzo / np.nanpercentile(bzo, blaze_p)

        # find where the blaze is bad
        with warnings.catch_warnings(record=True) as _:
            badblaze = blaze < p['MKTELLU_CUT_BLAZE_NORM']
        # set bad blaze to NaN
        blaze[badblaze] = np.nan

        # set to NaN values where spectrum is zero
        zeromask = sp == 0
        sp[zeromask] = np.nan
        # divide spectrum by blaze
        with warnings.catch_warnings(record=True) as _:
            sp = sp / blaze
        # add sp to loc
        loc['SP'] = sp
        loc.set_source('SP', main_name)

        # ----------------------------------------------------------------------
        # Get object name, airmass and berv
        # ----------------------------------------------------------------------
        # Get object name
        loc['OBJNAME'] = spirouImage.GetObjName(p, shdr)
        # Get the airmass
        loc['AIRMASS'] = spirouImage.GetAirmass(p, shdr)
        # Get the Barycentric correction from header
        loc['BERV'], _, _ = spirouTelluric.GetBERV(p, shdr)
        # set sources
        source = main_name + '+ spirouImage.ReadParams()'
        loc.set_sources(['OBJNAME', 'AIRMASS', 'BERV'], source)

        # ------------------------------------------------------------------
        # get output transmission filename
        outfile, tag1 = spirouConfig.Constants.TELLU_TRANS_MAP_FILE(p, filename)
        outfilename = os.path.basename(outfile)
        loc['OUTPUTFILES'].append(outfile)

        # ----------------------------------------------------------------------
        # Load template (if available)
        # ----------------------------------------------------------------------
        # read filename from telluDB
        template_file = spirouDB.GetDatabaseObjTemp(p, loc['OBJNAME'],
                                                    required=False)
        # if we don't have a template flag it
        if template_file is None:
            loc['FLAG_TEMPLATE'] = False
            loc['TEMPLATE'] = None
            # construct progres string
            pstring = 'No template found.'
        else:
            loc['FLAG_TEMPLATE'] = True
            # load template
            template, _, _, _ = spirouImage.ReadImage(p, template_file)
            # add to loc
            loc['TEMPLATE'] = template
            # construct progres string
            template_bfile = os.path.basename(template_file)
            pstring = 'Using template {0}'.format(template_bfile)
        # set the source for flag and template
        loc.set_sources(['FLAG_TEMPLATE', 'TEMPLATE'], main_name)

        # ------------------------------------------------------------------
        # log processing file
        wmsg = 'Processing file {0}. {1}'
        WLOG(p, '', [wmsg.format(outfilename, pstring)])

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
        # deal with applying template to spectrum
        # ------------------------------------------------------------------
        # Requires from loc:
        #           TEMPLATE   (None or template loaded from file)
        #           FLAG_TEMPLATE
        #           WAVE
        #           SP
        #           BERV
        #
        # Returns:
        #           SP (modified if template was used)
        #           TEMPLATE
        #           WCONV
        loc = spirouTelluric.ApplyTemplate(p, loc)

        # ------------------------------------------------------------------
        # calcullate telluric absorption (with a sigma clip loop)
        # ------------------------------------------------------------------
        # Requires from loc:
        #           AIRMASS
        #           WAVE
        #           SP
        #           WCONV
        # Returns:
        #           PASSED   [Bool] True or False
        #           SP_OUT
        #           SED_OUT
        #           RECOV_AIRMASS
        #           RECOV_WATER
        loc = spirouTelluric.CalcTelluAbsorption(p, loc)
        # calculate tranmission map from sp and sed
        transmission_map = loc['SP_OUT'] / loc['SED_OUT']

        # ----------------------------------------------------------------------
        # Quality control
        # ----------------------------------------------------------------------
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
            qc_pass.append(0)
        else:
            qc_pass.append(1)
        # add to qc header lists
        qc_values.append(snr[snr_order])
        qc_name_str = 'SNR[{0}]'.format(snr_order)
        qc_names.append(qc_name_str)
        qc_logic.append('{0} < {1:.2f}'.format(qc_name_str,
                                               p['QC_MK_TELLU_SNR_ORDER']))
        # ----------------------------------------------------------------------
        # check that the file passed the CalcTelluAbsorption sigma clip loop
        if not loc['PASSED']:
            fmsg = 'File {0} did not converge on a solution in function: {1}'
            fargs = [basefilename, 'spirouTelluric.CalcTelluAbsorption()']
            fail_msg.append(fmsg.format(*fargs))
            passed = False
            qc_pass.append(0)
        else:
            qc_pass.append(1)
        # add to qc header lists
        qc_values.append(basefilename)
        qc_names.append('FILE')
        qc_logic.append('FILE did not converge')
        # ----------------------------------------------------------------------
        # check that the airmass is not too different from input airmass
        airmass_diff = np.abs(loc['RECOV_AIRMASS'] - loc['AIRMASS'])
        fargs = [loc['RECOV_AIRMASS'], loc['AIRMASS'],
                 p['QC_MKTELLU_AIRMASS_DIFF']]
        if airmass_diff > p['QC_MKTELLU_AIRMASS_DIFF']:
            fmsg = ('Recovered airmass to de-similar than input airmass.'
                    'Recovered: {0:.3f}. Input: {1:.3f}. QC limit = {2}')
            fail_msg.append(fmsg.format(*fargs))
            passed = False
            qc_pass.append(0)
        else:
            qc_pass.append(1)
        # add to qc header lists
        qc_values.append(airmass_diff)
        qc_names.append('airmass_diff')
        qc_logic.append('airmass_diff > {0:.2f}'
                        ''.format(p['QC_MKTELLU_AIRMASS_DIFF']))
        # ----------------------------------------------------------------------
        # check that the water vapor is within limits
        water_cond1 = loc['RECOV_WATER'] < p['MKTELLU_TRANS_MIN_WATERCOL']
        water_cond2 = loc['RECOV_WATER'] > p['MKTELLU_TRANS_MAX_WATERCOL']
        fargs = [p['MKTELLU_TRANS_MIN_WATERCOL'],
                 p['MKTELLU_TRANS_MAX_WATERCOL']]
        if water_cond1 or water_cond2:
            fmsg = ('Recovered water vapor optical depth not between {0:.3f} '
                    'and {1:.3f}')
            fail_msg.append(fmsg.format(*fargs))
            passed = False
            qc_pass.append(0)
        else:
            qc_pass.append(1)
        # add to qc header lists
        qc_values.append(loc['RECOV_WATER'])
        qc_names.append('RECOV_WATER')
        qc_logic.append('RECOV_WATER not between {0:.3f} and {1:.3f}'
                        ''.format(*fargs))
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
            continue
        # store in qc_params
        qc_params = [qc_names, qc_values, qc_logic, qc_pass]

        # ------------------------------------------------------------------
        # Save transmission map to file
        # ------------------------------------------------------------------
        # get raw file name
        raw_in_file = os.path.basename(p['FITSFILENAME'])
        # copy original keys
        hdict = spirouImage.CopyOriginalKeys(loc['DATAHDR'])
        # add version number
        hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_PID'], value=p['PID'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag1)
        # set the input files
        hdict = spirouImage.AddKey(p, hdict, p['KW_CDBBLAZE'],
                                   value=p['BLAZFILE'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_CDBWAVE'],
                                   value=os.path.basename(masterwavefile))
        hdict = spirouImage.AddKey(p, hdict, p['KW_WAVESOURCE'], value=mwsource)
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
        # add telluric keys
        hdict = spirouImage.AddKey(p, hdict, p['KW_TELLU_AIRMASS'],
                                   value=loc['RECOV_AIRMASS'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_TELLU_WATER'],
                                   value=loc['RECOV_WATER'])
        # write to file
        p = spirouImage.WriteImage(p, outfile, transmission_map, hdict)

        # ------------------------------------------------------------------
        # Add transmission map to telluDB
        # ------------------------------------------------------------------
        if p['QC']:
            # copy tellu file to the telluDB folder
            spirouDB.PutTelluFile(p, outfile)
            # update the master tellu DB file with transmission map
            targs = [p, outfilename, loc['OBJNAME'], loc['RECOV_AIRMASS'],
                     loc['RECOV_WATER']]
            spirouDB.UpdateDatabaseTellMap(*targs)

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
    spirouStartup.Exit(ll, has_plots=True)

# =============================================================================
# End of code
# =============================================================================
