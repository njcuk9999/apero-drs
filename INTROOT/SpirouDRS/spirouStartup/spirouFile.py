#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2018-11-04 11:16
@author: ncook
Version 0.0.1
"""

# =============================================================================
# Define variables
# =============================================================================
WORKSPACE = './'


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
        self.header = dict()
        self.get_header_keys(kwargs)

    def get_header_keys(self, kwargs):
        # add values to the header
        for kwarg in kwargs:
            if 'KW_' in kwarg.upper():
                self.header[kwarg] = kwargs[kwarg]

    # -------------------------------------------------------------------------
    # class input methods
    # -------------------------------------------------------------------------
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
        for key in self.header:
            kwargs[key] = self.header
        self.get_header_keys(kwargs)
        # return new instance
        return DrsFitsFile(name, **kwargs)

    # TODO: fill out
    def set_filename(self):
        pass

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

    # -------------------------------------------------------------------------
    # fits file methods
    # -------------------------------------------------------------------------
    # TODO: fill out
    def read(self):
        pass

    def read_multi(self):
        pass

    # TODO: fill out
    def write(self):
        pass

    def write_multi(self):
        pass

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
# End of code
# =============================================================================