#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2020-02-04 at 13:37

@author: cook
"""

from apero.core import constants
from apero.core.core import drs_recipe


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
# get DrsRecipe
DrsRecipe = drs_recipe.DrsRecipe
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

    def add(self, *args):
        """
        Add temporary recipes to recipe definitions recipe list

        :param args:
        :return:
        """
        for arg in args:
            if isinstance(arg, TmpRecipe):
                self.recipes.append(arg)



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
