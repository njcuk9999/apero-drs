#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-18 at 14:44

@author: cook
"""
import numpy as np
import sys
import os
from typing import Any, Dict, List, Tuple, Type, Union

from apero.base import base
from apero.base import drs_base_classes as base_class
from apero.base import drs_misc
from apero.base import drs_exceptions

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'instruments.default.pseudo_const'
__PATH__ = 'instruments.default'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get error
ConfigError = drs_exceptions.ConfigError
# get not implemented error
NOT_IMPLEMENTED = ('Definition Error: Must be overwritten in instrument '
                   'pseudo_const not {0} \n\t i.e. in apero.core.'
                   'instruments.spirou.pseudoconst.py \n\t method = {1}')
# get display func
display_func = drs_misc.display_func


# =============================================================================
# Define Constants class (pseudo constants)
# =============================================================================
class PseudoConstants:
    def __init__(self, instrument: Union[str, None] = None):
        """
        Pseudo Constants constructor

        :param instrument: str, the drs instrument name
        """
        # set class name
        self.class_name = 'PsuedoConstants'
        # set function name
        _ = display_func(None, '__init__', __NAME__, self.class_name)
        # set instrument name
        self.instrument = instrument

    def __getstate__(self) -> dict:
        """
        For when we have to pickle the class
        :return:
        """
        # set function name
        _ = display_func(None, '__getstate__', __NAME__, self.class_name)
        # set state to __dict__
        state = dict(self.__dict__)
        # return dictionary state
        return state

    def __setstate__(self, state: dict):
        """
        For when we have to unpickle the class

        :param state: dictionary from pickle
        :return:
        """
        # set function name
        _ = display_func(None, '__setstate__', __NAME__, self.class_name)
        # update dict with state
        self.__dict__.update(state)

    def __str__(self) -> str:
        """
        string representation of PseudoConstants
        :return:
        """
        # set function name
        _ = display_func(None, '__str__', __NAME__, self.class_name)
        # return string representation
        return self.__repr__()

    def __repr__(self) -> str:
        """
        string representation of PseudoConstants
        :return:
        """
        # set function name
        _ = display_func(None, '__repr__', __NAME__, self.class_name)
        # return string representation
        return '{0}[{1}]'.format(self.class_name, self.instrument)

    # =========================================================================
    # File and Recipe definitions
    # =========================================================================
    # noinspection PyPep8Naming
    def FILEMOD(self) -> base_class.ImportModule:
        """
        The import for the file definitions
        :return: file_definitions
        """
        # set function name
        func_name = display_func(None, 'FILEMOD', __NAME__, self.class_name)
        # set module name
        module_name = 'apero.core.instruments.default.file_definitions'
        # try to import module
        try:
            return base_class.ImportModule('default.file_definitions',
                                           module_name)
        except Exception as e:
            # raise coded exception
            eargs = [module_name, 'system', func_name, type(e), str(e), '']
            ekwargs = dict(codeid='00-000-00003', level='error',
                           targs=eargs, func_name=func_name)
            raise drs_exceptions.DrsCodedException(**ekwargs)

    # noinspection PyPep8Naming
    def RECIPEMOD(self) -> base_class.ImportModule:
        """
        The import for the recipe defintions

        :return: file_definitions
        """
        # set function name
        func_name = display_func(None, 'RECIPEMOD', __NAME__, self.class_name)
        # set module name
        module_name = 'apero.core.instruments.default.recipe_definitions'
        # try to import module
        try:
            return base_class.ImportModule('default.recipe_definitions',
                                           module_name)
        except Exception as e:
            # raise coded exception
            eargs = [module_name, 'system', func_name, type(e), str(e), '']
            ekwargs = dict(codeid='00-000-00003', level='error',
                           targs=eargs, func_name=func_name)
            raise drs_exceptions.DrsCodedException(**ekwargs)

    # =========================================================================
    # HEADER SETTINGS
    # =========================================================================
    # noinspection PyPep8Naming
    def VALID_RAW_FILES(self) -> List[str]:
        """
        Return the extensions that are valid for raw files

        :return: a list of strings of valid extensions
        """
        # set function name
        _ = display_func(None, 'VALID_RAW_FILES', __NAME__, self.class_name)
        # set valid extentions
        valid = ['.fits']
        return valid

    # noinspection PyPep8Naming
    def FORBIDDEN_COPY_KEYS(self) -> List[str]:
        """
        Defines the keys in a HEADER file not to copy when copying over all
        HEADER keys to a new fits file

        :return forbidden_keys: list of strings, the keys in a HEADER file not
                                to copy from and old fits file
        """
        # set function name
        _ = display_func(None, 'FORBIDDEN_COPY_KEYS', __NAME__, self.class_name)
        # set forbidden keys
        forbidden_keys = []
        # return keys
        return forbidden_keys

    # noinspection PyPep8Naming
    def FORBIDDEN_HEADER_PREFIXES(self) -> List[str]:
        """
        Define the QC keys prefixes that should not be copied (i.e. they are
        just for the input file not the output file)

        :return keys:
        """
        # set function name
        _ = display_func(None, 'FORBIDDEN_HEADER_PREFIXES', __NAME__,
                         self.class_name)
        # set qc prefixes
        prefixes = ['QCC', 'INF1', 'INF2', 'INF3', 'INP1']
        # return keys
        return prefixes

    # noinspection PyPep8Naming
    def FORBIDDEN_DRS_KEY(self) -> List[str]:
        """
        Define a list of keys that should not be copied from headers to new
        headers

        :return: list of strings, the header keys to not be copied
        """
        # set function name
        _ = display_func(None, 'FORBIDDEN_DRS_KEY', __NAME__, self.class_name)
        # DRS OUTPUT KEYS
        forbidden_keys = ['WAVELOC', 'REFRFILE', 'DRSPID', 'VERSION',
                          'DRSOUTID']
        # return keys
        return forbidden_keys

    # noinspection PyPep8Naming
    def HEADER_FIXES(self, params: Any, recipe: Any, header: Any,
                     hdict: Any, filename: str) -> Any:
        """
        This should do nothing unless an instrument header needs fixing

        :param params: ParamDict, the parameter dictionary of constants
        :param recipe: DrsRecipe instance, the recipe instance the call came
                       from
        :param header: drs_fits.Header or astropy.io.fits.Header - containing
                       key words, can be unset if hdict set
        :param hdict:  drs_fits.Header, alternate source for keys, can be
                       unset if header set
        :param filename: str, used for filename reported in exceptions

        :return: the fixed header
        """
        # set function name
        _ = display_func(params, 'HEADER_FIXES', __NAME__, self.class_name)
        # do nothing
        _ = recipe
        _ = hdict
        _ = filename
        # return header
        return header

    # noinspection PyPep8Naming
    def DRS_OBJ_NAME(self, objname: str) -> str:
        """
        Clean and standardize an object name

        Default action: make upper case and remove white spaces

        :param objname: str, input object name
        :return:
        """
        # set function name
        _ = display_func(None, 'DRS_OBJ_NAME', __NAME__, self.class_name)
        # clean object name
        rawobjname = str(objname)
        objectname = rawobjname.strip()
        objectname = objectname.replace(' ', '_')
        objectname = objectname.upper()
        # return object name
        return objectname

    def DRS_DPRTYPE(self, params: Any, recipe: Any, header: Any,
                    filename: str) -> str:
        """
        Get the dprtype for a specific header

        :param params: ParamDict, the parameter dictionary of constants
        :param recipe: DrsRecipe instance (used to get file mod) - used to
                       get correct header keys to check dprtype
        :param header: fits.Header or drs_fits.Header - the header with
                       header keys to id file
        :param filename: str, the filename name header belongs to (for error
                         logging)
        :return: the dprtype - the database type in each fiber (e.g. {AB}_{C}
                 or DARK_DARK)
        """
        # cannot get dprtye without instrument
        _ = params, recipe, header, filename
        # return dprtype
        return 'None'

    def DRS_MIDMJD(self, params: Any, header: Any, filename: str) -> Any:
        """
        Get the midmjd for a specific header

        :param params: ParamDict, the parameter dictionary of constants
        :param header: fits.Header or drs_fits.Header - the header with
                       header keys to id file
        :param filename: str, the filename name header belongs to (for error
                         logging)

        :return: float the
        """
        # cannot get mid mjd without header definitions
        _ = params, header, filename
        # return NOIne
        return 'None'

    # =========================================================================
    # INDEXING SETTINGS
    # =========================================================================
    # noinspection PyPep8Naming
    def INDEX_OUTPUT_FILENAME(self) -> str:
        """
        Define the index output filename

        :return: str, the index output filename
        """
        # set function name
        _ = display_func(None, 'INDEX_OUTPUT_FILENAME', __NAME__,
                         self.class_name)
        # set index file name
        filename = 'index.fits'
        return filename

    # noinspection PyPep8Naming
    def INDEX_LOCK_FILENAME(self, params: Any) -> str:
        """
        Construct the index lock filename

        :param params: ParamDict, parameter dictionary of constants
        :return:
        """
        # set function name
        _ = display_func(params, 'INDEX_LOCK_FILENAME', __NAME__,
                         self.class_name)
        # set night name to unknown initially (change after)
        night_name = 'UNKNOWN'
        # get the night name directory
        if 'NIGHTNAME' in params:
            if params['NIGHTNAME'] is not None:
                night_name = params['NIGHTNAME'].replace(os.sep, '_')
                night_name = night_name.replace(' ', '_')
        # get the index file
        index_file = self.INDEX_OUTPUT_FILENAME()
        # construct the index lock file name
        oargs = [night_name, index_file]
        # get msg path
        msgpath = params['DRS_DATA_MSG_FULL']
        opath = os.path.join(msgpath, '{0}_{1}'.format(*oargs))
        # return the index lock file name
        return opath

    # noinspection PyPep8Naming
    def OUTPUT_FILE_HEADER_KEYS(self) -> List[str]:
        """
        Output file header keys. (Uesd for database)
        Used for indexing

        :return: list of strings, the output file header keys
        """
        # set function name
        _ = display_func(None, 'OUTPUT_FILE_HEADER_KEYS', __NAME__,
                         self.class_name)
        # Get required header keys from spirouKeywords.py (via p)
        output_keys = ['KW_DATE_OBS', 'KW_UTC_OBS', 'KW_ACQTIME',
                       'KW_MID_OBS_TIME', 'KW_OBJNAME', 'KW_OBSTYPE',
                       'KW_EXPTIME', 'KW_CCAS', 'KW_CREF', 'KW_CDEN',
                       'KW_DPRTYPE', 'KW_OUTPUT', 'KW_CMPLTEXP', 'KW_NEXP',
                       'KW_VERSION', 'KW_PPVERSION', 'KW_PI_NAME', 'KW_PID',
                       'KW_FIBER']
        # return output_keys
        return output_keys

    def INDEX_HEADER_KEYS(self) -> Tuple[List[str], List[Type]]:
        """
        Which header keys should we have in the index database.

        Only keys where you have to read many files to get these should be
        added - if you access file by file do not need header key to be here.

        Must overwrite for each instrument

        :return:
        """
        keys = []
        ctypes = []
        # check that filedef keys are present
        for fkey in self.FILEDEF_HEADER_KEYS():
            if fkey not in keys:
                emsg = __NAME__ + '.INDEX_HEADER_KEYS() missing key "{0}"'
                raise AttributeError(emsg.format(fkey))
        # return index header keys
        return keys, ctypes

    def FILEDEF_HEADER_KEYS(self) -> List[str]:
        """
        Define the keys allowed to be used in file definitions

        :return: list of keys
        """
        keys = []
        return keys

    # =========================================================================
    # DISPLAY/LOGGING SETTINGS
    # =========================================================================
    # noinspection PyPep8Naming
    def CHARACTER_LOG_LENGTH(self) -> int:
        """
        Define the maximum length of characters in the log

        :return: int,  the maximum length of characters
        """
        # set function name
        _ = display_func(None, 'CHARACTER_LOG_LENGTH', __NAME__,
                         self.class_name)
        # set default log character length
        length = 80
        return length

    # noinspection PyPep8Naming
    def COLOUREDLEVELS(self, params=None) -> dict:
        """
        Defines the colours if using coloured log.
        Allowed colour strings are found here:
                see here:
                http://ozzmaker.com/add-colour-to-text-in-python/
                or in drs_misc.Colors (colour class):
                    HEADER, OKBLUE, OKGREEN, WARNING, FAIL,
                    BOLD, UNDERLINE

        :return clevels: dictionary, containing all the keys identical to
                         LOG_TRIG_KEYS or WRITE_LEVEL, values must be strings
                         that prodive colour information to python print statement
                         see here:
                             http://ozzmaker.com/add-colour-to-text-in-python/
        """
        # set function name
        _ = display_func(params, 'COLOUREDLEVELS', __NAME__, self.class_name)
        # reference:
        colors = drs_misc.Colors()
        if params is not None:
            if 'THEME' in params:
                colors.update_theme(params['THEME'])
        # http://ozzmaker.com/add-colour-to-text-in-python/
        clevels = dict(error=colors.fail,  # red
                       warning=colors.warning,  # yellow
                       info=colors.okblue,  # blue
                       graph=colors.ok,  # magenta
                       all=colors.okgreen,  # green
                       debug=colors.debug)  # green
        return clevels

    # noinspection PyPep8Naming
    def EXIT(self, params: Any) -> Any:
        """
        Defines how to exit based on the string defined in
        spirouConst.LOG_EXIT_TYPE()

        :param params: ParamDict, parameter dictionary of constants

        :return my_exit: function
        """
        # set function name
        _ = display_func(None, 'EXIT', __NAME__, self.class_name)
        # try to key exit type
        my_exit = params.get('DRS_LOG_EXIT_TYPE', 'sys')
        if my_exit == 'sys':
            return sys.exit
        if my_exit == 'os':
            if hasattr(os, '_exit'):
                return getattr(os, '_exit')
        # return func that returns nothing in all other circumstances
        return lambda pos: None

    # noinspection PyPep8Naming
    def EXIT_LEVELS(self) -> List[str]:
        """
        Defines which levels (in spirouConst.LOG_TRIG_KEYS and
        spirouConst.WRITE_LEVELS) trigger an exit of the DRS after they are
        logged
        (must be a list of strings)

        :return exit_levels: list of strings, the keys in
                             spirouConst.LOG_TRIG_KEYS and
                             spirouConst.WRITE_LEVELS which trigger an exit
                             after they are logged
        """
        # set function name
        _ = display_func(None, 'EXIT_LEVELS', __NAME__, self.class_name)
        # set exit levels
        exit_levels = ['error']
        return exit_levels

    # noinspection PyPep8Naming
    def LOG_FILE_NAME(self, params: Any,
                      dir_data_msg: Union[str, None] = None) -> str:
        """
        Define the log filename and full path.

        The filename is defined as:
            DRS-YYYY-MM-DD  (GMT date)
        The directory is defined as dir_data_msg (or params['DRS_DATA_MSG']
            if not defined)

        if params['DRS_USED_DATE'] is set this date is used instead
        if no utime is defined uses the time now (in gmt time)

        :param params: parameter dictionary, ParamDict containing constants
            Must contain at least:
                    DRS_DATA_MSG: string, the directory that the log messages
                                  should be saved to (if "dir_data_msg" not
                                  defined)
                    DRS_USED_DATE: string, the used date (if not defined or
                                   set to "None" then "utime" is used or if
                                   "utime" not defined uses the time now
        :param dir_data_msg: string or None, if defined the p

        :return lpath: string, the full path and file name for the log file
        """
        # set function name
        _ = display_func(params, 'LOG_FILE_NAME', __NAME__, self.class_name)
        # deal with no dir_data_msg
        if dir_data_msg is None:
            dir_data_msg = str(params['DRS_DATA_MSG'])
        # deal with no PID
        if 'PID' not in params:
            pid = 'UNKNOWN-PID'
        else:
            pid = str(params['PID'])
        # deal with no recipe
        if 'RECIPE' not in params:
            recipe = 'UNKNOWN-RECIPE'
        else:
            recipe = str(params['RECIPE'].replace('.py', ''))
        # construct the logfile path
        largs = [pid, recipe]
        lpath = os.path.join(dir_data_msg, 'APEROL-{0}_{1}.log'.format(*largs))

        # return lpath
        return lpath

    # noinspection PyPep8Naming
    def LOG_STORAGE_KEYS(self) -> Dict[str, str]:
        """
        Create a dictionary of all the levels of logging available (values
        are the params[KEY] to save them in

        :return: dictionary of strings keys are logging levels, values are
                 params[KEY] to save them to
        """
        # set function name
        _ = display_func(None, 'LOG_STORAGE_KEYS', __NAME__, self.class_name)
        # The storage key to use for each key
        storekey = dict(all='LOGGER_ALL', error='LOGGER_ERROR',
                        warning='LOGGER_WARNING', info='LOGGER_INFO',
                        graph='LOGGER_ALL', debug='LOGGER_DEBUG')
        return storekey

    # noinspection PyPep8Naming
    def LOG_CAUGHT_WARNINGS(self) -> bool:
        """
        Defines a master switch, whether to report warnings that are caught in

        >> with warnings.catch_warnings(record=True) as w:
        >>     code_that_may_gen_warnings

        :return warn: bool, if True reports warnings, if False does not
        """
        # set function name
        _ = display_func(None, 'LOG_CAUGHT_WARNINGS', __NAME__, self.class_name)
        # Define whether we warn
        warn = True
        return warn

    # noinspection PyPep8Naming
    def LOG_TRIG_KEYS(self) -> Dict[str, str]:
        """
        The log trigger key characters to use in log. Keys must be the same as
        spirouConst.WRITE_LEVELS()

        i.e.

        if the following is defined:
        >> trig_key[error] = '!'
        and the following log is used:
        >> WLOG(p, 'error', 'message')
        the output is:
        >> print("TIMESTAMP - ! |program|message")

        :return trig_key: dictionary, contains all the trigger keys and the
                          characters/strings to use in logging. Keys must be the
                          same as spirouConst.WRITE_LEVELS()
        """
        # set function name
        _ = display_func(None, 'LOG_TRIG_KEYS', __NAME__, self.class_name)
        # The trigger character to display for each
        trig_key = dict(all=' ', error='!', warning='@', info='*', graph='~',
                        debug='+')
        return trig_key

    # noinspection PyPep8Naming
    def WRITE_LEVEL(self) -> Dict[str, str]:
        """
        The write levels. Keys must be the same as spirouConst.LOG_TRIG_KEYS()

        The write levels define which levels are logged and printed (based on
        constants "PRINT_LEVEL" and "LOG_LEVEL" in the primary config file

        i.e. if
        >> PRINT_LEVEL = 'warning'
        then no level with a numerical value less than
        >> write_level['warning']
        will be printed to the screen

        similarly if
        >> LOG_LEVEL = 'error'
        then no level with a numerical value less than
        >> write_level['error']
        will be printed to the log file

        :return write_level: dictionary, contains the keys and numerical levels
                             of each trigger level. Keys must be the same as
                             spirouConst.LOG_TRIG_KEYS()
        """
        # set function name
        _ = display_func(None, 'WRITE_LEVEL', __NAME__, self.class_name)
        # set the write levels
        write_level = dict(error=3, warning=2, info=1, graph=0, all=0,
                           debug=0)
        return write_level

    # noinspection PyPep8Naming
    def REPORT_KEYS(self) -> dict:
        """
        The report levels. Keys must be the same as spirouConst.LOG_TRIG_KEYS()

        If True then the input code is printed (used for errors /warning/debug)

        if False just the message is printed

        :returns: dictionary of True and False for each level
        """
        # set function name
        _ = display_func(None, 'REPORT_KEYS', __NAME__, self.class_name)
        # set the report level
        report_level = dict(error=True, warning=True, info=False, graph=False,
                            all=False, debug=False)
        return report_level

    # noinspection PyPep8Naming
    def SPLASH(self) -> List[str]:
        """
        The splash image for the instrument
        :return:
        """
        # set function name
        _ = display_func(None, 'SPLASH', __NAME__, self.class_name)
        # set the logo
        logo = [r" .----------------.  .----------------.  .----------------.   ",
                r" | .--------------. || .--------------. || .--------------. | ",
                r" | |  ________    | || |  _______     | || |    _______   | | ",
                r" | | |_   ___ `.  | || | |_   __ \    | || |   /  ___  |  | | ",
                r" | |   | |   `. \ | || |   | |__) |   | || |  |  (__ \_|  | | ",
                r" | |   | |    | | | || |   |  __ /    | || |   '.___`-.   | | ",
                r" | |  _| |___.' / | || |  _| |  \ \_  | || |  |`\____) |  | | ",
                r" | | |________.'  | || | |____| |___| | || |  |_______.'  | | ",
                r" | |              | || |              | || |              | | ",
                r" | '--------------' || '--------------' || '--------------' | ",
                r"  '----------------'  '----------------'  '----------------'  "]
        return logo

    # noinspection PyPep8Naming
    def LOGO(self) -> List[str]:
        """
        The apero logo (coloured)

        Font Author: ?

        More Info:
            https://web.archive.org/web/20120819044459/http://www.roysac.com/
                 thedrawfonts-tdf.asp

        FIGFont created with: http://patorjk.com/figfont-editor

        :return:
        """
        # set function name
        _ = display_func(None, 'LOGO', __NAME__, self.class_name)

        # logo = ["  █████╗ ██████╗ ███████╗██████╗  ██████╗  ",
        #         " ██╔══██╗██╔══██╗██╔════╝██╔══██╗██╔═══██╗ ",
        #         " ███████║██████╔╝█████╗  ██████╔╝██║   ██║ ",
        #         " ██╔══██║██╔═══╝ ██╔══╝  ██╔══██╗██║   ██║ ",
        #         " ██║  ██║██║     ███████╗██║  ██║╚██████╔╝ ",
        #         " ╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝ ╚═════╝  "]
        # set the logo
        logo = ["\t\033[1;91;1m  █████\033[1;37m╗\033[1;91;1m ██████\033[1;37m╗"
                "\033[1;91;1m ███████\033[1;37m╗\033[1;91;1m██████\033[1;37m╗"
                "\033[1;91;1m  ██████\033[1;37m╗\033[1;91;1m  ",

                "\t ██\033[1;37m╔\033[1;91;1m\033[1;37m═\033[1;91;1m\033[1;37m═"
                "\033[1;91;1m██\033[1;37m╗\033[1;91;1m██\033[1;37m╔"
                "\033[1;91;1m\033[1;37m═\033[1;91;1m\033[1;37m═\033[1;91;1m██"
                "\033[1;37m╗\033[1;91;1m██\033[1;37m╔\033[1;91;1m\033[1;37m═"
                "\033[1;91;1m\033[1;37m═\033[1;91;1m\033[1;37m═\033[1;91;1m"
                "\033[1;37m═\033[1;91;1m\033[1;37m╝\033[1;91;1m██\033[1;37m╔"
                "\033[1;91;1m\033[1;37m═\033[1;91;1m\033[1;37m═\033[1;91;1m██"
                "\033[1;37m╗\033[1;91;1m██\033[1;37m╔\033[1;91;1m\033[1;37m═"
                "\033[1;91;1m\033[1;37m═\033[1;91;1m\033[1;37m═\033[1;91;1m██"
                "\033[1;37m╗\033[1;91;1m ",

                "\t ███████\033[1;37m║\033[1;91;1m██████\033[1;37m╔\033[1;91;1m"
                "\033[1;37m╝\033[1;91;1m█████\033[1;37m╗\033[1;91;1m  ██████"
                "\033[1;37m╔\033[1;91;1m\033[1;37m╝\033[1;91;1m██\033[1;37m║"
                "\033[1;91;1m   ██\033[1;37m║\033[1;91;1m ",

                "\t ██\033[1;37m╔\033[1;91;1m\033[1;37m═\033[1;91;1m\033[1;37m═"
                "\033[1;91;1m██\033[1;37m║\033[1;91;1m██\033[1;37m╔\033[1;91;1m"
                "\033[1;37m═\033[1;91;1m\033[1;37m═\033[1;91;1m\033[1;37m═"
                "\033[1;91;1m\033[1;37m╝\033[1;91;1m ██\033[1;37m╔\033[1;91;1m"
                "\033[1;37m═\033[1;91;1m\033[1;37m═\033[1;91;1m\033[1;37m╝"
                "\033[1;91;1m  ██\033[1;37m╔\033[1;91;1m\033[1;37m═\033[1;91;1m"
                "\033[1;37m═\033[1;91;1m██\033[1;37m╗\033[1;91;1m██\033[1;37m║"
                "\033[1;91;1m   ██\033[1;37m║\033[1;91;1m ",

                "\t ██\033[1;37m║\033[1;91;1m  ██\033[1;37m║\033[1;91;1m██"
                "\033[1;37m║\033[1;91;1m     ███████\033[1;37m╗\033[1;91;1m██"
                "\033[1;37m║\033[1;91;1m  ██\033[1;37m║\033[1;91;1m\033[1;37m╚"
                "\033[1;91;1m██████\033[1;37m╔\033[1;91;1m\033[1;37m╝"
                "\033[1;91;1m ",

                "\t \033[1;37m╚\033[1;91;1m\033[1;37m═\033[1;91;1m\033[1;37m╝"
                "\033[1;91;1m  \033[1;37m╚\033[1;91;1m\033[1;37m═\033[1;91;1m"
                "\033[1;37m╝\033[1;91;1m\033[1;37m╚\033[1;91;1m\033[1;37m═"
                "\033[1;91;1m\033[1;37m╝\033[1;91;1m     \033[1;37m╚"
                "\033[1;91;1m\033[1;37m═\033[1;91;1m\033[1;37m═\033[1;91;1m"
                "\033[1;37m═\033[1;91;1m\033[1;37m═\033[1;91;1m\033[1;37m═"
                "\033[1;91;1m\033[1;37m═\033[1;91;1m\033[1;37m╝\033[1;91;1m"
                "\033[1;37m╚\033[1;91;1m\033[1;37m═\033[1;91;1m\033[1;37m╝"
                "\033[1;91;1m  \033[1;37m╚\033[1;91;1m\033[1;37m═\033[1;91;1m"
                "\033[1;37m╝\033[1;91;1m \033[1;37m╚\033[1;91;1m\033[1;37m═"
                "\033[1;91;1m\033[1;37m═\033[1;91;1m\033[1;37m═\033[1;91;1m"
                "\033[1;37m═\033[1;91;1m\033[1;37m═\033[1;91;1m\033[1;37m╝"
                "\033[1;91;1m  \033[0;0m"]

        return logo

    # =========================================================================
    # FIBER SETTINGS
    # =========================================================================
    # noinspection PyPep8Naming
    def FIBER_SETTINGS(self, params: Any, fiber: str) -> Any:
        """
        Get the fiber settings for localisation setup for a specific fiber
        (keys must be stored in params as a set of parameters with all fibers
         provided for i.e. MYKEY_AB, MYKEY_A, MYKEY_B, MYKEY_C)

        :param params: ParamDict the parameter dictionary of constants
        :param fiber: str, the fiber to get keys for
        :return:
        """
        # set function name
        func_name = display_func(None, 'FIBER_SETTINGS', __NAME__,
                                 self.class_name)
        # do nothing
        _ = params
        _ = fiber
        raise NotImplementedError(NOT_IMPLEMENTED.format(__NAME__, func_name))

    # noinspection PyPep8Naming
    def FIBER_LOC_TYPES(self, fiber: str) -> str:
        """
        The fiber localisation types to use (i.e. some fiber types should use
        another fiber for localisation e.g. SPIRou A or B --> AB

        :param fiber: str, the input fiber

        :return: str, the fiber to use for input fiber
        """
        # set function name
        _ = display_func(None, 'FIBER_LOC_TYPES', __NAME__, self.class_name)
        # return input fiber
        return fiber

    # noinspection PyPep8Naming
    def FIBER_WAVE_TYPES(self, fiber: str) -> str:
        """
        The fiber localisation types to use (i.e. some fiber types should use
        another fiber for localisation e.g. SPIRou A or B --> AB

        :param fiber: str, the input fiber

        :return: str, the fiber to use for input fiber
        """
        # set function name
        _ = display_func(None, 'FIBER_WAVE_TYPES', __NAME__, self.class_name)
        # return input fiber
        return fiber

    # noinspection PyPep8Naming
    def FIBER_DPR_POS(self, dprtype: str, fiber: str):
        """
        When we have a DPRTYPE figure out what is in the fiber requested

        :param dprtype: str in form fiber1_fiber2 type in each
                        (e.g. DARK, FLAT, FP, HC, OBJ etc)
        :param fiber: str, the fiber requested

        :return:
        """
        # set function name
        func_name = display_func(None, 'FIBER_DPR_POS', __NAME__,
                                 self.class_name)
        # do nothing
        _ = dprtype
        _ = fiber
        # raise not implemented yet error
        raise NotImplementedError(NOT_IMPLEMENTED.format(__NAME__, func_name))

    # noinspection PyPep8Naming
    def FIBER_LOC_COEFF_EXT(self, coeffs: np.ndarray, fiber: str):
        """
        Extract the localisation coefficients based on how they are stored
        FIBER_LOC_TYPES

        :param coeffs: the input localisation coefficients
        :param fiber: str, the fiber

        :returns: the update coefficients and the number of orders
        """
        # set function name
        func_name = display_func(None, 'FIBER_LOC_COEFF_EXT', __NAME__,
                                 self.class_name)
        # do nothing
        _ = coeffs
        _ = fiber
        raise NotImplementedError(NOT_IMPLEMENTED.format(__NAME__, func_name))

    # noinspection PyPep8Naming
    def FIBER_DATA_TYPE(self, dprtype, fiber):
        """
        Return the data type from a DPRTYPE

        i.e. for OBJ_FP   fiber = 'fiber1'  --> 'OBJ'
             for OBJ_FP   fiber = 'fiber2'  --> 'FP'

        :param dprtype: str, the DPRTYPE (data type {fiber1}_{fiber2})
        :param fiber: str, the current fiber

        :return:
        """
        # set function name
        func_name = display_func(None, 'FIBER_DATA_TYPE', __NAME__,
                                 self.class_name)
        # do nothing
        _ = dprtype
        _ = fiber
        raise NotImplementedError(NOT_IMPLEMENTED.format(__NAME__, func_name))

    # noinspection PyPep8Naming
    def FIBER_CCF(self):
        """
        Get the science and reference fiber to use in the CCF process

        :return: the science and reference fiber
        """
        # set function name
        func_name = display_func(None, 'FIBER_CCF', __NAME__, self.class_name)
        raise NotImplementedError(NOT_IMPLEMENTED.format(__NAME__, func_name))

    # noinspection PyPep8Naming
    def FIBER_KINDS(self):
        """
        Set the fiber kinds (those to be though as as "science" and those to be
        though as as "reference" fibers.

        :return: list of science fibers and the reference fiber
        """
        # set function name
        func_name = display_func(None, 'FIBER_KINDS', __NAME__, self.class_name)
        raise NotImplementedError(NOT_IMPLEMENTED.format(__NAME__, func_name))

    # noinspection PyPep8Naming
    def INDIVIDUAL_FIBERS(self):
        """
        List the individual fiber names

        :return: list of strings, the individual fiber names
        """
        # set function name
        func_name = display_func(None, 'INDIVIDUAL_FIBERS', __NAME__,
                                 self.class_name)
        raise NotImplementedError(NOT_IMPLEMENTED.format(__NAME__, func_name))

    # =========================================================================
    # BERV_KEYS
    # =========================================================================
    # noinspection PyPep8Naming
    def BERV_INKEYS(self):
        """
        Define how we get (INPUT) BERV parameters
        stored as a dictionary of list where each list has format:

        [in_key, out_key, kind, default]

           Where 'in_key' is the header key or param key to use
           Where 'out_key' is the output header key to save to
           Where 'kind' is 'header' or 'const'
           Where default is the default value to assign

           Must include ra and dec

        :return: dictionary of list with above format
        """
        # set function name
        func_name = display_func(None, 'BERV_INKEYS', __NAME__, self.class_name)
        raise NotImplementedError(NOT_IMPLEMENTED.format(__NAME__, func_name))

    # noinspection PyPep8Naming
    def BERV_OUTKEYS(self):
        """
        Define how we store (OUTPUT) BERV parameters
        stored as a dictionary of list where each list has format:

        [in_key, out_key, kind, default]

           Where 'in_key' is the header key or param key to use
           Where 'out_key' is the output header key to save to
           Where 'kind' is 'header' or 'const'
           Where default is the default value to assign

           Must include ra and dec

        :return: dictionary of list with above format
        """
        # set function name
        func_name = display_func(None, 'BERV_OUTKEYS', __NAME__,
                                 self.class_name)
        raise NotImplementedError(NOT_IMPLEMENTED.format(__NAME__, func_name))

    # =========================================================================
    # PLOT SETTINGS
    # =========================================================================
    # noinspection PyPep8Naming
    def FONT_DICT(self, params: Any) -> dict:
        """
        Font manager for matplotlib fonts - added to matplotlib.rcParams as a
        dictionary

        :param params: ParamDict, the parameter dictionary of constants

        :return font: rcParams dictionary (must be accepted by
                      maplotlbi.rcParams)

        see:
          https://matplotlib.org/api/matplotlib_configuration_api.html#matplotlib.rc
        """
        # set function name
        _ = display_func(None, 'FONT_DICT', __NAME__, self.class_name)
        # set up font storage
        font = dict()
        if params['DRS_PLOT_FONT_FAMILY'] != 'None':
            font['family'] = params['DRS_PLOT_FONT_FAMILY']
        if params['DRS_PLOT_FONT_WEIGHT'] != 'None':
            font['weight'] = params['DRS_PLOT_FONT_WEIGHT']
        if params['DRS_PLOT_FONT_SIZE'] > 0:
            font['size'] = params['DRS_PLOT_FONT_SIZE']
        return font

    # =========================================================================
    # DATABASE SETTINGS
    # =========================================================================
    # noinspection PyPep8Naming
    def CALIBRATION_DB_COLUMNS(self) -> Tuple[List[str], List[type]]:
        """
        Define the columns used in the calibration database
        :return: list of columns (strings)
        """
        # set function name
        _ = display_func(None, 'CALIBRATION_DB_COLUMNS', __NAME__,
                         self.class_name)
        # set columns
        columns = ['KEY', 'FIBER', 'SUPER', 'FILENAME', 'HUMANTIME',
                   'UNIXTIME', 'USED']
        ctypes = [str, str, int, str, str, float, int]
        return columns, ctypes

    # noinspection PyPep8Naming
    def TELLURIC_DB_COLUMNS(self) -> Tuple[List[str], List[type]]:
        """
        Define the columns used in the telluric database
        :return: list of columns (strings)
        """
        # set function name
        _ = display_func(None, 'TELLURIC_DB_COLUMNS', __NAME__,
                         self.class_name)
        # set columns
        columns = ['KEY', 'FIBER', 'SUPER', 'FILENAME', 'HUMANTIME',
                   'UNIXTIME', 'OBJECT', 'AIRMASS', 'TAU_WATER', 'TAU_OTHERS',
                   'USED']
        ctypes = [str, str, int, str, str, float, str, float, float, float, int]
        return columns, ctypes

    # noinspection PyPep8Naming
    def INDEX_DB_COLUMNS(self) -> Tuple[List[str], List[type]]:
        """
        Define the columns used in the index database

        Currently defined columns
            - PATH: the path under which files are stored (based on KIND)
            - DIRECTORY: the sub-directory in PATH which files are stored
            - FILENAME: the name of the file (basename)
            - KIND: either raw/tmp/red/calib/tellu/asset
            - LAST_MODIFIED: float, the last modified time of this file
                             (for sorting)
            - RUNSTRING: the arguments entered to make this file
                         (used for checksum)
            - {HKEYS}: see INDEX_HEADER_KEYS()
            - USED: int, whether entry should be used or ignored

        :return: list of columns (strings)
        """
        # set function name
        _ = display_func(None, 'INDEX_DB_COLUMNS', __NAME__,
                         self.class_name)
        # get header keys
        hkeys, htypes = self.INDEX_HEADER_KEYS()
        # set columns
        columns = ['PATH', 'DIRECTORY', 'FILENAME', 'KIND',
                   'LAST_MODIFIED', 'RUNSTRING'] + hkeys + ['USED', 'RAWFIX']
        ctypes = [str, str, str, str, float, str] + htypes + [int, int]
        return columns, ctypes

    # noinspection PyPep8Naming
    def LOG_DB_COLUMNS(self) -> Tuple[List[str], List[type]]:
        """
        Define the columns use in the log database
        :return: list of columns (strings)
        """
        # set function name
        _ = display_func(None, 'LOG_DB_COLUMNS', __NAME__,
                         self.class_name)
        # set columns
        columns = ['RECIPE', 'RKIND', 'PID', 'HUMANTIME', 'UNIXTIME',
                   'GROUPNAME', 'LEVEL', 'SUBLEVEL', 'LEVELCRIT', 'INPATH',
                   'OUTPATH', 'DIRECTORY', 'LOGFILE', 'PLOTDIR', 'RUNSTRING',
                   'ARGS', 'KWARGS', 'SKWARGS', 'STARTED', 'PASSED_ALL_QC',
                   'QC_STRING', 'QC_NAMES', 'QC_VALUES', 'QC_LOGIC', 'QC_PASS',
                   'ERRORS', 'ENDED', 'USED']
        ctypes = [str, str, str, str, float, str, int, int, str, str, str,
                  str, str, str, str, str, str, str, int, int, str, str, str,
                  str, str, str, int, int]
        return columns, ctypes

    # noinspection PyPep8Naming
    def OBJECT_DB_COLUMNS(self) -> Tuple[List[str], List[type]]:
        """
        Define the columns use in the object database
        :return: list of columns (strings)
        """
        # set function name
        _ = display_func(None, 'OBJECT_DB_COLUMNS', __NAME__,
                         self.class_name)
        # set columns
        columns = ['OBJNAME', 'GAIAID', 'RA', 'DEC', 'PMRA', 'PMDE', 'PLX',
                   'RV', 'GMAG', 'BPMAG', 'RPMAG', 'EPOCH', 'TEFF', 'ALIASES',
                   'USED']
        ctypes = [str, str, float, float, float, float, float, float, float,
                  float, float, float, float, str, int]
        return columns, ctypes

    # noinspection PyPep8Naming
    def PARAMS_DB_COLUMNS(self) -> Tuple[List[str], List[type]]:
        """
        Define the columns use in the parameter database
        :return: list of columns (Strings)
        """
        # set function name
        _ = display_func(None, 'PARAMS_DB_COLUMNS', __NAME__,
                         self.class_name)
        # set columns
        columns = ['KEY', 'VALUE', 'DTYPE', 'SOURCE', 'LAST_MODIFIED', 'USED']
        ctypes = [str, str, str, str, float, int]
        return columns, ctypes

    # noinspection PyPep8Naming
    def LANG_DB_COLUMNS(self) -> Tuple[List[str], List[type]]:
        """
        Define the columns use in the language database
        :return:
        """
        # set function name
        _ = display_func(None, 'LANG_DB_COLUMNS', __NAME__,
                         self.class_name)
        # set columns
        columns = ['KEY', 'KIND', 'COMMENT', 'ARGUMENTS'] + base.LANGUAGES
        ctypes = [str, str, str, str] + [str] * len(base.LANGUAGES)
        return columns, ctypes

# =============================================================================
# End of code
# =============================================================================
