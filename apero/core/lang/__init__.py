#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-17 at 14:31

@author: cook
"""
from apero.core.lang import drs_lang_text
from apero.core.lang import drs_lang_list

__all__ = ['textentry', 'Text']

# Access the langudate database with a key and return string
textentry = drs_lang_text.textentry

# the text class
Text = drs_lang_text.Text

# Language Error
DrsLanguageError = drs_lang_list.DrsLanguageError

# Common text
try:
    YES = drs_lang_text.textentry('C_YES')
    NO = drs_lang_text.textentry('C_NO')
    YES_OR_NO = drs_lang_text.textentry('C_YES_OR_NO')
    OPTIONS_ARE = drs_lang_text.textentry('C_OPTIONS_ARE')
    DEFAULT_IS = drs_lang_text.textentry('C_DEFAULT_IS')
    OR = drs_lang_text.textentry('C_OR')
    AND = drs_lang_text.textentry('C_AND')
except Exception as e:
    YES = 'Yes'
    NO = 'No'
    YES_OR_NO = 'Yes or No'
    OPTIONS_ARE = 'Options are'
    DEFAULT_IS = 'Default is'
    OR = 'or'
    AND = 'and'

# =============================================================================
# End of code
# =============================================================================
