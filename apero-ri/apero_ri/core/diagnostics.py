#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Read-only diagnostics for one explicitly authorized ARI profile."""

import hashlib
import re
from pathlib import Path
from typing import Any

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


def _manifests(profile: dict, instrument: str, name: str) -> dict:
    """Check published task manifests and bounded file checksum samples.

    :param profile: Authorized profile configuration.
    :param instrument: Instrument associated with this profile.
    :param name: Profile ID used for published directories.
    :return: Manifest validity, freshness, and checksum evidence.
    """
    shared = apero_sync.precomputed_directory(profile, instrument, name)
    if shared is None:
        return dict(available=False, reason='PATH_OTHER_unconfigured')
    result = dict(root=common.file_info(shared), tasks=dict())
    tasks = auth.load_async_tasks().get(instrument, [])
    for key in apero_sync.local_task_keys():
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
            include_logs: bool = False, include_database: bool = True
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
    :return: Redacted report with independently collected evidence sections.
    """
    if objname and not OBJECT.fullmatch(objname):
        raise ValueError('invalid_object_name')
    if len(pid) > 160:
        raise ValueError('invalid_pid')
    cache = data_root / 'tasks' / instrument / profile_id
    report = dict(schema_version=1, runtime=common.runtime(),
                  instrument=instrument, profile_id=profile_id,
                  filters=dict(objname=objname, pid=pid),
                  configuration=profile, sections=dict())
    sections = report['sections']
    checks = dict(queues=lambda: _queues(instrument, profile_id),
        paths=lambda: {
        key: common.inventory(Path(value).expanduser())
        for key, value in profile.get('paths', {}).items()
        if key.startswith('PATH_') and value},
        cache=lambda: _cache(cache, objname),
        manifests=lambda: _manifests(profile, instrument, profile_id),
        tasks=lambda: [row for row in
                       auth.load_async_tasks().get(instrument, [])
                       if row.get('apero_profile') == profile_id])
    if include_database:
        checks['database'] = lambda: _database(profile, objname, pid)
    for name, check in checks.items():
        try:
            sections[name] = check()
        except Exception as error:
            sections[name] = dict(error=str(error))
    if include_logs:
        path = profile.get('paths', {}).get('PATH_LOG')
        rows = sections.get('database', {}).get('recipe_logs', [])
        if path:
            logroot = Path(path).expanduser()
            selected = list(dict.fromkeys(str(row.get('LOGFILE', ''))
                                         for row in rows if row.get('LOGFILE')))
            sections['log_tails'] = [common.log_tail(Path(name), logroot)
                                     for name in selected[:3]]
    products = sections.get('database', {}).get('product_examples', [])
    sections['product_paths'] = _products(profile, products)
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
    return common.redact(report, secrets)


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