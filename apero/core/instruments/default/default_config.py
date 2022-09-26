"""
Default parameters for NO INSTRUMENT

This is the default config file

Created on 2019-01-17

@author: cook
"""
from apero.base import base
from apero.core.constants import constant_functions

# =============================================================================
# Define variables
# =============================================================================
# all definition
__all__ = [  # global settings
    'DRS_PLOT', 'DRS_DEBUG', 'PARAMETER_SNAPSHOT',
    # path settings
    'DRS_ROOT', 'DRS_DATA_RAW', 'DRS_DATA_REDUC', 'DRS_DATA_OUT',
    'DRS_CALIB_DB', 'DRS_TELLU_DB', 'DRS_DATA_MSG', 'DRS_DATA_WORKING',
    'DRS_DATA_RUN', 'DRS_DATA_MSG_FULL', 'DRS_DATA_ASSETS',
    # General properites
    'DRS_VERSION', 'AUTHORS', 'DRS_RELEASE', 'DRS_DATE', 'LANGUAGE',
    # Instrument/Observatory Constants
    'INSTRUMENT', 'OBS_LONG', 'OBS_LAT', 'OBS_ALT',
    # DRS SETTINGS
    'DRS_PACKAGE', 'DRS_USERENV', 'DRS_GROUP', 'DRS_RECIPE_KIND',
    'DRS_USER_DEFAULT', 'IS_REF', 'DRS_RECIPE_TYPE', 'DRS_GROUP_PATH',
    # DRS INTERNAL PATHS
    'DRS_USER_DEFAULT', 'DRS_MOD_DATA_PATH', 'DRS_MOD_INSTRUMENT_CONFIG',
    'DRS_MOD_CORE_CONFIG', 'DRS_WAVE_DATA',
    'DRS_INSTRUMENT_RECIPE_PATH', 'DRS_DEFAULT_RECIPE_PATH',
    'DRS_BADPIX_DATA', 'DRS_CALIB_DATA',
    'DRS_RESET_ASSETS_PATH', 'DRS_RESET_CALIBDB_PATH',
    'DRS_RESET_TELLUDB_PATH', 'DRS_USER_PROGRAM',
    'DRS_PDB_RC_FILE', 'IPYTHON_RETURN', 'ALLOW_BREAKPOINTS',
    'DRS_RESET_RUN_PATH', 'DRS_INSTRUMENTS', 'DRS_PDB_RC_FILENAME',
    # DATABASE SETTINGS
    'DATABASE_DIR', 'CALIB_DB_MATCH', 'TELLU_DB_MATCH',
    # DISPLAY/LOGGING SETTINGS
    'DRS_PRINT_LEVEL', 'DRS_LOG_LEVEL', 'DRS_COLOURED_LOG', 'DRS_THEME',
    'DRS_MAX_IO_DISPLAY_LIMIT', 'DRS_HEADER', 'DRS_LOG_CAUGHT_WARNINGS',
    'DRS_LOG_EXIT_TYPE', 'DRS_LOG_FORMAT', 'DRS_LOG_FITS_NAME', 'DRS_LOG_EMAIL',
    'DRS_LOG_EMAIL_AUTH', 'DRS_LOG_EMAIL_AUTH_PATH',
    # PLOT SETTINGS
    'DRS_PLOT_FONT_FAMILY', 'DRS_PLOT_FONT_WEIGHT',
    'DRS_PLOT_FONT_SIZE', 'DRS_PLOT_STYLE', 'DRS_DATA_PLOT',
    'DRS_PLOT_EXT', 'DRS_SUMMARY_EXT', 'DRS_SUMMARY_STYLE',
    # debug settings
    'DEBUG_MODE_LOG_PRINT', 'DEBUG_MODE_TEXTNAME_PRINT',
    'DEBUG_MODE_FUNC_PRINT',
]

# set name
__NAME__ = 'apero.constants.default.default_config'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Constants definition
Const = constant_functions.Const

# =============================================================================
# global settings
# =============================================================================
cgroup = 'GLOBAL SETTINGS'
# PLotting mode (0-3)
DRS_PLOT = Const('DRS_PLOT', value=0, dtype=int, source=__NAME__, user=True,
                 active=True, group=cgroup, options=[0, 1, 2, 3],
                 description='Plotting mode: '
                             '\n\t0: No plots'
                             '\n\t1: only summary plots '
                             '\n\t2: debug plots at end of code '
                             '\n\t3: debug plots at time of creation '
                             '(pauses code)')

