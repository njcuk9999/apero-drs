#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2020-01-24 at 11:55

@author: cook
"""
import numpy as np
from astropy.io import fits
import os
import matplotlib.pyplot as plt


# =============================================================================
# Define variables
# =============================================================================
WORKSPACE = '/scratch2/spirou/test_data/reduced'

file1 = '2400409a_pp_e2dsff_AB.fits'
night1 = '2019-04-20'

file2 = '2425831a_pp_e2dsff_AB.fits'
night2 = '2019-06-15'

LOC_FILE_HEADER_KEY = 'CDBLOCO'
ORDERP_FILE_HEADER_KEY = 'CDBORDP'
FLAT_FILE_HEADER_KEY = 'CDBFLAT'
BLAZE_FILE_HEADER_KEY = 'CDBBLAZE'

SHAPE_DX_HEADER_KEY = 'SHAPE_DX'
SHAPE_DY_HEADER_KEY = 'SHAPE_DY'
SHAPE_A_HEADER_KEY = 'SHAPE_A'
SHAPE_B_HEADER_KEY = 'SHAPE_B'
SHAPE_C_HEADER_KEY = 'SHAPE_C'
SHAPE_D_HEADER_KEY = 'SHAPE_D'


# =============================================================================
# Define functions
# =============================================================================
def loc_compare(header1, header2, path1, path2):
    # get keys from headers
    loco1 = _get_key(LOC_FILE_HEADER_KEY, header1)
    loco2 = _get_key(LOC_FILE_HEADER_KEY, header2)
    # check if we have both files
    if loco1 is None or loco2 is None:
        return 0
    # load files
    try:
        data1 = fits.getdata(os.path.join(path1, loco1))
        data2 = fits.getdata(os.path.join(path2, loco2))
    except Exception as e:
        print('Error {0}: {1}'.format(type(e), e))
        return 0
    # plot
    fig, frames = plt.subplots(ncols=1, nrows=2)
    frames[0] = _diff_image_axis(frames[0], data1, data2, axis=0)
    frames[1] = _diff_image(frames[1], data1, data2)
    fig.suptitle('Localisation Comparison')


def orderp_compare(header1, header2, path1, path2):
    # get keys from headers
    orderp1 = _get_key(ORDERP_FILE_HEADER_KEY, header1)
    orderp2 = _get_key(ORDERP_FILE_HEADER_KEY, header2)
    # check if we have both files
    if orderp1 is None or orderp2 is None:
        return 0
        # load files
    try:
        data1 = fits.getdata(os.path.join(path1, orderp1))
        data2 = fits.getdata(os.path.join(path2, orderp2))
    except Exception as e:
        print('Error {0}: {1}'.format(type(e), e))
        return 0
    # plot
    fig, frame = plt.subplots(ncols=1, nrows=1)
    _ = _diff_image(frame, data1, data2)
    fig.suptitle('Order Profile Comparison')


def flat_compare(header1, header2, path1, path2):
    # get keys from headers
    flat1 = _get_key(FLAT_FILE_HEADER_KEY, header1)
    flat2 = _get_key(FLAT_FILE_HEADER_KEY, header2)
    # check if we have both files
    if flat1 is None or flat2 is None:
        return 0
        # load files
    try:
        data1 = fits.getdata(os.path.join(path1, flat1))
        data2 = fits.getdata(os.path.join(path2, flat2))
    except Exception as e:
        print('Error {0}: {1}'.format(type(e), e))
        return 0
    # plot
    fig, frame = plt.subplots(ncols=1, nrows=1)
    _ = _diff_image(frame, data1, data2)
    fig.suptitle('Flat Comparison')


def blaze_compare(header1, header2, path1, path2):
    # get keys from headers
    blaze1 = _get_key(BLAZE_FILE_HEADER_KEY, header1)
    blaze2 = _get_key(BLAZE_FILE_HEADER_KEY, header2)
    # check if we have both files
    if blaze1 is None or blaze2 is None:
        return 0
        # load files
    try:
        data1 = fits.getdata(os.path.join(path1, blaze1))
        data2 = fits.getdata(os.path.join(path2, blaze2))
    except Exception as e:
        print('Error {0}: {1}'.format(type(e), e))
        return 0
    # plot
    fig, frame = plt.subplots(ncols=1, nrows=1)
    _ = _diff_image(frame, data1, data2)
    fig.suptitle('Blaze Comparison')


def shape_compare(header1, header2):
    # get keys from headers
    shape_dx1 = _get_key(SHAPE_DX_HEADER_KEY, header1)
    shape_dx2 = _get_key(SHAPE_DX_HEADER_KEY, header2)
    if shape_dx1 is None or shape_dx2 is None:
        return 0
    # get other keys
    shape_dy1 = _get_key(SHAPE_DY_HEADER_KEY, header1)
    shape_dy2 = _get_key(SHAPE_DY_HEADER_KEY, header2)
    shape_a1 = _get_key(SHAPE_A_HEADER_KEY, header1)
    shape_a2 = _get_key(SHAPE_A_HEADER_KEY, header2)
    shape_b1 = _get_key(SHAPE_B_HEADER_KEY, header1)
    shape_b2 = _get_key(SHAPE_B_HEADER_KEY, header2)
    shape_c1 = _get_key(SHAPE_C_HEADER_KEY, header1)
    shape_c2 = _get_key(SHAPE_C_HEADER_KEY, header2)
    shape_d1 = _get_key(SHAPE_D_HEADER_KEY, header1)
    shape_d2 = _get_key(SHAPE_D_HEADER_KEY, header2)
    # plot
    fig, frames = plt.subplots(ncols=3, nrows=1)
    frames[0].plot([shape_dx1, shape_dx2], [shape_dy1, shape_dy2],
                   linestyle='None', marker='x')
    frames[0].set(xlabel='dx', ylabel='dy')

    frames[1].plot([shape_a1, shape_a2], [shape_d1, shape_d2],
                   linestyle='None', marker='x')
    frames[1].set(xlabel='A', ylabel='D')

    frames[2].plot([shape_b1, shape_b2], [shape_c1, shape_c2],
                   linestyle='None', marker='x')
    frames[2].set(xlabel='B', ylabel='C')

    frames[0].ticklabel_format(style='sci', axis='both', scilimits=(0, 0))
    frames[1].ticklabel_format(style='sci', axis='both', scilimits=(0, 0))
    frames[2].ticklabel_format(style='sci', axis='both', scilimits=(0, 0))


def _get_key(key, header):
    if key in header:
        return header[key]
    else:
        return None


def _diff_image(frame, image1, image2):
    diff = image1 - image2
    frame.imshow(diff, aspect='auto', origin='lower',
                 vmin=np.nanpercentile(diff, 5),
                 vmax=np.nanpercentile(diff, 95))
    return frame


def _diff_image_axis(frame, image1, image2, axis=0):
    y1, x1 = image1.shape
    y2, x2 = image2.shape

    # deal with wrong shapes
    if y1 != y2:
        print('Y axis not the same image1={0} image2={1}'.format(y1, y2))
        return 0
    if x1 != x2:
        print('X axis not the same image1={0} image2={1}'.format(x1, x2))
        return 0

    # deal with axis
    if axis == 0:
        length = y1
    else:
        length = x1

    for it in range(length):

        if axis == 0:
            diff = image1[it] - image2[it]
        else:
            diff = image1[:, it] - image2[:, it]

        frame.plot(diff)
        frame.text(-1, diff[0], it)
        frame.text(len(diff), diff[-1], it)

        if axis == 0:
            xlabel = 'x pixel number'
            ylabel = 'Delta y pixel value'
            title = 'Y Difference'
        else:
            xlabel = 'y pixel number'
            ylabel = 'Delta x pixel value'
            title = 'X Difference'

        frame.set(xlabel=xlabel, ylabel=ylabel, title=title)

    return frame


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # interactive mode
    plt.ion()
    # ----------------------------------------------------------------------
    # get paths
    in_path1 = os.path.join(WORKSPACE, night1)
    in_path2 = os.path.join(WORKSPACE, night2)
    # ----------------------------------------------------------------------
    # get headers
    in_header1 = fits.getheader(os.path.join(in_path1, file1))
    in_header2 = fits.getheader(os.path.join(in_path2, file2))
    # ----------------------------------------------------------------------
    # loc comparison
    loc_compare(in_header1, in_header2, in_path1, in_path2)
    # ----------------------------------------------------------------------
    # order p comparison
    orderp_compare(in_header1, in_header2, in_path1, in_path2)
    # ----------------------------------------------------------------------
    # flat comparison
    flat_compare(in_header1, in_header2, in_path1, in_path2)
    # ----------------------------------------------------------------------
    # blaze comparison
    blaze_compare(in_header1, in_header2, in_path1, in_path2)
    # ----------------------------------------------------------------------
    # shape comparison
    shape_compare(in_header1, in_header2)
    # ----------------------------------------------------------------------


# =============================================================================
# End of code
# =============================================================================
