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
recipes = [changelog, database_mgr, explorer,
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
changelog.instrument = __INSTRUMENT__
changelog.description = textentry('CHANGELOG_DESCRIPTION')
changelog.kind = 'tool'
changelog.set_arg(pos=0, name='preview', dtype='bool',
                  helpstr=textentry('PREVIEW_HELP'))

# -----------------------------------------------------------------------------
# apero_database.py
# -----------------------------------------------------------------------------
database_mgr.name = 'apero_database.py'
database_mgr.instrument = __INSTRUMENT__
database_mgr.description = 'APERO database manager'
database_mgr.kind = 'tool'

database_mgr.set_kwarg(name='--kill', dtype='switch', default=False,
                       helpstr='Use this when database is stuck and you have'
                               'no other opens (mysql only)')
database_mgr.set_kwarg(name='--csv', dtype=str, default='None',
                       helpstr='Path to csv file. For --importdb this is the'
                               'csv file you wish to add. For --exportdb this'
                               'is the csv file that will be saved.')
database_mgr.set_kwarg(name='--exportdb', dtype=str, default='None',
                       options=base.DATABASE_NAMES,
                       helpstr='Export a database to a csv file')
database_mgr.set_kwarg(name='--importdb', dtype=str, default='None',
                       options=base.DATABASE_NAMES,
                       helpstr='Import a csv file into a database')
database_mgr.set_kwarg(name='--join', dtype=str, default='replace',
                       options=['replace', 'append'],
                       helpstr='How to add the csv file to database:'
                               ' append adds all lines to the end of current database, '
                               ' replace removes all previous lines from database.'
                               ' Default is "replace"')

# -----------------------------------------------------------------------------
# apero_documentation.py
# -----------------------------------------------------------------------------
remake_doc.name = 'apero_documentation.py'
remake_doc.instrument = __INSTRUMENT__
# TODO: Move to language DB
remake_doc.description = 'Re-make the apero documentation'
remake_doc.kind = 'tool'
# TODO: Move Help to language DB
remake_doc.set_kwarg(name='--upload', dtype='bool', default=False,
                     helpstr='[Bool] If True upload documentation to '
                             'defined server (for web access)')

# -----------------------------------------------------------------------------
# apero_explorer.py
# -----------------------------------------------------------------------------

explorer.name = 'apero_explorer.py'
explorer.instrument = __INSTRUMENT__
explorer.description = textentry('EXPLORER_DESCRIPTION')
explorer.kind = 'tool'
# TODO: move helpstr to language database
explorer.set_kwarg(name='--hash', default=False, dtype='switch',
                   helpstr=textentry('EXPLORER_HASH'))

# -----------------------------------------------------------------------------
# apero_listing.py
# -----------------------------------------------------------------------------
listing.name = 'apero_listing.py'
listing.instrument = __INSTRUMENT__
listing.description = textentry('LISTING_DESC')
listing.kind = 'tool'
listing.set_kwarg(name='--obs_dir', dtype=str, default='',
                  helpstr=textentry('LISTING_HELP_OBS_DIR'))
listing.set_kwarg(name='--kind', dtype=str, default='raw',
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
logstats.instrument = __INSTRUMENT__
logstats.description = textentry('LOGSTAT_DESC')
logstats.kind = 'tool'
logstats.set_debug_plots('LOGSTATS_BAR')
logstats.set_summary_plots()
logstats.set_kwarg(name='--obs_dir', dtype=str, default='',
                   helpstr=textentry('LOGSTAT_HELP_OBS_DIR'))
logstats.set_kwarg(name='--kind', dtype=str, default='red',
                   options=['tmp', 'red'],
                   helpstr=textentry('LOGSTAT_HELP_KIND'))
# TODO: add help string
logstats.set_kwarg(name='--recipe', dtype=str, default='None',
                   helpstr='Define a recipe name (the full python name) to'
                           'filter all results by - this will change the '
                           'analysis done on the log files')
logstats.set_kwarg(name='--since', dtype=str, default='None',
                   helpstr='Define a date and time for the earliest log. '
                           'Must be in the form yyyy-mm-dd HH:MM:SS or '
                           'yyyy-mm-dd (and the time will be assumed '
                           'midnight).')
logstats.set_kwarg(name='--before', dtype=str, default='None',
                   helpstr='Define a date and time for the most recent log. '
                           'Must be in the form yyyy-mm-dd HH:MM:SS or '
                           'yyyy-mm-dd (and the time will be assumed '
                           'midnight).')
logstats.set_kwarg(name='--mlog', dtype='bool', default=False,
                   helpstr='Whether to save a master log to the drs path '
                           '(MASTER_LOG.fits). '
                           'i.e. for --kind=red the DATA_DIR/reduced/ dir). '
                           'Note if --recipe is set this will add a suffix'
                           'to the output name. ')
logstats.set_kwarg(**plot)

# -----------------------------------------------------------------------------
# apero_mkdb.py
# -----------------------------------------------------------------------------
remake_db.name = 'apero_mkdb.py'
remake_db.instrument = __INSTRUMENT__
remake_db.description = textentry('REMAKE_DESC')
remake_db.kind = 'tool'
remake_db.set_kwarg(name='--kind', dtype='options',
                    options=['calibration', 'telluric'],
                    default_ref='REMAKE_DATABASE_DEFAULT',
                    helpstr=textentry('REMAKE_HELP_KIND'), default='calibration')

# -----------------------------------------------------------------------------
# apero_processing.py
# -----------------------------------------------------------------------------
processing.name = 'apero_processing.py'
processing.instrument = __INSTRUMENT__
processing.description = textentry('PROCESS_DESCRIPTION')
processing.kind = 'processing'
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
processing.set_kwarg(name='--test', dtype=str, default='None',
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
req_check.instrument = __INSTRUMENT__
req_check.description = textentry('DEPENDENCIES_DESCRIPTION')
req_check.kind = 'tool'

# -----------------------------------------------------------------------------
# apero_reset.py
# -----------------------------------------------------------------------------
reset.name = 'apero_reset.py'
reset.instrument = __INSTRUMENT__
reset.description = textentry('RESET_DESCRIPTION')
reset.kind = 'tool'
reset.set_kwarg(name='--log', dtype='bool', default=True,
                helpstr=textentry('RESET_LOG_HELP'))
reset.set_kwarg(name='--warn', dtype='bool', default=True,
                helpstr=textentry('RESET_WARN_HELP'))

# -----------------------------------------------------------------------------
# apero_validate.py
# -----------------------------------------------------------------------------
validate.name = 'apero_validate.py'
validate.instrument = __INSTRUMENT__
validate.description = textentry('VALIDATE_DESCRIPTION')
validate.kind = 'tool'

