#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-07-29 at 14:40

@author: cook
"""
from typing import Dict

from aperocore.base import base

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
# Supported languages
SUPPORTED_LANGUAGES = base.LANGUAGES
# default language
DEFAULT_LANG = base.DEFAULT_LANG
# compiled language list
LANG_VALUES = dict()
LANG_COMMENTS = dict()
# define types of language items
ITEM_KINDS = ['code', 'help']


# =============================================================================
# Define functions
# =============================================================================
class DrsLanguageException(Exception):
    """Raised when base function is incorrect"""
    pass


class DrsLanguageError(DrsLanguageException):
    def __init__(self, message):
        self.message = message

    def __getstate__(self) -> dict:
        """
        For when we have to pickle the class
        :return:
        """
        # set state to __dict__
        state = dict(self.__dict__)
        # return dictionary state (for pickle)
        return state

    def __setstate__(self, state):
        """
        For when we have to unpickle the class

        :param state: dictionary from pickle
        :return:
        """
        # update dict with state
        self.__dict__.update(state)

    def __repr__(self):
        """
        String representation used for raise Exception message printing
        :return:
        """
        return self.message

    def __str__(self) -> str:
        """
        String representation used for raise Exception message printing
        :return:
        """
        return self.__repr__()


class LanguageItem:
    """
    A simple way to store language elements
    """
    key: str
    kind: str
    value: Dict[str, str]
    arguments: str
    comment: str

    def __init__(self, key: str, kind: str,
                 value: Dict[str, str] = None, comment: str = ''):
        """
        Construct a language item
        """
        # deal with key and kind
        self.key = key
        self.kind = kind
        # deal with value (should be a dictionary)
        if value is None:
            self.value = dict()
        # deal with comment
        self.comment = comment

    def validate(self):
        """
        Validate the language item
        """
        # check key is a string
        if not isinstance(self.key, str):
            return False
        # make sure kind is dealt with
        cond1 = 'code' in self.kind.lower()
        cond2 = 'help' in self.kind.lower()
        cond3 = 'text' in self.kind.lower()
        # look at kind types
        if not (cond1 or cond2 or cond3):
            emsg = 'LanguageItem kind "{0}"not in ITEM_KINDS for "{1}" '
            raise DrsLanguageError(emsg.format(self.kind, self.key))
        # make sure default language is in item.value
        if DEFAULT_LANG not in self.value:
            emsg = 'Default language ("{0}") not found in item.value for "{1}"'
            eargs = [DEFAULT_LANG, self.key]
            raise DrsLanguageError(emsg.format(*eargs))
        # deal with specific item kind
        if 'code' in self.kind.lower():
            # check format of string (should be NN-NNN-NNNNN)
            if len(self.key) != 12:
                emsg = ('LanguageItem key "{0}" not in correct format '
                        '(NN-NNN-NNNNN)')
                raise DrsLanguageError(emsg.format(self.key))
            # check we have correct structure for code
            keypairs = self.key.split('-')
            if len(keypairs) != 3:
                emsg = ('LanguageItem key "{0}" not in correct format '
                        '(NN-NNN-NNNNN)')
                raise DrsLanguageError(emsg.format(self.key))
            # check we have correct sub-structure for oode
            cond1 = len(keypairs[0]) != 2
            cond2 = len(keypairs[1]) != 3
            cond3 = len(keypairs[2]) != 5
            # raise error if any of the conditions are met
            if cond1 or cond2 or cond3:
                emsg = ('LanguageItem key "{0}" not in correct format '
                        '(NN-NNN-NNNNN)')
                raise DrsLanguageError(emsg.format(self.key))

    def __repr__(self):
        """
        String representation of the language item
        """
        return 'LanguageItem[key={0}]'.format(self.key)

    def __str__(self) -> str:
        """
        String representation of the language item
        """
        return self.__repr__()


class LanguageList:
    """
    Class to hold the language lists

    Can have multiple of these that compile in Language class to overwrite
    each other
    """
    def __init__(self, name: str):
        self.name = name
        self.language_dict: Dict[str, LanguageItem] = dict()

    def get(self, language: str, key: str):
        if language in SUPPORTED_LANGUAGES:
            item = self.language_dict.get(key, None)
            if item is not None:
                return item.value[language]
            else:
                return None
        else:
            return None

    @staticmethod
    def create(key: str, kind: str) -> LanguageItem:
        return LanguageItem(key, kind)

    def add(self, item: LanguageItem):
        """
        Add a Language Item to the this language list
        """
        # validate item
        item.validate()
        # add to the language dictionary
        self.language_dict[item.key] = item

    def __repr__(self):
        """
        String representation of the language item
        """
        return 'LanguageList[len={0}]'.format(len(self.language_dict))

    def __str__(self) -> str:
        """
        String representation of the language item
        """
        return self.__repr__()


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
