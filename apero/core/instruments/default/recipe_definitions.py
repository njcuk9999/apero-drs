from apero.core.constants import param_functions
from apero.core.core import drs_recipe
from apero.locale import drs_text

from apero.core.instruments.default import file_definitions as sf

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'config.core.default.recipe_definitions.py'
__INSTRUMENT__ = 'None'
# Get constants
Constants = param_functions.load_config(__INSTRUMENT__)
# Get Help
Help = drs_text.HelpDict(__INSTRUMENT__, Constants['LANGUAGE'])
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']

# =============================================================================
# Commonly used arguments
# =============================================================================
directory = dict(name='directory', dtype='directory',
                 helpstr=Help['DIRECTORY_HELP'])

# =============================================================================
# List of usable recipes
# =============================================================================
drs_recipe = drs_recipe.DrsRecipe

# Below one must define all recipes and put into the "recipes" list
test = drs_recipe(__INSTRUMENT__)
changelog = drs_recipe(__INSTRUMENT__)
listing = drs_recipe(__INSTRUMENT__)
reset = drs_recipe(__INSTRUMENT__)
processing = drs_recipe(__INSTRUMENT__)
remake_db = drs_recipe(__INSTRUMENT__)
req_check = drs_recipe(__INSTRUMENT__)
validate = drs_recipe(__INSTRUMENT__)
explorer = drs_recipe(__INSTRUMENT__)

# push into a list
recipes = [test, changelog, explorer, reset, processing,
           remake_db, req_check, listing, validate]

# =============================================================================
# Recipe definitions
# =============================================================================
# Each recipe requires the following:
#    recipe = drs_recipe()  [DEFINED ABOVE]
#
#    recipe.name            the full name of the python script file
#    recipe.outputdir       the output directory [raw/tmp/reduced]
#    recipe.inputdir        the input directory [raw/tmp/reduced]
#    recipe.inputtype       the extension to look for and add for files
#                           (i.e. "fits")
#    recipe.description     the description (for help file)
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
# test.py
# -----------------------------------------------------------------------------
test.name = 'test_recipe.py'
test.instrument = __INSTRUMENT__
test.outputdir = 'tmp'
test.inputdir = 'tmp'
test.inputtype = 'pp'
test.extension = 'fits'
test.description = Help['TEST_DESCRIPTION']
test.epilog = Help['TEST_EXAMPLE']
test.set_arg(pos=0, **directory)
test.set_kwarg(name='-filelist1', dtype='files', default=[], nargs='+',
               files=[sf.pp_file], filelogic='inclusive',
               helpstr='test 1', required=True)
test.set_kwarg(name='-filelist2', dtype='files', default=[], nargs='+',
               files=[sf.pp_file], helpstr='test 2', required=True)

# -----------------------------------------------------------------------------
# changelog.py
# -----------------------------------------------------------------------------
changelog.name = 'apero_changelog.py'
changelog.instrument = __INSTRUMENT__
changelog.description = Help['CHANGELOG_DESCRIPTION']
changelog.set_arg(pos=0, name='preview', dtype='bool',
                      helpstr=Help['PREVIEW_HELP'])

# -----------------------------------------------------------------------------
# changelog.py
# -----------------------------------------------------------------------------

explorer.name = 'apero_explorer.py'
explorer.instrument = __INSTRUMENT__
# TODO: Add description
explorer.description = ''
# TODO: Add instrument help
explorer.set_arg(pos=0, name='instrument', dtype='options',
                 helpstr='', options=['SPIROU', 'NIRPS'])


# -----------------------------------------------------------------------------
# apero-reset.py
# -----------------------------------------------------------------------------
reset.name = 'apero_reset.py'
reset.instrument = __INSTRUMENT__
reset.description = Help['RESET_DESCRIPTION']
reset.set_arg(pos=0, name='instrument', dtype='options',
              helpstr=Help['RESET_INST_HELP'], options=['SPIROU', 'NIRPS'])
