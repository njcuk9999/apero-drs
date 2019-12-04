#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Problem: certain sub-processes are not completing

Created on 2019-12-03 at 17:38

@author: cook
"""
import time
from multiprocessing import Process, Manager, Event
import numpy as np
import warnings
import os
import sys


# ------------------------------------------------------------------------------
# constants
# ------------------------------------------------------------------------------
# max time to be in the taxing function (similar to my recipes)
#  we also add +/- 25% to this time so they do not all finish at the same time
MAXTIME = 10
# a high number of cores (way higher than normal)
CORES = 100
# number of groups (we have multiple groups of parallel processes
#                   one group (with X cores) starts after another
#                   finishes (with X cores))
GROUPS = 3

# On error what should we do
STOP_AT_ERROR = False

# ------------------------------------------------------------------------------
# This is to test a sys.exit()
TEST_SYS_EXIT = False
# this is the group num + core num to exit in [group num, core num]
TEST_SYS_NUMS = [1, 1]
# ------------------------------------------------------------------------------
# this is to test a ValueError exit (a standard python exit)
TEST_VALUE_ERROR = False
# this is the group num + core num to exit in [group num, core num]
TEST_VALUE_NUMS = [1, 1]
# ------------------------------------------------------------------------------
# This is to test a sys.exit()
TEST_OS_EXIT = False
# this is the group num + core num to exit in [group num, core num]
TEST_OS_NUMS = [1, 1]


# ------------------------------------------------------------------------------
# functions
# ------------------------------------------------------------------------------
def taxing(it, jt):
    """
    This simulates running a recipe
    (nothing in here should change)
    """
    stop_loop = False
    start = time.time()
    # set up x
    x = it + jt
    # add a random component to the time
    randcomp = np.random.uniform(-MAXTIME/4, MAXTIME/4)
    # create a large-ish array
    y = np.random.normal(0, 1, 4096*4096).reshape((4096, 4096))
    with warnings.catch_warnings(record=True) as _:
        z = y ** np.log(y)
        z = z ** y
    # loop until time is up
    while not stop_loop:
        x*x
        if time.time() - start > (MAXTIME + randcomp):
            stop_loop = True

    # --------------------------------------------------------------------------
    # deal with sys exit tests
    if TEST_SYS_EXIT:
        if TEST_SYS_NUMS[0] == it and TEST_SYS_NUMS[1] == jt:
            sys.exit(0)
    # deal with value error tests
    if TEST_VALUE_ERROR:
        if TEST_VALUE_NUMS[0] == it and TEST_VALUE_NUMS[1] == jt:
            raise ValueError('ValueError {0}-{1}'.format(it, jt))
    # deal with os exit tests
    if TEST_OS_EXIT:
        if TEST_OS_NUMS[0] == it and TEST_OS_NUMS[1] == jt:
            os._exit(0)


def myfunc(it, jt, event, rdict):
    """
    This simulates the recipe controller
    This is what is ran by multiprocessing.Process
    this should not change (other than how we call event)
    """
    if event.is_set():
        print('Skip group={0} core={1}'.format(it, jt))
        return rdict
    try:
        # run a function that does something
        print('Run: group={0} core={1}'.format(it, jt))
        taxing(it, jt)
        print('Finish: group={0} core={1}'.format(it, jt))
        # add to rdict after
        rdict[(it, jt)] = True
    except KeyboardInterrupt:
        print('KeyboardInterrupt group={0} core={1}'.format(it, jt))
        event.set()
    except Exception as e:
        print('Exception group={0} core={1}'.format(it, jt))
        if STOP_AT_ERROR:
            event.set()
    except SystemExit:
        print('SystemExit group={0} core={1}'.format(it, jt))
        if STOP_AT_ERROR:
            event.set()
    # rdict is return and multiprocessing manages combining
    # the dictionary between parallel processes
    return rdict


# ------------------------------------------------------------------------------
# main
# ------------------------------------------------------------------------------
if __name__ == '__main__':

    # event handling (using .is_set and set)
    event = Event()
    # shared data between processes
    manager = Manager()
    # just a dictionary
    return_dict = manager.dict()

    # number of runs = number_groups * number_cores
    #                = 3 * 100
    # loop around groups (number of times to run the set of parallel jobs)
    for it in range(GROUPS):
        jobs = []
        # these are the cores (set ridiculously high)
        #    - these all start in parallel
        for jt in range(CORES):
            process = Process(target=myfunc, args=[it, jt, event, return_dict])
            process.start()
            jobs.append(process)
        # after starting all parallel processes we join each one,
        #  wait then join the next
        #  --> all jobs must terminate to move on to the next group
        for pit, proc in enumerate(jobs):
            proc.join()

    # as a check
    print('Number of runs expected: {0}'.format(GROUPS * CORES))
    print('Number of runs processed: {0}'.format(len(return_dict.keys())))


# ==========================================================================
#
#         NOTES
#
# ==========================================================================
#
#        TEST_SYS_EXIT is caught - we lose 1 entry from rdict
#                                  processes in later groups run
#                                  (if STOP_AT_ERROR=False)
#
#        TEST_VALUE_ERROR is caught - we lose 1 entry from rdict
#                                     processes in later groups run
#                                     (if STOP_AT_ERROR=False)
#
#        TEST_OS_EXIT is not caught - we lose 1 entry from rdict
#
