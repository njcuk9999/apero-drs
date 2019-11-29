#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-21 at 09:37

import rules:
    Cannot import drs_table
    Cannot import whole of apero.config (drs_setup uses drs_table)

@author: cook
"""
from __future__ import division
import os
import time
import random
from signal import signal, SIGINT

from apero.core import constants
from apero.locale import drs_text
from apero.core.core import drs_log


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
# define a constant to check while breaks
BREAKWHILE = False

# =============================================================================
# Define functions
# =============================================================================
def break_lock_wait(signal_received, frame):
    global BREAKWHILE
    print('\nSIGINT or CTRL-C detected. Unlocking file\n')
    BREAKWHILE = True


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
    # allow changing of global variable
    global BREAKWHILE
    # set function name
    func_name = __NAME__ + '.check_lock_file()'
    # create lock file (to make sure database is only open once at a time)
    # construct lock file name
    max_wait_time = p['DB_MAX_WAIT']
    # get lock file name
    lock_file = filename + '.lock'
    # check if lock file already exists
    if os.path.exists(lock_file):
        WLOG(p, 'warning', TextEntry('10-001-00002', args=[lock_file]))
    # wait until lock_file does not exist or we have exceeded max wait time
    wait_time = 0
    # deal with while loop breaking
    signal(SIGINT, break_lock_wait)
    BREAKWHILE = False
    # wait for lock file not to exist
    while os.path.exists(lock_file) and wait_time < max_wait_time:
        try:
            time.sleep(1)
            wait_time += 1
            if wait_time % 10 == 0:
                dargs = [lock_file, wait_time, func_name]
                WLOG(p, 'debug', TextEntry('90-008-00008', args=dargs))
        except KeyboardInterrupt:
            BREAKWHILE = True
        # check for while break
        if BREAKWHILE:
            break
    # reset breakwhile
    BREAKWHILE = False
    signal(SIGINT, constants.catch_sigint)
    # display an error message if we went over time
    if wait_time > max_wait_time:
        eargs = [filename, lock_file]
        WLOG(p, 'error', TextEntry('01-001-00002', args=eargs))
    else:
        # TODO: move to db or remove
        WLOG(p, '', 'Unlocking checkfile: {0}'.format(lock_file))
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
    # allow changing of global variable
    global BREAKWHILE
    # set function name
    func_name = __NAME__ + '.open_lock_file()'
    # try to open the lock file
    # wait until lock_file does not exist or we have exceeded max wait time
    wait_time = 0
    open_file = True
    lock = None
    emessages = []
    # deal with while loop breaking
    signal(SIGINT, break_lock_wait)
    BREAKWHILE = False
    # wait for lock file to be opened
    while open_file and wait_time < p['LOCKOPEN_MAX_WAIT']:
        # noinspection PyBroadException
        try:
            lock = open(lock_file, 'w')
            open_file = False
        except KeyboardInterrupt:
            BREAKWHILE = True
        except Exception as e:
            if wait_time == 0:
                WLOG(p, 'warning', TextEntry('10-001-00003', args=[lock_file]))
            time.sleep(1)
            wait_time += 1
            # debug log if not already shown
            if str(e) not in emessages:
                dargs = [lock_file, wait_time, type(e), str(e), func_name]
                WLOG(p, 'debug', TextEntry('90-008-00009', args=dargs))
                # append emessages
                emessages.append(str(e))
        # print debug message every 10 iterations
        if wait_time % 10 == 0:
            dargs = [lock_file, wait_time, func_name]
            WLOG(p, 'debug', TextEntry('90-008-00008', args=dargs))
        # check for while break
        if BREAKWHILE:
            break
    # reset breakwhile
    BREAKWHILE = False
    signal(SIGINT, constants.catch_sigint)
    # display message if we went over max time
    if wait_time > p['LOCKOPEN_MAX_WAIT']:
        eargs = [filename, lock_file]
        WLOG(p, 'error', TextEntry('01-001-00002', args=eargs))
    # TODO: move to db or remove
    WLOG(p, '', 'Unlocking openfile: {0}'.format(lock_file))

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
    # allow changing of global variable
    global BREAKWHILE
    # set function name
    func_name = __NAME__ + '.close_lock_file()'
    # try to open the lock file
    # wait until lock_file does not exist or we have exceeded max wait time
    wait_time = 0
    close_file = True
    emessages= []
    # deal with while loop breaking
    signal(SIGINT, break_lock_wait)
    BREAKWHILE = False
    # wait for lock file to be closed
    while close_file and wait_time < p['LOCKOPEN_MAX_WAIT']:
        # noinspection PyBroadException
        try:
            lock.close()
            if os.path.exists(lock_file):
                os.remove(lock_file)
            close_file = False
        except KeyboardInterrupt:
            BREAKWHILE = True
        except Exception as e:
            if wait_time == 0:
                WLOG(p, 'warning', TextEntry('10-001-00004', args=[lock_file]))
            time.sleep(1)
            wait_time += 1
            # debug log if not already shown
            if str(e) not in emessages:
                dargs = [lock_file, wait_time, type(e), str(e), func_name]
                WLOG(p, 'debug', TextEntry('90-008-00009', args=dargs))
                # append emessages
                emessages.append(str(e))
        # print debug message every 10 iterations
        if wait_time % 10 == 0:
            dargs = [lock_file, wait_time, func_name]
            WLOG(p, 'debug', TextEntry('90-008-00008', args=dargs))
        # check for while break
        if BREAKWHILE:
            break
    # reset breakwhile
    BREAKWHILE = False
    signal(SIGINT, constants.catch_sigint)
    # display message if we went over max time
    if wait_time > p['LOCKOPEN_MAX_WAIT']:
        eargs = [filename, lock_file]
        WLOG(p, 'error', TextEntry('01-001-00002', args=eargs))
    # TODO: move to db or remove
    WLOG(p, '', 'Unlocking closefile: {0}'.format(lock_file))





# =============================================================================
# Define new functions
# =============================================================================
class Lock:
    """
    Class to control locking of decorated functions
    """
    def __init__(self):
        self.active = False
        self.func_name = None

    def activate(self):

        if self.func_name is None:
            print('lock started')
        else:
            print('lock started for {0}'.format(self.func_name))
        self.active = True

    def deactivate(self):
        if self.func_name is None:
            print('lock ended')
        else:
            print('lock ended for {0}'.format(self.func_name))
        self.active = False



def synchronized(lock, func_name=None):
    """
    Synchroisation decorator - wraps the function to lock
    :param lock:
    :param func_name:
    :return:
    """
    """ Synchronization decorator. """
    def wrap(f):
        def newFunction(*args, **kw):
            # set the function name
            if func_name is not None:
                lock.func_name = func_name
            # while the lock is active do not run function
            while lock.active:
                # randomise the wait time (so multiple hits don't wait
                #   the exact same amount of time)
                wait = random.randint(1000, 5000)
                # sleep
                time.sleep(wait / 10000)
            # activate the lock
            lock.activate()
            # now try to run the function
            try:
                return f(*args, **kw)
            # finally deactivate the lock
            finally:
                lock.deactivate()
        # return the new function (wrapped)
        return newFunction
    # return the wrapped function
    return wrap




# =============================================================================
# End of code
# =============================================================================
