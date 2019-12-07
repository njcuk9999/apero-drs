version: 0.6.001


```
21:57:31.437- |apero_processing| 
21:57:31.448- |apero_processing| 
21:57:31.460- |apero_processing| ***************************************************************************
21:57:31.489- |apero_processing| 
21:57:31.502- |apero_processing| ***************************************************************************
21:57:31.514-@|apero_processing| W[40-503-00019]: Error found for ID='686'
21:57:31.527-@|apero_processing| 	obj_fit_tellu_spirou.py 2019-04-20 2400486o_pp_e2dsff_AB.fits
21:57:31.540- |apero_processing| ***************************************************************************
21:57:31.554- |apero_processing| 
 E[00-002-00014]: Database Telluric. Error copying from
 	/scratch2/spirou/mini_data/reduced/2019-04-20/2400486o_pp_e2dsff_recon_AB.fits
 	to /scratch2/spirou/mini_data/telluDB/2400486o_pp_e2dsff_recon_AB.fits
 Error <class 'FileNotFoundError'>: [Errno 2] No such file or directory:
 	'/scratch2/spirou/mini_data/reduced/2019-04-20/2400486o_pp_e2dsff_recon_AB.fits'
 	 Function = core.core.drs_database.py._copy_file()
 E[01-010-00001]: Unhandled error has occurred: Error <class 'apero.locale.core.drs_exceptions.LogExit'> 
 
 Traceback (most recent call last):
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/core/core/drs_database.py", line 717, in locked_copy
    shutil.copyfile(inpath, outpath)
  File "/scratch/bin/anaconda3/envs/spirou_py3/lib/python3.7/shutil.py", line 120, in copyfile
    with open(src, 'rb') as fsrc:
 FileNotFoundError: [Errno 2] No such file or directory: '/scratch2/spirou/mini_data/reduced/2019-04-20/2400486o_pp_e2dsff_recon_AB.fits'
 
 During handling of the above exception, another exception occurred:
 
 Traceback (most recent call last):
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/core/core/drs_startup.py", line 293, in run
    llmain = func(recipe, params)
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/recipes/spirou/obj_fit_tellu_spirou.py", line 299, in __main__
    drs_database.add_file(params, reconfile)
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/core/core/drs_database.py", line 340, in add_file
    _copy_db_file(params, dbname, inpath, abs_outpath)
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/core/core/drs_database.py", line 729, in _copy_db_file
    locked_copy()
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/io/drs_lock.py", line 331, in wrapperfunc
    return func(*args, **kw)
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/core/core/drs_database.py", line 722, in locked_copy
    WLOG(params, 'error', TextEntry('00-002-00014', args=eargs))
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/core/core/drs_log.py", line 373, in __call__
    raise drs_exceptions.LogExit(errorstring)
 apero.locale.core.drs_exceptions.LogExit

```

```
21:57:31.570- |apero_processing| 
21:57:31.583- |apero_processing| 
21:57:31.596- |apero_processing| ***************************************************************************
21:57:31.608- |apero_processing| 
21:57:31.620- |apero_processing| ***************************************************************************
21:57:31.633-@|apero_processing| W[40-503-00019]: Error found for ID='691'
21:57:31.646-@|apero_processing| 	obj_fit_tellu_spirou.py 2019-04-20 2400489o_pp_e2dsff_AB.fits
21:57:31.659- |apero_processing| ***************************************************************************
21:57:31.672- |apero_processing| 
 E[00-002-00014]: Database Telluric. Error copying from
 	/scratch2/spirou/mini_data/reduced/2019-04-20/2400489o_pp_e2dsff_recon_AB.fits
 	to /scratch2/spirou/mini_data/telluDB/2400489o_pp_e2dsff_recon_AB.fits
 Error <class 'FileNotFoundError'>: [Errno 2] No such file or directory:
 	'/scratch2/spirou/mini_data/reduced/2019-04-20/2400489o_pp_e2dsff_recon_AB.fits'
 	 Function = core.core.drs_database.py._copy_file()
 E[01-010-00001]: Unhandled error has occurred: Error <class 'apero.locale.core.drs_exceptions.LogExit'> 
 
 Traceback (most recent call last):
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/core/core/drs_database.py", line 717, in locked_copy
    shutil.copyfile(inpath, outpath)
  File "/scratch/bin/anaconda3/envs/spirou_py3/lib/python3.7/shutil.py", line 120, in copyfile
    with open(src, 'rb') as fsrc:
 FileNotFoundError: [Errno 2] No such file or directory: '/scratch2/spirou/mini_data/reduced/2019-04-20/2400489o_pp_e2dsff_recon_AB.fits'
 
 During handling of the above exception, another exception occurred:
 
 Traceback (most recent call last):
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/core/core/drs_startup.py", line 293, in run
    llmain = func(recipe, params)
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/recipes/spirou/obj_fit_tellu_spirou.py", line 299, in __main__
    drs_database.add_file(params, reconfile)
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/core/core/drs_database.py", line 340, in add_file
    _copy_db_file(params, dbname, inpath, abs_outpath)
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/core/core/drs_database.py", line 729, in _copy_db_file
    locked_copy()
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/io/drs_lock.py", line 331, in wrapperfunc
    return func(*args, **kw)
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/core/core/drs_database.py", line 722, in locked_copy
    WLOG(params, 'error', TextEntry('00-002-00014', args=eargs))
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/core/core/drs_log.py", line 373, in __call__
    raise drs_exceptions.LogExit(errorstring)
 apero.locale.core.drs_exceptions.LogExit
```


