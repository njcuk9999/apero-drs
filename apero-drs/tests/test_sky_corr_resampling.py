#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Regression coverage for sky correction using the core resampler."""

from unittest.mock import MagicMock

import numpy as np
import pytest

from apero.science.telluric import sky_corr


def test_no_ref_resampling(
    monkeypatch: pytest.MonkeyPatch, spirou_params: sky_corr.ParamDict
) -> None:
    """Run both resampling steps without the obsolete params argument.

    :param monkeypatch: Fixture replacing model loading and output writes.
    :param spirou_params: Profile-free parameters loaded through apero.dev.
    :return: None.
    """
    wavemap = np.tile(np.linspace(1000, 1001, 16), (2, 1))
    model = np.zeros_like(wavemap)
    model[:, 6:10] = [1, 2, 2, 1]
    image = 100 + 3 * model
    props = sky_corr.ParamDict()
    props['SKY_WAVEMAP'] = wavemap
    props['SKY_MODEL_SCI'] = model
    props['SKY_MODEL_REF'] = model
    props['SKY_REG_ID'] = (model > 0).astype(int)
    props['SKY_WEIGHTS'] = np.ones_like(model)
    props['SKY_GRADIENT'] = np.gradient(model, axis=1)
    monkeypatch.setattr(sky_corr, 'get_sky_model',
                        MagicMock(return_value=props))
    monkeypatch.setattr(sky_corr, 'skyclean_write', MagicMock())
    pconst = MagicMock()
    pconst.FIBER_KINDS.return_value = (['A'], 'B')
    monkeypatch.setattr(sky_corr.load_functions, 'load_pconfig',
                        MagicMock(return_value=pconst))
    resampler = MagicMock(wraps=sky_corr.wave_to_wave)
    monkeypatch.setattr(sky_corr, 'wave_to_wave', resampler)
    infile = MagicMock()
    infile.data = image
    infile.fiber = 'A'
    wprops = sky_corr.ParamDict()
    wprops['WAVEMAP'] = wavemap

    result = sky_corr.correct_sky_no_ref(
        spirou_params, MagicMock(), infile, wprops, [], False,
        calibdbm=MagicMock(), telludbm=MagicMock())

    assert resampler.call_count == 2
    np.testing.assert_allclose(result['SKY_CORR_SCI'], 3 * model)
    np.testing.assert_allclose(result['CORR_EXT_A'], 100)
    np.testing.assert_array_equal(infile.data, image)