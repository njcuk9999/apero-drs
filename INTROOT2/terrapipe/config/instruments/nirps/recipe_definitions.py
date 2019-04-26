from terrapipe import constants
from terrapipe.config import drs_recipe
from terrapipe.config import drs_file
from terrapipe.locale import drs_text

from . import file_definitions as sf


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'recipe_definitions.py'
__INSTRUMENT__ = 'NIRPS'
# Get constants
Constants = constants.load(__INSTRUMENT__)
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
# Option definitions
# =============================================================================
#
# Note for these to work MUST add to spirouStartup.spirou_options_manager
#
# -----------------------------------------------------------------------------
add_cal = dict(name='--add2calib', dtype='bool', default=True,
               helpstr=Help['ADD_CAL_HELP'])
# -----------------------------------------------------------------------------
# # Must set default_ref per recipe!!
# extractmethod = dict(name='--extractmethod', dtype='options',
#                      helpstr=Help['EXTRACT_METHOD_HELP'],
#                      options=['1', '2', '3a', '3b', '3c', '3d', '4a', '4b'])
# -----------------------------------------------------------------------------
interactive = dict(name='--interactive', dtype='bool',
                   helpstr=Help['INTERACTIVE_HELP'],
                   default_ref='DRS_INTERACTIVE')
# -----------------------------------------------------------------------------
plot = dict(name='--plot', dtype=int, helpstr=Help['PLOT_HELP'],
            default_ref='DRS_PLOT', minimum=0, maximum=2)


# =============================================================================
# File option definitions
# =============================================================================
# badfile = dict(name='--badpixfile', dtype='file', default='None',
#                files=[sf.out_badpix],
#                helpstr=Help['BADFILE_HELP'])


# =============================================================================
# List of usable recipes
# =============================================================================
drs_recipe = drs_recipe.DrsRecipe

# Below one must define all recipes and put into the "recipes" list
cal_badpix = drs_recipe(__INSTRUMENT__)
cal_ccf = drs_recipe(__INSTRUMENT__)
cal_dark = drs_recipe(__INSTRUMENT__)
cal_drift1 = drs_recipe(__INSTRUMENT__)
cal_drift2 = drs_recipe(__INSTRUMENT__)
cal_extract = drs_recipe(__INSTRUMENT__)
cal_ff = drs_recipe(__INSTRUMENT__)
cal_hc = drs_recipe(__INSTRUMENT__)
cal_loc = drs_recipe(__INSTRUMENT__)
cal_pp = drs_recipe(__INSTRUMENT__)
cal_slit = drs_recipe(__INSTRUMENT__)
cal_shape = drs_recipe(__INSTRUMENT__)
cal_wave = drs_recipe(__INSTRUMENT__)

test = drs_recipe(__INSTRUMENT__)
# push into a list
recipes = [cal_badpix, cal_ccf, cal_dark, cal_drift1, cal_drift2,
           cal_extract, cal_ff, cal_hc, cal_loc, cal_pp, cal_slit,
           cal_shape, cal_wave,
           test]

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
test.description = Help['TEST_DESC']
test.epilog = Help['TEST_EXAMPLE']
test.arg(pos=0, **directory)
test.arg(name='filelist', dtype='files', default=[], nargs='+',
         files=[sf.pp_dark_dark, sf.pp_flat_flat], filelogic='inclusive',
         helpstr=Help['TEST_FILELIST1_HELP'], required=True)
test.kwarg(**plot)
test.kwarg(**interactive)
test.kwarg(**add_cal)
