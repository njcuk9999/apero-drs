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
import sys
from astropy.table import Table
import itertools

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup
from SpirouDRS.spirouUnitTests import spirouUnitRecipes

import cal_BADPIX_spirou
# import cal_CCF_E2DS_spirou
import cal_DARK_spirou
# import cal_DRIFT_E2DS_spirou
# import cal_DRIFTPEAK_E2DS_spirou
# import cal_exposure_meter
# import cal_wave_mapper
import cal_extract_RAW_spirou
import cal_FF_RAW_spirou
# import cal_HC_E2DS_spirou
# import cal_HC_E2DS_EA_spirou
import cal_loc_RAW_spirou
import cal_SLIT_spirou
import cal_SHAPE_spirou
# import cal_WAVE_E2DS_spirou
import cal_WAVE_E2DS_EA_spirou
# import cal_WAVE_NEW_E2DS_spirou
import cal_preprocess_spirou
# import off_listing_RAW_spirou
# import off_listing_REDUC_spirou
# import obj_mk_tellu
# import obj_fit_tellu
# import obj_mk_obj_template
# import visu_RAW_spirou
# import visu_E2DS_spirou
# import pol_spirou

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
# Get plotting functions
sPlt = spirouCore.sPlt
# Get param dictionary
ParamDict = spirouConfig.ParamDict
# skip found files
SKIP_DONE = True
# test run
TEST_RUN = False
TEST_STORE = []
# allowed files
RAW_CODES = ['a.fits', 'c.fits', 'd.fits', 'f.fits', 'o.fits']
# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
def recipe_lookup(p, key):
    lookup = dict()
    lookup['cal_preprocess_spirou'] = cal_preprocess_spirou
    lookup['cal_BADPIX_spirou'] = cal_BADPIX_spirou.main
    lookup['cal_DARK_spirou'] = cal_DARK_spirou.main
    lookup['cal_loc_RAW_spirou'] = cal_loc_RAW_spirou.main
    lookup['cal_SLIT_spirou'] = cal_SLIT_spirou.main
    lookup['cal_SHAPE_spirou'] = cal_SHAPE_spirou.main
    lookup['cal_FF_RAW_spirou'] = cal_FF_RAW_spirou.main
    lookup['cal_extract_RAW_spirou'] = cal_extract_RAW_spirou.main
    lookup['cal_WAVE_E2DS_EA_spirou'] = cal_WAVE_E2DS_EA_spirou
    if key not in lookup:
        emsg = 'Recipe {0} not found in lookup table. Recipe unsupported.'
        WLOG('error', p['LOG_OPT'], emsg.format(key))
        return 1
    else:
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


def get_control_index(control, index_file, recipe, fdprtypes=None):
    # load index file
    index = Table.read(index_file)
    # mask control file by recipe name
    cmask = np.array(control['Recipe']) == recipe
    control = control[cmask]
    # get valied files from index
    if 'None' in control['dprtype']:
        vmask = np.ones(len(index), dtype=bool)
    else:
        idprtypes = np.array(index['DPRTYPE']).astype(str)
        vmask = np.in1d(idprtypes, control['dprtype'])
    # apply mask
    vindex = index[vmask]

    # deal with dprtype filter
    if fdprtypes is not None:
        fmask = np.zeros(len(vindex), dtype=bool)
        for fdprtype in fdprtypes:
            fmask |= (vindex['DPRTYPE'] == fdprtype)
        # apply fmask
        vindex = vindex[fmask]

    # return control and vindex
    return control, vindex


def get_file_args(p, control, vindex, recipe, limit=None):
    # get the files in index that match the correct arguments
    args = []
    numbers = []
    # loop around control
    for row in range(len(control)):
        # get parameters from control
        number = control['number'][row]
        dprtype = control['dprtype'][row]
        # construct a mask of files
        if dprtype == 'None':
            filemask = np.ones(len(vindex), dtype=bool)
        else:
            filemask = dprtype == vindex['DPRTYPE']
        # check that we have some files
        if np.sum(filemask) == 0:
            wmsg = 'No files found for recipe "{0}" with key {1}'
            wargs = [recipe, dprtype]
            WLOG('warning', p['LOG_OPT'], wmsg.format(*wargs))

        # make selected files into a list of strings
        values = []
        for value in vindex['FILENAME'][filemask]:
            values.append(str(value))
        # deal with limit
        if limit is not None:
            values = values[:limit]
        # append to lists
        args.append(values)
        numbers.append(number)
    # return args
    return args, numbers


