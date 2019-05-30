#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cal_validate_spirou.py [debug]

To be run after installation to test whether modules run

Created on 2017-11-27 at 16:27

@author: cook
"""
import os
import sys
from collections import OrderedDict

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_validate_spirou.py'
__version__ = 'Unknown'
__author__ = 'Unknown'
__release__ = 'Unknown'
__date__ = 'Unknown'
# set modules required
MODULES = OrderedDict()
MODULES['numpy'] = '1.14.0'
MODULES['scipy'] = '1.0.0'
MODULES['matplotlib'] = '2.1.2'
MODULES['astropy'] = '2.0.3'
# Whether be default we run debug mode
DEBUG = 0
# exit type
# noinspection PyProtectedMember
EXIT = os._exit


# =============================================================================
# Define functions
# =============================================================================
def main(check=1, debug_mode=0):
    """
    cal_validate_spirou.py main function, if debug mode is None uses
    arguments from run time i.e.:
        cal_validate_spirou.py [debug_mode]

    :param check: bool or int, if 1 or True runs the check for modules/
                  DRS modules, if 0 or False just prints paths

    :param debug_mode: bool or int, if 1 or True runs in debug mode
                       (extra output), if 0 or False runs in normal mode
                       (less output)

    :return ll: dictionary, containing all the local variables defined in
                main
    """
    if check:
        # print log
        print(' *****************************************')
        print(' *        VALIDATING DRS ')
        if DEBUG:
            print(' * ')
            print(' *     (DEBUG MODE ACTIVE) ')
        print(' *****************************************')
        # ---------------------------------------------------------------------
        # Module tests
        # ---------------------------------------------------------------------
        print(' \n0) Checking dependencies...')
        # loop around modules
        passed = False
        for module in list(MODULES.keys()):
            # get required version
            reqversion = MODULES[module]
            # test for module and minimum version
            passed = module_test(module, reqversion)
        if not passed:
            EXIT(1)

        # Check imports
        print('\n1) Running core module tests')
        # ---------------------------------------------------------------------
        # SpirouDRS
        # ---------------------------------------------------------------------
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
            print('\tInstallation failed with message')
            print('\t{0}'.format(e))
            EXIT(1)

        # ---------------------------------------------------------------------
        # spirouConfig
        # ---------------------------------------------------------------------
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

        # ---------------------------------------------------------------------
        # spirouCore
        # ---------------------------------------------------------------------
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

        # ---------------------------------------------------------------------
        # test constants
        # ---------------------------------------------------------------------
        print('\n2) Running config test')
        constants = try_to_read_config_file()
        test_paths(constants)

        # ---------------------------------------------------------------------
        # spirouBACK
        # ---------------------------------------------------------------------
        print('\n3) Running sub-module tests')
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

        # ---------------------------------------------------------------------
        # spirouDB
        # ---------------------------------------------------------------------
        try:
            # noinspection PyUnresolvedReferences
            from SpirouDRS import spirouDB
            if debug_mode:
                debug_message(spirouDB.__NAME__)
                debug_message(spirouDB.spirouCDB.__NAME__, True)
        except ImportError as e:
            print('Fatal error cannot import spirouDB from SpirouDRS')
            print('Error was: {0}'.format(e))
            EXIT(1)
        except Exception as e:
            print('Installation failed with message')
            print('   {0}'.format(e))
            EXIT(1)

        # ---------------------------------------------------------------------
        # spirouEXTOR
        # ---------------------------------------------------------------------
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
        # ---------------------------------------------------------------------
        # spirouspirouFLAT
        # ---------------------------------------------------------------------
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
        # ---------------------------------------------------------------------
        # spirouImage
        # ---------------------------------------------------------------------
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
        # ---------------------------------------------------------------------
        # spirouLOCOR
        # ---------------------------------------------------------------------
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

        # ---------------------------------------------------------------------
        # spirouRV
        # ---------------------------------------------------------------------
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

        # ---------------------------------------------------------------------
        # spirouStartup
        # ---------------------------------------------------------------------
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

        # ---------------------------------------------------------------------
        # spirouTHORCA
        # ---------------------------------------------------------------------
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

        # ---------------------------------------------------------------------
        # Now we have all modules we can print the paths
        # ---------------------------------------------------------------------
        print('\n4) Running recipe test')

    # if we have got to this stage all modules load and are present
    from SpirouDRS.spirouStartup import spirouStartup as Startup
    from SpirouDRS import spirouConfig
    from SpirouDRS.spirouCore import spirouLog
    # get log
    wlog = spirouLog.wlog
    # Get config parameters
    cparams, _ = spirouConfig.ReadConfigFile()
    # get drs_name and drs_version
    cparams['PID'], cparams['DATE_NOW'] = Startup.assign_pid()
    cparams['RECIPE'] = __NAME__.replace('.py', '')
    cparams['DRS_NAME'] = spirouConfig.Constants.NAME()
    cparams['DRS_VERSION'] = spirouConfig.Constants.VERSION()
    sources = ['PID', 'DATE_NOW', 'RECIPE', 'DRS_NAME', 'DRS_VERSION']
    cparams.set_sources(sources, __NAME__ + '.main()')
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
        wlog(cparams, '', '')
        wlog(cparams, '', 'Validation successful. DRS installed corrected.')

    # -------------------------------------------------------------------------
    # Currently some files are required to run the DRS (calibDB setup)
    # -------------------------------------------------------------------------
    if check:
        from SpirouDRS.spirouTools import drs_reset

        # log and ask user to confirm
        messages = ['\nFirst time installation?',
                    '\nAdd required files to DRS?\n']
        inputmessage = '\n\tSetup databases? [Y]es or [N]o\t'
        uinput = drs_reset.custom_confirmation(cparams, messages, inputmessage)
        # add calibDB files
        if uinput:
            drs_reset.reset_calibdb(cparams, log=True)
            wlog(cparams, '', 'Calibration database setup correctly.')
            drs_reset.reset_telludb(cparams, log=True)
            wlog(cparams, '', 'Telluric database setup correctly.')
        else:
            wlog(cparams, '', 'Assuming files setup correctly.')

    # -------------------------------------------------------------------------
    # return a copy of locally defined variables in the memory
    return dict(locals())


def debug_message(program, sub=False):

    if sub:
        print('\t\t\t -- "{0}"'.format(program))
    else:
        print('\n\t Successfully loaded "{0}"'.format(program))


def try_to_read_config_file():
    from SpirouDRS.spirouStartup import Begin
    p = Begin(recipe=__NAME__, quiet=True)
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

    # if using user config file display has to be altered
    if p['USER_CONFIG'] and ('DRS_UCONFIG' in p):
        umsg = '\n\t\t1) {0}\n\t\t2) {1}'
    else:
        umsg = '\n\t\t{0}'

    # print which config files we are testing
    msg = '\t Testing file(s): ' + umsg
    print(msg.format(config_file, p['DRS_UCONFIG']))

    # loop around paths and check if they exist
    for path in paths:
        # see if path was found in config_file
        if path not in p:
            emsg = '\n\t\tError: "{0}" not found in config file'
            print(emsg.format(path, config_file))
            passed = False
        # see if path was correct if found
        elif not os.path.exists(p[path]):
            emsg = '\n\t\tError: Path {0}="{1}" does not exist'
            emsg += '\n\t\t\t(Defined in {2})'
            print(emsg.format(path, p[path], p.sources[path]))
            passed = False
        # else path exists and is present
        else:
            pass

    # if all tests were past print it
    if passed:
        wmsg = ('\n\tCongratulations all paths in file(s):' + umsg +
                '\n\tset up correctly.')
        print(wmsg.format(config_file, p['DRS_UCONFIG']))
    else:
        wmsg = ('\n\tPlease set up config file(s):' + umsg +
                '\n\twith valid paths.')
        print(wmsg.format(config_file, p['DRS_UCONFIG']))
        EXIT(1)


def module_test(module, reqversion):
    # try to import module
    # noinspection PyBroadException
    try:
        imod = __import__(module)
        # noinspection PyBroadException
        try:
            # try to get version
            version = imod.__version__
            # perform version test
            passed = version_test(module, version, reqversion)
        except:
            print('\t{0} found'.format(module))
            passed = True
    except:
        print('\tFatal error DRS requires the module "{0}" (version={1})'
              ' to be installed'.format(module, reqversion))
        passed = False
    return passed


def version_test(modname, current, required):

    # get current version
    lcurrent, emsgs = convert_version_to_list(current)
    # write error
    if emsgs is not None:
        print('Error trying to get current version for {0}'.format(modname))
        print(emsgs)
        return False
    # get required version
    lrequired, emsgs = convert_version_to_list(required)
    # write error
    if emsgs is not None:
        print('Error trying to get required version for {0}'.format(modname))
        print(emsgs)
        return False
    # test version
    if lcurrent[0] > lrequired[0]:
        passed = True
    elif lcurrent[1] > lrequired[1] and lcurrent[0] == lrequired[0]:
        passed = True
    elif lcurrent[2] >= lrequired[2] and lcurrent[1] == lrequired[1]:
        passed = True
    else:
        passed = False

    if passed:
        print('\t{0} version={1} found'.format(modname, current))
    else:
        print('\tFatal error DRS requires {0} to be at least version {1}'
              ' (currently={2})'.format(modname, required, current))
    return passed


def convert_version_to_list(v):
    # noinspection PyBroadException
    try:
        vlist = v.split('.')
    except:
        emsgs = ('\tCannot split version parts (expected X.Y.Z or X.Y or X)'
                 '\n\tGot "{0}"'.format(v))
        return [-1, -1, -1], emsgs
    try:
        if len(vlist) == 3:
            vlist = [int(vlist[0]), int(vlist[1]), int(vlist[2])]
            return vlist, None
        elif len(vlist) == 2:
            vlist = [int(vlist[0]), int(vlist[1]), 0]
            return vlist, None
        elif len(vlist) == 1:
            vlist = [int(vlist[0]), 0, 0]
            return vlist, None
        else:
            emsgs = ('\tCannot read version parts (expected X.Y.Z or X.Y or X)'
                     '\n\tGot "{0}"'.format(v))
            return [-1, -1, -1], emsgs
    except Exception as e:
        emsgs = ('\n\tError {0}: {1}'.format(type(e), e))
        return [-1, -1, -1], emsgs


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # if there is an argument it is the debug mode so try to convert it to
    #   boolean logic True/False
    if len(sys.argv) == 3:
        # noinspection PyBroadException
        try:
            check2 = bool(eval(sys.argv[1]))
            debug2 = bool(eval(sys.argv[2]))
        except Exception:
            check2 = 1
            debug2 = DEBUG

    elif len(sys.argv) == 2:
        # noinspection PyBroadException
        try:
            check2 = bool(eval(sys.argv[1]))
        except Exception:
            check2 = 1
        debug2 = DEBUG
    else:
        check2 = 1
        debug2 = DEBUG
    # run main with no arguments (get from command line - sys.argv)
    ll = main(check=check2, debug_mode=debug2)

# =============================================================================
# End of code
# =============================================================================
