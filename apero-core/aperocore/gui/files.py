#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Safe file access for browser guis

Every path that comes from the browser is resolved (symbolic links and
".." removed) and checked to be inside one of the application's allowed
root directories before anything is read or deleted. Deleting a root
itself is never allowed.

Also provides directory listings, small text reads, image collection
(for plot galleries) and directory size summaries.

Created on 2026-11-26

@author: cook
"""
import os
import shutil
import stat
import time
from typing import Any, Dict, List, Optional

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'aperocore.gui.files.py'
# maximum number of bytes of a text file sent to the browser
TEXT_MAX_BYTES = 2 * 1024 * 1024
# maximum number of entries listed for one directory
LIST_MAX_ENTRIES = 5000
# file extensions treated as images (shown inline)
IMAGE_EXTS = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp']
# file extensions treated as FITS files
FITS_EXTS = ['.fits', '.fit', '.fts', '.fits.gz', '.fit.gz']
# file extensions treated as text
TEXT_EXTS = ['.txt', '.yaml', '.yml', '.log', '.csv', '.dat', '.json',
             '.py', '.md', '.ecsv', '.tex', '.sh', '.sbatch', '.cfg',
             '.ini', '.out', '.err', '.ecf', '.epf', '.html', '.rc']


# =============================================================================
# Define classes
# =============================================================================
class FileAccessError(Exception):
    """Raised when a path is outside the allowed roots (or invalid)"""


# =============================================================================
# Define path functions
# =============================================================================
def is_within(path: str, root: str) -> bool:
    """
    Whether a (resolved) path is a root or inside it

    :param path: str, the resolved absolute path
    :param root: str, the resolved absolute root

    :return: bool, True if path is root or below root
    """
    root = root.rstrip(os.sep) or os.sep
    return path == root or path.startswith(root + os.sep)


def check_path(path: str, roots: Optional[List[str]]) -> str:
    """
    Resolve a path from the browser and check it is inside a root

    :param path: str, the requested path
    :param roots: list of str or None, the allowed roots (None = any path,
                  only used for read-only browsing)

    :raises FileAccessError: if the path is empty, contains a null byte or
                             is outside every root

    :return: str, the resolved absolute path
    """
    if path is None or str(path).strip() == '' or '\x00' in str(path):
        raise FileAccessError('invalid path')
    real = os.path.realpath(os.path.expanduser(str(path)))
    if roots is None:
        return real
    for root in roots:
        if is_within(real, os.path.realpath(root)):
            return real
    raise FileAccessError('path is outside the allowed directories: '
                          '{0}'.format(path))


def file_kind(name: str, is_dir: bool = False) -> str:
    """
    Classify a file by its name (for icons and viewers)

    :param name: str, the file name
    :param is_dir: bool, True for directories

    :return: str, one of dir, image, fits, text, other
    """
    if is_dir:
        return 'dir'
    lower = name.lower()
    if any(lower.endswith(ext) for ext in IMAGE_EXTS):
        return 'image'
    if any(lower.endswith(ext) for ext in FITS_EXTS):
        return 'fits'
    if any(lower.endswith(ext) for ext in TEXT_EXTS):
        return 'text'
    return 'other'


def list_directory(path: str, roots: Optional[List[str]],
                   exts: Optional[List[str]] = None,
                   show_hidden: bool = False) -> Dict[str, Any]:
    """
    List one directory (directories first, then files, by name)

    :param path: str, the directory (blank = the first root, or home)
    :param roots: list of str or None, the allowed roots (None = any)
    :param exts: list of str or None, only list files with these endings
    :param show_hidden: bool, include entries starting with a dot

    :raises FileAccessError: if the path is outside the roots

    :return: dict(path, parent, entries, truncated, error); each entry is
             dict(name, path, kind, size, mtime)
    """
    # default directory: the first root (or home for unrestricted)
    if path in [None, '']:
        path = roots[0] if roots else os.path.expanduser('~')
    real = check_path(path, roots)
    # list the parent of a file
    if os.path.isfile(real):
        real = os.path.dirname(real)
    out = dict(path=real, parent=None, entries=[], truncated=False,
               error=None)
    # the parent (only if still inside the roots)
    parent = os.path.dirname(real)
    if parent != real:
        try:
            check_path(parent, roots)
            out['parent'] = parent
        except FileAccessError:
            out['parent'] = None
    try:
        names = os.listdir(real)
    except OSError as error:
        out['error'] = str(error)
        return out
    entries = []
    for name in names:
        if not show_hidden and name.startswith('.'):
            continue
        full = os.path.join(real, name)
        try:
            info = os.stat(full)
        except OSError:
            # broken link etc.
            continue
        is_dir = stat.S_ISDIR(info.st_mode)
        lower = name.lower()
        if exts and not is_dir and not any(lower.endswith(ext.lower())
                                           for ext in exts):
            continue
        entries.append(dict(name=name, path=full,
                            kind=file_kind(name, is_dir),
                            size=None if is_dir else info.st_size,
                            mtime=info.st_mtime))
    entries.sort(key=lambda ent: (ent['kind'] != 'dir', ent['name'].lower()))
    if len(entries) > LIST_MAX_ENTRIES:
        entries = entries[:LIST_MAX_ENTRIES]
        out['truncated'] = True
    out['entries'] = entries
    return out


def read_text(path: str, roots: Optional[List[str]],
              max_bytes: int = TEXT_MAX_BYTES) -> Dict[str, Any]:
    """
    Read (the start of) a text file

    :param path: str, the file path
    :param roots: list of str or None, the allowed roots (None = any)
    :param max_bytes: int, the maximum number of bytes read

    :raises FileAccessError: if the path is outside the roots

    :return: dict(path, text, size, truncated, mtime, error)
    """
    real = check_path(path, roots)
    out = dict(path=real, text='', size=0, truncated=False, mtime=None,
               error=None)
    if not os.path.isfile(real):
        out['error'] = 'not a file'
        return out
    out['size'] = os.path.getsize(real)
    out['mtime'] = os.path.getmtime(real)
    with open(real, 'rb') as tfile:
        data = tfile.read(max_bytes + 1)
    if len(data) > max_bytes:
        data = data[:max_bytes]
        out['truncated'] = True
    # binary files are not shown as text
    if b'\x00' in data[:8192]:
        out['error'] = 'binary file'
        return out
    out['text'] = data.decode('utf-8', errors='replace')
    return out


def write_text(path: str, text: str, roots: Optional[List[str]],
               backup_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Write a text file (atomically), optionally keeping a time stamped
    backup of the previous version

    :param path: str, the file path
    :param text: str, the new text
    :param roots: list of str or None, the allowed roots (None = any)
    :param backup_dir: str or None, directory for the backup copy

    :raises FileAccessError: if the path is outside the roots

    :return: dict(path, backup, size)
    """
    real = check_path(path, roots)
    backup = None
    # keep a copy of the previous version
    if backup_dir is not None and os.path.isfile(real):
        os.makedirs(backup_dir, exist_ok=True)
        stamp = time.strftime('%Y%m%d-%H%M%S')
        backup = os.path.join(backup_dir, '{0}.{1}.bak'.format(
            os.path.basename(real), stamp))
        shutil.copy2(real, backup)
    os.makedirs(os.path.dirname(real), exist_ok=True)
    tmp_path = '{0}.tmp{1}'.format(real, os.getpid())
    with open(tmp_path, 'w', encoding='utf-8') as tfile:
        tfile.write(text)
    os.replace(tmp_path, real)
    return dict(path=real, backup=backup, size=os.path.getsize(real))