# Whether to run in debug mode
DRS_DEBUG = Const('DRS_DEBUG', value=0, dtype=int, source=__NAME__, user=True,
                  active=True, group=cgroup, options=[0, 1, 100, 200],
                  description='Debug mode: '
                              '\n\t0: no debug '
                              '\n\t1: some debug output + python debugging '
                              '\n\t100: all in (1) and Language DB codes on '
                              'all text '
                              '\n\t200: all in (100) + function entry '
                              'printouts')

# Language
LANGUAGE = Const('LANGUAGE', value=base.DEFAULT_LANG, dtype=str,
                 options=base.LANGUAGES,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description='Language for DRS messages (if translated)')


# Add snapshot parameter table to reduced outputs
PARAMETER_SNAPSHOT = Const('PARAMETER_SNAPSHOT', value=True, dtype=bool,
                           source=__NAME__, user=True, active=True,
                           group=cgroup,
                           description='Add snapshot parameter table to '
                                       'reduced outputs',
                           output=False)


# =============================================================================
# path settings
# =============================================================================
cgroup = 'PATH SETTINGS'
#   Define the root installation directory
DRS_ROOT = Const('DRS_ROOT', dtype='path', source=__NAME__, user=True,
                 active=True, group=cgroup, value='./',
                 description='Define the root installation directory')

#   Define the directory with the raw data files in  (block directory)
DRS_DATA_RAW = Const('DRS_DATA_RAW', dtype='path', source=__NAME__, user=True,
                     active=True, group=cgroup, value='./apero-data/raw',
                     description='Define the directory with the raw data '
                                 'files in  (block directory)')

#   Define the directory that the reduced data should be saved to/read from
DRS_DATA_REDUC = Const('DRS_DATA_REDUC', dtype='path', source=__NAME__,
                       user=True,
                       active=True, group=cgroup, value='./apero-data/reduced',
                       description='Define the directory that the reduced data '
                                   'should be saved to/read from')

#   Define the directory that the post processed data should be saved to
DRS_DATA_OUT = Const('DRS_DATA_OUT', dtype='path', source=__NAME__,
                     user=True, active=True, group=cgroup,
                     value='./apero-data/out',
                     description='Define the directory that the post processed'
                                 ' data should be saved to')

#   Define the directory that the calibration files should be saved to/read from
DRS_CALIB_DB = Const('DRS_CALIB_DB', dtype='path', source=__NAME__, user=True,
                     active=True, group=cgroup, value='./apero-data/calibDB',
                     description='Define the directory that the calibration '
                                 'files should be saved to/read from')

#   Define the directory that the calibration files should be saved to/read from
DRS_TELLU_DB = Const('DRS_TELLU_DB', dtype='path', source=__NAME__, user=True,
                     active=True, group=cgroup, value='./apero-data/telluDB',
                     description='Define the directory that the calibration '
                                 'files should be saved to/read from')

#   Define the directory that the log messages are stored in
DRS_DATA_MSG = Const('DRS_DATA_MSG', dtype='path', source=__NAME__, user=True,
                     active=True, group=cgroup, value='./apero-data/msg',
                     description='Define the directory that the log messages '
                                 'are stored in')

#   Define the full data message path (set after group name known)
DRS_DATA_MSG_FULL = Const('DRS_DATA_MSG_FULL', dtype='path', source=__NAME__,
                          user=False, group=cgroup, value=None,
                          description=('Define the full data message path '
                                       '(set after group name known)'))

#   Define the working directory
DRS_DATA_WORKING = Const('DRS_DATA_WORKING', dtype='path', source=__NAME__,
                         user=True, active=True, group=cgroup,
                         value='./apero-data/working',
                         description='Define the working directory')

#   Define the plotting directory
DRS_DATA_PLOT = Const('DRS_DATA_PLOT', dtype='path', source=__NAME__, user=True,
                      active=True, group=cgroup, value='./apero-data/plot',
                      description='Define the plotting directory')

