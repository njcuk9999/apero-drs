#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Admin-only API for installing or updating the local GeoLite database."""
from __future__ import annotations

import ipaddress
from pathlib import Path
from typing import Any

from flask import jsonify, request, session

from apero_ri.core import ari_lang_support
from apero_ri.setup import geoip as setup_geoip


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.application.admin_geoip_api_helpers'


# =============================================================================
# Define functions
# =============================================================================
def api_install(app: Any) -> Any:
    """Install the MaxMind database for an authenticated admin.

    :param app: ARI application with the standard admin-permission helper.
    :return: JSON success or localized error response.
    """
    user_info, _ = app._require_admin_user()
    if not user_info:
        return jsonify(success=False, error='Unauthorized'), 401
    if session.get('login_as'):
        return jsonify(success=False, error='Unauthorized'), 403

    origin = request.headers.get('Origin', '')
    expected_origin = request.host_url.rstrip('/')
    if not origin or origin != expected_origin:
        return jsonify(success=False, error='Request origin rejected.'), 403

    try:
        is_loopback = ipaddress.ip_address(
            request.remote_addr or '').is_loopback
    except ValueError:
        is_loopback = False
    if not request.is_secure and not is_loopback:
        message = ari_lang_support.translate(
            'Submit GeoLite credentials over HTTPS or from localhost.')
        return jsonify(success=False, error=message), 400

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(success=False, error='JSON request required.'), 400
    if payload.get('accept_terms') is not True:
        message = ari_lang_support.translate(
            'Accept the GeoLite terms before downloading the database.')
        return jsonify(success=False, error=message), 400

    account_id = str(payload.get('account_id') or '').strip()
    license_key = str(payload.get('license_key') or '').strip()
    if not account_id or not license_key:
        message = ari_lang_support.translate(
            'MaxMind account ID and license key are required.')
        return jsonify(success=False, error=message), 400

    data_dir = Path(app._resolve_local_data_dir())
    try:
        setup_geoip.install_database(data_dir, account_id, license_key)
    except Exception:
        message = ari_lang_support.translate(
            'GeoLite download failed. Check the account ID, license key, '
            'network access, and database permission.')
        return jsonify(success=False, error=message), 400

    message = ari_lang_support.translate(
        'GeoLite2 City database installed and active.')
    return jsonify(success=True, message=message)


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================
