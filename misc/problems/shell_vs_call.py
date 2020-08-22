#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-08-16 at 09:23

@author: cook
"""
import sys
import os
import platform
import psutil
import getpass
import socket

# =============================================================================
# Define functions
# =============================================================================
def main():
    keys = dict()
    keys['MAJOR'] = sys.version_info.major
    keys['MINOR'] = sys.version_info.minor
    keys['MICRO'] = sys.version_info.micro
    # get python path
    if 'PYTHONPATH' in os.environ:
        pythonpath = os.environ['PYTHONPATH']
        keys['PYTHONPATH'] = '\t\t' + '\n\t\t'.join(pythonpath.split(os.pathsep))
    else:
        keys['PYTHONPATH'] = 'None'
    # get path
    if 'PATH' in os.environ:
        path = os.environ['PATH']
        keys['PATH'] = '\t\t' + '\n\t\t'.join(path.split(os.pathsep))
    else:
        keys['PATH'] = 'None'
    # get DRS_UCONFIG
    if 'DRS_UCONFIG' in os.environ:
        keys['DRS_UCONFIG'] = os.environ['DRS_UCONFIG']
    else:
        keys['DRS_UCONFIG'] = 'None'
    # get modules
    try:
        import astropy
        keys['ASTROPY'] = astropy.__version__
    except:
        keys['ASTROPY'] = 'NOT FOUND'
    try:
        import barycorrpy
        keys['BARYCORRPY'] = barycorrpy.__version__
    except:
        keys['BARYCORRPY'] = 'NOT FOUND'
    try:
        import bottleneck
        keys['BOTTLENECK'] = bottleneck.__version__
    except:
        keys['BOTTLENECK'] = 'NOT FOUND'
    try:
        import numpy
        keys['NUMPY'] = numpy.__version__
    except:
        keys['NUMPY'] = 'NOT FOUND'
    try:
        import numba
        keys['NUMBA'] = numba.__version__
    except:
        keys['NUMBA'] = 'NOT FOUND'
    try:
        import matplotlib
        keys['MATPLOTLIB'] = matplotlib.__version__
    except:
        keys['MATPLOTLIB'] = 'NOT FOUND'
    try:
        import scipy
        keys['SCIPY'] = scipy.__version__
    except:
        keys['SCIPY'] = 'NOT FOUND'
    # apero setup
    try:
        import apero
        from apero.core.utils import drs_startup as drs
        from apero.core import constants
        instruments = drs.Constants['DRS_INSTRUMENTS']

        keys['APERO_VERSION'] = drs.__version__

        variables = ''
        variables += '\nAPERO DATE: {0}'.format(drs.__date__)
        variables += '\nAPERO PATH: {0}'.format(apero.__path__[0])
        variables += '\n'
        variables += '\nINSTALLED INSTRUMENTS: ' + ', '.join(instruments)

        for instrument in instruments:

            params = constants.load(instrument)
            # add variables
            variables += '\n\n' + '=' * 50
            variables += '\n\t' + instrument
            variables += '\n' + '='* 50 + '\n'
            variables += '\nDRS_ROOT: ' + params['DRS_ROOT']
            variables += '\nDRS_DATA_RAW: ' + params['DRS_DATA_RAW']
            variables += '\nDRS_DATA_REDUC: ' + params['DRS_DATA_REDUC']
            variables += '\nDRS_CALIB_DB: ' + params['DRS_CALIB_DB']
            variables += '\nDRS_TELLU_DB: ' + params['DRS_TELLU_DB']
            variables += '\nDRS_DATA_MSG: ' + params['DRS_DATA_MSG']
            variables += '\nDRS_DATA_WORKING: ' + params['DRS_DATA_WORKING']
            variables += '\nDRS_DATA_RUN: ' + params['DRS_DATA_RUN']

        keys['APERO_VARIABLES'] = variables


    except:
        keys['APERO_VERSION'] = 'NOT FOUND'
        keys['APERO_VARIABLES'] = ''

    # computer information
    keys['COMPUTER_RELEASE'] = platform.release()
    keys['COMPUTER_ARCHITECTURE'] = platform.machine()
    keys['COMPUTER_VERSION'] = platform.machine()
    keys['COMPUTER_SYSTEM'] = platform.system()
    keys['COMPUTER_PROCESSOR'] = platform.processor()
    totalmem = psutil.virtual_memory().total
    keys['COMPUTER_RAM'] = str(round(totalmem / (1024.0 ** 3))) + " GB"
    keys['USER'] = getpass.getuser()
    keys['HOST'] = socket.gethostname()
    keys['HOME'] = os.path.expanduser("~")

    print_string = """
    
================================================================================
APERO
================================================================================

DRS_UCONFIG = {DRS_UCONFIG}

APERO: {APERO_VERSION}

{APERO_VARIABLES}

================================================================================
PYTHON
================================================================================

PYTHON VERSION = {MAJOR}.{MINOR}.{MICRO}

PYTHON PATH:
{PYTHONPATH}

ASTROPY:       {ASTROPY}
BARYCORRPY:    {BARYCORRPY}
BOTTLENECK:    {BOTTLENECK}
NUMPY:         {NUMPY}
NUMBA:         {NUMBA}
MATPLOTLIB:    {MATPLOTLIB}
SCIPY:         {SCIPY}


================================================================================
COMPUTER
================================================================================
SYSTEM = {COMPUTER_SYSTEM}
RELEASE = {COMPUTER_RELEASE}
VERSION = {COMPUTER_VERSION}
ARCHITECTURE = {COMPUTER_ARCHITECTURE}
PROCESSOR = {COMPUTER_PROCESSOR}
RAM = {COMPUTER_RAM}
USER = {USER}
HOST = {HOST}
HOME = {HOME}

PATH:
{PATH}
    
    """

    print(print_string.format(**keys))


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments
    main()

# =============================================================================
# End of code
# =============================================================================