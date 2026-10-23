#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: server-to-server sync engine.

Change detection
    Each category keeps a local journal ``{key: {h, ts, d, i, l}}`` (hash,
    modification time, deleted flag, identities, label). A scan exports
    the category, compares hashes with the journal and stamps changed
    records with their own timestamp (or the file mtime). Records that
    disappear become tombstones (``d=True``) so deletions propagate.

Planning (three-way, per record)
    ``base`` holds the hash both servers agreed on after the last sync with
    a peer. Compared with base:

    - only the peer changed -> pull
    - only we changed -> push (mirror) / keep local (copy)
    - both changed -> newest wins (mirror) / peer wins (copy), or a merge
      when the category supports it (astrometric history)
    - no shared history and both differ -> conflict (Run tab)
    - a new record whose identity (e.g. email) belongs to another record
      on the other side -> duplicate conflict (Run tab)

    Conflicts are skipped until resolved ('local', 'remote', 'allow' or a
    persistent 'skip').

Created on 2026-10-22

@author: cook
"""
import hashlib
import json
import time
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

from apero_ri.ari_api import server_sync as peer_api
from apero_ri.base import base
from apero_ri.core import auth
from apero_ri.core import notifications
from apero_ri.core import permissions
from apero_ri.core.server_sync import adapters
from apero_ri.core.server_sync import store

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.core.server_sync.engine'
# hash used for tombstones
DELETED = 'DELETED'
# tombstones older than this are forgotten (seconds)
TOMBSTONE_TTL = 180 * 86400.0
# clock skew limits (seconds)
CLOCK_WARN = 60.0
CLOCK_BLOCK = 300.0
# records per fetch/apply request (task files are much larger)
BATCH_RECORDS = 200
BATCH_FILES = 10
# resolutions an admin can give a conflict
RESOLUTIONS = ('local', 'remote', 'skip', 'allow')
# which categories each run kind covers
RUN_KINDS = ('records', 'task_files', 'all')


# =============================================================================
# Define hashing and scanning
# =============================================================================
def normalise(data: Any) -> Any:
    """
    Round-trip data through JSON so both servers hash identical values.

    :param data: Any, record data

    :return: Any, JSON-normalised data
    :rtype: Any
    """
    return json.loads(json.dumps(data, default=str))


def record_hash(data: Any) -> str:
    """
    Hash portable record data (LOCAL_DEFAULTS is ignored).

    :param data: Any, normalised record data

    :return: str, truncated sha256 hex digest
    :rtype: str
    """
    if isinstance(data, dict) and adapters.LOCAL_DEFAULTS in data:
        data = {k: v for k, v in data.items()
                if k != adapters.LOCAL_DEFAULTS}
    raw = json.dumps(data, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()[:32]


def scan(category: str,
         ctx: Optional[adapters.SyncContext] = None) -> Dict[str, Any]:
    """
    Export a category and update its local journal.

    :param category: str, category name
    :param ctx: SyncContext or None

    :return: dict, the updated journal
    :rtype: dict
    """
    ctx = ctx or adapters.SyncContext()
    adapter = adapters.ADAPTERS[category]
    records = adapter.export(ctx)
    now = time.time()
    with store.journal_lock():
        journal = store.load_journal(category)
        for key, rec in records.items():
            if rec.digest is not None:
                digest = rec.digest
            else:
                digest = record_hash(normalise(rec.data))
            old = journal.get(key)
            if old and not old.get('d') and old.get('h') == digest:
                # unchanged: refresh identity/label only
                old['i'] = rec.ident
                old['l'] = rec.label
                continue
            ts = rec.ts if rec.ts is not None else now
            if old:
                # a change is always newer than the version it replaces
                ts = max(ts, float(old.get('ts') or 0) + 0.001)
            entry = dict(h=digest, ts=min(ts, now), d=False, i=rec.ident,
                         l=rec.label)
            journal[key] = entry
        for key, entry in list(journal.items()):
            if key in records:
                continue
            if not entry.get('d'):
                # record vanished locally: keep a tombstone
                entry.update(h=DELETED, ts=now, d=True, i=[])
            elif now - float(entry.get('ts') or 0) > TOMBSTONE_TTL:
                journal.pop(key)
        store.save_journal(category, journal)
    return journal


def manifest(categories: Iterable[str]) -> Dict[str, Dict[str, Any]]:
    """
    Scan categories and return their journals.

    :param categories: iterable of category names

    :return: dict category -> journal
    :rtype: dict
    """
    ctx = adapters.SyncContext()
    out = dict()
    for category in categories:
        if category in adapters.ADAPTERS:
            out[category] = scan(category, ctx)
    return out


def load_records(category: str, keys: Iterable[str]) -> Dict[str, Any]:
    """
    Return normalised record data for keys (used by peer fetch).

    :param category: str, category name
    :param keys: iterable of record keys

    :return: dict key -> data
    :rtype: dict
    """
    adapter = adapters.ADAPTERS[category]
    data = adapter.load(adapters.SyncContext(), list(keys))
    return {k: normalise(v) for k, v in data.items()}


def apply_records(category: str, upserts: Dict[str, Dict[str, Any]],
                  deletes: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
    """
    Apply records received from another server and journal them.

    Journal entries take the sender's hash and timestamp so the change
    is not mistaken for a new local edit on the next scan.

    :param category: str, category name
    :param upserts: dict key -> {'data', 'h', 'ts', 'i', 'l'}
    :param deletes: dict key -> {'ts', 'l'}

    :return: dict key -> error message
    :rtype: dict
    """
    adapter = adapters.ADAPTERS[category]
    ctx = adapters.SyncContext()
    if not adapter.deletes:
        deletes = dict()
    data = {k: v.get('data') for k, v in upserts.items()}
    with store.journal_lock():
        errors = adapter.apply(ctx, data, list(deletes))
        journal = store.load_journal(category)
        for key, entry in upserts.items():
            if key in errors:
                continue
            journal[key] = dict(h=entry.get('h'), ts=entry.get('ts'),
                                d=False, i=entry.get('i') or [],
                                l=entry.get('l') or '')
        for key, entry in deletes.items():
            if key in errors:
                continue
            journal[key] = dict(h=DELETED, ts=entry.get('ts'), d=True,
                                i=[], l=entry.get('l') or '')
        store.save_journal(category, journal)
    return errors


# =============================================================================
# Define planning
# =============================================================================
def _live(entry: Optional[Dict[str, Any]]) -> bool:
    """Return True for an existing, non-deleted journal entry."""
    return bool(entry) and not entry.get('d')


def _newer(local: Dict[str, Any], remote: Dict[str, Any]) -> str:
    """
    Pick the newest side ('local' or 'remote'), deterministic on ties.

    :param local: dict, local journal entry
    :param remote: dict, remote journal entry

    :return: str, 'local' or 'remote'
    :rtype: str
    """
    lts = float(local.get('ts') or 0)
    rts = float(remote.get('ts') or 0)
    if lts != rts:
        return 'local' if lts > rts else 'remote'
    # identical timestamps: both servers make the same choice
    return 'local' if str(local.get('h')) > str(remote.get('h')) else 'remote'


def _identities(journal: Dict[str, Any]) -> Dict[str, str]:
    """
    Map identity string -> key for live records.

    :param journal: dict, a journal

    :return: dict identity -> key
    :rtype: dict
    """
    out = dict()
    for key, entry in journal.items():
        if _live(entry):
            for ident in entry.get('i') or []:
                out.setdefault(ident, key)
    return out


def plan_category(category: str, local: Dict[str, Any],
                  remote: Dict[str, Any], base_hashes: Dict[str, str],
                  mode: str, resolutions: Dict[str, str]) -> Dict[str, Any]:
    """
    Decide what to do with every record of one category.

    :param category: str, category name
    :param local: dict, local journal
    :param remote: dict, remote journal
    :param base_hashes: dict, last agreed hashes with this peer
    :param mode: str, 'mirror' or 'copy'
    :param resolutions: dict key -> resolution for this category

    :return: dict with lists 'pull', 'push', 'merge', 'agree', 'keep',
             'conflicts', 'skipped'
    :rtype: dict
    """
    adapter = adapters.ADAPTERS[category]
    mirror = mode == 'mirror'
    plan = dict(pull=[], push=[], merge=[], agree=[], keep=[], conflicts=[],
                skipped=[])
    local_ids = _identities(local)
    remote_ids = _identities(remote)
    for key in sorted(set(local) | set(remote)):
        lent = local.get(key)
        rent = remote.get(key)
        lhash = lent.get('h') if lent else None
        rhash = rent.get('h') if rent else None
        label = (rent or lent or dict()).get('l') or key
        item = dict(key=key, label=label, local=lent, remote=rent)
        res = resolutions.get(key)
        if res == 'skip':
            plan['skipped'].append(item)
            continue
        if lhash == rhash:
            plan['agree'].append(item)
            continue
        action, reason = _decide(adapter, key, lent, rent,
                                 base_hashes.get(key), mirror)
        # an explicit admin resolution overrides the automatic choice
        if res == 'remote':
            action, reason = 'pull', 'resolved: take remote'
        elif res == 'local':
            action = 'push' if mirror else 'keep'
            reason = 'resolved: keep local'
        # derived categories never propagate deletions
        deleting = ((action == 'pull' and not _live(rent))
                    or (action == 'push' and not _live(lent)))
        if deleting and not adapter.deletes:
            action, reason = 'keep', 'deletions not propagated'
        # duplicates: a new record whose identity exists under another key
        if res != 'allow' and action in ('pull', 'push'):
            dup = _duplicate(key, action, lent, rent, local_ids, remote_ids)
            if dup:
                action, reason = 'conflict', dup
        item['reason'] = reason
        if action == 'conflict':
            item['kind'] = 'duplicate' if 'identity' in reason else 'diverged'
            plan['conflicts'].append(item)
        else:
            plan[action].append(item)
    return plan


def _decide(adapter: adapters.Adapter, key: str,
            lent: Optional[Dict[str, Any]], rent: Optional[Dict[str, Any]],
            base_hash: Optional[str], mirror: bool) -> Tuple[str, str]:
    """
    Three-way decision for one differing record.

    :return: tuple (action, reason) with action in pull/push/keep/merge/
             conflict
    :rtype: tuple
    """
    lhash = lent.get('h') if lent else None
    rhash = rent.get('h') if rent else None
    can_merge = (_live(lent) and _live(rent)
                 and adapter.merge(key, [], []) is not None)
    if base_hash is None:
        # no shared history with this peer for this record
        if not _live(lent) and not _live(rent):
            return 'keep', 'deleted on one side only'
        if lent is None:
            return 'pull', 'new on remote'
        if rent is None:
            if mirror:
                return 'push', 'new here'
            return 'keep', 'local only (copy mode)'
        if can_merge:
            return 'merge', 'merged (both sides kept)'
        if _live(lent) and _live(rent):
            return 'conflict', 'differs on both servers (first sync)'
        if not mirror:
            return 'pull', 'remote is the source (copy mode)'
        side = _newer(lent, rent)
        return ('push' if side == 'local' else 'pull'), f'newest is {side}'
    local_changed = lhash != base_hash
    remote_changed = rhash != base_hash
    if remote_changed and not local_changed:
        return 'pull', 'changed on remote'
    if local_changed and not remote_changed:
        if mirror:
            return 'push', 'changed here'
        return 'keep', 'local change kept (copy mode)'
    if can_merge:
        return 'merge', 'merged (both changed)'
    if not mirror:
        return 'pull', 'both changed: remote wins (copy mode)'
    side = _newer(lent, rent)
    action = 'push' if side == 'local' else 'pull'
    return action, f'both changed: newest is {side}'


def _duplicate(key: str, action: str, lent: Optional[Dict[str, Any]],
               rent: Optional[Dict[str, Any]], local_ids: Dict[str, str],
               remote_ids: Dict[str, str]) -> str:
    """
    Detect identity clashes for records about to be created.

    :return: str, reason when a duplicate is found, '' otherwise
    :rtype: str
    """
    if action == 'pull' and not lent and _live(rent):
        idents, other = rent.get('i') or [], local_ids
    elif action == 'push' and not rent and _live(lent):
        idents, other = lent.get('i') or [], remote_ids
    else:
        return ''
    for ident in idents:
        owner = other.get(ident)
        if owner and owner != key:
            where = 'here' if action == 'pull' else 'on remote'
            return f'identity {ident} already used by {owner} {where}'
    return ''


# =============================================================================
# Define peer run
# =============================================================================
def categories_for(peer: Dict[str, Any], kind: str) -> List[str]:
    """
    Return the enabled categories of a peer for a run kind.

    :param peer: dict, peer config
    :param kind: str, 'records', 'task_files' or 'all'

    :return: list of category names (registry order)
    :rtype: list
    """
    # categories added after the peer was configured take their default
    enabled = dict(adapters.default_categories(),
                   **(peer.get('categories') or dict()))
    out = []
    for name, adapter in adapters.ADAPTERS.items():
        if not enabled.get(name, False):
            continue
        if kind == 'records' and adapter.task_data:
            continue
        if kind == 'task_files' and not adapter.task_data:
            continue
        out.append(name)
    return out


def make_client(peer: Dict[str, Any]) -> peer_api.PeerClient:
    """
    Build a client for a configured peer.

    :param peer: dict, peer config

    :return: PeerClient
    :rtype: PeerClient
    :raises ValueError: if the peer token is missing
    """
    token = store.get_peer_token(peer['peer_id'])
    if not token:
        raise ValueError('No token stored for this peer')
    identity = store.get_identity()
    return peer_api.PeerClient(peer['url'], token, identity['server_id'])


def handshake(peer: Dict[str, Any]) -> Dict[str, Any]:
    """
    Contact a peer, check clocks/scope and store what it reports.

    :param peer: dict, peer config

    :return: dict, hello info plus 'warnings' and 'blocking' lists
    :rtype: dict
    """
    client = make_client(peer)
    identity = store.get_identity()
    info = client.hello(identity['server_name'])
    warnings, blocking = [], []
    skew = float(info.get('clock_skew') or 0.0)
    if abs(skew) > CLOCK_BLOCK:
        blocking.append(f'Clock difference is {skew:.0f}s (limit '
                        f'{CLOCK_BLOCK:.0f}s): fix NTP on one server.')
    elif abs(skew) > CLOCK_WARN:
        warnings.append(f'Clock difference is {skew:.0f}s: newest-wins '
                        'decisions may be wrong for edits made within that '
                        'window.')
    if info.get('server_id') == identity['server_id']:
        blocking.append('This URL points back to this same server.')
    if peer.get('mode') == 'mirror' and info.get('scope') != 'readwrite':
        blocking.append('Mirror mode needs a read+write token from the '
                        'other server (this token is read-only).')
    info['warnings'] = warnings
    info['blocking'] = blocking
    changes = dict(remote_server_id=info.get('server_id'),
                   remote_server_name=info.get('server_name'),
                   remote_version=info.get('version'),
                   remote_scope=info.get('scope'), clock_skew=skew,
                   last_hello_at=store.now_iso())
    store.update_peer(peer['peer_id'], **changes)
    return info


def run_peer(peer_id: str, dry_run: bool = True, kind: str = 'all',
             actor: str = 'system', auto: bool = False,
             logger: Optional[Callable[[str], None]] = None
             ) -> Dict[str, Any]:
    """
    Analyse (dry run) or execute a sync with one peer.

    :param peer_id: str, local peer id
    :param dry_run: bool, only compute the plan
    :param kind: str, 'records', 'task_files' or 'all'
    :param actor: str, username (or 'system' for the async task)
    :param auto: bool, True when called by the async task
    :param logger: callable or None, progress logger

    :return: dict summary (plan counts, conflicts, errors, warnings)
    :rtype: dict
    :raises store.SyncBusy: if another run holds the lock
    """
    def log(msg: str) -> None:
        if callable(logger):
            logger(msg)

    peer = store.get_peer(peer_id)
    if peer is None:
        raise KeyError(f'Unknown peer {peer_id}')
    started = time.time()
    summary = dict(peer_id=peer_id, peer=peer.get('label'), kind=kind,
                   dry_run=dry_run, auto=auto, actor=actor,
                   mode=peer.get('mode'), categories=dict(), errors=[],
                   warnings=[], conflicts=0, ok=False)
    with store.sync_lock():
        try:
            _run_locked(peer, dry_run, kind, summary, log)
            summary['ok'] = not summary['errors']
        except Exception as exc:
            summary['errors'].append(f'{type(exc).__name__}: {exc}')
            log(f'ERROR {exc}')
    summary['seconds'] = round(time.time() - started, 2)
    _record_run(peer, summary, dry_run, auto, actor)
    return summary


def _run_locked(peer: Dict[str, Any], dry_run: bool, kind: str,
                summary: Dict[str, Any], log: Callable[[str], None]) -> None:
    """
    Body of run_peer, executed while holding the sync lock.

    :return: None (results are written into summary)
    """
    info = handshake(peer)
    peer = store.get_peer(peer['peer_id'])
    summary['warnings'] += info['warnings']
    if info['blocking']:
        summary['errors'] += info['blocking']
        return
    client = make_client(peer)
    categories = categories_for(peer, kind)
    log(f'Categories: {", ".join(categories) or "(none)"}')
    remote_all = client.manifest(categories)
    state = store.load_state(peer['peer_id'])
    plans = dict()
    for category in categories:
        log(f'Scanning {category}')
        local = scan(category)
        remote = remote_all.get(category) or dict()
        base_hashes = store.load_base(peer['peer_id'], category)
        resolutions = state['resolutions'].get(category, dict())
        plan_args = [category, local, remote, base_hashes, peer['mode'],
                     resolutions]
        plan = plan_category(*plan_args)
        plans[category] = plan
        if not dry_run:
            exec_args = [client, peer, category, plan, base_hashes, local,
                         remote]
            errors = _execute(*exec_args)
            summary['errors'] += [f'{category}: {k}: {v}'
                                  for k, v in errors.items()]
            # one-shot resolutions are consumed once applied
            for item in plan['pull'] + plan['push'] + plan['keep']:
                resolutions.pop(item['key'], None)
        summary['categories'][category] = {k: len(v) for k, v in plan.items()}
        summary['conflicts'] += len(plan['conflicts'])
    state['last_plan'] = _plan_for_ui(plans)
    state['last_plan_at'] = store.now_iso()
    state['last_plan_dry_run'] = dry_run
    store.save_state(peer['peer_id'], state)


def _plan_for_ui(plans: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Reduce a plan to what the Run tab displays (no record data).

    :param plans: dict category -> plan

    :return: dict category -> {action: [items]}
    :rtype: dict
    """
    out = dict()
    for category, plan in plans.items():
        cat = dict()
        for action, items in plan.items():
            if action == 'agree':
                cat['agree_count'] = len(items)
                continue
            rows = []
            for item in items[:2000]:
                row = dict(key=item['key'], label=item['label'],
                           reason=item.get('reason', ''),
                           kind=item.get('kind', ''))
                for side in ('local', 'remote'):
                    entry = item.get(side)
                    row[side] = None if not entry else dict(
                        ts=entry.get('ts'), d=entry.get('d'))
                rows.append(row)
            cat[action] = rows
        out[category] = cat
    return out


