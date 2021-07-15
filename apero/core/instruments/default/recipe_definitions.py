from apero.base import base
from apero.core.constants import param_functions
from apero.core.utils import drs_recipe
from apero import lang

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
# Get constants
Constants = param_functions.load_config(__INSTRUMENT__)
# Get Help
textentry = lang.textentry

# =============================================================================
# Commonly used arguments
# =============================================================================
obs_dir = dict(name='obs_dir', dtype='obs_dir',
               helpstr=textentry('OBS_DIR_HELP'))
# -----------------------------------------------------------------------------
plot = dict(name='--plot', dtype=int, helpstr=textentry('PLOT_HELP'),
            default_ref='DRS_PLOT', minimum=0, maximum=2)

# =============================================================================
# List of usable recipes
# =============================================================================
drs_recipe = drs_recipe.DrsRecipe

# Below one must define all recipes and put into the "recipes" list
changelog = drs_recipe(__INSTRUMENT__)
explorer = drs_recipe(__INSTRUMENT__)
get_files = drs_recipe(__INSTRUMENT__)
database_mgr = drs_recipe(__INSTRUMENT__)
listing = drs_recipe(__INSTRUMENT__)
logstats = drs_recipe(__INSTRUMENT__)
processing = drs_recipe(__INSTRUMENT__)
remake_db = drs_recipe(__INSTRUMENT__)
remake_doc = drs_recipe(__INSTRUMENT__)
req_check = drs_recipe(__INSTRUMENT__)
reset = drs_recipe(__INSTRUMENT__)
validate = drs_recipe(__INSTRUMENT__)

# push into a list
recipes = [changelog, database_mgr, explorer, get_files,
           processing, listing, logstats, remake_db, remake_doc,
           req_check, reset, validate]

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
database_mgr.set_kwarg(name='--objdb', dtype=str, default='None',
                       helpstr='[True] or [str Path to dfits output]. '
                               'Update the object reset database using raw '
                               'directory [True] or a dfits output [str]')
database_mgr.set_kwarg(name='--update', dtype='switch', default=False,
                       helpstr=textentry('DBMGR_UPDATE_HELP'))
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
                       helpstr='Load up the delete table GUI (MySQL only)')


# -----------------------------------------------------------------------------
# apero_documentation.py
# -----------------------------------------------------------------------------
remake_doc.name = 'apero_documentation.py'
remake_doc.instrument = __INSTRUMENT__
remake_doc.shortname = 'DOC'
remake_doc.description = textentry('REMAKE_DOC_DESCRIPTION')
remake_doc.recipe_type = 'nolog-tool'
remake_doc.recipe_kind = 'admin'
remake_doc.set_kwarg(name='--compile', dtype='switch', default=False,
                     helpstr=textentry('REMAKE_DOC_COMPILE_HELP'))
remake_doc.set_kwarg(name='--upload', dtype='switch', default=False,
                     helpstr=textentry('REMAKE_DOC_UPLOADARG_HELP'))
remake_doc.set_kwarg(name='--filedef', dtype='switch', default=False,
                     helpstr=textentry('REMAKE_DOC_FILEDEF_HELP'))
remake_doc.set_kwarg(name='--recipedef', dtype='switch', default=False,
                     helpstr=textentry('REMAKE_DOC_RECIPEDEF_HELP'))
remake_doc.set_kwarg(name='--recipeseq', dtype='switch', default=False,
                     helpstr=textentry('REMAKE_DOC_RECIPESEQ_HELP'))

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


# -----------------------------------------------------------------------------
# apero_get.py
# -----------------------------------------------------------------------------
get_files.anme = 'apero_get.py'
get_files.shortname = 'GET'
get_files.instrument = __INSTRUMENT__
get_files.description = 'Use database to search and copy any files quickly'
get_files.recipe_type = 'nolog-tool'
get_files.recipe_kind = 'user'
get_files.set_kwarg(name='--gui', default=False, dtype='switch',
                    helpstr=textentry('GET_GUI_HELP'))
