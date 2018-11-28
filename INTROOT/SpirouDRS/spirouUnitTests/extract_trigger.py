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
from collections import OrderedDict

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup
from SpirouDRS.spirouUnitTests import spirouUnitRecipes

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
DATECOL = 'MJDATE'
# DATECOL = 'LAST_MODIFIED'

# switches
RUN_BADPIX = False
RUN_DARK = False
RUN_LOC = False
RUN_SLIT = False
RUN_SHAPE = False
RUN_FLAT = False
RUN_EXTRACT_HCFP = False
RUN_EXTRACT_OBJ = False
# -----------------------------------------------------------------------------


# =============================================================================
# Define functions
# =============================================================================
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
    # deal with ending /
    while rawpath.endswith(os.path.sep):
        rawpath = rawpath[:-1]
    while donepath.endswith(os.path.sep):
        donepath = donepath[:-1]
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
        # remove trailing separator
        while uncommonpath.endswith(os.path.sep):
            uncommonpath = uncommonpath[:-1]
        # get basename
        basename = os.path.basename(uncommonpath)
        # get nightname
        night_name = uncommonpath.split(basename)[0]
        # append to list
        night_names.append(night_name)
        filenames.append(basename)
    # return night names and filenames
    return night_names, filenames


def get_control_index(control, index_file, recipe, fdprtypes=None,
                      objnames=None):
    # load index file
    index = Table.read(index_file)

    if recipe == 'cal_preprocess_spirou':
        return control, index

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

    # deal with objname filter
    if objnames is not None:
        omask = np.zeros(len(vindex), dtype=bool)
        for objname in objnames:
            omask |= (vindex['OBJNAME'] == objname)
        # apply omask
        vindex = vindex[omask]

    # return control and vindex
    return control, vindex


def get_file_args(p, control, vindex, recipe, limit=None):
    # get the files in index that match the correct arguments
    args = []
    numbers = []
    sequences = []
    totals = []
    # loop around control
    for row in range(len(control)):
        # get parameters from control
        number = control['number'][row]
        dprtype = control['dprtype'][row]
        sequence = control['cmpltexp'][row]
        total = control['nexp'][row]
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
        sequences.append(sequence)
        totals.append(total)
    # return args
    return args, numbers, sequences, totals


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


def printrun(arg):
    global TEST_STORE
    TEST_STORE.append(arg)


def print_runs(p, combinations, recipe):
    # loop around combinations
    for it, combination in enumerate(combinations):

        command = 'run0000 = {0}'
        clist = [recipe] + list(np.array(combination).astype(str))
        # log progress
        printrun(command.format(clist))
        print(command.format(clist))


def manage_runs(p, lls, combinations, recipe, night):
    # loop around combinations
    for it, combination in enumerate(combinations):
        # log progress
        rargs = [recipe, it + 1, len(combinations)]
        runname = ' TRIGGER {0} File {1} of {2}'.format(*rargs)
        wmsgs = [spirouStartup.spirouStartup.HEADER, runname,
                 spirouStartup.spirouStartup.HEADER]
        WLOG('warning', p['LOG_OPT'], wmsgs)
        # setup storage for output parameters
        pp = ParamDict()
        # run command
        try:
            arglist = [recipe] + list(combination)
            varbs, name = spirouUnitRecipes.wrapper(p, runname, arglist)
            ll_s = spirouUnitRecipes.run_main(p, name, varbs)
            sPlt.closeall()
            # keep only some parameters
            pp['RECIPE'] = recipe
            pp['NIGHT_NAME'] = night
            pp['ARGS'] = combinations
            pp['ERROR'] = list(lls['p']['LOGGER_ERROR'])
            pp['WARNING'] = list(lls['p']['LOGGER_WARNING'])
            pp['OUTPUTS'] = dict(lls['p']['OUTPUTS'])
            # clean up
            del ll_s
        # Manage unexpected errors
        except Exception as e:
            # log error
            emsgs = ['Unexpected error occured Recipe={0} Run={1}'
                     ''.format(recipe, it)]
            for emsg in str(e).split('\n'):
                emsgs.append('\t' + emsg)
            WLOG('warning', p['LOG_OPT'], emsgs)
            # push to ll
            pp['RECIPE'] = recipe
            pp['NIGHT_NAME'] = night
            pp['ARGS'] = combination
            pp['ERROR'] = emsgs
            pp['WARNING'] = []
            pp['OUTPUTS'] = dict()
        # Manage expected errors
        except SystemExit as e:
            # log error
            emsgs = ['Expected error occured Recipe={0} Run={1}'
                     ''.format(recipe, it)]
            for emsg in str(e).split('\n'):
                emsgs.append('\t' + emsg)
            WLOG('warning', p['LOG_OPT'], emsgs)
            # push to ll
            pp['RECIPE'] = recipe
            pp['NIGHT_NAME'] = night
            pp['ARGS'] = combination
            pp['ERROR'] = emsgs
            pp['WARNING'] = []
            pp['OUTPUTS'] = dict()
        # append output parameters to ll and store in lls
        ll_s = dict(p=pp)
        lls.append(ll_s)
    return lls


