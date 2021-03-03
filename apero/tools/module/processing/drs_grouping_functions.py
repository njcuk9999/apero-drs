#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CODE DESCRIPTION HERE

Created on 2020-12-2020-12-01 12:10

@author: cook
"""
from astropy.table import Table
from collections import OrderedDict
import itertools
import numpy as np
from typing import Any, Dict, List, Tuple, Union

from apero.base import base
from apero.core.core import drs_argument
from apero.core.core import drs_log


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tools.module.processing.drs_grouping_functions.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get argument class
DrsArgument = drs_argument.DrsArgument
# define complex type argdict
ArgDictType = Union[Dict[str, Table], OrderedDict, None]
RunType = List[Dict[str, Any]]


# =============================================================================
# Define functions
# =============================================================================
class RunInstance:
    def __init__(self, rargs, rkwargs):
        """
        Storage for individual runs where we eventually turn these into a
        dictionary instance

    :param rargs: the dictionary of positional DrsArguments for this recipe
    :param rkwargs: the dictionary of optional DrsArguments for this recipe
        """
        self.args = rargs
        self.kwargs = rkwargs
        self.dictionary = dict()
        self.group_column = None
        self.group = None

    def copy(self):
        new_instance = RunInstance(self.args, self.kwargs)
        new_instance.dictionary = dict(self.dictionary)
        new_instance.group_column = self.group_column
        new_instance.group = self.group
        return new_instance


def find_file_args(rargs: Dict[str, DrsArgument],
                   rkwargs: Dict[str, DrsArgument],
                   argdict: Dict[str, ArgDictType],
                   kwargdict: Dict[str, ArgDictType]
                   ) -> Tuple[List[str], List[str], Dict[str, Any]]:
    """
    Find the file arguments and non file arguments in positional args (rargs)
    and optional args (rkwargs)

    :param rargs: the dictionary of positional DrsArguments for this recipe
    :param rkwargs: the dictionary of optional DrsArguments for this recipe
    :param argdict: the dictionary of tables raw files on disk that match the
                    criteria for positional arguments (one key per arg)
    :param kwargdict: the dictionary of tables raw files on disk that match the
                      criteria for optional arguments (one key per arg)

    :return:
    """

    # storage list
    file_args = []
    non_file_args = []
    # first loop around arguments
    for argname in argdict:
        # test for file argument
        if rargs[argname].dtype not in ['file', 'files']:
            non_file_args.append(argname)
        else:
            # deal with no file entries for this argument
            if argdict[argname] is None:
                file_args.append(None)
            elif len(argdict[argname]) == 0:
                file_args.append(None)
            else:
                file_args.append(argname)
    # then loop around keyword arguments
    for kwargname in kwargdict:
        # deal with other parameters (not 'files' or 'file')
        if rkwargs[kwargname].dtype not in ['file', 'files']:
            non_file_args.append(kwargname)
        else:
            # deal with no file entries for this argument
            if kwargdict[kwargname] is None:
                file_args.append(None)
            elif len(kwargdict[kwargname]) == 0:
                file_args.append(None)
            else:
                file_args.append(kwargname)

    # combine argdict and kwargdict
    alldict = OrderedDict()
    for argname in argdict:
        alldict[argname] = argdict[argname]
    for kwargname in kwargdict:
        alldict[kwargname] = kwargdict[kwargname]

    # return file args and non-file args
    return file_args, non_file_args, alldict


def get_argposorder(rargs: Dict[str, DrsArgument],
                    rkwargs: Dict[str, DrsArgument],
                    argdict: Dict[str, ArgDictType],
                    kwargdict: Dict[str, ArgDictType]):
    """
    Get the argument position order

    Take the dictionaries of arguments and figure out which order these
    positional arguments and keyword arguments should be in for this recipe
    i.e. cal_extract  directory comes before files and before optional arguments

    for positional arguments this is defined by recipe.args[{arg}].pos,
    for optional arguments they are added to the end in whichever order they
    come

    :param rargs: the dictionary of positional DrsArguments for this recipe
    :param rkwargs: the dictionary of optional DrsArguments for this recipe
    :param argdict: dictionary of values for each of the positional arguments
                   (each key is a positional argument name, each value is the
                    value that argument should have i.e.
                    directory should have value '2019-04-20'
                    --> dict(directory='2019-04-20', files=[file1, file2])
    :param kwargdict: dictionary of values for each of the optional arguments
                      (each key is an optional argument name, each value is the
                      value that argument should have i.e.
                      --{key}={value}    --plot=1
                      --> dict(plot=1)
    :return: tuple,
             1. runorder: list of strings of argument names, in the correct
                order - the value is the name of the argument
                (i.e. DrsArgument.name),
             2. rundict: a dictionary where the keys are the argument name and
                the value are a dictionary of DrsFitFile names and the values
                of these are astropy.table.Tables containing the
                files associated with this [argument][drsfile]
    """
    # set function name
    _ = __NAME__ + 'get_argposorder'
    # set up storage
    runorder = OrderedDict()
    # iterator for non-positional variables
    it = 0
    # loop around args
    for argname in rargs.keys():
        # must be in rundict keys
        if argname not in argdict.keys():
            continue
        # get arg
        arg = rargs[argname]
        # deal with non-required arguments when argdict has no values
        #    these are allowed only if arg.reprocess is True
        #    we skip adding to runorder
        if hasattr(argdict[argname], '__len__'):
            arglen = len(argdict[argname])
            if arg.reprocess and not arg.required and (arglen == 0):
                continue
        # get position or set it using iterator
        if arg.pos is not None:
            runorder[arg.pos] = argname
        else:
            runorder[1000 + it] = argname
            it += 1
    # loop around args
    for kwargname in rkwargs.keys():
        # must be in rundict keys
        if kwargname not in kwargdict.keys():
            continue
        # get arg
        kwarg = rkwargs[kwargname]
        # deal with non-required arguments when argdict has no values
        #    these are allowed only if arg.reprocess is True
        #    we skip adding to runorder
        if hasattr(kwargdict[kwargname], '__len__'):
            kwarglen = len(kwargdict[kwargname])
            if kwarg.reprocess and not kwarg.required and (kwarglen == 0):
                continue
        # get position or set it using iterator
        if kwarg.pos is not None:
            runorder[kwarg.pos] = kwargname
        else:
            runorder[1000 + it] = kwargname
            it += 1
    # recast run order into a numpy array of strings
    sortrunorder = np.argsort(list(runorder.keys()))
    runorder = np.array(list(runorder.values()))[sortrunorder]
    # return run order and run dictionary
    return list(runorder)


def get_non_file_args(non_file_args: List[str],
                      alldict: Dict[str, Any],
                      run_instances: List[RunInstance]) -> List[RunInstance]:
    """
    Deal with non file arguments (and the fact they can be lists so need
    combinations of those parameters)

    :param non_file_args: list of strings, list of the names of the non-file
                          arguments
    :param alldict: dictionary of all arguments + all possible values for
                    each argument
    :param run_instances: list of RunInstance instances - the semi-filed run
                          instances (only filled currently with file args)
    :return:
    """

    # storage for new instances
    new_run_instances = []
    # need to find any argument that is not files but is a list
    pkeys, pvalues = [], []
    for argname in non_file_args:
        # only do this for numpy arrays and lists (not files)
        if isinstance(alldict[argname], (np.ndarray, list)):
            # append values to storage
            pvalues.append(list(alldict[argname]))
            pkeys.append(argname)
    # convert pkey to array
    pkeys = np.array(pkeys)
    # we assume we want every combination of arguments (otherwise it is
    #   more complicated)
    if len(pkeys) != 0:
        combinations = list(itertools.product(*pvalues))
    else:
        combinations = [None]
    # count number of runs
    run_count = 0
    # loop around combinations
    for run_inst in run_instances:
        # loop around all combinations required
        for combination in combinations:
            # copy the run instance
            run_inst2 = run_inst.copy()
            # loop around all argument names
            for argname in non_file_args:
                # if key is directory set if from group name
                if argname == 'obs_dir':
                    value = run_inst2.group
                # if key is in our set of combinations get the value from
                #  combinations
                elif argname in pkeys:
                    # find position in combinations
                    pos = np.where(pkeys == argname)[0][0]
                    # get value from combinations
                    value = combination[pos]
                else:
                    value = alldict[argname]
                # add value to dictionary
                run_inst2.dictionary[argname] = value
            # print statement
            pmsg = '\t\tProcessing II run {0}'.format(run_count)
            drs_log.Printer(None, None, pmsg)
            # add to run count
            run_count += 1
            # add new instance to runs
            new_run_instances.append(run_inst2)
    # return new_run_instances
    return new_run_instances


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
