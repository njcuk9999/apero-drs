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

import apero
from apero.base import base
from apero.base import drs_break
from apero import lang
from apero.core.core import drs_log
from apero.core.utils import drs_startup
from apero.tools.module.documentation import drs_changelog


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_changelog.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
textentry = lang.textentry
# --------------------------------------------------------------------------
CLOGFILENAME = '../changelog.md'
VERSIONFILE = '../version.txt'
CONSTFILE = './base/base.py'
# define documentation properties
DOC_CONFPATH = '../documentation/working/conf.py'
DOC_CONF_PREFIX = 'release = '
DOC_INDEXPATH = '../documentation/working/index.rst'
DOC_INDEX_PREFIX = 'Latest version: '
DOC_CHANGELOGPATH = '../documentation/working/misc/changelog.rst'


# =============================================================================
# Define functions
# =============================================================================
def main(preview=1, **kwargs):
    """
    Main function for apero_changelog.py

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
    recipe, params = drs_startup.setup(__NAME__, __INSTRUMENT__, fkwargs)
    # solid debug mode option
    if kwargs.get('DEBUG0000', False):
        return recipe, params
    # ----------------------------------------------------------------------
    # run main bulk of code (catching all errors)
    llmain, success = drs_startup.run(__main__, recipe, params)
    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    return drs_startup.end_main(params, llmain, recipe, success, outputs='None')


def __main__(recipe, params):
    # Note: no instrument defined so do not use instrument only features

    # get current working directory
    current = os.getcwd()
    # change to apero root
    os.chdir(apero.__path__[0])
    # make sure we have update tags
    os.system('git fetch --tags')

    # get package
    package = params['DRS_PACKAGE']
    # get filename
    filename = drs_break.get_relative_folder(package, CLOGFILENAME)
    # get version file path
    versionfile = drs_break.get_relative_folder(package, VERSIONFILE)
    # get const file path
    constfile = drs_break.get_relative_folder(package, CONSTFILE)
    # ----------------------------------------------------------------------
    # if in preview mode tell user
    if params['INPUTS']['PREVIEW']:
        WLOG(params, 'info', textentry('40-501-00008'))
    # ----------------------------------------------------------------------
    # read and ask for new version
    WLOG(params, '', textentry('40-501-00009'))
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
        drs_changelog.update_version_file(versionfile, version)
        drs_changelog.update_py_version(CONSTFILE, version)
    # ----------------------------------------------------------------------
    # create new changelog
    # log that we are updating the change log
    WLOG(params, '', textentry('40-501-00010'))
    # if not in preview mode modify the changelog directly
    if not params['INPUTS']['PREVIEW']:
        drs_changelog.git_change_log(filename)
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
        uinput = input(textentry('40-501-00011') + ' [Y]es [N]o:\t')
        # if we want to keep the changes apply changes from above
        if 'Y' in uinput.upper():
            # redo tagging
            drs_changelog.git_remove_tag(version)
            drs_changelog.git_tag_head(version)
            # update version file and python version file
            drs_changelog.update_version_file(versionfile, version)
            drs_changelog.update_py_version(constfile, version)
            # move the tmp.txt to change log
            shutil.move('tmp.txt', filename)
        else:
            os.remove('tmp.txt')
    # ----------------------------------------------------------------------
    # get doc paths
    doc_confpath = drs_break.get_relative_folder(package, DOC_CONFPATH)
    doc_clogpath = drs_break.get_relative_folder(package, DOC_CHANGELOGPATH)
    doc_indxpath = drs_break.get_relative_folder(package, DOC_INDEXPATH)
    # update documentation (conf.py)
    strversion = '\'{0}\'\n'.format(version)
    drs_changelog.update_file(doc_confpath, DOC_CONF_PREFIX, strversion)
    # update documentation (index.py)
    drs_changelog.update_file(doc_indxpath, DOC_INDEX_PREFIX, version)

    # copy change log to path
    shutil.copy(filename, doc_clogpath)
    # need to re-format change log to conform to rst format
    drs_changelog.format_rst(doc_clogpath)

    # push tags via git
    os.system('git push --tags')
    # go back to current directory
    os.chdir(current)

    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return drs_startup.return_locals(params, locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()

# =============================================================================
# End of code
# =============================================================================