#   Define the run directory
DRS_DATA_RUN = Const('DRS_DATA_RUN', dtype='path', source=__NAME__, user=True,
                     active=True, group=cgroup, value='./apero-data/runs',
                     description='Define the run directory')

#   Define the assets directory
DRS_DATA_ASSETS = Const('DRS_DATA_ASSETS', dtype='path', source=__NAME__,
                        user=True, active=True, group=cgroup,
                        value='./apero-data/assets',
                        description='Define the assets directory')

# =============================================================================
# =============================================================================
# Internal configuration (These should probably not change per instrument)
# =============================================================================
# =============================================================================

# =============================================================================
# INTERNAL: General properites
# =============================================================================
cgroup = 'INTERNAL: General properites'
# Version
DRS_VERSION = Const('DRS_VERSION', value=__version__, dtype=str,
                    source=__NAME__, group=cgroup, description='Version')

# Authors
AUTHORS = Const('AUTHORS', value=__author__,
                dtype=list, dtypei=str, source=__NAME__, group=cgroup,
                description='Authors', output=False)

# Release version
DRS_RELEASE = Const('DRS_RELEASE', value=__release__, dtype=str,
                    source=__NAME__, group=cgroup,
                    description='Release version')

# Date
DRS_DATE = Const('DRS_DATE', value=__date__, dtype=str, source=__NAME__,
                 group=cgroup, description='Date')

# =============================================================================
# DRS SETTINGS
# =============================================================================
cgroup = 'INTERNAL: DRS SETTINGS'
#   The top-level package name (i.e. import PACKAGE)
DRS_PACKAGE = Const('DRS_PACKAGE', value=__PACKAGE__, dtype=str,
                    source=__NAME__, group=cgroup,
                    description=('The top-level package name (i.e. '
                                 'import PACKAGE)'), output=False)

#   User-config environmental variable
DRS_USERENV = Const('DRS_USERENV', value=base.USER_ENV, dtype=str,
                    source=__NAME__, group=cgroup,
                    description='User-config environmental variable')

#   User-defined program name (overwrite logging program)
DRS_USER_PROGRAM = Const('DRS_USER_PROGRAM', value=None, dtype=str,
                         source=__NAME__, group=cgroup,
                         description=('User-defined program name (overwrite '
                                      'logging program)'), output=False)

# whether to be in ipython return mode (always exits to ipdb via pdbrc)
IPYTHON_RETURN = Const('IPYTHON_RETURN', value=False, dtype=bool,
                       source=__NAME__, group=cgroup,
                       description=('whether to be in ipython return mode '
                                    '(always exits to ipdb via pdbrc)'),
                       output=False)
# whether to allow break points
ALLOW_BREAKPOINTS = Const('ALLOW_BREAKPOINTS', value=False, dtype=bool,
                          source=__NAME__, group=cgroup,
                          description='whether to allow break points',
                          output=False)

# Currently supported instruments
DRS_INSTRUMENTS = Const('DRS_INSTRUMENTS',
                        value=base.INSTRUMENTS,
                        dtype=list, source=__NAME__, group=cgroup,
                        description='Currently supported instruments')

# The group this target is set as (set in drs_setup)
DRS_GROUP = Const('DRS_GROUP', value=None, dtype=str, source=__NAME__,
                  group=cgroup,
                  description=('The group this target is set as '
                               '(set in drs_setup)'))
DRS_GROUP_PATH = Const('DRS_GROUP_PATH', value=None, dtype=str, source=__NAME__,
                       group=cgroup,
                       description=('The group path this target is set as '
                                    '(set in drs_setup)'))

# The recipe kind that this parameter dictionary is associated with
#   (i.e. reference-calib, night-calib, obj-science, obj-tellu)
DRS_RECIPE_KIND = Const('DRS_RECIPE_KIND', value=None, dtype=str,
                        source=__NAME__, group=cgroup,
                        description=('The recipe kind that this parameter '
                                     'dictionary is associated with (i.e. '
                                     'reference-calib, night-calib, obj-science, '
                                     'obj-tellu)'))

# The recipe type that this parameter dictionary is associated with
#   (i.e. recipe, tool, processing)
DRS_RECIPE_TYPE = Const('DRS_RECIPE_TYPE', value=None, dtype=str,
                        source=__NAME__, group=cgroup,
                        description=('The recipe type that this parameter '
                                     'dictionary is associated with  '
                                     '(i.e. recipe, tool, processing)'))

