#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
pol_spirou

Calculation of the polarimetric spectrum.

Created on 2018-06-11 at 9:42

@author: E. Martioli

Last modified: 2018-06-13 at 16:03

Up-to-date with pol_spirou AT-4
"""
from __future__ import division
import numpy as np
import os

from SpirouDRS import spirouCDB
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouStartup
from SpirouDRS import spirouImage

from SpirouDRS import spirouPOLAR

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'pol_spirou.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# Get the parameter dictionary class
ParamDict = spirouConfig.ParamDict
# Get plotting functions
sPlt = spirouCore.sPlt


# =============================================================================
# Define functions
# =============================================================================
def main(night_name=None, files=None):
    """
    pol_spirou.py main function, if night_name and files are None uses
    arguments from run time i.e.:
    pol_spirou.py [night_directory] [fitsfilename]

    :param night_name: string or None, the folder within data raw directory
                        containing files (also reduced directory) i.e.
                        /data/raw/20170710 would be "20170710" but
                        /data/raw/AT5/20180409 would be "AT5/20180409"
    :param files: string, list or None, the list of files to process
                    (if None assumes arg_file_names was set from run time)

    :return ll: dictionary, containing all the local variables defined in
                main
    """
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin()
    # get parameters from configuration files and run time arguments
    p = spirouStartup.LoadArguments(p, night_name, files,
                                    mainfitsdir='reduced')

    # set up polar storage
    polardict = ParamDict()
    # set up data storage
    loc = ParamDict()

    # ----------------------------------------------------------------------
    # Loop through files, identify and sort files and identify fiber types
    # ----------------------------------------------------------------------
    polardict = spirouPOLAR.SortPolarFiles(p, polardict)

    # ----------------------------------------------------------------------
    # Load the input polarimetry data and check if provided data are
    #    sufficient for polarimetry calculation
    # ----------------------------------------------------------------------
    loc = spirouPOLAR.LoadPolarData(p, polardict, loc)

    # ------------------------------------------------------------------
    # Read wavelength solution
    # ------------------------------------------------------------------
    loc['WAVE'] = spirouImage.ReadWaveFile(p, p['HDR'])
    loc.set_source('WAVE', __NAME__ + '/main() + /spirouImage.ReadWaveFile')

    # ----------------------------------------------------------------------
    # Polarimetry computation
    # ----------------------------------------------------------------------
    polardict = spirouPOLAR.CalculatePolarimetry(p, loc)

    # ----------------------------------------------------------------------
    # Calculate continuum (for plotting)
    # ----------------------------------------------------------------------
    loc = spirouPOLAR.CalculateContinuum(p, loc)

    # ----------------------------------------------------------------------
    # Plots
    # ----------------------------------------------------------------------
    if p['DRS_PLOT']:
        # start interactive plot
        sPlt.start_interactive_session()
        # plot continuum plots
        sPlt.polar_continuum_plot(loc)
        # plot polarimetry results
        sPlt.polar_result_plot(loc)
        # end interactive session
        sPlt.end_interactive_session()

    # ------------------------------------------------------------------
    # Store polarimetry in file(s)
    # ------------------------------------------------------------------
    # construct file names
    degpolfits = spirouConfig.Constants.DEG_POL_FILE(p, loc)
    degpolfitsname = os.path.split(degpolfits)[-1]
    nullpol1fits= spirouConfig.Constants.NULL_POL1_FILE(p, loc)
    nullpol1fitsname = os.path.split(nullpol1fits)[-1]
    nullpol2fits = spirouConfig.Constants.NULL_POL2_FILE(p, loc)
    nullpol2fitsname = os.path.split(nullpol2fits)[-1]
    # log that we are saving POL spectrum
    wmsg = 'Saving POL, NULL1, and NULL2 to {0}, {1}, {2}'
    wargs = [degpolfitsname, nullpol1fitsname, nullpol2fitsname]
    WLOG('info', p['LOG_OPT'], wmsg.format(*wargs))

    # add keys from original header of base file
    hdict = spirouImage.CopyOriginalKeys(loc['HDR'], loc['CDR'])
    # add stokes parameter keyword to header
    hdict = spirouImage.AddKey(hdict, p['KW_POL_STOKES'], value=loc['STOKES'])
    # add number of exposures parameter keyword to header
    hdict = spirouImage.AddKey(hdict, p['KW_POL_NEXP'], value=loc['NEXPOSURES'])
    # add the polarimetry method parameter keyword to header
    hdict = spirouImage.AddKey(hdict, p['KW_POL_METHOD'], value=loc['METHOD'])

    # save POL data to file
    spirouImage.WriteImage(degpolfits, loc['POL'], hdict)
    # save NULL1 data to file
    spirouImage.WriteImage(nullpol1fits, loc['NULL1'], hdict)
    # save NULL2 data to file
    spirouImage.WriteImage(nullpol2fits, loc['NULL2'], hdict)

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    wmsg = 'Recipe {0} has been successfully completed'
    WLOG('info', p['LOG_OPT'], wmsg.format(p['PROGRAM']))
    
    # return a copy of locally defined variables in the memory
    return dict(locals())

# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # run pol_spirou main
    # (get other arguments from command line - sys.argv)
    ll = main()
    # exit message if in debug mode
    spirouStartup.Exit(ll)

# =============================================================================
# End of code
# =============================================================================
