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
    # get wave image
    wout = spirouImage.GetWaveSolution(p, hdr=loc['HDR'], return_wavemap=True)
    _, loc['WAVE'] = wout
    loc.set_source('WAVE', wsource)

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
    if p['DRS_PLOT']:
        # start interactive plot
        sPlt.start_interactive_session()
        # plot continuum plots
        sPlt.polar_continuum_plot(loc)
        # plot polarimetry results
        sPlt.polar_result_plot(loc)
        # plot total flux (Stokes I)
        sPlt.polar_stokesI_plot(loc)
        # end interactive session
        sPlt.end_interactive_session()
    
    # ------------------------------------------------------------------
    # Store polarimetry in file(s)
    # ------------------------------------------------------------------
    # construct file names
    degpolfits, tag1 = spirouConfig.Constants.DEG_POL_FILE(p, loc)
    degpolfitsname = os.path.split(degpolfits)[-1]
    stokesIfits, tag2 = spirouConfig.Constants.STOKESI_POL_FILE(p, loc)
    stokesIfitsname = os.path.split(stokesIfits)[-1]
    nullpol1fits, tag3 = spirouConfig.Constants.NULL_POL1_FILE(p, loc)
    nullpol1fitsname = os.path.split(nullpol1fits)[-1]
    nullpol2fits, tag4 = spirouConfig.Constants.NULL_POL2_FILE(p, loc)
    nullpol2fitsname = os.path.split(nullpol2fits)[-1]

    # log that we are saving POL spectrum
    wmsg = 'Saving POL, STOKESI, NULL1, and NULL2 to {0}, {1}, {2}, {3}'
    wargs = [degpolfitsname, stokesIfitsname, nullpol1fitsname,
             nullpol2fitsname]
    WLOG('info', p['LOG_OPT'], wmsg.format(*wargs))

    # add keys from original header of base file
    hdict = spirouImage.CopyOriginalKeys(loc['HDR'], loc['CDR'])
    # add version number
    hdict = spirouImage.AddKey(hdict, p['KW_VERSION'])
    # add stokes parameter keyword to header
    hdict = spirouImage.AddKey(hdict, p['kw_POL_STOKES'], value=loc['STOKES'])
    # add number of exposures parameter keyword to header
    hdict = spirouImage.AddKey(hdict, p['kw_POL_NEXP'], value=loc['NEXPOSURES'])
    # add the polarimetry method parameter keyword to header
    hdict = spirouImage.AddKey(hdict, p['kw_POL_METHOD'], value=loc['METHOD'])
    
    meanbjd, tot_exptime = 0.0, 0.0
    bjd_first, bjd_last, exptime_last = 0.0, 0.0, 0.0
    berv_first, berv_last = 0.0, 0.0
    
    # loop over files in polar sequence to add keywords to header of products
    for filename in polardict.keys():
        # get this entry
        entry = polardict[filename]
        # get expnum, fiber, and header
        expnum, fiber, hdr = entry['exposure'], entry['fiber'], entry['hdr']
        # Add only times from fiber A
        if fiber == 'A':
            
            # calcualte total exposure time
            tot_exptime += hdr['EXPTIME']
            # get values for BJDCEN calculation
            if expnum == 1:
                bjd_first = hdr['BJD']
                berv_first = hdr['BERV']
            elif expnum == loc['NEXPOSURES']:
                bjd_last = hdr['BJD']
                berv_last = hdr['BERV']
                exptime_last = hdr['EXPTIME']
            meanbjd += hdr['BJD']
            # add exposure file name
            fileexp = p['kw_POL_FILENAM{0}'.format(expnum)]
            hdict = spirouImage.AddKey(hdict, fileexp, value=hdr['FILENAME'])
            # add EXPTIME for each exposure
            exptimeexp = p['kw_POL_EXPTIME{0}'.format(expnum)]
            hdict = spirouImage.AddKey(hdict, exptimeexp, value=hdr['EXPTIME'])
            # add MJDATE for each exposure
            mjdexp = p['kw_POL_MJDATE{0}'.format(expnum)]
            hdict = spirouImage.AddKey(hdict, mjdexp, value=hdr['MJDATE'])
            # add MJDEND for each exposure
            mjdendexp = p['kw_POL_MJDEND{0}'.format(expnum)]
            hdict = spirouImage.AddKey(hdict, mjdendexp, value=hdr['MJDEND'])
            # add BJD for each exposure
            bjdexp = p['kw_POL_BJD{0}'.format(expnum)]
            hdict = spirouImage.AddKey(hdict, bjdexp, value=hdr['BJD'])
            # add BERV for each exposure
            bervexp = p['kw_POL_BERV{0}'.format(expnum)]
            hdict = spirouImage.AddKey(hdict, bervexp, value=hdr['BERV'])

    # add total exposure time parameter keyword to header
    hdict = spirouImage.AddKey(hdict, p['kw_POL_EXPTIME'], value=tot_exptime)
    # add elapsed time parameter keyword to header
    elapsed_time = (bjd_last - bjd_first) * 86400. + exptime_last
    hdict = spirouImage.AddKey(hdict, p['kw_POL_ELAPTIME'], value=elapsed_time)
    
    # calculate BJD at center of polarimetric sequence
    bjdcen = bjd_first + (bjd_last - bjd_first + exptime_last/86400.)/2.0
    # add central BJD
    hdict = spirouImage.AddKey(hdict, p['kw_POL_BJDCEN'], value=bjdcen)

    # calculate BERV at center by linear interpolation
    berv_slope = (berv_last - berv_first) / (bjd_last - bjd_first)
    berv_intercept = berv_first - berv_slope * bjd_first
    loc['BERVCEN'] = berv_intercept + berv_slope * bjdcen
    
    # add central BERV
    hdict = spirouImage.AddKey(hdict, p['kw_POL_BERVCEN'], value=loc['BERVCEN'])

    # add mean BJD
    meanbjd = meanbjd / loc['NEXPOSURES']
    hdict = spirouImage.AddKey(hdict, p['kw_POL_MEANBJD'], value=meanbjd)

    # save POL data to file
    hdict = spirouImage.AddKey(hdict, p['KW_OUTPUT'], value=tag1)
    p = spirouImage.WriteImageMulti(p, degpolfits, [loc['POL'], loc['POLERR']],
                                    hdict)
    # save NULL1 data to file
    hdict = spirouImage.AddKey(hdict, p['KW_OUTPUT'], value=tag3)
    p = spirouImage.WriteImage(p, nullpol1fits, loc['NULL1'], hdict)
    # save NULL2 data to file
    hdict = spirouImage.AddKey(hdict, p['KW_OUTPUT'], value=tag4)
    p = spirouImage.WriteImage(p, nullpol2fits, loc['NULL2'], hdict)

    # add stokes parameter keyword to header
    hdict = spirouImage.AddKey(hdict, p['KW_POL_STOKES'], value="I")
    hdict = spirouImage.AddKey(hdict, p['KW_OUTPUT'], value=tag2)
    # save STOKESI data to file
    multi_image = [loc['STOKESI'], loc['STOKESIERR']]
    p = spirouImage.WriteImageMulti(p, stokesIfits, multi_image, hdict)

    # ------------------------------------------------------------------
    if p['IC_POLAR_LSD_ANALYSIS']:
        # ------------------------------------------------------------------
        # LSD Analysis
        # ------------------------------------------------------------------
        loc = spirouPOLAR.LSDAnalysis(p, loc)

        if p['DRS_PLOT']:
            # plot LSD analysis
            sPlt.polar_lsd_plot(loc)

        #  save LSD analysis data to file
        p, lsdfits, lsdfitsfitsname = spirouPOLAR.OutputLSDimage(p, loc, hdict)
        
        # log that we are saving LSD analysis data
        wmsg = 'Saving LSD analysis data to {0}'.format(lsdfitsfitsname)
        WLOG('info', p['LOG_OPT'], wmsg)

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
