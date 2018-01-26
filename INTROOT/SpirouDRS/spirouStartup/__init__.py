#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
initialization code for Spirou startup module

Created on 2017-11-17 at 13:38

@author: cook

"""
from SpirouDRS import spirouConfig
from . import spirouStartup

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouCore.__init__()'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__release__ = spirouConfig.Constants.RELEASE()
# define imports using asterisk
__all__ = ['Begin', 'GetCustomFromRuntime', 'GetFile', 'GetFiberType',
           'LoadArguments', 'InitialFileSetup']

# =============================================================================
# Function aliases
# =============================================================================

Begin = spirouStartup.run_begin
"""
Begin DRS - Must be run at start of every recipe
- loads the parameters from the primary configuration file, displays 
  title, checks priamry constants and displays initial parameterization

:return cparams: parameter dictionary, ParamDict constants from primary
                 configuration file
"""

GetCustomFromRuntime = spirouStartup.get_custom_from_run_time_args
"""
Extract custom arguments from defined positions in sys.argv (defined at
run time)

:param positions: list of integers, the positions of the arguments
                  (i.e. first argument is 0)

:param types: list of python types, the type (i.e. int, float) for each
              argument
:param names: list of strings, the names of each argument (to access in
              parameter dictionary once extracted)

:param required: list of bools or None, states whether the program
                 should exit if runtime argument not found

:param calls: list of objects or None, if define these are the values that
              come from a function call (overwrite command line arguments)

:param lognames: list of strings, the names displayed in the log (on error)
                 theses should be similar to "names" but in a form the
                 user can easily understand for each variable

:return values: dictionary, if run time arguments are correct python type
                the name-value pairs are returned
"""

GetFile = spirouStartup.get_file
"""
Get full file path and check the path and file exist

:param p: parameter dictionary, the parameter dictionary
:param path: string, either the directory to the folder (if name is None) or
             the full path to the file
:param name: string or None, the name of the file, if None name is assumed
             to be in path
:param prefix: string or None, if not None this substring must be in the
               filename
:param kind: string or None, the type of file (for logging)

:return location: string, the full file path of the file
"""

GetFiberType = spirouStartup.get_fiber_type
"""
Get fiber types and search for a valid fiber type in filename

:param p: parameter dictionary, the parameter dictionary
:param filename: string, the filename to search for fiber types in
:param fibertypes: list of strings, the fiber types to search for

:return fiber: string, the fiber found (exits via WLOG if no fiber found)
"""

LoadArguments = spirouStartup.load_arguments
"""
Run initial start up:

1) Read main config file
2) check certain parameters exist
3) display title
4) display initial parameterisation
5) display help file (if requested and exists)
6) loads run time arguments (and custom arguments, see below)
7) loads other config files

:param cparams: parameter dictionary from run_begin

:param night_name: string or None, the name of the directory in DRS_DATA_RAW
                   to find the files in

                   if None (undefined) uses the first argument in command
                   line (i.e. sys.argv[1])

                   if defined overwrites call from
                   command line (i.e. overwrites sys.argv)

                   stored in p['arg_night_name']

:param files: list of strings or None, the files to use for this program

              if None (undefined) uses the second and all other arguments in
              the command line (i.e. sys.argv[2:])

              if defined overwrites call from command line

              stored in p['arg_file_names']

:param customargs: None or list of strings, if list of strings then instead
                   of getting the standard runtime arguments

       i.e. in form:

            program.py rawdirectory arg_file_names[0] arg_file_names[1]...

       loads all arguments into customargs

       i.e. if customargs = ['rawdir', 'filename', 'a', 'b', 'c']
       expects command line arguments to be:

            program.py rawdir filename a b c

:return p: dictionary, parameter dictionary
"""

InitialFileSetup = spirouStartup.initial_file_setup
"""
Run start up code (based on program and parameters defined in p before)


:param p: dictionary, parameter dictionary

:param kind: string, description of program we are running (i.e. dark)

:param prefixes: list of strings, prefixes to look for in file name
:param prefixes: list of strings, prefixes to look for in file name
                 will exit code if none of the prefixes are found
                 (prefix = None if no prefixes are needed to be found)

:param add_to_p: dictionary structure:

        add_to_p[prefix1] = dict(key1=value1, key2=value2)
        add_to_p[prefix2] = dict(key3=value3, key4=value4)

        where prefix1 and prefix2 are the strings in "prefixes"

        This will add the sub dictionarys to the main parameter dictionary
        based on which prefix is found

        i.e. if prefix1 is found key "value3" and "value4" above are added
        (with "key3" and "key4") to the parameter dictionary p

:param calibdb: bool, if True calibDB folder and files are required and
                program will log and exit if they are not found
                if False, program will create calibDB folder

:return p: dictionary, parameter dictionary
"""

# =============================================================================
# End of code
# =============================================================================
