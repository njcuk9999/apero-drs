#!/usr/bin/env python
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
from astropy.table import Table
import os
import sys
import warnings
import shutil

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS.spirouImage import spirouFITS
from SpirouDRS.spirouCore import GetTimeNowString


if sys.version_info.major > 2:
    def raw_input(x):
        return str(input(x))

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouUnitTests.unit_test_comp_functions.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get plotting functions
sPlt = spirouCore.sPlt
plt = sPlt.plt
# -----------------------------------------------------------------------------


# =============================================================================
# Define functions
# =============================================================================
def get_folder_name(rawpath, foldername=None):

    # construct folder name if not given
    if foldername is None:
        # Make a new folder with todays date and timestamp
        timestamp = GetTimeNowString(r'Unit-Test-%Y%m%d-%H00', 'local')
        foldername = timestamp + '_unit_test'
    # join rawpath and foldername
    path = os.path.join(rawpath, foldername)

    # test to see if path exists
    if os.path.exists(path):
        shutil.rmtree(path)

    # add directory
    os.mkdir(path)

    # return directory
    return path


def compare(name, ll, newoutputs, oldoutputs, errors, oldpath, resultspath):

    print('\n\n Comparing files...')
    # define new output files from ll
    newfiles = ll['outputs']
    # define new path from p['reduced_dir']
    newpath = ll['p']['reduced_dir']
    # get old output locations (that should be the same as new output files)
    lists = create_oldfiles(newfiles, oldpath, newpath)
    newoutputs[name], oldoutputs[name] = lists
    # get any differences between old and new
    e0 = comparison_wrapper(name, oldoutputs[name], newoutputs[name],
                            path=resultspath)
    errors += e0

    # return dicts
    return newoutputs, oldoutputs, errors


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
            wmsg = '\n\t{0} differences found in {1}'
            print(wmsg.format(len(e0) + len(e1) + len(e2), newfile))
        else:
            wmsg = '\n\tNo difference found in {0} - files the same'
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
                np.nan, np.nan, np.nan, np.nan]
        errors.append(emsg)

    # check for new file
    if not os.path.exists(new_file):
        emsg = [name, oldname, newname, 'FILE',
                'New file "{0}" does not exist'.format(new_file),
                np.nan, np.nan, np.nan, np.nan]
        errors.append(emsg)

    # check for fits file
    if ('.fits' not in new_file) or ('.fits' not in old_file):
        emsg = [name, oldname, newname, 'FILE',
                'Cannot compare non fits file',
                np.nan, np.nan, np.nan, np.nan]
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
                np.nan, np.nan, np.nan, stats['order_diff']]
        errors.append(emsg)
        # log stats on old image
        emsg = [name, oldname, newname, 'DATA', 'axis=0 (mean,median,std)',
                stats['xmean'], stats['xmedian'], stats['xstd'],
                stats['order_diff']]
        errors.append(emsg)
        # log stats on new image
        emsg = [name, oldname, newname, 'DATA', 'axis=1 (mean,median,std)',
                stats['ymean'], stats['ymedian'], stats['ystd'],
                stats['order_diff']]
        errors.append(emsg)
        # log stats on full diff image
        emsg = [name, oldname, newname, 'DATA', 'diff (mean,median,std)',
                stats['diffmean'], stats['diffmedian'], stats['diffstd'],
                stats['order_diff']]
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
                    np.nan, np.nan, np.nan, np.nan]
            errors.append(emsg)
            continue
        # check key is in NEW
        elif ukey not in hdr2:
            # log error message
            emsg = [name, oldname, newname, 'HEADER',
                    'Key "{0}" is in OLD but not in NEW'.format(ukey),
                    np.nan, np.nan, np.nan, np.nan]
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
                        value1, value2, diff, np.nan]
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
    stats['diffmean'] = np.nanmean(diff)
    stats['diffmedian'] = np.nanmedian(diff)
    stats['diffstd'] = np.nanstd(diff)
    stats['diffmean1'] = np.nanmean(diff, axis=0)
    stats['diffmedian1'] = np.nanmedian(diff, axis=0)
    stats['diffstd1'] = np.nanstd(diff, axis=0)
    stats['diffmean2'] = np.nanmean(diff, axis=1)
    stats['diffmedian2'] = np.nanmedian(diff, axis=1)
    stats['diffstd2'] = np.nanstd(diff, axis=1)

    # get x stats
    stats['xmean'] = np.nanmean(x)
    stats['xmedian'] = np.nanmedian(x)
    stats['xstd'] = np.nanstd(x)
    stats['xmean1'] = np.nanmean(x, axis=0)
    stats['xmedian1'] = np.nanmedian(x, axis=0)
    stats['xstd1'] = np.nanstd(x, axis=0)
    stats['xmean2'] = np.nanmean(x, axis=1)
    stats['xmedian2'] = np.nanmedian(x, axis=1)
    stats['xstd2'] = np.nanstd(x, axis=1)

    # get y stats
    stats['ymean'] = np.nanmean(y)
    stats['ymedian'] = np.nanmedian(y)
    stats['ystd'] = np.nanstd(y)
    stats['ymean1'] = np.nanmean(y, axis=0)
    stats['ymedian1'] = np.nanmedian(y, axis=0)
    stats['ystd1'] = np.nanstd(y, axis=0)
    stats['ymean2'] = np.nanmean(y, axis=1)
    stats['ymedian2'] = np.nanmedian(y, axis=1)
    stats['ystd2'] = np.nanstd(y, axis=1)

    # work out stats order diff
    odiff1 = cal_order_diff(stats['xmean'], stats['ymean'], stats['diffmean'])
    odiff2 = cal_order_diff(stats['xmedian'], stats['ymedian'],
                            stats['diffmedian'])
    odiff3 = cal_order_diff(stats['xstd'], stats['ystd'], stats['diffstd'])

    stats['order_diff'] = np.max([odiff1, odiff2, odiff3])

    return stats


