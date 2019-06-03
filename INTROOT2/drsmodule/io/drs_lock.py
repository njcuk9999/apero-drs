#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-21 at 09:37

@author: cook
"""
from __future__ import division
import os
import time

from drsmodule import constants
from drsmodule.config import drs_log
from drsmodule.locale import drs_text


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'drs_startup.py'
__INSTRUMENT__ = None
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
ErrorEntry = drs_text.ErrorEntry
ErrorText = drs_text.ErrorText
HelpText = drs_text.HelpText


# =============================================================================
# Define functions
# =============================================================================
def check_fits_lock_file(p, filename):
    # create lock file (to make sure database is only open once at a time)
    # construct lock file name
    max_wait_time = p['DB_MAX_WAIT']
    # get lock file name
    if '.fits' in filename:
        lock_file = filename.replace('.fits', '.lock')
    else:
        lock_file = filename + '.lock'
    # check if lock file already exists
    if os.path.exists(lock_file):
        WLOG(p, 'warning', ErrorEntry('10-001-00002', args=[filename]))
    # wait until lock_file does not exist or we have exceeded max wait time
    wait_time = 0
    while os.path.exists(lock_file) and wait_time < max_wait_time:
        time.sleep(1)
        wait_time += 1
    if wait_time > max_wait_time:
        eargs = [filename, lock_file]
        WLOG(p, 'error', ErrorEntry('01-001-00002', args=eargs))
    # try to open the lock file
    # wait until lock_file does not exist or we have exceeded max wait time
    lock = open_fits_lock_file(p, lock_file, filename)
    # return lock file and name
    return lock, lock_file


def open_fits_lock_file(p, lock_file, filename):
    # try to open the lock file
    # wait until lock_file does not exist or we have exceeded max wait time
    wait_time = 0
    open_file = True
    lock = None
    while open_file and wait_time < p['FITSOPEN_MAX_WAIT']:
        try:
            lock = open(lock_file, 'w')
            open_file = False
        except Exception as e:
            if wait_time == 0:
                WLOG(p, 'warning', ErrorEntry('10-001-00003'))
            time.sleep(1)
            wait_time += 1
    if wait_time > p['FITSOPEN_MAX_WAIT']:
        eargs = [filename, lock_file]
        WLOG(p, 'error', ErrorEntry('01-001-00002', args=eargs))
    return lock


def close_fits_lock_file(p, lock, lock_file, filename):
    # try to open the lock file
    # wait until lock_file does not exist or we have exceeded max wait time
    wait_time = 0
    close_file = True
    while close_file and wait_time < p['FITSOPEN_MAX_WAIT']:
        try:
            lock.close()
            if os.path.exists(lock_file):
                os.remove(lock_file)
            close_file = False
        except Exception as e:
            if wait_time == 0:
                WLOG(p, 'warning', ErrorEntry('10-001-00004'))
            time.sleep(1)
            wait_time += 1
    if wait_time > p['FITSOPEN_MAX_WAIT']:
        eargs = [filename, lock_file]
        WLOG(p, 'error', ErrorEntry('01-001-00002', args=eargs))




# =============================================================================
# End of code
# =============================================================================
