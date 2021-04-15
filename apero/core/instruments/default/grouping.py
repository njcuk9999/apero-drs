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
from typing import Any, Dict, List, Tuple, Union

from apero.core.core import drs_argument
from apero.core.core import drs_log
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
def no_group(rargs: Dict[str, DrsArgument],
             rkwargs: Dict[str, DrsArgument],
             argdict: Dict[str, ArgDictType],
             kwargdict: Dict[str, ArgDictType],
             **kwargs) -> RunType:
    """
    Use this for all instances where we do not have a file argument
    if directory argument is required it is set to the 'master' kwarg
    i.e. master='MY_DIRNAME'

    :param rargs:
    :param rkwargs:
    :param argdict:
    :param kwargdict:
    :param kwargs:
    :return:
    """
    # group column
    group_column = kwargs.get('group_column', None)
    master_value = kwargs.get('master', None)
    # define runs
    run_instances = []
    # ----------------------------------------------------------------------
    # first we need to find the file arguments
    # ----------------------------------------------------------------------
    fout = drsgf.find_file_args(rargs, rkwargs, argdict, kwargdict)
    file_args, non_file_args, alldict = fout
    # define the first file_arg columns
    if len(file_args) != 0:
        raise ValueError('Must have 0 file arguements')
    # ----------------------------------------------------------------------
    # Now figure out the order these arguments should be added
    # ----------------------------------------------------------------------
    arg_order = drsgf.get_argposorder(rargs, rkwargs, argdict, kwargdict)

    # ----------------------------------------------------------------------
    # Make a run instance
    # ----------------------------------------------------------------------
    run_inst = drsgf.RunInstance(rargs, rkwargs)
    run_inst.group_column = group_column
    run_inst.group = master_value
    run_instances.append(run_inst)
    # print statement
    pmsg = '\t\tProcessing I run {0}'.format(0)
    drs_log.Printer(None, None, pmsg)
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


def group_individually(rargs: Dict[str, DrsArgument],
                       rkwargs: Dict[str, DrsArgument],
                       argdict: Dict[str, ArgDictType],
                       kwargdict: Dict[str, ArgDictType],
                       **kwargs) -> RunType:
    """
    Individually group files (with 1 file argument and multiple kinds)

    - for this to work there can only be one file argument among args and kwargs
      otherwise one has to use another way to group files

    :param rargs: the dictionary of positional DrsArguments for this recipe
    :param rkwargs: the dictionary of optional DrsArguments for this recipe
    :param argdict: the dictionary of tables raw files on disk that match the
                    criteria for positional arguments (one key per arg)
    :param kwargdict: the dictionary of tables raw files on disk that match the
                      criteria for optional arguments (one key per arg)
    :return: the run list - where each entry is a dictionary containing the
             arguments to send for each individual run
    """
    # group column
    group_column = kwargs.get('group_column', None)
    # define runs
    run_instances = []
    # ----------------------------------------------------------------------
    # first we need to find the file arguments
    # ----------------------------------------------------------------------
    fout = drsgf.find_file_args(rargs, rkwargs, argdict, kwargdict)
    file_args, non_file_args, alldict = fout
    # define the first file_arg columns
    if len(file_args) != 1:
        raise ValueError('Only 1 file arg allowed')
    else:
        first_arg = file_args[0]
    # ----------------------------------------------------------------------
    # Now figure out the order these arguments should be added
    # ----------------------------------------------------------------------
    arg_order = drsgf.get_argposorder(rargs, rkwargs, argdict, kwargdict)
    # ----------------------------------------------------------------------
    # add all kinds to run instances (for each colname)
    # ----------------------------------------------------------------------
    # get the drs files in file arg 0
    kinds = alldict[first_arg].keys()
    # count number of runs
    run_count = 0
    # need to loop around drsfiles in file arg 1
    for kind in kinds:
        # get arg 0 table
        table0 = alldict[first_arg][kind]
        # deal with no table
        if table0 is None:
            continue
        # deal with no table
        if len(table0) == 0:
            continue
        # loop around these unique entries and add to groups
        for row in range(len(table0)):
            # need to create a run instance here
            run_inst = drsgf.RunInstance(rargs, rkwargs)
            # set group identifier
            run_inst.group_column = group_column
            run_inst.group = str(table0[group_column][row])
            # in each dictionary we will have arguments
            run_inst.dictionary[first_arg] = [table0['OUT'][row]]
            # print statement
            pmsg = '\t\tProcessing I run {0}'.format(run_count)
            drs_log.Printer(None, None, pmsg)
            # add to run count
            run_count += 1
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


