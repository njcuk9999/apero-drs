#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
startupfunctions.py

Start up to be executed at beginning of all codes

Created on 2017-10-11 at 10:48

@author: cook

Version 0.0.1

Last modified: 2017-10-11 at 10:49
"""
import os
import sys

from . import configsetup
from . import log

# =============================================================================
# Define variables
# =============================================================================
WLOG = log.logger
LOGLEVELS = list(log.TRIG_KEY.keys())
# -----------------------------------------------------------------------------


# =============================================================================
# Define run functions
# =============================================================================
def run_inital_startup():
    """
    Run initial start up:

    1) Read main config file
    2) check certain parameters exist
    3) display title
    4) display initial parameterisation
    5) display help file (if requested and exists)
    6) loads run time arguments
    7) loads other config files

    :return p: dictionary, parameter dictionary
    """

    # Get config parameters
    cparams = configsetup.read_config_file()
    # check that drs_name and drs_version exist
    tmp = configsetup.check_config(cparams, ['DRS_NAME', 'DRS_VERSION'])
    if tmp is not None:
        WLOG('error', ' ', tmp)
        sys.exit(1)
    # display title
    display_title(cparams)
    # check input parameters
    cparams = check_params(cparams)
    # display initial parameterisation
    display_initial_parameterisation(cparams)
    # deal with run time arguments
    cparams = run_time_args(cparams)
    # Display help file if needed
    display_help_file(cparams)
    # display run file
    display_run_files(cparams)
    # load special config file
    # TODO: is this needed as special_config_SPIROU does not exist
    cparams = load_other_config_file(cparams, 'SPECIAL_NAME', logthis=False)
    # load ICDP config file
    cparams = load_other_config_file(cparams, 'ICDP_NAME', required=True)
    # return parameter dictionary
    return cparams


def run_startup(p, kind, prefixes=None, add_to_p=None, calibdb=False):
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

    :param calibdb: bool, whether to search for and load the calibDB

    :return p: dictionary, parameter dictionary
    """

    log_opt = p['log_opt']
    fits_fn = p['fitsfilename']
    arg_nn = p['arg_night_name']
    # -------------------------------------------------------------------------
    # check that fitsfilename exists
    if fits_fn is None:
        WLOG('error', log_opt, 'No fits file defined in run time argument'
                               ' format must be: {0}.py [FOLDER] [FILES]'
                               ''.format(p['program']))
        sys.exit(1)
    if not os.path.exists(fits_fn):
        WLOG('error', log_opt, 'File : {0} does not exist'.format(fits_fn))
        sys.exit(1)
    # -------------------------------------------------------------------------
    # if we have prefixes defined then check that fitsfilename has them
    # if add_to_params is defined then add params to p accordingly
    p = deal_with_prefixes(p, kind, prefixes, add_to_p)
    # -------------------------------------------------------------------------
    # Reduced directory
    # construct reduced directory
    reduced_dir = os.path.join(p['DRS_DATA_REDUC'], arg_nn)
    # if reduced directory does not exist create it
    if not os.path.isdir(p['DRS_DATA_REDUC']):
        os.makedirs(p['DRS_DATA_REDUC'])
    if not os.path.isdir(reduced_dir):
        os.makedirs(reduced_dir)
    # -------------------------------------------------------------------------
    # Calib DB setup
    calib_dir = os.path.join(p['DRS_CALIB_DB'])
    # if reduced directory does not exist create it
    if not os.path.isdir(calib_dir):
        os.makedirs(calib_dir)


    # TODO: Need to do calibDB stuff

    # TODO: anything else that needs adding to start up
    # -------------------------------------------------------------------------
    # return the parameter dictionary
    return p


# =============================================================================
# Define general functions
# =============================================================================
def check_params(p):
    """
    Check the parameter dictionary has certain required values

    :param p: dictionary, parameter dictionary
    :return p: dictionary, the updated parameter dictionary
    """
    # check that the drs_root and tdata variables are named
    tmp = configsetup.check_config(p, ['DRS_ROOT', 'TDATA'])
    if tmp is not None:
        WLOG('error', ' ', tmp)
        sys.exit(1)
    # check whether we have drs_data_raw key
    tmp = os.path.join(p['TDATA'], 'raw', '')
    p['DRS_DATA_RAW'] = p.get('DRS_DATA_RAW', tmp)

    # check whether we have drs_data_reduc key
    tmp = os.path.join(p['TDATA'], 'reduced', '')
    p['DRS_DATA_REDUC'] = p.get('DRS_DATA_REDUC', tmp)

    # check whether we have drs_data_msg key
    tmp = os.path.join(p['TDATA'], 'msg', '')
    p['DRS_DATA_MSG'] = p.get('DRS_DATA_MSG', tmp)

    # check whether we have drs_calib_db key
    tmp = os.path.join(p['TDATA'], 'calibDB', '')
    p['DRS_CALIB_DB'] = p.get('DRS_CALIB_DB', tmp)

    # check whether we have a drs_config key
    tmp = os.path.join(p['DRS_ROOT'], 'config', '')
    p['DRS_CONFIG'] = p.get('DRS_CONFIG', tmp)

    # check whether we have a drs_man key
    tmp = os.path.join(p['DRS_ROOT'], 'man', '')
    p['DRS_MAN'] = p.get('DRS_MAN', tmp)

    # check that drs_log exists else set to 1
    # cparams['DRS_LOG'] = cparams.get('DRS_LOG', 1)

    # check that drs_plot exists else set to 'NONE'
    p['DRS_PLOT'] = p.get('DRS_PLOT', 'undefined')

    # check whether we have a drs_config key
    p['DRS_DATA_WORKING'] = p.get('DRS_DATA_WORKING', None)

    # check that drs_used_date exists else set to 'undefined'
    p['DRS_USED_DATE'] = p.get('DRS_USED_DATE', 'undefined')

    # check that drs_debug exists else set to 0
    p['DRS_DEBUG'] = p.get('DRS_DEBUG', 0)

    # check that drs_interactive set else set to 0
    p['DRS_INTERACTIVE'] = p.get('DRS_INTERACTIVE', 0)

    # check that print_level is defined and make sure it is in defined levels
    #    default value is 'all' if doesnt exist or wrong
    p['PRINT_LEVEL'] = p.get('PRINT_LEVEL', 'all')
    if p['PRINT_LEVEL'] not in LOGLEVELS:
        p['PRINT_LEVEL'] = 'all'

    # check that print_level is defined and make sure it is in defined levels
    #    default value is 'all' if doesnt exist or wrong
    p['LOG_LEVEL'] = p.get('LOG_LEVEL', 'all')
    if p['LOG_LEVEL'] not in LOGLEVELS:
        p['LOG_LEVEL'] = 'all'
    # return parameters
    return p


