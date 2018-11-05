from . import spirouRecipe
from . import files_spirou as sf

# =============================================================================
# Commonly used arguments
# =============================================================================
directory = dict(name='directory', dtype='directory',
                 helpstr='The "night_name" or absolute path of the directory')

# =============================================================================
# Commonly used options
# =============================================================================

add_cal = dict(name='--add2calib', dtype='bool',
               helpstr='Whether to add outputs to calibration database')
dobad = dict(name='--badcorr', dtype='bool',
             helpstr='Whether to correct for the bad pixel file')
badfile = dict(name='--badpixfile', dtype='file',
               files=[sf.out_badpix],
               helpstr='Define a custom file to use for bad pixel correction.'
                       ' Checks for an absolute path and then checks '
                       '"directory".')
backsub = dict(name='--backsub', dtype='bool',
               helpstr='Whether to do background subtraction')
combine = dict(name='--combine', dtype='bool',
               helpstr='Whether to combine fits files in file list or to '
                       'process them separately')
dodark = dict(name='--darkcorr', dtype='bool',
              helpstr='Whether to correct for the dark file')
darkfile = dict(name='--darkfile', dtype='file',
                files=[sf.out_dark],
                helpstr='Define a custom file to use for dark correction'
                        ' Checks for an absolute path and then checks '
                        '"directory".')
extractmethod = dict(name='--extractmethod', dtype='options',
                     helpstr='Define a custom extraction method',
                     options=['1', '2', '3a', '3b', '3c', '3d', '4a', '4b'])
extfiber = dict(name='--extfiber', dtype='options',
                helpstr='Define which fibers to extract',
                options=['ALL', 'AB', 'A', 'B', 'C'])
flipimage = dict(name='--flipimage', dtype='options',
                 helpstr='Whether to flip fits image',
                 options=['None', 'x', 'y', 'both'])

fluxunits = dict(name='--fluxunits', dtype='options',
                 helpstr='Output units for flux',
                 options=['ADU/s', 'e-'])
plot = dict(name='--plot', dtype='bool', altnames=['-p'],
            helpstr='Manually turn on/off plot of graphs')
resize = dict(name='--resize', dtype='bool',
              helpstr='Whether to resize image')
shapefile = dict(name='--tiltfile', dtype='file',
                 files=[sf.out_silt_shape],
                 helpstr='Define a custom file to use for tilt correction.'
                         ' Checks for an absolute path and then checks '
                         '"directory".')
tiltfile = dict(name='--tiltfile', dtype='file',
                files=[sf.out_slit_tilt],
                helpstr='Define a custom file to use for tilt correction.'
                        ' Checks for an absolute path and then checks '
                        '"directory".')

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
# test.py
# -----------------------------------------------------------------------------
test.name = 'test.py'
test.outputdir = 'tmp'
test.inputdir = 'tmp'
test.inputtype = 'pp'
test.extension = 'fits'
test.description = 'Test recipe - used to test the argument parser of the DRS'
test.arg(pos=0, **directory)
test.arg(pos=1, name='filelist', dtype='files',
         files=[sf.pp_dark_dark, sf.pp_flat_flat],
         filelogic='exclusive',
         helpstr='A list of fits files to use, separated by spaces')
test.kwarg(**plot)
test.kwarg(**add_cal)
test.kwarg(**dobad)
test.kwarg(**badfile)
test.kwarg(**combine)
test.kwarg(**dodark)
test.kwarg(**darkfile)
test.kwarg(**flipimage)
test.kwarg(**fluxunits)
test.kwarg(**resize)

# -----------------------------------------------------------------------------
# cal_preprocess_spirou
# -----------------------------------------------------------------------------
cal_pp.name = 'cal_preprocess_spirou.py'
cal_pp.outputdir = 'tmp'
cal_pp.inputdir = 'raw'
cal_pp.inputtype = 'raw'
cal_pp.description = 'Pre-processing recipe'
cal_pp.arg(name='directory', dtype='directory', pos=0,
           helpstr='- The "night_name" or absolute directory path')
cal_pp.arg(name='ufiles', dtype='files', pos=1,
           helpstr='- The fits files to use, separated by spaces')
cal_pp.kwarg(**plot)

