#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cal_CCF_E2DS_spirou.py
       [night_directory] [E2DSfilename] [mask] [RV] [width] [step]

Computes the CCF for a specific file using a CCF mask, target RV, CCF width
and CCF step.

Created on 2017-12-18 at 15:43

@author: cook

Last modified: 2017-12-18 at 15:48

Up-to-date with cal_CCF_E2DS_spirou AT-4 V47
"""
from __future__ import division
import os
from collections import OrderedDict

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup
from SpirouDRS.spirouImage import spirouFile


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'calc_berv.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get the parameter dictionary class
ParamDict = spirouConfig.ParamDict
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt
# Get Path Exception
PathException = spirouFile.PathException


# =============================================================================
# Define functions
# =============================================================================
def main(night_name=None, e2dsfiles=None):
    """
    cal_CCF_E2DS_spirou.py main function, if arguments are None uses
    arguments from run time i.e.:
        cal_CCF_E2DS_spirou.py [night_directory] [E2DSfilename] [mask] [RV]
                               [width] [step]

    :param night_name: string or None, the folder within data raw directory
                                containing files (also reduced directory) i.e.
                                /data/raw/20170710 would be "20170710" but
                                /data/raw/AT5/20180409 would be "AT5/20180409"
    :param e2dsfiles: list of string, the E2DS files to use

    :return ll: dictionary, containing all the local variables defined in
                main
    """
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)
    # need custom args (to accept full path or wild card
    if e2dsfiles is None:
        names, types = ['e2dsfiles'], [str]
        customargs = spirouStartup.GetCustomFromRuntime(p, [0], types, names,
                                                        last_multi=True)
    else:
        customargs = dict(e2dsfiles=e2dsfiles)
    # get parameters from configuration files and run time arguments
    p = spirouStartup.LoadArguments(p, night_name, customargs=customargs,
                                    mainfitsdir='reduced')

    # ----------------------------------------------------------------------
    # Process files (including wildcards)
    # ----------------------------------------------------------------------
    try:
        e2dsfiles = spirouFile.Paths(p['E2DSFILES'],
                                     root=p['ARG_FILE_DIR']).abs_paths
    except PathException as e:
        WLOG(p, 'error', e)

    # loop around files
    for it, e2dsfile in enumerate(e2dsfiles):
        # get the base file name
        e2dsfilename = os.path.basename(e2dsfile)
        # log the file process
        wargs = [e2dsfilename, it + 1, len(e2dsfiles)]
        wmsg = ' * Processing file {0} ({1} of {2})'.format(*wargs)
        WLOG(p, '', spirouStartup.spirouStartup.HEADER)
        WLOG(p, '', wmsg)
        WLOG(p, '', spirouStartup.spirouStartup.HEADER)

        # ------------------------------------------------------------------
        # Check that we can process file
        # ------------------------------------------------------------------
        # check if ufile exists
        if not os.path.exists(e2dsfile):
            wmsg = 'File {0} does not exist... skipping'
            WLOG(p, 'warning', wmsg.format(e2dsfilename))
            continue
        elif ('e2ds' not in e2dsfilename) and ('e2dsff' not in e2dsfilename):
            wmsg = 'File {0} not a valid E2DS or E2DSFF file'
            WLOG(p, 'warning', wmsg.format(e2dsfilename))
            continue
        elif '.fits' not in e2dsfilename:
            wmsg = 'File {0} not a fits file... skipping'
            WLOG(p, 'warning', wmsg.format(e2dsfilename))
            continue

        # ----------------------------------------------------------------------
        # Read image file
        # ----------------------------------------------------------------------
        # read the image data
        e2ds, hdr, nbo, nx = spirouImage.ReadData(p, e2dsfile)
        # add to loc
        loc = ParamDict()
        loc['E2DS'] = e2ds
        loc['NUMBER_ORDERS'] = nbo
        loc.set_sources(['E2DS', 'number_orders'], __NAME__ + '/main()')

        # ----------------------------------------------------------------------
        # Get basic image properties for reference file
        # ----------------------------------------------------------------------
        # get sig det value
        p = spirouImage.GetSigdet(p, hdr, name='sigdet')
        # get exposure time
        p = spirouImage.GetExpTime(p, hdr, name='exptime')
        # get gain
        p = spirouImage.GetGain(p, hdr, name='gain')
        # get acquisition time
        p = spirouImage.GetAcqTime(p, hdr, name='acqtime', kind='julian')

        # ----------------------------------------------------------------------
        # Read star parameters
        # ----------------------------------------------------------------------
        p = spirouImage.ReadParam(p, hdr, 'KW_OBJRA', dtype=str)
        p = spirouImage.ReadParam(p, hdr, 'KW_OBJDEC', dtype=str)
        p = spirouImage.ReadParam(p, hdr, 'KW_OBJEQUIN')
        p = spirouImage.ReadParam(p, hdr, 'KW_OBJRAPM')
        p = spirouImage.ReadParam(p, hdr, 'KW_OBJDECPM')
        p = spirouImage.ReadParam(p, hdr, 'KW_DATE_OBS', dtype=str)
        p = spirouImage.ReadParam(p, hdr, 'KW_UTC_OBS', dtype=str)

        # -----------------------------------------------------------------------
        #  Earth Velocity calculation
        # -----------------------------------------------------------------------
        if p['IC_IMAGE_TYPE'] == 'H4RG':
            loc = spirouImage.EarthVelocityCorrection(p, loc,
                                                      method=p['CCF_BERVMODE'])
        else:
            loc['BERV'], loc['BJD'] = 0.0, 0.0
            loc['BERV_MAX'], loc['BERV_SOURCE'] = 0.0, 'None'
            loc.set_sources(['BERV', 'BJD', 'BERV_MAX'], __NAME__ + '.main()')

        # ----------------------------------------------------------------------
        # archive ccf to fits file
        # ----------------------------------------------------------------------
        outfilename = str(e2dsfile)
        # add keys
        hdict = spirouImage.CopyOriginalKeys(hdr)

        # add berv values
        hdict = spirouImage.AddKey(p, hdict, p['KW_BERV'], value=loc['BERV'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_BJD'], value=loc['BJD'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_BERV_MAX'],
                                   value=loc['BERV_MAX'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_BERV_SOURCE'],
                                   value=loc['BERV_SOURCE'])

        # write image and add header keys (via hdict)
        p = spirouImage.WriteImage(p, outfilename, e2ds, hdict)

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
