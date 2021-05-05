from apero.base import base
from apero.core.core import drs_base_classes as base_class
from apero.core import constants
from apero.core.utils import drs_recipe
from apero import lang
from apero.core.instruments.spirou import file_definitions as files
from apero.core.instruments.default import grouping

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'core.instruments.spirou.recipe_definitions.py'
__INSTRUMENT__ = 'SPIROU'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Define instrument alias
INSTRUMENT_ALIAS = 'spirou'
# Get constants
Constants = constants.load()
# Get Help
textentry = lang.textentry
# import file definitions in import module class
sf = base_class.ImportModule('spirou.file_definitions',
                             'apero.core.instruments.spirou.file_definitions',
                             mod=files)

# =============================================================================
# Commonly used arguments
# =============================================================================
obs_dir = dict(name='obs_dir', dtype='obs_dir',
               helpstr=textentry('OBS_DIR_HELP'))

# =============================================================================
# Option definitions
# =============================================================================
add_db = dict(name='--database', dtype='bool', default=True,
              helpstr=textentry('ADD_CAL_HELP'))
# -----------------------------------------------------------------------------
dobad = dict(name='--badcorr', dtype='bool', default=True,
             helpstr=textentry('DOBAD_HELP'))

# -----------------------------------------------------------------------------
backsub = dict(name='--backsub', dtype='bool', default=True,
               helpstr=textentry('BACKSUB_HELP'), default_ref='option_backsub')
# -----------------------------------------------------------------------------
# Must set default per recipe!!
combine = dict(name='--combine', dtype='bool',
               helpstr=textentry('COMBINE_HELP'),
               default_ref='INPUT_COMBINE_IMAGES')
# -----------------------------------------------------------------------------
dodark = dict(name='--darkcorr', dtype='bool', default=True,
              helpstr=textentry('DODARK_HELP'))
# -----------------------------------------------------------------------------
fiber = dict(name='--fiber', dtype='options', default='ALL',
             helpstr=textentry('EXTFIBER_HELP'),
             options=['ALL', 'AB', 'A', 'B', 'C'],
             default_ref='INPUT_FLIP_IMAGE')
# -----------------------------------------------------------------------------
flipimage = dict(name='--flipimage', dtype='options', default='both',
                 helpstr=textentry('FLIPIMAGE_HELP'),
                 options=['None', 'x', 'y', 'both'])
# -----------------------------------------------------------------------------
fluxunits = dict(name='--fluxunits', dtype='options', default='e-',
                 helpstr=textentry('FLUXUNITS_HELP'), options=['ADU/s', 'e-'])
# -----------------------------------------------------------------------------
plot = dict(name='--plot', dtype=int, helpstr=textentry('PLOT_HELP'),
            default_ref='DRS_PLOT', minimum=-1, maximum=2)
# -----------------------------------------------------------------------------
resize = dict(name='--resize', dtype='bool', default=True,
              helpstr=textentry('RESIZE_HELP'),
              default_ref='INPUT_RESIZE_IMAGE')
# -----------------------------------------------------------------------------
objname = dict(name='--objname', dtype=str, default='None',
               helpstr=textentry('OBJNAME_HELP'))
# -----------------------------------------------------------------------------
dprtype = dict(name='--dprtype', dtype=str, default='None',
               helpstr=textentry('DPRTYPE_HELP'))

# =============================================================================
# File option definitions
# =============================================================================
backfile = dict(name='--backfile', dtype='file', default='None',
                files=[files.out_backmap], helpstr=textentry('BACKFILE_HELP'))
# -----------------------------------------------------------------------------
badfile = dict(name='--badpixfile', dtype='file', default='None',
               files=[files.out_badpix], helpstr=textentry('BADFILE_HELP'))
# -----------------------------------------------------------------------------
blazefile = dict(name='--blazefile', dtype='file', default='None',
                 files=[files.out_ff_blaze],
                 helpstr=textentry('BLAZEFILE_HELP'))
# -----------------------------------------------------------------------------
darkfile = dict(name='--darkfile', dtype='file', default='None',
                files=[files.out_dark_master],
                helpstr=textentry('DARKFILE_HELP'))
# -----------------------------------------------------------------------------
flatfile = dict(name='--flatfile', dtype='file', default='None',
                files=[files.out_ff_flat], helpstr=textentry('FLATFILE_HELP'))
# -----------------------------------------------------------------------------
fpmaster = dict(name='--fpmaster', dtype='file', default='None',
                files=[files.out_shape_fpmaster],
                helpstr=textentry('FPMASTERFILE_HELP'))
# -----------------------------------------------------------------------------
locofile = dict(name='--locofile', dtype='file', default='None',
                files=[files.out_loc_loco], helpstr=textentry('LOCOFILE_HELP'))
# -----------------------------------------------------------------------------
orderpfile = dict(name='--orderpfile', dtype='file', default='None',
                  files=[files.out_loc_orderp],
                  helpstr=textentry('ORDERPFILE_HELP'))
# -----------------------------------------------------------------------------
shapexfile = dict(name='--shapex', dtype='file', default='None',
                  files=[files.out_shape_dxmap],
                  helpstr=textentry('SHAPEXFILE_HELP'))
# -----------------------------------------------------------------------------
shapeyfile = dict(name='--shapey', dtype='file', default='None',
                  files=[files.out_shape_dymap],
                  helpstr=textentry('SHAPEYFILE_HELP'))
# -----------------------------------------------------------------------------
shapelfile = dict(name='--shapel', dtype='file', default='None',
                  files=[files.out_shape_local],
                  helpstr=textentry('SHAPELFILE_HELP'))
# -----------------------------------------------------------------------------
thermalfile = dict(name='--thermalfile', dtype='file', default='None',
                   files=[files.out_thermal_e2ds_int,
                          files.out_thermal_e2ds_tel],
                   helpstr=textentry('THERMALFILE_HELP'))
# -----------------------------------------------------------------------------
wavefile = dict(name='--wavefile', dtype='file', default='None',
                files=[files.out_wave_hc, files.out_wave_fp,
                       files.out_wave_master],
                helpstr=textentry('WAVEFILE_HELP'))

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
#    recipe.in_block_str        the input directory [raw/tmp/reduced]
#    recipe.out_block_str       the output directory [raw/tmp/reduced]
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

# -----------------------------------------------------------------------------
# apero_preprocess
# -----------------------------------------------------------------------------
apero_preprocess = DrsRecipe(__INSTRUMENT__)
apero_preprocess.name = 'apero_preprocess_{0}.py'.format(INSTRUMENT_ALIAS)
apero_preprocess.shortname = 'PP'
apero_preprocess.instrument = __INSTRUMENT__
apero_preprocess.in_block_str = 'raw'
apero_preprocess.out_block_str = 'tmp'
apero_preprocess.extension = 'fits'
apero_preprocess.description = textentry('PREPROCESS_DESC')
apero_preprocess.epilog = textentry('PREPROCESS_EXAMPLE')
apero_preprocess.recipe_type = 'recipe'
apero_preprocess.recipe_kind = 'pre'
apero_preprocess.set_outputs(PP_FILE=files.pp_file)
apero_preprocess.set_arg(pos=0, **obs_dir)
apero_preprocess.set_arg(name='files', dtype='files', pos='1+',
                         files=[files.raw_file],
                         helpstr=textentry('PREPROCESS_UFILES_HELP'), limit=1)
apero_preprocess.set_kwarg(name='--skip', dtype='bool', default=False,
                           helpstr=textentry('PPSKIP_HELP'), default_ref='SKIP_DONE_PP')
apero_preprocess.group_func = grouping.group_individually
apero_preprocess.group_column = 'REPROCESS_OBSDIR_COL'
# add to recipe
recipes.append(apero_preprocess)

# -----------------------------------------------------------------------------
# apero_badpix
# -----------------------------------------------------------------------------
apero_badpix = DrsRecipe(__INSTRUMENT__)
apero_badpix.name = 'apero_badpix_{0}.py'.format(INSTRUMENT_ALIAS)
apero_badpix.shortname = 'BAD'
apero_badpix.instrument = __INSTRUMENT__
apero_badpix.in_block_str = 'tmp'
apero_badpix.out_block_str = 'red'
apero_badpix.extension = 'fits'
apero_badpix.description = textentry('BADPIX_DESC')
apero_badpix.epilog = textentry('BADPIX_EXAMPLE')
apero_badpix.recipe_type = 'recipe'
apero_badpix.recipe_kind = 'calib-night'
apero_badpix.set_outputs(BADPIX=files.out_badpix, BACKMAP=files.out_backmap)
apero_badpix.set_debug_plots('BADPIX_MAP')
apero_badpix.set_summary_plots('SUM_BADPIX_MAP')
apero_badpix.set_arg(pos=0, **obs_dir)
apero_badpix.set_kwarg(name='--flatfiles', dtype='files',
                       files=[files.pp_flat_flat],
                       filelogic='exclusive', required=True,
                       helpstr=textentry('BADPIX_FLATFILE_HELP'), default=[])
apero_badpix.set_kwarg(name='--darkfiles', dtype='files',
                       files=[files.pp_dark_dark_tel, files.pp_dark_dark_int],
                       filelogic='inclusive', required=True,
                       helpstr=textentry('BADPIX_DARKFILE_HELP'), default=[])
apero_badpix.set_kwarg(**add_db)
apero_badpix.set_kwarg(default=True, **combine)
apero_badpix.set_kwarg(**flipimage)
apero_badpix.set_kwarg(**fluxunits)
apero_badpix.set_kwarg(**plot)
apero_badpix.set_kwarg(**resize)
apero_badpix.group_func = grouping.group_by_dirname
apero_badpix.group_column = 'REPROCESS_OBSDIR_COL'
# add to recipe
recipes.append(apero_badpix)

# -----------------------------------------------------------------------------
# apero_dark
# -----------------------------------------------------------------------------
apero_dark = DrsRecipe(__INSTRUMENT__)
apero_dark.name = 'apero_dark_{0}.py'.format(INSTRUMENT_ALIAS)
apero_dark.shortname = 'DARK'
apero_dark.instrument = __INSTRUMENT__
apero_dark.in_block_str = 'tmp'
apero_dark.out_block_str = 'red'
apero_dark.extension = 'fits'
apero_dark.description = textentry('DARK_DESC')
apero_dark.epilog = textentry('DARK_EXAMPLE')
apero_dark.recipe_type = 'recipe'
apero_dark.recipe_kind = 'calib-night'
apero_dark.set_outputs(DARK_INT_FILE=files.out_dark_int,
                       DARK_TEL_FIEL=files.out_dark_tel,
                       DARK_SKY_FILE=files.out_dark_sky)
apero_dark.set_debug_plots('DARK_IMAGE_REGIONS', 'DARK_HISTOGRAM')
apero_dark.set_summary_plots('SUM_DARK_IMAGE_REGIONS', 'SUM_DARK_HISTOGRAM')
apero_dark.set_arg(pos=0, **obs_dir)
apero_dark.set_arg(name='files', dtype='files',
                   files=[files.pp_dark_dark_int, files.pp_dark_dark_tel,
                          files.pp_dark_dark_sky],
                   pos='1+', filelogic='exclusive',
                   helpstr=textentry('FILES_HELP') + textentry('DARK_FILES_HELP'))
apero_dark.set_kwarg(**add_db)
apero_dark.set_kwarg(default=True, **combine)
apero_dark.set_kwarg(**plot)
apero_dark.group_func = grouping.group_by_dirname
apero_dark.group_column = 'REPROCESS_OBSDIR_COL'
# add to recipe
recipes.append(apero_dark)

# -----------------------------------------------------------------------------
# apero_dark_master
# -----------------------------------------------------------------------------
apero_dark_master = DrsRecipe(__INSTRUMENT__)
apero_dark_master.name = 'apero_dark_master_{0}.py'.format(INSTRUMENT_ALIAS)
apero_dark_master.shortname = 'DARKM'
apero_dark_master.master = True
apero_dark_master.instrument = __INSTRUMENT__
apero_dark_master.in_block_str = 'tmp'
apero_dark_master.out_block_str = 'red'
apero_dark_master.extension = 'fits'
apero_dark_master.description = textentry('DARK_MASTER_DESC')
apero_dark_master.epilog = textentry('DARK_MASTER_EXAMPLE')
apero_dark_master.recipe_type = 'recipe'
apero_dark_master.recipe_kind = 'calib-master'
apero_dark_master.set_outputs(DARK_MASTER_FILE=files.out_dark_master)
apero_dark_master.set_kwarg(name='--filetype', dtype=str,
                            default='DARK_DARK_TEL, DARK_DARK_INT',
                            helpstr=textentry('DARK_MASTER_FILETYPE'))
