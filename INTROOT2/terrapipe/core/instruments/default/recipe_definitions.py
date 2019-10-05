from terrapipe.core.constants import param_functions
from terrapipe.core.core import drs_recipe
from terrapipe.locale import drs_text

from terrapipe.core.instruments.default import file_definitions as sf

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'config.core.default.recipe_definitions.py'
__INSTRUMENT__ = None
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
drs_changelog = drs_recipe(__INSTRUMENT__)
listing = drs_recipe(__INSTRUMENT__)
reset = drs_recipe(__INSTRUMENT__)
reprocess = drs_recipe(__INSTRUMENT__)

# push into a list
recipes = [test, drs_changelog, reset, reprocess, listing]

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
drs_changelog.name = 'drs_changelog.py'
drs_changelog.instrument = __INSTRUMENT__
drs_changelog.description = Help['CHANGELOG_DESCRIPTION']
drs_changelog.set_arg(pos=0, name='preview', dtype='bool',
                      helpstr=Help['PREVIEW_HELP'])

# -----------------------------------------------------------------------------
# reset.py
# -----------------------------------------------------------------------------
reset.name = 'reset.py'
reset.instrument = __INSTRUMENT__
reset.description = Help['RESET_DESCRIPTION']
reset.set_arg(pos=0, name='instrument', dtype='options',
              helpstr=Help['RESET_INST_HELP'], options=['SPIROU', 'NIRPS'])
reset.set_kwarg(name='-log', dtype='bool', default=True,
                helpstr=Help['RESET_LOG_HELP'])
reset.set_kwarg(name='-warn', dtype='bool', default=True,
                helpstr=Help['RESET_WARN_HELP'])

# -----------------------------------------------------------------------------
# reprocess.py
# -----------------------------------------------------------------------------
reprocess.name = 'reprocess.py'
reprocess.instrument = __INSTRUMENT__
reprocess.description = Help['REPROCESS_DESCRIPTION']
reprocess.set_arg(pos=0, name='instrument', dtype='options',
                  helpstr=Help['REPROCESS_INST_HELP'],
                  options=['SPIROU', 'NIRPS'])
reprocess.set_arg(pos=1, name='runfile', dtype=str,
                  helpstr=Help['REPROCESS_RUNFILE_HELP'])
reprocess.set_kwarg(name='--nightname', dtype=str, default='None',
                    helpstr=Help['REPROCESS_NIGHTNAME_HELP'])
reprocess.set_kwarg(name='--filename', dtype=str, default='None',
                    helpstr=Help['REPROCESS_FILENAME_HELP'])

# -----------------------------------------------------------------------------
# listing.py
# -----------------------------------------------------------------------------
listing.name = 'listing.py'
listing.instrument = __INSTRUMENT__
listing.description = 'None'
listing.set_arg(pos=0, name='instrument', dtype='options',
                  helpstr='None', options=['SPIROU', 'NIRPS'])
listing.set_kwarg(name='--nightname', dtype=str, default='',
                    helpstr='None')
listing.set_kwarg(name='--kind', dtype=str, default='raw',
                    options=['raw', 'tmp', 'red'],
                    helpstr='None')
