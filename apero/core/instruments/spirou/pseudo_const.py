#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-18 at 14:44

@author: cook
"""
import importlib
import numpy as np
from astropy.time import Time, TimeDelta

from apero.core import constants
from apero.core.instruments.default import pseudo_const
from apero.locale import drs_exceptions

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'config.instruments.spirou.pseudo_const'
__INSTRUMENT__ = 'SPIROU'
# get parameters
PARAMS = constants.load(__INSTRUMENT__)
# Get Parmeter Dictionary class
ParamDict = constants.ParamDict
# get default Constant class
DefaultConstants = pseudo_const.PseudoConstants
# get error
ConfigError = drs_exceptions.ConfigError


# =============================================================================
# Define Constants class (pseudo constants)
# =============================================================================
class PseudoConstants(DefaultConstants):
    def __init__(self, instrument=None):
        self.instrument = instrument
        DefaultConstants.__init__(self, instrument)

    # -------------------------------------------------------------------------
    # OVERWRITE PSEUDO-CONSTANTS from constants.default.pseudo_const.py here
    # -------------------------------------------------------------------------

    # =========================================================================
    # File and Recipe definitions
    # =========================================================================
    def FILEMOD(self):
        module_name = 'apero.core.instruments.spirou.file_definitions'
        return importlib.import_module(module_name)

    def RECIPEMOD(self):
        module_name = 'apero.core.instruments.spirou.recipe_definitions'
        return importlib.import_module(module_name)

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
        forbidden_keys = ['SIMPLE', 'BITPIX', 'NAXIS', 'NAXIS1', 'NAXIS2',
                          'EXTEND', 'COMMENT', 'CRVAL1', 'CRPIX1', 'CDELT1',
                          'CRVAL2', 'CRPIX2', 'CDELT2', 'BSCALE', 'BZERO',
                          'PHOT_IM', 'FRAC_OBJ', 'FRAC_SKY', 'FRAC_BB']
        # return keys
        return forbidden_keys

    def HEADER_FIXES(self, **kwargs):
        """
        For SPIRou the following keys may or may not be present (older data
        may need these adding):


        KW_TARGET_TYPE:   if KW_OBSTYPE=="OBJECT"
                                    TRG_TYPE = "SKY" if a sky observation
                                    TRG_TYPE = "TARGET" if not a sky
                          if KW_OBSTYPE!="OBJECT"
                                    TRG_TYPE = ""

        :param header: DrsFitsFile header

        :return: the fixed header
        """
        # get arguments from kwargs
        params = kwargs.get('params')
        recipe = kwargs.get('recipe')
        header = kwargs.get('header')
        # get keys from params
        kwobjname = params['KW_OBNAME']
        kwtrgtype = params['KW_TARGET_TYPE'][0]
        kwmidobstime = params['KW_MID_OBS_TIME'][0]
        kwdprtype = params['KW_DPRTYPE'][0]
        # ------------------------------------------------------------------
        # Deal with cleaning object name
        # ------------------------------------------------------------------
        if kwobjname not in header:
            header = clean_obj_name(params, header)

        # ------------------------------------------------------------------
        # Deal with TRG_TYPE
        # ------------------------------------------------------------------
        if kwtrgtype not in header:
            header = get_trg_type(params, header)

        # ------------------------------------------------------------------
        # Deal with MIDMJD
        # ------------------------------------------------------------------
        if kwmidobstime not in header:
            header = get_mid_obs_time(params, header)

        # ------------------------------------------------------------------
        # Deal with dprtype
        # ------------------------------------------------------------------
        if kwdprtype not in header:
            header = get_dprtype(params, recipe, header)

        # ------------------------------------------------------------------
        # Return header
        # ------------------------------------------------------------------
        return header

    def VALID_RAW_FILES(self):
        valid = ['a.fits', 'c.fits', 'd.fits', 'f.fits', 'o.fits']
        return valid

    # =========================================================================
    # DISPLAY/LOGGING SETTINGS
    # =========================================================================
    def SPLASH(self):
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
    def FIBER_SETTINGS(self, params, fiber):
        """
        Get the fiber settings

        :param params:
        :param fiber:
        :return:
        """
        source = __NAME__ + '.FIBER_SETTINGS()'
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
                emsg = 'Fiber Constant Error. Instrument requires key = {0}'
                ConfigError(emsg.format(key1), level='error')
            # if key exists add it for this fiber
            else:
                fiberparams[key] = params[key1]
                fiberparams.set_source(key, source)
        # return params
        return fiberparams

    def FIBER_LOC_TYPES(self, fiber):
        """
        For localisation only AB and C loco files exist thus need to
        use AB for AB or A or B fibers and use C for the C fiber
        note only having AB and C files also affects FIBER_LOC_COEFF_EXT

        :param fiber:
        :return:
        """
        if fiber in ['AB', 'A', 'B']:
            return 'AB'
        else:
            return 'C'

    def FIBER_WAVE_TYPES(self, fiber):
        """
        For wave only AB and C loco files exist thus need to
        use AB for AB or A or B fibers and use C for the C fiber
        note only having AB and C files

        :param fiber:
        :return:
        """
        if fiber in ['AB', 'A', 'B']:
            return 'AB'
        else:
            return 'C'

    def FIBER_DPR_POS(self, dprtype, fiber):
        """
        When we have a DPRTYPE figure out what is in the fiber requested

        :param dprtype: str in form fiber1_fiber2 type in each
                        (e.g. DARK, FLAT, FP, HC, OBJ etc)
        :param fiber: str, the fiber requested

        :return:
        """
        dprtypes = dprtype.split('_')

        if fiber in ['AB', 'A', 'B']:
            return dprtypes[0]
        else:
            return dprtypes[1]

    def FIBER_LOC_COEFF_EXT(self, coeffs, fiber):
        """
        Extract the localisation coefficients based on how they are stored
        for spirou we have either AB,A,B of size 98 orders or C of size 49
        orders. For AB we merge the A and B, for A and B we take alternating
        orders, for C we take all. Note only have AB and C files also affects
        FIBER_LOC_TYPES

        :param coeffs:
        :param fiber:
        :return:
        """

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
        if fiber in ['AB', 'A', 'B']:
            return dprtype.split('_')[0]
        else:
            return dprtype.split('_')[1]

    def FIBER_CCF(self):
        science = 'AB'
        reference = 'C'
        return science, reference

    def FIBER_KINDS(self):
        # can be multiple science channels
        science = ['AB', 'A', 'B']
        # can only be one reference
        reference = 'C'
        # return science and reference fiber(s)
        return science, reference

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
        #
        #    Must include ra and dec
        inputs = dict()
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

    def BERV_OUTKEYS(self):

        # FORMAT:   [in_key, out_key, kind, dtype]
        #
        #    Where 'in_key' is the header key or param key to use
        #    Where 'out_key' is the output header key to save to
        #    Where 'kind' is 'header' or 'const'
        #    Where dtype is the expected data type
        outputs = dict()
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
        outputs['obs_time'] = ['OBS_TIME', 'KW_BERV_OBSTIME', 'header', float]
        outputs['obs_time_method'] = ['OBS_TIME_METHOD',
                                      'KW_BERV_OBSTIME_METHOD', 'header', str]
        # return outputs
        return outputs


# =============================================================================
# Functions used by pseudo const (instrument specific)
# =============================================================================
def clean_obj_name(params, header):
    # get keys from params
    kwrawobjname = params['KW_OBJECTNAME'][0]
    kwobjname = params['KW_OBJNAME'][0]
    # get raw object name
    rawobjname = header[kwrawobjname]
    # let clean it
    objname = rawobjname.strip()
    objname = objname.replace(' ', '_')
    # add it to the header with new keyword
    header[kwobjname] = objname
    # return header
    return header


def get_trg_type(params, header):
    # get keys from params
    kwobjname = params['KW_OBJNAME'][0]
    kwobstype = params['KW_OBSTYPE'][0]
    kwtrgtype = params['KW_TARGET_TYPE'][0]
    kwtrgcomment = params['KW_TARGET_TYPE'][2]
    # get objname and obstype
    objname = header[kwobjname]
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
    # return header
    return header


def get_mid_obs_time(params, header):
    func_name = __NAME__ + '.get_mid_obs_time()'
    kwmidobstime = params['KW_MID_OBS_TIME'][0]
    kwmidcomment = params['KW_MID_OBS_TIME'][2]
    kwmidmethod = params['KW_BERV_OBSTIME_METHOD'][0]
    methodcomment = params['KW_BERV_OBSTIME_METHOD'][2]

    timefmt = params.instances['KW_MID_OBS_TIME'].datatype
    timetype = params.instances['KW_MID_OBS_TIME'].dataformat
    exp_timekey = params['KW_EXPTIME'][0]
    exp_timeunit = params.instances['KW_EXPTIME'].unit
    exptime = timetype(header[exp_timekey])
    # -------------------------------------------------------------------
    # get header time
    endtime = get_header_end_time(params, header)
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
    elif timefmt == 'mjd':
        header[kwmidobstime] = (float(obstime.mjd), kwmidcomment)
    elif timefmt == 'jd':
        header[kwmidobstime] = (float(obstime.jd), kwmidcomment)
    elif timefmt == 'iso' or timefmt == 'human':
        header[kwmidobstime] = (obstime.iso, kwmidcomment)
    elif timefmt == 'unix':
        header[kwmidobstime] = (float(obstime.unix), kwmidcomment)
    elif timefmt == 'decimalyear':
        header[kwmidobstime] = (float(obstime.decimalyear), kwmidcomment)
    # -------------------------------------------------------------------
    # add method
    header[kwmidmethod] = (method, methodcomment)
    # return the header
    return header


def get_header_end_time(params, header):
    """
    Get acquisition time from header

    :param params:
    :param hdr:
    :param out_fmt:
    :param func: str, input function name
    :param name:

    :type params: ParamDict
    :type hdr: Header
    :type out_fmt: str

    :return:
    """
    # ----------------------------------------------------------------------
    # get acqtime
    time_key = params['KW_MJDEND'][0]
    timefmt = params.instances['KW_MJDEND'].datatype
    timetype = params.instances['KW_MJDEND'].dataformat
    rawtime = header[time_key]
    # ----------------------------------------------------------------------
    # get astropy time
    return Time(timetype(rawtime), format=timefmt)


def get_dprtype(params, recipe, header):
    # set key
    kwdprtype = params['KW_DPRTYPE'][0]
    kwdprcomment = params['KW_DPRTYPE'][1]
    # get the drs files and raw_prefix



    drsfiles = recipe.filemod.raw_file.fileset
    raw_prefix = recipe.filemod.raw_prefix
    # set up inname
    dprtype = 'Unknown'
    # loop around drs files
    for drsfile in drsfiles:
        # set recipe
        drsfile.set_recipe(recipe)
        # find out whether file is valid
        valid, _ = drsfile.has_correct_hkeys(header, log=False)
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
    # return header
    return header


# =============================================================================
# End of code
# =============================================================================