apero_dark_master.set_kwarg(**add_db)
apero_dark_master.set_kwarg(**plot)
apero_dark_master.group_func = grouping.no_group
apero_dark_master.group_column = None
# add to recipe
recipes.append(apero_dark_master)

# -----------------------------------------------------------------------------
# apero_loc
# -----------------------------------------------------------------------------
apero_loc = DrsRecipe(__INSTRUMENT__)
apero_loc.name = 'apero_loc_{0}.py'.format(INSTRUMENT_ALIAS)
apero_loc.shortname = 'LOC'
apero_loc.instrument = __INSTRUMENT__
apero_loc.in_block_str = 'tmp'
apero_loc.out_block_str = 'red'
apero_loc.extension = 'fits'
apero_loc.description = textentry('LOC_DESC')
apero_loc.epilog = textentry('LOC_EXAMPLE')
apero_loc.recipe_type = 'recipe'
apero_loc.recipe_kind = 'calib-night'
apero_loc.set_outputs(ORDERP_FILE=files.out_loc_orderp,
                      LOCO_FILE=files.out_loc_loco,
                      FWHM_FILE=files.out_loc_fwhm,
                      SUP_FILE=files.out_loc_sup,
                      DEBUG_BACK=files.debug_back)
apero_loc.set_debug_plots('LOC_MINMAX_CENTS', 'LOC_MIN_CENTS_THRES',
                          'LOC_FINDING_ORDERS', 'LOC_IM_SAT_THRES',
                          'LOC_ORD_VS_RMS', 'LOC_CHECK_COEFFS',
                          'LOC_FIT_RESIDUALS')
apero_loc.set_summary_plots('SUM_LOC_IM_THRES', 'SUM_LOC_IM_CORNER')
apero_loc.set_arg(pos=0, **obs_dir)
apero_loc.set_arg(name='files', dtype='files', filelogic='exclusive',
                  files=[files.pp_dark_flat, files.pp_flat_dark], pos='1+',
                  helpstr=textentry('FILES_HELP') + textentry('LOC_FILES_HELP'))
apero_loc.set_kwarg(**add_db)
apero_loc.set_kwarg(**badfile)
apero_loc.set_kwarg(**dobad)
apero_loc.set_kwarg(**backsub)
apero_loc.set_kwarg(default=True, **combine)
apero_loc.set_kwarg(**darkfile)
apero_loc.set_kwarg(**dodark)
apero_loc.set_kwarg(**flipimage)
apero_loc.set_kwarg(**fluxunits)
apero_loc.set_kwarg(**plot)
apero_loc.set_kwarg(**resize)
apero_loc.group_func = grouping.group_by_dirname
apero_loc.group_column = 'REPROCESS_OBSDIR_COL'
# add to recipe
recipes.append(apero_loc)

# -----------------------------------------------------------------------------
# apero_shape_master
# -----------------------------------------------------------------------------
apero_shape_master = DrsRecipe(__INSTRUMENT__)
apero_shape_master.name = 'apero_shape_master_{0}.py'.format(INSTRUMENT_ALIAS)
apero_shape_master.shortname = 'SHAPEM'
apero_shape_master.master = True
apero_shape_master.instrument = __INSTRUMENT__
apero_shape_master.in_block_str = 'tmp'
apero_shape_master.out_block_str = 'red'
apero_shape_master.extension = 'fits'
apero_shape_master.description = textentry('SHAPE_DESC')
apero_shape_master.epilog = textentry('SHAPEMASTER_EXAMPLE')
apero_shape_master.recipe_type = 'recipe'
apero_shape_master.recipe_kind = 'calib-master'
apero_shape_master.set_outputs(FPMASTER_FILE=files.out_shape_fpmaster,
                               DXMAP_FILE=files.out_shape_dxmap,
                               DYMAP_FILE=files.out_shape_dymap,
                               SHAPE_IN_FP_FILE=files.out_shape_debug_ifp,
                               SHAPE_IN_HC_FILE=files.out_shape_debug_ihc,
                               SHAPE_OUT_FP_FILE=files.out_shape_debug_ofp,
                               SHAPE_OUT_HC_FILE=files.out_shape_debug_ohc,
                               SHAPE_BDXMAP_FILE=files.out_shape_debug_bdx,
                               DEBUG_BACK=files.debug_back)
apero_shape_master.set_debug_plots('SHAPE_DX', 'SHAPE_ANGLE_OFFSET_ALL',
                                   'SHAPE_ANGLE_OFFSET', 'SHAPE_LINEAR_TPARAMS')
apero_shape_master.set_summary_plots('SUM_SHAPE_ANGLE_OFFSET')
apero_shape_master.set_arg(pos=0, **obs_dir)
apero_shape_master.set_kwarg(name='--fpfiles', dtype='files',
                             files=[files.pp_fp_fp],
                             filelogic='exclusive', required=True,
                             helpstr=textentry('SHAPE_FPFILES_HELP'), default=[])
apero_shape_master.set_kwarg(name='--hcfiles', dtype='files',
                             files=[files.pp_hc1_hc1],
                             filelogic='exclusive', required=True,
                             helpstr=textentry('SHAPE_HCFILES_HELP'), default=[])
apero_shape_master.set_kwarg(**add_db)
apero_shape_master.set_kwarg(**badfile)
apero_shape_master.set_kwarg(**dobad)
apero_shape_master.set_kwarg(**backsub)
apero_shape_master.set_kwarg(default=True, **combine)
apero_shape_master.set_kwarg(**darkfile)
apero_shape_master.set_kwarg(**dodark)
apero_shape_master.set_kwarg(**flipimage)
apero_shape_master.set_kwarg(**fluxunits)
apero_shape_master.set_kwarg(**locofile)
apero_shape_master.set_kwarg(**plot)
apero_shape_master.set_kwarg(**resize)
apero_shape_master.set_kwarg(name='--fpmaster', dtype='files',
                             files=[files.out_shape_fpmaster], default='None',
                             helpstr=textentry('SHAPE_FPMASTER_HELP'))
apero_shape_master.group_func = grouping.group_by_dirname
apero_shape_master.group_column = 'REPROCESS_OBSDIR_COL'
# add to recipe
recipes.append(apero_shape_master)

# -----------------------------------------------------------------------------
# apero_shape
# -----------------------------------------------------------------------------
apero_shape = DrsRecipe(__INSTRUMENT__)
apero_shape.name = 'apero_shape_{0}.py'.format(INSTRUMENT_ALIAS)
apero_shape.shortname = 'SHAPE'
apero_shape.instrument = __INSTRUMENT__
apero_shape.in_block_str = 'tmp'
apero_shape.out_block_str = 'red'
apero_shape.extension = 'fits'
apero_shape.description = textentry('SHAPE_DESC')
apero_shape.epilog = textentry('SHAPE_EXAMPLE')
apero_shape.recipe_type = 'recipe'
apero_shape.recipe_kind = 'calib-night'
apero_shape.set_outputs(LOCAL_SHAPE_FILE=files.out_shape_local,
                        SHAPEL_IN_FP_FILE=files.out_shapel_debug_ifp,
                        SHAPEL_OUT_FP_FILE=files.out_shapel_debug_ofp,
                        DEBUG_BACK=files.debug_back)
apero_shape.set_debug_plots('SHAPEL_ZOOM_SHIFT', 'SHAPE_LINEAR_TPARAMS')
apero_shape.set_summary_plots('SUM_SHAPEL_ZOOM_SHIFT')
apero_shape.set_arg(pos=0, **obs_dir)
apero_shape.set_arg(name='files', dtype='files', files=[files.pp_fp_fp],
                    pos='1+', helpstr=textentry('SHAPE_FPFILES_HELP'))
apero_shape.set_kwarg(**add_db)
apero_shape.set_kwarg(**badfile)
apero_shape.set_kwarg(**dobad)
apero_shape.set_kwarg(**backsub)
apero_shape.set_kwarg(default=True, **combine)
apero_shape.set_kwarg(**darkfile)
apero_shape.set_kwarg(**dodark)
apero_shape.set_kwarg(**flipimage)
apero_shape.set_kwarg(**fluxunits)
apero_shape.set_kwarg(**fpmaster)
apero_shape.set_kwarg(**plot)
apero_shape.set_kwarg(**resize)
apero_shape.set_kwarg(**shapexfile)
apero_shape.set_kwarg(**shapeyfile)
apero_shape.group_func = grouping.group_by_dirname
apero_shape.group_column = 'REPROCESS_OBSDIR_COL'
# add to recipe
recipes.append(apero_shape)

# -----------------------------------------------------------------------------
# apero_flat
# -----------------------------------------------------------------------------
apero_flat = DrsRecipe(__INSTRUMENT__)
apero_flat.name = 'apero_flat_{0}.py'.format(INSTRUMENT_ALIAS)
apero_flat.shortname = 'FF'
apero_flat.instrument = __INSTRUMENT__
apero_flat.in_block_str = 'tmp'
apero_flat.out_block_str = 'red'
apero_flat.extension = 'fits'
apero_flat.description = textentry('FLAT_DESC')
apero_flat.epilog = textentry('FLAT_EXAMPLE')
apero_flat.recipe_type = 'recipe'
apero_flat.recipe_kind = 'calib-night'
apero_flat.set_outputs(FLAT_FILE=files.out_ff_flat,
                       BLAZE_FILE=files.out_ff_blaze,
                       E2DSLL_FILE=files.out_ext_e2dsll,
                       ORDERP_SFILE=files.out_orderp_straight,
                       DEBUG_BACK=files.debug_back)
apero_flat.set_debug_plots('FLAT_ORDER_FIT_EDGES1', 'FLAT_ORDER_FIT_EDGES2',
                           'FLAT_BLAZE_ORDER1', 'FLAT_BLAZE_ORDER2')
apero_flat.set_summary_plots('SUM_FLAT_ORDER_FIT_EDGES', 'SUM_FLAT_BLAZE_ORDER')
apero_flat.set_arg(pos=0, **obs_dir)
apero_flat.set_arg(name='files', dtype='files', filelogic='exclusive',
                   files=[files.pp_flat_flat], pos='1+',
                   helpstr=textentry('FILES_HELP') + textentry('FLAT_FILES_HELP'))
apero_flat.set_kwarg(**add_db)
apero_flat.set_kwarg(**badfile)
apero_flat.set_kwarg(**dobad)
apero_flat.set_kwarg(**backsub)
apero_flat.set_kwarg(default=True, **combine)
apero_flat.set_kwarg(**darkfile)
apero_flat.set_kwarg(**dodark)
apero_flat.set_kwarg(**fiber)
apero_flat.set_kwarg(**flipimage)
apero_flat.set_kwarg(**fluxunits)
apero_flat.set_kwarg(**locofile)
apero_flat.set_kwarg(**orderpfile)
apero_flat.set_kwarg(**plot)
apero_flat.set_kwarg(**resize)
apero_flat.set_kwarg(**shapexfile)
apero_flat.set_kwarg(**shapeyfile)
apero_flat.set_kwarg(**shapelfile)
apero_flat.group_func = grouping.group_by_dirname
apero_flat.group_column = 'REPROCESS_OBSDIR_COL'
# add to recipe
recipes.append(apero_flat)

