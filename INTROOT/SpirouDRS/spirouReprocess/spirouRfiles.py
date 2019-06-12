#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-06-10 at 10:56

@author: cook
"""

from __future__ import division
import numpy as np
import os
import sys
from astropy.table import Table
from collections import OrderedDict

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS.spirouTools import drs_reset

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouRfiles.py'
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
# -----------------------------------------------------------------------------
# valid file types
RAW_VALID = ['a.fits', 'c.fits', 'd.fits', 'f.fits', 'o.fits']

# index filename column
ITABLE_FILECOL = 'FILENAME'
NIGHT_COL = '@@@NIGHTNAME'
ABSFILE_COL = '@@@ABSFILE'
HEADERKEYS = ['KW_ACQTIME', 'KW_CCAS', 'KW_CREF', 'KW_CMPLTEXP', 'KW_NEXP']
SORTCOL = 'KW_ACQTIME'
# define where the run directory is
RUN_DIR = '/scratch/Projects/spirou/data_dev/runs/'
RUN_KEY = 'ID'

# =============================================================================
# find files
# =============================================================================
def find_raw_files(params):
    # get path
    path, rpath = get_path_and_check(params, 'DRS_DATA_RAW')
    # get files
    gfout = get_files(params, path, rpath)
    nightnames, filelist, basenames, kwargs = gfout
    # construct a table
    mastertable = Table()
    mastertable[NIGHT_COL] = nightnames
    mastertable[ITABLE_FILECOL] = basenames
    mastertable[ABSFILE_COL] = filelist
    for kwarg in kwargs:
        mastertable[kwarg] = kwargs[kwarg]
    # sort by sortcol
    sortmask = np.argsort(mastertable[SORTCOL])
    mastertable = mastertable[sortmask]
    # return the file list
    return mastertable, rpath


def find_tmp_files(params):
    # get path
    path, rpath = get_path_and_check(params, 'DRS_DATA_WORKING')
    # look for index files
    index_files, night_names = get_index_files(params, path, rpath)
    # get index file contents
    index_contents = load_index_files(params, path, index_files, night_names)
    # return index database
    return index_contents, rpath


def find_reduced_files(params):
    # get path
    path, rpath = get_path_and_check(params, 'DRS_DATA_REDUC')
    # look for index files
    index_files, night_names = get_index_files(params, path, rpath)
    # get index file contents
    index_contents = load_index_files(params, path, index_files, night_names)
    # return index database
    return index_contents, rpath


def read_run_file(params, runfile=None):
    func_name = __NAME__ + '.read_run_file()'
    # ----------------------------------------------------------------------
    # deal with no runfile
    if runfile is None:
        if len(sys.argv) < 2:
            emsg = 'Must provide a run file for reprocessing'
            WLOG(params, 'error', emsg)
        else:
            runfile = sys.argv[-1]
    # ----------------------------------------------------------------------
    # check if run file exists
    if not os.path.exists(runfile):
        # construct run file
        runfile = os.path.join(RUN_DIR, runfile)
        # check that it exists
        if not os.path.exists(runfile):
            emsg = 'Cannot find run file {0}'
            WLOG(params, 'error', emsg.format(runfile))
    # ----------------------------------------------------------------------
    # now try to load run file
    try:
        keys, values = np.loadtxt(runfile, delimiter='=', comments='#',
                                  unpack=True, dtype=str)
    except Exception as e:
        # log error
        emsg1 = 'RunFileError: Cannot open file {0}'.format(runfile)
        emsg2 = '\tError {0}: {1}'.format(type(e), e)
        WLOG(params, 'error', [emsg1, emsg2])
        keys, values = [], []
    # ----------------------------------------------------------------------
    # table storage
    runtable = OrderedDict()
    keytable = OrderedDict()
    # sort out keys into id keys and values for p
    for it in range(len(keys)):
        # get this iterations values
        key = keys[it].upper().strip()
        value = values[it].strip()
        # find the id keys
        if key.startswith(RUN_KEY):
            # attempt to read id string
            try:
                runid = int(key.replace(RUN_KEY, ''))
            except Exception as e:
                emsg1 = 'Problem reading run file key {0} = {1}'
                emsg2 = ('\t Key must be ID##### = command where #### is '
                         'an integer"')
                WLOG(params, 'error', [emsg1.format(key, value), emsg2])
                runid = None
            # check if we already have this column
            if runid in runtable:
                wmsg1 = 'Overwriting row {0}'.format(runid)
                wargs = [keytable[runid], runtable[runid]]
                wmsg2 = '\tOld value: {0} = {1}'.format(*wargs)
                tvalue = values[it][:40] + '...'
                wmsg3 = '\tNew value: {0} = {1}'.format(keys[it], tvalue)
                WLOG(params, 'warning', wmsg1)
                WLOG(params, 'warning', wmsg2)
                WLOG(params, 'warning', wmsg3)
            # add to table
            runtable[runid] = value
            keytable[runid] = key
        # else add to parameter dictionary
        else:
            # deal with special strings
            if value.upper() == 'TRUE':
                value = True
            elif value.upper() == 'FALSE':
                value = False
            # log if we are overwriting value
            if key in params:
                wmsg1 = 'Overwriting constant {0}'.format(key)
                wargs = [params[key], value]
                wmsg2 = '\tOld value = {0} New value = {1}'.format(*wargs)
                WLOG(params, 'warning', [wmsg1, wmsg2])
            # add to params
            params[key] = value
            params.set_source(key, func_name)

    # deal with night name
    if params['NIGHT_NAME'].upper() == 'NONE':
        params['NIGHT_NAME'] = None

    # return parameter dictionary and runtable
    return params, runtable


def send_email(params, kind='start'):

    if not params['SEND_EMAIL']:
        return 0
    try:
        import yagmail
        YAG = yagmail.SMTP(params['EMAIL_ADDRESS'])
    except ImportError:
        WLOG(params, 'error', 'Cannot send email (need pip install yagmail)')
        YAG = None
    except Exception as e:
        WLOG(params, 'error', 'Error {0}: {1}'.format(type(e), e))
        YAG = None

    if kind == 'start':
        receiver = params['EMAIL_ADDRESS']
        subject = ('[SPIROU-DRS] {0} has started (PID = {1})'
                   ''.format(__NAME__, params['PID']))
        body = ''
        for logmsg in WLOG.pout['LOGGER_ALL']:
            body += '{0}\t{1}\n'.format(*logmsg)

    elif kind == 'end':
        receiver = params['EMAIL_ADDRESS']
        subject = ('[SPIROU-DRS] {0} has finished (PID = {1})'
                   ''.format(__NAME__, params['PID']))
        body = ''
        for logmsg in params['LOGGER_FULL']:
            for log in logmsg:
                body += '{0}\t{1}\n'.format(*log)
    else:
        return 0

    YAG.send(to=receiver, subject=subject, contents=body)


def reset(params):
    if not params['RESET_ALLOWED']:
        return 0
    if params['RESET_TMP']:
        drs_reset.reset_tmp_folders(params, log=True)
    if params['RESET_REDUCED']:
        drs_reset.reset_reduced_folders(params, log=True)
    if params['RESET_CALIB']:
        drs_reset.reset_calibdb(params, log=True)
    if params['RESET_TELLU']:
        drs_reset.reset_telludb(params, log=True)
    if params['RESET_LOG']:
        drs_reset.reset_log(params)
    if params['RESET_PLOT']:
        drs_reset.reset_plot(params)


# =============================================================================
# Define worker functions
# =============================================================================
def get_uncommon_path(path1, path2):
    """
    Get the uncommon path from path1 and path2

    :param path1:
    :param path2:
    :return:
    """
    # get common path
    cpath = os.path.commonpath([path1, path2])
    # deal with no commonality
    if cpath == os.sep:
        return None
    # get uncommon path in path
    if len(path1) > len(path2):
        ucpath = path1.split(cpath)[-1]
    else:
        ucpath = path2.split(cpath)[-1]
    # remove separators at start
    while ucpath.startswith(os.sep):
        ucpath = ucpath.replace(os.sep, '', 1)
    # return uncommon path
    return ucpath


def get_path_and_check(params, key):
    # check key in params
    if key not in params:
        WLOG(params, 'error', '{0} not found in params'.format(key))
    # get top level path to search
    rpath = params[key]
    if params['NIGHT_NAME'] is not None and params['NIGHT_NAME'] != '':
        path = os.path.join(rpath, params['NIGHT_NAME'])
    else:
        path = str(rpath)
    # check if path exists
    if not os.path.exists(path):
        WLOG(params, 'error', 'Path {0} does not exist'.format(path))
    else:
        return path, rpath


def get_files(params, path, rpath):
    func_name = __NAME__ + '.get_files()'
    # storage list
    filelist, basenames, nightnames = [], [], []
    # populate the storage dictionary
    kwargs = dict()
    for key in HEADERKEYS:
        kwargs[key] = []
    # get files
    for root, dirs, files in os.walk(path):
        for filename in files:
            # get night name
            ucpath = get_uncommon_path(root, rpath)
            if ucpath is None:
                wmsg1 = 'Problem with paths: {0} and {1}'
                wmsg2 = '\tfunction = {0}'.format(func_name)
                WLOG(params, 'error', [wmsg1.format(path, rpath), wmsg2])
            # make sure file is valid
            isvalid = False
            for suffix in RAW_VALID:
                if filename.endswith(suffix):
                    isvalid = True
            # do not scan empty ucpath
            if len(ucpath) == 0:
                continue
            # log the night directory
            if ucpath not in nightnames:
                WLOG(params, '', '\tScanning directory: {0}'.format(ucpath))
            # get absolute path
            abspath = os.path.join(root, filename)
            # if not valid skip
            if not isvalid:
                continue
            # else append to list
            else:
                nightnames.append(ucpath)
                filelist.append(abspath)
                basenames.append(filename)
            # deal with header
            if filename.endswith('.fits'):
                header = spirouImage.ReadHeader(params, abspath)
                for key in HEADERKEYS:
                    rkey = params[key][0]
                    if rkey in header:
                        kwargs[key].append(header[rkey])
                    else:
                        kwargs[key].append('')
    # return filelist
    return nightnames, filelist, basenames, kwargs


def get_index_files(params, path, rpath):
    func_name = __NAME__ + '.get_index_files()'
    # get index filename
    index_filename = spirouConfig.Constants.INDEX_OUTPUT_FILENAME()
    # storage of index files
    filelist, nightnames = [], []
    # walk around all sub-directories and look for index files
    for root, dirs, files in os.walk(path):
        for filename in files:
            if filename == index_filename:
                # get night name
                ucpath = get_uncommon_path(root, rpath)
                if ucpath is None:
                    wmsg1 = 'Problem with paths: {0} and {1}'
                    wmsg2 = '\tfunction = {0}'.format(func_name)
                    WLOG(params, 'error', [wmsg1.format(path, rpath), wmsg2])
                nightnames.append(ucpath)
                # append absolute path
                filelist.append(os.path.join(root, filename))
    # return index file list
    return filelist, nightnames


def load_index_files(params, path, index_files, nightnames):
    # database storage
    database = OrderedDict()
    # loop around index_files
    for it, index_file in enumerate(index_files):
        # get this iterations night name
        nightname = nightnames[it]
        # log progress
        wmsg = '\tLoading index file {0}/{1} night: "{2}"'
        WLOG(params, '', wmsg.format(it + 1, len(index_files), nightname))
        # load table
        itable = spirouImage.ReadTable(params, index_file, fmt='fits')
        # set colnames
        colnames = [NIGHT_COL] + list(itable.colnames) + [ABSFILE_COL]
        # if we have no database set up yet then add all columns as empty
        #   lists
        if len(database) == 0:
            # make sure we have the same columns
            for col in colnames:
                database[col] = []
        # else make sure we have the same columns
        for col in colnames:
            if col not in database:
                database[col] = [''] * len(database[ITABLE_FILECOL])
        # generate key for each row and add to database
        for row in range(len(itable)):
            # get the key for the database dictionary (absolute file path)
            key = os.path.join(path, itable[row][ITABLE_FILECOL])
            # add each column to the table
            for col in database.keys():
                # if col is abspath key then add key
                if col == ABSFILE_COL:
                    database[col].append(key)
                # if col is night name key then add night name
                elif col == NIGHT_COL:
                    database[col].append(nightname)
                # if we don't have the key add a blank entry
                elif col not in list(itable.colnames):
                    database[col].append('')
                # else add entry
                else:
                    database[col].append(itable[col][row])
    # convert back to a master table
    mastertable = Table()
    for col in list(database.keys()):
        mastertable[col] = database[col]
    # return this master table
    return mastertable


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
