from terrapipe.core import constants
from terrapipe.core.core import drs_recipe
from terrapipe.locale import drs_text

from . import file_definitions as sf

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'config.instruments.spirou.recipe_definitions.py'
__INSTRUMENT__ = 'SPIROU'
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
dobad = dict(name='--badcorr', dtype='bool', default=True,
             helpstr=Help['DOBAD_HELP'])

# -----------------------------------------------------------------------------
backsub = dict(name='--backsub', dtype='bool', default=True,
               helpstr=Help['BACKSUB_HELP'], default_ref='option_backsub')
# -----------------------------------------------------------------------------
# Must set default per recipe!!
combine = dict(name='--combine', dtype='bool',
               helpstr=Help['COMBINE_HELP'], default_ref='INPUT_COMBINE_IMAGES')
# -----------------------------------------------------------------------------
dodark = dict(name='--darkcorr', dtype='bool', default=True,
              helpstr=Help['DODARK_HELP'])
# -----------------------------------------------------------------------------
fiber = dict(name='--fiber', dtype='options', default='ALL',
             helpstr=Help['EXTFIBER_HELP'],
             options=['ALL', 'AB', 'A', 'B', 'C'],
             default_ref='INPUT_FLIP_IMAGE')
# -----------------------------------------------------------------------------
flipimage = dict(name='--flipimage', dtype='options', default='both',
                 helpstr=Help['FLIPIMAGE_HELP'],
                 options=['None', 'x', 'y', 'both'])
# -----------------------------------------------------------------------------
fluxunits = dict(name='--fluxunits', dtype='options', default='e-',
                 helpstr=Help['FLUXUNITS_HELP'], options=['ADU/s', 'e-'])
# -----------------------------------------------------------------------------
interactive = dict(name='--interactive', dtype='bool',
                   helpstr=Help['INTERACTIVE_HELP'],
                   default_ref='DRS_INTERACTIVE')
# -----------------------------------------------------------------------------
plot = dict(name='--plot', dtype=int, helpstr=Help['PLOT_HELP'],
            default_ref='DRS_PLOT', minimum=0, maximum=2)
# -----------------------------------------------------------------------------
resize = dict(name='--resize', dtype='bool', default=True,
              helpstr=Help['RESIZE_HELP'], default_ref='INPUT_RESIZE_IMAGE')
# -----------------------------------------------------------------------------
objname = dict(name='--objname', dtype=str, default='None',
               helpstr=Help['OBJNAME_HELP'])
# -----------------------------------------------------------------------------
dprtype = dict(name='--dprtype', dtype=str, default='None',
               helpstr=Help['DPRTYPE_HELP'])

# =============================================================================
# File option definitions
# =============================================================================
backfile = dict(name='--backfile', dtype='file', default='None',
                files=[sf.out_backmap], helpstr=Help['BACKFILE_HELP'])
# -----------------------------------------------------------------------------
badfile = dict(name='--badpixfile', dtype='file', default='None',
               files=[sf.out_badpix], helpstr=Help['BADFILE_HELP'])
# -----------------------------------------------------------------------------
# TODO: Need to add blaze
# blazefile = dict(name='--blazefile', dtype='file', default='None',
#                  files=[sf.out_ff_blaze], helpstr=Help['BLAZEFILE_HELP'])
# -----------------------------------------------------------------------------
darkfile = dict(name='--darkfile', dtype='file', default='None',
                files=[sf.out_dark], helpstr=Help['DARKFILE_HELP'])
# -----------------------------------------------------------------------------
# TODO: Need to add flat
# flatfile = dict(name='--flatfile', dtype='file', default='None',
#                 files=[sf.out_ff_flat], helpstr=Help['FLATFILE_HELP'])
# -----------------------------------------------------------------------------
fpmaster = dict(name='--fpmaster', dtype='file', default='None',
                files=[sf.out_shape_fpmaster],
                helpstr=Help['FPMASTERFILE_HELP'])
# -----------------------------------------------------------------------------
locofile = dict(name='--locofile', dtype='file', default='None',
                files=[sf.out_loc_loco], helpstr=Help['LOCOFILE_HELP'])
