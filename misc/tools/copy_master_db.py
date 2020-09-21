#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CODE DESCRIPTION HERE

Created on 2020-09-2020-09-21 10:45

@author: cook
"""
from astropy.table import Table
import os
import shutil


# =============================================================================
# Define variables
# =============================================================================
OLD_CALIBDB = '/spirou/cfht_nights/cfht_sept1/calibDB/'
NEW_CALIBDB = '/spirou/cfht_nights/cfht_venus/calibDB/'

# TODO: will have to be database later
calib_file = 'master_calib_SPIROU.txt'

# =============================================================================
# Define functions
# =============================================================================


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":

    # get db path
    old_db_path = os.path.join(OLD_CALIBDB, calib_file)
    # get new db path
    new_db_path = os.path.join(NEW_CALIBDB, calib_file)
    # get master calib db (old)
    table = Table.read(old_db_path, format='ascii')
    # get master calibrations
    masters = table['col2'] == 1
    # filter table
    table = table[masters]
    # get file list
    files = table['col4']
    # write to new file
    table.write(new_db_path, format='ascii.no_header', overwrite=True)

    # copy files from old to new
    for filename in files:
        # construct old path
        old_file_path = os.path.join(OLD_CALIBDB, filename)
        # construct new path
        new_file_path = os.path.join(NEW_CALIBDB, filename)
        # print copy
        print('{0} --> {1}'.format(old_file_path, new_file_path))
        # copy
        shutil.copy(old_file_path, new_file_path)

# =============================================================================
# End of code
# =============================================================================
