from apero.base import base
from apero.base import drs_base_classes as base_class
from apero.core import constants
from apero.core.utils import drs_recipe
from apero import lang
from apero.core.instruments.nirps_ha import file_definitions as files

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'core.instruments.nirps_ha.recipe_definitions.py'
__INSTRUMENT__ = 'NIRPS_HA'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get Help
Help = lang.core.drs_lang_text.HelpDict(__INSTRUMENT__, Constants['LANGUAGE'])
# import file definitions in import module class
sf = base_class.ImportModule('nirps_ha.file_definitions',
                             'apero.core.instruments.nirps_ha.file_definitions',
                             mod=files)

# =============================================================================
# Commonly used arguments
# =============================================================================
directory = dict(name='directory', dtype='directory',
                 helpstr=Help['DIRECTORY_HELP'])

# =============================================================================
# Option definitions
# =============================================================================
add_db = dict(name='--database', dtype='bool', default=True,
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
plot = dict(name='--plot', dtype=int, helpstr=Help['PLOT_HELP'],
            default_ref='DRS_PLOT', minimum=-1, maximum=2)
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
                files=[files.out_backmap], helpstr=Help['BACKFILE_HELP'])
# -----------------------------------------------------------------------------
badfile = dict(name='--badpixfile', dtype='file', default='None',
               files=[files.out_badpix], helpstr=Help['BADFILE_HELP'])
# -----------------------------------------------------------------------------
blazefile = dict(name='--blazefile', dtype='file', default='None',
                 files=[files.out_ff_blaze], helpstr=Help['BLAZEFILE_HELP'])
# -----------------------------------------------------------------------------
darkfile = dict(name='--darkfile', dtype='file', default='None',
                files=[files.out_dark_master], helpstr=Help['DARKFILE_HELP'])
# -----------------------------------------------------------------------------
flatfile = dict(name='--flatfile', dtype='file', default='None',
                files=[files.out_ff_flat], helpstr=Help['FLATFILE_HELP'])
# -----------------------------------------------------------------------------
fpmaster = dict(name='--fpmaster', dtype='file', default='None',
                files=[files.out_shape_fpmaster],
                helpstr=Help['FPMASTERFILE_HELP'])
# -----------------------------------------------------------------------------
locofile = dict(name='--locofile', dtype='file', default='None',
                files=[files.out_loc_loco], helpstr=Help['LOCOFILE_HELP'])
# -----------------------------------------------------------------------------
orderpfile = dict(name='--orderpfile', dtype='file', default='None',
                  files=[files.out_loc_orderp], helpstr=Help['ORDERPFILE_HELP'])
# -----------------------------------------------------------------------------
shapexfile = dict(name='--shapex', dtype='file', default='None',
                  files=[files.out_shape_dxmap],
                  helpstr=Help['SHAPEXFILE_HELP'])
# -----------------------------------------------------------------------------
shapeyfile = dict(name='--shapey', dtype='file', default='None',
                  files=[files.out_shape_dymap],
                  helpstr=Help['SHAPEYFILE_HELP'])
# -----------------------------------------------------------------------------
shapelfile = dict(name='--shapel', dtype='file', default='None',
                  files=[files.out_shape_local],
                  helpstr=Help['SHAPELFILE_HELP'])
# -----------------------------------------------------------------------------
thermalfile = dict(name='--thermalfile', dtype='file', default='None',
                   files=[files.out_thermal_e2ds_int,
                          files.out_thermal_e2ds_tel],
                   helpstr=Help['THERMALFILE_HELP'])
# -----------------------------------------------------------------------------
wavefile = dict(name='--wavefile', dtype='file', default='None',
                files=[files.out_wave_hc, files.out_wave_fp,
                       files.out_wave_master],
                helpstr=Help['WAVEFILE_HELP'])

# =============================================================================
# Setup for recipes
# =============================================================================
DrsRecipe = drs_recipe.DrsRecipe
# push into a list
recipes = []

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
test = DrsRecipe(__INSTRUMENT__)
test.name = 'test_recipe.py'
test.instrument = __INSTRUMENT__
test.outputdir = 'tmp'
test.inputdir = 'tmp'
test.inputtype = 'pp'
test.extension = 'fits'
test.description = Help['TEST_DESC']
test.epilog = Help['TEST_EXAMPLE']
test.kind = 'test'
test.set_arg(pos=0, **directory)
test.set_kwarg(name='--filelist1', dtype='files', default=[],
               files=[files.pp_dark_dark_int, files.pp_flat_flat],
               filelogic='inclusive',
               helpstr=Help['TEST_FILELIST1_HELP'], required=True)
test.set_kwarg(name='--filelist2', dtype='files', default=[],
               files=[files.pp_fp_fp], helpstr=Help['TEST_FILELIST2_HELP'],
               required=True)
test.set_kwarg(**plot)
test.set_kwarg(**add_db)
test.set_kwarg(**dobad)
test.set_kwarg(**badfile)
test.set_kwarg(default=False, **combine)
test.set_kwarg(**dodark)
test.set_kwarg(**darkfile)
test.set_kwarg(**flipimage)
test.set_kwarg(**fluxunits)
test.set_kwarg(**resize)
# add to recipe
recipes.append(test)

# -----------------------------------------------------------------------------
# cal_pp_master_nirps_ha
# -----------------------------------------------------------------------------
cal_pp_master = DrsRecipe(__INSTRUMENT__)
cal_pp_master.name = 'cal_pp_master_nirps_ha.py'
cal_pp_master.shortname = 'PPM'
cal_pp_master.instrument = __INSTRUMENT__
cal_pp_master.outputdir = 'red'
cal_pp_master.inputdir = 'raw'
cal_pp_master.inputtype = 'raw'
cal_pp_master.extension = 'fits'
cal_pp_master.description = Help['PPMASTER_DESC']
cal_pp_master.epilog = Help['PPMASTER_EXAMPLE']
cal_pp_master.kind = 'recipe'
cal_pp_master.set_outputs(PP_MASTER=files.out_pp_master)
cal_pp_master.set_arg(pos=0, **directory)
cal_pp_master.set_kwarg(name='--filetype', dtype=str, default='FLAT_FLAT',
                        helpstr=Help['PPMASTER_FILETYPE_HELP'])
# add to recipe
recipes.append(cal_pp_master)

# -----------------------------------------------------------------------------
# cal_preprocess_nirps_ha
# -----------------------------------------------------------------------------
cal_pp = DrsRecipe(__INSTRUMENT__)
cal_pp.name = 'cal_preprocess_nirps_ha.py'
cal_pp.shortname = 'PP'
cal_pp.instrument = __INSTRUMENT__
cal_pp.outputdir = 'tmp'
cal_pp.inputdir = 'raw'
cal_pp.inputtype = 'raw'
cal_pp.extension = 'fits'
cal_pp.description = Help['PREPROCESS_DESC']
cal_pp.epilog = Help['PREPROCESS_EXAMPLE']
cal_pp.kind = 'recipe'
cal_pp.set_outputs(PP_FILE=files.pp_file)
cal_pp.set_arg(pos=0, **directory)
cal_pp.set_arg(name='files', dtype='files', pos='1+', files=[files.raw_file],
               helpstr=Help['PREPROCESS_UFILES_HELP'], limit=1)
cal_pp.set_kwarg(name='--skip', dtype='bool', default=False,
                 helpstr=Help['PPSKIP_HELP'], default_ref='SKIP_DONE_PP')
# add to recipe
recipes.append(cal_pp)

# -----------------------------------------------------------------------------
# cal_badpix_nirps_ha
# -----------------------------------------------------------------------------
cal_badpix = DrsRecipe(__INSTRUMENT__)
cal_badpix.name = 'cal_badpix_nirps_ha.py'
cal_badpix.shortname = 'BAD'
cal_badpix.instrument = __INSTRUMENT__
cal_badpix.outputdir = 'red'
cal_badpix.inputdir = 'tmp'
cal_badpix.inputtype = 'pp'
cal_badpix.extension = 'fits'
cal_badpix.description = Help['BADPIX_DESC']
cal_badpix.epilog = Help['BADPIX_EXAMPLE']
cal_badpix.kind = 'recipe'
cal_badpix.set_outputs(BADPIX=files.out_badpix, BACKMAP=files.out_backmap)
cal_badpix.set_debug_plots('BADPIX_MAP')
cal_badpix.set_summary_plots('SUM_BADPIX_MAP')
cal_badpix.set_arg(pos=0, **directory)
cal_badpix.set_kwarg(name='--flatfiles', dtype='files',
                     files=[files.pp_flat_flat],
                     filelogic='exclusive', required=True,
                     helpstr=Help['BADPIX_FLATFILE_HELP'], default=[])
