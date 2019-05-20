#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-04-16 at 14:09

@author: cook
"""
from __future__ import division
import numpy as np
import os
import warnings

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'drs_comp.py'
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt
plt = sPlt.plt
# -----------------------------------------------------------------------------
NIGHTNAME = '20170710'
OLDPATH = '/scratch/Projects/SPIRou_Pipeline/data/reduced/20170710/'
NEWPATH = '/scratch/Projects/spirou_py3/data/reduced/20170710/'
# -----------------------------------------------------------------------------
# FILENAME = 'hcone_hcone02c61_e2ds_AB.fits'
# FILENAME = 'fp_fp02a203_e2ds_AB.fits'
# FILENAME = 'hcone_hcone03c61_e2ds_AB.fits'
FILENAME = 'hcone_hcone06c61_e2ds_C.fits'


# =============================================================================
# Define functions
# =============================================================================
def diff_image(p, image1, image2, name1='Image 1', name2='Image 2', scale=None):
    """
    Difference image plot (plots the images and the difference between those
    images)

    :param image1: numpy array (2D), the first image
    :param image2: numpy array (2D), the second image
    :param name1: string, a name for the first image
    :param name2: string, a name for the second image
    :param scale: string or tuple, the scaling to apply to images

    :return None:
    """

    fig1, frame1 = plt.subplots(ncols=1, nrows=1)
    _ = plot_image(p, frame1, image1, title=name1, scale=scale)

    fig2, frame2 = plt.subplots(ncols=1, nrows=1)
    _ = plot_image(p, frame2, image2, title=name2, scale=scale)

    fig3, frame3 = plt.subplots(ncols=1, nrows=1)
    _ = plot_image(p, frame3, image2-image1, scale=scale,
                   title='"{0}" - "{1}"'.format(name2, name1))

    plt.show()
    plt.close()


def plot_image(p, frame, image, title='', scale=None):
    """
    Plot the image (rescaled and resized to be as square as possible)

    :param frame: matplotlib.axis (i.e. plt.subplot)
    :param image: numpy array (2D), the image to plot
    :param title: string, the title to add to the image
    :param scale: string or tuple, the scale to apply to the image
    :return:
    """
    # resize the image if not very square (for visualisation)
    if np.max(image.shape)/np.min(image.shape) > 2:
        # find out which axis is smaller
        small = np.argmin(image.shape)
        # find out the conversion factor
        factor = int(np.max(image.shape)/np.min(image.shape))
        # scale up image
        # noinspection PyTypeChecker
        newimage = np.repeat(image, factor, axis=small)
    else:
        newimage = image
    # scale the iamge
    newimage, strscale = scale_image(p, newimage, scale=scale)
    # plot the image
    im = frame.imshow(newimage)
    # set title
    frame.set(title='{0} {1}'.format(title, strscale))
    # remove x and y axis labels
    frame.set_xticklabels([])
    frame.set_yticklabels([])
    # plot colour bar
    plt.colorbar(im, ax=frame)

    return frame


def scale_image(p, image, scale=None):
    """
    Apply a scaling to the image. Currently supported options are:
        - log:    log10 image
        - sqrt:   sqrt image
        - (min, max)    min and maximum percentile to show (below "min" is set
                        to the value at "min" percentile, above "max" is set to
                        the value at "max" percentile)

    :param image: numpy array (2D), the image the scale
    :param scale: string or tuple, the scaling to apply:
                        "log", "sqrt" or tuple (min, max)
    :return newimage: numpy array (2D), the scaled image
    """
    # deal with no scaling
    if scale is None:
        return image, ''
    # copy image
    newimage = image.copy()

    # deal with scaling
    if scale == 'log':
        with warnings.catch_warnings(record=True) as _:
            return np.log10(newimage), '(scale = {0})'.format(scale)
    elif scale == 'sqrt':
        with warnings.catch_warnings(record=True) as _:
            return np.sqrt(newimage), '(scale = {0})'.format(scale)
    elif type(scale) == tuple:
        # get min and max points
        uppermask = newimage > np.nanpercentile(newimage, scale[1])
        lowermask = newimage < np.nanpercentile(newimage, scale[0])
        good = ~uppermask & ~lowermask
        # apply the masks
        newimage[uppermask] = np.nanmax(newimage[good])
        newimage[lowermask] = np.nanmin(newimage[good])
        # sort out string scale
        sscale = '(scale = {0}% - {1}%)'.format(*scale)
        # return scale
        return newimage, sscale
    else:
        WLOG(p, 'error', 'scale = {0} not understood'.format(scale))


def main(night_name=None, oldfile=None, newfile=None):

    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)
    # deal with arguments being None (i.e. get from sys.argv)
    pos = [0, 1]
    fmt = [str, str]
    names = ['oldfile', 'newfile']
    call = [oldfile, newfile]
    # now get custom arguments
    customargs = spirouStartup.GetCustomFromRuntime(p, pos, fmt, names,
                                                    calls=call)
    # get parameters from configuration files and run time arguments
    p = spirouStartup.LoadArguments(p, night_name, customargs=customargs,
                                    mainfitsfile='newfile')

    # ----------------------------------------------------------------------
    # Get files
    # ----------------------------------------------------------------------
    # check that path exists
    emsg = '{0} file = {1} does not exist'
    if not os.path.exists(p['OLDFILE']):
        WLOG(p, 'error', emsg.format('old', p['OLDFILE']))
    # check that paths exists
    if not os.path.exists(p['NEWFILE']):
        WLOG(p, 'error', emsg.format('new', p['NEWFILE']))
    # load files
    data1, hdr1, cdr1, _, _ = spirouImage.ReadImage(p, filename=oldfile)
    data2, hdr2, cdr2, _, _ = spirouImage.ReadImage(p, filename=newfile)

    # ----------------------------------------------------------------------
    # Do difference image
    # ----------------------------------------------------------------------
    diff_image(p, data1, data2, 'old image', 'new image', scale=(1, 99))

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    wmsg = 'Recipe {0} has been successfully completed'
    WLOG(p, 'info', wmsg.format(p['PROGRAM']))

    # return a copy of locally defined variables in the memory
    return dict(locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main(night_name=NIGHTNAME,
              oldfile=os.path.join(OLDPATH, FILENAME),
              newfile=os.path.join(NEWPATH, FILENAME))
    # exit message if in debug mode
    spirouStartup.Exit(ll)


# =============================================================================
# End of code
# =============================================================================
