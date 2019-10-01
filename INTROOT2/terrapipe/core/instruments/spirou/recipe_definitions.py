from terrapipe.core import constants
from terrapipe.core.core import drs_recipe
from terrapipe.locale import drs_text

from terrapipe.core.instruments.spirou import file_definitions as sf

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'core.instruments.spirou.recipe_definitions.py'
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
                files=[sf.out_wave_hc, sf.out_wave_fp, sf.out_wave_master],
                helpstr=Help['WAVEFILE_HELP'])

# =============================================================================
# List of usable recipes
# =============================================================================
DrsRecipe = drs_recipe.DrsRecipe

# Below one must define all recipes and put into the "recipes" list
#     must have filemod = correct file definitions
cal_badpix = DrsRecipe(__INSTRUMENT__)
cal_ccf = DrsRecipe(__INSTRUMENT__)
cal_dark = DrsRecipe(__INSTRUMENT__)
cal_dark_master = DrsRecipe(__INSTRUMENT__)
cal_drift1 = DrsRecipe(__INSTRUMENT__)
cal_drift2 = DrsRecipe(__INSTRUMENT__)
cal_extract = DrsRecipe(__INSTRUMENT__)
cal_ff = DrsRecipe(__INSTRUMENT__)
cal_loc = DrsRecipe(__INSTRUMENT__)
cal_pp = DrsRecipe(__INSTRUMENT__)
cal_shape = DrsRecipe(__INSTRUMENT__)
cal_shape_master = DrsRecipe(__INSTRUMENT__)
cal_thermal = DrsRecipe(__INSTRUMENT__)
cal_wave = DrsRecipe(__INSTRUMENT__)
obj_mk_tellu = DrsRecipe(__INSTRUMENT__)
obj_mk_tellu_db = DrsRecipe(__INSTRUMENT__)
obj_fit_tellu = DrsRecipe(__INSTRUMENT__)
obj_fit_tellu_db = DrsRecipe(__INSTRUMENT__)
obj_mk_template = DrsRecipe(__INSTRUMENT__, )

# TODO: remove later
test = DrsRecipe(__INSTRUMENT__)
# push into a list
recipes = [cal_badpix, cal_ccf, cal_dark, cal_dark_master, cal_drift1,
           cal_drift2, cal_extract, cal_ff, cal_loc, cal_pp,
           cal_shape, cal_shape_master, cal_thermal, cal_wave,
           obj_mk_tellu, obj_fit_tellu, obj_mk_template,
           obj_mk_tellu_db, obj_fit_tellu_db,
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
test.set_kwarg(**add_db)
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
cal_pp.shortname = 'PP'
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
cal_badpix.shortname = 'BAD'
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
cal_badpix.set_kwarg(**add_db)
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
cal_dark.set_kwarg(**add_db)
cal_dark.set_kwarg(default=True, **combine)
cal_dark.set_kwarg(**plot)
cal_dark.set_kwarg(**interactive)

# -----------------------------------------------------------------------------
# cal_dark_master_spirou
# -----------------------------------------------------------------------------
cal_dark_master.name = 'cal_dark_master_spirou.py'
cal_dark_master.shortname = 'DARKM'
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
cal_dark_master.set_kwarg(**add_db)
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
                    SUP_FILE=sf.out_loc_sup,
                    DEBUG_BACK=sf.debug_back)
