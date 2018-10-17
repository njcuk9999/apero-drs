#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-10-17 at 10:56

@author: cook
"""
from __future__ import division
import numpy as np
import os
from astropy.table import Table
import itertools

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup


import cal_BADPIX_spirou
import cal_CCF_E2DS_spirou
import cal_DARK_spirou
import cal_DRIFT_E2DS_spirou
import cal_DRIFTPEAK_E2DS_spirou
import cal_exposure_meter
import cal_wave_mapper
import cal_extract_RAW_spirou
import cal_FF_RAW_spirou
# import cal_HC_E2DS_spirou
import cal_HC_E2DS_EA_spirou
import cal_loc_RAW_spirou
import cal_SLIT_spirou
import cal_SHAPE_spirou
# import cal_WAVE_E2DS_spirou
import cal_WAVE_E2DS_EA_spirou
# import cal_WAVE_NEW_E2DS_spirou
import cal_preprocess_spirou
import off_listing_RAW_spirou
import off_listing_REDUC_spirou
import obj_mk_tellu
import obj_fit_tellu
import obj_mk_obj_template
import visu_RAW_spirou
import visu_E2DS_spirou
import pol_spirou

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'extract_trigger.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# Get param dictionary
ParamDict = spirouConfig.ParamDict
# skip found files
SKIP_DONE = True
# allowed files
RAW_CODES = ['a.fits', 'c.fits', 'd.fits', 'f.fits', 'o.fits']
# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
def recipe_lookup(key):
    lookup = dict()
    lookup['cal_preprocess_spirou'] = cal_preprocess_spirou
    lookup['cal_BAXPIX_spirou'] = cal_BADPIX_spirou.main
    lookup['cal_DARK_spirou'] = cal_DARK_spirou.main
    lookup['cal_loc_RAW_spirou'] = cal_loc_RAW_spirou.main
    lookup['cal_SLIT_spirou'] = cal_SLIT_spirou.main
    lookup['cal_SHAPE_spirou'] = cal_SHAPE_spirou.main
    lookup['cal_FF_RAW_spirou'] = cal_FF_RAW_spirou.main
    lookup['cal_extract_RAW_spirou'] = cal_extract_RAW_spirou.main
    return lookup[key]


def find_all_raw_files(p):
    # define path to walk around
    if p['ARG_NIGHT_NAME'] == '':
        path = p['DRS_DATA_RAW']
    else:
        path = os.path.join(p['DRS_DATA_RAW'], p['ARG_NIGHT_NAME'])
    # storage for raw file paths
    raw_files = []
    # walk around all sub-directories
    for root, dirs, filenames in os.walk(path):
        # loop around files
        for filename in filenames:
            abs_path = os.path.join(root, filename)
            for rawcode in RAW_CODES:
                if filename.endswith(rawcode):
                    raw_files.append(abs_path)
    # return raw files
    return raw_files


def skip_done_raw_files(p, filelist):
    # define the new expected extension
    ppext = p['PROCESSED_SUFFIX']
    # define path to tmp folder
    donepath = p['DRS_DATA_WORKING']
    # define path to raw folder
    rawpath = p['DRS_DATA_RAW']
    # storage
    newfilelist = []
    # loop around files
    for filename in filelist:
        # replace rawpath with donepath
        path = filename.replace(rawpath, donepath)
        # add the pp extension
        path = path.replace('.fits', ppext)
        # if does not exist add to newfile list
        if not os.path.exists(path):
            newfilelist.append(path)
    # return unfound files
    return newfilelist


def find_all_index_files(p):
    # define path to walk around
    path = p['ARG_FILE_DIR']
    # get index file name
    index_filename = spirouConfig.Constants.INDEX_OUTPUT_FILENAME()
    # storage for index file paths
    index_files = []
    # walk around all sub-directories
    for root, dirs, filenames in os.walk(path):
        # loop around files
        for filename in filenames:
            abs_path = os.path.join(root, filename)
            if filename == index_filename:
                index_files.append(abs_path)

    # return list of index_files
    return index_files


def get_night_name(path, filelist):
    night_names, filenames = [], []
    # loop around files
    for filename in filelist:
        # find common path
        commonpath = os.path.commonpath([path, filename])
        # find uncommonpath
        uncommonpath = filename.split(commonpath)[-1]
        # remove leading os.path.sep
        while uncommonpath.startswith(os.path.sep):
            uncommonpath = uncommonpath[1:]
        # get basename
        basename = os.path.basename(uncommonpath)
        # get nightname
        night_name = uncommonpath.split(basename)[0]
        # append to list
        night_names.append(night_name)
        filenames.append(basename)
    # return night names and filenames
    return night_names, filenames



# =============================================================================
# trigger functions
# =============================================================================
def trigger_preprocess(p, filelist):
    # define path to raw folder
    rawpath = p['DRS_DATA_RAW']
    # get night name
    night_names, filenames = get_night_name(rawpath, filelist)
    # pre-process files
    import cal_preprocess_spirou
    # loop around files
    lls = []
    for it in range(len(night_names)):
        # log progress
        wmsgs = [spirouStartup.spirouStartup.HEADER,
                 spirouStartup.spirouStartup.HEADER]
        wargs = [it + 1, len(night_names)]
        wmsgs.append(' TRIGGER PRE-PROCESS File {0} of {1}'.format(*wargs))
        wmsgs.append(spirouStartup.spirouStartup.HEADER)
        wmsgs.append(spirouStartup.spirouStartup.HEADER)
        WLOG('warning', p['LOG_OPT'], wmsgs)
        # run preprocess
        try:
            args = [night_names[it], filenames[it]]
            lls.append(cal_preprocess_spirou.main())
        except Exception as e:
            emsgs = ['There was an exception']
            emsgs.append('Exception message reads: {0}'.format(e))
            WLOG('warning', p['LOG_OPT'], emsgs)
            pp = ParamDict()
            pp['NIGHT_NAME'] = night_names[it]
            pp['FILENAME'] = filenames[it]
            pp['EMSGS'] = emsgs
            pp['Exception'] = e
            lls.append(dict(p=pp))

    # return local directories
    return lls


def trigger_main(p, loc, recipe):

    night_names = loc['INDEX_NIGHTNAME']
    index_files = loc['INDEX_FILES']
    # loop through index files
    lls = []
    for it, index_file in enumerate(index_files):
        # log progress
        wmsgs = [spirouStartup.spirouStartup.HEADER,
                 spirouStartup.spirouStartup.HEADER]
        wmsgs.append(' TRIGGER RECIPE: {0}'.format(recipe))
        wmsgs.append(spirouStartup.spirouStartup.HEADER)
        wmsgs.append(spirouStartup.spirouStartup.HEADER)
        # load index file
        index = Table.read(index_file)
        # get night_name
        night_name = night_names[it]
        # mask control file by recipe name
        cmask = np.array(p['CONTROL']['Recipe']) == recipe
        control = p['CONTROL'][cmask]
        file_args_expected = np.max(control['number'])

        # get valied files from index
        vmask = np.in1d(index['DPRTYPE'], control['dprtype'])
        vindex = index[vmask]

        # get the files in index that match the correct arguments
        args = dict()
        # loop around control
        for row in range(len(control)):
            # get parameters from control
            number = control['number'][row]
            dprtype = control['dprtype'][row]
            # construct a mask of files
            filemask = dprtype == vindex['DPRTYPE']
            # check that we have some files
            if np.sum(filemask) == 0:
                print("ERROR")
            # construct file number
            argnumber = 'FILE{0}'.format(number)
            if argnumber not in args:
                args[argnumber] = list(vindex['FILENAME'][filemask])
            else:
                args[argnumber] += list(vindex['FILENAME'][filemask])
        # make combinations of files
        arguments = [[night_name]]
        # add files
        for it in range(file_args_expected):
            arguments.append(args['FILE{0}'.format(it + 1)])
        combinations = list(itertools.product(*arguments))

        # get command
        command = recipe_lookup(recipe)

        # loop around combinations
        for it, combination in enumerate(combinations):
            # log progress
            wmsgs = [spirouStartup.spirouStartup.HEADER,
                     spirouStartup.spirouStartup.HEADER]
            wargs = [recipe, it + 1, len(combinations)]
            wmsgs.append(' TRIGGER {0} File {1} of {2}'.format(*wargs))
            wmsgs.append(spirouStartup.spirouStartup.HEADER)
            wmsgs.append(spirouStartup.spirouStartup.HEADER)
            # run command
            print([command] + list(combination))


            try:
                ll = command(*combination)
            except Exception as e:
                pp = ParamDict()

    #

# =============================================================================
# main function
# =============================================================================
#def main(night_name=None):
if True:
    night_name = None
    night_name = 'TEST1/20180805'

    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    main_name = __NAME__ + '.main()'
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)
    p = spirouStartup.LoadArguments(p, night_name, require_night_name=False)
    loc = ParamDict()

    # ----------------------------------------------------------------------
    # Check pre-processing
    # ----------------------------------------------------------------------
    raw_files = find_all_raw_files(p)
    # check for pre-processed files
    if SKIP_DONE:
        raw_files = skip_done_raw_files(p, raw_files)
    # pre-process remaining files
    pp_lls = trigger_preprocess(p, raw_files)

    # ----------------------------------------------------------------------
    # Load the recipe_control
    # ----------------------------------------------------------------------
    loc['CONTROL'] = spirouImage.spirouFile.get_control_file()
    loc.set_source('CONTROL', main_name)

    # ----------------------------------------------------------------------
    # Find index_files
    # ----------------------------------------------------------------------
    raw_index_files = find_all_index_files(p)
    gout = get_night_name(p['DRS_DATA_WORKING'], raw_index_files)
    loc['INDEX_NIGHTNAME'], loc['INDEX_FILES'] = gout

    # ----------------------------------------------------------------------
    # Run triggers
    # ----------------------------------------------------------------------
    # 1. cal_BADPIX_spirou.py
    badpix_lls = trigger_main(p, loc, recipe='cal_BADPIX_spirou')
    # 2. cal_DARK_spirou.py
    dark_lls = trigger_main(p, loc)
    # 3. cal_loc_RAW_spirou.py
    loc_lls = trigger_main(p, loc)
    # 4. cal_SLIT_spirou.py
    slit_lls = trigger_main(p, loc)
    # 5. cal_SHAPE_spirou.py
    shape_lls = trigger_main(p, loc)
    # 6. cal_FF_RAW_spirou.py
    flat_lls = trigger_main(p, loc)
    # 7. cal_extract_RAW_spirou.py
    ext_lls = trigger_main(p, loc)




def main(night_name=None):
    return dict(locals())






# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()
    # exit message if in debug mode
    # spirouStartup.Exit(ll, has_plots=False)

# =============================================================================
# End of code
# =============================================================================