cal_badpix.set_kwarg(name='--darkfiles', dtype='files',
                     files=[files.pp_dark_dark_tel, files.pp_dark_dark_int],
                     filelogic='exclusive', required=True,
                     helpstr=Help['BADPIX_DARKFILE_HELP'], default=[])
cal_badpix.set_kwarg(**add_db)
cal_badpix.set_kwarg(default=True, **combine)
cal_badpix.set_kwarg(**flipimage)
cal_badpix.set_kwarg(**fluxunits)
cal_badpix.set_kwarg(**plot)
cal_badpix.set_kwarg(**resize)
# add to recipe
recipes.append(cal_badpix)

# -----------------------------------------------------------------------------
# cal_dark_nirps_ha
# -----------------------------------------------------------------------------
cal_dark = DrsRecipe(__INSTRUMENT__)
cal_dark.name = 'cal_dark_nirps_ha.py'
cal_dark.shortname = 'DARK'
cal_dark.instrument = __INSTRUMENT__
cal_dark.outputdir = 'red'
cal_dark.inputdir = 'tmp'
cal_dark.intputtype = 'pp'
cal_dark.extension = 'fits'
cal_dark.description = Help['DARK_DESC']
cal_dark.epilog = Help['DARK_EXAMPLE']
cal_dark.kind = 'recipe'
cal_dark.set_outputs(DARK_INT_FILE=files.out_dark_int,
                     DARK_TEL_FIEL=files.out_dark_tel,
                     DARK_SKY_FILE=files.out_dark_sky)
cal_dark.set_debug_plots('DARK_IMAGE_REGIONS', 'DARK_HISTOGRAM')
cal_dark.set_summary_plots('SUM_DARK_IMAGE_REGIONS', 'SUM_DARK_HISTOGRAM')
cal_dark.set_arg(pos=0, **directory)
cal_dark.set_arg(name='files', dtype='files',
                 files=[files.pp_dark_dark_int, files.pp_dark_dark_tel,
                        files.pp_dark_dark_sky],
                 pos='1+', filelogic='exclusive',
                 helpstr=Help['FILES_HELP'] + Help['DARK_FILES_HELP'])
cal_dark.set_kwarg(**add_db)
cal_dark.set_kwarg(default=True, **combine)
cal_dark.set_kwarg(**plot)
# add to recipe
recipes.append(cal_dark)

# -----------------------------------------------------------------------------
# cal_dark_master_nirps_ha
# -----------------------------------------------------------------------------
cal_dark_master = DrsRecipe(__INSTRUMENT__)
cal_dark_master.name = 'cal_dark_master_nirps_ha.py'
cal_dark_master.shortname = 'DARKM'
cal_dark_master.master = True
cal_dark_master.instrument = __INSTRUMENT__
cal_dark_master.outputdir = 'red'
cal_dark_master.inputdir = 'tmp'
cal_dark_master.intputtype = 'pp'
cal_dark_master.extension = 'fits'
cal_dark_master.description = Help['DARK_MASTER_DESC']
cal_dark_master.epilog = Help['DARK_MASTER_EXAMPLE']
cal_dark_master.kind = 'recipe'
cal_dark_master.set_outputs(DARK_MASTER_FILE=files.out_dark_master)
cal_dark_master.set_kwarg(name='--filetype', dtype=str,
                          default='DARK_DARK_TEL, DARK_DARK_INT',
                          helpstr=Help['DARK_MASTER_FILETYPE'])
cal_dark_master.set_kwarg(**add_db)
cal_dark_master.set_kwarg(**plot)
# add to recipe
recipes.append(cal_dark_master)

# -----------------------------------------------------------------------------
# cal_loc_RAW_nirps_ha
# -----------------------------------------------------------------------------
cal_loc = DrsRecipe(__INSTRUMENT__)
cal_loc.name = 'cal_loc_nirps_ha.py'
cal_loc.shortname = 'LOC'
cal_loc.instrument = __INSTRUMENT__
cal_loc.outputdir = 'red'
cal_loc.inputdir = 'tmp'
cal_loc.inputtype = 'pp'
cal_loc.extension = 'fits'
cal_loc.description = Help['LOC_DESC']
cal_loc.epilog = Help['LOC_EXAMPLE']
cal_loc.kind = 'recipe'
cal_loc.set_outputs(ORDERP_FILE=files.out_loc_orderp,
                    LOCO_FILE=files.out_loc_loco,
                    FWHM_FILE=files.out_loc_fwhm,
                    SUP_FILE=files.out_loc_sup,
                    DEBUG_BACK=files.debug_back)
cal_loc.set_debug_plots('LOC_MINMAX_CENTS', 'LOC_MIN_CENTS_THRES',
                        'LOC_FINDING_ORDERS', 'LOC_IM_SAT_THRES',
                        'LOC_ORD_VS_RMS', 'LOC_CHECK_COEFFS',
                        'LOC_FIT_RESIDUALS')
cal_loc.set_summary_plots('SUM_LOC_IM_THRES', 'SUM_LOC_IM_CORNER')
cal_loc.set_arg(pos=0, **directory)
cal_loc.set_arg(name='files', dtype='files', filelogic='exclusive',
                files=[files.pp_dark_flat, files.pp_flat_dark], pos='1+',
                helpstr=Help['FILES_HELP'] + Help['LOC_FILES_HELP'])
cal_loc.set_kwarg(**add_db)
cal_loc.set_kwarg(**badfile)
cal_loc.set_kwarg(**dobad)
cal_loc.set_kwarg(**backsub)
cal_loc.set_kwarg(default=True, **combine)
cal_loc.set_kwarg(**darkfile)
cal_loc.set_kwarg(**dodark)
cal_loc.set_kwarg(**flipimage)
cal_loc.set_kwarg(**fluxunits)
cal_loc.set_kwarg(**plot)
cal_loc.set_kwarg(**resize)
# add to recipe
recipes.append(cal_loc)

# -----------------------------------------------------------------------------
# cal_shape_master_nirps_ha
# -----------------------------------------------------------------------------
cal_shape_master = DrsRecipe(__INSTRUMENT__)
cal_shape_master.name = 'cal_shape_master_nirps_ha.py'
cal_shape_master.shortname = 'SHAPEM'
cal_shape_master.master = True
cal_shape_master.instrument = __INSTRUMENT__
cal_shape_master.outputdir = 'red'
cal_shape_master.inputdir = 'tmp'
cal_shape_master.inputtype = 'pp'
cal_shape_master.extension = 'fits'
cal_shape_master.description = Help['SHAPE_DESC']
cal_shape_master.epilog = Help['SHAPEMASTER_EXAMPLE']
cal_shape_master.kind = 'recipe'
cal_shape_master.set_outputs(FPMASTER_FILE=files.out_shape_fpmaster,
                             DXMAP_FILE=files.out_shape_dxmap,
                             DYMAP_FILE=files.out_shape_dymap,
                             SHAPE_IN_FP_FILE=files.out_shape_debug_ifp,
                             SHAPE_OUT_FP_FILE=files.out_shape_debug_ofp,
                             SHAPE_BDXMAP_FILE=files.out_shape_debug_bdx,
                             DEBUG_BACK=files.debug_back)
cal_shape_master.set_debug_plots('SHAPE_DX', 'SHAPE_ANGLE_OFFSET_ALL',
                                 'SHAPE_ANGLE_OFFSET', 'SHAPE_LINEAR_TPARAMS')
cal_shape_master.set_summary_plots('SUM_SHAPE_ANGLE_OFFSET')
cal_shape_master.set_arg(pos=0, **directory)
cal_shape_master.set_kwarg(name='--fpfiles', dtype='files',
                           files=[files.pp_fp_fp],
                           filelogic='exclusive', required=True,
                           helpstr=Help['SHAPE_FPFILES_HELP'], default=[])
cal_shape_master.set_kwarg(**add_db)
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
cal_shape_master.set_kwarg(**resize)
cal_shape_master.set_kwarg(name='--fpmaster', dtype='files',
                           files=[files.out_shape_fpmaster], default='None',
                           helpstr=Help['SHAPE_FPMASTER_HELP'])
# add to recipe
recipes.append(cal_shape_master)

