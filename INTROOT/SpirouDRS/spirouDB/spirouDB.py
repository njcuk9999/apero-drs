#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2018-07-13 02:51
@author: ncook
Version 0.0.1
"""
from __future__ import division
import numpy as np
from astropy.io import fits
from astropy.time import Time
import os
import time
from collections import OrderedDict

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS.spirouCore import spirouMath


# =============================================================================
# Define variables
# =============================================================================
# Define the name of this module
__NAME__ = 'spirouDB.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get the parameter dictionary class
ParamDict = spirouConfig.ParamDict
# Get Logging function
WLOG = spirouCore.wlog
# get Config Error
ConfigError = spirouConfig.ConfigError
# Get plotting functions
sPlt = spirouCore.sPlt


# =============================================================================
# Define functions
# =============================================================================
def get_database(p, update=False, dbkind=None):
    """
    Gets all entries from telluDB where unix time <= max_time. If update is
    False then will first search for and use 'telluDB' in p (if it exists)

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                telluDB: dictionary, the telluric database dictionary
                log_opt: string, log option, normally the program name
    :param update: bool, if False looks for "telluDB' in p, and if found does
                   not load new database
    :param dbkind: string or None: if None set to "Database" else is the name
                   of the type of database (i.e. Telluric or Calibration)

    :return t_database: dictionary, the telluDB database in form:
                    c_database[key] = pos + line.split()

                    where line is the string entry from the database
                    therefore each entry is the values (separated by spaces)

            i.e. if line was: "KEY1 FILENAME DATE1 DATE2 INFO1"
            entry would be:

            t_database['KEY1'] = [1, "FILENAME", "DATE1", "DATE2",
                                  "INFO1"]
    """
    func_name = __NAME__ + '.get_database()'
    # deal with no db kind
    if dbkind is None:
        dbkind = 'Database'
    else:
        dbkind += ' Database'
    # if we already have telluric database don't load it
    if 'telluDB' in p and not update:
        return p['TELLUDB'], p
    # get and check the lock file
    lock, lock_file = get_check_lock_file(p, dbkind)
    # try to open the master file
    lines = read_master_file(p, lock, lock_file, dbkind)
    # store into dictionary of keys
    t_database = OrderedDict()
    # loop around lines in file
    for l_it, line in enumerate(lines):
        # ignore blank lines or lines starting with '#'
        if len(line) == 0:
            continue
        if line == '\n':
            continue
        if line.strip()[0] == '#':
            continue
        # get elements from database
        try:
            # need to get key. Must be first entry in line (separated by spaces)
            key = line.split()[0]
            # check if key already in database
            if key in t_database:
                # noinspection PyTypeChecker
                t_database[key].append([l_it] + line.split()[1:])
            else:
                # noinspection PyTypeChecker
                t_database[key] = [[l_it] + line.split()[1:]]
        # will crash if we don't have 5 variables --> thus log and exit
        except ValueError:
            # Must close and remove lock file before exiting
            close_lock_file(p, lock, lock_file)
            emsg1 = 'Incorrectly formatted line in {0} - function = {1}'
            eargs = [dbkind, func_name]
            lineedit = line.replace('\n', '')
            emsg2 = '   Line {0}: "{1}"'.format(l_it + 1, lineedit)
            WLOG(p, 'error', [emsg1.format(*eargs), emsg2])

    # Need to check if lists are empty after loop
    # Must close and remove lock file before exiting
    if len(t_database) == 0:
        close_lock_file(p, lock, lock_file)
        # log and exit

        # deal with dbkind
        if 'Telluric' in dbkind:
            masterfile = spirouConfig.Constants.TELLUDB_MASTERFILE(p)
        elif 'Calibration' in dbkind:
            masterfile = spirouConfig.Constants.CALIBDB_MASTERFILE(p)
        emsg1 = 'There are no entries in {0}'.format(dbkind)
        emsg2 = '   Please check {0} file at {1}'.format(dbkind, masterfile)
        emsg3 = '   function = {0}'.format(func_name)
        WLOG(p, 'error', [emsg1, emsg2, emsg3])

    # Must close and remove lock file before continuing
    close_lock_file(p, lock, lock_file)
    # return telluDB dictionary
    return t_database


def get_acqtime(p, header, kind='human'):
    # get time from header
    htime, utime = get_times_from_header(p, header=header)
    # deal with kind
    if kind == 'human':
        # htime here should have a space instead of "_"
        return htime.replace('_', ' ')
    elif kind == 'unix':
        return utime
    elif kind == 'julian' or kind == 'mjd':
        t_time = Time(float(utime), format='unix')
        return t_time.mjd
    else:
        t_time = Time(float(utime), format='unix')
        return t_time


# TODO: Write this function based on "get acquisition time
def get_times_from_header(p, header=None, filename=None):
    func_name = __NAME__ + '.get_times_from_header()'

    # if we don't have header get it (using 'fitsfilename')
    if header is None:
        # deal with no filename
        if filename is None:
            if os.path.exists(p['ARG_FILE_NAMES'][0]):
                headerfile = p['ARG_FILE_NAMES'][0]
            else:
                headerfile = os.path.join(p['ARG_FILE_DIR'],
                                          p['ARG_FILE_NAMES'][0])

            if not os.path.exists(headerfile):
                emsg1 = '"header" and "filename" not defined in {0}'
                emsg2 = '   AND "arg_file_names" not defined in ParamDict'
                eargs = func_name
                WLOG(p, 'error', [emsg1.format(eargs), emsg2])
        # else we have a filename defined
        else:
            headerfile = filename
            # if rawfile does not exist make error
            if not os.path.exists(headerfile):
                emsg = ('"header" not defined in {0} and "filename" '
                        'path not found.')
                WLOG(p, 'error', emsg.format(func_name))
        # get file
        header = fits.getheader(headerfile, ext=0)
    else:
        # else we have header just try to identify it from custom keys
        if '@@@fname' in header:
            headerfile = header['@@@fname']
        else:
            headerfile = 'UNKNOWN'

    # make sure keywords are in header
    if 'KW_ACQTIME' not in p:
        emsgs = ['Key "{0}" not defined in ParamDict (or SpirouKeywords.py)'
                 ''.format('KW_ACQTIME')]
        emsgs.append('\tfunction = {0}'.format(func_name))
        WLOG(p, 'error', emsgs)
    if 'KW_ACQTIME_FMT' not in p:
        emsgs = ['Key "{0}" not defined in ParamDict (or SpirouKeywords.py)'
                ''.format('KW_ACQTIME')]
        emsgs.append('\tfunction = {0}'.format(func_name))
        WLOG(p, 'error', emsgs)

    # try getting unix time
    if p['KW_ACQTIME'][0] in header:
        # get header keys
        raw_time = header[p['KW_ACQTIME'][0]]
        raw_fmt = p['KW_ACQTIME_FMT'][0]
        raw_type = p['KW_ACQTIME_DTYPE'][1]
        # get astropy time
        a_time = Time(raw_type(raw_time), format=raw_fmt)
        # get human time and unix time
        human_time = a_time.iso
        unix_time = float(a_time.unix)
    # else raise error
    else:
        eargs = [p['KW_ACQTIME'][0], headerfile, func_name]
        emsg = 'Key {0} not in HEADER file of {1} for function {2}'
        WLOG(p, 'error', emsg.format(*eargs))
        human_time, unix_time = None, None

    # lastly we need to remove spaces in the human time
    human_time = human_time.replace(' ', '_')
    # return human time and unix time
    return human_time, unix_time


def update_datebase(p, keys, lines, dbkind=None):
    """
    Updates (or creates) the telluDB with an entry or entries in the form:

        {key} lines[0]
        {key} lines[1]
        {key} lines[2]

    where lines[0] is a string with variables separated by a space

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                log_opt: string, log option, normally the program name
    :param keys: list of strings, keys to add to the telluDB
    :param lines: list of strings, lines to add to the telluDB
    :param dbkind: string or None: if None set to "Database" else is the name
                   of the type of database (i.e. Telluric or Calibration)

    :return None:
    """
    funcname = __NAME__ + '.update_database()'
    # deal with no db kind
    if dbkind is None:
        dbkind = 'Database'
    else:
        dbkind += ' Database'
    # check that the length of keys matches length of lines
    if len(keys) != len(lines):
        emsg1 = '{0}: Length of keys ({1}) does not match length of lines ({2})'
        emsg2 = '\tfunction = {0}'.format(funcname)
        eargs = [dbkind, len(keys), len(lines)]
        WLOG(p, 'error', [emsg1.format(*eargs), emsg2])
    # get and check the lock file (Any errors must close and remove lock file
    #     after this point)
    lock, lock_file = get_check_lock_file(p, dbkind)
    # get the unique keys
    ukeys = np.unique(keys)
    # write lines to master
    write_files_to_master(p, lines, ukeys, lock, lock_file, dbkind)
    # finally close the lock file and remove it for next access
    close_lock_file(p, lock, lock_file)


# =============================================================================
# Worker functions
# =============================================================================
def get_check_lock_file(p, dbkind):
    """
    Creates a lock_file if it doesn't exist, if it does waits for it to not
    exist - acts to stop telluDB being open multiple times at once

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                log_opt: string, log option, normally the program name
                DB_MAX_WAIT: float, the maximum wait time (in seconds)
                                for  database file to be in
                                use (locked) after which an error is raised
    :param dbkind: string or None: if None set to "Database" else is the name
                   of the type of database (i.e. Telluric or Calibration)


    :return lock: file, the opened lock_file (using open(lockfile, 'w'))
    :return lockfile: string, the opened lock file name
    """
    # create lock file (to make sure database is only open once at a time)
    # construct lock file name
    max_wait_time = p['DB_MAX_WAIT']
    # deal with dbkind
    if 'Telluric' in dbkind:
        name = 'TelluDB'
        lock_file = spirouConfig.Constants.TELLUDB_LOCKFILE(p)
    elif 'Calibration' in dbkind:
        name = 'CalibDB'
        lock_file = spirouConfig.Constants.CALIBDB_LOCKFILE(p)
    else:
        emsgs = ['Dev Error: "dbkind" not understood',
                 '\tdbkind = "{0}"'.format(dbkind)]
        WLOG(p, 'error', emsgs)
        lock_file = None
        name = None

    # check if lock file already exists
    if os.path.exists(lock_file):
        WLOG(p, 'warning', '{0} locked. Waiting...'.format(name))
        WLOG(p, 'warning', '\tFilename = {0}'.format(lock_file))
    # wait until lock_file does not exist or we have exceeded max wait time
    wait_time = 0
    while os.path.exists(lock_file) and wait_time < max_wait_time:
        time.sleep(1)
        wait_time += 1
    if wait_time > max_wait_time:
        emsg1 = ('{0} can not be accessed (file locked and max wait time '
                 'exceeded.'.format(name))
        emsg2 = ('\tPlease make sure {0} is not being used and '
                 'manually delete {1}').format(name, lock_file)
        WLOG(p, 'error', [emsg1, emsg2])
    # try to open the lock file
    # wait until lock_file does not exist or we have exceeded max wait time
    lock = open_lock_file(p, lock_file)
    # return lock file and name
    return lock, lock_file


def open_lock_file(p, lock_file):
    # try to open the lock file
    if not os.path.exists(os.path.dirname(lock_file)):
        emsg = 'Lock directory does not exist. Dir={0}'
        WLOG(p, 'error', emsg.format(os.path.dirname(lock_file)))

    # wait until lock_file does not exist or we have exceeded max wait time
    wait_time = 0
    open_file = True
    lock = None
    while open_file and wait_time < p['DB_MAX_WAIT']:
        try:
            lock = open(lock_file, 'w')
            open_file = False
        except Exception as e:
            if wait_time == 0:
                wmsg = 'Waiting to open lock: {0}'
                WLOG(p, 'warning', wmsg.format(lock_file))
            time.sleep(1)
            wait_time += 1
    if wait_time > p['DB_MAX_WAIT']:
        emsg1 = ('DB can not be accessed (Cannot open lock file and max '
                 'wait time exceeded.')
        emsg2 = ('\tPlease make sure DB is not being used and '
                 'manually delete {0}').format(lock_file)
        WLOG(p, 'error', [emsg1, emsg2])
    return lock


def close_lock_file(p, lock, lock_file):
    # try to open the lock file
    # wait until lock_file does not exist or we have exceeded max wait time
    wait_time = 0
    close_file = True
    while close_file and wait_time < p['DB_MAX_WAIT']:
        try:
            lock.close()
            if os.path.exists(lock_file):
                os.remove(lock_file)
            close_file = False
        except Exception as e:
            if wait_time == 0:
                WLOG(p, 'warning', 'Waiting to close lock')
            time.sleep(1)
            wait_time += 1
    if wait_time > p['DB_MAX_WAIT']:
        emsg1 = ('DB can not be closed (Cannot close lock file and max '
                 'wait time exceeded.')
        emsg2 = ('Please make sure DB is not being used and '
                 'manually delete {0}').format(lock_file)
        WLOG(p, 'error', [emsg1, emsg2])


def write_files_to_master(p, lines, keys, lock, lock_file, dbkind):
    """
    writes database entries to master file

    master file is defined as 'DRS_TELLU_DB'/'IC_TELLUDB_FILENAME' and
    variables are taken from p

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                log_opt: string, log option, normally the program name
    :param lines: list of strings, entries to add to the master file
    :param keys: list of strings, the keys that are to be added to master file
    :param lock: file, the lock file (for closing if error occurs)
    :param lock_file: string, the lock file name (for deleting once an error
                      occurs)
    :param dbkind: string or None: if None set to "Database" else is the name
                   of the type of database (i.e. Telluric or Calibration)


    :return:
    """
    func_name = __NAME__ + '.write_files_to_master()'
    # construct master filename
    if 'Telluric' in dbkind:
        masterfile = spirouConfig.Constants.TELLUDB_MASTERFILE(p)
    elif 'Calibration'in dbkind:
        masterfile = spirouConfig.Constants.CALIBDB_MASTERFILE(p)
    else:
        emsg1 = 'Invalid Database kind ({0})'.format(dbkind)
        emsg2 = '\tfunction = {0}'.format(func_name)
        WLOG(p, 'error', [emsg1, emsg2])
        masterfile = None
    # try to
    try:
        f = open(masterfile, 'a')
    except IOError:
        # Must close and delete lock file
        close_lock_file(p, lock, lock_file)
        # log and exit
        emsg1 = 'I/O Error on file: {0}'.format(masterfile)
        emsg2 = '   function = {0}'.format(func_name)
        WLOG(p, 'error', [emsg1, emsg2])
    else:
        # write database line entry to file
        f.writelines(lines)
        f.close()
        wmsg = 'Updating {0} with {1}'
        WLOG(p, 'info', wmsg.format(dbkind, ', '.join(keys)))
        try:
            os.chmod(masterfile, 0o666)
        except OSError:
            pass


def read_master_file(p, lock, lock_file, dbkind):
    """
    Read the telluric database master file

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                log_opt: string, log option, normally the program name
    :param lock: file, the lock file
    :param lock_file: string, the lock file location and filename
    :param dbkind: string or None: if None set to "Database" else is the name
                   of the type of database (i.e. Telluric or Calibration)


    :return lines: list of strings, the lines in telluric database
                   master file (defined at:
                      spirouConfig.Constants.TELLUDB_MASTERFILE)
    """
    func_name = __NAME__ + '.read_master_file()'
    # construct master filename
    if 'Telluric'in dbkind:
        masterfile = spirouConfig.Constants.TELLUDB_MASTERFILE(p)
    elif 'Calibration' in dbkind:
        masterfile = spirouConfig.Constants.CALIBDB_MASTERFILE(p)
    else:
        emsgs = ['Dev Error: Wrong "dbkind" in call to function {0}'
                 ''.format(func_name)]
        emsgs.append('\t"dbkind"="{0}" (Must be "Telluric" or "Calibration")'
                     ''.format(dbkind))
        WLOG(p, 'error', emsgs)
        masterfile = None
    # try to
    try:
        f = open(masterfile, 'r')
    except IOError:
        # Must close and delete lock file
        close_lock_file(p, lock, lock_file)
        # log and exit
        eargs = [dbkind, masterfile]
        emsg1 = '{0} master file: {1} can not be found!'.format(*eargs)
        emsg2 = '   function = {0}'.format(func_name)
        WLOG(p, 'error', [emsg1, emsg2])
    else:
        # write database line entry to file
        lines = list(f.readlines())
        f.close()
        return lines


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # Main code here
    pass

# =============================================================================
# End of code
# =============================================================================
