#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO Recipe definitions for NO INSTRUMENT

Created on 2018-10-31 at 18:06

@author: cook
"""
from apero import lang
from apero.base import base
from apero.core.constants import path_definitions
from apero.core.utils import drs_recipe

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'config.core.default.recipe_definitions.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Help
textentry = lang.textentry

# =============================================================================
# Commonly used arguments
# =============================================================================
obs_dir = dict(name='obs_dir', dtype='obs_dir',
               helpstr=textentry('OBS_DIR_HELP'))
# -----------------------------------------------------------------------------
plot = dict(name='--plot', dtype=int, helpstr=textentry('PLOT_HELP'),
            default_ref='DRS_PLOT', minimum=0, maximum=4)

# =============================================================================
# List of usable recipes
# =============================================================================
drs_recipe = drs_recipe.DrsRecipe

# Below one must define all recipes and put into the "recipes" list
astrometric = drs_recipe(__INSTRUMENT__)
changelog = drs_recipe(__INSTRUMENT__)
explorer = drs_recipe(__INSTRUMENT__)
get_files = drs_recipe(__INSTRUMENT__)
go_recipe = drs_recipe(__INSTRUMENT__)
database_mgr = drs_recipe(__INSTRUMENT__)
langdb = drs_recipe(__INSTRUMENT__)
listing = drs_recipe(__INSTRUMENT__)
stats = drs_recipe(__INSTRUMENT__)
precheck = drs_recipe(__INSTRUMENT__)
processing = drs_recipe(__INSTRUMENT__)
remake_db = drs_recipe(__INSTRUMENT__)
remake_doc = drs_recipe(__INSTRUMENT__)
req_check = drs_recipe(__INSTRUMENT__)
reset = drs_recipe(__INSTRUMENT__)
run_ini = drs_recipe(__INSTRUMENT__)
static = drs_recipe(__INSTRUMENT__)
trigger = drs_recipe(__INSTRUMENT__)
validate = drs_recipe(__INSTRUMENT__)
visulise = drs_recipe(__INSTRUMENT__)

# push into a list
recipes = [astrometric, changelog, database_mgr, explorer,
           get_files, go_recipe, langdb, listing,
           precheck, processing,
           remake_db, remake_doc, req_check, reset, run_ini,
           static, stats, trigger, validate, visulise]

# =============================================================================
# Recipe definitions
# =============================================================================
# Each recipe requires the following:
#    recipe = drs_recipe()  [DEFINED ABOVE]
#
#    recipe.name                the full name of the python script file
#    recipe.in_block_str        the input directory [raw/tmp/reduced]
#    recipe.out_block_str       the output directory [raw/tmp/reduced]
#    recipe.description         the description (for help file)
#
#    arguments:
#         recipe.arg(name=[STRING],             the name for the argument
#                    pos=[INT],                 the expected position
#                    dtype=[STRING or None],    the arg type (see below)
#                    helpstr=[STRING]           the help string for the argument
#                    )
#
#   options:
#         recipe.kwarg(name=[STRING],           the name for the argument
#                      dtype=[STRING]           the kwarg type (see below)
#                      options=[LIST OF STRINGS], the options allowed
#                      helpstr=[STRING]         the help string for the argument
#                      )
#
#    Note arg/kwarg types allowed:
#       directory, files, file, bool, options, switch
#
# -----------------------------------------------------------------------------
# generic recipe
# -----------------------------------------------------------------------------
raw_recipe = drs_recipe(__INSTRUMENT__)
pp_recipe = drs_recipe(__INSTRUMENT__)
out_recipe = drs_recipe(__INSTRUMENT__)

# -----------------------------------------------------------------------------
# apero_astrometrics.py
# -----------------------------------------------------------------------------
astrometric.name = 'apero_astrometrics.py'
astrometric.shortname = 'ASTROM'
astrometric.instrument = __INSTRUMENT__
astrometric.description = textentry('ASTROMETRIC_DESCRIPTION')
astrometric.recipe_type = 'tool'
astrometric.recipe_kind = 'user'
astrometric.set_arg(pos=0, name='objects', dtype=str,
                    helpstr=textentry('ASTROMETRIC_OBJ_HELP'))
astrometric.set_kwarg(name='--overwrite', dtype='switch', default=False,
                      helpstr=textentry('ASTROMETRIC_OVERWRITE_HELP'))
astrometric.set_kwarg(name='--getteff', dtype='switch', default=False,
                      helpstr=textentry('ASTROMETRIC_GETTEFF_HELP'))
astrometric.set_kwarg(name='--nopmrequired', dtype='switch', default=False,
                      helpstr=textentry('ASTROMETRIC_NOPM_REQ_HELP'))
astrometric.set_kwarg(name='--test', dtype='switch', default=False,
                      helpstr=textentry('ASTROMETRIC_TEST_HELP'))
astrometric.set_kwarg(name='--check', dtype='switch', default=False,
                      helpstr='Check object database for basic errors')
astrometric.description_file = 'apero_astrometrics.rst'

# -----------------------------------------------------------------------------
# apero_changelog.py
# -----------------------------------------------------------------------------
changelog.name = 'apero_changelog.py'
changelog.shortname = 'CLOG'
changelog.instrument = __INSTRUMENT__
changelog.description = textentry('CHANGELOG_DESCRIPTION')
changelog.recipe_type = 'nolog-tool'
changelog.recipe_kind = 'admin'
changelog.set_arg(pos=0, name='preview', dtype='bool',
                  helpstr=textentry('PREVIEW_HELP'))
changelog.description_file = 'apero_changelog.rst'

# -----------------------------------------------------------------------------
# apero_database.py
# -----------------------------------------------------------------------------
database_mgr.name = 'apero_database.py'
database_mgr.shortname = 'DBMGR'
database_mgr.instrument = __INSTRUMENT__
database_mgr.description = textentry('DBMGR_DESCRIPTION')
database_mgr.recipe_type = 'nolog-tool'
database_mgr.recipe_kind = 'admin'
database_mgr.set_kwarg(name='--kill', dtype='switch', default=False,
                       helpstr=textentry('DBMGR_KILLARG_HELP'))
database_mgr.set_kwarg(name='--dbkind', dtype=str, default='all',
                       options=['all', 'calib', 'tellu', 'findex', 'log',
                                'astrom', 'reject', 'lang'],
                       helpstr='Database kind to update or reset. Must use in'
                               'conjuction with --update or --reset')
database_mgr.set_kwarg(name='--update', dtype='switch', default=False,
                       helpstr=textentry('DBMGR_UPDATE_HELP'))
database_mgr.set_kwarg(name='--reset', dtype='switch', default=False,
                       helpstr=textentry('DBMGR_RESET_HELP'))
database_mgr.set_kwarg(name='--csv', dtype=str, default='None',
                       helpstr=textentry('DBMGR_CSVARG_HELP'))
database_mgr.set_kwarg(name='--exportdb', dtype='options', default='None',
                       options=base.DATABASE_NAMES,
                       helpstr=textentry('DBMGR_EXPORTDB_HELP'))
database_mgr.set_kwarg(name='--importdb', dtype='options', default='None',
                       options=base.DATABASE_NAMES,
                       helpstr=textentry('DBMGR_IMPORTDB_HELP'))
database_mgr.set_kwarg(name='--join', dtype='options', default='replace',
                       options=['replace', 'append'],
                       helpstr=textentry('DBMGR_JOIN_HELP'))
database_mgr.set_kwarg(name='--delete', dtype='switch', default=False,
                       helpstr=textentry('DBMGR_DELETE_HELP'))

database_mgr.description_file = 'apero_database.rst'

# -----------------------------------------------------------------------------
# apero_documentation.py
# -----------------------------------------------------------------------------
remake_doc.name = 'apero_documentation.py'
remake_doc.instrument = __INSTRUMENT__
remake_doc.shortname = 'DOC'
remake_doc.description = textentry('REMAKE_DOC_DESCRIPTION')
remake_doc.recipe_type = 'nolog-tool'
remake_doc.recipe_kind = 'admin'
remake_doc.set_kwarg(name='--instruments', dtype=str, default='ALL',
                     helpstr=textentry('REMAKE_INSTRUMENT_HELP'))
remake_doc.set_kwarg(name='--compile', dtype='switch', default=False,
                     helpstr=textentry('REMAKE_DOC_COMPILE_HELP'))
remake_doc.set_kwarg(name='--upload', dtype='switch', default=False,
                     helpstr=textentry('REMAKE_DOC_UPLOADARG_HELP'))
remake_doc.set_kwarg(name='--all', dtype='switch', default=False,
                     helpstr='--filedef --recipedef and --recipeseq')
remake_doc.set_kwarg(name='--filedef', dtype='switch', default=False,
                     helpstr=textentry('REMAKE_DOC_FILEDEF_HELP'))
remake_doc.set_kwarg(name='--recipedef', dtype='switch', default=False,
                     helpstr=textentry('REMAKE_DOC_RECIPEDEF_HELP'))
remake_doc.set_kwarg(name='--recipeseq', dtype='switch', default=False,
                     helpstr=textentry('REMAKE_DOC_RECIPESEQ_HELP'))
remake_doc.set_kwarg(name='--mode', dtype='options', default='both',
                     options=['both', 'html', 'latex'],
                     helpstr=textentry('REMAKE_MODE_HELP'))
remake_doc.description_file = 'apero_documentation.rst'

# -----------------------------------------------------------------------------
# apero_explorer.py
# -----------------------------------------------------------------------------
explorer.name = 'apero_explorer.py'
explorer.shortname = 'EXPLO'
explorer.instrument = __INSTRUMENT__
explorer.description = textentry('EXPLORER_DESCRIPTION')
explorer.recipe_type = 'nolog-tool'
explorer.recipe_kind = 'user'
explorer.set_kwarg(name='--hash', default=False, dtype='switch',
                   helpstr=textentry('EXPLORER_HASH'))
explorer.set_kwarg(name='--recipe', default='None', dtype=str,
                   helpstr=textentry('EXPLORER_RECIPE'))
explorer.set_kwarg(name='--flagnum', default=0, dtype=int,
                   helpstr=textentry('EXPLORER_FLAGNUM'))

explorer.description_file = 'apero_explorer.rst'

# -----------------------------------------------------------------------------
# apero_get.py
# -----------------------------------------------------------------------------
get_files.name = 'apero_get.py'
get_files.shortname = 'GET'
get_files.instrument = __INSTRUMENT__
get_files.description = textentry('GET_DESCRIPTION')
get_files.recipe_type = 'nolog-tool'
get_files.recipe_kind = 'user'
get_files.set_kwarg(name='--gui', default=False, dtype='switch',
                    helpstr=textentry('GET_GUI_HELP'))
get_files.set_kwarg(name='--outpath', dtype=str, default='None',
                    helpstr=textentry('GET_OUTPATH_HELP'))
get_files.set_kwarg(name='--symlinks', default=False, dtype='switch',
                    helpstr=textentry('GET_SYMLINKS_HELP'))
get_files.set_kwarg(name='--tar', default=False, dtype='switch',
                    helpstr='Whether to create a tar instead of copying files.'
                            'Must also provide the --tarfile argument')
get_files.set_kwarg(name='--tarfile', default='None', dtype=str,
                    helpstr='The name of the tar file to create. Must also '
                            'provide the --tar argument')
# file filters
get_files.set_kwarg(name='--objnames', dtype=str, default='None',
                    helpstr=textentry('GET_OBJNAME_HELP'))
get_files.set_kwarg(name='--dprtypes', dtype=str, default='None',
                    helpstr=textentry('GET_DPRTYPES_HELP'))
get_files.set_kwarg(name='--outtypes', dtype=str, default='None',
                    helpstr=textentry('GET_OUTTYPES_HELP'))
get_files.set_kwarg(name='--fibers', dtype=str, default='None',
                    helpstr=textentry('GET_FIBERS_HELP'))
get_files.set_kwarg(name='--since', default='None', dtype=str,
                    helpstr='Only get files processed since a certain date '
                            'YYYY-MM-DD hh:mm:ss')
get_files.set_kwarg(name='--latest', default='None', dtype=str,
                    helpstr='Only get files processed since a certain date '
                            'YYYY-MM-DD hh:mm:ss')
get_files.set_kwarg(name='--obsdir', default='None', dtype=str,
                    helpstr='Only get files from a certain observation '
                            'directory')
get_files.set_kwarg(name='--pi_name', default='None', dtype=str,
                    helpstr='Only get files from a certain PI')
get_files.set_kwarg(name='--runid', default='None', dtype=str,
                    helpstr='Only get files from certain run ids')
# advanced options
get_files.set_kwarg(name='--failedqc', default=False, dtype='switch',
                    helpstr=textentry('GET_FAILEDQC_HELP'))
get_files.set_kwarg(name='--nosubdir', default=False, dtype='switch',
                    helpstr='Do not put files into a sub-directory. '
                            'Only use thes outpath')
get_files.set_kwarg(name='--test', default=False, dtype='switch',
                    helpstr=textentry('GET_TEST_HELP'))

get_files.description_file = 'apero_get.rst'

# -----------------------------------------------------------------------------
# apero_go.py
# -----------------------------------------------------------------------------
go_recipe.name = 'apero_go.py'
go_recipe.shortname = 'GO'
go_recipe.instrument = __INSTRUMENT__
go_recipe.description = textentry('GO_DESCRIPTION')
go_recipe.recipe_type = 'nolog-tool'
go_recipe.recipe_kind = 'user'
go_recipe.set_kwarg(name='--data', dtype='switch', default=False,
                    helpstr=textentry('GO_DATA_HELP'))
go_recipe.set_kwarg(name='--all', dtype='switch', default=False,
                    helpstr='Display all relevant paths')
go_recipe.set_kwarg(name='--setup',  dtype='switch', default=False,
                    helpstr='Display DRS_UCONFIG path')
# loop around block kinds and add arguments
for block in path_definitions.BLOCKS:
    go_recipe.set_kwarg(name=f'--{block.argname}',
                        dtype='switch', default=False,
                        helpstr=textentry('GO_BLOCK_HELP', args=[block.name]))
go_recipe.description_file = 'apero_go.rst'

# -----------------------------------------------------------------------------
# apero_langdb.py
#      (proxy - also need to change apero_langdb.py)
# -----------------------------------------------------------------------------
langdb.name = 'apero_langdb.py'
langdb.shortname = 'LANG'
langdb.instrument = __INSTRUMENT__
langdb.description = textentry('LANGDB_DESC')
langdb.recipe_type = 'nolog-tool'
langdb.recipe_kind = 'admin'
langdb.set_kwarg(name='--find', dtype='switch', default=False,
                 helpstr=textentry('LANGDB_FIND_HELP'))
langdb.set_kwarg(name='--update', altnames=['--upgrade'],
                 dtype='switch', default=False,
                 helpstr=textentry('LANGDB_UPDATE_HELP'))
langdb.set_kwarg(name='--reload', dtype='switch', default=False,
                 helpstr=textentry('LANGDB_RELOAD_HELP'))
langdb.description_file = 'apero_langdb.rst'

# -----------------------------------------------------------------------------
# apero_listing.py
# -----------------------------------------------------------------------------
listing.name = 'apero_listing.py'
listing.shortname = 'LIST'
listing.instrument = __INSTRUMENT__
listing.description = textentry('LISTING_DESC')
listing.recipe_type = 'nolog-tool'
listing.recipe_kind = 'user'
listing.set_kwarg(name='--obs_dir', dtype=str, default='',
                  helpstr=textentry('LISTING_HELP_OBS_DIR'))
listing.set_kwarg(name='--block_kind', dtype='options', default='raw',
                  options=['raw', 'tmp', 'red', 'out'],
                  helpstr=textentry('LISTING_HELP_KIND'))
listing.set_kwarg(name='--exclude_obs_dirs', dtype=str, default='None',
                  helpstr=textentry('PROCESS_EXCLUDE_OBS_DIRS_HELP'))
listing.set_kwarg(name='--include_obs_dirs', dtype=str, default='None',
                  helpstr=textentry('PROCESS_INCLUDE_OBS_DIRS_HELP'))
listing.description_file = 'apero_listing.rst'

# -----------------------------------------------------------------------------
# apero_log_stats.py
# -----------------------------------------------------------------------------
stats.name = 'apero_stats.py'
stats.shortname = 'STAT'
stats.instrument = __INSTRUMENT__
stats.description = textentry('LOGSTAT_DESC')
stats.recipe_type = 'nolog-tool'
stats.recipe_kind = 'user'
stats.set_debug_plots('STATS_TIMING_PLOT', 'STAT_QC_RECIPE_PLOT',
                      'STAT_RAM_PLOT')
stats.set_summary_plots()
stats.set_kwarg(name='--mode', dtype=str, default='red',
                helpstr=textentry('LOGSTAT_MODE_HELP'))
stats.set_kwarg(name='--plog', dtype=str, default='None',
                helpstr=textentry('LOGSTAT_PLOG_HELP'))
stats.set_kwarg(**plot)
stats.set_kwarg(name='--sql', dtype=str, default='None',
                helpstr=textentry('LOGSTAT_SQL_HELP'))
stats.set_kwarg(name='--limit', dtype=int, default=0,
                helpstr='Limit the number of entries in memory plot '
                        '(any recipe with more than this limit is left '
                        'out of stats)')
stats.description_file = 'apero_stats.rst'

# -----------------------------------------------------------------------------
# apero_trigger.py
# -----------------------------------------------------------------------------
trigger.name = 'apero_trigger.py'
trigger.shortname = 'TRIGGER'
trigger.instrument = __INSTRUMENT__
trigger.description = textentry('TRIGGER_DESCRIPTION')
trigger.recipe_type = 'nolog-tool'
trigger.recipe_kind = 'processing'
trigger.set_debug_plots()
trigger.set_summary_plots()
trigger.set_kwarg(name='--indir', dtype=str, default='None',
                  helpstr=textentry('TRIGGER_INDIR_HELP'))
trigger.set_kwarg(name='--reset', dtype='switch', default=False,
                  helpstr=textentry('TRIGGER_RESET_HELP'))
trigger.set_kwarg(name='--ignore', dtype=str, default='None',
                  helpstr=textentry('TRIGGER_IGNORE_HELP'))
trigger.set_kwarg(name='--wait', dtype=int, default=60, minimum=1, maximum=3600,
                  helpstr=textentry('TRIGGER_WAIT_HELP'))
trigger.set_kwarg(name='--calib', dtype=str,
                  default='trigger_night_calibrun.ini',
                  helpstr=textentry('TRIGGER_CALIB_HELP'))
trigger.set_kwarg(name='--sci', dtype=str, default='trigger_night_scirun.ini',
                  helpstr=textentry('TRIGGER_SCI_HELP'))
trigger.set_kwarg(name='--trigger_test', dtype='switch', default=False,
                  helpstr=textentry('TRIGGER_TEST_HELP'))
trigger.description_file = 'apero_trigger.rst'

# -----------------------------------------------------------------------------
# apero_precheck.py
# -----------------------------------------------------------------------------
precheck.name = 'apero_precheck.py'
precheck.shortname = 'PRECHECK'
precheck.instrument = __INSTRUMENT__
precheck.description = textentry('PRECHECK_DESCRIPTION')
precheck.recipe_type = 'tool'
precheck.recipe_kind = 'processing'
precheck.set_arg(pos=0, name='runfile', dtype=str,
                 helpstr=textentry('PROCESS_RUNFILE_HELP'))
precheck.set_kwarg(name='--obs_dir', dtype=str, default='None',
                   helpstr=textentry('PROCESS_OBS_DIR_HELP'))
precheck.set_kwarg(name='--exclude_obs_dirs', dtype=str, default='None',
                   helpstr=textentry('PROCESS_EXCLUDE_OBS_DIRS_HELP'))
precheck.set_kwarg(name='--include_obs_dirs', dtype=str, default='None',
                   helpstr=textentry('PROCESS_INCLUDE_OBS_DIRS_HELP'))
precheck.set_kwarg(name='--no_file_check', dtype='switch', default=False,
                   helpstr=textentry('PRECHECK_NOFILECHECK_HELP'))
precheck.set_kwarg(name='--no_obj_check', dtype='switch', default=False,
                   helpstr=textentry('PRECHECK_NOOBJCHECK_HELP'))
precheck.description_file = 'apero_precheck.rst'

# -----------------------------------------------------------------------------
# apero_processing.py
# -----------------------------------------------------------------------------
processing.name = 'apero_processing.py'
processing.shortname = 'PROC'
processing.instrument = __INSTRUMENT__
processing.description = textentry('PROCESS_DESCRIPTION')
processing.recipe_type = 'tool'
processing.recipe_kind = 'processing'
processing.set_arg(pos=0, name='runfile', dtype=str,
                   helpstr=textentry('PROCESS_RUNFILE_HELP'))
processing.set_kwarg(name='--obs_dir', dtype=str, default='None',
                     helpstr=textentry('PROCESS_OBS_DIR_HELP'))
processing.set_kwarg(name='--filename', dtype=str, default='None',
                     helpstr=textentry('PROCESS_FILENAME_HELP'))
processing.set_kwarg(name='--exclude_obs_dirs', dtype=str, default='None',
                     helpstr=textentry('PROCESS_EXCLUDE_OBS_DIRS_HELP'))
processing.set_kwarg(name='--include_obs_dirs', dtype=str, default='None',
                     helpstr=textentry('PROCESS_INCLUDE_OBS_DIRS_HELP'))
processing.set_kwarg(name='--cores', dtype=str, default='None',
                     helpstr=textentry('PROCESS_CORES_HELP'))
processing.set_kwarg(name='--test', dtype='options', default='None',
                     options=['True', 'False', '1', '0', 'None'],
                     helpstr=textentry('PROCESS_TEST_HELP'))
processing.set_kwarg(name='--trigger', dtype='bool', default=False,
                     helpstr=textentry('PROCESS_TRIGGER_HELP'))
processing.set_kwarg(name='--science_targets', dtype=str, default='None',
                     helpstr=textentry('PROCESS_SCI_TARGETS'))
processing.set_kwarg(name='--telluric_targets', dtype=str, default='None',
                     helpstr=textentry('PROCESS_TELLU_TARGETS'))
processing.set_kwarg(name='--update_objdb', dtype=str, default='None',
                     helpstr=textentry('PROCESS_UPDATE_OBJDB'))
processing.description_file = 'apero_processing.rst'

# -----------------------------------------------------------------------------
# apero_requirements-check.py
# -----------------------------------------------------------------------------
req_check.name = 'apero_dependencies.py'
req_check.shortname = 'DEPEND'
req_check.instrument = __INSTRUMENT__
req_check.description = textentry('DEPENDENCIES_DESCRIPTION')
req_check.recipe_type = 'nolog-tool'
req_check.recipe_kind = 'admin'
req_check.description_file = 'apero_dependencies.rst'

# -----------------------------------------------------------------------------
# apero_reset.py
# -----------------------------------------------------------------------------
reset.name = 'apero_reset.py'
reset.shortname = 'RESET'
reset.instrument = __INSTRUMENT__
reset.description = textentry('RESET_DESCRIPTION')
reset.recipe_type = 'nolog-tool'
reset.recipe_kind = 'user'
reset.set_kwarg(name='--log', dtype='bool', default=True,
                helpstr=textentry('RESET_LOG_HELP'))
reset.set_kwarg(name='--warn', dtype='bool', default=True,
                helpstr=textentry('RESET_WARN_HELP'))
reset.set_kwarg(name='--database_timeout', dtype=int, default=0,
                helpstr=textentry('RESET_DATABASE_TIMEOUT_HELP'))
reset.description_file = 'apero_reset.rst'

# -----------------------------------------------------------------------------
# apero_run_ini.py
# -----------------------------------------------------------------------------
run_ini.name = 'apero_run_ini.py'
run_ini.shortname = 'RUN_INI'
run_ini.instrument = __INSTRUMENT__
run_ini.description = textentry('RUN_INI_DESCRIPTION')
run_ini.recipe_type = 'nolog-tool'
run_ini.recipe_kind = 'admin'
run_ini.set_kwarg(name='--instrument', dtype='options', default='None',
                  options=base.INSTRUMENTS,
                  helpstr=textentry('RUN_INI_INSTRUMENT_HELP'))
run_ini.description_file = 'apero_run_ini.rst'

# -----------------------------------------------------------------------------
# apero_static.py
# -----------------------------------------------------------------------------
static.name = 'apero_static.py'
static.shortname = 'STATIC'
static.instrument = __INSTRUMENT__
static.description = textentry('STATIC_DESCRIPTION')
static.recipe_type = 'nolog-tool'
static.recipe_kind = 'admin'
static.set_kwarg(name='--mode', dtype='options', default='None',
                 options=['LED_FLAT'],
                 helpstr=textentry('STATIC_MODE_HELP'), required=True)
static.description_file = 'apero_static.rst'

# -----------------------------------------------------------------------------
# apero_validate.py
# -----------------------------------------------------------------------------
validate.name = 'apero_validate.py'
validate.shortname = 'VALID'
validate.instrument = __INSTRUMENT__
validate.description = textentry('VALIDATE_DESCRIPTION')
validate.recipe_type = 'nolog-tool'
validate.recipe_kind = 'user'
validate.description_file = 'apero_validate.rst'

# -----------------------------------------------------------------------------
# apero_visu.py
# -----------------------------------------------------------------------------
visulise.name = 'apero_visu.py'
visulise.shortname = 'VISU'
visulise.instrument = __INSTRUMENT__
visulise.description = textentry('VISU_DESCRIPTION')
visulise.recipe_type = 'tool'
visulise.recipe_kind = 'user'
visulise.set_kwarg(name='--mode', dtype='options', default='None',
                   options=['e2ds'], helpstr=textentry('VISU_MODE_HELP'))
visulise.description_file = None