# -----------------------------------------------------------------------------
# apero_thermal
# -----------------------------------------------------------------------------
apero_thermal = DrsRecipe(__INSTRUMENT__)
apero_thermal.name = 'apero_thermal_{0}.py'.format(INSTRUMENT_ALIAS)
apero_thermal.shortname = 'THERM'
apero_thermal.instrument = __INSTRUMENT__
apero_thermal.in_block_str = 'tmp'
apero_thermal.out_block_str = 'red'
apero_thermal.extension = 'fits'
apero_thermal.description = textentry('EXTRACT_DESC')
apero_thermal.epilog = textentry('EXTRACT_EXAMPLE')
apero_thermal.recipe_type = 'recipe'
apero_thermal.recipe_kind = 'calib-night'
# TODO: Need to add out_thermal_e2ds_sky
apero_thermal.set_outputs(THERMAL_E2DS_FILE=files.out_ext_e2dsff,
                          THERMALI_FILE=files.out_thermal_e2ds_int,
                          THERMALT_FILE=files.out_thermal_e2ds_tel)
apero_thermal.set_arg(pos=0, **obs_dir)
# TODO: Need to add files.pp_dark_dark_sky
apero_thermal.set_arg(name='files', dtype='files', pos='1+',
                      files=[files.pp_dark_dark_int, files.pp_dark_dark_tel],
                      filelogic='exclusive',
                      helpstr=(textentry('FILES_HELP') +
                               textentry('EXTRACT_FILES_HELP')),
                      limit=1)
apero_thermal.set_kwarg(**add_db)
apero_thermal.set_kwarg(**badfile)
apero_thermal.set_kwarg(**dobad)
apero_thermal.set_kwarg(**backsub)
apero_thermal.set_kwarg(default=True, **combine)
apero_thermal.set_kwarg(**darkfile)
apero_thermal.set_kwarg(**dodark)
apero_thermal.set_kwarg(**fiber)
apero_thermal.set_kwarg(**flipimage)
apero_thermal.set_kwarg(**fluxunits)
apero_thermal.set_kwarg(**locofile)
apero_thermal.set_kwarg(**orderpfile)
apero_thermal.set_kwarg(**plot)
apero_thermal.set_kwarg(**resize)
apero_thermal.set_kwarg(**shapexfile)
apero_thermal.set_kwarg(**shapeyfile)
apero_thermal.set_kwarg(**shapelfile)
apero_thermal.set_kwarg(**wavefile)
apero_thermal.set_kwarg(name='--forceext', dtype='bool', default=False,
                        default_ref='THERMAL_ALWAYS_EXTRACT',
                        helpstr='THERMAL_EXTRACT_HELP')
apero_thermal.group_func = grouping.group_by_dirname
apero_thermal.group_column = 'REPROCESS_OBSDIR_COL'
# add to recipe
recipes.append(apero_thermal)

# -----------------------------------------------------------------------------
# apero_leak_master
# -----------------------------------------------------------------------------
apero_leak_master = DrsRecipe(__INSTRUMENT__)
apero_leak_master.name = 'apero_leak_master_{0}.py'.format(INSTRUMENT_ALIAS)
apero_leak_master.shortname = 'LEAKM'
apero_leak_master.master = True
apero_leak_master.instrument = __INSTRUMENT__
apero_leak_master.in_block_str = 'tmp'
apero_leak_master.out_block_str = 'red'
apero_leak_master.extension = 'fits'
apero_leak_master.description = textentry('LEAKM_DESC')
apero_leak_master.epilog = textentry('LEAKM_EXAMPLE')
apero_leak_master.recipe_type = 'recipe'
apero_leak_master.recipe_kind = 'calib-master'
apero_leak_master.set_outputs(LEAK_E2DS_FILE=files.out_ext_e2dsff,
                              LEAK_MASTER=files.out_leak_master)
apero_leak_master.set_arg(pos=0, **obs_dir)
apero_leak_master.set_kwarg(name='--filetype', dtype=str, default='DARK_FP',
                            helpstr=textentry('LEAKM_HELP_FILETYPE'))
apero_leak_master.set_kwarg(**add_db)
apero_leak_master.set_kwarg(**plot)
apero_leak_master.group_func = grouping.no_group
apero_leak_master.group_column = None
# add to recipe
recipes.append(apero_leak_master)

# -----------------------------------------------------------------------------
# apero_leak
# -----------------------------------------------------------------------------
apero_leak = DrsRecipe(__INSTRUMENT__)
apero_leak.name = 'apero_leak_{0}.py'.format(INSTRUMENT_ALIAS)
apero_leak.shortname = 'LEAK'
apero_leak.instrument = __INSTRUMENT__
apero_leak.in_block_str = 'red'
apero_leak.out_block_str = 'red'
apero_leak.extension = 'fits'
apero_leak.description = textentry('LEAK_DESC')
apero_leak.epilog = textentry('LEAK_EXAMPLE')
apero_leak.recipe_type = 'recipe'
apero_leak.recipe_kind = 'leak'
apero_leak.set_outputs(E2DS_FILE=files.out_ext_e2ds,
                       E2DSFF_FILE=files.out_ext_e2dsff,
                       E2DSLL_FILE=files.out_ext_e2dsll,
                       S1D_W_FILE=files.out_ext_s1d_w,
                       S1D_V_FILE=files.out_ext_s1d_v)
apero_leak.set_arg(pos=0, **obs_dir)
apero_leak.set_arg(name='files', dtype='files', pos='1+',
                   files=[files.out_ext_e2dsff],
                   helpstr=textentry('FILES_HELP') + textentry('LEAK_FILES_HELP'),
                   limit=1)
apero_leak.set_kwarg(**add_db)
apero_leak.set_kwarg(**plot)
apero_leak.set_kwarg(name='--leakfile', dtype='file', default='None',
                     files=[files.out_leak_master],
                     helpstr=textentry('LEAK_LEAKFILE_HELP'))
apero_leak.group_func = grouping.group_individually
apero_leak.group_column = 'REPROCESS_OBSDIR_COL'
# add to recipe
recipes.append(apero_leak)

# -----------------------------------------------------------------------------
# apero_extract
# -----------------------------------------------------------------------------
apero_extract = DrsRecipe(__INSTRUMENT__)
apero_extract.name = 'apero_extract_{0}.py'.format(INSTRUMENT_ALIAS)
apero_extract.shortname = 'EXT'
apero_extract.instrument = __INSTRUMENT__
apero_extract.in_block_str = 'tmp'
apero_extract.out_block_str = 'red'
apero_extract.extension = 'fits'
apero_extract.description = textentry('EXTRACT_DESC')
apero_extract.epilog = textentry('EXTRACT_EXAMPLE')
apero_extract.recipe_type = 'recipe'
apero_extract.recipe_kind = 'extract'
apero_extract.set_outputs(E2DS_FILE=files.out_ext_e2ds,
                          E2DSFF_FILE=files.out_ext_e2dsff,
                          E2DSLL_FILE=files.out_ext_e2dsll,
                          S1D_W_FILE=files.out_ext_s1d_w,
                          S1D_V_FILE=files.out_ext_s1d_v,
                          ORDERP_SFILE=files.out_orderp_straight,
                          DEBUG_BACK=files.debug_back,
                          EXT_FPLINES=files.out_ext_fplines,
                          Q2DS_FILE=files.out_ql_e2ds,
                          Q2DSFF_FILE=files.out_ql_e2dsff)
apero_extract.set_debug_plots('FLAT_ORDER_FIT_EDGES1', 'FLAT_ORDER_FIT_EDGES2',
                              'FLAT_BLAZE_ORDER1', 'FLAT_BLAZE_ORDER2',
                              'THERMAL_BACKGROUND', 'EXTRACT_SPECTRAL_ORDER1',
                              'EXTRACT_SPECTRAL_ORDER2', 'EXTRACT_S1D',
                              'EXTRACT_S1D_WEIGHT')
apero_extract.set_summary_plots('SUM_FLAT_ORDER_FIT_EDGES',
                                'SUM_EXTRACT_SP_ORDER', 'SUM_EXTRACT_S1D')
apero_extract.set_arg(pos=0, **obs_dir)
apero_extract.set_arg(name='files', dtype='files', pos='1+',
                      files=[files.pp_file],
                      helpstr=(textentry('FILES_HELP') +
                               textentry('EXTRACT_FILES_HELP')),
                      limit=1)
apero_extract.set_kwarg(name='--quicklook', dtype='bool', default=False,
                        helpstr=textentry('QUICK_LOOK_EXT_HELP'),
                        default_ref='EXT_QUICK_LOOK')
apero_extract.set_kwarg(**badfile)
apero_extract.set_kwarg(**dobad)
apero_extract.set_kwarg(**backsub)
apero_extract.set_kwarg(**blazefile)
apero_extract.set_kwarg(default=False, **combine)
apero_extract.set_kwarg(**objname)
apero_extract.set_kwarg(**dprtype)
apero_extract.set_kwarg(**darkfile)
apero_extract.set_kwarg(**dodark)
apero_extract.set_kwarg(**fiber)
apero_extract.set_kwarg(**flipimage)
apero_extract.set_kwarg(**fluxunits)
apero_extract.set_kwarg(**flatfile)
apero_extract.set_kwarg(**locofile)
apero_extract.set_kwarg(**orderpfile)
apero_extract.set_kwarg(**plot)
apero_extract.set_kwarg(**resize)
apero_extract.set_kwarg(**shapexfile)
apero_extract.set_kwarg(**shapeyfile)
apero_extract.set_kwarg(**shapelfile)
apero_extract.set_kwarg(name='--thermal', dtype='bool', default=True,
                        helpstr=textentry('THERMAL_HELP'),
                        default_ref='THERMAL_CORRECT')
apero_extract.set_kwarg(**thermalfile)
apero_extract.set_kwarg(**wavefile)
apero_extract.group_func = grouping.group_individually
apero_extract.group_column = 'REPROCESS_OBSDIR_COL'
# add to recipe
recipes.append(apero_extract)

# -----------------------------------------------------------------------------
# apero_wave_master
# -----------------------------------------------------------------------------
apero_wave_master = DrsRecipe(__INSTRUMENT__)
apero_wave_master.name = 'apero_wave_master_{0}.py'.format(INSTRUMENT_ALIAS)
apero_wave_master.shortname = 'WAVEM'
apero_wave_master.instrument = __INSTRUMENT__
apero_wave_master.in_block_str = 'tmp'
apero_wave_master.out_block_str = 'red'
apero_wave_master.extension = 'fits'
apero_wave_master.description = textentry('WAVE_DESC')
apero_wave_master.epilog = textentry('WAVE_EXAMPLE')
apero_wave_master.recipe_type = 'recipe'
apero_wave_master.recipe_kind = 'calib-master'
apero_wave_master.set_outputs(WAVE_E2DS=files.out_ext_e2dsff,
                              WAVESOL_MASTER=files.out_wavem_fp,
                              WAVEM_CAVITY=files.out_wavem_cavity,
                              WAVEM_HCLIST=files.out_wave_hclist_master,
                              WAVEM_FPLIST=files.out_wave_fplist_master,
                              WAVEM_RES=files.out_wavem_res,
                              CCF_RV=files.out_ccf_fits)
apero_wave_master.set_debug_plots('WAVE_WL_CAV', 'WAVE_FIBER_COMPARISON',
                                  'WAVE_FIBER_COMP', 'WAVE_HC_DIFF_HIST',
                                  'WAVEREF_EXPECTED', 'EXTRACT_S1D',
                                  'EXTRACT_S1D_WEIGHT', 'WAVE_RESMAP',
                                  'CCF_RV_FIT', 'CCF_RV_FIT_LOOP')
apero_wave_master.set_summary_plots('SUM_WAVE_FIBER_COMP', 'SUM_CCF_RV_FIT')
apero_wave_master.set_arg(pos=0, **obs_dir)
apero_wave_master.set_kwarg(name='--hcfiles', dtype='files',
                            files=[files.pp_hc1_hc1],
                            filelogic='exclusive', required=True,
                            helpstr=textentry('WAVE_HCFILES_HELP'), default=[])
apero_wave_master.set_kwarg(name='--fpfiles', dtype='files',
                            files=[files.pp_fp_fp],
                            filelogic='exclusive', required=True,
                            helpstr=textentry('WAVE_FPFILES_HELP'), default=[])
