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
from __future__ import division
import numpy as np

from apero import core
from apero import locale
from apero.core import constants
from apero.core.core import drs_database
from apero.io import drs_fits
from apero.io import drs_path
from apero.science.calib import wave
from apero.science import telluric


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'obj_mk_template_spirou.py'
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
    recipe, params = core.setup(__NAME__, __INSTRUMENT__, fkwargs)
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
    # get the object name
    objname = params['INPUTS']['OBJNAME']
    # get the filetype (this is overwritten from user inputs if defined)
    filetype = params['INPUTS']['FILETYPE']
    # get the fiber type required
    fiber = params['INPUTS']['FIBER']
    # ----------------------------------------------------------------------
    # get objects that match this object name
    object_filenames = drs_fits.find_files(params, kind='red', fiber=fiber,
                                           KW_OBJNAME=objname,
                                           KW_OUTPUT=filetype)
    # deal with no files being present
    if len(object_filenames) == 0:
        wargs = [objname, filetype]
        WLOG(params, 'warning', TextEntry('10-019-00005', args=wargs))
        return core.return_locals(params, locals())
    # ----------------------------------------------------------------------
    # Get filetype definition
    infiletype = core.get_file_definition(filetype, params['INSTRUMENT'],
                                          kind='red')
    # get new copy of file definition
    infile = infiletype.newcopy(recipe=recipe, fiber=fiber)
    # set reference filename
    infile.set_filename(object_filenames[-1])
    # read data
    infile.read()
    # get night name
    nightname = drs_path.get_nightname(params, infile.filename)
    params.set(key='NIGHTNAME', value=nightname, source=mainname)
    # set up plotting (no plotting before this) -- must be after setting
    #   night name
    recipe.plot.set_location(0)
    # ----------------------------------------------------------------------
    # load master wavelength solution
    mkwargs = dict(header=infile.header, master=True, fiber=fiber)
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
    cprops = telluric.make_template_cubes(params, recipe, *cargs)
    # deal with no good files
    if cprops['MEDIAN'] is None:
        return core.return_locals(params, locals())
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
        s1d_inst = core.get_file_definition(s1d_filetype, **dkwargs)
        # get new copy of file definition
        s1d_file = s1d_inst.newcopy(recipe=recipe, fiber=fiber)
        # get s1d filenames
        fkwargs = dict(kind='red', fiber=fiber, KW_OBJNAME=objname,
                       KW_OUTPUT=s1d_filetype)
        s1d_filenames = drs_fits.find_files(params, **fkwargs)
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
    margs = [infile, cprops, filetype, fiber, qc_params]
    template_file = telluric.mk_template_write(params, recipe, *margs)
    props1d = None
    # write s1d cubes + median
    for it, s1d_props in enumerate(s1d_cubes):
        sargs = [infile, s1d_props, infile.s1d[it], fiber, qc_params]
        props1d = telluric.mk_1d_template_write(params, recipe, *sargs)

    # ----------------------------------------------------------------------
    # Update the telluric database with the template
    # ----------------------------------------------------------------------
    if passed:
        # copy the big cube median to the calibDB
        drs_database.add_file(params, template_file, night=nightname)

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
