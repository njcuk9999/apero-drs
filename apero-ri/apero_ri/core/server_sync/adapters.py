#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: data-category adapters for server-to-server sync.

Each adapter exposes the records of one data category as
``{key: Rec}`` (``export``) and writes incoming changes (``apply``).
Keys are JSON-encoded lists so composite keys stay unambiguous.

Rules shared by every adapter:

- the setup ("root") admin and anything owned by it is never exported
  and never written
- host-specific fields (disk paths, local ports, ssh aliases, mount
  points) are kept local; values from the other server are offered only
  as ``LOCAL_DEFAULTS`` for newly created records, which are then flagged
  with ``sync_needs_local_setup``
- every key coming from the other server is validated before it is used
  to build a path

Created on 2026-10-22

@author: cook
"""
import hashlib
import json
import re
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from apero_ri.core import api_tokens
from apero_ri.core import apero_checks
from apero_ri.core import auth
from apero_ri.core import basket_funcs
from apero_ri.core import email_backend
from apero_ri.core import issues
from apero_ri.core import known_errors
from apero_ri.core import notifications
from apero_ri.core import object_comments
from apero_ri.core import object_groups
from apero_ri.core import permissions
from apero_ri.core import run_ids
from apero_ri.core import schedule
from apero_ri.core import sshfs_backend
from apero_ri.core import user_data
from apero_ri.core import vault_store
from apero_ri.core.server_sync import store

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.core.server_sync.adapters'
# record-data key holding values only used when creating a record locally
LOCAL_DEFAULTS = '__local_defaults__'
# flag written on records that need host-specific setup after a sync
NEEDS_SETUP = 'sync_needs_local_setup'
# safe file/user/profile name (no path separators, no leading dot)
_SAFE_NAME = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_.@+\-]{0,199}$')
# per-user files synced as whole files (notes are handled separately)
USER_FILES = ('links.yaml', 'calendar.yaml', 'todo.yaml', 'prefs.yaml',
              'pins.yaml', 'object_section.yaml', 'favourite_objects.yaml',
              'basket.json')
# user fields that change on every login / reset and must not sync
USER_VOLATILE = ('last_login', 'password_reset')
# apero-profile fields that stay on this server
PROFILE_LOCAL = ('paths', 'disabled', 'DISABLED', 'temporary', NEEDS_SETUP)
# astrometric catalogue status sub-directories ('' = legacy root)
ASTROM_STATUS = ('verified', 'pending', 'rejected', '')
# async task fields that are synced (everything else is host-specific)
ASYNC_SYNCED = ('active', 'frequency')
# async tasks that are never synced (they drive the sync itself)
ASYNC_EXCLUDED = ('SERVER_SYNC', 'SERVER_SYNC_TASK_DATA')
# sshfs mount fields that stay on this server
SSHFS_LOCAL = ('local_mount', 'ssh_config_host', 'connection_mode',
               'manual_mode', 'status', NEEDS_SETUP)
# db tunnel fields that stay on this server
TUNNEL_LOCAL = ('ssh_config_host', 'local_port', 'ssh_mode', NEEDS_SETUP)
# local database definition fields that stay on this server
LOCALDB_LOCAL = ('DATABASE_HOST', 'DATABASE_PORT', NEEDS_SETUP)
# derived task files larger than this are never transferred
TASK_FILE_MAX_BYTES = 200 * 1024 * 1024


class Rec:
    """A single exported record."""

    def __init__(self, data: Any, ts: Optional[float] = None,
                 ident: Iterable[str] = (), label: str = '',
                 digest: Optional[str] = None) -> None:
        """
        Build a record.

        :param data: Any, JSON-able portable record data (None when lazy)
        :param ts: float or None, best known modification time (epoch)
        :param ident: iterable of str, identity strings for duplicate checks
        :param label: str, short human-readable description
        :param digest: str or None, precomputed hash (lazy adapters only)

        :return: None
        """
        self.data = data
        self.ts = ts
        self.ident = list(ident)
        self.label = label
        self.digest = digest


class SyncContext:
    """Information shared by adapters during one export/apply."""

    def __init__(self) -> None:
        """
        Capture the data directory and root username.

        :return: None
        """
        self.ari_dir = Path(auth.ARI_DIR)
        self.root = store.root_username()


# =============================================================================
# Define helper functions
# =============================================================================
def make_key(*parts: Any) -> str:
    """
    Encode a composite key.

    :param parts: key components

    :return: str, JSON-encoded key
    :rtype: str
    """
    return json.dumps([str(p) for p in parts])


def split_key(key: str, size: int) -> List[str]:
    """
    Decode and validate a composite key.

    :param key: str, JSON-encoded key
    :param size: int, required number of components

    :return: list of str
    :rtype: list
    :raises ValueError: if the key is malformed
    """
    try:
        parts = json.loads(key)
    except ValueError as exc:
        raise ValueError(f'Malformed key: {key!r}') from exc
    if not isinstance(parts, list) or len(parts) != size:
        raise ValueError(f'Malformed key: {key!r}')
    return [str(p) for p in parts]


def safe_name(value: str) -> str:
    """
    Validate a name that will be used as a path component.

    :param value: str, candidate name

    :return: str, the same name
    :rtype: str
    :raises ValueError: if the name is unsafe
    """
    value = str(value or '')
    if not _SAFE_NAME.match(value) or '..' in value:
        raise ValueError(f'Unsafe name: {value!r}')
    return value


def mtime(path: Path) -> Optional[float]:
    """
    Return a file's modification time or None.

    :param path: Path, file

    :return: float or None
    :rtype: float
    """
    try:
        return path.stat().st_mtime
    except OSError:
        return None


def parse_ts(value: Any) -> Optional[float]:
    """
    Convert an ISO string / epoch / datetime into an epoch float.

    :param value: Any, timestamp-like value

    :return: float or None
    :rtype: float
    """
    if value is None or value == '':
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, datetime):
        dt = value
    else:
        try:
            dt = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        except ValueError:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.timestamp()


def max_ts(*values: Any) -> Optional[float]:
    """
    Return the latest of several timestamp-like values.

    :param values: timestamp-like values

    :return: float or None
    :rtype: float
    """
    parsed = [t for t in (parse_ts(v) for v in values) if t is not None]
    return max(parsed) if parsed else None


def instruments() -> List[str]:
    """
    Return the instruments configured in parameters.yaml.

    :return: list of instrument names
    :rtype: list
    """
    entry = permissions.load_parameters().get('instruments', dict())
    values = entry.get('value', []) if isinstance(entry, dict) else entry
    return [str(v) for v in (values or [])]


def write_text(path: Path, text: str, mode: Optional[int] = None) -> None:
    """
    Atomically write a text file.

    :param path: Path, destination
    :param text: str, contents
    :param mode: int or None, file mode

    :return: None
    """
    store.write_atomic(path, text, mode)


def split_local(data: Dict[str, Any],
                local_keys: Iterable[str]) -> Dict[str, Any]:
    """
    Return portable data with local-only fields as LOCAL_DEFAULTS.

    :param data: dict, full local record
    :param local_keys: iterable of str, host-specific field names

    :return: dict, portable record with a LOCAL_DEFAULTS sub-dict
    :rtype: dict
    """
    local_keys = set(local_keys)
    out = {k: v for k, v in data.items() if k not in local_keys}
    defaults = {k: data[k] for k in local_keys
                if k in data and k != NEEDS_SETUP}
    out[LOCAL_DEFAULTS] = defaults
    return out


def merge_local(incoming: Dict[str, Any], existing: Optional[Dict[str, Any]],
                local_keys: Iterable[str]) -> Dict[str, Any]:
    """
    Combine incoming portable data with this server's local-only fields.

    New records take the other server's values as defaults and are
    flagged as needing local setup.

    :param incoming: dict, portable record (may contain LOCAL_DEFAULTS)
    :param existing: dict or None, current local record
    :param local_keys: iterable of str, host-specific field names

    :return: dict, record to store locally
    :rtype: dict
    """
    record = {k: v for k, v in incoming.items() if k != LOCAL_DEFAULTS}
    if existing is None:
        record.update(dict(incoming.get(LOCAL_DEFAULTS) or dict()))
        record[NEEDS_SETUP] = True
        return record
    for name in local_keys:
        if name in existing:
            record[name] = existing[name]
    return record


# =============================================================================
# Define adapter base class
# =============================================================================
class Adapter:
    """Base class for one syncable data category."""

    # category id (used in URLs, config and journal file names)
    name = ''
    # short label for the UI
    label = ''
    # longer explanation for the UI
    description = ''
    # whether the category is enabled for a new peer
    default_enabled = True
    # whether deletions are applied (derived data never deletes)
    deletes = True
    # whether records can be created that need host-specific setup
    needs_setup = False
    # whether the category is handled by the task-data sync task
    task_data = False

    def export(self, ctx: SyncContext) -> Dict[str, Rec]:
        """
        Export all local records of this category.

        :param ctx: SyncContext

        :return: dict key -> Rec
        :rtype: dict
        """
        raise NotImplementedError

    def apply(self, ctx: SyncContext, upserts: Dict[str, Any],
              deletes: List[str]) -> Dict[str, str]:
        """
        Write incoming records and delete removed ones.

        :param ctx: SyncContext
        :param upserts: dict key -> portable record data
        :param deletes: list of keys to delete

        :return: dict key -> error message for records that failed
        :rtype: dict
        """
        raise NotImplementedError

    def load(self, ctx: SyncContext, keys: Iterable[str]) -> Dict[str, Any]:
        """
        Return record data for specific keys.

        :param ctx: SyncContext
        :param keys: iterable of str

        :return: dict key -> data
        :rtype: dict
        """
        records = self.export(ctx)
        return {k: records[k].data for k in keys if k in records}

    def merge(self, key: str, local: Any, remote: Any) -> Optional[Any]:
        """
        Merge two diverged versions (None when not mergeable).

        :param key: str, record key
        :param local: Any, local data
        :param remote: Any, remote data

        :return: merged data or None
        :rtype: Any
        """
        return None


# =============================================================================
# Define user adapters
# =============================================================================
class UsersAdapter(Adapter):
    """Accounts in admin/general/users.yaml (except the root admin)."""

    name = 'users'
    label = 'Users'
    description = ('Accounts: password hashes, groups, instruments, names '
                   'and emails. The root (setup) admin is never synced.')

    def export(self, ctx: SyncContext) -> Dict[str, Rec]:
        ts = mtime(auth.USERS_FILE)
        out = dict()
        for username, info in auth.load_users().items():
            if username == ctx.root or not isinstance(info, dict):
                continue
            data = {k: v for k, v in info.items() if k not in USER_VOLATILE}
            # emails identify a person: the same email on two usernames
            # is reported as a duplicate
            emails = list(info.get('emails') or [])
            emails.append(info.get('primary_email') or '')
            ident = {f'email:{str(e).strip().lower()}' for e in emails
                     if str(e).strip()}
            out[make_key(username)] = Rec(data, ts, sorted(ident),
                                          f'user {username}')
        return out

    def apply(self, ctx: SyncContext, upserts: Dict[str, Any],
              deletes: List[str]) -> Dict[str, str]:
        errors = dict()
        users = auth.load_users()
        for key, data in upserts.items():
            username = split_key(key, 1)[0]
            if username == ctx.root or not _SAFE_NAME.match(username):
                errors[key] = 'refused (root or invalid username)'
                continue
            local = users.get(username) or dict()
            record = dict(data)
            for name in USER_VOLATILE:
                if name in local:
                    record[name] = local[name]
            users[username] = record
        for key in deletes:
            username = split_key(key, 1)[0]
            if username == ctx.root:
                errors[key] = 'refused (root)'
                continue
            users.pop(username, None)
        auth.save_users(users)
        return errors


class UserFilesAdapter(Adapter):
    """Per-user files (links, notes, calendar, todo, prefs, favourites)."""

    name = 'user_data'
    label = 'Per-user data'
    description = ('Each user\'s links, notes, calendar, todo list, '
                   'preferences, pins, favourite objects and basket.')

    @staticmethod
    def _path(username: str, rel: str) -> Path:
        # basket_funcs keeps its own users directory
        if rel == 'basket.json':
            return basket_funcs.users_dir() / username / rel
        return Path(user_data.USERS_DIR) / username / rel

    @staticmethod
    def _check(username: str, rel: str) -> None:
        safe_name(username)
        if rel in USER_FILES:
            return
        parts = rel.split('/')
        if len(parts) == 2 and parts[0] == 'notes':
            if parts[1].endswith('.md'):
                safe_name(parts[1])
                return
        raise ValueError(f'Unsupported user file: {rel!r}')

    def export(self, ctx: SyncContext) -> Dict[str, Rec]:
        out = dict()
        for username in auth.load_users():
            if username == ctx.root or not _SAFE_NAME.match(username):
                continue
            paths = [(rel, self._path(username, rel)) for rel in USER_FILES]
            notes_dir = self._path(username, 'notes')
            if notes_dir.is_dir():
                for note in sorted(notes_dir.glob('*.md')):
                    paths.append((f'notes/{note.name}', note))
            for rel, path in paths:
                if not path.is_file():
                    continue
                text = path.read_text(encoding='utf-8', errors='replace')
                out[make_key(username, rel)] = Rec(text, mtime(path), (),
                                                   f'{username}: {rel}')
        return out

    def apply(self, ctx: SyncContext, upserts: Dict[str, Any],
              deletes: List[str]) -> Dict[str, str]:
        errors = dict()
        for key, text in upserts.items():
            username, rel = split_key(key, 2)
            try:
                self._check(username, rel)
            except ValueError as exc:
                errors[key] = str(exc)
                continue
            if username == ctx.root:
                errors[key] = 'refused (root)'
                continue
            write_text(self._path(username, rel), str(text))
        for key in deletes:
            username, rel = split_key(key, 2)
            try:
                self._check(username, rel)
            except ValueError as exc:
                errors[key] = str(exc)
                continue
            if username != ctx.root:
                self._path(username, rel).unlink(missing_ok=True)
        return errors


class ApiTokensAdapter(Adapter):
    """Personal API tokens (one per user)."""

    name = 'api_tokens'
    label = 'User API tokens'
    description = ('Personal API tokens so scripts work against either '
                   'server. Share/download links are host-local and never '
                   'synced.')
    default_enabled = False

    def export(self, ctx: SyncContext) -> Dict[str, Rec]:
        out = dict()
        with api_tokens._lock:
            tokens = api_tokens._load()
        for token, info in tokens.items():
            username = str(info.get('username') or '')
            if not username or username == ctx.root:
                continue
            data = dict(info)
            data['token'] = token
            out[make_key(username)] = Rec(data, parse_ts(
                info.get('created_at')), (), f'token for {username}')
        return out

    def apply(self, ctx: SyncContext, upserts: Dict[str, Any],
              deletes: List[str]) -> Dict[str, str]:
        errors = dict()
        with api_tokens._lock:
            tokens = api_tokens._load()
            for key in list(upserts) + list(deletes):
                username = split_key(key, 1)[0]
                if username == ctx.root:
                    errors[key] = 'refused (root)'
                    continue
                # one token per user: drop the old one first
                tokens = {t: i for t, i in tokens.items()
                          if i.get('username') != username}
                data = upserts.get(key)
                if data is None:
                    continue
                token = str(data.get('token') or '')
                if not re.fullmatch(r'[0-9a-f]{64}', token):
                    errors[key] = 'invalid token format'
                    continue
                info = {k: v for k, v in data.items() if k != 'token'}
                info['username'] = username
                tokens[token] = info
            api_tokens._save(tokens)
        return errors


# =============================================================================
# Define science group / run id / instrument adapters
# =============================================================================
class ScienceGroupsAdapter(Adapter):
    """Science groups per instrument."""

    name = 'science_groups'
    label = 'Science groups'
    description = 'Science group membership and RUN ID assignments.'

    def export(self, ctx: SyncContext) -> Dict[str, Rec]:
        out = dict()
        for inst in instruments():
            ts = mtime(auth._sci_groups_file(inst))
            for group, info in auth.load_science_groups(inst).items():
                out[make_key(inst, group)] = Rec(info, ts, (),
                                                 f'{inst}: {group}')
        return out

    def apply(self, ctx: SyncContext, upserts: Dict[str, Any],
              deletes: List[str]) -> Dict[str, str]:
        errors = dict()
        known = set(instruments())
        changes = _group_by_first(upserts, deletes, 2, known, errors)
        for inst, (ups, dels) in changes.items():
            groups = auth.load_science_groups(inst)
            for parts, data in ups:
                groups[parts[1]] = data
            for parts in dels:
                groups.pop(parts[1], None)
            auth.save_science_groups(inst, groups)
        return errors


class RunIdsAdapter(Adapter):
    """RUN ID catalogue (PI and comment per RUN ID)."""

    name = 'run_ids'
    label = 'RUN ID catalogues'
    description = 'PI names and comments for every RUN ID.'

    def export(self, ctx: SyncContext) -> Dict[str, Rec]:
        out = dict()
        for inst in instruments():
            path = ctx.ari_dir / 'apero-assets' / 'run_ids'
            ts = mtime(path / f'{inst.lower()}.json')
            records = run_ids.update_catalog(ctx.ari_dir, inst)
            for run_id, info in records.items():
                out[make_key(inst, run_id)] = Rec(info, ts, (),
                                                  f'{inst}: {run_id}')
        return out

    def apply(self, ctx: SyncContext, upserts: Dict[str, Any],
              deletes: List[str]) -> Dict[str, str]:
        errors = dict()
        known = set(instruments())
        changes = _group_by_first(upserts, deletes, 2, known, errors)
        for inst, (ups, dels) in changes.items():
            # same lock + atomic write as the RUN ID admin page
            with run_ids._catalog_transaction(ctx.ari_dir, inst) as records:
                for parts, data in ups:
                    records[parts[1]] = data
                for parts in dels:
                    records.pop(parts[1], None)
        return errors


class InstrumentDataAdapter(Adapter):
    """Instrument calendars and links (admin portal)."""

    name = 'instrument_data'
    label = 'Instrument calendars and links'
    description = ('Admin-managed instrument calendar events, ICS feed '
                   'definitions and link collections.')

    def export(self, ctx: SyncContext) -> Dict[str, Rec]:
        out = dict()
        for inst in instruments():
            cal_path = Path(user_data.INSTRUMENTS_DIR) / f'{inst}_calendar.yaml'
            if cal_path.exists():
                ts = mtime(cal_path)
                cal = user_data.load_instrument_calendar(inst)
                for event in cal.get('events', []):
                    # ICS events are re-derived from the feeds on each server
                    if event.get('ics_feed_id') or not event.get('id'):
                        continue
                    label = f'{inst}: event {event.get("title", "")}'
                    out[make_key(inst, 'event', event['id'])] = Rec(
                        event, ts, (), label)
                meta = {k: v for k, v in cal.items() if k != 'events'}
                out[make_key(inst, 'calendar_meta', '')] = Rec(
                    meta, ts, (), f'{inst}: calendar feeds/settings')
            link_path = Path(user_data.INSTRUMENTS_DIR) / f'{inst}_links.yaml'
            if link_path.exists():
                ts = mtime(link_path)
                links = user_data.load_instrument_links(inst)
                meta = {k: v for k, v in links.items() if k != 'links'}
                out[make_key(inst, 'links_meta', '')] = Rec(
                    meta, ts, (), f'{inst}: link sections')
                for section, items in (links.get('links') or {}).items():
                    for name, link in (items or {}).items():
                        key = make_key(inst, 'link', json.dumps([section,
                                                                 name]))
                        out[key] = Rec(link, ts, (),
                                       f'{inst}: link {section}/{name}')
        return out

    def apply(self, ctx: SyncContext, upserts: Dict[str, Any],
              deletes: List[str]) -> Dict[str, str]:
        errors = dict()
        known = set(instruments())
        changes = _group_by_first(upserts, deletes, 3, known, errors)
        for inst, (ups, dels) in changes.items():
            cal = user_data.load_instrument_calendar(inst)
            links = user_data.load_instrument_links(inst)
            events = {e.get('id'): e for e in cal.get('events', [])}
            items = [(p, d) for p, d in ups] + [(p, None) for p in dels]
            for parts, data in items:
                kind, ident = parts[1], parts[2]
                if kind == 'event':
                    if data is None:
                        events.pop(ident, None)
                    else:
                        events[ident] = data
                elif kind == 'calendar_meta' and data is not None:
                    cal.update({k: v for k, v in data.items()
                                if k != 'events'})
                elif kind == 'links_meta' and data is not None:
                    links.update({k: v for k, v in data.items()
                                  if k != 'links'})
                elif kind == 'link':
                    section, name = json.loads(ident)
                    sect = links.setdefault('links', dict())
                    if data is None:
                        sect.get(section, dict()).pop(name, None)
                    else:
                        sect.setdefault(section, dict())[name] = data
            cal['events'] = list(events.values())
            user_data.save_instrument_calendar(inst, cal)
            user_data.save_instrument_links(inst, links)
        return errors


# =============================================================================
# Define shared annotation adapters
# =============================================================================
class AstrometricsAdapter(Adapter):
    """Astrometric catalogue YAML files and their edit history."""

    name = 'astrometrics'
    label = 'Astrometrics catalogue + history'
    description = ('Verified / pending / rejected astrometric entries and '
                   'the per-object edit history (history is merged, never '
                   'overwritten).')

    @staticmethod
    def _root(ctx: SyncContext) -> Path:
        return ctx.ari_dir / 'apero-assets' / 'astrometrics'

    def export(self, ctx: SyncContext) -> Dict[str, Rec]:
        root = self._root(ctx)
        out = dict()
        for status in ASTROM_STATUS:
            folder = root / status if status else root
            if not folder.is_dir():
                continue
            for path in sorted(folder.glob('*.yaml')):
                key = make_key('entry', path.stem)
                # first status in ASTROM_STATUS order wins on duplicates
                if path.name.startswith('.') or key in out:
                    continue
                data = dict(status=status, text=path.read_text(
                    encoding='utf-8', errors='replace'))
                out[key] = Rec(data, mtime(path), (),
                               f'{path.stem} ({status or "legacy"})')
        hist = root / '.history'
        if hist.is_dir():
            for path in sorted(hist.glob('*.jsonl')):
                lines = path.read_text(encoding='utf-8').splitlines()
                lines = [ln for ln in lines if ln.strip()]
                out[make_key('history', path.name)] = Rec(
                    lines, mtime(path), (), f'history {path.stem}')
        return out

    def merge(self, key: str, local: Any, remote: Any) -> Optional[Any]:
        if split_key(key, 2)[0] != 'history':
            return None
        # history is append-only: keep the union, ordered by timestamp
        seen = dict()
        for line in list(local or []) + list(remote or []):
            seen.setdefault(line, None)

        def _order(line: str) -> str:
            try:
                return str(json.loads(line).get('timestamp') or '')
            except ValueError:
                return ''

        return sorted(seen, key=_order)

    def apply(self, ctx: SyncContext, upserts: Dict[str, Any],
              deletes: List[str]) -> Dict[str, str]:
        errors = dict()
        root = self._root(ctx)
        for key in list(upserts) + list(deletes):
            try:
                kind, name = split_key(key, 2)
                safe_name(name)
            except ValueError as exc:
                errors[key] = str(exc)
                continue
            data = upserts.get(key)
            if kind == 'history':
                path = root / '.history' / name
                if data is None:
                    path.unlink(missing_ok=True)
                elif name.endswith('.jsonl'):
                    write_text(path, '\n'.join(data) + '\n')
                continue
            if kind != 'entry':
                errors[key] = f'unknown kind {kind!r}'
                continue
            status = '' if data is None else str(data.get('status') or '')
            if status not in ASTROM_STATUS:
                errors[key] = f'unknown status {status!r}'
                continue
            # an entry lives in exactly one status folder
            for other in ASTROM_STATUS:
                folder = root / other if other else root
                if data is None or other != status:
                    (folder / f'{name}.yaml').unlink(missing_ok=True)
            if data is not None:
                folder = root / status if status else root
                write_text(folder / f'{name}.yaml', str(data.get('text')))
        return errors


def _history_identity(line: str) -> str:
    """
    Return the identity of a rejection-history line (ignoring resolve state).

    :param line: str, one JSONL line

    :return: str, identity (the raw line when it cannot be parsed)
    :rtype: str
    """
    try:
        rec = json.loads(line)
    except ValueError:
        return line
    if not isinstance(rec, dict):
        return line
    parts = [rec.get(k) for k in ('timestamp', 'user', 'instrument',
                                  'action', 'identifier',
                                  'previous_identifier')]
    return json.dumps(parts, default=str)


class RejectionListAdapter(Adapter):
    """APERO rejection lists (reject.csv per asset dir) and their history."""

    name = 'rejection_list'
    label = 'Rejection lists + history'
    description = ('Rows of every apero-assets/<instrument>/reject/'
                   'reject.csv and the shared rejection-list history '
                   '(history is merged, never overwritten).')
    # history file and lock under apero-assets
    HISTORY = ('.rejection_history', 'rejection_list.jsonl')
    HISTORY_LOCK = 'rejection_list.lock'

    @staticmethod
    def _mod():
        from apero.core import drs_rejection
        return drs_rejection

    @staticmethod
    def _assets(ctx: SyncContext) -> Path:
        return ctx.ari_dir / 'apero-assets'

    def _csv(self, ctx: SyncContext, asset_dir: str) -> Path:
        mod = self._mod()
        return (self._assets(ctx) / safe_name(asset_dir) / mod.REJECT_SUBDIR
                / mod.REJECT_CSV)

    def _lock(self, path: Path):
        mod = self._mod()
        return mod._FileLock(str(path.parent / mod.LOCK_SUBDIR
                                 / 'reject.lock'))

    def _read(self, path: Path) -> List[Dict[str, Any]]:
        df = self._mod()._read_csv(str(path))
        # to_json maps NaN -> null and numpy scalars -> plain JSON types
        return json.loads(df.to_json(orient='records'))

    def export(self, ctx: SyncContext) -> Dict[str, Rec]:
        mod = self._mod()
        out = dict()
        pattern = f'*/{mod.REJECT_SUBDIR}/{mod.REJECT_CSV}'
        for path in sorted(self._assets(ctx).glob(pattern)):
            asset_dir = path.parent.parent.name
            if not _SAFE_NAME.match(asset_dir):
                continue
            ts_file = mtime(path)
            for row in self._read(path):
                ident = str(row.get(mod.ID_COLUMN) or '')
                ts = max_ts(row.get('DATE_ADDED'),
                            row.get('LAST_UPDATE')) or ts_file
                out[make_key('row', asset_dir, ident)] = Rec(
                    row, ts, (), f'{asset_dir}: {ident}')
        hist = self._assets(ctx).joinpath(*self.HISTORY)
        if hist.is_file():
            lines = [ln for ln in hist.read_text(encoding='utf-8')
                     .splitlines() if ln.strip()]
            out[make_key('history', '', '')] = Rec(
                lines, mtime(hist), (), 'rejection-list history')
        return out

    def merge(self, key: str, local: Any, remote: Any) -> Optional[Any]:
        if split_key(key, 3)[0] != 'history':
            return None
        # union by record identity; a resolved copy beats an unresolved one
        merged = dict()
        for line in list(local or []) + list(remote or []):
            ident = _history_identity(line)
            current = merged.get(ident)
            if current is None or ('"resolved": true' in line
                                   and '"resolved": true' not in current):
                merged[ident] = line

        def _order(line: str) -> str:
            try:
                return str(json.loads(line).get('timestamp') or '')
            except (ValueError, AttributeError):
                return ''

        return sorted(merged.values(), key=_order)

    def apply(self, ctx: SyncContext, upserts: Dict[str, Any],
              deletes: List[str]) -> Dict[str, str]:
        import pandas as pd

        mod = self._mod()
        errors = dict()
        rows = dict()
        for key in list(upserts) + list(deletes):
            try:
                kind, asset_dir, ident = split_key(key, 3)
            except ValueError as exc:
                errors[key] = str(exc)
                continue
            if kind == 'history':
                self._apply_history(ctx, upserts.get(key))
                continue
            if kind != 'row' or not _SAFE_NAME.match(asset_dir):
                errors[key] = f'invalid key {key!r}'
                continue
            rows.setdefault(asset_dir, []).append((ident, upserts.get(key)))
        for asset_dir, changes in rows.items():
            path = self._csv(ctx, asset_dir)
            path.parent.mkdir(parents=True, exist_ok=True)
            with self._lock(path):
                df = mod._read_csv(str(path))
                drop = {ident for ident, _ in changes}
                keep = ~df[mod.ID_COLUMN].astype(str).isin(drop)
                new = [row for _, row in changes if row is not None]
                frames = [df[keep]]
                if new:
                    frames.append(pd.DataFrame(new, columns=mod.CSV_COLUMNS))
                merged = pd.concat(frames, ignore_index=True)
                mod._write_csv(str(path), merged)
        return errors

    def _apply_history(self, ctx: SyncContext,
                       lines: Optional[List[str]]) -> None:
        mod = self._mod()
        path = self._assets(ctx).joinpath(*self.HISTORY)
        with mod._FileLock(str(path.parent / self.HISTORY_LOCK)):
            if lines is None:
                path.unlink(missing_ok=True)
            else:
                write_text(path, '\n'.join(lines) + '\n')


class ChecksPolicyAdapter(Adapter):
    """APERO checks policy (ignored / override-allowed / excluded obsdirs)."""

    name = 'checks_policy'
    label = 'APERO checks policy'
    description = ('Ignored checks, checks that allow overrides and '
                   'excluded observation directories. The checks root path '
                   'stays local.')
    # policy keys synced as one record each (excluded_obsdirs per instrument)
    LIST_KEYS = ('ignored_checks', 'override_allowed')

    def export(self, ctx: SyncContext) -> Dict[str, Rec]:
        path = apero_checks.config_path(ctx.ari_dir)
        if not path.exists():
            return dict()
        ts = mtime(path)
        cfg = apero_checks.load_config(ctx.ari_dir)
        out = dict()
        for name in self.LIST_KEYS:
            if name in cfg:
                out[make_key(name, '')] = Rec(sorted(cfg[name] or []), ts, (),
                                              name)
        excluded = cfg.get('excluded_obsdirs') or dict()
        for inst, obsdirs in excluded.items():
            out[make_key('excluded_obsdirs', inst)] = Rec(
                sorted(obsdirs or []), ts, (), f'excluded obsdirs {inst}')
        return out

    def apply(self, ctx: SyncContext, upserts: Dict[str, Any],
              deletes: List[str]) -> Dict[str, str]:
        errors = dict()
        # copy: load_config returns the shared cached dict
        cfg = json.loads(json.dumps(apero_checks.load_config(ctx.ari_dir)))
        for key in list(upserts) + list(deletes):
            name, inst = split_key(key, 2)
            value = upserts.get(key)
            if name in self.LIST_KEYS:
                if value is None:
                    cfg.pop(name, None)
                else:
                    cfg[name] = list(value)
            elif name == 'excluded_obsdirs':
                section = cfg.setdefault('excluded_obsdirs', dict())
                if value is None:
                    section.pop(inst, None)
                else:
                    section[inst] = list(value)
            else:
                errors[key] = f'unknown policy key {name!r}'
        apero_checks.save_config(ctx.ari_dir, cfg)
        return errors


def _shared_profiles(base: Path, filename: str) -> List[str]:
    """
    List profile ids under shared/ that contain a given file.

    :param base: Path, the ARI data directory used by the module
    :param filename: str, file name inside shared/<profile_id>/

    :return: list of profile ids
    :rtype: list
    """
    shared = base / 'shared'
    if not shared.is_dir():
        return []
    return sorted(p.name for p in shared.iterdir()
                  if (p / filename).is_file() and _SAFE_NAME.match(p.name))


class ObjectCommentsAdapter(Adapter):
    """Object comments per APERO profile."""

    name = 'object_comments'
    label = 'Object comments'
    description = 'Comments left on object pages.'

    def export(self, ctx: SyncContext) -> Dict[str, Rec]:
        out = dict()
        base = object_comments._ari_dir()
        for pid in _shared_profiles(base, 'object_comments.yaml'):
            data = object_comments.load_comments(pid)
            for objname, comments in data.items():
                for comment in comments or []:
                    if not isinstance(comment, dict) or not comment.get('id'):
                        continue
                    ts = max_ts(comment.get('created_at'),
                                comment.get('updated_at'))
                    out[make_key(pid, objname, comment['id'])] = Rec(
                        comment, ts, (), f'{pid}: {objname} comment')
        return out

    def apply(self, ctx: SyncContext, upserts: Dict[str, Any],
              deletes: List[str]) -> Dict[str, str]:
        errors = dict()
        changes = _group_by_first(upserts, deletes, 3, None, errors)
        for pid, (ups, dels) in changes.items():
            data = object_comments.load_comments(pid)
            items = [(p, d) for p, d in ups] + [(p, None) for p in dels]
            for parts, comment in items:
                objname, cid = parts[1], parts[2]
                rows = [c for c in data.get(objname, []) or []
                        if c.get('id') != cid]
                if comment is not None:
                    rows.append(comment)
                rows.sort(key=lambda c: str(c.get('created_at') or ''))
                if rows:
                    data[objname] = rows
                else:
                    data.pop(objname, None)
            object_comments.save_comments(pid, data)
        return errors


class ObjectGroupsAdapter(Adapter):
    """Object groups (and summary-column settings) per APERO profile."""

    name = 'object_groups'
    label = 'Object groups'
    description = 'Named object groups and their summary-table settings.'

    def export(self, ctx: SyncContext) -> Dict[str, Rec]:
        out = dict()
        base = object_groups._ari_dir()
        for pid in _shared_profiles(base, 'object_groups.yaml'):
            path = base / 'shared' / pid / 'object_groups.yaml'
            ts = mtime(path)
            data = object_groups._load_groups_data(pid)
            for group in data.get('groups', []):
                name = str(group.get('name') or '')
                if name:
                    out[make_key(pid, 'group', name)] = Rec(
                        group, ts, (), f'{pid}: group {name}')
            settings = {k: v for k, v in data.items() if k != 'groups'}
            out[make_key(pid, 'settings', '')] = Rec(
                settings, ts, (), f'{pid}: group settings')
        return out

    def apply(self, ctx: SyncContext, upserts: Dict[str, Any],
              deletes: List[str]) -> Dict[str, str]:
        errors = dict()
        changes = _group_by_first(upserts, deletes, 3, None, errors)
        for pid, (ups, dels) in changes.items():
            data = object_groups._load_groups_data(pid)
            groups = {g.get('name'): g for g in data.get('groups', [])}
            items = [(p, d) for p, d in ups] + [(p, None) for p in dels]
            for parts, value in items:
                if parts[1] == 'settings' and value is not None:
                    data.update({k: v for k, v in value.items()
                                 if k != 'groups'})
                elif parts[1] == 'group' and value is None:
                    groups.pop(parts[2], None)
                elif parts[1] == 'group':
                    groups[parts[2]] = value
            data['groups'] = list(groups.values())
            object_groups._save_groups_data(pid, data)
        return errors


class IssuesAdapter(Adapter):
    """Monitor-portal issues (keyed by a sync uid, local numeric ids)."""

    name = 'issues'
    label = 'Issues'
    description = ('Monitor-portal issues. Numeric issue ids are local to '
                   'each server; issues are matched by a sync uid.')

    def export(self, ctx: SyncContext) -> Dict[str, Rec]:
        out = dict()
        path = ctx.ari_dir / 'shared' / 'issues.yaml'
        ts_file = mtime(path)
        with issues._LOCK:
            rows = issues._load(ctx.ari_dir)
            # numeric ids collide across servers: give each issue a uid
            missing = [r for r in rows if not r.get('sync_uid')]
            for row in missing:
                row['sync_uid'] = uuid.uuid4().hex
            if missing:
                issues._save(ctx.ari_dir, rows)
        for row in rows:
            data = {k: v for k, v in row.items() if k != 'id'}
            notes_ts = [n.get('created_at') for n in row.get('notes') or []
                        if isinstance(n, dict)]
            ts = max_ts(row.get('created_at'), row.get('updated_at'),
                        *notes_ts) or ts_file
            label = f'issue #{row.get("id")}: {row.get("title") or ""}'
            out[make_key(row['sync_uid'])] = Rec(data, ts, (), label)
        return out

    def apply(self, ctx: SyncContext, upserts: Dict[str, Any],
              deletes: List[str]) -> Dict[str, str]:
        with issues._LOCK:
            rows = issues._load(ctx.ari_dir)
            by_uid = {r.get('sync_uid'): r for r in rows}
            next_id = max([int(r.get('id') or 0) for r in rows] + [0]) + 1
            for key, data in upserts.items():
                uid = split_key(key, 1)[0]
                current = by_uid.get(uid)
                record = dict(data)
                record['sync_uid'] = uid
                if current is not None:
                    record['id'] = current.get('id')
                    current.clear()
                    current.update(record)
                else:
                    record['id'] = next_id
                    next_id += 1
                    rows.append(record)
                    by_uid[uid] = record
            gone = {split_key(k, 1)[0] for k in deletes}
            rows = [r for r in rows if r.get('sync_uid') not in gone]
            issues._save(ctx.ari_dir, rows)
        return dict()


class KnownErrorsAdapter(Adapter):
    """Known processing errors (uuid ids, updated_at timestamps)."""

    name = 'known_errors'
    label = 'Known errors'
    description = 'The known-errors catalogue used by the monitor portal.'

    def export(self, ctx: SyncContext) -> Dict[str, Rec]:
        out = dict()
        for row in known_errors.list_known_errors_raw():
            ts = max_ts(row.get('updated_at'), row.get('date_reported'))
            out[make_key(row['id'])] = Rec(row, ts, (),
                                           f'known error {row.get("title")}')
        return out

    def apply(self, ctx: SyncContext, upserts: Dict[str, Any],
              deletes: List[str]) -> Dict[str, str]:
        errors = dict()
        for key, data in upserts.items():
            error_id = split_key(key, 1)[0]
            try:
                safe_name(error_id)
            except ValueError as exc:
                errors[key] = str(exc)
                continue
            row = dict(data)
            row['id'] = error_id
            known_errors.write_known_error_raw(row)
        for key in deletes:
            error_id = split_key(key, 1)[0]
            if _SAFE_NAME.match(error_id):
                known_errors.delete_known_error(error_id)
        return errors


# =============================================================================
# Define admin configuration adapters
# =============================================================================
class DbAccessAdapter(Adapter):
    """User database access rules per profile."""

    name = 'db_access'
    label = 'User DB access rules'
    description = 'Which groups may query which tables/columns per profile.'

    def export(self, ctx: SyncContext) -> Dict[str, Rec]:
        out = dict()
        ts_file = mtime(auth.DB_ACCESS_FILE)
        for inst, profiles in (auth.load_db_access() or {}).items():
            for pid, rule in (profiles or {}).items():
                ts = parse_ts(rule.get('updated_at')) or ts_file
                out[make_key(inst, pid)] = Rec(rule, ts, (), f'{inst}/{pid}')
        return out

    def apply(self, ctx: SyncContext, upserts: Dict[str, Any],
              deletes: List[str]) -> Dict[str, str]:
        data = auth.load_db_access() or dict()
        for key, rule in upserts.items():
            inst, pid = split_key(key, 2)
            data.setdefault(inst, dict())[pid] = rule
        for key in deletes:
            inst, pid = split_key(key, 2)
            data.get(inst, dict()).pop(pid, None)
        auth.save_db_access(data)
        return dict()


class VaultAdapter(Adapter):
    """Shared admin vault entries."""

    name = 'vault'
    label = 'Vault'
    description = 'Shared secret/credential notes from the admin vault.'
    default_enabled = False

    def export(self, ctx: SyncContext) -> Dict[str, Rec]:
        out = dict()
        for entry in vault_store._load_raw().get('entries', []):
            if not entry.get('id'):
                continue
            ts = max_ts(entry.get('created_at'), entry.get('modified_at'))
            out[make_key(entry['id'])] = Rec(entry, ts, (),
                                             f'vault: {entry.get("title")}')
        return out

    def apply(self, ctx: SyncContext, upserts: Dict[str, Any],
              deletes: List[str]) -> Dict[str, str]:
        raw = vault_store._load_raw()
        entries = {e.get('id'): e for e in raw.get('entries', [])}
        for key, entry in upserts.items():
            entries[split_key(key, 1)[0]] = entry
        for key in deletes:
            entries.pop(split_key(key, 1)[0], None)
        raw['entries'] = list(entries.values())
        vault_store._save_raw(raw)
        return dict()


class AperoProfilesAdapter(Adapter):
    """APERO profiles without disk paths (and without enabled state)."""

    name = 'apero_profiles'
    label = 'APERO profiles'
    description = ('Profile settings including database credentials. Data '
                   'paths and the enabled/disabled state stay local; new '
                   'profiles arrive disabled until paths are set here.')
    needs_setup = True

    def export(self, ctx: SyncContext) -> Dict[str, Rec]:
        out = dict()
        ts = mtime(auth.APERO_PROFILES_FILE)
        kwargs = dict(hydrate=False, include_temporary=True)
        for inst, profiles in auth.load_apero_profiles(**kwargs).items():
            for pid, cfg in (profiles or {}).items():
                if not isinstance(cfg, dict) or cfg.get('temporary'):
                    continue
                data = {k: v for k, v in cfg.items()
                        if k not in PROFILE_LOCAL
                        and not str(k).upper().startswith('PATH')}
                out[make_key(inst, pid)] = Rec(data, ts, (), f'{inst}/{pid}')
        return out

    def apply(self, ctx: SyncContext, upserts: Dict[str, Any],
              deletes: List[str]) -> Dict[str, str]:
        kwargs = dict(hydrate=False, include_temporary=True)
        profiles = auth.load_apero_profiles(**kwargs)
        for key, data in upserts.items():
            inst, pid = split_key(key, 2)
            current = profiles.setdefault(inst, dict()).get(pid)
            record = dict(data)
            if current is None:
                # paths are host-specific: arrive disabled, flagged
                record['paths'] = dict()
                record['disabled'] = True
                record[NEEDS_SETUP] = True
            else:
                for name, value in current.items():
                    local = (name in PROFILE_LOCAL
                             or str(name).upper().startswith('PATH'))
                    if local:
                        record[name] = value
            profiles[inst][pid] = record
        for key in deletes:
            inst, pid = split_key(key, 2)
            current = profiles.get(inst, dict()).get(pid)
            if isinstance(current, dict) and not current.get('temporary'):
                profiles[inst].pop(pid, None)
        auth.save_apero_profiles(profiles)
        return dict()


class AsyncSettingsAdapter(Adapter):
    """Async task enabled flag and frequency (never paths)."""

    name = 'async_settings'
    label = 'Async task settings'
    description = ('Only the enabled flag and frequency of each async task. '
                   'Sync tasks themselves are never synced.')
    default_enabled = False

    def export(self, ctx: SyncContext) -> Dict[str, Rec]:
        out = dict()
        ts = mtime(auth.ASYNC_TASKS_FILE)
        for scope, rows in auth.load_async_tasks().items():
            for row in rows if isinstance(rows, list) else []:
                task_key = str(row.get('task_key') or '')
                if not task_key or task_key in ASYNC_EXCLUDED:
                    continue
                data = {k: row.get(k) for k in ASYNC_SYNCED}
                out[make_key(scope, task_key)] = Rec(data, ts, (),
                                                     f'{scope}: {task_key}')
        return out

    def apply(self, ctx: SyncContext, upserts: Dict[str, Any],
              deletes: List[str]) -> Dict[str, str]:
        errors = dict()
        tasks = auth.load_async_tasks()
        for key, data in upserts.items():
            scope, task_key = split_key(key, 2)
            if task_key in ASYNC_EXCLUDED:
                continue
            rows = [r for r in tasks.get(scope) or []
                    if r.get('task_key') == task_key]
            if not rows:
                errors[key] = 'task not configured on this server'
                continue
            for name in ASYNC_SYNCED:
                rows[0][name] = data.get(name)
        # deleting a task definition is never propagated
        auth.save_async_tasks(tasks)
        return errors


class EmailAdapter(Adapter):
    """SMTP configuration (use the other server's mail settings)."""

    name = 'email'
    label = 'Email (SMTP) settings'
    description = ('Off: keep this server\'s own SMTP setup. On: use the '
                   'same SMTP account as the other server.')
    default_enabled = False

    def export(self, ctx: SyncContext) -> Dict[str, Rec]:
        path = email_backend._get_email_config_path()
        if not path.exists():
            return dict()
        cfg = email_backend.load_email_config()
        data = {k: v for k, v in cfg.items() if k != 'smtp_password_enc'}
        data['smtp_password'] = email_backend.get_smtp_password(cfg)
        return {make_key('config'): Rec(data, mtime(path), (), 'SMTP')}

    def apply(self, ctx: SyncContext, upserts: Dict[str, Any],
              deletes: List[str]) -> Dict[str, str]:
        for data in upserts.values():
            # save_email_config pops and stores smtp_password itself
            email_backend.save_email_config(dict(data))
        return dict()


# =============================================================================
# Define external-connection adapters
# =============================================================================
class SshKeysAdapter(Adapter):
    """Private SSH keys used for SSHFS mounts and DB tunnels."""

    name = 'ssh_keys'
    label = 'SSH keys'
    description = 'Private keys stored by ARI for SSHFS / tunnels.'
    default_enabled = False

    def export(self, ctx: SyncContext) -> Dict[str, Rec]:
        out = dict()
        folder = sshfs_backend._get_ssh_keys_dir()
        for path in sorted(folder.glob('*.key')):
            out[make_key(path.stem)] = Rec(path.read_text(), mtime(path), (),
                                           f'key {path.stem}')
        return out

    def apply(self, ctx: SyncContext, upserts: Dict[str, Any],
              deletes: List[str]) -> Dict[str, str]:
        errors = dict()
        folder = sshfs_backend._get_ssh_keys_dir()
        for key, text in upserts.items():
            name = split_key(key, 1)[0]
            try:
                safe_name(name)
            except ValueError as exc:
                errors[key] = str(exc)
                continue
            write_text(folder / f'{name}.key', str(text), mode=0o600)
        for key in deletes:
            name = split_key(key, 1)[0]
            if _SAFE_NAME.match(name):
                (folder / f'{name}.key').unlink(missing_ok=True)
        return errors


class SshfsMountsAdapter(Adapter):
    """SSHFS mount definitions (local mount point / ssh alias stay local)."""

    name = 'sshfs_mounts'
    label = 'SSHFS mounts'
    description = ('Mount definitions. The local mount point and SSH host '
                   'alias are set per server (see Local setup).')
    default_enabled = False
    needs_setup = True

    def export(self, ctx: SyncContext) -> Dict[str, Rec]:
        out = dict()
        path = sshfs_backend._get_sshfs_config_path()
        ts = mtime(path)
        for mount in sshfs_backend.load_sshfs_config().get('mounts', []):
            name = str(mount.get('name') or '')
            if name:
                data = split_local(mount, SSHFS_LOCAL)
                out[make_key(name)] = Rec(data, ts, (), f'mount {name}')
        return out

    def apply(self, ctx: SyncContext, upserts: Dict[str, Any],
              deletes: List[str]) -> Dict[str, str]:
        cfg = sshfs_backend.load_sshfs_config()
        mounts = {m.get('name'): m for m in cfg.get('mounts', [])}
        for key, data in upserts.items():
            name = split_key(key, 1)[0]
            record = merge_local(data, mounts.get(name), SSHFS_LOCAL)
            if name not in mounts:
                # never reuse another machine's mount point
                record['local_mount'] = ''
            record['name'] = name
            mounts[name] = record
        for key in deletes:
            mounts.pop(split_key(key, 1)[0], None)
        cfg['mounts'] = list(mounts.values())
        sshfs_backend.save_sshfs_config(cfg)
        return dict()


class DbDefinitionsAdapter(Adapter):
    """Local database and DB SSH tunnel definitions."""

    name = 'db_definitions'
    label = 'Database definitions + DB SSH tunnels'
    description = ('Database Setup entries. SSH alias, local forward port '
                   'and local DB host/port are set per server.')
    default_enabled = False
    needs_setup = True

    def export(self, ctx: SyncContext) -> Dict[str, Rec]:
        out = dict()
        ts = mtime(auth.DB_TUNNELS_FILE)
        data = auth.load_db_tunnels() or dict()
        for name, info in (data.get('tunnels') or {}).items():
            out[make_key('tunnel', name)] = Rec(
                split_local(info, TUNNEL_LOCAL), ts, (), f'tunnel {name}')
        for name, info in (data.get('local_databases') or {}).items():
            out[make_key('local', name)] = Rec(
                split_local(info, LOCALDB_LOCAL), ts, (), f'local db {name}')
        return out

    def apply(self, ctx: SyncContext, upserts: Dict[str, Any],
              deletes: List[str]) -> Dict[str, str]:
        errors = dict()
        data = auth.load_db_tunnels() or dict()
        sections = dict(tunnel='tunnels', local='local_databases')
        local = dict(tunnel=TUNNEL_LOCAL, local=LOCALDB_LOCAL)
        for key in list(upserts) + list(deletes):
            kind, name = split_key(key, 2)
            if kind not in sections:
                errors[key] = f'unknown kind {kind!r}'
                continue
            section = data.setdefault(sections[kind], dict())
            if key in upserts:
                args = [upserts[key], section.get(name), local[kind]]
                section[name] = merge_local(*args)
            else:
                section.pop(name, None)
        auth.save_db_tunnels(data)
        return errors


# =============================================================================
# Define sqlite adapters
# =============================================================================
def _sqlite_rows(con: sqlite3.Connection, table: str) -> List[Dict[str, Any]]:
    """
    Return all rows of a table as dicts.

    :param con: sqlite3 connection
    :param table: str, table name (internal constant)

    :return: list of dict
    :rtype: list
    """
    cur = con.execute(f'SELECT * FROM {table}')
    names = [d[0] for d in cur.description]
    return [dict(zip(names, row)) for row in cur.fetchall()]


def _sqlite_upsert(con: sqlite3.Connection, table: str,
                   row: Dict[str, Any], columns: List[str]) -> None:
    """
    Insert-or-replace a row restricted to known columns.

    :param con: sqlite3 connection
    :param table: str, table name (internal constant)
    :param row: dict, column -> value
    :param columns: list of str, allowed columns

    :return: None
    """
    cols = [c for c in columns if c in row]
    marks = ', '.join('?' for _ in cols)
    sql = f'INSERT OR REPLACE INTO {table} ({", ".join(cols)}) VALUES ({marks})'
    con.execute(sql, [row[c] for c in cols])


def _sqlite_columns(con: sqlite3.Connection, table: str) -> List[str]:
    """
    Return the column names of a table.

    :param con: sqlite3 connection
    :param table: str, table name (internal constant)

    :return: list of str
    :rtype: list
    """
    return [r[1] for r in con.execute(f'PRAGMA table_info({table})')]


class NotificationsAdapter(Adapter):
    """Notifications, direct messages, flags and notification prefs."""

    name = 'notifications'
    label = 'Notifications + messages'
    description = ('In-app notifications, direct messages, message flags '
                   'and per-user notification preferences.')
    default_enabled = False
    # table -> (primary key columns, user columns, timestamp columns)
    TABLES = dict(
        notifications=(('id',), ('username',), ('created_at', 'read_at')),
        messages=(('id',), ('sender', 'recipient'), ('created_at',
                                                     'read_at')),
        message_flags=(('message_id',), ('flagger',), ('flagged_at',)),
        notification_prefs=(('username', 'channel'), ('username',), ()),
    )

    def export(self, ctx: SyncContext) -> Dict[str, Rec]:
        notifications._init_schema()
        out = dict()
        con = notifications._connect()
        try:
            for table, (pkeys, ucols, tcols) in self.TABLES.items():
                for row in _sqlite_rows(con, table):
                    if ctx.root and any(row.get(c) == ctx.root
                                        for c in ucols):
                        continue
                    key = make_key(table, *[row[c] for c in pkeys])
                    ts = max_ts(*[row.get(c) for c in tcols])
                    out[key] = Rec(row, ts, (), f'{table} {key}')
        finally:
            con.close()
        return out

    def apply(self, ctx: SyncContext, upserts: Dict[str, Any],
              deletes: List[str]) -> Dict[str, str]:
        errors = dict()
        notifications._init_schema()
        con = notifications._connect()
        try:
            for key in list(upserts) + list(deletes):
                table = json.loads(key)[0]
                if table not in self.TABLES:
                    errors[key] = f'unknown table {table!r}'
                    continue
                pkeys, ucols, _ = self.TABLES[table]
                parts = split_key(key, 1 + len(pkeys))[1:]
                row = upserts.get(key)
                if row is not None and any(row.get(c) == ctx.root
                                           for c in ucols if ctx.root):
                    errors[key] = 'refused (root)'
                    continue
                if row is None:
                    where = ' AND '.join(f'{c} = ?' for c in pkeys)
                    con.execute(f'DELETE FROM {table} WHERE {where}', parts)
                else:
                    columns = _sqlite_columns(con, table)
                    _sqlite_upsert(con, table, row, columns)
            con.commit()
        finally:
            con.close()
        return errors


class ScheduleAdapter(Adapter):
    """Monitoring schedule database (tasks, entries, settings)."""

    name = 'schedule'
    label = 'Monitoring schedule'
    description = ('Schedule tasks, shift entries, stats visibility and '
                   'instrument schedule settings.')
    default_enabled = False
    # table -> natural key columns (entries get a sync_uid column)
    TABLES = dict(
        schedule_tasks=('instrument', 'name'),
        schedule_entries=('sync_uid',),
        schedule_stats_visibility=('instrument', 'username'),
        schedule_instrument_settings=('instrument', 'key'),
    )

    @staticmethod
    def _connect(ctx: SyncContext) -> sqlite3.Connection:
        con = schedule._connect(ctx.ari_dir)
        # entries only have local autoincrement ids: add a global uid
        cols = _sqlite_columns(con, 'schedule_entries')
        if 'sync_uid' not in cols:
            con.execute('ALTER TABLE schedule_entries ADD COLUMN sync_uid '
                        'TEXT')
        rows = con.execute('SELECT id FROM schedule_entries WHERE sync_uid '
                           'IS NULL').fetchall()
        for row in rows:
            con.execute('UPDATE schedule_entries SET sync_uid = ? WHERE id = ?',
                        (uuid.uuid4().hex, row[0]))
        con.commit()
        return con

    def export(self, ctx: SyncContext) -> Dict[str, Rec]:
        out = dict()
        with schedule._LOCK:
            con = self._connect(ctx)
            try:
                for table, natural in self.TABLES.items():
                    for row in _sqlite_rows(con, table):
                        data = {k: v for k, v in row.items() if k != 'id'}
                        key = make_key(table, *[row[c] for c in natural])
                        ts = max_ts(row.get('created_at'),
                                    row.get('updated_at'))
                        out[key] = Rec(data, ts, (), f'{table} {key}')
            finally:
                con.close()
        return out

    def apply(self, ctx: SyncContext, upserts: Dict[str, Any],
              deletes: List[str]) -> Dict[str, str]:
        errors = dict()
        with schedule._LOCK:
            con = self._connect(ctx)
            try:
                for key in list(upserts) + list(deletes):
                    table = json.loads(key)[0]
                    if table not in self.TABLES:
                        errors[key] = f'unknown table {table!r}'
                        continue
                    natural = self.TABLES[table]
                    parts = split_key(key, 1 + len(natural))[1:]
                    where = ' AND '.join(f'{c} = ?' for c in natural)
                    row = upserts.get(key)
                    if row is None:
                        sql = f'DELETE FROM {table} WHERE {where}'
                        con.execute(sql, parts)
                        continue
                    columns = [c for c in _sqlite_columns(con, table)
                               if c != 'id' and c in row]
                    found = con.execute(f'SELECT 1 FROM {table} WHERE {where}',
                                        parts).fetchone()
                    if found:
                        sets = ', '.join(f'{c} = ?' for c in columns)
                        values = [row[c] for c in columns] + parts
                        con.execute(f'UPDATE {table} SET {sets} WHERE {where}',
                                    values)
                    else:
                        _sqlite_upsert(con, table, row, columns)
                con.commit()
            finally:
                con.close()
        return errors


# =============================================================================
# Define derived task-output adapter
# =============================================================================
class TaskFilesAdapter(Adapter):
    """Derived async-task outputs under tasks/ (file level, sha256)."""

    name = 'task_files'
    label = 'Derived task outputs (tasks/)'
    description = ('Object/observation tables and per-object query results. '
                   'Large and regenerable: synced by its own async task, '
                   'newest file wins, deletions are not propagated.')
    default_enabled = False
    deletes = False
    task_data = True

    @staticmethod
    def _root(ctx: SyncContext) -> Path:
        return ctx.ari_dir / 'tasks'

    @staticmethod
    def _cache_path() -> Path:
        return store.sync_dir() / 'task_files_hashes.json'

    def _check(self, ctx: SyncContext, rel: str) -> Path:
        parts = rel.split('/')
        for part in parts:
            safe_name(part)
        if not rel.endswith('.json'):
            raise ValueError(f'Only .json task outputs are synced: {rel!r}')
        return self._root(ctx).joinpath(*parts)

    def export(self, ctx: SyncContext) -> Dict[str, Rec]:
        root = self._root(ctx)
        if not root.is_dir():
            return dict()
        cache = store.read_json(self._cache_path(), dict())
        new_cache = dict()
        out = dict()
        for path in sorted(root.rglob('*.json')):
            rel = path.relative_to(root).as_posix()
            # skip state/lock/hidden files and anything unsafe
            if any(p.startswith('.') for p in rel.split('/')):
                continue
            try:
                self._check(ctx, rel)
                stat = path.stat()
            except (ValueError, OSError):
                continue
            if stat.st_size > TASK_FILE_MAX_BYTES:
                continue
            sig = [stat.st_size, stat.st_mtime]
            cached = cache.get(rel)
            # re-hash only files whose size/mtime changed
            if cached and cached[:2] == sig:
                digest = cached[2]
            else:
                digest = _file_sha256(path)
            new_cache[rel] = sig + [digest]
            out[make_key(rel)] = Rec(None, stat.st_mtime, (), rel,
                                     digest=digest)
        store.write_json(self._cache_path(), new_cache)
        return out

    def load(self, ctx: SyncContext, keys: Iterable[str]) -> Dict[str, Any]:
        out = dict()
        for key in keys:
            rel = split_key(key, 1)[0]
            path = self._check(ctx, rel)
            if path.is_file():
                out[key] = path.read_text(encoding='utf-8', errors='replace')
        return out

    def apply(self, ctx: SyncContext, upserts: Dict[str, Any],
              deletes: List[str]) -> Dict[str, str]:
        errors = dict()
        for key, text in upserts.items():
            try:
                path = self._check(ctx, split_key(key, 1)[0])
            except ValueError as exc:
                errors[key] = str(exc)
                continue
            write_text(path, str(text))
        return errors


def _file_sha256(path: Path) -> str:
    """
    Hash a file in chunks.

    :param path: Path, file to hash

    :return: str, truncated sha256 hex digest
    :rtype: str
    """
    sha = hashlib.sha256()
    with open(path, 'rb') as fio:
        for chunk in iter(lambda: fio.read(1 << 20), b''):
            sha.update(chunk)
    return sha.hexdigest()[:32]


def text_digest(text: str) -> str:
    """
    Hash text the same way _file_sha256 hashes a utf-8 file.

    :param text: str, file contents

    :return: str, truncated sha256 hex digest
    :rtype: str
    """
    return hashlib.sha256(str(text).encode('utf-8')).hexdigest()[:32]


# =============================================================================
# Define grouping helper
# =============================================================================
def _group_by_first(upserts: Dict[str, Any], deletes: List[str], size: int,
                    allowed: Optional[set], errors: Dict[str, str]
                    ) -> Dict[str, Tuple[list, list]]:
    """
    Group composite keys by their first component (instrument/profile).

    :param upserts: dict key -> data
    :param deletes: list of keys
    :param size: int, number of key components
    :param allowed: set or None, permitted first components
    :param errors: dict, receives key -> error for rejected keys

    :return: dict first -> (list of (parts, data), list of parts)
    :rtype: dict
    """
    out = dict()
    items = [(k, d, False) for k, d in upserts.items()]
    items += [(k, None, True) for k in deletes]
    for key, data, is_delete in items:
        try:
            parts = split_key(key, size)
            safe_name(parts[0])
        except ValueError as exc:
            errors[key] = str(exc)
            continue
        if allowed is not None and parts[0] not in allowed:
            errors[key] = f'unknown instrument {parts[0]!r}'
            continue
        ups, dels = out.setdefault(parts[0], ([], []))
        if is_delete:
            dels.append(parts)
        else:
            ups.append((parts, data))
    return out


# =============================================================================
# Define registry
# =============================================================================
# order matters: users first so per-user data has an owner
ADAPTERS = dict()
for _cls in (UsersAdapter, UserFilesAdapter, ApiTokensAdapter,
             ScienceGroupsAdapter, RunIdsAdapter, InstrumentDataAdapter,
             AstrometricsAdapter, RejectionListAdapter, ChecksPolicyAdapter,
             ObjectCommentsAdapter, ObjectGroupsAdapter,
             IssuesAdapter, KnownErrorsAdapter, DbAccessAdapter, VaultAdapter,
             NotificationsAdapter, ScheduleAdapter, AperoProfilesAdapter,
             AsyncSettingsAdapter, EmailAdapter, SshKeysAdapter,
             SshfsMountsAdapter, DbDefinitionsAdapter, TaskFilesAdapter):
    ADAPTERS[_cls.name] = _cls()


def describe() -> List[Dict[str, Any]]:
    """
    Describe every category for the UI.

    :return: list of dicts (name, label, description, flags)
    :rtype: list
    """
    rows = []
    for adapter in ADAPTERS.values():
        row = dict()
        row['name'] = adapter.name
        row['label'] = adapter.label
        row['description'] = adapter.description
        row['default_enabled'] = adapter.default_enabled
        row['needs_setup'] = adapter.needs_setup
        row['task_data'] = adapter.task_data
        rows.append(row)
    return rows


def default_categories() -> Dict[str, bool]:
    """
    Return the default category toggles for a new peer.

    :return: dict category -> enabled
    :rtype: dict
    """
    return {a.name: a.default_enabled for a in ADAPTERS.values()}


# =============================================================================
# End of code
# =============================================================================
