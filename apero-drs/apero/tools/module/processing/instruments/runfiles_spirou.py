#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2022-06-06

@author: cook
"""
from typing import List

from aperocore.constants import param_functions
from apero.tools.module.processing import drs_run_ini
from apero.base import base as apero_base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'instruments.runfiles_spirou.ini.py'
__INSTRUMENT__ = 'SPIROU'
__PACKAGE__ = apero_base.__PACKAGE__
__version__ = apero_base.__version__
__authors__ = apero_base.__authors__
__date__ = apero_base.__date__
__release__ = apero_base.__release__
# get the run file class
RunIniFile = drs_run_ini.RunIniFile
# get parameter dictionary class
ParamDict = param_functions.ParamDict
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
    # do not skip any steps of the lbl
    mini_run1_spirou.modify('SKIP_LBLREF', False)
    mini_run1_spirou.modify('SKIP_LBLMASK_SCI', False)
    mini_run1_spirou.modify('SKIP_LBLCOMPUTE_SCI', False)
    mini_run1_spirou.modify('SKIP_LBLCOMPILE_SCI', False)
    # mini runs need debug data
    mini_run1_spirou.modify('DEBUG.OUTFILE.BCKGRD_FILE', True)
    mini_run1_spirou.modify('DEBUG.OUTFILE.E2DSLL_FILE', True)
    mini_run1_spirou.modify('DEBUG.OUTFILE.SHAPE_FILES', True)
    mini_run1_spirou.modify('DEBUG.OUTFILE.UNCORR_EXT_FILES', True)
    run_files.append(mini_run1_spirou)

    # mini run 2
    mini_run2_spirou = RunIniFile(params, 'SPIROU', 'mini_run2')
    mini_run2_spirou.rkey('SCIENCE_TARGETS', 'Gl699')
    mini_run2_spirou.append_sequence('limited_seq')
    mini_run2_spirou.modify('SKIP_LBLREF', False)
    mini_run2_spirou.modify('SKIP_LBLMASK_SCI', False)
    mini_run2_spirou.modify('SKIP_LBLCOMPUTE_SCI', False)
    mini_run2_spirou.modify('SKIP_LBLCOMPILE_SCI', False)
    # mini runs need debug data
    mini_run2_spirou.modify('DEBUG.OUTFILE.BCKGRD_FILE', True)
    mini_run2_spirou.modify('DEBUG.OUTFILE.E2DSLL_FILE', True)
    mini_run2_spirou.modify('DEBUG.OUTFILE.SHAPE_FILES', True)
    mini_run2_spirou.modify('DEBUG.OUTFILE.UNCORR_EXT_FILES', True)
    run_files.append(mini_run2_spirou)
    # quick run
    quick_run_spirou = RunIniFile(params, 'SPIROU', 'quick_run')
    quick_run_spirou.append_sequence('pp_seq_opt')
    quick_run_spirou.append_sequence('quick_seq')
    quick_run_spirou.modify('RUN_PP_SCI', True)
    run_files.append(quick_run_spirou)
    # calib run
    calib_run_spirou = RunIniFile(params, 'SPIROU', 'calib_run')
    calib_run_spirou.append_sequence('pp_seq_opt')
    calib_run_spirou.append_sequence('calib_seq')
    calib_run_spirou.modify('RUN_PP_CAL', True)
    run_files.append(calib_run_spirou)
    # complete run
    complete_run_spirou = RunIniFile(params, 'SPIROU', 'complete_run')
    complete_run_spirou.append_sequence('full_seq')
    complete_run_spirou.skip_default = False
    complete_run_spirou.modify('CORES', -5)
    run_files.append(complete_run_spirou)
    # reference calib run
    mcalib_run_spirou = RunIniFile(params, 'SPIROU', 'ref_calib_run')
    mcalib_run_spirou.append_sequence('pp_seq_opt')
    mcalib_run_spirou.append_sequence('ref_seq')
    mcalib_run_spirou.modify('RUN_PP_CAL', True)
    run_files.append(mcalib_run_spirou)

    # static calib run (for static wavelength calibration)
    static_run_spirou = RunIniFile(params, 'SPIROU', 'static_run')
    static_run_spirou.append_sequence('pp_seq_opt')
    static_run_spirou.append_sequence('ref_seq')
    static_run_spirou.append_sequence('eng_seq')
    static_run_spirou.rkey('RUN_OBS_DIR', 'STATIC')
    static_run_spirou.rkey('REF_OBS_DIR', 'STATIC')
    static_run_spirou.rkey('USE_ENGINEERING', True)
    static_run_spirou.modify('RUN_PP_CAL', True)
    static_run_spirou.modify('RUN_LEAKREF', False)
    static_run_spirou.modify('RUN_WAVEREF', False)
    static_run_spirou.modify('RUN_THERM_REFI', False)
    static_run_spirou.modify('RUN_THERM_REFT', False)
    static_run_spirou.modify('RUN_EXTQUICK_HC', True)
    static_run_spirou.modify('RUN_EXTQUICK_FP', True)
    run_files.append(static_run_spirou)

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
    tellu_run_spirou.modify('RUN_PP_TEL', True)
    # science run
    science_run_spirou = RunIniFile(params, 'SPIROU', 'science_run')
    science_run_spirou.append_sequence('pp_seq_opt')
    science_run_spirou.append_sequence('science_seq')
    science_run_spirou.append_sequence('lbl_seq')
    science_run_spirou.modify('RUN_PP_SCI', True)
    science_run_spirou.modify('RECAL_TEMPLATE_IF_EXISTS', False)
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
    tnc_run_spirou.modify('RUN_PP_CAL', True)
    tnc_run_spirou.modify('RECAL_TEMPLATE_IF_EXISTS', False)
    tnc_run_spirou.modify('TRIGGER_RUN', True)
    tnc_run_spirou.modify('USE_ENGINEERING', True)
    run_files.append(tnc_run_spirou)
    # trigger night science run
    tns_run_spirou = RunIniFile(params, 'SPIROU', 'trigger_night_scirun')
    tns_run_spirou.append_sequence('pp_seq_opt')
    tns_run_spirou.append_sequence('science_seq')
    tns_run_spirou.modify('RUN_PP_SCI', True)
    tns_run_spirou.modify('RUN_PP_TEL', True)
    tns_run_spirou.modify('RUN_POLAR', False)
    tns_run_spirou.modify('RECAL_TEMPLATE_IF_EXISTS', False)
    tns_run_spirou.modify('TRIGGER_RUN', True)
    tns_run_spirou.modify('USE_ENGINEERING', True)
    run_files.append(tns_run_spirou)
    # lbl run
    lbl_run_spirou = RunIniFile(params, 'SPIROU', 'lbl_run')
    lbl_run_spirou.append_sequence('lbl_seq')
    # do not skip any steps of the lbl
    lbl_run_spirou.modify('SKIP_LBLREF', False)
    lbl_run_spirou.modify('SKIP_LBLMASK_SCI', False)
    lbl_run_spirou.modify('SKIP_LBLCOMPUTE_SCI', False)
    lbl_run_spirou.modify('SKIP_LBLCOMPILE_SCI', False)

    run_files.append(lbl_run_spirou)

    # batch run
    # TODO: put back in
    # batch_run_spirou = RunIniFile(params, 'SPIROU', 'batch_run')
    # batch_run_spirou.add_sequence_as_command('limited_seq')
    # batch_run_spirou.modify('RUN_OBS_DIR', DEFAULT_REF_OBSDIR)
    # run_files.append(batch_run_spirou)

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
