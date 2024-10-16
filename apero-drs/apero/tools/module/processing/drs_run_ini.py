#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2021-11-08

@author: cook
"""
import os
from collections import OrderedDict
from typing import Any, Dict, List, Optional, Union

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

from aperocore.base import base
from aperocore.constants import param_functions
from aperocore.constants import load_functions
from aperocore import drs_lang
from apero.core import drs_database
from apero.core import drs_file
from aperocore.core import drs_log
from apero.constants import run_params
from apero.utils import drs_recipe

from apero.io import drs_path
from apero.science import telluric
from apero.tools.module.processing import drs_processing
from apero.instruments import select

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
ParamDict = param_functions.ParamDict
DrsRecipe = drs_recipe.DrsRecipe
DrsFitsFile = drs_file.DrsFitsFile
DrsInputFile = drs_file.DrsInputFile
DrsSequence = drs_recipe.DrsRunSequence
# Get index database
FileIndexDatabase = drs_database.FileIndexDatabase
ObjectDatabase = drs_database.AstrometricDatabase
# get text entry instance
textentry = drs_lang.textentry
# define default reference dir
DEFAULT_REF_OBSDIR = dict()
DEFAULT_REF_OBSDIR['SPIROU'] = '2020-08-31'
DEFAULT_REF_OBSDIR['NIRPS_HA'] = '2022-11-24'
DEFAULT_REF_OBSDIR['NIRPS_HE'] = '2022-11-24'
# define default number of cores
DEFAULT_CORES = 5
# define relative output path
OUTPATH = 'apero-assets/{instrument}/reset/runs/'
# template
TEMPLATE = 'tools/resources/run_ini/run_{instrument}.ini'
# define groups of recipes (each group is a list of recipe_kind from recipe
#   definitions)
GROUPS = dict()
GROUPS['preprocessing'] = ['pre']
GROUPS['reference calibration'] = ['calib-reference']
GROUPS['night calibration'] = ['calib-night']
GROUPS['extraction'] = ['extract']
GROUPS['telluric'] = ['tellu']
GROUPS['radial velocity'] = ['rv']
GROUPS['polar'] = ['polar']
GROUPS['lbl'] = ['lbl']
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
        self.pconst = load_functions.load_pconfig(select.INSTRUMENTS,
                                                  instrument)
        # import the recipe module
        self.recipemod = self.pconst.RECIPEMOD().get()
        # get run keys (from startup)
        self.run_keys = dict()
        # deep copy all parameters (so we can use them multiple times)
        for key in run_params.RUN_KEYS:
            self.run_keys[key] = run_params.RUN_KEYS[key].copy()
        # modify/add some values
        self.rkey('VERSION', __version__)
        self.rkey('DATE', __date__)
        self.rkey('RUN_NAME', 'Run {0}'.format(self.name))
        self.rkey('REF_OBS_DIR', DEFAULT_REF_OBSDIR[self.instrument])
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
        if key in self.run_keys:
            self.run_keys[key].value = value
        else:
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
        emsg = 'Invalid sequence: {0} [{1}] {2}'
        eargs = [seqstr, self.instrument, self.name]
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
        if 'RUN_' in key and key not in run_params.EXCLUDE_RUN_KEYS:
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

    def write_yaml_file(self, params: ParamDict):
        # ---------------------------------------------------------------------
        # step 1: construct output filename for this instrument
        # ---------------------------------------------------------------------
        # push in instrument name
        outpath = OUTPATH.format(instrument=self.instrument.lower())
        # get absolute outpath path
        outpath = drs_path.get_relative_folder(__PACKAGE__, outpath)
        # store in class
        self.outpath = os.path.join(outpath, self.name + '.yaml')
        # ---------------------------------------------------------------------
        # step 3: generate run text and skip text
        # ---------------------------------------------------------------------
        # storage of run and skips
        run_dict, skip_dict = dict(), dict()
        # get list of recipe groups for this set of sequences
        #   based on recipe_kind and GROUPS defined above
        groups = self._generate_recipe_list(mode='group')
        recipes = self._generate_recipe_list(mode='recipes')
        # get recipe look up dictionary
        recipe_dict = dict()
        for recipe in recipes:
            recipe_dict[recipe.shortname] = recipe
        # loop around recipes in sequence
        for group_name in groups:
            # get group
            group = groups[group_name]
            # deal with no entries
            if len(group) == 0:
                continue
            # loop around entries in group and add these rows
            for srecipe in group:
                # get run and skip values
                run_value = self.run_extras.get(srecipe, self.run_default)
                skip_value = self.skip_extras.get(srecipe, self.skip_default)
                # add group comment
                run_text = 'Run the {0} recipes\n'.format(group_name)
                skip_text = 'Skip the {0} recipes\n'.format(group_name)
                # get comment
                if srecipe in recipe_dict:
                    run_comment = f'Run {recipe_dict[srecipe].name}'
                    skip_comment = f'Skip {recipe_dict[srecipe].name}'
                else:
                    run_comment, skip_comment = None, None

                # push into instances
                run_inst = run_params.RunParam(name=srecipe, value=run_value,
                                               section=run_text,
                                               after=run_comment)
                skip_inst = run_params.RunParam(name=srecipe, value=skip_value,
                                                section=skip_text,
                                                after=skip_comment)
                # add to run_text and skip_text
                run_dict[srecipe] = run_inst
                skip_dict[srecipe] = skip_inst

        # ---------------------------------------------------------------------
        # add the runs to the run section
        if len(run_dict) == 0:
            self.run_keys['RUN_RECIPES'].value = None
        else:
            self.run_keys['RUN_RECIPES'].value = run_dict
        # ---------------------------------------------------------------------
        # add the skips to the skip section
        if len(skip_dict) == 0:
            self.run_keys['SKIP_RECIPES'].value = None
        else:
            self.run_keys['SKIP_RECIPES'].value = skip_dict
        # ---------------------------------------------------------------------
        # add the ids to the id section
        self.run_keys['IDS'].value = self.ids
        # ---------------------------------------------------------------------
        # Create a commented map
        data = CommentedMap()
        # add start comment
        title = run_params.RUN_YAML_TITLE.format(__version__, __date__)
        data.yaml_set_start_comment(title)
        # ---------------------------------------------------------------------
        # set section title
        section_title = None
        # loop around run string
        for key in self.run_keys:
            # deal with keys that aren't run keys
            # TODO: remove this once we are only using yaml
            if not isinstance(self.run_keys[key], run_params.RunParam):
                continue
            # get the value
            value = self.run_keys[key].value
            # deal with dictionary as value
            if isinstance(value, dict):
                # set up a new commented map
                data[key] = CommentedMap()
                # push dictionary values into data
                for subkey in value:
                    # deal with non RunParam as sub value
                    if not isinstance(value[subkey], run_params.RunParam):
                        data[key][subkey] = value[subkey]
                        continue
                    # get value from sub key
                    data[key][subkey] = value[subkey].value
                    # create comment text
                    comment = value[subkey].create_comment(section_title,
                                                           no_header=True)
                    # update section title
                    section_title = str(value[subkey].section)
                    # add comment before the key
                    ckwargs = dict(key=subkey, before=comment, indent=2)
                    data[key].yaml_set_comment_before_after_key(**ckwargs)
                    # deal with after key
                    if value[subkey].after is not None:
                        # add comment after the key
                        ckwargs = dict(key=subkey, comment=value[subkey].after,
                                       column=35)
                        data[key].yaml_add_eol_comment(**ckwargs)
            else:
                # set value for data
                data[key] = self.run_keys[key].value
            # create comment text
            comment = self.run_keys[key].create_comment(section_title)
            # update section title
            section_title = str(self.run_keys[key].section)
            # add comment before the key
            ckwargs = dict(key=key, before=comment, indent=0)
            data.yaml_set_comment_before_after_key(**ckwargs)



        # ---------------------------------------------------------------------
        # print message
        msg = '\tWriting yaml file: {0}'
        margs = [self.outpath]
        WLOG(params, '', msg.format(*margs))
        # initialize YAML object
        yaml_inst = YAML()
        # write files
        with open(self.outpath, 'w') as y_file:
            yaml_inst.dump(data, y_file)


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
        outpath = drs_path.get_relative_folder(__PACKAGE__, outpath)
        # store in class
        self.outpath = os.path.join(outpath, self.name + '.ini')
        # ---------------------------------------------------------------------
        # step 2: load the template run.ini file for this instrument
        # ---------------------------------------------------------------------
        # push in instrument name
        template = TEMPLATE.format(instrument=self.instrument.lower())
        # get absolute template path
        template = drs_path.get_relative_folder(__PACKAGE__, template)
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
        #   based on recipe_kind and GROUPS defined above
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
            self.run_keys[key].value = self.run_keys_user_update[key]
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
        # map run key values into run key dict
        run_key_dict = dict()
        for key in self.run_keys:
            if isinstance(self.run_keys[key], run_params.RunParam):
                run_key_dict[key] = self.run_keys[key].value
            else:
                run_key_dict[key] = self.run_keys[key]
        # loop around lines
        for row in range(len(self.lines)):
            # update lines
            self.lines[row] = self.lines[row].format(**run_key_dict)

    def _generate_recipe_list(self, mode='group',
                              sequences: Optional[List[DrsSequence]] = None
                              ) -> Union[Dict[str, List[str]], List[DrsRecipe]]:
        # construct the index database instance
        findexdbm = FileIndexDatabase(self.params)
        findexdbm.load_db()
        # get a list of object names with templates
        template_olist = []
        # get a list of all objects from the file index database
        all_objects = drs_processing.get_uobjs_from_findex(self.params,
                                                           findexdbm)
        # get all telluric stars
        tstars = telluric.get_tellu_include_list(self.params,
                                                 all_objects=all_objects)
        # get all other stars
        ostars = drs_processing.get_non_telluric_stars(self.params, all_objects,
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

                if not found:
                    wmsg = ('Recipe {0} ({1}) not in valid group (add {2} to '
                            '{3}.GROUP)')
                    wargs = [srecipe.name, shortname, recipe_kind, __NAME__]
                    WLOG(self.params, 'warning', wmsg.format(*wargs))

        # ---------------------------------------------------------------------
        if mode == 'group':
            return groups
        else:
            return recipes

    def _add_command_sequences(self):
        """
        Add command sequences (i.e. for a batch job)

        This converts a sequence or set of sequences to a set of individual
        commands based on current directories

        :return:
        """

        # get run obs dir
        run_dir = self.run_keys['RUN_OBS_DIR']
        # get the raw dir
        raw_dir = self.params['DRS_DATA_RAW']
        # get raw run dir
        raw_run_dir = os.path.join(raw_dir, run_dir)
        # make sure raw run dir is present - if not we have to skip
        if not os.path.exists(raw_run_dir):
            wmsg = 'Skipping {0} [{1}]. Run directory: {2} does not exist'
            wargs = [self.name, self.instrument, raw_run_dir]
            WLOG(self.params, 'warning', wmsg.format(*wargs))
            return
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
        findexdbm = drs_database.FileIndexDatabase(sparams)
        # loop around sequences
        for sequence in sequencelist:
            # log progress
            WLOG(sparams, 'info', textentry('40-503-00009',
                                            args=[sequence[0]]))
            # generate new runs for sequence
            newruns = drs_processing.generate_run_from_sequence(sparams,
                                                                sequence,
                                                                findexdbm)
            for newrun in newruns:
                self.ids.append(newrun[0])

    def write_text_file(self):

        with open(self.outpath, 'w') as ofile:
            ofile.writelines(self.lines)


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # Main code here
    pass

# =============================================================================
# End of code
# =============================================================================
