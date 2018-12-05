#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-04-05 at 14:37

@author: cook
"""
from __future__ import division
import os
from collections import OrderedDict

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouStartup
from SpirouDRS.spirouDB import spirouCDB

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'drs_tools.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get param dict
ParamDict = spirouConfig.ParamDict
# Get Logging function
WLOG = spirouCore.wlog
# get default config parameters
PARAMS = spirouStartup.Begin(recipe=__NAME__, quiet=True)
# -----------------------------------------------------------------------------


# =============================================================================
# Define user functions
# =============================================================================
def list_raw_files(prefix=None, suffix=None, substring=None, nightname=None,
                   raw=False):
    # set path
    path = PARAMS['DRS_DATA_RAW']
    # list files
    list_files(path, kind='RAW', prefix=prefix, suffix=suffix,
               substring=substring, nightname=nightname, raw=raw)


def list_reduced_files(prefix=None, suffix=None, substring=None,
                       nightname=None, raw=False):
    # set path
    path = PARAMS['DRS_DATA_REDUC']
    # list files
    list_files(path, kind='REDUCED', prefix=prefix, suffix=suffix,
               substring=substring, nightname=nightname, raw=raw)


def list_calib_files(prefix=None, suffix=None, substring=None, nightname=None,
                     raw=False):
    # set path
    path = PARAMS['DRS_CALIB_DB']
    # list files
    list_files(path, kind='CALIB_DB', prefix=prefix, suffix=suffix,
               substring=substring, nightname=nightname, raw=raw)


def display_calibdb(max_time=None):

    # load other config
    p = spirouStartup.Begin(recipe=__NAME__, quiet=True)
    # add custom args straight to p
    p = spirouStartup.LoadMinimum(p, customargs={})
    # set path
    path = os.path.join(p['DRS_CALIB_DB'], p['IC_CALIBDB_FILENAME'])
    # get master calib db file
    if max_time is None:
        # log master calib db file
        wmsg = 'CalibDB located at: {0}'.format(path)
        WLOG(p, '', wmsg)
        # get and check the lock file
        lock, lock_file = spirouCDB.get_check_lock_file(p)
        # try to open the master file
        lines = spirouCDB.read_master_file(p, lock, lock_file)
        # print master calibDB
        for line in lines:
            print('', line.replace('\n', ''))
        # close and remove lock file
        lock.close()
        os.remove(lock_file)
    else:
        # log master calib db file
        args = [path, max_time, p['CALIB_DB_MATCH']]
        wmsgs = ['CalibDB located at: {0}'.format(*args),
                 '    max_time={1}  method={2}'.format(*args)]
        WLOG(p, '', wmsgs)
        # get database at max_time
        cdb, p = spirouCDB.get_database(p, max_time)
        # loop around entries
        for entry in cdb:
            values = [entry] + cdb[entry]
            print('\t{0} {1} {2} {3} {4}'.format(*values))


# =============================================================================
# Define workeer functions
# =============================================================================
def set_up():
    """
    Load the parameter dictionary (i.e. the recipe setup)

    :return p: ParamDict, the parameter dictionary with all constants from
               config files loaded in
    """
    # Set up
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)
    # need custom args (to accept full path or wild card
    args, kwargs = [p, 'ICDP_NAME'], dict(required=True, logthis=False)
    p = spirouStartup.LoadOtherConfig(*args, **kwargs)
    p['RECIPE'] = __NAME__
    p['LOG_OPT'], p['PROGRAM'] = p['RECIPE'], p['RECIPE']
    # return p
    return p



def list_files(path, kind=None, prefix=None, suffix=None, substring=None,
               nightname=None, raw=False):
    # get p
    p = set_up()
    # print message
    if kind is None:
        wmsg = 'All files in {1} are:'
    else:
        wmsg = 'All {0} files in {1} are:'
    WLOG(p, '', wmsg.format(kind, path))
    # create storage
    store = OrderedDict()
    # loop around files
    for root, dirs, files in os.walk(path + '/'):
        # get dir name
        directory = os.path.split(root)[-1]
        # check if we meet nightname criteria
        if nightname is not None:
            if not (directory.upper() == nightname.upper()):
                continue
        # loop around files
        for f in files:
            # check prefix
            if prefix is not None:
                if not f.upper().startswith(prefix.upper()):
                    continue
            # check suffix
            if suffix is not None:
                if not f.upper().endswith(suffix.upper()):
                    continue
            # check substring
            if substring is not None:
                if not substring.upper() in f.upper():
                    continue
            # if raw print full path
            if raw:
                f = os.path.join(root, f)
            # store directory and filenames
            if directory not in store:
                store[directory] = [f]
            else:
                store[directory].append(f)
    # check if we have any files
    if len(store) == 0:
        print('\t\tNo files found')
    # else print
    else:
        # print directories and files
        for dir_it in list(store.keys()):
            print('\t\t{0}'.format(dir_it))
            for f in store[dir_it]:
                print('\t\t\t{0}'.format(f))


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
