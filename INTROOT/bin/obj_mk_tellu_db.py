#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-30 at 14:44

@author: cook
"""
from __future__ import division
import numpy as np
import os
import warnings

import obj_mk_tellu_new
import obj_fit_tellu
import obj_mk_obj_template

from SpirouDRS import spirouTools
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
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
    # constants for constants file
    p['TELLU_DB_ALLOWED_OUTPUT'] = ['EXT_E2DS_AB', 'EXT_E2DS_A', 'EXT_E2DS_B',
                                    'EXT_E2DS_FF_AB', 'EXT_E2DS_FF_A',
                                    'EXT_E2DS_FF_B']
    p['TELLU_DB_ALLOWED_EXT_TYPE'] = ['OBJ_DARK', 'OBJ_FP']

    # -------------------------------------------------------------------------
    # find all telluric stars
    telluric_stars = find_telluric_stars(p)

    # print number found
    nfound = len(telluric_stars)
    nstar = 0
    for tell_star in list(telluric_stars.keys()):
        nstar += len(telluric_stars[tell_star])

    wmsg = 'Found {0} Telluric stars ({1} observations total)'
    WLOG(p, 'info', wmsg.format(nfound, nstar))

    # -------------------------------------------------------------------------
    # Step 0: Reset telluric database
    # -------------------------------------------------------------------------
    reset = spirouTools.drs_reset.reset_confirmation(p, 'TelluDB')
    if reset:
        spirouTools.drs_reset.reset_telludb(p, False)

    # -------------------------------------------------------------------------
    # Step 1: Run mk_tellu on all telluric stars
    # -------------------------------------------------------------------------
    for t_it, tell_star in enumerate(list(telluric_stars.keys())):
        # loop around object filenames
        for o_it, objfilename in enumerate(telluric_stars[tell_star]):
            # Log progress
            update_process(p, 'Make Tellurics II', tell_star, t_it, nfound,
                           o_it, len(telluric_stars[tell_star]))
            # get arguments from filename
            args = get_arguments(p, objfilename)
            # run obj_mk_tellu
            obj_mk_tellu_new.main(**args)
            # force close all plots
            sPlt.closeall()

    # -------------------------------------------------------------------------
    # Step 2: Run fit tellu on all telluric stars
    # -------------------------------------------------------------------------
    for t_it, tell_star in enumerate(list(telluric_stars.keys())):
        # loop around object filenames
        for o_it, objfilename in enumerate(telluric_stars[tell_star]):
            # Log progress
            update_process(p, 'Make Tellurics II', tell_star, t_it, nfound,
                           o_it, len(telluric_stars[tell_star]))
            # get arguments from filename
            args = get_arguments(p, objfilename)
            # run obj_mk_tellu
            obj_fit_tellu.main(**args)
            # force close all plots
            sPlt.closeall()

    # -------------------------------------------------------------------------
    # step 3: Run mk_obj_template on each telluric star obj name
    # -------------------------------------------------------------------------
    for t_it, tell_star in enumerate(list(telluric_stars.keys())):
        # log progress (big)
        pmsg = 'Make Telluric Template: Processing object = {0} ({1}/{2}'
        wmsgs = ['', '='*60, '', pmsg.format(tell_star, t_it+1, nfound),
                 '', '='*60, '']
        WLOG(p, 'info', wmsgs, wrap=False)
        # get last object
        objfilename = telluric_stars[tell_star][-1]
        # get arguments from filename
        args = get_arguments(p, objfilename)
        # run obj_mk_obj_template
        obj_mk_obj_template.main(**args)
        # force close all plots
        sPlt.closeall()

    # -------------------------------------------------------------------------
    # step 4: Run mk_tellu on all telluric stars
    # -------------------------------------------------------------------------
    for t_it, tell_star in enumerate(list(telluric_stars.keys())):
        # loop around object filenames
        for o_it, objfilename in enumerate(telluric_stars[tell_star]):
            # Log progress
            update_process(p, 'Make Tellurics II', tell_star, t_it, nfound,
                           o_it, len(telluric_stars[tell_star]))
            # get arguments from filename
            args = get_arguments(p, objfilename)
            # run obj_mk_tellu
            obj_mk_tellu_new.main(**args)
            # force close all plots
            sPlt.closeall()

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    p = spirouStartup.End(p)
    # return a copy of locally defined variables in the memory
    return dict(locals())



def update_process(p, title, objname, i1, t1, i2, t2):
    msg1 = '{0}: Processing object = {1} ({2}/{3})'
    msg2 = '\tObject {0} of {1}'
    wmsgs = ['', '=' * 60, '', msg1.format(title, objname, i1 + 1, t1),
             msg2.format(i2 + 1, t2), '', '=' * 60, '', ]
    WLOG(p, 'info', wmsgs, wrap=False)


def get_arguments(p, absfilename):
    # get constants from p
    path = p['ARG_FILE_DIR']
    # get relative path
    relpath = absfilename.split(path)[-1]
    # get night name
    night_name = os.path.dirname(relpath)
    # get filename
    filename = os.path.basename(relpath)
    # run dict
    return dict(night_name=night_name, files=[filename])



def find_telluric_stars(p):

    # get parameters from p
    path = p['ARG_FILE_DIR']
    filetype = p['FILETYPE']
    allowedtypes = p['TELLU_DB_ALLOWED_OUTPUT']
    ext_types = p['TELLU_DB_ALLOWED_EXT_TYPE']
    # -------------------------------------------------------------------------
    # get the list of whitelist files
    tell_names = spirouTelluric.spirouTelluric.get_whitelist()
    # -------------------------------------------------------------------------
    # check file type is allowed
    if filetype not in allowedtypes:
        emsgs = ['Invalid file type = {0}'.format(filetype),
                 '\t Must be one of the following']
        for allowedtype in allowedtypes:
            emsgs.append('\t\t - "{0}"'.format(allowedtype))
    # -------------------------------------------------------------------------
    # store index files
    index_files = []
    # walk through path and find index files
    for root, dirs, files in os.walk(path):
        for filename in files:
            if filename == spirouConfig.Constants.INDEX_OUTPUT_FILENAME():
                index_files.append(os.path.join(root, filename))
    # -------------------------------------------------------------------------
    # valid files dictionary (key = telluric object name)
    valid_files = dict()
    # loop around telluric names
    for tell_name in tell_names:
        # ---------------------------------------------------------------------
        # log progress
        wmsg = 'Searching for telluric star: "{0}"'
        WLOG(p, '', wmsg.format(tell_name))

        # storage for this objects files
        valid_obj_files = []
        # ---------------------------------------------------------------------
        # loop through index files
        for index_file in index_files:
            # read index file
            index = spirouImage.ReadFitsTable(p, index_file)
            # get directory
            dirname = os.path.dirname(index_file)
            # -----------------------------------------------------------------
            # get filename and object name
            index_filenames = index['FILENAME']
            index_objnames = index['OBJNAME']
            index_output = index[p['KW_OUTPUT'][0]]
            index_ext_type = index[p['KW_EXT_TYPE'][0]]
            # -----------------------------------------------------------------
            # mask by objname
            mask1 = index_objnames == tell_name
            # mask by KW_OUTPUT
            mask2 = index_output == filetype
            # mask by KW_EXT_TYPE
            mask3 = np.zeros(len(index), dtype=bool)
            for ext_type in ext_types:
                mask3 |= (index_ext_type == ext_type)
            # combine masks
            mask = mask1 & mask2 & mask3
            # -----------------------------------------------------------------
            # append found files to this list
            if np.sum(mask) > 0:
                for filename in index_filenames[mask]:
                    # construct absolute path
                    absfilename = os.path.join(dirname, filename)
                    # check that file exists
                    if not os.path.exists(absfilename):
                        continue
                    # append to storage
                    if filename not in valid_obj_files:
                        valid_obj_files.append(absfilename)
        # ---------------------------------------------------------------------
        # log found
        wmsg = '\tFound {0} objects'.format(len(valid_obj_files))
        WLOG(p, '', wmsg)
        # ---------------------------------------------------------------------
        # append to full dictionary
        if len(valid_obj_files) > 0:
            valid_files[tell_name] = valid_obj_files
    # return full list
    return valid_files


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
