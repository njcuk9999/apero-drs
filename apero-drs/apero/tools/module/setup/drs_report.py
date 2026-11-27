#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO state report (apero_validate.py --report and the setup gui)

Collects the state of an installed APERO profile into one json friendly
dictionary and formats it as a single plain text file that is easy to read
for humans and for AI assistants (stable section names, one "key: value"
per line, a summary of every problem at the top). Sections:

    - profile:  name, DRS_UCONFIG, instrument, language, setup choices
    - config:   the files apero_setup writes to DRS_UCONFIG (exist, parse,
                APERO version that wrote them)
    - paths:    every data directory (exists, writable, entries, disk use)
    - database: connection settings (never the password) and every table
                (exists, number of rows, a break down by its key column)
    - modules:  python, APERO / apero-core versions (and git state), the
                installed version of every APERO requirement
    - machine:  host, operating system, cpus, memory and load

Every section is collected independently: a failure in one section is
recorded as a problem of that section and never stops the report.

Created on 2026-11-27

@author: cook
"""
import datetime
import getpass
import importlib.metadata as importlib_metadata
import math
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from aperocore.base import base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero.tools.module.setup.drs_report.py'
# the version of the report layout (bump when sections / keys change)
REPORT_VERSION = 1
# status levels (ordered by severity)
LEVELS = ['ok', 'info', 'warn', 'bad']
# the files apero_setup writes into DRS_UCONFIG (name -> kind)
CONFIG_FILES = dict([('install.yaml', 'yaml'), ('database.yaml', 'yaml'),
                     ('user_config.yaml', 'yaml'),
                     ('user_constants.yaml', 'yaml'),
                     ('user_keywords.yaml', 'yaml'), ('setup.sh', 'text'),
                     ('setup.bat', 'text'), ('install_script.sh', 'text')])
# config files that must exist for APERO to start
REQUIRED_CONFIG = ['install.yaml', 'database.yaml', 'user_config.yaml']
# the data directories of a profile (parameter -> label)
PATH_KEYS = dict([('PATH.RAW', 'raw'), ('PATH.PP', 'tmp (pre-processed)'),
                  ('PATH.RED', 'reduced'), ('PATH.CALIB', 'calibration'),
                  ('PATH.TELLU', 'telluric'), ('PATH.OUT', 'out'),
                  ('PATH.LBL', 'lbl'), ('PATH.LOG', 'log'),
                  ('PATH.PLOT', 'plot'), ('PATH.RUN', 'run'),
                  ('PATH.ASSETS', 'assets'), ('PATH.OTHER', 'other')])
# the optional external raw directory
EXTERNAL_RAW_KEY = 'PATH.EXTERNAL_RAW'
# directories with more entries than this are reported as "> limit"
ENTRY_LIMIT = 100000
# database kind -> column used to break the rows down (if it exists)
DB_GROUPBY = dict(calib='KEYNAME', tellu='KEYNAME', findex='BLOCK_KIND',
                  log='RECIPE')
# databases stored as files (not sql tables)
FILE_STORES = ['astrom', 'reject']
# at most this many groups are listed per table
DB_MAX_GROUPS = 40
# the version line written in the header of apero yaml files
VERSION_RE = re.compile(r'^#\s*Version\s*=\s*(\S+)')
# packages always listed (in addition to the requirements of apero)
CORE_PACKAGES = ['apero', 'aperocore', 'apero_ri', 'lbl']
# seconds a git command may take
GIT_TIMEOUT = 5
# shown instead of secrets
MASK = '********'


# =============================================================================
# Define helper functions
# =============================================================================
def _now() -> str:
    """
    Get the current time (UTC, ISO format, seconds)

    :return: str, the time stamp
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    return now.replace(microsecond=0).isoformat()


def _check(level: str, section: str, message: str) -> Dict[str, str]:
    """
    Create one check result (a line of the report summary)

    :param level: str, one of LEVELS
    :param section: str, the section the check belongs to
    :param message: str, what was found

    :return: dict(level, section, message)
    """
    return dict(level=level, section=section, message=message)


