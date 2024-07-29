#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-07-29 at 08:53

@author: cook

only from:
    - apero.base.base
    - apero.base.drs_base
    - apero.base.drs_db
"""
from typing import Any, Dict, List

from apero.base import base
from apero.core.core import drs_base_classes as base_class
from apero.core.lang import drs_lang_list

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero.lang.drs_lang.py'
__PACKAGE__ = base.__PACKAGE__
__INSTRUMENT__ = 'None'
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# -----------------------------------------------------------------------------
# Languge error code
LANG_ERROR_CODE = '00-000-00014'
# Supported languages
SUPPORTED_LANGUAGES = base.LANGUAGES
# default language
DEFAULT_LANG = base.DEFAULT_LANG
# compiled language list
LANG_VALUES = dict()
LANG_COMMENTS = dict()
# get classes from drs_lang_list
DrsLanguageError = drs_lang_list.DrsLanguageError
LanguageList = drs_lang_list.LanguageList
LanguageItem = drs_lang_list.LanguageItem


# =============================================================================
# Define Language function
# =============================================================================
class LanguageLookup:
    """
    Class to get text in the correct language from the lanuage lists
    """
    def __init__(self, lang_insts: List[LanguageList] = None,
                 langauge=DEFAULT_LANG):
        self.language: str = langauge
        # compile only once
        if len(LANG_VALUES) == 0:
            self.lang_insts = lang_insts
            self._compile()
        # get lang
        self.lang_values = LANG_VALUES
        self.lang_comments = LANG_COMMENTS

    def _compile(self):
        """
        Compile a single language list from all language instances, by this
        point the code is running and we only have one language from one
        set of sources where lower sources overwrite higher sources
        (i.e. instrument values overwrite default values)

        This should only be in memory once and does not need to be run multiple
        times
        """
        global LANG_VALUES
        global LANG_COMMENTS
        # loop around all language instances
        for lang_inst in self.lang_insts:
            for key in lang_inst.language_dict:
                # get item
                item = lang_inst.language_dict[key]
                # deal with no item
                if item is None:
                    continue
                # get the new value from the language list
                # deal with no value
                if self.language not in item.value:
                    value = item.value[DEFAULT_LANG]
                else:
                    value = item.value[self.language]
                comment = item.comment
                # overwrite value in LANG_VALUES/LANG_COMMENTS
                LANG_VALUES[key] = value
                LANG_COMMENTS[key] = comment

    def __getitem__(self, key: str) -> Any:
        """
        Get a value (after compiling)
        """
        # get key from language values
        value = LANG_VALUES.get(key, None)
        # deal with no value
        if value is None:
            emsg = 'Key "{0}" not found in language lists.'
            eargs = [key]
            raise DrsLanguageError(emsg.format(*eargs))
        # return value
        else:
            return value

    def get(self, key: str, kind: str = 'value') -> Any:
        """
        Get a value or comment (after compiling)
        """
        if kind == 'value':
            return self.__getitem__(key)
        elif kind == 'comment':
            return LANG_COMMENTS.get(key, None)
        else:
            return None


def get_instrument_args() -> Dict[str, Any]:
    """
    Get the arguments for the Language class for the current instrument

    :return kwargs: dict, the arguments for the Language class
    """
    # load the install yaml
    iparams = base.load_install_yaml()
    # get module names for instrument
    lang_mod_names = iparams['DRS_LANG_MODULES']
    # storage of language lists for instrument
    lang_lists = []
    # loop around modules
    for module_name in lang_mod_names:
        try:
            modinst = base_class.ImportModule(module_name,
                                          module_name)
            # load the module
            mod = modinst.get()
            # Get the language list from the module
            # noinspection PyUnresolvedReferences
            langlist = mod.langlist
            # append to list of language lists
            lang_lists.append(langlist)

        except Exception as e:
            emsg = 'Language module "{0}" not found. \n\t{1}: {2}'
            eargs = [module_name, type(e), str(e)]
            raise DrsLanguageError(emsg.format(*eargs))

    # store as dictionary
    lang_kwargs = dict(lang_insts=lang_lists,
                       langauge=iparams['LANGUAGE'])
    # return the arguments for the Language class
    return lang_kwargs


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
