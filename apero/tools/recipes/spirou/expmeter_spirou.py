#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2020-02-28 at 16:47

@author: cook
"""
import numpy as np
import os
import warnings

from apero import core
from apero import locale
from apero.core import constants
from apero.io import drs_fits
from apero.core import math as mp
from apero.science.calib import shape
from apero.science.calib import wave
from apero.science import telluric
from apero.tools.module.testing import drs_dev
from apero.tools.module.utils import inverse

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'expmeter_spirou.py'
__INSTRUMENT__ = 'SPIROU'
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# get param dict
ParamDict = constants.ParamDict
# Get Logging function
WLOG = core.wlog
# Get the text types
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict
Help = locale.drs_text.HelpDict(__INSTRUMENT__, Constants['LANGUAGE'])
# -----------------------------------------------------------------------------
# set up recipe definitions (overwrites default one)
RMOD = drs_dev.RecipeDefinition(instrument=__INSTRUMENT__)
# define a recipe for this tool
exposuremeter = drs_dev.TmpRecipe()
exposuremeter.name = __NAME__
exposuremeter.shortname = 'EXPMTR'
exposuremeter.instrument = __INSTRUMENT__
exposuremeter.outputdir = 'reduced'
exposuremeter.inputdir = 'tmp'
exposuremeter.inputtype = 'tmp'
exposuremeter.extension = 'fits'
exposuremeter.description = 'Produces an exposuremeter map'
exposuremeter.kind = 'misc'
exposuremeter.set_arg(pos=0, name='directory', dtype='directory',
                      helpstr=Help['DIRECTORY_HELP'])

# add recipe to recipe definition
RMOD.add(exposuremeter)
# header keys
EM_MIN_WAVE = ('EM_MNWAV', 0.0, 'Exposure meter min wave for mask')
EM_MAX_WAVE = ('EM_MXWAV', 0.0, 'Exposure meter max wave for mask')
EM_TELL_THRES = ('EM_TLIM', 0.0, 'Exposure meter telluric threshold for mask')


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
# Everything else is controlled from recipe_definition
def main(directory=None, **kwargs):
    """
    Main function for exposuremeter_spirou.py

    :param kwargs: additional keyword arguments

    :type instrument: str

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(directory=directory, **kwargs)
    # ----------------------------------------------------------------------
    # deal with command line inputs / function call inputs
    recipe, params = core.setup(__NAME__, __INSTRUMENT__, fkwargs,
                                rmod=RMOD)
    # solid debug mode option
    if kwargs.get('DEBUG0000', False):
        return recipe, params
    # ----------------------------------------------------------------------
    # run main bulk of code (catching all errors)
    llmain, success = core.run(__main__, recipe, params)
    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    return core.end_main(params, llmain, recipe, success)


