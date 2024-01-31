#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-01-30 at 14:01

@author: cook
"""
import os
import warnings
from typing import Any, Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from astropy import units as uu
from astropy.coordinates import SkyCoord, Distance
from astropy.table import Table
from astropy.time import Time
from astropy.wcs import WCS
from astroquery.utils.tap.core import TapPlus
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyArrowPatch
from matplotlib.patches import Rectangle
from tqdm import tqdm

from apero.base import base
from apero.core import constants
from apero.core.core import drs_log

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero.tools.module.ari.ari_core.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# -----------------------------------------------------------------------------
# Get ParamDict
ParamDict = constants.ParamDict
# Get Logging function
WLOG = drs_log.wlog
# set the date for finder charts
DATE = Time.now()
# Skip done
SKIP_DONE = True
# columns in the apero astrometric database
ASTROM_COLS = ['OBJNAME', 'RA_DEG', 'DEC_DEG', 'PMRA', 'PMDE', 'PLX', 'RV',
               'EPOCH']
# -----------------------------------------------------------------------------
# Gaia specific
# -----------------------------------------------------------------------------
# URL for Gaia
GAIA_URL = 'https://gea.esac.esa.int/tap-server/tap'
# noinspection SqlNoDataSourceInspection,SqlDialectInspection
GAIA_QUERY = """
SELECT
    source_id,ra,dec,parallax,pmra,pmdec,phot_g_mean_mag,phot_rp_mean_mag,
    phot_bp_mean_mag, phot_g_mean_flux, phot_rp_mean_flux, phot_bp_mean_flux
FROM gaiadr3.gaia_source
WHERE 
    1=CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', {ra}, {dec}, {radius}))
