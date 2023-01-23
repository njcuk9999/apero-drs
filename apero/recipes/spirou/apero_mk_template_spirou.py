#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
apero_mk_template_nirps_ha.py [object name]

APERO recipe to make object templates

Created on 2019-09-05 at 14:58

@author: cook
"""
import os
from typing import Any, Dict, Optional, Tuple, Union

import numpy as np

from apero import lang
from apero.base import base
from apero.core import constants
from apero.core.core import drs_database
from apero.core.core import drs_file
from apero.core.core import drs_log
from apero.core.utils import drs_recipe
from apero.core.utils import drs_startup
from apero.core.utils import drs_utils
from apero.science import telluric
from apero.science.calib import wave

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_mk_template_spirou.py'
__INSTRUMENT__ = 'SPIROU'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
# Get Recipe class
DrsRecipe = drs_recipe.DrsRecipe
# Get parameter class
ParamDict = constants.ParamDict
# Get the text types
textentry = lang.textentry


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
# Everything else is controlled from recipe_definition
def main(objname: Optional[str] = None, **kwargs
         ) -> Union[Dict[str, Any], Tuple[DrsRecipe, ParamDict]]:
    """
    Main function for apero_mk_template

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


def __main__(recipe: DrsRecipe, params: ParamDict) -> Dict[str, Any]:
    """
    Main code: should only call recipe and params (defined from main)

    :param recipe: DrsRecipe, the recipe class using this function
    :param params: ParamDict, the parameter dictionary of constants

    :return: dictionary containing the local variables
    """
    # ----------------------------------------------------------------------
    # Main Code
    # ----------------------------------------------------------------------
    mainname = __NAME__ + '._main()'
    # get the object name
    objname = params['INPUTS']['OBJNAME']
    # need to convert object to drs object name
    pconst = constants.pload()
    # load object database
    objdbm = drs_database.AstrometricDatabase(params)
    objdbm.load_db()
    # get clean / alias-safe version of object name
    objname, _ = objdbm.find_objname(pconst, objname)
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
        object_filenames = drs_utils.find_files(params, block_kind='red',
                                                filters=dict(KW_OBJNAME=objname,
                                                             KW_OUTPUT=filetype,
                                                             KW_FIBER=fiber))
    else:
        # define the type of files we want to locate in the telluric database
        object_filenames = telluric.get_tellu_objs(params, filetype,
                                                   objnames=[objname],
                                                   database=telludbm)
    # ----------------------------------------------------------------------
    # deal with no files being present
    if len(object_filenames) == 0:
        wargs = [objname, filetype]
        WLOG(params, 'warning', textentry('10-019-00005', args=wargs),
             sublevel=2)
        # no object files --> qc failure
        qc_params = [['HAS_OBJ'], ['False'], ['HAS_OBJ==False'], [0]]
        # update recipe log
        recipe.log.add_qc(qc_params, True)
        # update recipe log file
        recipe.log.end()
        # end this run
        return locals()
    else:
        qc_params = [['HAS_OBJ'], ['True'], ['HAS_OBJ==False'], [1]]
    # ----------------------------------------------------------------------
    # Get filetype definition
    infiletype = drs_file.get_file_definition(params, filetype,
                                              block_kind='red')
    # get new copy of file definition
    infile = infiletype.newcopy(params=params, fiber=fiber)
    # set reference filename
    infile.set_filename(object_filenames[-1])
    # read data
    infile.read_file()
    # Need to deal with how we set the observation directory
    #     (depending on location)
    if params['MKTEMPLATE_FILESOURCE'].upper() == 'DISK':
        # set observation directory
        infile_inst = drs_file.DrsPath(params, abspath=infile.filename)
        obs_dir = infile_inst.obs_dir
        params.set(key='OBS_DIR', value=obs_dir, source=mainname)
    else:
        # set observation directory (we have no info about filename)
        obs_dir = 'other'
        params.set(key='OBS_DIR', value='other', source=mainname)
        # make obs directory (if it doesn't exist)
        abspath = os.path.join(params['OUTPATH'], obs_dir)
        if not os.path.exists(abspath):
            os.makedirs(abspath)

    # set up plotting (no plotting before this) -- must be after setting
    #   night name
    recipe.plot.set_location(0)
    # ----------------------------------------------------------------------
    # load reference wavelength solution
    mkwargs = dict(infile=infile, ref=True, fiber=fiber,
                   database=calibdbm, rlog=recipe.log)
    refprops = wave.get_wavesolution(params, recipe, **mkwargs)
    # ------------------------------------------------------------------
    # Normalize image by peak blaze
    # ------------------------------------------------------------------
    nargs = [infile.get_data(copy=True), infile.get_header(), fiber]
    _, nprops = telluric.normalise_by_pblaze(params, *nargs)
    # ----------------------------------------------------------------------
    # Make data cubes
    # ----------------------------------------------------------------------
    cargs = [object_filenames, infile, refprops, nprops, fiber, qc_params]
    cprops = telluric.make_template_cubes(params, recipe, *cargs,
                                          calibdb=calibdbm)
    # ----------------------------------------------------------------------
    # deal with QC params failure (do not continue)
    if not np.all(cprops['QC_PARAMS'][3]):
        # print qc failure
        telluric.mk_template_qc(params, qc_params, cprops['FAIL_MSG'])
        # update recipe log
        recipe.log.add_qc(cprops['QC_PARAMS'], True)
        # update recipe log file
        recipe.log.end()
        # end here
        return locals()
    # ----------------------------------------------------------------------
    # Make s1d cubes
    # ----------------------------------------------------------------------
    s1d_cubes = []
    # get objects that match this object name
    for s1d_filetype in infile.s1d:
        # log progress
        WLOG(params, 'info', textentry('40-019-00038', args=[s1d_filetype]))
        # Get filetype definition
        dkwargs = dict(block_kind='red')
        s1d_inst = drs_file.get_file_definition(params, s1d_filetype, **dkwargs)
        # get new copy of file definition
        s1d_file = s1d_inst.newcopy(params=params, fiber=fiber)
        # get s1d filenames
        filters = dict(KW_OBJNAME=objname, KW_OUTPUT=s1d_filetype,
                       KW_FIBER=fiber)
        s1d_filenames = drs_utils.find_files(params, block_kind='red',
                                             filters=filters)
        # make s1d cube
        margs = [s1d_filenames, s1d_file, fiber, infile.header, calibdbm]
        s1d_props = telluric.make_1d_template_cube(params, recipe, *margs)
        # append to storage
        s1d_cubes.append(s1d_props)

    # ----------------------------------------------------------------------
    # print/log quality control (all assigned previously)
    # ----------------------------------------------------------------------
    qc_params, passed = telluric.mk_template_qc(params, qc_params)
    # update recipe log
    recipe.log.add_qc(qc_params, passed)

    # ----------------------------------------------------------------------
    # Write cubes and median to file
    # ----------------------------------------------------------------------
    # write e2ds cubes + median
    margs = [infile, cprops, filetype, fiber, refprops, qc_params]
    template_file = telluric.mk_template_write(params, recipe, *margs)
    props1d = []
    # write s1d cubes + median
    for it, s1d_props in enumerate(s1d_cubes):
        sargs = [infile, s1d_props, infile.s1d[it], fiber, refprops, qc_params,
                 template_file]
        props1d.append(telluric.mk_1d_template_write(params, recipe, *sargs))

    # ----------------------------------------------------------------------
    # Update the telluric database with the template
    # ----------------------------------------------------------------------
    if passed and params['INPUTS']['DATABASE']:
        # copy the big cube median to the calibDB
        telludbm.add_tellu_file(template_file)
        # add s1d templates to telluric database
        for prop1d in props1d:
            telludbm.add_tellu_file(prop1d['S1DFILE'])

    # ----------------------------------------------------------------------
    # plots
    # ----------------------------------------------------------------------
    for prop1d in props1d:
        # plot debug plot
        recipe.plot('EXTRACT_S1D', params=params, props=prop1d, fiber=fiber,
                    kind='Template')
        # plot summary plot
        recipe.plot('SUM_EXTRACT_S1D', params=params, props=prop1d, fiber=fiber,
                    kind='Template')

    # ----------------------------------------------------------------------
    # Construct summary document
    # ----------------------------------------------------------------------
    telluric.mk_template_summary(recipe, params, cprops, template_file,
                                 qc_params)

    # ------------------------------------------------------------------
    # update recipe log file
    # ------------------------------------------------------------------
    recipe.log.end()

    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return locals()


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()

# =============================================================================
# End of code
# =============================================================================
