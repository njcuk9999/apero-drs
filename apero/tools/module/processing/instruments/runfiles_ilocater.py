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
__NAME__ = 'instruments.runfiles_ilocater.ini.py'
__INSTRUMENT__ = 'ILOCATER'
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
    blank_run_ilocater = RunIniFile(params, 'ILOCATER', 'blank_run')
    blank_run_ilocater.append_sequence('blank_seq')
    run_files.append(blank_run_ilocater)
    # mini run
    mini_run_ilocater = RunIniFile(params, 'ILOCATER', 'mini_run')
    mini_run_ilocater.modify('USE_ENGINEERING', True)
    mini_run_ilocater.append_sequence('limited_seq')
    # do not skip any steps of the lbl
    mini_run_ilocater.modify('SKIP_LBLREF', False)
    mini_run_ilocater.modify('SKIP_LBLMASK_SCI', False)
    mini_run_ilocater.modify('SKIP_LBLCOMPUTE_SCI', False)
    mini_run_ilocater.modify('SKIP_LBLCOMPILE_SCI', False)
    run_files.append(mini_run_ilocater)
    # quick run
    quick_run_ilocater = RunIniFile(params, 'ILOCATER', 'quick_run')
    quick_run_ilocater.append_sequence('pp_seq_opt')
    quick_run_ilocater.append_sequence('quick_seq')
    quick_run_ilocater.modify('RUN_PP_CAL', False)
    quick_run_ilocater.modify('RUN_PP_TEL', False)
    quick_run_ilocater.modify('RUN_PP_HC1HC1', False)
    quick_run_ilocater.modify('RUN_PP_FPFP', False)
    quick_run_ilocater.modify('RUN_PP_FF', False)
    quick_run_ilocater.modify('RUN_PP_DFP', False)
    quick_run_ilocater.modify('RUN_PP_SKY', False)
    quick_run_ilocater.modify('RUN_PP_LFC', False)
    quick_run_ilocater.modify('RUN_PP_LFCFP', False)
    quick_run_ilocater.modify('RUN_PP_FPLFC', False)
    run_files.append(quick_run_ilocater)
    # calib run
    calib_run_ilocater = RunIniFile(params, 'ILOCATER', 'calib_run')
    calib_run_ilocater.append_sequence('pp_seq_opt')
    calib_run_ilocater.append_sequence('calib_seq')
    calib_run_ilocater.modify('RUN_PP_SCI', False)
    calib_run_ilocater.modify('RUN_PP_TEL', False)
    calib_run_ilocater.modify('RUN_PP_HC1HC1', False)
    calib_run_ilocater.modify('RUN_PP_FPFP', False)
    calib_run_ilocater.modify('RUN_PP_FF', False)
    calib_run_ilocater.modify('RUN_PP_DFP', False)
    calib_run_ilocater.modify('RUN_PP_SKY', False)
    calib_run_ilocater.modify('RUN_PP_LFC', False)
    calib_run_ilocater.modify('RUN_PP_LFCFP', False)
    calib_run_ilocater.modify('RUN_PP_FPLFC', False)
    run_files.append(calib_run_ilocater)
    # complete run
    complete_run_ilocater = RunIniFile(params, 'ILOCATER', 'complete_run')
    complete_run_ilocater.skip_default = False
    complete_run_ilocater.append_sequence('full_seq')
    run_files.append(complete_run_ilocater)
    # reference calib run
    mcalib_run_ilocater = RunIniFile(params, 'ILOCATER', 'ref_calib_run')
    mcalib_run_ilocater.append_sequence('pp_seq_opt')
    mcalib_run_ilocater.append_sequence('ref_seq')
    mcalib_run_ilocater.modify('RUN_PP_SCI', False)
    mcalib_run_ilocater.modify('RUN_PP_TEL', False)
    mcalib_run_ilocater.modify('RUN_PP_HC1HC1', False)
    mcalib_run_ilocater.modify('RUN_PP_FPFP', False)
    mcalib_run_ilocater.modify('RUN_PP_FF', False)
    mcalib_run_ilocater.modify('RUN_PP_DFP', False)
    mcalib_run_ilocater.modify('RUN_PP_SKY', False)
    mcalib_run_ilocater.modify('RUN_PP_LFC', False)
    mcalib_run_ilocater.modify('RUN_PP_LFCFP', False)
    mcalib_run_ilocater.modify('RUN_PP_FPLFC', False)
    run_files.append(mcalib_run_ilocater)
    # other run
    other_run_ilocater = RunIniFile(params, 'ILOCATER', 'other_run')
    other_run_ilocater.append_sequence('pp_seq_opt')
    other_run_ilocater.append_sequence('eng_seq')
    other_run_ilocater.run_default = False
    run_files.append(other_run_ilocater)
    # science run
    science_run_ilocater = RunIniFile(params, 'ILOCATER', 'science_run')
    science_run_ilocater.append_sequence('pp_seq_opt')
    science_run_ilocater.append_sequence('science_seq')
    science_run_ilocater.append_sequence('lbl_seq')
    science_run_ilocater.modify('RUN_PP_CAL', False)
    science_run_ilocater.modify('RUN_PP_TEL', False)
    science_run_ilocater.modify('RUN_PP_HC1HC1', False)
    science_run_ilocater.modify('RUN_PP_FPFP', False)
    science_run_ilocater.modify('RUN_PP_FF', False)
    science_run_ilocater.modify('RUN_PP_DFP', False)
    science_run_ilocater.modify('RUN_PP_SKY', False)
    science_run_ilocater.modify('RUN_PP_LFC', False)
    science_run_ilocater.modify('RUN_PP_LFCFP', False)
    science_run_ilocater.modify('RUN_PP_FPLFC', False)
    science_run_ilocater.modify('RECAL_TEMPLATES', False)
    run_files.append(science_run_ilocater)
    # tellu run
    tellu_run_ilocater = RunIniFile(params, 'ILOCATER', 'tellu_run')
    tellu_run_ilocater.append_sequence('pp_seq_opt')
    tellu_run_ilocater.append_sequence('science_seq')
    tellu_run_ilocater.modify('RUN_PP_CAL', False)
    tellu_run_ilocater.modify('RUN_PP_SCI', False)
    tellu_run_ilocater.modify('RUN_PP_HC1HC1', False)
    tellu_run_ilocater.modify('RUN_PP_FPFP', False)
    tellu_run_ilocater.modify('RUN_PP_FF', False)
    tellu_run_ilocater.modify('RUN_PP_DFP', False)
    tellu_run_ilocater.modify('RUN_PP_SKY', False)
    tellu_run_ilocater.modify('RUN_PP_LFC', False)
    tellu_run_ilocater.modify('RUN_PP_LFCFP', False)
    tellu_run_ilocater.modify('RUN_PP_FPLFC', False)
    run_files.append(tellu_run_ilocater)
    # online run
    online_run_ilocater = RunIniFile(params, 'ILOCATER', 'online_run')
    online_run_ilocater.append_sequence('pp_seq_opt')
    online_run_ilocater.append_sequence('calib_seq')
    online_run_ilocater.append_sequence('tellu_seq')
    online_run_ilocater.append_sequence('science_seq')
    online_run_ilocater.append_sequence('lbl_seq')
    online_run_ilocater.modify('RUN_PPREF', False)
    online_run_ilocater.modify('RUN_PP_CAL', True)
    online_run_ilocater.modify('RUN_PP_SCI', True)
    online_run_ilocater.modify('RUN_PP_TEL', False)
    online_run_ilocater.modify('RUN_PP_HC1HC1', False)
    online_run_ilocater.modify('RUN_PP_FPFP', False)
    online_run_ilocater.modify('RUN_PP_FF', False)
    online_run_ilocater.modify('RUN_PP_DFP', False)
    online_run_ilocater.modify('RUN_PP_SKY', False)
    online_run_ilocater.modify('RUN_PP_LFC', False)
    online_run_ilocater.modify('RUN_PP_LFCFP', False)
    online_run_ilocater.modify('RUN_PP_FPLFC', False)
    online_run_ilocater.modify('RUN_PP_FPHC1', False)
    online_run_ilocater.modify('RUN_PP_HC1FP', False)
    online_run_ilocater.modify('RUN_PP_EVERY', False)
    online_run_ilocater.modify('RECAL_TEMPLATES', False)
    online_run_ilocater.modify('CORES', 5)
    online_run_ilocater.modify('USE_ENGINEERING', True)
    run_files.append(online_run_ilocater)
    # offline run
    offline_run_ilocater = RunIniFile(params, 'ILOCATER', 'offline_run')
    offline_run_ilocater.skip_default = False
    offline_run_ilocater.append_sequence('full_seq')
    offline_run_ilocater.modify('CORES', 15)
    offline_run_ilocater.modify('USE_ENGINEERING', True)
    run_files.append(offline_run_ilocater)
    # test run
    test_run_ilocater = RunIniFile(params, 'ILOCATER', 'test_run')
    test_run_ilocater.append_sequence('limited_seq')
    test_run_ilocater.run_default = False
    test_run_ilocater.modify('TEST_RUN', True)
    run_files.append(test_run_ilocater)
    # helios run
    helios_ilocater = RunIniFile(params, 'ILOCATER', 'helios_run')
    helios_ilocater.append_sequence('helios_seq')
    run_files.append(helios_ilocater)
    # lbl run
    lbl_run_ilocater = RunIniFile(params, 'ILOCATER', 'lbl_run')
    lbl_run_ilocater.append_sequence('lbl_seq')
    # do not skip any steps of the lbl
    lbl_run_ilocater.modify('SKIP_LBLREF', False)
    lbl_run_ilocater.modify('SKIP_LBLMASK_SCI', False)
    lbl_run_ilocater.modify('SKIP_LBLCOMPUTE_SCI', False)
    lbl_run_ilocater.modify('SKIP_LBLCOMPILE_SCI', False)
    run_files.append(lbl_run_ilocater)
    # batch run
    # batch_run_ilocater = RunIniFile(params, 'NIRPS_HA', 'batch_run')
    # batch_run_ilocater.add_sequence_as_command('limited_seq')
    # batch_run_ilocater.modify('RUN_OBS_DIR', DEFAULT_REF_OBSDIR['NIRPS_HA'])
    # run_files.append(batch_run_ilocater)

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
