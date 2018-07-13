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
import filecmp
from astropy.io import fits
import os
import shutil
import time

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
    lock, lock_file = get_check_lock_file(p)
    # try to open the master file
    lines = read_master_file(p, lock, lock_file, dbkind)

    # store into dictionary of keys
    t_database = dict()
    # loop around lines in file
    for l_it, line in lines:
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
                t_database[key].append([l_it] + line.split()[1:])
            else:
                t_database[key] = [[l_it] + line.split()[1:]]
        # will crash if we don't have 5 variables --> thus log and exit
        except ValueError:
            # Must close and remove lock file before exiting
            lock.close()
            os.remove(lock_file)
            emsg1 = 'Incorrectly formatted line in {0} - function = {1}'
            eargs = [dbkind, func_name]
            lineedit = line.replace('\n', '')
            emsg2 = '   Line {0}: "{1}"'.format(l_it + 1, lineedit)
            WLOG('error', p['LOG_OPT'], [emsg1.format(*eargs), emsg2])
            key, dirname, filename, t_fmt, t = None, None, None, None, None

    # Need to check if lists are empty after loop
    # Must close and remove lock file before exiting
    if len(t_database) == 0:
        lock.close()
        os.remove(lock_file)
        # log and exit
        telludb_file = spirouConfig.Constants.TELLUDB_MASTERFILE(p)
        emsg1 = 'There are no entries in {0}'.format(dbkind)
        emsg2 = '   Please check {0} file at {1}'.format(dbkind, telludb_file)
        emsg3 = '   function = {0}'.format(func_name)
        WLOG('error', p['LOG_OPT'], [emsg1, emsg2, emsg3])

    # Must close and remove lock file before continuing
    lock.close()
    os.remove(lock_file)
    # return telluDB dictionary
    return t_database



def get_times_from_header(p, hdr=None):

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
        WLOG('error', p['LOG_OPT'], [emsg1.format(*eargs), emsg2])
    # get and check the lock file (Any errors must close and remove lock file
    #     after this point)
    lock, lock_file = get_check_lock_file(p, dbkind)
    # get the unique keys
    ukeys = np.unique(keys)
    # write lines to master
    write_files_to_master(p, lines, ukeys, lock, lock_file, dbkind)
    # finally close the lock file and remove it for next access
    lock.close()
    os.remove(lock_file)


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
                TELLU_MAX_WAIT: float, the maximum wait time (in seconds)
                                for telluric database file to be in
                                use (locked) after which an error is raised

    :return lock: file, the opened lock_file (using open(lockfile, 'w'))
    :return lockfile: string, the opened lock file name
    """
    # create lock file (to make sure database is only open once at a time)
    # construct lock file name
    lock_file = spirouConfig.Constants.TELLUDB_LOCKFILE(p)
    # check if lock file already exists
    if os.path.exists(lock_file):
        wmsg = '{0} locked. Waiting...'.format(dbkind)
        WLOG('warning', p['LOG_OPT'], wmsg)
    # wait until lock_file does not exist or we have exceeded max wait time
    wait_time = 0
    while os.path.exists(lock_file) or wait_time > p['TELLU_MAX_WAIT']:
        time.sleep(1)
        wait_time += 1
    if wait_time > p['TELLU_MAX_WAIT']:
        emsg1 = ('TelluDB can not be accessed (file locked and max wait time '
                 'exceeded.')
        emsg2 = ('Please make sure TelluDB is not being used and '
                 'manually delete {0}').format(lock_file)
        WLOG('error', p['LOG_OPT'], [emsg1, emsg2])
    # open the lock file
    lock = open(lock_file, 'w')
    # return lock file and name
    return lock, lock_file


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
    :return:
    """
    func_name = __NAME__ + '.write_files_to_master()'
    # construct master filename
    masterfile = spirouConfig.Constants.TELLUDB_MASTERFILE(p)
    # try to
    try:
        f = open(masterfile, 'a')
    except IOError:
        # Must close and delete lock file
        lock.close()
        os.remove(lock_file)
        # log and exit
        emsg1 = 'I/O Error on file: {0}'.format(masterfile)
        emsg2 = '   function = {0}'.format(func_name)
        WLOG('error', p['LOG_OPT'], [emsg1, emsg2])
    else:
        # write database line entry to file
        f.writelines(lines)
        f.close()
        wmsg = 'Updating {0} with {1}'
        WLOG('info', p['LOG_OPT'], wmsg.format(dbkind, ', '.join(keys)))
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

    :return lines: list of strings, the lines in telluric database
                   master file (defined at:
                      spirouConfig.Constants.TELLUDB_MASTERFILE)
    """
    func_name = __NAME__ + '.read_master_file()'

    # construct master filename
    masterfile = spirouConfig.Constants.TELLUDB_MASTERFILE(p)
    # try to
    try:
        f = open(masterfile, 'r')
    except IOError:
        # Must close and delete lock file
        lock.close()
        os.remove(lock_file)
        # log and exit
        eargs = [dbkind, masterfile]
        emsg1 = '{0} master file: {1} can not be found!'.format(*eargs)
        emsg2 = '   function = {0}'.format(func_name)
        WLOG('error', p['LOG_OPT'], [emsg1, emsg2])
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