def ask(message):
    if sys.version_info.major < 3:
        # noinspection PyUnboundLocalVariable
        raw_input = raw_input
    else:
        raw_input = input
    user_input = raw_input(message)
    return user_input


def get_groups(vindex):

    date = vindex[DATECOL]
    dprtypes = vindex['DPRTYPE']
    raw_seqs = vindex['CMPLTEXP']
    seqs = np.zeros(len(raw_seqs)).astype(int)
    # mask out '--'
    for it in range(len(raw_seqs)):
        try:
            seqs[it] = int(raw_seqs[it])
        except:
            pass

    # sort vindex by date
    vindex = vindex[np.argsort(date)]


    groupnames = np.unique(dprtypes)
    allgroups = dict()

    for groupname in groupnames:
        # build a mask for this group
        groupmask = np.where(groupname == dprtypes)[0]
        # group by CMPLTEXP and NEXP
        last_seq = 0
        groups, group = [], []
        for row in range(len(vindex)):
            if row not in groupmask:
                continue
            if seqs[row] < last_seq:
                groups.append(group)
                group = []
            group.append(row)
            last_seq = seqs[row]
        if len(group) != 0:
            groups.append(group)
        # add indices to allgroups
        allgroups[groupname] = groups

    return allgroups



# =============================================================================
# trigger functions
# =============================================================================
def trigger_preprocess(p, filelist):
    recipe = 'cal_preprocess_spirou'
    # define path to raw folder
    rawpath = p['DRS_DATA_WORKING']
    # get night name
    night_names, filenames = get_night_name(rawpath, filelist)
    # catch errors
    errors = OrderedDict()
    # pre-process files
    import cal_preprocess_spirou
    # loop around files
    lls = []
    for it in range(len(night_names)):

        # get raw filename
        rawfilename = filenames[it].replace('_pp.fits', '.fits')

        if TEST_RUN:
            print_runs(p, [[night_names[it], rawfilename]], recipe)
        else:
            # log progress
            wmsgs = [spirouStartup.spirouStartup.HEADER]
            wargs = [it + 1, len(night_names)]
            wmsgs.append(' TRIGGER PRE-PROCESS File {0} of {1}'.format(*wargs))
            wmsgs.append(spirouStartup.spirouStartup.HEADER)
            WLOG('warning', p['LOG_OPT'], wmsgs)
            # run preprocess
            try:
                args = [night_names[it], rawfilename]
                lls.append(cal_preprocess_spirou.main(*args))
            # Manage unexpected errors
            except Exception as e:
                wmsgs = ['PPRun "{0}" had an unexpected error:'.format(it)]
                for msg in str(e).split('\n'):
                    wmsgs.append('\t' + msg)
                WLOG('warning', p['LOG_OPT'], wmsgs)
                errors['Run{0}'.format(it)] = str(e)

                pp = ParamDict()
                pp['NIGHT_NAME'] = night_names[it]
                pp['FILENAME'] = rawfilename
                pp['EMSGS'] = wmsgs
                pp['Exception'] = e
                lls.append(dict(p=pp))
            # Manage expected errors
            except SystemExit as e:
                wmsgs = ['PPRun "{0}" had an expected error:'.format(it)]
                for msg in str(e).split('\n'):
                    wmsgs.append('\t' + msg)
                WLOG('warning', p['LOG_OPT'], wmsgs)
                errors['PPRun{0}'.format(it)] = str(e)

                pp = ParamDict()
                pp['NIGHT_NAME'] = night_names[it]
                pp['FILENAME'] = rawfilename
                pp['EMSGS'] = wmsgs
                pp['Exception'] = e
                lls.append(dict(p=pp))

    # return local directories
    return lls, errors


