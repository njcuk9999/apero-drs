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
import itertools
from collections import OrderedDict
from typing import Any, Dict, Iterable, List, Tuple, Union

import numpy as np
from astropy.table import Table

from apero.base import base
from apero.core.core import drs_argument
from apero.core.core import drs_exceptions
from apero.core.core import drs_log
from apero.tools.module.processing import drs_grouping_functions as drsgf

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'drs_utils.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get display func
display_func = drs_log.display_func
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
    if directory argument is required it is set to the 'ref' kwarg
    i.e. ref='MY_DIRNAME'

    :param rargs: the dictionary of positional DrsArguments for this recipe
    :param rkwargs: the dictionary of optional DrsArguments for this recipe
    :param argdict: the dictionary of tables raw files on disk that match the
                    criteria for positional arguments (one key per arg)
    :param kwargdict: the dictionary of tables raw files on disk that match the
                      criteria for optional arguments (one key per arg)
    :param kwargs: dict, all other arguments passed to grouping function

    :return: the run list - where each entry is a dictionary containing the
             arguments to send for each individual run
    """
    # set function name
    # _ = display_func('no_group', __NAME__)
    # group column
    group_column = kwargs.get('group_column', None)
    ref_value = kwargs.get('ref', None)
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
    run_inst.group = ref_value
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
    :param kwargs: dict, all other arguments passed to grouping function

    :return: the run list - where each entry is a dictionary containing the
             arguments to send for each individual run
    """
    # set function name
    # _ = display_func('group_individually', __NAME__)
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
    drsfile_group = alldict[first_arg].keys()
    # count number of runs
    run_count = 0
    # need to loop around drsfiles in file arg 1
    for drsfiletype in drsfile_group:
        # get arg 0 table
        table0 = _get_raw_table(alldict, first_arg, drsfiletype)
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
    :param kwargs: dict, all other arguments passed to grouping function

    :return: the run list - where each entry is a dictionary containing the
             arguments to send for each individual run
    """
    # set function name
    func_name = display_func('group_by_dirname', __NAME__)
    # define runs
    run_instances = []
    # group column
    group_column = kwargs.get('group_column', None)
    group_filter = kwargs.get('group_filter', None)
    limit = kwargs.get('limit', None)
    # ----------------------------------------------------------------------
    # first we need to find the file arguments
    # ----------------------------------------------------------------------
    fout = drsgf.find_file_args(rargs, rkwargs, argdict, kwargdict)
    file_args, non_file_args, alldict = fout
    # define the first file_arg columns
    if len(file_args) == 0:
        raise ValueError('Must have file arguments')
    else:
        first_arg = file_args[0]
    # ----------------------------------------------------------------------
    # Now figure out the order these arguments should be added
    # ----------------------------------------------------------------------
    arg_order = drsgf.get_argposorder(rargs, rkwargs, argdict, kwargdict)
    # ----------------------------------------------------------------------
    # get drs kind combinations
    # ----------------------------------------------------------------------
    # here we link file arguments drs file kinds together
    #  i.e. if
    #  arg1 has drs file types: ['DARK_DARK_INT', 'DARK_DARK_TEL']
    #  arg2 has drs file types: ['FLAT_FLAT']
    #
    #   drsfile_groups =  [['DARK_DARK_INT', 'FLAT_FLAT'],
    #                      ['DARK_DARK_TEL', 'FLAT_FLAT']]
    #
    #  each element of drsfile_groups should be the length of file arguments
    raw_drsfile_groups = []
    for file_arg in file_args:
        raw_drsfile_groups.append(alldict[file_arg].keys())
    # get all combinations of drs files types
    drsfile_groups = list(itertools.product(*raw_drsfile_groups))
    # ----------------------------------------------------------------------
    # deal with each combination of kinds
    #    - loop around unique entries
    #    - loop around each argument
    #    - fill in run instance
    # ----------------------------------------------------------------------
    run_count = 0
    # loop around drs file groups (each file group has 1 drs file type for
    #    each file argument)
    for groupnum, drsfile_group in enumerate(drsfile_groups):
        # get arg 0 table
        table0 = _get_raw_table(alldict, first_arg, drsfile_group[0])
        # ---------------------------------------------------------------------
        # deal with no table
        if table0 is None:
            continue
        # deal with no table
        if len(table0) == 0:
            continue
        # ---------------------------------------------------------------------
        # get filter only for first arg
        #    - more than one filter group argument means you would need a way
        #      to match one set of arguments with another (this is difficult)
        # ---------------------------------------------------------------------
        # create filter masks - only if we have one file argument
        if group_filter is not None and len(file_args) == 1:
            table0, filtermasks = group_filter(table0)
            # must update alldict with table0 (because we use alldict below)
            alldict[first_arg][drsfile_group[0]] = table0
        # if we have a group filter defined and more than 1 file argument we
        #   have to crash - we can't deal with this
        elif group_filter is not None:
            # raise exception: Cannot use group filter with more than
            #                  1 file argument
            raise drs_exceptions.DrsCodedException('00-006-00025', 'error',
                                                   targs=[func_name],
                                                   func_name=func_name)
        else:
            # else we just have one mask and it is all Trues --> i.e. no
            #   filter mask
            filtermasks = [np.ones(len(table0)).astype(bool)]
        # ---------------------------------------------------------------------
        # get unique column entries
        #  - this is the highest level of grouping - no files can share
        #    different "group_column" value - they must be the same
        #    (i.e. no file group should share different observation directories)
        unique_entries = np.unique(table0[group_column])
        # loop around these unique entries and add to groups
        for entry in unique_entries:
            # loop around filter groups
            #      (only not all Trues if len(file_args) == 1)
            #   note these filter masks are combined with the group column
            #       so each filtermask must not cross different "group column"
            #       values
            for filtermask in filtermasks:
                # valid
                valid = True
                # need to create a run instance here
                run_inst = drsgf.RunInstance(rargs, rkwargs)
                # -------------------------------------------------------------
                # loop around the file arguments (a drsfile group should have
                #   the exact number of elements as the number of file
                #   arguments)
                for argpos, drsfiletype in enumerate(drsfile_group):
                    # get the file argument name
                    argname = file_args[argpos]
                    # get this arguments table - alldict[argname][drsfiletype]
                    #   may be a astropy.table.Row --> recast into Table
                    #   slower - but other lines later break when dealing with
                    #   a row
                    rawtab = alldict[argname][drsfiletype]
                    if isinstance(rawtab, Table.Row):
                        table1 = Table(rawtab)
                    elif isinstance(rawtab, Table):
                        table1 = rawtab
                    elif rawtab is None:
                        table1 = None
                    else:
                        # raise error: alldict[{0}][{1}] is not a valid
                        #     astropy table
                        eargs = [argname, drsfiletype, func_name]
                        ekwargs = dict(targs=eargs, func_name=func_name)
                        raise drs_exceptions.DrsCodedException('00-006-00024',
                                                               'error',
                                                               **ekwargs)
                    # deal with no table --> no files for this argument
                    if table1 is None:
                        valid = False
                        continue
                    # deal with no table --> no files for this argument
                    if len(table1) == 0:
                        valid = False
                        continue
                    # set group identifier --> this is the group that
                    #    split this value initially (not including the filter
                    #    mask)
                    run_inst.group_column = group_column
                    # this is the unique value of the group column - this cannot
                    #   be different for files in the same group
                    run_inst.group = entry
                    # create a mask of all files for this group_column
                    colmask = table1[group_column] == entry
                    # add the filter group mask (only for first argument)
                    #   again this can only be applied to the first file
                    #   argument - we currently cannot filter
                    if argpos == 0:
                        colmask &= filtermask
                    # get list of filenames
                    filenames = list(table1['OUT'][colmask])
                    # check we have entries
                    if len(filenames) == 0:
                        valid = False
                        continue
                    # # if we have a group limit only accept the last N files
                    if limit is not None:
                        if len(filenames) >= limit:
                            filenames = filenames[-limit:]
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
    :param kwargs: dict, all other arguments passed to grouping function

    :return: the run list - where each entry is a dictionary containing the
             arguments to send for each individual run
    """
    # set function name
    # _ = display_func('group_by_polar_sequence', __NAME__)

    # -------------------------------------------------------------------------
    # need to define a polar filter (inputs are the table out put is a set
    #   of masks - one for each group)
    def polar_filter(table: Table
                     ) -> Tuple[Table, List[np.ndarray]]:
        """
        Custom filter for polar files - can only use a table created from the
        index database as inputs and must return a list of masks (each mask
        is the same length as the table)

        :param table: astropy.table - the inputted "table" sorted to match
                      masks

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
        obj_col = 'KW_OBJNAME'
        # sort by filename (assume filename should put files in order)
        sort = np.argsort(table[path_col])
        table1 = Table(table[sort])
        # remove masked values (if table has masks)
        if hasattr(table1, 'mask'):
            seq_mask = ~np.array(table1.mask[seq_col])
            num_mask = ~np.array(table1.mask[num_col])
            # mask table1
            table1 = table1[seq_mask & num_mask]
        # mask num col and seq col and keep only rows with numbers
        seq_mask = _is_numeric(table1[seq_col])
        num_mask = _is_numeric(table1[num_col])
        # mask table1
        table1 = table1[seq_mask & num_mask]
        # set up list if masks
        masks = []
        # get correct columns (in correct sorted order)
        seq_arr = np.array(table1[seq_col]).astype(int)
        num_arr = np.array(table1[num_col]).astype(int)
        obs_dir_arr = np.array(table1[obs_dir_col])
        obj_name_arr = np.array(table1[obj_col])
        # make our zero group mask
        zero_mask = np.zeros(len(table1)).astype(bool)
        # start a counter
        obs_dir = None
        obj_name = None
        current_mask = np.array(zero_mask)
        current_seqs = []
        # loop around each row and group by KW_CMPLTEXP
        for row in range(len(table1)):
            # set the current value to this sequence's value
            current = seq_arr[row]
            # different observations cannot have different object names
            # ---> start a new group
            if obj_name_arr[row] != obj_name:
                # if we have a new group copy the mask
                current_mask = np.array(zero_mask)
                # reset the current sequence present for this group
                current_seqs = []
                # add this row to current group
                current_mask[row] = True
                # set current group obs dir
                obs_dir = str(obs_dir_arr[row])
                # set current object name
                obj_name = str(obj_name_arr[row])
            # different observation directories cannot be in the same group
            # ---> start a new group
            elif obs_dir_arr[row] != obs_dir:
                # if we have a new group copy the mask
                current_mask = np.array(zero_mask)
                # reset the current sequence present for this group
                current_seqs = []
                # add this row to current group
                current_mask[row] = True
                # set current group obs dir
                obs_dir = str(obs_dir_arr[row])
                # set current object name
                obj_name = str(obj_name_arr[row])
            # if current number if already in current group
            # ----> replace this row with the previously found one
            elif current in current_seqs:
                # set the current row to True
                current_mask[row] = True
                #  positions where current seq was True
                pos = np.where(np.array(current_seqs) == current)[0]
                # set these positions to False - we shouldn't have
                #  2 of the same position in the same group
                current_mask[current_mask][pos] = False
            # append to current file if current number is less than
            #   total number in sequence
            # ----> add to current group
            elif current < num_arr[row]:
                # add this row to current group
                current_mask[row] = True
                # append row to current group
                current_seqs.append(current)
                # set current group obs dir
                obs_dir = str(obs_dir_arr[row])
                # set current object name
                obj_name = str(obj_name_arr[row])
            # if we have reached the end of a group append the masks
            #   and set the current mask to zero and reset the current number
            #   to zero
            # ----> add to current group
            # if we have enough entres (==nexp) ----> start new group after add
            elif current == num_arr[row]:
                # add this row to current group
                current_mask[row] = True
                # append group to masks - only if we have NEXP sequences
                if np.sum(current_mask) == num_arr[row]:
                    masks.append(current_mask)
                # if we have a new group copy the mask
                current_mask = np.array(zero_mask)
                # reset the current sequence present for this group
                current_seqs = []
                # set current group obs dir
                obs_dir = str(obs_dir_arr[row])
                # set current object name
                obj_name = str(obj_name_arr[row])
            # if we have enough entries ----> add mask to list of masks
            # ----> start new group
            else:
                # append group to masks - only if we have NEXP sequences
                if np.sum(current_mask) == num_arr[row]:
                    masks.append(current_mask)
                # if we have a new group copy the mask
                current_mask = np.array(zero_mask)
                # reset the current sequence present for this group
                current_seqs = []
                # reset the observation directory
                obs_dir = None
                # rest the object name
                obj_name = None
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


def lbl_compute_group(rargs: Dict[str, DrsArgument],
                      rkwargs: Dict[str, DrsArgument],
                      argdict: Dict[str, ArgDictType],
                      kwargdict: Dict[str, ArgDictType],
                      **kwargs) -> RunType:
    """
    For objname = FP   sets iteration and total arguments
    based on number of cores given

    For all other objnames acts like "no_group"

    :param rargs:
    :param rkwargs:
    :param argdict:
    :param kwargdict:
    :param kwargs:
    :return:
    """

    # get params from kwargs
    params = kwargs['params']
    # get values from params
    cores = kwargs['cores']
    objlist = params.listp('LBL_MULTI_OBJLIST', dtype=str)

    # make sure this is not used for recipes that do not have the correct
    #  arguments
    cond1 = 'objname' in rargs
    cond2 = 'total' in rkwargs
    cond3 = 'iteration' in rkwargs

    # if any of these conditions are not met run no_group
    if not cond1 or not cond2 or not cond3:
        return no_group(rargs, rkwargs, argdict, kwargdict, **kwargs)

    # if object name is not in object list run no_group
    if argdict['objname'] not in objlist:
        return no_group(rargs, rkwargs, argdict, kwargdict, **kwargs)
    # ----------------------------------------------------------------------
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
    run_inst.group_column = None
    run_inst.group = None
    run_instances.append(run_inst)

    # ----------------------------------------------------------------------
    # deal with non-file arguments
    # ----------------------------------------------------------------------
    run_instances = drsgf.get_non_file_args(non_file_args, alldict,
                                            run_instances)
    # ----------------------------------------------------------------------
    # add the total and iteration arguments based on the number of cores
    # ----------------------------------------------------------------------
    new_run_instances = []
    # loop around run instances
    for run_inst in run_instances:
        # loop around cores - one group per core
        for core in range(cores):
            # copy the run instance
            run_inst2 = run_inst.copy()
            # get the total number of cores
            total = int(cores)
            # get the iteration number
            iteration = core + 1
            # add value to dictionary
            run_inst2.dictionary['total'] = total
            run_inst2.dictionary['iteration'] = iteration
            # append to run instances
            new_run_instances.append(run_inst2)
    # add iteration and total to arg_order
    arg_order += ['iteration', 'total']
    # ----------------------------------------------------------------------
    # convert in to run list of dictionaries
    # ----------------------------------------------------------------------
    runs = []
    # loop around instances
    for run_inst in new_run_instances:
        # create run dict
        rundict = OrderedDict()
        # loop around arguments in correct order
        for key in arg_order:
            rundict[key] = run_inst.dictionary[key]
        # add this run dictionary to runs
        runs.append(rundict)
    # return the run instances
    return runs



def _is_numeric(array: Union[list, np.ndarray, Iterable]) -> np.ndarray:
    """
    Create a mask of only numerical values in an array

    :param array: list or numpy array or iterable to find out whether elements
                  can be a float
    :return: numpy array of booleans True if element can be float, False
             otherwise
    """
    # mapping function: True for numeric False otherwise
    def test_float(x):
        # noinspection PyBroadException
        try:
            _ = float(x)
            return True
        except Exception as _:
            return False

    # return map as a numpy array of True and Falses (a mask)
    return np.array(list(map(test_float, array)))


def _get_raw_table(alldict: dict, first_arg: str,
                   drsfiletype: str) -> Union[Table, None]:
    """
    Get the raw table from alldict (which could contain a table or a single
    row or None

    :param alldict: dict, the all dict dictionary of dictionaries containing
                    the tables/rows or None entries for each arg
    :param first_arg: str, the argument to access in alldict
    :param drsfiletype: str, the file type to access in alldict

    :return: Table or None, returns Table if a Table.Row or Table was found
    """
    # get arg 0 table
    rawtab = alldict[first_arg][drsfiletype]
    # if rawtable is a single row - we had one row and need to convert
    #   back to a table
    if isinstance(rawtab, Table.Row):
        return Table(rawtab)
    # if rawtab is a Table then we are good - we have multiple rows
    elif isinstance(rawtab, Table):
        return rawtab
    # rawtab none means no files of this type
    elif rawtab is None:
        return None
    # else we have to deal with an error
    else:
        # set function name
        func_name = display_func('_get_raw_table', __NAME__)
        # raise error: alldict[{0}][{1}] is not a valid astropy table
        eargs = [first_arg, drsfiletype, func_name]
        raise drs_exceptions.DrsCodedException('00-006-00024', 'error',
                                               targs=eargs,
                                               func_name=func_name)


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
