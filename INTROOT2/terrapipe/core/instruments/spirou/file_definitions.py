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
from terrapipe.core import constants
from terrapipe.core.core import drs_file
from . import output_filenames as out

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'config.instruments.spirou.file_defintions.py'
__INSTRUMENT__ = 'SPIROU'
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']

# =============================================================================
# Define Files
# =============================================================================
drs_input = drs_file.DrsInputFile
drs_finput = drs_file.DrsFitsFile

# =============================================================================
# Raw Files
# =============================================================================
# Must add to list of raw files!!
raw_files = []
# =============================================================================
# generic raw file
raw_file = drs_finput('DRS_RAW', iletype = '.fits', suffix = '')
# -----------------------------------------------------------------------------
# raw dark files
raw_dark_dark = drs_finput('DARK_DARK', KW_CCAS='pos_pk', KW_CREF='pos_pk',
                           filetype = '.fits', suffix = '', inext='d.fits')
raw_file.addset(raw_dark_dark)

# -----------------------------------------------------------------------------
# raw flat files
raw_dark_flat = drs_finput('DARK_FLAT', KW_CCAS='pos_pk', KW_CREF='pos_wl',
                         filetype = '.fits', suffix = '')
raw_file.addset(raw_dark_flat)

raw_flat_dark = drs_finput('FLAT_DARK', KW_CCAS='pos_wl', KW_CREF='pos_pk',
                         filetype = '.fits', suffix = '')
raw_file.addset(raw_flat_dark)

raw_flat_flat = drs_finput('FLAT_FLAT', KW_CCAS='pos_wl', KW_CREF='pos_wl',
                         filetype = '.fits', suffix = '')
raw_file.addset(raw_flat_flat)

raw_flat_fp = drs_finput('FLAT_FP', KW_CCAS='pos_wl', KW_CREF='pos_fp',
                         filetype = '.fits', suffix = '')
raw_file.addset(raw_flat_fp)

# -----------------------------------------------------------------------------
# raw align files
raw_dark_fp = drs_finput('DARK_FP', KW_CCAS='pos_pk', KW_CREF='pos_fp',
                         filetype = '.fits', suffix = '')
raw_file.addset(raw_dark_fp)

raw_fp_dark = drs_finput('FP_DARK', KW_CCAS='pos_fp', KW_CREF='pos_pk',
                         filetype = '.fits', suffix = '')
raw_file.addset(raw_fp_dark)

raw_fp_flat = drs_finput('FP_FLAT', KW_CCAS='pos_fp', KW_CREF='pos_wl',
                         filetype = '.fits', suffix = '')
raw_file.addset(raw_fp_flat)

raw_fp_fp = drs_finput('FP_FP', KW_CCAS='pos_fp', KW_CREF='pos_fp',
                         filetype = '.fits', suffix = '')
raw_file.addset(raw_fp_fp)

# -----------------------------------------------------------------------------
# raw object files
raw_obj_dark = drs_finput('OBJ_DARK', KW_CCAS='pos_pk', KW_CREF='pos_pk',
                         filetype = '.fits', suffix = '', inext='o.fits')
raw_file.addset(raw_obj_dark)

raw_obj_fp = drs_finput('OBJ_FP', KW_CCAS='pos_pk', KW_CREF='pos_fp',
                         filetype = '.fits', suffix = '', inext='o.fits')
raw_file.addset(raw_obj_fp)

raw_obj_hc1 = drs_finput('OBJ_HCONE', KW_CCAS='pos_pk', KW_CREF='pos_hc1',
                         filetype = '.fits', suffix = '', inext='o.fits')
raw_file.addset(raw_obj_hc1)

raw_obj_hc2 = drs_finput('OBJ_HCTWO', KW_CCAS='pos_pk', KW_CREF='pos_hc2',
                         filetype = '.fits', suffix = '', inext='o.fits')
raw_file.addset(raw_obj_hc2)

# -----------------------------------------------------------------------------
# raw comparison files
raw_dark_hc1 = drs_finput('DARK_HCONE', KW_CCAS='pos_pk', KW_CREF='pos_hc1',
                         filetype = '.fits', suffix = '')