def _plain(value: Any) -> Any:
    """
    Convert a value to something json / yaml / text friendly

    :param value: Any, the value

    :return: Any, str / int / float / bool / None / list / dict
    """
    # NaN / inf are not valid json (kept as text)
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    # simple types are kept as they are
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    # containers are converted recursively
    if isinstance(value, dict):
        return {str(key): _plain(val) for key, val in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_plain(val) for val in value]
    # everything else (paths, numpy types...) as a string
    return str(value)


def _file_version(path: str) -> Optional[str]:
    """
    Get the APERO version written in the header of a config yaml file

    :param path: str, the yaml file

    :return: str or None, the version (None if there is no version line)
    """
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as rfile:
            # the version is in the first few comment lines
            for _ in range(20):
                line = rfile.readline()
                if not line:
                    break
                match = VERSION_RE.match(line.strip())
                if match:
                    return match.group(1)
    except OSError:
        return None
    return None


def _major_minor(version: Optional[str]) -> Optional[Tuple[str, ...]]:
    """
    Get the major / minor part of a version string (0.8.112 -> (0, 8))

    :param version: str or None, the version

    :return: tuple or None, the major and minor parts
    """
    if not version:
        return None
    parts = str(version).split('.')
    if len(parts) < 2:
        return None
    return tuple(parts[:2])


def _bytes(nbytes: Optional[float]) -> str:
    """
    Format a number of bytes for humans (e.g. 12.3 GiB)

    :param nbytes: float or None, the number of bytes

    :return: str, the formatted size
    """
    if nbytes is None:
        return 'unknown'
    value = float(nbytes)
    for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB']:
        if abs(value) < 1024 or unit == 'TiB':
            return '{0:.1f} {1}'.format(value, unit)
        value /= 1024.0
    return '{0:.1f} PiB'.format(value)


def _git_state(path: str) -> Dict[str, Any]:
    """
    Get the git branch / commit / dirty state of a source directory

    :param path: str, a directory inside the git checkout

    :return: dict(branch, commit, dirty) or dict(error)
    """
    def _git(*args: str) -> str:
        """
        Run one git command in the source directory

        :param args: str, the git arguments

        :return: str, the stripped output
        """
        output = subprocess.run(['git', '-C', path] + list(args),
                                capture_output=True, text=True,
                                timeout=GIT_TIMEOUT, check=True)
        return output.stdout.strip()

    try:
        branch = _git('rev-parse', '--abbrev-ref', 'HEAD')
        commit = _git('rev-parse', '--short', 'HEAD')
        # only tracked files count as "dirty"
        dirty = bool(_git('status', '--porcelain', '--untracked-files=no'))
        return dict(branch=branch, commit=commit, dirty=dirty)
    except (OSError, subprocess.SubprocessError) as error:
        return dict(error='not a git checkout ({0})'.format(
            type(error).__name__))


def _param(params: Any, key: str) -> Any:
    """
    Get a parameter value (None if it is missing)

    :param params: ParamDict or dict, the parameters
    :param key: str, the parameter key

    :return: Any, the value
    """
    try:
        if key in params:
            return params[key]
    except Exception as _:
        return None
    return None


# =============================================================================
# Define section functions
# =============================================================================
def profile_section(config_dir: str) -> Dict[str, Any]:
    """
    Describe the profile (from install.yaml and ~/.apero/profiles.ini)

    :param config_dir: str, the DRS_UCONFIG directory

    :return: dict(values, checks)
    """
    values: Dict[str, Any] = dict(name=os.path.basename(
        os.path.normpath(config_dir)), drs_uconfig=config_dir)
    checks: List[Dict[str, str]] = []
    # the install yaml holds the instrument, language and setup choices
    install_path = os.path.join(config_dir, base.INSTALL_YAML)
    if os.path.isfile(install_path):
        with open(install_path, 'r', encoding='utf-8') as ifile:
            install = yaml.safe_load(ifile) or dict()
        values['instrument'] = install.get('OBS.INSTRUMENT')
        values['language'] = install.get('GLOBAL.LANGUAGE')
        values['setup_arguments'] = _plain(install.get('SETUP_ARGUMENTS',
                                                       dict()))
        # the profile should point at itself
        recorded = install.get(base.USER_ENV)
        if recorded and os.path.realpath(str(recorded)) != (
                os.path.realpath(config_dir)):
            checks.append(_check('warn', 'profile', 'install.yaml '
                                 'DRS_UCONFIG={0} differs from the profile '
                                 'directory'.format(recorded)))
    # the profiles.ini registry (used by apero_profile.sh)
    profile_file = os.path.expanduser('~/.apero/profiles.ini')
    registered = None
    if os.path.isfile(profile_file):
        with open(profile_file, 'r', encoding='utf-8') as pfile:
            for line in pfile:
                if '=' not in line:
                    continue
                key, value = line.split('=', 1)
                if os.path.realpath(value.strip()) == (
                        os.path.realpath(config_dir)):
                    registered = key.strip()
    values['registered_as'] = registered
    if registered is None:
        checks.append(_check('info', 'profile', 'profile is not listed in '
                             '~/.apero/profiles.ini'))
    # the activated profile of this process
    values['active_drs_uconfig'] = os.environ.get(base.USER_ENV)
    return dict(values=values, checks=checks)


