#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Dedicated, non-persistent diagnostic transport for ARI and queue reports."""

from urllib.parse import urlsplit

import requests

from apero_ri.base import base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.ari_api.diagnostics'
__version__ = base.__version__
__date__ = base.__date__
__authors__ = base.__authors__
RESPONSE_LIMIT = 16 * 1024 * 1024

# =============================================================================
# Define functions
# =============================================================================
def _get(url: str, headers: dict, params: dict) -> dict:
    """Read bounded JSON without redirects or persisting authorization.

    :param url: Validated diagnostic URL.
    :param headers: Authorization headers, never included in errors.
    :param params: Scalar read-only filters.
    :return: JSON diagnostic response.
    """
    with requests.Session() as client:
        client.trust_env = False
        with client.get(url, headers=headers, params=params, stream=True,
                        allow_redirects=False, timeout=(10, 300)) as response:
            if response.status_code != 200:
                raise ValueError('diagnostic_http_' + str(response.status_code))
            content = bytearray()
            for chunk in response.iter_content(65536):
                content.extend(chunk)
                if len(content) > RESPONSE_LIMIT:
                    raise ValueError('diagnostic_response_too_large')
            import json

            data = json.loads(content)
            if not isinstance(data, dict) or data.get('success') is False:
                raise ValueError('invalid_diagnostic_response')
            return data


def request_report(host: str, key: str, action: str = 'profiles',
                   params: dict | None = None) -> dict:
    """Fetch a scoped ARI diagnostic report over HTTPS or local tunneling.

    :param host: ARI base URL, not a page or arbitrary endpoint.
    :param key: Short-lived diagnostic credential.
    :param action: Fixed profiles or report read operation.
    :param params: Optional instrument, profile, object, PID, and flags.
    :return: Diagnostic JSON response.
    """
    parsed = urlsplit(host)
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError('invalid_diagnostic_host')
    if parsed.scheme not in ('http', 'https') or not parsed.hostname:
        raise ValueError('invalid_diagnostic_host')
    if parsed.scheme == 'http' and parsed.hostname not in (
            'localhost', '127.0.0.1', '::1'):
        raise ValueError('diagnostics_require_https_or_local_tunnel')
    if action not in ('profiles', 'report'):
        raise ValueError('invalid_diagnostic_action')
    url = host.rstrip('/') + '/api/diagnostics/' + action
    return _get(url, dict(Authorization='Bearer ' + key), params or dict())


def queue_snapshot(local_port: str) -> dict:
    """Read only the diagnostic endpoint of an administrator-linked tunnel.

    :param local_port: Configured local SSH-forward port, never user input.
    :return: Queue-host diagnostic report.
    """
    if not local_port.isdigit() or not 0 < int(local_port) < 65536:
        raise ValueError('invalid_queue_tunnel_port')
    url = f'http://127.0.0.1:{local_port}/api/diagnostics'
    return _get(url, dict(), dict())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================