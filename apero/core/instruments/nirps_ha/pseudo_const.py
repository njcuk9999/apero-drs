#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-18 at 14:44

@author: cook
"""
import numpy as np
from pathlib import Path
from typing import Any, List, Optional, Tuple, Union

from apero.base import base
from apero.base import drs_db
from apero.core.core import drs_base_classes as base_class
from apero.core.core import drs_misc
from apero.core.core import drs_text
from apero.core import constants
from apero.core.instruments.default import pseudo_const
from apero.core.core import drs_exceptions

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'config.instruments.nirps_ha.pseudo_const'
__INSTRUMENT__ = 'NIRPS_HA'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get Time / TimeDelta
Time, TimeDelta = base.AstropyTime, base.AstropyTimeDelta
# Get Parmeter Dictionary class
ParamDict = constants.ParamDict
# Get the Database Columns class
DatabaseColumns = drs_db.DatabaseColumns
# get default Constant class
DefaultConstants = pseudo_const.PseudoConstants
# get error
DrsCodedException = drs_exceptions.DrsCodedException
# get display func
display_func = drs_misc.display_func
# null text
NULL_TEXT = ['', 'None', 'Null']


# =============================================================================
# Define Constants class (pseudo constants)
# =============================================================================
class PseudoConstants(pseudo_const.PseudoConstants):
    # set class name
    class_name = 'PsuedoConstants'

    def __init__(self, instrument: Union[str, None] = None):
        """
        Pseudo Constants constructor

        :param instrument: str, the drs instrument name
        """
        # set function name
        # _ = display_func('__init__', __NAME__, self.class_name)
        # set instrument name
        self.instrument = instrument
        # storage of things we don't want to compute twice without need
        self.exclude = ['header_cols', 'index_cols', 'calibration_cols',
                        'telluric_cols', 'logdb_cols', 'objdb_cols',
                        'filemod', 'recipemod']
        self.header_cols: Optional[DatabaseColumns] = None
        self.index_cols: Optional[DatabaseColumns] = None
        self.calibration_cols: Optional[DatabaseColumns] = None
        self.telluric_cols: Optional[DatabaseColumns] = None
        self.logdb_cols: Optional[DatabaseColumns] = None
        self.objdb_cols: Optional[DatabaseColumns] = None
        self.filemod: Optional[base_class.ImportModule] = None
        self.recipemod: Optional[base_class.ImportModule] = None

    def __getstate__(self) -> dict:
        """
        For when we have to pickle the class
        :return:
        """
        # set function name
        # _ = display_func('__getstate__', __NAME__, self.class_name)
        # need a dictionary for pickle
        state = dict()
        for key, item in self.__dict__.items():
            if key not in self.exclude:
                state[key] = item
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
        # reset excluded values to None
        for item in self.exclude:
            setattr(self, item, None)

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

    # -------------------------------------------------------------------------
    # OVERWRITE PSEUDO-CONSTANTS from constants.default.pseudo_const.py here
    # -------------------------------------------------------------------------

    # =========================================================================
    # File and Recipe definitions
    # =========================================================================
    def FILEMOD(self) -> base_class.ImportModule:
        """
        The import for the file definitions
        :return: file_definitions
        """
        # set function name
        func_name = display_func('FILEMOD', __NAME__, self.class_name)
        # deal with already having this defined
        if self.filemod is not None:
            return self.filemod
        # set module name
        module_name = 'apero.core.instruments.nirps_ha.file_definitions'
        # try to import module
        try:
            self.filemod = base_class.ImportModule('nirps_ha.file_definitions',
                                                   module_name)
            return self.filemod
        except Exception as e:
            # raise coded exception
            eargs = [module_name, 'system', func_name, type(e), str(e), '']
            ekwargs = dict(codeid='00-000-00003', level='error',
                           targs=eargs, func_name=func_name)
            raise drs_exceptions.DrsCodedException(**ekwargs)

    def RECIPEMOD(self) -> base_class.ImportModule:
        """
        The import for the recipe defintions

        :return: file_definitions
        """
        # set function name
        func_name = display_func('RECIPEMOD', __NAME__, self.class_name)
        # deal with already having this defined
        if self.recipemod is not None:
            return self.recipemod
        # set module name
        module_name = 'apero.core.instruments.nirps_ha.recipe_definitions'
        # try to import module
        try:
            strmod = 'nirps_ha.recipe_definitions'
            self.recipemod = base_class.ImportModule(strmod, module_name)
            return self.recipemod
        except Exception as e:
            # raise coded exception
            eargs = [module_name, 'system', func_name, type(e), str(e), '']
            ekwargs = dict(codeid='00-000-00003', level='error',
                           targs=eargs, func_name=func_name)
            raise drs_exceptions.DrsCodedException(**ekwargs)

    # =========================================================================
    # HEADER SETTINGS
    # =========================================================================
    def VALID_RAW_FILES(self) -> List[str]:
        """
        Return the extensions that are valid for raw files

        :return: a list of strings of valid extensions
        """
        # set function name
        # _ = display_func('VALID_RAW_FILES', __NAME__, self.class_name)
        # set valid extentions
        valid = ['.fits']
        return valid

    def NON_CHECK_DUPLICATE_KEYS(self) -> List[str]:
        """
        Post process do not check these duplicate keys
        """
        # set function name
        # _ = display_func('NON_CHECK_DUPLICATE_KEYS', __NAME__,
        #                  self.class_name)
        # set forbidden keys
        keys = ['SIMPLE', 'EXTEND', 'NEXTEND']
        # return forbiiden keys
        return keys

    def FORBIDDEN_OUT_KEYS(self) -> List[str]:
        """
        Post process primary extension should not have these keys
        """
        # set function name
        # _ = display_func('FORBIDDEN_OUT_KEYS', __NAME__, self.class_name)
        # set forbidden keys
        forbidden_keys = ['BITPIX', 'NAXIS', 'NAXIS1', 'NAXIS2', 'XTENSION']
        # return forbiiden keys
        return forbidden_keys

    # noinspection PyPep8Naming
    def FORBIDDEN_COPY_KEYS(self) -> List[str]:
        """
        Defines the keys in a HEADER file not to copy when copying over all
        HEADER keys to a new fits file

        :return forbidden_keys: list of strings, the keys in a HEADER file not
                                to copy from and old fits file
        """
        # set function name
        # _ = display_func('FORBIDDEN_COPY_KEYS', __NAME__, self.class_name)
        # set forbidden keys
        forbidden_keys = ['SIMPLE', 'BITPIX', 'NAXIS', 'NAXIS1', 'NAXIS2',
                          'EXTEND', 'COMMENT', 'CRVAL1', 'CRPIX1', 'CDELT1',
                          'CRVAL2', 'CRPIX2', 'CDELT2', 'BSCALE', 'BZERO',
                          'PHOT_IM', 'FRAC_OBJ', 'FRAC_SKY', 'FRAC_BB',
                          'NEXTEND', '', 'HISTORY', 'XTENSION']
        # return keys
        return forbidden_keys

    def HEADER_FIXES(self, params: ParamDict, recipe: Any, header: Any,
                     hdict: Any, filename: str) -> Any:
        """
        For NIRPS_HA the following keys may or may not be present (older data
        may need these adding):

        KW_TARGET_TYPE:   if KW_OBSTYPE=="OBJECT"
                                    TRG_TYPE = "SKY" if a sky observation
                                    TRG_TYPE = "TARGET" if not a sky
                          if KW_OBSTYPE!="OBJECT"
                                    TRG_TYPE = ""

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
        # _ = display_func('HEADER_FIXES', __NAME__, self.class_name)
        # ------------------------------------------------------------------
        # Deal with cleaning object name
        # ------------------------------------------------------------------
        header, hdict = clean_obj_name(params, header, hdict, filename=filename)
        # ------------------------------------------------------------------
        # Deal with TRG_TYPE
        # ------------------------------------------------------------------
        header, hdict = get_trg_type(params, header, hdict, filename=filename)
        # ------------------------------------------------------------------
        # Deal with MIDMJD
        # ------------------------------------------------------------------
        header, hdict = get_mid_obs_time(params, header, hdict,
                                         filename=filename)
        # ------------------------------------------------------------------
        # Deal with drs mode
        # ------------------------------------------------------------------
        header, hdict = get_drs_mode(params, header, hdict)
        # ------------------------------------------------------------------
        # Deal with dprtype
        # ------------------------------------------------------------------
        header, hdict = get_dprtype(params, recipe, header, hdict,
                                    filename=filename)
        # ------------------------------------------------------------------
        # Return header
        # ------------------------------------------------------------------
        return header, hdict

    def DRS_OBJ_NAME(self, objname: str) -> str:
        """
        Clean and standardize an object name
        i.e. make upper case and remove white spaces

        :param objname: str, input object name
        :return:
        """
        # set function name
        # _ = display_func('DRS_OBJ_NAME', __NAME__, self.class_name)
        # clean object name
        return clean_obj_name(objname=objname)

    def DRS_DPRTYPE(self, params: ParamDict, recipe: Any, header: Any,
                    filename: Union[Path, str]) -> str:
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
        # get correct header
        header, _ = get_dprtype(params, recipe, header, None, filename)
        # return dprtype
        return str(header[params['KW_DPRTYPE'][0]])

    def DRS_MIDMJD(self, params: ParamDict, header: Any,
                   filename: Union[Path, str]) -> float:
        """
        Get the midmjd for a specific header

        :param params: ParamDict, the parameter dictionary of constants
        :param header: fits.Header or drs_fits.Header - the header with
                       header keys to id file
        :param filename: str, the filename name header belongs to (for error
                         logging)

        :return: float the
        """

        header, _ = get_mid_obs_time(params, header, None, filename)
        return float(header[params['KW_MID_OBS_TIME']])

    def FRAME_TIME(self, params: ParamDict, header: Any):
        """
        Get the frame time (either from header or constants depending on
        instrument)

        :param params: ParamDict, the parameter dictionary of constants
        :param header: fits.Header or drs_fits.Header - the header with
                       header keys to id file
        :return: float the frame time in seconds
        """
        return float(params['IMAGE_FRAME_TIME'])

    def SATURATION(self, params: ParamDict, header: Any):
        """
        Get the saturation (either from header or constants depending on
        instrument)

        :param params: ParamDict, the parameter dictionary of constants
        :param header: fits.Header or drs_fits.Header - the header with
                       header keys to id file
        :return: float the frame time in seconds
        """
        return float(params['IMAGE_SATURATION'])

    # =========================================================================
    # INDEXING SETTINGS
    # =========================================================================
    def INDEX_HEADER_COLS(self) -> DatabaseColumns:
        """
        Which header keys should we have in the index database.

        Only keys where you have to read many files to get these should be
        added - if you access file by file do not need header key to be here.

        Note all keys accessed by file_defintions must be in this list at the
        very least!

        Must overwrite for each instrument

        :return:
        """
        # check for pre-existing values
        if self.header_cols is not None:
            return self.header_cols
        # set keyts
        header_cols = DatabaseColumns()
        header_cols.add(name='KW_DATE_OBS', datatype='VARCHAR(80)')
        header_cols.add(name='KW_MJDATE', datatype='VARCHAR(80)')
        header_cols.add(name='KW_TARGET_TYPE', datatype='VARCHAR(80)')
        header_cols.add(name='KW_MID_OBS_TIME', datatype='DOUBLE',
                        is_index=True)
        header_cols.add(name='KW_OBJECTNAME', datatype='VARCHAR(80)')
        header_cols.add(name='KW_OBJNAME', datatype='VARCHAR(80)',
                        is_index=True)
        header_cols.add(name='KW_OBSTYPE', datatype='VARCHAR(80)')
        header_cols.add(name='KW_EXPTIME', datatype='DOUBLE')
        header_cols.add(name='KW_INSTRUMENT', datatype='VARCHAR(80)')
        header_cols.add(name='KW_INST_MODE', datatype='VARCHAR(80)')
        header_cols.add(name='KW_RAW_DPRTYPE', datatype='VARCHAR(80)')
        header_cols.add(name='KW_RAW_DPRCATG', datatype='VARCHAR(80)')
        header_cols.add(name='KW_DPRTYPE', datatype='VARCHAR(80)',
                        is_index=True)
        header_cols.add(name='KW_DRS_MODE', datatype='VARCHAR(80)')
        header_cols.add(name='KW_OUTPUT', datatype='VARCHAR(80)',
                        is_index=True)
        header_cols.add(name='KW_CMPLTEXP', datatype='VARCHAR(80)')
        header_cols.add(name='KW_NEXP', datatype='VARCHAR(80)')
        header_cols.add(name='KW_VERSION', datatype='VARCHAR(80)')
        header_cols.add(name='KW_PPVERSION', datatype='VARCHAR(80)')
        header_cols.add(name='KW_DRS_DATE_NOW', datatype='VARCHAR(80)')
        header_cols.add(name='KW_PI_NAME', datatype='VARCHAR(80)')
        header_cols.add(name='KW_PID', datatype='VARCHAR(80)',
                        is_index=True)
        header_cols.add(name='KW_FIBER', datatype='VARCHAR(80)')
        header_cols.add(name='KW_IDENTIFIER', datatype='VARCHAR(80)',
                        is_index=True)
        # check that filedef keys are present
        for fkey in self.FILEDEF_HEADER_KEYS():
            if fkey not in header_cols.names:
                emsg = __NAME__ + '.INDEX_HEADER_COLS() missing key "{0}"'
                raise AttributeError(emsg.format(fkey))
        # return index header keys
        self.header_cols = header_cols
        return header_cols

    def FILEDEF_HEADER_KEYS(self) -> List[str]:
        """
        Define the keys allowed to be used in file definitions

        :return: list of keys
        """
        keys = ['KW_TARGET_TYPE', 'KW_OBJECTNAME', 'KW_OBSTYPE',
                'KW_RAW_DPRTYPE', 'KW_RAW_DPRCATG', 'KW_INSTRUMENT',
                'KW_INST_MODE', 'KW_DPRTYPE', 'KW_OUTPUT']
        return keys

    # =========================================================================
    # DISPLAY/LOGGING SETTINGS
    # =========================================================================
    def SPLASH(self) -> List[str]:
        """
        The splash image for the instrument
        :return:
        """
        # set function name
        # _ = display_func('SPLASH', __NAME__, self.class_name)
        # set the logo
        logo = ["                                                                                                    ",
                "    %%,                *##*      *##(      *#####(/*,           (######(/,            *#&&&&,  ,    ",
                "    **#%               /**/      /**/      /********/(&%        /********/(       /#/*******(&%     ",
                "    ***/##             /***      /**/      /***,    ****&/      /***,    ****&*   ,(****     ,***,  ",
                "    **,,,*##           /,,*      /,,*      /*,*       *,*(      /,,*,      *,*/   */,,/,            ",
                "    *,,,*,,/&,         /,,*      /,,*      /*,*,      *,,*      /***,     ,****    ***#(            ",
                "    ***/  ***/&,       /***      /***      /***,     /***(      /***,     /***(     ****#&(,        ",
                "    /**/    ***(&      /**/      /***,     (/**#(#%%**///,      (///%##%#*////        */////(%(,    ",
                "    (///      ///(%    (///      (///,     (//////////,         ((/((((((((,              */(((((   ",
                "    ((((       ,(((((, ((((      ((((,     ((((,*(((*           ((((,                        ,###*  ",
                "    ####         ,(##(((###     ,(###,     (###*  (##/          (###/                         (%%#/ ",
                "    ####,          ,#%%%%%#     ,(%%%,     (%%%*   ,%%#*        #%%%/            ,#%%#        #%%#, ",
                "    #%%%,             %%%%%     ,(%%%*     (%%%*     #%%/,      #%%%/             ,%%%/,    (%%%%*  ",
                "    %%%%,               %%%,    ,(%%%*     (%%%*      (%%%*     #%%%/               (%%%%%%%%%%/*   ",
                "                          (,       ,         ,           ,,,      ,,                   *(((/,       ",
                "                                                                                                    "]
        return logo

    # =========================================================================
    # FIBER SETTINGS
    # =========================================================================
    def FIBER_SETTINGS(self, params: ParamDict, fiber: str) -> ParamDict:
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
        # list fiber keys
        keys = ['FIBER_FIRST_ORDER_JUMP', 'FIBER_MAX_NUM_ORDERS',
                'FIBER_SET_NUM_FIBERS']
        # set up new param dict
        fiberparams = ParamDict()
        # loop around all fiber keys and add to params
        for key in keys:
            # get fiber key
            key1 = '{0}_{1}'.format(key, fiber)
            # deal with key not existing
            if key1 not in params:
                eargs = [key1]
                raise DrsCodedException('00-001-00052', 'error', targs=eargs,
                                        func_name=func_name)
            # if key exists add it for this fiber
            else:
                fiberparams[key] = params[key1]
                fiberparams.set_source(key, func_name)
        # return params
        return fiberparams

    def FIBER_LOCALISATION(self, fiber) -> List[str]:
        """
        Return which fibers to calculate localisation for

        :param fiber: str, fiber name

        :return: list of strings, the fibers to find localisation for
        """
        return fiber

    def FIBER_DILATE(self, fiber: str) -> bool:
        """
        whether we are dilate the imagine due to fiber configuration this should
        only be used when we want a combined localisation solution
        i.e. AB from A and B
        for NIRPS this is False

        :param fiber: str, the fiber name
        :return: bool, True if we should dilate, False otherwise
        """
        _ = fiber
        return False

    def FIBER_DOUBLETS(self, fiber: str) -> bool:
        """
        whether we have orders coming in doublets (i.e. SPIROUs AB --> A + B)

        Not used for NIRPS

        :param fiber: str, the fiber name
        :return: bool, True if we have fiber 'doublets', False otherwise
        """
        _ = fiber
        return False

    def FIBER_DOUBLET_PARITY(self, fiber: str) -> Union[int, None]:
        """
        Give the doublet fibers parity - all other fibers should not use this
        function - not used for NIRPS

        :param fiber: str, the fiber name
        :return: int or None, either +/-1 (for fiber A/B) or None)
        """
        _ = fiber
        return None

    def FIBER_LOC_TYPES(self, fiber: str) -> str:
        """
        The fiber localisation types to use (i.e. some fiber types should use
        another fiber for localisation e.g. SPIRou A or B --> AB

        :param fiber: str, the input fiber

        :return: str, the fiber to use for input fiber
        """
        # set function name
        # _ = display_func('FIBER_LOC_TYPES', __NAME__, self.class_name)
        # check fiber against list
        if fiber in ['A']:
            return 'A'
        else:
            return 'B'

    def FIBER_WAVE_TYPES(self, fiber: str) -> str:
        """
        The fiber localisation types to use (i.e. some fiber types should use
        another fiber for localisation e.g. SPIRou A or B --> AB

        :param fiber: str, the input fiber

        :return: str, the fiber to use for input fiber
        """
        # set function name
        # _ = display_func('FIBER_WAVE_TYPES', __NAME__, self.class_name)
        # check fiber against list
        if fiber in ['A']:
            return 'A'
        else:
            return 'B'

    def FIBER_DPR_POS(self, dprtype: str, fiber: str) -> str:
        """
        When we have a DPRTYPE figure out what is in the fiber requested

        :param dprtype: str in form fiber1_fiber2 type in each
                        (e.g. DARK, FLAT, FP, HC, OBJ etc)
        :param fiber: str, the fiber requested

        :return:
        """
        # set function name
        # _ = display_func('FIBER_DPR_POS', __NAME__, self.class_name)
        # split DPRTYPE
        dprtypes = dprtype.split('_')
        # check fiber type
        if fiber in ['A']:
            return dprtypes[0]
        else:
            return dprtypes[1]

    def FIBER_DPRTYPE(self, dprtype: str) -> Union[str, None]:
        """
        Input DPRTYPE tells you which fiber we are correcting for

        :param dprtype: str, the dprtype (probably either FLAT_DARK or DARK_FLAT
        :return: str, the fiber
        """
        # identify fiber type based on data type
        if dprtype == 'FLAT_DARK':
            return 'A'
        elif dprtype == 'DARK_FLAT':
            return 'B'
        else:
            return None

    def FIBER_LOC_COEFF_EXT(self, coeffs: np.ndarray,
                            fiber: str) -> Tuple[np.ndarray, int]:
        """
        Extract the localisation coefficients based on how they are stored
        for nirps we have either A or B of size 49
        orders.

        :param coeffs: the input localisation coefficients
        :param fiber: str, the fiber

        :returns: the update coefficients and the number of orders
        """
        # set function name
        # _ = display_func('FIBER_LOC_COEFF_EXT', __NAME__, self.class_name)
        # for A we take all of them (as there are only the A components)
        if fiber == 'A':
            acc = coeffs
            nbo = coeffs.shape[0]
        # for B we take all of them (as there are only the B components)
        else:
            acc = coeffs
            nbo = coeffs.shape[0]

        return acc, nbo

    def FIBER_DATA_TYPE(self, dprtype, fiber):
        """
        Return the data type from a DPRTYPE

        i.e. for OBJ_FP   fiber = 'A'  --> 'OBJ'
             for OBJ_FP   fiber = 'C'  --> 'FP'

        :param dprtype: str, the DPRTYPE (data type {AB}_{C})
        :param fiber: str, the current fiber (i.e. AB, A, B or C)

        :return:
        """
        # set function name
        # _ = display_func('FIBER_DATA_TYPE', __NAME__, self.class_name)
        # check fiber type
        if fiber in ['A']:
            return dprtype.split('_')[0]
        else:
            return dprtype.split('_')[1]

    def FIBER_CCF(self) -> Tuple[str, str]:
        """
        Get the science and reference fiber to use in the CCF process

        :return: the science and reference fiber
        """
        # set function name
        # _ = display_func('FIBER_CCF', __NAME__, self.class_name)
        # set the fibers and return
        science = 'A'
        reference = 'B'
        return science, reference

    def FIBER_KINDS(self) -> Tuple[List[str], str]:
        """
        Set the fiber kinds (those to be though as as "science" and those to be
        though as as "reference" fibers.

        :return: list of science fibers and the reference fiber
        """
        # set function name
        # _ = display_func('FIBER_KINDS', __NAME__, self.class_name)
        # can be multiple science channels
        science = ['A']
        # can only be one reference
        reference = 'B'
        # return science and reference fiber(s)
        return science, reference

    def FIBER_LOC(self, fiber: str) -> List[str]:
        """
        Set the localisation fibers
        AB --> A, B
        C --> C

        :param fiber:
        :return:
        """
        if fiber == 'A':
            return ['A']
        else:
            return ['B']

    def INDIVIDUAL_FIBERS(self) -> List[str]:
        """
        List the individual fiber names

        :return: list of strings, the individual fiber names
        """
        # set function name
        # _ = display_func('INDIVIDUAL_FIBERS', __NAME__, self.class_name)
        # list the individual fiber names
        return ['A', 'B']

    # =========================================================================
    # DATABASE SETTINGS
    # =========================================================================
    # noinspection PyPep8Naming
    def INDEX_DB_COLUMNS(self) -> DatabaseColumns:
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
            - {HKEYS}: see INDEX_HEADER_COLS()
            - USED: int, whether entry should be used or ignored
            - RAW: int, whether raw data has been fixed for the header

        :return: list of database columns
        """
        # set function name
        # _ = display_func('INDEX_DB_COLUMNS', __NAME__, self.class_name)
        # check for pre-existing values
        if self.index_cols is not None:
            return self.index_cols
        # column definitions
        index_cols = DatabaseColumns()
        index_cols.add(name='ABSPATH', datatype='TEXT', is_unique=True)
        index_cols.add(name='OBS_DIR', datatype='VARCHAR(200)', is_index=True)
        index_cols.add(name='FILENAME', is_index=True, datatype='VARCHAR(200)')
        index_cols.add(name='BLOCK_KIND', is_index=True, datatype='VARCHAR(20)')
        index_cols.add(name='LAST_MODIFIED', datatype='DOUBLE')
        index_cols.add(name='RECIPE', datatype='VARCHAR(200)')
        index_cols.add(name='RUNSTRING', datatype='TEXT')
        index_cols.add(name='INFILES', datatype='TEXT')
        # get header keys
        header_columns = self.INDEX_HEADER_COLS()
        # add header columns to index columns
        index_cols += header_columns
        # add extra columns
        index_cols.add(name='USED', datatype='INT')
        index_cols.add(name='RAWFIX', datatype='INT')
        # manage index groups
        index_cols.index_groups.append(['BLOCK_KIND', 'OBS_DIR', 'USED'])
        index_cols.index_groups.append(['OBS_DIR', 'BLOCK_KIND'])
        # return columns and column types
        self.index_cols = index_cols
        return index_cols

    def GET_EPOCH(self, params, header) -> float:
        """
        Get the EPOCH in JD from a input header file (instrument specific)
        """
        # spirou stores the equinox in decimal years
        key = params['KW_OBJEQUIN'][0]
        time_fmt = params.instances['KW_OBJEQUIN'].unit
        # get value from header
        value = header[key]
        # get time
        epoch = Time(value, format=time_fmt)
        # return epoch in JD
        return epoch.jd


# =============================================================================
# Functions used by pseudo const (instrument specific)
# =============================================================================
def clean_obj_name(params: Union[ParamDict, None] = None,
                   header: Any = None,
                   hdict: Any = None, objname: Union[str, None] = None,
                   filename: Union[None, str, Path] = None
                   ) -> Union[Tuple[Any, Any], str]:
    """
    Clean an object name (remove spaces and make upper case strip white space)

    :param params: ParamDict, parameter dictionary of constants
    :param header: drs_fits.Header or astropy.io.fits.Header, the header to
                   check for objname (if "objname" not set)
    :param hdict: drs_fits.Header the output header dictionary to update with
                  objname (as well as "header" if "objname" not set)
    :param objname: str, the uncleaned object name to clean
    :param filename: str, the filename header came from (for exception)

    :return: if objname set return str, else return the updated header and hdict
    """
    # set function name
    func_name = display_func('clean_obj_name', __NAME__)

    # if we don't have header don't try this part (this happens when we
    #   are just calling using objname)
    if header is not None:
        # return header if we have header given
        return_header = True
        # ---------------------------------------------------------------------
        # check KW_OBJNAME and then KW_OBJECTNAME
        # ---------------------------------------------------------------------
        # if objname is None we need to get it from the header
        if drs_text.null_text(objname, NULL_TEXT):
            # get keys from params
            kwrawobjname = params['KW_OBJECTNAME'][0]
            kwobjname = params['KW_OBJNAME'][0]
            # deal with output key already in header
            if kwobjname in header:
                if not drs_text.null_text(header[kwobjname], NULL_TEXT):
                    return header, hdict
            # get raw object name
            if kwrawobjname not in header:
                eargs = [kwrawobjname, filename]
                raise DrsCodedException('01-001-00027', 'error', targs=eargs,
                                        func_name=func_name)
            else:
                rawobjname = header[kwrawobjname]
        # else just set up blank parameters
        else:
            kwrawobjname, kwobjname = '', ''
            rawobjname = str(objname)
    # else just set up blank parameters
    else:
        kwrawobjname, kwobjname = '', ''
        return_header = False
        rawobjname = str(objname)
    # -------------------------------------------------------------------------
    # if object name is still None - just set it to Null - we can't do anything
    #    else here
    # -------------------------------------------------------------------------
    # finally if we really cannot resolve target name
    if drs_text.null_text(rawobjname, NULL_TEXT):
        objectname = 'Null'
    # else remove spaces - clean object name
    else:
        objectname = pseudo_const.clean_object(rawobjname)
    # -------------------------------------------------------------------------
    # deal with returning header
    if return_header:
        # add it to the header with new keyword
        header[kwobjname] = objectname
        hdict[kwobjname] = objectname
        # return header
        return header, hdict
    else:
        return objectname


def get_trg_type(params: ParamDict, header: Any, hdict: Any,
                 filename: Union[None, str, Path] = None) -> Tuple[Any, Any]:
    """
    Make sure "header" has TRG_TYPE key (and if not try to guess what it should
    be)

    :param params: ParamDict, parameter dictionary of constants
    :param header: drs_fits.Header or astropy.io.fits.Header, the header to
                   check for objname (if "objname" not set)
    :param hdict: drs_fits.Header the output header dictionary to update with
                  objname (as well as "header" if "objname" not set)
    :param filename: str, the filename header came from (for exception)

    :return: the updated header and hdict
    """
    # set function name
    # _ = display_func('get_trg_type', __NAME__)
    # get keys from params
    kwobstype = params['KW_OBSTYPE'][0]
    kwtrgtype = params['KW_TARGET_TYPE'][0]
    kwtrgcomment = params['KW_TARGET_TYPE'][2]
    # get obstype
    if kwobstype not in header:
        eargs = [kwobstype, filename]
        raise drs_exceptions.DrsCodedException('01-001-00027', 'error',
                                               targs=eargs)
    obstype = header[kwobstype]
    # deal with setting value
    if 'SKY' in obstype:
        trg_type = 'SKY'
    elif 'OBJECT' in obstype:
        trg_type = 'TARGET'
    elif 'STAR' in obstype:
        trg_type = 'TARGET'
    else:
        trg_type = ''
    # update header
    header[kwtrgtype] = (trg_type, kwtrgcomment)
    hdict[kwtrgtype] = (trg_type, kwtrgcomment)
    # return header
    return header, hdict


def get_mid_obs_time(params: ParamDict, header: Any, hdict: Any,
                     filename: Union[None, str, Path] = None
                     ) -> Tuple[Any, Any]:
    """
    Make sure "header" has MJDMID (the mid expsoure time)

    :param params: ParamDict, parameter dictionary of constants
    :param header: drs_fits.Header or astropy.io.fits.Header, the header to
                   check for objname (if "objname" not set)
    :param hdict: drs_fits.Header the output header dictionary to update with
                  objname (as well as "header" if "objname" not set)
    :param filename: str, the filename header came from (for exception)

    :return: the updated header and hdict
    """
    # set function name
    func_name = display_func('get_mid_obs_time', __NAME__)
    # get keys from params
    kwmidobstime = params['KW_MID_OBS_TIME'][0]
    kwmidcomment = params['KW_MID_OBS_TIME'][2]
    kwmidmethod = params['KW_MID_OBSTIME_METHOD'][0]
    methodcomment = params['KW_MID_OBSTIME_METHOD'][2]
    timefmt = params.instances['KW_MID_OBS_TIME'].datatype
    timetype = params.instances['KW_MID_OBS_TIME'].dataformat
    exp_timekey = params['KW_EXPTIME'][0]
    exp_timeunit = params.instances['KW_EXPTIME'].unit
    # deal with output key already in header
    if header is not None:
        if kwmidobstime in header:
            if not drs_text.null_text(header[kwmidobstime], NULL_TEXT):
                return header, hdict
    # deal with no hdict
    if hdict is None:
        hdict = dict()
    # get exptime
    if exp_timekey not in header:
        eargs = [exp_timekey, filename]
        raise DrsCodedException('01-001-00027', 'error', targs=eargs,
                                func_name=func_name)
    exptime = timetype(header[exp_timekey])
    # -------------------------------------------------------------------
    # get header time
    starttime = get_header_time(params, header, filename)
    # get the time after start of the observation
    timedelta = TimeDelta(exptime * exp_timeunit) / 2.0
    # calculate observation time
    obstime = starttime + timedelta
    # set the method for getting mid obs time
    method = 'mjdobs+exp/2'
    # -------------------------------------------------------------------
    # return time in requested format
    if timefmt is None:
        header[kwmidobstime] = (obstime.iso, kwmidcomment)
        hdict[kwmidobstime] = (obstime.iso, kwmidcomment)
    elif timefmt == 'mjd':
        header[kwmidobstime] = (float(obstime.mjd), kwmidcomment)
        hdict[kwmidobstime] = (float(obstime.mjd), kwmidcomment)
    elif timefmt == 'jd':
        header[kwmidobstime] = (float(obstime.jd), kwmidcomment)
        hdict[kwmidobstime] = (float(obstime.jd), kwmidcomment)
    elif timefmt == 'iso' or timefmt == 'human':
        header[kwmidobstime] = (obstime.iso, kwmidcomment)
        hdict[kwmidobstime] = (obstime.iso, kwmidcomment)
    elif timefmt == 'unix':
        header[kwmidobstime] = (float(obstime.unix), kwmidcomment)
        hdict[kwmidobstime] = (float(obstime.unix), kwmidcomment)
    elif timefmt == 'decimalyear':
        header[kwmidobstime] = (float(obstime.decimalyear), kwmidcomment)
        hdict[kwmidobstime] = (float(obstime.decimalyear), kwmidcomment)
    # -------------------------------------------------------------------
    # add method
    header[kwmidmethod] = (method, methodcomment)
    hdict[kwmidmethod] = (method, methodcomment)
    # return the header
    return header, hdict


def get_header_time(params: ParamDict, header: Any,
                    filename: Union[str, None, Path] = None) -> Time:
    """
    Get acquisition time from header

    :param params: ParamDict, the parameter dictionary of constants
    :param header: drs_fits.Header or astropy.io.fits.Header - the header to get
                   time from
    :param filename: str, the filename header came from (for exception)

    :return: astropy.Time instance for the header time
    """
    # set function name
    func_name = display_func('get_header_time', __NAME__)
    # get acqtime
    time_key = params['KW_MJDATE'][0]
    timefmt = params.instances['KW_MJDATE'].datatype
    timetype = params.instances['KW_MJDATE'].dataformat

    # get time key from header
    if time_key not in header:
        eargs = [time_key, filename]
        raise DrsCodedException('01-001-00027', 'error', targs=eargs,
                                func_name=func_name)

    rawtime = header[time_key]
    # ----------------------------------------------------------------------
    # get astropy time
    return Time(timetype(rawtime), format=timefmt)


def get_drs_mode(params: ParamDict, header: Any, hdict: Any) -> Tuple[Any, Any]:
    """
    Assign the drs mode to the drs (for nirps_ha this is HA)

    :param params: ParamDict, parameter dictionary of constants
    :param header: drs_fits.Header or astropy.io.fits.Header, the header to
                   check / update
    :param hdict: drs_fits.Header the output header dictionary to update

    # header keys used are ('SBRHB1_P','SBRHB2_P')
        SPECTROSCOPY = ('P16', 'P16')
        POLAR1 = ('P14', 'P16')
        POLAR2 = ('P2', 'P16')
        POLAR3 = ('P2', 'P4')
        POLAR4 = ('P14', 'P4')

    """
    # get drs mode header keyword store
    kw_drs_mode, _, kw_drs_mode_comment = params['KW_DRS_MODE']
    # get drs mode header keyword store
    drs_mode = 'HA'
    # -------------------------------------------------------------------------
    # add header key
    header[kw_drs_mode] = (drs_mode, kw_drs_mode_comment)
    hdict[kw_drs_mode] = (drs_mode, kw_drs_mode_comment)
    # return header
    return header, hdict


def get_dprtype(params: ParamDict, recipe: Any, header: Any, hdict: Any,
                filename: Union[None, str, Path] = None) -> Tuple[Any, Any]:
    """
    Get the DPRTYPE from the header

    :param params: ParamDict, the parameter dictionary of constants
    :param recipe: DrsRecipe instance, the recipe call from
    :param header: drs_fits.Header or astropy.io.fits.Header, the header to
                   check for objname (if "objname" not set)
    :param hdict: drs_fits.Header the output header dictionary to update with
                  objname (as well as "header" if "objname" not set)
    :param filename: str, the filename header came from (for exception)

    :return: the updated header and hdict
    """
    # set function name
    # _ = display_func('get_dprtype', __NAME__)
    # set key
    kwdprtype = params['KW_DPRTYPE'][0]
    kwdprcomment = params['KW_DPRTYPE'][1]
    kwoutput = params['KW_OUTPUT'][0]
    kwoutputcomment = params['KW_OUTPUT'][1]
    # deal with output key already in header
    if header is not None:
        if kwdprtype in header:
            if not drs_text.null_text(header[kwdprtype], NULL_TEXT):
                return header, hdict
    # deal with no hdict
    if hdict is None:
        hdict = dict()
    # get the drs files and raw_prefix
    drsfiles = recipe.filemod.get().raw_file.fileset
    raw_prefix = recipe.filemod.get().raw_prefix
    # set up inname
    dprtype, outtype = 'Unknown', 'Unknown'
    drsfile = None
    # loop around drs files
    for drsfile in drsfiles:
        # set recipe
        drsfile.set_params(params)
        # find out whether file is valid
        valid, _ = drsfile.has_correct_hkeys(header, log=False,
                                             filename=filename)
        # if valid the assign dprtype
        if valid:
            # remove prefix if not None
            if raw_prefix is not None:
                dprtype = drsfile.name.split(raw_prefix)[-1]
                outtype = drsfile.name
            else:
                dprtype = drsfile.name
                outtype = drsfile.name
            # we have found file so break
            break
    # update header with DPRTYPE
    header[kwdprtype] = (dprtype, kwdprcomment)
    hdict[kwdprtype] = (dprtype, kwdprcomment)
    # add drs file type (if drs file was found)
    if drsfile is not None:
        header[kwoutput] = (outtype, kwoutputcomment)
        hdict[kwoutput] = (outtype, kwoutputcomment)
    # return header
    return header, hdict


# =============================================================================
# End of code
# =============================================================================