def config_section(config_dir: str, apero_version: str) -> Dict[str, Any]:
    """
    Describe the files apero_setup writes into DRS_UCONFIG

    :param config_dir: str, the DRS_UCONFIG directory
    :param apero_version: str, the running APERO version

    :return: dict(files, checks)
    """
    files: List[Dict[str, Any]] = []
    checks: List[Dict[str, str]] = []
    for name, kind in CONFIG_FILES.items():
        path = os.path.join(config_dir, name)
        entry: Dict[str, Any] = dict(name=name, path=path,
                                     exists=os.path.isfile(path))
        if not entry['exists']:
            level = 'bad' if name in REQUIRED_CONFIG else 'info'
            checks.append(_check(level, 'config', name + ' is missing'))
            files.append(entry)
            continue
        stat = os.stat(path)
        entry['size'] = stat.st_size
        entry['modified'] = datetime.datetime.fromtimestamp(
            stat.st_mtime, datetime.timezone.utc).replace(
            microsecond=0).isoformat()
        # yaml files must parse
        if kind == 'yaml':
            try:
                with open(path, 'r', encoding='utf-8') as yfile:
                    data = yaml.safe_load(yfile)
                entry['parse'] = 'ok'
                entry['nkeys'] = len(data) if isinstance(data, dict) else 0
            except (OSError, yaml.YAMLError) as error:
                entry['parse'] = 'error: {0}'.format(
                    str(error).splitlines()[0])
                checks.append(_check('bad', 'config', '{0} does not parse '
                                     '({1})'.format(name, entry['parse'])))
        # the version of APERO that wrote the file
        version = _file_version(path)
        entry['written_by'] = version
        if version and _major_minor(version) != _major_minor(apero_version):
            checks.append(_check('warn', 'config', '{0} was written by APERO '
                                 '{1} (running {2}) - re-run apero_setup'
                                 ''.format(name, version, apero_version)))
        files.append(entry)
    return dict(files=files, checks=checks)


def paths_section(params: Any) -> Dict[str, Any]:
    """
    Describe every data directory of the profile

    :param params: ParamDict, the profile parameters

    :return: dict(paths, filesystems, checks)
    """
    paths: List[Dict[str, Any]] = []
    checks: List[Dict[str, str]] = []
    # file system usage (one entry per distinct file system)
    filesystems: Dict[str, Dict[str, Any]] = dict()
    keys = list(PATH_KEYS.items())
    external = _param(params, EXTERNAL_RAW_KEY)
    if external not in [None, '', 'None']:
        keys.append((EXTERNAL_RAW_KEY, 'external raw (read only)'))
    for key, label in keys:
        value = _param(params, key)
        entry: Dict[str, Any] = dict(key=key, label=label,
                                     path=None if value is None else
                                     str(value))
        if value in [None, '', 'None']:
            checks.append(_check('bad', 'paths', key + ' is not set'))
            paths.append(entry)
            continue
        path = str(value)
        entry['exists'] = os.path.isdir(path)
        entry['symlink'] = os.path.islink(path)
        if not entry['exists']:
            checks.append(_check('bad', 'paths', '{0} does not exist: {1}'
                                 ''.format(key, path)))
            paths.append(entry)
            continue
        entry['writable'] = os.access(path, os.W_OK)
        # the external raw directory is only read
        if not entry['writable'] and key != EXTERNAL_RAW_KEY:
            checks.append(_check('bad', 'paths', '{0} is not writable: {1}'
                                 ''.format(key, path)))
        # count the top level entries only (cheap even for big trees)
        try:
            count = 0
            with os.scandir(path) as entries:
                for _ in entries:
                    count += 1
                    if count > ENTRY_LIMIT:
                        break
            entry['entries'] = count if count <= ENTRY_LIMIT else (
                '> {0}'.format(ENTRY_LIMIT))
        except OSError as error:
            entry['entries'] = 'error: {0}'.format(error)
        # the file system the directory is on
        try:
            usage = shutil.disk_usage(path)
            device = str(os.stat(path).st_dev)
            entry['filesystem'] = device
            if device not in filesystems:
                frac = usage.free / usage.total if usage.total else 0
                filesystems[device] = dict(example=path, total=usage.total,
                                           free=usage.free,
                                           free_fraction=round(frac, 4))
                if frac < 0.05:
                    checks.append(_check('warn', 'paths', 'less than 5% free '
                                         'disk space on {0} ({1} free)'
                                         ''.format(path,
                                                   _bytes(usage.free))))
        except OSError:
            entry['filesystem'] = None
        paths.append(entry)
    return dict(paths=paths, filesystems=list(filesystems.values()),
                checks=checks)


