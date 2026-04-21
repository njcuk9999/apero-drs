#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI - Finder chart generation for the data portal.

Queries Gaia DR3 and 2MASS catalogues to build simulated sky
images around a target, rendered with matplotlib and returned
as base64-encoded PNGs.

Based on apero-drs ``apero.tools.module.ari.ari_find``.

Created on 2026-04-20

@author: cook
"""
from __future__ import annotations

import base64
import io
import time as _time
import warnings
from typing import Any, Callable, Dict, List, Optional, Tuple

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from astropy import units as uu
from astropy.coordinates import Distance, SkyCoord
from astropy.time import Time
from astropy.wcs import WCS
from astroquery.utils.tap.core import TapPlus
from matplotlib.patches import FancyArrowPatch, Rectangle

from apero_ri.base import base

# ============================================================
# Define variables
# ============================================================
__NAME__ = 'apero_ri.core.object_finder'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__

# Gaia DR3 TAP endpoint
GAIA_URL = 'https://gea.esac.esa.int/tap-server/tap'
# noinspection SqlNoDataSourceInspection,SqlDialectInspection
GAIA_QUERY = """
SELECT
    source_id as source_id,ra,dec,parallax,pmra,pmdec,
    phot_g_mean_mag,phot_rp_mean_mag,phot_bp_mean_mag,
    phot_g_mean_flux,phot_rp_mean_flux,phot_bp_mean_flux
FROM gaiadr3.gaia_source
WHERE
    1=CONTAINS(POINT('ICRS', ra, dec),
               CIRCLE('ICRS', {ra}, {dec}, {radius}))
"""
# Gaia DR3 reference epoch (decimal year)
GAIA_EPOCH = 2016.0

# 2MASS TAP endpoint
TMASS_URL = 'https://irsa.ipac.caltech.edu/TAP'
# noinspection SqlNoDataSourceInspection,SqlDialectInspection
TMASS_QUERY = """
SELECT
    {TMASS_COLS}
FROM fp_2mass.fp_psc
WHERE
    1=CONTAINS(POINT('ICRS', ra, dec),
               CIRCLE('ICRS', {ra}, {dec}, {radius}))
