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
from apero.core import constants
from apero.core.core import drs_file
from apero.core.instruments.spirou import output_filenames as out

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'config.instruments.nirps_ha.file_defintions.py'
__INSTRUMENT__ = 'NIRPS_HA'
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
drs_ninput = drs_file.DrsNpyFile

# =============================================================================
# Raw Files
# =============================================================================
# prefix for raw files
raw_prefix = 'RAW_'
# Must add to list of raw files!!
raw_files = []
# =============================================================================
# generic raw file
raw_file = drs_finput('DRS_RAW', filetype='.fits', suffix='',
                      outfunc=out.blank)
# -----------------------------------------------------------------------------
# raw dark files
# raw_dark_dark = drs_finput('RAW_DARK_DARK', KW_CCAS='pos_pk', KW_CREF='pos_pk',
#                            KW_OBSTYPE='DARK',
#                            filetype='.fits', suffix='', inext='d.fits',
#                            outfunc=out.blank)
# raw_file.addset(raw_dark_dark)

# raw dark in P4 (internal dark)
raw_dark_dark_int = drs_finput('RAW_DARK_DARK_INT', KW_CCAS='pos_pk',
                               KW_CREF='pos_pk', KW_OBSTYPE='DARK',
                               KW_CALIBWH='P4',
                               filetype='.fits', suffix='', inext='.fits',
                               outfunc=out.blank)
raw_file.addset(raw_dark_dark_int)

# raw dark in P5 (telescope dark)
raw_dark_dark_tel = drs_finput('RAW_DARK_DARK_TEL', KW_CCAS='pos_pk',
                               KW_CREF='pos_pk', KW_OBSTYPE='DARK',
                               KW_CALIBWH='P5',
                               filetype='.fits', suffix='', inext='.fits',
                               outfunc=out.blank)
raw_file.addset(raw_dark_dark_tel)

# sky observation (sky dark)
raw_dark_dark_sky = drs_finput('RAW_DARK_DARK_SKY', KW_CCAS='pos_pk',
                               KW_CREF='pos_pk',
                               KW_OBSTYPE='OBJECT',
                               KW_TARGET_TYPE='SKY',
                               filetype='.fits', suffix='', inext='.fits',
                               outfunc=out.blank)
raw_file.addset(raw_dark_dark_sky)

# sky observations (with fp)
raw_dark_fp_sky = drs_finput('RAW_DARK_FP_SKY', KW_CCAS='pos_pk',
                             KW_CREF='pos_fp',
                             KW_OBSTYPE='OBJECT',
                             KW_TARGET_TYPE='SKY',
                             filetype='.fits', suffix='', inext='.fits',
                             outfunc=out.blank)
raw_file.addset(raw_dark_fp_sky)

# -----------------------------------------------------------------------------
# raw flat files
raw_dark_flat = drs_finput('RAW_DARK_FLAT', KW_CCAS='pos_pk', KW_CREF='pos_wl',
                           KW_OBSTYPE='FLAT', outfunc=out.blank,
                           filetype='.fits', suffix='')
raw_file.addset(raw_dark_flat)

raw_flat_dark = drs_finput('RAW_FLAT_DARK', KW_CCAS='pos_wl', KW_CREF='pos_pk',
                           KW_OBSTYPE='FLAT', outfunc=out.blank,
                           filetype='.fits', suffix='')
raw_file.addset(raw_flat_dark)

raw_flat_flat = drs_finput('RAW_FLAT_FLAT', KW_CCAS='pos_wl', KW_CREF='pos_wl',
                           KW_OBSTYPE='FLAT', outfunc=out.blank,
                           filetype='.fits', suffix='')
raw_file.addset(raw_flat_flat)

raw_flat_fp = drs_finput('RAW_FLAT_FP', KW_CCAS='pos_wl', KW_CREF='pos_fp',
                         KW_OBSTYPE='FLAT', outfunc=out.blank,
                         filetype='.fits', suffix='')
raw_file.addset(raw_flat_fp)

# -----------------------------------------------------------------------------
# raw align files
raw_dark_fp = drs_finput('RAW_DARK_FP', KW_CCAS='pos_pk', KW_CREF='pos_fp',
                         KW_OBSTYPE='ALIGN', outfunc=out.blank,
                         filetype='.fits', suffix='')
raw_file.addset(raw_dark_fp)

raw_fp_dark = drs_finput('RAW_FP_DARK', KW_CCAS='pos_fp', KW_CREF='pos_pk',
                         KW_OBSTYPE='ALIGN', outfunc=out.blank,
                         filetype='.fits', suffix='')
raw_file.addset(raw_fp_dark)

raw_fp_flat = drs_finput('RAW_FP_FLAT', KW_CCAS='pos_fp', KW_CREF='pos_wl',
                         KW_OBSTYPE='ALIGN', outfunc=out.blank,
                         filetype='.fits', suffix='')
raw_file.addset(raw_fp_flat)

raw_fp_fp = drs_finput('RAW_FP_FP', KW_CCAS='pos_fp', KW_CREF='pos_fp',
                       KW_OBSTYPE='ALIGN', outfunc=out.blank,
                       filetype='.fits', suffix='')
raw_file.addset(raw_fp_fp)

# -----------------------------------------------------------------------------
# raw LFC files
raw_lfc_lfc = drs_finput('RAW_LFC_LFC', KW_CCAS='pos_rs', KW_CREF='pos_rs',
                         filetype='.fits', suffix='', KW_OBSTYPE='ALIGN')
raw_file.addset(raw_lfc_lfc)

# -----------------------------------------------------------------------------
# raw object files
raw_obj_dark = drs_finput('RAW_OBJ_DARK', KW_CCAS='pos_pk', KW_CREF='pos_pk',
                          KW_OBSTYPE='OBJECT', outfunc=out.blank,
                          KW_TARGET_TYPE='TARGET',
                          filetype='.fits', suffix='', inext='.fits')
raw_file.addset(raw_obj_dark)

