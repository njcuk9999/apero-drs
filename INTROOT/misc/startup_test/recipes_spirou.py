from misc.startup_test import spirouRecipe, files_spirou as sf, spirouFile, \
    recipe_descriptions as rd
from SpirouDRS import spirouConfig

# =============================================================================
# Define variables
# =============================================================================
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()

# =============================================================================
# Commonly used arguments
# =============================================================================
directory = dict(name='directory', dtype='directory',
                 helpstr=rd.General.directory_help)

# =============================================================================
# Option definitions
# =============================================================================
#
# Note for these to work MUST add to spirouStartup.spirou_options_manager
#
# -----------------------------------------------------------------------------
add_cal = dict(name='--add2calib', dtype='bool', default=True,
               helpstr=rd.General.add_cal_help)
# -----------------------------------------------------------------------------
dobad = dict(name='--badcorr', dtype='bool', default=True,
             helpstr=rd.General.dobad_help)

# -----------------------------------------------------------------------------
backsub = dict(name='--backsub', dtype='bool', default=True,
               helpstr=rd.General.backsub_help, default_ref='option_backsub')
# -----------------------------------------------------------------------------
# Must set default per recipe!!
combine = dict(name='--combine', dtype='bool',
               helpstr=rd.General.combine_help)
# -----------------------------------------------------------------------------
dodark = dict(name='--darkcorr', dtype='bool', default=True,
              helpstr=rd.General.dodark_help)
# -----------------------------------------------------------------------------
# Must set default_ref per recipe!!
extractmethod = dict(name='--extractmethod', dtype='options',
                     helpstr=rd.General.extractmethod_help,
                     options=['1', '2', '3a', '3b', '3c', '3d', '4a', '4b'])
# -----------------------------------------------------------------------------
extfiber = dict(name='--extfiber', dtype='options', default='ALL',
                helpstr=rd.General.extfiber_help,
                options=['ALL', 'AB', 'A', 'B', 'C'])
# -----------------------------------------------------------------------------
flipimage = dict(name='--flipimage', dtype='options', default='both',
                 helpstr=rd.General.flipimage_help,
                 options=['None', 'x', 'y', 'both'])
# -----------------------------------------------------------------------------
fluxunits = dict(name='--fluxunits', dtype='options', default='e-',
                 helpstr=rd.General.fluxunits_help, options=['ADU/s', 'e-'])
# -----------------------------------------------------------------------------
plot = dict(name='--plot', dtype='bool', helpstr=rd.General.plot_help,
            default_ref='DRS_PLOT')
# -----------------------------------------------------------------------------
resize = dict(name='--resize', dtype='bool', default=True,
              helpstr=rd.General.resize_help)

# =============================================================================
# File option definitions
# =============================================================================
badfile = dict(name='--badpixfile', dtype='file', default='None',
               files=[sf.out_badpix],
               helpstr=rd.General.badfile_help)
# -----------------------------------------------------------------------------
blazefile = dict(name='--blazefile', dtype='file', default='None',
                 files=[sf.out_ff_blaze_ab, sf.out_ff_blaze_a,
                        sf.out_ff_blaze_b, sf.out_ff_blaze_c],
                 helpstr=rd.General.blazefile_help)
# -----------------------------------------------------------------------------
darkfile = dict(name='--darkfile', dtype='file', default='None',
                files=[sf.out_dark],
                helpstr=rd.General.darkfile_help)
# -----------------------------------------------------------------------------
flatfile = dict(name='--flatfile', dtype='file', default='None',
                files=[sf.out_ff_flat_ab, sf.out_ff_flat_a,
                       sf.out_ff_flat_b, sf.out_ff_flat_c],
                helpstr=rd.General.flatfile_help)
# -----------------------------------------------------------------------------
shapefile = dict(name='--shapefile', dtype='file', default='None',
                 files=[sf.out_silt_shape],
                 helpstr=rd.General.shapefile_help)
# -----------------------------------------------------------------------------
tiltfile = dict(name='--tiltfile', dtype='file', default='None',
                files=[sf.out_slit_tilt],
                helpstr=rd.General.tiltfile_help)
# -----------------------------------------------------------------------------
wavefile = dict(name='--wavefile', dtype='file', default='None',
                files=[sf.out_wave_ab, sf.out_wave_a,
                       sf.out_wave_b, sf.out_wave_c],
                helpstr=rd.General.wavefile_help)

# =============================================================================
# List of usable recipes
# =============================================================================
drs_recipe = spirouRecipe.DrsRecipe

