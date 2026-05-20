#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pseudo constants (function) definitions for NO INSTRUMENT

Created on 2019-01-18 at 14:44

@author: cook
"""
import os
import string
import sys
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import sqlalchemy
from astropy import coordinates as coord
from astropy import units as uu
from astropy.table import Table

from aperocore.base import base
from aperocore.base import resources
from aperocore.core import drs_db
from aperocore.core import drs_misc
from aperocore.core import drs_text
from apero.base import base as apero_base
from apero.core import drs_astrometrics

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'apero.instruments.default.instrument'
__PATH__ = 'instruments.default'
__PACKAGE__ = apero_base.__PACKAGE__
__version__ = apero_base.__version__
__authors__ = apero_base.__authors__
__date__ = apero_base.__date__
__release__ = apero_base.__release__
# get Time / TimeDelta
Time = base.AstropyTime
# get not implemented error
NOT_IMPLEMENTED = ('Definition Error: Must be overwritten in instrument '
                   'pseudo_const not {0} \n\t i.e. in apero.core.'
                   'instruments.spirou.pseudoconst.py \n\t method = {1}')
# get database columns
DatabaseColumns = drs_db.AperoDatabaseColumns
# get display func
display_func = drs_misc.display_func
# define bad characters for objects (alpha numeric + "_")
BAD_OBJ_CHARS = [' '] + list(string.punctuation.replace('_', ''))
# null text
NULL_TEXT = ['', 'None', 'Null']
# define float sqlalchemy column types (forcing them to be floats on return)
SHORT_FLOAT = drs_db.AperoFloat(precision=32, asdecimal=False)
LONG_FLOAT = drs_db.AperoFloat(precision=53, asdecimal=False)


# =============================================================================
# Define Constants class (pseudo constants)
# =============================================================================
# noinspection PyMethodMayBeStatic,PyPep8Naming
class Instrument:
    # set class name
    class_name = 'Instrument'

    def __init__(self, instrument_name: Union[str, None] = None):
        """
        Pseudo Constants constructor

        :param instrument_name: str, the drs instrument name
        """
        # set function name
        # _ = display_func('__init__', __NAME__, self.class_name)
        # set instrument name
        self.instrument = instrument_name
        # storage of things we don't want to compute twice without need
        self.header_cols: Optional[DatabaseColumns] = None
        self.index_cols: Optional[DatabaseColumns] = None
        self.calibration_cols: Optional[DatabaseColumns] = None
        self.telluric_cols: Optional[DatabaseColumns] = None
        self.logdb_cols: Optional[DatabaseColumns] = None

    def __getstate__(self) -> dict:
        """
        For when we have to pickle the class
        :return:
        """
        # set function name
        # _ = display_func('__getstate__', __NAME__, self.class_name)
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
        # _ = display_func('__setstate__', __NAME__, self.class_name)
        # update dict with state
        self.__dict__.update(state)

    def __str__(self) -> str:
        """
        string representation of PseudoConstants
        :return:
        """
        # set function name
        # _ = display_func('__str__', __NAME__, self.class_name)
        # return string representation
        return self.__repr__()

    def __repr__(self) -> str:
        """
        string representation of PseudoConstants
        :return:
        """
        # set function name
        # _ = display_func('__repr__', __NAME__, self.class_name)
        # return string representation
        return '{0}[{1}]'.format(self.class_name, self.instrument)

    def copy(self):
        return Instrument(instrument_name=self.instrument)

    def _not_implemented(self, method_name: str):
        """
        Raise a Not Implemented Error (for methods that are required to be
        defined by PseudoConstants child class i.e. the instrument class)

        :param method_name: str, the method name that needs overriding

        :raises: NotImplementedError

        :return: None
        """
        emsg = '{0} must be defined at instrument level'
        raise NotImplementedError(emsg.format(method_name))

    def get_clists(self) -> List[Any]:
        # this has to be local
        from apero.instruments.default import config
        from apero.instruments.default import constants
        from apero.instruments.default import keywords
        # get constants dicts
        config_dict = config.CDict
        constants_dict = constants.CDict
        keywords_dict = keywords.KDict
        # ---------------------------------------------------------------------
        # return these
        return [config_dict, constants_dict, keywords_dict]

    # =========================================================================
    # File and Recipe definitions
    # =========================================================================
    def FILEMOD(self) -> Any:
        """
        The import for the file definitions
        :return: file_definitions
        """
        # this has to be local
        from apero.instruments.default import file_definitions
        # return import
        return file_definitions

    def RECIPEMOD(self) -> Any:
        """
        The import for the recipe defintions

        :return: file_definitions
        """
        # this has to be local
        from apero.instruments.default import recipe_definitions
        # return import
        return recipe_definitions

    # =========================================================================
    # HEADER SETTINGS
    # =========================================================================
    def HEADER_FIXES(self, params: Any, header: Any,
                     hdict: Any, filename: str, check_aliases: bool = False,
                     objdbm: Any = None):
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
        :param check_aliases: bool, if True check aliases (using database)
        :param objdbm: drs_database.ObjectDatabase - the database to check
                       aliases in
                       
        :return: the fixed header
        """
        # set function name
        # _ = display_func('HEADER_FIXES', __NAME__, self.class_name)
        # do nothing
        _ = params, header, hdict, filename, check_aliases, objdbm
        # raise implementation error
        self._not_implemented('HEADER_FIXES')

    def DRS_OBJ_NAME(self, objname: str) -> str:
        """
        Clean and standardize an object name

        Default action: make upper case and remove white spaces

        Should only be used when we do not have to worry about aliases to
        object names - use:
            objdbm = drs_database.ObjectDatabase(params)
            objdbm.load_db()
            objdbm.find_objname(objname)
        instead to deal with aliases

        :param objname: str, input object name
        :return:
        """
        # return object name
        return clean_object(objname)

    def GET_OBJNAME(self, params: Any, header: Any, filename: str,
                    check_aliases, objdbm: Any = None):
        """
        Get a cleaned version of the object name from the header

        :param params: ParamDict, the parameter dictionary of constants
        :param header: fits header, the header to get the object name from
        :param filename: str, the filename the header belongs to

        :return: str, the cleaned object name
        """
        # cannot get dprtye without instrument
        _ = params,  header, filename, check_aliases, objdbm
        # raise implementation error
        self._not_implemented('DRS_DPRTYPE')

    def DRS_DPRTYPE(self, params: Any, header: Any, filename: str):
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
        _ = params, header, filename
        # raise implementation error
        self._not_implemented('DRS_DPRTYPE')

    def DRS_MIDMJD(self, params: Any, header: Any, filename: str):
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
        # raise implementation error
        self._not_implemented('DRS_MIDMJD')

    def GET_AREL_DATE(self, params: Any, header: Any,
                      delta_key: str):
        """
        Get the apero release date

        :param delta_key: str, the key to use for the time delta
        :return:
        """
        # cannot get mid mjd without header definitions
        _ = params, header, delta_key
        # raise implementation error
        self._not_implemented('GET_AREL_DATE')

    def FRAME_TIME(self, params: Any, header: Any):
        """
        Get the frame time (either from header or constants depending on
        instrument)

        :param params: ParamDict, the parameter dictionary of constants
        :param header: fits.Header or drs_fits.Header - the header with
                       header keys to id file
        :return: float the frame time in seconds
        """
        # cannot get frame time without instrument
        _ = params, header
        # raise implementation error
        self._not_implemented('IMAGE.FRAME_TIME')

    def SATURATION(self, params: Any, header: Any):
        """
        Get the saturation (either from header or constants depending on
        instrument)

        :param params: ParamDict, the parameter dictionary of constants
        :param header: fits.Header or drs_fits.Header - the header with
                       header keys to id file
        :return: float the frame time in seconds
        """
        # cannot get saturation without instrument
        _ = params, header
        # raise implementation error
        self._not_implemented('IMAGE.SATURATION')

    def GET_STOKES_FROM_HEADER(self, params: Any, header: Any, wlog: Any):
        """
        Get the stokes parameter and exposure number from the header

        :param params: ParamDict, the parameter dictionary of constants
        :param header: fits.Header, the fits header to get keys from
        :param wlog: logger for error reporting

        :return: tuple, 1. The stokes parameter, 2. the exposure number
        """
        _ = params, header, wlog
        # raise implementation error
        self._not_implemented('GET_STOKES_FROM_HEADER')

    # =========================================================================
    # INDEXING SETTINGS
    # =========================================================================
    def FILEINDEX_HEADER_COLS(self) -> DatabaseColumns:
        """
        Which header keys should we have in the index database.

        Only keys where you have to read many files to get these should be
        added - if you access file by file do not need header key to be here.

        Must overwrite for each instrument

        :return:
        """
        # check for pre-existing values
        if self.header_cols is not None:
            return self.header_cols
        # set keyts
        header_cols = DatabaseColumns()
        # check that filedef keys are present
        for fkey in self.FILEDEF_HEADER_KEYS():
            if fkey not in header_cols.names:
                emsg = __NAME__ + '.FILEINDEX_HEADER_COLS() missing key "{0}"'
                raise AttributeError(emsg.format(fkey))
        # return index header keys
        self.header_cols = header_cols
        return header_cols

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
    def CHARACTER_LOG_LENGTH(self) -> int:
        """
        Define the maximum length of characters in the log

        :return: int,  the maximum length of characters
        """
        # set function name
        # _ = display_func('CHARACTER_LOG_LENGTH', __NAME__,
        #                  self.class_name)
        # set default log character length
        length = 80
        return length

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
        # _ = display_func('COLOUREDLEVELS', __NAME__, self.class_name)
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

    def EXIT(self, params: Any) -> Any:
        """
        Defines how to exit based on the string defined in
        spirouConst.LOG_EXIT_TYPE()

        :param params: ParamDict, parameter dictionary of constants

        :return my_exit: function
        """
        # set function name
        # _ = display_func('EXIT', __NAME__, self.class_name)
        # try to key exit type
        my_exit = params.get('LOG.EXIT_TYPE', 'sys')
        if my_exit == 'sys':
            return sys.exit
        if my_exit == 'os':
            if hasattr(os, '_exit'):
                return getattr(os, '_exit')
        # return func that returns nothing in all other circumstances
        return lambda pos: None

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
        # _ = display_func('EXIT_LEVELS', __NAME__, self.class_name)
        # set exit levels
        exit_levels = ['error']
        return exit_levels

    def LOG_FILE_NAME(self, params: Any,
                      dir_data_msg: Union[str, None] = None) -> str:
        """
        Define the log filename and full path.

        The filename is defined as:
            DRS-YYYY-MM-DD  (GMT date)
        The directory is defined as dir_data_msg (or params['PATH.LOG']
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
        # _ = display_func('LOG_FILE_NAME', __NAME__, self.class_name)
        # deal with no dir_data_msg
        if dir_data_msg is None:
            dir_data_msg = str(params['PATH.LOG'])
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

    def ADJUST_SUBLEVEL(self, code: str, sublevel: Optional[int] = None):
        """
        Adjust the log code based on sub level (minor and major)

        :param code: str, the default code for logging
        :param sublevel: float, required for giving levels sub level
                         (can filter by this) sets the priority of the message
                         (0 being the lowest, 9 being the highest)

        :return:
        """
        if sublevel is None:
            return code
        # deal with major and minor codes
        if sublevel > 5:
            return '{0}!'.format(code[0])
        else:
            return '{0}$'.format(code[0])

    def SPLASH(self) -> List[str]:
        """
        The splash image for the instrument
        :return:
        """
        # set function name
        # _ = display_func('SPLASH', __NAME__, self.class_name)
        # set the logo
        logo = [r".----------------.  .----------------.  .----------------.  ",
                r"| .--------------. || .--------------. || .--------------. |",
                r"| |  ________    | || |  _______     | || |    _______   | |",
                r"| | |_   ___ `.  | || | |_   __ \    | || |   /  ___  |  | |",
                r"| |   | |   `. \ | || |   | |__) |   | || |  |  (__ \_|  | |",
                r"| |   | |    | | | || |   |  __ /    | || |   '.___`-.   | |",
                r"| |  _| |___.' / | || |  _| |  \ \_  | || |  |`\____) |  | |",
                r"| | |________.'  | || | |____| |___| | || |  |_______.'  | |",
                r"| |              | || |              | || |              | |",
                r"| '--------------' || '--------------' || '--------------' |",
                r" '----------------'  '----------------'  '----------------' "]
        return logo

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
        # _ = display_func('LOGO', __NAME__, self.class_name)

        # logo = ["  █████╗ ██████╗ ███████╗██████╗  ██████╗  ",
        #         " ██╔══██╗██╔══██╗██╔════╝██╔══██╗██╔═══██╗ ",
        #         " ███████║██████╔╝█████╗  ██████╔╝██║   ██║ ",
        #         " ██╔══██║██╔═══╝ ██╔══╝  ██╔══██╗██║   ██║ ",
        #         " ██║  ██║██║     ███████╗██║  ██║╚██████╔╝ ",
        #         " ╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝ ╚═════╝  "]
        # set the logo
        return resources.apero_logo()

    # =========================================================================
    # FIBER SETTINGS
    # =========================================================================
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
        func_name = display_func('FIBER_SETTINGS', __NAME__,
                                 self.class_name)
        # do nothing
        _ = params
        _ = fiber
        raise NotImplementedError(NOT_IMPLEMENTED.format(__NAME__, func_name))

    def FIBER_LOCALISATION(self, fiber):
        """
        Return which fibers to calculate localisation for

        :param fiber: str, fiber name

        :return: list of strings, the fibers to find localisation for
        """
        # set function name
        func_name = display_func('FIBER_LOCALISATION', __NAME__,
                                 self.class_name)
        # do nothing
        _ = fiber
        raise NotImplementedError(NOT_IMPLEMENTED.format(__NAME__, func_name))

    def FIBER_DILATE(self, fiber: str):
        """
        whether we are dilate the imagine due to fiber configuration this should
        only be used when we want a combined localisation solution
        i.e. AB from A and B

        :param fiber: str, the fiber name
        :return: bool, True if we should dilate, False otherwise
        """
        # set function name
        func_name = display_func('FIBER_DILATE', __NAME__,
                                 self.class_name)
        # do nothing
        _ = fiber
        raise NotImplementedError(NOT_IMPLEMENTED.format(__NAME__, func_name))

    def FIBER_DOUBLETS(self, fiber: str):
        """
        whether we have orders coming in doublets (i.e. SPIROUs AB --> A + B)

        :param fiber: str, the fiber name
        :return: bool, True if we have fiber 'doublets', False otherwise
        """
        # set function name
        func_name = display_func('FIBER_DOUBLETS', __NAME__,
                                 self.class_name)
        # do nothing
        _ = fiber
        raise NotImplementedError(NOT_IMPLEMENTED.format(__NAME__, func_name))

    # noinspection PyTypeChecker
    def FIBER_DOUBLET_PARITY(self, fiber: str) -> Union[int, None]:
        """
        Give the doublt fibers parity - all other fibers should not use this
        function

        :param fiber: str, the fiber name
        :return: int or None, either +/-1 (for fiber A/B) or None)
        """
        # set function name
        func_name = display_func('FIBER_DOUBLET_PARITY', __NAME__,
                                 self.class_name)
        # do nothing
        _ = fiber
        raise NotImplementedError(NOT_IMPLEMENTED.format(__NAME__, func_name))

    def FIBER_LOC_TYPES(self, fiber: str) -> str:
        """
        The fiber localisation types to use (i.e. some fiber types should use
        another fiber for localisation e.g. SPIRou A or B --> AB

        :param fiber: str, the input fiber

        :return: str, the fiber to use for input fiber
        """
        # set function name
        # _ = display_func('FIBER_LOC_TYPES', __NAME__, self.class_name)
        # return input fiber
        return fiber

    def FIBER_WAVE_TYPES(self, fiber: str) -> str:
        """
        The fiber localisation types to use (i.e. some fiber types should use
        another fiber for localisation e.g. SPIRou A or B --> AB

        :param fiber: str, the input fiber

        :return: str, the fiber to use for input fiber
        """
        # set function name
        # _ = display_func('FIBER_WAVE_TYPES', __NAME__, self.class_name)
        # return input fiber
        return fiber

    def FIBER_DPR_POS(self, dprtype: str, fiber: str):
        """
        When we have a DPRTYPE figure out what is in the fiber requested

        :param dprtype: str in form fiber1_fiber2 type in each
                        (e.g. DARK, FLAT, FP, HC, OBJ etc)
        :param fiber: str, the fiber requested

        :return:
        """
        # set function name
        func_name = display_func('FIBER_DPR_POS', __NAME__,
                                 self.class_name)
        # do nothing
        _ = dprtype
        _ = fiber
        # raise not implemented yet error
        raise NotImplementedError(NOT_IMPLEMENTED.format(__NAME__, func_name))

    def FIBER_DPRTYPE(self, dprtype: str):
        """
        Input DPRTYPE tells you which fiber we are correcting for

        :param dprtype: str, the dprtype (probably either FLAT_DARK or DARK_FLAT
        :return: str, the fiber
        """
        # set function name
        func_name = display_func('FIBER_DPRTYPE', __NAME__,
                                 self.class_name)
        # do nothing
        _ = dprtype
        # raise not implemented yet error
        raise NotImplementedError(NOT_IMPLEMENTED.format(__NAME__, func_name))

    def FIBER_LOC_PROPS(self, fiber: str, lprops_all: dict):
        # get the cent coefficients
        _ccoeffs = lprops_all[fiber]['CENT_COEFFS']
        fccoeffs, nbo = self.FIBER_LOC_COEFF_EXT(_ccoeffs, fiber)
        # get the wid coefficients
        _wcoeffs = lprops_all[fiber]['WID_COEFFS']
        fwcoeffs, _ = self.FIBER_LOC_COEFF_EXT(_wcoeffs, fiber)
        # get the ycent positions
        _ycent = lprops_all[fiber]['YCENT']
        fycent, _ = self.FIBER_LOC_COEFF_EXT(_ycent, fiber)
        # set the localisation properties
        lprops = dict()
        lprops['LOCOFILE'] = str(lprops_all[fiber]['LOCOFILE'])
        lprops['LOCOTIME'] = float(lprops_all[fiber]['LOCOTIME'])
        lprops['LOCOOBJECT'] = lprops_all[fiber]['LOCOOBJECT']
        lprops['CENT_COEFFS'] = fccoeffs
        lprops['WID_COEFFS'] = fwcoeffs
        lprops['YCENT'] = fycent
        lprops['NBO'] = int(nbo)
        lprops['NBXPIX'] = int(lprops_all[fiber]['NBXPIX'])
        lprops['DEG_C'] = int(lprops_all[fiber]['DEG_C'])
        lprops['DEG_W'] = int(lprops_all[fiber]['DEG_W'])
        lprops['MERGED'] = lprops_all[fiber]['MERGED'] != nbo
        lprops['NSET'] = int(lprops_all[fiber]['NSET'])
        lprops['LOC_POLY_TYPE'] = str(lprops_all[fiber]['LOC_POLY_TYPE'])
        return lprops

    def FIBER_LOC_COEFF_EXT(self, coeffs: np.ndarray, fiber: str):
        """
        Extract the localisation coefficients based on how they are stored
        FIBER_LOC_TYPES

        :param coeffs: the input localisation coefficients
        :param fiber: str, the fiber

        :returns: the update coefficients and the number of orders
        """
        # set function name
        func_name = display_func('FIBER_LOC_COEFF_EXT', __NAME__,
                                 self.class_name)
        # do nothing
        _ = coeffs
        _ = fiber
        raise NotImplementedError(NOT_IMPLEMENTED.format(__NAME__, func_name))

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
        func_name = display_func('FIBER_DATA_TYPE', __NAME__,
                                 self.class_name)
        # do nothing
        _ = dprtype
        _ = fiber
        raise NotImplementedError(NOT_IMPLEMENTED.format(__NAME__, func_name))

    def FIBER_KINDS(self):
        """
        Set the fiber kinds (those to be though as as "science" and those to be
        though as as "reference" fibers.

        :return: list of science fibers and the reference fiber
        """
        # set function name
        func_name = display_func('FIBER_KINDS', __NAME__, self.class_name)
        raise NotImplementedError(NOT_IMPLEMENTED.format(__NAME__, func_name))

    def FIBER_LOC(self, fiber: str) -> Any:
        """
        Set the localisation fibers
        AB --> A, B
        C --> C

        :param fiber:
        :return:
        """
        _ = fiber
        # set function name
        func_name = display_func('FIBER_KINDS', __NAME__, self.class_name)
        raise NotImplementedError(NOT_IMPLEMENTED.format(__NAME__, func_name))

    # tellu fudge
    def TAPAS_INST_CORR(self, mask_water: Table,
                        mask_others: Table) -> Tuple[Table, Table]:
        """
        Default here is to do nothing

        :param mask_water: astropy table the water TAPAS mask table
        :param mask_others: astropy table the others TAPAS mask table

        :return: tuple, 1. the updated mask_water table, 2. the update
                 mask_others table
        """
        # default is to just return full mask in both cases
        return mask_water, mask_others

    def TELLU_BAD_WAVEREGIONS(self) -> List[Tuple[float, float]]:
        """
        Define bad wavelength regions to mask before correcting tellurics

        :return:  list of tuples (float, float), each tuple is a region from
                  min wavelength to max wavelength
        """
        # by default we mask no regions
        return []

    # =========================================================================
    # PLOT SETTINGS
    # =========================================================================
    def FONT_DICT(self, params: Any) -> dict:
        """
        Font manager for matplotlib fonts - added to matplotlib.rcParams as a
        dictionary

        :param params: ParamDict, the parameter dictionary of constants

        :return font: rcParams dictionary (must be accepted by
                      maplotlbi.rcParams)

        see:
          https://matplotlib.org/api/
              matplotlib_configuration_api.html#matplotlib.rc
        """
        # set function name
        # _ = display_func('FONT_DICT', __NAME__, self.class_name)
        # set up font storage
        font = dict()
        if params['PLOT.CORE.FONT_FAMILY'] != 'None':
            font['family'] = params['PLOT.CORE.FONT_FAMILY']
        if params['PLOT.CORE.FONT_WEIGHT'] != 'None':
            font['weight'] = params['PLOT.CORE.FONT_WEIGHT']
        if params['PLOT.CORE.FONT_SIZE'] > 0:
            font['size'] = params['PLOT.CORE.FONT_SIZE']
        return font

    # =========================================================================
    # DATABASE SETTINGS
    # =========================================================================
    def GET_DB_COLS(self, tname: str) -> Union[DatabaseColumns, None]:
        """
        Get a DB column definition based on tname (database table name)

        :param tname: str, the database table name

        :return: DatabaseColumn class if valid otherwise None
        """
        # get definitions from base
        database_names = apero_base.DATABASE_NAMES
        database_col_classes = apero_base.DATABASE_COL_CLASS
        # loop around database types
        for it, key in enumerate(database_names):
            if tname == key:

                if database_col_classes[it] is None:
                    return None
                else:
                    return getattr(self, database_col_classes[it])

    def CALIBRATION_DB_COLUMNS(self) -> DatabaseColumns:
        """
        Define the columns used in the calibration database
        :return: list of columns (strings)
        """
        # set function name
        # _ = display_func('CALIBRATION_DB_COLUMNS', __NAME__,
        #                  self.class_name)
        # check for pre-existing values
        if self.calibration_cols is not None:
            return self.calibration_cols
        # set columns
        calib_columns = DatabaseColumns()
        calib_columns.add(name='KEYNAME', datatype=sqlalchemy.String(20),
                          is_index=True, is_unique=True)
        calib_columns.add(name='FIBER', datatype=sqlalchemy.String(10),
                          is_unique=True)
        calib_columns.add(name='REFCAL', datatype=sqlalchemy.Integer,
                          is_unique=True)
        calib_columns.add(name='FILENAME', datatype=sqlalchemy.String(200),
                          is_unique=True)
        calib_columns.add(name='HUMANTIME', datatype=sqlalchemy.String(50))
        calib_columns.add(name='UNIXTIME', is_index=True,
                          datatype=LONG_FLOAT)
        calib_columns.add(name='PID', is_index=True,
                          datatype=sqlalchemy.String(80))
        calib_columns.add(name='PDATE', datatype=sqlalchemy.String(50))
        calib_columns.add(name='USED', datatype=sqlalchemy.Integer)
        # return columns
        self.calibration_cols = calib_columns
        return calib_columns

    def TELLURIC_DB_COLUMNS(self) -> DatabaseColumns:
        """
        Define the columns used in the telluric database
        :return: list of columns (strings)
        """
        # set function name
        # _ = display_func('TELLURIC_DB_COLUMNS', __NAME__, self.class_name)
        # check for pre-existing values
        if self.telluric_cols is not None:
            return self.telluric_cols
        # set columns
        tellu_columns = DatabaseColumns()
        tellu_columns.add(name='KEYNAME', is_index=True, is_unique=True,
                          datatype=sqlalchemy.String(20))
        tellu_columns.add(name='FIBER', is_unique=True,
                          datatype=sqlalchemy.String(10))
        tellu_columns.add(name='REFCAL', is_unique=True,
                          datatype=sqlalchemy.Integer)
        tellu_columns.add(name='FILENAME', is_unique=True,
                          datatype=sqlalchemy.String(200))
        tellu_columns.add(name='HUMANTIME', datatype=sqlalchemy.String(50))
        tellu_columns.add(name='UNIXTIME', is_index=True,
                          datatype=LONG_FLOAT)
        tellu_columns.add(name='OBJECT', is_index=True,
                          datatype=sqlalchemy.String(80))
        tellu_columns.add(name='AIRMASS', datatype=SHORT_FLOAT)
        tellu_columns.add(name='TAU_WATER',  datatype=SHORT_FLOAT)
        tellu_columns.add(name='TAU_OTHERS', datatype=SHORT_FLOAT)
        tellu_columns.add(name='RUN_ID', datatype=sqlalchemy.String(80))
        tellu_columns.add(name='BERV', datatype=LONG_FLOAT)
        tellu_columns.add(name='BJD', datatype=LONG_FLOAT)
        tellu_columns.add(name='PID', is_index=True,
                          datatype=sqlalchemy.String(80))
        tellu_columns.add(name='PDATE', datatype=sqlalchemy.String(50))
        tellu_columns.add(name='USED', datatype=sqlalchemy.Integer)
        # return columns and ctypes
        self.telluric_cols = tellu_columns
        return tellu_columns

    def FILEINDEX_DB_COLUMNS(self) -> DatabaseColumns:
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

        :return: tuple, list of columns (strings), list of types, list of
                 columns that should be unique
        """
        # set function name
        # _ = display_func('FILEINDEX_DB_COLUMNS', __NAME__, self.class_name)
        # check for pre-existing values
        if self.index_cols is not None:
            return self.index_cols
        # column definitions
        index_cols = DatabaseColumns()
        index_cols.add(name='BLOCK_KIND', is_index=True,
                       datatype=sqlalchemy.String(20))
        index_cols.add(name='OBS_DIR', datatype=sqlalchemy.String(200),
                       is_index=True)
        index_cols.add(name='FILENAME', is_index=True,
                       datatype=sqlalchemy.String(200))
        index_cols.add(name='LAST_MODIFIED', datatype=LONG_FLOAT)
        index_cols.add(name='RECIPE', datatype=sqlalchemy.String(200))
        index_cols.add(name='RUNSTRING',
                       datatype=sqlalchemy.TEXT)
        index_cols.add(name='INFILES',
                       datatype=sqlalchemy.TEXT)
        # get header keys
        header_columns = self.FILEINDEX_HEADER_COLS()
        # add header columns to index columns
        index_cols += header_columns
        # add extra columns
        index_cols.add(name='USED', datatype=sqlalchemy.Integer)
        index_cols.add(name='RAWFIX', datatype=sqlalchemy.Integer)
        # manage index groups
        index_cols.indexes.append(sqlalchemy.Index('idx_block_obs_used',
                                                   'BLOCK_KIND', 'OBS_DIR',
                                                   'USED'))
        index_cols.indexes.append(sqlalchemy.Index('idx_block_obs_filename',
                                                   'BLOCK_KIND', 'OBS_DIR',
                                                   'FILENAME'))
        # manage unique groups
        index_cols.uniques += ['BLOCK_KIND', 'OBS_DIR', 'FILENAME']
        # return column object
        return index_cols

    def LOG_DB_COLUMNS(self) -> DatabaseColumns:
        """
        Define the columns use in the log database
        :return: list of columns (strings)
        """
        # set function name
        # _ = display_func('LOG_DB_COLUMNS', __NAME__,
        #                  self.class_name)
        # check for pre-existing values
        if self.logdb_cols is not None:
            return self.logdb_cols
        # set columns (dictionary form for clarity
        log_columns = DatabaseColumns(name_prefix='rlog.')
        log_columns.add(name='RECIPE', datatype=sqlalchemy.String(200),
                        comment='Recipe name from recipe log')
        log_columns.add(name='SHORTNAME', datatype=sqlalchemy.String(20),
                        comment='Recipe shortname from recipe log')
        log_columns.add(name='BLOCK_KIND', is_index=True,
                        datatype=sqlalchemy.String(20),
                        comment='Recipe block type')
        log_columns.add(name='RECIPE_TYPE', datatype=sqlalchemy.String(80),
                        comment='Recipe type')
        log_columns.add(name='RECIPE_KIND', datatype=sqlalchemy.String(80),
                        comment='Recipe kind')
        log_columns.add(name='PROGRAM_NAME', datatype=sqlalchemy.String(80),
                        comment='Recipe Program Name')
        log_columns.add(name='PID', datatype=sqlalchemy.String(80),
                        is_index=True,
                        comment='Recipe drs process id number')
        log_columns.add(name='HUMANTIME', datatype=sqlalchemy.String(25),
                        comment='Recipe process time (human format)')
        log_columns.add(name='UNIXTIME', datatype=LONG_FLOAT,
                        is_index=True,
                        comment='Recipe process time (unix format)')
        log_columns.add(name='GROUPNAME', datatype=sqlalchemy.String(200),
                        comment='Recipe group name')
        log_columns.add(name='LEVEL', datatype=sqlalchemy.Integer,
                        comment='Recipe level name')
        log_columns.add(name='SUBLEVEL', datatype=sqlalchemy.Integer,
                        comment='Recipe sub-level name')
        log_columns.add(name='LEVELCRIT', datatype=sqlalchemy.String(80),
                        comment='Recipe level/sub level description')
        log_columns.add(name='INPATH',
                        datatype=sqlalchemy.TEXT,
                        comment='Recipe inputs path')
        log_columns.add(name='OUTPATH',
                        datatype=sqlalchemy.TEXT,
                        comment='Recipe outputs path')
        log_columns.add(name='OBS_DIR', datatype=sqlalchemy.String(200),
                        is_index=True,
                        comment='Recipe observation directory')
        log_columns.add(name='LOGFILE',
                        datatype=sqlalchemy.TEXT,
                        comment='Recipe log file path')
        log_columns.add(name='PLOTDIR',
                        datatype=sqlalchemy.TEXT,
                        comment='Recipe plot file path')
        log_columns.add(name='RUNSTRING',
                        datatype=sqlalchemy.TEXT,
                        comment='Recipe run string')
        log_columns.add(name='ARGS',
                        datatype=sqlalchemy.TEXT,
                        comment='Recipe argument list')
        log_columns.add(name='KWARGS',
                        datatype=sqlalchemy.TEXT,
                        comment='Recipe keyword argument list')
        log_columns.add(name='SKWARGS',
                        datatype=sqlalchemy.TEXT,
                        comment='Recipe special argument list')
        log_columns.add(name='START_TIME', datatype=sqlalchemy.String(25),
                        comment='Recipe start time YYYY-mm-dd HH:MM:SS.SSS')
        log_columns.add(name='END_TIME', datatype=sqlalchemy.String(25),
                        comment='Recipe end time YYYY-mm-dd HH:MM:SS.SSS')
        log_columns.add(name='STARTED', datatype=sqlalchemy.Integer,
                        comment='flag recipe started')
        log_columns.add(name='PASSED_ALL_QC', datatype=sqlalchemy.Integer,
                        comment='flag recipe passed all quality control')
        log_columns.add(name='QC_STRING',
                        datatype=sqlalchemy.TEXT,
                        comment='full quality control string')
        log_columns.add(name='QC_NAMES',
                        datatype=sqlalchemy.TEXT,
                        comment='full quality control names')
        log_columns.add(name='QC_VALUES',
                        datatype=sqlalchemy.TEXT,
                        comment='full quality control values')
        log_columns.add(name='QC_LOGIC',
                        datatype=sqlalchemy.TEXT,
                        comment='full quality control logic')
        log_columns.add(name='QC_PASS',
                        datatype=sqlalchemy.TEXT,
                        comment='full quality control pass/fail')
        log_columns.add(name='ERRORMSGS',
                        datatype=sqlalchemy.TEXT,
                        comment='recipe errors')
        log_columns.add(name='ENDED', datatype=sqlalchemy.Integer,
                        comment='flag for recipe ended '
                                '(false at time of writing)')
        log_columns.add(name='FLAGNUM', datatype=sqlalchemy.Integer,
                        comment='binary flag decimal number')
        log_columns.add(name='FLAGSTR',
                        datatype=sqlalchemy.TEXT,
                        comment='binary flag names (one for each binary flag)')
        log_columns.add(name='USED', datatype=sqlalchemy.Integer,
                        comment='Whether file should be used (always true)')
        log_columns.add(name='RAM_USAGE_START', datatype=SHORT_FLOAT,
                        comment='RAM usuage at start of recipe / GB')
        log_columns.add(name='RAM_USAGE_END', datatype=SHORT_FLOAT,
                        comment='RAM usuage at end of recipe / GB')
        log_columns.add(name='RAM_TOTAL', datatype=SHORT_FLOAT,
                        comment='Total RAM at start')
        log_columns.add(name='SWAP_USAGE_START', datatype=SHORT_FLOAT,
                        comment='SWAP usuage at start of recipe / GB')
        log_columns.add(name='SWAP_USAGE_END', datatype=SHORT_FLOAT,
                        comment='SWAP usuage at end of recipe / GB')
        log_columns.add(name='SWAP_TOTAL', datatype=SHORT_FLOAT,
                        comment='Total SWAP at start')
        log_columns.add(name='CPU_USAGE_START', datatype=SHORT_FLOAT,
                        comment='CPU usage at the start  or recipe (percent)')
        log_columns.add(name='CPU_USAGE_END', datatype=SHORT_FLOAT,
                        comment='CPU usage at the end  or recipe (percent)')
        log_columns.add(name='CPU_NUM', datatype=sqlalchemy.Integer,
                        comment='Total number of CPUs at start')
        log_columns.add(name='LOG_START', datatype=sqlalchemy.String(25),
                        comment='log sub-level start time '
                                'YYYY-mm-dd HH:MM:SS.SSS')
        log_columns.add(name='LOG_END', datatype=sqlalchemy.String(25),
                        comment='Log sub-level end time '
                                'YYYY-mm-dd HH:MM:SS.SSS')

        # return columns and ctypes
        self.logdb_cols = log_columns
        return log_columns

    def GET_EPOCH(self, params, header):
        """
        Get the EPOCH in JD from a input header file (instrument specific)
        """
        _ = params, header
        # raise implementation error
        self._not_implemented('GET_EPOCH')

    def COMBINE_FILE_SUFFIX(self, basenames: List[str], suffix: str):

        """
        Get a possible suffix from the basename

        :param basenames: list of strings, the base filenames
        :param suffix: str, the original suffix to add to the base filename

        :return: str, the new filename
        """
        _ = basenames, suffix
        # raise implementation error
        self._not_implemented('COMBINE_FILE_SUFFIX')

    def REJECT_CLEAN(self, reject_item: str) -> str:
        """
        How to clean the reject column / reject list

        :param reject_item: str, the item to reject

        :return: str, the cleaned string
        """
        # remove path
        reject_item = os.path.basename(reject_item)
        # remove .fits
        while reject_item.endswith('.fits'):
            reject_item = reject_item[:-len('.fits')]
        return reject_item

    def REJECTION(self, reject_list: np.ndarray,
                  reject_names: np.ndarray,
                  clean: bool = True) -> Tuple[np.ndarray, List[str]]:
        """
        Reject an array based on a rejection list

        :param reject_list: np.ndarray, the rejection list
        :param reject_names: np.ndarray, the rejection names
        :param clean: bool, whether to clean the rejection list

        :return: np.ndarray, a mask, True where we want to reject
        """
        # storage for clean reject list
        clean_reject_list = []
        # storage for clean reject names
        clean_reject_names = []
        # ---------------------------------------------------------------------
        # we need to clean up the rejection list
        for reject_item in reject_list:
            # skip None's and other things that shouldn't be in this list
            if not isinstance(reject_item, str):
                continue
            # clean (can be different per instrument)
            if clean:
                reject_item = self.REJECT_CLEAN(reject_item)
            # push into clean reject list
            if reject_item not in clean_reject_list:
                clean_reject_list.append(reject_item)
        # ---------------------------------------------------------------------
        # we need to clean up the rejection names
        for reject_name in reject_names:
            # skip None's and other things that shouldn't be in this list
            if not isinstance(reject_name, str):
                reject_name = 'None'
            # clean (can be different per instrument)
            if clean:
                reject_name = self.REJECT_CLEAN(reject_name)
            # push into clean_reject_names
            clean_reject_names.append(reject_name)
        # ---------------------------------------------------------------------
        reject_mask = np.isin(np.array(clean_reject_names),
                              np.array(clean_reject_list))
        # return the reject mask
        return reject_mask, clean_reject_list


    # =========================================================================
    # CROSSMATCHING
    # =========================================================================
    # noinspection SqlDialectInspection
    def PM_TAP_DICT(self, params: Any) -> Dict[str, Dict[str, str]]:
        """
        Once we have an id for a proper motion catalogue we can cross-match
        against this catalogue and get back variables. To do this we have
        to set up a TAP query. These are done per proper motion catalogue and
        stored as a dictionary.

        Each entry should have:

        query: SELECT {ra} as ra, {dec} as dec, {pmra} as pmde,
                      {pmde} as pmde, {plx} as {plx}, epoch as {epoch}
               FROM {cat} WHERE {id}={idnum}
        url: TAP url

        :return:
        """
        # storage
        tap_dict = dict()
        # ---------------------------------------------------------------------
        QUERY1 = ('SELECT TOP 5 {id} as sid, {ra} as ra, {dec} as dec, '
                  '{pmra} as pmra, {pmde} as pmde, {plx} as plx, '
                  '{epoch} as epoch FROM {cat} WHERE {id}=\'{idnum}\'')

        # ---------------------------------------------------------------------
        # Gaia DR3
        # ---------------------------------------------------------------------
        qkargs = dict(ra='ra', dec='dec', pmra='pmra', pmde='pmdec',
                      plx='parallax', epoch='ref_epoch',
                      cat='gaiadr3.gaia_source', id='source_id', idnum='{0}')
        params.set('TAP_GAIA_DR3_URL',
                   'https://gea.esac.esa.int/tap-server/tap')
        tap_dict['Gaia DR3 '] = dict()
        tap_dict['Gaia DR3 ']['QUERY'] = QUERY1.format(**qkargs)
        tap_dict['Gaia DR3 ']['URL'] = str(params['TAP_GAIA_DR3_URL'])
        # ---------------------------------------------------------------------
        # Gaia EDR3
        # ---------------------------------------------------------------------
        qkargs = dict(ra='ra', dec='dec', pmra='pmra', pmde='pmdec',
                      plx='parallax', epoch='ref_epoch',
                      cat='gaiaedr3.gaia_source', id='source_id', idnum='{0}')
        params.set('TAP_GAIA_EDR3_URL',
                   'https://gea.esac.esa.int/tap-server/tap')
        tap_dict['Gaia EDR3 '] = dict()
        tap_dict['Gaia EDR3 ']['QUERY'] = QUERY1.format(**qkargs)
        tap_dict['Gaia EDR3 ']['URL'] = str(params['TAP_GAIA_EDR3_URL'])
        # ---------------------------------------------------------------------
        # Gaia DR2
        # ---------------------------------------------------------------------
        qkargs = dict(ra='ra', dec='dec', pmra='pmra', pmde='pmdec',
                      plx='parallax', epoch='ref_epoch',
                      cat='gaiadr2.gaia_source', id='source_id', idnum='{0}')
        params.set('TAP_GAIA_DR2_URL',
                   'https://gea.esac.esa.int/tap-server/tap')
        tap_dict['Gaia DR2 '] = dict()
        tap_dict['Gaia DR2 ']['QUERY'] = QUERY1.format(**qkargs)
        tap_dict['Gaia DR2 ']['URL'] = str(params['TAP_GAIA_DR2_URL'])
        # ---------------------------------------------------------------------
        # Gaia DR1
        # ---------------------------------------------------------------------
        qkargs = dict(ra='ra', dec='dec', pmra='pmra', pmde='pmdec',
                      plx='parallax', epoch='ref_epoch',
                      cat='gaiadr1.gaia_source', id='source_id', idnum='{0}')
        params.set('TAP_GAIA_DR1_URL',
                   'https://gea.esac.esa.int/tap-server/tap')
        tap_dict['Gaia DR1 '] = dict()
        tap_dict['Gaia DR1 ']['QUERY'] = QUERY1.format(**qkargs)
        tap_dict['Gaia DR1 ']['URL'] = str(params['TAP_GAIA_DR1_URL'])
        # ---------------------------------------------------------------------
        # UCAC 4
        # ---------------------------------------------------------------------
        QUERY2 = ('SELECT TOP 5 {id} as sid, {ra} as ra, {dec} as dec, '
                  '{pmra}*3600*1000 as pmra, {pmde}*3600*1000 as pmde,'
                  '0 as plx, 2000.0 as epoch'
                  ' FROM {cat} WHERE {id}=\'UCAC4-{idnum}\'')
        qkargs = dict(ra='raj2000', dec='dej2000', pmra='pmra', pmde='pmde',
                      cat='ucac4.main', id='ucacid', idnum='{0}')
        params.set('TAP_UCAC4_URL', 'http://dc.zah.uni-heidelberg.de/tap')
        tap_dict['UCAC4 '] = dict()
        tap_dict['UCAC4 ']['QUERY'] = QUERY2.format(**qkargs)
        tap_dict['UCAC4 ']['URL'] = str(params['TAP_UCAC4_URL'])
        # ---------------------------------------------------------------------
        # Hipparcos
        # ---------------------------------------------------------------------
        QUERY3 = ('SELECT TOP 5 {id} as sid, {ra} as ra, {dec} as dec, '
                  '{pmra} as pmra, {pmde} as pmde,'
                  '{plx} as plx, 1991.25 as epoch'
                  ' FROM {cat} WHERE {id}=\'{idnum}\'')
        qkargs = dict(ra='ra', dec='dec', pmra='pm_ra', pmde='pm_de',
                      plx='plx', id='hip', idnum='{0}',
                      cat='public.hipparcos_newreduction')
        params.set('TAP_HIP_URL', 'https://gea.esac.esa.int/tap-server/tap')
        tap_dict['HIP '] = dict()
        tap_dict['HIP ']['QUERY'] = QUERY3.format(**qkargs)
        tap_dict['HIP ']['URL'] = str(params['TAP_HIP_URL'])
        # ---------------------------------------------------------------------
        # return dictionary
        return tap_dict


# =============================================================================
# Functions used by pseudo const
# =============================================================================
def clean_object(rawobjname: str) -> str:
    """
    Clean a 'rawobjname' to allow it to be consistent.

    Thin delegation to :func:`apero.core.drs_astrometrics.clean_object` so
    there is one canonical implementation across the DRS.

    :param rawobjname: str, the raw object name to clean

    :return: str, the cleaned object name
    """
    # delegate to the canonical core implementation
    return drs_astrometrics.clean_object(rawobjname)


def get_sun_altitude(params: Any, header: Any, hdict: Any) -> Tuple[Any, Any]:
    """
    Deal with flagging observations taken in the day and getting the
    twilight and sun altitude keywords

    :param params: ParamDict, parameter dictionary of constants
    :param header: drs_fits.Header or astropy.io.fits.Header, the header to
                   check for objname (if "objname" not set)
    :param hdict: drs_fits.Header the output header dictionary to update with
                  objname (as well as "header" if "objname" not set)

    :return: the updated header/hdict
    """
    # get longitude and latitude from params
    obs_lat = params['OBS.LAT'] * uu.deg
    obs_long = params['OBS.LONG'] * uu.deg
    # get the definitions of civil, nautical and astronomical twilight
    night_def = params['OBS.NIGHT_DEFINITION']
    civ_twil_angle = apero_base.CIVIL_TWILIGHT
    nau_twil_angle = apero_base.NAUTICAL_TWILIGHT
    ast_twil_angle = apero_base.ASTRONOMIAL_TWILIGHT
    # get header keys
    kwmidobstime = params['KW_MID_OBS_TIME'][0]
    kw_night_obs, _, kw_night_obs_comment = params['KW_NIGHT_OBS']
    kw_civ_twil, _, kw_civ_twil_comment = params['KW_CIV_TWIL']
    kw_nau_twil, _, kw_nau_twil_comment = params['KW_NAU_TWIL']
    kw_ast_twil, _, kw_ast_twil_comment = params['KW_AST_TWIL']
    kw_sun_elev, _, kw_sun_elev_comment = params['KW_SUN_ELEV']
    # -------------------------------------------------------------------------
    # get the mid exposure time
    mjdmid = header[kwmidobstime]
    # -------------------------------------------------------------------------
    # calculate the location of the observatory
    location = coord.EarthLocation(lon=obs_long, lat=obs_lat)
    # calculate sun time
    sun_time = Time(mjdmid, format='mjd')
    # get the alt-az angle
    alt_az = coord.AltAz(obstime=sun_time, location=location)
    # get the sun's elevation
    sun_elevation = 90 - coord.get_sun(sun_time).transform_to(alt_az).zen.value
    # calculate the twilight angles
    civ_twil = sun_elevation < civ_twil_angle
    nau_twil = sun_elevation < nau_twil_angle
    ast_twil = sun_elevation < ast_twil_angle
    # -------------------------------------------------------------------------
    # decide on flag for an observation to be a night observation
    if night_def == 'CIVIL':
        night_obs = civ_twil
    elif night_def == 'NAUTICAL':
        night_obs = nau_twil
    elif night_def == 'ASTRONOMICAL':
        night_obs = ast_twil
    else:
        night_obs = civ_twil
    # -------------------------------------------------------------------------
    # push values into header and hdict
    # -------------------------------------------------------------------------
    # night observation
    header[kw_night_obs] = (night_obs, kw_night_obs_comment)
    hdict[kw_night_obs] = (night_obs, kw_night_obs_comment)
    # civil twilight
    header[kw_civ_twil] = (civ_twil, kw_civ_twil_comment)
    hdict[kw_civ_twil] = (civ_twil, kw_civ_twil_comment)
    # nautical twilight
    header[kw_nau_twil] = (nau_twil, kw_nau_twil_comment)
    hdict[kw_nau_twil] = (nau_twil, kw_nau_twil_comment)
    # astronomical twilight
    header[kw_ast_twil] = (ast_twil, kw_ast_twil_comment)
    hdict[kw_ast_twil] = (ast_twil, kw_ast_twil_comment)
    # sun elevation
    header[kw_sun_elev] = (sun_elevation, kw_sun_elev_comment)
    header[kw_sun_elev] = (sun_elevation, kw_sun_elev_comment)
    # -------------------------------------------------------------------------
    # return header and hdict
    return header, hdict

# =============================================================================
# End of code
# =============================================================================