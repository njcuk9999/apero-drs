#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Read-only diagnostics for one explicitly authorized ARI profile."""

import hashlib
import re
import time
from pathlib import Path
from typing import Any, Callable

from aperocore.core import diagnostics as common
from apero_ri.base import base
from apero_ri.base.base import BLOCK_KIND
from apero_ri.ari_api import diagnostics as diagnostic_api
from apero_ri.core import apero_queues
from apero_ri.core import auth
from apero_ri.tasks import apero_async
from apero_ri.tasks import apero_sync

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.core.diagnostics'
__version__ = base.__version__
__date__ = base.__date__
__authors__ = base.__authors__
IDENTIFIER = re.compile(r'^[A-Za-z0-9_]+$')
OBJECT = re.compile(r'^[A-Za-z0-9_+ .-]{1,120}$')
# Cached Bokeh payloads embed full plot JSON, so allow larger files here
PLOT_CACHE_LIMIT = 64 * 1024 * 1024
# Maximum number of cached object-plot entries summarised per object
PLOT_CACHE_ENTRIES = 40
# Characters of each cached build traceback kept in the report
TRACEBACK_CHARS = 4000

# =============================================================================
# Define functions
# =============================================================================
def _table(profile: dict, kind: str) -> str:
    """Validate an administrator-configured SQL table identifier.

    :param profile: Hydrated profile configuration.
    :param kind: Fixed table category such as FINDEX or LOG.
    :return: Safely quoted table identifier.
    """
    name = profile.get('database', {}).get(kind + '_TABLENAME', '')
    if not IDENTIFIER.fullmatch(str(name)):
        raise ValueError('invalid_table_identifier')
    return '`' + name + '`'


def _query(profile: dict, query: str, bindings: dict) -> list[dict]:
    """Execute a collector-owned SELECT with bounded MySQL timeouts.

    :param profile: Hydrated profile containing database settings.
    :param query: Fixed SELECT statement with no client-provided SQL.
    :param bindings: Bound scalar filters.
    :return: At most 101 rows of diagnostic results.
    """
    from sqlalchemy import URL

    params = apero_async.get_db_params(profile)
    mode = str(params['DATABASE_MODE'])
    if mode != 'mysql+pymysql':
        raise ValueError('unsupported_diagnostic_database_driver')
    host, port = apero_async._resolve_database_endpoint(params)
    url_kwargs = dict(username=params['DATABASE_USER'],
                      password=params.get('DATABASE_PASSWORD', ''),
                      host=host, port=int(port),
                      database=params['DATABASE_NAME'])
    url = URL.create(mode, **url_kwargs)
    return common.database_rows(url, query, bindings)


def _database(profile: dict, objname: str, pid: str) -> dict[str, Any]:
    """Collect schemas, grouped products, and recent LogDatabase records.

    :param profile: Hydrated configuration for the authorized profile.
    :param objname: Optional exact object name.
    :param pid: Optional exact recipe process identifier.
    :return: Independent query results with errors recorded per check.
    """
    results = dict()
    for kind in ('FINDEX', 'LOG'):
        try:
            table = _table(profile, kind)
            query = ('SELECT COLUMN_NAME, DATA_TYPE FROM '
                     'information_schema.COLUMNS WHERE '
                     'TABLE_SCHEMA=DATABASE() AND TABLE_NAME=:table '
                     'LIMIT 100')
            results[kind + '_schema'] = _query(
                profile, query, dict(table=table.strip('`')))
        except Exception as error:
            results[kind + '_schema'] = dict(error=str(error))
    try:
        table = _table(profile, 'FINDEX')
        condition = ' WHERE KW_OBJNAME=:objname' if objname else ''
        query = ('SELECT BLOCK_KIND, KW_OUTPUT, KW_FIBER, KW_DPRTYPE, '
                 'COUNT(*) AS n_files, MAX(LAST_MODIFIED) AS last_modified, '
                 'SUM(KW_RUN_ID IS NULL OR KW_RUN_ID="") AS missing_run_id '
                 f'FROM {table}{condition} GROUP BY BLOCK_KIND, KW_OUTPUT, '
                 'KW_FIBER, KW_DPRTYPE LIMIT 100')
        results['product_counts'] = _query(profile, query,
                                           dict(objname=objname))
        if objname:
            query = ('SELECT FILENAME, OBS_DIR, BLOCK_KIND, KW_OUTPUT, '
                     'KW_FIBER, KW_RUN_ID, KW_PID, KW_DRS_QC '
                     f'FROM {table} WHERE KW_OBJNAME=:objname '
                     'ORDER BY LAST_MODIFIED DESC LIMIT 100')
            results['product_examples'] = _query(profile, query,
                                                 dict(objname=objname))
    except Exception as error:
        results['products_error'] = str(error)
    try:
        table = _table(profile, 'LOG')
        condition = ' WHERE PID=:pid' if pid else ''
        columns = ('PID, RECIPE, SHORTNAME, GROUPNAME, LEVEL, SUBLEVEL, '
                   'START_TIME, END_TIME, ENDED, PASSED_ALL_QC, ERRORMSGS, '
                   'LOGFILE, RAM_USAGE_START, RAM_USAGE_END, RAM_TOTAL, '
                   'CPU_USAGE_START, CPU_USAGE_END, CPU_NUM')
        query = (f'SELECT {columns} FROM {table}{condition} '
                 'ORDER BY UNIXTIME DESC LIMIT 100')
        results['recipe_logs'] = _query(profile, query, dict(pid=pid))
        results['resource_semantics'] = 'host_snapshots_not_process_peaks'
    except Exception as error:
        results['logs_error'] = str(error)
    results['row_limit'] = 100
    return results


