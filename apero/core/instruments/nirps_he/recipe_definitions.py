#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO Recipe definitions for NIRPS HE

Created on 2020-10-31 at 18:06

@author: cook
"""
from apero import lang
from apero.base import base
from apero.core.core import drs_base_classes as base_class
from apero.core.instruments.default import recipe_definitions as rd
from apero.core.instruments.default import grouping
from apero.core.instruments.nirps_he import file_definitions as files
from apero.core.utils import drs_recipe

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'core.instruments.nirps_he.recipe_definitions.py'
__INSTRUMENT__ = 'NIRPS_HE'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Define instrument alias
INSTRUMENT_ALIAS = 'nirps_he'
# Get Help
textentry = lang.textentry
# import file definitions in import module class
sf = base_class.ImportModule('nirps_he.file_definitions',
                             'apero.core.instruments.nirps_he.file_definitions',
                             mod=files)

# =============================================================================
# Commonly used arguments
# =============================================================================
obs_dir = rd.obs_dir
# -----------------------------------------------------------------------------
plot = rd.plot

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
             options=['ALL', 'A', 'B'],
             default_ref='INPUT_FLIP_IMAGE')
# -----------------------------------------------------------------------------
flipimage = dict(name='--flipimage', dtype='options', default='both',
                 helpstr=textentry('FLIPIMAGE_HELP'),
                 options=['None', 'x', 'y', 'both'])
# -----------------------------------------------------------------------------
fluxunits = dict(name='--fluxunits', dtype='options', default='e-',
                 helpstr=textentry('FLUXUNITS_HELP'), options=['ADU/s', 'e-'])
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
# -----------------------------------------------------------------------------
no_in_qc = dict(name='--no_in_qc', dtype='switch', default=False,
                helpstr='Disable checking the quality control of input files')

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
                files=[files.out_dark_ref],
                helpstr=textentry('DARKFILE_HELP'))
# -----------------------------------------------------------------------------
flatfile = dict(name='--flatfile', dtype='file', default='None',
                files=[files.out_ff_flat], helpstr=textentry('FLATFILE_HELP'))
# -----------------------------------------------------------------------------
fpref = dict(name='--fpref', dtype='file', default='None',
             files=[files.out_shape_fpref], path='red',
             helpstr=textentry('FPREFFILE_HELP'))
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
wavefile = dict(name='--wavefile', dtype='file', default='None',
                files=[files.out_wavem_sol, files.out_wave_night,
                       files.out_wave_default_ref],
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
# apero_pp_ref
# -----------------------------------------------------------------------------
apero_pp_ref = DrsRecipe(__INSTRUMENT__)
apero_pp_ref.name = 'apero_pp_ref_{0}.py'.format(INSTRUMENT_ALIAS)
apero_pp_ref.shortname = 'PPREF'
apero_pp_ref.instrument = __INSTRUMENT__
apero_pp_ref.in_block_str = 'raw'
apero_pp_ref.out_block_str = 'red'
apero_pp_ref.extension = 'fits'
apero_pp_ref.reference = True
apero_pp_ref.description = textentry('PP_REF_DESC')
apero_pp_ref.epilog = textentry('PP_REF_EXAMPLE')
apero_pp_ref.recipe_type = 'recipe'
apero_pp_ref.recipe_kind = 'pre-reference'
apero_pp_ref.set_outputs(PP_REF=files.out_pp_ref,
                         PP_LED_FLAT=files.out_pp_led_flat)
apero_pp_ref.set_arg(pos=0, **obs_dir)
apero_pp_ref.set_kwarg(name='--filetype', dtype=str, default='FLAT_FLAT',
                       helpstr=textentry('PP_REF_FILETYPE_HELP'))
apero_pp_ref.group_func = grouping.no_group
apero_pp_ref.group_column = None
# add to recipe
recipes.append(apero_pp_ref)

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
apero_preprocess.set_flags(OBJ=False, QCPASSED=False)
apero_preprocess.set_arg(pos=0, **obs_dir)
apero_preprocess.set_arg(name='files', dtype='files', pos='1+',
                         files=[files.raw_file],
                         helpstr=textentry('PREPROCESS_UFILES_HELP'), limit=1)
apero_preprocess.set_kwarg(name='--skip', dtype='bool', default=False,
                           helpstr=textentry('PPSKIP_HELP'),
                           default_ref='SKIP_DONE_PP')
apero_preprocess.group_func = grouping.group_individually
apero_preprocess.group_column = 'REPROCESS_OBSDIR_COL'
# documentation
apero_preprocess.schematic = 'apero_preproces_spirou_schematic.jpg'
apero_preprocess.description_file = 'apero_preprocess_spirou.rst'
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
apero_badpix.calib_required = True
apero_badpix.set_outputs(BADPIX=files.out_badpix, BACKMAP=files.out_backmap)
apero_badpix.set_debug_plots('BADPIX_MAP')
apero_badpix.set_summary_plots('SUM_BADPIX_MAP')
apero_badpix.set_arg(pos=0, **obs_dir)
apero_badpix.set_kwarg(name='--flatfiles', dtype='files',
                       files=[files.pp_flat_flat],
                       filelogic='exclusive', required=True,
                       helpstr=textentry('BADPIX_FLATFILE_HELP'), default=[])
apero_badpix.set_kwarg(name='--darkfiles', dtype='files',
                       files=[files.pp_dark_dark],
                       filelogic='inclusive', required=True,
                       helpstr=textentry('BADPIX_DARKFILE_HELP'), default=[])
apero_badpix.set_kwarg(**add_db)
apero_badpix.set_kwarg(default=True, **combine)
apero_badpix.set_kwarg(**flipimage)
apero_badpix.set_kwarg(**fluxunits)
apero_badpix.set_kwarg(**plot)
apero_badpix.set_kwarg(**resize)
apero_badpix.set_kwarg(**no_in_qc)
apero_badpix.set_min_nfiles('flatfiles', 1)
apero_badpix.set_min_nfiles('darkfiles', 1)
apero_badpix.group_func = grouping.group_by_dirname
apero_badpix.group_column = 'REPROCESS_OBSDIR_COL'
# documentation
apero_badpix.schematic = 'apero_badpix_spirou_schematic.jpg'
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
apero_dark.calib_required = False
apero_dark.set_outputs(DARK_INT_FILE=files.out_dark,
                       DARK_TEL_FIEL=files.out_dark)
apero_dark.set_debug_plots('DARK_IMAGE_REGIONS', 'DARK_HISTOGRAM')
apero_dark.set_summary_plots('SUM_DARK_IMAGE_REGIONS', 'SUM_DARK_HISTOGRAM')
apero_dark.set_arg(pos=0, **obs_dir)
apero_dark.set_arg(name='files', dtype='files',
                   files=[files.pp_dark_dark],
                   pos='1+', filelogic='exclusive',
                   helpstr=textentry('FILES_HELP') + textentry('DARK_FILES_HELP'))
apero_dark.set_kwarg(**add_db)
apero_dark.set_kwarg(default=True, **combine)
apero_dark.set_kwarg(**plot)
apero_dark.set_kwarg(**no_in_qc)
apero_dark.set_min_nfiles('files', 2)
apero_dark.group_func = grouping.group_by_dirname
apero_dark.group_column = 'REPROCESS_OBSDIR_COL'
# add to recipe
recipes.append(apero_dark)

# -----------------------------------------------------------------------------
# apero_dark_ref
# -----------------------------------------------------------------------------
apero_dark_ref = DrsRecipe(__INSTRUMENT__)
apero_dark_ref.name = 'apero_dark_ref_{0}.py'.format(INSTRUMENT_ALIAS)
apero_dark_ref.shortname = 'DARKREF'
apero_dark_ref.reference = True
apero_dark_ref.instrument = __INSTRUMENT__
apero_dark_ref.in_block_str = 'tmp'
apero_dark_ref.out_block_str = 'red'
apero_dark_ref.extension = 'fits'
apero_dark_ref.description = textentry('DARK_REF_DESC')
apero_dark_ref.epilog = textentry('DARK_REF_EXAMPLE')
apero_dark_ref.recipe_type = 'recipe'
apero_dark_ref.recipe_kind = 'calib-reference'
apero_dark_ref.calib_required = True
apero_dark_ref.set_outputs(DARK_REF_FILE=files.out_dark_ref)
apero_dark_ref.set_kwarg(name='--filetype', dtype=str,
                         default='DARK_DARK',
                         helpstr=textentry('DARK_REF_FILETYPE'))
apero_dark_ref.set_kwarg(**add_db)
apero_dark_ref.set_kwarg(**plot)
apero_dark_ref.set_kwarg(**no_in_qc)
apero_dark_ref.group_func = grouping.no_group
apero_dark_ref.group_column = None
# documentation
apero_dark_ref.schematic = 'apero_dark_ref_spirou_schematic.jpg'
# add to recipe
recipes.append(apero_dark_ref)

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
apero_loc.calib_required = True
apero_loc.set_outputs(ORDERP_FILE=files.out_loc_orderp,
                      LOCO_FILE=files.out_loc_loco,
                      FWHM_FILE=files.out_loc_fwhm,
                      SUP_FILE=files.out_loc_sup,
                      DEBUG_BACK=files.debug_back)
apero_loc.set_flags(SCIFIBER=False, REFFIBER=False)
apero_loc.set_debug_plots('LOC_WIDTH_REGIONS', 'LOC_FIBER_DOUBLET_PARITY',
                          'LOC_GAP_ORDERS', 'LOC_IMAGE_FIT', 'LOC_IM_CORNER',
                          'LOC_IM_REGIONS')
apero_loc.set_summary_plots('SUM_LOC_IM_FIT', 'SUM_LOC_IM_CORNER')
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
apero_loc.set_min_nfiles('files', 1)
apero_loc.group_func = grouping.group_by_dirname
apero_loc.group_column = 'REPROCESS_OBSDIR_COL'
# documentation
apero_loc.schematic = 'apero_loc_spirou_schematic.jpg'
# add to recipe
recipes.append(apero_loc)

# -----------------------------------------------------------------------------
# apero_shape_ref
# -----------------------------------------------------------------------------
apero_shape_ref = DrsRecipe(__INSTRUMENT__)
apero_shape_ref.name = 'apero_shape_ref_{0}.py'.format(INSTRUMENT_ALIAS)
apero_shape_ref.shortname = 'SHAPEREF'
apero_shape_ref.reference = True
apero_shape_ref.instrument = __INSTRUMENT__
apero_shape_ref.in_block_str = 'tmp'
apero_shape_ref.out_block_str = 'red'
apero_shape_ref.extension = 'fits'
apero_shape_ref.description = textentry('SHAPE_DESC')
apero_shape_ref.epilog = textentry('SHAPEREF_EXAMPLE')
apero_shape_ref.recipe_type = 'recipe'
apero_shape_ref.recipe_kind = 'calib-reference'
apero_shape_ref.calib_required = True
apero_shape_ref.set_outputs(FPREF_FILE=files.out_shape_fpref,
                            DXMAP_FILE=files.out_shape_dxmap,
                            DYMAP_FILE=files.out_shape_dymap,
                            SHAPE_IN_FP_FILE=files.out_shape_debug_ifp,
                            SHAPE_OUT_FP_FILE=files.out_shape_debug_ofp,
                            SHAPE_BDXMAP_FILE=files.out_shape_debug_bdx,
                            DEBUG_BACK=files.debug_back)
apero_shape_ref.set_debug_plots('SHAPE_DX', 'SHAPE_ANGLE_OFFSET_ALL',
                                'SHAPE_ANGLE_OFFSET', 'SHAPE_LINEAR_TPARAMS')
apero_shape_ref.set_summary_plots('SUM_SHAPE_ANGLE_OFFSET')
apero_shape_ref.set_arg(pos=0, **obs_dir)
apero_shape_ref.set_kwarg(name='--fpfiles', dtype='files',
                          files=[files.pp_fp_fp],
                          filelogic='exclusive', required=True,
                          helpstr=textentry('SHAPE_FPFILES_HELP'), default=[])
# apero_shape_ref.set_kwarg(name='--hcfiles', dtype='files',
#                              files=[files.pp_hc1_hc1],
#                              filelogic='exclusive', required=True,
#                              helpstr=textentry('SHAPE_HCFILES_HELP'), default=[])
apero_shape_ref.set_kwarg(**add_db)
apero_shape_ref.set_kwarg(**badfile)
apero_shape_ref.set_kwarg(**dobad)
apero_shape_ref.set_kwarg(**backsub)
apero_shape_ref.set_kwarg(default=True, **combine)
apero_shape_ref.set_kwarg(**darkfile)
apero_shape_ref.set_kwarg(**dodark)
apero_shape_ref.set_kwarg(**flipimage)
apero_shape_ref.set_kwarg(**fluxunits)
apero_shape_ref.set_kwarg(**locofile)
apero_shape_ref.set_kwarg(**plot)
apero_shape_ref.set_kwarg(**resize)
apero_shape_ref.set_kwarg(**no_in_qc)
apero_shape_ref.set_min_nfiles('fpfiles', 1)
apero_shape_ref.set_min_nfiles('hcfiles', 1)
apero_shape_ref.set_kwarg(**fpref)
apero_shape_ref.group_func = grouping.group_by_dirname
apero_shape_ref.group_column = 'REPROCESS_OBSDIR_COL'
# documentation
apero_shape_ref.schematic = 'apero_shape_ref_spirou_schematic.jpg'
# add to recipe
recipes.append(apero_shape_ref)

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
apero_shape.calib_required = True
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
apero_shape.set_kwarg(**fpref)
apero_shape.set_kwarg(**plot)
apero_shape.set_kwarg(**resize)
apero_shape.set_kwarg(**shapexfile)
apero_shape.set_kwarg(**shapeyfile)
apero_shape.set_kwarg(**no_in_qc)
apero_shape.set_min_nfiles('fpfiles', 1)
apero_shape.set_min_nfiles('hcfiles', 1)
apero_shape.group_func = grouping.group_by_dirname
apero_shape.group_column = 'REPROCESS_OBSDIR_COL'
# documentation
apero_shape.schematic = 'apero_shape_spirou_schematic.jpg'
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
apero_flat.calib_required = True
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
apero_flat.set_kwarg(**no_in_qc)
apero_flat.set_min_nfiles('files', 1)
apero_flat.group_func = grouping.group_by_dirname
apero_flat.group_column = 'REPROCESS_OBSDIR_COL'
# documentation
apero_flat.schematic = 'apero_flat_spirou_schematic.jpg'
# add to recipe
recipes.append(apero_flat)

# -----------------------------------------------------------------------------
# apero_leak_ref
# -----------------------------------------------------------------------------
apero_leak_ref = DrsRecipe(__INSTRUMENT__)
apero_leak_ref.name = 'apero_leak_ref_{0}.py'.format(INSTRUMENT_ALIAS)
apero_leak_ref.shortname = 'LEAKREF'
apero_leak_ref.reference = True
apero_leak_ref.instrument = __INSTRUMENT__
apero_leak_ref.in_block_str = 'tmp'
apero_leak_ref.out_block_str = 'red'
apero_leak_ref.extension = 'fits'
apero_leak_ref.description = textentry('LEAKREF_DESC')
apero_leak_ref.epilog = textentry('LEAKREF_EXAMPLE')
apero_leak_ref.recipe_type = 'recipe'
apero_leak_ref.recipe_kind = 'calib-reference'
apero_leak_ref.calib_required = False
apero_leak_ref.set_outputs(LEAK_E2DS_FILE=files.out_ext_e2ds,
                           LEAK_REF=files.out_leak_ref)
apero_leak_ref.set_flags(INT_EXT=True, EXT_FOUND=False)
apero_leak_ref.set_arg(pos=0, **obs_dir)
apero_leak_ref.set_kwarg(name='--filetype', dtype=str, default='DARK_FP',
                         helpstr=textentry('LEAKREF_HELP_FILETYPE'))
apero_leak_ref.set_kwarg(**add_db)
apero_leak_ref.set_kwarg(**plot)
apero_leak_ref.set_kwarg(**no_in_qc)
apero_leak_ref.group_func = grouping.no_group
apero_leak_ref.group_column = None
# add to recipe
recipes.append(apero_leak_ref)

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
apero_extract.set_flags(QUICKLOOK=False, EXP_FPLINE=False)
apero_extract.set_debug_plots('FLAT_ORDER_FIT_EDGES1', 'FLAT_ORDER_FIT_EDGES2',
                              'FLAT_BLAZE_ORDER1', 'FLAT_BLAZE_ORDER2',
                              'THERMAL_BACKGROUND', 'EXTRACT_SPECTRAL_ORDER1',
                              'EXTRACT_SPECTRAL_ORDER2', 'EXTRACT_S1D',
                              'EXTRACT_S1D_WEIGHT', 'WAVEREF_EXPECTED')
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
apero_extract.set_kwarg(name='--combine_method', dtype=str,
                        options=['sum', 'median', 'mean', 'subtract', 'divide',
                                 'multiply'], default='sum',
                        helpstr='Method to combine files (if --combine=True)')
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
apero_extract.set_kwarg(name='--leakcorr', dtype='bool', default=True,
                        helpstr=textentry('LEAKCORR_HELP'),
                        default_ref='CORRECT_LEAKAGE')
apero_extract.set_kwarg(**wavefile)
apero_extract.set_kwarg(name='--force_ref_wave', dtype='bool',
                        default=False,
                        helpstr='Force using the reference wave solution')
apero_extract.set_kwarg(**no_in_qc)
apero_extract.group_func = grouping.group_individually
apero_extract.group_column = 'REPROCESS_OBSDIR_COL'
# add to recipe
recipes.append(apero_extract)

# -----------------------------------------------------------------------------
# apero_wave_ref
# -----------------------------------------------------------------------------
apero_wave_ref = DrsRecipe(__INSTRUMENT__)
apero_wave_ref.name = 'apero_wave_ref_{0}.py'.format(INSTRUMENT_ALIAS)
apero_wave_ref.shortname = 'WAVEREF'
apero_wave_ref.reference = True
apero_wave_ref.instrument = __INSTRUMENT__
apero_wave_ref.in_block_str = 'tmp'
apero_wave_ref.out_block_str = 'red'
apero_wave_ref.extension = 'fits'
apero_wave_ref.description = textentry('WAVE_DESC')
apero_wave_ref.epilog = textentry('WAVE_EXAMPLE')
apero_wave_ref.recipe_type = 'recipe'
apero_wave_ref.recipe_kind = 'calib-reference'
apero_wave_ref.calib_required = True
apero_wave_ref.set_outputs(WAVE_E2DS=files.out_ext_e2dsff,
                           WAVESOL_REF=files.out_wavem_sol,
                           WAVEREF_CAVITY=files.out_waveref_cavity,
                           WAVEM_HCLIST=files.out_wave_hclist_ref,
                           WAVEM_FPLIST=files.out_wave_fplist_ref,
                           WAVEM_RES=files.out_wavem_res,
                           WAVEM_RES_E2DS=files.out_wavem_res_e2ds,
                           CCF_RV=files.out_ccf_fits)
apero_wave_ref.set_flags(INT_EXT=True, EXT_FOUND=False)
apero_wave_ref.set_debug_plots('WAVE_WL_CAV', 'WAVE_FIBER_COMPARISON',
                               'WAVE_FIBER_COMP', 'WAVE_HC_DIFF_HIST',
                               'WAVEREF_EXPECTED', 'EXTRACT_S1D',
                               'EXTRACT_S1D_WEIGHT', 'WAVE_RESMAP',
                               'CCF_RV_FIT', 'CCF_RV_FIT_LOOP')
apero_wave_ref.set_summary_plots('SUM_WAVE_FIBER_COMP', 'SUM_CCF_RV_FIT')
apero_wave_ref.set_arg(pos=0, **obs_dir)
apero_wave_ref.set_kwarg(name='--hcfiles', dtype='files',
                         files=[files.pp_hc1_hc1],
                         filelogic='exclusive', required=True,
                         helpstr=textentry('WAVE_HCFILES_HELP'), default=[])
apero_wave_ref.set_kwarg(name='--fpfiles', dtype='files',
                         files=[files.pp_fp_fp],
                         filelogic='exclusive', required=True,
                         helpstr=textentry('WAVE_FPFILES_HELP'), default=[])
apero_wave_ref.set_kwarg(**add_db)
apero_wave_ref.set_kwarg(**badfile)
apero_wave_ref.set_kwarg(**dobad)
apero_wave_ref.set_kwarg(**backsub)
apero_wave_ref.set_kwarg(**blazefile)
apero_wave_ref.set_kwarg(default=True, **combine)
apero_wave_ref.set_kwarg(**darkfile)
apero_wave_ref.set_kwarg(**dodark)
apero_wave_ref.set_kwarg(**fiber)
apero_wave_ref.set_kwarg(**flipimage)
apero_wave_ref.set_kwarg(**fluxunits)
apero_wave_ref.set_kwarg(**locofile)
apero_wave_ref.set_kwarg(**orderpfile)
apero_wave_ref.set_kwarg(**plot)
apero_wave_ref.set_kwarg(**resize)
apero_wave_ref.set_kwarg(**shapexfile)
apero_wave_ref.set_kwarg(**shapeyfile)
apero_wave_ref.set_kwarg(**shapelfile)
apero_wave_ref.set_kwarg(**wavefile)
apero_wave_ref.set_min_nfiles('fpfiles', 1)
apero_wave_ref.set_min_nfiles('hcfiles', 1)
apero_wave_ref.set_kwarg(name='--forceext', dtype='bool',
                         default_ref='WAVE_ALWAYS_EXTRACT',
                         helpstr='WAVE_EXTRACT_HELP')
apero_wave_ref.set_kwarg(name='--cavityfile', dtype='file', default='None',
                         files=[files.out_waveref_cavity],
                         helpstr=textentry('WAVEREF_CAVFILE_HELP'))
apero_wave_ref.set_kwarg(**no_in_qc)
apero_wave_ref.group_func = grouping.group_by_dirname
apero_wave_ref.group_column = 'REPROCESS_OBSDIR_COL'
# documentation
apero_wave_ref.schematic = 'apero_wave_ref_spirou_schematic.jpg'
# add to recipe
recipes.append(apero_wave_ref)

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
apero_wave_night.calib_required = True
apero_wave_night.set_outputs(WAVE_E2DS=files.out_ext_e2dsff,
                             WAVEMAP_NIGHT=files.out_wave_night,
                             WAVE_HCLIST=files.out_wave_hclist,
                             WAVE_FPLIST=files.out_wave_fplist,
                             CCF_RV=files.out_ccf_fits)
apero_wave_night.set_flags(INT_EXT=True, EXT_FOUND=False)
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
apero_wave_night.set_min_nfiles('fpfiles', 1)
apero_wave_night.set_min_nfiles('hcfiles', 1)
apero_wave_night.set_kwarg(name='--forceext', dtype='bool',
                           default_ref='WAVE_ALWAYS_EXTRACT',
                           helpstr='WAVE_EXTRACT_HELP')
apero_wave_night.set_kwarg(**no_in_qc)
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
apero_ccf.set_kwarg(name='--masknormmode', dtype='options',
                    default_ref='CCF_MASK_NORMALIZATION',
                    options=['None', 'all', 'order'],
                    helpstr=textentry('CCF_MASK_NORM_HELP'))
apero_ccf.set_kwarg(**add_db)
apero_ccf.set_kwarg(**blazefile)
apero_ccf.set_kwarg(**plot)
apero_ccf.set_kwarg(**no_in_qc)
apero_ccf.group_func = grouping.group_individually
apero_ccf.group_column = 'REPROCESS_OBSDIR_COL'
# add to recipe
recipes.append(apero_ccf)


# -----------------------------------------------------------------------------
# apero_mk_skymodel
# -----------------------------------------------------------------------------
apero_mk_skymodel = DrsRecipe(__INSTRUMENT__)
apero_mk_skymodel.name = 'apero_mk_skymodel_{0}.py'.format(INSTRUMENT_ALIAS)
apero_mk_skymodel.shortname = 'MKSKY'
apero_mk_skymodel.instrument = __INSTRUMENT__
apero_mk_skymodel.in_block_str = 'red'
apero_mk_skymodel.out_block_str = 'red'
apero_mk_skymodel.extension = 'fits'
apero_mk_skymodel.description = textentry('MKSKY_DESC')
apero_mk_skymodel.epilog = textentry('MKSKY_EXAMPLE')
apero_mk_skymodel.recipe_type = 'recipe'
apero_mk_skymodel.recipe_kind = 'tellu-sky'
apero_mk_skymodel.set_outputs(SKYMODEL=files.out_sky_model)
apero_mk_skymodel.set_debug_plots('TELLU_SKYMODEL_REGION_PLOT',
                                  'TELLU_SKYMODEL_MED',
                                  'TELLU_SKYMODEL_LINEFIT')
apero_mk_skymodel.group_func = grouping.no_group
apero_mk_skymodel.group_column = None
# add to recipe
recipes.append(apero_mk_skymodel)

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
                           TELLU_SCLEAN=files.out_tellu_sclean,
                           TELLU_PCLEAN=files.out_tellu_pclean)
apero_mk_tellu.set_debug_plots('TELLU_SKY_CORR_PLOT',
                               'MKTELLU_WAVE_FLUX1', 'MKTELLU_WAVE_FLUX2',
                               'TELLUP_WAVE_TRANS', 'TELLUP_ABSO_SPEC',
                               'TELLUP_CLEAN_OH', 'FTELLU_RECON_SPLINE2',
                               'TELLU_FINITE_RES_CORR')
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
apero_mk_tellu.set_kwarg(name='--finiteres', dtype='bool',
                         default_ref='TELLUP_DO_FINITE_RES_CORR',
                         helpstr='Whether to do the finite resolution '
                                 'correction (Always false if no template)')
apero_mk_tellu.set_kwarg(**no_in_qc)
apero_mk_tellu.group_func = grouping.group_individually
apero_mk_tellu.group_column = 'REPROCESS_OBSDIR_COL'
# add to recipe
recipes.append(apero_mk_tellu)

# -----------------------------------------------------------------------------
# apero_mk_model
# -----------------------------------------------------------------------------
apero_mk_model = DrsRecipe(__INSTRUMENT__)
apero_mk_model.name = 'apero_mk_model_{0}.py'.format(INSTRUMENT_ALIAS)
apero_mk_model.shortname = 'MKMODEL'
apero_mk_model.instrument = __INSTRUMENT__
apero_mk_model.in_block_str = 'red'
apero_mk_model.out_block_str = 'red'
apero_mk_model.extension = 'fits'
apero_mk_model.description = textentry('MKTELL_DESC')
apero_mk_model.epilog = textentry('MKTELL_EXAMPLE')
apero_mk_model.recipe_type = 'recipe'
apero_mk_model.recipe_kind = 'tellu-hotstar'
apero_mk_model.set_outputs(TRANS_MODEL=files.out_tellu_model)
apero_mk_model.set_debug_plots('MKTELLU_MODEL')
apero_mk_model.set_summary_plots('SUM_MKTELLU_MODEL')
apero_mk_model.set_kwarg(**add_db)
apero_mk_model.set_kwarg(**plot)
apero_mk_model.set_kwarg(**no_in_qc)
apero_mk_model.group_func = grouping.no_group
apero_mk_model.group_column = None
# add to recipe
recipes.append(apero_mk_model)

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
                            TELLU_SCLEAN=files.out_tellu_sclean,
                            TELLU_PCLEAN=files.out_tellu_pclean)
apero_fit_tellu.set_debug_plots('TELLU_SKY_CORR_PLOT',
                                'EXTRACT_S1D', 'EXTRACT_S1D_WEIGHT',
                                'FTELLU_PCA_COMP1', 'FTELLU_PCA_COMP2',
                                'FTELLU_RECON_SPLINE1', 'FTELLU_RECON_SPLINE2',
                                'FTELLU_WAVE_SHIFT1', 'FTELLU_WAVE_SHIFT2',
                                'FTELLU_RECON_ABSO1', 'FTELLU_RECON_ABSO2',
                                'TELLUP_WAVE_TRANS', 'TELLUP_ABSO_SPEC',
                                'TELLUP_CLEAN_OH', 'FTELLU_RES_MODEL',
                                'TELLU_FINITE_RES_CORR')
apero_fit_tellu.set_summary_plots('SUM_EXTRACT_S1D', 'SUM_FTELLU_RECON_ABSO',
                                  'SUM_TELLUP_WAVE_TRANS',
                                  'SUM_TELLUP_ABSO_SPEC',
                                  'SUM_FTELLU_RES_MODEL')
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
apero_fit_tellu.set_kwarg(name='--finiteres', dtype='bool',
                          default_ref='TELLUP_DO_FINITE_RES_CORR',
                          helpstr='Whether to do the finite resolution '
                                 'correction (Always false if no template)')
apero_fit_tellu.set_kwarg(name='--onlypreclean', dtype='switch', default=False,
                          helpstr='Only run the precleaning steps '
                                  '(not recommended - for debugging ONLY)')
apero_fit_tellu.set_kwarg(**add_db)
apero_fit_tellu.set_kwarg(**blazefile)
apero_fit_tellu.set_kwarg(**plot)
apero_fit_tellu.set_kwarg(**wavefile)
apero_fit_tellu.set_kwarg(**no_in_qc)
apero_fit_tellu.group_func = grouping.group_individually
apero_fit_tellu.group_column = 'REPROCESS_OBSDIR_COL'
# add to recipe
recipes.append(apero_fit_tellu)

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
                              TELLU_TEMP_S1DV=files.out_tellu_s1dv_template,
                              TELLU_TEMP_S1DW=files.out_tellu_s1dw_template,
                              TELLU_BIGCUBE_S1D=files.out_tellu_s1d_bigcube)
apero_mk_template.set_debug_plots('EXTRACT_S1D', 'MKTEMP_BERV_COV',
                                  'MKTEMP_S1D_DECONV')
apero_mk_template.set_summary_plots('SUM_EXTRACT_S1D', 'SUM_MKTEMP_BERV_COV')
apero_mk_template.set_arg(name='objname', pos=0, dtype=str,
                          helpstr=textentry('MKTEMP_OBJNAME_HELP'))
apero_mk_template.set_kwarg(name='--filetype', dtype='options',
                            default_ref='MKTEMPLATE_FILETYPE',
                            helpstr=textentry('MKTEMP_FILETYPE'),
                            options=['EXT_E2DS', 'EXT_E2DS_FF'])
apero_mk_template.set_kwarg(name='--fiber', dtype='options',
                            default_ref='MKTEMPLATE_FIBER_TYPE',
                            helpstr=textentry('MKTEMP_FIBER'),
                            options=['A', 'B'])
apero_mk_template.set_kwarg(**add_db)
apero_mk_template.set_kwarg(**blazefile)
apero_mk_template.set_kwarg(**plot)
apero_mk_template.set_kwarg(**wavefile)
apero_mk_template.set_kwarg(**no_in_qc)
apero_mk_template.group_func = grouping.no_group
apero_mk_template.group_column = None
# add to recipe
recipes.append(apero_mk_template)

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
apero_postprocess.set_kwarg(name='--skip', dtype='switch',
                            default_ref='POST_OVERWRITE',
                            helpstr=textentry('OUT_OVERWRITE_HELP'))
apero_postprocess.set_kwarg(name='--clear', dtype='switch',
                            default_ref='POST_CLEAR_REDUCED',
                            helpstr=textentry('OUT_CLEAR_HELP'))
apero_postprocess.set_kwarg(**no_in_qc)
apero_postprocess.group_func = grouping.group_individually
apero_postprocess.group_column = 'REPROCESS_OBSDIR_COL'
# add to recipe
recipes.append(apero_postprocess)

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
#           - whether a file is in the reference sequence (use reference obs dir only
#             in cases where normally a recipe would use any night)
#           - any header keyword reference (value must be set in run file)
#             i.e. those starting with "KW_"
#       i.e.
#
#       run.add(recipe, name='CUSTOM_RECIPE', reference=True,
#               files=[files.file_defintion], KW_HEADER='RUN_FILE_VARIABLE')
#
#
#   Example:
#           # the below example creates a run called 'run'
#           # it just extracts OBJ_FP files with OBJECT NAME listed in
#           #  'SCIENCE_TARGETS' in the runfile
#           # note as reference=True it will only extract from the reference obs dir
#
#           run = drs_recipe.DrsRunSequence('run', __INSTRUMENT__)
#           run.add(apero_extract, reference=True, files=[files.pp_obj_fp],
#                   KW_OBJNAME='SCIENCE_TARGETS')
#
#
#  Note: must add sequences to sequences list to be able to use!
#
sci_fiber = 'A'
cal_fiber = 'B'
# -----------------------------------------------------------------------------
# full seqeunce (reference + nights)
# -----------------------------------------------------------------------------
full_seq = drs_recipe.DrsRunSequence('full_seq', __INSTRUMENT__)
# define schematic file and description file
full_seq.schematic = 'full_seq.jpg'
full_seq.description_file = None
# reference run
full_seq.add(apero_pp_ref, recipe_kind='pre-reference',
             arguments=dict(obs_dir='RUN_OBS_DIR'))
full_seq.add(apero_preprocess, recipe_kind='pre-all')
full_seq.add(apero_dark_ref, ref=True)
full_seq.add(apero_badpix, name='BADREF', ref=True,
             recipe_kind='calib-reference')
full_seq.add(apero_loc, name='LOCREFCAL', files=[files.pp_dark_flat], ref=True,
             recipe_kind='calib-reference-CAL')
full_seq.add(apero_loc, name='LOCREFSCI', files=[files.pp_flat_dark], ref=True,
             recipe_kind='calib-reference-SCI')
full_seq.add(apero_shape_ref, ref=True)
full_seq.add(apero_shape, name='SHAPELREF', ref=True,
             recipe_kind='calib-reference')
full_seq.add(apero_flat, name='FLATREF', ref=True,
             recipe_kind='calib-reference')
full_seq.add(apero_leak_ref, ref=True)
full_seq.add(apero_wave_ref, ref=True,
             rkwargs=dict(hcfiles=[files.pp_hc1_hc1],
                          fpfiles=[files.pp_fp_fp]))
# night runs
full_seq.add(apero_badpix)
full_seq.add(apero_loc, files=[files.pp_dark_flat], name='LOCCAL',
             recipe_kind='calib-night-CAL')
full_seq.add(apero_loc, files=[files.pp_flat_dark], name='LOCSCI',
             recipe_kind='calib-night-SCI')
full_seq.add(apero_shape)
full_seq.add(apero_flat, files=[files.pp_flat_flat])
full_seq.add(apero_wave_night)
# extract all science OBJECTS
full_seq.add(apero_extract, name='EXTALL', recipe_kind='extract-ALL',
             files=files.science_pp)
# telluric recipes
full_seq.add(apero_mk_tellu, name='MKTELLU1', recipe_kind='tellu-hotstar',
             files=[files.out_ext_e2dsff], fiber=sci_fiber,
             filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
                          KW_DPRTYPE=files.science_dprtypes))
full_seq.add(apero_mk_model, name='MKTMOD1', recipe_kind='tellu-hotstar')
full_seq.add(apero_fit_tellu, name='MKTFIT1', recipe_kind='tellu-hotstar',
             files=[files.out_ext_e2dsff], fiber=sci_fiber,
             filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
                          KW_DPRTYPE=files.science_dprtypes))
full_seq.add(apero_mk_template, name='MKTEMP1',
             fiber=sci_fiber, template_required=True,
             recipe_kind='tellu-hotstar',
             arguments=dict(objname='TELLURIC_TARGETS'),
             filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
                          KW_DPRTYPE=files.science_dprtypes))
full_seq.add(apero_mk_tellu, name='MKTELLU2', files=[files.out_ext_e2dsff],
             fiber=sci_fiber, template_required=True,
             recipe_kind='tellu-hotstar',
             filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
                          KW_DPRTYPE=files.science_dprtypes))
full_seq.add(apero_mk_model, name='MKTMOD2', recipe_kind='tellu-hotstar')
full_seq.add(apero_fit_tellu, name='MKTFIT2', recipe_kind='tellu-hotstar',
             files=[files.out_ext_e2dsff], fiber=sci_fiber,
             template_required=True,
             filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
                          KW_DPRTYPE=files.science_dprtypes))
full_seq.add(apero_mk_template, name='MKTEMP2',
             fiber=sci_fiber, template_required=True,
             recipe_kind='tellu-hotstar',
             arguments=dict(objname='TELLURIC_TARGETS'),
             filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
                          KW_DPRTYPE=files.science_dprtypes))

full_seq.add(apero_fit_tellu, name='FTFIT1', recipe_kind='tellu-science',
             files=[files.out_ext_e2dsff], fiber=sci_fiber,
             filters=dict(KW_OBJNAME='SCIENCE_TARGETS',
                          KW_DPRTYPE=files.science_dprtypes))
full_seq.add(apero_mk_template, name='FTTEMP1', fiber=sci_fiber,
             arguments=dict(objname='SCIENCE_TARGETS'),
             filters=dict(KW_OBJNAME='SCIENCE_TARGETS',
                          KW_DPRTYPE=files.science_dprtypes),
             template_required=True, recipe_kind='tellu-science')
full_seq.add(apero_fit_tellu, name='FTFIT2',
             files=[files.out_ext_e2dsff], fiber=sci_fiber,
             filters=dict(KW_OBJNAME='SCIENCE_TARGETS',
                          KW_DPRTYPE=files.science_dprtypes),
             template_required=True, recipe_kind='tellu-science')
full_seq.add(apero_mk_template, name='FTTEMP2', fiber=sci_fiber,
             arguments=dict(objname='SCIENCE_TARGETS'),
             filters=dict(KW_OBJNAME='SCIENCE_TARGETS',
                          KW_DPRTYPE=files.science_dprtypes),
             template_required=True, recipe_kind='tellu-science')
# ccf on all OBJ_DARK / OBJ_FP
full_seq.add(apero_ccf, files=[files.out_tellu_obj], fiber=sci_fiber,
             filters=dict(KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP', 'POLAR_FP',
                                      'POLAR_DARK']),
             recipe_kind='rv-tcorr')

# post processing
full_seq.add(apero_postprocess, name='POSTALL', files=[files.pp_file],
             recipe_kind='post-all',
             filters=dict(KW_DPRTYPE=['OBJ_FP', 'OBJ_DARK', 'POLAR_FP',
                                      'POLAR_DARK']))

# -----------------------------------------------------------------------------
# limited sequence (reference + nights)
# -----------------------------------------------------------------------------
limited_seq = drs_recipe.DrsRunSequence('limited_seq', __INSTRUMENT__)
# define schematic file and description file
limited_seq.schematic = 'limited_seq.jpg'
limited_seq.description_file = None
# reference run
limited_seq.add(apero_pp_ref, recipe_kind='pre-reference',
                arguments=dict(obs_dir='RUN_OBS_DIR'))
limited_seq.add(apero_preprocess, recipe_kind='pre-all')
limited_seq.add(apero_dark_ref, ref=True)
limited_seq.add(apero_badpix, name='BADREF', ref=True,
                recipe_kind='calib-reference')
limited_seq.add(apero_loc, name='LOCREFCAL', files=[files.pp_dark_flat],
                ref=True, recipe_kind='calib-reference-CAL')
limited_seq.add(apero_loc, name='LOCREFSCI', files=[files.pp_flat_dark],
                ref=True, recipe_kind='calib-reference-SCI')
limited_seq.add(apero_shape_ref, ref=True)
limited_seq.add(apero_shape, name='SHAPELREF', ref=True,
                recipe_kind='calib-reference')
limited_seq.add(apero_flat, name='FLATREF', ref=True,
                recipe_kind='calib-reference')
limited_seq.add(apero_leak_ref, ref=True)
limited_seq.add(apero_wave_ref, ref=True,
                rkwargs=dict(hcfiles=[files.pp_hc1_hc1],
                             fpfiles=[files.pp_fp_fp]))
# night runs
limited_seq.add(apero_badpix)
limited_seq.add(apero_loc, files=[files.pp_dark_flat], name='LOCCAL',
                recipe_kind='calib-night-CAL')
limited_seq.add(apero_loc, files=[files.pp_flat_dark], name='LOCSCI',
                recipe_kind='calib-night-SCI')
limited_seq.add(apero_shape)
limited_seq.add(apero_flat, files=[files.pp_flat_flat])
limited_seq.add(apero_wave_night)
# extract tellurics
limited_seq.add(apero_extract, name='EXTTELL', recipe_kind='extract-hotstar',
                files=files.science_pp,
                filters=dict(KW_OBJNAME='TELLURIC_TARGETS'))

# extract science
limited_seq.add(apero_extract, name='EXTOBJ', recipe_kind='extract-science',
                files=files.science_pp,
                filters=dict(KW_OBJNAME='SCIENCE_TARGETS'))

# other telluric recipes
limited_seq.add(apero_mk_tellu, name='MKTELLU1', recipe_kind='tellu-hotstar',
                files=[files.out_ext_e2dsff], fiber=sci_fiber,
                filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
                             KW_DPRTYPE=files.science_dprtypes))
limited_seq.add(apero_mk_model, name='MKTMOD1', recipe_kind='tellu-hotstar')
limited_seq.add(apero_fit_tellu, name='MKTFIT1', recipe_kind='tellu-hotstar',
                files=[files.out_ext_e2dsff], fiber=sci_fiber,
                filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
                             KW_DPRTYPE=files.science_dprtypes))
limited_seq.add(apero_mk_template, name='MKTEMP1', recipe_kind='tellu-hotstar',
                fiber=sci_fiber, arguments=dict(objname='TELLURIC_TARGETS'),
                filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
                             KW_DPRTYPE=files.science_dprtypes),
                template_required=True)
limited_seq.add(apero_mk_tellu, name='MKTELLU2', recipe_kind='tellu-hotstar',
                files=[files.out_ext_e2dsff], fiber=sci_fiber,
                filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
                             KW_DPRTYPE=files.science_dprtypes),
                template_required=True)
limited_seq.add(apero_mk_model, name='MKTMOD2', recipe_kind='tellu-hotstar')
limited_seq.add(apero_fit_tellu, name='MKTFIT2', recipe_kind='tellu-hotstar',
                files=[files.out_ext_e2dsff], fiber=sci_fiber,
                template_required=True,
                filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
                             KW_DPRTYPE=files.science_dprtypes))
limited_seq.add(apero_mk_template, name='MKTEMP2', recipe_kind='tellu-hotstar',
                fiber=sci_fiber, arguments=dict(objname='TELLURIC_TARGETS'),
                filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
                             KW_DPRTYPE=files.science_dprtypes),
                template_required=True)

limited_seq.add(apero_fit_tellu, name='FTFIT1', recipe_kind='tellu-science',
                files=[files.out_ext_e2dsff], fiber=sci_fiber,
                filters=dict(KW_OBJNAME='SCIENCE_TARGETS',
                             KW_DPRTYPE=files.science_dprtypes))
limited_seq.add(apero_mk_template, name='FTTEMP1', recipe_kind='tellu-science',
                fiber=sci_fiber, arguments=dict(objname='SCIENCE_TARGETS'),
                filters=dict(KW_OBJNAME='SCIENCE_TARGETS',
                             KW_DPRTYPE=files.science_dprtypes),
                template_required=True)
limited_seq.add(apero_fit_tellu, name='FTFIT2', recipe_kind='tellu-science',
                files=[files.out_ext_e2dsff], fiber=sci_fiber,
                filters=dict(KW_OBJNAME='SCIENCE_TARGETS',
                             KW_DPRTYPE=files.science_dprtypes),
                template_required=True)
limited_seq.add(apero_mk_template, name='FTTEMP2', recipe_kind='tellu-science',
                fiber=sci_fiber, arguments=dict(objname='SCIENCE_TARGETS'),
                filters=dict(KW_OBJNAME='SCIENCE_TARGETS',
                             KW_DPRTYPE=files.science_dprtypes),
                template_required=True)
# ccf
limited_seq.add(apero_ccf, files=[files.out_tellu_obj], fiber=sci_fiber,
                recipe_kind='rv-tcorr',
                filters=dict(KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP', 'POLAR_DARK',
                                         'POLAR_FP'],
                             KW_OBJNAME='SCIENCE_TARGETS'))

# # post processing
# limited_seq.add(apero_postprocess, name='TELLPOST', files=[files.pp_file],
#                 recipe_kind='post-hotstar',
#                 filters=dict(KW_DPRTYPE=['OBJ_FP', 'OBJ_DARK', 'POLAR_DARK',
#                                          'POLAR_FP'],
#                              KW_OBJNAME='TELLURIC_TARGETS'))

limited_seq.add(apero_postprocess, name='SCIPOST', files=[files.pp_file],
                recipe_kind='post-science',
                filters=dict(KW_DPRTYPE=['OBJ_FP', 'OBJ_DARK', 'POLAR_DARK',
                                         'POLAR_FP'],
                             KW_OBJNAME='SCIENCE_TARGETS'))

# -----------------------------------------------------------------------------
# pp sequence (for trigger)
# -----------------------------------------------------------------------------
pp_seq = drs_recipe.DrsRunSequence('pp_seq', __INSTRUMENT__)
pp_seq.add(apero_pp_ref, recipe_kind='pre-reference')
pp_seq.add(apero_preprocess)

pp_seq_opt = drs_recipe.DrsRunSequence('pp_seq_opt', __INSTRUMENT__)
pp_seq_opt.add(apero_pp_ref, recipe_kind='pre-reference')
pp_seq_opt.add(apero_preprocess, name='PP_CAL', recipe_kind='pre-cal',
               filters=dict(KW_RAW_DPRCATG='CALIB'))
pp_seq_opt.add(apero_preprocess, name='PP_SCI', recipe_kind='pre-sci',
               filters=dict(KW_OBJNAME='SCIENCE_TARGETS'))
pp_seq_opt.add(apero_preprocess, name='PP_TEL', recipe_kind='pre-tel',
               filters=dict(KW_OBJNAME='TELLURIC_TARGETS'))
pp_seq_opt.add(apero_preprocess, name='PP_HC1HC1', files=[files.raw_hc1_hc1],
               recipe_kind='pre-hchc')
pp_seq_opt.add(apero_preprocess, name='PP_FPFP', files=[files.raw_fp_fp],
               recipe_kind='pre-fpfp')
pp_seq_opt.add(apero_preprocess, name='PP_FF', files=[files.raw_flat_flat],
               recipe_kind='pre-ff')
pp_seq_opt.add(apero_preprocess, name='PP_DFP', files=[files.raw_dark_fp],
               recipe_kind='pre-dfp')
pp_seq_opt.add(apero_preprocess, name='PP_FPD', files=[files.raw_fp_dark],
               recipe_kind='pre-fpd')
pp_seq_opt.add(apero_preprocess, name='PP_SKY',
               files=[files.raw_night_sky_sky],
               recipe_kind='pre-sky')
pp_seq_opt.add(apero_preprocess, name='PP_LFC', files=[files.raw_lfc_lfc],
               recipe_kind='pre-lfc')
pp_seq_opt.add(apero_preprocess, name='PP_LFCFP', files=[files.raw_lfc_fp],
               recipe_kind='pre-lfcfp')
pp_seq_opt.add(apero_preprocess, name='PP_FPLFC', files=[files.raw_fp_lfc],
               recipe_kind='pre-fplfc')
pp_seq_opt.add(apero_preprocess, name='PP_EVERY',
               files=[files.raw_file])

# -----------------------------------------------------------------------------
# reference sequence (for trigger)
# -----------------------------------------------------------------------------
ref_seq = drs_recipe.DrsRunSequence('ref_seq', __INSTRUMENT__)
# define schematic file and description file
ref_seq.schematic = 'ref_seq.jpg'
ref_seq.description_file = None
# add recipes
ref_seq.add(apero_dark_ref, ref=True)
ref_seq.add(apero_badpix, name='BADREF', ref=True,
            recipe_kind='calib-reference')
ref_seq.add(apero_loc, name='LOCREFCAL', files=[files.pp_dark_flat],
            ref=False, recipe_kind='calib-reference-CAL')
ref_seq.add(apero_loc, name='LOCREFSCI', files=[files.pp_flat_dark],
            ref=False, recipe_kind='calib-reference-SCI')
ref_seq.add(apero_shape_ref, ref=True)
ref_seq.add(apero_shape, name='SHAPELREF', ref=True,
            recipe_kind='calib-reference')
ref_seq.add(apero_flat, name='FLATREF', ref=True,
            recipe_kind='calib-reference')
ref_seq.add(apero_leak_ref, ref=True)
ref_seq.add(apero_wave_ref, ref=True,
            rkwargs=dict(hcfiles=[files.pp_hc1_hc1],
                         fpfiles=[files.pp_fp_fp]))

# -----------------------------------------------------------------------------
# calibration run (for trigger)
# -----------------------------------------------------------------------------
calib_seq = drs_recipe.DrsRunSequence('calib_seq', __INSTRUMENT__)
# define schematic file and description file
calib_seq.schematic = 'calib_seq.jpg'
calib_seq.description_file = None
# night runs
calib_seq.add(apero_badpix)
calib_seq.add(apero_loc, files=[files.pp_dark_flat], name='LOCCAL',
              recipe_kind='calib-night-CAL')
calib_seq.add(apero_loc, files=[files.pp_flat_dark], name='LOCSCI',
              recipe_kind='calib-night-SCI')
calib_seq.add(apero_shape)
calib_seq.add(apero_flat, files=[files.pp_flat_flat])
calib_seq.add(apero_wave_night)

# -----------------------------------------------------------------------------
# telluric sequence (for trigger)
# -----------------------------------------------------------------------------
tellu_seq = drs_recipe.DrsRunSequence('tellu_seq', __INSTRUMENT__)
# define schematic file and description file
tellu_seq.schematic = 'tellu_seq.jpg'
tellu_seq.description_file = None
# extract science
tellu_seq.add(apero_extract, name='EXTTELL', recipe_kind='extract-hotstar',
              files=files.science_pp,
              filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
                           KW_DPRTYPE=files.science_dprtypes))
# other telluric recipes
tellu_seq.add(apero_mk_tellu, name='MKTELLU1', recipe_kind='tellu-hotstar',
              files=[files.out_ext_e2dsff], fiber=sci_fiber,
              filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
                           KW_DPRTYPE=files.science_dprtypes))
tellu_seq.add(apero_mk_model, name='MKTMOD1', recipe_kind='tellu-hotstar')
tellu_seq.add(apero_fit_tellu, name='MKTFIT1', recipe_kind='tellu-hotstar',
              files=[files.out_ext_e2dsff], fiber=sci_fiber,
              filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
                           KW_DPRTYPE=files.science_dprtypes))
tellu_seq.add(apero_mk_template, name='MKTEMP1', recipe_kind='tellu-hotstar',
              fiber=sci_fiber, files=[files.out_ext_e2dsff],
              arguments=dict(objname='TELLURIC_TARGETS'),
              filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
                           KW_DPRTYPE=files.science_dprtypes),
              template_required=True)

tellu_seq.add(apero_mk_tellu, name='MKTELLU2', recipe_kind='tellu-hotstar',
              fiber=sci_fiber, files=[files.out_ext_e2dsff],
              filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
                           KW_DPRTYPE=files.science_dprtypes),
              template_required=True)
tellu_seq.add(apero_mk_model, name='MKTMOD2', recipe_kind='tellu-hotstar')

tellu_seq.add(apero_fit_tellu, name='MKTFIT2', recipe_kind='tellu-hotstar',
              files=[files.out_ext_e2dsff], fiber=sci_fiber,
              template_required=True,
              filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
                           KW_DPRTYPE=files.science_dprtypes))
tellu_seq.add(apero_mk_template, name='MKTEMP2', recipe_kind='tellu-hotstar',
              fiber=sci_fiber, files=[files.out_ext_e2dsff],
              arguments=dict(objname='TELLURIC_TARGETS'),
              filters=dict(KW_OBJNAME='TELLURIC_TARGETS',
                           KW_DPRTYPE=files.science_dprtypes),
              template_required=True)
#
# # post processing
# tellu_seq.add(apero_postprocess, files=[files.pp_file], name='TELLPOST',
#               recipe_kind='post-hotstar',
#               filters=dict(KW_DPRTYPE=['OBJ_FP', 'OBJ_DARK', 'POLAR_DARK',
#                                        'POLAR_FP'],
#                            KW_OBJNAME='TELLURIC_TARGETS'))

# -----------------------------------------------------------------------------
# science sequence (for trigger)
# -----------------------------------------------------------------------------
science_seq = drs_recipe.DrsRunSequence('science_seq', __INSTRUMENT__)
# define schematic file and description file
science_seq.schematic = 'science_seq.jpg'
science_seq.description_file = None
# extract science
science_seq.add(apero_extract, name='EXTOBJ', recipe_kind='extract-science',
                files=files.science_pp,
                filters=dict(KW_OBJNAME='SCIENCE_TARGETS',
                             KW_DPRTYPE=files.science_dprtypes))
science_seq.add(apero_fit_tellu, name='FTFIT1', recipe_kind='tellu-science',
                files=[files.out_ext_e2dsff], fiber=sci_fiber,
                filters=dict(KW_OBJNAME='SCIENCE_TARGETS',
                             KW_DPRTYPE=files.science_dprtypes))
science_seq.add(apero_mk_template, name='FTTEMP1', fiber=sci_fiber,
                recipe_kind='tellu-science',
                arguments=dict(objname='SCIENCE_TARGETS'),
                filters=dict(KW_OBJNAME='SCIENCE_TARGETS',
                             KW_DPRTYPE=files.science_dprtypes),
                template_required=True)
science_seq.add(apero_fit_tellu, name='FTFIT2', recipe_kind='tellu-science',
                files=[files.out_ext_e2dsff], fiber=sci_fiber,
                filters=dict(KW_OBJNAME='SCIENCE_TARGETS',
                             KW_DPRTYPE=files.science_dprtypes),
                template_required=True)
science_seq.add(apero_mk_template, name='FTTEMP2', fiber=sci_fiber,
                recipe_kind='tellu-science',
                arguments=dict(objname='SCIENCE_TARGETS'),
                filters=dict(KW_OBJNAME='SCIENCE_TARGETS',
                             KW_DPRTYPE=files.science_dprtypes),
                template_required=True)

# ccf
science_seq.add(apero_ccf, files=[files.out_tellu_obj], fiber=sci_fiber,
                recipe_kind='rv-tcorr',
                filters=dict(KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP', 'POLAR_DARK',
                                         'POLAR_FP'],
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
quick_seq = drs_recipe.DrsRunSequence('quick_seq', __INSTRUMENT__)
# extract science
quick_seq.add(apero_extract, name='EXTQUICK', recipe_kind='extract-quick',
              files=files.science_pp,
              arguments=dict(quicklook=True, fiber=sci_fiber),
              filters=dict(KW_OBJNAME='SCIENCE_TARGETS',
                           KW_DPRTYPE=files.science_dprtypes))

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
eng_seq.add(apero_extract, name='EXT_FF', files=[files.pp_flat_flat],
            recipe_kind='extract-ff')
eng_seq.add(apero_extract, name='EXT_DFP', files=[files.pp_dark_fp],
            recipe_kind='extract-dfp')
eng_seq.add(apero_extract, name='EXT_SKY',
            files=[files.pp_night_sky_sky],
            recipe_kind='extract-sky')
eng_seq.add(apero_extract, name='EXT_LFC', files=[files.pp_lfc_lfc],
            recipe_kind='extract-lfc')
eng_seq.add(apero_extract, name='EXT_FPD', files=[files.pp_fp_dark],
            recipe_kind='extract-fpd')
eng_seq.add(apero_extract, name='EXT_LFCFP', files=[files.pp_lfc_fp],
            recipe_kind='extract-lfcfp')
eng_seq.add(apero_extract, name='EXT_FPLFC', files=[files.pp_fp_lfc],
            recipe_kind='extract-fplfc')
eng_seq.add(apero_extract, name='EXT_EVERY', files=[files.pp_file],
            recipe_kind='extract-everything')

# -----------------------------------------------------------------------------
# helios sequence
# -----------------------------------------------------------------------------
helios_seq = drs_recipe.DrsRunSequence('helios_seq', __INSTRUMENT__)

# pp sequences
helios_seq.add(apero_preprocess, name='PP_SUN',
               files=[files.raw_sun_fp, files.raw_sun_dark],
               recipe_kind='pre-sun')
# extract sequences
helios_seq.add(apero_extract, name='EXT_SUN',
               files=[files.pp_sun_fp, files.pp_sun_dark],
               recipe_kind='extract-sun')

# -----------------------------------------------------------------------------
# sequences list
# -----------------------------------------------------------------------------
sequences = [pp_seq, pp_seq_opt, full_seq, limited_seq, ref_seq, calib_seq,
             tellu_seq, science_seq, quick_seq, blank_seq, eng_seq, helios_seq]
