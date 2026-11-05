#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Validate instrument static wavelength asset registration."""

from pathlib import Path

import pytest

from aperocore.base import base
from apero.base import base as apero_base
from apero.core import drs_file
from apero.dev import get_base_params
from apero.science.calib import wave

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tests.test_static_wave_definitions'
__version__ = apero_base.__version__
__date__ = apero_base.__date__
__authors__ = apero_base.__authors__

# =============================================================================
# Define functions
# =============================================================================
@pytest.mark.parametrize('instrument', ['NIRPS_HE', 'NIRPS_HA', 'SPIROU'])
@pytest.mark.parametrize('fiber', ['A', 'B'])
def test_static_wave_lookup(instrument: str, fiber: str,
                          monkeypatch: pytest.MonkeyPatch) -> None:
    """Resolve static wavelength definitions and instrument filenames.

    :param instrument: Instrument supplying the static file definition.
    :param fiber: Fiber suffix for the static wavelength file.
    :param monkeypatch: Fixture isolating process instrument selection.
    :return: None.
    """
    params = get_base_params(instrument)
    monkeypatch.setattr(base, 'IPARAMS', params)
    lookup_kwargs = dict(block_kind='asset', required=False)
    definition = drs_file.get_file_definition(params, 'STATIC_WAVE_REF',
                                              **lookup_kwargs)
    assert definition.name == 'STATIC_WAVE_REF'
    assert definition.get_hdulist_names() == ['WAVE']
    filename = Path(wave.get_static_wavesol(params, fiber))
    expected = f'static_{instrument.lower()}_wave_ref_{fiber}.fits'
    assert filename.name == expected
    expected_dir = Path(params['PATH.ASSETS'])
    expected_dir /= params['TOOLS.STATIC.CAL_PATH']
    assert filename.parent == expected_dir


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================