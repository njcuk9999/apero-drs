#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
These functions are used to group arguments for processing

Output of every function should be a list of runs

Each run should be a dictionary of arguments

Example:
    recipe: cal_test.py directory afiles bfiles

    output:  runs = [run1, run2, run3]

             run1 = dict(directory='Dir1', afiles=['file1'], bfiles=['file2'])
             run2 = dict(directory='Dir2', afiles=['file3', 'file4'],
                         bfiles=['file5'])


Created on 2020-12-2020-12-01 11:28

@author: cook
"""
from astropy.table import Table
from collections import OrderedDict
import itertools
import numpy as np
from typing import Any, Dict, List, Union

from apero.core.core import drs_argument
from apero.tools.module.processing import drs_grouping_functions as drsgf


# =============================================================================
# Define variables
# =============================================================================
# get argument class
DrsArgument = drs_argument.DrsArgument
# define complex type argdict
ArgDictType = Union[Dict[str, Table], OrderedDict, None]
RunType = List[Dict[str, Any]]


# =============================================================================
# Define default functions
# =============================================================================
def no_group(args: Dict[str, DrsArgument],
             kwargs: Dict[str, DrsArgument],
             argdict: Dict[str, ArgDictType],
             kwargdict: Dict[str, ArgDictType]) -> RunType:
    # define runs
    run_instances = []
    # ----------------------------------------------------------------------
    # first we need to find the file arguments
    # ----------------------------------------------------------------------
    fout = drsgf.find_file_args(args, kwargs, argdict, kwargdict)
    file_args, non_file_args, alldict = fout
    # define the first file_arg columns
    if len(file_args) != 0:
        raise ValueError('Must have 0 file arguements')
    # ----------------------------------------------------------------------
    # Now figure out the order these arguments should be added
    # ----------------------------------------------------------------------
    arg_order = drsgf.get_argposorder(args, kwargs, argdict, kwargdict)

    # ----------------------------------------------------------------------
    # Make a run instance
    # ----------------------------------------------------------------------
    run_inst = drsgf.RunInstance(args, kwargs)
    run_inst.group_column = None
    run_inst.group = None
    run_instances.append(run_inst)

    # ----------------------------------------------------------------------
    # deal with non-file arguments
    # ----------------------------------------------------------------------
    run_instances = drsgf.get_non_file_args(non_file_args, alldict,
                                            run_instances)
    # ----------------------------------------------------------------------
    # convert in to run list of dictionaries
    # ----------------------------------------------------------------------
    runs = []
    # loop around instances
    for run_inst in run_instances:
        # create run dict
        rundict = OrderedDict()
        # loop around arguments in correct order
        for key in arg_order:
            rundict[key] = run_inst.dictionary[key]
        # add this run dictionary to runs
        runs.append(rundict)
    # return runs
    return runs


def group_individually(args: Dict[str, DrsArgument],
                       kwargs: Dict[str, DrsArgument],
                       argdict: Dict[str, ArgDictType],
                       kwargdict: Dict[str, ArgDictType]) -> RunType:
    """
    Individually group files (with 1 file argument and multiple kinds)

    - for this to work there can only be one file argument among args and kwargs
      otherwise one has to use another way to group files

    :param args: the dictionary of positional DrsArguments for this recipe
    :param kwargs: the dictionary of optional DrsArguments for this recipe
    :param argdict: the dictionary of tables raw files on disk that match the
                    criteria for positional arguments (one key per arg)
    :param kwargdict: the dictionary of tables raw files on disk that match the
                      criteria for optional arguments (one key per arg)
    :return: the run list - where each entry is a dictionary containing the
             arguments to send for each individual run
    """
    # define runs
    run_instances = []
    # ----------------------------------------------------------------------
    # first we need to find the file arguments
    # ----------------------------------------------------------------------
    fout = drsgf.find_file_args(args, kwargs, argdict, kwargdict)
    file_args, non_file_args, alldict = fout
    # define the first file_arg columns
    if len(file_args) != 1:
        raise ValueError('Only 1 file arg allowed')
    else:
        first_arg = file_args[0]
    # ----------------------------------------------------------------------
    # Now figure out the order these arguments should be added
    # ----------------------------------------------------------------------
    arg_order = drsgf.get_argposorder(args, kwargs, argdict, kwargdict)
    # ----------------------------------------------------------------------
    # add all kinds to run instances (for each colname)
    # ----------------------------------------------------------------------
    # get the drs files in file arg 0
    kinds = alldict[first_arg].keys()
    # need to loop around drsfiles in file arg 1
    for kind in kinds:
        # get arg 0 table
        table0 = alldict[first_arg][kind]
        # loop around these unique entries and add to groups
        for row in range(len(table0)):
            # need to create a run instance here
            run_inst = drsgf.RunInstance(args, kwargs)
            # set group identifier
            run_inst.group_column = 'individual'
            run_inst.group = row
            # in each dictionary we will have arguments
            run_inst.dictionary[first_arg] = [table0['OUT'][row]]
            # add run_instance to list
            run_instances.append(run_inst)
    # ----------------------------------------------------------------------
    # deal with non-file arguments
    # ----------------------------------------------------------------------
    run_instances = drsgf.get_non_file_args(non_file_args, alldict,
                                            run_instances)
    # ----------------------------------------------------------------------
    # convert in to run list of dictionaries
    # ----------------------------------------------------------------------
    runs = []
    # loop around instances
    for run_inst in run_instances:
        # create run dict
        rundict = OrderedDict()
        # loop around arguments in correct order
        for key in arg_order:
            rundict[key] = run_inst.dictionary[key]
        # add this run dictionary to runs
        runs.append(rundict)
    # return runs
    return runs


def dir_group_1_arg_n_kinds(args: Dict[str, DrsArgument],
                            kwargs: Dict[str, DrsArgument],
                            argdict: Dict[str, ArgDictType],
                            kwargdict: Dict[str, ArgDictType]) -> RunType:
    """
    Group by column "DIRNAME" when we have one file argument and multiple
    drsfile kinds for that file argument

    :param args: the dictionary of positional DrsArguments for this recipe
    :param kwargs: the dictionary of optional DrsArguments for this recipe
    :param argdict: the dictionary of tables raw files on disk that match the
                    criteria for positional arguments (one key per arg)
    :param kwargdict: the dictionary of tables raw files on disk that match the
                      criteria for optional arguments (one key per arg)
    :return: the run list - where each entry is a dictionary containing the
             arguments to send for each individual run
    """
    # define runs
    run_instances = []
    # define directory column name
    columnname = 'DIRNAME'
    # ----------------------------------------------------------------------
    # first we need to find the file arguments
    # ----------------------------------------------------------------------
    fout = drsgf.find_file_args(args, kwargs, argdict, kwargdict)
    file_args, non_file_args, alldict = fout
    # define the first file_arg columns
    if len(file_args) != 1:
        raise ValueError('Only 1 file arg allowed')
    else:
        first_arg = file_args[0]
    # ----------------------------------------------------------------------
    # Now figure out the order these arguments should be added
    # ----------------------------------------------------------------------
    arg_order = drsgf.get_argposorder(args, kwargs, argdict, kwargdict)
    # ----------------------------------------------------------------------
    # add all kinds to run instances (for each colname)
    # ----------------------------------------------------------------------
    # get the drs files in file arg 0
    kinds = alldict[first_arg].keys()
    # need to loop around drsfiles in file arg 1
    for kind in kinds:
        # get arg 0 table
        table0 = alldict[first_arg][kind]
        # get unique column entries
        unique_entries = np.unique(table0[columnname])
        # loop around these unique entries and add to groups
        for entry in unique_entries:
            # need to create a run instance here
            run_inst = drsgf.RunInstance(args, kwargs)
            # set group identifier
            run_inst.group_column = columnname
            run_inst.group = entry
            # create a list of all out files
            colmask = table0[columnname] == entry
            # in each dictionary we will have arguments
            run_inst.dictionary[first_arg] = list(table0['OUT'][colmask])
            # add run_instance to list
            run_instances.append(run_inst)
    # ----------------------------------------------------------------------
    # deal with non-file arguments
    # ----------------------------------------------------------------------
    run_instances = drsgf.get_non_file_args(non_file_args, alldict,
                                            run_instances)
    # ----------------------------------------------------------------------
    # convert in to run list of dictionaries
    # ----------------------------------------------------------------------
    runs = []
    # loop around instances
    for run_inst in run_instances:
        # create run dict
        rundict = OrderedDict()
        # loop around arguments in correct order
        for key in arg_order:
            rundict[key] = run_inst.dictionary[key]
        # add this run dictionary to runs
        runs.append(rundict)
    # return runs
    return runs


def dir_group_n_args_1_kind(args: Dict[str, DrsArgument],
                            kwargs: Dict[str, DrsArgument],
                            argdict: Dict[str, ArgDictType],
                            kwargdict: Dict[str, ArgDictType]) -> RunType:
    """
    Group by column "DIRNAME" when we have multipe file argument and one
    drsfile kind for each file argument

    :param args: the dictionary of positional DrsArguments for this recipe
    :param kwargs: the dictionary of optional DrsArguments for this recipe
    :param argdict: the dictionary of tables raw files on disk that match the
                    criteria for positional arguments (one key per arg)
    :param kwargdict: the dictionary of tables raw files on disk that match the
                      criteria for optional arguments (one key per arg)
    :return: the run list - where each entry is a dictionary containing the
             arguments to send for each individual run
    """
    # define runs
    run_instances = []
    # define directory column name
    columnname = 'DIRNAME'
    # ----------------------------------------------------------------------
    # first we need to find the file arguments
    # ----------------------------------------------------------------------
    fout = drsgf.find_file_args(args, kwargs, argdict, kwargdict)
    file_args, non_file_args, alldict = fout
    # define the first file_arg columns
    if len(file_args) == 0:
        raise ValueError('Must have file arguements')
    else:
        first_arg = file_args[0]
    # ----------------------------------------------------------------------
    # Now figure out the order these arguments should be added
    # ----------------------------------------------------------------------
    arg_order = drsgf.get_argposorder(args, kwargs, argdict, kwargdict)
    # ----------------------------------------------------------------------
    # for first argument
    # ----------------------------------------------------------------------
    # find kind
    kind = alldict[first_arg].keys()[0]
    # get arg 0 table
    table0 = alldict[first_arg][kind]
    # get unique column entries
    unique_entries = np.unique(table0[columnname])
    # loop around these unique entries and add to groups
    for entry in unique_entries:
        # need to create a run instance here
        run_inst = drsgf.RunInstance(args, kwargs)
        # set group identifier
        run_inst.group_column = columnname
        run_inst.group = entry
        # create a list of all out files
        colmask = table0[columnname] == entry
        # in each dictionary we will have arguments
        run_inst.dictionary[first_arg] = list(table0['OUT'][colmask])
        # add run_instance to list
        run_instances.append(run_inst)
    # ----------------------------------------------------------------------
    # deal with other file arguments
    # ----------------------------------------------------------------------
    for argname in file_args[1:]:
        # find kind
        kind = alldict[argname].keys()[0]
        # get arg table
        table1 = alldict[argname][kind]
        # loop around runs
        for run_inst in run_instances:
            # create a list of all out files
            colmask = table1[columnname] == run_inst.group
            # in each dictionary we will have arguments
            run_inst.dictionary[argname] = list(table1['OUT'][colmask])
    # ----------------------------------------------------------------------
    # deal with non-file arguments
    # ----------------------------------------------------------------------
    run_instances = drsgf.get_non_file_args(non_file_args, alldict,
                                            run_instances)
    # ----------------------------------------------------------------------
    # convert in to run list of dictionaries
    # ----------------------------------------------------------------------
    runs = []
    # loop around instances
    for run_inst in run_instances:
        # create run dict
        rundict = OrderedDict()
        # loop around arguments in correct order
        for key in arg_order:
            rundict[key] = run_inst.dictionary[key]
        # add this run dictionary to runs
        runs.append(rundict)
    # return runs
    return runs


def group_by_dirname(args: Dict[str, DrsArgument],
                     kwargs: Dict[str, DrsArgument],
                     argdict: Dict[str, ArgDictType],
                     kwargdict: Dict[str, ArgDictType],
                     dirname: Union[str, None] = None) -> RunType:
    """
    Group by column "DIRNAME" when we have multipe file argument and multiple
    drsfile kinds for each file argument

    :param args: the dictionary of positional DrsArguments for this recipe
    :param kwargs: the dictionary of optional DrsArguments for this recipe
    :param argdict: the dictionary of tables raw files on disk that match the
                    criteria for positional arguments (one key per arg)
    :param kwargdict: the dictionary of tables raw files on disk that match the
                      criteria for optional arguments (one key per arg)
    :return: the run list - where each entry is a dictionary containing the
             arguments to send for each individual run
    """
    # define runs
    run_instances = []
    # define directory column name
    columnname = 'DIRNAME'
    # ----------------------------------------------------------------------
    # first we need to find the file arguments
    # ----------------------------------------------------------------------
    fout = drsgf.find_file_args(args, kwargs, argdict, kwargdict)
    file_args, non_file_args, alldict = fout
    # define the first file_arg columns
    if len(file_args) == 0:
        raise ValueError('Must have file arguements')
    else:
        first_arg = file_args[0]
    # ----------------------------------------------------------------------
    # Now figure out the order these arguments should be added
    # ----------------------------------------------------------------------
    arg_order = drsgf.get_argposorder(args, kwargs, argdict, kwargdict)
    # ----------------------------------------------------------------------
    # get kind combinations
    # ----------------------------------------------------------------------
    # get all drs file kinds for all file arguments
    raw_kinds = []
    for file_arg in file_args:
        raw_kinds.append(alldict[file_arg].keys())
    # get all combinations of kinds
    kinds = list(itertools.product(*raw_kinds))

    # ----------------------------------------------------------------------
    # deal with each combination of kinds
    #    - loop around unique entries
    #    - loop around each argument
    #    - fill in run instance
    # ----------------------------------------------------------------------
    # loop around arguments
    for f_it, fargs in enumerate(kinds):
        # get arg 0 table
        table0 = alldict[first_arg][fargs[0]]
        # get unique column entries
        unique_entries = np.unique(table0[columnname])
        # loop around these unique entries and add to groups
        for entry in unique_entries:
            # valid
            valid = True
            # need to create a run instance here
            run_inst = drsgf.RunInstance(args, kwargs)
            # loop around arguments
            for k_it, farg in enumerate(fargs):
                # get the argument name
                argname = file_args[k_it]
                # get this arguments table
                table1 = alldict[argname][farg]
                # set group identifier
                run_inst.group_column = columnname
                run_inst.group = entry
                # create a list of all out files
                colmask = table1[columnname] == entry
                # get list of filenames
                filenames = list(table1['OUT'][colmask])
                # check we have entries
                if len(filenames) == 0:
                    valid = False
                # in each dictionary we will have arguments
                run_inst.dictionary[argname] = filenames
            # add to run instances
            if valid:
                run_instances.append(run_inst)

    # ----------------------------------------------------------------------
    # deal with non-file arguments
    # ----------------------------------------------------------------------
    run_instances = drsgf.get_non_file_args(non_file_args, alldict,
                                            run_instances)
    # ----------------------------------------------------------------------
    # convert in to run list of dictionaries
    # ----------------------------------------------------------------------
    runs = []
    # loop around instances
    for run_inst in run_instances:
        # create run dict
        rundict = OrderedDict()
        # loop around arguments in correct order
        for key in arg_order:
            rundict[key] = run_inst.dictionary[key]
        # add this run dictionary to runs
        runs.append(rundict)
    # return runs
    return runs


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
