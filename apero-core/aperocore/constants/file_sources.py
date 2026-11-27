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

Download cache (download_dir given): online files are stored once in a
shared cache and symlinked into the directory of each constant:

    {download_dir}/pogos/{host}/{url path}/{file}   (source: pogos)
    {download_dir}/mast/jw{pid}/o{obsnumber}/{file} (source: mast)

The cache path comes from where a file was obtained, so files with the same
name from different server directories / programs never overwrite each
other. A file missing from a constant's directory is looked for in the cache
before going to the POGOS server / MAST (unless always_download is True). A
local mirror (demolocal) is copied into the cache, or with demosymlink the
directory links straight to the mirror. Without download_dir files are
written straight into the constant's directory (old behaviour).

Each cached file has a json record (see cache_meta_path) with where and when
it was obtained and every symlink made to it (link path -> parameter key),
so tools can show which projects use a cached file.

Created on 2026-11-25

@author: cook
"""
import json
import os
import shutil
import time
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple
from urllib.parse import urlparse

import requests
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq

from aperocore import progress as gprogress
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
# sub-directories of the download cache (one per online source)
CACHE_SOURCE_DIRS = dict(pogos='pogos', mast='mast')
# hidden directory of the download cache holding one json record per
#   cached file: {download_dir}/.meta/{path relative to download_dir}.json
CACHE_META_DIR = '.meta'


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


def cache_directory(download_dir: Optional[str],
                    fileobj: ccc.FileObject) -> Optional[str]:
    """
    The download cache directory of a file object's files

    pogos: {download_dir}/pogos/{host}/{url path} (the server layout, so
    files of different server directories never clash); mast:
    {download_dir}/mast/jw{pid}/o{obsnumber}

    :param download_dir: str or None, the download cache root
    :param fileobj: FileObject, the file source information

    :return: str or None, None if there is no cache (or not online)
    """
    if download_dir is None or not fileobj.online:
        return None
    root = os.path.join(os.path.abspath(str(download_dir)),
                        CACHE_SOURCE_DIRS[fileobj.source])
    if fileobj.source == 'pogos':
        if not fileobj.url:
            return None
        parsed = urlparse(str(fileobj.url))
        parts = [parsed.netloc] + parsed.path.split('/')
    else:
        parts = ['jw' + str(fileobj.pid).zfill(5),
                 'o' + str(fileobj.obsnumber).zfill(3)]
    # only keep safe path components (no '', '.', '..')
    parts = [_safe_part(part) for part in parts]
    parts = [part for part in parts if part not in ('', '.', '..')]
    return os.path.join(root, *parts)


def needs_download(fileobj: ccc.FileObject, directory: str,
                   download_dir: Optional[str] = None) -> bool:
    """
    Decide whether the files of a file object need obtaining

    A file counts as present if it exists in directory - except a symlink
    into the download cache that points at another cached file than this
    source gives (e.g. the url was changed), which is relinked.

    :param fileobj: FileObject, the file source information
    :param directory: str, the directory the files live in
    :param download_dir: str or None, the download cache root

    :return: bool, True if files need to be obtained (or linked)
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
    cache_dir = cache_directory(download_dir, fileobj)
    for filename in fileobj.files:
        localpath = _local_path(directory, filename)
        expected = _cache_path(cache_dir, filename)
        if not _present(localpath, expected, download_dir):
            return True
    return False


def link_cached(params: Any, fileobj: ccc.FileObject, directory: str,
                download_dir: Optional[str]) -> List[str]:
    """
    Symlink files that are in the download cache but missing from directory

    :param params: ParamDict, used for logging
    :param fileobj: FileObject, the file source information
    :param directory: str, the directory the files belong in
    :param download_dir: str or None, the download cache root

    :return: list of str, the files that were linked
    """
    cache_dir = cache_directory(download_dir, fileobj)
    if cache_dir is None or fileobj.always_download:
        return []
    linked = []
    for filename in fileobj.files:
        localpath = _local_path(directory, filename)
        cachepath = _cache_path(cache_dir, filename)
        if cachepath is None or _present(localpath, cachepath, download_dir):
            continue
        if os.path.isfile(cachepath):
            link_file(params, cachepath, localpath)
            linked.append(filename)
    return linked