"""
TMASS_COLS = 'ra,dec,j_m,h_m,k_m,jdate'
TMASS_RADIUS = 2 * uu.arcsec
TMASS_EPOCH = 2000.0

# Map of known catalogue sources to their reference epoch
# (decimal year).  Used when the object table does not carry
# an explicit EPOCH column.
_SOURCE_EPOCH_MAP = {
    'gaia edr3': 2016.0,
    'gaia dr3': 2016.0,
    'gaia dr2': 2015.5,
    'gaia dr1': 2015.0,
    '2mass': 2000.0,
    'hipparcos': 1991.25,
}
# Fallback when no source is recognised
_DEFAULT_EPOCH_DECYR = 2016.0


# ============================================================
# Public API
# ============================================================
def generate_finder_charts(
    obj_props: Dict[str, Any],
    preset: Dict[str, Any],
    log_func: Optional[Callable[[str], None]] = None,
) -> Dict[str, Any]:
    """Generate finder chart images for all configured bands.

    Parameters
    ----------
    obj_props : dict
        Object table row with RA/Dec, proper motion, etc.
    preset : dict
        Full instrument profile dict (from YAML).
    log_func : callable, optional
        If given, called with progress strings for live
        streaming output.

    Returns
    -------
    dict
        ``{'success': bool, 'images': [...],
           'bands': [...], 'title': str, 'error': str}``
        Each entry in *images* is a base64-encoded PNG string.
    """
    # helper: emit a log line if callback provided
    def _log(msg: str) -> None:
        if log_func is not None:
            log_func(msg)

    t0 = _time.monotonic()
    finder_cfg = preset.get('finder')
    if not finder_cfg:
        return dict(
            success=False, images=[], bands=[],
            title='', titles=[],
            error='No finder config in instrument profile.',
        )
    # resolve bands to plot
    bands = finder_cfg.get('BANDS')
    if not bands:
        bands = list(
            finder_cfg.get('FIELD_OF_VIEW', {}).keys()
        )
    if not bands:
        return dict(
            success=False, images=[], bands=[],
            title='', titles=[],
            error='No bands configured for finder charts.',
        )
    # build the object dictionary from obj_props
    objdict = _build_objdict(obj_props)
    if objdict is None:
        return dict(
            success=False, images=[], bands=[],
            title='', titles=[],
            error='Missing RA/Dec for this object.',
        )
    _log(
        f'[finder] Object: {objdict["OBJNAME"]}  '
        f'RA={objdict["RA_DEG"]:.6f}  '
        f'Dec={objdict["DEC_DEG"]:.6f}\n'
    )
    _log(f'[finder] Bands: {", ".join(bands)}\n')
    # pre-compute shared finder parameters
    fcfg = _prepare_finder_config(finder_cfg, bands)
    # propagate coordinates to now
    date = Time.now()
    obs_coords, obs_time = _propagate_coords(objdict, date)
    _log(
        f'[finder] Propagated coords to '
        f'{obs_time.iso}\n'
    )
    # ---------------------------------------------------------
    # fetch catalogue data
    # ---------------------------------------------------------
    _log('[finder] Querying Gaia DR3 catalogue ...\n')
    t1 = _time.monotonic()
    try:
        gaia_sources = _get_gaia_sources(
            obs_coords, obs_time,
            fcfg['radius']['G'], fcfg['max_pm'],
        )
    except Exception as exc:
        _log(f'[finder] ERROR: Gaia query failed: {exc}\n')
        return dict(
            success=False, images=[], bands=[],
            title='', titles=[],
            error=f'Gaia query failed: {exc}',
        )
    n_gaia = len(gaia_sources.get('ra', []))
    dt1 = _time.monotonic() - t1
    _log(
        f'[finder] Gaia query returned {n_gaia} '
        f'sources ({dt1:.1f}s)\n'
    )
    # get 2MASS photometry for infrared bands
    ir_bands = {'J', 'H', 'K'}
    if ir_bands.intersection(bands):
        _log('[finder] Querying 2MASS catalogue ...\n')
        t2 = _time.monotonic()
        try:
            _fill_2mass(
                gaia_sources, obs_coords, obs_time,
                fcfg['radius'].get(
                    'J', fcfg['radius']['G']
                ),
                fcfg['max_pm'],
                fcfg['sigma_limit'],
                fcfg['mag_limit'],
            )
            dt2 = _time.monotonic() - t2
            n_matched = int(np.sum(
                ~np.isnan(gaia_sources['J'])
            ))
            _log(
                f'[finder] 2MASS cross-match complete: '
                f'{n_matched}/{n_gaia} matched '
                f'({dt2:.1f}s)\n'
            )
        except Exception as exc:
            dt2 = _time.monotonic() - t2
            _log(
                f'[finder] 2MASS query failed '
                f'({dt2:.1f}s): {exc}\n'
            )
    # ---------------------------------------------------------
    # generate one image per band
    # ---------------------------------------------------------
    images: List[str] = []
    titles: List[str] = []
    band_labels = {
        'G': 'Gaia G',
        'J': '2MASS J',
        'H': '2MASS H',
        'K': '2MASS K',
    }
    objname = objdict['OBJNAME']
    # find the Gaia source closest to our target
    closest = int(np.argmin(gaia_sources['separation']))
    # build the super-title used on each panel
    suptitle = (
        f'Object: {objname}\n'
        f'Date: {obs_time.iso}\n'
        f'RA: {obs_coords.ra.to_string(uu.hourangle, sep=":")}'
        f'   Dec: '
        f'{obs_coords.dec.to_string(uu.deg, sep=":")}\n'
        f'Gmag: {gaia_sources["G"][closest]:.2f}   '
        f'Jmag: {gaia_sources["J"][closest]:.2f}'
    )
    for band in bands:
        tb = _time.monotonic()
        label = band_labels.get(band, band)
        _log(f'[finder] Rendering {label} ...\n')
        ps = fcfg['pixel_scale'][band]
        fov = fcfg['fov'][band]
        sf = fcfg['scale_factor'][band]
        fwhm = fcfg['fwhm'][band]
        sl = fcfg['sigma_limit'].get(band, 18)
        rot = fcfg['transform_rotate'][band]
        fx = fcfg['flip_x'][band]
        fy = fcfg['flip_y'][band]
        # seed image with gaussian PSFs
        image, wcs = _seed_image(
            gaia_sources, ps, obs_coords, fwhm,
            fov, sl, band, rot, fx, fy, sf,
        )
        # render image to base64 PNG
        png_b64 = _render_map(
            fcfg, image, wcs, obs_coords,
            label, fov, ps, sf, suptitle,
        )
        images.append(png_b64)
        titles.append(label)
        dtb = _time.monotonic() - tb
        _log(
            f'[finder] {label} done ({dtb:.1f}s)\n'
        )

    total = _time.monotonic() - t0
    _log(
        f'[finder] All bands complete '
        f'({total:.1f}s total)\n'
    )
    return dict(
        success=True,
        images=images,
        bands=bands,
        titles=titles,
        title=suptitle,
        error='',
    )


# ============================================================
# Internal helpers
# ============================================================
def _build_objdict(
    obj_props: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Extract needed fields from the object table row.

    The epoch is read from the 'EPOCH [JD]' column added by
    the apero_object_table task (astrom.EPOCH).  If that column
    is absent we fall back to inferring from the RA/Dec source
    catalogue name.
    """
    ra = _float_or(obj_props, ['RA [Deg]', 'RA_DEG'])
    dec = _float_or(obj_props, ['Dec [Deg]', 'DEC_DEG'])
    if ra is None or dec is None:
        return None
    # determine epoch in JD (from the astrom table)
    epoch_jd = _float_or(
        obj_props, ['EPOCH [JD]', 'EPOCH']
    )
    if epoch_jd is None or epoch_jd <= 0:
        # fallback: infer from RA/Dec source catalogue
        epoch_jd = _resolve_epoch_jd(obj_props)
    return dict(
        OBJNAME=obj_props.get('OBJNAME', 'Unknown'),
        RA_DEG=ra,
        DEC_DEG=dec,
        EPOCH=epoch_jd,
        PLX=_float_or(
            obj_props, ['Plx [mas]', 'PLX']
        ) or 0.0,
        PMRA=_float_or(
            obj_props, ['PMRA [mas/yr]', 'PMRA']
        ) or 0.0,
        PMDE=_float_or(
            obj_props,
            ['PMDE [mas/yr]', 'PMDE',
             'PMDEC [mas/yr]', 'PMDEC'],
        ) or 0.0,
    )