apero_wave_master.set_kwarg(**add_db)
apero_wave_master.set_kwarg(**badfile)
apero_wave_master.set_kwarg(**dobad)
apero_wave_master.set_kwarg(**backsub)
apero_wave_master.set_kwarg(**blazefile)
apero_wave_master.set_kwarg(default=True, **combine)
apero_wave_master.set_kwarg(**darkfile)
apero_wave_master.set_kwarg(**dodark)
apero_wave_master.set_kwarg(**fiber)
apero_wave_master.set_kwarg(**flipimage)
apero_wave_master.set_kwarg(**fluxunits)
apero_wave_master.set_kwarg(**locofile)
apero_wave_master.set_kwarg(**orderpfile)
apero_wave_master.set_kwarg(**plot)
apero_wave_master.set_kwarg(**resize)
apero_wave_master.set_kwarg(**shapexfile)
apero_wave_master.set_kwarg(**shapeyfile)
apero_wave_master.set_kwarg(**shapelfile)
apero_wave_master.set_kwarg(**wavefile)
apero_wave_master.set_kwarg(name='--forceext', dtype='bool',
                            default_ref='WAVE_ALWAYS_EXTRACT',
                            helpstr='WAVE_EXTRACT_HELP')
apero_wave_master.set_kwarg(name='--cavityfile', dtype='file', default='None',
                            files=[files.out_wavem_cavity],
                            helpstr=textentry('WAVEM_CAVFILE_HELP'))
apero_wave_master.group_func = grouping.group_by_dirname
apero_wave_master.group_column = 'REPROCESS_OBSDIR_COL'
# add to recipe
recipes.append(apero_wave_master)

# -----------------------------------------------------------------------------
# cal wave night
# -----------------------------------------------------------------------------
apero_wave_night = DrsRecipe(__INSTRUMENT__)
apero_wave_night.name = 'apero_wave_night_{0}.py'.format(INSTRUMENT_ALIAS)
apero_wave_night.shortname = 'WAVE'
apero_wave_night.instrument = __INSTRUMENT__
apero_wave_night.in_block_str = 'tmp'
apero_wave_night.out_block_str = 'red'
apero_wave_night.extension = 'fits'
apero_wave_night.description = textentry('WAVE_DESC')
apero_wave_night.epilog = textentry('WAVE_EXAMPLE')
apero_wave_night.recipe_type = 'recipe'
apero_wave_night.recipe_kind = 'calib-night'
apero_wave_night.set_outputs(WAVE_E2DS=files.out_ext_e2dsff,
                             WAVEMAP_NIGHT=files.out_wave_night,
                             WAVE_HCLIST=files.out_wave_hclist,
                             WAVE_FPLIST=files.out_wave_fplist,
                             CCF_RV=files.out_ccf_fits)
apero_wave_night.set_debug_plots('WAVE_WL_CAV', 'WAVE_FIBER_COMPARISON',
                                 'WAVE_FIBER_COMP', 'WAVE_HC_DIFF_HIST',
                                 'WAVEREF_EXPECTED', 'EXTRACT_S1D',
                                 'EXTRACT_S1D_WEIGHT', 'WAVE_RESMAP',
                                 'CCF_RV_FIT', 'CCF_RV_FIT_LOOP')
apero_wave_night.set_summary_plots('SUM_WAVE_FIBER_COMP', 'SUM_CCF_RV_FIT')
apero_wave_night.set_arg(pos=0, **obs_dir)
apero_wave_night.set_kwarg(name='--hcfiles', dtype='files',
                           files=[files.pp_hc1_hc1],
                           filelogic='exclusive', required=True,
                           helpstr=textentry('WAVE_HCFILES_HELP'), default=[])
apero_wave_night.set_kwarg(name='--fpfiles', dtype='files',
                           files=[files.pp_fp_fp],
                           filelogic='exclusive', required=True,
                           helpstr=textentry('WAVE_FPFILES_HELP'), default=[])
apero_wave_night.set_kwarg(**add_db)
apero_wave_night.set_kwarg(**badfile)
apero_wave_night.set_kwarg(**dobad)
apero_wave_night.set_kwarg(**backsub)
apero_wave_night.set_kwarg(**blazefile)
apero_wave_night.set_kwarg(default=True, **combine)
apero_wave_night.set_kwarg(**darkfile)
apero_wave_night.set_kwarg(**dodark)
apero_wave_night.set_kwarg(**fiber)
apero_wave_night.set_kwarg(**flipimage)
apero_wave_night.set_kwarg(**fluxunits)
apero_wave_night.set_kwarg(**locofile)
apero_wave_night.set_kwarg(**orderpfile)
apero_wave_night.set_kwarg(**plot)
apero_wave_night.set_kwarg(**resize)
apero_wave_night.set_kwarg(**shapexfile)
apero_wave_night.set_kwarg(**shapeyfile)
apero_wave_night.set_kwarg(**shapelfile)
apero_wave_night.set_kwarg(**wavefile)
apero_wave_night.set_kwarg(name='--forceext', dtype='bool',
                           default_ref='WAVE_ALWAYS_EXTRACT',
                           helpstr='WAVE_EXTRACT_HELP')
apero_wave_night.group_func = grouping.group_by_dirname
apero_wave_night.group_column = 'REPROCESS_OBSDIR_COL'
# add to recipe
recipes.append(apero_wave_night)

# -----------------------------------------------------------------------------
# apero_ccf
# -----------------------------------------------------------------------------
apero_ccf = DrsRecipe(__INSTRUMENT__)
apero_ccf.name = 'apero_ccf_{0}.py'.format(INSTRUMENT_ALIAS)
apero_ccf.shortname = 'CCF'
apero_ccf.instrument = __INSTRUMENT__
apero_ccf.in_block_str = 'red'
apero_ccf.out_block_str = 'red'
apero_ccf.extension = 'fits'
apero_ccf.description = textentry('CCF_DESC')
apero_ccf.epilog = textentry('CCF_EXAMPLE')
apero_ccf.recipe_type = 'recipe'
apero_ccf.recipe_kind = 'rv'
apero_ccf.set_outputs(CCF_RV=files.out_ccf_fits)
apero_ccf.set_debug_plots('CCF_RV_FIT', 'CCF_RV_FIT_LOOP', 'CCF_SWAVE_REF',
                          'CCF_PHOTON_UNCERT')
apero_ccf.set_summary_plots('SUM_CCF_PHOTON_UNCERT', 'SUM_CCF_RV_FIT')
apero_ccf.set_arg(pos=0, **obs_dir)
apero_ccf.set_arg(name='files', dtype='files', pos='1+',
                  files=[files.out_ext_e2ds, files.out_ext_e2dsff,
                         files.out_tellu_obj], filelogic='exclusive',
                  helpstr=textentry('FILES_HELP') + textentry('CCF_FILES_HELP'),
                  limit=1)
apero_ccf.set_kwarg(name='--mask', dtype='file', default_ref='CCF_DEFAULT_MASK',
                    helpstr=textentry('CCF_MASK_HELP'),
                    files=files.other_ccf_mask_file)
apero_ccf.set_kwarg(name='--rv', dtype=float, default_ref='CCF_NO_RV_VAL',
                    helpstr=textentry('CCF_RV_HELP'))
apero_ccf.set_kwarg(name='--width', dtype=float, default_ref='CCF_DEFAULT_WIDTH',
                    helpstr=textentry('CCF_WIDTH_HELP'))
apero_ccf.set_kwarg(name='--step', dtype=float, default_ref='CCF_DEFAULT_STEP',
                    helpstr=textentry('CCF_STEP_HELP'))
apero_ccf.set_kwarg(name='--masknormmode', dtype=str,
                    default_ref='CCF_MASK_NORMALIZATION',
                    options=['None', 'all', 'order'],
                    helpstr=textentry('CCF_MASK_NORM_HELP'))
apero_ccf.set_kwarg(**add_db)
apero_ccf.set_kwarg(**blazefile)
apero_ccf.set_kwarg(**plot)
apero_ccf.group_func = grouping.group_individually
apero_ccf.group_column = 'REPROCESS_OBSDIR_COL'
# add to recipe
recipes.append(apero_ccf)

# -----------------------------------------------------------------------------
# apero_mk_tellu
# -----------------------------------------------------------------------------
apero_mk_tellu = DrsRecipe(__INSTRUMENT__)
apero_mk_tellu.name = 'apero_mk_tellu_{0}.py'.format(INSTRUMENT_ALIAS)
apero_mk_tellu.shortname = 'MKTELL'
apero_mk_tellu.instrument = __INSTRUMENT__
apero_mk_tellu.in_block_str = 'red'
apero_mk_tellu.out_block_str = 'red'
apero_mk_tellu.extension = 'fits'
apero_mk_tellu.description = textentry('MKTELL_DESC')
apero_mk_tellu.epilog = textentry('MKTELL_EXAMPLE')
apero_mk_tellu.recipe_type = 'recipe'
apero_mk_tellu.recipe_kind = 'tellu-hotstar'
apero_mk_tellu.set_outputs(TELLU_CONV=files.out_tellu_conv,
                           TELLU_TRANS=files.out_tellu_trans,
                           TELLU_PCLEAN=files.out_tellu_pclean)
apero_mk_tellu.set_debug_plots('MKTELLU_WAVE_FLUX1', 'MKTELLU_WAVE_FLUX2',
                               'TELLUP_WAVE_TRANS', 'TELLUP_ABSO_SPEC',
                               'TELLUP_CLEAN_OH')
apero_mk_tellu.set_summary_plots('SUM_MKTELLU_WAVE_FLUX',
                                 'SUM_TELLUP_WAVE_TRANS', 'SUM_TELLUP_ABSO_SPEC')
apero_mk_tellu.set_arg(pos=0, **obs_dir)
apero_mk_tellu.set_arg(name='files', dtype='files', pos='1+',
                       files=[files.out_ext_e2ds, files.out_ext_e2dsff],
                       filelogic='exclusive',
                       helpstr=(textentry('FILES_HELP') +
                                textentry('MKTELL_FILES_HELP')),
                       limit=1)
apero_mk_tellu.set_kwarg(**add_db)
apero_mk_tellu.set_kwarg(**blazefile)
apero_mk_tellu.set_kwarg(**plot)
apero_mk_tellu.set_kwarg(**wavefile)
apero_mk_tellu.set_kwarg(name='--use_template', dtype='bool', default=True,
                         helpstr=textentry('USE_TEMP_HELP'))
apero_mk_tellu.set_kwarg(name='--template', dtype='file', default='None',
                         files=[files.out_tellu_template],
                         helpstr=textentry('TEMPLATE_FILE_HELP'))
apero_mk_tellu.group_func = grouping.group_individually
apero_mk_tellu.group_column = 'REPROCESS_OBSDIR_COL'
# add to recipe
recipes.append(apero_mk_tellu)

# -----------------------------------------------------------------------------
# apero_mk_tellu_db
# -----------------------------------------------------------------------------
apero_mk_tellu_db = DrsRecipe(__INSTRUMENT__)
apero_mk_tellu_db.name = 'apero_mk_tellu_db_{0}.py'.format(INSTRUMENT_ALIAS)
apero_mk_tellu_db.shortname = 'MKTELLDB'
apero_mk_tellu_db.master = False
apero_mk_tellu_db.instrument = __INSTRUMENT__
apero_mk_tellu_db.in_block_str = 'red'
apero_mk_tellu_db.out_block_str = 'red'
apero_mk_tellu_db.extension = 'fits'
apero_mk_tellu_db.recipe_type = 'recipe'
apero_mk_tellu_db.recipe_kind = 'tellu-hotstar'
apero_mk_tellu_db.description = textentry('MKTELLDB_DESC')
apero_mk_tellu_db.epilog = textentry('MKTELLDB_EXAMPLE')
apero_mk_tellu_db.set_outputs()
apero_mk_tellu_db.set_kwarg(name='--cores', dtype=int, default=1,
                            helpstr=textentry('MKTELLDB_CORES'))
apero_mk_tellu_db.set_kwarg(name='--filetype', dtype=str,
                            default_ref='TELLURIC_FILETYPE',
                            helpstr=textentry('MKTELLDB_FILETYPE'),
                            options=['EXT_E2DS', 'EXT_E2DS_FF'])
