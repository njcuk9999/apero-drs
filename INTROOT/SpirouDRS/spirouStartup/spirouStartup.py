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
import os
import sys
from IPython import embed
import code

from SpirouDRS import spirouCDB
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouStarup.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# get the default log_opt
DPROG = spirouConfig.Constants.DEFAULT_LOG_OPT()
# -----------------------------------------------------------------------------
# define string types
TYPENAMES = {int: 'integer', float: 'float', list: 'list',
             bool: 'bool', str: 'str'}
# define the print/log header divider
HEADER = ' *****************************************'


# =============================================================================
# Define setup functions
# =============================================================================
def run_begin():
    """
    Begin DRS - Must be run at start of every recipe
    - loads the parameters from the primary configuration file, displays
      title, checks priamry constants and displays initial parameterization

    :return cparams: parameter dictionary, ParamDict constants from primary
                     configuration file
            Adds the following:
                all constants in primary configuration file
                DRS_NAME: string, the name of the DRS
                DRS_VERSION: string, the version of the DRS
    """
    # Get config parameters
    cparams = spirouConfig.ReadConfigFile()
    # get variables from spirouConst
    cparams['DRS_NAME'] = spirouConfig.Constants.NAME()
    cparams['DRS_VERSION'] = spirouConfig.Constants.VERSION()
    cparams.set_sources(['DRS_NAME', 'DRS_VERSION'], 'spirouConfig.Constants')
    # display title
    display_title(cparams)
    # check input parameters
    cparams = spirouConfig.CheckCparams(cparams)
    # display initial parameterisation
    display_initial_parameterisation(cparams)
    # display system info (log only)
    display_system_info()
    # return parameters
    return cparams