def _resolve_epoch_jd(
    obj_props: Dict[str, Any],
) -> float:
    """Return the coordinate epoch in Julian Date.

    Priority order:
    1. Explicit 'EPOCH' key (assumed JD).
    2. Infer from 'RA source' / 'Dec source' catalogue name.
    3. Fall back to GAIA_EPOCH (J2016.0) since the apero
       astrometric database is Gaia-based.
    """
    # 1) explicit EPOCH (in JD)
    epoch_val = _float_or(obj_props, ['EPOCH'])
    if epoch_val is not None and epoch_val > 0:
        return epoch_val
    # 2) infer from source catalogue string
    for src_key in ('RA source', 'Dec source'):
        src = obj_props.get(src_key, '')
        if not isinstance(src, str):
            continue
        src_lower = src.strip().lower()
        for pattern, decyr in _SOURCE_EPOCH_MAP.items():
            if pattern in src_lower:
                return Time(
                    decyr, format='decimalyear'
                ).jd
    # 3) fallback: Gaia epoch
    return Time(
        _DEFAULT_EPOCH_DECYR, format='decimalyear'
    ).jd


def _float_or(
    d: Dict[str, Any], keys: List[str],
) -> Optional[float]:
    """Return the first valid float among *keys*, or None."""
    for k in keys:
        v = d.get(k)
        if v is not None:
            try:
                return float(v)
            except (ValueError, TypeError):
                continue
    return None


