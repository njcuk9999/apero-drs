#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
copyraw

Copy or symlink an entire raw directory (file by file) only for fits files

Created on 2022-02-11

Import Rules: Cannot use anything other than standard python 3 packages
(i.e. no numpy, no astropy etc)

@author: cook
"""
import argparse
import os
from pathlib import Path
import shutil
from typing import Union


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'copyraw.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = 'APERO'
__version__ = '0.1'


# =============================================================================
# Define functions
# =============================================================================
def get_args():
    """
    Get arguments using argparse

    :return:
    """
    # get parser
    description = ('Make symbolic links/hard copies to a raw directory. '
                   '(Useful for freezing the raw directory for a full run)')
    parser = argparse.ArgumentParser(description=description)
    # add arguments
    parser.add_argument('--indir', action='store',
                        default=None, dest='user_indir',
                        help='The full, original raw directory')
    parser.add_argument('--outdir', action='store',
                        default=None, dest='user_outdir',
                        help='The proposed out raw directory')
    parser.add_argument('--do_copy', action='store_true', default=False,
                        dest='do_copy', help='Hard copies of files')
    parser.add_argument('--do_symlink', action='store_true', default=True,
                        dest='do_symlink',
                        help='Symlink files (overrides --do_copy if used)')
    # parse arguments
    args = parser.parse_args()
    # check that in directory is a string
    if str(args.user_indir) in ['None', '', 'Null']:
        raise ValueError('--indir must be defined')
    # check that in directory exists
    if not os.path.exists(args.user_indir):
        emsg = '--indir must exist\n\tCurrent value: {0}'
        raise ValueError(emsg.format(args.user_indir))
    # check that out directory is a string
    if str(args.user_outdir) in ['None', '', 'Null']:
        raise ValueError('--outdir must be defined')
    # return args
    return args


def raw_files(user_indir: str, user_outdir: str, do_copy: bool = True,
              do_symlink: bool = False):
    """
    Copy (or sym-link) the whole raw directory

    :param user_indir: str, the full, original raw directory (absolute path)
    :param user_outdir: str, proposed out raw directory (absolute path)
    :param do_copy: bool, hard copies files
    :param do_symlink: bool, symlinks files (overrides do_copy if True)
    :return:
    """
    # get raw directory
    raw_path = user_indir
    # make sure user_outdir exists
    if not os.path.exists(user_outdir):
        os.makedirs(user_outdir)
    # walk through path
    for root, dirs, files in os.walk(raw_path):
        # get uncommon path
        upath = _get_uncommon_path(raw_path, root)
        # make outpath
        outdir = os.path.join(user_outdir, upath)
        # make out directory if it doesn't exist
        if not os.path.exists(outdir):
            os.mkdir(outdir)
        # loop around files
        for filename in files:
            # only copy fits
            if not filename.endswith('.fits'):
                continue
            # construct inpath
            inpath = os.path.join(root, filename)
            # construct outpath
            outpath = os.path.join(outdir, filename)

            # copy
            if do_symlink:
                # print process
                msg = 'Creating symlink {0}'
                print(msg.format(outpath))
                # create symlink
                os.symlink(inpath, outpath)
            elif do_copy:
                # print process
                msg = 'Copying file {0}'
                print(msg.format(outpath))
                # copy file
                shutil.copy(inpath, outpath)


# =============================================================================
# Worker functions
# =============================================================================
def _get_uncommon_path(path1: Union[Path, str], path2: Union[Path, str]) -> str:
    """
    Get the uncommon path of "path1" compared to "path2"

    i.e. if path1 = /home/user/dir1/dir2/dir3/
         and path2 = /home/user/dir1/

         the output should be /dir2/dir3/

    :param path1: string, the longer root path to return (without the common
                  path)
    :param path2: string, the shorter root path to compare to

    :return uncommon_path: string, the uncommon path between path1 and path2
    """
    # set function name (cannot break here --> no access to params)
    # _ = display_func('get_uncommon_path', __NAME__)
    # may need to switch paths if len(path2) > len(path1)
    if len(str(path2)) > len(str(path1)):
        _path1 = str(path2)
        _path2 = str(path1)
    else:
        _path1 = str(path1)
        _path2 = str(path2)
    # paths must be absolute
    _path1 = os.path.abspath(_path1)
    _path2 = os.path.abspath(_path2)
    # get common path
    common = os.path.commonpath([_path2, _path1]) + os.sep
    # return the non-common part of the path
    return _path1.split(common)[-1]


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # get arguments
    params = get_args()
    # make symlinks
    raw_files(params.user_indir, params.user_outdir,
              params.do_copy, params.do_symlink)


# =============================================================================
# End of code
# =============================================================================
