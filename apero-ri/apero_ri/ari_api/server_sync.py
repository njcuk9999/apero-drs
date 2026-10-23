#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ARI API: client for the server-to-server sync protocol.

Every call is a POST to ``/api/server-sync/peer/<action>`` on the other
server. The body is the encrypted JSON payload; headers carry the token
key id, a timestamp, a nonce and an HMAC signature (see
``apero_ri.core.server_sync.crypto``). Responses are encrypted with the
same key and echo the request nonce so they cannot be replayed or
swapped.

Created on 2026-10-22

@author: cook
"""
import secrets
import time
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import urlparse

from apero_ri.core.server_sync import crypto

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.ari_api.server_sync'
# URL prefix of the peer endpoints
PEER_PREFIX = '/api/server-sync/peer'
# default request timeout in seconds
DEFAULT_TIMEOUT = 120.0


class PeerError(RuntimeError):
    """Raised when a peer request fails."""

    def __init__(self, message: str, status: Optional[int] = None) -> None:
        """
        Store the message and HTTP status.

        :param message: str, error message
        :param status: int or None, HTTP status code

        :return: None
        """
        super().__init__(message)
        self.status = status


def normalise_url(url: str) -> str:
    """
    Validate and normalise a peer base URL.

    :param url: str, e.g. http://host:5000 or https://host/ari

    :return: str, URL without trailing slash
    :rtype: str
    :raises ValueError: if the URL is not http(s) with a host
    """
    url = str(url or '').strip().rstrip('/')
    parsed = urlparse(url)
    if parsed.scheme not in ('http', 'https') or not parsed.netloc:
        raise ValueError('URL must start with http:// or https:// and '
                         'include a host')
    if parsed.query or parsed.fragment:
        raise ValueError('URL must not contain a query or fragment')
    return url


class PeerClient:
    """Signed, encrypted client for one peer server."""

    def __init__(self, url: str, token: str, local_server_id: str,
                 timeout: float = DEFAULT_TIMEOUT) -> None:
        """
        Prepare a client.

        :param url: str, peer base URL
        :param token: str, pairing token issued by the peer
        :param local_server_id: str, this server's sync id (sent as header)
        :param timeout: float, request timeout in seconds

        :return: None
        """
        self.url = normalise_url(url)
        self.key_id, self._secret = crypto.parse_token(token)
        self.local_server_id = local_server_id
        self.timeout = timeout
        # path prefix when the peer is served below a sub-path
        self._base_path = urlparse(self.url).path

    def call(self, action: str, payload: Any) -> Any:
        """
        Send one signed/encrypted request and decode the reply.

        :param action: str, peer action (hello, manifest, fetch, apply)
        :param payload: Any, JSON-able request payload

        :return: Any, decoded response payload
        :rtype: Any
        :raises PeerError: on transport, auth or decoding failure
        """
        import requests

        path = f'{self._base_path}{PEER_PREFIX}/{action}'
        nonce = secrets.token_hex(16)
        timestamp = str(int(time.time()))
        envelope = dict(nonce=nonce, payload=payload)
        body = crypto.encrypt_payload(self._secret, envelope)
        sign_args = [self._secret, 'POST', path, timestamp, nonce, body]
        headers = dict()
        headers['Content-Type'] = 'application/octet-stream'
        headers[crypto.HDR_KEY_ID] = self.key_id
        headers[crypto.HDR_TIMESTAMP] = timestamp
        headers[crypto.HDR_NONCE] = nonce
        headers[crypto.HDR_SIGNATURE] = crypto.sign_request(*sign_args)
        headers[crypto.HDR_SERVER_ID] = self.local_server_id
        full_url = f'{self.url}{PEER_PREFIX}/{action}'
        try:
            resp = requests.post(full_url, data=body, headers=headers,
                                 timeout=self.timeout, allow_redirects=False)
        except requests.RequestException as exc:
            raise PeerError(f'Cannot reach {self.url}: {exc}') from exc
        if resp.status_code != 200:
            # errors before authentication are plain JSON
            try:
                message = resp.json().get('error') or resp.text[:300]
            except ValueError:
                message = resp.text[:300]
            raise PeerError(f'{action}: HTTP {resp.status_code}: {message}',
                            resp.status_code)
        try:
            reply = crypto.decrypt_payload(self._secret, resp.content)
        except ValueError as exc:
            raise PeerError(f'{action}: could not decrypt reply') from exc
        if not isinstance(reply, dict) or reply.get('nonce') != nonce:
            raise PeerError(f'{action}: reply does not match request')
        if reply.get('error'):
            raise PeerError(f'{action}: {reply["error"]}')
        return reply.get('payload')

    def hello(self, server_name: str) -> Dict[str, Any]:
        """
        Exchange identities and clocks.

        :param server_name: str, this server's display name

        :return: dict with the peer's identity, time and token scope
        :rtype: dict
        """
        sent = time.time()
        info = self.call('hello', dict(server_id=self.local_server_id,
                                       server_name=server_name, time=sent))
        received = time.time()
        # skew = peer clock - our clock (at the request midpoint)
        info['clock_skew'] = float(info.get('time', 0)) - (sent + received) / 2
        info['round_trip'] = received - sent
        return info

    def manifest(self, categories: Iterable[str]) -> Dict[str, Any]:
        """
        Fetch the peer's journal for some categories.

        :param categories: iterable of category names

        :return: dict category -> {key: entry}
        :rtype: dict
        """
        return self.call('manifest', dict(categories=list(categories)))

    def fetch(self, category: str, keys: List[str]) -> Dict[str, Any]:
        """
        Fetch record data from the peer.

        :param category: str, category name
        :param keys: list of record keys

        :return: dict key -> data
        :rtype: dict
        """
        return self.call('fetch', dict(category=category, keys=list(keys)))

    def apply(self, category: str, upserts: Dict[str, Any],
              deletes: Dict[str, Any]) -> Dict[str, str]:
        """
        Push records to the peer (requires a read+write token).

        :param category: str, category name
        :param upserts: dict key -> {'data', 'h', 'ts', 'i', 'l'}
        :param deletes: dict key -> {'ts', 'l'}

        :return: dict key -> error for records the peer rejected
        :rtype: dict
        """
        payload = dict(category=category, upserts=upserts, deletes=deletes)
        return self.call('apply', payload) or dict()


# =============================================================================
# End of code
# =============================================================================