def _prepare_finder_config(
    cfg: Dict[str, Any], bands: List[str],
) -> Dict[str, Any]:
    """Parse raw YAML finder dict into typed quantities."""
    # field of view per band
    fov: Dict[str, Any] = {}
    for band in cfg.get('FIELD_OF_VIEW', {}):
        raw = cfg['FIELD_OF_VIEW'][band]
        fov[band] = np.array(raw) * uu.arcsec
    # scale factors
    scale_factor: Dict[str, Any] = {}
    sf_cfg = cfg.get('SCALE_FACTOR', {})
    sf_bandname = list(sf_cfg.keys())[0] if sf_cfg else bands[0]
    sf_bandvalue = sf_cfg.get(sf_bandname, 1.5)
    fov_bandvalue = fov.get(
        sf_bandname, np.array([77.6, 77.6]) * uu.arcsec
    )
    for band in fov:
        if band == sf_bandname:
            scale_factor[band] = sf_bandvalue
        else:
            scale_factor[band] = (
                sf_bandvalue * (fov_bandvalue / fov[band])
            )
    # radius
    radius: Dict[str, Any] = {}
    for band in fov:
        sf = scale_factor[band]
        radius[band] = np.max(
            sf * fov[band] / np.sqrt(2)
        )
    # pixel scale
    pixel_scale: Dict[str, float] = {}
    for band, val in cfg.get('PIXEL_SCALE', {}).items():
        pixel_scale[band] = val * uu.arcsec / uu.pixel
    # rotation
    transform_rotate: Dict[str, Any] = {}
    for band, val in cfg.get('TRANSFORM_ROTATE', {}).items():
        transform_rotate[band] = val * uu.deg
    # FWHM
    fwhm: Dict[str, Any] = {}
    for band, val in cfg.get('FWHM', {}).items():
        fwhm[band] = val * uu.arcsec
    # scalar config
    max_pm = cfg.get('MAX_PM', 11) * uu.arcsec / uu.yr
    scale_size = cfg.get('SCALE_SIZE', 10) * uu.arcsec
    compass_frac = cfg.get('COMPASS_FRAC', 0.075)
    flip_x = cfg.get('FLIP_X', {})
    flip_y = cfg.get('FLIP_Y', {})

    return dict(
        fov=fov,
        scale_factor=scale_factor,
        radius=radius,
        pixel_scale=pixel_scale,
        transform_rotate=transform_rotate,
        fwhm=fwhm,
        max_pm=max_pm,
        scale_size=scale_size,
        compass_frac=compass_frac,
        flip_x=flip_x,
        flip_y=flip_y,
        sigma_limit=cfg.get('SIGMA_LIMIT', {}),
        mag_limit=cfg.get('MAG_LIMIT', -1),
    )


# ---- coordinate propagation --------------------------------
def _propagate_coords(
    objdata: Dict[str, Any], obs_time: Time,
) -> Tuple[SkyCoord, Time]:
    """Propagate target coords from catalogue epoch to now."""
    # deal with distance (negative/zero parallax)
    if objdata['PLX'] <= 0:
        distance = None
    else:
        distance = Distance(
            parallax=objdata['PLX'] * uu.mas
        )
    # build SkyCoord at the catalogue epoch
    coords = SkyCoord(
        ra=objdata['RA_DEG'] * uu.deg,
        dec=objdata['DEC_DEG'] * uu.deg,
        distance=distance,
        pm_ra_cosdec=objdata['PMRA'] * uu.mas / uu.yr,
        pm_dec=objdata['PMDE'] * uu.mas / uu.yr,
        obstime=Time(objdata['EPOCH'], format='jd'),
    )
    # propagate to the requested observation time
    with warnings.catch_warnings(record=True) as _:
        jepoch = Time(objdata['EPOCH'], format='jd')
        delta_time = (obs_time.jd - jepoch.jd) * uu.day
    with warnings.catch_warnings(record=True) as _:
        curr_coords = coords.apply_space_motion(
            dt=delta_time
        )
    return curr_coords, obs_time


