#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Validate magnitude provenance keyword mappings and FITS serialization."""

import io

from astropy.io import fits
import pytest

from apero.dev import get_base_params
from apero.core import drs_astrometrics
from apero.io import drs_fits


@pytest.mark.parametrize('instrument', ['SPIROU', 'NIRPS_HA', 'NIRPS_HE'])
def test_magnitude_source_header_round_trip(instrument: str) -> None:
    """Write all magnitude/source pairs using instrument keyword mappings.

    :param instrument: Instrument supplying the FITS card definitions.
    :return: None.
    """
    params = get_base_params(instrument)
    header = drs_fits.Header()
    card_names = []
    for magnitude, alias in zip(drs_astrometrics.MAGS,
                                drs_astrometrics.MAGS_HDR):
        source_alias = f'{alias}_SOURCE'
        value_card = params[alias][0]
        source_card = params[source_alias][0]
        suffix = alias.removeprefix('KW_DRS_MAG_')
        assert value_card == f'PPM_{suffix}'
        assert source_card == f'PPS_{suffix}'
        header.set_key(params, alias, value=12.5)
        header.set_key(params, source_alias, value=f'catalog:{magnitude}')
        assert header[value_card] == 12.5
        assert header[source_card] == f'catalog:{magnitude}'
        card_names.extend([value_card, source_card])
    assert len(set(card_names)) == 2 * len(drs_astrometrics.MAGS)
    with io.BytesIO() as buffer:
        fits.PrimaryHDU(header=header).writeto(buffer)
        buffer.seek(0)
        with fits.open(buffer) as hdus:
            for card_name in card_names:
                assert hdus[0].header[card_name] == header[card_name]