def dir_group_1_arg_n_kinds(rargs: Dict[str, DrsArgument],
                            rkwargs: Dict[str, DrsArgument],
                            argdict: Dict[str, ArgDictType],
                            kwargdict: Dict[str, ArgDictType],
                            **kwargs) -> RunType:
    """
    Group by column "DIRNAME" when we have one file argument and multiple
    drsfile kinds for that file argument

    :param rargs: the dictionary of positional DrsArguments for this recipe
    :param rkwargs: the dictionary of optional DrsArguments for this recipe
    :param argdict: the dictionary of tables raw files on disk that match the
                    criteria for positional arguments (one key per arg)
    :param kwargdict: the dictionary of tables raw files on disk that match the
                      criteria for optional arguments (one key per arg)
    :return: the run list - where each entry is a dictionary containing the
             arguments to send for each individual run
    """
    # kwargs not used for this function
    _ = kwargs
    # define runs
    run_instances = []
    # group column
    group_column = kwargs.get('group_column', None)
    # ----------------------------------------------------------------------
    # first we need to find the file arguments
    # ----------------------------------------------------------------------
    fout = drsgf.find_file_args(rargs, rkwargs, argdict, kwargdict)
    file_args, non_file_args, alldict = fout
    # define the first file_arg columns
    if len(file_args) != 1:
        raise ValueError('Only 1 file arg allowed')
    else:
        first_arg = file_args[0]
    # ----------------------------------------------------------------------
    # Now figure out the order these arguments should be added
    # ----------------------------------------------------------------------
    arg_order = drsgf.get_argposorder(rargs, rkwargs, argdict, kwargdict)
    # ----------------------------------------------------------------------
    # add all kinds to run instances (for each colname)
    # ----------------------------------------------------------------------
    # get the drs files in file arg 0
    kinds = alldict[first_arg].keys()
    # count number of runs
    run_count = 0
    # need to loop around drsfiles in file arg 1
    for kind in kinds:
        # get arg 0 table
        table0 = alldict[first_arg][kind]
        # deal with no table
        if table0 is None:
            continue
        # deal with no table
        if len(table0) == 0:
            continue
        # get unique column entries
        unique_entries = np.unique(table0[group_column])
        # loop around these unique entries and add to groups
        for entry in unique_entries:
            # need to create a run instance here
            run_inst = drsgf.RunInstance(rargs, rkwargs)
            # set group identifier
            run_inst.group_column = group_column
            run_inst.group = entry
            # create a list of all out files
            colmask = table0[group_column] == entry
            # in each dictionary we will have arguments
            run_inst.dictionary[first_arg] = list(table0['OUT'][colmask])
            # print statement
            pmsg = '\t\tProcessing I run {0}'.format(run_count)
            drs_log.Printer(None, None, pmsg)
            # add to run count
            run_count += 1
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


