#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Exercise error paths corrected by the package-wide undefined-name audit."""

import importlib
from pathlib import Path
from unittest import mock

import numpy as np
from astropy import units as uu
from astropy.coordinates import SkyCoord
from astropy.time import Time
import pytest

from apero.dev import get_base_params
from aperocore.core import drs_log
from apero.recipes.nirps_he import apero_pp_ref_nirps_he
from apero.tools.module.ari import ari_find
from apero.tools.module.ari import ari_pages
from apero.tools.module.setup import drs_reset


@pytest.mark.parametrize('instrument', ['spirou', 'nirps_ha', 'nirps_he'])
def test_dark_short_exposure_raises_formatted_error(
        monkeypatch: pytest.MonkeyPatch, instrument: str) -> None:
    """Keep the short-exposure diagnostic consistent across instruments.

    :param monkeypatch: Fixture replacing file, database, and logging calls.
    :param instrument: Instrument whose dark recipe is exercised.
    :return: None.
    """
    module_name = f'apero.recipes.{instrument}.apero_dark_{instrument}'
    module = importlib.import_module(module_name)
    params = get_base_params(instrument.upper())
    infile = mock.Mock(basename='dark.fits')
    infile.get_data.return_value = np.zeros((2, 2))
    infile.get_hkey.side_effect = [8.0, 1.0, 'DARK_DARK']
    params['INPUTS'] = dict(FILES=(None, [infile]))
    params['DATA_DICT'] = dict()
    params['IMAGE.COMBINE_INPUT'] = False
    params['CAL.DARK.QC_DARK_TIME'] = 10.0
    monkeypatch.setattr(module.drs_file, 'check_input_qc',
                        mock.Mock(return_value=[infile]))
    monkeypatch.setattr(module.drs_database, 'CalibrationDatabase',
                        mock.Mock())
    monkeypatch.setattr(module.drs_startup, 'file_processing_update',
                        mock.Mock())
    monkeypatch.setattr(module, 'WLOG', mock.Mock())
    recipe = mock.Mock()

    with pytest.raises(drs_log.AperoCodedException) as caught:
        module.__main__(recipe, params)

    expected = module.textentry('09-011-00006', args=[10.0])
    assert str(expected) in str(caught.value)


def test_ppref_invalid_type_raises_coded_error() -> None:
    """Reject unsupported PPREF input with its formatted coded exception."""
    params = get_base_params('NIRPS_HE')
    params['INPUTS'] = dict(FILETYPE=['INVALID_TEST_TYPE'])
    params['PP.ALLOWED_PPM_TYPES'] = ['DARK']
    recipe = mock.Mock()
    with pytest.raises(drs_log.AperoCodedException) as caught:
        apero_pp_ref_nirps_he.__main__(recipe, params)
    message = str(caught.value)
    assert 'INVALID_TEST_TYPE' in message
    assert 'DARK' in message
    recipe.plot.set_location.assert_called_once_with()


@pytest.mark.parametrize('catalog', ['gaia', '2mass'])
def test_finder_retry_exhaustion(
    monkeypatch: pytest.MonkeyPatch, catalog: str,
) -> None:
    """Preserve the final warning after ten failed offline catalog attempts.

    :param monkeypatch: Fixture replacing network, logging, and delay calls.
    :param catalog: Finder catalog whose retry loop is exercised.
    :return: None.
    """
    params = get_base_params('NIRPS_HE')
    params['ARI_FINDER'] = dict(MAX_PM=1 * uu.arcsec / uu.year,
                               SIGMA_LIMIT=3, MAG_LIMIT=20)
    coords = SkyCoord(10 * uu.deg, 20 * uu.deg)
    obstime = Time('2026-01-01')
    radius = 1 * uu.arcmin
    logger = mock.Mock()
    monkeypatch.setattr(ari_find, 'WLOG', logger)
    monkeypatch.setattr(ari_find.time, 'sleep', mock.Mock())
    failure = RuntimeError('offline catalog failure')
    if catalog == 'gaia':
        query = mock.Mock(side_effect=failure)
        tap = mock.Mock(launch_job=query)
        monkeypatch.setattr(ari_find, 'TapPlus', mock.Mock(return_value=tap))
        query_args = [params, coords, obstime, radius]
        with pytest.raises(drs_log.AperoCodedException) as caught:
            ari_find.get_gaia_sources(*query_args)
    else:
        query = mock.Mock(side_effect=failure)
        monkeypatch.setattr(ari_find, 'get_2mass_field', query)
        query_args = [params, dict(), coords, obstime, radius]
        with pytest.raises(drs_log.AperoCodedException) as caught:
            ari_find.get_2mass_sources(*query_args)
    assert query.call_count == 10
    assert logger.call_count == 10
    message = str(caught.value)
    assert '10' in message
    assert 'offline catalog failure' in message
    assert message == str(logger.call_args.args[2])


def test_finder_page_builds_object_table(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Build the finder table before stopping at the chart-generation boundary.

    :param monkeypatch: Fixture replacing the object database and chart setup.
    :return: None.
    """
    params = get_base_params('NIRPS_HE')
    database = mock.Mock()
    database.get_entries.return_value = [dict(OBJNAME='TEST_OBJECT')]
    constructor = mock.Mock(return_value=database)
    monkeypatch.setattr(ari_pages.drs_astrometrics, 'AstrometricDatabase',
                        constructor)
    boundary = mock.Mock(side_effect=RuntimeError('chart generation boundary'))
    monkeypatch.setattr(ari_pages.ari_find, 'load_params', boundary)
    with pytest.raises(RuntimeError, match='chart generation boundary'):
        ari_pages.make_finder_page(params)
    database.load_db.assert_called_once_with()
    database.get_entries.assert_called_once_with()
    boundary.assert_called_once_with(params)


def test_reset_missing_directory_prompt(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    """Format the create-directory prompt and create only a temporary path.

    :param monkeypatch: Fixture replacing user input and deletion calls.
    :param tmp_path: Fixture providing an isolated temporary directory.
    :return: None.
    """
    params = get_base_params('NIRPS_HE')
    path = str(tmp_path / 'missing')
    user_input = mock.Mock(return_value='Y')
    monkeypatch.setattr('builtins.input', user_input)
    monkeypatch.setattr(drs_reset, 'WLOG', mock.Mock())
    remover = mock.Mock(return_value=True)
    monkeypatch.setattr(drs_reset, 'fast_rm_remove', remover)
    drs_reset.remove_all(params, path)
    assert (tmp_path / 'missing').is_dir()
    assert path in user_input.call_args.args[0]
    remover.assert_called_once_with(path)