def _cache(root: Path, objname: str) -> dict[str, Any]:
    """Inspect profile artifacts and bounded exact-object file tables.

    :param root: Authorized profile cache directory.
    :param objname: Optional exact object name, validated by the caller.
    :return: Cache inventories, table summaries, and query state.
    """
    result = dict(inventory=common.inventory(root))
    for name in ('object_table.json', 'obs_table.json',
                 '.object_query_state.json'):
        payload = common.read_json(root / name, root)
        data = payload.pop('data', None)
        if isinstance(data, dict):
            rows = data.get('rows', [])
            payload['metadata'] = {key: value for key, value in data.items()
                                   if key != 'rows'}
            payload['n_rows'] = len(rows)
            if objname:
                selected = [row for row in rows
                            if row.get('OBJNAME') == objname]
                payload['object_rows'] = selected[:100]
                payload['object_rows_truncated'] = len(selected) > 100
        result[name] = payload
    objects = root / 'objects'
    result['objects'] = common.inventory(objects)
    if objname:
        result['object_tables'] = dict()
        for kind in ('all', 'raw', 'pp', 'ext', 'tcorr', 'ccf', 'efits',
                     'tfits', 'lbl', 'lbl_rdb', 'headers'):
            name = (f'htable_{objname}.json' if kind == 'headers' else
                    f'ftable_{kind}_{objname}.json')
            payload = common.read_json(objects / name, root)
            data = payload.pop('data', None)
            if isinstance(data, dict):
                rows = data.get('rows', [])
                payload.update(n_rows=len(rows), rows=rows[:100],
                               rows_truncated=len(rows) > 100)
                payload['metadata'] = {key: value
                                       for key, value in data.items()
                                       if key != 'rows'}
            result['object_tables'][kind] = payload
    return result


def _plot_payload_summary(payload: Any) -> dict[str, Any]:
    """Summarise one cached object-plot response without its Bokeh blobs.

    :param payload: Cached ``api_object_plots`` JSON response.
    :return: Response status, timings, and per-plot build outcomes.
    """
    if not isinstance(payload, dict):
        return dict(invalid_payload_type=type(payload).__name__)
    # top-level response fields describing the whole request
    keys = ('success', 'error', 'plot_group', 'updated_at',
            'server_timings_ms', 'hr_backdrop_ready',
            'hr_backdrop_expected')
    summary = {key: payload[key] for key in keys if key in payload}
    summary['plots'] = dict()
    for name, value in payload.items():
        # individual plots are dicts carrying a has_plot flag
        if not isinstance(value, dict) or 'has_plot' not in value:
            continue
        plot = dict(has_plot=value.get('has_plot'),
                    message=value.get('message'),
                    error=value.get('error'),
                    # sizes show whether Bokeh content was produced
                    script_chars=len(str(value.get('script') or '')),
                    div_chars=len(str(value.get('div') or '')),
                    keys=sorted(value))
        # keep only the end of a traceback, where the cause is
        trace = value.get('traceback')
        if trace:
            plot['traceback'] = str(trace)[-TRACEBACK_CHARS:]
        summary['plots'][name] = plot
    return summary