apero_mk_tellu_db.set_kwarg(name='--fiber', dtype=str,
                            default_ref='TELLURIC_FIBER_TYPE',
                            helpstr=textentry('MKTELLDB_FIBER'),
                            options=['AB', 'A', 'B', 'C'])
apero_mk_tellu_db.set_kwarg(name='--test', dtype=str, default='None',
                            options=['True', 'False', '1', '0', 'None'],
                            helpstr=textentry('PROCESS_TEST_HELP'))
apero_mk_tellu_db.set_kwarg(**add_db)
apero_mk_tellu_db.set_kwarg(**blazefile)
apero_mk_tellu_db.set_kwarg(**plot)
apero_mk_tellu_db.set_kwarg(**wavefile)
apero_mk_tellu_db.group_func = grouping.no_group
apero_mk_tellu_db.group_column = None
# add to recipe
recipes.append(apero_mk_tellu_db)

# -----------------------------------------------------------------------------
# apero_fit_tellu
# -----------------------------------------------------------------------------
apero_fit_tellu = DrsRecipe(__INSTRUMENT__)
apero_fit_tellu.name = 'apero_fit_tellu_{0}.py'.format(INSTRUMENT_ALIAS)
apero_fit_tellu.shortname = 'FTELLU'
apero_fit_tellu.instrument = __INSTRUMENT__
apero_fit_tellu.in_block_str = 'red'
apero_fit_tellu.out_block_str = 'red'
apero_fit_tellu.extension = 'fits'
apero_fit_tellu.description = textentry('FTELLU_DESC')
apero_fit_tellu.epilog = textentry('FTELLU_EXAMPLE')
apero_fit_tellu.recipe_type = 'recipe'
apero_fit_tellu.recipe_kind = 'tellu'
apero_fit_tellu.set_outputs(ABSO_NPY=files.out_tellu_abso_npy,
                            ABSO1_NPY=files.out_tellu_abso1_npy,
                            TELLU_OBJ=files.out_tellu_obj,
                            SC1D_W_FILE=files.out_tellu_sc1d_w,
                            SC1D_V_FILE=files.out_tellu_sc1d_v,
                            TELLU_RECON=files.out_tellu_recon,
                            RC1D_W_FILE=files.out_tellu_rc1d_w,
                            RC1D_V_FILE=files.out_tellu_rc1d_v,
                            TELLU_PCLEAN=files.out_tellu_pclean)
apero_fit_tellu.set_debug_plots('EXTRACT_S1D', 'EXTRACT_S1D_WEIGHT',
                                'FTELLU_PCA_COMP1', 'FTELLU_PCA_COMP2',
                                'FTELLU_RECON_SPLINE1', 'FTELLU_RECON_SPLINE2',
                                'FTELLU_WAVE_SHIFT1', 'FTELLU_WAVE_SHIFT2',
                                'FTELLU_RECON_ABSO1', 'FTELLU_RECON_ABSO2',
                                'TELLUP_WAVE_TRANS', 'TELLUP_ABSO_SPEC',
                                'TELLUP_CLEAN_OH')
apero_fit_tellu.set_summary_plots('SUM_EXTRACT_S1D', 'SUM_FTELLU_RECON_ABSO',
                                  'SUM_TELLUP_WAVE_TRANS', 'SUM_TELLUP_ABSO_SPEC')
apero_fit_tellu.set_arg(pos=0, **obs_dir)
apero_fit_tellu.set_arg(name='files', dtype='files', pos='1+',
                        files=[files.out_ext_e2ds, files.out_ext_e2dsff],
                        filelogic='exclusive',
                        helpstr=(textentry('FILES_HELP')
                                 + textentry('FTELLU_FILES_HELP')),
                        limit=1)
apero_fit_tellu.set_kwarg(name='--use_template', dtype='bool', default=True,
                          helpstr=textentry('USE_TEMP_HELP'))
apero_fit_tellu.set_kwarg(name='--template', dtype='file', default='None',
                          files=[files.out_tellu_template],
                          helpstr=textentry('TEMPLATE_FILE_HELP'))
apero_fit_tellu.set_kwarg(**add_db)
apero_fit_tellu.set_kwarg(**blazefile)
apero_fit_tellu.set_kwarg(**plot)
apero_fit_tellu.set_kwarg(**wavefile)
apero_fit_tellu.group_func = grouping.group_individually
apero_fit_tellu.group_column = 'REPROCESS_OBSDIR_COL'
# add to recipe
recipes.append(apero_fit_tellu)

# -----------------------------------------------------------------------------
# apero_fit_tellu_db
# -----------------------------------------------------------------------------
apero_fit_tellu_db = DrsRecipe(__INSTRUMENT__)
apero_fit_tellu_db.name = 'apero_fit_tellu_db_{0}.py'.format(INSTRUMENT_ALIAS)
apero_fit_tellu_db.shortname = 'FTELLDB'
apero_fit_tellu_db.master = False
apero_fit_tellu_db.instrument = __INSTRUMENT__
apero_fit_tellu_db.in_block_str = 'red'
apero_fit_tellu_db.out_block_str = 'red'
apero_fit_tellu_db.extension = 'fits'
apero_fit_tellu_db.description = textentry('FTELLUDB_DESC')
apero_fit_tellu_db.epilog = textentry('FTELLUDB_EXAMPLE')
apero_fit_tellu_db.recipe_type = 'recipe'
apero_fit_tellu_db.recipe_kind = 'tellu-science'
apero_fit_tellu_db.set_outputs()
apero_fit_tellu_db.set_kwarg(name='--cores', dtype=int, default=1,
                             helpstr=textentry('FTELLUDB_CORES'))
apero_fit_tellu_db.set_kwarg(name='--filetype', dtype=str,
                             default_ref='TELLURIC_FILETYPE',
                             helpstr=textentry('FTELLUDB_FILETYPE'))
apero_fit_tellu_db.set_kwarg(name='--fiber', dtype=str,
                             default_ref='TELLURIC_FIBER_TYPE',
                             helpstr=textentry('FTELLUDB_FIBER'))
apero_fit_tellu_db.set_kwarg(name='--objname', dtype=str, default='None',
                             helpstr=textentry('FTELLUDB_OBJNAME'))
apero_fit_tellu_db.set_kwarg(name='--dprtype', dtype=str,
                             default_ref='TELLU_ALLOWED_DPRTYPES',
                             helpstr=textentry('FTELLUDB_DPRTYPES'))
apero_fit_tellu_db.set_kwarg(name='--test', dtype=str, default='None',
                             options=['True', 'False', '1', '0', 'None'],
                             helpstr=textentry('PROCESS_TEST_HELP'))
apero_fit_tellu_db.set_kwarg(**add_db)
apero_fit_tellu_db.set_kwarg(**add_db)
apero_fit_tellu_db.set_kwarg(**plot)
apero_fit_tellu_db.set_kwarg(**wavefile)
apero_fit_tellu_db.group_func = grouping.no_group
apero_fit_tellu_db.group_column = None
# add to recipe
recipes.append(apero_fit_tellu_db)

# -----------------------------------------------------------------------------
# apero_mk_template
# -----------------------------------------------------------------------------
apero_mk_template = DrsRecipe(__INSTRUMENT__)
apero_mk_template.name = 'apero_mk_template_{0}.py'.format(INSTRUMENT_ALIAS)
apero_mk_template.shortname = 'MKTEMP'
apero_mk_template.instrument = __INSTRUMENT__
apero_mk_template.in_block_str = 'red'
apero_mk_template.out_block_str = 'red'
apero_mk_template.extension = 'fits'
apero_mk_template.description = textentry('MKTEMP_DESC')
apero_mk_template.epilog = textentry('MKTEMP_EXAMPLE')
apero_mk_template.recipe_type = 'recipe'
apero_mk_template.recipe_kind = 'tellu'
apero_mk_template.set_outputs(TELLU_TEMP=files.out_tellu_template,
                              TELLU_BIGCUBE=files.out_tellu_bigcube,
                              TELLU_BIGCUBE0=files.out_tellu_bigcube0,
                              TELLU_TEMP_S1D=files.out_tellu_s1d_template,
                              TELLU_BIGCUBE_S1D=files.out_tellu_s1d_bigcube)
apero_mk_template.set_debug_plots('EXTRACT_S1D', 'MKTEMP_BERV_COV')
apero_mk_template.set_summary_plots('SUM_EXTRACT_S1D', 'SUM_MKTEMP_BERV_COV')
apero_mk_template.set_arg(name='objname', pos=0, dtype=str,
                          helpstr=textentry('MKTEMP_OBJNAME_HELP'))
apero_mk_template.set_kwarg(name='--filetype', dtype=str,
                            default_ref='MKTEMPLATE_FILETYPE',
                            helpstr=textentry('MKTEMP_FILETYPE'),
                            options=['EXT_E2DS', 'EXT_E2DS_FF'])
apero_mk_template.set_kwarg(name='--fiber', dtype=str,
                            default_ref='MKTEMPLATE_FIBER_TYPE',
                            helpstr=textentry('MKTEMP_FIBER'),
                            options=['AB', 'A', 'B', 'C'])
apero_mk_template.set_kwarg(**add_db)
apero_mk_template.set_kwarg(**blazefile)
apero_mk_template.set_kwarg(**plot)
apero_mk_template.set_kwarg(**wavefile)
apero_mk_template.group_func = grouping.no_group
apero_mk_template.group_column = None
# add to recipe
recipes.append(apero_mk_template)

# -----------------------------------------------------------------------------
# polar recipe
# -----------------------------------------------------------------------------
apero_pol = DrsRecipe(__INSTRUMENT__)
apero_pol.name = 'apero_pol_{0}.py'.format(INSTRUMENT_ALIAS)
apero_pol.shortname = 'POLAR'
apero_pol.instrument = __INSTRUMENT__
apero_pol.in_block_str = 'red'
apero_pol.out_block_str = 'red'
apero_pol.extension = 'fits'
apero_pol.description = textentry('FTELLU_DESC')
apero_pol.epilog = textentry('FTELLU_EXAMPLE')
apero_pol.recipe_type = 'recipe'
apero_pol.recipe_kind = 'polar'
apero_pol.set_outputs(POL_DEG_FILE=files.out_pol_deg,
                      POL_NULL1=files.out_pol_null1,
                      POL_NULL2=files.out_pol_null2,
                      POL_STOKESI=files.out_pol_stokesi,
                      POL_LSD=files.out_pol_lsd,
                      S1DW_POL=files.out_pol_s1dw,
                      S1DV_POL=files.out_pol_s1dv,
                      S1DW_NULL1=files.out_null1_s1dw,
                      S1DV_NULL1=files.out_null1_s1dv,
                      S1DW_NULL2=files.out_null2_s1dw,
                      S1DV_NULL2=files.out_null2_s1dv,
                      S1DW_STOKESI=files.out_stokesi_s1dw,
                      S1DV_STOKESI=files.out_stokesi_s1dv)
apero_pol.set_debug_plots('PLOT_POLAR_FIT_CONT', 'POLAR_CONTINUUM',
                          'POLAR_RESULTS', 'POLAR_STOKES_I', 'POLAR_LSD',
                          'EXTRACT_S1D_WEIGHT', 'EXTRACT_S1D')
apero_pol.set_summary_plots('SUM_EXTRACT_S1D')
apero_pol.set_arg(pos=0, **obs_dir)
apero_pol.set_kwarg(name='--exposures', dtype='files',
                    files=[files.out_ext_e2dsff, files.out_tellu_obj],
                    filelogic='exclusive', default='None',
                    helpstr='List of exposures to add (order determined by '
                            'recipe)', reprocess=True)
apero_pol.set_kwarg(name='--exp1', altnames=['-1'], dtype='file',
                    files=[files.out_ext_e2dsff, files.out_tellu_obj],
                    filelogic='exclusive', default='None',
                    helpstr='Override input exposure 1')
apero_pol.set_kwarg(name='--exp2', altnames=['-2'], dtype='file',
                    files=[files.out_ext_e2dsff, files.out_tellu_obj],
                    filelogic='exclusive', default='None',
                    helpstr='Override input exposure 2')
apero_pol.set_kwarg(name='--exp3', altnames=['-3'], dtype='file',
                    files=[files.out_ext_e2dsff, files.out_tellu_obj],
                    filelogic='exclusive', default='None',
                    helpstr='Override input exposure 3')