# Flag for ref recipe associated with this param set
IS_REF = Const('IS_REFERENCE', value=False, dtype=bool, source=__NAME__,
               group=cgroup,
               description=('Flag for reference recipe associated with '
                            'this param set'))

# =============================================================================
# Instrument/Observatory Constants
# =============================================================================
cgroup = 'Instrument/Observatory Constants'
# Instrument Name
INSTRUMENT = Const('INSTRUMENT', value='None', dtype=str,
                   options=DRS_INSTRUMENTS.value, source=__NAME__, group=cgroup,
                   description='Instrument Name')

# Defines the longitude West is negative
OBS_LONG = Const('OBS_LONG', value=None, dtype=float, source=__NAME__,
                 group=cgroup,
                 description='Defines the longitude West is negative')
#  Defines the latitude North (deg)
OBS_LAT = Const('OBS_LAT', value=None, dtype=float, source=__NAME__,
                group=cgroup, description='Defines the latitude North (deg)')
#  Defines the CFHT altitude (m)
OBS_ALT = Const('OBS_LAT', value=None, dtype=float, source=__NAME__,
                group=cgroup)

# =============================================================================
# DRS INTERNAL PATHS
# =============================================================================
cgroup = 'DRS INTERNAL PATHS'
#   User-config default location (if environmental variable not set)
#   this is relative to the package level
DRS_USER_DEFAULT = Const('DRS_USER_DEFAULT', value='../config/', dtype=str,
                         source=__NAME__, group=cgroup,
                         description=('User-config default location '
                                      '(if environmental variable not set) '
                                      'this is relative to the package level'),
                         output=False)

#   where to store internal data
DRS_MOD_DATA_PATH = Const('DRS_MOD_DATA_PATH', value='./data/', dtype=str,
                          source=__NAME__, group=cgroup,
                          description='where to store internal data',
                          output=False)

#   where instrument configuration files are stored (do not change here)
DRS_MOD_INSTRUMENT_CONFIG = Const('DRS_MOD_INSTRUMENT_CONFIG', dtype=str,
                                  value=base.CONST_PATH,
                                  source=__NAME__, group=cgroup,
                                  description=('where instrument configuration '
                                               'files are stored (do not '
                                               'change here)'),
                                  output=False)

#   where the core configuration files are stored (do not change here)
DRS_MOD_CORE_CONFIG = Const('DRS_MOD_CORE_CONFIG', dtype=str,
                            value=base.CORE_PATH,
                            source=__NAME__, group=cgroup,
                            description=('where the core configuration files '
                                         'are stored (do not change here)'),
                            output=False)

# where the instrument recipes are stored
DRS_INSTRUMENT_RECIPE_PATH = Const('DRS_INSTRUMENT_RECIPE_PATH', dtype=str,
                                   value=None, source=__NAME__, group=cgroup,
                                   description=('where the instrument recipes '
                                                'are stored'),
                                   output=False)

# where the default recipes are stored
DRS_DEFAULT_RECIPE_PATH = Const('DRS_DEFAULT_RECIPE_PATH', dtype=str,
                                value='./recipes/', source=__NAME__,
                                group=cgroup,
                                description=('where the default recipes are '
                                             'stored'),
                                output=False)

#  where the bad pixel data are stored (within assets directory)
DRS_BADPIX_DATA = Const('DRS_BADPIX_DATA', dtype=str, source=__NAME__,
                        group=cgroup,
                        description=('where the bad pixel data are stored '
                                     '(within assets directory)'),
                        output=False)

# where the calibration data are stored (within assets directory)
DRS_CALIB_DATA = Const('DRS_CALIB_DATA', dtype=str, source=__NAME__,
                       group=cgroup,
                       description=('where the calibration data are stored '
                                    '(within assets directory)'),
                       output=False)

# where the wave data are stored (within assets directory)
DRS_WAVE_DATA = Const('DRS_WAVE_DATA', dtype=str, source=__NAME__, group=cgroup,
                      description='where the wave data are stored '
                                  '(within assets directory)',
                      output=False)

# where the assets directory is (relative to apero module)
# TODO: remove and replace with online link / user link
DRS_RESET_ASSETS_PATH = Const('DRS_RESET_ASSETS_PATH', dtype=str,
                              source=__NAME__, group=cgroup,
                              description=('where the assets directory is '
                                           '(relative to apero module)'),
                              output=False)

