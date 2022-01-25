#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2021-07-22

@author: cook

Import Rules: Cannot use anything other than standard python 3 packages
(i.e. no numpy, no astropy etc)

"""
import csv
import os


# =============================================================================
# Define variables
# =============================================================================
# define the default language (must be the same as base.DEAFULT_LANG)
DEFAULT_LANG = 'ENG'
# define all allowed languages (must be the same as base.LANGUAGES)
LANGUAGES = ['ENG', 'FR']
# the language database path relative to this file (this is copied to this
#    directory when updating language database)
LANG_FILE = '../apero/lang/databases/reset.lang.csv'
# list of all keys required before access to full database allowed
KEYS = ['00-000-00009', '00-000-00010', '00-000-00011',
        '00-000-00013',
        '40-001-00075', '40-001-00076', '40-001-00077', '40-001-00078',
        '40-001-00079', '40-001-00080', '40-001-00081']


# =============================================================================
# Define functions
# =============================================================================
class LangDict:
    """
    Just for setup codes - only to be used until we can access apero
    (need to check modules + apero first)
    """
    def __init__(self, language: str = DEFAULT_LANG):
        self.language = language
        self.lang_dict = get_lang_dict(language)

    def __getitem__(self, item: str) -> str:
        """
        Dictionary style getting of item i.e. x[item]

        :param item: str, the key to get

        :return: str, the value of the key
        """
        return self.lang_dict[item]

    def error(self, code):
        return 'E[{0}]: {1}'.format(code, self.lang_dict[code])

    def warning(self, code):
        return 'E[{0}]: {1}'.format(code, self.lang_dict[code])


def get_lang_dict(language: str) -> dict:
    """
    Get the language file from csv file and convert to dictionary

    :return: dictionary, the filtered language dictionary
    """
    # get the full path to the language file
    fullpath = _rel_folder(LANG_FILE)
    # store the raw csv table
    storage = dict()
    with open(fullpath, newline='') as lang_file:
        reader = csv.DictReader(lang_file)
        for row in reader:
            for col in row:
                if col in storage:
                    storage[col].append(row[col])
                else:
                    storage[col] = [row[col]]
    # make sure language is in storage
    if language not in storage.keys():
        raise ValueError('Language not valid')
    # get langugate dictionary
    lang_dict = dict()
    # loop around keys we need
    for key in KEYS:
        # make sure we have key
        if key not in storage['KEYNAME']:
            continue
        # get position of key
        pos = storage['KEYNAME'].index(key)
        # try to get language key default to default language
        if storage[language][pos] == '':
            value = storage[DEFAULT_LANG][pos]
        else:
            value = storage[language][pos]
        # update dictionary
        lang_dict[key] = value
    # convert keys
    for entry in lang_dict:
        if '\\t' in lang_dict[entry]:
            lang_dict[entry] = lang_dict[entry].replace('\\t', '\t')
        if '\\n' in lang_dict[entry]:
            lang_dict[entry] = lang_dict[entry].replace('\\n', '\n')
    # return the language dictionary
    return lang_dict


def _rel_folder(reldir: str) -> str:
    """
    Get relative directory (compared to this file)

    :param reldir: str, a relative path compared to this file
    :return:
    """
    # Get the config_folder from relative path
    current = os.getcwd()
    # change to directory in where this file is
    os.chdir(os.path.dirname(__file__))
    # change to relative directory
    os.chdir(os.path.dirname(reldir))
    # get the absolute path of the folder
    absfolder = os.path.abspath(os.path.basename(reldir))
    # change back to current dir
    os.chdir(current)
    # return the absfolder
    return absfolder


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # update the items for use after this point
    lang = LangDict()


# =============================================================================
# End of code
# =============================================================================
