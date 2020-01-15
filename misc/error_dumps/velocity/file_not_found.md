version 0.6.001:


```
21:57:31.906- |apero_processing| 
21:57:31.918- |apero_processing| 
21:57:31.929- |apero_processing| ***************************************************************************
21:57:31.940- |apero_processing| 
21:57:31.950- |apero_processing| ***************************************************************************
21:57:31.962-@|apero_processing| W[40-503-00019]: Error found for ID='844'
21:57:31.973-@|apero_processing| 	cal_ccf_spirou.py 2019-04-17 2399950o_pp_e2dsff_tcorr_AB.fits
21:57:31.983- |apero_processing| ***************************************************************************
21:57:31.994- |apero_processing| 
 E[01-001-00012]: Read Error: File '2399950o_pp_e2dsff_C.fits' could not be
 	found in directory '/scratch2/spirou/mini_data/reduced/2019-04-17'.
 	 function = io.drs_fits.py.read()
 E[01-010-00001]: Unhandled error has occurred: Error <class 'apero.locale.core.drs_exceptions.LogExit'> 
 
 Traceback (most recent call last):
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/core/core/drs_startup.py", line 293, in run
    llmain = func(recipe, params)
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/recipes/spirou/cal_ccf_spirou.py", line 201, in __main__
    infile_r = velocity.locate_reference_file(params, recipe, infile)
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/science/velocity/general.py", line 603, in locate_reference_file
    outfile.read()
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/core/core/drs_file.py", line 1321, in read
    fmt=fmt, ext=ext)
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/io/drs_fits.py", line 265, in read
    WLOG(params, 'error', TextEntry('01-001-00012', args=eargs))
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/core/core/drs_log.py", line 373, in __call__
    raise drs_exceptions.LogExit(errorstring)
 apero.locale.core.drs_exceptions.LogExit
```