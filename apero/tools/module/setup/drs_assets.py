#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2019-11-09 10:44
@author: ncook
Version 0.0.1
"""
import os

import wget

from apero.base import base
from apero.core import constants
from apero.core.core import drs_log
from apero.core.base import drs_text
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
def update_remote_assets(params: ParamDict):
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
                continue
            # remove the checksum yaml files from the directory
            if filename == base.CHECKSUM_FILE:
                if os.path.exists(filename):
                    os.remove(os.path.join(root, filename))
                continue
            # get full path to file
            abs_path = str(os.path.join(root, filename))
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
    yaml_dict['setup']['servers'] = params['DRS_ASSETS_URLS']
    # -------------------------------------------------------------------------
    # Step 4: Save the yaml file
    # -------------------------------------------------------------------------
    # get path to yaml file
    _data_path = params['DRS_CRITICAL_DATA_PATH']
    # get the data path
    abs_data_path = drs_data.construct_path(params, '', _data_path)
    # add the checksum filename
    checksum_path = os.path.join(abs_data_path, base.CHECKSUM_FILE)
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
    drs_path.make_tarfile(tar_path, indir, exclude_suffixes=['_assets.tar.gz'])
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


def check_local_assets(params: ParamDict):
    """
    Check if we need to update assets based on the check sums in the yaml file

    If any file does not exist or any file needs updating use assets yaml file
    to download all data into the github repo (but github repo will ignore
    all data changes)

    :param params: ParamDict, parameter dictionary of constants

    :return:
    """
    # get path to yaml file
    _asset_path = params['DRS_RESET_ASSETS_PATH']
    _data_path = params['DRS_CRITICAL_DATA_PATH']
    # get the absolute path to the assets dir
    abs_asset_path = drs_data.construct_path(params, '', _asset_path)
    # get the data path
    abs_data_path = drs_data.construct_path(params, '', _data_path)
    # add the checksum filename
    checksum_path = os.path.join(abs_data_path, base.CHECKSUM_FILE)
    # read the yaml file
    yaml_dict = base.load_yaml(checksum_path)
    # -------------------------------------------------------------------------
    # print progress
    WLOG(params, '', 'Checking assets in {0}'.format(abs_asset_path))
    # update flag (assume we need don't need to update)
    update = False
    # check the checksums of the yaml dictionary data
    for path in yaml_dict['data']:
        # expected path
        expected_path = os.path.join(abs_asset_path, path)
        # check if file exists
        if not os.path.exists(expected_path):
            # print warning
            wmsg = '\tFile does not exist: {0}'
            wargs = [expected_path]
            WLOG(params, 'warning', wmsg.format(*wargs), sublevel=1)
            # flag that we need to update
            update = True
            break
        # expected checksum
        expected_checksum = yaml_dict['data'][path]
        # actual checksum
        actual_checksum = drs_path.calculate_checksum(expected_path)
        # check if checksums match
        if expected_checksum != actual_checksum:
            # print warning
            wmsg = 'Checksums do not match: {0}'
            wargs = [expected_path]
            WLOG(params, 'warning', wmsg.format(*wargs), sublevel=1)
            # flag that we need to update
            update = True
            break
    # -------------------------------------------------------------------------
    # if we don't need to update, return
    if not update:
        # print that everything is up-to-date
        WLOG(params, '', 'Assets are up-to-date')
        return False
    else:
        # print that we need to update
        WLOG(params, '', 'Assets need updating.')
        return True


def update_local_assets(params: ParamDict, tarfile: str = None):
    # get path to yaml file
    _asset_path = params['DRS_RESET_ASSETS_PATH']
    _data_path = params['DRS_CRITICAL_DATA_PATH']
    # get the absolute path to the assets dir
    abs_asset_path = drs_data.construct_path(params, '', _asset_path)
    # get the data path
    abs_data_path = drs_data.construct_path(params, '', _data_path)
    # add the checksum filename
    checksum_path = os.path.join(abs_data_path, base.CHECKSUM_FILE)
    # read the yaml file
    yaml_dict = base.load_yaml(checksum_path)
    # -------------------------------------------------------------------------
    # deal with a local tar file
    local = False
    # check for valid tar file
    if not drs_text.null_text(tarfile, ['None', 'Null', '']):
        if os.path.exists(tarfile):
            # print progress
            WLOG(params, '', 'Using local assets tar file')
            # set local flag
            local = True
        else:
            emsg = 'Cannot find local assets tar file: {}'
            eargs = [tarfile]
            WLOG(params, 'error', emsg.format(*eargs))
    # -------------------------------------------------------------------------
    # deal with non-local tar file
    if not local:
        # get the tar file name
        server_tarfile = yaml_dict['setup']['tarfile']
        # check that tar file now exists locally
        tarfile = os.path.join(abs_asset_path, server_tarfile)
        # deal with not having the file on disk currently
        if not os.path.exists(tarfile):
            # print progress
            WLOG(params, '', 'Downloading correct assets tar file')
            # get the server list
            servers = yaml_dict['setup']['servers']
            # loop around servers and find one that can download our tar file
            for server in servers:
                # noinspection PyBroadException
                try:
                    # print progress
                    msg = 'Attempting downloading tar file from: {0}'
                    margs = [server + server_tarfile]
                    WLOG(params, '', msg.format(*margs), colour='magenta')
                    # get the file using wget
                    wget.download(server + server_tarfile, abs_asset_path)
                    # new line after wget print out
                    print('')
                    # print that the download was successful
                    WLOG(params, '', 'Download successful', colour='magenta')
                    # break if this works
                    break
                except Exception as _:
                    pass
            # check if tar file exists
            if not os.path.exists(tarfile):
                emsg = 'Cannot download assets tar file: {}'
                eargs = [tarfile]
                WLOG(params, 'error', emsg.format(*eargs))
        else:
            # print that we are reading from local file
            msg = 'Reading from local tar file: {0}'
            margs = [tarfile]
            WLOG(params, '', msg.format(*margs))
    # -------------------------------------------------------------------------
    # Extract the tar file
    # -------------------------------------------------------------------------
    # get the assets path
    extract_path = os.path.dirname(abs_asset_path.rstrip(os.sep))
    # print progress
    WLOG(params, '', f'Extracting tar file: {tarfile} to {extract_path}')
    # extract tar file
    try:
        drs_path.extract_tarfile(tarfile, extract_path)
    except Exception as e:
        emsg = 'Cannot extract tar file: {0} \n\t Error {1}: {2}'
        eargs = [tarfile, type(e), str(e)]
        WLOG(params, 'error', emsg.format(*eargs))


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
