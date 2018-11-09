#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-09-14 at 18:19

@author: cook
"""
import numpy as np
import argparse
import sys
import os
import glob
from collections import OrderedDict

from SpirouDRS import spirouCore
from SpirouDRS import spirouConfig
from . import spirouFile

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'drs_recipe.py'
# Get Logging function
WLOG = spirouCore.wlog
# get constants
CONSTANTS = spirouConfig.Constants
# get the default log_opt
DPROG = CONSTANTS.DEFAULT_LOG_OPT()
# get print colours
BCOLOR = CONSTANTS.BColors
# get param dict
ParamDict = spirouConfig.ParamDict
# get the config error
ConfigError = spirouConfig.ConfigError
# define hard display limit
HARD_DISPLAY_LIMIT = 99
# define display strings for types
STRTYPE = dict()
STRTYPE[int] = 'int'
STRTYPE[float] = 'float'
STRTYPE[str] = 'str'
STRTYPE[complex] = 'complex'
STRTYPE[list] = 'list'
STRTYPE[np.ndarray] = 'np.ndarray'
# -----------------------------------------------------------------------------


# =============================================================================
# Define ArgParse Parser and Action classes
# =============================================================================
# Adapted from: https://stackoverflow.com/a/16942165
class DRSArgumentParser(argparse.ArgumentParser):
    def __init__(self, recipe, **kwargs):
        self.recipe = recipe
        argparse.ArgumentParser.__init__(self, **kwargs)

    def error(self, message):
        #self.print_help(sys.stderr)
        #self.exit(2, '%s: error: %s\n' % (self.prog, message))

        # get parameterse from drs_params
        log_opt = self.recipe.drs_params['LOG_OPT']
        # construct error message
        underline = BCOLOR.UNDERLINE
        if self.recipe.drs_params['COLOURED_LOG']:
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
        log_opt = self.recipe.drs_params['LOG_OPT']
        # construct error message
        underline = BCOLOR.UNDERLINE
        if self.recipe.drs_params['COLOURED_LOG']:
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

    def has_help(self):
        if '-h' in sys.argv:
            self.print_help()
            # quit after call
            self.exit()
        if '--help' in sys.argv:
            self.print_help()
            # quit after call
            self.exit()
        if '--listing' in sys.argv:
            return True
        else:
            return False


class CheckDirectory(argparse.Action):
    def __init__(self, *args, **kwargs):
        self.recipe = None
        # force super initialisation
        argparse.Action.__init__(self, *args, **kwargs)

    def check_directory(self, directory):

        # get parameterse from drs_params
        log_opt = self.recipe.drs_params['LOG_OPT']
        limit = self.recipe.drs_params['DRS_NIGHT_NAME_DISPLAY_LIMIT']
        # get the input directory from recipe.inputdir keyword
        input_dir = get_input_dir(self.recipe)
        # step 1 check if directory is full absolute path
        if os.path.exists(directory):
            wmsg = 'Directory found (Absolute path)'
            WLOG('', log_opt, wmsg)
            return '', directory
        # step 2 check if directory is in input directory
        elif os.path.exists(os.path.join(input_dir, directory)):
            wmsg = 'Directory found (Found in {0})'.format(input_dir)
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
        # check for help
        skip = parser.has_help()
        if skip: return 0
        # get drs parameters
        self.recipe = parser.recipe
        # check value
        if type(values) == list:
            root, directory = self.check_directory(values[0])
        else:
            root, directory = self.check_directory(values)
        # Add the attributes
        setattr(namespace, self.dest, directory)


class CheckFiles(argparse.Action):
    def __init__(self, *args, **kwargs):
        self.recipe = None
        self.namespace = None
        self.id_num = 0
        self.id_type = None
        # force super initialisation
        argparse.Action.__init__(self, *args, **kwargs)

    def check_file_location(self, filename):
        # check if "input_dir" is in namespace
        input_dir = get_input_dir(self.recipe)
        # check if "directory" is in namespace
        directory = getattr(self.namespace, 'directory', '')
        # get argument/keyword argument
        if self.dest in self.recipe.args:
            arg = self.recipe.args[self.dest]
        elif  self.dest in self.recipe.kwargs:
            arg = self.recipe.kwargs[self.dest]
        else:
            arg = None
        # get display limit
        limit = self.recipe.drs_params['DRS_NIGHT_NAME_DISPLAY_LIMIT']
        # check if arg extension is in recipe (by looking at arg.files)
        ext = ''
        if len(arg.files) > 0:
            if arg.files[0].ext != '':
                ext = '.' + arg.files[0].ext
        # get parameterse from drs_params
        log_opt = self.recipe.drs_params['LOG_OPT']
        # ---------------------------------------------------------------------
        # step 1: check for wildcards and absolute path
        cout1 = check_for_file(self.dest, self.id_num, filename, log_opt,
                              kind='ABSPATH')
        cond1, newfilename = cout1
        if cond1:
            return newfilename
        # ---------------------------------------------------------------------
        # step 2: check if file is in input_dir
        input_dir_full = os.path.join(input_dir, directory)
        input_path = os.path.join(input_dir_full, filename)
        cout2 = check_for_file(self.dest, self.id_num, input_path, log_opt,
                              kind='INPUTDIR')
        cond2, newfilename = cout2
        if cond2:
            return newfilename
        # ---------------------------------------------------------------------
        # step 3: check if file is valid if we add ".fits"
        filename1 = filename + ext
        input_dir_full = os.path.join(input_dir, directory)
        input_path1 = os.path.join(input_dir_full, filename1)
        cout3 = check_for_file(self.dest, self.id_num, input_path1, log_opt,
                               kind='ADDFITS')
        cond3, newfilename = cout3
        if cond3:
            return newfilename
        # ---------------------------------------------------------------------
        # step 4: return error message
        emsgs = ['Argument Error: File was not found.'
                 ''.format(filename), '\tTried:']
        emsgs.append('\t\t ' + filename)
        path1 = os.path.realpath(os.path.join(input_dir_full, filename))
        emsgs.append('\t\t ' + path1)
        path2 = os.path.realpath(os.path.join(input_dir_full, filename1))
        emsgs.append('\t\t ' + path2)
        # generate error message
        emsgs.append('\tSome available files are as follows:')
        # get some available directories
        filelist = get_file_list(input_dir_full, limit, ext)
        # loop around night names and add to message
        for file_it in filelist:
            emsgs.append('\t\t {0}'.format(file_it))
        WLOG('error', log_opt, emsgs, wrap=False)

    def check_drs_filetype(self, files, value):
        """

        :param files:
        :param value:
        :return:
        """
        func_name = __NAME__ + '.CheckFiles.check_drs_file()'
        # get argument/keyword argument
        if self.dest in self.recipe.args:
            arg = self.recipe.args[self.dest]
        elif  self.dest in self.recipe.kwargs:
            arg = self.recipe.kwargs[self.dest]
        else:
            arg = None
        # if not a list make a list (for ease of use)
        if type(files) is not list:
            files = [files]
        # valid files
        valid_files, valid_ftypes = [], []
        # loop around each file
        for it, filename in enumerate(files):
            # get extension for the first file (Assume all the same)
            ext = ''
            if len(arg.files) > 0:
                if arg.files[0].ext != '':
                    ext = arg.files[0].ext
            # if file is not a fits file do not check it
            if ext != 'fits':
                valid_files.append(filename)
                valid_ftypes.append(None)
            # if fits file use fits file checked
            else:
                vfile, vtype = self.check_drs_fits_file(filename, arg, value)
                # append filenames
                valid_files.append(vfile)
                # append valid file types
                valid_ftypes.append(vtype)
                self.id_type = vtype
        # return valid files
        return valid_files, valid_ftypes

    def check_drs_fits_file(self, filepath, arg, value):
        func_name = __NAME__ + '.CheckFiles.check_drs_fits_file()'
        # get log_opt
        log_opt = self.recipe.drs_params['LOG_OPT']
        recipename = self.recipe.name
        # get directory and filename from filepath
        path = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        # ---------------------------------------------------------------------
        # check file extension (fits)
        emsgs = check_file_extension(filename, '.fits')
        if len(emsgs) > 0:
            print_check_error(self.dest, self.id_num, filename, recipename,
                              emsgs, value, log_opt)
        # ---------------------------------------------------------------------
        # storage for correct
        correct_drsfile = None
        # get exclusive/inclusive argument
        logic = arg.filelogic
        # ---------------------------------------------------------------------
        herrors = []
        # try to check header for keys and values
        for drs_file in arg.files:
            # get drs check_ext
            check_ext = drs_file.check_ext
            # -----------------------------------------------------------------
            # check ext "check_ext"
            errors = check_file_extension(filename, check_ext)
            if len(errors) > 0:
                print_check_error(self.dest, self.id_num, filename, recipename,
                                  errors, value, log_opt)

            # -----------------------------------------------------------------
            # create an instance of this drs_file with the filename set
            file_instance = drs_file.new(filename=filepath, recipe=self.recipe)
            file_instance.read()
            # -----------------------------------------------------------------
            # check header
            cfargs = [file_instance, herrors, self.dest, self.id_num,
                      self.recipe, value, log_opt]
            correct_file, herrors = check_file_header(*cfargs)
            # -----------------------------------------------------------------
            # if logic is exclusive must match current file types
            if self.id_type is not None:
                c_args = [file_instance, correct_file, logic, self.id_type]
                correct_file, errors = check_exclusivity(*c_args)
            if len(errors) > 0:
                print_check_error(self.dest, self.id_num, filename, recipename,
                                  errors, value, log_opt)
            # -----------------------------------------------------------------
            # if this is the correct file store the drsfile
            if correct_file:
                correct_drsfile = file_instance
                break
        # ---------------------------------------------------------------------
        # construct errors from header loop
        che_args = [herrors, self.recipe.drs_params, arg.files, logic]
        errors = construct_header_error(*che_args)
        # ---------------------------------------------------------------------
        # if we have a correct drs file then display passed message
        if correct_drsfile is not None:
            # log correct
            wmsg = ('Arg "{0}"[{1}]: File "{2}" (identified as "{3}") '
                    'valid for recipe "{4}"')
            wargs = [self.dest, self.id_num, filename, correct_drsfile.name,
                     self.recipe.name]
            WLOG('', log_opt, wmsg.format(*wargs))
        # else we have an incorrect file
        else:
            print_check_error(self.dest, self.id_num, filename, recipename,
                              errors, value, log_opt)
        # ---------------------------------------------------------------------
        # return filename and drs file type
        return filepath, correct_drsfile


    def check_file_types(self, files, value):

        # get log_opt
        log_opt = self.recipe.drs_params['LOG_OPT']
        # get the recipe arguments
        recipe_args = self.get_recipe_arguments()
        # if None then skip
        if recipe_args is not None:
            recipe_file_types = recipe_args.files
        else:
            return [], []
        # set up storage for valid files
        valid_files, valid_file_types = [], []
        # loop around filenames in argument
        for it, filename in enumerate(files):
            self.check_file_type(it, filename, value)


    def check_file_type(self, filename, value):
        # get log_opt
        log_opt = self.recipe.drs_params['LOG_OPT']
        # get the recipe arguments
        recipe_args = self.get_recipe_arguments()
        recipe_file_types = recipe_args.files
        recipe_logic = recipe_args.filelogic
        # storage for error messages
        msgs = []
        # set up placeholder for correct_Drsfile
        correct_drsfile = None
        # loop around valid file types
        for file_type in recipe_file_types:
            # set up a new file
            file_instance = file_type.new(filename=filename,
                                          recipe=self.recipe)
            file_instance.read()
            # now check file
            check1, msg1 = file_instance.check_file_exists(quiet=True)
            # check extension
            check2, msg2 = file_instance.check_file_extension(quiet=True)
            # check file header
            check3, msgtype, msg3 = file_instance.check_file_header(quiet=True)
            # check exclusivity
            check4, msg4 = file_instance.check_exclusivity(self.id_type,
                                                           quiet=True)

            # check conditions and report appropriate error
            if not check1:
                self.print_error(filename, msg1)
            elif not check2:
                self.print_error(filename, msg2)
            elif not check3:
                msgs.append(msg3)
            elif not check4:
                self.print_error(filename, msg4)
            else:
                correct_drsfile = file_instance
                break
        # ---------------------------------------------------------------------
        # construct errors from header loop
        che_args = [msgs, self.recipe.drs_params, recipe_file_types,
                    recipe_logic]
        errors = spirouFile.construct_header_error(*che_args)
        # ---------------------------------------------------------------------
        # if we have a correct drs file then display passed message
        if correct_drsfile is not None:
            self.print_success(filename, correct_drsfile)
        # else we have an error
        else:
            self.print_error(self, filename, errors)

    def print_error(self, filename, messages):
        # get log_opt
        log_opt = self.recipe.drs_params['LOG_OPT']
        # construct main error message
        eargs = [self.dest, self.id_num, filename, self.recipe.name]
        emsgs = ['Arg "{0}"[{1}]: File "{2}" not valid for recipe "{3}"'
                 ''.format(*eargs)]
        # loop around error messages and append
        for message in messages:
            emsgs.append(message)
        # print and log
        WLOG('error', log_opt, emsgs)

    def print_success(self, filename, correct_drsfile):
        # get log_opt
        log_opt = self.recipe.drs_params['LOG_OPT']
        # log correct
        wmsg = ('Arg "{0}"[{1}]: File "{2}" (identified as "{3}") '
                'valid for recipe "{4}"')
        wargs = [self.dest, self.id_num, filename, correct_drsfile.name,
                 self.recipe.name]
        # print and log
        WLOG('', log_opt, wmsg.format(*wargs))

    def get_recipe_arguments(self):
        # get argument/keyword argument
        if self.dest in self.recipe.args:
            arg = self.recipe.args[self.dest]
        elif  self.dest in self.recipe.kwargs:
            arg = self.recipe.kwargs[self.dest]
        else:
            arg = None
        return arg

    def __call__(self, parser, namespace, values, option_string=None):
        # check for help
        skip = parser.has_help()
        if skip: return 0
        # reset id parameters
        self.id_num = 0
        self.id_type = None
        # get drs parameters
        self.recipe = parser.recipe
        # get the namespace
        self.namespace = namespace
        # get the input values
        if type(values) == list:
            files, ftypes = [], []
            # must loop around values
            for value in values:
                self.id_num += 1
                # check file could return list or string
                file_it = self.check_file_location(value)
                file_it, ftype = self.check_drs_filetype(file_it, value)
                # must add to files depending on whether list or string
                if type(file_it) is list:
                    files += file_it
                    ftypes += ftype
                    self.id_type = ftype[0]
                else:
                    files.append(file_it)
                    ftypes.append(ftype)
                    self.id_type = ftype
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
        # check for help
        skip = parser.has_help()
        if skip: return 0
        if type(values) == list:
            value = list(map(self.check_bool, values))
        else:
            value = self.check_bool(values)
        # Add the attribute
        setattr(namespace, self.dest, value)


class CheckType(argparse.Action):
    def eval_type(self, value):
        emsg = 'Argument "{0}"="{1}" should be type "{2}"'
        eargs = [self.dest, value, self.type]
        try:
            return self.type(value)
        except ValueError as e:
            WLOG('error', '', emsg.format(*eargs))
        except TypeError as e:
            WLOG('error', '', emsg.format(*eargs))

    def check_type(self, value):
        # check that type matches
        if type(value) is self.type:
            return value
        # check if passed as a list
        if (self.nargs == 1) and (type(value) is list):
            if len(value) == 0:
                emsg = 'Argument "{0}" should not be an empty list.'
                WLOG('error', '', emsg.format(self.dest))
            else:
                return self.eval_type(value[0])
        # else if we have a list we should iterate
        elif type(value) is list:
            values = []
            for it in self.nargs:
                values.append(self.eval_type(values[it]))
            if len(values) < len(value):
                wmsg = 'Argument too long (expected {0} got {1})'
                wargs = [self.nargs, len(value)]
                WLOG('warning', '', wmsg.format(*wargs))
            return values
        # else
        else:
            emsg = ('Argument "{0}"="{1}" list expected with {2} arguments '
                    'got type {3}')
            eargs = [self.dest, value, self.nargs, type(value)]
            WLOG('error', '', emsg.format(eargs))

    def __call__(self, parser, namespace, values, option_string=None):
        # check for help
        skip = parser.has_help()
        if skip:
            return 0
        if self.nargs == 1:
            value = self.check_type(values)
        elif type(values) == list:
            value = list(map(self.check_type, values))
        else:
            value = self.check_type(values)
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
        # check for help
        skip = parser.has_help()
        if skip: return 0
        if type(values) == list:
            value = list(map(self.check_options, values))
        else:
            value = self.check_options(values)
        # Add the attribute
        setattr(namespace, self.dest, value)


class MakeListing(argparse.Action):
    def __init__(self, *args, **kwargs):
        self.recipe = None
        self.namespace = None
        # force super initialisation
        argparse.Action.__init__(self, *args, **kwargs)

    def display_listing(self, namespace):
        # get input dir
        input_dir = get_input_dir(self.recipe)
        # check if "directory" is in namespace
        directory = getattr(namespace, 'directory', '')
        # deal with non set directory
        if directory is None:
            directory = ''
        # create full dir path
        fulldir = os.path.join(input_dir, directory)
        # generate a file list
        filelist = get_file_list(fulldir, recursive=True)
        # construct log message
        wmsg = 'Displaying first {0} files in directory="{1}"'
        wmsgs = ['', wmsg.format(HARD_DISPLAY_LIMIT, fulldir), '']
        for filename in filelist:
            wmsgs.append('\t' + filename)
        WLOG('', self.recipe.drs_params['LOG_OPT'], wmsgs)

    def __call__(self, parser, namespace, values, option_string=None):
        # check for help
        parser.has_help()
        # get drs parameters
        self.recipe = parser.recipe
        # display listing
        self.display_listing(namespace)
        # quit after call
        parser.exit()


# =============================================================================
# Define Object Classes
# =============================================================================
class DrsArgument(object):
    def __init__(self, name, kind, **kwargs):
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
        # deal with name
        # get argument name
        self.argname = str(name)
        # get full name
        self.name = name
        while self.name.startswith('-'):
            self.name = self.name[1:]
        # get kind
        if kind in ['arg', 'kwarg', 'special']:
            self.kind = kind
        else:
            emsg = '"kind" must be "arg" or "kwarg" or "special"'
            self.exception(emsg)
        # get position
        self.pos = kwargs.get('pos', None)
        # add names from altnames
        self.names = [self.argname] + kwargs.get('altnames', [])
        # get dtype
        self.dtype = kwargs.get('dtype', None)
        # get options
        self.options = kwargs.get('options', None)
        # get help str
        self.helpstr = kwargs.get('helpstr', '')
        # get files
        self.files = kwargs.get('files', [])
        # get file logic
        self.filelogic = kwargs.get('filelogic', 'inclusive')
        if self.filelogic not in ['inclusive', 'exclusive']:
            emsg = ('"filelogic" must equal "inclusive" '
                    'or "exclusive" only. '
                    'Current value is "{0}"'.format(self.filelogic))
            self.exception(emsg)
        # deal with no default/default_ref for kwarg
        if kind == 'kwarg':
            if ('default' not in kwargs) and ('default_ref' not in kwargs):
                emsg = ('**kwargs must contain either "default"'
                        ' or "default_ref" for full definition of argument.')
                self.exception(emsg)
        # get default
        self.default = kwargs.get('default', None)
        # get default_ref
        self.default_ref = kwargs.get('default_ref', None)



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
            self.props['action'] = CheckType
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

    def exception(self, message):
        log_opt = 'DrsArgument[{0}] Error'.format(self.name)
        WLOG('error', log_opt, message)

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
        elif name.strip().endswith('.py'):
            self.name = name.split('.py')[0]
            while self.name.endswith('.py'):
                self.name = self.name.split('.py')[0]
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
        # get drs parameters
        self.drs_params = ParamDict()

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
        argument = DrsArgument(name, kind='arg', **kwargs)
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
        keywordargument = DrsArgument(name, kind='kwarg', **kwargs)
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
        listing = DrsArgument(name, kind='special',
                              altnames=listingprops['altnames'])
        listing.assign_properties(listingprops)
        self.specialargs[name] = listing

    def get_drs_params(self, quiet=False):
        func_name = __NAME__ + '.DrsRecipe.get_drs_params()'
        const_name = 'spirouConfig.Constants'
        # Get config parameters from primary file
        try:
            self.drs_params, warn_messages = spirouConfig.ReadConfigFile()
        except ConfigError as e:
            WLOG(e.level, self.__error__(), e.message)
            self.drs_params, warn_messages = None, []
        # ---------------------------------------------------------------------
        # log warning messages
        if len(warn_messages) > 0:
            WLOG('warning', DPROG, warn_messages)
        # ---------------------------------------------------------------------
        # set recipe name
        self.drs_params['RECIPE'] = self.name
        self.drs_params.set_source('RECIPE', func_name)
        # ---------------------------------------------------------------------
        # get variables from spirouConst
        self.drs_params['DRS_NAME'] = CONSTANTS.NAME()
        self.drs_params['DRS_VERSION'] = CONSTANTS.VERSION()
        self.drs_params.set_sources(['DRS_NAME', 'DRS_VERSION'], const_name)
        # get program name
        self.drs_params['PROGRAM'] = CONSTANTS.PROGRAM(self.drs_params)
        self.drs_params.set_source('program', func_name)
        # get the logging option
        self.drs_params['LOG_OPT'] = self.drs_params['PROGRAM']
        self.drs_params.set_source('LOG_OPT', func_name)
        # check input parameters
        self.drs_params = spirouConfig.CheckCparams(self.drs_params)
        # ---------------------------------------------------------------------
        # if DRS_INTERACTIVE is not True then DRS_PLOT should be turned off too
        if not self.drs_params['DRS_INTERACTIVE']:
            self.drs_params['DRS_PLOT'] = 0
        # ---------------------------------------------------------------------
        # set up array to store inputs/outputs
        self.drs_params['INPUTS'] = OrderedDict()
        self.drs_params['OUTPUTS'] = OrderedDict()
        self.drs_params.set_sources(['INPUTS', 'OUTPUTS'], func_name)
        # ---------------------------------------------------------------------
        # load ICDP config file
        logthis = not quiet
        self.drs_params = load_other_config_file(self.drs_params, 'ICDP_NAME',
                                                 required=True, logthis=logthis)
        # ---------------------------------------------------------------------
        # load keywords
        try:
            kout = spirouConfig.GetKeywordArguments(self.drs_params)
            self.drs_params, warnlogs = kout
            # print warning logs
            for warnlog in warnlogs:
                WLOG('warning', self.__error__(), warnlog)
        except spirouConfig.ConfigError as e:
            WLOG(e.level, DPROG, e.message)

    def __error__(self):
        """
        The option log for WLOG for all errors in class

        :return log_opt: string, the log_opt message for WLOG
        """
        return DPROG

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


# =============================================================================
# Define parser functions (to link from classes to argparse
# =============================================================================
def recipe_setup(recipe, fkwargs):
    """
    Interface between "recipe", inputs to function ("fkwargs") and argparse
    parser (inputs from command line)

    :param recipe: DrsRecipe instance, the Drs Recipe object
    :param fkwargs: dictionary, a dictionary where the keys match
                    arguments/keyword arguments in recipe (without -/--), and
                    the values are those to set in the output
                    (set to None for not value set)

    :return params:  dictionary, a dictionary where the keys match arguments/
                     keywords (without -/--) and values are the values to be
                     used for this recipe
    """
    # set up storage for arguments
    desc = recipe.description
    parser = DRSArgumentParser(recipe, description=desc)
    # deal with function call
    recipe.parse_args(fkwargs)
    # -------------------------------------------------------------------------
    # add arguments from recipe
    for rarg in recipe.args:
        # extract out name and kwargs from rarg
        rname = recipe.args[rarg].names
        rkwargs = recipe.args[rarg].props
        # parse into parser
        parser.add_argument(*rname, **rkwargs)
    # -------------------------------------------------------------------------
    # add keyword arguments
    for rarg in recipe.kwargs:
        # extract out name and kwargs from rarg
        rname = recipe.kwargs[rarg].names
        rkwargs = recipe.kwargs[rarg].props
        # parse into parser
        parser.add_argument(*rname, **rkwargs)
    # add special arguments
    for rarg in recipe.specialargs:
        # extract out name and kwargs from rarg
        rname = recipe.specialargs[rarg].names
        rkwargs = recipe.specialargs[rarg].props
        # parse into parser
        parser.add_argument(*rname, **rkwargs)
    # get params
    params = vars(parser.parse_args(args=recipe.str_arg_list))
    del parser
    # return parameters
    return params


# =============================================================================
# Define check functions
# =============================================================================
def check_for_file(argname, idnum, path, log_opt, kind=None):

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
        wmsg = 'Arg "{0}"[{1}]: File "{2}" exists in directory "{3}"' + kindstr
        WLOG('', log_opt, wmsg.format(argname, idnum, filename, directory))
        # return True and filename
        return True, os.path.realpath(raw_files[0])

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
            # if directory is not None:
            #     if directory_it != directory:
            #         emsg = ('Wildcard Error: Can only have files from one '
            #                 'directory. Multiple found')
            #         WLOG('error', log_opt, emsg)
            # else:
            #     directory = str(directory_it)
            directory = str(directory_it)
            # add to list of files (removing relative paths)
            files.append(os.path.realpath(raw_file))
        # log message
        wmsgs = ['Arg "{0}"[{1}]: Files found to exist (Abs. path + wildcard):'
                 ''.format(argname, idnum)]
        for raw_file in raw_files:
            wmsgs.append('\t' + os.path.realpath(raw_file))
        WLOG('', log_opt, wmsgs)
        # return True, filename and new idnum
        return True, files


def check_file_extension(filename, ext):

    # set error messages empty
    emsgs = []
    # check if we have an extension
    if ext is None:
        return emsgs
    # check file extension
    if not filename.endswith(ext):
        # add why it failed
        emsgs.append('\tFile must end with "{0}"'.format(ext))
    # return error messages
    return emsgs


def check_file_header(drs_file, errors, argname, idnum, recipe, value, log_opt):
    # get recipe
    params = recipe.drs_params
    recipename = recipe.name
    # get required keys
    rkeys = drs_file.required_header_keys
    # loop around keys and check that they are in
    emsgs = []
    for drskey in rkeys:
        # get key from drs_params
        if drskey in params:
            key = params[drskey][0]
        else:
            key = drskey
        # find if key found in header
        if key not in drs_file.header:
            emsgs.append('Key {0} not found in header'.format(key))

    # if we found errors in header key print these errors
    if len(emsgs) > 0:
        print_check_error(argname, idnum, drs_file.filename, recipename, errors,
                          value, log_opt)
    # get error storage
    if len(errors) == 3:
        keys, rvalues, values = errors
    else:
        keys, rvalues, values = [], [], []
    # assume we have found the value
    found = True
    # search for errors in file type
    for drskey in rkeys:
        # get key from drs_params
        if drskey in params:
            key = params[drskey][0]
        else:
            key = drskey
        # get value and required value
        value = drs_file.header[key].strip()
        rvalue = rkeys[drskey].strip()
        # add to error storage
        keys.append(key)
        values.append(value)
        rvalues.append(rvalue)

        # check if key is in file header
        if key in drs_file.header:
            # check if key is correct
            if rvalue != value:
                found = False
        else:
            found = False
    # reconstruct error array
    errors = [keys, rvalues, values]
    # return found and the error array
    return found, errors


def check_exclusivity(drs_file, correct_file, logic, idtype):
    # set up empty error messages
    emsgs = []
    # skip blank ftype
    if idtype is None:
        return correct_file, emsgs
    # if we have a ftype and our file type must be exclusive
    # then we must match the filetype
    if logic == 'exclusive':
        # match by name of file
        cond = drs_file.name == idtype.name
        correct_file = correct_file and cond
        if not cond:
            emsgs.append('File identified as "{0}" however first file '
                         'identified as "{1}" - files must match'
                         ''.format(drs_file.name, idtype.name))
    elif logic == 'inclusive':
        pass
    else:
        correct_file = False
        emsgs.append('logic = "{0}" is not understood must be "exclusive" or'
                     ' "inclusive".'.format(logic))

    # return check value and error messages
    return correct_file, emsgs


# =============================================================================
# Define worker functions
# =============================================================================
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


def get_input_dir(recipe):
    # check if "input_dir" is in namespace
    input_dir_pick = recipe.inputdir.upper()
    # get log_opt
    log_opt = recipe.drs_params['LOG_OPT']
    # get the input directory from recipe.inputdir keyword
    if input_dir_pick == 'RAW':
        input_dir = recipe.drs_params['DRS_DATA_RAW']
    elif input_dir_pick == 'TMP':
        input_dir = recipe.drs_params['DRS_DATA_WORKING']
    elif input_dir_pick == 'REDUCED':
        input_dir = recipe.drs_params['DRS_DATA_REDUC']
    # if not found produce error
    else:
        emsg1 = ('Recipe definition error: "inputdir" must be either'
                ' "RAW", "REDUCED" or "TMP".')
        emsg2 = '\tCurrently has value="{0}"'.format(input_dir_pick)
        WLOG('error', log_opt, [emsg1, emsg2])
        input_dir = None
    # return input_dir
    return input_dir


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
    props['help'] = 'List the files in the given input directory'
    return props


def load_other_config_file(p, key, logthis=True, required=False):
    """
    Load a secondary configuration file from p[key] with wrapper to deal
    with ConfigErrors (pushed to WLOG)

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                log_opt: string, log option, normally the program name
                key: "key" defined in call

    :param key: string, the key in "p" storing the location of the secondary
                configuration file
    :param logthis: bool, if True loading of this config file is logged to
                    screen/log file
    :param required: bool, if required is True then the secondary config file
                     is required for the DRS to run and a ConfigError is raised
                     (program exit)

    :return p: parameter, dictionary, the updated parameter dictionary with
               the secondary configuration files loaded into it as key/value
               pairs
    """
    # try to load config file from file
    try:
        pp, lmsgs = spirouConfig.LoadConfigFromFile(p, key, required=required,
                                                    logthis=logthis)
    except spirouConfig.ConfigError as e:
        WLOG(e.level, p['LOG_OPT'], e.message)
        pp, lmsgs = ParamDict(), []

    # log messages caught in loading config file
    if len(lmsgs) > 0:
        WLOG('', DPROG, lmsgs)
    # return parameter dictionary
    return pp


def print_check_error(argname, idnum, filename, recipename, errors,
                      value, log_opt):

    # construct main error message
    eargs = [argname, idnum, filename, recipename]
    emsgs = ['Arg "{0}"[{1}]: File "{2}" not valid for recipe "{3}"'
             ''.format(*eargs)]
    # add addition error information
    for error in errors:
        emsgs.append('\t' + error)
    # add warning for wildcards
    if '*' in value:
        wmsg = 'Arg "{0}"[{1}]: Wildcards found in "{0}"'
        WLOG('warning', log_opt, wmsg.format(argname, idnum, value))
    # log error
    WLOG('error', log_opt, emsgs, wrap=False)


# =============================================================================
# End of code
# =============================================================================
