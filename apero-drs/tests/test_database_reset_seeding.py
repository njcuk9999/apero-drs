#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Regression tests for asset CSV seeding during database reset."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pandas as pd
import pytest

from apero.tools.module.database import manage_databases


@pytest.mark.parametrize('kind', ['tellu', 'calib'])
@pytest.mark.parametrize('has_seed', [True, False])
def test_reset_seeds_only_tellurics(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    kind: str, has_seed: bool
) -> None:
    """Import optional telluric seeds without importing calibration seeds.

    :param tmp_path: Temporary asset root supplied by pytest.
    :param monkeypatch: Fixture replacing the database connection.
    :param kind: Database kind being reset.
    :param has_seed: Whether the asset CSV is present.
    :return: None.
    """
    params = dict()
    params['PATH.ASSETS'] = str(tmp_path)
    params['DB.DIR'] = 'database'
    seed_path = tmp_path / 'database' / f'reset.{kind}.csv'
    if has_seed:
        seed_path.parent.mkdir()
        seed_path.write_text('FILENAME, KW_OUTPUT\nsky.fits, SKY_MODEL\n',
                             encoding='utf-8')

    manager = SimpleNamespace(dburl='unused', dbtable=f'{kind}_table',
                              connect_args=dict())
    database = MagicMock()
    database.tablename = manager.dbtable
    database.get_tables.return_value = []
    monkeypatch.setattr(manage_databases.drs_db, 'AperoDatabase',
                        MagicMock(return_value=database))
    columns = SimpleNamespace(columns=[], indexes=[], uniques=[])
    pconst = MagicMock()
    pconst.TELLURIC_DB_COLUMNS.return_value = columns
    pconst.CALIBRATION_DB_COLUMNS.return_value = columns
    if kind == 'tellu':
        create_database = manage_databases.create_telluric_database
    else:
        create_database = manage_databases.create_calibration_database

    result = create_database(params, pconst, {kind: manager})

    assert result is database
    database.add_table.assert_called_once()
    if kind == 'tellu' and has_seed:
        database.add_from_pandas.assert_called_once()
        imported = database.add_from_pandas.call_args.args[0]
        expected = pd.DataFrame(dict(FILENAME=['sky.fits'],
                                     KW_OUTPUT=['SKY_MODEL']))
        pd.testing.assert_frame_equal(imported, expected)
        assert database.add_from_pandas.call_args.kwargs == dict(
            if_exists='append')
    else:
        database.add_from_pandas.assert_not_called()