# where the reset data are stored (within assets directory)
# for calibDB (within assets directory)
DRS_RESET_CALIBDB_PATH = Const('DRS_RESET_CALIBDB_PATH', dtype=str,
                               source=__NAME__, group=cgroup,
                               description=('where the reset data are stored '
                                            '(within assets directory) for '
                                            'calibDB (within assets '
                                            'directory)'),
                               output=False)
# for telluDB (within assets directory)
DRS_RESET_TELLUDB_PATH = Const('DRS_RESET_TELLUDB_PATH', dtype=str,
                               source=__NAME__, group=cgroup,
                               description=('for telluDB (within assets '
                                            'directory)'),
                               output=False)
# for run files (within assets directory)
DRS_RESET_RUN_PATH = Const('DRS_RESET_RUN_PATH', dtype=str, source=__NAME__,
                           group=cgroup,
                           description=('for run files (within assets '
                                        'directory)'),
                           output=False)

# where the pdb rc file is (do not change - just here for use)
DRS_PDB_RC_FILE = Const('DRS_PDB_RC_FILE', value=base.PDB_RC_FILE,
                        dtype=str, source=__NAME__, group=cgroup,
                        description=('where the pdb rc file is (do not change '
                                     '- just here for use)'),
                        output=False)

# what the pdb file should be called (do not change - just here for use)
DRS_PDB_RC_FILENAME = Const('DRS_PDB_RC_FILENAME', value=base.PDB_RC_FILENAME,
                            dtype=str, source=__NAME__, group=cgroup,
                            description=('what the pdb file should be called '
                                         '(do not change - just here for use)'),
                            output=False)

# =============================================================================
# DATABASE SETTINGS
# =============================================================================
cgroup = 'DATABASE SETTINGS'

# Define database directory (relative to assets directory)
DATABASE_DIR = Const('DATABASE_DIR', dtype=str, value='databases/',
                     source=__NAME__, group=cgroup,
                     description=('Define database directory '
                                  '(relative to assets directory)'),
                     output=False)

#   Define the match type for calibDB files
#         match = 'older'  when more than one file for each key will
#                          select the newest file that is OLDER than
#                          time in fitsfilename
#         match = 'closest'  when more than on efile for each key will
#                            select the file that is closest to time in
#                            fitsfilename
#    if two files match with keys and time the key lower in the
#         calibDB file will be used
CALIB_DB_MATCH = Const('CALIB_DB_MATCH', dtype=str, source=__NAME__,
                       value='closest', options=['closest', 'newer', 'older'],
                       group=cgroup,
                       description=('Define the match type for calibDB files'
                                    '\n\tmatch = older when more than one file '
                                    'for each key will select the newest file '
                                    'that is OLDER than time in fitsfilename '
                                    '\n\tmatch = closest when more than on '
                                    'efile for each key will select the file '
                                    'that is closest to time in fitsfilename '
                                    '\n\n\tif two files match with keys and '
                                    'time the key lower in the calibDB file '
                                    'will be used'))

#   Define the match type for telluDB files
#         match = 'older'  when more than one file for each key will
#                          select the newest file that is OLDER than
#                          time in fitsfilename
#         match = 'closest'  when more than on efile for each key will
#                            select the file that is closest to time in
#                            fitsfilename
#    if two files match with keys and time the key lower in the
#         calibDB file will be used
TELLU_DB_MATCH = Const('TELLU_DB_MATCH', dtype=str, source=__NAME__,
                       value='closest', group=cgroup,
                       description=('Define the match type for telluDB files '
                                    '\n\tmatch = older when more than one '
                                    'file for each key will select the newest '
                                    'file that is OLDER than time in '
                                    'fitsfilename '
                                    '\n\tmatch = closest when more than on '
                                    'efile for each key will select the file '
                                    'that is closest to time in fitsfilename '
                                    '\n\n\tif two files match with keys and '
                                    'time the key lower in the calibDB file '
                                    'will be used'))

