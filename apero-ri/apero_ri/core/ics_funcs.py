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

def fetch_and_parse(
    url: str,
    feed_id: str,
    color: str = "#4a90d9",
    category: str = "personal",
) -> list[dict]:
    """Download *url*, parse every VEVENT, return a list of event
    dicts compatible with the apero-ri calendar schema.

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
            "The 'icalendar' package is required for ICS feed support. "
            "Run: pip install icalendar"
        )

    resp = requests.get(
        url,
        timeout=REQUEST_TIMEOUT,
        headers={"User-Agent": "APERO-RI-CalendarSync/1.0"},
    )
    resp.raise_for_status()

    cal = Calendar.from_ical(resp.content)
    events: list[dict] = []

    for component in cal.walk():
        if component.name != "VEVENT":
            continue

        uid = component.get("UID", str(uuid.uuid4()))
        start = component.get("DTSTART")
        summary = component.get("SUMMARY", "Untitled")
        description = component.get("DESCRIPTION", "")
        rrule_prop = component.get("RRULE")
        tzone = "UTC"
        if hasattr(start, "dt") and hasattr(start.dt, "tzinfo"):
            tz = start.dt.tzinfo
            if tz is not None:
                tzone = str(tz)

        date_str = _to_date_str(start)
        if not date_str:
            continue

        # Only set time if it is a datetime (not date-only)
        time_str = ""
        if hasattr(start, "dt") and isinstance(start.dt, datetime):
            time_str = start.dt.strftime("%H:%M")

        recurrence = _map_rrule(rrule_prop)

        events.append(
            {
                "id": _event_id(feed_id, uid),
                "title": str(summary).strip(),
                "date": date_str,
                "time": time_str,
                "timezone": tzone,
                "color": color,
                "category": category,
                "recurrence": recurrence,
                "status": "confirmed",
                "notes": str(description).strip() if description else "",
                "source": ICS_SOURCE,
                "ics_feed_id": feed_id,
            }
        )

        if len(events) >= MAX_EVENTS_PER_FEED:
            log.warning(
                "Feed %s hit %d-event cap; remaining VEVENTs ignored.",
                feed_id,
                MAX_EVENTS_PER_FEED,
            )
            break

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