def add_files(p, night, filelist, numbers, combine=False):
    func_name = __NAME__ + '.add_files()'
    # find out which kind of recipe we are dealing with
    numbers = np.array(numbers, dtype=int)
    case1 = np.max(numbers) == 1
    case2 = np.max(numbers) == 2

    # set up storage
    combinations = []
    # deal with case 1
    #   arguments = night_name files[0]
    if case1 and combine:
        for files in filelist:
            if len(files) > 0:
                comb = [night] + list(files)
                combinations.append(comb)

    elif case1:
        for files in filelist:
            for filename in files:
                comb = [night] + [filename]
                combinations.append(comb)

    # deal with case 2
    #   arugmentts = night_names files[0][0] files[1][0]
    elif case2:
        if len(filelist) > 0:
            if len(filelist[0]) > 0 and len(filelist[1]) > 0:
                comb = [night] + [filelist[0][0], filelist[1][0]]
                combinations.append(comb)

    # else unsupported
    else:
        emsg1 = 'Recipe mode unsupported'
        emsg2 = '\tfunc_name = {0}'.format(func_name)
        WLOG('error', p['LOG_OPT'], [emsg1, emsg2])

    # return combinations
    return combinations


def printrun(*args):

    printstring = ''
    for arg in args:
        printstring += '{0}\t'.format(arg)
    TEST_STORE.append(printstring)


def print_runs(p, combinations, recipe):
    # loop around combinations
    for it, combination in enumerate(combinations):
        # log progress
        printrun(recipe, ' '.join(list(combination)))

        print(recipe, combination)


def manage_runs(p, lls, combinations, recipe, night):
    # get command
    command = recipe_lookup(p, recipe)
    # loop around combinations
    for it, combination in enumerate(combinations):
        # log progress
        rargs = [recipe, it + 1, len(combinations)]
        runname = ' TRIGGER {0} File {1} of {2}'.format(*rargs)
        wmsgs = [spirouStartup.spirouStartup.HEADER]
        wmsgs.append(runname)
        wmsgs.append(spirouStartup.spirouStartup.HEADER)
        WLOG('warning', p['LOG_OPT'], wmsgs)
        # run command
        try:
            arglist = [recipe] + list(combination)
            varbs, name = spirouUnitRecipes.wrapper(p, runname, arglist)
            ll = spirouUnitRecipes.run_main(p, name, varbs)
            sPlt.closeall()
            # keep only some parameters
            pp['RECIPE'] = recipe
            pp['NIGHT_NAME'] = night
            pp['ARGS'] = combinations
            pp['ERROR'] = list(ll['p']['LOGGER_ERROR'])
            pp['WARNING'] = list(ll['p']['LOGGER_WARNING'])
            pp['OUTPUTS'] = dict(ll['p']['OUTPUTS'])
            # clean up
            del ll
        except Exception as e:
            # log error
            emsgs = ['Error occured']
            emsgs.append('{0}'.format(e))
            WLOG('warning', p['LOG_OPT'], emsgs)
            # push to ll
            pp = ParamDict()
            pp['RECIPE'] = recipe
            pp['NIGHT_NAME'] = night
            pp['ARGS'] = combination
            pp['ERROR'] = emsgs
            pp['WARNING'] = []
            pp['OUTPUTS'] = dict()
        ll = dict(p=pp)
        lls.append(ll)
    return lls


def ask(message):
    if sys.version_info.major < 3:
        raw_input = raw_input
    else:
        raw_input = input
    user_input = raw_input(message)
    return user_input


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
        if printrun:
            print('cal_preprocess', ' '.join([night_names[it], filenames[it]]))
        else:
            # log progress
            wmsgs = [spirouStartup.spirouStartup.HEADER]
            wargs = [it + 1, len(night_names)]
            wmsgs.append(' TRIGGER PRE-PROCESS File {0} of {1}'.format(*wargs))
            wmsgs.append(spirouStartup.spirouStartup.HEADER)
            WLOG('warning', p['LOG_OPT'], wmsgs)
            # run preprocess
            try:
                args = [night_names[it], filenames[it]]
                lls.append(cal_preprocess_spirou.main(*args))
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