raw_obj_fp = drs_finput('RAW_OBJ_FP', KW_CCAS='pos_pk', KW_CREF='pos_fp',
                        KW_OBSTYPE='OBJECT', outfunc=out.blank,
                        KW_TARGET_TYPE='TARGET',
                        filetype='.fits', suffix='', inext='.fits')
raw_file.addset(raw_obj_fp)

raw_obj_hc1 = drs_finput('RAW_OBJ_HCONE', KW_CCAS='pos_pk', KW_CREF='pos_hc1',
                         KW_OBSTYPE='OBJECT', outfunc=out.blank,
                         KW_TARGET_TYPE='TARGET',
                         filetype='.fits', suffix='', inext='.fits')
raw_file.addset(raw_obj_hc1)

raw_obj_hc2 = drs_finput('RAW_OBJ_HCTWO', KW_CCAS='pos_pk', KW_CREF='pos_hc2',
                         KW_OBSTYPE='OBJECT', outfunc=out.blank,
                         KW_TARGET_TYPE='TARGET',
                         filetype='.fits', suffix='', inext='.fits')
raw_file.addset(raw_obj_hc2)

# -----------------------------------------------------------------------------
# raw comparison files
raw_dark_hc1 = drs_finput('RAW_DARK_HCONE', KW_CCAS='pos_pk', KW_CREF='pos_hc1',
                          KW_OBSTYPE='COMPARISON', outfunc=out.blank,
                          filetype='.fits', suffix='')
raw_file.addset(raw_dark_hc1)

raw_dark_hc2 = drs_finput('RAW_DARK_HCTWO', KW_CCAS='pos_pk', KW_CREF='pos_hc2',
                          KW_OBSTYPE='COMPARISON', outfunc=out.blank,
                          filetype='.fits', suffix='')
raw_file.addset(raw_dark_hc2)

raw_fp_hc1 = drs_finput('RAW_FP_HCONE', KW_CCAS='pos_fp', KW_CREF='pos_hc1',
                        KW_OBSTYPE='COMPARISON', outfunc=out.blank,
                        filetype='.fits', suffix='')
raw_file.addset(raw_fp_hc1)

raw_fp_hc2 = drs_finput('RAW_FP_HCTWO', KW_CCAS='pos_fp', KW_CREF='pos_hc2',
                        KW_OBSTYPE='COMPARISON', outfunc=out.blank,
                        filetype='.fits', suffix='')
raw_file.addset(raw_fp_hc2)

raw_hc1_fp = drs_finput('RAW_HCONE_FP', KW_CCAS='pos_hc1', KW_CREF='pos_fp',
                        KW_OBSTYPE='COMPARISON', outfunc=out.blank,
                        filetype='.fits', suffix='')
raw_file.addset(raw_hc1_fp)

raw_hc2_fp = drs_finput('RAW_HCTWO_FP', KW_CCAS='pos_hc2', KW_CREF='pos_fp',
                        KW_OBSTYPE='COMPARISON', outfunc=out.blank,
                        filetype='.fits', suffix='')
raw_file.addset(raw_hc2_fp)

raw_hc1_hc1 = drs_finput('RAW_HCONE_HCONE', KW_CCAS='pos_hc1',
                         KW_CREF='pos_hc1', KW_OBSTYPE='COMPARISON',
                         filetype='.fits', suffix='', outfunc=out.blank)
raw_file.addset(raw_hc1_hc1)

raw_hc2_hc2 = drs_finput('RAW_HCTWO_HCTWO', KW_CCAS='pos_hc2',
                         KW_CREF='pos_hc2', KW_OBSTYPE='COMPARISON',
                         filetype='.fits', suffix='', outfunc=out.blank)
raw_file.addset(raw_hc2_hc2)

raw_hc1_dark = drs_finput('RAW_HCONE_DARK', KW_CCAS='pos_hc1', KW_CREF='pos_pk',
                          KW_OBSTYPE='COMPARISON',
                          filetype='.fits', suffix='', outfunc=out.blank)
raw_file.addset(raw_hc1_dark)

raw_hc2_dark = drs_finput('RAW_HCTWO_DARK', KW_CCAS='pos_hc2', KW_CREF='pos_pk',
                          KW_OBSTYPE='COMPARISON',
                          filetype='.fits', suffix='', outfunc=out.blank)
raw_file.addset(raw_hc2_dark)

# =============================================================================
# Preprocessed Files
# =============================================================================
# generic pp file
pp_file = drs_finput('DRS_PP', filetype='.fits', suffix='_pp',
                     outfunc=out.general_file, intype=raw_file)
# -----------------------------------------------------------------------------
# dark
# pp_dark_dark = drs_finput('DARK_DARK', KW_DPRTYPE='DARK_DARK',
#                           filetype='.fits',
#                           suffix='_pp', intype=raw_dark_dark,
#                           inext='.fits', outfunc=out.general_file)
# pp_file.addset(pp_dark_dark)

pp_dark_dark_int = drs_finput('DARK_DARK_INT', KW_DPRTYPE='DARK_DARK_INT',
                              filetype='.fits',
                              suffix='_pp', intype=raw_dark_dark_int,
                              inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_dark_dark_int)

pp_dark_dark_tel = drs_finput('DARK_DARK_TEL', KW_DPRTYPE='DARK_DARK_TEL',
                              filetype='.fits',
                              suffix='_pp', intype=raw_dark_dark_tel,
                              inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_dark_dark_tel)

pp_dark_dark_sky = drs_finput('DARK_DARK_SKY', KW_DPRTYPE='DARK_DARK_SKY',
                              filetype='.fits',
                              suffix='_pp', intype=raw_dark_dark_sky,
                              inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_dark_dark_sky)

pp_dark_fp_sky = drs_finput('DARK_FP_SKY', KW_DPRTYPE='DARK_FP_SKY',
                            filetype='.fits',
                            suffix='_pp', intype=raw_dark_fp_sky,
                            inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_dark_fp_sky)

# -----------------------------------------------------------------------------
# flat
pp_flat_dark = drs_finput('FLAT_DARK', KW_DPRTYPE='FLAT_DARK',
                          filetype='.fits',
                          suffix='_pp', intype=raw_flat_dark,
                          inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_flat_dark)