cal_loc.set_arg(pos=0, **directory)
cal_loc.set_arg(name='files', dtype='files', filelogic='exclusive',
                files=[sf.pp_dark_flat, sf.pp_flat_dark], pos='1+',
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
cal_loc.set_kwarg(**interactive)
cal_loc.set_kwarg(**resize)

# -----------------------------------------------------------------------------
# cal_shape_master_spirou
# -----------------------------------------------------------------------------
cal_shape_master.name = 'cal_shape_master_spirou.py'
cal_shape_master.shortname = 'SHAPEM'
cal_shape_master.master = True
cal_shape_master.instrument = __INSTRUMENT__
cal_shape_master.outputdir = 'reduced'
cal_shape_master.inputdir = 'tmp'
cal_shape_master.inputtype = 'pp'
cal_shape_master.extension = 'fits'
cal_shape_master.description = Help['SHAPE_DESC']
cal_shape_master.epilog = Help['SHAPE_EXAMPLE']
cal_shape_master.set_outputs(FPMASTER_FILE=sf.out_shape_fpmaster,
                             DXMAP_FILE=sf.out_shape_dxmap,
                             DYMAP_FILE=sf.out_shape_dymap,
                             SHAPE_IN_FP_FILE=sf.out_shape_debug_ifp,
                             SHAPE_IN_HC_FILE=sf.out_shape_debug_ihc,
                             SHAPE_OUT_FP_FILE=sf.out_shape_debug_ofp,
                             SHAPE_OUT_HC_FILE=sf.out_shape_debug_ohc,
                             SHAPE_BDXMAP_FILE=sf.out_shape_debug_bdx,
                             DEBUG_BACK=sf.debug_back)
cal_shape_master.set_arg(pos=0, **directory)
cal_shape_master.set_kwarg(name='-hcfiles', dtype='files',
                           files=[sf.pp_hc1_hc1],
                           nargs='+', filelogic='exclusive', required=True,
                           helpstr=Help['SHAPE_HCFILES_HELP'], default=[])
cal_shape_master.set_kwarg(name='-fpfiles', dtype='files', files=[sf.pp_fp_fp],
                           nargs='+', filelogic='exclusive', required=True,
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
                      SHAPEL_OUT_FP_FILE=sf.out_shapel_debug_ofp,
                      DEBUG_BACK=sf.debug_back)
cal_shape.set_arg(pos=0, **directory)
cal_shape.set_arg(name='files', dtype='files', files=[sf.pp_fp_fp], pos='1+',
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
                   ORDERP_SFILE=sf.out_orderp_straight,
                   DEBUG_BACK=sf.debug_back)
cal_ff.set_arg(pos=0, **directory)
cal_ff.set_arg(name='files', dtype='files', filelogic='exclusive',
               files=[sf.pp_flat_flat], pos='1+',
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
cal_ff.set_kwarg(**interactive)
cal_ff.set_kwarg(**resize)
cal_ff.set_kwarg(**shapexfile)
cal_ff.set_kwarg(**shapeyfile)
cal_ff.set_kwarg(**shapelfile)

# -----------------------------------------------------------------------------
# cal_thermal_spirou
# -----------------------------------------------------------------------------
cal_thermal.name = 'cal_thermal_spirou.py'
cal_thermal.shortname = 'THERM'
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
cal_extract.shortname = 'EXT'
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
                        ORDERP_SFILE=sf.out_orderp_straight,
                        DEBUG_BACK=sf.debug_back)
cal_extract.set_arg(pos=0, **directory)
cal_extract.set_arg(name='files', dtype='files', pos='1+', files=[sf.pp_file],
                    helpstr=Help['FILES_HELP'] + Help['EXTRACT_FILES_HELP'],
                    limit=1)
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
# cal_WAVE_E2DS_spirou
# -----------------------------------------------------------------------------
cal_wave.name = 'cal_wave_spirou.py'
cal_wave.shortname = 'WAVE'
cal_wave.instrument = __INSTRUMENT__
cal_wave.outputdir = 'reduced'
cal_wave.inputdir = 'tmp'
cal_wave.inputtype = 'pp'
cal_wave.extension = 'fits'
cal_wave.description = Help['WAVE_DESC']
cal_wave.epilog = Help['WAVE_EXAMPLE']
cal_wave.set_outputs(WAVE_E2DS=sf.out_ext_e2dsff,
                     WAVE_HCLL=sf.out_wave_hcline,
                     WAVE_HCRES=sf.out_wave_hcres,
                     WAVE_HCMAP=sf.out_wave_hc,
                     WAVE_FPMAP=sf.out_wave_fp,
                     WAVE_FPRESTAB=sf.out_wave_res_table,
                     WAVE_FPLLTAB=sf.out_wave_ll_table)
cal_wave.set_arg(pos=0, **directory)
cal_wave.set_kwarg(name='-hcfiles', dtype='files', files=[sf.pp_hc1_hc1],
                   nargs='+', filelogic='exclusive', required=True,
                   helpstr=Help['WAVE_HCFILES_HELP'], default=[])
# note required is False (so we don't need fpfiles but reprocess is True
#    so reprocessing script will fill both hc and fp files
cal_wave.set_kwarg(name='-fpfiles', dtype='files', files=[sf.pp_fp_fp],
                   nargs='+', filelogic='exclusive', reprocess=True,
                   helpstr=Help['WAVE_FPFILES_HELP'], default=[])
cal_wave.set_kwarg(**add_db)
cal_wave.set_kwarg(**badfile)
cal_wave.set_kwarg(**dobad)
cal_wave.set_kwarg(**backsub)
cal_wave.set_kwarg(default=True, **combine)
cal_wave.set_kwarg(**darkfile)
cal_wave.set_kwarg(**dodark)
cal_wave.set_kwarg(**fiber)
cal_wave.set_kwarg(**flipimage)
cal_wave.set_kwarg(**fluxunits)
cal_wave.set_kwarg(**locofile)
cal_wave.set_kwarg(**orderpfile)
cal_wave.set_kwarg(**plot)
cal_wave.set_kwarg(**interactive)
cal_wave.set_kwarg(**resize)
cal_wave.set_kwarg(**shapexfile)
cal_wave.set_kwarg(**shapeyfile)
cal_wave.set_kwarg(**shapelfile)
cal_wave.set_kwarg(**wavefile)
cal_wave.set_kwarg(name='-hcmode', dtype='options', helpstr=Help['HCMODE_HELP'],
                   options=[0], default_ref='WAVE_MODE_HC')
cal_wave.set_kwarg(name='-fpmode', dtype='options', helpstr=Help['FPMODE_HELP'],
                   options=[0, 1], default_ref='WAVE_MODE_FP')

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
cal_ccf.name = 'cal_ccf_spirou.py'
cal_ccf.shortname = 'CCF'
cal_ccf.instrument = __INSTRUMENT__
cal_ccf.outputdir = 'reduced'
cal_ccf.inputdir = 'reduced'
cal_ccf.inputtype = 'reduced'
cal_ccf.extension = 'fits'
cal_ccf.description = Help['CCF_DESC']
cal_ccf.epilog = Help['CCF_EXAMPLE']
cal_ccf.set_outputs()
cal_ccf.set_arg(pos=0, **directory)
cal_ccf.set_arg(name='files', dtype='files', pos='1+',
                files=[sf.out_ext_e2ds, sf.out_ext_e2dsff,
                       sf.out_tellu_obj],
                helpstr=Help['FILES_HELP'] + Help['CCF_FILES_HELP'],
                limit=1)
cal_ccf.set_kwarg(name='--mask', dtype='file', default_ref='CCF_DEFAULT_MASK',
                  helpstr=Help['CCF_MASK_HELP'], path='WAVE_CCF_MASK_PATH',
                  files=sf.other_ccf_mask_file)
cal_ccf.set_kwarg(name='--rv', dtype=float, default=0.0,
                  helpstr=Help['CCF_RV_HELP'])
cal_ccf.set_kwarg(name='--width', dtype=float, default_ref='CCF_DEFAULT_WIDTH',
                  helpstr=Help['CCF_WIDTH_HELP'])
cal_ccf.set_kwarg(name='--step', dtype=float, default_ref='CCF_DEFAULT_STEP',
                  helpstr=Help['CCF_STEP_HELP'])
cal_ccf.set_kwarg(**add_db)
cal_ccf.set_kwarg(**plot)
cal_ccf.set_kwarg(**interactive)

# -----------------------------------------------------------------------------
# obj_mk_tellu
# -----------------------------------------------------------------------------
obj_mk_tellu.name = 'obj_mk_tellu_spirou.py'
obj_mk_tellu.shortname = 'MKTELL'
obj_mk_tellu.instrument = __INSTRUMENT__
obj_mk_tellu.outputdir = 'reduced'
obj_mk_tellu.inputdir = 'reduced'
obj_mk_tellu.inputtype = 'reduced'
obj_mk_tellu.extension = 'fits'
obj_mk_tellu.description = Help['MKTELL_DESC']
obj_mk_tellu.epilog = Help['MKTELL_EXAMPLE']
obj_mk_tellu.set_outputs(TELLU_CONV=sf.out_tellu_conv,
                         TELLU_TRANS=sf.out_tellu_trans)
obj_mk_tellu.set_arg(pos=0, **directory)
obj_mk_tellu.set_arg(name='files', dtype='files', pos='1+',
                     files=[sf.out_ext_e2ds, sf.out_ext_e2dsff],
                     helpstr=Help['FILES_HELP'] + Help['MKTELL_FILES_HELP'],
                     limit=1)
obj_mk_tellu.set_kwarg(**add_db)
obj_mk_tellu.set_kwarg(**plot)
obj_mk_tellu.set_kwarg(**interactive)
obj_mk_tellu.set_kwarg(**wavefile)

# -----------------------------------------------------------------------------
# obj_mk_tellu_db
# -----------------------------------------------------------------------------
obj_mk_tellu_db.name = 'obj_mk_tellu_db_spirou.py'
obj_mk_tellu_db.shortname = 'MKTELLDB'
obj_mk_tellu_db.instrument = __INSTRUMENT__
obj_mk_tellu_db.outputdir = 'reduced'
obj_mk_tellu_db.inputdir = 'reduced'
obj_mk_tellu_db.inputtype = 'reduced'
obj_mk_tellu_db.extension = 'fits'
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
obj_mk_tellu_db.set_kwarg(**add_db)
obj_mk_tellu_db.set_kwarg(**add_db)
obj_mk_tellu_db.set_kwarg(**plot)
obj_mk_tellu_db.set_kwarg(**interactive)
obj_mk_tellu_db.set_kwarg(**wavefile)

# -----------------------------------------------------------------------------
# obj_fit_tellu
# -----------------------------------------------------------------------------
obj_fit_tellu.name = 'obj_fit_tellu_spirou.py'
obj_fit_tellu.shortname = 'FTELLU'
obj_fit_tellu.instrument = __INSTRUMENT__
obj_fit_tellu.outputdir = 'reduced'
obj_fit_tellu.inputdir = 'reduced'
obj_fit_tellu.inputtype = 'reduced'
obj_fit_tellu.extension = 'fits'
obj_fit_tellu.description = Help['FTELLU_DESC']
obj_fit_tellu.epilog = Help['FTELLU_EXAMPLE']
obj_fit_tellu.set_outputs(ABSO_NPY=sf.out_tellu_abso_npy,
                          TELLU_OBJ=sf.out_tellu_obj,
                          SC1D_W_FILE=sf.out_tellu_sc1d_w,
                          SC1D_V_FILE=sf.out_tellu_sc1d_v,
                          TELLU_RECON=sf.out_tellu_recon,
                          RC1D_W_FILE=sf.out_tellu_rc1d_w,
                          RC1D_V_FILE=sf.out_tellu_rc1d_v)
obj_fit_tellu.set_arg(pos=0, **directory)
obj_fit_tellu.set_arg(name='files', dtype='files', pos='1+',
                      files=[sf.out_ext_e2ds, sf.out_ext_e2dsff],
                      helpstr=Help['FILES_HELP'] + Help['FTELLU_FILES_HELP'],
                      limit=1)
obj_fit_tellu.set_kwarg(**add_db)
obj_fit_tellu.set_kwarg(**plot)
obj_fit_tellu.set_kwarg(**interactive)
obj_fit_tellu.set_kwarg(**wavefile)

# -----------------------------------------------------------------------------
# obj_fit_tellu_db
# -----------------------------------------------------------------------------
obj_fit_tellu_db.name = 'obj_fit_tellu_db_spirou.py'
obj_fit_tellu_db.shortname = 'FTELLDB'
obj_fit_tellu_db.instrument = __INSTRUMENT__
obj_fit_tellu_db.outputdir = 'reduced'
obj_fit_tellu_db.inputdir = 'reduced'
obj_fit_tellu_db.inputtype = 'reduced'
obj_fit_tellu_db.extension = 'fits'
obj_fit_tellu_db.description = Help['FTELLUDB_DESC']
obj_fit_tellu_db.epilog = Help['FTELLUDB_EXAMPLE']
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
obj_fit_tellu_db.set_kwarg(**add_db)
obj_fit_tellu_db.set_kwarg(**add_db)
obj_fit_tellu_db.set_kwarg(**plot)
obj_fit_tellu_db.set_kwarg(**interactive)
obj_fit_tellu_db.set_kwarg(**wavefile)

# -----------------------------------------------------------------------------
# obj_mk_temp
# -----------------------------------------------------------------------------
obj_mk_template.name = 'obj_mk_template_spirou.py'
obj_mk_template.shortname = 'MKTEMP'
obj_mk_template.instrument = __INSTRUMENT__
obj_mk_template.outputdir = 'reduced'
obj_mk_template.inputdir = 'reduced'
obj_mk_template.inputtype = 'reduced'
obj_mk_template.extension = 'fits'
obj_mk_template.description = Help['MKTEMP_DESC']
obj_mk_template.epilog = Help['MKTEMP_EXAMPLE']
obj_mk_template.set_outputs(TELLU_TEMP=sf.out_tellu_template,
                            TELLU_BIGCUBE=sf.out_tellu_bigcube,
                            TELLU_BIGCUBE0=sf.out_tellu_bigcube0,
                            TELLU_TEMP_S1D=sf.out_tellu_s1d_template,
                            TELLU_BIGCUBE_S1D=sf.out_tellu_s1d_bigcube)
obj_mk_template.set_arg(name='objname', pos=0, dtype=str,
                        helpstr=Help['MKTEMP_OBJNAME_HELP'])
obj_mk_template.set_kwarg(name='-filetype', dtype=str,
                          default_ref='MKTEMPLATE_FILETYPE',
                          helpstr=Help['MKTEMP_FILETYPE'],
                          options=['EXT_E2DS', 'EXT_E2DS_FF'])
obj_mk_template.set_kwarg(name='-fiber', dtype=str,
                          default_ref='MKTEMPLATE_FIBER_TYPE',
                          helpstr=Help['MKTEMP_FIBER'],
                          options=['AB', 'A', 'B', 'C'])
obj_mk_template.set_kwarg(**add_db)
obj_mk_template.set_kwarg(**plot)
obj_mk_template.set_kwarg(**interactive)
obj_mk_template.set_kwarg(**wavefile)

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
full_run.add(cal_pp)
full_run.add(cal_dark_master, master=True)
full_run.add(cal_badpix, name='BADM', master=True)
full_run.add(cal_loc, name='LOCM', files=[sf.pp_dark_flat], master=True)
full_run.add(cal_loc, name='LOCM', files=[sf.pp_flat_dark], master=True)
full_run.add(cal_shape_master, master=True)
# night runs
full_run.add(cal_badpix)
full_run.add(cal_loc, files=[sf.pp_dark_flat])
full_run.add(cal_loc, files=[sf.pp_flat_dark])
full_run.add(cal_shape)
full_run.add(cal_ff, files=[sf.pp_flat_flat])
full_run.add(cal_thermal)
full_run.add(cal_wave, name='WAVEFP', hcfiles=[sf.pp_hc1_hc1],
             fpfiles=[sf.pp_fp_fp])
# extract all
full_run.add(cal_extract, name='EXTALL', files=[sf.pp_obj_dark, sf.pp_obj_fp])

# -----------------------------------------------------------------------------
# limited run (master + nights)
# -----------------------------------------------------------------------------
limited_run = drs_recipe.DrsRunSequence('limited_run', __INSTRUMENT__)
# master run
limited_run.add(cal_pp)
limited_run.add(cal_dark_master, master=True)
limited_run.add(cal_badpix, name='BADM', master=True)
limited_run.add(cal_loc, name='LOCM', files=[sf.pp_dark_flat], master=True)
limited_run.add(cal_loc, name='LOCM', files=[sf.pp_flat_dark], master=True)
limited_run.add(cal_shape_master, master=True)
# night runs
limited_run.add(cal_badpix)
limited_run.add(cal_loc, files=[sf.pp_dark_flat])
limited_run.add(cal_loc, files=[sf.pp_flat_dark])
limited_run.add(cal_shape)
limited_run.add(cal_ff, files=[sf.pp_flat_flat])
limited_run.add(cal_thermal)
limited_run.add(cal_wave, name='WAVEHC', files=[sf.pp_hc1_hc1], fpfiles=None)
limited_run.add(cal_wave, name='WAVEFP', hcfiles=[sf.pp_hc1_hc1],
                fpfiles=[sf.pp_fp_fp])
# extract tellurics
limited_run.add(cal_extract, name='EXTTELL', KW_OBJNAME='TELLURIC_TARGETS',
                files=[sf.pp_obj_dark, sf.pp_obj_fp])

# extract science
limited_run.add(cal_extract, name='EXTOBJ', KW_OBJNAME='SCIENCE_TARGETS',
                files=[sf.pp_obj_dark, sf.pp_obj_fp])

# telluric recipes
limited_run.add(obj_mk_tellu_db, arguments=dict(cores='CORES'))
limited_run.add(obj_fit_tellu_db, arguments=dict(cores='CORES'))

# limited_run.add(obj_mk_tellu, name='MKTELLU1', KW_OBJNAME='TELLURIC_TARGETS',
#                 files = [sf.out_ext_e2dsff], fiber='AB',
#                 KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP'])
# limited_run.add(obj_fit_tellu, name='MKTELLU2', KW_OBJNAME='TELLURIC_TARGETS',
#                 files=[sf.out_ext_e2dsff], fiber='AB',
#                 KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP'])
# limited_run.add(obj_mk_template, name='MKTELLU3', KW_OBJNAME='TELLURIC_TARGETS',
#                 fiber='AB', KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP'])
# limited_run.add(obj_mk_tellu, name='MKTELLU4', KW_OBJNAME='TELLURIC_TARGETS',
#                 fiber='AB', KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP'])

# limited_run.add(obj_fit_tellu, name='FTELLU1', KW_OBJNAME='SCIENCE_TARGETS',
#                 files=[sf.out_ext_e2dsff], fiber='AB',
#                 KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP'])
# limited_run.add(obj_mk_template, name='FTELLU2', KW_OBJNAME='SCIENCE_TARGETS',
#                 fiber='AB', KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP'])
# limited_run.add(obj_fit_tellu, name='FTELLU3', KW_OBJNAME='SCIENCE_TARGETS',
#                 fiber='AB', KW_DPRTYPE=['OBJ_DARK', 'OBJ_FP'])

# -----------------------------------------------------------------------------
# object run (extract )
# -----------------------------------------------------------------------------
science_run = drs_recipe.DrsRunSequence('science_run', __INSTRUMENT__)
# extract science
science_run.add(cal_extract, name='EXTOBJ', KW_OBJNAME='SCIENCE_TARGETS',
                files=[sf.pp_obj_dark, sf.pp_obj_fp])

# -----------------------------------------------------------------------------
# hc run (extract )
# -----------------------------------------------------------------------------
hc_run = drs_recipe.DrsRunSequence('hc_run', __INSTRUMENT__)
# master run
hc_run.add(cal_pp)
hc_run.add(cal_dark_master, master=True)
hc_run.add(cal_badpix, name='BADM', master=True)
hc_run.add(cal_loc, name='LOCM', files=[sf.pp_dark_flat], master=True)
hc_run.add(cal_loc, name='LOCM', files=[sf.pp_flat_dark], master=True)
hc_run.add(cal_shape_master, master=True)
# night runs
hc_run.add(cal_badpix)
hc_run.add(cal_loc, files=[sf.pp_dark_flat])
hc_run.add(cal_loc, files=[sf.pp_flat_dark])
hc_run.add(cal_shape)
hc_run.add(cal_ff, files=[sf.pp_flat_flat])
hc_run.add(cal_thermal)
# extract science
hc_run.add(cal_extract, name='EXTHC', files=[sf.pp_hc1_hc1])

# -----------------------------------------------------------------------------
# sequences list
# -----------------------------------------------------------------------------
sequences = [full_run, limited_run, science_run, hc_run]
