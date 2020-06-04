#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2020-05-21

@author: cook
"""
from astropy.time import Time
import argparse
import os


# =============================================================================
# Define variables
# =============================================================================
VERSION = [0, 0, 1]
DATE = "2020-05-01"
__FILE__ = 'git_update.py'
MAJOR_VERSION_DELTA_DAY = 1

# =============================================================================
# Define functions
# =============================================================================
def get_version(version=None):
    if version is None:
        version = VERSION
    if len(version) == 3:
        return '{0}.{1}.{2}'.format(*version)
    elif len(version) == 2:
        return '{0}.{1}'.format(*version)
    else:
        return str(version)


def get_date():
    return str(DATE)


# =============================================================================
# Define private functions
# =============================================================================
def _get_args():
    # get parser
    description = ' Commit Pull Push and update version on commit/pull'
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('--origin', '-o', action='store', dest='origin',
                        default=None,
                        help='Branch to do operation on (i.e. git pull '
                             'origin {origin})')

    parser.add_argument('--pull', action='store_true',
                        default=False, dest='pull',
                        help='Use this option to do a git pull')
    parser.add_argument('--push', action='store_true',
                        default=False, dest='push',
                        help='Use this option to do a git push')
    parser.add_argument('--commit', action='store_true',
                        default=False, dest='commit',
                        help='Use this option to do a git commit '
                             '(must provide a message with -m/--message)')
    parser.add_argument('--message', '-m', action='store', dest='message',
                        default=None, help='git commit message')
    parser.add_argument('--version', '--info', action='store_true',
                        dest='version', help='Display version information')
    parser.add_argument('--debug', action='store', dest='debug',
                        default=0, help='Debugging (practise run)',
                        choices=['0', '1', '2'])
    # parse arguments
    args = parser.parse_args()

    # convert debug
    args.debug = int(args.debug)

    return args


def _print_version():
    print('CURRENT VERSION: {0}'.format(get_version()))
    print('CURRENT DATE: {0}'.format(DATE))


def _git_operations(args):

    commands = []
    update_mode = 0
    # deal with pull request
    if args.pull:
        if args.origin is None:
            print('ERROR: Must define --origin/-o for git pull request')
            os._exit(0)
        else:
            commands.append('git pull origin {0}'.format(args.origin))

    # deal with commit
    elif args.commit:
        if args.message is None:
            print('ERROR: Must define --message/-m for git commit')
        else:
            commands.append('git commit -m "{0}"'.format(args.message))
            update_mode = 2

    # deal with push request
    if args.push:
        if args.origin is None:
            print('ERROR: Must define --origin/-o for git push request')
            os._exit(0)
        else:
            commands.append('git push origin {0}'.format(args.origin))
            if update_mode == 0:
                update_mode = 1

    if args.debug > 0:
        update_mode = args.debug

    return update_mode, commands


def _update_version(args, update_mode):
    # get time now
    now = Time.now()
    # get current version
    VERSION_KEY = 'VERSION = '
    DATE_KEY = 'DATE = '

    # open this file
    with open(__FILE__, 'r') as pyfile:
        lines = pyfile.readlines()

    # find the version and date lines
    versionstr, v_it, version = None, None, None
    datestr, d_it, datetime = None, None, None
    for it, line in enumerate(lines):
        # deal with version
        if line.startswith(VERSION_KEY):
            versionstr = line.split(VERSION_KEY)[-1].strip()
            v_it = int(it)
            # try to get date as a list
            try:
                version = list(eval(versionstr))
                v0 = int(version[0])
                v1 = int(version[1])
                v2 = int(version[2])
                version = [v0, v1, v2]
            except:
                print('ERROR: version invalid (="{0}")'.format(versionstr))
                os._exit(0)
        # deal with date
        if line.startswith(DATE_KEY):
            datestr = line.split(DATE_KEY)[-1].strip().strip('"')
            d_it = int(it)
            # try to get date as time object
            try:
                datetime = Time(datestr, format='iso')
            except:
                print('ERROR: Cannot set time from DATE = {0}'.format(datestr))
                os._exit(0)
    # deal with no versionstr or date str
    if versionstr is None or datestr is None:
        print('ERROR: Cannot read version/date from file: {0}'.format(__FILE__))
        os._exit(0)

    # set date
    lines[d_it] = '{0}"{1}"\n'.format(DATE_KEY, now.iso.split()[0])
    # set version
    if now - datetime > MAJOR_VERSION_DELTA_DAY:
        version[0] += 1
        version[1] = 0
        version[2] = 0
    elif update_mode == 1:
        version[1] += 1
        version[2] = 0
    elif update_mode == 2:
        version[2] += 1
    lines[v_it] = '{0}[{1}, {2}, {3}]\n'.format(VERSION_KEY, *version)

    vargs = [get_version(), get_version(version)]
    print('Version  {0}-->{1}'.format(*vargs))
    print('Date {0}-->{1}'.format(DATE, now.iso.split()[0]))

    with open(__FILE__, 'w') as pyfile:
        pyfile.writelines(lines)

    # commit this and push (if pushing)
    os.system('git add {0}'.format(__FILE__))


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # get arguments
    arguments = _get_args()
    # deal with version
    if arguments.version:
        _print_version()
        os._exit(1)
    # deal with push/pull/commit
    updatemode, cmds = _git_operations(arguments)
    # deal with updating the version
    if updatemode > 0:
        _update_version(arguments, updatemode)
    # run commands
    for cmd in cmds:
        os.system(cmd)


# =============================================================================
# End of code
# =============================================================================
