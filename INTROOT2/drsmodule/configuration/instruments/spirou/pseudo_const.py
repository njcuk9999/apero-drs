#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-18 at 14:44

@author: cook
"""

from drsmodule import constants
from drsmodule.constants.default import pseudo_const


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'recipe_definitions.py'
__INSTRUMENT__ = 'SPIROU'
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

# =============================================================================
# End of code
# =============================================================================