raw_file.addset(raw_dark_hc1)

raw_dark_hc2 = drs_finput('DARK_HCTWO', KW_CCAS='pos_pk', KW_CREF='pos_hc2',
                         filetype = '.fits', suffix = '')
raw_file.addset(raw_dark_hc2)

raw_fp_hc1 = drs_finput('FP_HCONE', KW_CCAS='pos_fp', KW_CREF='pos_hc1',
                         filetype = '.fits', suffix = '')
raw_file.addset(raw_fp_hc1)

raw_fp_hc2 = drs_finput('FP_HCTWO', KW_CCAS='pos_fp', KW_CREF='pos_hc2',
                         filetype = '.fits', suffix = '')
raw_file.addset(raw_fp_hc2)

raw_hc1_fp = drs_finput('HCONE_FP', KW_CCAS='pos_hc1', KW_CREF='pos_fp',
                         filetype = '.fits', suffix = '')
raw_file.addset(raw_hc1_fp)

raw_hc2_fp = drs_finput('HCTWO_FP', KW_CCAS='pos_hc2', KW_CREF='pos_fp',
                         filetype = '.fits', suffix = '')
raw_file.addset(raw_hc2_fp)

raw_hc1_hc1 = drs_finput('HCONE_HCONE', KW_CCAS='pos_hc1', KW_CREF='pos_hc1',
                         filetype = '.fits', suffix = '')
raw_file.addset(raw_hc1_hc1)

raw_hc2_hc2 = drs_finput('HCTWO_HCTWO', KW_CCAS='pos_hc2', KW_CREF='pos_hc2',
                         filetype = '.fits', suffix = '')
raw_file.addset(raw_hc2_hc2)

raw_hc1_dark = drs_finput('HCONE_DARK', KW_CCAS='pos_hc1', KW_CREF='pos_pk',
                         filetype = '.fits', suffix = '')
raw_file.addset(raw_hc1_dark)

raw_hc2_dark = drs_finput('HCTWO_DARK', KW_CCAS='pos_hc2', KW_CREF='pos_pk',
                         filetype = '.fits', suffix = '')
raw_file.addset(raw_hc2_dark)

# =============================================================================
# Preprocessed Files
# =============================================================================
# generic pp file
pp_file = drs_finput('DRS_PP', filetype = '.fits', suffix = '_pp')
# -----------------------------------------------------------------------------
# dark
pp_dark_dark = drs_finput('DARK_DARK', KW_DPRTYPE='DARK_DARK',
                         filetype = '.fits',
                         suffix = '_pp',
                         inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_dark_dark)
# -----------------------------------------------------------------------------
# flat
pp_flat_dark = drs_finput('FLAT_DARK', KW_DPRTYPE='FLAT_DARK',
                         filetype = '.fits',
                         suffix = '_pp',
                         inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_flat_dark)

pp_dark_flat = drs_finput('DARK_FLAT', KW_DPRTYPE='DARK_FLAT',
                         filetype = '.fits',
                         suffix = '_pp',
                         inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_dark_flat)

pp_flat_flat = drs_finput('FLAT_FLAT', KW_DPRTYPE='FLAT_FLAT',
                         filetype = '.fits',
                         suffix = '_pp',
                         inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_flat_flat)

pp_flat_fp = drs_finput('FLAT_FP', KW_DPRTYPE='FLAT_FP',
                         filetype = '.fits',
                         suffix = '_pp',
                         inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_flat_fp)
# -----------------------------------------------------------------------------
# align
pp_dark_fp = drs_finput('DARK_FP', KW_DPRTYPE='DARK_FP',
                         filetype = '.fits',
                         suffix = '_pp',
                         inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_dark_fp)
pp_fp_dark = drs_finput('FP_DARK', KW_DPRTYPE='FP_DARK',
                         filetype = '.fits',
                         suffix = '_pp',
                         inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_fp_dark)
pp_fp_flat = drs_finput('FP_FLAT', KW_DPRTYPE='FP_FLAT',
                         filetype = '.fits',
                         suffix = '_pp',
                         inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_fp_flat)
