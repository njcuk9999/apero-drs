#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-11-27 at 16:27

@author: cook



Version 0.0.0
"""
import sys
import os



# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_validate_drs.py'
# Whether be default we run debug mode
DEBUG = 0

# =============================================================================
# Define functions
# =============================================================================
def main(debug_mode=0):
    # Check imports

    # -------------------------------------------------------------------------
    # SpirouDRS
    # -------------------------------------------------------------------------
    try:
        import SpirouDRS
        if debug_mode:
            print('\n\tLoaded' + SpirouDRS.__NAME__)
    except ImportError as e:
        print('Fatal error cannot import SpirouDRS')
        print('INSTALL folder must be on PYTHONPATH')
        os._exit(1)
    # -------------------------------------------------------------------------
    # spirouBACK
    # -------------------------------------------------------------------------
    try:
        from SpirouDRS import spirouBACK
        if debug_mode:
            print('\n\t' + spirouBACK.__NAME__)
            print('\t\t--' + spirouBACK.spirouBACK.__NAME__)
    except ImportError as e:
        print('Fatal error cannot import spirouBACK from SpirouDRS')
        print('Error was: {0}'.format(e))   
        os._exit(1)
    # -------------------------------------------------------------------------
    # spirouCDB
    # -------------------------------------------------------------------------
    try:
        from SpirouDRS import spirouCDB
        if debug_mode:
            print('\n\t' + spirouCDB.__NAME__)
            print('\t\t--' + spirouCDB.spirouCDB.__NAME__)
    except ImportError as e:
        print('Fatal error cannot import spirouCDB from SpirouDRS')
        print('Error was: {0}'.format(e))   
        os._exit(1)
    # -------------------------------------------------------------------------
    # spirouCore
    # -------------------------------------------------------------------------
    try:
        from SpirouDRS import spirouCore
        if debug_mode:
            print('\n\tLoaded' + spirouCore.__NAME__)
            print('\t\tLoaded' + spirouCore.spirouLog.__NAME__)
            print('\t\tLoaded' + spirouCore.spirouPlot.__NAME__)
            print('\t\tLoaded' + spirouCore.spirouMath.__NAME__)
    except ImportError as e:
        print('Fatal error cannot import spirouCore from SpirouDRS')
        print('Error was: {0}'.format(e))   
        os._exit(1)
    # -------------------------------------------------------------------------
    # spirouConfig
    # -------------------------------------------------------------------------
    try:
        from SpirouDRS import spirouConfig
        if debug_mode:
            print('\n\tLoaded' + spirouConfig.__NAME__)
            print('\t\tLoaded' + spirouConfig.spirouConfig.__NAME__)
            print('\t\tLoaded' + spirouConfig.spirouKeywords.__NAME__)
            print('\t\tLoaded' + spirouConfig.spirouConst.__NAME__)
    except ImportError as e:
        print('Fatal error cannot import spirouConfig from SpirouDRS')
        print('Error was: {0}'.format(e))   
        os._exit(1)
    # -------------------------------------------------------------------------
    # spirouEXTOR
    # -------------------------------------------------------------------------
    try:
        from SpirouDRS import spirouEXTOR
        if debug_mode:
            print('\n\t' + spirouEXTOR.__NAME__)
            print('\t\t--' + spirouEXTOR.spirouEXTOR.__NAME__)
    except ImportError as e:
        print('Fatal error cannot import spirouEXTOR from SpirouDRS')
        print('Error was: {0}'.format(e))   
        os._exit(1)
    # -------------------------------------------------------------------------
    # spirouspirouFLAT
    # -------------------------------------------------------------------------
    try:
        from SpirouDRS import spirouFLAT
        if debug_mode:
            print('\n\t' + spirouFLAT.__NAME__)
            print('\t\t--' + spirouFLAT.spirouFLAT.__NAME__)
    except ImportError as e:
        print('Fatal error cannot import spirouFLAT from SpirouDRS')
        print('Error was: {0}'.format(e))   
        os._exit(1)
    # -------------------------------------------------------------------------
    # spirouImage
    # -------------------------------------------------------------------------
    try:
        from SpirouDRS import spirouImage
        if debug_mode:
            print('\n\t' + spirouImage.__NAME__)
            print('\t\t--' + spirouImage.spirouImage.__NAME__)
            print('\t\t--' + spirouImage.spirouFITS.__NAME__)
    except ImportError as e:
        print('Fatal error cannot import spirouImage from SpirouDRS')
        print('Error was: {0}'.format(e))   
        os._exit(1)
    # -------------------------------------------------------------------------
    # spirouLOCOR
    # -------------------------------------------------------------------------
    try:
        from SpirouDRS import spirouLOCOR
        if debug_mode:
            print('\n\t' + spirouLOCOR.__NAME__)
            print('\t\t--' + spirouLOCOR.spirouLOCOR.__NAME__)
    except ImportError as e:
        print('Fatal error cannot import spirouLOCOR from SpirouDRS')
        print('Error was: {0}'.format(e))   
        os._exit(1)
    # -------------------------------------------------------------------------
    # spirouImage
    # -------------------------------------------------------------------------
    try:
        from SpirouDRS import spirouStartup
        if debug_mode:
            print('\n\t' + spirouStartup.__NAME__)
            print('\t\t--' + spirouStartup.spirouStartup.__NAME__)
    except ImportError as e:
        print('Fatal error cannot import spirouStartup from SpirouDRS')
        print('Error was: ' + e)
        os._exit(1)

    # if we have got to this stage all modules load and are present
    import SpirouDRS.spirouStartup.spirouStartup as ss
    from SpirouDRS import spirouConfig
    from SpirouDRS.spirouCore import spirouLog
    # get log
    WLOG = spirouLog.logger
    # Get config parameters
    cparams = spirouConfig.ReadConfigFile()
    # check that drs_name and drs_version exist
    spirouConfig.CheckConfig(cparams, ['DRS_NAME', 'DRS_VERSION'])
    # display title
    ss.display_title(cparams)
    # check input parameters
    cparams = spirouConfig.CheckCparams(cparams)
    # display initial parameterisation
    ss.display_initial_parameterisation(cparams)
    # see if we are logging all

    # log that validation was successful
    if not spirouLog.correct_level('all', cparams['PRINT_LEVEL']):
        print('\n')
        print('Validation successful. DRS installed corrected.')
    else:
        WLOG('', '', '')
        WLOG('', '', 'Validation successful. DRS installed corrected.')

# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    main(debug_mode=DEBUG)


# =============================================================================
# End of code
# =============================================================================