# -----------------------------------------------------------------------------
orderpfile = dict(name='--orderpfile', dtype='file', default='None',
                  files=[sf.out_loc_orderp], helpstr=Help['ORDERPFILE_HELP'])
# -----------------------------------------------------------------------------
shapexfile = dict(name='--shapex', dtype='file', default='None',
                  files=[sf.out_shape_dxmap], helpstr=Help['SHAPEXFILE_HELP'])
# -----------------------------------------------------------------------------
shapeyfile = dict(name='--shapey', dtype='file', default='None',
                  files=[sf.out_shape_dymap], helpstr=Help['SHAPEYFILE_HELP'])
# -----------------------------------------------------------------------------
shapelfile = dict(name='--shapel', dtype='file', default='None',
                  files=[sf.out_shape_local], helpstr=Help['SHAPELFILE_HELP'])
# -----------------------------------------------------------------------------
# TODO: Need to add thermal
# thermalfile = dict(name='--thermal', dtype='file', default='None',
#                    files=[sf.out_thermal_e2ds],
#                    helpstr=Help['THERMALFILE_HELP'])
# -----------------------------------------------------------------------------
wavefile = dict(name='--wavefile', dtype='file', default='None',
                files=[sf.out_wave, sf.out_wave_master],
                helpstr=Help['WAVEFILE_HELP'])

# =============================================================================
# List of usable recipes
# =============================================================================
DrsRecipe = drs_recipe.DrsRecipe

# Below one must define all recipes and put into the "recipes" list
#     must have filemod = correct file definitions
cal_badpix = DrsRecipe(__INSTRUMENT__, filemod=sf)
cal_ccf = DrsRecipe(__INSTRUMENT__, filemod=sf)
cal_dark = DrsRecipe(__INSTRUMENT__, filemod=sf)
cal_dark_master = DrsRecipe(__INSTRUMENT__, filemod=sf)
cal_drift1 = DrsRecipe(__INSTRUMENT__, filemod=sf)
cal_drift2 = DrsRecipe(__INSTRUMENT__, filemod=sf)
cal_extract = DrsRecipe(__INSTRUMENT__, filemod=sf)
cal_ff = DrsRecipe(__INSTRUMENT__, filemod=sf)
cal_hc = DrsRecipe(__INSTRUMENT__, filemod=sf)
cal_loc = DrsRecipe(__INSTRUMENT__, filemod=sf)
cal_pp = DrsRecipe(__INSTRUMENT__, filemod=sf)
cal_slit = DrsRecipe(__INSTRUMENT__, filemod=sf)
cal_shape = DrsRecipe(__INSTRUMENT__, filemod=sf)
cal_shape_master = DrsRecipe(__INSTRUMENT__, filemod=sf)
cal_thermal = DrsRecipe(__INSTRUMENT__, filemod=sf)
cal_wave = DrsRecipe(__INSTRUMENT__, filemod=sf)

