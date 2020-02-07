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
import copy
import warnings

from apero.core.core import drs_log
from apero.core import constants
from apero.core import math as mp
from apero.locale import drs_text
from apero.io import drs_fits

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'drs_file.py'
__INSTRUMENT__ = 'None'
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# Get function string
display_func = drs_log.display_func
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
        # set function name
        _ = display_func(None, '__init__', __NAME__, 'DrsInputFile')
        # define a name
        self.name = name
        # define the extension
        self.filetype = kwargs.get('filetype', '')
        self.suffix = kwargs.get('suffix', '')
        self.remove_insuffix = kwargs.get('remove_insuffix', False)
        self.prefix = kwargs.get('prefix', '')
        self.filename = None
        self.intype = None
        # get fiber type (if set)
        self.fibers = kwargs.get('fibers', None)
        self.fiber = kwargs.get('fiber', None)
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
        self.fileset = kwargs.get('fileset', [])
        self.filesetnames = kwargs.get('filesetnames', [])
        self.indextable = kwargs.get('index', None)
        self.outfunc = kwargs.get('outfunc', None)
        # allow instance to be associated with a filename
        self.set_filename(kwargs.get('filename', None))

    def set_filename(self, filename):
        """
        Set the filename, basename and directory name from an absolute path

        :param filename: string, absolute path to the file

        :return None:
        """
        # set function name
        _ = display_func(None, 'set_filename', __NAME__, 'DrsInputFile')
        # skip if filename is None
        if filename is None:
            return True
        # set filename, basename and directory name
        self.filename = str(filename)
        self.basename = os.path.basename(filename)
        self.path = os.path.dirname(filename)

    def check_filename(self):
        # set function name
        _ = display_func(None, 'check_filename', __NAME__, 'DrsInputFile')
        # check that filename isn't None
        if self.filename is None:
            func = self.__repr__()
            eargs = [func, func + '.set_filename()']
            self.__error__(TextEntry('00-001-00002', args=eargs))

    def file_exists(self):
        # set function name
        _ = display_func(None, 'set_filename', __NAME__, 'DrsInputFile')
        # assume file does not exist
        found = False
        # if filename is set check filename exists
        if self.filename is not None:
            # if filename is string check filename exists
            if isinstance(self.filename, str):
                # update found
                found = os.path.exists(self.filename)
        # return whether file was found
        return found

    def set_recipe(self, recipe):
        """
        Set the associated recipe for the file (i.e. gives access to
        drs_parameters etc

        :param recipe: DrsRecipe instance, the recipe object to associate to
                       this file
        :return:
        """
        # set function name
        _ = display_func(None, 'set_recipe', __NAME__, 'DrsInputFile')
        # set the recipe
        self.recipe = recipe

    def newcopy(self, **kwargs):
        # set function name
        _ = display_func(None, 'newcopy', __NAME__, 'DrsInputFile')
        # copy this instances values (if not overwritten)
        name = kwargs.get('name', self.name)
        kwargs['filetype'] = kwargs.get('filetype', self.filetype)
        kwargs['suffix'] = kwargs.get('suffix', self.suffix)
        kwargs['remove_insuffix'] = kwargs.get('remove_insuffix',
                                               self.remove_insuffix)
        kwargs['prefix'] = kwargs.get('prefix', self.prefix)
        kwargs['filename'] = kwargs.get('filename', self.filename)
        kwargs['intype'] = kwargs.get('infile', self.intype)
        kwargs['fiber'] = kwargs.get('fiber', self.fiber)
        kwargs['fibers'] = kwargs.get('fibers', self.fibers)
        kwargs['recipe'] = kwargs.get('recipe', self.recipe)
        kwargs['filename'] = kwargs.get('filename', self.filename)
        kwargs['path'] = kwargs.get('path', self.path)
        kwargs['basename'] = kwargs.get('basename', self.basename)
        kwargs['inputdir'] = kwargs.get('inputdir', self.inputdir)
        kwargs['directory'] = kwargs.get('directory', self.directory)
        kwargs['data'] = kwargs.get('data', self.data)
        kwargs['header'] = kwargs.get('header', self.header)
        kwargs['fileset'] = kwargs.get('fileset', self.fileset)
        kwargs['filesetnames'] = kwargs.get('filesetnames', self.filesetnames)
        kwargs['indextable'] = kwargs.get('indextable', self.indextable)
        kwargs['outfunc'] = kwargs.get('outfunc', self.outfunc)
        # return new instance
        return DrsInputFile(name, **kwargs)

    def check_recipe(self):
        # set function name
        _ = display_func(None, 'check_recipe', __NAME__, 'DrsInputFile')
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
        # set function name
        _ = display_func(None, '__str__', __NAME__, 'DrsInputFile')
        # return the string representation of DrsInputFile
        return 'DrsInputFile[{0}]'.format(self.name)

    def __repr__(self):
        """
        Defines the print(DrsInputFile) return for DrsInputFile
        :return str: the string representation of DrsInputFile
                     i.e. DrsInputFile[name]
        """
        # set function name
        _ = display_func(None, '__repr__', __NAME__, 'DrsInputFile')
        # return the string representation of DrsInputFile
        return 'DrsInputFile[{0}]'.format(self.name)

    def __error__(self, messages):
        # set function name
        _ = display_func(None, '__error__', __NAME__, 'DrsInputFile')
        # run the log method: error mode
        self.__log__(messages, 'error')

    def __warning__(self, messages):
        # set function name
        _ = display_func(None, '__warning__', __NAME__, 'DrsInputFile')
        # run the log method: warning mode
        self.__log__(messages, 'warning')

    def __message__(self, messages):
        # set function name
        _ = display_func(None, '__message__', __NAME__, 'DrsInputFile')
        # get log_opt
        if self.recipe is not None:
            params = self.recipe.drs_params
        else:
            params = None
        # print and log via wlogger
        WLOG(params, '', messages)

    def __log__(self, messages, kind):
        # set function name
        _ = display_func(None, '__log__', __NAME__, 'DrsInputFile')
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
        # set function name
        _ = display_func(None, 'addset', __NAME__, 'DrsInputFile')
        # append drs file to file set
        self.fileset.append(drsfile)
        # apeend drs file name to file set name list
        self.filesetnames.append(drsfile.name)

    def copyother(self, drsfile, **kwargs):
        # set function name
        _ = display_func(None, 'copyother', __NAME__, 'DrsInputFile')
        # check recipe has been set
        if 'recipe' not in kwargs:
            self.check_recipe()
        else:
            self.recipe = kwargs['recipe']
        # get parameters
        params = self.recipe.drs_params
        # set function name
        func_name = display_func(params, 'copyother', __NAME__, 'DrsInputFile')
        # check file has been read (if 'read' not equal to False)
        if kwargs.get('read', True):
            if drsfile.data is None:
                dargs = [drsfile.filename, func_name]
                WLOG(params, 'debug', TextEntry('90-008-00010', args=dargs))
                drsfile.read_file()
        # set empty file attributes
        nkwargs = dict()
        nkwargs['name'] = kwargs.get('name', self.name)
        nkwargs['recipe'] = kwargs.get('recipe', self.recipe)
        nkwargs['filename'] = kwargs.get('filename', drsfile.filename)
        nkwargs['intype'] = kwargs.get('infile', drsfile.intype)
        nkwargs['path'] = kwargs.get('path', drsfile.path)
        nkwargs['basename'] = kwargs.get('basename', drsfile.basename)
        nkwargs['inputdir'] = kwargs.get('inputdir', drsfile.inputdir)
        nkwargs['directory'] = kwargs.get('directory', drsfile.directory)
        nkwargs['data'] = kwargs.get('data', drsfile.data)
        nkwargs['header'] = kwargs.get('header', drsfile.header)
        nkwargs['fileset'] = kwargs.get('fileset', self.fileset)
        nkwargs['filesetnames'] = kwargs.get('filesetnames', self.filesetnames)
        # return new instance of DrsFitsFile
        return DrsInputFile(**nkwargs)

    def completecopy(self, drsfile):
        # set function name
        _ = display_func(None, 'completecopy', __NAME__, 'DrsInputFile')
        # set empty file attributes
        nkwargs = dict()
        nkwargs['name'] = copy.deepcopy(drsfile.name)
        nkwargs['filetype'] = copy.deepcopy(drsfile.filetype)
        nkwargs['suffix'] = copy.deepcopy(drsfile.suffix)
        nkwargs['remove_insuffix'] = bool(drsfile.remove_insuffix)
        nkwargs['prefix'] = copy.deepcopy(drsfile.prefix)
        nkwargs['fiber'] = copy.deepcopy(drsfile.fiber)
        nkwargs['fibers'] = copy.deepcopy(drsfile.fibers)
        nkwargs['recipe'] = copy.deepcopy(drsfile.recipe)
        nkwargs['filename'] = copy.deepcopy(drsfile.filename)
        nkwargs['intype'] = drsfile.intype
        nkwargs['path'] = copy.deepcopy(drsfile.path)
        nkwargs['basename'] = copy.deepcopy(drsfile.basename)
        nkwargs['inputdir'] = copy.deepcopy(drsfile.inputdir)
        nkwargs['directory'] = copy.deepcopy(drsfile.directory)
        nkwargs['data'] = copy.deepcopy(drsfile.data)
        nkwargs['header'] = copy.deepcopy(drsfile.header)
        # ------------------------------------------------------------------
        if drsfile.fileset is None:
            nkwargs['fileset'] = None
        elif isinstance(drsfile.fileset, list):
            # set up new file set storage
            newfileset = []
            # loop around file sets
            for fileseti in drsfile.fileset:
                newfileset.append(fileseti.completecopy(fileseti))
            # append to nkwargs
            nkwargs['fileset'] = newfileset

        else:
            nkwargs['fileset'] = drsfile.fileset
        nkwargs['filesetnames'] = drsfile.filesetnames
        # ------------------------------------------------------------------
        nkwargs['indextable'] = copy.deepcopy(drsfile.indextable)
        nkwargs['outfunc'] = drsfile.outfunc
        # return new instance
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
        # set function name
        _ = display_func(None, 'check_another_file', __NAME__, 'DrsInputFile')
        # 1. check extension
        cond1, msg1 = self.has_correct_extension(input_file.ext)
        if not cond1:
            return False, msg1
        # 2. check file header keys exist
        cond2, msg2 = self.hkeys_exist(None)
        if not cond2:
            return False, msg2
        # 3. check file header keys are correct
        cond3, msg3 = self.has_correct_hkeys(None)
        if not cond2:
            return False, msg3
        # if 1, 2 and 3 pass return True
        return True, None

    def check_file(self):
        """
        Checks that this file is correct

        :returns: True or False and the reason why (if False)
        """
        # set function name
        _ = display_func(None, 'check_file', __NAME__, 'DrsInputFile')
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

    def has_correct_extension(self, filename=None, filetype=None, argname=None):
        # set function name
        _ = display_func(None, 'has_correct_extension', __NAME__,
                         'DrsInputFile')
        # always return True and None (abstract placeholder)
        return True, None

    def hkeys_exist(self, header=None, filename=None, argname=None):
        # set function name
        _ = display_func(None, 'hkeys_exist', __NAME__,
                         'DrsInputFile')
        # always return True and None (abstract placeholder)
        return True, None

    def has_correct_hkeys(self, header=None, argname=None, log=True):
        # set function name
        _ = display_func(None, 'has_correct_hkeys', __NAME__,  'DrsInputFile')
        # always return True and None (abstract placeholder)
        return True, None

    # -------------------------------------------------------------------------
    # file checking (old)
    # -------------------------------------------------------------------------
    def check_file_exists(self, quiet=False):
        # set function name
        _ = display_func(None, 'check_file_exists', __NAME__, 'DrsInputFile')
        # check that filename exists
        cond = os.path.exists(self.filename)
        # if it does add to log that file is found
        if cond:
            eargs = [self.basename, self.path]
            emsg = TextEntry('09-000-00001', args=eargs)
        # if it does not add to log that file is not found
        else:
            eargs = [self.basename, self.path]
            emsg = TextEntry('09-000-00002', args=eargs)
        # deal with printout and return
        # if we failed and aren't in quiet mode --> display error
        if (not cond) and (not quiet):
            self.__error__(emsg)
        # if we didn't fail and aren't in quiet mode --> display message
        elif not quiet:
            self.__message__(emsg)
        # return the condition and (error) message
        return cond, emsg

    def check_file_extension(self, quiet=False):
        # set function name
        _ = display_func(None, 'check_file_exists', __NAME__, 'DrsInputFile')
        # if filetype is None add message and set pass condition
        #   to True
        if self.filetype is None:
            msg = TextEntry('09-000-00003', args=[self.basename])
            cond = True
        # if filetype is set and is correct add message and set pass condition
        #   to True
        elif self.filename.endswith(self.filetype):
            msg = TextEntry('09-000-00004', args=[self.basename, self.filetype])
            cond = True
        # if it has failed set error message and set pass condition to False
        else:
            msg = TextEntry('09-000-00005', args=[self.basename, self.filetype])
            cond = False
        # deal with printout and return
        if (not cond) and (not quiet):
            self.__error__(msg)
        elif not quiet:
            self.__message__(msg)
        # return condition and message
        return cond, msg

    def check_file_header(self, quiet=False):
        # set function name
        _ = display_func(None, 'check_file_header', __NAME__, 'DrsInputFile')
        # there is no header for non-fits input files --> return True and
        #   a blank message
        return True, TextEntry('')

    # -------------------------------------------------------------------------
    # read/write methods
    # -------------------------------------------------------------------------
    def read_file(self, ext=None, check=False, params=None):
        # set function name
        _ = display_func(None, 'read_file', __NAME__, 'DrsInputFile')
        # do nothing else (no current read option for generic input files)

    def write_file(self, params=None):
        # set function name
        _ = display_func(None, 'write_file', __NAME__, 'DrsInputFile')
        # do nothing else (no current write option for generic input files)

    # -------------------------------------------------------------------------
    # user functions
    # -------------------------------------------------------------------------
    def construct_filename(self, params, infile=None, check=True, **kwargs):
        """
        Constructs the filename from the parameters defined at instance
        definition and using the infile (if required). If check is True, checks
        the infile type against "intype". Uses "outfunc" in instance definition
        to set the suffices/prefixes/fiber etc

        :param params: Param Dict
        :param infile: Drsfile, the input DrsFile
        :param check: bool, whether to check infile.name against self.intype
        :param kwargs: keyword arguments passed to self.outfunc

        :return: Sets self.filename and self.basename to the correct values
        """
        # set function name
        func_name = display_func(params, 'construct_filename', __NAME__,
                                 'DrsInputFile')
        # set outfile from self
        kwargs['outfile'] = self
        kwargs['func'] = func_name
        kwargs['infile'] = infile
        # if we have a function use it
        if self.outfunc is not None:
            abspath = self.outfunc(params, **kwargs)
            self.filename = abspath
            self.basename = os.path.basename(abspath)
        # else raise an error
        else:
            eargs = [self.__repr__(), func_name]
            WLOG(params, 'error', TextEntry('00-008-00004', args=eargs))
        # check that we are allowed to use infile (if set)
        if infile is not None and check:
            if self.intype is not None:
                # get required names
                reqfiles = self.generate_reqfiles()
                reqstr = ' or '.join(reqfiles)
                # see if infile is in reqfiles
                if infile.name not in reqfiles:
                    eargs = [infile.name, reqstr, self.filename, func_name]
                    WLOG(params, 'error', TextEntry('00-008-00017', args=eargs))

    def generate_reqfiles(self):
        """
        Takes "intype" and works out all the combinations of file names that
        are valid for this "intype" (i.e. if we have a fileset in one of the
        "intypes" we should add all files from this set)

        :return: list of DrsInputFile names (drsfile.name) to know which names
                 are valid
        :rtype list:
        """
        # set function name
        _ = display_func(None, 'generate_reqfiles', __NAME__, 'DrsInputFile')
        # deal with intype being unset
        if self.intype is None:
            return []
        # set out list storage
        required_names = []
        # deal with having a list of files
        if isinstance(self.intype, list):
            # loop around intypes
            for intype in self.intype:
                # deal with intype having fileset (set of files associated
                #   with this file)
                if len(intype.filesetnames) != 0:
                    required_names += list(intype.filesetnames)
                    required_names.append(intype.name)
                else:
                    required_names.append(intype.name)
        else:
            intype = self.intype
            # deal with intype having fileset (set of files associated
            #   with this file)
            if len(intype.filesetnames) != 0:
                required_names += list(intype.filesetnames)
                required_names.append(intype.name)
            else:
                required_names.append(intype.name)
        # clean up required name list by only keeping unique names
        required_names = list(np.unique(required_names))
        # return required names
        return required_names


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
        # set function name
        _ = display_func(None, '__init__', __NAME__, 'DrsFitsFile')
        # define a name
        self.name = name
        # get super init
        DrsInputFile.__init__(self, name, **kwargs)
        # if ext in kwargs then we have a file extension to check
        self.filetype = kwargs.get('filetype', '.fits')
        # set the input extension type
        self.inext = kwargs.get('inext', '.fits')
        # get the input type (another DrsFitsFile that was or will be used
        #   to create this one i.e. for pp intype is a raw drs fits file,
        #   for out intype is most likely a pp drs fits file)
        self.intype = kwargs.get('intype', None)
        # get fiber types allowed for this drs fits file
        self.fibers = kwargs.get('fibers', None)
        # get the specific fiber linked to this drs fits file
        self.fiber = kwargs.get('fiber', None)
        # get the function used for writing output file
        self.outfunc = kwargs.get('outfunc', None)
        # get the out tag # TODO: Is this used still?
        self.outtag = kwargs.get('KW_OUTPUT', 'UNKNOWN')
        # get the database name (only set if intended to go into a database)
        self.dbname = kwargs.get('dbname', None)
        # get the raw database key name (only set if intended to go into a
        #    database) - this is the one set in constants
        self.raw_dbkey = str(kwargs.get('dbkey', None))
        # get the current database key -- this can change i.e. adding of a
        #   fiber to the end -- for the default set key see raw_dbkey
        self.dbkey = str(kwargs.get('dbkey', None))
        # add required header keys storage
        self.required_header_keys = kwargs.get('rkeys', dict())
        # if we don't have any required keys pushed in we get these using
        #   the get_header_keys method (kwargs is passed to allow setting
        #   individual keys when drs fits instance is constructed)
        if len(self.required_header_keys) == 0:
            self.get_header_keys(kwargs)
        # get the fits data array (or set it to None)
        self.data = kwargs.get('data', None)
        # get the fits header (or set it to None)
        self.header = kwargs.get('header', None)
        # get the index table related to this file # TODO: Is this used still?
        self.indextable = kwargs.get('index', None)
        # get the number of files associated with this drs fits file
        self.numfiles = kwargs.get('numfiles', 0)
        # get the shape of the fits data array (self.data)
        self.shape = kwargs.get('shape', None)
        # get the hdict (header dictionary storage) that will be passed to
        #   self.header - if not passed this is set as an empty header
        #   kept separate from self.header until all keys are added
        #   (to allow clean up + checking to occur only once)
        self.hdict = kwargs.get('hdict', drs_fits.Header())
        # get the storage dictionary for output parameters
        self.output_dict = kwargs.get('output_dict', OrderedDict())
        # get the data type for this drs fits file (either image or table)
        self.datatype = kwargs.get('datatype', 'image')
        # get the dtype internally for fits image files (i.e. float or int)
        self.dtype = kwargs.get('dtype', None)
        # get the data array (for multi-extension fits)
        self.data_array = None
        # get the header array (fro multi-extnesion fits)
        self.header_array = None
        # TODO: IS this used?? What is it used for?
        self.s1d = kwargs.get('s1d', [])
        # update database key based on whether we have the fiber
        if self.fiber is not None:
            self.get_dbkey()

    def get_header_keys(self, kwargs):
        # set function name
        _ = display_func(None, 'get_header_keys', __NAME__, 'DrsFitsFile')
        # add values to the header
        for kwarg in kwargs:
            if 'KW_' in kwarg.upper():
                self.required_header_keys[kwarg] = kwargs[kwarg]

    # TODO: Merge/combine with completecopy and copyother
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
        # set function name
        _ = display_func(None, 'newcopy', __NAME__, 'DrsFitsFile')
        # copy this instances values (if not overwritten)
        name = kwargs.get('name', self.name)
        kwargs['filetype'] = kwargs.get('filetype', self.filetype)
        kwargs['suffix'] = kwargs.get('suffix', self.suffix)
        kwargs['remove_insuffix'] = kwargs.get('remove_insuffix',
                                               self.remove_insuffix)
        kwargs['prefix'] = kwargs.get('prefix', self.prefix)
        kwargs['recipe'] = kwargs.get('recipe', self.recipe)
        kwargs['filename'] = kwargs.get('filename', self.filename)
        kwargs['path'] = kwargs.get('path', self.path)
        kwargs['basename'] = kwargs.get('basename', self.basename)
        kwargs['inputdir'] = kwargs.get('inputdir', self.inputdir)
        kwargs['intype'] = kwargs.get('intype', self.intype)
        kwargs['directory'] = kwargs.get('directory', self.directory)
        kwargs['data'] = kwargs.get('data', self.data)
        kwargs['header'] = kwargs.get('header', self.header)
        kwargs['fileset'] = kwargs.get('fileset', self.fileset)
        kwargs['filesetnames'] = kwargs.get('filesetnames', self.filesetnames)
        kwargs['check_ext'] = kwargs.get('check_ext', self.filetype)
        kwargs['fiber'] = kwargs.get('fiber', self.fiber)
        kwargs['fibers'] = kwargs.get('fibers', self.fibers)
        kwargs['outtag'] = kwargs.get('KW_OUTPUT', self.outtag)
        kwargs['outfunc'] = kwargs.get('outfunc', self.outfunc)
        kwargs['dbname'] = kwargs.get('dbname', self.dbname)
        kwargs['dbkey'] = kwargs.get('dbkey', self.dbkey)
        kwargs['datatype'] = kwargs.get('datatype', self.datatype)
        kwargs['dtype'] = kwargs.get('dtype', self.dtype)
        kwargs['s1d'] = kwargs.get('s1d', self.s1d)
        kwargs['shape'] = kwargs.get('shape', self.shape)
        kwargs['numfiles'] = kwargs.get('numfiles', self.numfiles)
        for key in self.required_header_keys:
            kwargs[key] = self.required_header_keys[key]

        newfile = DrsFitsFile(name, **kwargs)
        newfile.get_header_keys(kwargs)
        # return new instance
        return newfile

    def string_output(self):
        """
        String output for DrsFitsFile. If fiber is not None this also
        contains the fiber type

        i.e. DrsFitsFile[{name}_{fiber}] or DrsFitsFile[{name}]
        :return string: str, the string to print
        """
        # set function name
        _ = display_func(None, 'string_output', __NAME__, 'DrsFitsFile')
        # if we don't have the fiber print the drs fits file string
        if self.fiber is None:
            return 'DrsFitsFile[{0}]'.format(self.name)
        # if we have the fiber add it and print the drs fits file string
        else:
            return 'DrsFitsFile[{0}_{1}]'.format(self.name, self.fiber)

    def set_required_key(self, key, value):
        # set function name
        _ = display_func(None, 'set_required_key', __NAME__, 'DrsFitsFile')
        # if we have a keyword (prefix 'KW_')
        if 'KW_' in key:
            # set required header keys
            self.required_header_keys[key] = value

    def __str__(self):
        """
        Defines the str(DrsFitsFile) return for DrsFitsFile
        :return str: the string representation of DrsFitsFile
                     i.e. DrsFitsFile[name] or DrsFitsFile[name_fiber]
        """
        # set function name
        _ = display_func(None, '__str__', __NAME__, 'DrsFitsFile')
        # return the string output
        return self.string_output()

    def __repr__(self):
        """
        Defines the print(DrsFitsFile) return for DrsFitsFile
        :return str: the string representation of DrsFitsFile
                     i.e. DrsFitsFile[name] or DrsFitsFile[name_fiber]
        """
        # set function name
        _ = display_func(None, '__repr__', __NAME__, 'DrsFitsFile')
        # return the string output
        return self.string_output()

    # TODO: Merge/combine with newcopy and copyother
    def completecopy(self, drsfile):
        """
        Copies all attributes from one drsfile to another
        :param drsfile:
        :return:
        """
        # set function name
        _ = display_func(None, 'completecopy', __NAME__, 'DrsFitsFile')
        # set empty file attributes
        nkwargs = dict()
        nkwargs['name'] = copy.deepcopy(drsfile.name)
        nkwargs['filetype'] = copy.deepcopy(drsfile.filetype)
        nkwargs['suffix'] = copy.deepcopy(drsfile.suffix)
        nkwargs['remove_insuffix'] = bool(drsfile.remove_insuffix)
        nkwargs['prefix'] = copy.deepcopy(drsfile.prefix)
        nkwargs['recipe'] = drsfile.recipe
        nkwargs['fiber'] = copy.deepcopy(drsfile.fiber)
        nkwargs['fibers'] = copy.deepcopy(drsfile.fibers)
        nkwargs['rkeys'] = copy.deepcopy(drsfile.required_header_keys)
        nkwargs['filename'] = copy.deepcopy(drsfile.filename)
        nkwargs['path'] = copy.deepcopy(drsfile.path)
        nkwargs['basename'] = copy.deepcopy(drsfile.basename)
        nkwargs['inputdir'] = copy.deepcopy(drsfile.inputdir)
        nkwargs['intype'] = drsfile.intype
        nkwargs['directory'] = copy.deepcopy(drsfile.directory)
        nkwargs['data'] = copy.deepcopy(drsfile.data)
        nkwargs['header'] = copy.deepcopy(drsfile.header)
        nkwargs['shape'] = copy.deepcopy(drsfile.shape)
        nkwargs['hdict'] = copy.deepcopy(drsfile.hdict)
        nkwargs['output_dict'] = copy.deepcopy(drsfile.output_dict)
        # ------------------------------------------------------------------
        if drsfile.fileset is None:
            nkwargs['fileset'] = None
        elif isinstance(drsfile.fileset, list):
            # set up new file set storage
            newfileset = []
            # loop around file sets
            for fileseti in drsfile.fileset:
                newfileset.append(fileseti.completecopy(fileseti))
            # append to nkwargs
            nkwargs['fileset'] = newfileset

        else:
            nkwargs['fileset'] = drsfile.fileset
        nkwargs['filesetnames'] = list(drsfile.filesetnames)
        # ------------------------------------------------------------------
        nkwargs['outfunc'] = drsfile.outfunc
        nkwargs['dbname'] = copy.deepcopy(drsfile.dbname)
        nkwargs['dbkey'] = copy.deepcopy(drsfile.dbkey)
        nkwargs['datatype'] = copy.deepcopy(drsfile.datatype)
        nkwargs['dtype'] = copy.deepcopy(drsfile.dtype)
        nkwargs['shape'] = copy.deepcopy(drsfile.shape)
        nkwargs['numfiles'] = copy.deepcopy(drsfile.numfiles)
        nkwargs['s1d'] = copy.deepcopy(drsfile.s1d)
        for key in drsfile.required_header_keys:
            nkwargs[key] = drsfile.required_header_keys[key]
        newfile = DrsFitsFile(**nkwargs)
        newfile.get_header_keys(nkwargs)
        # return new instance of DrsFitsFile
        return newfile

    # TODO: Merge/combine with completecopy and copyother
    def copyother(self, drsfile, **kwargs):
        # check recipe has been set
        if 'recipe' not in kwargs:
            self.check_recipe()
        else:
            self.recipe = kwargs['recipe']
        # must check recipe of drsfile
        if drsfile.recipe is None:
            drsfile.recipe = self.recipe
        # set function name
        _ = display_func(None, 'copyother', __NAME__, 'DrsFitsFile')
        # check file has been read (if 'read' not equal to False)
        if kwargs.get('read', True):
            drsfile.check_read(header_only=True, load=True)
        # set empty file attributes
        nkwargs = dict()
        nkwargs['name'] = kwargs.get('name', self.name)
        nkwargs['filetype'] = kwargs.get('filetype', self.filetype)
        nkwargs['suffix'] = kwargs.get('suffix', self.suffix)
        nkwargs['remove_insuffix'] = kwargs.get('remove_insuffix',
                                                self.remove_insuffix)
        nkwargs['prefix'] = kwargs.get('prefix', self.prefix)
        nkwargs['recipe'] = kwargs.get('recipe', self.recipe)
        nkwargs['fiber'] = kwargs.get('fiber', self.fiber)
        nkwargs['fibers'] = kwargs.get('fibers', self.fibers)
        nkwargs['rkeys'] = kwargs.get('rkeys', self.required_header_keys)
        nkwargs['filename'] = kwargs.get('filename', drsfile.filename)
        nkwargs['path'] = kwargs.get('path', drsfile.path)
        nkwargs['basename'] = kwargs.get('basename', drsfile.basename)
        nkwargs['inputdir'] = kwargs.get('inputdir', drsfile.inputdir)
        nkwargs['intype'] = kwargs.get('intype', drsfile.intype)
        nkwargs['directory'] = kwargs.get('directory', drsfile.directory)
        nkwargs['data'] = kwargs.get('data', drsfile.data)
        nkwargs['header'] = kwargs.get('header', drsfile.header)
        nkwargs['shape'] = kwargs.get('shape', drsfile.shape)
        nkwargs['hdict'] = kwargs.get('hdict', drsfile.hdict)
        nkwargs['output_dict'] = kwargs.get('output_dict', drsfile.output_dict)
        nkwargs['fileset'] = kwargs.get('fileset', self.fileset)
        nkwargs['filesetnames'] = kwargs.get('filesetnames', self.filesetnames)
        nkwargs['outfunc'] = kwargs.get('outfunc', self.outfunc)
        nkwargs['dbname'] = kwargs.get('dbname', self.dbname)
        nkwargs['dbkey'] = kwargs.get('dbkey', self.dbkey)
        nkwargs['datatype'] = kwargs.get('datatype', drsfile.datatype)
        nkwargs['dtype'] = kwargs.get('dtype', drsfile.dtype)
        nkwargs['shape'] = kwargs.get('shape', drsfile.shape)
        nkwargs['numfiles'] = kwargs.get('numfiles', drsfile.numfiles)
        nkwargs['s1d'] = kwargs.get('s1d', drsfile.s1d)
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
        # set function name
        _ = display_func(None, 'check_file', __NAME__, 'DrsFitsFile')
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

        # 4. check if we have a fiber defined
        self.has_fiber()

        # if 1, 2 and 3 pass return True
        return True, None

    def has_correct_extension(self, filename=None, filetype=None, argname=None):
        # set function name
        _ = display_func(None, 'has_correct_extension', __NAME__, 'DrsFitsFile')
        # deal with no input extension
        if filetype is None:
            filetype = self.filetype
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
        if filetype is None:
            msg = TextEntry('09-000-00003', args=[basename])
            cond = True
        elif filename.endswith(filetype):
            msg = TextEntry('09-000-00004', args=[basename, filetype])
            cond = True
        else:
            msg = TextEntry('09-000-00005', args=[basename, filetype])
            cond = False
        # if valid return True and no error
        if cond:
            dargs = [argname, os.path.basename(filename)]
            WLOG(params, 'debug', TextEntry('90-001-00009', args=dargs),
                 wrap=False)
            return True, msg
        # if False generate error and return it
        else:
            emsg = TextEntry('09-001-00006', args=[argname, filetype])
            return False, emsg

    def hkeys_exist(self, header=None, filename=None, argname=None):
        # set function name
        func_name = display_func(None, 'hkeys_exist', __NAME__, 'DrsFitsFile')
        # deal with no input header
        if header is None:
            # check file has been read
            self.check_read(header_only=True, load=True)
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
                WLOG(params, 'debug', emsg)
                return False, emsg
            else:
                dargs = [argname, key, basename]
                WLOG(params, 'debug', TextEntry('90-001-00010', args=dargs),
                     wrap=False)
        # if we have got to this point return True (success) and no error
        #   messages
        return True, None

    def has_correct_hkeys(self, header=None, argname=None, log=True):
        # set function name
        _ = display_func(None, 'has_correct_hkeys', __NAME__, 'DrsFitsFile')
        # -----------------------------------------------------------------
        # check recipe has been set
        self.check_recipe()
        # get recipe and parameters
        params = self.recipe.drs_params
        # -----------------------------------------------------------------
        # set function name
        _ = display_func(params, 'has_correct_hkeys', __NAME__, 'DrsFitsFile')
        # deal with no input header
        if header is None:
            # check file has been read
            self.check_read(header_only=True, load=True)
            # get header
            header = self.header
        # get short hand to required header keys
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
                if log:
                    WLOG(params, 'debug', TextEntry('90-001-00011', args=dargs),
                         wrap=False)
                found = False
            else:
                dargs = [argname, key, rvalue]
                if log:
                    WLOG(params, 'debug', TextEntry('90-001-00012', args=dargs),
                         wrap=False)
            # store info
            errors[key] = (found, argname, rvalue, value)
        # return found (bool) and errors
        return found, errors

    def has_fiber(self, header=None):
        # set function name
        _ = display_func(None, 'has_fiber', __NAME__, 'DrsFitsFile')
        # -----------------------------------------------------------------
        # check whether fiber already set (in which case ignore)
        if self.fiber is not None:
            return
        # -----------------------------------------------------------------
        # check recipe has been set
        self.check_recipe()
        # deal with no input header
        if header is None:
            # check file has been read
            self.check_read(header_only=True, load=True)
            # get header
            header = self.header
        # get recipe and parameters
        params = self.recipe.drs_params
        # -----------------------------------------------------------------
        kw_fiber = params['KW_FIBER'][0]
        # -----------------------------------------------------------------
        # deal with fiber
        if kw_fiber in self.header:
            fiber = header[kw_fiber]
        # TODO: remove elif when fiber is always in header if file
        # TODO:     has a fiber
        # TODO: START OF REMOVE ------------------------------------------------
        elif 'AB' in self.basename.split('_')[-1]:
            fiber = 'AB'
        elif 'A' in self.basename.split('_')[-1]:
            fiber = 'A'
        elif 'B' in self.basename.split('_')[-1]:
            fiber = 'B'
        elif 'C' in self.basename.split('_')[-1]:
            fiber = 'C'
        # TODO: END OF REMOVE --------------------------------------------------
        else:
            fiber = None
        # update fiber value
        if fiber is not None:
            self.fiber = fiber

    # -------------------------------------------------------------------------
    # table checking
    # -------------------------------------------------------------------------
    def get_infile_outfilename(self, params, recipe, infilename,
                               allowedfibers=None, ext='.fits'):
        # set function name
        _ = display_func(None, 'get_infile_outfilename', __NAME__,
                         'DrsFitsFile')
        # ------------------------------------------------------------------
        # 1. need to assign an input type for our raw file
        if self.intype is not None:
            # deal with in type being list
            if isinstance(self.intype, list):
                intype = self.intype[0]
            else:
                intype = self.intype
            # get new copy
            infile = intype.newcopy(recipe=recipe)
        else:
            infile = DrsFitsFile('DRS_RAW_TEMP')
        # ------------------------------------------------------------------
        # storage of files
        chain_files = []
        # need to go back through the file history and update filename
        cintype = self.completecopy(infile)
        # loop until we have no intype (raw file)
        while cintype is not None:
            # add to chain
            chain_files.append(self.completecopy(cintype))
            if hasattr(cintype, 'intype'):
                # deal with in type being list
                if isinstance(cintype.intype, list):
                    cintype = cintype.intype[0]
                else:
                    cintype = cintype.intype
            else:
                break
        # ------------------------------------------------------------------
        # set the file name to the infilename
        filename = str(infilename)
        bottomfile = chain_files[-1]
        # now we have chain we can project file (assuming last element in the
        #   chain is the raw file)
        for cintype in chain_files[::-1][1:]:
            bottomfile.filename = filename
            bottomfile.basename = os.path.basename(filename)
            # check whether we need fiber
            if bottomfile.fibers is not None:
                fiber = allowedfibers
            else:
                fiber = None
            # get out file name
            out = cintype.check_table_filename(params, recipe, bottomfile,
                                               fullpath=True,
                                               allowedfibers=fiber)
            valid, outfilename = out
            # set the filename to the outfilename
            filename = outfilename
            bottomfile = cintype
        # ------------------------------------------------------------------
        # add values to infile
        infile.filename = filename
        infile.basename = os.path.basename(filename)
        infile.filetype = ext
        # ------------------------------------------------------------------
        # get outfilename (final)
        valid, outfilename = self.check_table_filename(params, recipe, infile,
                                                       allowedfibers)
        # ------------------------------------------------------------------
        # return infile
        return infile, valid, outfilename

    def check_table_filename(self, params, recipe, infile, allowedfibers=None,
                             fullpath=False):
        """
        Checks whether raw "filename" belongs to this DrsFile

        :param params:
        :param recipe:
        :param infile:
        :param allowedfibers:
        :param fullpath:

        :return:
        """
        # set function name
        func_name = display_func(None, 'check_table_filename', __NAME__,
                                 'DrsFitsFile')
        # ------------------------------------------------------------------
        # deal with fibers
        if allowedfibers is not None:
            if isinstance(allowedfibers, str):
                fibers = [allowedfibers]
            else:
                fibers = list(allowedfibers)
        elif self.fibers is None:
            fibers = [None]
        else:
            fibers = self.fibers
        # set initial value of out filename
        outfilename = infile.filename
        # loop around fibers
        for fiber in fibers:
            # 2. need to assign an output filename for out file
            if self.outfunc is not None:
                outfilename = self.outfunc(params, infile=infile, outfile=self,
                                           fiber=fiber)
            else:
                eargs = [self.name, recipe.name, func_name]
                WLOG(params, 'error', TextEntry('09-503-00009', args=eargs))
                outfilename = None
        # ------------------------------------------------------------------
        # assume file is valid
        valid = True
        # ------------------------------------------------------------------
        # check extension
        if outfilename.endswith(self.filetype):
            # remove extension to test suffix
            filename = outfilename[:-len(self.filetype)]
        else:
            filename = None
            valid = False
            # debug log that extension was incorrect
            dargs = [self.filetype, filename]
            WLOG(params, 'debug', TextEntry('90-008-00004', args=dargs))
        # ------------------------------------------------------------------
        # check suffix (after extension removed)
        if (self.suffix is not None) and valid:
            # if we have no fibers file should end with suffix
            if fibers == [None]:
                if not filename.endswith(self.suffix):
                    valid = False
                    # debug log that extension was incorrect
                    dargs = [self.suffix, filename]
                    WLOG(params, 'debug', TextEntry('90-008-00005', args=dargs))
            # ------------------------------------------------------------------
            # if we have fibers then file should end with one of them and
            # the suffix
            elif len(fibers) > 0:
                # have to set up a new valid that should be True if any
                #  fiber is present
                valid1 = False
                # loop around fibers
                for fiber in fibers:
                    if filename.endswith('{0}_{1}'.format(self.suffix, fiber)):
                        valid1 |= True
                # if valid1 is False debug log that fibers were not found
                if not valid1:
                    dargs = [', '.join(fibers), filename]
                    WLOG(params, 'debug', TextEntry('90-008-00006', args=dargs))
                # put valid1 back into valid
                valid &= valid1
        # ------------------------------------------------------------------
        # return valid (True if filename is valid False otherwise)
        if fullpath:
            return valid, outfilename
        else:
            return valid, os.path.basename(outfilename)

    def check_table_keys(self, params, filedict, rkeys=None):
        """
        Checks whether a dictionary contains the required key/value pairs
        to belong to this DrsFile

        :param params:
        :param filedict:
        :param rkeys:

        :return:
        """
        # set function name
        _ = display_func(None, 'check_table_keys', __NAME__, 'DrsFitsFile')
        # ------------------------------------------------------------------
        # get required keys
        if rkeys is None:
            rkeys = self.required_header_keys
        # assume file is valid
        valid = True
        # loop around required keys
        for key in rkeys:
            # key needs to be in table
            if key in filedict:
                # get rvalue
                rvalues = rkeys[key]
                # check if rvalue is list
                if isinstance(rvalues, str):
                    rvalues = [rvalues]
                # set up aux valid
                valid1 = False
                # loop around
                for rvalue in rvalues:
                    # make sure there are no white spaces and all upper case
                    filedictvalue = filedict[key].strip().upper()
                    rvalueclean = rvalue.strip().upper()
                    # if key is in file dictionary then we should check it
                    if filedictvalue == rvalueclean:
                        valid1 |= True
                # modify valid value
                valid &= valid1
                dargs = [key, valid, rvalues]
                WLOG(params, 'debug', TextEntry('90-008-00003', args=dargs))
                # if we haven't found a key the we can stop here
                if not valid:
                    return False
            else:
                # Log that key was not found
                dargs = [key, ', '.join(list(filedict.keys()))]
                WLOG(params, 'debug', TextEntry('90-008-00002', args=dargs))

        # return valid
        return valid

    # -------------------------------------------------------------------------
    # fits file checking (OLD)
    # -------------------------------------------------------------------------
    def check_file_header(self, quiet=False, argname=None):
        """
        Check file header has all required header keys
        :param quiet:
        :param argname: string, the name of the argument we are checking
                        (for error and debug messages)

        :return:
        """
        # set function name
        func_name = display_func(None, 'check_file_header', __NAME__,
                                 'DrsFitsFile')
        # -----------------------------------------------------------------
        # check file has been read
        self.read_file()
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
    def read_file(self, ext=None, check=False, params=None):
        """
        Read this fits file data and header

        :param ext: int or None, the data extension to open
        :param check: bool, if True checks if data is already read and does
                      not read again, to overwrite/re-read set "check" to False
        :param params: Parameter Dict (not used --in overridden definition)

        :return None:
        """
        # set function name
        _ = display_func(None, 'read_file', __NAME__, 'DrsFitsFile')
        # check if we have data set
        if check:
            cond1 = self.data is not None
            cond2 = self.header is not None
            if cond1 and cond2:
                return True
        # deal with no extension
        if (ext is None) and (self.datatype == 'image'):
            ext = 0
        elif ext is None:
            ext = 1
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

        out = drs_fits.readfits(params, self.filename, getdata=True,
                                gethdr=True, fmt=fmt, ext=ext)

        self.data = out[0]
        self.header = drs_fits.Header.from_fits_header(out[1])
        # set number of data sets to 1
        self.numfiles = 1
        # set the shape
        if (self.data is not None) and (self.datatype == 'image'):
            self.shape = self.data.shape
        elif self.data is not None:
            self.shape = [len(self.data)]

    def read_data(self, ext=0):
        # set function name
        _ = display_func(None, 'read_data', __NAME__, 'DrsFitsFile')
        # check that filename is set
        self.check_filename()
        # get params
        params = self.recipe.drs_params
        # get data
        data = drs_fits.readfits(params, self.filename, ext=ext)
        # set number of data sets to 1
        self.numfiles = 1
        # assign to object
        self.data = data

    def read_header(self, ext=0):
        # set function name
        _ = display_func(None, 'read_header', __NAME__, 'DrsFitsFile')
        # check that filename is set
        self.check_filename()
        # get params
        params = self.recipe.drs_params
        # get header
        header = drs_fits.read_header(params, self.filename, ext=ext)
        # assign to object
        self.header = header

    def check_read(self, header_only=False, load=False):
        # set function name
        _ = display_func(None, 'check_read', __NAME__, 'DrsFitsFile')
        # deal with only wanting to check if header is read
        if header_only:
            if self.header is None:
                if load:
                    return self.read_file()
                func = self.__repr__()
                eargs = [func, func + '.read_file()']
                self.__error__(TextEntry('00-001-00004', args=eargs))
            else:
                return 1
        # check that data/header/comments is not None
        if self.data is None:
            if load:
                return self.read_file()
            func = self.__repr__()
            eargs = [func, func + '.read_file()']
            self.__error__(TextEntry('00-001-00004', args=eargs))

    def read_multi(self, ext=None, check=True):
        # set function name
        _ = display_func(None, 'read_multi', __NAME__, 'DrsFitsFile')
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
        if ext is not None:
            out = drs_fits.readfits(params, self.filename, getdata=True,
                                    ext=ext, gethdr=True,
                                    fmt='fits-image')
        else:
            out = drs_fits.readfits(params, self.filename, getdata=True,
                                    gethdr=True, fmt='fits-multi')
        self.data = out[0][0]
        self.header = drs_fits.Header.from_fits_header(out[1][0])
        self.data_array = out[0]
        # set number of data sets to 1
        self.numfiles = 1
        # append headers (as copy)
        self.header_array = []
        for header in out[1]:
            self.header_array.append(drs_fits.Header.from_fits_header(header))
        # set the shape
        if self.data is not None:
            self.shape = self.data.shape

    def update_header_with_hdict(self):
        # set function name
        _ = display_func(None, 'update_header_with_hdict', __NAME__,
                         'DrsFitsFile')
        # deal with unset header
        if self.header is None:
            self.header = drs_fits.Header()
        # add keys from hdict
        for key in self.hdict:
            self.header[key] = (self.hdict[key], self.hdict.comments[key])

    def write_file(self, params=None):
        # set function name
        func_name = display_func(None, 'write_file', __NAME__, 'DrsFitsFile')
        # get params
        params = self.recipe.drs_params
        # ---------------------------------------------------------------------
        # check that filename is set
        self.check_filename()
        # copy keys from hdict into header
        self.update_header_with_hdict()
        # write to file
        drs_fits.writefits(params, self.filename, self.data, self.header,
                           self.datatype, self.dtype, func=func_name)
        # ---------------------------------------------------------------------
        # write output dictionary
        self.output_dictionary()

    def write_multi(self, data_list, header_list=None, datatype_list=None,
                    dtype_list=None):
        # set function name
        func_name = display_func(None, 'write_multi', __NAME__, 'DrsFitsFile')
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
        # writefits to file
        drs_fits.writefits(params, self.filename, data_list, header_list,
                           datatype_list, dtype_list, func=func_name)
        # ---------------------------------------------------------------------
        # write output dictionary
        self.output_dictionary()

    def get_fiber(self, header=None):
        # set function name
        _ = display_func(None, 'get_fiber', __NAME__, 'DrsFitsFile')
        # get params
        params = self.recipe.drs_params
        # must have fibers defined to be able to get a fiber
        if self.fibers is None:
            return None
        # get fiber header key
        key = params['KW_FIBER'][0]
        # deal with case where no header was given
        if header is None:
            if self.header is not None:
                if key in self.header:
                    return str(self.header[key])
        else:
            if key in header:
                return str(header[key])
        # if we still don't have fiber search in file name for fiber
        for fiber in self.fibers:
            if '_{0}'.format(fiber) in self.basename:
                return fiber
        # if we still don't have fiber then return None
        return None

    def output_dictionary(self):
        """
        Generate the output dictionary (for use while writing)
        Uses OUTPUT_FILE_HEADER_KEYS and DrsFile.hdict to generate an
        output dictionary for this file (for use in indexing)

        Requires DrsFile.filename and DrsFile.recipe to be set

        :return None:
        """
        # set function name
        _ = display_func(None, 'output_dictionary', __NAME__, 'DrsFitsFile')
        # check that recipe is set
        self.check_recipe()
        params = self.recipe.drs_params
        pconstant = self.recipe.drs_pconstant
        # get output dictionary
        output_hdr_keys = pconstant.OUTPUT_FILE_HEADER_KEYS()
        # loop around the keys and find them in hdict (or add null character if
        #     not found)
        for key in output_hdr_keys:
            # deal with header key stores
            if key in params:
                dkey = params[key][0]
            else:
                dkey = str(key)

            if dkey in self.hdict:
                self.output_dict[key] = str(self.hdict[dkey])
            else:
                self.output_dict[key] = '--'

    def combine(self, infiles, math='sum', same_type=True):
        # set function name
        func_name = display_func(None, 'combine', __NAME__, 'DrsFitsFile')
        # define usable math
        available_math = ['sum', 'add', '+', 'average', 'mean', 'subtract',
                          '-', 'divide', '/', 'multiply', 'times', '*']
        # --------------------------------------------------------------------
        # check that recipe is set
        self.check_recipe()
        params = self.recipe.drs_params
        # check that data is read
        self.check_read()
        # set new data to this files data
        data = np.array(self.data)
        # --------------------------------------------------------------------
        # cube
        datacube = [data]
        # combine data into cube
        for infile in infiles:
            # check data is read for infile
            infile.check_read()
            # check that infile matches in name to self
            if (self.name != infile.name) and same_type:
                eargs = [func_name]
                WLOG(params, 'error', TextEntry('00-001-00021', args=eargs))
            # add to cube
            datacube.append(infile.data)
        # make datacube an numpy array
        datacube = np.array(datacube)
        # --------------------------------------------------------------------
        # deal with math
        # --------------------------------------------------------------------
        # log what we are doing
        WLOG(params, '', TextEntry('40-999-00004', args=[math]))
        # if we want to sum the data
        if math in ['sum', 'add', '+']:
            with warnings.catch_warnings(record=True) as _:
                data = mp.nansum(datacube, axis=0)
        # else if we want to subtract the data
        elif math in ['subtract', '-']:
            for im in range(1, len(datacube)):
                data -= datacube[im]
        # else if we want to divide the data
        elif math in ['divide', '/']:
            for im in range(1, len(datacube)):
                data /= datacube[im]
        # else if we want to multiple the data
        elif math in ['multiple', 'times', '*']:
            for im in range(1, len(datacube)):
                data *= datacube[im]
        # elif if mean/average
        elif math in ['average', 'mean']:
            with warnings.catch_warnings(record=True) as _:
                data = mp.nanmean(datacube, axis=0)
        # elif if median
        elif math in ['median', 'med']:
            with warnings.catch_warnings(record=True) as _:
                data = mp.nanmedian(datacube, axis=0)
        # else we have an error in math
        else:
            eargs = [math, ', '.join(available_math), func_name]
            WLOG(params, 'error', TextEntry('00-001-00042', args=eargs))
        # --------------------------------------------------------------------
        # construct keys for new DrsFitsFile
        # set empty file attributes
        nkwargs = dict()
        nkwargs['name'] = self.name
        nkwargs['filetype'] = self.filetype
        nkwargs['suffix'] = self.suffix
        nkwargs['remove_insuffix'] = self.remove_insuffix
        nkwargs['prefix'] = self.prefix
        nkwargs['recipe'] = self.recipe
        nkwargs['fiber'] = self.fiber
        nkwargs['fibers'] = self.fibers
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
        nkwargs['filesetnames'] = self.filesetnames
        nkwargs['outfunc'] = self.outfunc
        # return new instance of DrsFitsFile
        return DrsFitsFile(**nkwargs)

    # -------------------------------------------------------------------------
    # fits file header methods
    # -------------------------------------------------------------------------
    def get_key(self, key, has_default=False, default=None, required=True,
                dtype=float):
        # set function name
        _ = display_func(None, 'get_key', __NAME__, 'DrsFitsFile')
        # run read_header_key method
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
        :param dtype: type, the data type for output

        :return: the value from the header for key
        """
        # set function name
        func_name = display_func(None, 'read_header_key', __NAME__,
                                 'DrsFitsFile')
        # check that recipe is set
        self.check_recipe()
        # check that data is read
        self.check_read(header_only=True, load=True)
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
        # set function name
        func_name = display_func(None, 'read_header_keys', __NAME__,
                                 'DrsFitsFile')
        # check that recipe is set
        self.check_recipe()
        # check that data is read
        self.check_read(header_only=True, load=True)
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
        # set function name
        func_name = display_func(None, 'read_header_key_1d_list', __NAME__,
                                 'DrsFitsFile')
        # check that data is read
        self.check_read(header_only=True, load=True)
        # check key is valid
        drskey = self._check_key(key)
        # ------------------------------------------------------------------
        # deal with no dim1 key
        if dim1 is None:
            # use wild card to try to find keys
            wildkey = drskey.split('{')[0] + '*'
            # use wild card in header
            wildvalues = self.header[wildkey]
            # deal with no wild card values found
            if wildvalues is None:
                eargs = [wildkey, dim1, self.basename, func_name]
                self.__error__(TextEntry('09-000-00008', args=eargs))
            # else get the length of dim1
            else:
                dim1 = len(wildvalues)
        # ------------------------------------------------------------------
        # create 1d list
        values = []
        # loop around the 2D array
        for it in range(dim1):
            # construct the key name
            keyname = test_for_formatting(drskey, it)
            # try to get the values
            try:
                # set the value
                values.append(dtype(self.header[keyname]))
            except KeyError:
                eargs = [keyname, dim1, self.basename, func_name]
                self.__error__(TextEntry('09-000-00008', args=eargs))
                values = None
        # return values
        return np.array(values)

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
        # set function name
        func_name = display_func(None, 'read_header_key_2d_list', __NAME__,
                                 'DrsFitsFile')
        # check that data is read
        self.check_read(header_only=True, load=True)
        # check key is valid
        drskey = self._check_key(key)
        # create 2d list
        values = np.zeros((dim1, dim2), dtype=dtype)
        # loop around the 2D array
        dim1, dim2 = values.shape
        for it in range(dim1):
            for jt in range(dim2):
                # construct the key name
                keyname = test_for_formatting(drskey, it * dim2 + jt)
                # try to get the values
                try:
                    # set the value
                    values[it][jt] = dtype(self.header[keyname])
                except KeyError:
                    eargs = [keyname, drskey, dim1, dim2, self.basename,
                             func_name]
                    self.__error__(TextEntry('09-000-00009', args=eargs))
        # return values
        return values

    def _check_key(self, key):
        # set function name
        _ = display_func(None, '_check_key', __NAME__, 'DrsFitsFile')
        # get drs parameters
        drs_params = self.recipe.drs_params
        # need to check drs_params for key (if key is not in header)
        if (key not in self.header) and (key in drs_params):
            store = drs_params[key]
            # see if we have key store
            if isinstance(store, list) and len(store) == 3:
                drskey = store[0]
                source = 'store[0]'
            # if we dont assume we have a string
            else:
                drskey = store
                source = 'store'
        else:
            drskey = str(key)
            source = 'input'
        # debug log message
        dargs = [key, drskey, source]
        WLOG(drs_params, 'debug', TextEntry('90-008-00001', args=dargs))
        # return drskey
        return drskey

    def copy_original_keys(self, drs_file=None, forbid_keys=True, root=None,
                           allkeys=False, group=None, exclude_groups=None):
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

        :param allkeys: bool, if True return all keys from header

        :param group: string, if not None sets the group to use (will only
                      copy this groups header keys)

        :param exclude_groups: string or list or strings, if not None sets the
                              group or groups not to include in copy

        :return None:
        """
        # set function name
        _ = display_func(None, 'copy_original_keys', __NAME__, 'DrsFitsFile')
        # get params
        params = self.recipe.drs_params
        # generate instances from params
        Keyword = constants.constant_functions.Keyword
        keyworddict = params.get_instanceof(Keyword)
        # get pconstant
        pconstant = self.recipe.drs_pconstant
        # deal with exclude groups
        if exclude_groups is not None:
            if isinstance(exclude_groups, str):
                exclude_groups = [exclude_groups]
        # get drs_file header/comments
        if drs_file is None:
            self.check_read(header_only=True, load=True)
            fileheader = self.header
        else:
            # check that data/header is read
            drs_file.check_read(header_only=True, load=True)
            fileheader = drs_file.header

        def __keep_card(card):
            key = card[0]
            if root is not None:
                if not key.startswith(root):
                    return False
            # deal with exclude groups
            if exclude_groups is not None:
                # loop around keys
                for exgrp in exclude_groups:
                    # check if key is in keyword dict and return the
                    #    corresponding key (mkey) if found
                    cond, mkey = _check_keyworddict(key, keyworddict)
                    # if key is in keyword dict look if group matches
                    if cond:
                        keygroup = keyworddict[mkey].group
                        # if key group is None skip check
                        if keygroup is None:
                            continue
                        # if key group is equal to exclude group then return
                        #    False  i.e. don't keep
                        if keygroup.upper() == exgrp.upper():
                            return False
            # deal with group (have to get keyword instance from keyworddict
            #    then check if it has a group then see if group = keygroup)
            if group is not None:
                # check if key is in keyword dict and return the corresponding
                #    key (mkey) if found
                cond, mkey = _check_keyworddict(key, keyworddict)
                # if key is in keyword dict look if group matches
                if cond:
                    keygroup = keyworddict[mkey].group
                    # if key group is None skip it
                    if keygroup is None:
                        return False
                    # if key group does not match group skip it
                    if keygroup.upper() != group.upper():
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

        # deal with appending to a hidct that isn't empty
        if self.hdict is None:
            self.hdict = drs_fits.Header(copy_cards)
        else:
            for _card in copy_cards:
                self.hdict.append(_card)

        # return True to show completed successfully
        return True

    def add_hkey(self, key=None, keyword=None, value=None, comment=None,
                 fullpath=False):
        """
        Add a new key to DrsFile.hdict from kwstore. If kwstore is None
        and key and comment are defined these are used instead.

            Each keywordstore is in form:
                [key, value, comment]    where key and comment are strings

            DrsFile.hdict is updated with hdict[key] = (value, comment)

        :param key: string or None, if kwstore not defined this is the key to
                    set in hdict[key] = (value, comment)

        :param keyword:

        :param value: object or None, if any python object (other than None)
                      will set the value of hdict[key] to (value, comment)

        :param comment: string or None, if kwstore not define this is the
                        comment to set in hdict[key] = (value, comment)

        :param fullpath: bool, if true header keys retain the full path
                         if False filenames are cut down to just the filename
                         (os.path.basename)

        :return:
        """
        # set function name
        func_name = display_func(None, 'add_hkey', __NAME__, 'DrsFitsFile')
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

        # deal with paths (should only contain filename for header)
        if isinstance(value, str):
            if os.path.isfile(value) and (not fullpath):
                value = os.path.basename(value)

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
        # set function name
        func_name = display_func(None, 'add_hkeys', __NAME__, 'DrsFitsFile')
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
                self.add_hkey(key=kwstore, value=values[k_it])
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

    def add_hkey_1d(self, key=None, values=None, keyword=None,
                    comment=None, dim1name=None):
        """
        Add a new 1d list to key using the "kwstore"[0] or "key" as prefix
        in form:
            keyword = kwstore + row number
            keyword = key + row number
        and pushes it into DrsFile.hdict in form:
            hdict[keyword] = (value, comment)

        :param key: string or None, if kwstore not defined this is the key to
                    set in hdict[key] = (value, comment)
        :param values: numpy array or 1D list of keys or None
                       if numpy array or 1D list will create a set of keys
                       in form keyword = kwstore + row number
                      where row number is the position in values
                      with value = values[row number][column number]
        :param keyword: string, if key is None uses key and comment in form
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
        # set function name
        func_name = display_func(None, 'add_hkey_1d', __NAME__, 'DrsFitsFile')
        # deal with no keywordstore
        if (key is None) and (keyword is None or comment is None):
            self.__error__(TextEntry('00-001-00014', args=[func_name]))
        # deal with no dim1name
        if dim1name is None:
            dim1name = 'dim1'
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
            okey, dvalue, comment = self.get_keywordstore(kwstore, func_name)
        else:
            okey, dvalue, comment = keyword, None, comment
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
            keyname = test_for_formatting(okey, it)
            # get the value
            value = values[it]
            # deal with paths (should only contain filename for header)
            if isinstance(value, str):
                if os.path.isfile(value):
                    value = os.path.basename(value)
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

        :param key: string or None, if kwstore not defined this is the key to
                    set in hdict[key] = (value, comment)
        :param values: numpy array or 1D list of keys or None
                       if numpy array or 1D list will create a set of keys
                       in form keyword = kwstore + row number
                      where row number is the position in values
                      with value = values[row number][column number]
        :param keyword: string, if key is None uses key and comment in form
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
        # set function name
        func_name = display_func(None, 'add_hkeys_2d', __NAME__, 'DrsFitsFile')
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
                # deal with paths (should only contain filename for header)
                if isinstance(value, str):
                    if os.path.isfile(value):
                        value = os.path.basename(value)
                # construct the comment name
                cargs = [comment, dim1name, it, dim2name, jt]
                comm = '{0} {1}={2} {3}={4}'.format(*cargs)
                # add to header dictionary
                self.hdict[keyname] = (value, comm)

    def add_qckeys(self, qcparams):
        # set function name
        func_name = display_func(None, 'add_qckeys', __NAME__, 'DrsFitsFile')
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
        # add a final criteria that says whether everything passed or not
        qc_all = params['KW_DRS_QC'][0]
        self.hdict[qc_all] = np.all(qcparams[3])

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
            # set function name
            func_name = display_func(None, 'get_keywordstore', __NAME__,
                                     'DrsFitsFile')
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
        # set function name
        _ = display_func(None, 'copy_hdict', __NAME__, 'DrsFitsFile')
        # set this instance to the hdict instance of another drs fits file
        self.hdict = drsfile.hdict

    # -------------------------------------------------------------------------
    # database methods
    # -------------------------------------------------------------------------
    def get_dbkey(self, **kwargs):
        # set function name
        func_name = display_func(None, 'get_dbkey', __NAME__, 'DrsFitsFile')
        # update func name if in keywords
        func_name = kwargs.get('func', func_name)
        # deal with dbkey not set
        if self.raw_dbkey is None or self.dbkey is None:
            return None
        # update fiber if needed
        self.fiber = kwargs.get('fiber', self.fiber)
        # get parameters for error message
        if self.recipe is not None:
            params = self.recipe.drs_params
        else:
            params = None
        # deal with fiber being required but still unset
        if self.fibers is not None and self.fiber is None:
            eargs = [self, func_name]
            WLOG(params, 'error', TextEntry('00-001-00032', args=eargs))
        # add fiber name to dbkey
        if self.fibers is not None:
            if not self.raw_dbkey.endswith('_' + self.fiber):
                self.dbkey = '{0}_{1}'.format(self.raw_dbkey, self.fiber)
        else:
            self.dbkey = str(self.raw_dbkey)
        # make dbkey uppdercase
        if self.dbkey is not None:
            self.dbkey = self.dbkey.upper()
        # return dbkey
        return self.dbkey


class DrsNpyFile(DrsInputFile):
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
        # set function name
        _ = display_func(None, '__init__', __NAME__, 'DrsNpyFile')
        # define a name
        self.name = name
        # get super init
        DrsInputFile.__init__(self, name, **kwargs)
        # if ext in kwargs then we have a file extension to check
        self.filetype = kwargs.get('filetype', '.fits')
        self.inext = kwargs.get('inext', '.fits')
        # get fiber type (if set)
        self.fibers = kwargs.get('fibers', None)
        self.fiber = kwargs.get('fiber', None)
        # get tag
        self.outfunc = kwargs.get('outfunc', None)
        self.outtag = kwargs.get('KW_OUTPUT', 'UNKNOWN')
        self.dbname = kwargs.get('dbname', None)
        self.raw_dbkey = kwargs.get('dbkey', None)
        self.dbkey = kwargs.get('dbkey', None)
        # set empty fits file storage
        self.data = kwargs.get('data', None)
        self.filename = kwargs.get('filename', None)

    def read_file(self, ext=None, check=False, params=None):
        # set function name
        func_name = display_func(None, 'read_file', __NAME__, 'DrsNpyFile')
        # if filename is set
        if self.filename is not None:
            try:
                # read file
                self.data = np.load(self.filename)
            except Exception as e:
                eargs = [type(e), e, self.filename, func_name]
                WLOG(params, 'error', TextEntry('00-008-00018', args=eargs))
        # cause error if file name is not set
        else:
            WLOG(params, 'error', TextEntry('00-008-00013', args=[func_name]))

    def write_file(self, params=None):
        # set function name
        func_name = display_func(None, 'write_file', __NAME__, 'DrsNpyFile')
        # if filename is not set raise error
        if self.filename is None:
            WLOG(params, 'error', TextEntry('00-008-00013', args=[func_name]))
        if self.data is not None:
            try:
                # save to file
                np.save(self.filename, self.data)
            except Exception as e:
                eargs = [type(e), e, self.filename, func_name]
                WLOG(params, 'error', TextEntry('00-008-00015', args=eargs))
        else:
            eargs = [self.filename, func_name]
            WLOG(params, 'error', TextEntry('00-008-00014', args=eargs))

    def string_output(self):
        """
        String output for DrsFitsFile. If fiber is not None this also
        contains the fiber type

        i.e. DrsFitsFile[{name}_{fiber}] or DrsFitsFile[{name}]
        :return string: str, the string to print
        """
        # set function name
        _ = display_func(None, 'string_output', __NAME__, 'DrsNpyFile')
        # if we do not have a fiber print the string representation of drs npy
        if self.fiber is None:
            return 'DrsNpyFile[{0}]'.format(self.name)
        # if we do add fiber to the string representation
        else:
            return 'DrsNpyFile[{0}_{1}]'.format(self.name, self.fiber)

    def __str__(self):
        """
        Defines the str(DrsFitsFile) return for DrsFitsFile
        :return str: the string representation of DrsFitsFile
                     i.e. DrsFitsFile[name] or DrsFitsFile[name_fiber]
        """
        # set function name
        _ = display_func(None, '__str__', __NAME__, 'DrsNpyFile')
        # return string output
        return self.string_output()

    def __repr__(self):
        """
        Defines the print(DrsFitsFile) return for DrsFitsFile
        :return str: the string representation of DrsFitsFile
                     i.e. DrsFitsFile[name] or DrsFitsFile[name_fiber]
        """
        # set function name
        _ = display_func(None, '__repr__', __NAME__, 'DrsNpyFile')
        # return string output
        return self.string_output()

    def newcopy(self, **kwargs):
        # set function name
        _ = display_func(None, 'newcopy', __NAME__, 'DrsNpyFile')
        # copy this instances values (if not overwritten)
        name = kwargs.get('name', self.name)
        kwargs['filetype'] = kwargs.get('filetype', self.filetype)
        kwargs['suffix'] = kwargs.get('suffix', self.suffix)
        kwargs['remove_insuffix'] = kwargs.get('remove_insuffix',
                                               self.remove_insuffix)
        kwargs['prefix'] = kwargs.get('prefix', self.prefix)
        kwargs['fiber'] = kwargs.get('fiber', self.fiber)
        kwargs['fibers'] = kwargs.get('fibers', self.fibers)
        kwargs['recipe'] = kwargs.get('recipe', self.recipe)
        kwargs['filename'] = kwargs.get('filename', self.filename)
        kwargs['path'] = kwargs.get('path', self.path)
        kwargs['basename'] = kwargs.get('basename', self.basename)
        kwargs['inputdir'] = kwargs.get('inputdir', self.inputdir)
        kwargs['directory'] = kwargs.get('directory', self.directory)
        kwargs['data'] = kwargs.get('data', self.data)
        kwargs['header'] = kwargs.get('header', self.header)
        kwargs['fileset'] = kwargs.get('fileset', self.fileset)
        kwargs['filesetnames'] = kwargs.get('filesetnames', self.filesetnames)
        kwargs['indextable'] = kwargs.get('indextable', self.indextable)
        kwargs['outfunc'] = kwargs.get('outfunc', self.outfunc)
        kwargs['dbname'] = kwargs.get('dbname', self.dbname)
        kwargs['dbkey'] = kwargs.get('dbkey', self.dbkey)
        kwargs['raw_dbkey'] = kwargs.get('raw_dbkey', self.raw_dbkey)
        # return new instance
        return DrsNpyFile(name, **kwargs)

    def completecopy(self, drsfile):
        # set function name
        _ = display_func(None, 'completecopy', __NAME__, 'DrsNpyFile')
        # set empty file attributes
        nkwargs = dict()
        nkwargs['name'] = copy.deepcopy(drsfile.name)
        nkwargs['filetype'] = copy.deepcopy(drsfile.filetype)
        nkwargs['suffix'] = copy.deepcopy(drsfile.suffix)
        nkwargs['remove_insuffix'] = bool(drsfile.remove_insuffix)
        nkwargs['prefix'] = copy.deepcopy(drsfile.prefix)
        nkwargs['recipe'] = drsfile.recipe
        nkwargs['fiber'] = copy.deepcopy(drsfile.fiber)
        nkwargs['fibers'] = copy.deepcopy(drsfile.fibers)
        nkwargs['filename'] = copy.deepcopy(drsfile.filename)
        nkwargs['path'] = copy.deepcopy(drsfile.path)
        nkwargs['basename'] = copy.deepcopy(drsfile.basename)
        nkwargs['inputdir'] = copy.deepcopy(drsfile.inputdir)
        nkwargs['directory'] = copy.deepcopy(drsfile.directory)
        nkwargs['data'] = copy.deepcopy(drsfile.data)
        nkwargs['header'] = copy.deepcopy(drsfile.header)
        # ------------------------------------------------------------------
        if drsfile.fileset is None:
            nkwargs['fileset'] = None
        elif isinstance(drsfile.fileset, list):
            # set up new file set storage
            newfileset = []
            # loop around file sets
            for fileseti in drsfile.fileset:
                newfileset.append(fileseti.completecopy(fileseti))
            # append to nkwargs
            nkwargs['fileset'] = newfileset

        else:
            nkwargs['fileset'] = drsfile.fileset
        nkwargs['filesetnames'] = list(drsfile.filesetnames)
        # ------------------------------------------------------------------
        nkwargs['indextable'] = copy.deepcopy(drsfile.indextable)
        nkwargs['outfunc'] = drsfile.outfunc
        nkwargs['dbname'] = copy.deepcopy(drsfile.dbname)
        nkwargs['dbkey'] = copy.deepcopy(drsfile.dbkey)
        nkwargs['raw_dbkey'] = copy.deepcopy(drsfile.raw_dbkey)
        # return new instance of DrsFitsFile
        return DrsNpyFile(**nkwargs)

    # -------------------------------------------------------------------------
    # database methods
    # -------------------------------------------------------------------------
    def get_dbkey(self, **kwargs):
        # set function name
        func_name = display_func(None, 'get_dbkey', __NAME__, 'DrsNpyFile')
        # if we have function name
        func_name = kwargs.get('func', func_name)
        # deal with dbkey not set
        if self.raw_dbkey is None or self.dbkey is None:
            return None
        # update fiber if needed
        self.fiber = kwargs.get('fiber', self.fiber)
        # get parameters for error message
        if self.recipe is not None:
            params = self.recipe.drs_params
        else:
            params = None
        # deal with fiber being required but still unset
        if self.fibers is not None and self.fiber is None:
            eargs = [self, func_name]
            WLOG(params, 'error', TextEntry('00-001-00032', args=eargs))
        # add fiber name to dbkey
        if self.fibers is not None:
            if not self.raw_dbkey.endswith('_' + self.fiber):
                self.dbkey = '{0}_{1}'.format(self.raw_dbkey, self.fiber)
        else:
            self.dbkey = str(self.raw_dbkey)
        # make dbkey uppdercase
        if self.dbkey is not None:
            self.dbkey = self.dbkey.upper()
        # return dbkey
        return self.dbkey


# =============================================================================
# User functions
# =============================================================================
def add_required_keywords(drs_filelist, keys):
    # set function name
    _ = display_func(None, 'add_required_keywords', __NAME__)
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
    # set function name
    _ = display_func(None, 'deal_with_bad_header', __NAME__)
    # define condition to pass
    cond = True
    # define iterator
    it = 0
    # define storage
    datastore = []
    headerstore = []
    # loop through HDU's until we cannot open them
    while cond:
        # noinspection PyBroadException,PyPep8
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
    # set function name
    _ = display_func(None, 'construct_header_error', __NAME__)
    # get error storage
    keys, rvalues, values = herrors
    # get text for this language/instrument
    text = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
    # if we have no keys return None
    if len(keys) == 0:
        return None
    # set up a message for the error messages
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
    # set function name
    _ = display_func(None, 'test_for_formatting', __NAME__)
    # test the formatting by entering a number as format
    test_str = key.format(number)
    # if they are the same after test return key with the key and number in
    if test_str == key:
        return '{0}{1}'.format(key, number)
    # else we just return the test string
    else:
        return test_str


def is_forbidden_prefix(pconstant, key):
    # set function name
    _ = display_func(None, 'is_forbidden_prefix', __NAME__)
    # assume key is not forbidden
    cond = False
    # if prefix is forbidden and key starts with this prefix -->
    #   set cond to true (key is not forbidden)
    for prefix in pconstant.FORBIDDEN_HEADER_PREFIXES():
        if key.startswith(prefix):
            cond = True
    # return condition on whether key is forbidden
    return cond


def _check_keyworddict(key, keyworddict):
    """
    Some keys have formatting i.e. LOCE{0:04d} and thus for these we need to
    check their prefix matches the key (else we just check whole key)

    This ONLY works under the assumption that all format keys look as following:

        AAAA{0:4d}

        BBB{0:2d}

    (i.e. a string followed by a single formatting)

    :param key: string, key in header to check
    :param keyworddict: dictionary, the keyword dictionary to check (from
                        keyword definitions)

    :type key: str
    :type keyworddict: dict

    :return:
    """
    # set function name
    _ = display_func(None, '_check_keyworddict', __NAME__)
    # loop around keys in keyword dict
    for mkey in keyworddict:
        # check if we have not formatting (assuming int/float)
        # noinspection PyBroadException
        try:
            if mkey.format(0) == mkey:
                # if key is found then we stop here
                if key == mkey:
                    return True, mkey
                # we can skip to next key
                else:
                    continue
        # if it breaks assume we have a none int/float format
        except Exception as _:
            pass
        # else remove the formatting (assume it start with a '{'
        prefix = mkey.split('{')[0]
        # if key is found we stop here
        if key.startswith(prefix):
            return True, mkey
        else:
            continue
    # if we have checked every key then key is not found
    return False, None


# =============================================================================
# End of code
# =============================================================================
