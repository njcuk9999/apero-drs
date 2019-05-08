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
from multiprocessing import Process

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup
from SpirouDRS import spirouTelluric
from SpirouDRS.spirouUnitTests import spirouUnitRecipes
from SpirouDRS.spirouUnitTests import spirouUnitTests

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
# -----------------------------------------------------------------------------
# EMAIL SETTINGS
#    Note must have yagmail and dependencies installed
#    Will ask for keyring password each time or email password
#    One email will send at start and one at end with the log printed to the
#    body of the message (PID in subject)
EMAIL = True
EMAIL_ADDRESS = 'neil.james.cook@gmail.com'
try:
    if not EMAIL:
        YAG = None
    else:
        import yagmail
        YAG = yagmail.SMTP(EMAIL_ADDRESS)
except:
    YAG = None
# -----------------------------------------------------------------------------
# test run
TEST_RUN = True
TEST_STORE = []
# -----------------------------------------------------------------------------
# switches
RUN_BADPIX = True
RUN_DARK = True
RUN_LOC = True
RUN_SLIT = True
RUN_SHAPE = True
RUN_FLAT = True
RUN_EXTRACT_HCFP = True
RUN_HC_WAVE = True
RUN_WAVE_WAVE = True
RUN_EXTRACT_TELLU = False
RUN_EXTRACT_OBJ = False
RUN_EXTRACT_DARK = False
RUN_EXTRACT_ALL = False
RUN_OBJ_MK_TELLU = False
RUN_OBJ_FIT_TELLU = False
# -----------------------------------------------------------------------------
# skip found files
SKIP_DONE_PP = True
SKIP_DONE_EXTRACT = False
SKIP_DONE_HC_WAVE = False
SKIP_DONE_WAVE_WAVE = False
SKIP_DONE_MK_TELLU = False
SKIP_DONE_FIT_TELLU = False
# -----------------------------------------------------------------------------
# turn on parallelisation
PARALLEL = False
# Max Processes
MAX_PROCESSES = 8
# -----------------------------------------------------------------------------
# inputs
INPUT_HC_AB = '_e2dsff_AB.fits'
INPUT_HC_C = '_e2dsff_C.fits'
INPUT_WAVE_AB = '_e2dsff_AB.fits'
INPUT_WAVE_C = '_e2dsff_C.fits'
INPUT_MK_TELLU = '_e2dsff_AB.fits'
INPUT_FIT_TELLU = '_e2dsff_AB.fits'
# -----------------------------------------------------------------------------
# define the science targets
SCIENCE_TARGETS = ['Gl699', 'Gl15A']
# SCIENCE_TARGETS = ['HD189733', 'GJ1002']
# -----------------------------------------------------------------------------
# define run number
RUNNUMBER = 0
# allowed files
RAW_CODES = ['a.fits', 'c.fits', 'd.fits', 'f.fits', 'o.fits']
DATECOL = 'MJDATE'
# DATECOL = 'LAST_MODIFIED'
# telluric object list
TELL_WHITELIST = spirouTelluric.GetWhiteList()
# this is only used if DATES is not None
DATES = ['2018-05-22', '2018-05-23', '2018-05-24', '2018-05-25', '2018-05-26',
         '2018-05-27', '2018-05-28', '2018-05-29', '2018-05-30', '2018-05-31',
         '2018-07-22', '2018-07-23', '2018-07-24', '2018-07-25', '2018-07-26',
         '2018-07-27', '2018-07-28', '2018-07-29', '2018-07-30', '2018-07-31',
         '2018-08-01', '2018-08-02', '2018-08-03', '2018-08-04', '2018-08-05',
         '2018-08-06', '2018-08-07', '2018-09-19', '2018-09-20', '2018-09-21',
         '2018-09-22', '2018-09-23', '2018-09-24', '2018-09-25', '2018-09-26',
         '2018-09-27', '2018-10-22', '2018-10-23', '2018-10-24', '2018-10-25',
         '2018-10-26', '2018-10-27', '2018-12-16', '2018-12-17', '2018-12-18',
         '2018-12-19', '2018-12-20', '2019-01-14', '2019-01-15', '2019-01-16',
         '2019-01-17', '2019-01-18']
DATES = None


