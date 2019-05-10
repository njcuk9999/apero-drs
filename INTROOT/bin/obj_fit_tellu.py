#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

obj_fit_tellu [night_directory] [files]

Using all transmission files, we fit the absorption of a given science
observation. To reduce the number of degrees of freedom, we perform a PCA and
keep only the N (currently we suggest N=5)  principal components in absorbance.
As telluric absorption may shift in velocity from one observation to another,
we have the option of including the derivative of the absorbance in the
reconstruction. The method also measures a proxy of optical depth per molecule
(H2O, O2, O3, CO2, CH4, N2O) that can be used for data quality assessment.

Usage:
  obj_fit_tellu night_name object.fits

Outputs:
  telluDB: TELL_OBJ file - The object corrected for tellurics
        file also saved in the reduced folder
        input file + '_tellu_corrected.fits'

    recon_abso file - The reconstructed absorption file saved in the reduced
                    folder
        input file + '_tellu_recon.fits'

Created on 2018-07-13 05:18
@author: ncook
Version 0.0.1
"""
from __future__ import division
import numpy as np
import os
from collections import OrderedDict
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
__NAME__ = 'obj_fit_tellu.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# get constants
CONSTANTS = spirouConfig.Constants
# Custom parameter dictionary
ParamDict = spirouConfig.ParamDict
# Get sigma FWHM
SIG_FWHM = spirouCore.spirouMath.fwhm
# Get plotting functions
sPlt = spirouCore.sPlt


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

    # ----------------------------------------------------------------------
    # Load first file
    # ----------------------------------------------------------------------
    loc = ParamDict()
    rd = spirouImage.ReadImage(p, p['FITSFILENAME'])
    loc['DATA'], loc['DATAHDR'], loc['XDIM'], loc['YDIM'] = rd
    loc.set_sources(['DATA', 'DATAHDR', 'XDIM', 'YDIM'], main_name)

    # ----------------------------------------------------------------------
    # Get object name, airmass and berv
    # ----------------------------------------------------------------------
    # Get object name
    loc['OBJNAME'] = spirouImage.GetObjName(p, loc['DATAHDR'])
    # Get the airmass
    loc['AIRMASS'] = spirouImage.GetAirmass(p, loc['DATAHDR'])
    # Get the Barycentric correction from header
    loc['BERV'], _, _ = spirouTelluric.GetBERV(p, loc['DATAHDR'])
    # set sources
    source = main_name + '+ spirouImage.ReadParams()'
    loc.set_sources(['OBJNAME', 'AIRMASS', 'BERV'], source)
    # ----------------------------------------------------------------------
    # Read wavelength solution
    # ----------------------------------------------------------------------
    # Force A and B to AB solution
    if p['FIBER'] in ['A', 'B']:
        wave_fiber = 'AB'
    else:
        wave_fiber = p['FIBER']
    # used for plotting only
    wout = spirouImage.GetWaveSolution(p, image=loc['DATA'], hdr=loc['DATAHDR'],
                                       return_wavemap=True, fiber=wave_fiber)
    _, loc['WAVE'], _ = wout
    loc.set_source('WAVE', main_name)

    # ----------------------------------------------------------------------
    # Get and Normalise the blaze
    # ----------------------------------------------------------------------
    p, loc = spirouTelluric.GetNormalizedBlaze(p, loc, loc['DATAHDR'])

    # ----------------------------------------------------------------------
    # Load transmission files
    # ----------------------------------------------------------------------
    transdata = spirouDB.GetDatabaseTellMap(p)
    trans_files = transdata[0]
    # make sure we have unique filenames for trans_files
    trans_files = np.unique(trans_files)

    # ----------------------------------------------------------------------
    # Start plotting
    # ----------------------------------------------------------------------
    if p['DRS_PLOT'] > 0:
        # start interactive plot
        sPlt.start_interactive_session(p)

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
    else:
        loc['FLAG_TEMPLATE'] = True
        # load template
        template, _, _, _ = spirouImage.ReadImage(p, template_file)
        # add to loc
        loc['TEMPLATE'] = template
    # set the source for flag and template
    loc.set_sources(['FLAG_TEMPLATE', 'TEMPLATE'], main_name)

    # ----------------------------------------------------------------------
    # load the expected atmospheric transmission
    # ----------------------------------------------------------------------
    # read filename from telluDB
    tapas_file_names = spirouDB.GetDatabaseTellConv(p)
    tapas_file_name = tapas_file_names[-1]
    # load atmospheric transmission
    loc['TAPAS_ALL_SPECIES'] = np.load(tapas_file_name)
    loc.set_source('TAPAS_ALL_SPECIES', main_name)

    # ----------------------------------------------------------------------
    # Generate the absorption map
    # ----------------------------------------------------------------------
    # get number of files
    nfiles = len(trans_files)
    npc = p['TELLU_NUMBER_OF_PRINCIPLE_COMP']
    # check that we have enough files (greater than number of principle
    #    components)
    if nfiles <= npc:
        emsg1 = 'Not enough "TELL_MAP" files in telluDB to run PCA analysis'
        emsg2 = '\tNumber of files = {0}, number of PCA components = {1}'
        emsg3 = '\tNumber of files > number of PCA components'
        emsg4 = '\tAdd more files or reduce number of PCA components'
        WLOG(p, 'error', [emsg1, emsg2.format(nfiles, npc),
                                     emsg3, emsg4])

    # check whether we can used pre-saved abso
    filetime = spirouImage.GetMostRecent(trans_files)
    tout = spirouConfig.Constants.TELLU_ABSO_SAVE(p, filetime)
    abso_save_file, absoprefix = tout
    use_saved = os.path.exists(abso_save_file)
    # noinspection PyBroadException
    try:
        # try loading from file
        abso = np.load(abso_save_file)
        # log progress
        wmsg = 'Loaded abso from file {0}'.format(abso_save_file)
        WLOG(p, '', wmsg)
    except:
        # set up storage for the absorption
        abso = np.zeros([nfiles, np.product(loc['DATA'].shape)])
        # loop around outputfiles and add them to abso
        for it, filename in enumerate(trans_files):
            # load data
            data_it, _, _, _ = spirouImage.ReadImage(p, filename=filename)
            # push data into array
            abso[it, :] = data_it.reshape(np.product(loc['DATA'].shape))
        # log progres
        wmsg = 'Saving abso to file {0}'.format(abso_save_file)
        WLOG(p, '', wmsg)
        # remove all abso save files (only need most recent one)
        afolder = os.path.dirname(abso_save_file)
        afilelist = os.listdir(afolder)
        for afile in afilelist:
            if afile.startswith(absoprefix):
                os.remove(os.path.join(afolder, afile))
        # save to file for later use
        np.save(abso_save_file, abso)

    # log the absorption cube
    with warnings.catch_warnings(record=True) as w:
        log_abso = np.log(abso)

    # ----------------------------------------------------------------------
    # Locate valid pixels for PCA
    # ----------------------------------------------------------------------
    # determining the pixels relevant for PCA construction
    keep = np.isfinite(np.sum(abso, axis=0))
    # log fraction of valid (non NaN) pixels
    fraction = np.nansum(keep) / len(keep)
    wmsg = 'Fraction of valid pixels (not NaNs) for PCA construction = {0:.3f}'
    WLOG(p, '', wmsg.format(fraction))
    # log fraction of valid pixels > 1 - (1/e)
    with warnings.catch_warnings(record=True) as w:
        keep &= np.min(log_abso, axis=0) > -1
    fraction = np.nansum(keep) / len(keep)
    wmsg = 'Fraction of valid pixels with transmission > 1 - (1/e) = {0:.3f}'
    WLOG(p, '', wmsg.format(fraction))

    # ----------------------------------------------------------------------
    # Perform PCA analysis on the log of the telluric absorption map
    # ----------------------------------------------------------------------
    # Requires p:
    #           TELLU_NUMBER_OF_PRINCIPLE_COMP
    #           ADD_DERIV_PC
    #           FIT_DERIV_PC
    # Requires loc:
    #           DATA
    # Returns loc:
    #           PC
    #           NPC
    #           FIT_PC
    loc = spirouTelluric.CalculateAbsorptionPCA(p, loc, log_abso, keep)

    # Plot PCA components
    # debug plot
    if p['DRS_PLOT'] and (p['DRS_DEBUG'] > 1):
        # plot the transmission map plot
        sPlt.tellu_pca_comp_plot(p, loc)

    # ----------------------------------------------------------------------
    # Get master wavelength grid for shifting
    # ----------------------------------------------------------------------
    # get master wave map
    loc['MASTERWAVEFILE'] = spirouDB.GetDatabaseMasterWave(p)
    loc.set_source('MASTERWAVEFILE', main_name)
    # log progress
    wmsg1 = 'Getting master wavelength grid'
    wmsg2 = '\tFile = {0}'.format(os.path.basename(loc['MASTERWAVEFILE']))
    WLOG(p, '', [wmsg1, wmsg2])
    # Force A and B to AB solution
    if p['FIBER'] in ['A', 'B']:
        wave_fiber = 'AB'
    else:
        wave_fiber = p['FIBER']
    # read master wave map
    mout = spirouImage.GetWaveSolution(p, filename=loc['MASTERWAVEFILE'],
                                       return_wavemap=True, quiet=True,
                                       fiber=wave_fiber)
    _, loc['MASTERWAVE'], _ = mout
    loc.set_source('MASTERWAVE', main_name)

    # ----------------------------------------------------------------------
    # Loop around telluric files
    # ----------------------------------------------------------------------
    for basefilename in p['ARG_FILE_NAMES']:

        # ------------------------------------------------------------------
        # Construct absolute file path
        # ------------------------------------------------------------------
        filename = os.path.join(p['ARG_FILE_DIR'], basefilename)
        # ------------------------------------------------------------------
        # Construct output file names
        # ------------------------------------------------------------------
        outfile1, tag1 = CONSTANTS.TELLU_FIT_OUT_FILE(p, filename)
        outfilename1 = os.path.basename(outfile1)
        outfile2, tag2 = CONSTANTS.TELLU_FIT_RECON_FILE(p, filename)
        outfilename2 = os.path.basename(outfile2)

        # ------------------------------------------------------------------
        # Read filename
        # ------------------------------------------------------------------
        # read image
        tdata, thdr, _, _ = spirouImage.ReadImage(p, filename)
        # normalise with blaze function
        loc['SP'] = tdata / loc['NBLAZE']
        loc.set_source('SP', main_name)

        # ------------------------------------------------------------------
        # Set storage
        # ------------------------------------------------------------------
        loc['RECON_ABSO'] = np.ones(np.product(loc['DATA'].shape))
        loc['AMPS_ABSOL_TOTAL'] = np.zeros(loc['NPC'])
        loc.set_sources(['RECON_ABSO', 'AMPS_ABSOL_TOTAL'], main_name)

        # ------------------------------------------------------------------
        # Read wavelength solution
        # ------------------------------------------------------------------
        # Force A and B to AB solution
        if p['FIBER'] in ['A', 'B']:
            wave_fiber = 'AB'
        else:
            wave_fiber = p['FIBER']
        # get wavelength solution
        wout = spirouImage.GetWaveSolution(p, image=tdata, hdr=thdr,
                                           return_wavemap=True,
                                           return_filename=True,
                                           fiber=wave_fiber)
        _, loc['WAVE_IT'], loc['WAVEFILE'], loc['WSOURCE'] = wout
        loc.set_sources(['WAVE_IT', 'WAVEFILE', 'WSOURCE'], main_name)
        # load wave keys
        loc = spirouImage.GetWaveKeys(p, loc, thdr)

        # ------------------------------------------------------------------
        # Interpolate at shifted wavelengths (if we have a template)
        # ------------------------------------------------------------------
        if loc['FLAG_TEMPLATE']:
            # Requires p:
            #           TELLU_FIT_KEEP_FRAC
            # Requires loc:
            #           DATA
            #           TEMPLATE
            #           WAVE_IT
            # Returns:
            #           TEMPLATE2
            loc = spirouTelluric.BervCorrectTemplate(p, loc, thdr)

            # debug plot
            if p['DRS_PLOT'] and (p['DRS_DEBUG'] > 1):
                # plot the transmission map plot
                sPlt.tellu_fit_tellu_spline_plot(p, loc)

        # store PC and TAPAS_ALL_SPECIES before shift
        loc['PC_PRESHIFT'] = np.array(loc['PC'])
        loc['TAPAS_ALL_PRESHIFT'] = np.array(loc['TAPAS_ALL_SPECIES'])
        loc.set_sources(['PC_PRESHIFT', 'TAPAS_ALL_PRESHIFT'], main_name)

        # ------------------------------------------------------------------
        # Shift the pca components to correct frame
        # ------------------------------------------------------------------
        # log process
        wmsg1 = 'Shifting PCA components from master wavelength grid'
        wmsg2 = '\tFile = {0}'.format(os.path.basename(loc['MASTERWAVEFILE']))
        WLOG(p, '', [wmsg1, wmsg2])
        # shift pca components (one by one)
        for comp in range(loc['NPC']):
            wargs = [p, loc['PC'][:, comp], loc['MASTERWAVE'], loc['WAVE_IT']]
            shift_pc = spirouTelluric.Wave2Wave(*wargs, reshape=True)
            loc['PC'][:, comp] = shift_pc.reshape(wargs[1].shape)

            wargs = [p, loc['FIT_PC'][:, comp], loc['MASTERWAVE'],
                     loc['WAVE_IT']]
            shift_fpc = spirouTelluric.Wave2Wave(*wargs, reshape=True)
            loc['FIT_PC'][:, comp] = shift_fpc.reshape(wargs[1].shape)

        # ------------------------------------------------------------------
        # Shift the pca components to correct frame
        # ------------------------------------------------------------------
        # log process
        wmsg1 = 'Shifting TAPAS spectrum from master wavelength grid'
        wmsg2 = '\tFile = {0}'.format(os.path.basename(loc['MASTERWAVEFILE']))
        WLOG(p, '', [wmsg1, wmsg2])
        # shift tapas
        for comp in range(len(loc['TAPAS_ALL_SPECIES'])):
            wargs = [p, loc['TAPAS_ALL_SPECIES'][comp], loc['MASTERWAVE'],
                     loc['WAVE_IT']]
            stapas = spirouTelluric.Wave2Wave(*wargs, reshape=True)
            loc['TAPAS_ALL_SPECIES'][comp] = stapas.reshape(wargs[1].shape)

        # Debug plot to test shifting
        if p['DRS_PLOT'] and p['DRS_DEBUG'] > 1:
            sPlt.tellu_fit_debug_shift_plot(p, loc)

        # ------------------------------------------------------------------
        # Calculate reconstructed absorption
        # ------------------------------------------------------------------
        # Requires p:
        #           TELLU_FIT_MIN_TRANSMISSION
        #           TELLU_FIT_NITER
        #           TELLU_LAMBDA_MIN
        #           TELLU_LAMBDA_MAX
        #           TELLU_FIT_VSINI
        #           TRANSMISSION_CUT
        #           FIT_DERIV_PC
        #           LOG_OPT
        # Requires loc:
        #           FLAG_TEMPLATE
        #           TAPAS_ALL_SPECIES
        #           AMPS_ABSOL_TOTAL
        #           WAVE_IT
        #           TEMPLATE2
        #           FIT_PC
        #           NPC
        #           PC
        # Returns loc:
        #           SP2
        #           TEMPLATE2
        #           RECON_ABSO
        #           AMPS_ABSOL_TOTAL
        loc = spirouTelluric.CalcReconAbso(p, loc)
        # debug plot
        if p['DRS_PLOT'] > 0:
            # plot the recon abso plot
            sPlt.tellu_fit_recon_abso_plot(p, loc)

        # ------------------------------------------------------------------
        # Get molecular absorption
        # ------------------------------------------------------------------
        # Requires p:
        #           TELLU_FIT_LOG_LIMIT
        # Requeres loc:
        #           RECON_ABSO
        #           TAPAS_ALL_SPECIES
        # Returns loc:
        #           TAPAS_{molecule}
        loc = spirouTelluric.CalcMolecularAbsorption(p, loc)

        # ----------------------------------------------------------------------
        # Quality control
        # ----------------------------------------------------------------------
        # set passed variable and fail message list
        passed, fail_msg = True, []
        qc_values, qc_names, qc_logic, qc_pass = [], [], [], []
        # ----------------------------------------------------------------------
        # get SNR for each order from header
        nbo = loc['DATA'].shape[0]
        snr_order = p['QC_FIT_TELLU_SNR_ORDER']
        snr = spirouImage.Read1Dkey(p, thdr, p['kw_E2DS_SNR'][0], nbo)
        # check that SNR is high enough
        if snr[snr_order] < p['QC_FIT_TELLU_SNR_MIN']:
            fmsg = 'low SNR in order {0}: ({1:.2f} < {2:.2f})'
            fargs = [snr_order, snr[snr_order], p['QC_FIT_TELLU_SNR_MIN']]
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
                                               p['QC_FIT_TELLU_SNR_ORDER']))
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
        # Get components amplitudes for header
        # ------------------------------------------------------------------
        # get raw file name
        raw_in_file = os.path.basename(p['FITSFILENAME'])
        # copy original keys
        hdict = spirouImage.CopyOriginalKeys(thdr)
        # add version number
        hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_DATE'],
                                   value=p['DRS_DATE'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_DATE_NOW'],
                                   value=p['DATE_NOW'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_PID'], value=p['PID'])
        # set the input files
        hdict = spirouImage.AddKey(p, hdict, p['KW_CDBBLAZE'],
                                   value=p['BLAZFILE'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_CDBWAVE'],
                                   value=loc['WAVEFILE'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_WAVESOURCE'],
                                   value=loc['WSOURCE'])
        hdict = spirouImage.AddKey1DList(p, hdict, p['KW_INFILE1'],
                                         dim1name='file',
                                         values=p['ARG_FILE_NAMES'])
        # add qc parameters
        hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_QC'], value=p['QC'])
        hdict = spirouImage.AddQCKeys(p, hdict, qc_params)
        # set tellu keys
        npc = loc['NPC']
        hdict = spirouImage.AddKey(p, hdict, p['KW_TELLU_NPC'], value=npc)
        hdict = spirouImage.AddKey(p, hdict, p['KW_TELLU_FIT_DPC'],
                                   value=p['FIT_DERIV_PC'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_TELLU_ADD_DPC'],
                                   value=p['ADD_DERIV_PC'])
        if p['ADD_DERIV_PC']:
            values = loc['AMPS_ABSOL_TOTAL'][:npc - 2]
            hdict = spirouImage.AddKey1DList(p, hdict, p['KW_TELLU_AMP_PC'],
                                             values=values, dim1name='amp')
            hdict = spirouImage.AddKey(p, hdict, p['KW_TELLU_DV_TELL1'],
                                       value=loc['AMPS_ABSOL_TOTAL'][npc - 2])
            hdict = spirouImage.AddKey(p, hdict, p['KW_TELLU_DV_TELL2'],
                                       value=loc['AMPS_ABSOL_TOTAL'][npc - 1])
        else:
            values = loc['AMPS_ABSOL_TOTAL'][:npc]
            hdict = spirouImage.AddKey1DList(p, hdict, p['KW_TELLU_AMP_PC'],
                                             values=values, dim1name='PC')

        # ------------------------------------------------------------------
        # Write corrected spectrum to E2DS
        # ------------------------------------------------------------------
        # reform the E2DS
        sp_out = loc['SP2'] / loc['RECON_ABSO']
        sp_out = sp_out.reshape(loc['DATA'].shape)
        # multiply by blaze
        sp_out = sp_out * loc['NBLAZE']
        hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag1)
        # log progress
        wmsg = 'Saving {0} to file'.format(outfilename1)
        WLOG(p, '', wmsg)
        # write sp_out to file
        p = spirouImage.WriteImage(p, outfile1, sp_out, hdict)

        # ------------------------------------------------------------------
        # 1-dimension spectral S1D (uniform in wavelength)
        # ------------------------------------------------------------------
        # get arguments for E2DS to S1D
        e2dsargs = [loc['WAVE'], sp_out, loc['BLAZE']]
        # get 1D spectrum
        xs1d1, ys1d1 = spirouImage.E2DStoS1D(p, *e2dsargs, wgrid='wave')
        # Plot the 1D spectrum
        if p['DRS_PLOT'] > 0:
            sPlt.ext_1d_spectrum_plot(p, xs1d1, ys1d1)
        # construct file name
        targs = [p, raw_in_file]
        s1dfile1, tag3 = spirouConfig.Constants.TELLU_FIT_S1D_FILE1(*targs)
        s1dfilename1 = os.path.basename(s1dfile1)
        # add header keys
        # set the version
        hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_DATE'],
                                   value=p['DRS_DATE'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_DATE_NOW'],
                                   value=p['DATE_NOW'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag3)
        hdict = spirouImage.AddKey(p, hdict, p['KW_EXT_TYPE'],
                                   value=p['DPRTYPE'])
        # log writing to file
        wmsg = 'Saving 1D spectrum (uniform in wavelength) in {0}'
        WLOG(p, '', wmsg.format(s1dfilename1))
        # Write to file
        columns = ['wavelength', 'flux', 'eflux']
        values = [xs1d1, ys1d1, np.zeros_like(ys1d1)]
        units = ['nm', None, None]
        s1d1 = spirouImage.MakeTable(p, columns, values, units=units)
        spirouImage.WriteTable(p, s1d1, s1dfile1, header=hdict)

        # ------------------------------------------------------------------
        # 1-dimension spectral S1D (uniform in velocity)
        # ------------------------------------------------------------------
        # get arguments for E2DS to S1D
        e2dsargs = [loc['WAVE'], sp_out, loc['BLAZE']]
        # get 1D spectrum
        xs1d2, ys1d2 = spirouImage.E2DStoS1D(p, *e2dsargs, wgrid='velocity')
        # Plot the 1D spectrum
        if p['DRS_PLOT'] > 0:
            sPlt.ext_1d_spectrum_plot(p, xs1d2, ys1d2)
        # construct file name
        targs = [p, raw_in_file]
        s1dfile2, tag4 = spirouConfig.Constants.TELLU_FIT_S1D_FILE2(*targs)
        s1dfilename2 = os.path.basename(s1dfile2)
        # add header keys
        hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_DATE'],
                                   value=p['DRS_DATE'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_DATE_NOW'],
                                   value=p['DATE_NOW'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag4)
        hdict = spirouImage.AddKey(p, hdict, p['KW_EXT_TYPE'],
                                   value=p['DPRTYPE'])
        # log writing to file
        wmsg = 'Saving 1D spectrum (uniform in velocity) in {0}'
        WLOG(p, '', wmsg.format(s1dfilename2))
        # Write to file
        columns = ['wavelength', 'flux', 'eflux']
        values = [xs1d2, ys1d2, np.zeros_like(ys1d2)]
        units = ['nm', None, None]
        s1d2 = spirouImage.MakeTable(p, columns, values, units=units)
        spirouImage.WriteTable(p, s1d2, s1dfile2, header=hdict)

        # ------------------------------------------------------------------
        # Write reconstructed absorption to E2DS
        # ------------------------------------------------------------------
        # set up empty storage
        recon_abso2 = np.zeros_like(loc['DATA'])
        # get dimensions of data
        ydim, xdim = loc['DATA'].shape
        # loop around orders
        for order_num in range(ydim):
            # get start and end points
            start, end = xdim * order_num, xdim * order_num + xdim
            # save to storage
            recon_abso2[order_num, :] = loc['RECON_ABSO'][start:end]
        # add molecular absorption to file
        for it, molecule in enumerate(p['TELLU_ABSORBERS'][1:]):
            # get molecule keyword store and key
            molkey = '{0}_{1}'.format(p['KW_TELLU_ABSO'][0], molecule.upper())
            molkws = [molkey, 0, 'Absorption in {0}'.format(molecule.upper())]
            # load into hdict
            hdict = spirouImage.AddKey(p, hdict, molkws, value=loc[molkey])
            # add water col
            if molecule == 'h2o':
                loc['WATERCOL'] = loc[molkey]
                # set source
                loc.set_source('WATERCOL', main_name)

        # log progress
        wmsg = 'Saving {0} to file'.format(outfilename2)
        WLOG(p, '', wmsg)
        # write recon_abso to file
        hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag2)
        p = spirouImage.WriteImage(p, outfile2, recon_abso2, hdict)

        # ------------------------------------------------------------------
        # Update the Telluric database
        # ------------------------------------------------------------------
        if p['QC']:
            # add TELLU_OBJ to telluric database
            oparams = dict(objname=loc['OBJNAME'], berv=loc['BERV'],
                           airmass=loc['AIRMASS'], watercol=loc['WATERCOL'])
            spirouDB.UpdateDatabaseTellObj(p, outfilename1, **oparams)
            # copy file to database
            spirouDB.PutTelluFile(p, outfile1)
            # add TELLU_RECON to telluric database
            # add TELLU_OBJ to telluric database
            oparams = dict(objname=loc['OBJNAME'], berv=loc['BERV'],
                           airmass=loc['AIRMASS'], watercol=loc['WATERCOL'])
            spirouDB.UpdateDatabaseTellRecon(p, outfilename2, **oparams)
            # copy file to database
            spirouDB.PutTelluFile(p, outfile2)

    # ----------------------------------------------------------------------
    # End plotting
    # ----------------------------------------------------------------------
    # debug plot
    if p['DRS_PLOT'] > 0:
        # end interactive session
        sPlt.end_interactive_session(p)

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
    spirouStartup.Exit(ll)

# =============================================================================
# End of code
# =============================================================================
