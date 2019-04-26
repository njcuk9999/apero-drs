# Readme for drsmodule.constants

## import rules

- sub-modules to the constants package cannot import any other DRS sub-modules
- with the exception of the locale package

## core

- contains functions and classes for the DRS constants package


## default

- contains the default constants for the DRS these can be overwritten by instrument values
    - ```default_config.py``` contains config definitions
    - ```default_constants.py``` contains constants definitions
    - ```default_keywords.py``` contains keyword defintions
    - ```pseudo_const.py``` contains class/function (pseudo) constants
    