#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Spirou Files

# For fits files

file_name = drs_finput("name", KW_KEY1="value1", KW_KEY2="value2",
                       ext=".fits", filename=)


Created on 2018-10-31 at 18:06

@author: cook
"""
from __future__ import division
import numpy as np
import os
from collections import OrderedDict

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore

from . import output_filenames as out

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
# TODO: replace with terrapipe
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


class DrsFile:
    def __init__(self, name, **kwargs):
        self.name = name
        self.fileset = []
        self.args = dict()
        for kwarg in kwargs:
            self.args[kwarg] = kwargs[kwarg]

    def addarg(self, arg, value):
        self.args[arg] = value

    def addset(self, drsfile):
        self.fileset.append(drsfile)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return 'DrsRecipe[{0}]'.format(self.name)

    def copy(self):
        return DrsFile(self.name, **self.args)

    @staticmethod
    def add_required_keywords(drsfiles, kwargs):
        for kwarg in kwargs:
            for drsfile in drsfiles:
                drsfile.addarg(kwarg, kwargs[kwarg])
        return drsfiles

# =============================================================================
# TODO: replace with terrapipe
# Define proxy variables
# =============================================================================
Help = Helper()
drs_file = DrsFile
drs_input = drs_file
drs_finput = drs_file

# =============================================================================
# Raw Files
# =============================================================================
# Must add to list of raw files!!
raw_files = []
# =============================================================================
# generic raw file
raw_file = drs_finput('DRS_RAW', ext='.fits')
# -----------------------------------------------------------------------------
# raw dark files
raw_dark_dark = drs_finput('DARK_DARK', KW_CCAS='pos_pk', KW_CREF='pos_pk',
                           ext='d.fits')
raw_file.addset(raw_dark_dark)

# -----------------------------------------------------------------------------
# raw flat files
raw_dark_flat = drs_finput('DARK_FLAT', KW_CCAS='pos_pk', KW_CREF='pos_wl',
                           ext='f.fits')
raw_file.addset(raw_dark_flat)

raw_flat_dark = drs_finput('FLAT_DARK', KW_CCAS='pos_wl', KW_CREF='pos_pk',
                           ext='f.fits')
raw_file.addset(raw_flat_dark)

raw_flat_flat = drs_finput('FLAT_FLAT', KW_CCAS='pos_wl', KW_CREF='pos_wl',
                           ext='f.fits')
raw_file.addset(raw_flat_flat)

raw_flat_fp = drs_finput('FLAT_FP', KW_CCAS='pos_wl', KW_CREF='pos_fp',
                         ext='f.fits')
raw_file.addset(raw_flat_fp)

# -----------------------------------------------------------------------------
# raw align files
raw_dark_fp = drs_finput('DARK_FP', KW_CCAS='pos_pk', KW_CREF='pos_fp',
                         ext='a.fits')
raw_file.addset(raw_dark_fp)

raw_fp_dark = drs_finput('FP_DARK', KW_CCAS='pos_fp', KW_CREF='pos_pk',
                         ext='a.fits')
raw_file.addset(raw_fp_dark)

raw_fp_flat = drs_finput('FP_FLAT', KW_CCAS='pos_fp', KW_CREF='pos_wl',
                         ext='a.fits')
raw_file.addset(raw_fp_flat)

raw_fp_fp = drs_finput('FP_FP', KW_CCAS='pos_fp', KW_CREF='pos_fp',
                       ext='a.fits')
raw_file.addset(raw_fp_fp)

# -----------------------------------------------------------------------------
# raw object files
raw_obj_dark = drs_finput('OBJ_DARK', KW_CCAS='pos_pk', KW_CREF='pos_pk',
                          ext='o.fits')
raw_file.addset(raw_obj_dark)

raw_obj_fp = drs_finput('OBJ_FP', KW_CCAS='pos_pk', KW_CREF='pos_fp',
                        ext='o.fits')
raw_file.addset(raw_obj_fp)

raw_obj_hc1 = drs_finput('OBJ_HCONE', KW_CCAS='pos_pk', KW_CREF='pos_hc1',
                         ext='o.fits')
raw_file.addset(raw_obj_hc1)

raw_obj_hc2 = drs_finput('OBJ_HCTWO', KW_CCAS='pos_pk', KW_CREF='pos_hc2',
                         ext='o.fits')
raw_file.addset(raw_obj_hc2)

# -----------------------------------------------------------------------------
# raw comparison files
raw_dark_hc1 = drs_finput('DARK_HCONE', KW_CCAS='pos_pk', KW_CREF='pos_hc1',
                          ext='c.fits')
raw_file.addset(raw_dark_hc1)

raw_dark_hc2 = drs_finput('DARK_HCTWO', KW_CCAS='pos_pk', KW_CREF='pos_hc2',
                          ext='c.fits')
raw_file.addset(raw_dark_hc2)

raw_fp_hc1 = drs_finput('FP_HCONE', KW_CCAS='pos_fp', KW_CREF='pos_hc1',
                        ext='c.fits')
raw_file.addset(raw_fp_hc1)

raw_fp_hc2 = drs_finput('FP_HCTWO', KW_CCAS='pos_fp', KW_CREF='pos_hc2',
                        ext='c.fits')
raw_file.addset(raw_fp_hc2)

raw_hc1_fp = drs_finput('HCONE_FP', KW_CCAS='pos_hc1', KW_CREF='pos_fp',
                        ext='c.fits')
raw_file.addset(raw_hc1_fp)

raw_hc2_fp = drs_finput('HCTWO_FP', KW_CCAS='pos_hc2', KW_CREF='pos_fp',
                        ext='c.fits')
raw_file.addset(raw_hc2_fp)

raw_hc1_hc1 = drs_finput('HCONE_HCONE', KW_CCAS='pos_hc1', KW_CREF='pos_hc1',
                         ext='c.fits')
raw_file.addset(raw_hc1_hc1)

raw_hc2_hc2 = drs_finput('HCTWO_HCTWO', KW_CCAS='pos_hc2', KW_CREF='pos_hc2',
                         ext='c.fits')
raw_file.addset(raw_hc2_hc2)

raw_hc1_dark = drs_finput('HCONE_DARK', KW_CCAS='pos_hc1', KW_CREF='pos_pk',
                          ext='c.fits')
raw_file.addset(raw_hc1_dark)

raw_hc2_dark = drs_finput('HCTWO_DARK', KW_CCAS='pos_hc2', KW_CREF='pos_pk',
                          ext='c.fits')
raw_file.addset(raw_hc2_dark)

# =============================================================================
# Preprocessed Files
# =============================================================================
# generic pp file
pp_file = drs_finput('DRS_PP', ext='_pp.fits', intype=raw_file)
# -----------------------------------------------------------------------------
# dark
pp_dark_dark = drs_finput('DARK_DARK', KW_DPRTYPE='DARK_DARK', ext='d_pp.fits',
                          inext='.fits', outfunc=out.general_file,
                          intype=raw_dark_dark)
pp_file.addset(pp_dark_dark)
# -----------------------------------------------------------------------------
# flat
pp_flat_dark = drs_finput('FLAT_DARK', KW_DPRTYPE='FLAT_DARK', ext='f_pp.fits',
                          inext='.fits', outfunc=out.general_file,
                          intype=raw_flat_dark)
pp_file.addset(pp_flat_dark)

pp_dark_flat = drs_finput('DARK_FLAT', KW_DPRTYPE='DARK_FLAT', ext='f_pp.fits',
                          inext='.fits', outfunc=out.general_file,
                          intype=raw_dark_flat)
pp_file.addset(pp_dark_flat)

pp_flat_flat = drs_finput('FLAT_FLAT', KW_DPRTYPE='FLAT_FLAT', ext='f_pp.fits',
                          inext='.fits', outfunc=out.general_file,
                          intype=raw_flat_flat)
pp_file.addset(pp_flat_flat)

pp_flat_fp = drs_finput('FLAT_FP', KW_DPRTYPE='FLAT_FP', ext='f_pp.fits',
                        inext='.fits', outfunc=out.general_file,
                        intype=raw_flat_fp)
pp_file.addset(pp_flat_fp)
# -----------------------------------------------------------------------------
# align
pp_dark_fp = drs_finput('DARK_FP', KW_DPRTYPE='DARK_FP', ext='a_pp.fits',
                        inext='.fits', outfunc=out.general_file,
                        intype=raw_dark_fp)
pp_file.addset(pp_dark_fp)
pp_fp_dark = drs_finput('FP_DARK', KW_DPRTYPE='FP_DARK', ext='a_pp.fits',
                        inext='.fits', outfunc=out.general_file,
                        intype=raw_fp_dark)
pp_file.addset(pp_fp_dark)
pp_fp_flat = drs_finput('FP_FLAT', KW_DPRTYPE='FP_FLAT', ext='a_pp.fits',
                        inext='.fits', outfunc=out.general_file,
                        intype=raw_fp_flat)
pp_file.addset(pp_fp_flat)
pp_fp_fp = drs_finput('FP_FP', KW_DPRTYPE='FP_FP', ext='a_pp.fits',
                      inext='.fits', outfunc=out.general_file,
                      intype=raw_fp_fp)
pp_file.addset(pp_fp_fp)
# -----------------------------------------------------------------------------
#  object
pp_obj_dark = drs_finput('OBJ_DARK', KW_DPRTYPE='OBJ_DARK', ext='o_pp.fits',
                         inext='.fits', outfunc=out.general_file,
                         intype=raw_obj_dark)
pp_file.addset(pp_obj_dark)
pp_obj_fp = drs_finput('OBJ_FP', KW_DPRTYPE='OBJ_FP', ext='o_pp.fits',
                       inext='.fits', outfunc=out.general_file,
                       intype=raw_obj_fp)
pp_file.addset(pp_obj_fp)
pp_obj_hc1 = drs_finput('OBJ_HC1', KW_DPRTYPE='OBJ_HCONE', ext='o_pp.fits',
                        inext='.fits', outfunc=out.general_file,
                        intype=raw_obj_hc1)
pp_file.addset(pp_obj_hc1)
pp_obj_hc2 = drs_finput('OBJ_HC2', KW_DPRTYPE='OBJ_HCTWO', ext='o_pp.fits',
                        inext='.fits', outfunc=out.general_file,
                        intype=raw_obj_hc2)
pp_file.addset(pp_obj_hc2)
# -----------------------------------------------------------------------------
#  comparison
pp_dark_hc1 = drs_finput('DARK_HCONE', KW_DPRTYPE='DARK_HCONE', ext='c_pp.fits',
                         inext='.fits', outfunc=out.general_file,
                         intype=raw_dark_hc1)
pp_file.addset(pp_dark_hc1)
pp_dark_hc2 = drs_finput('DARK_HCTW0', KW_DPRTYPE='DARK_HCTW0', ext='c_pp.fits',
                         inext='.fits', outfunc=out.general_file,
                         intype=raw_dark_hc2)
pp_file.addset(pp_dark_hc2)
pp_fp_hc1 = drs_finput('FP_HCONE', KW_DPRTYPE='FP_HCONE', ext='c_pp.fits',
                       inext='.fits', outfunc=out.general_file,
                         intype=raw_fp_hc1)
pp_file.addset(pp_fp_hc1)
pp_fp_hc2 = drs_finput('FP_HCTWO', KW_DPRTYPE='FP_HCTWO', ext='c_pp.fits',
                       inext='.fits', outfunc=out.general_file,
                         intype=raw_fp_hc2)
pp_file.addset(pp_fp_hc2)
pp_hc1_fp = drs_finput('HCONE_FP', KW_DPRTYPE='HCONE_FP', ext='c_pp.fits',
                       inext='.fits', outfunc=out.general_file,
                         intype=raw_fp_hc2)
pp_file.addset(pp_hc1_fp)
pp_hc2_fp = drs_finput('HCTWO_FP', KW_DPRTYPE='HCTWO_FP', ext='c_pp.fits',
                       inext='.fits', outfunc=out.general_file,
                         intype=raw_hc2_fp)
pp_file.addset(pp_hc2_fp)
pp_hc1_hc1 = drs_finput('HCONE_HCONE', KW_DPRTYPE='HCONE_HCONE', ext='c_pp.fits',
                        inext='.fits', outfunc=out.general_file,
                         intype=raw_hc1_hc1)
pp_file.addset(pp_hc1_hc1)
pp_hc2_hc2 = drs_finput('HCTWO_HCTWO', KW_DPRTYPE='HCTWO_HCTWO', ext='c_pp.fits',
                        inext='.fits', outfunc=out.general_file,
                         intype=raw_hc2_hc2)
pp_file.addset(pp_hc2_hc2)
pp_hc1_dark = drs_finput('HCONE_DARK', KW_DPRTYPE='HCONE_DARK', ext='c_pp.fits',
                         inext='.fits', outfunc=out.general_file,
                         intype=raw_hc1_dark)
pp_file.addset(pp_hc1_dark)
pp_hc2_dark = drs_finput('HCTWO_DARK', KW_DPRTYPE='HCTWO_DARK', ext='c_pp.fits',
                         inext='.fits', outfunc=out.general_file,
                         intype=raw_hc2_dark)
pp_file.addset(pp_hc2_dark)

# =============================================================================
# Reduced Files
# =============================================================================
# generic out file
out_file = drs_finput('DRS_OUTPUT')
# -----------------------------------------------------------------------------
# dark out file
out_dark = drs_finput('DARK', KW_OUTPUT='DARK', ext='.fits',
                      outfunc=out.calib_file,
                      dbname='calibration', dbkey='DARK')
out_sky = drs_finput('SKY', KW_OUTPUT='SKY', ext='.fits',
                     outfunc=out.calib_file,
                     dbname='calibration', dbkey='SKYDARK')
# -----------------------------------------------------------------------------
# badpix out file
out_badpix = drs_finput('BADPIX', KW_OUTPUT='BADPIX',
                        ext='_badpixel.fits', outfunc=out.calib_file,
                        dbname='calibration', dbkey='BADPIX')
out_backmap = drs_finput('BKGRD_MAP', KW_OUTPUT='BKGRD_MAP',
                         ext='_bmap.fits', outfunc=out.calib_file,
                         dbname='calibration', dbkey='BKGRDMAP')

# -----------------------------------------------------------------------------
# loc
out_loc_orderp_ab = drs_finput('LOC_ORDERP_AB', KW_OUTPUT='LOC_ORDERP_AB',
                               fiber='AB', ext='_order_profile_AB.fits',
                               outfunc=out.calib_file,
                               dbname='calibration', dbkey='ORDER_PROFILE_AB')
out_loc_orderp_c = drs_finput('LOC_ORDERP_C', KW_OUTPUT='LOC_ORDERP_C',
                              fiber='C', ext='_order_profile_C.fits',
                              outfunc=out.calib_file,
                              dbname='calibration', dbkey='ORDER_PROFILE_C')
out_loc_loco_ab = drs_finput('LOC_LOCO_AB', KW_OUTPUT='LOC_LOCO_AB',
                             fiber='AB', ext='_loco_AB.fits',
                             outfunc=out.calib_file,
                             dbname='calibration', dbkey='LOC_AB')
out_loc_loco_c = drs_finput('LOC_LOCO_C', KW_OUTPUT='LOC_LOCO_C',
                            fiber='C', ext='_loco_C.fits',
                            outfunc=out.calib_file,
                            dbname='calibration', dbkey='LOC_C')
out_loc_loco_2_ab = drs_finput('LOC_FWHM_AB', KW_OUTPUT='LOC_FWHM_AB',
                               fiber='AB', ext='_fwhm-order_AB.fits',
                               outfunc=out.calib_file)
out_loc_loco_2c = drs_finput('LOC_FWHM_C', KW_OUTPUT='LOC_FWHM_C',
                             fiber='C', ext='_fwhm-order_C.fits',
                             outfunc=out.calib_file)
out_loc_loco_3_ab = drs_finput('LOC_SUP_AB', KW_OUTPUT='LOC_SUP_AB',
                               fiber='AB', ext='_with-order_AB.fits',
                               outfunc=out.calib_file)
out_loc_loco_3_c = drs_finput('LOC_SUP_C', KW_OUTPUT='LOC_SUP_C',
                              fiber='C', ext='_with-order_C.fits',
                              outfunc=out.calib_file)

# -----------------------------------------------------------------------------
# slit
out_slit_tilt = drs_finput('SLIT_TILT', KW_OUTPUT='SLIT_TILT')
out_silt_shape = drs_finput('SLIT_SHAPE', KW_OUTPUT='SLIT_SHAPE')
# -----------------------------------------------------------------------------
# flat
out_ff_blaze_ab = drs_finput('FF_BLAZE_AB', KW_OUTPUT='FF_BLAZE_AB', fiber='AB')
out_ff_blaze_a = drs_finput('FF_BLAZE_A', KW_OUTPUT='FF_BLAZE_A', fiber='A')
out_ff_blaze_b = drs_finput('FF_BLAZE_B', KW_OUTPUT='FF_BLAZE_B', fiber='B')
out_ff_blaze_c = drs_finput('FF_BLAZE_C', KW_OUTPUT='FF_BLAZE_C', fiber='C')
out_ff_flat_ab = drs_finput('FF_FLAT_AB', KW_OUTPUT='FF_FLAT_AB', fiber='AB')
out_ff_flat_a = drs_finput('FF_FLAT_A', KW_OUTPUT='FF_FLAT_A', fiber='A')
out_ff_flat_b = drs_finput('FF_FLAT_B', KW_OUTPUT='FF_FLAT_B', fiber='B')
out_ff_flat_c = drs_finput('FF_FLAT_C', KW_OUTPUT='FF_FLAT_C', fiber='C')
# -----------------------------------------------------------------------------
# extract
out_ext_e2ds_ab = drs_finput('EXTRACT_E2DS_AB', KW_OUTPUT='EXT_E2DS_AB',
                             fiber='AB', ext='_e2ds_AB.fits',
                             intype=pp_file)
out_ext_e2ds_a = drs_finput('EXTRACT_E2DS_A', KW_OUTPUT='EXT_E2DS_A',
                            fiber='A', ext='_e2ds_A.fits',
                             intype=pp_file)
out_ext_e2ds_b = drs_finput('EXTRACT_E2DS_B', KW_OUTPUT='EXT_E2DS_B',
                            fiber='B', ext='_e2ds_B.fits',
                             intype=pp_file)
out_ext_e2ds_c = drs_finput('EXTRACT_E2DS_C', KW_OUTPUT='EXT_E2DS_C',
                            fiber='C', ext='_e2ds_C.fits',
                             intype=pp_file)
out_ext_e2dsff_ab = drs_finput('EXTRACT_E2DS_FF_AB', KW_OUTPUT='EXT_E2DS_FF_AB',
                               fiber='AB', ext='_e2dsff_AB.fits',
                             intype=pp_file)
out_ext_e2dsff_a = drs_finput('EXTRACT_E2DS_FF_A', KW_OUTPUT='EXT_E2DS_FF_A',
                              fiber='A', ext='_e2dsff_A.fits',
                             intype=pp_file)
out_ext_e2dsff_b = drs_finput('EXTRACT_E2DS_FF_B', KW_OUTPUT='EXT_E2DS_FF_B',
                              fiber='B', ext='_e2dsff_B.fits',
                             intype=pp_file)
out_ext_e2dsff_c = drs_finput('EXTRACT_E2DS_FF_C', KW_OUTPUT='EXT_E2DS_FF_C',
                              fiber='C', ext='_e2dsff_C.fits',
                             intype=pp_file)
out_ext_e2dsll_ab = drs_finput('EXTRACT_E2DS_LL_AB', KW_OUTPUT='EXT_E2DS_LL_AB',
                               fiber='AB', ext='_e2dsll_AB.fits',
                             intype=pp_file)
out_ext_e2dsll_a = drs_finput('EXTRACT_E2DS_LL_A', KW_OUTPUT='EXT_E2DS_LL_A',
                              fiber='A', ext='_e2dsll_A.fits',
                             intype=pp_file)
out_ext_e2dsll_b = drs_finput('EXTRACT_E2DS_LL_B', KW_OUTPUT='EXT_E2DS_LL_B',
                              fiber='B', ext='_e2dsll_B.fits',
                             intype=pp_file)
out_ext_e2dsll_c = drs_finput('EXTRACT_E2DS_LL_C', KW_OUTPUT='EXT_E2DS_LL_C',
                              fiber='C', ext='_e2dsll_C.fits',
                             intype=pp_file)
out_ext_loco_ab = drs_finput('EXTRACT_LOCO_AB', KW_OUTPUT='EXT_LOCO_AB',
                             fiber='AB')
out_ext_loco_a = drs_finput('EXTRACT_LOCO_A', KW_OUTPUT='EXT_LOCO_A',
                            fiber='A')
out_ext_loco_b = drs_finput('EXTRACT_LOCO_B', KW_OUTPUT='EXT_LOCO_B',
                            fiber='B')
out_ext_loco_c = drs_finput('EXTRACT_LOCO_C', KW_OUTPUT='EXT_LOCO_C',
                            fiber='C')
out_ext_s1d_ab = drs_finput('EXTRACT_S1D_AB', KW_OUTPUT='EXT_S1D_AB',
                            fiber='AB')
out_ext_s1d_a = drs_finput('EXTRACT_S1D_A', KW_OUTPUT='EXT_S1D_A',
                           fiber='A')
out_ext_s1d_b = drs_finput('EXTRACT_S1D_B', KW_OUTPUT='EXT_S1D_B',
                           fiber='B')
out_ext_s1d_c = drs_finput('EXTRACT_S1D_C', KW_OUTPUT='EXT_S1D_C',
                           fiber='C')
# -----------------------------------------------------------------------------
# wave
out_wave_ab = drs_finput('WAVE_AB', fiber='AB', KW_OUTPUT='WAVE_SOL_AB')
out_wave_a = drs_finput('WAVE_A', fiber='A', KW_OUTPUT='WAVE_SOL_A')
out_wave_b = drs_finput('WAVE_B', fiber='B', KW_OUTPUT='WAVE_SOL_B')
out_wave_c = drs_finput('WAVE_C', fiber='C', KW_OUTPUT='WAVE_SOL_C')
out_wave_fp_ab = drs_finput('WAVE_FP_AB', fiber='AB',
                            KW_OUTPUT='WAVE_FP_SOL_AB')
out_wave_fp_a = drs_finput('WAVE_FP_A', fiber='A',
                           KW_OUTPUT='WAVE_FP_SOL_A')
out_wave_fp_b = drs_finput('WAVE_FP_B', fiber='B',
                           KW_OUTPUT='WAVE_FP_SOL_B')
out_wave_fp_c = drs_finput('WAVE_FP_C', fiber='C',
                           KW_OUTPUT='WAVE_FP_SOL_C')
out_wave_ea_ab = drs_finput('WAVE_EA_AB', fiber='AB',
                            KW_OUTPUT='WAVE_SOL_EA_AB')
out_wave_ea_a = drs_finput('WAVE_EA_A', fiber='A',
                           KW_OUTPUT='WAVE_SOL_EA_A')
out_wave_ea_b = drs_finput('WAVE_EA_B', fiber='B',
                           KW_OUTPUT='WAVE_SOL_EA_B')
out_wave_ea_c = drs_finput('WAVE_EA_C', fiber='C',
                           KW_OUTPUT='WAVE_SOL_EA_C')
out_wave_fp_ea_ab = drs_finput('WAVE_FP_EA_AB', fiber='AB',
                               KW_OUTPUT='WAVE_SOL_EA_AB')
out_wave_fp_ea_a = drs_finput('WAVE_FP_EA_A', fiber='A',
                              KW_OUTPUT='WAVE_SOL_EA_A')
out_wave_fp_ea_b = drs_finput('WAVE_FP_EA_B', fiber='B',
                              KW_OUTPUT='WAVE_SOL_EA_B')
out_wave_fp_ea_c = drs_finput('WAVE_FP_EA_C', fiber='C',
                              KW_OUTPUT='WAVE_SOL_EA_C')
out_wave_e2ds_ab = drs_finput('WAVE_E2DS_COPY_AB', fiber='AB',
                              KW_OUTPUT='WAVE_E2DSCOPY_AB')
out_wave_e2ds_a = drs_finput('WAVE_E2DS_COPY_A', fiber='A',
                             KW_OUTPUT='WAVE_E2DSCOPY_A')
out_wave_e2ds_b = drs_finput('WAVE_E2DS_COPY_B', fiber='B',
                             KW_OUTPUT='WAVE_E2DSCOPY_B')
out_wave_e2ds_c = drs_finput('WAVE_E2DS_COPY_C', fiber='C',
                             KW_OUTPUT='WAVE_E2DSCOPY_C')
out_wave_res_ab = drs_finput('WAVE_RES_EA_AB', fiber='AB',
                             KW_OUTPUT='WAVE_RES_AB')
out_wave_res_a = drs_finput('WAVE_RES_EA_A', fiber='A',
                            KW_OUTPUT='WAVE_RES_A')
out_wave_res_b = drs_finput('WAVE_RES_EA_B', fiber='B',
                            KW_OUTPUT='WAVE_RES_B')
out_wave_res_c = drs_finput('WAVE_RES_EA_C', fiber='C',
                            KW_OUTPUT='WAVE_RES_C')
# -----------------------------------------------------------------------------
# drift
out_drift_raw_ab = drs_finput('DRIFT_RAW_AB', KW_OUTPUT='DRIFT_RAW_AB',
                              fiber='AB')
out_drift_raw_a = drs_finput('DRIFT_RAW_A', KW_OUTPUT='DRIFT_RAW_A',
                             fiber='A')
out_drift_raw_b = drs_finput('DRIFT_RAW_B', KW_OUTPUT='DRIFT_RAW_B',
                             fiber='B')
out_drift_raw_c = drs_finput('DRIFT_RAW_C', KW_OUTPUT='DRIFT_RAW_C',
                             fiber='C')
out_drift_e2ds_ab = drs_finput('DRIFT_E2DS_FITS_AB', fiber='AB',
                               KW_OUTPUT='DRIFT_E2DS_AB')
out_drift_e2ds_a = drs_finput('DRIFT_E2DS_FITS_A', fiber='A',
                              KW_OUTPUT='DRIFT_E2DS_A')
out_drift_e2ds_b = drs_finput('DRIFT_E2DS_FITS_B', fiber='B',
                              KW_OUTPUT='DRIFT_E2DS_B')
out_drift_e2ds_c = drs_finput('DRIFT_E2DS_FITS_C', fiber='C',
                              KW_OUTPUT='DRIFT_E2DS_C')
out_driftpeak_e2ds_ab = drs_finput('DRIFTPEAK_E2DS_FITS_AB', fiber='AB',
                                   KW_OUTPUT='DRIFTPEAK_E2DS_AB')
out_driftpeak_e2ds_a = drs_finput('DRIFTPEAK_E2DS_FITS_A', fiber='A',
                                  KW_OUTPUT='DRIFTPEAK_E2DS_A')
out_driftpeak_e2ds_b = drs_finput('DRIFTPEAK_E2DS_FITS_B', fiber='B',
                                  KW_OUTPUT='DRIFTPEAK_E2DS_B')
out_driftpeak_e2ds_c = drs_finput('DRIFTPEAK_E2DS_FITS_C', fiber='C',
                                  KW_OUTPUT='DRIFTPEAK_E2DS_C')
out_driftccf_e2ds_ab = drs_finput('DRIFTCCF_E2DS_FITS_AB', fiber='AB',
                                  KW_OUTPUT='DRIFTCCF_E2DS_AB')
out_driftccf_e2ds_a = drs_finput('DRIFTCCF_E2DS_FITS_A', fiber='A',
                                 KW_OUTPUT='DRIFTCCF_E2DS_A')
out_driftccf_e2ds_b = drs_finput('DRIFTCCF_E2DS_FITS_B', fiber='B',
                                 KW_OUTPUT='DRIFTCCF_E2DS_B')
out_driftccf_e2ds_c = drs_finput('DRIFTCCF_E2DS_FITS_C', fiber='C',
                                 KW_OUTPUT='DRIFTCCF_E2DS_C')
# -----------------------------------------------------------------------------
# ccf
out_ccf_fits_ab = drs_finput('CCF_FITS_AB', KW_OUTPUT='CCF_E2DS',
                             fiber='AB')
out_ccf_fits_a = drs_finput('CCF_FITS_A', KW_OUTPUT='CCF_E2DS', fiber='A')
out_ccf_fits_b = drs_finput('CCF_FITS_B', KW_OUTPUT='CCF_E2DS', fiber='B')
out_ccf_fits_c = drs_finput('CCF_FITS_C', KW_OUTPUT='CCF_E2DS', fiber='C')
out_ccf_fits_ff_ab = drs_finput('CCF_FITS_FF_AB', KW_OUTPUT='CCF_E2DS_FF',
                                fiber='AB')
out_ccf_fits_ff_a = drs_finput('CCF_FITS_FF_A', KW_OUTPUT='CCF_E2DS_FF',
                               fiber='A')
out_ccf_fits_ff_b = drs_finput('CCF_FITS_FF_B', KW_OUTPUT='CCF_E2DS_FF',
                               fiber='B')
out_ccf_fits_ff_c = drs_finput('CCF_FITS_FF_C', KW_OUTPUT='CCF_E2DS_FF',
                               fiber='C')
out_ccf_fp_fits_ab = drs_finput('CCF_FP_FITS_AB', KW_OUTPUT='CCF_E2DS_FP',
                                fiber='AB')
out_ccf_fp_fits_a = drs_finput('CCF_FP_FITS_A', KW_OUTPUT='CCF_E2DS_FP',
                               fiber='A')
out_ccf_fp_fits_b = drs_finput('CCF_FP_FITS_B', KW_OUTPUT='CCF_E2DS_FP',
                               fiber='B')
out_ccf_fp_fits_c = drs_finput('CCF_FP_FITS_C', KW_OUTPUT='CCF_E2DS_FP',
                               fiber='C')
out_ccf_ff_fits_ff_ab = drs_finput('CCF_FP_FITS_FF_AB', fiber='AB',
                                   KW_OUTPUT='CCF_E2DS_FP_FF_AB')
out_ccf_ff_fits_ff_a = drs_finput('CCF_FP_FITS_FF_A', fiber='A',
                                  KW_OUTPUT='CCF_E2DS_FP_FF_A')
out_ccf_ff_fits_ff_b = drs_finput('CCF_FP_FITS_FF_B', fiber='B',
                                  KW_OUTPUT='CCF_E2DS_FP_FF_B')
out_ccf_ff_fits_ff_c = drs_finput('CCF_FP_FITS_FF_C', fiber='C',
                                  KW_OUTPUT='CCF_E2DS_FP_FF_C')
# -----------------------------------------------------------------------------
# telluric

out_tellu_trans_map_ab = drs_finput('TELLU_TRANS_MAP_AB', fiber='AB',
                                    KW_OUTPUT='TELLU_TRANS_AB')
out_tellu_trans_map_a = drs_finput('TELLU_TRANS_MAP_A', fiber='A',
                                   KW_OUTPUT='TELLU_TRANS_A')
out_tellu_trans_map_b = drs_finput('TELLU_TRANS_MAP_B', fiber='B',
                                   KW_OUTPUT='TELLU_TRANS_B')
out_tellu_trans_map_c = drs_finput('TELLU_TRANS_MAP_C', fiber='C',
                                   KW_OUTPUT='TELLU_TRANS_C')
out_tellu_abso_map_ab = drs_finput('TELLU_ABSO_MAP_AB', fiber='AB',
                                   KW_OUTPUT='TELLU_ABSO_MAP_AB')
out_tellu_abso_map_a = drs_finput('TELLU_ABSO_MAP_A', fiber='A',
                                  KW_OUTPUT='TELLU_ABSO_MAP_A')
out_tellu_abso_map_b = drs_finput('TELLU_ABSO_MAP_B', fiber='B',
                                  KW_OUTPUT='TELLU_ABSO_MAP_B')
out_tellu_abso_map_c = drs_finput('TELLU_ABSO_MAP_C', fiber='C',
                                  KW_OUTPUT='TELLU_ABSO_MAP_C')
out_tellu_abso_med_ab = drs_finput('TELLU_ABSO_MEDIAN_AB', fiber='AB',
                                   KW_OUTPUT='TELLU_ABSO_MED_AB')
out_tellu_abso_med_a = drs_finput('TELLU_ABSO_MEDIAN_A', fiber='A',
                                  KW_OUTPUT='TELLU_ABSO_MED_A')
out_tellu_abso_med_b = drs_finput('TELLU_ABSO_MEDIAN_B', fiber='B',
                                  KW_OUTPUT='TELLU_ABSO_MED_B')
out_tellu_abso_med_c = drs_finput('TELLU_ABSO_MEDIAN_C', fiber='C',
                                  KW_OUTPUT='TELLU_ABSO_MED_C')
out_tellu_abso_norm_ab = drs_finput('TELLU_ABSO_NORM_MAP_AB', fiber='AB',
                                    KW_OUTPUT='TELLU_ABSO_NORM_AB')
out_tellu_abso_norm_a = drs_finput('TELLU_ABSO_NORM_MAP_A', fiber='A',
                                   KW_OUTPUT='TELLU_ABSO_NORM_A')
out_tellu_abso_norm_b = drs_finput('TELLU_ABSO_NORM_MAP_B', fiber='B',
                                   KW_OUTPUT='TELLU_ABSO_NORM_B')
out_tellu_abso_norm_c = drs_finput('TELLU_ABSO_NORM_MAP_C', fiber='C',
                                   KW_OUTPUT='TELLU_ABSO_NORM_C')
out_tellu_fit_ab = drs_finput('TELLU_FIT_OUT_AB', fiber='AB',
                              KW_OUTPUT='TELLU_CORRECTED_AB')
out_tellu_fit_a = drs_finput('TELLU_FIT_OUT_A', fiber='A',
                             KW_OUTPUT='TELLU_CORRECTED_A')
out_tellu_fit_b = drs_finput('TELLU_FIT_OUT_B', fiber='B',
                             KW_OUTPUT='TELLU_CORRECTED_B')
out_tellu_fit_c = drs_finput('TELLU_FIT_OUT_C', fiber='C',
                             KW_OUTPUT='TELLU_CORRECTED_C')
out_tellu_fit_recon_ab = drs_finput('TELLU_FIT_RECON_AB', fiber='AB',
                                    KW_OUTPUT='TELLU_RECON_AB')
out_tellu_fit_recon_a = drs_finput('TELLU_FIT_RECON_A', fiber='A',
                                   KW_OUTPUT='TELLU_RECON_AB')
out_tellu_fit_recon_b = drs_finput('TELLU_FIT_RECON_B', fiber='B',
                                   KW_OUTPUT='TELLU_RECON_AB')
out_tellu_fit_recon_c = drs_finput('TELLU_FIT_RECON_C', fiber='C',
                                   KW_OUTPUT='TELLU_RECON_AB')
out_tellu_obj_temp_ab = drs_finput('OBJTELLU_TEMPLATE_AB', fiber='AB',
                                   KW_OUTPUT='OBJTELLU_TEMPLATE_AB')
out_tellu_obj_temp_a = drs_finput('OBJTELLU_TEMPLATE_A', fiber='A',
                                  KW_OUTPUT='OBJTELLU_TEMPLATE_A')
out_tellu_obj_temp_b = drs_finput('OBJTELLU_TEMPLATE_B', fiber='B',
                                  KW_OUTPUT='OBJTELLU_TEMPLATE_B')
out_tellu_obj_temp_c = drs_finput('OBJTELLU_TEMPLATE_C', fiber='C',
                                  KW_OUTPUT='OBJTELLU_TEMPLATE_C')
out_tellu_cube1_ab = drs_finput('OBJTELLU_TEMPLATE_CUBE_FILE1_AB', fiber='AB',
                                KW_OUTPUT='OBJTELLU_BIG1_AB')
out_tellu_cube1_a = drs_finput('OBJTELLU_TEMPLATE_CUBE_FILE1_A', fiber='A',
                               KW_OUTPUT='OBJTELLU_BIG1_A')
out_tellu_cube1_b = drs_finput('OBJTELLU_TEMPLATE_CUBE_FILE1_B', fiber='B',
                               KW_OUTPUT='OBJTELLU_BIG1_B')
out_tellu_cube1_c = drs_finput('OBJTELLU_TEMPLATE_CUBE_FILE1_C', fiber='C',
                               KW_OUTPUT='OBJTELLU_BIG1_C')
out_tellu_cube2_ab = drs_finput('OBJTELLU_TEMPLATE_CUBE_FILE2_AB', fiber='AB',
                                KW_OUTPUT='OBJTELLU_BIG0_AB')
out_tellu_cube2_a = drs_finput('OBJTELLU_TEMPLATE_CUBE_FILE2_A', fiber='A',
                               KW_OUTPUT='OBJTELLU_BIG0_A')
out_tellu_cube2_b = drs_finput('OBJTELLU_TEMPLATE_CUBE_FILE2_B', fiber='B',
                               KW_OUTPUT='OBJTELLU_BIG0_B')
out_tellu_cube2_c = drs_finput('OBJTELLU_TEMPLATE_CUBE_FILE2_C', fiber='C',
                               KW_OUTPUT='OBJTELLU_BIG0_C')
# -----------------------------------------------------------------------------
# polarisation
out_pol_deg = drs_finput('DEG_POL', KW_OUTPUT='POL_DEG')
out_pol_stokesi = drs_finput('STOKESI_POL', KW_OUTPUT='POL_STOKES_I')
out_pol_null1 = drs_finput('NULL_POL1', KW_OUTPUT='POL_NULL_POL1')
out_pol_null2 = drs_finput('NULL_POL2', KW_OUTPUT='POL_NULL_POL2')
out_pol_lsd = drs_finput('LSD_POL', KW_OUTPUT='POL_LSD')
# -----------------------------------------------------------------------------
# exposure map
raw_em_spe = drs_finput('EM_SPE', KW_OUTPUT='EM_TELL_SPEC_RAW')
raw_em_wave = drs_finput('EM_WAVE', KW_OUTPUT='EM_WAVEMAP_RAW')
raw_em_mask = drs_finput('EM_MASK', KW_OUTPUT='EM_MASK_RAW')
pp_em_spe = drs_finput('EM_SPE', KW_OUTPUT='EM_TELL_SPEC_PP')
pp_em_wave = drs_finput('EM_WAVE', KW_OUTPUT='EM_WAVEMAP_PP')
pp_em_mask = drs_finput('EM_MASK', KW_OUTPUT='EM_MASK_PP')
out_em_spe = drs_finput('EM_SPE', KW_OUTPUT='EM_TELL_SPEC_DRS')
out_em_wave = drs_finput('EM_WAVE', KW_OUTPUT='EM_WAVEMAP_DRS')
out_em_mask = drs_finput('EM_MASK', KW_OUTPUT='EM_MASK_DRS')
# -----------------------------------------------------------------------------
# wave map
raw_backmap_spe = drs_finput('WAVE_MAP_SPE',
                             KW_OUTPUT='EM_WAVEMAP_SPE_RAW')
raw_backmap_spe0 = drs_finput('WAVE_MAP_SPE0',
                              KW_OUTPUT='EM_WAVEMAP_SPE0_RAW')
pp_backmap_spe = drs_finput('WAVE_MAP_SPE',
                            KW_OUTPUT='EM_WAVEMAP_SPE_PP')
pp_backmap_spe0 = drs_finput('WAVE_MAP_SPE0',
                             KW_OUTPUT='EM_WAVEMAP_SPE0_PP')
out_backmap_spe = drs_finput('WAVE_MAP_SPE',
                             KW_OUTPUT='EM_WAVEMAP_SPE_DRS')
out_backmap_spe0 = drs_finput('WAVE_MAP_SPE0',
                              KW_OUTPUT='EM_WAVEMAP_SPE0_DRS')

# =============================================================================
# End of code
# =============================================================================
