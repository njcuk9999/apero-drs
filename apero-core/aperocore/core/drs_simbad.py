#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SIMBAD server selection with mirror fallback

Checks (once per process) which SIMBAD TAP server in an ordered list is
responding and returns it, so callers can fall back to a mirror (e.g.
Harvard) when the main CDS server is down. Also points astroquery's
SIMBAD client at the selected server.

Created on 2026-11-03

@author: cook

import rules:
    only aperocore.base + python stdlib (astroquery imported lazily)
"""
import urllib.error
import urllib.parse
import urllib.request
from typing import Dict, List, Optional, Sequence, Tuple

from aperocore.base import base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'aperocore.core.drs_simbad.py'
__PACKAGE__ = base.__PACKAGE__
__INSTRUMENT__ = 'None'
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__
# default SIMBAD TAP servers: main server first, then mirrors
SIMBAD_TAP_URLS = ['https://simbad.cds.unistra.fr/simbad/sim-tap',
                   'https://simbad.harvard.edu/simbad/sim-tap']
# tiny query used to test whether a SIMBAD TAP server responds
TEST_ADQL = 'SELECT TOP 1 oid FROM basic'
# default timeout (seconds) for the up-check of each server
CHECK_TIMEOUT = 10.0
# user-agent for the up-check request
USER_AGENT = 'apero-simbad-check/1.0'
# {tuple of candidate urls -> selected url} (one check per process)
_SELECTED_URL: Dict[Tuple[str, ...], str] = dict()


# =============================================================================
# Define functions
# =============================================================================
def simbad_tap_is_up(url: str, timeout: float = CHECK_TIMEOUT) -> bool:
    """
    Test whether a SIMBAD TAP server answers a trivial ADQL query.

    :param url: str, TAP base url (``.../sim-tap``) or its ``/sync``
                endpoint
    :param timeout: float, request timeout in seconds

    :return: bool, True if the server returned HTTP 200
    """
    # normalise to the synchronous endpoint
    sync_url = str(url).rstrip('/')
    if not sync_url.endswith('/sync'):
        sync_url += '/sync'
    # build the query string for the test query
    query = dict(REQUEST='doQuery', LANG='ADQL', FORMAT='json',
                 QUERY=TEST_ADQL)
    full_url = sync_url + '?' + urllib.parse.urlencode(query)
    request = urllib.request.Request(full_url,
                                     headers={'User-Agent': USER_AGENT})
    # any network / http / malformed-url failure counts as "down"
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status == 200
    except (urllib.error.URLError, OSError, ValueError):
        return False


def select_simbad_url(urls: Optional[Sequence[str]] = None,
                      timeout: float = CHECK_TIMEOUT) -> str:
    """
    Return the first responding SIMBAD TAP url from ``urls``.

    The check is done only once per process for a given list of urls;
    later calls return the cached choice. If no server responds the
    first url is returned (so callers fail as they did before).

    :param urls: ordered list of TAP urls (main first, then mirrors);
                 defaults to :data:`SIMBAD_TAP_URLS`
    :param timeout: float, up-check timeout per server in seconds

    :raises ValueError: if ``urls`` is empty

    :return: str, the selected TAP url
    """
    # deal with no urls given
    if urls is None:
        urls = SIMBAD_TAP_URLS
    key = tuple(str(url).strip() for url in urls)
    if len(key) == 0:
        raise ValueError('No SIMBAD urls given')
    # only check once per process
    if key in _SELECTED_URL:
        return _SELECTED_URL[key]
    # default to the main server if nothing responds
    selected = key[0]
    # with a single url there is nothing to fall back to
    if len(key) > 1:
        for url in key:
            if simbad_tap_is_up(url, timeout):
                selected = url
                break
    # cache and return
    _SELECTED_URL[key] = selected
    return selected


def simbad_server(url: str) -> str:
    """
    Return the host name of a SIMBAD url (as used by astroquery).

    :param url: str, a full url (``https://host/...``) or a bare host

    :return: str, the host name e.g. ``'simbad.harvard.edu'``
    """
    # bare host names have no scheme so urlparse gives no netloc
    netloc = urllib.parse.urlparse(str(url)).netloc
    if netloc:
        return netloc
    return str(url).strip().split('/')[0]


def use_simbad_mirror(urls: Optional[Sequence[str]] = None,
                      timeout: float = CHECK_TIMEOUT) -> str:
    """
    Point astroquery's SIMBAD client at the first responding server.

    Updates both ``astroquery.simbad.conf.server`` (used by new
    ``SimbadClass`` instances) and the shared ``Simbad`` instance.

    :param urls: ordered list of TAP urls (main first, then mirrors);
                 defaults to :data:`SIMBAD_TAP_URLS`
    :param timeout: float, up-check timeout per server in seconds

    :return: str, the selected SIMBAD host name
    """
    # lazy import: astroquery is optional for most of APERO
    from astroquery import simbad as aq_simbad
    # find the working server (checked once per process)
    server = simbad_server(select_simbad_url(urls, timeout))
    # astroquery only accepts servers in its own list
    servers_list: List[str] = aq_simbad.conf.servers_list
    if server not in servers_list:
        servers_list.append(server)
    # conf.server is a fixed-option config item (custom hosts rejected)
    try:
        aq_simbad.conf.server = server
    except TypeError:
        pass
    # the shared instance copied conf.server at import time
    aq_simbad.Simbad.server = server
    return server


# =============================================================================
# End of code
# =============================================================================
