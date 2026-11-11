#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Check fit_tellu recipes pass every argument the recon writer needs."""

import ast
import inspect
from pathlib import Path

import pytest

from apero.science.telluric import fit_tellu


@pytest.mark.parametrize('instrument', ['spirou', 'nirps_ha', 'nirps_he'])
def test_recon_writer_arguments(instrument: str) -> None:
    """Match the recipe's splatted recon arguments to the writer signature.

    :param instrument: Instrument whose fit_tellu recipe is checked.
    :return: None.
    """
    recipe_root = Path(__file__).parents[1] / 'apero' / 'recipes'
    recipe_path = recipe_root / instrument / f'apero_fit_tellu_{instrument}.py'
    tree = ast.parse(recipe_path.read_text())
    frargs = [node.value for node in ast.walk(tree)
              if isinstance(node, ast.Assign)
              and any(isinstance(target, ast.Name) and target.id == 'frargs'
                      for target in node.targets)]
    assert len(frargs) == 1
    passed = [element.id for element in frargs[0].elts]
    signature = inspect.signature(fit_tellu.fit_tellu_write_recon)
    expected = list(signature.parameters)[2:]
    assert passed == expected
