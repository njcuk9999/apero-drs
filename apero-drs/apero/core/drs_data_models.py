#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2025-07-17 at 14:04

@author: cook
"""
import ast
import os
import string
import textwrap
import time
import warnings
from collections import OrderedDict
from copy import deepcopy
from hashlib import blake2b
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Type, Union

import numpy as np
import pandas as pd
from astropy.table import Table, vstack
from astropy import units as uu
from scipy.stats import pearsonr

from aperocore.base import base
from aperocore.base import drs_base
from aperocore.constants import param_functions
from aperocore.constants import constant_functions
from aperocore.constants import load_functions

from apero.base import base as apero_base
from apero.instruments.default import instrument as instrument_mod
from aperocore import drs_lang
from aperocore import math as mp
from apero.constants import path_definitions as pathdef
from aperocore.core import drs_base_classes as base_class
from aperocore.core import drs_text
from aperocore.core import drs_misc
from apero.core import drs_out_file as out
from aperocore.core import drs_log
from apero.io import drs_fits
from apero.io import drs_path
from apero.io import drs_table
from apero.instruments import select

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'drs_file.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = apero_base.__PACKAGE__
__version__ = apero_base.__version__
__authors__ = apero_base.__authors__
__date__ = apero_base.__date__
__release__ = apero_base.__release__
# get parameter dictionary
ParamDict = param_functions.ParamDict
# get exceptions
AperoCodedException = drs_log.AperoCodedException
AperoCodedWarning = drs_log.AperoCodedWarning


# =============================================================================
# Define Apere Data Model classes
# =============================================================================
class AperoDataModel:
    classname = 'AperoDataModel'

    def __init__(self, name: str):
        # some info
        self.name = name
        self.datatype = None

    def __getstate__(self) -> dict:
        """
        For when we have to pickle the class
        :return:
        """
        # set state to __dict__
        state = dict(self.__dict__)
        # return dictionary state
        return state

    def __setstate__(self, state: dict):
        """
        For when we have to unpickle the class

        :param state: dictionary from pickle
        :return:
        """
        # update dict with state
        self.__dict__.update(state)

    def load_data(self, params: ParamDict, filename: str,
                  **kwargs) -> Any:
        emsg = 'AperoDataModel.load_data not implemented'
        raise NotImplemented(emsg)


class AperoTableModel(AperoDataModel):
    classname = 'AperoTableModel'

    """
    Model AperoTable - for use whenever a table is to be saved

    This can also be used to create a table - checking the format is correct
    """

    def __init__(self, name: str, columns=None, units=None, descriptions=None):
        """
        Construct the AperoTableModel
        """
        # some info
        super().__init__(name)
        self.datatype = 'table'
        # set values
        self.columns = [] if columns is None else columns
        self.units = [] if units is None else units
        self.descriptions = [] if descriptions is None else descriptions

    def add_column(self, column: str, units: uu.Unit = None,
                   description: str = None):
        """
        Add a column to this AperoTable model

        :param column: str, the name of the column
        :param units: str, the units of the column (can be left blank)
        :param description: str, the description of the column (can be
                            left blank)
        """
        self.columns.append(column)
        self.units.append(units)
        self.descriptions.append(description)

    def create_table(self, **kwargs) -> Table:
        """
        Create a new astropy table using the defined AperoTable framework

        :param kwargs: A list of columns to add to the table
        """
        # create a table
        outtable = Table()
        # loop around columns
        for c_it, column in enumerate(self.columns):
            # check that we have required column
            if column in kwargs:
                outtable[column] = kwargs[column]
            # otherwise throw an error
            else:
                emsg = 'AperoTable[{0}] requires column "{1}"'
                eargs = [self.name, column]
                raise AperoCodedException(None, None,
                                          message=emsg.format(*eargs),
                                          targs=eargs)
            # set units if present
            if self.units[c_it] is not None:
                outtable[column].unit = self.units[c_it]
            # set description if present
            if self.descriptions[c_it] is not None:
                outtable[column].description = self.descriptions[c_it]
        # return out table
        return outtable

    def load_data(self, params: ParamDict, filename: str,
                  **kwargs) -> Table:
        """
        Load a fits table from 'filename'

        :param params: ParamDict, parameter dictionary of constants
        :param filename: str, name of the fits file
        :param kwargs: keyword arguments to send to drs_table.read_table

        return: Table, the fits table
        """
        # make sure we don't duplicate this key (forced by Model)
        keys_passed = list(kwargs.keys())
        for key in ['hdu', 'fmt']:
            if key in keys_passed:
                del kwargs[key]
        # read and return table
        return drs_table.read_table(params, filename, hdu=self.name,
                                    fmt='fits', **kwargs)


class AperoImageModel(AperoDataModel):
    classname = 'AperoImageModel'

    def __init__(self, name: str, shape: List[Union[str, int]] = None):
        # some info
        super().__init__(name)
        self.datatype = 'image'
        self.shape = shape

    def load_data(self, params: ParamDict, filename: str,
                  **kwargs) -> drs_fits.DataHdrType:
        """
        Load a fits image from 'filename'

        :param params: ParamDict, parameter dictionary of constants
        :param filename: str, name of the fits file
        :param kwargs: keyword arguments to send to drs_table.read_table

        return: Table, the fits table
        """
        # make sure we don't duplicate this key (forced by Model)
        keys_passed = list(kwargs.keys())
        for key in ['ext', 'extname', 'fmt']:
            if key in keys_passed:
                del kwargs[key]
        # read and return image
        return drs_fits.readfits(params, filename, extname=self.name,
                                 fmt='fits-image', **kwargs)


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
