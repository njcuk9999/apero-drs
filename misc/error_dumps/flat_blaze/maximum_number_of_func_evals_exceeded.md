Version: V0.5.120

```
05:14:19.153- |apero_processing| 
05:14:19.164- |apero_processing| 
05:14:19.175- |apero_processing| ***************************************************************************
05:14:19.185- |apero_processing| 
05:14:19.196- |apero_processing| ***************************************************************************
05:14:19.206-@|apero_processing| W[40-503-00019]: Error found for ID='981'
05:14:19.217-@|apero_processing| 	cal_flat_spirou.py 2019-04-22 2401029f_pp.fits 2401030f_pp.fits 2401031f_pp.fits 2401032f_pp.fits 2401033f_pp.fits
05:14:19.227- |apero_processing| ***************************************************************************
05:14:19.238- |apero_processing| 
 E[01-010-00001]: Unhandled error has occurred: Error <class 'RuntimeError'> 
 
 Traceback (most recent call last):
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/core/core/drs_startup.py", line 292, in run
    llmain = func(recipe, params)
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/recipes/spirou/cal_flat_spirou.py", line 189, in __main__
    nframes, props, kind='flat', fiber=fiber)
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/science/extract/extraction.py", line 172, in extraction_twod
    fout = flat_blaze.calculate_blaze_flat_sinc(*fargs)
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/science/calib/flat_blaze.py", line 159, in calculate_blaze_flat_sinc
    p0=fit_guess, bounds=bounds)
  File "/scratch/bin/anaconda3/envs/spirou_py3/lib/python3.7/site-packages/scipy/optimize/minpack.py", line 765, in curve_fit
    raise RuntimeError("Optimal parameters not found: " + res.message)
 RuntimeError: Optimal parameters not found: The maximum number of function evaluations is exceeded.
```
