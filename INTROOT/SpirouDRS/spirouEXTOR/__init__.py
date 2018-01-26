#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
initialization code for Spirou Extraction module

Created on 2017-11-07 13:45

@author: cook

"""
from SpirouDRS.spirouConfig import Constants
from . import spirouEXTOR

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouEXTOR.__init__()'
# Get version and author
__version__ = Constants.VERSION()
__author__ = Constants.AUTHORS()
__date__ = Constants.LATEST_EDIT()
__release__ = Constants.RELEASE()
# define imports using asterisk
__all__ = ['Extraction', 'ExtractABOrderOffset', 'ExtractOrder',
           'ExtractTiltOrder', 'ExtractTiltWeightOrder',
           'ExtractTiltWeightOrder2', 'ExtractWeightOrder']

# =============================================================================
# Function aliases
# =============================================================================
Extraction = spirouEXTOR.extract_wrapper
"""
Extraction wrapper - takes in image, pos, sig and kwargs and decides
which extraction process to use.

:param image: numpy array (2D), the image
:param pos: numpy array (1D), the position fit coefficients
            size = number of coefficients for fit
:param sig: numpy array (1D), the width fit coefficients
            size = number of coefficients for fit
:param kwargs: additional keyword arguments

currently accepted keyword arguments are:

    extopt:         int, Extraction option in tilt file:
                     if 0 extraction by summation over constant range
                     if 1 extraction by summation over constant sigma
                        (not currently available)
                     if 2 Horne extraction without cosmic elimination
                        (not currently available)
                     if 3 Horne extraction with cosmic elimination
                        (not currently available)

    nbsig:          float,  distance away from center to extract out to +/-
                    defaults to p['nbsig'] from constants_SPIROU.py

    gain:           float, gain of the image
                    defaults to p['gain'] from fitsfilename HEADER

    sigdet:         float, the sigdet of the image
                    defaults to p['sigdet'] from fitsfilename HEADER

    range1:         float, Half-zone extraction width left side
                    (formally plage1)
                    defaults to p['ic_ext_range1'] from fiber parameters in
                    constatns_SPIROU.txt

    range2:         float, Half-zone extraction width left side
                    (formally plage2)
                    defaults to p['ic_ext_range2'] from fiber parameters in
                    constatns_SPIROU.txt

    tilt:           numpy array (1D), the tilt for this order, if defined
                    uses tilt, if not defined does not

    use_weight:    bool, if True use weighted extraction, if False or not
                    defined does not use weighted extraction

    order_profile:  numpy array (2D), the image with fit superposed on top,
                    required for tilt and or weighted fit

    mode:           if use_weight and tilt is not None then
                    if mode = 'old'  will use old code (use this if
                    exception generated)
                    extract_tilt_weight_order_old() is run

                    else mode = 'new' and
                    extract_tilt_weight_order() is run

:return spe: numpy array (1D), the extracted pixel values,
             size = image.shape[1] (along the order direction)
:return nbcos: int, zero in this case
"""

ExtractABOrderOffset = spirouEXTOR.extract_AB_order
"""
Perform the extraction on the AB fibers separately using the summation
over constant range

:param pp: dictionary, parameter dictionary
:param loc: dictionary, parameter dictionary containing the data
:param image: numpy array (2D), the image
:param rnum: int, the order number for this iteration

:return loc: dictionary, parameter dictionary containing the data
"""

ExtractOrder = spirouEXTOR.extract_order
"""
Extract order without tilt or weight using spirouEXTOR.extract_wrapper()

:param pp: dictionary, parameter dictionary
           must have at least "IC_EXT_RANGE" and "GAIN"
:param loc: dictionary, parameter dictionary containing the data
            must have at least "ACC" and "ASS"
:param image: numpy array (2D), the image
:param rnum: int, the order number for this iteration
:param kwargs: additional keywords to pass to the extraction wrapper

        - allowed keywords are:

        range1  (defaults to "IC_EXT_RANGE")
        range2  (defaults to "IC_EXT_RANGE")
        gain    (defaults to "GAIN")