# =============================================================================
# DISPLAY/LOGGING SETTINGS
# =============================================================================
cgroup = 'DISPLAY/LOGGING SETTINGS'
#   Level at which to print, values can be:
#       'all' - to print all events
#       'info' - to print info/warning/error events
#       'warning' - to print warning/error events
#       'error' - to print only error events
DRS_PRINT_LEVEL = Const('DRS_PRINT_LEVEL', value='all', dtype=str,
                        options=['all', 'info', 'warning', 'error'],
                        source=__NAME__, group=cgroup,
                        description=('Level at which to print, values can be: '
                                     '\n\tall - to print all events '
                                     '\n\tinfo - to print info/warning/error '
                                     'events '
                                     '\n\twarning - to print warning/error '
                                     'events '
                                     '\n\terror - to print only error events'),
                        output=False)

#   Level at which to log in log file, values can be:
#       'all' - to print all events
#       'info' - to print info/warning/error events
#       'warning' - to print warning/error events
#       'error' - to print only error events
DRS_LOG_LEVEL = Const('DRS_LOG_LEVEL', value='all', dtype=str,
                      options=['all', 'info', 'majorwarn', 'minorwarn', 'error'],
                      source=__NAME__, group=cgroup,
                      description=('Level at which to log in log file, '
                                   'values can be: '
                                   '\n\tall - to print all events '
                                   '\n\tinfo - to print info/warning/error '
                                   'events '
                                   '\n\twarning - to print warning/error events'
                                   '\n\terror - to print only error events'),
                      output=False)

#   Coloured logging to standard output (console)
DRS_COLOURED_LOG = Const('DRS_COLOURED_LOG', value=True, dtype=bool,
                         source=__NAME__, group=cgroup,
                         description=('Coloured logging to standard output '
                                      '(console)'),
                         output=False)

#   Theme (DARK or LIGHT)
DRS_THEME = Const('DRS_THEME', value='DARK', dtype=str,
                  options=['DARK', 'LIGHT'], source=__NAME__, group=cgroup,
                  description='Theme (DARK or LIGHT)',
                  output=False)

# Maximum display limit for files/directory when argument error raise
DRS_MAX_IO_DISPLAY_LIMIT = Const('DRS_MAX_IO_DISPLAY_LIMIT', value=15,
                                 dtype=int, source=__NAME__, group=cgroup,
                                 description=('Maximum display limit for '
                                              'files/directory when argument '
                                              'error raise'),
                                 output=False)

# DRS Header string
DRS_HEADER = Const('DRS_HEADER', value=(' ' + '*' * 75), dtype=str,
                   source=__NAME__, group=cgroup,
                   description='DRS Header string',
                   output=False)

# Defines a reference switch, whether to report warnings that are caught in
DRS_LOG_CAUGHT_WARNINGS = Const('DRS_LOG_CAUGHT_WARNINGS',
                                value=True, dtype=bool, source=__NAME__,
                                group=cgroup,
                                description=('Defines a reference switch, '
                                             'whether to report warnings '
                                             'that are caught in'),
                                output=False)

# Defines how python exits, when an exit is required after logging, string
#     input fed into spirouConst.EXIT()
#     if 'sys' exits via sys.exit   - soft exit (ipython Exception)
#     if 'os' exits via os._exit    - hard exit (complete exit)
DRS_LOG_EXIT_TYPE = Const('DRS_LOG_EXIT_TYPE', value='sys', dtype=str,
                          options=['os', 'sys'], source=__NAME__, group=cgroup,
                          description=('Defines how python exits, when an '
                                       'exit is required after logging, string '
                                       'input fed into spirouConst.EXIT() '
                                       '\n\tif sys exits via sys.exit '
                                       '- soft exit (ipython Exception) '
                                       '\n\tif os exits via os._exit - '
                                       'hard exit (complete exit)'),
                          output=False)

# Defines the DRS log format
DRS_LOG_FORMAT = Const('DRS_LOG_FORMAT', value='{0}-{1}|{2}|{3}',
                       dtype=str, source=__NAME__, group=cgroup,
                       description='Defines the DRS log format',
                       output=False)

# Define the log fits file name
DRS_LOG_FITS_NAME = Const('DRS_LOG_FITS_NAME', value='log.fits', dtype=str,
                          source=__NAME__, group=cgroup,
                          description='Define the log fits file name',
                          output=False)

