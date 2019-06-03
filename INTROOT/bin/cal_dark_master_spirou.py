#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cal_DARK_spirou.py [night_directory] [fitsfilename]

Dark with short exposure time (~5min, to be defined during AT-4) to check
if read-out noise, dark current and hot pixel mask are consistent with the
ones obtained during technical night. Quality control is done automatically
by the pipeline

Created on 2017-10-11 at 10:45

@author: cook

Last modified: 2017-12-11 at 15:08

Up-to-date with cal_DARK_spirou AT-4 V47
"""
from __future__ import division
import numpy as np
import os
import warnings

from SpirouDRS import spirouDB
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_dark_master_spirou.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt


# =============================================================================
# Define functions
# =============================================================================
def main(filetype='DARK_DARK'):
    """
    cal_DARK_spirou.py main function, if night_name and files are None uses
    arguments from run time i.e.:
        cal_DARK_spirou.py [night_directory] [fitsfilename]

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
    # set up function name
    main_name = __NAME__ + '.main()'
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)

    # now get custom arguments
    pos, fmt = [0], [str]
    names, call = ['filetype'], [filetype]
    customargs = spirouStartup.GetCustomFromRuntime(p, pos, fmt, names,
                                                    calls=call,
                                                    require_night_name=False)
    p = spirouStartup.LoadArguments(p, None, customargs=customargs,
                                    mainfitsdir='tmp',
                                    require_night_name=False)
    # set the DRS type (for file indexing)
    p['DRS_TYPE'] = 'RAW'
    p.set_source('DRS_TYPE', __NAME__ + '.main()')
    # -------------------------------------------------------------------------
    # find all "filetype" objects
    filenames = spirouImage.FindFiles(p, filetype=p['FILETYPE'],
                                      allowedtypes=p['ALLOWED_DARK_TYPES'])
    # convert filenames to a numpy array
    filenames = np.array(filenames)
    # -------------------------------------------------------------------------
    # julian date to know which file we need to
    # process together
    dark_time = np.zeros(len(filenames))
    dark_exp, dark_pp_version, dark_wt_temp = [], [], []
    basenames, nightnames, dark_cass_temp, dark_humidity = [], [], [], []
    # log progress
    WLOG(p, '', 'Reading all dark file headers')
    # looping through the file headers
    for it in range(len(filenames)):
        # get night name
        night_name = os.path.dirname(filenames[it]).split(p['TMP_DIR'])[-1]
        # get header
        hdr = spirouImage.ReadHeader(p, filepath=filenames[it])
        # add MJDATE to dark times
        dark_time[it] = float(hdr[p['KW_ACQTIME'][0]])
        # add other keys (for tabular output)
        basenames.append(os.path.basename(filenames[it]))
        nightnames.append(night_name)
        dark_exp.append(float(hdr[p['KW_EXPTIME'][0]]))
        dark_pp_version.append(hdr[p['KW_PPVERSION'][0]])
        dark_wt_temp.append(float(hdr[p['KW_WEATHER_TOWER_TEMP'][0]]))
        dark_cass_temp.append(float(hdr[p['KW_CASS_TEMP'][0]]))
        dark_humidity.append(float(hdr[p['KW_HUMIDITY'][0]]))

    # -------------------------------------------------------------------------
    # match files by date
    # -------------------------------------------------------------------------
    # log progress
    wmsg = 'Matching dark files by observation time (+/- {0} hrs)'
    WLOG(p, '', wmsg.format(p['DARK_MASTER_MATCH_TIME']))
    # get the time threshold
    time_thres = p['DARK_MASTER_MATCH_TIME']
    # get items grouped by time
    matched_id = spirouImage.GroupFilesByTime(p, dark_time, time_thres)
    # -------------------------------------------------------------------------
    # get the most recent position
    lastpos = np.argmax(dark_time)
    # load up the most recent dark
    rout = spirouImage.ReadImage(p, filenames[lastpos], log=False)
    data_ref, hdr_ref, nx, ny = rout
    # set the night name and update the reduced directory
    p['ARG_NIGHT_NAME'] = nightnames[lastpos]
    p.set_source('ARG_NIGHT_NAME', __NAME__ + '.main()')
    p['REDUCED_DIR'] = spirouConfig.Constants.REDUCED_DIR(p)
    p.set_source('REDUCED_DIR', __NAME__ + '.main()')

    # -------------------------------------------------------------------------
    # Read individual files and sum groups
    # -------------------------------------------------------------------------
    # log process
    WLOG(p, '', 'Reading Dark files and combining groups')
    # Find all unique groups
    u_groups = np.unique(matched_id)
    # currently number of bins == number of groups
    num_bins = len(u_groups)
    # storage of dark cube
    dark_cube = np.zeros([num_bins, ny, nx])
    bin_cube = np.zeros(num_bins)
    # loop through groups
    for g_it, group_num in enumerate(u_groups):
        # log progress
        WLOG(p, '', '\tGroup {0} of {1}'.format(g_it + 1, len(u_groups)))
        # find all files for this group
        dark_ids = filenames[matched_id == group_num]
        # load this groups files into a cube
        cube = []
        for filename in dark_ids:
            # read data
            data_it, _, _, _ = spirouImage.ReadImage(p, filename, log=False)
            # add to cube
            cube.append(data_it)
        # median dark cube
        groupdark = np.nanmedian(cube, axis=0)
        # sum within each bin
        dark_cube[g_it % num_bins] += groupdark
        # record the number of cubes that are going into this bin
        bin_cube[g_it % num_bins] += 1

    # need to normalize if we have more than 1 cube per bin
    for bin_it in range(num_bins):
        dark_cube[bin_it] /= bin_cube[bin_it]
    # -------------------------------------------------------------------------
    # we perform a median filter over a +/- "med_size" pixel box
    # -------------------------------------------------------------------------
    # log process
    WLOG(p, '', 'Performing median filter for {0} bins'.format(num_bins))
    # get med_size from p
    med_size = p['DARK_MASTER_MED_SIZE']
    # storage of output dark cube
    dark_cube1 = np.zeros([num_bins, ny, nx])
    # loop around the bins
    for bin_it in range(num_bins):
        # get the dark for this bin
        bindark = dark_cube[bin_it]
        # performing a median filter of the image with [-med_size, med_size]
        #     box in x and 1 pixel wide in y. Skips the pixel considered,
        #     so this is equivalent of a 2*med_size boxcar
        tmp = []
        for jt in range(-med_size, med_size + 1):
            if jt != 0:
                tmp.append(np.roll(bindark, [0, jt]))
        # low frequency image
        lf_dark = np.nanmedian(tmp, axis=0)
        # high frequency image
        dark_cube1[bin_it] = bindark - lf_dark
    # -------------------------------------------------------------------------
    # median the dark cube to create the master dark
    master_dark = np.nanmedian(dark_cube, axis=0)
    # ----------------------------------------------------------------------
    # Quality control
    # ----------------------------------------------------------------------
    # set passed variable and fail message list
    passed, fail_msg = True, []
    qc_values, qc_names, qc_logic, qc_pass = [], [], [], []
    # ----------------------------------------------------------------------
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
    # Save master dark to file
    # ----------------------------------------------------------------------
    # set reference filename
    reffile = filenames[lastpos]
    # construct folder and filename
    darkmasterfits, tag = spirouConfig.Constants.DARK_FILE_MASTER(p, reffile)
    darkmasterfitsname = os.path.basename(darkmasterfits)
    # log writing of file
    WLOG(p, '', 'Saving master dark to {0}'.format(darkmasterfitsname))
    # construct big dark table
    colnames = ['FILENAME', 'NIGHT', 'MJDATE', 'EXPTIME', 'WEATHER_TEMP',
                'CASS_TEMP', 'RELHUMID', 'PVERSION', 'GROUPID']
    values = [basenames, nightnames, dark_time, dark_exp, dark_wt_temp,
              dark_cass_temp, dark_humidity, dark_pp_version, matched_id]
    darktable = spirouImage.MakeTable(p, colnames, values)
    # add keys from original header file
    hdict = spirouImage.CopyOriginalKeys(hdr_ref)
    # define new keys to add
    hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_DATE'], value=p['DRS_DATE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DATE_NOW'], value=p['DATE_NOW'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_PID'], value=p['PID'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag)
    # add qc parameters
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_QC'], value=p['QC'])
    hdict = spirouImage.AddQCKeys(p, hdict, qc_params)
    # write master dark + dark table to file
    p = spirouImage.WriteImageTable(p, darkmasterfits, image=master_dark,
                                    table=darktable, hdict=hdict)
    # ----------------------------------------------------------------------
    # Move to calibDB and update calibDB
    # ----------------------------------------------------------------------
    if p['QC']:
        # set dark master key
        keydb = 'DARKM'
        # copy dark fits file to the calibDB folder
        spirouDB.PutCalibFile(p, darkmasterfits)
        # update the master calib DB file with new key
        spirouDB.UpdateCalibMaster(p, keydb, darkmasterfitsname, hdr_ref)
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