:return cent: numpy array (1D), the extracted pixel values,
             size = image.shape[1] (along the order direction)
:return cpt: int, zero in this case
"""

ExtractTiltOrder = spirouEXTOR.extract_tilt_order
"""
Extract order with tilt but without weight using 
spirouEXTOR.extract_wrapper()

:param pp: dictionary, parameter dictionary
           must have at least "IC_EXT_RANGE" and "GAIN"
:param loc: dictionary, parameter dictionary containing the data
            must have at least "ACC" and "ASS" and "TILT"
:param image: numpy array (2D), the image
:param rnum: int, the order number for this iteration
:param kwargs: additional keywords to pass to the extraction wrapper

        - allowed keywords are:

        range1  (defaults to "IC_EXT_RANGE")
        range2  (defaults to "IC_EXT_RANGE")
        gain    (defaults to "GAIN")

:return cent: numpy array (1D), the extracted pixel values,
             size = image.shape[1] (along the order direction)
:return cpt: int, zero in this case
"""

ExtractTiltWeightOrder = spirouEXTOR.extract_tilt_weight_order
"""
Extract order with tilt and weight using 
spirouEXTOR.extract_wrapper() with mode=1 
(extract_tilt_weight_order_old() is run)

:param pp: dictionary, parameter dictionary
           must have at least "IC_EXT_RANGE", "GAIN" and "SIGDET"
:param loc: dictionary, parameter dictionary containing the data
            must have at least "ACC" and "ASS" and "TILT"
:param image: numpy array (2D), the image
:param orderp: numpy array (2D), the order profile image
:param rnum: int, the order number for this iteration
:param kwargs: additional keywords to pass to the extraction wrapper

        - allowed keywords are:

        range1  (defaults to "IC_EXT_RANGE")
        range2  (defaults to "IC_EXT_RANGE")
        gain    (defaults to "GAIN")
        sigdet  (defaults to "SIGDET")

:return cent: numpy array (1D), the extracted pixel values,
             size = image.shape[1] (along the order direction)
:return cpt: int, zero in this case
"""

ExtractTiltWeightOrder2 = spirouEXTOR.extract_tilt_weight_order2
"""
Extract order with tilt and weight using 
spirouEXTOR.extract_wrapper() with mode=2
(extract_tilt_weight_order() is run)

:param pp: dictionary, parameter dictionary
           must have at least "IC_EXT_RANGE1", "IC_EXT_RANGE2", 
           "GAIN" and "SIGDET"
:param loc: dictionary, parameter dictionary containing the data
            must have at least "ACC" and "ASS" and "TILT"
:param image: numpy array (2D), the image
:param orderp: numpy array (2D), the order profile image
:param rnum: int, the order number for this iteration
:param kwargs: additional keywords to pass to the extraction wrapper

        - allowed keywords are:

        range1  (defaults to "IC_EXT_RANGE1")
        range2  (defaults to "IC_EXT_RANGE2")
        gain    (defaults to "GAIN")
        sigdet  (defaults to "SIGDET")

:return cent: numpy array (1D), the extracted pixel values,
             size = image.shape[1] (along the order direction)
:return cpt: int, zero in this case
"""

ExtractWeightOrder = spirouEXTOR.extract_weight_order
"""
Extract order with weight but without tilt using 
spirouEXTOR.extract_wrapper()

:param pp: dictionary, parameter dictionary
           must have at least "IC_EXT_RANGE", "GAIN" and "SIGDET"
:param loc: dictionary, parameter dictionary containing the data
            must have at least "ACC" and "ASS"
:param image: numpy array (2D), the image
:param orderp: numpy array (2D), the order profile image
:param rnum: int, the order number for this iteration
:param kwargs: additional keywords to pass to the extraction wrapper

        - allowed keywords are:

        range1  (defaults to "IC_EXT_RANGE")
        range2  (defaults to "IC_EXT_RANGE")
        gain    (defaults to "GAIN")
        sigdet  (defaults to "SIGDET")

:return cent: numpy array (1D), the extracted pixel values,
             size = image.shape[1] (along the order direction)
:return cpt: int, zero in this case
"""