pp_fp_fp = drs_finput('FP_FP', KW_DPRTYPE='FP_FP',
                         filetype = '.fits',
                         suffix = '_pp',
                         inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_fp_fp)
# -----------------------------------------------------------------------------
#  object
pp_obj_dark = drs_finput('OBJ_DARK', KW_DPRTYPE='OBJ_DARK',
                         filetype = '.fits',
                         suffix = '_pp',
                         inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_obj_dark)
pp_obj_fp = drs_finput('OBJ_FP', KW_DPRTYPE='OBJ_FP',
                         filetype = '.fits',
                         suffix = '_pp',
                         inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_obj_fp)
pp_obj_hc1 = drs_finput('OBJ_HC1', KW_DPRTYPE='OBJ_HCONE',
                        filetype = '.fits',
                        suffix = '_pp',
                        inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_obj_hc1)
pp_obj_hc2 = drs_finput('OBJ_HC2', KW_DPRTYPE='OBJ_HCTWO',
                         filetype = '.fits',
                         suffix = '_pp',
                         inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_obj_hc2)
# -----------------------------------------------------------------------------
#  comparison
pp_dark_hc1 = drs_finput('DARK_HCONE', KW_DPRTYPE='DARK_HCONE',
                         filetype = '.fits',
                         suffix = '_pp',
                         inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_dark_hc1)
pp_dark_hc2 = drs_finput('DARK_HCTW0', KW_DPRTYPE='DARK_HCTW0',
                         filetype = '.fits',
                         suffix = '_pp',
                         inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_dark_hc2)
pp_fp_hc1 = drs_finput('FP_HCONE', KW_DPRTYPE='FP_HCONE',
                         filetype = '.fits',
                         suffix = '_pp',
                         inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_fp_hc1)
pp_fp_hc2 = drs_finput('FP_HCTWO', KW_DPRTYPE='FP_HCTWO',
                         filetype = '.fits',
                         suffix = '_pp',
                         inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_fp_hc2)
pp_hc1_fp = drs_finput('HCONE_FP', KW_DPRTYPE='HCONE_FP',
                         filetype = '.fits',
                         suffix = '_pp',
                         inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_hc1_fp)
pp_hc2_fp = drs_finput('HCTWO_FP', KW_DPRTYPE='HCTWO_FP',
                         filetype = '.fits',
                         suffix = '_pp',
                         inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_hc2_fp)
pp_hc1_hc1 = drs_finput('HCONE_HCONE', KW_DPRTYPE='HCONE_HCONE',
                         filetype = '.fits',
                         suffix = '_pp',
                         inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_hc1_hc1)
pp_hc2_hc2 = drs_finput('HCTWO_HCTWO', KW_DPRTYPE='HCTWO_HCTWO',
                         filetype = '.fits',
                         suffix = '_pp',
                         inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_hc2_hc2)
pp_hc1_dark = drs_finput('HCONE_DARK', KW_DPRTYPE='HCONE_DARK',
                         filetype = '.fits',
                         suffix = '_pp',
                         inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_hc1_dark)
pp_hc2_dark = drs_finput('HCTWO_DARK', KW_DPRTYPE='HCTWO_DARK',
                         filetype = '.fits',
                         suffix = '_pp',
                         inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_hc2_dark)

# =============================================================================
# Reduced Files
# =============================================================================
# generic out file
out_file = drs_finput('DRS_OUTPUT', filetype='.fits', suffix='')
# -----------------------------------------------------------------------------
# dark out file
out_dark = drs_finput('DARK', KW_OUTPUT='DARK',
                      filetype='.fits',
                      suffix='',
                      outfunc=out.calib_file,
                      dbname='calibration', dbkey='DARK')
out_sky = drs_finput('SKY', KW_OUTPUT='SKY',
                     filetype='.fits',
                     suffix='',
                     outfunc=out.calib_file,
                     dbname='calibration', dbkey='SKYDARK')
out_dark_master = drs_finput('DARKM', KW_OUTPUT='DARKM',
                             filetype='.fits',
                             suffix='_dark_master',
                             outfunc=out.calib_file,
                             dbname='calibration', dbkey='DARKM')