# =============================================================================
# Define functions
# =============================================================================
def send_email(params, kind='start'):

    if YAG is None:
        return 0

    if kind == 'start':
        receiver = EMAIL_ADDRESS
        subject = ('[SPIROU-DRS] {0} has started (PID = {1})'
                   ''.format(__NAME__, params['PID']))
        body = ''
        for logmsg in WLOG.pout['LOGGER_ALL']:
            body += '{0}\t{1}\n'.format(*logmsg)

    elif kind == 'end':
        receiver = EMAIL_ADDRESS
        subject = ('[SPIROU-DRS] {0} has finished (PID = {1})'
                   ''.format(__NAME__, params['PID']))

        body = ''
        for logmsg in params['LOGGER_FULL']:
            for log in logmsg:
                body += '{0}\t{1}\n'.format(*log)
    else:
        return 0

    YAG.send(to=receiver, subject=subject, contents=body)


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
            newfilelist.append(filename)
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

    # deal with stripping string rows
    vindex['DPRTYPE'] = np.array(strip_names(vindex['DPRTYPE']))
    vindex['OBJNAME'] = np.array(strip_names(vindex['OBJNAME']))

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
            WLOG(p, 'warning', wmsg.format(*wargs))

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
        WLOG(p, 'error', [emsg1, emsg2])

    # return combinations
    return combinations


def printrun(arg):
    global TEST_STORE
    TEST_STORE.append(arg)


def print_runs(p, combinations, recipe, logonly=False):
    global RUNNUMBER
    # loop around combinations
    for it, combination in enumerate(combinations):
        command = 'run{0:04d} = {1}'
        clist = [recipe] + list(np.array(combination).astype(str))
        # log progress
        printrun(command.format(RUNNUMBER, clist))
        WLOG(p, '', command.format(RUNNUMBER, clist), logonly=logonly)
        # iterate run number
        RUNNUMBER += 1


def manage_run(p, recipe, args, runname, night):
    # setup storage for output parameters
    pp = ParamDict()
    # run command
    try:
        arglist = [recipe] + list(args)
        varbs, name = spirouUnitRecipes.wrapper(p, runname, arglist)
        ll_s = spirouUnitRecipes.run_main(p, name, varbs)
        sPlt.closeall()
        # keep only some parameters
        pp['RECIPE'] = recipe
        pp['NIGHT_NAME'] = night
        pp['ARGS'] = args
        pp['ERROR'] = list(ll_s['p']['LOGGER_ERROR'])
        pp['WARNING'] = list(ll_s['p']['LOGGER_WARNING'])
        pp['OUTPUTS'] = dict(ll_s['p']['OUTPUTS'])
        # clean up
        del ll_s
    # Manage unexpected errors
    except Exception as e:
        # log error
        emsgs = ['Unexpected error occured in run={0}'.format(runname)]
        for emsg in str(e).split('\n'):
            emsgs.append('\t' + emsg)
        WLOG(p, 'warning', emsgs)
        # push to ll
        pp['RECIPE'] = recipe
        pp['NIGHT_NAME'] = night
        pp['ARGS'] = args
        pp['ERROR'] = emsgs
        pp['WARNING'] = []
        pp['OUTPUTS'] = dict()
    # Manage expected errors
    except SystemExit as e:
        # log error
        emsgs = ['Unexpected error occured in run={0}'.format(runname)]
        for emsg in str(e).split('\n'):
            emsgs.append('\t' + emsg)
        WLOG(p, 'warning', emsgs)
        # push to ll
        pp['RECIPE'] = recipe
        pp['NIGHT_NAME'] = night
        pp['ARGS'] = args
        pp['ERROR'] = emsgs
        pp['WARNING'] = []
        pp['OUTPUTS'] = dict()
    # append output parameters to ll and store in lls
    ll_s = dict(p=pp)
    return ll_s


def manage_runs(p, lls, combinations, recipe, night):
    # loop around combinations
    for it, combination in enumerate(combinations):
        # log progress
        rargs = [recipe, it + 1, len(combinations)]
        runname = ' TRIGGER {0} File {1} of {2}'.format(*rargs)
        wmsgs = [spirouStartup.spirouStartup.HEADER, runname,
                 spirouStartup.spirouStartup.HEADER]
        WLOG(p, 'warning', wmsgs)
        ll_s = manage_run(p, recipe, combination, runname, night)
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
# parallelisation functions
# =============================================================================
def group_runs(runs):
    # define storage for group runs
    groups = OrderedDict()
    # start group number at zero
    group_number = 0
    # start group program is None
    group_program = None
    # loop around runs
    for runn in runs:
        # get iteration program
        program = runs[runn][0]
        # get group program
        if group_program is None:
            group_program = str(program)
            group_number += 1
        elif program != group_program:
            group_program = str(program)
            group_number += 1
        else:
            group_program = str(group_program)
            group_number += 0

        # get key name
        group_name = 'Group{0:03d}'.format(group_number)
        # add run to group
        if group_name not in groups:
            groups[group_name] = [runs[runn]]
        else:
            groups[group_name].append(runs[runn])
    # return group runs
    return groups


