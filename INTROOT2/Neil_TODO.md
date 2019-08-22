# TODO: SpirouDRS --> Terrapipe


## General

- Add blaze, flat, wave files to options
- need to add `obj_spec` recipe
- need to add `obj_pol` recipe
- need to add all plots
    - Some way to turn off/on indiviudal plots
- Summary PDF - QC + plots
- background still over correcting?
- need to add `cal_validate spirou`
- need to add user setup scripts
- need to get data separately from the drs
- need to add new instrument installation script
- need to save outputs like CFHT does (and have script to return to drs standards)
- need to write documentation

## localisation

- Need to add QC for gradient x and y always positive

## flat

- Need to add Etiennes sinc function fitting to blaze

##  Wave solution

- Finish converting `cal_wave_spirou.py` from SpirouDrs
    - problem with constants `WAVE_HC_N_ORD_START`, `WAVE_HC_N_ORD_START`, `WAVE_N_ORD_START`
    - need to add cavity constants to defaults
    - need fp constants in header (how do we deal with different constants for modes?)
    - need to separate `fp_wavesol_lovis` into different functions (too much to handle in one)
    - need to add join_orders
    - need to add FP CCF computation
    - need to add FP QC
    - need to add FP file writing
    - need to add calibDB update
    - check that cavity file from EA is same as one from Melissa (and combine filename)
    
## tellurics

- Need to convert `obj_mk_tellu`
    - start from e2ds or pp?
    - need to make sure we have s1d for trans
- Need to convert `obj_fit_tellu`
    - start from e2ds or pp?
    - need to make sure we have s1d for correct + recon
- Need to convert `obj_mk_obj_template`
    - rename to `obj_mk_template`
    - need to add s1d for template
- Need to convert `obj_mk_tellu_db`
- Need to convert `obj_fit_tellu_db`

## RV

- Need to convert `cal_CCF_spirou` (and FP -- merge into 1)
- Need to convert `cal_DRIFT_PEAK_spirou`?

## Polarisation

- Need to convert `pol_spirou`
- Need to add s1d polar outputs