def delete_paths(paths: List[str], roots: List[str]) -> Dict[str, Any]:
    """
    Delete files and directories (only inside the roots, never a root)

    :param paths: list of str, the paths to delete
    :param roots: list of str, the allowed roots

    :return: dict(success, message, deleted=list of str, errors=list)
    """
    deleted, errors = [], []
    real_roots = [os.path.realpath(root) for root in roots]
    for path in paths:
        try:
            # links are removed themselves (never their target)
            absolute = os.path.abspath(os.path.expanduser(path))
            if os.path.islink(absolute):
                check_path(os.path.dirname(absolute), roots)
                os.remove(absolute)
                deleted.append(absolute)
                continue
            real = check_path(path, roots)
            if real in real_roots:
                raise FileAccessError('refusing to delete a root directory: '
                                      '{0}'.format(real))
            if os.path.isdir(real):
                shutil.rmtree(real)
            elif os.path.exists(real):
                os.remove(real)
            else:
                raise FileAccessError('does not exist: {0}'.format(real))
            deleted.append(real)
        except (FileAccessError, OSError) as error:
            errors.append(str(error))
    message = 'Deleted {0} item(s)'.format(len(deleted))
    if errors:
        message += '; {0} error(s): {1}'.format(len(errors),
                                                '; '.join(errors))
    return dict(success=len(errors) == 0, message=message, deleted=deleted,
                errors=errors)


def dir_stats(path: str) -> Dict[str, Any]:
    """
    Count the files and total size below a directory

    :param path: str, the directory

    :return: dict(nfiles, size, mtime) - mtime is the newest file time
    """
    nfiles, size, newest = 0, 0, 0.0
    for root, _, names in os.walk(path):
        for name in names:
            try:
                info = os.stat(os.path.join(root, name))
            except OSError:
                continue
            nfiles += 1
            size += info.st_size
            newest = max(newest, info.st_mtime)
    return dict(nfiles=nfiles, size=size, mtime=newest or None)


def find_images(top: str, exts: Optional[List[str]] = None,
                max_files: int = 20000) -> List[Dict[str, Any]]:
    """
    Find the image files below a directory (for plot galleries)

    :param top: str, the directory to search
    :param exts: list of str or None, image endings (default IMAGE_EXTS)
    :param max_files: int, stop after this many images

    :return: list of dict(path, rel, dir, name, size, mtime) where rel is
             relative to top and dir is the relative directory
    """
    exts = [ext.lower() for ext in (exts or IMAGE_EXTS)]
    images = []
    for root, dirs, names in os.walk(top):
        # skip hidden directories
        dirs[:] = sorted(name for name in dirs if not name.startswith('.'))
        for name in sorted(names):
            if not any(name.lower().endswith(ext) for ext in exts):
                continue
            full = os.path.join(root, name)
            try:
                info = os.stat(full)
            except OSError:
                continue
            rel = os.path.relpath(full, top)
            images.append(dict(path=full, rel=rel,
                               dir=os.path.dirname(rel), name=name,
                               size=info.st_size, mtime=info.st_mtime))
            if len(images) >= max_files:
                return images
    return images


# =============================================================================
# End of code
# =============================================================================
