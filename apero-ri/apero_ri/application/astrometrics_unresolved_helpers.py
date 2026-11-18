#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: unresolved astrometric objects.

Collects the raw-header object names the ASTROM check could not resolve,
across every APERO profile the user can access (so only the user's
instruments are shown), for the astrometrics "Unresolved objects" page.

The ASTROM check stores the unresolved names as structured ``details`` in
its failure entry; the per-profile checks index tells us which nights have
an ASTROM failure, so only those YAML files are read.

Created on 2026-11-18

@author: cook
"""
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import urlencode

from flask import url_for

from apero_ri.core import apero_checks as checks_core
from apero_ri.core import checks_index
from apero_ri.core.auth import get_accessible_profiles

# =============================================================================
# Define variables
# =============================================================================
# Check key whose failures list unresolved object names.
ASTROM_CHECK_KEY = 'ASTROM'
# Index states meaning the ASTROM check did not pass on a night.
NOT_PASSED_STATES = ('failed', 'monitored', 'overridden', 'mixed')
# Nights listed inline per object before summarising.
MAX_NIGHTS_SHOWN = 5


# =============================================================================
# Define functions
# =============================================================================
def collect_unresolved(app: Any, user_info: Dict[str, Any]) -> Dict[str, Any]:
    """Return unresolved object rows for every profile the user can access.

    Names that resolve in the astrometric database now (resolved since the
    check last ran) are dropped and counted separately.

    :param app: The ARI application.
    :param user_info: Effective logged-in user.
    :return: Mapping with ``rows`` (one per object name), ``n_profiles``,
             ``n_resolved_since`` and ``nights_without_details`` (ASTROM
             failures recorded before details were stored).
    """
    from apero.core import drs_astrometrics as dra

    local_data_dir = Path(app._resolve_local_data_dir())
    checks_cfg = checks_core.load_config(local_data_dir)
    astrom_root = local_data_dir / 'apero-assets' / 'astrometrics'
    profiles = get_accessible_profiles(user_info, app.ari_groups) or []
    rows: Dict[str, Dict[str, Any]] = dict()
    nights_without_details: List[Dict[str, str]] = []
    for profile in profiles:
        profile_id = str(profile.get('profile_id') or '').strip()
        if not profile_id:
            continue
        # Prefer the specific instrument (e.g. NIRPS_HE) over the group key.
        general = (profile.get('data') or {}).get('general') or {}
        instrument = str(general.get('instrument')
                         or profile.get('instrument') or '').strip()
        # Nights where ASTROM did not pass (from the index, no YAML I/O).
        obsdirs = set()
        for state in NOT_PASSED_STATES:
            for entry in checks_index.get_check_results(
                    profile_id, ASTROM_CHECK_KEY, state):
                obsdirs.add(str(entry.get('obsdir') or ''))
        obsdirs.discard('')
        if not obsdirs:
            continue
        root_kwargs = dict(profile_data=profile.get('data'),
                           configured_root=checks_cfg.get('checks_root', ''))
        root = checks_core.resolve_checks_root(local_data_dir, **root_kwargs)
        for obsdir in sorted(obsdirs):
            failure = _astrom_failure(root, obsdir)
            if failure is None:
                continue
            unresolved = (failure.get('details') or {}).get('unresolved')
            # Failures written before details existed need a check re-run.
            if not isinstance(unresolved, list):
                nights_without_details.append(
                    dict(profile_id=profile_id, obsdir=obsdir))
                continue
            for item in unresolved:
                _add_item(rows, item, profile_id, instrument, obsdir)
    # Drop names resolved since the check ran.
    n_resolved_since = 0
    out_rows = []
    for row in rows.values():
        if dra.find_by_name(str(astrom_root), row['name']) is not None:
            n_resolved_since += 1
            continue
        out_rows.append(_finalise_row(row))
    # Most recently seen first.
    out_rows.sort(key=lambda row: (row['last_night'], row['name']),
                  reverse=True)
    return dict(rows=out_rows, n_profiles=len(profiles),
                n_resolved_since=n_resolved_since,
                nights_without_details=nights_without_details)


def resolve_url(name: str) -> str:
    """Return the astrometrics resolver URL that looks up one name.

    :param name: Raw object name.
    :return: URL opening the resolver with the name filled in and run.
    """
    query = urlencode(dict(rt_name=name, rt_run='1'))
    return url_for('home_astrometrics') + '?' + query


# =============================================================================
# Define worker functions
# =============================================================================
def _astrom_failure(root: Path, obsdir: str) -> Any:
    """Return the ASTROM failure entry of one night, if any.

    :param root: Profile checks root.
    :param obsdir: Observation directory.
    :return: Failure entry dict, or None.
    """
    path = Path(root) / f'{obsdir}.yaml'
    if not path.is_file():
        return None
    loaded = checks_core.load_check_file(path)
    failure = (loaded.get('failures') or {}).get(ASTROM_CHECK_KEY)
    return failure if isinstance(failure, dict) else None


def _add_item(rows: Dict[str, Dict[str, Any]], item: Any, profile_id: str,
              instrument: str, obsdir: str) -> None:
    """Merge one unresolved-name record into the per-name rows.

    :param rows: Rows keyed by object name (updated in place).
    :param item: One ``details.unresolved`` record.
    :param profile_id: Profile the night belongs to.
    :param instrument: Instrument of the profile.
    :param obsdir: Observation directory.
    :return: None.
    """
    if not isinstance(item, dict):
        return
    name = str(item.get('name') or '').strip()
    if not name:
        return
    row = rows.setdefault(name, dict(
        name=name, header_keys=set(), instruments=set(), profiles=set(),
        nights=set(), n_files=0, files=[], resolver=''))
    row['header_keys'].add(str(item.get('header_key') or ''))
    if instrument:
        row['instruments'].add(instrument)
    row['profiles'].add(profile_id)
    row['nights'].add((obsdir, profile_id))
    row['n_files'] += int(item.get('n_files') or 0)
    for fname in item.get('files') or []:
        if fname not in row['files'] and len(row['files']) < 5:
            row['files'].append(str(fname))
    if not row['resolver'] and item.get('resolver'):
        row['resolver'] = str(item['resolver'])


def _finalise_row(row: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a merged row into template-ready values.

    :param row: Merged per-name row.
    :return: Row with sorted lists, night links and the resolve URL.
    """
    nights = sorted(row['nights'], reverse=True)
    night_links = []
    for obsdir, profile_id in nights[:MAX_NIGHTS_SHOWN]:
        link_kwargs = dict(profile_id=profile_id, obsdir=obsdir)
        night_links.append(dict(
            obsdir=obsdir, profile_id=profile_id,
            url=url_for('monitor_apero_checks_obsdir_view', **link_kwargs)))
    return dict(
        name=row['name'],
        header_keys=sorted(key for key in row['header_keys'] if key),
        instruments=sorted(row['instruments']),
        profiles=sorted(row['profiles']),
        n_nights=len(nights),
        night_links=night_links,
        last_night=nights[0][0] if nights else '',
        n_files=row['n_files'],
        files=row['files'],
        resolver=row['resolver'],
        resolve_url=resolve_url(row['name']),
    )


# =============================================================================
# End of code
# =============================================================================
