#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cal_SLIT_spirou.py [night_directory] [files]

Fabry-Perot exposures in which the three fibres are simultaneously fed by light
from the Fabry-Perot filter. Each exposure is used to build the slit
orientation. Finds the tilt of the orders.

Created on 2017-11-06 11:32

@author: cook

Last modified: 2017-12-11 at 15:09

Up-to-date with cal_SLIT_spirou AT-4 V47
"""
from __future__ import division
import numpy as np
import os

from SpirouDRS import spirouBACK
from SpirouDRS import spirouDB
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouLOCOR
from SpirouDRS import spirouStartup
from SpirouDRS import spirouTHORCA


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_SHAPE_spirou.py'
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


# =============================================================================
# Define functions
# =============================================================================
def main(night_name=None, fpfile=None, hcfiles=None):
    """
    cal_SLIT_spirou.py main function, if night_name and files are None uses
    arguments from run time i.e.:
        cal_SLIT_spirou.py [night_directory] [files]

    :param night_name: string or None, the folder within data raw directory
                                containing files (also reduced directory) i.e.
                                /data/raw/20170710 would be "20170710" but
                                /data/raw/AT5/20180409 would be "AT5/20180409"
    :param files: string, list or None, the list of files to use for
                  arg_file_names and fitsfilename
                  (if None assumes arg_file_names was set from run time)

    :return ll: dictionary, containing all the local variables defined in
                main
    """
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)
    if hcfiles is None or fpfile is None:
        names, types = ['fpfile', 'hcfiles'], [str, str]
        customargs = spirouStartup.GetCustomFromRuntime([0, 1], types, names,
                                                        last_multi=True)
    else:
        customargs = dict(hcfiles=hcfiles, fpfile=fpfile)

    # get parameters from configuration files and run time arguments
    p = spirouStartup.LoadArguments(p, night_name, customargs=customargs,
                                    mainfitsfile='hcfiles')

    # make sure we only have one HCFILE more than one is not currently
    # supported
    # TODO: Fix problem with updating output and then remove this
    if len(p['HCFILES']) > 1:
        emsg = 'Currently we do not support multiple HCFILES'
        WLOG('error', p['LOG_OPT'], emsg)

    # ----------------------------------------------------------------------
    # Construct reference filename and get fiber type
    # ----------------------------------------------------------------------
    p, fpfitsfilename = spirouStartup.SingleFileSetup(p, filename=p['FPFILE'])
    fiber1 = str(p['FIBER'])
    p, hcfilenames = spirouStartup.MultiFileSetup(p, files=p['HCFILES'])
    fiber2 = str(p['FIBER'])
    # set the hcfilename to the first hcfilenames
    hcfitsfilename = hcfilenames[0]

    # ----------------------------------------------------------------------
    # Once we have checked the e2dsfile we can load calibDB
    # ----------------------------------------------------------------------
    # as we have custom arguments need to load the calibration database
    p = spirouStartup.LoadCalibDB(p)

    # ----------------------------------------------------------------------
    # Have to check that the fibers match
    # ----------------------------------------------------------------------
    if fiber1 == fiber2:
        p['FIBER'] = fiber1
        fsource = __NAME__ + '/main() & spirouStartup.GetFiberType()'
        p.set_source('FIBER', fsource)
    else:
        emsg = 'Fiber not matching for {0} and {1}, should be the same'
        eargs = [hcfitsfilename, fpfitsfilename]
        WLOG('error', p['LOG_OPT'], emsg.format(*eargs))
    # set the fiber type
    p['FIB_TYP'] = [p['FIBER']]
    p.set_source('FIB_TYP', __NAME__ + '/main()')

    # ----------------------------------------------------------------------
    # Read FP and HC files
    # ----------------------------------------------------------------------

    # read and combine all HC files except the first (fpfitsfilename)
    rargs = [p, 'add', hcfitsfilename, hcfilenames[1:]]
    p, hcdata, hchdr, hccdr = spirouImage.ReadImageAndCombine(*rargs)
    # read first file (fpfitsfilename)
    fpdata, fphdr, fpcdr, _, _ = spirouImage.ReadImage(p, fpfitsfilename)

    # add data and hdr to loc
    loc = ParamDict()
    loc['HCDATA'], loc['HCHDR'], loc['HCCDR'] = hcdata, hchdr, hccdr
    loc['FPDATA'], loc['FPHDR'], loc['FPCDR'] = fpdata, fphdr, fpcdr
    # set the source
    sources = ['HCDATA', 'HCHDR', 'HCCDR']
    loc.set_sources(sources, 'spirouImage.ReadImageAndCombine()')
    sources = ['FPDATA', 'FPHDR', 'FPCDR']
    loc.set_sources(sources, 'spirouImage.ReadImage()')

    # ---------------------------------------------------------------------
    # fix for un-preprocessed files
    # ----------------------------------------------------------------------
    hcdata = spirouImage.FixNonPreProcess(p, hcdata)
    fpdata = spirouImage.FixNonPreProcess(p, fpdata)

    # ----------------------------------------------------------------------
    # Get basic image properties for reference file
    # ----------------------------------------------------------------------
    # get sig det value
    p = spirouImage.GetSigdet(p, fphdr, name='sigdet')
    # get exposure time
    p = spirouImage.GetExpTime(p, fphdr, name='exptime')
    # get gain
    p = spirouImage.GetGain(p, fphdr, name='gain')
    # get lamp parameters
    p = spirouTHORCA.GetLampParams(p, hchdr)

    # ----------------------------------------------------------------------
    # Correction of DARK
    # ----------------------------------------------------------------------
    p, hcdatac = spirouImage.CorrectForDark(p, hcdata, hchdr)
    hcdatac = hcdata

    p, fpdatac = spirouImage.CorrectForDark(p, fpdata, fphdr)
    fpdatac = fpdata

    # ----------------------------------------------------------------------
    # Resize hc data
    # ----------------------------------------------------------------------
    # rotate the image and convert from ADU/s to e-
    hcdata = spirouImage.ConvertToE(spirouImage.FlipImage(hcdatac), p=p)
    # convert NaN to zeros
    hcdata0 = np.where(~np.isfinite(hcdata), np.zeros_like(hcdata), hcdata)
    # resize image
    bkwargs = dict(xlow=p['IC_CCDX_LOW'], xhigh=p['IC_CCDX_HIGH'],
                   ylow=p['IC_CCDY_LOW'], yhigh=p['IC_CCDY_HIGH'],
                   getshape=False)
    hcdata2 = spirouImage.ResizeImage(hcdata0, **bkwargs)
    # log change in data size
    WLOG('', p['LOG_OPT'], ('HC Image format changed to '
                            '{0}x{1}').format(*hcdata2.shape))

    # ----------------------------------------------------------------------
    # Resize fp data
    # ----------------------------------------------------------------------
    # rotate the image and convert from ADU/s to e-
    fpdata = spirouImage.ConvertToE(spirouImage.FlipImage(fpdatac), p=p)
    # convert NaN to zeros
    fpdata0 = np.where(~np.isfinite(fpdata), np.zeros_like(fpdata), fpdata)
    # resize image
    bkwargs = dict(xlow=p['IC_CCDX_LOW'], xhigh=p['IC_CCDX_HIGH'],
                   ylow=p['IC_CCDY_LOW'], yhigh=p['IC_CCDY_HIGH'],
                   getshape=False)
    fpdata2 = spirouImage.ResizeImage(fpdata0, **bkwargs)
    # log change in data size
    WLOG('', p['LOG_OPT'], ('FP Image format changed to '
                            '{0}x{1}').format(*fpdata2.shape))


    # ----------------------------------------------------------------------
    # Correct for the BADPIX mask (set all bad pixels to zero)
    # ----------------------------------------------------------------------
    p, hcdata2 = spirouImage.CorrectForBadPix(p, hcdata2, hchdr)
    p, fpdata2 = spirouImage.CorrectForBadPix(p, fpdata2, fphdr)

    # ----------------------------------------------------------------------
    # Background computation for HC file
    # ----------------------------------------------------------------------
    if p['IC_DO_BKGR_SUBTRACTION']:
        # log that we are doing background measurement
        WLOG('', p['LOG_OPT'], 'Doing background measurement on raw frame')
        # get the bkgr measurement
        bdata = spirouBACK.MeasureBackgroundFF(p, hcdata2)
        background, gridx, gridy, minlevel = bdata
    else:
        background = np.zeros_like(hcdata2)

    hcdata2 = hcdata2 - background

    # correct data2 with background (where positive)
    hcdata2 = np.where(hcdata2 > 0, hcdata2 - background, 0)

    # save data to loc
    loc = ParamDict()
    loc['HCDATA'] = hcdata2
    loc.set_source('HCDATA', __NAME__ + '/main()')

    # ----------------------------------------------------------------------
    # Background computation for FP file
    # ----------------------------------------------------------------------
    if p['IC_DO_BKGR_SUBTRACTION']:
        # log that we are doing background measurement
        WLOG('', p['LOG_OPT'], 'Doing background measurement on raw frame')
        # get the bkgr measurement
        bdata = spirouBACK.MeasureBackgroundFF(p, fpdata2)
        background, gridx, gridy, minlevel = bdata
    else:
        background = np.zeros_like(fpdata2)

    fpdata2 = fpdata2 - background

    # correct data2 with background (where positive)
    fpdata2 = np.where(fpdata2 > 0, fpdata2 - background, 0)

    # save data to loc
    loc = ParamDict()
    loc['FPDATA'] = fpdata2
    loc.set_source('FPDATA', __NAME__ + '/main()')

    # ----------------------------------------------------------------------
    # Log the number of dead pixels
    # ----------------------------------------------------------------------
    # get the number of bad pixels
    n_bad_pix = np.sum(hcdata2 <= 0)
    n_bad_pix_frac = n_bad_pix * 100 / np.product(hcdata2.shape)
    # Log number
    wmsg = 'Nb HC dead pixels = {0} / {1:.2f} %'
    WLOG('info', p['LOG_OPT'], wmsg.format(int(n_bad_pix), n_bad_pix_frac))

    # ----------------------------------------------------------------------
    # Log the number of dead pixels
    # ----------------------------------------------------------------------
    # get the number of bad pixels
    n_bad_pix = np.sum(fpdata2 <= 0)
    n_bad_pix_frac = n_bad_pix * 100 / np.product(fpdata2.shape)
    # Log number
    wmsg = 'Nb FP dead pixels = {0} / {1:.2f} %'
    WLOG('info', p['LOG_OPT'], wmsg.format(int(n_bad_pix), n_bad_pix_frac))

    # ------------------------------------------------------------------
    # Get localisation coefficients
    # ------------------------------------------------------------------
    # original there is a loop but it is not used --> removed
    p = spirouImage.FiberParams(p, p['FIBER'], merge=True)
    # get localisation fit coefficients
    p, loc = spirouLOCOR.GetCoeffs(p, fphdr, loc)

    # ------------------------------------------------------------------
    # Get master wave solution map
    # ------------------------------------------------------------------
    # get master wave map
    masterwavefile = spirouDB.GetDatabaseMasterWave(p)
    # log process
    wmsg1 = 'Shifting transmission map on to master wavelength grid'
    wmsg2 = '\tFile = {0}'.format(os.path.basename(masterwavefile))
    WLOG('', p['LOG_OPT'], [wmsg1, wmsg2])
    # Force A and B to AB solution
    if p['FIBER'] in ['A', 'B']:
        wave_fiber = 'AB'
    else:
        wave_fiber = p['FIBER']
    # read master wave map
    mout = spirouImage.GetWaveSolution(p, filename=masterwavefile,
                                       return_wavemap=True, quiet=True,
                                       return_header=True, fiber=wave_fiber)
    loc['MASTERWAVEP'], loc['MASTERWAVE'], loc['MASTERWAVEHDR'] = mout
    # set sources
    wsource = ['MASTERWAVEP', 'MASTERWAVE', 'MASTERWAVEHDR']
    loc.set_sources(wsource, 'spirouImage.GetWaveSolution()')

    # ----------------------------------------------------------------------
    # Read UNe solution
    # ----------------------------------------------------------------------
    wave_u_ne, amp_u_ne = spirouImage.ReadLineList(p)
    loc['LL_LINE'], loc['AMPL_LINE'] = wave_u_ne, amp_u_ne
    source = __NAME__ + '.main() + spirouImage.ReadLineList()'
    loc.set_sources(['LL_LINE', 'AMPL_LINE'], source)

    # ----------------------------------------------------------------------
    # Read cavity length file
    # ----------------------------------------------------------------------
    loc['CAVITY_LEN_COEFFS'] = spirouImage.ReadCavityLength(p)
    source = __NAME__ + '.main() + spirouImage.ReadCavityLength()'
    loc.set_source('CAVITY_LEN_COEFFS', source)

    # ------------------------------------------------------------------
    # Calculate shape map
    # ------------------------------------------------------------------
    loc = spirouImage.GetShapeMap2(p, loc)

    # ------------------------------------------------------------------
    # Plotting
    # ------------------------------------------------------------------
    if p['DRS_PLOT']:
        # plots setup: start interactive plot
        sPlt.start_interactive_session()
        # plot the shape process for each order
        if p['DRS_DEBUG'] == 2:
            sPlt.slit_shape_angle_plot(p, loc, mode='all')
        # plot the shape process for one order
        else:
            sPlt.slit_shape_angle_plot(p, loc, mode='single')
        # end interactive section
        sPlt.end_interactive_session()

    # ------------------------------------------------------------------
    # Writing DXMAP to file
    # ------------------------------------------------------------------
    # get the raw tilt file name
    raw_shape_file = os.path.basename(p['FITSFILENAME'])
    # construct file name and path
    shapefits, tag = spirouConfig.Constants.SLIT_SHAPE_FILE(p)
    shapefitsname = os.path.basename(shapefits)
    # Log that we are saving tilt file
    wmsg = 'Saving shape information in file: {0}'
    WLOG('', p['LOG_OPT'], wmsg.format(shapefitsname))
    # Copy keys from fits file
    # Copy keys from fits file
    hdict = spirouImage.CopyOriginalKeys(fphdr, hccdr)
    # add version number
    hdict = spirouImage.AddKey(hdict, p['KW_VERSION'])
    hdict = spirouImage.AddKey(hdict, p['KW_OUTPUT'], value=tag)
    hdict = spirouImage.AddKey(hdict, p['KW_DARKFILE'], value=p['DARKFILE'])
    hdict = spirouImage.AddKey(hdict, p['KW_BADPFILE1'], value=p['BADPFILE1'])
    hdict = spirouImage.AddKey(hdict, p['KW_BADPFILE2'], value=p['BADPFILE2'])
    hdict = spirouImage.AddKey(hdict, p['KW_LOCOFILE'], value=p['LOCOFILE'])
    hdict = spirouImage.AddKey(hdict, p['KW_SHAPEFILE'], value=raw_shape_file)
    # write tilt file to file
    p = spirouImage.WriteImage(p, shapefits, loc['DXMAP'], hdict)


    # ------------------------------------------------------------------
    # Writing sanity check files
    # ------------------------------------------------------------------
    if p['SHAPE_DEBUG_OUTPUTS']:
        # log
        WLOG('', p['LOG_OPT'], 'Saving debug sanity check files')
        # construct file names
        input_fp_file, tag1 = spirouConfig.Constants.SLIT_SHAPE_IN_FP_FILE(p)
        output_fp_file, tag2 = spirouConfig.Constants.SLIT_SHAPE_OUT_FP_FILE(p)
        input_hc_file, tag3 = spirouConfig.Constants.SLIT_SHAPE_IN_HC_FILE(p)
        output_hc_file, tag4 = spirouConfig.Constants.SLIT_SHAPE_IN_HC_FILE(p)
        overlap_file, tag5 = spirouConfig.Constants.SLIT_SHAPE_OVERLAP_FILE(p)
        # write input fp file
        hdict = spirouImage.AddKey(hdict, p['KW_OUTPUT'], value=tag1)
        p = spirouImage.WriteImage(p, input_fp_file, loc['FPDATA'])
        # write output fp file
        hdict = spirouImage.AddKey(hdict, p['KW_OUTPUT'], value=tag2)
        p = spirouImage.WriteImage(p, output_fp_file, loc['FPDATA2'])
        # write input fp file
        hdict = spirouImage.AddKey(hdict, p['KW_OUTPUT'], value=tag3)
        p = spirouImage.WriteImage(p, input_hc_file, loc['HCDATA'])
        # write output fp file
        hdict = spirouImage.AddKey(hdict, p['KW_OUTPUT'], value=tag4)
        p = spirouImage.WriteImage(p, output_hc_file, loc['HCDATA2'])
        # write overlap file
        hdict = spirouImage.AddKey(hdict, p['KW_OUTPUT'], value=tag5)
        p = spirouImage.WriteImage(p, overlap_file, loc['ORDER_OVERLAP'])

    # ----------------------------------------------------------------------
    # Quality control
    # ----------------------------------------------------------------------
    # TODO: Decide on some quality control criteria?
    # set passed variable and fail message list
    passed, fail_msg = True, []
    # finally log the failed messages and set QC = 1 if we pass the
    # quality control QC = 0 if we fail quality control
    if passed:
        WLOG('info', p['LOG_OPT'], 'QUALITY CONTROL SUCCESSFUL - Well Done -')
        p['QC'] = 1
        p.set_source('QC', __NAME__ + '/main()')
    else:
        for farg in fail_msg:
            wmsg = 'QUALITY CONTROL FAILED: {0}'
            WLOG('warning', p['LOG_OPT'], wmsg.format(farg))
        p['QC'] = 0
        p.set_source('QC', __NAME__ + '/main()')

    # ----------------------------------------------------------------------
    # Move to calibDB and update calibDB
    # ----------------------------------------------------------------------
    if p['QC']:
        keydb = 'SHAPE'
        # copy shape file to the calibDB folder
        spirouDB.PutCalibFile(p, shapefits)
        # update the master calib DB file with new key
        spirouDB.UpdateCalibMaster(p, keydb, shapefitsname, fphdr)

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
