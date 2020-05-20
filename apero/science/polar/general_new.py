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
from scipy.interpolate import splrep, splev

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
        self.rawflux = None
        self.raweflux = None
        self.flux = None
        self.eflux = None
        self.filename = None
        self.basename = None
        self.header = None
        self.header0 = None
        self.header1 = None
        self.nbo = None
        self.nbpix = None
        self.mjd = None
        self.dprtype = None
        self.berv = None
        self.bjd = None
        self.bervmax = None
        # get observation properties (flux, berv, etc)
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
        self.mwaveprops = None
        self._get_wave()
        # clean, spline on to master wave solution
        self._clean()
        # get times
        self._get_times()
        # close hdu if possible
        if self.hdu is not None:
            self.hdu.close()

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
        # set the flux data
        self.rawflux = self.infile.data
        self.eflux = np.sqrt(self.flux)
        # set file names and header
        self.filename = self.infile.filename
        self.basename = self.infile.basename
        self.header = self.infile.header
        # get sizes
        self.nbo = self.rawflux.shape[0]
        self.nbpix = self.rawflux.shape[1]
        # get keys from header
        self.mjd = self.infile.get_key('KW_MID_OBS_TIME', dtype=float)
        self.exptime = self.infile.get_key('KW_EXPTIME', dtype=float)
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
        # TODO: Question:    and not by order?
        blaze = blaze / np.nanmax(blaze)
        # props
        self.blazeprops = ParamDict()
        self.blazeprops['BLAZEFILE'] = blaze_file
        self.blazeprops['RAW_BLAZE'] = blaze
        # set source of blaze properties
        bkeys = ['BLAZEFILE', 'RAW_BLAZE']
        self.blazeprops.set_sources(bkeys, func_name)

    def _get_tell(self, **kwargs):
        # set function name
        func_name = display_func(self.params, '_get_tell', __NAME__, 'PolarObj')
        # get parameters from params
        tcorr_key = pcheck(self.params, 'POLAR_TCORR_FILE', 'tcorr_key', kwargs,
                         func_name)
        recon_key = pcheck(self.params, 'POLAR_RECON_FILE', 'recon_key', kwargs,
                           func_name)
        tfiber = pcheck(self.params, 'POLAR_MASTER_FIBER', 'tfiber', kwargs,
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
        # log which telluric files we are using
        wmsg = 'Using Telluric Object File: {0}'
        wargs = [tcorr_file.filename]
        WLOG(self.params, '', wmsg.format(*wargs))
        wmsg = 'Using Telluric Recon File: {0}'
        wargs = [recon_file.filename]
        WLOG(self.params, '', wmsg.format(*wargs))
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
            self.telluprops['RAW_RECON_DATA'] = recon_file.data
        else:
            self.telluprops['RAW_RECON_DATA'] = None
        # add recon data source
        self.telluprops.set_source('RAW_RECON_DATA', func_name)

    def _get_ccf(self, **kwargs):
        # set function name
        func_name = display_func(self.params, '_get_ccf', __NAME__, 'PolarObj')
        # get parameters from params
        ccf_key = pcheck(self.params, 'POLAR_CCF_FILE', 'ccf_key', kwargs,
                         func_name)
        mask_file = pcheck(self.params, 'POLAR_CCF_MASK', 'mask_file', kwargs,
                           func_name)
        pfiber = pcheck(self.params, 'POLAR_MASTER_FIBER', 'pfiber', kwargs,
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
        # log which telluric files we are using
        wmsg = 'Using CCF File: {0}'
        wargs = [ccf_file.filename]
        WLOG(self.params, '', wmsg.format(*wargs))
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

    def _get_wave(self, **kwargs):
        """
        Get wave solution assuming we have a DRS output file as input (infile)
        :return:
        """
        # set function name
        func_name = display_func(self.params, '_get_wave', __NAME__, 'PolarObj')
        # get parameters from params
        mfiber = pcheck(self.params, 'POLAR_MASTER_FIBER', 'pfiber', kwargs,
                        func_name)
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
        # ------------------------------------------------------------------
        # get master fiber
        self.mwaveprops = wave.get_wavesolution(self.params, self.recipe,
                                       fiber=mfiber, infile=self.infile)

    def _clean(self, **kwargs):
        # set function name
        func_name = display_func(self.params, '_clean', __NAME__, 'PolarObj')
        # get parameters from params
        tcorrect = pcheck(self.params, 'POLAR_TELLU_CORRECT', 'tcorrect',
                          kwargs, func_name)
        # ------------------------------------------------------------------
        # get master wavemap
        mwavemap = self.mwaveprops['WAVEMAP']
        wavemap = self.waveprops['WAVEMAP']
        # ------------------------------------------------------------------
        # set up arrays as all NaN
        self.flux = np.zeros_like(self.rawflux) * np.nan
        self.eflux = np.zeros_like(self.rawflux) * np.nan
        blazearr = np.zeros_like(self.rawflux) * np.nan
        # get blaze array
        rblazearr = self.blazeprops['RAW_BLAZE']
        # get telluric recon array
        if tcorrect and not self.is_telluric_corrected:
            rreconarr = self.telluprops['RAW_RECON_DATA']
            reconarr = np.zeros_like(rreconarr) * np.nan
        else:
            rreconarr, reconarr = None, None
        # ------------------------------------------------------------------
        # loop around orders
        for order_num in range(self.nbo):
            # ------------------------------------------------------------------
            # identify NaN values
            clean = np.isfinite(self.rawflux[order_num])
            # if we don't have any finite values skip this order
            if np.sum(clean) == 0:
                continue
            # ------------------------------------------------------------------
            # get clean vectors for this order
            # ------------------------------------------------------------------
            # get this orders wave solution
            owave = wavemap[order_num][clean]
            # get this orders raw flux
            orflux = self.rawflux[order_num][clean]
            # get this orders raw blaze
            orblaze = rblazearr[order_num][clean]
            # get the master fiber wave solution for this order
            omwave = mwavemap[order_num][clean]
            # get the recon spectra
            if tcorrect and not self.is_telluric_corrected:
                orrecon = [order_num]
                tclean = np.isfinite(orrecon)
            else:
                orrecon, tclean = None, None
            # ------------------------------------------------------------------
            # get splines
            # ------------------------------------------------------------------
            # interpolate flux data to match wavelength grid of first exposure
            tck = splrep(owave, orflux, s=0)
            # interpolate blaze data to match wavelength grid of first exposure
            btck = splrep(owave, orblaze, s=0)
            # interpolate recon data to match wavelength grid of first exposure
            #   note that telluric has own clean mask (tclean)
            if tcorrect and not self.is_telluric_corrected:
                ttck = splrep(wavemap[order_num][tclean], orrecon[tclean], s=0)
            else:
                ttck = None
            # ------------------------------------------------------------------
            # only keep wavelengths within master fiber limits
            wlmask = (omwave > np.min(owave)) & (omwave < np.max(owave))
            # ------------------------------------------------------------------
            # get vectors splined on the master fiber wave solution
            # ------------------------------------------------------------------
            # update blaze
            oblaze = splev(omwave[wlmask], btck, der=0)
            # update flux data
            oflux = splev(omwave[wlmask], tck, der=0)
            # normalize by blaze
            oflux = oflux / oblaze
            # update flux error data
            # TODO: Question: Why sqrt(flux/blaze/blaze) ?
            oeflux = np.sqrt(oflux / oblaze)
            # update telluric (if required)
            if reconarr is not None:
                # TODO: Question: wlmask not used for recon why?
                orecon = splev(mwavemap[order_num][tclean], ttck, der=0)
            else:
                orecon = None
            # ------------------------------------------------------------------
            # get vectors splined on the master fiber wave solution
            # ------------------------------------------------------------------
            # update vectors
            self.flux[order_num][clean] = oflux
            self.eflux[order_num][clean] = oeflux
            blazearr[order_num][clean] = oblaze
            if reconarr is not None:
                reconarr[order_num][tclean] = orecon
                # telluric correct flux/eflux
                tcorr = self.flux[order_num] / reconarr[order_num]
                self.flux[order_num] = tcorr

        # push blaze back into props
        self.blazeprops['BLAZE'] = blazearr
        # push recon back into props if telluric correction required
        if tcorrect and not self.is_telluric_corrected:
            self.telluprops['RECON_DATA'] = reconarr

    def _get_times(self):
        # TODO: Fill in this function (Line 346 in spirouPolar.py)
        pass

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
        flux_key = FLUX_HDU_KEY.format(fiber=self.fiber)
        self.rawflux = np.array(self.hdu[flux_key].data)
        self.raweflux = np.sqrt(self.rawflux)
        self.filename = self.infile.filename
        self.basename = self.infile.basename
        # get sizes
        self.nbo = self.rawflux.shape[0]
        self.nbpix = self.raweflux.shape[1]
        # get keys from header
        self.mjd = self.header1[self.params['KW_MID_OBS_TIME'][0]]
        self.exptime = self.header1[self.params['KW_EXPTIME'][0]]
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
        # log which telluric files we are using
        wmsg = 'Using blaze from HDU: {0}'
        wargs = [blaze_key]
        WLOG(self.params, '', wmsg.format(*wargs))
        # load blaze
        blaze = np.array(self.hdu[blaze_key].data)
        blaze_file = 'HDU[{0}]'.format(blaze_key)
        # normalise
        # TODO: Question: Are you sure you want to normalise by the whole array
        # TODO: Qusestion:    and not by order?
        blaze = blaze / np.nanmax(blaze)
        # props
        self.blazeprops = ParamDict()
        self.blazeprops['BLAZEFILE'] = blaze_file
        self.blazeprops['RAW_BLAZE'] = blaze
        # set source of blaze properties
        bkeys = ['BLAZEFILE', 'RAW_BLAZE']
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
        # log which telluric files we are using
        wmsg = 'Using Telluric Object File: {0}'
        wargs = [tcorr_filename]
        WLOG(self.params, '', wmsg.format(*wargs))
        wmsg = 'Using Telluric Recon File: {0}'
        wargs = [recon_filename]
        WLOG(self.params, '', wmsg.format(*wargs))
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
            self.telluprops['RAW_RECON_DATA'] = np.array(thdu[4].data)
            thdu.close()
        else:
            self.telluprops['RAW_RECON_DATA'] = None
        # add recon data source
        self.telluprops.set_source('RAW_RECON_DATA', func_name)

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
        # log which telluric files we are using
        wmsg = 'Using CCF File: {0}'
        wargs = [ccf_filename]
        WLOG(self.params, '', wmsg.format(*wargs))
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

    def _get_wave(self, **kwargs):
        """
        Get wave solution assuming we have a CADC output file as input (infile)
        :return:
        """
        # set function name
        func_name = display_func(self.params, '_get_wave', __NAME__, 'PolarObj')
        # get parameters from params
        mfiber = pcheck(self.params, 'POLAR_MASTER_FIBER', 'pfiber', kwargs,
                        func_name)
        # ----------------------------------------------------------------------
        # load wavelength solution for this fiber
        # ----------------------------------------------------------------------
        wavekey = WAVE_HDU_KEY.format(fiber=self.fiber)
        wavemap = np.array(self.hdu[wavekey].data)
        # log which telluric files we are using
        wmsg = 'Using wave from HDU: {0}'
        wargs = [wavekey]
        WLOG(self.params, '', wmsg.format(*wargs))
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
        # ------------------------------------------------------------------
        # get master fiber
        mwavekey = WAVE_HDU_KEY.format(fiber=mfiber)
        mwavemap = np.array(self.hdu[mwavekey].data)
        # ------------------------------------------------------------------
        # load into wave props
        self.mwaveprops = ParamDict()
        self.mwaveprops['WAVEMAP'] = mwavemap
        self.mwaveprops['WAVEFILE'] = 'HDU[{0}]'.format(mwavekey)
        # add sources
        mwkeys = ['WAVEMAP', 'WAVEFILE']
        self.mwaveprops.set_sources(mwkeys, func_name)

    def _get_times(self):
        # TODO: Fill in this function (Line 346 in spirouPolar.py)
        pass

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