apero_pol.set_kwarg(name='--exp4', altnames=['-4'], dtype='file',
                    files=[files.out_ext_e2dsff, files.out_tellu_obj],
                    filelogic='exclusive', default='None',
                    helpstr='Override input exposure 4')
apero_pol.set_kwarg(name='--objrv', dtype=float, default=0.0,
                    helpstr='Object radial velocity [km/s]')
apero_pol.set_kwarg(name='--lsdmask', altnames=['-m'], dtype=str,
                    helpstr='LSD mask', default='None')
apero_pol.set_kwarg(name='--output', altnames=['-o'], dtype=str,
                    helpstr='Output file', default='None')
apero_pol.set_kwarg(name='--output_lsd', altnames=['-l'], dtype=str,
                    helpstr='Output LSD file', default='None')
apero_pol.set_kwarg(name='--lsd', altnames=['-L'], dtype='switch',
                    default=False, helpstr='Run LSD analysis')
apero_pol.set_kwarg(**blazefile)
apero_pol.set_kwarg(**plot)
apero_pol.set_kwarg(**wavefile)
# TODO: Will need custom group function
apero_pol.group_func = grouping.group_by_polar_sequence
apero_pol.group_column = 'REPROCESS_OBSDIR_COL'
# add to recipe
recipes.append(apero_pol)

# -----------------------------------------------------------------------------
# apero_postprocess
# -----------------------------------------------------------------------------
apero_postprocess = DrsRecipe(__INSTRUMENT__)
apero_postprocess.name = 'apero_postprocess_{0}.py'.format(INSTRUMENT_ALIAS)
apero_postprocess.shortname = 'OBJPOST'
apero_postprocess.instrument = __INSTRUMENT__
apero_postprocess.in_block_str = 'tmp'
apero_postprocess.out_block_str = 'out'
apero_postprocess.extension = 'fits'
apero_postprocess.description = textentry('OUT_DESC_HELP')
apero_postprocess.epilog = ''
apero_postprocess.recipe_type = 'recipe'
apero_postprocess.recipe_kind = 'post'
apero_postprocess.set_arg(pos=0, **obs_dir)
apero_postprocess.set_arg(name='files', dtype='files', pos='1+',
                          files=[files.pp_file],
                          filelogic='exclusive',
                          helpstr=(textentry('FILES_HELP')),
                          limit=1)
apero_postprocess.set_kwarg(name='--overwrite', dtype='switch',
                            default_ref='POST_OVERWRITE',
                            helpstr=textentry('OUT_OVERWRITE_HELP'))
apero_postprocess.set_kwarg(name='--clear', dtype='switch',
                            default_ref='POST_CLEAR_REDUCED',
                            helpstr=textentry('OUT_CLEAR_HELP'))
apero_postprocess.group_func = grouping.group_individually
apero_postprocess.group_column = 'REPROCESS_OBSDIR_COL'
# add to recipe
recipes.append(apero_postprocess)

# =============================================================================
# Graveyard - old scripts
# =============================================================================

# -----------------------------------------------------------------------------
# apero_wave_master_old
# -----------------------------------------------------------------------------
apero_wave_master_old = DrsRecipe(__INSTRUMENT__)
apero_wave_master_old.name = 'apero_wave_master_old_{0}.py'.format(INSTRUMENT_ALIAS)
apero_wave_master_old.shortname = 'WAVEM'
apero_wave_master_old.instrument = __INSTRUMENT__
apero_wave_master_old.in_block_str = 'tmp'
apero_wave_master_old.out_block_str = 'red'
apero_wave_master_old.extension = 'fits'
apero_wave_master_old.description = textentry('WAVE_DESC')
apero_wave_master_old.epilog = textentry('WAVE_EXAMPLE')
apero_wave_master_old.recipe_type = 'recipe'
apero_wave_master_old.recipe_kind = 'calib-master'
apero_wave_master_old.set_outputs(WAVE_E2DS=files.out_ext_e2dsff,
                                  WAVE_HCLL=files.out_wave_hcline,
                                  WAVEM_HCRES=files.out_wavem_hcres,
                                  WAVEM_HCMAP=files.out_wavem_hc,
                                  WAVEM_FPMAP=files.out_wavem_fp,
                                  WAVEM_FPRESTAB=files.out_wavem_res_table,
                                  WAVEM_FPLLTAB=files.out_wavem_ll_table,
                                  WAVEM_HCLIST=files.out_wave_hclist_master,
                                  WAVEM_FPLIST=files.out_wave_fplist_master,
                                  CCF_RV=files.out_ccf_fits)
apero_wave_master_old.set_debug_plots('WAVE_HC_GUESS', 'WAVE_HC_BRIGHTEST_LINES',
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
apero_wave_master_old.set_summary_plots('SUM_WAVE_FP_IPT_CWID_LLHC',
                                        'SUM_WAVE_LITTROW_CHECK',
                                        'SUM_WAVE_LITTROW_EXTRAP',
                                        'SUM_CCF_RV_FIT', 'SUM_WAVE_FIBER_COMP',
                                        'SUM_WAVENIGHT_ITERPLOT',
                                        'SUM_WAVENIGHT_HISTPLOT', )
apero_wave_master_old.set_arg(pos=0, **obs_dir)
apero_wave_master_old.set_kwarg(name='--hcfiles', dtype='files',
                                files=[files.pp_hc1_hc1],
                                filelogic='exclusive', required=True,
                                helpstr=textentry('WAVE_HCFILES_HELP'), default=[])
apero_wave_master_old.set_kwarg(name='--fpfiles', dtype='files',
                                files=[files.pp_fp_fp],
                                filelogic='exclusive', required=True,
                                helpstr=textentry('WAVE_FPFILES_HELP'), default=[])
apero_wave_master_old.set_kwarg(**add_db)
apero_wave_master_old.set_kwarg(**badfile)
apero_wave_master_old.set_kwarg(**dobad)
apero_wave_master_old.set_kwarg(**backsub)
apero_wave_master_old.set_kwarg(**blazefile)
apero_wave_master_old.set_kwarg(default=True, **combine)
apero_wave_master_old.set_kwarg(**darkfile)
apero_wave_master_old.set_kwarg(**dodark)
apero_wave_master_old.set_kwarg(**fiber)
apero_wave_master_old.set_kwarg(**flipimage)
apero_wave_master_old.set_kwarg(**fluxunits)
apero_wave_master_old.set_kwarg(**locofile)
apero_wave_master_old.set_kwarg(**orderpfile)
apero_wave_master_old.set_kwarg(**plot)
apero_wave_master_old.set_kwarg(**resize)
apero_wave_master_old.set_kwarg(**shapexfile)
apero_wave_master_old.set_kwarg(**shapeyfile)
apero_wave_master_old.set_kwarg(**shapelfile)
apero_wave_master_old.set_kwarg(**wavefile)
apero_wave_master_old.set_kwarg(name='--forceext', dtype='bool',
                                default_ref='WAVE_ALWAYS_EXTRACT',
                                helpstr='WAVE_EXTRACT_HELP')
apero_wave_master_old.set_kwarg(name='--hcmode', dtype='options',
                                helpstr=textentry('HCMODE_HELP'), options=['0'],
                                default_ref='WAVE_MODE_HC')
apero_wave_master_old.set_kwarg(name='--fpmode', dtype='options',
                                helpstr=textentry('FPMODE_HELP'), options=['0', '1'],
                                default_ref='WAVE_MODE_FP')
apero_wave_master_old.group_func = grouping.group_by_dirname
apero_wave_master_old.group_column = 'REPROCESS_OBSDIR_COL'
# add to recipe
recipes.append(apero_wave_master_old)

# -----------------------------------------------------------------------------
# apero_wave_night_old
# -----------------------------------------------------------------------------
apero_wave_night_old = DrsRecipe(__INSTRUMENT__)
apero_wave_night_old.name = 'apero_wave_night_old_{0}.py'.format(INSTRUMENT_ALIAS)
apero_wave_night_old.shortname = 'WAVE'
apero_wave_night_old.instrument = __INSTRUMENT__
apero_wave_night_old.in_block_str = 'tmp'
apero_wave_night_old.out_block_str = 'red'
apero_wave_night_old.extension = 'fits'
apero_wave_night_old.description = textentry('WAVE_DESC')
apero_wave_night_old.epilog = textentry('WAVE_EXAMPLE')
apero_wave_night_old.recipe_type = 'recipe'
apero_wave_night_old.recipe_kind = 'calib-night'
apero_wave_night_old.set_outputs(WAVE_E2DS=files.out_ext_e2dsff,
                                 WAVEMAP_NIGHT=files.out_wave_night,
                                 WAVE_HCLIST=files.out_wave_hclist,
                                 WAVE_FPLIST=files.out_wave_fplist,
                                 CCF_RV=files.out_ccf_fits)
apero_wave_night_old.set_debug_plots('WAVENIGHT_ITERPLOT', 'WAVENIGHT_HISTPLOT',
                                     'WAVEREF_EXPECTED', 'CCF_RV_FIT',
                                     'CCF_RV_FIT_LOOP', 'EXTRACT_S1D',
                                     'EXTRACT_S1D_WEIGHT')
apero_wave_night_old.set_summary_plots('SUM_WAVENIGHT_ITERPLOT',
                                       'SUM_WAVENIGHT_HISTPLOT',
                                       'SUM_CCF_RV_FIT')
apero_wave_night_old.set_arg(pos=0, **obs_dir)
apero_wave_night_old.set_kwarg(name='--hcfiles', dtype='files',
                               files=[files.pp_hc1_hc1],
                               filelogic='exclusive', required=True,
                               helpstr=textentry('WAVE_HCFILES_HELP'), default=[])
apero_wave_night_old.set_kwarg(name='--fpfiles', dtype='files',
                               files=[files.pp_fp_fp],
                               filelogic='exclusive', required=True,
                               helpstr=textentry('WAVE_FPFILES_HELP'), default=[])
apero_wave_night_old.set_kwarg(**add_db)
apero_wave_night_old.set_kwarg(**badfile)
apero_wave_night_old.set_kwarg(**dobad)
apero_wave_night_old.set_kwarg(**backsub)
apero_wave_night_old.set_kwarg(**blazefile)
apero_wave_night_old.set_kwarg(default=True, **combine)
apero_wave_night_old.set_kwarg(**darkfile)
apero_wave_night_old.set_kwarg(**dodark)
apero_wave_night_old.set_kwarg(**fiber)
apero_wave_night_old.set_kwarg(**flipimage)
apero_wave_night_old.set_kwarg(**fluxunits)
apero_wave_night_old.set_kwarg(**locofile)
apero_wave_night_old.set_kwarg(**orderpfile)
apero_wave_night_old.set_kwarg(**plot)
apero_wave_night_old.set_kwarg(**resize)
apero_wave_night_old.set_kwarg(**shapexfile)
apero_wave_night_old.set_kwarg(**shapeyfile)
apero_wave_night_old.set_kwarg(**shapelfile)
apero_wave_night_old.set_kwarg(**wavefile)
apero_wave_night_old.set_kwarg(name='--forceext', dtype='bool',
                               default_ref='WAVE_ALWAYS_EXTRACT',
                               helpstr='WAVE_EXTRACT_HELP')
apero_wave_night_old.group_func = grouping.group_by_dirname
apero_wave_night_old.group_column = 'REPROCESS_OBSDIR_COL'
# add to recipe
recipes.append(apero_wave_night_old)

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
#           - whether a file is in the master sequence (use master obs dir only
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
#           # note as master=True it will only extract from the master obs dir
#
#           run = drs_recipe.DrsRunSequence('run', __INSTRUMENT__)
#           run.add(apero_extract, master=True, files=[files.pp_obj_fp],
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
full_seq.add(apero_preprocess, recipe_kind='pre-all')
full_seq.add(apero_dark_master, master=True)
full_seq.add(apero_badpix, name='BADM', master=True, recipe_kind='calib-master')
full_seq.add(apero_loc, name='LOCMC', files=[files.pp_dark_flat], master=True,
             recipe_kind='calib-master-C')
full_seq.add(apero_loc, name='LOCMAB', files=[files.pp_flat_dark], master=True,
             recipe_kind='calib-master-AB')
full_seq.add(apero_shape_master, master=True)
full_seq.add(apero_shape, name='SHAPELM', master=True,
             recipe_kind='calib-master')
full_seq.add(apero_flat, name='FLATM', master=True,
             recipe_kind='calib-master')
full_seq.add(apero_thermal, name='THI_M', files=[files.pp_dark_dark_int],
             master=True, recipe_kind='calib-master-INT')
full_seq.add(apero_thermal, name='THT_M', files=[files.pp_dark_dark_tel],
             master=True, recipe_kind='calib-master-TEL')
full_seq.add(apero_leak_master, master=True)
full_seq.add(apero_wave_master, master=True,
             rkwargs=dict(hcfiles=[files.pp_hc1_hc1],
                          fpfiles=[files.pp_fp_fp]))
# night runs
full_seq.add(apero_badpix)
full_seq.add(apero_loc, files=[files.pp_dark_flat], name='LOCC',
             recipe_kind='calib-night-C')
full_seq.add(apero_loc, files=[files.pp_flat_dark], name='LOCAB',
             recipe_kind='calib-night-AB')
full_seq.add(apero_shape)
full_seq.add(apero_flat, files=[files.pp_flat_flat])
full_seq.add(apero_thermal, files=[files.pp_dark_dark_int], name='THI')
full_seq.add(apero_thermal, files=[files.pp_dark_dark_tel], name='THT')
full_seq.add(apero_wave_night)
# extract all OBJ_DARK and OBJ_FP
full_seq.add(apero_extract, name='EXTALL', recipe_kind='extract-ALL',
             files=[files.pp_obj_dark, files.pp_obj_fp, files.pp_polar_dark,
                    files.pp_polar_fp])
# correct leakage
full_seq.add(apero_leak, name='LEAKALL', files=[files.out_ext_e2dsff],
             fiber='AB', filters=dict(KW_DPRTYPE=['OBJ_FP', 'POLAR_FP']),
             recipe_kind='leak-ALL')
# telluric recipes
full_seq.add(apero_mk_tellu, name='MKTELLU1', recipe_kind='tellu-hotstar',
             files=[files.out_ext_e2dsff], fiber='AB',
             filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
                          KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP', 'POLAR_FP',
                                      'POLAR_DARK']))
