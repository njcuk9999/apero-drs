#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
drs_dependencies

Lists the dependencies the DRS currently has

Created on 2017-11-27 at 13:08

@author: cook
"""
import numpy as np
import os
import pkg_resources
from collections import OrderedDict

from SpirouDRS import spirouCore
from SpirouDRS import spirouStartup
from SpirouDRS import spirouConfig

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'drs_dependencies.py'
# define DRS path
DRSPATH = pkg_resources.resource_filename('SpirouDRS', '')
PATH = os.path.dirname(DRSPATH)
if PATH == '':
    PATH = DRSPATH
# Get Logging function
WLOG = spirouCore.wlog
# get print log
printl = spirouCore.PrintLog
# -----------------------------------------------------------------------------
# path strings to exclude
EXCLUDE_PATH_STR = ['/spirouUnitTests/', '/documentation/', '/man/',
                    '/spirouTools/', '/misc/', '/config/']
# dependencies to exclude
EXCLUDE_MOD_STR = ['SpirouDRS', 'spirou', 'obj_', 'cal_']
# debug mode
DEBUG = True


# =============================================================================
# Define functions
# =============================================================================
def get_python_files(path):
    pyfiles = []
    for path, dirs, files in os.walk(path):
        for filename in files:
            # set up abs path
            abspath = os.path.join(path, filename)
            # check for bad paths (excluded baths)
            badpath = False
            for exclude in EXCLUDE_PATH_STR:
                if exclude in abspath:
                    badpath = True
            if badpath:
                continue
            # make sure they are python files
            if '.py' in filename and '.pyc' not in filename:
                pyfiles.append(abspath)
    return pyfiles


def get_import_statements(p, files):
    importslist = []

    statsdict = OrderedDict()
    statsdict['total lines'] = 0
    statsdict['total empty lines'] = 0
    statsdict['total lines of comments'] = 0
    statsdict['total lines of code'] = 0

    statsdict2 = OrderedDict()

    infodict = OrderedDict()
    infodict['imports'] = []
    infodict['filename'] = []
    # loop around the files
    for filename in files:
        # open this iterations file
        f = open(filename)
        # read all lines from this iteration
        lines = f.readlines()

        statsdict['total lines'] += len(lines)
        statsdict2[filename] = OrderedDict()
        statsdict2[filename]['total lines'] = len(lines)
        statsdict2[filename]['total empty lines'] = 0
        statsdict2[filename]['total lines of comments'] = 0
        statsdict2[filename]['total lines of code'] = 0

        # loop around the lines of code in this file
        docstring_skip = False
        for line in lines:
            # skip if in doc string
            docstring_skip = deal_with_doc_strings(line, docstring_skip)
            if docstring_skip:
                # print('\tSkip doc string')
                statsdict['total lines of comments'] += 1
                statsdict2[filename]['total lines of comments'] += 1
                continue
            # blank lines should not count
            if len(line.strip()) == 0:
                statsdict['total empty lines'] += 1
                statsdict2[filename]['total empty lines'] += 1
                continue
            # commented lines should not count
            elif line.strip()[0] == '#':
                statsdict['total lines of comments'] += 1
                statsdict2[filename]['total lines of comments'] += 1
                continue
            else:
                statsdict['total lines of code'] += 1
                statsdict2[filename]['total lines of code'] += 1
                # filter any lines with excluded strings in
            excluded = False
            for ext in EXCLUDE_MOD_STR:
                if ext in line:
                    excluded = True
            # line must have import and not be excluded
            if 'import' in line and not excluded:
                importslist.append(line.replace('\n', ''))
                infodict['imports'].append(line.replace('\n', ''))
                infodict['filename'].append(filename)
                # print('\tWritten...')

        if DEBUG:
            # print total number of lines
            WLOG(p, '', '='*50)
            WLOG(p, '', 'Stats file={0}'.format(os.path.basename(filename)))
            WLOG(p, '', '=' * 50)
            stats = statsdict2[filename]
            for stat in stats:
                WLOG(p, '', '\t{0}: {1}'.format(stat, stats[stat]))

    # return
    return importslist, statsdict, infodict


def deal_with_doc_strings(line, docstring_skip):
    # find doc strings
    docstart = line.strip().startswith('\"\"\"')
    docstart |= line.strip().startswith('\'\'\'')
    docend = line.strip().endswith('\"\"\"')
    docend |= line.strip().endswith('\'\'\'')
    # need to deal with doc strings
    if docstart:
        # print('\tDoc string found')
        if docstring_skip is False:
            docstring_skip = True
        else:
            docstring_skip = False
    if (docstart & docend) & (len(line.strip()) != 3):
        docstring_skip = False
    return docstring_skip


def clean_imports(rawimports):

    # clean up (keep unique only)
    uimports = np.unique(rawimports)
    # loop around unique imports
    importslist = []
    for uimport in uimports:
        # strip down uimport
        usimport = uimport.strip()
        # strip out import and from statements
        if usimport.startswith('import '):
            modulename = uimport.split('import ')[1]
        # deal with from . import
        elif 'from .' in usimport:
            continue
        elif usimport.startswith('from '):
            modulename = uimport.split('from ')[1].split(' import')[0]
        else:
            continue
        # deal with . (only want main module)
        if '.' in modulename:
            modulename = modulename.split('.')[0]
        # deal with 'as'
        if 'as' in modulename:
            modulename = modulename.split(' as')[0]
        # make sure we only have one version in final list
        if modulename not in importslist:
            importslist.append(modulename.strip())
    # return cleaned imports
    return importslist


# get current versions
def get_current_versions(importslist):
    versionslist = []
    for imp in importslist:
        try:
            mod = __import__(imp)
            if hasattr(mod, '__version__'):
                versionslist.append(mod.__version__)
            else:
                versionslist.append('No version info')
        except ImportError:
            versionslist.append('NOT INSTALLED')
    return versionslist


def main(return_locals=False):
    # ----------------------------------------------------------------------
    # get p
    p = spirouStartup.Begin('None')
    p['RECIPE'] = __NAME__
    # title
    spirouStartup.DisplayTitle(p, ' * DRS Dependencies')
    # list the version of python found
    spirouStartup.DisplaySysInfo(p, logonly=False)
    # get all python files
    WLOG(p, '', 'Getting python files')
    python_files = get_python_files(PATH)
    # get all import statements
    WLOG(p, '', 'Getting import statements')
    rimports, stats, info = get_import_statements(p, python_files)
    # clean imports
    imports = clean_imports(rimports)
    # get versions
    versions = get_current_versions(imports)
    # print total number of lines
    WLOG(p, '', '=' * 50)
    WLOG(p, '', 'Stats:')
    WLOG(p, '', '=' * 50)
    for stat in stats:
        WLOG(p, '', '\t{0}: {1}'.format(stat, stats[stat]))
    # print import statements
    WLOG(p, '', '=' * 50)
    WLOG(p, '', 'Import statements found are:')
    WLOG(p, '', '=' * 50)
    for it in range(len(imports)):
        args = [imports[it], versions[it]]
        if versions[it] is not None:
            WLOG(p, '', '\t{0: <16}({1})'.format(*args))
        else:
            WLOG(p, '', '\t{0}'.format(*args))
    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    wmsg = 'Recipe {0} has been successfully completed'
    WLOG(p, 'info', wmsg.format(p['RECIPE']))
    # return a copy of locally defined variables in the memory
    if return_locals:
        return dict(locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main(return_locals=True)
    # exit message
    spirouStartup.Exit(ll, has_plots=False)

# =============================================================================
# End of code
# =============================================================================
