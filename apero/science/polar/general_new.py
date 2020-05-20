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
import os

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
        # deal with getting telluric files
        self.is_telluric_corrected = False
        self.telluprops = None
        self._get_tell()
        # deal with getting CCF file
        self.ccfprops = None
        self._get_ccf()
        # deal with getting wavelength solution
        self.waveprops = None
        self._get_wave()

        # TODO: Need to clean with "clean loop" (Line 281 onwards)

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

    def _get_tell(self, **kwargs):
        # set function name
        func_name = display_func(self.params, '_get_tell', __NAME__, 'PolarObj')
        # get parameters from params
        tcorr_key = pcheck(self.params, 'POLAR_TCORR_FILE', 'tcorr_key', kwargs,
                         func_name)
        recon_key = pcheck(self.params, 'POLAR_RECON_FILE', 'recon_key', kwargs,
                           func_name)
        tfiber = pcheck(self.params, 'POLAR_TELLU_FIBER', 'tfiber', kwargs,
                        func_name)
        tcorrect = pcheck(self.params, 'POLAR_TELLU_CORRECT', 'tcorrect',
                          kwargs, func_name)
        # ----------------------------------------------------------------------
        # get file definition
        tfile = core.get_file_definition(tcorr_key, self.params['INSTRUMENT'],
                                         kind='red')
        rfile = core.get_file_definition(recon_key, self.params['INSTRUMENT'],
                                         kind='red')
        # get copies of the file definitions (for filling out)
        tcorr_file = tfile.newcopy(recipe=self.recipe, fiber=tfiber)
        recon_file = rfile.newcopy(recipe=self.recipe, fiber=tfiber)
        # ----------------------------------------------------------------------
        # need to deal with input file being the telluric corrected file
        if self.infile.name == tcorr_file.name:
            # File is already telluric corrected
            self.is_telluric_corrected = True
            # copy telluric file instance
            tcorr_file = self.infile.newcopy(recipe=self.recipe)
            # in this case set recon file to None - we do not need it
            recon_file = None
        else:
            # file is not already telluric corrected
            self.is_telluric_corrected = False
            # ----------------------------------------------------------------------
            # if current fiber doesn't match polar fiber get a copy of the infile
            # for this fiber
            if self.fiber != tfiber:
                # copy file (for update)
                t_infile = self.infile.newcopy(recipe=self.recipe)
                # reconstruct file name forcing new fiber
                t_infile.reconstruct_filename(self.params,
                                              outext=self.infile.filetype,
                                              fiber=tfiber)
            else:
                t_infile = self.infile
            # construct the filenames from file instances
            tcorr_file.construct_filename(self.params, infile=t_infile,
                                          fiber=tfiber)
            recon_file.construct_filename(self.params, infile=t_infile,
                                          fiber=tfiber)
        # ----------------------------------------------------------------------
        # check whether files exist
        if not os.path.exists(tcorr_file.filename):
            return
        if not os.path.exists(recon_file.filename):
            return
        # ----------------------------------------------------------------------
        # create tellu props
        self.telluprops = ParamDict()
        self.telluprops['TCORR_INST'] = tcorr_file
        self.telluprops['TCORR_FILE'] = tcorr_file.filename
        self.telluprops['RECON_INST'] = recon_file
        # add recon file
        if recon_file is not None:
            self.telluprops['RECON_FILE'] = recon_file.filename
        else:
            self.telluprops['RECON_FILE'] = None
        # add sources
        keys = ['TCORR_INST', 'TCORR_FILE', 'RECON_INST', 'RECON_FILE']
        self.telluprops.set_sources(keys, func_name)
        # ----------------------------------------------------------------------
        # load recon only if telluric correction required
        if tcorrect and recon_file is not None:
            recon_file.read_file()
            self.telluprops['RECON_DATA'] = recon_file.data
        else:
            self.telluprops['RECON_DATA'] = None
        # add recon data source
        self.telluprops.set_source('RECON_DATA', func_name)

    def _get_ccf(self, **kwargs):
        # set function name
        func_name = display_func(self.params, '_get_ccf', __NAME__, 'PolarObj')
        # get parameters from params
        ccf_key = pcheck(self.params, 'POLAR_CCF_FILE', 'ccf_key', kwargs,
                         func_name)
        mask_file = pcheck(self.params, 'POLAR_CCF_MASK', 'mask_file', kwargs,
                           func_name)
        pfiber = pcheck(self.params, 'POLAR_CCF_FIBER', 'pfiber', kwargs,
                        func_name)
        ccf_correct = pcheck(self.params, 'POLAR_SOURCERV_CORRECT',
                             'ccf_correct', kwargs, func_name)
        # ----------------------------------------------------------------------
        # get file definition
        cfile = core.get_file_definition(ccf_key, self.params['INSTRUMENT'],
                                             kind='red', fiber=pfiber)
        # get copies of the file definitions (for filling out)
        ccf_file = cfile.newcopy(recipe=self.recipe)
        # push mask to suffix
        suffix = ccf_file.suffix
        mask_file = os.path.basename(mask_file).replace('.mas', '')
        if suffix is not None:
            suffix += '_{0}'.format(mask_file).lower()
        else:
            suffix = '_ccf_{0}'.format(mask_file).lower()
        # ----------------------------------------------------------------------
        # if current fiber doesn't match polar fiber get a copy of the infile
        # for this fiber
        if self.fiber != pfiber:
            # should use telluric file if present
            if self.telluprops is not None:
                # get telluric tcorr file
                tfile = self.telluprops['TCORR_INST']
                # copy file (for update)
                p_infile = tfile.newcopy(recipe=self.recipe)
            else:
                # copy file (for update)
                p_infile = self.infile.newcopy(recipe=self.recipe)
                # reconstruct file name forcing new fiber
                p_infile.reconstruct_filename(self.params,
                                              outext=self.infile.filetype,
                                              fiber=pfiber)
                p_infile.fiber = pfiber
        else:
            p_infile = self.infile
        # ----------------------------------------------------------------------
        # construct the filename from file instance
        ccf_file.construct_filename(self.params, infile=p_infile,
                                    suffix=suffix, fiber=pfiber)
        # deal with no ccf file
        if not os.path.exists(ccf_file):
            return
        # ----------------------------------------------------------------------
        # create ccf props
        self.ccfprops = ParamDict()
        self.ccfprops['CCF_INST'] = ccf_file
        self.ccfprops['CCF_FILE'] = ccf_file.filename
        # set sources
        keys = ['CCF_INST', 'CCF_FILE']
        self.ccfprops.set_sources(keys, func_name)
        # ----------------------------------------------------------------------
        # load source rv
        if ccf_correct:
            ccf_file.read_header()
            self.ccfprops['SOURCE_RV'] = ccf_file.get_key('KW_CCF_RV_CORR')
        else:
            self.ccfprops['SOURCE_RV'] = 0.0
        # set source
        self.ccfprops.set_source('SOURCE_RV', func_name)

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
            if self.ccfprops is not None:
                rv_ccf = self.ccfprops['SOURCE_RV']
            else:
                rv_ccf = 0.0
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

    def _get_tell(self, **kwargs):
        # set function name
        func_name = display_func(self.params, '_get_ccf', __NAME__, 'PolarObj')
        # get parameters from params
        tcorrect = pcheck(self.params, 'POLAR_TELLU_CORRECT', 'tcorrect',
                          kwargs, func_name)

        if self.filename.endswith('e.fits'):
            tcorr_filename = self.filename.replace('e.fits', 't.fits')
            recon_filename = self.filename.replace('e.fits', 't.fits')
        elif self.filename.endswith('t.fits'):
            # set the telluric file to the input filename
            tcorr_filename = self.filename
            # in this case set recon file to None - we do not need it
            recon_filename = None
            # File is already telluric corrected
            self.is_telluric_corrected = True
        else:
            emsg = 'Input file {0} incorrect, cannot get telluric data'
            eargs = [self.filename]
            WLOG(self.params, 'error', emsg.format(*eargs))
            return

        # ----------------------------------------------------------------------
        # create tellu props
        self.telluprops = ParamDict()
        # TODO: Need to get file instance of t.fits (not currently supported)
        self.telluprops['TCORR_INST'] = None
        self.telluprops['TCORR_FILE'] = tcorr_filename
        # TODO: Need to get file instance of t.fits (not currently supported)
        self.telluprops['RECON_INST'] = None
        # add recon file
        if recon_filename is not None:
            self.telluprops['RECON_FILE'] = recon_filename
        else:
            self.telluprops['RECON_FILE'] = None
        # add sources
        keys = ['TCORR_INST', 'TCORR_FILE', 'RECON_INST', 'RECON_FILE']
        self.telluprops.set_sources(keys, func_name)
        # ----------------------------------------------------------------------
        # load recon only if telluric correction required
        if tcorrect and recon_filename is not None:
            thdu = fits.open(tcorr_filename)
            self.telluprops['RECON_DATA'] = np.array(thdu[4].data)
            thdu.close()
        else:
            self.telluprops['RECON_DATA'] = None
        # add recon data source
        self.telluprops.set_source('RECON_DATA', func_name)

    def _get_ccf(self, **kwargs):
        # set function name
        func_name = display_func(self.params, '_get_ccf', __NAME__, 'PolarObj')
        # get parameters from params
        ccf_correct = pcheck(self.params, 'POLAR_SOURCERV_CORRECT',
                             'ccf_correct', kwargs, func_name)
        # ----------------------------------------------------------------------
        # get ccf filename
        if self.filename.endswith('e.fits'):
            ccf_filename = self.filename.replace('e.fits', 'v.fits')
        elif self.filename.endswith('t.fits'):
            ccf_filename = self.filename.replace('t.fits', 'v.fits')
        else:
            emsg = 'Input file {0} incorrect, cannot get CCF'
            eargs = [self.filename]
            WLOG(self.params, 'error', emsg.format(*eargs))
            return
        # ----------------------------------------------------------------------
        # deal with no ccf file
        if not os.path.exists(ccf_filename):
            return
        # ----------------------------------------------------------------------
        # create ccf props
        self.ccfprops = ParamDict()
        # TODO: Need to get file instance of v.fits (not currently supported)
        self.ccfprops['CCF_INST'] = None
        self.ccfprops['CCF_FILE'] = ccf_filename
        # set sources
        keys = ['CCF_INST', 'CCF_FILE']
        self.ccfprops.set_sources(keys, func_name)
        # ----------------------------------------------------------------------
        # load source rv
        if ccf_correct:
            ccf_header = fits.getheader(ccf_filename)
            ccf_key = self.params['KW_CCF_RV_CORR'][0]
            self.ccfprops['SOURCE_RV'] = ccf_header[ccf_key]
        else:
            self.ccfprops['SOURCE_RV'] = 0.0
        # set source
        self.ccfprops.set_source('SOURCE_RV', func_name)

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
    keys = ['STOKES', 'NEXPOSURES', 'VALID_FIBERS', 'VALID_STOKES']
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