# ---- Gaia query --------------------------------------------
def _get_gaia_sources(
    coords: SkyCoord, obstime: Time,
    radius: Any, max_pm: Any,
) -> Dict[str, np.ndarray]:
    """Query Gaia DR3 and propagate sources to *obstime*."""
    gaia_time = Time(GAIA_EPOCH, format='decimalyear')
    with warnings.catch_warnings(record=True) as _:
        delta_time_now = (
            (obstime.jd - gaia_time.jd) * uu.day
        )
    # widen search radius for proper motion
    search = abs(delta_time_now * max_pm).to(uu.deg)
    radius = radius.to(uu.deg) + search
    # run TAP query
    gaia = TapPlus(url=GAIA_URL)
    gaia_query = GAIA_QUERY.format(
        ra=coords.ra.deg,
        dec=coords.dec.deg,
        radius=radius.to(uu.deg).value,
    )
    job = gaia.launch_job(gaia_query)
    table = job.get_results()
    del job
    # use async for very large result sets
    if len(table) == 2000:
        gaia2 = TapPlus(url=GAIA_URL)
        job2 = gaia2.launch_job_async(gaia_query)
        table = job2.get_results()
        del job2
    # normalise column case
    if 'SOURCE_ID' in table.colnames:
        table['source_id'] = table['SOURCE_ID']
    n = len(table)
    if n == 0:
        empty = np.array([])
        keys = [
            'gaia_id', 'ra', 'dec', 'G', 'Rp', 'Bp',
            'J', 'H', 'K', 'ra_gaia', 'dec_gaia',
            'pmra', 'pmdec', 'parallax', 'separation',
        ]
        return {k: empty for k in keys}
    # ---- extract arrays and handle masks ----
    ra_arr = np.array(table['ra'], dtype=float)
    dec_arr = np.array(table['dec'], dtype=float)
    # properly fill masked proper motions with 0 (no PM)
    pmra_arr = _filled_float(table['pmra'], fill=0.0)
    pmdec_arr = _filled_float(table['pmdec'], fill=0.0)
    plx_arr = _filled_float(table['parallax'], fill=np.nan)
    # build distances: use tiny parallax for invalid
    plx_for_dist = np.where(
        np.isnan(plx_arr) | (plx_arr <= 0),
        1e-6, plx_arr,
    )
    distances = Distance(parallax=plx_for_dist * uu.mas)
    # vectorized SkyCoord + proper motion propagation
    gaia_coords = SkyCoord(
        ra=ra_arr * uu.deg,
        dec=dec_arr * uu.deg,
        distance=distances,
        pm_ra_cosdec=pmra_arr * uu.mas / uu.yr,
        pm_dec=pmdec_arr * uu.mas / uu.yr,
        obstime=gaia_time,
        frame='icrs',
    )
    with warnings.catch_warnings(record=True) as _:
        curr = gaia_coords.apply_space_motion(
            dt=delta_time_now
        )
    sep = coords.separation(curr)
    # mark invalid parallaxes as NaN
    plx_out = np.where(
        np.isnan(plx_arr) | (plx_arr <= 0),
        np.nan, plx_arr,
    )
    return {
        'gaia_id': np.array(table['source_id']),
        'ra': curr.ra.deg,
        'dec': curr.dec.deg,
        'G': _filled_float(
            table['phot_g_mean_mag'], fill=np.nan
        ),
        'Rp': _filled_float(
            table['phot_rp_mean_mag'], fill=np.nan
        ),
        'Bp': _filled_float(
            table['phot_bp_mean_mag'], fill=np.nan
        ),
        'J': np.full(n, np.nan),
        'H': np.full(n, np.nan),
        'K': np.full(n, np.nan),
        'ra_gaia': ra_arr,
        'dec_gaia': dec_arr,
        'pmra': pmra_arr,
        'pmdec': pmdec_arr,
        'parallax': plx_out,
        'separation': sep.deg,
    }


def _filled_float(
    column: Any, fill: float = 0.0,
) -> np.ndarray:
    """Convert a (possibly masked) column to a float array.

    Masked / invalid entries are replaced with *fill*.
    """
    arr = np.array(column, dtype=float)
    if hasattr(column, 'mask'):
        mask = np.array(column.mask)
        arr[mask] = fill
    # also catch any NaN that leaked through
    if np.isnan(fill):
        return arr
    arr[np.isnan(arr)] = fill
    return arr