# Define the email address to send emails from
DRS_LOG_EMAIL = Const('DRS_LOG_EMAIL', value='apero.drs@gmail.com', dtype=str,
                      source=__NAME__, group=cgroup,
                      description='Define the email address to send emails '
                                  'from',
                      output=False)

# Define the relative path of the log email oauth file
DRS_LOG_EMAIL_AUTH_PATH = Const('DRS_LOG_EMAIL_AUTH_PATH',
                                value='data/core',
                                dtype=str, source=__NAME__, group=cgroup,
                                description='Define the relative path of the '
                                            'log email oauth file',
                                output=False)


# Define the filename of the log email oauth file
DRS_LOG_EMAIL_AUTH = Const('DRS_LOG_EMAIL_AUTH', value='apero.drs.oauth2.json',
                           dtype=str, source=__NAME__, group=cgroup,
                           description='Define the filename of the log email '
                                       'oauth file',
                           output=False)

# =============================================================================
# PLOT SETTINGS
# =============================================================================
cgroup = 'PLOT SETTINGS'
# Set the default font family for all graphs
#     (i.e. monospace) "None" for not set
DRS_PLOT_FONT_FAMILY = Const('DRS_PLOT_FONT_FAMILY', value='None', dtype=str,
                             source=__NAME__, group=cgroup,
                             description=('Set the default font family for all '
                                          'graphs (i.e. monospace) "None" '
                                          'for not set'),
                             output=False)

# Set the default font weight for all graphs
#     (i.e. bold/normal) "None" for not set
DRS_PLOT_FONT_WEIGHT = Const('DRS_PLOT_FONT_WEIGHT', value='None', dtype=str,
                             source=__NAME__, group=cgroup,
                             description=('Set the default font weight for all '
                                          'graphs (i.e. bold/normal) "None" '
                                          'for not set'),
                             output=False)

# Set the default font size for all graphs (-1 for not set)
DRS_PLOT_FONT_SIZE = Const('DRS_PLOT_FONT_SIZE', value=-1, dtype=int,
                           source=__NAME__, group=cgroup,
                           description=('Set the default font size for all '
                                        'graphs (-1 for not set)'),
                           output=False)

# Set the default plotting style
#     (i.e. seaborn or dark_background) "None" for not set
DRS_PLOT_STYLE = Const('DRS_PLOT_STYLE', value='None', dtype=str,
                       source=__NAME__, group=cgroup,
                       description=('Set the default plotting style (i.e. '
                                    'seaborn or dark_background) "None" '
                                    'for not set'),
                       output=False)

# Set the plot file extension
DRS_PLOT_EXT = Const('DRS_PLOT_EXT', value='pdf', dtype=str, source=__NAME__,
                     group=cgroup,
                     description='Set the plot file extension',
                     output=False)

# Set the summary document extension
DRS_SUMMARY_EXT = Const('DRS_SUMMARY_EXT', value='pdf', dtype=str,
                        source=__NAME__, group=cgroup,
                        description='Set the summary document extension',
                        output=False)

# Set the summary document style
DRS_SUMMARY_STYLE = Const('DRS_SUMMARY_STYLE', value='latex', dtype=str,
                          source=__NAME__, group=cgroup,
                          description='Set the summary document style',
                          output=False)

# =============================================================================
# DEBUG MODES
# =============================================================================
cgroup = 'DEBUG MODES'
# The debug number to print debug log messages
DEBUG_MODE_LOG_PRINT = Const('DEBUG_MODE_LOG_PRINT', value=10, dtype=int,
                             source=__NAME__, group=cgroup,
                             description=('The debug number to print debug '
                                          'log messages'),
                             output=False)

# The debug number to print text entry names on all messages
DEBUG_MODE_TEXTNAME_PRINT = Const('DEBUG_MODE_TEXTNAME_PRINT', value=100,
                                  dtype=int, source=__NAME__, group=cgroup,
                                  description=('The debug number to print text '
                                               'entry names on all messages'),
                                  output=False)

# The debug number to print function definitions
DEBUG_MODE_FUNC_PRINT = Const('DEBUG_MODE_FUNC_PRINT', value=200, dtype=int,
                              source=__NAME__, group=cgroup,
                              description=('The debug number to print function '
                                           'definitions'),
                              output=False)

# =============================================================================
#  End of configuration file
# =============================================================================
