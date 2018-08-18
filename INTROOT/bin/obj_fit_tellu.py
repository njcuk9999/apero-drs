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

  recon_abso file - The reconstructed absorption file saved in the reduced folder
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
# if __name__ == '__main__':
#
#     import sys
#     sys.argv = 'obj_fit_tellu.py tellu_e2ds 2279005o_HR8489_pp_e2dsff_AB.fits'.split()
#     night_name, files = None, None

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
    loc['DATA'], loc['DATAHDR'], loc['DATACDR'], loc['XDIM'], loc['YDIM'] = rd
    loc.set_sources(['DATA', 'DATAHDR', 'DATACDR', 'XDIM', 'YDIM'], main_name)


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
    loc['WAVE'] = spirouImage.GetWaveSolution(p, loc['DATA'], loc['DATAHDR'])

    # ----------------------------------------------------------------------
    # Get and Normalise the blaze
    # ----------------------------------------------------------------------
    loc = spirouTelluric.GetNormalizedBlaze(p, loc, loc['DATAHDR'])

    # ----------------------------------------------------------------------
    # Load transmission files
    # ----------------------------------------------------------------------
    transdata = spirouDB.GetDatabaseTellMap(p)
    trans_files = transdata[0]

    # ----------------------------------------------------------------------
    # Start plotting
    # ----------------------------------------------------------------------
    if p['DRS_PLOT']:
        # start interactive plot
        sPlt.start_interactive_session()

    # ----------------------------------------------------------------------
    # Load template (if available)
    # ----------------------------------------------------------------------
    # TODO: Is this per object? If so how do we select? Based on OBJNAME?
    # TODO: Currently just selects the most recent
    # read filename from telluDB
    template_file = spirouDB.GetDatabaseTellTemp(p, loc['OBJNAME'],
                                                 required=False)
    # if we don't have a template flag it
    if template_file is None:
        loc['FLAG_TEMPLATE'] = False
        loc['TEMPLATE'] = None
    else:
        loc['FLAG_TEMPLATE'] = True
        # load template
        template, _, _, _, _ = spirouImage.ReadImage(p, template_file)
        # renormalize the template
        template = template / loc['NBLAZE']
        # add to loc
        loc['TEMPLATE'] = template
    # set the source for flag and template
    loc.set_sources(['FLAG_TEMPLATE', 'TEMPLATE'], main_name)

    # ----------------------------------------------------------------------
    # load the expected atmospheric transmission
    # ----------------------------------------------------------------------
    # read filename from telluDB
    # TODO: This is per wave solution but wave solution in e2ds file header
    # TODO:  If so how do we select?
    # TODO: Currently just selects the most recent
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
        WLOG('error', p['LOG_OPT'], [emsg1, emsg2.format(nfiles, npc),
                                     emsg3, emsg4])
    # set up storage for the absorption
    abso = np.zeros([nfiles, np.product(loc['DATA'].shape)])
    # loop around outputfiles and add them to abso
    for it, filename in enumerate(trans_files):
        # push data into array
        data_it, _, _, _, _ = spirouImage.ReadImage(p, filename=filename)
        abso[it, :] = data_it.reshape(np.product(loc['DATA'].shape))



    # log the absorption cube
    with warnings.catch_warnings(record=True) as w:
        log_abso = np.log(abso)

    # ----------------------------------------------------------------------
    # Locate valid pixels for PCA
    # ----------------------------------------------------------------------
    # determining the pixels relevant for PCA construction
    keep = np.isfinite(np.sum(abso, axis=0))
    # log fraction of valid (non NaN) pixels
    fraction = np.sum(keep)/len(keep)
    wmsg = 'Fraction of valid pixels (not NaNs) for PCA construction = {0:.3f}'
    WLOG('', p['LOG_OPT'], wmsg.format(fraction))
    # log fraction of valid pixels > 1 - (1/e)
    with warnings.catch_warnings(record=True) as w:
        keep &= np.min(log_abso, axis=0) > -1
    fraction = np.sum(keep)/len(keep)
    wmsg = 'Fraction of valid pixels with transmission > 1 - (1/e) = {0:.3f}'
    WLOG('', p['LOG_OPT'], wmsg.format(fraction))

    # ----------------------------------------------------------------------
    # Perform PCA analysis on the log of the telluric absorption map
    # ----------------------------------------------------------------------
    loc = spirouTelluric.CalculateAbsorptionPCA(p, loc, log_abso, keep)
    # Plot PCA components
    # debug plot
    if p['DRS_PLOT'] and (p['DRS_DEBUG'] > 1):
        # plot the transmission map plot
        sPlt.tellu_pca_comp_plot(p, loc)

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
        outfile1 = spirouConfig.Constants.TELLU_FIT_OUT_FILE(p, filename)
        outfilename1 = os.path.basename(outfile1)
        outfile2 = spirouConfig.Constants.TELLU_FIT_RECON_FilE(p, filename)
        outfilename2 = os.path.basename(outfile2)

        # ------------------------------------------------------------------
        # Skip if output file already exists
        # ------------------------------------------------------------------
        # TODO: Do we really want to skip?
        # if os.path.exists(outfile1):
        #     # log that file was skipped
        #     wmsg = 'File "{0}" exist, skipping.'
        #     WLOG('', p['LOG_OPT'], wmsg.format(outfilename1))
        #     continue

        # ------------------------------------------------------------------
        # Read filename
        # ------------------------------------------------------------------
        # read image
        tdata, thdr, tcdr, _, _ = spirouImage.ReadImage(p, filename)
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
        loc['WAVE_IT'] = spirouImage.GetWaveSolution(p, tdata, thdr)
        loc.set_source('WAVE_IT', main_name)
        # load wave keys
        loc = spirouImage.GetWaveKeys(p, loc, thdr)

        # ------------------------------------------------------------------
        # Interpolate at shifted wavelengths (if we have a template)
        # ------------------------------------------------------------------
        if loc['FLAG_TEMPLATE']:
            loc = spirouTelluric.InterpAtShiftedWavelengths(p, loc, thdr)

            # debug plot
            if p['DRS_PLOT'] and (p['DRS_DEBUG'] > 1):
                # plot the transmission map plot
                sPlt.tellu_fit_tellu_spline_plot(p, loc)

        # ------------------------------------------------------------------
        # Calculate reconstructed absorption
        # ------------------------------------------------------------------
        loc = spirouTelluric.CalcReconAbso(p, loc)
        # debug plot
        if p['DRS_PLOT'] and (p['DRS_DEBUG'] > 1):
            # plot the recon abso plot
            sPlt.tellu_fit_recon_abso_plot(p, loc)

        # ------------------------------------------------------------------
        # Get molecular absorption
        # ------------------------------------------------------------------
        loc = spirouTelluric.CalcMolecularAbsorption(p, loc)

        # ------------------------------------------------------------------
        # Get components amplitudes for header
        # ------------------------------------------------------------------
        hdict = OrderedDict()

        # add version number
        hdict = spirouImage.AddKey(hdict, p['KW_VERSION'])

        npc = loc['NPC']
        if p['ADD_DERIV_PC']:
            values = loc['AMPS_ABSOL_TOTAL'][:npc-2]
            hdict = spirouImage.AddKey1DList(hdict, p['KW_TELLU_AMP_PC'],
                                             values=values, dim1name='amp')
            hdict = spirouImage.AddKey(hdict, p['KW_TELLU_DV_TELL1'],
                                       value=loc['AMPS_ABSOL_TOTAL'][npc - 2])
            hdict = spirouImage.AddKey(hdict, p['KW_TELLU_DV_TELL2'],
                                       value=loc['AMPS_ABSOL_TOTAL'][npc - 1])
        else:
            values = loc['AMPS_ABSOL_TOTAL'][:npc]
            hdict = spirouImage.AddKey1DList(hdict, p['KW_TELLU_AMP_PC'],
                                             values=values, dim1name='PC')


        # ------------------------------------------------------------------
        # Write corrected spectrum to E2DS
        # ------------------------------------------------------------------
        # reform the E2DS
        sp_out = loc['SP2'] / loc['RECON_ABSO']
        sp_out = sp_out.reshape(loc['DATA'].shape)
        # multiply by blaze
        sp_out = sp_out * loc['NBLAZE']
        # copy original keys
        hdict = spirouImage.CopyOriginalKeys(thdr, tcdr, hdict=hdict)
        # write sp_out to file
        spirouImage.WriteImage(outfile1, sp_out, hdict)

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
            hdict = spirouImage.AddKey(hdict, molkws, value=loc[molkey])
            # add water col
            if molecule == 'h2o':
                loc['WATERCOL'] = loc[molkey]
                # set source
                loc.set_source('WATERCOL', main_name)
        # write recon_abso to file
        spirouImage.WriteImage(outfile2, recon_abso2, hdict)

        # ------------------------------------------------------------------
        # Update the Telluric database
        # ------------------------------------------------------------------
        # add to telluric database
        oparams = dict(objname=loc['OBJNAME'], berv=loc['BERV'],
                       airmass=loc['AIRMASS'], watercol=loc['WATERCOL'])
        spirouDB.UpdateDatavaseTellObj(p, outfilename1, **oparams)
        # copy file to database
        spirouDB.PutTelluFile(p, outfile1)

    # ----------------------------------------------------------------------
    # End plotting
    # ----------------------------------------------------------------------
    # debug plot
    if p['DRS_PLOT']:
        # end interactive session
        sPlt.end_interactive_session()

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
