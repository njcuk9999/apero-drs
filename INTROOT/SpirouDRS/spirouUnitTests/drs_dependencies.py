#!/usr/bin/env python3
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

# =============================================================================
# Define variables
# =============================================================================
DRSPATH = pkg_resources.resource_filename('SpirouDRS', '')
PATH = os.path.dirname(DRSPATH)

# -----------------------------------------------------------------------------
# path strings to exclude
EXCLUDE_PATH_STR = ['/spirouUnitTests/', '/documentation/', '/man/']
# dependencies to exclude
EXCLUDE_MOD_STR = ['SpirouDRS', 'spirou']

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

def get_import_statements(files):
    imports = []

    stats = dict()
    stats['total lines'] = 0
    stats['total empty lines'] = 0
    stats['total lines of comments'] = 0
    stats['total lines of code'] = 0

    info = dict()
    info['imports'] = []
    info['filename'] = []
    # loop around the files
    for filename in files:
        # open this iterations file
        f = open(filename)
        # read all lines from this iteration
        lines = f.readlines()
        stats['total lines'] += len(lines)
        # loop around the lines of code in this file
        docstring_skip = False
        for line in lines:
            # skip if in doc string
            docstring_skip = deal_with_doc_strings(line, docstring_skip)
            if docstring_skip:
                # print('\tSkip doc string')
                stats['total lines of comments'] += 1
                continue
            # blank lines should not count
            if len(line.strip()) == 0:
                stats['total empty lines'] += 1
                continue
            # commented lines should not count
            elif line.strip()[0] == '#':
                stats['total lines of comments'] += 1
                continue
            else:
                stats['total lines of code'] += 1
            # filter any lines with excluded strings in
            excluded = False
            for ext in EXCLUDE_MOD_STR:
                if ext in line:
                    excluded = True
            # line must have import and not be excluded
            if 'import' in line and not excluded:
                imports.append(line.replace('\n', ''))
                info['imports'].append(line.replace('\n', ''))
                info['filename'].append(filename)
                # print('\tWritten...')
    # return
    return imports, stats, info


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
    imports = []
    for uimport in uimports:
        # strip down uimport
        usimport = uimport.strip()
        # strip out import and from statements
        if usimport.startswith('import'):
            module = uimport.split('import ')[1]
        elif usimport.startswith('from'):
            module = uimport.split('from ')[1].split(' import')[0]
        # deal with . (only want main module)
        if '.' in module:
            module = module.split('.')[0]
        # deal with 'as'
        if 'as' in module:
            module = module.split(' as')[0]
        # make sure we only have one version in final list
        if module not in imports:
            imports.append(module.strip())
    # return cleaned imports
    return imports


# get current versions
def get_current_versions(imports):
    versions = []
    for imp in imports:
        try:
            mod = __import__(imp)
            if hasattr(mod, '__version__'):
                versions.append(mod.__version__)
            else:
                versions.append('No version info')
        except ImportError:
            versions.append('NOT INSTALLED')
    return versions

# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # get all python files
    print('\n Getting python files')
    python_files = get_python_files(PATH)
    # get all import statements
    print('\n Getting import statements')
    rimports, stats, info = get_import_statements(python_files)
    # clean imports
    imports = clean_imports(rimports)
    # get versions
    versions = get_current_versions(imports)
    # print total number of lines
    print('\nStats:')
    for stat in stats:
        print('\t{0}: {1}'.format(stat, stats[stat]))
    # print import statements
    print('\n Import statements found are: \n\n')
    for it in range(len(imports)):
        args = [imports[it], versions[it]]
        if versions[it] is not None:
            print('\t{0: <16}({1})'.format(*args))
        else:
            print('\t{0}'.format(*args))



# =============================================================================
# End of code
# =============================================================================
