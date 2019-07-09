#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-18 at 14:44

@author: cook
"""
import numpy as np

from terrapipe.core import constants
from terrapipe.core.instruments.default import pseudo_const
from terrapipe.locale import drs_exceptions

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'config.instruments.spirou.pseudo_const'
__INSTRUMENT__ = 'SPIROU'
# get parameters
PARAMS = constants.load(__INSTRUMENT__)
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
    def FIBER_SETTINGS(self, params, fiber=None):
        """
        Get the fiber settings

        :param params:
        :param fiber:
        :return:
        """
        source = __NAME__ + '.FIBER_SETTINGS()'
        # get fiber type
        if fiber is None:
            fiber = params['FIBER']
        # list fiber keys
        keys = ['FIBER_FIRST_ORDER_JUMP', 'FIBER_MAX_NUM_ORDERS',
                'FIBER_SET_NUM_FIBERS']
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
                params[key] = params[key1]
                params.set_source(key, source)
        # return params
        return params


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


    def FIBER_LOC_COEFF_EXT(self, coeffs, fiber):
        """
        Extract the localisation coefficients based on how they are stored
        for spirou we have either AB,A,B of size 98 orders or C of size 49
        orders. For AB we merge the A and B, for A and B we take alternating
        orders, for C we take all. Note only have AB and C files also affects
        FIBER_LOC_TYPES

        :param props:
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


# =============================================================================
# End of code
# =============================================================================
