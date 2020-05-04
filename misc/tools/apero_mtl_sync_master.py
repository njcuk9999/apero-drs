#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2020-04-01 at 13:40

@author: cook
"""
import os


# =============================================================================
# Define variables
# =============================================================================
INSTRUMENT = 'SPIROU'
DEBUG = False
TEMPDIR = 'temp1234'

if INSTRUMENT == 'SPIROU':
    RSYNC_SERVER = 'spirou_master@craq-astro.ca'
    RSYNC_COMMAND = 'rsync -avr --port=8080 {0} {1}::SPIROU_MASTER/{2}'
    RSYNC_PASSWORD = 'Secotine763'
elif 'NIRPS' in INSTRUMENT:
    RSYNC_SERVER = 'nirps_master@craq-astro.ca'
    RSYNC_COMMAND = 'rsync -avr --port=8080 {0} {1}::NIRPS_MASTER/{2}'
    RSYNC_PASSWORD= 'LaChaise001'
else:
    RSYNC_SERVER = 'spirou_master@craq-astro.ca'
    RSYNC_COMMAND = 'rsync -avr --port=8080 {0} {1}::SPIROU_MASTER/{2}'
    RSYNC_PASSWORD = 'Secotine763'

name = 'mini_data_0_6_063_older'
localpath = 'mini_data_older_20200328'
directories = ['calibDB', 'telluDB', 'reduced']
# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
# rsync -avr --port=8080 mini_data_0_6_063_closest spirou_master@craq-astro.ca::SPIROU_MASTER/
# rsync -avr --port=8080 mini_data_closest_20200328/calibDB spirou_master@craq-astro.ca::SPIROU_MASTER/mini_data_0_6_063_closest/calibDB
# rsync -avr --port=8080 mini_data_older_20200328/calibDB spirou_master@craq-astro.ca::SPIROU_MASTER/mini_data_0_6_063_older/calibDB




# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # set password
    os.environ['RSYNC_PASSWORD'] = RSYNC_PASSWORD

    # get current working dir
    current = os.getcwd()
    # step 1: make local directory
    if os.path.exists(TEMPDIR):
        os.system('rm -rf {0}'.format(TEMPDIR))
    os.mkdir(TEMPDIR)
    os.chdir(TEMPDIR)
    os.mkdir(name)

    # make sync directory command
    command = RSYNC_COMMAND.format(name, RSYNC_SERVER, name)
    if DEBUG:
        print(command)
    else:
        print(command)
        os.system(command)

    # remove dir
    os.chdir('..')
    os.system('rm -rf {0}'.format(TEMPDIR))

    # copy data paths
    for directory in directories:
        inpath = os.path.join(localpath, directory)
        outpath = os.path.join(name, directory)
        command = RSYNC_COMMAND.format(inpath, RSYNC_SERVER, outpath)
        if DEBUG:
            print(command)
        else:
            print(command)
            os.system(command)

# =============================================================================
# End of code
# =============================================================================
