#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Per-check debug recorder for APERO monitoring checks.

Every check run by the APERO check task is wrapped in a recorder that
captures the run environment, all inputs, every traced helper call (with
its arguments, return value and timing), explicit ``log`` lines written by
the check itself, and the final result. The recorded text is stored per
obsdir in ``<checks root>/_debug/<obsdir>.json.gz`` (one section per check)
and shown from the monitor portal "Debug log" button.

The recorder is always on but is designed to be cheap: when no recorder is
active every hook costs a single ``ContextVar`` lookup, values are
summarised and truncated, and per-file FITS header reads are counted rather
than logged one by one.

Created on 2026-11-18

@author: cook
"""
import contextvars
import functools
import getpass
import gzip
import inspect
import json
import os
import platform
import socket
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import numpy as np

# =============================================================================
# Define variables
# =============================================================================
# Sub-directory (under the checks root) holding the per-obsdir debug files.
#   A non-YAML suffix keeps these files out of the obsdir YAML scans.
DEBUG_DIRNAME = '_debug'
# Suffix of the per-obsdir debug files (gzip-compressed JSON: the text
#   logs compress roughly tenfold).
DEBUG_SUFFIX = '.json.gz'
# Maximum characters shown for one described value.
MAX_VALUE_CHARS = 4000
# Maximum list/array items shown before summarising.
MAX_LIST_ITEMS = 25
# Maximum unique values listed for a summarised array.
MAX_UNIQUE_VALUES = 40
# Hard cap on lines per check so a runaway loop cannot exhaust memory.
MAX_LINES = 20000
# Dict keys (upper-cased substrings) whose values are always redacted.
SECRET_MARKERS = ('PASSWORD', 'PASSWD', 'SECRET', 'TOKEN', 'API_KEY',
                  'PRIVATE')
# Argument names describing a full profile mapping (summarised, not dumped).
PROFILE_ARG_NAMES = ('aparams', 'profile', 'profile_data')
# Sentinel used when ``log`` is called without a value.
_NO_VALUE = object()
# The recorder active for the current thread/process context.
_ACTIVE = contextvars.ContextVar('apero_check_debug_recorder', default=None)
# Cached per-process environment lines (computed once).
_ENV_LINES: Optional[List[str]] = None
# Cached preset files keyed by (path, mtime) for drift comparisons.
_PRESET_CACHE: Dict[Any, Dict[str, Any]] = dict()
# Cached check-module source files keyed by check object id.
_MODULE_FILE_CACHE: Dict[int, str] = dict()


# =============================================================================
# Define classes
# =============================================================================
class CheckDebugRecorder:
    """Collect timestamped debug lines for one check on one obsdir."""

    def __init__(self, check_key: str, obs_dir: str) -> None:
        """Initialise an empty recorder.

        :param check_key: Registry key of the check being recorded.
        :param obs_dir: Observation directory being checked.
        :return: None.
        """
        # Identify what is being recorded.
        self.check_key = str(check_key)
        self.obs_dir = str(obs_dir)
        # Reference time for relative timestamps.
        self.start = time.perf_counter()
        # Recorded text lines.
        self.lines: List[str] = []
        # Current call-nesting depth (indents traced calls).
        self.depth = 0
        # Number of lines dropped once MAX_LINES was reached.
        self.dropped = 0
        # apero-checks sections read through the config helpers.
        self.sections_used: List[str] = []
        # Simple named counters (e.g. FITS header reads).
        self.counters: Dict[str, int] = dict()

    def elapsed_ms(self) -> float:
        """Return milliseconds since the recorder started.

        :return: Elapsed time in milliseconds.
        """
        return 1000.0 * (time.perf_counter() - self.start)

    def add(self, message: str, value: Any = _NO_VALUE) -> None:
        """Append one timestamped line (and optional described value).

        :param message: Text of the line.
        :param value: Optional value appended as ``message = <value>``.
        :return: None.
        """
        # Stop recording (but keep counting) once the cap is reached.
        if len(self.lines) >= MAX_LINES:
            self.dropped += 1
            return
        # Indent nested traced calls so the call tree is readable.
        prefix = f'[{self.elapsed_ms():10.2f} ms] ' + '  ' * self.depth
        text = str(message)
        if value is not _NO_VALUE:
            text += ' = ' + describe(value)
        # Indent continuation lines of multi-line values under the prefix.
        pad = '\n' + ' ' * len(prefix) + '    '
        self.lines.append(prefix + text.replace('\n', pad))

    def note_section(self, section: str) -> None:
        """Remember one apero-checks section read by this check.

        :param section: Section name under ``apero-checks``.
        :return: None.
        """
        name = str(section)
        if name not in self.sections_used:
            self.sections_used.append(name)

    def count(self, name: str, amount: int = 1) -> None:
        """Increment one named counter.

        :param name: Counter name.
        :param amount: Increment.
        :return: None.
        """
        self.counters[name] = int(self.counters.get(name, 0)) + int(amount)

    def text(self) -> str:
        """Return the full recorded text.

        :return: Newline-joined debug text.
        """
        lines = list(self.lines)
        if self.dropped:
            lines.append(f'... {self.dropped} further line(s) dropped '
                         f'(MAX_LINES={MAX_LINES})')
        return '\n'.join(lines)


# =============================================================================
# Define functions
# =============================================================================
def start(check_key: str, obs_dir: str) -> Any:
    """Start recording one check and make the recorder active.

    :param check_key: Registry key of the check being recorded.
    :param obs_dir: Observation directory being checked.
    :return: Token to pass to ``stop``.
    """
    recorder = CheckDebugRecorder(check_key, obs_dir)
    return _ACTIVE.set(recorder)


def stop(token: Any) -> Optional[CheckDebugRecorder]:
    """Stop the active recorder and restore the previous one.

    :param token: Token returned by ``start``.
    :return: The recorder that was active.
    """
    recorder = _ACTIVE.get()
    _ACTIVE.reset(token)
    return recorder


def active() -> Optional[CheckDebugRecorder]:
    """Return the active recorder, if any.

    :return: Active recorder or None.
    """
    return _ACTIVE.get()


def log(message: str, value: Any = _NO_VALUE) -> None:
    """Write one line to the active recorder (no-op when inactive).

    :param message: Text of the line.
    :param value: Optional value appended as ``message = <value>``.
    :return: None.
    """
    recorder = _ACTIVE.get()
    if recorder is not None:
        recorder.add(message, value)


def section(title: str) -> None:
    """Write a section heading to the active recorder.

    :param title: Heading text.
    :return: None.
    """
    recorder = _ACTIVE.get()
    if recorder is not None:
        recorder.add('')
        recorder.add(f'---- {title} ' + '-' * max(0, 60 - len(title)))


def count(name: str, amount: int = 1) -> None:
    """Increment one counter on the active recorder (no-op when inactive).

    :param name: Counter name.
    :param amount: Increment.
    :return: None.
    """
    recorder = _ACTIVE.get()
    if recorder is not None:
        recorder.count(name, amount)


def traced(func: Optional[Callable] = None, *,
           log_result: bool = True) -> Callable:
    """Decorate a helper so its calls are recorded when a recorder is active.

    Records the call with its bound arguments, nests any traced calls made
    inside it, then records the return value (or raised exception) and the
    duration. When no recorder is active the wrapped function is called
    directly.

    :param func: Function to wrap (when used without arguments).
    :param log_result: If False only record that the call returned.
    :return: Wrapped function (or decorator when ``func`` is None).
    """
    def decorator(inner: Callable) -> Callable:
        """Wrap one function with call tracing.

        :param inner: Function to wrap.
        :return: Wrapped function.
        """
        # Resolve the signature once so arguments can be named cheaply.
        try:
            signature = inspect.signature(inner)
        except (TypeError, ValueError):
            signature = None
        name = inner.__name__

        @functools.wraps(inner)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            """Call the wrapped function, recording it when active."""
            recorder = _ACTIVE.get()
            # Fast path: nothing is recording.
            if recorder is None:
                return inner(*args, **kwargs)
            # Describe the arguments by name.
            arg_text = _describe_arguments(signature, args, kwargs)
            # Remember which apero-checks sections are read.
            _note_sections(recorder, name, signature, args, kwargs)
            recorder.add(f'-> {name}({arg_text})')
            recorder.depth += 1
            start_time = time.perf_counter()
            try:
                result = inner(*args, **kwargs)
            except Exception as exc:
                recorder.depth -= 1
                recorder.add(f'x  {name} raised {type(exc).__name__}: {exc}')
                raise
            duration = 1000.0 * (time.perf_counter() - start_time)
            recorder.depth -= 1
            if log_result:
                recorder.add(f'<- {name} [{duration:.2f} ms] returned',
                             result)
            else:
                recorder.add(f'<- {name} [{duration:.2f} ms] returned')
            return result

        return wrapper

    if func is not None:
        return decorator(func)
    return decorator


def describe(value: Any, name: str = '') -> str:
    """Return a bounded, secret-redacted description of one value.

    :param value: Value to describe.
    :param name: Optional argument/key name (used to spot profiles).
    :return: Description text (truncated to MAX_VALUE_CHARS).
    """
    try:
        text = _describe(value, name)
    except Exception as exc:
        text = f'<undescribable {type(value).__name__}: {exc}>'
    if len(text) > MAX_VALUE_CHARS:
        extra = len(text) - MAX_VALUE_CHARS
        text = text[:MAX_VALUE_CHARS] + f' ...<{extra} more chars>'
    return text


def environment_lines() -> List[str]:
    """Return cached lines describing the running process and package.

    :return: Environment description lines.
    """
    global _ENV_LINES
    if _ENV_LINES is not None:
        return list(_ENV_LINES)
    lines = []
    # Package version and location.
    try:
        from apero_ri import _version
        version = str(getattr(_version, '__version__', 'unknown'))
        vdate = str(getattr(_version, '__date__', 'unknown'))
    except Exception:
        version, vdate = 'unknown', 'unknown'
    package_dir = Path(__file__).resolve().parents[2]
    lines.append(f'apero_ri version: {version} (version date {vdate})')
    lines.append(f'apero_ri package: {package_dir}')
    lines.append(f'apero_ri git: {_git_description(package_dir)}')
    # Process and host.
    lines.append(f'host: {socket.gethostname()}  pid: {os.getpid()}  '
                 f'user: {_safe_user()}')
    lines.append(f'python: {platform.python_version()} ({sys.executable})')
    # Key library versions.
    lines.append(f'numpy: {np.__version__}  astropy: {_astropy_version()}')
    _ENV_LINES = lines
    return list(lines)


def file_info(path: Any) -> str:
    """Return ``path (modified <time>, <size> bytes)`` or a missing note.

    :param path: File path.
    :return: Description text.
    """
    try:
        filename = Path(str(path))
        stat = filename.stat()
    except Exception:
        return f'{path} (not found)'
    modified = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
    mtext = modified.isoformat(timespec='seconds')
    return f'{filename} (modified {mtext}, {stat.st_size} bytes)'


def preset_path(preset_name: str) -> Optional[Path]:
    """Return the packaged aprofile_instruments path for one preset.

    :param preset_name: Preset filename (e.g. ``nirps_he_v8.yaml``).
    :return: Path, or None when no preset name is given.
    """
    name = Path(str(preset_name or '')).name
    if not name:
        return None
    package_dir = Path(__file__).resolve().parents[2]
    return package_dir / 'resources' / 'aprofile_instruments' / name


def load_preset_from_disk(path: Optional[Path]) -> Dict[str, Any]:
    """Load one preset file, cached by (path, modification time).

    :param path: Preset file path.
    :return: Parsed preset mapping (empty when unavailable).
    """
    import yaml

    if path is None:
        return dict()
    try:
        key = (str(path), path.stat().st_mtime)
    except OSError:
        return dict()
    if key not in _PRESET_CACHE:
        try:
            with open(path, 'r', encoding='utf-8') as handle:
                data = yaml.safe_load(handle) or dict()
        except Exception:
            data = dict()
        _PRESET_CACHE[key] = data if isinstance(data, dict) else dict()
    return _PRESET_CACHE[key]


def log_check_context(template: Any, check_key: str, instrument: str,
                      aparams: Dict[str, Any], dbparams: Dict[str, Any],
                      row: Dict[str, Any],
                      check_dict: Dict[str, Any]) -> None:
    """Record the environment and every input of one check run.

    :param template: Registered ``AperoCheck`` (used to find its module).
    :param check_key: Registry key of the check.
    :param instrument: Instrument name passed to the check.
    :param aparams: Hydrated APERO profile passed to the check.
    :param dbparams: Database parameters passed to the check.
    :param row: Obsdir row (name, first/last file) for this run.
    :param check_dict: Dependency states passed to the check.
    :return: None.
    """
    if _ACTIVE.get() is None:
        return
    section('Environment')
    for line in environment_lines():
        log(line)
    log('run started (UTC)', datetime.now(timezone.utc).isoformat(
        timespec='seconds'))
    # Describe the check definition and where its code lives.
    section('Check definition')
    log('check key', check_key)
    log('check name', getattr(template, 'string_name', ''))
    log('check type', getattr(template, 'check_type', ''))
    log('valid instruments', list(getattr(template, 'instruments', [])))
    log('dependencies', list(getattr(template, 'dependencies', [])))
    log('check module file', file_info(_check_module_file(template)))
    log('simple check', getattr(template, 'simple_check', None) is not None)
    # Describe the profile and where its configuration comes from.
    section('Profile and inputs')
    preset_name = str(aparams.get('APERO_INSTRUMENT_PROFILE', '') or '')
    log('instrument argument', instrument)
    log('obs_dir argument', row.get('obs_dir', ''))
    log('APERO profile', aparams.get('apero_profile', ''))
    log('APERO_INSTRUMENT_PROFILE (preset)', preset_name)
    log('preset file on disk', file_info(preset_path(preset_name))
        if preset_name else '(no preset referenced by this profile)')
    log('profile carries preset copy (APERO_INSTRUMENT_PROFILE_DATA)',
        isinstance(aparams.get('APERO_INSTRUMENT_PROFILE_DATA'), dict))
    log('profile general', aparams.get('general', {}))
    log('profile paths', aparams.get('paths', {}))
    log('apero-checks sections in profile',
        sorted(dict(aparams.get('apero-checks', {}) or {})))
    log('obsdir row', row)
    log('dependency states (check_dict)', check_dict)
    log('database parameters', dbparams)


def log_config_drift(aparams: Dict[str, Any]) -> None:
    """Compare config sections read by the check against the preset.

    For each ``apero-checks`` section the check read, compare the value
    actually used (from the hydrated profile) against (a) the preset copy
    loaded by this server process and (b) the preset file currently on
    disk, and explain any mismatch.

    :param aparams: Hydrated APERO profile passed to the check.
    :return: None.
    """
    recorder = _ACTIVE.get()
    if recorder is None:
        return
    section('Configuration source check')
    sections = list(recorder.sections_used)
    log('apero-checks sections read by this check', sections)
    if not sections:
        return
    preset_name = str(aparams.get('APERO_INSTRUMENT_PROFILE', '') or '')
    if not preset_name:
        log('no APERO_INSTRUMENT_PROFILE in this profile: cannot compare '
            'against a preset file')
    # Config actually used by the check.
    used_cfg = dict(aparams.get('apero-checks', {}) or {})
    # Preset copy loaded by this process when the profile was hydrated.
    hydrated = aparams.get('APERO_INSTRUMENT_PROFILE_DATA')
    has_hydrated = isinstance(hydrated, dict)
    hydrated_cfg = dict((hydrated or {}).get('apero-checks', {}) or {})
    # Preset file as it is on disk right now.
    disk_path = preset_path(preset_name)
    disk_cfg = dict(load_preset_from_disk(disk_path).get('apero-checks',
                                                          {}) or {})
    missing = '<missing>'
    for name in sections:
        used = used_cfg.get(name, missing)
        on_disk = disk_cfg.get(name, missing)
        if not preset_name:
            log(f'[{name}] value used', used)
            continue
        if used == on_disk:
            log(f'[{name}] OK: value used matches preset file on disk')
            continue
        log(f'[{name}] MISMATCH: value used differs from preset file '
            f'{disk_path}')
        log(f'[{name}] value used by the check', used)
        log(f'[{name}] value in preset file on disk', on_disk)
        if has_hydrated:
            in_memory = hydrated_cfg.get(name, missing)
            log(f'[{name}] value in preset copy loaded by this process',
                in_memory)
            if in_memory != on_disk:
                log(f'[{name}] DIAGNOSIS: this server process loaded an '
                    'older copy of the preset file (cached at startup); '
                    'restart the ARI server and its workers')
            elif used != in_memory:
                log(f'[{name}] DIAGNOSIS: the saved profile overrides the '
                    'preset (apero-checks.' + name + ' stored in '
                    'apero_profiles.yaml); remove it from the saved '
                    'profile')
        else:
            log(f'[{name}] DIAGNOSIS: profile value differs from the '
                'preset file (saved profile override or out-of-date '
                'installed package)')


def log_result(check_obj: Any, duration_s: float) -> None:
    """Record the final state of one check run.

    :param check_obj: The ``AperoCheck`` instance after running.
    :param duration_s: Run duration in seconds.
    :return: None.
    """
    recorder = _ACTIVE.get()
    if recorder is None:
        return
    section('Result')
    log('passed', bool(getattr(check_obj, 'passed', False)))
    log('wrong instrument (skipped)',
        bool(getattr(check_obj, 'wrong_instrument', False)))
    log('duration (s)', round(float(duration_s), 4))
    log('counters', dict(recorder.counters))
    log('message', str(getattr(check_obj, 'message', '') or ''))


def debug_filename(root_dir: Path, obs_dir: str) -> Path:
    """Return the per-obsdir debug file path under one checks root.

    :param root_dir: APERO checks output root.
    :param obs_dir: Observation directory name.
    :return: Debug file path (gzip-compressed JSON).
    """
    return Path(root_dir) / DEBUG_DIRNAME / f'{obs_dir}{DEBUG_SUFFIX}'


def load_obsdir_debug(path: Path) -> Dict[str, Any]:
    """Load one per-obsdir debug file.

    :param path: Debug file path (gzip-compressed JSON).
    :return: Parsed mapping (empty when missing or unreadable).
    """
    try:
        with gzip.open(path, 'rt', encoding='utf-8') as handle:
            data = json.load(handle)
    except Exception:
        return dict()
    return data if isinstance(data, dict) else dict()


def write_obsdir_debug(root_dir: Path, obs_dir: str, profile: str,
                       check_logs: Dict[str, Dict[str, Any]]) -> Path:
    """Merge new check logs into the per-obsdir debug file atomically.

    Logs of checks not re-run this time are kept, so re-running one check
    only replaces that check's section.

    :param root_dir: APERO checks output root.
    :param obs_dir: Observation directory name.
    :param profile: APERO profile name.
    :param check_logs: Mapping of check key to its log entry.
    :return: Written debug file path.
    """
    filename = debug_filename(root_dir, obs_dir)
    filename.parent.mkdir(parents=True, exist_ok=True)
    # Keep sections from earlier runs of other checks.
    data = load_obsdir_debug(filename)
    checks = dict(data.get('checks', {}) or {})
    for check_key, entry in check_logs.items():
        # Pop first so re-run checks move to the end (latest run order).
        checks.pop(check_key, None)
        checks[check_key] = dict(entry)
    payload = dict(obsdir=str(obs_dir), profile=str(profile),
                   updated=datetime.now(timezone.utc).isoformat(
                       timespec='seconds'),
                   checks=checks)
    # Write to a temporary file first so readers never see partial data.
    tmpname = filename.with_name(filename.name + '.tmp')
    with gzip.open(tmpname, 'wt', encoding='utf-8',
                   compresslevel=5) as handle:
        json.dump(payload, handle)
    tmpname.replace(filename)
    return filename


def format_obsdir_debug(data: Dict[str, Any],
                        check_key: str = '') -> str:
    """Render a debug file as text (all checks, or one check).

    :param data: Parsed debug file mapping.
    :param check_key: When given, only render this check's section.
    :return: Display text.
    """
    checks = dict(data.get('checks', {}) or {})
    keys = [check_key] if check_key else list(checks)
    lines = ['=' * 78,
             f'APERO check debug log: obsdir={data.get("obsdir", "")} '
             f'profile={data.get("profile", "")}',
             f'debug file last updated: {data.get("updated", "")}',
             f'checks in this view: {len(keys)}',
             '=' * 78]
    for key in keys:
        entry = checks.get(key)
        lines.append('')
        lines.append('#' * 78)
        if not isinstance(entry, dict):
            lines.append(f'# {key}: no debug log recorded for this check '
                         'yet (re-run it to create one)')
            lines.append('#' * 78)
            continue
        status = 'PASSED' if entry.get('passed') else 'FAILED'
        lines.append(f'# {key}: {status}  run at {entry.get("run_at", "")}'
                     f'  ({float(entry.get("duration_s", 0.0)):.3f} s)')
        lines.append('#' * 78)
        lines.append(str(entry.get('text', '')))
    return '\n'.join(lines)


# =============================================================================
# Define worker functions
# =============================================================================
def _describe(value: Any, name: str, indent: int = 0) -> str:
    """Describe one value recursively without bounds checking.

    Containers are described item by item so the list/array summaries
    apply at every nesting level (a short tuple holding a long file list
    is still summarised).

    :param value: Value to describe.
    :param name: Optional argument/key name (used to spot profiles).
    :param indent: Nesting level (for multi-line layout).
    :return: Description text.
    """
    # Summarise full profile mappings instead of dumping them.
    if isinstance(value, dict) and name in PROFILE_ARG_NAMES:
        profile = value.get('apero_profile', '?')
        preset = value.get('APERO_INSTRUMENT_PROFILE', '?')
        return (f'<profile {profile!r} preset={preset!r} '
                f'({len(value)} top-level keys)>')
    # Scalars and paths.
    if value is None or isinstance(value, (bool, int, float, np.generic)):
        return repr(value)
    if isinstance(value, str):
        # Show top-level multi-line text (reports, tracebacks) as a block.
        if '\n' in value and indent == 0:
            return '"""\n' + value + '\n"""'
        return repr(value)
    if isinstance(value, Path):
        return repr(str(value))
    # Numpy arrays: shape, dtype and a value summary.
    if isinstance(value, np.ndarray):
        return _describe_array(value)
    # FITS headers: count cards only.
    if type(value).__name__ == 'Header':
        return f'<FITS Header with {len(value)} cards>'
    # Mappings: describe each value, hiding secrets.
    if isinstance(value, dict):
        items = []
        for key, item in value.items():
            if _is_secret_key(key) and item not in (None, ''):
                shown = "'<redacted>'"
            else:
                shown = _describe(item, str(key), indent + 1)
            items.append(f'{key!r}: {shown}')
        return _layout('{', items, '}', indent)
    # Sets: describe sorted items.
    if isinstance(value, (set, frozenset)):
        return _describe_sequence(sorted(value, key=str), indent, '{', '}')
    # Lists/tuples: show everything when short, otherwise head and tail.
    if isinstance(value, tuple):
        return _describe_sequence(list(value), indent, '(', ')')
    if isinstance(value, list):
        return _describe_sequence(value, indent, '[', ']')
    return repr(value)


def _describe_sequence(items: List[Any], indent: int,
                       open_char: str, close_char: str) -> str:
    """Describe a sequence, summarising long ones and file lists.

    :param items: Sequence items.
    :param indent: Nesting level.
    :param open_char: Opening bracket.
    :param close_char: Closing bracket.
    :return: Description text.
    """
    count = len(items)
    prefix = ''
    # Lists of files in one folder: show the folder once, then names.
    if count > 1 and all(isinstance(item, Path) for item in items):
        parents = {str(item.parent) for item in items}
        if len(parents) == 1:
            prefix = f'<{count} files in {parents.pop()}> '
            items = [item.name for item in items]
    # Long sequences: keep the first 10 and last 3 items.
    if count > MAX_LIST_ITEMS:
        prefix = prefix or f'<{count} items> '
        shown = [_describe(item, '', indent + 1) for item in items[:10]]
        shown.append(f'... {count - 13} more ...')
        shown += [_describe(item, '', indent + 1) for item in items[-3:]]
    else:
        shown = [_describe(item, '', indent + 1) for item in items]
    return prefix + _layout(open_char, shown, close_char, indent)


def _layout(open_char: str, items: List[str], close_char: str,
            indent: int) -> str:
    """Join described items on one line, or one per line when long.

    :param open_char: Opening bracket.
    :param items: Described items.
    :param close_char: Closing bracket.
    :param indent: Nesting level.
    :return: Joined text.
    """
    one_line = open_char + ', '.join(items) + close_char
    if len(one_line) + 2 * indent <= 76 and '\n' not in one_line:
        return one_line
    pad = '  ' * (indent + 1)
    # Short items (file names, numbers): fill several per line.
    if items and all(len(item) <= 30 and '\n' not in item
                     for item in items):
        rows, current = [], ''
        for item in items:
            candidate = item if not current else current + ', ' + item
            if current and len(pad) + len(candidate) > 76:
                rows.append(current + ',')
                candidate = item
            current = candidate
        rows.append(current)
        body = '\n'.join(pad + row for row in rows)
    else:
        body = ',\n'.join(pad + item for item in items)
    return open_char + '\n' + body + '\n' + '  ' * indent + close_char


def _describe_array(value: np.ndarray) -> str:
    """Describe a numpy array with a value summary.

    :param value: Numpy array.
    :return: Description text.
    """
    head = f'ndarray(shape={value.shape}, dtype={value.dtype})'
    if value.size <= MAX_LIST_ITEMS:
        return head + ' ' + repr(value.tolist())
    # Summarise categorical arrays by their unique values and counts.
    if value.dtype.kind in 'USOb':
        uniques, counts = np.unique(value.astype(str), return_counts=True)
        pairs = [f'{u!r}: {c}' for u, c in zip(uniques, counts)]
        if len(pairs) > MAX_UNIQUE_VALUES:
            more = len(pairs) - MAX_UNIQUE_VALUES
            pairs = pairs[:MAX_UNIQUE_VALUES] + [f'... {more} more']
        return head + ' unique counts {' + ', '.join(pairs) + '}'
    # Summarise numeric arrays by simple statistics.
    if value.dtype.kind in 'iuf':
        # Only float arrays can hold non-finite values.
        if value.dtype.kind == 'f':
            finite = value[np.isfinite(value)]
        else:
            finite = value
        if finite.size == 0:
            return head + ' (no finite values)'
        return (head + f' min={finite.min()!r} max={finite.max()!r} '
                f'n_finite={finite.size}')
    return head


def _describe_arguments(signature: Optional[inspect.Signature],
                        args: tuple, kwargs: dict) -> str:
    """Describe call arguments by parameter name.

    :param signature: Signature of the called function (or None).
    :param args: Positional arguments.
    :param kwargs: Keyword arguments.
    :return: Comma-separated ``name=value`` text.
    """
    if signature is None:
        parts = [describe(arg) for arg in args]
        parts += [f'{key}={describe(val, key)}' for key, val in
                  kwargs.items()]
        return ', '.join(parts)
    try:
        bound = signature.bind_partial(*args, **kwargs)
    except TypeError:
        return describe(list(args)) + ', ' + describe(kwargs)
    parts = [f'{key}={describe(val, key)}'
             for key, val in bound.arguments.items()]
    return ', '.join(parts)


def _note_sections(recorder: CheckDebugRecorder, name: str,
                   signature: Optional[inspect.Signature],
                   args: tuple, kwargs: dict) -> None:
    """Record which apero-checks section a config helper reads.

    :param recorder: Active recorder.
    :param name: Called function name.
    :param signature: Signature of the called function.
    :param args: Positional arguments.
    :param kwargs: Keyword arguments.
    :return: None.
    """
    if name in ('get_common_value', 'get_header_key'):
        recorder.note_section('common')
        return
    if signature is None:
        return
    try:
        bound = signature.bind_partial(*args, **kwargs)
    except TypeError:
        return
    check_name = bound.arguments.get('check_name')
    if check_name is not None:
        recorder.note_section(str(check_name))


def _check_module_file(template: Any) -> str:
    """Return the source file defining one registered check.

    :param template: Registered ``AperoCheck`` instance.
    :return: Module file path or 'unknown'.
    """
    key = id(template)
    if key in _MODULE_FILE_CACHE:
        return _MODULE_FILE_CACHE[key]
    filename = 'unknown'
    for module in list(sys.modules.values()):
        if getattr(module, 'CHECK', None) is template:
            filename = str(getattr(module, '__file__', 'unknown'))
            break
    _MODULE_FILE_CACHE[key] = filename
    return filename


def _is_secret_key(key: Any) -> bool:
    """Return True when a mapping key names a secret value.

    :param key: Mapping key.
    :return: True when the value must be redacted.
    """
    text = str(key).upper()
    return any(marker in text for marker in SECRET_MARKERS)


def _git_description(package_dir: Path) -> str:
    """Return the git branch/commit of the checkout holding the package.

    Reads ``.git`` files directly (no subprocess) so it stays cheap.

    :param package_dir: apero_ri package directory.
    :return: ``branch@commit`` text or a not-a-checkout note.
    """
    for parent in [package_dir] + list(package_dir.parents):
        git_dir = parent / '.git'
        if not git_dir.exists():
            continue
        try:
            # Worktrees/submodules store a pointer file instead of a dir.
            if git_dir.is_file():
                pointer = git_dir.read_text().strip()
                git_dir = (parent / pointer.split(':', 1)[1].strip())
            head = (git_dir / 'HEAD').read_text().strip()
            if not head.startswith('ref:'):
                return f'detached@{head[:12]} ({parent})'
            ref = head.split(':', 1)[1].strip()
            ref_file = git_dir / ref
            if ref_file.exists():
                commit = ref_file.read_text().strip()
            else:
                commit = _packed_ref(git_dir, ref)
            branch = ref.rsplit('/', 1)[-1]
            return f'{branch}@{commit[:12]} ({parent})'
        except Exception as exc:
            return f'unreadable ({exc})'
    return 'not a git checkout (installed package)'


def _packed_ref(git_dir: Path, ref: str) -> str:
    """Look up a ref in ``packed-refs``.

    :param git_dir: Git directory.
    :param ref: Full ref name.
    :return: Commit hash or 'unknown'.
    """
    try:
        for line in (git_dir / 'packed-refs').read_text().splitlines():
            parts = line.strip().split(' ')
            if len(parts) == 2 and parts[1] == ref:
                return parts[0]
    except OSError:
        pass
    return 'unknown'


def _safe_user() -> str:
    """Return the current user name without raising.

    :return: User name or 'unknown'.
    """
    try:
        return getpass.getuser()
    except Exception:
        return 'unknown'


def _astropy_version() -> str:
    """Return the astropy version without raising.

    :return: Version text.
    """
    try:
        import astropy
        return str(astropy.__version__)
    except Exception:
        return 'unknown'


# =============================================================================
# End of code
# =============================================================================
