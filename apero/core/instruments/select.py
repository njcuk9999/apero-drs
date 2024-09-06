#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Add instrument definitions here

Created on 2024-09-06 at 14:27

@author: cook
"""
from apero.core.instruments.default.instrument import Instrument
from apero.core.instruments.spirou.instrument import Spirou
from apero.core.instruments.nirps_he.instrument import NirpsHe
from apero.core.instruments.nirps_ha.instrument import NirpsHa

# =============================================================================
# Define variables
# =============================================================================
INSTRUMENTS = dict()
# Add the null case
INSTRUMENTS['NONE'] = Instrument
# Add the SPIRou instrument
INSTRUMENTS['SPIROU'] = Spirou
# Add the NIRPS HE instrument
INSTRUMENTS['NIRPS_HE'] = NirpsHe
# Add the NIRPS HA instrument
INSTRUMENTS['NIRPS_HA'] = NirpsHa

# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