def parallelize(groups, max_number):
    new_groups = OrderedDict()

    for group_name in groups:
        # get the length of groups
        group_length = len(groups[group_name])
        # get the max length of sub groups
        max_length = int(np.ceil(group_length / max_number))
        # set up the iteration
        sub_group = []
        # loop around elements in this group
        for element in groups[group_name]:
            if group_name not in new_groups:
                new_groups[group_name] = []
            # end group if longer than max_number
            if len(sub_group) >= max_length:
                new_groups[group_name].append(sub_group)
                sub_group = []
            # append to next group
            sub_group.append(element)
        # make sure to add last group!
        new_groups[group_name].append(sub_group)
    # return new groups with subgroups
    return new_groups


def make_subgroup_dict(sub_group, group_name):
    sruns = OrderedDict()
    for it, element in enumerate(sub_group):
        # construct name for run
        sname = '{0}-{1:03d}'.format(group_name, it)
        sruns[sname] = element
    return sruns


def run_parallel(p, runs, recipe, night_name):
    # make parallel runs
    pruns = dict()
    for jt, run_it in enumerate(runs):
        pruns['RUN{0}'.format(jt)] = [recipe] + run_it
    # ----------------------------------------------------------------------
    # group runs (for parallelisation)
    # ----------------------------------------------------------------------
    # get groups that can be run in parallel
    groups = group_runs(pruns)
    # split groups by max number of processes
    groups = parallelize(groups, MAX_PROCESSES)
    # loop around groups
    for group_name in groups:
        # process storage
        pp = []

        print('GROUP = {0}'.format(group_name))
        # loop around sub groups (to be run at the same time)
        for sub_group in groups[group_name]:
            # make sub_group a dict
            sruns = make_subgroup_dict(sub_group, group_name)
            print('', sruns)
            # do parallel run
            process = Process(target=unit_wrapper, args=(p, sruns))
            process.start()
            pp.append(process)
        # do not continue until
        for process in pp:
            while process.is_alive():
                pass
    return []


def unit_wrapper(p, runs):
    # storage for times
    times = OrderedDict()
    errors = OrderedDict()
    # log the start of the unit tests
    spirouUnitTests.unit_log_title(p)
    # loop around runs and process each
    for runn in list(runs.keys()):
        # try to run
        try:
            # do run
            rargs = [p, runn, runs[runn], times]
            times = spirouUnitTests.manage_run(*rargs)
        # Manage unexpected errors
        except Exception as e:
            wmsgs = ['Run "{0}" had an unexpected error:'.format(runn)]
            for msg in str(e).split('\n'):
                wmsgs.append('\t' + msg)
            WLOG(p, 'warning', wmsgs)
            errors[runn] = str(e)
        # Manage expected errors
        except SystemExit as e:
            wmsgs = ['Run "{0}" had an expected error:'.format(runn)]
            for msg in str(e).split('\n'):
                wmsgs.append('\t' + msg)
            WLOG(p, 'warning', wmsgs)
            errors[runn] = str(e)

    # make sure all plots are closed
    sPlt.closeall()
    # return times
    return times, errors


