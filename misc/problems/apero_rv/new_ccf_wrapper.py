#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2020-03-27 at 13:42

@author: cook
"""
import os
import glob
import sys

import arv_util as arv

# =============================================================================
# Define variables
# =============================================================================
# get arguments
args = arv.Arguments(sys.argv)

# if all files copied to same directory set these to ''
# W1 = ''
# W2 = ''
# these files are on cook@nb19
W1 = '/scratch3/rali/spirou/mini_data/reduced/2019-04-20/'
W2 = '/scratch3/rali/drs/apero-drs/apero/data/spirou/ccf/'
# output directory
args.OUTDIR = './ccfwrapper/'

# whether to plot (True or False)
args.PLOT = False
#---------------------------------------------------------------------------
# Pick you CCF convolution kernel. See explanantions below in the
# CCF function. Uncomment the kernel type you want and change the
# parameter.
# CCF is a set of Dirac functions
args.KERNEL = 'None'
# args.KERNEL_WIDTH = None
# args.KERNEL_EWIDTH = None
# args.KERNEL_BETA = None

# boxcar length expressed in km/s
# args.KERNEL = 'boxcar'
# args.KERNEL_WIDTH = 5

# gaussian with e-width in km/s
# args.KERNEL = 'gaussian'
# args.KERNEL_EWIDTH = 3.5

# supergaussian e-width + exponent
# args.KERNEL = 'supergaussian'
# args.KERNEL_EWIDTH = 3.5
# args.KERNEL_BETA = 4
#---------------------------------------------------------------------------

# deal with cases (quick switch between fiber=AB (OBJ) and fiber=C (FP)
#   quickly switch between:
#     case == 1:  standard AB OBJ fiber (edited in this file)
#     case == 2:  standard C FP fiber (edited in this file)
# set the case in the arguments
if args.CASE == 1:
    # ----------------------------------------------------------------------
    # variables to vary
    # ----------------------------------------------------------------------
    # IN_FILES = glob.glob(os.path.join(W1, '24005*o_pp_e2dsff_tcorr_AB.fits'))
    IN_FILES = ['a.fits', 'b.fits', 'c.fits', 'd.fits', 'e.fits']
    MASK_FILES = [os.path.join(W2, 'masque_sept18_andres_trans50.mas')]
    # ----------------------------------------------------------------------
    # static variables
    # ----------------------------------------------------------------------
    # args.IN_FILE = os.path.join(W1, '2400515o_pp_e2dsff_tcorr_AB.fits')
    args.BLAZE_FILE = os.path.join(W1, '2019-04-20_2400404f_pp_blaze_AB.fits')
    args.WAVE_FILE = "None"
    # args.MASK_FILE = os.path.join(W2, 'masque_sept18_andres_trans50.mas')
    args.MASK_WIDTH = 1.7  # CCF_MASK_WIDTH
    args.MASK_MIN_WEIGHT = 0.0  # CCF_MASK_MIN_WEIGHT
    args.CCF_STEP = 0.5  # CCF_DEFAULT_STEP (or user input)
    args.CCF_WIDTH = 300  # CCF_DEFAULT_WIDTH (or user input)
    args.CCF_RV_NULL = 1000  # CCF_OBJRV_NULL_VAL (max allowed)
    args.IN_RV = None  # user input [km/s]
    args.CCF_N_ORD_MAX = 48  # CCF_N_ORD_MAX
    args.BLAZE_NORM_PERCENTILE = 90  # CCF_BLAZE_NORM_PERCENTILE
    args.BLAZE_THRESHOLD = 0.3  # WAVE_FP_BLAZE_THRES
    args.NOISE_SIGDET = 8.0  # CCF_NOISE_SIGDET
    args.NOISE_SIZE = 12  # CCF_NOISE_BOXSIZE
    args.NOISE_THRES = 1.0e9  # CCF_NOISE_THRES
elif args.CASE == 2:
    # ----------------------------------------------------------------------
    # variables to vary
    # ----------------------------------------------------------------------
    IN_FILES = glob.glob(os.path.join(W1, '24005*o_pp_e2dsff_C.fits'))
    MASK_FILES = os.path.join(W2, 'fp.mas')
    # ----------------------------------------------------------------------
    # static variables
    # ----------------------------------------------------------------------
    # args.IN_FILE = os.path.join(W1, '2400515o_pp_e2dsff_C.fits')
    args.BLAZE_FILE = os.path.join(W1, '2019-04-20_2400404f_pp_blaze_C.fits')
    args.WAVE_FILE = "None"
    # args.MASK_FILE = os.path.join(W2, 'fp.mas')
    args.MASK_WIDTH = 1.7  # CCF_MASK_WIDTH
    args.MASK_MIN_WEIGHT = 0.0  # CCF_MASK_MIN_WEIGHT
    args.CCF_STEP = 0.5  # WAVE_CCF_STEP
    args.CCF_WIDTH = 7.5  # WAVE_CCF_WIDTH
    args.CCF_RV_NULL = 1000  # CCF_OBJRV_NULL_VAL (max allowed)
    args.IN_RV = None  # user input [km/s]
    args.CCF_N_ORD_MAX = 48  # WAVE_CCF_N_ORD_MAX
    args.BLAZE_NORM_PERCENTILE = 90  # CCF_BLAZE_NORM_PERCENTILE
    args.BLAZE_THRESHOLD = 0.3  # WAVE_FP_BLAZE_THRES
    args.NOISE_SIGDET = 8.0  # WAVE_CCF_NOISE_SIGDET
    args.NOISE_SIZE = 12  # WAVE_CCF_NOISE_BOXSIZE
    args.NOISE_THRES = 1.0e9  # WAVE_CCF_NOISE_THRES
else:
    raise ValueError('INPUT ERROR: Case must be 1 or 2')


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    # need to get arguments from command line
    args.args_from_cmd()
    args.kernel_args()
    # list here all variables to vary (must have the same names as the static
    #   variables above
    NAMES = ['IN_FILE', 'MASK']
    # the arrays / lists
    VARIABLES = [IN_FILES, MASK_FILES]
    # whether we want a new directory per output
    NEWDIRS = [False, True]
    # generate combinations
    combinations = arv.get_combinations(names=NAMES, variables=VARIABLES,
                                        newdirs=NEWDIRS, outdir=args.OUTDIR)
    # get command keys
    cmdargs = args.cmdkeys()
    # loop around combinations
    for combination in combinations:
        # get iteration value
        pargs = [combination.number + 1, combination.total]
        print('='*50)
        print('Processing iteration {0} of {1}'.format(*pargs))
        print('='*50)
        # get combination parameters
        parameters = combination.parameters
        # set up command
        command = 'new_ccf_code.py --case={0} '.format(args.CASE)
        # add plot if needed
        if args.PLOT:
            command += '--plot '
        # loop around keys and add them to command
        for key in cmdargs:
            # if key is one of our parameters then populate it from parameters
            if key in parameters:
                command += cmdargs[key].format(parameters[key])
            # else use the value in args
            else:
                command += cmdargs[key].format(getattr(args, key))
        # add output directory
        command += '--outdir={0}'.format(combination.outpath)
        # deal with debug print of command/running command
        if args.DEBUG:
            print('\t' + command)
        else:
            os.system(command)