# Below one must define all recipes and put into the "recipes" list
cal_badpix = drs_recipe()
cal_ccf = drs_recipe()
cal_dark = drs_recipe()
cal_drift1 = drs_recipe()
cal_drift2 = drs_recipe()
cal_extract = drs_recipe()
cal_ff = drs_recipe()
cal_hc = drs_recipe()
cal_loc = drs_recipe()
cal_pp = drs_recipe()
cal_slit = drs_recipe()
cal_shape = drs_recipe()
cal_wave = drs_recipe()

test = drs_recipe()
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
raw_recipe = drs_recipe()
pp_recipe = drs_recipe()
out_recipe = drs_recipe()

# -----------------------------------------------------------------------------
# test.py
# -----------------------------------------------------------------------------
test.name = 'test_recipe.py'
test.instrument = 'SPIROU'
test.outputdir = 'tmp'
test.inputdir = 'tmp'
test.inputtype = 'pp'
test.extension = 'fits'
test.description = rd.Test.description
test.epilog = rd.Test.example
test.arg(pos=0, **directory)
test.kwarg(name='-filelist1', dtype='files', default=[], nargs='+',
           files=[sf.pp_dark_dark, sf.pp_flat_flat], filelogic='inclusive',
           helpstr='test 1', required=True)
test.kwarg(name='-filelist2', dtype='files', default=[], nargs='+',
           files=[sf.pp_fp_fp], helpstr='test 2', required=True)
test.kwarg(**plot)
test.kwarg(**add_cal)
test.kwarg(**dobad)
test.kwarg(**badfile)
test.kwarg(default=False, **combine)
test.kwarg(**dodark)
test.kwarg(**darkfile)
test.kwarg(**flipimage)
test.kwarg(**fluxunits)
test.kwarg(**resize)

# -----------------------------------------------------------------------------
# cal_preprocess_spirou
# -----------------------------------------------------------------------------
cal_pp.name = 'cal_preprocess_spirou.py'
cal_pp.instrument = 'SPIROU'
cal_pp.outputdir = 'tmp'
cal_pp.inputdir = 'raw'
cal_pp.inputtype = 'raw'
cal_pp.extension = 'fits'
cal_pp.description = rd.Preprocess.description
cal_pp.epilog = rd.Preprocess.example
cal_pp.arg(pos=0, **directory)
cal_pp.arg(name='ufiles', dtype='files', pos='1+', files=[sf.raw_file],
           helpstr=rd.Preprocess.ufiles_help)
cal_pp.kwarg(**plot)

# -----------------------------------------------------------------------------
# cal_badpix_spirou
# -----------------------------------------------------------------------------
cal_badpix.name = 'cal_BADPIX_spirou.py'
cal_badpix.instrument = 'SPIROU'
cal_badpix.outputdir = 'reduced'
cal_badpix.inputdir = 'tmp'
cal_badpix.inputtype = 'pp'
cal_badpix.extension = 'fits'
cal_badpix.description = rd.Badpix.description
cal_badpix.epilog = rd.Badpix.example
cal_badpix.run_order = 1
cal_badpix.arg(pos=0, **directory)
cal_badpix.arg(name='flatfile', dtype='file', files=[sf.pp_flat_flat], pos=1,
               filelogic='exclusive', helpstr=rd.Badpix.flatfile_help)
cal_badpix.arg(name='darkfile', dtype='file', files=[sf.pp_dark_dark], pos=2,
               filelogic='exclusive', helpstr=rd.Badpix.darkfile_help)
cal_badpix.kwarg(**add_cal)
cal_badpix.kwarg(**badfile)
cal_badpix.kwarg(**dobad)
cal_badpix.kwarg(default=True, **combine)
cal_badpix.kwarg(**darkfile)
cal_badpix.kwarg(**dodark)
cal_badpix.kwarg(**flipimage)
cal_badpix.kwarg(**fluxunits)
cal_badpix.kwarg(**plot)
cal_badpix.kwarg(**resize)

# -----------------------------------------------------------------------------
# cal_dark_spirou
# -----------------------------------------------------------------------------
cal_dark.name = 'cal_DARK_spirou.py'
cal_dark.instrument = 'SPIROU'
cal_dark.outputdir = 'reduced'
cal_dark.inputdir = 'tmp'
cal_dark.intputtype = 'pp'
cal_dark.extension = 'fits'
cal_dark.description = rd.Dark.description
cal_dark.epilog = rd.Dark.example
cal_dark.run_order = 2
cal_dark.arg(pos=0, **directory)
cal_dark.arg(name='files', dtype='files', files=[sf.pp_dark_dark], pos='1+',
             helpstr=rd.Dark.files_help)
