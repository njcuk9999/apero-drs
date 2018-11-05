#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2018-11-04 11:16
@author: ncook
Version 0.0.1
"""
from astropy.io import fits
from astropy import version as av
import argparse
import os
import glob
from collections import OrderedDict

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
# get the default log_opt
DPROG = spirouConfig.Constants.DEFAULT_LOG_OPT()
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

            - KW_OUTPUT: this will set the output type for this file (i.e.
                         file.outtag
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
        self.required_header_keys = dict()
        self.get_header_keys(kwargs)
        # set empty attributes
        self.filename = None
        self.directory = None
        self.basename = None
        self.data = None
        self.header = None
        self.shape = None
        self.hdict = OrderedDict()

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
        # copy this instances values (if not overwriten
        name = kwargs.get('name', self.name)
        kwargs['check_ext'] = kwargs.get('check_ext', self.check_ext)
        kwargs['fiber'] = kwargs.get('fiber', self.fiber)
        kwargs['outtag'] = kwargs.get('KW_OUTPUT', self.outtag)
        for key in self.required_header_keys:
            kwargs[key] = self.required_header_keys[key]
        self.get_header_keys(kwargs)
        # return new instance
        return DrsFitsFile(name, **kwargs)

    def set_filename(self, filename):
        """
        Set the filename, basename and directory name from an absolute path

        :param filename: string, absolute path to the file

        :return None:
        """
        func_name = __NAME__ + '.DrsFitsFile.set_filename()'
        # check that filename exists
        if not os.path.exists(filename):
            emsg1 = 'File {0} does not exist'.format(filename)
            emsg2 = '\tfunction = {0}'.format(func_name)
            WLOG('error', self.__error__(), [emsg1, emsg2])
        # set filename, basename and directory name
        self.filename = str(filename)
        self.basename = os.path.basename(filename)
        self.directory = os.path.dirname(filename)

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

    def __error__(self):
        return DPROG

    # -------------------------------------------------------------------------
    # fits file methods
    # -------------------------------------------------------------------------
    # TODO: fill out
    def read(self, ext=None, hdr_ext=0):
        """
        Read this fits file data and header

        :param ext: int or None, the data extension to open
        :param hdr_ext: int, the header extension to open

        :return None:
        """
        func_name = __NAME__ + '.DrsFitsFile.read()'
        # check that filename isn't None
        if self.filename is None:
            emsg = ('Filename is not set. Must set a filename with file.'
                    'set_filename() first.')
            WLOG('error', self.__error__(), emsg)
        # attempt to open hdu of fits file
        try:
            hdu = fits.open(self.filename)
        except Exception as e:
            emsg1 = ('File "{0}" cannot be opened by astropy.io.fits'
                     ''.format(self.basename))
            emsg2 = '\tError {0}: {1}'.format(type(e), e)
            emsg3 = '\tfunction = {0}'.format(func_name)
            WLOG('error', self.__error__(), [emsg1, emsg2, emsg3])
            hdu = None
        # get the number of fits files in filename
        try:
            n_ext = len(hdu)
        except Exception as e:
            wmsg1 = 'Proglem with one of the extensions'
            wmsg2 = '\tError {0}, {1}'.format(type(e), e)
            WLOG('warning', self.__error__(), [wmsg1, wmsg2])
            n_ext = None
        # deal with unknown number of extensions
        if n_ext is None:
            self.data, self.header = deal_with_bad_header(hdu)
        # else get the data and header based on how many extnesions there are
        else:
            # deal with extension number
            if n_ext == 1 and ext is None:
                ext = 0
            elif n_ext > 1 and ext is None:
                ext = 1
            # try to open the data
            try:
                self.data = hdu[ext].data
            except Exception as e:
                emsg1 = ('Could not open data for file "{0}" extension={1}'
                         ''.format(self.basename, ext))
                emsg2 = '\tError {0}: {1}'.format(type(e), e)
                emsg3 = '\tfunction = {0}'.format(func_name)
                WLOG('error', self.__error__(), [emsg1, emsg2, emsg3])
                self.data = None
            # try to open the header
            try:
                self.header = hdu[hdr_ext].header
            except Exception as e:
                emsg1 = ('Could not open header for file "{0}" extension={1}'
                         ''.format(self.basename, hdr_ext))
                emsg2 = '\tError {0}: {1}'.format(type(e), e)
                emsg3 = '\tfunction = {0}'.format(func_name)
                WLOG('error', self.__error__(), [emsg1, emsg2, emsg3])
                self.header = None
        # close the HDU
        if hdu is not None:
            hdu.close()
        # set the shape
        self.shape = self.data.shape


    def read_multi(self):
        pass

    # TODO: fill out
    def write(self, dtype=None):
        func_name = __NAME__ + 'DrsFitsFile.write()'
        # check that filename isn't None
        if self.filename is None:
            emsg = ('Filename is not set. Must set a filename with file.'
                    'set_filename() first.')
            WLOG('error', self.__error__(), emsg)
        # check if file exists and remove it if it does
        if os.path.exists(self.filename):
            try:
                os.remove(self.filename)
            except Exception as e:
                emsg1 = (' File {0} already exists and cannot be overwritten.'
                         ''.format(self.basename))
                emsg2 = '\tError {0}: {1}'.format(type(e), e)
                emsg3 = '\tfunction = {0}'.format(func_name)
                WLOG('error', self.__error__(), [emsg1, emsg2, emsg3])
        # create the primary hdu
        try:
            hdu = fits.PrimaryHDU(self.data)
        except Exception as e:
            emsg1 = 'Cannot open image with astropy.io.fits'
            emsg2 = '\tError {0}: {1}'.format(type(e), e)
            emsg3 = '\tfunction = {0}'.format(func_name)
            WLOG('error', DPROG, [emsg1, emsg2, emsg3])
            hdu = None
        # force type
        if dtype is not None:
            hdu.scale(type=dtype, **SCALEARGS)
        # add header keys to the hdu header
        if self.hdict is not None:
            for key in list(self.hdict.keys()):
                hdu.header[key] = self.hdict[key]

        # write output dictionary


        pass

    def write_multi(self):
        pass


    def output_dictionary(self):
        output_header_keys = spirouConfig.Constants.OUTPUT_FILE_HEADER_KEYS()

    # -------------------------------------------------------------------------
    # fits file header methods
    # -------------------------------------------------------------------------
    def read_key(self, key):
        pass

    def read_keys(self, keys):
        pass

    def read_key_1d_list(self, key):
        pass

    def read_key_2d_list(self, key):
        pass

    def write_key(self):
        pass

    def write_keys(self):
        pass

    def write_key_1d_list(self):
        pass

    def write_keys_2d_list(self):
        pass



# =============================================================================
# Worker functions
# =============================================================================
def deal_with_bad_header(hdu):
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
        WLOG('warning', DPROG, '\tPartially recovered fits file')
        WLOG('warning', DPROG, '\tProblem with ext={0}'.format(it - 1))
    # find the first one that contains equal shaped array
    valid = []
    for d_it in range(len(datastore)):
        if hasattr(datastore[d_it], 'shape'):
            valid.append(d_it)
    # if valid is empty we have a problem
    if len(valid) == 0:
        emsg = 'Recovery failed: Fatal I/O Error cannot load file.'
        WLOG('error', DPROG, emsg)
        data, header = None, None
    else:
        data = datastore[valid[0]]
        header = hdu[0].header
    # return data and header
    return data, header


# =============================================================================
# End of code
# =============================================================================