#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cal_preprocess_spirou [night_name] [files]

Rotation of the H4RG fits files

Created on 2018-04-13 at 17:20

@author: melissa-hobson
"""
from __future__ import division
import numpy as np
import os

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouStartup
from SpirouDRS import spirouImage
from SpirouDRS.spirouImage import spirouFile

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_preprocess_spirou.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
__args__ = ['night_name', 'ufiles']
__required__ = [True, True]
# Get Logging function
WLOG = spirouCore.wlog
# Get Path Exception
PathException = spirouFile.PathException


# =============================================================================
# Define functions
# =============================================================================
def main(night_name=None, ufiles=None):
    """
    cal_preprocess_spirou.py main function, if night_name and files are
    None uses arguments from run time i.e.:
        cal_preprocess_spirou.py [night_directory] [fitsfilename]

    :param night_name: string or None, the folder within data raw directory
                                containing files (also reduced directory) i.e.
                                /data/raw/20170710 would be "20170710" but
                                /data/raw/AT5/20180409 would be "AT5/20180409"
    :param ufiles: string, list or None, the list of files to process
                  Note can include wildcard i.e. "*.fits"
                  (if None assumes arg_file_names was set from run time)

    :return ll: dictionary, containing all the local variables defined in
                main
    """
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)
    # need custom args (to accept full path or wild card
    if ufiles is None:
        names, types = ['ufiles'], [str]
        customargs = spirouStartup.GetCustomFromRuntime(p, [0], types, names,
                                                        last_multi=True)
    else:
        customargs = dict(ufiles=ufiles)
    # get parameters from configuration files and run time arguments
    p = spirouStartup.LoadArguments(p, night_name, customargs=customargs,
                                    mainfitsdir='raw')

    # ----------------------------------------------------------------------
    # Get hot pixels for corruption check
    # ----------------------------------------------------------------------
    hotpixels = spirouImage.PPGetHotPixels(p)

    # ----------------------------------------------------------------------
    # Process files (including wildcards)
    # ----------------------------------------------------------------------
    # get raw folder (assume all files are in the root directory)
    rawdir = spirouConfig.Constants.RAW_DIR(p)
    try:
        ufiles = spirouFile.Paths(p['UFILES'], root=rawdir).abs_paths
    except PathException as e:
        WLOG(p, 'error', e)

    # log how many files were found
    wmsg = '{0} files found'
    WLOG(p, '', wmsg.format(len(ufiles)))

    # storage for output files
    p['OUTPUT_NAMES'] = []
    p.set_source('OUTPUT_NAMES', __NAME__ + '.main()')

    # loop around files
    for u_it, ufile in enumerate(ufiles):
        # log the file process
        wmsg = 'Processing file {0} ({1} of {2})'
        WLOG(p, '', spirouStartup.spirouStartup.HEADER)
        bfilename = os.path.basename(ufile)
        WLOG(p, 'info', wmsg.format(bfilename, u_it+1, len(ufiles)))
        WLOG(p, '', spirouStartup.spirouStartup.HEADER)

        # ------------------------------------------------------------------
        # Check that we can process file
        # ------------------------------------------------------------------
        # check if ufile exists
        if not os.path.exists(ufile):
            wmsg = 'File {0} does not exist... skipping'
            WLOG(p, 'warning', wmsg.format(ufile))
            continue
        # skip processed files
        elif p['PROCESSED_SUFFIX'] in bfilename:
            wmsg = 'File {0} has been processed... skipping'
            WLOG(p, 'warning', wmsg.format(ufile))
            continue
        # skip non-fits files
        elif '.fits' not in bfilename:
            wmsg = 'File {0} not a fits file... skipping'
            WLOG(p, 'warning', wmsg.format(ufile))
            continue
        # skip index file
        elif bfilename == spirouConfig.Constants.INDEX_OUTPUT_FILENAME():
            wmsg = 'Skipping index fits file'
            WLOG(p, 'warning', wmsg.format(ufile))
            continue

        # ------------------------------------------------------------------
        # Read image file
        # ------------------------------------------------------------------
        # read the image data
        rout = spirouImage.ReadImage(p, filename=ufile)
        image, hdr, nx, ny = rout

        # ------------------------------------------------------------------
        # Identify file (and update filename, header and comments)
        # ------------------------------------------------------------------
        ufile, hdr = spirouImage.IdentifyUnProFile(p, ufile, hdr)

        # ------------------------------------------------------------------
        # correct image
        # ------------------------------------------------------------------
        # correct for the top and bottom reference pixels
        WLOG(p, '', 'Correcting for top and bottom pixels')
        image = spirouImage.PPCorrectTopBottom(p, image)

        # correct by a median filter from the dark amplifiers
        wmsg = 'Correcting by the median filter from dark amplifiers'
        WLOG(p, '', wmsg)
        image = spirouImage.PPMedianFilterDarkAmps(p, image)

        # correct for the 1/f noise
        wmsg = 'Correcting for the 1/f noise'
        WLOG(p, '', wmsg)
        image = spirouImage.PPMedianOneOverfNoise2(p, image)

        # ------------------------------------------------------------------
        # Quality control to check for corrupt files
        # ------------------------------------------------------------------
        # set passed variable and fail message list
        passed, fail_msg = True, []
        qc_values, qc_names, qc_logic, qc_pass = [], [], [], []
        # ----------------------------------------------------------------------
        # get pass condition
        cout = spirouImage.PPTestForCorruptFile(p, image, hotpixels)
        snr_hotpix, rms_list = cout
        # print out SNR hotpix value
        wmsg = 'Corruption check: SNR Hotpix value = {0:.5e}'
        WLOG(p, '', wmsg.format(snr_hotpix))
        #deal with printing corruption message
        if snr_hotpix < p['PP_CORRUPT_SNR_HOTPIX']:
            # add failed message to fail message list
            fargs = [snr_hotpix, p['PP_CORRUPT_SNR_HOTPIX'],ufile ]
            fmsg = ('File was found to be corrupted. (SNR_HOTPIX < threshold, '
                    '{0:.4e} < {1:.4e}). File will not be saved. '
                    'File = {2}'.format(*fargs))
            fail_msg.append(fmsg)
            passed = False
            qc_pass.append(0)
        else:
            qc_pass.append(1)
        # add to qc header lists
        qc_values.append(snr_hotpix)
        qc_names.append('snr_hotpix')
        qc_logic.append('snr_hotpix < {0:.5e}'
                        ''.format(p['PP_CORRUPT_SNR_HOTPIX']))
        # ----------------------------------------------------------------------
        if np.max(rms_list) > p['PP_CORRUPT_RMS_THRES']:
            # add failed message to fail message list
            fargs = [np.max(rms_list), p['PP_CORRUPT_RMS_THRES'], ufile]
            fmsg = ('File was found to be corrupted. (RMS < threshold, '
                    '{0:.4e} > {1:.4e}). File will not be saved. '
                    'File = {0}'.format(*fargs))
            fail_msg.append(fmsg)
            passed = False
            qc_pass.append(0)
        else:
            qc_pass.append(1)
        # add to qc header lists
        qc_values.append(np.max(rms_list))
        qc_names.append('max(rms_list)')
        qc_logic.append('max(rms_list) > {0:.4e}'
                        ''.format(p['PP_CORRUPT_RMS_THRES']))
        # ----------------------------------------------------------------------
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
            WLOG(p, 'warning', '\tFile not written')
            continue
        # store in qc_params
        qc_params = [qc_names, qc_values, qc_logic, qc_pass]

        # ------------------------------------------------------------------
        # rotate image
        # ------------------------------------------------------------------
        # rotation to match HARPS orientation (expected by DRS)
        image = spirouImage.RotateImage(image, p['RAW_TO_PP_ROTATION'])

        # ------------------------------------------------------------------
        # Save rotated image
        # ------------------------------------------------------------------
        # construct rotated file name
        outfits = spirouConfig.Constants.PP_FILE(p, bfilename)
        outfitsname = os.path.basename(outfits)
        # log that we are saving rotated image
        WLOG(p, '', 'Saving Rotated Image in ' + outfitsname)
        # add keys from original header file
        hdict = spirouImage.CopyOriginalKeys(hdr)

        # set the version
        hdict = spirouImage.AddKey(p, hdict, p['KW_PPVERSION'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_PID'], value=p['PID'])
        # set the inputs
        hdict = spirouImage.AddKey1DList(p, hdict, p['KW_INFILE1'],
                                         dim1name='file',
                                         values=[os.path.basename(ufile)])
        # add qc parameters
        hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_QC'], value=p['QC'])
        hdict = spirouImage.AddKey1DList(p, hdict, p['KW_DRS_QC_NAME'],
                                         values=qc_names)
        hdict = spirouImage.AddQCKeys(p, hdict, qc_params)

        # set the DRS type (for file indexing)
        p['DRS_TYPE'] = 'RAW'
        p.set_source('DRS_TYPE', __NAME__ + '.main()')

        # write to file
        p = spirouImage.WriteImage(p, outfits, image, hdict)

        # index this file
        p = spirouStartup.End(p, outputs='pp', end=False)

        # ------------------------------------------------------------------
        # append to output storage in p
        # ------------------------------------------------------------------
        p['OUTPUT_NAMES'].append(outfitsname)

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    p = spirouStartup.End(p, outputs=None)
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
