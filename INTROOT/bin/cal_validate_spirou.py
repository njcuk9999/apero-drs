#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cal_validate_spirou.py

To be run after installation to test whether modules run

Created on 2017-11-27 at 16:27

@author: cook
"""
import os

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_validate_spirou.py'
__version__ = 'Unknown'
__author__ = 'Unknown'
__release__ = 'Unknown'
__date__ = 'Unknown'

# Whether be default we run debug mode
DEBUG = 0
# exit type
# noinspection PyProtectedMember
EXIT = os._exit


# =============================================================================
# Define functions
# =============================================================================
def main(debug_mode=0):
    # print log
    print(' *****************************************')
    print(' *        VALIDATING DRS ')
    if DEBUG:
        print(' * ')
        print(' *     (DEBUG MODE ACTIVE) ')
    print(' *****************************************\n')

    # Check imports
    print('\n\n1) Running core module tests\n')
    # -------------------------------------------------------------------------
    # SpirouDRS
    # -------------------------------------------------------------------------
    try:
        # noinspection PyUnresolvedReferences
        import SpirouDRS
        if debug_mode:
            debug_message(SpirouDRS.__NAME__)
    except ImportError as e:
        print('Fatal error cannot import SpirouDRS')
        print('INSTALL folder must be on PYTHONPATH')
        EXIT(1)
    # if other exception try to read constants file and check paths
    except Exception as e:
        print('Installation failed with message')
        print('   {0}'.format(e))
        EXIT(1)

    # -------------------------------------------------------------------------
    # spirouConfig
    # -------------------------------------------------------------------------
    try:
        # noinspection PyUnresolvedReferences
        from SpirouDRS import spirouConfig
        if debug_mode:
            debug_message(spirouConfig.__NAME__)
            debug_message(spirouConfig.spirouConfig.__NAME__, True)
            debug_message(spirouConfig.spirouKeywords.__NAME__, True)
            debug_message(spirouConfig.spirouConst.__NAME__, True)
    except ImportError as e:
        print('Fatal error cannot import spirouConfig from SpirouDRS')
        print('Error was: {0}'.format(e))
        EXIT(1)
    except Exception as e:
        print('Installation failed with message')
        print('   {0}'.format(e))
        EXIT(1)

    # -------------------------------------------------------------------------
    # spirouCore
    # -------------------------------------------------------------------------
    try:
        # noinspection PyUnresolvedReferences
        from SpirouDRS import spirouCore
        if debug_mode:
            debug_message(spirouCore.__NAME__)
            debug_message(spirouCore.spirouLog.__NAME__, True)
            debug_message(spirouCore.spirouPlot.__NAME__, True)
            debug_message(spirouCore.spirouMath.__NAME__, True)
    except ImportError as e:
        print('Fatal error cannot import spirouCore from SpirouDRS')
        print('Error was: {0}'.format(e))
        EXIT(1)
    except Exception as e:
        print('Installation failed with message')
        print('   {0}'.format(e))
        EXIT(1)

    # -------------------------------------------------------------------------
    # test constants
    # -------------------------------------------------------------------------
    print('\n\n2) Running config test\n')
    constants = try_to_read_config_file()
    test_paths(constants)

    # -------------------------------------------------------------------------
    # spirouBACK
    # -------------------------------------------------------------------------
    print('\n\n2) Running sub-module tests\n')
    try:
        # noinspection PyUnresolvedReferences
        from SpirouDRS import spirouBACK
        if debug_mode:
            debug_message(spirouBACK.__NAME__)
            debug_message(spirouBACK.spirouBACK.__NAME__, True)
    except ImportError as e:
        print('Fatal error cannot import spirouBACK from SpirouDRS')
        print('Error was: {0}'.format(e))   
        EXIT(1)
    except Exception as e:
        print('Installation failed with message')
        print('   {0}'.format(e))
        EXIT(1)

    # -------------------------------------------------------------------------
    # spirouCDB
    # -------------------------------------------------------------------------
    try:
        # noinspection PyUnresolvedReferences
        from SpirouDRS import spirouCDB
        if debug_mode:
            debug_message(spirouCDB.__NAME__)
            debug_message(spirouCDB.spirouCDB.__NAME__, True)
    except ImportError as e:
        print('Fatal error cannot import spirouCDB from SpirouDRS')
        print('Error was: {0}'.format(e))   
        EXIT(1)
    except Exception as e:
        print('Installation failed with message')
        print('   {0}'.format(e))
        EXIT(1)

    # -------------------------------------------------------------------------
    # spirouEXTOR
    # -------------------------------------------------------------------------
    try:
        # noinspection PyUnresolvedReferences
        from SpirouDRS import spirouEXTOR
        if debug_mode:
            debug_message(spirouEXTOR.__NAME__)
            debug_message(spirouEXTOR.spirouEXTOR.__NAME__, True)
    except ImportError as e:
        print('Fatal error cannot import spirouEXTOR from SpirouDRS')
        print('Error was: {0}'.format(e))   
        EXIT(1)
    except Exception as e:
        print('Installation failed with message')
        print('   {0}'.format(e))
        EXIT(1)
    # -------------------------------------------------------------------------
    # spirouspirouFLAT
    # -------------------------------------------------------------------------
    try:
        # noinspection PyUnresolvedReferences
        from SpirouDRS import spirouFLAT
        if debug_mode:
            debug_message(spirouFLAT.__NAME__)
            debug_message(spirouFLAT.spirouFLAT.__NAME__, True)
    except ImportError as e:
        print('Fatal error cannot import spirouFLAT from SpirouDRS')
        print('Error was: {0}'.format(e))   
        EXIT(1)
    except Exception as e:
        print('Installation failed with message')
        print('   {0}'.format(e))
        EXIT(1)
    # -------------------------------------------------------------------------
    # spirouImage
    # -------------------------------------------------------------------------
    try:
        # noinspection PyUnresolvedReferences
        from SpirouDRS import spirouImage
        if debug_mode:
            debug_message(spirouImage.__NAME__)
            debug_message(spirouImage.spirouImage.__NAME__, True)
            debug_message(spirouImage.spirouFITS.__NAME__, True)
    except ImportError as e:
        print('Fatal error cannot import spirouImage from SpirouDRS')
        print('Error was: {0}'.format(e))   
        EXIT(1)
    except Exception as e:
        print('Installation failed with message')
        print('   {0}'.format(e))
        EXIT(1)
    # -------------------------------------------------------------------------
    # spirouLOCOR
    # -------------------------------------------------------------------------
    try:
        # noinspection PyUnresolvedReferences
        from SpirouDRS import spirouLOCOR
        if debug_mode:
            debug_message(spirouLOCOR.__NAME__)
            debug_message(spirouLOCOR.spirouLOCOR.__NAME__, True)
    except ImportError as e:
        print('Fatal error cannot import spirouLOCOR from SpirouDRS')
        print('Error was: {0}'.format(e))   
        EXIT(1)
    except Exception as e:
        print('Installation failed with message')
        print('   {0}'.format(e))
        EXIT(1)

    # -------------------------------------------------------------------------
    # spirouRV
    # -------------------------------------------------------------------------
    try:
        # noinspection PyUnresolvedReferences
        from SpirouDRS import spirouRV
        if debug_mode:
            debug_message(spirouRV.__NAME__)
            debug_message(spirouRV.spirouRV.__NAME__, True)
    except ImportError as e:
        print('Fatal error cannot import spirouRV from SpirouDRS')
        print('Error was: {0}'.format(e))
        EXIT(1)
    except Exception as e:
        print('Installation failed with message')
        print('   {0}'.format(e))
        EXIT(1)

    # -------------------------------------------------------------------------
    # spirouStartup
    # -------------------------------------------------------------------------
    try:
        # noinspection PyUnresolvedReferences
        from SpirouDRS import spirouStartup
        if debug_mode:
            debug_message(spirouStartup.__NAME__)
            debug_message(spirouStartup.spirouStartup.__NAME__, True)
    except ImportError as e:
        print('Fatal error cannot import spirouStartup from SpirouDRS')
        print('Error was: ' + str(e))
        EXIT(1)
    except Exception as e:
        print('Installation failed with message')
        print('   {0}'.format(e))
        EXIT(1)

    # -------------------------------------------------------------------------
    # spirouTHORCA
    # -------------------------------------------------------------------------
    try:
        # noinspection PyUnresolvedReferences
        from SpirouDRS import spirouTHORCA
        if debug_mode:
            debug_message(spirouTHORCA.__NAME__)
            debug_message(spirouTHORCA.spirouTHORCA.__NAME__, True)
    except ImportError as e:
        print('Fatal error cannot import spirouTHORCA from SpirouDRS')
        print('Error was: ' + str(e))
        EXIT(1)
    except Exception as e:
        print('Installation failed with message')
        print('   {0}'.format(e))
        EXIT(1)

    # -------------------------------------------------------------------------
    # Now we have all modules we can print the paths
    # -------------------------------------------------------------------------
    print('\n\n4) Running recipe test\n')

    # if we have got to this stage all modules load and are present
    from SpirouDRS.spirouStartup import spirouStartup as Startup
    from SpirouDRS import spirouConfig
    from SpirouDRS.spirouCore import spirouLog
    # get log
    wlog = spirouLog.logger
    # Get config parameters
    cparams = spirouConfig.ReadConfigFile()
    # get drs_name and drs_version
    cparams['DRS_NAME'] = spirouConfig.Constants.NAME()
    cparams['DRS_VERSION'] = spirouConfig.Constants.VERSION()
    cparams.set_sources(['DRS_NAME', 'DRS_VERSION'], 'spirouConfig.Constants')
    # display title
    Startup.display_drs_title(cparams)
    # check input parameters
    cparams = spirouConfig.CheckCparams(cparams)
    # display initial parameterisation
    Startup.display_initial_parameterisation(cparams)
    # log that validation was successful
    if not spirouLog.correct_level('all', cparams['PRINT_LEVEL']):
        print('\n')
        print('Validation successful. DRS installed corrected.')
    else:
        wlog('', '', '')
        wlog('', '', 'Validation successful. DRS installed corrected.')

    # return a copy of locally defined variables in the memory
    return dict(locals())


def debug_message(program, sub=False):

    if sub:
        print('\t\t\t -- "{0}"'.format(program))
    else:
        print('\n\t Successfully loaded "{0}"'.format(program))


def try_to_read_config_file():
    from SpirouDRS.spirouConfig.spirouConfigFile import read_config_file
    from SpirouDRS.spirouConfig.spirouConst import PACKAGE
    from SpirouDRS.spirouConfig.spirouConst import CONFIGFOLDER
    from SpirouDRS.spirouConfig.spirouConst import CONFIGFILE

    p = read_config_file(PACKAGE(), CONFIGFOLDER(), CONFIGFILE(),
                         return_raw=False)
    return p


def test_paths(p):
    from SpirouDRS.spirouConfig.spirouConfigFile import get_default_config_file
    from SpirouDRS.spirouConfig.spirouConst import PACKAGE
    from SpirouDRS.spirouConfig.spirouConst import CONFIGFOLDER
    from SpirouDRS.spirouConfig.spirouConst import CONFIGFILE
    config_file = get_default_config_file(PACKAGE(), CONFIGFOLDER(),
                                          CONFIGFILE())

    paths = ['TDATA', 'DRS_ROOT', 'DRS_DATA_RAW', 'DRS_DATA_REDUC',
             'DRS_CALIB_DB', 'DRS_DATA_MSG', 'DRS_DATA_WORKING']

    passed = True
    print('\t Testing {0}'.format(config_file))
    for path in paths:
        # see if path was found in config_file
        if path not in p:
            emsg = '\n\t\tError: "{0}" not found in config file'
            print(emsg.format(path, config_file))
            passed = False
        # see if path was correct if found
        elif not os.path.exists(p[path]):
            emsg = '\n\t\tError: Path {0}="{1}" does not exist'
            print(emsg.format(path, p[path], config_file))
            passed = False
        # else path exists and is present
        else:
            pass

    # if all tests were past print it
    if passed:
        wmsg = '\n\t\tCongraulations all paths in {0} set up correctly.\n'
        print(wmsg.format(config_file))
    else:
        wmsg = '\n\tPlease set up config file ({0}) with valid paths.\n'
        print(wmsg.format(config_file))
        EXIT(1)


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main(debug_mode=DEBUG)

# =============================================================================
# End of code
# =============================================================================
