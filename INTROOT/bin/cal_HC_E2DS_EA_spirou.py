#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cal_HC_E2DS_spirou.py [night_directory] [fitsfilename]

Wavelength calibration

Created on 2018-08-28

@author: artigau, hobson, cook
"""
from __future__ import division
import numpy as np
import os

from SpirouDRS import spirouDB
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouFLAT
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup
from SpirouDRS import spirouTHORCA
from SpirouDRS.spirouTHORCA import spirouWAVE


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_HC_E2DS_spirou.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt
# Get parameter dictionary
ParamDict = spirouConfig.ParamDict


# =============================================================================
# Define functions
# =============================================================================

if __name__ == '__main__':
    import sys
    sys.argv = 'cal_HC_E2DS_EA_spirou.py AT5/20180409 hcone_hcone_001_pp_e2ds_AB.fits'.split()
    night_name, files = None, None
    """
    cal_HC_E2DS.py main function, if night_name and files are None uses
    arguments from run time i.e.:
        cal_DARK_spirou.py [night_directory] [fitsfilename]

    :param night_name: string or None, the folder within data raw directory
                                containing files (also reduced directory) i.e.
                                /data/raw/20170710 would be "20170710" but
                                /data/raw/AT5/20180409 would be "AT5/20180409"
    :param files: string, list or None, the list of files to use for
                  arg_file_names and fitsfilename
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
    p = spirouStartup.LoadArguments(p, night_name, files, mainfitsdir='reduced')
    # setup files and get fiber
    p = spirouStartup.InitialFileSetup(p, calibdb=True)
    # set the fiber type
    p['FIB_TYP'] = [p['FIBER']]
    p.set_source('FIB_TYP', __NAME__ + '/main()')

    # TODO: Add to constants file
    # ===============================
    # Add to constant file
    # ===============================
    # whether to do plot per order (very slow + interactive)
    p['HC_EA_PLOT_PER_ORDER'] = False
    # width of the box for fitting HC lines. Lines will be fitted
    #     from -W to +W, so a 2*W+1 window
    p['HC_FITTING_BOX_SIZE'] = 6
    # number of sigma above local RMS for a line to be flagged as such
    p['HC_FITTING_BOX_SIGMA'] = 2.0
    # the fit degree for the gaussian fit
    p['HC_FITTING_BOX_GFIT_TYPE'] = 5
    # the RMS of line-fitted line must be before 0 and 0.2 of the peak value
    #     must be SNR>5 (or 1/SNR<0.2)
    p['HC_FITTINGBOX_RMS_DEVMIN'] = 0
    p['HC_FITTINGBOX_RMS_DEVMAX'] = 0.2
    # the e-width of the line expressed in pixels.
    p['HC_FITTINGBOX_EW_MIN'] = 0.7
    p['HC_FITTINGBOX_EW_MAX'] = 1.1
    # number of bright lines kept per order
    #     avoid >25 as it takes super long
    #     avoid <12 as some orders are ill-defined and we need >10 valid
    #         lines anyway
    #     20 is a good number, and I see now reason to change it
    p['HC_NMAX_BRIGHT'] = 20
    # Number of times to run the fit triplet algorithm
    p['HC_NITER_FIT_TRIPLET'] = 3
    # Maximum distance between catalog line and init guess line to accept line
    #    in m/s
    p['HC_MAX_DV_CAT_GUESS'] = 60000
    # The fit degree between triplets
    p['HC_TFIT_DEG'] = 2
    # Cut threshold for the triplet line fit [in km/s]
    p['HC_TFIT_CUT_THRES'] = 1.0
    # Minimum number of lines required per order
    p['HC_TFIT_MIN_NUM_LINES'] = 10
    # Minimum total number of lines required
    p['HC_TFIT_MIN_TOT_LINES'] = 200

    # this sets the order of the polynomial used to ensure continuity in the xpix vs wave solutions
    # by setting the first term = 12, we force that the zeroth element of the xpix of the wavelegnth
    # grid is fitted with a 12th order polynomial as a function of order number
    p['HC_TFIT_ORDER_FIT_CONTINUITY'] = [12, 9, 6, 2, 2]

    # Number of times to loop through the sigma clip
    p['HC_TFIT_SIGCLIP_NUM'] = 20
    # Sigma clip threshold
    p['HC_TFIT_SIGCLIP_THRES'] = 3.5

    # quality control criteria if sigma greater than this many sigma fails
    p['QC_HC_WAVE_SIGMA_MAX'] = 8

    # TODO: Add to constants file


    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read and combine all files
    p, hcdata, hchdr, hccdr = spirouImage.ReadImageAndCombine(p, 'add')
    # add data and hdr to loc
    loc = ParamDict()
    loc['HCDATA'], loc['HCHDR'], loc['HCCDR'] = hcdata, hchdr, hccdr
    # set the source
    sources = ['HCDATA', 'HCHDR', 'HCCDR']
    loc.set_sources(sources, 'spirouImage.ReadImageAndCombine()')

    # ----------------------------------------------------------------------
    # Get basic parameters
    # ----------------------------------------------------------------------
    # get sig det value
    p = spirouImage.GetSigdet(p, loc['HCHDR'], name='sigdet')
    # get exposure time
    p = spirouImage.GetExpTime(p, loc['HCHDR'], name='exptime')
    # get gain
    p = spirouImage.GetGain(p, loc['HCHDR'], name='gain')
    # get acquisition time
    p = spirouImage.GetAcqTime(p, loc['HCHDR'], name='acqtime', kind='julian')
    bjdref = p['ACQTIME']
    # set sigdet and conad keywords (sigdet is changed later)
    p['KW_CCD_SIGDET'][1] = p['SIGDET']
    p['KW_CCD_CONAD'][1] = p['GAIN']
    # get lamp parameters
    p = spirouTHORCA.GetLampParams(p, loc['HCHDR'])

    # get number of orders
    # we always get fibre A number because AB is doubled in constants file
    loc['NBO'] = p['QC_LOC_NBO_FPALL']['A']
    loc.set_source('NBO', __NAME__ + '.main()')
    # get number of pixels in x from hcdata size
    loc['NBPIX'] = loc['HCDATA'].shape[1]
    loc.set_source('NBPIX', __NAME__ + '.main()')

    # ----------------------------------------------------------------------
    # Read blaze
    # ----------------------------------------------------------------------
    # get tilts
    loc['BLAZE'] = spirouImage.ReadBlazeFile(p, hchdr)
    loc.set_source('BLAZE', __NAME__ + '/main() + /spirouImage.ReadBlazeFile')

    # ----------------------------------------------------------------------
    # Read wave solution
    # ----------------------------------------------------------------------
    # wavelength file; we will use the polynomial terms in its header,
    # NOT the pixel values that would need to be interpolated
    # getting header info with wavelength polynomials
    wdata = spirouImage.ReadWaveFile(p, hchdr, return_header=True)
    wave, wave_hdr = wdata
    loc['WAVE_INIT'] = wave
    loc['WAVEHDR'] = wave_hdr
    loc.set_source('WAVE_INIT',
                   __NAME__ + '/main() + /spirouImage.ReadWaveFile')
    # get wave params from wave header
    poly_wave_sol = spirouImage.ReadWaveParams(p, wave_hdr)
    loc['WAVEPARAMS'] = poly_wave_sol
    loc.set_source('WAVEPARAMS', 'spirouImage.ReadWaveFile')

    # ----------------------------------------------------------------------
    # Read UNe solution
    # ----------------------------------------------------------------------
    wave_UNe, amp_UNe = spirouImage.ReadLineList(p)
    loc['LL_LINE'], loc['AMPL_LINE'] = wave_UNe, amp_UNe
    source = __NAME__ + '.main() + spirouImage.ReadLineList()'
    loc.set_sources(['ll_line', 'ampl_line'], source)

    # ----------------------------------------------------------------------
    # Generate wave map from wave solution
    # ----------------------------------------------------------------------
    loc = spirouWAVE.generate_wave_map(p, loc)

    # ----------------------------------------------------------------------
    # Find Gaussian Peaks in HC spectrum
    # ----------------------------------------------------------------------
    loc = spirouWAVE.find_hc_gauss_peaks(p, loc)

    # ----------------------------------------------------------------------
    # Start plotting session
    # ----------------------------------------------------------------------
    if p['DRS_PLOT']:
        # start interactive plot
        sPlt.start_interactive_session()

    # ----------------------------------------------------------------------
    # Fit Gaussian peaks (in triplets) to
    # ----------------------------------------------------------------------
    loc = spirouWAVE.fit_gaussian_triplets(p, loc)

    # ----------------------------------------------------------------------
    # End plotting session
    # ----------------------------------------------------------------------
    # end interactive session
    if p['DRS_PLOT']:
        sPlt.end_interactive_session()

    # ----------------------------------------------------------------------
    # Quality control
    # ----------------------------------------------------------------------
    passed, fail_msg = True, []
    # quality control on sigma clip (sig1 > qc_hc_wave_sigma_max
    if loc['SIG1'] > p['QC_HC_WAVE_SIGMA_MAX']:
        fmsg = 'Sigma too high ({0:.5f} > {1:.5f})'
        fail_msg.append(fmsg.format(loc['SIG1'], p['QC_HC_WAVE_SIGMA_MAX']))
        passed = False
    # finally log the failed messages and set QC = 1 if we pass the
    # quality control QC = 0 if we fail quality control
    if passed:
        WLOG('info', p['LOG_OPT'], 'QUALITY CONTROL SUCCESSFUL - Well Done -')
        p['QC'] = 1
        p.set_source('QC', __NAME__ + '/main()')
    else:
        for farg in fail_msg:
            wmsg = 'QUALITY CONTROL FAILED: {0}'
            WLOG('warning', p['LOG_OPT'], wmsg.format(farg))
        p['QC'] = 0
        p.set_source('QC', __NAME__ + '/main()')

    # ----------------------------------------------------------------------
    # Generate Resolution map and line profiles
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Save wave map to file
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Update calibDB
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Update header of current file
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    p = spirouStartup.End(p)

def main(night_name=None, files=None):
    # return a copy of locally defined variables in the memory
    return dict(locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()
    # exit message if in debug mode
    spirouStartup.Exit(ll)

# =============================================================================
# End of code
# =============================================================================