# add dark outputs to output fileset
out_file.addset(out_dark)
out_file.addset(out_sky)
out_file.addset(out_dark_master)
# -----------------------------------------------------------------------------
# badpix out file
out_badpix = drs_finput('BADPIX', KW_OUTPUT='BADPIX',
                        fileext='.fits',
                        suffix='_badpixel',
                        outfunc=out.calib_file,
                        dbname='calibration', dbkey='BADPIX')
out_backmap = drs_finput('BKGRD_MAP', KW_OUTPUT='BKGRD_MAP',
                         ext='_bmap.fits', outfunc=out.calib_file,
                         dbname='calibration', dbkey='BKGRDMAP')
# add badpix outputs to output fileset
out_file.addset(out_badpix)
out_file.addset(out_backmap)
# -----------------------------------------------------------------------------
# localisation
out_loc_orderp = drs_finput('LOC_ORDERP', KW_OUTPUT='LOC_ORDERP',
                            fibers=['AB', 'A', 'B', 'C'],
                            fileext='.fits',
                            suffix='_order_profile.fits',
                            outfunc=out.calib_file,
                            dbname='calibration', dbkey='ORDER_PROFILE')
out_loc_loco = drs_finput('LOC_LOCO', KW_OUTPUT='LOC_LOCO',
                          fibers=['AB', 'A', 'B', 'C'],
                          fileext='.fits',
                          suffix='_loco',
                          outfunc=out.calib_file,
                          dbname='calibration', dbkey='LOC')
out_loc_fwhm = drs_finput('LOC_FWHM', KW_OUTPUT='LOC_FWHM',
                          fibers=['AB', 'A', 'B', 'C'],
                          fileext='.fits',
                          suffix='_fwhm-order',
                          outfunc=out.calib_file)
out_loc_sup = drs_finput('LOC_SUP', KW_OUTPUT='LOC_SUP',
                         fibers=['AB', 'A', 'B', 'C'],
                         fileext='.fits',
                         suffix='_with-order',
                         outfunc=out.calib_file)
# add localisation outputs to output fileset
out_file.addset(out_loc_orderp)
out_file.addset(out_loc_loco)
out_file.addset(out_loc_fwhm)
out_file.addset(out_loc_sup)

# -----------------------------------------------------------------------------
# shape master
out_shape_dxmap = drs_finput('SHAPE_X', KW_OUTPUT='SHAPE_X',
                             fileext='.fits',
                             suffix='_shapex',
                             outfunc=out.calib_file,
                             dbname='calibration', dbkey='SHAPEX')
out_shape_dymap = drs_finput('SHAPE_Y', KW_OUTPUT='SHAPE_Y',
                             fileext='.fits',
                             suffix='_shapey',
                             outfunc=out.calib_file,
                             dbname='calibration', dbkey='SHAPEY')
out_shape_fpmaster = drs_finput('MASTER_FP', KW_OUTPUT='MASTER_FP',
                                fileext='.fits',
                                suffix='_fpmaster',
                                outfunc=out.calib_file,
                                dbname='calibration', dbkey='FPMASTER')
out_shape_debug_ifp = drs_finput('SHAPE_IN_FP', KW_OUTPUT='SHAPE_IN_FP',
                                 fileext='.fits',
                                 suffix='_shape_in_fp',
                                 outfunc=out.debug_file)
out_shape_debug_ofp = drs_finput('SHAPE_OUT_FP', KW_OUTPUT='SHAPE_OUT_FP',
                                 fileext='.fits',
                                 suffix='_shape_out_fp',
                                 outfunc=out.debug_file)
out_shape_debug_ihc = drs_finput('SHAPE_IN_HC', KW_OUTPUT='SHAPE_IN_HC',
                                 fileext='.fits',
                                 suffix='_shape_out_fp',
                                 outfunc=out.debug_file)
out_shape_debug_ohc = drs_finput('SHAPE_OUT_HC', KW_OUTPUT='SHAPE_OUT_HC',
                                 fileext='.fits',
                                 suffix='_shape_out_hc',
                                 outfunc=out.debug_file)
