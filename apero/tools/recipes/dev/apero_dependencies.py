#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-11-27 at 13:58

@author: cook
"""
import numpy as np
import os
from collections import OrderedDict

from apero.base import base
from apero.core.core import drs_misc
from apero.core.core import drs_log
from apero.core.utils import drs_startup


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_dependencies.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
# --------------------------------------------------------------------------
# path strings to exclude
EXCLUDE_PATH_STR = []
# dependencies to exclude
EXCLUDE_MOD_STR = ['apero']
# debug mode
DEBUG = True


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
# Everything else is controlled from recipe_definition
def main(**kwargs):
    """
    Main function for apero_dependencies.py

    :param kwargs: any additional keywords

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(**kwargs)
    # ----------------------------------------------------------------------
    # deal with command line inputs / function call inputs
    recipe, params = drs_startup.setup(__NAME__, __INSTRUMENT__, fkwargs)
    # solid debug mode option
    if kwargs.get('DEBUG0000', False):
        return recipe, params
    # ----------------------------------------------------------------------
    # run main bulk of code (catching all errors)
    llmain, success = drs_startup.run(__main__, recipe, params)
    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    return drs_startup.end_main(params, llmain, recipe, success, outputs='None')


def __main__(recipe, params):
    # Note: no instrument defined so do not use instrument only features

    # ----------------------------------------------------------------------
    # define DRS path
    drs_path = drs_misc.get_relative_folder(params['DRS_PACKAGE'], '')
    # ----------------------------------------------------------------------
    # get all python files
    WLOG(params, '', 'Getting python files')
    python_files = get_python_files(drs_path)
    # get all import statements
    WLOG(params, '', 'Getting import statements')
    rimports, stats, info = get_import_statements(params, python_files)
    # clean imports
    imports = clean_imports(rimports)
    # get versions
    versions = get_current_versions(imports)
    # print total number of lines
    WLOG(params, '', '=' * 50)
    WLOG(params, '', 'Stats:')
    WLOG(params, '', '=' * 50)
    for stat in stats:
        WLOG(params, '', '\t{0}: {1}'.format(stat, stats[stat]))
    # print import statements
    WLOG(params, '', '=' * 50)
    WLOG(params, '', 'Import statements found are:')
    WLOG(params, '', '=' * 50)
    for it in range(len(imports)):
        args = [imports[it], versions[it]]
        if versions[it] is not None:
            WLOG(params, '', '\t{0: <16}({1})'.format(*args))
        else:
            WLOG(params, '', '\t{0}'.format(*args))
    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return drs_startup.return_locals(params, dict(locals()))


def get_python_files(path):
    pyfiles = []
    for path, dirs, files in os.walk(path, followlinks=True):
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
    return np.sort(pyfiles)


def get_import_statements(params, files):
    # get package list
    package = params['DRS_PACKAGE']
    # get import list
    importslist = []
    # populate stats dictionary
    statsdict = OrderedDict()
    statsdict['total lines'] = 0
    statsdict['total empty lines'] = 0
    statsdict['total lines of comments'] = 0
    statsdict['total lines of code'] = 0
    # second stats dictionary for per file stats
    statsdict2 = OrderedDict()
    # info dictionary
    infodict = OrderedDict()
    infodict['imports'] = []
    infodict['filename'] = []
    # loop around the files
    for filename in files:

        # read the lines
        with open(filename, 'r') as f:
            lines = f.readlines()
        # get the stats
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
            # get package path
            packagepath = drs_misc.get_relative_folder(package, '')
            # get relative path
            relfilename = filename.split(packagepath)[-1]
            # remove leading/trailing separators
            relfilename = relfilename.strip(os.sep)
            # add package to start
            relfilename = os.path.join(package, relfilename)
            # print total number of lines
            WLOG(params, '', '=' * 60)
            WLOG(params, '', 'Stats file={0}'.format(relfilename))
            WLOG(params, '', '=' * 60)
            stats = statsdict2[filename]
            for stat in stats:
                lines_of_code = stats['total lines of code']
                lines_of_comment = stats['total lines of comments']
                # yellow message if code > comments
                if lines_of_code > lines_of_comment:
                    WLOG(params, '', '\t{0}: {1}'.format(stat, stats[stat]),
                         colour='yellow')
                else:
                    WLOG(params, '', '\t{0}: {1}'.format(stat, stats[stat]))

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


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()

# =============================================================================
# End of code
# =============================================================================
