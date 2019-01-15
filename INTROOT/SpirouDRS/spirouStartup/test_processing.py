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
from multiprocessing import Process
from collections import OrderedDict

from SpirouDRS import spirouStartup
from SpirouDRS import spirouCore
from SpirouDRS.spirouStartup import spirouStartup2
from SpirouDRS.spirouStartup import recipes_spirou


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
RECIPES = recipes_spirou.recipes
DEBUG = True
MAX_CORES = 5
# global variables
ERRORS = OrderedDict()
TIMES = OrderedDict()
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


def execute_runs(recipe, runs, processes=1):
    if DEBUG:
        return 0

    # get subgroups based on number of processes
    pgroups = parallelize(runs[0], processes)
    dgroups = parallelize(runs[1], processes)

    # run parallel processes
    if processes > 1:
        pp = []
        for sub_group in pgroups:
            # start the process
            pargs = (recipe, dgroups[sub_group], pgroups[sub_group])
            process = Process(target=run_wrapper, args=pargs)
            process.start()
        # do not continue with code until all cores have finished
        for process in pp:
            while process.is_alive():
                pass
    # run single processes
    else:
        for sub_group in pgroups:
            run_wrapper(recipe, dgroups[sub_group], pgroups[sub_group])


def run_wrapper(recipe, druns, pruns):
    # allow changing of global constants (for storage)
    global ERRORS
    global TIMES
    # loop around runs
    for it in range(len(druns)):
        # get this iterations run arguments
        run_kwargs = druns[it]
        run_statement = pruns[it]
        # print progress
        WLOG(recipe.drs_params, 'warning', ['', run_statement, ''])
        # try to run
        try:
            start = time.time()
            recipe.main(**run_kwargs)
            TIMES[run_statement] = time.time() - start
        # Manage unexpected errors
        except Exception as e:
            wmsgs = ['Run had an unexpected error']
            for msg in str(e).split('\n'):
                wmsgs.append('\t' + msg)
            WLOG(recipe.drs_params, 'warning', wmsgs)
            ERRORS[run_statement] = [str(e)]
        # Manage expected errors
        except SystemExit as e:
            wmsgs = ['Run had an expected error']
            for msg in str(e).split('\n'):
                wmsgs.append('\t' + msg)
            WLOG(recipe.drs_params, 'warning', wmsgs)
            ERRORS[run_statement] = [str(e)]
        # make sure all plots are closed
        sPlt.closeall()


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
    p = spirouStartup2.get_params(recipe=__NAME__.replace('.py', ''))
    # get list of files to test
    files = glob.glob(PATH)

    # ----------------------------------------------------------------------
    # log
    WLOG(p, 'info', 'Test for test_recipe.py')
    # trigger
    test_runs, test_recipe = generate_runs('test_recipe.py', files)
    execute_runs(test_recipe, test_runs, processes=MAX_CORES)
    # ----------------------------------------------------------------------
    # log
    WLOG(p, 'info', 'Test for cal_dark')
    # trigger
    dark_runs, dark_recipe = generate_runs('cal_DARK_spirou.py', files,
                                           plot=1, debug=1)
    # execute_runs(dark_recipe, dark_runs, processes=MAX_CORES)
    # ----------------------------------------------------------------------
    # log
    WLOG(p, 'info', 'Test for cal_badpix')
    # trigger
    badpix_runs, badpix_recipe = generate_runs('cal_BADPIX_spirou.py', files,
                                               plot=1)
    # ----------------------------------------------------------------------
    # log
    WLOG(p, 'info', 'Test for cal_loc')
    # trigger
    loc_runs, loc_recipe = generate_runs('cal_loc_RAW_spirou.py', files,
                                         plot=1)
    # ----------------------------------------------------------------------
    # log
    WLOG(p, 'info', 'Test for cal_extract')
    # define filters
    filters = dict(DPRTYPE=['OBJ_DARK', 'OBJ_FP'])
    # trigger
    ext_runs, ext_recipe = generate_runs('cal_extract_RAW_spirou.py', files,
                                         filters, add2calib=False)


    # ----------------------------------------------------------------------
    # Print timing
    # ----------------------------------------------------------------------
    WLOG(p, 'info', ['', 'Timings:', ''])
    tlog = []
    for key in TIMES:
        tlog.append(key)
        tlog.append('\t\tTime taken = {0:.3f} s'.format(TIMES[key]))
    WLOG(p, 'info', tlog)

    # ----------------------------------------------------------------------
    # Print Errors
    # ----------------------------------------------------------------------
    WLOG(p, '', ['', 'Errors:', ''])
    emsgs = []
    for key in ERRORS:
        emsgs.append(key)
        emsgs += ERRORS[key]
        emsgs += ['', '']
    WLOG(p, 'warning', emsgs)

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    wmsg = 'Recipe {0} has been successfully completed'
    WLOG(p, 'info', wmsg.format(p['PROGRAM']))
    # return a copy of locally defined variables in the memory
    # return dict(locals())





# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()
    # exit message if in debug mode
    spirouStartup.Exit(ll, has_plots=False)

# =============================================================================
# End of code
# =============================================================================




# =============================================================================
# End of code
# =============================================================================
