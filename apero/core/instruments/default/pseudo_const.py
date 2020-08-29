#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-18 at 14:44

@author: cook
"""
import importlib
import sys
import os
from typing import List, Tuple

from apero.base import base
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


# =============================================================================
# Define Constants class (pseudo constants)
# =============================================================================
class PseudoConstants:
    def __init__(self, instrument=None):
        self.instrument = instrument

    # =========================================================================
    # File and Recipe definitions
    # =========================================================================
    def FILEMOD(self):
        module_name = 'apero.core.instruments.default.file_definitions'
        return importlib.import_module(module_name)

    def RECIPEMOD(self):
        module_name = 'apero.core.instruments.default.recipe_definitions'
        return importlib.import_module(module_name)

    # =========================================================================
    # HEADER SETTINGS
    # =========================================================================
    def VALID_RAW_FILES(self):
        valid = ['.fits']
        return valid

    # =========================================================================
    # HEADER SETTINGS
    # =========================================================================
    # noinspection PyPep8Naming
    def FORBIDDEN_COPY_KEYS(self):
        """
        Defines the keys in a HEADER file not to copy when copying over all
        HEADER keys to a new fits file

        :return forbidden_keys: list of strings, the keys in a HEADER file not
                                to copy from and old fits file
        """
        forbidden_keys = []
        # return keys
        return forbidden_keys

    # noinspection PyPep8Naming
    def FORBIDDEN_HEADER_PREFIXES(self):
        """
        Define the QC keys prefixes that should not be copied (i.e. they are
        just for the input file not the output file)

        :return keys:
        """
        prefixes = ['QCC', 'INF1', 'INF2', 'INF3', 'INP1']
        # return keys
        return prefixes

    # noinspection PyPep8Naming
    def FORBIDDEN_DRS_KEY(self):
        # DRS OUTPUT KEYS
        forbidden_keys = ['WAVELOC', 'REFRFILE', 'DRSPID', 'VERSION',
                          'DRSOUTID']
        # return keys
        return forbidden_keys

    # noinspection PyPep8Naming
    def HEADER_FIXES(self, **kwargs):
        """
        This should do nothing unless an instrument header needs fixing

        :param header: DrsFitsFile header

        :return: the fixed header
        """
        # get arguments from kwargs
        params = kwargs.get('params')
        recipe = kwargs.get('recipe')
        header = kwargs.get('header')
        filename = kwargs.get('filename')
        # return header
        return header

    def DRS_OBJ_NAME(self, objname):
        """
        Do nothing by default
        :param objname: str
        :return:
        """
        return objname

    # =========================================================================
    # INDEXING SETTINGS
    # =========================================================================
    # noinspection PyPep8Naming
    def INDEX_OUTPUT_FILENAME(self):
        filename = 'index.fits'
        return filename

    # noinspection PyPep8Naming
    def INDEX_LOCK_FILENAME(self, params):
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
    def OUTPUT_FILE_HEADER_KEYS(self):
        """
        Output file header keys.
        Used for indexing

        :param p:
        :return:
        """
        # Get required header keys from spirouKeywords.py (via p)
        output_keys = ['KW_DATE_OBS', 'KW_UTC_OBS', 'KW_ACQTIME',
                       'KW_MID_OBS_TIME', 'KW_OBJNAME', 'KW_OBSTYPE',
                       'KW_EXPTIME', 'KW_CCAS', 'KW_CREF', 'KW_CDEN',
                       'KW_DPRTYPE', 'KW_OUTPUT', 'KW_CMPLTEXP', 'KW_NEXP',
                       'KW_VERSION', 'KW_PPVERSION', 'KW_PI_NAME', 'KW_PID',
                       'KW_FIBER']
        # return output_keys
        return output_keys

    # TODO: remove these
    # # noinspection PyPep8Naming
    # def RAW_OUTPUT_KEYS(self):
    #     # define selected keys
    #     output_keys = ['KW_DATE_OBS', 'KW_UTC_OBS', 'KW_ACQTIME',
    #                    'KW_MID_OBS_TIME', 'KW_OBJNAME', 'KW_OBSTYPE',
    #                    'KW_EXPTIME', 'KW_DPRTYPE', 'KW_CCAS', 'KW_CREF',
    #                    'KW_CDEN', 'KW_CMPLTEXP', 'KW_NEXP', 'KW_PI_NAME',
    #                    'KW_PID']
    #     # return these keys
    #     return output_keys
    #
    # # noinspection PyPep8Naming
    # def REDUC_OUTPUT_KEYS(self):
    #     # define selected keys
    #     output_keys = ['KW_DATE_OBS', 'KW_UTC_OBS', 'KW_MID_OBS_TIME',
    #                    'KW_OBJNAME', 'KW_OUTPUT', 'KW_DPRTYPE',
    #                    'KW_VERSION', 'KW_PID', 'KW_FIBER']
    #     # return these keys
    #     return output_keys
    #
    # # noinspection PyPep8Naming
    # def GEN_OUTPUT_COLUMNS(self):
    #     output_keys = ['KW_DATE_OBS', 'KW_UTC_OBS', 'KW_MID_OBS_TIME',
    #                    'KW_OBJNAME', 'KW_OBSTYPE', 'KW_EXPTIME',
    #                    'KW_OUTPUT', 'KW_DPRTYPE', 'KW_VERSION', 'KW_PID']
    #     return output_keys

    # =========================================================================
    # DISPLAY/LOGGING SETTINGS
    # =========================================================================
    # noinspection PyPep8Naming
    def CHARACTER_LOG_LENGTH(self):
        length = 80
        return length

    # noinspection PyPep8Naming
    def COLOUREDLEVELS(self, p=None):
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
        # reference:
        colors = drs_misc.Colors()
        if p is not None:
            if 'THEME' in p:
                colors.update_theme(p['THEME'])
        # http://ozzmaker.com/add-colour-to-text-in-python/
        clevels = dict(error=colors.fail,  # red
                       warning=colors.warning,  # yellow
                       info=colors.okblue,  # blue
                       graph=colors.ok,  # magenta
                       all=colors.okgreen,  # green
                       debug=colors.debug)  # green
        return clevels

    def EXIT(self, params):
        """
        Defines how to exit based on the string defined in
        spirouConst.LOG_EXIT_TYPE()

        :return my_exit: function
        """
        my_exit = params.get('DRS_LOG_EXIT_TYPE', 'sys')
        if my_exit == 'sys':
            return sys.exit
        elif my_exit == 'os':
            # noinspection PyProtectedMember
            return os._exit
        else:
            def my_exit(_):
                return None

    def EXIT_LEVELS(self):
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
        exit_levels = ['error']
        return exit_levels

    # noinspection PyPep8Naming
    def LOG_FILE_NAME(self, params, dir_data_msg=None):
        """
        Define the log filename and full path.

        The filename is defined as:
            DRS-YYYY-MM-DD  (GMT date)
        The directory is defined as dir_data_msg (or p['DRS_DATA_MSG'] if not
            defined)

        if p['DRS_USED_DATE'] is set this date is used instead
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
        :param utime: float or None, the unix time to use to set the date, if
                      undefined uses time.time() (time now) - in GMT

        :return lpath: string, the full path and file name for the log file
        """
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
    def LOG_STORAGE_KEYS(self):
        # The storage key to use for each key
        storekey = dict(all='LOGGER_ALL', error='LOGGER_ERROR',
                        warning='LOGGER_WARNING', info='LOGGER_INFO',
                        graph='LOGGER_ALL', debug='LOGGER_DEBUG')
        return storekey

    # noinspection PyPep8Naming
    def LOG_CAUGHT_WARNINGS(self):
        """
        Defines a master switch, whether to report warnings that are caught in

        >> with warnings.catch_warnings(record=True) as w:
        >>     code_that_may_gen_warnings

        :return warn: bool, if True reports warnings, if False does not
        """
        # Define whether we warn
        warn = True
        return warn

    def LOG_TRIG_KEYS(self):
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
        # The trigger character to display for each
        trig_key = dict(all=' ', error='!', warning='@', info='*', graph='~',
                        debug='+')
        return trig_key

    def WRITE_LEVEL(self):
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
        write_level = dict(error=3, warning=2, info=1, graph=0, all=0,
                           debug=0)
        return write_level

    def REPORT_KEYS(self):
        """
        The report levels. Keys must be the same as spirouConst.LOG_TRIG_KEYS()

        If True then the input code is printed (used for errors /warning/debug)

        if False just the message is printed
        """
        write_level = dict(error=True, warning=True, info=False, graph=False,
                           all=False, debug=False)
        return write_level

    def SPLASH(self):
        logo = [" .----------------.  .----------------.  .----------------.   ",
                " | .--------------. || .--------------. || .--------------. | ",
                " | |  ________    | || |  _______     | || |    _______   | | ",
                " | | |_   ___ `.  | || | |_   __ \    | || |   /  ___  |  | | ",
                " | |   | |   `. \ | || |   | |__) |   | || |  |  (__ \_|  | | ",
                " | |   | |    | | | || |   |  __ /    | || |   '.___`-.   | | ",
                " | |  _| |___.' / | || |  _| |  \ \_  | || |  |`\____) |  | | ",
                " | | |________.'  | || | |____| |___| | || |  |_______.'  | | ",
                " | |              | || |              | || |              | | ",
                " | '--------------' || '--------------' || '--------------' | ",
                "  '----------------'  '----------------'  '----------------'  "]
        return logo

    def LOGO(self):
        """
        apero logo

        Font Author: ?

        More Info:
            https://web.archive.org/web/20120819044459/http://www.roysac.com/
                 thedrawfonts-tdf.asp

        FIGFont created with: http://patorjk.com/figfont-editor

        :return:
        """
        logo = ["  █████╗ ██████╗ ███████╗██████╗  ██████╗  ",
                " ██╔══██╗██╔══██╗██╔════╝██╔══██╗██╔═══██╗ ",
                " ███████║██████╔╝█████╗  ██████╔╝██║   ██║ ",
                " ██╔══██║██╔═══╝ ██╔══╝  ██╔══██╗██║   ██║ ",
                " ██║  ██║██║     ███████╗██║  ██║╚██████╔╝ ",
                " ╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝ ╚═════╝  "]

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
    def FIBER_SETTINGS(self, params, fiber):
        func_name = 'FIBER_SETTINGS'
        raise NotImplementedError(NOT_IMPLEMENTED.format(__NAME__, func_name))

    def FIBER_LOC_TYPES(self, fiber):
        return fiber

    def FIBER_WAVE_TYPES(self, fiber):
        return fiber

    def FIBER_DPR_POS(self, dprtype, fiber):
        """
        When we have a DPRTYPE figure out what is in the fiber requested

        :param dprtype: str in form fiber1_fiber2 type in each
                        (e.g. DARK, FLAT, FP, HC, OBJ etc)
        :param fiber: str, the fiber requested

        :return:
        """
        func_name = 'FIBER_DPR_POS'
        raise NotImplementedError(NOT_IMPLEMENTED.format(__NAME__, func_name))

    def FIBER_LOC_COEFF_EXT(self, coeffs, fiber):
        func_name = 'FIBER_LOC_COEFF_EXT'
        raise NotImplementedError(NOT_IMPLEMENTED.format(__NAME__, func_name))

    def FIBER_DATA_TYPE(self, dprtype, fiber):
        func_name = 'FIBER_DATA_TYPE'
        raise NotImplementedError(NOT_IMPLEMENTED.format(__NAME__, func_name))

    def FIBER_CCF(self):
        func_name = 'FIBER_CCF'
        raise NotImplementedError(NOT_IMPLEMENTED.format(__NAME__, func_name))

    def FIBER_KINDS(self):
        func_name = 'FIBER_KINDS'
        raise NotImplementedError(NOT_IMPLEMENTED.format(__NAME__, func_name))

    def INDIVIDUAL_FIBERS(self):
        func_name = 'INDIVIDUAL_FIBERS'
        raise NotImplementedError(NOT_IMPLEMENTED.format(__NAME__, func_name))

    # =========================================================================
    # BERV_KEYS
    # =========================================================================
    def BERV_INKEYS(self):
        # FORMAT:   [in_key, out_key, kind, default]
        #
        #    Where 'in_key' is the header key or param key to use
        #    Where 'out_key' is the output header key to save to
        #    Where 'kind' is 'header' or 'const'
        #    Where default is the default value to assign
        func_name = 'BERV_INKEYS'
        raise NotImplementedError(NOT_IMPLEMENTED.format(__NAME__, func_name))

    def BERV_OUTKEYS(self):
        # FORMAT:   [in_key, out_key, kind, default]
        #
        #    Where 'in_key' is the header key or param key to use
        #    Where 'out_key' is the output header key to save to
        #    Where 'kind' is 'header' or 'const'
        #    Where default is the default value to assign
        func_name = 'BERV_OUTKEYS'
        raise NotImplementedError(NOT_IMPLEMENTED.format(__NAME__, func_name))

    # =========================================================================
    # OTHER KEYS
    # =========================================================================
    def MASTER_DB_KEYS(self):
        func_name = 'MASTER_DB_KEYS'
        raise NotImplementedError(NOT_IMPLEMENTED.format(__NAME__, func_name))

    # =========================================================================
    # PLOT SETTINGS
    # =========================================================================
    def FONT_DICT(self, params):
        """
        Font manager for matplotlib fonts - added to matplotlib.rcParams as a
        dictionary
        :return font: rcParams dictionary (must be accepted by maplotlbi.rcParams)

        see:
          https://matplotlib.org/api/matplotlib_configuration_api.html#matplotlib.rc
        """
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
    def CALIBRATION_DB_COLUMNS(self) -> Tuple[List[str], List[type]]:
        """
        Define the columns used in the calibration database
        :return: list of columns (strings)
        """
        columns = ['KEY', 'FIBER', 'SUPER', 'FILENAME', 'HUMANTIME',
                   'UNIXTIME', 'USED']
        ctypes = [str, str, int, str, str, float, int]
        return columns, ctypes

    def TELLURIC_DB_COLUMNS(self) -> Tuple[List[str], List[type]]:
        """
        Define the columns used in the telluric database
        :return: list of columns (strings)
        """
        columns = ['KEY', 'FIBER', 'SUPER', 'FILENAME', 'HUMANTIME',
                   'UNIXTIME', 'OBJECT', 'AIRMASS', 'TAU_WATER', 'TAU_OTHERS',
                   'USED']
        ctypes = [str, str, int, str, str, float, str, float, float, float, int]
        return columns, ctypes

    def INDEX_DB_COLUMNS(self) -> Tuple[List[str], List[type]]:
        """
        Define the columns used in the index database
        :return: list of columns (strings)
        """
        columns = ['DIRECTORY', 'FILENAME', 'KIND', 'LAST_MODIFIED',
                   'DATE_OBS', 'UTC_OBS', 'MJDMID', 'OBJNAME', 'OBSTYPE',
                   'EXPTIME', 'CCAS', 'CREF', 'CDEN', 'DPRTYPE', 'TRGTYPE',
                   'OUTPUT', 'EXPSEQ', 'NUMEXP', 'VERSION', 'PPVERSION',
                   'PINAME', 'PID', 'FIBER', 'UID', 'USED']
        ctypes = [str, str, str, float, str, str, float, str, str, float,
                  str, str, float, str, str, str, int, int, str, str, str,
                  str, str, str, int]
        return columns, ctypes

    def LOG_DB_COLUMNS(self) -> Tuple[List[str], List[type]]:
        """
        Define the columns use in the log database
        :return: list of columns (strings)
        """
        columns = ['RECIPE', 'RKIND', 'PID', 'HUMANTIME', 'UNIXTIME', 'GROUP',
                   'LEVEL', 'SUBLEVEL', 'LEVELCRIT', 'INPATH', 'OUTPATH',
                   'DIRECTORY', 'LOGFILE', 'PLOTDIR', 'RUNSTRING', 'ARGS',
                   'KWARGS', 'SKWARGS', 'STARTED', 'PASSED_ALL_QC',
                   'QC_STRING', 'QC_NAMES', 'QC_VALUES', 'QC_LOGIC', 'QC_PASS',
                   'ERRORS', 'ENDED', 'USED']
        ctypes = [str, str, str, str, str, str, int, int, str, str, str,
                  str, str, str, str, str, str, str, int, int, str, str, str,
                  str, str, str, int, int]
        return columns, ctypes

    def OBJECT_DB_COLUMNS(self) -> Tuple[List[str], List[type]]:
        """
        Define the columns use in the object database
        :return: list of columns (strings)
        """
        columns = ['OBJNAME', 'GAIAID', 'RA', 'DEC', 'PMRA', 'PMDE', 'PLX',
                   'RV', 'GMAG', 'BPMAG', 'RPMAG', 'EPOCH', 'TEFF', 'USED']
        ctypes = [str, str, float, float, float, float, float, float, float,
                  float, float, float, float, int]
        return columns, ctypes

    def PARAMS_DB_COLUMNS(self) -> Tuple[List[str], List[type]]:
        """
        Define the columns use in the parameter database
        :return: list of columns (Strings)
        """
        columns = ['KEY', 'VALUE', 'DTYPE', 'SOURCE', 'LAST_MODIFIED', 'USED']
        ctypes = [str, str, str, str, float, int]
        return columns, ctypes

    def LANG_DB_COLUMNS(self) -> Tuple[List[str], List[type]]:
        """
        Define the columns use in the language database
        :return:
        """
        columns = ['KEY', 'KIND', 'COMMENT', 'ARGUMENTS'] + base.LANGUAGES
        ctypes = [str, str, str, str] + [str]*len(base.LANGUAGES)
        return columns, ctypes


# =============================================================================
# Define functions
# =============================================================================
# defines the colours


# =============================================================================
# End of code
# =============================================================================
