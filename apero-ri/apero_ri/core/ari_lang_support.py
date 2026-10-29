#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ARI interface language support helpers.

Text shown in the ARI web interface is written in English in the templates
and looked up (by its English text) in ``resources/ari_lang.yaml`` which
holds the FR / ES translations. The active language comes from (in order):
the ``ari_lang`` cookie (set by the language switcher), the browser
``Accept-Language`` header, then English.

Created on 2026-10-28

@author: cook
"""
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import yaml
from flask import Response, make_response, redirect, request
from markupsafe import Markup, escape

# =============================================================================
# Define variables
# =============================================================================
RESOURCES_DIR = Path(__file__).parent.parent / "resources"
LANG_FILE = RESOURCES_DIR / "ari_lang.yaml"
# cookie that stores the user's explicit language choice
LANG_COOKIE = "ari_lang"
# one year (seconds)
LANG_COOKIE_AGE = 365 * 24 * 3600
# browser language code -> APERO language code (first entry is the default)
LANGUAGES = {"en": "ENG", "fr": "FR", "es": "ES"}
DEFAULT_LANG = "en"
# label shown in the language switcher (always in its own language)
LANGUAGE_NAMES = {"en": "English", "fr": "Français", "es": "Español"}
# cached translation table: {english text: {"FR": ..., "ES": ...}}
_TABLE: Optional[Dict[str, Dict[str, str]]] = None
_TABLE_MTIME: Optional[float] = None


# =============================================================================
# Define functions
# =============================================================================
def load_table(force: bool = False) -> Dict[str, Dict[str, str]]:
    """
    Load (and cache) the ARI translation table.

    The cache is refreshed when ``ari_lang.yaml`` changes on disk.

    :param force: bool, if True always re-read the yaml file

    :return: dict, english text -> {language code: translated text}
    """
    global _TABLE, _TABLE_MTIME
    try:
        mtime = LANG_FILE.stat().st_mtime
    except OSError:
        return dict()
    if _TABLE is not None and not force and mtime == _TABLE_MTIME:
        return _TABLE
    with LANG_FILE.open("r", encoding="utf-8") as fhandle:
        raw = yaml.safe_load(fhandle) or dict()
    table = dict()
    for key, values in raw.items():
        if isinstance(values, dict):
            table[str(key)] = {str(k): str(v) for k, v in values.items()}
    _TABLE, _TABLE_MTIME = table, mtime
    return table


def get_language() -> str:
    """
    Work out the language for the current request.

    :return: str, browser-style language code (one of LANGUAGES)
    """
    cookie = request.cookies.get(LANG_COOKIE, "")
    if cookie in LANGUAGES:
        return cookie
    best = request.accept_languages.best_match(list(LANGUAGES))
    return best if best in LANGUAGES else DEFAULT_LANG


def translate(text: str, lang: Optional[str] = None, **kwargs: Any) -> str:
    """
    Translate an English interface string.

    Missing translations fall back to the English text. ``kwargs`` are
    substituted with ``str.format`` after translation.

    :param text: str, the English text (also the lookup key)
    :param lang: str or None, language code; None uses the request language
    :param kwargs: values for any ``{name}`` fields in the text

    :return: str, the translated (and formatted) text
    """
    if lang is None:
        lang = get_language()
    value = str(text)
    if lang != DEFAULT_LANG:
        entry = load_table().get(value, dict())
        value = entry.get(LANGUAGES.get(lang, ""), value)
    if kwargs:
        value = value.format(**kwargs)
    return value


def language_options() -> List[Dict[str, str]]:
    """
    Language choices for the language switcher.

    :return: list of dicts with keys code and name
    """
    return [dict(code=code, name=LANGUAGE_NAMES[code]) for code in LANGUAGES]


def _safe_next(target: str) -> str:
    """
    Only allow redirects back to a local path (avoid open redirects).

    :param target: str, the requested redirect target

    :return: str, a local path to redirect to
    """
    if not target or '\\' in target:
        return "/"
    parsed = urlparse(target)
    if parsed.scheme or parsed.netloc:
        target = parsed.path or "/"
        if parsed.query:
            target += "?" + parsed.query
    if not target.startswith("/") or target.startswith("//"):
        return "/"
    return target


def set_language_view(lang: str) -> Response:
    """
    Store the chosen interface language in a cookie and go back.

    :param lang: str, browser-style language code

    :return: flask response redirecting to the ``next`` local path
    """
    target = _safe_next(request.args.get("next", ""))
    response = make_response(redirect(target))
    if lang in LANGUAGES:
        response.set_cookie(LANG_COOKIE, lang, max_age=LANG_COOKIE_AGE,
                            samesite="Lax", secure=request.is_secure,
                            httponly=True)
    return response


def context() -> Dict[str, Any]:
    """
    Template globals for the active request.

    :return: dict with ``_`` (translate), current_lang and ari_languages
    """
    lang = get_language()

    def _gettext(text: str, **kwargs: Any) -> Markup:
        # escape the translated text; placeholder values are escaped too
        # unless they are already Markup (e.g. ``'<code>x</code>'|safe``)
        value = escape(translate(text, lang))
        if kwargs:
            value = value.format(**kwargs)
        return value

    return {"_": _gettext, "current_lang": lang,
            "ari_languages": language_options()}

