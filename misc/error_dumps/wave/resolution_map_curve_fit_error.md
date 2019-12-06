Version 0.5.120


```
05:14:20.022- |apero_processing| 
05:14:20.033- |apero_processing| 
05:14:20.044- |apero_processing| ***************************************************************************
05:14:20.054- |apero_processing| 
05:14:20.065- |apero_processing| ***************************************************************************
05:14:20.076-@|apero_processing| W[40-503-00019]: Error found for ID='1120'
05:14:20.086-@|apero_processing| 	cal_wave_spirou.py 2019-06-21 -hcfiles 2426701c_pp.fits 2426702c_pp.fits -fpfiles 2426694a_pp.fits 2426695a_pp.fits 2426696a_pp.fits 2426697a_pp.fits 2426698a_pp.fits
05:14:20.097- |apero_processing| ***************************************************************************
05:14:20.107- |apero_processing| 
 E[09-017-00002]: Resolution map curve_fit error 
 	 <class 'TypeError'>: Improper input: N=5 must not exceed M=0 
 	 Function = science.calib.wave.py.generate_resolution_map()
 E[01-010-00001]: Unhandled error has occurred: Error <class 'apero.locale.core.drs_exceptions.LogExit'> 
 
 Traceback (most recent call last):
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/science/calib/wave.py", line 1997, in generate_resolution_map
    popt, pcov = mp.fit_gauss_with_slope(**fargs)
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/core/math/gauss.py", line 222, in fit_gauss_with_slope
    popt, pcov = curve_fit(gauss_fit_s, x, y, p0=guess)
  File "/scratch/bin/anaconda3/envs/spirou_py3/lib/python3.7/site-packages/scipy/optimize/minpack.py", line 751, in curve_fit
    res = leastsq(func, p0, Dfun=jac, full_output=1, **kwargs)
  File "/scratch/bin/anaconda3/envs/spirou_py3/lib/python3.7/site-packages/scipy/optimize/minpack.py", line 386, in leastsq
    raise TypeError('Improper input: N=%s must not exceed M=%s' % (n, m))
 TypeError: Improper input: N=5 must not exceed M=0
 
 During handling of the above exception, another exception occurred:
 
 Traceback (most recent call last):
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/core/core/drs_startup.py", line 292, in run
    llmain = func(recipe, params)
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/recipes/spirou/cal_wave_spirou.py", line 196, in __main__
    hc_e2ds_file, fiber)
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/science/calib/wave.py", line 469, in hc_wavesol
    wavell, ampll)
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/science/calib/wave.py", line 560, in hc_wavesol_ea
    llprops = generate_resolution_map(params, recipe, llprops, e2dsfile)
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/science/calib/wave.py", line 2001, in generate_resolution_map
    WLOG(params, 'error', TextEntry('09-017-00002', args=eargs))
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/core/core/drs_log.py", line 373, in __call__
    raise drs_exceptions.LogExit(errorstring)
 apero.locale.core.drs_exceptions.LogExit
```