# ---- 2MASS fill --------------------------------------------
def _fill_2mass(
    gaia_sources: Dict[str, np.ndarray],
    obs_coords: SkyCoord,
    obs_time: Time,
    radius: Any,
    max_pm: Any,
    sigma_limit: Dict[str, float],
    mag_limit: float,
) -> None:
    """Cross-match Gaia sources with 2MASS photometry."""
    tmass = TapPlus(url=TMASS_URL)
    tmass_time = Time(TMASS_EPOCH, format='decimalyear')
    with warnings.catch_warnings(record=True) as _:
        dt_2mass = (
            (tmass_time.jd - obs_time.jd) * uu.day
        )
    # propagate target position to 2MASS epoch
    obs_copy = SkyCoord(obs_coords)
    with warnings.catch_warnings(record=True) as _:
        tmass_center = obs_copy.apply_space_motion(
            dt=dt_2mass
        )
    # widen search for proper motion
    search = abs(dt_2mass * max_pm).to(uu.deg)
    r = radius.to(uu.deg) + search
    # query 2MASS
    tmass_query = TMASS_QUERY.format(
        TMASS_COLS=TMASS_COLS,
        ra=tmass_center.ra.deg,
        dec=tmass_center.dec.deg,
        radius=r.value,
    )
    job0 = tmass.launch_job(tmass_query)
    table0 = job0.get_results()
    del job0
    if len(table0) == 2000:
        tmass2 = TapPlus(url=TMASS_URL)
        job2 = tmass2.launch_job_async(tmass_query)
        table0 = job2.get_results()
        del job2
    if len(table0) == 0:
        return
    # rename generic col_N columns when present
    # (some TAP services return positional names)
    col_list = TMASS_COLS.split(',')
    if f'col_{0}' in table0.colnames:
        for it, col in enumerate(col_list):
            table0[col] = table0[f'col_{it}']
            del table0[f'col_{it}']
    # get mean observation date for the 2MASS field
    mean_jdate = np.mean(table0['jdate'])
    jdate_time = Time(mean_jdate, format='jd')
    tmass_cat_coords = SkyCoord(
        ra=table0['ra'], dec=table0['dec'],
        distance=None,
        pm_ra_cosdec=None, pm_dec=None,
        obstime=jdate_time, frame='icrs',
    )
    # propagate Gaia sources to 2MASS epoch in bulk
    gaia_time = Time(GAIA_EPOCH, format='decimalyear')
    with warnings.catch_warnings(record=True) as _:
        dt_jdate = (
            (jdate_time.jd - gaia_time.jd) * uu.day
        )
    plx_arr = gaia_sources['parallax']
    plx_safe = np.where(
        np.isnan(plx_arr) | (plx_arr <= 0),
        1e-6, plx_arr,
    )
    distances = Distance(parallax=plx_safe * uu.mas)
    gaia_all = SkyCoord(
        ra=gaia_sources['ra_gaia'] * uu.deg,
        dec=gaia_sources['dec_gaia'] * uu.deg,
        distance=distances,
        pm_ra_cosdec=(
            gaia_sources['pmra'] * uu.mas / uu.yr
        ),
        pm_dec=(
            gaia_sources['pmdec'] * uu.mas / uu.yr
        ),
        obstime=gaia_time, frame='icrs',
    )
    with warnings.catch_warnings(record=True) as _:
        jdate_all = gaia_all.apply_space_motion(
            dt=dt_jdate
        )
    # vectorized cross-match
    idx, sep2d, _ = jdate_all.match_to_catalog_sky(
        tmass_cat_coords
    )
    # defaults when no match
    jmag_def = sigma_limit.get('J', 15) + mag_limit
    hmag_def = sigma_limit.get('H', 15) + mag_limit
    kmag_def = sigma_limit.get('K', 15) + mag_limit
    matched = sep2d <= TMASS_RADIUS
    # use _filled_float to handle masked magnitude cols
    j_arr = _filled_float(table0['j_m'], fill=np.nan)
    h_arr = _filled_float(table0['h_m'], fill=np.nan)
    k_arr = _filled_float(table0['k_m'], fill=np.nan)
    gaia_sources['J'] = np.where(
        matched, j_arr[idx], jmag_def
    )
    gaia_sources['H'] = np.where(
        matched, h_arr[idx], hmag_def
    )
    gaia_sources['K'] = np.where(
        matched, k_arr[idx], kmag_def
    )


