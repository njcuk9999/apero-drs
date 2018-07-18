#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-07-04 at 11:44

@author: cook
"""
from __future__ import division
import numpy as np
import sys
import os
from datetime import datetime

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
TMPFILENAME2 = 'CHANGELOGLINE.tmp'
VERSIONFILE = os.path.join(PATH, 'VERSION.txt')
REVKEY = '(rev.'

rargs = [CONSTANTS.PACKAGE(), './spirouConfig']
CONSTPATH = spirouConfig.spirouConfigFile.get_relative_folder(*rargs)
CONSTFILE = os.path.join(CONSTPATH, 'spirouConst.py')

VERSIONSTR = '__version__ = '
DATESTR = '__date__ = '

# =============================================================================
# Define functions
# =============================================================================
def update(filename, path, kind='rpm', version=None, since=None, until=None):
    # get default run
    cargs = [path, filename]
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
    # add until if needed
    if until is not None:
        command += ' -u {0}'.format(until)
    # run command
    os.system(command)
    # check that file created
    if not os.path.exists(filename):
        WLOG('error', __NAME__.split('.py')[0], 'Error with gcg (see above)')


def process_lines(fullfilename, tmpfilename, path, kind='rpm', version=None):

    # read log
    f = open(tmpfilename, 'r')
    # read lines
    tmplines = f.readlines()
    # close file
    f.close()
    os.remove(tmpfilename)

    # read full file
    if not os.path.exists(fullfilename):
        fulllines = []
    else:
        g = open(fullfilename, 'r')
        fulllines = g.readlines()
        g.close()
        os.remove(fullfilename)

    # get full list of revkeys
    fullreferences = get_references(fulllines)

    # log process
    WLOG('', __NAME__, 'Getting references')

    # filter unwanted lines
    tmplines2 = []
    for tmpline in tmplines:
        # filter out all lines without the revision key
        if REVKEY not in tmpline:
            continue
        else:
            tmplines2.append(tmpline)

    # for each line we need the line before and after
    references = []
    for it in range(len(tmplines2)):
        reference = get_reference(tmplines2[it])
        # if reference in fullreferences skip
        if reference in fullreferences:
            continue
        # else get the reference after
        if it == 0:
            after = None
        else:
            after = get_reference(tmplines2[it - 1])
        # and get the reference before
        if it == len(tmplines2) - 1:
            before = None
        else:
            before = get_reference(tmplines2[it + 1])
        # finally append the before and after (to locate it)
        references.append([before, after])

    # set the tmp filename
    tmpfilename2 = 'tmp_' + tmpfilename
    # set up storage
    entry_storage = dict()
    date_storage = dict()
    # for each reference get the date
    for it, reference in enumerate(references):
        # print progress
        wargs = [it + 1, len(references)]
        WLOG('', __NAME__, 'Processing commit {0} of {1}'.format(*wargs))
        # get entry
        update(tmpfilename2, path, since=reference[0], until=reference[1],
               kind=kind, version=version)
        # check we have tmpfile
        if not os.path.exists(tmpfilename2):
            continue
        # read the tmp file
        f = open(tmpfilename2)
        # get the lines
        tmplines = f.readlines()
        # close and delete the file
        f.close()
        os.remove(tmpfilename2)

        # line 0 should be the date
        # line 1 should be the entry
        key = tmplines[0]
        entry = tmplines[1]
        # add tab to entries
        entry = '\t' + entry
        # try to get date from key
        date = get_date(key)
        # add the dictionary
        if key in entry_storage:
            if entry not in entry_storage[key]:
                entry_storage[key].append(entry)
                date_storage[key] = date
        else:
            entry_storage[key] = [entry]
            date_storage[key] = date

    # get unique dates
    dates = np.unique(list(date_storage.values()))

    # now we have our entries need to recombine into a single list (sorted by
    #    date_storage values)
    newlines = fulllines

    # loop around dates
    for it, date in enumerate(dates):
        # print progress
        # print progress
        wargs = [it + 1, len(dates)]
        WLOG('', __NAME__, 'Processing day {0} of {1}'.format(*wargs))
        # loop around keys
        for key in entry_storage:
            # check we have date
            if date in date_storage[key]:
                # append header
                newlines.append('\n\n\n' + '=' * 80 + '\n')
                newlines.append(key + '\n' + '=' * 80 + '\n')
                # append lines
                for newline in entry_storage[key]:
                    newlines.append(newline)

    # finally write newlines to file
    WLOG('', __NAME__, 'Writing to file {0}'.format(fullfilename))
    f = open(fullfilename, 'w')
    f.writelines(newlines)
    f.close()


def get_reference(line):
    reference = line.split(REVKEY)[-1]
    reference = reference.split(')')[0]
    return reference


def get_references(lines):
    references = []
    for line in lines:
        if REVKEY in line:
            references.append(get_reference(line))
    return references


def get_date(key):
    fmt = '%a %b %d %Y'
    dt = datetime.strptime(key[2:17], fmt)
    return '{0:04d}-{1:02d}-{2:02d}'.format(dt.year, dt.month, dt.day)


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
        # reverse lines
        lines = lines[::-1]
        # get last commit
        last_commit = None
        for line in lines:
            if REVKEY in line:
                last_commit = line.split('rev.')[-1].split(')')[0]
                break
        # return last commit
        return last_commit


def update_version_file(filename, version):
    # read file and delete
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()
    os.remove(filename)
    # edit first line
    lines[0] = 'DRS_VERSION = {0}\n'.format(version)
    # write file and save
    f = open(filename, 'w')
    f.writelines(lines)
    f.close()


def update_py_version(filename, version):
    # read const file
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()
    # find version and date to change
    version_it, date_it = None, None
    for it, line in enumerate(lines):
        if line.startswith(VERSIONSTR):
            version_it = it
        if line.startswith(DATESTR):
            date_it = it
    # while loop for user input
    cond = True
    uinput1 = None
    while cond:
        # ask to update version
        print('Current version is "{0}"'.format(version))
        print('New version [Y]es or [N]o?')
        # deal with python 2 / python 3 input method
        if sys.version_info.major < 3:
            # noinspection PyUnresolvedReferences
            uinput = raw_input('\t>> ')      # note python 3 wont find this!
        else:
            uinput = input('\t>> ')

        # deal with version input
        if 'Y' in uinput.upper():
            print('\nEnter new version number:')
            if sys.version_info.major < 3:
                # noinspection PyUnresolvedReferences
                uinput1 = raw_input('\t>> ')    # note python 3 wont find this!
            else:
                uinput1 = input('\t>> ')
                print('\nNew version is "{0}"'.format(uinput1))
            print('Accept version [Y]es or [N]o?')
            if sys.version_info.major < 3:
                # noinspection PyUnresolvedReferences
                uinput2 = raw_input('\t>> ')    # note python 3 wont find this!
            else:
                uinput2 = input('\t>> ')
            if 'Y' in uinput2.upper():
                cond = False
        else:
            cond = False
            uinput1 = None

    if uinput1 is not None:
        # update version
        lines[version_it] = '{0} \'{1}\'\n'.format(VERSIONSTR, uinput1)
        # update date
        dt = datetime.now()
        dargs = [DATESTR, dt.year, dt.month, dt.day]
        lines[date_it] = '{0} \'{1:04d}-{2:02d}-{3:02d}\'\n'.format(*dargs)
        # write lines
        f = open(filename, 'w')
        f.writelines(lines)
        f.close()
        # update version number
        version = uinput1
    # return version
    return version


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # get values from config file
    p = spirouStartup.Begin(recipe=__NAME__, quiet=True)
    # get the version
    version = p['DRS_VERSION']
    # update version text file
    update_version_file(VERSIONFILE, version)
    # increment version in config files
    version = update_py_version(CONSTFILE, version)
    # check full log file for previous entries
    since = get_last_entry(FILENAME)
    # log if not None
    if since is not None:
        wmsg = 'Found previous entries: starting from Commit {0}'
        WLOG('', __NAME__, wmsg.format(since))
    # get full log
    WLOG('', __NAME__, 'Getting full commit log')
    update(TMPFILENAME, PATH, kind='rpm', version=version, since=since)
    # get lines group them and save to full file
    process_lines(FILENAME, TMPFILENAME, PATH, kind='rpm', version=version)


# =============================================================================
# End of code
# =============================================================================
