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
import numpy as np
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
    def __init__(self, params, lockname, lockpath):
        """
        Construct the lock instance

        :param params:
        :param lockname:
        :param lockpath:
        """
        # replace all . and whitespace with _
        self.lockname = self.__clean_name(lockname)

        self.params = params
        self.maxwait = params.get('DB_MAX_WAIT', 100)
        self.path = os.path.join(lockpath, self.lockname)
        self.queue = []
        # make the lock directory
        self.__makelockdir()

    def __makelockdir(self):
        """
        Internal use only: make the lock directory

        :return:
        """
        # set up a timer
        timer = 0
        # keep trying to create the folder
        while timer < self.maxwait:
            # if path does not exist try to create it
            if not os.path.exists(self.path):
                try:
                    os.mkdir(self.path)
                    WLOG(params, '', 'Lock: Activated {0}'.format(self.path))
                    break
                except:
                    # whatever the problem sleep for a second
                    time.sleep(0.1)
                    # add to the timer
                    timer += 1
                    # update user every 10 seconds file is locked
                    if timer % 100 == 0:
                        wargs = [self.lockname]
                        wmsg = 'Lock: Make lock dir waiting {0}'
                        WLOG(params, 'warning', wmsg.format(*wargs))
            # if path does exist just skip
            else:
                break

    def __makelockfile(self, name):
        """
        Internal use only: make the lock file "name.lock"

        :param name:
        :return:
        """
        # clean name
        name = self.__clean_name(name)
        # get absolute path
        abspath = os.path.join(self.path, name + '.lock')
        # set up a timer
        timer = 0
        # keep trying to create the folder
        while timer < self.maxwait:
            # if path does not exist try to create it
            if not os.path.exists(abspath):
                try:

                    f = open(abspath, 'w')
                    f.write(name)
                    f.close()
                    break
                except:
                    # whatever the problem sleep for a second
                    time.sleep(0.1)
                    # add to the timer
                    timer += 1
                    # update user every 10 seconds file is locked
                    if timer % 100 == 0:
                        wargs = [self.lockname, name]
                        wmsg = 'Lock: Make lock file waiting {0} {1}'
                        WLOG(params, 'warning', wmsg.format(*wargs))
            # if path does exist just skip
            else:
                break

    def __getfirst(self):
        """
        Internal use only: get the first (based on creation time) file in
        self.path

        :return:
        """
        path = self.path
        # get the raw list
        rawlist = os.listdir(path)
        # get times
        pos, mintime = np.nan, np.inf
        for it in range(len(rawlist)):
            # get the absolute path
            abspath = os.path.join(path, rawlist[it])
            # get the creation time for the file
            filetime = os.path.getctime(abspath)
            # check if it is older than mintime
            if filetime < mintime:
                mintime = filetime
                pos = it
        # return list
        return rawlist[pos]

    def __remove_file(self, name):
        """
        Internal use only: Remove file "name.lock"

        :param name:
        :return:
        """
        # clean name
        name = self.__clean_name(name)
        # get the absolute path
        abspath = os.path.join(self.path, name + '.lock')
        # if the file exists remove it
        if os.path.exists(abspath):
            os.remove(abspath)

    def __clean_name(self, name):
        BAD_CHARS = ['/', '\\' , '.', ',']
        # loop around bad characters and replace them
        for char in BAD_CHARS:
            name = name.replace(char, '_')
        return name

    def enqueue(self, name):
        """
        Used to add "name" to the queue

        :param name:
        :return:
        """
        # clean name
        name = self.__clean_name(name)
        # log progress
        WLOG(self.params, '', 'Lock: File added to queue: {0}'.format(name))
        # add unique name to queue
        self.__makelockfile(name)
        # put in just to see if we are appending too quickly
        time.sleep(0.1)

    def myturn(self, name):
        """
        Used to check whether it is time to run function for "name" (based on
        position in queue)

        :param name:
        :return:
        """
        # clean name
        name = self.__clean_name(name)
        # if the unique name is first in the list then we can unlock this file
        if name + '.lock' == self.__getfirst():
            WLOG(self.params, '', 'Lock: File unlocked: {0}'.format(name))
            return True
        # else we return False (and ask whether it is my turn later)
        else:
            return False

    def dequeue(self, name):
        """
        Used to remove "name" from queue

        :param name:
        :return:
        """
        WLOG(self.params, '', 'Lock: File removed from queue: {0}'.format(name))
        # once we are finished with a lock we remove it from the queue
        self.__remove_file(name)

    def reset(self):
        """
        Used to remove all entries from a queue (and start again)

        :return:
        """
        WLOG(params, '', 'Lock: Deactivated {0}'.format(self.path))
        # get the raw list
        rawlist = os.listdir(self.path)
        # loop around files
        for it in range(len(rawlist)):
            # get the absolute path
            abspath = os.path.join(self.path, rawlist[it])
            # remove files
            if os.path.exists(abspath):
                os.remove(abspath)
        # now remove directory
        if os.path.exists(self.path):
            os.removedirs(self.path)


def synchronized(lock, name):
    """
    Synchroisation decorator - wraps the function to lock
    calls to function are added to a queue based on the lock given and
    the name for this call to the function (must be unique)

    :param lock:
    :param func_name:
    :return:
    """
    def wrap(f):
        def newFunction(*args, **kw):
            # add to the queue
            lock.enqueue(name)
            # timer
            timer = 0
            # while the lock is active do not run function
            while not lock.myturn(name):
                # sleep
                time.sleep(1)
                # update user every 10 seconds file is locked
                if timer % 10 == 0:
                    wargs = [lock.path, name]
                    wmsg = 'Lock: Waiting {0} {1}'
                    WLOG(lock.params, 'warning', wmsg.format(*wargs))
                # increase timer
                timer += 1
            # now try to run the function
            try:
                return f(*args, **kw)
            # finally deactivate the lock
            finally:
                # unlock file
                lock.dequeue(name)
        # return the new function (wrapped)
        return newFunction
    # return the wrapped function
    return wrap


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":

    # testing the locking mechanism
    from multiprocessing import Process
    import string

    params = constants.load()

    def printfunc(i, j):
        # set up the lock file (usually a file or function)
        mylock = Lock(params, 'printfunc', './')

        # this is where we define the locked function
        @synchronized(mylock, '{0}-{1}'.format(i, j))
        def lockprint():
            for k in list(string.ascii_lowercase):
                print('{0}-{1}-{2}'.format(i, j, k))
            time.sleep(0.1)

        # this is where we run the function
        try:
            lockprint()
        except KeyboardInterrupt:
            mylock.reset()

    for jt in range(2):
        jobs = []
        # loop around sub groups (to be run at same time)
        for it in range(10):
            # get parallel process
            process = Process(target=printfunc, args=[it, jt])
            process.start()
            jobs.append(process)
        # do not continue until finished
        for proc in jobs:
            proc.join()


# =============================================================================
# End of code
# =============================================================================