# -----------------------------------------------------------------------------
# cal_SHAPE_nirps_ha
# -----------------------------------------------------------------------------
cal_shape = DrsRecipe(__INSTRUMENT__)
cal_shape.name = 'cal_shape_nirps_ha.py'
cal_shape.shortname = 'SHAPE'
cal_shape.instrument = __INSTRUMENT__
cal_shape.outputdir = 'red'
cal_shape.inputdir = 'tmp'
cal_shape.inputtype = 'pp'
cal_shape.extension = 'fits'
cal_shape.description = Help['SHAPE_DESC']
cal_shape.epilog = Help['SHAPE_EXAMPLE']
cal_shape.kind = 'recipe'
cal_shape.set_outputs(LOCAL_SHAPE_FILE=files.out_shape_local,
                      SHAPEL_IN_FP_FILE=files.out_shapel_debug_ifp,
                      SHAPEL_OUT_FP_FILE=files.out_shapel_debug_ofp,
                      DEBUG_BACK=files.debug_back)
cal_shape.set_debug_plots('SHAPEL_ZOOM_SHIFT', 'SHAPE_LINEAR_TPARAMS')
cal_shape.set_summary_plots('SUM_SHAPEL_ZOOM_SHIFT')
cal_shape.set_arg(pos=0, **directory)
cal_shape.set_arg(name='files', dtype='files', files=[files.pp_fp_fp], pos='1+',
                  helpstr=Help['SHAPE_FPFILES_HELP'])
cal_shape.set_kwarg(**add_db)
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
cal_shape.set_kwarg(**resize)
cal_shape.set_kwarg(**shapexfile)
cal_shape.set_kwarg(**shapeyfile)
# add to recipe
recipes.append(cal_shape)

# -----------------------------------------------------------------------------
# cal_FF_RAW_nirps_ha
# -----------------------------------------------------------------------------
cal_ff = DrsRecipe(__INSTRUMENT__)
cal_ff.name = 'cal_flat_nirps_ha.py'
cal_ff.shortname = 'FF'
cal_ff.instrument = __INSTRUMENT__
cal_ff.outputdir = 'red'
cal_ff.inputdir = 'tmp'
cal_ff.inputtype = 'pp'
cal_ff.extension = 'fits'
cal_ff.description = Help['FLAT_DESC']
cal_ff.epilog = Help['FLAT_EXAMPLE']
cal_ff.kind = 'recipe'
cal_ff.set_outputs(FLAT_FILE=files.out_ff_flat,
                   BLAZE_FILE=files.out_ff_blaze,
                   E2DSLL_FILE=files.out_ext_e2dsll,
                   ORDERP_SFILE=files.out_orderp_straight,
                   DEBUG_BACK=files.debug_back)
cal_ff.set_debug_plots('FLAT_ORDER_FIT_EDGES1', 'FLAT_ORDER_FIT_EDGES2',
                       'FLAT_BLAZE_ORDER1', 'FLAT_BLAZE_ORDER2')
cal_ff.set_summary_plots('SUM_FLAT_ORDER_FIT_EDGES', 'SUM_FLAT_BLAZE_ORDER')
cal_ff.set_arg(pos=0, **directory)
cal_ff.set_arg(name='files', dtype='files', filelogic='exclusive',
               files=[files.pp_flat_flat], pos='1+',
               helpstr=Help['FILES_HELP'] + Help['FLAT_FILES_HELP'])
cal_ff.set_kwarg(**add_db)
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
cal_ff.set_kwarg(**resize)
cal_ff.set_kwarg(**shapexfile)
cal_ff.set_kwarg(**shapeyfile)
cal_ff.set_kwarg(**shapelfile)
# add to recipe
recipes.append(cal_ff)

# -----------------------------------------------------------------------------
# cal_thermal_nirps_ha
# -----------------------------------------------------------------------------
cal_thermal = DrsRecipe(__INSTRUMENT__)
cal_thermal.name = 'cal_thermal_nirps_ha.py'
cal_thermal.shortname = 'THERM'
cal_thermal.instrument = __INSTRUMENT__
cal_thermal.outputdir = 'red'
cal_thermal.inputdir = 'tmp'
cal_thermal.inputtype = 'pp'
cal_thermal.extension = 'fits'
cal_thermal.description = Help['EXTRACT_DESC']
cal_thermal.epilog = Help['EXTRACT_EXAMPLE']
cal_thermal.kind = 'recipe'
# TODO: Need to add out_thermal_e2ds_sky
cal_thermal.set_outputs(THERMAL_E2DS_FILE=files.out_ext_e2dsff,
                        THERMALI_FILE=files.out_thermal_e2ds_int,
                        THERMALT_FILE=files.out_thermal_e2ds_tel)
cal_thermal.set_arg(pos=0, **directory)
# TODO: Need to add files.pp_dark_dark_sky
cal_thermal.set_arg(name='files', dtype='files', pos='1+',
                    files=[files.pp_dark_dark_int, files.pp_dark_dark_tel],
                    filelogic='exclusive',
                    helpstr=Help['FILES_HELP'] + Help['EXTRACT_FILES_HELP'],
                    limit=1)
cal_thermal.set_kwarg(**add_db)
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
cal_thermal.set_kwarg(**resize)
cal_thermal.set_kwarg(**shapexfile)
cal_thermal.set_kwarg(**shapeyfile)
cal_thermal.set_kwarg(**shapelfile)
cal_thermal.set_kwarg(**wavefile)
cal_thermal.set_kwarg(name='--forceext', dtype='bool',
                      default_ref='THERMAL_ALWAYS_EXTRACT',
                      helpstr='THERMAL_EXTRACT_HELP')
# add to recipe
recipes.append(cal_thermal)

# -----------------------------------------------------------------------------
# cal_leak_master_nirps_ha
# -----------------------------------------------------------------------------
cal_leak_master = DrsRecipe(__INSTRUMENT__)
cal_leak_master.name = 'cal_leak_master_nirps_ha.py'
cal_leak_master.shortname = 'LEAKM'
cal_leak_master.master = True
cal_leak_master.instrument = __INSTRUMENT__
cal_leak_master.outputdir = 'red'
cal_leak_master.inputdir = 'tmp'
cal_leak_master.intputtype = 'pp'
cal_leak_master.extension = 'fits'
cal_leak_master.description = Help['LEAKM_DESC']
cal_leak_master.epilog = Help['LEAKM_EXAMPLE']
cal_leak_master.kind = 'recipe'
cal_leak_master.set_outputs(LEAK_E2DS_FILE=files.out_ext_e2dsff,
                            LEAK_MASTER=files.out_leak_master)
cal_leak_master.set_arg(pos=0, **directory)
cal_leak_master.set_kwarg(name='--filetype', dtype=str, default='DARK_FP',
                          helpstr=Help['LEAKM_HELP_FILETYPE'])
cal_leak_master.set_kwarg(**add_db)
cal_leak_master.set_kwarg(**plot)
# add to recipe
recipes.append(cal_leak_master)

# -----------------------------------------------------------------------------
# cal_leak_mnirps_ha
# -----------------------------------------------------------------------------
cal_leak = DrsRecipe(__INSTRUMENT__)
cal_leak.name = 'cal_leak_nirps_ha.py'
cal_leak.shortname = 'LEAK'
cal_leak.instrument = __INSTRUMENT__
cal_leak.outputdir = 'red'
cal_leak.inputdir = 'red'
cal_leak.intputtype = 'red'
cal_leak.extension = 'fits'
cal_leak.description = Help['LEAK_DESC']
cal_leak.epilog = Help['LEAK_EXAMPLE']
cal_leak.kind = 'recipe'
cal_leak.set_outputs(E2DS_FILE=files.out_ext_e2ds,
                     E2DSFF_FILE=files.out_ext_e2dsff,
                     E2DSLL_FILE=files.out_ext_e2dsll,
                     S1D_W_FILE=files.out_ext_s1d_w,
                     S1D_V_FILE=files.out_ext_s1d_v)
cal_leak.set_arg(pos=0, **directory)
cal_leak.set_arg(name='files', dtype='files', pos='1+',
                 files=[files.out_ext_e2dsff],
                 helpstr=Help['FILES_HELP'] + Help['LEAK_FILES_HELP'],
                 limit=1)
cal_leak.set_kwarg(**add_db)
cal_leak.set_kwarg(**plot)
cal_leak.set_kwarg(name='--leakfile', dtype='file', default='None',
                   files=[files.out_leak_master],
                   helpstr=Help['LEAK_LEAKFILE_HELP'])
# add to recipe
recipes.append(cal_leak)