def link_file(params: Any, src: str, dest: str) -> None:
    """
    Make dest a symlink to src (replacing whatever dest currently is)

    :param params: ParamDict, used for logging
    :param src: str, the file to link to
    :param dest: str, the symlink to create

    :return: None
    """
    src = os.path.abspath(src)
    # nothing to do if it already links there
    if os.path.islink(dest) and os.readlink(dest) == src:
        return
    # never remove the source itself (dest is src, e.g. via a symlinked
    #   directory)
    if (os.path.exists(dest) and not os.path.islink(dest)
            and os.path.samefile(dest, src)):
        return
    os.makedirs(os.path.dirname(os.path.abspath(dest)), exist_ok=True)
    if os.path.lexists(dest):
        os.remove(dest)
    WLOG(params, '', '\t\tLinking: {0} -> {1}'.format(dest, src))
    os.symlink(src, dest)


def resolve_files(params: Any, keys: Optional[Iterable[str]] = None,
                  skip_keys: Iterable[str] = (),
                  yaml_file: Optional[str] = None,
                  demolocal: Optional[str] = None,
                  demosymlink: bool = False,
                  dry_run: bool = False,
                  get_directory: Optional[Callable[[Any, str, str], str]]
                  = None,
                  download_dir: Optional[str] = None,
                  link_only: bool = False) -> Dict[str, Any]:
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
    :param download_dir: str or None, the download cache root: files are
                         stored there and symlinked into each directory,
                         and looked for there before going online
    :param link_only: bool, if True only link files already in the download
                      cache (never go online)

    :return: dict, key -> new yaml value for every key that was updated
    :raises FileSourceError: if two parameters want different files under
                             the same name in the same directory
    """
    # default to every file object parameter
    if keys is None:
        keys = find_file_keys(params)
    keys = list(keys)
    # upper case keys to compare case insensitively
    skip = set(key.upper() for key in skip_keys)
    # storage for yaml updates
    updates = dict()
    # file in a directory -> (key, source) of the parameter that wants it
    claimed: Dict[str, Tuple[str, str]] = dict()
    # loop around file object parameters
    for it, key in enumerate(keys):
        # report progress (e.g. the pogos_gui Status tab; no-op otherwise)
        gprogress.advance(detail='{0} ({1}/{2})'.format(key, it + 1,
                                                         len(keys)),
                          force=True)
        # get the instance and current value
        instance = params.instances.get(key, None)
        value = params[key]
        # get the source information (plain values are local)
        fileobj = ccc.get_fileobj(value)
        if fileobj is None or not fileobj.online:
            continue
        # skip files produced by an earlier step of this run
        if key.upper() in skip:
            if not link_only:
                msg = '\t{0}: produced by an earlier step - not downloading'
                WLOG(params, '', msg.format(key))
            continue
        # get the directory the files belong in
        directory = _get_directory(params, key, instance, get_directory)
        # the same file name must not come from two different sources
        _claim_files(claimed, key, fileobj, directory)
        # use files already in the download cache
        if not dry_run:
            linked = link_cached(params, fileobj, directory, download_dir)
            if len(linked) > 0:
                msg = '\t{0}: linked {1} file(s) from {2}'
                margs = [key, len(linked),
                         cache_directory(download_dir, fileobj)]
                WLOG(params, '', msg.format(*margs))
        # nothing to do if all files exist
        if not needs_download(fileobj, directory, download_dir):
            record_links(download_dir, fileobj, directory, key)
            if not link_only:
                msg = '\t{0}: all files present in {1}'
                WLOG(params, '', msg.format(key, directory))
            continue
        if link_only:
            continue
        # report what is being done
        msg = '\t{0}: obtaining files from {1}'
        WLOG(params, 'info', msg.format(key, fileobj.source))
        if dry_run:
            continue
        # make sure the directory exists
        os.makedirs(directory, exist_ok=True)
        cache_dir = cache_directory(download_dir, fileobj)
        # obtain the files from the source
        if fileobj.source == 'pogos':
            pkwargs = dict(demolocal=demolocal, demosymlink=demosymlink,
                           cache_dir=cache_dir, download_dir=download_dir)
            filenames = fetch_pogos(params, fileobj, directory, **pkwargs)
        else:
            mkwargs = dict(cache_dir=cache_dir, download_dir=download_dir)
            filenames = fetch_mast(params, fileobj, directory, **mkwargs)
        # files MAST gave (empty filelist) must not clash either
        new_fileobj = fileobj.copy()
        new_fileobj.filelist = _filelist_for(instance, filenames, key)
        _claim_files(claimed, key, new_fileobj, directory)
        # record which parameter uses each cached file
        record_links(download_dir, new_fileobj, directory, key)
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


def cache_meta_path(download_dir: str, cachepath: str) -> str:
    """
    The json record of a cached file

    :param download_dir: str, the download cache root
    :param cachepath: str, the cached file

    :return: str, {download_dir}/.meta/{relative path}.json
    """
    root = os.path.abspath(str(download_dir))
    rel = os.path.relpath(os.path.abspath(cachepath), root)
    return os.path.join(root, CACHE_META_DIR, rel + '.json')


def read_cache_meta(download_dir: str, cachepath: str) -> Dict[str, Any]:
    """
    Read the json record of a cached file (empty dict if there is none)

    :param download_dir: str, the download cache root
    :param cachepath: str, the cached file

    :return: dict, the record (source, origin, product, downloaded, links)
    """
    meta_file = cache_meta_path(download_dir, cachepath)
    try:
        with open(meta_file, 'r') as mfile:
            meta = json.load(mfile)
    except (OSError, ValueError):
        return dict()
    return meta if isinstance(meta, dict) else dict()


def write_cache_meta(download_dir: str, cachepath: str,
                     meta: Dict[str, Any]) -> None:
    """
    Write the json record of a cached file (atomically)

    :param download_dir: str, the download cache root
    :param cachepath: str, the cached file
    :param meta: dict, the record

    :return: None
    """
    meta_file = cache_meta_path(download_dir, cachepath)
    os.makedirs(os.path.dirname(meta_file), exist_ok=True)
    # unique temporary name (several runs may write at once)
    tmp_file = '{0}.{1}.tmp'.format(meta_file, os.getpid())
    with open(tmp_file, 'w') as mfile:
        json.dump(meta, mfile, indent=1, sort_keys=True)
    os.replace(tmp_file, meta_file)


def record_download(download_dir: Optional[str], cachepath: str,
                    fileobj: ccc.FileObject, source: str,
                    origin: str) -> None:
    """
    Record where and when a cached file was obtained (keeps its links)

    :param download_dir: str or None, the download cache root
    :param cachepath: str, the cached file
    :param fileobj: FileObject, the file source information
    :param source: str, pogos / mast / local (copied from a local mirror)
    :param origin: str, the url, MAST observation or mirror file

    :return: None
    """
    if download_dir is None:
        return
    meta = read_cache_meta(download_dir, cachepath)
    meta.update(source=source, origin=origin, product=fileobj.product,
                downloaded=time.time(), file=os.path.abspath(cachepath))
    meta.setdefault('links', dict())
    write_cache_meta(download_dir, cachepath, meta)


def record_links(download_dir: Optional[str], fileobj: ccc.FileObject,
                 directory: str, key: str) -> None:
    """
    Record the parameter key of every symlink to a cached file

    Only writes records that change (cheap on every run).

    :param download_dir: str or None, the download cache root
    :param fileobj: FileObject, the file source information
    :param directory: str, the directory the files belong in
    :param key: str, the parameter key using the files

    :return: None
    """
    cache_dir = cache_directory(download_dir, fileobj)
    if cache_dir is None:
        return
    for filename in fileobj.files:
        localpath = os.path.abspath(_local_path(directory, filename))
        cachepath = _cache_path(cache_dir, filename)
        # only links into the cache are recorded
        if cachepath is None or not os.path.islink(localpath):
            continue
        if os.path.realpath(localpath) != os.path.realpath(cachepath):
            continue
        meta = read_cache_meta(download_dir, cachepath)
        links = meta.setdefault('links', dict())
        if links.get(localpath) == key:
            continue
        links[localpath] = key
        # files cached before records existed
        meta.setdefault('source', fileobj.source)
        meta.setdefault('product', fileobj.product)
        meta.setdefault('file', os.path.abspath(cachepath))
        write_cache_meta(download_dir, cachepath, meta)


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
    lines.append('Files already downloaded (e.g. by another project) are '
                 'reused, not downloaded again.')
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
                demosymlink: bool = False,
                cache_dir: Optional[str] = None,
                download_dir: Optional[str] = None) -> List[str]:
    """
    Get files from the POGOS data server (or a local mirror of it)

    With a cache_dir files are stored there and symlinked into directory
    (a demolocal mirror with demosymlink is linked to directly instead).

    :param params: ParamDict, used for logging
    :param fileobj: FileObject, with filelist and url set
    :param directory: str, the directory the files belong in
    :param demolocal: str or None, local mirror root (the last directory of
                      the url is looked for inside this)
    :param demosymlink: bool, symlink (True) or copy (False) from demolocal
    :param cache_dir: str or None, this url's download cache directory
    :param download_dir: str or None, the download cache root

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
        # report what is being obtained (rate limited, no-op if no gui)
        gprogress.advance(detail='{0}: {1}'.format(fileobj.name, basename))
        # absolute filenames are written where they are (no cache)
        cachepath = _cache_path(cache_dir, filename)
        # skip existing files unless always_download is set
        present = _present(localpath, cachepath, download_dir)
        if present and not fileobj.always_download:
            filenames.append(basename)
            continue
        # the local mirror file (if a mirror is used)
        src_path = None
        if demolocal is not None:
            last_dir = fileobj.url.rstrip('/').split('/')[-1]
            src_path = os.path.join(demolocal, last_dir, basename)
            if not os.path.exists(src_path):
                emsg = 'Local mirror file not found: {0}'
                raise FileSourceError(emsg.format(src_path))
        # symlink straight to the mirror (nothing stored in the cache)
        if src_path is not None and demosymlink:
            link_file(params, src_path, localpath)
            filenames.append(basename)
            continue
        # the file is stored in the cache (or directly in directory)
        target = localpath if cachepath is None else cachepath
        os.makedirs(os.path.dirname(target), exist_ok=True)
        # remove any existing file first (always_download / stale link)
        if os.path.lexists(target):
            os.remove(target)
        if src_path is not None:
            WLOG(params, '', '\t\tCopying: {0}'.format(target))
            shutil.copy2(src_path, target)
            origin = dict(source='local', origin=src_path)
        else:
            url = fileobj.url.rstrip('/') + '/' + basename
            WLOG(params, '', '\t\tDownloading: {0}'.format(url))
            download_url(url, target)
            origin = dict(source='pogos', origin=url)
        # record where / when the cached file came from
        if cachepath is not None:
            record_download(download_dir, cachepath, fileobj, **origin)
        # link the cached file into directory
        if cachepath is not None:
            link_file(params, cachepath, localpath)
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
               observations_module: Any = None,
               cache_dir: Optional[str] = None,
               download_dir: Optional[str] = None) -> List[str]:
    """
    Download MAST products for a file object

    With a cache_dir products are downloaded there (only those not already
    cached) and symlinked into directory.

    :param params: ParamDict, used for logging
    :param fileobj: FileObject, with pid, obsnumber and product set
    :param directory: str, the directory the files belong in
    :param observations_module: astroquery.mast.Observations (for testing)
    :param cache_dir: str or None, this observation's download cache
    :param download_dir: str or None, the download cache root

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
    # products are stored in the cache (or directly in directory)
    target_dir = directory if cache_dir is None else cache_dir
    os.makedirs(target_dir, exist_ok=True)
    # only download files we do not have (unless always_download)
    if not fileobj.always_download:
        mask = []
        for name in products['productFilename']:
            localpath = os.path.join(directory, str(name))
            cachepath = _cache_path(cache_dir, str(name))
            # already in directory, or already in the cache
            have = _present(localpath, cachepath, download_dir)
            have |= cachepath is not None and os.path.isfile(cachepath)
            mask.append(not have)
        products = products[mask]
    # download
    msg = '\t\tDownloading {0} file(s) from MAST to {1}'
    WLOG(params, '', msg.format(len(products), target_dir))
    gprogress.advance(detail='{0}: downloading {1} file(s) from MAST'.format(
        fileobj.name, len(products)), force=True)
    if len(products) > 0:
        dkwargs = dict(download_dir=target_dir, flat=True)
        manifest = observations_module.download_products(products, **dkwargs)
        # check the manifest for failures
        _check_manifest(fileobj, manifest)
        # record where / when the cached files came from
        if cache_dir is not None:
            for name in products['productFilename']:
                cachepath = os.path.join(cache_dir, str(name))
                if os.path.isfile(cachepath):
                    rkwargs = dict(source='mast', origin=_mast_label(fileobj))
                    record_download(download_dir, cachepath, fileobj,
                                    **rkwargs)
    # link cached files into directory
    for filename in filenames:
        localpath = os.path.join(directory, filename)
        cachepath = _cache_path(cache_dir, filename)
        if cachepath is None or not os.path.isfile(cachepath):
            continue
        refresh = fileobj.always_download
        if refresh or not _present(localpath, cachepath, download_dir):
            link_file(params, cachepath, localpath)
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


def _safe_part(part: str) -> str:
    """Make a url / id component safe to use as one directory name."""
    keep = [char if (char.isalnum() or char in '-+._') else '_'
            for char in str(part)]
    return ''.join(keep)


def _cache_path(cache_dir: Optional[str], filename: str) -> Optional[str]:
    """
    The download cache path of a filelist entry

    :param cache_dir: str or None, the cache directory of this source
    :param filename: str, the filelist entry

    :return: str or None, None without a cache or for absolute filenames
             (those are used where they are)
    """
    if cache_dir is None or os.path.isabs(filename):
        return None
    return os.path.join(cache_dir, os.path.basename(filename))


def _present(localpath: str, expected: Optional[str],
             download_dir: Optional[str]) -> bool:
    """
    Whether a file is present in its directory

    A symlink into the download cache that points to another cached file
    than expected (e.g. the url / program changed) does not count.

    :param localpath: str, the file in the constant's directory
    :param expected: str or None, the cache file it should link to
    :param download_dir: str or None, the download cache root

    :return: bool, True if present
    """
    if not os.path.exists(localpath):
        return False
    if expected is None or download_dir is None:
        return True
    if not os.path.islink(localpath):
        return True
    real = os.path.realpath(localpath)
    root = os.path.realpath(str(download_dir)) + os.sep
    if real.startswith(root):
        return real == os.path.realpath(expected)
    return True


def _source_label(fileobj: ccc.FileObject) -> str:
    """A short description of where a file object's files come from."""
    if fileobj.source == 'pogos':
        return 'pogos {0}'.format(str(fileobj.url).rstrip('/'))
    if fileobj.source == 'mast':
        return 'mast pid={0} obsnumber={1}'.format(fileobj.pid,
                                                  fileobj.obsnumber)
    return str(fileobj.source)


