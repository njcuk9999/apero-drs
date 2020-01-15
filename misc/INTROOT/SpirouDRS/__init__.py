#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__init__.py

startup module controller

Created on 2017-10-11 at 10:43

@author: cook

Version 0.0.1
"""
from . import spirouBACK
from . import spirouDB
from . import spirouConfig
from . import spirouCore
from . import spirouEXTOR
from . import spirouFLAT
from . import spirouImage
from . import spirouLOCOR
from . import spirouPOLAR
from . import spirouRV
from . import spirouStartup
from . import spirouTelluric
from . import spirouTHORCA
from . import spirouUnitTests
from . import spirouTools


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'SpirouDRS'
# These three must also be changed in spirouConfig.spirouConstant to update
#    all sub-packages
__author__ = spirouConfig.Constants.AUTHORS()
__version__ = spirouConfig.Constants.VERSION()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# define imports using asterisk
__all__ = ['spirouBACK',
           'spirouConfig',
           'spirouCore',
           'spirouDB',
           'spirouEXTOR',
           'spirouFLAT',
           'spirouImage',
           'spirouLOCOR',
           'spirouPOLAR',
           'spirouRV',
           'spirouStartup',
           'spirouTelluric',
           'spirouTHORCA',
           'spirouUnitTests',
           'spirouTools']


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    print('Loaded modules:')
    # spirouBACK
    print('\n\t' + spirouBACK.__NAME__)
    print('\t\t--' + spirouBACK.spirouBACK.__NAME__)
    # spirouDB
    print('\n\t' + spirouDB.__NAME__)
    print('\t\t--' + spirouDB.spirouCDB.__NAME__)
    # spirouConfig
    print('\n\t' + spirouConfig.__NAME__)
    print('\t\t--' + spirouConfig.spirouConfig.__NAME__)
    print('\t\t--' + spirouConfig.spirouKeywords.__NAME__)
    print('\t\t--' + spirouConfig.spirouConst.__NAME__)
    # spirouCore
    print('\n\t' + spirouCore.__NAME__)
    print('\t\t--' + spirouCore.spirouLog.__NAME__)
    print('\t\t--' + spirouCore.spirouPlot.__NAME__)
    print('\t\t--' + spirouCore.spirouMath.__NAME__)
    # spirouEXTOR
    print('\n\t' + spirouEXTOR.__NAME__)
    print('\t\t--' + spirouEXTOR.spirouEXTOR.__NAME__)
    # spirouFLAT
    print('\n\t' + spirouFLAT.__NAME__)
    print('\t\t--' + spirouFLAT.spirouFLAT.__NAME__)
    # spirouImage
    print('\n\t' + spirouImage.__NAME__)
    print('\t\t--' + spirouImage.spirouImage.__NAME__)
    print('\t\t--' + spirouImage.spirouFITS.__NAME__)
    # spirouLOCOR
    print('\n\t' + spirouLOCOR.__NAME__)
    print('\t\t--' + spirouLOCOR.spirouLOCOR.__NAME__)
    # spirouPOLAR
    print('\n\t' + spirouPOLAR.__NAME__)
    print('\t\t--' + spirouPOLAR.spirouPOLAR.__NAME__)
    print('\t\t--' + spirouPOLAR.spirouLSD.__NAME__)
    # spirouRV
    print('\n\t' + spirouRV.__NAME__)
    print('\t\t--' + spirouRV.spirouRV.__NAME__)
    # spirouStartup
    print('\n\t' + spirouStartup.__NAME__)
    print('\t\t--' + spirouStartup.spirouStartup.__NAME__)
    # spirouTelluric
    print('\n\t' + spirouTelluric.__NAME__)
    print('\t\t--' + spirouTelluric.spirouTelluric.__NAME__)
    # spirouTHORCA
    print('\n\t' + spirouTHORCA.__NAME__)
    print('\t\t--' + spirouTHORCA.spirouTHORCA.__NAME__)

# =============================================================================
# End of Code
# =============================================================================