# =============================================================================
# trigger functions
# =============================================================================
def trigger_preprocess(p, filelist):
    recipe = 'cal_preprocess_spirou'
    # define path to raw folder
    rawpath = p['DRS_DATA_RAW']
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
            WLOG(p, 'warning', wmsgs)
            # run preprocess
            try:
                args = [night_names[it], rawfilename]
                llrun = cal_preprocess_spirou.main(*args)
                # keep only some parameters
                pp = ParamDict()
                pp['RECIPE'] = recipe
                pp['NIGHT_NAME'] = night_names[it]
                pp['ARGS'] = rawfilename
                pp['ERROR'] = list(llrun['p']['LOGGER_ERROR'])
                pp['WARNING'] = list(llrun['p']['LOGGER_WARNING'])
                pp['OUTPUTS'] = dict(llrun['p']['OUTPUTS'])
                lls.append(pp)
                del llrun
            # Manage unexpected errors
            except Exception as e:
                wmsgs = ['PPRun "{0}" had an unexpected error:'.format(it)]
                for msg in str(e).split('\n'):
                    wmsgs.append('\t' + msg)
                WLOG(p, 'warning', wmsgs)
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
                WLOG(p, 'warning', wmsgs)
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
    skip = False
    for it, index_file in enumerate(index_files):
        # if skip then continue
        if skip:
            continue
        # Get the night name for this recipes
        night_name = night_names[it]
        # if night name not in list continue
        if DATES is not None:
            if night_name.replace('/', '') not in DATES:
                continue

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
        WLOG(p, 'warning', wmsgs)
        # get the control and index for this
        control, vindex = get_control_index(fullcontrol, index_file, recipe,
                                            fdprtypes, fobjnames)
        # make sure MJDATE is float
        vindex[DATECOL] = np.array(vindex[DATECOL]).astype(float)

        # deal with recipes that need custom arguments
        if recipe == 'obj_fit_tellu_db':
            custom_args = [1, ','.join(fobjnames)]
        else:
            custom_args = None

        # make the runs
        runs = trigger_runs(p, recipe, night_name, control, vindex,
                            custom_args)
        # update recipe names (fudge)
        if recipe == 'cal_HC_E2DS_spirou':
            recipe1 = 'cal_HC_E2DS_EA_spirou'
        elif recipe == 'cal_WAVE_E2DS_spirou':
            recipe1 = 'cal_WAVE_E2DS_EA_spirou'
        elif recipe == 'obj_mk_tellu_db' or recipe == 'obj_fit_tellu_db':
            recipe1 = str(recipe)
            night_name = None
            skip = True
        else:
            recipe1 = str(recipe)
        # manage the running of this recipe
        if TEST_RUN:
            print_runs(p, runs, recipe1, logonly=False)
        elif PARALLEL:
            print_runs(p, runs, recipe1, logonly=True)
            lls = run_parallel(p, runs, recipe1, night_name)
        else:
            print_runs(p, runs, recipe1, logonly=True)
            lls = manage_runs(p, lls, runs, recipe1, night_name)
    # return local spaces and errors
    return lls


def trigger_runs(p, recipe, night_name, control, vindex,
                 custom_args=None):
    # define groups of different objects
    groups = get_groups(vindex)

    # manually deal with recipes separately # TODO: change
    if recipe == 'cal_BADPIX_spirou':
        return cal_badpix_spirou(p, night_name, vindex, groups)

    if recipe == 'cal_DARK_spirou':
        return cal_dark_spirou(p, night_name, vindex, groups)

    if recipe == 'cal_loc_RAW_spirou':
        return cal_loc_raw_spirou(p, night_name, vindex, groups)

    if recipe == 'cal_SLIT_spirou':
        return cal_slit_spirou(p, night_name, vindex, groups)

    if recipe == 'cal_SHAPE_spirou':
        return cal_shape_spirou(p, night_name, vindex, groups)

    if recipe == 'cal_FF_RAW_spirou':
        return cal_ff_raw_spirou(p, night_name, vindex, groups)

    if recipe == 'cal_extract_RAW_spirou':
        return cal_extract_raw_spirou(p, night_name, vindex, groups)

    if recipe == 'cal_HC_E2DS_spirou':
        return cal_hc_e2ds_ea_spirou(p, night_name, vindex, groups)

    if recipe == 'cal_WAVE_E2DS_spirou':
        return cal_wave_e2ds_ea_spirou(p, night_name, vindex, groups)

    if recipe == 'obj_mk_tellu':
        return obj_mk_tellu(p, night_name, vindex, groups)

    if recipe == 'obj_mk_tellu_db':
        return [[]]

    if recipe == 'obj_fit_tellu_db':
        return [custom_args]

    if recipe == 'obj_fit_tellu':
        return obj_fit_tellu(p, night_name, vindex, groups)

    WLOG(p, 'warning', 'Error Recipe={0} not defined'.format(recipe))
    return []


# =============================================================================
# recipe functions
# =============================================================================
def cal_badpix_spirou(p, night_name, vindex, groups):
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
        WLOG(p, 'warning', 'DARK_DARK not in groups')
        return []

    # get the flat_flat files
    if 'FLAT_FLAT' in groups:
        flat_groups = groups['FLAT_FLAT']
        flat_dates = get_group_vindex(vindex, flat_groups, DATECOL)
        flat_files = get_group_vindex(vindex, flat_groups, 'FILENAME')
        num_flat_groups = len(dark_dates)
        mean_flat_dates = get_group_mean(flat_dates)
    else:
        WLOG(p, 'warning', 'FLAT_FLAT not in groups')
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


def cal_dark_spirou(p, night_name, vindex, groups):
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
        WLOG(p, 'warning', 'DARK_DARK not in groups')
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


def cal_loc_raw_spirou(p, night_name, vindex, groups):
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
        WLOG(p, 'warning', 'Must have FLAT_DARK or DARK_FLAT files in group')
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


def cal_slit_spirou(p, night_name, vindex, groups):
    # get the dark_dark files
    if 'FP_FP' in groups:
        fp_fp_groups = groups['FP_FP']
        fp_fp_files = get_group_vindex(vindex, fp_fp_groups, 'FILENAME')
        num_fp_fp_groups = len(fp_fp_files)
    else:
        WLOG(p, 'warning', 'FP_FP not in groups')
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