def database_section(params: Any) -> Dict[str, Any]:
    """
    Describe the database connection and every APERO table

    :param params: ParamDict, the profile parameters

    :return: dict(settings, tables, checks)
    """
    checks: List[Dict[str, str]] = []
    # connection settings (never the password)
    dparams = base.load_database_yaml()
    settings = dict(type=dparams.get('TYPE'), host=dparams.get('HOST'),
                    user=dparams.get('USER'),
                    database=dparams.get('DATABASE'),
                    use_ssl=dparams.get('USE_SSL'),
                    password='not set' if dparams.get('PASSWD') in [
                        None, '', 'None'] else MASK)
    tables: List[Dict[str, Any]] = []
    # import here: needs an activated profile
    from apero.tools.module.database import manage_databases
    try:
        databases = manage_databases.list_databases(params, 'VALID')
    except Exception as error:
        checks.append(_check('bad', 'database', 'could not create the '
                             'database managers: {0}: {1}'.format(
                                 type(error).__name__, error)))
        return dict(settings=settings, tables=tables, checks=checks)
    for kind, dbm in databases.items():
        entry: Dict[str, Any] = dict(kind=kind)
        # file backed stores (astrometrics yaml directory, reject csv)
        if kind in FILE_STORES:
            entry.update(_file_store(dbm))
            tables.append(entry)
            continue
        try:
            dbm.load_db()
            entry['table'] = getattr(dbm, 'dbtable', None)
            database = dbm.database
            entry['exists'] = bool(database.has_table(entry['table']))
            if not entry['exists']:
                checks.append(_check('bad', 'database', 'table {0} ({1}) '
                                     'does not exist'.format(entry['table'],
                                                             kind)))
                tables.append(entry)
                continue
            entry['rows'] = int(database.count())
            # break the rows down by the key column of this table
            column = DB_GROUPBY.get(kind)
            colnames = list(database.colnames('*') or [])
            if column and column in colnames and entry['rows'] > 0:
                counts = database.get('{0}, COUNT(*)'.format(column),
                                      groupby=column, return_pandas=True)
                groups = sorted(((str(row[0]), int(row[1]))
                                 for row in counts.itertuples(index=False)),
                                key=lambda item: -item[1])
                entry['groupby'] = column
                entry['groups'] = dict(groups[:DB_MAX_GROUPS])
                entry['ngroups'] = len(groups)
        except Exception as error:
            entry['error'] = '{0}: {1}'.format(type(error).__name__,
                                               str(error).splitlines()[0]
                                               if str(error) else '')
            checks.append(_check('bad', 'database', '{0} database: {1}'
                                 ''.format(kind, entry['error'])))
        tables.append(entry)
    # an empty file index usually means the raw directory was never indexed
    for entry in tables:
        if entry['kind'] == 'findex' and entry.get('rows') == 0:
            checks.append(_check('info', 'database', 'the file index is empty '
                                 '(no files processed / indexed yet)'))
    return dict(settings=settings, tables=tables, checks=checks)


