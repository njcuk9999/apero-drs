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
import glob

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

        # get parameterse from drs_params
        log_opt = self.drs_params['LOG_OPT']
        # construct error message
        emsg1 = 'Argument Error:'
        emsg2 = '\t {0}'.format(message)
        emsg3 = ''
        emsg4 = self.format_help()
        # log message
        WLOG('error', log_opt, [emsg1, emsg2, emsg3, emsg3, emsg4])

    def _print_message(self, message, file=None):
        # get parameterse from drs_params
        log_opt = self.drs_params['LOG_OPT']
        # log message
        WLOG('warning', log_opt, message)


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
        self.drs_params['RECIPE']['extension'] = ''
        # force super initialisation
        argparse.Action.__init__(self, *args, **kwargs)

    def check_file(self, filename):
        # check if "input_dir" is in namespace
        input_dir = getattr(self.namespace, 'input_dir', '')
        # check if "directory" is in namespace
        directory = getattr(self.namespace, 'directory', '')
        # get display limit
        limit = self.drs_params['DRS_NIGHT_NAME_DISPLAY_LIMIT']
        # check if extension is in recipe
        if self.drs_params['RECIPE']['extension'] != '':
            ext = '.' + self.drs_params['RECIPE']['extension']
        else:
            ext = ''
        # get parameterse from drs_params
        log_opt = self.drs_params['LOG_OPT']
        # step 1: check for wildcards and absolute path
        cond1, newfilename = check_for_file(filename, log_opt)
        if cond1:
            return newfilename
        # step 2: check if file is in input_dir
        input_path = os.path.join(input_dir, directory, filename)
        cond2, newfilename = check_for_file(input_path, log_opt)
        if cond2:
            return newfilename
        # step 3: check if file is valid if we add ".fits"
        filename1 = filename + ext
        input_path1 = os.path.join(input_dir, directory, filename1)
        cond3, newfilename = check_for_file(input_path1, log_opt)
        if cond3:
            return newfilename
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
                file_it = self.check_file(value)
                # must add to files depending on whether list or string
                if type(file_it) is list:
                    files += file_it
                else:
                    files.append(file_it)
        else:
            files = self.check_file(values)
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
    if dtype == 'files':
        props['action'] = CheckFiles
        props['nargs'] = '+'
        props['type'] = str
    elif dtype == 'file':
        props['action'] = CheckFiles
        props['nargs'] = 1
        props['type'] = str
    elif dtype == 'directory':
        props['action'] = CheckDirectory
        props['nargs'] = 1
        props['type'] = str
    elif dtype == 'bool':
        props['action'] = CheckBool
        props['type'] = str
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