def cal_shape_spirou(p, night_name, vindex, groups):
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
        WLOG(p, 'warning', 'FP_FP not in groups')
        return []

    if 'HCONE_HCONE' in groups:
        hc_hc_groups = groups['HCONE_HCONE']
        hc_hc_files = get_group_vindex(vindex, hc_hc_groups, 'FILENAME')
        hc_hc_dates = get_group_vindex(vindex, hc_hc_groups, DATECOL)
        num_hc_hc_groups = len(hc_hc_files)
        mean_hc_hc_dates = get_group_mean(hc_hc_dates)
    else:
        WLOG(p, 'warning', 'HCONE_HCONE not in groups')
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


def cal_ff_raw_spirou(p, night_name, vindex, groups):
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
        WLOG(p, 'warning', 'FLAT_FLAT not in groups')
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


def cal_extract_raw_spirou(p, night_name, vindex, groups):
    """
    for cal_extract_raw_spirou we just separate files and run each
    separately
    """
    reducedpath = p['DRS_DATA_REDUC']
    # get the dark_dark files
    filelist = []
    for group in groups:
        file_groups = groups[group]
        for subgroup in file_groups:
            filelist += get_group_vindex(vindex, subgroup, 'FILENAME')
    # -------------------------------------------------------------------------
    # skip done
    if SKIP_DONE_EXTRACT:
        filelist2 = []
        skipped_number = 0
        for num in range(len(filelist)):
            filename2ab = filelist[num].replace('.fits', '_e2ds_AB.fits')
            filename2a = filelist[num].replace('.fits', '_e2ds_A.fits')
            filename2b = filelist[num].replace('.fits', '_e2ds_B.fits')
            filename2c = filelist[num].replace('.fits', '_e2ds_C.fits')
            abspath_ab = os.path.join(reducedpath, night_name, filename2ab)
            abspath_a = os.path.join(reducedpath, night_name, filename2a)
            abspath_b = os.path.join(reducedpath, night_name, filename2b)
            abspath_c = os.path.join(reducedpath, night_name, filename2c)
            # check existence
            cond1 = not os.path.exists(abspath_ab)
            cond2 = not os.path.exists(abspath_a)
            cond3 = not os.path.exists(abspath_b)
            cond4 = not os.path.exists(abspath_c)
            # append file if not in existence
            if cond1 or cond2 or cond3 or cond4:
                filelist2.append(filelist[num])
            else:
                skipped_number += 1
        WLOG(p, '', 'Skipped {0} files'.format(skipped_number))
    else:
        filelist2 = list(filelist)
    # -------------------------------------------------------------------------
    # runs
    runs = []
    # push all from group into file
    for num in range(len(filelist2)):
        myrun = [night_name, filelist2[num]]
        runs.append(myrun)
    # return runs
    return runs


def cal_hc_e2ds_ea_spirou(p, night_name, vindex, groups):
    """
    for cal_shape_spirou2 we need to match hc groups to fp groups
    we need to use the last hc of a group and all but the first fp_fp in a
    sequence (unless there is only fp_fp file)

    for cal_hc_e2ds_ea_spirou we need to get hc files and add the e2ds code
    for fiber AB and C
    """
    if 'HCONE_HCONE' in groups:
        hc_hc_groups = groups['HCONE_HCONE']
        hc_hc_files = get_group_vindex(vindex, hc_hc_groups, 'FILENAME')
        if SKIP_DONE_HC_WAVE:
            path = os.path.join(p['DRS_DATA_REDUC'], night_name)
            hc_hc_files = get_group_skip(hc_hc_files, path, '.fits',
                                         '_wave_ea_AB.fits')
            hc_hc_files = get_group_skip(hc_hc_files, path, '.fits',
                                         '_wave_ea_C.fits')
        num_hc_hc_groups = len(hc_hc_files)
        hc_EAB_files = get_group_replace(hc_hc_files, '.fits', INPUT_HC_AB)
        hc_EC_files = get_group_replace(hc_hc_files, '.fits', INPUT_HC_C)
    else:
        WLOG(p, 'warning', 'HCONE_HCONE not in groups')
        return []
    # -------------------------------------------------------------------------
    # runs
    runs = []
    # match dark groups and flat groups
    for num in range(num_hc_hc_groups):
        # create run for HC E2DS AB file
        myrun = [night_name, hc_EAB_files[num][-1]]
        runs.append(myrun)
        # create run for HC E2DS C file
        myrun = [night_name, hc_EC_files[num][-1]]
        runs.append(myrun)

    # return runs
    return runs


