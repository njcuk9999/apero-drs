#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CODE DESCRIPTION HERE

Created on 2020-10-2020-10-05 17:43

@author: cook
"""
from astropy.table import Table
from astropy import version as av
from collections import OrderedDict
from copy import deepcopy
import numpy as np
import os
from pathlib import Path
from typing import Any, Dict, List, Union, Tuple, Type
import warnings


from apero.base import base
from apero.base import drs_exceptions
from apero.base import drs_text
from apero.core.core import drs_log
from apero.core import constants
from apero.core.utils import drs_database
from apero import lang
from apero.io import drs_fits


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'drs_utils.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get display func
display_func = drs_log.display_func
# get time object
Time = base.Time
# Get Logging function
WLOG = drs_log.wlog
# alias pcheck
pcheck = constants.PCheck(wlog=WLOG)
# get parameter dictionary
ParamDict = constants.ParamDict
# get databases
IndexDatabase = drs_database.IndexDatabase
# get header classes from io.drs_fits
Header = drs_fits.Header
FitsHeader = drs_fits.fits.Header
# Get the text types
TextEntry = lang.core.drs_lang_text.TextEntry
TextDict = lang.core.drs_lang_text.TextDict
HelpText = lang.core.drs_lang_text.HelpDict


# =============================================================================
# Define functions
# =============================================================================
def update_index_db(params: ParamDict, kind: str,
                    whitelist: Union[List[str], None],
                    blacklist: Union[List[str], None],
                    filename: Union[List[Path], Path, List[str], str, None],
                    suffix: str = ''):
    # deal with white list and black list
    if not drs_text.null_text(whitelist, ['None', 'All', '']):
       include_dirs = list(whitelist)
    else:
       include_dirs = None
    if not drs_text.null_text(blacklist, ['None', 'All', '']):
        exclude_dirs = list(blacklist)
    else:
        exclude_dirs = None
    # load the index database
    indexdbm = drs_database.IndexDatabase(params)
    indexdbm.load_db()
    # get white
    # update index database with raw files
    indexdbm.update_entries(kind=kind, exclude_directories=exclude_dirs,
                            include_directories=include_dirs,
                            filename=filename, suffix=suffix)
    # return the database
    return indexdbm



# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