pp_dark_flat = drs_finput('DARK_FLAT', KW_DPRTYPE='DARK_FLAT',
                          filetype='.fits',
                          suffix='_pp', intype=raw_dark_flat,
                          inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_dark_flat)

pp_flat_flat = drs_finput('FLAT_FLAT', KW_DPRTYPE='FLAT_FLAT',
                          filetype='.fits',
                          suffix='_pp', intype=raw_flat_flat,
                          inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_flat_flat)

pp_flat_fp = drs_finput('FLAT_FP', KW_DPRTYPE='FLAT_FP',
                        filetype='.fits',
                        suffix='_pp', intype=raw_flat_fp,
                        inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_flat_fp)
# -----------------------------------------------------------------------------
# align
pp_dark_fp = drs_finput('DARK_FP', KW_DPRTYPE='DARK_FP',
                        filetype='.fits',
                        suffix='_pp', intype=raw_dark_fp,
                        inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_dark_fp)
pp_fp_dark = drs_finput('FP_DARK', KW_DPRTYPE='FP_DARK',
                        filetype='.fits',
                        suffix='_pp', intype=raw_fp_dark,
                        inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_fp_dark)
pp_fp_flat = drs_finput('FP_FLAT', KW_DPRTYPE='FP_FLAT',
                        filetype='.fits',
                        suffix='_pp', intype=raw_fp_flat,
                        inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_fp_flat)
pp_fp_fp = drs_finput('FP_FP', KW_DPRTYPE='FP_FP',
                      filetype='.fits',
                      suffix='_pp', intype=raw_fp_fp,
                      inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_fp_fp)

# -----------------------------------------------------------------------------
# LFC
pp_lfc_lfc = drs_finput('LFC_LFC', KW_DPRTYPE='LFC_LFC',
                        filetype='.fits', suffix='_pp', intype=raw_lfc_lfc,
                        inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_lfc_lfc)

# -----------------------------------------------------------------------------
#  object
pp_obj_dark = drs_finput('OBJ_DARK', KW_DPRTYPE='OBJ_DARK',
                         filetype='.fits',
                         suffix='_pp', intype=raw_obj_dark,
                         inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_obj_dark)
pp_obj_fp = drs_finput('OBJ_FP', KW_DPRTYPE='OBJ_FP',
                       filetype='.fits',
                       suffix='_pp', intype=raw_obj_fp,
                       inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_obj_fp)
pp_obj_hc1 = drs_finput('OBJ_HC1', KW_DPRTYPE='OBJ_HCONE',
                        filetype='.fits',
                        suffix='_pp', intype=raw_obj_hc1,
                        inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_obj_hc1)
pp_obj_hc2 = drs_finput('OBJ_HC2', KW_DPRTYPE='OBJ_HCTWO',
                        filetype='.fits',
                        suffix='_pp', intype=raw_obj_hc2,
                        inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_obj_hc2)
# -----------------------------------------------------------------------------
#  comparison
pp_dark_hc1 = drs_finput('DARK_HCONE', KW_DPRTYPE='DARK_HCONE',
                         filetype='.fits',
                         suffix='_pp', intype=raw_dark_hc1,
                         inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_dark_hc1)
pp_dark_hc2 = drs_finput('DARK_HCTW0', KW_DPRTYPE='DARK_HCTW0',
                         filetype='.fits',
                         suffix='_pp', intype=raw_dark_hc2,
                         inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_dark_hc2)
pp_fp_hc1 = drs_finput('FP_HCONE', KW_DPRTYPE='FP_HCONE',
                       filetype='.fits',
                       suffix='_pp', intype=raw_fp_hc1,
                       inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_fp_hc1)
pp_fp_hc2 = drs_finput('FP_HCTWO', KW_DPRTYPE='FP_HCTWO',
                       filetype='.fits',
                       suffix='_pp', intype=raw_fp_hc2,
                       inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_fp_hc2)
pp_hc1_fp = drs_finput('HCONE_FP', KW_DPRTYPE='HCONE_FP',
                       filetype='.fits',
                       suffix='_pp', intype=raw_hc1_fp,
                       inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_hc1_fp)
pp_hc2_fp = drs_finput('HCTWO_FP', KW_DPRTYPE='HCTWO_FP',
                       filetype='.fits',
                       suffix='_pp', intype=raw_hc2_fp,
                       inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_hc2_fp)
pp_hc1_hc1 = drs_finput('HCONE_HCONE', KW_DPRTYPE='HCONE_HCONE',
                        filetype='.fits',
                        suffix='_pp', intype=raw_hc1_hc1,
                        inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_hc1_hc1)
pp_hc2_hc2 = drs_finput('HCTWO_HCTWO', KW_DPRTYPE='HCTWO_HCTWO',
                        filetype='.fits',
                        suffix='_pp', intype=raw_hc2_hc2,
                        inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_hc2_hc2)
pp_hc1_dark = drs_finput('HCONE_DARK', KW_DPRTYPE='HCONE_DARK',
                         filetype='.fits',
                         suffix='_pp', intype=raw_hc1_dark,
                         inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_hc1_dark)
pp_hc2_dark = drs_finput('HCTWO_DARK', KW_DPRTYPE='HCTWO_DARK',
                         filetype='.fits',
                         suffix='_pp', intype=raw_hc2_dark,
                         inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_hc2_dark)

# =============================================================================
# Reduced Files
# =============================================================================
# generic out file
out_file = drs_finput('DRS_OUTPUT', filetype='.fits', suffix='',
                      intype=pp_file)
# calib out file
calib_file = drs_finput('DRS_OUTPUT', filetype='.fits', suffix='',
                        intype=pp_file)
# telluric out file
tellu_file = drs_finput('DRS_OUTPUT', filetype='.fits', suffix='',
                        intype=pp_file)

# -----------------------------------------------------------------------------
# pp master files
# -----------------------------------------------------------------------------
out_pp_master = drs_finput('PPMSTR', KW_OUTPUT='PPMSTR', filetype='.fits',
                           intype=[raw_flat_flat],
                           suffix='_pmaster',
                           outfunc=out.calib_file,
                           dbname='calibration', dbkey='PPMSTR')
