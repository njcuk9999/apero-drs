#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Thin user-facing wrapper around the yaml-backed astrometric database in
``apero.core.drs_astrometrics``.

All catalogue resolution (SIMBAD / Gaia / VizieR) lives in core; this
module only handles the user-prompt / google-sheet plumbing for the
``apero_astrometrics`` and ``apero_reject`` recipes.

Created on 2026-04-21 (rewrite)

@author: cook
"""
import getpass
import os
import socket
import sys
import warnings
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

from apero.base import base as apero_base
from apero.core import drs_astrometrics as _core_astrom
from apero.core import drs_database
from apero.tools.module.database import manage_databases
from apero.tools.module.setup import drs_installation
from apero.utils import drs_recipe
from apero.utils import drs_startup
from aperocore import drs_lang
from aperocore.base import base
from aperocore.constants import param_functions
from aperocore.core import drs_log
from aperocore.core import drs_misc
from aperocore.core import drs_text


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tools.module.database.drs_astrometrics'
__INSTRUMENT__ = 'None'
__PACKAGE__ = apero_base.__PACKAGE__
__version__ = apero_base.__version__
__authors__ = apero_base.__authors__
__date__ = apero_base.__date__
__release__ = apero_base.__release__
# astropy time wrapper used in note timestamps
Time = base.Time
# language entry helper
textentry = drs_lang.textentry
# parameter dictionary type
ParamDict = param_functions.ParamDict
# recipe type
DrsRecipe = drs_recipe.DrsRecipe
# central logger
WLOG = drs_log.wlog
# coded exception type
AperoCodedException = drs_log.AperoCodedException
# canonical AstrometricDatabase from core
AstrometricDatabase = _core_astrom.AstrometricDatabase
# canonical name cleaner from core
clean_object = _core_astrom.clean_object
# null text values used by ad-hoc input parsing
NULL_TEXT = ['None', '--', '', ' ']


# =============================================================================
# Define classes
# =============================================================================
class AstroObj:
    """
    Lightweight container around a single yaml astrometric entry.

    Carries both the underlying dict (``self.entry``) and the legacy
    flat attributes (``objname``, ``ra``, ``aliases``, ...) used by the
    existing user-facing recipes so callers do not have to know about
    the yaml schema.
    """
    # type hints (kept as class attributes for back-compat with the legacy
    # tool which relied on the same attribute names)
    objname: Optional[str] = None
    original_name: Optional[str] = None
    aliases: Optional[str] = None
    ra: Optional[float] = None
    ra_source: Optional[str] = None
    dec: Optional[float] = None
    dec_source: Optional[str] = None
    epoch: Optional[float] = None
    pmra: Optional[float] = None
    pmra_source: Optional[str] = None
    pmde: Optional[float] = None
    pmde_source: Optional[str] = None
    plx: Optional[float] = None
    plx_source: Optional[str] = None
    rv: Optional[float] = None
    rv_source: Optional[str] = None
    sp_type: Optional[str] = None
    sp_source: Optional[str] = None
    teff: Optional[float] = None
    teff_source: Optional[str] = None
    notes: Optional[str] = None

    def __init__(self, name: str,
                 entry: Optional[Dict[str, Any]] = None) -> None:
        """
        :param name: str, the user-supplied target name
        :param entry: optional dict, an existing yaml entry to wrap
        """
        # the raw input name (used for prompts)
        self.name = name
        # the underlying yaml entry dict (always present)
        self.entry: Dict[str, Any] = dict(entry) if entry else dict()
        # populate flat attributes from the entry (if any)
        self._refresh_from_entry()

    def __repr__(self) -> str:
        return 'AstroObj[{0}]'.format(self.name)

    __str__ = __repr__

    # -------------------------------------------------------------------------
    # Helpers to keep the flat attributes in sync with self.entry
    # -------------------------------------------------------------------------
    def _refresh_from_entry(self) -> None:
        """Mirror keys from ``self.entry`` onto the flat attributes."""
        # canonical APERO_NAME (cleaned form of the input name)
        self.objname = (self.entry.get('APERO_NAME')
                        or clean_object(self.name))
        # original (uncleaned) name as supplied to SIMBAD
        self.original_name = self.entry.get('ORIGINAL_NAME') or self.name
        # aliases stored as a pipe-separated string for back-compat
        aliases = self.entry.get('ALIASES')
        if isinstance(aliases, list):
            self.aliases = '|'.join(str(a) for a in aliases if a)
        else:
            self.aliases = aliases or ''
        # value+source nested blocks
        self.ra = self._nested_value('RA')
        self.ra_source = self._nested_source('RA')
        self.dec = self._nested_value('DEC')
        self.dec_source = self._nested_source('DEC')
        self.pmra = self._nested_value('PMRA')
        self.pmra_source = self._nested_source('PMRA')
        self.pmde = self._nested_value('PMDE')
        self.pmde_source = self._nested_source('PMDE')
        self.plx = self._nested_value('PLX')
        self.plx_source = self._nested_source('PLX')
        self.rv = self._nested_value('RV')
        self.rv_source = self._nested_source('RV')
        self.sp_type = self._nested_value('SPT')
        self.sp_source = self._nested_source('SPT')
        self.teff = self._nested_value('TEFF')
        self.teff_source = self._nested_source('TEFF')
        # plain top-level scalars
        self.epoch = self.entry.get('EPOCH')
        self.notes = self.entry.get('NOTES') or ''

    def _nested_value(self, key: str) -> Any:
        """Return ``entry[key]['value']`` if nested, else ``entry[key]``."""
        val = self.entry.get(key)
        if isinstance(val, dict):
            return val.get('value')
        return val

    def _nested_source(self, key: str) -> Any:
        """Return ``entry[key]['source']`` if nested, else None."""
        val = self.entry.get(key)
        if isinstance(val, dict):
            return val.get('source')
        return None

    # -------------------------------------------------------------------------
    # Public utilities used by the recipes
    # -------------------------------------------------------------------------
    def all_aliases(self) -> None:
        """
        Strip whitespace from all aliases and store back as a clean
        pipe-separated string.
        """
        # split, strip, drop blanks, and collapse duplicates
        if not self.aliases:
            return
        items = [a.strip() for a in self.aliases.split('|') if a.strip()]
        # uniquify while preserving order
        seen: Dict[str, int] = dict()
        unique_items: List[str] = []
        for item in items:
            if item not in seen:
                seen[item] = 1
                unique_items.append(item)
        # write back to both flat string and entry dict
        self.aliases = '|'.join(unique_items)
        self.entry['ALIASES'] = unique_items

    def stamp_note(self, prefix: str = '') -> None:
        """
        Append a ``Added on ... by user@host using <NAME>`` provenance note.
        """
        nargs = [Time.now().iso, getpass.getuser(),
                 socket.gethostname(), __NAME__]
        note = ' Added on {0} by {1}@{2} using {3}'.format(*nargs)
        # build the new combined notes string
        existing = self.notes or ''
        sep = '' if not existing else ' '
        self.notes = (prefix + sep + existing + note).strip()
        self.entry['NOTES'] = self.notes


# =============================================================================
# Define worker functions
# =============================================================================
def _entry_to_astroobj(name: str,
                       entry: Dict[str, Any]) -> AstroObj:
    """Construct an :class:`AstroObj` from a yaml entry dict."""
    return AstroObj(name=name, entry=entry)


def _is_null(value: Any) -> bool:
    """Match the null-string conventions used by the recipe inputs."""
    return drs_text.null_text(value, ['None', 'Null', ''])


# =============================================================================
# Public API consumed by apero_astrometrics.py
# =============================================================================
def identify_from_file(params: ParamDict) -> ParamDict:
    """
    Identify a target by RA/DEC from a fits header and let the user pick
    one of the closest SIMBAD matches; populate
    ``params['INPUTS']['OBJECTS']`` with the chosen name.

    Network access is required (SIMBAD via astroquery).

    :param params: ParamDict, the parameter dictionary of constants
    :return: ParamDict, the updated parameter dictionary
    """
    # lazy imports - astroquery / astropy are optional in some envs
    from astropy.io import fits
    from astropy.coordinates import SkyCoord
    from astroquery.simbad import Simbad
    # get file option from inputs
    fileoption = params['INPUTS']['fileoption']
    # nothing to do if no file given
    if fileoption == 'None':
        return params
    # try to read the header
    try:
        header = fits.getheader(fileoption)
    except Exception:
        WLOG(params, 'warning',
             'File: {0} invalid (cannot read header)'.format(fileoption))
        return params
    # locate the raw object name
    kw_objname1 = params['KW_OBJECTNAME2'][0]
    kw_objname = params['KW_OBJECTNAME'][0]
    rawobjname = None
    if kw_objname1 in header:
        rawobjname = header[kw_objname1]
    if rawobjname is None and kw_objname not in header:
        eargs = [kw_objname, fileoption]
        raise AperoCodedException(params, '01-001-00027', targs=eargs)
    if rawobjname is None:
        rawobjname = header[kw_objname]
    # extract coordinates from header
    ra = header[params['KW_OBJRA'][0]]
    dec = header[params['KW_OBJDEC'][0]]
    # log progress
    msg = ('Trying to identify from file: {0}'
           '\n\t NAME = {1}\n\t RA = {2}\n\t DEC = {3}'
           '\n\n Note "NAME" should be added as an alias later!')
    WLOG(params, '', msg.format(fileoption, rawobjname, ra, dec))
    # build SkyCoord and query SIMBAD region
    coord = SkyCoord(ra, dec, unit='deg')
    with warnings.catch_warnings(record=True):
        Simbad.add_votable_fields('flux(H)', 'flux(V)')
        result = Simbad.query_region(coord, radius='0d1m0s')
    # mask any missing magnitudes for sorting
    if 'FLUX_H' in result.colnames:
        h_mask = result['FLUX_H'].mask
        result['FLUX_H'][h_mask] = 99
    if 'FLUX_V' in result.colnames:
        v_mask = result['FLUX_V'].mask
        result['FLUX_V'][v_mask] = 99
    # sort and keep brightest 10 by H
    sortmask = np.argsort(result['FLUX_H'])
    names = result['MAIN_ID'][sortmask][:10]
    hmags = result['FLUX_H'][sortmask][:10]
    vmags = result['FLUX_V'][sortmask][:10]
    options = list(np.arange(1, len(names) + 1).astype(int))
    max_name_len = max(len(name) for name in names)
    # build option labels
    optionsstr = []
    for it, name in enumerate(names):
        line = ('{0}: {1:<{w}}  H={2:.2f}  V={3:.2f}'
                .format(it + 1, name, hmags[it], vmags[it],
                        w=max_name_len))
        optionsstr.append(line)
    # ask user
    question = ('Closest {0} nearest objects sorted by H mag.'
                '\n\nPick a number from 1 to {0}').format(len(names))
    uinput = drs_installation.ask(question, dtype=int, options=options,
                                  optiondesc=optionsstr, color='m')
    chosen = names[uinput - 1]
    # update inputs
    params['INPUTS'].set('OBJECTS', value=chosen)
    params['INPUTS'].set('ALIASES', value=rawobjname)
    msg = ('Updated the following inputs:\n\t OBJECTS = {0}'
           '\n\t ALIASES = {1}')
    WLOG(params, '', msg.format(chosen, rawobjname))
    return params


def check_database(params: ParamDict, shortname: str) -> None:
    """
    Print a summary of the local astrometric database to the log.

    :param params: ParamDict, the parameter dictionary of constants
    :param shortname: str, the calling recipe short name
    :return: None (prints a table)
    """
    # construct the database
    objdbm = AstrometricDatabase(params, shortname=shortname)
    objdbm.load_db()
    # report total count
    total = objdbm.count()
    WLOG(params, 'info', 'Astrometric database: {0} entries'.format(total))
    # iterate alphabetically
    entries = objdbm.get_entries(columns='*')
    if not entries:
        WLOG(params, '', '\t(empty)')
        return
    # build the table header
    msg = '{0:<20s} {1:<20s} {2:<25s}'
    margs = ['APERO_NAME', 'ORIGINAL_NAME', 'ALIASES']
    WLOG(params, '', msg.format(*margs))
    WLOG(params, '', '-' * 70)
    # sort by APERO_NAME for stable display
    entries_sorted = sorted(
        entries, key=lambda e: str(e.get('APERO_NAME') or ''))
    for entry in entries_sorted:
        ap = str(entry.get('APERO_NAME') or '')
        og = str(entry.get('ORIGINAL_NAME') or '')
        aliases = entry.get('ALIASES') or []
        if isinstance(aliases, list):
            alias_str = ', '.join(str(a) for a in aliases[:3])
            if len(aliases) > 3:
                alias_str += ', ...'
        else:
            alias_str = str(aliases)
            
        msg = '{0:<20s} {1:<20s} {2:<25s}'
        margs = [ap, og, alias_str]
        WLOG(params, '', msg.format(*margs))


def query_database(params: ParamDict, shortname: str,
                   rawobjnames: List[str], overwrite: bool = False
                   ) -> Tuple[List[str], List[str]]:
    """
    Split ``rawobjnames`` into (unfound, found) against the local archive.

    :param params: ParamDict, the parameter dictionary of constants
    :param shortname: str, the calling recipe shortname
    :param rawobjnames: list of str, raw object names to check
    :param overwrite: bool, if True force every name into the unfound list
                      so it gets re-queried.

    :return: ``(unfound_names, found_apero_names)``
    """
    # build the database
    objdbm = AstrometricDatabase(params, shortname=shortname)
    objdbm.load_db()
    # accumulate
    unfound: List[str] = []
    found: List[str] = []
    # iterate each name
    for raw in rawobjnames:
        # accept comma-separated bundles for convenience
        for one in str(raw).split(','):
            one = one.strip()
            if not one:
                continue
            if overwrite:
                unfound.append(one)
                continue
            apero_name, ok = objdbm.find_objname(one)
            if ok:
                found.append(apero_name)
            else:
                unfound.append(one)
    # log a summary
    WLOG(params, 'info',
         'Database lookup: {0} found, {1} unfound'.format(
             len(found), len(unfound)))
    return unfound, found


def check_object(params: ParamDict, recipe: DrsRecipe,
                 found_objs: List[str]) -> None:
    """
    Stub for the legacy QC-issue check. Logs the list of already-known
    objects so the user can spot anything unexpected; the gsheet-backed
    QC reject list previously implemented here is no longer required for
    the yaml-backed archive (each entry stands on its own).

    :param params: ParamDict, the parameter dictionary of constants
    :param recipe: DrsRecipe, the calling recipe
    :param found_objs: list of str, the APERO_NAMES already in the db
    :return: None
    """
    _ = recipe  # kept for API compat
    if not found_objs:
        return
    msg = '{0} objects already in the local archive:'.format(
        len(found_objs))
    WLOG(params, '', msg)
    for obj in found_objs:
        WLOG(params, '', '\t- {0}'.format(obj))


def query_simbad(params: ParamDict, rawobjname: str
                 ) -> Tuple[List[AstroObj], str]:
    """
    Resolve ``rawobjname`` against SIMBAD/Gaia/VizieR via the core
    resolver and wrap the result in an :class:`AstroObj`.

    :param params: ParamDict, the parameter dictionary of constants
    :param rawobjname: str, the raw object name to resolve

    :return: ``(astro_objs, reason)`` - ``astro_objs`` will contain a
             single :class:`AstroObj` on success or be empty on failure.
             ``reason`` describes the failure mode for the recipe to
             display.
    """
    # construct the database (only used for path / config)
    objdbm = AstrometricDatabase(params, shortname='ASTRO-UP')
    # log progress
    WLOG(params, '', 'Querying SIMBAD/Gaia for "{0}"'.format(rawobjname))
    # delegate to core
    entry = objdbm.resolve_target(rawobjname)
    # nothing returned - report failure
    if entry is None:
        return [], '\n\tSIMBAD did not resolve "{0}".'.format(rawobjname)
    # wrap and stamp provenance
    astro_obj = _entry_to_astroobj(rawobjname, entry)
    astro_obj.stamp_note('Added via SIMBAD resolution.')
    return [astro_obj], ''


def lookup(params: ParamDict, rawobjname: str
           ) -> Tuple[Optional[AstroObj], str]:
    """
    Fall-back resolver for objects not in SIMBAD.

    The yaml-backed core already exhausts SIMBAD/Gaia/VizieR via
    :meth:`AstrometricDatabase.resolve_target`, so this function is now
    a no-op kept only for API compatibility with the
    ``apero_astrometrics`` recipe.

    :param params: ParamDict, the parameter dictionary of constants
    :param rawobjname: str, the raw object name to look up
    :return: ``(None, reason)`` always - core has already tried the
             available catalogues.
    """
    _ = params, rawobjname
    return None, '\n\tNo additional proper-motion catalogue lookup.'


def ask_user(params: ParamDict, recipe: DrsRecipe,
             astro_obj: AstroObj) -> Tuple[AstroObj, bool]:
    """
    Walk the user through confirming an astrometric resolution and
    optionally rename / add aliases.

    :param params: ParamDict, the parameter dictionary of constants
    :param recipe: DrsRecipe, the calling recipe
    :param astro_obj: AstroObj, the candidate object

    :return: ``(astro_obj, add_to_list)`` - ``add_to_list`` is True if
             the user accepted the entry.
    """
    _ = recipe  # kept for API compat
    # display the candidate
    msg = (
        '\nCandidate astrometric entry for "{0}":'
        '\n\t APERO_NAME    = {1}'
        '\n\t ORIGINAL_NAME = {2}'
        '\n\t SIMBAD_NAME   = {3}'
        '\n\t RA / DEC      = {4} / {5}'
        '\n\t PMRA / PMDE   = {6} / {7}'
        '\n\t PLX           = {8}'
        '\n\t RV            = {9}'
        '\n\t TEFF          = {10}'
        '\n\t SP_TYPE       = {11}'
    )
    margs = [astro_obj.name, astro_obj.objname, astro_obj.original_name,
             astro_obj.entry.get('SIMBAD_NAME'), astro_obj.ra,
             astro_obj.dec, astro_obj.pmra, astro_obj.pmde,
             astro_obj.plx, astro_obj.rv, astro_obj.teff,
             astro_obj.sp_type]
    WLOG(params, '', msg.format(*margs))
    # ask whether to accept
    question = '\nAdd OBJECT="{0}" to local astrometric archive?'
    cond = drs_installation.ask(question.format(astro_obj.name),
                                dtype='YN', color='m')
    if not cond:
        return astro_obj, False
    # optionally let the user add user-supplied aliases (recipe-level input)
    user_aliases = params['INPUTS'].get('ALIASES', None)
    if user_aliases not in [None, 'None', '', 'NULL']:
        existing = astro_obj.aliases.split('|') if astro_obj.aliases else []
        new = [a.strip() for a in str(user_aliases).split(',')
               if a.strip()]
        astro_obj.aliases = '|'.join(existing + new)
    # normalise aliases
    astro_obj.all_aliases()
    return astro_obj, True


def add_obj_to_sheet(params: ParamDict,
                     astro_objs: List[AstroObj]) -> None:
    """
    Persist a list of :class:`AstroObj` into the local yaml archive.

    The legacy implementation also pushed entries to the online "pending
    list" google-sheet; with the yaml-backed archive there is no
    upstream sheet, so this function now just writes each entry to disk.

    :param params: ParamDict, the parameter dictionary of constants
    :param astro_objs: list of AstroObj, entries to persist
    :return: None
    """
    if not astro_objs:
        return
    # build the database
    objdbm = AstrometricDatabase(params, shortname='ASTRO-UP')
    # collect entry dicts
    entries: List[Dict[str, Any]] = []
    for astro_obj in astro_objs:
        # ensure aliases are in clean list form
        astro_obj.all_aliases()
        # propagate flat fields back into the entry dict (in case the
        # caller mutated them after construction)
        astro_obj.entry['APERO_NAME'] = astro_obj.objname
        astro_obj.entry['ORIGINAL_NAME'] = astro_obj.original_name
        if astro_obj.notes:
            astro_obj.entry['NOTES'] = astro_obj.notes
        entries.append(astro_obj.entry)
    # write all entries (per-file lock, atomic write)
    objdbm.add_entries(entries, overwrite=True, merge=True)
    # log progress
    msg = 'Added {0} entries to the local astrometric archive ({1})'
    WLOG(params, '', msg.format(len(entries), objdbm.path))


def add_object_reject(params: ParamDict, raw_objname: str) -> None:
    """
    Add an object to the local reject list (a yaml file under the
    astrometrics directory).

    :param params: ParamDict, the parameter dictionary of constants
    :param raw_objname: str or comma-separated list of names to reject
    :return: None
    """
    # build the database to discover the astrometrics dir
    objdbm = AstrometricDatabase(params, shortname='REJECT')
    # split comma-separated bundles
    if ',' in raw_objname:
        objnames = [n.strip() for n in raw_objname.split(',') if n.strip()]
    else:
        objnames = [raw_objname]
    # path to the local reject list
    reject_path = os.path.join(objdbm.path, 'reject_list.yaml')
    # load existing reject list (or start fresh)
    reject_data: Dict[str, Any] = dict()
    if os.path.exists(reject_path):
        try:
            import yaml as _yaml
            with open(reject_path, 'r', encoding='utf-8') as fh:
                reject_data = _yaml.safe_load(fh) or dict()
        except Exception:
            reject_data = dict()
    reject_data.setdefault('OBJECTS', dict())
    # check input mode (auto-fill or interactive)
    autofill = params['INPUTS'].get('autofill', None)
    test = params['INPUTS'].get('test', False)
    # append each name
    for objname in objnames:
        apero_objname = clean_object(objname)
        # skip duplicates
        if apero_objname in reject_data['OBJECTS']:
            existing = reject_data['OBJECTS'][apero_objname]
            msg = 'Object {0} (APERO={1}) already in reject list: {2}'
            WLOG(params, '', msg.format(objname, apero_objname,
                                        existing.get('NOTES', '')))
            continue
        # gather aliases / bad_astro / notes
        if autofill not in [None, 'None']:
            parts = str(autofill).split(',')
            if len(parts) != 3:
                emsg = ('Auto fill must be in the form '
                        'ALIASES,BAD_ASTRO,NOTES')
                raise AperoCodedException(params, message=emsg)
            aliases, bad_astro, notes = parts
        else:
            qfmt = ('Enter aliases for object={0} (APERO={1}) separate '
                    'aliases by a "|"')
            aliases = drs_installation.ask(
                qfmt.format(objname, apero_objname), dtype=str)
            qfmt = ('Reject object={0} (APERO={1}) due to bad/no '
                    'proper motion?')
            bad_astro = drs_installation.ask(
                qfmt.format(objname, apero_objname), dtype='YN')
            qfmt = 'Enter a comment to reject object={0} (APERO={1})'
            notes = drs_installation.ask(
                qfmt.format(objname, apero_objname), dtype=str)
        # build the reject entry
        entry = dict()
        entry['ORIGINAL_NAME'] = objname
        entry['ALIASES'] = aliases
        entry['BAD_ASTROMETRICS'] = bad_astro
        entry['NOTES'] = notes
        entry['DATE_ADDED'] = Time.now().iso
        reject_data['OBJECTS'][apero_objname] = entry
        msg = 'Object {0} (APERO={1}) queued for rejection.'
        WLOG(params, '', msg.format(objname, apero_objname))
    # write back atomically (unless test mode)
    if not test:
        import tempfile
        import yaml as _yaml
        # ensure the parent directory exists
        os.makedirs(os.path.dirname(reject_path), exist_ok=True)
        # write to a temp file and replace
        fd, tmppath = tempfile.mkstemp(prefix='reject_',
                                       suffix='.yaml',
                                       dir=os.path.dirname(reject_path))
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as fh:
                _yaml.safe_dump(reject_data, fh, sort_keys=False,
                                allow_unicode=False)
            os.replace(tmppath, reject_path)
        except Exception:
            # clean up the tempfile if anything failed
            if os.path.exists(tmppath):
                os.unlink(tmppath)
            raise
        WLOG(params, '', 'Reject list updated: {0}'.format(reject_path))


def update_astrometrics(params: ParamDict) -> None:
    """
    Refresh the local astrometric archive against SIMBAD/Gaia/VizieR.

    Thin wrapper around :meth:`AstrometricDatabase.update_archive`.

    :param params: ParamDict, the parameter dictionary of constants
    :return: None
    """
    # construct the database
    objdbm = AstrometricDatabase(params, shortname='ASTRO-UP')
    objdbm.load_db()
    # honour the --overwrite_existing input if present
    overwrite = bool(params['INPUTS'].get('overwrite_existing', False))
    # run the refresh
    counts = objdbm.update_archive(overwrite_existing=overwrite)
    # log summary
    msg = ('Archive refresh complete - resolved={0}, failed={1}, '
           'skipped={2}')
    WLOG(params, 'info', msg.format(counts['resolved'], counts['failed'],
                                    counts['skipped']))


def update_teffs(params: ParamDict, shortname: str) -> None:
    """
    Compatibility shim for the legacy ``--update_teffs`` CLI mode.
    Delegates to :func:`update_astrometrics` (the per-target Teff field
    is refreshed during a full archive update).

    :param params: ParamDict, the parameter dictionary of constants
    :param shortname: str, the calling recipe shortname
    :return: None
    """
    _ = shortname
    update_astrometrics(params)


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    # minimal CLI harness mirroring the legacy entry points
    _args = sys.argv
    # load_pconfig is not required for the new yaml backend; we only need
    # a parameter dictionary populated with DRS_DATA_ASSETS to run.
    from aperocore.constants import load_functions
    from apero.instruments import select
    _params = load_functions.load_config(select.INSTRUMENTS)
    _params['PID'], _ = drs_startup.assign_pid()
    _params['RECIPE'] = __NAME__
    _params['RECIPE_SHORT'] = str('ASTRO-UP')
    if '--update_coords' in _args or '--update_teffs' in _args:
        update_astrometrics(_params)
    else:
        check_database(_params, 'ASTRO-UP')

# =============================================================================
# End of code
# =============================================================================
