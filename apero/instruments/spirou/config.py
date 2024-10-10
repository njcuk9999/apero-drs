"""
Default parameters for SPIROU

Created on 2019-01-17

@author: cook
"""
from apero.base import base
from apero.instruments.default import config

__NAME__ = 'apero.instruments.spirou.config.py'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# copy the storage
CDict = config.CDict.copy(source='config.instruments.default.config.py')

# -----------------------------------------------------------------------------
# global settings
# -----------------------------------------------------------------------------
# Instrument Name
CDict.set('INSTRUMENT', value='SPIROU', source=__NAME__, author='NJC')

# Defines the longitude West is negative
CDict.set('OBS_LONG', value=-155.468876, source=__NAME__, author='EA')

#  Defines the latitude North (deg)
CDict.set('OBS_LAT', value=19.825252, source=__NAME__, author='EA')

#  Defines the CFHT altitude (m)
CDict.set('OBS_ALT', value=4204, source=__NAME__, author='EA')

# -----------------------------------------------------------------------------
# global settings
# -----------------------------------------------------------------------------
# PLotting mode (0-3)
CDict.set('DRS_PLOT', value=0, source=__NAME__, author='NJC')

# Whether to run in debug mode
#      0: no debug
#      1: basic debugging on errors
#      2: recipes specific (plots and some code runs)
CDict.set('DRS_DEBUG', value=0, source=__NAME__, author='NJC')

# Add snapshot parameter table to reduced outputs
CDict.set('PARAMETER_SNAPSHOT', value=True, source=__NAME__, author='NJC')

# -----------------------------------------------------------------------------
# path settings
# -----------------------------------------------------------------------------
#   Define the root installation directory
CDict.set('DRS_ROOT', value='/drs/spirou/drs/', source=__NAME__, author='NJC')

#   Define the folder with the raw data files in
CDict.set('DRS_DATA_RAW', value='/drs/spirou/data/raw/', source=__NAME__,
          author='NJC')

#   Define the directory that the reduced data should be saved to/read from
CDict.set('DRS_DATA_REDUC', value='/drs/spirou/data/reduced', source=__NAME__,
          author='NJC')

#   Define the directory that the post processed data should be saved to
CDict.set('DRS_DATA_OUT', value='/drs/spirou/data/out', source=__NAME__,
          author='NJC')

#   Define the directory that the calibration files should be saved to/read from
CDict.set('DRS_CALIB_DB', value='/drs/spirou/data/calibDB', source=__NAME__,
          author='NJC')

#   Define the directory that the calibration files should be saved to/read from
CDict.set('DRS_TELLU_DB', value='/drs/spirou/data/telluDB', source=__NAME__,
          author='NJC')

#   Define the directory that the log messages are stored in
CDict.set('DRS_DATA_MSG', value='/drs/spirou/data/msg', source=__NAME__,
          author='NJC')

#   Define the working directory
CDict.set('DRS_DATA_WORKING', value='/drs/spirou/data/tmp', source=__NAME__,
          author='NJC')

#   Define the plotting directory
CDict.set('DRS_DATA_PLOT', value='/drs/spirou/data/plot', source=__NAME__,
          author='NJC')

#   Define the run directory
CDict.set('DRS_DATA_RUN', value='/drs/spirou/data/run', source=__NAME__,
          author='NJC')

#   Define the assets directory
CDict.set('DRS_DATA_ASSETS', value='/drs/spirou/data/assets', source=__NAME__,
          author='NJC')

#   Define the other directory
CDict.set('DRS_DATA_OTHER', value='/drs/spirou/data/other', source=__NAME__,
          author='NJC')

# Define the lbl directory
CDict.set('LBL_PATH', value='/drs/spirou/data/lbl', source=__NAME__,
          author='NJC')

# =============================================================================
# DATABASE SETTINGS
# =============================================================================
# Define database directory (relative to assets directory)
CDict.set('DATABASE_DIR', value='databases/', source=__NAME__, author='NJC')

#   Define the match type for calibDB files
#         match = 'older'  only select calibration files that are older in
#                          time than input file (and then base it on which is
#                          closest in time)
#         match = 'newer'  only select calibration files that are newer in
#                          time than input file (and then base it on which is
#                          closest in time)
#         match = 'closest'  calibration file selection based on which is
#                            closest in time to the input file
#    if two files match with keys and time the key lower in the
#         calibDB file will be used
CDict.set('CALIB_DB_MATCH', value='closest', source=__NAME__, author='NJC')

#   Define the match type for calibDB files
#         match = 'older'  when more than one file for each key will
#                          select the newest file that is OLDER than
#                          time in fitsfilename
#         match = 'closest'  when more than on efile for each key will
#                            select the file that is closest to time in
#                            fitsfilename
#    if two files match with keys and time the key lower in the
#         calibDB file will be used
CDict.set('TELLU_DB_MATCH', value='closest', source=__NAME__, author='NJC')

# =============================================================================
# DRS INTERNAL PATHS
# =============================================================================
# where the instrument recipes are stored
CDict.set('DRS_INSTRUMENT_RECIPE_PATH', value='./recipes/', source=__NAME__,
          author='NJC')

#  where the bad pixel data are stored (within assets directory)
CDict.set('DRS_BADPIX_DATA', value='engineering/', source=__NAME__,
          author='NJC')

# where the calibration data are stored (within assets directory)
CDict.set('DRS_CALIB_DATA', value='calib/', source=__NAME__, author='NJC')

# where the wave data are stored (within assets directory)
CDict.set('DRS_WAVE_DATA', value='calib/', source=__NAME__, author='NJC')

# where the assets directory is (relative to apero module)
# TODO: remove and replace with online link / user link
CDict.set('DRS_RESET_ASSETS_PATH', value='./apero-assets/', source=__NAME__,
          author='NJC')

# where the checksum and critica data (git managed) are stored
CDict.set('DRS_CRITICAL_DATA_PATH', value='./data/', source=__NAME__,
          author='NJC')

# where the reset data are stored (within assets directory)
# for calibDB (within assets directory)
CDict.set('DRS_RESET_CALIBDB_PATH', value='reset/calibdb/', source=__NAME__,
          author='NJC')
# for telluDB (within assets directory)
CDict.set('DRS_RESET_TELLUDB_PATH', value='reset/telludb/', source=__NAME__,
          author='NJC')
# for run files (within assets directory)
CDict.set('DRS_RESET_RUN_PATH', value='reset/runs/', source=__NAME__,
          author='NJC')

# =============================================================================
#  End of configuration file
# =============================================================================