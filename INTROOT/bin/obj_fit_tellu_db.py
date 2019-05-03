#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-05-03 at 09:49

@author: cook
"""
from __future__ import division

import obj_fit_tellu
import obj_mk_obj_template

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouStartup
from SpirouDRS import spirouTelluric


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'obj_fit_tellu_db.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# Custom parameter dictionary
ParamDict = spirouConfig.ParamDict
# Get sigma FWHM
SIG_FWHM = spirouCore.spirouMath.fwhm
# Get plotting functions
sPlt = spirouCore.sPlt


# =============================================================================
# Define functions
# =============================================================================
def main(cores=1, objects=None, filetype='EXT_E2DS_FF_AB'):
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # set up function name
    main_name = __NAME__ + '.main()'
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)

    # now get custom arguments
    pos, fmt = [0, 1, 2], [int, str, str]
    names = ['cores', 'objects', 'filetype']
    call = [cores, objects, filetype]
    required = [False, False, False]
    customargs = spirouStartup.GetCustomFromRuntime(p, pos, fmt, names,
                                                    calls=call,
                                                    required=required,
                                                    require_night_name=False)
    p = spirouStartup.LoadArguments(p, None, customargs=customargs,
                                    mainfitsdir='reduced',
                                    require_night_name=False)

    # keep track of errors
    errors = []

    # -------------------------------------------------------------------------
    # find all objects (matching 'objects' if not None)
    target_list = spirouTelluric.FindObjects(p)

    # print number found
    nfound = len(target_list)
    nstar = 0
    for target in list(target_list.keys()):
        nstar += len(target_list[target])

        wmsg = 'Found target "{0}" ({1} observations total)'
        WLOG(p, 'info', wmsg.format(target, len(target_list[target])))
    # list total found
    wmsg = 'Found {0} observations total for {1} object(s)'
    WLOG(p, 'info', wmsg.format(nstar, nfound))

    # -------------------------------------------------------------------------
    # Step 1: Run fit_tellu on all objects
    # -------------------------------------------------------------------------
    for t_it, target in enumerate(list(target_list.keys())):
        # loop around object filenames
        for o_it, objfilename in enumerate(target_list[target]):
            # Log progress
            pargs = [p, 'Fit Tellurics', target, t_it, nfound,
                     o_it, len(target_list[target])]
            spirouTelluric.UpdateProcessDB(*pargs)
            # get arguments from filename
            args = spirouTelluric.GetDBarguments(p, objfilename)
            # run obj_mk_tellu
            try:
                obj_fit_tellu.main(**args)
            except SystemExit as e:
                errors.append([pargs[1], objfilename, e])
            # force close all plots
            sPlt.closeall()

    # -------------------------------------------------------------------------
    # Step 2: Run mk_obj_template on each science target
    # -------------------------------------------------------------------------
    for t_it, target in enumerate(list(target_list.keys())):
        # log progress (big)
        pmsg = 'Make Telluric Template: Processing object = {0} ({1}/{2}'
        wmsgs = ['', '=' * 60, '', pmsg.format(target, t_it + 1, nfound),
                 '', '=' * 60, '']
        WLOG(p, 'info', wmsgs, wrap=False)
        # get last object
        objfilename = target_list[target][-1]
        # get arguments from filename
        args = spirouTelluric.GetDBarguments(p, objfilename)
        # run obj_mk_obj_template
        try:
            obj_mk_obj_template.main(**args)
        except SystemExit as e:
            errors.append(['Telluric Template', target, e])
        # force close all plots
        sPlt.closeall()

    # -------------------------------------------------------------------------
    # Step 3: Re-Run fit_tellu on all objects
    # -------------------------------------------------------------------------
    for t_it, target in enumerate(list(target_list.keys())):
        # loop around object filenames
        for o_it, objfilename in enumerate(target_list[target]):
            # Log progress
            pargs = [p, 'Fit Tellurics', target, t_it, nfound,
                     o_it, len(target_list[target])]
            spirouTelluric.UpdateProcessDB(*pargs)
            # get arguments from filename
            args = spirouTelluric.GetDBarguments(p, objfilename)
            # run obj_mk_tellu
            try:
                obj_fit_tellu.main(**args)
            except SystemExit as e:
                errors.append([pargs[1], objfilename, e])
            # force close all plots
            sPlt.closeall()

    # ----------------------------------------------------------------------
    # Print all errors
    # ----------------------------------------------------------------------
    if len(errors) > 0:
        emsgs = ['', '=' * 50, 'Errors were as follows: ']
        # loop around errors
        for error in errors:
            emsgs.append('')
            emsgs.append('{0}: Object = {1}'.format(error[0], error[1]))
            emsgs.append('\t{0}'.format(error[2]))
            emsgs.append('')
        WLOG(p, 'error', emsgs)

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    p = spirouStartup.End(p)
    # return a copy of locally defined variables in the memory
    return dict(locals())

    # =============================================================================
    # Start of code
    # =============================================================================


if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()
    # exit message if in debug mode
    spirouStartup.Exit(ll, has_plots=False)

# =============================================================================
# End of code
# =============================================================================