def run_time_args(p):
    """
    Get sys.argv arguments (run time arguments and use them to fill parameter
    dictionary

    :param p: dictionary, parameter dictionary
    :return p: dictionary, the updated parameter dictionary
    """
    # get run time parameters
    rparams = list(sys.argv)
    # get program name
    program = os.path.basename(rparams[0]).split('.py')[0]

    # get night name and filenames
    arg_file_names, arg_night_name = [], ''
    if len(rparams) > 1:
        arg_night_name = str(rparams[1])
        for r_it in range(2, len(rparams)):
            arg_file_names.append(str(rparams[r_it]))

    # deal with the log_opt "log option"
    #    either {program}   or {program}:{prefix}   or {program}:{prefix}+[...]
    if len(arg_file_names) == 0:
        log_opt = program
    elif len(arg_file_names) == 1:
        index = arg_file_names[0].find('.')
        lo_arg = [program, arg_file_names[0][index - 5: index]]
        log_opt = '{0}:{1}'.format(*lo_arg)
    else:
        index = arg_file_names[0].find('.')
        lo_arg = [program, arg_file_names[0][index - 5: index]]
        log_opt = '{0}:{1}+[...]'.format(*lo_arg)

    # construct fits file name (full path + first file in arguments)
    if len(arg_file_names) > 0:
        fits_fn = os.path.join(p['DRS_DATA_RAW'], arg_night_name,
                               arg_file_names[0])
    else:
        fits_fn = None

    # add to parameter dictionary
    p['log_opt'] = log_opt
    p['program'] = program
    p['arg_night_name'] = arg_night_name
    p['str_file_names'] = ', '.join(arg_file_names)
    p['arg_file_names'] = arg_file_names
    p['fitsfilename'] = fits_fn

    return p


def load_other_config_file(p, key, logthis=True, required=False):
    # Check that key  exists in config file
    tmp = configsetup.check_config(p, key)
    if tmp is not None and required:
        WLOG('error', ' ', tmp)
        sys.exit(1)
    elif tmp is not None:
        return p
    # construct icdp file name
    filename = os.path.join(p['DRS_CONFIG'], p[key])
    # try to open file
    if os.path.exists(filename):
        # read config file into new dictionary
        newparams = configsetup.read_config_file(filename)
        # merge with param file
        for newkey in list(newparams.keys()):
            p[newkey] = newparams[newkey]
        # log output
        if logthis:
            WLOG('', p['log_opt'], '{0} loaded from: {1}'.format(key, filename))
    else:
        if required:
            # log error
            WLOG('error', p['log_opt'],
                 'Config file: {0} not found'.format(filename))
            sys.exit(1)
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
        WLOG('info', log_opt, ('Now processing Image TYPE {0} with {1} '
                               'recipe').format(kind, program))
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
                return p
        else:
            return p
    # Else if we don't have the correct prefix then log and exit
    else:
        WLOG('error', log_opt, ('Wrong type of image for {0}, should be {1}'
                                '').format(kind, ' or '.join(prefixes)))
        sys.exit(1)


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
    WLOG('', p['log_opt'], ('Now running : {program} on file(s): '
                            '{str_file_names}').format(**p))
    tmp = os.path.join(p['DRS_DATA_RAW'], p['arg_night_name'])
    WLOG('', p['log_opt'], 'On directory {0}'.format(tmp))


def display_help_file(p):

    if p['arg_night_name'] != "HELP":
        return 0
    else:
        # Log help file
        WLOG('', p['log_opt'], 'HELP mode for  ' + p['program'])
        # Get man file
        man_file = os.path.join(p['DRS_MAN'].replace(p['program'], '.info'))
        # try to open man file
        if os.path.exists(man_file):
            f = open(man_file, 'r')
            print('\n')
            lines = f.readlines()
            for line in lines:
                print(line)
        # else print that we have no man file
        else:
            WLOG('info', p['log_opt'], 'INFO file is not found for this recipe')
        # exit after help printed
        sys.exit(1)


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
