from . import spirouRecipe
from . import spirouFiles

# =============================================================================
# Commonly used arguments
# =============================================================================
directory = dict(name='directory', dtype='directory',
                 helpstr='The "night_name" or absolute path of the directory')

# =============================================================================
# Commonly used options
# =============================================================================
combine = dict(name='--combine', dtype='bool',
               helpstr='Whether to combine fits files in file list or to '
                       'process them separately')

flipimage = dict(name='--flipimage', dtype='options',
                 helpstr='Whether to flip fits image',
                 options=['None', 'x', 'y', 'both'])

fluxunits = dict(name='--fluxunits', dtype='options',
                 helpstr='Output units for flux',
                 options=['ADU/s', 'e-'])

resize = dict(name='--resize', dtype='bool',
              helpstr='Whether to resize image')

plot = dict(name='--plot', dtype='bool', altnames=['-p'],
            helpstr='Manually turn on/off plot of graphs')

add_cal = dict(name='--add2calib', dtype='bool',
               helpstr='Whether to add outputs to calibration database')

darkfile = dict(name='--darkfile', dtype='file',
                files=[spirouFiles.dark_dark],
                helpstr='Define a custom file to use for dark correction'
                        ' Checks for an absolute path and then checks '
                        '"directory".')

badfile = dict(name='--badpixfile', dtype='file',
               helpstr='Define a custom file to use for bad pixel correction.'
                       ' Checks for an absolute path and then checks '
                       '"directory".')

dodark = dict(name='--darkcorr', dtype='bool',
              helpstr='Whether to correct for the dark file')

dobad = dict(name='--badcorr', dtype='bool',
             helpstr='Whether to correct for the bad pixel file')




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
cal_wave = drs_recipe()

