#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
spirouStartup.py

Start up to be executed at beginning of all codes

Created on 2017-10-11 at 10:48

@author: cook

Version 0.0.1

Last modified: 2017-10-11 at 10:49
"""
from __future__ import division
import numpy as np
from astropy.time import Time
import os
import sys
import code
from collections import OrderedDict

from SpirouDRS import spirouDB
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouStartup.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# get param dict
ParamDict = spirouConfig.ParamDict
# get the config error
ConfigError = spirouConfig.ConfigError
# -----------------------------------------------------------------------------
# define string types
TYPENAMES = {int: 'integer', float: 'float', list: 'list',
             bool: 'bool', str: 'str'}
# define the print/log header divider
HEADER = ' ' + '*' * 65


# =============================================================================
# Define setup functions
# =============================================================================
def run_begin(recipe, quiet=False):
    """
    Begin DRS - Must be run at start of every recipe
    - loads the parameters from the primary configuration file, displays
      title, checks priamry constants and displays initial parameterization

    :param recipe: string, the recipe name
    :param quiet: bool, if True no messages are displayed

    :return cparams: parameter dictionary, ParamDict constants from primary
                     configuration file
            Adds the following:
                all constants in primary configuration file
                DRS_NAME: string, the name of the DRS
                DRS_VERSION: string, the version of the DRS
    """
    func_name = __NAME__ + '.run_begin()'

    # set up process id
    pid, htime = assign_pid()

    # Clean WLOG
    WLOG.clean_log(pid)
    # Get config parameters from primary file
    try:
        cparams, warn_messages = spirouConfig.ReadConfigFile()
    except ConfigError as e:
        WLOG(None, e.level, e.message)
        cparams, warn_messages = None, []
    # add process id to cparams
    cparams['PID'] = pid
    cparams.set_source('PID', func_name)
    # add date now to cparams
    cparams['DATE_NOW'] = htime
    cparams.set_source('DATE_NOW', func_name)
    cparams['DRS_DATE'] = str(__date__)
    cparams.set_source('DRS_DATE', func_name)

    # log warning messages
    if len(warn_messages) > 0:
        WLOG(cparams, 'warning', warn_messages)

    # set recipe name
    cparams['RECIPE'] = recipe.split('.py')[0]
    cparams.set_source('RECIPE', func_name)
    # set program and log_opt
    cparams['LOG_OPT'] = cparams['RECIPE']
    cparams['PROGRAM'] = cparams['RECIPE']
    cparams.set_sources(['LOG_OPT', 'PROGRAM'], func_name)
    # get variables from spirouConst
    cparams['DRS_NAME'] = spirouConfig.Constants.NAME()
    cparams['DRS_VERSION'] = spirouConfig.Constants.VERSION()
    cparams.set_sources(['DRS_NAME', 'DRS_VERSION'], 'spirouConfig.Constants')
    # display title
    if not quiet:
        display_drs_title(cparams)
    # check input parameters
    cparams = spirouConfig.CheckCparams(cparams)

    if not quiet:
        # display initial parameterisation
        display_initial_parameterisation(cparams)
        # display system info (log only)
        display_system_info(cparams)

    # if DRS_INTERACTIVE is not True and DRS_PLOT is to the screen
    #     then DRS_PLOT should be turned off too
    if not cparams['DRS_INTERACTIVE']:
        if cparams['DRS_PLOT'] == 1:
            cparams['DRS_PLOT'] = 0

    # set up array to store inputs/outputs
    cparams['INPUTS'] = OrderedDict()
    cparams['OUTPUTS'] = OrderedDict()
    source = recipe + '.main() + ' + func_name
    cparams.set_sources(['INPUTS', 'OUTPUTS'], source)

    # return parameters
    return cparams


def assign_pid():
    # get the time now from astropy
    timenow = Time.now()
    # get unix and human time from astropy time now
    unixtime = timenow.unix * 1e7
    humantime = timenow.iso
    # write pid
    pid = 'PID-{0:020d}'.format(int(unixtime))
    # return pid and human time
    return pid, humantime


def load_arguments(cparams, night_name=None, files=None, customargs=None,
                   mainfitsfile=None, mainfitsdir=None, quiet=False,
                   require_night_name=True):
    """
    Deal with loading run time arguments:

    1) display help file (if requested and exists)
    2) loads run time arguments (and custom arguments, see below)
    3) loads other config files

    :param cparams: parameter dictionary, ParamDict containing constants

    :param night_name: string or None, the name of the directory in DRS_DATA_RAW
                       to find the files in

                       if None (undefined) uses the first argument in command
                       line (i.e. sys.argv[1])

                       if defined overwrites call from
                       command line (i.e. overwrites sys.argv)

                       stored in p['ARG_NIGHT_NAME']

    :param files: list of strings or None, the files to use for this program

                  if None (undefined) uses the second and all other arguments in
                  the command line (i.e. sys.argv[2:])

                  if defined overwrites call from command line

                  stored in p['ARG_FILE_NAMES']

    :param customargs: None or list of strings, if list of strings then instead
                       of getting the standard runtime arguments

           i.e. in form:

                program.py night_dir arg_file_names[0] arg_file_names[1]...

           loads all arguments into customargs

           i.e. if customargs = ['night_dir', 'filename', 'a', 'b', 'c']
           expects command line arguments to be:

                program.py night_dir filename a b c

    :param mainfitsfile: string or None, if "customargs" is not None (i.e. if we
                         are using custom arguments) we must define one
                         of the parameters in "customargs" to be the main fits
                         file (fitsfilename and arg_file_names[0]).
                         The parameter MUST be a string, a fits file,
                         and have HEADER key defining the acquisition time
                         as defined in kw_ACQTIME_KEY in spirouKeywords.py
                         if not using custom arguments (i.e. customargs=None
                         files must be defined and these files are used
                         set fitsfilename and arg_file_names

    :param mainfitsdir: string or None, if mainfitsfile is defined and needed
                        this is the location of the mainfitsfile if None this
                        is assumed to be the raw dir folder
                        current other options are:
                            'reduced' - the DRS_DATA_REDUC folder
                            'calibdb' - the DRS_CALIB_DB folder
                            or the full path to the file

    :param require_night_name: bool, if False we do not check or need the
                               the night_name (useful for recipes that do not
                               need a night_name as input)

    :param quiet: bool, if True does not print or log messages

    :return p: dictionary, parameter dictionary
    """
    func_name = __NAME__ + '.load_arguments()'
    # -------------------------------------------------------------------------
    # deal with arg_night_name defined in call
    if night_name is not None:
        cparams['ARG_NIGHT_NAME'] = str(night_name)
        cparams.set_source('ARG_NIGHT_NAME', func_name)
    elif not require_night_name:
        cparams['ARG_NIGHT_NAME'] = ''
        cparams.set_source('ARG_NIGHT_NAME', func_name)
    # -------------------------------------------------------------------------
    # deal with run time arguments
    if customargs is None:
        cparams = run_time_args(cparams, mainfitsdir, require_night_name)
        # to log only:
        lmsg = 'args: {0}'.format(' '.join(sys.argv))
        WLOG(cparams, '', lmsg, logonly=True)

    else:
        cparams = run_time_custom_args(cparams, customargs, mainfitsdir,
                                       require_night_name)
        # to log only:
        args = []
        for customarg in customargs:
            args.append('{0}={1}'.format(customarg, customargs[customarg]))
        # to log only:
        lmsg = 'args: {0}'.format(' '.join(args))
        WLOG(cparams, '', lmsg, logonly=True)

    # -------------------------------------------------------------------------
    # deal with files being defined in call
    if files is not None:
        cparams = get_call_arg_files_fitsfilename(cparams, files,
                                                  mfd=mainfitsdir,
                                                  rnn=require_night_name)
    # if files not defined we have custom arguments and hence need to define
    #    arg_file_names and fitsfilename manually
    elif mainfitsfile is not None and customargs is not None:
        cparams = get_custom_arg_files_fitsfilename(cparams, customargs,
                                                    mainfitsfile,
                                                    mfd=mainfitsdir,
                                                    rnn=require_night_name)
    # -------------------------------------------------------------------------
    # check key parameters
    cparams = check_key_fparams(cparams)
    # -------------------------------------------------------------------------
    # Display help file if needed
    display_help_file(cparams)
    # display run file
    if customargs is None and not quiet:
        display_run_files(cparams)
    elif not quiet:
        display_custom_args(cparams, customargs)
    # -------------------------------------------------------------------------
    # load ICDP config file
    logthis = not quiet
    cparams = load_other_config_file(cparams, 'ICDP_NAME', required=True,
                                     logthis=logthis)
    # load keywords
    try:
        cparams, warnlogs = spirouConfig.GetKeywordArguments(cparams)
        # print warning logs
        for warnlog in warnlogs:
            WLOG(cparams, 'warning', warnlog)
    except spirouConfig.ConfigError as e:
        WLOG(cparams, e.level, e.message)
    # -------------------------------------------------------------------------
    # Reduced directory
    # if reduced directory does not exist create it
    if not os.path.isdir(cparams['DRS_DATA_REDUC']):
        os.makedirs(cparams['DRS_DATA_REDUC'])
    if not os.path.isdir(cparams['REDUCED_DIR']):
        os.makedirs(cparams['REDUCED_DIR'])
    if not os.path.isdir(cparams['DRS_DATA_WORKING']):
        os.makedirs(cparams['DRS_DATA_WORKING'])
    if not os.path.isdir(cparams['TMP_DIR']):
        os.makedirs(cparams['TMP_DIR'])
    if not os.path.isdir(cparams['DRS_DATA_PLOT']):
        os.makedirs(cparams['DRS_DATA_PLOT'])
    # -------------------------------------------------------------------------
    # return parameter dictionary
    return cparams


def initial_file_setup(p, files=None, calibdb=False, no_night_name=False,
                       no_files=False, skipcheck=False):
    """
    Sets up the initial files (obtained with load_arguments) for a standard run
     (i.e. requiring night_name and files) and performs checks based on the
     recipe name p['RECIPE'] to see if files are correct for this recipe. If
     calibdb is True loads the calibration database, if no_night_name is True
     no night name is required. If no files is True no files are required. If
     skipcheck is True file is not checked.

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            LOG_OPT: string, log option, normally the program name
            RECIPE: string, the recipe name (must be defined in recipe control
                    file)
            arg_night_name: string, the folder within data raw directory
                            containing files (also reduced directory) i.e.
                            /data/raw/20170710 would be "20170710"
            arg_file_names: list, list of files taken from the command line
                            (or call to recipe function) must have at least
                            one string filename in the list
            fitsfilename: string, the full path of for the main raw fits
                          file for a recipe
                          i.e. /data/raw/20170710/filename.fits

    :param files: list or None, the files passed in as arguments
                  (If None comes from ARG_FILE_NAMES)
    :param calibdb: bool, if True calibration database loaded
    :param no_night_name: bool, if True no night name expected
    :param no_files: bool, if True no files expected
    :param skipcheck: bool, if True does not check files


    :return p: parameter dictionary, the updated parameter dictionary
            Adds the following:
                DPRTYPE: string, the datatype header key
                PREPROCESSED: bool, if True file is processed (or unchecked)

    returns SystemExit if file is not valid for recipe
    """
    # func_name = __NAME__ + '.initial_file_setup()'
    recipe = p['RECIPE']
    # -------------------------------------------------------------------------
    if not no_night_name:
        # check ARG_NIGHT_NAME is not None
        if p['ARG_NIGHT_NAME'] == '':
            emsgs = ['Argument Error: No FOLDER defined at run time argument',
                     '    format must be:',
                     '    >>> {0} [FOLDER] [Other Arguments]'
                     ''.format(recipe), ' ']
            # get available night_names
            nightnames = get_night_dirs(p)
            emsgs.append('Some available [FOLDER]s are as follows:')
            # loop around night names and add to message
            for nightname in nightnames:
                emsgs.append('\t {0}'.format(nightname))
            # log error message
            WLOG(p, 'error', emsgs)
    if not no_files:
        fits_fn = p['FITSFILENAME']
        # -------------------------------------------------------------------------
        # check that fitsfilename exists
        if fits_fn is None:
            wmsg1 = 'Argument Error: No fits file defined at run time argument'
            wmsg2 = '    format must be:'
            emsg = '    >>> {0}.py [FOLDER] [FILES]'
            WLOG(p, 'error', [wmsg1, wmsg2, emsg.format(recipe)])
        if not os.path.exists(fits_fn):
            WLOG(p, 'error', 'File : {0} does not exist'.format(fits_fn))

    # -------------------------------------------------------------------------
    # deal with no files being defined
    if files is None:
        files = []
        for filename in p['ARG_FILE_NAMES']:
            files.append(os.path.join(p['ARG_FILE_DIR'], filename))
    elif type(files) != list:
        files = [files]
    # -------------------------------------------------------------------------
    # check file based on recipe name
    p = spirouImage.CheckFiles(p, files, recipe, skipcheck)
    # -------------------------------------------------------------------------
    # Calib DB setup
    p = load_calibdb(p, calibdb)
    # -------------------------------------------------------------------------
    # log processing image type
    if p['DPRTYPE'] == 'None':
        wmsg = 'Now processing Image with {1} recipe'
    else:
        wmsg = 'Now processing Image TYPE {0} with {1} recipe'
    WLOG(p, 'info', wmsg.format(p['DPRTYPE'], recipe))
    # -------------------------------------------------------------------------
    # return p
    return p


def single_file_setup(p, filename, log=True, skipcheck=False, pos=None):
    """
    Check "filename" is valid for recipe p["RECIPE"] and get the correct path,
    logs the output if log is True, and skips the check if skipcheck is True

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            LOG_OPT: string, log option, normally the program name
            RECIPE: string, the recipe name (must be defined in recipe control
                    file)
    :param filename: string, the filename to check
    :param log: bool, whether to log "Now Processing" message
    :param skipcheck: bool, whether to skip the check
    :param pos: int or None, if not None defines the position of the file

    :return p: parameter dictionary, the updated parameter dictionary
            Adds the following:
                DPRTYPE: string, the datatype header key
                PREPROCESSED: bool, if True file is processed (or unchecked)
    :return location: string, the path of the filename (i.e. the raw or
                      reduced directory)

    returns SystemExit if file is not valid for recipe
    """
    # func_name = __NAME__ + '.single_file_setup()'

    recipe = p['RECIPE']
    # check file based on recipe name
    p, path = spirouImage.CheckFile(p, filename, recipe, skipcheck,
                                    return_path=True, pos=pos)
    # get location of file
    location = get_file(p, path, filename)
    # log processing image type
    if log:
        if p['DPRTYPE'] == 'None':
            wmsg = 'Now processing Image with {1} recipe'
        else:
            wmsg = 'Now processing Image TYPE {0} with {1} recipe'
        WLOG(p, 'info', wmsg.format(p['DPRTYPE'], p['PROGRAM']))
    # return p
    return p, location


def multi_file_setup(p, files=None, log=True, skipcheck=False):
    """
    Wrapper for single_file_setup, checks that "files" are valid for recipe
    p["RECIPE"] and get the correct path, logs the output if log is True,
    and skips the check if skipcheck is True

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            LOG_OPT: string, log option, normally the program name
            RECIPE: string, the recipe name (must be defined in recipe control
                    file)
    :param files: list of string, the filenames to check
    :param log: bool, whether to log "Now Processing" message
    :param skipcheck: bool, whether to skip the check

    :return p: parameter dictionary, the updated parameter dictionary
            Adds the following:
                DPRTYPE: string, the datatype header key
                PREPROCESSED: bool, if True file is processed (or unchecked)
    :return locations: list of string, the paths of the filename
                       (i.e. the raw or reduced directory)

    returns SystemExit if any file is not valid for recipe
    """

    # func_name = __NAME__ + '.single_file_setup()'
    # check file based on recipe name
    locations = []
    recipe = p['RECIPE']
    # make sure files is a list
    if isinstance(files, str):
        files = [files]
    # loop around files
    for filename in files:
        p, path = spirouImage.CheckFile(p, filename, recipe, skipcheck,
                                        return_path=True)
        # get location of file
        location = get_file(p, path, filename)
        # append location to locations
        locations.append(location)
    # log processing image type
    if log:
        if p['DPRTYPE'] == 'None':
            wmsg = 'Now processing Image(s) with {1} recipe'
        else:
            wmsg = 'Now processing Image(s) TYPE {0} with {1} recipe'
        WLOG(p, 'info', wmsg.format(p['DPRTYPE'], p['PROGRAM']))
    # return p
    return p, locations


def load_calibdb(p, calibdb=True, header=None):
    """
    Load calibration (on startup) this is loaded by default when
    spirouStartup.spirouStartup.initial_file_setup
    (spirouStartup.InitialFileSetup) so this is only needed to be run when
    InitialFileSetup is not used (i.e. when custom arguments are used)


    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                log_opt: string, log option, normally the program name
                DRS_CALIB_DB: string, the directory that the calibration
                              files should be saved to/read from

    :param calibdb: bool, whether to load the calibration database (if False
                    just makes sure DRS_CALIB_DB exists (and creates it if it
                    doesn't)

    :return p: parameter dictionary, the updated parameter dictionary
            Adds the following:
                if calibdb is True:
                    calibDB: dictionary, the calibration database dictionary
    """
    if header is not None:
        spirouDB.CopyCDBfiles(p, header=header)
        calib_db, p = spirouDB.GetCalibDatabase(p, header=header)
        p['CALIBDB'] = calib_db
        p.set_source('CALIBDB', __NAME__ + '/run_startup()')
    elif calibdb:
        if not os.path.exists(p['DRS_CALIB_DB']):
            WLOG(p, 'error',
                 'CalibDB: {0} does not exist'.format(p['DRS_CALIB_DB']))
        # then make sure files are copied
        spirouDB.CopyCDBfiles(p)
        # then load the calibdb into p
        calib_db, p = spirouDB.GetCalibDatabase(p)
        p['CALIBDB'] = calib_db
        p.set_source('CALIBDB', __NAME__ + '/run_startup()')
    else:
        calib_dir = p['DRS_CALIB_DB']
        # if reduced directory does not exist create it
        if not os.path.isdir(calib_dir):
            os.makedirs(calib_dir)
    # return p (with calibration database)
    return p


def main_end_script(p, outputs='reduced', end=True):
    # func_name = __NAME__ + '.main_end_script()'

    # construct a lock file name
    opath = spirouConfig.Constants.INDEX_LOCK_FILENAME(p)

    if outputs is not None:
        # get and check for file lock file
        lock, lock_file = spirouImage.CheckFitsLockFile(p, opath)

        # Must now deal with errors and make sure we close the lock file
        try:
            if outputs == 'pp':
                # index outputs to pp dir
                index_pp(p)
            elif outputs == 'reduced':
                # index outputs to reduced dir
                index_outputs(p)
            # close lock file
            spirouImage.CloseFitsLockFile(p, lock, lock_file, opath)
        # Must close lock file
        except SystemExit as e:
            spirouImage.CloseFitsLockFile(p, lock, lock_file, opath)
            raise e
        except Exception as e:
            spirouImage.CloseFitsLockFile(p, lock, lock_file, opath)
            raise e

    # log end message
    if end:
        wmsg = 'Recipe {0} has been successfully completed'
        WLOG(p, 'info', wmsg.format(p['PROGRAM']))
        # add the logger messsages to p
        p = WLOG.output_param_dict(p)
        # finally clear out the log in WLOG
        WLOG.clean_log(p['PID'])
    # return p
    return p


def index_pp(p):
    # get index filename
    filename = spirouConfig.Constants.INDEX_OUTPUT_FILENAME()
    # get night name
    path = p['TMP_DIR']
    # get absolute path
    abspath = os.path.join(path, filename)
    # get the outputs
    outputs = p['OUTPUTS']
    # check that outputs is not empty
    if len(outputs) == 0:
        WLOG(p, '', 'No outputs to index, skipping indexing')
        return 0
    # get the index columns
    icolumns = spirouConfig.Constants.RAW_OUTPUT_COLUMNS(p)
    # ------------------------------------------------------------------------
    # index files
    istore = indexing(p, outputs, icolumns, abspath)
    # ------------------------------------------------------------------------
    # sort and save
    sort_and_save_outputs(p, istore, abspath)


def index_outputs(p):
    # get index filename
    filename = spirouConfig.Constants.INDEX_OUTPUT_FILENAME()
    # get night name
    path = p['REDUCED_DIR']
    # get absolute path
    abspath = os.path.join(path, filename)
    # get the outputs
    outputs = p['OUTPUTS']
    # check that outputs is not empty
    if len(outputs) == 0:
        WLOG(p, '', 'No outputs to index, skipping indexing')
        return 0
    # get the index columns
    icolumns = spirouConfig.Constants.REDUC_OUTPUT_COLUMNS(p)
    # ------------------------------------------------------------------------
    # index files
    istore = indexing(p, outputs, icolumns, abspath)
    # ------------------------------------------------------------------------
    # sort and save
    sort_and_save_outputs(p, istore, abspath)


def indexing(p, outputs, icolumns, abspath):
    # ------------------------------------------------------------------------
    # log indexing
    wmsg = 'Indexing outputs onto {0}'
    WLOG(p, '', wmsg.format(abspath))
    # construct a dictionary from outputs and icolumns
    istore = OrderedDict()
    # get output path
    opath = os.path.dirname(abspath)
    # looop around outputs
    for output in outputs:
        # get absfilename
        absoutput = os.path.join(opath, output)
        # get filename
        if 'FILENAME' not in istore:
            istore['FILENAME'] = [output]
            istore['LAST_MODIFIED'] = [os.path.getmtime(absoutput)]
        else:
            istore['FILENAME'].append(output)
            istore['LAST_MODIFIED'].append(os.path.getmtime(absoutput))

        # loop around index columns and add outputs to istore
        for icol in icolumns:
            # get value from outputs
            if icol not in outputs[output]:
                value = 'None'
            else:
                value = outputs[output][icol]
            # push in to istore
            if icol not in istore:
                istore[icol] = [value]
            else:
                istore[icol].append(value)
    # ------------------------------------------------------------------------
    # deal with file existing (add existing rows)
    if os.path.exists(abspath):
        # get the current index fits file
        idict = spirouImage.ReadFitsTable(p, abspath, return_dict=True)
        # check that all keys are in idict
        for key in icolumns:
            if key not in list(idict.keys()):
                wmsg1 = ('Warning: Index file does not have column="{0}"'
                         ''.format(key))
                wmsg2 = '\tPlease run the appropriate off_listing recipe'
                WLOG(p, 'warning', [wmsg1, wmsg2])
        # loop around rows in idict
        for row in range(len(idict['FILENAME'])):
            # skip if we already have this file
            if idict['FILENAME'][row] in istore['FILENAME']:
                continue
            # else add filename
            istore['FILENAME'].append(idict['FILENAME'][row])
            istore['LAST_MODIFIED'].append(idict['LAST_MODIFIED'][row])
            # loop around columns
            for icol in icolumns:
                # if column not in index deal with it
                if icol not in idict.keys():
                    istore[icol].append('None')
                else:
                    # add to the istore
                    istore[icol].append(idict[icol][row])
    # ------------------------------------------------------------------------
    return istore


def sort_and_save_outputs(p, istore, abspath):
    # ------------------------------------------------------------------------
    # sort the istore by column name and add to table
    sortmask = np.argsort(istore['FILENAME'])
    # loop around columns and apply sort
    for icol in istore:
        istore[icol] = np.array(istore[icol])[sortmask]
    # ------------------------------------------------------------------------
    # Make fits table and write fits table
    itable = spirouImage.MakeFitsTable(istore)
    spirouImage.WriteFitsTable(p, itable, abspath)


# noinspection PyProtectedMember
def exit_script(ll, has_plots=True):
    """
    Exit script for handling interactive endings to sessions (if DRS_PLOT is
    active)

    :param ll: dict, the local variables
    :param has_plots: bool, if True looks for and deal with having plots
                      (i.e. asks the user to close or closest automatically),
                      if False no plot windows are assumed to be open

    :return None:
    """
    # get parameter dictionary of constants (or create it)
    if 'p' in ll:
        p = ll['p']
    else:
        p = OrderedDict()
    # make sure we have DRS_PLOT
    if 'DRS_PLOT' not in p:
        p['DRS_PLOT'] = 0
    # make sure we have DRS_INTERACTIVE
    if 'DRS_INTERACTIVE' not in p:
        p['DRS_INTERACTIVE'] = 1
    # make sure we have log_opt
    if 'log_opt' not in p:
        p['LOG_OPT'] = sys.argv[0]
    # if DRS_INTERACTIVE is False just return 0
    if not p['DRS_INTERACTIVE']:
        # print('Interactive mode off')
        return 0
    # find whether user is in ipython or python
    if find_ipython():
        kind = 'ipython'
    else:
        kind = 'python'
    # log message
    wmsg = 'Press "Enter" to exit or [Y]es to continue in {0}'
    WLOG(p, '', '')
    WLOG(p, '', HEADER, printonly=True)
    WLOG(p, 'warning', wmsg.format(kind), printonly=True)
    WLOG(p, '', HEADER, printonly=True)
    # deal with python 2 / python 3 input method
    if sys.version_info.major < 3:
        # noinspection PyUnresolvedReferences
        uinput = raw_input('')  # note python 3 wont find this!
    else:
        uinput = input('')

    # if yes or YES or Y or y then we need to continue in python
    # this may require starting an interactive session
    if 'Y' in uinput.upper():
        # if user in ipython we need to try opening ipython
        if kind == 'ipython':
            # noinspection PyBroadException
            try:
                from IPython import embed
                # this is only to be used in this situation and should not
                # be used in general
                locals().update(ll)
                embed()
            except Exception:
                pass
        if not find_interactive():
            # add some imports to locals
            ll['np'], ll['plt'], ll['WLOG'] = np, spirouCore.sPlt.plt, WLOG
            ll['os'], ll['sys'], ll['ParamDict'] = os, sys, ParamDict
            # run code
            code.interact(local=ll)
    # if "No" and not interactive quit python/ipython
    elif not find_interactive():
        # noinspection PyProtectedMember
        os._exit(0)
    # if interactive ask about closing plots
    if find_interactive() and has_plots and p['DRS_PLOT'] == 1:
        # deal with closing plots
        wmsg = 'Close plots? [Y]es or [N]o?'
        WLOG(p, '', HEADER, printonly=True)
        WLOG(p, 'warning', wmsg.format(kind), printonly=True)
        WLOG(p, '', HEADER, printonly=True)
        # deal with python 2 / python 3 input method
        if sys.version_info.major < 3:
            # noinspection PyUnresolvedReferences
            uinput = raw_input('')  # note python 3 wont find this!
        else:
            uinput = input('')
        # if yes close all plots
        if 'Y' in uinput.upper():
            # close any open plots properly
            spirouCore.sPlt.closeall()


def spirou_input_yes_no(p, question):
    # if DRS_INTERACTIVE is False just return 0
    if not p['DRS_INTERACTIVE']:
        print('Interactive mode off')
        return False
    # find whether user is in ipython or python
    if find_ipython():
        kind = 'ipython'
    else:
        kind = 'python'
    # log message
    wmsg = question
    WLOG('', '', '')
    WLOG('', '', HEADER, printonly=True)
    WLOG(p, 'warning', wmsg.format(kind), printonly=True)
    WLOG('', '', HEADER, printonly=True)
    # deal with python 2 / python 3 input method
    if sys.version_info.major < 3:
        # noinspection PyUnresolvedReferences
        uinput = raw_input('')  # note python 3 wont find this!
    else:
        uinput = input('')
    # if yes or YES or Y or y return True else return False
    if 'Y' in uinput.upper():
        return True
    else:
        return False


# =============================================================================
# Define general functions
# =============================================================================
def check_key_fparams(p):
    # if fitsfilename exists it must be found
    if 'FITSFILENAME' in p:
        if p['FITSFILENAME'] is not None:
            if not os.path.exists(p['FITSFILENAME']):
                emsg = 'Fatal error cannot find FITSFILENAME={0}'
                WLOG(p, 'error', emsg.format(p['FITSFILENAME']))

    if 'ARG_FILE_NAMES' in p:
        for afile in p['ARG_FILE_NAMES']:
            apath = os.path.join(p['ARG_FILE_DIR'], afile)
            if not os.path.exists(apath):
                emsg1 = 'Fatal error cannot find ARG_FILE_NAME={0}'
                emsg2 = '   in directory = {0}'.format(p['ARG_FILE_DIR'])
                WLOG(p, 'error', [emsg1.format(afile), emsg2])
    # finally return param dict
    return p


def run_time_args(p, mainfitsdir, require_night_name=True):
    """
    Get sys.argv arguments (run time arguments and use them to fill parameter
    dictionary

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                constants from primary configuration file

    :param mainfitsdir: string or None, if mainfitsfile is defined and needed
                        this is the location of the mainfitsfile if None this
                        is assumed to be the raw dir folder
                        current other options are:
                            'reduced' - the DRS_DATA_REDUC folder
                            'calibdb' - the DRS_CALIB_DB folder
                            or the full path to the file

    :param require_night_name: bool, if False do not require night_name

    :return p: parameter dictionary, the updated parameter dictionary
            Adds the following:
                program: string, the recipe/way the script was called
                         i.e. from sys.argv[0]
                arg_night_name: string, the folder within data raw directory
                                containing files (also reduced directory) i.e.
                                /data/raw/20170710 would be "20170710"
                arg_file_names: list, list of files taken from the command line
                                (or call to recipe function) must have at least
                                one string filename in the list
                STR_FILE_NAMES: string, the "arg_file_names" in string form
                                separated by commas
                fitsfilename: string, the full path of for the main raw fits
                              file for a recipe
                              i.e. /data/raw/20170710/filename.fits
                log_opt: string, log option, normally the program name
                nbframes: int, the number of frames/files (usually the length
                          of "arg_file_names")
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME'])
                raw_dir: string, the raw data directory
                         (i.e. p['DRS_DATA_RAW']/p['ARG_NIGHT_NAME'])
    """
    # get constants name
    cname = spirouConfig.Constants.__NAME__

    # get program name
    p['PROGRAM'] = spirouConfig.Constants.PROGRAM(p)
    p.set_source('PROGRAM', cname + '/PROGRAM()')

    # get night name and filenames
    p['ARG_NIGHT_NAME'] = spirouConfig.Constants.ARG_NIGHT_NAME(p)
    p.set_source('ARG_NIGHT_NAME', cname + '/ARG_NIGHT_NAME')
    p['ARG_FILE_NAMES'] = spirouConfig.Constants.ARG_FILE_NAMES(p)
    p.set_source('ARG_FILE_NAMES', cname + '/ARG_FILE_NAMES')
    p['STR_FILE_NAMES'] = ', '.join(p['ARG_FILE_NAMES'])
    p.set_source('STR_FILE_NAMES', __NAME__ + '/run_time_args()')

    # set reduced path
    p['REDUCED_DIR'] = spirouConfig.Constants.REDUCED_DIR(p)
    p.set_source('REDUCED_DIR', cname + '/REDUCED_DIR()')
    # set temp path
    p['TMP_DIR'] = spirouConfig.Constants.TMP_DIR(p)
    p.set_source('TMP_DIR', cname + '/TMP_DIR()')
    # set raw path
    p['RAW_DIR'] = spirouConfig.Constants.RAW_DIR(p)
    p.set_source('RAW_DIR', cname + '/RAW_DIR()')

    # deal with setting main fits directory (sets ARG_FILE_DIR)
    p = set_arg_file_dir(p, mfd=mainfitsdir,
                         require_night_name=require_night_name)

    # get fitsfilename
    p['FITSFILENAME'] = spirouConfig.Constants.FITSFILENAME(p)
    p.set_source('FITSFILENAME', cname + '/FITSFILENAME()')

    # get the logging option
    p['LOG_OPT'] = spirouConfig.Constants.LOG_OPT(p)
    p.set_source('LOG_OPT', cname + '/LOG_OPT()')

    # Get number of frames
    p['NBFRAMES'] = spirouConfig.Constants.NBFRAMES(p)
    p.set_source('NBFRAMES', cname + '/NBFRAMES()')

    # return updated parameter dictionary
    return p


def run_time_custom_args(p, customargs, mainfitsdir, require_night_name=True):
    """
    Get the custom arguments and add them (with some default arguments)
    to the constants parameter dictionary

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
        constants from primary configuration file

    :param customargs: dictionary, the custom arguments to add

    :param mainfitsdir: string or None, if mainfitsfile is defined and needed
                        this is the location of the mainfitsfile if None this
                        is assumed to be the raw dir folder
                        current other options are:
                            'reduced' - the DRS_DATA_REDUC folder
                            'calibdb' - the DRS_CALIB_DB folder
                            or the full path to the file

    :param require_night_name: bool, if False do not require night_name

    :return p: parameter dictionary, the updated parameter dictionary
            Adds the following:
                program: string, the recipe/way the script was called
                         i.e. from sys.argv[0]
                log_opt: string, log option, normally the program name
                arg_night_name: string, the folder within data raw directory
                                containing files (also reduced directory) i.e.
                                /data/raw/20170710 would be "20170710"
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME'])
                raw_dir: string, the raw data directory
                         (i.e. p['DRS_DATA_RAW']/p['ARG_NIGHT_NAME'])
                customargs: "customargs" added from call
    """
    # set source
    source = __NAME__ + '/run_time_custom_args()'
    sconst = 'spirouConfig.Constants.'
    # get program name
    p['PROGRAM'] = spirouConfig.Constants.PROGRAM(p)
    p.set_source('program', source + ' & {0}PROGRAM()'.format(sconst))
    # get the logging option
    p['LOG_OPT'] = p['PROGRAM']
    p.set_source('log_opt', source + ' & {0}PROGRAM()'.format(sconst))
    # get night name and filenames
    p['ARG_NIGHT_NAME'] = spirouConfig.Constants.ARG_NIGHT_NAME(p)
    p.set_source('arg_night_name',
                 source + ' & {0}ARG_NIGHT_NAME()'.format(sconst))
    # set reduced path
    p['REDUCED_DIR'] = spirouConfig.Constants.REDUCED_DIR(p)
    p.set_source('reduced_dir', source + ' & {0}/REDUCED_DIR()')
    # set temp path
    p['TMP_DIR'] = spirouConfig.Constants.TMP_DIR(p)
    p.set_source('TMP_DIR', source + '/TMP_DIR()')
    # set raw path
    p['RAW_DIR'] = spirouConfig.Constants.RAW_DIR(p)
    p.set_source('raw_dir', source + ' & {0}/RAW_DIR()')

    # deal with setting main fits directory (sets ARG_FILE_DIR)
    p = set_arg_file_dir(p, mfd=mainfitsdir,
                         require_night_name=require_night_name)

    # loop around defined run time arguments
    for key in list(customargs.keys()):
        # set the value
        p[key] = customargs[key]
        p.set_source(key, 'From run time arguments (sys.argv)')

    return p


def get_call_arg_files_fitsfilename(p, files, mfd=None,
                                    rnn=True):
    """
    We need to deal with there being no run time arguments and having
    files defined from "files". In the case that there are no run time
    arguments "arg_file_names" and "fitsfilename" are not defined so these
    have to be defined from "files". "arg_file_names" is simply equal to "files"
    however "fitsfilename" is a full path so this is more complicated.
    In runtime arguments all "arg_file_names" are assumed to be in the raw
    directory thus we need to add this to the fitsfilename

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                DRS_DATA_RAW: string, the directory that the raw data should
                              be saved to/read from
                arg_night_name: string, the folder within data raw directory
                                containing files (also reduced directory) i.e.
                                /data/raw/20170710 would be "20170710"
    :param files: list or None, the list of files to use for arg_file_names
                  (if None assumes arg_file_names was set from run time)

    :param mfd: string or None, if mainfitsfile is defined and needed this is
            the location of the mainfitsfile if None this is assumed to
            be the raw dir folder current other options are:
                'reduced' - the DRS_DATA_REDUC folder
                'calibdb' - the DRS_CALIB_DB folder
                or the full path to the file

    :param rnn: bool, if False do not require night_name

    :return cparams: parameter dictionary, the updated parameter dictionary
            Adds the following:
                arg_file_names: list, list of files taken from the command line
                                (or call to recipe function) must have at least
                                one string filename in the list
                fitsfilename: string, the full path of for the main raw fits
                              file for a recipe
                              i.e. /data/raw/20170710/filename.fits
    """
    func_name = __NAME__ + '.get_call_arg_files_fitsfilename()'
    # make sure we have DRS_DATA_RAW and ARG_NIGHT_NAME
    if 'DRS_DATA_RAW' not in p or 'arg_night_name' not in p:
        emsg1 = (' Error "cparams" must contain "DRS_DATA_RAW" and '
                 '"ARG_NIGHT_NAME"')
        emsg2 = '    function = {0}'.format(func_name)
        WLOG(p, 'error', [emsg1, emsg2])
    # get chosen arg_file_dir
    p = set_arg_file_dir(p, mfd, rnn)

    # check files type
    # need to check whether files is a list
    if type(files) == str:
        checkfiles = [files]
    elif type(files) in [list, np.ndarray]:
        checkfiles = list(files)
    else:
        emsg1 = ('Input Error: "files" must be either a string or a list '
                 'of strings')
        emsg2 = '\t"files" type is currently = "{0}"'.format(type(files))
        emsg3 = '\tfunction = {0}'.format(func_name)
        WLOG(p, 'error', [emsg1, emsg2, emsg3])
        checkfiles = []

    # if we don't have arg_file_names set it to the "files"
    if 'ARG_FILE_NAMES' not in p:
        p['ARG_FILE_NAMES'] = checkfiles
        # need to re-set nbframes
        p['NBFRAMES'] = len(checkfiles)
        # set source
        p.set_sources(['ARG_FILE_NAMES', 'NBFRAMES'], func_name)
    # if we have no files in arg_file_names set it to the "files"
    elif len(p['ARG_FILE_NAMES']) == 0:
        p['ARG_FILE_NAMES'] = checkfiles
        # need to re-set nbframes
        p['NBFRAMES'] = len(checkfiles)
        # set source
        p.set_sources(['ARG_FILE_NAMES', 'NBFRAMES'], func_name)
    # if we don't have fitsfilename set it to the ARG_FILE_DIR + files[0]
    if 'FITSFILENAME' not in p:
        p['FITSFILENAME'] = os.path.join(p['ARG_FILE_DIR'], checkfiles[0])
        # set source
        p.set_source('FITSFILENAME', func_name)
    # if fitsfilename is set to None set it to the ARG_FILE_DIR + files[0]
    elif p['FITSFILENAME'] is None:
        p['FITSFILENAME'] = os.path.join(p['ARG_FILE_DIR'], checkfiles[0])
        # set source
        p.set_source('FITSFILENAME', func_name)
    # set string file names
    p['STR_FILE_NAMES'] = ', '.join(p['ARG_FILE_NAMES'])
    p.set_source('STR_FILE_NAMES', func_name)
    # finally return the updated cparams
    return p


def set_arg_file_dir(p, mfd=None, require_night_name=True):
    """

    :param p: parameter dictionary, ParamDict containing constants
            Must contain at least:
                DRS_DATA_RAW: string, the directory that the raw data should
                              be saved to/read from
                arg_night_name: string, the folder within data raw directory
                                containing files (also reduced directory) i.e.
                                /data/raw/20170710 would be "20170710"
                DRS_DATA_REDUC: string, the directory that the reduced data
                                should be saved to/read from
                DRS_CALIB_DB: string, the directory that the calibration
                              files should be saved to/read from

    :param mfd: string or None, if mainfitsfile is defined and needed this is
            the location of the mainfitsfile if None this is assumed to
            be the raw dir folder current other options are:
                'reduced' - the DRS_DATA_REDUC folder
                'calibdb' - the DRS_CALIB_DB folder
                or the full path to the file

    :param require_night_name: bool, if False do not require night_name

    :return p: parameter dictionary, the updated parameter dictionary
            Adds the following:
                ARG_FILE_DIR: string, the directory containing the files
                              in p['ARG_FILE_NAMES']
    """
    # fix for when someone enters the wrong path in windows/unix
    if 'win' in sys.platform:
        p['ARG_NIGHT_NAME'] = p['ARG_NIGHT_NAME'].replace(r'/', os.sep)
    else:
        p['ARG_NIGHT_NAME'] = p['ARG_NIGHT_NAME'].replace('\\', os.sep)

    # first we need to make sure night_name doesn't have backslahses at the end
    while p['ARG_NIGHT_NAME'].endswith(os.sep):
        p['ARG_NIGHT_NAME'] = p['ARG_NIGHT_NAME'][:-1]

    # define the raw/reduced/calib folder from cparams
    raw_dir = spirouConfig.Constants.RAW_DIR(p)
    tmp_dir = spirouConfig.Constants.TMP_DIR(p)
    red_dir = spirouConfig.Constants.REDUCED_DIR(p)
    calib_dir = p['DRS_CALIB_DB']
    # deal with main fits file (see if it exists)
    if mfd is not None:
        cond = os.path.exists(mfd)
    else:
        cond = False
    # choose between the different possible values for the main arg_file_dir
    if cond:
        p['ARG_FILE_DIR'] = mfd
        location = 'mainfitsfile definition'
    elif mfd == 'reduced':
        p['ARG_FILE_DIR'] = red_dir
        location = 'spirouConfig.Constants.REDUCED_DIR()'
    elif mfd == 'calibdb':
        p['ARG_FILE_DIR'] = calib_dir
        location = 'DRS_CALIB_DB'
    elif mfd == 'raw':
        p['ARG_FILE_DIR'] = raw_dir
        location = 'spirouConfig.Constants.RAW_DIR()'
    else:
        p['ARG_FILE_DIR'] = tmp_dir
        location = 'spirouConfig.Constants.RAW_DIR()'
    # set ARG_FILE_DIR source
    p.set_source('ARG_FILE_DIR', location)
    # check that ARG_FILE_DIR is valid
    if not os.path.exists(p['ARG_FILE_DIR']):
        # get arg path (path without [FOLDER] or NIGHT_NAME
        if p['ARG_NIGHT_NAME'] in p['ARG_FILE_DIR']:
            arg_fp = p['ARG_FILE_DIR'][:-len(p['ARG_NIGHT_NAME'])]
        else:
            arg_fp = p['ARG_FILE_DIR']
        # if arg path does exist it is the [FOLDER] or NIGHT_NAME which
        #   is wrong
        if os.path.exists(arg_fp):
            emsgs = ['Fatal error cannot find '
                     'NIGHT_NAME="{0}"'.format(p['ARG_NIGHT_NAME']),
                     '    in directory {0} ({1})'.format(arg_fp, location)]
            WLOG(p, 'error', emsgs)
        elif not require_night_name:
            p['ARG_FILE_DIR'] = ''
        # else it is the directory which is wrong (cal_validate was not run)
        else:
            emsg1 = ('Fatal error cannot find directory NIGHT_NAME="{0}"'
                     ''.format(p['ARG_FILE_DIR']))
            # log error
            WLOG(p, 'error', emsg1)

    # return p
    return p


def load_other_config_file(p, key, logthis=True, required=False):
    """
    Load a secondary configuration file from p[key] with wrapper to deal
    with ConfigErrors (pushed to WLOG)

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                log_opt: string, log option, normally the program name
                key: "key" defined in call

    :param key: string, the key in "p" storing the location of the secondary
                configuration file
    :param logthis: bool, if True loading of this config file is logged to
                    screen/log file
    :param required: bool, if required is True then the secondary config file
                     is required for the DRS to run and a ConfigError is raised
                     (program exit)

    :return p: parameter, dictionary, the updated parameter dictionary with
               the secondary configuration files loaded into it as key/value
               pairs
    """
    # try to load config file from file
    try:
        pp, lmsgs = spirouConfig.LoadConfigFromFile(p, key, required=required,
                                                    logthis=logthis)
    except spirouConfig.ConfigError as e:
        WLOG(p, e.level, e.message)
        pp, lmsgs = ParamDict(), []

    # log messages caught in loading config file
    if len(lmsgs) > 0:
        WLOG(p, '', lmsgs)
    # return parameter dictionary
    return pp


def deal_with_prefixes(p=None, kind=None, prefixes=None,
                       add_to_p=None, filename=None):
    """
    Deals with finding the prefixes and adding any add_to_p values to p

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                log_opt: string, log option, normally the program name
                arg_file_names: list, list of files taken from the command line
                                (or call to recipe function) must have at least
                                one string filename in the list

    :param kind: string or None, description of program we are running
                 (i.e. dark) if None is not used.

    :param prefixes: list of strings, prefixes to look for in file name
                     will exit code if none of the prefixes are found
                     (prefix = None if no prefixes are needed to be found)

    :param add_to_p: dictionary structure or None:

            add_to_p[prefix1] = dict(key1=value1, key2=value2)
            add_to_p[prefix2] = dict(key3=value3, key4=value4)

            where prefix1 and prefix2 are the strings in "prefixes"

            This will add the sub dictionaries to the main parameter dictionary
            based on which prefix is found

            i.e. if prefix1 is found key "value3" and "value4" above are added
            (with "key3" and "key4") to the parameter dictionary p

    :param filename: string or None, the filename to check (if None checks
                     "arf_file_names"[0] from p

    :return p: parameter dictionary, the updated parameter dictionary
            Adds the following:
                the subdictionary key/value pairs in "add_to_p" that contains
                the correct prefix for p['ARG_FILE_NAMES'][0]
    """
    func_name = __NAME__ + '.deal_with_prefixes()'
    # if we have p then we are just checking a filename
    if p is None:
        p = ParamDict(log_opt=__NAME__)
        if filename is None:
            emsgs = ['ParamDict "p" or "filename" must be defined '
                     '(both are None)',
                     '   function = {0}'.format(func_name)]
            WLOG(p, 'error', emsgs)
    # if we have no prefixes we can just return p
    if prefixes is None:
        return p
    elif not type(prefixes) == list:
        prefixes = [prefixes]
    # get variables from p
    if filename is None:
        arg_fn1 = p['ARG_FILE_NAMES'][0]
    else:
        arg_fn1 = filename
    # set up found variables
    found, fprefix = False, None
    # loop around prefixes
    for prefix in prefixes:
        # if prefix in arg_file_name then the correct file is being used
        # set found to True and store the prefix (for use later)
        if prefix in arg_fn1:
            found = True
            fprefix = prefix
    # if found log that we found image
    if found:
        if kind is None:
            wmsg = 'Correct type of image ({1})'
        else:
            wmsg = 'Correct type of image for {0} ({1})'
        WLOG(p, 'info', wmsg.format(kind, ' or '.join(prefixes)))
        # if a2p is not None we have some variables that need added to
        # parameter dictionary based on the prefix found
        if add_to_p is not None:
            # if fprefix is None (shouldn't be) just return original parameters
            if fprefix is None:
                return p
            # elif fprefix is not in add_to_p (if set up correctly it should be)
            # return original parameters
            elif fprefix not in add_to_p:
                return p
            # if fprefix is in a2p and not None
            else:
                # add parameters from correct a2p dictionary to parameters
                for param in add_to_p[fprefix]:
                    p[param] = add_to_p[fprefix][param]
                    # set the source for parameter
                    source = add_to_p[fprefix].get_source(param)
                    p.set_source(param, source=source)
                return p
        else:
            return p
    # Else if we don't have the correct prefix then log and exit
    else:
        if kind is None:
            wmsg = 'Wrong type of image, should be {1}'
        else:
            wmsg = 'Wrong type of image for {0}, should be {1}'
        WLOG(p, 'error', wmsg.format(kind, ' or '.join(prefixes)))


def get_arguments(p, positions, types, names, required, calls, cprior, lognames,
                  require_night_name=True, recipe=None):
    """
    Take the "positions" and extract from sys.argv[2:] (first arg is the program
    name, second arg is reserved for night_name) use "types" to force type
    (i.e. int/str/float) of each argument (error raised if cannot convert) and
    push results into a dictionary with keys = "names"

    :param positions: list of integers or None, the positions of the arguments
                      (i.e. first argument is 0)

    :param types: list of python types or None, the type (i.e. int, float) for
                  each argument. Note if last_multi = True, the type of the
                  last defined parameter should be the type of each argument
                  (but the output parameter will be a list of this type of
                  arguments)

    :param names: list of strings, the names of each argument (to access in
                  parameter dictionary once extracted)

    :param required: list of bools or None, states whether the program
                     should exit if runtime argument not found

    :param calls: list of objects or None, if define these are the values that
                  come from a function call (overwrite command line arguments)

    :param cprior: list of bools, if True the call takes priority over arguments
                   defined at run time, if False run time arguments take
                   priority

    :param lognames: list of strings, the names displayed in the log (on error)
                     theses should be similar to "names" but in a form the
                     user can easily understand for each variable

    :param require_night_name: bool, if False night name is not required in
                               the arguments

    :param recipe: string, the program name that called this function

    :return customdict: dictionary containing the run time arguments converts
                        to "types", keys are equal to "names"
    """
    if require_night_name:
        first_arg_pos = 2
    else:
        first_arg_pos = 1

    # set up the dictionary
    customdict = OrderedDict()
    for pos in positions:
        # deal with not having enough arguments
        try:
            # get from sys.argv
            # first arg should be the program name
            # second arg should be the night name
            raw_value = sys.argv[pos + first_arg_pos]
        except IndexError:
            # if calls is None and required = True then we should exit now
            if calls is None or calls[pos] is None:

                # if not required then it is okay to not find it
                if not required[pos]:
                    raw_value = None
                else:
                    # noinspection PyListCreation
                    emsgs = ['Argument Error: "{0}" is not defined'
                             ''.format(lognames[pos])]
                    emsgs.append(('   must be format:'.format(pos + 1)))
                    eargs = [recipe, ' '.join(lognames)]
                    # deal with difference between modes (i.e. no night_name)
                    if require_night_name:
                        emsg = '\t>>> {0} NIGHT_NAME {1}'
                        emsgs.append(emsg.format(*eargs))
                    else:
                        emsgs.append(('\t>>> {0} {1}'.format(*eargs)))
                    # log error
                    WLOG(p, 'error', emsgs)
                    raw_value = None
            # else we must use the value from calls
            else:
                raw_value = calls[pos]
        # if calls priority is True then override value with that in calls
        if calls is not None:
            if calls[pos] is not None and cprior[pos]:
                raw_value = calls[pos]
        # get the name
        name = names[pos]
        # get the type
        kind = types[pos]
        # test the raw_value
        try:
            value = kind(raw_value)
            # add value to dictionary
            customdict[name] = value
        except ValueError:
            emsg = 'Arguments Error: "{0}" should be a {1} (Value = {2})'
            eargs = [lognames[pos], TYPENAMES[kind], raw_value]
            WLOG(p, 'error', emsg.format(*eargs))
        except TypeError:
            pass
    # return dict
    return customdict


def get_multi_last_argument(p, customdict, positions, types, names, lognames):
    """
    Takes the largest argument in "positions" and pushes all further arguments
    into a list under names[max(positions)], all further arguments are
    required to conform to the type "types[max(positions)] and
    names[max(position)] becomes a list of types[max(positions)]

    :param customdict: dictionary containing the run time arguments converts
                       to "types", keys are equal to "names"

    :param positions: list of integers or None, the positions of the arguments
                      (i.e. first argument is 0)

    :param types: list of python types or None, the type (i.e. int, float) for
                  each argument. Note if last_multi = True, the type of the
                  last defined parameter should be the type of each argument
                  (but the output parameter will be a list of this type of
                  arguments)

    :param names: list of strings, the names of each argument (to access in
                  parameter dictionary once extracted)

    :param lognames: list of strings, the names displayed in the log (on error)
                     theses should be similar to "names" but in a form the
                     user can easily understand for each variable

    :return dict: dictionary containing the run time arguments converts to
                  "types", keys are equal to
                  "names"dirname = os.path.dirname(abs_path)
                  dict[names[max(positions)] is updated to be a list of
                  type types[max(positions)]
    """
    # get the last position and name/type for it
    maxpos = np.max(positions)
    maxname = names[maxpos]
    maxkind = types[maxpos]
    # check the length of sys.argv (needs to be > maxpos + 2)
    if len(sys.argv) > maxpos + 3:
        # convert maxname to a list
        customdict[maxname] = [customdict[maxname]]
        # if maxpos = 0 then we are done
        if maxpos == 0:
            return customdict
        else:
            # now append additional arguments to this list with type maxkind
            for pos in range(maxpos + 2, len(sys.argv)):
                # get vaue from sys.argv
                raw_value = sys.argv[pos]
                try:
                    # try to cast it to type "maxkind"
                    raw_value = maxkind(raw_value)
                    # try to add it to dictionary
                    customdict[maxname].append(raw_value)
                except ValueError:
                    emsg = ('Arguments Error: "{0}" should be a {1} '
                            '(Value = {2})')
                    eargs = [lognames[pos], TYPENAMES[maxkind], raw_value]
                    WLOG(p, 'error', emsg.format(*eargs))
    else:
        customdict[maxname] = [customdict[maxname]]
    # return the new custom dictionary
    return customdict


def get_file(p, path, filename):
    """
    Get full file path and check the path and file exist

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                log_opt: string, log option, normally the program name
                program: string, the recipe/way the script was called
                         i.e. from sys.argv[0]

    :param path: string, either the directory to the folder (if name is None) or
                 the full path to the file
    :param filename: string or None, if None uses the path, defines the
                     filename to ge tthe file of

    :return location: string, the full file path of the file
    """
    # if path is None and name is None
    if path is None:
        WLOG(p, 'error', 'No file defined')
    # if name and path are not None
    if filename is None:
        filename = os.path.basename(path)
        path = os.path.dirname(path)
    # join path and name
    location = os.path.join(path, filename)
    # test if path exists
    if not os.path.exists(path):
        emsg = 'Directory: {0} does not exist'
        WLOG(p, 'error', emsg.format(path))
    # test if path + file exits
    if not os.path.exists(location):
        emsg = 'File : {0} does not exist at location {1}'
        WLOG(p, 'error', emsg.format(filename, path))
    # if all conditions passed return full path
    return location


def get_night_dirs(p):
    night_dirs = []
    limit = p['DRS_NIGHT_NAME_DISPLAY_LIMIT']
    for root, dirs, files in os.walk(p['ARG_FILE_DIR']):
        # skip dirs that are empty (or full of directories)
        if len(files) == 0:
            continue
        # do not display all
        if len(night_dirs) > limit:
            night_dirs.append('...')
            return night_dirs
        # find the relative root of directories compared to ARG_FILE_DIR
        common = os.path.commonpath([p['ARG_FILE_DIR'], root]) + '/'
        relroot = root.split(common)[-1]
        # append relative roots
        night_dirs.append(relroot)
    # return night_dirs
    return night_dirs


def find_interactive():
    """
    Find whether user is using an interactive session

    i.e. True if:
        ipython code.py
        ipython >> run code.py
        python -i code.py

    False if
        python code.py
        code.py

    Note cannot distinguish between ipython from shell (so assumed interactive)

    :return cond: bool, True if interactive
    """
    cond1 = sys.flags.interactive
    cond2 = hasattr(sys, 'ps1')
    cond3 = not sys.stderr.isatty()
    return cond1 or cond2 or cond3


# noinspection PyUnresolvedReferences
def find_ipython():
    """
    Find whether user is using ipython or python

    :return using_ipython: bool, True if using ipython, false otherwise
    """
    try:
        # noinspection PyStatementEffect
        __IPYTHON__  # Note python wont define this, ipython will
        return True
    except NameError:
        return False


def sort_version(messages=None):
    """
    Obtain and sort version info

    :param messages: list of strings or None, if defined is a list of messages
                     that version_info is added to, else new list of strings
                     is created

    :return messages: list of strings updated or created (if messages is None)
    """
    # deal with no messages
    if messages is None:
        messages = []
    # get version info
    major = sys.version_info.major
    minor = sys.version_info.minor
    micro = sys.version_info.micro

    version = '{0}.{1}.{2}'.format(major, minor, micro)

    # add version info to messages
    messages.append('    Python version = {0}'.format(version))

    # add distribution if possible
    try:
        build = sys.version.split('|')[1].strip()
        messages.append('    Python distribution = {0}'.format(build))
    except IndexError:
        pass

    # add date information if possible
    try:
        date = sys.version.split('(')[1].split(')')[0].strip()
        messages.append('    Distribution date = {0}'.format(date))
    except IndexError:
        pass

    # add Other info information if possible
    try:
        other = sys.version.split('[')[1].split(']')[0].strip()
        messages.append('    Dist Other = {0}'.format(other))
    except IndexError:
        pass

    # return updated messages
    return messages


# =============================================================================
# Define custom argument functions
# =============================================================================
def get_custom_from_run_time_args(p, positions=None, types=None, names=None,
                                  required=None, calls=None, cprior=None,
                                  lognames=None, last_multi=False,
                                  require_night_name=True, recipe=None):
    """
    Extract custom arguments from defined positions in sys.argv (defined at
    run time)

    :param positions: list of integers or None, the positions of the arguments
                      (i.e. first argument is 0)

    :param types: list of python types or None, the type (i.e. int, float) for
                  each argument. Note if last_multi = True, the type of the
                  last defined parameter should be the type of each argument
                  (but the output parameter will be a list of this type of
                  arguments)

    :param names: list of strings, the names of each argument (to access in
                  parameter dictionary once extracted)

    :param required: list of bools or None, states whether the program
                     should exit if runtime argument not found

    :param calls: list of objects or None, if define these are the values that
                  come from a function call (overwrite command line arguments)

    :param cprior: list of bools, if True the call takes priority over arguments
                   defined at run time, if False run time arguments take
                   priority

    :param lognames: list of strings, the names displayed in the log (on error)
                     theses should be similar to "names" but in a form the
                     user can easily understand for each variable

    :param last_multi: bool, if True then last argument in positions/types/
                       names adds all additional arguments into a list

    :param require_night_name: bool, if False night name is not required in
                               the arguments

    :param recipe: string, the program that called this function

    :return values: dictionary, if run time arguments are correct python type
                    the name-value pairs are returned
    """
    # deal with no recipe
    if recipe is None:
        recipe = str(__NAME__)
    recipe = recipe.split('.py')[0]
    # deal with no positions (use length of types or names or exit with error)
    if positions is None:
        if types is not None:
            positions = range(len(types))
        elif names is not None:
            positions = range(len(names))
        else:
            emsg = ('Either "positions", "name" or "types" must be defined to'
                    'get custom arguments.')
            WLOG(p, '', emsg)
    # deal with no types (set to strings)
    if types is None:
        types = [str] * len(positions)
    # deal with no names (set to Arg0, Arg1, Arg2 etc)
    if names is None:
        names = ['Arg{0}'.format(pos) for pos in positions]
    if lognames is None:
        lognames = names
    # deal with no required (set all to be required)
    if required is None:
        required = [True] * len(positions)
    # deal with no calls priority (set priority for calls to False)
    if cprior is None:
        cprior = [False] * len(positions)
    # loop around positions test the type and add the value to dictionary
    customdict = get_arguments(p, positions, types, names, required, calls,
                               cprior, lognames, require_night_name,
                               recipe)
    # deal with the position needing to find additional parameters
    if last_multi:
        customdict = get_multi_last_argument(p, customdict, positions, types,
                                             names, lognames)
    # finally return dictionary
    return customdict


def get_custom_arg_files_fitsfilename(p, customargs, mff, mfd=None, rnn=True):
    """
    Deal with having to set arg_file_names and fitsfilenames manually
    uses "mff" the main fits filename and "mdf" the main fits file directory

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                arg_night_name: string, the folder within data raw directory
                                containing files (also reduced directory) i.e.
                                /data/raw/20170710 would be "20170710"
                DRS_DATA_RAW: string, the directory that the raw data should
                              be saved to/read from
                DRS_DATA_REDUC: string, the directory that the reduced data
                                should be saved to/read from
                DRS_CALIB_DB: string, the directory that the calibration
                              files should be saved to/read from
    :param customargs: None or list of strings, if list of strings then instead
                       of getting the standard runtime arguments

           i.e. in form:

                program.py night_dir arg_file_names[0] arg_file_names[1]...

           loads all arguments into customargs

           i.e. if customargs = ['night_dir', 'filename', 'a', 'b', 'c']
           expects command line arguments to be:

                program.py night_dir filename a b c

    :param mff: string, the main fits file (fitsfilename and arg_file_names[0]).
                The parameter MUST be a string, a fits file, and have HEADER
                key defining the acquisition time as  defined in kw_ACQTIME_KEY
                in spirouKeywords.py

    :param mfd: string or None, if mainfitsfile is defined and needed this is
                the location of the mainfitsfile if None this is assumed to
                be the raw dir folder current other options are:
                    'reduced' - the DRS_DATA_REDUC folder
                    'calibdb' - the DRS_CALIB_DB folder
                    or the full path to the file

    :param rnn: bool, if False do not require night name

    :return p: parameter dictionary, the updated parameter dictionary
            Adds/updates the following:
                arg_file_names: list, list of files taken from the command line
                                (or call to recipe function) must have at least
                                one string filename in the list
                fitsfilename: string, the full path of for the main raw fits
                              file for a recipe
                              i.e. /data/raw/20170710/filename.fits
    """
    # define function name
    func_name = __NAME__ + '.get_custom_arg_files_fitsfilename()'
    # define the chosen arg_file_dir
    p = set_arg_file_dir(p, mfd=mfd, require_night_name=rnn)
    # mainfitsfile must be a key in customargs
    if mff in customargs:
        # the value of mainfitsfile must be a string or list of strings
        #    if it isn't raise an error
        cmff = customargs[mff]
        tcmff = type(cmff)
        if tcmff == list:
            rawfilename = cmff[0]
        elif tcmff == str:
            rawfilename = cmff
        else:
            emsg1 = 'customarg[{0}] must be a list or a string'.format(mff)
            emsg2 = ('    customarg[{0}]={1} (type={2})'
                     ''.format(mff, cmff, tcmff))
            emsg3 = '    function = {0}'.format(func_name)
            WLOG(p, 'error', [emsg1, emsg2, emsg3])
            rawfilename = None

        # check if mainfitsvalue is a full path
        if not os.path.exists(rawfilename):
            # construct main file value path
            abspathname = os.path.join(p['ARG_FILE_DIR'], rawfilename)
        else:
            abspathname = rawfilename
        # test type mainfitsfile (must be str or list)
        if type(mff) == str:
            p['ARG_FILE_NAMES'] = [rawfilename]
            p['FITSFILENAME'] = abspathname
            p.set_sources(['ARG_FILE_NAMES', 'FITSFILENAME'], func_name)
        elif type(mff) == list:
            p['ARG_FILE_NAMES'] = rawfilename
            p['FITSFILENAME'] = abspathname[0]
            p.set_sources(['ARG_FILE_NAMES', 'FITSFILENAME'], func_name)
        else:
            eargs = [mff, p['ARG_FILE_DIR']]
            emsg1 = ('The value of mainfitsfile: "{0}"={1} must be a '
                     'valid python string or list').format(*eargs)
            emsg2 = '    function = {0}'.format(func_name)
            WLOG(p, 'error', [emsg1, emsg2])
    # if mainfitsfile is not a key in customargs raise an error
    else:
        emsg1 = ('If using custom arguments "mainfitsfile" must be a '
                 'key in "customargs"')
        emsg2 = '    function = {0}'.format(func_name)
        WLOG(p, 'error', [emsg1, emsg2])

    return p


def load_minimum(p, customargs=None, quiet=False):
    """
    Load minimal settings (without fitsfilename, arg_file_names, arg_file_dir
    etc)

    :param p: parameter dictionary, ParamDict containing constants
    :param customargs: None or list of strings, if list of strings then instead
                       of getting the standard runtime arguments

           i.e. in form:

                program.py night_dir arg_file_names[0] arg_file_names[1]...

           loads all arguments into customargs

           i.e. if customargs = ['night_dir', 'filename', 'a', 'b', 'c']
           expects command line arguments to be:

                program.py night_dir filename a b c

    :return p: dictionary, parameter dictionary
            Adds the following:
                program: string, the recipe/way the script was called
                         i.e. from sys.argv[0]
                log_opt: string, log option, normally the program name
                arg_night_name: string, empty (i.e. '')
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['ARG_NIGHT_NAME'])
                raw_dir: string, the raw data directory
                         (i.e. p['DRS_DATA_RAW']/p['ARG_NIGHT_NAME'])
    """
    # set source
    source = __NAME__ + '.load_minimum()'
    sconst = 'spirouConfig.Constants.'
    # get program name
    p['PROGRAM'] = spirouConfig.Constants.PROGRAM(p)
    p.set_source('PROGRAM', source + ' & {0}PROGRAM()'.format(sconst))
    # get the logging option
    p['LOG_OPT'] = p['PROGRAM']
    p.set_source('LOG_OPT', source + ' & {0}PROGRAM()'.format(sconst))
    # get night name and filenames
    p['ARG_NIGHT_NAME'] = spirouConfig.Constants.ARG_NIGHT_NAME(p)
    p.set_source('ARG_NIGHT_NAME',
                 source + ' & {0}ARG_NIGHT_NAME()'.format(sconst))
    # set reduced path
    p['REDUCED_DIR'] = spirouConfig.Constants.REDUCED_DIR(p)
    p.set_source('REDUCED_DIR', source + ' & {0}/REDUCED_DIR()')
    # set raw path
    p['RAW_DIR'] = spirouConfig.Constants.RAW_DIR(p)
    p.set_source('RAW_DIR', source + ' & {0}/RAW_DIR()')
    # -------------------------------------------------------------------------
    # load ICDP config file
    logthis = not quiet
    p = load_other_config_file(p, 'ICDP_NAME', required=True, logthis=logthis)
    # -------------------------------------------------------------------------
    # if we have customargs
    if customargs is not None:
        # loop around defined run time arguments
        for key in list(customargs.keys()):
            # set the value
            p[key] = customargs[key]
            p.set_source(key, 'From run time arguments (sys.argv)')
    # return p
    return p


# =============================================================================
# Define display functions
# =============================================================================
def display_drs_title(p):
    """
    Display title for this execution

    :param p: dictionary, parameter dictionary

    :return None:
    """
    # get colours
    colors = spirouConfig.Constants.Colors()

    # create title
    title = ' * '
    title += colors.RED1 + ' {DRS_NAME} ' + colors.okgreen + '@{PID}'
    title += ' (' + colors.BLUE1 + 'V{DRS_VERSION}' + colors.okgreen + ')'
    title += colors.ENDC
    title = title.format(**p)

    # Log title
    display_title(p, title)

    if p['DRS_DEBUG'] == 42:
        display_ee(p)


def display_title(p, title):
    """
    Display any title between HEADER bars via the WLOG command

    :param title: string, title string

    :return None:
    """
    # Log title
    WLOG(p, '', HEADER)
    WLOG(p, '', '{0}'.format(title), wrap=False)
    WLOG(p, '', HEADER)


def display_ee(p):
    # get colours
    colors = spirouConfig.Constants.Colors()
    # noinspection PyPep8
    logo = ['',
            '      `-+syyyso:.   -/+oossssso+:-`   `.-:-`  `...------.``                                 ',
            '    `ohmmmmmmmmmdy: +mmmmmmmmmmmmmy- `ydmmmh: sdddmmmmmmddho-                               ',
            '   `ymmmmmdmmmmmmmd./mmmmmmhhhmmmmmm-/mmmmmmo ymmmmmmmmmmmmmmo                              ',
            '   /mmmmm:.-:+ydmm/ :mmmmmy``.smmmmmo.ydmdho` ommmmmhsshmmmmmm.      ```                    ',
            '   ommmmmhs+/-..::  .mmmmmmoshmmmmmd- `.-::-  +mmmmm:  `hmmmmm`  `-/+ooo+:.   .:::.   .:/// ',
            '   .dmmmmmmmmmdyo.   mmmmmmmmmmmddo. oyyyhm/  :mmmmmy+osmmmmms  `osssssssss+` /sss-   :ssss ',
            '    .ohdmmmmmmmmmmo  dmmmmmdo+/:.`   ymmmmm/  .mmmmmmmmmmmmms`  +sss+..-ossso`+sss-   :ssss ',
            '   --.`.:/+sdmmmmmm: ymmmmmh         ymmmmm/   mmmmmmmmmddy-    ssss`   :ssss.osss.   :ssss ',
            '  +mmmhs/-.-smmmmmm- ommmmmm`        hmmmmm/   dmmmmm/sysss+.  `ssss-  `+ssss`osss`   :ssss ',
            ' -mmmmmmmmmmmmmmmms  /mmmmmm.        hmmmmm/   ymmmmm``+sssss/` /sssso+sssss- +sss:` .ossso ',
            ' -sdmmmmmmmmmmmmdo`  -mmmmmm/        hmmmmm:   smmmmm-  -osssss/`-osssssso/.  -sssssosssss+ ',
            '    ./osyhhhyo+-`    .mmmddh/        sddhhy-   /mdddh-    -//::-`  `----.      `.---.``.--. ',
            '']
    for line in logo:
        WLOG(p, '', colors.RED1 + line + colors.ENDC, wrap=False)
    WLOG(p, '', HEADER)

def display_initial_parameterisation(p):
    """
    Display initial parameterisation for this execution

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                DRS_DATA_RAW: string, the directory that the raw data should
                              be saved to/read from
                DRS_DATA_REDUC: string, the directory that the reduced data
                                should be saved to/read from
                DRS_CALIB_DB: string, the directory that the calibration
                              files should be saved to/read from
                DRS_DATA_MSG: string, the directory that the log messages
                              should be saved to
                PRINT_LEVEL: string, Level at which to print, values can be:
                                  'all' - to print all events
                                  'info' - to print info/warning/error events
                                  'warning' - to print warning/error events
                                  'error' - to print only error events
                LOG_LEVEL: string, Level at which to log, values can be:
                                  'all' - to print all events
                                  'info' - to print info/warning/error events
                                  'warning' - to print warning/error events
                                  'error' - to print only error events
                DRS_PLOT: bool, Whether to plot (True to plot)
                DRS_USED_DATE: string, the DRS USED DATE (not really used)
                DRS_DATA_WORKING: (optional) string, the temporary working
                                  directory
                DRS_INTERACTIVE: bool, True if running in interactive mode.
                DRS_DEBUG: int, Whether to run in debug mode
                                0: no debug
                                1: basic debugging on errors
                                2: recipes specific (plots and some code runs)

    :return None:
    """
    # Add initial parameterisation
    WLOG(p, '', '(dir_data_raw)      DRS_DATA_RAW={DRS_DATA_RAW}'.format(**p))
    WLOG(p, '', '(dir_data_reduc)    DRS_DATA_REDUC={DRS_DATA_REDUC}'
                ''.format(**p))
    WLOG(p, '', '(dir_drs_config)    DRS_CONFIG={DRS_CONFIG}'.format(**p))
    WLOG(p, '', '(dir_drs_uconfig)   DRS_UCONFIG={DRS_UCONFIG}'.format(**p))
    WLOG(p, '', '(dir_calib_db)      DRS_CALIB_DB={DRS_CALIB_DB}'.format(**p))
    WLOG(p, '', '(dir_tellu_db)      DRS_TELLU_DB={DRS_TELLU_DB}'.format(**p))
    WLOG(p, '', '(dir_data_msg)      DRS_DATA_MSG={DRS_DATA_MSG}'.format(**p))
    WLOG(p, '', '(drs_data_plot)     DRS_DATA_PLOT={DRS_DATA_PLOT}'.format(**p))
    # WLOG('', '', ('(print_log)         DRS_LOG={DRS_LOG}         '
    #               '%(0: minimum stdin-out logs)').format(**p))
    WLOG(p, '', ('(print_level)       PRINT_LEVEL={PRINT_LEVEL}         '
                 '%(error/warning/info/all)').format(**p))
    WLOG(p, '', ('(log_level)         LOG_LEVEL={LOG_LEVEL}         '
                 '%(error/warning/info/all)').format(**p))
    WLOG(p, '', ('(plot_graph)        DRS_PLOT={DRS_PLOT}            '
                 '%(def/undef/trigger)').format(**p))
    if p['DRS_DATA_WORKING'] is None:
        WLOG(p, '', ('(working_dir)       DRS_DATA_WORKING is not set, '
                     'running on-line mode'))
    else:
        WLOG(p, '', ('(working_dir)       DRS_DATA_WORKING={DRS_DATA_WORKING}'
                     '').format(**p))
    if p['DRS_INTERACTIVE'] == 0:
        WLOG(p, '', ('                    DRS_INTERACTIVE is not set, '
                     'running on-line mode'))
    else:
        WLOG(p, '', '                    DRS_INTERACTIVE is set')
    if p['DRS_DEBUG'] > 0:
        WLOG(p, '', ('                    DRS_DEBUG is set, debug mode level'
                     ':{DRS_DEBUG}').format(**p))
    WLOG(p, '', HEADER)


def display_run_files(p):
    """
    Display run files for this execution

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                log_opt: string, log option, normally the program name
                program: string, the recipe/way the script was called
                         i.e. from sys.argv[0]
                STR_FILE_NAMES: string, the "arg_file_names" in string form
                                separated by commas

    :return None:
    """
    WLOG(p, '', ('Now running : {PROGRAM} on file(s): '
                 '{STR_FILE_NAMES}').format(**p))
    tmp = spirouConfig.Constants.RAW_DIR(p)
    WLOG(p, '', 'On directory {0}'.format(tmp))


def display_custom_args(p, customargs):
    """
    Display the custom arguments that have been loaded

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                program: string, the recipe/way the script was called
                         i.e. from sys.argv[0]
                log_opt: string, log option, normally the program name
                customargs: the key/value pairs loaded from "customargs"

    :param customargs: dictionary, custom arguments

    :return None:
    """
    wmsg = 'Now running : {0} with: '.format(p['PROGRAM'])

    WLOG(p, '', wmsg)
    for customarg in customargs:
        wmsg = '       -- {0}={1} '.format(customarg, p[customarg])
        WLOG(p, '', wmsg)


def display_help_file(p):
    """
    If help file exists display it

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                arg_night_name: string, the folder within data raw directory
                                containing files (also reduced directory) i.e.
                                /data/raw/20170710 would be "20170710"
                arg_file_names: list, list of files taken from the command line
                                (or call to recipe function) must have at least
                                one string filename in the list
                log_opt: string, log option, normally the program name
                program: string, the recipe/way the script was called
                         i.e. from sys.argv[0]

    :return None:
    """

    # find help signal
    if 'HELP' in p['ARG_NIGHT_NAME'].upper():
        display_help = True
    else:
        display_help = False

    if 'arg_file_names' in p:
        for argfilename in p['ARG_FILE_NAMES']:
            if 'HELP' in argfilename.upper():
                display_help = True

    # do display help
    if display_help:
        # Log help file
        WLOG(p, '', 'HELP mode for  ' + p['PROGRAM'])
        # Get man file
        man_file = spirouConfig.Constants.MANUAL_FILE(p)
        # try to open man file
        if os.path.exists(man_file):
            try:
                f = open(man_file, 'r')
                print('\n')
                lines = f.readlines()
                for line in lines:
                    print(line)
                # then exit
                spirouConfig.Constants.EXIT()(1)
            except Exception as e:
                emsg1 = 'Cannot open help file {0}'.format(man_file)
                emsg2 = '   error {0} was: {1}'.format(type(e), e)
                WLOG(p, 'error', [emsg1, emsg2])

        # else print that we have no man file
        else:
            # log and exit
            emsg = 'No help file is not found for this recipe'
            WLOG(p, 'error', emsg)


# noinspection PyListCreation
def display_system_info(p, logonly=True, return_message=False):
    """
    Display system information via the WLOG command

    :param logonly: bool, if True will only display in the log (not to screen)
                    default=True, if False prints to both log and screen

    :param return_message: bool, if True returns the message to the call, if
                           False logs the message using WLOG

    :return None:
    """
    messages = [HEADER]
    messages.append(" * System information:")
    messages.append(HEADER)
    messages = sort_version(messages)
    messages.append("    Path = \"{0}\"".format(sys.executable))
    messages.append("    Platform = \"{0}\"".format(sys.platform))
    for it, arg in enumerate(sys.argv):
        messages.append("    Arg {0} = \"{1}\"".format(it + 1, arg))
    messages.append(HEADER)
    if return_message:
        return messages
    else:
        # return messages for logger
        WLOG(p, '', messages, logonly=logonly)

# =============================================================================
# End of code
# =============================================================================
