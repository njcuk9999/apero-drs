"""
Default parameters for NIRPS HA

Created on 2019-01-17

@author: cook
"""
from aperocore.base import base
from apero.instruments.default import config
from apero.base import base as apero_base

__NAME__ = 'apero.instruments.nirps_ha.config.py'
__PACKAGE__ = apero_base.__PACKAGE__
__version__ = apero_base.__version__
__authors__ = apero_base.__authors__
__date__ = apero_base.__date__
__release__ = apero_base.__release__
# copy the storage
CDict = config.CDict.copy(source=__NAME__)

# -----------------------------------------------------------------------------
# global settings
# -----------------------------------------------------------------------------
cgroup = 'GLOBAL'
# PLotting mode (0-3)
CDict.set('PLOT_MODE', value=0, source=__NAME__, author='NJC', group=cgroup)

# Whether to run in debug mode
#      0: no debug
#      1: basic debugging on errors
#      2: recipes specific (plots and some code runs)
CDict.set('DEBUG', value=0, source=__NAME__, author='NJC', group=cgroup)

# Add snapshot parameter table to reduced outputs
CDict.set('PSNAPSHOT', value=True, source=__NAME__, author='NJC',
          group=cgroup)

# -----------------------------------------------------------------------------
# Instrument/Observatory Constants
# -----------------------------------------------------------------------------
cgroup = 'OBS'
# Instrument Name
CDict.set('INSTRUMENT', value='NIRPS_HA', source=__NAME__, author='NJC',
          group=cgroup)

# Defines the longitude West is negative
CDict.set('LONG', value=-70.731330408, source=__NAME__, author='NJC',
          group=cgroup)

#  Defines the latitude North (deg)
CDict.set('LAT', value=-29.261165622, source=__NAME__, author='NJC',
          group=cgroup)

#  Defines the telescope altitude (m)
CDict.set('ALT', value=2400, source=__NAME__, author='NJC',
          group=cgroup)

#  Define the telescopes time zone (from pytz.all_timezones)
CDict.set('TIMEZONE', value='Chile/Continental', source=__NAME__,
          author='NJC', group=cgroup)

# -----------------------------------------------------------------------------
# path settings
# -----------------------------------------------------------------------------
cgroup = 'PATH'
#   Define the root installation directory
CDict.set('ROOT', value='/drs/nirps_ha/drs/', source=__NAME__, author='NJC',
          group=cgroup)

#   Define the folder with the raw data files in
CDict.set('RAW', value='/drs/nirps_ha/data/raw/', source=__NAME__,
          author='NJC', group=cgroup)

#   Define the directory that the reduced data should be saved to/read from
CDict.set('RED', value='/drs/nirps_ha/data/reduced', source=__NAME__,
          author='NJC', group=cgroup)

#   Define the directory that the post processed data should be saved to
CDict.set('OUT', value='/drs/nirps_ha/data/out', source=__NAME__,
          author='NJC', group=cgroup)

#   Define the directory that the calibration files should be saved to/read from
CDict.set('CALIB', value='/drs/nirps_ha/data/calibDB', source=__NAME__,
          author='NJC', group=cgroup)

#   Define the directory that the calibration files should be saved to/read from
CDict.set('TELLU', value='/drs/nirps_ha/data/telluDB', source=__NAME__,
          author='NJC', group=cgroup)

#   Define the directory that the log messages are stored in
CDict.set('LOG', value='/drs/nirps_ha/data/msg', source=__NAME__,
          author='NJC', group=cgroup)

#   Define the working directory
CDict.set('PP', value='/drs/nirps_ha/data/tmp', source=__NAME__,
          author='NJC', group=cgroup)

#   Define the plotting directory
CDict.set('PLOT', value='/drs/nirps_ha/data/plot', source=__NAME__,
          author='NJC', group=cgroup)

#   Define the run directory
CDict.set('RUN', value='/drs/nirps_ha/data/run', source=__NAME__,
          author='NJC', group=cgroup)

#   Define the assets directory
CDict.set('ASSETS', value='/drs/nirps_ha/data/assets', source=__NAME__,
          author='NJC', group=cgroup)

#   Define the other directory
CDict.set('OTHER', value='/drs/nirps_ha/data/other', source=__NAME__,
          author='NJC', group=cgroup)

# Define the lbl directory
CDict.set('LBL', value='/drs/nirps_ha/data/lbl', source=__NAME__,
          author='NJC', group=cgroup)

# =============================================================================
# DATABASE SETTINGS
# =============================================================================
group = 'DB'
# Define database directory (relative to assets directory)
CDict.set('DIR', value='databases/', source=__NAME__, author='NJC',
          group=cgroup)

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
CDict.set('CALIB_MATCH', value='closest', source=__NAME__, author='NJC',
          group=cgroup)

#   Define the match type for calibDB files
#         match = 'older'  when more than one file for each key will
#                          select the newest file that is OLDER than
#                          time in fitsfilename
#         match = 'closest'  when more than on efile for each key will
#                            select the file that is closest to time in
#                            fitsfilename
#    if two files match with keys and time the key lower in the
#         calibDB file will be used
CDict.set('TELLU_MATCH', value='closest', source=__NAME__, author='NJC',
          group=cgroup)

# =============================================================================
# DRS INTERNAL PATHS
# =============================================================================
cgroup = 'IPATH'
#  where the bad pixel data are stored (within assets directory)
CDict.set('BADPIX', value='engineering/', source=__NAME__,
          author='NJC', group=cgroup)

# where the calibration data are stored (within assets directory)
CDict.set('CALIB', value='calib/', source=__NAME__, author='NJC',
          group=cgroup)

# where the wave data are stored (within assets directory)
CDict.set('WAVE', value='calib/', source=__NAME__, author='NJC',
          group=cgroup)

# where the assets directory is (relative to apero module)
# TODO: remove and replace with online link / user link
CDict.set('RESET_ASSETS', value='./apero-assets/', source=__NAME__,
          author='NJC', group=cgroup)

# where the checksum and critica data (git managed) are stored
CDict.set('CDATA', value='./data/', source=__NAME__,
          author='NJC', group=cgroup)

# where the reset data are stored (within assets directory)
# for calibDB (within assets directory)
CDict.set('RESET_CALIB', value='reset/calibdb/', source=__NAME__,
          author='NJC', group=cgroup)
# for telluDB (within assets directory)
CDict.set('RESET_TELLU', value='reset/telludb/', source=__NAME__,
          author='NJC', group=cgroup)
# for run files (within assets directory)
CDict.set('RESET_RUN', value='reset/runs/', source=__NAME__,
          author='NJC', group=cgroup)

# =============================================================================
#  End of configuration file
# =============================================================================