def _batches(items: List[Any], size: int) -> Iterable[List[Any]]:
    """Yield fixed-size chunks of a list."""
    for start in range(0, len(items), size):
        yield items[start:start + size]


def _execute(client: peer_api.PeerClient, peer: Dict[str, Any],
             category: str, plan: Dict[str, Any], base_hashes: Dict[str, str],
             local: Dict[str, Any], remote: Dict[str, Any]
             ) -> Dict[str, str]:
    """
    Carry out a category plan and update the agreed base.

    :return: dict key -> error
    :rtype: dict
    """
    adapter = adapters.ADAPTERS[category]
    batch = BATCH_FILES if adapter.task_data else BATCH_RECORDS
    errors = dict()
    # --- pull: fetch data for live records, delete tombstoned ones
    pulls = plan['pull']
    for chunk in _batches(pulls, batch):
        live = [i['key'] for i in chunk if _live(i['remote'])]
        fetched = client.fetch(category, live) if live else dict()
        upserts = dict()
        deletes = dict()
        for item in chunk:
            key, rent = item['key'], item['remote']
            if _live(rent):
                if key not in fetched:
                    errors[key] = 'remote no longer has this record'
                    continue
                upserts[key] = dict(rent, data=fetched[key])
            else:
                deletes[key] = dict(ts=rent.get('ts') if rent else None,
                                    l=item['label'])
        errors.update(apply_records(category, upserts, deletes))
        for key in list(upserts) + list(deletes):
            if key not in errors:
                base_hashes[key] = remote.get(key, dict()).get('h', DELETED)
    # --- push (mirror only): send our data / tombstones
    for chunk in _batches(plan['push'], batch):
        live = [i['key'] for i in chunk if _live(i['local'])]
        data = load_records(category, live)
        upserts = dict()
        deletes = dict()
        for item in chunk:
            key, lent = item['key'], item['local']
            if _live(lent):
                if key not in data:
                    errors[key] = 'record vanished locally'
                    continue
                upserts[key] = dict(lent, data=data[key])
            else:
                deletes[key] = dict(ts=lent.get('ts') if lent else None,
                                    l=item['label'])
        remote_errors = client.apply(category, upserts, deletes)
        errors.update({k: f'remote: {v}' for k, v in remote_errors.items()})
        for key in list(upserts) + list(deletes):
            if key not in remote_errors:
                base_hashes[key] = local.get(key, dict()).get('h', DELETED)
    # --- merge: combine both versions and write to both sides
    for item in plan['merge']:
        key = item['key']
        rdata = client.fetch(category, [key]).get(key)
        ldata = load_records(category, [key]).get(key)
        merged = normalise(adapter.merge(key, ldata, rdata))
        entry = dict(data=merged, h=record_hash(merged), ts=time.time(),
                     i=(item['local'] or dict()).get('i') or [],
                     l=item['label'])
        errors.update(apply_records(category, {key: entry}, dict()))
        if peer.get('mode') == 'mirror':
            remote_errors = client.apply(category, {key: entry}, dict())
            if remote_errors:
                errors[key] = f'remote: {remote_errors.get(key)}'
                continue
        base_hashes[key] = entry['h']
    # --- agreed records (and resolved 'keep' in copy mode)
    for item in plan['agree']:
        base_hashes[item['key']] = (item['local'] or dict()).get('h')
    for item in plan['keep']:
        if item.get('reason', '').startswith('resolved') and item['remote']:
            # remember the remote version we chose not to take
            base_hashes[item['key']] = item['remote']['h']
    # forget base entries for records that no longer exist anywhere
    for key in list(base_hashes):
        if key not in local and key not in remote:
            base_hashes.pop(key)
    store.save_base(peer['peer_id'], category, base_hashes)
    return errors


