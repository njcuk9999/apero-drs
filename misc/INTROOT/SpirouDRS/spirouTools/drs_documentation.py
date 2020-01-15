#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-04-23 at 14:55

@author: cook
"""
from __future__ import division
import numpy as np
import os
from collections import OrderedDict

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouStartup

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'drs_documentation.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# get package name
PACKAGE = spirouConfig.Constants.PACKAGE()
# -----------------------------------------------------------------------------
DOC_PATH = ('/scratch/Projects/spirou/drs/spirou_github/spirou_dev/'
            'misc/INTROOT/documentation/')
# -----------------------------------------------------------------------------
MOD_PATH = DOC_PATH + 'Chapters/modules/'
CAL_PATH = DOC_PATH + 'Chapters/recipes/'
VARB_PATH = DOC_PATH + 'Chapters/Variables.tex'
SPECIAL_CHARS = ['\\', '/', '{', '}', '(', ')']


# =============================================================================
# Define user functions
# =============================================================================
def list_modules(return_values=False):
    """
    Lists the modules defined in the DRS and descriped in the documentation

    :return None:
    """
    # setup
    p = set_up()
    # get files
    files = os.listdir(MOD_PATH)
    # log progress
    WLOG(p, '', 'Modules described in tex:')
    # print modules from tex files
    files = np.sort(files)
    mods = []
    for f in files:
        modname = f.split('.tex')[0]
        WLOG(p, '', '\t\t- {0}'.format(modname))
        mods.append(modname)
    # log progress
    WLOG(p, '', 'Modules in {0}'.format(PACKAGE))
    # get modules from package
    imp = __import__(PACKAGE)
    for f in imp.__all__:
        WLOG(p, '', '\t\t- {0}'.format(f))

    if return_values:
        return mods


def list_recipes():
    """
    Lists the recipes defined in the DRS and described in the documentation

    :return None:
    """
    # setup
    p = set_up()
    # get files
    files = os.listdir(CAL_PATH)
    # log progress
    WLOG(p, '', 'Recipes described in tex:')
    # print modules from tex files
    files = np.sort(files)
    for f in files:
        WLOG(p, '', '\t\t- {0}'.format(f.split('.tex')[0]))
    # get recipes path
    package_path = __import__(PACKAGE).__file__
    root = os.path.dirname(os.path.dirname(package_path))
    binfolder = os.path.join(root, 'bin')
    # log progress
    WLOG(p, '', 'Recipes in {0}'.format(binfolder))
    # get recipes from bin folder
    if os.path.exists(binfolder):
        files = np.sort(os.listdir(binfolder))
        for f in files:
            # ignore pyc files
            if '.pyc' in f:
                continue
            # only count .py files
            if '.py' in f:
                WLOG(p, '', '\t\t- {0}'.format(f))
    else:
        WLOG(p, 'error', 'Bin folder = {0} does not exist'
                                    ''.format(binfolder))


def list_variables():
    """
    Lists the variables defined in the DRS config files

    :return None:
    """
    # setup
    p = set_up()
    # read file
    lines = read_file(p, VARB_PATH)
    # log progress
    WLOG(p, '', 'Finding missing variables')
    WLOG(p, '', '    from {0}'.format(VARB_PATH))
    # get text variables from latex file
    text_variables = tex_id_variables(lines)
    # compare text_variables to p
    missing_variables = []
    found_variables = []
    for const in list(p.keys()):
        if const.upper() not in list(text_variables):
            missing_variables.append(const.upper())
        else:
            found_variables.append(const.upper())
    # print table
    WLOG(p, '', 'Variables: ')
    fmt = '{0:5s}{1:40s}{2:10s}{3:10s}'
    WLOG(p, '', '=' * 80)
    args = ['NUM', 'NAME', 'In .py', 'In .tex']
    WLOG(p, '', fmt.format(*args) + 'Where')
    WLOG(p, '', '=' * 80)
    count = 1
    for var in found_variables:
        if p.sources[var] is None:
            f = 'None'
        else:
            f = os.path.basename(p.sources[var])
        WLOG(p, '', fmt.format(str(count), var, 'x', 'x') + f)
        count += 1
    for var in missing_variables:
        if p.sources[var] is None:
            f = 'None'
        else:
            f = os.path.basename(p.sources[var])
        WLOG(p, 'warning', fmt.format(str(count), var, 'x', '') + f)
        count += 1

    # print end
    end(p)


def find_all_missing_modules():

    # setup
    p = set_up()

    ll = list_modules(return_values=True)

    missing = OrderedDict()

    for mod in ll:
        try:
            mll = find_missing_module_functions(mod, return_values=True)
            missing[mod] = list(mll)
        except SystemExit:
            print('Skipping {0}'.format(mod))

    # print all missing
    WLOG(p, '', '')
    WLOG(p, '', 'List of all missing: ')
    WLOG(p, '', '')
    for mod in missing:
        if len(missing[mod]) == 0:
            continue
        WLOG(p, '', '\t{0}'.format(mod))
        for mll in missing[mod]:
            WLOG(p, '', '\t\t- {0}'.format(mll))


def find_missing_module_functions(module_name, return_values=False):
    """
    Looks for missing functions (that are in __init__ file of module) but not
    in module_name.tex (as a subsection)

    :param module_name: string, the name of the module in the DRS to check

    :param return_values: bool, if True returns the missing functions

    :return None:
    """
    # setup
    p = set_up()
    # read file
    filename = MOD_PATH + '/{0}.tex'.format(module_name)
    lines = read_file(p, filename)
    # get functions from latex file
    WLOG(p, '', 'Finding missing functions in {0}'
                           ''.format(module_name))
    WLOG(p, '', '    from {0}'.format(filename))
    functions = tex_id_functions(lines)
    # get functions from __init__ file
    WLOG(p, '', 'Finding functions in {0}.__init__.py'
                           ''.format(module_name))
    dfunctions = init_id_functions(p, module_name).__all__
    # compare functions to dfunctions
    missing_funcs = []
    for func in dfunctions:
        if func not in functions:
            missing_funcs.append(func)
    # print results
    if len(missing_funcs) == 0:
        WLOG(p, '', 'Congratulations there are no missing functions '
                               'in {0}'.format(module_name))
    else:
        if len(missing_funcs) > 1:
            wmsg = 'There are {0} missing function in {1}'
            wargs = [module_name, len(missing_funcs)]
            WLOG(p, 'warning', wmsg.format(*wargs))
        else:
            wmsg = 'There is 1 missing variable in {0}'
            WLOG(p, 'warning', wmsg.format(module_name))

        WLOG(p, 'warning', 'Missing functions(s) are as follows:')
        for missing_varb in missing_funcs:
            WLOG(p, 'warning', '\t{0}'.format(missing_varb))

        wmsg = 'Please add to "{0}.tex"'
        WLOG(p, 'warning', wmsg.format(module_name))
    # print end
    end(p)

    if return_values:
        return missing_funcs


def find_missing_variables():
    """
    Find the missing variables in the .tex file compared to the what is loaded
    into the parameter dictionary at run time "p"

    The .tex file is search for the phrase "% VARIABLE_NAME and matched to
    "VARIABLE_NAME" in "p" (i.e. p['VARIABLE_NAME'])

    :return None:
    """
    # setup
    p = set_up()
    # read file
    lines = read_file(p, VARB_PATH)
    # log progress
    WLOG(p, '', 'Finding missing variables')
    WLOG(p, '', '    from {0}'.format(VARB_PATH))
    # get text variables from latex file
    text_variables = tex_id_variables(lines)

    # compare text_variables to p
    missing_variables = []
    for const in list(p.keys()):
        if const.upper() not in list(text_variables):
            missing_variables.append(const.upper())

    # print results
    if len(missing_variables) == 0:
        WLOG(p, '', 'Congratulations there are no missing variables')
    else:
        if len(missing_variables) > 1:
            WLOG(p, 'warning', 'There are {0} missing variables'
                 ''.format(len(missing_variables)))
        else:
            WLOG(p, 'warning', 'There is 1 missing variable')

        WLOG(p, 'warning', 'Missing variable(s) are as follows:')
        for missing_varb in missing_variables:
            WLOG(p, 'warning', '\t{0}'.format(missing_varb))
        WLOG(p, 'warning', 'Please add to "Variables.tex"')

    # print end
    end(p)


def print_docstrings(module_name):
    """
    Prints all doc strings in the DRS modules '__all__' variable

    :param module_name: string, the module name in the DRS

    :return None:
    """
    # setup
    p = set_up()
    # log progress
    WLOG(p, '', 'Finding functions in {0}.__init__.py'.format(module_name))
    # get functions from __init__ file
    imp = init_id_functions(p, module_name)

    # list modules
    fullpath = '{0}.{1}'.format(PACKAGE, module_name)
    # loop around modules
    for funcname in list(imp.__all__):
        args = ['='*74, '{0}.{1}'.format(fullpath, funcname)]
        print('\n{0}\n\t{1}\n{0}\n'.format(*args))
        # import func
        func = getattr(imp, funcname)
        if hasattr(func, '__doc__'):
            print(func.__doc__)
        else:
            print('No doc string found.')

    print('\n\n')
    # print end
    end(p)


# =============================================================================
# Define worker functions
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


def end(p):
    """
    The standard end message as with all other DRS recipes.

    :param p: parameter dictionary, ParamDict containing constants
            Must contain at least:
                log_opt: string, log option, normally the program name

    :return None:
    """
    # End Message
    wmsg = 'Recipe {0} has been successfully completed'
    WLOG(p, 'info', wmsg.format(p['LOG_OPT']))


def read_file(p, filename):
    """
    Read a text (or latex) file using open and readlines

    :param filename: string, filename to be read

    :return lines: list of strings (one string per line)
    """
    func_name = __NAME__ + '.read_file()'
    # open file
    # noinspection PyPep8,PyBroadException
    try:
        f = open(filename, 'r')
    except:
        emsg1 = 'Cannot open filename={0}'.format(filename)
        emsg2 = '    function={0}'.format(func_name)
        WLOG(p, 'error', [emsg1, emsg2])
        f = None
    # read lines
    lines = f.readlines()
    # cloase
    f.close()
    # return lines as list
    return lines


def tex_id_variables(lines):
    """
    Search a list of strings for valid variables

    Looking for "% VARIABLE_NAME" in a line and nothing else

    :param lines: list of strings, the list of strings to search

    :return text_variables: list of strings, the variables found
    """
    # looking at comments only (variables should have the varb name as a
    #   comment) filter out bad lines and keep first word of good lines
    text_variables = []
    for line in lines:
        line = line.strip().replace('\n', '')
        if len(line) == 0:
            continue
        if line[0] == '%' and '%%' not in line:
            # don't keep anything with special chars in
            good = True
            for char in SPECIAL_CHARS:
                if char in line:
                    good = False
            if not good:
                continue
            # only keep the fisrt word after the first %
            key = (line[1:].split()[0]).upper()
            text_variables.append(key)
    return text_variables


def tex_id_functions(lines):
    """
    Search a list of strings for functions

    Looking for "\substring{FUNCTION_NAME}" in a line and nothing else

    :param lines: list of strings, the list of strings to search

    :return functions: list of strings, the functions found
    """
    # looking at lines beginning with \subsection only
    #    (each Function should have a subsection)
    functions = []
    for line in lines:
        line = line.strip().replace('\n', '')
        if len(line) == 0:
            continue
        # condition for good line
        cond1 = line.startswith('\\subsection')
        cond2 = ('{' in line) and ('}' in line)
        cond3 = line.endswith('}')
        if cond1 and cond2 and cond3:
            key = line.split('}')[0].split('{')[1]
            if len(key) != 0:
                functions.append(key)
    return functions


def init_id_functions(p, module_name):
    """
    Import the string "module_name" from pacakge PACKAGE
    (i.e. same as import PACKAGE.module_name

    :param module_name: string, the module in the DRS

    :return imp: python import instance (PACKAGE.module_name)
    """
    # import module
    fullpath = '{0}.{1}'.format(PACKAGE, module_name)
    # noinspection PyPep8,PyBroadException
    try:
        imp = __import__(fullpath, fromlist=[''])
    except:
        WLOG(p, 'error', 'Module = {0} not found'.format(fullpath))
        imp = None
    if hasattr(imp, '__all__'):
        return imp
    else:
        WLOG(p, 'error', 'Module = {0} does not have __ALL__ property and '
                      'cannot be checked for functions')


# =============================================================================
# End of code
# =============================================================================
