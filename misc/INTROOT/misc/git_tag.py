#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-05-01 at 16:46

@author: cook
"""

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.table import Table
from astropy import units as u
from tqdm import tqdm
import warnings
import os

# =============================================================================
# Define variables
# =============================================================================
LOG = '/scratch/Projects/spirou/drs/spirou_github/spirou_dev/CHANGELOG.md'



# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
def git_tag(version, commit):
    os.system('git tag {0} {1}'.format(version, commit))



# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------

    # load changelog
    f = open(LOG)
    lines = f.readlines()
    f.close()


    # store version and commit linked to it
    storage = dict()

    for it, line in enumerate(lines):

        if not line.strip().startswith('*'):
            continue


        if '*' in line and '-' in line:
            version = line.split('-')[-1].strip()
        else:
            continue

        if '(rev.' not in lines[it + 3]:
            continue

        commit = lines[it + 3].split('rev.')[-1].split(')')[0]

        if version not in storage:
            storage[version] = commit


    for version in storage:
        print('Tagging {0}: {1}'.format(version, storage[version]))
        git_tag(version, storage[version])


# =============================================================================
# End of code
# =============================================================================
