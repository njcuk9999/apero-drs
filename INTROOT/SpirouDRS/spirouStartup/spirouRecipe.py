#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-09-14 at 18:19

@author: cook
"""
from astropy.io import fits
import argparse
import os
import glob

from SpirouDRS import spirouCore
from SpirouDRS import spirouConfig


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'drs_recipe.py'
# Get Logging function
WLOG = spirouCore.wlog
# get print colours
BCOLOR = spirouConfig.Constants.BColors
# define hard display limit
HARD_DISPLAY_LIMIT = 99
# -----------------------------------------------------------------------------


# =============================================================================
# Define ArgParse Parser and Action classes
# =============================================================================
# Adapted from: https://stackoverflow.com/a/16942165
class DRSArgumentParser(argparse.ArgumentParser):
    def __init__(self, drs_params, **kwargs):
        self.drs_params = drs_params
        argparse.ArgumentParser.__init__(self, **kwargs)

    def error(self, message):
        #self.print_help(sys.stderr)
        #self.exit(2, '%s: error: %s\n' % (self.prog, message))

        # get parameterse from drs_params
        log_opt = self.drs_params['LOG_OPT']
        # construct error message
        underline = BCOLOR.UNDERLINE
        if self.drs_params['COLOURED_LOG']:
            red, end = BCOLOR.FAIL, BCOLOR.ENDC
            yellow, blue = BCOLOR.WARNING, BCOLOR.OKBLUE
        else:
            red, end = BCOLOR.ENDC, BCOLOR.ENDC
            yellow, blue = BCOLOR.ENDC, BCOLOR.ENDC
        # Manually print error message (with help)
        print()
        print(red + underline + 'Argument Error:' + end)
        print()
        print(BCOLOR.WARNING + message + end)
        print()
        print(blue + self.format_help() + end)
        # log message (without print)
        emsg1 = '\nArgument Error:'
        emsg2 = '\t {0}'.format(message)
        WLOG('error', log_opt, [emsg1, emsg2],
             logonly=True)



    def _print_message(self, message, file=None):
        # get parameterse from drs_params
        log_opt = self.drs_params['LOG_OPT']
        # construct error message
        underline = BCOLOR.UNDERLINE
        if self.drs_params['COLOURED_LOG']:
            green, end = BCOLOR.OKGREEN, BCOLOR.ENDC
            yellow, blue = BCOLOR.WARNING, BCOLOR.OKBLUE
        else:
            green, end = BCOLOR.ENDC, BCOLOR.ENDC
            yellow, blue = BCOLOR.ENDC, BCOLOR.ENDC
        # Manually print error message (with help)
        print()
        print(green + underline + 'Help for: {0}.py'.format(log_opt) + end)
        print()
        print(blue + self.format_help() + end)


class CheckDirectory(argparse.Action):
    def __init__(self, *args, **kwargs):
        self.drs_params = dict()
        # set default values
        self.drs_params['LOG_OPT'] = ''
        self.drs_params['RECIPE'] = dict()
        self.drs_params['RECIPE']['inputdir'] = 'RAW'
        # force super initialisation
        argparse.Action.__init__(self, *args, **kwargs)

    def check_directory(self, directory):

        # get parameterse from drs_params
        input_dir_pick = self.drs_params['RECIPE']['inputdir']
        log_opt = self.drs_params['LOG_OPT']
        limit = self.drs_params['DRS_NIGHT_NAME_DISPLAY_LIMIT']
        # get the input directory from recipe.inputdir keyword
        if input_dir_pick == 'RAW':
            input_dir = self.drs_params['DRS_DATA_RAW']
        elif input_dir_pick == 'TMP':
            input_dir = self.drs_params['DRS_DATA_WORKING']
        elif input_dir_pick == 'REDUCED':
            input_dir = self.drs_params['DRS_DATA_REDUC']
        # if not found produce error
        else:
            emsg1 = ('Recipe definition error: "inputdir" must be either'
                    ' "RAW", "REDUCED" or "TMP".')
            emsg2 = '\tCurrently has value="{0}"'.format(input_dir_pick)
            WLOG('error', log_opt, [emsg1, emsg2])
            input_dir = None
        # step 1 check if directory is full absolute path
        if os.path.exists(directory):
            wmsg = 'Directory found! (Absolute path)'
            WLOG('', log_opt, wmsg)
            return '', directory
        # step 2 check if directory is in input directory
        elif os.path.exists(os.path.join(input_dir, directory)):
            wmsg = 'Directory found! (Found in {0})'.format(input_dir)
            WLOG('', log_opt, wmsg)
            return input_dir, directory
        # step 3: fail if neither step1 or step2 is True
        else:
            emsgs = ['Argument Error: "{0}" is not a valid DRS directory'
                     ''.format(directory),
                     '\tSome available [FOLDER]s are as follows:']
            # get some available directories
            dirlist = get_dir_list(input_dir, limit)
            # loop around night names and add to message
            for dir_it in dirlist:
                emsgs.append('\t\t {0}'.format(dir_it))
            WLOG('error', log_opt, emsgs)

    def __call__(self, parser, namespace, values, option_string=None):
        # get drs parameters
        self.drs_params = parser.drs_params
        # check value
        if type(values) == list:
            root, directory = self.check_directory(values[0])
        else:
            root, directory = self.check_directory(values)
        # Add the attributes
        setattr(namespace, self.dest, directory)
        setattr(namespace, 'input_dir', root)


class CheckFiles(argparse.Action):
    def __init__(self, *args, **kwargs):
        self.drs_params = dict()
        self.namespace = None
        # set default values
        self.drs_params['LOG_OPT'] = ''
        self.drs_params['RECIPE'] = dict()
        self.drs_params['RECIPE']['NAME'] = 'UNKNOWN'
        # force super initialisation
        argparse.Action.__init__(self, *args, **kwargs)

    def check_file_location(self, filename):
        # check if "input_dir" is in namespace
        input_dir = getattr(self.namespace, 'input_dir', '')
        # check if "directory" is in namespace
        directory = getattr(self.namespace, 'directory', '')
        # get argument/keyword argument
        if self.dest in self.drs_params['RECIPE']['args']:
            arg = self.drs_params['RECIPE']['args'][self.dest]
        elif  self.dest in self.drs_params['RECIPE']['kwargs']:
            arg = self.drs_params['RECIPE']['kwargs'][self.dest]
        else:
            arg = None
        # get display limit
        limit = self.drs_params['DRS_NIGHT_NAME_DISPLAY_LIMIT']
        # check if arg extension is in recipe (by looking at arg.files)
        ext = ''
        if len(arg.files) > 0:
            if arg.files[0].ext != '':
                ext = '.' + arg.files[0].ext
        # get parameterse from drs_params
        log_opt = self.drs_params['LOG_OPT']
        # step 1: check for wildcards and absolute path
        cond1, newfilename = check_for_file(filename, log_opt, 'ABSPATH')
        if cond1:
            return newfilename
        # step 2: check if file is in input_dir
        input_dir_full = os.path.join(input_dir, directory)
        input_path = os.path.join(input_dir_full, filename)
        cond2, newfilename = check_for_file(input_path, log_opt, 'INPUTDIR')
        if cond2:
            return newfilename
        # step 3: check if file is valid if we add ".fits"
        filename1 = filename + ext
        input_path1 = os.path.join(input_dir_full, filename1)
        cond3, newfilename = check_for_file(input_path1, log_opt, 'ADDFITS')
        if cond3:
            return newfilename
        # step 4: return error message

        emsgs = ['Argument Error: File was not found.'
                 ''.format(filename), '\tTried:']
        emsgs.append('\t\t ' + filename)
        emsgs.append('\t\t ' + os.path.join(input_dir_full, filename))
        emsgs.append('\t\t ' + os.path.join(input_dir_full, filename1))
        # generate error message
        emsgs.append('\tSome available files are as follows:')
        # get some available directories
        filelist = get_file_list(input_dir_full, limit, ext)
        # loop around night names and add to message
        for file_it in filelist:
            emsgs.append('\t\t {0}'.format(file_it))
        WLOG('error', log_opt, emsgs, wrap=False)

    def check_drs_filetype(self, files, value):
        # func_name = __NAME__ + '.CheckFiles.check_drs_file()'
        # get argument/keyword argument
        if self.dest in self.drs_params['RECIPE']['args']:
            arg = self.drs_params['RECIPE']['args'][self.dest]
        elif  self.dest in self.drs_params['RECIPE']['kwargs']:
            arg = self.drs_params['RECIPE']['kwargs'][self.dest]
        else:
            arg = None
        # if not a list make a list (for ease of use)
        if type(files) is not list:
            files = [files]
        # get list of drs file objects
        drs_files = arg.files
        # valid files
        valid_files, valid_ftypes = [], []
        # loop around each file
        for it, filename in enumerate(files):
            # get extension for the first file (Assume all the same)
            ext = ''
            if len(arg.files) > 0:
                if drs_files[0].ext != '':
                    ext = drs_files[0].ext
            # if file is not a fits file do not check it
            if ext != 'fits':
                valid_files.append(filename)
                valid_ftypes.append(None)
            # if fits file use fits file checked
            else:
                vfile, vtype = self.check_drs_fits_file(filename, drs_files,
                                                        value)
                valid_files.append(vfile)
                valid_ftypes.append(vtype)
        # return valid files
        return valid_files, valid_ftypes

    def check_drs_fits_file(self, filepath, drs_files, value):
        func_name = __NAME__ + '.CheckFiles.check_drs_fits_file()'
        # get log_opt
        log_opt = self.drs_params['LOG_OPT']
        recipename = self.drs_params['RECIPE']['name']
        # get directory and filename from filepath
        path = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        # deal with fail msgs
        fail_msgs = []
        # add a warning that wildcards were used
        if '*' in value:
            fmsg = 'WARNING: Arg "{0}": wildcards were used in input="{1}"'
            fail_msgs.append(fmsg.format(self.dest, value))
        # check extension ".fits"
        check_file_extension(self.dest, recipename, filename, '.fits', log_opt,
                             fail_msgs)
        # try to open header of file
        try:
            # obtain the header
            fileheader = fits.getheader(filepath)
        except Exception as e:
            emsg1 = ('An error occured when trying to read the header of '
                    'file="{0}" from dir={1}'.format(filename, path))
            emsg2 = '\tfunction={0}'.format(func_name)
            WLOG('error', log_opt, [emsg1, emsg2])
            fileheader = None
        # storage for correct
        correct_drsfile = None
        # try to check header for keys and values
        for drs_file in drs_files:
            # get drs check_ext
            check_ext = drs_file.check_ext
            # check ext "check_ext"
            check_file_extension(self.dest, recipename, filename, check_ext,
                                 log_opt, fail_msgs)
            # check header
            correct_file = drs_file.check(self, fileheader, self.drs_params,
                                          fail_msgs)
            # if this is the correct file store the drsfile
            if correct_file:
                correct_drsfile = drs_file
                break
        # if we have a correct drs file then display passed message
        if correct_drsfile is not None:
            # log correct
            wmsg = ('Arg "{0}": File "{1}" (identified as "{2}") valid for '
                    'recipe "{3}"')
            wargs = [self.dest, filename, correct_drsfile.name,
                     self.drs_params['RECIPE']['name']]
            WLOG('', log_opt, wmsg.format(*wargs))
        # else we have an incorrect file
        else:
            # log incorrect
            eargs = [self.dest, filename, self.drs_params['RECIPE']['name']]
            emsgs = ['Arg "{0}": File "{1}" not valid for recipe "{2}"'
                     ''.format(*eargs)]
            if len(set(fail_msgs)) > 1:
                emsgs.append('\tErrors/Warnings were as follows:')
            else:
                emsgs.append('\tError was as follows:')
            for fmsg in set(fail_msgs):
                emsgs.append('\t\t{0}'.format(fmsg))
            # log error
            WLOG('error', log_opt, emsgs)
        # return filename and drs file type
        return filepath, correct_drsfile


    def __call__(self, parser, namespace, values, option_string=None):
        # get drs parameters
        self.drs_params = parser.drs_params
        # get the namespace
        self.namespace = namespace
        # get the input values
        if type(values) == list:
            files, ftypes = [], []
            # must loop around values
            for value in values:
                # check file could return list or string
                file_it = self.check_file_location(value)
                file_it, ftype = self.check_drs_filetype(file_it, value)
                # must add to files depending on whether list or string
                if type(file_it) is list:
                    files += file_it
                    ftypes += ftype
                else:
                    files.append(file_it)
                    ftypes.append(ftype)
        else:
            files = self.check_file_location(values)
            files, ftypes = self.check_drs_filetype(files, values)
        # Add the attribute
        setattr(namespace, self.dest, [files, ftypes])


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


class CheckOptions(argparse.Action):
    def check_options(self, value):

        if value in self.choices:
            return value
        else:
            emsg1 = 'Arguement "{0}" must be {1}'
            eargs1 = [self.dest, ' or '.join(self.choices)]
            emsg2 = '\tCurrent value = {0}'.format(value)
            WLOG('error', '', [emsg1.format(*eargs1), emsg2])


    def __call__(self, parser, namespace, values, option_string=None):
        if type(values) == list:
            value = list(map(self.check_options, values))
        else:
            value = self.check_options(values)
        # Add the attribute
        setattr(namespace, self.dest, value)


class MakeListing(argparse.Action):
    def __init__(self, *args, **kwargs):
        self.drs_params = dict()
        self.namespace = None
        # set default values
        self.drs_params['LOG_OPT'] = ''
        self.drs_params['RECIPE'] = dict()
        self.drs_params['RECIPE']['NAME'] = 'UNKNOWN'
        # force super initialisation
        argparse.Action.__init__(self, *args, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        # check if "input_dir" is in namespace
        input_dir = getattr(namespace, 'input_dir', '')
        # check if "directory" is in namespace
        directory = getattr(namespace, 'directory', '')
        # create full dir path
        fulldir = os.path.join(input_dir, directory)
        # generate a file list
        filelist = get_file_list(fulldir, recursive=True)
        # construct log message
        wmsg = 'Displaying first {0} files in directory="{1}"'
        wmsgs = ['', wmsg.format(HARD_DISPLAY_LIMIT, fulldir), '']
        for filename in filelist:
            wmsgs.append('\t' + filename)
        WLOG('', self.drs_params['LOG_OPT'], wmsgs)
        # quit after call
        parser.exit()


# =============================================================================
# Define Object Classes
# =============================================================================
class DrsArgument(object):
    def __init__(self, name, **kwargs):
        """
        Create a DRS Argument object

        :param name: string, the name of the argument and call, for optional
                     arguments should include the "-" and "--" in front
                     ("arg.name" will not include these but "arg.argname"
                     and "arg.names" will)

        :param kwargs: currently allowed kwargs are:

            - pos: int or None, the position of a position argument, if None
                   not a positional argument (i.e. optional argument)

            - altnames: list of strings or None, the alternative calls to
                        the argument in argparse (as well as "name"), if None
                        only call to argument is "name"

            - dtype: string or type or None, the data type currently must
                     be one of the following:
                        ['files', 'file', 'directory', 'bool',
                         'options', 'switch', int, float, str, list]
                     if None set to string.
                     these control the checking of the argument in most cases.
                     int/flat/str/list are not checked

            - options: list of strings or None, sets the allowed string values
                       of the argument, if None no options are required (other
                       than those set by dtype)

            - helpstr: string or None, if not None sets the text to add to the
                       help string

            - files: list of DrsInput objects or None, if not None and dtype
                     is "files" or "file" sets the type of file to expect
                     the way the list is understood is based on "filelogic"

            - filelogic: string, either "inclusive" or "exclusive", if
                         inclusive and combination of DrsInput objects are
                         valid, if exclusive only one DrsInput in the list is
                         valid for all files i.e.
                         - if files = [A, B] and filelogic = 'inclusive'
                           the input files may all be A or all be B
                         - if files = [A, B] and filelogic = 'exclusive'
                           the input files may be either A or B
        """
        # ----------------------------------------------
        # define class constants
        # ----------------------------------------------
        # define allowed properties
        self.propkeys = ['action', 'nargs', 'type', 'choices', 'default',
                         'help']
        # define allowed dtypes
        self.allowed_dtypes = ['files', 'file', 'directory', 'bool',
                               'options', 'switch', int, float, str, list]
        # ----------------------------------------------
        # assign values from construction
        # ----------------------------------------------
        # get argument name
        self.argname = str(name)
        # get full name
        self.name = name
        while self.name.startswith('-'):
            self.name = self.name[1:]
        # get position
        self.pos = kwargs.get('pos', None)
        # add names from altnames
        self.names = [self.argname] + kwargs.get('altnames', [])
        # get dtype
        self.dtype = kwargs.get('dtype', None)
        # get default
        self.default = kwargs.get('default', None)
        # get options
        self.options = kwargs.get('options', None)
        # get help str
        self.helpstr = kwargs.get('helpstr', '')
        # get files
        self.files = kwargs.get('files', [])
        # get file logic
        self.filelogic = kwargs.get('filelogic', 'inclusive')
        if self.filelogic not in ['inclusive', 'exclusive']:
            emsg = ('DrsArgument Error: "filelogic" must equal "inclusive" '
                    'or "exclusive" only. '
                    'Current value is "{0}"'.format(self.filelogic))
            raise ValueError(emsg)

        # set empty
        self.props = dict()

    def make_properties(self):
        """
        Make the properties dictionary for argparser based on the
        "arg.dtype" assigned during construction.
        i.e. one of the following provides the information to fill arg.props
            ['files', 'file', 'directory', 'bool', 'options',
             'switch', int, float, str, list]

        This must be run manually once an instance of DrsArgument is
        constructed.

        :return None:
        """
        # deal with no dtype
        if self.dtype is None:
            self.dtype = str
        # make sure dtype is valid
        if self.dtype not in self.allowed_dtypes:
            a_dtypes_str = ['"{0}"'.format(i) for i in self.allowed_dtypes]
            eargs = [' or '.join(a_dtypes_str), self.dtype]
            emsg = ('DrsArgument Error: "dtype" is not valid. Must be equal'
                    ' to {0}. Current value is "{1}"'.format(*eargs))
            raise ValueError(emsg)
        # deal with dtype
        if self.dtype == 'files':
            self.props['action'] = CheckFiles
            self.props['nargs'] = '+'
            self.props['type'] = str
        elif self.dtype == 'file':
            self.props['action'] = CheckFiles
            self.props['nargs'] = 1
            self.props['type'] = str
        elif self.dtype == 'directory':
            self.props['action'] = CheckDirectory
            self.props['nargs'] = 1
            self.props['type'] = str
        elif self.dtype == 'bool':
            self.props['action'] = CheckBool
            self.props['type'] = str
            self.props['choices'] = ['True', 'False', '1', '0']
        elif self.dtype == 'options':
            self.props['action'] = CheckOptions
            self.props['type'] = str
            self.props['choices'] = self.options
        elif self.dtype=='switch':
            self.props['action'] = 'store_true'
        elif type(self.dtype) is type:
            self.props['type'] = self.dtype
            self.props['nargs'] = 1
        else:
            self.props['type'] = str
            self.props['nargs'] = 1
        # deal with default argument
        if self.default is not None:
            self.props['default'] = self.default
        # add help string
        self.props['help'] = self.helpstr

    def assign_properties(self, props):
        """
        Assigns argparse properties from "props"

        Instead of creating properties based on dtype one can assign
        properties based on a input dictionary "props". This is useful
        when one has a defined static set or properties to pass to
        argparse. Only keys in the following list will be allowed to be passed
        to arg.props:
            ['action', 'nargs', 'type', 'choices', 'default', 'help']

        :param props: dictionary, contains pre-defined key value pairs to
                      parse to argparser keys must be in the following list:
                      ['action', 'nargs', 'type', 'choices', 'default', 'help']
        :return None:
        """

        # loop around properties
        for prop in self.propkeys:
            if prop in props:
                self.props[prop] = props[prop]

    def __str__(self):
        """
        Defines the str(DrsArgument) return for DrsArgument
        :return str: the string representation of DrSArgument
                     i.e. DrsArgument[name]
        """
        return 'DrsArgument[{0}]'.format(self.name)

    def __repr__(self):
        """
        Defines the print(DrsArgument) return for DrsArgument
        :return str: the string representation of DrSArgument
                     i.e. DrsArgument[name]
        """
        return 'DrsArgument[{0}]'.format(self.name)


class DrsRecipe(object):
    def __init__(self, name=None):
        """
        Create a DRS Recipe object

        :param name: string, name of the recipe (the .py file) relating to
                     this recipe object
        """
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
        self.specialargs = dict()
        # make special arguments
        self.make_specials()
        # define arg list
        self.arg_list = []
        self.str_arg_list = None

    def arg(self, name=None, **kwargs):
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
        # create argument
        argument = DrsArgument(name, **kwargs)
        # make arg parser properties
        argument.make_properties()
        # recast name
        name = argument.name
        # add to arg list
        self.args[name] = argument

    def kwarg(self, name=None, **kwargs):
        """
        Add a keyword argument to the recipe

        :param name: string or None, the name and reference of the argument
        :param dtype: type or None, the type expected for the argument (will
                      raise error if not this type)

        :param default: object or None, the default value for the keyword
                        argument
        :param helpstr: string or  None, the help string
        :param options: list of strings or None: the options allowed for
                        keyword argument
        :param altnames: list of strings or None: alternative names for the
                         reference of the argument

        :return None:
        """
        if name is None:
            name = 'Kwarg{0}'.format(len(self.args) + 1)
        # create keyword argument
        keywordargument = DrsArgument(name, **kwargs)
        # make arg parser properties
        keywordargument.make_properties()
        # recast name
        name = keywordargument.name
        # set to keyword argument
        self.kwargs[name] = keywordargument

    def parse_args(self, dictionary):
        """
        Parse a dictionary of arguments into argparser in the format required
        to match up to the recipe.args/recipe.kwarg assigned to this
        DrsRecipe by calls to "recipe.arg" and "recipe.kwarg"

        :param dictionary: list of key value pairs where the keys must match
                           the names (without "-" and "--") of the arguments
                           and keyword arguments. This is then passed into
                           "recipe.str_arg_list" for parsing into argparser
                           directly (and overiding run time arguments)
        :return None:
        """
        self.str_arg_list = []
        if dictionary is None:
            return None
        for argname in self.args:
            # check if key in dictionary
            if argname not in dictionary:
                continue
            # get value(s)
            values = dictionary[argname]
            # pass this argument
            self.parse_arg(self.args[argname], values)
        for kwargname in self.kwargs:
            # check if key in dictionary
            if kwargname not in dictionary:
                continue
            # get value(s)
            values = dictionary[kwargname]
            # pass this argument
            self.parse_arg(self.kwargs[kwargname], values)
        # check if we have parameters
        if len(self.str_arg_list) == 0:
            self.str_arg_list = None

    def parse_arg(self, arg, values):
        """
        Parse argument to "recipe.str_arg_list"

        :param arg: str, the name of the argument (with "-" and "--" for
                    optional arguments)
        :param values: object, the object to push into the value of argument.
                       The string representation of this value must be
                       readable by argparser i.e. int/float/str etc
        :return None:
        """
        # check that value is not None
        if values is None:
            return
        # if we have an optional argument
        if '-' in arg.argname:
            strfmt = '{0}={1}'
        # if we have a positional argument
        else:
            strfmt = '{1}'
        # now add these arguments (as a string) to str_arg_list
        if type(values) == list:
            for value in values:
                strarg = [arg.argname, value]
                self.str_arg_list.append(strfmt.format(*strarg))
        else:
            strarg = [arg.argname, values]
            self.str_arg_list.append(strfmt.format(*strarg))

    def make_specials(self):
        """
        Make special arguments based on pre-defined static properties
        (i.e. a valid kwargs for parser.add_argument)

        Currently adds the following special arguments:

        --listing, --list     List the files in the given input directory

        :return None:
        """
        # make listing functionality
        listingprops = make_listing()
        name = listingprops['name']
        listing = DrsArgument(name, altnames=listingprops['altnames'])
        listing.assign_properties(listingprops)
        self.specialargs[name] = listing

    def __str__(self):
        """
        Defines the str(DrsRecipe) return for DrsRecipe
        :return str: the string representation of DrsRecipe
                     i.e. DrsRecipe[name]
        """
        return 'DrsRecipe[{0}]'.format(self.name)

    def __repr__(self):
        """
        Defines the print(DrsRecipe) return for DrsRecipe
        :return str: the string representation of DrsRecipe
                     i.e. DrsRecipe[name]
        """
        return 'DrsRecipe[{0}]'.format(self.name)


class DrsInputFile:

    def __init__(self, name, ext):
        """
        Create a DRS Input File object

        :param name: string, the name of the DRS input file
        :param ext: string, the extension for the DRS input file (without
                    the '.' i.e. A.txt  ext='txt'

        - Parent class for Drs Fits File object (DrsFitsFile)
        """
        # define a name
        self.name = name
        # define the extension
        self.ext = ext

    def __str__(self):
        """
        Defines the str(DrsInputFile) return for DrsInputFile
        :return str: the string representation of DrsInputFile
                     i.e. DrsInputFile[name]
        """
        return 'DrsInputFile[{0}]'.format(self.name)

    def __repr__(self):
        """
        Defines the print(DrsInputFile) return for DrsInputFile
        :return str: the string representation of DrsInputFile
                     i.e. DrsInputFile[name]
        """
        return 'DrsInputFile[{0}]'.format(self.name)


class DrsFitsFile(DrsInputFile):
    def __init__(self, name, **kwargs):
        """
        Create a DRS Fits File Input object

        :param name: string, the name of the DRS input file

        :param kwargs: currently allowed kwargs are:

            - ext: string or None, the extension for the DRS input file
                   (without the '.' i.e. A.txt  ext='txt'). This will be
                   checked if used in a DrsArgument if not None.

            - fiber: string or None, the fiber of the Fits File.

            - KW_{str}: string, any keywordstore variable name currently
                        defined in spirouKeywords.py. If used in DrsArgument
                        the HEADER of this fits file must have the value
                        of this KW_{str} to be a valid argument.
        """
        # define a name
        self.name = name
        # get super init
        DrsInputFile.__init__(self, name, 'fits')
        # if ext in kwargs then we have a file extension to check
        self.check_ext = kwargs.get('ext', None)
        # get fiber type (if set)
        self.fiber = kwargs.get('fiber', None)
        # get tag
        self.outtag = kwargs.get('KW_OUTPUT', 'UNKNOWN')
        # add header
        self.header = dict()
        # add values to the header
        for kwarg in kwargs:
            if 'KW_' in kwarg.upper():
                self.header[kwarg] = kwargs[kwarg]

    def check(self, header, params, fail_msgs):
        """
        Check "header" for valid key value pairs

        Uses recipe.header with the KW_{str} keyword-store keys to locate
        the params[KW_{str}] to check in "header"
        i.e. the following must be True for all keys

        key = params[KW_{str}][0]
        recipe.header[KW_{str}]] == header[key]

        :param header: dictionary, the header file from a fits file to check
                       for the correct keys

        :return file_found: bool, True if file found
        :return fail_msgs: list of strings, strings contain error messages
                           for all checks that failed
        """
        # start off thinking this file is correct
        correct_file = True
        # loop around keys that are needed for this to be a good file
        for drskey in self.header:
            # get key from drs_params
            if drskey in params:
                key = params[drskey][0]
            else:
                key = drskey
            # check if key is in file header
            if key in header:
                # check if key is correct
                if self.header[drskey].strip() != header[key].strip():
                    correct_file = False
                    # construct fail msg
                    fmsg = ('ERROR: file header key "{0}"="{1}" should '
                            'be "{2}"')
                    fargs = [key, header[key], self.header[drskey]]
                    fail_msgs.append(fmsg.format(*fargs))
            else:
                correct_file = False
                fmsg = 'ERROR: file header key "{0}" not in header'
                fail_msgs.append(fmsg.format(key))

        return correct_file, fail_msgs


    def string_output(self):
        """
        String output for DrsFitsFile. If fiber is not None this also
        contains the fiber type

        i.e. DrsFitsFile[{name}_{fiber}] or DrsFitsFile[{name}]
        :return string: str, the string to print
        """
        if self.fiber is None:
            return 'DrsFitsFile[{0}]'.format(self.name)
        else:
            return 'DrsFitsFile[{0}_{1}]'.format(self.name, self.fiber)

    def __str__(self):
        """
        Defines the str(DrsFitsFile) return for DrsFitsFile
        :return str: the string representation of DrsFitsFile
                     i.e. DrsFitsFile[name] or DrsFitsFile[name_fiber]
        """
        return self.string_output()

    def __repr__(self):
        """
        Defines the print(DrsFitsFile) return for DrsFitsFile
        :return str: the string representation of DrsFitsFile
                     i.e. DrsFitsFile[name] or DrsFitsFile[name_fiber]
        """
        return self.string_output()



# =============================================================================
# Define functions
# =============================================================================
def check_for_file(path, log_opt, kind=None):

    if kind is not None:
        kindstr = ' ({0})'.format(kind)
    else:
        kindstr = ''

    # get glob list of files using glob
    raw_files = glob.glob(path)

    # if we cannot find file return
    if len(raw_files) == 0:
        # return False and no filename
        return False, None

    # if we find just one file
    elif len(raw_files) == 1:
        # get filename
        filename = os.path.basename(raw_files[0])
        # get directory
        directory = os.path.dirname(raw_files[0])
        # log message
        wmsg = 'File "{0}" exists in directory "{1}"' + kindstr
        WLOG('', log_opt, wmsg.format(filename, directory))
        # return True and filename
        return True, raw_files[0]

    # else we have multiple files (from wild cards)
    else:
        # set up storage
        files = []
        directory = None
        # loop around raw files
        for raw_file in raw_files:
            # get directory
            directory_it = os.path.dirname(raw_file)
            # check that we don't have multiple directories
            if directory is not None:
                if directory_it != directory:
                    emsg = ('Wildcard Error: Can only have files from one '
                            'directory. Multiple found')
                    WLOG('error', log_opt, emsg)
            else:
                directory = str(directory_it)
            # add to list of files
            files.append(raw_file)
        # log message
        wmsgs = ['Files exists (Absolute path + wildcard):']
        for raw_file in raw_files:
            wmsgs.append('\t' + raw_file)
        WLOG('', log_opt, wmsgs)

        return True, files


def get_dir_list(dirroot, limit):
    dir_list = []
    for root, dirs, files in os.walk(dirroot):
        # skip dirs that are empty (or full of directories)
        if len(files) == 0:
            continue
        # do not display all
        if len(dir_list) > limit:
            dir_list.append('...')
            return dir_list
        # find the relative root of directories compared to ARG_FILE_DIR
        common = os.path.commonpath([dirroot, root]) + '/'
        relroot = root.split(common)[-1]
        # append relative roots
        dir_list.append(relroot)
    # if empty list add none found
    if len(dir_list) == 0:
        dir_list = ['No valid directories found.']
    # return night_dirs
    return dir_list


def get_file_list(path, limit=None, ext=None, recursive=False):

    # deal with no limit - set hard limit
    if limit is None:
        limit = HARD_DISPLAY_LIMIT
    # deal with extension
    if ext is None:
        ext = ''
    # set up file list storage
    file_list = []
    # walk through directories
    for root, dirs, files in os.walk(path):
        if len(file_list) > limit:
            file_list.append('...')
            return file_list
        if not recursive and root != path:
            continue
        if len(files) > 0 and recursive:
            # add root to file list
            file_list.append('\t' + root)
            limit += 1
        for filename in files:
            # do not display all (if limit reached)
            if len(file_list) > limit:
                file_list.append('...')
                return file_list
            # do not display if extension is true
            if not filename.endswith(ext):
                continue
            # add to file list
            file_list.append('\t\t' + filename)
    # if empty list add none found
    if len(file_list) == 0:
        file_list = ['No valid files found.']
    # return file_list
    return file_list


def check_file_extension(arg, recipe, filename, ext, log_opt, fail_msgs):

    if ext is None:
        return 0

    if not filename.endswith(ext):
        # add fail message
        fmsg = 'ERROR: File {0} must end with "{1}"'
        fail_msgs.append(fmsg.format(filename, ext))
        # construct error message
        eargs = [arg, filename, recipe]
        emsgs = ['Arg "{0}": File "{1}" not valid for recipe "{2}"'
                 ''.format(*eargs)]
        # add fail msg
        if len(fail_msgs) > 1:
            emsgs.append('\tErrors/Warnings were as follows:')
        else:
            emsgs.append('\tError was as follows:')
        for fail_msg in fail_msgs:
            emsgs.append('\t\t' + fail_msg)
        # log error
        WLOG('error', log_opt, emsgs)


def make_listing():
    """
    Make a custom special argument that lists the files in the given
    input directory
    :return props: dictionary for argparser
    """
    props = dict()
    props['name'] = '--listing'
    props['altnames'] = ['--list']
    props['action'] = MakeListing
    props['nargs'] = 0
    props['help'] = 'List the files in the given input directory.'
    return props


# =============================================================================
# End of code
# =============================================================================