def _mast_label(fileobj: ccc.FileObject) -> str:
    """The MAST program / observation of a file object (for records)."""
    return 'jw{0} o{1}'.format(str(fileobj.pid).zfill(5),
                               str(fileobj.obsnumber).zfill(3))


def _claim_files(claimed: Dict[str, Tuple[str, str]], key: str,
                 fileobj: ccc.FileObject, directory: str) -> None:
    """
    Record which parameter / source each file of a directory comes from

    :param claimed: dict, file path -> (key, source label) (updated)
    :param key: str, the parameter key
    :param fileobj: FileObject, the file source information
    :param directory: str, the directory the files belong in

    :return: None
    :raises FileSourceError: if a file name is wanted from two different
                             sources (they would overwrite each other)
    """
    label = _source_label(fileobj)
    for filename in fileobj.files:
        localpath = os.path.abspath(_local_path(directory, filename))
        other = claimed.get(localpath, None)
        if other is not None and other[1] != label:
            emsg = ('File name clash: {0} is wanted by {1} ({2}) and by '
                    '{3} ({4}). Give one of them a different directory '
                    'parameter.')
            eargs = [localpath, other[0], other[1], key, label]
            raise FileSourceError(emsg.format(*eargs))
        claimed[localpath] = (key, label)


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
