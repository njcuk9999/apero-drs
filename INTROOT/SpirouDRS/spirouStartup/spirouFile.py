#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2018-11-04 11:16
@author: ncook
Version 0.0.1
"""
import numpy as np
from astropy.io import fits
from astropy import version as av
import os
import glob
import warnings
from collections import OrderedDict

from SpirouDRS import spirouCore
from SpirouDRS import spirouConfig


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'spirouFile.py'
# Get Logging function
WLOG = spirouCore.wlog
# Get constants
CONSTANTS = spirouConfig.Constants
# get the default log_opt
DPROG = CONSTANTS.DEFAULT_LOG_OPT()
# get forbidden key list from constants
FORBIDDEN_COPY_KEY = CONSTANTS.FORBIDDEN_COPY_KEYS()
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
        self.filename = None
        self.path = None
        self.basename = None
        self.inputdir = None
        self.directory = None
        self.data = None
        self.header = None
        self.comments = None
        self.index = None
        # allow instance to be associated with a filename
        self.set_filename(kwargs.get('filename', None))

    def set_filename(self, filename, check=True, quiet=False):
        """
        Set the filename, basename and directory name from an absolute path

        :param filename: string, absolute path to the file
        :param check: bool, if True will check for a valid file
        :param quiet: bool, if True prints check message else does not

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
            emsg = ('{0} Filename is not set. Must set a filename with file.'
                    'set_filename() first.')
            self.__error__(emsg.format(self.__repr__()))

    def set_recipe(self, recipe):
        """
        Set the associated recipe for the file (i.e. gives access to
        drs_parameters etc

        :param recipe: DrsRecipe instance, the recipe object to associate to
                       this file
        :return:
        """
        self.recipe = recipe

    def new(self, **kwargs):
        # copy this instances values (if not overwritten)
        name = kwargs.get('name', self.name)
        kwargs['ext'] = kwargs.get('ext', self.ext)
        # return new instance
        return DrsInputFile(name, **kwargs)

    def check_recipe(self):
        # ---------------------------------------------------------------------
        # check that recipe isn't None
        if self.recipe is None:
            emsg = 'No recipe set for {0} filename={1}. Run set_recipe() first.'
            eargs = [self.__repr__(), self.filename]
            self.__error__(emsg.format(*eargs))

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
        message0 = ['{0}: {1}'.format(kind.capitalize(), self.__repr__()),
                    '-'*10]
        # append initial error message to messages
        if isinstance(messages, list):
            messages = message0 + messages
        elif isinstance(messages, str):
            messages = message0 + [messages]
        # get log_opt
        if self.recipe is not None:
            params = self.recipe.drs_params
        else:
            params = None
        # print and log via wlogger
        WLOG(params, kind, messages)

    # -------------------------------------------------------------------------
    # file checking
    # -------------------------------------------------------------------------
    def check_file_exists(self, quiet=False):
        cond = os.path.exists(self.filename)
        if cond:
            msg = 'File "{0}" found in directory "{1}"'
            args = [self.basename, self.path]
        else:
            msg = 'File "{0}" does not exist in directory "{1}".'
            args = [self.basename, self.path]

        # deal with printout and return
        if (not cond) and (not quiet):
            self.__error__(msg.format(*args))
        elif not quiet:
            self.__message__(msg.format(*args))
        return cond, msg.format(*args)

    def check_file_extension(self, quiet=False):
        if self.ext is None:
            msg = 'File "{0}" extension not checked.'
            args = [self.basename]
            cond = True
        elif self.filename.endswith(self.ext):
            cond = True
            msg = 'File "{0}" has correct extension'
            args = [self.basename]
        else:
            msg = 'File "{0}" must have extension "{1}".'
            args = [self.basename, self.ext]
            cond = False
        # deal with printout and return
        if (not cond) and (not quiet):
            self.__error__(msg.format(*args))
        elif not quiet:
            self.__message__(msg.format(*args))
        return cond, msg.format(*args)

    def check_file_header(self, quiet=False):
        return True, ''


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
        # get fiber type (if set)
        self.fiber = kwargs.get('fiber', None)
        # get tag
        self.outtag = kwargs.get('KW_OUTPUT', 'UNKNOWN')
        # add header
        self.required_header_keys = dict()
        self.get_header_keys(kwargs)
        # set empty fits file storage
        self.data = None
        self.header = None
        self.comments = None
        self.index = None
        # set additional attributes
        self.shape = None
        self.hdict = OrderedDict()
        self.output_dict = OrderedDict()

    def get_header_keys(self, kwargs):
        # add values to the header
        for kwarg in kwargs:
            if 'KW_' in kwarg.upper():
                self.required_header_keys[kwarg] = kwargs[kwarg]

    def new(self, **kwargs):
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
        kwargs['check_ext'] = kwargs.get('check_ext', self.ext)
        kwargs['fiber'] = kwargs.get('fiber', self.fiber)
        kwargs['outtag'] = kwargs.get('KW_OUTPUT', self.outtag)
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

    # -------------------------------------------------------------------------
    # fits file checking
    # -------------------------------------------------------------------------
    def check_file_header(self, quiet=False, argname=None, debug=False):
        """
        Check file header has all required header keys
        :param quiet:
        :return:
        """
        # deal with no argument name
        if argname is None:
            argstring = ''
        else:
            argstring = 'Argument "{0}":'.format(argname)
        # -----------------------------------------------------------------
        # check file has been read
        self.read()
        # check recipe has been set
        self.check_recipe()
        params = self.recipe.drs_params

        rkeys = self.required_header_keys
        # -----------------------------------------------------------------
        # Step 1: Check that required keys are in header
        for drskey in rkeys:
            # check whether header key is in param dict (i.e. from a
            #    keywordstore) or whether we have to use the key as is
            if drskey in params:
                key = params[drskey][0]
            else:
                key = drskey
            # check if key is in header
            if key not in self.header:
                eargs = [argstring, key]
                emsgs = ['{0} Header key "{1}" not found'.format(*eargs)]
                return [False, True], None, [emsgs, None]
            elif debug:
                dmsg = '{0} Header key {1} found for {2}'
                dargs = [argstring, key, os.path.basename(self.filename)]
                WLOG(params, '', dmsg.format(*dargs))
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
                if debug:
                    dmsg = '{0} Header key {1} value is incorrect ({2})'
                    dargs = [argstring, key, rvalue]
                    WLOG(params, '', dmsg.format(*dargs))
                found = False
            elif debug:
                dmsg = '{0} Header key {1} valid for recipe ("{2}")'
                dargs = [argstring, key, value]
                WLOG(params, '', dmsg.format(*dargs))
            # store info
            errors[key] = (found, argstring, rvalue, value)
        # return:
        #       [valid cond1, valid cond2], self, [errors1, errors2]
        if found:
            return [True, True], self, [None, errors]
        else:
            return [True, False], self, [None, errors]


    def check_excluivity(self, drs_file, logic, quiet=False, debug=False):
        if drs_file is None:
            emsg = 'File type not set'
            cond = True
        elif logic == 'exclusive':
            cond = drs_file.name == self.name
            if cond and debug:
                emsg = 'File identified as "{0}" files match'
                emsg = emsg.format(self.name, drs_file.name)
            else:
                emsg = ('File identified as "{0}" however first file '
                        'identified as "{1}" - files must match')
                emsg = emsg.format(self.name, drs_file.name)
        elif logic == 'inclusive':
            if debug:
                emsg = 'Logic is inclusive'
            cond = True
        else:
            cond = False
            emsg = ('logic = "{0}" is not understood must be "exclusive" or'
                    ' "inclusive".')
            emsg = emsg.format(logic)

        if (not cond) and (not quiet):
            self.__error__(emsg)
        elif not quiet:
            self.__message__(emsg)
        return cond, emsg

    # -------------------------------------------------------------------------
    # fits file methods
    # -------------------------------------------------------------------------
    def read(self, ext=None, hdr_ext=0, check=True):
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
        # attempt to open hdu of fits file
        try:
            hdu = fits.open(self.filename)
        except Exception as e:
            emsg1 = ('File "{0}" cannot be opened by astropy.io.fits'
                     ''.format(self.basename))
            emsg2 = '\tError {0}: {1}'.format(type(e), e)
            emsg3 = '\tfunction = {0}'.format(func_name)
            self.__error__([emsg1, emsg2, emsg3])
            hdu = None
        # get the number of fits files in filename
        try:
            n_ext = len(hdu)
        except Exception as e:
            wmsg1 = 'Proglem with one of the extensions'
            wmsg2 = '\tError {0}, {1}'.format(type(e), e)
            self.__warning__([wmsg1, wmsg2])
            n_ext = None
        # deal with unknown number of extensions
        if n_ext is None:
            data, header = deal_with_bad_header(params, hdu)
        # else get the data and header based on how many extnesions there are
        else:
            # deal with extension number
            if n_ext == 1 and ext is None:
                ext = 0
            elif n_ext > 1 and ext is None:
                ext = 1
            # try to open the data
            try:
                data = hdu[ext].data
            except Exception as e:
                emsg1 = ('Could not open data for file "{0}" extension={1}'
                         ''.format(self.basename, ext))
                emsg2 = '\tError {0}: {1}'.format(type(e), e)
                emsg3 = '\tfunction = {0}'.format(func_name)
                self.__error__([emsg1, emsg2, emsg3])
                data = None
            # try to open the header
            try:
                header = hdu[hdr_ext].header
            except Exception as e:
                emsg1 = ('Could not open header for file "{0}" extension={1}'
                         ''.format(self.basename, hdr_ext))
                emsg2 = '\tError {0}: {1}'.format(type(e), e)
                emsg3 = '\tfunction = {0}'.format(func_name)
                self.__error__([emsg1, emsg2, emsg3])
                header = None
        # close the HDU
        if hdu is not None:
            hdu.close()

        # push into storage
        # TODO: Note this used to be "self.data = np.array(data)"
        # TODO:    But this is over 55% of the time of this function
        # TODO     May be needed if "data" linked to "hdu"
        self.data = data
        self.header = OrderedDict(zip(header.keys(), header.values()))
        self.comments = OrderedDict(zip(header.keys(), header.comments))

        # set the shape
        self.shape = self.data.shape

    def read_header(self, ext=0):
        func_name = __NAME__ + '.DrsFitsFile.read_header()'
        # check that filename is set
        self.check_filename()
        # try to open header
        try:
            self.header = fits.getheader(self.filename, ext=ext)
        except Exception as e:
            emsg1 = ('Could not open header for file "{0}" extention={1}'
                     ''.format(self.basename, ext))
            emsg2 = '\tError {0}: {1}'.format(type(e), e)
            emsg3 = '\tfunction = {0}'.format(func_name)
            self.__error__([emsg1, emsg2, emsg3])

    def read_data(self, ext=0):
        func_name = __NAME__ + '.DrsFitsFile.read_data()'
        # check that filename is set
        self.check_filename()
        # try to open header
        try:
            self.header = fits.getdata(self.filename, ext=ext)
        except Exception as e:
            emsg1 = ('Could not open data for file "{0}" extention={1}'
                     ''.format(self.basename, ext))
            emsg2 = '\tError {0}: {1}'.format(type(e), e)
            emsg3 = '\tfunction = {0}'.format(func_name)
            self.__error__([emsg1, emsg2, emsg3])

    def check_read(self):
        # check that data/header/comments is not None
        if self.data is None:
            emsg = (
                '{0} data is not set. Must read fits file first using'
                'read() first.')
            self.__error__(emsg.format(self.__repr__()))

    def read_multi(self):
        pass

    def write(self, dtype=None):
        func_name = __NAME__ + '.DrsFitsFile.write()'
        # get params
        params = self.recipe.drs_params
        # ---------------------------------------------------------------------
        # check that filename is set
        self.check_filename()
        # ---------------------------------------------------------------------
        # check if file exists and remove it if it does
        if os.path.exists(self.filename):
            try:
                os.remove(self.filename)
            except Exception as e:
                emsg1 = (' File {0} already exists and cannot be overwritten.'
                         ''.format(self.basename))
                emsg2 = '\tError {0}: {1}'.format(type(e), e)
                emsg3 = '\tfunction = {0}'.format(func_name)
                self.__error__([emsg1, emsg2, emsg3])
        # ---------------------------------------------------------------------
        # create the primary hdu
        try:
            hdu = fits.PrimaryHDU(self.data)
        except Exception as e:
            emsg1 = 'Cannot open image with astropy.io.fits'
            emsg2 = '\tError {0}: {1}'.format(type(e), e)
            emsg3 = '\tfunction = {0}'.format(func_name)
            self.__error__([emsg1, emsg2, emsg3])
            hdu = None
        # force type
        if dtype is not None:
            hdu.scale(type=dtype, **SCALEARGS)
        # ---------------------------------------------------------------------
        # add header keys to the hdu header
        if self.hdict is not None:
            for key in list(self.hdict.keys()):
                hdu.header[key] = self.hdict[key]
        # ---------------------------------------------------------------------
        # write to file
        with warnings.catch_warnings(record=True) as w:
            try:
                hdu.writeto(self.filename, overwrite=True)
            except Exception as e:
                emsg1 = ('Cannot write image to fits file {0}'
                         ''.format(self.basename))
                emsg2 = '    Error {0}: {1}'.format(type(e), e)
                emsg3 = '    function = {0}'.format(func_name)
                self.__error__([emsg1, emsg2, emsg3])
        # ---------------------------------------------------------------------
        # ignore truncated comment warning since spirou images have some poorly
        #   formatted header cards
        w1 = []
        for warning in w:
            wmsg = 'Card is too long, comment will be truncated.'
            if wmsg != str(warning.message):
                w1.append(warning)
        # add warnings to the warning logger and log if we have them
        spirouCore.spirouLog.warninglogger(params, w1)
        # ---------------------------------------------------------------------
        # write output dictionary
        self.output_dictionary()

    def write_multi(self):
        pass

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
        # get output dictionary
        output_hdr_keys = CONSTANTS.OUTPUT_FILE_HEADER_KEYS(p)
        # loop around the keys and find them in hdict (or add null character if
        #     not found)
        for key in output_hdr_keys:
            if key in self.hdict:
                self.output_dict[key] = str(self.hdict[key][0])
            else:
                self.output_dict[key] = '--'

    # -------------------------------------------------------------------------
    # fits file header methods
    # -------------------------------------------------------------------------
    def read_header_key(self, key, has_default=False, default=None,
                        required=True):
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
        # get drs parameters
        drs_params = self.recipe.drs_params
        # need to check drs_params for key (if key is not in header)
        if (key not in self.header) and (key in drs_params):
            # see if we have key store
            if len(drs_params[key]) == 3:
                drskey = drs_params[key][0]
            # if we dont assume we have a string
            else:
                drskey = drs_params[key]
        else:
            drskey = str(key)
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
                    if drskey == drskey:
                        emsg1 = 'Key "{0}" not found in header of file="{1}"'
                    else:
                        emsg1 = ('Key "{0}" ("{2}") not found in header of '
                                 'file="{1}"')
                    emsg1 = emsg1.format(drskey, self.filename, key)
                    emsg2 = '    function = {0}'.format(func_name)
                    self.__error__([emsg1, emsg2])
                    value = None
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
            emsg1 = '"keys" must be a valid python list'
            emsg2 = '    function = {0}'.format(func_name)
            self.__error__([emsg1, emsg2])
        # if defaults is None --> list of Nones else make sure defaults
        #    is a list
        if defaults is None:
            defaults = list(np.repeat([None], len(keys)))
        else:
            try:
                defaults = list(defaults)
                if len(defaults) != len(keys):
                    emsg1 = '"defaults" must be same length as "keys"'
                    emsg2 = '    function = {0}'.format(func_name)
                    self.__error__([emsg1, emsg2])
            except TypeError:
                emsg1 = '"defaults" must be a valid python list'
                emsg2 = '    function = {0}'.format(func_name)
                self.__error__([emsg1, emsg2])
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
        # create 2d list
        values = np.zeros(dim1, dtype=dtype)
        # loop around the 2D array
        for it in range(dim1):
            # construct the key name
            keyname = '{0}{1}'.format(key, it)
            # try to get the values
            try:
                # set the value
                values[it] = dtype(self.header[keyname])
            except KeyError:
                emsg1 = ('Cannot find key "{0}" with dim={1} in header for'
                         ' file={2}').format(keyname, dim1, self.basename)
                emsg2 = '    function = {0}'.format(func_name)
                self.__error__([emsg1, emsg2])
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
        # create 2d list
        values = np.zeros((dim1, dim2), dtype=dtype)
        # loop around the 2D array
        dim1, dim2 = values.shape
        for it in range(dim1):
            for jt in range(dim2):
                # construct the key name
                keyname = '{0}{1}'.format(key, it * dim2 + jt)
                # try to get the values
                try:
                    # set the value
                    values[it][jt] = dtype(self.header[keyname])
                except KeyError:
                    emsg1 = ('Cannot find key "{0}" with dim1={1} dim2={2} in '
                             '"hdict"').format(keyname, dim1, dim2)
                    emsg2 = '    function = {0}'.format(func_name)
                    self.__error__([emsg1, emsg2])
        # return values
        return values

    def copy_original_keys(self, drs_file, forbid_keys=True, root=None):
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
        # check that data/header is read
        drs_file.check_read()
        # get drs_file header/comments
        fileheader = drs_file.header
        filecomments = drs_file.comments
        # loop around keys in header
        for key in list(fileheader.keys()):
            if root is not None:
                if key.startswith(root):
                    # if key in "comments" add it as a tuple else
                    #    comments is blank
                    if key in filecomments:
                        self.hdict[key] = (fileheader[key], filecomments[key])
                    else:
                        self.hdict[key] = (fileheader[key], '')

            # skip if key is forbidden keys
            if forbid_keys and (key in FORBIDDEN_COPY_KEY):
                continue
            # skip if key added temporarily in code (denoted by @@@)
            elif '@@@' in key:
                continue
            # else add key to hdict
            else:
                # if key in "comments" add it as a tuple else comments is blank
                if key in filecomments:
                    self.hdict[key] = (fileheader[key], filecomments[key])
                else:
                    self.hdict[key] = (fileheader[key], '')
        return True

    def add_header_key(self, kwstore=None, value=None, key=None,
                       comment=None):
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
        # deal with no keywordstore
        if (kwstore is None) and (key is None or comment is None):
            emsg1 = ('Either "keywordstore" or ("key" and "comment") must '
                     'be defined')
            emsg2 = '    function = {0}'.format(func_name)
            self.__error__([emsg1, emsg2])

        # extract keyword, value and comment and put it into hdict
        if kwstore is not None:
            key, dvalue, comment = self.get_keywordstore(kwstore, func_name)
        else:
            key, dvalue, comment = key, None, comment

        # set the value to default value if value is None
        if value is None:
            value = dvalue
        # add to the hdict dictionary in form (value, comment)
        self.hdict[key] = (value, comment)

    def add_header_keys(self, kwstores=None, values=None, keys=None,
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
            emsg1 = ('Either "keywordstores" or ("keys" and "comments") must '
                     'be defined')
            emsg2 = '\tfunction = {0}'.format(func_name)
            self.__error__([emsg1, emsg2])
        # deal with kwstores set
        if kwstores is not None:
            # make sure kwstores is a list of list
            if not isinstance(kwstores, list):
                emsg1 = 'Error "kwstores" must be a list'
                emsg2 = '\tfunction = {0}'.format(func_name)
                self.__error__([emsg1, emsg2])
            # loop around entries
            for k_it, kwstore in enumerate(kwstores):
                self.add_header_key(kwstore=kwstore, value=values[k_it])
        # else we assume keys and comments
        else:
            if not isinstance(keys, list):
                emsg1 = ('Error "keys" must be a list (or "kwstores" must '
                         'be defined)')
                emsg2 = '\tfunction = {0}'.format(func_name)
                self.__error__([emsg1, emsg2])
            if not isinstance(comments, list):
                emsg1 = ('Error "comments" must be a list (or "kwstores" must '
                         'be defined)')
                emsg2 = '\tfunction = {0}'.format(func_name)
                self.__error__([emsg1, emsg2])
            if len(keys) != len(comments):
                emsg1 = 'Error "keys" must be same length as "comments"'
                emsg2 = '\tfunction = {0}'.format(func_name)
                self.__error__([emsg1, emsg2])
            # loop around entries
            for k_it in range(len(keys)):
                self.add_header_key(key=keys[k_it], value=values[k_it],
                                    comment=comments[k_it])

    def add_header_key_1d_list(self, kwstore=None, values=None, key=None,
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
            emsg1 = ('Either "keywordstore" or ("key" and "comment") must '
                     'be defined')
            emsg2 = '    function = {0}'.format(func_name)
            self.__error__([emsg1, emsg2])
        # deal with no dim1name
        if dim1name is None:
            dim1name = 'dim1'
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
            keyname = '{0}{1}'.format(key, it)
            # get the value
            value = values[it]
            # construct the comment name
            comm = '{0} {1}={2}'.format(comment, dim1name, it)
            # add to header dictionary
            self.hdict[keyname] = (value, comm)

    def add_header_keys_2d_list(self, kwstore=None, values=None, key=None,
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
        # deal with no keywordstore
        if (kwstore is None) and (key is None or comment is None):
            emsg1 = ('Either "keywordstore" or ("key" and "comment") must '
                     'be defined')
            emsg2 = '    function = {0}'.format(func_name)
            self.__error__([emsg1, emsg2])
        # deal with no dim names
        if dim1name is None:
            dim1name = 'dim1'
        if dim2name is None:
            dim2name = 'dim2'
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
                keyname = '{0}{1}'.format(key, it * dim2 + jt)
                # get the value
                value = values[it, jt]
                # construct the comment name
                cargs = [comment, dim1name, it, dim2name, jt]
                comm = '{0} {1}={2} {3}={4}'.format(*cargs)
                # add to header dictionary
                self.hdict[keyname] = (value, comm)

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
            emsg1 = 'There was a problem with the "keywordstore"'
            emsg2 = '   It must be a list/tuple with of the following format:'
            emsg3 = '       [string, object, string]'
            emsg4 = '     where the first is the HEADER name of the keyword'
            emsg5 = '     where the second is the default value for the keyword'
            emsg6 = '     where the third is the HEADER comment'
            emsg7 = '   keywordstore currently is "{0}"'.format(kwstore)
            emsg8 = '   function = {0}'.format(func_name)
            emsgs = [emsg1, emsg2, emsg3, emsg4, emsg5, emsg6, emsg7, emsg8]
            self.__error__(emsgs)
            key, dvalue, comment = None, None, None
        # return values
        return key, dvalue, comment


# =============================================================================
# User functions
# =============================================================================
def add_required_keywords(drs_filelist, keys):
    # setup new list
    drs_filelist1 = []
    # loop around the DrsFitsFiles in "drs_filelist"
    for drs_file in drs_filelist:
        # create a copy of the DrsFitsfile
        drs_file1 = drs_file.new()
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
def deal_with_bad_header(p, hdu):
    """
    Deal with bad headers by iterating through good hdu's until we hit a
    problem

    :param hdu: astropy.io.fits HDU

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
        WLOG(p, 'warning', '\tPartially recovered fits file')
        WLOG(p, 'warning', '\tProblem with ext={0}'.format(it - 1))
    # find the first one that contains equal shaped array
    valid = []
    for d_it in range(len(datastore)):
        if hasattr(datastore[d_it], 'shape'):
            valid.append(d_it)
    # if valid is empty we have a problem
    if len(valid) == 0:
        emsg = 'Recovery failed: Fatal I/O Error cannot load file.'
        WLOG(p, 'error', emsg)
        data, header = None, None
    else:
        data = datastore[valid[0]]
        header = hdu[0].header
    # return data and header
    return data, header


def construct_header_error(herrors, params, drs_files, logic):

    # get error storage
    keys, rvalues, values = herrors

    if len(keys) == 0:
        return None

    emsgs = ['Current file has:']
    used = []
    # loop around the current values
    for it, key in enumerate(keys):
        emsg = '\t{0} = {1}'.format(key, values[it])
        if (key, values[it]) not in used:
            emsgs.append(emsg)
            used.append((key, values[it]))

    # print the required values
    emsgs.append('Recipe required values are:')
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
        emsgs.append(emsg + ' exclusively')
    elif logic == 'inclusive':
        emsgs.append(emsg + ' inclusively')
    else:
        emsgs.append(emsg)
    # return error strings
    return emsgs


# =============================================================================
# End of code
# =============================================================================
