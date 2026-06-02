#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Raw APERO check that every raw-file object name resolves in the astrometric database."""

from typing import Optional, Tuple

import apero_ri.apero_monitoring.core.raw_common as raw_common
from apero_ri.apero_monitoring.core.core import AperoCheck
from apero_ri.apero_monitoring.core import contacts
from apero_ri.apero_monitoring.core import links


# =============================================================================
# Define variables
# =============================================================================
CHECK_NAME = 'ASTROM'
CHECK_HUMAN_NAME = 'Astrometric Object Name Check'
CHECK_TYPE = 'raw'
INSTRUMENTS = ['SPIROU', 'NIRPS_HE', 'NIRPS_HA']

CHECK = AperoCheck(CHECK_NAME, CHECK_HUMAN_NAME, CHECK_TYPE, INSTRUMENTS)
CHECK.dependencies = ['BLANK', 'HAS_OBSDIR']

CHECK.description = """
This test checks that every raw FITS file whose header contains an object
name can be resolved in the APERO astrometric database (by exact name,
registered alias, or cleaned name variant).  Files that carry no object
name in any of the configured header keys are skipped.
"""

CHECK.what_to_do = f"""
If FALSE please [re-run the check]({links.RUN_CHECK}) with --test=ASTROM.

For each failing file, the object name listed in the report was not found
in the astrometric database.

Go to the ARI astrometrics resolve page, search for the name, and either:
  - Add a new entry for the target if it is genuinely absent.
  - Add the raw header name as an alias to an existing entry.

Contact <CONTACT:C1> if you need help determining the correct target, or
<CONTACT:C2> if you need help adding the entry to the database.
"""

clist1 = contacts.AperoCheckContactList()
clist1.add(contacts.NJC, starred=True)
clist1.add(contacts.EA)
clist1.add(contacts.LM)

clist2 = contacts.AperoCheckContactList()
clist2.add(contacts.NJC, starred=True)

CHECK.contact_list['C1'] = clist1
CHECK.contact_list['C2'] = clist2


# =============================================================================
# Internal helpers
# =============================================================================
def _resolve_astrom(name: str) -> Optional[str]:
    """Resolve *name* in the astrometric database and return the APERO name.

    Returns the APERO_NAME string on success, or None when the name cannot be
    resolved or any network/server error occurs.  The server-side resolver
    checks the APERO_NAME field, all registered aliases, and normalised
    (alphanumeric-only) name variants.
    """
    try:
        from apero_ri.ari_api import astrometrics as _astro_api
        result = _astro_api.resolve_by_name(name)
        if result.get('success', False):
            return str(result.get('apero_name', '') or '').strip() or name
        return None
    except Exception:
        return None


