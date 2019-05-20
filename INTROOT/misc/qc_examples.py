#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-03-22 at 12:55

@author: cook
"""

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.table import Table
from astropy import units as u
import os
import sys
import warnings


# =============================================================================
# Define variables
# =============================================================================
WORKSPACE = '/scratch/Projects/spirou/data_dev/reduced/'

OUTPUTFILE = WORKSPACE + 'qc_examples.md'
# -----------------------------------------------------------------------------
FILENAME = '*_pp_*.fits'

KEY_PREFIX = 'QCC'

# =============================================================================
# Define functions
# =============================================================================
def find_examples(path):


    # get all pp files
    all_files = []
    for root, dirs, files in os.walk(path):
        for filename in files:
            cond1 = '_pp_' in filename
            cond2 = filename.endswith('.fits')
            if cond1 and cond2:
                all_files.append(os.path.join(root, filename))
    # find one example of each output (between pp and .fits)
    ex_files = dict()
    for filename in all_files:
        bname = os.path.basename(filename)
        # get unique output string
        outstr = bname.split('_pp_')[-1].split('.fits')[0]
        if outstr not in ex_files:
            ex_files[outstr] = filename
    # return ex_files
    return ex_files


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # find one example of each extension
    examples = find_examples(WORKSPACE)

    # for each example we need to open the file and print to a string
    lines = []
    # loop around examples
    for example in np.sort(list(examples.keys())):
        # filename
        example_filename = examples[example]
        # add line to lines with which example this is
        lines.append(' - {0}'.format(example))
        lines.append('')
        lines.append('```')
        # open file
        header = fits.getheader(example_filename)
        # loop around header keys
        for key in header:
            if key.startswith(KEY_PREFIX):
                largs = [key, header[key], header.comments[key]]
                lines.append('{0:9s} {1} // {2}'.format(*largs))
        lines.append('```')
        lines.append('')
        lines.append('')

    # write to file
    f = open(OUTPUTFILE, 'w')
    for line in lines:
        f.write(line + '\n')
    f.close()


# =============================================================================
# End of code
# =============================================================================
