#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Regression coverage for the cached TAPAS telluric file location."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import numpy as np
import pytest
from astropy.table import Table

from apero.core.drs_database import TelluricDatabase
from apero.science.telluric import gen_tellu


class _TapasFile:
    """Minimal TELLU_TAPAS file definition recording the written path."""

    def __init__(self) -> None:
        """Initialise the fake file with no filename or data.

        :return: None.
        """
        self.filename = None
        self.data = None
        self.header = None
        self.hdict = None

    def newcopy(self, params: dict) -> '_TapasFile':
        """Return this instance as the copied file definition.

        :param params: Unused parameter dictionary.
        :return: The same fake file instance.
        """
        _ = params
        return self

    def get_dbkey(self) -> str:
        """Return the telluric database key.

        :return: The TAPAS database key.
        """
        return 'TELLU_TAPAS'

    def construct_filename(self, path: str) -> None:
        """Store the cache filename in the requested directory.

        :param path: Directory used for the cache file.
        :return: None.
        """
        self.filename = str(Path(path) / 'tapas_spl.npy')

    def write_npy(self, block_kind: str, runstring: str) -> None:
        """Write cached data to the constructed filename.

        :param block_kind: Unused output block kind.
        :param runstring: Unused recipe run string.
        :return: None.
        """
        _ = block_kind, runstring
        np.save(self.filename, self.data)


def test_tapas_cache_matches_lookup(tmp_path: Path,
                                    monkeypatch: pytest.MonkeyPatch) -> None:
    """Write an objectless TAPAS cache where telluric lookup resolves it.

    :param tmp_path: Temporary telluric root supplied by pytest.
    :param monkeypatch: Fixture replacing file, data, and logging access.
    :return: None.
    """
    tapas_file = _TapasFile()
    tapas = Table()
    tapas['wavelength'] = [1000.0, 1001.0]
    for species in ['ch4', 'o3', 'n2o', 'o2', 'co2', 'h2o']:
        tapas[f'trans_{species}'] = [1.0, 1.0]
    monkeypatch.setattr(gen_tellu.drs_file, 'get_file_definition',
                        MagicMock(return_value=tapas_file))
    monkeypatch.setattr(gen_tellu, 'load_tellu_file',
                        MagicMock(return_value=None))
    monkeypatch.setattr(gen_tellu.drs_data, 'load_tapas',
                        MagicMock(return_value=(tapas, 'tapas.fits')))
    monkeypatch.setattr(gen_tellu, 'WLOG', MagicMock())
    params = {'PATH.TELLU': str(tmp_path)}
    recipe = SimpleNamespace(shortname='TEST', out_block_str='red',
                             runstring='test')

    gen_tellu.load_tapas_spl(params, recipe, header=dict(),
                             database=MagicMock())

    database = TelluricDatabase.__new__(TelluricDatabase)
    database.instrument = 'NIRPS_HE'
    database.database = MagicMock()
    database.filedir = tmp_path
    database.classname = 'TelluricDatabase'
    database.get_tellu_entry = MagicMock(
        return_value=('tapas_spl.npy', 'None'))
    found = database.get_tellu_file('TELLU_TAPAS', no_times=True,
                                    timemode='closest')
    assert Path(tapas_file.filename) == tmp_path / 'OTHER' / 'tapas_spl.npy'
    assert found == Path(tapas_file.filename).absolute()