# -----------------------------------------------------------------------------
# cal_extract_nirps_ha
# -----------------------------------------------------------------------------
cal_extract = DrsRecipe(__INSTRUMENT__)
cal_extract.name = 'cal_extract_nirps_ha.py'
cal_extract.shortname = 'EXT'
cal_extract.instrument = __INSTRUMENT__
cal_extract.outputdir = 'red'
cal_extract.inputdir = 'tmp'
cal_extract.inputtype = 'pp'
cal_extract.extension = 'fits'
cal_extract.description = Help['EXTRACT_DESC']
cal_extract.epilog = Help['EXTRACT_EXAMPLE']
cal_extract.kind = 'recipe'
cal_extract.set_outputs(E2DS_FILE=files.out_ext_e2ds,
                        E2DSFF_FILE=files.out_ext_e2dsff,
                        E2DSLL_FILE=files.out_ext_e2dsll,
                        S1D_W_FILE=files.out_ext_s1d_w,
                        S1D_V_FILE=files.out_ext_s1d_v,
                        ORDERP_SFILE=files.out_orderp_straight,
                        DEBUG_BACK=files.debug_back,
                        EXT_FPLINES=files.out_ext_fplines)
cal_extract.set_debug_plots('FLAT_ORDER_FIT_EDGES1', 'FLAT_ORDER_FIT_EDGES2',
                            'FLAT_BLAZE_ORDER1', 'FLAT_BLAZE_ORDER2',
                            'THERMAL_BACKGROUND', 'EXTRACT_SPECTRAL_ORDER1',
                            'EXTRACT_SPECTRAL_ORDER2', 'EXTRACT_S1D',
                            'EXTRACT_S1D_WEIGHT')
cal_extract.set_summary_plots('SUM_FLAT_ORDER_FIT_EDGES',
                              'SUM_EXTRACT_SP_ORDER', 'SUM_EXTRACT_S1D')
cal_extract.set_arg(pos=0, **directory)
cal_extract.set_arg(name='files', dtype='files', pos='1+',
                    files=[files.pp_file],
                    helpstr=Help['FILES_HELP'] + Help['EXTRACT_FILES_HELP'],
                    limit=1)
cal_extract.set_kwarg(**badfile)
cal_extract.set_kwarg(**dobad)
cal_extract.set_kwarg(**backsub)
cal_extract.set_kwarg(**blazefile)
cal_extract.set_kwarg(default=False, **combine)
cal_extract.set_kwarg(**objname)
cal_extract.set_kwarg(**dprtype)
cal_extract.set_kwarg(**darkfile)
cal_extract.set_kwarg(**dodark)
cal_extract.set_kwarg(**fiber)
cal_extract.set_kwarg(**flipimage)
cal_extract.set_kwarg(**fluxunits)
cal_extract.set_kwarg(**flatfile)
cal_extract.set_kwarg(**locofile)
cal_extract.set_kwarg(**orderpfile)
cal_extract.set_kwarg(**plot)
cal_extract.set_kwarg(**resize)
cal_extract.set_kwarg(**shapexfile)
cal_extract.set_kwarg(**shapeyfile)
cal_extract.set_kwarg(**shapelfile)
cal_extract.set_kwarg(name='--thermal', dtype='bool', default=True,
                      helpstr=Help['THERMAL_HELP'],
                      default_ref='THERMAL_CORRECT')
cal_extract.set_kwarg(**thermalfile)
cal_extract.set_kwarg(**wavefile)
# add to recipe
recipes.append(cal_extract)

# -----------------------------------------------------------------------------
# cal_wave_master
# -----------------------------------------------------------------------------
cal_wave_master = DrsRecipe(__INSTRUMENT__)
cal_wave_master.name = 'cal_wave_master_nirps_ha.py'
cal_wave_master.shortname = 'WAVEM'
cal_wave_master.instrument = __INSTRUMENT__
cal_wave_master.outputdir = 'red'
cal_wave_master.inputdir = 'tmp'
cal_wave_master.inputtype = 'pp'
cal_wave_master.extension = 'fits'
cal_wave_master.description = Help['WAVE_DESC']
cal_wave_master.epilog = Help['WAVE_EXAMPLE']
cal_wave_master.kind = 'recipe'
cal_wave_master.set_outputs(WAVE_E2DS=files.out_ext_e2dsff,
                            WAVE_HCLL=files.out_wave_hcline,
                            WAVEM_HCRES=files.out_wavem_hcres,
                            WAVEM_HCMAP=files.out_wavem_hc,
                            WAVEM_FPMAP=files.out_wavem_fp,
                            WAVEM_FPRESTAB=files.out_wavem_res_table,
                            WAVEM_FPLLTAB=files.out_wavem_ll_table,
                            WAVEM_HCLIST=files.out_wave_hclist_master,
                            WAVEM_FPLIST=files.out_wave_fplist_master,
                            CCF_RV=files.out_ccf_fits)
cal_wave_master.set_debug_plots('WAVE_HC_GUESS', 'WAVE_HC_BRIGHTEST_LINES',
                                'WAVE_HC_TFIT_GRID', 'WAVE_HC_RESMAP',
                                'WAVE_LITTROW_CHECK1', 'WAVE_LITTROW_EXTRAP1',
                                'WAVE_LITTROW_CHECK2', 'WAVE_LITTROW_EXTRAP2',
                                'WAVE_FP_FINAL_ORDER', 'WAVE_FP_LWID_OFFSET',
                                'WAVE_FP_WAVE_RES', 'WAVE_FP_M_X_RES',
                                'WAVE_FP_IPT_CWID_1MHC',
                                'WAVE_FP_IPT_CWID_LLHC',
                                'WAVE_FP_LL_DIFF', 'WAVE_FP_MULTI_ORDER',
                                'WAVE_FP_SINGLE_ORDER',
                                'CCF_RV_FIT', 'CCF_RV_FIT_LOOP',
                                'WAVEREF_EXPECTED', 'EXTRACT_S1D',
                                'EXTRACT_S1D_WEIGHT', 'WAVE_FIBER_COMPARISON',
                                'WAVE_FIBER_COMP', 'WAVENIGHT_ITERPLOT',
                                'WAVENIGHT_HISTPLOT')
cal_wave_master.set_summary_plots('SUM_WAVE_FP_IPT_CWID_LLHC',
                                  'SUM_WAVE_LITTROW_CHECK',
                                  'SUM_WAVE_LITTROW_EXTRAP',
                                  'SUM_CCF_RV_FIT', 'SUM_WAVE_FIBER_COMP',
                                  'SUM_WAVENIGHT_ITERPLOT',
                                  'SUM_WAVENIGHT_HISTPLOT', )
cal_wave_master.set_arg(pos=0, **directory)
cal_wave_master.set_kwarg(name='--hcfiles', dtype='files',
                          files=[files.pp_hc1_hc1],
                          filelogic='exclusive', required=True,
                          helpstr=Help['WAVE_HCFILES_HELP'], default=[])
cal_wave_master.set_kwarg(name='--fpfiles', dtype='files',
                          files=[files.pp_fp_fp],
                          filelogic='exclusive', required=True,
                          helpstr=Help['WAVE_FPFILES_HELP'], default=[])
cal_wave_master.set_kwarg(**add_db)
cal_wave_master.set_kwarg(**badfile)
cal_wave_master.set_kwarg(**dobad)
cal_wave_master.set_kwarg(**backsub)
cal_wave_master.set_kwarg(**blazefile)
cal_wave_master.set_kwarg(default=True, **combine)
cal_wave_master.set_kwarg(**darkfile)
cal_wave_master.set_kwarg(**dodark)
cal_wave_master.set_kwarg(**fiber)
cal_wave_master.set_kwarg(**flipimage)
cal_wave_master.set_kwarg(**fluxunits)
cal_wave_master.set_kwarg(**locofile)
cal_wave_master.set_kwarg(**orderpfile)
cal_wave_master.set_kwarg(**plot)
cal_wave_master.set_kwarg(**resize)
cal_wave_master.set_kwarg(**shapexfile)
cal_wave_master.set_kwarg(**shapeyfile)
cal_wave_master.set_kwarg(**shapelfile)
cal_wave_master.set_kwarg(**wavefile)
cal_wave_master.set_kwarg(name='--forceext', dtype='bool',
                          default_ref='WAVE_ALWAYS_EXTRACT',
                          helpstr='WAVE_EXTRACT_HELP')
cal_wave_master.set_kwarg(name='--hcmode', dtype='options',
                          helpstr=Help['HCMODE_HELP'], options=['0'],
                          default_ref='WAVE_MODE_HC')
cal_wave_master.set_kwarg(name='--fpmode', dtype='options',
                          helpstr=Help['FPMODE_HELP'], options=['0', '1'],
                          default_ref='WAVE_MODE_FP')
# add to recipe
recipes.append(cal_wave_master)

