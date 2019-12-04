#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-12-04 at 09:16

@author: cook
"""

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.table import Table
from astropy import units as u
from astropy.time import Time
from tqdm import tqdm
import warnings
import glob
import os


# =============================================================================
# Define variables
# =============================================================================

WORKSPACE = '/spirou/cfht_nights/cfht_nov1/msg'

MASTER_LOG_FILE = 'DRS-HOST_PID-00015754175082736862_apero-processing'
LOG_RECIPE = 'cal_preprocess_spirou'
GROUP_DIR = 'DRS-HOST_PID-00015754175082736862_apero-processing_group'

PASSED_STR = 'has been successfully completed'
FAILED_STR = 'has NOT been successfully completed'

# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
class Log:
    def __init__(self, filename, master=None):
        self.filename = filename
        self.lines = self.__read__()
        self.starttime = self.lines[0].split('-')[0]
        self.endtime = self.lines[-1].split('-')[0]
        _, line = self.__search__('PID-')
        if line is not None:
            self.pid = line.split('PID-')[-1].split(' ')[0]
        else:
            self.pid = 'Not found'

        self.time = Time(os.path.getctime(filename), format='unix')
        _, line = self.__search__('PP[')
        if line is not None:
            self.idnum = line.split('PP[')[-1].split(']')[0]
        else:
            self.idnum = None
        if master is not None and self.idnum is not None:
            idkey = 'ID{0}|C'.format(self.idnum)
            _, line = master.__search__(idkey)
            self.core = int(line.split(idkey)[-1].split('|')[0].split('/')[0])
        else:
            self.core = None

    def __read__(self):
        # open file
        logfile = open(self.filename, 'r')
        lines = logfile.readlines()
        logfile.close()
        return lines


    def __search__(self, findstr):
        for lit, line in enumerate(self.lines):
            if findstr in line:
                return lit, line
        print('Value {0} not found in {1}'.format(findstr, self.filename))
        return None, None

    def __contains__(self, text):
        for line in self.lines:
            if text in line:
                return True
        return False

    def __str__(self):
        return 'Log[{0}]'.format(self.filename)

    def __repr__(self):
        return 'Log[{0}]'.format(self.filename)


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # find all log files
    masterpath = os.path.join(WORKSPACE, MASTER_LOG_FILE)
    path = os.path.join(WORKSPACE, GROUP_DIR)
    print('Constructing list of files')
    files = glob.glob('{0}/*{1}'.format(path, LOG_RECIPE))


    masterlogfile = Log(masterpath)

    # storage
    storage = dict()
    storage['PASSED'] = []
    storage['FAILED'] = []
    storage['TERMINATED'] = []

    print('Reading log files...')
    for filename in tqdm(files):
        # get log file
        logfile = Log(filename, master=masterlogfile)
        # sort into groups
        if PASSED_STR in logfile:
            storage['PASSED'].append(logfile)
        elif FAILED_STR in logfile:
            storage['FAILED'].append(logfile)
        else:
            storage['TERMINATED'].append(logfile)

    passed_times = list(map(lambda x: x.time.unix, storage['PASSED']))
    passed_cores = list(map(lambda x: x.core, storage['PASSED']))

    failed_times = list(map(lambda x: x.time.unix, storage['FAILED']))
    failed_cores = list(map(lambda x: x.core, storage['FAILED']))

    terminated_times = list(map(lambda x: x.time.unix, storage['TERMINATED']))
    terminated_cores = list(map(lambda x: x.core, storage['TERMINATED']))

    import matplotlib
    matplotlib.use('Qt5Agg')
    import matplotlib.pyplot as plt
    plt.close()
    plt.scatter(passed_cores, passed_times, color='g', label='Passed')
    plt.scatter(failed_cores, failed_times, color='b', label='Failed')
    plt.scatter(terminated_cores, terminated_times, color='r', label='Terminated')
    plt.xlabel('Cores')
    plt.ylabel('Time [unix]')
    plt.legend(loc=0)
    plt.show()
    plt.close()


# =============================================================================
# End of code
# =============================================================================
