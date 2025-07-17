#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 2025-06-02 at 08:50

@author: artigau

===============================================================================
Code Steps (matches main code steps):
===============================================================================
    1. Change to working directory.
    2. Load and filter the Uranium-Neon line catalog.
    3. Deduplicate lines, keeping only the brightest within 20 km/s.
    4. Define function to get approximate wavelength for an order.
    5. Load hollow cathode (HC) and Fabry-Perot (FP) spectra.
    6. Prepare order list (start from middle order and alternate outwards).
    7. Initialize cavity fit and bookkeeping arrays.
    8. If enough previous solutions exist, robustly fit the cavity using all orders.
    9. Check for integer offset in cavity numbering and correct if needed.
    10. Fill missing values and robustly filter orders for cavity fit.
    11. Final robust fit to the cavity using all FP data and user validation.
    12. Main loop over orders to build wavelength solution:
        a. Extract 1D spectrum for this order.
        b. Find the NLINES brightest HC lines in this order.
        c. Find Fabry-Perot peaks for this order.
        d. Estimate the step between FP peaks and fit a polynomial to it.
        e. Normalize the step size to integer multiples of the fit.
        f. Assign a running index to each FP peak (cavity order).
        g. Remove outliers in the FP peak sequence.
        h. Create a synthetic spectrum with spikes at the HC line positions.
        i. Get the approximate wavelength range for this order.
        j. Estimate the range of possible FP cavity orders for this order.
        k. Try all possible FP cavity order guesses and find the best alignment.
        l. Normalize the nvalid2 array for plotting.
        m. Plot the results and ask the user for validation.
        n. If user accepts, save the wavelength solution and pickle.
    13. Build the final 2D wavelength solution for all orders:
        a. For each order, fit a Chebyshev polynomial to the wavelength solution.
        b. Smooth the Chebyshev coefficients across orders to remove outliers.
        c. For each order, compute the final wavelength solution and store coefficients in header.
    14. Save the final wavelength solution to a FITS file.
    15. Save the cavity fit coefficients to a file.
    16. Plot the final wavelength solution for all orders.