def _file_store(dbm: Any) -> Dict[str, Any]:
    """
    Describe a file backed store (astrometric yaml files / reject csv)

    :param dbm: Any, the store manager (has a "path" attribute)

    :return: dict(store, path, exists, rows)
    """
    path = str(getattr(dbm, 'path', '') or '')
    entry: Dict[str, Any] = dict(store='files', path=path,
                                 exists=os.path.exists(path))
    if not entry['exists']:
        # created on first use (not an error)
        entry['rows'] = 0
        return entry
    if os.path.isdir(path):
        # one yaml file per object
        entry['rows'] = len([name for name in os.listdir(path)
                             if name.endswith(('.yaml', '.yml'))])
    else:
        # one csv row per entry (minus the header line)
        with open(path, 'r', encoding='utf-8', errors='replace') as sfile:
            entry['rows'] = max(sum(1 for line in sfile if line.strip())
                                - 1, 0)
    return entry


def _requirements() -> List[Tuple[str, str]]:
    """
    Get the requirements of the installed apero distribution

    :return: list of (name, specifier) - specifier may be ''
    """
    out: List[Tuple[str, str]] = []
    try:
        requires = importlib_metadata.requires('apero') or []
    except importlib_metadata.PackageNotFoundError:
        return out
    for requirement in requires:
        # skip optional extras ("; extra == 'dev'")
        if 'extra ==' in requirement:
            continue
        spec = requirement.split(';')[0].strip()
        match = re.match(r'^([A-Za-z0-9_.\-]+)\s*(.*)$', spec)
        if match:
            out.append((match.group(1), match.group(2).strip()))
    return out


def modules_section() -> Dict[str, Any]:
    """
    Describe python, APERO and every installed requirement

    :return: dict(python, apero, packages, checks)
    """
    checks: List[Dict[str, str]] = []
    python = dict(version=sys.version.split()[0],
                  executable=sys.executable,
                  conda_env=os.environ.get('CONDA_DEFAULT_ENV'),
                  virtual_env=os.environ.get('VIRTUAL_ENV'))
    # the apero / apero-core sources (and their git state)
    import apero
    import aperocore
    apero_info = dict()
    for name, module in [('apero', apero), ('aperocore', aperocore)]:
        source = os.path.dirname(os.path.abspath(module.__file__))
        apero_info[name] = dict(source=source,
                                version=getattr(module, '__version__',
                                                None) or _dist_version(name),
                                git=_git_state(source))
    # the installed version of every requirement
    try:
        from packaging.requirements import Requirement
    except ImportError:
        Requirement = None
    packages: List[Dict[str, Any]] = []
    names = [(name, '') for name in CORE_PACKAGES] + _requirements()
    seen = set()
    for name, spec in names:
        key = name.lower().replace('_', '-')
        if key in seen:
            continue
        seen.add(key)
        installed = _dist_version(name)
        entry = dict(name=name, required=spec or None, installed=installed)
        if installed is None:
            # optional core packages (apero_ri, lbl) may be missing
            level = 'info' if name in CORE_PACKAGES else 'bad'
            entry['status'] = 'missing'
            checks.append(_check(level, 'modules', name + ' is not '
                                 'installed'))
        elif spec and Requirement is not None:
            try:
                ok = Requirement(name + spec).specifier.contains(
                    installed, prereleases=True)
            except Exception as _:
                ok = True
            entry['status'] = 'ok' if ok else 'mismatch'
            if not ok:
                checks.append(_check('warn', 'modules', '{0} {1} installed '
                                     '(requires {2})'.format(name, installed,
                                                             spec)))
        else:
            entry['status'] = 'ok'
        packages.append(entry)
    return dict(python=python, apero=apero_info, packages=packages,
                checks=checks)


def _dist_version(name: str) -> Optional[str]:
    """
    Get the installed version of a distribution

    :param name: str, the distribution name

    :return: str or None, the version (None if not installed)
    """
    for candidate in [name, name.replace('_', '-'), name.replace('-', '_')]:
        try:
            return importlib_metadata.version(candidate)
        except importlib_metadata.PackageNotFoundError:
            continue
    return None


