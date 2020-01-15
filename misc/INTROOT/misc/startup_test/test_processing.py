#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-12-19 at 16:44

@author: cook
"""
import glob
import time
from multiprocessing import Manager, Process
from collections import OrderedDict

from SpirouDRS import spirouCore
from misc.startup_test import recipes_spirou, spirouStartup2

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'test_processing.py'
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt
# Define some paths
PATH = '/scratch/Projects/spirou/data_dev/tmp/*/*/*'


# PATH = '/scratch/Projects/spirou/data_dev/tmp/TEST1a/20180805/*d_pp.fits'

RECIPES = recipes_spirou.recipes
DEBUG = False
MAX_CORES = 5
# global variables
MANAGER = Manager()
# -----------------------------------------------------------------------------


# =============================================================================
# Define functions
# =============================================================================
def generate_runs(__recipe__, __files__, __filters__=None, **kwargs):
    # set up process id
    pid = spirouStartup2.assign_pid()
    # Clean WLOG
    WLOG.clean_log(pid)
    # get a recipe to test
    recipe = spirouStartup2.find_recipe(__recipe__)
    # quietly load DRS parameters (for setup)
    recipe.get_drs_params(quiet=True, pid=pid)
    # generate runs
    args = [__files__, __filters__]
    pruns, druns = recipe.generate_runs_from_filelist(*args, **kwargs)

    if DEBUG:
        for run_it in pruns:
            print(run_it)

    # return the runs
    return [pruns, druns], recipe


def execute_runs(p, recipe, runs, processes=1):


    if DEBUG:
        return 0

    # get subgroups based on number of processes
    pgroups = parallelize(runs[0], processes)
    dgroups = parallelize(runs[1], processes)

    # run parallel processes
    if processes > 1:
        errors = MANAGER.dict()
        times = MANAGER.dict()
        pp = []
        for sub_group in pgroups:
            # start the process
            pargs = (p, recipe, dgroups[sub_group], pgroups[sub_group],
                     times, errors)
            process = Process(target=run_wrapper, args=pargs)
            process.start()
            # append process to list
            pp.append(process)
        # do not continue with code until all cores have finished
        for process in pp:
            while process.is_alive():
                pass
        # get results
        for process in pp:
            process.join()

    # run single processes
    else:
        times, errors = OrderedDict(), OrderedDict()
        for sub_group in pgroups:
            pargs = [p, recipe, dgroups[sub_group], pgroups[sub_group],
                     times, errors]
            times, errors = run_wrapper(*pargs)

    # return times and errors
    return times, errors


def run_wrapper(p, recipe, druns, pruns, times, errors):
    # loop around runs
    for it in range(len(druns)):
        # get this iterations run arguments
        run_kwargs = druns[it]
        run_statement = pruns[it]
        # print progress
        WLOG(p, 'warning', ['', run_statement, ''])
        # try to run
        try:
            start = time.time()
            recipe.main(**run_kwargs)
            times[run_statement] = time.time() - start
        # Manage unexpected errors
        except Exception as e:
            wmsgs = ['Run had an unexpected error']
            for msg in str(e).split('\n'):
                wmsgs.append('\t' + msg)
            WLOG(p, 'warning', wmsgs)
            errors[run_statement] = [str(e)]
        # Manage expected errors
        except SystemExit as e:
            wmsgs = ['Run had an expected error']
            for msg in str(e).split('\n'):
                wmsgs.append('\t' + msg)
            WLOG(p, 'warning', wmsgs)
            errors[run_statement] = [str(e)]
        # make sure all plots are closed
        sPlt.closeall()
        # return times and errors
        return times, errors


def parallelize(jobs, processes):
    # deal with less entries than max_number
    if processes > len(jobs):
        processes = len(jobs)
    # storage for groups
    groups = OrderedDict()
    # loop around groups
    for it in range(processes):
        # get name
        name = 'Group {0}/{1}'.format(it + 1, processes)
        groups[name] = jobs[it::processes]
    # return groups
    return groups


# def main():
if __name__ == "__main__":
    pp = spirouStartup2.get_params(recipe=__NAME__)
    # get list of files to test
    files = glob.glob(PATH)
    # storage for times
    times, errors = OrderedDict(), OrderedDict()

    # ----------------------------------------------------------------------
    # log
    WLOG(pp, 'info', 'Test for test_recipe.py')
    # trigger
    test_runs, test_recipe = generate_runs('test_recipe.py', files)
    exargs = [pp, test_recipe, test_runs]
    test_times, test_errors = execute_runs(*exargs, processes=MAX_CORES)
    for key in test_times:
        times[key] = test_times[key]
    for key in test_errors:
        errors[key] = test_errors[key]
    # ----------------------------------------------------------------------
    # log
    WLOG(pp, 'info', 'Test for cal_dark')
    # trigger
    dark_runs, dark_recipe = generate_runs('cal_DARK_spirou.py', files,
                                           plot=1, debug=1)
    # execute_runs(dark_recipe, dark_runs, processes=MAX_CORES)
    # ----------------------------------------------------------------------
    # log
    WLOG(pp, 'info', 'Test for cal_badpix')
    # trigger
    badpix_runs, badpix_recipe = generate_runs('cal_BADPIX_spirou.py', files,
                                               plot=1)
    # ----------------------------------------------------------------------
    # log
    WLOG(pp, 'info', 'Test for cal_loc')
    # trigger
    loc_runs, loc_recipe = generate_runs('cal_loc_RAW_spirou.py', files,
                                         plot=1)
    # ----------------------------------------------------------------------
    # log
    WLOG(pp, 'info', 'Test for cal_extract')
    # define filters
    filters = dict(DPRTYPE=['OBJ_DARK', 'OBJ_FP'])
    # trigger
    ext_runs, ext_recipe = generate_runs('cal_extract_RAW_spirou.py', files,
                                         filters, add2calib=False)


    # ----------------------------------------------------------------------
    # Print timing
    # ----------------------------------------------------------------------
    if len(times) > 0:
        WLOG(pp, 'info', ['', 'Timings:', ''])
        tlog = []
        for key in times:
            tlog.append(key)
            tlog.append('\t\tTime taken = {0:.3f} s'.format(times[key]))
            tlog.append('')
        WLOG(pp, '', tlog)

    # ----------------------------------------------------------------------
    # Print Errors
    # ----------------------------------------------------------------------
    if len(errors) > 0:
        WLOG(pp, '', ['', 'Errors:', ''])
        emsgs = []
        for key in errors:
            emsgs.append(key)
            emsgs += errors[key]
            emsgs += ['', '']
        WLOG(pp, 'warning', emsgs)

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    wmsg = 'Recipe {0} has been successfully completed'
    WLOG(pp, 'info', wmsg.format(pp['PROGRAM']))
    # return a copy of locally defined variables in the memory
    # return dict(locals())





# =============================================================================
# Start of code
# =============================================================================
# if __name__ == "__main__":
#     # run main with no arguments (get from command line - sys.argv)
#     ll = main()
#     # exit message if in debug mode
#     spirouStartup.Exit(ll, has_plots=False)

# =============================================================================
# End of code
# =============================================================================




# =============================================================================
# End of code
# =============================================================================
