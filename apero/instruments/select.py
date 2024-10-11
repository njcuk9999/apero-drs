#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Add instrument definitions here

Created on 2024-09-06 at 14:27

@author: cook
"""
from apero.instruments.default.instrument import Instrument
from apero.instruments.spirou.instrument import Spirou
from apero.instruments.nirps_he.instrument import NirpsHe
from apero.instruments.nirps_ha.instrument import NirpsHa

# New imports here

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

# New instruments here

# =============================================================================
# End of code
# =============================================================================
