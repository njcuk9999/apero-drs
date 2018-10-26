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
from scipy.interpolate import InterpolatedUnivariateSpline as IUVSpline

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
    loc['DATA'], loc['DATAHDR'], loc['DATACDR'] = rdata[:3]

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
    tellu_db_files = spirouImage.SortByName(tellu_db_files)

    # filter by object name (only keep OBJNAME objects) and only keep
    #   unique filenames
    tell_files = []
    for it in range(len(tellu_db_files)):
        # check that objname is correct
        cond1 = loc['OBJNAME'] in tellu_db_names[it]
        # check that filename is not already used
        cond2 = tellu_db_files[it] not in tell_files
        # append to file list if criteria correct
        if cond1 and cond2:
            tell_files.append(tellu_db_files[it])

    # log if we have no files
    if len(tell_files) == 0:
        wmsg = 'No "TELL_OBJ" files found for object ="{0}" skipping'
        WLOG('warning', p['LOG_OPT'], wmsg.format(loc['OBJNAME']))
        # End Message
        wmsg = 'Recipe {0} has been successfully completed'
        WLOG('info', p['LOG_OPT'], wmsg.format(p['PROGRAM']))
        # return a copy of locally defined variables in the memory
        return dict(locals())
    else:
        # log how many found
        wmsg = 'N={0} "TELL_OBJ" files found for object ="{1}"'
        WLOG('', p['LOG_OPT'], wmsg.format(len(tell_files), loc['OBJNAME']))

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
    loc['MASTERWAVEPARAMS'], loc['MASTERWAVE'] = mout
    keys = ['MASTERWAVEPARAMS', 'MASTERWAVE', 'MASTERWAVEFILE']
    loc.set_sources(keys, main_name)

    # ----------------------------------------------------------------------
    # Loop through input files
    # ----------------------------------------------------------------------
    base_filelist, berv_list = [], []
    # loop through files
    for it, filename in enumerate(tell_files):
        # get base filenmae
        basefilename = os.path.basename(filename)
        # append basename to file list
        base_filelist.append(basefilename)
        # ------------------------------------------------------------------
        # create image for storage
        image = np.repeat([np.nan], np.product(loc['DATA'].shape))
        image = image.reshape(loc['DATA'].shape)
        # ------------------------------------------------------------------
        # Load the data for this file
        tdata0, thdr, tcdr, _, _ = spirouImage.ReadImage(p, filename)
        # Correct for the blaze
        tdata = tdata0 / loc['NBLAZE']

        # get berv and add to list
        if p['KW_BERV'][0] in thdr:
            berv_list.append('{0}'.format(thdr[p['KW_BERV'][0]]))
        else:
            berv_list.append('UNKNOWN')

        # ------------------------------------------------------------------
        # Get the wave solution for this file
        # ------------------------------------------------------------------
        # Force A and B to AB solution
        if p['FIBER'] in ['A', 'B']:
            wave_fiber = 'AB'
        else:
            wave_fiber = p['FIBER']
        # get wave solution
        wout = spirouImage.GetWaveSolution(p, image=tdata, hdr=thdr,
                                           return_wavemap=True,
                                           fiber=wave_fiber,
                                           return_filename=True)
        _, loc['WAVE'], loc['WAVEFILE'] = wout
        loc.set_sources(['WAVE', 'WAVEFILE'], main_name)
        # ------------------------------------------------------------------
        # Get the Barycentric correction from header
        dv, _, _ = spirouTelluric.GetBERV(p, thdr)
        # ------------------------------------------------------------------
        # log stats
        wmsg = 'Processing file {0} of {1} file={2} dv={3}'
        wargs = [it + 1, len(tell_files), basefilename, dv]
        WLOG('', p['LOG_OPT'], wmsg.format(*wargs))
        # ------------------------------------------------------------------
        # shift to correct berv
        dvshift = spirouMath.relativistic_waveshift(dv, units='km/s')

        image = spirouTelluric.Wave2Wave(tdata, loc['WAVE'] * dvshift,
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
    # make median image
    with warnings.catch_warnings(record=True) as _:
        big_cube_med = np.nanmedian(big_cube, axis=2)

    # ----------------------------------------------------------------------
    # Write Cube median (the template) to file
    # ----------------------------------------------------------------------
    # get raw file name
    raw_in_file = os.path.basename(p['FITSFILENAME'])
    # construct filename
    outfile, tag = spirouConfig.Constants.OBJTELLU_TEMPLATE_FILE(p, loc)
    outfilename = os.path.basename(outfile)

    # hdict is first file keys
    hdict = spirouImage.CopyOriginalKeys(loc['DATAHDR'], loc['DATACDR'])
    # add version number
    hdict = spirouImage.AddKey(hdict, p['KW_VERSION'])
    hdict = spirouImage.AddKey(hdict, p['KW_OUTPUT'], value=tag)
    # set the input files
    hdict = spirouImage.AddKey(hdict, p['KW_BLAZFILE'], value=p['BLAZFILE'])
    hdict = spirouImage.AddKey(hdict, p['kw_INFILE'], value=raw_in_file)
    hdict = spirouImage.AddKey(hdict, p['KW_WAVEFILE'],
                               value=loc['MASTERWAVEFILE'])
    # add file list to header
    hdict = spirouImage.AddKey1DList(hdict, p['KW_OBJFILELIST'],
                                     values=base_filelist)
    hdict = spirouImage.AddKey1DList(hdict, p['KW_OBJBERVLIST'],
                                     values=berv_list)
    # add wave solution coefficients
    hdict = spirouImage.AddKey2DList(hdict, p['KW_WAVE_PARAM'],
                                     values=loc['MASTERWAVEPARAMS'])
    # write to file
    p = spirouImage.WriteImage(p, outfile, big_cube_med, hdict)

    # ----------------------------------------------------------------------
    # Update the telluric database with the template
    # ----------------------------------------------------------------------
    objname = loc['OBJNAME']
    spirouDB.UpdateDatabaseObjTemp(p, outfilename, objname, loc['DATAHDR'])
    # put file in telluDB
    spirouDB.PutTelluFile(p, outfile)

    # ----------------------------------------------------------------------
    # Save cubes to file
    # ----------------------------------------------------------------------
    # construct file names
    outfile1, tag1 = spirouConfig.Constants.OBJTELLU_TEMPLATE_CUBE_FILE1(p, loc)
    outfile2, tag2 = spirouConfig.Constants.OBJTELLU_TEMPLATE_CUBE_FILE2(p, loc)
    # log big cube 1
    wmsg1 = 'Saving bigcube to file {0}'.format(os.path.basename(outfile1))
    # save big cube 1
    hdict = spirouImage.AddKey(hdict, p['KW_OUTPUT'], value=tag1)
    big_cube_s = np.swapaxes(big_cube, 1, 2)
    p = spirouImage.WriteImage(p, outfile1, big_cube_s, hdict)
    # log big cube 0
    wmsg = 'Saving bigcube0 to file {0}'.format(os.path.basename(outfile2))
    # save big cube 0
    hdict = spirouImage.AddKey(hdict, p['KW_OUTPUT'], value=tag2)
    big_cube_s0 = np.swapaxes(big_cube0, 1, 2)
    p = spirouImage.WriteImage(p, outfile2, big_cube_s0, hdict)


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