def dir_group_n_args_1_kind(rargs: Dict[str, DrsArgument],
                            rkwargs: Dict[str, DrsArgument],
                            argdict: Dict[str, ArgDictType],
                            kwargdict: Dict[str, ArgDictType],
                            **kwargs) -> RunType:
    """
    Group by column "DIRNAME" when we have multiple file argument and one
    drsfile kind for each file argument

    :param rargs: the dictionary of positional DrsArguments for this recipe
    :param rkwargs: the dictionary of optional DrsArguments for this recipe
    :param argdict: the dictionary of tables raw files on disk that match the
                    criteria for positional arguments (one key per arg)
    :param kwargdict: the dictionary of tables raw files on disk that match the
                      criteria for optional arguments (one key per arg)
    :return: the run list - where each entry is a dictionary containing the
             arguments to send for each individual run
    """
    # kwargs not used for this function
    _ = kwargs
    # define runs
    run_instances = []
    # group column
    group_column = kwargs.get('group_column', None)
    # ----------------------------------------------------------------------
    # first we need to find the file arguments
    # ----------------------------------------------------------------------
    fout = drsgf.find_file_args(rargs, rkwargs, argdict, kwargdict)
    file_args, non_file_args, alldict = fout
    # define the first file_arg columns
    if len(file_args) == 0:
        raise ValueError('Must have file arguements')
    else:
        first_arg = file_args[0]
    # ----------------------------------------------------------------------
    # Now figure out the order these arguments should be added
    # ----------------------------------------------------------------------
    arg_order = drsgf.get_argposorder(rargs, rkwargs, argdict, kwargdict)
    # ----------------------------------------------------------------------
    # for first argument
    # ----------------------------------------------------------------------
    # find kind
    kind = alldict[first_arg].keys()[0]
    # get arg 0 table
    table0 = alldict[first_arg][kind]
    # deal with no table
    if table0 is None:
        return []
    # deal with no table
    if len(table0) == 0:
        return []
    # get unique column entries
    unique_entries = np.unique(table0[group_column])
    # count number of runs
    run_count = 0
    # loop around these unique entries and add to groups
    for entry in unique_entries:
        # need to create a run instance here
        run_inst = drsgf.RunInstance(rargs, rkwargs)
        # set group identifier
        run_inst.group_column = group_column
        run_inst.group = entry
        # create a list of all out files
        colmask = table0[group_column] == entry
        # in each dictionary we will have arguments
        run_inst.dictionary[first_arg] = list(table0['OUT'][colmask])
        # print statement
        pmsg = '\t\tProcessing I run {0}'.format(run_count)
        drs_log.Printer(None, None, pmsg)
        # add to run count
        run_count += 1
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
            colmask = table1[group_column] == run_inst.group
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


def group_by_dirname(rargs: Dict[str, DrsArgument],
                     rkwargs: Dict[str, DrsArgument],
                     argdict: Dict[str, ArgDictType],
                     kwargdict: Dict[str, ArgDictType],
                     **kwargs) -> RunType:
    """
    Group by column "DIRNAME" when we have multipe file argument and multiple
    drsfile kinds for each file argument

    :param rargs: the dictionary of positional DrsArguments for this recipe
    :param rkwargs: the dictionary of optional DrsArguments for this recipe
    :param argdict: the dictionary of tables raw files on disk that match the
                    criteria for positional arguments (one key per arg)
    :param kwargdict: the dictionary of tables raw files on disk that match the
                      criteria for optional arguments (one key per arg)
    :return: the run list - where each entry is a dictionary containing the
             arguments to send for each individual run
    """
    # define runs
    run_instances = []
    # group column
    group_column = kwargs.get('group_column', None)
    group_filter = kwargs.get('group_filter', None)
    # ----------------------------------------------------------------------
    # first we need to find the file arguments
    # ----------------------------------------------------------------------
    fout = drsgf.find_file_args(rargs, rkwargs, argdict, kwargdict)
    file_args, non_file_args, alldict = fout
    # define the first file_arg columns
    if len(file_args) == 0:
        raise ValueError('Must have file arguements')
    else:
        first_arg = file_args[0]
    # ----------------------------------------------------------------------
    # Now figure out the order these arguments should be added
    # ----------------------------------------------------------------------
    arg_order = drsgf.get_argposorder(rargs, rkwargs, argdict, kwargdict)
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
    run_count = 0
    # loop around arguments
    for f_it, fargs in enumerate(kinds):
        # get arg 0 table
        table0 = alldict[first_arg][fargs[0]]
        # deal with no table
        if table0 is None:
            continue
        # deal with no table
        if len(table0) == 0:
            continue
        # create filter masks
        if group_filter is not None:
            # get the filter groups and update the sort on the table
            table0, filtermasks = group_filter(table0)
        else:
            # else we just have one mask and it is all Trues --> i.e. no
            #   filter mask
            filtermasks = [np.ones(len(table0)).astype(bool)]

        # get unique column entries
        unique_entries = np.unique(table0[group_column])
        # loop around these unique entries and add to groups
        for entry in unique_entries:
            # loop around filter groups
            for filtermask in filtermasks:
                # valid
                valid = True
                # need to create a run instance here
                run_inst = drsgf.RunInstance(rargs, rkwargs)
                # loop around arguments
                for k_it, farg in enumerate(fargs):
                    # get the argument name
                    argname = file_args[k_it]
                    # get this arguments table
                    table1 = alldict[argname][farg]
                    # deal with no table
                    if table1 is None:
                        valid = False
                        continue
                    # deal with no table
                    if len(table1) == 0:
                        valid = False
                        continue
                    # set group identifier
                    run_inst.group_column = group_column
                    run_inst.group = entry
                    # create a mask of all files for this group_column
                    colmask = table1[group_column] == entry
                    # add the filter group mask
                    colmask &= filtermask
                    # get list of filenames
                    filenames = list(table1['OUT'][colmask])
                    # check we have entries
                    if len(filenames) == 0:
                        valid = False
                        continue
                    # in each dictionary we will have arguments
                    run_inst.dictionary[argname] = filenames
                # add to run instances
                if valid:
                    # print statement
                    pmsg = '\t\tProcessing I run {0}'.format(run_count)
                    drs_log.Printer(None, None, pmsg)
                    # add to run count
                    run_count += 1
                    # add to run_instances
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



