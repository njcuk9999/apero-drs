#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI – Finder chart plot generation for the data portal object page.

Queries Gaia DR3 and 2MASS catalogs to build simulated sky images around
a target, rendered with matplotlib and returned as base64-encoded PNGs.

The number and identity of bands to plot is driven by the instrument
profile YAML key ``finder.BANDS`` (e.g. ``["G", "J"]``).

Based on apero-drs ``apero.tools.module.ari.ari_find``.

Created on 2026-03-25

@author: cook
"""
from __future__ import annotations

import base64
import io
import warnings
from typing import Any, Dict, List, Optional, Tuple

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from astropy import units as uu
from astropy.coordinates import SkyCoord, Distance
from astropy.time import Time
from astropy.wcs import WCS
from astroquery.utils.tap.core import TapPlus
from matplotlib.patches import FancyArrowPatch, Rectangle
from tqdm import tqdm

from apero_ri.base import base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.plots.plot_find'
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
    source_id as source_id,ra,dec,parallax,pmra,pmdec,phot_g_mean_mag,
    phot_rp_mean_mag,phot_bp_mean_mag,phot_g_mean_flux,phot_rp_mean_flux,
    phot_bp_mean_flux
FROM gaiadr3.gaia_source
WHERE
    1=CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', {ra}, {dec}, {radius}))
"""
GAIA_EPOCH = 2016.0

# 2MASS TAP endpoint
TMASS_URL = 'https://irsa.ipac.caltech.edu/TAP'
# noinspection SqlNoDataSourceInspection,SqlDialectInspection
TMASS_QUERY = """
SELECT
    {TMASS_COLS}
FROM fp_2mass.fp_psc
WHERE
    1=CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', {ra}, {dec}, {radius}))
"""
TMASS_COLS = 'ra,dec,j_m,h_m,k_m,jdate'
TMASS_RADIUS = 2 * uu.arcsec
TMASS_EPOCH = 2000.0


# =============================================================================
# Public API
# =============================================================================
def generate_finder_charts(obj_props: Dict[str, Any],
                           preset: Dict[str, Any],
                           ) -> Dict[str, Any]:
    """Generate finder chart images for all configured bands.

    Parameters
    ----------
    obj_props : dict
        Object table row with RA_DEG, DEC_DEG, PMRA, PMDE, PLX, EPOCH etc.
    preset : dict
        Full instrument profile dict (from YAML).

    Returns
    -------
    dict
        ``{'success': bool, 'images': [...], 'bands': [...], 'title': str,
           'error': str}``
        Each entry in *images* is a base64-encoded PNG string.
    """
    finder_cfg = preset.get('finder')
    if not finder_cfg:
        return dict(success=False, images=[], bands=[], title='',
                    error='No finder configuration in instrument profile.')

    # Resolve bands to plot
    bands = finder_cfg.get('BANDS')
    if not bands:
        bands = list(finder_cfg.get('FIELD_OF_VIEW', {}).keys())
    if not bands:
        return dict(success=False, images=[], bands=[], title='',
                    error='No bands configured for finder charts.')

    # Build the object dictionary from obj_props
    objdict = _build_objdict(obj_props)
    if objdict is None:
        return dict(success=False, images=[], bands=[], title='',
                    error='Missing RA/Dec for this object.')

    # Pre-compute shared finder parameters (FOV, pixel scale, etc.)
    fcfg = _prepare_finder_config(finder_cfg, bands)

    # Propagate coordinates to now
    date = Time.now()
    obs_coords, obs_time = _propagate_coords(objdict, date)

    # -----------------------------------------------------------------
    # Fetch catalogue data
    # -----------------------------------------------------------------
    try:
        gaia_sources = _get_gaia_sources(obs_coords, obs_time,
                                         fcfg['radius']['G'],
                                         fcfg['max_pm'])
    except Exception as exc:
        return dict(success=False, images=[], bands=[], title='',
                    error=f'Gaia query failed: {exc}')

    if 'J' in bands or 'H' in bands or 'K' in bands:
        try:
            _fill_2mass(gaia_sources, obs_coords, obs_time,
                        fcfg['radius'].get('J', fcfg['radius']['G']),
                        fcfg['max_pm'], fcfg['sigma_limit'],
                        fcfg['mag_limit'])
        except Exception:
            pass  # 2MASS failure is non-fatal; J/H/K will be at limit

    # -----------------------------------------------------------------
    # Generate one image per band
    # -----------------------------------------------------------------
    images: List[str] = []
    titles: List[str] = []
    band_labels = {'G': 'Gaia G', 'J': '2MASS J', 'H': '2MASS H',
                   'K': '2MASS K'}
    objname = objdict['OBJNAME']

    closest = int(np.argmin(gaia_sources['separation']))
    suptitle = (f'Object: {objname}\n'
                f'Date: {obs_time.iso}\n'
                f'RA: {obs_coords.ra.to_string(uu.hourangle, sep=":")}'
                f'   Dec: {obs_coords.dec.to_string(uu.deg, sep=":")}\n'
                f'Gmag: {gaia_sources["G"][closest]:.2f}   '
                f'Jmag: {gaia_sources["J"][closest]:.2f}')

    for band in bands:
        ps = fcfg['pixel_scale'][band]
        fov = fcfg['fov'][band]
        sf = fcfg['scale_factor'][band]
        fwhm = fcfg['fwhm'][band]
        sl = fcfg['sigma_limit'].get(band, 18)
        rot = fcfg['transform_rotate'][band]
        fx = fcfg['flip_x'][band]
        fy = fcfg['flip_y'][band]

        image, wcs = _seed_image(gaia_sources, ps, obs_coords, fwhm,
                                 fov, sl, band, rot, fx, fy, sf)
        label = band_labels.get(band, band)
        png_b64 = _render_map(fcfg, image, wcs, obs_coords, label,
                              fov, ps, sf, suptitle)
        images.append(png_b64)
        titles.append(label)

    return dict(success=True, images=images, bands=bands,
                titles=titles, title=suptitle, error='')