test = drs_recipe()
# push into a list
recipes = [cal_badpix, cal_ccf, cal_dark, cal_drift1, cal_drift2, cal_extract,
           cal_ff, cal_hc, cal_loc, cal_pp, cal_slit, cal_wave,
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
test.inputdir = 'raw'
test.inputtype = 'pp'
test.extension = 'fits'
test.description = 'Test recipe - used to test the argument parser of the DRS'
test.arg(pos=0, **directory)
test.arg(pos=1, name='filelist', dtype='files', files=[spirouFiles.raw_file],
         helpstr='A list of fits files to use, separated by spaces')
test.kwarg(**plot)
test.kwarg(**combine)
test.kwarg(**flipimage)
test.kwarg(**fluxunits)
test.kwarg(**resize)
test.kwarg(**add_cal)
test.kwarg(**darkfile)
test.kwarg(**dodark)
test.kwarg(**badfile)
test.kwarg(**dobad)


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
cal_pp.arg(name='ufiles', dtype='infile', pos=1,
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
cal_badpix.arg(name='flatfile', key='flat_dark', dtype='infile', pos=1)
cal_badpix.arg(name='darkfile', key='dark_dark', dtype='infile', pos=2)
cal_badpix.kwarg(**plot)

# -----------------------------------------------------------------------------
# cal_dark_spirou
# -----------------------------------------------------------------------------
cal_dark.name = 'cal_DARK_spirou.py'
cal_dark.outputdir = 'reduced'
cal_dark.inputdir = 'tmp'
cal_dark.intputtype = 'pp'
cal_dark.run_order = 2
cal_dark.arg(name='directory', dtype='path', pos=0)
cal_dark.arg(name='files', key='dark_dark', dtype='infile', pos='1+')
cal_dark.kwarg(**plot)


# -----------------------------------------------------------------------------
# cal_loc_RAW_spirou
# -----------------------------------------------------------------------------
cal_loc.name = 'cal_loc_RAW_spirou.py'
cal_loc.outputdir = 'reduced'
cal_loc.inputdir = 'tmp'
cal_loc.inputtype = 'pp'
cal_loc.run_order = 3
cal_loc.arg(name='directory', dtype='path', pos=0)
cal_loc.arg(name='files', key='flat_dark', dtype='infile', pos='1+')
cal_loc.arg(name='files', key='dark_flat', dtype='infile', pos='1+')
cal_loc.kwarg(name='DARK_FILE', dtype='outfile',
              helpstr='Force a dark file [file/path]')
cal_loc.kwarg(**plot)

# -----------------------------------------------------------------------------
# cal_SLIT_spirou
# -----------------------------------------------------------------------------
cal_slit.name = 'cal_SLIT_spirou.py'
cal_slit.outputdir = 'reduced'
cal_slit.inputdir = 'tmp'
cal_slit.inputtype = 'pp'
cal_slit.run_order = 4
cal_slit.arg(name='directory', dtype='path', pos=0)
cal_slit.arg(name='files', key='fp_fp', dtype='infile', pos='1+')
cal_slit.kwarg(**plot)

# -----------------------------------------------------------------------------
# cal_FF_RAW_spirou
# -----------------------------------------------------------------------------
cal_ff.name = 'cal_FF_RAW_spirou.py'
cal_ff.outputdir = 'reduced'
cal_ff.inputdir = 'tmp'
cal_ff.inputtype = 'pp'
cal_ff.run_order = 5
cal_ff.arg(name='directory', dtype='path', pos=0)
cal_ff.arg(name='files', key='flat_flat', dtype='infile', pos='1+')
cal_ff.arg(name='files', key='flat_dark', dtype='infile', pos='1+')
cal_ff.arg(name='files', key='dark_flat', dtype='infile', pos='1+')
cal_ff.kwarg(**plot)

# -----------------------------------------------------------------------------
# cal_extract_RAW_spirou
# -----------------------------------------------------------------------------
cal_extract.name = 'cal_extract_RAW_spirou.py'
cal_extract.outputdir = 'reduced'
cal_extract.inputdir = 'tmp'
cal_extract.inputtype = 'pp'
cal_extract.run_order = 6
cal_extract.arg(name='directory', dtype='path', pos=0)
cal_extract.arg(name='files', dtype=str, pos='1+')
cal_extract.kwarg(name='fiber', dtype=str)
cal_extract.kwarg(**plot)

# -----------------------------------------------------------------------------
# cal_HC_E2DS_spirou
# -----------------------------------------------------------------------------
cal_hc.name = 'cal_HC_E2DS_spirou.py'
cal_hc.outputdir = 'reduced'
cal_hc.inputdir = 'reduced'
cal_hc.inputtype = 'reduced'
cal_hc.run_order = 7
cal_hc.arg(name='directory', dtype='path', pos=0)
cal_hc.arg(name='files', dtype='outfile', pos='1+')
cal_hc.arg(name='files', dtype='outfile', pos='1+')
cal_hc.kwarg(**plot)

# -----------------------------------------------------------------------------
# cal_WAVE_E2DS_spirou
# -----------------------------------------------------------------------------
cal_wave.name = 'cal_WAVE_E2DS_spirou.py'
cal_wave.outputdir = 'reduced'
cal_wave.inputdir = 'reduced'
cal_wave.inputtype = 'reduced'
cal_wave.run_order = 8
cal_wave.arg(name='directory', dtype='path', pos=0)
cal_wave.arg(name='fpfile', key1='EXTRACT_E2DS_FILE', key2='FP_FP',
             dtype='outfile', pos=1)
cal_wave.arg(name='fpfile', key1='EXTRACT_E2DSFF_FILE', key2='FP_FP',
             dtype='outfile', pos=1)
cal_wave.arg(name='hcfiles', key1='EXTRACT_E2DS_FILE', key2='HCONE_HCONE',
             dtype='outfile', pos='2+')
cal_wave.arg(name='hcfiles', key1='EXTRACT_E2DSFF_FILE', key2='HCONE_HCONE',
             dtype='outfile', pos='2+')
cal_wave.kwarg(**plot)

# -----------------------------------------------------------------------------
# cal_DRIFT_E2DS_spirou
# -----------------------------------------------------------------------------
cal_drift1.name = 'cal_DRIFT_E2DS_spirou.py'
cal_drift1.outputdir = 'reduced'
cal_drift1.inputdir = 'reduced'
cal_drift1.inputtype = 'reduced'
cal_drift1.run_order = 9
cal_drift1.arg(name='directory', dtype='path', pos=0)
cal_drift1.arg(name='reffile', key1='EXTRACT_E2DS_FILE', key2='FP_FP',
               dtype='outfile', pos=1)
cal_drift1.arg(name='reffile', key1='EXTRACT_E2DSFF_FILE', key2='FP_FP',
               dtype='outfile', pos=1)
cal_drift1.arg(name='reffile', key1='EXTRACT_E2DS_FILE', key2='HCONE_HCONE',
               dtype='outfile', pos=1)
cal_drift1.arg(name='reffile', key1='EXTRACT_E2DSFF_FILE', key2='HCONE_HCONE',
               dtype='outfile', pos=1)
cal_drift1.kwarg(**plot)

# -----------------------------------------------------------------------------
# cal_DRIFTPEAK_E2DS_spirou
# -----------------------------------------------------------------------------
cal_drift2.name = 'cal_DRIFTPEAK_E2DS_spirou.py'
cal_drift2.outputdir = 'reduced'
cal_drift2.inputdir = 'reduced'
cal_drift2.inputtype = 'reduced'
cal_drift2.run_order = 10
cal_drift2.arg(name='directory', dtype='path', pos=0)
cal_drift2.arg(name='reffile', key1='EXTRACT_E2DS_FILE', key2='FP_FP',
               dtype='outfile', pos=1)
cal_drift2.arg(name='reffile', key1='EXTRACT_E2DSFF_FILE', key2='FP_FP',
               dtype='outfile', pos=1)
cal_drift2.arg(name='reffile', key1='EXTRACT_E2DS_FILE', key2='HCONE_HCONE',
               dtype='outfile', pos=1)
cal_drift2.arg(name='reffile', key1='EXTRACT_E2DSFF_FILE', key2='HCONE_HCONE',
               dtype='outfile', pos=1)
cal_drift2.kwarg(**plot)

# -----------------------------------------------------------------------------
# cal_CCF_E2DS_spirou
# -----------------------------------------------------------------------------
cal_ccf.name = 'cal_CCF_E2DS_spirou.py'
cal_ccf.outputdir = 'reduced'
cal_ccf.inputdir = 'reduced'
cal_ccf.inputtype = 'reduced'
cal_ccf.run_order = 11
cal_ccf.arg(name='directory', dtype='path', pos=0)
cal_ccf.arg(name='e2dsfile', key1='EXTRACT_E2DS_FILE', dtype='outfile', pos=1)
cal_ccf.arg(name='e2dsfile', key1='EXTRACT_E2DSFF_FILE', dtype='outfile', pos=1)
cal_ccf.arg(name='e2dsfile', key1='TELLU_CORRECTED', dtype='outfile', pos=1)
cal_ccf.arg(name='e2dsfile', key1='TELLU_CORRECTED', dtype='outfile', pos=1)
cal_ccf.arg(name='e2dsfile', key1='POL_DEG', dtype='outfile', pos=1)
cal_ccf.arg(name='e2dsfile', key1='POL_STOKES_I', dtype='outfile', pos=1)
cal_ccf.arg(name='e2dsfile', key1='POL_LSD', dtype='outfile', pos=1)
cal_ccf.arg(name='mask', dtype='str', pos=2)
cal_ccf.arg(name='rv', dtype=float, pos=3)
cal_ccf.arg(name='width', dtype=float, pos=4)
cal_ccf.arg(name='step', dtype=float, pos=5)
cal_ccf.kwarg(**plot)

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