# ---- WCS setup ---------------------------------------------
def _setup_wcs(
    image_shape: Tuple[int, int],
    cent_coords: SkyCoord,
    pixel_scale: Any,
    rotation: Any,
    flip_x: bool,
    flip_y: bool,
) -> WCS:
    """Build a TAN WCS for the finder chart image."""
    naxis2, naxis1 = image_shape
    pix_scale = pixel_scale.to(uu.deg / uu.pixel).value
    wcs = WCS(naxis=2)
    wcs.wcs.crpix = [naxis1 / 2, naxis2 / 2]
    # apply axis flips via cdelt sign
    if flip_y and flip_x:
        wcs.wcs.cdelt = np.array(
            [pix_scale, -pix_scale]
        )
    elif flip_x:
        wcs.wcs.cdelt = np.array(
            [pix_scale, pix_scale]
        )
    elif flip_y:
        wcs.wcs.cdelt = np.array(
            [pix_scale, -pix_scale]
        )
    else:
        wcs.wcs.cdelt = np.array(
            [-pix_scale, pix_scale]
        )
    wcs.wcs.crval = [
        cent_coords.ra.deg, cent_coords.dec.deg
    ]
    wcs.wcs.ctype = ['RA---TAN', 'DEC--TAN']
    # rotation matrix
    cos_r = float(np.cos(rotation))
    sin_r = float(np.sin(rotation))
    wcs.wcs.pc = np.array(
        [[cos_r, -sin_r], [sin_r, cos_r]]
    )
    return wcs


# ---- image seeding -----------------------------------------
def _seed_image(
    gaia_sources, pixel_scale, obs_coords, fwhm,
    field_of_view, sigma_limit, band,
    rotation, flip_x, flip_y, scale_factor,
):
    """Create a synthetic sky image with Gaussian PSFs."""
    fov_scaled = field_of_view * scale_factor
    npixel_x = int(
        fov_scaled[0].to(uu.deg)
        // (pixel_scale * uu.pixel).to(uu.deg)
    )
    npixel_y = int(
        fov_scaled[1].to(uu.deg)
        // (pixel_scale * uu.pixel).to(uu.deg)
    )
    fwhm_pix = (
        fwhm.to(uu.arcsec)
        / (pixel_scale * uu.pixel).to(uu.arcsec)
    )
    wcs = _setup_wcs(
        (npixel_y, npixel_x), obs_coords,
        pixel_scale, rotation, flip_x, flip_y,
    )
    # noise background
    image = np.random.normal(
        size=(npixel_y, npixel_x), scale=1.0, loc=0,
    )
    # PSF amplitudes from magnitudes
    nsig_psf = np.array(
        10 ** ((sigma_limit - gaia_sources[band]) / 2.5)
    )
    # world-to-pixel for all sources
    x_src, y_src = wcs.all_world2pix(
        gaia_sources['ra'], gaia_sources['dec'], 0,
    )
    # pixel grid
    y, x = np.mgrid[0:npixel_y, 0:npixel_x]
    # Gaussian sigma from FWHM
    ew = fwhm_pix.value / (2 * np.sqrt(2 * np.log(2)))
    # rotation values for PSF elongation
    cos_rot = float(np.cos(rotation))
    sin_rot = float(np.sin(rotation))
    # only process sources within image bounds
    margin = 6 * ew
    in_bounds = (
        (x_src > -margin)
        & (x_src < npixel_x + margin)
        & (y_src > -margin)
        & (y_src < npixel_y + margin)
        & np.isfinite(nsig_psf)
    )
    xs = x_src[in_bounds]
    ys = y_src[in_bounds]
    nsig = nsig_psf[in_bounds]
    # seed each source as a Gaussian + halo
    for i in range(len(xs)):
        xdiff0 = x - xs[i]
        ydiff0 = y - ys[i]
        xdiff = xdiff0 * cos_rot - ydiff0 * sin_rot
        ydiff = xdiff0 * sin_rot + ydiff0 * cos_rot
        r2 = xdiff ** 2 + ydiff ** 2
        exp1 = np.exp(-r2 / (2 * ew ** 2))
        exp_halo = np.exp(
            -r2 / (2 * (ew * 3) ** 2)
        )
        image += nsig[i] * (exp1 + 1e-3 * exp_halo)
    # arcsinh stretch for display
    image = np.arcsinh(image)
    return image, wcs