def machine_section() -> Dict[str, Any]:
    """
    Describe the machine (host, operating system, cpus, memory, load)

    :return: dict(values, checks)
    """
    checks: List[Dict[str, str]] = []
    values: Dict[str, Any] = dict(hostname=socket.gethostname(),
                                  user=getpass.getuser(),
                                  platform=platform.platform(),
                                  system=platform.system(),
                                  release=platform.release(),
                                  machine=platform.machine(),
                                  cpus=os.cpu_count())
    # load average (unix only)
    if hasattr(os, 'getloadavg'):
        values['load_average'] = [round(val, 2) for val in os.getloadavg()]
    # memory (psutil is an APERO requirement)
    try:
        import psutil
        memory = psutil.virtual_memory()
        values['memory_total'] = memory.total
        values['memory_available'] = memory.available
        values['cpus_physical'] = psutil.cpu_count(logical=False)
        if memory.total and memory.available / memory.total < 0.1:
            checks.append(_check('warn', 'machine', 'less than 10% of the '
                                 'memory is available'))
    except Exception as _:
        values['memory_total'] = None
    # the batch system (if any)
    values['slurm'] = shutil.which('sbatch') is not None
    return dict(values=values, checks=checks)


# =============================================================================
# Define main functions
# =============================================================================
def collect(params: Any, config_dir: Optional[str] = None
            ) -> Dict[str, Any]:
    """
    Collect the full state report of an activated APERO profile

    :param params: ParamDict, the parameters of the profile (load_config)
    :param config_dir: str or None, the DRS_UCONFIG directory (default:
                       the DRS_UCONFIG environment variable)

    :return: dict(meta, summary, checks, profile, config, paths, database,
             modules, machine) - json friendly
    """
    if config_dir is None:
        config_dir = os.environ.get(base.USER_ENV, '')
    config_dir = os.path.realpath(os.path.expanduser(str(config_dir)))
    import apero
    apero_version = str(getattr(apero, '__version__', '') or
                        _dist_version('apero'))
    report: Dict[str, Any] = dict(meta=dict(title='APERO state report',
                                            generated=_now(),
                                            report_version=REPORT_VERSION,
                                            apero_version=apero_version))
    # each section is collected on its own (errors never stop the report)
    sections = [('profile', lambda: profile_section(config_dir)),
                ('config', lambda: config_section(config_dir,
                                                  apero_version)),
                ('paths', lambda: paths_section(params)),
                ('database', lambda: database_section(params)),
                ('modules', modules_section),
                ('machine', machine_section)]
    checks: List[Dict[str, str]] = []
    for name, func in sections:
        try:
            section = func()
        except Exception as error:
            section = dict(error='{0}: {1}'.format(type(error).__name__,
                                                   error))
            section['checks'] = [_check('bad', name, 'could not collect '
                                        'this section: ' + section['error'])]
        checks += section.pop('checks', [])
        report[name] = _plain(section)
    report['checks'] = checks
    report['summary'] = summarise(checks)
    return report