def cal_order_diff(val1, val2, val3):
    # get the order of the value -- log(val)
    if val1 == 0:
        logval1 = 0
    else:
        logval1 = np.log10(abs(val1))
    if val2 == 0:
        logval2 = 0
    else:
        logval2 = np.log10(abs(val2))
    # if val3 (difference) is zero then make it a very small order
    if val3 == 0:
        logval3 = -9999
    else:
        logval3 = np.log10(abs(val3))
    # get the minimum order of the old and new values
    minorder = np.min([logval1, logval2])
    # get the order difference between diff and minimum order
    #     of values
    order_diff = logval3 - minorder
    # return order_diff
    return order_diff


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
    frames[0][0] = plot_stat(frames[0][0], stats['xmean1'], stats['ymean1'],
                             stats['diffmean1'], title='mean axis=0')
    # medians
    frames[1][0] = plot_stat(frames[1][0], stats['xmedian1'], stats['ymedian1'],
                             stats['diffmedian1'], title='median axis=0')
    # std
    frames[0][1] = plot_stat(frames[0][1], stats['xstd1'], stats['ystd1'],
                             stats['diffstd1'], title='std axis=0')
    # diff image
    frames[1][1] = plot_image(frames[1][1], stats['diff'])

    # set title
    plt.suptitle(title)

    # -------------------------------------------------------------------------
    # show and close
    name = 'OLD_{0}_NEW_{1}_axis0'.format(oldname, newname)
    filename = os.path.join(path, name)

    plt.savefig(filename + '.png', bbox_inches='tight')
    plt.savefig(filename + '.pdf', bbox_inches='tight')
    plt.close()

    # -------------------------------------------------------------------------
    # y direction
    fig2, frames = plt.subplots(ncols=2, nrows=2)
    fig2.set_size_inches(16, 10)

    # means
    frames[0][0] = plot_stat(frames[0][0], stats['xmean2'], stats['ymean2'],
                             stats['diffmean2'], title='mean axis=1')
    # medians
    frames[1][0] = plot_stat(frames[1][0], stats['xmedian2'], stats['ymedian2'],
                             stats['diffmedian2'], title='median axis=1')
    # std
    frames[0][1] = plot_stat(frames[0][1], stats['xstd2'], stats['ystd2'],
                             stats['diffstd2'], title='std axis=1')
    # diff image
    frames[1][1] = plot_image(frames[1][1], stats['diff'])

    # set title
    plt.suptitle(title)

    # -------------------------------------------------------------------------
    # show and close
    name = 'OLD_{0}_NEW_{1}_axis1'.format(oldname, newname)
    filename = os.path.join(path, name)

    plt.savefig(filename + '.png', bbox_inches='tight')
    plt.savefig(filename + '.pdf', bbox_inches='tight')
    plt.close()


