"""
ICS / iCalendar Feed Helpers
============================

Fetch, parse, and sync external .ics calendar feeds into the
user and instrument calendar YAML stores.

Each feed is persisted in the ``ics_feeds`` list of the relevant
``calendar.yaml`` alongside regular events.  Imported events carry::

    source:      'ics'
    ics_feed_id: <feed_id>   # 12-char SHA-1 hex of the feed URL
    id:          ics-<feed_id[:8]>-<uid_hash[:12]>

so they can be cleanly replaced on every refresh without touching
user-created events.  Up to ``MAX_EVENTS_PER_FEED`` events are
imported per feed.
"""

import hashlib
import logging
import uuid
from datetime import datetime

import requests

log = logging.getLogger(__name__)

REQUEST_TIMEOUT: int = 20
MAX_EVENTS_PER_FEED: int = 2000
ICS_SOURCE: str = "ics"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _feed_id(url: str) -> str:
    """Return a stable 12-char hex id derived from *url*."""
    return hashlib.sha1(url.encode()).hexdigest()[:12]


def _event_id(feed_id: str, uid: object) -> str:
    """Build a stable event id from feed id and VEVENT UID."""
    raw = f"{feed_id}:{uid!s}"
    digest = hashlib.sha1(raw.encode()).hexdigest()[:12]
    return f"ics-{feed_id[:8]}-{digest}"


def _to_date_str(dt_val: object) -> str | None:
    """Convert a dtstart value (vDDDTypes / datetime / date) to
    YYYY-MM-DD, or *None* if conversion fails."""
    if dt_val is None:
        return None
    if hasattr(dt_val, "dt"):
        dt_val = dt_val.dt
    try:
        if isinstance(dt_val, datetime):
            return dt_val.date().strftime("%Y-%m-%d")
        return dt_val.strftime("%Y-%m-%d")
    except AttributeError:
        s = str(dt_val)
        return s[:10] if len(s) >= 10 else None


def _map_rrule(rrule_prop: object) -> str:
    """Map a RRULE FREQ value to the apero-ri recurrence string
    (``none`` / ``daily`` / ``weekly`` / ``monthly`` / ``yearly``)."""
    if not rrule_prop:
        return "none"
    freq_map = {
        "DAILY": "daily",
        "WEEKLY": "weekly",
        "MONTHLY": "monthly",
        "YEARLY": "yearly",
    }
    try:
        raw = dict(rrule_prop)
        freq_list = raw.get("FREQ", [])
        if freq_list:
            return freq_map.get(str(freq_list[0]).upper(), "none")
    except (TypeError, AttributeError):
        pass
    return "none"


# ---------------------------------------------------------------------------
# Fetch + parse a single ICS URL
# ---------------------------------------------------------------------------

def _expand_rrule(start_prop: object, rrule_prop: object) -> list:
    """Expand *rrule_prop* from *start_prop* into a list of naive
    datetime occurrences.  Falls back to ``[dtstart]`` on error.

    Capped at ``MAX_EVENTS_PER_FEED`` occurrences to guard against
    open-ended rules (no UNTIL / no COUNT).
    """
    from dateutil.rrule import rrulestr as _rrulestr
    from itertools import islice as _islice

    dtstart = (
        start_prop.dt
        if hasattr(start_prop, "dt")
        else start_prop
    )
    if isinstance(dtstart, datetime):
        dtstart = dtstart.replace(tzinfo=None)
    else:
        dtstart = datetime(
            dtstart.year, dtstart.month, dtstart.day
        )
    try:
        rule_str = "RRULE:" + rrule_prop.to_ical().decode()
        rule = _rrulestr(
            rule_str, dtstart=dtstart, ignoretz=True
        )
        return list(_islice(rule, MAX_EVENTS_PER_FEED))
    except Exception:
        return [dtstart]