def summarise(checks: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Summarise the checks (overall status and counts per level)

    :param checks: list of dict(level, section, message)

    :return: dict(status, counts)
    """
    counts = {level: 0 for level in LEVELS}
    for check in checks:
        counts[check['level']] = counts.get(check['level'], 0) + 1
    if counts['bad']:
        status = 'bad'
    elif counts['warn']:
        status = 'warn'
    else:
        status = 'ok'
    return dict(status=status, counts=counts)


def _lines(data: Any, indent: int = 0) -> List[str]:
    """
    Format a value as indented "key: value" lines

    :param data: Any, the value (dicts and lists are expanded)
    :param indent: int, the indentation level

    :return: list of str, the lines
    """
    pad = '  ' * indent
    out: List[str] = []
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)) and value:
                out.append('{0}{1}:'.format(pad, key))
                out += _lines(value, indent + 1)
            else:
                out.append('{0}{1}: {2}'.format(pad, key, _text(value)))
    elif isinstance(data, list):
        for value in data:
            if isinstance(value, dict):
                sub = _lines(value, indent + 1)
                # the first key starts the list item
                if sub:
                    out.append(pad + '- ' + sub[0].strip())
                    out += sub[1:]
            else:
                out.append('{0}- {1}'.format(pad, _text(value)))
    else:
        out.append(pad + _text(data))
    return out


def _text(value: Any) -> str:
    """
    Format a single value for the text report

    :param value: Any, the value

    :return: str, the value (None -> "None", empty containers -> "none")
    """
    if isinstance(value, (dict, list)) and not value:
        return 'none'
    return str(value)


def to_text(report: Dict[str, Any]) -> str:
    """
    Format a report (see collect) as one plain text document

    :param report: dict, the report

    :return: str, the text (ends with a new line)
    """
    meta = report.get('meta', dict())
    rule = '=' * 78
    out = [rule, 'APERO STATE REPORT', rule]
    out += _lines(meta)
    out.append('format: sections are "N. NAME"; one "key: value" per line; '
               'lists start with "- "')
    # the summary first: every problem in one place
    summary = report.get('summary', dict())
    out += ['', '0. SUMMARY', '-' * 78,
            'status: {0}'.format(summary.get('status', 'unknown'))]
    out += _lines(dict(counts=summary.get('counts', dict())))
    out.append('checks:')
    checks = sorted(report.get('checks', []),
                    key=lambda chk: -LEVELS.index(chk['level']))
    if not checks:
        out.append('  - [OK] no problems found')
    for check in checks:
        out.append('  - [{0}] {1}: {2}'.format(check['level'].upper(),
                                              check['section'],
                                              check['message']))
    # every section in a fixed order
    names = [('profile', 'PROFILE'), ('config', 'CONFIG FILES (DRS_UCONFIG)'),
             ('paths', 'DATA PATHS'), ('database', 'DATABASE'),
             ('modules', 'PYTHON MODULES'), ('machine', 'MACHINE')]
    for it, (key, title) in enumerate(names):
        out += ['', '{0}. {1}'.format(it + 1, title), '-' * 78]
        section = report.get(key, dict())
        # one line per package (the full list is long)
        if key == 'modules':
            section = dict(section)
            section['packages'] = [_package_line(pkg) for pkg
                                   in section.get('packages', [])]
        # human friendly sizes next to the raw byte counts
        if key == 'paths':
            for fs in section.get('filesystems', []):
                fs['total_human'] = _bytes(fs.get('total'))
                fs['free_human'] = _bytes(fs.get('free'))
        if key == 'machine':
            values = section.get('values', dict())
            for mkey in ['memory_total', 'memory_available']:
                if values.get(mkey) is not None:
                    values[mkey + '_human'] = _bytes(values[mkey])
        out += _lines(section) or ['none']
    out += ['', rule, 'END OF REPORT', rule]
    return '\n'.join(out) + '\n'


def _package_line(package: Dict[str, Any]) -> str:
    """
    Format one package of the modules section as a single line

    :param package: dict(name, installed, required, status)

    :return: str, e.g. "numpy 2.3.3 (requires ==2.3.3) [ok]"
    """
    text = '{0} {1}'.format(package.get('name'),
                            package.get('installed') or 'not installed')
    if package.get('required'):
        text += ' (requires {0})'.format(package['required'])
    return text + ' [{0}]'.format(package.get('status', 'unknown'))


def default_report_path(config_dir: Optional[str] = None,
                        directory: Optional[str] = None) -> str:
    """
    Get the default file name of a report:
    {directory}/apero_report_{profile}_{YYYYmmdd_HHMMSS}.txt

    :param config_dir: str or None, the DRS_UCONFIG directory (default:
                       the DRS_UCONFIG environment variable)
    :param directory: str or None, the output directory (default: the
                      current working directory)

    :return: str, the report path
    """
    if config_dir is None:
        config_dir = os.environ.get(base.USER_ENV, 'apero')
    profile = os.path.basename(os.path.normpath(str(config_dir))) or 'apero'
    stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    name = 'apero_report_{0}_{1}.txt'.format(profile, stamp)
    return str(Path(directory or os.getcwd()).joinpath(name))


def write_report(report: Dict[str, Any], path: str) -> str:
    """
    Write a report as text

    :param report: dict, the report (see collect)
    :param path: str, the output file

    :return: str, the absolute path written
    """
    path = os.path.realpath(os.path.expanduser(path))
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as rfile:
        rfile.write(to_text(report))
    return path


# =============================================================================
# End of code
# =============================================================================