def trigger_main(p, loc, recipe, fdprtypes=None, fobjnames=None):
    """

    :param p: parameter dictionary, contains spirou DRS constants
    :param loc: parameter dictionary, contains the data
    :param recipe: string, the name of the recipe (without .py)
    :param fdprtypes: list of strings, allowed DPRTYPES
    :param fobjnames: list of strings, allowed OBJNAMES

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
        wmsgs.append(wmsg.format(recipe, night_name, it + 1, len(index_files)))
        # add dprtype filter
        if fdprtypes is not None:
            for fdprtype in fdprtypes:
                wmsgs.append('\tDPRTYPE: {0}'.format(fdprtype))
        # add objname filter
        if fobjnames is not None:
            for fobjname in fobjnames:
                wmsgs.append('\tOBJNAME: {0}'.format(fobjname))

        # add closing header
        wmsgs.append(spirouStartup.spirouStartup.HEADER)
        WLOG('warning', p['LOG_OPT'], wmsgs)
        # get the control and index for this
        control, vindex = get_control_index(fullcontrol, index_file, recipe,
                                            fdprtypes, fobjnames)
        # make sure MJDATE is float
        vindex[DATECOL] = np.array(vindex[DATECOL]).astype(float)
        # make the runs
        runs = trigger_runs(p, recipe, night_name, control, vindex)
        # manage the running of this recipe
        if TEST_RUN:
            print_runs(p, runs, recipe)
        else:
            lls = manage_runs(p, lls, runs, recipe, night_name)
    # return local spaces and errors
    return lls


def trigger_runs(p, recipe, night_name, control, vindex):

    # define groups of different objects
    groups = get_groups(vindex)

    # manually deal with recipes separately # TODO: change
    if recipe == 'cal_BADPIX_spirou':
        return cal_badpix_spirou(night_name, vindex, groups)

    if recipe == 'cal_DARK_spirou':
        return cal_dark_spirou(night_name, vindex, groups)

    if recipe == 'cal_loc_RAW_spirou':
        return cal_loc_raw_spirou(night_name, vindex, groups)

    if recipe == 'cal_SLIT_spirou':
        return cal_slit_spirou(night_name, vindex, groups)

    if recipe == 'cal_SHAPE_spirou':
        return cal_shape_spirou(night_name, vindex, groups)

    if recipe == 'cal_SHAPE_spirou2':
        return cal_shape_spirou2(night_name, vindex, groups)

    if recipe == 'cal_FF_RAW_spirou':
        return cal_ff_raw_spirou(night_name, vindex, groups)

    if recipe == 'cal_extract_RAW_spirou':
        return cal_extract_raw_spirou(night_name, vindex, groups)

    return []


# =============================================================================
# recipe functions
# =============================================================================
def cal_badpix_spirou(night_name, vindex, groups):
    """
    for cal_badpix we need 1 dark_dark and 1 flat_flat
    we need to match the groups by date
    we need to choose the last file in the dark_dark and flat_flat groups
    """
    # get the dark_dark files
    if 'DARK_DARK' in groups:
        dark_groups = groups['DARK_DARK']
        dark_dates = get_group_vindex(vindex, dark_groups, DATECOL)
        dark_files = get_group_vindex(vindex, dark_groups, 'FILENAME')
        num_dark_groups = len(dark_dates)
        mean_dark_dates = get_group_mean(dark_dates)

    else:
        WLOG('warning', '', 'DARK_DARK not in groups')
        return []

    # get the flat_flat files
    if 'FLAT_FLAT' in groups:
        flat_groups = groups['FLAT_FLAT']
        flat_dates = get_group_vindex(vindex, flat_groups, DATECOL)
        flat_files = get_group_vindex(vindex, flat_groups, 'FILENAME')
        num_flat_groups = len(dark_dates)
        mean_flat_dates = get_group_mean(flat_dates)
    else:
        WLOG('warning', '', 'FLAT_FLAT not in groups')
        return []

    # runs
    runs = []
    # match dark groups and flat groups
    if num_dark_groups > num_flat_groups:
        for num in range(num_flat_groups):
            # find dark group closest
            date_dist = mean_flat_dates[num] - np.array(mean_dark_dates)
            pos = np.argmin(np.abs(date_dist))
            myrun = [night_name, flat_files[num][-1], dark_files[pos][-1]]
            runs.append(myrun)
    else:
        for num in range(num_dark_groups):
            # find dark group closest
            date_dist = mean_dark_dates[num] - np.array(mean_flat_dates)
            pos = np.argmin(np.abs(date_dist))
            myrun = [night_name, flat_files[pos][-1], dark_files[num][-1]]
            runs.append(myrun)
    # return runs
    return runs


def cal_dark_spirou(night_name, vindex, groups):
    """
    for cal_dark we need all but the first dark in a sequence (unless there
    is only one dark file)

    """
    # get the dark_dark files
    if 'DARK_DARK' in groups:
        dark_groups = groups['DARK_DARK']
        dark_files = get_group_vindex(vindex, dark_groups, 'FILENAME')
        num_dark_groups = len(dark_files)
    else:
        WLOG('warning', '', 'DARK_DARK not in groups')
        return []
    # runs
    runs = []
    # push all from group into file
    for num in range(num_dark_groups):
        if len(dark_files[num]) == 1:
            myrun = [night_name] + dark_files[num]
        else:
             myrun = [night_name] + dark_files[num][1:]
        runs.append(myrun)
    # return runs
    return runs


def cal_loc_raw_spirou(night_name, vindex, groups):
    """
    for cal_loc_raw_spirou we need to do all the flat_dark groups and
    all of the dark_flat groups separately, we need to use all files except
    the first unless there is only one file

    """
    # get the flat_dark files
    if 'FLAT_DARK' in groups:
        flat_dark_groups = groups['FLAT_DARK']
        flat_dark_files = get_group_vindex(vindex, flat_dark_groups, 'FILENAME')
        num_flat_dark_groups = len(flat_dark_files)
    else:
        num_flat_dark_groups = 0
        flat_dark_files = []
    # get the flat_dark files
    if 'DARK_FLAT' in groups:
        dark_flat_groups = groups['DARK_FLAT']
        dark_flat_files = get_group_vindex(vindex, dark_flat_groups, 'FILENAME')
        num_dark_flat_groups = len(dark_flat_files)
    else:
        dark_flat_files = []
        num_dark_flat_groups = 0

    if len(dark_flat_files) == 0 and len(flat_dark_files) == 0:
        WLOG('warning', '', 'Must have FLAT_DARK or DARK_FLAT files in group')
        return []

    # runs
    runs = []
    # push all from group into file
    for num in range(num_flat_dark_groups):
        if len(flat_dark_files[num]) == 1:
            myrun = [night_name] + flat_dark_files[num]
        else:
             myrun = [night_name] + flat_dark_files[num][1:]
        runs.append(myrun)
    # push all from group into file
    for num in range(num_dark_flat_groups):
        if len(dark_flat_files[num]) == 1:
            myrun = [night_name] + dark_flat_files[num]
        else:
             myrun = [night_name] + dark_flat_files[num][1:]
        runs.append(myrun)
    # return runs
    return runs


def cal_slit_spirou(night_name, vindex, groups):
    # get the dark_dark files
    if 'FP_FP' in groups:
        fp_fp_groups = groups['FP_FP']
        fp_fp_files = get_group_vindex(vindex, fp_fp_groups, 'FILENAME')
        num_fp_fp_groups = len(fp_fp_files)
    else:
        WLOG('warning', '', 'FP_FP not in groups')
        return []
    # runs
    runs = []
    # push all from group into file
    for num in range(num_fp_fp_groups):
        if len(fp_fp_files[num]) == 1:
            myrun = [night_name] + fp_fp_files[num]
        else:
             myrun = [night_name] + fp_fp_files[num][1:]
        runs.append(myrun)
    # return runs
    return runs


def cal_shape_spirou(night_name, vindex, groups):
    """
    for cal_shape_spirou we use all the fp_fp files except the first (unless
    there is only one fp_fp file)
    """
    # get the dark_dark files
    if 'FP_FP' in groups:
        fp_fp_groups = groups['FP_FP']
        fp_fp_files = get_group_vindex(vindex, fp_fp_groups, 'FILENAME')
        num_fp_fp_groups = len(fp_fp_files)
    else:
        WLOG('warning', '', 'FP_FP not in groups')
        return []
    # runs
    runs = []
    # push all from group into file
    for num in range(num_fp_fp_groups):
        if len(fp_fp_files[num]) == 1:
            myrun = [night_name] + fp_fp_files[num]
        else:
             myrun = [night_name] + fp_fp_files[num][1:]
        runs.append(myrun)
    # return runs
    return runs


def cal_shape_spirou2(night_name, vindex, groups):
    """
    for cal_shape_spirou2 we need to match hc groups to fp groups
    we need to use the last hc of a group and all but the first fp_fp in a
    sequence (unless there is only fp_fp file)
    """
    # get the dark_dark files
    if 'FP_FP' in groups:
        fp_fp_groups = groups['FP_FP']
        fp_fp_files = get_group_vindex(vindex, fp_fp_groups, 'FILENAME')
        fp_fp_dates = get_group_vindex(vindex, fp_fp_groups, DATECOL)
        num_fp_fp_groups = len(fp_fp_files)
        mean_fp_fp_dates = get_group_mean(fp_fp_dates)
    else:
        WLOG('warning', '', 'FP_FP not in groups')
        return []

    if 'HCONE_HCONE' in groups:
        hc_hc_groups = groups['HCONE_HCONE']
        hc_hc_files = get_group_vindex(vindex, hc_hc_groups, 'FILENAME')
        hc_hc_dates = get_group_vindex(vindex, hc_hc_groups, DATECOL)
        num_hc_hc_groups = len(hc_hc_files)
        mean_hc_hc_dates = get_group_mean(hc_hc_dates)
    else:
        WLOG('warning', '', 'HCONE_HCONE not in groups')
        return []
    # runs
    runs = []
    # match dark groups and flat groups
    for num in range(num_hc_hc_groups):
        # find dark group closest
        date_dist = mean_hc_hc_dates[num] - np.array(mean_fp_fp_dates)
        pos = np.argmin(np.abs(date_dist))

        if len(fp_fp_files[pos]) == 1:
            myrun = [night_name, hc_hc_files[num][-1]] + fp_fp_files[pos]
        else:
            myrun = [night_name, hc_hc_files[num][-1]] + fp_fp_files[pos][1:]
        runs.append(myrun)

    # return runs
    return runs


def cal_ff_raw_spirou(night_name, vindex, groups):
    """
    for cal_ff_raw_spirou we use all the flat_flat files except the first
    (unless there is only one fp_fp file)
    """
    # get the dark_dark files
    if 'FLAT_FLAT' in groups:
        flat_flat_groups = groups['FLAT_FLAT']
        flat_flat_files = get_group_vindex(vindex, flat_flat_groups, 'FILENAME')
        num_flat_flat_groups = len(flat_flat_files)
    else:
        WLOG('warning', '', 'FLAT_FLAT not in groups')
        return []
    # runs
    runs = []
    # push all from group into file
    for num in range(num_flat_flat_groups):
        if len(flat_flat_files[num]) == 1:
            myrun = [night_name] + flat_flat_files[num]
        else:
             myrun = [night_name] + flat_flat_files[num][1:]
        runs.append(myrun)
    # return runs
    return runs


def cal_extract_raw_spirou(night_name, vindex, groups):
    """
    for cal_extract_raw_spirou we just separate files and run each
    separately
    """
    # get the dark_dark files
    filelist = []
    for group in groups:
        file_groups = groups[group]
        for subgroup in file_groups:
            filelist += get_group_vindex(vindex, subgroup, 'FILENAME')
    # runs
    runs = []
    # push all from group into file
    for num in range(len(filelist)):
        myrun = [night_name, filelist[num]]
        runs.append(myrun)
    # return runs
    return runs



# =============================================================================
# group functions
# =============================================================================
def get_group_vindex(vindex, group, col=None):


    # case 1 we have an integer as a group
    if type(group) == int:
        if col is None:
            return vindex[group]
        else:
            return vindex[group][col]

    if type(group) == list:
        # case 2 we have a list of ints as a group
        if type(group[0]) == int:
            rlist = []
            for row in range(len(group)):
                if col is None:
                    rlist.append(vindex[group[row]])
                else:
                    rlist.append(vindex[group[row]][col])
            return rlist
        # case 3 we have a list of list as a group
        if type(group[0]) == list:
            rlist = []
            for it in range(len(group)):
                rit_list = []
                for row in range(len(group[it])):
                    if col is None:
                        rit_list.append(vindex[group[it][row]])
                    else:
                        rit_list.append(vindex[group[it][row]][col])
                rlist.append(rit_list)
            return rlist


def get_group_mean(group):
    if type(group) == int:
        return group
    if type(group) == list:
        if type(group[0]) == int:
            return np.mean(group)
        if type(group[0]) == list:
            rlist = []
            for it in range(len(group)):
                rlist.append(np.mean(group[it]))
            return rlist


def report_errors(p, errors, recipe):
    if len(errors) > 0:
        WLOG('warning', p['LOG_OPT'], '')
        WLOG('warning', p['LOG_OPT'], '{0} Errors:'.format(recipe))
        WLOG('warning', p['LOG_OPT'], '')
        for key in errors:
            error = errors[key]
            WLOG('warning', p['LOG_OPT'], error)


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
    # sort by name
    raw_files = np.sort(raw_files)

    # ask whether to pre-process
    if len(raw_files) > 0:
        message = 'Will pre-process {0}/{1} files continue? [Y]es or [N]o:\t'
        uinput = ask(message.format(len(raw_files), n_raw))
        if 'Y' in uinput.upper():
            # pre-process remaining files
            pp_lls = trigger_preprocess(p, raw_files)
        else:
            pp_lls = [None, dict()]
    elif not SKIP_DONE or n_raw == 0:
        wmsg = 'No raw files found'
        WLOG('warning', p['LOG_OPT'], wmsg)
        pp_lls = [None, dict()]
    else:
        wmsg = 'All files pre-processed (Found {0} files)'
        WLOG('', p['LOG_OPT'], wmsg.format(n_raw))
        pp_lls = [None, dict()]

    # report pp errors
    report_errors(p, pp_lls[1], 'cal_preprocess')

    # ----------------------------------------------------------------------
    # Load the recipe_control
    # ----------------------------------------------------------------------
    loc['CONTROL'] = spirouImage.spirouFile.get_control_file()
    loc.set_source('CONTROL', main_name)

    # ----------------------------------------------------------------------
    # Find index_files
    # ----------------------------------------------------------------------
    loc['RAW_INDEX_FILES'] = find_all_index_files(p)
    loc['RAW_INDEX_FILES'] = np.sort(loc['RAW_INDEX_FILES'])
    gout = get_night_name(p['DRS_DATA_WORKING'], loc['RAW_INDEX_FILES'])
    loc['INDEX_NIGHTNAME'], loc['INDEX_FILES'] = gout
    # set sources
    keys = ['RAW_INDEX_FILES', 'INDEX_NIGHTNAME', 'INDEX_FILES']
    loc.set_sources(keys, main_name)

    # ----------------------------------------------------------------------
    # Run triggers
    # ----------------------------------------------------------------------
    WLOG('', p['LOG_OPT'], 'Running triggers')
    all_lls = OrderedDict()

    # # 1. cal_BADPIX_spirou.py
    if RUN_BADPIX:
        lls = trigger_main(p, loc, recipe='cal_BADPIX_spirou')
        all_lls['cal_BADPIX_spirou'] = lls
    # # 2. cal_DARK_spirou.py
    if RUN_DARK:
        lls = trigger_main(p, loc, recipe='cal_DARK_spirou')
        all_lls['cal_DARK_spirou'] = lls
    # # 3. cal_loc_RAW_spirou.py
    if RUN_LOC:
        lls = trigger_main(p, loc, recipe='cal_loc_RAW_spirou')
        all_lls['cal_loc_RAW_spirou'] = lls
    # # 4. cal_SLIT_spirou.py
    if RUN_SLIT:
        lls = trigger_main(p, loc, recipe='cal_SLIT_spirou')
        all_lls['cal_SLIT_spirou'] = lls
    # # 5. cal_SHAPE_spirou.py
    if RUN_SHAPE:
        lls = trigger_main(p, loc, recipe='cal_SHAPE_spirou2')
        all_lls['cal_SHAPE_spirou2'] = lls
    # # 6. cal_FF_RAW_spirou.py
    if RUN_FLAT:
        lls = trigger_main(p, loc, recipe='cal_FF_RAW_spirou')
        all_lls['cal_FF_RAW_spirou'] = lls
    # # 7. cal_extract_RAW_spirou.py (HCONE_HCONE, FP_FP)
    if RUN_EXTRACT_HCFP:
        lls = trigger_main(p, loc, recipe='cal_extract_RAW_spirou',
                                 fdprtypes=['HCONE_HCONE', 'FP_FP'])
        all_lls['cal_extract_RAW_spirou (HC/FP)'] = lls
    # # 8. extract objects
    if RUN_EXTRACT_OBJ:
        lls = trigger_main(p, loc, recipe='cal_extract_RAW_spirou',
                               fdprtypes=['OBJ_FP', 'OBJ_OBJ'],
                               fobjnames=['Gl699', 'Gl15A'])
        all_lls['cal_extract_RAW_spirou (OBJ)'] = lls

    # 8. cal_WAVE_E2DS_RAW_spirou.py
    # wave_lls = trigger_main(p, loc, recipe='cal_WAVE_E2DS_EA_spirou',
    #                         limit=1)
    # 9. cal_extract_RAW_spirou.py (OBJ_FP, OBJ_OBJ, FP_FP)

    # ----------------------------------------------------------------------
    # report errors
    # ----------------------------------------------------------------------
    for recipe in all_lls:
        errors = all_lls[recipe][1]
        report_errors(p, errors, recipe)

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