def cal_wave_e2ds_ea_spirou(p, night_name, vindex, groups):
    """
    for cal_shape_spirou2 we need to match hc groups to fp groups
    we need to use the last hc of a group and all but the first fp_fp in a
    sequence (unless there is only fp_fp file)

    for cal_hc_e2ds_ea_spirou we need to get hc files and add the e2ds code
    for fiber AB and C
    """
    # get the dark_dark files
    if 'FP_FP' in groups:
        fp_fp_groups = groups['FP_FP']
        fp_fp_files = get_group_vindex(vindex, fp_fp_groups, 'FILENAME')
        if SKIP_DONE_WAVE_WAVE:
            path = os.path.join(p['DRS_DATA_REDUC'], night_name)
            fout = get_group_skip(fp_fp_files, path, '.fits',
                                  '_wave_ea_AB.fits',
                                  fp_fp_groups)
            fp_fp_groups, fp_fp_files = fout
        fp_fp_dates = get_group_vindex(vindex, fp_fp_groups, DATECOL)
        num_fp_fp_groups = len(fp_fp_files)
        mean_fp_fp_dates = get_group_mean(fp_fp_dates)
        fp_EAB_files = get_group_replace(fp_fp_files, '.fits', INPUT_WAVE_AB)
        fp_EC_files = get_group_replace(fp_fp_files, '.fits', INPUT_WAVE_C)
    else:
        WLOG(p, 'warning', 'FP_FP not in groups')
        return []

    if 'HCONE_HCONE' in groups:
        hc_hc_groups = groups['HCONE_HCONE']
        hc_hc_files = get_group_vindex(vindex, hc_hc_groups, 'FILENAME')
        if SKIP_DONE_WAVE_WAVE:
            path = os.path.join(p['DRS_DATA_REDUC'], night_name)
            hout = get_group_skip(hc_hc_files, path, '.fits',
                                  '_wave_ea_AB.fits', hc_hc_groups)
            hc_hc_groups, hc_hc_files = hout
        hc_hc_dates = get_group_vindex(vindex, hc_hc_groups, DATECOL)
        num_hc_hc_groups = len(hc_hc_files)
        mean_hc_hc_dates = get_group_mean(hc_hc_dates)
        hc_EAB_files = get_group_replace(hc_hc_files, '.fits', INPUT_WAVE_AB)
        hc_EC_files = get_group_replace(hc_hc_files, '.fits', INPUT_WAVE_C)

    else:
        WLOG(p, 'warning', 'HCONE_HCONE not in groups')
        return []
    # runs
    runs = []
    # match dark groups and flat groups
    for num in range(num_hc_hc_groups):
        # find dark group closest
        date_dist = mean_hc_hc_dates[num] - np.array(mean_fp_fp_dates)
        pos = int(np.argmin(np.abs(date_dist)))

        myrun = [night_name, fp_EAB_files[pos][-1], hc_EAB_files[num][-1]]
        runs.append(myrun)
        myrun = [night_name, fp_EC_files[pos][-1], hc_EC_files[num][-1]]
        runs.append(myrun)

    # return runs
    return runs


def obj_fit_tellu(p, night_name, vindex, groups):
    """
    for obj_fit_tellu any file can be used but must be _e2dsff_AB.fits
    """
    reducedpath = p['DRS_DATA_REDUC']
    extension = '_e2dsff_AB_tellu_corrected.fits'
    # get the dark_dark files
    filelist = []
    objnamelist = []
    for group in groups:
        file_groups = groups[group]
        for subgroup in file_groups:
            filelist += get_group_vindex(vindex, subgroup, 'FILENAME')
            objnamelist += get_group_vindex(vindex, subgroup, 'OBJNAME')
    # -------------------------------------------------------------------------
    # skip done
    if SKIP_DONE_FIT_TELLU:
        filelist2, objnamelist2 = [], []
        for num in range(len(filelist)):
            filename2ab = filelist[num].replace('.fits', extension)
            abspath_ab = os.path.join(reducedpath, night_name, filename2ab)
            # append file if not in existence
            if not os.path.exists(abspath_ab):
                filelist2.append(filelist[num])
                objnamelist2.append(objnamelist[num])
    else:
        filelist2, objnamelist2 = list(filelist), list(objnamelist)
    # -------------------------------------------------------------------------
    # change filenames to e2ds_ab
    filelist3 = []
    for num in range(len(filelist2)):
        # select objects only
        if not filelist[num].endswith('o_pp.fits'):
            continue
        # select objects only (not sky)
        if 'sky' in objnamelist2[num]:
            continue
        else:
            filename3 = filelist2[num].replace('.fits', INPUT_FIT_TELLU)
            filelist3.append(filename3)
    # runs
    runs = []
    # push all from group into file
    for num in range(len(filelist3)):
        myrun = [night_name, filelist3[num]]
        runs.append(myrun)
    # return runs
    return runs


