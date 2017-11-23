#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
spirouStartup.py

Start up to be executed at beginning of all codes

Created on 2017-10-11 at 10:48

@author: cook

Version 0.0.1

Last modified: 2017-10-11 at 10:49
"""
import os
import sys

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
# Get Logging function
WLOG = spirouCore.wlog
# -----------------------------------------------------------------------------


# =============================================================================
# Define run functions
# =============================================================================
def run_initial_startup(night_name=None, files=None, customargs=None):
    """
    Run initial start up:

    1) Read main config file
    2) check certain parameters exist
    3) display title
    4) display initial parameterisation
    5) display help file (if requested and exists)
    6) loads run time arguments (and custom arguments, see below)
    7) loads other config files

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

    :return p: dictionary, parameter dictionary
    """

    # Get config parameters
    cparams = spirouConfig.ReadConfigFile()
    # check that drs_name and drs_version exist
    spirouConfig.CheckConfig(cparams, ['DRS_NAME', 'DRS_VERSION'])
    # display title
    display_title(cparams)
    # check input parameters
    cparams = spirouConfig.CheckCparams(cparams)
    # display initial parameterisation
    display_initial_parameterisation(cparams)
    # deal with arg_night_name defined in call
    if night_name is not None:
        cparams['ARG_NIGHT_NAME'] = night_name
    # deal with files being defined in call
    if files is not None:
        cparams['ARG_FILE_NAMES'] = files
    # deal with run time arguments
    if customargs is None:
        cparams = run_time_args(cparams)
    else:
        cparams = run_time_custom_args(cparams, customargs)
    # Display help file if needed
    display_help_file(cparams)
    # display run file
    if customargs is None:
        display_run_files(cparams)
    else:
        display_custom_args(cparams, customargs)
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
            WLOG('warning', '', warnlog)
    except spirouConfig.ConfigError as e:
        WLOG(e.level, '', e.message)
    # return parameter dictionary
    return cparams


def run_startup(p, kind=None, prefixes=None, add_to_p=None, calibdb=False):
    """
    Run start up code (based on program and parameters defined in p before)


    :param p: dictionary, parameter dictionary

    :param kind: string, description of program we are running (i.e. dark)

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

    :return p: dictionary, parameter dictionary
    """

    log_opt = p['log_opt']
    fits_fn = p['fitsfilename']
    # -------------------------------------------------------------------------
    # check that fitsfilename exists
    if fits_fn is None:
        WLOG('error', log_opt, 'No fits file defined in run time argument'
                               ' format must be: {0}.py [FOLDER] [FILES]'
                               ''.format(p['program']))
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
    if calibdb:
        if not os.path.exists(p['DRS_CALIB_DB']):
            WLOG('error', log_opt,
                 'CalibDB: {0} does not exist'.format(p['DRS_CALIB_DB']))
        # then make sure files are copied
        spirouCDB.CopyCDBfiles(p)
        # then load the calibdb into p
        calibDB, p = spirouCDB.GetDatabase(p)
        p['calibDB'] = calibDB
        p.set_source('calibDB', __NAME__ + '/run_startup()')
    else:
        calib_dir = p['DRS_CALIB_DB']
        # if reduced directory does not exist create it
        if not os.path.isdir(calib_dir):
            os.makedirs(calib_dir)

    # -------------------------------------------------------------------------
    # return the parameter dictionary
    return p


# =============================================================================
# Define general functions
# =============================================================================

def run_time_args(p):
    """
    Get sys.argv arguments (run time arguments and use them to fill parameter
    dictionary

    :param p: dictionary, parameter dictionary
    :return p: dictionary, the updated parameter dictionary
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

    return p


def run_time_custom_args(p, customargs):

    rparams = list(sys.argv)
    p['program'] = spirouConfig.Constants.PROGRAM()
    p['log_opt'] = p['program']
    p.set_source('log_opt', __NAME__ + '/run_time_custom_args()')

    if len(rparams) == 1:
        WLOG('error', '', 'No arguments defined - cannot used customargs')
    if len(rparams) > 1:
        # loop around defined run time arguments
        for r_it in range(1, len(rparams)):
            # try to get the custom name for this argument (from customargs)
            try:
                customarg = str(customargs[r_it - 1])
            # if there are too many run time arguments then create an error
            except IndexError:
                emsg = ('Too many arguments defined there must be {0} defined')
                WLOG('error', p['log_opt'], emsg.format(len(customargs)))
                customarg = None
            except SyntaxError:
                emsg = ('Invalid string in customargs. Please redefine')
                WLOG('error', p['log_opt'], emsg)

            # try to evaluate the argument (int/float/list/bool)
            try:
                value = eval(str(rparams[r_it]))
                # if not int/float/list/bool set to string
                if type(value) not in [int, float, list, bool]:
                    value = str(rparams[r_it])
            # if we cannot evaluate set to a string
            except NameError:
                value = str(rparams[r_it])
            # set the value
            p[customarg] = value
            p.set_source(customarg, 'From run time arguments (sys.argv)')

    return p


def load_other_config_file(p, key, logthis=True, required=False):
    # try to load config file from file
    try:
        p = spirouConfig.LoadConfigFromFile(p, key, required=required,
                                            logthis=logthis)
    except spirouConfig.ConfigError as e:
        WLOG(e.level, p['log_opt'], e.message)

    return p


def deal_with_prefixes(p, kind, prefixes, add_to_p):
    """
    Deals with finding the prefixes and adding any add_to_p values to p


    :param p: dictionary, parameter dictionary

    :param kind: string, description of program we are running (i.e. dark)

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

    :return:
    """
    if prefixes is None:
        return p

    log_opt = p['log_opt']
    arg_fn1 = p['arg_file_names'][0]
    program = p['program']

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
            # elif fprefix is not in a2p (if set up correctly it should be)
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


# =============================================================================
# Define display functions
# =============================================================================
def display_title(p):
    """
    Display title for this execution

    :param p: dictionary, parameter dictionary
    :return:
    """
    # Log title
    WLOG('', '', ' *****************************************')
    WLOG('', '',
         ' * {DRS_NAME} @(#) Geneva Observatory ({DRS_VERSION})'.format(**p))
    WLOG('', '', ' *****************************************')


def display_initial_parameterisation(p):
    """
    Display initial parameterisation for this execution

    :param p: dictionary, parameter dictionary
    :return:
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
    WLOG('', '', ('(log_level)         LOG_LEVEL={PRINT_LEVEL}         '
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

    :param p: dictionary, parameter dictionary
    :return:
    """
    WLOG('', p['log_opt'], ('Now running : {PROGRAM} on file(s): '
                            '{STR_FILE_NAMES}').format(**p))
    tmp = spirouConfig.Constants.RAW_DIR(p)
    WLOG('', p['log_opt'], 'On directory {0}'.format(tmp))


def display_custom_args(p, customargs):

    wmsg = 'Now running : {0} with '.format(p['program'])
    for customarg in customargs:
        wmsg += '{0}={1} '.format(customarg, p[customarg])
    WLOG('', p['log_opt'], wmsg)


def display_help_file(p):

    if 'arg_night_name' not in list(p.keys()):
        if 'HELP' not in list(p.keys()):
            return 0

    if p['arg_night_name'] != "HELP":
        return 0
    else:
        # Log help file
        WLOG('', p['log_opt'], 'HELP mode for  ' + p['program'])
        # Get man file
        man_file = spirouConfig.Constants.MANUAL_FILE(p)
        # try to open man file
        if os.path.exists(man_file):
            f = open(man_file, 'r')
            print('\n')
            lines = f.readlines()
            for line in lines:
                print(line)
        # else print that we have no man file
        else:
            # log and exit
            WLOG('info', p['log_opt'], 'INFO file is not found for this recipe')


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
