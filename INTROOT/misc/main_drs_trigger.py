#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cal_BADPIX_spirou.py [night_directory] [flat_flat_*.fits] [dark_dark_*.fits]

Recipe to generate the bad pixel map

Created on 2017-12-06 at 14:50

@author: cook

Last modified: 2017-12-11 at 15:23

Up-to-date with cal_BADPIX_spirou AT-4 V47
"""
from __future__ import division
import numpy as np
import os
import sys
import importlib
import glob

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouStartup

from SpirouDRS.spirouCore import spirouMath
from SpirouDRS.spirouImage import spirouFile
from SpirouDRS.spirouUnitTests import spirouUnitRecipes

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'main_drs_trigger.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
printc = spirouCore.PrintColour
# ----------------------------------------------------------------------
HISTORY_FILE_NAME = 'HISTORY.txt'

FORCE_REDO = False


# =============================================================================
# Define functions
# =============================================================================
def main(night_name=None):
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin()
    p = spirouStartup.LoadArguments(p, night_name=night_name)

    # ----------------------------------------------------------------------
    # Get raw fits file in ARG_FILE_DIR
    # ----------------------------------------------------------------------
    files, nights = get_valid_files(p)

    # ----------------------------------------------------------------------
    # Get control and imports
    # ----------------------------------------------------------------------
    # get control and imports
    control, imports = get_recipes(p, raw_only=True)

    # ----------------------------------------------------------------------
    # identify files we have for each recipe
    # ----------------------------------------------------------------------
    # get requirements from control for each recipe
    requirements = get_requirements(p, control)
    # check files
    runs, missed = get_runs(requirements, files, nights)

    # ----------------------------------------------------------------------
    # For each night name ID when we don't have a full set
    # ----------------------------------------------------------------------
    # get the warning and error colours
    w1, w2 = printc('warning')
    e1, e2 = printc('error')
    if len(missed) > 0:
        for miss in missed:
            wargs = [w1, miss[1], miss[0], w2]
            wmsg = 'Could not find required files for {1} in {2}'
            WLOG('warning', p['LOG_OPT'], wmsg.format(*wargs))
        eargs = [e1, e2]
        wmsg = '{0}\tContinue? [Y]es or [N]o?\t{1}'.format(*eargs)
        # require user input
        print('\n')
        if sys.version_info.major < 3:
            # noinspection PyUnresolvedReferences
            uinput = raw_input(wmsg)
        else:
            uinput = input(wmsg)
        # line break
        print('\n')
        if 'N' in uinput.upper():
            wmsg = 'Code ended by user'
            WLOG('error', p['LOG_OPT'], wmsg)


    # ----------------------------------------------------------------------
    # Run given recipes
    # ----------------------------------------------------------------------
    # sort groups by name (assumes all nights will be alphabetical
    run_order = np.sort(list(runs.keys()))
    # loop around group (night name)
    for g_it in range(len(run_order)):
        # get group
        group = run_order[g_it]
        # get this run
        runi = runs[group]
        # check and add to history
        skip = add_to_history(p, group, runi)
        # if skip then skip
        if skip:
            wmsg = '\t Skipped run (Already processed group={0})'
            WLOG('', '', wmsg.format(group))
            continue
        # loop around run in runs
        for it in range(len(runi)):
            try:
                # display progress
                iteration_bar(p, g_it, len(run_order), it, len(runi))
                # get function from runs
                name = runi[it][0]
                # run function
                args, name = spirouUnitRecipes.wrapper(p, name, inputs=runi[it])
                ll = spirouUnitRecipes.run_main(p, name, args)
            # Skip any exit errors
            except SystemExit:
                continue

    # clear some lines
    WLOG('', '', '')
    WLOG('', '', '=' * 50)
    WLOG('', '', '')

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    wmsg = 'Recipe {0} has been successfully completed'
    WLOG('info', p['LOG_OPT'], wmsg.format(p['PROGRAM']))
    # return a copy of locally defined variables in the memory
    return dict(locals())


def get_night_name(p, directory):
    night_name = directory.split(p['DRS_DATA_RAW'])[-1][len(os.path.sep):]
    return night_name


def get_valid_files(p):
    # get all files in the ARG_FILE_DIR
    if p['ARG_NIGHT_NAME'] == '':
        all_files, all_night_names = get_all_files(p)
    else:
        all_files = os.listdir(p['ARG_FILE_DIR'])
        all_night_names = [p['ARG_NIGHT_NAME']] * len(all_files)
    # loop around files and get valid files
    files, night_names = [], []
    for f_it in range(len(all_files)):
        # get this iterations values
        filename = all_files[f_it]
        night_name = all_night_names[f_it]
        # get base filename
        basefilename = os.path.basename(filename)
        # if we are forcing preprocess should check for pp files
        if p['IC_FORCE_PREPROCESS']:
            # only add pre-processed files
            if p['PROCESSED_SUFFIX'] in basefilename:
                files.append(basefilename)
                night_names.append(night_name)
        else:
            # only add '.fits' files
            if '.fits' in basefilename:
                files.append(basefilename)
                night_names.append(night_name)
    # if we have no files cause exception
    if len(files) == 0:
        if p['IC_FORCE_PREPROCESS']:
            emsgs = ['No valid pre-processed files found in {0}'
                     ''.format(p['ARG_FILE_DIR'])]
            emsgs.append('\tFiles need suffix={0} (Please run '
                         'cal_preprocessing)'.format(p['PROCESSED_SUFFIX']))
        else:
             emsgs = ['No valid ".fits" files found in {0}'
                     ''.format(p['ARG_FILE_DIR'])]
        WLOG('error', p['LOG_OPT'], emsgs)
    # return file list
    return files, night_names


def get_all_files(p):
    # define search path
    search_path = os.path.join(p['DRS_DATA_RAW'], '**')
    # get all files
    rawfiles = glob.glob(search_path, recursive=True)
    # loop around files and sort into nights names
    files, night_names = [], []
    for rawfilename in rawfiles:
        # skip directories
        if os.path.isdir(rawfilename):
            continue
        # get base name and dir name
        basename = os.path.basename(rawfilename)
        directory = os.path.dirname(rawfilename)
        # get night name
        night_name = directory.split(p['DRS_DATA_RAW'])[-1][len(os.path.sep):]
        # append to files and night_names
        files.append(basename)
        night_names.append(night_name)
    # return files and night_names
    return files, night_names


def get_recipes(p, raw_only=True):

    control = spirouFile.get_control_file()
    # filter out negative order numbers (should not be used/checked)
    negorder = control['order'] < 0
    control = control[~negorder]

    # sort control by order
    sort = np.argsort(control['order'])
    control = control[sort]

    # only look at raw files
    if raw_only:
        mask = control['kind'] == 'RAW'
        control = control[mask]

    # only want recipes valid for our detector
    # TODO: Remove H2RG dependency
    if p['IC_IMAGE_TYPE'] == 'H2RG':
        mask = (control['det'] == 1) | (control['det'] == 2)
    else:
        mask = (control['det'] == 1) | (control['det'] == 4)
    control = control[mask]

    # get recipe names
    names = np.unique(control['Recipe'])

    # import recipes into dictionary
    import_dict = dict()

    # loop around recipe names and import the modules
    for name in names:
        if name == 'None':
            continue
        try:
            import_dict[name] = importlib.import_module(name)
        except ImportError:
            emsg1 = 'FATAL ERROR: Cannot import module="{0}"'
            emsg2 = '   Please check Recipe control file'
            WLOG('error', p['LOG_OPT'], [emsg1.format(name), emsg2])

    # return control file and import dict
    return control, import_dict


def get_requirements(p, control):

    # get constants from p
    image_type = p['IC_IMAGE_TYPE']

    # set up storage
    requirements = dict()
    # loop around the lines in control
    for row in range(len(control)):
        # get this iteration parameters
        name = control['Recipe'][row]
        number = control['number'][row]
        dstring = control['dstring'][row]
        # if recipe not in requirements add
        if name not in requirements:
            requirements[name] = dict(dstring=[dstring], number=[number])
        # else append
        else:
            requirements[name]['dstring'].append(dstring)
            requirements[name]['number'].append(number)
    # return requirements
    return requirements


def get_runs(requirements, files, nights):

    # store runs
    runs = dict()
    missed = []
    # get unique night names
    unights = np.unique(nights)
    # loop around unique night names
    for unight in unights:
        runs[unight] = []
        # create list of files for this unight
        mask = np.array(nights) == unight
        nfiles = np.array(files)[mask]
        # loop through recipes
        for name in list(requirements.keys()):
            # get this iterations requirement
            requirement = requirements[name]
            unumbers = np.unique(requirement['number'])
            dstrings = requirement['dstring']
            # -----------------------------------------------------------------
            # We need to deal with different ways to run recipes
            # -----------------------------------------------------------------
            # Way 1: recipe requires 1 run with 1 suffix
            if len(unumbers) == 1 and len(dstrings) == 1:
                ufiles = recipe_mode_1(requirement, nfiles)
            # Way 2: recipe requires 1 run with multiple suffices
            elif len(unumbers) == 1 and len(dstrings) > 1:
                ufiles = recipe_mode_2(requirement, nfiles)
            # Way 3: recipe requires multiple runs with multiple suffices
            elif len(unumbers) > 1 and len(dstrings) > 1:
                ufiles = recipe_mode_3(requirement, nfiles)
            else:
                ufiles = []
            # append ufiles to run
            if len(ufiles) > 0:
                for ufile in ufiles:
                    if type(ufile) not in [list, np.ndarray]:
                        ufile = [ufile]
                    runs[unight].append([name, unight] + ufile)
            else:
                missed.append([unight, name])
    # return runs and names
    return runs, missed


def recipe_mode_1(req, nfiles):
    # Way 1: recipe requires 1 run with 1 suffix

    # get suffix (should only be 1)
    suffix = req['dstring'][0]
    # storage for usable filenames
    ufiles = []
    # if suffix == 'None use all files
    if suffix == 'None':
        return list(nfiles)
    # loop around files and add files that have this suffix
    for filename in nfiles:
        if suffix in filename:
            ufiles.append(str(filename))
    # return files as a single list entry
    if len(ufiles) == 0:
        return []
    else:
        return [ufiles]


def recipe_mode_2(req, nfiles):
    # Way 2: recipe requires 1 run with multiple suffices
    suffices = req['dstring']
    # if None in suffices use all files
    if None in suffices:
        for filename in nfiles:
            runs = [str(filename)]
    else:
        runs = []
        # loop around suffixes
        for suffix in suffices:
            ufiles = []
            # loop around files and add files that have this suffix
            for filename in nfiles:
                if suffix in filename:
                    ufiles.append(str(filename))
            if len(ufiles) > 0:
                runs.append(ufiles)
    # return runs
    return runs


def recipe_mode_3(req, nfiles):
    # Way 4: recipe requires multiple runs with multiple suffices
    suffices = req['dstring']
    sfiles = []
    # loop around suffixes
    for suffix in suffices:
        ufiles = []
        # loop around files and add files that have this suffix
        for filename in nfiles:
            if suffix in filename:
                ufiles.append(str(filename))
            elif suffix == 'None':
                ufiles.append(str(filename))
        sfiles.append(ufiles)
    if len(sfiles) == 0:
        return []
    # should just use the first one of each argument
    only_run = []
    for s_it in range(len(suffices)):
        try:
            only_run.append(str(sfiles[s_it][0]))
        except IndexError:
            return []
    # return runs
    return [only_run]


def iteration_bar(p, it_number1, t_number1, it_number2, t_number2):
    WLOG('', '', '')
    WLOG('', '', '=' * 50)
    wmsg1 = 'Processing Group {0} of {1}'.format(it_number1 + 1, t_number1)
    wmsg2 = '           Run {0} of {1}'.format(it_number2 + 1, t_number2)
    WLOG('', p['LOG_OPT'], [wmsg1, wmsg2])
    WLOG('', '', '=' * 50)
    WLOG('', '', '')


def add_to_history(p, night_name, runs):
    # get directory for run
    dir = os.path.join(p['DRS_DATA_RAW'], night_name)
    # check it exists
    if not os.path.exists(dir):
        emsg1 = 'Directory "{0}" does not exist'.format(dir)
        emsg2 = '\tSomething wrong with night name={0}?'.format(night_name)
        WLOG('error', p['LOG_OPT'], [emsg1, emsg2])

    # construct filename
    filename = os.path.join(dir, HISTORY_FILE_NAME)

    # if file in directory delete it
    if os.path.exists(filename):
        if not FORCE_REDO:
            return True
        else:
            os.remove(filename)

    # construct history
    lines = []
    # add version
    lines.append('\n' + spirouStartup.spirouStartup.HEADER + '\n')
    lines.append(' * Automated run information')
    lines.append('\n' + spirouStartup.spirouStartup.HEADER + '\n')
    lines.append('\n')
    lines.append('\n DRS VERSION = {0}\n'.format(p['DRS_VERSION']))
    # get the time format and display time zone from constants
    tfmt = spirouConfig.Constants.DATE_FMT_CALIBDB()
    zone = spirouConfig.Constants.LOG_TIMEZONE()
    # Get the time now in human readable format
    human_time = spirouMath.get_time_now_string(fmt=tfmt, zone=zone)
    # add time now
    lines.append('\n DATE = {0}\n'.format(human_time))
    # add the runs
    lines.append('\n RUNS EXECUTED:\n')
    lines.append('\n')
    # loop around runs and add to history
    for it in range(len(runs)):
        recipe = runs[it][0]
        nn = runs[it][1]
        files = runs[it][2]
        if type(files) != list:
            files = [files]
        args = [recipe, nn, ' '.join(files)]
        lines.append('\t{0} {1} {2}\n'.format(*args))
    # add system info
    messages = spirouStartup.spirouStartup.display_system_info(True, True)
    lines.append('\n')
    for message in messages:
        lines.append(message + '\n')

    # open file with write
    f = open(filename, 'w')
    f.writelines(lines)
    f.close()

    # we do not need to skip if we have reached this point
    return False


# =============================================================================
# Start of code
# =============================================================================
# if __name__ == "__main__":
#     # run main with no arguments (get from command line - sys.argv)
#     ll = main()
#     # exit message
#     spirouStartup.Exit(ll, has_plots=False)


# =============================================================================
# End of code
# =============================================================================