def group_by_polar_sequence(rargs: Dict[str, DrsArgument],
                            rkwargs: Dict[str, DrsArgument],
                            argdict: Dict[str, ArgDictType],
                            kwargdict: Dict[str, ArgDictType],
                            **kwargs) -> RunType:
    """
    Group by directory name but add a group by sequence number
    (controlled by columns KW_NEXP and KW_CMPLTEXP in index database)

    essentially a group by directory but also grouped by polar sequence

    :param rargs: the dictionary of positional DrsArguments for this recipe
    :param rkwargs: the dictionary of optional DrsArguments for this recipe
    :param argdict: the dictionary of tables raw files on disk that match the
                    criteria for positional arguments (one key per arg)
    :param kwargdict: the dictionary of tables raw files on disk that match the
                      criteria for optional arguments (one key per arg)

    :return: the run list - where each entry is a dictionary containing the
             arguments to send for each individual run
    """
    # -------------------------------------------------------------------------
    # need to define a polar filter (inputs are the table out put is a set
    #   of masks - one for each group)
    def polar_filter(table: Table
                     ) -> Tuple[Table, List[np.ndarray]]:
        """
        Custom filter for polar files - can only use a table created from the
        index database as inputs and must return a list of masks (each mask
        is the same length as the table)

        :param table: astropy.table.Table, the index database table

        :return: list of masks, each mask is a group of files that match a
                 polar sequence, each mask should be True where a file is part
                 of that group or False it is not - each mask should therefore
                 be the length of the input astropy table
        """
        # define some specific columns for polar recipe - these will need to
        #   change if column definitions change
        path_col = 'ABSPATH'
        obs_dir_col = 'OBS_DIR'
        num_col = 'KW_NEXP'
        seq_col = 'KW_CMPLTEXP'
        # sort by filename (assume filename should put files in order)
        sort = np.argsort(table[path_col])
        table1 = table[sort]

        masks = []
        # make our zero group mask
        zero_mask = np.zeros(len(table1)).astype(bool)
        # start a counter
        obs_dir = None
        current_mask = np.array(zero_mask)
        # loop around each row and group by KW_CMPLTEXP
        for row in range(len(table1)):
            # set the current value to this sequence's value
            current = table1[seq_col][row]
            # different observation directories cannot have same file
            if table1[obs_dir_col][row] != obs_dir:
                # if we have a new group copy the mask
                current_mask = np.array(zero_mask)
                # add this row to current group
                current_mask[row] = True
                # set group obs dir
                obs_dir = table1[obs_dir_col][row]
            # append to current file if current number is less than
            #   total number in sequence
            elif current < table1[num_col][row]:
                # add this row to current group
                current_mask[row] = True
                # set group obs dir
                obs_dir = table1[obs_dir_col][row]
            # if we have reached the end of a group append the masks
            #   and set the current mask to zero and reset the current number
            #   to zero
            elif current == table1[num_col][row]:
                # add this row to current group
                current_mask[row] = True
                # append group to masks
                masks.append(current_mask)
                # if we have a new group copy the mask
                current_mask = np.array(zero_mask)
                # set group obs dir
                obs_dir = table1[obs_dir_col][row]
            else:
                # append group to masks
                masks.append(current_mask)
                # if we have a new group copy the mask
                current_mask = np.array(zero_mask)

        # return list of masks
        return table1, masks

    # -------------------------------------------------------------------------
    # update kwargs to have a group filter (default is None) this must be
    #  a function with a "table" input and a mask return
    kwargs['group_filter'] = polar_filter
    # -------------------------------------------------------------------------
    # generate the groups
    runs = group_by_dirname(rargs, rkwargs, argdict, kwargdict,
                            **kwargs)
    # -------------------------------------------------------------------------
    # return the groups
    return runs


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