def _plot_cache(data_root: Path, instrument: str, profile_id: str,
                objname: str) -> dict[str, Any]:
    """Inspect server-side cached object-page plot responses for one object.

    Cached failures are served until the cache is invalidated or the user
    forces a reload, so this shows what the object page actually receives.

    :param data_root: Active ARI data directory.
    :param instrument: Explicitly authorized instrument.
    :param profile_id: Explicitly authorized profile ID.
    :param objname: Exact object name, validated by the caller.
    :return: Cache configuration, profile metadata, and entry summaries.
    """
    from apero_ri.core import plot_cache

    config = plot_cache.load_cache_config(data_root)
    cache_root = plot_cache.resolve_cache_root(data_root, config)
    pdir = plot_cache._profile_dir(cache_root, instrument, profile_id)
    section = pdir / 'object_plots'
    result = dict(enabled=bool(config.get('enabled')),
                  cache_root=str(cache_root),
                  meta=common.read_json(pdir / '_meta.json', pdir),
                  section=common.file_info(section), entries=[],
                  truncated=False)
    # cache keys look like <plot_group>__<objname>__<run-id tag>...
    token = '__' + plot_cache._safe_filename(objname) + '__'
    try:
        names = sorted(path.name for path in section.iterdir()
                       if path.suffix == '.json' and token in path.name)
    except OSError as error:
        result['error_type'] = type(error).__name__
        return result
    result['truncated'] = len(names) > PLOT_CACHE_ENTRIES
    for name in names[:PLOT_CACHE_ENTRIES]:
        entry = common.read_json(section / name, section,
                                 limit=PLOT_CACHE_LIMIT)
        data = entry.pop('data', None)
        if isinstance(data, dict):
            entry.update(cached_at=data.get('cached_at'),
                         generation_time_s=data.get('generation_time_s'),
                         response=_plot_payload_summary(
                             data.get('payload')))
        result['entries'].append(entry)
    return result


def _cache_with_plots(root: Path, data_root: Path, instrument: str,
                      profile_id: str, objname: str) -> dict[str, Any]:
    """Combine task-cache evidence with cached object-plot responses.

    :param root: Authorized profile task-cache directory.
    :param data_root: Active ARI data directory.
    :param instrument: Explicitly authorized instrument.
    :param profile_id: Explicitly authorized profile ID.
    :param objname: Optional exact object name, validated by the caller.
    :return: Cache section, with ``object_plots`` when an object is given.
    """
    result = _cache(root, objname)
    if objname:
        # isolate failures so table evidence survives a plot-cache error
        try:
            result['object_plots'] = _plot_cache(data_root, instrument,
                                                 profile_id, objname)
        except Exception as error:
            result['object_plots'] = dict(error=str(error))
    return result


def _manifests(profile: dict, instrument: str, name: str,
               tasks: list[dict],
               on_task: Callable[[str], None] | None = None) -> dict:
    """Check published task manifests and bounded file checksum samples.

    :param profile: Authorized profile configuration.
    :param instrument: Instrument associated with this profile.
    :param name: Profile ID used for published directories.
    :param tasks: This instrument's async task rows (loaded once by caller).
    :param on_task: Optional callback identifying the manifest being checked.
    :return: Manifest validity, freshness, and checksum evidence.
    """
    shared = apero_sync.precomputed_directory(profile, instrument, name)
    if shared is None:
        return dict(available=False, reason='PATH_OTHER_unconfigured')
    result = dict(root=common.file_info(shared), tasks=dict())
    for key in apero_sync.local_task_keys():
        if on_task is not None:
            on_task(key)
        payload = common.read_json(shared / ('.' + key + '.json'), shared)
        data = payload.pop('data', None)
        if isinstance(data, dict):
            task = next((row for row in tasks
                         if row.get('task_key') == key
                         and row.get('apero_profile') == name), dict())
            stale = apero_sync._manifest_is_stale(
                data, dict(TASK_CONFIG=task))
            files = data.get('files', [])
            payload.update(stale=stale, generated_at=data.get('generated_at'),
                           n_files=len(files), checks=[],
                           checks_truncated=len(files) > 5)
            for entry in files[:5]:
                path = shared / str(entry.get('path', ''))
                check = common.file_info(path)
                safe = (path.resolve().is_relative_to(shared.resolve())
                        and not path.is_symlink())
                if safe and path.is_file() and path.stat().st_size <= (
                        common.FILE_LIMIT):
                    digest = hashlib.sha256(path.read_bytes()).hexdigest()
                    check['checksum_valid'] = digest == entry.get('sha256')
                else:
                    check['checksum_skipped'] = True
                payload['checks'].append(check)
        result['tasks'][key] = payload
    return result