def _record_run(peer: Dict[str, Any], summary: Dict[str, Any],
                dry_run: bool, auto: bool, actor: str) -> None:
    """
    Persist run results, history and admin notifications.

    :return: None
    """
    changes = dict(last_run_at=store.now_iso(), last_run_ok=summary['ok'],
                   last_run_dry=dry_run, last_conflicts=summary['conflicts'])
    if not dry_run:
        changes['last_sync_at'] = changes['last_run_at']
    store.update_peer(peer['peer_id'], **changes)
    store.append_history(summary)
    if auto and (summary['conflicts'] or not summary['ok']):
        _notify_admins(peer, summary)


def _notify_admins(peer: Dict[str, Any], summary: Dict[str, Any]) -> None:
    """
    Notify super admins about new conflicts or failures of the auto sync.

    :param peer: dict, peer config
    :param summary: dict, run summary

    :return: None
    """
    state = store.load_state(peer['peer_id'])
    plan = state.get('last_plan') or dict()
    current = sorted(f'{c}:{i["key"]}' for c, p in plan.items()
                     for i in p.get('conflicts', []))
    new = sorted(set(current) - set(state.get('notified') or []))
    state['notified'] = current
    store.save_state(peer['peer_id'], state)
    if not new and summary['ok']:
        return
    users = [u for u, info in auth.load_users().items()
             if 'super_admin' in (info or dict()).get('groups', [])]
    title = f'Server sync with {peer.get("label")}: attention needed'
    parts = []
    if new:
        parts.append(f'{len(new)} new conflict(s) were skipped.')
    if not summary['ok']:
        parts.append('Errors: ' + '; '.join(summary['errors'][:3]))
    url = permissions.page_id_to_url('home.admin_portal.server_sync')
    notify_args = [users, 'system', title, ' '.join(parts), url]
    notifications.emit_notification_bulk(*notify_args)


