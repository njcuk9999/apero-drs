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
    - check that cavity file from EA is same as one from Melissa (and combine filename)
    
## RV

- Need to convert `cal_CCF_spirou` (and FP -- merge into 1)
- Need to convert `cal_DRIFT_PEAK_spirou`?

## Polarisation

- Need to convert `pol_spirou`
- Need to add s1d polar outputs