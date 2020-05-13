#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2020-05-13

@author: cook
"""
import numpy as np
import warnings
from astropy.io import fits

from apero import core
from apero.core import math as mp
from apero import lang
from apero.core import constants
from apero.core.core import drs_log
from apero.core.core import drs_file
from apero.io import drs_table
from apero.science.calib import flat_blaze
from apero.science.calib import wave
from apero.science import extract


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'polar.general.py'
__INSTRUMENT__ = 'None'
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# get param dict
ParamDict = constants.ParamDict
DrsFitsFile = drs_file.DrsFitsFile
# Get Logging function
WLOG = core.wlog
# Get function string
display_func = drs_log.display_func
# Get the text types
TextEntry = lang.drs_text.TextEntry
TextDict = lang.drs_text.TextDict
# alias pcheck
pcheck = core.pcheck


# define output keys
BLAZE_HDU_KEY = 'Blaze{fiber}'
FLUX_HDU_KEY = 'Flux{fiber}'
WAVE_HDU_KEY = 'WAVE{fiber}'


# =============================================================================
# Define class
# =============================================================================
class PolarObj:
    def __init__(self, params, recipe, infile, fiber, exposure,
                 stoke, seq, seqtot):
        # store shallow copy of params/recipe
        self.params = params
        self.recipe = recipe
        # get parameters from call
        self.infile = infile
        self.fiber = fiber
        self.exposure = exposure
        self.stokes = stoke
        self.sequence = seq
        self.sequencetot = seqtot
        # get name
        self.name = self.__gen_key__()
        # deal with getting properties
        self.hdu = None   # not used in PolarObj but used in PolarObjOut
        self.data = None
        self.filename = None
        self.basename = None
        self.header = None
        self.header0 = None
        self.header1 = None
        self.mjd = None
        self.dprtype = None
        self.berv = None
        self.bjd = None
        self.bervmax = None
        self._get_properties()
        # deal with blaze solution
        self.blazeprops = None
        self._get_blaze()
        # deal with getting CCF file
        self.ccfprops = None
        self._get_ccf()
        # deal with getting wavelength solution
        self.waveprops = None
        self._get_wave()

    def __gen_key__(self):
        return '{0}_{1}'.format(self.fiber, self.exposure)

    def __str__(self):
        return 'PolarObj[{0}]'.format(self.name)

    def __repr__(self):
        return 'PolarObj[{0}]'.format(self.name)

    def _get_properties(self):
        """
        Get properties assuming we have a DRS output file as input (infile)
        :return:
        """
        self.data = self.infile.data
        self.filename = self.infile.filename
        self.basename = self.infile.basename
        self.header = self.infile.header
        # get keys from header
        self.mjd = self.infile.get_key('KW_MID_OBS_TIME', dtype=float)
        self.dprtype = self.infile.get_key('KW_DPRTYPE', dtype=str)
        # get berv properties
        bprops = extract.get_berv(self.params, self.infile,
                                  dprtype=self.dprtype)
        # store berv properties
        self.berv = bprops['USE_BERV']
        self.bjd = bprops['USE_BJD']
        self.bervmax = bprops['USE_BERV_MAX']

    def _get_blaze(self):
        """
        Get blaze assuming we have a DRS output file as input (infile)
        :return:
        """
        # set function name
        func_name = display_func(self.params, '_get_blaze', __NAME__,
                                 'PolarObj')
        # load
        blaze_file, blaze = flat_blaze.get_blaze(self.params, fiber=self.fiber,
                                                 header=self.header)
        # normalise
        # TODO: Question: Are you sure you want to normalise by the whole array
        # TODO: Qusestion:    and not by order?
        blaze = blaze / np.nanmax(blaze)
        # props
        self.blazeprops = ParamDict()
        self.blazeprops['BLAZEFILE'] = blaze_file
        self.blazeprops['BLAZE'] = blaze
        # set source of blaze properties
        bkeys = ['BLAZEFILE', 'BLAZE']
        self.blazeprops.set_sources(bkeys, func_name)

    def _get_ccf(self):
        # set function name
        func_name = display_func(self.params, '_get_ccf', __NAME__, 'PolarObj')
        pass

    def _get_tell(self):
        # set function name
        func_name = display_func(self.params, '_get_ccf', __NAME__, 'PolarObj')
        pass

    def _get_wave(self):
        """
        Get wave solution assuming we have a DRS output file as input (infile)
        :return:
        """
        # set function name
        func_name = display_func(self.params, '_get_wave', __NAME__, 'PolarObj')
        # ----------------------------------------------------------------------
        # load wavelength solution for this fiber
        # ----------------------------------------------------------------------
        wprops = wave.get_wavesolution(self.params, self.recipe,
                                       fiber=self.fiber, infile=self.infile)
        # get a copy of the wave map
        wavemap = np.array(wprops['WAVEMAP'])
        # ------------------------------------------------------------------
        if self.params['POLAR_BERV_CORRECT']:
            # get the RV from the CCF properties
            rv_ccf = self.ccfprops['SOURCE_RV']
            # get the berv
            berv = self.berv
            # calculate the shifts
            wprops['WAVE_SHIFT'] = mp.relativistic_waveshift(rv_ccf - berv)
            # add a new wave map
            wprops['WAVEMAP_S'] = wavemap * wprops['WAVE_SHIFT']
        else:
            wprops['WAVE_SHIFT'] = 0.0
            wprops['WAVEMAP_S'] = wavemap
        # add sources
        wkeys = ['WAVE_SHIFT', 'WAVEMAP_S']
        wprops.set_sources(wkeys, func_name)
        # ------------------------------------------------------------------
        # push wprops into self
        self.waveprops = wprops



class PolarObjOut(PolarObj):


    def _get_properties(self):
        """
        Get properties assuming we have a CADC output file as input (infile)
        :return:
        """
        self.hdu = fits.open(self.infile.filename)
        # get the headres
        self.header0 = self.hdu[0].header
        self.header1 = self.hdu[1].header
        self.data = self.hdu.data
        self.filename = self.infile.filename
        self.basename = self.infile.basename
        # get keys from header
        self.mjd = self.header1[self.params['KW_MID_OBS_TIME'][0]]
        self.dprtype = self.header1[self.params['KW_DPRTYPE'][0]]
        # get berv properties
        bprops = extract.get_berv(self.params, header=self.header1,
                                  dprtype=self.dprtype)
        # store berv properties
        self.berv = bprops['USE_BERV']
        self.bjd = bprops['USE_BJD']
        self.bervmax = bprops['USE_BERV_MAX']


    def _get_blaze(self):
        """
        Get blaze assuming we have a CADC output file as input (infile)
        :return:
        """
        # set function name
        func_name = display_func(self.params, '_get_blaze', __NAME__,
                                 'PolarObjOut')
        # get blaze key
        blaze_key = BLAZE_HDU_KEY.format(fiber=self.fiber)
        # load blaze
        blaze = self.hdu[blaze_key].data
        blaze_file = 'HDU[{0}]'.format(blaze_key)
        # normalise
        # TODO: Question: Are you sure you want to normalise by the whole array
        # TODO: Qusestion:    and not by order?
        blaze = blaze / np.nanmax(blaze)
        # props
        self.blazeprops = ParamDict()
        self.blazeprops['BLAZEFILE'] = blaze_file
        self.blazeprops['BLAZE'] = blaze
        # set source of blaze properties
        bkeys = ['BLAZEFILE', 'BLAZE']
        self.blazeprops.set_sources(bkeys, func_name)

    def _get_ccf(self):
        # set function name
        func_name = display_func(self.params, '_get_ccf', __NAME__, 'PolarObj')
        pass

    def _get_tell(self):
        # set function name
        func_name = display_func(self.params, '_get_ccf', __NAME__, 'PolarObj')
        pass

    def _get_wave(self):
        """
        Get wave solution assuming we have a CADC output file as input (infile)
        :return:
        """
        # set function name
        func_name = display_func(self.params, '_get_wave', __NAME__, 'PolarObj')
        # ----------------------------------------------------------------------
        # load wavelength solution for this fiber
        # ----------------------------------------------------------------------
        wavekey = WAVE_HDU_KEY.format(fiber=self.fiber)
        wavemap = self.hdu[wavekey].data
        # ------------------------------------------------------------------
        # load into wave props
        wprops = ParamDict()
        wprops['WAVEMAP'] = wavemap
        wprops['WAVEFILE'] = 'HDU[{0}]'.format(wavekey)
        # add sources
        wkeys = ['WAVEMAP', 'WAVEFILE']
        wprops.set_sources(wkeys, func_name)
        # ------------------------------------------------------------------
        if self.params['POLAR_BERV_CORRECT']:
            # get the RV from the CCF properties
            rv_ccf = self.ccfprops['SOURCE_RV']
            # get the berv
            berv = self.berv
            # calculate the shifts
            wprops['WAVE_SHIFT'] = mp.relativistic_waveshift(rv_ccf - berv)
            # add a new wave map
            wprops['WAVEMAP_S'] = wavemap * wprops['WAVE_SHIFT']
        else:
            wprops['WAVE_SHIFT'] = 0.0
            wprops['WAVEMAP_S'] = wavemap

        # add sources
        wkeys = ['WAVE_SHIFT', 'WAVEMAP_S']
        wprops.set_sources(wkeys, func_name)
        # ------------------------------------------------------------------
        # push wprops into self
        self.waveprops = wprops




# =============================================================================
# Define functions
# =============================================================================
def validate_polar_files(params, recipe, infiles, **kwargs):
    # set function name
    func_name = display_func(params, 'validate_polar_files', __NAME__)
    # get the number of infiles
    num_files = len(infiles)
    arg_names = ['--exp1', '--exp2', '--exp3', '--exp4']
    # get parameters from params
    valid_fibers = pcheck(params, 'POLAR_VALID_FIBERS', 'valid_fibers', kwargs,
                          func_name, mapf='list', dtype=str)
    valid_stokes = pcheck(params, 'POLAR_VALID_STOKES', 'valid_stokes', kwargs,
                          func_name, mapf='list', dtype=str)
    # ----------------------------------------------------------------------
    # storage dictionary
    pobjects = ParamDict()
    stokes, fibers, basenames = [], [] ,[]
    # loop around files
    for it in range(num_files):
        # print file iteration progress
        core.file_processing_update(params, it, num_files)
        # ge this iterations file
        infile = infiles[it]
        # extract polar values and validate file
        pout = valid_polar_file(params, infile)
        stoke, exp, seq, seqtot, fiber, valid = pout
        # skip any invalid files
        if not valid:
            # log error
            # TODO: move the language database
            emsg = ('File in argument {0} not valid for polar recipe. '
                    '\n\tFile = {1}')
            eargs = [arg_names[it], infile.filename]
            WLOG(params, 'error', emsg.format(*eargs))
        # ------------------------------------------------------------------
        # log file addition
        wargs = [infile.basename, fiber, stoke, exp, seq, seqtot]
        WLOG(params, '', TextEntry('40-021-00001', args=wargs))
        # ------------------------------------------------------------------
        # get polar object for each
        pobj = PolarObj(params, recipe, infile=infile, fiber=fiber,
                        exposure=exp, stoke=stoke, seq=seq, seqtot=seqtot)
        # get name
        name = pobj.name
        # push into storage dictionary
        pobjects[name] = pobj
        # set source
        pobjects.set_source(name, func_name)
        # append lists (for checks)
        stokes.append(stoke)
        fibers.append(fiber)
        basenames.append(infile.basename)
    # ----------------------------------------------------------------------
    # set the output parameters
    props = ParamDict()
    props['NEXPOSURES'] = len(infiles)
    props['STOKES'] = np.unique(stokes)[0]
    props['VALID_FIBERS'] = valid_fibers
    props['VALID_STOKES'] = valid_stokes
    # set sources
    keys = ['STOKES', 'NEXPOSURES', 'MIN_FILES', 'VALID_FIBERS', 'VALID_STOKES']
    props.set_sources(keys, func_name)
    # ----------------------------------------------------------------------
    # return polar object and properties
    return pobjects, props


def valid_polar_file(params, infile, **kwargs):
    """
    Read and extract parameters from cmmtseq string from header key at
    KW_CMMTSEQ

    for spirou the format is as follows:
       {0} exposure {1}, sequence {2} of {3}
     where {0} is the stokes parameter
     where {1} is the exposure number
     where {2} is the sequence number
     where {3} is the total number of sequences

    :param params: ParamDict, the parameter dictionary
    :param infile: DrsFitsFile, the Drs Fits file to get the header key from

    :type params: ParamDict
    :type infile: DrsFitsFile

    :return:
    """
    # set function name
    func_name = display_func(params, 'read_cmmtseq', __NAME__)
    # assume valid at first
    valid = True
    # get values from parameters
    valid_fibers = pcheck(params, 'POLAR_VALID_FIBERS', 'valid_fibers', kwargs,
                          func_name, mapf='list', dtype=str)
    valid_stokes = pcheck(params, 'POLAR_VALID_STOKES', 'valid_stokes', kwargs,
                          func_name, mapf='list', dtype=str)
    # ----------------------------------------------------------------------
    # get cmmtseq key
    cmmtseq = infile.get_key('KW_CMMTSEQ')
    # get fiber type
    fiber = infile.get_key('KW_FIBER')
    # ----------------------------------------------------------------------
    # deal with bad file
    if cmmtseq in [None, '', 'None']:
        eargs = [params['KW_CMMTSEQ'][0], infile.filename]
        WLOG(params, 'warning', TextEntry('10-021-00004', args=eargs))
        return None, None, None, None, fiber, False
    # ----------------------------------------------------------------------
    # split to string by white spaces
    split = cmmtseq.split()
    # ----------------------------------------------------------------------
    # get stokes parameter (first letter)
    stoke_parameter = split[0]
    # ----------------------------------------------------------------------
    # get exposure number
    exposure = split[2].strip(',')
    try:
        exposure = int(exposure)
    except ValueError:
        eargs = [params['KW_CMMTSEQ'][0], cmmtseq]
        WLOG(params, 'warning', TextEntry('10-021-00001', args=eargs))
        valid = False
    # ----------------------------------------------------------------------
    # get the sequence number
    sequence = split[4]
    try:
        sequence = int(sequence)
    except ValueError:
        eargs = [params['KW_CMMTSEQ'][0], cmmtseq]
        WLOG(params, 'warning', TextEntry('10-021-00002', args=eargs))
        valid = False
    # ----------------------------------------------------------------------
    # get the total number of sequences
    total = split[6]
    try:
        total = int(total)
    except ValueError:
        eargs = [params['KW_CMMTSEQ'][0], cmmtseq]
        WLOG(params, 'warning', TextEntry('10-021-00003', args=eargs))
        valid = False
    # ----------------------------------------------------------------------
    # deal with fiber type
    if fiber not in valid_fibers:
        eargs = [fiber, ', '.join(valid_fibers), infile.filename]
        WLOG(params, 'warning', TextEntry('10-021-00005', args=eargs))
        valid = False
    # ----------------------------------------------------------------------
    # deal with stokes parameters - check parameter is valid
    if stoke_parameter not in valid_stokes:
        eargs = [stoke_parameter, ', '.join(valid_stokes), infile.filename]
        WLOG(params, 'warning', TextEntry('10-021-00006', args=eargs))
        valid = False
    # ----------------------------------------------------------------------
    # return extracted parameters
    if not valid:
        return None, None, None, None, fiber, False
    else:
        return stoke_parameter, exposure, sequence, total, fiber, valid


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================