cal_dark.kwarg(**add_cal)
cal_dark.kwarg(default=True, **combine)
cal_dark.kwarg(**flipimage)
cal_dark.kwarg(**fluxunits)
cal_dark.kwarg(**plot)
cal_dark.kwarg(**resize)

# -----------------------------------------------------------------------------
# cal_loc_RAW_spirou
# -----------------------------------------------------------------------------
cal_loc.name = 'cal_loc_RAW_spirou.py'
cal_loc.instrument = 'SPIROU'
cal_loc.outputdir = 'reduced'
cal_loc.inputdir = 'tmp'
cal_loc.inputtype = 'pp'
cal_loc.extension = 'fits'
cal_loc.description = rd.Localisation.description
cal_loc.epilog = rd.Localisation.example
cal_loc.run_order = 3
cal_loc.arg(pos=0, **directory)
cal_loc.arg(name='files', dtype='files', filelogic='exclusive',
            files=[sf.pp_dark_flat, sf.pp_flat_dark], pos='1+',
            helpstr=rd.Localisation.files_help)
cal_loc.kwarg(**add_cal)
cal_loc.kwarg(**badfile)
cal_loc.kwarg(**dobad)
cal_loc.kwarg(**backsub)
cal_loc.kwarg(default=True, **combine)
cal_loc.kwarg(**darkfile)
cal_loc.kwarg(**dodark)
cal_loc.kwarg(**flipimage)
cal_loc.kwarg(**fluxunits)
cal_loc.kwarg(**plot)
cal_loc.kwarg(**resize)

# -----------------------------------------------------------------------------
# cal_SLIT_spirou
# -----------------------------------------------------------------------------
cal_slit.name = 'cal_SLIT_spirou.py'
cal_slit.instrument = 'SPIROU'
cal_slit.outputdir = 'reduced'
cal_slit.inputdir = 'tmp'
cal_slit.inputtype = 'pp'
cal_slit.extension = 'fits'
cal_slit.description = rd.Slit.description
cal_slit.epilog = rd.Slit.example
cal_slit.run_order = 4
cal_slit.arg(pos=0, **directory)
cal_slit.arg(name='files', dtype='files', files=[sf.pp_fp_fp], pos='1+', 
             helpstr=rd.Slit.files_help)
cal_slit.kwarg(**add_cal)
cal_slit.kwarg(**badfile)
cal_slit.kwarg(**dobad)
cal_slit.kwarg(**backsub)
cal_slit.kwarg(default=True, **combine)
cal_slit.kwarg(**darkfile)
cal_slit.kwarg(**dodark)
cal_slit.kwarg(**flipimage)
cal_slit.kwarg(**fluxunits)
cal_slit.kwarg(**plot)
cal_slit.kwarg(**resize)

# -----------------------------------------------------------------------------
# cal_SHAPE_spirou
# -----------------------------------------------------------------------------
cal_shape.name = 'cal_SHAPE_spirou.py'
cal_shape.instrument = 'SPIROU'
cal_shape.outputdir = 'reduced'
cal_shape.inputdir = 'tmp'
cal_shape.inputtype = 'pp'
cal_shape.extension = 'fits'
cal_shape.description = rd.Shape.description
cal_shape.epilog = rd.Shape.example
cal_shape.run_order = 4
cal_shape.arg(pos=0, **directory)
cal_shape.arg(name='hcfile', dtype='file', files=[sf.pp_hc1_hc1], pos='1', 
             helpstr=rd.Shape.hcfile_help)
cal_shape.arg(name='fpfiles', dtype='files', files=[sf.pp_fp_fp], pos='2+', 
             helpstr=rd.Shape.fpfiles_help)
cal_shape.kwarg(**add_cal)
cal_shape.kwarg(**badfile)
cal_shape.kwarg(**dobad)
cal_shape.kwarg(**backsub)
cal_shape.kwarg(default=True, **combine)
cal_shape.kwarg(**darkfile)
cal_shape.kwarg(**dodark)
cal_shape.kwarg(**flipimage)
cal_shape.kwarg(**fluxunits)
cal_shape.kwarg(**plot)
cal_shape.kwarg(**resize)

