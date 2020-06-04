#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2020-05-07

@author: cook
"""
from astropy.io import fits
from astropy.table import Table
from astropy import units as uu
from astropy.time import Time
import numpy as np
import sys
import os
import argparse
from scipy.interpolate import InterpolatedUnivariateSpline
import matplotlib.pyplot as plt
import itertools


# =============================================================================
# Define variables
# =============================================================================
__VERSION__ = '0.2.000'
__DATE__ = '2020-05-07'
# constants
SPEED_OF_LIGHT = 299792.458  # [km/s]
IMAGE_PIXEL_SIZE = 2.28  # IMAGE_PIXEL_SIZE


# =============================================================================
# Argument functions
# =============================================================================
class Arguments:
    def __init__(self, rawargs):
        self.version = __VERSION__
        self.date = __DATE__
        # static
        self.CASE = 1
        self.OUTDIR = '.'
        self.PLOT = True
        self.DEBUG = False
        self.kernelparams = None
        # can be dynamic
        self.KERNEL = None
        self.KERNEL_WIDTH = None
        self.KERNEL_EWIDTH = None
        self.KERNEL_BETA = None
        self.IN_FILE = None
        self.BLAZE_FILE = None
        self.WAVE_FILE = None
        self.MASK_FILE = None
        self.MASK_WIDTH = None
        self.MASK_MIN_WEIGHT = None
        self.CCF_STEP = None
        self.CCF_WIDTH = None
        self.CCF_RV_NULL = None
        self.IN_RV = None
        self.CCF_N_ORD_MAX = None
        self.BLAZE_NORM_PERCENTILE = None
        self.BLAZE_THRESHOLD = None
        self.NOISE_SIGDET = None
        self.NOISE_SIZE = None
        self.NOISE_THRES = None
        # get raw args
        self.rawargs = rawargs[1:]
        self.cmdargs = None
        # deal with version argument
        if '--version' in self.rawargs:
            print('Version={0} ({1})'.format(__VERSION__, __DATE__))
            sys.exit(1)
        # do we get arguments from args?
        if len(self.rawargs) > 0:
            self.parseargs()

    def cmdkeys(self):
        keys = dict()
        keys['KERNEL'] = '--kernel={0} '
        keys['KERNEL_WIDTH'] = '--kernelwid={0} '
        keys['KERNEL_EWIDTH'] = '--kernelewid={0} '
        keys['KERNEL_BETA'] = '--kernelbeta={0} '
        keys['IN_FILE'] = '--infile={0} '
        keys['BLAZE_FILE'] = '--blaze={0} '
        keys['WAVE_FILE'] = '--wave={0} '
        keys['MASK_WIDTH'] = '--maskwidth={0} '
        keys['MASK_MIN_WEIGHT'] = '--maskminweight={0} '
        keys['CCF_STEP'] = '--ccfstep={0} '
        keys['CCF_WIDTH'] = '--ccfwidth={0} '
        keys['CCF_RV_NULL'] = '--ccf_rv_null={0} '
        keys['IN_RV'] = '--targetrv={0} '
        keys['CCF_N_ORD_MAX'] = '--ccf_ord_max={0} '
        keys['BLAZE_NORM_PERCENTILE'] = '--blazenormper={0} '
        keys['BLAZE_THRESHOLD'] = '--blaze_thres={0} '
        keys['NOISE_SIGDET'] = '--noise_sigdet={0} '
        keys['NOISE_SIZE'] = '--noise_size={0} '
        keys['NOISE_THRES'] = '--noise_thres={0} '
        return keys


    def parseargs(self):
        # get parser
        desc = ('Stand alone CCF code from the DRS. Version {0}. '
                'Note any arguments left out will default to the default '
                'defined in the --case argument '
                '(if left out this defaults to --case=1)')
        parser = argparse.ArgumentParser(description=desc.format(self.version))

        parser.add_argument('--case', action='store', default=self.CASE,
                            dest='CASE', choices=[1, 2], required=True,
                            type=int,
                            help='The case to use for all undefined keywords. '
                                 'case=1   default setup for datatype=OBJ. '
                                 'case=2   default setup for datatype=FP')
        parser.add_argument('--plot', action='store_true', default=self.PLOT,
                            dest='PLOT', help='If set plots graphics')
        parser.add_argument('--debug', action='store_true', default=False,
                            dest='DEBUG', help='Debug mode')
        parser.add_argument('--outdir', action='store', default=self.OUTDIR,
                            dest='OUTDIR',
                            help='Output path for files (absolute path) if'
                                 'blank uses the input file directory.')
        parser.add_argument('--kernel', action='store', default=self.KERNEL,
                            dest='KERNEL',
                            choices=['None', 'boxcar', 'gaussian',
                                     'supergaussian'],
                            help='Kernal name. '
                                 'If boxcar must define --kernelwid '
                                 'If gaussian must define --kernelewid '
                                 'If supergaussian must define '
                                 '--kernelewid --kernelbeta.')
        parser.add_argument('--kernelwid', action='store',
                            default=self.KERNEL_WIDTH, dest='KERNEL_WIDTH',
                            help='The kernel width if --kernel=boxcar')
        parser.add_argument('--kernelewid', action='store',
                            default=self.KERNEL_EWIDTH, dest='KERNEL_EWIDTH',
                            help='The kernel e-width if --kernel=gaussian or'
                                 '--kernel=supergaussian')
        parser.add_argument('--kernelbeta', action='store',
                            default=self.KERNEL_BETA, dest='KERNEL_BETA',
                            help='The kernel beta value if '
                                 '--kernel=supergaussian')
        parser.add_argument('--infile', action='store',
                            default=self.IN_FILE, dest='IN_FILE',
                            help='The input e2dsff file (absolute path)')
        parser.add_argument('--blaze', action='store',
                            default=self.BLAZE_FILE, dest='BLAZE_FILE',
                            help='The input blaze file (absolute path)')
        parser.add_argument('--wave', action='store',
                            default=self.WAVE_FILE, dest='WAVE_FILE',
                            help='The input wave solution (absolute path)'
                                 'if one wishes to use the header set this to'
                                 '"None" or "header" i.e. --wave="None" or'
                                 ' --wave="header"')
        parser.add_argument('--mask', action='store', default=self.MASK_FILE,
                            dest='MASK_FILE',
                            help='The ccf mask file to use (absolute path)')
        parser.add_argument('--maskwidth', action='store', type=float,
                            default=self.MASK_WIDTH, dest='MASK_WIDTH',
                            help='The size of the mask lines to use')
        parser.add_argument('--maskminweight', action='store', type=float,
                            default=self.MASK_MIN_WEIGHT,
                            dest='MASK_MIN_WEIGHT',
                            help='The minimum line weighting to use. If set to'
                                 '1 forces all weights to be equal')
        parser.add_argument('--ccfstep', action='store', default=self.CCF_STEP,
                            dest='CCF_STEP', type=float,
                            help='CCF step size [km/s]')
        parser.add_argument('--ccfwidth', action='store',
                            default=self.CCF_WIDTH, dest='CCF_WIDTH',
                            help='CCF step width [km/s]')
        parser.add_argument('--ccf_rv_null', action='store',
                            default=self.CCF_RV_NULL, dest='CCF_RV_NULL',
                            help='The largest absolute RV value to accept from '
                                 'header. Above or below this values are '
                                 'rejected')
        parser.add_argument('--targetrv', action='store',
                            default=self.IN_RV, dest='IN_RV',
                            help='The input target RV [km/s]')
        parser.add_argument('--ccf_ord_max', action='store',
                            default=self.CCF_N_ORD_MAX, dest='CCF_N_ORD_MAX',
                            help='The reddest order to use (bluest = 0)')
        parser.add_argument('--blazenormper', action='store',
                            default=self.BLAZE_NORM_PERCENTILE,
                            dest='BLAZE_NORM_PERCENTILE',
                            help='The blaze percentile to normalise by [0-100]')
        parser.add_argument('--blaze_thres', action='store',
                            default=self.BLAZE_THRESHOLD,
                            dest='BLAZE_THRESHOLD',
                            help='The blaze threshold to cut at '
                                 '(below this blaze level flux is ignored)')
        parser.add_argument('--noise_sigdet', action='store',
                            default=self.NOISE_SIGDET, dest='NOISE_SIGDET',
                            help='The noise level used to calculate dv rms '
                                 'and ccf snr')
        parser.add_argument('--noise_size', action='store',
                            default=self.NOISE_SIZE, dest='NOISE_SIZE',
                            help='The size around saturated pixels to flag as '
                                 'unusable for dv rms')
        parser.add_argument('--noise_thres', action='store',
                            default=self.NOISE_THRES, dest='NOISE_THRES',
                            help='The maximum flux for a good unsaturated pixel'
                                 'for dv rms')

        # parse arguments
        self.cmdargs = parser.parse_args()
        # update case (as other parameters are defined by default from this)
        if self.cmdargs.CASE is not None:
            self.CASE = self.cmdargs.CASE

    def args_from_cmd(self):
        """
        Push commands from arguments into constants in self
        i.e. access through Argument.VARIABLE

        :return:
        """
        if self.cmdargs is None:
            return
        # update self with args
        for key in self.__dict__:
            if hasattr(self.cmdargs, key):
                argval = getattr(self.cmdargs, key)
                if argval is not None:
                    setattr(self, key, argval)

    def kernel_args(self):
        # get the kernel name
        name = self.KERNEL.lower()
        # deal with kernel cases
        if name in [None, 'None', '']:
            self.kernelparams = None
        elif 'box' in name:
            # get the width
            width = self.KERNEL_WIDTH
            if width is None:
                raise ValueError('ERROR: kernel width must be set')
            try:
                width = float(width)
            except:
                raise ValueError('ERROR: kernel width must be a valid float')
            # set kernel params
            self.kernelparams = ['boxcar', width]
        elif ('gauss' in name) and ('super' not in name):
            # get the e-width
            ewidth = self.KERNEL_EWIDTH
            if ewidth is None:
                raise ValueError('ERROR: kernel e-width must be set')
            try:
                ewidth = float(ewidth)
            except:
                raise ValueError('ERROR: kernel e-width must be a valid float')
            # set kernel params
            self.kernelparams = ['gaussian', ewidth]
        elif ('gauss' in name):
            # get the e-width
            ewidth = self.KERNEL_EWIDTH
            if ewidth is None:
                raise ValueError('ERROR: kernel e-width must be set')
            try:
                ewidth = float(ewidth)
            except:
                raise ValueError('ERROR: kernel e-width must be a valid float')
            # get the beta value
            beta = self.KERNEL_BETA
            if beta is None:
                raise ValueError('ERROR: kernel beta must be set')
            try:
                beta = float(beta)
            except:
                raise ValueError('ERROR: kernel beta must be a valid float')
            # set kernel params
            self.kernelparams = ['supergaussian', ewidth, beta]
        else:
            self.kernelparams = None


def get_combinations(names, variables, newdirs, outdir):
    combinations = []
    # generate time string
    timestr = Time.now().iso.replace(' ', '_')
    # get all combinations
    combs = list(itertools.product(*variables))
    # loop around combinations and create combination
    for c_it, comb in enumerate(combs):
        cargs = [c_it, comb, names, newdirs, len(combs), outdir, timestr]
        combinations.append(Combination(*cargs))
    # return all combination instances
    return combinations


class Combination:
    def __init__(self, number, variables, names, newdirs, total, outpath,
                 timestr):
        # get some stats (for ease of use)
        self.number = number
        self.total = total
        # get output directory
        self.outdir = str(timestr)
        # setup parameter dictionary
        self.parameters = dict()
        # append parameters and outdir
        for n_it, name in enumerate(names):
            value = variables[n_it]
            self.parameters[name] = value
            # deal with paths
            if os.sep in value:
                strvalue = os.path.basename(value)
                strvalue.split('.')[0]
            # add to the outdir
            if newdirs[n_it]:
                self.outdir += '_{0}={1}'.format(name, strvalue)
        # set output dir
        self.outpath = os.path.join(outpath, self.outdir)
        # need to make the directory
        if not os.path.exists(self.outpath):
            print('Creating directory {0}'.format(self.outpath))
            os.mkdir(self.outpath)


# =============================================================================
# Reading functions
# =============================================================================
def read_mask(mask_file, mask_cols):
    table = Table.read(mask_file, format='ascii')
    # get column names
    oldcols = list(table.colnames)
    # rename columns
    for c_it, col in enumerate(mask_cols):
        table[oldcols[c_it]].name = col
    # return table
    return table


def read_wave(image, iheader, wavefile):
    if wavefile not in [None, 'None', '', 'False', False, 'header']:
        # load the wave file and return it
        wavemap, waveheader = fits.getdata(wavefile, header=True)
        # return the wave map and the wave header
        return wavemap, waveheader, wavefile
    else:
        # get image dimensions
        nbo, nbx = image.shape
        deg = iheader['WAVEDEGN']
        # populate the wave coefficients
        wave_coeffs = np.zeros((nbo, deg + 1))
        for it in range(nbo):
            for jt in range(deg + 1):
                kt = it * (deg + 1 + jt)
                wave_coeffs[it][jt] = iheader['WAVE{0:04d}'.format(kt)]
        # set up storage
        wavemap = np.zeros((nbo, nbx))
        xpixels = np.arange(nbx)
        # loop aroun each order and make the wave map
        for order_num in range(nbo):
            # get this order coefficients
            ocoeffs = wave_coeffs[order_num][::-1]
            # calculate polynomial values and push into wavemap
            wavemap[order_num] = np.polyval(ocoeffs, xpixels)
        # get wave keys from header
        waveheader = fits.Header()
        waveheader['MJDMID'] = iheader['WAVETIME']
        # return the wave map and the wave header
        return wavemap, waveheader, iheader['WAVEFILE']


def get_mask(table, mask_width, mask_min, mask_units='nm'):
    ll_mask_e = np.array(table['ll_mask_e']).astype(float)
    ll_mask_s = np.array(table['ll_mask_s']).astype(float)
    ll_mask_d = ll_mask_e - ll_mask_s
    ll_mask_ctr = ll_mask_s + ll_mask_d * 0.5
    # if mask_width > 0 ll_mask_d is multiplied by mask_width/c
    if mask_width > 0:
        ll_mask_d = mask_width * ll_mask_s / SPEED_OF_LIGHT
    # make w_mask an array
    w_mask = np.array(table['w_mask']).astype(float)
    # use w_min to select on w_mask or keep all if w_mask_min >= 1
    if mask_min < 1.0:
        mask = w_mask > mask_min
        ll_mask_d = ll_mask_d[mask]
        ll_mask_ctr = ll_mask_ctr[mask]
        w_mask = w_mask[mask]
    # else set all w_mask to one (and use all lines in file)
    else:
        w_mask = np.ones(len(ll_mask_d))
    # ----------------------------------------------------------------------
    # deal with the units of ll_mask_d and ll_mask_ctr
    # must be returned in nanometers
    # ----------------------------------------------------------------------
    # get unit object from mask units string
    unit = getattr(uu, mask_units)
    # add units
    ll_mask_d = ll_mask_d * unit
    ll_mask_ctr = ll_mask_ctr * unit
    # convert to nanometers
    ll_mask_d = ll_mask_d.to(uu.nm).value
    ll_mask_ctr = ll_mask_ctr.to(uu.nm).value
    # ----------------------------------------------------------------------
    # return the size of each pixel, the central point of each pixel
    #    and the weight mask
    return ll_mask_d, ll_mask_ctr, w_mask


# =============================================================================
# Math functions
# =============================================================================
def relativistic_waveshift(dv, units='km/s'):
    """
    Relativistic offset in wavelength

    default is dv in km/s

    :param dv: float or numpy array, the dv values
    :param units: string or astropy units, the units of dv
    :return:
    """
    # get c in correct units
    # noinspection PyUnresolvedReferences
    if units == 'km/s' or units == uu.km / uu.s:
        c = SPEED_OF_LIGHT
    # noinspection PyUnresolvedReferences
    elif units == 'm/s' or units == uu.m / uu.s:
        c = SPEED_OF_LIGHT * 1000
    else:
        raise ValueError("Wrong units for dv ({0})".format(units))
    # work out correction
    corrv = np.sqrt((1 + dv / c) / (1 - dv / c))
    # return correction
    return corrv


def iuv_spline(x, y, **kwargs):
    # copy x and y
    x, y = np.array(x), np.array(y)
    # find all NaN values
    nanmask = ~np.isfinite(y)

    if np.sum(~nanmask) < 2:
        y = np.zeros_like(x)
    elif np.sum(nanmask) == 0:
        pass
    else:
        # replace all NaN's with linear interpolation
        badspline = InterpolatedUnivariateSpline(x[~nanmask], y[~nanmask],
                                                 k=1, ext=1)
        y[nanmask] = badspline(x[nanmask])
    # return spline
    return InterpolatedUnivariateSpline(x, y, **kwargs)


def gauss_function(x, a, x0, sigma, dc):
    """
    A standard 1D gaussian function (for fitting against)]=

    :param x: numpy array (1D), the x data points
    :param a: float, the amplitude
    :param x0: float, the mean of the gaussian
    :param sigma: float, the standard deviation (FWHM) of the gaussian
    :param dc: float, the constant level below the gaussian

    :return gauss: numpy array (1D), size = len(x), the output gaussian
    """
    return a * np.exp(-0.5 * ((x - x0) / sigma) ** 2) + dc


def fwhm(sigma=1.0):
    """
    Get the Full-width-half-maximum value from the sigma value (~2.3548)

    :param sigma: float, the sigma, default value is 1.0 (normalised gaussian)
    :return: 2 * sqrt(2 * log(2)) * sigma = 2.3548200450309493 * sigma
    """
    return 2 * np.sqrt(2 * np.log(2)) * sigma


# =============================================================================
# Plot functions
# =============================================================================
def plotloop(looplist):
    # check that looplist is a valid list
    if not isinstance(looplist, list):
        # noinspection PyBroadException
        try:
            looplist = list(looplist)
        except Exception as _:
            print('PLOT ERROR: looplist must be a list')
    # define message to give to user
    message = ('Plot loop navigation: Go to \n\t [P]revious plot '
               '\n\t [N]ext plot \n\t [E]nd plotting '
               '\n\t Number from [0 to {0}]: \t')
    message = message.format(len(looplist) - 1)
    # start the iterator at zero
    it = 0
    first = True
    # loop around until we hit the length of the loop list
    while it < len(looplist):
        # deal with end of looplist
        if it == len(looplist):
            # break out of while
            break
        # if this is the first iteration do not print message
        if first:
            # yield the first iteration value
            yield looplist[it]
            # increase the iterator value
            it += 1
            first = False
        # else we need to ask to go to previous, next or end
        else:
            # get user input
            userinput = input(message)
            # try to cast into a integer
            # noinspection PyBroadException
            try:
                userinput = int(userinput)
            except Exception as _:
                userinput = str(userinput)
            # if 'p' in user input we assume they want to go to previous
            if 'P' in str(userinput).upper():
                yield looplist[it - 1]
                it -= 1
            # if 'n' in user input we assume they want to go to next
            elif 'N' in str(userinput).upper():
                yield looplist[it + 1]
                it += 1
            elif isinstance(userinput, int):
                it = userinput
                # deal with it too low
                if it < 0:
                    it = 0
                # deal with it too large
                elif it >= len(looplist):
                    it = len(looplist) - 1
                # yield the value of it
                yield looplist[it]
            # else we assume the loop is over and we want to exit
            else:
                # break out of while
                break


def plot_individual_ccf(props, nbo):
    # get the plot loop generator
    generator = plotloop(range(nbo))
    # loop around orders
    for order_num in generator:
        plt.close()
        fig, frame = plt.subplots(ncols=1, nrows=1)
        frame.plot(props['RV_CCF'], props['CCF'][order_num], color='b',
                   marker='+', ls='None', label='data')
        frame.plot(props['RV_CCF'], props['CCF_FIT'][order_num], color='r', )
        rvorder = props['CCF_FIT_COEFFS'][order_num][1]
        frame.set(title='Order {0}  RV = {1} km/s'.format(order_num, rvorder),
                  xlabel='RV [km/s]', ylabel='CCF')
        plt.show()
        plt.close()


def plot_mean_ccf(props):
    plt.close()
    fig, frame = plt.subplots(ncols=1, nrows=1)
    frame.plot(props['RV_CCF'], props['MEAN_CCF'], color='b', marker='+',
               ls='None')
    frame.plot(props['RV_CCF'], props['MEAN_CCF_FIT'], color='r')
    frame.set(title='Mean CCF   RV = {0} km/s'.format(props['MEAN_RV']),
              xlabel='RV [km/s]', ylabel='CCF')
    plt.show()
    plt.close()


# =============================================================================
# Writing functions
# =============================================================================
def write_file(props, infile, maskname, header, wheader, wave_file,
               outpath=None):
    # ----------------------------------------------------------------------
    # construct out file name
    inbasename = os.path.basename(infile).split('.')[0]
    maskbasename = os.path.basename(maskname).split('.')[0]
    inpath = os.path.dirname(infile)
    outfile = 'CCFTABLE_{0}_{1}.fits'.format(inbasename, maskbasename)
    # deal with no outpath
    if outpath is None:
        outpath = os.path.join(inpath, outfile)
    # ----------------------------------------------------------------------
    # produce CCF table
    table1 = Table()
    table1['RV'] = props['RV_CCF']
    for order_num in range(len(props['CCF'])):
        table1['ORDER{0:02d}'.format(order_num)] = props['CCF'][order_num]
    table1['COMBINED'] = props['MEAN_CCF']
    # ----------------------------------------------------------------------
    # produce stats table
    table2 = Table()
    table2['ORDERS'] = np.arange(len(props['CCF'])).astype(int)
    table2['NLINES'] = props['CCF_LINES']
    # get the coefficients
    coeffs = props['CCF_FIT_COEFFS']
    table2['CONTRAST'] = np.abs(100 * coeffs[:, 0])
    table2['RV'] = coeffs[:, 1]
    table2['FWHM'] = coeffs[:, 2]
    table2['DC'] = coeffs[:, 3]
    table2['SNR'] = props['CCF_SNR']
    table2['NORM'] = props['CCF_NORM']

    # ----------------------------------------------------------------------
    # add to the header
    # ----------------------------------------------------------------------
    # add results from the CCF
    header['CCFMNRV'] = (props['MEAN_RV'],
                         'Mean RV calc. from the mean CCF [km/s]')
    header['CCFMCONT'] = (props['MEAN_CONTRAST'],
                          'Mean contrast (depth of fit) from mean CCF')
    header['CCFMFWHM'] = (props['MEAN_FWHM'],
                          'Mean FWHM from mean CCF')
    header['CCFMRVNS'] = (props['MEAN_RV_NOISE'],
                          'Mean RV Noise from mean CCF')
    header['CCFTLINE'] = (props['TOT_LINE'],
                          'Total no. of mask lines used in CCF')
    # ----------------------------------------------------------------------
    # add constants used to process
    header['CCFMASK'] = (props['CCF_MASK'], 'CCF mask file used')
    header['CCFSTEP'] = (props['CCF_STEP'], 'CCF step used [km/s]')
    header['CCFWIDTH'] = (props['CCF_WIDTH'], 'CCF width used [km/s]')
    header['CCFTRGRV'] = (props['TARGET_RV'],
                          'CCF central RV used in CCF [km/s]')
    header['CCFSIGDT'] = (props['CCF_SIGDET'],
                          'Read noise used in photon noise calc. in CCF')
    header['CCFBOXSZ'] = (props['CCF_BOXSIZE'],
                          'Size of bad px used in photon noise calc. in CCF')
    header['CCFMAXFX'] = (props['CCF_MAXFLUX'],
                          'Flux thres for bad px in photon noise calc. in CCF')
    header['CCFORDMX'] = (props['CCF_NMAX'],
                          'Last order used in mean for mean CCF')
    header['CCFMSKMN'] = (props['MASK_MIN'],
                          'Minimum weight of lines used in the CCF mask')
    header['CCFMSKWD'] = (props['MASK_WIDTH'],
                          'Width of lines used in the CCF mask')
    header['CCFMUNIT'] = (props['MASK_UNITS'], 'Units used in CCF Mask')
    # ----------------------------------------------------------------------
    header['RV_WAVFN'] = (os.path.basename(wave_file), 'RV wave file used')
    header['RV_WAVTM'] = (wheader['MJDMID'],
                          'RV wave file time [mjd]')
    header['RV_WAVTD'] = (header['MJDMID'] - wheader['MJDMID'],
                          'RV timediff [days] btwn file and wave solution')
    header['RV_WAVFP'] = ('None', 'RV measured from wave sol FP CCF [km/s]')
    header['RV_SIMFP'] = ('None', 'RV measured from simultaneous FP CCF [km/s]')
    header['RV_DRIFT'] = ('None',
                          'RV drift between wave sol and sim. FP CCF [km/s]')
    header['RV_OBJ'] = (props['MEAN_RV'],
                        'RV calc in the object CCF (non corr.) [km/s]')
    header['RV_CORR'] = ('None', 'RV corrected for FP CCF drift [km/s]')
    # ----------------------------------------------------------------------
    # log where we are writing the file to
    print('Writing file to {0}'.format(outpath))
    # construct hdus
    hdu = fits.PrimaryHDU()
    t1 = fits.BinTableHDU(table1, header=header)
    t2 = fits.BinTableHDU(table2, header=header)
    # construct hdu list
    hdulist = fits.HDUList([hdu, t1, t2])
    # write hdulist
    hdulist.writeto(outpath, overwrite=True)
