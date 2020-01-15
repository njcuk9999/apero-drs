#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-18 at 14:44

@author: cook
"""

from apero.core import constants
from apero.core.instruments.default import pseudo_const

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'spirou.pseudo_const'
__INSTRUMENT__ = 'NIRPS'
# get parameters
PARAMS = constants.load(__INSTRUMENT__)
# get default Constant class
DefaultConstants = pseudo_const.PseudoConstants
# -----------------------------------------------------------------------------

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


# =============================================================================
# End of code
# =============================================================================
