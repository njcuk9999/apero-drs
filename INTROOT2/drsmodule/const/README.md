# Readme for Constants module

This module contains scripts that define constants


## Rules

- Cannot import any other internal module



## Core package

- Must contain a default value for every value in instrument packages
- Constants are defined by object "Const"
    - Const("name", value="value", dtype="type", options="options")
    
- Keywords are defined by object "Keyword"
    - Keyword("name", key="key", value="value", dtype="type", options="options")

   
    
## Instrument packages

- Values that overwrite those in core package (based on instrument being used)
