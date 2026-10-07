#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Permission-checked endpoints for persistent RUN ID metadata."""

from typing import Any

from flask import jsonify, request, session

from apero_ri.core import auth
from apero_ri.core import permissions
from apero_ri.core import run_ids


def catalog_api(app: Any, save: bool = False) -> Any:
    """List or save RUN IDs for a permitted instrument.

    :param app: ARI application providing profile discovery and groups.
    :param save: Save one record when True; list catalog rows otherwise.
    :return: Flask JSON response with rows/record or a validation error.
    """
    user = auth.get_effective_user(session)
    if not user:
        return jsonify(success=False, error='Login required'), 401
    perms = permissions.resolve_user_permissions(user['groups'], app.ari_groups)
    body = request.get_json(silent=True) if save else request.args
    if not body or (save and not isinstance(body, dict)):
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
    app._get_instrument_run_ids(instrument)
    if not save:
        records = run_ids.update_catalog(auth.ARI_DIR, instrument)
        rows = [dict(run_id=rid, **records[rid]) for rid in sorted(records)]
        return jsonify(success=True, rows=rows)
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
    return jsonify(success=True, row=dict(run_id=rid, **records[rid]))