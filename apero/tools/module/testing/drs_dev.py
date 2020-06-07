#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2020-02-04 at 13:37

@author: cook
"""
import sys

from apero import core
from apero.core import constants
from apero.lang import drs_text
from apero.core.constants import constant_functions as cf
from apero.core.constants import param_functions as pf
from apero.core.core import drs_recipe
from apero.core.core import drs_file

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'drs_startup.py'
__INSTRUMENT__ = 'None'
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Define package name
PACKAGE = Constants['DRS_PACKAGE']
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# get param dict
ParamDict = constants.ParamDict
# Get Logging function
WLOG = core.wlog
# Get the text types
TextEntry = drs_text.TextEntry
TextDict = drs_text.TextDict
HelpEntry = drs_text.HelpEntry
HelpText = drs_text.HelpDict
# get DrsRecipe
DrsRecipe = drs_recipe.DrsRecipe
DrsFitsFile = drs_file.DrsFitsFile
DrsInputFile = drs_file.DrsInputFile
DrsNpyFile = drs_file.DrsNpyFile
# recipe control path
INSTRUMENT_PATH = Constants['DRS_MOD_INSTRUMENT_CONFIG']
CORE_PATH = Constants['DRS_MOD_CORE_CONFIG']
PDB_RC_FILE = Constants['DRS_PDB_RC_FILE']
CURRENT_PATH = ''
# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
class TmpRecipe(DrsRecipe):
    def __init__(self, instrument=None, name=None, filemod=None):
        # load super class
        super().__init__(instrument, name, filemod)


class RecipeDefinition():
    def __init__(self, instrument=None):
        self.instrument = instrument
        self.recipes = []
        self.mod = None
        # populate recipes using instrument
        self.populate_recipes()

    def populate_recipes(self):
        func_name = __NAME__ + '.RecipeDefinition.populate_recipes()'
        # deal with no instrument
        if self.instrument == 'None' or self.instrument is None:
            ipath = CORE_PATH
            self.instrument = None
        else:
            ipath = INSTRUMENT_PATH
        # get recipe definitions module
        margs = [self.instrument, ['recipe_definitions.py'], ipath, CORE_PATH]
        modules = constants.getmodnames(*margs, path=False)
        # load module
        mod = constants.import_module(func_name, modules[0], full=True)
        # add to recipes
        self.recipes = mod.recipes
        self.mod = mod

    def add(self, *args):
        """
        Add temporary recipes to recipe definitions recipe list

        :param args:
        :return:
        """
        for arg in args:
            if isinstance(arg, TmpRecipe):
                self.recipes.append(arg)


class TmpInputFile(DrsFitsFile):
    def __init__(self, name, **kwargs):
        # load super class
        super().__init__(name, **kwargs)


class TmpFitsFile(DrsFitsFile):
    def __init__(self, name, **kwargs):
        # load super class
        super().__init__(name, **kwargs)


class TmpNpyFile(DrsFitsFile):
    def __init__(self, name, **kwargs):
        # load super class
        super().__init__(name, **kwargs)


class FileDefinition():
    def __init__(self, instrument=None):
        self.instrument = instrument
        self.files = None
        self.out = None
        # populate files using instrument
        self.populate_files()

    def populate_files(self):
        func_name = __NAME__ + '.FileDefinition.populate_files()'
        # deal with no instrument
        if self.instrument == 'None' or self.instrument is None:
            ipath = CORE_PATH
            self.instrument = None
        else:
            ipath = INSTRUMENT_PATH
        # get recipe definitions module
        margs = [self.instrument, ['file_definitions.py'], ipath, CORE_PATH]
        modules = constants.getmodnames(*margs, path=False)
        # load module
        mod = constants.import_module(func_name, modules[0], full=True)
        # add to recipes
        self.files = mod
        self.out = mod.out

class Demo:
    """
    Holder of demonstration functions (to keep demo clean)
    """
    def __init__(self, params=None):
        # get parameters
        if params is None:
            self.params = Constants
        else:
            self.params = params
        # get package
        self.package = params['DRS_PACKAGE']

    def setup(self):
        # deal with arguments
        if isinstance(sys.argv, list):
            args = list(sys.argv)
        else:
            args = sys.argv.split()
        # if we don't have the required arguments add them
        if len(args) < 2:
            sys.argv = ['demo', '1']
        return args

    def get_lang_db_loc(self):
        # get language database relative path
        relpath = drs_text.DEFAULT_PATH
        # return absolute language database path
        return pf.get_relative_folder(self.package, relpath)

    def change_lang(self, params, language):
        # get instrument
        instrument = self.params['INSTRUMENT']
        # update the language
        self.params.set('LANGUAGE', language)
        params.set('LANGUAGE', language)

    def test_data(self, params):
        # TODO: get test data from data/spirou/demo
        pass






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
