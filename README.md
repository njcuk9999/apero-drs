# SPIRou DRS in python 3

<img src="./documentation/Figures/Logo_SPIRou-22.jpg" alt="Drawing" style="width:128px;"/>

# User manual

![User manual page](./documentation/User_guide_spirou_drs.pdf "User manual page")

## Download here:

![User manual download](https://github.com/njcuk9999/spirou_py3/raw/master/documentation/User_guide_spirou_drs.pdf "User manual pdf download")

# Developer manual

![Dev manual page](./documentation/Dev_guide_spirou_drs.pdf "Developer manual page")

## Download here: 

![Dev manual download](https://github.com/njcuk9999/spirou_py3/raw/master/documentation/Dev_guide_spirou_drs.pdf "Developer manual pdf download")

<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>

# Quick manual


## Table of Contents
1. [Installation process](#1-installation-process)

2. [Change log from Version 43 of the Drs](#2-change-log-from-version-43-of-the-drs)

    2.1 [General](#21-general)

    2.2 [cal_DARK_spirou](#22-cal_dark_spiroupy)

    2.3 [cal_loc_RAW_spirou](#23-cal_loc_raw_spiroupy)

    2.4 [cal_SLIT_spirou](#24-cal_slit_spiroupy)
    
    2.5 [cal_FF_RAW_spirou](#25-cal_ff_raw_spiroupy)
    
    2.6 [cal_extract_RAW_spirou](#26-cal_extract_raw_spiroupy)
    
    2.7 [cal_DRIFT_RAW_spirou](#27-cal_drift_raw_spiroupy)

    2.8 [cal_BADPIX_spirou](#28-cal_badpix_spiroupy)

3. [Timing](#3-timing)

    3.1 [Full unit test in python 3](#31-full-unit-test-in-python-3)
    
    3.2 [Full unit test in python 2](#32-full-unit-test-python-2)
    
    3.3 [Full unit test in AT4 V46](#33-full-unit-test-at4-v46)

4. [Progress](#4-progress)


- - - -

## 1 Installation process

- - - -

- Prerequisites: latest version of anaconda (python 2 or python 3)

- Step 1: Download this repository (say to directory at /home/user/spirou_drs/INTROOT)

- Step 2: Add download path to your PYTHONPATH environmental variable
    ```bash
    export PYTHONPATH=/home/user/spirou_drs/INTROOT/:$PYTHONPATH
    ```

- Step 3: Add download /bin path to your PATH environmental variable
    ```bash
    export PYTHON=/home/user/spirou_drs/INTROOT/bin/:$PATH
    ```

- Step 4a: If you want to run files as executables run `chmod +x` on all files in /bin/ folder
    - One can then run codes as `cal_DARK_spirou.py NIGHTNAME [files]`

- Step 4b: To run from python or ipython
    - start up 
    ```bash
    ipython
    ```  
  - type 
    ```python
    run cal_DARK_spirou NIGHTNAME [files]
    ```

- Step 4c: To run from python scription
    - in a python code:
    ```python
    import cal_DARK_spirou
    
    NIGHTNAME = '20170710'
    FILES = ['dark_dark02d406.fits']
  
    cal_DARK_spirou.main(night_name=NIGHTNAME, files=FILES)
    ```

- Extra steps
    - Currently due to the set up of calibDB all dates (TILT, LOC_AB, LOC_C etc) must be acquired earlier than (or equal to) the file defined at run time (FILES). Therefore codes will crash if this is not the case. To fix this just edit both the human formatted time and the unix time to be older than that of the file defined at run time
        
        - open /data/calibDB/master_calib_SPIROU.txt
        
        - set all files date to ```2000-01-01 00:00:00.00 946684800```
        
        - i.e. ```DARK 20170710 dark_dark02d406.fits 2000-01-01 00:00:00.00 946684800```

    - Currently no wave solution is generated and has to be added manually to the calibDB file
    
        - open /data/calibDB/master_calib_SPIROU.txt
        
        - add row: ```WAVE 20170710 spirou_wave_ini3.fits 2000-01-01 00:00:00.00 946684800```

        - put ```spirou_wave_ini3.fits``` in the data/calibDB/ directory

- - - -

## 2 Change log from Version 43 of the DRS

- - - -

### 2.1 General

- all import functions re-worked (removed or changed or updated)

- all recipes main body of code is now in a `main()` function and called in `__main__`
    - This allows recipes to be called as functions 
    - i.e. in python for cal_DARK_spirou.py:
        ```python
        import cal_DARK_spirou
            
        files = ['dark_dark02d406.fits']
        night_name = '20170710'
        cal_DARK_spirou.main(night_name=night_name, files=files)
    
        ```
        Will run the exact same procedure as:
        ```bash
        cal_DARK_spirou.py 201707 dark_dark02d406.fits
        ```

- `WLOG` function overhaul (now in `spirouCore.spirouLog.logger)`
    - `WLOG(key, option, message)` or `logger(key, option, message)`
    - produces print out (to log and console) of the following:
        `HH:MM:SS - trigger |option|message`
    - keys allowed are set in `spirouConfig.spirouConfig` as a dictionary
        - `all`   displays ' ' in the trigger column
        - `error`  displays '!' in the trigger column
            - will exit if `spirouConfig.spirouConfig.EXIT` is set
            - via `sys.exit(1)` (soft exit) if `EXIT = 'sys'`
            - via `os._exit(1)` (hard exit) if `EXIT = 'os'`
            - else will not exit on error triggered (*NOT RECOMMENDED*)
        - `warning` displays '@' in the trigger column
        - `info` displays '*' in the trigger column
        - `graph` displays '~' in the trigger column
        ```python
        from SpirouDRS import spirouCore
        
        WLOG = spirouCore.wlog
        
        WLOG('all', 'Program', 'This produces a normal message')

        >>> HH:MM:DD -   | Program | This produces a warning

        
        WLOG('warning', 'Program', 'This produces a warning')

        >>> HH:MM:DD - @ | Program | This produces a warning

        
        WLOG('info', 'Program', 'This produces an info message')

        >>> HH:MM:DD - * | Program | This produces an info message

        
        WLOG('graph', 'Program', 'This produces a graph message')

        >>> HH:MM:DD - ~ | Program | This produces a graph message

        
        WLOG('error', 'Program', 'This produces an error')

        >>> HH:MM:DD - ! | Program | This produces an error
        >>> sys.exit(1) or os._exit(1) or None
        ```

- execution of pythonstartup codes removed and replaced with functions
    - `spirouCore.RunInitialStartup()` to replace `execfile(os.getenv('PYTHONSTARTUP))`
    - `spirouCore.RunStartup` to replace `execfile(os.getenv('PYTHONSTARTUP2))`

- loading of many variables into python memory replaced with parameter dictionary containing all variables
    - This includes all variables loaded into memory by `startup.py` and `startup_recipes.py`
    - Loading many variables from many codes into memory is dangerous as any variable can be overwritten/previously defined.

- *ParamDict* is a custom dictionary that has all the normal features of a python dictionary but has one extra feature that the "source" of the parameter can be defined.
    - This is used to set the source (the program and function where the parameter was defined)
    - This means at any point after this the place where any parameter was created can be checked (be it a program, a function or a config file - with all programs/functions/files named in the source)
    - `ParamDict` is constructed/initiated like a python dictionary
        - `x = ParamDict()`  or `y = ParamDict(zip(keys, values))`
    - Set functions are defined to allow setting the source
        - `set_source(key, source)`
            - key is a string
            - source is a string
            ```python
            x = ParamDict()
            x['version'] = 1.0.0
            x.set_source('version', '/home/user/config.txt')
            ```
        - `set_sources(keys, sources)`
            - keys is a string
            - sources can be a list or a string)
            ```python
            x = ParamDict()
            x['a'] = 1
            x['b'] = 2
            x['c'] = 3
            sources = ['a.py', 'b.py', 'c.py']
            x.set_sources(['a' 'b', 'c'], sources)
            ```
        - `set_all_sources(source)`
            - source is a string
            - will override all previous sources
            ```python
            x = ParamDict()
            x['a'] = 1
            x['b'] = 2
            x['c'] = 3
            x.set_all_sources('/home/user/config.txt')
            ```
    - Get function are defined and a dictionary of sources can be accessed
        - `get_source(key)`
            - key is a string
            - returns the source (as a string)
            ```python
            x = ParamDict()                  
            x['version'] = 1.0.0
            x.set_source('version', '/home/user/config.txt')
            xsource = x.get_source('version')
            ```
        - `sources`
            - returns a dictionary with all the sources in (keys are identical to `x.keys()`)
            ```python
                x = ParamDict()
                x['a'] = 1
                x['b'] = 2
                x['c'] = 3
                sources = ['a.py', 'b.py', 'c.py']
                x.set_sources(['a' 'b', 'c'], sources)
                allsources = x.sources
            ```
           
- all hard coded constants (i.e. ints/floats/strings) that may be changed moved into config files
    - `config.txt` - This contains all the variables previously defined as environmental variables
        - i.e. this will allow functionality across platforms and avoid having many variables defined in the environment (fine for a dedicated machine but a nightmare for anyone else)
    - `hadmrICDP_SPIROU.txt` - final location can be changed by all other variables are currently in this file (loaded in previous versions as a python code loading variables into the memory). This is dangerous as any variable can be overwritten/previously defined.

- *ConfigError* overrides *ConfigException* - new classes to handle errors due to the config file or calling a config parameter from config file (also used in *ParamDict*)
    - Most importantly interacts nicely with WLOG() function (in `spirouCore.spirouLog`)
    - Use is as follows:
        ```python
        def a_function():
            try:
                # some_code that causes an exception
                x = dict()
                y = x['a']
                return y
            except KeyError:
                # define a log message
                message = 'a was not found in dictionary x'
                raise ConfigError(message, level='error')

        # Main code:
        try:
            a_function()
        except ConfigError as e:
            WLOG(e.level, 'program', e.message)
        ```
    - as well as a message (stored in `e.message`) a level can also be set, which in turn can be used in `WLOG` function (recall with WLOG is `level=error` the code will exit)
        
- moved resizing of image to function
    - `spirouImage.ResizeImage(data, xlow, xhigh, ylow, yhigh)`

- plots are now only plotted if `DRS_PLOT` is True (or =1)
    - Can turn plotting off in `config.txt` =0 or =False

[Back to top](#table-of-contents)


- - - -

### 2.2 cal_DARK_spirou.py

- dark measurement moved to internal function `measure_dark` (for clarity)
     - This is, in part, due to the repetition of code for "Whole det", "Blue part" and "Red part"

- all plotting moved to internal functions (for clarity)
    - `sPlt.plot_image_and_regions(p, data)` for the image/region plot
    - `sPlt.plot_datacut` for the DARK > cutlimit plot
    - `SPlt.plot_hisotgrams` for the histogram plots 
    - `sPlt` is import alias for `spirouCore.spirouPlot`
    
- histogram plot updated
    - original plot plotted bin centers as a smooth peak, simple modification to make sure histogram bars are present
    
- writing of data is sped up by caching all HEADER keys and writing to file **once** with the write of the data.

- *speed up*

	- AT-4 v44: 4.88102817535 seconds
	
	- py3: 1.8896541595458984 seconds


[Back to top](#table-of-contents)

- - - -

### 2.3 cal_loc_RAW_spirou.py


- added function to convert from ADU/s to electrons
    - `spirouImage.ConvertToE(image)`
    
- added function to flip image
    - `spirouImage.FlipImage(image)`

- smoothed image (by a box) is now in a function (creates order_profile)
    - added different way to calculate order_profile - currently set to 'manual' be default
    - `spirouLOCOR.BoxSmoothedImage(image, size, weighted=True, mode='convolve')` 
        - Instead of manually working out the mean for each box you convolve the weighted image with a tophat function and the weights with a topcat function and then divide the two.
        - This gives approximately the same result (with small deviations due to the FT of a topcat function not being perfect).
        - The function can be turned back to the original 'manual' mode by using `mode='manual'` but is slower ()by a factor of ~x8)
        - The figure below shows the differences (To view interactively use: `spirouLOCOR.__test_smoothed_boxmean_image(image, size)`).
            ![picture alt](./documentation/Figures/OrderProfileCreation_convolve_vs_manual.jpg "Produced by running spirouLOCOR.__test_smoothed_boxmean_image")

- added storage dictionary to store (and pass around) all variables created
    - `loc` - a Parameter dictionary (thus source can be set for all variables to keep track of them)

- added function to measure background and get central pixel positions
    - `spirouLOCOR.MeasureBkgrdGetCentPixs(p, loc, image)`

- debug plot added to plot the minimum of `ycc` and `ic_locseuil`
    - `sPlt.debug_locplot_min_ycc_loc_threshold(p, loc['ycc'])`

- added function for locating central position (previously `spirouLOCOR.poscolc`) - currently set to 'manual' be default
    - `.LocateCentralOrderPositions(cvalues, threshold, mode='convolve')` 
        - Instead of manually working out the starts and ends of each order (with while loops) convolves a mask of cvalues > threshold with a top-hat (size=3) function such that all edges are found
        - i.e. `[False, True, True]` or `[True, True, False]` give a different value than `[True, True, True]` or `[False, False, False]` or `[False, False, True]`
        - i.e. the convolution gives the sum of three elements, thus selected those elements with a sum of 2 give our edges
        - The function can be turned back to the original 'manual' mode by using `mode='manual` but is slower (by a factor of x2)

- debug plot added to plot the image above saturation threshold
    - `sPlt.locplot_im_sat_threshold(image, threshold)`
        
- moved `ctro`,`sigo`,`ac`,`ass` etc into loc (for storage and ease of use)        
        
- the fit across each order has been split into functions
    - the initial fit is done by `spirouLOCOR.InitialOrderFit(p, loc, mask, order_num, rorder_num, kind)`
        - This initial fit takes in the plotting args and thus as order is fit the fit is piped on to plot via `sPlt.locplot_order`
    - the sigma clipping fit is done by `spirouLOCOR.SigClipOrderFit(p, loc, mask, order_num, rorder_num, kind)`
    - kind is used to change between 'center' and 'fwhm' fits (thus function is reused in both cases), kind will do the tiny bits of code which are different for each fit
    - all fit parameters are loaded into the `loc` parameter dictionary

- plot of order number against rms is move to `sPlt`
    - `sPlt.locplot_order_number_against_rms(p, loc, rorder_num)`

- function created to add the 2Dlist (i.e. the coefficients) to hdict (the dictionary used to save keys to so that we only write to the fits file once)

- superimposed fit on the image is pushed into a function
    - this is many times faster than before - due to optimisation
    - `spirouLOCOR.imageLocSuperimp(image, coefficients_of_fit)`

- Writing of fits file cleaned up (header keywords written during data write)

- *speed up*

	- AT-4 v44: 5.69740796089 seconds
	
    - py3:  2.2549290657043457 seconds



[Back to top](#table-of-contents)

- - - -

### 2.4 cal_SLIT_spirou.py

- added storage dictionary to store (and pass around) all variables created
    - `loc` - a Parameter dictionary (thus source can be set for all variables to keep track of them)

- Retrieval of coefficients from `_loco_` file moved to `spirouLOCOR.GetCoeffs`

- Tilt finding is moved to function `spirouImage.GetTilt(p, loc, image)`

- Fitting the tilt is moved to function `spirouImage.FitTilt(p, loc, image)`

- selected order plot moved to `sPlt.slit_sorder_plot(o, loc, image)`

- slit tilt angle and fit plot moved to `sPlt.slit_tilt_angle_and_fit_plot(p, loc)`

- Writing of fits file cleaned up (header keywords written during data write)

- *speed up*

    - AT-4 v44: 11.0713419914 seconds
    
    - py3: 4.385987043380737 seconds


[Back to top](#table-of-contents)

- - - -

### 2.5 cal_FF_RAW_spirou.py

- added function to replace measure_bkgr_FF, but incomplete (not currently used)
    - would need to convert interpol.c to python (spline fitting)

- added storage dictionary to store (and pass around) all variables created
    - `loc` - a Parameter dictionary (thus source can be set for all variables to keep track of them)

- Created function to read TILT file from calibDB (replaces `readkeyloco`)
    - `spirouImage.ReadTiltFile(p, hdr)`
    - takes in header dictionary from `fitsfilename` in order to avoid re-opening FITS rec (acqutime used in calibDB to get max_time of calibDB entry) 

- Created function to read order profile (replaces `read_data_raw` + pre-amble)
    - `spirouImage.ReadOrderProfile(p, hdr)`
    - takes in header dictionary from `fitsfilename` in order to avoid re-opening FITS rec (acqutime used in calibDB to get max_time of calibDB entry) 

- Used `spirouLOCOR.GetCoeffs(p, hdr, loc=loc)` to get the coefficients from file

- Created merge coefficients function to perform AB coefficient merge
    - `spirouLOCOR.MergeCoefficients`
    
- Updated extraction function `spirouEXTOR.ExtracTiltWeightOrder2()` - much faster as takes many of the calculations outside the pixel loop
    - (i.e. calculating the pixel contribution due to tilt in array `ww`).
        - `ww` is constant for an order, thus doesn't need to be worked out for each pixel in one order, just the multiplication between ww and the image
    - up to 8 times faster with these improvements

- `e2ds`, `SNR`, `RMS`, `blaze` and `flat` are stored in `loc` parameter dictionary

- Plotting code moved to `spirouCore.spirouPlot` functions

- Writing of fits file cleaned up (header keywords written during data write)

- QC (max_signal > qc_max_signal * nbframes) moved to end, however in old code it is not used as a failure criteria so also not used to fail in new code

- **speed up*

    - AT-4 v44: 25.9624619484 seconds
    
    - py3: 4.675365924835205 seconds



[Back to top](#table-of-contents)

- - - -

### 2.6 cal_extract_RAW_spirou.py

- Merged `cal_extract_RAW_spirouAB`, `cal_extract_RAW_spirouC` and `cal_extract_RAW_spirouALL`
    - can still access `cal_extract_RAW_spirouAB` and `cal_extract_RAW_spirouC` but instead of being modified copies of the code they are just wrappers for `cal_extract_RAW_spirou.py` (i.e. they forward the fiber type)

- added storage dictionary to store (and pass around) all variables created
    - `loc` - a Parameter dictionary (thus source can be set for all variables to keep track of them)

- Created function to read TILT file from calibDB (replaces `readkeyloco`)
    - `spirouImage.ReadTiltFile(p, hdr)`
    - takes in header dictionary from `fitsfilename` in order to avoid re-opening FITS rec (acqutime used in calibDB to get max_time of calibDB entry) 

- Created function to read WAVE file from calibDB (replaces `read_data_raw(`)
    - `spirouImage.ReadWaveFile(p, hdr)`
    - takes in header dictionary from `fitsfilename` in order to avoid re-opening FITS rec (acqutime used in calibDB to get max_time of calibDB entry) 

- Used `spirouLOCOR.GetCoeffs(p, hdr, loc=loc)` to get the coefficients from file

- Created function to read order profile (replaces `read_data_raw` + pre-amble)
    - `spirouImage.ReadOrderProfile(p, hdr)`
    - takes in header dictionary from `fitsfilename` in order to avoid re-opening FITS rec (acqutime used in calibDB to get max_time of calibDB entry) 

- Created merge coefficients function to perform AB coefficient merge
    - `spirouLOCOR.MergeCoefficients`

- New structures above replace the need for specific fiber sections ('AB', 'C', 'A', 'B') (In `cal_extract_RAW_spirouALL` and individual setups for `cal_extract_RAW_spirouAB` and `cal_extract_RAW_spirouC`)

- all extraction functions passed into spirouEXTOR to wrapper functions (`spirouEXTOR.ExtractOrder`, `spirouEXTOR.ExtractTiltOrder`, `spirouEXTOR.ExtractTiltWeightOrder` and `spirouEXTOR.ExtractWeightOrder`) these are then run into `spirouEXTOR.ExtractionWrapper` and processed accordingly

- Added a timing string (to record timings of all extraction processes)
    - use `print(timing))` to view
    
- `e2ds` and `SNR` stored in `loc`

- Plotting code moved to `spirouCore.spirouPlot` functions

- Writing of fits file cleaned up (header keywords written during data write)

- QC (max_signal > qc_max_signal * nbframes) moved to end, however in old code it is not used as a failure criteria so also not used to fail in new code

- **speed up**

	- AT-4 v44: 60.8522210121
	
	- py3: 8.693637132644653

	- Extraction timing Py3:

         - ExtractOrder = 0.02470088005065918 s
         
         - ExtractTiltOrder = 0.05955362319946289 s
         
         - ExtractTiltWeightOrder = 0.14079713821411133 s
         
         - ExtractWeightOrder = 0.06998181343078613 s

	- Extraction timing AT-4 v46:

         - ExtractOrder (Fortran) = 0.0191688537598 s
         
         - ExtractOrder (Py2) = 0.0850250720978 s
         
         - ExtractTiltOrder = 0.765933990479 s
         
         - ExtractTiltWeightOrder = 0.83994603157 s
         
         - ExtractWeightOrder = 0.155860900879 s

	- Speed increase (Py3 over AT-4 v46)

		- ExtractOrder (Py3 --> Fortran) = slower    x 1.3 times slower
		
		- ExtractOrder (Py3 --> Py3) = faster     x 3.4 times faster
		
		- ExtractTiltOrder (Py3 --> Py3) = faster     x12.9 times faster
		
		- ExtractTiltWeightOrder (Py3 --> Py3) = faster    x6.0 times faster
		
		- ExtractWeightOrder (Py3 --> Py3) = faster    x2.2 times faster

[Back to top](#table-of-contents)

- - - -

### 2.7 cal_DRIFT_RAW_spirou.py

- acqtime (bjdref) got from header using `spirouImage.GetAcqTime`
    - `spirouImage.GetAcqTime(p, hdr, name='acqtime', kind='unix')`
    - can be used to get both `human` readible and `unix` time (use key kind=`human` or kind=`unix)
    
- Created function to read TILT file from calibDB (replaces `readkeyloco`)
    - `spirouImage.ReadTiltFile(p, hdr)`
    - takes in header dictionary from `fitsfilename` in order to avoid re-opening FITS rec (acqutime used in calibDB to get max_time of calibDB entry) 

- Created function to read WAVE file from calibDB (replaces `read_data_raw(`)
    - `spirouImage.ReadWaveFile(p, hdr)`
    - takes in header dictionary from `fitsfilename` in order to avoid re-opening FITS rec (acqutime used in calibDB to get max_time of calibDB entry) 

- Used `spirouLOCOR.GetCoeffs(p, hdr, loc=loc)` to get the coefficients from file

- Created function to read order profile (replaces `read_data_raw` + pre-amble)
    - `spirouImage.ReadOrderProfile(p, hdr)`
    - takes in header dictionary from `fitsfilename` in order to avoid re-opening FITS rec (acqutime used in calibDB to get max_time of calibDB entry) 

- Created merge coefficients function to perform AB coefficient merge
    - `spirouLOCOR.MergeCoefficients`

- all extraction functions passed into spirouEXTOR to wrapper functions (`spirouEXTOR.ExtractOrder`, `spirouEXTOR.ExtractTiltOrder`, `spirouEXTOR.ExtractTiltWeightOrder` and `spirouEXTOR.ExtractWeightOrder`) these are then run into `spirouEXTOR.ExtractionWrapper` and processed accordingly

- delta RV RMS calculation in `spirouRV.DeltaVrms2D`
    - `dvrmsref, wmeanref = spirouRV.DeltaVrms2D(*dargs, **dkwargs)`
    - where arguments are `speref` and `wave` (stored in `loc`)
    - where keyword arguments are `sigdet`, `size` and `threshold` (stored in p)

- all functionality to do with listing files moved to `spirouImage.GetAllSimilarFiles`
    - no need for "alphanumeric short"/"nice sort" - `np.sort(x)` does this
    
- Renormlisation and cosmics correction in `spirouRV.ReNormCosmic2D`
    - `spen, cfluxr, cpt = spirouRV.ReNormCosmic2D(*dargs, **dkwargs)`
    - where arguments are `speref` and `spe` (stored in `loc`)
    - where keyword arguments are `cut`, `size` and `threshold` (stored in p)

- RV drift calculated in `CalcRVdrift2D`
    - `rv = spirouRV.CalcRVdrift2D(*dargs, **dkwargs)`
    - where arguments are `speref`, `spen` and `wave` (`speref` and `spen` stored in loc)
    - where keyword arguments are `sigdet`, `size` and `threshold` (stored in p)

- `drift`, `errdrift`, `deltatime`, `mdrift`, `merrdrift` stored in loc

- Writing of fits file cleaned up (header keywords written during data write)

- **speed up**

    - AT-4 v44: 22.556137085 s
    
	- py3:  8.14345932006836 s


[Back to top](#table-of-contents)


### 2.8 cal_BADPIX_spirou.py

- loading of custom arguments moved to `spirouStartup.GetCustomFromRuntime`

- loading of files moved to `spirouImage.ReadImage`

- normalising flat and median of flat moved to `spirouImage.NormMedianFlat`

- locating bad pixels moved to `spirouImage.LocateBadPixels`

- instead of taking the 90th pixel in flattened meadian flat image now work out the 90th percentile of finite values (will lead to a slightly more correct normalisation value)

- Writing of fits file cleaned up (header keywords written during data write)

[Back to top](#table-of-contents)

- - - - 

## 3 Timing:

### 3.1 Full unit test in python 3:

- cal_DARK_spirou Time taken = 4.265186309814453 s

- cal_loc_RAW_spirou (flat_dark) Time taken = 3.7583842277526855 s

- cal_loc_RAW_spirou (dark_flat) Time taken = 2.230999231338501 s

- cal_SLIT_spirou Time taken = 5.18412446975708 s

- cal_FF_RAW_spirou (flat_dark) Time taken = 4.059345960617065 s

- cal_FF_RAW_spirou (dark_flat) Time taken = 3.144118547439575 s

- cal_extract_RAW_spirou (hcone_dark) Time taken = 8.436801671981812 s

- cal_extract_RAW_spirou (dark_hcone) Time taken = 8.53130316734314 s

- cal_extract_RAW_spirou (hcone_hcone AB) Time taken = 8.019875049591064 s

- cal_extract_RAW_spirou (hcone_hcone C) Time taken = 8.143184423446655 s

- cal_extract_RAW_spirou (dark_dark_AHC1 AB) Time taken = 8.70938754081726 s

- cal_extract_RAW_spirou (dark_dark_AHC1 C) Time taken = 7.307146787643433 s

- cal_extract_RAW_spirou (hctwo_dark AB) Time taken = 7.910982608795166 s

- cal_extract_RAW_spirou (hctwo_dark C) Time taken = 7.214818239212036 s

- cal_extract_RAW_spirou (dark_hctwo AB) Time taken = 9.284996032714844 s

- cal_extract_RAW_spirou (dark_hctwo C) Time taken = 8.095324277877808 s

- cal_extract_RAW_spirou (hctwo-hctwo AB) Time taken = 7.679980993270874 s

- cal_extract_RAW_spirou (hctwo-hctwo C) Time taken = 6.652430534362793 s

- cal_extract_RAW_spirou (dark_dark_AHC2 AB) Time taken = 7.698842525482178 s

- cal_extract_RAW_spirou (dark_dark_AHC2 C) Time taken = 7.389096260070801 s

- cal_extract_RAW_spirou (fp_fp AB) Time taken = 7.700818777084351 s

- cal_extract_RAW_spirou (fp_fp C) Time taken = 7.595874547958374 s

- cal_DRIFT_RAW_spirou Time taken = 6.379834890365601 s

- **Total Time taken** = 155.42251753807068 s


[Back to top](#table-of-contents)

### 3.2 Full unit test python 2:

- cal_DARK_spirou Time taken = 3.1798491478 s

- cal_loc_RAW_spirou (flat_dark) Time taken = 6.40095114708 s

- cal_loc_RAW_spirou (dark_flat) Time taken = 3.44882392883 s

- cal_SLIT_spirou Time taken = 5.83366394043 s

- cal_FF_RAW_spirou (flat_dark) Time taken = 4.56528401375 s

- cal_FF_RAW_spirou (dark_flat) Time taken = 4.36482381821 s

- cal_extract_RAW_spirou (hcone_dark) Time taken = 9.87302112579 s

- cal_extract_RAW_spirou (dark_hcone) Time taken = 10.0084240437 s

- cal_extract_RAW_spirou (hcone_hcone AB) Time taken = 10.2958710194 s

- cal_extract_RAW_spirou (hcone_hcone C) Time taken = 8.27689790726 s

- cal_extract_RAW_spirou (dark_dark_AHC1 AB) Time taken = 10.073319912 s

- cal_extract_RAW_spirou (dark_dark_AHC1 C) Time taken = 7.87540793419 s

- cal_extract_RAW_spirou (hctwo_dark AB) Time taken = 9.89485096931 s

- cal_extract_RAW_spirou (hctwo_dark C) Time taken = 7.43826508522 s

- cal_extract_RAW_spirou (dark_hctwo AB) Time taken = 9.87350988388 s

- cal_extract_RAW_spirou (dark_hctwo C) Time taken = 7.1852619648 s

- cal_extract_RAW_spirou (hctwo-hctwo AB) Time taken = 9.37891101837 s

- cal_extract_RAW_spirou (hctwo-hctwo C) Time taken = 7.4923620224 s

- cal_extract_RAW_spirou (dark_dark_AHC2 AB) Time taken = 9.52454400063 s

- cal_extract_RAW_spirou (dark_dark_AHC2 C) Time taken = 7.53619909286 s

- cal_extract_RAW_spirou (fp_fp AB) Time taken = 8.90776896477 s

- cal_extract_RAW_spirou (fp_fp C) Time taken = 8.34801197052 s

- cal_DRIFT_RAW_spirou Time taken = 6.39085698128 s

- **Total Time taken** = 176.209826231 s



[Back to top](#table-of-contents)

### 3.3 Full unit test in AT4 V46

- cal_DARK_spirou Time taken = 4.96914315224 s

- cal_loc_RAW_spirou (flat_dark) Time taken = 7.34097385406 s

- cal_loc_RAW_spirou (dark_flat) Time taken = 6.64635396004 s

- cal_FF_RAW_spirou (flat_dark) Time taken = 27.31854105 s

- cal_FF_RAW_spirou (dark_flat) Time taken = 25.1645009518 s

- cal_SLIT_spirou Time taken = 8.83131313324 s

- cal_extract_RAW_spirou (hcone_dark) Time taken = 59.4400849342 s

- cal_extract_RAW_spirou (dark_hcone) Time taken = 60.0921180248 s

- cal_extract_RAW_spirou (hcone_hcone AB) Time taken = 58.6570830345 s

- cal_extract_RAW_spirou (hcone_hcone C) Time taken = 51.9204559326 s

- cal_extract_RAW_spirou (dark_dark_AHC1 AB) Time taken = 58.6610798836 s

- cal_extract_RAW_spirou (dark_dark_AHC1 C) Time taken = 58.7274119854 s

- cal_extract_RAW_spirou (hctwo_dark AB) Time taken = 60.0075399876 s

- cal_extract_RAW_spirou (hctwo_dark C) Time taken = 57.5560529232 s

- cal_extract_RAW_spirou (dark_hctwo AB) Time taken = 65.7684230804 s

- cal_extract_RAW_spirou (dark_hctwo C) Time taken = 57.0358560085 s

- cal_extract_RAW_spirou (hctwo-hctwo AB) Time taken = 0.00649285316467 s

- cal_extract_RAW_spirou (hctwo-hctwo C) Time taken = 61.2897648811 s

- cal_extract_RAW_spirou (dark_dark_AHC2 AB) Time taken = 61.0548040867 s

- cal_extract_RAW_spirou (dark_dark_AHC2 C) Time taken = 59.3190112114 s

- cal_extract_RAW_spirou (fp_fp AB) Time taken = 65.0505418777 s

- cal_extract_RAW_spirou (fp_fp C) Time taken = 59.2866010666 s

- cal_DRIFT_RAW_spirou Time taken = 25.8372788429 s

- **Total Time taken** = 1001.15767193 s


[Back to top](#table-of-contents)

- - - -

## 4 Progress:

- main codes (Done):

    - [x] - ~~cal_dark_spirou~~
    
    - [x] - ~~cal_loc_RAW_spioru~~
    
    - [x] - ~~cal_SLIT_spirou~~
    
    - [x] - ~~cal_FF_RAW_spirou~~
    
    - [x] - ~~cal_extract_RAW_spirou~~
    
    - [x] - ~~cal_DRIFT_RAW_spirou~~
    
    - [ ] - cal_HC_E2DS_spirou

    - [x] - ~~cal_DRIFT_E2DS_spirou~~
 
    - [ ] - cal_DRIFT-PEAK_E2DS_spirou
    
    - [x] - ~~cal_BADPIX_spirou~~
    
    - [ ] - cal_WAVE_E2DS_spirou
    
    - [ ] - cal_CCF_E2DS_spirou
    
    - [ ] - pol_spirou

    
- unit test run:

    - [x] - cal_dark_spirou
    
    - [x] - cal_loc_RAW_spioru
    
    - [x] - cal_SLIT_spirou
    
    - [x] - cal_FF_RAW_spirou
    
    - [x] - cal_extract_RAW_spirou
    
    - [x] - cal_DRIFT_RAW_spirou
    
    - [ ] - cal_HC_E2DS_spirou

    - [ ] - cal_DRIFT_E2DS_spirou
 
    - [ ] - cal_DRIFT-PEAK_E2DS_spirou
    
    - [ ] - cal_BADPIX_spirou
    
    - [ ] - cal_WAVE_E2DS_spirou
    
    - [ ] - cal_CCF_E2DS_spirou
    
    - [ ] - pol_spirou
    
- unit test outputs (Against AT-4 output)

    - [ ] - cal_dark_spirou
    
    - [ ] - cal_loc_RAW_spioru
    
    - [ ] - cal_SLIT_spirou
    
    - [ ] - cal_FF_RAW_spirou
    
    - [ ] - cal_extract_RAW_spirou
    
    - [ ] - cal_DRIFT_RAW_spirou
    
    - [ ] - cal_HC_E2DS_spirou

    - [ ] - cal_DRIFT_E2DS_spirou
 
    - [ ] - cal_DRIFT-PEAK_E2DS_spirou
    
    - [ ] - cal_BADPIX_spirou
    
    - [ ] - cal_WAVE_E2DS_spirou
    
    - [ ] - cal_CCF_E2DS_spirou
    
    - [ ] - pol_spirou
        
- Documentation

    - [ ] - user guide
    
    - [ ] - developer guide


        
    
[Back to top](#table-of-contents)

- - - -