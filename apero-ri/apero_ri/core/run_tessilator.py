#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Wrapper around the *tessilator* package to generate TESS rotation-
period light-curves and plots for a single target.

Results (PNG per sector + CSV light-curve per sector) are written to a
cache directory so that subsequent requests can be served immediately.

Cache layout::

    cache/{INSTRUMENT}/tess/{safe_objname}/
        meta.json            -- sector list + timestamps
        sector_NNN.png       -- combined plot per sector
        sector_NNN_lc.csv    -- light-curve data per sector
"""
import base64
import io
import json
import logging
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# -----------------------------------------------------------------------
# TeeWriter – copy stdout to the real console AND a queue
# -----------------------------------------------------------------------


class _TeeWriter:
    """Write to a real stream *and* buffer everything.

    If *log_queue* is not ``None``, complete lines are
    also pushed to that ``queue.Queue`` so a streaming
    endpoint can relay them to the browser in real-time.
    """

    __slots__ = ('_real', '_q', '_buf', '_line')

    def __init__(self, real_stream, log_queue=None):
        self._real = real_stream
        self._q = log_queue
        self._buf = io.StringIO()
        self._line = ''

    # -- file-like interface -------------------------------------------

    def write(self, text):
        self._real.write(text)
        self._buf.write(text)
        if self._q is not None:
            self._line += text
            while '\n' in self._line:
                ln, self._line = (
                    self._line.split('\n', 1)
                )
                self._q.put(ln + '\n')
        return len(text)

    def flush(self):
        self._real.flush()
        if self._q is not None and self._line:
            self._q.put(self._line)
            self._line = ''

    # -- helpers -------------------------------------------------------

    def getvalue(self):
        return self._buf.getvalue()

__NAME__ = 'apero_ri.core.run_tessilator'

log = logging.getLogger(__NAME__)

# -----------------------------------------------------------------------
# Public high-level helpers
# -----------------------------------------------------------------------

def tess_cache_dir(
    cache_root: Path, instrument: str, objname: str
) -> Path:
    """Return the directory used to store TESS results."""
    from apero_ri.core.plot_cache import _safe_filename
    safe = _safe_filename(objname)
    return cache_root / instrument / 'tess' / safe


def get_tess_cached(
    cache_root: Path, instrument: str, objname: str
) -> Optional[Dict[str, Any]]:
    """Load cached TESS results and return an API-ready dict.

    Returns *None* on miss.
    """
    d = tess_cache_dir(cache_root, instrument, objname)
    meta_path = d / 'meta.json'
    if not meta_path.exists():
        return None
    try:
        with open(meta_path, 'r') as fh:
            meta = json.load(fh)
    except Exception:
        return None

    # Period results file (single ECSV for all sectors)
    periods_path = d / 'periods.ecsv'
    has_periods = periods_path.exists()

    sectors: List[Dict[str, Any]] = []
    for entry in meta.get('sectors', []):
        png_path = d / entry['png']
        if not png_path.exists():
            return None
        img_b64 = base64.b64encode(
            png_path.read_bytes()
        ).decode('ascii')
        sectors.append(dict(
            sector=entry['sector'],
            image=img_b64,
            has_csv=has_periods,
        ))

    if not sectors:
        return None

    # Collect list of downloadable data files
    data_files = []
    for fname in meta.get('data_files', []):
        if (d / fname).exists():
            data_files.append(fname)

    return dict(
        success=True,
        objname=meta.get('objname', objname),
        sectors=sectors,
        data_files=data_files,
        cached_at=meta.get('cached_at', ''),
        console_log=meta.get('console_log', ''),
    )


def get_tess_lc_csv_path(
    cache_root: Path, instrument: str,
    objname: str, sector: int
) -> Optional[Path]:
    """Return the path to a cached period ECSV, or *None*."""
    d = tess_cache_dir(cache_root, instrument, objname)
    p = d / 'periods.ecsv'
    if p.exists():
        return p
    return None


def get_tess_data_file_path(
    cache_root: Path, instrument: str,
    objname: str, filename: str,
) -> Optional[Path]:
    """Return path to a cached TESS data file, or *None*.

    Only serves files listed in ``meta.json['data_files']``
    to prevent arbitrary file access.
    """
    import os
    d = tess_cache_dir(cache_root, instrument, objname)
    meta_path = d / 'meta.json'
    if not meta_path.exists():
        return None
    try:
        with open(meta_path, 'r') as fh:
            meta = json.load(fh)
    except Exception:
        return None
    # only allow files explicitly listed in metadata
    allowed = set(meta.get('data_files', []))
    # also allow periods.ecsv
    allowed.add('periods.ecsv')
    # sanitise: basename only, no path traversal
    safe_name = os.path.basename(filename)
    if safe_name not in allowed:
        return None
    p = d / safe_name
    if p.exists():
        return p
    return None


# -----------------------------------------------------------------------
# Run tessilator
# -----------------------------------------------------------------------

def run_tessilator(
    objname: str,
    cache_root: Path,
    instrument: str,
    aliases: Optional[List[str]] = None,
    log_queue=None,
) -> Dict[str, Any]:
    """Run tessilator for *objname*, store results in cache dir.

    Parameters
    ----------
    objname : str
        Canonical APERO object name (e.g. ``GL436``).
    cache_root : str or Path
        Root of the ARI cache tree
        (e.g. ``~/.ari/cache``).
    instrument : str
        Instrument key (``SPIROU``, ``NIRPS_HA``, …).
    aliases : list of str, optional
        All known aliases for this object (pipe-separated
        ALIASES field from the object table, already split).
        Each is tried with SIMBAD in order until one
        succeeds.
    log_queue : queue.Queue, optional
        If supplied, complete lines of console output are
        pushed here in real-time (for SSE streaming).

    Returns
    -------
    dict
        ``{success, objname, sectors: [{sector, image,
        has_csv}], resolved_via}``
        or ``{success: False, error: ...}``.
    """
    names_to_try = _build_name_list(objname, aliases)

    work_dir = Path(
        tempfile.mkdtemp(prefix='tess_')
    )
    try:
        # Capture all console output produced by tessilator
        # and tee it to the real console at the same time.
        old_stdout, old_stderr = sys.stdout, sys.stderr
        tee = _TeeWriter(old_stdout, log_queue)
        sys.stdout = tee
        sys.stderr = tee
        try:
            result = _run_in_workdir(
                work_dir, names_to_try
            )
        finally:
            sys.stdout, sys.stderr = (
                old_stdout, old_stderr
            )
            tee.flush()
        console_log = tee.getvalue()
        result['console_log'] = console_log
        if not result['success']:
            return result
        _store_to_cache(
            work_dir, result,
            cache_root, instrument, objname,
        )
        return result
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


# -----------------------------------------------------------------------
# Internal helpers
# -----------------------------------------------------------------------

def _build_name_list(
    objname: str,
    aliases: Optional[List[str]] = None,
) -> List[str]:
    """Return ordered list of names to try with SIMBAD.

    Order:
      1. Canonical APERO object name (try first).
      2. Common mutations of the canonical name
         (underscores → spaces).
      3. Filtered aliases from the object table.

    Instrument-suffix aliases (ending in ``-HA``, ``-HE``,
    etc.) are excluded.  The list is capped at 10 entries
    to avoid excessive SIMBAD queries.
    """
    names: List[str] = []
    # 1. Canonical APERO name first
    names.append(objname)
    # 2. Common mutations
    cleaned = objname.replace('_', ' ')
    if cleaned != objname:
        names.append(cleaned)
    # 3. Filtered aliases (skip instrument-specific ones)
    if aliases:
        for a in aliases:
            a = a.strip()
            if not a:
                continue
            # Skip APERO instrument suffixes
            upper = a.upper()
            if upper.endswith(('-HA', '-HE')):
                continue
            names.append(a)
    # Deduplicate while preserving order, cap at 10
    return list(dict.fromkeys(names))[:10]


def _run_in_workdir(
    work_dir: Path,
    names_to_try: List[str],
) -> Dict[str, Any]:
    """Attempt to run tessilator in *work_dir*.

    Tries each name in *names_to_try* until one succeeds
    with SIMBAD resolution.

    Returns an API-ready dict with base64 images.
    """
    try:
        # Force a non-interactive backend so matplotlib
        # never touches tkinter.  Without this, running
        # tessilator in a background thread crashes the
        # process ("main thread is not in main loop").
        import matplotlib
        matplotlib.use('Agg')
        from tessilator import tessilator as tess_mod
    except ImportError:
        return dict(
            success=False,
            error='tessilator is not installed.',
        )

    # Save and restore working directory (tessilator writes
    # output relative to cwd).
    orig_cwd = os.getcwd()
    os.chdir(str(work_dir))
    try:
        return _try_names(work_dir, names_to_try, tess_mod)
    finally:
        os.chdir(orig_cwd)


def _patch_simbad_column_case():
    """Monkey-patch Simbad.query_objectids for tessilator.

    Newer astroquery returns lowercase ``'id'`` column but
    tessilator expects uppercase ``'ID'``.  Patch once.
    """
    from astroquery.simbad import Simbad

    if getattr(Simbad, '_tessilator_patched', False):
        return
    _orig = Simbad.query_objectids

    @staticmethod
    def _fixed(*args, **kwargs):
        res = _orig(*args, **kwargs)
        if res is not None and 'id' in res.colnames:
            res.rename_column('id', 'ID')
        return res

    Simbad.query_objectids = _fixed
    Simbad._tessilator_patched = True


def _resolve_target(
    name: str, work_dir: Path, tess_mod: Any
) -> Tuple[Any, str]:
    """Resolve *name* via SIMBAD through tessilator.

    Writes target name to a temporary CSV so that
    ``read_data`` invokes the 1-column SIMBAD pathway.

    Returns ``(t_targets, error_msg)``.  On success
    *error_msg* is empty.
    """
    import tempfile

    _patch_simbad_column_case()

    tmp = tempfile.NamedTemporaryFile(
        mode='w', suffix='.csv',
        dir=str(work_dir), delete=False,
    )
    try:
        tmp.write(f'{name}\n')
        tmp.close()
        t_targets = tess_mod.read_data(tmp.name)
    except Exception as exc:
        return None, str(exc)
    finally:
        if os.path.exists(tmp.name):
            os.unlink(tmp.name)

    if t_targets is None or len(t_targets) == 0:
        return None, f'No SIMBAD results for "{name}".'

    return t_targets, ''


def _try_names(
    work_dir: Path,
    names: List[str],
    tess_mod: Any,
) -> Dict[str, Any]:
    """Try each candidate name; return on first success."""
    errors: List[str] = []

    for name in names:
        t_targets, err = _resolve_target(
            name, work_dir, tess_mod
        )
        if err:
            log.info(
                'SIMBAD resolve failed for %r: %s',
                name, err,
            )
            errors.append(f'{name}: {err}')
            continue

        # Set up tessilator parameters manually to avoid
        # interactive prompts from setup_input_parameters().
        file_ref = 'ari_tess'
        con_file, period_file = (
            tess_mod.setup_filenames(file_ref)
        )

        # Ensure contamination columns exist (tessilator
        # expects them but read_data doesn't add them).
        if 'log_tot_bg' not in t_targets.colnames:
            t_targets.add_column(
                -999, name='log_tot_bg'
            )
            t_targets.add_column(
                -999, name='log_max_bg'
            )
            t_targets.add_column(
                0, name='num_tot_bg'
            )

        try:
            tess_mod.all_sources_cutout(
                t_targets,
                period_file,
                False,     # LC_con
                False,     # flux_con
                con_file,  # con_file
                True,      # make_plots
                choose_sec=None,
            )
        except Exception as exc:
            log.warning(
                'tessilator failed for %r: %s',
                name, exc, exc_info=True,
            )
            errors.append(f'{name}: {exc}')
            continue

        return _collect_results(work_dir, name)

    # All names exhausted — build a user-friendly message
    msg = (
        'Object not resolvable in SIMBAD. '
        'Tried: ' + ', '.join(names) + '.'
    )
    return dict(success=False, error=msg)


def _collect_results(
    work_dir: Path,
    resolved_name: str,
) -> Dict[str, Any]:
    """Scan *work_dir* for tessilator output files.

    tessilator writes PNG plots, ``.ecsv`` period tables,
    and per-sector light-curve CSVs directly in the working
    directory.  All CSV/ECSV products are preserved so they
    can be offered as downloads in the UI.
    """
    sectors: List[Dict[str, Any]] = []

    # Discover PNG plots (one combined plot per sector)
    png_files = sorted(work_dir.glob('*.png'))

    # Discover all CSV/ECSV data products
    ecsv_files = (
        list(work_dir.glob('*.ecsv'))
        + list(work_dir.glob('*.csv'))
    )
    # Identify the single periods file
    periods_file = None
    for ef in ecsv_files:
        if ef.name.startswith('periods_'):
            periods_file = ef
            break
    if periods_file is None and ecsv_files:
        periods_file = ecsv_files[0]

    # Collect all extra data files (light curves, etc.)
    extra_files: List[Path] = []
    for ef in ecsv_files:
        if ef == periods_file:
            continue
        extra_files.append(ef)

    # Parse sector number from PNG filenames.
    sector_pngs = _group_by_sector(png_files)

    all_sectors = sorted(sector_pngs.keys())

    if not all_sectors:
        # Fallback: treat every PNG as a separate sector
        for idx, p in enumerate(png_files):
            img_b64 = base64.b64encode(
                p.read_bytes()
            ).decode('ascii')
            sectors.append(dict(
                sector=idx + 1,
                image=img_b64,
                has_csv=periods_file is not None,
                _png_path=str(p),
            ))
        if not sectors:
            return dict(
                success=False,
                error='tessilator produced no output.',
            )
        return dict(
            success=True,
            objname=resolved_name,
            sectors=sectors,
            _periods_path=(
                str(periods_file)
                if periods_file else ''
            ),
            _extra_paths=[
                str(f) for f in extra_files
            ],
        )

    for sec in all_sectors:
        png_path = sector_pngs.get(sec)
        if png_path is None:
            continue
        img_b64 = base64.b64encode(
            png_path.read_bytes()
        ).decode('ascii')
        sectors.append(dict(
            sector=sec,
            image=img_b64,
            has_csv=periods_file is not None,
            _png_path=str(png_path),
        ))

    if not sectors:
        return dict(
            success=False,
            error='tessilator produced no output.',
        )

    return dict(
        success=True,
        objname=resolved_name,
        sectors=sectors,
        _periods_path=(
            str(periods_file)
            if periods_file else ''
        ),
        _extra_paths=[
            str(f) for f in extra_files
        ],
    )


def _group_by_sector(
    files: List[Path],
) -> Dict[int, Path]:
    """Extract sector numbers from filenames.

    Looks for patterns like ``_S04_``, ``_004_``,
    ``sector_004``, etc.
    """
    import re
    result: Dict[int, Path] = {}
    # Pattern: S followed by digits or just 2-3 digit sector
    pat = re.compile(r'[_\-]S?0*(\d{1,3})[_\-.]')
    for f in files:
        m = pat.search(f.stem)
        if m:
            sec = int(m.group(1))
            if sec not in result:
                result[sec] = f
    return result


def _store_to_cache(
    work_dir: Path,
    result: Dict[str, Any],
    cache_root: Path,
    instrument: str,
    objname: str,
) -> None:
    """Copy output files to the ARI cache directory."""
    d = tess_cache_dir(cache_root, instrument, objname)
    d.mkdir(parents=True, exist_ok=True)

    meta_sectors: List[Dict[str, str]] = []
    for entry in result.get('sectors', []):
        sec = entry['sector']
        png_name = f'sector_{sec:03d}.png'

        # Copy PNG
        src_png = entry.get('_png_path', '')
        if src_png and Path(src_png).exists():
            shutil.copy2(src_png, d / png_name)

        meta_sectors.append(dict(
            sector=sec,
            png=png_name,
        ))

    # Copy the single periods ECSV (shared across sectors)
    src_periods = result.get('_periods_path', '')
    if src_periods and Path(src_periods).exists():
        shutil.copy2(src_periods, d / 'periods.ecsv')

    # Copy all extra data files (light curves, etc.)
    # preserving their original filenames.
    data_files: List[str] = []
    for src in result.get('_extra_paths', []):
        src_path = Path(src)
        if src_path.exists():
            dest_name = src_path.name
            shutil.copy2(src_path, d / dest_name)
            data_files.append(dest_name)

    meta = dict(
        objname=objname,
        cached_at=datetime.now(
            timezone.utc
        ).isoformat(),
        sectors=meta_sectors,
        data_files=data_files,
        console_log=result.get('console_log', ''),
    )
    with open(d / 'meta.json', 'w') as fh:
        json.dump(meta, fh, indent=2)

    # Remove internal path keys from the result dict
    # so the API response does not leak server paths.
    result.pop('_periods_path', None)
    result.pop('_extra_paths', None)
    # Attach the list of downloadable data files
    result['data_files'] = data_files
    for entry in result.get('sectors', []):
        entry.pop('_png_path', None)