```
21:57:31.686- |apero_processing| 
21:57:31.698- |apero_processing| 
21:57:31.709- |apero_processing| ***************************************************************************
21:57:31.721- |apero_processing| 
21:57:31.733- |apero_processing| ***************************************************************************
21:57:31.746-@|apero_processing| W[40-503-00019]: Error found for ID='756'
21:57:31.758-@|apero_processing| 	obj_fit_tellu_spirou.py 2019-05-15 2413066o_pp_e2dsff_AB.fits
21:57:31.770- |apero_processing| ***************************************************************************
21:57:31.782- |apero_processing| 
 E[00-002-00014]: Database Telluric. Error copying from
 	/scratch2/spirou/mini_data/reduced/2019-05-15/2413066o_pp_e2dsff_recon_AB.fits
 	to /scratch2/spirou/mini_data/telluDB/2413066o_pp_e2dsff_recon_AB.fits
 Error <class 'FileNotFoundError'>: [Errno 2] No such file or directory:
 	'/scratch2/spirou/mini_data/reduced/2019-05-15/2413066o_pp_e2dsff_recon_AB.fits'
 	 Function = core.core.drs_database.py._copy_file()
 E[01-010-00001]: Unhandled error has occurred: Error <class 'apero.locale.core.drs_exceptions.LogExit'> 
 
 Traceback (most recent call last):
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/core/core/drs_database.py", line 717, in locked_copy
    shutil.copyfile(inpath, outpath)
  File "/scratch/bin/anaconda3/envs/spirou_py3/lib/python3.7/shutil.py", line 120, in copyfile
    with open(src, 'rb') as fsrc:
 FileNotFoundError: [Errno 2] No such file or directory: '/scratch2/spirou/mini_data/reduced/2019-05-15/2413066o_pp_e2dsff_recon_AB.fits'
 
 During handling of the above exception, another exception occurred:
 
 Traceback (most recent call last):
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/core/core/drs_startup.py", line 293, in run
    llmain = func(recipe, params)
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/recipes/spirou/obj_fit_tellu_spirou.py", line 299, in __main__
    drs_database.add_file(params, reconfile)
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/core/core/drs_database.py", line 340, in add_file
    _copy_db_file(params, dbname, inpath, abs_outpath)
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/core/core/drs_database.py", line 729, in _copy_db_file
    locked_copy()
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/io/drs_lock.py", line 331, in wrapperfunc
    return func(*args, **kw)
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/core/core/drs_database.py", line 722, in locked_copy
    WLOG(params, 'error', TextEntry('00-002-00014', args=eargs))
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/core/core/drs_log.py", line 373, in __call__
    raise drs_exceptions.LogExit(errorstring)
 apero.locale.core.drs_exceptions.LogExit

```

```
21:57:31.797- |apero_processing| 
21:57:31.808- |apero_processing| 
21:57:31.820- |apero_processing| ***************************************************************************
21:57:31.831- |apero_processing| 
21:57:31.843- |apero_processing| ***************************************************************************
21:57:31.855-@|apero_processing| W[40-503-00019]: Error found for ID='765'
21:57:31.868-@|apero_processing| 	obj_fit_tellu_spirou.py 2019-06-15 2425698o_pp_e2dsff_AB.fits
21:57:31.880- |apero_processing| ***************************************************************************
21:57:31.892- |apero_processing| 
 E[00-002-00014]: Database Telluric. Error copying from
 	/scratch2/spirou/mini_data/reduced/2019-06-15/2425698o_pp_e2dsff_tcorr_AB.fits
 	to /scratch2/spirou/mini_data/telluDB/2425698o_pp_e2dsff_tcorr_AB.fits
 Error <class 'FileNotFoundError'>: [Errno 2] No such file or directory:
 	'/scratch2/spirou/mini_data/reduced/2019-06-15/2425698o_pp_e2dsff_tcorr_AB.fits'
 	 Function = core.core.drs_database.py._copy_file()
 E[01-010-00001]: Unhandled error has occurred: Error <class 'apero.locale.core.drs_exceptions.LogExit'> 
 
 Traceback (most recent call last):
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/core/core/drs_database.py", line 717, in locked_copy
    shutil.copyfile(inpath, outpath)
  File "/scratch/bin/anaconda3/envs/spirou_py3/lib/python3.7/shutil.py", line 120, in copyfile
    with open(src, 'rb') as fsrc:
 FileNotFoundError: [Errno 2] No such file or directory: '/scratch2/spirou/mini_data/reduced/2019-06-15/2425698o_pp_e2dsff_tcorr_AB.fits'
 
 During handling of the above exception, another exception occurred:
 
 Traceback (most recent call last):
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/core/core/drs_startup.py", line 293, in run
    llmain = func(recipe, params)
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/recipes/spirou/obj_fit_tellu_spirou.py", line 297, in __main__
    drs_database.add_file(params, corrfile)
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/core/core/drs_database.py", line 340, in add_file
    _copy_db_file(params, dbname, inpath, abs_outpath)
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/core/core/drs_database.py", line 729, in _copy_db_file
    locked_copy()
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/io/drs_lock.py", line 331, in wrapperfunc
    return func(*args, **kw)
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/core/core/drs_database.py", line 722, in locked_copy
    WLOG(params, 'error', TextEntry('00-002-00014', args=eargs))
  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/core/core/drs_log.py", line 373, in __call__
    raise drs_exceptions.LogExit(errorstring)
 apero.locale.core.drs_exceptions.LogExit
```

