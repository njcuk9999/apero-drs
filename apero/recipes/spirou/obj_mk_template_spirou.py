#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
obj_fit_tellu [night_directory] [files]

Using all transmission files, we fit the absorption of a given science
observation. To reduce the number of degrees of freedom, we perform a PCA and
keep only the N (currently we suggest N=5)  principal components in absorbance.
As telluric absorption may shift in velocity from one observation to another,
we have the option of including the derivative of the absorbance in the
reconstruction. The method also measures a proxy of optical depth per molecule
(H2O, O2, O3, CO2, CH4, N2O) that can be used for data quality assessment.

Usage:
  obj_fit_tellu night_name object.fits

Outputs:
  telluDB: TELL_OBJ file - The object corrected for tellurics
        file also saved in the reduced folder
        input file + '_tellu_corrected.fits'

    recon_abso file - The reconstructed absorption file saved in the reduced
                    folder
        input file + '_tellu_recon.fits'

Created on 2019-09-05 at 14:58

@author: cook
"""
import numpy as np
import os

from apero.base import base
from apero import lang
from apero.core import constants
from apero.core.core import drs_log
from apero.core.utils import drs_startup
from apero.core.utils import drs_database2 as drs_database
from apero.io import drs_fits
from apero.io import drs_path
from apero.science.calib import wave
from apero.science import telluric


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'obj_mk_template_spirou.py'
__INSTRUMENT__ = 'SPIROU'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get param dict
ParamDict = constants.ParamDict
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
TextEntry = lang.core.drs_lang_text.TextEntry
TextDict = lang.core.drs_lang_text.TextDict


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
# Everything else is controlled from recipe_definition
def main(objname=None, **kwargs):
    """
    Main function for obj_mk_template_spirou.py

    :param objname: str, the object name to make a template for
    :param kwargs: additional keyword arguments

    :type objname: str

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(objname=objname, **kwargs)
    # ----------------------------------------------------------------------
    # deal with command line inputs / function call inputs
    recipe, params = drs_startup.setup(__NAME__, __INSTRUMENT__, fkwargs)
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
    # get the object name
    objname = params['INPUTS']['OBJNAME']
    # need to convert object to drs object name
    pconst = constants.pload(instrument=params['INSTRUMENT'])
    objname = pconst.DRS_OBJ_NAME(objname)

    # get the filetype (this is overwritten from user inputs if defined)
    filetype = params['INPUTS']['FILETYPE']
    # get the fiber type required
    fiber = params['INPUTS']['FIBER']
    # load the calibration and telluric databases
    calibdbm = drs_database.CalibrationDatabase(params)
    calibdbm.load_db()
    telludbm = drs_database.TelluricDatabase(params)
    telludbm.load_db()
    # ----------------------------------------------------------------------
    # get objects that match this object name
    if params['MKTEMPLATE_FILESOURCE'].upper() == 'DISK':
        object_filenames = drs_fits.find_files(params, recipe, kind='red',
                                               fiber=fiber,
                                               KW_OBJNAME=objname,
                                               KW_OUTPUT=filetype)
    else:
        # define the type of files we want to locate in the telluric database
        tkey = '{0}_{1}'.format(filetype, fiber)
        object_filenames = telluric.get_tellu_objs(params, tkey,
                                                   objnames=[objname])

    # deal with no files being present
    if len(object_filenames) == 0:
        wargs = [objname, filetype]
        WLOG(params, 'warning', TextEntry('10-019-00005', args=wargs))
        # dummy pass of qc --> pass
        qc_params = [['None'], ['None'], ['None'], [1]]
        # update recipe log
        recipe.log.add_qc(params, qc_params, True)
        # update recipe log file
        recipe.log.end(params)
        # end this run
        return drs_startup.return_locals(params, locals())
    # ----------------------------------------------------------------------
    # Get filetype definition
    infiletype = drs_startup.get_file_definition(filetype, params['INSTRUMENT'],
                                                 kind='red')
    # get new copy of file definition
    infile = infiletype.newcopy(recipe=recipe, fiber=fiber)
    # set reference filename
    infile.set_filename(object_filenames[-1])
    # read data
    infile.read_file()
    # Need to deal with how we set the night name (depending on location)
    if params['MKTEMPLATE_FILESOURCE'].upper() == 'DISK':
        # get night name
        nightname = drs_path.get_nightname(params, infile.filename)
        params.set(key='NIGHTNAME', value=nightname, source=mainname)
    else:
        # set night name (we have no info about filename)
        nightname = 'other'
        params.set(key='NIGHTNAME', value='other', source=mainname)
        # make night directory (if it doesn't exist)
        absnightpath = os.path.join(params['OUTPATH'], nightname)
        if not os.path.exists(absnightpath):
            os.makedirs(absnightpath)

    # set up plotting (no plotting before this) -- must be after setting
    #   night name
    recipe.plot.set_location(0)
    # ----------------------------------------------------------------------
    # load master wavelength solution
    mkwargs = dict(header=infile.header, master=True, fiber=fiber,
                   database=calibdbm)
    mprops = wave.get_wavesolution(params, recipe, **mkwargs)
    # ------------------------------------------------------------------
    # Normalize image by peak blaze
    # ------------------------------------------------------------------
    nargs = [np.array(infile.data), infile.header, fiber]
    _, nprops = telluric.normalise_by_pblaze(params, *nargs)
    # ----------------------------------------------------------------------
    # Make data cubes
    # ----------------------------------------------------------------------
    cargs = [object_filenames, infile, mprops, nprops, fiber]
    cprops = telluric.make_template_cubes(params, recipe, *cargs,
                                          database=calibdbm)
    # deal with no good files
    if cprops['MEDIAN'] is None:
        return drs_startup.return_locals(params, locals())
    # ----------------------------------------------------------------------
    # Make s1d cubes
    # ----------------------------------------------------------------------
    s1d_cubes = []
    # get objects that match this object name
    for s1d_filetype in infile.s1d:
        # log progress
        WLOG(params, 'info', TextEntry('40-019-00038', args=[s1d_filetype]))
        # Get filetype definition
        dkwargs = dict(instrument=params['INSTRUMENT'], kind='red')
        s1d_inst = drs_startup.get_file_definition(s1d_filetype, **dkwargs)
        # get new copy of file definition
        s1d_file = s1d_inst.newcopy(recipe=recipe, fiber=fiber)
        # get s1d filenames
        fkwargs = dict(kind='red', fiber=fiber, KW_OBJNAME=objname,
                       KW_OUTPUT=s1d_filetype)
        s1d_filenames = drs_fits.find_files(params, recipe, **fkwargs)
        # make s1d cube
        margs = [s1d_filenames, s1d_file, fiber]
        s1d_props = telluric.make_1d_template_cube(params, recipe, *margs)
        # append to storage
        s1d_cubes.append(s1d_props)

    # ----------------------------------------------------------------------
    # Quality control
    # ----------------------------------------------------------------------
    qc_params, passed = telluric.mk_template_qc(params)
    # update recipe log
    recipe.log.add_qc(params, qc_params, passed)

    # ----------------------------------------------------------------------
    # Write cubes and median to file
    # ----------------------------------------------------------------------
    # write e2ds cubes + median
    margs = [infile, cprops, filetype, fiber, mprops, qc_params]
    template_file = telluric.mk_template_write(params, recipe, *margs)
    props1d = None
    # write s1d cubes + median
    for it, s1d_props in enumerate(s1d_cubes):
        sargs = [infile, s1d_props, infile.s1d[it], fiber, mprops, qc_params]
        props1d = telluric.mk_1d_template_write(params, recipe, *sargs)

    # ----------------------------------------------------------------------
    # Update the telluric database with the template
    # ----------------------------------------------------------------------
    if passed:
        # copy the big cube median to the calibDB
        telludbm.add_tellu_file(template_file)    # , night=nightname)

    # ----------------------------------------------------------------------
    # plots
    # ----------------------------------------------------------------------
    # plot debug plot
    recipe.plot('EXTRACT_S1D', params=params, props=props1d, fiber=fiber,
                kind='Template')
    # plot summary plot
    recipe.plot('SUM_EXTRACT_S1D', params=params, props=props1d, fiber=fiber,
                kind='Template')
    # ----------------------------------------------------------------------
    # Construct summary document
    # ----------------------------------------------------------------------
    telluric.mk_template_summary(recipe, params, cprops, qc_params)

    # ------------------------------------------------------------------
    # update recipe log file
    # ------------------------------------------------------------------
    recipe.log.end(params)

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
