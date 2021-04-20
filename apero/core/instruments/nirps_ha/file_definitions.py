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
from apero.base import base
from apero.core.core import drs_file
from apero.core.instruments.spirou import output_filenames as out

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'config.instruments.nirps_ha.file_defintions.py'
__INSTRUMENT__ = 'NIRPS_HA'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__

# =============================================================================
# Define Files
# =============================================================================
drs_input = drs_file.DrsInputFile
drs_finput = drs_file.DrsFitsFile
drs_ninput = drs_file.DrsNpyFile
drs_oinput = drs_file.DrsOutFile

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

# raw dark
raw_dark_dark = drs_finput('RAW_DARK_DARK', filetype='.fits',
                               suffix='', inext='.fits', outfunc=out.blank,
                               hkeys=dict(KW_RAW_DPRTYPE='DARK'))
raw_file.addset(raw_dark_dark)

# sky observation (sky dark)
raw_dark_dark_sky = drs_finput('RAW_DARK_DARK_SKY', filetype='.fits',
                               suffix='', inext='.fits', outfunc=out.blank,
                               hkeys=dict(KW_RAW_DPRTYPE='EFF,SKY,SKY'))
raw_file.addset(raw_dark_dark_sky)

# sky observations (with fp)
# NIRPS-CHANGE: Not defined - this is a guess
raw_dark_fp_sky = drs_finput('RAW_DARK_FP_SKY', filetype='.fits', suffix='',
                             inext='.fits', outfunc=out.blank,
                             hkeys=dict(KW_RAW_DPRTYPE='SKY,FP'))
raw_file.addset(raw_dark_fp_sky)

# -----------------------------------------------------------------------------
# raw flat files
raw_dark_flat = drs_finput('RAW_DARK_FLAT', outfunc=out.blank, filetype='.fits',
                           suffix='',
                           hkeys=dict(KW_RAW_DPRTYPE='ORDERDEF,DARK,LAMP'))
raw_file.addset(raw_dark_flat)

raw_flat_dark = drs_finput('RAW_FLAT_DARK', outfunc=out.blank,
                           filetype='.fits', suffix='',
                           hkeys=dict(KW_RAW_DPRTYPE='ORDERDEF,LAMP,DARK'))
raw_file.addset(raw_flat_dark)

raw_flat_flat = drs_finput('RAW_FLAT_FLAT', outfunc=out.blank,
                           filetype='.fits', suffix='',
                           hkeys=dict(KW_RAW_DPRTYPE='FLAT,LAMP,LAMP'))
raw_file.addset(raw_flat_flat)

# NIRPS-CHANGE: Not defined - this is a guess
raw_flat_fp = drs_finput('RAW_FLAT_FP', outfunc=out.blank,
                         filetype='.fits', suffix='',
                         hkeys=dict(KW_RAW_DPRTYPE='FLAT,LAMP,FP'))
raw_file.addset(raw_flat_fp)

# -----------------------------------------------------------------------------
# raw align files
raw_dark_fp = drs_finput('RAW_DARK_FP', outfunc=out.blank,
                         filetype='.fits', suffix='',
                         hkeys=dict(KW_RAW_DPRTYPE='CONTAM,DARK,FP'))
raw_file.addset(raw_dark_fp)

raw_fp_dark = drs_finput('RAW_FP_DARK', outfunc=out.blank,
                         filetype='.fits', suffix='',
                         hkeys=dict(KW_RAW_DPRTYPE='CONTAM,FP,DARK'))
raw_file.addset(raw_fp_dark)

# NIRPS-CHANGE: Not defined - this is a guess
raw_fp_flat = drs_finput('RAW_FP_FLAT', outfunc=out.blank,
                         filetype='.fits', suffix='',
                         hkeys=dict(KW_RAW_DPRTYPE='CONTAM,FP,LAMP'))
raw_file.addset(raw_fp_flat)

raw_fp_fp = drs_finput('RAW_FP_FP', outfunc=out.blank,
                       filetype='.fits', suffix='',
                       hkeys=dict(KW_RAW_DPRTYPE='WAVE,FP,FP'))
raw_file.addset(raw_fp_fp)

# -----------------------------------------------------------------------------
# raw LFC files
# NIRPS-CHANGE: Not defined - this is a guess
raw_lfc_lfc = drs_finput('RAW_LFC_LFC', filetype='.fits', suffix='',
                         outfunc=out.blank,
                         hkeys=dict(KW_RAW_DPRTYPE='WAVE,LFC,LFC'))
raw_file.addset(raw_lfc_lfc)

# NIRPS-CHANGE: Not defined - this is a guess
raw_lfc_fp = drs_finput('RAW_LFC_FP',
                        filetype='.fits', suffix='',
                        hkeys=dict(KW_RAW_DPRTYPE='WAVE,LFC,FP'))
raw_file.addset(raw_lfc_fp)

# NIRPS-CHANGE: Not defined - this is a guess
raw_fp_lfc = drs_finput('RAW_FP_LFC',
                        filetype='.fits', suffix='',
                        hkeys=dict(KW_RAW_DPRTYPE='WAVE,FP,LFC'))
raw_file.addset(raw_fp_lfc)

# -----------------------------------------------------------------------------
# raw LED LED file
raw_led_led = drs_finput('RAW_LED_LED', filetype='.fits', suffix='',
                         hkeys=dict(KW_RAW_DPRTYPE='LED'))
raw_file.addset(raw_led_led)

# -----------------------------------------------------------------------------
# raw object files
raw_obj_dark = drs_finput('RAW_OBJ_DARK', outfunc=out.blank,
                          hkeys=dict(KW_RAW_DPRTYPE='OBJECT,STAR,DARK',
                                     KW_TARGET_TYPE='TARGET', ))
raw_file.addset(raw_obj_dark)

raw_obj_fp = drs_finput('RAW_OBJ_FP', outfunc=out.blank, filetype='.fits',
                        suffix='', inext='.fits',
                        hkeys=dict(KW_RAW_DPRTYPE='OBJECT,STAR,FP',
                                   KW_TARGET_TYPE='TARGET'))
raw_file.addset(raw_obj_fp)

raw_obj_hc1 = drs_finput('RAW_OBJ_HCONE', outfunc=out.blank,
                         filetype='.fits', suffix='', inext='.fits',
                         hkeys=dict(KW_RAW_DPRTYPE='OBJECT,STAR,UN1',
                                    KW_TARGET_TYPE='TARGET'))
raw_file.addset(raw_obj_hc1)

# -----------------------------------------------------------------------------
# raw comparison files
raw_dark_hc1 = drs_finput('RAW_DARK_HCONE', outfunc=out.blank,
                          filetype='.fits', suffix='',
                          hkeys=dict(KW_RAW_DPRTYPE='WAVE,DARK,UN1'))
raw_file.addset(raw_dark_hc1)

raw_fp_hc1 = drs_finput('RAW_FP_HCONE', outfunc=out.blank,
                        filetype='.fits', suffix='',
                        hkeys=dict(KW_RAW_DPRTYPE='WAVE,FP,UN1'))
raw_file.addset(raw_fp_hc1)