# -----------------------------------------------------------------------------
# cal_wave_night_nirps_ha
# -----------------------------------------------------------------------------
cal_wave_night = DrsRecipe(__INSTRUMENT__)
cal_wave_night.name = 'cal_wave_night_nirps_ha.py'
cal_wave_night.shortname = 'WAVE'
cal_wave_night.instrument = __INSTRUMENT__
cal_wave_night.outputdir = 'red'
cal_wave_night.inputdir = 'tmp'
cal_wave_night.inputtype = 'pp'
cal_wave_night.extension = 'fits'
cal_wave_night.description = Help['WAVE_DESC']
cal_wave_night.epilog = Help['WAVE_EXAMPLE']
cal_wave_night.kind = 'recipe'
cal_wave_night.set_outputs(WAVE_E2DS=files.out_ext_e2dsff,
                           WAVEMAP_NIGHT=files.out_wave_night,
                           WAVE_HCLIST=files.out_wave_hclist,
                           WAVE_FPLIST=files.out_wave_fplist,
                           CCF_RV=files.out_ccf_fits)
cal_wave_night.set_debug_plots('WAVENIGHT_ITERPLOT', 'WAVENIGHT_HISTPLOT',
                               'WAVEREF_EXPECTED', 'CCF_RV_FIT',
                               'CCF_RV_FIT_LOOP', 'EXTRACT_S1D',
                               'EXTRACT_S1D_WEIGHT')
cal_wave_night.set_summary_plots('SUM_WAVENIGHT_ITERPLOT',
                                 'SUM_WAVENIGHT_HISTPLOT',
                                 'SUM_CCF_RV_FIT')
cal_wave_night.set_arg(pos=0, **directory)
cal_wave_night.set_kwarg(name='--hcfiles', dtype='files',
                         files=[files.pp_hc1_hc1],
                         filelogic='exclusive', required=True,
                         helpstr=Help['WAVE_HCFILES_HELP'], default=[])
cal_wave_night.set_kwarg(name='--fpfiles', dtype='files',
                         files=[files.pp_fp_fp],
                         filelogic='exclusive', required=True,
                         helpstr=Help['WAVE_FPFILES_HELP'], default=[])
cal_wave_night.set_kwarg(**add_db)
cal_wave_night.set_kwarg(**badfile)
cal_wave_night.set_kwarg(**dobad)
cal_wave_night.set_kwarg(**backsub)
cal_wave_night.set_kwarg(**blazefile)
cal_wave_night.set_kwarg(default=True, **combine)
cal_wave_night.set_kwarg(**darkfile)
cal_wave_night.set_kwarg(**dodark)
cal_wave_night.set_kwarg(**fiber)
cal_wave_night.set_kwarg(**flipimage)
cal_wave_night.set_kwarg(**fluxunits)
cal_wave_night.set_kwarg(**locofile)
cal_wave_night.set_kwarg(**orderpfile)
cal_wave_night.set_kwarg(**plot)
cal_wave_night.set_kwarg(**resize)
cal_wave_night.set_kwarg(**shapexfile)
cal_wave_night.set_kwarg(**shapeyfile)
cal_wave_night.set_kwarg(**shapelfile)
cal_wave_night.set_kwarg(**wavefile)
cal_wave_night.set_kwarg(name='--forceext', dtype='bool',
                         default_ref='WAVE_ALWAYS_EXTRACT',
                         helpstr='WAVE_EXTRACT_HELP')
# add to recipe
recipes.append(cal_wave_night)

# -----------------------------------------------------------------------------
# cal_DRIFT_E2DS_nirps_ha
# -----------------------------------------------------------------------------
cal_drift1 = DrsRecipe(__INSTRUMENT__)
cal_drift1.name = 'cal_DRIFT_E2DS_nirps_ha.py'
# add to recipe
recipes.append(cal_drift1)

# -----------------------------------------------------------------------------
# cal_DRIFTPEAK_E2DS_nirps_ha
# -----------------------------------------------------------------------------
cal_drift2 = DrsRecipe(__INSTRUMENT__)
cal_drift2.name = 'cal_DRIFTPEAK_E2DS_nirps_ha.py'
# add to recipe
recipes.append(cal_drift2)

# -----------------------------------------------------------------------------
# cal_CCF_E2DS_nirps_ha
# -----------------------------------------------------------------------------
cal_ccf = DrsRecipe(__INSTRUMENT__)
cal_ccf.name = 'cal_ccf_nirps_ha.py'
cal_ccf.shortname = 'CCF'
cal_ccf.instrument = __INSTRUMENT__
cal_ccf.outputdir = 'red'
cal_ccf.inputdir = 'red'
cal_ccf.inputtype = 'red'
cal_ccf.extension = 'fits'
cal_ccf.description = Help['CCF_DESC']
cal_ccf.epilog = Help['CCF_EXAMPLE']
cal_ccf.kind = 'recipe'
cal_ccf.set_outputs(CCF_RV=files.out_ccf_fits)
cal_ccf.set_debug_plots('CCF_RV_FIT', 'CCF_RV_FIT_LOOP', 'CCF_SWAVE_REF',
                        'CCF_PHOTON_UNCERT')
cal_ccf.set_summary_plots('SUM_CCF_PHOTON_UNCERT', 'SUM_CCF_RV_FIT')
cal_ccf.set_arg(pos=0, **directory)
cal_ccf.set_arg(name='files', dtype='files', pos='1+',
                files=[files.out_ext_e2ds, files.out_ext_e2dsff,
                       files.out_tellu_obj], filelogic='exclusive',
                helpstr=Help['FILES_HELP'] + Help['CCF_FILES_HELP'],
                limit=1)
cal_ccf.set_kwarg(name='--mask', dtype='file', default_ref='CCF_DEFAULT_MASK',
                  helpstr=Help['CCF_MASK_HELP'],
                  files=files.other_ccf_mask_file)
cal_ccf.set_kwarg(name='--rv', dtype=float, default_ref='CCF_NO_RV_VAL',
                  helpstr=Help['CCF_RV_HELP'])
cal_ccf.set_kwarg(name='--width', dtype=float, default_ref='CCF_DEFAULT_WIDTH',
                  helpstr=Help['CCF_WIDTH_HELP'])
cal_ccf.set_kwarg(name='--step', dtype=float, default_ref='CCF_DEFAULT_STEP',
                  helpstr=Help['CCF_STEP_HELP'])
cal_ccf.set_kwarg(**add_db)
cal_ccf.set_kwarg(**blazefile)
cal_ccf.set_kwarg(**plot)
# add to recipe
recipes.append(cal_ccf)

# -----------------------------------------------------------------------------
# obj_mk_tellu_nirps_ha
# -----------------------------------------------------------------------------
obj_mk_tellu = DrsRecipe(__INSTRUMENT__)
obj_mk_tellu.name = 'obj_mk_tellu_nirps_ha.py'
obj_mk_tellu.shortname = 'MKTELL'
obj_mk_tellu.instrument = __INSTRUMENT__
obj_mk_tellu.outputdir = 'red'
obj_mk_tellu.inputdir = 'red'
obj_mk_tellu.inputtype = 'red'
obj_mk_tellu.extension = 'fits'
obj_mk_tellu.description = Help['MKTELL_DESC']
obj_mk_tellu.epilog = Help['MKTELL_EXAMPLE']
obj_mk_tellu.kind = 'recipe'
obj_mk_tellu.set_outputs(TELLU_CONV=files.out_tellu_conv,
                         TELLU_TRANS=files.out_tellu_trans,
                         TELLU_PCLEAN=files.out_tellu_pclean)
obj_mk_tellu.set_debug_plots('MKTELLU_WAVE_FLUX1', 'MKTELLU_WAVE_FLUX2',
                             'TELLUP_WAVE_TRANS', 'TELLUP_ABSO_SPEC')
obj_mk_tellu.set_summary_plots('SUM_MKTELLU_WAVE_FLUX',
                               'SUM_TELLUP_WAVE_TRANS', 'SUM_TELLUP_ABSO_SPEC')
obj_mk_tellu.set_arg(pos=0, **directory)
obj_mk_tellu.set_arg(name='files', dtype='files', pos='1+',
                     files=[files.out_ext_e2ds, files.out_ext_e2dsff],
                     filelogic='exclusive',
                     helpstr=Help['FILES_HELP'] + Help['MKTELL_FILES_HELP'],
                     limit=1)
obj_mk_tellu.set_kwarg(**add_db)
obj_mk_tellu.set_kwarg(**blazefile)
obj_mk_tellu.set_kwarg(**plot)
obj_mk_tellu.set_kwarg(**wavefile)
# TODO: Add to language DB
obj_mk_tellu.set_kwarg(name='--use_template', dtype='bool', default=True,
                       helpstr='Whether to use the template provided from '
                               'the telluric database')
