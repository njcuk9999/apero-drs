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
from aperocore import drs_lang
from aperocore.core import drs_log
from aperocore.core import drs_misc
from apero.utils import drs_startup
from apero.tools.module.documentation import drs_changelog
from apero.base import base as apero_base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_changelog.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = apero_base.__PACKAGE__
__version__ = apero_base.__version__
__authors__ = apero_base.__authors__
__date__ = apero_base.__date__
__release__ = apero_base.__release__
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
textentry = drs_lang.textentry
# --------------------------------------------------------------------------
# Paths are relative to apero package (apero-drs/apero),
# repository root is ../../
CLOGFILENAME = '../../changelog.md'
# define documentation properties
DOC_INDEXPATH = '../../documentation/working/index.rst'
DOC_INDEX_PREFIX = 'Documentation written with version: '
DOC_CHANGELOGPATH = '../../documentation/working/main/misc/changelog.rst'


# =============================================================================
# Define functions
# =============================================================================
def ask_for_new_tag():
    """
    Ask user for a new tag in format major.minor.subversion

    Returns tuple: (tag_string, is_subversion_increment) or None if cancelled
    """
    # Get current version from git tags
    import subprocess
    try:
        current_tag = subprocess.check_output(
            ['git', 'describe', '--tags', '--abbrev=0'],
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except:
        current_tag = '0.0.0'

    print(f'Current tag: {current_tag}')

    # ask if we wish to create a new tag
    uinput1 = str(input('Do you want to create a new tag? [Y]es [N]o:\t'))

    if 'Y' not in uinput1.upper():
        return None

    # Parse current tag
    parts = current_tag.split('.')
    if len(parts) == 3:
        curr_major, curr_minor, curr_sub = parts
    else:
        curr_major, curr_minor, curr_sub = '0', '0', '0'

    cond = True
    while cond:
        # ask for new tag
        print(f'\nEnter new tag in format major.minor.subversion')
        print(f'  (e.g., 0.8.200 for next subversion after 0.8.199)')
        print(f'  (e.g., 0.9.001 for new minor version)')
        print(f'  (e.g., 1.0.001 for new major version)')
        new_tag = str(input('New tag: ')).strip()

        # Validate format
        tag_parts = new_tag.split('.')
        if len(tag_parts) != 3:
            print('Error: Tag must have format major.minor.subversion')
            continue

        try:
            new_major = int(tag_parts[0])
            new_minor = int(tag_parts[1])
            new_sub = int(tag_parts[2])
        except ValueError:
            print('Error: Tag parts must be integers')
            continue

        # Check if it's a subversion increment
        is_subversion = (new_major == int(curr_major) and
                        new_minor == int(curr_minor) and
                        new_sub > int(curr_sub))

        # Confirm the tag
        if is_subversion:
            print(f'\nThis is a subversion increment from {current_tag} to {new_tag}')
            print(f'Will backfill all tags from {curr_major}.{curr_minor}.{int(curr_sub)+1} to {new_tag}')
        else:
            print(f'\nThis is a major/minor version change to {new_tag}')
            print(f'Will create only the tag {new_tag}')

        confirm = str(input('Is this correct? [Y]es [N]o:\t'))
        if 'Y' in confirm.upper():
            return (new_tag, is_subversion)

    return None


def create_single_tag(tag):
    """Create a single git tag at HEAD with the commit date"""
    import subprocess
    import os

    # Remove tag if it exists
    subprocess.run(['git', 'tag', '-d', tag],
                  stderr=subprocess.DEVNULL)

    # Get HEAD commit date
    commit_date = subprocess.check_output(
        ['git', 'show', '-s', '--format=%cI', 'HEAD'],
        text=True
    ).strip()

    # Create new tag with commit date
    env = os.environ.copy()
    env['GIT_COMMITTER_DATE'] = commit_date

    subprocess.run(['git', 'tag', '-a', tag, '-m', f'Version {tag}'],
                  env=env, check=True)
    print(f'Created tag: {tag} with date {commit_date[:10]}')


def backfill_subversion_tags(end_tag, params):
    """
    Backfill all subversion tags from the last existing tag to end_tag
    """
    import subprocess

    # Parse end tag
    parts = end_tag.split('.')
    major, minor, end_sub = int(parts[0]), int(parts[1]), int(parts[2])

    # Get the last tag for this major.minor
    prefix = f'{major}.{minor}.'
    try:
        all_tags = subprocess.check_output(
            ['git', 'tag', '-l', f'{prefix}*'],
            text=True
        ).strip().split('\n')
        all_tags = [t for t in all_tags if t]  # Remove empty strings

        if all_tags:
            # Find the highest subversion
            subversions = []
            for tag in all_tags:
                try:
                    sub = int(tag.split('.')[-1])
                    subversions.append(sub)
                except:
                    pass
            start_sub = max(subversions) if subversions else 0
        else:
            start_sub = 0
    except:
        start_sub = 0

    # Get current commit
    head_commit = subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'],
        text=True
    ).strip()

    # Get the start commit (commit of the last tag)
    if start_sub > 0:
        start_tag = f'{major}.{minor}.{start_sub:03d}'
        try:
            start_commit = subprocess.check_output(
                ['git', 'rev-parse', start_tag],
                text=True
            ).strip()
        except:
            # If tag doesn't exist, use HEAD~
            start_commit = subprocess.check_output(
                ['git', 'rev-parse', 'HEAD~1'],
                text=True
            ).strip()
    else:
        # No previous tags, use first commit
        start_commit = subprocess.check_output(
            ['git', 'rev-list', '--max-parents=0', 'HEAD'],
            text=True
        ).strip()

    # Get commits between start and end (exclusive start, inclusive end)
    try:
        commits = subprocess.check_output(
            ['git', 'rev-list', '--reverse', f'{start_commit}..{head_commit}'],
            text=True
        ).strip().split('\n')
        commits = [c for c in commits if c]  # Remove empty strings
    except:
        commits = [head_commit]

    total_commits = len(commits)
    total_tags = end_sub - start_sub

    WLOG(params, 'info', f'Found {total_commits} commits')
    WLOG(params, 'info', f'Creating {total_tags} tags from '
                         f'{prefix}{start_sub+1:03d} to {end_tag}')

    if total_commits == 0:
        WLOG(params, 'warning', 'No commits found! Tagging HEAD only.')
        create_single_tag(end_tag)
        return

    # Calculate spacing
    spacing = total_commits / total_tags if total_tags > 0 else 1

    # Create the tags
    for sub in range(start_sub + 1, end_sub + 1):
        tag_name = f'{major}.{minor}.{sub:03d}'

        # Calculate which commit to tag
        commit_index = int((sub - start_sub - 1) * spacing)
        if commit_index >= total_commits:
            commit_index = total_commits - 1

        commit_hash = commits[commit_index]

        # Check if tag already exists
        try:
            subprocess.run(['git', 'rev-parse', tag_name],
                         check=True, capture_output=True)
            WLOG(params, 'info', f'Skipping {tag_name} (already exists)')
            continue
        except:
            pass

        # Get the commit date for this commit to backdate the tag
        commit_date = subprocess.check_output(
            ['git', 'show', '-s', '--format=%cI', commit_hash],
            text=True
        ).strip()

        # Create the tag with the commit date (backdate the tag)
        # This ensures gitchangelog uses the correct date
        import os
        env = os.environ.copy()
        env['GIT_COMMITTER_DATE'] = commit_date

        subprocess.run(
            ['git', 'tag', '-a', tag_name, commit_hash,
             '-m', f'Version {tag_name}'],
            env=env,
            check=True
        )
        WLOG(params, 'info', f'Created tag {tag_name} at commit '
                             f'{commit_hash[:8]} with date {commit_date[:10]}')


