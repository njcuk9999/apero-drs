#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import os
from astropy.io import fits
from scipy.interpolate import InterpolatedUnivariateSpline as IUVSpline


# =============================================================================
# Define variables
# =============================================================================
# define workspace
WORKSPACE = '/scratch/Projects/spirou/data_misc/etiennes_problems/extract_issue555/'

# define flat flat file
FLATFILE = '2295520f_pp.fits'
FPFILE = '2295525a_pp.fits'
LOCOFILE_AB = '20180805_2295515f_pp_loco_AB.fits'
LOCOFILE_C = '20180805_2295510f_pp_loco_C.fits'
SHAPEFILE = '20180805_2295525a_pp_shape.fits'

# SIZE
XLOW, XHIGH = 4, 4092
YLOW, YHIGH = 250, 3350


# =============================================================================
# Define functions
# =============================================================================
def WLOG(p, level, message):
    if p is None:
        print('{0} | {1}'.format(level, message))
    else:
        print('{0} | {1}'.format(level, message))


def get_coefficients(hdr, kind='a'):
    number_orders = int(hdr['LONBO'])
    number_coeffs_width = int(hdr['LODEGCTR']) + 1
    number_coeffs_pos = int(hdr['LODEGFWH']) + 1

    width_coeff = read2dkey(hdr, 'LOFW', number_orders, number_coeffs_width)
    pos_coeffs = read2dkey(hdr, 'LOCTR', number_orders, number_coeffs_pos)

    if kind == 'b':
        pos_coeffs = pos_coeffs[:-1:2]
        width_coeff = width_coeff[:-1:2]
    elif kind == 'a':
        pos_coeffs = pos_coeffs[1::2]
        width_coeff = width_coeff[1::2]

    return pos_coeffs, width_coeff


def read2dkey(hdict, key, dim1, dim2):
    func_name = '.read_key_2d_list()'
    # create 2d list
    values = np.zeros((dim1, dim2), dtype=float)
    # loop around the 2D array
    dim1, dim2 = values.shape
    for i_it in range(dim1):
        for j_it in range(dim2):
            # construct the key name
            keyname = '{0}{1}'.format(key, i_it * dim2 + j_it)
            # try to get the values
            try:
                # set the value
                values[i_it][j_it] = float(hdict[keyname])
            except KeyError:
                emsg1 = ('Cannot find key "{0}" with dim1={1} dim2={2} in '
                         '"hdict"').format(keyname, dim1, dim2)
                emsg2 = '    function = {0}'.format(func_name)
                WLOG(p, 'error', [emsg1, emsg2])
    # return values
    return values


def format_data(data):
    # flip data
    data = data[::-1, ::-1]
    # convert NaN to zeros
    data = np.where(~np.isfinite(data), np.zeros_like(data), data)
    # resize data
    xmask = np.arange(XLOW, XHIGH)
    ymask = np.arange(YLOW, YHIGH)
    data = np.take(np.take(data, xmask, axis=1), ymask, axis=0)
    return data


def debananafication(p, image=None, dx=None, pos_a=None, pos_b=None,
                     pos_c=None):
    """
    Uses a shape map (dx) to straighten (de-banana) an image

    :param image: numpy array (2D), the original image
    :param dx: numpy array (2D), the shape image (dx offsets)

    :return image1: numpy array (2D), the straightened image
    """
    # deal with None
    if image is None:
        WLOG(p, 'error', 'Dev Error: Must define an image')
    if dx is None:
        WLOG(p, 'error', 'Dev Error: Must define a shape image (dx)')

    # getting the size of the image and creating the image after correction of
    # distortion
    image1 = np.array(image)
    sz = np.shape(dx)

    # x indices in the initial image
    xpix = np.array(range(sz[1]))

    # we shift all lines by the appropiate, pixel-dependent, dx
    for it in range(sz[0]):
        not0 = image[it, :] != 0
        # do spline fit
        spline = IUVSpline(xpix[not0], image[it, not0], ext=1)
        # only pixels where dx is finite are considered
        nanmask = np.isfinite(dx[it, :])
        image1[it, nanmask] = spline(xpix[nanmask] + dx[it, nanmask])

    if pos_a is not None and pos_b is None and pos_c is not None:
        # TODO: Etienne's code here
        pass


    # return the straightened image
    return image1


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # ------------------------------------------------------------------
    # set p
    p = None
    # get paths to data
    flat_file = os.path.join(WORKSPACE, FLATFILE)
    fp_file = os.path.join(WORKSPACE, FPFILE)
    # ------------------------------------------------------------------
    # get data
    WLOG(p, '', 'Loading data')
    flat_data = fits.getdata(flat_file)
    fp_data = fits.getdata(fp_file)
    shapemap = fits.getdata(os.path.join(WORKSPACE, SHAPEFILE))
    # ------------------------------------------------------------------
    # get data and reformat
    WLOG(p, '', 'Converting data to right shape')
    flat_data = format_data(flat_data)
    fp_data = format_data(fp_data)
    # ------------------------------------------------------------------
    # get file header
    WLOG(p, '', 'Getting headers')
    header_ab = fits.getheader(os.path.join(WORKSPACE, LOCOFILE_AB))
    header_c = fits.getheader(os.path.join(WORKSPACE, LOCOFILE_C))
    # ------------------------------------------------------------------
    # coeffs_ab
    WLOG(p, '', 'Getting Coefficients')
    pos_a, wid_a = get_coefficients(header_ab, kind='a')
    pos_b, wid_b = get_coefficients(header_ab, kind='b')
    pos_c, wid_c = get_coefficients(header_c, kind='c')
    # ------------------------------------------------------------------
    image, dx = flat_data, shapemap
    # ------------------------------------------------------------------
    # straighten image
    WLOG(p, '', 'debananafication on flat')
    sflat = debananafication(p, image=flat_data, dx=shapemap,
                             pos_a=pos_a, pos_b=pos_b, pos_c=pos_c)
    WLOG(p, '', 'debananafication on fp')
    sfp = debananafication(p, image=fp_data, dx=shapemap,
                           pos_a=pos_a, pos_b=pos_b, pos_c=pos_c)
    # ------------------------------------------------------------------
    # write to file
    WLOG(p, '', 'Writing to file')
    fits.writeto(filename=flat_file.replace('.fits', '_s.fits'),
                 data=sflat, overwrite=True)
    fits.writeto(filename=fp_file.replace('.fits', '_s.fits'),
                 data=sfp, overwrite=True)