out_shape_debug_bdx = drs_finput('SHAPE_BDX', KW_OUTPUT='SHAPE_BDX',
                                 fileext='.fits',
                                 suffix='_shape_out_bdx',
                                 outfunc=out.debug_file)
# add shape master outputs to output fileset
out_file.addset(out_shape_dxmap)
out_file.addset(out_shape_dymap)
out_file.addset(out_shape_fpmaster)
out_file.addset(out_shape_debug_ifp)
out_file.addset(out_shape_debug_ofp)
out_file.addset(out_shape_debug_ihc)
out_file.addset(out_shape_debug_ohc)
out_file.addset(out_shape_debug_bdx)
# -----------------------------------------------------------------------------
# shape local
out_shape_local = drs_finput('SHAPEL', KW_OUTPUT='SHAPEL',
                             fileext='.fits',
                             suffix='_shapel',
                             outfunc=out.calib_file,
                             dbname='calibration', dbkey='SHAPEL')
out_shapel_debug_ifp = drs_finput('SHAPEL_IN_FP', KW_OUTPUT='SHAPEL_IN_FP',
                                  fileext='.fits',
                                  suffix='_shapel_in_fp.fits',
                                  outfunc=out.debug_file)

out_shapel_debug_ofp = drs_finput('SHAPEL_OUT_FP', KW_OUTPUT='SHAPEL_OUT_FP',
                                  fileext='.fits',
                                  suffix='_shapel_out_fp.fits',
                                  outfunc=out.debug_file)
# add shape local outputs to output fileset
out_file.addset(out_shape_local)
out_file.addset(out_shapel_debug_ifp)
out_file.addset(out_shapel_debug_ofp)

# -----------------------------------------------------------------------------
# flat
out_ff_blaze = drs_finput('FF_BLAZE', KW_OUTPUT='FF_BLAZE',
                          fibers=['AB', 'A', 'B', 'C'],
                          fileext='.fits',
                          suffix='_blaze',
                          dbname='calibration', dbkey='BLAZE')
out_ff_flat = drs_finput('FF_FLAT', KW_OUTPUT='FF_FLAT',
                         fibers=['AB', 'A', 'B', 'C'],
                         fileext='.fits',
                         suffix='_flat',
                         dbname='calibration', dbkey='FLAT')
# add flat outputs to output fileset
out_file.addset(out_ff_blaze)
out_file.addset(out_ff_flat)

# -----------------------------------------------------------------------------
# extract
out_ext_e2ds = drs_finput('EXTRACT_E2DS', KW_OUTPUT='EXT_E2DS',
                          fibers=['AB', 'A', 'B', 'C'],
                          fileext='.fits',
                          suffix='_e2ds')
out_ext_e2dsff = drs_finput('EXTRACT_E2DS_FF', KW_OUTPUT='EXT_E2DS_FF',
                            fibers=['AB', 'A', 'B', 'C'],
                          fileext='.fits',
                          suffix='_e2dsff')
out_ext_e2dsll = drs_finput('EXTRACT_E2DS_LL', KW_OUTPUT='EXT_E2DS_LL',
                            fibers=['AB', 'A', 'B', 'C'],
                          fileext='.fits',
                          suffix='_e2dsll')
out_ext_loco = drs_finput('EXTRACT_LOCO_AB', KW_OUTPUT='EXT_LOCO',
                          fibers=['AB', 'A', 'B', 'C'],
                          fileext='.fits',
                          suffix='_e2dsloco')
out_ext_s1d = drs_finput('EXTRACT_S1D_AB', KW_OUTPUT='EXT_S1D',
                         fibers=['AB', 'A', 'B', 'C'],
                          fileext='.fits',
                          suffix='s1d')
# add extract outputs to output fileset
out_file.addset(out_ext_e2ds)
out_file.addset(out_ext_e2dsff)
out_file.addset(out_ext_e2dsll)
out_file.addset(out_ext_loco)
out_file.addset(out_ext_s1d)

