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
__NAME__ = 'cal_preprocess_spirou.py'
# Get Logging function
WLOG = spirouCore.wlog
# get print colours
BCOLOR = spirouConfig.Constants.BColors
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
        # force super initialisation
        argparse.Action.__init__(self, *args, **kwargs)

    def check_file(self, filename):
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
        cond1, newfilename = check_for_file(filename, log_opt)
        if cond1:
            return newfilename, None
        # step 2: check if file is in input_dir
        input_path = os.path.join(input_dir, directory, filename)
        cond2, newfilename = check_for_file(input_path, log_opt)
        if cond2:
            return newfilename, input_path
        # step 3: check if file is valid if we add ".fits"
        filename1 = filename + ext
        input_path1 = os.path.join(input_dir, directory, filename1)
        cond3, newfilename = check_for_file(input_path1, log_opt)
        if cond3:
            return newfilename, input_path1
        # step 4: return error message
        else:
            path = os.path.join(input_dir, directory)

            emsgs = ['Argument Error: File "{0}" was not found in {1}'
                     ''.format(filename, path),
                     '\tSome available files are as follows:']
            # get some available directories
            filelist = get_file_list(path, limit, ext)
            # loop around night names and add to message
            for file_it in filelist:
                emsgs.append('\t\t {0}'.format(file_it))
            WLOG('error', log_opt, emsgs)

    def check_drs_file(self, path, files):
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

        # loop around each file
        for filename in files:
            # get extension
            ext = ''
            if len(arg.files) > 0:
                if arg.files[0].ext != '':
                    ext = arg.files[0].ext
            # if file is not a fits file do not check it
            if ext != 'fits':
                continue

            # make path
            filepath = os.path.join(path, filename)
            # try to open header of file
            try:
                header =



    def __call__(self, parser, namespace, values, option_string=None):
        # get drs parameters
        self.drs_params = parser.drs_params
        # get the namespace
        self.namespace = namespace
        # get the input values
        if type(values) == list:
            files = []
            # must loop around values
            for value in values:
                # check file could return list or string
                file_it, fpath = self.check_file(value)
                file_it = self.check_drs_file(fpath, file_it)
                # must add to files depending on whether list or string
                if type(file_it) is list:
                    files += file_it
                else:
                    files.append(file_it)
        else:
            files, fpath = self.check_file(values)
            files = self.check_drs_file(fpath, files)
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


class DrsArgument:
    def __init__(self, name, **kwargs):
        # get argument name
        self.argname = name
        # get full name
        self.name = name
        while self.name.startswith('-'):
            self.name = self.name[1:]
        # get position
        self.pos = kwargs.get('pos', None)
        # add names from altnames
        self.names = [name] + kwargs.get('altnames', [])
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
        # set empty
        self.props = dict()


    def make_properties(self):
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
            self.pass_arg(self.args[argname], values)
        for kwargname in self.kwargs:
            # check if key in dictionary
            if kwargname not in dictionary:
                continue
            # get value(s)
            values = dictionary[kwargname]
            # pass this argument
            self.pass_arg(self.kwargs[kwargname], values)
        # check if we have parameters
        if len(self.str_arg_list) == 0:
            self.str_arg_list = None

    def pass_arg(self, arg, values):
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
                self.str_arg_list.append(strfmt.format(strarg))
        else:
            strarg = [arg.argname, values]
            self.str_arg_list.append(strfmt.format(strarg))


class DrsInput:
    def __init__(self, name, ext):
        # define a name
        self.name = name
        # define the extension
        self.ext = ext


class DrsFitsFile(DrsInput):
    def __init__(self, name, **kwargs):
        # define a name
        self.name = name
        # get super init
        super(DrsInput).__init__(name, 'fits')
        # add header
        self.header = dict()
        # add values to the header
        for kwarg in kwargs:
            self.header[kwarg] = kwargs[kwarg]

    def check(self, header):
        # store fail messages
        fail_msgs = []
        # loop around keys to check
        for key in self.header:
            # check whether key is in header
            if key in header:
                # check if we are checking a list
                if type(self.header[key]) is not list:
                    items = [self.header[key]]
                else:
                    items = self.header[key]
                # find the file
                correct = False
                for item in items:
                    if item == key:
                        correct = True
                # add to the fail msgs
                if not correct:
                    msg = 'Key {0} not equal to {1}'
                    margs = [key, ' , '.join(items)]
                    fail_msgs.append(msg.format(*margs))
            else:
                fail_msgs.append('Key {0} not in header'.format(key))

        found = len(fail_msgs) == 0
        # return found and fail_msgs
        return found, fail_msgs





# =============================================================================
# Define functions
# =============================================================================
def check_for_file(path, log_opt):

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
        wmsg = 'File "{0}" exists in directory "{1}"'
        WLOG('', log_opt, wmsg.format(filename, directory))
        # return True and filename
        return True, filename

    # else we have multiple files (from wild cards)
    else:
        # set up storage
        files = []
        directory = None
        # loop around raw files
        for raw_file in raw_files:
            # get filename
            filename = os.path.basename(raw_file)
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
            files.append(filename)
        # log message
        wmsg = ['Files exists (Absolute path + wildcard):']
        for raw_file in raw_files:
            wmsg.append('\t' + raw_file)

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


def get_file_list(path, limit, ext=None):
    raw_file_list = os.listdir(path)
    file_list = []
    for raw_file in raw_file_list:
        # skip directories
        if os.path.isdir(raw_file):
            continue
        # skip bad extensions
        if ext is not None or ext != '':
            if not raw_file.endswith(ext):
                continue
        # do not display all
        if len(file_list) > limit:
            file_list.append('...')
            return file_list
        # append files to list
        file_list.append(raw_file)

    # if empty list add none found
    if len(file_list) == 0:
        file_list = ['No valid files found.']
    # return night_dirs
    return file_list


# =============================================================================
# End of code
# =============================================================================
