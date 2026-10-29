#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO Recipe definitions for NO INSTRUMENT

Created on 2018-10-31 at 18:06

@author: cook
"""
from aperocore import drs_lang
from apero.constants import path_definitions
from apero.utils import drs_recipe
from apero.base import base as apero_base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero.instruments.default.recipe_definitions.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = apero_base.__PACKAGE__
__version__ = apero_base.__version__
__authors__ = apero_base.__authors__
__date__ = apero_base.__date__
__release__ = apero_base.__release__
# Get Help
textentry = drs_lang.textentry

# =============================================================================
# Commonly used arguments
# =============================================================================
obs_dir = dict(name='obs_dir', dtype='obs_dir',
               helpstr=textentry('OBS_DIR_HELP'))
# -----------------------------------------------------------------------------
plot = dict(name='--plot', dtype=int, helpstr=textentry('PLOT_HELP'),
            default_ref='GLOBAL.PLOT_MODE', minimum=0, maximum=4)

# =============================================================================
# List of usable recipes
# =============================================================================
DrsRecipe = drs_recipe.DrsRecipe

# Below one must define all recipes and put into the "recipes" list
ari = DrsRecipe(__INSTRUMENT__)
astrometric = DrsRecipe(__INSTRUMENT__)
changelog = DrsRecipe(__INSTRUMENT__)
explorer = DrsRecipe(__INSTRUMENT__)
get_files = DrsRecipe(__INSTRUMENT__)
go_recipe = DrsRecipe(__INSTRUMENT__)
database_mgr = DrsRecipe(__INSTRUMENT__)
db_push = DrsRecipe(__INSTRUMENT__)
langdb = DrsRecipe(__INSTRUMENT__)
listing = DrsRecipe(__INSTRUMENT__)
stats = DrsRecipe(__INSTRUMENT__)
precheck = DrsRecipe(__INSTRUMENT__)
processing = DrsRecipe(__INSTRUMENT__)
queue_recipe = DrsRecipe(__INSTRUMENT__)
remake_doc = DrsRecipe(__INSTRUMENT__)
req_check = DrsRecipe(__INSTRUMENT__)
reject = DrsRecipe(__INSTRUMENT__)
remove = DrsRecipe(__INSTRUMENT__)
reset = DrsRecipe(__INSTRUMENT__)
run_ini = DrsRecipe(__INSTRUMENT__)
static = DrsRecipe(__INSTRUMENT__)
trigger = DrsRecipe(__INSTRUMENT__)
validate = DrsRecipe(__INSTRUMENT__)
visulise = DrsRecipe(__INSTRUMENT__)

# push into a list
recipes = [ari, astrometric, changelog, database_mgr, db_push, explorer,
           get_files, go_recipe, langdb, listing,
           precheck, processing, queue_recipe, remake_doc, req_check,
           reject, remove, reset, run_ini,
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
raw_recipe = DrsRecipe(__INSTRUMENT__)
pp_recipe = DrsRecipe(__INSTRUMENT__)
out_recipe = DrsRecipe(__INSTRUMENT__)


# -----------------------------------------------------------------------------
# apero_ri.py
# -----------------------------------------------------------------------------
ari.name = 'apero_ari.py'
ari.path = 'apero.tools.recipes.bin'
ari.shortname = 'ARI'
ari.instrument = __INSTRUMENT__
ari.description = textentry('ARI_DESCRIPTION')
ari.recipe_type = 'nolog-tool'
ari.recipe_kind = 'user'
ari.set_arg(pos=0, name='profile', dtype=str,
            helpstr=textentry('ARI_PROFILE_HELP'))
ari.set_kwarg(name='--obsdir', dtype=str, default='None',
              helpstr=textentry('OBS_DIR_HELP'))
ari.set_kwarg(name='--reset', dtype='switch',
              helpstr=textentry('ARI_RESET_HELP'))
ari.set_kwarg(name='--redo_objs', dtype='List[str]', default='None',
              helpstr=textentry('ARI_REDO_OBJS_HELP'))
ari.set_kwarg(name='--finder_create', dtype='switch',
              helpstr=textentry('ARI_FINDER_CREATE_HELP'))
ari.set_kwarg(name='--finder_reset', dtype='switch',
              helpstr=textentry('ARI_FINDER_RESET_HELP'))
ari.set_kwarg(name='--profiles', dtype='switch',
              helpstr=textentry('ARI_PROFILES_HELP'))
ari.set_kwarg(name='--cores', dtype=int, default=0,
              helpstr=textentry('ARI_CORES_HELP'))
ari.set_kwarg(name='--filterobjs', dtype=str, default='None',
              helpstr=textentry('ARI_FILTEROBJS_HELP'))

# -----------------------------------------------------------------------------
# apero_astrometrics.py
# -----------------------------------------------------------------------------
astrometric.name = 'apero_astrometrics.py'
astrometric.path = 'apero.tools.recipes.bin'
astrometric.shortname = 'ASTROM'
astrometric.instrument = __INSTRUMENT__
astrometric.description = textentry('ASTROMETRIC_DESCRIPTION')
astrometric.recipe_type = 'tool'
astrometric.recipe_kind = 'user'
astrometric.set_arg(pos=0, name='objects', dtype='List[str]',
                    helpstr=textentry('ASTROMETRIC_OBJ_HELP'))
astrometric.set_kwarg(name='--overwrite', dtype='switch',
                      helpstr=textentry('ASTROMETRIC_OVERWRITE_HELP'))
astrometric.set_kwarg(name='--getteff', dtype='switch',
                      helpstr=textentry('ASTROMETRIC_GETTEFF_HELP'))
astrometric.set_kwarg(name='--nopmrequired', dtype='switch',
                      helpstr=textentry('ASTROMETRIC_NOPM_REQ_HELP'))
astrometric.set_kwarg(name='--test', dtype='switch',
                      helpstr=textentry('ASTROMETRIC_TEST_HELP'))
astrometric.set_kwarg(name='--check', dtype='switch',
                      helpstr=textentry('ASTROMETRIC_CHECK_HELP'))
astrometric.set_kwarg(name='--fileoption', dtype=str, default='None',
                      helpstr=textentry('ASTROMETRIC_FILEOPTION_HELP'))
astrometric.set_kwarg(name='--aliases', dtype=str, default='None',
                      helpstr=textentry('ASTROMETRIC_ALIASES_HELP'))

# -----------------------------------------------------------------------------
# apero_changelog.py
# -----------------------------------------------------------------------------
changelog.name = 'apero_changelog.py'
changelog.path = 'apero.tools.recipes.dev'
changelog.shortname = 'CLOG'
changelog.instrument = __INSTRUMENT__
changelog.description = textentry('CHANGELOG_DESCRIPTION')
changelog.recipe_type = 'nolog-tool'
changelog.recipe_kind = 'admin'
changelog.set_kwarg(name='--preview', dtype='switch',
                    helpstr=textentry('PREVIEW_HELP'))

# -----------------------------------------------------------------------------
# apero_database.py
# -----------------------------------------------------------------------------
database_mgr.name = 'apero_database.py'
database_mgr.path = 'apero.tools.recipes.bin'
database_mgr.shortname = 'DBMGR'
database_mgr.instrument = __INSTRUMENT__
database_mgr.description = textentry('DBMGR_DESCRIPTION')
database_mgr.recipe_type = 'nolog-tool'
database_mgr.recipe_kind = 'admin'
database_mgr.set_kwarg(name='--push', dtype='switch',
                       helpstr=textentry('DATABASE_MGR_PUSH_HELP'))
database_mgr.set_kwarg(name='--pushname', dtype=str, default='*',
                       helpstr=textentry('DATABASE_MGR_PUSHNAME_HELP'))
database_mgr.set_kwarg(name='--kill', dtype='switch',
                       helpstr=textentry('DBMGR_KILLARG_HELP'))
database_mgr.set_kwarg(name='--dbkind', dtype='options', default='all',
                       options=['all', 'calib', 'tellu', 'findex', 'log',
                                'astrom', 'reject', 'lang'],
                       helpstr=textentry('DATABASE_MGR_DBKIND_HELP'))
database_mgr.set_kwarg(name='--update', dtype='switch',
                       helpstr=textentry('DBMGR_UPDATE_HELP'))
database_mgr.set_kwarg(name='--reset', dtype='switch',
                       helpstr=textentry('DBMGR_RESET_HELP'))
database_mgr.set_kwarg(name='--csv', dtype=str, default='None',
                       helpstr=textentry('DBMGR_CSVARG_HELP'))
database_mgr.set_kwarg(name='--exportdb', dtype='options', default='None',
                       options=apero_base.DATABASE_NAMES,
                       helpstr=textentry('DBMGR_EXPORTDB_HELP'))
database_mgr.set_kwarg(name='--importdb', dtype='options', default='None',
                       options=apero_base.DATABASE_NAMES,
                       helpstr=textentry('DBMGR_IMPORTDB_HELP'))
database_mgr.set_kwarg(name='--join', dtype='options', default='replace',
                       options=['replace', 'append'],
                       helpstr=textentry('DBMGR_JOIN_HELP'))
database_mgr.set_kwarg(name='--delete', dtype='switch',
                       helpstr=textentry('DBMGR_DELETE_HELP'))
database_mgr.set_kwarg(name='--cores', dtype=int, default=0,
                       helpstr=textentry('DATABASE_MGR_CORES_HELP'))
database_mgr.set_kwarg(name='--block_kind', dtype=str, default='None',
                       helpstr=textentry('DATABASE_MGR_BLOCK_KIND_HELP'))
# TODO: Add to language database
database_mgr.set_kwarg(name='--keys', dtype='List[str]', default='None',
                       helpstr=textentry('DATABASE_MGR_KEYS_HELP'))
database_mgr.set_kwarg(name='--since', dtype=str, default='None',
                       helpstr=textentry('DATABASE_MGR_SINCE_HELP'))
database_mgr.set_kwarg(name='--before', dtype=str, default='None',
                       helpstr=textentry('DATABASE_MGR_BEFORE_HELP'))
database_mgr.set_kwarg(name='--deletefiles', dtype='switch',
                       helpstr=textentry('DATABASE_MGR_DELETEFILES_HELP'))
database_mgr.set_kwarg(name='--test', dtype='switch',
                       helpstr=textentry('DATABASE_MGR_TEST_HELP'))


# -----------------------------------------------------------------------------
# apero_documentation.py
# -----------------------------------------------------------------------------
remake_doc.name = 'apero_documentation.py'
remake_doc.path = 'apero.tools.recipes.dev'
remake_doc.instrument = __INSTRUMENT__
remake_doc.shortname = 'DOC'
remake_doc.description = textentry('REMAKE_DOC_DESCRIPTION')
remake_doc.recipe_type = 'nolog-tool'
remake_doc.recipe_kind = 'admin'
remake_doc.set_kwarg(name='--instruments', dtype='List[str]', default='ALL',
                     helpstr=textentry('REMAKE_INSTRUMENT_HELP'))
remake_doc.set_kwarg(name='--compile', dtype='switch',
                     helpstr=textentry('REMAKE_DOC_COMPILE_HELP'))
remake_doc.set_kwarg(name='--upload', dtype='switch',
                     helpstr=textentry('REMAKE_DOC_UPLOADARG_HELP'))
remake_doc.set_kwarg(name='--all', dtype='switch',
                     helpstr=textentry('REMAKE_DOC_ALL_HELP'))
remake_doc.set_kwarg(name='--filedef', dtype='switch',
                     helpstr=textentry('REMAKE_DOC_FILEDEF_HELP'))
remake_doc.set_kwarg(name='--recipedef', dtype='switch',
                     helpstr=textentry('REMAKE_DOC_RECIPEDEF_HELP'))
remake_doc.set_kwarg(name='--recipeseq', dtype='switch',
                     helpstr=textentry('REMAKE_DOC_RECIPESEQ_HELP'))
remake_doc.set_kwarg(name='--mode', dtype='options', default='both',
                     options=['both', 'html', 'latex'],
                     helpstr=textentry('REMAKE_MODE_HELP'))
remake_doc.set_kwarg(name='--ari', dtype='switch',
                     helpstr=textentry('REMAKE_DOC_ARI_HELP'))
remake_doc.set_kwarg(name='--docversion', dtype=str, default='None',
                     helpstr=textentry('REMAKE_DOC_DOCVERSION_HELP'))

# -----------------------------------------------------------------------------
# apero_explorer.py
# -----------------------------------------------------------------------------
explorer.name = 'apero_explorer.py'
explorer.path = 'apero.tools.recipes.bin'
explorer.shortname = 'EXPLO'
explorer.instrument = __INSTRUMENT__
explorer.description = textentry('EXPLORER_DESCRIPTION')
explorer.recipe_type = 'nolog-tool'
explorer.recipe_kind = 'user'
explorer.set_kwarg(name='--hash', dtype='switch',
                   helpstr=textentry('EXPLORER_HASH'))
explorer.set_kwarg(name='--recipe', default='None', dtype=str,
                   helpstr=textentry('EXPLORER_RECIPE'))
explorer.set_kwarg(name='--flagnum', default=0, dtype=int,
                   helpstr=textentry('EXPLORER_FLAGNUM'))


# -----------------------------------------------------------------------------
# apero_get.py
# -----------------------------------------------------------------------------
get_files.name = 'apero_get.py'
get_files.path = 'apero.tools.recipes.bin'
get_files.shortname = 'GET'
get_files.instrument = __INSTRUMENT__
get_files.description = textentry('GET_DESCRIPTION')
get_files.recipe_type = 'nolog-tool'
get_files.recipe_kind = 'user'
get_files.set_kwarg(name='--assets', dtype='switch',
                    helpstr=textentry('GET_FILES_ASSETS_HELP'))
get_files.set_kwarg(name='--gui', dtype='switch',
                    helpstr=textentry('GET_GUI_HELP'))
get_files.set_kwarg(name='--dbkind', dtype='options', default='findex',
                    options=['findex', 'calib', 'tellu'])
get_files.set_kwarg(name='--outpath', dtype=str, default='None',
                    helpstr=textentry('GET_OUTPATH_HELP'))
get_files.set_kwarg(name='--symlinks', dtype='switch',
                    helpstr=textentry('GET_SYMLINKS_HELP'))
get_files.set_kwarg(name='--tar', dtype='switch',
                    helpstr=textentry('GET_FILES_TAR_HELP'))
get_files.set_kwarg(name='--tarfile', default='None', dtype=str,
                    helpstr=textentry('GET_FILES_TARFILE_HELP'))
get_files.set_kwarg(name='--cores', default=1, dtype=int,
                    helpstr=textentry('GET_FILES_CORES_HELP'),
                    minimum=1)
# file filters
get_files.set_kwarg(name='--objnames', dtype='List[str]', default='None',
                    helpstr=textentry('GET_OBJNAME_HELP'))
get_files.set_kwarg(name='--dprtypes', dtype='List[str]', default='None',
                    helpstr=textentry('GET_DPRTYPES_HELP'))
get_files.set_kwarg(name='--outtypes', dtype='List[str]', default='None',
                    helpstr=textentry('GET_OUTTYPES_HELP'))
get_files.set_kwarg(name='--fibers', dtype='List[str]', default='None',
                    helpstr=textentry('GET_FIBERS_HELP'))
get_files.set_kwarg(name='--block_kind', dtype=str, default='None',
                    helpstr=textentry('GET_FILES_BLOCK_KIND_HELP'))
get_files.set_kwarg(name='--keynames', dtype='List[str]', default='None',
                    helpstr=textentry('GET_FILES_KEYNAMES_HELP'))
get_files.set_kwarg(name='--since', default='None', dtype=str,
                    helpstr=textentry('GET_FILES_SINCE_HELP'))
get_files.set_kwarg(name='--latest', default='None', dtype=str,
                    helpstr=textentry('GET_FILES_LATEST_HELP'))
get_files.set_kwarg(name='--timekey', default='observed', dtype='options',
                    options=['processed', 'observed'],
                    helpstr=textentry('GET_FILES_TIMEKEY_HELP'))
get_files.set_kwarg(name='--obsdir', default='None', dtype=str,
                    helpstr=textentry('GET_FILES_OBSDIR_HELP'))
get_files.set_kwarg(name='--pi_name', default='None', dtype='List[str]',
                    helpstr=textentry('GET_FILES_PI_NAME_HELP'))
get_files.set_kwarg(name='--runid', default='None', dtype='List[str]',
                    helpstr=textentry('GET_FILES_RUNID_HELP'))
# with group permissions options
get_files.set_kwarg(name='--out_prefix', default='None', dtype=str,
                     helpstr=textentry('GET_FILES_OUT_PREFIX_HELP'))
get_files.set_kwarg(name='--out_suffix', default='None', dtype=str,
                     helpstr=textentry('GET_FILES_OUT_SUFFIX_HELP'))
get_files.set_kwarg(name='--permission_yaml', default='None', dtype=str,
                    helpstr=textentry('GET_FILES_PERMISSION_YAML_HELP'))
get_files.set_kwarg(name='--group_yaml', default='None', dtype=str,
                    helpstr=textentry('GET_FILES_GROUP_YAML_HELP'))
get_files.set_kwarg(name='--group_server', default='None', dtype=str,
                    helpstr=textentry('GET_FILES_GROUP_SERVER_HELP'))
# advanced options
get_files.set_kwarg(name='--failedqc', dtype='switch',
                    helpstr=textentry('GET_FAILEDQC_HELP'))
get_files.set_kwarg(name='--nosubdir', dtype='switch',
                    helpstr=textentry('GET_FILES_NOSUBDIR_HELP'))
get_files.set_kwarg(name='--test', dtype='switch',
                    helpstr=textentry('GET_TEST_HELP'))
get_files.set_kwarg(name='--sizelimit', default=0, dtype=int,
                    helpstr=textentry('GET_FILES_SIZELIMIT_HELP'))
get_files.set_kwarg(name='--nodb', dtype='switch',
                    helpstr=textentry('GET_FILES_NODB_HELP'))
get_files.set_kwarg(name='--nodb_wildcard', default='*', dtype=str,
                    helpstr=textentry('GET_FILES_NODB_WILDCARD_HELP'))
get_files.set_kwarg(name='--mp_mode', default='process', dtype=str,
                    options=['pathos', 'pool', 'process', 'linear'],
                    helpstr=textentry('GET_FILES_MP_MODE_HELP'))


# -----------------------------------------------------------------------------
# apero_go.py
# -----------------------------------------------------------------------------
go_recipe.name = 'apero_go.py'
go_recipe.path = 'apero.tools.recipes.bin'
go_recipe.shortname = 'GO'
go_recipe.instrument = __INSTRUMENT__
go_recipe.description = textentry('GO_DESCRIPTION')
go_recipe.recipe_type = 'nolog-tool'
go_recipe.recipe_kind = 'user'
# IMPORTANT NOTE: These must be added to apero_go.py - it has a quick load
go_recipe.set_kwarg(name='--data', dtype='switch',
                    helpstr=textentry('GO_DATA_HELP'))
go_recipe.set_kwarg(name='--all', dtype='switch',
                    helpstr=textentry('GO_RECIPE_ALL_HELP'))
go_recipe.set_kwarg(name='--setup', dtype='switch',
                    helpstr=textentry('GO_RECIPE_SETUP_HELP'))
go_recipe.set_kwarg(name='--mysql', dtype='switch',
                    helpstr=textentry('GO_RECIPE_MYSQL_HELP'))
# loop around block kinds and add arguments
for block in path_definitions.BLOCKS:
    go_recipe.set_kwarg(name=f'--{block.argname}', dtype='switch',
                        helpstr=textentry('GO_BLOCK_HELP', args=[block.name]))

# -----------------------------------------------------------------------------
# apero_langdb.py
#      (proxy - also need to change apero_langdb.py)
# -----------------------------------------------------------------------------
langdb.name = 'apero_langdb.py'
langdb.path = 'apero.tools.recipes.bin'
langdb.shortname = 'LANG'
langdb.instrument = __INSTRUMENT__
langdb.description = textentry('LANGDB_DESC')
langdb.recipe_type = 'nolog-tool'
langdb.recipe_kind = 'admin'
langdb.set_kwarg(name='--find', dtype='switch',
                 helpstr=textentry('LANGDB_FIND_HELP'))
langdb.set_kwarg(name='--update', altnames=['--upgrade'],
                 dtype='switch',
                 helpstr=textentry('LANGDB_UPDATE_HELP'))
langdb.set_kwarg(name='--reload', dtype='switch',
                 helpstr=textentry('LANGDB_RELOAD_HELP'))

# -----------------------------------------------------------------------------
# apero_listing.py
# -----------------------------------------------------------------------------
listing.name = 'apero_listing.py'
listing.path = 'apero.tools.recipes.bin'
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
listing.set_kwarg(name='--exclude_obs_dirs', dtype='List[str]', default='None',
                  helpstr=textentry('PROCESS_EXCLUDE_OBS_DIRS_HELP'))
listing.set_kwarg(name='--include_obs_dirs', dtype='List[str]', default='None',
                  helpstr=textentry('PROCESS_INCLUDE_OBS_DIRS_HELP'))

# -----------------------------------------------------------------------------
# apero_log_stats.py
# -----------------------------------------------------------------------------
stats.name = 'apero_stats.py'
stats.path = 'apero.tools.recipes.bin'
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
                helpstr=textentry('STATS_LIMIT_HELP'))

# -----------------------------------------------------------------------------
# apero_trigger.py
# -----------------------------------------------------------------------------
trigger.name = 'apero_trigger.py'
trigger.path = 'apero.tools.recipes.bin'
trigger.shortname = 'TRIGGER'
trigger.instrument = __INSTRUMENT__
trigger.description = textentry('TRIGGER_DESCRIPTION')
trigger.recipe_type = 'nolog-tool'
trigger.recipe_kind = 'processing'
trigger.set_debug_plots()
trigger.set_summary_plots()
trigger.set_kwarg(name='--indir', dtype=str, default='None',
                  helpstr=textentry('TRIGGER_INDIR_HELP'))
trigger.set_kwarg(name='--reset', dtype='switch',
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
trigger.set_kwarg(name='--trigger_test', dtype='switch',
                  helpstr=textentry('TRIGGER_TEST_HELP'))

# -----------------------------------------------------------------------------
# apero_precheck.py
# -----------------------------------------------------------------------------
precheck.name = 'apero_precheck.py'
precheck.path = 'apero.tools.recipes.bin'
precheck.shortname = 'PRECHECK'
precheck.instrument = __INSTRUMENT__
precheck.description = textentry('PRECHECK_DESCRIPTION')
precheck.recipe_type = 'tool'
precheck.recipe_kind = 'processing'
precheck.set_arg(pos=0, name='runfile', dtype=str,
                 helpstr=textentry('PROCESS_RUNFILE_HELP'))
precheck.set_kwarg(name='--obs_dir', dtype=str, default='None',
                   helpstr=textentry('PROCESS_OBS_DIR_HELP'))
precheck.set_kwarg(name='--exclude_obs_dirs', dtype='List[str]', default='None',
                   helpstr=textentry('PROCESS_EXCLUDE_OBS_DIRS_HELP'))
precheck.set_kwarg(name='--include_obs_dirs', dtype='List[str]', default='None',
                   helpstr=textentry('PROCESS_INCLUDE_OBS_DIRS_HELP'))
precheck.set_kwarg(name='--no_file_check', dtype='switch',
                   helpstr=textentry('PRECHECK_NOFILECHECK_HELP'))
precheck.set_kwarg(name='--no_obj_check', dtype='switch',
                   helpstr=textentry('PRECHECK_NOOBJCHECK_HELP'))

# -----------------------------------------------------------------------------
# apero_processing.py
# -----------------------------------------------------------------------------
processing.name = 'apero_processing.py'
processing.path = 'apero.tools.recipes.bin'
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
processing.set_kwarg(name='--exclude_obs_dirs', dtype='List[str]', default='None',
                     helpstr=textentry('PROCESS_EXCLUDE_OBS_DIRS_HELP'))
processing.set_kwarg(name='--include_obs_dirs', dtype='List[str]', default='None',
                     helpstr=textentry('PROCESS_INCLUDE_OBS_DIRS_HELP'))
processing.set_kwarg(name='--cores', dtype=str, default='None',
                     helpstr=textentry('PROCESS_CORES_HELP'))
processing.set_kwarg(name='--test', dtype='options', default='None',
                     options=['True', 'False', '1', '0', 'None'],
                     helpstr=textentry('PROCESS_TEST_HELP'))
processing.set_kwarg(name='--trigger', dtype='switch',
                     helpstr=textentry('PROCESS_TRIGGER_HELP'))
processing.set_kwarg(name='--science_targets', dtype='List[str]', default='None',
                     helpstr=textentry('PROCESS_SCI_TARGETS'))
processing.set_kwarg(name='--telluric_targets', dtype='List[str]', default='None',
                     helpstr=textentry('PROCESS_TELLU_TARGETS'))
processing.set_kwarg(name='--update_objdb', dtype='switch',
                     helpstr=textentry('PROCESS_UPDATE_OBJDB'))
processing.set_kwarg(name='--to_file', dtype=str, default='None',
                     helpstr=textentry('PROCESS_TO_FILE_HELP'))
processing.set_kwarg(name='--verify', dtype='switch',
                     helpstr=textentry('PROCESS_VERIFY_HELP'))
processing.set_kwarg(name='--queue_mode', altnames=['--queue'],
                     dtype='switch',
                     helpstr=textentry('PROCESSING_QUEUE_MODE_HELP'))

# -----------------------------------------------------------------------------
# apero_db_push.py
# -----------------------------------------------------------------------------
db_push.name = 'apero_db_push.py'
db_push.path = 'apero.tools.recipes.bin'
db_push.shortname = 'DBPUSH'
db_push.instrument = __INSTRUMENT__
db_push.description = (textentry('DB_PUSH_DESCRIPTION'))
db_push.recipe_type = 'nolog-tool'
db_push.recipe_kind = 'processing'

# -----------------------------------------------------------------------------
# apero_queue.py
# -----------------------------------------------------------------------------
queue_recipe.name = 'apero_queue.py'
queue_recipe.path = 'apero.tools.recipes.bin'
queue_recipe.shortname = 'QUEUE'
queue_recipe.instrument = __INSTRUMENT__
queue_recipe.description = (textentry('QUEUE_RECIPE_DESCRIPTION'))
queue_recipe.recipe_type = 'nolog-tool'
queue_recipe.recipe_kind = 'processing'
queue_recipe.set_arg(pos=0, name='mode', dtype='options',
                     options=['run', 'batch', 'chain', 'status', 'gui',
                              'reset', 'init', 'action', 'system'],
                     helpstr=textentry('QUEUE_RECIPE_MODE_HELP'))
queue_recipe.set_kwarg(name='--cores', dtype=str, default='None',
                       helpstr=textentry('QUEUE_RECIPE_CORES_HELP'))
queue_recipe.set_kwarg(name='--mpmode', dtype='options', default='None',
                       options=['process', 'pool', 'linear', 'None'],
                       helpstr=textentry('QUEUE_RECIPE_MPMODE_HELP'))
queue_recipe.set_kwarg(name='--ntasks', dtype=str, default='None',
                       helpstr=textentry('QUEUE_RECIPE_NTASKS_HELP'))
queue_recipe.set_kwarg(name='--qstate', dtype='options', default='None',
                       options=['pending', 'running', 'complete', 'failed',
                                'all', 'None'],
                       helpstr=textentry('QUEUE_RECIPE_QSTATE_HELP'))
queue_recipe.set_kwarg(name='--qaction', dtype='options', default='None',
                       options=['move_to_pending',
                                'move_all_failed_to_pending',
                                'move_all_complete_to_pending',
                                'stop_all_running',
                                'stop_to_pending',
                                'stop_to_complete',
                                'stop_to_failed',
                                'clear_all_pending', 'fail_stale_running',
                                'None'],
                       helpstr=textentry('QUEUE_RECIPE_QACTION_HELP'))
queue_recipe.set_kwarg(name='--rows', dtype=str, default='None',
                       helpstr=textentry('QUEUE_RECIPE_ROWS_HELP'))
queue_recipe.set_kwarg(name='--host', dtype=str, default='None',
                       helpstr=textentry('QUEUE_RECIPE_HOST_HELP'))
queue_recipe.set_kwarg(name='--port', dtype=str, default='None',
                       helpstr=textentry('QUEUE_RECIPE_PORT_HELP'))
queue_recipe.set_kwarg(name='--qpath', dtype=str, default='None',
                       helpstr=textentry('QUEUE_RECIPE_QPATH_HELP'))
queue_recipe.set_kwarg(name='--qid', dtype=str, default='None',
                       helpstr=textentry('QUEUE_RECIPE_QID_HELP'))
queue_recipe.set_kwarg(name='--qresult', dtype='options', default='None',
                       options=['success', 'failed', 'None'],
                       helpstr=textentry('QUEUE_RECIPE_QRESULT_HELP'))
queue_recipe.set_kwarg(name='--template', dtype=str, default='None',
                       helpstr=textentry('QUEUE_RECIPE_TEMPLATE_HELP'))
queue_recipe.set_kwarg(name='--per_batch', dtype=str, default='None',
                       helpstr=textentry('QUEUE_RECIPE_PER_BATCH_HELP'))
queue_recipe.set_kwarg(name='--n_batches', dtype=str, default='None',
                       helpstr=textentry('QUEUE_RECIPE_N_BATCHES_HELP'))
queue_recipe.set_kwarg(name='--submit', dtype='options', default='None',
                       options=['True', 'False', 'None'],
                       helpstr=textentry('QUEUE_RECIPE_SUBMIT_HELP'))
queue_recipe.set_kwarg(name='--dry_run', dtype='switch',
                       helpstr=textentry('QUEUE_RECIPE_DRY_RUN_HELP'))

# -----------------------------------------------------------------------------
# apero_requirements-check.py
# -----------------------------------------------------------------------------
req_check.name = 'apero_dependencies.py'
req_check.path = 'apero.tools.recipes.dev'
req_check.shortname = 'DEPEND'
req_check.instrument = __INSTRUMENT__
req_check.description = textentry('DEPENDENCIES_DESCRIPTION')
req_check.recipe_type = 'nolog-tool'
req_check.recipe_kind = 'admin'

# -----------------------------------------------------------------------------
# apero_reject.py
# -----------------------------------------------------------------------------
reject.name = 'apero_reject.py'
reject.path = 'apero.tools.recipes.bin'
reject.shortname = 'REJECT'
reject.instrument = __INSTRUMENT__
reject.description = (textentry('REJECT_DESCRIPTION'))
reject.recipe_type = 'nolog-tool'
reject.recipe_kind = 'user'
reject.set_kwarg(name='--identifier', dtype='List[str]', default='None',
                 helpstr=textentry('REJECT_IDENTIFIER_HELP'))
reject.set_kwarg(name='--objname', dtype='List[str]', default='None',
                 helpstr=textentry('REJECT_OBJNAME_HELP'))
reject.set_kwarg(name='--obsdir', dtype=str, default='None',
                 helpstr=textentry('REJECT_OBSDIR_HELP'))
reject.set_kwarg(name='--autofill', dtype=str, default='None',
                 helpstr=textentry('REJECT_AUTOFILL_HELP'))
reject.set_kwarg(name='--test', dtype='switch',
                 helpstr=textentry('REJECT_TEST_HELP'))

# -----------------------------------------------------------------------------
# apero_reset.py
# -----------------------------------------------------------------------------
remove.name = 'apero_remove.py'
remove.path = 'apero.tools.recipes.bin'
remove.shortname = 'REMOVE'
remove.instrument = __INSTRUMENT__
remove.description = textentry('REMOVE_DESCRIPTION')
remove.recipe_type = 'nolog-tool'
remove.recipe_kind = 'user'
remove.set_kwarg(name='--obsdir', dtype=str, default='None',
                 helpstr=textentry('REMOVE_OBSDIR_HELP'))
remove.set_kwarg(name='--blocks', dtype='List[str]', default='None',
                 helpstr=textentry('REMOVE_BLOCKS_HELP'))
remove.set_kwarg(name='--file_prefix', dtype=str, default='None',
                 helpstr=textentry('REMOVE_FILE_PREFIX_HELP'))
remove.set_kwarg(name='--file_suffix', dtype=str, default='None',
                 helpstr=textentry('REMOVE_FILE_SUFFIX_HELP'))
remove.set_kwarg(name='--objnames', dtype='List[str]', default='None',
                 helpstr=textentry('REMOVE_OBJNAMES_HELP'))
remove.set_kwarg(name='--test', dtype='switch',
                 helpstr=textentry('REMOVE_TEST_HELP'))
remove.set_kwarg(name='--nowarn', dtype='switch',
                 helpstr=textentry('REMOVE_NOWARN_HELP'))
remove.set_kwarg(name='--rawdb', dtype='switch',
                 helpstr=textentry('REMOVE_RAWDB_HELP'))

# -----------------------------------------------------------------------------
# apero_reset.py
# -----------------------------------------------------------------------------
reset.name = 'apero_reset.py'
reset.path = 'apero.tools.recipes.bin'
reset.shortname = 'RESET'
reset.instrument = __INSTRUMENT__
reset.description = textentry('RESET_DESCRIPTION')
reset.recipe_type = 'nolog-tool'
reset.recipe_kind = 'user'
reset.set_kwarg(name='--nolog', dtype='switch',
                helpstr=textentry('RESET_LOG_HELP'))
reset.set_kwarg(name='--nowarn', dtype='switch',
                helpstr=textentry('RESET_WARN_HELP'))
reset.set_kwarg(name='--database_timeout', dtype=int, default=0,
                helpstr=textentry('RESET_DATABASE_TIMEOUT_HELP'))
reset.set_kwarg(name='--only_assets', dtype='switch',
                helpstr=textentry('RESET_ONLY_ASSETS_HELP'))
reset.set_kwarg(name='--only_tmp', dtype='switch',
                helpstr=textentry('RESET_ONLY_TMP_HELP'))
reset.set_kwarg(name='--only_red', dtype='switch',
                helpstr=textentry('RESET_ONLY_RED_HELP'))
reset.set_kwarg(name='--only_calib', dtype='switch',
                helpstr=textentry('RESET_ONLY_CALIB_HELP'))
reset.set_kwarg(name='--only_tellu', dtype='switch',
                helpstr=textentry('RESET_ONLY_TELLU_HELP'))
reset.set_kwarg(name='--only_log', dtype='switch',
                helpstr=textentry('RESET_ONLY_LOG_HELP'))
reset.set_kwarg(name='--only_plot', dtype='switch',
                helpstr=textentry('RESET_ONLY_PLOT_HELP'))
reset.set_kwarg(name='--only_run', dtype='switch',
                helpstr=textentry('RESET_ONLY_RUN_HELP'))
reset.set_kwarg(name='--only_lbl', dtype='switch',
                helpstr=textentry('RESET_ONLY_LBL_HELP'))
reset.set_kwarg(name='--only_out', dtype='switch',
                helpstr=textentry('RESET_ONLY_OUT_HELP'))
reset.set_kwarg(name='--only_other', dtype='switch',
                helpstr=textentry('RESET_ONLY_OTHER_HELP'))
reset.set_kwarg(name='--only_queue', dtype='switch',
                helpstr=textentry('RESET_ONLY_QUEUE_HELP'))


# -----------------------------------------------------------------------------
# apero_update_run_config.py
# -----------------------------------------------------------------------------
run_ini.name = 'apero_update_run_config.py'
run_ini.path = 'apero.tools.recipes.dev'
run_ini.shortname = 'RUN_INI'
run_ini.instrument = __INSTRUMENT__
run_ini.description = textentry('RUN_INI_DESCRIPTION')
run_ini.recipe_type = 'nolog-tool'
run_ini.recipe_kind = 'admin'
run_ini.set_kwarg(name='--instrument', dtype='options', default='None',
                  options=apero_base.INSTRUMENTS,
                  helpstr=textentry('RUN_INI_INSTRUMENT_HELP'))
run_ini.set_kwarg(name='--runfile', dtype=str, default='None',
                  helpstr=textentry('RUN_INI_RUNFILE_HELP'))

# -----------------------------------------------------------------------------
# apero_validate.py
# -----------------------------------------------------------------------------
validate.name = 'apero_validate.py'
validate.path = 'apero.tools.recipes.bin'
validate.shortname = 'VALID'
validate.instrument = __INSTRUMENT__
validate.description = textentry('VALIDATE_DESCRIPTION')
validate.recipe_type = 'nolog-tool'
validate.recipe_kind = 'user'

# -----------------------------------------------------------------------------
# apero_visu.py
# -----------------------------------------------------------------------------
visulise.name = 'apero_visu.py'
visulise.path = 'apero.tools.recipes.bin'
visulise.shortname = 'VISU'
visulise.instrument = __INSTRUMENT__
visulise.description = textentry('VISU_DESCRIPTION')
visulise.recipe_type = 'tool'
visulise.recipe_kind = 'user'
visulise.set_kwarg(name='--mode', dtype='options', default='info',
                   options=['info', 'e2ds'],
                   helpstr=textentry('VISU_MODE_HELP'))
visulise.set_kwarg(name='--path', dtype=str, default='None',
                   helpstr=textentry('VISULISE_PATH_HELP'))
visulise.set_kwarg(name='--infopath', dtype=str, default='None',
                   helpstr=textentry('VISULISE_INFOPATH_HELP'))
visulise.set_kwarg(name='--core', dtype=int, default=1,
                   helpstr=textentry('VISULISE_CORE_HELP'))

# -----------------------------------------------------------------------------
# compile recipe list
# -----------------------------------------------------------------------------
RECIPE_DICT = drs_recipe.compile_recipe_dict(recipes)