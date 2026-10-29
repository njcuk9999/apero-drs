#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2020-02-04 at 13:37

@author: cook
"""
import sys
from typing import Any, List, Optional, Set

from aperocore.base import base
from apero.base import base as apero_base
from aperocore.constants import param_functions
from aperocore.constants import load_functions
from aperocore.core import drs_log
from apero.core import drs_file
from aperocore.core import drs_misc
from apero.utils import drs_recipe
from apero.instruments import select
from apero.base import base as apero_base

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'tools.module.testing.drs_dev.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = apero_base.__PACKAGE__
__version__ = apero_base.__version__
__authors__ = apero_base.__authors__
__date__ = apero_base.__date__
__release__ = apero_base.__release__
# get param dict
ParamDict = param_functions.ParamDict
# Get Logging function
WLOG = drs_log.wlog
# get DrsRecipe
DrsRecipe = drs_recipe.DrsRecipe
DrsFitsFile = drs_file.DrsFitsFile
DrsInputFile = drs_file.DrsInputFile
DrsNpyFile = drs_file.DrsNpyFile
# recipe control path
INSTRUMENT_PATH = apero_base.CONST_PATH
CORE_PATH = apero_base.CORE_PATH
PDB_RC_FILE = apero_base.PDB_RC_FILE
CURRENT_PATH = ''


# -----------------------------------------------------------------------------

# =============================================================================
# Define classes
# =============================================================================
class TmpRecipe(DrsRecipe):
    """Recipe instance used by developer tools and demonstrations."""

    def __init__(self, instrument: str = 'None', name: Optional[str] = None,
                 filemod: Any = None) -> None:
        """Initialize a recipe wrapper for developer tooling.

        :param instrument: Instrument associated with the recipe.
        :param name: Optional recipe module name.
        :param filemod: Optional file-definition module for the recipe.
        :return: None. Initializes the inherited recipe state.
        """
        # load super class
        super().__init__(instrument, name, filemod)


class RecipeDefinition:
    """Expose instrument recipe definitions with temporary additions."""

    def __init__(self, instrument: str = 'None') -> None:
        """Load recipe definitions for the selected instrument.

        :param instrument: Instrument associated with the recipe definitions.
        :return: None. Loads the recipe module and initial definitions.
        """
        self.instrument = instrument
        self.recipes = []
        self.mod = None
        # populate recipes using instrument
        self.populate_recipes()

    def populate_recipes(self) -> None:
        """Load the active instrument's recipe-definition module."""
        # need to update filemod and recipe mod
        pconst = load_functions.load_pconfig(select.INSTRUMENTS)
        # update filemod
        recipemod = pconst.RECIPEMOD()
        # add to recipes
        self.recipes = recipemod.recipes
        self.recipemod = recipemod

    def add(self, *args: Any) -> None:
        """Add temporary recipe objects to the definition list.

        :param args: Candidate recipe objects; non-temporary recipes are ignored.
        :return: None. Appends accepted temporary recipes to ``recipes``.
        """
        for arg in args:
            if isinstance(arg, TmpRecipe):
                self.recipes.append(arg)


class TmpInputFile(DrsFitsFile):
    """Temporary FITS input-file definition used in developer tooling."""

    def __init__(self, name: str, **kwargs: Any) -> None:
        """Initialize a temporary FITS input file definition.

        :param name: Name of the temporary input file.
        :param kwargs: File-definition values forwarded to ``DrsFitsFile``.
        :return: None. Initializes the inherited FITS file state.
        """
        # load super class
        super().__init__(name, **kwargs)


class TmpFitsFile(DrsFitsFile):
    """Temporary FITS output-file definition used in developer tooling."""

    def __init__(self, name: str, **kwargs: Any) -> None:
        """Initialize a temporary FITS output file definition.

        :param name: Name of the temporary output file.
        :param kwargs: File-definition values forwarded to ``DrsFitsFile``.
        :return: None. Initializes the inherited FITS file state.
        """
        # load super class
        super().__init__(name, **kwargs)


class TmpNpyFile(DrsFitsFile):
    """Temporary NumPy-file definition used in developer tooling."""

    def __init__(self, name: str, **kwargs: Any) -> None:
        """Initialize a temporary NumPy file definition.

        :param name: Name of the temporary NumPy file.
        :param kwargs: File-definition values forwarded to ``DrsFitsFile``.
        :return: None. Initializes the inherited file state.
        """
        # load super class
        super().__init__(name, **kwargs)


class FileDefinition:
    """Expose the active instrument's input and output file definitions."""

    def __init__(self, instrument: str = 'None') -> None:
        """Load file definitions for one instrument.

        :param instrument: Instrument whose file definitions are exposed.
        :return: None. Loads the module and its output file definitions.
        """
        self.instrument = instrument
        self.files = None
        self.out = None
        # populate files using instrument
        self.populate_files()

    def populate_files(self) -> None:
        """Load this instrument's file-definition module."""
        # need to update filemod and recipe mod
        pconst = load_functions.load_pconfig(select.INSTRUMENTS)
        # update filemod
        filemod = pconst.FILEMOD()
        # add to recipes
        self.files = filemod
        self.out = filemod.out


class Demo:
    """
    Holder of demonstration functions (to keep demo clean)
    """

    def __init__(self, params: Optional[ParamDict] = None) -> None:
        """Initialize demo helpers using supplied or loaded APERO parameters.

        :param params: Optional parameter dictionary; loaded when omitted.
        :return: None. Stores parameters and package metadata.
        """
        # get parameters
        if params is None:
            self.params = load_functions.load_config(select.INSTRUMENTS)
        else:
            self.params = params
        # get package
        self.package = params['DRS.PACKAGE']

    @staticmethod
    def setup() -> List[str]:
        """Ensure demo arguments exist and return the current argv values."""
        # deal with arguments
        if isinstance(sys.argv, list):
            args = list(sys.argv)
        else:
            args = str(sys.argv).split()
        # if we don't have the required arguments add them
        if len(args) < 2:
            sys.argv = ['demo', '1']
        return args

    def get_lang_db_loc(self) -> str:
        """Return the absolute path to the package language database."""
        # get language database relative path
        relpath = base.LANG_DEFAULT_PATH
        # return absolute language database path
        return drs_misc.get_relative_folder(self.package, relpath)

    def change_lang(self, params: ParamDict, language: str) -> None:
        """Set the language on this demo and the supplied parameters."""
        # update the language
        self.params.set('GLOBAL.LANGUAGE', language)
        params.set('GLOBAL.LANGUAGE', language)

    def test_data(self, params: ParamDict) -> None:
        """Placeholder for loading packaged demonstration data."""
        # TODO: get test data from data/spirou/demo
        pass


# =============================================================================
# Define functions
# =============================================================================
def get_size(obj: object, seen: Optional[Set[int]] = None) -> int:
    """
    Recursively finds size of objects

    :param obj: Object whose recursive in-memory size is measured.
    :param seen: Object identities already counted to prevent cycles.
    :return: Estimated size in bytes, counting each referenced object once.

    from: https://goshippo.com/blog/measure-real-size-any-python-object/
    """

    sbtype = (str, bytes, bytearray)

    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, sbtype):
        size += sum([get_size(i, seen) for i in obj])
    return size


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