full_seq.add(apero_fit_tellu, name='MKTELLU2', recipe_kind='tellu-hotstar',
             files=[files.out_ext_e2dsff], fiber='AB',
             filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
                          KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP', 'POLAR_FP',
                                      'POLAR_DARK']))
full_seq.add(apero_mk_template, name='MKTELLU3',
             fiber='AB', template_required=True, recipe_kind='tellu-hotstar',
             arguments=dict(objname='TELLURIC_TARGETS'),
             filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
                          KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP', 'POLAR_FP',
                                      'POLAR_DARK']))
full_seq.add(apero_mk_tellu, name='MKTELLU4', files=[files.out_ext_e2dsff],
             fiber='AB', template_required=True, recipe_kind='tellu-hotstar',
             filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
                          KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP', 'POLAR_FP',
                                      'POLAR_DARK']))
full_seq.add(apero_fit_tellu, name='FTELLU1', recipe_kind='tellu-science',
             files=[files.out_ext_e2dsff], fiber='AB',
             filters=dict(KW_OBJNAME='SCIENCE_TARGETS',
                          KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP', 'POLAR_FP',
                                      'POLAR_DARK']))
full_seq.add(apero_mk_template, name='FTELLU2',
             fiber='AB',
             arguments=dict(objname='SCIENCE_TARGETS'),
             filters=dict(KW_OBJNAME='SCIENCE_TARGETS',
                          KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP', 'POLAR_FP',
                                      'POLAR_DARK']),
             template_required=True, recipe_kind='tellu-science')
full_seq.add(apero_fit_tellu, name='FTELLU3',
             files=[files.out_ext_e2dsff], fiber='AB',
             filters=dict(KW_OBJNAME='SCIENCE_TARGETS',
                          KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP', 'POLAR_FP',
                                      'POLAR_DARK']),
             template_required=True, recipe_kind='tellu-science')

# ccf on all OBJ_DARK / OBJ_FP
full_seq.add(apero_ccf, files=[files.out_tellu_obj], fiber='AB',
             filters=dict(KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP', 'POLAR_FP',
                                      'POLAR_DARK']),
             recipe_kind='rv-tcorr')

# polar sequence on all POLAR_DARK / POLAR_FP
full_seq.add(apero_pol, rkwargs=dict(exposures=[files.out_tellu_obj]), fiber='AB',
             filters=dict(KW_DPRTYPE=['POLAR_FP', 'POLAR_DARK']),
             recipe_kind='polar-tcorr')

# post processing
full_seq.add(apero_postprocess, name='POSTALL', files=[files.pp_file],
             recipe_kind='post-all',
             filters=dict(KW_DPRTYPE=['OBJ_FP', 'OBJ_DARK', 'POLAR_FP',
                                      'POLAR_DARK']))

# -----------------------------------------------------------------------------
# limited sequence (master + nights)
# -----------------------------------------------------------------------------
limited_seq = drs_recipe.DrsRunSequence('limited_seq', __INSTRUMENT__)
# master run
limited_seq.add(apero_preprocess, recipe_kind='pre-all')
limited_seq.add(apero_dark_master, master=True)
limited_seq.add(apero_badpix, name='BADM', master=True,
                recipe_kind='calib-master')
limited_seq.add(apero_loc, name='LOCMC', files=[files.pp_dark_flat], master=True,
                recipe_kind='calib-master-C')
limited_seq.add(apero_loc, name='LOCMAB', files=[files.pp_flat_dark], master=True,
                recipe_kind='calib-master-AB')
limited_seq.add(apero_shape_master, master=True)
limited_seq.add(apero_shape, name='SHAPELM', master=True,
                recipe_kind='calib-master')
limited_seq.add(apero_flat, name='FLATM', master=True,
                recipe_kind='calib-master')
limited_seq.add(apero_thermal, name='THI_M', files=[files.pp_dark_dark_int],
                master=True, recipe_kind='calib-master-INT')
limited_seq.add(apero_thermal, name='THT_M', files=[files.pp_dark_dark_tel],
                master=True, recipe_kind='calib-master-TEL')
limited_seq.add(apero_leak_master, master=True)
limited_seq.add(apero_wave_master, master=True,
                rkwargs=dict(hcfiles=[files.pp_hc1_hc1],
                             fpfiles=[files.pp_fp_fp]))
# night runs
limited_seq.add(apero_badpix)
limited_seq.add(apero_loc, files=[files.pp_dark_flat], name='LOCC',
                recipe_kind='calib-night-C')
limited_seq.add(apero_loc, files=[files.pp_flat_dark], name='LOCAB',
                recipe_kind='calib-night-AB')
limited_seq.add(apero_shape)
limited_seq.add(apero_flat, files=[files.pp_flat_flat])
limited_seq.add(apero_thermal, files=[files.pp_dark_dark_int], name='THI')
limited_seq.add(apero_thermal, files=[files.pp_dark_dark_tel], name='THT')
limited_seq.add(apero_wave_night)
# extract tellurics
limited_seq.add(apero_extract, name='EXTTELL', recipe_kind='extract-hotstar',
                files=[files.pp_obj_dark, files.pp_obj_fp, files.pp_polar_fp,
                       files.pp_polar_dark],
                filters=dict(KW_OBJNAME='TELLURIC_TARGETS'))

# extract science
limited_seq.add(apero_extract, name='EXTOBJ', recipe_kind='extract-science',
                files=[files.pp_obj_dark, files.pp_obj_fp, files.pp_polar_fp,
                       files.pp_polar_dark],
                filters=dict(KW_OBJNAME='SCIENCE_TARGETS'))

# correct leakage for any telluric targets that are OBJ_FP
limited_seq.add(apero_leak, name='LEAKTELL', recipe_kind='leak-hotstar',
                files=[files.out_ext_e2dsff], fiber='AB',
                filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
                             KW_DPRTYPE=['OBJ_FP', 'POLAR_FP']))

# correct leakage for any science targets that are OBJ_FP
limited_seq.add(apero_leak, name='LEAKOBJ', recipe_kind='leak-science',
                files=[files.out_ext_e2dsff], fiber='AB',
                filters=dict(KW_OBJNAME='SCIENCE_TARGETS',
                             KW_DPRTYPE=['OBJ_FP', 'POLAR_FP']))

# other telluric recipes
limited_seq.add(apero_mk_tellu, name='MKTELLU1', recipe_kind='tellu-hotstar',
                files=[files.out_ext_e2dsff], fiber='AB',
                filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
                             KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP', 'POLAR_DARK',
                                         'POLAR_FP']))
limited_seq.add(apero_fit_tellu, name='MKTELLU2', recipe_kind='tellu-hotstar',
                files=[files.out_ext_e2dsff], fiber='AB',
                filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
                             KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP', 'POLAR_DARK',
                                         'POLAR_FP']))
limited_seq.add(apero_mk_template, name='MKTELLU3', recipe_kind='tellu-hotstar',
                fiber='AB', arguments=dict(objname='TELLURIC_TARGETS'),
                filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
                             KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP', 'POLAR_DARK',
                                         'POLAR_FP']),
                template_required=True)
limited_seq.add(apero_mk_tellu, name='MKTELLU4', recipe_kind='tellu-hotstar',
                files=[files.out_ext_e2dsff], fiber='AB',
                filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
                             KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP', 'POLAR_DARK',
                                         'POLAR_FP']),
                template_required=True)
limited_seq.add(apero_fit_tellu, name='FTELLU1', recipe_kind='tellu-science',
                files=[files.out_ext_e2dsff], fiber='AB',
                filters=dict(KW_OBJNAME='SCIENCE_TARGETS',
                             KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP', 'POLAR_DARK',
                                         'POLAR_FP']))
limited_seq.add(apero_mk_template, name='FTELLU2', recipe_kind='tellu-science',
                fiber='AB', arguments=dict(objname='SCIENCE_TARGETS'),
                filters=dict(KW_OBJNAME='SCIENCE_TARGETS',
                             KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP', 'POLAR_DARK',
                                         'POLAR_FP']),
                template_required=True)
limited_seq.add(apero_fit_tellu, name='FTELLU3', recipe_kind='tellu-science',
                files=[files.out_ext_e2dsff], fiber='AB',
                filters=dict(KW_OBJNAME='SCIENCE_TARGETS',
                             KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP', 'POLAR_DARK',
                                         'POLAR_FP']),
                template_required=True)

# ccf
limited_seq.add(apero_ccf, files=[files.out_tellu_obj], fiber='AB',
                recipe_kind='rv-tcorr',
                filters=dict(KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP', 'POLAR_DARK',
                                         'POLAR_FP'],
                             KW_OBJNAME='SCIENCE_TARGETS'))

# polar sequence on all POLAR_DARK / POLAR_FP
limited_seq.add(apero_pol, rkwargs=dict(exposures=[files.out_tellu_obj]),
                recipe_kind='polar-tcorr',
                fiber='AB', filters=dict(KW_DPRTYPE=['POLAR_FP', 'POLAR_DARK']))

# post processing
limited_seq.add(apero_postprocess, name='TELLPOST', files=[files.pp_file],
                recipe_kind='post-hotstar',
                filters=dict(KW_DPRTYPE=['OBJ_FP', 'OBJ_DARK', 'POLAR_DARK',
                                         'POLAR_FP'],
                             KW_OBJNAME='TELLURIC_TARGETS'))

limited_seq.add(apero_postprocess, name='SCIPOST', files=[files.pp_file],
                recipe_kind='post-science',
                filters=dict(KW_DPRTYPE=['OBJ_FP', 'OBJ_DARK', 'POLAR_DARK',
                                         'POLAR_FP'],
                             KW_OBJNAME='SCIENCE_TARGETS'))

# -----------------------------------------------------------------------------
# pp sequence (for trigger)
# -----------------------------------------------------------------------------
pp_seq = drs_recipe.DrsRunSequence('pp_seq', __INSTRUMENT__)
pp_seq.add(apero_preprocess)

