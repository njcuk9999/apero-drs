#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for single telluric database result paths."""

from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd
import pytest

from apero.core import drs_database


@pytest.mark.parametrize('object_name', [None, 'None', 'Null', '', 'HR7590'])
@pytest.mark.parametrize('absolute', [False, True])
@pytest.mark.parametrize('row_type', [list, tuple])
@pytest.mark.parametrize('nentries', [1, '*'])
def test_single_telluric_path(
    tmp_path: Path, spirou_params: drs_database.ParamDict,
    object_name: str | None, absolute: bool, row_type: type,
    nentries: int | str
) -> None:
    """Resolve telluric rows using the same directories as the writer.

    :param tmp_path: Temporary telluric root.
    :param spirou_params: Profile-free parameters supplied through apero.dev.
    :param object_name: Database OBJECT value.
    :param absolute: Whether the stored filename is an absolute asset path.
    :param row_type: Container used for a single database result.
    :param nentries: Whether to request a scalar or multiple results.
    :return: None.
    """
    directory = object_name or 'OTHER'
    if directory in ['None', 'Null']:
        directory = 'OTHER'
    if directory == 'OTHER':
        model_path = tmp_path / directory / 'sky_model.fits'
    else:
        model_path = tmp_path / 'SKY_MODEL' / directory / 'sky_model.fits'
    model_path.parent.mkdir(parents=True)
    model_path.touch()
    filename = str(model_path) if absolute else model_path.name
    manager = object.__new__(drs_database.TelluricDatabase)
    manager.params = spirou_params
    manager.instrument = 'SPIROU'
    manager.database = MagicMock()
    manager.filedir = tmp_path
    manager.classname = 'TelluricDatabase'
    if nentries == 1:
        entries = row_type([filename, object_name])
    else:
        entries = pd.DataFrame(dict(FILENAME=[filename], OBJECT=[object_name]))
    manager.get_tellu_entry = MagicMock(return_value=entries)

    result = manager.get_tellu_file('SKY_MODEL', timemode='closest',
                                    nentries=nentries)

    assert result == (model_path if nentries == 1 else [model_path])