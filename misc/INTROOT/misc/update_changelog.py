#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-07-04 at 10:38

@author: cook
"""
from __future__ import division
import os

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouStartup

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'update_changelog.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt
# Get constants
CONSTANTS = spirouConfig.Constants
# -----------------------------------------------------------------------------
# changelog variables
rargs = [CONSTANTS.PACKAGE(), '../../']
PATH = spirouConfig.spirouConfigFile.get_relative_folder(*rargs)
FILENAME = os.path.join(PATH, 'CHANGELOG.md')
TMPFILENAME = 'CHANGELOG.tmp'


# =============================================================================
# Define functions
# =============================================================================
def update(p, filename, path1, kind='rpm', version=None, since=None):
    # get default run
    cargs = [path1, filename]
    command = 'gcg -p {0} -o {1} -x -t'.format(*cargs)
    if kind == 'rpm':
        command += ' -O {0}'.format(kind)
    else:
        command += ' -O {0} -D None -n DRS'.format(kind)
    # add version if needed
    if version is not None:
        command += ' -c {0}'.format(version)
    # add since if needed
    if since is not None:
        command += ' -s {0}'.format(since)
    # run command
    os.system(command)
    # check that file created
    if not os.path.exists(filename):
        WLOG(p, 'error', 'Error with gcg (see above)')


def get_last_entry(filename):
    # check if we have a file
    if not os.path.exists(filename):
        return None
    else:
        # open file
        f = open(filename, 'r')
        # read file content
        lines = f.readlines()
        # close file
        f.close()
        # get last commit
        last_commit = None
        for line in lines:
            if '(rev.' in line:
                last_commit = line.split('rev.')[-1].split(')')[0]
                break
        # return last commit
        return last_commit


def add_to_full(fullfilename, tmpfilename):
    if not os.path.exists(fullfilename):
        fulllines = ['\n\n\nEnd of Changelog.']
    else:
        # open full file
        full = open(fullfilename, 'r')
        # get full lines
        fulllines = full.readlines()
        # close full file
        full.close()
        # delete full file
        os.remove(fullfilename)

    # open tmp file
    tmp = open(tmpfilename, 'r')
    # get tmp lines
    tmplines = tmp.readlines()
    # close tmp file
    tmp.close()
    # delete tmp file
    os.remove(tmpfilename)

    # append in correct order (tmp first then full with a separator)
    if len(tmplines) == 0:
        all_lines = list(fulllines)
    else:
        all_lines = fulllines + ['\n', '\n', '\n'] + tmplines
    # open full file
    full = open(fullfilename, 'w')
    # add tmp lines to full
    full.writelines(all_lines)
    # close full file
    full.close()


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # get values from config file
    p = spirouStartup.Begin(recipe=__NAME__, quiet=True)

    # get the absolute path
    path = spirouConfig.GetAbsFolderPath(CONSTANTS.PACKAGE(), PATH)
    # get the version
    drs_version = p['DRS_VERSION']
    # get the last entry
    last_entry = get_last_entry(FILENAME)
    # get the change log
    WLOG('', p['RECIPE'], 'Creating changelog')
    update(p, TMPFILENAME, path, kind='rpm', version=drs_version,
           since=last_entry)
    # now append to full changelog (do not overwrite contents)
    WLOG('', p['RECIPE'], 'Saving change log to file {0}'.format(FILENAME))
    add_to_full(FILENAME, TMPFILENAME)

# =============================================================================
# End of code
# =============================================================================
