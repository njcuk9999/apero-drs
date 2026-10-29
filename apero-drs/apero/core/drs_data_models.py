#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Define models that load APERO image and table FITS extensions.

Each model records an extension's data kind and provides the matching loader.
Table models can also validate and construct tables from named columns.

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

    def __init__(self, name: str) -> None:
        """Initialize a model for a named FITS extension.

        :param name: Extension name used when loading the data
        :return: None
        """
        # some info
        self.name = name
        self.datatype = None

    def __getstate__(self) -> Dict[str, Any]:
        """
        Return this model's attributes for pickling.

        :return: A shallow copy of the instance attribute dictionary
        """
        # set state to __dict__
        state = dict(self.__dict__)
        # return dictionary state
        return state

    def __setstate__(self, state: Dict[str, Any]) -> None:
        """
        Restore model attributes from a pickled state dictionary.

        :param state: Previously serialized instance attributes
        :return: None
        """
        # update dict with state
        self.__dict__.update(state)

    def load_data(self, params: ParamDict, filename: str,
                  **kwargs: Any) -> Any:
        """Load data for this model's extension.

        Subclasses implement loading for their specific data kind.

        :param params: APERO parameter dictionary
        :param filename: FITS file containing the extension
        :param kwargs: Loader-specific options
        :return: Loaded extension data
        :raises NotImplementedError: This base method has no loader
        """
        emsg = 'AperoDataModel.load_data not implemented'
        raise NotImplementedError(emsg)


class AperoTableModel(AperoDataModel):
    classname = 'AperoTableModel'

    """
    Model AperoTable - for use whenever a table is to be saved

    This can also be used to create a table - checking the format is correct
    """

    def __init__(self, name: str, columns: Optional[List[str]] = None,
                 units: Optional[
                     List[Optional[Union[str, uu.Quantity]]]] = None,
                 descriptions: Optional[List[Optional[str]]] = None
                 ) -> None:
        """
        Define the expected columns and their optional metadata.

        :param name: FITS extension name for this table
        :param columns: Required column names, in output order
        :param units: Optional unit for each column
        :param descriptions: Optional description for each column
        :return: None
        """
        # some info
        super().__init__(name)
        self.datatype = 'table'
        # set values
        self.columns = [] if columns is None else columns
        self.units = [] if units is None else units
        self.descriptions = [] if descriptions is None else descriptions

    def add_column(self, column: str,
                   units: Optional[Union[str, uu.Quantity]] = None,
                   description: Optional[str] = None) -> None:
        """
        Add a column to this AperoTable model

        :param column: str, the name of the column
        :param units: str, the units of the column (can be left blank)
        :param description: str, the description of the column (can be
                            left blank)
        :return: None
        """
        self.columns.append(column)
        self.units.append(units)
        self.descriptions.append(description)

    def create_table(self, **kwargs: Any) -> Table:
        """
        Create a new astropy table using the defined AperoTable framework

        :param kwargs: Column-name to data mappings for the required columns
        :return: Astropy table populated with the model's columns and metadata
        :raises AperoCodedException: If a required column is not provided
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
                eargs = [self.name, column]
                # error: AperoTable[{0}] requires column "{1}"
                raise AperoCodedException(None, '00-006-00027', targs=eargs)
            # set units if present
            if self.units[c_it] is not None:
                outtable[column].unit = self.units[c_it]
            # set description if present
            if self.descriptions[c_it] is not None:
                outtable[column].description = self.descriptions[c_it]
        # return out table
        return outtable

    def load_data(self, params: ParamDict, filename: str,
                  **kwargs: Any) -> Table:
        """
        Load a fits table from 'filename'

        :param params: ParamDict, parameter dictionary of constants
        :param filename: str, name of the fits file
        :param kwargs: Additional keyword arguments for ``read_table``

        :return: Table read from this model's FITS extension
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

    def __init__(self, name: str,
                 shape: Optional[List[Union[str, int]]] = None) -> None:
        """
        Construct the AperoImageModel

        :param name: str, name of the image model
        :param shape: List, the shape of the image (e.g. [2048, 2048])
                      or None for any shape
        :return: None
        """
        # some info
        super().__init__(name)
        self.datatype = 'image'
        self.shape = shape

    def load_data(self, params: ParamDict, filename: str,
                  **kwargs: Any) -> Union[drs_fits.DataHdrType, np.ndarray,
                                          drs_fits.fits.Header, None]:
        """
        Load a fits image from 'filename'

        :param params: ParamDict, parameter dictionary of constants
        :param filename: str, name of the fits file
        :param kwargs: Additional keyword arguments for ``readfits``

        :return: Image data, header data, or None as returned by ``readfits``
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
