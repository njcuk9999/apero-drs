#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2021-11-08

@author: cook
"""
import os
from typing import Any, Dict, List, Union

from apero import lang
from apero.base import base
from apero.core import constants
from apero.core.core import drs_log
from apero.core.core import drs_database
from apero.core.core import drs_file
from apero.core.core import drs_text
from apero.core.utils import drs_recipe
from apero.core.utils import drs_startup
from apero.io import drs_path
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
# define relative output path
OUTPATH = 'data/{instrument}/reset/runs/'
# template
TEMPLATE = 'tools/resources/run_ini/run_{instrument}.ini'
# define groups of recipes
GROUPS = dict()
GROUPS['preprocessing'] = ['pre']
GROUPS['master calibration'] = ['calib-master']
GROUPS['night calibration'] = ['calib-night']
GROUPS['extraction'] = ['extract']
GROUPS['telluric'] = ['tellu']
GROUPS['radial velocity'] = ['rv']
GROUPS['polar'] = ['polar']
GROUPS['postprocessing'] = ['post']


# =============================================================================
# Define classes
# =============================================================================
class RunIniFile:
    def __init__(self, params: ParamDict, instrument: str, name: str):
        # core properties
        self.name = name
        self.instrument = instrument
        # load params and pconst for use throughout
        self.params = params
        self.pconst = constants.pload(instrument)
        # import the recipe module
        self.recipemod = self.pconst.RECIPEMOD().get()
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
        # storage for user modified values
        self.run_keys_user_update = dict()
        self.run_extras = dict()
        self.skip_extras = dict()
        # storage of lines in the output file
        self.lines = []
        # storage of outpath
        self.outpath = None

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

    def modify(self, key: str, value: Any):
        """
        Modify the run_keys or run_text/skip_Text just before they are
        used (only if present)

        :param key: str, the run_key or run_text or skip_text to modify
        :param value: Any, the value to push into run_key

        :return: None, updates run key
        """
        # deal with run keys
        if 'RUN_' in key:
            # get srecipe name
            srecipe = key.split('RUN_')[-1]
            # push into run_extras
            self.run_extras[srecipe] = value
        # deal with skip keys
        elif 'SKIP_' in key:
            # get srecipe name
            srecipe = key.split('SKIP_')[-1]
            # push into run_extras
            self.skip_extras[srecipe] = value
        # else push into run keys user update
        else:
            self.run_keys_user_update[key] = value

    def populate_text_file(self, params: ParamDict):
        # ---------------------------------------------------------------------
        # step 1: construct output filename for this instrument
        # ---------------------------------------------------------------------
        # push in instrument name
        outpath = OUTPATH.format(instrument=self.instrument.lower())
        # get absolute outpath path
        outpath = drs_path.get_relative_folder(params, __PACKAGE__, outpath)
        # store in class
        self.outpath = os.path.join(outpath, self.name + '.ini')
        # ---------------------------------------------------------------------
        # step 2: load the template run.ini file for this instrument
        # ---------------------------------------------------------------------
        # push in instrument name
        template = TEMPLATE.format(instrument=self.instrument.lower())
        # get absolute template path
        template = drs_path.get_relative_folder(params, __PACKAGE__, template)
        # load template
        if os.path.exists(template):
            with open(template, 'r') as tfile:
                self.lines = tfile.readlines()
        else:
            emsg = 'Template file does not exist: {0}'
            eargs = [template]
            WLOG(params, 'error', emsg.format(*eargs))
        # ---------------------------------------------------------------------
        # step 3: generate run text and skip text
        # ---------------------------------------------------------------------
        # get list of recipe groups for this set of sequences
        groups = self.generate_recipe_list()
        # storage for the run and skip text
        run_text, skip_text = '', ''
        # loop around recipes in sequence
        for group_name in groups:
            # get group
            group = groups[group_name]
            # deal with no entries
            if len(group) == 0:
                continue
            # add group comment
            run_text += '\n# Run the {0} recipes\n'.format(group_name)
            skip_text += '\n# Skip the {0} recipes\n'.format(group_name)
            # loop around entries in group and add these rows
            for srecipe in group:
                # get run and skip values
                run_value = self.run_extras.get(srecipe, True)
                skip_value = self.skip_extras.get(srecipe, True)
                # add to run_text and skip_text
                run_text += 'RUN_{0} = {1}\n'.format(srecipe, run_value)
                skip_text += 'SKIP_{0} = {1}\n'.format(srecipe, skip_value)
        # deal with blank
        if len(run_text) == 0:
            run_text = '# No sequence recipes to run\n'
            skip_text = '# No sequence recipes to skip\n'

        # push into run_keys
        self.rkey('RUN_TEXT', run_text)
        self.rkey('SKIP_TEXT', skip_text)
        # ---------------------------------------------------------------------
        # step 4: generate sequence / command text (via ids)
        # ---------------------------------------------------------------------
        # storage for id text
        id_text = '\n'
        # loop around ids
        for it in range(len(self.ids)):
            # add ids (be it sequence or command
            id_text += 'id{0:05d} = {1}\n'.format(it, self.ids[it])
        # push into run_keys
        self.rkey('SEQUENCE_TEXT', id_text)
        # ---------------------------------------------------------------------
        # step 5: populate the lines
        # ---------------------------------------------------------------------
        # update run keys from user input (forced)
        for key in self.run_keys_user_update:
            self.run_keys[key] = self.run_keys_user_update[key]
        # ---------------------------------------------------------------------
        # step 6: populate the lines
        # ---------------------------------------------------------------------
        # loop around lines
        for row in range(len(self.lines)):
            # update lines
            self.lines[row] = self.lines[row].format(**self.run_keys)

    def generate_recipe_list(self) -> Dict[str, List[str]]:
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
        groups = dict()
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

                recipe_kind = srecipe.recipe_kind
                shortname = srecipe.shortname
                # set found to False
                found = False
                # loop around processing groups
                for group in GROUPS:
                    # if already found break
                    if found:
                        break
                    # loop around text in group
                    for text in GROUPS[group]:
                        # if we have found the text in recipe kind it belongs
                        #   to this group
                        if text in recipe_kind:
                            # set found to True - we add it to the first group
                            #   only that matches some text portion
                            found = True
                            # deal with group already present in groups
                            if group in groups:
                                groups[group].append(shortname)
                            # deal with group not present in groups
                            else:
                                groups[group] = [shortname]
        # ---------------------------------------------------------------------
        return groups

    def write_text_file(self):

        with open(self.outpath, 'w') as ofile:
            ofile.writelines(self.lines)



# =============================================================================
# Define functions
# =============================================================================
def main(params: ParamDict) -> List[RunIniFile]:
    # storage list
    run_files = []
    # -------------------------------------------------------------------------
    # create default runs files for spirou
    # -------------------------------------------------------------------------
    # blank run
    blank_run = RunIniFile(params, 'SPIROU', 'blank_run')
    blank_run.append_sequence('blank_seq')
    run_files.append(blank_run)
    # mini run 1
    mini_run1_spirou = RunIniFile(params, 'SPIROU', 'mini_run1')
    mini_run1_spirou.rkey('MASTER_OBS_DIR', '2019-04-20')
    mini_run1_spirou.rkey('SCIENCE_TARGETS', 'Gl699')
    mini_run1_spirou.append_sequence('limited_seq')
    run_files.append(mini_run1_spirou)
    # mini run 2
    mini_run2_spirou = RunIniFile(params, 'SPIROU', 'mini_run2')
    mini_run2_spirou.rkey('SCIENCE_TARGETS', 'Gl699')
    mini_run2_spirou.append_sequence('limited_seq')
    run_files.append(mini_run2_spirou)
    # quick run
    quick_run_spirou = RunIniFile(params, 'SPIROU', 'quick_run')
    quick_run_spirou.append_sequence('pp_seq_opt')
    quick_run_spirou.append_sequence('quick_seq')
    quick_run_spirou.modify('RUN_PP_CAL', False)
    quick_run_spirou.modify('RUN_PP_TEL', False)
    run_files.append(quick_run_spirou)
    # calib run
    calib_run_spirou = RunIniFile(params, 'SPIROU', 'calib_run')
    calib_run_spirou.append_sequence('pp_seq_opt')
    calib_run_spirou.append_sequence('calib_seq')
    calib_run_spirou.modify('RUN_PP_SCI', False)
    calib_run_spirou.modify('RUN_PP_TEL', False)
    # complete run

    # master calib run

    # other run

    # science run

    # trigger night calib run

    # trigger night science run

    # -------------------------------------------------------------------------
    # create default runs files for nirps_ha
    # -------------------------------------------------------------------------


    # return list of RunIniFile instances
    return run_files


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    _ = main()


# =============================================================================
# End of code
# =============================================================================
