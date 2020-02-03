#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2020-01-28 at 11:56

@author: cook

Import rules: Cannot import from drs
"""
# Do not import from the drs

# =============================================================================
# Define variables
# =============================================================================
# Define package name
PACKAGE = 'apero'

# =============================================================================
# Define functions
# =============================================================================
def get_entries(language='ENG'):
    # if language requested is english use english dict function
    if language == 'ENG':
        return get_entries_eng()
    # else revert to english dict function
    else:
        return get_entries_eng()


# noinspection PyPep8
def get_entries_eng():
    # set the entries dictionary
    #   this is keys that are used ONLY in functions which cannot
    #   access the language database - note these will have to be
    #   manually updated here if changed in the database

    # try to keep these in order

    vs = dict()

    vs[''] = ""

    vs['00-000-00003'] = "Cannot import module '{0}' from '{1}' \n\t Function = {2} \n\t Error {3}: {4} \n\n Traceback: \n\n {5}"

    vs['00-004-00003'] = "File '{0}' cannot be read by {1} \n\t Error {2}: {3}"

    vs['00-004-00004'] = "File '{0}' cannot be written by {1} \n\t Error {2}: {3}"

    vs['00-003-00002'] = "Parameter '{0}' can not be converted to a list. \n\t Error {1}: {2}. \n\t function = {3}"

    vs['00-003-00003'] = "Parameter '{0}' can not be converted to a dictionary. \n\t Error {1}: {2}. \n\t function = {3}"

    vs['00-003-00005'] = "Folder '{0}' does not exist in {1}"

    vs['00-003-00006'] = "Duplicate Const parameter {0} for instrument '{1}' \n\t Module list: {2} \n\t Function = {3}"

    vs['00-003-00007'] = "Must define new source when copying a Constant \n\t Syntax: Constant.copy(source) \n\t where 'source' is a string \n\t Function = {0}"

    vs['00-003-00008'] = "Must define new source when copying a Keyword \n\t Syntax: Keyword.copy(source) \n\t where 'source' is a string \n\t Function = {0}"

    vs['00-003-00009'] = "Parameter '{0}' must be a string. \n\t Type: '{1}' \n\t Value: '{2}' \n\t Config File = '{3}' \n\t Function = {4}"

    vs['00-003-00010'] = "Const validate error - Key {0}: Path does not exist '{1}' \n\t Function = {2}"

    vs['00-003-00011'] = "Parameter '{0}' should be a list not a string. \n\t Value = {1} \n\t Config File = '{2}' \n\t Function = {3}"

    vs['00-003-00012'] = "Parameter '{0}' dtype is incorrect. Expected '{1}' value='{2}' (dtype={3}) \n\t Error {4}: {5} \n\t Config File = {6} \n\t Function = {7}"

    vs['00-003-00013'] = "Parameter '{0}' dtype not set \n\t Config File = {1} \n\t Function = {2}"

    vs['00-003-00014'] = "Parameter '{0}' dtype is incorrect. Must be one of the following: \n\t {1} \n\t Config file: {2} \n\t function = {3}"

    vs['00-003-00015'] = "Parameter '{0}' value is not set. \n\t Config file = '{1}' \n\t Function = {2}"

    vs['00-003-00016'] = "Parameter '{0}' must be True or False or 1 or 0 \n\t Current value: '{1}' \n\t Config file: {2} \n\t Function = {3}"

    vs['00-003-00017'] = "Parameter '{0}' value is incorrect. \n\t Options are: {1} \n\t Current value: '{2}' \n\t Config File = {3} \n\t Function = {4}"

    vs['00-003-00018'] = "Parameter '{0}' too large. \n\t Value must be less than {1} \n\t Current value: {2} \n\t Config File = {3} \n\t Function = {4}"

    vs['00-003-00019'] = "Parameter '{0}' too small. \n\t Value must be greater than {1} \n\t Current value: {2} \n\t Config File = {3} \n\t Function = {4}"

    vs['00-003-00020'] = "Invalid character(s) found in file = {0} \n\t Function = {1}"

    vs['00-003-00021'] = "\n\t\t Line {0}: character = '{1}'"

    vs['00-003-00022'] = "Wrong format for line {0} in file {1} \n\t Line {0}: {2} \n\t Lines must be in format: 'key = value' \n\t where 'key' and 'value' are valid python strings containing no equal signs \n\t Function = {3}"

    vs['00-003-00023'] = "No valid lines found in file: {0} \n\t Function = {1}"

    vs['00-003-00024'] = "ParamDict Error: Parameter '{0}' not found in parameter dictionary"

    vs['00-003-00025'] = "ParamDict locked. \n\t Cannot add '{0}'='{1}'"

    vs['00-003-00026'] = "ParamDict Error: Source cannot be added for key '{0}' \n\t '{0}' is not in parameter dictionary"

    vs['00-003-00027'] = "ParamDict Error: Instance cannot be added for key '{0}' \n\t '{0} is not in parameter dictionary"

    vs['00-003-00028'] = "ParamDict Error: No source set for key={0}"

    vs['00-003-00029'] = "ParamDict Error: No instance set for key={0}"

    vs['00-003-00030'] = "ParamDict Error: parameter '{0}' not found in parameter dictionary (via listp)"

    vs['00-003-00031'] = "ParamDict Error: parameter '{0}' not found in parameter dictionary (via listp)"

    vs['00-003-00032'] = ""

    vs[''] = ""

    vs[''] = ""

    vs[''] = ""

    vs[''] = ""

    vs[''] = ""

    vs[''] = ""

    vs[''] = ""

    vs[''] = ""

    vs[''] = ""

    vs[''] = ""

    vs['00-008-00001'] = "Package name = '{0}' is invalid (function = {1})"

    vs['10-002-00001'] = "User config defined in {0} but instrument '{1}' directory not found. \n\t Directory = {2} \n\t Using default configuration files."

    vs['10-002-00002'] = "Key '{0}' duplicated in '{1}' \n\t Other configs: {2} \n\t Config File = {3}"

    vs['10-005-00004'] = "Breakpoint reached (breakfunc={0})"

    vs['40-000-00001'] = "ParamDict Info: Key = '{0}' not found"

    vs['40-000-00002'] = "Information for key = '{0}'"

    vs['40-000-00003'] = "\tData Type: \t\t {0}"

    vs['40-000-00004'] = "\tMin Value: \t\t {0} \n\tMax Value: \t\t {1} \n\t Has NaNs: \t\t {2} \n\t Values: \t\t {3}"

    vs['40-000-00005'] = "\t Num Keys: \t\t {0} \n\t Values: \t\t {1}"

    vs['40-000-00006'] = "\tValue: \t\t {0}"

    vs['40-000-00007'] = "\tSource: \t\t {0}"

    vs['40-000-00008'] = "\tInstance: \t\t {0}"

    vs['40-000-00009'] = "History for key = '{0}'"

    vs['40-000-00010'] = "No history found for key='{0}'"

    vs['90-000-00004'] = "In Func: {0}"

    vs['90-000-00005'] = "\t Entered {0} times"


    return vs

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
