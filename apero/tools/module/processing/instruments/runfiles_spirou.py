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
__NAME__ = 'instruments.runfiles_spirou.ini.py'
__INSTRUMENT__ = 'SPIROU'
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
    # create default runs files for SPIROU
    # -------------------------------------------------------------------------
    # blank run
    blank_run_spirou = RunIniFile(params, 'SPIROU', 'blank_run')
    blank_run_spirou.append_sequence('blank_seq')
    run_files.append(blank_run_spirou)
    # mini run 1
    mini_run1_spirou = RunIniFile(params, 'SPIROU', 'mini_run1')
    mini_run1_spirou.rkey('REF_OBS_DIR', '2019-04-20')
    mini_run1_spirou.rkey('SCIENCE_TARGETS', 'Gl699')
    mini_run1_spirou.append_sequence('limited_seq')
    run_files.append(mini_run1_spirou)
    # mini run 2
    mini_run2_spirou = RunIniFile(params, 'SPIROU', 'mini_run2')
    mini_run2_spirou.rkey('SCIENCE_TARGETS', 'Gl699')
    mini_run2_spirou.append_sequence('limited_seq')
    run_files.append(mini_run2_spirou)
    # quick run
    quick_run_spirou = RunIniFile(params, 'SPIROU', 'quick_run')
    quick_run_spirou.append_sequence('pp_seq_opt')
    quick_run_spirou.append_sequence('quick_seq')
    quick_run_spirou.modify('RUN_PP_CAL', False)
    quick_run_spirou.modify('RUN_PP_TEL', False)
    quick_run_spirou.modify('RUN_PP_HC1HC1', False)
    quick_run_spirou.modify('RUN_PP_FPFP', False)
    quick_run_spirou.modify('RUN_PP_FF', False)
    quick_run_spirou.modify('RUN_PP_DFP', False)
    quick_run_spirou.modify('RUN_PP_SKY', False)
    quick_run_spirou.modify('RUN_PP_LFC', False)
    quick_run_spirou.modify('RUN_PP_LFCFP', False)
    quick_run_spirou.modify('RUN_PP_FPLFC', False)
    run_files.append(quick_run_spirou)
    # calib run
    calib_run_spirou = RunIniFile(params, 'SPIROU', 'calib_run')
    calib_run_spirou.append_sequence('pp_seq_opt')
    calib_run_spirou.append_sequence('calib_seq')
    calib_run_spirou.modify('RUN_PP_SCI', False)
    calib_run_spirou.modify('RUN_PP_TEL', False)
    calib_run_spirou.modify('RUN_PP_HC1HC1', False)
    calib_run_spirou.modify('RUN_PP_FPFP', False)
    calib_run_spirou.modify('RUN_PP_FF', False)
    calib_run_spirou.modify('RUN_PP_DFP', False)
    calib_run_spirou.modify('RUN_PP_SKY', False)
    calib_run_spirou.modify('RUN_PP_LFC', False)
    calib_run_spirou.modify('RUN_PP_LFCFP', False)
    calib_run_spirou.modify('RUN_PP_FPLFC', False)
    run_files.append(calib_run_spirou)
    # complete run
    complete_run_spirou = RunIniFile(params, 'SPIROU', 'complete_run')
    complete_run_spirou.append_sequence('full_seq')
    complete_run_spirou.modify('CORES', -5)
    run_files.append(complete_run_spirou)
    # reference calib run
    mcalib_run_spirou = RunIniFile(params, 'SPIROU', 'ref_calib_run')
    mcalib_run_spirou.append_sequence('pp_seq_opt')
    mcalib_run_spirou.append_sequence('ref_seq')
    mcalib_run_spirou.modify('RUN_PP_SCI', False)
    mcalib_run_spirou.modify('RUN_PP_TEL', False)
    mcalib_run_spirou.modify('RUN_PP_HC1HC1', False)
    mcalib_run_spirou.modify('RUN_PP_FPFP', False)
    mcalib_run_spirou.modify('RUN_PP_FF', False)
    mcalib_run_spirou.modify('RUN_PP_DFP', False)
    mcalib_run_spirou.modify('RUN_PP_SKY', False)
    mcalib_run_spirou.modify('RUN_PP_LFC', False)
    mcalib_run_spirou.modify('RUN_PP_LFCFP', False)
    mcalib_run_spirou.modify('RUN_PP_FPLFC', False)
    mcalib_run_spirou.modify('RUN_OBS_DIR', DEFAULT_REF_OBSDIR)
    run_files.append(mcalib_run_spirou)
    # other run
    other_run_spirou = RunIniFile(params, 'SPIROU', 'other_run')
    other_run_spirou.append_sequence('pp_seq_opt')
    other_run_spirou.append_sequence('eng_seq')
    other_run_spirou.run_default = False
    run_files.append(other_run_spirou)
    # tellu run
    tellu_run_spirou = RunIniFile(params, 'SPIROU', 'tellu_run')
    tellu_run_spirou.append_sequence('pp_seq_opt')
    tellu_run_spirou.append_sequence('science_seq')
    tellu_run_spirou.modify('RUN_PP_CAL', False)
    tellu_run_spirou.modify('RUN_PP_SCI', False)
    tellu_run_spirou.modify('RUN_PP_HC1HC1', False)
    tellu_run_spirou.modify('RUN_PP_FPFP', False)
    tellu_run_spirou.modify('RUN_PP_FF', False)
    tellu_run_spirou.modify('RUN_PP_DFP', False)
    tellu_run_spirou.modify('RUN_PP_SKY', False)
    tellu_run_spirou.modify('RUN_PP_LFC', False)
    tellu_run_spirou.modify('RUN_PP_LFCFP', False)
    tellu_run_spirou.modify('RUN_PP_FPLFC', False)
    # science run
    science_run_spirou = RunIniFile(params, 'SPIROU', 'science_run')
    science_run_spirou.append_sequence('pp_seq_opt')
    science_run_spirou.append_sequence('science_seq')
    science_run_spirou.modify('RUN_PP_CAL', False)
    science_run_spirou.modify('RUN_PP_TEL', False)
    science_run_spirou.modify('RUN_PP_HC1HC1', False)
    science_run_spirou.modify('RUN_PP_FPFP', False)
    science_run_spirou.modify('RUN_PP_FF', False)
    science_run_spirou.modify('RUN_PP_DFP', False)
    science_run_spirou.modify('RUN_PP_SKY', False)
    science_run_spirou.modify('RUN_PP_LFC', False)
    science_run_spirou.modify('RUN_PP_LFCFP', False)
    science_run_spirou.modify('RUN_PP_FPLFC', False)
    science_run_spirou.modify('RECAL_TEMPLATES', False)
    run_files.append(science_run_spirou)
    # test run
    test_run_spirou = RunIniFile(params, 'SPIROU', 'test_run')
    test_run_spirou.append_sequence('limited_seq')
    test_run_spirou.run_default = False
    test_run_spirou.modify('TEST_RUN', True)
    run_files.append(test_run_spirou)
    # trigger night calib run
    tnc_run_spirou = RunIniFile(params, 'SPIROU', 'trigger_night_calibrun')
    tnc_run_spirou.append_sequence('pp_seq_opt')
    tnc_run_spirou.append_sequence('calib_seq')
    tnc_run_spirou.modify('RUN_PP_SCI', False)
    tnc_run_spirou.modify('RUN_PP_TEL', False)
    tnc_run_spirou.modify('RUN_PP_HC1HC1', False)
    tnc_run_spirou.modify('RUN_PP_FPFP', False)
    tnc_run_spirou.modify('RUN_PP_FF', False)
    tnc_run_spirou.modify('RUN_PP_DFP', False)
    tnc_run_spirou.modify('RUN_PP_SKY', False)
    tnc_run_spirou.modify('RUN_PP_LFC', False)
    tnc_run_spirou.modify('RUN_PP_LFCFP', False)
    tnc_run_spirou.modify('RUN_PP_FPLFC', False)
    tnc_run_spirou.modify('RECAL_TEMPLATES', False)
    tnc_run_spirou.modify('TRIGGER_RUN', True)
    tnc_run_spirou.modify('USE_ENGINEERING', True)
    run_files.append(tnc_run_spirou)
    # trigger night science run
    tns_run_spirou = RunIniFile(params, 'SPIROU', 'trigger_night_scirun')
    tns_run_spirou.append_sequence('pp_seq_opt')
    tns_run_spirou.append_sequence('science_seq')
    tns_run_spirou.modify('RUN_PP_CAL', False)
    tns_run_spirou.modify('RUN_PP_TEL', False)
    tns_run_spirou.modify('RUN_PP_HC1HC1', False)
    tns_run_spirou.modify('RUN_PP_FPFP', False)
    tns_run_spirou.modify('RUN_PP_FF', False)
    tns_run_spirou.modify('RUN_PP_DFP', False)
    tns_run_spirou.modify('RUN_PP_SKY', False)
    tns_run_spirou.modify('RUN_PP_LFC', False)
    tns_run_spirou.modify('RUN_PP_LFCFP', False)
    tns_run_spirou.modify('RUN_PP_FPLFC', False)
    tns_run_spirou.modify('RUN_POLAR', False)
    tns_run_spirou.modify('RECAL_TEMPLATES', False)
    tns_run_spirou.modify('TRIGGER_RUN', True)
    tns_run_spirou.modify('USE_ENGINEERING', True)
    run_files.append(tns_run_spirou)
    # batch run
    batch_run_spirou = RunIniFile(params, 'SPIROU', 'batch_run')
    batch_run_spirou.add_sequence_as_command('limited_seq')
    batch_run_spirou.modify('RUN_OBS_DIR', DEFAULT_REF_OBSDIR)
    run_files.append(batch_run_spirou)

    # return the run files
    return run_files


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # Main code here
    pass

# =============================================================================
# End of code
# =============================================================================