# add dark outputs to output fileset
out_file.addset(out_pp_master)
calib_file.addset(out_pp_master)

# -----------------------------------------------------------------------------
# dark files
# -----------------------------------------------------------------------------
# dark out file
# out_dark = drs_finput('DARK', KW_OUTPUT='DARK',
#                       filetype='.fits', intype=pp_dark_dark,
#                       suffix='',
#                       outfunc=out.calib_file,
#                       dbname='calibration', dbkey='DARK')

out_dark_int = drs_finput('DARKI', KW_OUTPUT='DARKI',
                          filetype='.fits', intype=pp_dark_dark_int,
                          suffix='_darki',
                          outfunc=out.calib_file,
                          dbname='calibration', dbkey='DARKI')

out_dark_tel = drs_finput('DARKT', KW_OUTPUT='DARKT',
                          filetype='.fits', intype=pp_dark_dark_tel,
                          suffix='_darkt',
                          outfunc=out.calib_file,
                          dbname='calibration', dbkey='DARKT')

out_dark_sky = drs_finput('DARKS', KW_OUTPUT='DARKS',
                          filetype='.fits', intype=pp_dark_dark_sky,
                          suffix='_darks',
                          outfunc=out.calib_file,
                          dbname='calibration', dbkey='DARKS')

out_dark_master = drs_finput('DARKM', KW_OUTPUT='DARKM',
                             filetype='.fits',
                             intype=[pp_dark_dark_tel, pp_dark_dark_int],
                             suffix='_dark_master',
                             outfunc=out.calib_file,
                             dbname='calibration', dbkey='DARKM')
# add dark outputs to output fileset
out_file.addset(out_dark_int)
out_file.addset(out_dark_tel)
out_file.addset(out_dark_sky)
out_file.addset(out_dark_master)
calib_file.addset(out_dark_int)
calib_file.addset(out_dark_tel)
calib_file.addset(out_dark_sky)
calib_file.addset(out_dark_master)

# -----------------------------------------------------------------------------
# Bad pixel / background files
# -----------------------------------------------------------------------------
# badpix out file
out_badpix = drs_finput('BADPIX', KW_OUTPUT='BADPIX',
                        filetype='.fits',
                        intype=[pp_flat_flat],
                        suffix='_badpixel',
                        outfunc=out.calib_file,
                        dbname='calibration', dbkey='BADPIX')
out_backmap = drs_finput('BKGRD_MAP', KW_OUTPUT='BKGRD_MAP',
                         intype=[pp_flat_flat],
                         suffix='_bmap.fits', outfunc=out.calib_file,
                         dbname='calibration', dbkey='BKGRDMAP')

# background debug file
debug_back = drs_finput('DEBUG_BACK', KW_OUTPUT='DEBUG_BACK',
                        filetype='.fits', intype=pp_file,
                        suffix='_background.fits', outfunc=out.debug_file)

# add badpix outputs to output fileset
out_file.addset(out_badpix)
out_file.addset(out_backmap)
out_file.addset(debug_back)
calib_file.addset(out_badpix)
calib_file.addset(out_backmap)

# -----------------------------------------------------------------------------
# localisation files
# -----------------------------------------------------------------------------
# localisation
out_loc_orderp = drs_finput('LOC_ORDERP', KW_OUTPUT='LOC_ORDERP',
                            fibers=['A', 'B'],
                            filetype='.fits',
                            intype=[pp_flat_dark, pp_dark_flat],
                            suffix='_order_profile',
                            outfunc=out.calib_file,
                            dbname='calibration', dbkey='ORDER_PROFILE')
out_loc_loco = drs_finput('LOC_LOCO', KW_OUTPUT='LOC_LOCO',
                          fibers=['A', 'B'],
                          filetype='.fits', intype=[pp_flat_dark, pp_dark_flat],
                          suffix='_loco',
                          outfunc=out.calib_file,
                          dbname='calibration', dbkey='LOC')
out_loc_fwhm = drs_finput('LOC_FWHM', KW_OUTPUT='LOC_FWHM',
                          fibers=['A', 'B'],
                          filetype='.fits', intype=[pp_flat_dark, pp_dark_flat],
                          suffix='_fwhm-order',
                          outfunc=out.calib_file)
out_loc_sup = drs_finput('LOC_SUP', KW_OUTPUT='LOC_SUP',
                         fibers=['A', 'B'],
                         filetype='.fits', intype=[pp_flat_dark, pp_dark_flat],
                         suffix='_with-order',
                         outfunc=out.calib_file)
# add localisation outputs to output fileset
out_file.addset(out_loc_orderp)
out_file.addset(out_loc_loco)
out_file.addset(out_loc_fwhm)
out_file.addset(out_loc_sup)
calib_file.addset(out_loc_orderp)
calib_file.addset(out_loc_loco)

# -----------------------------------------------------------------------------
# shape files (master)
# -----------------------------------------------------------------------------
# shape master
out_shape_dxmap = drs_finput('SHAPE_X', KW_OUTPUT='SHAPE_X',
                             filetype='.fits', intype=pp_fp_fp,
                             suffix='_shapex',
                             outfunc=out.calib_file,
                             dbname='calibration', dbkey='SHAPEX')
out_shape_dymap = drs_finput('SHAPE_Y', KW_OUTPUT='SHAPE_Y',
                             filetype='.fits', intype=pp_fp_fp,
                             suffix='_shapey',
                             outfunc=out.calib_file,
                             dbname='calibration', dbkey='SHAPEY')
out_shape_fpmaster = drs_finput('MASTER_FP', KW_OUTPUT='MASTER_FP',
                                filetype='.fits', intype=pp_fp_fp,
                                suffix='_fpmaster',
                                outfunc=out.calib_file,
                                dbname='calibration', dbkey='FPMASTER')
out_shape_debug_ifp = drs_finput('SHAPE_IN_FP', KW_OUTPUT='SHAPE_IN_FP',
                                 filetype='.fits', intype=pp_fp_fp,
                                 suffix='_shape_in_fp',
                                 outfunc=out.debug_file)