def remove_backfilled_tags(end_tag):
    """Remove backfilled tags if user cancels in preview mode"""
    import subprocess

    parts = end_tag.split('.')
    major, minor, end_sub = int(parts[0]), int(parts[1]), int(parts[2])

    # Get current tag to determine start
    try:
        current_tag = subprocess.check_output(
            ['git', 'describe', '--tags', '--abbrev=0'],
            stderr=subprocess.DEVNULL, text=True
        ).strip()
        curr_parts = current_tag.split('.')
        if len(curr_parts) == 3:
            start_sub = int(curr_parts[2])
        else:
            start_sub = 0
    except:
        start_sub = 0

    # Remove tags
    for sub in range(start_sub + 1, end_sub + 1):
        tag_name = f'{major}.{minor}.{sub:03d}'
        subprocess.run(['git', 'tag', '-d', tag_name],
                      stderr=subprocess.DEVNULL)


def main(**kwargs):
    """
    Main function for apero_changelog.py

    :param kwargs: any additional keywords

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(**kwargs)
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
    package = params['DRS.PACKAGE']
    # get filename
    filename = drs_misc.get_relative_folder(package, CLOGFILENAME)
    # ----------------------------------------------------------------------
    # if in preview mode tell user
    if params['INPUTS']['PREVIEW']:
        WLOG(params, 'info', textentry('40-501-00008'))
    # ----------------------------------------------------------------------
    # read and ask for new tag
    WLOG(params, '', 'Enter new tag information')
    # set new version using new tag-based approach
    tag_info = ask_for_new_tag()

    if tag_info is None:
        WLOG(params, 'info', 'No tag changes requested.')
        WLOG(params, 'info', 'Will generate changelog with existing tags.')
        new_tag = None
        is_subversion_increment = False
    else:
        new_tag, is_subversion_increment = tag_info
        # ----------------------------------------------------------------------
        # Handle tag creation
        if is_subversion_increment:
            # For subversion increment, backfill all intermediate tags
            WLOG(params, 'info', f'Creating subversion tags up to {new_tag}')
            backfill_subversion_tags(new_tag, params)
        else:
            # For major/minor version change, just create the single tag
            WLOG(params, 'info', f'Creating new tag: {new_tag}')
            create_single_tag(new_tag)

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

    # ----------------------------------------------------------------------
    # if we are in preview mode should we keep these changes
    if params['INPUTS']['PREVIEW']:
        # ask whether to keep changes
        uinput = input(textentry('40-501-00011') + ' [Y]es [N]o:\t')
        # if we want to keep the changes apply changes from above
        if 'Y' in uinput.upper():
            # move the tmp.txt to change log
            shutil.move('tmp.txt', filename)
        else:
            os.remove('tmp.txt')
            # remove the tags we just created (only if new tag was created)
            if new_tag is not None:
                if is_subversion_increment:
                    remove_backfilled_tags(new_tag)
                else:
                    import subprocess
                    subprocess.run(['git', 'tag', '-d', new_tag],
                                 stderr=subprocess.DEVNULL)
            WLOG(params, 'info', 'Changes cancelled, tags removed.')
            os.chdir(current)
            return locals()

    # ----------------------------------------------------------------------
    # get doc paths
    doc_clogpath = drs_misc.get_relative_folder(package, DOC_CHANGELOGPATH)
    doc_indxpath = drs_misc.get_relative_folder(package, DOC_INDEXPATH)

    # update documentation index only if new tag was created
    if new_tag is not None:
        drs_changelog.update_file(doc_indxpath, DOC_INDEX_PREFIX, new_tag)

    # copy change log to path
    shutil.copy(filename, doc_clogpath)
    # need to re-format change log to conform to rst format
    drs_changelog.format_rst(doc_clogpath)

    # push tags via git (only if new tag was created)
    if new_tag is not None:
        WLOG(params, 'info', 'Pushing tags to remote...')
        os.system('git push --tags')
        WLOG(params, 'info',
             f'Successfully created and pushed tag(s) up to {new_tag}')
    else:
        WLOG(params, 'info', 'Changelog updated successfully (no new tags)')

    # go back to current directory
    os.chdir(current)

    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return locals()


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()

# =============================================================================
# End of code
# =============================================================================
