#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-03-15 at 13:37

@author: cook
"""

import glob
import os
import tqdm

# =============================================================================
# Define variables
# =============================================================================
WORKSPACE = '/spirou/cfht_nights/cfht_Jan19/msg_3'
# -----------------------------------------------------------------------------
LOG_FILE = '*PID*cal_extract*'

EXCLUDED = ['has been successfully completed']


# =============================================================================
# Define functions
# =============================================================================


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # get log files
    logfiles = glob.glob(os.path.join(WORKSPACE, LOG_FILE))

    # storage for good files
    goodfiles = []
    goodlines = []

    # loop around log files
    for logfile in logfiles:

        f = open(logfile)
        lines = f.readlines()
        f.close()

        # exclude text
        excluded_found = False
        for excluded_text in EXCLUDED:
            for line in lines:
                if excluded_text in line:
                    excluded_found = True
                    break
            if excluded_found:
                break
        # append good files
        if not excluded_found:
            goodfiles.append(logfile)
            goodlines.append(lines)

    # storage counter
    last_line_dict = dict()

    # look at the last five lines in every file
    for it, goodfile in enumerate(goodfiles):
        goodline = goodlines[it]

        last_message = goodline[-1].split('|')[-1]
        if last_message in last_line_dict:
            last_line_dict[last_message] += 1
        else:
            last_line_dict[last_message] = 1

            print('='*200)
            print('\t' + goodfile)
            print('='*200)
            print()
            for jt, line in enumerate(goodline[-10:]):
                print('{0}:\t\t{1}'.format(jt, line))
            print()
            print()

# =============================================================================
# End of code
# =============================================================================
