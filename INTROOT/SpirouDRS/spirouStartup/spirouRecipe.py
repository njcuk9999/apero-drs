#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-09-14 at 18:19

@author: cook
"""
import argparse
import os

from SpirouDRS import spirouCore

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'cal_preprocess_spirou.py'
# Get Logging function
WLOG = spirouCore.wlog
# -----------------------------------------------------------------------------

# =============================================================================
# Define classes
# =============================================================================
# Adapted from: https://stackoverflow.com/a/16942165
class DRSArgumentParser(argparse.ArgumentParser):
    def __init__(self, drs_params, **kwargs):
        self.drs_params = drs_params
        argparse.ArgumentParser.__init__(self, **kwargs)

    def error(self, message):
        #self.print_help(sys.stderr)
        #self.exit(2, '%s: error: %s\n' % (self.prog, message))

        emsg1 = 'There was an error reading input arguments'
        emsg2 = ''
        emsg3 = self.format_help()
        emsg4 = 'Error was: {0}'.format(message)

        WLOG('error', '', [emsg1, emsg2, emsg3, emsg4])

    def _print_message(self, message, file=None):
        WLOG('', '', message)


class CheckDirectory(argparse.Action):
    def check_directory(self, directory, drs_params):

        if not os.path.exists(directory):
            emsg = 'Directory="{0}" does not exist'
            WLOG('error', '', emsg.format(directory))

        elif not os.path.isdir(directory):
            emsg = '"{0}" is not a valid directory'
            WLOG('error', '', emsg.format(directory))
        else:
            return directory

    def __call__(self, parser, namespace, values, option_string=None):

        # get drs parameters
        drs_params = parser.drs_params
        # check value
        if type(values) == list:
            directory = list(map(self.check_directory, values, drs_params))
        else:
            directory = str(self.check_directory(values, drs_params))
        # Add the attribute
        setattr(namespace, self.dest, directory)


class CheckInFile(argparse.Action):
    def check_in_file(self, filename):

        if not os.path.exists(filename):
            emsg = 'File="{0}" is not valid'
            WLOG('error', '', emsg.format(filename))

        else:
            emsg = 'File="{0}" is valid'
            WLOG('', '', emsg.format(filename))

        return filename

    def __call__(self, parser, namespace, values, option_string=None):
        if type(values) == list:
            files = list(map(self.check_in_file, values))
        else:
            files = self.check_in_file(values)
        # Add the attribute
        setattr(namespace, self.dest, files)


class CheckOutFile(argparse.Action):
    def check_in_file(self, filename):

        if not os.path.exists(filename):
            emsg = 'File="{0}" is not valid'
            WLOG('error', '', emsg.format(filename))

        else:
            emsg = 'File="{0}" is valid'
            WLOG('', '', emsg.format(filename))

        return filename

    def __call__(self, parser, namespace, values, option_string=None):
        if type(values) == list:
            files = list(map(self.check_in_file, values))
        else:
            files = self.check_in_file(values)
        # Add the attribute
        setattr(namespace, self.dest, files)


class CheckBool(argparse.Action):
    def check_bool(self, value):
        if str(value).lower() in ['yes', 'true', 't', 'y', '1']:
            return True
        elif str(value).lower() in ['no', 'false', 'f', 'n', '0']:
            return False
        else:
            emsg1 = 'Argument "{0}" must be a Boolean value (True/False)'
            WLOG('error', '', emsg1.format(self.dest))

    def __call__(self, parser, namespace, values, option_string=None):
        if type(values) == list:
            value = list(map(self.check_bool, values))
        else:
            value = self.check_bool(values)
        # Add the attribute
        setattr(namespace, self.dest, value)


class DrsRecipe:
    def __init__(self, name=None):
        # name
        if name is None:
            self.name = 'Unknown'
        else:
            self.name = name
        # output directory
        self.outputdir = 'reduced'
        # input directory
        self.inputdir = 'tmp'
        # input type (RAW/REDUCED)
        self.inputtype = 'raw'
        # recipe description
        self.description = 'No description defined'
        # run order
        self.run_order = None
        # define sets of arguments
        self.args = dict()
        self.kwargs = dict()
        # define arg list
        self.arg_list = []

    def arg(self, name=None, dtype=None, pos=0, default=None, helpstr=None,
            key=None, key1=None, key2=None, nargs=None):
        """
        Add an argument to the recipe

        :param name: string or None, the name and reference of the argument
        :param dtype: type or None, the type expected for the argument (will
                      raise error if not this type)
        :param pos: int, the expected position of the argument in the call to
                    the recipe or function
        :param helpstr: string or None, the help string related to this argument
        :return None:
        """
        # set name
        if name is None:
            name = 'Arg{0}'.format(len(self.args) + 1)
        if key is None:
            key = ''
        if key1 is None:
            key1 = ''
        if key2 is None:
            key2 = ''
        # arg list
        arglist = dict()
        arglist['name'] = name
        # set other properties
        arglist['dtype'] = dtype
        arglist['pos'] = pos
        arglist['default'] = default
        arglist['nargs'] = nargs
        arglist['helpstr'] = helpstr
        arglist['key'] = key
        arglist['key1'] = key1
        arglist['key2'] = key2
        # add to arg list
        if name not in self.args.keys():
            self.args[name] = [arglist]
        else:
            self.args[name].append(arglist)

    def kwarg(self, name=None, dtype=None, default=None, helpstr=None,
              key=None, key1=None, key2=None):
        """
        Add a keyword argument to the recipe

        :param name: string or None, the name and reference of the argument
        :param dtype: type or None, the type expected for the argument (will
                      raise error if not this type)
        :return None:
        """
        if name is None:
            name = 'kwarg{0}'.format(len(self.args) + 1)
        # set name
        if key is None:
            key = ''
        if key1 is None:
            key1 = ''
        if key2 is None:
            key2 = ''
        # arg list
        kwarglist = dict()
        kwarglist['name'] = name
        # set other properties
        kwarglist['dtype'] = dtype
        kwarglist['default'] = default
        kwarglist['helpstr'] = helpstr
        kwarglist['key'] = key
        kwarglist['key1'] = key1
        kwarglist['key2'] = key2
        # add to arg list
        self.kwargs[name] = kwarglist

    def make(self):
        self.arg_list = []
        # first process the arguments
        for argitem in self.args:
            argi = self.args[argitem][0]
            # get arg name
            name = argi['name'].replace(' ', '_')
            # get props
            props = get_arg_props(argi)
            # add to arg_list
            self.arg_list.append([name, props])
        # then add the keywrod arguments
        for argitem in self.kwargs:
            argi = self.kwargs[argitem]
            # get arg name
            dest = argi['name'].replace(' ', '_')
            # get props
            props = get_arg_props(argi)
            # add to arg_list
            self.arg_list.append([dest, props])


# =============================================================================
# Define functions
# =============================================================================
def get_arg_props(argi):
    """

    :param argi:
    :return:
    """
    props = dict()
    # deal with dtype
    dtype = argi['dtype']
    if dtype == 'infile':
        props['action'] = CheckInFile
        props['nargs'] = '+'
        props['type'] = str
    elif dtype == 'outfile':
        # props['action'] = 'check_outfile'
        props['nargs'] = '+'
        props['type'] = str
    elif dtype == 'directory':
        props['action'] = CheckDirectory
        props['nargs'] = 1
        props['type'] = str
    elif dtype == 'bool':
        props['action'] = CheckBool
        props['type'] = bool
    elif dtype=='switch':
        props['action'] = 'store_true'
    elif type(dtype) is type:
        props['type'] = dtype
        props['nargs'] = 1
    else:
        props['type'] = str
        props['nargs'] = 1
    # deal with default
    if argi['default'] is not None:
        props['default'] = argi['default']
    # deal with help string
    if argi['helpstr'] is None:
        props['help'] = ''
    else:
        props['help'] = argi['helpstr']
    # return the props dictionary
    return props

# =============================================================================
# End of code
# =============================================================================