# =============================================================================
# Define peer-side request handling
# =============================================================================
def handle_peer(action: str, payload: Dict[str, Any], scope: str,
                caller: str) -> Any:
    """
    Serve one authenticated request from another server.

    :param action: str, hello / manifest / fetch / apply
    :param payload: dict, decrypted request payload
    :param scope: str, scope of the token used ('read' or 'readwrite')
    :param caller: str, the calling server's name/id (for logs)

    :return: Any, JSON-able response payload
    :rtype: Any
    :raises PermissionError: if the token scope does not allow the action
    :raises ValueError: for malformed requests
    """
    payload = payload or dict()
    if action == 'hello':
        identity = store.get_identity()
        out = dict()
        out['server_id'] = identity['server_id']
        out['server_name'] = identity['server_name']
        out['time'] = time.time()
        out['version'] = base.__version__
        out['scope'] = scope
        out['categories'] = list(adapters.ADAPTERS)
        return out
    category = payload.get('category')
    if action == 'manifest':
        return manifest(payload.get('categories') or [])
    if category not in adapters.ADAPTERS:
        raise ValueError(f'Unknown category {category!r}')
    if action == 'fetch':
        return load_records(category, payload.get('keys') or [])
    if action == 'apply':
        if scope != 'readwrite':
            raise PermissionError('This token is read-only')
        upserts = payload.get('upserts') or dict()
        deletes = payload.get('deletes') or dict()
        errors = apply_records(category, upserts, deletes)
        entry = dict(event='incoming', caller=caller, category=category,
                     upserts=len(upserts), deletes=len(deletes),
                     errors=len(errors))
        store.append_history(entry)
        return errors
    raise ValueError(f'Unknown action {action!r}')


# =============================================================================
# End of code
# =============================================================================
