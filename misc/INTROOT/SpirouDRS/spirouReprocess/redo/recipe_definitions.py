#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-06-10 at 13:38

@author: cook
"""
from __future__ import division

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore

from . import file_definitions as sf

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'recipe_definitions.py'
__INSTRUMENT__ = 'SPIROU'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt
# Get param dictionary
ParamDict = spirouConfig.ParamDict


# =============================================================================
# TODO: replace with apero
# Define proxy classes (from input_redo)
# =============================================================================
class Helper:
    """
    Proxy class to avoid changes below
    """

    def __init__(self):
        pass

    def __getitem__(self, item):
        return item


class DrsRecipe:
    def __init__(self, instrument):
        self.instrument = instrument
        self.name = 'Unknown'
        self.args = dict()

    def arg(self, **kwargs):
        self.args[kwargs['name']] = dict()
        for kwarg in kwargs:
            self.args[kwargs['name']][kwarg] = kwargs[kwarg]

    def kwarg(self, **kwargs):
        self.arg(**kwargs)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return 'DrsRecipe[{0}]'.format(self.name)


# =============================================================================
# TODO: replace with apero
# Define proxy variables
# =============================================================================
Help = Helper()
drs_recipe = DrsRecipe
drs_file = sf.DrsFile

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
# Must set default_ref per recipe!!
extractmethod = dict(name='--extractmethod', dtype='options',
                     helpstr=Help['EXTRACT_METHOD_HELP'],
                     options=['1', '2', '3a', '3b', '3c', '3d', '4a', '4b'])
# -----------------------------------------------------------------------------
extfiber = dict(name='--extfiber', dtype='options', default='ALL',
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

# =============================================================================
# File option definitions
# =============================================================================
badfile = dict(name='--badpixfile', dtype='file', default='None',
               files=[sf.out_badpix],
               helpstr=Help['BADFILE_HELP'])
# -----------------------------------------------------------------------------
blazefile = dict(name='--blazefile', dtype='file', default='None',
                 files=[sf.out_ff_blaze_ab, sf.out_ff_blaze_a,
                        sf.out_ff_blaze_b, sf.out_ff_blaze_c],
                 helpstr=Help['BLAZEFILE_HELP'])
# -----------------------------------------------------------------------------
darkfile = dict(name='--darkfile', dtype='file', default='None',
                files=[sf.out_dark],
                helpstr=Help['DARKFILE_HELP'])
# -----------------------------------------------------------------------------
flatfile = dict(name='--flatfile', dtype='file', default='None',
                files=[sf.out_ff_flat_ab, sf.out_ff_flat_a,
                       sf.out_ff_flat_b, sf.out_ff_flat_c],
                helpstr=Help['FLATFILE_HELP'])
# -----------------------------------------------------------------------------
shapefile = dict(name='--shapefile', dtype='file', default='None',
                 files=[sf.out_silt_shape],
                 helpstr=Help['SHAPEFILE_HELP'])
# -----------------------------------------------------------------------------
tiltfile = dict(name='--tiltfile', dtype='file', default='None',
                files=[sf.out_slit_tilt],
                helpstr=Help['TILTFILE_HELP'])
# -----------------------------------------------------------------------------
wavefile = dict(name='--wavefile', dtype='file', default='None',
                files=[sf.out_wave_ab, sf.out_wave_a,
                       sf.out_wave_b, sf.out_wave_c],
                helpstr=Help['WAVEFILE_HELP'])

# =============================================================================
# List of usable recipes
# =============================================================================
# TODO: add back in
# drs_recipe = drs_recipe.DrsRecipe

# Below one must define all recipes and put into the "recipes" list
cal_badpix = drs_recipe(__INSTRUMENT__)
cal_ccf = drs_recipe(__INSTRUMENT__)
cal_dark = drs_recipe(__INSTRUMENT__)
cal_dark_master = drs_recipe(__INSTRUMENT__)
cal_drift1 = drs_recipe(__INSTRUMENT__)
cal_drift2 = drs_recipe(__INSTRUMENT__)
cal_extract = drs_recipe(__INSTRUMENT__)
cal_ff = drs_recipe(__INSTRUMENT__)
cal_thermal = drs_recipe(__INSTRUMENT__)
cal_hc = drs_recipe(__INSTRUMENT__)
cal_loc = drs_recipe(__INSTRUMENT__)
cal_pp = drs_recipe(__INSTRUMENT__)
cal_slit = drs_recipe(__INSTRUMENT__)
cal_shape = drs_recipe(__INSTRUMENT__)
cal_shape_master = drs_recipe(__INSTRUMENT__)
cal_wave = drs_recipe(__INSTRUMENT__)
obj_fit_tellu = drs_recipe(__INSTRUMENT__)
obj_mk_tellu = drs_recipe(__INSTRUMENT__)
obj_fit_tellu_db = drs_recipe(__INSTRUMENT__)
obj_mk_tellu_db = drs_recipe(__INSTRUMENT__)

test = drs_recipe(__INSTRUMENT__)
# push into a list
recipes = [cal_badpix, cal_ccf, cal_dark, cal_dark_master,
           cal_drift1, cal_drift2, cal_thermal,
           cal_extract, cal_ff, cal_hc, cal_loc, cal_pp,
           cal_slit, cal_shape, cal_shape_master,
           cal_wave, obj_fit_tellu, obj_mk_tellu, obj_fit_tellu_db,
           obj_mk_tellu_db,
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
test.kwarg(name='-filelist1', dtype='files', default=[], nargs='+',
           files=[sf.pp_dark_dark, sf.pp_flat_flat], filelogic='inclusive',
           helpstr=Help['TEST_FILELIST1_HELP'], required=True)
test.kwarg(name='-filelist2', dtype='files', default=[], nargs='+',
           files=[sf.pp_fp_fp], helpstr=Help['TEST_FILELIST2_HELP'],
           required=True)
test.kwarg(**plot)
test.kwarg(**interactive)
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
cal_pp.instrument = __INSTRUMENT__
cal_pp.outputdir = 'tmp'
cal_pp.inputdir = 'raw'
cal_pp.inputtype = 'raw'
cal_pp.extension = 'fits'
cal_pp.description = Help['PREPROCESS_DESC']
cal_pp.epilog = Help['PREPROCESS_EXAMPLE']
cal_pp.arg(pos=0, **directory)
cal_pp.arg(name='ufiles', dtype='files', pos='1+', files=[sf.raw_file],
           helpstr=Help['PREPROCESS_UFILES_HELP'], limit=1)

# -----------------------------------------------------------------------------
# cal_badpix_spirou
# -----------------------------------------------------------------------------
cal_badpix.name = 'cal_BADPIX_spirou.py'
cal_badpix.instrument = __INSTRUMENT__
cal_badpix.outputdir = 'reduced'
cal_badpix.inputdir = 'tmp'
cal_badpix.inputtype = 'pp'
cal_badpix.extension = 'fits'
cal_badpix.description = Help['BADPIX_DESC']
cal_badpix.epilog = Help['BADPIX_EXAMPLE']
cal_badpix.run_order = 1
cal_badpix.arg(pos=0, **directory)
cal_badpix.kwarg(name='-flatfile', dtype='files', files=[sf.pp_flat_flat],
                 nargs='+', filelogic='exclusive', required=True,
                 helpstr=Help['BADPIX_FLATFILE_HELP'], default=[])
cal_badpix.kwarg(name='-darkfile', dtype='files', files=[sf.pp_dark_dark],
                 nargs='+', filelogic='exclusive', required=True,
                 helpstr=Help['BADPIX_DARKFILE_HELP'], default=[])
cal_badpix.kwarg(**add_cal)
cal_badpix.kwarg(default=True, **combine)
cal_badpix.kwarg(**flipimage)
cal_badpix.kwarg(**fluxunits)
cal_badpix.kwarg(**plot)
cal_badpix.kwarg(**interactive)
cal_badpix.kwarg(**resize)

# -----------------------------------------------------------------------------
# cal_dark_spirou
# -----------------------------------------------------------------------------
cal_dark.name = 'cal_dark_spirou.py'
cal_dark.instrument = __INSTRUMENT__
cal_dark.outputdir = 'reduced'
cal_dark.inputdir = 'tmp'
cal_dark.intputtype = 'pp'
cal_dark.extension = 'fits'
cal_dark.description = Help['DARK_DESC']
cal_dark.epilog = Help['DARK_EXAMPLE']
cal_dark.run_order = 2
cal_dark.arg(pos=0, **directory)
cal_dark.arg(name='files', dtype='files', files=[sf.pp_dark_dark], pos='1+',
             helpstr=Help['FILES_HELP'] + Help['DARK_FILES_HELP'])
cal_dark.kwarg(**add_cal)
cal_dark.kwarg(default=True, **combine)
cal_dark.kwarg(**flipimage)
cal_dark.kwarg(**fluxunits)
cal_dark.kwarg(**plot)
cal_dark.kwarg(**interactive)
cal_dark.kwarg(**resize)

# -----------------------------------------------------------------------------
# cal_dark_master_spirou
# -----------------------------------------------------------------------------
cal_dark_master.name = 'cal_dark_master_spirou.py'
cal_dark_master.instrument = __INSTRUMENT__
cal_dark_master.outputdir = 'reduced'
cal_dark_master.inputdir = 'tmp'
cal_dark_master.intputtype = 'pp'
cal_dark_master.extension = 'fits'
cal_dark_master.description = Help['DARK_DESC']
cal_dark_master.epilog = Help['DARK_EXAMPLE']
cal_dark_master.run_order = 2
cal_dark_master.kwarg(**add_cal)
cal_dark_master.kwarg(default=True, **combine)
cal_dark_master.kwarg(**flipimage)
cal_dark_master.kwarg(**fluxunits)
cal_dark_master.kwarg(**plot)
cal_dark_master.kwarg(**interactive)
cal_dark_master.kwarg(**resize)

# -----------------------------------------------------------------------------
# cal_loc_RAW_spirou
# -----------------------------------------------------------------------------
cal_loc.name = 'cal_loc_RAW_spirou.py'
cal_loc.instrument = __INSTRUMENT__
cal_loc.outputdir = 'reduced'
cal_loc.inputdir = 'tmp'
cal_loc.inputtype = 'pp'
cal_loc.extension = 'fits'
cal_loc.description = Help['LOC_DESC']
cal_loc.epilog = Help['LOC_EXAMPLE']
cal_loc.run_order = 3
cal_loc.arg(pos=0, **directory)
cal_loc.arg(name='files', dtype='files', filelogic='exclusive',
            files=[sf.pp_dark_flat, sf.pp_flat_dark], pos='1+',
            helpstr=Help['FILES_HELP'] + Help['LOC_FILES_HELP'])
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
cal_loc.kwarg(**interactive)
cal_loc.kwarg(**resize)

# -----------------------------------------------------------------------------
# cal_SLIT_spirou
# -----------------------------------------------------------------------------
cal_slit.name = 'cal_SLIT_spirou.py'
cal_slit.instrument = __INSTRUMENT__
cal_slit.outputdir = 'reduced'
cal_slit.inputdir = 'tmp'
cal_slit.inputtype = 'pp'
cal_slit.extension = 'fits'
cal_slit.description = Help['SLIT_DESC']
cal_slit.epilog = Help['SLIT_EXAMPLE']
cal_slit.run_order = 4
cal_slit.arg(pos=0, **directory)
cal_slit.arg(name='files', dtype='files', files=[sf.pp_fp_fp], pos='1+',
             helpstr=Help['FILES_HELP'] + Help['SLIT_FILES_HELP'])
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
cal_slit.kwarg(**interactive)
cal_slit.kwarg(**resize)

# -----------------------------------------------------------------------------
# cal_SHAPE_spirou
# -----------------------------------------------------------------------------
cal_shape.name = 'cal_shape_spirou.py'
cal_shape.instrument = __INSTRUMENT__
cal_shape.outputdir = 'reduced'
cal_shape.inputdir = 'tmp'
cal_shape.inputtype = 'pp'
cal_shape.extension = 'fits'
cal_shape.description = Help['SHAPE_DESC']
cal_shape.epilog = Help['SHAPE_EXAMPLE']
cal_shape.run_order = 4
cal_shape.arg(pos=0, **directory)
cal_shape.arg(name='files', dtype='files', files=[sf.pp_fp_fp], pos='1+',
              helpstr=Help['SHAPE_FPFILES_HELP'])
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
cal_shape.kwarg(**interactive)
cal_shape.kwarg(**resize)

# -----------------------------------------------------------------------------
# cal_shape_master_spirou
# -----------------------------------------------------------------------------
cal_shape_master.name = 'cal_shape_master_spirou.py'
cal_shape_master.instrument = __INSTRUMENT__
cal_shape_master.outputdir = 'reduced'
cal_shape_master.inputdir = 'tmp'
cal_shape_master.inputtype = 'pp'
cal_shape_master.extension = 'fits'
cal_shape_master.description = Help['SHAPE_DESC']
cal_shape_master.epilog = Help['SHAPE_EXAMPLE']
cal_shape_master.run_order = 4
cal_shape_master.arg(pos=0, **directory)
cal_shape_master.arg(name='hcfile', dtype='file', files=[sf.pp_hc1_hc1],
                     pos='1',
                     helpstr=Help['SHAPE_HCFILES_HELP'])
cal_shape_master.arg(name='fpfile', dtype='files', files=[sf.pp_fp_fp], pos='2',
                     helpstr=Help['SHAPE_FPFILES_HELP'])
cal_shape_master.kwarg(**add_cal)
cal_shape_master.kwarg(**badfile)
cal_shape_master.kwarg(**dobad)
cal_shape_master.kwarg(**backsub)
cal_shape_master.kwarg(default=True, **combine)
cal_shape_master.kwarg(**darkfile)
cal_shape_master.kwarg(**dodark)
cal_shape_master.kwarg(**flipimage)
cal_shape_master.kwarg(**fluxunits)
cal_shape_master.kwarg(**plot)
cal_shape_master.kwarg(**interactive)
cal_shape_master.kwarg(**resize)

# -----------------------------------------------------------------------------
# cal_FF_RAW_spirou
# -----------------------------------------------------------------------------
cal_ff.name = 'cal_FF_RAW_spirou.py'
cal_ff.instrument = __INSTRUMENT__
cal_ff.outputdir = 'reduced'
cal_ff.inputdir = 'tmp'
cal_ff.inputtype = 'pp'
cal_ff.extension = 'fits'
cal_ff.description = Help['FLAT_DESC']
cal_ff.epilog = Help['FLAT_EXAMPLE']
cal_ff.run_order = 5
cal_ff.arg(pos=0, **directory)
cal_ff.arg(name='files', dtype='files', filelogic='exclusive',
           files=[sf.pp_flat_flat], pos='1+',
           helpstr=Help['FILES_HELP'] + Help['FLAT_FILES_HELP'])
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
cal_ff.kwarg(**interactive)
cal_ff.kwarg(**resize)
cal_ff.kwarg(**shapefile)
cal_ff.kwarg(**tiltfile)

# -----------------------------------------------------------------------------
# cal_thermal_spirou
# -----------------------------------------------------------------------------
cal_thermal.name = 'cal_thermal_spirou.py'
cal_thermal.instrument = __INSTRUMENT__
cal_thermal.outputdir = 'reduced'
cal_thermal.inputdir = 'tmp'
cal_thermal.inputtype = 'pp'
cal_thermal.extension = 'fits'
cal_thermal.description = Help['EXTRACT_DESC']
cal_thermal.epilog = Help['EXTRACT_EXAMPLE']
cal_thermal.run_order = 6
cal_thermal.arg(pos=0, **directory)
cal_thermal.arg(name='files', dtype='files', pos='1+', files=[sf.pp_dark_dark],
                helpstr=Help['FILES_HELP'] + Help['EXTRACT_FILES_HELP'])
cal_thermal.kwarg(**add_cal)
cal_thermal.kwarg(**badfile)
cal_thermal.kwarg(**dobad)
cal_thermal.kwarg(**backsub)
cal_thermal.kwarg(default=True, **combine)
cal_thermal.kwarg(**darkfile)
cal_thermal.kwarg(**dodark)
cal_thermal.kwarg(default_ref='IC_EXTRACT_TYPE', **extractmethod)
cal_thermal.kwarg(**extfiber)
cal_thermal.kwarg(**flipimage)
cal_thermal.kwarg(**fluxunits)
cal_thermal.kwarg(**plot)
cal_thermal.kwarg(**interactive)
cal_thermal.kwarg(**resize)
cal_thermal.kwarg(**shapefile)
cal_thermal.kwarg(**tiltfile)

# -----------------------------------------------------------------------------
# cal_extract_RAW_spirou
# -----------------------------------------------------------------------------
cal_extract.name = 'cal_extract_RAW_spirou.py'
cal_extract.instrument = __INSTRUMENT__
cal_extract.outputdir = 'reduced'
cal_extract.inputdir = 'tmp'
cal_extract.inputtype = 'pp'
cal_extract.extension = 'fits'
cal_extract.description = Help['EXTRACT_DESC']
cal_extract.epilog = Help['EXTRACT_EXAMPLE']
cal_extract.run_order = 6
cal_extract.arg(pos=0, **directory)
cal_extract.arg(name='files', dtype='files', pos='1+', files=[sf.pp_file],
                helpstr=Help['FILES_HELP'] + Help['EXTRACT_FILES_HELP'],
                limit=1)
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
cal_extract.kwarg(**interactive)
cal_extract.kwarg(**resize)
cal_extract.kwarg(**shapefile)
cal_extract.kwarg(**tiltfile)

# -----------------------------------------------------------------------------
# cal_HC_E2DS_spirou
# -----------------------------------------------------------------------------
cal_hc.name = 'cal_HC_E2DS_EA_spirou.py'
cal_hc.instrument = __INSTRUMENT__
cal_hc.outputdir = 'reduced'
cal_hc.inputdir = 'reduced'
cal_hc.inputtype = 'e2ds'
cal_hc.extension = 'fits'
cal_hc.description = Help['HC_E2DS_DESC']
cal_hc.epilog = Help['HC_E2DS_EXAMPLE']
cal_hc.run_order = 7
# setup custom files (add a required keyword in the header to each file)
#    in this case we require "KW_EXT_TYPE" = "HCONE_HCONE"
hc_file1 = sf.out_ext_e2dsff_ab.copy()
hc_file1.args['KW_EXT_TYPE'] = 'HCONE_HCONE'
hc_file1.args['intype'] = sf.pp_hc1_hc1
hc_file1.args['ext'] = 'c_pp_e2ds_AB.fits'

hc_file2 = sf.out_ext_e2dsff_c.copy()
hc_file2.args['KW_EXT_TYPE'] = 'HCONE_HCONE'
hc_file2.args['intype'] = sf.pp_hc1_hc1
hc_file2.args['ext'] = 'c_pp_e2ds_AB.fits'

# set up arguments
cal_hc.arg(pos=0, **directory)
cal_hc.arg(name='files', dtype='files', pos='1+', files=[hc_file1, hc_file2],
           filelogic='exclusive', helpstr=Help['FILES_HELP'])
cal_hc.kwarg(**add_cal)
cal_hc.kwarg(**plot)
cal_hc.kwarg(**interactive)
cal_hc.kwarg(**blazefile)
cal_hc.kwarg(**flatfile)
cal_hc.kwarg(**wavefile)

# -----------------------------------------------------------------------------
# cal_WAVE_E2DS_spirou
# -----------------------------------------------------------------------------
cal_wave.name = 'cal_WAVE_E2DS_EA_spirou.py'
cal_wave.instrument = __INSTRUMENT__
cal_wave.outputdir = 'reduced'
cal_wave.inputdir = 'reduced'
cal_wave.inputtype = 'e2ds'
cal_wave.extension = 'fits'
cal_wave.description = Help['HC_E2DS_DESC']
cal_wave.epilog = Help['HC_E2DS_EXAMPLE']
cal_wave.run_order = 8
# setup custom files (add a required keyword in the header to each file)
#    in this case we require "KW_EXT_TYPE" = "HCONE_HCONE"
hc_file1 = sf.out_ext_e2dsff_ab.copy()
hc_file1.args['KW_EXT_TYPE'] = 'HCONE_HCONE'
hc_file1.args['intype'] = sf.pp_hc1_hc1
hc_file1.args['ext'] = 'c_pp_e2ds_AB.fits'

hc_file2 = sf.out_ext_e2dsff_c.copy()
hc_file2.args['KW_EXT_TYPE'] = 'HCONE_HCONE'
hc_file2.args['intype'] = sf.pp_hc1_hc1
hc_file2.args['ext'] = 'c_pp_e2ds_AB.fits'

fp_file1 = sf.out_ext_e2dsff_ab.copy()
fp_file1.args['KW_EXT_TYPE'] = 'FP_FP'
fp_file1.args['intype'] = sf.pp_fp_fp
fp_file1.args['ext'] = 'a_pp_e2ds_AB.fits'

fp_file2 = sf.out_ext_e2dsff_c.copy()
fp_file2.args['KW_EXT_TYPE'] = 'FP_FP'
fp_file2.args['intype'] = sf.pp_fp_fp
fp_file2.args['ext'] = 'a_pp_e2ds_AB.fits'

# set up arguments
cal_wave.arg(pos=0, **directory)
cal_wave.arg(name='fpfile', dtype='file', files=[fp_file1, fp_file2], pos='1',
             helpstr=Help['SHAPE_HCFILES_HELP'])
cal_wave.arg(name='hcfiles', dtype='files', files=[hc_file1, hc_file2],
             pos='2+',
             helpstr=Help['SHAPE_FPFILES_HELP'])
cal_wave.kwarg(**add_cal)
cal_wave.kwarg(**plot)
cal_wave.kwarg(**interactive)
cal_wave.kwarg(**blazefile)
cal_wave.kwarg(**flatfile)
cal_wave.kwarg(**wavefile)

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
# obj_mk_tellu
# -----------------------------------------------------------------------------
obj_mk_tellu.name = 'obj_mk_tellu.py'
obj_mk_tellu.instrument = __INSTRUMENT__
obj_mk_tellu.outputdir = 'reduced'
obj_mk_tellu.inputdir = 'reduced'
obj_mk_tellu.inputtype = 'e2ds'
obj_mk_tellu.extension = 'fits'
obj_mk_tellu.description = Help['EXTRACT_DESC']
obj_mk_tellu.epilog = Help['EXTRACT_EXAMPLE']
obj_mk_tellu.run_order = 9
obj_mk_tellu.arg(pos=0, **directory)
obj_mk_tellu.arg(name='files', dtype='files', pos='1+',
                 files=[sf.out_ext_e2dsff_ab],
                 helpstr=Help['FILES_HELP'] + Help['EXTRACT_FILES_HELP'],
                 limit=1)
obj_mk_tellu.kwarg(**add_cal)
obj_mk_tellu.kwarg(**badfile)
obj_mk_tellu.kwarg(**dobad)
obj_mk_tellu.kwarg(**backsub)
obj_mk_tellu.kwarg(default=True, **combine)
obj_mk_tellu.kwarg(**darkfile)
obj_mk_tellu.kwarg(**dodark)
obj_mk_tellu.kwarg(default_ref='IC_EXTRACT_TYPE', **extractmethod)
obj_mk_tellu.kwarg(**extfiber)
obj_mk_tellu.kwarg(**flipimage)
obj_mk_tellu.kwarg(**fluxunits)
obj_mk_tellu.kwarg(**plot)
obj_mk_tellu.kwarg(**interactive)
obj_mk_tellu.kwarg(**resize)
obj_mk_tellu.kwarg(**shapefile)
obj_mk_tellu.kwarg(**tiltfile)

# -----------------------------------------------------------------------------
# obj_mk_tellu_db
# -----------------------------------------------------------------------------
obj_mk_tellu_db.name = 'obj_mk_tellu_db.py'
obj_mk_tellu_db.instrument = __INSTRUMENT__
obj_mk_tellu_db.outputdir = 'reduced'
obj_mk_tellu_db.inputdir = 'reduced'
obj_mk_tellu_db.intputtype = 'e2ds'
obj_mk_tellu_db.extension = 'fits'
obj_mk_tellu_db.description = Help['DARK_DESC']
obj_mk_tellu_db.epilog = Help['DARK_EXAMPLE']
obj_mk_tellu_db.run_order = 10
obj_mk_tellu_db.kwarg(**add_cal)
obj_mk_tellu_db.kwarg(default=True, **combine)
obj_mk_tellu_db.kwarg(**flipimage)
obj_mk_tellu_db.kwarg(**fluxunits)
obj_mk_tellu_db.kwarg(**plot)
obj_mk_tellu_db.kwarg(**interactive)
obj_mk_tellu_db.kwarg(**resize)

# -----------------------------------------------------------------------------
# obj_fit_tellu
# -----------------------------------------------------------------------------
obj_fit_tellu.name = 'obj_fit_tellu.py'
obj_fit_tellu.instrument = __INSTRUMENT__
obj_fit_tellu.outputdir = 'reduced'
obj_fit_tellu.inputdir = 'reduced'
obj_fit_tellu.inputtype = 'e2ds'
obj_fit_tellu.extension = 'fits'
obj_fit_tellu.description = Help['EXTRACT_DESC']
obj_fit_tellu.epilog = Help['EXTRACT_EXAMPLE']
obj_fit_tellu.run_order = 11
obj_fit_tellu.arg(pos=0, **directory)
obj_fit_tellu.arg(name='files', dtype='files', pos='1+',
                  files=[sf.out_ext_e2dsff_ab],
                  helpstr=Help['FILES_HELP'] + Help['EXTRACT_FILES_HELP'],
                  limit=1)
obj_fit_tellu.kwarg(**add_cal)
obj_fit_tellu.kwarg(**badfile)
obj_fit_tellu.kwarg(**dobad)
obj_fit_tellu.kwarg(**backsub)
obj_fit_tellu.kwarg(default=True, **combine)
obj_fit_tellu.kwarg(**darkfile)
obj_fit_tellu.kwarg(**dodark)
obj_fit_tellu.kwarg(default_ref='IC_EXTRACT_TYPE', **extractmethod)
obj_fit_tellu.kwarg(**extfiber)
obj_fit_tellu.kwarg(**flipimage)
obj_fit_tellu.kwarg(**fluxunits)
obj_fit_tellu.kwarg(**plot)
obj_fit_tellu.kwarg(**interactive)
obj_fit_tellu.kwarg(**resize)
obj_fit_tellu.kwarg(**shapefile)
obj_fit_tellu.kwarg(**tiltfile)

# -----------------------------------------------------------------------------
# obj_fit_tellu_db
# -----------------------------------------------------------------------------
obj_fit_tellu_db.name = 'obj_fit_tellu_db.py'
obj_fit_tellu_db.instrument = __INSTRUMENT__
obj_fit_tellu_db.outputdir = 'reduced'
obj_fit_tellu_db.inputdir = 'reduced'
obj_fit_tellu_db.intputtype = 'e2ds'
obj_fit_tellu_db.extension = 'fits'
obj_fit_tellu_db.description = Help['DARK_DESC']
obj_fit_tellu_db.epilog = Help['DARK_EXAMPLE']
obj_fit_tellu_db.run_order = 12
obj_fit_tellu_db.kwarg(**add_cal)
obj_fit_tellu_db.kwarg(default=True, **combine)
obj_fit_tellu_db.kwarg(**flipimage)
obj_fit_tellu_db.kwarg(**fluxunits)
obj_fit_tellu_db.kwarg(**plot)
obj_fit_tellu_db.kwarg(**interactive)
obj_fit_tellu_db.kwarg(**resize)

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
