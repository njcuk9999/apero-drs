#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: cryptography for server-to-server sync.

A pairing token has the form ``ARISYNC1.<key_id>.<secret>``. The token is
never sent over the wire: each request carries only the key id plus an
HMAC-SHA256 signature over (method, path, timestamp, nonce, body digest),
and every request/response body is gzip-compressed and Fernet-encrypted
(AES-128-CBC + HMAC-SHA256) with a key derived from the secret. This keeps
payloads confidential and tamper-proof on plain HTTP links.

Created on 2026-10-22

@author: cook
"""
import base64
import gzip
import hashlib
import hmac
import json
import secrets
from typing import Any, Tuple

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.core.server_sync.crypto'
# token prefix (bump the number if the token or key scheme ever changes)
TOKEN_PREFIX = 'ARISYNC1'
# HKDF salt shared by both servers (not secret)
_HKDF_SALT = b'apero-ri-server-sync-v1'
# header names used by the signed protocol
HDR_KEY_ID = 'X-ARI-Sync-Key'
HDR_TIMESTAMP = 'X-ARI-Sync-Timestamp'
HDR_NONCE = 'X-ARI-Sync-Nonce'
HDR_SIGNATURE = 'X-ARI-Sync-Signature'
HDR_SERVER_ID = 'X-ARI-Sync-Server'


# =============================================================================
# Define token functions
# =============================================================================
def new_token() -> Tuple[str, str, str]:
    """
    Create a new pairing token.

    :return: tuple (key_id, secret, token string)
    :rtype: tuple
    """
    # short public id used to look up the secret on the issuing server
    key_id = secrets.token_hex(8)
    # 256-bit secret, url-safe so it can be copied/pasted safely
    secret = secrets.token_urlsafe(32)
    token = f'{TOKEN_PREFIX}.{key_id}.{secret}'
    return key_id, secret, token


def parse_token(token: str) -> Tuple[str, str]:
    """
    Split a pairing token into its key id and secret.

    :param token: str, the pairing token (ARISYNC1.<key_id>.<secret>)

    :return: tuple (key_id, secret)
    :rtype: tuple
    :raises ValueError: if the token is malformed
    """
    parts = str(token or '').strip().split('.', 2)
    if len(parts) != 3 or parts[0] != TOKEN_PREFIX:
        raise ValueError('Token must look like ARISYNC1.<id>.<secret>')
    key_id, secret = parts[1], parts[2]
    if len(key_id) != 16 or len(secret) < 32:
        raise ValueError('Token is truncated or malformed')
    return key_id, secret


def _derive(secret: str, info: bytes) -> bytes:
    """
    Derive a 32-byte sub-key from the token secret.

    :param secret: str, the token secret
    :param info: bytes, purpose label (separates signing/encryption keys)

    :return: bytes, derived key
    :rtype: bytes
    """
    hkdf = HKDF(algorithm=hashes.SHA256(), length=32, salt=_HKDF_SALT,
                info=info)
    return hkdf.derive(secret.encode('utf-8'))


def _fernet(secret: str) -> Fernet:
    """
    Build the Fernet cipher for a token secret.

    :param secret: str, the token secret

    :return: Fernet instance
    :rtype: Fernet
    """
    key = base64.urlsafe_b64encode(_derive(secret, b'encrypt'))
    return Fernet(key)


# =============================================================================
# Define signing functions
# =============================================================================
def body_digest(body: bytes) -> str:
    """
    Return the sha256 hex digest of a request body.

    :param body: bytes, raw request body

    :return: str, hex digest
    :rtype: str
    """
    return hashlib.sha256(body or b'').hexdigest()


def sign_request(secret: str, method: str, path: str, timestamp: str,
                 nonce: str, body: bytes) -> str:
    """
    Compute the HMAC signature of a request.

    :param secret: str, the token secret
    :param method: str, HTTP method
    :param path: str, URL path (no host, no query)
    :param timestamp: str, unix time as a string
    :param nonce: str, single-use random value
    :param body: bytes, raw (encrypted) request body

    :return: str, hex signature
    :rtype: str
    """
    parts = [method.upper(), path, timestamp, nonce, body_digest(body)]
    message = '\n'.join(parts).encode('utf-8')
    sign_key = _derive(secret, b'sign')
    return hmac.new(sign_key, message, hashlib.sha256).hexdigest()


def verify_request(secret: str, method: str, path: str, timestamp: str,
                   nonce: str, body: bytes, signature: str) -> bool:
    """
    Check a request signature in constant time.

    :param secret: str, the token secret
    :param method: str, HTTP method
    :param path: str, URL path
    :param timestamp: str, unix time as a string
    :param nonce: str, single-use random value
    :param body: bytes, raw request body
    :param signature: str, signature supplied by the caller

    :return: bool, True if the signature is valid
    :rtype: bool
    """
    sign_args = [secret, method, path, timestamp, nonce, body]
    expected = sign_request(*sign_args)
    return hmac.compare_digest(expected, str(signature or ''))


# =============================================================================
# Define payload functions
# =============================================================================
def encrypt_payload(secret: str, payload: Any) -> bytes:
    """
    Serialise, compress and encrypt a JSON-able payload.

    :param secret: str, the token secret
    :param payload: Any, JSON-serialisable object

    :return: bytes, Fernet token
    :rtype: bytes
    """
    raw = json.dumps(payload, default=str).encode('utf-8')
    return _fernet(secret).encrypt(gzip.compress(raw))


def decrypt_payload(secret: str, blob: bytes) -> Any:
    """
    Decrypt, decompress and parse a payload.

    :param secret: str, the token secret
    :param blob: bytes, Fernet token

    :return: Any, the decoded JSON object
    :rtype: Any
    :raises ValueError: if the payload cannot be authenticated
    """
    try:
        raw = _fernet(secret).decrypt(bytes(blob or b''))
    except InvalidToken as exc:
        raise ValueError('Payload failed authentication') from exc
    return json.loads(gzip.decompress(raw).decode('utf-8'))


# =============================================================================
# End of code
# =============================================================================
