#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Permission-checked endpoints for persistent RUN ID metadata."""

import csv
from io import StringIO
from typing import Any

from flask import Response, jsonify, request, session

from apero_ri.core import auth
from apero_ri.core import permissions
from apero_ri.core import run_ids


def build_run_id_health(app: Any, perms: set) -> dict:
    """Report missing PI names for instruments the user can manage.

    :param app: ARI application providing RUN ID discovery.
    :param perms: Resolved user permissions.
    :return: Health status, totals, and per-instrument breakdown.
    """
    params = permissions.load_parameters()
    instruments = params.get('instruments', dict()).get('value', [])
    breakdown = []
    details = []
    total = 0
    missing = 0
    errors = []
    for instrument in instruments:
        if f'manage.run_id.{instrument}' not in perms:
            continue
        try:
            app._get_instrument_run_ids(instrument)
            records = run_ids.update_catalog(auth.ARI_DIR, instrument)
            count = sum(not str(row.get('pi') or '').strip()
                        for row in records.values())
            total += len(records)
            missing += count
            breakdown.append(dict(instrument=instrument, total=len(records),
                                  missing_pi=count))
            details.append(f'{instrument}: {count} of {len(records)} '
                           'RUN ID(s) missing a PI name.')
        except Exception as exc:
            errors.append(instrument)
            details.append(f'{instrument}: health check failed: {exc}')
    status = 'warning' if missing else 'ok'
    message = (f'{missing} of {total} RUN ID(s) missing a PI name.'
               if missing else f'All {total} RUN ID(s) have a PI name.')
    if errors:
        status = 'error'
        message += ' Health check failed for: ' + ', '.join(errors) + '.'
    return dict(status=status, message=message, details=details,
                instruments=breakdown, total=total, missing_pi=missing)


def catalog_api(app: Any, save: bool = False) -> Any:
    """List or save RUN IDs for a permitted instrument.

    :param app: ARI application providing profile discovery and groups.
    :param save: Save one record when True; list catalog rows otherwise.
    :return: Flask JSON response with rows/record or a validation error.
    """
    return _catalog_api(app, 'save' if save else 'list')


def import_api(app: Any) -> Any:
    """Import RUN ID CSV with normal catalog authorization.

    :param app: ARI application.
    :return: JSON import summary or validation error.
    """
    return _catalog_api(app, 'import')


def export_api(app: Any) -> Any:
    """Export the selected saved RUN IDs in their requested order.

    :param app: ARI application.
    :return: Downloadable CSV or JSON authorization/validation error.
    """
    return _catalog_api(app, 'export')


def _catalog_api(app: Any, operation: str) -> Any:
    """Authorize and execute one catalog operation.

    :param app: ARI application.
    :param operation: list, save, import, or export.
    :return: Flask JSON response.
    """
    user = auth.get_effective_user(session)
    if not user:
        return jsonify(success=False, error='Login required'), 401
    perms = permissions.resolve_user_permissions(user['groups'], app.ari_groups)
    mutation = operation != 'list'
    body = request.get_json(silent=True) if mutation else request.args
    if not body or (mutation and not isinstance(body, dict)):
        return jsonify(success=False, error='Missing data'), 400
    instrument = body.get('instrument', '')
    if not isinstance(instrument, str):
        return jsonify(success=False, error='Invalid instrument'), 400
    instrument = instrument.strip()
    if f'manage.run_id.{instrument}' not in perms:
        return jsonify(success=False, error='Insufficient permissions'), 403
    params = permissions.load_parameters()
    valid = params.get('instruments', dict()).get('value', [])
    if instrument not in valid:
        return jsonify(success=False, error='Invalid instrument'), 400
    if operation != 'import':
        app._get_instrument_run_ids(instrument)
    if operation == 'list':
        records = run_ids.update_catalog(auth.ARI_DIR, instrument)
        rows = [dict(run_id=rid, **records[rid]) for rid in sorted(records)]
        health = build_run_id_health(app, perms)
        return jsonify(success=True, rows=rows, health=health)
    if operation == 'export':
        selected = body.get('run_ids', [])
        if not isinstance(selected, list):
            return jsonify(success=False, error='Invalid RUN ID selection'), 400
        records = run_ids.update_catalog(auth.ARI_DIR, instrument)
        seen = set()
        output = StringIO(newline='')
        writer = csv.writer(output)
        writer.writerow(['RUN ID', 'PI', 'COMMENT'])
        for run_id in selected:
            if not isinstance(run_id, str) or run_id not in records:
                return jsonify(success=False, error='Unknown RUN ID'), 400
            if run_id in seen:
                continue
            seen.add(run_id)
            record = records[run_id]
            writer.writerow([run_id, record.get('pi', ''),
                             record.get('comment', '')])
        response = Response('\ufeff' + output.getvalue(),
                            mimetype='text/csv')
        filename = f'{instrument.lower()}_run_ids.csv'
        response.headers.set('Content-Disposition', 'attachment',
                             filename=filename)
        return response
    if operation == 'import':
        content = body.get('csv', '')
        policy = body.get('duplicate_policy', 'reject')
        if not isinstance(content, str) or not isinstance(policy, str):
            return jsonify(success=False, error='Invalid import fields'), 400
        if len(content.encode('utf-8')) > 5 * 1024 * 1024:
            return jsonify(success=False, error='CSV exceeds 5 MB'), 400
        try:
            import_args = [auth.ARI_DIR, instrument, content, policy]
            summary = run_ids.import_csv(*import_args)
        except ValueError as exc:
            return jsonify(success=False, error=str(exc)), 400
        records = run_ids.update_catalog(auth.ARI_DIR, instrument)
        app._sync_all_science_group(instrument, None, sorted(records), True)
        app._refresh_admin_health_after_change(user, perms)
        rows = [dict(run_id=rid, **records[rid]) for rid in sorted(records)]
        health = build_run_id_health(app, perms)
        return jsonify(success=True, summary=summary, rows=rows, health=health)
    fields = ['run_id', 'pi', 'comment']
    if any(not isinstance(body.get(key, ''), str) for key in fields):
        return jsonify(success=False, error='Fields must be text'), 400
    create = body.get('create', False)
    if not isinstance(create, bool):
        return jsonify(success=False, error='Invalid create flag'), 400
    save_kwargs = dict(run_id=body.get('run_id', ''), create=create,
                       pi=body.get('pi', ''), comment=body.get('comment', ''))
    try:
        save_args = [auth.ARI_DIR, instrument]
        records = run_ids.update_catalog(*save_args, **save_kwargs)
    except ValueError as exc:
        return jsonify(success=False, error=str(exc)), 400
    rid = str(body.get('run_id', '')).strip()
    app._sync_all_science_group(instrument, None, sorted(records), True)
    app._refresh_admin_health_after_change(user, perms)
    health = build_run_id_health(app, perms)
    return jsonify(success=True, row=dict(run_id=rid, **records[rid]),
                   health=health)