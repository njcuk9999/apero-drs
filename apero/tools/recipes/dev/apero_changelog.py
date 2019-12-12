#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-26 at 09:40

@author: cook
"""
import os
import shutil
from datetime import datetime

from apero import core
from apero.core import constants
from apero import locale
from apero.io import drs_path
from apero.tools.module.documentation import drs_changelog

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_changelog.py'
__INSTRUMENT__ = 'None'
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# Get Logging function
WLOG = core.wlog
# Get the text types
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict
# -----------------------------------------------------------------------------
rargs = [Constants, Constants['DRS_PACKAGE'], '../']
PATH = drs_path.get_relative_folder(*rargs)
FILENAME = os.path.join(PATH, 'changelog.md')
VERSIONFILE = os.path.join(PATH, 'VERSION.txt')
rargs = [Constants, Constants['DRS_PACKAGE'], './core/instruments/default/']
CONSTPATH = drs_path.get_relative_folder(*rargs)
CONSTFILE = os.path.join(CONSTPATH, 'default_config.py')
# define line parameters
VERSIONSTR_PREFIX = 'DRS_VERSION = Const('
DATESTR_PREFIX = 'DRS_DATE = Const('

VERSIONSTR = """
DRS_VERSION = Const('DRS_VERSION', value='{0}', dtype=str, 
                    source=__NAME__)
"""
DATESTR = """
DRS_DATE = Const('DATE', value='{0}', dtype=str, 
                 source=__NAME__)
"""


# =============================================================================
# Define functions
# =============================================================================
def main(preview=1, **kwargs):
    """
    Main function for drs_changelog.py

    :param preview: bool, if True does not save before previewing if False
                    saves without previewing
    :param kwargs: any additional keywords

    :type preview: bool

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(preview=preview, **kwargs)
    # ----------------------------------------------------------------------
    # deal with command line inputs / function call inputs
    recipe, params = core.setup(__NAME__, __INSTRUMENT__, fkwargs)
    # solid debug mode option
    if kwargs.get('DEBUG0000', False):
        return recipe, params
    # ----------------------------------------------------------------------
    # run main bulk of code (catching all errors)
    llmain, success = core.run(__main__, recipe, params)
    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    return core.end_main(params, llmain, recipe, success, outputs='None')


def __main__(recipe, params):

    # get the text dictionary
    textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
    # ----------------------------------------------------------------------
    # if in preview mode tell user
    if params['INPUTS']['PREVIEW']:
        WLOG(params, 'info', TextEntry('40-501-00008'))
    # ----------------------------------------------------------------------
    # read and ask for new version
    WLOG(params, '', TextEntry('40-501-00009'))
    # set new version
    version = drs_changelog.ask_for_new_version(params)
    # add tag of version
    if version is not None:
        # tag head with version
        drs_changelog.git_remove_tag(version)
        drs_changelog.git_tag_head(version)
        new = True
    else:
        version = str(__version__)
        new = False
    # ----------------------------------------------------------------------
    # update DRS files
    if not params['INPUTS']['PREVIEW']:
        drs_changelog.update_version_file(VERSIONFILE, version)
        drs_changelog.update_py_version(CONSTFILE, version)
    # ----------------------------------------------------------------------
    # create new changelog
    # log that we are updating the change log
    WLOG(params, '', TextEntry('40-501-00010'))
    # if not in preview mode modify the changelog directly
    if not params['INPUTS']['PREVIEW']:
        drs_changelog.git_change_log(FILENAME)
    # else save to a tmp file
    else:
        drs_changelog.git_change_log('tmp.txt')
        drs_changelog.preview_log('tmp.txt')
        # if the version is new make sure this version is not a git tag
        #    already (won't fail if we don't have the tag)
        if new:
            drs_changelog.git_remove_tag(version)
    # ----------------------------------------------------------------------
    # if we are in preview mode should we keep these changes and update version
    if params['INPUTS']['PREVIEW']:
        # ask whether to keep changes
        uinput = input(textdict['40-501-00011'] + ' [Y]es [N]o:\t')
        # if we want to keep the changes apply changes from above
        if 'Y' in uinput.upper():
            # redo tagging
            drs_changelog.git_remove_tag(version)
            drs_changelog.git_tag_head(version)
            # update version file and python version file
            drs_changelog.update_version_file(VERSIONFILE, version)
            drs_changelog.update_py_version(CONSTFILE, version)
            # move the tmp.txt to change log
            shutil.move('tmp.txt', FILENAME)
        else:
            os.remove('tmp.txt')

    # ------------------------------------------------------------------
    # update recipe log file
    # ------------------------------------------------------------------
    # no quality control --> so set passed qc to True
    recipe.log.no_qc(params)
    # update log
    recipe.log.end(params)
    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return core.return_locals(params, locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()

# =============================================================================
# End of code
# =============================================================================