get_files.set_kwarg(name='--objnames', dtype=str, default='None',
                    helpstr=textentry('GET_OBJNAME_HELP'))
get_files.set_kwarg(name='--dprtypes', dtype=str, default='None',
                    helpstr=textentry('GET_DPRTYPES_HELP'))
get_files.set_kwarg(name='--outtypes', dtype=str, default='None',
                    helpstr=textentry('GET_OUTTYPES_HELP'))
get_files.set_kwarg(name='--fibers', dtype=str, default='None',
                    helpstr=textentry('GET_FIBERS_HELP'))
get_files.set_kwarg(name='--outpath', dtype=str, default='None',
                    helpstr=textentry('GET_OUTPATH_HELP'))
get_files.set_kwarg(name='--symlinks', default=False, dtype='switch',
                    helpstr=textentry('GET_SYMLINKS_HELP'))
get_files.set_kwarg(name='--test', default=False, dtype='switch',
                    helpstr=textentry('GET_TEST_HELP'))

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
listing.set_kwarg(name='--kind', dtype='options', default='raw',
                  options=['raw', 'tmp', 'red'],
                  helpstr=textentry('LISTING_HELP_KIND'))
listing.set_kwarg(name='--exclude_obs_dirs', dtype=str, default='None',
                  helpstr=textentry('PROCESS_EXCLUDE_OBS_DIRS_HELP'))
listing.set_kwarg(name='--include_obs_dirs', dtype=str, default='None',
                  helpstr=textentry('PROCESS_INCLUDE_OBS_DIRS_HELP'))

# -----------------------------------------------------------------------------
# apero_log_stats.py
# -----------------------------------------------------------------------------
logstats.name = 'apero_log_stats.py'
logstats.shortname = 'LSTAT'
logstats.instrument = __INSTRUMENT__
logstats.description = textentry('LOGSTAT_DESC')
logstats.recipe_type = 'nolog-tool'
logstats.recipe_kind = 'user'
logstats.set_debug_plots('LOGSTATS_BAR')
logstats.set_summary_plots()
logstats.set_kwarg(name='--obs_dir', dtype=str, default='',
                   helpstr=textentry('LOGSTAT_HELP_OBS_DIR'))
logstats.set_kwarg(name='--kind', dtype='options', default='red',
                   options=['tmp', 'red'],
                   helpstr=textentry('LOGSTAT_HELP_KIND'))
logstats.set_kwarg(name='--recipe', dtype=str, default='None',
                   helpstr=textentry('LOGSTAT_HELP_RECIPEARG'))
logstats.set_kwarg(name='--since', dtype=str, default='None',
                   helpstr=textentry('LOGSTAT_HELP_SINCEARG'))
logstats.set_kwarg(name='--before', dtype=str, default='None',
                   helpstr=textentry('LOGSTAT_HELP_BEFOREARG'))
logstats.set_kwarg(name='--mlog', dtype='bool', default=False,
                   helpstr=textentry('LOGSTAT_HELP_MLOG'))
logstats.set_kwarg(**plot)

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

# -----------------------------------------------------------------------------
# apero_requirements-check.py
# -----------------------------------------------------------------------------
req_check.name = 'apero_dependencies.py'
req_check.shortname = 'DEPEND'
req_check.instrument = __INSTRUMENT__
req_check.description = textentry('DEPENDENCIES_DESCRIPTION')
req_check.recipe_type = 'nolog-tool'
req_check.recipe_kind = 'admin'

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

# -----------------------------------------------------------------------------
# apero_validate.py
# -----------------------------------------------------------------------------
validate.name = 'apero_validate.py'
validate.shortname = 'VALID'
validate.instrument = __INSTRUMENT__
validate.description = textentry('VALIDATE_DESCRIPTION')
validate.recipe_type = 'nolog-tool'
validate.recipe_kind = 'user'