# TODO: remove later
test = DrsRecipe(__INSTRUMENT__, filemod=sf)
# push into a list
recipes = [cal_badpix, cal_ccf, cal_dark, cal_dark_master, cal_drift1,
           cal_drift2, cal_extract, cal_ff, cal_hc, cal_loc, cal_pp, cal_slit,
           cal_shape, cal_shape_master, cal_thermal, cal_wave,
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
raw_recipe = DrsRecipe(__INSTRUMENT__, filemod=sf)
pp_recipe = DrsRecipe(__INSTRUMENT__, filemod=sf)
out_recipe = DrsRecipe(__INSTRUMENT__, filemod=sf)

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
test.set_arg(pos=0, **directory)
test.set_kwarg(name='-filelist1', dtype='files', default=[], nargs='+',
               files=[sf.pp_dark_dark, sf.pp_flat_flat], filelogic='inclusive',
               helpstr=Help['TEST_FILELIST1_HELP'], required=True)
test.set_kwarg(name='-filelist2', dtype='files', default=[], nargs='+',
               files=[sf.pp_fp_fp], helpstr=Help['TEST_FILELIST2_HELP'],
               required=True)
test.set_kwarg(**plot)
test.set_kwarg(**interactive)
test.set_kwarg(**add_cal)
test.set_kwarg(**dobad)
test.set_kwarg(**badfile)
test.set_kwarg(default=False, **combine)
test.set_kwarg(**dodark)
test.set_kwarg(**darkfile)
test.set_kwarg(**flipimage)
test.set_kwarg(**fluxunits)
test.set_kwarg(**resize)

# -----------------------------------------------------------------------------
# cal_preprocess_spirou
# -----------------------------------------------------------------------------
cal_pp.name = 'cal_preprocess_spirou.py'
cal_pp.shortname = 'PREPROCESS'
cal_pp.instrument = __INSTRUMENT__
cal_pp.outputdir = 'tmp'
cal_pp.inputdir = 'raw'
cal_pp.inputtype = 'raw'
cal_pp.extension = 'fits'
cal_pp.description = Help['PREPROCESS_DESC']
cal_pp.epilog = Help['PREPROCESS_EXAMPLE']
cal_pp.set_outputs(PP_FILE=sf.pp_file)
cal_pp.set_arg(pos=0, **directory)
cal_pp.set_arg(name='files', dtype='files', pos='1+', files=[sf.raw_file],
               helpstr=Help['PREPROCESS_UFILES_HELP'], limit=1)
cal_pp.set_kwarg(name='--skip', dtype='bool', default=False,
                 helpstr=Help['PPSKIP_HELP'], default_ref='SKIP_DONE_PP')

# -----------------------------------------------------------------------------
# cal_badpix_spirou
# -----------------------------------------------------------------------------
cal_badpix.name = 'cal_badpix_spirou.py'
cal_badpix.shortname = 'BADPIX'
cal_badpix.instrument = __INSTRUMENT__
cal_badpix.outputdir = 'reduced'
cal_badpix.inputdir = 'tmp'
cal_badpix.inputtype = 'pp'
cal_badpix.extension = 'fits'
cal_badpix.description = Help['BADPIX_DESC']
cal_badpix.epilog = Help['BADPIX_EXAMPLE']
cal_badpix.set_outputs(BADPIX=sf.out_badpix, BACKMAP=sf.out_backmap)
cal_badpix.set_arg(pos=0, **directory)
cal_badpix.set_kwarg(name='-flatfiles', dtype='files', files=[sf.pp_flat_flat],
                     nargs='+', filelogic='exclusive', required=True,
                     helpstr=Help['BADPIX_FLATFILE_HELP'], default=[])
cal_badpix.set_kwarg(name='-darkfiles', dtype='files', files=[sf.pp_dark_dark],
                     nargs='+', filelogic='exclusive', required=True,
                     helpstr=Help['BADPIX_DARKFILE_HELP'], default=[])
cal_badpix.set_kwarg(**add_cal)
cal_badpix.set_kwarg(default=True, **combine)
cal_badpix.set_kwarg(**flipimage)
cal_badpix.set_kwarg(**fluxunits)
cal_badpix.set_kwarg(**plot)
cal_badpix.set_kwarg(**interactive)
cal_badpix.set_kwarg(**resize)

# -----------------------------------------------------------------------------
# cal_dark_spirou
# -----------------------------------------------------------------------------
cal_dark.name = 'cal_dark_spirou.py'
cal_dark.shortname = 'DARK'
cal_dark.instrument = __INSTRUMENT__
cal_dark.outputdir = 'reduced'
cal_dark.inputdir = 'tmp'
cal_dark.intputtype = 'pp'
cal_dark.extension = 'fits'
cal_dark.description = Help['DARK_DESC']
cal_dark.epilog = Help['DARK_EXAMPLE']
cal_dark.set_outputs(DARK_FILE=sf.out_dark, SKY_FILE=sf.out_sky)
cal_dark.set_arg(pos=0, **directory)
cal_dark.set_arg(name='files', dtype='files', files=[sf.pp_dark_dark], pos='1+',
                 helpstr=Help['FILES_HELP'] + Help['DARK_FILES_HELP'])
cal_dark.set_kwarg(**add_cal)
cal_dark.set_kwarg(default=True, **combine)
cal_dark.set_kwarg(**plot)
cal_dark.set_kwarg(**interactive)

# -----------------------------------------------------------------------------
# cal_dark_master_spirou
# -----------------------------------------------------------------------------
cal_dark_master.name = 'cal_dark_master_spirou.py'
cal_dark_master.shortname = 'DARK_MASTER'
cal_dark_master.master = True
cal_dark_master.instrument = __INSTRUMENT__
cal_dark_master.outputdir = 'reduced'
cal_dark_master.inputdir = 'tmp'
cal_dark_master.intputtype = 'pp'
cal_dark_master.extension = 'fits'
cal_dark_master.description = Help['DARK_MASTER_DESC']
cal_dark_master.epilog = Help['DARK_MASTER_EXAMPLE']
cal_dark_master.set_outputs(DARK_MASTER_FILE=sf.out_dark_master)
cal_dark_master.set_kwarg(name='--filetype', dtype=str, default='DARK_DARK',
                          helpstr=Help['DARK_MASTER_FILETYPE'])
cal_dark_master.set_kwarg(**add_cal)
cal_dark_master.set_kwarg(**plot)
cal_dark_master.set_kwarg(**interactive)

# -----------------------------------------------------------------------------
# cal_loc_RAW_spirou
# -----------------------------------------------------------------------------
cal_loc.name = 'cal_loc_spirou.py'
cal_loc.shortname = 'LOC'
cal_loc.instrument = __INSTRUMENT__
cal_loc.outputdir = 'reduced'
cal_loc.inputdir = 'tmp'
cal_loc.inputtype = 'pp'
cal_loc.extension = 'fits'
cal_loc.description = Help['LOC_DESC']
cal_loc.epilog = Help['LOC_EXAMPLE']
cal_loc.set_outputs(ORDERP_FILE=sf.out_loc_orderp,
                    LOCO_FILE=sf.out_loc_loco,
                    FWHM_FILE=sf.out_loc_fwhm,
                    SUP_FILE=sf.out_loc_sup)
cal_loc.set_arg(pos=0, **directory)
cal_loc.set_arg(name='files', dtype='files', filelogic='exclusive',
                files=[sf.pp_dark_flat, sf.pp_flat_dark], pos='1+',
                helpstr=Help['FILES_HELP'] + Help['LOC_FILES_HELP'])
cal_loc.set_kwarg(**add_cal)
cal_loc.set_kwarg(**badfile)
cal_loc.set_kwarg(**dobad)
cal_loc.set_kwarg(**backsub)
cal_loc.set_kwarg(default=True, **combine)
cal_loc.set_kwarg(**darkfile)
cal_loc.set_kwarg(**dodark)
cal_loc.set_kwarg(**flipimage)
cal_loc.set_kwarg(**fluxunits)
cal_loc.set_kwarg(**plot)
cal_loc.set_kwarg(**interactive)
cal_loc.set_kwarg(**resize)

# -----------------------------------------------------------------------------
# cal_shape_master_spirou
# -----------------------------------------------------------------------------
cal_shape_master.name = 'cal_shape_master_spirou.py'
cal_shape_master.shortname = 'SHAPE_MASTER'
cal_shape_master.master = True
cal_shape_master.instrument = __INSTRUMENT__
cal_shape_master.outputdir = 'reduced'
cal_shape_master.inputdir = 'tmp'
cal_shape_master.inputtype = 'pp'
cal_shape_master.extension = 'fits'
cal_shape_master.description = Help['SHAPE_DESC']
cal_shape_master.epilog = Help['SHAPE_EXAMPLE']
cal_shape_master.set_outputs(FPMASTER_FILE=sf.out_shape_fpmaster,
                             DXMAP_FiLE=sf.out_shape_dxmap,
                             DYMAP_FILE=sf.out_shape_dymap,
                             SHAPE_IN_FP_FILE=sf.out_shape_debug_ifp,
                             SHAPE_IN_HC_FILE=sf.out_shape_debug_ihc,
                             SHAPE_OUT_FP_FILE=sf.out_shape_debug_ofp,
                             SHAPE_OUT_HC_FILE=sf.out_shape_debug_ohc,
                             SHAPE_BDXMAP_FILE=sf.out_shape_debug_bdx)
cal_shape_master.set_arg(pos=0, **directory)
cal_shape_master.set_kwarg(name='-hcfiles', dtype='files',
                           files=[sf.pp_hc1_hc1],
                           nargs='+', filelogic='exclusive', required=True,
                           helpstr=Help['SHAPE_HCFILES_HELP'], default=[])
cal_shape_master.set_kwarg(name='-fpfiles', dtype='files', files=[sf.pp_fp_fp],
                           nargs='+', filelogic='exclusive', required=True,
                           helpstr=Help['SHAPE_FPFILES_HELP'], default=[])
cal_shape_master.set_kwarg(**add_cal)
cal_shape_master.set_kwarg(**badfile)
cal_shape_master.set_kwarg(**dobad)
cal_shape_master.set_kwarg(**backsub)
cal_shape_master.set_kwarg(default=True, **combine)
cal_shape_master.set_kwarg(**darkfile)
cal_shape_master.set_kwarg(**dodark)
cal_shape_master.set_kwarg(**flipimage)
cal_shape_master.set_kwarg(**fluxunits)
cal_shape_master.set_kwarg(**locofile)
cal_shape_master.set_kwarg(**plot)
cal_shape_master.set_kwarg(**interactive)
cal_shape_master.set_kwarg(**resize)

# -----------------------------------------------------------------------------
# cal_SHAPE_spirou
# -----------------------------------------------------------------------------
cal_shape.name = 'cal_shape_spirou.py'
cal_shape.shortname = 'SHAPE'
cal_shape.instrument = __INSTRUMENT__
cal_shape.outputdir = 'reduced'
cal_shape.inputdir = 'tmp'
cal_shape.inputtype = 'pp'
cal_shape.extension = 'fits'
cal_shape.description = Help['SHAPE_DESC']
cal_shape.epilog = Help['SHAPE_EXAMPLE']
cal_shape.set_outputs(LOCAL_SHAPE_FILE=sf.out_shape_local,
                      SHAPEL_IN_FP_FILE=sf.out_shapel_debug_ifp,
                      SHAPEL_OUT_FP_FILE=sf.out_shapel_debug_ofp)
cal_shape.set_arg(pos=0, **directory)
cal_shape.set_arg(name='files', dtype='files', files=[sf.pp_fp_fp], pos='1+',
                  helpstr=Help['SHAPE_FPFILES_HELP'])
cal_shape.set_kwarg(**add_cal)
cal_shape.set_kwarg(**badfile)
cal_shape.set_kwarg(**dobad)
cal_shape.set_kwarg(**backsub)
cal_shape.set_kwarg(default=True, **combine)
cal_shape.set_kwarg(**darkfile)
cal_shape.set_kwarg(**dodark)
cal_shape.set_kwarg(**flipimage)
cal_shape.set_kwarg(**fluxunits)
cal_shape.set_kwarg(**fpmaster)
cal_shape.set_kwarg(**plot)
cal_shape.set_kwarg(**interactive)
cal_shape.set_kwarg(**resize)
cal_shape.set_kwarg(**shapexfile)
cal_shape.set_kwarg(**shapeyfile)

# -----------------------------------------------------------------------------
# cal_FF_RAW_spirou
# -----------------------------------------------------------------------------
cal_ff.name = 'cal_flat_spirou.py'
cal_ff.shortname = 'FF'
cal_ff.instrument = __INSTRUMENT__
cal_ff.outputdir = 'reduced'
cal_ff.inputdir = 'tmp'
cal_ff.inputtype = 'pp'
cal_ff.extension = 'fits'
cal_ff.description = Help['FLAT_DESC']
cal_ff.epilog = Help['FLAT_EXAMPLE']
cal_ff.set_outputs(FLAT_FILE=sf.out_ff_flat,
                   BLAZE_FILE=sf.out_ff_blaze,
                   E2DSLL_FILE=sf.out_ext_e2dsll,
                   ORDERP_SFILE=sf.out_orderp_straight)
cal_ff.set_arg(pos=0, **directory)
cal_ff.set_arg(name='files', dtype='files', filelogic='exclusive',
               files=[sf.pp_flat_flat, sf.pp_dark_flat, sf.pp_flat_dark],
               pos='1+',
               helpstr=Help['FILES_HELP'] + Help['FLAT_FILES_HELP'])
cal_ff.set_kwarg(**add_cal)
cal_ff.set_kwarg(**badfile)
cal_ff.set_kwarg(**dobad)
cal_ff.set_kwarg(**backsub)
cal_ff.set_kwarg(default=True, **combine)
cal_ff.set_kwarg(**darkfile)
cal_ff.set_kwarg(**dodark)
cal_ff.set_kwarg(**fiber)
cal_ff.set_kwarg(**flipimage)
cal_ff.set_kwarg(**fluxunits)
cal_ff.set_kwarg(**locofile)
cal_ff.set_kwarg(**orderpfile)
cal_ff.set_kwarg(**plot)
cal_ff.set_kwarg(**interactive)
cal_ff.set_kwarg(**resize)
cal_ff.set_kwarg(**shapexfile)
cal_ff.set_kwarg(**shapeyfile)
cal_ff.set_kwarg(**shapelfile)

# -----------------------------------------------------------------------------
# cal_thermal_spirou
# -----------------------------------------------------------------------------
cal_thermal.name = 'cal_thermal_spirou.py'
cal_thermal.shortname = 'THERMAL'
cal_thermal.instrument = __INSTRUMENT__
cal_thermal.outputdir = 'reduced'
cal_thermal.inputdir = 'tmp'
cal_thermal.inputtype = 'pp'
cal_thermal.extension = 'fits'
cal_thermal.description = Help['EXTRACT_DESC']
cal_thermal.epilog = Help['EXTRACT_EXAMPLE']
cal_thermal.set_outputs(THERMAL_E2DS_FILE=sf.out_thermal_e2ds)
cal_thermal.set_arg(pos=0, **directory)
cal_thermal.set_arg(name='files', dtype='files', pos='1+',
                    files=[sf.pp_dark_dark],
                    helpstr=Help['FILES_HELP'] + Help['EXTRACT_FILES_HELP'],
                    limit=1)
cal_thermal.set_kwarg(**add_cal)
cal_thermal.set_kwarg(**badfile)
cal_thermal.set_kwarg(**dobad)
cal_thermal.set_kwarg(**backsub)
cal_thermal.set_kwarg(default=True, **combine)
cal_thermal.set_kwarg(**darkfile)
cal_thermal.set_kwarg(**dodark)
cal_thermal.set_kwarg(**fiber)
cal_thermal.set_kwarg(**flipimage)
cal_thermal.set_kwarg(**fluxunits)
cal_thermal.set_kwarg(**locofile)
cal_thermal.set_kwarg(**orderpfile)
cal_thermal.set_kwarg(**plot)
cal_thermal.set_kwarg(**interactive)
cal_thermal.set_kwarg(**resize)
cal_thermal.set_kwarg(**shapexfile)
cal_thermal.set_kwarg(**shapeyfile)
cal_thermal.set_kwarg(**shapelfile)
cal_thermal.set_kwarg(**wavefile)

# -----------------------------------------------------------------------------
# cal_extract_spirou
# -----------------------------------------------------------------------------
cal_extract.name = 'cal_extract_spirou.py'
cal_extract.shortname = 'EXTRACT'
cal_extract.instrument = __INSTRUMENT__
cal_extract.outputdir = 'reduced'
cal_extract.inputdir = 'tmp'
cal_extract.inputtype = 'pp'
cal_extract.extension = 'fits'
cal_extract.description = Help['EXTRACT_DESC']
cal_extract.epilog = Help['EXTRACT_EXAMPLE']
cal_extract.set_outputs(E2DS_FILE=sf.out_ext_e2ds,
                        E2DSFF_FILE=sf.out_ext_e2dsff,
                        E2DSLL_FILE=sf.out_ext_e2dsll,
                        S1D_W_FILE=sf.out_ext_s1d_w,
                        S1D_V_FILE=sf.out_ext_s1d_v,
                        ORDERP_SFILE=sf.out_orderp_straight)
cal_extract.set_arg(pos=0, **directory)
cal_extract.set_arg(name='files', dtype='files', pos='1+', files=[sf.pp_file],
                    helpstr=Help['FILES_HELP'] + Help['EXTRACT_FILES_HELP'],
                    limit=1)
cal_extract.set_kwarg(**add_cal)
cal_extract.set_kwarg(**badfile)
cal_extract.set_kwarg(**dobad)
cal_extract.set_kwarg(**backsub)
cal_extract.set_kwarg(default=False, **combine)
cal_extract.set_kwarg(**objname)
cal_extract.set_kwarg(**dprtype)
cal_extract.set_kwarg(**darkfile)
cal_extract.set_kwarg(**dodark)
cal_extract.set_kwarg(**fiber)
cal_extract.set_kwarg(**flipimage)
cal_extract.set_kwarg(**fluxunits)
cal_extract.set_kwarg(**locofile)
cal_extract.set_kwarg(**orderpfile)
cal_extract.set_kwarg(**plot)
cal_extract.set_kwarg(**interactive)
cal_extract.set_kwarg(**resize)
cal_extract.set_kwarg(**shapexfile)
cal_extract.set_kwarg(**shapeyfile)
cal_extract.set_kwarg(**shapelfile)
cal_extract.set_kwarg(**wavefile)

# -----------------------------------------------------------------------------
# cal_HC_E2DS_spirou
# -----------------------------------------------------------------------------
# cal_hc.name = 'cal_HC_E2DS_spirou.py'
# cal_hc.instrument = __INSTRUMENT__
# cal_hc.outputdir = 'reduced'
# cal_hc.inputdir = 'reduced'
# cal_hc.inputtype = 'e2ds'
# cal_hc.extension = 'fits'
# cal_hc.description = Help['HC_E2DS_DESC']
# cal_hc.epilog = Help['HC_E2DS_EXAMPLE']
# # setup custom files (add a required keyword in the header to each file)
# #    in this case we require "KW_EXT_TYPE" = "HCONE_HCONE"
# cal_hc_files1 = [sf.out_ext_e2ds,  sf.out_ext_e2dsff]
# cal_hc_rkeys = dict(KW_EXT_TYPE='HCONE_HCONE')
# cal_hc_files2 = drs_file.add_required_keywords(cal_hc_files1, cal_hc_rkeys)
# # set up arguments
# cal_hc.arg(pos=0, **directory)
# cal_hc.arg(name='files', dtype='files', pos='1+', files=cal_hc_files2,
#            filelogic='exclusive', limit=1,
#            helpstr=Help['FILES_HELP'] + Help['HC_E2DS_FILES_HELP'])
# cal_hc.kwarg(**add_cal)
# cal_hc.kwarg(**plot)
# cal_hc.kwarg(**interactive)
# cal_hc.kwarg(**blazefile)
# cal_hc.kwarg(**flatfile)
# cal_hc.kwarg(**wavefile)

# -----------------------------------------------------------------------------
# cal_WAVE_E2DS_spirou
# -----------------------------------------------------------------------------
cal_wave.name = 'cal_WAVE_E2DS_spirou.py'

# -----------------------------------------------------------------------------
# cal_DRIFT_E2DS_spirou
# -----------------------------------------------------------------------------
cal_drift1.name = 'cal_DRIFT_E2DS_spirou.py'

# -----------------------------------------------------------------------------
# cal_DRIFTPEAK_E2DS_spirou
# -----------------------------------------------------------------------------
cal_drift2.name = 'cal_DRIFTPEAK_E2DS_spirou.py'

# -----------------------------------------------------------------------------
# cal_CCF_E2DS_spirou
# -----------------------------------------------------------------------------
cal_ccf.name = 'cal_CCF_E2DS_spirou.py'

# -----------------------------------------------------------------------------
# obj_fit_tellu
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# obj_mk_tellu
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# obj_mk_tell_template
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# pol_spirou
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# cal_exposure_meter
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# cal_wave_mapper
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# visu_RAW_spirou
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# visu_E2DS_spirou
# -----------------------------------------------------------------------------


# =============================================================================
# Run order
# =============================================================================
#
#  These defines run sequences that can be used
#     (recipes will be executed in ordered added)
#
#       To define a new sequence first construct a DrsRunSequence
#       i.e.   run = drs_recipe.DrsRunSequence(name, instrument)
#
#       Then one must add recipes to a sequence
#           recipes can be customised by:
#           - name (shortname)
#           - allowed files (the name of the file argument)
#           - whether a file is in the master sequence (use master night only
#             in cases where normally a recipe would use any night)
#           - any header keyword reference (value must be set in run file)
#             i.e. those starting with "KW_"
#       i.e.
#
#       run.add(recipe, name='CUSTOM_RECIPE', master=True,
#               files=[sf.file_defintion], KW_HEADER='RUN_FILE_VARIABLE')
#
#
#   Example:
#           # the below example creates a run called 'run'
#           # it just extracts OBJ_FP files with OBJECT NAME listed in
#           #  'SCIENCE_TARGETS' in the runfile
#           # note as master=True it will only extract from the master night
#
#           run = drs_recipe.DrsRunSequence('run', __INSTRUMENT__)
#           run.add(cal_extract, master=True, files=[sf.pp_obj_fp],
#                   KW_OBJNAME='SCIENCE_TARGETS')
#
#
#  Note: must add sequences to sequences list to be able to use!
#
# -----------------------------------------------------------------------------
# full run (master + nights)
# -----------------------------------------------------------------------------
full_run = drs_recipe.DrsRunSequence('full_run', __INSTRUMENT__)
# master run
full_run.add(cal_pp, master=True)
full_run.add(cal_dark_master, master=True)
full_run.add(cal_badpix, master=True)
full_run.add(cal_loc, files=[sf.pp_dark_flat], master=True)
full_run.add(cal_loc, files=[sf.pp_flat_dark], master=True)
full_run.add(cal_shape_master, master=True)
# night runs
full_run.add(cal_pp)
full_run.add(cal_badpix)
full_run.add(cal_loc, files=[sf.pp_dark_flat])
full_run.add(cal_loc, files=[sf.pp_flat_dark])
full_run.add(cal_shape)
full_run.add(cal_ff, files=[sf.pp_flat_flat])
full_run.add(cal_thermal)
full_run.add(cal_wave)
# extract
full_run.add(cal_extract, name='EXTRACT_ALL',
             files=[sf.pp_obj_dark, sf.pp_obj_fp])

# -----------------------------------------------------------------------------
# limited run (master + nights)
# -----------------------------------------------------------------------------
limited_run = drs_recipe.DrsRunSequence('limited_run', __INSTRUMENT__)
# master run
limited_run.add(cal_pp, master=True)
limited_run.add(cal_dark_master, master=True)
limited_run.add(cal_badpix, master=True)
limited_run.add(cal_loc, files=[sf.pp_dark_flat], master=True)
limited_run.add(cal_loc, files=[sf.pp_flat_dark], master=True)
limited_run.add(cal_shape_master, master=True)
# night runs
limited_run.add(cal_pp)
limited_run.add(cal_badpix)
limited_run.add(cal_loc, files=[sf.pp_dark_flat])
limited_run.add(cal_loc, files=[sf.pp_flat_dark])
limited_run.add(cal_shape)
limited_run.add(cal_ff, files=[sf.pp_flat_flat])
limited_run.add(cal_thermal)
limited_run.add(cal_wave)
# extract tellurics
limited_run.add(cal_extract, name='EXTRACT_TELLU',
                files=[sf.pp_obj_dark, sf.pp_obj_fp],
                KW_OBJNAME='TELLURIC_TARGETS')
# extract science
limited_run.add(cal_extract, name='EXTRACT_OBJ',
                files=[sf.pp_obj_dark, sf.pp_obj_fp],
                KW_OBJNAME='SCIENCE_TARGETS')


# -----------------------------------------------------------------------------
# sequences list
# -----------------------------------------------------------------------------
sequences = [full_run, limited_run]

