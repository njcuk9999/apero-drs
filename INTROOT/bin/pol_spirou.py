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
import os

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
__args__ = ['night_name', 'files']
__required__ = [True, True]
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
    p = spirouStartup.Begin(recipe=__NAME__)
    # get parameters from configuration files and run time arguments
    p = spirouStartup.LoadArguments(p, night_name, files,
                                    mainfitsdir='reduced')
    p = spirouStartup.InitialFileSetup(p, calibdb=True)

    # ----------------------------------------------------------------------
    # Loop through files, identify and sort files and identify fiber types
    # ----------------------------------------------------------------------
    # set up polar storage
    polardict = ParamDict()
    # sort files
    polardict = spirouPOLAR.SortPolarFiles(p, polardict)
    
    # ----------------------------------------------------------------------
    # Load the input polarimetry data and check if provided data are
    #    sufficient for polarimetry calculation
    # ----------------------------------------------------------------------
    # set up data storage
    loc = ParamDict()
    # load files
    p, loc = spirouPOLAR.LoadPolarData(p, polardict, loc)
    
    # ------------------------------------------------------------------
    # Read wavelength solution
    # ------------------------------------------------------------------
    # set source of wave file
    wsource = __NAME__ + '/main() + /spirouImage.GetWaveSolution'
    # Force A and B to AB solution
    if p['FIBER'] in ['A', 'B']:
        wave_fiber = 'AB'
    else:
        wave_fiber = p['FIBER']
    # get wave image
    wout = spirouImage.GetWaveSolution(p, hdr=loc['HDR'], return_wavemap=True,
                                       return_filename=True, fiber=wave_fiber)
    _, loc['WAVE'], loc['WAVEFILE'], loc['WSOURCE'] = wout
    loc.set_sources(['WAVE', 'WAVEFILE', 'WSOURCE'], wsource)

    # ----------------------------------------------------------------------
    # Polarimetry computation
    # ----------------------------------------------------------------------
    loc = spirouPOLAR.CalculatePolarimetry(p, loc)
    
    # ----------------------------------------------------------------------
    # Stokes I computation
    # ----------------------------------------------------------------------
    loc = spirouPOLAR.CalculateStokesI(p, loc)

    # ----------------------------------------------------------------------
    # Calculate continuum (for plotting)
    # ----------------------------------------------------------------------
    loc = spirouPOLAR.CalculateContinuum(p, loc)
    
    # ----------------------------------------------------------------------
    # Plots
    # ----------------------------------------------------------------------
    if p['DRS_PLOT'] > 0:
        # start interactive plot
        sPlt.start_interactive_session(p)
        # plot continuum plots
        sPlt.polar_continuum_plot(p, loc)
        # plot polarimetry results
        sPlt.polar_result_plot(p, loc)
        # plot total flux (Stokes I)
        sPlt.polar_stokes_i_plot(p, loc)
        # end interactive session
        sPlt.end_interactive_session(p)

    # ----------------------------------------------------------------------
    # Quality control
    # ----------------------------------------------------------------------
    # set passed variable and fail message list
    passed, fail_msg = True, []
    qc_values, qc_names, qc_logic, qc_pass = [], [], [], []
    # TODO: Needs doing
    # finally log the failed messages and set QC = 1 if we pass the
    # quality control QC = 0 if we fail quality control
    if passed:
        WLOG(p, 'info', 'QUALITY CONTROL SUCCESSFUL - Well Done -')
        p['QC'] = 1
        p.set_source('QC', __NAME__ + '/main()')
    else:
        for farg in fail_msg:
            wmsg = 'QUALITY CONTROL FAILED: {0}'
            WLOG(p, 'warning', wmsg.format(farg))
        p['QC'] = 0
        p.set_source('QC', __NAME__ + '/main()')
    # add to qc header lists
    qc_values.append('None')
    qc_names.append('None')
    qc_logic.append('None')
    qc_pass.append(1)
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]

    # ------------------------------------------------------------------
    # Store polarimetry in file(s)
    # ------------------------------------------------------------------
    # construct file names
    degpolfits, tag1 = spirouConfig.Constants.DEG_POL_FILE(p, loc)
    degpolfitsname = os.path.split(degpolfits)[-1]
    stokes_ifits, tag2 = spirouConfig.Constants.STOKESI_POL_FILE(p, loc)
    stokes_ifitsname = os.path.split(stokes_ifits)[-1]
    nullpol1fits, tag3 = spirouConfig.Constants.NULL_POL1_FILE(p, loc)
    nullpol1fitsname = os.path.split(nullpol1fits)[-1]
    nullpol2fits, tag4 = spirouConfig.Constants.NULL_POL2_FILE(p, loc)
    nullpol2fitsname = os.path.split(nullpol2fits)[-1]

    # log that we are saving POL spectrum
    wmsg = 'Saving POL, STOKESI, NULL1, and NULL2 to {0}, {1}, {2}, {3}'
    wargs = [degpolfitsname, stokes_ifitsname, nullpol1fitsname,
             nullpol2fitsname]
    WLOG(p, '', wmsg.format(*wargs))

    # construct header keywords for output products
    hdict, loc = spirouPOLAR.PolarHeader(p, loc, polardict, qc_params)

    # save POL data to file
    hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag1)
    p = spirouImage.WriteImageMulti(p, degpolfits, [loc['POL'], loc['POLERR']],
                                    hdict)
    # save NULL1 data to file
    hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag3)
    p = spirouImage.WriteImage(p, nullpol1fits, loc['NULL1'], hdict)
    
    # save NULL2 data to file
    hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag4)
    p = spirouImage.WriteImage(p, nullpol2fits, loc['NULL2'], hdict)

    # add stokes parameter keyword to header
    hdict = spirouImage.AddKey(p, hdict, p['KW_POL_STOKES'], value="I")
    hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag2)
    # save STOKESI data to file
    multi_image = [loc['STOKESI'], loc['STOKESIERR']]
    p = spirouImage.WriteImageMulti(p, stokes_ifits, multi_image, hdict)

    # ------------------------------------------------------------------
    if p['IC_POLAR_LSD_ANALYSIS']:
        # ------------------------------------------------------------------
        # LSD Analysis
        # ------------------------------------------------------------------
        loc = spirouPOLAR.LSDAnalysis(p, loc)

        if p['DRS_PLOT'] > 0:
            # plot LSD analysis
            sPlt.polar_lsd_plot(p, loc)

        #  save LSD analysis data to file
        p, lsdfits, lsdfitsfitsname = spirouPOLAR.OutputLSDimage(p, loc, hdict)
        
        # log that we are saving LSD analysis data
        wmsg = 'Saving LSD analysis data to {0}'.format(lsdfitsfitsname)
        WLOG(p, '', wmsg)

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    p = spirouStartup.End(p)
    # # return a copy of locally defined variables in the memory
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
