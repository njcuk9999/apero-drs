#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Obtain the files of FileObjectConst parameters from their source

Sources (see custom_const_classes.FileObjectConst):
    local  - nothing to do (files must already exist)
    pogos  - download filelist from the POGOS data server (url) or copy /
             symlink them from a local mirror of the server
    mast   - query MAST (astroquery) for program pid / observation
             obsnumber products ending in _{product}.fits and download them

Files are only downloaded when the filelist is empty, when a listed file is
missing, or when always_download is True. After downloading, the parameter
value (filelist) is updated and, if a yaml file is given, the yaml entry is
updated in place (comments preserved) so the next run uses the local copy.

Created on 2026-11-25

@author: cook
"""
import os
import shutil
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

import requests
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq

from aperocore.base import base
from aperocore.constants import custom_const_classes as ccc
from aperocore.core import drs_log

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'aperocore.constants.file_sources'
# get the logger
WLOG = drs_log.wlog
# environment variable holding a MAST API token (proprietary data)
MAST_TOKEN_ENV = 'MAST_API_TOKEN'
# download chunk size in bytes
CHUNK_SIZE = 1024 * 1024


# =============================================================================
# Define exceptions
# =============================================================================
class FileSourceError(Exception):
    """Raised when the files of a FileObjectConst cannot be obtained."""


# =============================================================================
# Define functions
# =============================================================================
def find_file_keys(params: Any) -> List[str]:
    """
    Find all parameter keys whose constant is a FileObjectConst

    :param params: ParamDict, the parameter dictionary

    :return: list of str, the parameter keys (in parameter order)
    """
    # storage for the keys found
    keys = []
    # loop around all parameters
    for key in list(params.keys()):
        # the instance tells us whether this is a file object constant
        instance = params.instances.get(key, None)
        if isinstance(instance, ccc.FileObjectConst):
            keys.append(key)
    return keys


def module_prefix(key: str, instance: ccc.FileObjectConst) -> str:
    """
    Get the prefix that turns a module relative key into a parameter key

    e.g. key='SOSSISSE.GENERAL.FILES' with instance GENERAL.FILES returns
    'SOSSISSE.' (and '' when SOSSISSE runs standalone)

    :param key: str, the full parameter key
    :param instance: FileObjectConst, the constant of this parameter

    :return: str, the prefix (possibly empty, else ending with '.')
    """
    # the module relative name of this constant (as first defined)
    fullname = getattr(instance, 'relname', instance.fullname).upper()
    # compare upper case (parameter keys are case insensitive)
    if key.upper().endswith(fullname):
        return key[:len(key) - len(fullname)]
    return ''


def needs_download(fileobj: ccc.FileObject, directory: str) -> bool:
    """
    Decide whether the files of a file object need downloading

    :param fileobj: FileObject, the file source information
    :param directory: str, the directory the files live in

    :return: bool, True if files need to be obtained from the source
    """
    # local files are never downloaded
    if not fileobj.online:
        return False
    # the user asked to always re-download
    if fileobj.always_download:
        return True
    # nothing listed yet (e.g. first MAST query)
    if len(fileobj.files) == 0:
        return True
    # any missing file triggers a download
    for filename in fileobj.files:
        if not os.path.exists(_local_path(directory, filename)):
            return True
    return False


def resolve_files(params: Any, keys: Optional[Iterable[str]] = None,
                  skip_keys: Iterable[str] = (),
                  yaml_file: Optional[str] = None,
                  demolocal: Optional[str] = None,
                  demosymlink: bool = False,
                  dry_run: bool = False,
                  get_directory: Optional[Callable[[Any, str, str], str]]
                  = None) -> Dict[str, Any]:
    """
    Make sure the files of all online FileObjectConst parameters exist

    :param params: ParamDict, the parameter dictionary (updated in place)
    :param keys: list of keys to resolve (default: all FileObjectConst keys)
    :param skip_keys: keys that are produced by an earlier step in this run
                      (e.g. SOSSISSE.GENERAL.FILES when TSOVORE runs) - these
                      are never downloaded
    :param yaml_file: str or None, if set the yaml entries of updated keys
                      are rewritten in this file
    :param demolocal: str or None, a local mirror of the POGOS data server
                      (copy/symlink instead of downloading source=pogos files)
    :param demosymlink: bool, symlink (True) or copy (False) from demolocal
    :param dry_run: bool, if True only report what would be downloaded
    :param get_directory: function(params, key, path_key) -> directory, used
                          when directory parameters may still be relative
                          (default: the value of params[path_key])

    :return: dict, key -> new yaml value for every key that was updated
    """
    # default to every file object parameter
    if keys is None:
        keys = find_file_keys(params)
    # upper case keys to compare case insensitively
    skip = set(key.upper() for key in skip_keys)
    # storage for yaml updates
    updates = dict()
    # loop around file object parameters
    for key in keys:
        # get the instance and current value
        instance = params.instances.get(key, None)
        value = params[key]
        # get the source information (plain values are local)
        fileobj = ccc.get_fileobj(value)
        if fileobj is None or not fileobj.online:
            continue
        # skip files produced by an earlier step of this run
        if key.upper() in skip:
            msg = '\t{0}: produced by an earlier step - not downloading'
            WLOG(params, '', msg.format(key))
            continue
        # get the directory the files belong in
        directory = _get_directory(params, key, instance, get_directory)
        # nothing to do if all files exist
        if not needs_download(fileobj, directory):
            msg = '\t{0}: all files present in {1}'
            WLOG(params, '', msg.format(key, directory))
            continue
        # report what is being done
        msg = '\t{0}: obtaining files from {1}'
        WLOG(params, 'info', msg.format(key, fileobj.source))
        if dry_run:
            continue
        # make sure the directory exists
        os.makedirs(directory, exist_ok=True)
        # obtain the files from the source
        if fileobj.source == 'pogos':
            pkwargs = dict(demolocal=demolocal, demosymlink=demosymlink)
            filenames = fetch_pogos(params, fileobj, directory, **pkwargs)
        else:
            filenames = fetch_mast(params, fileobj, directory)
        # update the file object with the files we now have
        new_fileobj = fileobj.copy()
        new_fileobj.filelist = _filelist_for(instance, filenames, key)
        # push the updated value into params
        new_value = instance.wrap(new_fileobj)
        params.set(key, new_value, source=__NAME__, instance=instance)
        # record the yaml form of the update
        updates[key] = instance.yaml_value(new_value)
    # update the yaml file (if requested)
    if yaml_file is not None and len(updates) > 0:
        update_yaml_file(yaml_file, updates)
        msg = 'Updated {0} file entries in yaml: {1}'
        WLOG(params, 'info', msg.format(len(updates), yaml_file))
    # return the updates
    return updates


def ask_download_now(params: Any, summary: Dict[str, str]
                     ) -> Tuple[bool, Optional[str], bool]:
    """
    Ask the user whether to download online input files now

    :param params: ParamDict, used for logging
    :param summary: dict, parameter key -> source for files to download

    :return: tuple, (download now, local mirror path or None, symlink)
    """
    # list what would be downloaded
    lines = ['\nThe following inputs are obtained online:']
    for key, source in summary.items():
        lines.append(f'    {key}  (source: {source})')
    lines.append('\nHow would you like to handle these files?')
    lines.append('  [D]ownload now')
    lines.append('  [L]ocal mirror of the POGOS data server (copy/symlink '
                 'source: pogos files from disk, download the rest)')
    lines.append('  [R]un - download when they are first needed (default)')
    prompt = '\n'.join(lines) + '\n'
    # loop until we get a valid answer
    while True:
        userinput = str(input(prompt)).upper().strip()
        if userinput in ['', 'R', 'RUN']:
            return False, None, False
        if userinput in ['D', 'DOWNLOAD']:
            return True, None, False
        if userinput in ['L', 'LOCAL']:
            path = str(input('\nLocal mirror path: ')).strip()
            if not os.path.isdir(path):
                WLOG(params, 'warning', f'Path does not exist: {path}')
                continue
            symlink = str(input('\nUse symlinks? [Y]es / [N]o (copy): '))
            return True, path, symlink.upper().strip() in ['Y', 'YES']
        WLOG(params, 'warning', 'Invalid choice. Please select D, L or R.')


def fetch_pogos(params: Any, fileobj: ccc.FileObject, directory: str,
                demolocal: Optional[str] = None,
                demosymlink: bool = False) -> List[str]:
    """
    Get files from the POGOS data server (or a local mirror of it)

    :param params: ParamDict, used for logging
    :param fileobj: FileObject, with filelist and url set
    :param directory: str, the directory to save files to
    :param demolocal: str or None, local mirror root (the last directory of
                      the url is looked for inside this)
    :param demosymlink: bool, symlink (True) or copy (False) from demolocal

    :return: list of str, the filenames now present in directory
    :raises FileSourceError: if any file cannot be obtained
    """
    # storage for the filenames obtained
    filenames = []
    # loop around the listed files
    for filename in fileobj.files:
        # where the file should end up
        localpath = _local_path(directory, filename)
        basename = os.path.basename(filename)
        # skip existing files unless always_download is set
        if os.path.exists(localpath) and not fileobj.always_download:
            filenames.append(basename)
            continue
        # copy / symlink from a local mirror of the server
        if demolocal is not None:
            last_dir = fileobj.url.rstrip('/').split('/')[-1]
            src_path = os.path.join(demolocal, last_dir, basename)
            if not os.path.exists(src_path):
                emsg = 'Local mirror file not found: {0}'
                raise FileSourceError(emsg.format(src_path))
            # remove any existing file first (always_download)
            if os.path.lexists(localpath):
                os.remove(localpath)
            if demosymlink:
                WLOG(params, '', '\t\tSymlinking: {0}'.format(localpath))
                os.symlink(src_path, localpath)
            else:
                WLOG(params, '', '\t\tCopying: {0}'.format(localpath))
                shutil.copy2(src_path, localpath)
        # otherwise download from the server
        else:
            url = fileobj.url.rstrip('/') + '/' + basename
            WLOG(params, '', '\t\tDownloading: {0}'.format(url))
            download_url(url, localpath)
        filenames.append(basename)
    return filenames


def download_url(url: str, localpath: str) -> None:
    """
    Download a url to a file (via a temporary file so partial downloads
    never look like complete files)

    :param url: str, the url
    :param localpath: str, the destination file

    :return: None
    :raises FileSourceError: if the download fails
    """
    # temporary file next to the destination
    tmppath = localpath + '.part'
    try:
        with requests.get(url, stream=True, timeout=60) as response:
            # 404 etc. become errors
            response.raise_for_status()
            with open(tmppath, 'wb') as tmpfile:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    tmpfile.write(chunk)
        # move into place only once complete
        os.replace(tmppath, localpath)
    except (requests.RequestException, OSError) as error:
        # never leave partial files behind
        if os.path.exists(tmppath):
            os.remove(tmppath)
        emsg = 'Could not download {0}: {1}'
        raise FileSourceError(emsg.format(url, error)) from error


def mast_product_table(fileobj: ccc.FileObject,
                       observations_module: Any = None) -> Any:
    """
    Query MAST for the products of a file object (no download)

    Products must end with _{product}.fits, contain every string in match
    and be at least min_size_mb in size. If the filelist is set only those
    files are kept.

    :param fileobj: FileObject, with pid, obsnumber and product set
    :param observations_module: astroquery.mast.Observations (or a
                                compatible object, for testing)

    :return: astropy Table of the selected MAST products
    :raises FileSourceError: if nothing matches
    """
    # get the astroquery Observations class (only needed for MAST)
    if observations_module is None:
        observations_module = _get_mast_observations()
    # MAST uses zero padded identifiers
    pid = str(fileobj.pid).zfill(5)
    obs_number = str(fileobj.obsnumber).zfill(3)
    # query observations belonging to the program
    qkwargs = dict(obs_collection='JWST', proposal_id=pid)
    observations = observations_module.query_criteria(**qkwargs)
    # select the requested observation: level 3 obs_ids contain -o{obs}_
    #   (e.g. jw01366-o001_t001_...) and only hold the science exposures
    obs_ids = [str(obs_id) for obs_id in observations['obs_id']]
    obs_pattern = f'-o{obs_number}_'
    mask = [obs_pattern in obs_id for obs_id in obs_ids]
    # some observations only have exposure level obs_ids starting
    #   jw{pid}{obs} (e.g. jw03730009001_03101_...) - use those if needed
    if not any(mask):
        exp_prefix = f'jw{pid}{obs_number}'
        mask = [obs_id.startswith(exp_prefix) for obs_id in obs_ids]
    selected = observations[mask]
    if len(selected) == 0:
        emsg = ('{0}: no MAST observation found for program {1} '
                'observation {2}')
        raise FileSourceError(emsg.format(fileobj.name, pid, obs_number))
    # get the data products of the observation
    products = observations_module.get_product_list(selected)
    # selection criteria
    suffix = f'_{fileobj.product}.fits'
    match = fileobj.get_match()
    min_size = fileobj.get_min_size_mb() * 1e6
    wanted = set(os.path.basename(f) for f in fileobj.files)
    # storage for the selection mask (and filenames already chosen)
    keep, seen = [], set()
    for filename, size in zip(products['productFilename'],
                              products['size']):
        filename = str(filename)
        good = filename.endswith(suffix)
        good &= all(sub in filename for sub in match)
        good &= _as_float(size) >= min_size
        # only the listed files if filelist is set
        if len(wanted) > 0:
            good &= filename in wanted
        # the same file can appear for several observations - keep one
        good &= filename not in seen
        if good:
            seen.add(filename)
        keep.append(good)
    selected_products = products[keep]
    if len(selected_products) == 0:
        emsg = ('{0}: no MAST products matching *{1} (match={2}, '
                'min_size_mb={3}) for program {4} observation {5}')
        eargs = [fileobj.name, suffix, match, fileobj.get_min_size_mb(),
                 pid, obs_number]
        raise FileSourceError(emsg.format(*eargs))
    # warn about listed files that MAST does not have
    missing = wanted - seen
    if len(missing) > 0:
        emsg = '{0}: files not found on MAST: {1}'
        raise FileSourceError(emsg.format(fileobj.name, sorted(missing)))
    return selected_products


def fetch_mast(params: Any, fileobj: ccc.FileObject, directory: str,
               observations_module: Any = None) -> List[str]:
    """
    Download MAST products for a file object

    :param params: ParamDict, used for logging
    :param fileobj: FileObject, with pid, obsnumber and product set
    :param directory: str, the directory to save files to
    :param observations_module: astroquery.mast.Observations (for testing)

    :return: list of str, the sorted filenames now present in directory
    :raises FileSourceError: if the query or a download fails
    """
    # get the astroquery Observations class (only needed for MAST)
    if observations_module is None:
        observations_module = _get_mast_observations()
    # log in if the user gave a token (needed for proprietary data)
    token = os.environ.get(MAST_TOKEN_ENV, None)
    if token:
        observations_module.login(token=token)
    # query the products
    msg = '\t\tQuerying MAST: program={0} observation={1} product={2}'
    margs = [fileobj.pid, fileobj.obsnumber, fileobj.product]
    WLOG(params, '', msg.format(*margs))
    products = mast_product_table(fileobj, observations_module)
    filenames = sorted(str(name) for name in products['productFilename'])
    # only download files we do not have (unless always_download)
    if not fileobj.always_download:
        mask = [not os.path.exists(os.path.join(directory, str(name)))
                for name in products['productFilename']]
        products = products[mask]
    # download
    msg = '\t\tDownloading {0} file(s) from MAST to {1}'
    WLOG(params, '', msg.format(len(products), directory))
    if len(products) > 0:
        dkwargs = dict(download_dir=directory, flat=True)
        manifest = observations_module.download_products(products, **dkwargs)
        # check the manifest for failures
        _check_manifest(fileobj, manifest)
    # check that every file now exists
    for filename in filenames:
        if not os.path.exists(os.path.join(directory, filename)):
            emsg = '{0}: MAST download did not produce {1}'
            raise FileSourceError(emsg.format(fileobj.name, filename))
    return filenames


def update_yaml_file(yaml_file: str, updates: Dict[str, Any]) -> None:
    """
    Update entries of a yaml file in place (keeping comments and order)

    :param yaml_file: str, the yaml file
    :param updates: dict, dotted key (e.g. SOSSISSE.GENERAL.FILES) -> value

    :return: None, rewrites yaml_file
    """
    # round trip yaml (same settings as ConstantsDict.save_yaml)
    yaml_inst = YAML(typ='rt')
    base.enable_scientific_floats(yaml_inst)
    yaml_inst.width = 4096
    with open(yaml_file, 'r') as yfile:
        data = yaml_inst.load(yfile)
    if data is None:
        data = CommentedMap()
    # loop around updates
    for key, value in updates.items():
        _set_nested(data, key.split('.'), value)
    # write to a temporary file then move into place
    tmp_file = yaml_file + '.tmp'
    with open(tmp_file, 'w') as yfile:
        yaml_inst.dump(data, yfile)
    os.replace(tmp_file, yaml_file)


# =============================================================================
# Define worker functions
# =============================================================================
def _local_path(directory: str, filename: str) -> str:
    """Absolute filenames are used as is, others are joined to directory."""
    if os.path.isabs(filename):
        return filename
    return os.path.join(directory, filename)


def _get_directory(params: Any, key: str,
                   instance: ccc.FileObjectConst,
                   get_directory: Optional[Callable[[Any, str, str], str]]
                   = None) -> str:
    """
    Get the directory a file object parameter's files belong in

    :param params: ParamDict, the parameters
    :param key: str, the parameter key
    :param instance: FileObjectConst, the constant
    :param get_directory: optional function(params, key, path_key)

    :return: str, the directory
    :raises FileSourceError: if the directory parameter is not set
    """
    if instance.path_key is None:
        emsg = '{0}: no directory parameter (path_key) defined'
        raise FileSourceError(emsg.format(key))
    # the directory parameter lives in the same module as the file
    path_key = module_prefix(key, instance) + instance.path_key
    # caller specific directory resolution (e.g. relative paths)
    if get_directory is not None:
        directory = get_directory(params, key, path_key)
    else:
        directory = params.get(path_key, None)
    if directory is None:
        emsg = ('{0}: directory parameter {1} is not set - cannot '
                'download files')
        raise FileSourceError(emsg.format(key, path_key))
    return str(directory)


def _filelist_for(instance: ccc.FileObjectConst, filenames: List[str],
                  key: str) -> Any:
    """
    Convert obtained filenames into a filelist for this constant

    :param instance: FileObjectConst, the constant
    :param filenames: list of str, the filenames obtained
    :param key: str, the parameter key (for messages)

    :return: list (list constants / multiple files) or str (single file)
    :raises FileSourceError: if a single file constant got several files
    """
    # list constants always take the list
    if instance.dtype in [list, 'list']:
        return list(filenames)
    # single file constants
    if len(filenames) == 1:
        return filenames[0]
    # some single file constants accept a list (e.g. WAVE_FILE)
    if instance.allow_list:
        return list(filenames)
    emsg = ('{0} takes a single file but the source gave {1} files: {2}. '
            'Use "match" (MAST) or list one file (POGOS).')
    raise FileSourceError(emsg.format(key, len(filenames), filenames))


def _set_nested(data: Any, levels: List[str], value: Any) -> None:
    """
    Set a nested value in a round trip yaml mapping

    Matches existing keys case insensitively and keeps the existing node
    (and its comments) when updating a mapping.

    :param data: CommentedMap, the yaml mapping
    :param levels: list of str, the key levels
    :param value: the value to set

    :return: None, updates data in place
    """
    # walk down (creating mappings when needed)
    cursor = data
    for level in levels[:-1]:
        name = _match_key(cursor, level)
        if name not in cursor or not isinstance(cursor[name], dict):
            cursor[name] = CommentedMap()
        cursor = cursor[name]
    # the final key
    name = _match_key(cursor, levels[-1])
    current = cursor.get(name, None)
    # update an existing mapping in place (keeps comments)
    if isinstance(value, dict) and isinstance(current, CommentedMap):
        for subkey in list(current.keys()):
            if subkey not in value:
                del current[subkey]
        for subkey, subvalue in value.items():
            current[subkey] = _yaml_node(subvalue)
    else:
        cursor[name] = _yaml_node(value)


def _yaml_node(value: Any) -> Any:
    """Convert plain python values into round trip yaml nodes."""
    if isinstance(value, dict):
        node = CommentedMap()
        for key, subvalue in value.items():
            node[key] = _yaml_node(subvalue)
        return node
    if isinstance(value, (list, tuple)):
        return CommentedSeq([_yaml_node(item) for item in value])
    if isinstance(value, str):
        return str(value)
    return value


def _match_key(mapping: Any, key: str) -> str:
    """Return the existing key in mapping matching key (case insensitive)."""
    for existing in mapping.keys():
        if str(existing).upper() == key.upper():
            return existing
    return key


def _as_float(value: Any) -> float:
    """Convert a (possibly masked) table value to float (0 if invalid)."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _check_manifest(fileobj: ccc.FileObject, manifest: Any) -> None:
    """
    Raise if the astroquery download manifest reports failures

    :param fileobj: FileObject, for messages
    :param manifest: astropy Table returned by download_products (or None)

    :return: None
    :raises FileSourceError: if any file failed to download
    """
    if manifest is None or 'Status' not in manifest.colnames:
        return
    bad = [str(row['Local Path']) for row in manifest
           if str(row['Status']) not in ('COMPLETE', 'SKIPPED')]
    if len(bad) > 0:
        emsg = ('{0}: MAST download failed for {1}. For proprietary data '
                'set the environment variable {2} to your MAST token.')
        raise FileSourceError(emsg.format(fileobj.name, bad, MAST_TOKEN_ENV))


def _get_mast_observations() -> Any:
    """
    Import astroquery.mast.Observations (only needed for source=mast)

    :return: the astroquery Observations class
    :raises FileSourceError: if astroquery is not installed
    """
    try:
        from astroquery.mast import Observations
    except ImportError as error:
        emsg = ('astroquery is required for source=mast. '
                'Install it with: pip install astroquery')
        raise FileSourceError(emsg) from error
    return Observations


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================
