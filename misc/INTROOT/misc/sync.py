#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-09-20 at 14:52

@author: cook
"""
import os
import glob
import shutil

# =============================================================================
# Define functions
# =============================================================================
start_dir = '/space/spirou/cfht/'
out_dir = '/space/spirou/cfht_nights/'


valid_codes = ['a', 'c', 'o', 'f', 'd']

# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    dir_list = os.listdir(start_dir)
    print('Getting dir/file list...')
    valid_dirs = dict()
    count = 0
    for dir_it in dir_list:
        if os.path.isdir(dir_it):
            # get absolute sub-directory
            abs_dir = os.path.join(start_dir, dir_it)
            # get fits files
            absfiles = glob.glob(abs_dir + '/*.fits')
            # loop around these files
            goodfiles = []
            for absfile in absfiles:
                basefile = os.path.basename(absfile)
                # check that file exists
                if not os.path.exists(absfile):
                    continue
                # only copy valid codes (raw files)
                keep = False
                for valid_code in valid_codes:
                    if basefile.endswith(valid_code + '.fits'):
                        keep = True
                # add to list
                if keep:
                    goodfiles.append(absfile)
                    count += 1
            # add good files to valid_dirs
            if len(goodfiles) > 0:
                valid_dirs[dir_it] = goodfiles

    # copy all
    print('Copying files...')
    newcount = 0
    for valid_dir in valid_dirs.keys():
        # make path
        outpath = os.path.join(out_dir, valid_dir)
        # make dir
        if not os.path.exists(outpath):
            os.makedirs(outpath)
        # copy files
        for goodfile in valid_dirs[valid_dir]:
            # keep count
            newcount += 1
            # get old path
            oldpath = goodfile
            # get new path
            oldfile = os.path.basename(goodfile)
            newpath = os.path.join(out_dir, valid_dir, oldfile)
            # check file already exists
            if os.path.exists(newpath):
                continue
            # print
            pargs = [newcount, count, oldpath, newpath]
            print('\t{0}/{1} File {2} --> {3}'.format(*pargs))
            # copy
            shutil.copy(oldpath, newpath)


# =============================================================================
# End of code
# =============================================================================