# =============================================================================
# Internal helpers
# =============================================================================
def _build_objdict(obj_props: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Extract needed fields from the object table row."""
    ra = _float_or(obj_props, ['RA [Deg]', 'RA_DEG'])
    dec = _float_or(obj_props, ['Dec [Deg]', 'DEC_DEG'])
    if ra is None or dec is None:
        return None
    return dict(
        OBJNAME=obj_props.get('OBJNAME', 'Unknown'),
        RA_DEG=ra,
        DEC_DEG=dec,
        EPOCH=_float_or(obj_props, ['EPOCH']) or Time(2000.0, format='decimalyear').jd,
        PLX=_float_or(obj_props, ['Plx [mas]', 'PLX']) or 0.0,
        PMRA=_float_or(obj_props, ['PMRA [mas/yr]', 'PMRA']) or 0.0,
        PMDE=_float_or(obj_props, ['PMDE [mas/yr]', 'PMDE', 'PMDEC [mas/yr]',
                                    'PMDEC']) or 0.0,
    )


def _float_or(d: Dict[str, Any], keys: List[str]) -> Optional[float]:
    for k in keys:
        v = d.get(k)
        if v is not None:
            try:
                return float(v)
            except (ValueError, TypeError):
                continue
    return None


def _prepare_finder_config(cfg: Dict[str, Any],
                           bands: List[str]) -> Dict[str, Any]:
    """Parse the raw YAML finder dict into typed quantities."""
    fov: Dict[str, Any] = {}
    for band in cfg.get('FIELD_OF_VIEW', {}):
        fov[band] = np.array(cfg['FIELD_OF_VIEW'][band]) * uu.arcsec

    # Scale factors
    scale_factor: Dict[str, Any] = {}
    sf_cfg = cfg.get('SCALE_FACTOR', {})
    sf_bandname = list(sf_cfg.keys())[0] if sf_cfg else bands[0]
    sf_bandvalue = sf_cfg.get(sf_bandname, 1.5)
    fov_bandvalue = fov.get(sf_bandname, np.array([77.6, 77.6]) * uu.arcsec)
    for band in fov:
        if band == sf_bandname:
            scale_factor[band] = sf_bandvalue
        else:
            scale_factor[band] = sf_bandvalue * (fov_bandvalue / fov[band])

    # Radius
    radius: Dict[str, Any] = {}
    for band in fov:
        sf = scale_factor[band]
        radius[band] = np.max(sf * fov[band] / np.sqrt(2))

    # Pixel scale
    pixel_scale: Dict[str, float] = {}
    for band, val in cfg.get('PIXEL_SCALE', {}).items():
        pixel_scale[band] = val * uu.arcsec / uu.pixel

    # Rotation
    transform_rotate: Dict[str, Any] = {}
    for band, val in cfg.get('TRANSFORM_ROTATE', {}).items():
        transform_rotate[band] = val * uu.deg

    # FWHM
    fwhm: Dict[str, Any] = {}
    for band, val in cfg.get('FWHM', {}).items():
        fwhm[band] = val * uu.arcsec

    max_pm = cfg.get('MAX_PM', 11) * uu.arcsec / uu.yr
    scale_size = cfg.get('SCALE_SIZE', 10) * uu.arcsec
    compass_frac = cfg.get('COMPASS_FRAC', 0.075)

    flip_x = cfg.get('FLIP_X', {})
    flip_y = cfg.get('FLIP_Y', {})

    return dict(
        fov=fov, scale_factor=scale_factor, radius=radius,
        pixel_scale=pixel_scale, transform_rotate=transform_rotate,
        fwhm=fwhm, max_pm=max_pm, scale_size=scale_size,
        compass_frac=compass_frac, flip_x=flip_x, flip_y=flip_y,
        sigma_limit=cfg.get('SIGMA_LIMIT', {}),
        mag_limit=cfg.get('MAG_LIMIT', -1),
    )


# ---- coordinate propagation ------------------------------------------------
def _propagate_coords(objdata: Dict[str, Any], obs_time: Time
                      ) -> Tuple[SkyCoord, Time]:
    if objdata['PLX'] <= 0:
        distance = None
    else:
        distance = Distance(parallax=objdata['PLX'] * uu.mas)
    coords = SkyCoord(
        ra=objdata['RA_DEG'] * uu.deg,
        dec=objdata['DEC_DEG'] * uu.deg,
        distance=distance,
        pm_ra_cosdec=objdata['PMRA'] * uu.mas / uu.yr,
        pm_dec=objdata['PMDE'] * uu.mas / uu.yr,
        obstime=Time(objdata['EPOCH'], format='jd'),
    )
    with warnings.catch_warnings(record=True) as _:
        jepoch = Time(objdata['EPOCH'], format='jd')
        delta_time = (obs_time.jd - jepoch.jd) * uu.day
    with warnings.catch_warnings(record=True) as _:
        curr_coords = coords.apply_space_motion(dt=delta_time)
    return curr_coords, obs_time


# ---- Gaia query -------------------------------------------------------------
def _get_gaia_sources(coords: SkyCoord, obstime: Time,
                      radius: Any, max_pm: Any
                      ) -> Dict[str, np.ndarray]:
    gaia_time = Time(GAIA_EPOCH, format='decimalyear')
    with warnings.catch_warnings(record=True) as _:
        delta_time_now = (obstime.jd - gaia_time.jd) * uu.day
    search = abs(delta_time_now * max_pm).to(uu.deg)
    radius = radius.to(uu.deg) + search

    gaia = TapPlus(url=GAIA_URL)
    gaia_query = GAIA_QUERY.format(ra=coords.ra.deg, dec=coords.dec.deg,
                                   radius=radius.to(uu.deg).value)
    job = gaia.launch_job(gaia_query)
    table = job.get_results()
    del job

    if len(table) == 2000:
        gaia2 = TapPlus(url=GAIA_URL)
        job2 = gaia2.launch_job_async(gaia_query)
        table = job2.get_results()
        del job2

    if 'SOURCE_ID' in table.colnames:
        table['source_id'] = table['SOURCE_ID']

    n = len(table)
    if n == 0:
        return {k: np.array([]) for k in
                ['gaia_id', 'ra', 'dec', 'G', 'Rp', 'Bp',
                 'J', 'H', 'K', 'ra_gaia', 'dec_gaia',
                 'pmra', 'pmdec', 'parallax', 'separation']}

    # Extract arrays
    ra_arr = np.array(table['ra'], dtype=float)
    dec_arr = np.array(table['dec'], dtype=float)
    pmra_arr = np.array(table['pmra'], dtype=float)
    pmdec_arr = np.array(table['pmdec'], dtype=float)
    plx_arr = np.array(table['parallax'], dtype=float)
    plx_mask = table['parallax'].mask

    # Build distances (set invalid parallax to large distance)
    plx_safe = np.where(plx_mask | (plx_arr <= 0), 1e-6, plx_arr)
    distances = Distance(parallax=plx_safe * uu.mas)

    # Vectorized SkyCoord + proper motion propagation
    gaia_coords = SkyCoord(
        ra=ra_arr * uu.deg, dec=dec_arr * uu.deg,
        distance=distances,
        pm_ra_cosdec=pmra_arr * uu.mas / uu.yr,
        pm_dec=pmdec_arr * uu.mas / uu.yr,
        obstime=gaia_time, frame='icrs',
    )
    with warnings.catch_warnings(record=True) as _:
        curr = gaia_coords.apply_space_motion(dt=delta_time_now)
    sep = coords.separation(curr)

    # Mark invalid parallaxes as NaN
    plx_out = np.where(plx_mask | (plx_arr <= 0), np.nan, plx_arr)

    return {
        'gaia_id': np.array(table['source_id']),
        'ra': curr.ra.deg,
        'dec': curr.dec.deg,
        'G': np.array(table['phot_g_mean_mag'], dtype=float),
        'Rp': np.array(table['phot_rp_mean_mag'], dtype=float),
        'Bp': np.array(table['phot_bp_mean_mag'], dtype=float),
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


# ---- 2MASS fill -------------------------------------------------------------
def _fill_2mass(gaia_sources: Dict[str, np.ndarray],
                obs_coords: SkyCoord, obs_time: Time,
                radius: Any, max_pm: Any,
                sigma_limit: Dict[str, float],
                mag_limit: float) -> None:
    tmass = TapPlus(url=TMASS_URL)
    tmass_time = Time(TMASS_EPOCH, format='decimalyear')
    with warnings.catch_warnings(record=True) as _:
        delta_time_2mass = (tmass_time.jd - obs_time.jd) * uu.day
    obs_copy = SkyCoord(obs_coords)
    with warnings.catch_warnings(record=True) as _:
        tmass_coords_center = obs_copy.apply_space_motion(dt=delta_time_2mass)

    search = abs(delta_time_2mass * max_pm).to(uu.deg)
    r = radius.to(uu.deg) + search

    tmass_query = TMASS_QUERY.format(
        TMASS_COLS=TMASS_COLS,
        ra=tmass_coords_center.ra.deg,
        dec=tmass_coords_center.dec.deg,
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
    for it, col in enumerate(TMASS_COLS.split(',')):
        table0[col] = table0[f'col_{it}']
        del table0[f'col_{it}']

    mean_jdate = np.mean(table0['jdate'])
    jdate_time = Time(mean_jdate, format='jd')
    tmass_cat_coords = SkyCoord(ra=table0['ra'], dec=table0['dec'],
                                distance=None, pm_ra_cosdec=None,
                                pm_dec=None, obstime=jdate_time, frame='icrs')

    # Propagate all Gaia sources to 2MASS epoch in bulk
    gaia_time = Time(GAIA_EPOCH, format='decimalyear')
    with warnings.catch_warnings(record=True) as _:
        delta_time_jdate = (jdate_time.jd - gaia_time.jd) * uu.day

    n = len(gaia_sources['parallax'])
    plx_arr = gaia_sources['parallax']
    plx_safe = np.where(np.isnan(plx_arr) | (plx_arr <= 0), 1e-6, plx_arr)
    distances = Distance(parallax=plx_safe * uu.mas)

    gaia_coords_all = SkyCoord(
        ra=gaia_sources['ra_gaia'] * uu.deg,
        dec=gaia_sources['dec_gaia'] * uu.deg,
        distance=distances,
        pm_ra_cosdec=gaia_sources['pmra'] * uu.mas / uu.yr,
        pm_dec=gaia_sources['pmdec'] * uu.mas / uu.yr,
        obstime=gaia_time, frame='icrs',
    )
    with warnings.catch_warnings(record=True) as _:
        jdate_coords_all = gaia_coords_all.apply_space_motion(
            dt=delta_time_jdate)

    # Vectorized cross-match: find closest 2MASS source for each Gaia source
    idx, sep2d, _ = jdate_coords_all.match_to_catalog_sky(tmass_cat_coords)

    jmag_default = sigma_limit.get('J', 15) + mag_limit
    hmag_default = sigma_limit.get('H', 15) + mag_limit
    kmag_default = sigma_limit.get('K', 15) + mag_limit

    matched = sep2d <= TMASS_RADIUS
    j_arr = np.array(table0['j_m'])
    h_arr = np.array(table0['h_m'])
    k_arr = np.array(table0['k_m'])

    gaia_sources['J'] = np.where(matched, j_arr[idx], jmag_default)
    gaia_sources['H'] = np.where(matched, h_arr[idx], hmag_default)
    gaia_sources['K'] = np.where(matched, k_arr[idx], kmag_default)


# ---- WCS setup --------------------------------------------------------------
def _setup_wcs(image_shape: Tuple[int, int], cent_coords: SkyCoord,
               pixel_scale: Any, rotation: Any,
               flip_x: bool, flip_y: bool) -> WCS:
    naxis2, naxis1 = image_shape
    pix_scale = pixel_scale.to(uu.deg / uu.pixel).value
    wcs = WCS(naxis=2)
    wcs.wcs.crpix = [naxis1 / 2, naxis2 / 2]
    if flip_y and flip_x:
        wcs.wcs.cdelt = np.array([pix_scale, -pix_scale])
    elif flip_x:
        wcs.wcs.cdelt = np.array([pix_scale, pix_scale])
    elif flip_y:
        wcs.wcs.cdelt = np.array([pix_scale, -pix_scale])
    else:
        wcs.wcs.cdelt = np.array([-pix_scale, pix_scale])
    wcs.wcs.crval = [cent_coords.ra.deg, cent_coords.dec.deg]
    wcs.wcs.ctype = ["RA---TAN", "DEC--TAN"]
    wcs.wcs.pc = np.array([
        [np.cos(rotation), -np.sin(rotation)],
        [np.sin(rotation), np.cos(rotation)],
    ])
    return wcs


# ---- image seeding ----------------------------------------------------------
def _seed_image(gaia_sources, pixel_scale, obs_coords, fwhm,
                field_of_view, sigma_limit, band, rotation,
                flip_x, flip_y, scale_factor):
    fov_scaled = field_of_view * scale_factor
    npixel_x = int(fov_scaled[0].to(uu.deg) // (pixel_scale * uu.pixel).to(uu.deg))
    npixel_y = int(fov_scaled[1].to(uu.deg) // (pixel_scale * uu.pixel).to(uu.deg))
    fwhm_pix = fwhm.to(uu.arcsec) / (pixel_scale * uu.pixel).to(uu.arcsec)

    wcs = _setup_wcs((npixel_y, npixel_x), obs_coords, pixel_scale,
                     rotation, flip_x, flip_y)
    image = np.random.normal(size=(npixel_y, npixel_x), scale=1.0, loc=0)
    nsig_psf = np.array(10 ** ((sigma_limit - gaia_sources[band]) / 2.5))

    x_sources, y_sources = wcs.all_world2pix(gaia_sources['ra'],
                                             gaia_sources['dec'], 0)
    y, x = np.mgrid[0:npixel_y, 0:npixel_x]
    ew = fwhm_pix.value / (2 * np.sqrt(2 * np.log(2)))
    cos_rot = np.cos(rotation).value if hasattr(np.cos(rotation), 'value') else np.cos(rotation)
    sin_rot = np.sin(rotation).value if hasattr(np.sin(rotation), 'value') else np.sin(rotation)

    # Filter to sources that are within the image bounds (with margin)
    margin = 6 * ew  # 6 sigma cutoff
    in_bounds = ((x_sources > -margin) & (x_sources < npixel_x + margin) &
                 (y_sources > -margin) & (y_sources < npixel_y + margin) &
                 np.isfinite(nsig_psf))
    x_src = x_sources[in_bounds]
    y_src = y_sources[in_bounds]
    nsig = nsig_psf[in_bounds]

    for i in range(len(x_src)):
        xdiff0 = x - x_src[i]
        ydiff0 = y - y_src[i]
        xdiff = xdiff0 * cos_rot - ydiff0 * sin_rot
        ydiff = xdiff0 * sin_rot + ydiff0 * cos_rot
        r2 = xdiff ** 2 + ydiff ** 2
        exp1 = np.exp(-r2 / (2 * ew ** 2))
        exp_halo = np.exp(-r2 / (2 * (ew * 3) ** 2))
        image += nsig[i] * (exp1 + 1e-3 * exp_halo)

    image = np.arcsinh(image)
    return image, wcs


# ---- matplotlib rendering ---------------------------------------------------
def _render_map(fcfg: Dict[str, Any], image: np.ndarray, wcs: WCS,
                obs_coords: SkyCoord, title: str,
                field_of_view: Any, pixel_scale: Any,
                scale_factor: float, suptitle: str) -> str:
    """Render a single finder chart panel and return base64-encoded PNG."""
    compass_frac = fcfg['compass_frac']
    scale_size = fcfg['scale_size']
    pixel_scale_g = fcfg['pixel_scale'].get('G', pixel_scale)

    fig, frame = plt.subplots(ncols=1, nrows=1, figsize=(10, 10))
    frame.imshow(image, origin='lower', vmin=np.arcsinh(-3),
                 vmax=np.arcsinh(200),
                 cmap='gist_heat', interpolation='nearest')
    color = 'cyan'

    # Current position marker
    x_curr, y_curr = wcs.all_world2pix(obs_coords.ra.value,
                                       obs_coords.dec.value, 0)
    frame.plot(x_curr, y_curr, marker='o', color=color, ms=30, mfc='none')
    frame.plot(x_curr, y_curr, marker='+', color=color, ms=30, mfc='none')

    # Compass
    x_comp0 = 0.9 * image.shape[0]
    y_comp0 = 0.1 * image.shape[0]
    ra_comp, dec_comp = wcs.all_pix2world(x_comp0, y_comp0, 0)
    cos_dec = np.cos(float(dec_comp) * uu.deg)
    length_world = field_of_view * scale_factor
    ra_comp_e = ra_comp + (length_world[0].to(uu.deg).value * compass_frac) / cos_dec
    dec_comp_n = dec_comp + length_world[1].to(uu.deg).value * compass_frac
    x_comp, y_comp = wcs.all_world2pix(ra_comp, dec_comp, 0)
    x_comp_e, y_comp_e = wcs.all_world2pix(ra_comp_e, dec_comp, 0)
    x_comp_n, y_comp_n = wcs.all_world2pix(ra_comp, dec_comp_n, 0)
    arrow_kw = dict(ha='center', va='center', color=color,
                    arrowprops=dict(arrowstyle='<-', color=color,
                                   shrinkA=0.0, shrinkB=0.0))
    frame.annotate('N', (x_comp, y_comp), (x_comp_n, y_comp_n), **arrow_kw)
    frame.annotate('E', (x_comp, y_comp), (x_comp_e, y_comp_e), **arrow_kw)

    # Scale bar
    length = (scale_size / pixel_scale_g).value
    x_scale = 0.1 * image.shape[0]
    y_scale = 0.1 * image.shape[1]
    x_stext = x_scale + 0.5 * length
    patch = FancyArrowPatch((x_scale, y_scale),
                            (x_scale + length, y_scale),
                            arrowstyle='-', shrinkA=0.0, shrinkB=0.0,
                            capstyle='round', color=color, linewidth=2)
    frame.text(x_stext, y_scale,
               f'{scale_size.value:g} {scale_size.unit:unicode}',
               ha='center', va='bottom', color=color)
    frame.add_patch(patch)

    # Remove ticks
    frame.set_xticks([])
    frame.set_yticks([])

    # Field of view rectangle
    npixel_x = int(field_of_view[0].to(uu.deg)
                   // (pixel_scale * uu.pixel).to(uu.deg))
    npixel_y = int(field_of_view[1].to(uu.deg)
                   // (pixel_scale * uu.pixel).to(uu.deg))
    center_x, center_y = image.shape[1] // 2, image.shape[0] // 2
    x0, y0 = center_x - npixel_x // 2, center_y - npixel_y // 2
    rect = Rectangle((x0, y0), npixel_x, npixel_y, linewidth=2,
                      edgecolor=color, facecolor='none', ls='--')
    frame.add_patch(rect)

    # Titles
    frame.set_title(title, y=1.0, pad=-14, color=color)
    fig.suptitle(suptitle, fontsize=10, color='white')

    fig.tight_layout()

    # Convert to base64 PNG
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=120, bbox_inches='tight',
                facecolor='#1a1a2e')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('ascii')


# ---------------------------------------------------------------------------
# Debug / standalone entry point
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    import yaml, pathlib

    # GL699 (Barnard's Star) properties
    obj_props = {
        'OBJNAME': 'GL699',
        'RA_DEG': 269.45207695,
        'DEC_DEG': 4.69339088,
        'PMRA': -801.551,
        'PMDEC': 10362.394,
        'PLX': 546.9759,
    }

    # Load the SPIRou v8 preset
    preset_dir = pathlib.Path(__file__).resolve().parents[1] / 'admin' / 'instruments'
    preset_file = preset_dir / 'spirou_v8.yaml'
    with open(preset_file, 'r') as f:
        preset = yaml.safe_load(f)

    charts = generate_finder_charts(obj_props, preset)

    out_dir = pathlib.Path('finder_debug')
    out_dir.mkdir(exist_ok=True)
    for key, b64data in charts.items():
        png_path = out_dir / f'{obj_props["OBJNAME"]}_{key}.png'
        png_path.write_bytes(base64.b64decode(b64data))
        print(f'Saved {png_path}')
    print('Done.')
