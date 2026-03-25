#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: Email backend module.

Configuration is loaded from {ARI_DIR}/admin/email.yaml.
If that file does not exist or is empty, falls back to the legacy
ARI_EMAIL_BACKEND=log mode (writes codes to email_log.txt).

email.yaml schema
-----------------
enabled: true
provider: gmail          # gmail | outlook | smtp | log
from_address: you@gmail.com
smtp_host: smtp.gmail.com
smtp_port: 465
smtp_ssl: true           # true = SMTP_SSL (port 465), false = STARTTLS or plain
smtp_tls: false          # true = STARTTLS (port 587), ignored when smtp_ssl true
smtp_user: you@gmail.com
# smtp_password is stored in {ARI_DIR}/secret/smtp_password.enc via save_email_config().

Supported providers and their defaults
---------------------------------------
gmail:      smtp.gmail.com  port 465  SSL
outlook:    smtp.office365.com  port 587  TLS (STARTTLS)
yahoo:      smtp.mail.yahoo.com  port 465  SSL
office365:  smtp.office365.com  port 587  TLS
custom:     user-supplied host/port/flags
log:        no SMTP; write verification codes to admin/email_log.txt
"""

import base64
import os
import re
import smtplib
from email.message import EmailMessage
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import yaml

from apero_ri.core import secret_store as ss

# Email provider defaults
PROVIDER_DEFAULTS = {
    'gmail': {
        'label': 'Gmail',
        'smtp_host': 'smtp.gmail.com',
        'smtp_port': 465,
        'smtp_ssl': True,
        'smtp_tls': False,
        'help_url': 'https://support.google.com/accounts/answer/185833',
        'help_steps': [
            'Go to your Google Account → Security.',
            'Under "How you sign in to Google", enable 2-Step Verification.',
            'Back in Security, search for "App passwords" (or go to '
            'myaccount.google.com/apppasswords).',
            'Select app "Mail", device "Other", enter a name like "APERO RI", '
            'then click Generate.',
            'Copy the 16-character password shown — this is your SMTP password.',
            'You do NOT need to change this unless you revoke the app password.',
        ],
    },
    'outlook': {
        'label': 'Outlook / Hotmail',
        'smtp_host': 'smtp.office365.com',
        'smtp_port': 587,
        'smtp_ssl': False,
        'smtp_tls': True,
        'help_url': 'https://support.microsoft.com/en-us/office/pop-imap-and-smtp-settings-8361e398-8af4-4e97-b147-6c6c4ac95353',
        'help_steps': [
            'Sign in to outlook.com / office365.',
            'Go to Settings → Mail → Sync email → POP and IMAP.',
            'Enable IMAP access if not already on.',
            'Use your regular Microsoft account password as the SMTP password.',
            'If you have two-factor authentication, create an App Password via '
            'your Microsoft Account → Security → Advanced security options → '
            'App passwords.',
        ],
    },
    'yahoo': {
        'label': 'Yahoo Mail',
        'smtp_host': 'smtp.mail.yahoo.com',
        'smtp_port': 465,
        'smtp_ssl': True,
        'smtp_tls': False,
        'help_url': 'https://help.yahoo.com/kb/generate-third-party-passwords-sln15241.html',
        'help_steps': [
            'Sign in to Yahoo Mail.',
            'Go to Account Security (myaccount.yahoo.com/security).',
            'Enable two-step verification if not already on.',
            'Scroll to "Generate app password".',
            'Select "Other App", enter a name like "APERO RI", click Generate.',
            'Copy the displayed password — this is your SMTP password.',
        ],
    },
    'office365': {
        'label': 'Office 365 (org)',
        'smtp_host': 'smtp.office365.com',
        'smtp_port': 587,
        'smtp_ssl': False,
        'smtp_tls': True,
        'help_url': 'https://learn.microsoft.com/en-us/exchange/mail-flow-best-practices/how-to-set-up-a-multifunction-device-or-application-to-send-email-using-microsoft-365-or-office-365',
        'help_steps': [
            'Your O365 admin must enable SMTP AUTH for your mailbox.',
            'Go to Microsoft 365 admin centre → Users → Active users → '
            'your user → Mail tab → Manage email apps.',
            'Enable "Authenticated SMTP".',
            'Use your regular O365 email and password (or an app password if MFA '
            'is enabled).',
        ],
    },
    'custom': {
        'label': 'Custom SMTP',
        'smtp_host': '',
        'smtp_port': 587,
        'smtp_ssl': False,
        'smtp_tls': True,
        'help_url': '',
        'help_steps': [
            'Enter your SMTP server hostname, port, and credentials.',
            'Enable SSL if your server uses SSL (port 465 typically).',
            'Enable STARTTLS if your server uses STARTTLS (port 587 typically).',
        ],
    },
    'log': {
        'label': 'Log only (no email sent)',
        'smtp_host': '',
        'smtp_port': 0,
        'smtp_ssl': False,
        'smtp_tls': False,
        'help_url': '',
        'help_steps': [
            'In "log" mode no emails are sent.',
            'Verification codes are written to ~/.ari/admin/email_log.txt.',
            'An admin must read the code from that file and share it manually.',
            'Useful when setting up the system before email is configured.',
        ],
    },
}


def _get_email_config_path() -> Path:
    ari_dir = os.environ.get('ARI_DIR', os.path.expanduser('~/.ari'))
    return Path(ari_dir) / 'admin' / 'email.yaml'


def _get_email_password_path() -> Path:
    return ss.resolve_secret_file('smtp_password.enc')


def load_email_config() -> dict:
    """Load email configuration from disk. Returns defaults if missing."""
    path = _get_email_config_path()
    cfg = {}
    if path.exists():
        try:
            with open(path, 'r') as f:
                cfg = yaml.safe_load(f) or {}
        except Exception:
            cfg = {}

    password_path = _get_email_password_path()
    if (str(cfg.get('smtp_password_enc', '')).strip()
            and not password_path.exists()):
        password_path.write_text(
            str(cfg.get('smtp_password_enc', '')).strip(), encoding='utf-8')
        ss.protect_path(password_path, 0o600)
    if password_path.exists():
        cfg['smtp_password_enc'] = '__stored__'
    return cfg


def save_email_config(cfg: dict) -> None:
    """Persist email config. Passwords are base64-encoded before saving."""
    path = _get_email_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    password_path = _get_email_password_path()

    # Encode password if provided as plain text (not already encoded)
    raw_pw = cfg.pop('smtp_password', None)
    if raw_pw is not None:
        provider = str(cfg.get('provider', '')).strip().lower()
        normalized = _normalize_smtp_password(str(raw_pw), provider)
        if normalized:
            password_path.write_text(
                _encode_password(normalized), encoding='utf-8')
            ss.protect_path(password_path, 0o600)
        else:
            password_path.unlink(missing_ok=True)

    cfg.pop('smtp_password_enc', None)

    with open(path, 'w') as f:
        yaml.safe_dump(cfg, f, default_flow_style=False, allow_unicode=True)


def _encode_password(plain: str) -> str:
    """Lightly encode password so it is not plain-text in YAML."""
    return base64.b64encode(plain.encode()).decode()


def _decode_password(encoded: str) -> str:
    """Decode a lightly-encoded password."""
    try:
        return base64.b64decode(encoded.encode()).decode()
    except Exception:
        return ''


def _normalize_smtp_password(password: str, provider: str = '') -> str:
    """Normalise entered SMTP passwords while preserving non-Gmail semantics.

    Gmail app passwords are often copied as four groups with spaces,
    e.g. ``xxxx xxxx xxxx xxxx``. For Gmail, collapse those spaces.
    """
    pw = password.strip()
    if provider == 'gmail':
        # Remove grouping spaces from 16-char app passwords entered as 4x4.
        if re.fullmatch(r'[A-Za-z0-9]{4}( [A-Za-z0-9]{4}){3}', pw):
            pw = pw.replace(' ', '')
    return pw


def get_smtp_password(cfg: dict) -> str:
    """Extract SMTP password from config (decodes if encoded)."""
    provider = str(cfg.get('provider', '')).strip().lower()
    password_path = _get_email_password_path()
    if password_path.exists():
        try:
            encoded = password_path.read_text(encoding='utf-8').strip()
        except Exception:
            encoded = ''
        if encoded:
            return _normalize_smtp_password(
                _decode_password(encoded), provider)
    if 'smtp_password_enc' in cfg and cfg['smtp_password_enc']:
        return _normalize_smtp_password(
            _decode_password(cfg['smtp_password_enc']), provider)
    return ''


def test_email_connection(cfg: Optional[dict] = None) -> dict:
    """
    Attempt to connect and authenticate with the configured SMTP server.
    Returns {'ok': bool, 'error': str}.
    """
    if cfg is None:
        cfg = load_email_config()

    provider = cfg.get('provider', 'log')
    if provider == 'log' or not cfg.get('enabled', False):
        return {'ok': True, 'error': ''}  # log mode always "ok"

    host = str(cfg.get('smtp_host', '')).strip()
    port = int(cfg.get('smtp_port', 587))
    use_ssl = bool(cfg.get('smtp_ssl', False))
    use_tls = bool(cfg.get('smtp_tls', False))
    user = str(cfg.get('smtp_user', '')).strip()
    password = get_smtp_password(cfg)

    if not host:
        return {'ok': False, 'error': 'No SMTP host configured.'}
    if not user:
        return {'ok': False, 'error': 'No SMTP user configured.'}
    if not password:
        return {'ok': False, 'error': 'No SMTP password configured.'}

    timeout = float(cfg.get('smtp_timeout', 20))

    try:
        if use_ssl:
            with smtplib.SMTP_SSL(host, port, timeout=timeout) as server:
                server.ehlo()
                server.login(user, password)
        else:
            with smtplib.SMTP(host, port, timeout=timeout) as server:
                server.ehlo()
                if use_tls:
                    server.starttls()
                    server.ehlo()
                server.login(user, password)
        return {'ok': True, 'error': ''}
    except Exception as exc:
        return {'ok': False, 'error': str(exc)}


def send_email(to_address: str,
               subject: str,
               body: str,
               cfg: Optional[dict] = None) -> Optional[str]:
    """
    Send an email. Returns None on success, error string on failure.
    Falls back to log mode if not configured or provider=='log'.
    """
    if cfg is None:
        cfg = load_email_config()

    # Also respect legacy env-var override
    env_backend = os.environ.get('ARI_EMAIL_BACKEND', '').strip().lower()

    provider = cfg.get('provider', 'log')
    if (provider == 'log'
            or not cfg.get('enabled', False)
            or env_backend == 'log'):
        return _log_fallback(to_address, subject, body)

    host = str(cfg.get('smtp_host', '')).strip()
    port = int(cfg.get('smtp_port', 587))
    use_ssl = bool(cfg.get('smtp_ssl', False))
    use_tls = bool(cfg.get('smtp_tls', False))
    from_addr = (str(cfg.get('from_address', '')).strip()
                 or str(cfg.get('smtp_user', '')).strip())
    user = str(cfg.get('smtp_user', '')).strip()
    password = get_smtp_password(cfg)

    if not host or not user or not password:
        return _log_fallback(to_address, subject, body)

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = to_address
    msg.set_content(body)

    try:
        if use_ssl:
            with smtplib.SMTP_SSL(host, port, timeout=25) as server:
                server.ehlo()
                server.login(user, password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(host, port, timeout=25) as server:
                server.ehlo()
                if use_tls:
                    server.starttls()
                    server.ehlo()
                server.login(user, password)
                server.send_message(msg)
        return None
    except Exception as exc:
        return str(exc)


def send_verification_email(recipient_email: str,
                             code: str,
                             purpose: str) -> Optional[str]:
    """Send a verification code email. Returns None on success, error on failure."""
    subject = f'APERO RI verification code ({purpose})'
    body = (
        f'Your APERO RI verification code is: {code}\n\n'
        'This code expires in 15 minutes.\n\n'
        'If you did not request this, please ignore this email.\n'
    )
    return send_email(recipient_email, subject, body)


def _log_fallback(to_address: str, subject: str, body: str) -> Optional[str]:
    """Write email content to a log file instead of sending."""
    ari_dir = os.environ.get('ARI_DIR', os.path.expanduser('~/.ari'))
    log_path = Path(ari_dir) / 'admin' / 'email_log.txt'
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, 'a') as lf:
            lf.write(
                f'{datetime.now(timezone.utc).isoformat()}'
                f'  to={to_address}'
                f'  subject={subject!r}\n'
                f'  body={body!r}\n'
                f'---\n'
            )
        return None
    except Exception as exc:
        return f'Could not write email log: {exc}'


def get_support_email(cfg: Optional[dict] = None) -> str:
    """
    Return the configured support/from email address, or empty string.

    :param cfg: dict or None, pre-loaded email config (loads if None)

    :return: str, configured from email address
    :rtype: str
    """
    if cfg is None:
        cfg = load_email_config()
    return str(cfg.get('from_address', '')).strip()

# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================