def load_arguments(cparams, night_name=None, files=None, customargs=None,
                   mainfitsfile=None, mainfitsdir=None):
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

                       stored in p['arg_night_name']

    :param files: list of strings or None, the files to use for this program

                  if None (undefined) uses the second and all other arguments in
                  the command line (i.e. sys.argv[2:])

                  if defined overwrites call from command line

                  stored in p['arg_file_names']

    :param customargs: None or list of strings, if list of strings then instead
                       of getting the standard runtime arguments

           i.e. in form:

                program.py rawdirectory arg_file_names[0] arg_file_names[1]...

           loads all arguments into customargs

           i.e. if customargs = ['rawdir', 'filename', 'a', 'b', 'c']
           expects command line arguments to be:

                program.py rawdir filename a b c

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

    :return p: dictionary, parameter dictionary
    """
    # -------------------------------------------------------------------------
    # deal with arg_night_name defined in call
    if night_name is not None:
        cparams['ARG_NIGHT_NAME'] = night_name
    # -------------------------------------------------------------------------
    # deal with run time arguments
    if customargs is None:
        cparams = run_time_args(cparams)
    else:
        cparams = run_time_custom_args(cparams, customargs)
    # -------------------------------------------------------------------------
    # deal with files being defined in call
    if files is not None:
        cparams['ARG_FILE_NAMES'] = files
        cparams['FITSFILENAME'] = files[0]
    # if files not defined we have custom arguments and hence need to define
    #    arg_file_names and fitsfilename manually
    elif mainfitsfile is not None and customargs is not None:
        cparams = get_custom_arg_files_fitsfilename(cparams, customargs,
                                                    mainfitsfile, mainfitsdir)
    # -------------------------------------------------------------------------
    # Display help file if needed
    display_help_file(cparams)
    # display run file
    if customargs is None:
        display_run_files(cparams)
    else:
        display_custom_args(cparams, customargs)
    # -------------------------------------------------------------------------
    # load special config file
    # TODO: is this needed as special_config_SPIROU does not exist
    cparams = load_other_config_file(cparams, 'SPECIAL_NAME', logthis=False)
    # load ICDP config file
    cparams = load_other_config_file(cparams, 'ICDP_NAME', required=True)
    # load keywords
    try:
        cparams, warnlogs = spirouConfig.GetKeywordArguments(cparams)
        # print warning logs
        for warnlog in warnlogs:
            WLOG('warning', DPROG, warnlog)
    except spirouConfig.ConfigError as e:
        WLOG(e.level, DPROG, e.message)
    # -------------------------------------------------------------------------
    # return parameter dictionary
    return cparams


def initial_file_setup(p, kind=None, prefixes=None, add_to_p=None,
                       calibdb=False):
    """
    Run start up code (based on program and parameters defined in p before)

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                log_opt: string, log option, normally the program name
                fitsfilename: string, the full path of for the main raw fits
                              file for a recipe
                              i.e. /data/raw/20170710/filename.fits
                program: string, the recipe/way the script was called
                         i.e. from sys.argv[0]
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['arg_night_name'])
                DRS_DATA_REDUC: string, the directory that the reduced data
                                should be saved to/read from
                DRS_CALIB_DB: string, the directory that the calibration
                              files should be saved to/read from

    :param kind: string, description of program we are running (i.e. dark)

    :param prefixes: list of strings, prefixes to look for in file name
    :param prefixes: list of strings, prefixes to look for in file name
                     will exit code if none of the prefixes are found
                     (prefix = None if no prefixes are needed to be found)

    :param add_to_p: dictionary structure:

            add_to_p[prefix1] = dict(key1=value1, key2=value2)
            add_to_p[prefix2] = dict(key3=value3, key4=value4)

            where prefix1 and prefix2 are the strings in "prefixes"

            This will add the sub dictionarys to the main parameter dictionary
            based on which prefix is found

            i.e. if prefix1 is found key "value3" and "value4" above are added
            (with "key3" and "key4") to the parameter dictionary p

    :param calibdb: bool, if True calibDB folder and files are required and
                    program will log and exit if they are not found
                    if False, program will create calibDB folder

    :return p: parameter dictionary, the updated parameter dictionary
            Adds the following:
                calibDB: dictionary, the calibration database dictionary
                prefixes from add_to_p (see spirouStartup.deal_with_prefixes)
    """

    log_opt = p['log_opt']
    fits_fn = p['fitsfilename']
    # -------------------------------------------------------------------------
    # check that fitsfilename exists
    if fits_fn is None:
        wmsg1 = 'Argument Error: No fits file defined at run time argument'
        wmsg2 = '    format must be:'
        emsg = '    >>> {0}.py [FOLDER] [FILES]'
        WLOG('error', log_opt, [wmsg1, wmsg2, emsg.format(p['program'])])
    if not os.path.exists(fits_fn):
        WLOG('error', log_opt, 'File : {0} does not exist'.format(fits_fn))
    # -------------------------------------------------------------------------
    # if we have prefixes defined then check that fitsfilename has them
    # if add_to_params is defined then add params to p accordingly
    p = deal_with_prefixes(p, kind, prefixes, add_to_p)
    # -------------------------------------------------------------------------
    # Reduced directory
    # construct reduced directory
    reduced_dir = p['reduced_dir']
    # if reduced directory does not exist create it
    if not os.path.isdir(p['DRS_DATA_REDUC']):
        os.makedirs(p['DRS_DATA_REDUC'])
    if not os.path.isdir(reduced_dir):
        os.makedirs(reduced_dir)
    # -------------------------------------------------------------------------
    # Calib DB setup
    p = load_calibdb(p, calibdb)
    # -------------------------------------------------------------------------
    # return the parameter dictionary
    return p


def load_calibdb(p, calibdb=True):
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
    if calibdb:
        if not os.path.exists(p['DRS_CALIB_DB']):
            WLOG('error', p['log_opt'],
                 'CalibDB: {0} does not exist'.format(p['DRS_CALIB_DB']))
        # then make sure files are copied
        spirouCDB.CopyCDBfiles(p)
        # then load the calibdb into p
        calib_db, p = spirouCDB.GetDatabase(p)
        p['calibDB'] = calib_db
        p.set_source('calibDB', __NAME__ + '/run_startup()')
    else:
        calib_dir = p['DRS_CALIB_DB']
        # if reduced directory does not exist create it
        if not os.path.isdir(calib_dir):
            os.makedirs(calib_dir)
    # return p (with calibration database)
    return p


def exit_script(ll):
    """
    Exit script for handling interactive endings to sessions (if DRS_PLOT is
    active)

    :param ll: dict, the local variables

    :return None:
    """
    # get parameter dictionary of constants (or create it)
    if 'p' in ll:
        p = ll['p']
    else:
        p = dict()
    # make sure we have DRS_PLOT
    if 'DRS_PLOT' not in p:
        p['DRS_PLOT'] = 0
    # make sure we have log_opt
    if 'log_opt' not in p:
        p['log_opt']=sys.argv[0]
    # if DRS_PLOT is 0 just return 0
    if not p['DRS_PLOT']:
        return 0
    # find whether user is in ipython or python
    if find_ipython():
        kind = 'ipython'
    else:
        kind = 'python'
    # log message
    wmsg = 'Press "Enter" to exit or [Y]es to continue in {0}'
    WLOG('', '', '')
    WLOG('', '', HEADER, printonly=True)
    WLOG('warning', p['log_opt'], wmsg.format(kind), printonly=True)
    WLOG('', '', HEADER, printonly=True)
    # deal with python 2 / python 3 input method
    if sys.version_info.major < 3:
        uinput = raw_input('')      # note python 3 wont find this!
    else:
        uinput = input('')
    # close any open plots properly
    spirouCore.sPlt.closeall()
    # if yes or YES or Y or y then we need to continue in python
    # this may require starting an interactive session
    if 'Y' in uinput.upper():
        # if user in ipython we need to try opening ipython
        if kind == 'ipython':
            try:
                # this is only to be used in this situation and should not
                # be used in general
                locals().update(ll)
                embed()
            except Exception:
                pass
        if not find_interactive():
            code.interact(local=ll)


# =============================================================================
# Define general functions
# =============================================================================
def run_time_args(p):
    """
    Get sys.argv arguments (run time arguments and use them to fill parameter
    dictionary

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                constants from primary configuration file

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
                             (i.e. p['DRS_DATA_REDUC']/p['arg_night_name'])
                raw_dir: string, the raw data directory
                         (i.e. p['DRS_DATA_RAW']/p['arg_night_name'])
    """
    # get constants name
    cname = spirouConfig.Constants.__NAME__

    # get program name
    p['program'] = spirouConfig.Constants.PROGRAM()
    p.set_source('program', cname + '/PROGRAM()')

    # get night name and filenames
    p['arg_night_name'] = spirouConfig.Constants.ARG_NIGHT_NAME(p)
    p.set_source('arg_night_name', cname + '/ARG_NIGHT_NAME')
    p['arg_file_names'] = spirouConfig.Constants.ARG_FILE_NAMES(p)
    p.set_source('arg_file_names', cname + '/ARG_FILE_NAMES')
    p['str_file_names'] = ', '.join(p['arg_file_names'])
    p.set_source('str_file_names', __NAME__ + '/run_time_args()')

    # get fitsfilename
    p['fitsfilename'] = spirouConfig.Constants.FITSFILENAME(p)
    p.set_source('fitsfilename', cname + '/FITSFILENAME()')

    # get the logging option
    p['log_opt'] = spirouConfig.Constants.LOG_OPT(p)
    p.set_source('log_opt', cname + '/LOG_OPT()')

    # Get number of frames
    p['nbframes'] = spirouConfig.Constants.NBFRAMES(p)
    p.set_source('nbframes', cname + '/NBFRAMES()')

    # set reduced path
    p['reduced_dir'] = spirouConfig.Constants.REDUCED_DIR(p)
    p.set_source('reduced_dir', cname + '/REDUCED_DIR()')
    # set raw path
    p['raw_dir'] = spirouConfig.Constants.RAW_DIR(p)
    p.set_source('raw_dir', cname + '/RAW_DIR()')

    # return updated parameter dictionary
    return p


def run_time_custom_args(p, customargs):
    """
    Get the custom arguments and add them (with some default arguments)
    to the constants parameter dictionary

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
        constants from primary configuration file

    :param customargs:

    :return p: parameter dictionary, the updated parameter dictionary
            Adds the following:
                program: string, the recipe/way the script was called
                         i.e. from sys.argv[0]
                log_opt: string, log option, normally the program name
                arg_night_name: string, the folder within data raw directory
                                containing files (also reduced directory) i.e.
                                /data/raw/20170710 would be "20170710"
                reduced_dir: string, the reduced data directory
                             (i.e. p['DRS_DATA_REDUC']/p['arg_night_name'])
                raw_dir: string, the raw data directory
                         (i.e. p['DRS_DATA_RAW']/p['arg_night_name'])
                customargs: "customargs" added from call
    """
    # set source
    source = __NAME__ + '/run_time_custom_args()'
    sconst = 'spirouConfig.Constants.'
    # get program name
    p['program'] = spirouConfig.Constants.PROGRAM()
    p.set_source('program', source + ' & {0}PROGRAM()'.format(sconst))
    # get the logging option
    p['log_opt'] = p['program']
    p.set_source('log_opt', source + ' & {0}PROGRAM()'.format(sconst))
    # get night name and filenames
    p['arg_night_name'] = spirouConfig.Constants.ARG_NIGHT_NAME(p)
    p.set_source('arg_night_name',
                 source + ' & {0}ARG_NIGHT_NAME()'.format(sconst))
    # set reduced path
    p['reduced_dir'] = spirouConfig.Constants.REDUCED_DIR(p)
    p.set_source('reduced_dir', source + ' & {0}/REDUCED_DIR()')
    # set raw path
    p['raw_dir'] = spirouConfig.Constants.RAW_DIR(p)
    p.set_source('raw_dir', source + ' & {0}/RAW_DIR()')

    # loop around defined run time arguments
    for key in list(customargs.keys()):
        # set the value
        p[key] = customargs[key]
        p.set_source(key, 'From run time arguments (sys.argv)')

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
        p = spirouConfig.LoadConfigFromFile(p, key, required=required,
                                            logthis=logthis)
    except spirouConfig.ConfigError as e:
        WLOG(e.level, p['log_opt'], e.message)
    # return parameter dictionary
    return p


def deal_with_prefixes(p, kind, prefixes, add_to_p):
    """
    Deals with finding the prefixes and adding any add_to_p values to p

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                log_opt: string, log option, normally the program name
                arg_file_names: list, list of files taken from the command line
                                (or call to recipe function) must have at least
                                one string filename in the list

    :param kind: string, description of program we are running (i.e. dark)

    :param prefixes: list of strings, prefixes to look for in file name
                     will exit code if none of the prefixes are found
                     (prefix = None if no prefixes are needed to be found)

    :param add_to_p: dictionary structure:

            add_to_p[prefix1] = dict(key1=value1, key2=value2)
            add_to_p[prefix2] = dict(key3=value3, key4=value4)

            where prefix1 and prefix2 are the strings in "prefixes"

            This will add the sub dictionaries to the main parameter dictionary
            based on which prefix is found

            i.e. if prefix1 is found key "value3" and "value4" above are added
            (with "key3" and "key4") to the parameter dictionary p

    :return p: parameter dictionary, the updated parameter dictionary
            Adds the following:
                the subdictionary key/value pairs in "add_to_p" that contains
                the correct prefix for p["arg_file_names"][0]
    """
    if prefixes is None:
        return p
    # get variables from p
    log_opt = p['log_opt']
    arg_fn1 = p['arg_file_names'][0]
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
        wmsg = 'Correct type of image for {0} ({1})'
        WLOG('info', log_opt, wmsg.format(kind, ' or '.join(prefixes)))
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
        wmsg = 'Wrong type of image for {0}, should be {1}'
        WLOG('error', log_opt, wmsg.format(kind, ' or '.join(prefixes)))


def get_arguments(positions, types, names, required, calls, cprior, lognames):
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

    :param lognames: list of strings, the names displayed in the log (on error)
                     theses should be similar to "names" but in a form the
                     user can easily understand for each variable

    :return dict: dictionary containing the run time arguments converts to
                  "types", keys are equal to "names"
    """
    # set up the dictionary
    customdict = dict()
    for pos in positions:
        # deal with not having enough arguments
        try:
            # get from sys.argv
            # first arg should be the program name
            # second arg should be the night name
            raw_value = sys.argv[pos + 2]
        except IndexError:
            # if not required then it is okay to not find it
            if not required[pos]:
                raw_value = None
            # if calls is None and required = True then we should exit now
            elif calls is None or calls[pos] is None:
                emsgs = []

                emsgs.append(('Argument Error: "{0}" is not defined'
                              ''.format(lognames[pos])))

                emsgs.append(('   must be format:'
                              ''.format(pos + 1)))
                eargs = [DPROG, ' '.join(lognames)]
                emsgs.append(('   >>> {0} NIGHT_NAME {1}'
                              ''.format(*eargs)))
                WLOG('error', DPROG, emsgs)
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
            emsg = ('Arguments Error: "{0}" should be a {1} (Value = {2})')
            eargs = [lognames[pos], TYPENAMES[kind], raw_value]
            WLOG('error', DPROG, emsg.format(*eargs))
        except TypeError:
            pass
    # return dict
    return customdict


def get_multi_last_argument(customdict, positions, types, names, lognames):
    """
    Takes the largest argument in "positions" and pushes all further arguments
    into a list under names[max(positions)], all further arguments are
    required to conform to the type "types[max(positions)] and
    names[max(position)] becomes a list of types[max(positions)]

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
                  "types", keys are equal to "names"
                  dict[names[max(positions)] is updated to be a list of
                  type types[max(positions)]
    """
    # get the last position and name/type for it
    maxpos = np.max(positions)
    maxname = names[maxpos]
    maxkind = types[maxpos]
    # check the length of sys.argv (needs to be > maxpos + 2)
    if len(sys.argv) > maxpos + 2:
        # convert maxname to a list
        customdict[maxname] = [customdict[maxname]]
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
                WLOG('error', DPROG, emsg.format(*eargs))
    # return the new custom dictionary
    return customdict


def get_files(p, path, names, prefix=None, kind=None):
    """
    Get a set of full file path and check the path and file exist
    (wrapper around get_files)

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                log_opt: string, log option, normally the program name
                program: string, the recipe/way the script was called
                         i.e. from sys.argv[0]

    :param path: string, either the directory to the folder (if name is None) or
                 the full path to the files
    :param names: list of strings, the names of the files
    :param prefix: string or None, if not None this substring must be in the
                   filenames
    :param kind: string or None, the type of files (for logging)

    :return locations: list of strings, the full file paths of the files
    """
    # define storage for locations
    locations = []
    # loop around names of files
    for name in names:
        locations.append(get_file(p, path, name, prefix, kind))
    # if all conditions passed return full path
    return locations


def get_file(p, path, name=None, prefix=None, kind=None):
    """
    Get full file path and check the path and file exist

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                log_opt: string, log option, normally the program name
                program: string, the recipe/way the script was called
                         i.e. from sys.argv[0]

    :param path: string, either the directory to the folder (if name is None) or
                 the full path to the file
    :param name: string or None, the name of the file, if None name is assumed
                 to be in path
    :param prefix: string or None, if not None this substring must be in the
                   filename
    :param kind: string or None, the type of file (for logging)

    :return location: string, the full file path of the file
    """

    # if path is None and name is None
    if path is None:
        WLOG('error', p['log_opt'], 'No file defined')
    # if name and path are not None
    if name is None:
        name = os.path.split(path)[-1]
        path = path.split(name)[0]
    # join path and name
    location = os.path.join(path, name)
    # test if path exists
    if not os.path.exists(path):
        emsg = 'Directory: {0} does not exist'
        WLOG('error', p['log_opt'], emsg.format(path))
    # test if path + file exits
    if not os.path.exists(location):
        emsg = 'File : {0} does not exist at location {1}'
        WLOG('error', p['log_opt'], emsg.format(name, path))
    # if prefix is defined make sure file conforms
    wmsg = 'Now processing Image TYPE {0} with {1} recipe'
    if prefix is not None:
        # deal with no kind
        if kind is None:
            kind = 'UNKNOWN'
        # look for prefix in name
        if prefix not in name:
            emsg = 'Wrong type of image for {0}, should be {1}'
            emsg2 = '  tried to load file: {0}'
            WLOG('', p['log_opt'], emsg.format(kind, prefix))
            WLOG('error', p['log_opt'], emsg2.format(location))
        else:
            WLOG('info', p['log_opt'], wmsg.format(kind, p['program']))
    else:
        WLOG('info', p['log_opt'], wmsg.format(kind, p['program']))
    # if all conditions passed return full path
    return location


def get_fiber_type(p, filename, fibertypes=None):
    """
    Get fiber types and search for a valid fiber type in filename

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                FIBER_TYPES: list of strings, the types of fiber available
                             (i.e. ['AB', 'A', 'B', 'C'])
                log_opt: string, log option, normally the program name

    :param filename: string, the filename to search for fiber types in
    :param fibertypes: list of strings, the fiber types to search for

    :return fiber: string, the fiber found (exits via WLOG if no fiber found)
    """
    # deal with no fiber types
    if fibertypes is None:
        fibertypes = p['FIBER_TYPES']
    # loop around each fiber type
    for fiber in fibertypes:
        if fiber in filename:
            return fiber
    # if we have reached this type then we have no recognized fiber
    emsg = 'Fiber name not recognized (must be in {0})'
    WLOG('error', p['log_opt'], emsg.format(', '.join(fibertypes)))


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


def find_ipython():
    """
    Find whether user is using ipython or python

    :return using_ipython: bool, True if using ipython, false otherwise
    """
    try:
        __IPYTHON__             # Note python wont define this, ipython will
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
    vstr = sys.version
    version = vstr.split('|')[0].strip()
    build = vstr.split('|')[1].strip()
    date = vstr.split(build)[1].split('(')[1].split(')')[0].strip()
    other = vstr.split('[')[1].split(']')[0].strip()
    # add version info to messages
    messages.append('    Python version = {0}'.format(version))
    messages.append('    Python distribution = {0}'.format(build))
    messages.append('    Distribution date = {0}'.format(date))
    messages.append('    Dist Other = {0}'.format(other))
    # return updated messages
    return messages


# =============================================================================
# Define custom argument functions
# =============================================================================
def get_custom_from_run_time_args(positions=None, types=None, names=None,
                                  required=None, calls=None, cprior=None,
                                  lognames=None, last_multi=False):
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

    :param lognames: list of strings, the names displayed in the log (on error)
                     theses should be similar to "names" but in a form the
                     user can easily understand for each variable

    :param last_multi: bool, if True then last argument in positions/types/
                       names adds all additional arguments into a list

    :return values: dictionary, if run time arguments are correct python type
                    the name-value pairs are returned
    """
    # deal with no positions (use length of types or names or exit with error)
    if positions is None:
        if types is not None:
            positions = range(len(types))
        elif names is not None:
            positions = range(len(names))
        else:
            emsg = ('Either "positions", "name" or "types" must be defined to'
                    'get custom arguments.')
            WLOG('', DPROG, emsg)
    # deal with no types (set to strings)
    if types is None:
        types = [str]*len(positions)
    # deal with no names (set to Arg0, Arg1, Arg2 etc)
    if names is None:
        names = ['Arg{0}'.format(pos) for pos in positions]
    if lognames is None:
        lognames = names
    # deal with no required (set all to be required)
    if required is None:
        required = [True]*len(positions)
    # deal with no calls priority (set priority for calls to False)
    if cprior is None:
        cprior = [False]*len(positions)
    # loop around positions test the type and add the value to dictionary
    customdict = get_arguments(positions, types, names, required, calls,
                                cprior, lognames)
    # deal with the position needing to find additional parameters
    if last_multi:
        customdict = get_multi_last_argument(customdict, positions, types,
                                             names, lognames)
    # finally return dictionary
    return customdict


def get_custom_arg_files_fitsfilename(cparams, customargs, mff, mfd=None):
    """
    Deal with having to set arg_file_names and fitsfilenames manually
    uses "mff" the main fits filename and "mdf" the main fits file directory

    :param cparams: parameter dictionary, ParamDict containing constants
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

                program.py rawdirectory arg_file_names[0] arg_file_names[1]...

           loads all arguments into customargs

           i.e. if customargs = ['rawdir', 'filename', 'a', 'b', 'c']
           expects command line arguments to be:

                program.py rawdir filename a b c

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
    :return cparams: parameter dictionary, the updated parameter dictionary
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
    # define the raw/reduced/calib folder from cparams
    raw = os.path.join(cparams['DRS_DATA_RAW'], cparams['arg_night_name'])
    red = os.path.join(cparams['DRS_DATA_REDUC'], cparams['arg_night_name'])
    calib = cparams['DRS_CALIB_DB']
    # mainfitsfile must be a key in customargs
    if mff in customargs:
        # the value of mainfitsfile must be a string or list of strings
        #    if it isn't raise an error
        mfv = customargs[mff]
        # check if mainfitsvalue is a full path
        if not os.path.exists(mfv):
            # check if mainfits dir is defined
            if mfd is not None:
                tpath = os.path.join(mfd, mfv)
                # if path exists then use it
                if os.path.exists(tpath):
                    mfv = os.path.join(mfd, mfv)
                elif mfd == 'reduced':
                    mfv = os.path.join(red, mfv)
                elif mfd == 'calibdb':
                    mfv = os.path.join(calib, mfv)
                else:
                    emsg1 = '"mainfitsdir"={0} not a valid path/option'
                    emsg2 = '    function = {0}'.format(func_name)
                    WLOG('error', DPROG, [emsg1.format(mfd), emsg2])
                    mfv = ''
                    # if mainfits dir is not defined make the path the raw
            else:
                # redefine the mainfits file
                mfv = os.path.join(raw, mfv)
        # test type mainfitsfile (must be str or list)
        if type(mff) == str:
            cparams['ARG_FILE_NAMES'] = [mfv]
            cparams['FITSFILENAME'] = mfv
        elif type(mff) == list:
            cparams['ARG_FILE_NAMES'] = mfv
            cparams['FITSFILENAME'] = mfv[0]
        else:
            eargs = [mff, mfv]
            emsg1 = ('The value of mainfitsfile: "{0}"={1} must be a '
                     'valid python string or list').format(*eargs)
            emsg2 = '    function = {0}'.format(func_name)
            WLOG('error', DPROG, [emsg1, emsg2])
    # if mainfitsfile is not a key in customargs raise an error
    else:
        emsg1 = ('If using custom arguments "mainfitsfile" must be a '
                 'key in "customargs"')
        emsg2 = '    function = {0}'.format(func_name)
        WLOG('error', DPROG, [emsg1, emsg2])

    return cparams


# =============================================================================
# Define display functions
# =============================================================================
def display_title(p):
    """
    Display title for this execution

    :param p: dictionary, parameter dictionary

    :return None:
    """
    # Log title
    WLOG('', '', HEADER)
    WLOG('', '',
         ' * {DRS_NAME} @(#) Geneva Observatory ({DRS_VERSION})'.format(**p))
    WLOG('', '', HEADER)


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
    WLOG('', '',
         '(dir_data_raw)      DRS_DATA_RAW={DRS_DATA_RAW}'.format(**p))
    WLOG('', '',
         '(dir_data_reduc)    DRS_DATA_REDUC={DRS_DATA_REDUC}'.format(**p))
    # WLOG('', '',
    #      '(dir_drs_config)    DRS_CONFIG={DRS_CONFIG}'.format(**p))
    WLOG('', '',
         '(dir_calib_db)      DRS_CALIB_DB={DRS_CALIB_DB}'.format(**p))
    WLOG('', '',
         '(dir_data_msg)      DRS_DATA_MSG={DRS_DATA_MSG}'.format(**p))
    # WLOG('', '', ('(print_log)         DRS_LOG={DRS_LOG}         '
    #               '%(0: minimum stdin-out logs)').format(**p))
    WLOG('', '', ('(print_level)       PRINT_LEVEL={PRINT_LEVEL}         '
                  '%(error/warning/info/all)').format(**p))
    WLOG('', '', ('(log_level)         LOG_LEVEL={LOG_LEVEL}         '
                  '%(error/warning/info/all)').format(**p))
    WLOG('', '', ('(plot_graph)        DRS_PLOT={DRS_PLOT}            '
                  '%(def/undef/trigger)').format(**p))
    WLOG('', '', ('(used_date)         DRS_USED_DATE={DRS_USED_DATE}'
                  '').format(**p))
    if p['DRS_DATA_WORKING'] is None:
        WLOG('', '', ('(working_dir)       DRS_DATA_WORKING is not set, '
                      'running on-line mode'))
    else:
        WLOG('', '', ('(working_dir)       DRS_DATA_WORKING={DRS_DATA_WORKING}'
                      '').format(**p))
    if p['DRS_INTERACTIVE'] == 0:
        WLOG('', '', ('                    DRS_INTERACTIVE is not set, '
                      'running on-line mode'))
    else:
        WLOG('', '', '                    DRS_INTERACTIVE is set')
    if p['DRS_DEBUG'] > 0:
        WLOG('', '', ('                    DRS_DEBUG is set, debug mode level'
                      ':{DRS_DEBUG}').format(**p))


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
    WLOG('', p['log_opt'], ('Now running : {PROGRAM} on file(s): '
                            '{STR_FILE_NAMES}').format(**p))
    tmp = spirouConfig.Constants.RAW_DIR(p)
    WLOG('', p['log_opt'], 'On directory {0}'.format(tmp))


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

    wmsg = 'Now running : {0} with: '.format(p['program'])

    WLOG('', p['log_opt'], wmsg)
    for customarg in customargs:
        wmsg = '       -- {0}={1} '.format(customarg, p[customarg])
        WLOG('', p['log_opt'], wmsg)


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
    if 'HELP' in p['arg_night_name'].upper():
        display_help = True
    else:
        display_help = False

    if 'arg_file_names' in p:
        for argfilename in p['arg_file_names']:
            if 'HELP' in argfilename.upper():
                display_help = True

    # do display help
    if display_help:
        # Log help file
        WLOG('', p['log_opt'], 'HELP mode for  ' + p['program'])
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
                WLOG('error', p['log_opt'], [emsg1, emsg2])

        # else print that we have no man file
        else:
            # log and exit
            emsg = 'No help file is not found for this recipe'
            WLOG('error', p['log_opt'], emsg)


def display_system_info():
    """
    Display system information

    :return messages: list of strings, the system information
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
    # return messages for logger
    WLOG('', '', messages, logonly=True)




# =============================================================================
# End of code
# =============================================================================
