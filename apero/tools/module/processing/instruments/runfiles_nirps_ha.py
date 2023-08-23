#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2022-06-06

@author: cook
"""
from typing import List

from apero.base import base
from apero.core import constants
from apero.tools.module.processing import drs_run_ini

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'instruments.runfiles_nirps_ha.ini.py'
__INSTRUMENT__ = 'NIRPS_HA'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get the run file class
RunIniFile = drs_run_ini.RunIniFile
# get parameter dictionary class
ParamDict = constants.ParamDict
# Define the default reference observation directory
DEFAULT_REF_OBSDIR = drs_run_ini.DEFAULT_REF_OBSDIR[__INSTRUMENT__]


# =============================================================================
# Define functions
# =============================================================================
def get_runfiles(params: ParamDict) -> List[RunIniFile]:
    """
    Defines all possible run files

    :param params: ParamDict, parameter dictionary of constants

    :return: list of RunIniFile instances
    """
    # storage list
    run_files = []
    # -------------------------------------------------------------------------
    # create default runs files for nirps_ha
    # -------------------------------------------------------------------------
    # blank run
    blank_run_nirps_ha = RunIniFile(params, 'NIRPS_HA', 'blank_run')
    blank_run_nirps_ha.append_sequence('blank_seq')
    run_files.append(blank_run_nirps_ha)
    # mini run
    mini_run_nirps_ha = RunIniFile(params, 'NIRPS_HA', 'mini_run')
    mini_run_nirps_ha.append_sequence('limited_seq')
    mini_run_nirps_ha.modify('SKIP_LBLREF', False)
    mini_run_nirps_ha.modify('SKIP_LBLMASK_SCI', False)
    mini_run_nirps_ha.modify('SKIP_LBLCOMPUTE_SCI', False)
    mini_run_nirps_ha.modify('SKIP_LBLCOMPILE_SCI', False)
    run_files.append(mini_run_nirps_ha)
    # quick run
    quick_run_nirps_ha = RunIniFile(params, 'NIRPS_HA', 'quick_run')
    quick_run_nirps_ha.append_sequence('pp_seq_opt')
    quick_run_nirps_ha.append_sequence('quick_seq')
    quick_run_nirps_ha.modify('RUN_PP_CAL', False)
    quick_run_nirps_ha.modify('RUN_PP_TEL', False)
    quick_run_nirps_ha.modify('RUN_PP_HC1HC1', False)
    quick_run_nirps_ha.modify('RUN_PP_FPFP', False)
    quick_run_nirps_ha.modify('RUN_PP_FF', False)
    quick_run_nirps_ha.modify('RUN_PP_DFP', False)
    quick_run_nirps_ha.modify('RUN_PP_SKY', False)
    quick_run_nirps_ha.modify('RUN_PP_LFC', False)
    quick_run_nirps_ha.modify('RUN_PP_LFCFP', False)
    quick_run_nirps_ha.modify('RUN_PP_FPLFC', False)
    run_files.append(quick_run_nirps_ha)
    # calib run
    calib_run_nirps_ha = RunIniFile(params, 'NIRPS_HA', 'calib_run')
    calib_run_nirps_ha.append_sequence('pp_seq_opt')
    calib_run_nirps_ha.append_sequence('calib_seq')
    calib_run_nirps_ha.modify('RUN_PP_SCI', False)
    calib_run_nirps_ha.modify('RUN_PP_TEL', False)
    calib_run_nirps_ha.modify('RUN_PP_HC1HC1', False)
    calib_run_nirps_ha.modify('RUN_PP_FPFP', False)
    calib_run_nirps_ha.modify('RUN_PP_FF', False)
    calib_run_nirps_ha.modify('RUN_PP_DFP', False)
    calib_run_nirps_ha.modify('RUN_PP_SKY', False)
    calib_run_nirps_ha.modify('RUN_PP_LFC', False)
    calib_run_nirps_ha.modify('RUN_PP_LFCFP', False)
    calib_run_nirps_ha.modify('RUN_PP_FPLFC', False)
    run_files.append(calib_run_nirps_ha)
    # complete run
    complete_run_nirps_ha = RunIniFile(params, 'NIRPS_HA', 'complete_run')
    complete_run_nirps_ha.append_sequence('full_seq')
    run_files.append(complete_run_nirps_ha)
    # reference calib run
    mcalib_run_nirps_ha = RunIniFile(params, 'NIRPS_HA', 'ref_calib_run')
    mcalib_run_nirps_ha.append_sequence('pp_seq_opt')
    mcalib_run_nirps_ha.append_sequence('ref_seq')
    mcalib_run_nirps_ha.modify('RUN_PP_SCI', False)
    mcalib_run_nirps_ha.modify('RUN_PP_TEL', False)
    mcalib_run_nirps_ha.modify('RUN_PP_HC1HC1', False)
    mcalib_run_nirps_ha.modify('RUN_PP_FPFP', False)
    mcalib_run_nirps_ha.modify('RUN_PP_FF', False)
    mcalib_run_nirps_ha.modify('RUN_PP_DFP', False)
    mcalib_run_nirps_ha.modify('RUN_PP_SKY', False)
    mcalib_run_nirps_ha.modify('RUN_PP_LFC', False)
    mcalib_run_nirps_ha.modify('RUN_PP_LFCFP', False)
    mcalib_run_nirps_ha.modify('RUN_PP_FPLFC', False)
    run_files.append(mcalib_run_nirps_ha)
    # other run
    other_run_nirps_ha = RunIniFile(params, 'NIRPS_HA', 'other_run')
    other_run_nirps_ha.append_sequence('pp_seq_opt')
    other_run_nirps_ha.append_sequence('eng_seq')
    other_run_nirps_ha.run_default = False
    run_files.append(other_run_nirps_ha)
    # science run
    science_run_nirps_ha = RunIniFile(params, 'NIRPS_HA', 'science_run')
    science_run_nirps_ha.append_sequence('pp_seq_opt')
    science_run_nirps_ha.append_sequence('science_seq')
    science_run_nirps_ha.modify('RUN_PP_CAL', False)
    science_run_nirps_ha.modify('RUN_PP_TEL', False)
    science_run_nirps_ha.modify('RUN_PP_HC1HC1', False)
    science_run_nirps_ha.modify('RUN_PP_FPFP', False)
    science_run_nirps_ha.modify('RUN_PP_FF', False)
    science_run_nirps_ha.modify('RUN_PP_DFP', False)
    science_run_nirps_ha.modify('RUN_PP_SKY', False)
    science_run_nirps_ha.modify('RUN_PP_LFC', False)
    science_run_nirps_ha.modify('RUN_PP_LFCFP', False)
    science_run_nirps_ha.modify('RUN_PP_FPLFC', False)
    science_run_nirps_ha.modify('RECAL_TEMPLATES', False)
    run_files.append(science_run_nirps_ha)
    # tellu run
    tellu_run_nirps_ha = RunIniFile(params, 'NIRPS_HA', 'tellu_run')
    tellu_run_nirps_ha.append_sequence('pp_seq_opt')
    tellu_run_nirps_ha.append_sequence('science_seq')
    tellu_run_nirps_ha.modify('RUN_PP_CAL', False)
    tellu_run_nirps_ha.modify('RUN_PP_SCI', False)
    tellu_run_nirps_ha.modify('RUN_PP_HC1HC1', False)
    tellu_run_nirps_ha.modify('RUN_PP_FPFP', False)
    tellu_run_nirps_ha.modify('RUN_PP_FF', False)
    tellu_run_nirps_ha.modify('RUN_PP_DFP', False)
    tellu_run_nirps_ha.modify('RUN_PP_SKY', False)
    tellu_run_nirps_ha.modify('RUN_PP_LFC', False)
    tellu_run_nirps_ha.modify('RUN_PP_LFCFP', False)
    tellu_run_nirps_ha.modify('RUN_PP_FPLFC', False)
    run_files.append(tellu_run_nirps_ha)
    # test run
    test_run_nirps_ha = RunIniFile(params, 'NIRPS_HA', 'test_run')
    test_run_nirps_ha.append_sequence('limited_seq')
    test_run_nirps_ha.run_default = False
    test_run_nirps_ha.modify('TEST_RUN', True)
    run_files.append(test_run_nirps_ha)
    # helios run
    helios_nirps_ha = RunIniFile(params, 'NIRPS_HA', 'helios_run')
    helios_nirps_ha.append_sequence('helios_seq')
    run_files.append(helios_nirps_ha)
    # trigger night calib run
    tnc_run_nirps_ha = RunIniFile(params, 'NIRPS_HA', 'trigger_night_calibrun')
    tnc_run_nirps_ha.append_sequence('pp_seq_opt')
    tnc_run_nirps_ha.append_sequence('calib_seq')
    tnc_run_nirps_ha.modify('RUN_PP_SCI', False)
    tnc_run_nirps_ha.modify('RUN_PP_TEL', False)
    tnc_run_nirps_ha.modify('RUN_PP_HC1HC1', False)
    tnc_run_nirps_ha.modify('RUN_PP_FPFP', False)
    tnc_run_nirps_ha.modify('RUN_PP_FF', False)
    tnc_run_nirps_ha.modify('RUN_PP_DFP', False)
    tnc_run_nirps_ha.modify('RUN_PP_SKY', False)
    tnc_run_nirps_ha.modify('RUN_PP_LFC', False)
    tnc_run_nirps_ha.modify('RUN_PP_LFCFP', False)
    tnc_run_nirps_ha.modify('RUN_PP_FPLFC', False)
    tnc_run_nirps_ha.modify('RECAL_TEMPLATES', False)
    tnc_run_nirps_ha.modify('TRIGGER_RUN', True)
    tnc_run_nirps_ha.modify('USE_ENGINEERING', True)
    run_files.append(tnc_run_nirps_ha)
    # trigger night science run
    tns_run_nirps_ha = RunIniFile(params, 'NIRPS_HA', 'trigger_night_scirun')
    tns_run_nirps_ha.append_sequence('pp_seq_opt')
    tns_run_nirps_ha.append_sequence('science_seq')
    tns_run_nirps_ha.modify('RUN_PP_CAL', False)
    tns_run_nirps_ha.modify('RUN_PP_TEL', False)
    tns_run_nirps_ha.modify('RUN_PP_HC1HC1', False)
    tns_run_nirps_ha.modify('RUN_PP_FPFP', False)
    tns_run_nirps_ha.modify('RUN_PP_FF', False)
    tns_run_nirps_ha.modify('RUN_PP_DFP', False)
    tns_run_nirps_ha.modify('RUN_PP_SKY', False)
    tns_run_nirps_ha.modify('RUN_PP_LFC', False)
    tns_run_nirps_ha.modify('RUN_PP_LFCFP', False)
    tns_run_nirps_ha.modify('RUN_PP_FPLFC', False)
    tns_run_nirps_ha.modify('RECAL_TEMPLATES', False)
    tns_run_nirps_ha.modify('TRIGGER_RUN', True)
    tns_run_nirps_ha.modify('USE_ENGINEERING', True)
    run_files.append(tns_run_nirps_ha)
    # lbl run
    lbl_run_nirps_ha = RunIniFile(params, 'NIRPS_HA', 'lbl_run')
    lbl_run_nirps_ha.append_sequence('lbl_seq')
    # do not skip any steps of the lbl
    lbl_run_nirps_ha.modify('SKIP_LBLREF', False)
    lbl_run_nirps_ha.modify('SKIP_LBLMASK_SCI', False)
    lbl_run_nirps_ha.modify('SKIP_LBLCOMPUTE_SCI', False)
    lbl_run_nirps_ha.modify('SKIP_LBLCOMPILE_SCI', False)
    run_files.append(lbl_run_nirps_ha)
    # batch run
    # batch_run_nirps_ha = RunIniFile(params, 'NIRPS_HA', 'batch_run')
    # batch_run_nirps_ha.add_sequence_as_command('limited_seq')
    # batch_run_nirps_ha.modify('RUN_OBS_DIR', DEFAULT_REF_OBSDIR['NIRPS_HA'])
    # run_files.append(batch_run_nirps_ha)

    return run_files


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # print hello world
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