pp_seq_opt = drs_recipe.DrsRunSequence('pp_seq_opt', __INSTRUMENT__)
pp_seq_opt.add(apero_preprocess, name='PP_CAL', recipe_kind='pre-cal',
               filters=dict(KW_OBJNAME='Calibration'))
pp_seq_opt.add(apero_preprocess, name='PP_SCI', recipe_kind='pre-sci',
               filters=dict(KW_OBJNAME='SCIENCE_TARGETS'))
pp_seq_opt.add(apero_preprocess, name='PP_TEL', recipe_kind='pre-tel',
               filters=dict(KW_OBJNAME='TELLURIC_TARGETS'))
pp_seq_opt.add(apero_preprocess, name='PP_HC1HC1', files=[files.raw_hc1_hc1],
               recipe_kind='pre-hchc')
pp_seq_opt.add(apero_preprocess, name='PP_FPFP', files=[files.raw_fp_fp],
               recipe_kind='pre-fpfp')
pp_seq_opt.add(apero_preprocess, name='PP_DFP', files=[files.raw_dark_fp],
               recipe_kind='pre-dfp')
pp_seq_opt.add(apero_preprocess, name='PP_SKY', files=[files.raw_dark_dark_sky],
               recipe_kind='pre-sky')
pp_seq_opt.add(apero_preprocess, name='PP_LFC', files=[files.raw_lfc_lfc],
               recipe_kind='pre-lfc')
pp_seq_opt.add(apero_preprocess, name='PP_LFCFP', files=[files.raw_lfc_fp],
               recipe_kind='pre-lfcfp')
pp_seq_opt.add(apero_preprocess, name='PP_FPLFC', files=[files.raw_fp_lfc],
               recipe_kind='pre-fplfc')

# -----------------------------------------------------------------------------
# master sequence (for trigger)
# -----------------------------------------------------------------------------
master_seq = drs_recipe.DrsRunSequence('master_seq', __INSTRUMENT__)
master_seq.add(apero_dark_master, master=True)
master_seq.add(apero_badpix, name='BADM', master=True,
               recipe_kind='calib-master')
master_seq.add(apero_loc, name='LOCMC', files=[files.pp_dark_flat], master=True,
               recipe_kind='calib-master-C')
master_seq.add(apero_loc, name='LOCMAB', files=[files.pp_flat_dark], master=True,
               recipe_kind='calib-master-AB')
master_seq.add(apero_shape_master, master=True)
master_seq.add(apero_shape, name='SHAPELM', master=True,
               recipe_kind='calib-master')
master_seq.add(apero_flat, name='FLATM', master=True,
               recipe_kind='calib-master')
master_seq.add(apero_thermal, name='THI_M', files=[files.pp_dark_dark_int],
               master=True, recipe_kind='calib-master-INT')
master_seq.add(apero_thermal, name='THT_M', files=[files.pp_dark_dark_tel],
               master=True, recipe_kind='calib-master-TEL')
master_seq.add(apero_leak_master, master=True)
master_seq.add(apero_wave_master, master=True,
               rkwargs=dict(hcfiles=[files.pp_hc1_hc1],
                            fpfiles=[files.pp_fp_fp]))

# -----------------------------------------------------------------------------
# calibration run (for trigger)
# -----------------------------------------------------------------------------
calib_seq = drs_recipe.DrsRunSequence('calib_seq', __INSTRUMENT__)
# night runs
calib_seq.add(apero_badpix)
calib_seq.add(apero_loc, files=[files.pp_dark_flat], name='LOCC',
              recipe_kind='calib-night-C')
calib_seq.add(apero_loc, files=[files.pp_flat_dark], name='LOCAB',
              recipe_kind='calib-night-AB')
calib_seq.add(apero_shape)
calib_seq.add(apero_flat, files=[files.pp_flat_flat])
calib_seq.add(apero_thermal, files=[files.pp_dark_dark_int])
calib_seq.add(apero_thermal, files=[files.pp_dark_dark_tel])
calib_seq.add(apero_wave_night)

# -----------------------------------------------------------------------------
# telluric sequence (for trigger)
# -----------------------------------------------------------------------------
tellu_seq = drs_recipe.DrsRunSequence('tellu_seq', __INSTRUMENT__)
# extract science
tellu_seq.add(apero_extract, name='EXTTELL', recipe_kind='extract-hotstar',
              files=[files.pp_obj_dark, files.pp_obj_fp, files.pp_polar_dark,
                     files.pp_polar_fp],
              filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
                           KW_DPRTYPE=['OBJ_FP', 'OBJ_DARK', 'POLAR_DARK',
                                       'POLAR_FP']))

# correct leakage for any telluric targets that are OBJ_FP
tellu_seq.add(apero_leak, name='LEAKTELL', recipe_kind='leak-hotstar',
              files=[files.out_ext_e2dsff], fiber='AB',
              filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
                           KW_DPRTYPE=['OBJ_FP', 'POLAR_FP']))

# other telluric recipes
tellu_seq.add(apero_mk_tellu, name='MKTELLU1', recipe_kind='tellu-hotstar',
              files=[files.out_ext_e2dsff], fiber='AB',
              filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
                           KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP', 'POLAR_DARK',
                                       'POLAR_FP']))

tellu_seq.add(apero_fit_tellu, name='MKTELLU2', recipe_kind='tellu-hotstar',
              files=[files.out_ext_e2dsff], fiber='AB',
              filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
                           KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP', 'POLAR_DARK',
                                       'POLAR_FP']))

tellu_seq.add(apero_mk_template, name='MKTELLU3', recipe_kind='tellu-hotstar',
              fiber='AB', files=[files.out_ext_e2dsff],
              arguments=dict(objname='TELLURIC_TARGETS'),
              filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
                           KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP', 'POLAR_DARK',
                                       'POLAR_FP']),
              template_required=True)

tellu_seq.add(apero_mk_tellu, name='MKTELLU4', recipe_kind='tellu-hotstar',
              fiber='AB', files=[files.out_ext_e2dsff],
              filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
                           KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP', 'POLAR_DARK',
                                       'POLAR_FP']),
              template_required=True)

# post processing
tellu_seq.add(apero_postprocess, files=[files.pp_file], name='TELLPOST',
              recipe_kind='post-hotstar',
              filters=dict(KW_DPRTYPE=['OBJ_FP', 'OBJ_DARK', 'POLAR_DARK',
                                       'POLAR_FP'],
                           KW_OBJNAME='TELLURIC_TARGETS'))

# -----------------------------------------------------------------------------
# science sequence (for trigger)
# -----------------------------------------------------------------------------
science_seq = drs_recipe.DrsRunSequence('science_seq', __INSTRUMENT__)
# extract science
science_seq.add(apero_extract, name='EXTOBJ', recipe_kind='extract-science',
                files=[files.pp_obj_dark, files.pp_obj_fp, files.pp_polar_dark,
                       files.pp_polar_fp],
                filters=dict(KW_OBJNAME='SCIENCE_TARGETS',
                             KW_DPRTYPE=['OBJ_FP', 'OBJ_DARK', 'POLAR_DARK',
                                         'POLAR_FP']))

# correct leakage for any science targets that are OBJ_FP
science_seq.add(apero_leak, name='LEAKOBJ', recipe_kind='leak-science',
                files=[files.out_ext_e2dsff], fiber='AB',
                filters=dict(KW_DPRTYPE=['OBJ_FP', 'POLAR_FP'],
                             KW_OBJNAME='SCIENCE_TARGETS'))

science_seq.add(apero_fit_tellu, name='FTELLU1', recipe_kind='tellu-science',
                files=[files.out_ext_e2dsff], fiber='AB',
                filters=dict(KW_OBJNAME='SCIENCE_TARGETS',
                             KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP', 'POLAR_DARK',
                                         'POLAR_FP']))

science_seq.add(apero_mk_template, name='FTELLU2', fiber='AB',
                recipe_kind='tellu-science',
                arguments=dict(objname='SCIENCE_TARGETS'),
                filters=dict(KW_OBJNAME='SCIENCE_TARGETS',
                             KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP', 'POLAR_DARK',
                                         'POLAR_FP']),
                template_required=True)
science_seq.add(apero_fit_tellu, name='FTELLU3', recipe_kind='tellu-science',
                files=[files.out_ext_e2dsff], fiber='AB',
                filters=dict(KW_OBJNAME='SCIENCE_TARGETS',
                             KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP', 'POLAR_DARK',
                                         'POLAR_FP']),
                template_required=True)

# ccf
science_seq.add(apero_ccf, files=[files.out_tellu_obj], fiber='AB',
                recipe_kind='rv-tcorr',
                filters=dict(KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP', 'POLAR_DARK',
                                         'POLAR_FP'],
                             KW_OBJNAME='SCIENCE_TARGETS'))

# polar sequence on all POLAR_DARK / POLAR_FP
science_seq.add(apero_pol, rkwargs=dict(exposures=[files.out_tellu_obj]),
                fiber='AB', recipe_kind='polar-tcorr',
                filters=dict(KW_DPRTYPE=['POLAR_FP', 'POLAR_DARK'],
                             KW_OBJNAME='SCIENCE_TARGETS'))

# post processing
science_seq.add(apero_postprocess, files=[files.pp_file], name='SCIPOST',
                recipe_kind='post-science',
                filters=dict(KW_DPRTYPE=['OBJ_FP', 'OBJ_DARK', 'POLAR_DARK',
                                         'POLAR_FP'],
                             KW_OBJNAME='SCIENCE_TARGETS'))

# -----------------------------------------------------------------------------
# science sequence (for trigger)
# -----------------------------------------------------------------------------
# TODO: TEST THIS
quick_seq = drs_recipe.DrsRunSequence('quick_seq', __INSTRUMENT__)
# extract science
quick_seq.add(apero_extract, name='EXTQUICK', recipe_kind='extract-quick',
              files=[files.pp_obj_dark, files.pp_obj_fp, files.pp_polar_dark,
                     files.pp_polar_fp],
              arguments=dict(quicklook=True),
              filters=dict(KW_OBJNAME='SCIENCE_TARGETS',
                           KW_DPRTYPE=['OBJ_FP', 'OBJ_DARK', 'POLAR_DARK',
                                       'POLAR_FP']))

# -----------------------------------------------------------------------------
# blank sequence (for trigger)
# -----------------------------------------------------------------------------
blank_seq = drs_recipe.DrsRunSequence('blank_seq', __INSTRUMENT__)

# -----------------------------------------------------------------------------
# engineering sequences
# -----------------------------------------------------------------------------
eng_seq = drs_recipe.DrsRunSequence('eng_seq', __INSTRUMENT__)

# extract sequences
eng_seq.add(apero_extract, name='EXT_HC1HC1', files=[files.pp_hc1_hc1],
            recipe_kind='extract-hchc')
eng_seq.add(apero_extract, name='EXT_FPFP', files=[files.pp_fp_fp],
            recipe_kind='extract-fpfp')
eng_seq.add(apero_extract, name='EXT_DFP', files=[files.pp_dark_fp],
            recipe_kind='extract-dfp')
eng_seq.add(apero_extract, name='EXT_SKY', files=[files.pp_dark_dark_sky],
            recipe_kind='extract-sky')
eng_seq.add(apero_extract, name='EXT_LFC', files=[files.pp_lfc_lfc],
            recipe_kind='extract-lfc')
eng_seq.add(apero_extract, name='EXT_FPD', files=[files.pp_fp_dark],
            recipe_kind='extract-fpd')
eng_seq.add(apero_extract, name='EXT_LFCFP', files=[files.pp_lfc_fp],
            recipe_kind='extract-lfcfp')
eng_seq.add(apero_extract, name='EXT_FPLFC', files=[files.pp_fp_lfc],
            recipe_kind='extract-fplfc')

# -----------------------------------------------------------------------------
# sequences list
# -----------------------------------------------------------------------------
sequences = [pp_seq, pp_seq_opt, full_seq, limited_seq, master_seq, calib_seq,
             tellu_seq, science_seq, quick_seq, blank_seq, eng_seq]
