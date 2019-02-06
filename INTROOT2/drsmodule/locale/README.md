# Readme for drsmodule.locale

## import rules

- sub-modules to the constants package cannot import any other DRS sub-modules
- no exceptions

## core

- contains functions and classes for the DRS Locale package

## databases

- DO NOT edit the `.csv` files directly they will be overwritten by code (from the `language.xls` file) 

- contains the language databases
    - `language.xls`

- also contains csv files (extracted from `language.xls`) using `.core.port_database.py`
    - `error.csv`   (Sheet `ERROR`)
    - `help.csv`    (Sheet `HELP`)
    - `error_{instrument}.csv`
    - `help_{instrument}.csv`

- can overwrite only for specific instrument as follows
    - go to `language.xls'
    - find a line in `ERROR` or `HELP`
    - find the instrument sheet (i.e. `ERROR_SPIROU`)
    - copy line into instrument sheet
    - This will overwrite that line for this instrument (including translation)
    - Using `.core.port_database.py` will write these to the instrument `.csv`
        - `error_{instrument}.csv`
        - `help_{instrument}.csv`
        - e.g. `error_spirou.csv`
        
Notes:
    - extra database `sheets` have to be added to  `.core.port_database.py` manually
    - for instrument names instrument must be lower case
    - tmp files (.npy files) generated when `.csv` files have been modified (these can be deleted at any time without consequence) and are ignored by `git`