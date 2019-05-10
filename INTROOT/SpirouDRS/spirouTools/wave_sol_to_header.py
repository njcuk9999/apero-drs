#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-12-16 at 10:51

@author: cook
"""
from __future__ import division
import os

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup
from SpirouDRS import spirouDB

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'extract_trigger.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt
# Get param dictionary
ParamDict = spirouConfig.ParamDict
# files to change
REDUCE_CODES = ['o_pp_e2ds_AB.fits', 'o_pp_e2dsff_AB.fits',
                'o_pp_e2ds_C.fits', 'o_pp_e2dsff_C.fits',
                'a_pp_e2ds_AB.fits', 'a_pp_e2dsff_AB.fits',
                'a_pp_e2ds_C.fits', 'a_pp_e2dsff_C.fits']


# =============================================================================
# Define functions
# =============================================================================
def main(night_name=None):
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    main_name = __NAME__ + '.main()'
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)
    p = spirouStartup.LoadArguments(p, night_name, require_night_name=False)
    # ----------------------------------------------------------------------
    # find all directories if night name was None (ARG_NIGHT_NAME = '')
    files, dirs = find_all_reduced_files(p)
    # ----------------------------------------------------------------------
    # loop around each file
    # ----------------------------------------------------------------------
    for it in range(len(files)):
        # get file name for this iteration
        basefilename = os.path.basename(files[it])
        # Log process
        wmsg = 'Processing file {0} ({1}/{2})'
        wargs = [basefilename, it + 1, len(files)]
        WLOG(p, 'info', wmsg.format(*wargs))
        # get this iteration values
        p['FITSFILENAME'] = files[it]
        p['ARG_NIGHT_NAME'] = dirs[it]
        p['REDUCED_DIR'] = os.path.join(p['DRS_DATA_REDUC'], dirs[it])
        p['ARG_FILE_NAMES'] = [basefilename]
        p['DRS_TYPE'] = "REDUCED"
        # identify fiber
        if '_AB.fits' in os.path.basename(files[it]):
            p['FIBER'] = 'AB'
        elif '_AB.fits' in os.path.basename(files[it]):
            p['FIBER'] = 'A'
        elif '_AB.fits' in os.path.basename(files[it]):
            p['FIBER'] = 'B'
        elif '_C.fits' in os.path.basename(files[it]):
            p['FIBER'] = 'C'
        else:
            wmsg1 = 'Wrong fiber type found. This should happen. Skipping'
            wmsg2 = '\tFile = {0}'.format(files[it])
            WLOG(p, 'warning', [wmsg1, wmsg2])
            # skip
            continue
        # set sources
        source = ['FITSFILENAME', 'ARG_NIGHT_NAME', 'REDUCED_DIR', 'FIBER',
                  'ARG_FILE_NAMES']
        p.set_sources(source, main_name)
        # define loc storage parameter dictionary
        loc = ParamDict()

        # ---------------------------------------------------------------------
        # Read image file
        # ---------------------------------------------------------------------
        # read the image data
        p, data, hdr = spirouImage.ReadImageAndCombine(p, framemath='add')

        # ---------------------------------------------------------------------
        # Load calibDB for this file
        # ---------------------------------------------------------------------
        # as we need a different calibDB for each file
        p = spirouStartup.LoadCalibDB(p, header=hdr)

        # ------------------------------------------------------------------
        # Read wavelength solution
        # ------------------------------------------------------------------
        # force reading from calibDB
        p['CALIB_DB_FORCE_WAVESOL'] = True
        p.set_source('CALIB_DB_FORCE_WAVESOL', main_name)
        # set source of wave file
        wsource = __NAME__ + '/main() + /spirouImage.GetWaveSolution'
        # Force A and B to AB solution
        if p['FIBER'] in ['A', 'B']:
            wave_fiber = 'AB'
        else:
            wave_fiber = p['FIBER']
        # get wave image
        wout = spirouImage.GetWaveSolution(p, hdr=hdr, return_wavemap=True,
                                           return_filename=True,
                                           return_header=True, fiber=wave_fiber)
        loc['WAVEPARAMS'], loc['WAVE'], loc['WAVEFILE'] = wout[:3]
        loc['WAVEHDR'], loc['WSOURCE'] = wout[3:]
        source_names = ['WAVE', 'WAVEFILE', 'WAVEPARAMS', 'WAVEHDR', 'WSOURCE']
        loc.set_sources(source_names, wsource)

        # get dates
        loc['WAVE_ACQTIMES'] = spirouDB.GetTimes(p, loc['WAVEHDR'])
        loc.set_source('WAVE_ACQTIMES', __NAME__ + '.main()')
        # get the recipe that produced the wave solution
        if 'WAVECODE' in loc['WAVEHDR']:
            loc['WAVE_CODE'] = loc['WAVEHDR']['WAVECODE']
        else:
            loc['WAVE_CODE'] = 'UNKNOWN'
        loc.set_source('WAVE_CODE', __NAME__ + '.main()')

        # ------------------------------------------------------------------
        # Save file with new header
        # ------------------------------------------------------------------
        # log that we are saving E2DS spectrum
        wmsg = 'Saving E2DS spectrum of Fiber {0} in {1}'
        WLOG(p, '', wmsg.format(p['FIBER'], basefilename))

        # add keys from original header file
        hdict = spirouImage.CopyOriginalKeys(hdr)
        # set the version
        hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_PID'], value=p['PID'])
        # set the input files
        hdict = spirouImage.AddKey(p, hdict, p['KW_CDBWAVE'],
                                   value=loc['WAVEFILE'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_WAVESOURCE'],
                                   value=loc['WSOURCE'])
        # add wave solution date
        hdict = spirouImage.AddKey(p, hdict, p['KW_WAVE_TIME1'],
                                   value=loc['WAVE_ACQTIMES'][0])
        hdict = spirouImage.AddKey(p, hdict, p['KW_WAVE_TIME2'],
                                   value=loc['WAVE_ACQTIMES'][1])
        # add wave solution number of orders
        hdict = spirouImage.AddKey(p, hdict, p['KW_WAVE_ORD_N'],
                                   value=loc['WAVEPARAMS'].shape[0])
        # add wave solution degree of fit
        hdict = spirouImage.AddKey(p, hdict, p['KW_WAVE_LL_DEG'],
                                   value=loc['WAVEPARAMS'].shape[1] - 1)
        # add wave solution coefficients
        hdict = spirouImage.AddKey2DList(p, hdict, p['KW_WAVE_PARAM'],
                                         values=loc['WAVEPARAMS'])
        # write to file
        p = spirouImage.WriteImage(p, p['FITSFILENAME'], data, hdict)
    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    p = spirouStartup.End(p, outputs=None)
    # return a copy of locally defined variables in the memory
    return dict(locals())


def find_all_reduced_files(p):
    # define path to walk around
    if p['ARG_NIGHT_NAME'] == '':
        path = p['DRS_DATA_REDUC']
    else:
        path = os.path.join(p['DRS_DATA_REDUC'], p['ARG_NIGHT_NAME'])
    # storage for raw file paths
    red_files, red_dirs = [], []
    # walk around all sub-directories
    for root, dirs, filenames in os.walk(path):
        # loop around files
        for filename in filenames:
            abs_path = os.path.join(root, filename)
            commonpath = os.path.commonpath([root, path])
            night = root.split(commonpath)[-1]
            while night.startswith('/'):
                night = night[1:]
            print(abs_path)
            for rawcode in REDUCE_CODES:
                if filename.endswith(rawcode):
                    red_files.append(abs_path)
                    red_dirs.append(night)
    # return raw files
    return red_files, red_dirs


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