# add to recipe
recipes.append(obj_mk_tellu)

# -----------------------------------------------------------------------------
# obj_mk_tellu_db_nirps_ha
# -----------------------------------------------------------------------------
obj_mk_tellu_db = DrsRecipe(__INSTRUMENT__)
obj_mk_tellu_db.name = 'obj_mk_tellu_db_nirps_ha.py'
obj_mk_tellu_db.shortname = 'MKTELLDB'
obj_mk_tellu_db.master = False
obj_mk_tellu_db.instrument = __INSTRUMENT__
obj_mk_tellu_db.outputdir = 'red'
obj_mk_tellu_db.inputdir = 'red'
obj_mk_tellu_db.inputtype = 'red'
obj_mk_tellu_db.extension = 'fits'
obj_mk_tellu_db.kind = 'recipe'
obj_mk_tellu_db.description = Help['MKTELLDB_DESC']
obj_mk_tellu_db.epilog = Help['MKTELLDB_EXAMPLE']
obj_mk_tellu_db.set_outputs()
obj_mk_tellu_db.set_kwarg(name='--cores', dtype=int, default=1,
                          helpstr=Help['MKTELLDB_CORES'])
obj_mk_tellu_db.set_kwarg(name='--filetype', dtype=str,
                          default_ref='TELLURIC_FILETYPE',
                          helpstr=Help['MKTELLDB_FILETYPE'],
                          options=['EXT_E2DS', 'EXT_E2DS_FF'])
obj_mk_tellu_db.set_kwarg(name='--fiber', dtype=str,
                          default_ref='TELLURIC_FIBER_TYPE',
                          helpstr=Help['MKTELLDB_FIBER'],
                          options=['AB', 'A', 'B', 'C'])
obj_mk_tellu_db.set_kwarg(name='--test', dtype=str, default='None',
                          options=['True', 'False', '1', '0', 'None'],
                          helpstr=Help['PROCESS_TEST_HELP'])
obj_mk_tellu_db.set_kwarg(**add_db)
obj_mk_tellu_db.set_kwarg(**blazefile)
obj_mk_tellu_db.set_kwarg(**plot)
obj_mk_tellu_db.set_kwarg(**wavefile)
# add to recipe
recipes.append(obj_mk_tellu_db)

# -----------------------------------------------------------------------------
# obj_fit_tellu_nirps_ha
# -----------------------------------------------------------------------------
obj_fit_tellu = DrsRecipe(__INSTRUMENT__)
obj_fit_tellu.name = 'obj_fit_tellu_nirps_ha.py'
obj_fit_tellu.shortname = 'FTELLU'
obj_fit_tellu.instrument = __INSTRUMENT__
obj_fit_tellu.outputdir = 'red'
obj_fit_tellu.inputdir = 'red'
obj_fit_tellu.inputtype = 'red'
obj_fit_tellu.extension = 'fits'
obj_fit_tellu.description = Help['FTELLU_DESC']
obj_fit_tellu.epilog = Help['FTELLU_EXAMPLE']
obj_fit_tellu.kind = 'recipe'
obj_fit_tellu.set_outputs(ABSO_NPY=files.out_tellu_abso_npy,
                          ABSO1_NPY=files.out_tellu_abso1_npy,
                          TELLU_OBJ=files.out_tellu_obj,
                          SC1D_W_FILE=files.out_tellu_sc1d_w,
                          SC1D_V_FILE=files.out_tellu_sc1d_v,
                          TELLU_RECON=files.out_tellu_recon,
                          RC1D_W_FILE=files.out_tellu_rc1d_w,
                          RC1D_V_FILE=files.out_tellu_rc1d_v,
                          TELLU_PCLEAN=files.out_tellu_pclean)
obj_fit_tellu.set_debug_plots('EXTRACT_S1D', 'EXTRACT_S1D_WEIGHT',
                              'FTELLU_PCA_COMP1', 'FTELLU_PCA_COMP2',
                              'FTELLU_RECON_SPLINE1', 'FTELLU_RECON_SPLINE2',
                              'FTELLU_WAVE_SHIFT1', 'FTELLU_WAVE_SHIFT2',
                              'FTELLU_RECON_ABSO1', 'FTELLU_RECON_ABSO2',
                              'TELLUP_WAVE_TRANS', 'TELLUP_ABSO_SPEC')
obj_fit_tellu.set_summary_plots('SUM_EXTRACT_S1D', 'SUM_FTELLU_RECON_ABSO',
                                'SUM_TELLUP_WAVE_TRANS', 'SUM_TELLUP_ABSO_SPEC')
obj_fit_tellu.set_arg(pos=0, **directory)
obj_fit_tellu.set_arg(name='files', dtype='files', pos='1+',
                      files=[files.out_ext_e2ds, files.out_ext_e2dsff],
                      filelogic='exclusive',
                      helpstr=Help['FILES_HELP'] + Help['FTELLU_FILES_HELP'],
                      limit=1)
# TODO: Add to language DB
obj_fit_tellu.set_kwarg(name='--use_template', dtype='bool', default=True,
                        helpstr='Whether to use the template provided from '
                                'the telluric database')
obj_fit_tellu.set_kwarg(**add_db)
obj_fit_tellu.set_kwarg(**blazefile)
obj_fit_tellu.set_kwarg(**plot)
obj_fit_tellu.set_kwarg(**wavefile)
# add to recipe
recipes.append(obj_fit_tellu)

# -----------------------------------------------------------------------------
# obj_fit_tellu_db_nirps_ha
# -----------------------------------------------------------------------------
obj_fit_tellu_db = DrsRecipe(__INSTRUMENT__)
obj_fit_tellu_db.name = 'obj_fit_tellu_db_nirps_ha.py'
obj_fit_tellu_db.shortname = 'FTELLDB'
obj_fit_tellu_db.master = False
obj_fit_tellu_db.instrument = __INSTRUMENT__
obj_fit_tellu_db.outputdir = 'red'
obj_fit_tellu_db.inputdir = 'red'
obj_fit_tellu_db.inputtype = 'red'
obj_fit_tellu_db.extension = 'fits'
obj_fit_tellu_db.description = Help['FTELLUDB_DESC']
obj_fit_tellu_db.epilog = Help['FTELLUDB_EXAMPLE']
obj_fit_tellu_db.kind = 'recipe'
obj_fit_tellu_db.set_outputs()
obj_fit_tellu_db.set_kwarg(name='--cores', dtype=int, default=1,
                           helpstr=Help['FTELLUDB_CORES'])
obj_fit_tellu_db.set_kwarg(name='--filetype', dtype=str,
                           default_ref='TELLURIC_FILETYPE',
                           helpstr=Help['FTELLUDB_FILETYPE'])
obj_fit_tellu_db.set_kwarg(name='--fiber', dtype=str,
                           default_ref='TELLURIC_FIBER_TYPE',
                           helpstr=Help['FTELLUDB_FIBER'])
obj_fit_tellu_db.set_kwarg(name='--objname', dtype=str, default='None',
                           helpstr=Help['FTELLUDB_OBJNAME'])
obj_fit_tellu_db.set_kwarg(name='--dprtype', dtype=str,
                           default_ref='TELLU_ALLOWED_DPRTYPES',
                           helpstr=Help['FTELLUDB_DPRTYPES'])
obj_fit_tellu_db.set_kwarg(name='--test', dtype=str, default='None',
                           options=['True', 'False', '1', '0', 'None'],
                           helpstr=Help['PROCESS_TEST_HELP'])
obj_fit_tellu_db.set_kwarg(**add_db)
obj_fit_tellu_db.set_kwarg(**add_db)
obj_fit_tellu_db.set_kwarg(**plot)
obj_fit_tellu_db.set_kwarg(**wavefile)
# add to recipe
recipes.append(obj_fit_tellu_db)

# -----------------------------------------------------------------------------
# obj_mk_template_nirps_ha
# -----------------------------------------------------------------------------
obj_mk_template = DrsRecipe(__INSTRUMENT__)
obj_mk_template.name = 'obj_mk_template_nirps_ha.py'
obj_mk_template.shortname = 'MKTEMP'
obj_mk_template.instrument = __INSTRUMENT__
obj_mk_template.outputdir = 'red'
obj_mk_template.inputdir = 'red'
obj_mk_template.inputtype = 'red'
obj_mk_template.extension = 'fits'
obj_mk_template.description = Help['MKTEMP_DESC']
obj_mk_template.epilog = Help['MKTEMP_EXAMPLE']
obj_mk_template.kind = 'recipe'
obj_mk_template.set_outputs(TELLU_TEMP=files.out_tellu_template,
                            TELLU_BIGCUBE=files.out_tellu_bigcube,
                            TELLU_BIGCUBE0=files.out_tellu_bigcube0,
                            TELLU_TEMP_S1D=files.out_tellu_s1d_template,
                            TELLU_BIGCUBE_S1D=files.out_tellu_s1d_bigcube)