===============================================================================
"""
import os
from typing import Dict, Any
import numpy as np

from astropy.table import Table
from astropy import units as uu
from astropy import constants as cc
from astroquery.vizier import Vizier

from aperocore.core import drs_log
from aperocore.constants import param_functions

from apero.base import base as apero_base
from apero.utils import drs_data
from apero.tools.module.static import drs_static


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tools.module.static.static_wavelength.py'
__INSTRUMENT__ = 'None'
# Get version and author
__PACKAGE__ = apero_base.__PACKAGE__
__version__ = apero_base.__version__
__authors__ = apero_base.__authors__
__date__ = apero_base.__date__
__release__ = apero_base.__release__
# get param dict
ParamDict = param_functions.ParamDict
# Get Logging function
WLOG = drs_log.wlog
# get exceptions
AperoCodedException = drs_log.AperoCodedException
# Speed of light
# noinspection PyUnresolvedReferences
speed_of_light_ms = cc.c.to(uu.m / uu.s).value
# noinspection PyUnresolvedReferences
speed_of_light = cc.c.to(uu.km / uu.s).value
# TODO:
#    1.  Fill in + test this code
#    2.  Remove REF_LEAK from usage
#    3.  Get wave guess from assets
#    4.  Add HC update part (from apero-utils.updates_to_drs.apero_Static_tools.hollow_cathode_update.py
#    5.  remove "reset" directory from assets (move assets/reset/runs to assets/runs)
#    6.  when resetting copy assets/runs to runs


# =============================================================================
# Define functions
# =============================================================================
def main(params: ParamDict, recipe, sparams: Dict[str, Any]):
    # -------------------------------------------------------------------------
    # sort out detector path (this is where we are saving things to)
    cal_path = str(os.path.join(params['PATH.ASSETS'],
                                params['TOOLS.STATIC.CAL_PATH']))
    if not os.path.exists(cal_path):
        os.makedirs(cal_path)
    # -------------------------------------------------------------------------
    # Step 1: Create HC catalogue
    # -------------------------------------------------------------------------
    if sparams['wavelength']['run_generate_hc_catalogue']:
        generate_hc_catagloue(params, recipe, sparams, cal_path)

    # -------------------------------------------------------------------------
    # Step 2: Run reduction for given night
    # -------------------------------------------------------------------------
    if sparams['wavelength']['run_generate_night']:
        generate_night(params, recipe, sparams)

    # -------------------------------------------------------------------------
    # Step 3: Extract HC and FP
    # -------------------------------------------------------------------------
    if sparams['wavelength']['run_generate_wave_guess']:
        generate_wave_guess(params, recipe, sparams, cal_path)

    # -------------------------------------------------------------------------
    # Update repo
    # -------------------------------------------------------------------------
    drs_static.update_repo(params, recipe, save_path=cal_path)


def generate_hc_catagloue(params: ParamDict, recipe, sparams: Dict[str, Any],
                          cal_path: str):
    # get the wavelength sparams for input hc cat
    wparams = sparams['waelength']['input_hc_cat']
    # download the hc model
    hc_model = get_hc_model(params, sparams)
    # only keep lines
    hc_table = get_hc_lines(params, recipe, sparams, hc_model)
    # -------------------------------------------------------------------------
    # remove duplicated lines (keep brightest within certain velocity range)
    # -------------------------------------------------------------------------
    # get the hc window
    hc_window = wparams['window_size']
    # get the vectors for convience
    wavemap = hc_table['wavemap']
    flux = hc_table['wavemap']
    # lines to keep
    keep = np.zeros_like(wavemap, dtype=bool)
    # loop around table
    for it in range(len(hc_table)):
        # work out the velocity of every line compared to this iteration
        dv = (1 - wavemap[it]/wavemap) * speed_of_light
        # find all lines within our velocity window
        good = np.abs(dv) < hc_window
        # if the flux of this peak is the max in itself velocity window keep it
        if flux[it] == np.nanmax(flux[good]):
            keep[it] = True
    # cut down out hc_table
    hc_table = hc_table[keep]
    # -------------------------------------------------------------------------
    # get static file
    static_file = recipe.outputs['STATIC_HC_CAT'].newcopy(params=params)
    # construct the filename from file instance
    static_file.construct_filename(path=cal_path)
    # save static file
    drs_static.save_static_file(params, recipe, static_file,
                                desc='hotpix', data_list=[hc_table])


def generate_night(params: ParamDict, recipe, sparams: Dict[str, Any]):
    # TODO: How do you generate a night without a wavelength solution?
    # TODO: How do we do this without adding to the database?

    # step 1: preprocess

    # step 2: dark ref

    # step 3: bad ref

    # step 4: locrefsci

    # step 5: extract (no shape/no flat/no thermal, just one fiber)


    pass


def generate_wave_guess(params: ParamDict, recipe, sparams: Dict[str, Any],
                        cal_path: str):

    # get static hc e2ds file
    hc_file = recipe.outputs['STATIC_HC_E2DS'].newcopy(params=params)
    # construct the filename from file instance
    hc_file.construct_filename(path=cal_path)
    # load the hc file
    hc_image = hc_file.hdulist_load('HC_E2DS')

    # get static fp e2ds file
    fp_file = recipe.outputs['STATIC_FP_E2DS'].newcopy(params=params)
    # construct the filename from file instance
    fp_file.construct_filename(path=cal_path)
    # load the hc file
    fp_image = fp_file.hdulist_load('FP_E2DS')

    # get static file
    hc_cat_file = recipe.outputs['STATIC_HC_CAT'].newcopy(params=params)
    # construct the filename from file instance
    hc_cat_file.construct_filename(path=cal_path)
    # load the hc catalogue
    hc_cat_table = hc_cat_file.hdulist_load('HC_CAT')


    # get the number of orders
    norders, nxpix = hc_image.shape

    # get the orders starting from the middle and alternating outwards
    orders = np.arange(norders)
    orders = orders[np.argsort(np.abs(orders - (norders / 2)))]





    pass



# =============================================================================
# Define worker functions
# =============================================================================
def get_hc_model(params: ParamDict, sparams: Dict[str, Any]) -> Table:
    """
    Get the HC mode using the wavelength.input_hc_cat.vizier-ref keyword
    from Vizier and save to input + wavelength.input_hc_cat.filename

    :param params: ParamDict, parameter dictionary of constants
    :param sparams: dict, parameters from yaml file
    """
    # get the wavelength sparams for input hc cat
    wparams = sparams['wavelength']['input_hc_cat']
    # get the vizier reference
    vizier_ref = wparams['vizier-ref']
    # construct the name for the downloaded hc model
    hc_model_file = os.path.join(sparams['inpath'], wparams['filename'])
    # -------------------------------------------------------------------------
    # if we already have the file don't download again
    if os.path.exists(hc_model_file):
        return Table.read(hc_model_file)
    # -------------------------------------------------------------------------
    # deal with vizier-ref being a file on disk
    if os.path.exists(vizier_ref):
        table = Table.read(vizier_ref)
    else:
        # No row limit: get all rows
        Vizier.ROW_LIMIT = -1
        # Query the entire table
        try:
            tables = Vizier.get_catalogs(vizier_ref)
            # get the first table
            table = tables[0]
        except Exception as e:
            # TODO: Move to language database
            emsg = 'Failed to load model: {0} from Vizier\n\t{1}: {2}'
            eargs = [vizier_ref, type(e), str(e)]
            # raise an APERO exception
            raise AperoCodedException(params, None, message=emsg.format(*eargs),
                                      targs=eargs)
    # -------------------------------------------------------------------------
    # try to save the HC model to file
    try:
        # print that we are writing hc model file
        msg = 'Saving HC model file to: {0}'
        margs = [hc_model_file]
        WLOG(params, '', msg.format(*margs))
        # write to file
        table.write(hc_model_file, overwrite=True)
        # return tables[0]
        return table
    except Exception as e:
        # TODO: Move to language database
        emsg = 'Failed to save model: {0} to: {1}\n\t{2}: {3}'
        eargs = [vizier_ref, hc_model_file, (e), str(e)]
        # raise an APERO exception
        raise AperoCodedException(params, None, message=emsg.format(*eargs),
                                  targs=eargs)


def get_hc_lines(params: ParamDict, recipe, sparams: Dict[str, Any],
                 table: Table) -> Table:
    """
    Cut down the HC model to only keep species and wavelength we are
    interested in.

    :param params: ParamDict, parameter dictionary of constants
    :param sparams: dict, parameters from yaml file
    :param table: Table, table containing HC model

    :return: Table, table containing the cut down HC model for lines we
             are interested in
    """
    # get the wavelength sparams for input hc cat
    wparams = sparams['wavelength']['input_hc_cat']
    # get the required wavelength domain
    wavemin, wavemax = wparams['wave_domain']
    # get the species we want
    species_keep = wparams['species_keep']
    # get the species column
    hc_species_col = wparams['species_col']
    # get the flux column
    hc_flux_col = wparams['hc_flux_col']
    # get the wavelength column
    hc_wave_col = wparams['wave_col']
    # get wavelength units and convert to astropy unit
    hc_wave_unit = wparams['wave_units']
    # get the vizier reference
    vizier_ref = wparams['vizier-ref']
    # -------------------------------------------------------------------------
    try:
        wave_unit = uu.Unit(hc_wave_unit)
    except Exception as e:
        emsg = 'wavelength.input_hc_Cat.wave_units={0} invalid.\n\t{1}: {2}'
        eargs = [hc_wave_unit, type(e), str(e)]
        raise AperoCodedException(params, None, message=emsg.format(*eargs),
                                  targs=eargs)
    # make sure wavelength is in nm
    try:
        wavemap = ((table[hc_wave_col] * wave_unit).to(uu.nm)).value
    except Exception as e:
        # TODO: Add to language database
        emsg = ('wavelength.input_hc_Cat.wave_units={0} [astropy={1}] invalid.'
                '\n\t{2}: {3}')
        eargs = [hc_wave_unit, str(wave_unit), type(e), str(e)]
        raise AperoCodedException(params, None, message=emsg.format(*eargs),
                                  targs=eargs)
    # -------------------------------------------------------------------------
    # assume we don't want any lines at first
    smask = np.zeros_like(len(table))
    # loop around species to keep from hc model
    for species in species_keep:
        # get a mask just for this species
        sp_mask = table[hc_species_col] == species
        # get wavelength constraints
        sp_mask &= wavemap > wavemin
        sp_mask &= wavemap < wavemax
        # combine to full mask
        smask |= sp_mask
    # deal with no lines
    if np.sum(smask) == 0:
        # TODO: Add to language database
        emsg = ('No lines left in HC model after cut\n\tSpecies: {0}'
                '\n\tWavemin: {1} nm\n\tWavemax: {2} nm')
        eargs = [','.join(species_keep), wavemin, wavemax]
        raise AperoCodedException(params, None, message=emsg.format(*eargs),
                                  targs=eargs)
    else:
        # get static file
        hccat = recipe.outputs['STATIC_HC_CAT'].newcopy(params=params)
        stbl = hccat.hdulist['HC_CAT']
        # lets make a new table, cut down to smask, and cleaned ready for use
        outtable = stbl.create_table(wavelength=wavemap[smask],
                                     flux=table[hc_flux_col][smask],
                                     species=table[hc_species_col][smask],
                                     source=[vizier_ref] * np.sum(smask))
        # return the new, cleaned, cut down table
        return outtable


def get_approx_wavesol(sparams: Dict[str, Any], order_num: int,
                       norders: int) -> Tuple[float, float, float]:
    """
    Calculate a very rough approximation of the wave solution
    (center and start and end) for an order - based on a linear fit
    in wavenumber

    :param sparams: dict, parameters from yaml file
    :param order_num: int, order of approximation
    :param norders: int, number of orders in total

    :return: Tuple, Guess for this order: 1. wave center, 2. start, 3. end
    """
    # get the wavelength sparams for input hc cat
    wparams = sparams['wavelength']['input_hc_cat']
    # get the required wavelength domain
    wavemin, wavemax = wparams['wave_domain']
    # get the fractional range for approximate wavelength
    wave_approx = wparams['wave_approx']

    # linear fit across orders in wavenumber
    lfit = np.polyfit([0, norders], [1/wavemin, 1/wavemax], 1)
    # the wave guess it the inverse of this fit in wavenumber
    waveguess = 1 / np.polyval(lfit, order_num)
    # start and end points given the wave_approx size (and waveguess as center)
    wavestart = waveguess * (1 - wave_approx)
    waveend = waveguess * (1 + wave_approx)

    return waveguess, wavestart, waveend


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