"""
# define epoch
GAIA_EPOCH = 2016.0
# -----------------------------------------------------------------------------
# Gaia specific
# -----------------------------------------------------------------------------
# define mean epoch
TMASS_EPOCH = 2000.0
# URL for Gaia
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
# CROSSMATCH RADIUS (SHOULD BE SMALL)
TMASS_RADIUS = 2 * uu.arcsec
# -----------------------------------------------------------------------------
# Other Surveys
# -----------------------------------------------------------------------------
# Define the epoch for SIMBAD
SIMBAD_EPOCH = 2000.0


# =============================================================================
# Define functions
# =============================================================================
def load_params(params: ParamDict) -> ParamDict:
    # set function name
    func_name = __NAME__ + '.load_params()'
    # check if we already have params loaded (don't load twice)
    if 'ARI_FINDER' in params:
        if params['ARI_FINDER']['loaded']:
            return params
    # get finding chart parameters
    finder_yaml = params['ARI_FINDING_CHARTS']['yaml']
    finder_create = params['ARI_FINDING_CHARTS']['create']
    finder_reset = params['ARI_FINDING_CHARTS']['reset']
    # storage for finder dict
    finder_dict = dict(loaded=True)
    # ----------------------------------------------------------------------
    # add path to the finder_yaml
    finder_path = str(os.path.join(params['DRS_DATA_OTHER'], 'ari-config',
                                   finder_yaml))
    # ----------------------------------------------------------------------
    # setup the directory
    finder_dict['directory'] = str(os.path.join(params['DRS_DATA_OTHER'],
                                                'ari', 'finder'))
    # add in the reset criteria
    finder_dict['reset'] = finder_reset
    # ------------------------------------------------------------------------
    # make sure finder directory exists
    if not os.path.exists(finder_dict['directory']):
        os.makedirs(finder_dict['directory'])
    # ------------------------------------------------------------------------
    if not finder_create:
        finder_dict['create'] = False
        # push the directory into params
        params.set('ARI_FINDER', value=finder_dict, source=func_name)
        # return params
        return params
    elif not os.path.exists(finder_path):
        finder_dict['create'] = False
        # push the directory into params
        params.set('ARI_FINDER', value=finder_dict, source=func_name)
        # return params
        return params
    else:
        finder_dict['create'] = True
    # ----------------------------------------------------------------------
    # load the yaml
    raw_dict = base.load_yaml(finder_path)
    # look for the instrument -if it doesn't exist we do not run finding
    #   charts
    if params['ARI_INSTRUMENT'] not in raw_dict:
        finder_dict['create'] = False
        # push the directory into params
        params.set('ARI_FINDER', value=finder_dict, source=func_name)
        # return params
        return params

    # now push all other values into finder_dict
    for key in raw_dict[params['ARI_INSTRUMENT']]:
        finder_dict[key] = raw_dict[params['ARI_INSTRUMENT']][key]
    # ----------------------------------------------------------------------
    # convert FOV to a numpy array and add astropy units (arcsec)
    for band in finder_dict['FIELD_OF_VIEW']:
        fov_band = finder_dict['FIELD_OF_VIEW'][band]
        finder_dict['FIELD_OF_VIEW'][band] = np.array(fov_band) * uu.arcsec
    # ----------------------------------------------------------------------
    # set up scale factor for other bands
    sf_bandname = list(finder_dict['SCALE_FACTOR'].keys())[0]
    sf_bandvalue = finder_dict['SCALE_FACTOR'][sf_bandname]
    fov_bandvalue = finder_dict['FIELD_OF_VIEW'][sf_bandname]
    # loop around bands
    for band_it in finder_dict['FIELD_OF_VIEW']:
        fov_band_it = finder_dict['FIELD_OF_VIEW'][band_it]
        # do not recalculate the given band
        if band_it != sf_bandname:
            sf_it = sf_bandvalue * (fov_bandvalue / fov_band_it)
            # push into finder_dict
            finder_dict['SCALE_FACTOR'][band_it] = sf_it
    # ----------------------------------------------------------------------
    # set up the radius
    finder_dict['RADIUS'] = dict()
    # loop around all bands
    for band in finder_dict['FIELD_OF_VIEW']:
        sf_band = finder_dict['SCALE_FACTOR'][band]
        fov_band = finder_dict['FIELD_OF_VIEW'][band]
        radius_band = np.max(sf_band * fov_band / np.sqrt(2))
        # push into finder_dict
        finder_dict['RADIUS'][band] = radius_band
    # ----------------------------------------------------------------------
    # pixel scale should be in arcsec / pixel
    for band in finder_dict['PIXEL_SCALE']:
        finder_dict['PIXEL_SCALE'][band] *= uu.arcsec / uu.pixel
    # ----------------------------------------------------------------------
    # transform rotate should be in degrees
    for band in finder_dict['TRANSFORM_ROTATE']:
        finder_dict['TRANSFORM_ROTATE'][band] *= uu.deg
    # ----------------------------------------------------------------------
    # FWHM should be in arcsec
    for band in finder_dict['FWHM']:
        finder_dict['FWHM'][band] *= uu.arcsec
    # ----------------------------------------------------------------------
    # max_pm should be in arcsec / yr
    finder_dict['MAX_PM'] *= uu.arcsec / uu.yr
    # scale bar should be in arcsec
    finder_dict['SCALE_SIZE'] *= uu.arcsec
    # push the directory into params
    params.set('ARI_FINDER', value=finder_dict, source=func_name)
    # return params
    return params


def create_finder_chart(params: ParamDict, objname: str,
                        it: int, object_table: pd.DataFrame):
    """
    Get all objects and push into finder chart one by one
    :return:
    """
    # print progress
    WLOG(params, '', 'Creating finder ')
    # get directory to save finder charts to
    directory = params['ARI_FINDER']['directory']
    # set up arguments
    args = [objname, it + 1, len(object_table)]
    # check whether file already exists
    abspath = os.path.join(directory, f'{objname}.pdf')
    if SKIP_DONE and os.path.exists(abspath):
        msg = 'Skipping finder for object: {0} [{1}/{2}]'
        WLOG(params, '', msg.format(*args))
        return
    # get the objdict
    objdict = from_apero_objtable(it, object_table)
    # print progress
    print('\n' + '=' * 50)
    msg = 'Running NIRPS finder for object: {0} [{1}/{2}]'
    print(msg.format(*args))
    print('=' * 50 + '\n')
    # run the main code
    make_finder_chart(params, objname, DATE, objdict=objdict,
                      directory=directory)


# =============================================================================
# Worker functions
# =============================================================================
def construct_savepath(directory: str, date: Time, objname: str) -> str:
    """
    Get the pdf savepath
    :param directory:
    :param date:
    :param objname:
    :return:
    """
    # strtime
    strtime = f'{date.datetime.year}_{date.datetime.month}'
    # create directory
    save_directory = os.path.join(directory, objname)
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
    # construct filename
    save_filename = f'APERO_finder_chart_{objname}_{strtime}.pdf'
    # construct absolute path
    abspath = os.path.join(save_directory, save_filename)
    # return the absolute path
    return abspath


def from_apero_objtable(it: int, object_table: pd.DataFrame) -> Dict[str, Any]:
    """
    Create a objdict for use in apero_finder_chart.main() from this row of the
    full object table

    :param it: int, the row of the table to create dictionary for
    :param object_table: astropy.Table, the full object database table

    :return: Dict, the objdict ofr use in apero_finder_chart.main()
    """
    # get the row from the object_table
    objdata = object_table.iloc[it]
    # set up the storage
    objdict = dict()
    # get the object name
    objdict['OBJNAME'] = objdata['OBJNAME']
    # get the object ra and dec
    objdict['RA_DEG'] = objdata['RA_DEG']
    objdict['DEC_DEG'] = objdata['DEC_DEG']
    # get the object epoch (jd)
    objdict['EPOCH'] = objdata['EPOCH']
    # get the object parallax
    objdict['PLX'] = objdata['PLX']
    # get the object proper motion
    objdict['PMRA'] = objdata['PMRA']
    objdict['PMDE'] = objdata['PMDE']
    # return the object dictionary
    return objdict


def make_finder_chart(params: ParamDict, objname: str, date: Time,
                      objdict: Dict[str, Any], directory: str):
    """
    Using an object name, an astropy time and a dictionary of the target
    object parameters create the finder chart for the object

    :param params: ParamDict, parameter dictionary of constants
    :param objname: str, the name of the object
    :param date: Time, the time of the observation
    :param objdict: Dict[str, Any], the dictionary of object parameters
    :param directory: Directory to save finding charts to

    Object dictionary must contain the following:
        - OBJNAME: str, the name of the object
        - RA_DEG: float, the right ascension of the object (degrees)
        - DEC_DEG: float, the declination of the object (degrees)
        - EPOCH: float, the epoch of the object (jd)
        - PLX: float, the parallax of the object (mas)
        - PMRA: float, the proper motion in right ascension (mas/yr)
        - PMDE: float, the proper motion in declination (mas/yr)

    """
    # get parameters from params
    radius = params['ARI_FINDER']['RADIUS']
    pixel_scale = params['ARI_FINDER']['PIXEL_SCALE']
    field_of_view = params['ARI_FINDER']['FIELD_OF_VIEW']
    sigma_limit = params['ARI_FINDER']['SIGMA_LIMIT']
    scale_factor = params['ARI_FINDER']['SCALE_FACTOR']
    fwhm = params['ARI_FINDER']['FWHM']
    transform_rotate = params['ARI_FINDER']['TRANSFORM_ROTATE']
    flip_x = params['ARI_FINDER']['FLIP_X']
    flip_y = params['ARI_FINDER']['FLIP_Y']

    print(f'Propagating coords to {date.iso}')
    obs_coords, obs_time = propagate_coords(objdict, date)
    # -------------------------------------------------------------------------
    # get all Gaia data around the current coordinates
    print('Getting Gaia sources for this region')
    # TODO: Deal with >2000 sources
    gaia_sources = get_gaia_sources(params, obs_coords, obs_time,
                                    radius=radius['G'])
    # -------------------------------------------------------------------------
    # Get the 2MASS source for each Gaia source
    print('Getting 2MASS sources for this region')
    # TODO: Deal with >2000 sources
    gaia_sources = get_2mass_sources(params, gaia_sources, obs_coords, obs_time,
                                     radius=radius['J'])
    # -------------------------------------------------------------------------
    # seed Gaia images
    # -------------------------------------------------------------------------
    kwargs_gaia = dict(pixel_scale=pixel_scale['G'], obs_coords=obs_coords,
                       fwhm=fwhm['G'], field_of_view=field_of_view['G'],
                       sigma_limit=sigma_limit['G'], band='G',
                       scale_factor=scale_factor['G'])
    print('\nSeeding Gaia image')
    image1, wcs1 = seed_image(gaia_sources,
                              flip_x=flip_x['G'], flip_y=flip_y['G'],
                              rotation=transform_rotate['G'].to(uu.deg),
                              **kwargs_gaia)

    print('\nSeeding Gaia image (no rotation)')
    image3, wcs3 = seed_image(gaia_sources, flip_x=False, flip_y=False,
                              rotation=0 * uu.deg, **kwargs_gaia)
    # -------------------------------------------------------------------------
    # seed 2MASS images
    # -------------------------------------------------------------------------
    kwargs_tmass = dict(pixel_scale=pixel_scale['J'], obs_coords=obs_coords,
                        fwhm=fwhm['J'], field_of_view=field_of_view['J'],
                        sigma_limit=sigma_limit['J'], band='J',
                        scale_factor=scale_factor['J'])
    print('\nSeeding 2MASS image')
    image2, wcs2 = seed_image(gaia_sources,
                              flip_x=flip_x['J'], flip_y=flip_y['J'],
                              rotation=transform_rotate['J'].to(uu.deg),
                              **kwargs_tmass)

    print('\nSeeding 2MASS image (no rotation)')
    image4, wcs4 = seed_image(gaia_sources, flip_x=False, flip_y=False,
                              rotation=0 * uu.deg, **kwargs_tmass)

    # -------------------------------------------------------------------------
    # plot figures
    # -------------------------------------------------------------------------
    fig1, frame1 = plt.subplots(ncols=1, nrows=1, figsize=(16, 16))
    fig2, frame2 = plt.subplots(ncols=1, nrows=1, figsize=(16, 16))
    fig3, frame3 = plt.subplots(ncols=1, nrows=1, figsize=(16, 16))
    fig4, frame4 = plt.subplots(ncols=1, nrows=1, figsize=(16, 16))
    # plot the gaia map
    # noinspection PyTypeChecker
    plot_map1(params, frame1, image1, wcs1, obs_coords,
              'Gaia', field_of_view['G'], pixel_scale['G'],
              scale_factor=scale_factor['G'])
    # plot the 2mass map
    # noinspection PyTypeChecker
    plot_map1(params, frame2, image2, wcs2, obs_coords,
              '2MASS', field_of_view['J'], pixel_scale['J'],
              scale_factor=scale_factor['J'])

    # noinspection PyTypeChecker
    plot_map1(params, frame3, image3, wcs3, obs_coords,
              'Gaia [No rotation]', field_of_view['G'],
              field_of_view['G'],
              scale_factor=field_of_view['G'])
    # plot the 2mass map
    # noinspection PyTypeChecker
    plot_map1(params, frame4, image4, wcs4, obs_coords,
              '2MASS [No rotation]', field_of_view['J'],
              pixel_scale['J'],
              scale_factor=scale_factor['J'])

    # -------------------------------------------------------------------------
    # add title
    # -------------------------------------------------------------------------
    # find the object closest to our source
    closest = np.argmin(gaia_sources['separation'])
    title = (f'Object: {objname}\n'
             f'Date: {obs_time.iso}   [{obs_time.jd}]\n'
             f'RA: {obs_coords.ra.to_string(uu.hourangle, sep=":")}   '
             f'Dec: {obs_coords.dec.to_string(uu.deg, sep=":")}   \n'
             f'Gmag: {gaia_sources["G"][closest]:.2f}   '
             f'Jmag: {gaia_sources["J"][closest]:.2f}   ')
    fig1.suptitle(title)
    fig2.suptitle(title)
    fig3.suptitle(title)
    fig4.suptitle(title)
    # construct absolute path
    abspath = construct_savepath(directory, date, objname)
    # write pdf pages
    with PdfPages(abspath) as pp:
        fig1.savefig(pp, format='pdf')
        fig2.savefig(pp, format='pdf')
        fig3.savefig(pp, format='pdf')
        fig4.savefig(pp, format='pdf')
    # close plot
    plt.close()


def propagate_coords(objdata: Dict[str, Any], obs_time: Time
                     ) -> Tuple[SkyCoord, Time]:
    # deal with distance
    if objdata['PLX'] <= 0:
        distance = None
    else:
        distance = Distance(parallax=objdata['PLX'] * uu.mas)
    # need to propagate ra and dec to J2000
    coords = SkyCoord(ra=objdata['RA_DEG'] * uu.deg,
                      dec=objdata['DEC_DEG'] * uu.deg,
                      distance=distance,
                      pm_ra_cosdec=objdata['PMRA'] * uu.mas / uu.yr,
                      pm_dec=objdata['PMDE'] * uu.mas / uu.yr,
                      obstime=Time(objdata['EPOCH'], format='jd'))
    # work out the delta time between epoch and J2000.0
    with warnings.catch_warnings(record=True) as _:
        jepoch = Time(objdata['EPOCH'], format='jd')
        delta_time = (obs_time.jd - jepoch.jd) * uu.day
    # get the coordinates
    with warnings.catch_warnings(record=True) as _:
        # center the image on the current coordinates
        curr_coords = coords.apply_space_motion(dt=delta_time)
        curr_time = obs_time
    # return some stuff
    return curr_coords, curr_time


# noinspection PyUnresolvedReferences
def setup_wcs(image_shape: Tuple[int, int], cent_coords: SkyCoord,
              pixel_scale: uu.Quantity, rotation: uu.Quantity,
              flip_x: bool, flip_y: bool) -> WCS:
    # need to set up a wcs
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
    # add a rotation
    wcs.wcs.pc = np.array([[np.cos(rotation), -np.sin(rotation)],
                           [np.sin(rotation), np.cos(rotation)]])

    return wcs


def get_gaia_sources(params: ParamDict, coords: SkyCoord, obstime: Time,
                     radius: uu.Quantity) -> Dict[str, List[float]]:
    # get parameters from params
    max_pm = params['ARI_FINDER']['MAX_PM']
    # get the gaia time
    gaia_time = Time(GAIA_EPOCH, format='decimalyear')
    # work out the delta time between epoch and J2000.0
    with warnings.catch_warnings(record=True) as _:
        delta_time_now = (obstime.jd - gaia_time.jd) * uu.day
    # modify radius to catch all sources
    search = abs(delta_time_now * max_pm).to(uu.deg)
    radius = radius.to(uu.deg) + search
    # -------------------------------------------------------------------------
    # define the gaia Tap instance
    gaia = TapPlus(url=GAIA_URL)

    gaia_query = GAIA_QUERY.format(ra=coords.ra.deg, dec=coords.dec.deg,
                                   radius=radius.to(uu.deg).value)
    # launch the query
    job = gaia.launch_job(gaia_query)
    # get the query results
    table = job.get_results()
    # delete job
    del job
    # deal with query being exactly 2000 (the max size)
    if len(table) == 2000:
        print('Too many sources. Launching job asyncronously. Please wait...')
        job = gaia.launch_job_async(gaia_query)
        # get the query results
        table = job.get_results()
        # delete job
        del job
    # -------------------------------------------------------------------------
    # storage for sources
    sources = dict()
    sources['gaia_id'] = []
    sources['ra'] = []
    sources['dec'] = []
    sources['G'] = []
    sources['Rp'] = []
    sources['Bp'] = []
    sources['J'] = []
    sources['H'] = []
    sources['K'] = []
    sources['ra_gaia'] = []
    sources['dec_gaia'] = []
    sources['pmra'] = []
    sources['pmdec'] = []
    sources['parallax'] = []
    sources['separation'] = []
    # get parallax mask
    parallax_mask = table['parallax'].mask
    # -------------------------------------------------------------------------
    # get all stars in the region where they would be now
    for row in range(len(table)):
        # get table row
        table_row = table[row]
        # deal with distances
        if parallax_mask[row]:
            distance = None
            plx = np.nan
        elif table_row['parallax'] <= 0:
            distance = None
            plx = np.nan
        else:
            plx = table_row['parallax']
            distance = Distance(parallax=plx * uu.mas)
        # need to propagate ra and dec to J2000
        gaia_coords = SkyCoord(ra=table_row['ra'] * uu.deg,
                               dec=table_row['dec'] * uu.deg,
                               distance=distance,
                               pm_ra_cosdec=table_row['pmra'] * uu.mas / uu.yr,
                               pm_dec=table_row['pmdec'] * uu.mas / uu.yr,
                               obstime=gaia_time, frame='icrs')
        # center the image on the current coordinates
        with warnings.catch_warnings(record=True) as _:
            curr_coords = gaia_coords.apply_space_motion(dt=delta_time_now)
        # work out the separation between this point and the center point
        separation = coords.separation(curr_coords)
        # add to sources
        sources['gaia_id'].append(table_row['source_id'])
        sources['ra'].append(curr_coords.ra.deg)
        sources['dec'].append(curr_coords.dec.deg)
        sources['G'].append(table_row['phot_g_mean_mag'])
        sources['Rp'].append(table_row['phot_rp_mean_mag'])
        sources['Bp'].append(table_row['phot_bp_mean_mag'])
        sources['J'].append(np.nan)
        sources['H'].append(np.nan)
        sources['K'].append(np.nan)
        sources['ra_gaia'].append(table_row['ra'])
        sources['dec_gaia'].append(table_row['dec'])
        sources['pmra'].append(table_row['pmra'])
        sources['pmdec'].append(table_row['pmdec'])
        sources['parallax'].append(plx)
        sources['separation'].append(separation.value)
    # -------------------------------------------------------------------------
    # convert all to numpy arrays
    sources['gaia_id'] = np.array(sources['gaia_id'])
    sources['ra'] = np.array(sources['ra'])
    sources['dec'] = np.array(sources['dec'])
    # warning is for the fact some columns are masked
    with warnings.catch_warnings(record=True) as _:
        sources['G'] = np.array(sources['G'])
        sources['Rp'] = np.array(sources['Rp'])
        sources['Bp'] = np.array(sources['Bp'])
        sources['J'] = np.array(sources['J'])
        sources['H'] = np.array(sources['H'])
        sources['K'] = np.array(sources['K'])
        sources['ra_gaia'] = np.array(sources['ra_gaia'])
        sources['dec_gaia'] = np.array(sources['dec_gaia'])
        sources['pmra'] = np.array(sources['pmra'])
        sources['pmdec'] = np.array(sources['pmdec'])
        sources['parallax'] = np.array(sources['parallax'])
        sources['separation'] = np.array(sources['separation'])
    # -------------------------------------------------------------------------
    return sources


def get_2mass_field(params: ParamDict, obs_coords: SkyCoord, obs_time: Time,
                    radius: uu.Quantity) -> Tuple[Time, Table]:
    """
    We don't know the epoch of the 2MASS data, so we need to get the epoch
    for the field

    :param params: ParamDict, parameter dictionary of constants
    :param obs_coords: SkyCoord, the coordinates of the observation
    :param obs_time: Time, the time of the observation
    :param radius: Quantity, the radius of the search (should be at least
                   field_of_view / sqrt(2) in size so full image is filled
                   with sources
    :return:
    """
    # get parameters from params
    max_pm = params['ARI_FINDER']['MAX_PM']
    # define the gaia Tap instance
    tmass = TapPlus(url=TMASS_URL)
    # get the 2MASS time
    tmass_time = Time(TMASS_EPOCH, format='decimalyear')
    # work out the delta time between 2mass and Gaia
    with warnings.catch_warnings(record=True) as _:
        delta_time_2mass = (tmass_time.jd - obs_time.jd) * uu.day
    # need to get the observation coords again (as a copy)
    obs_coords = SkyCoord(obs_coords)
    # get the 2mass coords at the 2mass epoch
    with warnings.catch_warnings(record=True) as _:
        tmass_coords = obs_coords.apply_space_motion(dt=delta_time_2mass)

    # modify radius to catch all sources
    search = abs(delta_time_2mass * max_pm).to(uu.deg)
    radius = radius.to(uu.deg) + search

    # get 2MASS query
    tmass_query = TMASS_QUERY.format(TMASS_COLS=TMASS_COLS,
                                     ra=tmass_coords.ra.deg,
                                     dec=tmass_coords.dec.deg,
                                     radius=radius.value)
    # launch the query
    job0 = tmass.launch_job(tmass_query)
    # get the query results
    table0 = job0.get_results()
    # delete job0
    del job0
    # deal with query being exactly 2000 (the max size)
    if len(table0) == 2000:
        print('Too many sources. Launching job asyncronously. Please wait...')
        job0 = tmass.launch_job_async(tmass_query)
        # get the query results
        table0 = job0.get_results()
        # delete job0
        del job0
    # -------------------------------------------------------------------------
    if len(table0) == 0:
        raise ValueError('No sources found in 2MASS catalog')
    else:
        for it, col in enumerate(TMASS_COLS.split(',')):
            table0[col] = table0[f'col_{it}']
            del table0[f'col_{it}']
    # get the mean date for field - we don't know when these ra and dec were
    # so we had to "guess" the date above
    mean_jdate = np.mean(table0['jdate'])
    # make this a time
    jdate_time = Time(mean_jdate, format='jd')
    return jdate_time, table0


def get_2mass_sources(params: ParamDict, gaia_sources: Dict[str, List[float]],
                      obs_coords: SkyCoord, obs_time: Time,
                      radius: uu.Quantity):
    """
    for each source in gaia sources cross match with the 2mass/Gaia catalog

    :param params: ParamDict, parameter dictionary of constants
    :param gaia_sources: Dict, the gaia sources
    :param obs_coords: SkyCoord, the coordinates of the observation
    :param obs_time: Time, the time of the observation
    :param radius: Quantity, the radius of the search (should be at least
                   field_of_view / sqrt(2) in size so full image is filled
                   with sources
    :return:
    """
    # get parameters from params
    sigma_limit = params['ARI_FINDER']['SIGMA_LIMIT']
    mag_limit = params['ARI_FINDER']['MAG_LIMIT']
    # get the mean jdate for the field
    jdate_time, tmass_table = get_2mass_field(params, obs_coords, obs_time,
                                              radius)
    # get all 2MASS coords
    tmass_coords = SkyCoord(ra=tmass_table['ra'], dec=tmass_table['dec'],
                            distance=None, pm_ra_cosdec=None, pm_dec=None,
                            obstime=jdate_time, frame='icrs')
    # get the gaia time
    gaia_time = Time(GAIA_EPOCH, format='decimalyear')

    # loop around objects
    for row in tqdm(range(len(gaia_sources['parallax']))):
        # deal with distances
        if np.isnan(gaia_sources['parallax'][row]):
            distance = None
        else:
            distance = Distance(parallax=gaia_sources['parallax'][row] * uu.mas)
        # need to get the gaia coords again
        gaia_coords = SkyCoord(ra=gaia_sources['ra_gaia'][row] * uu.deg,
                               dec=gaia_sources['dec_gaia'][row] * uu.deg,
                               distance=distance,
                               pm_ra_cosdec=gaia_sources['pmra'][row] * uu.mas / uu.yr,
                               pm_dec=gaia_sources['pmdec'][row] * uu.mas / uu.yr,
                               obstime=gaia_time, frame='icrs')
        # work out the delta time between 2mass and Gaia
        with warnings.catch_warnings(record=True) as _:
            delta_time_jdate = (jdate_time.jd - gaia_time.jd) * uu.day
        # get the 2mass coords at the 2mass epoch
        with warnings.catch_warnings(record=True) as _:
            jdate_coords = gaia_coords.apply_space_motion(dt=delta_time_jdate)

        # Need to find the closest sources in 2MASS to the jdate coords
        separation = jdate_coords.separation(tmass_coords)
        # find the closest source
        closest = np.argmin(separation)

        # if there is no match then we set the value to the sigma limit
        if separation[closest] > TMASS_RADIUS:
            jmag = sigma_limit['J'] + mag_limit
            hmag = sigma_limit['H'] + mag_limit
            kmag = sigma_limit['K'] + mag_limit
        else:
            # get the magnitudes
            jmag = tmass_table['j_m'][closest]
            hmag = tmass_table['h_m'][closest]
            kmag = tmass_table['k_m'][closest]

        gaia_sources['J'][row] = jmag
        gaia_sources['H'][row] = hmag
        gaia_sources['K'][row] = kmag

    return gaia_sources


def seed_image(gaia_sources, pixel_scale, obs_coords, fwhm, field_of_view,
               sigma_limit, band, rotation, flip_x, flip_y, scale_factor):
    """
    Create the image WCS and seed all gaia soirces for band at their co
    """
    # plot out to the scale factor
    field_of_view = field_of_view * scale_factor

    # number of pixels in each direction
    npixel_x = int(field_of_view[0].to(uu.deg) // (pixel_scale * uu.pixel).to(uu.deg))
    npixel_y = int(field_of_view[1].to(uu.deg) // (pixel_scale * uu.pixel).to(uu.deg))

    fwhm_pix = fwhm.to(uu.arcsec) / (pixel_scale * uu.pixel).to(uu.arcsec)

    wcs = setup_wcs((npixel_y, npixel_x), obs_coords, pixel_scale, rotation,
                    flip_x, flip_y)

    image = np.random.normal(size=(npixel_y, npixel_x), scale=1.0, loc=0)

    nsig_psf = np.array(10 ** ((sigma_limit - gaia_sources[band]) / 2.5))

    # convert all coords to pixel coords
    x_sources, y_sources = wcs.all_world2pix(gaia_sources['ra'],
                                             gaia_sources['dec'], 0)
    # create a grid of all pixels
    y, x = np.mgrid[0:npixel_y, 0:npixel_x]
    # get the width of the PSF from the fwhm
    ew = fwhm_pix.value / (2 * np.sqrt(2 * np.log(2)))
    # loop around all sources
    for i in tqdm(range(len(x_sources))):

        if np.isnan(nsig_psf[i]):
            continue

        xdiff0 = x - x_sources[i]
        ydiff0 = y - y_sources[i]

        xdiff = xdiff0 * np.cos(rotation) - ydiff0 * np.sin(rotation)
        ydiff = xdiff0 * np.sin(rotation) + ydiff0 * np.cos(rotation)
        # core of PSF
        exp1 = np.exp(-(xdiff ** 2 + ydiff ** 2) / (2 * ew ** 2))
        image += nsig_psf[i] * exp1
        # halo of PSF
        exp_halo = np.exp(-(xdiff ** 2 + ydiff ** 2) / (2 * (ew * 3) ** 2))
        image += nsig_psf[i] * exp_halo * 1e-3
        # # spike in y
        # exp_spike_y = np.exp(-np.abs(xdiff ** 2 + 0.1 * np.abs(ydiff) ** 2) / (2 * ew ** 2))
        # image += nsig_psf[i] * exp_spike_y * 1e-2
        # # spike in x
        # exp_spike_x = np.exp(-(0.1 * np.abs(xdiff) ** 2 + np.abs(ydiff) ** 2) / (2 * ew ** 2))
        # image += nsig_psf[i] * exp_spike_x * 1e-2

    # display with an arcsinh stretch
    image = np.arcsinh(image)

    # return the image and the wcs
    return image, wcs


def plot_map1(params: ParamDict, frame, image, wcs, obs_coords, title,
              field_of_view, pixel_scale, scale_factor):
    # get parameters from params
    compass_frac = params['ARI_FINDER']['COMPASS_FRAC']
    scale_size = params['ARI_FINDER']['SCALE_SIZE']
    pixel_scale_all = params['ARI_FINDER']['PIXEL_SCALE']
    # plot image
    frame.imshow(image, origin='lower', vmin=np.arcsinh(-3),
                 vmax=np.arcsinh(200),
                 cmap='gist_heat', interpolation='nearest')
    # pick a color for the annotations
    color = 'cyan'
    # -------------------------------------------------------------------------
    # plot trail
    # -------------------------------------------------------------------------
    # x_all_pix, y_all_pix = wcs.all_world2pix(all_coords.ra.value,
    #                                          all_coords.dec.value, 0)
    #
    # extent = [0, image.shape[0], 0, image.shape[1]]
    # dx = extent[1] - extent[0]
    # dy = extent[3] - extent[2]
    # # plot the year labels
    # for it, coord in enumerate(all_coords):
    #     # check whether text is out of bounds
    #     if out_of_bounds(extent, x_all_pix[it], y_all_pix[it]):
    #         continue
    #
    #     # text is offset by 1% of the ra range
    #     frame.text(float(x_all_pix[it] + 0.05 * dx),
    #                float(y_all_pix[it] + 0.05 * dy),
    #                f'{all_times[it].decimalyear:.1f}', color='yellow',
    #                alpha=0.5,
    #                horizontalalignment='left', verticalalignment='center')
    #
    #     frame.plot(x_all_pix[it], y_all_pix[it], color='y', ms=10, marker='+',
    #                ls='None', alpha=0.5)

    # -------------------------------------------------------------------------
    # plot current position
    # -------------------------------------------------------------------------
    x_curr_pix, y_curr_pix = wcs.all_world2pix(obs_coords.ra.value,
                                               obs_coords.dec.value, 0)

    frame.plot(x_curr_pix, y_curr_pix, marker='o',
               color=color, ms=30, mfc='none')
    frame.plot(x_curr_pix, y_curr_pix, marker='+',
               color=color, ms=30, mfc='none')
    # -------------------------------------------------------------------------
    # plot compass
    # -------------------------------------------------------------------------
    x_comp0 = 0.9 * image.shape[0]
    y_comp0 = 0.1 * image.shape[0]
    # convert compass center to ra/dec from pixel space
    ra_comp, dec_comp = wcs.all_pix2world(x_comp0, y_comp0, 0)
    # get the cos(dec) term
    cos_dec = np.cos(dec_comp * uu.deg)
    # get the compas
    length_world = field_of_view * scale_factor
    ra_comp_e = ra_comp + (length_world[0].to(uu.deg).value * compass_frac) / cos_dec
    dec_comp_n = dec_comp + length_world[1].to(uu.deg).value * compass_frac
    # convert back to pixel space
    x_comp, y_comp = wcs.all_world2pix(ra_comp, dec_comp, 0)
    x_comp_e, y_comp_e = wcs.all_world2pix(ra_comp_e, dec_comp, 0)
    x_comp_n, y_comp_n = wcs.all_world2pix(ra_comp, dec_comp_n, 0)
    # plot the compass
    kwargs = dict(ha='center', va='center', color=color,
                  arrowprops=dict(arrowstyle='<-', color=color,
                                  shrinkA=0.0, shrinkB=0.0))
    frame.annotate('N', (x_comp, y_comp), (x_comp_n, y_comp_n), **kwargs)
    frame.annotate('E', (x_comp, y_comp), (x_comp_e, y_comp_e), **kwargs)

    # -------------------------------------------------------------------------
    # plot scale bar
    # -------------------------------------------------------------------------
    # get the length of the scale in pixels
    length = (scale_size / pixel_scale_all['G']).value

    x_scale_px = 0.1 * image.shape[0]
    y_scale_px = 0.1 * image.shape[1]
    x_stext_px = 0.1 * image.shape[0] + 0.5 * length
    y_stext_px = 0.1 * image.shape[1]

    patch = FancyArrowPatch((x_scale_px, y_scale_px),
                            (x_scale_px + length, y_scale_px),
                            arrowstyle='-', shrinkA=0.0, shrinkB=0.0,
                            capstyle='round', color=color, linewidth=2)
    frame.text(x_stext_px, y_stext_px,
               f'{scale_size.value:g} {scale_size.unit:unicode}',
               ha='center', va='bottom', color=color)
    frame.add_patch(patch)

    # -------------------------------------------------------------------------
    # remove ticks
    # -------------------------------------------------------------------------
    frame.set_xticks([])
    frame.set_yticks([])

    # -------------------------------------------------------------------------
    # Add rectangle for the real field of view
    # -------------------------------------------------------------------------
    # number of pixels in each direction
    npixel_x = int(field_of_view[0].to(uu.deg) // (pixel_scale * uu.pixel).to(uu.deg))
    npixel_y = int(field_of_view[1].to(uu.deg) // (pixel_scale * uu.pixel).to(uu.deg))
    # the recetangle should be centered on the center of the image
    center_x, center_y = image.shape[1] // 2, image.shape[0] // 2
    # we need to bottom left corner of the rectangle
    x0, y0 = center_x - npixel_x // 2, center_y - npixel_y // 2
    # plot a rectangle
    rect = Rectangle((x0, y0), npixel_x, npixel_y, linewidth=2, edgecolor=color,
                     facecolor='none', ls='--')
    frame.add_patch(rect)

    # -------------------------------------------------------------------------
    # add title
    # -------------------------------------------------------------------------
    frame.set_title(title, y=1.0, pad=-14, color=color)


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
