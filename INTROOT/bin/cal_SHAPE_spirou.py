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
# force plot off
PLOT_PER_ORDER = False


# =============================================================================
# Define functions
# =============================================================================
def main(night_name=None, hcfile=None, fpfiles=None):
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
    if hcfile is None or fpfiles is None:
        names, types = ['hcfile', 'fpfiles'], [str, str]
        customargs = spirouStartup.GetCustomFromRuntime(p, [0, 1], types, names,
                                                        last_multi=True)
    else:
        customargs = dict(hcfile=hcfile, fpfiles=fpfiles)

    # get parameters from configuration files and run time arguments
    p = spirouStartup.LoadArguments(p, night_name, customargs=customargs,
                                    mainfitsfile='fpfiles')

    # ----------------------------------------------------------------------
    # Construct reference filename and get fiber type
    # ----------------------------------------------------------------------
    p, hcfitsfilename = spirouStartup.SingleFileSetup(p, filename=p['HCFILE'])
    p, fpfilenames = spirouStartup.MultiFileSetup(p, files=p['FPFILES'])
    # set fiber (it doesn't matter with the 2D image but we need this to get
    # the lamp type for FPFILES and HCFILES, AB == C
    p['FIBER'] = 'AB'
    p['FIB_TYP'] = [p['FIBER']]
    fsource = __NAME__ + '/main()'
    p.set_sources(['FIBER', 'FIB_TYP'], fsource)
    # set the hcfilename to the first hcfilenames
    fpfitsfilename = fpfilenames[0]

    # ----------------------------------------------------------------------
    # Once we have checked the e2dsfile we can load calibDB
    # ----------------------------------------------------------------------
    # as we have custom arguments need to load the calibration database
    p = spirouStartup.LoadCalibDB(p)

    # add a force plot off
    p['PLOT_PER_ORDER'] = PLOT_PER_ORDER
    p.set_source('PLOT_PER_ORDER', __NAME__ + '.main()')

    # ----------------------------------------------------------------------
    # Read FP and HC files
    # ----------------------------------------------------------------------
    # read and combine all FP files except the first (fpfitsfilename)
    rargs = [p, 'add', fpfitsfilename, fpfilenames[1:]]
    p, fpdata, fphdr, fpcdr = spirouImage.ReadImageAndCombine(*rargs)
    # read first file (hcfitsfilename)
    hcdata, hchdr, hccdr, _, _ = spirouImage.ReadImage(p, hcfitsfilename)

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
    # p, hcdatac = spirouImage.CorrectForDark(p, hcdata, hchdr)
    hcdatac = hcdata
    p['DARKFILE'] = 'None'

    # p, fpdatac = spirouImage.CorrectForDark(p, fpdata, fphdr)
    fpdatac = fpdata

    # ----------------------------------------------------------------------
    # Resize hc data
    # ----------------------------------------------------------------------
    # rotate the image and convert from ADU/s to e-
    hcdata = spirouImage.ConvertToE(spirouImage.FlipImage(p, hcdatac), p=p)
    # convert NaN to zeros
    hcdata0 = np.where(~np.isfinite(hcdata), np.zeros_like(hcdata), hcdata)
    # resize image
    bkwargs = dict(xlow=p['IC_CCDX_LOW'], xhigh=p['IC_CCDX_HIGH'],
                   ylow=p['IC_CCDY_LOW'], yhigh=p['IC_CCDY_HIGH'],
                   getshape=False)
    hcdata2 = spirouImage.ResizeImage(p, hcdata0, **bkwargs)
    # log change in data size
    WLOG(p, '', ('HC Image format changed to '
                            '{0}x{1}').format(*hcdata2.shape))

    # ----------------------------------------------------------------------
    # Resize fp data
    # ----------------------------------------------------------------------
    # rotate the image and convert from ADU/s to e-
    fpdata = spirouImage.ConvertToE(spirouImage.FlipImage(p, fpdatac), p=p)
    # convert NaN to zeros
    fpdata0 = np.where(~np.isfinite(fpdata), np.zeros_like(fpdata), fpdata)
    # resize image
    bkwargs = dict(xlow=p['IC_CCDX_LOW'], xhigh=p['IC_CCDX_HIGH'],
                   ylow=p['IC_CCDY_LOW'], yhigh=p['IC_CCDY_HIGH'],
                   getshape=False)
    fpdata2 = spirouImage.ResizeImage(p, fpdata0, **bkwargs)
    # log change in data size
    WLOG(p, '', ('FP Image format changed to '
                            '{0}x{1}').format(*fpdata2.shape))

    # ----------------------------------------------------------------------
    # Correct for the BADPIX mask (set all bad pixels to zero)
    # ----------------------------------------------------------------------
    # p, hcdata2 = spirouImage.CorrectForBadPix(p, hcdata2, hchdr)
    # p, fpdata2 = spirouImage.CorrectForBadPix(p, fpdata2, fphdr)
    p['BADPFILE'] = 'None'

    # ----------------------------------------------------------------------
    # Background computation for HC file
    # ----------------------------------------------------------------------
    # if p['IC_DO_BKGR_SUBTRACTION']:
    #     # log that we are doing background measurement
    #     WLOG(p, '', 'Doing background measurement on HC frame')
    #     # get the bkgr measurement
    #     bdata = spirouBACK.MeasureBackgroundFF(p, hcdata2)
    #     background, gridx, gridy, minlevel = bdata
    # else:
    #     background = np.zeros_like(hcdata2)
    #
    # hcdata2 = hcdata2 - background
    #
    # # correct data2 with background (where positive)
    # hcdata2 = np.where(hcdata2 > 0, hcdata2 - background, 0)

    # save data to loc
    loc['HCDATA'] = hcdata2
    loc.set_source('HCDATA', __NAME__ + '/main()')

    # ----------------------------------------------------------------------
    # Background computation for FP file
    # ----------------------------------------------------------------------
    # if p['IC_DO_BKGR_SUBTRACTION']:
    #     # log that we are doing background measurement
    #     WLOG(p, '', 'Doing background measurement on FP frame')
    #     # get the bkgr measurement
    #     bdata = spirouBACK.MeasureBackgroundFF(p, fpdata2)
    #     background, gridx, gridy, minlevel = bdata
    # else:
    #     background = np.zeros_like(fpdata2)
    #
    # fpdata2 = fpdata2 - background
    #
    # # correct data2 with background (where positive)
    # fpdata2 = np.where(fpdata2 > 0, fpdata2 - background, 0)

    # save data to loc
    loc['FPDATA'] = fpdata2
    loc.set_source('FPDATA', __NAME__ + '/main()')

    # ----------------------------------------------------------------------
    # Log the number of dead pixels
    # ----------------------------------------------------------------------
    # get the number of bad pixels
    n_bad_pix = np.nansum(hcdata2 <= 0)
    n_bad_pix_frac = n_bad_pix * 100 / np.product(hcdata2.shape)
    # Log number
    wmsg = 'Nb HC dead pixels = {0} / {1:.2f} %'
    WLOG(p, 'info', wmsg.format(int(n_bad_pix), n_bad_pix_frac))

    # ----------------------------------------------------------------------
    # Log the number of dead pixels
    # ----------------------------------------------------------------------
    # get the number of bad pixels
    n_bad_pix = np.nansum(fpdata2 <= 0)
    n_bad_pix_frac = n_bad_pix * 100 / np.product(fpdata2.shape)
    # Log number
    wmsg = 'Nb FP dead pixels = {0} / {1:.2f} %'
    WLOG(p, 'info', wmsg.format(int(n_bad_pix), n_bad_pix_frac))

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
    wmsg1 = 'Getting master wavelength grid'
    wmsg2 = '\tFile = {0}'.format(os.path.basename(masterwavefile))
    WLOG(p, '', [wmsg1, wmsg2])
    # Force A and B to AB solution
    if p['FIBER'] in ['A', 'B']:
        wave_fiber = 'AB'
    else:
        wave_fiber = p['FIBER']
    # read master wave map
    wout = spirouImage.GetWaveSolution(p, filename=masterwavefile,
                                       return_wavemap=True, quiet=True,
                                       return_header=True, fiber=wave_fiber)
    loc['MASTERWAVEP'], loc['MASTERWAVE'] = wout[:2]
    loc['MASTERWAVEHDR'], loc['WSOURCE'] = wout[2:]
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
    loc = spirouImage.GetShapeMap(p, loc)

    # ------------------------------------------------------------------
    # Plotting
    # ------------------------------------------------------------------
    if p['DRS_PLOT'] > 0:
        # plots setup: start interactive plot
        sPlt.start_interactive_session(p)
        # plot the shape process for one order
        sPlt.slit_shape_angle_plot(p, loc)
        # end interactive section
        sPlt.end_interactive_session(p)

    # ----------------------------------------------------------------------
    # Quality control
    # ----------------------------------------------------------------------
    # TODO: Decide on some quality control criteria?
    # set passed variable and fail message list
    passed, fail_msg = True, []
    qc_values, qc_names, qc_logic, qc_pass = [], [], [], []
    # finally log the failed messages and set QC = 1 if we pass the
    # quality control QC = 0 if we fail quality control
    if passed:
        WLOG(p, 'info', 'QUALITY CONTROL SUCCESSFUL - Well Done -')
        p['QC'] = 1
        p.set_source('QC', __NAME__ + '/main()')
    else:
        for farg in fail_msg:
            wmsg = 'QUALITY CONTROL FAILED: {0}'
            WLOG(p, 'warning', wmsg.format(farg))
        p['QC'] = 0
        p.set_source('QC', __NAME__ + '/main()')
    # add to qc header lists
    qc_values.append('None')
    qc_names.append('None')
    qc_logic.append('None')
    qc_pass.append(1)
    # store in qc_params
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]

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
    WLOG(p, '', wmsg.format(shapefitsname))
    # Copy keys from fits file
    hdict = spirouImage.CopyOriginalKeys(fphdr, fpcdr)
    # add version number
    hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_PID'], value=p['PID'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag)
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBDARK'], value=p['DARKFILE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBBAD'], value=p['BADPFILE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBLOCO'], value=p['LOCOFILE'])
    hdict = spirouImage.AddKey1DList(p, hdict, p['KW_INFILE1'],
                                     dim1name='hcfile', values=p['HCFILE'])
    hdict = spirouImage.AddKey1DList(p, hdict, p['KW_INFILE2'],
                                     dim1name='fpfile', values=p['FPFILES'])
    # add qc parameters
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_QC'], value=p['QC'])
    hdict = spirouImage.AddQCKeys(p, hdict, qc_params)
    # write tilt file to file
    p = spirouImage.WriteImage(p, shapefits, loc['DXMAP'], hdict)


    # ------------------------------------------------------------------
    # Writing sanity check files
    # ------------------------------------------------------------------
    if p['SHAPE_DEBUG_OUTPUTS']:
        # log
        WLOG(p, '', 'Saving debug sanity check files')
        # construct file names
        input_fp_file, tag1 = spirouConfig.Constants.SLIT_SHAPE_IN_FP_FILE(p)
        output_fp_file, tag2 = spirouConfig.Constants.SLIT_SHAPE_OUT_FP_FILE(p)
        input_hc_file, tag3 = spirouConfig.Constants.SLIT_SHAPE_IN_HC_FILE(p)
        output_hc_file, tag4 = spirouConfig.Constants.SLIT_SHAPE_OUT_HC_FILE(p)
        overlap_file, tag5 = spirouConfig.Constants.SLIT_SHAPE_OVERLAP_FILE(p)
        # write input fp file
        hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag1)
        p = spirouImage.WriteImage(p, input_fp_file, loc['FPDATA'], hdict)
        # write output fp file
        hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag2)
        p = spirouImage.WriteImage(p, output_fp_file, loc['FPDATA2'], hdict)
        # write input fp file
        hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag3)
        p = spirouImage.WriteImage(p, input_hc_file, loc['HCDATA'], hdict)
        # write output fp file
        hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag4)
        p = spirouImage.WriteImage(p, output_hc_file, loc['HCDATA2'], hdict)
        # write overlap file
        hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag5)
        p = spirouImage.WriteImage(p, overlap_file, loc['ORDER_OVERLAP'],
                                   hdict)

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
