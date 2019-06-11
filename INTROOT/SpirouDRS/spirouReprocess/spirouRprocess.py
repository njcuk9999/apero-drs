#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-06-10 at 13:38

@author: cook
"""
from __future__ import division
import numpy as np
import os
import multiprocessing
from multiprocessing import Process, Manager

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouRgen.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt
# Get param dictionary
ParamDict = spirouConfig.ParamDict


# =============================================================================
# Define user functions
# =============================================================================
def process_run_list(params, runlist):
    # get number of cores
    cores = get_cores(params)
    # pipe to correct module
    if cores == 1:
        # log process
        WLOG(params, 'info', 'Running with 1 core')
        # run as linear process
        rdict = linear_process(params, runlist)
    else:
        # log process
        WLOG(params, 'info', 'Running with {0} cores'.format(cores))
        # run as multiple processes
        rdict = multi_process(params, runlist, cores)
    # convert to ParamDict and set all sources
    odict = []
    keys = np.sort(np.array(list(rdict.keys())))
    for key in keys:
        odict.append(ParamDict(rdict[key]))

    # return the output array (dictionary with priority as key)
    #    values is a parameter dictionary consisting of
    #        RECIPE, NIGHT_NAME, ARGS, ERROR, WARNING, OUTPUTS
    return rdict


# =============================================================================
# Define processing functions
# =============================================================================
def linear_process(params, runlist, return_dict=None, number=0, cores=1):

    # deal with empty return_dict
    if return_dict is None:
        return_dict = dict()
    # loop around runlist
    for run_item in runlist:
        # ------------------------------------------------------------------
        # get the module
        module = run_item.recipemod
        # get the kwargs
        kwargs = run_item.kwargs
        # get the priority
        priority = run_item.priority
        # parameters to save
        pp = dict()
        pp['RECIPE'] = run_item.recipename
        pp['NIGHT_NAME'] = run_item.nightname
        pp['ARGS'] = kwargs
        pp['RUNSTRING'] = run_item.runstring
        # ------------------------------------------------------------------
        # log what we are running
        wmsg = 'ID{0:05d} | {1}'.format(priority, run_item.runstring)
        WLOG(params, 'info', wmsg, colour='magenta')
        # deal with a debug run
        if params['DEBUG']:
            # log which core is being used (only if using multiple cores)
            if cores > 1:
                wargs = ['', number, cores, run_item.nightname]
                wmsg = '{0:7s} | core = {1}/{2} night = "{3}"'.format(*wargs)
                WLOG(params, '', wmsg, colour='magenta')
            # add default outputs
            pp['ERROR'] = []
            pp['WARNING'] = []
            pp['OUTPUTS'] = dict()
        else:
            # try to run the main function
            try:
                # ----------------------------------------------------------
                # run main function of module
                ll_item = module.main(**kwargs)
                # ----------------------------------------------------------
                # close all plotting
                sPlt.closeall()
                # keep only some parameters
                pp['ERROR'] = list(ll_item['p']['LOGGER_ERROR'])
                pp['WARNING'] = list(ll_item['p']['LOGGER_WARNING'])
                pp['OUTPUTS'] = dict(ll_item['p']['OUTPUTS'])
            # --------------------------------------------------------------
            # Manage unexpected errors
            except Exception as e:
                emsgs = ['Unexpected error occured in run {0}'
                         ''.format(priority)]
                for emsg in str(e).split('\n'):
                    emsgs.append('\t' + emsg)
                WLOG(params, 'warning', emsgs)
                pp['ERROR'] = emsgs
                pp['WARNING'] = []
                pp['OUTPUTS'] = dict()
            # --------------------------------------------------------------
            # Manage expected errors
            except SystemExit as e:
                emsgs = ['Expected error occured in run {0}'
                         ''.format(priority)]
                for emsg in str(e).split('\n'):
                    emsgs.append('\t' + emsg)
                WLOG(params, 'warning', emsgs)
                pp['ERROR'] = emsgs
                pp['WARNING'] = []
                pp['OUTPUTS'] = dict()
        # ------------------------------------------------------------------
        # append to return dict
        return_dict[priority] = pp
    # return the output array
    return return_dict


def multi_process(params, runlist, cores):
    # first try to group tasks
    grouplist = group_tasks(params, runlist, cores)
    # start process manager
    manager = Manager()
    return_dict = manager.dict()
    # loop around groups
    for g_it, group in enumerate(grouplist):
        # process storage
        jobs = []
        # log progress
        group_progress(params, g_it, grouplist)
        # loop around sub groups (to be run at same time)
        for r_it, runlist_group in enumerate(group):
            # get args
            args = [params, runlist_group, return_dict, r_it + 1, cores]
            # get parallel process
            process = Process(target=linear_process, args=args)
            process.start()
            jobs.append(process)
        # do not continue until finished
        for proc in jobs:
            proc.join()
    # return return_dict
    return dict(return_dict)




# =============================================================================
# Define worker functions
# =============================================================================
def get_cores(params):
    # get number of cores
    if 'CORES' in params:
        try:
            cores = int(params['CORES'])
        except ValueError as e:
            emsg1 = 'RunList Error: "CORES"={0} must be an integer'
            emsg2 = '\tError{0}: {1}'.format(type(e), e)
            WLOG(params, 'error', [emsg1.format(params['CORES']), emsg2])
            cores = 1
        except Exception as e:
            emsg1 = 'RunList Error: "CORES" must be an integer'
            emsg2 = '\tError{0}: {1}'.format(type(e), e)
            WLOG(params, 'error', [emsg1, emsg2])
            cores = 1
    else:
        cores = 1
    # get number of cores on machine
    cpus = multiprocessing.cpu_count()
    # check that cores is valid
    if cores < 1:
        emsg1 = 'RunList Error: Number of cores must be greater than zero'
        emsg2 = '\tCORES={0}'.format(cores)
        WLOG(params, 'error', [emsg1, emsg2])
    if cores >= cpus:
        emsg1 = 'RunList Error: Number of cores must be less than {0}'
        emsg2 = '\tCORES={0}'.format(cores)
        WLOG(params, 'error', [emsg1.format(cpus), emsg2])

    # return number of cores
    return cores


def group_progress(params, g_it, grouplist):
    # get header text
    header = spirouConfig.Constants.HEADER()
    # get message
    wmsg = ' * GROUP {0}/{1}'.format(g_it + 1, len(grouplist))
    # log
    WLOG(params, 'info', '', colour='magenta')
    WLOG(params, 'info', header, colour='magenta')
    WLOG(params, 'info', wmsg, colour='magenta')
    WLOG(params, 'info', header, colour='magenta')
    WLOG(params, 'info', '', colour='magenta')


def group_tasks(params, runlist, cores):

    # individual runs of the same recipe are independent of each other

    # get all recipe names
    recipenames = []
    for it, run_item in enumerate(runlist):
        recipenames.append(run_item.recipename)
    # storage of groups
    groups = dict()
    group_number = 0
    # loop around runlist
    for it, run_item in enumerate(runlist):
        # get recipe name
        recipe = run_item.recipename
        # if it is the first item must have a new group
        if it == 0:
            groups[group_number] = [run_item]
        else:
            if recipe == recipenames[it - 1]:
                groups[group_number].append(run_item)
            else:
                group_number += 1
                groups[group_number] = [run_item]
    # now we have the groups we can push into the core sub-groups
    out_groups = []

    for groupkey in groups:

        out_group = []
        group = groups[groupkey]

        for it in range(cores):
            sub_group = group[it::cores]
            if len(sub_group) > 0:
                out_group.append(sub_group)

        out_groups.append(out_group)
    # return output groups
    return out_groups


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