def obj_mk_tellu(p, night_name, vindex, groups):
    """
    for obj_mk_tellu any file with objname in the telluric list is valid
    and must be _e2dsff_AB.fits
    """
    reducedpath = p['DRS_DATA_REDUC']
    extension = '_e2dsff_AB_trans.fits'
    # get the dark_dark files
    filelist = []
    objnamelist = []
    for group in groups:
        file_groups = groups[group]
        for subgroup in file_groups:
            filelist += get_group_vindex(vindex, subgroup, 'FILENAME')
            objnamelist += get_group_vindex(vindex, subgroup, 'OBJNAME')
    # -------------------------------------------------------------------------
    # skip done
    if SKIP_DONE_MK_TELLU:
        filelist2, objnamelist2 = [], []
        for num in range(len(filelist)):
            filename2ab = filelist[num].replace('.fits', extension)
            abspath_ab = os.path.join(reducedpath, night_name, filename2ab)
            # append file if not in existence
            if not os.path.exists(abspath_ab):
                filelist2.append(filelist[num])
                objnamelist2.append(objnamelist[num])
    else:
        filelist2, objnamelist2 = list(filelist), list(objnamelist)
    # -------------------------------------------------------------------------
    # change filenames to e2ds_ab
    filelist3 = []
    for num in range(len(filelist2)):
        # select objects only
        if not filelist2[num].endswith('o_pp.fits'):
            continue
        if objnamelist2[num] not in TELL_WHITELIST:
            continue
        else:
            filename3 = filelist2[num].replace('.fits', INPUT_MK_TELLU)
            filelist3.append(filename3)
    # runs
    runs = []
    # push all from group into file
    for num in range(len(filelist3)):
        myrun = [night_name, filelist3[num]]
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


def get_group_replace(group, replace1, replace2):
    outgroup = []
    for group_it in group:
        outgroup_it = []
        for file_it in group_it:
            outfile = file_it.replace(replace1, replace2)
            outgroup_it.append(outfile)
        outgroup.append(outgroup_it)
    return outgroup


def report_errors(p, errors, recipe):
    if len(errors) > 0:
        WLOG(p, 'warning', '')
        WLOG(p, 'warning', '{0} Errors:'.format(recipe))
        WLOG(p, 'warning', '')
        for key in errors:
            error = errors[key]
            WLOG(p, 'warning', error)


def get_group_skip(group, path, replace1, replace2, groups=None):
    outgroups, outfiles = [], []
    for it, group_it in enumerate(group):
        outfile_it, outgroup_it = [], []
        for jt, file_it in enumerate(group_it):
            testfile = file_it.replace(replace1, replace2)
            testpath = os.path.join(path, testfile)
            if not os.path.exists(testpath):
                outfile_it.append(file_it)
                if groups is not None:
                    outgroup_it.append(groups[it][jt])
        outgroups.append(outgroup_it)
        outfiles.append(outfile_it)
    if groups is not None:
        return outgroups, outfiles
    else:
        return outfiles


