#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-05 at 16:46

@author: cook
"""
import itertools
import os

from apero.base import base
from apero.core import constants
from apero.core.core import drs_log
from apero.core.core import drs_file
from apero.core.utils import drs_startup
from apero.core.utils import drs_utils
from apero.science import extract
from apero.tools.module.testing import drs_dev


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_uberv_spirou.py'
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
# -----------------------------------------------------------------------------
# set up recipe definitions (overwrites default one)
RMOD = drs_dev.RecipeDefinition(instrument=__INSTRUMENT__)
# define a recipe for this tool
cal_update_berv = drs_dev.TmpRecipe()
cal_update_berv.name = __NAME__
cal_update_berv.shortname = 'UBERV'
cal_update_berv.instrument = __INSTRUMENT__
cal_update_berv.in_block_str = 'red'
cal_update_berv.out_block_str = 'red'
cal_update_berv.extension = 'fits'
cal_update_berv.description = 'Updates all BERV parameters'
cal_update_berv.kind = 'misc'
cal_update_berv.set_kwarg(name='--skip', dtype='bool', default=True,
                          helpstr='Skip files already with BERV measurement')
cal_update_berv.set_kwarg(name='--objects', dtype=str, default='None',
                          helpstr='List of objects to correct berv for')
# add recipe to recipe definition
RMOD.add(cal_update_berv)


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
# Everything else is controlled from recipe_definition
def main(**kwargs):
    """
    Main function for cal_update_berv.py

    :param kwargs: additional keyword arguments

    :type instrument: str

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(**kwargs)
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
    # ----------------------------------------------------------------------
    # find all OBJ_DARK and OBJ_FP files
    filetypes = ['OBJ_FP', 'OBJ_DARK']
    # set the KW_OUTPUT (DRSOUTID) to get
    intypes = ['EXT_E2DS', 'EXT_E2DS_FF', 'EXT_S1D_W', 'EXT_S1D_V',
               'EXT_FPLIST']
    # set the fibers
    fibers = ['AB', 'A', 'B', 'C']
    # add prefixes to remove
    prefixes = ['DEBUG-uncorr-']

    # get list of skip objects
    if params['INPUTS']['OBJECTS'] in [None, 'None', 'None', '']:
        skip_objects = None
    else:
        skip_objects = params['INPUTS'].listp('OBJECTS', dtype=str)
    # ----------------------------------------------------------------------
    # get all combinations
    combinations = list(itertools.product(filetypes, intypes, fibers))
    # get files of this type and the in types
    filenames, infiletypes = dict(), dict()
    # ----------------------------------------------------------------------
    # loop around files and update BERV
    for comb in combinations:
        # get this iterations values
        filetype, intype, fiber = comb
        # ------------------------------------------------------------------
        # log progress
        WLOG(params, 'info', params['DRS_HEADER'])
        wargs = [filetype, intype, fiber]
        msg = 'FILETYPE = {0}   INTYPE = {1}   FIBER = {2}'
        WLOG(params, 'info', msg.format(*wargs))
        WLOG(params, 'info', params['DRS_HEADER'])
        # get the in file type
        infiletype = drs_file.get_file_definition(params, intype,
                                                  block_kind='red')
        # get the files for this filetype
        fkwargs = dict()
        fkwargs['KW_OUTPUT'] = intype
        fkwargs['KW_DPRTYPE'] = filetype
        fkwargs['KW_FIBER'] = fiber
        if skip_objects is not None:
            fkwargs['KW_OBJNAME'] = skip_objects
        WLOG(params, '', 'Finding files...')
        filenames1 = drs_utils.find_files(params, block_kind='red',
                                          filters=fkwargs)
        # group files
        for filename in filenames1:
            odocode = os.path.basename(filename).split('_pp')[0]
            # make sure we get rid of prefix as well
            for prefix in prefixes:
                if odocode.startswith(prefix):
                    odocode = odocode.split(prefix)[-1]

            if odocode in filename:
                if odocode in filenames:
                    filenames[odocode].append(filename)
                    infiletypes[odocode].append(infiletype)
                else:
                    filenames[odocode] = [filename]
                    infiletypes[odocode] = [infiletype]

    # ------------------------------------------------------------------
    # loop around files
    for it, odocode in enumerate(list(filenames.keys())):
        # print file currently processing
        wmsg = 'Processing file {1} of {2} \n\t File: {0}'
        wargs = [odocode, it + 1, len(list(filenames.keys()))]
        WLOG(params, 'info', wmsg.format(*wargs))
        # ----------------------------------------------------------
        # get files associated with this odocode
        ofiles = filenames[odocode]
        ointypes = infiletypes[odocode]
        # -------------------------------------------
        # skip if already using barycorppy
        skip = params['INPUTS']['SKIP']
        infiles = []
        # loop around ofiles
        for jt, filename in enumerate(ofiles):
            # get new copy of file definition
            infile1 = ointypes[jt].newcopy(params=params)
            # set filename
            infile1.set_filename(ofiles[jt])
            # skip missing files (they shouldn't be missing unless
            #     process interupted)
            if not os.path.exists(infile1.filename):
                continue
            # read data
            infile1.read_file()
            # get header from file instance
            header1 = infile1.get_header()
            # append to list
            infiles.append(infile1)
            # ----------------------------------------------------------
            # skip if already using barycorppy
            if header1['BERVSRCE'] != 'barycorrpy':
                skip = False
            # ----------------------------------------------------------
        # deal with skip
        if skip:
            for jt, filename in enumerate(ofiles):
                wmsg = 'Skipping file {0}'.format(filename)
                WLOG(params, '', 'Skipping file {0}'.format(filename))
            continue
        # --------------------------------------------------------------
        # get the first infile
        infile = infiles[0]
        # --------------------------------------------------------------
        # get header from file instance
        header = infile.get_header()
        # --------------------------------------------------------------
        # Calculate Barycentric correction
        # --------------------------------------------------------------
        props = ParamDict()
        props['DPRTYPE'] = infile.get_hkey('KW_DPRTYPE', dtype=float)
        bprops = extract.get_berv(params, infile, header,
                                  warn=True, force=True)
        args = [infile.basename, bprops['USE_BERV']]
        # print that we have update the BERV measurement
        if bprops['USED_ESTIMATE']:
            wargs = ['PyASL', bprops['USE_BERV']]
        else:
            wargs = ['Barycorrpy', bprops['USE_BERV']]
        WLOG(params, '', '{0} BERV: {1}'.format(*wargs))

        # log the change to berv parameters (input vs output)
        WLOG(params, '', 'Final berv input parameters:')
        for key in bprops:
            if key in infile.get_header():
                wargs = [key, infile.get_header()[key], bprops[key]]
                WLOG(params, '', '\t{0:20s}{1} --> {2}'.format(*wargs))
        # --------------------------------------------------------------
        # overwrite file(s)
        # --------------------------------------------------------------
        for jt in range(len(infiles)):
            # get infile from storage
            infile1 = infiles[jt]
            # get header from file instance
            header1 = infile1.get_header()
            # ----------------------------------------------------------
            # log progress
            wmsg = 'Writing to file: {0}'.format(infile1.filename)
            WLOG(params, '', wmsg)
            # update header
            infile1.copy_original_keys(infile1, forbid_keys=False,
                                       allkeys=True)
            extract.add_berv_keys(params, infile1, bprops)
            # define multi lists
            data_list, name_list = [], []
            # snapshot of parameters
            if params['PARAMETER_SNAPSHOT']:
                data_list += [params.snapshot_table(recipe,
                                                    drsfitsfile=infile1)]
                name_list += ['PARAM_TABLE']
            # write data to file
            infile1.write_multi(data_list=data_list, name_list=name_list,
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
    # import sys
    # sys.argv = 'update_berv.py --objects TOI-1278,TOI-1759,AUMic,TOI-1452,TOI-233,TOI-736,TOI-876,TOI-732'.split()

    # run main with no arguments (get from command line - sys.argv)
    ll = main()

# =============================================================================
# End of code
# =============================================================================
