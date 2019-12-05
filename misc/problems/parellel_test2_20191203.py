#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Problem: certain sub-processes are not completing

Created on 2019-12-03 at 17:38

@author: cook
"""
import time
from multiprocessing import Pool, Manager, Event
import numpy as np
import warnings
import os
import sys
import string

# ------------------------------------------------------------------------------
# constants
# ------------------------------------------------------------------------------
# max time to be in the taxing function (similar to my recipes)
#  we also add +/- 25% to this time so they do not all finish at the same time
MAXTIME = 10
# a high number of cores (way higher than normal)
CORES = 20
# number of groups (we have multiple groups of parallel processes
#                   one group (with X cores) starts after another
#                   finishes (with X cores))
GROUPS = 1
# number of sub groups (within a group we have the recipe runs) these
#   sub-groups are all the same recipe and divided by the number of cores
SUBGROUPS = 5

# On error what should we do
STOP_AT_ERROR = True

# ------------------------------------------------------------------------------
# This is to test a sys.exit()
TEST_SYS_EXIT = True
# this is the group num + core num to exit in [group num, core num, sub group]
TEST_SYS_NUMS = [0, 1, 'b']
# ------------------------------------------------------------------------------
# this is to test a ValueError exit (a standard python exit)
TEST_VALUE_ERROR = False
# this is the group num + core num to exit in [group num, core num, sub group]
TEST_VALUE_NUMS = [0, 1, 'b']
# ------------------------------------------------------------------------------
# This is to test a sys.exit()
TEST_OS_EXIT = False
# this is the group num + core num to exit in [group num, core num, sub group]
TEST_OS_NUMS = [0, 1, 'b']


# ------------------------------------------------------------------------------
# functions
# ------------------------------------------------------------------------------
def taxing(it, jt, kt):
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
        if TEST_SYS_NUMS[0] == it and TEST_SYS_NUMS[1] == jt and TEST_SYS_NUMS[2] == kt:
            sys.exit(0)
    # deal with value error tests
    if TEST_VALUE_ERROR:
        if TEST_VALUE_NUMS[0] == it and TEST_VALUE_NUMS[1] == jt and TEST_SYS_NUMS[2] == kt:
            raise ValueError('ValueError {0}-{1}-{2}'.format(it, jt, kt))
    # deal with os exit tests
    if TEST_OS_EXIT:
        if TEST_OS_NUMS[0] == it and TEST_OS_NUMS[1] == jt and TEST_SYS_NUMS[2] == kt:
            print('EXIT {0}-{1}-{2}'.format(it, jt, kt))
            os._exit(0)


def myfunc(it, jt, kt, event, rdict):
    """
    This simulates the recipe controller
    This is what is ran by multiprocessing.Process
    this should not change (other than how we call event)
    """
    if event.is_set():
        print('Skip group={0} core={1} sub={2}'.format(it, jt, kt))
        return rdict
    try:
        # run a function that does something
        print('Run: group={0} core={1} sub={2}'.format(it, jt, kt))
        taxing(it, jt, kt)
        print('Finish: group={0} core={1} sub={2}'.format(it, jt, kt))
        # add to rdict after
        rdict[(it, jt, kt)] = True
    except KeyboardInterrupt:
        print('KeyboardInterrupt group={0} core={1} sub={2}'
              ''.format(it, jt, kt))
        event.set()
    except Exception as e:
        print('Exception group={0} core={1} sub={2}'.format(it, jt, kt))
        if STOP_AT_ERROR:
            event.set()
    except SystemExit:
        print('SystemExit group={0} core={1} sub={2}'.format(it, jt, kt))
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
    # event = Event()
    # shared data between processes
    manager = Manager()
    # just a dictionary
    return_dict = manager.dict()
    event = manager.Event()

    letters = string.ascii_lowercase

    # number of runs = number_groups * number_cores
    #                = 3 * 100
    # loop around groups (number of times to run the set of parallel jobs)
    for it in range(GROUPS):
        params_per_process = []

        jobs = []
        # these are the cores (set ridiculously high)
        #    - these all start in parallel
        for jt in range(CORES):
            for kit in range(SUBGROUPS):
                if SUBGROUPS < len(letters):
                    kt = letters[kit]
                # after starting all parallel processes we join each one,
                else:
                        kt = kit
                params_per_process.append((it, jt, kt, event, return_dict))

        # start parellel jobs
        pool = Pool(CORES)
        pool.starmap(myfunc, params_per_process)

    # as a check
    print('Number of runs expected: {0}'.format(GROUPS * CORES * SUBGROUPS))
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
#
#
