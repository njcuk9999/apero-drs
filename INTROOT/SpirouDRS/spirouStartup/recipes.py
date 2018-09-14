from . import spirouRecipe

# =============================================================================
# Define variables
# =============================================================================
drs_recipe = spirouRecipe.DrsRecipe

# =============================================================================
# List of usable recipes
# =============================================================================
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
# push into a list
recipes = [cal_badpix, cal_ccf, cal_dark, cal_drift1, cal_drift2, cal_extract,
           cal_ff, cal_hc, cal_loc, cal_pp, cal_slit, cal_wave]

# =============================================================================
# Add inputs below
# =============================================================================
# This section is for defining the inputs arguments and keywords and
#    outputs of the recipes. Steps that need to be followed are:
#
#    1)  setup the recipe with a call to "drs_recipe()"
#                  >> my_recipe = drs_recipe()
#
#    2)  give the recipe filename (and __NAME__) with
#                  >> my_recipe.name = "my_name.py"
#
#    3)  give the recipe an output dir
#          - default is "reduced"
#          - options are ["reduced", "raw", "tmp"] or a valid path
#                  >> my_recipe.outputdir = "reduced"
#
#    4)  give the recipe an input dir
#          - default is "tmp"
#          - options are ["reduced", "raw", "tmp"] or a valid path
#                  >> my_recipe.inputdir = "tmp"
#
#    5)  give the recipe an input type
#          - default is "raw"
#          - options are ["raw", "pp", "reduced", None]
#                  >> my_recipe.inputtype = "raw"
#
#    6)  give the recipe a run order (for deciding the order to run in triggers)
#          - default is None
#          - options are [None, 0, 1, 2, ...]  - any valid positive integer
#                  >> my_recipe.run_order = 0
#
#    7)  give the recipe some arguments/keyword arguments
#          - default is no arguments
#          - options within an argument are:
#                 :name: string or None, the name and reference of the argument
#                 :dtype: string, type or None: the type of an argument
#                          if string must be ["infile", "outfile"] if type
#                          error will be raised, if None not checked
#                 :pos: int, the expected position of the argument in the
#                       call to the recipe or function (only for arguments
#                       not keyword arguments)
#                 :helpstr: string or None, the help string related to this
#                           argument
#              >> my_recipe.arg(name='Arg1', dtype=str, pos=0)
#              >> my_recipe.kwarg(name='plot', dtype=bool)
# comment help files
plothelp = 'Plot graphs: True/1, Do not plot graphs: False/0'

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
cal_pp.kwarg(name='-plot', dtype='bool',
             helpstr='- Manually turn on/off plotting (True/False/1/0)')
cal_pp.kwarg(name='--plotoff', dtype='switch',
             helpstr='- Force plotting to be off')
cal_pp.kwarg(name='--ploton', dtype='switch',
             helpstr='- Force plotting to be on')
# -----------------------------------------------------------------------------
# cal_badpix_spirou
# -----------------------------------------------------------------------------
cal_badpix.name = 'cal_badpix_spirou.py'
cal_badpix.outputdir = 'reduced'
cal_badpix.inputdir = 'tmp'
cal_badpix.inputtype = 'pp'
cal_badpix.run_order = 1
cal_badpix.arg(name='directory', dtype='path', pos=0)
cal_badpix.arg(name='flatfile', key='flat_dark', dtype='infile', pos=1)
cal_badpix.arg(name='darkfile', key='dark_dark', dtype='infile', pos=2)
cal_badpix.kwarg(name='-plot', dtype='bool',
                 helpstr='- Manually turn on/off plotting (True/False/1/0)')
cal_badpix.kwarg(name='--plotoff', dtype='switch',
                 helpstr='- Force plotting to be off')
cal_badpix.kwarg(name='--ploton', dtype='switch',
                 helpstr='- Force plotting to be on')

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
cal_dark.kwarg(name='-plot', dtype='bool',
               helpstr='- Manually turn on/off plotting (True/False/1/0)')
cal_dark.kwarg(name='--plotoff', dtype='switch',
               helpstr='- Force plotting to be off')
cal_dark.kwarg(name='--ploton', dtype='switch',
               helpstr='- Force plotting to be on')

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
cal_loc.kwarg(name='plot', dtype=bool, helpstr=plothelp)

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
cal_slit.kwarg(name='plot', dtype=bool, helpstr=plothelp)

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
cal_badpix.kwarg(name='plot', dtype=bool, helpstr=plothelp)

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
cal_extract.kwarg(name='plot', dtype=bool, helpstr=plothelp)

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
cal_hc.kwarg(name='plot', dtype=bool, helpstr=plothelp)

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
cal_wave.kwarg(name='plot', dtype=bool, helpstr=plothelp)

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
cal_drift1.kwarg(name='plot', dtype=bool, helpstr=plothelp)

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
cal_drift2.kwarg(name='plot', dtype=bool, helpstr=plothelp)

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
cal_ccf.kwarg(name='plot', dtype=bool, helpstr=plothelp)

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