def strip_names(innames):
    outnames = []
    for inname in innames:
        outnames.append(inname.strip())
    return outnames


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

    # clear run number and test store
    global RUNNUMBER
    global TEST_STORE
    RUNNUMBER = 0
    TEST_STORE = []

    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)
    p = spirouStartup.LoadArguments(p, night_name, require_night_name=False)

    loc = ParamDict()

    # send email if configured
    send_email(p, kind='start')

    # ----------------------------------------------------------------------
    # Check pre-processing
    # ----------------------------------------------------------------------
    raw_files = find_all_raw_files(p)
    n_raw = len(raw_files)
    # check for pre-processed files
    if SKIP_DONE_PP:
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
    elif not SKIP_DONE_PP or n_raw == 0:
        wmsg = 'No raw files found'
        WLOG(p, 'warning', wmsg)
        pp_lls = [None, dict()]
    else:
        wmsg = 'All files pre-processed (Found {0} files)'
        WLOG(p, '', wmsg.format(n_raw))
        pp_lls = [None, dict()]

    # report pp errors
    report_errors(p, pp_lls[1], 'cal_preprocess')

    # ----------------------------------------------------------------------
    # Load the recipe_control
    # ----------------------------------------------------------------------
    loc['CONTROL'] = spirouImage.spirouFile.get_control_file(p)
    loc.set_source('CONTROL', main_name)

    # ----------------------------------------------------------------------
    # Find raw index_files
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
    WLOG(p, '', 'Running triggers')
    all_lls = OrderedDict()

    # 1. cal_BADPIX_spirou.py
    if RUN_BADPIX:
        lls = trigger_main(p, loc, recipe='cal_BADPIX_spirou')
        all_lls['cal_BADPIX_spirou'] = lls
    # 2. cal_DARK_spirou.py
    if RUN_DARK:
        lls = trigger_main(p, loc, recipe='cal_DARK_spirou')
        all_lls['cal_DARK_spirou'] = lls
    # 3. cal_loc_RAW_spirou.py
    if RUN_LOC:
        lls = trigger_main(p, loc, recipe='cal_loc_RAW_spirou')
        all_lls['cal_loc_RAW_spirou'] = lls
    # 4. cal_SLIT_spirou.py
    if RUN_SLIT:
        lls = trigger_main(p, loc, recipe='cal_SLIT_spirou')
        all_lls['cal_SLIT_spirou'] = lls
    # 5. cal_SHAPE_spirou.py
    if RUN_SHAPE:
        lls = trigger_main(p, loc, recipe='cal_SHAPE_spirou')
        all_lls['cal_SHAPE_spirou'] = lls
    # 6. cal_FF_RAW_spirou.py
    if RUN_FLAT:
        lls = trigger_main(p, loc, recipe='cal_FF_RAW_spirou')
        all_lls['cal_FF_RAW_spirou'] = lls
    # 7. cal_extract_RAW_spirou.py (HCONE_HCONE, FP_FP)
    if RUN_EXTRACT_HCFP:
        lls = trigger_main(p, loc, recipe='cal_extract_RAW_spirou',
                           fdprtypes=['HCONE_HCONE', 'FP_FP'])
        all_lls['cal_extract_RAW_spirou (HC/FP)'] = lls
    # 8. get cal hc wave solutions
    if RUN_HC_WAVE:
        lls = trigger_main(p, loc, recipe='cal_HC_E2DS_spirou')
    # 9. get cal hc wave solutions
    if RUN_WAVE_WAVE:
        lls = trigger_main(p, loc, recipe='cal_WAVE_E2DS_spirou')
    # 10. extract tellurics
    if RUN_EXTRACT_TELLU:
        lls = trigger_main(p, loc, recipe='cal_extract_RAW_spirou',
                           fdprtypes=['OBJ_FP', 'OBJ_DARK'],
                           fobjnames=TELL_WHITELIST)
        all_lls['cal_extract_RAW_spirou (TELLU)'] = lls
    # 11. extract objects
    if RUN_EXTRACT_OBJ:
        lls = trigger_main(p, loc, recipe='cal_extract_RAW_spirou',
                           fdprtypes=['OBJ_FP', 'OBJ_DARK'],
                           fobjnames=SCIENCE_TARGETS)
        all_lls['cal_extract_RAW_spirou (OBJ)'] = lls
    # 12. extract objects
    if RUN_EXTRACT_ALL:
        lls = trigger_main(p, loc, recipe='cal_extract_RAW_spirou',
                           fdprtypes=['OBJ_FP', 'OBJ_DARK'])
        all_lls['cal_extract_RAW_spirou (OBJ)'] = lls
    # 12. extract objects
    if RUN_EXTRACT_DARK:
        lls = trigger_main(p, loc, recipe='cal_extract_RAW_spirou',
                           fdprtypes=['DARK_DARK'])
        all_lls['cal_extract_RAW_spirou (DARK)'] = lls
    # 13. get cal hc wave solutions
    if RUN_OBJ_MK_TELLU:
        lls = trigger_main(p, loc, recipe='obj_mk_tellu_db')
        all_lls['obj_mk_tellu_db'] = lls

    # 14. get cal hc wave solutions
    if RUN_OBJ_FIT_TELLU:
        lls = trigger_main(p, loc, recipe='obj_fit_tellu_db',
                           fobjnames=SCIENCE_TARGETS)
        all_lls['obj_fit_tellu (OBJ)'] = lls

    # if test run print report
    if TEST_RUN:
        print('\n\n')
        print('TEST RUN LIST:')
        print('\n\n')
        for line in TEST_STORE:
            print(line)
        print('\n\n')
    # ----------------------------------------------------------------------
    # report errors
    # ----------------------------------------------------------------------
    for recipe in all_lls:
        if len(all_lls[recipe]) == 2:
            errors = all_lls[recipe][1]
            report_errors(p, errors, recipe)

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    p = spirouStartup.End(p, outputs=None)

    # send email if configured
    send_email(p, kind='end')

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
