from terrapipe.constants import param_functions
from terrapipe.config.core import drs_recipe
from terrapipe.locale import drs_text

from . import file_definitions as sf

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

# push into a list
recipes = [test, drs_changelog]

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
test.arg(pos=0, **directory)
test.kwarg(name='-filelist1', dtype='files', default=[], nargs='+',
           files=[sf.pp_file], filelogic='inclusive',
           helpstr='test 1', required=True)
test.kwarg(name='-filelist2', dtype='files', default=[], nargs='+',
           files=[sf.pp_file], helpstr='test 2', required=True)

# -----------------------------------------------------------------------------
# drs_changelog.py
# -----------------------------------------------------------------------------
drs_changelog.name = 'drs_changelog.py'
drs_changelog.instrument = __INSTRUMENT__
drs_changelog.description = Help['CHANGELOG_DESCRIPTION']
drs_changelog.arg(pos=0, name='preview', dtype='bool',
                  helpstr=Help['PREVIEW_HELP'])