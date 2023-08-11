#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO DrsFile definitions for SPIROU

# For fits files

file_name = drs_finput(name, filetype, suffix=, outclass, instrument,
                       description)


Created on 2018-10-31 at 18:06

@author: cook
"""
import os

from apero.base import base
from apero.core import constants
from apero.core.core import drs_file
from apero.core.core import drs_out_file as out

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'config.instruments.spirou.file_defintions.py'
__INSTRUMENT__ = 'SPIROU'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Instrument name in header
INSTRUMENT_NAME = 'SPIRou'

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
lbl_ofile = out.LBLOutFile()
post_ofile = out.PostOutFile()
calib_ofile = out.CalibOutFile()
refcalib_ofile = out.RefCalibOutFile()
tellu_ofile = out.TelluOutFile()
reftellu_ofile = out.RefTelluOutFile()
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
                      outclass=blank_ofile, instrument=__INSTRUMENT__,
                      description='Generic raw file')
# -----------------------------------------------------------------------------
# raw dark files
# raw_dark_dark = drs_finput('RAW_DARK_DARK', KW_CCAS='pos_pk', KW_CREF='pos_pk',
#                            KW_OBSTYPE='DARK',
#                            filetype='.fits', suffix='', inext='d.fits',
#                            outclass=blank_ofile)
# raw_file.addset(raw_dark_dark)

# raw dark in P4 (internal dark)
raw_dark_dark_int = drs_finput('RAW_DARK_DARK_INT', filetype='.fits',
                               suffix='', inext='.fits', outclass=blank_ofile,
                               hkeys=dict(KW_CCAS='pos_pk', KW_CREF='pos_pk',
                                          KW_OBSTYPE='DARK', KW_CALIBWH='P4',
                                          KW_INSTRUMENT=INSTRUMENT_NAME),
                               description='Raw sci=DARK calib=DARK file, '
                                           'where dark is an internal dark')
raw_file.addset(raw_dark_dark_int)

# raw dark in P5 (telescope dark)
raw_dark_dark_tel = drs_finput('RAW_DARK_DARK_TEL', filetype='.fits',
                               suffix='', inext='.fits', outclass=blank_ofile,
                               hkeys=dict(KW_CCAS='pos_pk', KW_CREF='pos_pk',
                                          KW_OBSTYPE='DARK', KW_CALIBWH='P5',
                                          KW_INSTRUMENT=INSTRUMENT_NAME),
                               description='Raw sci=DARK calib=DARK file, '
                                           'where dark is a telescope dark')
raw_file.addset(raw_dark_dark_tel)

# sky observation (sky dark)
raw_dark_dark_sky = drs_finput('RAW_DARK_DARK_SKY', filetype='.fits',
                               suffix='', inext='.fits', outclass=blank_ofile,
                               hkeys=dict(KW_CCAS='pos_pk', KW_CREF='pos_pk',
                                          KW_OBSTYPE='OBJECT',
                                          KW_TARGET_TYPE='SKY',
                                          KW_INSTRUMENT=INSTRUMENT_NAME),
                               description='Raw sci=DARK calib=DARK file, '
                                           'where dark is a sky dark')
raw_file.addset(raw_dark_dark_sky)

# sky observations (with fp)
raw_dark_fp_sky = drs_finput('RAW_DARK_FP_SKY', filetype='.fits', suffix='',
                             inext='.fits', outclass=blank_ofile,
                             hkeys=dict(KW_CCAS='pos_pk', KW_CREF='pos_fp',
                                        KW_OBSTYPE='OBJECT',
                                        KW_TARGET_TYPE='SKY',
                                        KW_INSTRUMENT=INSTRUMENT_NAME),
                             description='Raw sci=DARK calib=FP file, '
                                         'where dark is an internal dark')
raw_file.addset(raw_dark_fp_sky)

# -----------------------------------------------------------------------------
# raw flat files
raw_dark_flat = drs_finput('RAW_DARK_FLAT', outclass=blank_ofile,
                           filetype='.fits', suffix='',
                           hkeys=dict(KW_CCAS='pos_pk', KW_CREF='pos_wl',
                                      KW_OBSTYPE='FLAT',
                                      KW_INSTRUMENT=INSTRUMENT_NAME),
                           description='Raw sci=DARK calib=FLAT file,'
                                       ' where dark is an internal dark')
raw_file.addset(raw_dark_flat)

raw_flat_dark = drs_finput('RAW_FLAT_DARK', outclass=blank_ofile,
                           filetype='.fits', suffix='',
                           hkeys=dict(KW_CCAS='pos_wl', KW_CREF='pos_pk',
                                      KW_OBSTYPE='FLAT',
                                      KW_INSTRUMENT=INSTRUMENT_NAME),
                           description='Raw sci=FLAT calib=DARK file,'
                                       ' where dark is an internal dark')
raw_file.addset(raw_flat_dark)

raw_flat_flat = drs_finput('RAW_FLAT_FLAT', outclass=blank_ofile,
                           filetype='.fits', suffix='',
                           hkeys=dict(KW_CCAS='pos_wl', KW_CREF='pos_wl',
                                      KW_OBSTYPE='FLAT',
                                      KW_INSTRUMENT=INSTRUMENT_NAME),
                           description='Raw sci=FLAT calib=FLAT file')
raw_file.addset(raw_flat_flat)

raw_flat_fp = drs_finput('RAW_FLAT_FP', outclass=blank_ofile,
                         filetype='.fits', suffix='',
                         hkeys=dict(KW_CCAS='pos_wl', KW_CREF='pos_fp',
                                    KW_OBSTYPE='FLAT',
                                    KW_INSTRUMENT=INSTRUMENT_NAME),
                         description='Raw sci=FLAT calib=FP file')
raw_file.addset(raw_flat_fp)

# -----------------------------------------------------------------------------
# raw align files
raw_dark_fp = drs_finput('RAW_DARK_FP', outclass=blank_ofile,
                         filetype='.fits', suffix='',
                         hkeys=dict(KW_CCAS='pos_pk', KW_CREF='pos_fp',
                                    KW_OBSTYPE='ALIGN',
                                    KW_INSTRUMENT=INSTRUMENT_NAME),
                         description='Raw sci=DARK calib=FP file,'
                                     ' where dark is an internal dark')
raw_file.addset(raw_dark_fp)

raw_fp_dark = drs_finput('RAW_FP_DARK', outclass=blank_ofile,
                         filetype='.fits', suffix='',
                         hkeys=dict(KW_CCAS='pos_fp', KW_CREF='pos_pk',
                                    KW_OBSTYPE='ALIGN',
                                    KW_INSTRUMENT=INSTRUMENT_NAME),
                         description='Raw sci=FP calib=DARK file, '
                                     ' where dark is an internal dark')
raw_file.addset(raw_fp_dark)

raw_fp_flat = drs_finput('RAW_FP_FLAT', outclass=blank_ofile,
                         filetype='.fits', suffix='',
                         hkeys=dict(KW_CCAS='pos_fp', KW_CREF='pos_wl',
                                    KW_OBSTYPE='ALIGN',
                                    KW_INSTRUMENT=INSTRUMENT_NAME),
                         description='Raw sci=FP calib=FLAT file')
raw_file.addset(raw_fp_flat)

raw_fp_fp = drs_finput('RAW_FP_FP', outclass=blank_ofile,
                       filetype='.fits', suffix='',
                       hkeys=dict(KW_CCAS='pos_fp', KW_CREF='pos_fp',
                                  KW_OBSTYPE='ALIGN',
                                  KW_INSTRUMENT=INSTRUMENT_NAME),
                       description='Raw sci=FP calib=FP file')
raw_file.addset(raw_fp_fp)

# -----------------------------------------------------------------------------
# raw LFC files
raw_lfc_lfc = drs_finput('RAW_LFC_LFC', filetype='.fits', suffix='',
                         outclass=blank_ofile,
                         hkeys=dict(KW_CCAS='pos_rs', KW_CREF='pos_rs',
                                    KW_OBSTYPE='ALIGN',
                                    KW_INSTRUMENT=INSTRUMENT_NAME),
                         description='Raw sci=LFC calib=LFC file')
raw_file.addset(raw_lfc_lfc)

raw_lfc_fp = drs_finput('RAW_LFC_FP', outclass=blank_ofile,
                        filetype='.fits', suffix='',
                        hkeys=dict(KW_CCAS='pos_rs', KW_CREF='pos_fp',
                                   KW_OBSTYPE='ALIGN',
                                   KW_INSTRUMENT=INSTRUMENT_NAME),
                        description='Raw sci=LFC calib=FP file')
raw_file.addset(raw_lfc_fp)

raw_fp_lfc = drs_finput('RAW_FP_LFC', outclass=blank_ofile,
                        filetype='.fits', suffix='',
                        hkeys=dict(KW_CCAS='pos_fp', KW_CREF='pos_rs',
                                   KW_OBSTYPE='ALIGN',
                                   KW_INSTRUMENT=INSTRUMENT_NAME),
                        description='Raw sci=FP calib=LFC file')
raw_file.addset(raw_fp_lfc)

# -----------------------------------------------------------------------------
# raw object files
raw_obj_dark = drs_finput('RAW_OBJ_DARK', outclass=blank_ofile,
                          hkeys=dict(KW_CCAS='pos_pk', KW_CREF='pos_pk',
                                     KW_OBSTYPE='OBJECT',
                                     KW_DRS_MODE='SPECTROSCOPY',
                                     KW_TARGET_TYPE='TARGET',
                                     KW_INSTRUMENT=INSTRUMENT_NAME),
                          description='Raw sci=OBJ calib=DARK file,'
                                      ' where dark is an internal dark')
raw_file.addset(raw_obj_dark)

raw_obj_fp = drs_finput('RAW_OBJ_FP', outclass=blank_ofile, filetype='.fits',
                        suffix='', inext='.fits',
                        hkeys=dict(KW_CCAS='pos_pk', KW_CREF='pos_fp',
                                   KW_OBSTYPE='OBJECT',
                                   KW_DRS_MODE='SPECTROSCOPY',
                                   KW_TARGET_TYPE='TARGET',
                                   KW_INSTRUMENT=INSTRUMENT_NAME),
                        description='Raw sci=OBJ calib=FP file')
raw_file.addset(raw_obj_fp)

raw_obj_hc1 = drs_finput('RAW_OBJ_HCONE', outclass=blank_ofile,
                         filetype='.fits', suffix='', inext='.fits',
                         hkeys=dict(KW_CCAS='pos_pk', KW_CREF='pos_hc1',
                                    KW_OBSTYPE='OBJECT',
                                    KW_TARGET_TYPE='TARGET',
                                    KW_INSTRUMENT=INSTRUMENT_NAME),
                         description='Raw sci=OBJ calib=Hollow Cathode file,'
                                     ' Uranium Neon lamp')
raw_file.addset(raw_obj_hc1)

raw_obj_hc2 = drs_finput('RAW_OBJ_HCTWO', outclass=blank_ofile,
                         filetype='.fits', suffix='', inext='.fits',
                         hkeys=dict(KW_CCAS='pos_pk', KW_CREF='pos_hc2',
                                    KW_OBSTYPE='OBJECT',
                                    KW_TARGET_TYPE='TARGET',
                                    KW_INSTRUMENT=INSTRUMENT_NAME),
                         description='Raw sci=OBJ calib=Hollow Cathode file,'
                                     ' Thorium Argon lamp')
raw_file.addset(raw_obj_hc2)

# raw object files
raw_polar_dark = drs_finput('RAW_POLAR_DARK', outclass=blank_ofile,
                            hkeys=dict(KW_CCAS='pos_pk', KW_CREF='pos_pk',
                                       KW_OBSTYPE='OBJECT',
                                       KW_DRS_MODE='POLAR',
                                       KW_TARGET_TYPE='TARGET',
                                       KW_INSTRUMENT=INSTRUMENT_NAME),
                            description='Raw sci=POLAR calib=DARK,'
                                        ' where dark is an internal dark')
raw_file.addset(raw_polar_dark)

raw_polar_fp = drs_finput('RAW_POLAR_FP', outclass=blank_ofile, filetype='.fits',
                          suffix='', inext='.fits',
                          hkeys=dict(KW_CCAS='pos_pk', KW_CREF='pos_fp',
                                     KW_OBSTYPE='OBJECT',
                                     KW_DRS_MODE='POLAR',
                                     KW_TARGET_TYPE='TARGET',
                                     KW_INSTRUMENT=INSTRUMENT_NAME),
                          description='Raw sci=POLAR calib=FP')
raw_file.addset(raw_polar_fp)

# -----------------------------------------------------------------------------
# raw comparison files
raw_dark_hc1 = drs_finput('RAW_DARK_HCONE', outclass=blank_ofile,
                          filetype='.fits', suffix='',
                          hkeys=dict(KW_CCAS='pos_pk', KW_CREF='pos_hc1',
                                     KW_OBSTYPE='COMPARISON',
                                     KW_INSTRUMENT=INSTRUMENT_NAME),
                          description='Raw sci=DARK calib=Hollow Cathode file,'
                                      ' where dark is an internal dark,'
                                      ' Uranium Neon lamp')
raw_file.addset(raw_dark_hc1)

raw_dark_hc2 = drs_finput('RAW_DARK_HCTWO', outclass=blank_ofile,
                          filetype='.fits', suffix='',
                          hkeys=dict(KW_CCAS='pos_pk', KW_CREF='pos_hc2',
                                     KW_OBSTYPE='COMPARISON',
                                     KW_INSTRUMENT=INSTRUMENT_NAME),
                          description='Raw sci=DARK calib=Hollow Cathode file,'
                                      ' where dark is an internal dark,'
                                      ' Thorium Argon lamp')
raw_file.addset(raw_dark_hc2)

raw_fp_hc1 = drs_finput('RAW_FP_HCONE', outclass=blank_ofile,
                        filetype='.fits', suffix='',
                        hkeys=dict(KW_CCAS='pos_fp', KW_CREF='pos_hc1',
                                   KW_OBSTYPE='COMPARISON',
                                   KW_INSTRUMENT=INSTRUMENT_NAME),
                        description='Raw sci=FP calib=Hollow Cathode file,'
                                    ' Uranium Neon lamp')
raw_file.addset(raw_fp_hc1)

raw_fp_hc2 = drs_finput('RAW_FP_HCTWO', outclass=blank_ofile,
                        filetype='.fits', suffix='',
                        hkeys=dict(KW_CCAS='pos_fp', KW_CREF='pos_hc2',
                                   KW_OBSTYPE='COMPARISON',
                                   KW_INSTRUMENT=INSTRUMENT_NAME),
                        description='Raw sci=FP calib=Hollow Cathode file,'
                                    ' Thorium Argon lamp')
raw_file.addset(raw_fp_hc2)

raw_hc1_fp = drs_finput('RAW_HCONE_FP', outclass=blank_ofile,
                        filetype='.fits', suffix='',
                        hkeys=dict(KW_CCAS='pos_hc1', KW_CREF='pos_fp',
                                   KW_OBSTYPE='COMPARISON',
                                   KW_INSTRUMENT=INSTRUMENT_NAME),
                        description='Raw sci=Hollow Cathode calib=FP file,'
                                    ' Uranium Neion lamp')
raw_file.addset(raw_hc1_fp)

raw_hc2_fp = drs_finput('RAW_HCTWO_FP', outclass=blank_ofile,
                        filetype='.fits', suffix='',
                        hkeys=dict(KW_CCAS='pos_hc2', KW_CREF='pos_fp',
                                   KW_OBSTYPE='COMPARISON',
                                   KW_INSTRUMENT=INSTRUMENT_NAME),
                        description='Raw sci=Hollow Cathode calib=FP file,'
                                    ' Thorium Argon lamp')
raw_file.addset(raw_hc2_fp)

raw_hc1_hc1 = drs_finput('RAW_HCONE_HCONE', filetype='.fits', suffix='',
                         outclass=blank_ofile,
                         hkeys=dict(KW_CCAS='pos_hc1', KW_CREF='pos_hc1',
                                    KW_OBSTYPE='COMPARISON',
                                    KW_INSTRUMENT=INSTRUMENT_NAME),
                         description='Raw sci=Hollow Cathode calib=Hollow '
                                     'Cathode file, Uranium Neon lamp')
raw_file.addset(raw_hc1_hc1)

raw_hc2_hc2 = drs_finput('RAW_HCTWO_HCTWO', filetype='.fits', suffix='',
                         outclass=blank_ofile,
                         hkeys=dict(KW_CCAS='pos_hc2', KW_CREF='pos_hc2',
                                    KW_OBSTYPE='COMPARISON',
                                    KW_INSTRUMENT=INSTRUMENT_NAME),
                         description='Raw sci=Hollow Cathode calib=Hollow '
                                     'Cathode file, Thorium Argon lamp')
raw_file.addset(raw_hc2_hc2)

raw_hc1_dark = drs_finput('RAW_HCONE_DARK', filetype='.fits', suffix='',
                          outclass=blank_ofile,
                          hkeys=dict(KW_CCAS='pos_hc1', KW_CREF='pos_pk',
                                     KW_OBSTYPE='COMPARISON',
                                     KW_INSTRUMENT=INSTRUMENT_NAME),
                          description='Raw sci=Hollow Cathode calib=DARK file,'
                                      ' where dark is an internal dark,'
                                      ' Uranium Neon lamp')
raw_file.addset(raw_hc1_dark)

raw_hc2_dark = drs_finput('RAW_HCTWO_DARK', filetype='.fits', suffix='',
                          outclass=blank_ofile,
                          hkeys=dict(KW_CCAS='pos_hc2', KW_CREF='pos_pk',
                                     KW_OBSTYPE='COMPARISON',
                                     KW_INSTRUMENT=INSTRUMENT_NAME),
                          description='Raw sci=Hollow Cathode calib=DARK file,'
                                      ' where dark is an internal dark,'
                                      ' Thorium Argon lamp')
raw_file.addset(raw_hc2_dark)

# =============================================================================
# Preprocessed Files
# =============================================================================
# generic pp file
pp_file = drs_finput('DRS_PP', filetype='.fits', suffix='_pp',
                     outclass=general_ofile, intype=raw_file,
                     instrument=__INSTRUMENT__,
                     description='Generic pre-processed file')

# -----------------------------------------------------------------------------
# dark
# pp_dark_dark = drs_finput('DARK_DARK', KW_DPRTYPE='DARK_DARK',
#                           filetype='.fits',
#                           suffix='_pp', intype=raw_dark_dark,
#                           inext='.fits', outclass=general_ofile)
# pp_file.addset(pp_dark_dark)

pp_dark_dark_int = drs_finput('DARK_DARK_INT', filetype='.fits',
                              suffix='_pp', intype=raw_dark_dark_int,
                              inext='.fits', outclass=general_ofile,
                              hkeys=dict(KW_DPRTYPE='DARK_DARK_INT'),
                              description='Preprocessed sci=DARK calib=DARK'
                                          ' file, where dark is an internal'
                                          ' dark')
pp_file.addset(pp_dark_dark_int)

pp_dark_dark_tel = drs_finput('DARK_DARK_TEL', filetype='.fits',
                              suffix='_pp', intype=raw_dark_dark_tel,
                              inext='.fits', outclass=general_ofile,
                              hkeys=dict(KW_DPRTYPE='DARK_DARK_TEL'),
                              description='Preprocessed sci=DARK calib=DARK'
                                          ' file, where dark is a telescope'
                                          ' dark')
pp_file.addset(pp_dark_dark_tel)

pp_dark_dark_sky = drs_finput('DARK_DARK_SKY', filetype='.fits',
                              suffix='_pp', intype=raw_dark_dark_sky,
                              inext='.fits', outclass=general_ofile,
                              hkeys=dict(KW_DPRTYPE='DARK_DARK_SKY'),
                              description='Preprocessed sci=DARK calib=DARK '
                                          'file, where dark is a sky dark')
pp_file.addset(pp_dark_dark_sky)

pp_dark_fp_sky = drs_finput('DARK_FP_SKY', filetype='.fits',
                            suffix='_pp', intype=raw_dark_fp_sky,
                            inext='.fits', outclass=general_ofile,
                            hkeys=dict(KW_DPRTYPE='DARK_FP_SKY'),
                            description='Preprocessed sci=DARK calib=FP file, '
                                        'where dark is an internal dark')
pp_file.addset(pp_dark_fp_sky)

# -----------------------------------------------------------------------------
# flat
pp_flat_dark = drs_finput('FLAT_DARK', filetype='.fits',
                          suffix='_pp', intype=raw_flat_dark,
                          inext='.fits', outclass=general_ofile,
                          hkeys=dict(KW_DPRTYPE='FLAT_DARK'),
                          description='Preprocessed sci=FLAT calib=DARK file,'
                                      ' where dark is an internal dark')
pp_file.addset(pp_flat_dark)

pp_dark_flat = drs_finput('DARK_FLAT', filetype='.fits',
                          suffix='_pp', intype=raw_dark_flat,
                          inext='.fits', outclass=general_ofile,
                          hkeys=dict(KW_DPRTYPE='DARK_FLAT'),
                          description='Preprocessed sci=DARK calib=FLAT file,'
                                      ' where dark is an internal dark')
pp_file.addset(pp_dark_flat)

pp_flat_flat = drs_finput('FLAT_FLAT', filetype='.fits',
                          suffix='_pp', intype=raw_flat_flat,
                          inext='.fits', outclass=general_ofile,
                          hkeys=dict(KW_DPRTYPE='FLAT_FLAT'),
                          description='Preprocessed sci=FLAT calib=FLAT file')
pp_file.addset(pp_flat_flat)

pp_flat_fp = drs_finput('FLAT_FP', filetype='.fits',
                        suffix='_pp', intype=raw_flat_fp,
                        inext='.fits', outclass=general_ofile,
                        hkeys=dict(KW_DPRTYPE='FLAT_FP'),
                        description='Preprocessed sci=FLAT calib=FP file')
pp_file.addset(pp_flat_fp)
# -----------------------------------------------------------------------------
# align
pp_dark_fp = drs_finput('DARK_FP', filetype='.fits',
                        suffix='_pp', intype=raw_dark_fp,
                        inext='.fits', outclass=general_ofile,
                        hkeys=dict(KW_DPRTYPE='DARK_FP'),
                        description='Preprocessed sci=DARK calib=FP file,'
                                    ' where dark is an internal dark')
pp_file.addset(pp_dark_fp)

pp_fp_dark = drs_finput('FP_DARK', filetype='.fits',
                        suffix='_pp', intype=raw_fp_dark,
                        inext='.fits', outclass=general_ofile,
                        hkeys=dict(KW_DPRTYPE='FP_DARK'),
                        description='Preprocessed sci=FP calib=DARK file, '
                                    ' where dark is an internal dark')
pp_file.addset(pp_fp_dark)

pp_fp_flat = drs_finput('FP_FLAT', filetype='.fits',
                        suffix='_pp', intype=raw_fp_flat,
                        inext='.fits', outclass=general_ofile,
                        hkeys=dict(KW_DPRTYPE='FP_FLAT'),
                        description='Preprocessed sci=FP calib=FLAT file')
pp_file.addset(pp_fp_flat)

pp_fp_fp = drs_finput('FP_FP', filetype='.fits',
                      suffix='_pp', intype=raw_fp_fp,
                      inext='.fits', outclass=general_ofile,
                      hkeys=dict(KW_DPRTYPE='FP_FP'),
                      description='Preprocessed sci=FP calib=FP file')
pp_file.addset(pp_fp_fp)

# -----------------------------------------------------------------------------
# LFC
pp_lfc_lfc = drs_finput('LFC_LFC', filetype='.fits', suffix='_pp',
                        intype=raw_lfc_lfc, inext='.fits',
                        outclass=general_ofile,
                        hkeys=dict(KW_DPRTYPE='LFC_LFC'),
                        description='Preprocessed sci=LFC calib=LFC file')
pp_file.addset(pp_lfc_lfc)

pp_lfc_fp = drs_finput('LFC_FP', hkeys=dict(KW_DPRTYPE='LFC_FP'),
                       filetype='.fits', suffix='_pp', intype=raw_lfc_fp,
                       inext='.fits', outclass=general_ofile,
                       description='Preprocessed sci=LFC calib=FP file')
pp_file.addset(pp_lfc_fp)

pp_fp_lfc = drs_finput('FP_LFC', hkeys=dict(KW_DPRTYPE='FP_LFC'),
                       filetype='.fits', suffix='_pp', intype=raw_fp_lfc,
                       inext='.fits', outclass=general_ofile,
                       description='Preprocessed sci=FP calib=LFC file')
pp_file.addset(pp_fp_lfc)

# -----------------------------------------------------------------------------
#  object
pp_obj_dark = drs_finput('OBJ_DARK', hkeys=dict(KW_DPRTYPE='OBJ_DARK'),
                         filetype='.fits',
                         suffix='_pp', intype=raw_obj_dark,
                         inext='.fits', outclass=general_ofile,
                         description='Preprocessed sci=OBJ calib=DARK file,'
                                     ' where dark is an internal dark')
pp_file.addset(pp_obj_dark)
pp_obj_fp = drs_finput('OBJ_FP', hkeys=dict(KW_DPRTYPE='OBJ_FP'),
                       filetype='.fits',
                       suffix='_pp', intype=raw_obj_fp,
                       inext='.fits', outclass=general_ofile,
                       description='Preprocessed sci=OBJ calib=FP file')
pp_file.addset(pp_obj_fp)

pp_obj_hc1 = drs_finput('OBJ_HCONE', hkeys=dict(KW_DPRTYPE='OBJ_HCONE'),
                        filetype='.fits',
                        suffix='_pp', intype=raw_obj_hc1,
                        inext='.fits', outclass=general_ofile,
                        description='Preprocessed sci=OBJ calib=Hollow Cathode '
                                    'file, Uranium Neon lamp')
pp_file.addset(pp_obj_hc1)

pp_obj_hc2 = drs_finput('OBJ_HCTWO', hkeys=dict(KW_DPRTYPE='OBJ_HCTWO'),
                        filetype='.fits',
                        suffix='_pp', intype=raw_obj_hc2,
                        inext='.fits', outclass=general_ofile,
                        description='Preprocessed sci=OBJ calib=Hollow Cathode '
                                    'file, Thorium Argon lamp')
pp_file.addset(pp_obj_hc2)

pp_polar_dark = drs_finput('POLAR_DARK', hkeys=dict(KW_DPRTYPE='POLAR_DARK'),
                           filetype='.fits',
                           suffix='_pp', intype=raw_polar_dark,
                           inext='.fits', outclass=general_ofile,
                           description='Preprocessed sci=POLAR calib=DARK,'
                                       ' where dark is an internal dark')
pp_file.addset(pp_polar_dark)

pp_polar_fp = drs_finput('POLAR_FP', hkeys=dict(KW_DPRTYPE='POLAR_FP'),
                         filetype='.fits',
                         suffix='_pp', intype=raw_polar_fp,
                         inext='.fits', outclass=general_ofile,
                         description='Preprocessed sci=POLAR calib=FP')
pp_file.addset(pp_polar_fp)


# define all science observations
science_pp = [pp_obj_dark, pp_obj_fp, pp_polar_dark, pp_polar_fp]
science_dprtypes = ['OBJ_DARK', 'OBJ_FP', 'POLAR_DARK', 'POLAR_FP']

# -----------------------------------------------------------------------------
#  comparison
pp_dark_hc1 = drs_finput('DARK_HCONE', hkeys=dict(KW_DPRTYPE='DARK_HCONE'),
                         filetype='.fits',
                         suffix='_pp', intype=raw_dark_hc1,
                         inext='.fits', outclass=general_ofile,
                         description='Preprocessed sci=DARK calib=Hollow '
                                     'Cathode file, where dark is an internal '
                                     'dark, Uranium Neon lamp')
pp_file.addset(pp_dark_hc1)

pp_dark_hc2 = drs_finput('DARK_HCTWO', hkeys=dict(KW_DPRTYPE='DARK_HCTWO'),
                         filetype='.fits',
                         suffix='_pp', intype=raw_dark_hc2,
                         inext='.fits', outclass=general_ofile,
                         description='Preprocessed sci=DARK calib=Hollow '
                                     ' Cathode file, where dark is an internal '
                                     'dark, Thorium Argon lamp')
pp_file.addset(pp_dark_hc2)

pp_fp_hc1 = drs_finput('FP_HCONE', hkeys=dict(KW_DPRTYPE='FP_HCONE'),
                       filetype='.fits',
                       suffix='_pp', intype=raw_fp_hc1,
                       inext='.fits', outclass=general_ofile,
                       description='Preprocessed sci=FP calib=Hollow Cathode '
                                   'file, Uranium Neon lamp')
pp_file.addset(pp_fp_hc1)

pp_fp_hc2 = drs_finput('FP_HCTWO', hkeys=dict(KW_DPRTYPE='FP_HCTWO'),
                       filetype='.fits',
                       suffix='_pp', intype=raw_fp_hc2,
                       inext='.fits', outclass=general_ofile,
                       description='Preprocessed sci=FP calib=Hollow Cathode '
                                   'file, Thorium Argon lamp')
pp_file.addset(pp_fp_hc2)

pp_hc1_fp = drs_finput('HCONE_FP', hkeys=dict(KW_DPRTYPE='HCONE_FP'),
                       filetype='.fits',
                       suffix='_pp', intype=raw_hc1_fp,
                       inext='.fits', outclass=general_ofile,
                       description='Preprocessed sci=Hollow Cathode calib=FP '
                                   'file, Uranium Neion lamp')
pp_file.addset(pp_hc1_fp)

pp_hc2_fp = drs_finput('HCTWO_FP', hkeys=dict(KW_DPRTYPE='HCTWO_FP'),
                       filetype='.fits',
                       suffix='_pp', intype=raw_hc2_fp,
                       inext='.fits', outclass=general_ofile,
                       description='Preprocessed sci=Hollow Cathode calib=FP '
                                   'file, Thorium Argon lamp')
pp_file.addset(pp_hc2_fp)

pp_hc1_hc1 = drs_finput('HCONE_HCONE', hkeys=dict(KW_DPRTYPE='HCONE_HCONE'),
                        filetype='.fits',
                        suffix='_pp', intype=raw_hc1_hc1,
                        inext='.fits', outclass=general_ofile,
                        description='Preprocessed sci=Hollow Cathode '
                                    'calib=Hollow Cathode file, Uranium Neon '
                                    'lamp')
pp_file.addset(pp_hc1_hc1)

pp_hc2_hc2 = drs_finput('HCTWO_HCTWO', hkeys=dict(KW_DPRTYPE='HCTWO_HCTWO'),
                        filetype='.fits',
                        suffix='_pp', intype=raw_hc2_hc2,
                        inext='.fits', outclass=general_ofile,
                        description='Preprocessed sci=Hollow Cathode '
                                    'calib=Hollow  Cathode file, Thorium '
                                    'Argon lamp')
pp_file.addset(pp_hc2_hc2)

pp_hc1_dark = drs_finput('HCONE_DARK', hkeys=dict(KW_DPRTYPE='HCONE_DARK'),
                         filetype='.fits',
                         suffix='_pp', intype=raw_hc1_dark,
                         inext='.fits', outclass=general_ofile,
                         description='Preprocessed sci=Hollow Cathode '
                                     'calib=DARK file, where dark is an '
                                     'internal dark, Uranium Neon lamp')
pp_file.addset(pp_hc1_dark)

pp_hc2_dark = drs_finput('HCTWO_DARK', hkeys=dict(KW_DPRTYPE='HCTWO_DARK'),
                         filetype='.fits',
                         suffix='_pp', intype=raw_hc2_dark,
                         inext='.fits', outclass=general_ofile,
                         description='Preprocessed sci=Hollow Cathode '
                                     'calib=DARK file, where dark is an '
                                     'internal dark, Thorium Argon lamp')
pp_file.addset(pp_hc2_dark)

# =============================================================================
# Reduced Files
# =============================================================================
# generic out file
red_file = drs_finput('DRS_OUTPUT', filetype='.fits', suffix='',
                      intype=pp_file, instrument=__INSTRUMENT__,
                      description='Generic reduced file')
# calib out file
calib_file = drs_finput('DRS_OUTPUT', filetype='.fits', suffix='',
                        intype=pp_file, instrument=__INSTRUMENT__,
                        description='Generic calibration file')
# telluric out file
tellu_file = drs_finput('DRS_OUTPUT', filetype='.fits', suffix='',
                        intype=pp_file, instrument=__INSTRUMENT__,
                        description='Generic telluric file')

# -----------------------------------------------------------------------------
# dark files
# -----------------------------------------------------------------------------
# dark out file
# out_dark = drs_finput('DARK', KW_OUTPUT='DARK',
#                       filetype='.fits', intype=pp_dark_dark,
#                       suffix='',
#                       outclass=calib_ofile,
#                       dbname='calibration', dbkey='DARK')

out_dark_int = drs_finput('DARKI', hkeys=dict(KW_OUTPUT='DARKI'),
                          filetype='.fits', intype=pp_dark_dark_int,
                          suffix='_darki',
                          outclass=calib_ofile,
                          dbname='calibration', dbkey='DARKI',
                          description='Internal dark calibration file')

out_dark_tel = drs_finput('DARKT', hkeys=dict(KW_OUTPUT='DARKT'),
                          filetype='.fits', intype=pp_dark_dark_tel,
                          suffix='_darkt',
                          outclass=calib_ofile,
                          dbname='calibration', dbkey='DARKT',
                          description='Telescope dark calibration file')

out_dark_sky = drs_finput('DARKS', hkeys=dict(KW_OUTPUT='DARKS'),
                          filetype='.fits', intype=pp_dark_dark_sky,
                          suffix='_darks',
                          outclass=calib_ofile,
                          dbname='calibration', dbkey='DARKS',
                          description='Sky dark calibration file')

out_dark_ref = drs_finput('DARKREF', hkeys=dict(KW_OUTPUT='DARKREF'),
                          filetype='.fits',
                          intype=[pp_dark_dark_tel, pp_dark_dark_int],
                          suffix='_dark_ref',
                          outclass=refcalib_ofile,
                          dbname='calibration', dbkey='DARKREF',
                          description='Reference dark calibration file')
# add dark outputs to output fileset
red_file.addset(out_dark_int)
red_file.addset(out_dark_tel)
red_file.addset(out_dark_sky)
red_file.addset(out_dark_ref)
calib_file.addset(out_dark_int)
calib_file.addset(out_dark_tel)
calib_file.addset(out_dark_sky)
calib_file.addset(out_dark_ref)

# -----------------------------------------------------------------------------
# Bad pixel / background files
# -----------------------------------------------------------------------------
# badpix out file
out_badpix = drs_finput('BADPIX', hkeys=dict(KW_OUTPUT='BADPIX'),
                        filetype='.fits',
                        intype=[pp_flat_flat],
                        suffix='_badpixel',
                        outclass=calib_ofile,
                        dbname='calibration', dbkey='BADPIX',
                        description='Bad pixel map')
out_backmap = drs_finput('BKGRD_MAP', hkeys=dict(KW_OUTPUT='BKGRD_MAP'),
                         intype=[pp_flat_flat],
                         suffix='_bmap.fits', outclass=calib_ofile,
                         dbname='calibration', dbkey='BKGRDMAP',
                         description='Bad pixel background map')

# background debug file
debug_back = drs_finput('DEBUG_BACK', hkeys=dict(KW_OUTPUT='DEBUG_BACK'),
                        filetype='.fits', intype=pp_file,
                        suffix='_background.fits', outclass=debug_ofile,
                        description='Individual file background map')

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
valid_lfibers = ['AB', 'C']
# localisation
out_loc_orderp = drs_finput('LOC_ORDERP', hkeys=dict(KW_OUTPUT='LOC_ORDERP'),
                            fibers=valid_lfibers,
                            filetype='.fits',
                            intype=[pp_flat_dark, pp_dark_flat],
                            suffix='_order_profile',
                            outclass=calib_ofile,
                            dbname='calibration', dbkey='ORDER_PROFILE',
                            description='Localisation: Order profile '
                                        'calibration file')
out_loc_loco = drs_finput('LOC_LOCO', hkeys=dict(KW_OUTPUT='LOC_LOCO'),
                          fibers=valid_lfibers,
                          filetype='.fits', intype=[pp_flat_dark, pp_dark_flat],
                          suffix='_loco',
                          outclass=calib_ofile,
                          dbname='calibration', dbkey='LOC',
                          description='Localisation: Position polynomial '
                                      'calibration file')
out_loc_fwhm = drs_finput('LOC_FWHM', hkeys=dict(KW_OUTPUT='LOC_FWHM'),
                          fibers=valid_lfibers,
                          filetype='.fits', intype=[pp_flat_dark, pp_dark_flat],
                          suffix='_fwhm-order',
                          outclass=calib_ofile,
                          description='Localisation: Width polynomial '
                                      'calibration file')
out_loc_sup = drs_finput('LOC_SUP', hkeys=dict(KW_OUTPUT='LOC_SUP'),
                         fibers=valid_lfibers,
                         filetype='.fits', intype=[pp_flat_dark, pp_dark_flat],
                         suffix='_with-order',
                         outclass=calib_ofile,
                         description='Localisation: Position superposition'
                                     'image calibration file')
# add localisation outputs to output fileset
red_file.addset(out_loc_orderp)
red_file.addset(out_loc_loco)
red_file.addset(out_loc_fwhm)
red_file.addset(out_loc_sup)
calib_file.addset(out_loc_orderp)
calib_file.addset(out_loc_loco)

# -----------------------------------------------------------------------------
# shape files (reference)
# -----------------------------------------------------------------------------
# shape reference
out_shape_dxmap = drs_finput('SHAPE_X', hkeys=dict(KW_OUTPUT='SHAPE_X'),
                             filetype='.fits', intype=pp_fp_fp,
                             suffix='_shapex', outclass=refcalib_ofile,
                             dbname='calibration', dbkey='SHAPEX',
                             description='Reference shape dx calibration file')
out_shape_dymap = drs_finput('SHAPE_Y', hkeys=dict(KW_OUTPUT='SHAPE_Y'),
                             filetype='.fits', intype=pp_fp_fp,
                             suffix='_shapey', outclass=refcalib_ofile,
                             dbname='calibration', dbkey='SHAPEY',
                             description='Reference shape dy calibration file')
out_shape_fpref = drs_finput('REF_FP', hkeys=dict(KW_OUTPUT='REF_FP'),
                             filetype='.fits', intype=pp_fp_fp,
                             suffix='_fpref', outclass=refcalib_ofile,
                             dbname='calibration', dbkey='FPREF',
                             description='Reference shape master FP '
                                         'calibration file')
out_shape_debug_ifp = drs_finput('SHAPE_IN_FP',
                                 hkeys=dict(KW_OUTPUT='SHAPE_IN_FP'),
                                 filetype='.fits', intype=pp_fp_fp,
                                 suffix='_shape_in_fp', outclass=debug_ofile,
                                 description='Input FP file for shape '
                                             'comparison')
out_shape_debug_ofp = drs_finput('SHAPE_OUT_FP',
                                 hkeys=dict(KW_OUTPUT='SHAPE_OUT_FP'),
                                 filetype='.fits', intype=pp_fp_fp,
                                 suffix='_shape_out_fp', outclass=debug_ofile,
                                 description='Output FP file for shape '
                                             'comparison')
out_shape_debug_ihc = drs_finput('SHAPE_IN_HC',
                                 hkeys=dict(KW_OUTPUT='SHAPE_IN_HC'),
                                 filetype='.fits', intype=pp_hc1_hc1,
                                 suffix='_shape_in_hc', outclass=debug_ofile,
                                 description='Input Hollow Cathode file for'
                                             'shape comparison')
out_shape_debug_ohc = drs_finput('SHAPE_OUT_HC',
                                 hkeys=dict(KW_OUTPUT='SHAPE_OUT_HC'),
                                 filetype='.fits', intype=pp_hc1_hc1,
                                 suffix='_shape_out_hc', outclass=debug_ofile,
                                 description='Output Hollow Cathode file for'
                                             'shape comparison')
out_shape_debug_bdx = drs_finput('SHAPE_BDX', hkeys=dict(KW_OUTPUT='SHAPE_BDX'),
                                 filetype='.fits', intype=pp_fp_fp,
                                 suffix='_shape_out_bdx', outclass=debug_ofile,
                                 description='Shape transformed dx comparison'
                                             ' file')
# add shape reference outputs to output fileset
red_file.addset(out_shape_dxmap)
red_file.addset(out_shape_dymap)
red_file.addset(out_shape_fpref)
red_file.addset(out_shape_debug_ifp)
red_file.addset(out_shape_debug_ofp)
red_file.addset(out_shape_debug_ihc)
red_file.addset(out_shape_debug_ohc)
red_file.addset(out_shape_debug_bdx)

calib_file.addset(out_shape_dxmap)
calib_file.addset(out_shape_dymap)
calib_file.addset(out_shape_fpref)

# valid ext fibers
valid_efibers = ['AB', 'A', 'B', 'C']
# -----------------------------------------------------------------------------
# shape files (per night)
# -----------------------------------------------------------------------------
# shape local
out_shape_local = drs_finput('SHAPEL', hkeys=dict(KW_OUTPUT='SHAPEL'),
                             filetype='.fits', intype=pp_fp_fp,
                             suffix='_shapel',
                             outclass=calib_ofile,
                             dbname='calibration', dbkey='SHAPEL',
                             description='Nightly shape calibration files')
out_shapel_debug_ifp = drs_finput('SHAPEL_IN_FP',
                                  hkeys=dict(KW_OUTPUT='SHAPEL_IN_FP'),
                                  filetype='.fits', intype=pp_fp_fp,
                                  suffix='_shapel_in_fp.fits',
                                  outclass=debug_ofile,
                                  description='Input FP file for nightly'
                                              ' shape comparison')

out_shapel_debug_ofp = drs_finput('SHAPEL_OUT_FP',
                                  hkeys=dict(KW_OUTPUT='SHAPEL_OUT_FP'),
                                  filetype='.fits', intype=pp_fp_fp,
                                  suffix='_shapel_out_fp.fits',
                                  outclass=debug_ofile,
                                  description='Output FP file for nightly'
                                              ' shape comparison')
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
                          fibers=valid_efibers, filetype='.fits',
                          intype=pp_flat_flat, suffix='_blaze',
                          dbname='calibration', dbkey='BLAZE',
                          outclass=calib_ofile,
                          description='Blaze calibration file')
out_ff_flat = drs_finput('FF_FLAT', hkeys=dict(KW_OUTPUT='FF_FLAT'),
                         fibers=valid_efibers, filetype='.fits',
                         intype=pp_flat_flat, suffix='_flat',
                         dbname='calibration', dbkey='FLAT',
                         outclass=calib_ofile,
                         description='Flat calibration file')

out_orderp_straight = drs_finput('ORDERP_STRAIGHT',
                                 hkeys=dict(KW_OUTPUT='ORDERP_STRAIGHT'),
                                 fibers=valid_efibers,
                                 filetype='.fits', intype=out_shape_local,
                                 suffix='_orderps',
                                 outclass=general_ofile,
                                 description='Straightened order profile for'
                                             ' an individual image')

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
                         suffix='_q2ds', outclass=general_ofile,
                         description='Extracted 2D spectrum (quick output)')

# extract E2DS with flat fielding
out_ql_e2dsff = drs_finput('QL_E2DS_FF', hkeys=dict(KW_OUTPUT='QL_E2DS_FF'),
                           fibers=valid_efibers,
                           filetype='.fits', intype=pp_file,
                           suffix='_q2dsff', outclass=general_ofile,
                           description='Extracted + flat-fielded 2D spectrum '
                                       '(quick output)')

# -----------------------------------------------------------------------------
# extract files
# -----------------------------------------------------------------------------
# extract E2DS without flat fielding
out_ext_e2ds = drs_finput('EXT_E2DS', hkeys=dict(KW_OUTPUT='EXT_E2DS'),
                          fibers=valid_efibers,
                          filetype='.fits', intype=pp_file,
                          suffix='_e2ds', outclass=general_ofile,
                          description='Extracted 2D spectrum')
# extract E2DS with flat fielding
out_ext_e2dsff = drs_finput('EXT_E2DS_FF', hkeys=dict(KW_OUTPUT='EXT_E2DS_FF'),
                            fibers=valid_efibers,
                            filetype='.fits', intype=pp_file,
                            suffix='_e2dsff', outclass=general_ofile,
                            s1d=['EXT_S1D_W', 'EXT_S1D_V'],
                            description='Extracted + flat-fielded 2D spectrum')
# pre-extract debug file
out_ext_e2dsll = drs_finput('EXT_E2DS_LL', hkeys=dict(KW_OUTPUT='EXT_E2DS_LL'),
                            fibers=valid_efibers,
                            filetype='.fits', intype=[pp_file, pp_flat_flat],
                            suffix='_e2dsll', outclass=debug_ofile,
                            description='Pre-extracted straighted stacked '
                                        'spectrum')
# extraction localisation file
out_ext_loco = drs_finput('EXT_LOCO', hkeys=dict(KW_OUTPUT='EXT_LOCO'),
                          fibers=valid_efibers,
                          filetype='.fits', intype=pp_file,
                          suffix='_e2dsloco', outclass=debug_ofile,
                          description='Straightened localisation file')
# extract s1d without flat fielding (constant in wavelength)
out_ext_s1d_w = drs_finput('EXT_S1D_W', hkeys=dict(KW_OUTPUT='EXT_S1D_W'),
                           fibers=valid_efibers,
                           filetype='.fits', intype=pp_file, datatype='table',
                           suffix='_s1d_w', outclass=general_ofile,
                           description='1D stitched spectrum '
                                       '(constant wavelength binning)')
# extract s1d without flat fielding (constant in velocity)
out_ext_s1d_v = drs_finput('EXT_S1D_V', hkeys=dict(KW_OUTPUT='EXT_S1D_V'),
                           fibers=valid_efibers,
                           filetype='.fits', intype=pp_file, datatype='table',
                           suffix='_s1d_v', outclass=general_ofile,
                           description='1D stitched spectrum '
                                       '(constant velocity binning)')

# fp line file from night
out_ext_fplines = drs_finput('EXT_FPLIST', hkeys=dict(KW_OUTPUT='EXT_FPLIST'),
                             fibers=valid_efibers,
                             filetype='.fits', remove_insuffix=True,
                             intype=[out_ext_e2ds, out_ext_e2dsff],
                             suffix='_ext_fplines',
                             outclass=general_ofile,
                             description='FP lines identified from extracted'
                                         ' FP fiber')

# add extract outputs to output fileset
red_file.addset(out_ext_e2ds)
red_file.addset(out_ext_e2dsff)
red_file.addset(out_ext_e2dsll)
red_file.addset(out_ext_loco)
red_file.addset(out_ext_s1d_w)
red_file.addset(out_ext_s1d_v)
red_file.addset(out_ext_fplines)

# -----------------------------------------------------------------------------
# thermal files
# -----------------------------------------------------------------------------
# thermal from internal dark
out_thermal_e2ds_int = drs_finput('THERMALI_E2DS',
                                  hkeys=dict(KW_OUTPUT='THERMALI_E2DS'),
                                  fibers=valid_efibers,
                                  filetype='.fits', intype=pp_dark_dark_int,
                                  suffix='_thermal_e2ds_int',
                                  dbname='calibration', dbkey='THERMALI',
                                  outclass=general_ofile,
                                  description='Extracted sci=DARK calib=DARK '
                                              'thermal calibration file, '
                                              'where dark is an internal dark')

# thermal from telescope dark
out_thermal_e2ds_tel = drs_finput('THERMALT_E2DS',
                                  hkeys=dict(KW_OUTPUT='THERMALT_E2DS'),
                                  fibers=valid_efibers,
                                  filetype='.fits', intype=pp_dark_dark_tel,
                                  suffix='_thermal_e2ds_tel',
                                  dbname='calibration', dbkey='THERMALT',
                                  outclass=general_ofile,
                                  description='Extracted sci=DARK calib=DARK '
                                              'thermal calibration file, '
                                              'where dark is a telescope dark')

# add thermal outputs to output fileset
red_file.addset(out_thermal_e2ds_int)
red_file.addset(out_thermal_e2ds_tel)
calib_file.addset(out_thermal_e2ds_int)
calib_file.addset(out_thermal_e2ds_tel)

# -----------------------------------------------------------------------------
# leakage files
# -----------------------------------------------------------------------------
# thermal from internal dark
out_leak_ref = drs_finput('LEAKREF_E2DS', hkeys=dict(KW_OUTPUT='LEAKREF_E2DS'),
                          fibers=valid_efibers,
                          filetype='.fits',
                          intype=[out_ext_e2ds, out_ext_e2dsff],
                          suffix='_leak_ref',
                          dbname='calibration', dbkey='LEAKREF',
                          outclass=refcalib_ofile,
                          description='Reference leak correction calibration '
                                      'file')
red_file.addset(out_leak_ref)
calib_file.addset(out_leak_ref)

# -----------------------------------------------------------------------------
# wave files (reference) ea
# -----------------------------------------------------------------------------
# wave solution using hc + fp
out_wavem_sol = drs_finput('WAVESOL_REF',
                           hkeys=dict(KW_OUTPUT='WAVESOL_REF'),
                           fibers=valid_efibers,
                           filetype='.fits',
                           intype=[out_ext_e2ds, out_ext_e2dsff],
                           suffix='_wavesol_ref',
                           dbname='calibration', dbkey='WAVESOL_REF',
                           outclass=refcalib_ofile,
                           description='Reference wavelength solution '
                                       'calibration file')

# hc line file from reference
out_wave_hclist_ref = drs_finput('WAVE_HCLIST_REF',
                                 hkeys=dict(KW_OUTPUT='WAVE_HCLIST_REF'),
                                 fibers=valid_efibers,
                                 filetype='.fits',
                                 intype=[out_ext_e2ds, out_ext_e2dsff],
                                 suffix='_waveref_hclines',
                                 dbname='calibration', dbkey='WAVEHCL',
                                 datatype='table',
                                 outclass=refcalib_ofile,
                                 description='Reference list of Hollow cathode'
                                             ' lines calibration file')

# fp line file from reference
out_wave_fplist_ref = drs_finput('WAVE_FPLIST_REF',
                                 hkeys=dict(KW_OUTPUT='WAVE_FPLIST_REF'),
                                 fibers=valid_efibers,
                                 filetype='.fits',
                                 intype=[out_ext_e2ds, out_ext_e2dsff],
                                 suffix='_waveref_fplines',
                                 dbname='calibration', dbkey='WAVEFPL',
                                 datatype='table',
                                 outclass=refcalib_ofile,
                                 description='Reference list of FP liens '
                                             'calibration file')

# teh cavity file polynomial file
out_waveref_cavity = drs_finput('WAVEREF_CAV',
                                hkeys=dict(KW_OUTPUT='WAVEREF_CAV'),
                                filetype='.fits',
                                fibers=['AB'],
                                intype=[out_ext_e2ds, out_ext_e2dsff],
                                suffix='_waveref_cav_',
                                dbname='calibration', dbkey='WAVECAV',
                                outclass=refcalib_ofile,
                                description='Reference wavelength cavity width'
                                            ' polynomial calibration file')

# the default wave reference
out_wave_default_ref = drs_finput('WAVESOL_DEFAULT',
                                  hkeys=dict(KW_OUTPUT='WAVESOL_DEFAULT'),
                                  fibers=valid_efibers,
                                  filetype='.fits',
                                  intype=[out_ext_e2ds, out_ext_e2dsff],
                                  suffix='_wave_d_ref',
                                  dbname='calibration', dbkey='WAVESOL_DEFAULT',
                                  outclass=refcalib_ofile,
                                  description='Default wavelength solution '
                                              'calibration file')

# add wave outputs to output fileset
red_file.addset(out_wavem_sol)
red_file.addset(out_wave_hclist_ref)
red_file.addset(out_wave_fplist_ref)
red_file.addset(out_waveref_cavity)
red_file.addset(out_wave_default_ref)
calib_file.addset(out_wavem_sol)
calib_file.addset(out_wave_hclist_ref)
calib_file.addset(out_wave_fplist_ref)
calib_file.addset(out_waveref_cavity)
calib_file.addset(out_wave_default_ref)

# -----------------------------------------------------------------------------
# wave files (reference) old
# -----------------------------------------------------------------------------
# resolution map
out_wavem_res = drs_finput('WAVERES', hkeys=dict(KW_OUTPUT='WAVE_RES'),
                           fibers=valid_efibers,
                           filetype='.fits',
                           intype=[out_ext_e2ds, out_ext_e2dsff],
                           suffix='_waveref_resmap',
                           outclass=refcalib_ofile,
                           description='Reference wavelength resolution map '
                                       'file')
# resolution e2ds file
out_wavem_res_e2ds = drs_finput('WAVEM_RES_E2DS',
                                hkeys=dict(KW_OUTPUT='WAVEM_RES_E2DS'),
                                fibers=valid_efibers,
                                filetype='.fits',
                                intype=[out_ext_e2ds, out_ext_e2dsff],
                                suffix='_waveref_res_e2ds',
                                dbname='calibration',
                                dbkey='WAVR_E2DS', outclass=refcalib_ofile,
                                description='Reference wavelength resolution '
                                            'e2ds file')

# fp global results table
out_wavem_res_table = drs_input('WAVE_FPRESTAB',
                                hkeys=dict(KW_OUTPUT='WAVE_FPRESTAB'),
                                fibers=valid_efibers,
                                filetype='.tbl',
                                intype=[out_ext_e2ds, out_ext_e2dsff],
                                outclass=set_ofile,
                                basename='apero_wave_results',
                                description='Reference wavelength resolution '
                                            'table')

# fp line list table
out_wavem_ll_table = drs_input('WAVE_FPLLTABL',
                               hkeys=dict(KW_OUTPUT='WAVE_FPLLTAB'),
                               fibers=valid_efibers,
                               filetype='.tbl',
                               intype=[out_ext_e2ds, out_ext_e2dsff],
                               suffix='_mhc_lines',
                               outclass=refcalib_ofile,
                               description='Reference wavelength FP line-list '
                                           'table')

# add wave outputs to output fileset
red_file.addset(out_wavem_res)
red_file.addset(out_wavem_res_table)
red_file.addset(out_wavem_ll_table)
red_file.addset(out_wavem_res_e2ds)
calib_file.addset(out_wavem_res_e2ds)

# -----------------------------------------------------------------------------
# wave files
# -----------------------------------------------------------------------------
# wave solution using night modifications
out_wave_night = drs_finput('WAVE_NIGHT', hkeys=dict(KW_OUTPUT='WAVE_NIGHT'),
                            fibers=valid_efibers, filetype='.fits',
                            intype=[out_ext_e2ds, out_ext_e2dsff],
                            suffix='_wave_night', dbname='calibration',
                            dbkey='WAVE', outclass=calib_ofile,
                            description='Nightly wavelength solution '
                                        'calibration file')

# hc initial linelist
out_wave_hcline = drs_input('WAVEHCLL', hkeys=dict(KW_OUTPUT='WAVEHCLL'),
                            fibers=valid_efibers, filetype='.dat',
                            intype=[out_ext_e2ds, out_ext_e2dsff],
                            suffix='_linelist', outclass=calib_ofile,
                            description='Nightly HC line list calibration '
                                        'file')

# hc resolution map
out_wave_hcres = drs_finput('WAVERES', hkeys=dict(KW_OUTPUT='WAVE_RES'),
                            fibers=valid_efibers, filetype='.fits',
                            intype=[out_ext_e2ds, out_ext_e2dsff],
                            suffix='_wave_res', outclass=calib_ofile,
                            description='Nightly wavelength resolution map '
                                        'file')

# fp global results table
out_wave_res_table = drs_input('WAVE_FPRESTAB',
                               hkeys=dict(KW_OUTPUT='WAVE_FPRESTAB'),
                               fibers=valid_efibers, filetype='.tbl',
                               intype=[out_ext_e2ds, out_ext_e2dsff],
                               outclass=set_ofile,
                               basename='apero_wave_results',
                               description='Nightly wavelength resolution'
                                           'table')

# fp line list table
out_wave_ll_table = drs_input('WAVE_FPLLTABL',
                              hkeys=dict(KW_OUTPUT='WAVE_FPLLTAB'),
                              fibers=valid_efibers, filetype='.tbl',
                              intype=[out_ext_e2ds, out_ext_e2dsff],
                              suffix='_hc_lines', outclass=calib_ofile,
                              description='Nightly wavelength FP line-list '
                                          'table')

# hc line file from night
out_wave_hclist = drs_finput('WAVE_HCLIST', hkeys=dict(KW_OUTPUT='WAVE_HCLIST'),
                             fibers=valid_efibers, filetype='.fits',
                             intype=[out_ext_e2ds, out_ext_e2dsff],
                             suffix='_wave_hclines', outclass=calib_ofile,
                             description='Nightly wavelength Hollow cathode'
                                         'line-list table')

# fp line file from night
out_wave_fplist = drs_finput('WAVE_FPLIST', hkeys=dict(KW_OUTPUT='WAVE_FPLIST'),
                             fibers=valid_efibers, filetype='.fits',
                             intype=[out_ext_e2ds, out_ext_e2dsff],
                             suffix='_wave_fplines', outclass=calib_ofile,
                             description='Nightly wavelength FP line-list '
                                         'calibration file')

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
valid_tfibers = ['AB', 'A', 'B']

# cleaned spectrum
out_sky_model = drs_finput('SKY_MODEL',
                           hkeys=dict(KW_OUTPUT='SKY_MODEL'),
                           filetype='.fits', intype=out_ext_e2dsff,
                           suffix='_sky_model', remove_insuffix=True,
                           dbname='telluric', dbkey='SKY_MODEL',
                           outclass=tellu_ofile,
                           description='Telluric sky model file')

# cleaned spectrum
out_tellu_sclean = drs_finput('TELLU_SCLEAN',
                              hkeys=dict(KW_OUTPUT='TELLU_SCLEAN'),
                              filetype='.fits', intype=out_ext_e2dsff,
                              suffix='_tellu_sclean.fits', outclass=debug_ofile,
                              description='Sky-cleaning file')

# cleaned spectrum
out_tellu_pclean = drs_finput('TELLU_PCLEAN',
                              hkeys=dict(KW_OUTPUT='TELLU_PCLEAN'),
                              fibers=valid_tfibers,
                              filetype='.fits', intype=out_ext_e2dsff,
                              suffix='_tellu_pclean', remove_insuffix=True,
                              dbname='telluric', dbkey='TELLU_PCLEAN',
                              outclass=tellu_ofile,
                              description='Telluric pre-cleaning file')

# convolved tapas map (with reference wave solution)
out_tellu_conv = drs_ninput('TELLU_CONV', hkeys=dict(KW_OUTPUT='TELLU_CONV'),
                            fibers=valid_tfibers,
                            filetype='.npy',
                            intype=[out_wavem_sol, out_wave_night,
                                    out_wave_default_ref],
                            suffix='_tellu_conv', remove_insuffix=True,
                            dbname='telluric', dbkey='TELLU_CONV',
                            outclass=tellu_ofile,
                            description='Telluric convolution file')

# tapas file in format for pre-cleaning
out_tellu_spl_npy = drs_ninput('TELLU_TAPAS', filetype='.npy',
                               basename='tapas_spl.npy',
                               dbname='telluric', dbkey='TELLU_TAPAS',
                               outclass=tellu_set_ofile,
                               description='Telluric TAPAS spline file')

# transmission map
out_tellu_trans = drs_finput('TELLU_TRANS', hkeys=dict(KW_OUTPUT='TELLU_TRANS'),
                             fibers=valid_tfibers,
                             filetype='.fits', intype=out_ext_e2dsff,
                             suffix='_tellu_trans', remove_insuffix=True,
                             dbname='telluric', dbkey='TELLU_TRANS',
                             outclass=tellu_ofile,
                             description='Telluric transmission file')

# transmission model
out_tellu_model = drs_finput('TRANS_MODEL', hkeys=dict(KW_OUTPUT='TRANS_MODEL'),
                             fibers=valid_tfibers, filetype='.fits',
                             basename='trans_model_{0}',  # add fiber manually
                             dbname='telluric', dbkey='TELLU_MODEL',
                             outclass=tellu_set_ofile,
                             description='Telluric transmission model file')

# add make_telluric outputs to output fileset
red_file.addset(out_sky_model)
red_file.addset(out_tellu_sclean)
red_file.addset(out_tellu_pclean)
red_file.addset(out_tellu_conv)
red_file.addset(out_tellu_trans)
red_file.addset(out_tellu_spl_npy)
red_file.addset(out_tellu_model)
tellu_file.addset(out_sky_model)
tellu_file.addset(out_tellu_sclean)
tellu_file.addset(out_tellu_pclean)
tellu_file.addset(out_tellu_conv)
tellu_file.addset(out_tellu_trans)
tellu_file.addset(out_tellu_spl_npy)
tellu_file.addset(out_tellu_model)

# -----------------------------------------------------------------------------
# fit telluric
# -----------------------------------------------------------------------------
# absorption files (npy file)
out_tellu_abso_npy = drs_ninput('ABSO_NPY', filetype='.npy',
                                basename='tellu_save.npy',
                                outclass=tellu_set_ofile,
                                description='Telluric absorption temporary '
                                            'file 1')
out_tellu_abso1_npy = drs_ninput('ABSO1_NPY', filetype='.npy',
                                 basename='tellu_save1.npy',
                                 outclass=tellu_set_ofile,
                                 description='Telluric absorption temporary '
                                             'file 2')

# telluric corrected e2ds spectrum
out_tellu_obj = drs_finput('TELLU_OBJ', hkeys=dict(KW_OUTPUT='TELLU_OBJ'),
                           fibers=valid_tfibers,
                           filetype='.fits', intype=out_ext_e2dsff,
                           suffix='_e2dsff_tcorr', remove_insuffix=True,
                           dbname='telluric', dbkey='TELLU_OBJ',
                           outclass=tellu_ofile,
                           s1d=['SC1D_W_FILE', 'SC1D_V_FILE'],
                           description='Telluric corrected extracted 2D '
                                       'spectrum')

# telluric corrected s1d spectrum
out_tellu_sc1d_w = drs_finput('SC1D_W_FILE',
                              hkeys=dict(KW_OUTPUT='SC1D_W_FILE'),
                              fibers=valid_tfibers,
                              filetype='.fits', intype=out_ext_e2dsff,
                              suffix='_s1d_w_tcorr', remove_insuffix=True,
                              outclass=tellu_ofile, datatype='table',
                              description='Telluric corrected extracted 1D '
                                          'spectrum (constant wavelength '
                                          'binning)')
out_tellu_sc1d_v = drs_finput('SC1D_V_FILE',
                              hkeys=dict(KW_OUTPUT='SC1D_V_FILE'),
                              fibers=valid_tfibers,
                              filetype='.fits', intype=out_ext_e2dsff,
                              suffix='_s1d_v_tcorr', remove_insuffix=True,
                              outclass=tellu_ofile, datatype='table',
                              description='Telluric corrected extracted 1D '
                                          'spectrum (constant velocity '
                                          'binning)')

# reconstructed telluric absorption file
out_tellu_recon = drs_finput('TELLU_RECON', hkeys=dict(KW_OUTPUT='TELLU_RECON'),
                             fibers=valid_tfibers,
                             filetype='.fits', intype=out_ext_e2dsff,
                             suffix='_e2dsff_recon', remove_insuffix=True,
                             dbname='telluric', dbkey='TELLU_RECON',
                             outclass=tellu_ofile,
                             s1d=['RC1D_W_FILE', 'RC1D_V_FILE'],
                             description='Telluric reconstructed 2D absorption '
                                         'file')

# reconstructed telluric 1d absorption
out_tellu_rc1d_w = drs_finput('RC1D_W_FILE',
                              hkeys=dict(KW_OUTPUT='RC1D_W_FILE'),
                              fibers=valid_tfibers,
                              filetype='.fits', intype=out_ext_e2dsff,
                              suffix='_s1d_w_recon', remove_insuffix=True,
                              outclass=tellu_ofile, datatype='table',
                              description='Telluric reconstructed 1D '
                                          'absorption file (constant '
                                          'wavelength binning)')
out_tellu_rc1d_v = drs_finput('RC1D_V_FILE',
                              hkeys=dict(KW_OUTPUT='RC1D_V_FILE'),
                              fibers=valid_tfibers,
                              filetype='.fits', intype=out_ext_e2dsff,
                              suffix='_s1d_v_recon', remove_insuffix=True,
                              outclass=tellu_ofile, datatype='table',
                              description='Telluric reconstructed 1D '
                                          'absorption file (constant '
                                          'velocity binning)')

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
                                fibers=valid_tfibers, filetype='.fits',
                                intype=[out_ext_e2dsff, out_tellu_obj],
                                basename='Template',
                                dbname='telluric', dbkey='TELLU_TEMP',
                                outclass=tellu_set_ofile,
                                description='Telluric 2D template file')

# template cube file (after shift)
out_tellu_bigcube = drs_finput('TELLU_BIGCUBE',
                               hkeys=dict(KW_OUTPUT='TELLU_BIGCUBE'),
                               fibers=valid_tfibers, filetype='.fits',
                               intype=[out_ext_e2dsff, out_tellu_obj],
                               basename='BigCube',
                               outclass=tellu_set_ofile,
                               description='Telluric object 2D stack file'
                                           ' (star frame)')

# template cube file (before shift)
out_tellu_bigcube0 = drs_finput('TELLU_BIGCUBE0',
                                hkeys=dict(KW_OUTPUT='TELLU_BIGCUBE0'),
                                fibers=valid_tfibers, filetype='.fits',
                                intype=[out_ext_e2dsff, out_tellu_obj],
                                basename='BigCube0',
                                outclass=tellu_set_ofile,
                                description='Telluric object  2D stack file'
                                            ' (Earth frame)')

# s1d template file (median) wavelength grid
out_tellu_s1dw_template = drs_finput('TELLU_TEMP_S1DW',
                                     hkeys=dict(KW_OUTPUT='TELLU_TEMP_S1DW'),
                                     fibers=valid_tfibers,
                                     filetype='.fits',
                                     intype=[out_ext_e2dsff, out_tellu_obj],
                                     basename='Template_s1dw', datatype='table',
                                     dbname='telluric', dbkey='TELLU_TEMP_S1DW',
                                     outclass=tellu_set_ofile,
                                     description='Telluric 1D template file')

# s1d template file (median) velocity grid
out_tellu_s1dv_template = drs_finput('TELLU_TEMP_S1DV',
                                     hkeys=dict(KW_OUTPUT='TELLU_TEMP_S1DV'),
                                     fibers=valid_tfibers,
                                     filetype='.fits',
                                     intype=[out_ext_e2dsff, out_tellu_obj],
                                     basename='Template_s1dv', datatype='table',
                                     dbname='telluric', dbkey='TELLU_TEMP_S1DV',
                                     outclass=tellu_set_ofile,
                                     description='Telluric 1D template file')

# s1d cibe file (after shift)
out_tellu_s1d_bigcube = drs_finput('TELLU_BIGCUBE_S1D',
                                   hkeys=dict(KW_OUTPUT='TELLU_BIGCUBE_S1D'),
                                   fibers=valid_tfibers,
                                   filetype='.fits',
                                   intype=[out_ext_e2dsff, out_tellu_obj],
                                   basename='BigCube_s1d',
                                   outclass=tellu_set_ofile,
                                   description='Telluric object 1D stack file'
                                               ' (Earth frame)')

# add make template outputs to output fileset
red_file.addset(out_tellu_template)
red_file.addset(out_tellu_bigcube)
red_file.addset(out_tellu_bigcube0)
red_file.addset(out_tellu_s1dw_template)
red_file.addset(out_tellu_s1dv_template)
red_file.addset(out_tellu_s1d_bigcube)
tellu_file.addset(out_tellu_template)
tellu_file.addset(out_tellu_s1dw_template)
tellu_file.addset(out_tellu_s1dv_template)

# -----------------------------------------------------------------------------
# ccf
# -----------------------------------------------------------------------------
# valid ccf_fibers
valid_ccf_fibers = ['AB', 'A', 'B', 'C']
# ccf out file
out_ccf_fits = drs_finput('CCF_RV', hkeys=dict(KW_OUTPUT='CCF_RV'),
                          fibers=valid_ccf_fibers,
                          filetype='.fits', suffix='_ccf',
                          intype=[out_ext_e2dsff, out_tellu_obj],
                          datatype='table', outclass=general_ofile,
                          description='Cross-correlation RV results file')

red_file.addset(out_ccf_fits)

# -----------------------------------------------------------------------------
# polarisation
# -----------------------------------------------------------------------------
# pol deg file
out_pol_deg = drs_finput('POL_DEG', hkeys=dict(KW_OUTPUT='POL_DEG'),
                         filetype='.fits', suffix='_pol',
                         intype=[out_ext_e2dsff, out_tellu_obj],
                         outclass=general_ofile,
                         description='Polarimetry 2D degree of polarisation '
                                     'file')

# pol calib file
out_pol_calib = drs_finput('POL_CALIB', hkeys=dict(KW_OUTPUT='POL_CALIB'),
                           filetype='.fits', datatype='table',
                           suffix='_pol_calib',
                           intype=[out_ext_e2dsff, out_tellu_obj],
                           outclass=general_ofile,
                           description='Polarimetry 2D shifted wavelength '
                                       'solution and blaze calibration file')

# stokes i file
out_pol_stokesi = drs_finput('STOKESI_POL',
                             hkeys=dict(KW_OUTPUT='STOKESI_POL'),
                             filetype='.fits',
                             suffix='_StokesI',
                             intype=[out_ext_e2dsff, out_tellu_obj],
                             outclass=general_ofile,
                             description='Polarimetry 2D stokes I '
                                         'polarisation file')

# null 1 file
out_pol_null1 = drs_finput('NULL_POL1', hkeys=dict(KW_OUTPUT='NULL_POL1'),
                           filetype='.fits', suffix='_null1_pol',
                           intype=[out_ext_e2dsff, out_tellu_obj],
                           outclass=general_ofile,
                           description='2D Null polarisation 1 file')

# null 2 file
out_pol_null2 = drs_finput('NULL_POL2', hkeys=dict(KW_OUTPUT='NULL_POL2'),
                           filetype='.fits', suffix='_null2_pol',
                           intype=[out_ext_e2dsff, out_tellu_obj],
                           outclass=general_ofile,
                           description='2D Null polarisation 2 file')

# lsd file
out_pol_lsd = drs_finput('LSD_POL', hkeys=dict(KW_OUTPUT='LSD_POL'),
                         filetype='.fits', suffix='_lsd_pol',
                         intype=[out_ext_e2dsff, out_tellu_obj],
                         outclass=general_ofile,
                         description='Least squares deconvolution file')

# pol s1d files
out_pol_s1dw = drs_finput('S1DW_POL', hkeys=dict(KW_OUTPUT='S1DW_POL'),
                          filetype='.fits',
                          suffix='_s1d_w_pol', remove_insuffix=True,
                          intype=[out_ext_e2dsff, out_tellu_obj],
                          outclass=general_ofile,
                          description='Polarimetry 2D degree of polarisation '
                                      'file (constant wavelength binning)')
out_pol_s1dv = drs_finput('S1DV_POL', hkeys=dict(KW_OUTPUT='S1DV_POL'),
                          filetype='.fits',
                          suffix='_s1d_v_pol', remove_insuffix=True,
                          intype=[out_ext_e2dsff, out_tellu_obj],
                          outclass=general_ofile,
                          description='Polarimetry 2D degree of polarisation '
                                      'file (constant velocity binning)')

# null1 s1d files
out_null1_s1dw = drs_finput('S1DW_NULL1', hkeys=dict(KW_OUTPUT='S1DW_NULL1'),
                            filetype='.fits',
                            suffix='_s1d_w_null1', remove_insuffix=True,
                            intype=[out_ext_e2dsff, out_tellu_obj],
                            outclass=general_ofile,
                            description='1D Null polarisation 1 file '
                                        '(constant wavelength binning)')
out_null1_s1dv = drs_finput('S1DV_NULL1', hkeys=dict(KW_OUTPUT='S1DV_NULL1'),
                            filetype='.fits',
                            suffix='_s1d_v_null1', remove_insuffix=True,
                            intype=[out_ext_e2dsff, out_tellu_obj],
                            outclass=general_ofile,
                            description='1D Null polarisation 1 file '
                                        '(constant velocity binning)')

# null2 s1d files
out_null2_s1dw = drs_finput('S1DW_NULL2', hkeys=dict(KW_OUTPUT='S1DW_NULL1'),
                            filetype='.fits',
                            suffix='_s1d_w_null2', remove_insuffix=True,
                            intype=[out_ext_e2dsff, out_tellu_obj],
                            outclass=general_ofile,
                            description='1D Null polarisation 2 file '
                                        '(constant wavelength binning)')
out_null2_s1dv = drs_finput('S1DV_NULL2', hkeys=dict(KW_OUTPUT='S1DV_NULL2'),
                            filetype='.fits',
                            suffix='_s1d_v_null2', remove_insuffix=True,
                            intype=[out_ext_e2dsff, out_tellu_obj],
                            outclass=general_ofile,
                            description='1D Null polarisation 2 file '
                                        '(constant velocity binning)')

# stokes I s1d files
out_stokesi_s1dw = drs_finput('S1DW_STOKESI',
                              hkeys=dict(KW_OUTPUT='S1DW_STOKESI'),
                              filetype='.fits',
                              suffix='_s1d_w_stokesi', remove_insuffix=True,
                              intype=[out_ext_e2dsff, out_tellu_obj],
                              outclass=general_ofile,
                              description='Polarimetry 1D stokes I '
                                          'polarisation file '
                                          '(constant wavelength binning)')
out_stokesi_s1dv = drs_finput('S1DV_STOKESI',
                              hkeys=dict(KW_OUTPUT='S1DV_STOKESI'),
                              filetype='.fits',
                              suffix='_s1d_v_stokesi', remove_insuffix=True,
                              intype=[out_ext_e2dsff, out_tellu_obj],
                              outclass=general_ofile,
                              description='Polarimetry 1D stokes I '
                                          'polarisation file '
                                          '(constant velocity binning)')

red_file.addset(out_pol_deg)
red_file.addset(out_pol_stokesi)
red_file.addset(out_pol_null1)
red_file.addset(out_pol_null2)
red_file.addset(out_pol_lsd)
red_file.addset(out_pol_s1dw)
red_file.addset(out_pol_s1dv)
red_file.addset(out_null1_s1dw)
red_file.addset(out_null1_s1dv)
red_file.addset(out_null2_s1dw)
red_file.addset(out_null2_s1dv)
red_file.addset(out_stokesi_s1dw)
red_file.addset(out_stokesi_s1dv)

# =============================================================================
# LBL processed Files
# =============================================================================
lbl_fibers = ['AB']

# lbl template file
lbl_template_file = drs_input('LBL_TEMPLATE', path='templates',
                              filetype='.fits',
                              basename='Template_s1dv_{obj}_sc1d_v_file_AB.fits',
                              datatype='table',
                              outclass=lbl_ofile,
                              description='Telluric 1D template file',
                              required=False)

# lbl mask file
lbl_mask_file = drs_input('LBL_MASK',
                          filetype='.fits', path='masks',
                          basename='{obj}', datatype='table',
                          outclass=lbl_ofile,
                          description='Telluric mask file')

# lbl fits files
lbl_fits_file = drs_finput('LBL_FITS', filetype='.fits',
                           path='lblrv/{obj}_{temp}/',
                           suffix='_{obj}_{temp}_lbl',
                           datatype='table',
                           outclass=lbl_ofile, instrument=__INSTRUMENT__,
                           description='LBL line list fits files')

# lbl rdb file
lbl_rdb_file = drs_input('LBL_RDB',
                         filetype='.rdb', path='lblrdb',
                         basename='lbl_{obj}_{temp}', datatype='table',
                         outclass=lbl_ofile,
                         description='LBL rdb file (RVs) in ascii-rdb format')

# lbl rdb fits file
lbl_rdb_fits_file = drs_input('LBL_RDB_FITS',
                              filetype='.fits', path='lblrdb',
                              basename='lbl_{obj}_{temp}', datatype='table',
                              outclass=lbl_ofile,
                              description='LBL rdb file (RVs) in fits format')

# lbl rdb2 file
lbl_rdb2_file = drs_input('LBL_RDB2',
                         filetype='.rdb', path='lblrdb',
                         basename='lbl2_{obj}_{temp}', datatype='table',
                         outclass=lbl_ofile,
                         description='LBL binned per night rdb file (RVs)')

# lbl drift file
lbl_drift_file = drs_input('LBL_DRIFT',
                           filetype='.rdb', path='lblrdb',
                           basename='drift',
                           datatype='table',
                           outclass=lbl_ofile,
                           description='LBL drift file (calculated from FPs)',
                           required=False)


# lbl rdb file with drift
lbl_rdb_drift_file = drs_input('LBL_RDB_DRIFT',
                               filetype='.rdb', path='lblrdb',
                               basename='lbl_{obj}_{temp}_drift',
                               datatype='table',
                               outclass=lbl_ofile,
                               description='LBL Drift corrected rdb file',
                               required=False)


# lbl rdb2 file with drift
lbl_rdb2_drift_file = drs_input('LBL_RDB2_DRIFT',
                               filetype='.rdb', path='lblrdb',
                               basename='lbl2_{obj}_{temp}_drift',
                               datatype='table',
                               outclass=lbl_ofile,
                               description='LBL Drift corrected binned '
                                           'rdb file',
                               required=False)


# =============================================================================
# Post processed Files
# =============================================================================
# generic post processed file
post_file = drs_oinput('DRS_POST', filetype='.fits', suffix='',
                       outclass=post_ofile, instrument=__INSTRUMENT__,
                       description='Generic post process file')

# define a list of wave outputs
wave_files = DrsFileGroup(name='WAVE_FILES',
                          files=[out_wavem_sol, out_wave_night,
                                 out_wave_default_ref])

# -----------------------------------------------------------------------------
# post processed 2D extraction file
# -----------------------------------------------------------------------------
post_e_file = drs_oinput('DRS_POST_E', filetype='.fits', suffix='e.fits',
                         outclass=post_ofile, inext='o', required=True,
                         description='Post process 2D extracted spectrum '
                                     'collection')

# add extensions
post_e_file.add_ext('PP', pp_file, pos=0, header_only=True, block_kind='tmp',
                    hkeys=dict(KW_DPRTYPE=['OBJ_FP', 'OBJ_DARK', 'POLAR_FP',
                                           'POLAR_DARK']),
                    remove_drs_hkeys=True)

post_e_file.add_ext('EXT_AB', out_ext_e2dsff, pos=1, fiber='AB', block_kind='red',
                    link='PP', hlink='KW_IDENTIFIER', clear_file=True,
                    tag='FluxAB')

post_e_file.add_ext('EXT_A', out_ext_e2dsff, pos=2, fiber='A', block_kind='red',
                    link='EXT_AB', hlink='KW_IDENTIFIER', clear_file=True,
                    tag='FluxA')

post_e_file.add_ext('EXT_B', out_ext_e2dsff, pos=3, fiber='B', block_kind='red',
                    link='EXT_AB', hlink='KW_IDENTIFIER', clear_file=True,
                    tag='FluxB')

post_e_file.add_ext('EXT_C', out_ext_e2dsff, pos=4, fiber='C', block_kind='red',
                    link='EXT_AB', hlink='KW_IDENTIFIER', clear_file=True,
                    tag='FluxC')

post_e_file.add_ext('WAVE_AB', wave_files, pos=5, fiber='AB', block_kind='red',
                    link='EXT_AB', hlink='CALIB::WAVE', tag='WaveAB')

post_e_file.add_ext('WAVE_A', wave_files, pos=6, fiber='A', block_kind='red',
                    link='EXT_A', hlink='CALIB::WAVE', tag='WaveA')

post_e_file.add_ext('WAVE_B', wave_files, pos=7, fiber='B', block_kind='red',
                    link='EXT_B', hlink='CALIB::WAVE', tag='WaveB')

post_e_file.add_ext('WAVE_C', wave_files, pos=8, fiber='C', block_kind='red',
                    link='EXT_C', hlink='CALIB::WAVE', tag='WaveC')

post_e_file.add_ext('BLAZE_AB', out_ff_blaze, pos=9, fiber='AB',
                    block_kind='red', link='EXT_AB', hlink='CALIB::BLAZE',
                    tag='BlazeAB')

post_e_file.add_ext('BLAZE_A', out_ff_blaze, pos=10, fiber='A',
                    block_kind='red', link='EXT_A', hlink='CALIB::BLAZE',
                    tag='BlazeA')

post_e_file.add_ext('BLAZE_B', out_ff_blaze, pos=11, fiber='B',
                    block_kind='red', link='EXT_B', hlink='CALIB::BLAZE',
                    tag='BlazeB')

post_e_file.add_ext('BLAZE_C', out_ff_blaze, pos=12, fiber='C',
                    block_kind='red', link='EXT_C', hlink='CALIB::BLAZE',
                    tag='BlazeC')

# move header keys
post_e_file.add_hkey('KW_VERSION', inheader='EXT_AB', outheader='PP')
post_e_file.add_hkey('KW_DRS_DATE_NOW', inheader='EXT_AB', outheader='PP')
# add to post processed file set
post_file.addset(post_e_file)

# -----------------------------------------------------------------------------
# post processed 1D extraction file
# -----------------------------------------------------------------------------
post_s_file = drs_oinput('DRS_POST_S', filetype='.fits', suffix='s.fits',
                         outclass=post_ofile, inext='o', required=True,
                         description='Post process 1D spectrum collection')
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
                       incol='wavelength', outcol='Wave', fiber='AB',
                       units='nm', block_kind='red', clear_file=True)

post_s_file.add_column('S1D_W', out_ext_s1d_w,
                       incol='flux', outcol='FluxAB', fiber='AB',
                       block_kind='red', clear_file=True)

post_s_file.add_column('S1D_W', out_ext_s1d_w,
                       incol='eflux', outcol='FluxErrAB', fiber='AB',
                       block_kind='red', clear_file=True)

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

post_s_file.add_column('S1D_W', out_ext_s1d_w,
                       incol='flux', outcol='FluxC', fiber='C',
                       block_kind='red', clear_file=True)

post_s_file.add_column('S1D_W', out_ext_s1d_w,
                       incol='eflux', outcol='FluxErrC', fiber='C',
                       block_kind='red', clear_file=True)

post_s_file.add_column('S1D_W', out_tellu_sc1d_w,
                       incol='flux', outcol='FluxABTelluCorrected', fiber='AB',
                       required=False, block_kind='red', clear_file=True)

post_s_file.add_column('S1D_W', out_tellu_sc1d_w,
                       incol='eflux', outcol='FluxErrABTelluCorrected',
                       fiber='AB', required=False,
                       block_kind='red', clear_file=True)

post_s_file.add_column('S1D_W', out_tellu_sc1d_w,
                       incol='flux', outcol='FluxATelluCorrected', fiber='A',
                       required=False, block_kind='red', clear_file=True)

post_s_file.add_column('S1D_W', out_tellu_sc1d_w,
                       incol='eflux', outcol='FluxErrATelluCorrected',
                       fiber='A', required=False,
                       block_kind='red', clear_file=True)

post_s_file.add_column('S1D_W', out_tellu_sc1d_w,
                       incol='flux', outcol='FluxBTelluCorrected', fiber='B',
                       required=False, block_kind='red', clear_file=True)

post_s_file.add_column('S1D_W', out_tellu_sc1d_w,
                       incol='eflux', outcol='FluxErrBTelluCorrected',
                       fiber='B', required=False,
                       block_kind='red', clear_file=True)

post_s_file.add_column('S1D_W', out_tellu_rc1d_w, fiber='AB',
                       incol='flux', outcol='Recon',
                       required=False, block_kind='red', clear_file=True)

post_s_file.add_column('S1D_W', out_tellu_rc1d_w, fiber='AB',
                       incol='eflux', outcol='ReconErr',
                       required=False, block_kind='red', clear_file=True)

# s1d w is a composite table
post_s_file.add_ext('S1D_V', 'table', pos=2, block_kind='red',
                    link='PP', hlink='KW_IDENTIFIER',
                    extname='UniformVelocity', tag='UniformVelocity')

# add s1d w columns (all linked via PP file)
post_s_file.add_column('S1D_V', out_ext_s1d_v,
                       incol='wavelength', outcol='Wave', fiber='AB',
                       units='nm', block_kind='red', clear_file=True)

post_s_file.add_column('S1D_V', out_ext_s1d_v,
                       incol='flux', outcol='FluxAB', fiber='AB',
                       block_kind='red', clear_file=True)

post_s_file.add_column('S1D_V', out_ext_s1d_v,
                       incol='eflux', outcol='FluxErrAB', fiber='AB',
                       block_kind='red', clear_file=True)

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

post_s_file.add_column('S1D_V', out_ext_s1d_v,
                       incol='flux', outcol='FluxC', fiber='C',
                       block_kind='red', clear_file=True)

post_s_file.add_column('S1D_V', out_ext_s1d_v,
                       incol='eflux', outcol='FluxErrC', fiber='C',
                       block_kind='red', clear_file=True)

# TODO: from telluric database?
post_s_file.add_column('S1D_V', out_tellu_sc1d_v,
                       incol='flux', outcol='FluxABTelluCorrected', fiber='AB',
                       required=False, block_kind='red', clear_file=True)

# TODO: from telluric database?
post_s_file.add_column('S1D_V', out_tellu_sc1d_v,
                       incol='eflux', outcol='FluxErrABTelluCorrected',
                       fiber='AB', required=False,
                       block_kind='red', clear_file=True)

# TODO: from telluric database?
post_s_file.add_column('S1D_V', out_tellu_sc1d_v,
                       incol='flux', outcol='FluxATelluCorrected', fiber='A',
                       required=False, block_kind='red', clear_file=True)
# TODO: from telluric database?
post_s_file.add_column('S1D_V', out_tellu_sc1d_v,
                       incol='eflux', outcol='FluxErrATelluCorrected',
                       fiber='A', required=False,
                       block_kind='red', clear_file=True)
# TODO: from telluric database?
post_s_file.add_column('S1D_V', out_tellu_sc1d_v,
                       incol='flux', outcol='FluxBTelluCorrected', fiber='B',
                       required=False, block_kind='red', clear_file=True)
# TODO: from telluric database?
post_s_file.add_column('S1D_V', out_tellu_sc1d_v,
                       incol='eflux', outcol='FluxErrBTelluCorrected',
                       fiber='B', required=False,
                       block_kind='red', clear_file=True)
# TODO: from telluric database?
post_s_file.add_column('S1D_V', out_tellu_rc1d_v, fiber='AB',
                       incol='flux', outcol='Recon',
                       required=False, block_kind='red', clear_file=True)
# TODO: from telluric database?
post_s_file.add_column('S1D_V', out_tellu_rc1d_v, fiber='AB',
                       incol='eflux', outcol='ReconErr',
                       required=False, block_kind='red', clear_file=True)

# move header keys
post_s_file.add_hkey('KW_VERSION', inheader='S1D_W', outheader='PP')
post_s_file.add_hkey('KW_DRS_DATE_NOW', inheader='S1D_W', outheader='PP')
# add to post processed file set
post_file.addset(post_s_file)

# -----------------------------------------------------------------------------
# post processed telluric file
# -----------------------------------------------------------------------------
post_t_file = drs_oinput('DRS_POST_T', filetype='.fits', suffix='t.fits',
                         outclass=post_ofile, inext='o', required=False,
                         description='Post process 2D telluric corrected '
                                     'collection')
# add extensions
post_t_file.add_ext('PP', pp_file, pos=0, header_only=True, block_kind='tmp',
                    hkeys=dict(KW_DPRTYPE=['OBJ_FP', 'OBJ_DARK', 'POLAR_FP',
                                           'POLAR_DARK']),
                    remove_drs_hkeys=True)
post_t_file.add_ext('TELLU_AB', out_tellu_obj, pos=1, fiber='AB',
                    link='PP', hlink='KW_IDENTIFIER', block_kind='red',
                    clear_file=True, tag='FluxAB')

post_t_file.add_ext('WAVE_AB', wave_files, pos=2, fiber='AB',
                    link='TELLU_AB', hlink='CALIB::WAVE', block_kind='red',
                    clear_file=True, tag='WaveAB')

post_t_file.add_ext('BLAZE_AB', out_ff_blaze, pos=3, fiber='AB',
                    link='TELLU_AB', hlink='CALIB::BLAZE', block_kind='red',
                    clear_file=True, tag='BlazeAB')

post_t_file.add_ext('RECON_AB', out_tellu_recon, pos=4, fiber='AB',
                    link='TELLU_AB', hlink='KW_IDENTIFIER',
                    block_kind='red', clear_file=True, tag='Recon')

post_t_file.add_ext('OHLINE', out_tellu_pclean, pos=5, fiber='AB',
                    link='TELLU_AB', hlink='KW_IDENTIFIER',
                    block_kind='red', clear_file=True, tag='OHLine',
                    extname='PCA_SKY')

post_t_file.add_ext('TELLU_A', out_tellu_obj, pos=6, fiber='A',
                    link='PP', hlink='KW_IDENTIFIER', block_kind='red',
                    clear_file=True, tag='FluxA')

post_t_file.add_ext('WAVE_A', wave_files, pos=7, fiber='A',
                    link='TELLU_A', hlink='CALIB::WAVE', block_kind='red',
                    clear_file=True, tag='WaveA')

post_t_file.add_ext('BLAZE_A', out_ff_blaze, pos=8, fiber='A',
                    link='TELLU_A', hlink='CALIB::BLAZE', block_kind='red',
                    clear_file=True, tag='BlazeA')

post_t_file.add_ext('TELLU_B', out_tellu_obj, pos=9, fiber='B',
                    link='PP', hlink='KW_IDENTIFIER', block_kind='red',
                    clear_file=True, tag='FluxB')

post_t_file.add_ext('WAVE_B', wave_files, pos=10, fiber='B',
                    link='TELLU_B', hlink='CALIB::WAVE', block_kind='red',
                    clear_file=True, tag='WaveB')

post_t_file.add_ext('BLAZE_B', out_ff_blaze, pos=11, fiber='B',
                    link='TELLU_B', hlink='CALIB::BLAZE', block_kind='red',
                    clear_file=True, tag='BlazeB')

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
                         outclass=post_ofile, inext='o', required=False,
                         description='Post process radial velocity collection')
post_v_file.add_ext('PP', pp_file, pos=0, header_only=True, block_kind='tmp',
                    hkeys=dict(KW_DPRTYPE=['OBJ_FP', 'OBJ_DARK', 'POLAR_FP',
                                           'POLAR_DARK']),
                    clear_file=True, remove_drs_hkeys=True)

post_v_file.add_ext('VEL', out_ccf_fits, pos=1, fiber='AB',
                    link='PP', hlink='KW_IDENTIFIER', block_kind='red',
                    clear_file=True, tag='CCF')
# move header keys
post_v_file.add_hkey('KW_VERSION', inheader='VEL', outheader='PP')
post_v_file.add_hkey('KW_DRS_DATE_NOW', inheader='VEL', outheader='PP')

# add to post processed file set
post_file.addset(post_v_file)

# -----------------------------------------------------------------------------
# post processed polar file
# -----------------------------------------------------------------------------
# Not always required (i.e. for hot stars)
post_p_file = drs_oinput('DRS_POST_P', filetype='.fits', suffix='p.fits',
                         outclass=post_ofile, inext='o', required=False,
                         exclude_keys=dict(KW_DRS_MODE=['SPECTROSCOPY',
                                                        'Unknown']),
                         description='Post process polarimetry collection')

# add extensions
post_p_file.add_ext('PP', pp_file, pos=0, header_only=True, block_kind='tmp',
                    hkeys=dict(KW_DPRTYPE=['POLAR_FP', 'POLAR_DARK']),
                    clear_file=True, remove_drs_hkeys=True)
post_p_file.add_ext('POL', out_pol_deg, pos=1, block_kind='red',
                    link='PP', hlink='KW_IDENTIFIER', clear_file=True,
                    tag='Pol', extname='POL_DEG')
post_p_file.add_ext('POLERR', out_pol_deg, pos=2, block_kind='red',
                    link='PP', hlink='KW_IDENTIFIER', clear_file=True,
                    tag='PolErr', extname='POL_ERR')
post_p_file.add_ext('STOKESI', out_pol_stokesi, pos=3, block_kind='red',
                    link='PP', hlink='KW_IDENTIFIER', clear_file=True,
                    tag='StokesI', extname='STOKESI_POL')
post_p_file.add_ext('STOKESIERR', out_pol_stokesi, pos=4, block_kind='red',
                    link='PP', hlink='KW_IDENTIFIER', clear_file=True,
                    tag='StokesIErr', extname='STOKESI_ERR')
post_p_file.add_ext('NULL1', out_pol_null1, pos=5, block_kind='red',
                    link='PP', hlink='KW_IDENTIFIER', clear_file=True,
                    tag='Null1', extname='NULL_POL1')
post_p_file.add_ext('NULL2', out_pol_null2, pos=6, block_kind='red',
                    link='PP', hlink='KW_IDENTIFIER', clear_file=True,
                    tag='Null2', extname='NULL_POL2')
post_p_file.add_ext('WAVE_AB', out_pol_calib, pos=7,
                    block_kind='red', link='PP', hlink='KW_IDENTIFIER',
                    tag='WaveAB', extname='POL_WAVE', datatype='image',
                    hdr_extname='POL_WAVE')
post_p_file.add_ext('BLAZE_AB', out_pol_calib, pos=8,
                    block_kind='red', link='PP', hlink='KW_IDENTIFIER',
                    tag='BlazeAB', extname='POL_BLAZE', datatype='image',
                    hdr_extname='POL_BLAZE')
# s1d w table
post_p_file.add_ext('S1D_W', 'table', pos=9, block_kind='red',
                    link='PP', hlink='KW_IDENTIFIER',
                    extname='UniformWavelength', tag='UniformWavelength')
# add s1d w columns (all linked via PP file)
post_p_file.add_column('S1D_W', out_pol_s1dw,
                       incol='wavelength', outcol='Wave', fiber='None',
                       units='nm', block_kind='red', clear_file=True)
post_p_file.add_column('S1D_W', out_pol_s1dw,
                       incol='flux', outcol='FluxPol', fiber='None',
                       block_kind='red', clear_file=True)
post_p_file.add_column('S1D_W', out_pol_s1dw,
                       incol='eflux', outcol='FluxErrPol', fiber='None',
                       block_kind='red', clear_file=True)
post_p_file.add_column('S1D_W', out_stokesi_s1dw,
                       incol='flux', outcol='FluxStokesI', fiber='None',
                       block_kind='red', clear_file=True)
post_p_file.add_column('S1D_W', out_stokesi_s1dw,
                       incol='eflux', outcol='FluxErrStokesI', fiber='None',
                       block_kind='red', clear_file=True)
post_p_file.add_column('S1D_W', out_null1_s1dw,
                       incol='flux', outcol='FluxNull1', fiber='None',
                       block_kind='red', clear_file=True)
post_p_file.add_column('S1D_W', out_null1_s1dw,
                       incol='eflux', outcol='FluxErrNull1', fiber='None',
                       block_kind='red', clear_file=True)
post_p_file.add_column('S1D_W', out_null2_s1dw,
                       incol='flux', outcol='FluxNull2', fiber='None',
                       block_kind='red', clear_file=True)
post_p_file.add_column('S1D_W', out_null2_s1dw,
                       incol='eflux', outcol='FluxErrNull2', fiber='None',
                       block_kind='red', clear_file=True)
# s1d v table
post_p_file.add_ext('S1D_V', 'table', pos=10, block_kind='red',
                    link='PP', hlink='KW_IDENTIFIER',
                    extname='UniformVelocity', tag='UniformVelocity')
# add s1d w columns (all linked via PP file)
post_p_file.add_column('S1D_V', out_pol_s1dv,
                       incol='wavelength', outcol='Wave', fiber='None',
                       units='nm', block_kind='red', clear_file=True)
post_p_file.add_column('S1D_V', out_pol_s1dv,
                       incol='flux', outcol='FluxPol', fiber='None',
                       block_kind='red', clear_file=True)
post_p_file.add_column('S1D_V', out_pol_s1dv,
                       incol='eflux', outcol='FluxErrPol', fiber='None',
                       block_kind='red', clear_file=True)
post_p_file.add_column('S1D_V', out_stokesi_s1dv,
                       incol='flux', outcol='FluxStokesI', fiber='None',
                       block_kind='red', clear_file=True)
post_p_file.add_column('S1D_V', out_stokesi_s1dv,
                       incol='eflux', outcol='FluxErrStokesI', fiber='None',
                       block_kind='red', clear_file=True)
post_p_file.add_column('S1D_V', out_null1_s1dv,
                       incol='flux', outcol='FluxNull1', fiber='None',
                       block_kind='red', clear_file=True)
post_p_file.add_column('S1D_V', out_null1_s1dv,
                       incol='eflux', outcol='FluxErrNull1', fiber='None',
                       block_kind='red', clear_file=True)
post_p_file.add_column('S1D_V', out_null2_s1dv,
                       incol='flux', outcol='FluxNull2', fiber='None',
                       block_kind='red', clear_file=True)
post_p_file.add_column('S1D_V', out_null2_s1dv,
                       incol='eflux', outcol='FluxErrNull2', fiber='None',
                       block_kind='red', clear_file=True)
# add the polar input combine table
post_p_file.add_ext('POLTABLE', out_pol_deg, pos=11, block_kind='red',
                    link='PP', hlink='KW_IDENTIFIER', clear_file=True,
                    tag='PolTable', extname='POL_TABLE', datatype='table')
# move header keys
post_p_file.add_hkey('KW_VERSION', inheader='POL', outheader='PP')
post_p_file.add_hkey('KW_DRS_DATE_NOW', inheader='POL', outheader='PP')

# add to post processed file set
post_file.addset(post_p_file)

# =============================================================================
# Other Files
# =============================================================================
_params = constants.load()
ccf_path = os.path.join(_params['DRS_DATA_ASSETS'],
                        _params['WAVE_CCF_MASK_PATH'])
# special case where input file may not be in default path directory
other_ccf_mask_file = drs_input('CCF_MASK', filetype='.mas',
                                description='CCF mask file',
                                inpath=ccf_path)

# =============================================================================
# End of code
# =============================================================================