raw_hc1_fp = drs_finput('RAW_HCONE_FP', outfunc=out.blank,
                        filetype='.fits', suffix='',
                        hkeys=dict(KW_RAW_DPRTYPE='WAVE,UN1,FP'))
raw_file.addset(raw_hc1_fp)

raw_hc1_hc1 = drs_finput('RAW_HCONE_HCONE', filetype='.fits', suffix='',
                         outfunc=out.blank,
                         hkeys=dict(KW_RAW_DPRTYPE='WAVE,UN1,UN1'))
raw_file.addset(raw_hc1_hc1)

raw_hc1_dark = drs_finput('RAW_HCONE_DARK', filetype='.fits', suffix='',
                          outfunc=out.blank,
                          hkeys=dict(KW_RAW_DPRTYPE='WAVE,UN1,DARK'))
raw_file.addset(raw_hc1_dark)

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

pp_dark_dark = drs_finput('DARK_DARK_INT', filetype='.fits',
                              suffix='_pp', intype=raw_dark_dark,
                              inext='.fits', outfunc=out.general_file,
                              hkeys=dict(KW_DPRTYPE='DARK_DARK_INT', ))
pp_file.addset(pp_dark_dark)

pp_dark_dark_sky = drs_finput('DARK_DARK_SKY', filetype='.fits',
                              suffix='_pp', intype=raw_dark_dark_sky,
                              inext='.fits', outfunc=out.general_file,
                              hkeys=dict(KW_DPRTYPE='DARK_DARK_SKY'))
pp_file.addset(pp_dark_dark_sky)

pp_dark_fp_sky = drs_finput('DARK_FP_SKY', filetype='.fits',
                            suffix='_pp', intype=raw_dark_fp_sky,
                            inext='.fits', outfunc=out.general_file,
                            hkeys=dict(KW_DPRTYPE='DARK_FP_SKY'))
pp_file.addset(pp_dark_fp_sky)

# -----------------------------------------------------------------------------
# flat
pp_flat_dark = drs_finput('FLAT_DARK', filetype='.fits',
                          suffix='_pp', intype=raw_flat_dark,
                          inext='.fits', outfunc=out.general_file,
                          hkeys=dict(KW_DPRTYPE='FLAT_DARK'))
pp_file.addset(pp_flat_dark)

pp_dark_flat = drs_finput('DARK_FLAT', filetype='.fits',
                          suffix='_pp', intype=raw_dark_flat,
                          inext='.fits', outfunc=out.general_file,
                          hkeys=dict(KW_DPRTYPE='DARK_FLAT'))
pp_file.addset(pp_dark_flat)

pp_flat_flat = drs_finput('FLAT_FLAT', filetype='.fits',
                          suffix='_pp', intype=raw_flat_flat,
                          inext='.fits', outfunc=out.general_file,
                          hkeys=dict(KW_DPRTYPE='FLAT_FLAT'))
pp_file.addset(pp_flat_flat)

pp_flat_fp = drs_finput('FLAT_FP', filetype='.fits',
                        suffix='_pp', intype=raw_flat_fp,
                        inext='.fits', outfunc=out.general_file,
                        hkeys=dict(KW_DPRTYPE='FLAT_FP'))
pp_file.addset(pp_flat_fp)
# -----------------------------------------------------------------------------
# align
pp_dark_fp = drs_finput('DARK_FP', filetype='.fits',
                        suffix='_pp', intype=raw_dark_fp,
                        inext='.fits', outfunc=out.general_file,
                        hkeys=dict(KW_DPRTYPE='DARK_FP'))
pp_file.addset(pp_dark_fp)
pp_fp_dark = drs_finput('FP_DARK', filetype='.fits',
                        suffix='_pp', intype=raw_fp_dark,
                        inext='.fits', outfunc=out.general_file,
                        hkeys=dict(KW_DPRTYPE='FP_DARK'))
pp_file.addset(pp_fp_dark)
pp_fp_flat = drs_finput('FP_FLAT', filetype='.fits',
                        suffix='_pp', intype=raw_fp_flat,
                        inext='.fits', outfunc=out.general_file,
                        hkeys=dict(KW_DPRTYPE='FP_FLAT'))
pp_file.addset(pp_fp_flat)
pp_fp_fp = drs_finput('FP_FP', filetype='.fits',
                      suffix='_pp', intype=raw_fp_fp,
                      inext='.fits', outfunc=out.general_file,
                      hkeys=dict(KW_DPRTYPE='FP_FP'))
pp_file.addset(pp_fp_fp)

# -----------------------------------------------------------------------------
# LFC
pp_lfc_lfc = drs_finput('LFC_LFC', filetype='.fits', suffix='_pp',
                        intype=raw_lfc_lfc, inext='.fits',
                        outfunc=out.general_file,
                        hkeys=dict(KW_DPRTYPE='LFC_LFC'))
pp_file.addset(pp_lfc_lfc)

pp_lfc_fp = drs_finput('LFC_FP', hkeys=dict(KW_DPRTYPE='LFC_FP'),
                       filetype='.fits', suffix='_pp', intype=raw_lfc_fp,
                       inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_lfc_fp)

pp_fp_lfc = drs_finput('FP_LFC', hkeys=dict(KW_DPRTYPE='FP_LFC'),
                       filetype='.fits', suffix='_pp', intype=raw_fp_lfc,
                       inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_fp_lfc)

# -----------------------------------------------------------------------------
# LED LED file
pp_led_led = drs_finput('LED_LED', hkeys=dict(KW_DPRTYPE='LED_LED'),
                        filetype='.fits', suffix='_pp', intype=raw_led_led,
                        inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_led_led)

# -----------------------------------------------------------------------------
#  object
pp_obj_dark = drs_finput('OBJ_DARK', hkeys=dict(KW_DPRTYPE='OBJ_DARK'),
                         filetype='.fits',
                         suffix='_pp', intype=raw_obj_dark,
                         inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_obj_dark)
pp_obj_fp = drs_finput('OBJ_FP', hkeys=dict(KW_DPRTYPE='OBJ_FP'),
                       filetype='.fits',
                       suffix='_pp', intype=raw_obj_fp,
                       inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_obj_fp)
pp_obj_hc1 = drs_finput('OBJ_HC1', hkeys=dict(KW_DPRTYPE='OBJ_HCONE'),
                        filetype='.fits',
                        suffix='_pp', intype=raw_obj_hc1,
                        inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_obj_hc1)
# -----------------------------------------------------------------------------
#  comparison
pp_dark_hc1 = drs_finput('DARK_HCONE', hkeys=dict(KW_DPRTYPE='DARK_HCONE'),
                         filetype='.fits',
                         suffix='_pp', intype=raw_dark_hc1,
                         inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_dark_hc1)

pp_fp_hc1 = drs_finput('FP_HCONE', hkeys=dict(KW_DPRTYPE='FP_HCONE'),
                       filetype='.fits',
                       suffix='_pp', intype=raw_fp_hc1,
                       inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_fp_hc1)

