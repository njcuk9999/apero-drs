#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2019-11-09 10:44
@author: ncook
Version 0.0.1
"""
import os

import requests
import wget

from aperocore.base import base
from aperocore.constants import param_functions
from aperocore.core import drs_log
from aperocore.core import drs_text
from apero.utils import drs_data
from apero.io import drs_path
from apero.base import base as apero_base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tools.module.setup.drs_assets.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = apero_base.__PACKAGE__
__version__ = apero_base.__version__
__authors__ = apero_base.__authors__
__date__ = apero_base.__date__
__release__ = apero_base.__release__
# get param dict
ParamDict = param_functions.ParamDict
# RSYNC command
RSYNC_CMD = 'rsync -avuz -e "{SSH}" {INPATH} {USER}@{HOST}:{OUTPATH}'
# APERO RI endpoint that receives asset uploads (UPLOAD_MODE = 'ari')
ARI_UPLOAD_ENDPOINT = '/api/admin/assets/upload'
# APERO RI token-authenticated download endpoint (DOWNLOAD_MODE = 'ari')
ARI_DOWNLOAD_ENDPOINT = '/api/assets/download/'
# APERO RI public (no login) download url prefix (DOWNLOAD_MODE = 'url')
ARI_PUBLIC_PREFIX = '/apero-assets/'
# environment variable holding the APERO RI admin API token
ARI_TOKEN_ENVVAR = 'APERO_ARI_TOKEN'
# timeout (connect, read) in seconds for the APERO RI upload
ARI_UPLOAD_TIMEOUT = (30, 3600)
# Get Logging function
WLOG = drs_log.wlog
# get exceptions
AperoCodedException = drs_log.AperoCodedException


# =============================================================================
# functions
# =============================================================================
def get_asset_directory(package: str = None) -> str:
    """
    Get the package asset directory used for APERO remote assets.

    :param package: str or None, package name to resolve assets from. If None,
                    use the APERO package name.

    :return: str, absolute path to the package apero-assets directory
    """
    if package is None:
        package = __PACKAGE__
    return drs_path.get_relative_folder(package, 'apero-assets')


def update_remote_assets(params: ParamDict, indir: str):
    """
    Create a yaml file containing all checksums and create a tar file of the
    assets directory and upload to the server

    :param params: ParamDict, parameter dictionary of constants
    :param indir: the input directory for local assets to be uploaded

    :return:
    """
    # check that indir is correct
    if not indir.endswith(os.sep):
        indir += os.sep
    # lets make sure we have one correct file - getting this wrong can lead
    # to a lot of problems for everyone
    if not os.path.exists(os.path.join(indir, 'apero-assets.txt')):
        emsg = 'indir={0} is not correct (should have "apero-assets.txt" file)'
        eargs = [indir]
        raise AperoCodedException(params, None, message=emsg.format(*eargs),
                                  targs=eargs)
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
            if filename == apero_base.CHECKSUM_FILE:
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
    # public download urls stored in the yaml (used by DOWNLOAD_MODE = 'url')
    servers = list(params['AURLS.URLS'])
    upload_mode = str(params['AURLS.UPLOAD_MODE']).strip().lower()
    # tars pushed to APERO RI are also served from its public url
    if upload_mode == 'ari':
        ari_public = get_ari_url(params, 'UPLOAD_MODE') + ARI_PUBLIC_PREFIX
        if ari_public not in servers:
            servers.append(ari_public)
    yaml_dict['setup']['servers'] = servers
    # -------------------------------------------------------------------------
    # Step 4: Save the yaml file
    # -------------------------------------------------------------------------
    # get path to yaml file
    _data_path = params['IPATH.CDATA']
    # get the data path
    abs_data_path = drs_data.construct_path(params, '', _data_path)
    # add the checksum filename
    checksum_path = os.path.join(abs_data_path, apero_base.CHECKSUM_FILE)
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
    # Step 6: Upload the tar file (legacy ssh/rsync or APERO RI API)
    # -------------------------------------------------------------------------
    if upload_mode == 'ari':
        upload_assets_ari(params, tar_path)
    elif upload_mode == 'ssh':
        upload_assets_ssh(params, tar_path)
    else:
        emsg = 'AURLS.UPLOAD_MODE={0} is invalid (must be "ssh" or "ari")'
        eargs = [upload_mode]
        raise AperoCodedException(params, None, message=emsg.format(*eargs),
                                  targs=eargs)


def upload_assets_ssh(params: ParamDict, tar_path: str):
    """
    Upload the assets tar file to the remote server using rsync over ssh

    :param params: ParamDict, parameter dictionary of constants
    :param tar_path: str, absolute path to the local assets tar file

    :return: None
    """
    # get rsync dict
    rdict = dict()
    rdict['SSH'] = params['AURLS.SSH_OPTIONS']
    rdict['USER'] = params['AURLS.SSH_USER']
    rdict['HOST'] = params['AURLS.SSH_HOST']
    rdict['INPATH'] = tar_path
    rdict['OUTPATH'] = params['AURLS.SSH_ASSETSPATH']
    # print command to rsync
    WLOG(params, '', RSYNC_CMD.format(**rdict))
    # run rsync command
    os.system(RSYNC_CMD.format(**rdict))


def get_ari_url(params: ParamDict, mode_key: str) -> str:
    """
    Get the APERO RI base url (AURLS.ARI_URL) without a trailing slash

    :param params: ParamDict, parameter dictionary of constants
    :param mode_key: str, the AURLS mode constant that requires it (for the
                     error message)

    :return: str, the APERO RI base url
    """
    ari_url = params['AURLS.ARI_URL']
    if drs_text.null_text(ari_url, ['None', 'Null', '']):
        emsg = ('AURLS.ARI_URL must be set (e.g. https://ari.example.com) '
                'when AURLS.{0} = "ari"')
        eargs = [mode_key]
        raise AperoCodedException(params, None, message=emsg.format(*eargs),
                                  targs=eargs)
    return str(ari_url).rstrip('/')


def get_ari_token(params: ParamDict, mode_key: str) -> str:
    """
    Get the APERO RI API token from the APERO_ARI_TOKEN environment variable

    :param params: ParamDict, parameter dictionary of constants
    :param mode_key: str, the AURLS mode constant that requires it (for the
                     error message)

    :return: str, the API token
    """
    # kept out of config files as it is a secret
    token = os.environ.get(ARI_TOKEN_ENVVAR, '').strip()
    if not token:
        emsg = ('Environment variable {0} must hold an APERO RI API token '
                '(generate it in the APERO RI User Portal -> API Access) '
                'when AURLS.{1} = "ari"')
        eargs = [ARI_TOKEN_ENVVAR, mode_key]
        raise AperoCodedException(params, None, message=emsg.format(*eargs),
                                  targs=eargs)
    return token


def check_ari_response(params: ParamDict, response: requests.Response,
                       action: str) -> dict:
    """
    Raise a clear error if an APERO RI asset request failed

    :param params: ParamDict, parameter dictionary of constants
    :param response: requests.Response, the APERO RI response
    :param action: str, 'upload' or 'download' (for the error message)

    :return: dict, the decoded json reply (empty for non-json replies)
    """
    # decode the json reply (files and proxy errors are not json)
    try:
        reply = response.json()
    except ValueError:
        reply = dict()
    if not isinstance(reply, dict):
        reply = dict()
    # deal with the APERO RI admin not having set an assets directory
    if reply.get('setup_required', False):
        emsg = ('APERO RI asset hosting is not set up. An APERO RI admin '
                'must set the assets directory at: {0}')
        eargs = [reply.get('setup_url', '')]
        raise AperoCodedException(params, None, message=emsg.format(*eargs),
                                  targs=eargs)
    # deal with any other failure
    if not response.ok:
        emsg = 'APERO RI {0} failed [HTTP {1}]: {2}'
        eargs = [action, response.status_code,
                 reply.get('error', response.reason)]
        raise AperoCodedException(params, None, message=emsg.format(*eargs),
                                  targs=eargs)
    return reply


def upload_assets_ari(params: ParamDict, tar_path: str):
    """
    Upload the assets tar file to an APERO RI server through its admin API

    Requires AURLS.ARI_URL and an admin APERO RI API token in the
    APERO_ARI_TOKEN environment variable. If the APERO RI admin has not
    set an assets directory the server replies with the page to set it on.

    :param params: ParamDict, parameter dictionary of constants
    :param tar_path: str, absolute path to the local assets tar file

    :return: None
    """
    # construct the upload request
    url = get_ari_url(params, 'UPLOAD_MODE') + ARI_UPLOAD_ENDPOINT
    token = get_ari_token(params, 'UPLOAD_MODE')
    headers = dict()
    headers['Authorization'] = f'Bearer {token}'
    headers['Content-Type'] = 'application/octet-stream'
    # the server verifies the upload against this checksum
    headers['X-Content-MD5'] = drs_path.calculate_checksum(tar_path)
    query = dict(filename=os.path.basename(tar_path))
    # print progress
    WLOG(params, '', f'Uploading {tar_path} to {url}')
    # stream the tar file as the raw request body
    try:
        with open(tar_path, 'rb') as tar_fh:
            ul_kwargs = dict(params=query, data=tar_fh, headers=headers,
                             timeout=ARI_UPLOAD_TIMEOUT)
            response = requests.post(url, **ul_kwargs)
    except requests.RequestException as exc:
        emsg = 'Could not connect to APERO RI at {0}: {1}'
        eargs = [url, exc]
        raise AperoCodedException(params, None, message=emsg.format(*eargs),
                                  targs=eargs)
    reply = check_ari_response(params, response, 'upload')
    # print that the upload worked
    msg = 'Uploaded {0} ({1} bytes) to APERO RI'
    margs = [reply.get('name'), reply.get('size_bytes')]
    WLOG(params, '', msg.format(*margs))


def download_assets_url(params: ParamDict, servers: list,
                        server_tarfile: str, abs_asset_path: str):
    """
    Download the assets tar file from the first working public url

    :param params: ParamDict, parameter dictionary of constants
    :param servers: list of str, public base urls (from the checksum yaml)
    :param server_tarfile: str, basename of the tar file on the servers
    :param abs_asset_path: str, directory to download the tar file into

    :return: None
    """
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
    tarfile = os.path.join(abs_asset_path, server_tarfile)
    if not os.path.exists(tarfile):
        # TODO: Add to language database
        emsg = 'Cannot download assets tar file: {0}'
        emsg += '\tTried servers: {1}'
        eargs = [tarfile, servers]
        raise AperoCodedException(params, message=emsg.format(*eargs),
                                  targs=eargs)


def download_assets_ari(params: ParamDict, server_tarfile: str,
                        abs_asset_path: str):
    """
    Download the assets tar file through the APERO RI API (token required)

    :param params: ParamDict, parameter dictionary of constants
    :param server_tarfile: str, basename of the tar file on APERO RI
    :param abs_asset_path: str, directory to download the tar file into

    :return: None
    """
    url = get_ari_url(params, 'DOWNLOAD_MODE') + ARI_DOWNLOAD_ENDPOINT
    url += server_tarfile
    token = get_ari_token(params, 'DOWNLOAD_MODE')
    headers = dict(Authorization=f'Bearer {token}')
    tarfile = os.path.join(abs_asset_path, server_tarfile)
    # download to a temporary name so a partial file is never used
    tmp_tarfile = tarfile + '.part'
    # print progress
    msg = 'Attempting downloading tar file from: {0}'
    WLOG(params, '', msg.format(url), colour='magenta')
    try:
        dl_kwargs = dict(headers=headers, stream=True,
                         timeout=ARI_UPLOAD_TIMEOUT)
        with requests.get(url, **dl_kwargs) as response:
            check_ari_response(params, response, 'download')
            with open(tmp_tarfile, 'wb') as tar_fh:
                for chunk in response.iter_content(chunk_size=1 << 20):
                    tar_fh.write(chunk)
    except requests.RequestException as exc:
        if os.path.exists(tmp_tarfile):
            os.remove(tmp_tarfile)
        emsg = 'Could not download from APERO RI at {0}: {1}'
        eargs = [url, exc]
        raise AperoCodedException(params, None, message=emsg.format(*eargs),
                                  targs=eargs)
    os.replace(tmp_tarfile, tarfile)
    WLOG(params, '', 'Download successful', colour='magenta')


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
    _asset_path = params['IPATH.RESET_ASSETS']
    _data_path = params['IPATH.CDATA']
    # get the absolute path to the assets dir
    abs_asset_path = drs_data.construct_path(params, '', _asset_path)
    # get the data path
    abs_data_path = drs_data.construct_path(params, '', _data_path)
    # add the checksum filename
    checksum_path = os.path.join(abs_data_path, apero_base.CHECKSUM_FILE)
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

    # get the input directory
    indir = params['INPUTS'].get('INDIR', 'None')
    # path to the checksum yaml (needed whether or not indir is given)
    _data_path = params['IPATH.CDATA']
    # deal with no input directory
    if drs_text.null_text(indir, ['None', 'Null', '']):
        # get path to yaml file
        _asset_path = params['IPATH.RESET_ASSETS']
        # get the absolute path to the assets dir
        abs_asset_path = drs_data.construct_path(params, '', _asset_path)
    else:
        # set this to the input directory given by the user (if given)
        abs_asset_path = str(indir)
        # make sure directory exists
        if not os.path.exists(abs_asset_path):
            os.makedirs(abs_asset_path)
    # get the data path
    abs_data_path = drs_data.construct_path(params, '', _data_path)
    # add the checksum filename
    checksum_path = os.path.join(abs_data_path, apero_base.CHECKSUM_FILE)
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
            # TODO: Add to language database
            emsg = 'Cannot find local assets tar file: {}'
            eargs = [tarfile]
            raise AperoCodedException(params, message=emsg.format(*eargs),
                                      targs=eargs)
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
            # public urls (legacy + APERO RI public) or APERO RI API
            download_mode = str(params['AURLS.DOWNLOAD_MODE']).strip().lower()
            if download_mode == 'ari':
                download_assets_ari(params, server_tarfile, abs_asset_path)
            elif download_mode == 'url':
                dl_args = [params, yaml_dict['setup']['servers'],
                           server_tarfile, abs_asset_path]
                download_assets_url(*dl_args)
            else:
                emsg = ('AURLS.DOWNLOAD_MODE={0} is invalid (must be "url" '
                        'or "ari")')
                eargs = [download_mode]
                raise AperoCodedException(params, None,
                                          message=emsg.format(*eargs),
                                          targs=eargs)
        else:
            # print that we are reading from local file
            msg = 'Reading from local tar file: {0}'
            margs = [tarfile]
            WLOG(params, '', msg.format(*margs))
    # -------------------------------------------------------------------------
    # Extract the tar file
    # -------------------------------------------------------------------------
    # get the assets path
    extract_path = str(abs_asset_path)
    # print progress
    WLOG(params, '', f'Extracting tar file: {tarfile} to {extract_path}')
    # extract tar file
    try:
        drs_path.extract_tarfile(tarfile, extract_path)
    except Exception as e:
        # TODO: Add to language database
        emsg = 'Cannot extract tar file: {0} \n\t Error {1}: {2}'
        eargs = [tarfile, type(e), str(e)]
        raise AperoCodedException(params, message=emsg.format(*eargs),
                                  targs=eargs)


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
