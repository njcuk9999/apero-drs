Version: 0.5.120


```
E[01-010-00001]: Unhandled error has occurred: Error <class 'TypeError'> 

Traceback (most recent call last):
 File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/core/core/drs_startup.py", line 292, in run
   llmain = func(recipe, params)
 File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/tools/bin/apero_processing.py", line 133, in __main__
   group=groupname)
 File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/tools/module/setup/drs_processing.py", line 608, in process_run_list
   rdict = _multi_process1(params, recipe, runlist, cores, group)
 File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/tools/module/setup/drs_processing.py", line 1542, in _multi_process1
   pool.starmap(_linear_process, params_per_process)
 File "/scratch/bin/anaconda3/envs/spirou_py3/lib/python3.7/multiprocessing/pool.py", line 298, in starmap
   return self._map_async(func, iterable, starmapstar, chunksize).get()
 File "/scratch/bin/anaconda3/envs/spirou_py3/lib/python3.7/multiprocessing/pool.py", line 683, in get
   raise self._value
 File "/scratch/bin/anaconda3/envs/spirou_py3/lib/python3.7/multiprocessing/pool.py", line 457, in _handle_tasks
   put(task)
 File "/scratch/bin/anaconda3/envs/spirou_py3/lib/python3.7/multiprocessing/connection.py", line 206, in send
   self._send_bytes(_ForkingPickler.dumps(obj))
 File "/scratch/bin/anaconda3/envs/spirou_py3/lib/python3.7/multiprocessing/reduction.py", line 51, in dumps
   cls(buf, protocol).dump(obj)
TypeError: can't pickle module objects
```