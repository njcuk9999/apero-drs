#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-30 at 14:44

@author: cook
"""
from __future__ import division

import obj_mk_tellu
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
__NAME__ = 'obj_mk_tellu_db.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
__args__ = ['cores', 'filetype']
__required__ = [False, False]
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
def main(cores=1, filetype='EXT_E2DS_FF_AB'):
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # set up function name
    main_name = __NAME__ + '.main()'
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)

    # now get custom arguments
    pos, fmt = [0, 1], [int, str]
    names, call = ['cores', 'filetype'], [cores, filetype]
    customargs = spirouStartup.GetCustomFromRuntime(p, pos, fmt, names,
                                                    calls=call,
                                                    require_night_name=False)
    p = spirouStartup.LoadArguments(p, None, customargs=customargs,
                                    mainfitsdir='reduced',
                                    require_night_name=False)
    # -------------------------------------------------------------------------
    # find all telluric stars
    telluric_stars = spirouTelluric.FindTelluricStars(p)

    # print number found
    nfound = len(telluric_stars)
    nstar = 0
    for tell_star in list(telluric_stars.keys()):
        nstar += len(telluric_stars[tell_star])

    wmsg = 'Found {0} Telluric stars ({1} observations total)'
    WLOG(p, 'info', wmsg.format(nfound, nstar))

    # # -------------------------------------------------------------------------
    # # Step 0: Reset telluric database
    # # -------------------------------------------------------------------------
    # #reset = spirouTools.drs_reset.reset_confirmation(p, 'TelluDB')
    # reset = True
    # if reset:
    #     spirouTools.drs_reset.reset_telludb(p, False)

    # keep track of errors
    errors = []

    # -------------------------------------------------------------------------
    # Step 1: Run mk_tellu on all telluric stars
    # -------------------------------------------------------------------------
    for t_it, tell_star in enumerate(list(telluric_stars.keys())):
        # loop around object filenames
        for o_it, objfilename in enumerate(telluric_stars[tell_star]):
            # Log progress
            pargs = [p, 'Make Tellurics I', tell_star, t_it, nfound,
                     o_it, len(telluric_stars[tell_star])]
            spirouTelluric.UpdateProcessDB(*pargs)
            # get arguments from filename
            args = spirouTelluric.GetDBarguments(p, objfilename)
            # run obj_mk_tellu
            try:
                ll = obj_mk_tellu.main(**args)
            except SystemExit as e:
                errors.append([pargs[1], objfilename, e])
            # force close all plots
            sPlt.closeall()

    # -------------------------------------------------------------------------
    # Step 2: Run fit tellu on all telluric stars
    # -------------------------------------------------------------------------
    for t_it, tell_star in enumerate(list(telluric_stars.keys())):
        # loop around object filenames
        for o_it, objfilename in enumerate(telluric_stars[tell_star]):
            # Log progress
            pargs = [p, 'Fit Tellurics', tell_star, t_it, nfound,
                     o_it, len(telluric_stars[tell_star])]
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
    # step 3: Run mk_obj_template on each telluric star obj name
    # -------------------------------------------------------------------------
    for t_it, tell_star in enumerate(list(telluric_stars.keys())):
        # log progress (big)
        pmsg = 'Make Telluric Template: Processing object = {0} ({1}/{2}'
        wmsgs = ['', '=' * 60, '', pmsg.format(tell_star, t_it + 1, nfound),
                 '', '=' * 60, '']
        WLOG(p, 'info', wmsgs, wrap=False)
        # get last object
        objfilename = telluric_stars[tell_star][-1]
        # get arguments from filename
        args = spirouTelluric.GetDBarguments(p, objfilename)
        # run obj_mk_obj_template
        try:
            obj_mk_obj_template.main(**args)
        except SystemExit as e:
            errors.append(['Telluric Template', tell_star, e])
        # force close all plots
        sPlt.closeall()

    # -------------------------------------------------------------------------
    # step 4: Run mk_tellu on all telluric stars
    # -------------------------------------------------------------------------
    for t_it, tell_star in enumerate(list(telluric_stars.keys())):
        # loop around object filenames
        for o_it, objfilename in enumerate(telluric_stars[tell_star]):
            # Log progress
            pargs = [p, 'Make Tellurics II', tell_star, t_it, nfound, o_it,
                     len(telluric_stars[tell_star])]
            spirouTelluric.UpdateProcessDB(*pargs)
            # get arguments from filename
            args = spirouTelluric.GetDBarguments(p, objfilename)
            # run obj_mk_tellu
            try:
                obj_mk_tellu.main(**args)
            except SystemExit as e:
                errors.append([pargs[1], objfilename, e])
            # force close all plots
            sPlt.closeall()

    # ----------------------------------------------------------------------
    # Print all errors
    # ----------------------------------------------------------------------
    if len(errors) > 0:
        emsgs = ['', '='*50, 'Errors were as follows: ']
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