# ---- matplotlib rendering ----------------------------------
def _render_map(
    fcfg: Dict[str, Any],
    image: np.ndarray,
    wcs: WCS,
    obs_coords: SkyCoord,
    title: str,
    field_of_view: Any,
    pixel_scale: Any,
    scale_factor: float,
    suptitle: str,
) -> str:
    """Render a finder chart panel to base64-encoded PNG."""
    compass_frac = fcfg['compass_frac']
    scale_size = fcfg['scale_size']
    pixel_scale_g = fcfg['pixel_scale'].get(
        'G', pixel_scale
    )
    fig, frame = plt.subplots(
        ncols=1, nrows=1, figsize=(10, 10),
    )
    frame.imshow(
        image, origin='lower',
        vmin=np.arcsinh(-3), vmax=np.arcsinh(200),
        cmap='gist_heat', interpolation='nearest',
    )
    color = 'cyan'
    # current position marker
    x_curr, y_curr = wcs.all_world2pix(
        obs_coords.ra.value, obs_coords.dec.value, 0,
    )
    frame.plot(
        x_curr, y_curr,
        marker='o', color=color, ms=30, mfc='none',
    )
    frame.plot(
        x_curr, y_curr,
        marker='+', color=color, ms=30, mfc='none',
    )
    # compass arrows
    x_comp0 = 0.9 * image.shape[0]
    y_comp0 = 0.1 * image.shape[0]
    ra_comp, dec_comp = wcs.all_pix2world(
        x_comp0, y_comp0, 0,
    )
    cos_dec = np.cos(float(dec_comp) * uu.deg)
    length_world = field_of_view * scale_factor
    ra_comp_e = (
        ra_comp
        + (length_world[0].to(uu.deg).value
           * compass_frac) / cos_dec
    )
    dec_comp_n = (
        dec_comp
        + length_world[1].to(uu.deg).value
        * compass_frac
    )
    x_comp, y_comp = wcs.all_world2pix(
        ra_comp, dec_comp, 0,
    )
    x_comp_e, y_comp_e = wcs.all_world2pix(
        ra_comp_e, dec_comp, 0,
    )
    x_comp_n, y_comp_n = wcs.all_world2pix(
        ra_comp, dec_comp_n, 0,
    )
    arrow_kw = dict(
        ha='center', va='center', color=color,
        arrowprops=dict(
            arrowstyle='<-', color=color,
            shrinkA=0.0, shrinkB=0.0,
        ),
    )
    frame.annotate(
        'N', (x_comp, y_comp),
        (x_comp_n, y_comp_n), **arrow_kw,
    )
    frame.annotate(
        'E', (x_comp, y_comp),
        (x_comp_e, y_comp_e), **arrow_kw,
    )
    # scale bar
    length = (scale_size / pixel_scale_g).value
    x_scale = 0.1 * image.shape[0]
    y_scale = 0.1 * image.shape[1]
    x_stext = x_scale + 0.5 * length
    patch = FancyArrowPatch(
        (x_scale, y_scale),
        (x_scale + length, y_scale),
        arrowstyle='-',
        shrinkA=0.0, shrinkB=0.0,
        capstyle='round', color=color, linewidth=2,
    )
    frame.text(
        x_stext, y_scale,
        f'{scale_size.value:g}'
        f' {scale_size.unit:unicode}',
        ha='center', va='bottom', color=color,
    )
    frame.add_patch(patch)
    # remove ticks
    frame.set_xticks([])
    frame.set_yticks([])
    # field of view rectangle
    npixel_x = int(
        field_of_view[0].to(uu.deg)
        // (pixel_scale * uu.pixel).to(uu.deg)
    )
    npixel_y = int(
        field_of_view[1].to(uu.deg)
        // (pixel_scale * uu.pixel).to(uu.deg)
    )
    cx = image.shape[1] // 2
    cy = image.shape[0] // 2
    x0 = cx - npixel_x // 2
    y0 = cy - npixel_y // 2
    rect = Rectangle(
        (x0, y0), npixel_x, npixel_y,
        linewidth=2, edgecolor=color,
        facecolor='none', ls='--',
    )
    frame.add_patch(rect)
    # titles
    frame.set_title(
        title, y=1.0, pad=-14, color=color,
    )
    fig.suptitle(
        suptitle, fontsize=10, color='white',
    )
    fig.tight_layout()
    # convert to base64 PNG
    buf = io.BytesIO()
    fig.savefig(
        buf, format='png', dpi=120,
        bbox_inches='tight', facecolor='#1a1a2e',
    )
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('ascii')
