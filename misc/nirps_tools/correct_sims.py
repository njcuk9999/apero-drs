#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2020-04-20 at 10:35

@author: cook
"""
from astropy.io import fits
import glob
import os


# =============================================================================
# Define variables
# =============================================================================
WORKSPACE = '/spirou/NIRPS_nights/common/raw/SIM_APR1'

KEYS = ['SBCCAS_P', 'SBCREF_P', 'SBCALI_P', 'OBSTYPE', 'TRG_TYPE', 'EXT']

TEST = False

DPRTYPE = dict()
DPRTYPE['DARK_DARK_INT'] = 'pos_pk', 'pos_pk', 'P4', 'DARK', 'CALIBRATION', 'd.fits'
DPRTYPE['DARK_DARK_TEL'] = 'pos_pk', 'pos_pk', 'P5', 'DARK', 'CALIBRATION', 'd.fits'
DPRTYPE['DARK_DARK'] = 'pos_pk', 'pos_pk', 'P5', 'DARK', 'CALIBRATION', 'd.fits'
DPRTYPE['OBJ_DARK'] = 'pos_pk', 'pos_pk', '?', 'OBJECT', 'TARGET', 'o.fits'
DPRTYPE['DARK_DARK_SKY'] = 'pos_pk', 'pos_pk', '?', 'OBJECT', 'SKY', 'o.fits'
DPRTYPE['DARK_FP_SKY'] = 'pos_pk', 'pos_fp', '?', 'OBJECT', 'SKY', 'o.fits'
DPRTYPE['DARK_FP'] = 'pos_pk', 'pos_fp', '?', 'OBJECT', 'CALIBRATION', 'o.fits'
DPRTYPE['FP_DARK'] = 'pos_pk', 'pos_fp', '?', 'OBJECT', 'CALIBRATION', 'o.fits'
DPRTYPE['OBJ_FP'] = 'pos_pk', 'pos_fp', '?', 'OBJECT', 'TARGET', 'o.fits'
DPRTYPE['FP_FP'] = 'pos_fp', 'pos_fp', '?', 'ALIGN', 'CALIBRATION', 'a.fits'
DPRTYPE['LFC_LFC'] = 'pos_rs', 'pos_rs', '?', 'ALIGN', 'CALIBRATION', 'a.fits'
DPRTYPE['FLAT_DARK'] = 'pos_wl', 'pos_pk', '?', 'FLAT', 'CALIBRATION', 'f.fits'
DPRTYPE['DARK_FLAT'] = 'pos_pk', 'pos_wl', '?', 'FLAT', 'CALIBRATION', 'f.fits'
DPRTYPE['FLAT_FLAT'] = 'pos_wl', 'pos_wl', '?', 'FLAT', 'CALIBRATION', 'f.fits'
DPRTYPE['HCONE_DARK'] = 'pos_hc1', 'pos_pk', '?', 'COMPARISON', 'CALIBRATION', 'c.fits'
DPRTYPE['HC_DARK'] = 'pos_hc1', 'pos_pk', '?', 'COMPARISON', 'CALIBRATION', 'c.fits'
DPRTYPE['HCTWO_DARK'] = 'pos_hc2', 'pos_pk', '?', 'COMPARISON', 'CALIBRATION', 'c.fits'
DPRTYPE['FP_HCONE'] = 'pos_fp', 'pos_hc1', '?', 'COMPARISON', 'CALIBRATION', 'c.fits'
DPRTYPE['FP_HC'] = 'pos_fp', 'pos_hc1', '?', 'COMPARISON', 'CALIBRATION', 'c.fits'
DPRTYPE['FP_HCTWO'] = 'pos_fp', 'pos_hc2', '?', 'COMPARISON', 'CALIBRATION', 'c.fits'
DPRTYPE['HCONE_FP'] = 'pos_hc1', 'pos_fp', '?', 'COMPARISON', 'CALIBRATION', 'c.fits'
DPRTYPE['HC_FP'] = 'pos_hc1', 'pos_fp', '?', 'COMPARISON', 'CALIBRATION', 'c.fits'
DPRTYPE['HCTWO_FP'] = 'pos_hc2', 'pos_fp', '?', 'COMPARISON', 'CALIBRATION', 'c.fits'
DPRTYPE['DARK_HCONE'] = 'pos_pk', 'pos_hc1', '?', 'COMPARISON', 'CALIBRATION', 'c.fits'
DPRTYPE['DARK_HC'] = 'pos_pk', 'pos_hc1', '?', 'COMPARISON', 'CALIBRATION', 'c.fits'
DPRTYPE['DARK_HCTWO'] = 'pos_pk', 'pos_hc2', '?', 'COMPARISON', 'CALIBRATION', 'c.fits'
DPRTYPE['HCONE_HCONE'] = 'pos_hc1', 'pos_hc1', '?', 'COMPARISON', 'CALIBRATION', 'c.fits'
DPRTYPE['HC_HC'] = 'pos_hc1', 'pos_hc1', '?', 'COMPARISON', 'CALIBRATION', 'c.fits'
DPRTYPE['HCTWO_HCTWO'] = 'pos_hc2', 'pos_hc2', '?', 'COMPARISON', 'CALIBRATION', 'c.fits'




# =============================================================================
# Define functions
# =============================================================================
def id_file(filename, dprtypes):
    for dprtype in dprtypes:
        # find file
        if dprtype.upper() in filename:
            return dprtype.upper()
    return None


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # load files
    files = np.sort(glob.glob(WORKSPACE  +'/*.fits'))
    # loop around files
    for filename in files:
        # get file basename
        basename = os.path.basename(filename)
        # id file
        dprtype = id_file(filename, list(DPRTYPE.keys()))
        # deal with dprtype
        if dprtype is None:
            print('ERROR: Cannot id file: {0}'.format(basename))
            continue
        else:
            print('\nProcessing {0} file: {1}'.format(dprtype, basename))
        # open fits file
        hdulist = fits.open(filename)
        # get primary header
        header = hdulist[0].header
        # assume file is correct
        correct = True
        # loop through keys
        for kit, key in enumerate(KEYS):
            if key in header:
                # check if value is correct
                if header[key] == DPRTYPE[dprtype][kit]:
                    continue
                else:
                    correct = False
                # deal with test or update of value
                if TEST and not correct:
                    args = [key, header[key], DPRTYPE[dprtype][kit]]
                    print('\t{0:8s}: {1} --> {2}'.format(*args))
                else:
                    header[key] = DPRTYPE[dprtype][kit]
        # if correct continue
        if correct or TEST:
            hdulist.close()
            continue
        # add back to file
        hdulist[0].header = header
        # save file
        hdulist.writeto(filename, overwrite=True)
        # close fits file
        hdulist.close()




# =============================================================================
# End of code
# =============================================================================
