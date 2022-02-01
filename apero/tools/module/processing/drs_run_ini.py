#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2021-11-08

@author: cook
"""
import os
from typing import Any, Dict, List, Optional, Union
from collections import OrderedDict

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
DrsSequence = drs_recipe.DrsRunSequence
# Get index database
IndexDatabase = drs_database.IndexDatabase
ObjectDatabase = drs_database.ObjectDatabase
# get text entry instance
textentry = lang.textentry
# define default master dir
DEFAULT_MASTER_OBSDIR = dict()
DEFAULT_MASTER_OBSDIR['SPIROU'] = '2020-08-31'
DEFAULT_MASTER_OBSDIR['NIRPS_HA'] = 'm20210605'
DEFAULT_MASTER_OBSDIR['NIRPS_HE'] = 'm20210605'
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
# define keys which should not be found as recipe RUN_ keys
EXCLUDE_RUN_KEYS = ['RUN_NAME', 'RUN_OBS_DIR']


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
        self.rkey('MASTER_OBS_DIR', DEFAULT_MASTER_OBSDIR[self.instrument])
        self.rkey('CORES', DEFAULT_CORES)
        # storage of recipes and sequences
        self.recipes = []
        self.sequences = []
        self.cmd_sequences = []
        self.ids = []
        # storage for user modified values
        self.run_keys_user_update = dict()
        self.run_extras = dict()
        self.skip_extras = dict()
        self.run_default = True
        self.skip_default = True
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

    def add_sequence_as_command(self, seqstr: str):
        """
        Add a sequence that generates a set of commands for the ids directly

        :param seqstr: str, the sequence name (must match the name of a
                       DrsRunSequence)
        :return:
        """
        # get sequence
        sequence = self.find_sequence(seqstr)
        # push into command sequence list
        self.cmd_sequences.append(sequence)

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
        if 'RUN_' in key and key not in EXCLUDE_RUN_KEYS:
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
        """
        Populate the text file

        :param params: ParamDict, parameter dictionary of constants

        :return:
        """
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
        groups = self._generate_recipe_list(mode='group')
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
                run_value = self.run_extras.get(srecipe, self.run_default)
                skip_value = self.skip_extras.get(srecipe, self.skip_default)
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
        # step 4: populate the lines
        # ---------------------------------------------------------------------
        # update run keys from user input (forced)
        for key in self.run_keys_user_update:
            self.run_keys[key] = self.run_keys_user_update[key]
        # ---------------------------------------------------------------------
        # step 5: deal with sequences to command line ids
        # ---------------------------------------------------------------------
        if len(self.cmd_sequences) > 0:
            self._add_command_sequences()
        # ---------------------------------------------------------------------
        # step 6: generate sequence / command text (via ids)
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
        # step 7: populate the lines
        # ---------------------------------------------------------------------
        # loop around lines
        for row in range(len(self.lines)):
            # update lines
            self.lines[row] = self.lines[row].format(**self.run_keys)


    def _generate_recipe_list(self, mode='group',
                             sequences: Optional[List[DrsSequence]] = None
                             ) -> Union[Dict[str, List[str]], List[DrsRecipe]]:
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
        # deal with having / not having sequence
        if sequences is None:
            sequences = self.sequences
        # deal with logging for group
        if mode == 'group':
            logmsg = True
        else:
            logmsg = False
        # loop around sequences
        for seq in sequences:
            # must process the adds
            seq.process_adds(self.params, tstars=list(tstars),
                             ostars=list(ostars), template_stars=template_olist,
                             logmsg=logmsg)
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
        if mode == 'group':
            return groups
        else:
            return recipes


    def _add_command_sequences(self):
        # TODO: finish this
        # copy params
        sparams = self.params.copy()
        # get sequence list
        sequencelist = []
        for sequence in self.cmd_sequences:
            sequencelist.append([sequence.name, sequence])
        # push run keys into sparams
        for run_key in self.run_keys:
            sparams[run_key] = self.run_keys[run_key]
        # get list of recipe groups for this set of sequences
        srecipes = self._generate_recipe_list(mode='recipes',
                                             sequences=self.cmd_sequences)
        # add recipe run keys
        for srecipe in srecipes:
            run_key = 'RUN_{0}'.format(srecipe.shortname)
            sparams[run_key] = True

        # generate run table
        runtable = OrderedDict()
        for it, sequence in enumerate(self.cmd_sequences):
            runtable[it] = sequence.name
        # get index database
        indexdbm = drs_database.IndexDatabase(sparams)
        # loop around sequences
        for sequence in sequencelist:
            # log progress
            WLOG(sparams, 'info', textentry('40-503-00009',
                                                args=[sequence[0]]))
            # generate new runs for sequence
            newruns = drs_processing._generate_run_from_sequence(sparams,
                                                                 sequence,
                                                                 indexdbm)
            for newrun in newruns:
                self.ids.append(newrun[0])




    def write_text_file(self):

        with open(self.outpath, 'w') as ofile:
            ofile.writelines(self.lines)



# =============================================================================
# Define functions
# =============================================================================
def get_runfiles(params: ParamDict) -> List[RunIniFile]:
    """
    Defines all possible run files

    :param params: ParamDict, parameter dictionary of constants

    :return: list of RunIniFile instances
    """
    # storage list
    run_files = []
    # -------------------------------------------------------------------------
    # create default runs files for SPIROU
    # -------------------------------------------------------------------------
    # blank run
    blank_run_spirou = RunIniFile(params, 'SPIROU', 'blank_run')
    blank_run_spirou.append_sequence('blank_seq')
    run_files.append(blank_run_spirou)
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
    quick_run_spirou.modify('RUN_PP_HC1HC1', False)
    quick_run_spirou.modify('RUN_PP_FPFP', False)
    quick_run_spirou.modify('RUN_PP_FF', False)
    quick_run_spirou.modify('RUN_PP_DFP', False)
    quick_run_spirou.modify('RUN_PP_SKY', False)
    quick_run_spirou.modify('RUN_PP_LFC', False)
    quick_run_spirou.modify('RUN_PP_LFCFP', False)
    quick_run_spirou.modify('RUN_PP_FPLFC', False)
    run_files.append(quick_run_spirou)
    # calib run
    calib_run_spirou = RunIniFile(params, 'SPIROU', 'calib_run')
    calib_run_spirou.append_sequence('pp_seq_opt')
    calib_run_spirou.append_sequence('calib_seq')
    calib_run_spirou.modify('RUN_PP_SCI', False)
    calib_run_spirou.modify('RUN_PP_TEL', False)
    calib_run_spirou.modify('RUN_PP_HC1HC1', False)
    calib_run_spirou.modify('RUN_PP_FPFP', False)
    calib_run_spirou.modify('RUN_PP_FF', False)
    calib_run_spirou.modify('RUN_PP_DFP', False)
    calib_run_spirou.modify('RUN_PP_SKY', False)
    calib_run_spirou.modify('RUN_PP_LFC', False)
    calib_run_spirou.modify('RUN_PP_LFCFP', False)
    calib_run_spirou.modify('RUN_PP_FPLFC', False)
    run_files.append(calib_run_spirou)
    # complete run
    complete_run_spirou = RunIniFile(params, 'SPIROU', 'complete_run')
    complete_run_spirou.append_sequence('full_seq')
    run_files.append(complete_run_spirou)
    # master calib run
    mcalib_run_spirou = RunIniFile(params, 'SPIROU', 'master_calib_run')
    mcalib_run_spirou.append_sequence('pp_seq_opt')
    mcalib_run_spirou.append_sequence('master_seq')
    mcalib_run_spirou.modify('RUN_PP_SCI', False)
    mcalib_run_spirou.modify('RUN_PP_TEL', False)
    mcalib_run_spirou.modify('RUN_PP_HC1HC1', False)
    mcalib_run_spirou.modify('RUN_PP_FPFP', False)
    mcalib_run_spirou.modify('RUN_PP_FF', False)
    mcalib_run_spirou.modify('RUN_PP_DFP', False)
    mcalib_run_spirou.modify('RUN_PP_SKY', False)
    mcalib_run_spirou.modify('RUN_PP_LFC', False)
    mcalib_run_spirou.modify('RUN_PP_LFCFP', False)
    mcalib_run_spirou.modify('RUN_PP_FPLFC', False)
    mcalib_run_spirou.modify('RUN_OBS_DIR', DEFAULT_MASTER_OBSDIR['SPIROU'])
    run_files.append(mcalib_run_spirou)
    # other run
    other_run_spirou = RunIniFile(params, 'SPIROU', 'other_run')
    other_run_spirou.append_sequence('pp_seq_opt')
    other_run_spirou.append_sequence('eng_seq')
    other_run_spirou.run_default = False
    run_files.append(other_run_spirou)
    # tellu run
    tellu_run_spirou = RunIniFile(params, 'SPIROU', 'tellu_run')
    tellu_run_spirou.append_sequence('pp_seq_opt')
    tellu_run_spirou.append_sequence('science_seq')
    tellu_run_spirou.modify('RUN_PP_CAL', False)
    tellu_run_spirou.modify('RUN_PP_SCI', False)
    tellu_run_spirou.modify('RUN_PP_HC1HC1', False)
    tellu_run_spirou.modify('RUN_PP_FPFP', False)
    tellu_run_spirou.modify('RUN_PP_FF', False)
    tellu_run_spirou.modify('RUN_PP_DFP', False)
    tellu_run_spirou.modify('RUN_PP_SKY', False)
    tellu_run_spirou.modify('RUN_PP_LFC', False)
    tellu_run_spirou.modify('RUN_PP_LFCFP', False)
    tellu_run_spirou.modify('RUN_PP_FPLFC', False)
    # science run
    science_run_spirou = RunIniFile(params, 'SPIROU', 'science_run')
    science_run_spirou.append_sequence('pp_seq_opt')
    science_run_spirou.append_sequence('science_seq')
    science_run_spirou.modify('RUN_PP_CAL', False)
    science_run_spirou.modify('RUN_PP_TEL', False)
    science_run_spirou.modify('RUN_PP_HC1HC1', False)
    science_run_spirou.modify('RUN_PP_FPFP', False)
    science_run_spirou.modify('RUN_PP_FF', False)
    science_run_spirou.modify('RUN_PP_DFP', False)
    science_run_spirou.modify('RUN_PP_SKY', False)
    science_run_spirou.modify('RUN_PP_LFC', False)
    science_run_spirou.modify('RUN_PP_LFCFP', False)
    science_run_spirou.modify('RUN_PP_FPLFC', False)
    science_run_spirou.modify('RECAL_TEMPLATES', False)
    run_files.append(science_run_spirou)
    # test run
    test_run_spirou = RunIniFile(params, 'SPIROU', 'test_run')
    test_run_spirou.append_sequence('limited_seq')
    test_run_spirou.run_default = False
    test_run_spirou.modify('TEST_RUN', True)
    run_files.append(test_run_spirou)
    # trigger night calib run
    tnc_run_spirou = RunIniFile(params, 'SPIROU', 'trigger_night_calib_run')
    tnc_run_spirou.append_sequence('pp_seq_opt')
    tnc_run_spirou.append_sequence('calib_seq')
    tnc_run_spirou.modify('RUN_PP_SCI', False)
    tnc_run_spirou.modify('RUN_PP_TEL', False)
    tnc_run_spirou.modify('RUN_PP_HC1HC1', False)
    tnc_run_spirou.modify('RUN_PP_FPFP', False)
    tnc_run_spirou.modify('RUN_PP_FF', False)
    tnc_run_spirou.modify('RUN_PP_DFP', False)
    tnc_run_spirou.modify('RUN_PP_SKY', False)
    tnc_run_spirou.modify('RUN_PP_LFC', False)
    tnc_run_spirou.modify('RUN_PP_LFCFP', False)
    tnc_run_spirou.modify('RUN_PP_FPLFC', False)
    tnc_run_spirou.modify('RECAL_TEMPLATES', False)
    tnc_run_spirou.modify('TRIGGER_RUN', True)
    run_files.append(tnc_run_spirou)
    # trigger night science run
    tns_run_spirou = RunIniFile(params, 'SPIROU', 'trigger_night_science_run')
    tns_run_spirou.append_sequence('pp_seq_opt')
    tns_run_spirou.append_sequence('science_seq')
    tns_run_spirou.modify('RUN_PP_CAL', False)
    tns_run_spirou.modify('RUN_PP_TEL', False)
    tns_run_spirou.modify('RUN_PP_HC1HC1', False)
    tns_run_spirou.modify('RUN_PP_FPFP', False)
    tns_run_spirou.modify('RUN_PP_FF', False)
    tns_run_spirou.modify('RUN_PP_DFP', False)
    tns_run_spirou.modify('RUN_PP_SKY', False)
    tns_run_spirou.modify('RUN_PP_LFC', False)
    tns_run_spirou.modify('RUN_PP_LFCFP', False)
    tns_run_spirou.modify('RUN_PP_FPLFC', False)
    tns_run_spirou.modify('RECAL_TEMPLATES', False)
    tns_run_spirou.modify('TRIGGER_RUN', True)
    run_files.append(tns_run_spirou)
    # batch run
    batch_run_spirou = RunIniFile(params, 'SPIROU', 'batch_run')
    batch_run_spirou.add_sequence_as_command('limited_seq')
    batch_run_spirou.modify('RUN_OBS_DIR', DEFAULT_MASTER_OBSDIR['SPIROU'])
    run_files.append(batch_run_spirou)
    # -------------------------------------------------------------------------
    # create default runs files for nirps_ha
    # -------------------------------------------------------------------------
    # blank run
    blank_run_nirps_ha = RunIniFile(params, 'NIRPS_HA', 'blank_run')
    blank_run_nirps_ha.append_sequence('blank_seq')
    run_files.append(blank_run_nirps_ha)
    # mini run
    mini_run_nirps_ha = RunIniFile(params, 'NIRPS_HA', 'mini_run')
    mini_run_nirps_ha.append_sequence('limited_seq')
    run_files.append(mini_run_nirps_ha)
    # quick run
    quick_run_nirps_ha = RunIniFile(params, 'NIRPS_HA', 'quick_run')
    quick_run_nirps_ha.append_sequence('pp_seq_opt')
    quick_run_nirps_ha.append_sequence('quick_seq')
    quick_run_nirps_ha.modify('RUN_PP_CAL', False)
    quick_run_nirps_ha.modify('RUN_PP_TEL', False)
    quick_run_nirps_ha.modify('RUN_PP_HC1HC1', False)
    quick_run_nirps_ha.modify('RUN_PP_FPFP', False)
    quick_run_nirps_ha.modify('RUN_PP_FF', False)
    quick_run_nirps_ha.modify('RUN_PP_DFP', False)
    quick_run_nirps_ha.modify('RUN_PP_SKY', False)
    quick_run_nirps_ha.modify('RUN_PP_LFC', False)
    quick_run_nirps_ha.modify('RUN_PP_LFCFP', False)
    quick_run_nirps_ha.modify('RUN_PP_FPLFC', False)
    run_files.append(quick_run_nirps_ha)
    # calib run
    calib_run_nirps_ha = RunIniFile(params, 'NIRPS_HA', 'calib_run')
    calib_run_nirps_ha.append_sequence('pp_seq_opt')
    calib_run_nirps_ha.append_sequence('calib_seq')
    calib_run_nirps_ha.modify('RUN_PP_SCI', False)
    calib_run_nirps_ha.modify('RUN_PP_TEL', False)
    calib_run_nirps_ha.modify('RUN_PP_HC1HC1', False)
    calib_run_nirps_ha.modify('RUN_PP_FPFP', False)
    calib_run_nirps_ha.modify('RUN_PP_FF', False)
    calib_run_nirps_ha.modify('RUN_PP_DFP', False)
    calib_run_nirps_ha.modify('RUN_PP_SKY', False)
    calib_run_nirps_ha.modify('RUN_PP_LFC', False)
    calib_run_nirps_ha.modify('RUN_PP_LFCFP', False)
    calib_run_nirps_ha.modify('RUN_PP_FPLFC', False)
    run_files.append(calib_run_nirps_ha)
    # complete run
    complete_run_nirps_ha = RunIniFile(params, 'NIRPS_HA', 'complete_run')
    complete_run_nirps_ha.append_sequence('full_seq')
    run_files.append(complete_run_nirps_ha)
    # master calib run
    mcalib_run_nirps_ha = RunIniFile(params, 'NIRPS_HA', 'master_calib_run')
    mcalib_run_nirps_ha.append_sequence('pp_seq_opt')
    mcalib_run_nirps_ha.append_sequence('master_seq')
    mcalib_run_nirps_ha.modify('RUN_PP_SCI', False)
    mcalib_run_nirps_ha.modify('RUN_PP_TEL', False)
    mcalib_run_nirps_ha.modify('RUN_PP_HC1HC1', False)
    mcalib_run_nirps_ha.modify('RUN_PP_FPFP', False)
    mcalib_run_nirps_ha.modify('RUN_PP_FF', False)
    mcalib_run_nirps_ha.modify('RUN_PP_DFP', False)
    mcalib_run_nirps_ha.modify('RUN_PP_SKY', False)
    mcalib_run_nirps_ha.modify('RUN_PP_LFC', False)
    mcalib_run_nirps_ha.modify('RUN_PP_LFCFP', False)
    mcalib_run_nirps_ha.modify('RUN_PP_FPLFC', False)
    mcalib_run_nirps_ha.modify('RUN_OBS_DIR', DEFAULT_MASTER_OBSDIR['NIRPS_HA'])
    run_files.append(mcalib_run_nirps_ha)
    # other run
    other_run_nirps_ha = RunIniFile(params, 'NIRPS_HA', 'other_run')
    other_run_nirps_ha.append_sequence('pp_seq_opt')
    other_run_nirps_ha.append_sequence('eng_seq')
    other_run_nirps_ha.run_default = False
    run_files.append(other_run_nirps_ha)
    # science run
    science_run_nirps_ha = RunIniFile(params, 'NIRPS_HA', 'science_run')
    science_run_nirps_ha.append_sequence('pp_seq_opt')
    science_run_nirps_ha.append_sequence('science_seq')
    science_run_nirps_ha.modify('RUN_PP_CAL', False)
    science_run_nirps_ha.modify('RUN_PP_TEL', False)
    science_run_nirps_ha.modify('RUN_PP_HC1HC1', False)
    science_run_nirps_ha.modify('RUN_PP_FPFP', False)
    science_run_nirps_ha.modify('RUN_PP_FF', False)
    science_run_nirps_ha.modify('RUN_PP_DFP', False)
    science_run_nirps_ha.modify('RUN_PP_SKY', False)
    science_run_nirps_ha.modify('RUN_PP_LFC', False)
    science_run_nirps_ha.modify('RUN_PP_LFCFP', False)
    science_run_nirps_ha.modify('RUN_PP_FPLFC', False)
    science_run_nirps_ha.modify('RECAL_TEMPLATES', False)
    run_files.append(science_run_nirps_ha)
    # tellu run
    tellu_run_nirps_ha = RunIniFile(params, 'NIRPS_HA', 'tellu_run')
    tellu_run_nirps_ha.append_sequence('pp_seq_opt')
    tellu_run_nirps_ha.append_sequence('science_seq')
    tellu_run_nirps_ha.modify('RUN_PP_CAL', False)
    tellu_run_nirps_ha.modify('RUN_PP_SCI', False)
    tellu_run_nirps_ha.modify('RUN_PP_HC1HC1', False)
    tellu_run_nirps_ha.modify('RUN_PP_FPFP', False)
    tellu_run_nirps_ha.modify('RUN_PP_FF', False)
    tellu_run_nirps_ha.modify('RUN_PP_DFP', False)
    tellu_run_nirps_ha.modify('RUN_PP_SKY', False)
    tellu_run_nirps_ha.modify('RUN_PP_LFC', False)
    tellu_run_nirps_ha.modify('RUN_PP_LFCFP', False)
    tellu_run_nirps_ha.modify('RUN_PP_FPLFC', False)
    run_files.append(tellu_run_nirps_ha)
    # test run
    test_run_nirps_ha = RunIniFile(params, 'NIRPS_HA', 'test_run')
    test_run_nirps_ha.append_sequence('limited_seq')
    test_run_nirps_ha.run_default = False
    test_run_nirps_ha.modify('TEST_RUN', True)
    run_files.append(test_run_nirps_ha)
    # batch run
    # batch_run_nirps_ha = RunIniFile(params, 'NIRPS_HA', 'batch_run')
    # batch_run_nirps_ha.add_sequence_as_command('limited_seq')
    # batch_run_nirps_ha.modify('RUN_OBS_DIR', DEFAULT_MASTER_OBSDIR['NIRPS_HA'])
    # run_files.append(batch_run_nirps_ha)
    # -------------------------------------------------------------------------
    # create default runs files for nirps_he
    # -------------------------------------------------------------------------
    # blank run
    blank_run_nirps_he = RunIniFile(params, 'NIRPS_HE', 'blank_run')
    blank_run_nirps_he.append_sequence('blank_seq')
    run_files.append(blank_run_nirps_he)
    # mini run
    mini_run_nirps_he = RunIniFile(params, 'NIRPS_HE', 'mini_run')
    mini_run_nirps_he.append_sequence('limited_seq')
    run_files.append(mini_run_nirps_he)
    # quick run
    quick_run_nirps_he = RunIniFile(params, 'NIRPS_HE', 'quick_run')
    quick_run_nirps_he.append_sequence('pp_seq_opt')
    quick_run_nirps_he.append_sequence('quick_seq')
    quick_run_nirps_he.modify('RUN_PP_CAL', False)
    quick_run_nirps_he.modify('RUN_PP_TEL', False)
    quick_run_nirps_he.modify('RUN_PP_HC1HC1', False)
    quick_run_nirps_he.modify('RUN_PP_FPFP', False)
    quick_run_nirps_he.modify('RUN_PP_FF', False)
    quick_run_nirps_he.modify('RUN_PP_DFP', False)
    quick_run_nirps_he.modify('RUN_PP_SKY', False)
    quick_run_nirps_he.modify('RUN_PP_LFC', False)
    quick_run_nirps_he.modify('RUN_PP_LFCFP', False)
    quick_run_nirps_he.modify('RUN_PP_FPLFC', False)
    run_files.append(quick_run_nirps_he)
    # calib run
    calib_run_nirps_he = RunIniFile(params, 'NIRPS_HE', 'calib_run')
    calib_run_nirps_he.append_sequence('pp_seq_opt')
    calib_run_nirps_he.append_sequence('calib_seq')
    calib_run_nirps_he.modify('RUN_PP_SCI', False)
    calib_run_nirps_he.modify('RUN_PP_TEL', False)
    calib_run_nirps_he.modify('RUN_PP_HC1HC1', False)
    calib_run_nirps_he.modify('RUN_PP_FPFP', False)
    calib_run_nirps_he.modify('RUN_PP_FF', False)
    calib_run_nirps_he.modify('RUN_PP_DFP', False)
    calib_run_nirps_he.modify('RUN_PP_SKY', False)
    calib_run_nirps_he.modify('RUN_PP_LFC', False)
    calib_run_nirps_he.modify('RUN_PP_LFCFP', False)
    calib_run_nirps_he.modify('RUN_PP_FPLFC', False)
    run_files.append(calib_run_nirps_he)
    # complete run
    complete_run_nirps_he = RunIniFile(params, 'NIRPS_HE', 'complete_run')
    complete_run_nirps_he.append_sequence('full_seq')
    run_files.append(complete_run_nirps_he)
    # master calib run
    mcalib_run_nirps_he = RunIniFile(params, 'NIRPS_HE', 'master_calib_run')
    mcalib_run_nirps_he.append_sequence('pp_seq_opt')
    mcalib_run_nirps_he.append_sequence('master_seq')
    mcalib_run_nirps_he.modify('RUN_PP_SCI', False)
    mcalib_run_nirps_he.modify('RUN_PP_TEL', False)
    mcalib_run_nirps_he.modify('RUN_PP_HC1HC1', False)
    mcalib_run_nirps_he.modify('RUN_PP_FPFP', False)
    mcalib_run_nirps_he.modify('RUN_PP_FF', False)
    mcalib_run_nirps_he.modify('RUN_PP_DFP', False)
    mcalib_run_nirps_he.modify('RUN_PP_SKY', False)
    mcalib_run_nirps_he.modify('RUN_PP_LFC', False)
    mcalib_run_nirps_he.modify('RUN_PP_LFCFP', False)
    mcalib_run_nirps_he.modify('RUN_PP_FPLFC', False)
    mcalib_run_nirps_he.modify('RUN_OBS_DIR', DEFAULT_MASTER_OBSDIR['NIRPS_HE'])
    run_files.append(mcalib_run_nirps_he)
    # other run
    other_run_nirps_he = RunIniFile(params, 'NIRPS_HE', 'other_run')
    other_run_nirps_he.append_sequence('pp_seq_opt')
    other_run_nirps_he.append_sequence('eng_seq')
    other_run_nirps_he.run_default = False
    run_files.append(other_run_nirps_he)
    # science run
    science_run_nirps_he = RunIniFile(params, 'NIRPS_HE', 'science_run')
    science_run_nirps_he.append_sequence('pp_seq_opt')
    science_run_nirps_he.append_sequence('science_seq')
    science_run_nirps_he.modify('RUN_PP_CAL', False)
    science_run_nirps_he.modify('RUN_PP_TEL', False)
    science_run_nirps_he.modify('RUN_PP_HC1HC1', False)
    science_run_nirps_he.modify('RUN_PP_FPFP', False)
    science_run_nirps_he.modify('RUN_PP_FF', False)
    science_run_nirps_he.modify('RUN_PP_DFP', False)
    science_run_nirps_he.modify('RUN_PP_SKY', False)
    science_run_nirps_he.modify('RUN_PP_LFC', False)
    science_run_nirps_he.modify('RUN_PP_LFCFP', False)
    science_run_nirps_he.modify('RUN_PP_FPLFC', False)
    science_run_nirps_he.modify('RECAL_TEMPLATES', False)
    # tellu run
    tellu_run_nirps_he = RunIniFile(params, 'NIRPS_HE', 'tellu_run')
    tellu_run_nirps_he.append_sequence('pp_seq_opt')
    tellu_run_nirps_he.append_sequence('science_seq')
    tellu_run_nirps_he.modify('RUN_PP_CAL', False)
    tellu_run_nirps_he.modify('RUN_PP_SCI', False)
    tellu_run_nirps_he.modify('RUN_PP_HC1HC1', False)
    tellu_run_nirps_he.modify('RUN_PP_FPFP', False)
    tellu_run_nirps_he.modify('RUN_PP_FF', False)
    tellu_run_nirps_he.modify('RUN_PP_DFP', False)
    tellu_run_nirps_he.modify('RUN_PP_SKY', False)
    tellu_run_nirps_he.modify('RUN_PP_LFC', False)
    tellu_run_nirps_he.modify('RUN_PP_LFCFP', False)
    tellu_run_nirps_he.modify('RUN_PP_FPLFC', False)
    run_files.append(tellu_run_nirps_ha)
    # test run
    test_run_nirps_he = RunIniFile(params, 'NIRPS_HE', 'test_run')
    test_run_nirps_he.append_sequence('limited_seq')
    test_run_nirps_he.run_default = False
    test_run_nirps_he.modify('TEST_RUN', True)
    run_files.append(test_run_nirps_he)
    # batch run
    # batch_run_nirps_he = RunIniFile(params, 'NIRPS_HE', 'batch_run')
    # batch_run_nirps_he.add_sequence_as_command('limited_seq')
    # batch_run_nirps_he.modify('RUN_OBS_DIR', DEFAULT_MASTER_OBSDIR['NIRPS_HE'])
    # run_files.append(batch_run_nirps_he)
    # -------------------------------------------------------------------------
    # return list of RunIniFile instances
    return run_files


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    _ = get_runfiles()


# =============================================================================
# End of code
# =============================================================================