# -----------------------------------------------------------------------------
# thermal
out_thermal_e2ds = drs_finput('THERMAL_E2DS_AB',
                              KW_OUTPUT='THERMAL_E2DS',
                              fibers=['AB', 'A', 'B', 'C'],
                              fileext='.fits',
                              suffix='_e2ds',
                              dbname='calibration', dbkey='THERMAL')
# add thermal outputs to output fileset
out_file.addset(out_thermal_e2ds)

# -----------------------------------------------------------------------------
# TODO: fill in definitions
# wave
# out_wave = drs_finput('WAVE_SOL', KW_OUTPUT='WAVE_SOL',
#                       fibers=['AB', 'A', 'B', 'C'])
# out_wave_fp = drs_finput('WAVE_FP',
#                          fibers=['AB', 'A', 'B', 'C'],
#                          KW_OUTPUT='WAVE_FP')
# out_wave_ea = drs_finput('WAVE_EA', fibers=['AB', 'A', 'B', 'C'],
#                          KW_OUTPUT='WAVE_EA')
# out_wave_fp_ea = drs_finput('WAVE_FP_EA', fibers=['AB', 'A', 'B', 'C'],
#                             KW_OUTPUT='WAVE_FP_EA')
# out_wave_e2ds = drs_finput('WAVE_E2DS_COPY', fibers=['AB', 'A', 'B', 'C'],
#                            KW_OUTPUT='WAVE_E2DS_COPY')
# out_wave_res = drs_finput('WAVE_RES_EA', fibers=['AB', 'A', 'B', 'C'],
#                           KW_OUTPUT='WAVE_RES_EA')
# # add wave outputs to output fileset
# out_file.addset(out_wave)
# out_file.addset(out_wave_fp)
# out_file.addset(out_wave_ea)
# out_file.addset(out_wave_fp_ea)
# out_file.addset(out_wave_e2ds)
# out_file.addset(out_wave_res)

# -----------------------------------------------------------------------------
# TODO: fill in definitions
# drift
# out_drift_raw = drs_finput('DRIFT_RAW_AB', KW_OUTPUT='DRIFT_RAW_AB',
#                            fiber='AB')
# out_drift_e2ds = drs_finput('DRIFT_E2DS_FITS_AB', fiber='AB',
#                             KW_OUTPUT='DRIFT_E2DS_AB')
# out_driftpeak_e2ds = drs_finput('DRIFTPEAK_E2DS_FITS_AB', fiber='AB',
#                                 KW_OUTPUT='DRIFTPEAK_E2DS_AB')
# out_driftccf_e2ds = drs_finput('DRIFTCCF_E2DS_FITS_AB', fiber='AB',
#                                KW_OUTPUT='DRIFTCCF_E2DS_AB')
# -----------------------------------------------------------------------------
# TODO: fill in definitions
# ccf
# out_ccf_fits = drs_finput('CCF_FITS_AB', KW_OUTPUT='CCF_E2DS',
#                           fiber='AB')
# out_ccf_fits_ff = drs_finput('CCF_FITS_FF_AB', KW_OUTPUT='CCF_E2DS_FF',
#                              fiber='AB')
# out_ccf_fp_fits = drs_finput('CCF_FP_FITS_AB', KW_OUTPUT='CCF_E2DS_FP',
#                              fiber='AB')
# out_ccf_ff_fits_ff = drs_finput('CCF_FP_FITS_FF_AB', fiber='AB',
#                                 KW_OUTPUT='CCF_E2DS_FP_FF_AB')

