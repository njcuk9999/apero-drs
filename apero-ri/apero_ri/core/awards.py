#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""APERO RI monitor "awards"/service-medal helpers.

Combines all-time monitor schedule statistics (hours/days served per
instrument, from :mod:`apero_ri.core.schedule`) with resolved-issue
counts (from :mod:`apero_ri.core.issues`) to compute per-user medals:

- Per-instrument "top 3" hours -> gold/silver/bronze.
- All-instrument "service" hours -> bronze/silver/gold at
  50/100/200 hours.
- Resolved-issue counts -> bronze/silver/gold at 250/500/1000.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from apero_ri.core import schedule as schedule_core
from apero_ri.core import issues as issues_core


__NAME__ = 'apero_ri.core.awards'


# All-time window used for "lifetime" totals.
_ALL_TIME_SINCE = '1900-01-01'
_ALL_TIME_UNTIL = '2999-12-31'

# Hours-of-service medal thresholds.
SERVICE_THRESHOLDS = (
    ('gold', 200.0),
    ('silver', 100.0),
    ('bronze', 50.0),
)

# Resolved-issues medal thresholds.
ISSUES_THRESHOLDS = (
    ('gold', 1000),
    ('silver', 500),
    ('bronze', 250),
)


def service_medal(total_hours: float) -> Optional[str]:
    """Return 'gold'/'silver'/'bronze'/None for total hours served."""
    for label, threshold in SERVICE_THRESHOLDS:
        if total_hours >= threshold:
            return label
    return None


def issues_medal(resolved_count: int) -> Optional[str]:
    """Return 'gold'/'silver'/'bronze'/None for resolved-issue count."""
    for label, threshold in ISSUES_THRESHOLDS:
        if resolved_count >= threshold:
            return label
    return None


def compute_user_hours(
    data_dir: Path, instruments: List[str]
) -> Dict[str, Dict]:
    """Return all-time per-user, per-instrument schedule totals.

    :return: dict keyed by username, each value a dict with keys
        ``who``, ``total_hours`` (sum across instruments), and
        ``instruments`` -- a dict keyed by instrument name with
        ``hours_estimated``/``days_completed``/``days_proposed``/
        ``total_days``.
    """
    by_user: Dict[str, Dict] = {}
    for inst in instruments:
        try:
            stats = schedule_core.compute_stats(
                data_dir, inst, _ALL_TIME_SINCE, _ALL_TIME_UNTIL,
            )
        except Exception:
            continue
        for row in stats.get('rows', []):
            username = row['username']
            entry = by_user.setdefault(username, {
                'username': username,
                'who': row.get('who') or username,
                'total_hours': 0.0,
                'instruments': {},
            })
            if row.get('who'):
                entry['who'] = row['who']
            hours = float(row.get('hours_estimated', 0.0) or 0.0)
            entry['total_hours'] += hours
            entry['instruments'][inst] = {
                'hours_estimated': hours,
                'days_completed': row.get('days_completed', 0),
                'days_proposed': row.get('days_proposed', 0),
                'total_days': row.get('total_days', 0),
            }
    return by_user


def compute_resolved_issue_counts(data_dir: Path) -> Dict[str, int]:
    """Return a dict of username -> count of issues resolved by them.

    Uses the issue's ``assigned_to`` field as a proxy for "who
    resolved it" -- issues are typically assigned to the monitor who
    is handling/resolving them.
    """
    counts: Dict[str, int] = {}
    try:
        resolved = issues_core.list_issues(
            data_dir, visibility='admin', status='resolved',
        )
    except Exception:
        return counts
    for issue in resolved:
        assigned = str(issue.get('assigned_to') or '').strip()
        if not assigned:
            continue
        counts[assigned] = counts.get(assigned, 0) + 1
    return counts


def instrument_rankings(
    user_hours: Dict[str, Dict], instrument: str, top_n: int = 3
) -> List[Dict]:
    """Return the top ``top_n`` users by hours for ``instrument``.

    :return: list of dicts ``{username, who, hours}`` sorted
        descending by hours (zero-hour entries excluded).
    """
    ranked = []
    for username, entry in user_hours.items():
        inst_entry = entry.get('instruments', {}).get(instrument)
        if not inst_entry:
            continue
        hours = float(inst_entry.get('hours_estimated', 0.0) or 0.0)
        if hours <= 0:
            continue
        ranked.append({
            'username': username,
            'who': entry.get('who') or username,
            'hours': hours,
        })
    ranked.sort(key=lambda item: item['hours'], reverse=True)
    return ranked[:top_n]


_INSTRUMENT_MEDALS = ('gold', 'silver', 'bronze')


def compute_awards(
    data_dir: Path, instruments: List[str]
) -> Dict[str, Dict]:
    """Compute the full awards payload for all monitors.

    :return: dict keyed by username, each value a dict with:
        - ``who``: display name
        - ``total_hours``: lifetime hours across all instruments
        - ``instruments``: per-instrument hours/days dict
        - ``instrument_medals``: dict instrument -> 'gold'/'silver'/
          'bronze' for the top-3 users of that instrument
        - ``service_medal``: 'gold'/'silver'/'bronze'/None
        - ``issues_resolved``: int
        - ``issues_medal``: 'gold'/'silver'/'bronze'/None
    """
    user_hours = compute_user_hours(data_dir, instruments)
    issue_counts = compute_resolved_issue_counts(data_dir)

    awards: Dict[str, Dict] = {}
    for username, entry in user_hours.items():
        awards[username] = {
            'username': username,
            'who': entry.get('who') or username,
            'total_hours': entry.get('total_hours', 0.0),
            'instruments': entry.get('instruments', {}),
            'instrument_medals': {},
            'service_medal': service_medal(entry.get('total_hours', 0.0)),
            'issues_resolved': 0,
            'issues_medal': None,
        }

    for inst in instruments:
        for rank, item in enumerate(
            instrument_rankings(user_hours, inst, top_n=3)
        ):
            username = item['username']
            awards[username]['instrument_medals'][inst] = (
                _INSTRUMENT_MEDALS[rank]
            )

    for username, count in issue_counts.items():
        entry = awards.setdefault(username, {
            'username': username,
            'who': username,
            'total_hours': 0.0,
            'instruments': {},
            'instrument_medals': {},
            'service_medal': None,
            'issues_resolved': 0,
            'issues_medal': None,
        })
        entry['issues_resolved'] = count
        entry['issues_medal'] = issues_medal(count)

    return awards
