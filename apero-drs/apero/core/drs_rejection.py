#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO rejection "database" (CSV-backed, no SQL)

Drop-in replacement for ``drs_database.RejectDatabase`` using a plain CSV
file instead of an SQL database.

CSV schema: IDENTIFIER, DATE_ADDED, PP, TEL, RV, USED, COMMENT

CSV location: os.path.join(params['PATH.ASSETS'], 'reject', 'reject.csv')

Import rules: only aperocore.* + python stdlib + numpy + pandas.
No imports from apero.* at module scope.  The interactive helper functions
(add_file_reject, update_from_obsdir) use deferred apero.* imports inside
their function bodies.

Created on 2026-04-25

@author: cook
"""
import glob
import os
import tempfile
import time
from typing import Any, Dict, Optional, Tuple, Union

import numpy as np
import pandas as pd

from aperocore.base import base
from aperocore.constants import param_functions
from aperocore.core import drs_log
from aperocore.core import drs_misc

# fcntl is POSIX-only; on Windows we silently fall back to lock-file polling
try:
    import fcntl as _fcntl
except ImportError:  # pragma: no cover - Windows fallback
    _fcntl = None

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'core.drs_rejection.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__
# get astropy time from aperocore base
Time = base.Time
# get ParamDict
ParamDict = param_functions.ParamDict
# get exceptions / warnings
AperoCodedException = drs_log.AperoCodedException
AperoCodedWarning = drs_log.AperoCodedWarning
# get display func
display_func = drs_misc.display_func
# get Logging function
WLOG = drs_log.wlog

# ---------------------------------------------------------------------------
# CSV layout constants
# ---------------------------------------------------------------------------
# ordered column list for the reject CSV
CSV_COLUMNS = ['IDENTIFIER', 'DATE_ADDED', 'PP', 'TEL', 'RV', 'USED',
               'COMMENT']
# unique key used to avoid duplicate rows for the same identifier
ID_COLUMN = 'IDENTIFIER'
# columns that should be stored as integers
INT_COLUMNS = ['PP', 'TEL', 'RV', 'USED']
# sub-directory under PATH.ASSETS that holds the reject CSV
REJECT_SUBDIR = 'reject'
# filename of the reject CSV
REJECT_CSV = 'reject.csv'
# sub-directory used for lock files
LOCK_SUBDIR = '.locks'
# ---------------------------------------------------------------------------
# Module-level caches keyed by the absolute CSV path.
# Shared by all RejectDatabase instances inside a process.
# ---------------------------------------------------------------------------
# {csv_path -> pd.DataFrame}
_DF_CACHE: Dict[str, pd.DataFrame] = dict()
# {csv_path -> float} - mtime when the cache was last populated
_MTIME_CACHE: Dict[str, float] = dict()


# =============================================================================
# Define classes
# =============================================================================
class _FileLock:
    """
    Cross-platform best-effort file lock.

    On POSIX uses ``fcntl.flock`` on a sidecar ``*.lock`` file.  On platforms
    without ``fcntl`` falls back to spinning on ``O_EXCL`` creation of a
    sentinel file.  Either way the lock is released on context exit.

    Copied verbatim from ``drs_astrometrics._FileLock`` so this module
    remains independent of apero-drs.
    """
    DEFAULT_TIMEOUT = 30.0
    SLEEP_INTERVAL = 0.05

    def __init__(self, lockpath: str,
                 timeout: float = DEFAULT_TIMEOUT) -> None:
        self.lockpath = lockpath
        self.timeout = timeout
        self._fh = None
        self._fallback = _fcntl is None

    def __enter__(self) -> '_FileLock':
        os.makedirs(os.path.dirname(self.lockpath), exist_ok=True)
        start = time.time()
        if not self._fallback:
            self._fh = open(self.lockpath, 'a+')
            while True:
                try:
                    _fcntl.flock(self._fh.fileno(),
                                 _fcntl.LOCK_EX | _fcntl.LOCK_NB)
                    return self
                except (BlockingIOError, OSError):
                    if (time.time() - start) > self.timeout:
                        self._fh.close()
                        emsg = 'Timeout acquiring lock {0}'.format(
                            self.lockpath)
                        raise AperoCodedException(None, message=emsg)
                    time.sleep(self.SLEEP_INTERVAL)
        # Fallback: O_EXCL spin-wait
        while True:
            try:
                fd = os.open(self.lockpath,
                             os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, str(os.getpid()).encode('utf-8'))
                self._fh = fd
                return self
            except FileExistsError:
                if (time.time() - start) > self.timeout:
                    emsg = 'Timeout acquiring lock {0}'.format(self.lockpath)
                    raise AperoCodedException(None, message=emsg)
                time.sleep(self.SLEEP_INTERVAL)

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if not self._fallback and self._fh is not None:
            try:
                _fcntl.flock(self._fh.fileno(), _fcntl.LOCK_UN)
            finally:
                self._fh.close()
                self._fh = None
            return
        if self._fallback and self._fh is not None:
            try:
                os.close(self._fh)
            finally:
                self._fh = None
                try:
                    os.remove(self.lockpath)
                except OSError:
                    pass


class RejectDatabase:
    """
    CSV-backed reject "database".

    Replaces ``drs_database.RejectDatabase`` with the same public API.
    All I/O goes through a single CSV file located at::

        os.path.join(params['PATH.ASSETS'], 'reject', 'reject.csv')

    Public methods: :meth:`load_db`, :meth:`get_entries`,
    :meth:`add_entries`, :meth:`remove_entries`.
    """
    classname = 'RejectDatabase'

    def __init__(self, params: ParamDict,
                 shortname: str = 'None',
                 pconst: Any = None) -> None:
        """
        Construct the reject database.

        :param params: ParamDict, the apero parameter dictionary.
        :param shortname: str or None, the calling recipe shortname.
        :param pconst: unused – kept for API parity with the SQL version.
        """
        self.params = params
        self.shortname = shortname or 'None'
        self.name = 'reject'
        self.kind = 'reject'
        # legacy compatibility attrs (callers may read these)
        self.pconst = pconst
        self.database = None
        # best-effort instrument name
        try:
            self.instrument = str(params['INSTRUMENT'])
        except Exception:
            self.instrument = 'None'
        # resolve the CSV path
        try:
            assets_root = str(params['PATH.ASSETS'])
        except Exception:
            assets_root = ''
        self.path = os.path.abspath(
            os.path.join(assets_root, REJECT_SUBDIR, REJECT_CSV)
        )
        # lock file directory lives beside the CSV
        self.lockdir = os.path.join(os.path.dirname(self.path), LOCK_SUBDIR)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def load_db(self) -> None:
        """Load / refresh the CSV into the module-level cache."""
        _ensure_loaded(self.path)

    def get_entries(self, columns: str = '*',
                    nentries: Optional[int] = None,
                    condition: Optional[str] = None,
                    ) -> Union[None, tuple, np.ndarray, pd.DataFrame]:
        """
        Query the in-memory DataFrame.

        Mirrors the call contract of the old SQL-backed ``RejectDatabase``:

        * ``nentries=1``   → single tuple (or scalar for 1 column) or None
        * single column    → ``np.ndarray``
        * multiple columns → ``pd.DataFrame``

        Always filters ``USED == 1`` and sorts newest first.

        :param columns: str, comma-separated column list or ``'*'`` for all
        :param nentries: int or None, maximum rows to return
        :param condition: str or None, pandas ``DataFrame.query`` expression
        :return: see above
        """
        if self.instrument == 'None':
            return None
        _ensure_loaded(self.path)
        df = _DF_CACHE.get(self.path, pd.DataFrame(columns=CSV_COLUMNS))
        # filter USED = 1
        if 'USED' in df.columns and len(df) > 0:
            df = df[df['USED'].astype(int) == 1].copy()
        # sort newest first (best-effort; DATE_ADDED is ISO string)
        if 'DATE_ADDED' in df.columns and len(df) > 0:
            try:
                df = df.sort_values('DATE_ADDED',
                                    ascending=False).reset_index(drop=True)
            except Exception:
                pass
        # apply optional pandas query
        if condition is not None and len(df) > 0:
            try:
                df = df.query(condition).reset_index(drop=True)
            except Exception:
                pass
        # resolve column names
        if columns.strip() == '*':
            colnames = list(df.columns)
        else:
            colnames = [c.strip() for c in columns.split(',')]
        # limit row count
        if isinstance(nentries, int):
            df = df.head(nentries)
        # --- nentries == 1: return tuple/scalar or None ---
        if nentries == 1:
            if len(df) == 0:
                return None
            row = df.iloc[0]
            if len(colnames) == 1:
                col = colnames[0]
                return row[col] if col in df.columns else None
            return tuple(row[c] if c in df.columns else None
                         for c in colnames)
        # --- single column: return np.ndarray ---
        if len(colnames) == 1:
            col = colnames[0]
            if col not in df.columns:
                return np.array([])
            return np.array(df[col])
        # --- multiple columns: return pd.DataFrame ---
        available = [c for c in colnames if c in df.columns]
        return df[available].reset_index(drop=True)

    def add_entries(self, identifier: Optional[str] = None,
                    pp_flag: Optional[int] = None,
                    tel_flag: Optional[int] = None,
                    rv_flag: Optional[int] = None,
                    used: Optional[int] = None,
                    comment: Optional[str] = None) -> None:
        """
        Append a row to the reject CSV (file-locked for concurrency safety).

        :param identifier: str, the observation identifier (odometer code)
        :param pp_flag: int (0/1), reject at preprocessing stage
        :param tel_flag: int (0/1), reject at telluric-correction stage
        :param rv_flag: int (0/1), reject at RV stage
        :param used: int (0/1), whether the entry is active (default 1)
        :param comment: str, human-readable reason for the rejection
        """
        clean_identifier = ''
        if identifier is not None:
            clean_identifier = str(identifier).strip()
        if clean_identifier == '':
            emsg = 'identifier cannot be empty when adding reject entries'
            raise AperoCodedException(self.params, message=emsg)
        lockpath = os.path.join(self.lockdir, 'reject.lock')
        with _FileLock(lockpath):
            df = _read_csv(self.path)
            if len(df) > 0 and ID_COLUMN in df.columns:
                id_mask = df[ID_COLUMN].astype(str) == clean_identifier
                df = df[~id_mask].reset_index(drop=True)
            new_row = pd.DataFrame([{
                ID_COLUMN: clean_identifier,
                'DATE_ADDED': Time.now().iso,
                'PP': int(pp_flag) if pp_flag is not None else 0,
                'TEL': int(tel_flag) if tel_flag is not None else 0,
                'RV': int(rv_flag) if rv_flag is not None else 0,
                'USED': int(used) if used is not None else 1,
                'COMMENT': str(comment) if comment is not None else '',
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            _write_csv(self.path, df)
        # invalidate cache so next load_db() picks up the fresh file
        _DF_CACHE.pop(self.path, None)
        _MTIME_CACHE.pop(self.path, None)

    def remove_entries(self, condition: str) -> None:
        """
        Remove rows matching a pandas ``DataFrame.eval`` expression.

        :param condition: str, boolean expression understood by
                          ``pd.DataFrame.eval`` e.g. ``'IDENTIFIER == "abc"'``
        """
        lockpath = os.path.join(self.lockdir, 'reject.lock')
        with _FileLock(lockpath):
            df = _read_csv(self.path)
            if len(df) == 0:
                return
            try:
                keep_mask = ~df.eval(condition)
                df = df[keep_mask].reset_index(drop=True)
            except Exception:
                return
            _write_csv(self.path, df)
        _DF_CACHE.pop(self.path, None)
        _MTIME_CACHE.pop(self.path, None)


# =============================================================================
# Interactive functions (deferred apero.* imports inside each function)
# =============================================================================
def add_file_reject(params: ParamDict, recipe: Any,
                    raw_identifier: str) -> None:
    """
    Interactively add an odometer identifier (or comma-separated list) to the
    CSV reject list.

    All ``apero.*`` imports are deferred to avoid circular-import issues
    (this module lives in ``apero.core`` and must not import from ``apero``
    at module scope).

    :param params: ParamDict, the apero parameter dictionary
    :param recipe: DrsRecipe instance, the calling recipe
    :param raw_identifier: str, one or more comma-separated odometer codes
    """
    # deferred imports – apero.* only inside this function
    from aperocore.constants import load_functions
    from apero.instruments import select
    from apero.io import drs_fits
    from apero.core import drs_astrometrics
    from apero.tools.module.setup import drs_installation
    from astropy.table import Table
    # -------------------------------------------------------------------------
    # recipe inputs
    test = params['INPUTS']['test']
    autofill = params['INPUTS']['autofill']
    rawdir = params['PATH.RAW']
    # load astrometric database (needed for header fixes)
    objdbm = drs_astrometrics.AstrometricDatabase(params, recipe.shortname)
    objdbm.load_db()
    # load pseudo-constants (for HEADER_FIXES)
    pconst = load_functions.load_pconfig(select.INSTRUMENTS)
    # -------------------------------------------------------------------------
    # scan raw directory for all FITS files
    WLOG(params, 'info', 'Generating list of raw files')
    all_files: Dict[str, str] = dict()
    for root, dirs, files in os.walk(rawdir, followlinks=True):
        for filename in files:
            filepath = os.path.join(root, filename)
            ident = os.path.basename(filename).split('.fits')[0]
            all_files[ident] = filepath
    # -------------------------------------------------------------------------
    # split and clean the input identifiers
    if ',' in raw_identifier:
        identifiers = raw_identifier.split(',')
    else:
        identifiers = [raw_identifier]
    for it, identifier in enumerate(identifiers):
        clean = os.path.basename(identifier)
        if clean.endswith('.fits'):
            clean = clean[:-len('.fits')]
        identifiers[it] = clean
    # -------------------------------------------------------------------------
    # load existing reject DB to detect duplicates
    rejectdbm = RejectDatabase(params, recipe.shortname)
    rejectdbm.load_db()
    existing_df = _DF_CACHE.get(rejectdbm.path,
                                pd.DataFrame(columns=CSV_COLUMNS))
    if len(existing_df) > 0:
        existing_ids = set(np.array(existing_df['IDENTIFIER']).astype(str))
    else:
        existing_ids = set()
    # -------------------------------------------------------------------------
    # gather per-identifier file metadata
    file_info: Dict[str, list] = {
        'ROW': [], 'IDENTIFIER': [], 'OBSDIR': [],
        'DPRTYPE': [], 'OBJNAME': [],
    }
    row = 0
    for identifier in identifiers:
        WLOG(params, '',
             '\tAnalysing files for identifier: {0}'.format(identifier))
        if identifier in existing_ids:
            mask = existing_df['IDENTIFIER'].astype(str) == identifier
            comment_val = str(existing_df.loc[mask, 'COMMENT'].iloc[0])
            msg = ('\tIdentifier {0} already in reject list '
                   'with comment: {1}')
            WLOG(params, '', msg.format(identifier, comment_val),
                 colour='magenta')
            continue
        if identifier in all_files:
            filepath = str(all_files[identifier])
            obsdir = filepath.split(rawdir)[-1].split(identifier)[0]
            obsdir = obsdir.strip(os.sep)
            header = drs_fits.read_header(params, filepath)
            header, _ = pconst.HEADER_FIXES(params, header, dict(),
                                            filepath, True, objdbm)
            dprtype = header[params['KW_DPRTYPE'][0]]
            objname = header[params['KW_OBJNAME'][0]]
        else:
            dprtype = '--'
            objname = '--'
            obsdir = 'NOT-ON-DISK'
        file_info['ROW'].append(row)
        file_info['IDENTIFIER'].append(identifier)
        file_info['OBSDIR'].append(obsdir)
        file_info['DPRTYPE'].append(dprtype)
        file_info['OBJNAME'].append(objname)
        row += 1
    # -------------------------------------------------------------------------
    # display summary table
    file_table = Table(file_info)
    file_table.pprint(max_lines=-1, max_width=-1)
    # -------------------------------------------------------------------------
    # ask user to confirm / remove rows
    question = 'Are all rows correct, please check carefully?'
    correct = drs_installation.ask(question, dtype='YN', default='Y')
    remove_row_ints = []
    while not correct:
        question = ('Enter the row numbers to remove (comma separated),'
                    ' leave blank for no rows to add')
        remove_rows_str = drs_installation.ask(question, dtype=str)
        remove_rows_list = remove_rows_str.split(',')
        if len(remove_rows_list) == 0:
            correct = True
            continue
        remove_row_ints = []
        has_warnings = False
        for _row in remove_rows_list:
            try:
                remove_row_ints.append(int(_row))
                if int(_row) not in file_table['ROW']:
                    WLOG(params, 'warning',
                         'Row number={0} not in table'.format(_row))
                    has_warnings = True
            except ValueError:
                WLOG(params, 'warning',
                     'Row number={0} must be an integer'.format(_row))
                has_warnings = True
        if has_warnings:
            continue
        else:
            correct = True
    remove_rows_arr = np.array(remove_row_ints).astype(int)
    file_table.remove_rows(remove_rows_arr)
    # -------------------------------------------------------------------------
    # get PP / TEL / RV flags and comment
    if autofill not in [None, 'None']:
        autofill_list = autofill.split(',')
        if len(autofill_list) != 4:
            emsg = 'Autofill must be in form PP,TEL,RV,COMMENT'
            raise AperoCodedException(params, message=emsg)
        pp_str, tel_str, rv_str, comment = autofill_list
        logic_values = []
        for val in [pp_str, tel_str, rv_str]:
            if str(val).upper() in ['1', 'TRUE', 'T']:
                logic_values.append(1)
            elif str(val).upper() in ['0', 'FALSE', 'F']:
                logic_values.append(0)
            else:
                emsg = '{0} must be True/T/1 or False/F/0'.format(val)
                raise AperoCodedException(params, message=emsg)
        pp, tel, rv = logic_values
    else:
        pp, tel, rv, comment = _ask_user_for_reject_info(params,
                                                         drs_installation)
    # -------------------------------------------------------------------------
    # write new entries to CSV
    if not test:
        for identifier in file_table['IDENTIFIER']:
            rejectdbm.add_entries(identifier=identifier,
                                  pp_flag=pp, tel_flag=tel, rv_flag=rv,
                                  used=1, comment=comment)
            WLOG(params, '',
                 'identifier={0} added to reject list'.format(identifier))
    else:
        for identifier in file_table['IDENTIFIER']:
            WLOG(params, '',
                 '[TEST] Would add identifier={0} to reject list'.format(
                     identifier))


def update_from_obsdir(params: ParamDict, recipe: Any,
                       obsdir: str) -> str:
    """
    Collect all non-science-DPRTYPE identifiers from an observation directory
    and return them as a comma-separated string for use as the ``identifier``
    input to :func:`add_file_reject`.

    :param params: ParamDict, the apero parameter dictionary
    :param recipe: DrsRecipe instance, the calling recipe
    :param obsdir: str, the observation directory name (relative to PATH.RAW)
    :return: str, comma-separated odometer identifiers, or ``'None'``
    """
    # guard against empty/null obsdir
    if obsdir in [None, 'None', '', 'Null']:
        return 'None'
    # deferred imports
    from aperocore.constants import load_functions
    from aperocore.base import base as _base
    from apero.instruments import select
    from apero.io import drs_fits
    from apero.core import drs_astrometrics
    TQDM = _base.tqdm_module()
    # -------------------------------------------------------------------------
    rawdir = params['PATH.RAW']
    if obsdir not in os.listdir(rawdir):
        emsg = 'Obsdir={0} not found in raw directory'
        raise AperoCodedException(params, message=emsg.format(obsdir))
    rawpath = os.path.join(rawdir, obsdir)
    # load astrometric database
    objdbm = drs_astrometrics.AstrometricDatabase(params, recipe.shortname)
    objdbm.load_db()
    pconst = load_functions.load_pconfig(select.INSTRUMENTS)
    # -------------------------------------------------------------------------
    files = glob.glob(os.path.join(rawpath, '*.fits'))
    if len(files) == 0:
        emsg = 'No files found in raw directory: {0}'
        raise AperoCodedException(params, message=emsg.format(rawpath))
    sci_dprtype = params['PP.OBJ_DPRTYPES']
    WLOG(params, '',
         'Analysing files in raw directory: {0}'.format(rawpath))
    valid_files = []
    for filename in TQDM(files):
        header = drs_fits.read_header(params, filename)
        header, _ = pconst.HEADER_FIXES(params, header, dict(),
                                        filename, True, objdbm)
        dprtype = header[params['KW_DPRTYPE'][0]]
        if dprtype not in sci_dprtype:
            valid_files.append(filename)
    # collect identifiers
    identifiers = []
    for filename in valid_files:
        identifier = os.path.basename(filename).split('.fits')[0]
        identifiers.append(identifier)
    WLOG(params, '',
         'Adding {0} identifiers from obsdir={1}'.format(
             len(identifiers), obsdir))
    return ','.join(identifiers)


# =============================================================================
# Private helpers
# =============================================================================
def _ask_user_for_reject_info(params: ParamDict,
                              drs_installation: Any,
                              ) -> Tuple[int, int, int, str]:
    """
    Interactively ask the user for PP/TEL/RV flags and a comment.

    :param params: ParamDict (passed to drs_installation.ask for logging)
    :param drs_installation: the drs_installation module (already imported by
                              the caller)
    :return: tuple (pp, tel, rv, comment)
    """
    _ = params  # unused but kept for API symmetry
    logic_values = []
    for stage in ('PP', 'TEL', 'RV'):
        msg = 'Reject identifier(s) at the {0} stage?'.format(stage)
        value = drs_installation.ask(msg, dtype='YN')
        logic_values.append(int(value))
    pp, tel, rv = logic_values
    comment = drs_installation.ask('Enter a comment to reject identifier(s)',
                                   dtype=str)
    return pp, tel, rv, comment


def _ensure_loaded(csv_path: str, force: bool = False) -> None:
    """
    Load or refresh the module-level DataFrame cache for *csv_path*.

    Uses a simple mtime-based invalidation strategy: if the file has not
    changed since the last load, the cached DataFrame is reused.

    :param csv_path: str, absolute path to the reject CSV
    :param force: bool, if True reload even if mtime is unchanged
    """
    if not os.path.isfile(csv_path):
        _DF_CACHE[csv_path] = pd.DataFrame(columns=CSV_COLUMNS)
        _MTIME_CACHE[csv_path] = -1.0
        return
    try:
        mtime = os.path.getmtime(csv_path)
    except OSError:
        mtime = -1.0
    if (not force
            and csv_path in _MTIME_CACHE
            and _MTIME_CACHE[csv_path] == mtime
            and csv_path in _DF_CACHE):
        return
    _DF_CACHE[csv_path] = _read_csv(csv_path)
    _MTIME_CACHE[csv_path] = mtime


def _read_csv(csv_path: str) -> pd.DataFrame:
    """
    Read the reject CSV and return a well-typed DataFrame.

    Returns an empty DataFrame (with the correct columns) if the file
    does not exist or is unreadable.

    :param csv_path: str, absolute path to the reject CSV
    :return: pd.DataFrame
    """
    if not os.path.isfile(csv_path):
        return pd.DataFrame(columns=CSV_COLUMNS)
    try:
        df = pd.read_csv(csv_path, dtype=str)
        # ensure all expected columns are present
        for col in CSV_COLUMNS:
            if col not in df.columns:
                df[col] = ''
        # coerce integer columns
        for col in INT_COLUMNS:
            values = pd.to_numeric(df[col], errors='coerce')
            df[col] = values.fillna(0).astype(int)
        # enforce uniqueness on identifier (keep most recent row)
        if ID_COLUMN in df.columns and len(df) > 0:
            id_series = df[ID_COLUMN].astype(str).str.strip()
            df[ID_COLUMN] = id_series
            mask = id_series != ''
            df = df[mask].reset_index(drop=True)
            df = df.drop_duplicates(subset=[ID_COLUMN], keep='last')
        return df[CSV_COLUMNS].reset_index(drop=True)
    except Exception:
        return pd.DataFrame(columns=CSV_COLUMNS)


def _write_csv(csv_path: str, df: pd.DataFrame) -> None:
    """
    Write *df* to *csv_path*, creating parent directories as needed.

    :param csv_path: str, absolute path for the output CSV
    :param df: pd.DataFrame, the reject table to write
    """
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    # enforce uniqueness before persisting to disk
    if ID_COLUMN in df.columns and len(df) > 0:
        id_series = df[ID_COLUMN].astype(str).str.strip()
        df[ID_COLUMN] = id_series
        mask = id_series != ''
        df = df[mask].reset_index(drop=True)
        df = df.drop_duplicates(subset=[ID_COLUMN], keep='last')
    df = df[CSV_COLUMNS]
    df.to_csv(csv_path, index=False)


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    tmp_assets = tempfile.mkdtemp(prefix='apero_reject_demo_')
    demo_params = dict()
    demo_params['INSTRUMENT'] = 'DEMO'
    demo_params['PATH.ASSETS'] = tmp_assets
    demo_db = RejectDatabase(demo_params, shortname='DEMO')
    demo_db.load_db()
    demo_db.add_entries(identifier='DEMO_0001', pp_flag=1,
                        tel_flag=0, rv_flag=1,
                        used=1, comment='minimum working example')
    demo_db.add_entries(identifier='DEMO_0001', pp_flag=1,
                        tel_flag=1, rv_flag=1,
                        used=1, comment='updated entry (same identifier)')
    print('CSV path:', demo_db.path)
    print(demo_db.get_entries('*'))

# =============================================================================
# End of code
# =============================================================================
