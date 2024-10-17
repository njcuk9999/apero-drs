#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2020-02-04 at 13:37

@author: cook
"""
import sys

from aperocore.base import base
from apero.base import base as apero_base
from aperocore.constants import param_functions
from aperocore.constants import load_functions
from aperocore.core import drs_log
from apero.core import drs_file
from aperocore.core import drs_misc
from apero.utils import drs_recipe
from apero.instruments import select

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'tools.module.testing.drs_dev.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__
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
    def __init__(self, instrument='None', name=None, filemod=None):
        # load super class
        super().__init__(instrument, name, filemod)


class RecipeDefinition:
    def __init__(self, instrument='None'):
        self.instrument = instrument
        self.recipes = []
        self.mod = None
        # populate recipes using instrument
        self.populate_recipes()

    def populate_recipes(self):
        # need to update filemod and recipe mod
        pconst = load_functions.load_pconfig(select.INSTRUMENTS)
        # update filemod
        recipemod = pconst.RECIPEMOD()
        # add to recipes
        self.recipes = recipemod.recipes
        self.recipemod = recipemod

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


class FileDefinition:
    def __init__(self, instrument='None'):
        self.instrument = instrument
        self.files = None
        self.out = None
        # populate files using instrument
        self.populate_files()

    def populate_files(self):
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

    def __init__(self, params=None):
        # get parameters
        if params is None:
            self.params = load_functions.load_config(select.INSTRUMENTS)
        else:
            self.params = params
        # get package
        self.package = params['DRS_PACKAGE']

    @staticmethod
    def setup():
        # deal with arguments
        if isinstance(sys.argv, list):
            args = list(sys.argv)
        else:
            args = str(sys.argv).split()
        # if we don't have the required arguments add them
        if len(args) < 2:
            sys.argv = ['demo', '1']
        return args

    def get_lang_db_loc(self):
        # get language database relative path
        relpath = base.LANG_DEFAULT_PATH
        # return absolute language database path
        return drs_misc.get_relative_folder(self.package, relpath)

    def change_lang(self, params, language):
        # update the language
        self.params.set('LANGUAGE', language)
        params.set('LANGUAGE', language)

    def test_data(self, params):
        # TODO: get test data from data/spirou/demo
        pass


# =============================================================================
# Define functions
# =============================================================================
def get_size(obj, seen=None):
    """
    Recursively finds size of objects

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
