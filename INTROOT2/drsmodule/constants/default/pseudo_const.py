#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-18 at 14:44

@author: cook
"""
import sys
import os

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'default.pseudo_const'

# =============================================================================
# Define Constants class (pseudo constants)
# =============================================================================
class PseudoConstants:
    def __init__(self, instrument=None):
        self.instrument = instrument

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

    # =========================================================================
    # INDEXING SETTINGS
    # =========================================================================
    # noinspection PyPep8Naming
    def INDEX_OUTPUT_FILENAME(self):
        filename = 'index.fits'
        return filename

    # noinspection PyPep8Naming
    def OUTPUT_FILE_HEADER_KEYS(self, p):
        """
        Output file header keys.

        This list is the master list and RAW_OUTPUT_COLUMNS, REDUC_OUTPUT_COLUMNS
        etc must be in this list
        :param p:
        :return:
        """
        # Get required header keys from spirouKeywords.py (via p)
        output_keys = [p['KW_DATE_OBS'][0],
                       p['KW_UTC_OBS'][0],
                       p['KW_ACQTIME'][0],
                       p['KW_OBJNAME'][0],
                       p['KW_OBSTYPE'][0],
                       p['KW_EXPTIME'][0],
                       p['KW_CCAS'][0],
                       p['KW_CREF'][0],
                       p['KW_CDEN'][0],
                       p['KW_DPRTYPE'][0],
                       p['KW_OUTPUT'][0],
                       p['KW_EXT_TYPE'][0],
                       p['KW_CMPLTEXP'][0],
                       p['KW_NEXP'][0]]
        # return output_keys
        return output_keys

    # noinspection PyPep8Naming
    def RAW_OUTPUT_COLUMNS(self, p):
        func_name = __NAME__ + '.RAW_OUTPUT_COLUMNS()'
        # define selected keys
        output_keys = [p['KW_DATE_OBS'][0],
                       p['KW_UTC_OBS'][0],
                       p['KW_ACQTIME'][0],
                       p['KW_OBJNAME'][0],
                       p['KW_OBSTYPE'][0],
                       p['KW_EXPTIME'][0],
                       p['KW_DPRTYPE'][0],
                       p['KW_CCAS'][0],
                       p['KW_CREF'][0],
                       p['KW_CDEN'][0],
                       p['KW_CMPLTEXP'][0],
                       p['KW_NEXP'][0]]
        # check in master list
        masterlist = __NAME__ + '.OUTPUT_FILE_HEADER_KEYS()'
        for key in output_keys:
            if key not in self.OUTPUT_FILE_HEADER_KEYS(p):
                emsg1 = 'Key {0} must be in {1}'.format(key, masterlist)
                emsg2 = '\tfunction = {0}'.format(func_name)
                raise ValueError(emsg1 + '\n' + emsg2)
        # return keys
        return output_keys

    # noinspection PyPep8Naming
    def REDUC_OUTPUT_COLUMNS(self, p):
        func_name = __NAME__ + '.REDUC_OUTPUT_COLUMNS()'

        output_keys = [p['KW_DATE_OBS'][0],
                       p['KW_UTC_OBS'][0],
                       p['KW_ACQTIME'][0],
                       p['KW_OBJNAME'][0],
                       p['KW_OUTPUT'][0],
                       p['KW_EXT_TYPE'][0]]
        # check in master list
        masterlist = __NAME__ + '.OUTPUT_FILE_HEADER_KEYS()'
        for key in output_keys:
            if key not in self.OUTPUT_FILE_HEADER_KEYS(p):
                emsg1 = 'Key {0} must be in {1}'.format(key, masterlist)
                emsg2 = '\tfunction = {0}'.format(func_name)
                raise ValueError(emsg1 + '\n' + emsg2)
        # return keys
        return output_keys

    # noinspection PyPep8Naming
    def GEN_OUTPUT_COLUMNS(self, p):
        output_keys = [p['KW_DATE_OBS'][0],
                       p['KW_UTC_OBS'][0],
                       p['KW_ACQTIME'][0],
                       p['KW_OBJNAME'][0],
                       p['KW_OBSTYPE'][0],
                       p['KW_EXPTIME'][0],
                       p['KW_OUTPUT'][0],
                       p['KW_EXT_TYPE'][0]]
        return output_keys

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
                or in spirouConst.colors (colour class):
                    HEADER, OKBLUE, OKGREEN, WARNING, FAIL,
                    BOLD, UNDERLINE

        :return clevels: dictionary, containing all the keys identical to
                         LOG_TRIG_KEYS or WRITE_LEVEL, values must be strings
                         that prodive colour information to python print statement
                         see here:
                             http://ozzmaker.com/add-colour-to-text-in-python/
        """
        # reference:
        colors = Colors()
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
        my_exit = params['DRS_LOG_EXIT_TYPE']
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
    def LOG_FILE_NAME(self, p, dir_data_msg=None):
        """
        Define the log filename and full path.

        The filename is defined as:
            DRS-YYYY-MM-DD  (GMT date)
        The directory is defined as dir_data_msg (or p['DRS_DATA_MSG'] if not
            defined)

        if p['DRS_USED_DATE'] is set this date is used instead
        if no utime is defined uses the time now (in gmt time)

        :param p: parameter dictionary, ParamDict containing constants
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
            dir_data_msg = p['DRS_DATA_MSG']

        # deal with no PID
        if 'PID' not in p:
            pid = 'UNKNOWN-PID'
        else:
            pid = p['PID']

        # deal with no recipe
        if 'RECIPE' not in p:
            recipe = 'UNKNOWN-RECIPE'
        else:
            recipe = p['RECIPE'].replace('.py', '')

        # Get the HOST name (if it does not exist host = 'HOST')
        host = os.environ.get('HOST', 'HOST')
        # construct the logfile path
        largs = [host, pid, recipe]
        lpath = os.path.join(dir_data_msg, 'DRS-{0}_{1}_{2}'.format(*largs))

        # return lpath
        return lpath

    # noinspection PyPep8Naming
    def LOG_STORAGE_KEYS(self):
        # The storage key to use for each key
        storekey = dict(all='LOGGER_ALL', error='LOGGER_ERROR',
                        warning='LOGGER_WARNING', info='LOGGER_INFO',
                        graph='LOGGER_ALL', debug='LOGGER_DEBUG')
        return storekey

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
                           all=False, debug=True)
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


# =============================================================================
# Define functions
# =============================================================================
# defines the colours
class Colors:
    BLACK1 = '\033[90;1m'
    RED1 = '\033[1;91;1m'
    GREEN1 = '\033[92;1m'
    YELLOW1 = '\033[1;93;1m'
    BLUE1 = '\033[94;1m'
    MAGENTA1 = '\033[1;95;1m'
    CYAN1 = '\033[1;96;1m'
    WHITE1 = '\033[97;1m'
    BLACK2 = '\033[1;30m'
    RED2 = '\033[1;31m'
    GREEN2 = '\033[1;32m'
    YELLOW2 = '\033[1;33m'
    BLUE2 = '\033[1;34m'
    MAGENTA2 = '\033[1;35m'
    CYAN2 = '\033[1;36m'
    WHITE2 = '\033[1;37m'
    ENDC = '\033[0;0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    def __init__(self, theme=None):
        if theme is None:
            self.theme = 'DARK'
        else:
            self.theme = theme
        self.endc = self.ENDC
        self.bold = self.BOLD
        self.underline = self.UNDERLINE
        self.update_theme()

    def update_theme(self, theme=None):
        if theme is not None:
            self.theme = theme
        if self.theme == 'DARK':
            self.header = self.MAGENTA1
            self.okblue = self.BLUE1
            self.okgreen = self.GREEN1
            self.ok = self.MAGENTA2
            self.warning = self.YELLOW1
            self.fail = self.RED1
            self.debug = self.BLACK1
        else:
            self.header = self.MAGENTA2
            self.okblue = self.MAGENTA2
            self.okgreen = self.BLACK2
            self.ok = self.MAGENTA2
            self.warning = self.BLUE2
            self.fail = self.RED2
            self.debug = self.GREEN2

# =============================================================================
# End of code
# =============================================================================
