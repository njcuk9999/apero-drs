#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
apero add instrument

The purpose of this script is to add a new instrument to the apero package.

Created on 2024-10-10 at 10:58

@author: cook
"""
import glob
import os
from pathlib import Path
from typing import Dict, List

from astropy.time import Time

# =============================================================================
# Define variables
# =============================================================================
# define the base path of apero
BASE_INPATH = str(Path(__file__).resolve().parents[4])
BASE_OUTPATH = '/scratch2/spirou/drs-bin/apero-test/'
# define allowed extensions (to take off files)
EXTENSIONS = ['.py']
# get time now iso format
time_now = Time.now().iso


# =============================================================================
# Define classes
# =============================================================================
class AperoElement:
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.kind = None
        self.wildcard = None
        self.edits = dict()

    def process(self, instrument_name, class_name, author, starting_point):

        # deal with kwargsdict
        kwargsdict = dict()
        kwargsdict['instrument'] = instrument_name
        kwargsdict['INSTRUMENT'] = instrument_name.upper()
        kwargsdict['InstrumentClass'] = class_name
        kwargsdict['author'] = author
        kwargsdict['prev_inst'] = starting_point
        # processed based on kind
        if self.kind == 'dir':
            self.process_dir(kwargsdict)
        elif self.kind == 'multi-file-copy':
            self.process_multi_file_copy(kwargsdict)
        elif self.kind == 'file-copy':
            self.process_file_copy(kwargsdict)
        elif self.kind == 'file-edit':
            self.process_file_edit(kwargsdict)
        else:
            print('Kind not recognized')

    def process_dir(self, kwargdict: dict[str, str]):
        # get the relative path for this os
        relpath = self.get_rel_path()
        # make sure all arguments all pushed into relpath
        relpath = relpath.format(**kwargdict)
        # join to the base path
        path = os.path.join(BASE_OUTPATH, relpath)
        # print progress
        print(f'\nCreating directory {path}')
        # if path doesn't exist create this directory
        if not os.path.exists(path):
            os.makedirs(path)

    def process_file_copy(self, kwargdict: dict[str, str]):
        # get the relative path for this os
        rel_inpath = self.get_rel_path()
        # make sure all arguments all pushed into relpath
        rel_inpath = rel_inpath.format(instrument=kwargdict['prev_inst'])
        # get the relative path for this os
        rel_outpath = self.get_rel_path()
        # make sure all arguments all pushed into relpath
        rel_outpath = rel_outpath.format(instrument=kwargdict['instrument'])
        # get full paths
        inpath = os.path.join(BASE_INPATH, rel_inpath)
        outpath = os.path.join(BASE_OUTPATH, rel_outpath)
        # process single file copy and update
        self.process_single_file_copy(inpath, outpath, kwargdict)

    def process_single_file_copy(self, inpath, outpath, kwargdict):
        # print progress
        print(f'Editing with {outpath}')
        # deal with input file not existing
        if not os.path.exists(inpath):
            raise ValueError(f'File {inpath} does not exist')
        # deal with output file existing
        if os.path.exists(outpath):
            raise ValueError(f'File {outpath} already exists')
        # ---------------------------------------------------------------------
        # print progress
        print(f'\tReading {inpath}')
        # read the file
        with open(inpath, 'r') as f:
            content = f.read()
        # ---------------------------------------------------------------------
        # edit the content
        content = self.process_edits(content, kwargdict)
        # ---------------------------------------------------------------------
        # make sure directory exists
        outdir = os.path.dirname(outpath)
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        # print progress
        print(f'\tWriting {outpath}')
        # write the file
        with open(outpath, 'w') as f:
            f.write(content)

    def process_multi_file_copy(self, kwargdict: dict[str, str]):

        wildcard = '{' + self.wildcard + '}'
        # replace the wildcard
        rel_inpath = self.get_rel_path().replace(wildcard, '*')
        # make sure all arguments all pushed into relpath
        rel_inpath = rel_inpath.format(instrument=kwargdict['prev_inst'])
        # get the relative path for this os
        rel_outpath = self.get_rel_path().replace(wildcard, '*')
        # make sure all arguments all pushed into relpath
        rel_outpath = rel_outpath.format(instrument=kwargdict['instrument'])
        # get full paths
        inpath = os.path.join(BASE_INPATH, rel_inpath)
        outpath = os.path.join(BASE_OUTPATH, rel_outpath)
        # get paths
        inpaths = glob.glob(inpath)
        outpaths = glob.glob(outpath)
        # loop around all paths
        for inpath, outpath in zip(inpaths, outpaths):
            # get before and after wildcard from input
            before = self.get_rel_path().split(wildcard)[0]
            after = self.get_rel_path().split(wildcard)[-1]
            # get the wildcard value
            wildcard_value = inpath.split(before)[-1].split(after)[0]
            # add the wildcard value to the kwargdict
            kwargdict[self.wildcard] = wildcard_value
            # process single file copy and update
            self.process_single_file_copy(inpath, outpath, kwargdict)

    def process_file_edit(self, kwargdict: dict[str, str]):
        # get the relative path for this os
        rel_path = self.get_rel_path()
        # make sure all arguments all pushed into relpath
        rel_path = rel_path.format(instrument=kwargdict['instrument'])
        # copy file to new location
        path = os.path.join(BASE_INPATH, rel_path)
        if not os.path.exists(path):
            raise ValueError(f'File {path} does not exist')
        # ---------------------------------------------------------------------
        # print progress
        print(f'Reading {path}')
        # read the file
        with open(path, 'r') as f:
            content = f.read()
        # ---------------------------------------------------------------------
        # edit the content
        content = self.process_edits(content, kwargdict)
        # ---------------------------------------------------------------------
        # print progress
        print(f'Writing {path}')
        # write the file
        with open(path, 'w') as f:
            f.write(content)

    def process_edits(self, content: str, kwargdict: Dict[str, str]) -> str:
        for edit in self.edits:
            content = self.edits[edit].process(content, kwargdict)
        return content

    def get_rel_path(self) -> str:
        # set the extension to None at first
        extension = None
        # get the relative path
        relpath = str(self.path)
        # remove extension
        for ext in EXTENSIONS:
            if relpath.endswith(ext):
                relpath = relpath.replace(ext, '')
                extension = str(ext)
                break
        # get the relative path for this os
        relpath = relpath.replace('.', os.sep)
        # add extension back
        if extension is not None:
            relpath += extension
        # return relpath
        return relpath


class AperoEdit:
    def __init__(self, name, kind='replace'):
        """
        Edit class to store edit information

        :param name: str, the name of the edit
        :param kind: str, the kind of edit (replace, add)
        """
        self.name = name
        if kind not in ['replace', 'add']:
            raise ValueError(f'Error Edit: {self.name}: Kind must be replace '
                             f'or add not {kind}')
        else:
            self.kind = kind
        self.before = None
        self.after = None
        self.line = None
        self.content = None
        self.current_content = None
        self.new_content = None

    def process(self, content, kwargsdict):
        # deal with line edits
        if self.kind == 'replace':
            if self.line is not None:
                content = self.replace_line(content, kwargsdict)
            else:
                content = self.replace_element(content, kwargsdict)
        # deal with add edits
        elif self.kind == 'add':
            if self.line is not None:
                content = self.add_line(content, kwargsdict)
            else:
                raise ValueError(f'Element: {self.name}: Add edits must have '
                                 f'a line to add')
        # return content
        return content

    def replace_line(self, content: str, kwargsdict) -> str:
        # get inkwargsdict
        inkwargsdict = self.inkwargs(kwargsdict)
        # get current and new line
        current_line = self.line.format(**inkwargsdict)
        new_line = self.line.format(**kwargsdict)
        # replace line
        content = content.replace(current_line, new_line)
        # print progress
        print(f'\t\tReplaced {current_line} with {new_line}')
        # return content
        return content

    def replace_element(self, content: str, kwargsdict) -> str:
        # convert content to a single string
        content = '\n'.join(content)
        # get inkwargsdict
        inkwargsdict = self.inkwargs(kwargsdict)
        # deal with user definition being wrong
        if self.content is None:
            raise ValueError(f'Element: {self.name}: Content must be set for '
                             f'replace (when line=None)')
        if self.current_content is None:
            raise ValueError(f'Element: {self.name}: Current content must be '
                             f'set for replace (when line=None)')
        if self.new_content is None:
            raise ValueError(f'Element: {self.name}: New content must be set '
                             f'for replace (when line=None)')
        # set the content to current content
        kwargsdict['content'] = self.content
        # construct the find string
        current_content = self.current_content.format(**inkwargsdict)
        # set the content to the new content
        kwargsdict['content'] = self.new_content
        # construct the replace string
        new_content = self.new_content.format(**kwargsdict)
        # replace the content
        content = content.replace(current_content, new_content)
        # print progress
        print(f'\t\tReplaced {current_content} with {new_content}')
        # return content
        return content

    def inkwargs(self, kwargsdict: Dict[str, str]) -> Dict[str, str]:
        instrument_name = str(kwargsdict['prev_inst'])
        inkwargsdict = dict()
        inkwargsdict['instrument'] = instrument_name
        inkwargsdict['INSTRUMENT'] = instrument_name.upper()
        inkwargsdict['InstrumentClass'] = instrument_name.capitalize()
        inkwargsdict['author'] = 'NJC'
        inkwargsdict['new_inst'] = str(kwargsdict['instrument'])
        return inkwargsdict

    def get_pos(self, content) -> int:
        if self.before is not None:
            # get the index of the before line
            before = content.index(self.before)
            # deal with first line
            index = max(0, before - 1)
        else:
            # get the index of the before line
            after = content.index(self.after)
            # deal with last line
            index = min(len(content), after + 1)
        return index

    def add_line(self, content: str, kwargsdict) -> str:
        # get the line to add
        line = self.line.format(**kwargsdict)
        # get where we need to split
        index = self.get_pos(content)
        # split the content
        before = content[:index]
        after = content[index:]
        # add the line
        content = before + '\n' + line + '\n' +  after
        # print progress
        print(f'\t\tAdded {line}')
        # return content
        return content


# =============================================================================
# Define variables
# =============================================================================
CURRENT_INSTRUMENTS = ['spirou', 'nirps_he', 'nirps_ha']

# storage for elements
ELEMENTS = dict()


# Edit keywords
#  - instrument, INSTRUMENT
#  - InstrumentClass
#  - author

# add the instrument directory
element  = AperoElement('instrument', 'apero.instruments')
element.kind = 'dir'
ELEMENTS['instrument dir'] = element

# add the assets directory
element  = AperoElement('apero-assets', 'apero.apero-assets')
element.kind = 'dir'
ELEMENTS['apero assets dir'] = element

# add the config file
element  = AperoElement('config file', 'apero.instruments.{instrument}.config.py')
element.kind = 'file-copy'
element.edits['__NAME__'] = AperoEdit('__NAME__')
element.edits['__NAME__'].line = "__NAME__ = 'apero.instruments.{instrument}.config.py'"
element.edits['INSTRUMENT'] = AperoEdit('INSTRUMENT')
element.edits['INSTRUMENT'].line = "CDict.set('INSTRUMENT', value='{INSTRUMENT}', source=__NAME__, author='{author}')"
element.edits['title'] = AperoEdit('title')
element.edits['title'].content = 'Default parameters for {INSTRUMENT}'
element.edits['title'].current_content = '{INSTRUMENT}'
element.edits['title'].new_content = '{INSTRUMENT}'
element.edits['date'] = AperoEdit('date')
element.edits['date'].content = 'Created on {DATE}'
element.edits['date'].current_content = '{DATE}'
element.edits['date'].new_content = '{DATE}'
ELEMENTS['config file'] = element

# add the constants file
element = AperoElement('constants file', 'apero.instruments.{instrument}.constants.py')
element.kind = 'file-copy'
element.edits['__NAME__'] = AperoEdit('__NAME__')
element.edits['__NAME__'].line = "__NAME__ = 'apero.instruments.{instrument}.constants.py'"
element.edits['title'] = AperoEdit('title')
element.edits['title'].content = 'Default parameters for {INSTRUMENT}'
element.edits['title'].current_content = '{INSTRUMENT}'
element.edits['title'].new_content = '{INSTRUMENT}'
element.edits['date'] = AperoEdit('date')
element.edits['date'].content = 'Created on {DATE}'
element.edits['date'].current_content = '{DATE}'
element.edits['date'].new_content = '{DATE}'
ELEMENTS['constants file'] = element

# add the file definitions file
element = AperoElement('file definitions', 'apero.instruments.{instrument}.file_definitions.py')
element.kind = 'file-copy'
element.edits['__NAME__'] = AperoEdit('__NAME__')
element.edits['__NAME__'].line = "__NAME__ = 'apero.instruments.{instrument}.file_definitions.py'"
element.edits['__INSTRUMENT__'] = AperoEdit('__INSTRUMENT__')
element.edits['__INSTRUMENT__'].line = "__INSTRUMENT__ = '{INSTRUMENT}'"
element.edits['INSTRUMENT_NAME'] = AperoEdit('INSTRUMENT_NAME')
element.edits['INSTRUMENT_NAME'].line = "INSTRUMENT_NAME = '{instrument}'"
element.edits['title'] = AperoEdit('title')
element.edits['title'].content = 'Default parameters for {INSTRUMENT}'
element.edits['title'].current_content = '{INSTRUMENT}'
element.edits['title'].new_content = '{INSTRUMENT}'
element.edits['date'] = AperoEdit('date')
element.edits['date'].content = 'Created on {DATE}'
element.edits['date'].current_content = '{DATE}'
element.edits['date'].new_content = '{DATE}'
ELEMENTS['file definitions'] = element

# add the instrument file
element = AperoElement('instrument file', 'apero.instruments.{instrument}.instrument.py')
element.kind = 'file-copy'
element.edits['__NAME__'] = AperoEdit('__NAME__')
element.edits['__NAME__'].line = "__NAME__ = 'apero.instruments.{instrument}.instrument.py'"
element.edits['__INSTRUMENT__'] = AperoEdit('__INSTRUMENT__')
element.edits['__INSTRUMENT__'].line = "__INSTRUMENT__ = '{INSTRUMENT}'"
element.edits['class'] = AperoEdit('class')
element.edits['class'].line = "class {InstrumentClass}(instrument_mod.Instrument):"
element.edits['class_name'] = AperoEdit('class_name')
element.edits['class_name'].line = "    class_name = '{instrument}'"
element.edits['title'] = AperoEdit('title')
element.edits['title'].content = 'Pseudo constants (function) definitions for {INSTRUMENT}'
element.edits['title'].current_content = '{INSTRUMENT}'
element.edits['title'].new_content = '{INSTRUMENT}'
element.edits['date'] = AperoEdit('date')
element.edits['date'].content = 'Created on {DATE}'
element.edits['date'].current_content = '{DATE}'
element.edits['date'].new_content = '{DATE}'
ELEMENTS['instrument file'] = element

# add the recipe file
element = AperoElement('recipe file', 'apero.instruments.{instrument}.recipe_definitions.py')
element.kind = 'file-copy'
element.edits['file_def_import'] = AperoEdit('file_def_import')
element.edits['file_def_import'].line = 'from apero.instruments.{instrument} import file_definitions as files'
element.edits['__NAME__'] = AperoEdit('__NAME__')
element.edits['__NAME__'].line = "__NAME__ = 'apero.instruments.{instrument}.recipe_definitions.py'"
element.edits['__INSTRUMENT__'] = AperoEdit('__INSTRUMENT__')
element.edits['__INSTRUMENT__'].line = "__INSTRUMENT__ = '{INSTRUMENT}'"
element.edits['INSTRUMENT_ALIAS'] = AperoEdit('INSTRUMENT_ALIAS')
element.edits['INSTRUMENT_ALIAS'].line = "INSTRUMENT_ALIAS = '{instrument}'"
element.edits['import file def 1'] = AperoEdit('import file def 1')
element.edits['import file def 1'].line = "sf = base_class.ImportModule('{instrument}.file_definitions',"
element.edits['import file def 2'] = AperoEdit('import file def 2')
element.edits['import file def 2'].line = "                             'apero.instruments.{instrument}.file_definitions',"
element.edits['title'] = AperoEdit('title')
element.edits['title'].content = 'APERO Recipe definitions for {INSTRUMENT}'
element.edits['title'].current_content = '{INSTRUMENT}'
element.edits['title'].new_content = '{INSTRUMENT}'
element.edits['date'] = AperoEdit('date')
element.edits['date'].content = 'Created on {DATE}'
element.edits['date'].current_content = '{DATE}'
element.edits['date'].new_content = '{DATE}'
ELEMENTS['recipe file'] = element

# add the keywords file
element = AperoElement('keywords file', 'apero.instruments.{instrument}.keywords.py')
element.kind = 'file-copy'
element.edits['__NAME__'] = AperoEdit('__NAME__')
element.edits['__NAME__'].line = "__NAME__ = 'apero.instruments.{instrument}.keywords.py'"
element.edits['title'] = AperoEdit('title')
element.edits['title'].content = 'APERO DrsFile definitions for {INSTRUMENT}'
element.edits['title'].current_content = '{INSTRUMENT}'
element.edits['title'].new_content = '{INSTRUMENT}'
element.edits['date'] = AperoEdit('date')
element.edits['date'].content = 'Created on {DATE}'
element.edits['date'].current_content = '{DATE}'
element.edits['date'].new_content = '{DATE}'
ELEMENTS['keywords file'] = element

# add the base file
element = AperoElement('base file', 'apero.base.base.py')
element.kind = 'file-edit'
element.edits['INSTRUMENTS'] = AperoEdit('INSTRUMENTS')
element.edits['INSTRUMENTS'].kind = 'replace'
element.edits['INSTRUMENTS'].content = 'INSTRUMENTS = [{content}]'
element.edits['INSTRUMENTS'].current_content = ','.join(CURRENT_INSTRUMENTS)
element.edits['INSTRUMENTS'].new_content = ','.join(CURRENT_INSTRUMENTS + ['{instrument}'])
ELEMENTS['base file'] = element

# add the select file
element = AperoElement('select file', 'apero.instruments.select.py')
element.kind = 'file-edit'
element.edits['import'] = AperoEdit('import')
element.edits['import'].line = 'from apero.instruments.{instrument}.instrument import {InstrumentClass}'
element.edits['import'].kind = 'add'
element.edits['import'].before = '# New imports here'
element.edits['INSTRUMENTS'] = AperoEdit('INSTRUMENTS')
element.edits['INSTRUMENTS'].line = 'INSTRUMENTS[{INSTRUMENT}] = {InstrumentClass}'
element.edits['INSTRUMENTS'].kind = 'add'
element.edits['INSTRUMENTS'].before = '# New instruments here'
ELEMENTS['select file'] = element

# add the recipes/instrument directory
element = AperoElement('recipes/instrument dir', 'apero.recipes.{instrument}')
element.kind = 'dir'
ELEMENTS['recipes/instrument dir'] = element

# add all recipes from recipe directory
element = AperoElement('recipes', 'apero.recipes.{instrument}.{recipe}_{instrument}.py')
element.kind = 'multi-file-copy'
element.wildcard = 'recipe'
element.edits['__NAME__'] = AperoEdit('__NAME__')
element.edits['__NAME__'].line = "__NAME__ = '{recipe}_{instrument}.py"
element.edits['__INSTRUMENT__'] = AperoEdit('__INSTRUMENT__')
element.edits['__INSTRUMENT__'].line = "__INSTRUMENT__ = '{INSTRUMENT}'"
ELEMENTS['recipes'] = element

# add thhe tools/instrument directory
element = AperoElement('tools/instrument dir', 'apero.tools.{instrument}')
element.kind = 'dir'
ELEMENTS['tools/instrument dir'] = element

# =============================================================================
# Define functions
# =============================================================================
def main():
    # -------------------------------------------------------------------------
    # ask for authors initials
    author = input('Author initials (e.g. NJC): ')
    # -------------------------------------------------------------------------
    # ask for instrument name (no spaces, no special characters, other than _)
    instrument_name = input('Instrument name (no spaces, no special '
                            'characters, other than _): ')
    # -------------------------------------------------------------------------
    # ask for a starting point (e.g. copy from another instrument)
    starting_point = None
    # loop until option is valid
    while starting_point is None:
        # get starting options
        starting_options = CURRENT_INSTRUMENTS
        # ask user for starting point
        starting_question = ('Starting point (e.g. copy from another '
                             'instrument) options are: \n\t - {0} '
                             ''.format('\n\t - '.join(starting_options)))
        starting_question += 'Enter option:\t'
        starting_point = input(starting_question)
        # deal with bad input
        if starting_point not in starting_options:
            print('Starting point not recognized')
            starting_point = None
    # -------------------------------------------------------------------------
    # ask about the class name
    class_question = ('Class name (e.g. Spirou or NirpsHe or Nirps HA). '
                      'Should be CamelCase and contain no spaces or '
                      'punctuation: ')
    class_name = input(class_question)
    # -------------------------------------------------------------------------
    # print progress
    print('\n\n\n' + '*' * 50)
    print('Adding instrument: {0}'.format(instrument_name))
    print('\t - Author: {0}'.format(author))
    print('\t - Starting point: {0}'.format(starting_point))
    print('\t - Class name: {0}'.format(class_name))
    print('\n' + '*' * 50 + '\n')
    # loop around all elements
    for element in ELEMENTS.values():
        element.process(instrument_name, class_name, author, starting_point)
    # -------------------------------------------------------------------------
    return 0


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # run main code
    _ = main()

# =============================================================================
# End of code
# =============================================================================