# -----------------------------------------------------------------------------
# cal_badpix_spirou
# -----------------------------------------------------------------------------
cal_badpix.name = 'cal_badpix_spirou.py'
cal_badpix.outputdir = 'reduced'
cal_badpix.inputdir = 'tmp'
cal_badpix.inputtype = 'pp'
cal_badpix.run_order = 1
cal_badpix.arg(name='directory', dtype='directory', pos=0)
cal_badpix.arg(name='flatfile', dtype='files', files=[sf.pp_flat_flat], pos=1)
cal_badpix.arg(name='darkfile', dtype='files', files=[sf.pp_dark_dark], pos=2)
cal_badpix.kwarg(**add_cal)
cal_badpix.kwarg(**badfile)
cal_badpix.kwarg(**dobad)
cal_badpix.kwarg(**combine)
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
cal_dark.outputdir = 'reduced'
cal_dark.inputdir = 'tmp'
cal_dark.intputtype = 'pp'
cal_dark.run_order = 2
cal_dark.arg(name='directory', dtype='directory', pos=0)
cal_dark.arg(name='files', dtype='files', files=[sf.pp_dark_dark], pos='1+')
cal_dark.kwarg(**add_cal)
cal_dark.kwarg(**combine)
cal_dark.kwarg(**flipimage)
cal_dark.kwarg(**fluxunits)
cal_dark.kwarg(**plot)
cal_dark.kwarg(**resize)

# -----------------------------------------------------------------------------
# cal_loc_RAW_spirou
# -----------------------------------------------------------------------------
cal_loc.name = 'cal_loc_RAW_spirou.py'
cal_loc.outputdir = 'reduced'
cal_loc.inputdir = 'tmp'
cal_loc.inputtype = 'pp'
cal_loc.run_order = 3
cal_loc.arg(name='directory', dtype='directory', pos=0)
cal_loc.arg(name='files', dtype='files', filelogic='exclusive',
            files=[sf.pp_dark_flat, sf.pp_flat_dark], pos='1+')
cal_loc.kwarg(**add_cal)
cal_loc.kwarg(**badfile)
cal_loc.kwarg(**dobad)
cal_loc.kwarg(**backsub)
cal_loc.kwarg(**combine)
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
cal_slit.outputdir = 'reduced'
cal_slit.inputdir = 'tmp'
cal_slit.inputtype = 'pp'
cal_slit.run_order = 4
cal_slit.arg(name='directory', dtype='directory', pos=0)
cal_slit.arg(name='files', dtype='files', files=[sf.pp_fp_fp], pos='1+')
cal_slit.kwarg(**add_cal)
cal_slit.kwarg(**badfile)
cal_slit.kwarg(**dobad)
cal_slit.kwarg(**backsub)
cal_slit.kwarg(**combine)
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
cal_shape.outputdir = 'reduced'
cal_shape.inputdir = 'tmp'
cal_shape.inputtype = 'pp'
cal_shape.run_order = 4
cal_shape.arg(name='directory', dtype='directory', pos=0)
cal_shape.arg(name='files', dtype='files', files=[sf.pp_fp_fp], pos='1+')
cal_shape.kwarg(**add_cal)
cal_shape.kwarg(**badfile)
cal_shape.kwarg(**dobad)
cal_shape.kwarg(**backsub)
cal_shape.kwarg(**combine)
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
cal_ff.outputdir = 'reduced'
cal_ff.inputdir = 'tmp'
cal_ff.inputtype = 'pp'
cal_ff.run_order = 5
cal_ff.arg(name='directory', dtype='directory', pos=0)
cal_ff.arg(name='files', dtype='files', filelogic='exclusive',
           files=[sf.pp_flat_flat, sf.pp_dark_flat, sf.pp_flat_dark], pos='1+')
cal_ff.kwarg(**add_cal)
cal_ff.kwarg(**badfile)
cal_ff.kwarg(**dobad)
cal_ff.kwarg(**backsub)
cal_ff.kwarg(**combine)
cal_ff.kwarg(**darkfile)
cal_ff.kwarg(**dodark)
cal_ff.kwarg(**extractmethod)
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
cal_extract.outputdir = 'reduced'
cal_extract.inputdir = 'tmp'
cal_extract.inputtype = 'pp'
cal_extract.run_order = 6
cal_extract.arg(name='directory', dtype='directory', pos=0)
cal_extract.arg(name='files', dtype='files', pos='1+', files=[sf.pp_file])
cal_extract.kwarg(**add_cal)
cal_extract.kwarg(**badfile)
cal_extract.kwarg(**dobad)
cal_extract.kwarg(**backsub)
cal_extract.kwarg(**combine)
cal_extract.kwarg(**darkfile)
cal_extract.kwarg(**dodark)
cal_extract.kwarg(**extractmethod)
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
# cal_hc.outputdir = 'reduced'
# cal_hc.inputdir = 'reduced'
# cal_hc.inputtype = 'reduced'
# cal_hc.run_order = 7
# cal_hc.arg(name='directory', dtype='directory', pos=0)
# cal_hc.arg(name='files', dtype='files', pos='1+')
# cal_hc.arg(name='files', dtype='files', pos='1+')
# cal_hc.kwarg(**plot)