def trigger_main(p, loc, recipe, limit=None, combine=False, fdprtypes=None):
    """

    :param p: parameter dictionary, contains spirou DRS constants
    :param loc: parameter dictionary, contains the data
    :param recipe: string, the name of the recipe (without .py)
    :param fdprtypes: list of strings, allowed DPRTYPES

    :return:
    """
    night_names = loc['INDEX_NIGHTNAME']
    index_files = loc['RAW_INDEX_FILES']
    fullcontrol = loc['CONTROL']
    # loop through index files
    lls = []
    for it, index_file in enumerate(index_files):
        # Get the night name for this recipes
        night_name = night_names[it]

        # log progress
        wmsgs = [spirouStartup.spirouStartup.HEADER]
        wmsg = ' TRIGGER RECIPE: {0} NIGHT_NAME={1} ({2}/{3})'
        wmsgs.append(wmsg.format(recipe, night_name, it+1, len(index_files)))
        if fdprtypes is not None:
            for fdprtype in fdprtypes:
                wmsgs.append('\tDPRTYPE: {0}'.format(fdprtype))
        wmsgs.append(spirouStartup.spirouStartup.HEADER)
        WLOG('warning', p['LOG_OPT'], wmsgs)
        # get the control and index for this
        control, vindex = get_control_index(fullcontrol, index_file, recipe,
                                            fdprtypes)
        # get the files expected
        args, numbers = get_file_args(p, control, vindex, recipe, limit)
        # add files
        combinations = add_files(p, night_name, args, numbers, combine)
        # manage the running of this recipe
        if TEST_RUN:
            print_runs(p, combinations, recipe)
        else:
            lls = manage_runs(p, lls, combinations, recipe, night_name)
    # return local spaces and errors
    return lls


# =============================================================================
# main function
# =============================================================================
def main(night_name=None):
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    main_name = __NAME__ + '.main()'
    if len(sys.argv) > 1:
        night_name = sys.argv[1]

    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)
    p = spirouStartup.LoadArguments(p, night_name, require_night_name=False)

    loc = ParamDict()

    # ----------------------------------------------------------------------
    # Check pre-processing
    # ----------------------------------------------------------------------
    raw_files = find_all_raw_files(p)
    n_raw = len(raw_files)
    # check for pre-processed files
    if SKIP_DONE:
        raw_files = skip_done_raw_files(p, raw_files)

    # ask whether to pre-process
    if len(raw_files) > 0:
        message = 'Will pre-process {0}/{1} files continue? [Y]es or [N]o:\t'
        uinput = ask(message.format(len(raw_files), n_raw))
        if 'Y' in uinput:
            # pre-process remaining files
            pp_lls = trigger_preprocess(p, raw_files)
    elif not SKIP_DONE or n_raw == 0:
        wmsg = 'No raw files found'
        WLOG('warning', p['LOG_OPT'], wmsg)
    else:
        wmsg = 'All files pre-processed (Found {0} files)'
        WLOG('', p['LOG_OPT'], wmsg.format(n_raw))

    # ----------------------------------------------------------------------
    # Load the recipe_control
    # ----------------------------------------------------------------------
    loc['CONTROL'] = spirouImage.spirouFile.get_control_file()
    loc.set_source('CONTROL', main_name)

    # ----------------------------------------------------------------------
    # Find index_files
    # ----------------------------------------------------------------------
    loc['RAW_INDEX_FILES'] = find_all_index_files(p)
    gout = get_night_name(p['DRS_DATA_WORKING'], loc['RAW_INDEX_FILES'])
    loc['INDEX_NIGHTNAME'], loc['INDEX_FILES'] = gout
    # set sources
    keys = ['RAW_INDEX_FILES', 'INDEX_NIGHTNAME', 'INDEX_FILES']
    loc.set_sources(keys, main_name)

    # ----------------------------------------------------------------------
    # Run triggers
    # ----------------------------------------------------------------------
    WLOG('', p['LOG_OPT'], 'Running triggers')

    # 1. cal_BADPIX_spirou.py
    badpix_lls = trigger_main(p, loc, recipe='cal_BADPIX_spirou', limit=1)
    # 2. cal_DARK_spirou.py
    dark_lls = trigger_main(p, loc, recipe='cal_DARK_spirou', combine=True)
    # 3. cal_loc_RAW_spirou.py
    loc_lls = trigger_main(p, loc, recipe='cal_loc_RAW_spirou', combine=True)
    # 4. cal_SLIT_spirou.py
    slit_lls = trigger_main(p, loc, recipe='cal_SLIT_spirou', combine=True)
    # 5. cal_SHAPE_spirou.py
    shape_lls = trigger_main(p, loc, recipe='cal_SHAPE_spirou', combine=True)
    # 6. cal_FF_RAW_spirou.py
    flat_lls = trigger_main(p, loc, recipe='cal_FF_RAW_spirou', combine=True)
    # 7. cal_extract_RAW_spirou.py (HCONE_HCONE, FP_FP)
    hcfp_lls = trigger_main(p, loc, recipe='cal_extract_RAW_spirou',
                           fdprtypes=['HCONE_HCONE', 'FP_FP'])
    # 8. cal_WAVE_E2DS_RAW_spirou.py
    # wave_lls = trigger_main(p, loc, recipe='cal_WAVE_E2DS_EA_spirou',
    #                         limit=1)
    # 9. cal_extract_RAW_spirou.py (OBJ_FP, OBJ_OBJ, FP_FP)


    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    p = spirouStartup.End(p, outputs=None)
    # return locals
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