def __main__(recipe, params):
    """
    Main code: should only call recipe and params (defined from main)

    :param recipe:
    :param params:
    :return:
    """
    # ----------------------------------------------------------------------
    # Main Code
    # ----------------------------------------------------------------------
    mainname = __NAME__ + '._main()'
    # define file type
    filetype = 'WAVE_NIGHT'
    # get pseudo constants
    pconst = constants.pload(params['INSTRUMENT'])
    # get fibers
    fibers = pconst.INDIVIDUAL_FIBERS()

    # ----------------------------------------------------------------------
    # Get the wave image
    # ----------------------------------------------------------------------
    # storage for wave images
    wave_images = dict()
    wave_infiles = dict()

    # log progress
    WLOG(params, '', 'Gettings wave files')
    # loop around fibers
    for fiber in fibers:
        # print fibers
        WLOG(params, '', '\tFiber {0}'.format(fiber))
        # find file instance in set (verify user input)
        drsfile = core.get_file_definition(filetype, params['INSTRUMENT'],
                                           kind='red')
        # get all "filetype" filenames
        files = drs_fits.find_files(params, recipe, kind='red',
                                    KW_OUTPUT=filetype, fiber=fiber,
                                    night=params['NIGHTNAME'])
        # deal with no files found
        if len(files) == 0:
            eargs = [filetype, fiber, mainname]
            emsg = 'No files found for {0} (fiber = {1}) \n\t Function = {2}'
            WLOG(params, 'error', emsg.format(*eargs))
        # make a new copy of infile
        infile = drsfile.newcopy(filename=files[-1], recipe=recipe)
        # read file
        infile.read_file()
        # append to storage
        wave_images[fiber] = infile.data
        wave_infiles[fiber] = infile

    # ----------------------------------------------------------------------
    # Get the telluric image
    # ----------------------------------------------------------------------
    # storage for tellu images
    tellu_images = dict()

    for fiber in fibers:
        # wave infile
        header = wave_infiles[fiber].header
        ishape = wave_images[fiber].shape
        # ------------------------------------------------------------------
        # load wavelength solution for this fiber
        wprops = wave.get_wavesolution(params, recipe,
                                       filename=wave_infiles[fiber].filename)
        # ------------------------------------------------------------------
        # Load the TAPAS atmospheric transmission convolved with the
        #   master wave solution (1D spectrum)
        # ------------------------------------------------------------------
        largs = [header, wprops, fiber]
        tapas_props = telluric.load_conv_tapas(params, recipe, *largs)
        # get the combined tapas absorption
        tapas_comb = tapas_props['TAPAS_ALL_SPECIES'][0].reshape(ishape)
        # add to storage
        tellu_images[fiber] = tapas_comb

    # ----------------------------------------------------------------------
    # Get and prepare shape and position images
    # ----------------------------------------------------------------------
    # get ref image
    ref_infile = wave_infiles[fibers[0]]
    ref_header = ref_infile.header
    # get image shape
    ishape = inverse.drs_image_shape(params)

    # get the x and y position images
    yimage, ximage = np.indices(ishape)
    # get shape files
    shapexfile, shapex = shape.get_shapex(params, ref_header)
    shapeyfile, shapey = shape.get_shapey(params, ref_header)
    # transform the shapex map
    WLOG(params, '', 'Transforming shapex map')
    shapex2 = shape.ea_transform(params, shapex, dymap=-shapey)

    # ----------------------------------------------------------------------
    # Get localisation for all fibers
    # ----------------------------------------------------------------------
    # print progress
    WLOG(params, '', 'Loading localisation')
    # storage
    centers, widths = dict(), dict()
    # loop around fibers
    for fiber in fibers:
        # wave infile
        header = wave_infiles[fiber].header
        # get the localisation parameters for this fiber
        WLOG(params, '', '\t Getting localisation for Fiber={0}'.format(fiber))
        cents, wids = inverse.calc_central_localisation(params, recipe, fiber,
                                                        header=header)
        # add to storage
        centers[fiber] = cents
        widths[fiber] = wids

    # ----------------------------------------------------------------------
    # Prepare simage for wave map (straight image)
    # ----------------------------------------------------------------------
    # set simage to None
    swave_map = None
    # log progress
    WLOG(params, '', 'Calculating straight image for wave map')
    # loop around fibers
    for fiber in fibers:
        # wave infile
        header = wave_infiles[fiber].header
        # get the localisation parameters for this fiber
        cents, wids = centers[fiber], widths[fiber]
        # get straighted wave image
        WLOG(params, '', '\t Adding flux (Fiber={0})'.format(fiber))
        swave_map =  inverse.e2ds_to_simage(wave_images[fiber], ximage, yimage,
                                            cents, wids, fill=np.nan,
                                            simage=swave_map)

    # ----------------------------------------------------------------------
    # Prepare simage for tellu map (straight image)
    # ----------------------------------------------------------------------
    # set simage to None
    stellu_map = None
    # log progress
    WLOG(params, '', 'Calculating straight image for wave map')
    # loop around fibers
    for fiber in fibers:
        # wave infile
        header = wave_infiles[fiber].header
        # get the localisation parameters for this fiber
        cents, wids = centers[fiber], widths[fiber]
        # get straighted wave image
        WLOG(params, '', '\t Adding flux (Fiber={0})'.format(fiber))
        stellu_map = inverse.e2ds_to_simage(tellu_images[fiber], ximage,
                                            yimage, cents, wids, fill=np.nan,
                                            simage=stellu_map)

    # ----------------------------------------------------------------------
    # Prepare drs images (de-straightened image)
    # ----------------------------------------------------------------------
    # for wave image
    WLOG(params, '', 'De-straightening wave image')
    pwave_map = inverse.simage_to_drs(params, swave_map, shapex2, shapey)
    # for tellu image
    WLOG(params, '', 'De-straightening tellu image')
    ptellu_map = inverse.simage_to_drs(params, stellu_map, shapex2, shapey)

    # ----------------------------------------------------------------------
    # Make the exposure time mask
    # ----------------------------------------------------------------------
    # get limits for the mask
    # TODO: move to constants
    min_lambda = params['EXPMETER_MIN_LAMBDA'] = 1478.7
    max_lambda = params['EXPMETER_MAX_LAMBDA'] = 1823.1
    tell_thres = params['EXPMETER_TELLU_THRES'] = 0.95
    # create masks
    with warnings.catch_warnings(record=True) as _:
        mask1 = pwave_map > min_lambda
        mask2 = pwave_map < max_lambda
        mask3 = ptellu_map > tell_thres

    # combined mask
    mask = mask1 & mask2 & mask3

    # get raw image
    maskraw = mp.rot8(mask, params['RAW_TO_PP_ROTATION'], invert=True)

    # ----------------------------------------------------------------------
    # write output files
    # ----------------------------------------------------------------------
    # add keys to header
    ref_header = drs_fits.add_header_key(ref_header, EM_MIN_WAVE, min_lambda)
    ref_header = drs_fits.add_header_key(ref_header, EM_MAX_WAVE, max_lambda)
    ref_header = drs_fits.add_header_key(ref_header, EM_TELL_THRES, tell_thres)
    # construct output filenames
    infile = ref_infile.filename
    out_pp_file = infile.replace('.fits', 'PPTYPE.fits')
    out_raw_file = infile.replace('.fits', 'RAWTYPE.fits')
    # save pp file
    WLOG(params, '', 'Saving pp file: {0}'.format(out_pp_file))
    drs_fits.writefits(params, out_pp_file, mask, ref_header)

    # save raw to file
    WLOG(params, '', 'Saving raw file: {0}'.format(out_raw_file))
    drs_fits.writefits(params, out_raw_file, maskraw, ref_header)

    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return core.return_locals(params, locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()

# =============================================================================
# End of code
# =============================================================================