out_shape_debug_ofp = drs_finput('SHAPE_OUT_FP', KW_OUTPUT='SHAPE_OUT_FP',
                                 filetype='.fits', intype=pp_fp_fp,
                                 suffix='_shape_out_fp',
                                 outfunc=out.debug_file)
out_shape_debug_ihc = drs_finput('SHAPE_IN_HC', KW_OUTPUT='SHAPE_IN_HC',
                                 filetype='.fits', intype=pp_hc1_hc1,
                                 suffix='_shape_in_hc',
                                 outfunc=out.debug_file)
out_shape_debug_ohc = drs_finput('SHAPE_OUT_HC', KW_OUTPUT='SHAPE_OUT_HC',
                                 filetype='.fits', intype=pp_hc1_hc1,
                                 suffix='_shape_out_hc',
                                 outfunc=out.debug_file)
out_shape_debug_bdx = drs_finput('SHAPE_BDX', KW_OUTPUT='SHAPE_BDX',
                                 filetype='.fits', intype=pp_fp_fp,
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

calib_file.addset(out_shape_dxmap)
calib_file.addset(out_shape_dymap)
calib_file.addset(out_shape_fpmaster)

# -----------------------------------------------------------------------------
# shape files (per night)
# -----------------------------------------------------------------------------
# shape local
out_shape_local = drs_finput('SHAPEL', KW_OUTPUT='SHAPEL',
                             filetype='.fits', intype=pp_fp_fp,
                             suffix='_shapel',
                             outfunc=out.calib_file,
                             dbname='calibration', dbkey='SHAPEL')
out_shapel_debug_ifp = drs_finput('SHAPEL_IN_FP', KW_OUTPUT='SHAPEL_IN_FP',
                                  filetype='.fits', intype=pp_fp_fp,
                                  suffix='_shapel_in_fp.fits',
                                  outfunc=out.debug_file)

out_shapel_debug_ofp = drs_finput('SHAPEL_OUT_FP', KW_OUTPUT='SHAPEL_OUT_FP',
                                  filetype='.fits', intype=pp_fp_fp,
                                  suffix='_shapel_out_fp.fits',
                                  outfunc=out.debug_file)
# add shape local outputs to output fileset
out_file.addset(out_shape_local)
out_file.addset(out_shapel_debug_ifp)
out_file.addset(out_shapel_debug_ofp)
calib_file.addset(out_shape_local)

# -----------------------------------------------------------------------------
# flat files
# -----------------------------------------------------------------------------
# flat
out_ff_blaze = drs_finput('FF_BLAZE', KW_OUTPUT='FF_BLAZE',
                          fibers=['A', 'B'],
                          filetype='.fits', intype=pp_flat_flat,
                          suffix='_blaze',
                          dbname='calibration', dbkey='BLAZE',
                          outfunc=out.calib_file)
out_ff_flat = drs_finput('FF_FLAT', KW_OUTPUT='FF_FLAT',
                         fibers=['A', 'B'],
                         filetype='.fits', intype=pp_flat_flat,
                         suffix='_flat',
                         dbname='calibration', dbkey='FLAT',
                         outfunc=out.calib_file)

out_orderp_straight = drs_ninput('ORDERP_STRAIGHT', KW_OUTPUT='ORDERP_STRAIGHT',
                                 fibers=['A', 'B'],
                                 filetype='.npy', intype=pp_flat_flat,
                                 suffix='_orderp',
                                 outfunc=out.npy_file)

# add flat outputs to output fileset
out_file.addset(out_ff_blaze)
out_file.addset(out_ff_flat)
out_file.addset(out_orderp_straight)
calib_file.addset(out_ff_blaze)
calib_file.addset(out_ff_flat)

# -----------------------------------------------------------------------------
# extract files
# -----------------------------------------------------------------------------
# extract E2DS without flat fielding
out_ext_e2ds = drs_finput('EXT_E2DS', KW_OUTPUT='EXT_E2DS',
                          fibers=['A', 'B'],
                          filetype='.fits', intype=pp_file,
                          suffix='_e2ds', outfunc=out.general_file)
# extract E2DS with flat fielding
out_ext_e2dsff = drs_finput('EXT_E2DS_FF', KW_OUTPUT='EXT_E2DS_FF',
                            fibers=['A', 'B'],
                            filetype='.fits', intype=pp_file,
                            suffix='_e2dsff', outfunc=out.general_file,
                            s1d=['EXT_S1D_W', 'EXT_S1D_V'])
# pre-extract debug file
out_ext_e2dsll = drs_finput('EXT_E2DS_LL', KW_OUTPUT='EXT_E2DS_LL',
                            fibers=['A', 'B'],
                            filetype='.fits', intype=[pp_file, pp_flat_flat],
                            suffix='_e2dsll', outfunc=out.debug_file)
# extraction localisation file
out_ext_loco = drs_finput('EXT_LOCO', KW_OUTPUT='EXT_LOCO',
                          fibers=['A', 'B'],
                          filetype='.fits', intype=pp_file,
                          suffix='_e2dsloco', outfunc=out.debug_file)
# extract s1d without flat fielding (constant in wavelength)
out_ext_s1d_w = drs_finput('EXT_S1D_W', KW_OUTPUT='EXT_S1D_W',
                           fibers=['A', 'B'],
                           filetype='.fits', intype=pp_file, datatype='table',
                           suffix='_s1d_w', outfunc=out.general_file)
# extract s1d without flat fielding (constant in velocity)
out_ext_s1d_v = drs_finput('EXT_S1D_V', KW_OUTPUT='EXT_S1D_V',
                           fibers=['A', 'B'],
                           filetype='.fits', intype=pp_file, datatype='table',
                           suffix='_s1d_v', outfunc=out.general_file)

# fp line file from night
out_ext_fplines = drs_finput('EXT_FPLIST', KW_OUTPUT='EXT_FPLIST',
                                    fibers=['AB', 'A', 'B', 'C'],
                                    filetype='.fits', remove_insuffix=True,
                                    intype=[out_ext_e2ds, out_ext_e2dsff],
                                    suffix='_ext_fplines',
                                    outfunc=out.general_file)

# add extract outputs to output fileset
out_file.addset(out_ext_e2ds)
out_file.addset(out_ext_e2dsff)
out_file.addset(out_ext_e2dsll)
out_file.addset(out_ext_loco)
out_file.addset(out_ext_s1d_w)
out_file.addset(out_ext_s1d_v)
out_file.addset(out_ext_fplines)

# -----------------------------------------------------------------------------
# thermal files
# -----------------------------------------------------------------------------
# thermal from internal dark
out_thermal_e2ds_int = drs_finput('THERMALI_E2DS', KW_OUTPUT='THERMALI_E2DS',
                                  fibers=['A', 'B'],
                                  filetype='.fits', intype=pp_dark_dark_int,
                                  suffix='_thermal_e2ds_int',
                                  dbname='calibration', dbkey='THERMALI',
                                  outfunc=out.general_file)

# thermal from telescope dark
out_thermal_e2ds_tel = drs_finput('THERMALT_E2DS', KW_OUTPUT='THERMALT_E2DS',
                                  fibers=['A', 'B'],
                                  filetype='.fits', intype=pp_dark_dark_tel,
                                  suffix='_thermal_e2ds_tel',
                                  dbname='calibration', dbkey='THERMALT',
                                  outfunc=out.general_file)

# add thermal outputs to output fileset
out_file.addset(out_thermal_e2ds_int)
out_file.addset(out_thermal_e2ds_tel)
calib_file.addset(out_thermal_e2ds_int)
calib_file.addset(out_thermal_e2ds_tel)

# -----------------------------------------------------------------------------
# leakage files
# -----------------------------------------------------------------------------
# thermal from internal dark
out_leak_master = drs_finput('LEAKM_E2DS', KW_OUTPUT='LEAKM_E2DS',
                             fibers=['AB', 'A', 'B', 'C'],
                             filetype='.fits',
                             intype=[out_ext_e2ds, out_ext_e2dsff],
                             suffix='_leak_master',
                             dbname='calibration', dbkey='LEAKM',
                             outfunc=out.general_file)
out_file.addset(out_leak_master)
calib_file.addset(out_leak_master)

# -----------------------------------------------------------------------------
# wave files (master)
# -----------------------------------------------------------------------------
# wave solution using hc only
out_wavem_hc = drs_finput('WAVEM_HC', KW_OUTPUT='WAVEM_HC',
                          fibers=['A', 'B'],
                          filetype='.fits',
                          intype=[out_ext_e2ds, out_ext_e2dsff],
                          suffix='_wavem_hc',
                          dbname='calibration', dbkey='WAVEM',
                          outfunc=out.calib_file)

# wave solution using hc + fp
out_wavem_fp = drs_finput('WAVEM_FP', KW_OUTPUT='WAVEM_FP',
                          fibers=['A', 'B'],
                          filetype='.fits',
                          intype=[out_ext_e2ds, out_ext_e2dsff],
                          suffix='_wavem_fp',
                          dbname='calibration', dbkey='WAVEM',
                          outfunc=out.calib_file)

# hc resolution map
out_wavem_hcres = drs_finput('WAVERES', KW_OUTPUT='WAVE_RES',
                             fibers=['A', 'B'],
                             filetype='.fits',
                             intype=[out_ext_e2ds, out_ext_e2dsff],
                             suffix='_wavemres',
                             outfunc=out.calib_file)

# fp global results table
out_wavem_res_table = drs_input('WAVE_FPRESTAB', KW_OUTPUT='WAVE_FPRESTAB',
                                fibers=['A', 'B'],
                                filetype='.tbl',
                                intype=[out_ext_e2ds, out_ext_e2dsff],
                                outfunc=out.set_file,
                                basename='cal_wave_results')

# fp line list table
out_wavem_ll_table = drs_input('WAVE_FPLLTABL', KW_OUTPUT='WAVE_FPLLTAB',
                               fibers=['A', 'B'],
                               filetype='.tbl',
                               intype=[out_ext_e2ds, out_ext_e2dsff],
                               suffix='_mhc_lines',
                               outfunc=out.calib_file)

# hc line file from master
out_wave_hclist_master = drs_finput('WAVE_HCLIST_MASTER',
                                    KW_OUTPUT='WAVE_HCLIST_MASTER',
                                    fibers=['A', 'B'],
                                    filetype='.fits',
                                    intype=[out_ext_e2ds, out_ext_e2dsff],
                                    suffix='_wavem_hclines',
                                    dbname='calibration', dbkey='WAVEHCL',
                                    datatype='table',
                                    outfunc=out.calib_file)

# fp line file from master
out_wave_fplist_master = drs_finput('WAVE_FPLIST_MASTER',
                                    KW_OUTPUT='WAVE_FPLIST_MASTER',
                                    fibers=['A', 'B'],
                                    filetype='.fits',
                                    intype=[out_ext_e2ds, out_ext_e2dsff],
                                    suffix='_wavem_fplines',
                                    dbname='calibration', dbkey='WAVEFPL',
                                    datatype='table',
                                    outfunc=out.calib_file)

# the default wave master
out_wave_master = drs_finput('WAVEM_D', KW_OUTPUT='WAVEM_SOL',
                             fibers=['A', 'B'],
                             filetype='.fits',
                             intype=[out_ext_e2ds, out_ext_e2dsff],
                             suffix='_wavem',
                             dbname='calibration', dbkey='WAVEM_D',
                             outfunc=out.calib_file)

# add wave outputs to output fileset
out_file.addset(out_wavem_hc)
out_file.addset(out_wavem_fp)
out_file.addset(out_wavem_hcres)
out_file.addset(out_wavem_res_table)
out_file.addset(out_wavem_ll_table)
out_file.addset(out_wave_hclist_master)
out_file.addset(out_wave_fplist_master)
out_file.addset(out_wave_master)
calib_file.addset(out_wavem_hc)
calib_file.addset(out_wavem_fp)
calib_file.addset(out_wave_master)
calib_file.addset(out_wave_hclist_master)
calib_file.addset(out_wave_fplist_master)

# -----------------------------------------------------------------------------
# wave files
# -----------------------------------------------------------------------------
# wave solution using hc only
out_wave_hc = drs_finput('WAVE_HC', KW_OUTPUT='WAVE_HC',
                         fibers=['A', 'B'],
                         filetype='.fits',
                         intype=[out_ext_e2ds, out_ext_e2dsff],
                         suffix='_wave_hc',
                         dbname='calibration', dbkey='WAVE',
                         outfunc=out.calib_file)

# wave solution using hc + fp
out_wave_fp = drs_finput('WAVE_FP', KW_OUTPUT='WAVE_FP',
                         fibers=['A', 'B'],
                         filetype='.fits',
                         intype=[out_ext_e2ds, out_ext_e2dsff],
                         suffix='_wave_fp',
                         dbname='calibration', dbkey='WAVE',
                         outfunc=out.calib_file)

# wave solution using night modifications
out_wave_night = drs_finput('WAVE_NIGHT', KW_OUTPUT='WAVE_NIGHT',
                            fibers=['A', 'B'],
                            filetype='.fits',
                            intype=[out_ext_e2ds, out_ext_e2dsff],
                            suffix='_wave_night',
                            dbname='calibration', dbkey='WAVE',
                            outfunc=out.calib_file)

# hc initial linelist
out_wave_hcline = drs_input('WAVEHCLL', KW_OUTPUT='WAVEHCLL',
                            fibers=['A', 'B'],
                            filetype='.dat',
                            intype=[out_ext_e2ds, out_ext_e2dsff],
                            suffix='_linelist',
                            outfunc=out.calib_file)

# hc resolution map
out_wave_hcres = drs_finput('WAVERES', KW_OUTPUT='WAVE_RES',
                            fibers=['A', 'B'],
                            filetype='.fits',
                            intype=[out_ext_e2ds, out_ext_e2dsff],
                            suffix='_waveres',
                            outfunc=out.calib_file)

# fp global results table
out_wave_res_table = drs_input('WAVE_FPRESTAB', KW_OUTPUT='WAVE_FPRESTAB',
                               fibers=['A', 'B'],
                               filetype='.tbl',
                               intype=[out_ext_e2ds, out_ext_e2dsff],
                               outfunc=out.set_file,
                               basename='cal_wave_results')

# fp line list table
out_wave_ll_table = drs_input('WAVE_FPLLTABL', KW_OUTPUT='WAVE_FPLLTAB',
                              fibers=['A', 'B'],
                              filetype='.tbl',
                              intype=[out_ext_e2ds, out_ext_e2dsff],
                              suffix='_hc_lines',
                              outfunc=out.calib_file)

# hc line file from night
out_wave_hclist = drs_finput('WAVE_HCLIST', KW_OUTPUT='WAVE_HCLIST',
                                    fibers=['A', 'B'],
                                    filetype='.fits',
                                    intype=[out_ext_e2ds, out_ext_e2dsff],
                                    suffix='_wave_hclines',
                                    outfunc=out.calib_file)

# fp line file from night
out_wave_fplist = drs_finput('WAVE_FPLIST', KW_OUTPUT='WAVE_FPLIST',
                                    fibers=['A', 'B'],
                                    filetype='.fits',
                                    intype=[out_ext_e2ds, out_ext_e2dsff],
                                    suffix='_wave_fplines',
                                    outfunc=out.calib_file)

# add wave outputs to output fileset
out_file.addset(out_wave_hc)
out_file.addset(out_wave_fp)
out_file.addset(out_wave_night)
out_file.addset(out_wave_hcline)
out_file.addset(out_wave_hcres)
out_file.addset(out_wave_res_table)
out_file.addset(out_wave_ll_table)
out_file.addset(out_wave_hclist)
out_file.addset(out_wave_fplist)
calib_file.addset(out_wave_hc)
calib_file.addset(out_wave_fp)
calib_file.addset(out_wave_night)

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
# make telluric
# -----------------------------------------------------------------------------
# cleaned spectrum
out_tellu_pclean = drs_finput('TELLU_PCLEAN', KW_OUTPUT='TELLU_PCLEAN',
                              fibers=['A', 'B'],
                              filetype='.fits', intype=out_ext_e2dsff,
                              suffix='_tellu_pclean', remove_insuffix=True,
                              dbname='telluric', dbkey='TELLU_PCLEAN',
                              outfunc=out.general_file)

# convolved tapas map (with wave solution)
out_tellu_conv = drs_ninput('TELLU_CONV', KW_OUTPUT='TELLU_CONV',
                            fibers=['A', 'B'],
                            filetype='.npy', intype=out_ext_e2dsff,
                            suffix='_tellu_conv', remove_insuffix=True,
                            dbname='telluric', dbkey='TELLU_CONV',
                            outfunc=out.general_file)


# tapas file in format for pre-cleaning
out_tellu_spl_npy = drs_ninput('TELLU_TAPAS', filetype='.npy',
                                basename='tapas_spl.npy',
                                dbname='telluric', dbkey='TELLU_TAPAS',
                                outfunc=out.set_file)

# transmission map
out_tellu_trans = drs_finput('TELLU_TRANS', KW_OUTPUT='TELLU_TRANS',
                             fibers=['A', 'B'],
                             filetype='.fits', intype=out_ext_e2dsff,
                             suffix='_tellu_trans', remove_insuffix=True,
                             dbname='telluric', dbkey='TELLU_TRANS',
                             outfunc=out.general_file)

# add make_telluric outputs to output fileset
out_file.addset(out_tellu_pclean)
out_file.addset(out_tellu_conv)
out_file.addset(out_tellu_trans)
out_file.addset(out_tellu_spl_npy)
tellu_file.addset(out_tellu_pclean)
tellu_file.addset(out_tellu_conv)
tellu_file.addset(out_tellu_trans)
tellu_file.addset(out_tellu_spl_npy)

# -----------------------------------------------------------------------------
# fit telluric
# -----------------------------------------------------------------------------
# absorption files (npy file)
out_tellu_abso_npy = drs_ninput('ABSO_NPY',
                                filetype='.npy',
                                basename='tellu_save.npy',
                                outfunc=out.set_file)

# telluric corrected e2ds spectrum
out_tellu_obj = drs_finput('TELLU_OBJ', KW_OUTPUT='TELLU_OBJ',
                           fibers=['A', 'B'],
                           filetype='.fits', intype=out_ext_e2dsff,
                           suffix='_e2dsff_tcorr', remove_insuffix=True,
                           dbname='telluric', dbkey='TELLU_OBJ',
                           outfunc=out.general_file,
                           s1d=['SC1D_W_FILE', 'SC1D_V_FILE'])

# telluric corrected s1d spectrum
out_tellu_sc1d_w = drs_finput('SC1D_W_FILE', KW_OUTPUT='SC1D_W_FILE',
                              fibers=['A', 'B'],
                              filetype='.fits', intype=out_ext_e2dsff,
                              suffix='_s1d_w_tcorr', remove_insuffix=True,
                              outfunc=out.general_file, datatype='table')
out_tellu_sc1d_v = drs_finput('SC1D_V_FILE', KW_OUTPUT='SC1D_V_FILE',
                              fibers=['A', 'B'],
                              filetype='.fits', intype=out_ext_e2dsff,
                              suffix='_s1d_v_tcorr', remove_insuffix=True,
                              outfunc=out.general_file, datatype='table')

# reconstructed telluric absorption file
out_tellu_recon = drs_finput('TELLU_RECON', KW_OUTPUT='TELLU_RECON',
                             fibers=['A', 'B'],
                             filetype='.fits', intype=out_ext_e2dsff,
                             suffix='_e2dsff_recon', remove_insuffix=True,
                             dbname='telluric', dbkey='TELLU_RECON',
                             outfunc=out.general_file,
                             s1d=['RC1D_W_FILE', 'RC1D_V_FILE'])

# reconstructed telluric 1d absorption
out_tellu_rc1d_w = drs_finput('RC1D_W_FILE', KW_OUTPUT='RC1D_W_FILE',
                              fibers=['A', 'B'],
                              filetype='.fits', intype=out_ext_e2dsff,
                              suffix='_s1d_w_recon', remove_insuffix=True,
                              outfunc=out.general_file, datatype='table')
out_tellu_rc1d_v = drs_finput('RC1D_V_FILE', KW_OUTPUT='RC1D_V_FILE',
                              fibers=['A', 'B'],
                              filetype='.fits', intype=out_ext_e2dsff,
                              suffix='_s1d_v_recon', remove_insuffix=True,
                              outfunc=out.general_file, datatype='table')

# add fit telluric outputs to output fileset
out_file.addset(out_tellu_abso_npy)
out_file.addset(out_tellu_obj)
out_file.addset(out_tellu_sc1d_w)
out_file.addset(out_tellu_sc1d_v)
out_file.addset(out_tellu_recon)
out_file.addset(out_tellu_rc1d_w)
out_file.addset(out_tellu_rc1d_v)
tellu_file.addset(out_tellu_obj)
tellu_file.addset(out_tellu_recon)

# -----------------------------------------------------------------------------
# make template files
# -----------------------------------------------------------------------------
# template file (median)
out_tellu_template = drs_finput('TELLU_TEMP', KW_OUTPUT='TELLU_TEMP',
                                fibers=['A', 'B'],
                                filetype='.fits',
                                intype=[out_ext_e2dsff, out_tellu_obj],
                                basename='Template',
                                dbname='telluric', dbkey='TELLU_TEMP',
                                outfunc=out.set_file)

# template cube file (after shift)
out_tellu_bigcube = drs_finput('TELLU_BIGCUBE', KW_OUTPUT='TELLU_BIGCUBE',
                               fibers=['A', 'B'],
                               filetype='.fits',
                               intype=[out_ext_e2dsff, out_tellu_obj],
                               basename='BigCube',
                               outfunc=out.set_file)

# template cube file (before shift)
out_tellu_bigcube0 = drs_finput('TELLU_BIGCUBE0', KW_OUTPUT='TELLU_BIGCUBE0',
                                fibers=['A', 'B'],
                                filetype='.fits',
                                intype=[out_ext_e2dsff, out_tellu_obj],
                                basename='BigCube0',
                                outfunc=out.set_file)

# s1d template file (median)
out_tellu_s1d_template = drs_finput('TELLU_TEMP_S1D',
                                    KW_OUTPUT='TELLU_TEMP_S1D',
                                    fibers=['A', 'B'],
                                    filetype='.fits',
                                    intype=[out_ext_e2dsff, out_tellu_obj],
                                    basename='Template_s1d', datatype='table',
                                    outfunc=out.set_file)

# s1d cibe file (after shift)
out_tellu_s1d_bigcube = drs_finput('TELLU_BIGCUBE_S1D',
                                   KW_OUTPUT='TELLU_BIGCUBE_S1D',
                                   fibers=['A', 'B'],
                                   filetype='.fits',
                                   intype=[out_ext_e2dsff, out_tellu_obj],
                                   basename='BigCube_s1d',
                                   outfunc=out.set_file)

# add make template outputs to output fileset
out_file.addset(out_tellu_template)
out_file.addset(out_tellu_bigcube)
out_file.addset(out_tellu_bigcube0)
out_file.addset(out_tellu_s1d_template)
out_file.addset(out_tellu_s1d_bigcube)
tellu_file.addset(out_tellu_template)

# -----------------------------------------------------------------------------
# ccf
# -----------------------------------------------------------------------------
# ccf out file
out_ccf_fits = drs_finput('CCF_RV', KW_OUTPUT='CCF_RV',
                          fibers=['A', 'B'],
                          filetype='.fits',
                          suffix='_ccf',
                          intype=[out_ext_e2dsff, out_tellu_obj],
                          datatype='table',
                          outfunc=out.general_file)

out_file.addset(out_ccf_fits)


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
# Other Files
# =============================================================================
other_ccf_mask_file = drs_input('CCF_MASK', filetype='.mas')

# =============================================================================
# End of code
# =============================================================================