obj_mk_template.set_debug_plots('EXTRACT_S1D')
obj_mk_template.set_summary_plots('SUM_EXTRACT_S1D')
obj_mk_template.set_arg(name='objname', pos=0, dtype=str,
                        helpstr=Help['MKTEMP_OBJNAME_HELP'])
obj_mk_template.set_kwarg(name='--filetype', dtype=str,
                          default_ref='MKTEMPLATE_FILETYPE',
                          helpstr=Help['MKTEMP_FILETYPE'],
                          options=['EXT_E2DS', 'EXT_E2DS_FF'])
obj_mk_template.set_kwarg(name='--fiber', dtype=str,
                          default_ref='MKTEMPLATE_FIBER_TYPE',
                          helpstr=Help['MKTEMP_FIBER'],
                          options=['AB', 'A', 'B', 'C'])
obj_mk_template.set_kwarg(**add_db)
obj_mk_template.set_kwarg(**blazefile)
obj_mk_template.set_kwarg(**plot)
obj_mk_template.set_kwarg(**wavefile)
# add to recipe
recipes.append(obj_mk_template)

# -----------------------------------------------------------------------------
# obj_spec_nirps_ha
# -----------------------------------------------------------------------------
obj_spec = DrsRecipe(__INSTRUMENT__)
obj_spec.name = 'obj_spec_nirps_ha.py'
obj_spec.shortname = 'OBJ_SPEC'
obj_spec.instrument = __INSTRUMENT__
obj_spec.outputdir = 'red'
obj_spec.inputdir = 'tmp'
obj_spec.inputtype = 'red'
obj_spec.extension = 'fits'
obj_spec.description = ''
obj_spec.epilog = ''
obj_spec.kind = 'recipe'
obj_spec.set_arg(pos=0, **directory)
obj_spec.set_arg(name='files', dtype='files', pos='1+',
                 files=[files.pp_file],
                 helpstr=Help['FILES_HELP'] + Help['EXTRACT_FILES_HELP'],
                 limit=1)
obj_spec.set_kwarg(**plot)
obj_spec.set_kwarg(name='--cores', dtype=int, default=1,
                   helpstr='')
# add to recipe
recipes.append(obj_spec)

# -----------------------------------------------------------------------------
# cal_exposure_meter
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# cal_wave_mapper
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# visu_RAW_nirps_ha
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# visu_E2DS_nirps_ha
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
#               files=[files.file_defintion], KW_HEADER='RUN_FILE_VARIABLE')
#
#
#   Example:
#           # the below example creates a run called 'run'
#           # it just extracts OBJ_FP files with OBJECT NAME listed in
#           #  'SCIENCE_TARGETS' in the runfile
#           # note as master=True it will only extract from the master night
#
#           run = drs_recipe.DrsRunSequence('run', __INSTRUMENT__)
#           run.add(cal_extract, master=True, files=[files.pp_obj_fp],
#                   KW_OBJNAME='SCIENCE_TARGETS')
#
#
#  Note: must add sequences to sequences list to be able to use!
#
# -----------------------------------------------------------------------------
# full seqeunce (master + nights)
# -----------------------------------------------------------------------------
full_seq = drs_recipe.DrsRunSequence('full_seq', __INSTRUMENT__)
# master run
full_seq.add(cal_pp_master, master=True)
full_seq.add(cal_pp)
full_seq.add(cal_dark_master, master=True)
full_seq.add(cal_badpix, name='BADM', master=True)
full_seq.add(cal_loc, name='LOCM', files=[files.pp_dark_flat], master=True)
full_seq.add(cal_loc, name='LOCM', files=[files.pp_flat_dark], master=True)
full_seq.add(cal_shape_master, master=True)
full_seq.add(cal_shape, name='SHAPELM', master=True)
full_seq.add(cal_ff, name='FLATM', master=True)
full_seq.add(cal_leak_master, master=True)
full_seq.add(cal_wave_master, master=True,
             rkwargs=dict(hcfiles=[files.pp_hc1_hc1],
                          fpfiles=[files.pp_fp_fp]))
# night runs
full_seq.add(cal_badpix)
full_seq.add(cal_loc, files=[files.pp_dark_flat])
full_seq.add(cal_loc, files=[files.pp_flat_dark])
full_seq.add(cal_shape)
full_seq.add(cal_ff, files=[files.pp_flat_flat])
full_seq.add(cal_thermal)
full_seq.add(cal_wave_night)
# extract all OBJ_DARK and OBJ_FP
full_seq.add(cal_extract, name='EXTALL',
             files=[files.pp_obj_dark, files.pp_obj_fp])
# correct leakage
full_seq.add(cal_leak, name='LEAKALL', files=[files.out_ext_e2dsff],
             fiber='A', filters=dict(KW_DPRTYPE=['OBJ_FP']))
