#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-21 at 09:37

@author: cook


Import rules:
    Not from core.utils

"""
import numpy as np
import os
import random
import time
from typing import Any, Tuple, Union

from apero.base import base
from apero.core import constants
from apero import lang
from apero.core.core import drs_log

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'drs_lock.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get the parameter dictionary
ParamDict = constants.ParamDict
# Get function string
display_func = drs_log.display_func
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
TextEntry = lang.core.drs_lang_text.TextEntry
TextDict = lang.core.drs_lang_text.TextDict
HelpText = lang.core.drs_lang_text.HelpDict


# =============================================================================
# Define functions
# =============================================================================
class Lock:
    """
    Class to control locking of decorated functions
    """

    def __init__(self, params: ParamDict, lockname: str):
        """
        Construct the lock instance

        :param params: ParamDict, parameter dictionary of constants
        :param lockname: str, the name for the lock file
        
        :returns: None
        """
        # set class name
        self.classname = 'Lock'
        # set function
        func_name = display_func(params, '__init__', __NAME__, self.classname)
        # set the bad characters to clean
        self.bad_chars = ['/', '\\', '.', ',']
        # replace all . and whitespace with _
        self.lockname = self.__clean_name(lockname)
        self.params = params
        # get the lock path
        self.lockpath = os.path.join(params['DRS_DATA_MSG'], 'lock')
        # ------------------------------------------------------------------
        # making the lock dir could be accessed in parallel several times
        #   at once so try 10 times with a wait in between
        it, error = 0, None
        while not os.path.exists(self.lockpath) and it < 10:
            try:
                os.mkdir(self.lockpath)
            except Exception as e:
                error = e
                # add one to the number of tries
                it += 1
                # sleep for one second to allow another process to complete this
                time.sleep(1 + 0.1 * random.random())
        # if we had an error and got to 10 tries then cause an error
        if error is not None and it == 10:
            eargs = [type(error), error, self.lockpath, func_name]
            WLOG(params, 'error', TextEntry('00-503-00016', args=eargs))
        # ------------------------------------------------------------------
        self.maxwait = params.get('DB_MAX_WAIT', 100)
        self.path = os.path.join(self.lockpath, self.lockname)
        self.queue = []
        # make the lock directory
        self.__makelockdir()

    def __getstate__(self) -> dict:
        """
        For when we have to pickle the class
        :return:
        """
        # set state to __dict__
        state = dict(self.__dict__)
        # return dictionary state
        return state

    def __setstate__(self, state: dict):
        """
        For when we have to unpickle the class

        :param state: dictionary from pickle
        :return:
        """
        # update dict with state
        self.__dict__.update(state)

    def __makelockdir(self):
        """
        Internal use only: make the lock directory

        :return:
        """
        # set function
        _ = display_func(self.params, '__makelockdir', __NAME__, self.classname)
        # set up a timer
        timer = 0
        # keep trying to create the folder
        while timer < self.maxwait:
            # if path does not exist try to create it
            if not os.path.exists(self.path):
                # noinspection PyBroadException
                try:
                    os.mkdir(self.path)
                    # log that lock has been activated
                    wargs = [self.path]
                    WLOG(self.params, 'debug',
                         TextEntry('40-101-00001', args=wargs))
                    break
                except Exception as _:
                    # whatever the problem sleep for a second
                    time.sleep(0.1 * random.random())
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

    def __makelockfile(self, name: str):
        """
        Internal use only: make the lock file "name.lock"

        :param name: str, the name of the item in lock queue
        
        :return: None - writes lock file to disk
        """
        # set function
        _ = display_func(self.params, '__makelockfile', __NAME__,
                         self.classname)
        # check that path exists
        if not os.path.exists(self.path):
            self.__makelockdir()
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
                # noinspection PyBroadException
                try:
                    # write filename
                    with open(abspath, 'w') as f:
                        msg = 'File={0} Timer={1}'
                        f.write(msg.format([filename, timer]))
                    break
                except Exception as _:
                    # whatever the problem sleep for a second
                    time.sleep(0.1 * random.random())
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

    def __getfirst(self, name: str) -> str:
        """
        Internal use only: get the first (based on creation time) file in
        self.path
        
        :param name: str, the name of the item in lock queue

        :returns: str, the first item in the lock queue 
        """
        # set function
        _ = display_func(self.params, '__getfirst', __NAME__, self.classname)
        # set path from self.path
        path = self.path
        # check path exists - if it doesn't then create it
        if not os.path.exists(path):
            self.enqueue(name)
        # get the raw list
        rawlist = np.sort(os.listdir(path))
        # if we don't have this file add it to the end of the list
        if name + '.lock' not in rawlist:
            self.enqueue(name)
            rawlist = np.sort(os.listdir(path))
        # deal with no raw files
        if len(rawlist) == 0:
            self.enqueue(name)
            rawlist = np.sort(os.listdir(path))
        # get times
        pos, mintime, it = np.nan, np.inf, 0
        for it in range(len(rawlist)):
            # get the absolute path
            abspath = os.path.join(path, rawlist[it])
            # get the creation time for the file
            filetime = os.path.getctime(abspath)
            # check if it is older than mintime
            if filetime < mintime:
                mintime = filetime
                pos = it
        # deal with a NaN position (impossible?)
        if np.isnan(pos):
            eargs = [name + '.lock', path, ','.join(rawlist[it])]
            emsg = 'Impossible Error: {0} not in {1} '
            emsg += '\n\t Raw files: {2}'
            raise ValueError(emsg.format(*eargs))

        # return list
        return rawlist[pos]

    def __remove_file(self, name: str):
        """
        Internal use only: Remove file "name.lock"

        :param name: str, the name of the item in lock queue
        
        :return: None
        """
        # set function
        _ = display_func(self.params, '__remove_file', __NAME__, self.classname)
        # clean name
        name = self.__clean_name(name)
        # get the absolute path
        filename = name + '.lock'
        abspath = os.path.join(self.path, filename)
        # loop until we have desired result (or have tried 10 times)
        attempt = 0
        while 1:
            # if the file exists remove it
            if os.path.exists(abspath):
                # do not remove lock path
                if abspath != self.lockpath:
                    # remove file
                    try:
                        attempt += 1
                        os.remove(abspath)
                    except Exception as e:
                        if attempt >= 10:
                            # log warning for error
                            eargs = [abspath, type(e), str(e)]
                            emsg = TextEntry('10-101-00007', args=eargs)
                            WLOG(self.params, 'warning', emsg)
                            break
                        else:
                            continue
                else:
                    break
            else:
                break

    def __clean_name(self, name: str) -> str:
        """
        Clean the item name (replace bad characters with '_')

        :param name: str, the name of the item in lock queue

        :return: str, the cleaned name of the item in lock queue
        """
        # set function
        _ = display_func(self.params, '__clean_name', __NAME__, self.classname)
        # loop around bad characters and replace them
        for char in self.bad_chars:
            name = name.replace(char, '_')
        # return the cleaned name
        return name

    def enqueue(self, name: str):
        """
        Used to add "name" item to the queue

        :param name: str, the name of the item in lock queue

        :return: None - writes name.lock to disk (and waits a short time)
        """
        # set function
        _ = display_func(self.params, '__clean_name', __NAME__, self.classname)
        # clean name
        name = self.__clean_name(name)
        # log progress: lock file added to queue
        filename = name + '.lock'
        abspath = os.path.join(self.path, filename)
        WLOG(self.params, 'debug', TextEntry('40-101-00002', args=[abspath]))
        # add unique name to queue
        self.__makelockfile(name)
        # put in just to see if we are appending too quickly
        time.sleep(0.1 * random.random())

    def myturn(self, name: str) -> Tuple[bool, Union[Exception, None]]:
        """
        Used to check whether it is time to run function for "name" (based on
        position in queue)

        :param name: str, the name of the item in lock queue

        :return: tuple, 1. bool - whether it is 'name' item turn to be unlocked
                        2. None or exception (to be handled elsewhere)
        """
        # set function
        _ = display_func(self.params, 'myturn', __NAME__, self.classname)
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
            WLOG(self.params, 'debug',
                 TextEntry('40-101-00003', args=[abspath]))
            return True, None
        # else we return False (and ask whether it is my turn later)
        else:
            return False, None

    def dequeue(self, name: str):
        """
        Used to remove "name" from queue

        :param name: str, the name of the item in lock queue

        :return: None - removes lock file for 'name' to 'name' item can be
                 unlocked
        """
        # set function
        _ = display_func(self.params, 'dequeue', __NAME__, self.classname)
        # log that lock file has been removed from the queue
        filename = name + '.lock'
        abspath = os.path.join(self.path, filename)
        WLOG(self.params, 'debug', TextEntry('40-101-00004', args=[abspath]))
        # once we are finished with a lock we remove it from the queue
        self.__remove_file(name)

    def reset(self):
        """
        Used to remove all entries from a queue (and start again)

        :return: None - remove lock file and all items in it (reset lock queue)
        """
        # set function
        _ = display_func(self.params, 'reset', __NAME__, self.classname)
        # log that lock is deactivated
        WLOG(self.params, 'debug', TextEntry('40-101-00005', args=[self.path]))
        # get the raw list
        if os.path.exists(self.path):
            rawlist = np.sort(os.listdir(self.path))
        else:
            return
        # loop around files
        for it in range(len(rawlist)):
            # get the absolute path
            abspath = os.path.join(self.path, rawlist[it])
            # remove files
            if os.path.exists(abspath):
                if abspath == self.lockpath:
                    continue
                # remove file
                try:
                    os.remove(abspath)
                except Exception as e:
                    # log warning for error
                    eargs = [abspath, type(e), str(e)]
                    emsg = TextEntry('10-101-00006', args=eargs)
                    WLOG(self.params, 'warning', emsg)
        # now remove directory (if possible)
        if os.path.exists(self.path):
            # do not remove lock path (used by other processes)
            if self.path != self.lockpath:
                # remove path
                try:
                    os.removedirs(self.path)
                except Exception as e:
                    # log warning for error
                    eargs = [self.path, type(e), str(e)]
                    emsg = TextEntry('10-101-00005', args=eargs)
                    WLOG(self.params, 'warning', emsg)


def synchronized(lock: Lock, name: str):
    """
    Synchroisation decorator - wraps the function to lock
    calls to function are added to a queue based on the lock given and
    the name for this call to the function (must be unique)

    use as follows:

    1. generate lock instance:
    >> mylock = Lock(params, lockfile)

    2. decorate a function that is to be locked
    >> @synchronized(mylock, name)
    >> def my_locked_function(*args, **kwargs):
    >>     do something pythonic that requires locking

    3. call locked function normally
    >> my_locked_function(*args, **kwargs)


    :param lock: Lock instance
    :param name: str, the name of the item in lock queue

    :return: wrapper around function (decorator uses this in place of the
             function itself)
    """
    def wrap(func):
        """
        Internal wrap around decorator - required to pull in function to be
        locked (see how to on defining decorator)

        :param func: function to be locked

        :return: return the wrapper function (which does the locking before
                 running 'func' - passes all args, kwargs to the 'func'
        """
        def wrapperfunc(*args, **kw):
            """
            The proxy wrapper of 'func' i.e. in here is where we do the locking
            then run the function - this function is what is called when
            'func' is called (and is run internally after all locking
            functionality is complete

            :param args: the positional arguments passed to 'func'
            :param kw: the keyword arguments passed to 'func'
            :return: the returns of 'func' for args, kwargs
            """
            # set function
            _ = display_func(lock.params, 'wrapperfunc', __NAME__)
            # add to the queue
            lock.enqueue(name)
            # timer
            timer = 0
            # find whether it is this name's turn
            cond, error = lock.myturn(name)
            time.sleep(0.1 * random.random())
            # while the lock is active do not run function
            while not cond:
                # sleep
                time.sleep(1)
                # if we reach 240 seconds reset the timer and reset the lock
                #   directory (something has clashed)
                if timer > 240:
                    # reset the timer
                    timer = 0
                    # wait 1 second + a bit (so two or more don't hit this
                    #   at the same time)
                    time.sleep(1 + random.random())
                    # reset all lock files
                    lock.reset()
                # update user every 60 seconds file is locked
                if (timer % 60 == 0) and (timer != 0):
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


def locker(params: ParamDict, lockfile: str, my_func: Any, *args, **kwargs):
    """
    A one function solution to avoid having to deal with decorators.
    Lock file is created in here, and locked function is decorated/run
    using 'my_func' as the function to be locked and passing all args, kwargs
    to it

    :param params: ParamDict, the parameter dictionary of constants
    :param lockfile: str, the file that is being locked
    :param my_func: function, the function to lock at until specific item is
                    unlocked
    :param args: positional arguments passed to my_func (after locking
                 functionality)
    :param kwargs: optional arguments passed to my_func (after locking
                   functionatity)

    :return: the return of 'my_func' for args, kwargs
    """
    # set function
    _ = display_func(params, 'locker', __NAME__)
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


def reset_lock_dir(params: ParamDict, log: bool = False):
    """
    Reset the full lock directory (if empty and if it exists) of all
    sub-directories - should only be used when we know no locking is expected
    after this point

    :param params: ParamDict, the parameter dictionary of constants
    :param log: bool, if True logs the removal of files (via __remove_empty__)

    :return: None - just removes lock directory
    """
    # set function
    _ = display_func(params, 'locker', __NAME__)
    # get the lock path
    lockpath = os.path.join(params['DRS_DATA_MSG_FULL'], 'lock')
    if not os.path.exists(lockpath):
        return
    # remove empties
    __remove_empty__(params, lockpath, remove_head=False, log=log)


def __remove_empty__(params: ParamDict, path: str, remove_head: bool = True,
                     log: bool = False):
    """
    Remove empty directories/sub-directories from under 'path' (and remove
    'path' if remove_head = True

    :param params: ParamDict, the parameter dictionary of constants
    :param path: str, the path to remove all empty sub-directories from
    :param remove_head: bool, if True also try to remove the path directory
                        (after removing all sub-directories) again if empty
    :param log: bool, if True log that we are remove directories

    :return: None - just removes directories
    """
    # set function
    _ = display_func(params, '__remove_empty__', __NAME__)
    # define function name
    func_name = __NAME__ + '.__remove_empty__()'
    # check if path is not a directory or if path is link
    if not os.path.isdir(path) or os.path.islink(path):
        return
    # remove empty subfolders
    files = np.sort(os.listdir(path))
    if len(files):
        for f in files:
            fullpath = os.path.join(path, f)
            if os.path.isdir(fullpath):
                __remove_empty__(params, fullpath, log=log)
    # if folder empty, delete it
    files = np.sort(os.listdir(path))
    if len(files) == 0 and remove_head:
        if log:
            WLOG(params, 'debug', "Removing empty folder: {0}".format(path))
        # try to remove or report warning
        try:
            os.rmdir(path)
        except Exception as e:
            eargs = [path, type(e), e, func_name]
            emsg = ('Cannot remove dir {0}. \n\t Error {1}: {2} '
                    '\n\t function = {3}')
            WLOG(params, 'warning', emsg.format(*eargs))


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # testing the locking mechanism in a multiprocess way

    # testing the locking mechanism
    from multiprocessing import Process
    import string
    # load parameters
    _params = constants.load()

    # define a function to print (this is the function to be called in a
    #    parallelised way)
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
        # allow Ctrl+Z interrupt - and deal with locking accordingly
        except KeyboardInterrupt as e:
            mylock.reset()
            raise e
    # loop around 2 iterations for each with 10 sub groups
    for jjjt in range(2):
        jobs = []
        # loop around sub groups (to be run at same time)
        for iiit in range(10):
            # get parallel process
            process = Process(target=printfunc, args=(iiit, jjjt))
            process.start()
            jobs.append(process)
        # do not continue until finished
        for proc in jobs:
            proc.join()

# =============================================================================
# End of code
# =============================================================================
