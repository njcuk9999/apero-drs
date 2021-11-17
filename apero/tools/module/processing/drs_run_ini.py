#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2021-11-08

@author: cook
"""
from typing import Any, Union

from apero import lang
from apero.base import base
from apero.core import constants
from apero.core.core import drs_log
from apero.core.core import drs_database
from apero.core.core import drs_file
from apero.core.core import drs_text
from apero.core.utils import drs_recipe
from apero.core.utils import drs_startup
from apero.science import telluric
from apero.tools.module.processing import drs_processing

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'drs_run.ini.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
ParamDict = constants.ParamDict
DrsRecipe = drs_recipe.DrsRecipe
DrsFitsFile = drs_file.DrsFitsFile
DrsInputFile = drs_file.DrsInputFile
# Get index database
IndexDatabase = drs_database.IndexDatabase
ObjectDatabase = drs_database.ObjectDatabase
# get text entry instance
textentry = lang.textentry
# define default master dir
DEFAULT_MASTER_OBSDIR = '2020-08-31'
# define default number of cores
DEFAULT_CORES = 5
# storage of run files
RUN_FILES = []


# =============================================================================
# Define classes
# =============================================================================
class RunIniFile:
    def __init__(self, instrument: str, name: str):
        # core properties
        self.name = name
        self.instrument = instrument
        # load params and pconst for use throughout
        self.params = constants.load(instrument)
        self.pconst = constants.pload(instrument)
        # import the recipe module
        self.recipemod = self.pconst.RECIPEMOD().get()
        # set a PID for this set up (to avoid error messages)
        self.params['PID'], _ = drs_startup.assign_pid()
        # get run keys (from startup)
        self.run_keys = dict(drs_startup.RUN_KEYS)
        # modify/add some values
        self.rkey('VERSION', __version__)
        self.rkey('DATE', __date__)
        self.rkey('RUN_NAME', 'Run {0}'.format(self.name))
        self.rkey('MASTER_OBS_DIR', DEFAULT_MASTER_OBSDIR)
        self.rkey('CORES', DEFAULT_CORES)
        # storage of recipes and sequences
        self.recipes = []
        self.sequences = []
        self.ids = []
        # storage of lines in the output file
        self.lines = []

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return 'RunIniFile[{0},{1}]'.format(self.instrument, self.name)

    def rkey(self, key: str, value: Any):
        """
        alias to self.run_keys[key] = value

        :param key: str, the key to update in run_keys dict
        :param value: Any, the value to update in run_keys dict

        :return: None, updates self.run_keys[key] with value
        """
        self.run_keys[key] = value

    def append_sequence(self, seqstr: str):
        """
        Append a sequence to the run.ini file

        :param seqstr: str, the sequence name (must match the name of a
                       DrsRunSequence)

        :return: None, updates self.sequences and self.ids
        """
        # get sequence
        sequence = self.find_sequence(seqstr)
        # push into lists
        self.sequences.append(sequence)
        self.ids.append(sequence.name)

    def append_command(self, command: str):
        """
        Append a single command to the run.ini file

        :param command: str, the command to add (all on one line)

        :return: None, updates self.ids
        """
        self.ids.append(command)

    def find_sequence(self, seqstr: str
                      ) -> Union[drs_recipe.DrsRunSequence, None]:
        """
        Find a sequence based on the string "seqstr"

        :param seqstr: str, the sequence name (must match the name of a
                       DrsRunSequence)

        :return: the DrsRunSequence class or raises an error if not found
        """
        # get list of seqeunces
        sequences = self.recipemod.sequences
        # search for sequence in sequences (based on name)
        for seq in sequences:
            if seq.name == seqstr:
                return seq
        # if we got to here sequence is invalid
        emsg = 'Invalid sequence: {0}'
        eargs = [seqstr]
        WLOG(self.params, 'error', emsg.format(*eargs))
        return None

    def populate_text_file(self):
        # TODO: fill this out using resources/run_ini/run_template.ini
        pass


    def generate_recipe_list(self):
        # construct the index database instance
        indexdbm = IndexDatabase(self.params)
        indexdbm.load_db()
        # get a list of object names with templates
        template_olist = []
        # get all telluric stars
        tstars = telluric.get_tellu_include_list(self.params)
        # get all other stars
        ostars = drs_processing.get_non_telluric_stars(self.params, indexdbm,
                                                       tstars)
        # ----------------------------------------------------------------------
        recipes, shortnames = [], []
        # loop around sequences
        for seq in self.sequences:
            # must process the adds
            seq.process_adds(self.params, tstars=list(tstars),
                             ostars=list(ostars), template_stars=template_olist)
            # loop around recipe in sequences
            for srecipe in seq.sequence:
                # only add unique recipes
                if srecipe.shortname not in shortnames:
                    # add recipe
                    recipes.append(srecipe)
                    # add short names
                    shortnames.append(srecipe.shortname)



# =============================================================================
# Define functions
# =============================================================================


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # -------------------------------------------------------------------------
    # create default runs files for spirou
    # -------------------------------------------------------------------------
    # mini run 1
    mini_run1_spirou = RunIniFile('SPIROU', 'mini_run1')
    mini_run1_spirou.rkey('MASTER_OBS_DIR', '2019-04-20')
    mini_run1_spirou.rkey('SCIENCE_TARGETS', 'Gl699')
    mini_run1_spirou.append_sequence('limited_seq')
    RUN_FILES.append(mini_run1_spirou)
    # mini run 2
    mini_run2_spirou = RunIniFile('SPIROU', 'mini_run2')
    mini_run2_spirou.rkey('MASTER_OBS_DIR', '2020-08-31')
    mini_run2_spirou.rkey('SCIENCE_TARGETS', 'Gl699')
    mini_run2_spirou.append_sequence('limited_seq')
    RUN_FILES.append(mini_run2_spirou)



# =============================================================================
# End of code
# =============================================================================
