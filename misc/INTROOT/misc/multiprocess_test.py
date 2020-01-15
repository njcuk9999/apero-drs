#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-06-11 at 13:40

@author: cook
"""

from multiprocessing import Process, Manager, Event
import sys

# =============================================================================
# Define variables
# =============================================================================

# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
def myfunc(name, return_dict, event):
    print('Running {0}'.format(name))
    if name == 'Run3':
        event.set()
    return_dict[name] = 'OUT' + name


def terminate_jobs(jobs):
    for job in jobs:
        job.terminate()


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    grouplist = [['Run1a', 'Run1b', 'Run1c'], ['Run2a', 'Run2b'], ['Run3'],
                 ['Run4a', 'Run4b', 'Run4c', 'Run4d', 'Run4e']]

    # start process manager
    manager = Manager()
    event = Event()
    return_dict = manager.dict()
    # loop around groups
    for g_it, group in enumerate(grouplist):
        # skip if event is set
        if event.is_set():
            continue
        # process storage
        jobs = []
        # loop around sub groups (to be run at same time)
        for runlist_group in group:
            # get args
            args = [runlist_group, return_dict, event]
            # get parallel process
            process = Process(target=myfunc, args=args)
            process.start()
            jobs.append(process)
        # do not continue until finished
        for proc in jobs:
            proc.join()
            if event.is_set():
                terminate_jobs(jobs)





# =============================================================================
# End of code
# =============================================================================