# -----------------------------------------------------------------------------
# cal_WAVE_E2DS_spirou
# -----------------------------------------------------------------------------
cal_wave.name = 'cal_WAVE_E2DS_spirou.py'
# cal_wave.outputdir = 'reduced'
# cal_wave.inputdir = 'reduced'
# cal_wave.inputtype = 'reduced'
# cal_wave.run_order = 8
# cal_wave.arg(name='directory', dtype='directory', pos=0)
# cal_wave.arg(name='fpfile', key1='EXTRACT_E2DS_FILE', key2='FP_FP',
#              dtype='files', pos=1)
# cal_wave.arg(name='fpfile', key1='EXTRACT_E2DSFF_FILE', key2='FP_FP',
#              dtype='files', pos=1)
# cal_wave.arg(name='hcfiles', key1='EXTRACT_E2DS_FILE', key2='HCONE_HCONE',
#              dtype='files', pos='2+')
# cal_wave.arg(name='hcfiles', key1='EXTRACT_E2DSFF_FILE', key2='HCONE_HCONE',
#              dtype='files', pos='2+')
# cal_wave.kwarg(**plot)

# -----------------------------------------------------------------------------
# cal_DRIFT_E2DS_spirou
# -----------------------------------------------------------------------------
cal_drift1.name = 'cal_DRIFT_E2DS_spirou.py'
cal_drift1.outputdir = 'reduced'
cal_drift1.inputdir = 'reduced'
cal_drift1.inputtype = 'reduced'
cal_drift1.run_order = 9
# cal_drift1.arg(name='directory', dtype='directory', pos=0)
# cal_drift1.arg(name='reffile', key1='EXTRACT_E2DS_FILE', key2='FP_FP',
#                dtype='files', pos=1)
# cal_drift1.arg(name='reffile', key1='EXTRACT_E2DSFF_FILE', key2='FP_FP',
#                dtype='files', pos=1)
# cal_drift1.arg(name='reffile', key1='EXTRACT_E2DS_FILE', key2='HCONE_HCONE',
#                dtype='files', pos=1)
# cal_drift1.arg(name='reffile', key1='EXTRACT_E2DSFF_FILE', key2='HCONE_HCONE',
#                dtype='files', pos=1)
# cal_drift1.kwarg(**plot)

# -----------------------------------------------------------------------------
# cal_DRIFTPEAK_E2DS_spirou
# -----------------------------------------------------------------------------
cal_drift2.name = 'cal_DRIFTPEAK_E2DS_spirou.py'
cal_drift2.outputdir = 'reduced'
cal_drift2.inputdir = 'reduced'
cal_drift2.inputtype = 'reduced'
cal_drift2.run_order = 10
# cal_drift2.arg(name='directory', dtype='directory', pos=0)
# cal_drift2.arg(name='reffile', key1='EXTRACT_E2DS_FILE', key2='FP_FP',
#                dtype='files', pos=1)
# cal_drift2.arg(name='reffile', key1='EXTRACT_E2DSFF_FILE', key2='FP_FP',
#                dtype='files', pos=1)
# cal_drift2.arg(name='reffile', key1='EXTRACT_E2DS_FILE', key2='HCONE_HCONE',
#                dtype='files', pos=1)
# cal_drift2.arg(name='reffile', key1='EXTRACT_E2DSFF_FILE', key2='HCONE_HCONE',
#                dtype='files', pos=1)
# cal_drift2.kwarg(**plot)

# -----------------------------------------------------------------------------
# cal_CCF_E2DS_spirou
# -----------------------------------------------------------------------------
cal_ccf.name = 'cal_CCF_E2DS_spirou.py'
cal_ccf.outputdir = 'reduced'
cal_ccf.inputdir = 'reduced'
cal_ccf.inputtype = 'reduced'
cal_ccf.run_order = 11
# cal_ccf.arg(name='directory', dtype='directory', pos=0)
# cal_ccf.arg(name='e2dsfile', key1='EXTRACT_E2DS_FILE', dtype='files', pos=1)
# cal_ccf.arg(name='e2dsfile', key1='EXTRACT_E2DSFF_FILE', dtype='files', pos=1)
# cal_ccf.arg(name='e2dsfile', key1='TELLU_CORRECTED', dtype='files', pos=1)
# cal_ccf.arg(name='e2dsfile', key1='TELLU_CORRECTED', dtype='files', pos=1)
# cal_ccf.arg(name='e2dsfile', key1='POL_DEG', dtype='files', pos=1)
# cal_ccf.arg(name='e2dsfile', key1='POL_STOKES_I', dtype='files', pos=1)
# cal_ccf.arg(name='e2dsfile', key1='POL_LSD', dtype='files', pos=1)
# cal_ccf.arg(name='mask', dtype=str, pos=2)
# cal_ccf.arg(name='rv', dtype=float, pos=3)
# cal_ccf.arg(name='width', dtype=float, pos=4)
# cal_ccf.arg(name='step', dtype=float, pos=5)
# cal_ccf.kwarg(**plot)

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