def plot_stat(frame, x1, x2, x3, title):
    
    # if all of x is <= 0 flip it
    if np.max(x1) <= 0 and np.max(x2) <= 0:
        x1 = -x1
        x2 = -x2
        ylabel = '$log_{10}$(negative of pixel value)'
    else:
        ylabel = '$log_{10}$(pixel value)'
        
    # log x
    with warnings.catch_warnings(record=True) as _:
        logx1 = np.log10(x1)
        logx2 = np.log10(x2)
        logx3 = np.log10(abs(x3))
    
    # plot
    frame.plot(logx1, color='r', label='OLD')
    frame.plot(logx2, color='b', label='NEW')
    frame.plot(logx3, color='g', label='DIFF')
    frame.legend(loc=0)
    frame.set(xlabel='pixel number', ylabel=ylabel,
              title=title)

    return frame


def plot_image(frame, image):

    if np.max(image.shape)/np.min(image.shape) > 2:

        # find out which axis is smaller
        small = np.argmin(image.shape)
        # find out the conversion factor
        factor = int(np.max(image.shape)/np.min(image.shape))
        # scale up image
        newimage = np.repeat(image, factor, axis=small)
    else:
        newimage = image

    im = frame.imshow(newimage)
    # set title
    frame.set(title='Difference image')
    # remove x and y axis labels
    frame.set_xticklabels([])
    frame.set_yticklabels([])
    # plot colour bar
    plt.colorbar(im, ax=frame)

    return frame


# =============================================================================
# Define analysis functions
# =============================================================================
def column(matrix, i):
    return [row[i] for row in matrix]


def old_new_diff_pass(errors, threshold):
    # get columns
    kinds = column(errors, 3)
    labels = column(errors, 4)
    val1s = column(errors, 5)
    val2s = column(errors, 6)
    val3s = column(errors, 7)
    val4s = column(errors, 8)
    # define storage
    passed, ratio = [], []

    # loop around each row
    for row in range(len(labels)):
        # get iteration value
        kind, label = kinds[row], labels[row]
        val1, val2 = val1s[row], val2s[row]
        val3, val4 = val3s[row], val4s[row]
        # check that we have a difference from HEADER
        if 'old,new,diff' in label and kind == 'HEADER':
            try:
                # try to make values floats
                val1, val2, val3 = float(val1), float(val2), float(val3)
                # get the order of the value -- log(val)
                order_diff = cal_order_diff(val1, val2, val3)
                # check that order_diff is below threshold for pass
                if order_diff < threshold:
                    passed.append(True)
                # else test fails
                else:
                    passed.append(False)
                # append ratio
                ratio.append(order_diff)
            # if we cannot convert to a float then test fails
            except ValueError:
                passed.append(False)
                ratio.append(np.nan)
        # check that we have a difference from DATA
        elif kind == 'DATA':
            try:
                # try to make values floats
                val4 = float(val4)
                # check that order_diff is below threshold for pass
                if val4 < threshold:
                    passed.append(True)
                # else test fails
                else:
                    passed.append(False)
                # append ratio
                ratio.append(val4)
            # if we cannot convert to a float then test fails
            except ValueError:
                passed.append(False)
                ratio.append(np.nan)

        # else we have the wrong type
        else:
            passed.append(False)
            ratio.append(np.nan)

    # return passed and ratio
    return passed, ratio


def construct_error_table(errors, threshold=-8, results_path='./'):
    # get passed and ratio
    passed, ratio = old_new_diff_pass(errors, threshold)

    table = Table()

    table['names'] = column(errors, 0)
    table['oldfile'] = column(errors, 1)
    table['newfile'] = column(errors, 2)
    table['kind'] = column(errors, 3)
    table['error'] = column(errors, 4)
    table['val1'] = column(errors, 5)
    table['val2'] = column(errors, 6)
    table['val3'] = column(errors, 7)
    table['val4'] = column(errors, 8)
    table['passed'] = np.array(passed, dtype=bool)
    table['failed'] = ~np.array(passed, dtype=bool)
    table['order_diff'] = ratio

    # construct filename
    filename = os.path.split(sys.argv[0])[-1].split('.py')[0]
    # construct path
    path = os.path.join(results_path, '{0}_results.fits'.format(filename))
    # write to file
    table.write(path, overwrite=True)


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
