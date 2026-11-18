#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Legacy sheet rows import from sheet values when SIMBAD is unreachable."""
from pathlib import Path

import yaml

from apero_ri.tasks import legacy_astrom_gsheet as lag

# =============================================================================
# Define variables
# =============================================================================
# A pending-tab row like TOI260 (values only need to be plausible).
TOI_ROW = dict(OBJNAME='TOI260', ORIGINAL_NAME='TOI-260',
               ALIASES='TIC 37749396|TOI-260', RA_DEG='5.3412',
               RA_SOURCE='Gaia DR3', DEC_DEG='-24.9861',
               DEC_SOURCE='Gaia DR3', EPOCH='2016.0', PMRA='114.1',
               PMRA_SOURCE='Gaia DR3', PMDE='-62.6', PMDE_SOURCE='Gaia DR3',
               PLX='49.6', PLX_SOURCE='Gaia DR3', RV='', RV_SOURCE='',
               TEFF='4100', TEFF_SOURCE='', SP_TYPE='K6V', SP_SOURCE='',
               NOTES='', USED=1)


# =============================================================================
# Define functions
# =============================================================================
def _add(tmp_path: Path, row: dict, monkeypatch) -> dict:
    """Run the import with the online resolver failing (SIMBAD down)."""
    from apero_ri.core import issues

    monkeypatch.setattr(lag, '_resolve_online_entry', lambda name: None)
    monkeypatch.setattr(issues, 'create_issue', lambda **kwargs: None)
    astrom_root = tmp_path / 'apero-assets' / 'astrometrics'
    astrom_root.mkdir(parents=True)
    add_kwargs = dict(astrom_root=astrom_root, sheet_row=row,
                      task_logger=None, tolerance_arcsec=5.0,
                      created_by='test', dry_run=False)
    return lag._add_sheet_object_to_ari(**add_kwargs)


def test_unresolvable_row_imports_from_sheet(tmp_path: Path,
                                             monkeypatch) -> None:
    """A sheet row with coordinates is imported as pending, not dropped."""
    from apero.core import drs_astrometrics as dra

    result = _add(tmp_path, dict(TOI_ROW), monkeypatch)
    assert result['status'] == 'added_to_ari'
    assert result['from_sheet'] is True
    astrom_root = tmp_path / 'apero-assets' / 'astrometrics'
    # The ASTROM check resolves the raw header name through aliases.
    entry = dra.find_by_name(str(astrom_root), 'TOI-260')
    assert entry is not None
    assert entry['STATUS'] == 'pending'
    assert entry['RA']['value'] == 5.3412
    assert entry['PMRA']['source'] == 'Gaia DR3'
    assert 'Online resolution failed' in entry['NOTES']
    files = list((astrom_root / 'pending').glob('*.yaml'))
    assert len(files) == 1
    assert yaml.safe_load(files[0].read_text())['APERO_NAME'] == 'TOI260'


def test_row_without_coordinates_stays_unresolved(tmp_path: Path,
                                                  monkeypatch) -> None:
    """Rows with no usable RA/Dec cannot be imported."""
    row = dict(TOI_ROW, RA_DEG='', DEC_DEG='')
    result = _add(tmp_path, row, monkeypatch)
    assert result['status'] == 'unresolved'
