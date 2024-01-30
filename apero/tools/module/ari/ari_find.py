#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-01-30 at 14:01

@author: cook
"""
import os

from astropy.time import Time

from apero.core import constants
from apero.core.core import drs_database
from apero.core.core import drs_log
from apero.core.utils import drs_startup

# =============================================================================
# Define variables
# =============================================================================
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


def make_finder_chart(objname: str, date: Time, objdict: Dict[str, Any],
                      directory: str):
    """
    Using an object name, an astropy time and a dictionary of the target
    object parameters create the finder chart for the object

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
    print(f'Propagating coords to {date.iso}')
    obs_coords, obs_time = propagate_coords(objdict, date)
    # -------------------------------------------------------------------------
    # get all Gaia data around the current coordinates
    print('Getting Gaia sources for this region')
    # TODO: Deal with >2000 sources
    gaia_sources = get_gaia_sources(obs_coords, obs_time,
                                    radius=RADIUS['G'])
    # -------------------------------------------------------------------------
    # Get the 2MASS source for each Gaia source
    print('Getting 2MASS sources for this region')
    # TODO: Deal with >2000 sources
    gaia_sources = get_2mass_sources(gaia_sources, obs_coords, obs_time,
                                     radius=RADIUS['J'])
    # -------------------------------------------------------------------------
    # seed Gaia images
    # -------------------------------------------------------------------------
    kwargs_gaia = dict(pixel_scale=PIXEL_SCALE['G'], obs_coords=obs_coords,
                       fwhm=FWHM['G'], field_of_view=FIELD_OF_VIEW['G'],
                       sigma_limit=SIGMA_LIMIT['G'], band='G',
                       scale_factor=SCALE_FACTOR['G'])
    print('\nSeeding Gaia image')
    image1, wcs1 = seed_image(gaia_sources,
                              flip_x=FLIP_X['G'], flip_y=FLIP_Y['G'],
                              rotation=TRANSFORM_ROTATE['G'].to(uu.deg),
                              **kwargs_gaia)

    print('\nSeeding Gaia image (no rotation)')
    image3, wcs3 = seed_image(gaia_sources, flip_x=False, flip_y=False,
                              rotation=0 * uu.deg, **kwargs_gaia)
    # -------------------------------------------------------------------------
    # seed 2MASS images
    # -------------------------------------------------------------------------
    kwargs_tmass = dict(pixel_scale=PIXEL_SCALE['J'], obs_coords=obs_coords,
                        fwhm=FWHM['J'], field_of_view=FIELD_OF_VIEW['J'],
                        sigma_limit=SIGMA_LIMIT['J'], band='J',
                        scale_factor=SCALE_FACTOR['J'])
    print('\nSeeding 2MASS image')
    image2, wcs2 = seed_image(gaia_sources,
                              flip_x=FLIP_X['J'], flip_y=FLIP_Y['J'],
                              rotation=TRANSFORM_ROTATE['J'].to(uu.deg),
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
    plot_map1(frame1, image1, wcs1, obs_coords,
              'Gaia', FIELD_OF_VIEW['G'], PIXEL_SCALE['G'],
              scale_factor=SCALE_FACTOR['G'])
    # plot the 2mass map
    # noinspection PyTypeChecker
    plot_map1(frame2, image2, wcs2, obs_coords,
              '2MASS', FIELD_OF_VIEW['J'], PIXEL_SCALE['J'],
              scale_factor=SCALE_FACTOR['J'])

    # noinspection PyTypeChecker
    plot_map1(frame3, image3, wcs3, obs_coords,
              'Gaia [No rotation]', FIELD_OF_VIEW['G'],
              PIXEL_SCALE['G'],
              scale_factor=SCALE_FACTOR['G'])
    # plot the 2mass map
    # noinspection PyTypeChecker
    plot_map1(frame4, image4, wcs4, obs_coords,
              '2MASS [No rotation]', FIELD_OF_VIEW['J'],
              PIXEL_SCALE['J'],
              scale_factor=SCALE_FACTOR['J'])

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




def main(params: ParamDict, objname: str):
    """
    Get all objects and push into finder chart one by one
    :return:
    """
    # print progress
    print('Getting objects from database')
    # get directory to save finder charts to
    directory = os.path.join(params['DRS_DATA_OTHER', 'ari'])
    # load object database
    objdbm = drs_database.AstrometricDatabase(params)
    objdbm.load_db()
    # start condition
    condition = 'OBJNAME={objname}'
    # get all objects
    object_table = objdbm.get_entries('*', condition=condition)
    # loop around objnames
    for it, objname in enumerate(object_table['OBJNAME']):
        # args for printout
        args = [objname, it + 1, len(object_table)]
        # check whether file already exists
        abspath = construct_savepath(directory, DATE, objname)
        if SKIP_DONE and os.path.exists(abspath):
            msg = 'Skipping NIRPS finder for object: {0} [{1}/{2}]'
            print(msg.format(*args))
            continue
        # get the objdict
        objdict = from_apero_objtable(it, object_table)
        # print progress
        print('\n' + '=' * 50)
        msg = 'Running NIRPS finder for object: {0} [{1}/{2}]'
        print(msg.format(*args))
        print('=' * 50 + '\n')
        # run the main code
        make_finder_chart(objname, DATE, objdict=objdict, directory=directory)


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
