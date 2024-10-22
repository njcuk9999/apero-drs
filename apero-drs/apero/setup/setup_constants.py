#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-10-22 at 10:10

@author: cook
"""
import string

from apero.setup import drs_setup

# =============================================================================
# Define variables
# =============================================================================
# set the setup argument class
SetupArgument = drs_setup.SetupArgument
# get the instrument list
INSTRUMENTS = drs_setup.INSTRUMENTS
# Get the database modes possible
DB_MODES = drs_setup.__YAML__['DB_MODES']
# Get the available plot modes
PLOT_MODES = drs_setup.__YAML__['PLOT_MODES']
PLOT_DESCS = drs_setup.__YAML__['PLOT_DESCS']
# all punctuation except underscore + whitespaces
EXC_CHARS = string.punctuation.replace('_', ' ').split()

# =============================================================================
# Define setup arguments
# =============================================================================
SARGS = dict()
# APERO profile name
SARGS['name'] = SetupArgument(name='name', argname='--name',
                              default_value=None, dtype='str',
                              required=True,
                              helpstr='The name of the apero profile to create',
                              restricted_chars=EXC_CHARS)
# whether we are updating the current profile or creating a new one
SARGS['update'] = SetupArgument(name='update', argname='--update',
                                default_value=False, dtype='bool', ask=False,
                                helpstr='whether to update current profile')
# the path where the user config files for this apero profile will be stored
SARGS['config_path'] = SetupArgument(name='config_path', argname='--config',
                                     default_value=None, dtype='path',
                                     required=True,
                                     helpstr='The path to the user config '
                                             'directory for this apero profile')
# The instrument we are installing apero for
SARGS['INSTRUMENT'] = SetupArgument(name='INSTRUMENT', argname='--instrument',
                                    default_value=None,
                                    dtype='str', options=INSTRUMENTS,
                                    required=True,
                                    helpstr='The instrument to use')
# -----------------------------------------------------------------------------
# Directory settings
# -----------------------------------------------------------------------------
# The data source we are installing apero for
SARGS['DATADIR'] = SetupArgument(name='DATADIR', argname='--datadir',
                                 default_value=None, dtype='path',
                                 helpstr='The data directory to use (do not '
                                         'set if setting directories '
                                         'separately)',
                                 qstr='Define the data directory to use '
                                      '(leave blank to set directories '
                                      'separately)',
                                 sets=dict(RAWDIR='{DATADIR}/raw',
                                           TMPDIR='{DATADIR}/tmp',
                                           REDDIR='{DATADIR}/red',
                                           CALDIR='{DATADIR}/calib',
                                           TELDIR='{DATADIR}/tellu',
                                           OUTDIR='{DATADIR}/out',
                                           LBLDIR='{DATADIR}/lbl',
                                           LOGDIR='{DATADIR}/log',
                                           PLOTDIR='{DATADIR}/plot',
                                           RUNDIR='{DATADIR}/run',
                                           ASSETSDIR='{DATADIR}/assets',
                                           OTHERDIR='{DATADIR}/other'
                                           ))
# The raw data directory to use (if not using DATADIR)
SARGS['RAWDIR'] = SetupArgument(name='RAWDIR', default_value=None,
                                dtype='path', required=True, depends='DATADIR',
                                helpstr='The raw data directory to use')
# The tmp data directory to use (if not using DATADIR)
SARGS['TMPDIR'] = SetupArgument(name='TMPDIR', default_value=None,
                                dtype='path', required=True, depends='DATADIR',
                                helpstr='The tmp data directory to use')
# The reduced data directory to use (if not using DATADIR)
SARGS['REDDIR'] = SetupArgument(name='REDDIR', default_value=None,
                                dtype='path', required=True, depends='DATADIR',
                                helpstr='The reduced data directory to use')
# the calibration directory to use (if not using DATADIR)
SARGS['CALDIR'] = SetupArgument(name='CALDIR', default_value=None,
                                dtype='path', required=True, depends='DATADIR',
                                helpstr='The calibration data directory to use')
# the telluric directory to use (if not using DATADIR)
SARGS['TELDIR'] = SetupArgument(name='TELDIR', default_value=None,
                                dtype='path', required=True, depends='DATADIR',
                                helpstr='The telluric data directory to use')
# the out directory to use (if not using DATADIR)
SARGS['OUTDIR'] = SetupArgument(name='OUTDIR', default_value=None,
                                dtype='path', required=True, depends='DATADIR',
                                helpstr='The out directory to use')
# the lbl directory to use (if not using DATADIR)
SARGS['LBLDIR'] = SetupArgument(name='LBLDIR', default_value=None,
                                dtype='path', required=True, depends='DATADIR',
                                helpstr='The lbl directory to use')
# the log directory to use (if not using DATADIR)
SARGS['LOGDIR'] = SetupArgument(name='LOGDIR', default_value=None,
                                dtype='path', required=True, depends='DATADIR',
                                helpstr='The log directory to use')
# the plot directory to use (if not using DATADIR)
SARGS['PLOTDIR'] = SetupArgument(name='PLOTDIR', default_value=None,
                                 dtype='path', required=True, depends='DATADIR',
                                 helpstr='The plot directory to use')
# the run directory to use (if not using DATADIR)
SARGS['RUNDIR'] = SetupArgument(name='RUNDIR', default_value=None,
                                dtype='path', required=True, depends='DATADIR',
                                helpstr='The run directory to use')
# the assets directory to use (if not using DATADIR)
SARGS['ASSETSDIR'] = SetupArgument(name='ASSETSDIR', default_value=None,
                                   dtype='path', required=True,
                                   depends='DATADIR',
                                   helpstr='The assets directory to use')
# the other directory to use (if not using DATADIR)
SARGS['OTHERDIR'] = SetupArgument(name='OTHERDIR', default_value=None,
                                  dtype='path', required=True,
                                  depends='DATADIR',
                                  helpstr='The other directory to use')
# whether to always create nre directories without asking user
SARGS['FORCE_DIR_CREATE'] = SetupArgument(name='FORCE_DIR_CREATE',
                                          argname='--always-create',
                                          default_value=False, dtype='bool',
                                          helpstr='Force directory creation',
                                          ask=False)
# -----------------------------------------------------------------------------
# Database settings
# -----------------------------------------------------------------------------
# which database backend to use
SARGS['DATABASE_MODE'] = SetupArgument(name='DATABASE_MODE',
                                       argname='--database-mode',
                                       default_value=DB_MODES[0],
                                       dtype='str',
                                       options=DB_MODES,
                                       helpstr='The database mode to use')
# the database host name
SARGS['DATABASE_HOST'] = SetupArgument(name='DATABASE_HOST',
                                       argname='--database-host',
                                       default_value='localhost',
                                       dtype='str',
                                       helpstr='The database host')
# the database user name
SARGS['DATABASE_USER'] = SetupArgument(name='DATABASE_USER',
                                       argname='--database-user',
                                       default_value='root',
                                       dtype='str',
                                       helpstr='The database user')
# the database password
SARGS['DATABASE_PASS'] = SetupArgument(name='DATABASE_PASS',
                                       argname='--database-pass',
                                       default_value='None',
                                       dtype='str',
                                       helpstr='The database password')
# the database name
SARGS['DATABASE_NAME'] = SetupArgument(name='DATABASE_NAME',
                                       argname='--database-name',
                                       default_value='None',
                                       dtype='str',
                                       helpstr='The database name')
# the sets dictionary for edit_dbtables
edt_sets = dict()
edt_sets['CALIB_DBTABLE'] = 'calib_{NAME}_db'
edt_sets['TELLU_DBTABLE'] = 'tellu_{NAME}_db'
edt_sets['FINDEX_DBTABLE'] = 'findex_{NAME}_db'
edt_sets['ASTROM_DBTABLE'] = 'astrom_{NAME}_db'
edt_sets['REJECT_DBTABLE'] = 'reject_{NAME}_db'
edt_sets['LOG_DBTABLE'] = 'log_{NAME}_db'

# whether to edit table names
SARGS['EDIT_DBTABLES'] = SetupArgument(name='EDIT_DBTABLES',
                                       argname='--edit-table-names',
                                       default_value=False, dtype='bool',
                                       helpstr='Edit table names',
                                       sets=edt_sets)
# calibration table name
SARGS['CALIB_DBTABLE'] = SetupArgument(name='CALIB_DBTABLE',
                                       argname='--calibtable',
                                       default_value='calib',
                                       dtype='str', depends='EDIT_DBTABLES',
                                       helpstr='The calibration table name')
# telluric table name
SARGS['TELLU_DBTABLE'] = SetupArgument(name='TELLU_DBTABLE',
                                       argname='--tellutable',
                                       default_value='tellu',
                                       dtype='str', depends='EDIT_DBTABLES',
                                       helpstr='The telluric table name')
# file index table name
SARGS['FINDEX_DBTABLE'] = SetupArgument(name='FINDEX_DBTABLE',
                                        argname='--findextable',
                                        default_value='findex',
                                        dtype='str', depends='EDIT_DBTABLES',
                                        helpstr='The file index table name')
# astrometric table name
SARGS['ASTROM_DBTABLE'] = SetupArgument(name='ASTROM_DBTABLE',
                                        argname='--astromtable',
                                        default_value='astrom',
                                        dtype='str', depends='EDIT_DBTABLES',
                                        helpstr='The astrometric table name')
# the reject table name
SARGS['REJECT_DBTABLE'] = SetupArgument(name='REJECT_DBTABLE',
                                        argname='--rejecttable',
                                        default_value='reject',
                                        dtype='str', depends='EDIT_DBTABLES',
                                        helpstr='The reject table name')
# the log table name
SARGS['LOG_DBTABLE'] = SetupArgument(name='LOG_DBTABLE',
                                     argname='--logtable',
                                     default_value='log',
                                     dtype='str', depends='EDIT_DBTABLES',
                                     helpstr='The log table name')
# -----------------------------------------------------------------------------
# Other settings
# -----------------------------------------------------------------------------
# set the plot mode
SARGS['PLOT_MODE'] = SetupArgument(name='PLOT_MODE', argname='--plotmode',
                                   default_value=0, dtype='int',
                                   options=PLOT_MODES,
                                   optiondescs=PLOT_DESCS,
                                   helpstr='The plot mode to use')
# whether to start from a clean state
SARGS['CLEAN_START'] = SetupArgument(name='CLEAN_START', argname='--clean',
                                     default_value=True, dtype='bool',
                                     helpstr='Start from a clean state')
# whether to ptompt user a warning when clean start is True
SARGS['CLEAN_PROMPT'] = SetupArgument(name='CLEAN_PROMPT',
                                      argname='--clean-prompt',
                                      default_value=True, dtype='bool',
                                      ask=False,
                                      helpstr='Prompt user before cleaning')

# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
