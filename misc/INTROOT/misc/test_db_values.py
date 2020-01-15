#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-12-18 at 10:47

@author: cook
"""

import numpy as np
import os
from astropy.io import fits


# =============================================================================
# Define variables
# =============================================================================
WORKSPACE = '/spirou/cfht_nights/mtl/telluDB'
DATABASE = os.path.join(WORKSPACE, 'master_tellu_SPIROU.txt')
# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
def read_data_base(databasepath):
    # open file
    f = open(databasepath, 'r')
    lines = f.readlines()
    f.close()
    # split by space
    dlines = []
    for line in lines:
        dlines.append(line.split())
    # return database lines
    return dlines



# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # load database file
    database = read_data_base(DATABASE)

    # get filename sna obj name for all TELL_OBJ
    tell_file, tell_obj = [], []
    for entry in database:
        if len(entry) == 0:
            continue
        if entry[0] == 'TELL_OBJ':
            tell_file.append(entry[1].strip())
            tell_obj.append(entry[4].strip())

    # loop around files and check header
    hdr_obj = []
    for it, filename in enumerate(tell_file):
        # print progress
        print('Reading file {0} of {1}'.format(it + 1, len(tell_file)))
        # load header
        fhdr = fits.getheader(os.path.join(WORKSPACE, filename))
        # get objname from header
        objname_hdr = str(fhdr['OBJNAME']).strip()
        hdr_obj.append(objname_hdr)
        # check for consistency
        if objname_hdr.upper() != tell_obj[it].upper():
            wmsg = '\tFile {0} OBJNAME match fail ({1} != {2})'
            print(wmsg.format(filename, tell_obj[it], objname_hdr))

    tell_obj = np.array(tell_obj)
    hdr_obj = np.array(hdr_obj)
    mask = tell_obj != hdr_obj
    print('Number OBJNAMES not equal = {0}'.format(np.nansum(mask)))


# =============================================================================
# End of code
# =============================================================================
