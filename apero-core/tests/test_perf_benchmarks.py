#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Performance benchmarks for hot APERO functions.

These are timing tests, not correctness tests. They print per-call timings
for representative array sizes and are marked ``perf`` so a normal test run
can skip them with ``-m "not perf"``. Run with::

    PYTHONPATH="apero-core" python -m pytest -q -s \
        apero-core/tests/test_perf_benchmarks.py -m perf

Each benchmark aims to make it easy to reproduce the numbers cited in the
markdown files in ``documentation/agent/performance/``.

Array sizes are picked to match the largest arrays that appear inside
APERO extraction/calibration:

    - 4096 x 4096 detector-style arrays
    - 71 x 8176 order-ribbon-style arrays (one order after straightening)

Created on 2026-09-24
"""
import time
import warnings

import numpy as np

try:
    import pytest
except ImportError:  # pragma: no cover - lets the file be imported bare
    class _PytestShim:
        class mark:  # noqa: N801 - mimic pytest attribute layout
            @staticmethod
            def perf(func):
                return func
    pytest = _PytestShim()

from aperocore.math import gen_math, interpolate
from aperocore.science.calib import background_core
from aperocore.science.extract import extract_core
from aperocore.science.extract import extract_model_core as emc


# =============================================================================
# Helpers
# =============================================================================
def _time(func, *args, repeats: int = 3, **kwargs):
    """Return (best_seconds, result) for a small number of repeats."""
    best = np.inf
    result = None
    for _ in range(repeats):
        t0 = time.perf_counter()
        result = func(*args, **kwargs)
        dt = time.perf_counter() - t0
        best = min(best, dt)
    return best, result


# =============================================================================
# Benchmarks
# =============================================================================
@pytest.mark.perf
def test_perf_extraction_ribbon():
    """Time the per-order extract_core.extraction() on a 71 x 8176 ribbon."""
    rng = np.random.default_rng(0)
    ny, nx = 71, 8176
    simage = rng.normal(1000.0, 30.0, (ny, nx)).astype(float)
    profile = np.exp(-0.5 * ((np.arange(ny)[:, None] - ny / 2) / 8.0) ** 2)
    orderp = profile * np.ones((ny, nx))
    pos = np.array([ny / 2, 0.0, 0.0])
    dt, _ = _time(extract_core.extraction, simage, orderp, pos,
                  15.0, 15.0, 5.0, repeats=3)
    print(f'\nextract_core.extraction 71x8176: {dt * 1000:.1f} ms')


@pytest.mark.perf
def test_perf_measure_box_min_max():
    """Time gen_math.measure_box_min_max on a 4096 vector."""
    rng = np.random.default_rng(0)
    y = rng.normal(size=4096)
    dt, _ = _time(gen_math.measure_box_min_max, y, 32, repeats=10)
    print(f'\nmeasure_box_min_max(4096, 32): {dt * 1000:.2f} ms')


@pytest.mark.perf
def test_perf_lowpassfilter():
    """Time gen_math.lowpassfilter on an 8176 vector with holes."""
    rng = np.random.default_rng(0)
    v = rng.normal(size=8176)
    v[::37] = np.nan
    dt, _ = _time(gen_math.lowpassfilter, v, 101, repeats=10)
    print(f'\nlowpassfilter(8176, 101): {dt * 1000:.2f} ms')


@pytest.mark.perf
def test_perf_create_background_map():
    """Time background_core.create_background_map on 4088x4088 frame."""
    rng = np.random.default_rng(0)
    image = rng.normal(0.0, 50.0, (4088, 4088)).astype(float)
    image[100:105, :] += 500.0
    bp = np.zeros((4088, 4088), dtype=bool)
    dt, _ = _time(background_core.create_background_map,
                  image, bp, 100, 5, 7, 3, repeats=1)
    print(f'\ncreate_background_map(4088x4088): {dt:.2f} s')


@pytest.mark.perf
def test_perf_iterative_box_background():
    """Time background_core.iterative_box_background on 4088x4088 frame."""
    rng = np.random.default_rng(0)
    image = rng.normal(0.0, 30.0, (4088, 4088)).astype(float)
    dt, _ = _time(background_core.iterative_box_background,
                  image, 100, repeats=1, niter=3)
    print(f'\niterative_box_background(4088x4088): {dt:.2f} s')


@pytest.mark.perf
def test_perf_correct_local_background():
    """Time background_core.correct_local_background."""
    rng = np.random.default_rng(0)
    image = rng.normal(0.0, 30.0, (4088, 4088)).astype(float)
    dt, _ = _time(background_core.correct_local_background,
                  image, 1, 9, 4, repeats=2)
    print(f'\ncorrect_local_background(4088x4088): {dt * 1000:.1f} ms')


@pytest.mark.perf
def test_perf_fit_lower_envelope_2d():
    """Time background_core.fit_lower_envelope_2d on a synthetic frame."""
    rng = np.random.default_rng(0)
    image = np.abs(rng.normal(100.0, 20.0, (4088, 4088))).astype(float)
    err = np.abs(rng.normal(0.0, 5.0, (4088, 4088))) + 1.0
    dt, _ = _time(background_core.fit_lower_envelope_2d,
                  image, err, repeats=1, xorder=3, yorder=3, niter=10)
    print(f'\nfit_lower_envelope_2d(4088x4088, bin=4): {dt:.2f} s')


@pytest.mark.perf
def test_perf_background_model():
    """Time extract_model_core.background_model on 4088x4088 frame."""
    rng = np.random.default_rng(0)
    image = rng.normal(0.0, 30.0, (4088, 4088)).astype(float)
    image[::13, ::17] = np.nan
    dt, _ = _time(emc.background_model, image, repeats=1, size=(31, 7))
    print(f'\nextract_model_core.background_model(4088x4088): {dt:.2f} s')


@pytest.mark.perf
def test_perf_ron_between_orders():
    """Time extract_model_core.ron_between_orders on a 4088x4088 frame."""
    rng = np.random.default_rng(0)
    image = rng.normal(0.0, 30.0, (4088, 4088)).astype(float)
    bg = np.abs(rng.normal(0.0, 5.0, (4088, 4088)))
    om = np.zeros((4088, 4088), dtype=np.int32)
    om[100:200, :] = 1
    dt, _ = _time(emc.ron_between_orders, image, bg, om, repeats=2)
    print(f'\nron_between_orders(4088x4088): {dt * 1000:.1f} ms')


@pytest.mark.perf
def test_perf_fill_nans_nearest():
    """Time interpolate.fill_nans_nearest on 4088x4088 and a 4-image list."""
    rng = np.random.default_rng(0)
    img = rng.normal(size=(4088, 4088))
    img[::5, ::7] = np.nan
    dt, _ = _time(interpolate.fill_nans_nearest, img, repeats=1)
    print(f'\nfill_nans_nearest single(4088x4088): {dt * 1000:.1f} ms')
    imgs = [img.copy() for _ in range(4)]
    dt, _ = _time(interpolate.fill_nans_nearest, imgs, repeats=1)
    print(f'fill_nans_nearest x4 same mask: {dt * 1000:.1f} ms')


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Run with: PYTHONPATH="apero-core" python -m pytest -q -s '
          '-m perf apero-core/tests/test_perf_benchmarks.py')

# =============================================================================
# End of code
# =============================================================================