def collect(profile: dict, instrument: str, profile_id: str,
            data_root: Path, objname: str = '', pid: str = '',
            include_logs: bool = False, include_database: bool = True,
            progress: Callable[[str, int, int], None] | None = None
            ) -> dict[str, Any]:
    """Collect one profile's read-only report without refreshing its caches.

    :param profile: Authorized hydrated ARI profile configuration.
    :param instrument: Explicitly authorized instrument.
    :param profile_id: Explicitly authorized profile ID.
    :param data_root: Active ARI data directory.
    :param objname: Optional exact object filter.
    :param pid: Optional exact LogDatabase PID filter.
    :param include_logs: Include bounded log tails selected from DB metadata.
    :param include_database: Enable live bounded read-only database queries.
    :param progress: Optional callback receiving stage, completed and total.
    :return: Redacted report with independently collected evidence sections.
    """
    if objname and not OBJECT.fullmatch(objname):
        raise ValueError('invalid_object_name')
    if len(pid) > 160:
        raise ValueError('invalid_pid')
    total = 8 + int(include_database) + int(include_logs)
    completed = 0

    def notify(stage: str) -> None:
        """Publish the current stage and completed check count.

        :param stage: Stable collector stage identifier.
        :return: None.
        """
        if progress is not None:
            progress(stage, completed, total)

    notify('runtime')
    cache = data_root / 'tasks' / instrument / profile_id
    report = dict(schema_version=1, runtime=common.runtime(),
                  instrument=instrument, profile_id=profile_id,
                  filters=dict(objname=objname, pid=pid),
                  configuration=profile, sections=dict())
    completed += 1
    sections = report['sections']
    # async_tasks.yaml can be large; parse it once for manifests and tasks
    loaded_tasks: list[list[dict]] = []

    def instrument_tasks() -> list[dict]:
        """Return this instrument's async task rows, loading them once.

        :return: Task configuration rows for ``instrument``.
        """
        if not loaded_tasks:
            loaded_tasks.append(
                auth.load_async_tasks().get(instrument, []))
        return loaded_tasks[0]

    checks = dict(queues=lambda: _queues(instrument, profile_id),
        paths=lambda: {
        key: common.inventory(Path(value).expanduser())
        for key, value in profile.get('paths', {}).items()
        if key.startswith('PATH_') and value},
        cache=lambda: _cache_with_plots(cache, data_root, instrument,
                                        profile_id, objname),
        manifests=lambda: _manifests(
            profile, instrument, profile_id, instrument_tasks(),
            on_task=lambda key: notify('manifests:' + key)),
        tasks=lambda: [row for row in instrument_tasks()
                       if row.get('apero_profile') == profile_id])
    if include_database:
        checks['database'] = lambda: _database(profile, objname, pid)
    # seconds spent per stage, so slow checks are visible in the report
    timings = report['timings'] = dict()
    for name, check in checks.items():
        notify(name)
        stage_start = time.monotonic()
        try:
            sections[name] = check()
        except Exception as error:
            sections[name] = dict(error=str(error))
        timings[name] = round(time.monotonic() - stage_start, 3)
        completed += 1
    if include_logs:
        notify('log_tails')
        path = profile.get('paths', {}).get('PATH_LOG')
        rows = sections.get('database', {}).get('recipe_logs', [])
        if path:
            logroot = Path(path).expanduser()
            selected = list(dict.fromkeys(str(row.get('LOGFILE', ''))
                                         for row in rows if row.get('LOGFILE')))
            # LOGFILE values are usually relative to PATH_LOG
            logs = [Path(name) if Path(name).is_absolute()
                    else logroot / name for name in selected[:3]]
            sections['log_tails'] = [common.log_tail(log, logroot)
                                     for log in logs]
        completed = completed + 1
    notify('product_paths')
    products = sections.get('database', {}).get('product_examples', [])
    sections['product_paths'] = _products(profile, products)
    completed = completed + 1
    notify('finalize')
    report['limits'] = dict(file_bytes=common.FILE_LIMIT, rows=100,
                            log_files=3, log_tail_bytes=65536,
                            manifest_checks=5, recursive_scan=False)
    secrets = common.secret_values(profile)
    if include_database or include_logs:
        try:
            resolved = apero_async.get_db_params(profile)
            secrets.extend(common.secret_values(resolved))
        except Exception:
            pass
    result = common.redact(report, secrets)
    completed += 1
    notify('complete')
    return result


