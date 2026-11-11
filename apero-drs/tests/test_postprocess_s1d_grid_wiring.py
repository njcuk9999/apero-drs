#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Check reconstructed S1D columns use their matching wavelength grid."""

import ast
from pathlib import Path

import pytest


@pytest.mark.parametrize('instrument', ['spirou', 'nirps_ha', 'nirps_he'])
def test_reconstructed_columns_use_matching_grid(instrument: str) -> None:
    """Keep wavelength and velocity reconstruction columns on their grids.

    :param instrument: Instrument file definitions to inspect.
    :return: None.
    """
    definitions = Path(__file__).parents[1] / 'apero' / 'instruments'
    path = definitions / instrument / 'file_definitions.py'
    tree = ast.parse(path.read_text())
    found = dict()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr != 'add_column' or len(node.args) < 2:
            continue
        if not isinstance(node.args[0], ast.Constant):
            continue
        grid = node.args[0].value
        output = node.args[1]
        if not isinstance(output, ast.Name):
            continue
        column = next((kw.value.value for kw in node.keywords
                       if kw.arg == 'incol'
                       and isinstance(kw.value, ast.Constant)), None)
        if column in ['RECON_flux', 'RECON_eflux', 'SKYC_flux',
                      'SKYC_eflux', 'FRES_flux', 'FRES_eflux']:
                found[(grid, column)] = output.id

    for column in ['RECON_flux', 'RECON_eflux']:
        assert found[('S1D_W', column)] == 'out_tellu_rc1d_w'
        assert found[('S1D_V', column)] == 'out_tellu_rc1d_v'
    for column in ['SKYC_flux', 'SKYC_eflux', 'FRES_flux', 'FRES_eflux']:
        assert found[('S1D_W', column)] == 'out_tellu_rc1d_w'
        assert found[('S1D_V', column)] == 'out_tellu_rc1d_v'