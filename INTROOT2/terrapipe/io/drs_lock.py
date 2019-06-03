#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-21 at 09:37

import rules:
    Cannot import drs_table
    Cannot import whole of terrapipe.config (drs_setup uses drs_table)

@author: cook
"""
from __future__ import division
import os
import time

from terrapipe import constants
from terrapipe.locale import drs_text
from terrapipe.config import drs_log


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'drs_lock.py'
__INSTRUMENT__ = None
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# get the parameter dictionary
ParamDict = constants.ParamDict
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
TextEntry = drs_text.TextEntry
TextDict = drs_text.TextDict
HelpText = drs_text.HelpDict


# =============================================================================
# Define functions
# =============================================================================
def check_lock_file(p, filename):
    """
    Check whether lock file exists - wait if it does - else create a lock
    file and return the lock file and lock filename

    :param p: ParamDict, the constants parameter dictionary
    :param filename: string, the filename to lock the file for (this will
                     be used to create the lock file)

    :type p: ParamDict
    :type filename: str

    :exception SystemExit: on caught errors

    :returns: tuple containing the lock file and lock filename
    :rtype: tuple[_io.TextIOWrapper, str]
    """
    # create lock file (to make sure database is only open once at a time)
    # construct lock file name
    max_wait_time = p['DB_MAX_WAIT']
    # get lock file name
    lock_file = filename + '.lock'
    # check if lock file already exists
    if os.path.exists(lock_file):
        WLOG(p, 'warning', TextEntry('10-001-00002', args=[filename]))
    # wait until lock_file does not exist or we have exceeded max wait time
    wait_time = 0
    while os.path.exists(lock_file) and wait_time < max_wait_time:
        time.sleep(1)
        wait_time += 1
    if wait_time > max_wait_time:
        eargs = [filename, lock_file]
        WLOG(p, 'error', TextEntry('01-001-00002', args=eargs))
    # try to open the lock file
    # wait until lock_file does not exist or we have exceeded max wait time
    lock = open_lock_file(p, lock_file, filename)
    # return lock file and name
    return lock, lock_file


def open_lock_file(p, lock_file, filename):
    """
    Opens the lock file (or waits if file is already being opened)

    :param p: ParamDict, the constants parameter dictionary
    :param lock_file: str, the lock file name
    :param filename: string, the filename to lock the file for (this will
                     be used to create the lock file)

    :type p: ParamDict
    :type lock_file: str
    :type filename: str

    :exception SystemExit: on caught errors

    :returns: the lock_file
    :rtype: _io.TextIOWrapper
    """
    # try to open the lock file
    # wait until lock_file does not exist or we have exceeded max wait time
    wait_time = 0
    open_file = True
    lock = None
    while open_file and wait_time < p['LOCKOPEN_MAX_WAIT']:
        # noinspection PyBroadException
        try:
            lock = open(lock_file, 'w')
            open_file = False
        except Exception as e:
            if wait_time == 0:
                WLOG(p, 'warning', TextEntry('10-001-00003', args=[lock_file]))
            time.sleep(1)
            wait_time += 1
    if wait_time > p['LOCKOPEN_MAX_WAIT']:
        eargs = [filename, lock_file]
        WLOG(p, 'error', TextEntry('01-001-00002', args=eargs))
    return lock


def close_lock_file(p, lock, lock_file, filename):
    """
    Opens the lock file (or waits if file is already being opened)

    :param p: ParamDict, the constants parameter dictionary
    :param lock: file, the object file
    :param lock_file: str, the lock file name
    :param filename: string, the filename to lock the file for (this will
                     be used to create the lock file)

    :type p: ParamDict
    :type lock: _io.TextIOWrapper
    :type lock_file: str
    :type filename: str

    :exception SystemExit: on caught errors

    :returns: None
    """
    # try to open the lock file
    # wait until lock_file does not exist or we have exceeded max wait time
    wait_time = 0
    close_file = True
    while close_file and wait_time < p['LOCKOPEN_MAX_WAIT']:
        # noinspection PyBroadException
        try:
            lock.close()
            if os.path.exists(lock_file):
                os.remove(lock_file)
            close_file = False
        except Exception as e:
            if wait_time == 0:
                WLOG(p, 'warning', TextEntry('10-001-00004', args=[lock_file]))
            time.sleep(1)
            wait_time += 1
    if wait_time > p['LOCKOPEN_MAX_WAIT']:
        eargs = [filename, lock_file]
        WLOG(p, 'error', TextEntry('01-001-00002', args=eargs))


# =============================================================================
# End of code
# =============================================================================
