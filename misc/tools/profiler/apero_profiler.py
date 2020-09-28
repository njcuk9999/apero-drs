#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CODE DESCRIPTION HERE

Created on 2020-09-2020-09-28 17:30

@author: cook
"""
from astropy.table import Table
import argparse
import io
import numpy as np
import os
import pstats
import sys

# =============================================================================
# Define variables
# =============================================================================
# define the path to recipes
PROGRAM_PATH = '/spirou/drs/apero-drs/bin/'
# define the profile command
COMMAND = 'python -m cProfile -o {0} {1}'
# define function path to test
FUNC_PATH = 'apero-drs/apero'
# test run (without argumnet)
sys.argv = ['mycode', 'cal_extract_spirou.py 2020-05-10 2487537o_pp.fits']

# =============================================================================
# Define functions
# =============================================================================
def get_args():
    parser = argparse.ArgumentParser(description='Neils profiling script')
    parser.add_argument('recipe', type=str,
                        help='The recipe string to run - must be surrounded by'
                             '"" to avoid parsing in multiple arguments'
                             ' i.e. "cal_extract_spirou.py NIGHT FILE" ')
    return parser.parse_args()


def stat_to_table(outputname):
    # create csv file name
    csvfile = outputname + '.csv'
    # from here:
    #     https://stackoverflow.com/a/51541290/7858439
    rawresult = io.StringIO()
    pstats.Stats(outputname, stream=rawresult).print_stats()
    rawresult = rawresult.getvalue()
    rawresult = 'ncalls' + rawresult.split('ncalls')[-1]

    rawlines = rawresult.split('\n')

    # set up storage dict
    storage = dict()
    storage['ncalls'] = []
    storage['tottime'] = []
    storage['percall1'] = []
    storage['cumtime'] = []
    storage['percall2'] = []
    storage['func'] = []

    for rawline in rawlines:
        entries = rawline.rstrip().split(None, 5)
        if len(entries) == 6:
            if entries[0] == 'ncalls':
                continue
            storage['ncalls'].append(entries[0].split('/')[0])
            storage['tottime'].append(entries[1])
            storage['percall1'].append(entries[2])
            storage['cumtime'].append(entries[3])
            storage['percall2'].append(entries[4])
            storage['func'].append(entries[5])

    # convert floats to numpy float arrays
    storage['ncalls'] = np.array(storage['ncalls']).astype(int)
    storage['tottime'] = np.array(storage['tottime']).astype(float)
    storage['percall1'] = np.array(storage['percall1']).astype(float)
    storage['cumtime'] = np.array(storage['cumtime']).astype(float)
    storage['percall2'] = np.array(storage['percall2']).astype(float)

    # set up Table
    table = Table()
    for col in storage:
        table[col] = storage[col]

    return table


def mask_by_func(table, key, column='func'):
    # define mask
    mask = np.zeros(len(table)).astype(bool)
    for row in range(len(table)):
        if key in table[column][row]:
            mask[row] = True
    return table[mask]


def sort_by_col(table, column='cumtime', ascending=True):
    sortmask = np.argsort(table[column])
    if ascending:
        return table[sortmask]
    else:
        return table[sortmask[::-1]]


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # deal with arguments
    args = get_args()
    # get recipe from arguments
    recipestr = PROGRAM_PATH + args.recipe.strip()
    # get recipe name from arguments
    recipename = args.recipe.split(' ')[0]
    # create output name
    outputname = recipename.replace('.py', '.profile')
    # make command
    command = COMMAND.format(outputname, recipestr)
    # run profile command
    print('\n\n' + '=' * 50)
    print('\tRunning profiling on:')
    print('\t\t{0}'.format(recipestr))
    print('=' * 50 + '\n\n')
    os.system(command)
    # load it with pstats and save to csv file
    stat_table = stat_to_table(outputname)
    # mask by func having apero
    func_table = mask_by_func(stat_table, key=FUNC_PATH)
    # sort by total time
    ncalls = sort_by_col(func_table, column='ncalls', ascending=False)
    tot_time = sort_by_col(func_table, column='tottime', ascending=False)
    cum_time = sort_by_col(func_table, column='cumtime', ascending=False)



# =============================================================================
# End of code
# =============================================================================