# =============================================================================
# Define check function
# =============================================================================
def check_function(instrument: str, obs_dir: str,
                   aparams: dict, dbparams: dict) -> Tuple[bool, str]:
    """Check that every science-file object name resolves in the astrometric database.

    Files are first filtered to science frames.  When ``sci_suffix`` is set
    (e.g. ``o.fits`` for SPIRou), only files whose name ends with that suffix
    pass the filter — no header read is needed for the filter step.  When
    ``sci_suffix`` is empty, the ``dprtypes`` allowlist is used instead (DPRTYPE
    header key read required).  Non-matching files are counted and skipped.
    The object name is then read from the first non-empty key in
    ``obj_name_keys``; files with no matching header key are counted and skipped.
    Files whose name cannot be resolved in the astrometric database are reported
    as failures.

    :param instrument: APERO instrument name (unused by this check body).
    :param obs_dir: Obsdir identifier currently being validated.
    :param aparams: Hydrated APERO profile parameters.
    :param dbparams: Database parameters (unused by this check body).
    :return: Tuple of pass flag and formatted report text.
    """
    _ = instrument, dbparams

    if not raw_common.is_check_enabled(aparams, 'astrom_test', default=True):
        return True, 'Skipped astrom_test: disabled.'

    obs_path, files = raw_common.list_obsdir_files(aparams, obs_dir)
    if not obs_path.exists():
        return False, f'Observation directory {obs_dir} does not exist.'
    if not files:
        return False, f'No FITS files found in {obs_path}'

    # Load the ordered list of header keys to try for the object name.
    obj_name_keys = raw_common.get_check_value(
        aparams, 'astrom_test', ['obj_name_keys'], [])
    obj_name_keys = list(obj_name_keys) if isinstance(obj_name_keys, list) else []
    if not obj_name_keys:
        return True, 'No obj_name_keys configured for astrom_test; check skipped.'

    # Load the science filter config: suffix takes priority over DPRTYPE list.
    sci_suffix = str(raw_common.get_check_value(
        aparams, 'astrom_test', ['sci_suffix'], '') or '').strip()
    sci_dprtypes = raw_common.get_check_value(
        aparams, 'astrom_test', ['dprtypes'], [])
    sci_dprtypes = set(sci_dprtypes) if isinstance(sci_dprtypes, list) else set()
    dpr_key = raw_common.get_header_key(aparams, 'dpr_type')

    # resolved_objects: ordered unique (obj_key, header_name, apero_name) tuples
    resolved_objects = []
    resolved_seen = set()
    failed_lines = []
    n_nonsci = 0
    n_no_objname = 0

    for filename in files:
        # Science filter: suffix check takes priority over DPRTYPE header.
        if sci_suffix:
            if not filename.name.endswith(sci_suffix):
                n_nonsci += 1
                continue
        elif sci_dprtypes and dpr_key:
            header = raw_common.read_primary_header(filename)
            dpr_type = str(header.get(dpr_key, '') or '').strip()
            if dpr_type not in sci_dprtypes:
                n_nonsci += 1
                continue

        header = raw_common.read_primary_header(filename)

        # Try each key in order; record the key used and the value found.
        obj_key = ''
        obj_name = ''
        for key in obj_name_keys:
            val = str(header.get(key, '') or '').strip()
            if val:
                obj_key = key
                obj_name = val
                break

        # Files with no object name header key are skipped but counted.
        if not obj_name:
            n_no_objname += 1
            continue

        apero_name = _resolve_astrom(obj_name)
        if apero_name is not None:
            entry = (obj_key, obj_name, apero_name)
            if entry not in resolved_seen:
                resolved_seen.add(entry)
                resolved_objects.append(entry)
        else:
            failed_lines.append(
                f'\t{obj_key}: {obj_name}  (filename: {filename.name})'
            )

    # Build passed lines: one line per unique resolved (key, name, apero_name).
    passed_lines = []
    for obj_key, obj_name, apero_name in resolved_objects:
        passed_lines.append(f'\t{obj_key}: {obj_name}  (APERO: {apero_name})')

    # Append skipped-file summary to passed lines for visibility.
    if n_nonsci > 0:
        passed_lines.append(
            f'\t({n_nonsci} non-science file(s) skipped by DPRTYPE/suffix filter)'
        )
    if n_no_objname > 0:
        passed_lines.append(
            f'\t({n_no_objname} file(s) skipped: no object name in header)'
        )

    # An obsdir with only skipped files is treated as a pass with explanation.
    if not passed_lines and not failed_lines:
        return True, f'No science files with object names found in {obs_dir}; nothing to check.'

    return raw_common.build_report(obs_dir, passed_lines, failed_lines)


# =============================================================================
# Must put the function to run for this check
# =============================================================================
CHECK.func = check_function


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    _instrument = 'NIRPS_HA'
    _obs_dir = '2021-01-01'
    _aparams = raw_common.load_example_aparams(_instrument)
    _dbparams = dict()
    CHECK(_instrument, _obs_dir, _aparams, _dbparams, check_dict={})
    print(CHECK.report())


# =============================================================================
# End of code
# =============================================================================
