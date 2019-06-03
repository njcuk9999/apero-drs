#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

obj_mk_tell_Template.py NIGHT_NAME FILES

REFFILE = FILES[0] This is the file used to get the object name and date from
the header (used for getting/setting telluric/calibration database info
(saved into telluDB under "TELL_TEMP
" keys)

Created on 2018-07-13 05:16
@author: ncook
Version 0.0.1
"""
from __future__ import division
import numpy as np
from astropy import constants
import os
import warnings

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouDB
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup
from SpirouDRS import spirouTelluric
from SpirouDRS.spirouCore import spirouMath

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'obj_mk_obj_template.py'
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
# get speed of light
# noinspection PyUnresolvedReferences
CONSTANT_C = constants.c.value


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
    # load up first file
    # ----------------------------------------------------------------------
    # construct loc parameter dictionary for storing data
    loc = ParamDict()
    # read first file and assign values
    rdata = spirouImage.ReadImage(p, p['FITSFILENAME'])
    loc['DATA'], loc['DATAHDR'] = rdata[:2]

    # Get object name and airmass
    loc['OBJNAME'] = spirouImage.GetObjName(p, loc['DATAHDR'])
    loc.set_source('OBJNAME', main_name)
    loc['AIRMASS'] = spirouImage.GetAirmass(p, loc['DATAHDR'])
    # set source
    source = main_name + '+ spirouImage.ReadParams()'
    loc.set_sources(['OBJNAME', 'AIRMASS'], source)

    # ----------------------------------------------------------------------
    # Get and Normalise the blaze
    # ----------------------------------------------------------------------
    p, loc = spirouTelluric.GetNormalizedBlaze(p, loc, loc['DATAHDR'])

    # ----------------------------------------------------------------------
    # Get database files
    # ----------------------------------------------------------------------
    # get current telluric maps from telluDB
    tellu_db_data = spirouDB.GetDatabaseTellObj(p, required=False)
    tellu_db_files, tellu_db_names = tellu_db_data[0], tellu_db_data[1]

    # sort files by name
    # sortmask = spirouImage.SortByName(tellu_db_files)
    # tellu_db_files = np.array(tellu_db_files)[sortmask]
    # tellu_db_names = np.array(tellu_db_names)[sortmask]

    # filter by object name (only keep OBJNAME objects) and only keep
    #   unique filenames
    tell_files, tell_names = [], []
    for it in range(len(tellu_db_files)):
        # check that objname is correct
        cond1 = loc['OBJNAME'] in tellu_db_names[it]
        # check that filename is not already used
        cond2 = tellu_db_files[it] not in tell_files
        # append to file list if criteria correct
        if cond1 and cond2:
            tell_files.append(tellu_db_files[it])
            tell_names.append(tellu_db_names[it])

    # log if we have no files
    if len(tell_files) == 0:
        wmsg = 'No "TELL_OBJ" files found for object ="{0}" skipping'
        WLOG(p, 'warning', wmsg.format(loc['OBJNAME']))
        # End Message
        wmsg = 'Recipe {0} has been successfully completed'
        WLOG(p, 'info', wmsg.format(p['PROGRAM']))
        # return a copy of locally defined variables in the memory
        return dict(locals())
    else:
        # log how many found
        wmsg = 'N={0} "TELL_OBJ" files found for object ="{1}"'
        WLOG(p, 'info', wmsg.format(len(tell_files), loc['OBJNAME']))

    # ----------------------------------------------------------------------
    # Set up storage for cubes (NaN arrays)
    # ----------------------------------------------------------------------
    # set up flat size
    dims = [loc['DATA'].shape[0], loc['DATA'].shape[1], len(tell_files)]
    flatsize = np.product(dims)
    # create NaN filled storage
    big_cube = np.repeat([np.nan], flatsize).reshape(*dims)
    big_cube0 = np.repeat([np.nan], flatsize).reshape(*dims)

    # Force A and B to AB solution
    if p['FIBER'] in ['A', 'B']:
        wave_fiber = 'AB'
    else:
        wave_fiber = p['FIBER']
        # get master wave map
        loc['MASTERWAVEFILE'] = spirouDB.GetDatabaseMasterWave(p)
    # read master wave map
    mout = spirouImage.GetWaveSolution(p, filename=loc['MASTERWAVEFILE'],
                                       return_wavemap=True, quiet=True,
                                       fiber=wave_fiber)
    loc['MASTERWAVEPARAMS'], loc['MASTERWAVE'], loc['WSOURCE'] = mout
    keys = ['MASTERWAVEPARAMS', 'MASTERWAVE', 'MASTERWAVEFILE', 'WSOURCE']
    loc.set_sources(keys, main_name)

    # ----------------------------------------------------------------------
    # Compile a median SNR for rejection of bad files
    # ----------------------------------------------------------------------
    snr_all = []
    # choose snr to check
    snr_order = p['QC_FIT_TELLU_SNR_ORDER']
    # loop through files
    for it, filename in enumerate(tell_files):
        header = spirouImage.ReadHeader(p, filename)
        # get the SNR from header
        nbo = spirouImage.ReadParam(p, header, 'KW_WAVE_ORD_N', dtype=int,
                                    return_value=True)
        snr = spirouImage.Read1Dkey(p, header, p['kw_E2DS_SNR'][0], nbo)
        # append snr_all
        snr_all.append(snr[snr_order])

    # work our bad snr (less than half the median SNR)
    snr_thres = np.nanmedian(snr_all) / 2.0
    bad_snr_objects = np.where(snr_all < snr_thres)[0]

    # ----------------------------------------------------------------------
    # Loop through input files
    # ----------------------------------------------------------------------
    # empty lists for storage
    loc['BASE_ROWNUM'], loc['BASE_FILELIST'] = [], []
    loc['BASE_OBJNAME'], loc['BASE_OBJECT'] = [], []
    loc['BASE_BERVLIST'], loc['BASE_WAVELIST'] = [], []
    loc['BASE_SNRLIST_{0}'.format(snr_order)] = []
    loc['BASE_DATELIST'], loc['BASE_VERSION'] = [], []
    loc['BASE_DARKFILE'], loc['BASE_BADFILE'] = [], []
    loc['BASE_LOCOFILE'], loc['BASE_BLAZFILE'] = [], []
    loc['BASE_FLATFILE'], loc['BASE_SHAPEFILE'] = [], []

    # loop through files
    for it, filename in enumerate(tell_files):
        # get base filenmae
        basefilename = os.path.basename(filename)
        # ------------------------------------------------------------------
        # skip if in bad snr objects
        if it in bad_snr_objects:
            wargs = [it + 1, len(tell_files), snr_all[it], snr_thres]
            wmsg1 = ('Skipping file {0} of {1} due to bad SNR ({2:.3f} < '
                     '{3:.3f})'.format(*wargs))
            wmsg2 = '\tFile = {0}'.format(basefilename)
            WLOG(p, 'warning', [wmsg1, wmsg2])
            continue
        # ------------------------------------------------------------------
        # append basename to file list
        loc['BASE_FILELIST'].append(basefilename)
        # ------------------------------------------------------------------
        # create image for storage
        image = np.repeat([np.nan], np.product(loc['DATA'].shape))
        image = image.reshape(loc['DATA'].shape)
        # ------------------------------------------------------------------
        # Load the data for this file
        tdata0, thdr, _, _ = spirouImage.ReadImage(p, filename)
        nbo, npix = tdata0.shape
        # Correct for the blaze
        tdata = tdata0 / loc['NBLAZE']

        # get berv and add to list
        if p['KW_BERV'][0] in thdr:
            loc['BASE_BERVLIST'].append('{0}'.format(thdr[p['KW_BERV'][0]]))
        else:
            loc['BASE_BERVLIST'].append('UNKNOWN')

        # ------------------------------------------------------------------
        # Get parameters from header
        snr = snr_all[it]
        dateobs = spirouImage.ReadParam(p, thdr, 'KW_DATE_OBS', dtype=str,
                                        return_value=True)
        utcobs = spirouImage.ReadParam(p, thdr, 'KW_UTC_OBS', dtype=str,
                                       return_value=True)
        tobjname = spirouImage.ReadParam(p, thdr, 'KW_OBJNAME', dtype=str,
                                         return_value=True)
        tobject = spirouImage.ReadParam(p, thdr, 'KW_OBJECT', dtype=str,
                                        return_value=True)
        tversion = spirouImage.ReadParam(p, thdr, 'KW_version', dtype=str,
                                         return_value=True)
        tdarkfile = spirouImage.ReadParam(p, thdr, 'KW_CDBDARK', dtype=str,
                                          return_value=True)
        tbadfile = spirouImage.ReadParam(p, thdr, 'KW_CDBBAD', dtype=str,
                                          return_value=True)
        tlocofile = spirouImage.ReadParam(p, thdr, 'KW_CDBLOCO', dtype=str,
                                          return_value=True)
        tblazfile = spirouImage.ReadParam(p, thdr, 'KW_CDBBLAZE', dtype=str,
                                          return_value=True)
        tflatfile = spirouImage.ReadParam(p, thdr, 'KW_CDBFLAT', dtype=str,
                                          return_value=True)
        tshapfile = spirouImage.ReadParam(p, thdr, 'KW_CDBSHAPE', dtype=str,
                                          return_value=True)
        # append to lists
        loc['BASE_ROWNUM'].append(it)
        loc['BASE_SNRLIST_{0}'.format(snr_order)].append(snr_all[it])
        loc['BASE_DATELIST'].append('{0}_{1}'.format(dateobs, utcobs))
        loc['BASE_OBJNAME'].append(tobjname)
        loc['BASE_OBJECT'].append(tobject)
        loc['BASE_VERSION'].append(tversion)
        loc['BASE_DARKFILE'].append(tdarkfile)
        loc['BASE_BADFILE'].append(tbadfile)
        loc['BASE_LOCOFILE'].append(tlocofile)
        loc['BASE_BLAZFILE'].append(tblazfile)
        loc['BASE_FLATFILE'].append(tflatfile)
        loc['BASE_SHAPEFILE'].append(tshapfile)

        # ------------------------------------------------------------------
        # Get the wave solution for this file
        # ------------------------------------------------------------------
        # Force A and B to AB solution
        if p['FIBER'] in ['A', 'B']:
            wave_fiber = 'AB'
        else:
            wave_fiber = p['FIBER']
        # need to reload calibDB
        # as we have custom arguments need to load the calibration database
        calib_db = dict(p['CALIBDB'])
        del p['CALIBDB']
        p = spirouStartup.LoadCalibDB(p, header=thdr)
        # get wave solution
        wout = spirouImage.GetWaveSolution(p, image=tdata, hdr=thdr,
                                           return_wavemap=True,
                                           fiber=wave_fiber,
                                           return_filename=True)
        _, loc['WAVE'], loc['WAVEFILE'], _ = wout
        loc.set_sources(['WAVE', 'WAVEFILE'], main_name)

        # add wave to wave list
        loc['BASE_WAVELIST'].append(loc['WAVEFILE'])

        # readd original calibDB to p
        p['CALIBDB'] = dict(calib_db)

        # ------------------------------------------------------------------
        # Get the Barycentric correction from header
        dv, _, _ = spirouTelluric.GetBERV(p, thdr)
        # ------------------------------------------------------------------
        # log stats
        wmsg = 'Processing file {0} of {1} file={2} dv={3}'
        wargs = [it + 1, len(tell_files), basefilename, dv]
        WLOG(p, 'info', wmsg.format(*wargs))
        # ------------------------------------------------------------------
        # shift to correct berv
        dvshift = spirouMath.relativistic_waveshift(dv, units='km/s')

        image = spirouTelluric.Wave2Wave(p, tdata, loc['WAVE'] * dvshift,
                                         loc['MASTERWAVE'])
        # ------------------------------------------------------------------
        # loop around orders
        for order_num in range(loc['DATA'].shape[0]):
            # normalise the tdata
            tdata[order_num, :] /= np.nanmedian(tdata[order_num, :])
            image[order_num, :] /= np.nanmedian(image[order_num, :])
        # ------------------------------------------------------------------
        # add to cube storage
        big_cube[:, :, it] = image
        big_cube0[:, :, it] = tdata

    # ----------------------------------------------------------------------
    # log if we have no files
    if len(loc['BASE_FILELIST']) == 0:
        wmsg = 'No good files found for object ="{0}" skipping'
        WLOG(p, 'warning', wmsg.format(loc['OBJNAME']))
        # End Message
        wmsg = 'Recipe {0} has been successfully completed'
        WLOG(p, 'info', wmsg.format(p['PROGRAM']))
        # return a copy of locally defined variables in the memory
        return dict(locals())

    # ----------------------------------------------------------------------
    # make median image
    with warnings.catch_warnings(record=True) as _:
        big_cube_med = np.nanmedian(big_cube, axis=2)

    # ----------------------------------------------------------------------
    # Quality control
    # ----------------------------------------------------------------------
    # set passed variable and fail message list
    passed, fail_msg = True, []
    qc_values, qc_names, qc_logic, qc_pass = [], [], [], []
    # TODO: Needs doing
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

    # ----------------------------------------------------------------------
    # Write Cube median (the template) to file
    # ----------------------------------------------------------------------
    # get raw file name
    raw_in_file = os.path.basename(p['FITSFILENAME'])
    # construct filename
    outfile, tag = spirouConfig.Constants.OBJTELLU_TEMPLATE_FILE(p, loc)
    outfilename = os.path.basename(outfile)

    # hdict is first file keys
    hdict = spirouImage.CopyOriginalKeys(loc['DATAHDR'])
    # add version number
    hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_DATE'], value=p['DRS_DATE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DATE_NOW'], value=p['DATE_NOW'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_PID'], value=p['PID'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag)
    # set the input files
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBBLAZE'], value=p['BLAZFILE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBWAVE'],
                               value=loc['MASTERWAVEFILE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_WAVESOURCE'],
                               value=loc['WSOURCE'])
    hdict = spirouImage.AddKey1DList(p, hdict, p['KW_INFILE1'], dim1name='file',
                                     values=p['ARG_FILE_NAMES'])
    # add qc parameters
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_QC'], value=p['QC'])
    hdict = spirouImage.AddQCKeys(p, hdict, qc_params)
    # add wave solution coefficients
    hdict = spirouImage.AddKey2DList(p, hdict, p['KW_WAVE_PARAM'],
                                     values=loc['MASTERWAVEPARAMS'])
    # write to file
    p = spirouImage.WriteImage(p, outfile, big_cube_med, hdict)

    # ----------------------------------------------------------------------
    # Update the telluric database with the template
    # ----------------------------------------------------------------------
    spirouDB.UpdateDatabaseObjTemp(p, outfilename, loc['OBJNAME'],
                                   loc['DATAHDR'])
    # put file in telluDB
    spirouDB.PutTelluFile(p, outfile)

    # ----------------------------------------------------------------------
    # Save cubes to file
    # ----------------------------------------------------------------------
    # make big cube table
    big_table = spirouTelluric.ConstructBigTable(p, loc)
    # construct file names
    outfile1, tag1 = spirouConfig.Constants.OBJTELLU_TEMPLATE_CUBE_FILE1(p, loc)
    outfile2, tag2 = spirouConfig.Constants.OBJTELLU_TEMPLATE_CUBE_FILE2(p, loc)
    # log big cube 1
    wmsg1 = 'Saving bigcube to file {0}'.format(os.path.basename(outfile1))
    # save big cube 1
    hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag1)
    big_cube_s = np.swapaxes(big_cube, 1, 2)
    p = spirouImage.WriteImageTable(p, outfile1, image=big_cube_s,
                                    table=big_table, hdict=hdict)
    # log big cube 0
    wmsg = 'Saving bigcube0 to file {0}'.format(os.path.basename(outfile2))
    # save big cube 0
    hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag2)
    big_cube_s0 = np.swapaxes(big_cube0, 1, 2)
    p = spirouImage.WriteImageTable(p, outfile2, image=big_cube_s0,
                                    table=big_table, hdict=hdict)

    # # mega plot
    # nfiles = big_cube_s0.shape[1]
    # ncols = int(np.ceil(np.sqrt(nfiles)))
    # nrows = int(np.ceil(nfiles/ncols))
    # fig, frames = plt.subplots(ncols=ncols, nrows=nrows)
    # for it in range(big_cube_s0.shape[1]):
    #     jt, kt = it // ncols, it % ncols
    #     frame = frames[jt][kt]
    #     frame.imshow(big_cube_s0[:, it, :], origin='lower')
    #     frame.set(xlim=(2030, 2060))

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