def fetch_and_parse(
    url: str,
    feed_id: str,
    color: str = "#4a90d9",
    category: str = "personal",
) -> list[dict]:
    """Download *url*, parse every VEVENT, return a list of event
    dicts compatible with the apero-ri calendar schema.

    Recurring events (RRULE) are expanded into individual per-date
    occurrences, each stored with ``recurrence="none"``, so the
    front-end calendar does not attempt its own infinite expansion.

    :param url: HTTPS URL of the ICS feed
    :param feed_id: stable feed identifier (from :func:`_feed_id`)
    :param color:   hex colour string for imported events
    :param category: event category string
    :return: list of event dicts
    :raises RuntimeError: if ``icalendar`` is not installed
    :raises requests.HTTPError: on non-2xx HTTP response
    """
    try:
        from icalendar import Calendar  # type: ignore
    except ImportError:
        raise RuntimeError(
            "The 'icalendar' package is required for ICS feed "
            "support. Run: pip install icalendar"
        )

    resp = requests.get(
        url,
        timeout=REQUEST_TIMEOUT,
        headers={"User-Agent": "APERO-RI-CalendarSync/1.0"},
    )
    resp.raise_for_status()

    cal = Calendar.from_ical(resp.content)

    # First pass: collect {uid -> set(date_str)} for RECURRENCE-ID
    # overrides so we can skip those dates during RRULE expansion.
    override_dates: dict[str, set[str]] = {}
    vevents: list = []
    for component in cal.walk():
        if component.name != "VEVENT":
            continue
        vevents.append(component)
        rec_id = component.get("RECURRENCE-ID")
        if rec_id:
            uid_str = str(component.get("UID", ""))
            d = _to_date_str(rec_id)
            if d:
                override_dates.setdefault(
                    uid_str, set()
                ).add(d)

    events: list[dict] = []

    def _tz_str(start) -> str:
        if (
            hasattr(start, "dt")
            and hasattr(start.dt, "tzinfo")
            and start.dt.tzinfo is not None
        ):
            return str(start.dt.tzinfo)
        return "UTC"

    def _mk_event(
        uid_key: str,
        date_str: str,
        time_str: str,
        tzone: str,
        title: str,
        notes: str,
    ) -> dict:
        return {
            "id": _event_id(feed_id, uid_key),
            "title": title,
            "date": date_str,
            "time": time_str,
            "timezone": tzone,
            "color": color,
            "category": category,
            "recurrence": "none",
            "status": "confirmed",
            "notes": notes,
            "source": ICS_SOURCE,
            "ics_feed_id": feed_id,
        }

    _capped = False
    for component in vevents:
        uid = str(component.get("UID", str(uuid.uuid4())))
        start = component.get("DTSTART")
        summary = str(
            component.get("SUMMARY", "Untitled")
        ).strip()
        description = component.get("DESCRIPTION", "")
        notes = str(description).strip() if description else ""
        rrule_prop = component.get("RRULE")
        rec_id = component.get("RECURRENCE-ID")
        tz = _tz_str(start)

        if rec_id:
            # Override for one specific occurrence.
            date_str = _to_date_str(start)
            if not date_str:
                continue
            dt_val = (
                start.dt if hasattr(start, "dt") else start
            )
            time_str = (
                dt_val.strftime("%H:%M")
                if isinstance(dt_val, datetime)
                else ""
            )
            events.append(
                _mk_event(
                    f"{uid}:{date_str}", date_str,
                    time_str, tz, summary, notes,
                )
            )
        elif rrule_prop:
            # Master recurring: expand RRULE to individual dates.
            excluded = override_dates.get(uid, set())
            for occ_dt in _expand_rrule(start, rrule_prop):
                occ_date = occ_dt.strftime("%Y-%m-%d")
                if occ_date in excluded:
                    continue
                events.append(
                    _mk_event(
                        f"{uid}:{occ_date}", occ_date,
                        occ_dt.strftime("%H:%M"), tz,
                        summary, notes,
                    )
                )
                if len(events) >= MAX_EVENTS_PER_FEED:
                    _capped = True
                    break
        else:
            # Single non-recurring event.
            date_str = _to_date_str(start)
            if not date_str:
                continue
            dt_val = (
                start.dt if hasattr(start, "dt") else start
            )
            time_str = (
                dt_val.strftime("%H:%M")
                if isinstance(dt_val, datetime)
                else ""
            )
            events.append(
                _mk_event(
                    uid, date_str, time_str, tz,
                    summary, notes,
                )
            )

        if _capped or len(events) >= MAX_EVENTS_PER_FEED:
            _capped = True
            break

    if _capped:
        log.warning(
            "Feed %s hit %d-event cap; remaining VEVENTs ignored.",
            feed_id,
            MAX_EVENTS_PER_FEED,
        )

    return events


