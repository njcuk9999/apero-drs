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
import glob
import sys

from apero.core import constants
from apero.locale import drs_text
from apero.core.core import drs_log


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'drs_lock.py'
__INSTRUMENT__ = 'None'
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
class Lock:
    """
    Class to control locking of decorated functions
    """
    def __init__(self, params, lockname):
        """
        Construct the lock instance

        :param params:
        :param lockname:
        :param lockpath:
        """
        # set the bad characters to clean
        self.bad_chars = ['/', '\\' , '.', ',']
        # replace all . and whitespace with _
        self.lockname = self.__clean_name(lockname)
        self.params = params
        # get the lock path
        lockpath = os.path.join(params['DRS_DATA_MSG_FULL'], 'lock')
        if not os.path.exists(lockpath):
            os.mkdir(lockpath)

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
                    # log that lock has been activated
                    wargs = [self.path]
                    WLOG(self.params, '', TextEntry('40-101-00001', args=wargs))
                    break
                except:
                    # whatever the problem sleep for a second
                    time.sleep(0.1)
                    # add to the timer
                    timer += 1
                    # update user every 10 seconds file is locked
                    if (timer % 100 == 0) and (timer != 0):
                        # Warn that lock is waiting due to making the lock dir
                        wmsg = TextEntry('10-101-00001', args=[self.lockname])
                        WLOG(self.params, 'warning', wmsg)
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
        filename = name + '.lock'
        # get absolute path
        abspath = os.path.join(self.path, filename)
        # set up a timer
        timer = 0
        # keep trying to create the folder
        while timer < self.maxwait:
            # if path does not exist try to create it
            if not os.path.exists(abspath):
                try:

                    f = open(abspath, 'w')
                    f.write(filename)
                    f.close()
                    break
                except:
                    # whatever the problem sleep for a second
                    time.sleep(0.1)
                    # add to the timer
                    timer += 1
                    # update user every 10 seconds file is locked
                    if (timer % 100 == 0) and (timer != 0):
                        abspath = os.path.join(self.path, filename)
                        wargs = [self.lockname, abspath]
                        # warn that lock is waiting due to making the lock file
                        wmsg = TextEntry('10-101-00002', args=wargs)
                        WLOG(self.params, 'warning', wmsg)
            # if path does exist just skip
            else:
                break

    def __getfirst(self, name):
        """
        Internal use only: get the first (based on creation time) file in
        self.path

        :return:
        """
        path = self.path

        # check path exists - if it doesn't then create it
        if not os.path.exists(path):
            self.enqueue(name)

        # get the raw list
        rawlist = os.listdir(path)

        # if we don't have this file add it to the end of the list
        if name + '.lock' not in rawlist:
            self.enqueue(name)

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

        if np.isnan(pos):
            eargs = [name + '.lock', path]
            raise ValueError('Impossible Error: {0} not in {1}'.format(*eargs))

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
        filename = name + '.lock'
        abspath = os.path.join(self.path, filename)
        # if the file exists remove it
        if os.path.exists(abspath):
            os.remove(abspath)

    def __clean_name(self, name):
        # loop around bad characters and replace them
        for char in self.bad_chars:
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
        # log progress: lock file added to queue
        filename = name + '.lock'
        abspath = os.path.join(self.path, filename)
        WLOG(self.params, '', TextEntry('40-101-00002', args=[abspath]))
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
        filename = name + '.lock'
        # try to get the first file (this could fail if a file is removed by
        #   another process) - if it fails it is not your turn so wait longer
        try:
            first = self.__getfirst(name)
        except Exception as e:
            return False, e
        # if the unique name is first in the list then we can unlock this file
        if filename == first:
            # log that lock file is unlocked
            abspath = os.path.join(self.path, filename)
            WLOG(self.params, '', TextEntry('40-101-00003', args=[abspath]))
            return True, None
        # else we return False (and ask whether it is my turn later)
        else:
            return False, None

    def dequeue(self, name):
        """
        Used to remove "name" from queue

        :param name:
        :return:
        """
        # log that lock file has been removed from the queue
        filename = name + '.lock'
        abspath = os.path.join(self.path, filename)
        WLOG(self.params, '', TextEntry('40-101-00004', args=[abspath]))
        # once we are finished with a lock we remove it from the queue
        self.__remove_file(name)

    def reset(self):
        """
        Used to remove all entries from a queue (and start again)

        :return:
        """
        # log that lock is deactivated
        WLOG(self.params, '', TextEntry('40-101-00005', args=[self.path]))
        # get the raw list
        if os.path.exists(self.path):
            rawlist = os.listdir(self.path)
        else:
            return
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
    :param name:
    :return:
    """
    def wrap(func):
        def wrapperfunc(*args, **kw):
            # add to the queue
            lock.enqueue(name)
            # timer
            timer = 0
            # find whether it is this name's turn
            cond, error = lock.myturn(name)
            # while the lock is active do not run function
            while not cond:
                # sleep
                time.sleep(1)
                # update user every 10 seconds file is locked
                if (timer % 10 == 0) and (timer != 0):
                    # log that we are waiting in a queue
                    wargs = [lock.path, name, timer]
                    wmsg = TextEntry('10-101-00003', args=wargs)
                    WLOG(lock.params, 'warning', wmsg)
                # find whether it is this name's turn
                cond, error = lock.myturn(name)
                if error is not None:
                    # log that we are waiting in a queue and error generated
                    wargs = [lock.path, name, error, timer]
                    wmsg = TextEntry('10-101-00004', args=wargs)
                    WLOG(lock.params, 'warning', wmsg)
                # increase timer
                timer += 1
            # now try to run the function
            try:
                return func(*args, **kw)
            # finally deactivate the lock
            finally:
                # unlock file
                lock.dequeue(name)
        # return the new function (wrapped)
        return wrapperfunc
    # return the wrapped function
    return wrap


def locker(params, lockfile, my_func, *args, **kwargs):
    # define lock file
    lock = Lock(params, lockfile)
    # ------------------------------------------------------------------
    # define wrapper lock file function
    @synchronized(lock, params['PID'])
    def locked_function():
        return my_func(*args, **kwargs)
    # ------------------------------------------------------------------
    # try to run locked read function
    try:
        return locked_function()
    except KeyboardInterrupt as e:
        lock.reset()
        raise e
    except Exception as e:
        # reset lock
        lock.reset()
        raise e


def reset_lock_dir(params, log=False):
    # get the lock path
    lockpath = os.path.join(params['DRS_DATA_MSG_FULL'], 'lock')
    if not os.path.exists(lockpath):
        return
    # remove empties
    __remove_empty__(params, lockpath, remove_head=False, log=False)


def __remove_empty__(params, path, remove_head=True, log=False):
    if not os.path.isdir(path):
        return

    # remove empty subfolders
    files = os.listdir(path)
    if len(files):
        for f in files:
            fullpath = os.path.join(path, f)
            if os.path.isdir(fullpath):
                __remove_empty__(params, fullpath, log=log)

    # if folder empty, delete it
    files = os.listdir(path)
    if len(files) == 0 and remove_head:
        if log:
            WLOG(params, '', "Removing empty folder: {0}".format(path))
        os.rmdir(path)



# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":

    # testing the locking mechanism
    from multiprocessing import Process
    import string

    _params = constants.load()

    def printfunc(i, j):
        # set up the lock file (usually a file or function)
        mylock = Lock(_params, 'printfunc')

        # this is where we define the locked function
        @synchronized(mylock, '{0}-{1}'.format(i, j))
        def lockprint():
            for k in list(string.ascii_lowercase):
                print('{0}-{1}-{2}'.format(i, j, k))
            time.sleep(0.1)

        # this is where we run the function
        try:
            lockprint()
        except KeyboardInterrupt as e:
            mylock.reset()
            raise e

    for jjjt in range(2):
        jobs = []
        # loop around sub groups (to be run at same time)
        for iiit in range(10):
            # get parallel process
            process = Process(target=printfunc, args=[iiit, jjjt])
            process.start()
            jobs.append(process)
        # do not continue until finished
        for proc in jobs:
            proc.join()


# =============================================================================
# End of code
# =============================================================================
