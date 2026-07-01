#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Raw and reduced APERO check function modules and CHECKS registry."""

from importlib import import_module


def _module(module_name: str):
	"""Import one APERO-check module by its full dotted name."""
	return import_module(module_name)


# Load check definitions from sibling modules.
BLANK_CHECK = _module('apero_ri.apero_monitoring.checks.check_blank').CHECK
COB_CHECK = _module(
	'apero_ri.apero_monitoring.checks.check_calib_ob_test'
).CHECK
CALIB_CHECK = _module('apero_ri.apero_monitoring.checks.check_calib_test').CHECK
ENG_ENC_TEMP_RMS_CHECK = _module(
	'apero_ri.apero_monitoring.checks.check_eng_enclosure_temperature_rms'
).CHECK
ENG_ENC_SETPOINT_OFFSET_CHECK = _module(
	'apero_ri.apero_monitoring.checks.check_eng_enclosure_setpoint_offset'
).CHECK
ENG_VAC_GAUGE_UPPER_CHECK = _module(
	'apero_ri.apero_monitoring.checks.check_eng_vacuum_gauge_upper'
).CHECK
ENG_ISO_VALVE_STATE_CHECK = _module(
	'apero_ri.apero_monitoring.checks.check_eng_isolation_valve_state'
).CHECK
ENG_CRYO1_STATE_CHECK = _module(
	'apero_ri.apero_monitoring.checks.check_eng_cryo1_state'
).CHECK
ENG_CRYO2_STATE_CHECK = _module(
	'apero_ri.apero_monitoring.checks.check_eng_cryo2_state'
).CHECK
ENG_TURBOPUMP_STATE_CHECK = _module(
	'apero_ri.apero_monitoring.checks.check_eng_turbopump_state'
).CHECK
ENG_WARN_CRYO1_CHECK = _module(
	'apero_ri.apero_monitoring.checks.check_eng_warning_cryo1_state'
).CHECK
ENG_WARN_CRYO2_CHECK = _module(
	'apero_ri.apero_monitoring.checks.check_eng_warning_cryo2_state'
).CHECK
ENG_FP_INTERIOR_RMS_CHECK = _module(
	'apero_ri.apero_monitoring.checks.check_eng_fp_interior_rms'
).CHECK
ENG_FP_EXTERIOR_RANGE_CHECK = _module(
	'apero_ri.apero_monitoring.checks.check_eng_fp_exterior_range'
).CHECK
ENG_FP_SETPOINT_RMS_CHECK = _module(
	'apero_ri.apero_monitoring.checks.check_eng_fp_setpoint_rms'
).CHECK
ENG_ENC_HEATER_MAX_CHECK = _module(
	'apero_ri.apero_monitoring.checks.check_eng_enclosure_heater_power_max'
).CHECK
ENG_SCRAMBLING_STATE_CHECK = _module(
	'apero_ri.apero_monitoring.checks.check_eng_scrambling_status_science'
).CHECK
ENG_STRETCHER_STATE_CHECK = _module(
	'apero_ri.apero_monitoring.checks.check_eng_stretcher_status_state'
).CHECK
ENG_BACKEND_ERROR_STATE_CHECK = _module(
	'apero_ri.apero_monitoring.checks.check_eng_backend_device_error_state'
).CHECK
NO_SCI_CHECK = _module(
	'apero_ri.apero_monitoring.checks.check_no_sci_test'
).CHECK
HAS_OBSDIR_CHECK = _module(
	'apero_ri.apero_monitoring.checks.check_obsdir_test'
).CHECK
QUAL_CHECK = _module('apero_ri.apero_monitoring.checks.check_qual_test').CHECK
ASTROM_CHECK = _module(
    'apero_ri.apero_monitoring.checks.check_astrometrics'
).CHECK
CRITICAL_CHECK = _module(
    'apero_ri.apero_monitoring.checks.check_critical_test'
).CHECK
CRITICAL_SCI_CHECK = _module(
    'apero_ri.apero_monitoring.checks.check_critical_sci_test'
).CHECK