# telluric recipes
full_seq.add(obj_mk_tellu_db, arguments=dict(cores='CORES'))
full_seq.add(obj_fit_tellu_db, arguments=dict(cores='CORES'))
full_seq.add(obj_fit_tellu, name='FTELLU',
             files=[files.out_ext_e2dsff], fiber='A',
             filters=dict(KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP']))

# ccf on all OBJ_DARK / OBJ_FP
full_seq.add(cal_ccf, files=[files.out_tellu_obj], fiber='A',
             filters=dict(KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP']))

# -----------------------------------------------------------------------------
# limited sequence (master + nights)
# -----------------------------------------------------------------------------
limited_seq = drs_recipe.DrsRunSequence('limited_seq', __INSTRUMENT__)
# master run
limited_seq.add(cal_pp_master, master=True)
limited_seq.add(cal_pp)
limited_seq.add(cal_dark_master, master=True)
limited_seq.add(cal_badpix, name='BADM', master=True)
limited_seq.add(cal_loc, name='LOCM', files=[files.pp_dark_flat], master=True)
limited_seq.add(cal_loc, name='LOCM', files=[files.pp_flat_dark], master=True)
limited_seq.add(cal_shape_master, master=True)
limited_seq.add(cal_shape, name='SHAPELM', master=True)
limited_seq.add(cal_ff, name='FLATM', master=True)
limited_seq.add(cal_leak_master, master=True)
limited_seq.add(cal_wave_master, master=True,
                rkwargs=dict(hcfiles=[files.pp_hc1_hc1],
                             fpfiles=[files.pp_fp_fp]))
# night runs
limited_seq.add(cal_badpix)
limited_seq.add(cal_loc, files=[files.pp_dark_flat])
limited_seq.add(cal_loc, files=[files.pp_flat_dark])
limited_seq.add(cal_shape)
limited_seq.add(cal_ff, files=[files.pp_flat_flat])
limited_seq.add(cal_wave_night)
# extract tellurics
limited_seq.add(cal_extract, name='EXTTELL',
                files=[files.pp_obj_dark, files.pp_obj_fp],
                filters=dict(KW_OBJNAME='TELLURIC_TARGETS'))

# extract science
limited_seq.add(cal_extract, name='EXTOBJ',
                files=[files.pp_obj_dark, files.pp_obj_fp],
                filters=dict(KW_OBJNAME='SCIENCE_TARGETS'))

# correct leakage for any telluric targets that are OBJ_FP
limited_seq.add(cal_leak, name='LEAKTELL',
                files=[files.out_ext_e2dsff], fiber='A',
                filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
                             KW_DPRTYPE=['OBJ_FP']))

# correct leakage for any science targets that are OBJ_FP
limited_seq.add(cal_leak, name='LEAKOBJ',
                files=[files.out_ext_e2dsff], fiber='A',
                filters=dict(KW_OBJNAME='SCIENCE_TARGETS',
                             KW_DPRTYPE=['OBJ_FP']))

# # telluric recipes
# limited_seq.add(obj_mk_tellu_db, arguments=dict(cores='CORES'))
# limited_seq.add(obj_fit_tellu_db, arguments=dict(cores='CORES'))
#
# # other telluric recipes
# limited_seq.add(obj_mk_tellu, name='MKTELLU1',
#                 files=[files.out_ext_e2dsff], fiber='AB',
#                 filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
#                              KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP']))
# limited_seq.add(obj_fit_tellu, name='MKTELLU2',
#                 files=[files.out_ext_e2dsff], fiber='AB',
#                 filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
#                              KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP']))
# limited_seq.add(obj_mk_template, name='MKTELLU3',
#                 fiber='AB',
#                 arguments=dict(objname='TELLURIC_TARGETS'),
#                 filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
#                              KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP']))
# limited_seq.add(obj_mk_tellu, name='MKTELLU4',
#                 files=[files.out_ext_e2dsff], fiber='AB',
#                 filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
#                              KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP']))
# limited_seq.add(obj_fit_tellu, name='FTELLU1',
#                 files=[files.out_ext_e2dsff], fiber='AB',
#                 filters=dict(KW_OBJNAME='SCIENCE_TARGETS',
#                              KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP']))
# limited_seq.add(obj_mk_template, name='FTELLU2',
#                 fiber='AB',
#                 arguments=dict(objname='SCIENCE_TARGETS'),
#                 filters=dict(KW_OBJNAME='SCIENCE_TARGETS',
#                              KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP']))
# limited_seq.add(obj_fit_tellu, name='FTELLU3',
#                 files=[files.out_ext_e2dsff], fiber='AB',
#                 filters=dict(KW_OBJNAME='SCIENCE_TARGETS',
#                              KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP']))
#
# # ccf
# limited_seq.add(cal_ccf, files=[files.out_tellu_obj], fiber='AB',
#                 filters=dict(KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP'],
#                              KW_OBJNAME='SCIENCE_TARGETS'))

# -----------------------------------------------------------------------------
# pp sequence (for trigger)
# -----------------------------------------------------------------------------
pp_seq = drs_recipe.DrsRunSequence('pp_seq', __INSTRUMENT__)
pp_seq.add(cal_pp_master, master=True)
pp_seq.add(cal_pp)

pp_seq_opt = drs_recipe.DrsRunSequence('pp_seq_opt', __INSTRUMENT__)
pp_seq_opt.add(cal_pp_master, master=True)
pp_seq_opt.add(cal_pp, name='PP_CAL',
               filters=dict(KW_OBJNAME='Calibration'))
pp_seq_opt.add(cal_pp, name='PP_SCI',
               filters=dict(KW_OBJNAME='SCIENCE_TARGETS'))
pp_seq_opt.add(cal_pp, name='PP_TEL',
               filters=dict(KW_OBJNAME='TELLURIC_TARGETS'))
pp_seq_opt.add(cal_pp, name='PP_HC1HC1', files=[files.raw_hc1_hc1])
pp_seq_opt.add(cal_pp, name='PP_FPFP', files=[files.raw_fp_fp])
pp_seq_opt.add(cal_pp, name='PP_DFP', files=[files.raw_dark_fp])
pp_seq_opt.add(cal_pp, name='PP_SKY', files=[files.raw_dark_dark_sky])
pp_seq_opt.add(cal_pp, name='PP_LFC', files=[files.raw_lfc_lfc])

# -----------------------------------------------------------------------------
# master sequence (for trigger)
# -----------------------------------------------------------------------------
master_seq = drs_recipe.DrsRunSequence('master_seq', __INSTRUMENT__)
master_seq.add(cal_dark_master, master=True)
master_seq.add(cal_badpix, name='BADM', master=True)
master_seq.add(cal_loc, name='LOCM', files=[files.pp_dark_flat], master=True)
master_seq.add(cal_loc, name='LOCM', files=[files.pp_flat_dark], master=True)
master_seq.add(cal_shape_master, master=True)
master_seq.add(cal_shape, name='SHAPELM', master=True)
master_seq.add(cal_ff, name='FLATM', master=True)
master_seq.add(cal_leak_master, master=True)
master_seq.add(cal_wave_master, master=True,
               rkwargs=dict(hcfiles=[files.pp_hc1_hc1],
                            fpfiles=[files.pp_fp_fp]))

# -----------------------------------------------------------------------------
# calibration run (for trigger)
# -----------------------------------------------------------------------------
calib_seq = drs_recipe.DrsRunSequence('calib_seq', __INSTRUMENT__)
# night runs
calib_seq.add(cal_badpix)
calib_seq.add(cal_loc, files=[files.pp_dark_flat])
calib_seq.add(cal_loc, files=[files.pp_flat_dark])
calib_seq.add(cal_shape)
calib_seq.add(cal_ff, files=[files.pp_flat_flat])
calib_seq.add(cal_wave_night)

# -----------------------------------------------------------------------------
# telluric sequence (for trigger)
# -----------------------------------------------------------------------------
tellu_seq = drs_recipe.DrsRunSequence('tellu_seq', __INSTRUMENT__)
# extract science
tellu_seq.add(cal_extract, name='EXTOBJ',
              files=[files.pp_obj_dark, files.pp_obj_fp],
              filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
                           KW_DPRTYPE=['OBJ_FP', 'OBJ_DARK']))
# correct leakage for any telluric targets that are OBJ_FP
tellu_seq.add(cal_leak, name='LEAKTELL',
              files=[files.out_ext_e2dsff], fiber='A',
              filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
                           KW_DPRTYPE=['OBJ_FP']))
# other telluric recipes
tellu_seq.add(obj_mk_tellu, name='MKTELLU1',
              files=[files.out_ext_e2dsff], fiber='A',
              filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
                           KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP']))
tellu_seq.add(obj_fit_tellu, name='MKTELLU2',
              files=[files.out_ext_e2dsff], fiber='A',
              filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
                           KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP']))
tellu_seq.add(obj_mk_template, name='MKTELLU3',
              fiber='A', files=[files.out_ext_e2dsff],
              arguments=dict(objname='TELLURIC_TARGETS'),
              filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
                           KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP']))
tellu_seq.add(obj_mk_tellu, name='MKTELLU4',
              fiber='A', files=[files.out_ext_e2dsff],
              filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
                           KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP']))

# -----------------------------------------------------------------------------
# science sequence (for trigger)
# -----------------------------------------------------------------------------
science_seq = drs_recipe.DrsRunSequence('science_seq', __INSTRUMENT__)
# extract science
science_seq.add(cal_extract, name='EXTOBJ',
                files=[files.pp_obj_dark, files.pp_obj_fp],
                filters=dict(KW_OBJNAME='SCIENCE_TARGETS',
                             KW_DPRTYPE=['OBJ_FP', 'OBJ_DARK']))
# correct leakage for any science targets that are OBJ_FP
science_seq.add(cal_leak, name='LEAKOBJ',
                files=[files.out_ext_e2dsff], fiber='A',
                filters=dict(KW_DPRTYPE=['OBJ_FP'],
                             KW_OBJNAME='SCIENCE_TARGETS'))
science_seq.add(obj_fit_tellu, name='FTELLU1',
                files=[files.out_ext_e2dsff], fiber='A',
                filters=dict(KW_OBJNAME='SCIENCE_TARGETS',
                             KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP']))
science_seq.add(obj_mk_template, name='FTELLU2', fiber='A',
                arguments=dict(objname='SCIENCE_TARGETS'),
                filters=dict(KW_OBJNAME='SCIENCE_TARGETS',
                             KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP'], ))
science_seq.add(obj_fit_tellu, name='FTELLU3',
                files=[files.out_ext_e2dsff], fiber='A',
                filters=dict(KW_OBJNAME='SCIENCE_TARGETS',
                             KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP']))
# ccf
science_seq.add(cal_ccf, files=[files.out_tellu_obj], fiber='A',
                filters=dict(KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP'],
                             KW_OBJNAME='SCIENCE_TARGETS'))

# -----------------------------------------------------------------------------
# engineering sequences
# -----------------------------------------------------------------------------
eng_seq = drs_recipe.DrsRunSequence('eng_seq', __INSTRUMENT__)

# extract sequences
eng_seq.add(cal_extract, name='EXT_HC1HC1', files=[files.pp_hc1_hc1])
eng_seq.add(cal_extract, name='EXT_FPFP', files=[files.pp_fp_fp])
eng_seq.add(cal_extract, name='EXT_DFP', files=[files.pp_dark_fp])
eng_seq.add(cal_extract, name='EXT_SKY', files=[files.pp_dark_dark_sky])
eng_seq.add(cal_extract, name='EXT_LFC', files=[files.pp_lfc_lfc])

# -----------------------------------------------------------------------------
# sequences list
# -----------------------------------------------------------------------------
sequences = [pp_seq, pp_seq_opt, full_seq, limited_seq, master_seq, calib_seq,
             tellu_seq, science_seq, eng_seq]