# ---------------------------------------------------------------------------
# Feed CRUD helpers (operate on in-memory data dicts)
# ---------------------------------------------------------------------------

def get_feeds(data: dict) -> list[dict]:
    """Return the ``ics_feeds`` list from a calendar data dict."""
    return list(data.get("ics_feeds", []))


def add_feed(
    data: dict,
    name: str,
    url: str,
    color: str = "#4a90d9",
    category: str = "personal",
) -> dict:
    """Add a new feed entry to *data* (does not fetch yet).

    Returns the existing feed dict if *url* is already registered.
    """
    fid = _feed_id(url)
    for existing in data.get("ics_feeds", []):
        if existing.get("url") == url:
            return existing
    feed: dict = {
        "id": fid,
        "name": name,
        "url": url,
        "color": color,
        "category": category,
        "enabled": True,
        "last_synced": None,
        "last_error": None,
    }
    data.setdefault("ics_feeds", []).append(feed)
    return feed


def update_feed(
    data: dict,
    feed_id: str,
    name: str | None = None,
    color: str | None = None,
) -> dict:
    """Update the display name and/or colour of an existing feed.

    Also updates the colour on all events already imported from that
    feed so the calendar view reflects the change immediately.

    :raises ValueError: if *feed_id* is not found.
    """
    feeds = data.get("ics_feeds", [])
    feed = next(
        (f for f in feeds if f.get("id") == feed_id), None
    )
    if feed is None:
        raise ValueError(f"ICS feed '{feed_id}' not found")
    if name is not None:
        feed["name"] = name
    if color is not None:
        feed["color"] = color
        for event in data.get("events", []):
            if (
                event.get("source") == ICS_SOURCE
                and event.get("ics_feed_id") == feed_id
            ):
                event["color"] = color
    return feed


def delete_feed(data: dict, feed_id: str) -> None:
    """Remove *feed_id* and all its imported events from *data*."""
    data["ics_feeds"] = [
        f for f in data.get("ics_feeds", [])
        if f.get("id") != feed_id
    ]
    data["events"] = [
        e for e in data.get("events", [])
        if not (
            e.get("source") == ICS_SOURCE
            and e.get("ics_feed_id") == feed_id
        )
    ]


def refresh_feed(data: dict, feed_id: str) -> dict:
    """Re-fetch one ICS feed and replace its events in *data*.

    Mutates *data* in-place.

    :raises ValueError: if *feed_id* is not found in ``ics_feeds``
    """
    feeds = data.setdefault("ics_feeds", [])
    feed = next((f for f in feeds if f.get("id") == feed_id), None)
    if feed is None:
        raise ValueError(f"ICS feed '{feed_id}' not found")
    if not feed.get("enabled", True):
        return feed

    # Remove stale events
    data["events"] = [
        e for e in data.get("events", [])
        if not (
            e.get("source") == ICS_SOURCE
            and e.get("ics_feed_id") == feed_id
        )
    ]

    try:
        new_events = fetch_and_parse(
            feed["url"],
            feed_id,
            color=feed.get("color", "#4a90d9"),
            category=feed.get("category", "personal"),
        )
        data["events"].extend(new_events)
        feed["last_synced"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        feed["last_error"] = None
        log.info(
            "ICS feed '%s' refreshed: %d events imported.",
            feed.get("name"),
            len(new_events),
        )
    except Exception as exc:
        feed["last_error"] = str(exc)
        log.error(
            "ICS feed '%s' refresh failed: %s", feed.get("name"), exc
        )
        raise

    return feed


def refresh_all_feeds(data: dict) -> dict[str, str]:
    """Refresh every enabled ICS feed in *data* in-place.

    Errors per feed are stored in ``feed['last_error']`` but do not
    abort processing of remaining feeds.

    :returns: mapping ``{feed_id: 'ok' | 'disabled' | error_message}``
    """
    results: dict[str, str] = {}
    for feed in data.get("ics_feeds", []):
        fid = feed.get("id", "")
        if not feed.get("enabled", True):
            results[fid] = "disabled"
            continue
        try:
            refresh_feed(data, fid)
            results[fid] = "ok"
        except Exception as exc:
            results[fid] = str(exc)
    return results