def _products(profile: dict, rows: list[dict]) -> dict:
    """Verify indexed product paths and sample FITS headers without arrays.

    :param profile: Authorized profile with configured product roots.
    :param rows: Bounded file-index product examples.
    :return: Path-access evidence and at most three FITS metadata samples.
    """
    from astropy.io import fits

    paths = profile.get('paths', {})
    result = dict(files=[], fits_samples=[])
    for row in rows[:100]:
        root_value = paths.get(BLOCK_KIND.get(row.get('BLOCK_KIND'), ''))
        if not root_value or not row.get('FILENAME'):
            continue
        root = Path(root_value).expanduser()
        filename = Path(str(row['FILENAME']))
        if filename.is_absolute():
            path = filename
        else:
            path = root / str(row.get('OBS_DIR') or '') / filename
        outside = not path.resolve().is_relative_to(root.resolve())
        if path.is_symlink() or outside:
            result['files'].append(dict(skipped='outside_root_or_symlink'))
            continue
        info = common.file_info(path)
        info['output'] = row.get('KW_OUTPUT')
        result['files'].append(info)
        if (len(result['fits_samples']) >= 3 or not path.is_file()
                or path.suffix.lower() != '.fits'):
            continue
        sample = dict(path=str(path), hdus=[])
        try:
            with fits.open(path, memmap=True, lazy_load_hdus=True) as hdus:
                for index, hdu in enumerate(hdus):
                    if index >= 12:
                        sample['hdus_truncated'] = True
                        break
                    header = {card.keyword: card.value
                              for card in list(hdu.header.cards)[:120]}
                    sample['hdus'].append(dict(name=hdu.name, header=header,
                                               header_cards=len(hdu.header)))
        except Exception as error:
            sample['error'] = str(error)
        result['fits_samples'].append(sample)
    return result


def _queues(instrument: str, profile_id: str) -> dict:
    """Collect diagnostics only from enabled queues linked to this profile.

    :param instrument: Authorized instrument.
    :param profile_id: Authorized profile ID.
    :return: Linked queue configuration, remote evidence, or failure metadata.
    """
    reports = dict()
    for name, queue in apero_queues.load_queues().items():
        if (not queue['enabled'] or queue['instrument'] != instrument
                or queue['profile_id'] != profile_id):
            continue
        entry = dict(connection=common.redact(queue))
        try:
            remote = diagnostic_api.queue_snapshot(queue['local_port'])
            matches = (remote.get('instrument') == instrument
                       and remote.get('profile_id') == profile_id)
            entry['identity_match'] = matches
            if matches:
                entry['report'] = remote
            else:
                entry['remote_identity'] = dict(
                    instrument=remote.get('instrument'),
                    profile_id=remote.get('profile_id'),
                    drs_uconfig=remote.get('drs_uconfig'))
                entry['error'] = 'linked_queue_profile_identity_mismatch'
        except Exception as error:
            entry['error'] = str(error)
        reports[name] = entry
    return reports


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================