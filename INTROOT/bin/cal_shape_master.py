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
import warnings

from SpirouDRS import spirouDB
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouLOCOR
from SpirouDRS import spirouStartup
from SpirouDRS import spirouTHORCA
from SpirouDRS import spirouEXTOR


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_shape_master.py'
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
def main(night_name=None, hcfile=None, fpfile=None):
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
    if hcfile is None or fpfile is None:
        names, types = ['hcfile', 'fpfile'], [str, str]
        customargs = spirouStartup.GetCustomFromRuntime(p, [0, 1], types, names)
    else:
        customargs = dict(hcfile=hcfile, fpfile=fpfile)

    # get parameters from configuration files and run time arguments
    p = spirouStartup.LoadArguments(p, night_name, customargs=customargs,
                                    mainfitsfile='fpfile')

    # ----------------------------------------------------------------------
    # Construct reference filename and get fiber type
    # ----------------------------------------------------------------------
    p, hcfitsfilename = spirouStartup.SingleFileSetup(p, filename=p['HCFILE'])
    p, fpfitsfilename = spirouStartup.SingleFileSetup(p, filename=p['FPFILE'])
    # set fiber (it doesn't matter with the 2D image but we need this to get
    # the lamp type for FPFILES and HCFILES, AB == C
    p['FIBER'] = 'AB'
    p['FIB_TYP'] = [p['FIBER']]
    fsource = __NAME__ + '/main()'
    p.set_sources(['FIBER', 'FIB_TYP'], fsource)

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
    # read input fp and hc data
    fpdata, fphdr, _, _ = spirouImage.ReadImage(p, fpfitsfilename)
    hcdata, hchdr, _, _ = spirouImage.ReadImage(p, hcfitsfilename)

    # add data and hdr to loc
    loc = ParamDict()
    loc['HCDATA'], loc['HCHDR'] = hcdata, hchdr
    loc['FPDATA'], loc['FPHDR'] = fpdata, fphdr
    # set the source
    sources = ['HCDATA', 'HCHDR']
    loc.set_sources(sources, 'spirouImage.ReadImage()')
    sources = ['FPDATA', 'FPHDR']
    loc.set_sources(sources, 'spirouImage.ReadImage()')

    # ---------------------------------------------------------------------
    # fix for un-preprocessed files
    # ----------------------------------------------------------------------
    hcdata = spirouImage.FixNonPreProcess(p, hcdata)
    fpdata = spirouImage.FixNonPreProcess(p, fpdata)

    # ----------------------------------------------------------------------
    # Once we have checked the e2dsfile we can load calibDB
    # ----------------------------------------------------------------------
    # as we have custom arguments need to load the calibration database
    p = spirouStartup.LoadCalibDB(p)

    # add a force plot off
    p['PLOT_PER_ORDER'] = PLOT_PER_ORDER
    p.set_source('PLOT_PER_ORDER', __NAME__ + '.main()')

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
    # get FP_FP DPRTYPE
    p = spirouImage.ReadParam(p, fphdr, 'KW_DPRTYPE', 'DPRTYPE', dtype=str)


    # ----------------------------------------------------------------------
    # Correction of reference FP
    # ----------------------------------------------------------------------
    # set the number of frames
    p['NBFRAMES'] = 1
    p.set_source('NBFRAMES', __NAME__ + '.main()')
    # Correction of DARK
    p, fpdatac = spirouImage.CorrectForDark(p, fpdata, fphdr)
    # Resize hc data
    # rotate the image and convert from ADU/s to e-
    fpdata = spirouImage.ConvertToE(spirouImage.FlipImage(p, fpdatac), p=p)
    # resize image
    bkwargs = dict(xlow=p['IC_CCDX_LOW'], xhigh=p['IC_CCDX_HIGH'],
                   ylow=p['IC_CCDY_LOW'], yhigh=p['IC_CCDY_HIGH'],
                   getshape=False)
    fpdata1 = spirouImage.ResizeImage(p, fpdata, **bkwargs)
    # log change in data size
    WLOG(p, '',
         ('FPref Image format changed to {0}x{1}').format(*fpdata1.shape))
    # Correct for the BADPIX mask (set all bad pixels to zero)
    bargs = [p, fpdata1, hchdr]
    p, fpdata1 = spirouImage.CorrectForBadPix(*bargs)
    p, badpixmask = spirouImage.CorrectForBadPix(*bargs, return_map=True)
    # log progress
    WLOG(p, '', 'Cleaning FPref hot pixels')
    # correct hot pixels
    fpdata1 = spirouEXTOR.CleanHotpix(fpdata1, badpixmask)
    # add to loc
    loc['FPDATA1'] = fpdata1
    loc.set_source('FPDATA1', __NAME__ + '.main()')
    # Log the number of dead pixels
    # get the number of bad pixels
    with warnings.catch_warnings(record=True) as _:
        n_bad_pix = np.nansum(fpdata1 <= 0)
        n_bad_pix_frac = n_bad_pix * 100 / np.product(fpdata1.shape)
    # Log number
    wmsg = 'Nb FPref dead pixels = {0} / {1:.2f} %'
    WLOG(p, 'info', wmsg.format(int(n_bad_pix), n_bad_pix_frac))

    # ----------------------------------------------------------------------
    # Correction of HC
    # ----------------------------------------------------------------------
    # set the number of frames
    p['NBFRAMES'] = 1
    p.set_source('NBFRAMES', __NAME__ + '.main()')
    # Correction of DARK
    p, hcdatac = spirouImage.CorrectForDark(p, hcdata, hchdr)
    # Resize hc data
    # rotate the image and convert from ADU/s to e-
    hcdata = spirouImage.ConvertToE(spirouImage.FlipImage(p, hcdatac), p=p)
    # resize image
    bkwargs = dict(xlow=p['IC_CCDX_LOW'], xhigh=p['IC_CCDX_HIGH'],
                   ylow=p['IC_CCDY_LOW'], yhigh=p['IC_CCDY_HIGH'],
                   getshape=False)
    hcdata1 = spirouImage.ResizeImage(p, hcdata, **bkwargs)
    # log change in data size
    WLOG(p, '',
         ('HC Image format changed to {0}x{1}').format(*hcdata1.shape))
    # Correct for the BADPIX mask (set all bad pixels to zero)
    bargs = [p, hcdata1, hchdr]
    p, hcdata1 = spirouImage.CorrectForBadPix(*bargs)
    p, badpixmask = spirouImage.CorrectForBadPix(*bargs, return_map=True)
    # log progress
    WLOG(p, '', 'Cleaning HC hot pixels')
    # correct hot pixels
    fpdata1 = spirouEXTOR.CleanHotpix(hcdata1, badpixmask)
    # add to loc
    loc['HCDATA1'] = hcdata1
    loc.set_source('HCDATA1', __NAME__ + '.main()')
    # Log the number of dead pixels
    # get the number of bad pixels
    with warnings.catch_warnings(record=True) as _:
        n_bad_pix = np.nansum(hcdata1 <= 0)
        n_bad_pix_frac = n_bad_pix * 100 / np.product(hcdata1.shape)
    # Log number
    wmsg = 'Nb HC dead pixels = {0} / {1:.2f} %'
    WLOG(p, 'info', wmsg.format(int(n_bad_pix), n_bad_pix_frac))


    # -------------------------------------------------------------------------
    # get all FP_FP files
    # -------------------------------------------------------------------------
    fpfilenames = spirouImage.FindFiles(p, filetype=p['DPRTYPE'],
                          allowedtypes=p['ALLOWED_FP_TYPES'])
    # convert filenames to a numpy array
    fpfilenames = np.array(fpfilenames)
    # julian date to know which file we need to
    # process together
    fp_time = np.zeros(len(fpfilenames))
    basenames, fp_exp, fp_pp_version, nightnames = [], [], [], []
    # log progress
    WLOG(p, '', 'Reading all fp file headers')
    # looping through the file headers
    for it in range(len(fpfilenames)):
        # log progress
        wmsg = '\tReading file {0} / {1}'
        WLOG(p, 'info', wmsg.format(it + 1, len(fpfilenames)))
        # get fp filename
        fpfilename = fpfilenames[it]
        # get night name
        night_name = os.path.dirname(fpfilenames[it]).split(p['TMP_DIR'])[-1]
        # read data
        data_it, hdr_it, _, _ = spirouImage.ReadImage(p, fpfilename)
        # get header
        hdr = spirouImage.ReadHeader(p, filepath=fpfilenames[it])
        # add MJDATE to dark times
        fp_time[it] = float(hdr[p['KW_ACQTIME'][0]])
        # add other keys (for tabular output)
        basenames.append(os.path.basename(fpfilenames[it]))
        nightnames.append(night_name)
        fp_exp.append(float(hdr[p['KW_EXPTIME'][0]]))
        fp_pp_version.append(hdr[p['KW_PPVERSION'][0]])

    # -------------------------------------------------------------------------
    # match files by date
    # -------------------------------------------------------------------------
    # log progress
    wmsg = 'Matching FP files by observation time (+/- {0} hrs)'
    WLOG(p, '', wmsg.format(p['DARK_MASTER_MATCH_TIME']))
    # get the time threshold
    time_thres = p['FP_MASTER_MATCH_TIME']
    # get items grouped by time
    matched_id = spirouImage.GroupFilesByTime(p, fp_time, time_thres)

    # -------------------------------------------------------------------------
    # construct the master fp file (+ correct for dark/badpix)
    # -------------------------------------------------------------------------
    cargs = [fpdata1, fpfilenames, matched_id]
    fpcube, transforms = spirouImage.ConstructMasterFP(p, *cargs)
    # log process
    wmsg1 = 'Master FP construction complete.'
    wmsg2 = '\tAdding {0} group images to form FP master image'
    WLOG(p, 'info', [wmsg1, wmsg2.format(len(fpcube))])
    # sum the cube to make fp data
    fpdata1 = np.sum(fpcube, axis=0)
    # add to loc
    loc['FPDATA1'] = fpdata1
    loc.set_source('FPDATA1', __NAME__ + '.main()')

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
    loc = spirouImage.GetXShapeMap(p, loc)
    loc = spirouImage.GetYShapeMap(p, loc, fphdr)

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
    # Writing FP big table
    # ------------------------------------------------------------------
    # construct big fp table
    colnames = ['FILENAME', 'NIGHT', 'MJDATE', 'EXPTIME', 'PVERSION',
                'GROUPID', 'DXREF', 'DYREF', 'A', 'B', 'C', 'D']
    values = [basenames, nightnames, fp_time, fp_exp, fp_pp_version,
              matched_id, transforms[:, 0], transforms[:, 1],
              transforms[:, 2], transforms[:, 3], transforms[:, 4]]
    fptable = spirouImage.MakeTable(p, colnames, values)

    # ------------------------------------------------------------------
    # Writing DXMAP to file
    # ------------------------------------------------------------------
    # get the raw tilt file name
    raw_shape_file = os.path.basename(p['FITSFILENAME'])
    # construct file name and path
    shapexfits, tag = spirouConfig.Constants.SLIT_XSHAPE_FILE(p)
    shapexfitsname = os.path.basename(shapexfits)
    # Log that we are saving tilt file
    wmsg = 'Saving shape x information in file: {0}'
    WLOG(p, '', wmsg.format(shapexfitsname))
    # Copy keys from fits file
    hdict = spirouImage.CopyOriginalKeys(fphdr)
    # add version number
    hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_DATE'], value=p['DRS_DATE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DATE_NOW'], value=p['DATE_NOW'])
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
    p = spirouImage.WriteImageTable(p, shapexfits, image=loc['DXMAP'],
                                    table=fptable, hdict=hdict)

    # ------------------------------------------------------------------
    # Writing DYMAP to file
    # ------------------------------------------------------------------
    # get the raw tilt file name
    raw_shape_file = os.path.basename(p['FITSFILENAME'])
    # construct file name and path
    shapeyfits, tag = spirouConfig.Constants.SLIT_YSHAPE_FILE(p)
    shapeyfitsname = os.path.basename(shapeyfits)
    # Log that we are saving tilt file
    wmsg = 'Saving shape y information in file: {0}'
    WLOG(p, '', wmsg.format(shapeyfitsname))
    # Copy keys from fits file
    hdict = spirouImage.CopyOriginalKeys(fphdr)
    # add version number
    hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_DATE'], value=p['DRS_DATE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DATE_NOW'], value=p['DATE_NOW'])
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
    p = spirouImage.WriteImageTable(p, shapeyfits, image=loc['DYMAP'],
                                    table=fptable, hdict=hdict)

    # ------------------------------------------------------------------
    # Writing Master FP to file
    # ------------------------------------------------------------------
    # get the raw tilt file name
    raw_shape_file = os.path.basename(p['FITSFILENAME'])
    # construct file name and path
    fpmasterfits, tag = spirouConfig.Constants.SLIT_MASTER_FP_FILE(p)
    fpmasterfitsname = os.path.basename(fpmasterfits)
    # Log that we are saving tilt file
    wmsg = 'Saving master FP file: {0}'
    WLOG(p, '', wmsg.format(fpmasterfitsname))
    # Copy keys from fits file
    hdict = spirouImage.CopyOriginalKeys(fphdr)
    # add version number
    hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_DATE'], value=p['DRS_DATE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DATE_NOW'], value=p['DATE_NOW'])
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
    p = spirouImage.WriteImageTable(p, fpmasterfits, image=fpdata1,
                                    table=fptable, hdict=hdict)

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
        # add shape x
        keydb = 'SHAPEX'
        # copy shape file to the calibDB folder
        spirouDB.PutCalibFile(p, shapexfits)
        # update the master calib DB file with new key
        spirouDB.UpdateCalibMaster(p, keydb, shapeyfitsname, fphdr)
        # add shape y
        keydb = 'SHAPEY'
        # copy shape file to the calibDB folder
        spirouDB.PutCalibFile(p, shapeyfits)
        # update the master calib DB file with new key
        spirouDB.UpdateCalibMaster(p, keydb, shapeyfitsname, fphdr)
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