pp_hc1_fp = drs_finput('HCONE_FP', hkeys=dict(KW_DPRTYPE='HCONE_FP'),
                       filetype='.fits',
                       suffix='_pp', intype=raw_hc1_fp,
                       inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_hc1_fp)

pp_hc1_hc1 = drs_finput('HCONE_HCONE', hkeys=dict(KW_DPRTYPE='HCONE_HCONE'),
                        filetype='.fits',
                        suffix='_pp', intype=raw_hc1_hc1,
                        inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_hc1_hc1)

pp_hc1_dark = drs_finput('HCONE_DARK', hkeys=dict(KW_DPRTYPE='HCONE_DARK'),
                         filetype='.fits',
                         suffix='_pp', intype=raw_hc1_dark,
                         inext='.fits', outfunc=out.general_file)
pp_file.addset(pp_hc1_dark)

# =============================================================================
# Reduced Files
# =============================================================================
# generic out file
red_file = drs_finput('DRS_OUTPUT', filetype='.fits', suffix='',
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
out_pp_master = drs_finput('PPMSTR', hkeys=dict(KW_OUTPUT='PPMSTR'), 
                           filetype='.fits',
                           intype=[raw_flat_flat],
                           suffix='_pmaster',
                           outfunc=out.calib_file,
                           dbname='calibration', dbkey='PPMSTR')
# add dark outputs to output fileset
red_file.addset(out_pp_master)
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

out_dark = drs_finput('DARKI', hkeys=dict(KW_OUTPUT='DARKI'),
                          filetype='.fits', intype=pp_dark_dark,
                          suffix='_darki',
                          outfunc=out.calib_file,
                          dbname='calibration', dbkey='DARKI')

out_dark_sky = drs_finput('DARKS', hkeys=dict(KW_OUTPUT='DARKS'),
                          filetype='.fits', intype=pp_dark_dark_sky,
                          suffix='_darks',
                          outfunc=out.calib_file,
                          dbname='calibration', dbkey='DARKS')

out_dark_master = drs_finput('DARKM', hkeys=dict(KW_OUTPUT='DARKM'),
                             filetype='.fits',
                             intype=[pp_dark_dark],
                             suffix='_dark_master',
                             outfunc=out.calib_file,
                             dbname='calibration', dbkey='DARKM')
# add dark outputs to output fileset
red_file.addset(out_dark)
red_file.addset(out_dark_sky)
red_file.addset(out_dark_master)
calib_file.addset(out_dark)
calib_file.addset(out_dark_sky)
calib_file.addset(out_dark_master)

# -----------------------------------------------------------------------------
# Bad pixel / background files
# -----------------------------------------------------------------------------
# badpix out file
out_badpix = drs_finput('BADPIX', hkeys=dict(KW_OUTPUT='BADPIX'),
                        filetype='.fits',
                        intype=[pp_flat_flat],
                        suffix='_badpixel',
                        outfunc=out.calib_file,
                        dbname='calibration', dbkey='BADPIX')
out_backmap = drs_finput('BKGRD_MAP', hkeys=dict(KW_OUTPUT='BKGRD_MAP'),
                         intype=[pp_flat_flat],
                         suffix='_bmap.fits', outfunc=out.calib_file,
                         dbname='calibration', dbkey='BKGRDMAP')

# background debug file
debug_back = drs_finput('DEBUG_BACK', hkeys=dict(KW_OUTPUT='DEBUG_BACK'),
                        filetype='.fits', intype=pp_file,
                        suffix='_background.fits', outfunc=out.debug_file)

# add badpix outputs to output fileset
red_file.addset(out_badpix)
red_file.addset(out_backmap)
red_file.addset(debug_back)
calib_file.addset(out_badpix)
calib_file.addset(out_backmap)

# -----------------------------------------------------------------------------
# localisation files
# -----------------------------------------------------------------------------
# localisation
out_loc_orderp = drs_finput('LOC_ORDERP', hkeys=dict(KW_OUTPUT='LOC_ORDERP'),
                            fibers=['A', 'B'],
                            filetype='.fits',
                            intype=[pp_flat_dark, pp_dark_flat],
                            suffix='_order_profile',
                            outfunc=out.calib_file,
                            dbname='calibration', dbkey='ORDER_PROFILE')
out_loc_loco = drs_finput('LOC_LOCO', hkeys=dict(KW_OUTPUT='LOC_LOCO'),
                          fibers=['A', 'B'],
                          filetype='.fits', intype=[pp_flat_dark, pp_dark_flat],
                          suffix='_loco',
                          outfunc=out.calib_file,
                          dbname='calibration', dbkey='LOC')
out_loc_fwhm = drs_finput('LOC_FWHM', hkeys=dict(KW_OUTPUT='LOC_FWHM'),
                          fibers=['A', 'B'],
                          filetype='.fits', intype=[pp_flat_dark, pp_dark_flat],
                          suffix='_fwhm-order',
                          outfunc=out.calib_file)
out_loc_sup = drs_finput('LOC_SUP', hkeys=dict(KW_OUTPUT='LOC_SUP'),
                         fibers=['A', 'B'],
                         filetype='.fits', intype=[pp_flat_dark, pp_dark_flat],
                         suffix='_with-order',
                         outfunc=out.calib_file)
# add localisation outputs to output fileset
red_file.addset(out_loc_orderp)
red_file.addset(out_loc_loco)
red_file.addset(out_loc_fwhm)
red_file.addset(out_loc_sup)
calib_file.addset(out_loc_orderp)
calib_file.addset(out_loc_loco)

# -----------------------------------------------------------------------------
# shape files (master)
# -----------------------------------------------------------------------------
# shape master
out_shape_dxmap = drs_finput('SHAPE_X', hkeys=dict(KW_OUTPUT='SHAPE_X'),
                             filetype='.fits', intype=pp_fp_fp,
                             suffix='_shapex',
                             outfunc=out.calib_file,
                             dbname='calibration', dbkey='SHAPEX')
out_shape_dymap = drs_finput('SHAPE_Y', hkeys=dict(KW_OUTPUT='SHAPE_Y'),
                             filetype='.fits', intype=pp_fp_fp,
                             suffix='_shapey',
                             outfunc=out.calib_file,
                             dbname='calibration', dbkey='SHAPEY')
out_shape_fpmaster = drs_finput('MASTER_FP', hkeys=dict(KW_OUTPUT='MASTER_FP'),
                                filetype='.fits', intype=pp_fp_fp,
                                suffix='_fpmaster',
                                outfunc=out.calib_file,
                                dbname='calibration', dbkey='FPMASTER')
out_shape_debug_ifp = drs_finput('SHAPE_IN_FP',
                                 hkeys=dict(KW_OUTPUT='SHAPE_IN_FP'),
                                 filetype='.fits', intype=pp_fp_fp,
                                 suffix='_shape_in_fp',
                                 outfunc=out.debug_file)
out_shape_debug_ofp = drs_finput('SHAPE_OUT_FP',
                                 hkeys=dict(KW_OUTPUT='SHAPE_OUT_FP'),
                                 filetype='.fits', intype=pp_fp_fp,
                                 suffix='_shape_out_fp',
                                 outfunc=out.debug_file)
out_shape_debug_ihc = drs_finput('SHAPE_IN_HC',
                                 hkeys=dict(KW_OUTPUT='SHAPE_IN_HC'),
                                 filetype='.fits', intype=pp_hc1_hc1,
                                 suffix='_shape_in_hc',
                                 outfunc=out.debug_file)
out_shape_debug_ohc = drs_finput('SHAPE_OUT_HC',
                                 hkeys=dict(KW_OUTPUT='SHAPE_OUT_HC'),
                                 filetype='.fits', intype=pp_hc1_hc1,
                                 suffix='_shape_out_hc',
                                 outfunc=out.debug_file)
out_shape_debug_bdx = drs_finput('SHAPE_BDX', hkeys=dict(KW_OUTPUT='SHAPE_BDX'),
                                 filetype='.fits', intype=pp_fp_fp,
                                 suffix='_shape_out_bdx',
                                 outfunc=out.debug_file)
# add shape master outputs to output fileset
red_file.addset(out_shape_dxmap)
red_file.addset(out_shape_dymap)
red_file.addset(out_shape_fpmaster)
red_file.addset(out_shape_debug_ifp)
red_file.addset(out_shape_debug_ofp)
red_file.addset(out_shape_debug_ihc)
red_file.addset(out_shape_debug_ohc)
red_file.addset(out_shape_debug_bdx)

calib_file.addset(out_shape_dxmap)
calib_file.addset(out_shape_dymap)
calib_file.addset(out_shape_fpmaster)

# -----------------------------------------------------------------------------
# shape files (per night)
# -----------------------------------------------------------------------------
# shape local
out_shape_local = drs_finput('SHAPEL', hkeys=dict(KW_OUTPUT='SHAPEL'),
                             filetype='.fits', intype=pp_fp_fp,
                             suffix='_shapel',
                             outfunc=out.calib_file,
                             dbname='calibration', dbkey='SHAPEL')
out_shapel_debug_ifp = drs_finput('SHAPEL_IN_FP',
                                  hkeys=dict(KW_OUTPUT='SHAPEL_IN_FP'),
                                  filetype='.fits', intype=pp_fp_fp,
                                  suffix='_shapel_in_fp.fits',
                                  outfunc=out.debug_file)

out_shapel_debug_ofp = drs_finput('SHAPEL_OUT_FP',
                                  hkeys=dict(KW_OUTPUT='SHAPEL_OUT_FP'),
                                  filetype='.fits', intype=pp_fp_fp,
                                  suffix='_shapel_out_fp.fits',
                                  outfunc=out.debug_file)
# add shape local outputs to output fileset
red_file.addset(out_shape_local)
red_file.addset(out_shapel_debug_ifp)
red_file.addset(out_shapel_debug_ofp)
calib_file.addset(out_shape_local)

# -----------------------------------------------------------------------------
# flat files
# -----------------------------------------------------------------------------
# flat
out_ff_blaze = drs_finput('FF_BLAZE', hkeys=dict(KW_OUTPUT='FF_BLAZE'),
                          fibers=['A', 'B'],
                          filetype='.fits', intype=pp_flat_flat,
                          suffix='_blaze',
                          dbname='calibration', dbkey='BLAZE',
                          outfunc=out.calib_file)
out_ff_flat = drs_finput('FF_FLAT', hkeys=dict(KW_OUTPUT='FF_FLAT'),
                         fibers=['A', 'B'],
                         filetype='.fits', intype=pp_flat_flat,
                         suffix='_flat',
                         dbname='calibration', dbkey='FLAT',
                         outfunc=out.calib_file)

out_orderp_straight = drs_ninput('ORDERP_STRAIGHT',
                                 hkeys=dict(KW_OUTPUT='ORDERP_STRAIGHT'),
                                 fibers=['A', 'B'],
                                 filetype='.npy', intype=out_shape_local,
                                 suffix='_orderps',
                                 outfunc=out.npy_file)

# add flat outputs to output fileset
red_file.addset(out_ff_blaze)
red_file.addset(out_ff_flat)
red_file.addset(out_orderp_straight)
calib_file.addset(out_ff_blaze)
calib_file.addset(out_ff_flat)

# -----------------------------------------------------------------------------
# extract files (quick look)
# -----------------------------------------------------------------------------
# extract E2DS without flat fielding
out_ql_e2ds = drs_finput('QL_E2DS', hkeys=dict(KW_OUTPUT='QL_E2DS'),
                         fibers=['A', 'B'],
                         filetype='.fits', intype=pp_file,
                         suffix='_q2ds', outfunc=out.general_file)

# extract E2DS with flat fielding
out_ql_e2dsff = drs_finput('QL_E2DS_FF', hkeys=dict(KW_OUTPUT='QL_E2DS_FF'),
                           fibers=['A', 'B'],
                           filetype='.fits', intype=pp_file,
                           suffix='_q2dsff', outfunc=out.general_file)

# -----------------------------------------------------------------------------
# extract files
# -----------------------------------------------------------------------------
# extract E2DS without flat fielding
out_ext_e2ds = drs_finput('EXT_E2DS', hkeys=dict(KW_OUTPUT='EXT_E2DS'),
                          fibers=['A', 'B'],
                          filetype='.fits', intype=pp_file,
                          suffix='_e2ds', outfunc=out.general_file)
# extract E2DS with flat fielding
out_ext_e2dsff = drs_finput('EXT_E2DS_FF', hkeys=dict(KW_OUTPUT='EXT_E2DS_FF'),
                            fibers=['A', 'B'],
                            filetype='.fits', intype=pp_file,
                            suffix='_e2dsff', outfunc=out.general_file,
                            s1d=['EXT_S1D_W', 'EXT_S1D_V'])
# pre-extract debug file
out_ext_e2dsll = drs_finput('EXT_E2DS_LL', hkeys=dict(KW_OUTPUT='EXT_E2DS_LL'),
                            fibers=['A', 'B'],
                            filetype='.fits', intype=[pp_file, pp_flat_flat],
                            suffix='_e2dsll', outfunc=out.debug_file)
# extraction localisation file
out_ext_loco = drs_finput('EXT_LOCO', hkeys=dict(KW_OUTPUT='EXT_LOCO'),
                          fibers=['A', 'B'],
                          filetype='.fits', intype=pp_file,
                          suffix='_e2dsloco', outfunc=out.debug_file)
# extract s1d without flat fielding (constant in wavelength)
out_ext_s1d_w = drs_finput('EXT_S1D_W', hkeys=dict(KW_OUTPUT='EXT_S1D_W'),
                           fibers=['A', 'B'],
                           filetype='.fits', intype=pp_file, datatype='table',
                           suffix='_s1d_w', outfunc=out.general_file)
# extract s1d without flat fielding (constant in velocity)
out_ext_s1d_v = drs_finput('EXT_S1D_V', hkeys=dict(KW_OUTPUT='EXT_S1D_V'),
                           fibers=['A', 'B'],
                           filetype='.fits', intype=pp_file, datatype='table',
                           suffix='_s1d_v', outfunc=out.general_file)

# fp line file from night
out_ext_fplines = drs_finput('EXT_FPLIST', hkeys=dict(KW_OUTPUT='EXT_FPLIST'),
                             fibers=['A', 'B'],
                             filetype='.fits', remove_insuffix=True,
                             intype=[out_ext_e2ds, out_ext_e2dsff],
                             suffix='_ext_fplines',
                             outfunc=out.general_file)

# add extract outputs to output fileset
red_file.addset(out_ext_e2ds)
red_file.addset(out_ext_e2dsff)
red_file.addset(out_ext_e2dsll)
red_file.addset(out_ext_loco)
red_file.addset(out_ext_s1d_w)
red_file.addset(out_ext_s1d_v)
red_file.addset(out_ext_fplines)

# -----------------------------------------------------------------------------
# leakage files
# -----------------------------------------------------------------------------
# thermal from internal dark
out_leak_master = drs_finput('LEAKM_E2DS', hkeys=dict(KW_OUTPUT='LEAKM_E2DS'),
                             fibers=['A', 'B'],
                             filetype='.fits',
                             intype=[out_ext_e2ds, out_ext_e2dsff],
                             suffix='_leak_master',
                             dbname='calibration', dbkey='LEAKM',
                             outfunc=out.general_file)
red_file.addset(out_leak_master)
calib_file.addset(out_leak_master)


# -----------------------------------------------------------------------------
# wave files (master) ea
# -----------------------------------------------------------------------------
# wave solution using hc + fp
out_wavem_sol = drs_finput('WAVESOL_MASTER',
                           hkeys=dict(KW_OUTPUT='WAVESOL_MASTER'),
                           fibers=['A', 'B'],
                           filetype='.fits',
                           intype=[out_ext_e2ds, out_ext_e2dsff],
                           suffix='_wavesol_master_',
                           dbname='calibration', dbkey='WAVESOL_MASTER',
                           outfunc=out.calib_file)

# hc line file from master
out_wave_hclist_master = drs_finput('WAVE_HCLIST_MASTER',
                                    hkeys=dict(KW_OUTPUT='WAVE_HCLIST_MASTER'),
                                    fibers=['A', 'B'],
                                    filetype='.fits',
                                    intype=[out_ext_e2ds, out_ext_e2dsff],
                                    suffix='_wavem_hclines',
                                    dbname='calibration', dbkey='WAVEHCL',
                                    datatype='table',
                                    outfunc=out.calib_file)

# fp line file from master
out_wave_fplist_master = drs_finput('WAVE_FPLIST_MASTER',
                                    hkeys=dict(KW_OUTPUT='WAVE_FPLIST_MASTER'),
                                    fibers=['A', 'B'],
                                    filetype='.fits',
                                    intype=[out_ext_e2ds, out_ext_e2dsff],
                                    suffix='_wavem_fplines',
                                    dbname='calibration', dbkey='WAVEFPL',
                                    datatype='table',
                                    outfunc=out.calib_file)

# teh cavity file polynomial file
out_wavem_cavity = drs_finput('WAVEM_CAV', hkeys=dict(KW_OUTPUT='WAVEM_CAV'),
                              filetype='.fits',
                              intype=[out_ext_e2ds, out_ext_e2dsff],
                              suffix='_wavecav_',
                              dbname='calibration', dbkey='WAVECAV',
                              outfunc=out.calib_file)

# the default wave master
out_wave_master = drs_finput('WAVEM_D', hkeys=dict(KW_OUTPUT='WAVEM_SOL'),
                             fibers=['A', 'B'],
                             filetype='.fits',
                             intype=[out_ext_e2ds, out_ext_e2dsff],
                             suffix='_wavem',
                             dbname='calibration', dbkey='WAVEM_D',
                             outfunc=out.calib_file)

# add wave outputs to output fileset
red_file.addset(out_wavem_sol)
red_file.addset(out_wave_hclist_master)
red_file.addset(out_wave_fplist_master)
red_file.addset(out_wavem_cavity)
red_file.addset(out_wave_master)
calib_file.addset(out_wavem_sol)
calib_file.addset(out_wave_hclist_master)
calib_file.addset(out_wave_fplist_master)
calib_file.addset(out_wavem_cavity)
calib_file.addset(out_wave_master)

# -----------------------------------------------------------------------------
# wave files (master) old
# -----------------------------------------------------------------------------
# old wave fp
out_wavem_fp = drs_finput('WAVEM_FP',
                          hkeys=dict(KW_OUTPUT='WAVEM_FP'),
                          fibers=['A', 'B'],
                          filetype='.fits',
                          intype=[out_ext_e2ds, out_ext_e2dsff],
                          suffix='_wavem_fp',
                          dbname='calibration', dbkey='WAVESOL_MASTER',
                          outfunc=out.calib_file)


# wave solution using hc only
out_wavem_hc = drs_finput('WAVEM_HC', hkeys=dict(KW_OUTPUT='WAVEM_HC'),
                          fibers=['A', 'B'],
                          filetype='.fits',
                          intype=[out_ext_e2ds, out_ext_e2dsff],
                          suffix='_wavem_hc',
                          dbname='calibration', dbkey='WAVEM',
                          outfunc=out.calib_file)

# resolution map
out_wavem_res = drs_finput('WAVERES', hkeys=dict(KW_OUTPUT='WAVE_RES'),
                             fibers=['A', 'B'],
                             filetype='.fits',
                             intype=[out_ext_e2ds, out_ext_e2dsff],
                             suffix='_wavemres',
                             outfunc=out.calib_file)

# hc resolution map
out_wavem_hcres = drs_finput('WAVERES', hkeys=dict(KW_OUTPUT='WAVE_RES'),
                             fibers=['A', 'B'],
                             filetype='.fits',
                             intype=[out_ext_e2ds, out_ext_e2dsff],
                             suffix='_wavemres',
                             outfunc=out.calib_file)

# fp global results table
out_wavem_res_table = drs_input('WAVE_FPRESTAB',
                                hkeys=dict(KW_OUTPUT='WAVE_FPRESTAB'),
                                fibers=['A', 'B'],
                                filetype='.tbl',
                                intype=[out_ext_e2ds, out_ext_e2dsff],
                                outfunc=out.set_file,
                                basename='cal_wave_results')

# fp line list table
out_wavem_ll_table = drs_input('WAVE_FPLLTABL',
                               hkeys=dict(KW_OUTPUT='WAVE_FPLLTAB'),
                               fibers=['A', 'B'],
                               filetype='.tbl',
                               intype=[out_ext_e2ds, out_ext_e2dsff],
                               suffix='_mhc_lines',
                               outfunc=out.calib_file)

# add wave outputs to output fileset
red_file.addset(out_wavem_fp)
red_file.addset(out_wavem_hc)
red_file.addset(out_wavem_hcres)
red_file.addset(out_wavem_res_table)
red_file.addset(out_wavem_ll_table)
calib_file.addset(out_wavem_fp)
calib_file.addset(out_wavem_hc)

# -----------------------------------------------------------------------------
# wave files
# -----------------------------------------------------------------------------
# wave solution using hc only
out_wave_hc = drs_finput('WAVE_HC', hkeys=dict(KW_OUTPUT='WAVE_HC'),
                         fibers=['A', 'B'],
                         filetype='.fits',
                         intype=[out_ext_e2ds, out_ext_e2dsff],
                         suffix='_wave_hc',
                         dbname='calibration', dbkey='WAVE',
                         outfunc=out.calib_file)

# wave solution using hc + fp
out_wave_fp = drs_finput('WAVE_FP', hkeys=dict(KW_OUTPUT='WAVE_FP'),
                         fibers=['A', 'B'],
                         filetype='.fits',
                         intype=[out_ext_e2ds, out_ext_e2dsff],
                         suffix='_wave_fp',
                         dbname='calibration', dbkey='WAVE',
                         outfunc=out.calib_file)

# wave solution using night modifications
out_wave_night = drs_finput('WAVE_NIGHT', hkeys=dict(KW_OUTPUT='WAVE_NIGHT'),
                            fibers=['A', 'B'],
                            filetype='.fits',
                            intype=[out_ext_e2ds, out_ext_e2dsff],
                            suffix='_wave_night',
                            dbname='calibration', dbkey='WAVE',
                            outfunc=out.calib_file)

# hc initial linelist
out_wave_hcline = drs_input('WAVEHCLL', hkeys=dict(KW_OUTPUT='WAVEHCLL'),
                            fibers=['A', 'B'],
                            filetype='.dat',
                            intype=[out_ext_e2ds, out_ext_e2dsff],
                            suffix='_linelist',
                            outfunc=out.calib_file)

# hc resolution map
out_wave_hcres = drs_finput('WAVERES', hkeys=dict(KW_OUTPUT='WAVE_RES'),
                            fibers=['A', 'B'],
                            filetype='.fits',
                            intype=[out_ext_e2ds, out_ext_e2dsff],
                            suffix='_waveres',
                            outfunc=out.calib_file)

# fp global results table
out_wave_res_table = drs_input('WAVE_FPRESTAB',
                               hkeys=dict(KW_OUTPUT='WAVE_FPRESTAB'),
                               fibers=['A', 'B'],
                               filetype='.tbl',
                               intype=[out_ext_e2ds, out_ext_e2dsff],
                               outfunc=out.set_file,
                               basename='cal_wave_results')

# fp line list table
out_wave_ll_table = drs_input('WAVE_FPLLTABL',
                              hkeys=dict(KW_OUTPUT='WAVE_FPLLTAB'),
                              fibers=['A', 'B'],
                              filetype='.tbl',
                              intype=[out_ext_e2ds, out_ext_e2dsff],
                              suffix='_hc_lines',
                              outfunc=out.calib_file)

# hc line file from night
out_wave_hclist = drs_finput('WAVE_HCLIST', hkeys=dict(KW_OUTPUT='WAVE_HCLIST'),
                             fibers=['A', 'B'],
                             filetype='.fits',
                             intype=[out_ext_e2ds, out_ext_e2dsff],
                             suffix='_wave_hclines',
                             outfunc=out.calib_file)

# fp line file from night
out_wave_fplist = drs_finput('WAVE_FPLIST', hkeys=dict(KW_OUTPUT='WAVE_FPLIST'),
                             fibers=['A', 'B'],
                             filetype='.fits',
                             intype=[out_ext_e2ds, out_ext_e2dsff],
                             suffix='_wave_fplines',
                             outfunc=out.calib_file)

# add wave outputs to output fileset
red_file.addset(out_wave_hc)
red_file.addset(out_wave_fp)
red_file.addset(out_wave_night)
red_file.addset(out_wave_hcline)
red_file.addset(out_wave_hcres)
red_file.addset(out_wave_res_table)
red_file.addset(out_wave_ll_table)
red_file.addset(out_wave_hclist)
red_file.addset(out_wave_fplist)
calib_file.addset(out_wave_hc)
calib_file.addset(out_wave_fp)
calib_file.addset(out_wave_night)

# -----------------------------------------------------------------------------
# make telluric
# -----------------------------------------------------------------------------
# cleaned spectrum
out_tellu_pclean = drs_finput('TELLU_PCLEAN',
                              hkeys=dict(KW_OUTPUT='TELLU_PCLEAN'),
                              fibers=['A', 'B'],
                              filetype='.fits', intype=out_ext_e2dsff,
                              suffix='_tellu_pclean', remove_insuffix=True,
                              dbname='telluric', dbkey='TELLU_PCLEAN',
                              outfunc=out.general_file)

# convolved tapas map (with master wave solution)
out_tellu_conv = drs_ninput('TELLU_CONV', hkeys=dict(KW_OUTPUT='TELLU_CONV'),
                            fibers=['A', 'B'],
                            filetype='.npy',
                            intype=[out_wavem_fp, out_wavem_hc],
                            suffix='_tellu_conv', remove_insuffix=True,
                            dbname='telluric', dbkey='TELLU_CONV',
                            outfunc=out.general_file)

# tapas file in format for pre-cleaning
out_tellu_spl_npy = drs_ninput('TELLU_TAPAS', filetype='.npy',
                               basename='tapas_spl.npy',
                               dbname='telluric', dbkey='TELLU_TAPAS',
                               outfunc=out.set_file)

# transmission map
out_tellu_trans = drs_finput('TELLU_TRANS', hkeys=dict(KW_OUTPUT='TELLU_TRANS'),
                             fibers=['A', 'B'],
                             filetype='.fits', intype=out_ext_e2dsff,
                             suffix='_tellu_trans', remove_insuffix=True,
                             dbname='telluric', dbkey='TELLU_TRANS',
                             outfunc=out.general_file)

# add make_telluric outputs to output fileset
red_file.addset(out_tellu_pclean)
red_file.addset(out_tellu_conv)
red_file.addset(out_tellu_trans)
red_file.addset(out_tellu_spl_npy)
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
out_tellu_abso1_npy = drs_ninput('ABSO1_NPY',
                                 filetype='.npy',
                                 basename='tellu_save1.npy',
                                 outfunc=out.set_file)

# telluric corrected e2ds spectrum
out_tellu_obj = drs_finput('TELLU_OBJ', hkeys=dict(KW_OUTPUT='TELLU_OBJ'),
                           fibers=['A', 'B'],
                           filetype='.fits', intype=out_ext_e2dsff,
                           suffix='_e2dsff_tcorr', remove_insuffix=True,
                           dbname='telluric', dbkey='TELLU_OBJ',
                           outfunc=out.general_file,
                           s1d=['SC1D_W_FILE', 'SC1D_V_FILE'])

# telluric corrected s1d spectrum
out_tellu_sc1d_w = drs_finput('SC1D_W_FILE',
                              hkeys=dict(KW_OUTPUT='SC1D_W_FILE'),
                              fibers=['A', 'B'],
                              filetype='.fits', intype=out_ext_e2dsff,
                              suffix='_s1d_w_tcorr', remove_insuffix=True,
                              outfunc=out.general_file, datatype='table')
out_tellu_sc1d_v = drs_finput('SC1D_V_FILE',
                              hkeys=dict(KW_OUTPUT='SC1D_V_FILE'),
                              fibers=['A', 'B'],
                              filetype='.fits', intype=out_ext_e2dsff,
                              suffix='_s1d_v_tcorr', remove_insuffix=True,
                              outfunc=out.general_file, datatype='table')

# reconstructed telluric absorption file
out_tellu_recon = drs_finput('TELLU_RECON', hkeys=dict(KW_OUTPUT='TELLU_RECON'),
                             fibers=['A', 'B'],
                             filetype='.fits', intype=out_ext_e2dsff,
                             suffix='_e2dsff_recon', remove_insuffix=True,
                             dbname='telluric', dbkey='TELLU_RECON',
                             outfunc=out.general_file,
                             s1d=['RC1D_W_FILE', 'RC1D_V_FILE'])

# reconstructed telluric 1d absorption
out_tellu_rc1d_w = drs_finput('RC1D_W_FILE',
                              hkeys=dict(KW_OUTPUT='RC1D_W_FILE'),
                              fibers=['A', 'B'],
                              filetype='.fits', intype=out_ext_e2dsff,
                              suffix='_s1d_w_recon', remove_insuffix=True,
                              outfunc=out.general_file, datatype='table')
out_tellu_rc1d_v = drs_finput('RC1D_V_FILE',
                              hkeys=dict(KW_OUTPUT='RC1D_V_FILE'),
                              fibers=['A', 'B'],
                              filetype='.fits', intype=out_ext_e2dsff,
                              suffix='_s1d_v_recon', remove_insuffix=True,
                              outfunc=out.general_file, datatype='table')

# add fit telluric outputs to output fileset
red_file.addset(out_tellu_abso_npy)
red_file.addset(out_tellu_obj)
red_file.addset(out_tellu_sc1d_w)
red_file.addset(out_tellu_sc1d_v)
red_file.addset(out_tellu_recon)
red_file.addset(out_tellu_rc1d_w)
red_file.addset(out_tellu_rc1d_v)
tellu_file.addset(out_tellu_obj)
tellu_file.addset(out_tellu_recon)

# -----------------------------------------------------------------------------
# make template files
# -----------------------------------------------------------------------------
# template file (median)
out_tellu_template = drs_finput('TELLU_TEMP',
                                hkeys=dict(KW_OUTPUT='TELLU_TEMP'),
                                fibers=['A', 'B'],
                                filetype='.fits',
                                intype=[out_ext_e2dsff, out_tellu_obj],
                                basename='Template',
                                dbname='telluric', dbkey='TELLU_TEMP',
                                outfunc=out.set_file)

# template cube file (after shift)
out_tellu_bigcube = drs_finput('TELLU_BIGCUBE',
                               hkeys=dict(KW_OUTPUT='TELLU_BIGCUBE'),
                               fibers=['A', 'B'],
                               filetype='.fits',
                               intype=[out_ext_e2dsff, out_tellu_obj],
                               basename='BigCube',
                               outfunc=out.set_file)

# template cube file (before shift)
out_tellu_bigcube0 = drs_finput('TELLU_BIGCUBE0',
                                hkeys=dict(KW_OUTPUT='TELLU_BIGCUBE0'),
                                fibers=['A', 'B'],
                                filetype='.fits',
                                intype=[out_ext_e2dsff, out_tellu_obj],
                                basename='BigCube0',
                                outfunc=out.set_file)

# s1d template file (median)
out_tellu_s1d_template = drs_finput('TELLU_TEMP_S1D',
                                    hkeys=dict(KW_OUTPUT='TELLU_TEMP_S1D'),
                                    fibers=['A', 'B'],
                                    filetype='.fits',
                                    intype=[out_ext_e2dsff, out_tellu_obj],
                                    basename='Template_s1d', datatype='table',
                                    outfunc=out.set_file)

# s1d cibe file (after shift)
out_tellu_s1d_bigcube = drs_finput('TELLU_BIGCUBE_S1D',
                                   hkeys=dict(KW_OUTPUT='TELLU_BIGCUBE_S1D'),
                                   fibers=['A', 'B'],
                                   filetype='.fits',
                                   intype=[out_ext_e2dsff, out_tellu_obj],
                                   basename='BigCube_s1d',
                                   outfunc=out.set_file)

# add make template outputs to output fileset
red_file.addset(out_tellu_template)
red_file.addset(out_tellu_bigcube)
red_file.addset(out_tellu_bigcube0)
red_file.addset(out_tellu_s1d_template)
red_file.addset(out_tellu_s1d_bigcube)
tellu_file.addset(out_tellu_template)

# -----------------------------------------------------------------------------
# ccf
# -----------------------------------------------------------------------------
# ccf out file
out_ccf_fits = drs_finput('CCF_RV', hkeys=dict(KW_OUTPUT='CCF_RV'),
                          fibers=['A', 'B'],
                          filetype='.fits',
                          suffix='_ccf',
                          intype=[out_ext_e2dsff, out_tellu_obj],
                          datatype='table',
                          outfunc=out.general_file)

red_file.addset(out_ccf_fits)

# =============================================================================
# Post processed Files
# =============================================================================
# generic post processed file
post_file = drs_oinput('DRS_POST', filetype='.fits', suffix='',
                       outfunc=out.post_file)

# -----------------------------------------------------------------------------
# post processed 2D extraction file
# -----------------------------------------------------------------------------
post_e_file = drs_oinput('DRS_POST_E', filetype='.fits', suffix='e.fits',
                         outfunc=out.post_file, inext='o', required=False)
# add extensions
post_e_file.add_ext('PP', pp_file, pos=0, header_only=True, block_kind='tmp',
                    hkeys=dict(KW_DPRTYPE=['OBJ_FP', 'OBJ_DARK', 'POLAR_FP',
                                           'POLAR_DARK']),
                    remove_drs_hkeys=True, remove_std_hkeys=True)
post_e_file.add_ext('EXT_A', out_ext_e2dsff, pos=2, fiber='A', block_kind='red',
                    link='EXT_A', hlink='KW_IDENTIFIER', clear_file=True,
                    tag='FluxA')
post_e_file.add_ext('EXT_B', out_ext_e2dsff, pos=3, fiber='B', block_kind='red',
                    link='EXT_A', hlink='KW_IDENTIFIER', clear_file=True,
                    tag='FluxB')
post_e_file.add_ext('WAVE_A', out_wavem_fp, pos=6, fiber='A', block_kind='red',
                    link='EXT_A', hlink='KW_CDBWAVE',
                    tag='WaveA')
post_e_file.add_ext('WAVE_B', out_wavem_fp, pos=7, fiber='B', block_kind='red',
                    link='EXT_B', hlink='KW_CDBWAVE',
                    tag='WaveB')
post_e_file.add_ext('BLAZE_A', out_ff_blaze, pos=10, fiber='A',
                    block_kind='red', link='EXT_A', hlink='KW_CDBBLAZE',
                    tag='BlazeA')
post_e_file.add_ext('BLAZE_B', out_ff_blaze, pos=11, fiber='B',
                    block_kind='red', link='EXT_B', hlink='KW_CDBBLAZE',
                    tag='BlazeB')
# move header keys
post_e_file.add_hkey('KW_VERSION', inheader='VEL', outheader='PP')
post_e_file.add_hkey('KW_DRS_DATE_NOW', inheader='VEL', outheader='PP')
# add to post processed file set
post_file.addset(post_e_file)

# -----------------------------------------------------------------------------
# post processed 1D extraction file
# -----------------------------------------------------------------------------
post_s_file = drs_oinput('DRS_POST_S', filetype='.fits', suffix='s.fits',
                         outfunc=out.post_file, inext='o', required=False)
post_s_file.add_ext('PP', pp_file, pos=0, header_only=True, block_kind='tmp',
                    hkeys=dict(KW_DPRTYPE=['OBJ_FP', 'OBJ_DARK', 'POLAR_FP',
                                           'POLAR_DARK']))
# s1d w is a composite table
post_s_file.add_ext('S1D_W', 'table', pos=1, block_kind='red',
                    link='PP', hlink='KW_IDENTIFIER')
# add s1d w columns (all linked via PP file)
post_s_file.add_column('S1D_W', out_ext_s1d_w,
                       incol='wavelength', outcol='Wave', fiber='A',
                       units='nm', block_kind='red', clear_file=True)
post_s_file.add_column('S1D_W', out_ext_s1d_w,
                       incol='flux', outcol='FluxA', fiber='A',
                       block_kind='red', clear_file=True)
post_s_file.add_column('S1D_W', out_ext_s1d_w,
                       incol='eflux', outcol='FluxErrA', fiber='A',
                       block_kind='red', clear_file=True)
post_s_file.add_column('S1D_W', out_ext_s1d_w,
                       incol='flux', outcol='FluxB', fiber='B',
                       block_kind='red', clear_file=True)
post_s_file.add_column('S1D_W', out_ext_s1d_w,
                       incol='eflux', outcol='FluxErrB', fiber='B',
                       block_kind='red', clear_file=True)
post_s_file.add_column('S1D_W', out_tellu_sc1d_w,
                       incol='flux', outcol='FluxATelluCorrected', fiber='A',
                       required=False, block_kind='red', clear_file=True)
post_s_file.add_column('S1D_W', out_tellu_sc1d_w,
                       incol='eflux', outcol='FluxErrATelluCorrected',
                       fiber='A', required=False,
                       block_kind='red', clear_file=True)
# s1d w is a composite table
post_s_file.add_ext('S1D_V', 'table', pos=2, block_kind='red',
                    link='PP', hlink='KW_IDENTIFIER')
# add s1d w columns (all linked via PP file)
post_s_file.add_column('S1D_V', out_ext_s1d_v,
                       incol='wavelength', outcol='Wave', fiber='A',
                       units='nm', block_kind='red', clear_file=True)
post_s_file.add_column('S1D_V', out_ext_s1d_v,
                       incol='flux', outcol='FluxA', fiber='A',
                       block_kind='red', clear_file=True)
post_s_file.add_column('S1D_V', out_ext_s1d_v,
                       incol='eflux', outcol='FluxErrA', fiber='A',
                       block_kind='red', clear_file=True)
post_s_file.add_column('S1D_V', out_ext_s1d_v,
                       incol='flux', outcol='FluxB', fiber='B',
                       block_kind='red', clear_file=True)
post_s_file.add_column('S1D_V', out_ext_s1d_v,
                       incol='eflux', outcol='FluxErrB', fiber='B',
                       block_kind='red', clear_file=True)
post_s_file.add_column('S1D_V', out_tellu_sc1d_v,
                       incol='flux', outcol='FluxATelluCorrected', fiber='A',
                       required=False, block_kind='red', clear_file=True)
post_s_file.add_column('S1D_V', out_tellu_sc1d_v,
                       incol='eflux', outcol='FluxErrATelluCorrected',
                       fiber='A', required=False,
                       block_kind='red', clear_file=True)
# move header keys
post_s_file.add_hkey('KW_VERSION', inheader='VEL', outheader='PP')
post_s_file.add_hkey('KW_DRS_DATE_NOW', inheader='VEL', outheader='PP')
# add to post processed file set
post_file.addset(post_s_file)


# -----------------------------------------------------------------------------
# post processed telluric file
# -----------------------------------------------------------------------------
post_t_file = drs_oinput('DRS_POST_T', filetype='.fits', suffix='t.fits',
                         outfunc=out.post_file, inext='o', required=False)
# add extensions
post_t_file.add_ext('PP', pp_file, pos=0, header_only=True, block_kind='tmp',
                    hkeys=dict(KW_DPRTYPE=['OBJ_FP', 'OBJ_DARK', 'POLAR_FP',
                                           'POLAR_DARK']))
post_t_file.add_ext('TELLU_A', out_tellu_obj, pos=1, fiber='A',
                    link='PP', hlink='KW_IDENTIFIER', block_kind='red',
                    clear_file=True, tag='FluxA')
post_t_file.add_ext('WAVE_A', out_wavem_fp, pos=2, fiber='A',
                    link='TELLU_A', hlink='KW_CDBWAVE', block_kind='red',
                    clear_file=True, tag='WaveA')
post_t_file.add_ext('BLAZE_A', out_ff_blaze, pos=3, fiber='A',
                    link='TELLU_A', hlink='KW_CDBBLAZE', block_kind='red',
                    clear_file=True, tag='BlazeA')
post_t_file.add_ext('RECON_A', out_tellu_recon, pos=4, fiber='A',
                    link='TELLU_A', hlink='KW_IDENTIFIER', block_kind='red',
                    clear_file=True, tag='Recon')
# move header keys
post_t_file.add_hkey('KW_VERSION', inheader='VEL', outheader='PP')
post_t_file.add_hkey('KW_DRS_DATE_NOW', inheader='VEL', outheader='PP')
# add to post processed file set
post_file.addset(post_t_file)

# -----------------------------------------------------------------------------
# post processed velocity file
# -----------------------------------------------------------------------------
post_v_file = drs_oinput('DRS_POST_V', filetype='.fits', suffix='v.fits',
                         outfunc=out.post_file, inext='o', required=False)
post_v_file.add_ext('PP', pp_file, pos=0, header_only=True, block_kind='tmp',
                    hkeys=dict(KW_DPRTYPE=['OBJ_FP', 'OBJ_DARK']),
                    clear_file=True)
post_v_file.add_ext('VEL', out_ccf_fits, pos=1, fiber='A',
                    link='PP', hlink='KW_IDENTIFIER', block_kind='red',
                    clear_file=True, tag='CCF')
# move header keys
post_v_file.add_hkey('KW_VERSION', inheader='VEL', outheader='PP')
post_v_file.add_hkey('KW_DRS_DATE_NOW', inheader='VEL', outheader='PP')

# add to post processed file set
post_file.addset(post_v_file)

# =============================================================================
# Other Files
# =============================================================================
other_ccf_mask_file = drs_input('CCF_MASK', filetype='.mas')

# =============================================================================
# End of code
# =============================================================================
