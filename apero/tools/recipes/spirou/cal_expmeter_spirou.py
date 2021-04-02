#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2020-02-28 at 16:47

@author: cook
"""
import numpy as np
import warnings

from apero.base import base
from apero import lang
from apero.core import constants
from apero.core import math as mp
from apero.core.core import drs_database
from apero.core.core import drs_log
from apero.core.core import drs_file
from apero.core.utils import drs_startup
from apero.core.utils import drs_utils
from apero.science.calib import shape
from apero.science.calib import wave
from apero.science import telluric
from apero.tools.module.testing import drs_dev
from apero.tools.module.utils import inverse

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'cal_expmeter_spirou.py'
__INSTRUMENT__ = 'SPIROU'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get constants
Constants = constants.load()
# get param dict
ParamDict = constants.ParamDict
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
textentry = lang.textentry
# -----------------------------------------------------------------------------
# set up recipe definitions (overwrites default one)
RMOD = drs_dev.RecipeDefinition(instrument=__INSTRUMENT__)
# define a recipe for this tool
exposuremeter = drs_dev.TmpRecipe()
exposuremeter.name = __NAME__
exposuremeter.shortname = 'EXPMTR'
exposuremeter.instrument = __INSTRUMENT__
exposuremeter.in_block_str = 'tmp'
exposuremeter.out_block_str = 'red'
exposuremeter.extension = 'fits'
exposuremeter.description = 'Produces an exposuremeter map'
exposuremeter.kind = 'misc'
exposuremeter.set_arg(pos=0, **RMOD.mod.obs_dir)
exposuremeter.set_kwarg(name='--fibers', dtype=str, default='None',
                        helpstr='Choose the fibers to populate in the mask')

# add recipe to recipe definition
RMOD.add(exposuremeter)

# get file definitions for this instrument
FMOD = drs_dev.FileDefinition(instrument=__INSTRUMENT__)
# make files for this tool
exp_pp_file = drs_dev.TmpFitsFile('EXP_PP_FILE', KW_OUTPUT='EXP_PP_FILE',
                                  filetype='.fits', prefix='EXPMETER_',
                                  suffix='_PPTYPE', remove_insuffix=True,
                                  intype=[FMOD.files.out_wave_night],
                                  outfunc=FMOD.out.general_file)
exp_raw_file = drs_dev.TmpFitsFile('EXP_RAW_FILE', KW_OUTPUT='EXP_PP_FILE',
                                   filetype='.fits', prefix='EXPMETER_',
                                   suffix='_RAWTYPE', remove_insuffix=True,
                                   intype=[FMOD.files.out_wave_night],
                                   outfunc=FMOD.out.general_file)

# header keys
EM_MIN_WAVE = ['EM_MNWAV', 0.0, 'Exposure meter min wave for mask']
EM_MAX_WAVE = ['EM_MXWAV', 0.0, 'Exposure meter max wave for mask']
EM_TELL_THRES = ['EM_TLIM', 0.0, 'Exposure meter telluric threshold for mask']
EM_KIND = ['EM_KIND', '', 'Exposure meter image kind (PP or RAW)']


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
# Everything else is controlled from recipe_definition
def main(obs_dir=None, **kwargs):
    """
    Main function for exposuremeter_spirou.py

    :param kwargs: additional keyword arguments

    :type instrument: str

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(obs_dir=obs_dir, **kwargs)
    # ----------------------------------------------------------------------
    # deal with command line inputs / function call inputs
    recipe, params = drs_startup.setup(__NAME__, __INSTRUMENT__, fkwargs,
                                       rmod=RMOD)
    # solid debug mode option
    if kwargs.get('DEBUG0000', False):
        return recipe, params
    # ----------------------------------------------------------------------
    # run main bulk of code (catching all errors)
    llmain, success = drs_startup.run(__main__, recipe, params)
    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    return drs_startup.end_main(params, llmain, recipe, success)


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
    pconst = constants.pload()
    # load the calibration database
    calibdbm = drs_database.CalibrationDatabase(params)
    calibdbm.load_db()
    # ----------------------------------------------------------------------
    # get all allowed fibers
    allowed_fibers = pconst.INDIVIDUAL_FIBERS()
    # get fibers
    if params['INPUTS']['FIBERS'] not in ['None', '']:
        fibers = params['INPUTS'].listp('FIBERS', dtype=str)
        # check that all fibers are valid
        for fiber in fibers:
            if fiber not in allowed_fibers:
                # log error message
                emsg = ('--fibers FIBER="{0}" is not a valid fiber'
                        '\n\t Valid fibers are {1}')
                eargs = [fiber, ' or '.join(allowed_fibers)]
                WLOG(params, 'error', emsg.format(*eargs))
    # else set fibers to all allowed fibers
    else:
        fibers = allowed_fibers

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
        drsfile = drs_file.get_file_definition(params, filetype,
                                               block_kind='red')
        # get all "filetype" filenames
        filters = dict(KW_OUTPUT=filetype, KW_FIBER=fiber,
                       OBS_DIR=params['OBS_DIR'])
        files = drs_utils.find_files(params, block_kind='red', filters=filters)
        # deal with no files found
        if len(files) == 0:
            eargs = [filetype, fiber, mainname]
            emsg = 'No files found for {0} (fiber = {1}) \n\t Function = {2}'
            WLOG(params, 'error', emsg.format(*eargs))
        # make a new copy of infile
        infile = drsfile.newcopy(filename=files[-1], params=params)
        # read file
        infile.read_file()
        # append to storage
        wave_images[fiber] = infile.get_data()
        wave_infiles[fiber] = infile

    # ----------------------------------------------------------------------
    # Get the telluric image
    # ----------------------------------------------------------------------
    # storage for tellu images
    tellu_images = dict()

    for fiber in fibers:
        # wave infile
        header = wave_infiles[fiber].get_header()
        ishape = wave_images[fiber].get_data().shape
        # ------------------------------------------------------------------
        # load wavelength solution for this fiber
        wprops = wave.get_wavesolution(params, recipe,
                                       filename=wave_infiles[fiber].filename,
                                       database=calibdbm)
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
    ref_header = ref_infile.get_header()
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
        header = wave_infiles[fiber].get_header()
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
        header = wave_infiles[fiber].get_header()
        # get the localisation parameters for this fiber
        cents, wids = centers[fiber], widths[fiber]
        # get straighted wave image
        WLOG(params, '', '\t Adding flux (Fiber={0})'.format(fiber))
        swave_map = inverse.e2ds_to_simage(wave_images[fiber], ximage, yimage,
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
        header = wave_infiles[fiber].get_header()
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
    min_lambda = params['EXPMETER_MIN_LAMBDA']
    max_lambda = params['EXPMETER_MAX_LAMBDA']
    tell_thres = params['EXPMETER_TELLU_THRES']
    # create masks
    with warnings.catch_warnings(record=True) as _:
        mask1 = pwave_map > min_lambda
        mask2 = pwave_map < max_lambda
        mask3 = ptellu_map > tell_thres

    # combined mask
    mask = np.array(mask1 & mask2 & mask3)
    # make mask a integer mask
    mask = mask.astype(int)

    # ----------------------------------------------------------------------
    # Convert drs --> pp and pp --> raw
    # ----------------------------------------------------------------------
    maskpp = inverse.drs_to_pp(params, mask, fill=0)

    # get raw image
    maskraw = mp.rot8(maskpp, params['RAW_TO_PP_ROTATION'], invert=True)

    # ----------------------------------------------------------------------
    # write pp out file
    # ----------------------------------------------------------------------
    # get a new copy of the out file
    out_pp_file = exp_pp_file.newcopy(params=params)
    # custom suffix
    suffix = '{0}_{1}'.format(exp_pp_file.suffix, ''.join(fibers))
    # construct filename
    out_pp_file.construct_filename(infile=ref_infile, suffix=suffix)
    # copy header from ref file
    out_pp_file.copy_original_keys(ref_infile)
    # add header keys
    out_pp_file.add_hkey(EM_MIN_WAVE, value=min_lambda)
    out_pp_file.add_hkey(EM_MAX_WAVE, value=max_lambda)
    out_pp_file.add_hkey(EM_TELL_THRES, value=tell_thres)
    out_pp_file.add_hkey(EM_KIND, value='PP')
    # add data
    out_pp_file.data = maskpp
    # save to file
    WLOG(params, '', 'Saving pp file: {0}'.format(out_pp_file.filename))
    # define multi lists
    data_list, name_list = [], []
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=out_pp_file)]
        name_list += ['PARAM_TABLE']
    # write file
    out_pp_file.write_multi(data_list=data_list, name_list=name_list,
                            block_kind=recipe.out_block_str,
                            runstring=recipe.runstring)
    # ----------------------------------------------------------------------
    # write raw out file
    # ----------------------------------------------------------------------
    # get a new copy of the out file
    out_raw_file = exp_raw_file.newcopy(params=params)
    # custom suffix
    suffix = '{0}_{1}'.format(exp_raw_file.suffix, ''.join(fibers))
    # construct filename
    out_raw_file.construct_filename(infile=ref_infile, suffix=suffix)
    # copy header from ref file
    out_raw_file.copy_original_keys(ref_infile)
    # add header keys
    out_raw_file.add_hkey(EM_MIN_WAVE, value=min_lambda)
    out_raw_file.add_hkey(EM_MAX_WAVE, value=max_lambda)
    out_raw_file.add_hkey(EM_TELL_THRES, value=tell_thres)
    out_raw_file.add_hkey(EM_KIND, value='PP')
    # add data
    out_raw_file.data = np.array(maskraw).astype(int)
    # save to file
    WLOG(params, '', 'Saving raw file: {0}'.format(out_raw_file.filename))
    # define multi lists
    data_list, name_list = [], []
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=out_raw_file)]
        name_list += ['PARAM_TABLE']
    # write file
    out_raw_file.write_multi(data_list=data_list, name_list=name_list,
                             block_kind=recipe.out_block_str,
                             runstring=recipe.runstring)

    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return drs_startup.return_locals(params, locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()

# =============================================================================
# End of code
# =============================================================================
