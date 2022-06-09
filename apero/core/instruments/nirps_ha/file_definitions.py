#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NIRPS Files

# For fits files

file_name = drs_finput("name", KW_KEY1="value1", KW_KEY2="value2",
                       ext=".fits", filename=)


Created on 2018-10-31 at 18:06

@author: cook
"""
from apero.base import base
from apero.core.core import drs_file
from apero.core.core import drs_out_file as out


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
# Instrument name in header
INSTRUMENT_NAME = 'NIRPS'
INSTRUMENT_MODE = 'HA'

# =============================================================================
# Define Files
# =============================================================================
drs_input = drs_file.DrsInputFile
drs_finput = drs_file.DrsFitsFile
drs_ninput = drs_file.DrsNpyFile
drs_oinput = drs_file.DrsOutFile
DrsFileGroup = drs_file.DrsFileGroup
# define out file classes
blank_ofile = out.BlankOutFile()
general_ofile = out.GeneralOutFile()
debug_ofile = out.DebugOutFile()
set_ofile = out.SetOutFile()
post_ofile = out.PostOutFile()
calib_ofile = out.CalibOutFile()
mcalib_ofile = out.MasterCalibOutFile()
tellu_ofile = out.TelluOutFile()
mtellu_ofile = out.MasterTelluOutFile()
tellu_set_ofile = out.TelluSetOutFile()


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
                      outclass=blank_ofile, instrument=__INSTRUMENT__)
# -----------------------------------------------------------------------------
# raw dark files
# raw_dark_dark = drs_finput('RAW_DARK_DARK', KW_CCAS='pos_pk', KW_CREF='pos_pk',
#                            KW_OBSTYPE='DARK',
#                            filetype='.fits', suffix='', inext='d.fits',
#                            outclass=blank_ofile)
# raw_file.addset(raw_dark_dark)

# raw dark
raw_dark_dark = drs_finput('RAW_DARK_DARK', filetype='.fits',
                           suffix='', inext='.fits', outclass=blank_ofile,
                           hkeys=dict(KW_RAW_DPRTYPE='DARK',
                                      KW_RAW_DPRCATG='CALIB',
                                      KW_INST_MODE=INSTRUMENT_MODE,
                                      KW_INSTRUMENT=INSTRUMENT_NAME))
raw_file.addset(raw_dark_dark)

# sky observation (sky dark)
raw_dark_dark_sky = drs_finput('RAW_DARK_DARK_SKY', filetype='.fits',
                               suffix='', inext='.fits', outclass=blank_ofile,
                               hkeys=dict(KW_RAW_DPRTYPE='EFF,SKY,SKY',
                                          KW_RAW_DPRCATG='CALIB',
                                          KW_INST_MODE=INSTRUMENT_MODE,
                                          KW_INSTRUMENT=INSTRUMENT_NAME))
raw_file.addset(raw_dark_dark_sky)

# -----------------------------------------------------------------------------
# raw flat files
raw_dark_flat = drs_finput('RAW_DARK_FLAT', outclass=blank_ofile, filetype='.fits',
                           suffix='',
                           hkeys=dict(KW_RAW_DPRTYPE='ORDERDEF,DARK,LAMP',
                                      KW_RAW_DPRCATG='CALIB',
                                      KW_INST_MODE=INSTRUMENT_MODE,
                                      KW_INSTRUMENT=INSTRUMENT_NAME))
raw_file.addset(raw_dark_flat)

raw_flat_dark = drs_finput('RAW_FLAT_DARK', outclass=blank_ofile,
                           filetype='.fits', suffix='',
                           hkeys=dict(KW_RAW_DPRTYPE='ORDERDEF,LAMP,DARK',
                                      KW_RAW_DPRCATG='CALIB',
                                      KW_INST_MODE=INSTRUMENT_MODE,
                                      KW_INSTRUMENT=INSTRUMENT_NAME))
raw_file.addset(raw_flat_dark)

raw_flat_flat = drs_finput('RAW_FLAT_FLAT', outclass=blank_ofile,
                           filetype='.fits', suffix='',
                           hkeys=dict(KW_RAW_DPRTYPE='FLAT,LAMP,LAMP',
                                      KW_RAW_DPRCATG='CALIB',
                                      KW_INST_MODE=INSTRUMENT_MODE,
                                      KW_INSTRUMENT=INSTRUMENT_NAME))
raw_file.addset(raw_flat_flat)

# -----------------------------------------------------------------------------
# raw align files
raw_dark_fp = drs_finput('RAW_DARK_FP', outclass=blank_ofile,
                         filetype='.fits', suffix='',
                         hkeys=dict(KW_RAW_DPRTYPE='CONTAM,DARK,FP',
                                    KW_RAW_DPRCATG='CALIB',
                                    KW_INST_MODE=INSTRUMENT_MODE,
                                    KW_INSTRUMENT=INSTRUMENT_NAME))
raw_file.addset(raw_dark_fp)

raw_fp_dark = drs_finput('RAW_FP_DARK', outclass=blank_ofile,
                         filetype='.fits', suffix='',
                         hkeys=dict(KW_RAW_DPRTYPE='CONTAM,FP,DARK',
                                    KW_RAW_DPRCATG='CALIB',
                                    KW_INST_MODE=INSTRUMENT_MODE,
                                    KW_INSTRUMENT=INSTRUMENT_NAME))
raw_file.addset(raw_fp_dark)

raw_fp_fp = drs_finput('RAW_FP_FP', outclass=blank_ofile,
                       filetype='.fits', suffix='',
                       hkeys=dict(KW_RAW_DPRTYPE='WAVE,FP,FP',
                                  KW_RAW_DPRCATG='CALIB',
                                  KW_INST_MODE=INSTRUMENT_MODE,
                                  KW_INSTRUMENT=INSTRUMENT_NAME))
raw_file.addset(raw_fp_fp)

# -----------------------------------------------------------------------------
# raw LFC files
# NIRPS-CHANGE: Not defined - this is a guess
raw_lfc_lfc = drs_finput('RAW_LFC_LFC', filetype='.fits', suffix='',
                         outclass=blank_ofile,
                         hkeys=dict(KW_RAW_DPRTYPE='WAVE,LFC,LFC',
                                    KW_RAW_DPRCATG='CALIB',
                                    KW_INST_MODE=INSTRUMENT_MODE,
                                    KW_INSTRUMENT=INSTRUMENT_NAME))
raw_file.addset(raw_lfc_lfc)

# NIRPS-CHANGE: Not defined - this is a guess
raw_lfc_fp = drs_finput('RAW_LFC_FP', filetype='.fits', suffix='',
                        outclass=blank_ofile,
                        hkeys=dict(KW_RAW_DPRTYPE='WAVE,LFC,FP',
                                   KW_RAW_DPRCATG='CALIB',
                                   KW_INST_MODE=INSTRUMENT_MODE,
                                   KW_INSTRUMENT=INSTRUMENT_NAME))
raw_file.addset(raw_lfc_fp)

# NIRPS-CHANGE: Not defined - this is a guess
raw_fp_lfc = drs_finput('RAW_FP_LFC',
                        filetype='.fits', suffix='',
                        outclass=blank_ofile,
                        hkeys=dict(KW_RAW_DPRTYPE='WAVE,FP,LFC',
                                   KW_RAW_DPRCATG='CALIB',
                                   KW_INST_MODE=INSTRUMENT_MODE,
                                   KW_INSTRUMENT=INSTRUMENT_NAME))
raw_file.addset(raw_fp_lfc)

# -----------------------------------------------------------------------------
# raw LED LED file
raw_led_led = drs_finput('RAW_LED_LED', filetype='.fits', suffix='',
                         outclass=blank_ofile,
                         hkeys=dict(KW_RAW_DPRTYPE='LED,LAMP',
                                    KW_RAW_DPRCATG='CALIB',
                                    KW_INST_MODE=INSTRUMENT_MODE,
                                    KW_INSTRUMENT=INSTRUMENT_NAME))
raw_file.addset(raw_led_led)

# raw FLAT LED file
raw_flat_led = drs_finput('RAW_FLAT_LED', filetype='.fits', suffix='',
                          outclass=blank_ofile,
                          hkeys=dict(KW_RAW_DPRTYPE='FLAT,LED',
                                     KW_RAW_DPRCATG='CALIB',
                                     KW_INST_MODE=INSTRUMENT_MODE,
                                     KW_INSTRUMENT=INSTRUMENT_NAME))
raw_file.addset(raw_flat_led)

# -----------------------------------------------------------------------------
# raw object files
raw_obj_dark = drs_finput('RAW_OBJ_DARK', outclass=blank_ofile,
                          hkeys=dict(KW_RAW_DPRTYPE='OBJECT,DARK',
                                     KW_TARGET_TYPE='TARGET',
                                     KW_INST_MODE=INSTRUMENT_MODE,
                                     KW_INSTRUMENT=INSTRUMENT_NAME))
raw_file.addset(raw_obj_dark)

raw_obj_fp = drs_finput('RAW_OBJ_FP', outclass=blank_ofile, filetype='.fits',
                        suffix='', inext='.fits',
                        hkeys=dict(KW_RAW_DPRTYPE='OBJECT,FP',
                                   KW_TARGET_TYPE='TARGET',
                                   KW_INST_MODE=INSTRUMENT_MODE,
                                   KW_INSTRUMENT=INSTRUMENT_NAME))
raw_file.addset(raw_obj_fp)

raw_obj_hc1 = drs_finput('RAW_OBJ_HCONE', outclass=blank_ofile,
                         filetype='.fits', suffix='', inext='.fits',
                         hkeys=dict(KW_RAW_DPRTYPE='OBJECT,UN1',
                                    KW_TARGET_TYPE='TARGET',
                                    KW_INST_MODE=INSTRUMENT_MODE,
                                    KW_INSTRUMENT=INSTRUMENT_NAME))
raw_file.addset(raw_obj_hc1)

raw_obj_sky = drs_finput('RAW_OBJ_SKY', outclass=blank_ofile,
                         filetype='.fits', suffix='', inext='.fits',
                         hkeys=dict(KW_RAW_DPRTYPE='OBJECT,SKY',
                                    KW_TARGET_TYPE='TARGET',
                                    KW_INST_MODE=INSTRUMENT_MODE,
                                    KW_INSTRUMENT=INSTRUMENT_NAME))
raw_file.addset(raw_obj_sky)

raw_obj_tun = drs_finput('RAW_OBJ_TUN', outclass=blank_ofile,
                         filetype='.fits', suffix='', inext='.fits',
                         hkeys=dict(KW_RAW_DPRTYPE='OBJECT,TUN',
                                    KW_TARGET_TYPE='TARGET',
                                    KW_INST_MODE=INSTRUMENT_MODE,
                                    KW_INSTRUMENT=INSTRUMENT_NAME))
raw_file.addset(raw_obj_tun)

raw_sun_fp = drs_finput('RAW_SUN_FP', outclass=blank_ofile,
                        filetype='.fits', suffix='', inext='.fits',
                        hkeys=dict(KW_RAW_DPRTYPE='SUN,FP,G2V',
                                   KW_INST_MODE=INSTRUMENT_MODE,
                                   KW_INSTRUMENT=INSTRUMENT_NAME))
raw_file.addset(raw_sun_fp)

raw_sun_dark = drs_finput('RAW_SUN_DARK', outclass=blank_ofile,
                        filetype='.fits', suffix='', inext='.fits',
                        hkeys=dict(KW_RAW_DPRTYPE='SUN,DARK,G2V',
                                   KW_INST_MODE=INSTRUMENT_MODE,
                                   KW_INSTRUMENT=INSTRUMENT_NAME))
raw_file.addset(raw_sun_dark)

raw_fluxstd_sky = drs_finput('RAW_FLUXSTD_SKY', outclass=blank_ofile,
                          filetype='.fits', suffix='', inext='.fits',
                          hkeys=dict(KW_RAW_DPRTYPE='FLUX,STD,SKY',
                                     KW_INST_MODE=INSTRUMENT_MODE,
                                     KW_INSTRUMENT=INSTRUMENT_NAME))
raw_file.addset(raw_fluxstd_sky)

raw_tellu_sky = drs_finput('RAW_TELLU_SKY', outclass=blank_ofile,
                          filetype='.fits', suffix='', inext='.fits',
                          hkeys=dict(KW_RAW_DPRTYPE='TELLURIC,SKY',
                                     KW_INST_MODE=INSTRUMENT_MODE,
                                     KW_INSTRUMENT=INSTRUMENT_NAME))
raw_file.addset(raw_tellu_sky)

# -----------------------------------------------------------------------------
# raw comparison files
raw_dark_hc1 = drs_finput('RAW_DARK_HCONE', outclass=blank_ofile,
                          filetype='.fits', suffix='',
                          hkeys=dict(KW_RAW_DPRTYPE='WAVE,DARK,UN1',
                                     KW_RAW_DPRCATG='CALIB',
                                     KW_INST_MODE=INSTRUMENT_MODE,
                                     KW_INSTRUMENT=INSTRUMENT_NAME))
raw_file.addset(raw_dark_hc1)

raw_fp_hc1 = drs_finput('RAW_FP_HCONE', outclass=blank_ofile,
                        filetype='.fits', suffix='',
                        hkeys=dict(KW_RAW_DPRTYPE='WAVE,FP,UN1',
                                   KW_RAW_DPRCATG='CALIB',
                                   KW_INST_MODE=INSTRUMENT_MODE,
                                   KW_INSTRUMENT=INSTRUMENT_NAME))
raw_file.addset(raw_fp_hc1)

raw_hc1_fp = drs_finput('RAW_HCONE_FP', outclass=blank_ofile,
                        filetype='.fits', suffix='',
                        hkeys=dict(KW_RAW_DPRTYPE='WAVE,UN1,FP',
                                   KW_RAW_DPRCATG='CALIB',
                                   KW_INST_MODE=INSTRUMENT_MODE,
                                   KW_INSTRUMENT=INSTRUMENT_NAME))
raw_file.addset(raw_hc1_fp)

raw_hc1_hc1 = drs_finput('RAW_HCONE_HCONE', filetype='.fits', suffix='',
                         outclass=blank_ofile,
                         hkeys=dict(KW_RAW_DPRTYPE='WAVE,UN1,UN1',
                                    KW_RAW_DPRCATG='CALIB',
                                    KW_INST_MODE=INSTRUMENT_MODE,
                                    KW_INSTRUMENT=INSTRUMENT_NAME))
raw_file.addset(raw_hc1_hc1)

raw_hc1_dark = drs_finput('RAW_HCONE_DARK', filetype='.fits', suffix='',
                          outclass=blank_ofile,
                          hkeys=dict(KW_RAW_DPRTYPE='WAVE,UN1,DARK',
                                     KW_RAW_DPRCATG='CALIB',
                                     KW_INST_MODE=INSTRUMENT_MODE,
                                     KW_INSTRUMENT=INSTRUMENT_NAME))
raw_file.addset(raw_hc1_dark)

# -----------------------------------------------------------------------------
# test raw files
# -----------------------------------------------------------------------------
# raw test dark flat file
# TODO: Should this exist?
raw_calib_dark_flat = drs_finput('RAW_CALIB_DARK_FLAT', outclass=blank_ofile,
                                 filetype='.fits', suffix='',
                                 hkeys=dict(KW_RAW_DPRTYPE='FLAT,DARK,LAMP',
                                            KW_RAW_DPRCATG='CALIB',
                                            KW_INST_MODE=INSTRUMENT_MODE,
                                            KW_INSTRUMENT=INSTRUMENT_NAME))
raw_file.addset(raw_calib_dark_flat)

# raw test flat dark file
# TODO: Should this exist?
raw_calib_flat_dark = drs_finput('RAW_CALIB_FLAT_DARK', outclass=blank_ofile,
                                 filetype='.fits', suffix='',
                                 hkeys=dict(KW_RAW_DPRTYPE='FLAT,LAMP,DARK',
                                            KW_RAW_DPRCATG='CALIB',
                                            KW_INST_MODE=INSTRUMENT_MODE,
                                            KW_INSTRUMENT=INSTRUMENT_NAME))
raw_file.addset(raw_calib_flat_dark)

# raw test dark fp
raw_test_dark_fp = drs_finput('RAW_TEST_DARK_FP', outclass=blank_ofile,
                              filetype='.fits', suffix='',
                              hkeys=dict(KW_RAW_DPRTYPE='CONTAM,DARK,FP',
                                         KW_RAW_DPRCATG='TEST',
                                         KW_INST_MODE=INSTRUMENT_MODE,
                                         KW_INSTRUMENT=INSTRUMENT_NAME))
raw_file.addset(raw_test_dark_fp)

# raw test dark flat file
raw_test_dark_flat = drs_finput('RAW_TEST_DARK_FLAT', outclass=blank_ofile,
                                filetype='.fits', suffix='',
                                hkeys=dict(KW_RAW_DPRTYPE='FLAT,DARK,LAMP',
                                           KW_RAW_DPRCATG='TEST',
                                           KW_INST_MODE=INSTRUMENT_MODE,
                                           KW_INSTRUMENT=INSTRUMENT_NAME))
raw_file.addset(raw_test_dark_flat)

# raw test flat dark file
raw_test_flat_dark = drs_finput('RAW_TEST_FLAT_DARK', outclass=blank_ofile,
                                filetype='.fits', suffix='',
                                hkeys=dict(KW_RAW_DPRTYPE='FLAT,LAMP,DARK',
                                           KW_RAW_DPRCATG='TEST',
                                           KW_INST_MODE=INSTRUMENT_MODE,
                                           KW_INSTRUMENT=INSTRUMENT_NAME))
raw_file.addset(raw_test_flat_dark)

# raw test wave fp fp file
raw_test_fp_fp = drs_finput('RAW_TEST_FP_FP', outclass=blank_ofile,
                            filetype='.fits', suffix='',
                            hkeys=dict(KW_RAW_DPRTYPE='WAVE,FP,FP',
                                       KW_RAW_DPRCATG='TEST',
                                       KW_INST_MODE=INSTRUMENT_MODE,
                                       KW_INSTRUMENT=INSTRUMENT_NAME))
raw_file.addset(raw_test_fp_fp)

# raw test led
raw_test_led_led = drs_finput('RAW_TEST_LED_LED', filetype='.fits', suffix='',
                              hkeys=dict(KW_RAW_DPRTYPE='LED,LAMP',
                                         KW_RAW_DPRCATG='TEST',
                                         KW_INST_MODE=INSTRUMENT_MODE,
                                         KW_INSTRUMENT=INSTRUMENT_NAME))
raw_file.addset(raw_test_led_led)

raw_test_hc1_hc1 = drs_finput('RAW_TEST_HCONE_HCONE', filetype='.fits',
                              suffix='', outclass=blank_ofile,
                              hkeys=dict(KW_RAW_DPRTYPE='WAVE,UN1,UN1',
                                         KW_RAW_DPRCATG='TEST',
                                         KW_INST_MODE=INSTRUMENT_MODE,
                                         KW_INSTRUMENT=INSTRUMENT_NAME))
raw_file.addset(raw_test_hc1_hc1)

raw_test_fp_hc1 = drs_finput('RAW_TEST_FP_HCONE', outclass=blank_ofile,
                             filetype='.fits', suffix='',
                             hkeys=dict(KW_RAW_DPRTYPE='WAVE,FP,UN1',
                                        KW_RAW_DPRCATG='TEST',
                                        KW_INST_MODE=INSTRUMENT_MODE,
                                        KW_INSTRUMENT=INSTRUMENT_NAME))
raw_file.addset(raw_test_fp_hc1)

raw_test_hc1_fp = drs_finput('RAW_TEST_HCONE_FP', outclass=blank_ofile,
                             filetype='.fits', suffix='',
                             hkeys=dict(KW_RAW_DPRTYPE='WAVE,UN1,FP',
                                        KW_RAW_DPRCATG='TEST',
                                        KW_INST_MODE=INSTRUMENT_MODE,
                                        KW_INSTRUMENT=INSTRUMENT_NAME))
raw_file.addset(raw_test_hc1_fp)

# =============================================================================
# Preprocessed Files
# =============================================================================
# generic pp file
pp_file = drs_finput('DRS_PP', filetype='.fits', suffix='_pp',
                     outclass=general_ofile, intype=raw_file,
                     instrument=__INSTRUMENT__)
# -----------------------------------------------------------------------------
# dark
# pp_dark_dark = drs_finput('DARK_DARK', KW_DPRTYPE='DARK_DARK',
#                           filetype='.fits',
#                           suffix='_pp', intype=raw_dark_dark,
#                           inext='.fits', outclass=general_ofile)
# pp_file.addset(pp_dark_dark)

pp_dark_dark = drs_finput('DARK_DARK', filetype='.fits',
                          suffix='_pp', intype=raw_dark_dark,
                          inext='.fits', outclass=general_ofile,
                          hkeys=dict(KW_DPRTYPE='DARK_DARK'))
pp_file.addset(pp_dark_dark)

pp_dark_dark_sky = drs_finput('DARK_DARK_SKY', filetype='.fits',
                              suffix='_pp', intype=raw_dark_dark_sky,
                              inext='.fits', outclass=general_ofile,
                              hkeys=dict(KW_DPRTYPE='DARK_DARK_SKY'))
pp_file.addset(pp_dark_dark_sky)

# -----------------------------------------------------------------------------
# flat
pp_flat_dark = drs_finput('FLAT_DARK', filetype='.fits',
                          suffix='_pp', intype=raw_flat_dark,
                          inext='.fits', outclass=general_ofile,
                          hkeys=dict(KW_DPRTYPE='FLAT_DARK'))
pp_file.addset(pp_flat_dark)

pp_dark_flat = drs_finput('DARK_FLAT', filetype='.fits',
                          suffix='_pp', intype=raw_dark_flat,
                          inext='.fits', outclass=general_ofile,
                          hkeys=dict(KW_DPRTYPE='DARK_FLAT'))
pp_file.addset(pp_dark_flat)

pp_flat_flat = drs_finput('FLAT_FLAT', filetype='.fits',
                          suffix='_pp', intype=raw_flat_flat,
                          inext='.fits', outclass=general_ofile,
                          hkeys=dict(KW_DPRTYPE='FLAT_FLAT'))
pp_file.addset(pp_flat_flat)

# -----------------------------------------------------------------------------
# align
pp_dark_fp = drs_finput('DARK_FP', filetype='.fits',
                        suffix='_pp', intype=raw_dark_fp,
                        inext='.fits', outclass=general_ofile,
                        hkeys=dict(KW_DPRTYPE='DARK_FP'))
pp_file.addset(pp_dark_fp)
pp_fp_dark = drs_finput('FP_DARK', filetype='.fits',
                        suffix='_pp', intype=raw_fp_dark,
                        inext='.fits', outclass=general_ofile,
                        hkeys=dict(KW_DPRTYPE='FP_DARK'))
pp_file.addset(pp_fp_dark)

pp_fp_fp = drs_finput('FP_FP', filetype='.fits',
                      suffix='_pp', intype=raw_fp_fp,
                      inext='.fits', outclass=general_ofile,
                      hkeys=dict(KW_DPRTYPE='FP_FP'))
pp_file.addset(pp_fp_fp)

# -----------------------------------------------------------------------------
# LFC
pp_lfc_lfc = drs_finput('LFC_LFC', filetype='.fits', suffix='_pp',
                        intype=raw_lfc_lfc, inext='.fits',
                        outclass=general_ofile,
                        hkeys=dict(KW_DPRTYPE='LFC_LFC'))
pp_file.addset(pp_lfc_lfc)

pp_lfc_fp = drs_finput('LFC_FP', hkeys=dict(KW_DPRTYPE='LFC_FP'),
                       filetype='.fits', suffix='_pp', intype=raw_lfc_fp,
                       inext='.fits', outclass=general_ofile)
pp_file.addset(pp_lfc_fp)

pp_fp_lfc = drs_finput('FP_LFC', hkeys=dict(KW_DPRTYPE='FP_LFC'),
                       filetype='.fits', suffix='_pp', intype=raw_fp_lfc,
                       inext='.fits', outclass=general_ofile)
pp_file.addset(pp_fp_lfc)

# -----------------------------------------------------------------------------
# LED LED file
pp_led_led = drs_finput('LED_LED', hkeys=dict(KW_DPRTYPE='LED_LED'),
                        filetype='.fits', suffix='_pp', intype=raw_led_led,
                        inext='.fits', outclass=general_ofile)
pp_file.addset(pp_led_led)

# FLAT LED
pp_flat_led = drs_finput('FLAT_LED', hkeys=dict(KW_DPRTYPE='FLAT_LED'),
                         filetype='.fits', suffix='_pp', intype=raw_flat_led,
                         inext='.fits', outclass=general_ofile)
pp_file.addset(pp_flat_led)

# -----------------------------------------------------------------------------
#  object
pp_obj_dark = drs_finput('OBJ_DARK', hkeys=dict(KW_DPRTYPE='OBJ_DARK'),
                         filetype='.fits',
                         suffix='_pp', intype=raw_obj_dark,
                         inext='.fits', outclass=general_ofile)
pp_file.addset(pp_obj_dark)
pp_obj_fp = drs_finput('OBJ_FP', hkeys=dict(KW_DPRTYPE='OBJ_FP'),
                       filetype='.fits',
                       suffix='_pp', intype=raw_obj_fp,
                       inext='.fits', outclass=general_ofile)
pp_file.addset(pp_obj_fp)
pp_obj_hc1 = drs_finput('OBJ_HC1', hkeys=dict(KW_DPRTYPE='OBJ_HCONE'),
                        filetype='.fits',
                        suffix='_pp', intype=raw_obj_hc1,
                        inext='.fits', outclass=general_ofile)
pp_file.addset(pp_obj_hc1)

pp_obj_sky = drs_finput('OBJ_SKY', hkeys=dict(KW_DPRTYPE='OBJ_SKY'),
                        filetype='.fits',
                        suffix='_pp', intype=raw_obj_sky,
                        inext='.fits', outclass=general_ofile)
pp_file.addset(pp_obj_sky)

pp_obj_tun = drs_finput('OBJ_TUN', hkeys=dict(KW_DPRTYPE='OBJ_TUN'),
                        filetype='.fits',
                        suffix='_pp', intype=raw_obj_tun,
                        inext='.fits', outclass=general_ofile)
pp_file.addset(pp_obj_tun)

pp_sun_fp = drs_finput('SUN_FP', hkeys=dict(KW_DPRTYPE='SUN_FP'),
                       filetype='.fits',
                       suffix='_pp', intype=raw_sun_fp,
                       inext='.fits', outclass=general_ofile)
pp_file.addset(pp_sun_fp)

pp_sun_dark = drs_finput('SUN_DARK', hkeys=dict(KW_DPRTYPE='SUN_DARK'),
                         filetype='.fits',
                         suffix='_pp', intype=raw_sun_dark,
                         inext='.fits', outclass=general_ofile)
pp_file.addset(pp_sun_dark)

pp_fluxstd_sky = drs_finput('FLUXSTD_SKY', hkeys=dict(KW_DPRTYPE='FLUXSTD_SKY'),
                            filetype='.fits',
                            suffix='_pp', intype=raw_fluxstd_sky,
                            inext='.fits', outclass=general_ofile)
pp_file.addset(pp_fluxstd_sky)

pp_tellu_sky = drs_finput('TELLU_SKY', hkeys=dict(KW_DPRTYPE='TELLU_SKY'),
                          filetype='.fits',
                          suffix='_pp', intype=raw_tellu_sky,
                          inext='.fits', outclass=general_ofile)
pp_file.addset(pp_tellu_sky)

# define all science observations
science_pp = [pp_obj_dark, pp_obj_fp, pp_obj_sky, pp_obj_tun, pp_fluxstd_sky,
              pp_tellu_sky]
science_dprtypes = ['OBJ_DARK', 'OBJ_FP', 'OBJ_SKY', 'OBJ_TUN', 'FLUXSTD_SKY',
                    'TELLU_SKY']

# -----------------------------------------------------------------------------
#  comparison
pp_dark_hc1 = drs_finput('DARK_HCONE', hkeys=dict(KW_DPRTYPE='DARK_HCONE'),
                         filetype='.fits',
                         suffix='_pp', intype=raw_dark_hc1,
                         inext='.fits', outclass=general_ofile)
pp_file.addset(pp_dark_hc1)

pp_fp_hc1 = drs_finput('FP_HCONE', hkeys=dict(KW_DPRTYPE='FP_HCONE'),
                       filetype='.fits',
                       suffix='_pp', intype=raw_fp_hc1,
                       inext='.fits', outclass=general_ofile)
pp_file.addset(pp_fp_hc1)

pp_hc1_fp = drs_finput('HCONE_FP', hkeys=dict(KW_DPRTYPE='HCONE_FP'),
                       filetype='.fits',
                       suffix='_pp', intype=raw_hc1_fp,
                       inext='.fits', outclass=general_ofile)
pp_file.addset(pp_hc1_fp)

pp_hc1_hc1 = drs_finput('HCONE_HCONE', hkeys=dict(KW_DPRTYPE='HCONE_HCONE'),
                        filetype='.fits',
                        suffix='_pp', intype=raw_hc1_hc1,
                        inext='.fits', outclass=general_ofile)
pp_file.addset(pp_hc1_hc1)

pp_hc1_dark = drs_finput('HCONE_DARK', hkeys=dict(KW_DPRTYPE='HCONE_DARK'),
                         filetype='.fits',
                         suffix='_pp', intype=raw_hc1_dark,
                         inext='.fits', outclass=general_ofile)
pp_file.addset(pp_hc1_dark)

# -----------------------------------------------------------------------------
# test pp files
# -----------------------------------------------------------------------------
# raw test dark flat file
# TODO: Should this exist?
calib_dark_flat = drs_finput('CALIB_DARK_FLAT', filetype='.fits',
                             hkeys=dict(KW_DPRTYPE='CALIB_DARK_FLAT'),
                             suffix='_pp', intype=raw_calib_dark_flat,
                             inext='.fits', outclass=general_ofile)
pp_file.addset(calib_dark_flat)

# raw test flat dark file
# TODO: Should this exist?
calib_flat_dark = drs_finput('CALIB_FLAT_DARK', filetype='.fits',
                             hkeys=dict(KW_DPRTYPE='CALIB_FLAT_DARK'),
                             suffix='_pp', intype=raw_calib_flat_dark,
                             inext='.fits', outclass=general_ofile)
pp_file.addset(calib_flat_dark)

# raw test dark flat file
pp_test_dark_flat = drs_finput('TEST_DARK_FLAT', filetype='.fits',
                               hkeys=dict(KW_DPRTYPE='TEST_DARK_FLAT'),
                               suffix='_pp', intype=raw_test_dark_flat,
                               inext='.fits', outclass=general_ofile)

pp_file.addset(pp_test_dark_flat)

# raw test flat dark file
pp_test_flat_dark = drs_finput('TEST_FLAT_DARK', filetype='.fits',
                               hkeys=dict(KW_DPRTYPE='TEST_FLAT_DARK'),
                               suffix='_pp', intype=raw_test_flat_dark,
                               inext='.fits', outclass=general_ofile)
pp_file.addset(pp_test_flat_dark)

# raw test dark fp
pp_test_dark_fp = drs_finput('TEST_DARK_FP', filetype='.fits',
                             suffix='_pp', intype=raw_test_dark_fp,
                             inext='.fits', outclass=general_ofile,
                             hkeys=dict(KW_DPRTYPE='TEST_DARK_FP'))
pp_file.addset(pp_test_dark_fp)

# raw test wave fp fp file
pp_test_fp_fp = drs_finput('TEST_FP_FP', filetype='.fits',
                           hkeys=dict(KW_DPRTYPE='TEST_FP_FP'),
                           suffix='_pp', intype=raw_test_fp_fp,
                           inext='.fits', outclass=general_ofile)
pp_file.addset(pp_test_fp_fp)

# raw test led
pp_test_led_led = drs_finput('TEST_LED_LED', filetype='.fits',
                             hkeys=dict(KW_DPRTYPE='TEST_LED_LED'),
                             suffix='_pp', intype=raw_test_led_led,
                             inext='.fits', outclass=general_ofile)
pp_file.addset(pp_test_led_led)

# raw test hc1 hc1
pp_test_hc1_hc1 = drs_finput('TEST_HCONE_HCONE', filetype='.fits',
                             hkeys=dict(KW_DPRTYPE='TEST_HCONE_HCONE'),
                             suffix='_pp', intype=raw_test_hc1_hc1,
                             inext='.fits', outclass=general_ofile)
pp_file.addset(pp_test_hc1_hc1)

# test fp hc
pp_test_fp_hc1 = drs_finput('TEST_FP_HCONE',
                            hkeys=dict(KW_DPRTYPE='TEST_FP_HCONE'),
                            filetype='.fits',
                            suffix='_pp', intype=raw_test_fp_hc1,
                            inext='.fits', outclass=general_ofile)
pp_file.addset(pp_test_fp_hc1)

# test hc fp
pp_test_hc1_fp = drs_finput('TEST_HCONE_FP',
                            hkeys=dict(KW_DPRTYPE='TEST_HCONE_FP'),
                            filetype='.fits',
                            suffix='_pp', intype=raw_test_hc1_fp,
                            inext='.fits', outclass=general_ofile)
pp_file.addset(pp_test_hc1_fp)

# =============================================================================
# Reduced Files
# =============================================================================
# generic out file
red_file = drs_finput('DRS_OUTPUT', filetype='.fits', suffix='',
                      intype=pp_file, instrument=__INSTRUMENT__)
# calib out file
calib_file = drs_finput('DRS_OUTPUT', filetype='.fits', suffix='',
                        intype=pp_file, instrument=__INSTRUMENT__)
# telluric out file
tellu_file = drs_finput('DRS_OUTPUT', filetype='.fits', suffix='',
                        intype=pp_file, instrument=__INSTRUMENT__)

# -----------------------------------------------------------------------------
# pp master files
# -----------------------------------------------------------------------------
out_pp_master = drs_finput('PPMSTR', hkeys=dict(KW_OUTPUT='PPMSTR'),
                           filetype='.fits',
                           intype=[raw_flat_flat],
                           suffix='_pmaster',
                           outclass=mcalib_ofile,
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
#                       outclass=calib_ofile,
#                       dbname='calibration', dbkey='DARK')

out_dark = drs_finput('DARKI', hkeys=dict(KW_OUTPUT='DARKI'),
                      filetype='.fits', intype=pp_dark_dark,
                      suffix='_darki',
                      outclass=calib_ofile,
                      dbname='calibration', dbkey='DARKI')

out_dark_sky = drs_finput('DARKS', hkeys=dict(KW_OUTPUT='DARKS'),
                          filetype='.fits', intype=pp_dark_dark_sky,
                          suffix='_darks',
                          outclass=calib_ofile,
                          dbname='calibration', dbkey='DARKS')

out_dark_master = drs_finput('DARKM', hkeys=dict(KW_OUTPUT='DARKM'),
                             filetype='.fits',
                             intype=[pp_dark_dark],
                             suffix='_dark_master',
                             outclass=mcalib_ofile,
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
                        outclass=calib_ofile,
                        dbname='calibration', dbkey='BADPIX')
out_backmap = drs_finput('BKGRD_MAP', hkeys=dict(KW_OUTPUT='BKGRD_MAP'),
                         intype=[pp_flat_flat],
                         suffix='_bmap.fits', outclass=calib_ofile,
                         dbname='calibration', dbkey='BKGRDMAP')

# background debug file
debug_back = drs_finput('DEBUG_BACK', hkeys=dict(KW_OUTPUT='DEBUG_BACK'),
                        filetype='.fits', intype=pp_file,
                        suffix='_background.fits', outclass=debug_ofile)

# add badpix outputs to output fileset
red_file.addset(out_badpix)
red_file.addset(out_backmap)
red_file.addset(debug_back)
calib_file.addset(out_badpix)
calib_file.addset(out_backmap)

# -----------------------------------------------------------------------------
# localisation files
# -----------------------------------------------------------------------------
# define fiber valid for localisation
valid_lfibers = ['A', 'B']
# localisation
out_loc_orderp = drs_finput('LOC_ORDERP', hkeys=dict(KW_OUTPUT='LOC_ORDERP'),
                            fibers=valid_lfibers,
                            filetype='.fits',
                            intype=[pp_flat_dark, pp_dark_flat],
                            suffix='_order_profile',
                            outclass=calib_ofile,
                            dbname='calibration', dbkey='ORDER_PROFILE')
out_loc_loco = drs_finput('LOC_LOCO', hkeys=dict(KW_OUTPUT='LOC_LOCO'),
                          fibers=valid_lfibers,
                          filetype='.fits', intype=[pp_flat_dark, pp_dark_flat],
                          suffix='_loco',
                          outclass=calib_ofile,
                          dbname='calibration', dbkey='LOC')
out_loc_fwhm = drs_finput('LOC_FWHM', hkeys=dict(KW_OUTPUT='LOC_FWHM'),
                          fibers=valid_lfibers,
                          filetype='.fits', intype=[pp_flat_dark, pp_dark_flat],
                          suffix='_fwhm-order',
                          outclass=calib_ofile)
out_loc_sup = drs_finput('LOC_SUP', hkeys=dict(KW_OUTPUT='LOC_SUP'),
                         fibers=valid_lfibers,
                         filetype='.fits', intype=[pp_flat_dark, pp_dark_flat],
                         suffix='_with-order',
                         outclass=calib_ofile)
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
                             outclass=mcalib_ofile,
                             dbname='calibration', dbkey='SHAPEX')
out_shape_dymap = drs_finput('SHAPE_Y', hkeys=dict(KW_OUTPUT='SHAPE_Y'),
                             filetype='.fits', intype=pp_fp_fp,
                             suffix='_shapey',
                             outclass=mcalib_ofile,
                             dbname='calibration', dbkey='SHAPEY')
out_shape_fpmaster = drs_finput('MASTER_FP', hkeys=dict(KW_OUTPUT='MASTER_FP'),
                                filetype='.fits', intype=pp_fp_fp,
                                suffix='_fpmaster',
                                outclass=mcalib_ofile,
                                dbname='calibration', dbkey='FPMASTER')
out_shape_debug_ifp = drs_finput('SHAPE_IN_FP',
                                 hkeys=dict(KW_OUTPUT='SHAPE_IN_FP'),
                                 filetype='.fits', intype=pp_fp_fp,
                                 suffix='_shape_in_fp',
                                 outclass=debug_ofile)
out_shape_debug_ofp = drs_finput('SHAPE_OUT_FP',
                                 hkeys=dict(KW_OUTPUT='SHAPE_OUT_FP'),
                                 filetype='.fits', intype=pp_fp_fp,
                                 suffix='_shape_out_fp',
                                 outclass=debug_ofile)
out_shape_debug_bdx = drs_finput('SHAPE_BDX', hkeys=dict(KW_OUTPUT='SHAPE_BDX'),
                                 filetype='.fits', intype=pp_fp_fp,
                                 suffix='_shape_out_bdx',
                                 outclass=debug_ofile)
# add shape master outputs to output fileset
red_file.addset(out_shape_dxmap)
red_file.addset(out_shape_dymap)
red_file.addset(out_shape_fpmaster)
red_file.addset(out_shape_debug_ifp)
red_file.addset(out_shape_debug_ofp)
red_file.addset(out_shape_debug_bdx)

calib_file.addset(out_shape_dxmap)
calib_file.addset(out_shape_dymap)
calib_file.addset(out_shape_fpmaster)

# valid ext fibers
valid_efibers = ['A', 'B']
# -----------------------------------------------------------------------------
# shape files (per night)
# -----------------------------------------------------------------------------
# shape local
out_shape_local = drs_finput('SHAPEL', hkeys=dict(KW_OUTPUT='SHAPEL'),
                             filetype='.fits', intype=pp_fp_fp,
                             suffix='_shapel',
                             outclass=calib_ofile,
                             dbname='calibration', dbkey='SHAPEL')
out_shapel_debug_ifp = drs_finput('SHAPEL_IN_FP',
                                  hkeys=dict(KW_OUTPUT='SHAPEL_IN_FP'),
                                  filetype='.fits', intype=pp_fp_fp,
                                  suffix='_shapel_in_fp.fits',
                                  outclass=debug_ofile)

out_shapel_debug_ofp = drs_finput('SHAPEL_OUT_FP',
                                  hkeys=dict(KW_OUTPUT='SHAPEL_OUT_FP'),
                                  filetype='.fits', intype=pp_fp_fp,
                                  suffix='_shapel_out_fp.fits',
                                  outclass=debug_ofile)
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
                          fibers=valid_efibers,
                          filetype='.fits', intype=pp_flat_flat,
                          suffix='_blaze',
                          dbname='calibration', dbkey='BLAZE',
                          outclass=calib_ofile)
out_ff_flat = drs_finput('FF_FLAT', hkeys=dict(KW_OUTPUT='FF_FLAT'),
                         fibers=valid_efibers,
                         filetype='.fits', intype=pp_flat_flat,
                         suffix='_flat',
                         dbname='calibration', dbkey='FLAT',
                         outclass=calib_ofile)

out_orderp_straight = drs_finput('ORDERP_STRAIGHT',
                                 hkeys=dict(KW_OUTPUT='ORDERP_STRAIGHT'),
                                 fibers=valid_efibers,
                                 filetype='.fits', intype=out_shape_local,
                                 suffix='_orderps',
                                 outclass=general_ofile)

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
                         fibers=valid_efibers,
                         filetype='.fits', intype=pp_file,
                         suffix='_q2ds', outclass=general_ofile)

# extract E2DS with flat fielding
out_ql_e2dsff = drs_finput('QL_E2DS_FF', hkeys=dict(KW_OUTPUT='QL_E2DS_FF'),
                           fibers=valid_efibers,
                           filetype='.fits', intype=pp_file,
                           suffix='_q2dsff', outclass=general_ofile)

# -----------------------------------------------------------------------------
# extract files
# -----------------------------------------------------------------------------
# extract E2DS without flat fielding
out_ext_e2ds = drs_finput('EXT_E2DS', hkeys=dict(KW_OUTPUT='EXT_E2DS'),
                          fibers=valid_efibers,
                          filetype='.fits', intype=pp_file,
                          suffix='_e2ds', outclass=general_ofile)
# extract E2DS with flat fielding
out_ext_e2dsff = drs_finput('EXT_E2DS_FF', hkeys=dict(KW_OUTPUT='EXT_E2DS_FF'),
                            fibers=valid_efibers,
                            filetype='.fits', intype=pp_file,
                            suffix='_e2dsff', outclass=general_ofile,
                            s1d=['EXT_S1D_W', 'EXT_S1D_V'])
# pre-extract debug file
out_ext_e2dsll = drs_finput('EXT_E2DS_LL', hkeys=dict(KW_OUTPUT='EXT_E2DS_LL'),
                            fibers=valid_efibers,
                            filetype='.fits', intype=[pp_file, pp_flat_flat],
                            suffix='_e2dsll', outclass=debug_ofile)
# extraction localisation file
out_ext_loco = drs_finput('EXT_LOCO', hkeys=dict(KW_OUTPUT='EXT_LOCO'),
                          fibers=valid_efibers,
                          filetype='.fits', intype=pp_file,
                          suffix='_e2dsloco', outclass=debug_ofile)
# extract s1d without flat fielding (constant in wavelength)
out_ext_s1d_w = drs_finput('EXT_S1D_W', hkeys=dict(KW_OUTPUT='EXT_S1D_W'),
                           fibers=valid_efibers,
                           filetype='.fits', intype=pp_file, datatype='table',
                           suffix='_s1d_w', outclass=general_ofile)
# extract s1d without flat fielding (constant in velocity)
out_ext_s1d_v = drs_finput('EXT_S1D_V', hkeys=dict(KW_OUTPUT='EXT_S1D_V'),
                           fibers=valid_efibers,
                           filetype='.fits', intype=pp_file, datatype='table',
                           suffix='_s1d_v', outclass=general_ofile)

# fp line file from night
out_ext_fplines = drs_finput('EXT_FPLIST', hkeys=dict(KW_OUTPUT='EXT_FPLIST'),
                             fibers=valid_efibers,
                             filetype='.fits', remove_insuffix=True,
                             intype=[out_ext_e2ds, out_ext_e2dsff],
                             suffix='_ext_fplines',
                             outclass=general_ofile)

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
                             fibers=valid_efibers,
                             filetype='.fits',
                             intype=[out_ext_e2ds, out_ext_e2dsff],
                             suffix='_leak_master',
                             dbname='calibration', dbkey='LEAKM',
                             outclass=mcalib_ofile)
red_file.addset(out_leak_master)
calib_file.addset(out_leak_master)

# -----------------------------------------------------------------------------
# wave files (master) ea
# -----------------------------------------------------------------------------
# wave solution using hc + fp
out_wavem_sol = drs_finput('WAVESOL_MASTER',
                           hkeys=dict(KW_OUTPUT='WAVESOL_MASTER'),
                           fibers=valid_efibers,
                           filetype='.fits',
                           intype=[out_ext_e2ds, out_ext_e2dsff],
                           suffix='_wavesol_master',
                           dbname='calibration', dbkey='WAVESOL_MASTER',
                           outclass=mcalib_ofile)

# hc line file from master
out_wave_hclist_master = drs_finput('WAVE_HCLIST_MASTER',
                                    hkeys=dict(KW_OUTPUT='WAVE_HCLIST_MASTER'),
                                    fibers=valid_efibers,
                                    filetype='.fits',
                                    intype=[out_ext_e2ds, out_ext_e2dsff],
                                    suffix='_wavem_hclines',
                                    dbname='calibration', dbkey='WAVEHCL',
                                    datatype='table',
                                    outclass=mcalib_ofile)

# fp line file from master
out_wave_fplist_master = drs_finput('WAVE_FPLIST_MASTER',
                                    hkeys=dict(KW_OUTPUT='WAVE_FPLIST_MASTER'),
                                    fibers=valid_efibers,
                                    filetype='.fits',
                                    intype=[out_ext_e2ds, out_ext_e2dsff],
                                    suffix='_wavem_fplines',
                                    dbname='calibration', dbkey='WAVEFPL',
                                    datatype='table',
                                    outclass=mcalib_ofile)

# teh cavity file polynomial file
out_wavem_cavity = drs_finput('WAVEM_CAV', hkeys=dict(KW_OUTPUT='WAVEM_CAV'),
                              filetype='.fits',
                              fibers=['A'],
                              intype=[out_ext_e2ds, out_ext_e2dsff],
                              suffix='_wavecav_',
                              dbname='calibration', dbkey='WAVECAV',
                              outclass=mcalib_ofile)

# the default wave master
out_wave_master = drs_finput('WAVESOL_DEFAULT',
                             hkeys=dict(KW_OUTPUT='WAVESOL_DEFAULT'),
                             fibers=valid_efibers,
                             filetype='.fits',
                             intype=[out_ext_e2ds, out_ext_e2dsff],
                             suffix='_wavem',
                             dbname='calibration', dbkey='WAVESOL_DEFAULT',
                             outclass=mcalib_ofile)

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
# resolution map
out_wavem_res = drs_finput('WAVERES', hkeys=dict(KW_OUTPUT='WAVE_RES'),
                           fibers=valid_efibers,
                           filetype='.fits',
                           intype=[out_ext_e2ds, out_ext_e2dsff],
                           suffix='_wavemres',
                           outclass=mcalib_ofile)

# hc resolution map
out_wavem_hcres = drs_finput('WAVERES', hkeys=dict(KW_OUTPUT='WAVE_RES'),
                             fibers=valid_efibers,
                             filetype='.fits',
                             intype=[out_ext_e2ds, out_ext_e2dsff],
                             suffix='_wavemres',
                             outclass=mcalib_ofile)

# fp global results table
out_wavem_res_table = drs_input('WAVE_FPRESTAB',
                                hkeys=dict(KW_OUTPUT='WAVE_FPRESTAB'),
                                fibers=valid_efibers,
                                filetype='.tbl',
                                intype=[out_ext_e2ds, out_ext_e2dsff],
                                outclass=set_ofile,
                                basename='apero_wave_results')

# fp line list table
out_wavem_ll_table = drs_input('WAVE_FPLLTABL',
                               hkeys=dict(KW_OUTPUT='WAVE_FPLLTAB'),
                               fibers=valid_efibers,
                               filetype='.tbl',
                               intype=[out_ext_e2ds, out_ext_e2dsff],
                               suffix='_mhc_lines',
                               outclass=mcalib_ofile)

# add wave outputs to output fileset
red_file.addset(out_wavem_hcres)
red_file.addset(out_wavem_res_table)
red_file.addset(out_wavem_ll_table)

# -----------------------------------------------------------------------------
# wave files
# -----------------------------------------------------------------------------
# wave solution using night modifications
out_wave_night = drs_finput('WAVE_NIGHT', hkeys=dict(KW_OUTPUT='WAVE_NIGHT'),
                            fibers=valid_efibers,
                            filetype='.fits',
                            intype=[out_ext_e2ds, out_ext_e2dsff],
                            suffix='_wave_night',
                            dbname='calibration', dbkey='WAVE',
                            outclass=calib_ofile)

# hc initial linelist
out_wave_hcline = drs_input('WAVEHCLL', hkeys=dict(KW_OUTPUT='WAVEHCLL'),
                            fibers=valid_efibers,
                            filetype='.dat',
                            intype=[out_ext_e2ds, out_ext_e2dsff],
                            suffix='_linelist',
                            outclass=calib_ofile)

# hc resolution map
out_wave_hcres = drs_finput('WAVERES', hkeys=dict(KW_OUTPUT='WAVE_RES'),
                            fibers=valid_efibers,
                            filetype='.fits',
                            intype=[out_ext_e2ds, out_ext_e2dsff],
                            suffix='_waveres',
                            outclass=calib_ofile)

# fp global results table
out_wave_res_table = drs_input('WAVE_FPRESTAB',
                               hkeys=dict(KW_OUTPUT='WAVE_FPRESTAB'),
                               fibers=valid_efibers,
                               filetype='.tbl',
                               intype=[out_ext_e2ds, out_ext_e2dsff],
                               outclass=set_ofile,
                               basename='apero_wave_results')

# fp line list table
out_wave_ll_table = drs_input('WAVE_FPLLTABL',
                              hkeys=dict(KW_OUTPUT='WAVE_FPLLTAB'),
                              fibers=valid_efibers,
                              filetype='.tbl',
                              intype=[out_ext_e2ds, out_ext_e2dsff],
                              suffix='_hc_lines',
                              outclass=calib_ofile)

# hc line file from night
out_wave_hclist = drs_finput('WAVE_HCLIST', hkeys=dict(KW_OUTPUT='WAVE_HCLIST'),
                             fibers=valid_efibers,
                             filetype='.fits',
                             intype=[out_ext_e2ds, out_ext_e2dsff],
                             suffix='_wave_hclines',
                             outclass=calib_ofile)

# fp line file from night
out_wave_fplist = drs_finput('WAVE_FPLIST', hkeys=dict(KW_OUTPUT='WAVE_FPLIST'),
                             fibers=valid_efibers,
                             filetype='.fits',
                             intype=[out_ext_e2ds, out_ext_e2dsff],
                             suffix='_wave_fplines',
                             outclass=calib_ofile)

# add wave outputs to output fileset
red_file.addset(out_wave_night)
red_file.addset(out_wave_hcline)
red_file.addset(out_wave_hcres)
red_file.addset(out_wave_res_table)
red_file.addset(out_wave_ll_table)
red_file.addset(out_wave_hclist)
red_file.addset(out_wave_fplist)
calib_file.addset(out_wave_night)

# -----------------------------------------------------------------------------
# make telluric
# -----------------------------------------------------------------------------
# define valid fibers for telluric process
valid_tfibers = ['A']

# cleaned spectrum
out_tellu_pclean = drs_finput('TELLU_PCLEAN',
                              hkeys=dict(KW_OUTPUT='TELLU_PCLEAN'),
                              fibers=valid_tfibers,
                              filetype='.fits', intype=out_ext_e2dsff,
                              suffix='_tellu_pclean', remove_insuffix=True,
                              dbname='telluric', dbkey='TELLU_PCLEAN',
                              outclass=tellu_ofile)

# convolved tapas map (with master wave solution)
out_tellu_conv = drs_ninput('TELLU_CONV', hkeys=dict(KW_OUTPUT='TELLU_CONV'),
                            fibers=valid_tfibers,
                            filetype='.npy',
                            intype=[out_wavem_sol, out_wave_night,
                                    out_wave_master],
                            suffix='_tellu_conv', remove_insuffix=True,
                            dbname='telluric', dbkey='TELLU_CONV',
                            outclass=tellu_ofile)

# tapas file in format for pre-cleaning
out_tellu_spl_npy = drs_ninput('TELLU_TAPAS', filetype='.npy',
                               basename='tapas_spl.npy',
                               dbname='telluric', dbkey='TELLU_TAPAS',
                               outclass=tellu_set_ofile)

# transmission map
out_tellu_trans = drs_finput('TELLU_TRANS', hkeys=dict(KW_OUTPUT='TELLU_TRANS'),
                             fibers=valid_tfibers,
                             filetype='.fits', intype=out_ext_e2dsff,
                             suffix='_tellu_trans', remove_insuffix=True,
                             dbname='telluric', dbkey='TELLU_TRANS',
                             outclass=tellu_ofile)

# transmission model
out_tellu_model = drs_finput('TRANS_MODEL', hkeys=dict(KW_OUTPUT='TRANS_MODEL'),
                             fibers=valid_tfibers, filetype='.fits',
                             basename='trans_model_{0}',  # add fiber manually
                             dbname='telluric', dbkey='TELLU_MODEL',
                             outclass=tellu_set_ofile)

# add make_telluric outputs to output fileset
red_file.addset(out_tellu_pclean)
red_file.addset(out_tellu_conv)
red_file.addset(out_tellu_trans)
red_file.addset(out_tellu_spl_npy)
red_file.addset(out_tellu_model)
tellu_file.addset(out_tellu_pclean)
tellu_file.addset(out_tellu_conv)
tellu_file.addset(out_tellu_trans)
tellu_file.addset(out_tellu_spl_npy)
tellu_file.addset(out_tellu_model)

# -----------------------------------------------------------------------------
# fit telluric
# -----------------------------------------------------------------------------
# absorption files (npy file)
out_tellu_abso_npy = drs_ninput('ABSO_NPY',
                                filetype='.npy',
                                basename='tellu_save.npy',
                                outclass=tellu_set_ofile)
out_tellu_abso1_npy = drs_ninput('ABSO1_NPY',
                                 filetype='.npy',
                                 basename='tellu_save1.npy',
                                 outclass=tellu_set_ofile)

# telluric corrected e2ds spectrum
out_tellu_obj = drs_finput('TELLU_OBJ', hkeys=dict(KW_OUTPUT='TELLU_OBJ'),
                           fibers=valid_tfibers,
                           filetype='.fits', intype=out_ext_e2dsff,
                           suffix='_e2dsff_tcorr', remove_insuffix=True,
                           dbname='telluric', dbkey='TELLU_OBJ',
                           outclass=tellu_ofile,
                           s1d=['SC1D_W_FILE', 'SC1D_V_FILE'])

# telluric corrected s1d spectrum
out_tellu_sc1d_w = drs_finput('SC1D_W_FILE',
                              hkeys=dict(KW_OUTPUT='SC1D_W_FILE'),
                              fibers=valid_tfibers,
                              filetype='.fits', intype=out_ext_e2dsff,
                              suffix='_s1d_w_tcorr', remove_insuffix=True,
                              outclass=tellu_ofile, datatype='table')
out_tellu_sc1d_v = drs_finput('SC1D_V_FILE',
                              hkeys=dict(KW_OUTPUT='SC1D_V_FILE'),
                              fibers=valid_tfibers,
                              filetype='.fits', intype=out_ext_e2dsff,
                              suffix='_s1d_v_tcorr', remove_insuffix=True,
                              outclass=tellu_ofile, datatype='table')

# reconstructed telluric absorption file
out_tellu_recon = drs_finput('TELLU_RECON', hkeys=dict(KW_OUTPUT='TELLU_RECON'),
                             fibers=valid_tfibers,
                             filetype='.fits', intype=out_ext_e2dsff,
                             suffix='_e2dsff_recon', remove_insuffix=True,
                             dbname='telluric', dbkey='TELLU_RECON',
                             outclass=tellu_ofile,
                             s1d=['RC1D_W_FILE', 'RC1D_V_FILE'])

# reconstructed telluric 1d absorption
out_tellu_rc1d_w = drs_finput('RC1D_W_FILE',
                              hkeys=dict(KW_OUTPUT='RC1D_W_FILE'),
                              fibers=valid_tfibers,
                              filetype='.fits', intype=out_ext_e2dsff,
                              suffix='_s1d_w_recon', remove_insuffix=True,
                              outclass=tellu_ofile, datatype='table')
out_tellu_rc1d_v = drs_finput('RC1D_V_FILE',
                              hkeys=dict(KW_OUTPUT='RC1D_V_FILE'),
                              fibers=valid_tfibers,
                              filetype='.fits', intype=out_ext_e2dsff,
                              suffix='_s1d_v_recon', remove_insuffix=True,
                              outclass=tellu_ofile, datatype='table')

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
                                fibers=valid_tfibers,
                                filetype='.fits',
                                intype=[out_ext_e2dsff, out_tellu_obj],
                                basename='Template',
                                dbname='telluric', dbkey='TELLU_TEMP',
                                outclass=tellu_set_ofile)

# template cube file (after shift)
out_tellu_bigcube = drs_finput('TELLU_BIGCUBE',
                               hkeys=dict(KW_OUTPUT='TELLU_BIGCUBE'),
                               fibers=valid_tfibers,
                               filetype='.fits',
                               intype=[out_ext_e2dsff, out_tellu_obj],
                               basename='BigCube',
                               outclass=tellu_set_ofile)

# template cube file (before shift)
out_tellu_bigcube0 = drs_finput('TELLU_BIGCUBE0',
                                hkeys=dict(KW_OUTPUT='TELLU_BIGCUBE0'),
                                fibers=valid_tfibers,
                                filetype='.fits',
                                intype=[out_ext_e2dsff, out_tellu_obj],
                                basename='BigCube0',
                                outclass=tellu_set_ofile)

# s1d template file (median)
out_tellu_s1d_template = drs_finput('TELLU_TEMP_S1D',
                                    hkeys=dict(KW_OUTPUT='TELLU_TEMP_S1D'),
                                    fibers=valid_tfibers,
                                    filetype='.fits',
                                    intype=[out_ext_e2dsff, out_tellu_obj],
                                    basename='Template_s1d', datatype='table',
                                    outclass=tellu_set_ofile)

# s1d cibe file (after shift)
out_tellu_s1d_bigcube = drs_finput('TELLU_BIGCUBE_S1D',
                                   hkeys=dict(KW_OUTPUT='TELLU_BIGCUBE_S1D'),
                                   fibers=valid_tfibers,
                                   filetype='.fits',
                                   intype=[out_ext_e2dsff, out_tellu_obj],
                                   basename='BigCube_s1d',
                                   outclass=tellu_set_ofile)

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
# valid ccf_fibers
valid_ccf_fibers = ['A', 'B']
# ccf out file
out_ccf_fits = drs_finput('CCF_RV', hkeys=dict(KW_OUTPUT='CCF_RV'),
                          fibers=valid_ccf_fibers,
                          filetype='.fits',
                          suffix='_ccf',
                          intype=[out_ext_e2dsff, out_tellu_obj],
                          datatype='table',
                          outclass=general_ofile)

red_file.addset(out_ccf_fits)

# =============================================================================
# Post processed Files
# =============================================================================
# generic post processed file
post_file = drs_oinput('DRS_POST', filetype='.fits', suffix='',
                       outclass=post_ofile, instrument=__INSTRUMENT__)
# define a list of wave outputs
wave_files = DrsFileGroup(name='WAVE_FILES',
                          files=[out_wavem_sol, out_wave_night,
                                 out_wave_master])

# -----------------------------------------------------------------------------
# post processed 2D extraction file
# -----------------------------------------------------------------------------
post_e_file = drs_oinput('DRS_POST_E', filetype='.fits', suffix='e.fits',
                         outclass=post_ofile, inext='o', required=True)

# add extensions
post_e_file.add_ext('PP', pp_file, pos=0, header_only=True, block_kind='tmp',
                    hkeys=dict(KW_DPRTYPE=['OBJ_FP', 'OBJ_DARK', 'POLAR_FP',
                                           'POLAR_DARK']),
                    remove_drs_hkeys=True)

post_e_file.add_ext('EXT_A', out_ext_e2dsff, pos=1, fiber='A', block_kind='red',
                    link='PP', hlink='KW_IDENTIFIER', clear_file=True,
                    tag='FluxA')

post_e_file.add_ext('EXT_B', out_ext_e2dsff, pos=2, fiber='B', block_kind='red',
                    link='EXT_A', hlink='KW_IDENTIFIER', clear_file=True,
                    tag='FluxB')

post_e_file.add_ext('WAVE_A', wave_files, pos=3, fiber='A', block_kind='red',
                    link='EXT_A', hlink='CALIB::WAVE', tag='WaveA')

post_e_file.add_ext('WAVE_B', wave_files, pos=4, fiber='B', block_kind='red',
                    link='EXT_B', hlink='CALIB::WAVE', tag='WaveB')

post_e_file.add_ext('BLAZE_A', out_ff_blaze, pos=5, fiber='A',
                    block_kind='red', link='EXT_A', hlink='CALIB::BLAZE',
                    tag='BlazeA')

post_e_file.add_ext('BLAZE_B', out_ff_blaze, pos=6, fiber='B',
                    block_kind='red', link='EXT_B', hlink='CALIB::BLAZE',
                    tag='BlazeB')
# move header keys
post_e_file.add_hkey('KW_VERSION', inheader='EXT_AB', outheader='PP')
post_e_file.add_hkey('KW_DRS_DATE_NOW', inheader='EXT_AB', outheader='PP')
# add to post processed file set
post_file.addset(post_e_file)

# -----------------------------------------------------------------------------
# post processed 1D extraction file
# -----------------------------------------------------------------------------
post_s_file = drs_oinput('DRS_POST_S', filetype='.fits', suffix='s.fits',
                         outclass=post_ofile, inext='o', required=True)
post_s_file.add_ext('PP', pp_file, pos=0, header_only=True, block_kind='tmp',
                    hkeys=dict(KW_DPRTYPE=['OBJ_FP', 'OBJ_DARK', 'POLAR_FP',
                                           'POLAR_DARK']),
                    remove_drs_hkeys=True)
# s1d w is a composite table
post_s_file.add_ext('S1D_W', 'table', pos=1, block_kind='red',
                    link='PP', hlink='KW_IDENTIFIER',
                    extname='UniformWavelength', tag='UniformWavelength')
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
                    link='PP', hlink='KW_IDENTIFIER',
                    extname='UniformVelocity', tag='UniformVelocity')

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
post_s_file.add_hkey('KW_VERSION', inheader='S1D_W', outheader='PP')
post_s_file.add_hkey('KW_DRS_DATE_NOW', inheader='S1D_W', outheader='PP')
# add to post processed file set
post_file.addset(post_s_file)

# -----------------------------------------------------------------------------
# post processed telluric file
# -----------------------------------------------------------------------------
post_t_file = drs_oinput('DRS_POST_T', filetype='.fits', suffix='t.fits',
                         outclass=post_ofile, inext='o', required=False)
# add extensions
post_t_file.add_ext('PP', pp_file, pos=0, header_only=True, block_kind='tmp',
                    hkeys=dict(KW_DPRTYPE=['OBJ_FP', 'OBJ_DARK', 'POLAR_FP',
                                           'POLAR_DARK']),
                    remove_drs_hkeys=True)
post_t_file.add_ext('TELLU_A', out_tellu_obj, pos=1, fiber='A',
                    link='PP', hlink='KW_IDENTIFIER', block_kind='red',
                    clear_file=True, tag='FluxA')

post_t_file.add_ext('WAVE_A', wave_files, pos=2, fiber='A',
                    link='TELLU_A', hlink='CALIB::WAVE', block_kind='red',
                    clear_file=True, tag='WaveA')

post_t_file.add_ext('BLAZE_A', out_ff_blaze, pos=3, fiber='A',
                    link='TELLU_A', hlink='CALIB::BLAZE', block_kind='red',
                    clear_file=True, tag='BlazeA')

post_t_file.add_ext('RECON_A', out_tellu_recon, pos=4, fiber='A',
                    link='TELLU_A', hlink='KW_IDENTIFIER', block_kind='red',
                    clear_file=True, tag='Recon')

# TODO: If precleaning fails --> no OHLINE file produced
post_t_file.add_ext('OHLINE', out_tellu_pclean, pos=5, fiber='A',
                    link='TELLU_A', hlink='KW_IDENTIFIER',
                    block_kind='red', clear_file=True, tag='OHLine',
                    extname='SKY_MODEL')
# move header keys
post_t_file.add_hkey('KW_VERSION', inheader='TELLU_AB', outheader='PP')
post_t_file.add_hkey('KW_DRS_DATE_NOW', inheader='TELLU_AB', outheader='PP')
# add to post processed file set
post_file.addset(post_t_file)

# -----------------------------------------------------------------------------
# post processed velocity file
# -----------------------------------------------------------------------------
# Not always required (i.e. for hot stars)
post_v_file = drs_oinput('DRS_POST_V', filetype='.fits', suffix='v.fits',
                         outclass=post_ofile, inext='o', required=False)
post_v_file.add_ext('PP', pp_file, pos=0, header_only=True, block_kind='tmp',
                    hkeys=dict(KW_DPRTYPE=['OBJ_FP', 'OBJ_DARK', 'POLAR_FP',
                                           'POLAR_DARK']),
                    clear_file=True, remove_drs_hkeys=True)

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
