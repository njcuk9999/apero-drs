#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-19 at 12:03

@author: cook
"""
import numpy as np
from astropy import version as av
from astropy.table import Table
import os
from collections import OrderedDict

from . import drs_log
from terrapipe.core import constants
from terrapipe.locale import drs_text
from terrapipe.io import drs_fits

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'drs_file.py'
__INSTRUMENT__ = None
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
TextEntry = drs_text.TextEntry
TextDict = drs_text.TextDict
HelpText = drs_text.HelpDict
# TODO: This should be changed for astropy -> 2.0.1
# bug that hdu.scale has bug before version 2.0.1
if av.major < 2 or (av.major == 2 and av.minor < 1):
    SCALEARGS = dict(bscale=(1.0 + 1.0e-8), bzero=1.0e-8)
else:
    SCALEARGS = dict(bscale=1, bzero=0)
# -----------------------------------------------------------------------------


# =============================================================================
# Define File classes
# =============================================================================
class DrsInputFile:
    def __init__(self, name, **kwargs):
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
        self.ext = kwargs.get('ext', None)
        # allow instance to be associated with a recipe
        self.recipe = kwargs.get('recipe', None)
        # set empty file attributes
        self.filename = kwargs.get('filename', None)
        self.path = kwargs.get('path', None)
        self.basename = kwargs.get('basename', None)
        self.inputdir = kwargs.get('inputdir', None)
        self.directory = kwargs.get('directory', None)
        self.data = kwargs.get('data', None)
        self.header = kwargs.get('header', None)
        self.index = kwargs.get('index', None)
        self.fileset = kwargs.get('fileset', [])
        # allow instance to be associated with a filename
        self.set_filename(kwargs.get('filename', None))

    def set_filename(self, filename):
        """
        Set the filename, basename and directory name from an absolute path

        :param filename: string, absolute path to the file

        :return None:
        """
        # func_name = __NAME__ + '.DrsFitsFile.set_filename()'
        # skip if filename is None
        if filename is None:
            return True
        # set filename, basename and directory name
        self.filename = str(filename)
        self.basename = os.path.basename(filename)
        self.path = os.path.dirname(filename)

    def check_filename(self):
        # check that filename isn't None
        if self.filename is None:
            func = self.__repr__()
            eargs = [func, func + '.set_filename()']
            self.__error__(TextEntry('00-001-00002', args=eargs))

    def set_recipe(self, recipe):
        """
        Set the associated recipe for the file (i.e. gives access to
        drs_parameters etc

        :param recipe: DrsRecipe instance, the recipe object to associate to
                       this file
        :return:
        """
        self.recipe = recipe

    def newcopy(self, **kwargs):
        # copy this instances values (if not overwritten)
        name = kwargs.get('name', self.name)
        kwargs['ext'] = kwargs.get('ext', self.ext)
        kwargs['recipe'] = kwargs.get('recipe', self.recipe)
        kwargs['filename'] = kwargs.get('filename', self.filename)
        kwargs['path'] = kwargs.get('path', self.path)
        kwargs['basename'] = kwargs.get('basename', self.basename)
        kwargs['inputdir'] = kwargs.get('inputdir', self.inputdir)
        kwargs['directory'] = kwargs.get('directory', self.directory)
        kwargs['data'] = kwargs.get('data', self.data)
        kwargs['header'] = kwargs.get('header', self.header)
        kwargs['fileset'] = kwargs.get('fileset', self.fileset)
        # return new instance
        return DrsInputFile(name, **kwargs)

    def check_recipe(self):
        # ---------------------------------------------------------------------
        # check that recipe isn't None
        if self.recipe is None:
            func = self.__repr__()
            eargs = [func, self.filename, func + '.set_filename()']
            self.__error__(TextEntry('00-001-00003', args=eargs))

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

    def __error__(self, messages):
        self.__log__(messages, 'error')

    def __warning__(self, messages):
        self.__log__(messages, 'warning')

    def __message__(self, messages):
        # get log_opt
        if self.recipe is not None:
            params = self.recipe.drs_params
        else:
            params = None
        # print and log via wlogger
        WLOG(params, '', messages)

    def __log__(self, messages, kind):
        # format initial error message
        m0args = [kind.capitalize(), self.__repr__()]
        message0 = TextEntry('{0}: {1}'.format(*m0args))

        # append initial error message to messages
        messages = message0 + messages
        # get log_opt
        if self.recipe is not None:
            params = self.recipe.drs_params
        else:
            params = None
        # print and log via wlogger
        WLOG(params, kind, messages)

    def addset(self, drsfile):
        """
        For generic Input files only
        Add to a list of associated drs files

        :param drsfile:
        :return:
        """
        self.fileset.append(drsfile)

    def copyother(self, drsfile, **kwargs):
        # check recipe has been set
        if 'recipe' not in kwargs:
            self.check_recipe()
        # check file has been read
        drsfile.read()
        # set empty file attributes
        nkwargs = dict()
        nkwargs['name'] = kwargs.get('name', self.name)
        nkwargs['recipe'] = kwargs.get('recipe', self.recipe)
        nkwargs['filename'] = kwargs.get('filename', drsfile.filename)
        nkwargs['path'] = kwargs.get('path', drsfile.path)
        nkwargs['basename'] = kwargs.get('basename', drsfile.basename)
        nkwargs['inputdir'] = kwargs.get('inputdir', drsfile.inputdir)
        nkwargs['directory'] = kwargs.get('directory', drsfile.directory)
        nkwargs['data'] = kwargs.get('data', drsfile.data)
        nkwargs['header'] = kwargs.get('header', drsfile.header)
        nkwargs['fileset'] = kwargs.get('fileset', self.fileset)
        # return new instance of DrsFitsFile
        return DrsInputFile(**nkwargs)

    # -------------------------------------------------------------------------
    # file checking
    # -------------------------------------------------------------------------
    def check_another_file(self, input_file):
        """
        Checks that another file is consistent with this file type

        :param input_file: DrsInputFile
        :returns: True or False and the reason why (if False)
        """
        # 1. check extension
        cond1, msg1 = self.has_correct_extension(input_file.ext)
        if not cond1:
            return False, msg1
        # 2. check file header keys exist
        cond2, msg2 = self.header_keys_exist(None)
        if not cond2:
            return False, msg2
        # 3. check file header keys are correct
        cond3, msg3 = self.has_correct_header_keys(None)
        if not cond2:
            return False, msg3
        # if 1, 2 and 3 pass return True
        return True, None

    def check_file(self):
        """
        Checks that this file is correct

        :returns: True or False and the reason why (if False)
        """
        # 1. check extension
        cond1, msg1 = self.has_correct_extension()
        if not cond1:
            return False, msg1
        # 2. check file header keys exist
        cond2, msg2 = self.header_keys_exist()
        if not cond2:
            return False, msg2
        # 3. check file header keys are correct
        cond3, msg3 = self.has_correct_header_keys()
        if not cond2:
            return False, msg3
        # if 1, 2 and 3 pass return True
        return True, None

    def has_correct_extension(self, ext=None):
        return True, None

    def header_keys_exist(self, header=None):
        return True, None

    def has_correct_header_keys(self, header=None):
        return True, None

    # -------------------------------------------------------------------------
    # file checking (old)
    # -------------------------------------------------------------------------
    def check_file_exists(self, quiet=False):
        cond = os.path.exists(self.filename)
        if cond:
            eargs = [self.basename, self.path]
            emsg = TextEntry('09-000-00001', args=eargs)
        else:
            eargs = [self.basename, self.path]
            emsg = TextEntry('09-000-00002', args=eargs)
        # deal with printout and return
        if (not cond) and (not quiet):
            self.__error__(emsg)
        elif not quiet:
            self.__message__(emsg)
        return cond, emsg

    def check_file_extension(self, quiet=False):
        if self.ext is None:
            msg = TextEntry('09-000-00003', args=[self.basename])
            cond = True
        elif self.filename.endswith(self.ext):
            msg = TextEntry('09-000-00004', args=[self.basename, self.ext])
            cond = True
        else:
            msg = TextEntry('09-000-00005', args=[self.basename, self.ext])
            cond = False
        # deal with printout and return
        if (not cond) and (not quiet):
            self.__error__(msg)
        elif not quiet:
            self.__message__(msg)
        return cond, msg

    def check_file_header(self, quiet=False):
        return True, TextEntry('')


class DrsFitsFile(DrsInputFile):
    def __init__(self, name, **kwargs):
        """
        Create a DRS Fits File Input object

        :param name: string, the name of the DRS input file

        :param kwargs: currently allowed kwargs are:

            - ext: string or None, the extension for the DRS input file
                   (without the '.' i.e. A.txt  ext='txt'). This will be
                   checked if used in a DrsArgument is not None.

            - fiber: string or None, the fiber of the Fits File.

            - KW_{str}: string, any keywordstore variable name currently
                        defined in spirouKeywords.py. If used in DrsArgument
                        the HEADER of this fits file must have the value
                        of this KW_{str} to be a valid argument.

            - KW_OUTPUT: this will set the output type for this file (i.e.
                         file.outtag
        """
        # define a name
        self.name = name
        # get super init
        DrsInputFile.__init__(self, name, **kwargs)
        # if ext in kwargs then we have a file extension to check
        self.ext = kwargs.get('ext', '.fits')
        self.inext = kwargs.get('inext', '.fits')
        # get fiber type (if set)
        self.fiber = kwargs.get('fiber', None)
        # get tag
        self.outfunc = kwargs.get('outfunc', None)
        self.outtag = kwargs.get('KW_OUTPUT', 'UNKNOWN')
        self.dbname = kwargs.get('dbname', None)
        self.dbkey = kwargs.get('dbkey', None)
        # add header
        self.required_header_keys = kwargs.get('rkeys', dict())
        if len(self.required_header_keys) == 0:
            self.get_header_keys(kwargs)
        # set empty fits file storage
        self.data = kwargs.get('data', None)
        self.header = kwargs.get('header', None)
        self.index = kwargs.get('index', None)
        # set additional attributes
        self.shape = kwargs.get('shape', None)
        self.hdict = kwargs.get('hdict', drs_fits.Header())
        self.output_dict = kwargs.get('output_dict', OrderedDict())
        self.datatype = kwargs.get('datatype', 'image')
        self.dtype = kwargs.get('dtype', None)
        self.data_array = None
        self.header_array = None

    def get_header_keys(self, kwargs):
        # add values to the header
        for kwarg in kwargs:
            if 'KW_' in kwarg.upper():
                self.required_header_keys[kwarg] = kwargs[kwarg]

    def newcopy(self, **kwargs):
        """
        Make a new copy of this class (using all default parameters
        set when constructed

        :param kwargs:
            - name: string, the name of the DRS input file
            - ext: string or None, the extension for the DRS input file
                   (without the '.' i.e. A.txt  ext='txt'). This will be
                   checked if used in a DrsArgument if not None.

            - fiber: string or None, the fiber of the Fits File.

            - KW_{str}: string, any keywordstore variable name currently
                        defined in spirouKeywords.py. If used in DrsArgument
                        the HEADER of this fits file must have the value
                        of this KW_{str} to be a valid argument.

            - KW_OUTPUT: this will set the output type for this file (i.e.
                         file.outtag

        :return:
        """
        # copy this instances values (if not overwritten)
        name = kwargs.get('name', self.name)
        kwargs['ext'] = kwargs.get('ext', self.ext)
        kwargs['recipe'] = kwargs.get('recipe', self.recipe)
        kwargs['filename'] = kwargs.get('filename', self.filename)
        kwargs['path'] = kwargs.get('path', self.path)
        kwargs['basename'] = kwargs.get('basename', self.basename)
        kwargs['inputdir'] = kwargs.get('inputdir', self.inputdir)
        kwargs['directory'] = kwargs.get('directory', self.directory)
        kwargs['data'] = kwargs.get('data', self.data)
        kwargs['header'] = kwargs.get('header', self.header)
        kwargs['fileset'] = kwargs.get('fileset', self.fileset)
        kwargs['check_ext'] = kwargs.get('check_ext', self.ext)
        kwargs['fiber'] = kwargs.get('fiber', self.fiber)
        kwargs['outtag'] = kwargs.get('KW_OUTPUT', self.outtag)
        kwargs['outfunc'] = kwargs.get('outfunc', self.outfunc)
        kwargs['dbname'] = kwargs.get('dbname', self.dbname)
        kwargs['dbkey'] = kwargs.get('dbkey', self.dbkey)
        kwargs['datatype'] = kwargs.get('datatype', self.datatype)
        kwargs['dtype'] = kwargs.get('dtype', self.dtype)
        for key in self.required_header_keys:
            kwargs[key] = self.required_header_keys[key]
        self.get_header_keys(kwargs)
        # return new instance
        return DrsFitsFile(name, **kwargs)

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

    def set_required_key(self, key, value):
        if 'KW_' in key:
            self.required_header_keys[key] = value

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

    def copyother(self, drsfile, **kwargs):
        # check recipe has been set
        if 'recipe' not in kwargs:
            self.check_recipe()
        # check file has been read
        drsfile.read()
        # set empty file attributes
        nkwargs = dict()
        nkwargs['name'] = kwargs.get('name', self.name)
        nkwargs['recipe'] = kwargs.get('recipe', self.recipe)
        nkwargs['fiber'] = kwargs.get('fiber', self.fiber)
        nkwargs['rkeys'] = kwargs.get('rkeys', self.required_header_keys)
        nkwargs['filename'] = kwargs.get('filename', drsfile.filename)
        nkwargs['path'] = kwargs.get('path', drsfile.path)
        nkwargs['basename'] = kwargs.get('basename', drsfile.basename)
        nkwargs['inputdir'] = kwargs.get('inputdir', drsfile.inputdir)
        nkwargs['directory'] = kwargs.get('directory', drsfile.directory)
        nkwargs['data'] = kwargs.get('data', drsfile.data)
        nkwargs['header'] = kwargs.get('header', drsfile.header)
        nkwargs['shape'] = kwargs.get('shape', drsfile.shape)
        nkwargs['hdict'] = kwargs.get('hdict', drsfile.hdict)
        nkwargs['output_dict'] = kwargs.get('output_dict', drsfile.output_dict)
        nkwargs['fileset'] = kwargs.get('fileset', self.fileset)
        nkwargs['outfunc'] = kwargs.get('outfunc', self.outfunc)
        nkwargs['dbname'] = kwargs.get('dbname', self.dbname)
        nkwargs['dbkey'] = kwargs.get('dbkey', self.dbkey)
        nkwargs['datatype'] = kwargs.get('datatype', self.datatype)
        nkwargs['dtype'] = kwargs.get('dtype', self.dtype)
        # return new instance of DrsFitsFile
        return DrsFitsFile(**nkwargs)

    # -------------------------------------------------------------------------
    # file checking
    # -------------------------------------------------------------------------
    def check_file(self):
        """
        Checks that this file is correct

        :returns: True or False and the reason why (if False)
        """
        # 1. check extension
        cond1, msg1 = self.has_correct_extension()
        if not cond1:
            return False, msg1
        # 2. check file header keys exist
        cond2, msg2 = self.hkeys_exist()
        if not cond2:
            return False, msg2
        # 3. check file header keys are correct
        cond3, msg3 = self.has_correct_hkeys()
        if not cond3:
            return False, msg3
        # if 1, 2 and 3 pass return True
        return True, None

    def has_correct_extension(self, filename=None, ext=None, argname=None):
        # deal with no input extension
        if ext is None:
            ext = self.ext
        # deal with no input filename
        if filename is None:
            filename = self.filename
            basename = self.basename
        else:
            basename = os.path.basename(filename)
        # -----------------------------------------------------------------
        # deal with no argument name
        if argname is None:
            argname = TextEntry('40-001-00018')
        # -----------------------------------------------------------------
        # check recipe has been set
        self.check_recipe()
        # get recipe and parameters
        params = self.recipe.drs_params
        # -----------------------------------------------------------------
        # check extension
        if ext is None:
            msg = TextEntry('09-000-00003', args=[basename])
            cond = True
        elif filename.endswith(ext):
            msg = TextEntry('09-000-00004', args=[basename, ext])
            cond = True
        else:
            msg = TextEntry('09-000-00005', args=[basename, ext])
            cond = False
        # if valid return True and no error
        if cond:
            dargs = [argname, os.path.basename(filename)]
            WLOG(params, 'debug', TextEntry('90-001-00009', args=dargs),
                 wrap=False)
            return True, msg
        # if False generate error and return it
        else:
            emsg = TextEntry('09-001-00006', args=[argname, ext])
            return False, emsg

    def hkeys_exist(self, header=None, filename=None, argname=None):
        func_name = __NAME__ + 'DrsFitsFile.header_keys_exist()'

        # deal with no input header
        if header is None:
            # check file has been read
            self.read()
            # get header
            header = self.header
        # deal with no input filename
        if filename is None:
            basename = self.basename
        else:
            basename = os.path.basename(filename)
        # -----------------------------------------------------------------
        # check recipe has been set
        self.check_recipe()
        # get recipe and parameters
        params = self.recipe.drs_params
        rkeys = self.required_header_keys
        # -----------------------------------------------------------------
        # deal with no argument name
        if argname is None:
            argname = TextEntry('40-001-00018')
        # -----------------------------------------------------------------
        # Check that required keys are in header
        for drskey in rkeys:
            # check whether header key is in param dict (i.e. from a
            #    keywordstore) or whether we have to use the key as is
            if drskey in params:
                key = params[drskey][0]
                source = params.sources[drskey]
            else:
                key = drskey
                source = func_name
            # deal with empty key
            if (key is None) or key == '':
                eargs = [key, drskey, source]
                WLOG(params, 'error', TextEntry('00-006-00011', args=eargs))
            # check if key is in header
            if key not in header:
                eargs = [argname, key]
                emsg = TextEntry('09-001-00007', args=eargs)
                return False, emsg
            else:
                dargs = [argname, key, basename]
                WLOG(params, 'debug', TextEntry('90-001-00010', args=dargs),
                     wrap=False)

        return True, None

    def has_correct_hkeys(self, header=None, argname=None):
        func_name = __NAME__ + 'DrsFitsFile.has_correct_header_keys()'
        # deal with no input header
        if header is None:
            # check file has been read
            self.read()
            # get header
            header = self.header
        # -----------------------------------------------------------------
        # check recipe has been set
        self.check_recipe()
        # get recipe and parameters
        params = self.recipe.drs_params
        rkeys = self.required_header_keys
        # -----------------------------------------------------------------
        # deal with no argument name
        if argname is None:
            argname = TextEntry('40-001-00018')
        # -----------------------------------------------------------------
        # search for correct value for each header key
        found = True
        # storage
        errors = dict()
        # -----------------------------------------------------------------
        # loop around required keys
        for drskey in rkeys:
            # check whether header key is in param dict (i.e. from a
            #    keywordstore) or whether we have to use the key as is
            if drskey in params:
                key = params[drskey][0]
            else:
                key = drskey
            # get value and required value
            value = header[key].strip()
            rvalue = rkeys[drskey].strip()
            # check if key is valid
            if rvalue != value:
                dargs = [argname, key, rvalue]
                WLOG(params, 'debug', TextEntry('90-001-00011', args=dargs),
                     wrap=False)
                found = False
            else:
                dargs = [argname, key, rvalue]
                WLOG(params, 'debug', TextEntry('90-001-00012', args=dargs),
                     wrap=False)
            # store info
            errors[key] = (found, argname, rvalue, value)

        return found, errors

    # -------------------------------------------------------------------------
    # fits file checking (OLD)
    # -------------------------------------------------------------------------
    def check_file_header(self, quiet=False, argname=None):
        """
        Check file header has all required header keys
        :param quiet:
        :param argname: string, the name of the argument we are checking
                        (for error and debug messages)
        :param debug: bool, if True prints a debug message

        :return:
        """
        func_name = __NAME__ + 'DrsFitsFile.check_file_header()'
        # -----------------------------------------------------------------
        # check file has been read
        self.read()
        # check recipe has been set
        self.check_recipe()
        params = self.recipe.drs_params
        rkeys = self.required_header_keys
        # -----------------------------------------------------------------
        # deal with no argument name
        if argname is None:
            argname = TextEntry('40-001-00018')
        # -----------------------------------------------------------------
        # Step 1: Check that required keys are in header
        for drskey in rkeys:
            # check whether header key is in param dict (i.e. from a
            #    keywordstore) or whether we have to use the key as is
            if drskey in params:
                key = params[drskey][0]
                source = params.sources[drskey]
            else:
                key = drskey
                source = func_name
            # deal with empty key
            if (key is None) or key == '':
                eargs = [key, drskey, source]
                WLOG(params, 'error', TextEntry('00-006-00011', args=eargs))
            # check if key is in header
            if key not in self.header:
                eargs = [argname, key]
                emsg = TextEntry('09-001-00007', args=eargs)
                return [False, True], None, [emsg, None]
            else:
                dargs = [argname, key, os.path.basename(self.filename)]
                WLOG(params, 'debug', TextEntry('90-001-00010', args=dargs),
                     wrap=False)
        # -----------------------------------------------------------------
        # Step 2: search for correct value for each header key
        found = True

        # storage
        errors = dict()

        # loop around required keys
        for drskey in rkeys:
            # check whether header key is in param dict (i.e. from a
            #    keywordstore) or whether we have to use the key as is
            if drskey in params:
                key = params[drskey][0]
            else:
                key = drskey
            # get value and required value
            value = self.header[key].strip()
            rvalue = rkeys[drskey].strip()

            # write error message
            # emsg1 = '{0} Header key {1} value is incorrect'
            # emsg2 = '\tvalue = {2}   required = {3}'
            # eargs = [argstring, key, value, rvalue, self.filename]
            # emsgs = [emsg1.format(*eargs), emsg2.format(*eargs)]

            # check if key is valid
            if rvalue != value:
                dargs = [argname, key, rvalue]
                WLOG(params, 'debug', TextEntry('90-001-00011', args=dargs),
                     wrap=False)
                found = False
            else:
                dargs = [argname, key, rvalue]
                WLOG(params, 'debug', TextEntry('90-001-00012', args=dargs),
                     wrap=False)
            # store info
            errors[key] = (found, argname, rvalue, value)
        # return:
        #       [valid cond1, valid cond2], self, [errors1, errors2]
        if found:
            return [True, True], self, [None, errors]
        else:
            return [True, False], self, [None, errors]

    # -------------------------------------------------------------------------
    # fits file methods
    # -------------------------------------------------------------------------
    def read(self, ext=None, check=True):
        """
        Read this fits file data and header

        :param ext: int or None, the data extension to open
        :param hdr_ext: int, the header extension to open
        :param check: bool, if True checks if data is already read and does
                      not read again, to overwrite/re-read set "check" to False

        :return None:
        """
        func_name = __NAME__ + '.DrsFitsFile.read()'
        # check if we have data set
        if check:
            cond1 = self.data is not None
            cond2 = self.header is not None
            if cond1 and cond2:
                return True
        # get params
        params = self.recipe.drs_params
        # check that filename is set
        self.check_filename()

        # get data format
        if self.datatype == 'image':
            fmt = 'fits-image'
        elif self.datatype == 'table':
            fmt = 'fits-table'
        else:
            fmt = None

        out = drs_fits.read(params, self.filename, getdata=True, gethdr=True,
                            fmt=fmt, ext=ext)

        self.data = out[0]
        self.header = drs_fits.Header.from_fits_header(out[1])
        # set the shape
        if self.data is not None:
            self.shape = self.data.shape

    def read_data(self, ext=0):
        func_name = __NAME__ + '.DrsFitsFile.read_data()'
        # check that filename is set
        self.check_filename()
        # get params
        params = self.recipe.drs_params
        # get data
        data = drs_fits.read(params, self.filename, ext=ext)
        # assign to object
        self.data = data

    def read_header(self, ext=0):
        func_name = __NAME__ + '.DrsFitsFile.read_header()'
        # check that filename is set
        self.check_filename()
        # get params
        params = self.recipe.drs_params
        # get header
        header = drs_fits.read_header(params, self.filename, ext=ext)
        # assign to object
        self.header = header

    def check_read(self):
        # check that data/header/comments is not None
        if self.data is None:
            func = self.__repr__()
            eargs = [func, func + '.read()']
            self.__error__(TextEntry('00-001-00004', args=eargs))

    def read_multi(self, ext=None, check=True):
        func_name = __NAME__ + '.DrsFitsFile.read()'
        # check if we have data set
        if check:
            cond1 = self.data is not None
            cond2 = self.header is not None
            if cond1 and cond2:
                return True
        # get params
        params = self.recipe.drs_params
        # check that filename is set
        self.check_filename()
        # get data format
        out = drs_fits.read(params, self.filename, getdata=True, gethdr=True,
                            fmt='fits-multi')

        self.data = out[0][0]
        self.header = drs_fits.Header.from_fits_header(out[1][0])
        self.data_array = out[0]
        # append headers (as copy)
        self.header_array = []
        for header in out[1]:
            self.header_array.append(drs_fits.Header.from_fits_header(header))
        # set the shape
        if self.data is not None:
            self.shape = self.data.shape

    def update_header_with_hdict(self):
        # deal with unset header
        if self.header is None:
            self.header = drs_fits.Header()
        # add keys from hdict
        for key in self.hdict:
            self.header[key] = (self.hdict[key], self.hdict.comments[key])

    def write(self, dtype=None):
        func_name = __NAME__ + '.DrsFitsFile.write()'
        # get params
        params = self.recipe.drs_params
        # ---------------------------------------------------------------------
        # check that filename is set
        self.check_filename()
        # copy keys from hdict into header
        self.update_header_with_hdict()
        # write to file
        drs_fits.write(params, self.filename, self.data, self.header,
                       self.datatype, self.dtype, func=func_name)
        # ---------------------------------------------------------------------
        # write output dictionary
        self.output_dictionary()
        # add output to outfiles
        params['OUTFILES'][self.basename] = self.output_dict

    def write_multi(self, data_list, header_list=None, datatype_list=None,
                    dtype_list=None):
        func_name = __NAME__ + '.DrsFitsFile.write_multi()'
        # get params
        params = self.recipe.drs_params
        # ---------------------------------------------------------------------
        # check that filename is set
        self.check_filename()
        # copy keys from hdict into header
        self.update_header_with_hdict()
        # ---------------------------------------------------------------------
        # deal with header list being empty
        if header_list is None:
            header_list = []
            for it in range(len(data_list)):
                if self.header is not None:
                    header_list.append(self.header.to_fits_header())
                else:
                    header_list.append(None)
        # deal with datatype_list being empty
        if datatype_list is None:
            datatype_list = []
            for it in range(len(data_list)):
                if isinstance(data_list[it], Table):
                    datatype_list.append('table')
                else:
                    datatype_list.append('image')
        # deal with dtype being empty
        if dtype_list is None:
            dtype_list = [None] * len(data_list)
        # ---------------------------------------------------------------------
        # get data and header lists
        data_list = [self.data] + data_list
        header_list = [self.header] + header_list
        datatype_list = [self.datatype] + datatype_list
        dtype_list = [self.dtype] + dtype_list
        # write to file
        drs_fits.write(params, self.filename, data_list, header_list,
                       datatype_list, dtype_list, func=func_name)
        # ---------------------------------------------------------------------
        # write output dictionary
        self.output_dictionary()
        # add output to outfiles
        params['OUTFILES'][self.basename] = self.output_dict

    def output_dictionary(self):
        """
        Generate the output dictionary (for use while writing)
        Uses OUTPUT_FILE_HEADER_KEYS and DrsFile.hdict to generate an
        output dictionary for this file (for use in indexing)

        Requires DrsFile.filename and DrsFile.recipe to be set

        :return None:
        """
        # check that recipe is set
        self.check_recipe()
        p = self.recipe.drs_params
        pconstant = self.recipe.drs_pconstant
        # get output dictionary
        output_hdr_keys = pconstant.OUTPUT_FILE_HEADER_KEYS(p)
        # loop around the keys and find them in hdict (or add null character if
        #     not found)
        for key in output_hdr_keys:
            if key in self.hdict:
                self.output_dict[key] = str(self.hdict[key])
            else:
                self.output_dict[key] = '--'

    def construct_filename(self, params, **kwargs):
        # set outfile from self
        kwargs['outfile'] = self
        # if we have a function use it
        if self.outfunc is not None:
            abspath = self.outfunc(params, **kwargs)
            self.filename = abspath
            self.basename = os.path.basename(abspath)
        # else raise an error
        else:
            WLOG(params, 'error', TextEntry('00-008-00004'))

    def combine(self, infiles, math='sum', same_type=True):
        func_name = __NAME__ + '.DrsFitsFile.combine()'
        available_math = ['sum', 'add', '+', 'average', 'mean', 'subtract',
                          '-', 'divide', '/', 'multiply', 'times', '*']
        # --------------------------------------------------------------------
        # check that recipe is set
        self.check_recipe()
        params = self.recipe.drs_params
        # check that data is read
        self.check_read()
        # set new data to this files data
        data = self.data
        # --------------------------------------------------------------------
        # combine data
        for infile in infiles:
            # check data is read for infile
            infile.check_read()
            # check that infile matches in name to self
            if (self.name != infile.name) and same_type:
                eargs = [func_name]
                WLOG(params, 'error', TextEntry('00-001-00021', args=eargs))
            # if we want to sum the data
            if math in ['sum', 'add', '+', 'average', 'mean']:
                data += infile.data
            # else if we want to subtract the data
            elif math in ['subtract', '-']:
                data -= infile.data
            # else if we want to divide the data
            elif math in ['divide', '/']:
                data /= infile.data
            # else if we want to multiple the data
            elif math in ['multiply', 'times', '*']:
                data *= infile.data
            # else we have an error in math
            else:
                eargs = [math, available_math, func_name]
                WLOG(params, 'error', TextEntry('', args=eargs))
        # --------------------------------------------------------------------
        # if average/mean then divide by the number of files
        if math in ['average', 'mean']:
            data = data / (len(infiles) + 1)
        # --------------------------------------------------------------------
        # construct keys for new DrsFitsFile
        # set empty file attributes
        nkwargs = dict()
        nkwargs['name'] = self.name
        nkwargs['recipe'] = self.recipe
        nkwargs['fiber'] = self.fiber
        nkwargs['rkeys'] = self.required_header_keys
        nkwargs['filename'] = self.filename
        nkwargs['path'] = self.path
        nkwargs['basename'] = self.basename
        nkwargs['inputdir'] = self.inputdir
        nkwargs['directory'] = self.directory
        nkwargs['data'] = data
        nkwargs['header'] = self.header
        nkwargs['shape'] = data.shape
        nkwargs['hdict'] = self.hdict
        nkwargs['output_dict'] = self.output_dict
        nkwargs['fileset'] = self.fileset
        nkwargs['outfunc'] = self.outfunc
        # return new instance of DrsFitsFile
        return DrsFitsFile(**nkwargs)

    # -------------------------------------------------------------------------
    # fits file header methods
    # -------------------------------------------------------------------------
    def get_key(self, key, has_default=False, default=None,
                        required=True, dtype=float):
        return self.read_header_key(key, has_default, default, required, dtype)

    def read_header_key(self, key, has_default=False, default=None,
                        required=True, dtype=float):
        """
        Looks for a key in DrsFile.header, if has_default is
        True sets value of key to 'default' if not found else if "required"
        logs an error

        :param key: string, key in the dictionary to find first looks in
                            DrsFile.header directly then checks
        :param has_default: bool, if True uses "default" as the value if key
                            not found
        :param default: object, value of the key if not found and
                        has_default is True
        :param required: bool, if True key is required and causes error is
                         missing if False and key not found value is None

        :return value: object, value of DrsFile.header[key] or default (if
                       has_default=True)
        """
        func_name = __NAME__ + '.DrsFitsFile.read_header_key()'
        # check that recipe is set
        self.check_recipe()
        # check that data is read
        self.check_read()
        # check key is valid
        drskey = self._check_key(key)
        # if we have a default key try to get key else use default value
        if has_default:
            value = self.header.get(drskey, default)
        # else we must look for the value manually and handle the exception
        else:
            try:
                value = self.header[drskey]
            except KeyError:
                # if we do not require this keyword don't generate an error
                #   just return None
                if not required:
                    return None
                # else generate an error
                else:
                    if key == drskey:
                        eargs = [drskey, self.filename, func_name]
                        emsg = TextEntry('09-000-00006', args=eargs)
                    else:
                        eargs = [drskey, self.filename, key, func_name]
                        emsg = TextEntry('09-000-00006', args=eargs)
                    self.__error__(emsg)
                    value = None

        # try to convert to dtype else just return as string
        try:
            value = dtype(value)
        except ValueError:
            value = str(value)
        except TypeError:
            value = str(value)

        # return value
        return value

    def read_header_keys(self, keys, has_default=False, defaults=None):
        """
        Looks for a set of keys in DrsFile.header, if has_default is
        True sets value of key to 'default' if not found else if "required"
        logs an error

        :param keys: string, key in the dictionary to find
        :param has_default: bool, if True uses "default" as the value if key
                            not found
        :param defaults: object, value of the key if not found and
                        has_default is True

        :return value: object, value of DrsFile.header[key] or default (if
                       has_default=True)
        """
        func_name = __NAME__ + '.DrsFitsFile.read_header_keys()'
        # check that recipe is set
        self.check_recipe()
        # check that data is read
        self.check_read()
        # make sure keys is a list
        try:
            keys = list(keys)
        except TypeError:
            self.__error__(TextEntry('00-001-00005', args=[func_name]))
        # if defaults is None --> list of Nones else make sure defaults
        #    is a list
        if defaults is None:
            defaults = list(np.repeat([None], len(keys)))
        else:
            try:
                defaults = list(defaults)
                if len(defaults) != len(keys):
                    self.__error__(TextEntry('00-001-00006', args=[func_name]))
            except TypeError:
                self.__error__(TextEntry('00-001-00007', args=[func_name]))
        # loop around keys and look up each key
        values = []
        for k_it, key in enumerate(keys):
            # get the value for key
            v = self.read_header_key(key, has_default, default=defaults[k_it])
            # append value to values list
            values.append(v)
        # return values
        return values

    def read_header_key_1d_list(self, key, dim1, dtype=float):
        """
        Read a set of header keys that were created from a 1D list

        :param key: string, prefix of HEADER key to construct 1D list from
                     key[row number]

        :param dim1: int, the number of elements in dimension 1
                     (number of rows)

        :param dtype: type, the type to force the data to be (i.e. float, int)

        :return values: numpy array (1D), the values force to type = dtype
        """
        func_name = __NAME__ + '.DrsFitsFile.read_header_key_1d_list()'
        # check that data is read
        self.check_read()
        # check key is valid
        drskey = self._check_key(key)
        # create 2d list
        values = np.zeros(dim1, dtype=dtype)
        # loop around the 2D array
        for it in range(dim1):
            # construct the key name
            keyname = '{0}{1}'.format(drskey, it)
            # try to get the values
            try:
                # set the value
                values[it] = dtype(self.header[keyname])
            except KeyError:
                eargs = [keyname, dim1, self.basename, func_name]
                self.__error__(TextEntry('09-000-00008', args=eargs))
                values = None
        # return values
        return values

    def read_header_key_2d_list(self, key, dim1, dim2, dtype=float):
        """
        Read a set of header keys that were created from a 2D list

        :param key: string, prefix of HEADER key to construct 2D list from
                     key[number]

               where number = (row number * number of columns) + column number
               where column number = dim2 and row number = range(0, dim1)

        :param dim1: int, the number of elements in dimension 1
                     (number of rows)
        :param dim2: int, the number of columns in dimension 2
                     (number of columns)

        :param dtype: type, the type to force the data to be (i.e. float, int)

        :return values: numpy array (2D), the values force to type = dtype
        """
        func_name = __NAME__ + '.read_key_2d_list()'
        # check that data is read
        self.check_read()
        # check key is valid
        drskey = self._check_key(key)
        # create 2d list
        values = np.zeros((dim1, dim2), dtype=dtype)
        # loop around the 2D array
        dim1, dim2 = values.shape
        for it in range(dim1):
            for jt in range(dim2):
                # construct the key name
                keyname = '{0}{1}'.format(drskey, it * dim2 + jt)
                # try to get the values
                try:
                    # set the value
                    values[it][jt] = dtype(self.header[keyname])
                except KeyError:
                    eargs = [keyname, dim1, dim2, self.basename, func_name]
                    self.__error__(TextEntry('09-000-00009', args=eargs))
        # return values
        return values

    def _check_key(self, key):
        # get drs parameters
        drs_params = self.recipe.drs_params
        # need to check drs_params for key (if key is not in header)
        if (key not in self.header) and (key in drs_params):
            store = drs_params[key]
            # see if we have key store
            if isinstance(store, list) and len(store) == 3:
                drskey = store[0]
            # if we dont assume we have a string
            else:
                drskey = store
        else:
            drskey = str(key)
        return drskey

    def copy_original_keys(self, drs_file=None, forbid_keys=True, root=None,
                           allkeys=False):
        """
        Copies keys from hdr dictionary to DrsFile.hdict,
        if forbid_keys is True some keys will not be copied
        (defined in spirouConfig.Constants.FORBIDDEN_COPY_KEYS())

        adds keys in form: hdict[key] = (value, comment)

        :param drs_file: DrsFile instance, the file to be used to copy the
                         header keys from (must have read this file to generate
                         the header)

        :param forbid_keys: bool, if True uses the forbidden copy keys
                            (defined in
                               spirouConfig.Constants.FORBIDDEN_COPY_KEYS()
                            to remove certain keys from those being copied,
                            if False copies all keys from input header

        :param root: string, if we have "root" then only copy keywords that
                     start with this string (prefix)

        :return None:
        """
        # get pconstant
        pconstant = self.recipe.drs_pconstant
        # get drs_file header/comments
        if drs_file is None:
            self.check_read()
            fileheader = self.header
        else:
            # check that data/header is read
            drs_file.check_read()
            fileheader = drs_file.header

        def __keep_card(card):
            key = card[0]
            if root is not None:
                if not key.startswith(root):
                    return False
            # skip if key is forbidden key
            if forbid_keys and (key in pconstant.FORBIDDEN_COPY_KEYS()):
                return False
            # skip if key is drs forbidden key (unless allkeys)
            elif (key in pconstant.FORBIDDEN_DRS_KEY()) and (not allkeys):
                return False
            # skip if key added temporarily in code (denoted by @@@)
            elif '@@@' in key:
                return False
            # skip QC keys (unless allkeys)
            elif is_forbidden_prefix(pconstant, key) and (not allkeys):
                return False
            else:
                return True
        # filter and create new header
        copy_cards = filter(__keep_card, fileheader.cards)
        self.hdict = drs_fits.Header(copy_cards)
        # return True to show completed successfully
        return True

    def add_hkey(self, key=None, keyword=None, value=None, comment=None):
        """
        Add a new key to DrsFile.hdict from kwstore. If kwstore is None
        and key and comment are defined these are used instead.

            Each keywordstore is in form:
                [key, value, comment]    where key and comment are strings

            DrsFile.hdict is updated with hdict[key] = (value, comment)

        :param kwstore: list, keyword list (defined in spirouKeywords.py)
                        must be in form [string, value, string]

        :param value: object or None, if any python object (other than None)
                      will set the value of hdict[key] to (value, comment)

        :param key: string or None, if kwstore not defined this is the key to
                    set in hdict[key] = (value, comment)
        :param comment: string or None, if kwstore not define this is the
                        comment to set in hdict[key] = (value, comment)
        :return:
        """
        func_name = __NAME__ + '.DrsFitsFile.add_header_key()'
        # check for kwstore in params
        self.check_recipe()
        params = self.recipe.drs_params
        # if key is set use it (it should be from parameter dictionary
        if key is not None:
            if isinstance(key, str) and (key in params):
                kwstore = params[key]
            elif isinstance(key, list):
                kwstore = list(key)
            else:
                eargs = [key, func_name]
                self.__error__(TextEntry('00-001-00008', args=eargs))
                kwstore = None
        else:
            kwstore = [keyword, value, comment]
        # extract keyword, value and comment and put it into hdict
        if kwstore is not None:
            okey, dvalue, comment = self.get_keywordstore(kwstore, func_name)
        else:
            okey, dvalue, comment = key, None, comment

        # set the value to default value if value is None
        if value is None:
            value = dvalue
        # add to the hdict dictionary in form (value, comment)
        self.hdict[okey] = (value, comment)

    def add_hkeys(self, kwstores=None, values=None, keys=None,
                  comments=None):
        """
        Add a set of new key to DrsFile.hdict from keywordstores. If kwstores
        is None and keys and comments are defined these are used instead.

        Each kwstores is in form:
                [key, value, comment]    where key and comment are strings

        :param kwstores: list of lists, list of "keyword list" lists
                              each "keyword list" must be in form:
                              [string, value, string]
        :param values: list of objects or None, if any python object
                       (other than None) will replace the values in kwstores
                       (i.e. kwstore[1]) with value[i], if None uses the
                       value = kwstore[1] for each kwstores

        :param keys: list of strings, if kwstores is None this is the list
                         of keys (must be same size as "comments")

        :param comments: list of string, if kwstores is None this is the list
                         of comments (must be same size as "keys")

        :return None:
        """
        func_name = __NAME__ + '.DrsFitsFile.add_header_keys()'
        # deal with no keywordstore
        if (kwstores is None) and (keys is None or comments is None):
            self.__error__(TextEntry('00-001-00009', args=[func_name]))
        # deal with kwstores set
        if kwstores is not None:
            # make sure kwstores is a list of list
            if not isinstance(kwstores, list):
                self.__error__(TextEntry('00-001-00010', args=[func_name]))
            # loop around entries
            for k_it, kwstore in enumerate(kwstores):
                self.add_hkey(kwstore=kwstore, value=values[k_it])
        # else we assume keys and comments
        else:
            if not isinstance(keys, list):
                self.__error__(TextEntry('00-001-00011', args=[func_name]))
            if not isinstance(comments, list):
                self.__error__(TextEntry('00-001-00012', args=[func_name]))
            if len(keys) != len(comments):
                self.__error__(TextEntry('00-001-00013', args=[func_name]))
            # loop around entries
            for k_it in range(len(keys)):
                self.add_hkey(key=keys[k_it], value=values[k_it],
                              comment=comments[k_it])

    def add_hkey_1d(self, kwstore=None, values=None, key=None,
                    comment=None, dim1name=None):
        """
        Add a new 1d list to key using the "kwstore"[0] or "key" as prefix
        in form:
            keyword = kwstore + row number
            keyword = key + row number
        and pushes it into DrsFile.hdict in form:
            hdict[keyword] = (value, comment)

        :param kwstore: list, keyword list (defined in spirouKeywords.py)
                        must be in form [string, value, string]
        :param values: numpy array or 1D list of keys or None
                       if numpy array or 1D list will create a set of keys
                       in form keyword = kwstore + row number
                      where row number is the position in values
                      with value = values[row number][column number]
        :param key: string, if kwstore is None uses key and comment in form
                   keyword = key + row number
        :param comment: string, the comment to go into the header
                        hdict[keyword] = (value, comment)
        :param dim1name: string, the name for dimension 1 (rows), used in
                         FITS rec HEADER comments in form:
                             comment = kwstore[2] dim1name={row number}
                             or
                             comment = "comment" dim1name={row number}
        :return None:
        """
        func_name = __NAME__ + '.DrsFitsFile.add_header_key_1d_list()'
        # deal with no keywordstore
        if (kwstore is None) and (key is None or comment is None):
            self.__error__(TextEntry('00-001-00014', args=[func_name]))
        # deal with no dim1name
        if dim1name is None:
            dim1name = 'dim1'
        # check for kwstore in params
        self.check_recipe()
        params = self.recipe.drs_params
        # check for kwstore in params
        if kwstore in params:
            kwstore = params[kwstore]
        # extract keyword, value and comment and put it into hdict
        if kwstore is not None:
            key, dvalue, comment = self.get_keywordstore(kwstore, func_name)
        else:
            key, dvalue, comment = key, None, comment
        # set the value to default value if value is None
        if values is None:
            values = [dvalue]
        # convert to a numpy array
        values = np.array(values)
        # get the length of dimension 1
        dim1 = len(values)
        # loop around the 1D array
        for it in range(dim1):
            # construct the key name
            keyname = test_for_formatting(key, it)
            # get the value
            value = values[it]
            # construct the comment name
            comm = '{0} {1}={2}'.format(comment, dim1name, it)
            # add to header dictionary
            self.hdict[keyname] = (value, comm)

    def add_hkeys_2d(self, key=None, keyword=None, values=None,
                     comment=None, dim1name=None, dim2name=None):
        """
        Add a new 2d list to key using the "kwstore"[0] or "key" as prefix
        in form:
            keyword = kwstore + row number
            keyword = key + row number

        where number = (row number * number of columns) + column number

        and pushes it into DrsFile.hdict in form:
            hdict[keyword] = (value, comment)

        :param kwstore: list, keyword list (defined in spirouKeywords.py)
                        must be in form [string, value, string]
        :param values: numpy array or 1D list of keys or None
                       if numpy array or 1D list will create a set of keys
                       in form keyword = kwstore + row number
                      where row number is the position in values
                      with value = values[row number][column number]
        :param key: string, if kwstore is None uses key and comment in form
                   keyword = key + row number
        :param comment: string, the comment to go into the header
                        hdict[keyword] = (value, comment)
        :param dim1name: string, the name for dimension 1 (rows), used in
                         FITS rec HEADER comments in form:
                             comment = kwstore[2] dim1name={row number}
                             or
                             comment = "comment" dim1name={row number}
        :param dim2name: string, the name for dimension 2 (rows), used in
                         FITS rec HEADER comments in form:
                             comment = kwstore[2] dim1name={row number}
                             or
                             comment = "comment" dim1name={row number}
        :return None:
        """
        func_name = __NAME__ + '.DrsFitsFile.add_header_key_1d_list()'
        # deal with no dim names
        if dim1name is None:
            dim1name = 'dim1'
        if dim2name is None:
            dim2name = 'dim2'
        # check for kwstore in params
        self.check_recipe()
        params = self.recipe.drs_params
        # if key is set use it (it should be from parameter dictionary
        if key is not None:
            if isinstance(key, str) and (key in params):
                kwstore = params[key]
            elif isinstance(key, list):
                kwstore = list(key)
            else:
                eargs = [key, func_name]
                self.__error__(TextEntry('00-001-00008', args=eargs))
                kwstore = None
        else:
            kwstore = [keyword, None, comment]
        # extract keyword, value and comment and put it into hdict
        if kwstore is not None:
            key, dvalue, comment = self.get_keywordstore(kwstore, func_name)
        else:
            key, dvalue, comment = key, None, comment
        # set the value to default value if value is None
        if values is None:
            values = [dvalue]
        # convert to a numpy array
        values = np.array(values)
        # get the length of dimension 1
        dim1, dim2 = values.shape
        # loop around the 1D array
        for it in range(dim1):
            for jt in range(dim2):
                # construct the key name
                keyname = test_for_formatting(key, it * dim2 + jt)
                # get the value
                value = values[it, jt]
                # construct the comment name
                cargs = [comment, dim1name, it, dim2name, jt]
                comm = '{0} {1}={2} {3}={4}'.format(*cargs)
                # add to header dictionary
                self.hdict[keyname] = (value, comm)

    def add_qckeys(self, qcparams):
        func_name = __NAME__ + '.add_qc_keys()'
        # get parameters
        qc_kws = ['KW_DRS_QC_NAME', 'KW_DRS_QC_VAL', 'KW_DRS_QC_LOGIC',
                  'KW_DRS_QC_PASS']
        # check for kwstore in params
        self.check_recipe()
        params = self.recipe.drs_params
        # check lengths are the same
        lengths = []
        for qcparam in qcparams:
            lengths.append(len(qcparam))
        strlengths = map(lambda x: str(x), lengths)
        # loop around lengths and test that they are the same
        for length in lengths:
            if lengths[0] != length:
                eargs = [', '.join(strlengths), func_name]
                WLOG(params, 'error', TextEntry('00-001-00019', args=eargs))
        # loop around values and add to hdict
        for it in range(lengths[0]):
            # loop around qc parameters
            for jt, keystr in enumerate(qc_kws):
                keyws = params[keystr]
                # extract keyword, value and comment and put it into hdict
                key, dvalue, comment = self.get_keywordstore(keyws, func_name)
                value = qcparams[jt][it]
                # add to the hdict dictionary in form (value, comment)
                self.hdict[key.format(it + 1)] = (value, comment)

    def get_keywordstore(self, kwstore=None, func_name=None):
        """
        Deal with extraction of key, value and comment from kwstore
        the kwstore should be a list in the following form:

        [name, value, comment]     with types [string, object, string]

        :param kwstore: list, keyword list must be in form:
                          [string, value, string]
        :param func_name: string or None, if not None defined where the
                          kwstore function is being called, if None
                          is set to here (spirouFITS.extract_key_word_store())

        :return key: string, the name/key of the HEADER (key/value/comment)
        :return value: object, any object to be put into the HEADER value
                       (under HEADER key="key")
        :return comment: string, the comment associated with the HEADER key
        """
        # deal with no func_name
        if func_name is None:
            func_name = __NAME__ + '.extract_key_word_store()'
        # extract keyword, value and comment and put it into hdict
        # noinspection PyBroadException
        try:
            key, dvalue, comment = kwstore
        except Exception as _:
            eargs = [kwstore, func_name]
            self.__error__(TextEntry('00-001-00016', args=eargs))
            key, dvalue, comment = None, None, None
        # return values
        return key, dvalue, comment

    def copy_hdict(self, drsfile):
        self.hdict = drsfile.hdict


# =============================================================================
# User functions
# =============================================================================
def add_required_keywords(drs_filelist, keys):
    # setup new list
    drs_filelist1 = []
    # loop around the DrsFitsFiles in "drs_filelist"
    for drs_file in drs_filelist:
        # create a copy of the DrsFitsfile
        drs_file1 = drs_file.newcopy()
        # storage for addition to drs_file1 name
        nameadd = []
        # loop around the key, value pairs
        for key in keys:
            if 'KW_' in key:
                drs_file1.set_required_key(key, keys[key])
                nameadd.append(keys[key])
        # add to name
        if len(nameadd) > 0:
            drs_file1.name += '({0})'.format(','.join(nameadd))
        # append to new list
        drs_filelist1.append(drs_file1)
    # return new file list
    return drs_filelist1


# =============================================================================
# Worker functions
# =============================================================================
def deal_with_bad_header(p, hdu, filename):
    """
    Deal with bad headers by iterating through good hdu's until we hit a
    problem

    :param p: ParamDict, the constants file
    :param hdu: astropy.io.fits HDU
    :param filename: string - the filename for logging

    :return data:
    :return header:
    """
    # define condition to pass
    cond = True
    # define iterator
    it = 0
    # define storage
    datastore = []
    headerstore = []
    # loop through HDU's until we cannot open them
    while cond:
        # noinspection PyBroadException
        try:
            datastore.append(hdu[it].data)
            headerstore.append(hdu[it].header)
        except:
            cond = False
        # iterate
        it += 1
    # print message
    if len(datastore) > 0:
        dargs = [it-1, filename]
        WLOG(p, 'warning', TextEntry('10-001-00001', args=dargs))
    # find the first one that contains equal shaped array
    valid = []
    for d_it in range(len(datastore)):
        if hasattr(datastore[d_it], 'shape'):
            valid.append(d_it)
    # if valid is empty we have a problem
    if len(valid) == 0:
        WLOG(p, 'error', TextEntry('01-001-00001', args=[filename]))
        data, header = None, None
    else:
        data = datastore[valid[0]]
        header = hdu[0].header
    # return data and header
    return data, header


def construct_header_error(herrors, params, drs_files, logic):

    # get error storage
    keys, rvalues, values = herrors

    # get text for this language/instrument
    text = TextDict(params['INSTRUMENT'], params['LANGUAGE'])

    if len(keys) == 0:
        return None

    emsgs = [text['09-001-00009']]
    used = []
    # loop around the current values
    for it, key in enumerate(keys):
        emsg = '\t{0} = {1}'.format(key, values[it])
        if (key, values[it]) not in used:
            emsgs.append(emsg)
            used.append((key, values[it]))

    # print the required values
    emsgs.append(text['09-001-00010'])
    used, used_it = [], []
    # log around the required values
    for it, drs_file in enumerate(drs_files):
        # do not list files we have already checked
        if drs_file in used:
            continue
        # add to used list
        used.append(drs_file)
        used_it.append(str(it + 1))
        # get emsg
        emsg = '\t{0}. '.format(it + 1)
        # get rkeys
        rkeys = drs_file.required_header_keys
        # loop around keys in drs_file
        keys = []
        for drskey in rkeys:
            # get key from drs_params
            if drskey in params:
                key = params[drskey][0]
            else:
                key = drskey
            # append key to file
            keys.append('{0}={1}'.format(key, rkeys[drskey]))
        emsg += ' and '.join(keys)
        # append to emsgs
        emsgs.append(emsg)
    # deal with exclusivity message
    emsg = ' or '.join(used_it)
    if logic == 'exclusive':
        emsgs.append(emsg + ' ' + text['09-001-00011'])
    elif logic == 'inclusive':
        emsgs.append(emsg + ' ' + text['09-001-00012'])
    else:
        emsgs.append(emsg)
    # return error strings
    return emsgs


def test_for_formatting(key, number):
    test_str = key.format(number)
    if test_str == key:
        return '{0}{1}'.format(key, number)
    else:
        return test_str


def is_forbidden_prefix(pconstant, key):
    cond = False
    for prefix in pconstant.FORBIDDEN_HEADER_PREFIXES():
        if key.startswith(prefix):
            cond = True
    return cond


# =============================================================================
# End of code
# =============================================================================
