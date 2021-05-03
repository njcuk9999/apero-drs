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
import string
from typing import Any, List, Tuple, Type, Union

from apero.base import base
from apero.core.core import drs_base_classes as base_class
from apero.core.core import drs_misc
from apero.core.core import drs_text
from apero.core import constants
from apero.core.instruments.default import pseudo_const
from apero.core.core import drs_exceptions

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'config.instruments.spirou.pseudo_const'
__INSTRUMENT__ = 'SPIROU'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get Time / TimeDelta
Time, TimeDelta = base.AstropyTime, base.AstropyTimeDelta
# Get Parmeter Dictionary class
ParamDict = constants.ParamDict
# get default Constant class
DefaultConstants = pseudo_const.PseudoConstants
# get error
DrsCodedException = drs_exceptions.DrsCodedException
# get display func
display_func = drs_misc.display_func
# define bad characters for objects (alpha numeric + "_")
BAD_OBJ_CHARS = [' '] + list(string.punctuation.replace('_', ''))

# =============================================================================
# Define Constants class (pseudo constants)
# =============================================================================
class PseudoConstants(DefaultConstants):
    # set class name
    class_name = 'PsuedoConstants'

    def __init__(self, instrument: Union[str, None] = None):
        """
        Pseudo Constants constructor

        :param instrument: str, the drs instrument name
        """
        # set function name
        _ = display_func('__init__', __NAME__, self.class_name)
        # set instrument name
        self.instrument = instrument

    def __getstate__(self) -> dict:
        """
        For when we have to pickle the class
        :return:
        """
        # set function name
        _ = display_func('__getstate__', __NAME__, self.class_name)
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
        _ = display_func('__setstate__', __NAME__, self.class_name)
        # update dict with state
        self.__dict__.update(state)

    def __str__(self) -> str:
        """
        string representation of PseudoConstants
        :return:
        """
        # set function name
        _ = display_func('__str__', __NAME__, self.class_name)
        # return string representation
        return self.__repr__()

    def __repr__(self) -> str:
        """
        string representation of PseudoConstants
        :return:
        """
        # set function name
        _ = display_func('__repr__', __NAME__, self.class_name)
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
        # set module name
        module_name = 'apero.core.instruments.spirou.file_definitions'
        # try to import module
        try:
            return base_class.ImportModule('spirou.file_definitions',
                                           module_name)
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
        # set module name
        module_name = 'apero.core.instruments.spirou.recipe_definitions'
        # try to import module
        try:
            return base_class.ImportModule('spirou.recipe_definitions',
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
    def VALID_RAW_FILES(self) -> List[str]:
        """
        Return the extensions that are valid for raw files

        :return: a list of strings of valid extensions
        """
        # set function name
        _ = display_func('VALID_RAW_FILES', __NAME__, self.class_name)
        # set valid extentions
        valid = ['a.fits', 'c.fits', 'd.fits', 'f.fits', 'o.fits']
        return valid

    def NON_CHECK_DUPLICATE_KEYS(self) -> List[str]:
        """
        Post process do not check these duplicate keys
        """
        # set function name
        _ = display_func('NON_CHECK_DUPLICATE_KEYS', __NAME__,
                         self.class_name)
        # set forbidden keys
        keys = ['SIMPLE', 'EXTEND', 'NEXTEND']
        # return forbiiden keys
        return keys

    def FORBIDDEN_OUT_KEYS(self) -> List[str]:
        """
        Post process primary extension should not have these keys
        """
        # set function name
        _ = display_func('FORBIDDEN_OUT_KEYS', __NAME__, self.class_name)
        # set forbidden keys
        forbidden_keys = ['BITPIX', 'NAXIS', 'NAXIS1', 'NAXIS2']
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
        _ = display_func('FORBIDDEN_COPY_KEYS', __NAME__, self.class_name)
        # set forbidden keys
        forbidden_keys = ['SIMPLE', 'BITPIX', 'NAXIS', 'NAXIS1', 'NAXIS2',
                          'EXTEND', 'COMMENT', 'CRVAL1', 'CRPIX1', 'CDELT1',
                          'CRVAL2', 'CRPIX2', 'CDELT2', 'BSCALE', 'BZERO',
                          'PHOT_IM', 'FRAC_OBJ', 'FRAC_SKY', 'FRAC_BB']
        # return keys
        return forbidden_keys

    def HEADER_FIXES(self, params: ParamDict, recipe: Any, header: Any,
                     hdict: Any, filename: str) -> Any:
        """
        For SPIRou the following keys may or may not be present (older data
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
        _ = display_func('HEADER_FIXES', __NAME__, self.class_name)
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
        header, hdict = get_drs_mode(params, header, hdict,
                                     filename=filename)
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
        _ = display_func('DRS_OBJ_NAME', __NAME__, self.class_name)
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

    def GET_STOKES_FROM_HEADER(self, params: ParamDict, header: Any,
                               wlog: Any = None) -> Tuple[Union[str, None], int]:
        """
        Get the stokes parameter and exposure number from the header

        :param params: ParamDict, the parameter dictionary of constants
        :param header: fits.Header, the fits header to get keys from
        :param wlog: logger for error reporting

        :raises ValueError: if header key incorrect and wlog is None
        :raises DrsLogError: if header key incorrect and wlog is logger
        :return: tuple, 1. The stokes parameter, 2. the exposure number
        """
        # get cmmtseq from key from params
        kw_cmmtseq = params['KW_CMMTSEQ'][0]
        # ---------------------------------------------------------------------
        # deal with no key in header
        if kw_cmmtseq not in header:
            return None, -1
        # ---------------------------------------------------------------------
        # get cmmtseq key
        cmmtseq = header[kw_cmmtseq]
        # key should read as follows:
        #    {STOKE} exposure {exp_num}, sequence N of M
        seqlist = cmmtseq.split()
        # ---------------------------------------------------------------------
        # check length is correct - raise error if incorrect
        if len(seqlist) != 7:
            # generate error message
            emsg = 'CMMTSEQ key incorrect'
            emsg += '\n\tExpected {STOKE} exposure {exp_num}, sequence N of M'
            emsg += '\n\tGot: "{0}"'.format(cmmtseq)
            # log or raise error
            if wlog is not None:
                # wlog error
                wlog(params, 'error', emsg)
                return None, -1
            else:
                raise ValueError(emsg)
        # ---------------------------------------------------------------------
        # get stokes and exposure number
        stokes = seqlist[0]
        # try to get exposure number
        try:
            exp_num = int(seqlist[2].replace(',', ''))
        except Exception as e:
            # generate error message
            emsg = 'CMMTSEQ exp_num incorrect'
            emsg += '\n\tExpected {STOKE} exposure {exp_num}, sequence N of M'
            emsg += '\n\tGot: "{0}"'.format(cmmtseq)
            # log or raise error
            if wlog is not None:
                # wlog error
                wlog(params, 'error', emsg)
                return None, -1
            else:
                raise ValueError(emsg)
        # ---------------------------------------------------------------------
        # return stokes and exposure number
        return stokes, exp_num

    def GET_POLAR_TELLURIC_BANDS(self) -> List[List[float]]:
        """
        Define regions where telluric absorption is high

        :return: list of bands each element is a list of a minimum wavelength
                 and a maximum wavelength of that band
        """
        # storage for bands
        bands = []
        # add bands (as tuples for low wave to high wave
        bands.append([930, 967])
        bands.append([1109, 1167])
        bands.append([1326, 1491])
        bands.append([1782, 1979])
        bands.append([1997, 2027])
        bands.append([2047, 2076])
        # return bands
        return bands

    def GET_LSD_LINE_REGIONS(self) -> List[List[float]]:
        """
        Define regions to select lines in the LSD analysis

        :return: list of regions each element is a list of a minimum wavelength
                 and a maximum wavelength of that band
        """
        # storage for bands
        bands = []
        # add bands (as tuples for low wave to high wave
        bands.append([983.0, 1116.0])
        bands.append([1163.0, 1260.0])
        bands.append([1280.0, 1331.0])
        bands.append([1490.0, 1790.0])
        bands.append([1975.0, 1995.0])
        bands.append([2030.0, 2047.5])
        # return bands
        return bands

    def GET_LSD_ORDER_RANGES(self) -> List[List[float]]:
        """
        Define the valid wavelength ranges for each order in SPIrou.

        :return orders: array of float pairs for wavelength ranges
        """
        # storage for order ranges
        orders = []
        # add ranges as pairs of wavelengths (low wave to high wave)
        orders.append([963.6, 986.0])
        orders.append([972.0, 998.4])
        orders.append([986.3, 1011])
        orders.append([1000.1, 1020])
        orders.append([1015, 1035])
        orders.append([1027.2, 1050])
        orders.append([1042, 1065])
        orders.append([1055, 1078])
        orders.append([1070, 1096])
        orders.append([1084, 1112.8])
        orders.append([1098, 1128])
        orders.append([1113, 1146])
        orders.append([1131, 1162])
        orders.append([1148, 1180])
        orders.append([1166, 1198])
        orders.append([1184, 1216])
        orders.append([1202, 1235])
        orders.append([1222, 1255])
        orders.append([1243, 1275])
        orders.append([1263, 1297])
        orders.append([1284, 1320])
        orders.append([1306, 1342])
        orders.append([1328, 1365])
        orders.append([1352, 1390])
        orders.append([1377, 1415])
        orders.append([1405, 1440])
        orders.append([1429, 1470])
        orders.append([1456, 1497])
        orders.append([1485, 1526])
        orders.append([1515, 1557])
        orders.append([1545, 1590])
        orders.append([1578, 1623])
        orders.append([1609, 1657])
        orders.append([1645, 1692])
        orders.append([1681, 1731])
        orders.append([1722, 1770])
        orders.append([1760, 1810])
        orders.append([1800, 1855])
        orders.append([1848, 1900])
        orders.append([1890, 1949])
        orders.append([1939, 1999])
        orders.append([1991, 2050])
        orders.append([2044.5, 2105])
        orders.append([2104, 2162])
        orders.append([2161, 2226])
        orders.append([2225, 2293])
        orders.append([2291, 2362])
        orders.append([2362, 2430])
        orders.append([2440, 2510])
        # return order ranges
        return orders

    # =========================================================================
    # INDEXING SETTINGS
    # =========================================================================
    def INDEX_HEADER_KEYS(self) -> Tuple[List[str], List[Type]]:
        """
        Which header keys should we have in the index database.

        Only keys where you have to read many files to get these should be
        added - if you access file by file do not need header key to be here.

        Note all keys accessed by file_defintions must be in this list at the
        very least!

        Must overwrite for each instrument

        :return:
        """
        # set keyts
        index_keys = dict()
        index_keys['KW_DATE_OBS'] = str
        index_keys['KW_UTC_OBS'] = str
        index_keys['KW_ACQTIME'] = float
        index_keys['KW_TARGET_TYPE'] = str
        index_keys['KW_MID_OBS_TIME'] = float
        index_keys['KW_OBJECTNAME'] = str
        index_keys['KW_OBJNAME'] = str
        index_keys['KW_OBSTYPE'] =str
        index_keys['KW_EXPTIME'] = float
        index_keys['KW_CCAS'] = str
        index_keys['KW_CREF'] = str
        index_keys['KW_CDEN'] = float
        index_keys['KW_CALIBWH'] = str
        index_keys['KW_POLAR_KEY_1'] = str
        index_keys['KW_POLAR_KEY_2'] = str
        index_keys['KW_DPRTYPE'] = str
        index_keys['KW_DRS_MODE'] = str
        index_keys['KW_OUTPUT'] = str
        index_keys['KW_CMPLTEXP'] = int
        index_keys['KW_NEXP'] = int
        index_keys['KW_VERSION'] = str
        index_keys['KW_PPVERSION'] = str
        index_keys['KW_PI_NAME'] = str
        index_keys['KW_PID'] = str
        index_keys['KW_FIBER'] = str
        index_keys['KW_IDENTIFIER'] = str
        # split names and types and add header keys
        keys = list(index_keys.keys())
        ctypes = list(index_keys.values())
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
        keys = ['KW_TARGET_TYPE', 'KW_OBJECTNAME', 'KW_OBSTYPE',
                'KW_CCAS', 'KW_CREF', 'KW_CALIBWH',
                'KW_DPRTYPE', 'KW_OUTPUT', 'KW_DRS_MODE']
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
        _ = display_func('SPLASH', __NAME__, self.class_name)
        # set the logo
        logo = ['',
                '      `-+syyyso:.   -/+oossssso+:-`   `.-:-`  `...------.``                                 ',
                '    `ohmmmmmmmmmdy: +mmmmmmmmmmmmmy- `ydmmmh: sdddmmmmmmddho-                               ',
                '   `ymmmmmdmmmmmmmd./mmmmmmhhhmmmmmm-/mmmmmmo ymmmmmmmmmmmmmmo                              ',
                '   /mmmmm:.-:+ydmm/ :mmmmmy``.smmmmmo.ydmdho` ommmmmhsshmmmmmm.      ```                    ',
                '   ommmmmhs+/-..::  .mmmmmmoshmmmmmd- `.-::-  +mmmmm:  `hmmmmm`  `-/+ooo+:.   .:::.   .:/// ',
                '   .dmmmmmmmmmdyo.   mmmmmmmmmmmddo. oyyyhm/  :mmmmmy+osmmmmms  `osssssssss+` /sss-   :ssss ',
                '    .ohdmmmmmmmmmmo  dmmmmmdo+/:.`   ymmmmm/  .mmmmmmmmmmmmms`  +sss+..-ossso`+sss-   :ssss ',
                '   --.`.:/+sdmmmmmm: ymmmmmh         ymmmmm/   mmmmmmmmmddy-    ssss`   :ssss.osss.   :ssss ',
                '  +mmmhs/-.-smmmmmm- ommmmmm`        hmmmmm/   dmmmmm/sysss+.  `ssss-  `+ssss`osss`   :ssss ',
                ' -mmmmmmmmmmmmmmmms  /mmmmmm.        hmmmmm/   ymmmmm``+sssss/` /sssso+sssss- +sss:` .ossso ',
                ' -sdmmmmmmmmmmmmdo`  -mmmmmm/        hmmmmm:   smmmmm-  -osssss/`-osssssso/.  -sssssosssss+ ',
                '    ./osyhhhyo+-`    .mmmddh/        sddhhy-   /mdddh-    -//::-`  `----.      `.---.``.--. ',
                '']
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

    def FIBER_LOC_TYPES(self, fiber: str) -> str:
        """
        The fiber localisation types to use (i.e. some fiber types should use
        another fiber for localisation e.g. SPIRou A or B --> AB

        :param fiber: str, the input fiber

        :return: str, the fiber to use for input fiber
        """
        # set function name
        _ = display_func('FIBER_LOC_TYPES', __NAME__, self.class_name)
        # check fiber against list
        if fiber in ['AB', 'A', 'B']:
            return 'AB'
        else:
            return 'C'

    def FIBER_WAVE_TYPES(self, fiber: str) -> str:
        """
        The fiber localisation types to use (i.e. some fiber types should use
        another fiber for localisation e.g. SPIRou A or B --> AB

        :param fiber: str, the input fiber

        :return: str, the fiber to use for input fiber
        """
        # set function name
        _ = display_func('FIBER_WAVE_TYPES', __NAME__, self.class_name)
        # check fiber against list
        if fiber in ['AB', 'A', 'B']:
            return 'AB'
        else:
            return 'C'

    def FIBER_DPR_POS(self, dprtype: str, fiber: str) -> str:
        """
        When we have a DPRTYPE figure out what is in the fiber requested

        :param dprtype: str in form fiber1_fiber2 type in each
                        (e.g. DARK, FLAT, FP, HC, OBJ etc)
        :param fiber: str, the fiber requested

        :return:
        """
        # set function name
        _ = display_func('FIBER_DPR_POS', __NAME__, self.class_name)
        # split DPRTYPE
        dprtypes = dprtype.split('_')
        # check fiber type
        if fiber in ['AB', 'A', 'B']:
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
            return 'AB'
        elif dprtype == 'DARK_FLAT':
            return 'C'
        else:
            return None

    def FIBER_LOC_COEFF_EXT(self, coeffs: np.ndarray,
                            fiber: str) -> Tuple[np.ndarray, int]:
        """
        Extract the localisation coefficients based on how they are stored
        for spirou we have either AB,A,B of size 98 orders or C of size 49
        orders. For AB we merge the A and B, for A and B we take alternating
        orders, for C we take all. Note only have AB and C files also affects
        FIBER_LOC_TYPES

        :param coeffs: the input localisation coefficients
        :param fiber: str, the fiber

        :returns: the update coefficients and the number of orders
        """
        # set function name
        _ = display_func('FIBER_LOC_COEFF_EXT', __NAME__, self.class_name)
        # for AB we need to merge the A and B components
        if fiber == 'AB':
            # get shape
            nbo, ncoeff = coeffs.shape
            # set up acc
            acc = np.zeros([int(nbo / 2), ncoeff])
            # get sum of 0 to step pixels
            cosum = np.array(coeffs[0:nbo:2, :])
            # add the sum of 1 to step
            cosum = cosum + coeffs[1:nbo:2, :]
            # overwrite values into coeffs array
            acc[0:int(nbo / 2), :] = (1 / 2) * cosum
        # for A we only need the A components
        elif fiber == 'A':
            acc = coeffs[1::2]
            nbo = coeffs.shape[0] // 2
        # for B we only need the B components
        elif fiber == 'B':
            acc = coeffs[:-1:2]
            nbo = coeffs.shape[0] // 2
        # for C we take all of them (as there are only the C components)
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
        _ = display_func('FIBER_DATA_TYPE', __NAME__, self.class_name)
        # check fiber type
        if fiber in ['AB', 'A', 'B']:
            return dprtype.split('_')[0]
        else:
            return dprtype.split('_')[1]

    def FIBER_CCF(self) -> Tuple[str, str]:
        """
        Get the science and reference fiber to use in the CCF process

        :return: the science and reference fiber
        """
        # set function name
        _ = display_func('FIBER_CCF', __NAME__, self.class_name)
        # set the fibers and return
        science = 'AB'
        reference = 'C'
        return science, reference

    def FIBER_KINDS(self) -> Tuple[List[str], str]:
        """
        Set the fiber kinds (those to be though as as "science" and those to be
        though as as "reference" fibers.

        :return: list of science fibers and the reference fiber
        """
        # set function name
        _ = display_func('FIBER_KINDS', __NAME__, self.class_name)
        # can be multiple science channels
        science = ['AB', 'A', 'B']
        # can only be one reference
        reference = 'C'
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
        if fiber == 'AB':
            return ['A', 'B']
        else:
            return ['C']

    def INDIVIDUAL_FIBERS(self) -> List[str]:
        """
        List the individual fiber names

        :return: list of strings, the individual fiber names
        """
        # set function name
        _ = display_func('INDIVIDUAL_FIBERS', __NAME__, self.class_name)
        # list the individual fiber names
        return ['A', 'B', 'C']

    # =========================================================================
    # BERV_KEYS
    # =========================================================================
    def BERV_INKEYS(self) -> base_class.ListDict:
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
        _ = display_func('BERV_INKEYS', __NAME__, self.class_name)
        # set up storage
        #     [in_key, out_key, kind, default]
        inputs = base_class.ListDict()
        inputs['gaiaid'] = ['KW_GAIA_ID', 'KW_BERVGAIA_ID', 'header', 'None']
        inputs['objname'] = ['KW_OBJNAME', 'KW_BERVOBJNAME', 'header', 'None']
        inputs['ra'] = ['KW_OBJRA', 'KW_BERVRA', 'header', None]
        inputs['dec'] = ['KW_OBJDEC', 'KW_BERVDEC', 'header', None]
        inputs['epoch'] = ['KW_OBJEQUIN', 'KW_BERVEPOCH', 'header', None]
        inputs['pmra'] = ['KW_OBJRAPM', 'KW_BERVPMRA', 'header', None]
        inputs['pmde'] = ['KW_OBJDECPM', 'KW_BERVPMDE', 'header', None]
        inputs['lat'] = ['OBS_LAT', 'KW_BERVLAT', 'const', None]
        inputs['long'] = ['OBS_LONG', 'KW_BERVLONG', 'const', None]
        inputs['alt'] = ['OBS_ALT', 'KW_BERVALT', 'const', None]
        inputs['plx'] = ['KW_PLX', 'KW_BERVPLX', 'header', 0.0]
        inputs['rv'] = ['KW_RV', 'KW_BERVRV', 'header', np.nan]

        inputs['inputsource'] = ['KW_BERV_POS_SOURCE', 'KW_BERV_POS_SOURCE',
                                 'header', 'None']
        inputs['gmag'] = ['KW_BERV_GAIA_GMAG', 'KW_BERV_GAIA_GMAG', 'header',
                          np.nan]
        inputs['bpmag'] = ['KW_BERV_GAIA_BPMAG', 'KW_BERV_GAIA_BPMAG', 'header',
                           np.nan]
        inputs['rpmag'] = ['KW_BERV_GAIA_RPMAG', 'KW_BERV_GAIA_RPMAG', 'header',
                           np.nan]
        inputs['gaia_mag_lim'] = ['KW_BERV_GAIA_MAGLIM', 'KW_BERV_GAIA_MAGLIM',
                                  'header', np.nan]
        inputs['gaia_plx_lim'] = ['KW_BERV_GAIA_PLXLIM', 'KW_BERV_GAIA_PLXLIM',
                                  'header', np.nan]
        # return inputs
        return inputs

    def BERV_OUTKEYS(self) -> base_class.ListDict:
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
        _ = display_func('BERV_OUTKEYS', __NAME__, self.class_name)
        # set up storage
        #     [in_key, out_key, kind, default]
        outputs = base_class.ListDict()
        outputs['berv'] = ['BERV', 'KW_BERV', 'header', float]
        outputs['bjd'] = ['BJD', 'KW_BJD', 'header', float]
        outputs['bervmax'] = ['BERV_MAX', 'KW_BERVMAX', 'header', float]
        outputs['dberv'] = ['DBERV', 'KW_DBERV', 'header', float]
        outputs['source'] = ['BERV_SOURCE', 'KW_BERVSOURCE', 'header', str]
        outputs['bervest'] = ['BERV_EST', 'KW_BERV_EST', 'header', float]
        outputs['bjdest'] = ['BJD_EST', 'KW_BJD_EST', 'header', float]
        outputs['bervmaxest'] = ['BERV_MAX_EST', 'KW_BERVMAX_EST', 'header',
                                 float]
        outputs['dbervest'] = ['DBERV_EST', 'KW_DBERV_EST', 'header', float]
        # add KW_MID_OBS_TIME as KW_BERV_OBSTIME
        outputs['obs_time'] = ['OBS_TIME', 'KW_BERV_OBSTIME', 'header', float]
        # add KW_MID_OBSTIME_METHOD as KW_BERV_OBSTIME_METHOD
        outputs['obs_time_method'] = ['OBS_TIME_METHOD',
                                      'KW_BERV_OBSTIME_METHOD', 'header', str]
        # return outputs
        return outputs

    # =========================================================================
    # DATABASE SETTINGS
    # =========================================================================
    # noinspection PyPep8Naming
    def INDEX_DB_COLUMNS(self) -> Tuple[List[str], List[type], List[str]]:
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
            - RAW: int, whether raw data has been fixed for the header

        :return: tuple, list of columns (strings), list of types, list of
                 columns (strings) that should be unique
        """
        # set function name
        _ = display_func('INDEX_DB_COLUMNS', __NAME__,
                         self.class_name)
        # get header keys
        hkeys, htypes = self.INDEX_HEADER_KEYS()
        # set columns
        index_columns = dict()
        index_columns['ABSPATH'] = str
        index_columns['OBS_DIR'] = str
        index_columns['FILENAME'] = str
        index_columns['BLOCK_KIND'] = str
        index_columns['LAST_MODIFIED'] = float
        index_columns['RECIPE'] = str
        index_columns['RUNSTRING'] = str
        # split names and types and add header keys
        columns = list(index_columns.keys()) + hkeys
        ctypes = list(index_columns.values()) + htypes
        # add extra columns
        extra_columns = dict()
        extra_columns['USED'] = int
        extra_columns['RAWFIX'] = int
        columns += list(extra_columns.keys())
        ctypes += list(extra_columns.values())
        # define columns that should be unique
        unique_cols = ['ABSPATH']
        # return columns and column types
        return columns, ctypes, unique_cols


# =============================================================================
# Functions used by pseudo const (instrument specific)
# =============================================================================
def clean_obj_name(params: ParamDict = None, header: Any = None,
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
    # deal with no objname --> header mode
    if objname is None:
        return_header = True
        # get keys from params
        kwrawobjname = params['KW_OBJECTNAME'][0]
        kwobjname = params['KW_OBJNAME'][0]
        # deal with output key already in header
        if header is not None:
            if kwobjname in header:
                if not drs_text.null_text(header[kwobjname], ['None', '']):
                    return header, hdict
        # get raw object name
        if kwrawobjname not in header:
            eargs = [kwrawobjname, filename]
            raise DrsCodedException('01-001-00027', 'error', targs=eargs,
                                    func_name=func_name)

        rawobjname = header[kwrawobjname]
    # else just set up blank parameters
    else:
        kwrawobjname, kwobjname = '', ''
        return_header = False
        rawobjname = str(objname)
    # clean object name
    objectname = rawobjname.strip()
    for bad_char in BAD_OBJ_CHARS:
        objectname = objectname.replace(bad_char, '_')
    objectname = objectname.upper()
    # deal with multiple underscores in a row
    while '__' in objectname:
        objectname = objectname.replace('__', '_')
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
    func_name = display_func('get_trg_type', __NAME__)
    # get keys from params
    kwobjname = params['KW_OBJNAME'][0]
    kwobstype = params['KW_OBSTYPE'][0]
    kwtrgtype = params['KW_TARGET_TYPE'][0]
    kwtrgcomment = params['KW_TARGET_TYPE'][2]
    # deal with output key already in header
    if header is not None:
        if kwtrgtype in header:
            if not drs_text.null_text(header[kwtrgtype], ['None', '']):
                return header, hdict
    # get objname
    if kwobjname not in header:
        eargs = [kwobjname, filename]
        raise DrsCodedException('01-001-00027', 'error', targs=eargs,
                                func_name=func_name)

    objname = header[kwobjname]
    # get obstype
    if kwobstype not in header:
        eargs = [kwobstype, filename]
        raise DrsCodedException('01-001-00027', 'error', targs=eargs,
                                func_name=func_name)

    obstype = header[kwobstype]
    # deal with setting value
    if obstype != 'OBJECT':
        trg_type = ''
    elif 'sky' in objname:
        trg_type = 'SKY'
    else:
        trg_type = 'TARGET'
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
            if not drs_text.null_text(header[kwmidobstime], ['None', '']):
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
    endtime = get_header_end_time(params, header, filename)
    # get the time after start of the observation
    timedelta = TimeDelta(exptime * exp_timeunit) / 2.0
    # calculate observation time
    obstime = endtime - timedelta
    # set the method for getting mid obs time
    method = 'mjdend-exp/2'
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


def get_header_end_time(params: ParamDict, header: Any,
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
    func_name = display_func('get_header_end_time', __NAME__)
    # get acqtime
    time_key = params['KW_ACQTIME'][0]
    timefmt = params.instances['KW_ACQTIME'].datatype
    timetype = params.instances['KW_ACQTIME'].dataformat

    # get time key from header
    if time_key not in header:
        eargs = [time_key, filename]
        raise DrsCodedException('01-001-00027', 'error', targs=eargs,
                                func_name=func_name)

    rawtime = header[time_key]
    # ----------------------------------------------------------------------
    # get astropy time
    return Time(timetype(rawtime), format=timefmt)


def get_drs_mode(params: ParamDict, header: Any, hdict: Any,
                 filename: Union[str, None, Path] = None) -> Tuple[Any, Any]:
    """
    Assign the drs mode to the drs (for spirou based on the polar mode)

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
    kw_polar_key_1 = params['KW_POLAR_KEY_1'][0]
    kw_polar_key_2 = params['KW_POLAR_KEY_2'][0]
    kw_obstype = params['KW_OBSTYPE'][0]
    # -------------------------------------------------------------------------
    # set drs_mode
    drs_mode = None
    # deal with no hdict
    if hdict is None:
        hdict = dict()
    # get polar key 1 from the header
    if kw_polar_key_1 not in header:
        drs_mode = 'UNKNOWN'
        polar_key1 = None
    else:
        polar_key1 = header[kw_polar_key_1]
    # get polar key 2 from the header
    if kw_polar_key_2 not in header:
        drs_mode = 'UNKNOWN'
        kw_polar_key_2 = None
    else:
        polar_key2 = header[kw_polar_key_2]
    # -------------------------------------------------------------------------
    # get obstype from the header
    if kw_obstype not in header:
        drs_mode = 'UNKNOWN'
        obstype = None
    else:
        obstype = header[kw_obstype]
    # -------------------------------------------------------------------------
    # get drs mode
    if drs_mode is None and obstype == 'OBJECT':
        # define the drs mode
        if polar_key1 == 'P16' and polar_key2 == 'P16':
            drs_mode = 'SPECTROSCOPY'
        elif polar_key1 == 'P14' and polar_key2 == 'P16':
            drs_mode = 'POLAR'
        elif polar_key1 == 'P2' and polar_key2 == 'P16':
            drs_mode = 'POLAR'
        elif polar_key1 == 'P2' and polar_key2 == 'P4':
            drs_mode = 'POLAR'
        elif polar_key1 == 'P14' and polar_key2 == 'P4':
            drs_mode = 'POLAR'
        else:
            drs_mode = 'UNKNOWN'
    else:
        drs_mode = 'UNKNOWN'
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
    _ = display_func('get_dprtype', __NAME__)
    # set key
    kwdprtype = params['KW_DPRTYPE'][0]
    kwdprcomment = params['KW_DPRTYPE'][1]
    # deal with output key already in header
    if header is not None:
        if kwdprtype in header:
            if not drs_text.null_text(header[kwdprtype], ['None', '']):
                return header, hdict
    # deal with no hdict
    if hdict is None:
        hdict = dict()
    # get the drs files and raw_prefix
    drsfiles = recipe.filemod.get().raw_file.fileset
    raw_prefix = recipe.filemod.get().raw_prefix
    # set up inname
    dprtype = 'Unknown'
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
            else:
                dprtype = drsfile.name
            # we have found file so break
            break
    # update header
    header[kwdprtype] = (dprtype, kwdprcomment)
    hdict[kwdprtype] = (dprtype, kwdprcomment)
    # return header
    return header, hdict

# =============================================================================
# End of code
# =============================================================================
