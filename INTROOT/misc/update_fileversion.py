#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-05-01 at 13:04

@author: cook
"""

from astropy.io import fits
import shutil
import os


# =============================================================================
# Define variables
# =============================================================================
#INPUTDIR = '/spirou/cfht_nights/cfht_April19/perrun'
INPUTDIR = '/spirou/cfht_nights/cfht_April19/pernight'

# -----------------------------------------------------------------------------
KEYS = dict()
KEYS['VERSION'] = 'SPIROU_0.4.120'
KEYS['PVERSION'] = 'SPIROU_0.4.120'
RKEYS = ['CRPIX1', 'CRVAL1', 'CDELT1', 'CTYPE1', 'BUNIT']


def correct_file(filename):
    if 's1dw' in filename:
        if 'tellu_corrected' in filename and 'e2dsff' in filename:
            filename = filename.replace('s1dw_', '')
            outfilename = filename.replace('e2dsff', 's1d_w')
        elif 'tellu_corrected' in filename and 'e2ds' in filename:
            filename = filename.replace('s1dw_', '')
            outfilename = filename.replace('e2ds', 's1d_w')
        else:
            outfilename = filename.replace('s1dw', 's1d_w')
    elif 's1dv' in filename:
        if 'tellu_corrected' in filename and 'e2dsff' in filename:
            filename = filename.replace('s1dv_', '')
            outfilename = filename.replace('e2dsff', 's1d_v')
        elif 'tellu_corrected' in filename and 'e2ds' in filename:
            filename = filename.replace('s1dv_', '')
            outfilename = filename.replace('e2ds', 's1d_v')
        else:
            outfilename = filename.replace('s1dw', 's1d_w')
    else:
        outfilename = filename
    return outfilename


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # walk through path
    for root, dirs, files in os.walk(INPUTDIR):
        for filename in files:
            # get output filename
            outfilename = correct_file(filename)

            if 'perrun' in root:
                root1 = root.replace('perrun', 'perrun1')
                if not os.path.exists(root1):
                    os.makedirs(root1)
            elif 'pernight' in root:
                root1 = root.replace('pernight', 'pernight1')
                if not os.path.exists(root1):
                    os.makedirs(root1)
            else:
                root1 = root
            abspath = os.path.join(root, filename)
            abspath1 = os.path.join(root1, outfilename)

            # do not change files that do not start with a number
            if not filename[0].isdigit() or not filename.endswith('.fits'):
                print('\tCopying file {0}'.format(abspath))
                shutil.copy(abspath, abspath1)
                continue
            # correct header keys
            if filename.endswith('.fits'):
                try:
                    print('Processing file {0}'.format(abspath))
                    data, header = fits.getdata(abspath, header=True)
                    for key in KEYS:
                        if key in header:
                            header[key] = KEYS[key]
                    # remove some keys from files
                    if 'tellu' in filename:
                        for key in RKEYS:
                            if key in header:
                                del header[key]
                    # write to file
                    fits.writeto(abspath1, data, header, overwrite=True)
                    print('\tWriting complete')
                except:
                    print('\tCopying file {0}'.format(abspath))
                    shutil.copy(abspath, abspath1)
                    continue


# =============================================================================
# End of code
# =============================================================================

# import os
# from astropy.io import fits
#
# RKEYS = ['CRPIX1', 'CRVAL1', 'CDELT1', 'CTYPE1', 'BUNIT']
#
# errors = []
#
# for root, dirs, files in os.walk('./'):
#     for filename in files:
#         abspath = os.path.join(root, filename)
#         if not filename.endswith('.fits'):
#             continue
#         try:
#             if 'pp_s1dv' in filename:
#                 data, header = fits.getdata(abspath, header=True)
#                 abspath1 = abspath.replace('pp_s1dv', 'pp_s1d_v')
#                 print('Processing file {0}'.format(abspath))
#                 for key in RKEYS:
#                     if key in header:
#                         del header[key]
#                 # write to file
#                 fits.writeto(abspath1, data, header, overwrite=True)
#                 print('\tWriting complete')
#                 os.remove(abspath)
#             elif 'pp_s1dw' in filename:
#                 data, header = fits.getdata(abspath, header=True)
#                 abspath1 = abspath.replace('pp_s1dw', 'pp_s1d_w')
#                 print('Processing file {0}'.format(abspath))
#                 for key in RKEYS:
#                     if key in header:
#                         del header[key]
#                 # write to file
#                 fits.writeto(abspath1, data, header, overwrite=True)
#                 print('\tWriting complete')
#                 os.remove(abspath)
#         except Exception as e:
#             errors.append([type(e), e, abspath])
#
# for error in errors:
#     print('Error {0}: {1} \n\t File={2}'.format(*error))

