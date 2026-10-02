---
card_label: Checks
card_icon: fa-solid fa-list-check
related:
  - monitor
  - monitor/how_to/
  - known_errors
---

# APERO monitor checks

Checks evaluate one specific property of an observation, reduction, or
instrument state. Use the result together with the observation context and
known-error guidance; a failed check is a signal to investigate, not always a
reason to reject data automatically.

| Check | What it inspects |
| --- | --- |
| [APERO start](apero_start) | Whether APERO processing began for the observation. |
| [APERO end](apero_end) | Whether APERO processing reached its expected end state. |
| [ARI start](ari_start) | Whether the ARI monitoring workflow started. |
| [ARI end](ari_end) | Whether the ARI monitoring workflow completed. |
| [Blank](blank) | Whether an observation directory contains usable observation data. |
| [Calibration test](calib_test) | Presence of the required calibration data. |
| [COB test](cob_test) | Observation-block consistency checks. |
| [Has observation directory](has_obsdir) | Whether the expected observation directory is present. |
| [No science](no_sci) | Whether an observation has no science exposure to reduce. |
| [Quality test](qual_test) | General quality criteria for observation data. |
| [Critical test](critical_test) | Critical instrument or observation conditions. |
| [Critical science test](critical_sci_test) | Critical conditions affecting science exposures. |
| [Astrometry](astrom) | Whether target astrometry is available and usable. |
| [Low signal-to-noise](low_snr) | Whether signal-to-noise is below the expected range. |
| [Bad CCF](bad_ccf) | Cross-correlation-function quality indicators. |
| [Excess modal noise](excess_modal) | Excess modal-noise indicators in the spectra. |
| [Pixel shifts](pixel_shifts) | Detector or spectral pixel-shift anomalies. |
| [Previous reduction](prev_reduc) | Whether the observation has a previous successful reduction. |
| [Manual start](manual_start) | A manually recorded monitoring start marker. |
| [Manual end](manual_end) | A manually recorded monitoring end marker. |

## Engineering checks

Engineering checks inspect instrument telemetry and hardware state rather than
reduced science products.

| Check | What it inspects |
| --- | --- |
| [FP interior RMS](eng_fp_interior_rms) | Fabry-Pérot interior-region RMS. |
| [FP setpoint RMS](eng_fp_setpoint_rms) | Fabry-Pérot setpoint stability. |
| [FP exterior range](eng_fp_exterior_range) | Fabry-Pérot exterior-region range. |
| [Isolation valve state](eng_iso_valve_state) | Instrument isolation valve state. |
| [Scrambling state](eng_scrambling_state) | Scrambler state and telemetry. |
| [Stretcher state](eng_stretcher_state) | Fiber stretcher state. |
| [Turbopump state](eng_turbopump_state) | Turbopump state. |
| [Vacuum gauge upper](eng_vac_gauge_upper) | Upper vacuum-gauge limit. |
| [Cryostat 1 state](eng_cryo1_state) | Cryostat 1 state telemetry. |
| [Cryostat 2 state](eng_cryo2_state) | Cryostat 2 state telemetry. |
| [Cryostat 1 warning](eng_warn_cryo1) | Cryostat 1 warning telemetry. |
| [Cryostat 2 warning](eng_warn_cryo2) | Cryostat 2 warning telemetry. |
| [Backend error state](eng_backend_error_state) | Backend-reported engineering errors. |
| [Encoder heater maximum](eng_enc_heater_max) | Encoder-heater maximum telemetry. |
| [Encoder setpoint offset](eng_enc_setpoint_offset) | Encoder temperature setpoint offset. |
| [Encoder temperature RMS](eng_enc_temp_rms) | Encoder temperature stability. |