reset.set_kwarg(name='-log', dtype='bool', default=True,
                helpstr=Help['RESET_LOG_HELP'])
reset.set_kwarg(name='-warn', dtype='bool', default=True,
                helpstr=Help['RESET_WARN_HELP'])

# -----------------------------------------------------------------------------
# apero-processing.py
# -----------------------------------------------------------------------------
processing.name = 'apero_processing.py'
processing.instrument = __INSTRUMENT__
processing.description = Help['PROCESS_DESCRIPTION']
processing.set_arg(pos=0, name='instrument', dtype='options',
                  helpstr=Help['PROCESS_INST_HELP'],
                  options=['SPIROU', 'NIRPS'])
processing.set_arg(pos=1, name='runfile', dtype=str,
                  helpstr=Help['PROCESS_RUNFILE_HELP'])
processing.set_kwarg(name='--nightname', dtype=str, default='None',
                    helpstr=Help['PROCESS_NIGHTNAME_HELP'])
processing.set_kwarg(name='--filename', dtype=str, default='None',
                    helpstr=Help['PROCESS_FILENAME_HELP'])
processing.set_kwarg(name='--bnightnames', dtype=str, default='None',
                     helpstr=Help['PROCESS_BNIGHTNAMES_HELP'])
processing.set_kwarg(name='--wnightnames', dtype=str, default='None',
                     helpstr=Help['PROCESS_WNIGHTNAMES_HELP'])
processing.set_kwarg(name='--cores', dtype=str, default='None',
                     helpstr=Help['PROCESS_CORES_HELP'])
processing.set_kwarg(name='--test', dtype=str, default='None',
                     options=['True', 'False', '1', '0', 'None'],
                     helpstr=Help['PROCESS_TEST_HELP'])

# -----------------------------------------------------------------------------
# apero-listing.py
# -----------------------------------------------------------------------------
listing.name = 'apero_listing.py'
listing.instrument = __INSTRUMENT__
listing.description = Help['LISTING_DESC']
listing.set_arg(pos=0, name='instrument', dtype='options',
                helpstr=Help['LISTING_HELP_INSTRUMENT'],
                options=['SPIROU', 'NIRPS'])
listing.set_kwarg(name='--nightname', dtype=str, default='',
                  helpstr=Help['LISTING_HELP_NIGHTNAME'])
listing.set_kwarg(name='--kind', dtype=str, default='raw',
                  options=['raw', 'tmp', 'red'],
                  helpstr=Help['LISTING_HELP_KIND'])

# -----------------------------------------------------------------------------
# apero-requirements-check.py
# -----------------------------------------------------------------------------
req_check.name = 'apero_dependencies.py'
req_check.instrument = __INSTRUMENT__
# TODO: Add description
req_check.description = ''

# -----------------------------------------------------------------------------
# apero-mkdb.py
# -----------------------------------------------------------------------------
remake_db.name = 'apero_mkdb.py'
remake_db.instrument = __INSTRUMENT__
remake_db.description = Help['REMAKE_DESC']
remake_db.set_arg(pos=0, name='instrument', dtype='options',
                   helpstr=Help['REMAKE_HELP_INSTRUMENT'],
                  options=['SPIROU', 'NIRPS'])
remake_db.set_kwarg(name='--kind', dtype='options',
                  options=['calibration', 'telluric'],
                  default_ref='REMAKE_DATABASE_DEFAULT',
                  helpstr=Help['REMAKE_HELP_KIND'], default='calibration')

# -----------------------------------------------------------------------------
# apero-validate.py
# -----------------------------------------------------------------------------
validate.name = 'apero_validate.py'
validate.instrument = __INSTRUMENT__
# TODO: Add description
validate.description = ''
validate.set_arg(pos=0, name='instrument', dtype='options',
                  helpstr=Help['REMAKE_HELP_INSTRUMENT'],
                  options=['SPIROU', 'NIRPS'])