# -----------------------------------------------------------------------------
# telluric
# TODO: fill in definitions
# out_tellu_trans_map = drs_finput('TELLU_TRANS_MAP_AB', fiber='AB',
#                                  KW_OUTPUT='TELLU_TRANS_AB')
# out_tellu_abso_map = drs_finput('TELLU_ABSO_MAP_AB', fiber='AB',
#                                 KW_OUTPUT='TELLU_ABSO_MAP_AB')
# out_tellu_abso_med = drs_finput('TELLU_ABSO_MEDIAN_AB', fiber='AB',
#                                 KW_OUTPUT='TELLU_ABSO_MED_AB')
# out_tellu_abso_norm = drs_finput('TELLU_ABSO_NORM_MAP_AB', fiber='AB',
#                                  KW_OUTPUT='TELLU_ABSO_NORM_AB')
# out_tellu_fit = drs_finput('TELLU_FIT_OUT_AB', fiber='AB',
#                            KW_OUTPUT='TELLU_CORRECTED_AB')
# out_tellu_fit_recon = drs_finput('TELLU_FIT_RECON_AB', fiber='AB',
#                                  KW_OUTPUT='TELLU_RECON_AB')
# out_tellu_obj_temp = drs_finput('OBJTELLU_TEMPLATE_AB', fiber='AB',
#                                 KW_OUTPUT='OBJTELLU_TEMPLATE_AB')
# out_tellu_cube1 = drs_finput('OBJTELLU_TEMPLATE_CUBE_FILE1_AB', fiber='AB',
#                              KW_OUTPUT='OBJTELLU_BIG1_AB')
# out_tellu_cube2 = drs_finput('OBJTELLU_TEMPLATE_CUBE_FILE2_AB', fiber='AB',
#                              KW_OUTPUT='OBJTELLU_BIG0_AB')
# -----------------------------------------------------------------------------
# polarisation
# TODO: fill in definitions
# out_pol_deg = drs_finput('DEG_POL', KW_OUTPUT='POL_DEG')
# out_pol_stokesi = drs_finput('STOKESI_POL', KW_OUTPUT='POL_STOKES_I')
# out_pol_null1 = drs_finput('NULL_POL1', KW_OUTPUT='POL_NULL_POL1')
# out_pol_null2 = drs_finput('NULL_POL2', KW_OUTPUT='POL_NULL_POL2')
# out_pol_lsd = drs_finput('LSD_POL', KW_OUTPUT='POL_LSD')
# -----------------------------------------------------------------------------
# exposure map
# TODO: fill in definitions
# raw_em_spe = drs_finput('EM_SPE', KW_OUTPUT='EM_TELL_SPEC_RAW')
# raw_em_wave = drs_finput('EM_WAVE', KW_OUTPUT='EM_WAVEMAP_RAW')
# raw_em_mask = drs_finput('EM_MASK', KW_OUTPUT='EM_MASK_RAW')
# pp_em_spe = drs_finput('EM_SPE', KW_OUTPUT='EM_TELL_SPEC_PP')
# pp_em_wave = drs_finput('EM_WAVE', KW_OUTPUT='EM_WAVEMAP_PP')
# pp_em_mask = drs_finput('EM_MASK', KW_OUTPUT='EM_MASK_PP')
# out_em_spe = drs_finput('EM_SPE', KW_OUTPUT='EM_TELL_SPEC_DRS')
# out_em_wave = drs_finput('EM_WAVE', KW_OUTPUT='EM_WAVEMAP_DRS')
# out_em_mask = drs_finput('EM_MASK', KW_OUTPUT='EM_MASK_DRS')
# -----------------------------------------------------------------------------
# wave map
# TODO: fill in definitions
# raw_backmap_spe = drs_finput('WAVE_MAP_SPE',
#                              KW_OUTPUT='EM_WAVEMAP_SPE_RAW')
# raw_backmap_spe0 = drs_finput('WAVE_MAP_SPE0',
#                               KW_OUTPUT='EM_WAVEMAP_SPE0_RAW')
# pp_backmap_spe = drs_finput('WAVE_MAP_SPE',
#                             KW_OUTPUT='EM_WAVEMAP_SPE_PP')
# pp_backmap_spe0 = drs_finput('WAVE_MAP_SPE0',
#                              KW_OUTPUT='EM_WAVEMAP_SPE0_PP')
# out_backmap_spe = drs_finput('WAVE_MAP_SPE',
#                              KW_OUTPUT='EM_WAVEMAP_SPE_DRS')
# out_backmap_spe0 = drs_finput('WAVE_MAP_SPE0',
#                               KW_OUTPUT='EM_WAVEMAP_SPE0_DRS')

# =============================================================================
# End of code
# =============================================================================
