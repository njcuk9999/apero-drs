#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-23 at 17:55

@author: cook
"""
from apero.lang.core import drs_lang

__all__ = ['textentry']

# Access the langudate database with a key and return string
textentry = drs_lang.textentry

# the text class
Text = drs_lang.Text

# Common text
YES = drs_lang.textentry('C_YES')
NO = drs_lang.textentry('C_NO')
YES_OR_NO = drs_lang.textentry('C_YES_OR_NO')
OPTIONS_ARE = drs_lang.textentry('C_OPTIONS_ARE')
DEFAULT_IS = drs_lang.textentry(('C_DEFAULT_IS'))
OR = drs_lang.textentry('C_OR')
AND = drs_lang.textentry('C_AND')

# =============================================================================
# End of code
# =============================================================================
