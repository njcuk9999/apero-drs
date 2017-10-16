# SPIRou DRS in python 3


## Change log from Version 43 of the DRS

### cal_DARK_spirou.py

- all import functions re-worked (removed or changed or updated)

- execution of pythonstartup codes removed and replaced with functions
    - `startup.RunInitialStartup()` to replace `execfile(os.getenv('PYTHONSTARTUP))`
    - `startup.RunStartup` to replace `execfile(os.getenv('PYTHONSTARTUP2))`

- loading of many variables into python memory replaced with parameter dictionary containing all variables
    - This includes all variables loaded into memory by `startup.py` and `startup_recipes.py`
    - Loading many variables from many codes into memory is dangerous as any variable can be overwritten/previously defined.

- all hard coded constants (i.e. ints/floats/strings) that may be changed moved into config files
    - `config.txt` - This contains all the variables previously defined as environmental variables
        - i.e. this will allow functionality across platforms and avoid having many variables defined in the environment (fine for a dedicated machine but a nightmare for anyone else)
    - `hadmrICDP_SPIROU.txt` - final location can be changed by all other variables are currently in this file (loaded in previous versions as a python code loading variables into the memory). This is dangerous as any variable can be overwritten/previously defined.

- moved resizing of image to function
    - `gf.ResizeImage(data, xlow, xhigh, ylow, yhigh)`
    - `gf` is an alias to the module `generalfunctions`

- dark measurement moved to internal function `measure_dark` (for clarity)
     - This is, in part, due to the repetition of code for "Whole det", "Blue part" and "Red part"

- plots are now only plotted if `DRS_PLOT` is True (or =1)
    - Can turn plotting off in `config.txt` =0 or =False

- all plotting moved to internal functions (for clarity)
    - `plot_image_and_regions(p, data)` for the image/region plot
    - `plot_datacut` for the DARK > cutlimit plot
    - `plot_hisotgrams` for the histogram plots 
    
- histogram plot updated
    - original plot plotted bin centers as a smooth peak, simple modification to make sure histogram bars are present
    
- writing of data is sped up by caching all HEADER keys and writing to file **once** with the write of the data.