# -----------------------------------------------------------------------------
# cal_FF_RAW_spirou
# -----------------------------------------------------------------------------
cal_ff.name = 'cal_FF_RAW_spirou.py'
cal_ff.instrument = 'SPIROU'
cal_ff.outputdir = 'reduced'
cal_ff.inputdir = 'tmp'
cal_ff.inputtype = 'pp'
cal_ff.extension = 'fits'
cal_ff.description = rd.Flat.description
cal_ff.epilog = rd.Flat.example
cal_ff.run_order = 5
cal_ff.arg(pos=0, **directory)
cal_ff.arg(name='files', dtype='files', filelogic='exclusive',
           files=[sf.pp_flat_flat, sf.pp_dark_flat, sf.pp_flat_dark], pos='1+',
           helpstr=rd.Flat.files_help)
cal_ff.kwarg(**add_cal)
cal_ff.kwarg(**badfile)
cal_ff.kwarg(**dobad)
cal_ff.kwarg(**backsub)
cal_ff.kwarg(default=True, **combine)
cal_ff.kwarg(**darkfile)
cal_ff.kwarg(**dodark)
cal_ff.kwarg(default_ref='IC_FF_EXTRACT_TYPE', **extractmethod)
cal_ff.kwarg(**extfiber)
cal_ff.kwarg(**flipimage)
cal_ff.kwarg(**fluxunits)
cal_ff.kwarg(**plot)
cal_ff.kwarg(**resize)
cal_ff.kwarg(**shapefile)
cal_ff.kwarg(**tiltfile)

# -----------------------------------------------------------------------------
# cal_extract_RAW_spirou
# -----------------------------------------------------------------------------
cal_extract.name = 'cal_extract_RAW_spirou.py'
cal_extract.instrument = 'SPIROU'
cal_extract.outputdir = 'reduced'
cal_extract.inputdir = 'tmp'
cal_extract.inputtype = 'pp'
cal_extract.extension = 'fits'
cal_extract.description = rd.Extract.description
cal_extract.epilog = rd.Extract.example
cal_extract.run_order = 6
cal_extract.arg(pos=0, **directory)
cal_extract.arg(name='files', dtype='files', pos='1+', files=[sf.pp_file],
                limit=1, helpstr=rd.Extract.files_help)
cal_extract.kwarg(**add_cal)
cal_extract.kwarg(**badfile)
cal_extract.kwarg(**dobad)
cal_extract.kwarg(**backsub)
cal_extract.kwarg(default=True, **combine)
cal_extract.kwarg(**darkfile)
cal_extract.kwarg(**dodark)
cal_extract.kwarg(default_ref='IC_EXTRACT_TYPE', **extractmethod)
cal_extract.kwarg(**extfiber)
cal_extract.kwarg(**flipimage)
cal_extract.kwarg(**fluxunits)
cal_extract.kwarg(**plot)
cal_extract.kwarg(**resize)
cal_extract.kwarg(**shapefile)
cal_extract.kwarg(**tiltfile)

# -----------------------------------------------------------------------------
# cal_HC_E2DS_spirou
# -----------------------------------------------------------------------------
cal_hc.name = 'cal_HC_E2DS_spirou.py'
cal_hc.instrument = 'SPIROU'
cal_hc.outputdir = 'reduced'
cal_hc.inputdir = 'reduced'
cal_hc.inputtype = 'e2ds'
cal_hc.extension = 'fits'
cal_hc.description = rd.HcE2DS.description
cal_hc.epilog = rd.HcE2DS.example
cal_hc.run_order = 7
# setup custom files (add a required keyword in the header to each file)
#    in this case we require "KW_EXT_TYPE" = "HCONE_HCONE"
cal_hc_files1 = [sf.out_ext_e2ds_ab, sf.out_ext_e2ds_c,
                 sf.out_ext_e2dsff_ab, sf.out_ext_e2dsff_c]
cal_hc_rkeys = dict(KW_EXT_TYPE='HCONE_HCONE')
cal_hc_files2 = spirouFile.add_required_keywords(cal_hc_files1, cal_hc_rkeys)
# set up arguments
cal_hc.arg(pos=0, **directory)
cal_hc.arg(name='files', dtype='files', pos='1+', files=cal_hc_files2,
           filelogic='exclusive', limit=1, helpstr=rd.HcE2DS.files_help)
cal_hc.kwarg(**add_cal)
cal_hc.kwarg(**plot)
cal_hc.kwarg(**blazefile)
cal_hc.kwarg(**flatfile)
cal_hc.kwarg(**wavefile)

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


# -----------------------------------------------------------------------------
# define valid recipes as a list
# -----------------------------------------------------------------------------

