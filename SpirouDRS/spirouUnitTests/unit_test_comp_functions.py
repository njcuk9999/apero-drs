#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-01-11 at 13:40

@author: cook



Version 0.0.0
"""
from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
import os
import sys

from SpirouDRS import spirouConfig
from SpirouDRS.spirouImage import spirouFITS

if sys.version_info.major > 2:
    raw_input = lambda x: str(input(x))

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouUnitTests.unit_test1.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
def create_oldfiles(newfiles, oldpath, newpath):
    oldfiles = []
    newfiles1 = []
    # loop around new files
    for newfile in newfiles:
        # deal with a string
        if type(newfile) == str:
            # get old file
            oldfile = newfile.replace(newpath, oldpath)
            # append to storage
            oldfiles.append(oldfile)
            newfiles1.append(newfile)
        # else assume we have a list in a list
        else:
            for newf in newfile:
                # get old file
                oldfile = newf.replace(newpath, oldpath)
                # append to storage
                oldfiles.append(oldfile)
                newfiles1.append(newf)
    # return oldfiles
    return newfiles1, oldfiles


def comparison_wrapper(name, oldfiles, newfiles, errors=None, path=None):

    # deal with no path
    if path is None:
        path = './'

    # deal with source errors
    if errors is None:
        errors = []

    # check lengths
    if len(oldfiles) != len(newfiles):
        emsg = ("Length of oldfiles (len={0}) and newfiles (len={1}) "
                "is not the same")
        raise ValueError(emsg.format(len(oldfiles), len(newfiles)))

    # loop around files
    for f_it in range(len(oldfiles)):
        # get iteration params
        oldfile, newfile = oldfiles[f_it], newfiles[f_it]
        # check they both exist
        e0 = check_existance(oldfile, newfile, name=name)
        # compare data
        if len(e0) == 0:
            e1 = compare_data(oldfile, newfile, plot=True, path=path, name=name)
            e2 = compare_header(oldfile, newfile, name=name)
            # store errors
            errors += e1
            errors += e2
        else:
            e1, e2 = [], []

        # print status
        if len(errors) > 0:
            wmsg = '\n\t{0} errors found in {1}'
            print(wmsg.format(len(e0) + len(e1) + len(e2), newfile))
        else:
            wmsg = '\n\tNo errors found in {0} - files the same'
            print(wmsg.format(newfile))

    # return errors for files
    return errors


def check_existance(old_file, new_file, name):

    errors = []

    # get name of file
    oldname = os.path.split(old_file)[-1]
    newname = os.path.split(new_file)[-1]
    # check for old file
    if not os.path.exists(old_file):
        emsg = [name, oldname, newname, 'FILE',
                'Old file "{0}" does not exist'.format(old_file),
                np.nan, np.nan, np.nan]
        errors.append(emsg)

    # check for new file
    if not os.path.exists(new_file):
        emsg = [name, oldname, newname, 'FILE',
                'New file "{0}" does not exist'.format(new_file),
                np.nan, np.nan, np.nan]
        errors.append(emsg)

    # return errors
    return errors

def compare_data(old_file, new_file, errors=None, plot=False, path='./',
                 name=''):

    # get name of file
    oldname = os.path.split(old_file)[-1]
    newname = os.path.split(new_file)[-1]

    # setup error array
    if errors is None:
        errors = []
    # read old file data
    data1, nx1, ny1 = spirouFITS.read_raw_data(old_file, getheader=False)
    # read new file data
    data2, nx2, ny2 = spirouFITS.read_raw_data(new_file, getheader=False)

    # get stats
    stats = get_stats(data1, data2)

    # check if data is the same
    if np.sum(stats['diff']) != 0:
        # log non-zero error
        emsg = [name, oldname, newname, 'DATA', 'Difference image is non-zero',
                np.nan, np.nan, np.nan]
        errors.append(emsg)
        # log stats on old image
        emsg = [name, oldname, newname, 'DATA', 'axis=0 (mean,median,std)',
                stats['xmean'], stats['xmedian'], stats['xstd']]
        errors.append(emsg)
        # log stats on new image
        emsg = [name, oldname, newname, 'DATA', 'axis=0 (mean,median,std)',
                stats['ymean'], stats['ymedian'], stats['ystd']]
        errors.append(emsg)
        # log stats on full diff image
        emsg = [name, oldname, newname, 'DATA', 'diff (mean,median,std)',
                stats['diffmean'], stats['diffmedian'], stats['diffstd']]
        errors.append(emsg)

    # plot
    if (np.sum(stats['diff']) != 0) and plot:
        # plot graph for each row and column (running stats)
        plot_stats(stats, oldname, newname, path)

    return errors


def compare_header(old_file, new_file, errors=None, name=''):

    # get name of file
    oldname = os.path.split(old_file)[-1]
    newname = os.path.split(new_file)[-1]

    # setup error array
    if errors is None:
        errors = []
    # read old file data
    hdr1, cmt1 = spirouFITS.read_raw_header(old_file)
    # read new file data
    hdr2, cmt2 = spirouFITS.read_raw_header(new_file)

    # find all keys in both files
    keys1 = list(hdr1.keys())
    keys2 = list(hdr2.keys())
    ukeys = np.unique(keys1 + keys2)

    for ukey in ukeys:
        # check key is in OLD
        if ukey not in hdr1:
            # log error message
            emsg = [name, oldname, newname, 'HEADER',
                    'Key "{0}" is in NEW but not in OLD'.format(ukey),
                    np.nan, np.nan, np.nan]
            errors.append(emsg)
            continue
        # check key is in NEW
        elif ukey not in hdr2:
            # log error message
            emsg = [name, oldname, newname, 'HEADER',
                    'Key "{0}" is in OLD but not in NEW'.format(ukey),
                    np.nan, np.nan, np.nan]
            errors.append(emsg)
        # check that value is the same in both
        else:
            # get values and diff
            value1, value2 = hdr1[ukey], hdr2[ukey]
            try:
                diff = value1 - value2
            except TypeError:
                diff = np.nan

            # check that that are the same
            if value1 != value2:
                # log error message for value1 != value2
                emsg = [name, oldname, newname, 'HEADER',
                        'key={0} old,new,diff'.format(ukey),
                        value1, value2, diff]
                errors.append(emsg)

    # return errors
    return errors


def get_stats(x, y):

    # define storage
    stats = dict()

    # get difference
    diff = x - y
    stats['diff'] = diff

    # get diff stats
    stats['diffmean'] = np.mean(diff)
    stats['diffmedian'] = np.median(diff)
    stats['diffstd'] = np.std(diff)
    stats['diffmean1'] = np.mean(diff, axis=0)
    stats['diffmedian1'] = np.median(diff, axis=0)
    stats['diffstd1'] = np.std(diff, axis=0)
    stats['diffmean2'] = np.mean(diff, axis=1)
    stats['diffmedian2'] = np.median(diff, axis=1)
    stats['diffstd2'] = np.std(diff, axis=1)

    # get x stats
    stats['xmean'] = np.mean(x)
    stats['xmedian'] = np.median(x)
    stats['xstd'] = np.std(x)
    stats['xmean1'] = np.mean(x, axis=0)
    stats['xmedian1'] = np.median(x, axis=0)
    stats['xstd1'] = np.std(x, axis=0)
    stats['xmean2'] = np.mean(x, axis=1)
    stats['xmedian2'] = np.median(x, axis=1)
    stats['xstd2'] = np.std(x, axis=1)

    # get y stats
    stats['ymean'] = np.mean(y)
    stats['ymedian'] = np.median(y)
    stats['ystd'] = np.std(y)
    stats['ymean1'] = np.mean(y, axis=0)
    stats['ymedian1'] = np.median(y, axis=0)
    stats['ystd1'] = np.std(y, axis=0)
    stats['ymean2'] = np.mean(y, axis=1)
    stats['ymedian2'] = np.median(y, axis=1)
    stats['ystd2'] = np.std(y, axis=1)

    return stats

# =============================================================================
# Define plot functions
# =============================================================================

def plot_stats(stats, oldname, newname, path='./'):

    # clean
    plt.close()

    # get title
    title = 'OLD = {0}   NEW = {1}'.format(oldname, newname)

    # x direction
    fig1, frames = plt.subplots(ncols=2, nrows=2)
    fig1.set_size_inches(16, 10)

    # means
    frames[0][0].plot(stats['xmean1'], color='r', label='OLD')
    frames[0][0].plot(stats['ymean1'], color='b', label='NEW')
    frames[0][0].plot(stats['diffmean1'], color='g', label='DIFF')
    frames[0][0].legend(loc=0)
    frames[0][0].set(xlabel='pixel number', ylabel='pixel value',
                     title='mean axis=0')
    # medians
    frames[1][0].plot(stats['xmedian1'], color='r', label='OLD')
    frames[1][0].plot(stats['ymedian1'], color='b', label='NEW')
    frames[1][0].plot(stats['diffmedian1'], color='g', label='DIFF')
    frames[1][0].legend(loc=0)
    frames[1][0].set(xlabel='pixel number', ylabel='pixel value',
                     title='median axis=0')
    # std
    frames[0][1].plot(stats['xstd1'], color='r', label='OLD')
    frames[0][1].plot(stats['ystd1'], color='b', label='NEW')
    frames[0][1].plot(stats['diffstd1'], color='g', label='DIFF')
    frames[0][1].legend(loc=0)
    frames[0][1].set(xlabel='pixel number', ylabel='pixel value',
                     title='std axis=0')
    # diff image
    frames[1][1].imshow(stats['diff'])
    frames[1][1].set(title='Difference image')

    # set title
    plt.suptitle(title)

    # -------------------------------------------------------------------------
    # show and close
    name = 'OLD_{0}_NEW_{1}_axis0'.format(oldname, newname)
    filename = os.path.join(path, name)

    plt.tight_layout()
    plt.savefig(filename + '.png', bbox_inches='tight')
    plt.savefig(filename + '.pdf', bbox_inches='tight')
    plt.close()

    # -------------------------------------------------------------------------
    # y direction
    fig2, frames = plt.subplots(ncols=2, nrows=2)
    fig2.set_size_inches(16, 10)

    # means
    frames[0][0].plot(stats['xmean2'], color='r', label='OLD')
    frames[0][0].plot(stats['ymean2'], color='b', label='NEW')
    frames[0][0].plot(stats['diffmean2'], color='g', label='DIFF')
    frames[0][0].legend(loc=0)
    frames[0][0].set(xlabel='pixel number', ylabel='pixel value',
                     title='mean axis=1')
    # medians
    frames[1][0].plot(stats['xmedian2'], color='r', label='OLD')
    frames[1][0].plot(stats['ymedian2'], color='b', label='NEW')
    frames[1][0].plot(stats['diffmedian2'], color='g', label='DIFF')
    frames[1][0].legend(loc=0)
    frames[1][0].set(xlabel='pixel number', ylabel='pixel value',
                     title='median axis=1')
    # std
    frames[0][1].plot(stats['xstd2'], color='r', label='OLD')
    frames[0][1].plot(stats['ystd2'], color='b', label='NEW')
    frames[0][1].plot(stats['diffstd2'], color='g', label='DIFF')
    frames[0][1].legend(loc=0)
    frames[0][1].set(xlabel='pixel number', ylabel='pixel value',
                     title='std axis=1')
    # diff image
    frames[1][1].imshow(stats['diff'])
    frames[1][1].set(title='Difference image')

    # set title
    plt.suptitle(title)

    # -------------------------------------------------------------------------
    # show and close
    name = 'OLD_{0}_NEW_{1}_axis1'.format(oldname, newname)
    filename = os.path.join(path, name)

    plt.tight_layout()
    plt.savefig(filename + '.png', bbox_inches='tight')
    plt.savefig(filename + '.pdf', bbox_inches='tight')
    plt.close()


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