# =============================================================================
# Red checks
# =============================================================================
MANUAL_START_CHECK = _module(
    'apero_ri.apero_monitoring.checks.check_manual_start'
).CHECK
MANUAL_END_CHECK = _module(
    'apero_ri.apero_monitoring.checks.check_manual_end'
).CHECK
APERO_START_CHECK = _module(
    'apero_ri.apero_monitoring.checks.check_apero_start'
).CHECK
APERO_END_CHECK = _module(
    'apero_ri.apero_monitoring.checks.check_apero_end'
).CHECK
ARI_START_CHECK = _module(
    'apero_ri.apero_monitoring.checks.check_ari_start'
).CHECK
ARI_END_CHECK = _module(
    'apero_ri.apero_monitoring.checks.check_ari_end'
).CHECK
PIXEL_SHIFTS_CHECK = _module(
    'apero_ri.apero_monitoring.checks.check_pixel_shifts'
).CHECK
LOW_SNR_CHECK = _module(
    'apero_ri.apero_monitoring.checks.check_low_snr'
).CHECK
EXCESS_MODAL_CHECK = _module(
    'apero_ri.apero_monitoring.checks.check_excess_modal'
).CHECK
PREV_REDUC_CHECK = _module(
    'apero_ri.apero_monitoring.checks.check_prev_reduc'
).CHECK
BAD_CCF_CHECK = _module(
    'apero_ri.apero_monitoring.checks.check_bad_ccf'
).CHECK


# =============================================================================
# Checks storage
# =============================================================================
CHECKS = dict()


# =============================================================================
# Raw checks
# =============================================================================
CHECKS['BLANK'] = BLANK_CHECK
CHECKS['HAS_OBSDIR'] = HAS_OBSDIR_CHECK
CHECKS['CALIB_TEST'] = CALIB_CHECK
CHECKS['COB_TEST'] = COB_CHECK
CHECKS['ENG_ENC_TEMP_RMS'] = ENG_ENC_TEMP_RMS_CHECK
CHECKS['ENG_ENC_SETPOINT_OFFSET'] = ENG_ENC_SETPOINT_OFFSET_CHECK
CHECKS['ENG_VAC_GAUGE_UPPER'] = ENG_VAC_GAUGE_UPPER_CHECK
CHECKS['ENG_ISO_VALVE_STATE'] = ENG_ISO_VALVE_STATE_CHECK
CHECKS['ENG_CRYO1_STATE'] = ENG_CRYO1_STATE_CHECK
CHECKS['ENG_CRYO2_STATE'] = ENG_CRYO2_STATE_CHECK
CHECKS['ENG_TURBOPUMP_STATE'] = ENG_TURBOPUMP_STATE_CHECK
CHECKS['ENG_WARN_CRYO1'] = ENG_WARN_CRYO1_CHECK
CHECKS['ENG_WARN_CRYO2'] = ENG_WARN_CRYO2_CHECK
CHECKS['ENG_FP_INTERIOR_RMS'] = ENG_FP_INTERIOR_RMS_CHECK
CHECKS['ENG_FP_EXTERIOR_RANGE'] = ENG_FP_EXTERIOR_RANGE_CHECK
CHECKS['ENG_FP_SETPOINT_RMS'] = ENG_FP_SETPOINT_RMS_CHECK
CHECKS['ENG_ENC_HEATER_MAX'] = ENG_ENC_HEATER_MAX_CHECK
CHECKS['ENG_SCRAMBLING_STATE'] = ENG_SCRAMBLING_STATE_CHECK
CHECKS['ENG_STRETCHER_STATE'] = ENG_STRETCHER_STATE_CHECK
CHECKS['ENG_BACKEND_ERROR_STATE'] = ENG_BACKEND_ERROR_STATE_CHECK
CHECKS['NO_SCI'] = NO_SCI_CHECK
CHECKS['QUAL_TEST'] = QUAL_CHECK
CHECKS['ASTROM'] = ASTROM_CHECK
CHECKS['CRITICAL_TEST'] = CRITICAL_CHECK
CHECKS['CRITICAL_SCI_TEST'] = CRITICAL_SCI_CHECK

# =============================================================================
# Red checks
# =============================================================================
CHECKS['MANUAL_START'] = MANUAL_START_CHECK
CHECKS['MANUAL_END'] = MANUAL_END_CHECK
CHECKS['APERO_START'] = APERO_START_CHECK
CHECKS['APERO_END'] = APERO_END_CHECK
CHECKS['ARI_START'] = ARI_START_CHECK
CHECKS['ARI_END'] = ARI_END_CHECK
CHECKS['PIXEL_SHIFTS'] = PIXEL_SHIFTS_CHECK
CHECKS['LOW_SNR'] = LOW_SNR_CHECK
CHECKS['EXCESS_MODAL'] = EXCESS_MODAL_CHECK
CHECKS['PREV_REDUC'] = PREV_REDUC_CHECK
CHECKS['BAD_CCF'] = BAD_CCF_CHECK
