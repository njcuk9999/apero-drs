#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-10-29 at 10:16

@author: cook
"""
import argparse
import os
import string
from typing import Optional

from aperocore.constants import param_functions
from aperocore.constants import load_functions
from aperocore.core import drs_log
from aperocore.core import drs_text

from aperotest.core import base
from aperotest.constants import constants

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'aperotest.recipes.run.py'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__
# get parameter dictionary
ParamDict = param_functions.ParamDict
# get the logger
WLOG = drs_log.wlog
# Define paths to create
PATHS = ['DATA_PATH', 'PLOT_PATH']


# =============================================================================
# Define functions
# =============================================================================
def get_params(yaml_file: Optional[str] = None,
               description: str = None,
               yaml_required: bool = True,
               from_file: bool = True,
               name: Optional[str] = None) -> ParamDict:
    """
    Get the parameters (default, command line and function call)

    :param yaml_file:
    :param description:
    :param yaml_required:
    :param from_file:
    :return:
    """
    # get the default arguments
    params = load_functions.load_parameters([constants.CDict])
    # set name
    if name is not None:
        params['RECIPE_SHORT'] = name
    # get the yaml file
    yaml_file = command_line_args(description=description,
                                  yaml_required=yaml_required,
                                  yaml_file=yaml_file)
    # get constants from user config files
    if from_file:
        # get instrument user config files
        largs = [[os.path.realpath(yaml_file)], params.instances]
        # load keys, values, sources and instances from yaml files
        ovalues, osources, oinstances = load_functions.load_from_yaml(*largs)
        # add to params
        for key in ovalues:
            # set value
            params[key] = ovalues[key]
            # set instance (Const/Keyword instance)
            params.set_instance(key, oinstances[key])
            params.set_source(key, osources[key])

    # set the yaml file
    params['GLOBAL']['YAML_FILE'] = yaml_file

    # make sure we have the minimal log parameters from wlog
    params = WLOG.minimal_params(params)

    # return params
    return params


def command_line_args(description: str = None,
                      yaml_required: bool = True,
                      yaml_file: Optional[str] = None) -> str:
    """
    Get the yaml file from the command line

    :param description: str, the description of the command line arguments
    :param yaml_required: bool, if True the yaml file is required and raises an
                            exception if it does not exist
    :param yaml_file: str or None, pre-set the yaml file name
                      (if None will check command line)
    :return:
    """
    # deal with pre-set yaml file (from function call)
    if yaml_file is not None:
        if yaml_required:
            # deal with no yaml file existing
            if not os.path.exists(yaml_file):
                # raise exception
                emsg = 'Yaml file does not exist: {0}'
                eargs = [yaml_file]
                raise base.SCARVSException(emsg.format(*eargs))
        # make sure yaml file is a string
        if isinstance(yaml_file, str):
            return yaml_file
    # -------------------------------------------------------------------------
    # setup argument parser
    parser = argparse.ArgumentParser(description=description)
    # add yaml file argument (depends on whether the yaml file is required)
    parser.add_argument('yaml_file', type=str, help='yaml file to load',
                            nargs='?', default='None')
    # parse arguments
    args = parser.parse_args()
    # -------------------------------------------------------------------------
    # deal with no yaml file set from function call or command line arguments
    # -------------------------------------------------------------------------
    if args.yaml_file == 'None':
        question = '\nPlease enter the yaml file to load:\t'
        # we always go into here
        while True:
            # ask the user for a yaml file
            yaml_file = input(question)
            # deal with yaml file being required
            if yaml_required:
                # yaml file must end in .yaml
                if not yaml_file.endswith('.yaml'):
                    yaml_file += '.yaml'
                # deal with no yaml file existing
                if not os.path.exists(yaml_file):
                    # raise exception
                    emsg = 'Yaml file does not exist: {0}'
                    eargs = [yaml_file]
                    print(emsg.format(*eargs))
                    continue
            # yaml file cannot have spaces
            if ' ' in yaml_file:
                emsg = 'Yaml file cannot have spaces in the name'
                print(emsg)
                continue
            # replace all punctuation with underscores
            for char in string.punctuation.replace('.', ''):
                yaml_file = yaml_file.replace(char, '_')
            # replace double underscores with single underscores
            while '__' in yaml_file:
                yaml_file = yaml_file.replace('__', '_')
            # yaml must have characters
            if len(yaml_file) <= 4:
                emsg = ('Yaml file must be longer than 4 characters and '
                        'only contain letters, numbers and underscores')
                print(emsg)
                continue
            # break loop
            break
        # yaml file must end in .yaml
        if not yaml_file.endswith('.yaml'):
            yaml_file += '.yaml'
    else:
        yaml_file = args.yaml_file
    # -------------------------------------------------------------------------
    # deal with no yaml file
    if yaml_required:
        # deal with no yaml file existing
        if not os.path.exists(yaml_file):
            # raise exception
            emsg = 'Yaml file does not exist: {0}'
            eargs = [yaml_file]
            raise base.SCARVSException(emsg.format(*eargs))
    # return the yaml file
    return yaml_file



def setup(params: ParamDict):
    """
    Setup the general module

    :return: None
    """
    # print progress
    WLOG(params, 'info', params['DRS_HEADER'])
    WLOG(params, 'info', 'Checking arguments')
    WLOG(params, 'info', params['DRS_HEADER'])
    # ask user for any missing arguments
    params = ask_user_for_missing_arguments(params)
    # ----------------------------------------------------------------------
    # print progress
    WLOG(params, 'info', params['DRS_HEADER'])
    WLOG(params, 'info', 'Checking paths')
    WLOG(params, 'info', params['DRS_HEADER'])
    # Create some paths
    for path in PATHS:
        # deal with path not existing in params (skip) - these really should
        #    exist though
        if path not in params:
            continue
        # convert path to a real absolute path
        params[path] = os.path.abspath(params[path])
        # find if path exists
        if os.path.exists(params[path]):
            WLOG(params, '', 'Path exists: {0}'.format(params[path]))
            continue
        # ask user to create path
        question = '\nPath does not exist: {0}\nWould you like to create it?'
        question = question.format(params[path])
        # ask user
        if drs_text.user_input(question, dtype='YN', required=True):
            os.makedirs(params[path])
    # ----------------------------------------------------------------------
    # print progress
    WLOG(params, 'info', params['DRS_HEADER'])
    WLOG(params, 'info', 'Constructing yaml file')
    WLOG(params, 'info', params['DRS_HEADER'])
    # Get the constants dictionary
    cdict = constants.CDict
    # get the yaml file
    yaml_file = params['GLOBAL']['YAML_FILE']
    # print progress
    msg = 'Saving constants to yaml file: {0}'
    WLOG(params, '', msg.format(os.path.realpath(yaml_file)))
    # save the constants dictionary to yaml file
    cdict.save_yaml(params, outpath=yaml_file, log=False)


def ask_user_for_missing_arguments(params: ParamDict):
    """
    Ask the user for any missing arguments

    :param params: ParamDict, the parameter dictionary
    :return: ParamDict, the updated parameter dictionary
    """
    # set function name
    func_name = __NAME__ + '.ask_user_for_missing_arguments()'
    # set up parameters that are required and currently None in parameters
    for key in params:
        # skip if value is not None
        if params[key] is not None:
            continue
        # get the parameter constant instance
        instance = params.instances[key]

        # see if we have to ask the user for this value
        if instance.not_none:
            # loop until we get a valid response from the user
            while True:
                question = '\nPlease enter the value for {0}'.format(key)
                # loop and ask
                value = drs_text.user_input(question, dtype=instance.dtype,
                                            options=instance.options,
                                            required=True)
                # validate value
                try:
                    value = instance.validate(test_value=value)
                except Exception as e:
                    print('Error: {0}'.format(e))
                    continue
                # if we get here the value is good
                break
            # set the value and source
            params.set(key, value, source=func_name)
    # return parameters
    return params


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
