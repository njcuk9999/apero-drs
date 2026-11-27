#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Dedicated, non-persistent diagnostic transport for ARI and queue reports."""

import json
from typing import Callable
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
# full profile reports can be tens of MB (object tables, FITS samples)
STREAM_LIMIT = 512 * 1024 * 1024
# the server sends a heartbeat every 10 s, so silence this long is a failure
STREAM_READ_TIMEOUT = 60

# =============================================================================
# Define functions
# =============================================================================
def _http_error(response: requests.Response) -> ValueError:
    """Build an error naming the HTTP status and the server's error code.

    :param response: Non-200 diagnostic response.
    :return: Error safe to show (codes only, never request headers).
    """
    code = ''
    try:
        # ARI errors are small JSON bodies with a fixed ``code`` identifier
        body = json.loads(response.raw.read(4096, decode_content=True))
        if isinstance(body, dict) and isinstance(body.get('code'), str):
            code = body['code']
    except (ValueError, OSError, AttributeError):
        pass
    message = 'diagnostic_http_' + str(response.status_code)
    return ValueError(message + (': ' + code if code else ''))


def _stream_event(line: bytes,
                  on_event: Callable[[dict], None] | None) -> dict | None:
    """Handle one stream line, returning the report when it arrives.

    :param line: One newline-delimited JSON event.
    :param on_event: Optional callback for progress and heartbeat events.
    :return: Completed report, or None for any other event.
    :raises ValueError: On a collection error event or invalid data.
    """
    if not line.strip():
        return None
    event = json.loads(line)
    if not isinstance(event, dict):
        raise ValueError('invalid_diagnostic_response')
    if event.get('type') == 'report':
        return event.get('report') or dict()
    if event.get('type') == 'error':
        raise ValueError(str(event.get('code', 'collection_failed')))
    if on_event is not None:
        on_event(event)
    return None


def _stream(url: str, headers: dict, params: dict,
            on_event: Callable[[dict], None] | None) -> dict:
    """Follow a newline-delimited JSON collection until its report arrives.

    :param url: Validated diagnostic stream URL.
    :param headers: Authorization headers, never included in errors.
    :param params: Scalar read-only filters.
    :param on_event: Optional callback for progress and heartbeat events.
    :return: Completed diagnostic report.
    :raises ValueError: On HTTP errors, collection failure or oversize data.
    """
    with requests.Session() as client:
        client.trust_env = False
        timeout = (10, STREAM_READ_TIMEOUT)
        with client.get(url, headers=headers, params=params, stream=True,
                        allow_redirects=False, timeout=timeout) as response:
            if response.status_code != 200:
                raise _http_error(response)
            pending = bytearray()
            received = 0
            for chunk in response.iter_content(65536):
                received += len(chunk)
                if received > STREAM_LIMIT:
                    raise ValueError('diagnostic_response_too_large')
                # split only the new chunk so a large report line stays linear
                pieces = chunk.split(b'\n')
                pending.extend(pieces[0])
                for piece in pieces[1:]:
                    # ``pending`` now holds one complete line
                    report = _stream_event(bytes(pending), on_event)
                    if report is not None:
                        return report
                    pending = bytearray(piece)
            # the stream closed without a report or error event
            raise ValueError('diagnostic_stream_incomplete')


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
                raise _http_error(response)
            content = bytearray()
            for chunk in response.iter_content(65536):
                content.extend(chunk)
                if len(content) > RESPONSE_LIMIT:
                    raise ValueError('diagnostic_response_too_large')
            data = json.loads(content)
            if not isinstance(data, dict) or data.get('success') is False:
                raise ValueError('invalid_diagnostic_response')
            return data


def request_report(host: str, key: str, action: str = 'profiles',
                   params: dict | None = None,
                   on_event: Callable[[dict], None] | None = None) -> dict:
    """Fetch a scoped ARI diagnostic report over HTTP or HTTPS.

    :param host: ARI base URL, not a page or arbitrary endpoint.
    :param key: Short-lived diagnostic credential.
    :param action: Fixed profiles, report, or stream read operation.
    :param params: Optional instrument, profile, object, PID, and flags.
    :param on_event: For ``stream`` only: callback receiving progress and
                     heartbeat events while the server collects.
    :return: Diagnostic JSON response (the report itself for ``stream``).
    """
    parsed = urlsplit(host)
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError('invalid_diagnostic_host')
    if parsed.scheme not in ('http', 'https') or not parsed.hostname:
        raise ValueError('invalid_diagnostic_host')
    if action not in ('profiles', 'report', 'stream'):
        raise ValueError('invalid_diagnostic_action')
    url = host.rstrip('/') + '/api/diagnostics/' + action
    headers = dict(Authorization='Bearer ' + key)
    if action == 'stream':
        return _stream(url, headers, params or dict(), on_event)
    return _get(url, headers, params or dict())


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