Version: V0.5.120

```
05:14:18.896- |apero_processing| 
05:14:18.906- |apero_processing| ***************************************************************************
05:14:18.916-@|apero_processing| W[40-503-00019]: Error found for ID='833'
05:14:18.927-@|apero_processing| 	cal_preprocess_spirou.py 2019-06-21 2426791f.fits
05:14:18.938- |apero_processing| ***************************************************************************
05:14:18.949- |apero_processing| 
Expected error occurred in run '833'

E[01-001-00014]: Read Error: Fits-Image (data) could not be read. 

	 Filename = /scratch2/spirou/mini_data/raw/2019-06-21/2426791f.fits, Ext = 0 

	 Error was type <class 'TypeError'> 



 Traceback (most recent call last):

  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/io/drs_fits.py", line 360, in _read_fitsimage

    data = fits.getdata(filename, ext=ext)

  File "/scratch/bin/anaconda3/envs/spirou_py3/lib/python3.7/site-packages/astropy/io/fits/convenience.py", line 196, in getdata

    data = hdu.data

  File "/scratch/bin/anaconda3/envs/spirou_py3/lib/python3.7/site-packages/astropy/utils/decorators.py", line 744, in __get__

    val = self.fget(obj)

  File "/scratch/bin/anaconda3/envs/spirou_py3/lib/python3.7/site-packages/astropy/io/fits/hdu/image.py", line 230, in data

    data = self._get_scaled_image_data(self._data_offset, self.shape)

  File "/scratch/bin/anaconda3/envs/spirou_py3/lib/python3.7/site-packages/astropy/io/fits/hdu/image.py", line 696, in _get_scaled_image_data

    raw_data = self._get_raw_data(shape, code, offset)

  File "/scratch/bin/anaconda3/envs/spirou_py3/lib/python3.7/site-packages/astropy/io/fits/hdu/base.py", line 508, in _get_raw_data

    return self._file.readarray(offset=offset, dtype=code, shape=shape)

  File "/scratch/bin/anaconda3/envs/spirou_py3/lib/python3.7/site-packages/astropy/io/fits/file.py", line 334, in readarray

    buffer=self._mmap)

TypeError: buffer is too small for requested array
```




```
05:14:18.962- |apero_processing| 
05:14:18.972- |apero_processing| 
05:14:18.983- |apero_processing| ***************************************************************************
05:14:18.993- |apero_processing| 
05:14:19.004- |apero_processing| ***************************************************************************
05:14:19.014-@|apero_processing| W[40-503-00019]: Error found for ID='836'
05:14:19.024-@|apero_processing| 	cal_preprocess_spirou.py 2019-06-21 2426794f.fits
05:14:19.035- |apero_processing| ***************************************************************************
05:14:19.045- |apero_processing| 
Expected error occurred in run '836'

E[01-001-00014]: Read Error: Fits-Image (data) could not be read. 

	 Filename = /scratch2/spirou/mini_data/raw/2019-06-21/2426794f.fits, Ext = 0 

	 Error was type <class 'TypeError'> 



 Traceback (most recent call last):

  File "/scratch/Projects/spirou/drs/spirou_github/spirou_run/apero/io/drs_fits.py", line 360, in _read_fitsimage

    data = fits.getdata(filename, ext=ext)

  File "/scratch/bin/anaconda3/envs/spirou_py3/lib/python3.7/site-packages/astropy/io/fits/convenience.py", line 196, in getdata

    data = hdu.data

  File "/scratch/bin/anaconda3/envs/spirou_py3/lib/python3.7/site-packages/astropy/utils/decorators.py", line 744, in __get__

    val = self.fget(obj)

  File "/scratch/bin/anaconda3/envs/spirou_py3/lib/python3.7/site-packages/astropy/io/fits/hdu/image.py", line 230, in data

    data = self._get_scaled_image_data(self._data_offset, self.shape)

  File "/scratch/bin/anaconda3/envs/spirou_py3/lib/python3.7/site-packages/astropy/io/fits/hdu/image.py", line 696, in _get_scaled_image_data

    raw_data = self._get_raw_data(shape, code, offset)

  File "/scratch/bin/anaconda3/envs/spirou_py3/lib/python3.7/site-packages/astropy/io/fits/hdu/base.py", line 508, in _get_raw_data

    return self._file.readarray(offset=offset, dtype=code, shape=shape)

  File "/scratch/bin/anaconda3/envs/spirou_py3/lib/python3.7/site-packages/astropy/io/fits/file.py", line 334, in readarray

    buffer=self._mmap)

TypeError: buffer is too small for requested array
```

