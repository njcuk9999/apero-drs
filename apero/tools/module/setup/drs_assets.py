#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2019-11-09 10:44
@author: ncook
Version 0.0.1
"""
import os

from apero.base import base
from apero.core import constants
from apero.core.core import drs_log
from apero.core.utils import drs_data
from apero.io import drs_path

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tools.module.setup.drs_assets.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get param dict
ParamDict = constants.ParamDict
# RSYNC command
RSYNC_CMD = 'rsync -avuz -e "{SSH}" {INPATH} {USER}@{HOST}:{OUTPATH}'
# Get Logging function
WLOG = drs_log.wlog


# =============================================================================
# functions
# =============================================================================
def upload_assets(params: ParamDict):
    """
    Create a yaml file containing all checksums and create a tar file of the
    assets directory and upload to the server

    :param params: ParamDict
    :return:
    """
    # get input directory
    indir = params['INPUTS']['INDIR']
    # -------------------------------------------------------------------------
    # Step 1: get a list of all files in indir
    # -------------------------------------------------------------------------
    # print progress
    WLOG(params, '', 'Indexing assets directory')
    # get a list of all files in indir using os.walk
    abs_paths, rel_paths = [], []
    for root, dirs, files in os.walk(indir):
        # loop around files
        for filename in files:
            # remove any assets tar files from the directory
            if filename.endswith('_assets.tar.gz'):
                if os.path.exists(filename):
                    os.remove(os.path.join(root, filename))
            # remove the checksum yaml files from the directory
            if filename == base.CHECKSUM_FILE:
                if os.path.exists(filename):
                    os.remove(os.path.join(root, filename))
            # get full path to file
            abs_path = os.path.join(root, filename)
            # append to full paths
            abs_paths.append(abs_path)
            # get the relative path to file
            rel_paths.append(os.path.relpath(abs_path, indir))
    # -------------------------------------------------------------------------
    # Step 2: create the hash codes for all files
    # -------------------------------------------------------------------------
    # print progress
    WLOG(params, '', 'Creating checksums for all files')
    # storage of all paths
    yaml_dict = dict(setup=dict(), data=dict())
    # create a yaml file containing the path relative to indir to all files
    # within indir and a md checksum for each file
    for it in range(len(abs_paths)):
        # generate hash code for file
        hashcode = drs_path.calculate_checksum(abs_paths[it])
        # push into yaml dictionary
        yaml_dict['data'][rel_paths[it]] = hashcode
    # -------------------------------------------------------------------------
    # Step 3: Construct the tar filename
    # -------------------------------------------------------------------------
    # print progress
    WLOG(params, '', 'Constructing tar filename')
    # get the string unix time now using base.Time
    time_now = base.Time.now()
    unixtime = str(time_now.unix).replace('.', '_')
    # make a tar file of the contents of the assets directory
    tar_path = os.path.join(indir, f'{unixtime}_assets.tar.gz')
    # add the tar file name to the yaml dict
    yaml_dict['setup']['tarfile'] = os.path.basename(tar_path)
    yaml_dict['setup']['version'] = base.__version__
    yaml_dict['setup']['vdate'] = base.__date__
    yaml_dict['setup']['unixtime'] = float(time_now.unix)
    yaml_dict['setup']['humantime'] = time_now.iso
    yaml_dict['setup']['servers'] = params.listp('DRS_ASSETS_URLS', dtype=str)
    # -------------------------------------------------------------------------
    # Step 4: Save the yaml file
    # -------------------------------------------------------------------------
    # create path to yaml file
    asset_path = params['DRS_RESET_ASSETS_PATH']
    # get the absolute path to the assets dir
    abs_asset_path = drs_data.construct_path(params, '', asset_path)
    # add the checksum filename
    checksum_path = os.path.join(abs_asset_path, base.CHECKSUM_FILE)
    # print progress
    WLOG(params, '', f'Saving yaml file to: {checksum_path}')
    # create yaml file
    base.write_yaml(yaml_dict, checksum_path)
    # -------------------------------------------------------------------------
    # Step 5:  make the tar file (including the yaml)
    # -------------------------------------------------------------------------
    # print progress
    WLOG(params, '', f'Making tar file: {tar_path}')
    # make tar file
    drs_path.make_tarfile(tar_path, indir)
    # -------------------------------------------------------------------------
    # Step 6: Upload the tar file using rsync
    # -------------------------------------------------------------------------
    # get rsync dict
    rdict = dict()
    rdict['SSH'] = params['DRS_SSH_OPTIONS']
    rdict['USER'] = params['DRS_SSH_USER']
    rdict['HOST'] = params['DRS_SSH_HOST']
    rdict['INPATH'] = tar_path
    rdict['OUTPATH'] = params['DRS_SSH_ASSETSPATH']
    # print command to rsync
    WLOG(params, '', RSYNC_CMD.format(**rdict))
    # run rsync command
    os.system(RSYNC_CMD.format(**rdict))


def download_assets(params: ParamDict):
    """
    Use assets yaml file to download all data into the github repo
    (but github repo will ignore all data changes)

    :param params:
    :return:
    """

    pass


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
