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
from astropy import units as uu
import os
from scipy.interpolate import splrep, splev, UnivariateSpline, interp1d
from scipy import stats, signal

from apero.base import base
from apero.base.drs_exceptions import DrsCodedException
from apero.core import math as mp
from apero import lang
from apero.core import constants
from apero.core.core import drs_log, drs_file
from apero.core.utils import drs_startup
from apero.science.calib import flat_blaze
from apero.science.calib import wave
from apero.science import extract

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'polar.general.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get param dict
ParamDict = constants.ParamDict
DrsFitsFile = drs_file.DrsFitsFile
# Get Logging function
WLOG = drs_log.wlog
# Get function string
display_func = drs_log.display_func
# Get the text types
textentry = lang.textentry
# alias pcheck
pcheck = constants.PCheck(wlog=WLOG)
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
        self.hdu = None  # not used in PolarObj but used in PolarObjOut
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
        self.rawflux = self.infile.get_data()
        self.eflux = np.sqrt(self.rawflux)
        # set file names and header
        self.filename = self.infile.filename
        self.basename = self.infile.basename
        self.header = self.infile.get_header()
        # get sizes
        self.nbo = self.rawflux.shape[0]
        self.nbpix = self.rawflux.shape[1]
        # get keys from header
        self.mjd = self.infile.get_hkey('KW_MID_OBS_TIME', dtype=float)
        self.exptime = self.infile.get_hkey('KW_EXPTIME', dtype=float)
        self.exptime_hrs = (self.exptime * uu.s).to(uu.hr).value
        self.mjdstart = self.mjd - (self.exptime / 2)
        self.mjdend = self.mjd + (self.exptime / 2)
        self.dprtype = self.infile.get_hkey('KW_DPRTYPE', dtype=str)
        # get berv properties
        bprops = extract.get_berv(self.params, self.infile)
        # store berv properties
        self.berv = bprops['USE_BERV']
        self.bjd = bprops['USE_BJD']
        self.bervmax = bprops['USE_BERV_MAX']
        self.bervstart = self.berv - (self.exptime / 2)
        self.bervend = self.berv + (self.exptime / 2)

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
        tfile = drs_startup.get_file_definition(tcorr_key,
                                                self.params['INSTRUMENT'],
                                                kind='red')
        rfile = drs_startup.get_file_definition(recon_key,
                                                self.params['INSTRUMENT'],
                                                kind='red')
        # get copies of the file definitions (for filling out)
        tcorr_file = tfile.newcopy(params=self.params, fiber=tfiber)
        recon_file = rfile.newcopy(params=self.params, fiber=tfiber)
        # ----------------------------------------------------------------------
        # need to deal with input file being the telluric corrected file
        if self.infile.name == tcorr_file.name:
            # File is already telluric corrected
            self.is_telluric_corrected = True
            # copy telluric file instance
            tcorr_file = self.infile.newcopy(params=self.params)
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
                t_infile = self.infile.newcopy(params=self.params)
                # reconstruct file name forcing new fiber
                t_infile.reconstruct_filename(self.params,
                                              outext=self.infile.filetype,
                                              fiber=tfiber)
            else:
                t_infile = self.infile
            # construct the filenames from file instances
            tcorr_file.construct_filename(infile=t_infile, fiber=tfiber)
            recon_file.construct_filename(infile=t_infile, fiber=tfiber)
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
            self.telluprops['RAW_RECON_DATA'] = recon_file.get_data()
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
        cfile = drs_startup.get_file_definition(ccf_key,
                                                self.params['INSTRUMENT'],
                                                kind='red', fiber=pfiber)
        # get copies of the file definitions (for filling out)
        ccf_file = cfile.newcopy(params=self.params)
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
                p_infile = tfile.newcopy(params=self.params)
            else:
                # copy file (for update)
                p_infile = self.infile.newcopy(params=self.params)
                # reconstruct file name forcing new fiber
                p_infile.reconstruct_filename(outext=self.infile.filetype,
                                              fiber=pfiber)
                p_infile.fiber = pfiber
        else:
            p_infile = self.infile
        # ----------------------------------------------------------------------
        # construct the filename from file instance
        ccf_file.construct_filename(infile=p_infile, suffix=suffix,
                                    fiber=pfiber)
        # deal with no ccf file
        if not os.path.exists(ccf_file.filename):
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
            self.ccfprops['SOURCE_RV'] = ccf_file.get_hkey('KW_CCF_RV_CORR')
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
        database = kwargs.get('database', None)
        # ----------------------------------------------------------------------
        # load wavelength solution for this fiber
        # ----------------------------------------------------------------------
        wprops = wave.get_wavesolution(self.params, self.recipe,
                                       fiber=self.fiber, infile=self.infile,
                                       database=database)
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
                                                fiber=mfiber,
                                                infile=self.infile,
                                                database=database)

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
                orrecon = rreconarr[order_num]
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
            ttck = None
            if tcorrect and not self.is_telluric_corrected:
                if np.sum(tclean) > 0:
                    ttck = splrep(wavemap[order_num][tclean], orrecon[tclean],
                                  s=0)
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
            with warnings.catch_warnings(record=True) as _:
                oeflux = np.sqrt(oflux / oblaze)
            # update telluric (if required)
            if reconarr is not None and ttck is not None:
                # TODO: Question: wlmask not used for recon why?
                orecon = splev(mwavemap[order_num][tclean], ttck, der=0)
            else:
                orecon = None
            # ------------------------------------------------------------------
            # get vectors splined on the master fiber wave solution
            # ------------------------------------------------------------------
            # update vectors
            self.flux[order_num][clean][wlmask] = oflux
            self.eflux[order_num][clean][wlmask] = oeflux
            blazearr[order_num][clean][wlmask] = oblaze
            if reconarr is not None and orecon is not None:
                reconarr[order_num][tclean] = orecon
                # telluric correct flux/eflux
                tcorr = self.flux[order_num] / reconarr[order_num]
                self.flux[order_num] = tcorr

        # push blaze back into props
        self.blazeprops['BLAZE'] = blazearr
        # push recon back into props if telluric correction required
        if tcorrect and not self.is_telluric_corrected:
            self.telluprops['RECON_DATA'] = reconarr


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
        self.rawflux = np.array(self.hdu[flux_key].get_data())
        self.raweflux = np.sqrt(self.rawflux)
        self.filename = self.infile.filename
        self.basename = self.infile.basename
        # get sizes
        self.nbo = self.rawflux.shape[0]
        self.nbpix = self.raweflux.shape[1]
        # get keys from header
        self.mjd = self.header1[self.params['KW_MID_OBS_TIME'][0]]
        self.exptime = self.header1[self.params['KW_EXPTIME'][0]]
        self.exptime_hrs = (self.exptime * uu.s).to(uu.hr).value
        self.mjdstart = self.mjd - (self.exptime / 2)
        self.mjdend = self.mjd + (self.exptime / 2)
        self.dprtype = self.header1[self.params['KW_DPRTYPE'][0]]
        # get berv properties
        bprops = extract.get_berv(self.params, header=self.header1)
        # store berv properties
        self.berv = bprops['USE_BERV']
        self.bjd = bprops['USE_BJD']
        self.bervmax = bprops['USE_BERV_MAX']
        self.bervstart = self.berv - (self.exptime / 2)
        self.bervend = self.berv + (self.exptime / 2)

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
        blaze = np.array(self.hdu[blaze_key].get_data())
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
            self.telluprops['RAW_RECON_DATA'] = np.array(thdu[4].get_data())
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
        wavemap = np.array(self.hdu[wavekey].get_data())
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
        mwavemap = np.array(self.hdu[mwavekey].get_data())
        # ------------------------------------------------------------------
        # load into wave props
        self.mwaveprops = ParamDict()
        self.mwaveprops['WAVEMAP'] = mwavemap
        self.mwaveprops['WAVEFILE'] = 'HDU[{0}]'.format(mwavekey)
        # add sources
        mwkeys = ['WAVEMAP', 'WAVEFILE']
        self.mwaveprops.set_sources(mwkeys, func_name)


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
    stokes, fibers, basenames = [], [], []
    # loop around files
    for it in range(num_files):
        # print file iteration progress
        drs_startup.file_processing_update(params, it, num_files)
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
        WLOG(params, '', textentry('40-021-00001', args=wargs))
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
    # get time related information
    ptimes = polar_time(params, pobjects)
    # ----------------------------------------------------------------------
    # set the output parameters
    props = ParamDict()
    props['NEXPOSURES'] = len(infiles)
    props['STOKES'] = np.unique(stokes)[0]
    props['VALID_FIBERS'] = valid_fibers
    props['VALID_STOKES'] = valid_stokes
    props['PTIMES'] = ptimes
    # set sources
    keys = ['STOKES', 'NEXPOSURES', 'VALID_FIBERS', 'VALID_STOKES', 'PTIMES']
    props.set_sources(keys, func_name)
    # ----------------------------------------------------------------------
    # return polar object and properties
    return pobjects, props


def calculate_polarimetry(params, pobjs, props, **kwargs):
    """
    Function to call functions to calculate polarimetry either using
    the Ratio or Difference methods.

    :param params: parameter dictionary, ParamDict containing constants
        Must contain at least:
            POLAR_METHOD: string, to define polar method "Ratio" or
                             "Difference"
    :param pobjs: list of polar objects
    :param props: ParamDict, the polar properties dictionary

    :return polarfunc: function, either polarimetry_diff_method(p, loc)
                       or polarimetry_ratio_method(p, loc)
    """
    # set function name
    func_name = display_func(params, 'calculate_polarimetry', __NAME__)
    # get parameters from params/kwargs
    method = pcheck(params, 'POLAR_METHOD', 'method', kwargs, func_name)
    # if method is not a string then break here
    if not isinstance(method, str):
        eargs = [method]
        WLOG(params, 'error', textentry('09-021-00006', args=eargs))
    # decide which method to use
    if method.lower() == 'difference':
        return polar_diff_method(params, pobjs, props)
    elif method.lower() == 'ratio':
        return polar_ratio_method(params, pobjs, props)
    else:
        eargs = [method]
        WLOG(params, 'error', textentry('09-021-00007', args=eargs))
        return 0


def calculate_stokes_i(params, pobjs, pprops, **kwargs):
    """
    Function to calculate the Stokes I polarization

    :param params: ParamDict, parameter dictionary of constants
    :param pobjs: dict, dictionary of polar object instance
    :param pprops: parameter dictionary, ParamDict containing data
        Must contain at least:
            NEXPOSURES: int, number of exposures in polar sequence

    :return pprops: parameter dictionary, the updated parameter dictionary
        Adds/updates the following:
            STOKESI: numpy array (2D), the Stokes I parameters, same shape as
                     DATA
            STOKESIERR: numpy array (2D), the Stokes I error parameters, same
                        shape as DATA
    """
    # set the function
    func_name = display_func(params, 'calculate_stokes_i', __NAME__)
    # log start of polarimetry calculations
    WLOG(params, '', textentry('40-021-00003'))
    # get parameters from params
    interpolate_flux = pcheck(params, 'POLAR_INTERPOLATE_FLUX',
                              'interpolate_flux', kwargs, func_name)
    # get parameters from props
    nexp = pprops['NEXPOSURES']
    # get the first file for reference
    pobj = pobjs['A_1']
    # storage of stokes parameters
    stokes_i = np.zeros(pobj.infile.shape)
    stokes_i_err = np.zeros(pobj.infile.shape)
    # storage of flux and variance
    flux, var = [], []
    # loop around exposures
    for it in range(1, int(nexp) + 1):
        # get a and b data for this exposure
        if interpolate_flux:
            data_a = pobjs['A_{0}'.format(it)].flux
            data_b = pobjs['B_{0}'.format(it)].flux
            edata_a = pobjs['A_{0}'.format(it)].eflux
            edata_b = pobjs['B_{0}'.format(it)].eflux
        else:
            data_a = pobjs['A_{0}'.format(it)].rawflux
            data_b = pobjs['B_{0}'.format(it)].rawflux
            edata_a = pobjs['A_{0}'.format(it)].raweflux
            edata_b = pobjs['B_{0}'.format(it)].raweflux
        # Calculate sum of fluxes from fibers A and B
        flux_ab = data_a + data_b
        # Save A+B flux for each exposure
        flux.append(flux_ab)
        # Calculate the variances for fiber A+B, assuming Poisson noise
        # only. In fact the errors should be obtained from extraction, i.e.
        # from the error extension in the e2ds files.
        var_ab = edata_a ** 2 + edata_b ** 2
        # Save varAB = sigA^2 + sigB^2, ignoring cross-correlated terms
        var.append(var_ab)

    # Sum fluxes and variances from different exposures
    for it in range(len(flux)):
        stokes_i += flux[it]
        stokes_i_err += var[it]
    # Calcualte errors -> sigma = sqrt(variance)
    with warnings.catch_warnings(record=True) as _:
        stokes_i_err = np.sqrt(stokes_i_err)

    # update the polar properties with stokes parameters
    pprops['STOKESI'] = stokes_i
    pprops['STOKESIERR'] = stokes_i_err
    # set sources
    keys = ['STOKESI', 'STOKESIERR']
    pprops.set_sources(keys, func_name)
    # return properties
    return pprops


def calculate_continuum(params, pprops, **kwargs):
    """
    Function to calculate the continuum polarization

    :param params: ParamDict, parameter dictionary of constants
    :param pprops: parameter dictionary, ParamDict containing data
        Must contain at least:
            POL: numpy array (2D), e2ds degree of polarization data
            POLERR: numpy array (2D), e2ds errors of degree of polarization
            NULL1: numpy array (2D), e2ds 1st null polarization
            NULL2: numpy array (2D), e2ds 2nd null polarization
            STOKESI: numpy array (2D), e2ds Stokes I data
            STOKESIERR: numpy array (2D), e2ds errors of Stokes I
    :params wprops: parameter dictionary, ParamDict containing wave data

    :return pprop: parameter dictionary, the updated parameter dictionary
        Adds/updates the following:
            FLAT_X: numpy array (1D), flatten polarimetric x data
            FLAT_POL: numpy array (1D), flatten polarimetric pol data
            FLAT_POLERR: numpy array (1D), flatten polarimetric pol error data
            FLAT_STOKESI: numpy array (1D), flatten polarimetric stokes I data
            FLAT_STOKESIERR: numpy array (1D), flatten polarimetric stokes I
                             error data
            FLAT_NULL1: numpy array (1D), flatten polarimetric null1 data
            FLAT_NULL2: numpy array (1D), flatten polarimetric null2 data
            CONT_POL: numpy array (1D), e2ds continuum polarization data
                      interpolated from xbin, ybin points, same shape as
                      FLAT_POL
            CONT_XBIN: numpy array (1D), continuum in x polarization samples
            CONT_YBIN: numpy array (1D), continuum in y polarization samples
    """
    # set the function
    func_name = display_func(params, 'calculate_continuum', __NAME__)
    # get constants from params/kwargs
    stokes_binsize = pcheck(params, 'POLAR_SCONT_BINSIZE', 'pol_binsize',
                            kwargs, func_name)
    stokes_overlap = pcheck(params, 'POLAR_SCONT_OVERLAP', 'pol_overlap',
                            kwargs, func_name)
    pol_binsize = pcheck(params, 'POLAR_PCONT_BINSIZE', 'pol_binsize', kwargs,
                         func_name)
    pol_overlap = pcheck(params, 'POLAR_PCONT_OVERLAP', 'pol_overlap', kwargs,
                         func_name)

    pol_excl_bands_l = pcheck(params, 'POLAR_CONT_TELLMASK_LOWER',
                              'pol_excl_bands_l', kwargs, func_name,
                              mapf='list', dtype=float)
    pol_excl_bands_u = pcheck(params, 'POLAR_CONT_TELLMASK_UPPER',
                              'pol_excl_bands_u', kwargs, func_name,
                              mapf='list', dtype=float)
    s_det_mode = pcheck(params, 'POLAR_STOKESI_CONT_MODE', 's_det_mode',
                        kwargs, func_name)
    p_det_mode = pcheck(params, 'POLAR_POLAR_CONT_MODE', 'p_det_mode',
                        kwargs, func_name)
    # continuum for stokes i
    scont_window = pcheck(params, 'POLAR_SCONT_WINDOW', 'scont_window', kwargs,
                          func_name)
    scont_mode = pcheck(params, 'POLAR_SCONT_MODE', 'scont_mode', kwargs,
                        func_name)
    scont_linfit = pcheck(params, 'POLAR_SCONT_LINFIT', 'scont_linfit', kwargs,
                          func_name)
    # iraf constants for stokes i
    siraf_fit_func = pcheck(params, 'POLAR_SIRAF_FIT_FUNC', 'siraf_fit_func',
                            kwargs, func_name)
    siraf_cont_order = pcheck(params, 'POLAR_SIRAF_CONT_ORD', 'siraf_cont_order',
                              kwargs, func_name)
    siraf_nit = pcheck(params, 'POLAR_SIRAF_NIT', 'siraf_nit', kwargs, func_name)
    siraf_rej_low = pcheck(params, 'POLAR_SIRAF_REJ_LOW', 'siraf_rej_low',
                           kwargs, func_name)
    siraf_rej_high = pcheck(params, 'POLAR_SIRAF_REJ_HIGH', 'siraf_rej_high',
                            kwargs, func_name)
    siraf_grow = pcheck(params, 'POLAR_SIRAF_GROW', 'siraf_grow',
                        kwargs, func_name)
    siraf_med_filt = pcheck(params, 'POLAR_SIRAF_MED_FILT', 'siraf_med_filt',
                            kwargs, func_name)
    siraf_plow = pcheck(params, 'POLAR_SIRAF_PER_LOW', 'siraf_plow', kwargs,
                        func_name)
    siraf_phigh = pcheck(params, 'POLAR_SIRAF_PER_HIGH', 'siraf_phigh', kwargs,
                         func_name)
    siraf_min_pts = pcheck(params, 'POLAR_SIRAF_MIN_PTS', 'siraf_min_pts',
                           kwargs, func_name)
    # continuum for polar
    pcont_mode = pcheck(params, 'POLAR_PCONT_MODE', 'pcont_mode', kwargs,
                        func_name)
    pcont_use_polyfit = pcheck(params, 'POLAR_PCONT_USE_POLYFIT',
                               'pcont_use_polyfit', kwargs, func_name)
    pcont_poly_deg = pcheck(params, '', 'pcont_poly_deg', kwargs, func_name)
    # iraf constants for polarization
    piraf_fit_func = pcheck(params, 'POLAR_PIRAF_FIT_FUNC', 'piraf_fit_func',
                            kwargs, func_name)
    piraf_cont_order = pcheck(params, 'POLAR_PIRAF_CONT_ORD', 'piraf_cont_order',
                              kwargs, func_name)
    piraf_nit = pcheck(params, 'POLAR_PIRAF_NIT', 'piraf_nit', kwargs, func_name)
    piraf_rej_low = pcheck(params, 'POLAR_PIRAF_REJ_LOW', 'piraf_rej_low',
                           kwargs, func_name)
    piraf_rej_high = pcheck(params, 'POLAR_PIRAF_REJ_HIGH', 'piraf_rej_high',
                            kwargs, func_name)
    piraf_grow = pcheck(params, 'POLAR_PIRAF_GROW', 'piraf_grow',
                        kwargs, func_name)
    piraf_med_filt = pcheck(params, 'POLAR_PIRAF_MED_FILT', 'piraf_med_filt',
                            kwargs, func_name)
    piraf_plow = pcheck(params, 'POLAR_PIRAF_PER_LOW', 'piraf_plow', kwargs,
                        func_name)
    piraf_phigh = pcheck(params, 'POLAR_PIRAF_PER_HIGH', 'piraf_phigh', kwargs,
                         func_name)
    piraf_min_pts = pcheck(params, 'POLAR_PIRAF_MIN_PTS', 'piraf_min_pts',
                           kwargs, func_name)

    s_normalize = pcheck(params, 'POLAR_NORMALIZE_STOKES_I', 's_normalize',
                         kwargs, func_name)

    # combine pol_excl_bands
    pol_excl_bands = list(zip(pol_excl_bands_l, pol_excl_bands_u))
    # ---------------------------------------------------------------------
    # flatten data (across orders)
    wl = pprops['WAVEMAP'].ravel()
    pol = pprops['POL'].ravel()
    polerr = pprops['POLERR'].ravel()
    stokes_i = pprops['STOKESI'].ravel()
    stokes_i_err = pprops['STOKESIERR'].ravel()
    null1 = pprops['NULL1'].ravel()
    null2 = pprops['NULL2'].ravel()
    # ---------------------------------------------------------------------
    # sort by wavelength (or pixel number)
    sortmask = np.argsort(wl)
    flat_x = wl[sortmask]
    flat_pol = pol[sortmask]
    flat_polerr = polerr[sortmask]
    flat_stokes_i = stokes_i[sortmask]
    flat_stokes_i_err = stokes_i_err[sortmask]
    flat_null1 = null1[sortmask]
    flat_null2 = null2[sortmask]
    # ---------------------------------------------------------------------
    # calculate continuum stokes i
    # ---------------------------------------------------------------------
    if s_det_mode == 'MOVING_MEDIAN':
        contflux, xbin, ybin = continuum(flat_x, flat_stokes_i,
                                         binsize=stokes_binsize,
                                         overlap=stokes_overlap,
                                         window=scont_window, mode=scont_mode,
                                         use_linear_fit=scont_linfit,
                                         excl_bands=pol_excl_bands)
    elif s_det_mode == 'IRAF':
        contflux = fit_continuum(flat_x, flat_stokes_i,
                                 func=siraf_fit_func, order=siraf_cont_order,
                                 nit=siraf_nit, rej_low=siraf_rej_low,
                                 rej_high=siraf_rej_high, grow=siraf_grow,
                                 med_filt=siraf_med_filt,
                                 percentile_low=siraf_plow,
                                 percentile_high=siraf_phigh,
                                 min_points=siraf_min_pts, verbose=False)
        xbin, ybin = None, None
    else:
        emsg = 'Continuum detection (Stokes I) mode = {0} invalid'
        WLOG(params, '', emsg.format(s_det_mode))
        return ParamDict()
    # normalize by continuum if required
    if s_normalize:
        flat_stokes_i = flat_stokes_i / contflux
        flat_stokes_i_err = flat_stokes_i_err / contflux

    # ---------------------------------------------------------------------
    # calculate continuum polarization
    # ---------------------------------------------------------------------
    if p_det_mode == 'MOVING_MEDIAN':
        cpout = continuum_polarization(flat_x, flat_pol, binsize=pol_binsize,
                                       overlap=pol_overlap, mode=pcont_mode,
                                       use_polyfit=pcont_use_polyfit,
                                       deg_polyfit=pcont_poly_deg,
                                       excl_bands=pol_excl_bands)
        contpol, xbinpol, ybinpol = cpout
    elif p_det_mode == 'IRAF':
        contpol = fit_continuum(flat_x, flat_pol,
                                func=piraf_fit_func, order=piraf_cont_order,
                                nit=piraf_nit, rej_low=piraf_rej_low,
                                rej_high=piraf_rej_high, grow=piraf_grow,
                                med_filt=piraf_med_filt,
                                percentile_low=piraf_plow,
                                percentile_high=piraf_phigh,
                                min_points=piraf_min_pts, verbose=False)
        xbinpol, ybinpol = None, None
    else:
        emsg = 'Continuum detection (POL) mode = {0} invalid'
        WLOG(params, '', emsg.format(s_det_mode))
        return ParamDict()
    # ---------------------------------------------------------------------
    # update pprops
    pprops['FLAT_X'] = flat_x
    pprops['FLAT_POL'] = flat_pol
    pprops['FLAT_POLERR'] = flat_polerr
    pprops['FLAT_STOKES_I'] = flat_stokes_i
    pprops['FLAT_STOKES_I_ERR'] = flat_stokes_i_err
    pprops['FLAT_NULL1'] = flat_null1
    pprops['FLAT_NULL2'] = flat_null2
    pprops['CONT_FLUX'] = contflux
    pprops['CONT_POL'] = contpol
    pprops['CONT_FLUX_XBIN'] = xbin
    pprops['CONT_FLUX_YBIN'] = ybin
    pprops['CONT_POL_XBIN'] = xbinpol
    pprops['CONT_POL_YBIN'] = ybinpol
    # set sources
    keys = ['FLAT_X', 'FLAT_POL', 'FLAT_POLERR', 'FLAT_STOKES_I',
            'FLAT_STOKES_I_ERR', 'FLAT_NULL1', 'FLAT_NULL2', 'CONT_POL',
            'CONT_XBIN', 'CONT_YBIN']
    pprops.set_sources(keys, func_name)
    # add constants
    pprops['CONT_BINSIZE'] = pol_binsize
    pprops['CONT_OVERLAP'] = pol_overlap
    # set constants sources
    keys = ['CONT_BINSIZE', 'CONT_OVERLAP']
    pprops.set_sources(keys, func_name)
    # return pprops
    return pprops


def remove_continuum_polarization(params, pprops, **kwargs):
    """
        Function to remove the continuum polarization

        :param params: ParamDict of constants
        :param pprops: parameter dictionary, ParamDict containing data

        Must contain at least:
        - POL: numpy array (2D), e2ds degree of polarization data
        - FLAT_X: numpy array (1D), flatten polarimetric x data
       -  CONT_POL: numpy array (1D), e2ds continuum polarization data

        :return: pprops parameter dictionary, the updated parameter dictionary

        Adds/updates the following:
         - POL: numpy array (2D), e2ds degree of polarization data
         - ORDER_CONT_POL: numpy array (2D), e2ds degree of continuum
                           polarization data
    """
    # set the function
    func_name = display_func(params, 'remove_continuum_polarization', __NAME__)
    # get parameters from param dict
    remove_continuum = pcheck(params, 'POLAR_REMOVE_CONTINUUM',
                              'remove_continuum', kwargs, func_name)
    # get polar array
    pol = pprops['POL']
    # get master wave solution
    wavemap = pprops['WAVEMAP']
    # get the flat_x array
    flat_x = pprops['FLAT_X']
    cont_pol = pprops['CONT_POL']
    # get the shape of the polar array
    ydim, xdim = pol.shape
    # initialize continuum as a NaN filled array
    order_cont_pol = np.zeros(pol.shape) * np.nan
    # ---------------------------------------------------------------------
    # deal with removing continuum
    if remove_continuum:
        # interpolate and remove continuum (across orders)
        for order_num in range(ydim):
            # get wavelengths for current order
            owave = wavemap[order_num]
            # get the minimum and maximum wavelengths
            wl_start, wl_final = np.nanmin(owave), np.nanmax(owave)
            # get the polarimetry for this order
            opolar = pol[order_num]
            # create mask to get only continuum data within wavelength range
            wlmask = (flat_x >= wl_start) * (flat_x <= wl_final)
            # get continnum data within order range
            wl_cont = flat_x[wlmask]
            pol_cont = cont_pol[wlmask]
            # interpolate points applying a cubic spline to the continuum data
            pol_int = interp1d(wl_cont, pol_cont, kind='cubic')
            # create continuum vector at same wavelength sampling as polar data
            continuum_vec = pol_int(owave)
            # save continuum with the same shape as input pol
            order_cont_pol[order_num] = continuum_vec
            # remove continuum from data
            pol[order_num] = opolar - continuum_vec
        # push values back into pprops
        pprops['POL'] = pol
        pprops.append_source('POL', func_name)
    # ---------------------------------------------------------------------
    # add order continuum polarisation to pprops
    pprops['ORDER_CONT_POL'] = order_cont_pol
    # set sources
    pprops.set_source('ORDER_CONT_POL', func_name)
    # return pprops
    return pprops


def normalize_stokes_i(params, pprops, **kwargs):
    """
        Function to normalize Stokes I by the continuum flux

        :param params: ParamDict of constants

        :param pprops: parameter dictionary, ParamDict containing data

        Must contain at least:
        - WAVE: numpy array (2D), e2ds wavelength data
        - STOKESI: numpy array (2D), e2ds degree of polarization data
        - POLERR: numpy array (2D), e2ds errors of degree of polarization
        - FLAT_X: numpy array (1D), flatten polarimetric x data
        - CONT_POL: numpy array (1D), e2ds continuum polarization data

        :return loc: parameter dictionary, the updated parameter dictionary
        Adds/updates the following:
        - STOKESI: numpy array (2D), e2ds Stokes I data
        - STOKESIERR: numpy array (2D), e2ds Stokes I error data
        - ORDER_CONT_FLUX: numpy array (2D), e2ds flux continuum data
    """
    # set the function
    func_name = display_func(params, 'normalize_stokes_i', __NAME__)
    # get parameters from param dict
    normalize = pcheck(params, 'POLAR_NORMALIZE_STOKES_I', 'normalize', kwargs,
                       func_name)
    # get polar array
    stokesi = pprops['STOKESI']
    stokesierr = pprops['STOKESIERR']
    # get master wave solution
    wavemap = pprops['WAVEMAP']
    # get the flat_x array
    flat_x = pprops['FLAT_X']
    cont_pol = pprops['CONT_POL']
    # get the shape of the polar array
    ydim, xdim = stokesi.shape
    # initialize continuum as a NaN filled array
    order_cont_flux = np.zeros(stokesi.shape) * np.nan
    # ---------------------------------------------------------------------
    # deal with removing continuum
    if normalize:
        # ---------------------------------------------------------------------
        # interpolate and remove continuum (across orders)
        # loop around order data
        for order_num in range(ydim):
            # get wavelengths for current order
            owave = wavemap[order_num]
            # get the minimum and maximum wavelengths
            wl_start, wl_final = np.nanmin(owave), np.nanmax(owave)
            # get the polarimetry for this order
            oflux = stokesi[order_num]
            ofluxerr = stokesierr[order_num]
            # create mask to get only continuum data within wavelength range
            wlmask = (flat_x >= wl_start) * (flat_x <= wl_final)
            # get continnum data within order range
            wl_cont = flat_x[wlmask]
            pol_cont = cont_pol[wlmask]
            # interpolate points applying a cubic spline to the continuum data
            pol_int = interp1d(wl_cont, pol_cont, kind='cubic')
            # create continuum vector at same wavelength sampling as polar data
            continuum_vec = pol_int(owave)
            # save continuum with the same shape as input pol
            order_cont_flux[order_num] = continuum_vec
            # remove continuum from data
            stokesi[order_num] = oflux / continuum_vec
            stokesierr[order_num] = ofluxerr / continuum_vec
            # push values back into pprops
            pprops['STOKESI'] = stokesi
            pprops['STOKESIERR'] = stokesierr
            pprops.append_source('POL', func_name)
    # ---------------------------------------------------------------------
    # add order continuum polarisation to pprops
    pprops['ORDER_CONT_FLUX'] = order_cont_flux
    # set sources
    pprops.set_source('ORDER_CONT_FLUX', func_name)
    # return pprops
    return pprops


def clean_polar_data(params, pprops, **kwargs):
    """
    Function to clean polarimetry data.

    :param loc: parameter dictionary, ParamDict to store data
        Must contain at least:
            WAVE: numpy array (2D), wavelength data
            STOKESI: numpy array (2D), Stokes I data
            STOKESIERR: numpy array (2D), errors of Stokes I
            POL: numpy array (2D), degree of polarization data
            POLERR: numpy array (2D), errors of degree of polarization
            NULL2: numpy array (2D), 2nd null polarization

    :keyword sigclip: bool, if True sigma clip
    :keyword nsig: int, set the number of sigmas to clip at (deafult = 3)
    :keyword overwrite: bool, if True overwrite input data with sigma clipped
                        data

    :return loc: parameter dictionaries,
        The updated parameter dictionary adds/updates the following:
            WAVE: numpy array (1D), wavelength data
            STOKESI: numpy array (1D), Stokes I data
            STOKESIERR: numpy array (1D), errors of Stokes I
            POL: numpy array (1D), degree of polarization data
            POLERR: numpy array (1D), errors of polarization
            NULL2: numpy array (1D), 2nd null polarization

    """
    # set the function
    func_name = display_func(params, 'clean_polar_data', __NAME__)
    # get parameters from params
    sigclip = pcheck(params, 'POLAR_CLEAN_SIGCLIP', 'sigclip',
                     kwargs, func_name, default=False)
    nsig = pcheck(params, 'POLAR_NSIGMA_CLIPPING', 'nsig', kwargs, func_name,
                  default=3)
    overwrite = pcheck(params, 'POLAR_SIGCLIP_OVERWRITE', 'overwrite',
                       kwargs, func_name)
    # storage for clean outputs
    clean_wave, clean_stokesi, clean_stokesierr = [], [], []
    clean_pol, clean_polerr, clean_null1, clean_null2 = [], [], [], []
    clean_cont_pol, clean_cont_flux, clean_order = [], [], []
    # get shape of the polar data
    ydim, xdim = pprops['POL'].shape
    # loop over each order
    # loop over each order
    for order_num in range(ydim):
        # mask NaN values
        mask = ~np.isnan(pprops['POL'][order_num])
        mask &= ~np.isnan(pprops['STOKESI'][order_num])
        mask &= ~np.isnan(pprops['NULL1'][order_num])
        mask &= ~np.isnan(pprops['NULL2'][order_num])
        mask &= ~np.isnan(pprops['STOKESIERR'][order_num])
        mask &= ~np.isnan(pprops['POLERR'][order_num])
        mask &= pprops['STOKESI'][order_num] > 0
        mask &= ~np.isinf(pprops['POL'][order_num])
        mask &= ~np.isinf(pprops['STOKESI'][order_num])
        mask &= ~np.isinf(pprops['NULL1'][order_num])
        mask &= ~np.isinf(pprops['NULL2'][order_num])
        mask &= ~np.isinf(pprops['STOKESIERR'][order_num])
        mask &= ~np.isinf(pprops['POLERR'][order_num])
        # sigma clip
        if sigclip:
            opolm = pprops['POL'][order_num][mask]
            median_pol = np.median(opolm)
            medsig_pol = np.median(np.abs(opolm - median_pol)) / 0.67499
            mask &= pprops['POL'][order_num] > median_pol - nsig * medsig_pol
            mask &= pprops['POL'][order_num] < median_pol + nsig * medsig_pol
        # get masked values
        wl = pprops['WAVEMAP'][order_num][mask]
        pol = pprops['POL'][order_num][mask]
        polerr = pprops['POLERR'][order_num][mask]
        flux = pprops['STOKESI'][order_num][mask]
        fluxerr = pprops['STOKESIERR'][order_num][mask]
        null1 = pprops['NULL1'][order_num][mask]
        null2 = pprops['NULL2'][order_num][mask]
        cont_pol = pprops['ORDER_CONT_POL'][order_num][mask]
        cont_flux = pprops['ORDER_CONT_FLUX'][order_num][mask]
        # test if order is not empty
        if np.sum(mask) > 0:
            clean_wave.append(wl)
            clean_stokesi.append(flux)
            clean_stokesierr.append(fluxerr)
            clean_pol.append(pol)
            clean_polerr.append(polerr)
            clean_null1.append(null1)
            clean_null2.append(null2)
            clean_cont_pol.append(cont_pol)
            clean_cont_flux.append(cont_flux)
            clean_order.append([order_num] * np.sum(mask))
        # deal with overwriting arrays
        if overwrite:
            pprops['WAVEMAP'][order_num][~mask] = np.nan
            pprops['POL'][order_num][~mask] = np.nan
            pprops['POLERR'][order_num][~mask] = np.nan
            pprops['STOKESI'][order_num][~mask] = np.nan
            pprops['STOKESIERR'][order_num][~mask] = np.nan
            pprops['NULL1'][order_num][~mask] = np.nan
            pprops['NULL2'][order_num][~mask] = np.nan
            pprops['ORDER_CONT_POL'][order_num][~mask] = np.nan
            pprops['ORDER_CONT_FLUX'][order_num][~mask] = np.nan
            # set sources
            keys = ['WAVEMAP', 'POL', 'POLERR', 'STOKESI', 'STOKESIERR',
                    'NULL1', 'NULL2', 'ORDER_CONT_POL', 'ORDER_CONT_FLUX']
            pprops.append_sources(keys, func_name)
        # sort by wavelength (or pixel number)
        sortmask = np.argsort(clean_wave)
        # save back to properties
        pprops['FLAT_X'] = np.array(clean_wave)[sortmask]
        pprops['FLAT_POL'] = np.array(clean_pol)[sortmask]
        pprops['FLAT_POLERR'] = np.array(clean_polerr)[sortmask]
        pprops['FLAT_STOKESI'] = np.array(clean_stokesi)[sortmask]
        pprops['FLAT_STOKESIERR'] = np.array(clean_stokesierr)[sortmask]
        pprops['FLAT_NULL1'] = np.array(clean_null1)[sortmask]
        pprops['FLAT_NULL2'] = np.array(clean_null2)[sortmask]
        pprops['CONT_POL'] = np.array(clean_cont_pol)[sortmask]
        pprops['CONT_FLUX'] = np.array(clean_cont_flux)[sortmask]
        pprops['FLAT_ORDER'] = np.array(clean_order)[sortmask]
        # set sources
        keys = ['FLAT_X', 'FLAT_POL', 'FLAT_POLERR', 'FLAT_STOKESI',
                'FLAT_STOKESIERR', 'FLAT_NULL1', 'FLAT_NULL2', 'CONT_POL',
                'CONT_FLUX']
        pprops.append_sources(keys, func_name)
        pprops.set_source('FLAT_ORDER', func_name)
        # return pprops
        return pprops


# =============================================================================
# Define internal functions
# =============================================================================
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
    cmmtseq = infile.get_hkey('KW_CMMTSEQ')
    # get fiber type
    fiber = infile.get_hkey('KW_FIBER')
    # ----------------------------------------------------------------------
    # deal with bad file
    if cmmtseq in [None, '', 'None']:
        eargs = [params['KW_CMMTSEQ'][0], infile.filename]
        WLOG(params, 'warning', textentry('10-021-00004', args=eargs))
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
        WLOG(params, 'warning', textentry('10-021-00001', args=eargs))
        valid = False
    # ----------------------------------------------------------------------
    # get the sequence number
    sequence = split[4]
    try:
        sequence = int(sequence)
    except ValueError:
        eargs = [params['KW_CMMTSEQ'][0], cmmtseq]
        WLOG(params, 'warning', textentry('10-021-00002', args=eargs))
        valid = False
    # ----------------------------------------------------------------------
    # get the total number of sequences
    total = split[6]
    try:
        total = int(total)
    except ValueError:
        eargs = [params['KW_CMMTSEQ'][0], cmmtseq]
        WLOG(params, 'warning', textentry('10-021-00003', args=eargs))
        valid = False
    # ----------------------------------------------------------------------
    # deal with fiber type
    if fiber not in valid_fibers:
        eargs = [fiber, ', '.join(valid_fibers), infile.filename]
        WLOG(params, 'warning', textentry('10-021-00005', args=eargs))
        valid = False
    # ----------------------------------------------------------------------
    # deal with stokes parameters - check parameter is valid
    if stoke_parameter not in valid_stokes:
        eargs = [stoke_parameter, ', '.join(valid_stokes), infile.filename]
        WLOG(params, 'warning', textentry('10-021-00006', args=eargs))
        valid = False
    # ----------------------------------------------------------------------
    # return extracted parameters
    if not valid:
        return None, None, None, None, fiber, False
    else:
        return stoke_parameter, exposure, sequence, total, fiber, valid


def polar_time(params, pobjs):
    # set function name
    func_name = display_func(params, 'polar_time', __NAME__)
    # polar sequence start time
    starttime = np.inf
    obj_s = None
    # polar sequence end time
    endtime = -np.inf
    obj_l = None

    # storage of times and fluxes
    mean_fluxes = []
    midmjds = []
    midbjds = []
    bervmaxs = []

    # loop over files in polar sequence
    for name in pobjs:
        # get the polar object instance
        pobj = pobjs[name]
        # get expnum
        expnum = pobj.exposure
        # find the first file time/name
        if pobj.mjdstart < starttime:
            starttime = pobj.mjdstart
            obj_s = pobj
        # find the last file time/name
        if pobj.mjdend > endtime:
            endtime = pobj.mjdend
            obj_l = pobj
        # get mean flux
        aflux = pobjs['A_{0}'.format(expnum)].rawflux
        bflux = pobjs['B_{0}'.format(expnum)].rawflux
        # calcaulte mean A+B flux
        meanflux = np.nanmean(aflux + bflux)
        # append to mean_fluxes
        mean_fluxes.append(meanflux)
        # get mid mjd time
        midmjds.append(pobj.mjd)
        midbjds.append(pobj.bjd)
        bervmaxs.append(pobj.bervmax)

    # convert to numpy arrays
    mean_fluxes = np.array(mean_fluxes)
    midmjds = np.array(midmjds)
    midbjds = np.array(midbjds)
    bervmaxs = np.array(bervmaxs)

    # calculate total elapsed time
    elapsed_time = obj_l.mjdend - obj_s.mjdstart

    # calculate flux-weighted mjd of polarimetric sequence
    mjdfwcen = np.sum(mean_fluxes * midmjds) / np.sum(mean_fluxes)

    # calculate flux-weight bjd of polarimetric sequence
    bjdfwcen = np.sum(mean_fluxes * midbjds) / np.sum(mean_fluxes)

    # calculate MJD at center of polarimetric sequence
    mjdcen = np.mean([obj_l.mjdstart, obj_s.mjdend])

    # calculate BJD at center of polarimetric sequence
    bjdcen = np.mean([obj_l.bjdstart, obj_s.bjdend])

    # calculate BERV at center by linear interpolation
    berv_slope = (obj_l.berv - obj_s.berv) / (obj_l.bjd - obj_s.bjd)
    berv_intercept = obj_s.berv - (berv_slope * obj_s.bjd)
    bervcen = berv_intercept + (berv_slope * bjdcen)

    # calculate the berv max
    bervmax = np.max(bervmaxs)
    # add mean bjd
    meanbjd = np.mean(midbjds)

    # add all to ptimes
    ptimes = ParamDict()
    ptimes['ELAPSED_TIME'] = elapsed_time
    ptimes['MJDFWCEN'] = mjdfwcen
    ptimes['BJDFWCEN'] = bjdfwcen
    ptimes['MJDCEN'] = mjdcen
    ptimes['BERVCEN'] = bervcen
    ptimes['BERVMAX'] = bervmax
    ptimes['MEANBJD'] = meanbjd
    # add sources
    keys = ['ELAPSED_TIME', 'MJDFWCEN', 'BJDFWCEN', 'MJDCEN', 'BERVCEN',
            'BERVMAX', 'MEANBJD']
    ptimes.set_sources(keys, func_name)
    # return ptimes
    return ptimes


def polar_diff_method(params, pobjs, props, **kwargs):
    """
    Function to calculate polarimetry using the difference method as described
    in the paper:
        Bagnulo et al., PASP, Volume 121, Issue 883, pp. 993 (2009)

    :param params: ParamDict, parameter dictionary of constants
    :param pobjs: dict, dictionary of polar object instance
    :param props: parameter dictionary, parameter dictionary from polar
                  validation

    :type params: ParamDict
    :type pobjs: dict
    :type props: ParamDict

    :return: ParamDict of polar outputs (pol, pol_err, null1, null2, method)
    """
    # set function name
    func_name = display_func(params, 'polar_diff_method', __NAME__)
    # log start of polarimetry calculations
    WLOG(params, '', textentry('40-021-00002', args=['difference']))
    # get parameters from params
    interpolate_flux = pcheck(params, 'POLAR_INTERPOLATE_FLUX',
                              'interpolate_flux', kwargs, func_name)
    # get parameters from props
    nexp = int(props['NEXPOSURES'])
    # get the first file for reference
    pobj = pobjs['A_1']
    # ---------------------------------------------------------------------
    # set up storage
    # ---------------------------------------------------------------------
    pol = np.zeros(pobj.infile.shape)
    pol_err = np.zeros(pobj.infile.shape)
    null1 = np.zeros(pobj.infile.shape)
    null2 = np.zeros(pobj.infile.shape)
    # ---------------------------------------------------------------------
    # loop around exposures and combine A and B
    gg, gvar = [], []
    for it in range(1, int(nexp) + 1):
        # get a and b data for this exposure
        if interpolate_flux:
            data_a = pobjs['A_{0}'.format(it)].flux
            data_b = pobjs['B_{0}'.format(it)].flux
            edata_a = pobjs['A_{0}'.format(it)].eflux
            edata_b = pobjs['B_{0}'.format(it)].eflux
        else:
            data_a = pobjs['A_{0}'.format(it)].rawflux
            data_b = pobjs['B_{0}'.format(it)].rawflux
            edata_a = pobjs['A_{0}'.format(it)].raweflux
            edata_b = pobjs['B_{0}'.format(it)].raweflux
        # ---------------------------------------------------------------------
        # STEP 1 - calculate the quantity Gn (Eq #12-14 on page 997 of
        #          Bagnulo et al. 2009), n being the pair of exposures
        # ---------------------------------------------------------------------
        part1 = data_a - data_b
        part2 = data_a + data_b
        gg.append(part1 / part2)
        # Calculate the variances for fiber A and B, assuming Poisson noise
        # only. In fact the errors should be obtained from extraction, i.e.
        # from the error extension of e2ds files.
        a_var = edata_a ** 2
        b_var = edata_b ** 2
        # ---------------------------------------------------------------------
        # STEP 2 - calculate the quantity g_n^2 (Eq #A4 on page 1013 of
        #          Bagnulo et al. 2009), n being the pair of exposures
        # ---------------------------------------------------------------------
        nomin = 2.0 * data_a * data_b
        denom = (data_a + data_b) ** 2.0
        factor1 = (nomin / denom) ** 2.0
        a_var_part = a_var / (data_a ** 2.0)
        b_var_part = b_var / (data_b ** 2.0)
        gvar.append(factor1 * (a_var_part + b_var_part))
    # ---------------------------------------------------------------------
    # if we have 4 exposures
    if nexp == 4:
        # -----------------------------------------------------------------
        # STEP 3 - calculate the quantity Dm (Eq #18 on page 997 of
        #          Bagnulo et al. 2009 paper) and the quantity Dms with
        #          exposures 2 and 4 swapped, m being the pair of exposures
        #          Ps. Notice that SPIRou design is such that the angles of
        #          the exposures that correspond to different angles of the
        #          retarder are obtained in the order (1)->(2)->(4)->(3),
        #          which explains the swap between G[3] and G[2].
        # -----------------------------------------------------------------
        d1, d2 = gg[0] - gg[1], gg[3] - gg[2]
        d1s, d2s = gg[0] - gg[2], gg[3] - gg[1]
        # -----------------------------------------------------------------
        # STEP 4 - calculate the degree of polarization for Stokes
        #          parameter (Eq #19 on page 997 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        pol = (d1 + d2) / nexp
        # -----------------------------------------------------------------
        # STEP 5 - calculate the first NULL spectrum
        #          (Eq #20 on page 997 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        null1 = (d1 - d2) / nexp
        # -----------------------------------------------------------------
        # STEP 6 - calculate the second NULL spectrum
        #          (Eq #20 on page 997 of Bagnulo et al. 2009)
        #          with exposure 2 and 4 swapped
        # -----------------------------------------------------------------
        null2 = (d1s - d2s) / nexp
        # -----------------------------------------------------------------
        # STEP 7 - calculate the polarimetry error
        #          (Eq #A3 on page 1013 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        sum_of_gvar = gvar[0] + gvar[1] + gvar[2] + gvar[3]
        pol_err = np.sqrt(sum_of_gvar / (nexp ** 2.0))
    # ---------------------------------------------------------------------
    # else if we have 2 exposures
    elif nexp == 2:
        # -----------------------------------------------------------------
        # STEP 3 - calculate the quantity Dm
        #          (Eq #18 on page 997 of Bagnulo et al. 2009) and
        #          the quantity Dms with exposure 2 and 4 swapped,
        #          m being the pair of exposures
        # -----------------------------------------------------------------
        d1 = gg[0] - gg[1]
        # -----------------------------------------------------------------
        # STEP 4 - calculate the degree of polarization
        #          (Eq #19 on page 997 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        pol = d1 / nexp
        # -----------------------------------------------------------------
        # STEP 5 - calculate the polarimetry error
        #          (Eq #A3 on page 1013 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        sum_of_gvar = gvar[0] + gvar[1]
        pol_err = np.sqrt(sum_of_gvar / (nexp ** 2.0))
    # ---------------------------------------------------------------------
    # else we have insufficient data (should not get here)
    else:
        # Log that the number of exposures is not sufficient
        eargs = [nexp, func_name]
        WLOG(params, 'error', textentry('09-021-00008', args=eargs))
    # ---------------------------------------------------------------------
    # populate the polar properties
    pprops = props.copy()
    pprops['POL'] = pol
    pprops['NULL1'] = null1
    pprops['NULL2'] = null2
    pprops['POLERR'] = pol_err
    pprops['WAVEMAP'] = pobj.mwaveprops['WAVEMAP']
    pprops['METHOD'] = 'Difference'
    # set sources
    keys = ['POL', 'NULL1', 'NULL2', 'POLERR', 'WAVEMAP', 'METHOD']
    pprops.set_sources(keys, func_name)
    # return the properties
    return pprops


def polar_ratio_method(params, pobjs, props, **kwargs):
    """
    Function to calculate polarimetry using the ratio method as described
    in the paper:
        Bagnulo et al., PASP, Volume 121, Issue 883, pp. 993 (2009)


    :param params: ParamDict, parameter dictionary of constants
    :param pobjs: dict, dictionary of polar object instance
    :param props: parameter dictionary, parameter dictionary from polar
                  validation

    :type params: ParamDict
    :type pobjs: dict
    :type props: ParamDict

    :return: ParamDict of polar outputs (pol, pol_err, null1, null2, method)
    """
    # set function name
    func_name = display_func(params, 'polar_ratio_method', __NAME__)
    # log start of polarimetry calculations
    WLOG(params, '', textentry('40-021-00002', args=['difference']))
    # get parameters from params
    interpolate_flux = pcheck(params, 'POLAR_INTERPOLATE_FLUX',
                              'interpolate_flux', kwargs, func_name)
    # get parameters from props
    nexp = int(props['NEXPOSURES'])
    # get the first file for reference
    pobj = pobjs['A_1']
    # ---------------------------------------------------------------------
    # set up storage
    # ---------------------------------------------------------------------
    pol = np.zeros(pobj.infile.shape)
    pol_err = np.zeros(pobj.infile.shape)
    null1 = np.zeros(pobj.infile.shape)
    null2 = np.zeros(pobj.infile.shape)
    # storage
    flux_ratio, var_term = [], []
    # loop around exposures
    for it in range(1, int(nexp) + 1):
        # get a and b data for this exposure
        if interpolate_flux:
            data_a = pobjs['A_{0}'.format(it)].flux
            data_b = pobjs['B_{0}'.format(it)].flux
            edata_a = pobjs['A_{0}'.format(it)].eflux
            edata_b = pobjs['B_{0}'.format(it)].eflux
        else:
            data_a = pobjs['A_{0}'.format(it)].rawflux
            data_b = pobjs['B_{0}'.format(it)].rawflux
            edata_a = pobjs['A_{0}'.format(it)].raweflux
            edata_b = pobjs['B_{0}'.format(it)].raweflux
        # ---------------------------------------------------------------------
        # STEP 1 - calculate ratio of beams for each exposure
        #          (Eq #12 on page 997 of Bagnulo et al. 2009 )
        # ---------------------------------------------------------------------
        with warnings.catch_warnings(record=True) as _:
            flux_ratio.append(data_a / data_b)
        # Calculate the variances for fiber A and B, assuming Poisson noise
        # only. In fact the errors should be obtained from extraction, i.e.
        # from the error extension of e2ds files.
        a_var = edata_a ** 2
        b_var = edata_b ** 2
        # ---------------------------------------------------------------------
        # STEP 2 - calculate the error quantities for Eq #A10 on page 1014 of
        #          Bagnulo et al. 2009
        # ---------------------------------------------------------------------
        with warnings.catch_warnings(record=True) as _:
            var_term_part1 = a_var / (data_a ** 2.0)
            var_term_part2 = b_var / (data_b ** 2.0)
        var_term.append(var_term_part1 + var_term_part2)
    # ---------------------------------------------------------------------
    # if we have 4 exposures
    if nexp == 4:
        # -----------------------------------------------------------------
        # STEP 3 - calculate the quantity Rm
        #          (Eq #23 on page 998 of Bagnulo et al. 2009) and
        #          the quantity Rms with exposure 2 and 4 swapped,
        #          m being the pair of exposures
        #          Ps. Notice that SPIRou design is such that the angles of
        #          the exposures that correspond to different angles of the
        #          retarder are obtained in the order (1)->(2)->(4)->(3),which
        #          explains the swap between flux_ratio[3] and flux_ratio[2].
        # -----------------------------------------------------------------
        with warnings.catch_warnings(record=True) as _:
            r1 = flux_ratio[0] / flux_ratio[1]
            r2 = flux_ratio[3] / flux_ratio[2]
            r1s = flux_ratio[0] / flux_ratio[2]
            r2s = flux_ratio[3] / flux_ratio[1]
        # -----------------------------------------------------------------
        # STEP 4 - calculate the quantity R
        #          (Part of Eq #24 on page 998 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        with warnings.catch_warnings(record=True) as _:
            rr = (r1 * r2) ** (1.0 / nexp)
        # -----------------------------------------------------------------
        # STEP 5 - calculate the degree of polarization
        #          (Eq #24 on page 998 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        with warnings.catch_warnings(record=True) as _:
            pol = (rr - 1.0) / (rr + 1.0)
        # -----------------------------------------------------------------
        # STEP 6 - calculate the quantity RN1
        #          (Part of Eq #25-26 on page 998 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        with warnings.catch_warnings(record=True) as _:
            rn1 = (r1 / r2) ** (1.0 / nexp)
        # -----------------------------------------------------------------
        # STEP 7 - calculate the first NULL spectrum
        #          (Eq #25-26 on page 998 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        with warnings.catch_warnings(record=True) as _:
            null1 = (rn1 - 1.0) / (rn1 + 1.0)
        # -----------------------------------------------------------------
        # STEP 8 - calculate the quantity RN2
        #          (Part of Eq #25-26 on page 998 of Bagnulo et al. 2009),
        #          with exposure 2 and 4 swapped
        # -----------------------------------------------------------------
        with warnings.catch_warnings(record=True) as _:
            rn2 = (r1s / r2s) ** (1.0 / nexp)
        # -----------------------------------------------------------------
        # STEP 9 - calculate the second NULL spectrum
        #          (Eq #25-26 on page 998 of Bagnulo et al. 2009),
        #          with exposure 2 and 4 swapped
        # -----------------------------------------------------------------
        with warnings.catch_warnings(record=True) as _:
            null2 = (rn2 - 1.0) / (rn2 + 1.0)
        # -----------------------------------------------------------------
        # STEP 10 - calculate the polarimetry error (Eq #A10 on page 1014
        #           of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        with warnings.catch_warnings(record=True) as _:
            numer_part1 = (r1 * r2) ** (1.0 / 2.0)
            denom_part1 = ((r1 * r2) ** (1.0 / 4.0) + 1.0) ** 4.0
            part1 = numer_part1 / (denom_part1 * 4.0)
        sumvar = var_term[0] + var_term[1] + var_term[2] + var_term[3]
        with warnings.catch_warnings(record=True) as _:
            pol_err = np.sqrt(part1 * sumvar)
    # ---------------------------------------------------------------------
    # else if we have 2 exposures
    elif nexp == 2:
        # -----------------------------------------------------------------
        # STEP 3 - calculate the quantity Rm
        #          (Eq #23 on page 998 of Bagnulo et al. 2009) and
        #          the quantity Rms with exposure 2 and 4 swapped,
        #          m being the pair of exposures
        # -----------------------------------------------------------------
        with warnings.catch_warnings(record=True) as _:
            r1 = flux_ratio[0] / flux_ratio[1]
        # -----------------------------------------------------------------
        # STEP 4 - calculate the quantity R
        #          (Part of Eq #24 on page 998 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        with warnings.catch_warnings(record=True) as _:
            rr = r1 ** (1.0 / nexp)
        # -----------------------------------------------------------------
        # STEP 5 - calculate the degree of polarization
        #          (Eq #24 on page 998 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        with warnings.catch_warnings(record=True) as _:
            pol = (rr - 1.0) / (rr + 1.0)
        # -----------------------------------------------------------------
        # STEP 6 - calculate the polarimetry error (Eq #A10 on page 1014
        #           of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        # numer_part1 = R1
        with warnings.catch_warnings(record=True) as _:
            denom_part1 = ((r1 ** 0.5) + 1.0) ** 4.0
            part1 = r1 / denom_part1
        sumvar = var_term[0] + var_term[1]
        pol_err = np.sqrt(part1 * sumvar)
    # ---------------------------------------------------------------------
    # else we have insufficient data (should not get here)
    else:
        # Log that the number of exposures is not sufficient
        eargs = [nexp, func_name]
        WLOG(params, 'error', textentry('09-021-00008', args=eargs))
    # ---------------------------------------------------------------------
    # populate the polar properties
    pprops = props.copy()
    pprops['POL'] = pol
    pprops['NULL1'] = null1
    pprops['NULL2'] = null2
    pprops['POLERR'] = pol_err
    pprops['WAVEMAP'] = pobj.mwaveprops['WAVEMAP']
    pprops['METHOD'] = 'Ratio'
    # set sources
    keys = ['POL', 'NULL1', 'NULL2', 'POLERR', 'METHOD']
    pprops.set_sources(keys, func_name)
    # return the properties
    return pprops


def continuum(x, y, binsize=200, overlap=100, sigmaclip=3.0, window=3,
              mode='median', use_linear_fit=False, excl_bands=None,
              outx=None):
    """
    Function to detect and calculate continuum spectrum
    :param x: numpy array (1D), input x data
    :param y: numpy array (1D), input y data (x and y must be of the same size)
    :param binsize: int, number of points in each bin
    :param overlap: int, number of points to overlap with adjacent bins
    :param sigmaclip: int, number of times sigma to cut-off points
    :param window: int, number of bins to use in local fit
    :param mode: string, set combine mode, where mode accepts "median", "mean",
                 "max"
    :param use_linear_fit: bool, whether to use the linar fit
    :param excl_bands: list of pairs of float, list of wavelength ranges
                        ([wl0,wlf]) to exclude data for continuum detection

    :return continuum, xbin, ybin
        continuum: numpy array (1D) of the same size as input arrays containing
                   the continuum data already interpolated to the same points
                   as input data.
        xbin,ybin: numpy arrays (1D) containing the bins used to interpolate
                   data for obtaining the continuum
    """
    # set function name
    func_name = display_func(None, 'continuum', __NAME__)
    # deal with no outx
    if outx is None:
        outx = x
    # deal with no excl_bands
    if excl_bands is None:
        excl_bands = []
    # ----------------------------------------------------------------------
    # set number of bins given the input array length and the bin size
    nbins = int(np.floor(len(x) / binsize))
    # ----------------------------------------------------------------------
    # initialize arrays to store binned data
    xbin, ybin = [], []
    # ----------------------------------------------------------------------
    # loop around bins
    for i in range(nbins):
        # get first and last index within the bin
        idx0 = i * binsize - overlap
        idxf = (i + 1) * binsize + overlap
        # if it reaches the edges then it reset the indexes
        if idx0 < 0:
            idx0 = 0
        if idxf >= len(x):
            idxf = len(x) - 1
        # ------------------------------------------------------------------
        # get data within the bin
        xbin_tmp = np.array(x[idx0:idxf])
        ybin_tmp = np.array(y[idx0:idxf])
        # create mask of exclusion bands
        excl_mask = np.full(np.shape(xbin_tmp), False, dtype=bool)
        for band in excl_bands:
            excl_mask += (xbin_tmp > band[0]) & (xbin_tmp < band[1])
        # -----------------------------------------------------------------
        # mask data within exclusion bands
        xtmp = xbin_tmp[~excl_mask]
        ytmp = ybin_tmp[~excl_mask]
        # create mask to get rid of NaNs
        nanmask = ~np.isnan(ytmp)
        # deal with first bin (if not using linear fit)
        if i == 0 and not use_linear_fit:
            xbin.append(x[0] - np.abs(x[1] - x[0]))
            # create mask to get rid of NaNs
            localnanmask = ~np.isnan(y)
            ybin.append(np.median(y[localnanmask][:binsize]))

        if len(xtmp[nanmask]) > 2:
            # calculate mean x within the bin
            xmean = np.nanmean(xtmp[nanmask])
            # calculate median y within the bin
            medy = np.nanmedian(ytmp[nanmask])

            # calculate median deviation
            medydev = np.nanmedian(np.abs(ytmp[nanmask] - medy))
            # create mask to filter data outside n*sigma range
            filtermask = (ytmp[nanmask] > medy)
            filtermask &= (ytmp[nanmask] < medy + sigmaclip * medydev)
            # --------------------------------------------------------------
            if len(ytmp[nanmask][filtermask]) > 2:
                # save mean x wihthin bin
                xbin.append(xmean)
                if mode == 'max':
                    # save maximum y of filtered data
                    ybin.append(np.max(ytmp[nanmask][filtermask]))
                elif mode == 'median':
                    # save median y of filtered data
                    ybin.append(np.median(ytmp[nanmask][filtermask]))
                elif mode == 'mean':
                    # save mean y of filtered data
                    ybin.append(np.mean(ytmp[nanmask][filtermask]))
                else:
                    raise DrsCodedException('00-009-10001', 'error',
                                            targs=[mode], func_name=func_name)

    # ----------------------------------------------------------------------
    # Option to use a linearfit within a given window
    if use_linear_fit:
        # initialize arrays to store new bin data
        newxbin, newybin = [], []
        # -----------------------------------------------------------------
        # loop around bins to obtain a linear fit within a given window size
        for i in range(len(xbin)):
            # set first and last index to select bins within window
            idx0 = i - window
            idxf = i + 1 + window
            # make sure it doesnt go over the edges
            if idx0 < 0:
                idx0 = 0
            if idxf > nbins:
                idxf = nbins - 1
            # --------------------------------------------------------------
            # perform linear fit to these data
            sout = stats.linregress(xbin[idx0:idxf], ybin[idx0:idxf])
            slope, intercept, r_value, p_value, std_err = sout
            # --------------------------------------------------------------
            # save data obtained from the fit
            newxbin.append(xbin[i])
            newybin.append(intercept + slope * xbin[i])
        # ------------------------------------------------------------------
        xbin, ybin = newxbin, newybin
    # ----------------------------------------------------------------------
    # interpolate points applying an Spline to the bin data
    sfit = UnivariateSpline(xbin, ybin)
    # sfit.set_smoothing_factor(0.5)
    # Resample interpolation to the original grid
    continuum_val = sfit(outx)
    # return continuum and x and y bins
    return continuum_val, xbin, ybin


def fit_continuum(wav, spec, func='polynomial', order=3, nit=5,
                  rej_low=2.0, rej_high=2.5, grow=1, med_filt=0,
                  percentile_low=0.0, percentile_high=100.0,
                  min_points=10, verbose=False):
    """
    Continuum fitting re-implemented from IRAF's 'continuum' function
    in non-interactive mode only but with additional options.
    :Parameters:

    wav: array(float)
        abscissa values (wavelengths, velocities, ...)
    spec: array(float)
        spectrum values
    function: str
        function to fit to the continuum among 'polynomial', 'spline3'
    order: int
        fit function order:
        'polynomial': degree (not number of parameters as in IRAF)
        'spline3': number of knots
    nit: int
        number of iteractions of non-continuum points
        see also 'min_points' parameter
    rej_low: float
        rejection threshold in unit of residul standard deviation for point
        below the continuum
    rej_high: float
        same as rej_low for point above the continuum
    grow: int
        number of neighboring points to reject
    med_filt: int
        median filter the spectrum on 'med_filt' pixels prior to fit
        improvement over IRAF function
        'med_filt' must be an odd integer
    percentile_low: float
        reject point below below 'percentile_low' percentile prior to fit
        improvement over IRAF function
        "percentile_low' must be a float between 0. and 100.
    percentile_high: float
        same as percentile_low but reject points in percentile above
        'percentile_high'

    min_points: int
        stop rejection iterations when the number of points to fit is less than
        'min_points'
    plot_fit: bool
        if true display two plots:
            1. spectrum, fit function, rejected points
            2. residual, rejected points
    verbose: bool
        if true fit information is printed on STDOUT:
            * number of fit points
            * RMS residual
    """
    # set function name
    func_name = display_func(None, 'fit_continuum', __NAME__)

    mspec = np.ma.masked_array(spec, mask=np.zeros_like(spec))
    # mask 1st and last point: avoid error when no point is masked
    # [not in IRAF]
    mspec.mask[0] = True
    mspec.mask[-1] = True

    mspec = np.ma.masked_where(np.isnan(spec), mspec)
    # apply median filtering prior to fit
    # [opt] [not in IRAF]
    if int(med_filt):
        fspec = signal.medfilt(spec, kernel_size=med_filt)
    else:
        fspec = spec
    # consider only a fraction of the points within percentile range
    # [opt] [not in IRAF]
    mspec = np.ma.masked_where(fspec < np.percentile(fspec, percentile_low),
                               mspec)
    mspec = np.ma.masked_where(fspec > np.percentile(fspec, percentile_high),
                               mspec)
    # perform 1st fit
    if func == 'polynomial':
        coeff = np.polyfit(wav[~mspec.mask], spec[~mspec.mask], order)
        cont = np.poly1d(coeff)(wav)
    elif func == 'spline3':
        mterm = ((wav[-1] - wav[0]) / (order + 1))
        knots = wav[0] + np.arange(order + 1)[1:] * mterm
        spl = splrep(wav[~mspec.mask], spec[~mspec.mask], k=3, t=knots)
        cont = splev(wav, spl)
    else:
        eargs = [func, func_name]
        raise DrsCodedException('00-021-00002', 'error', targs=eargs,
                                func_name=func_name)
    # iteration loop: reject outliers and fit again
    if nit > 0:
        for it in range(nit):
            res = fspec - cont
            sigm = np.std(res[~mspec.mask])
            # mask outliers
            mspec1 = np.ma.masked_where(res < -rej_low * sigm, mspec)
            mspec1 = np.ma.masked_where(res > rej_high * sigm, mspec1)
            # exlude neighbors cf IRAF's continuum parameter 'grow'
            if grow > 0:
                for sl in np.ma.clump_masked(mspec1):
                    for ii in range(sl.start - grow, sl.start):
                        if ii >= 0:
                            mspec1.mask[ii] = True
                    for ii in range(sl.stop + 1, sl.stop + grow + 1):
                        if ii < len(mspec1):
                            mspec1.mask[ii] = True
            # stop rejection process when min_points is reached
            # [opt] [not in IRAF]
            if np.ma.count(mspec1) < min_points:
                if verbose:
                    print("  min_points %d reached" % min_points)
                break
            mspec = mspec1
            if func == 'polynomial':
                coeff = np.polyfit(wav[~mspec.mask], spec[~mspec.mask], order)
                cont = np.poly1d(coeff)(wav)
            elif func == 'spline3':
                mterm = ((wav[-1] - wav[0]) / (order + 1))
                knots = wav[0] + np.arange(order + 1)[1:] * mterm
                spl = splrep(wav[~mspec.mask], spec[~mspec.mask], k=3, t=knots)
                cont = splev(wav, spl)
            else:
                eargs = [func, func_name]
                raise DrsCodedException('00-021-00002', 'error', targs=eargs,
                                        func_name=func_name)
    # compute residual and rms
    res = fspec - cont
    sigm = np.std(res[~mspec.mask])
    # print nfit and fit rms
    if verbose:
        print("  nfit=%d/%d" % (np.ma.count(mspec), len(mspec)))
        print("  fit rms=%.3e" % sigm)
    # compute residual and rms between original spectrum and model
    # different from above when median filtering is applied
    ores = spec - cont
    osigm = np.std(ores[~mspec.mask])
    # print message
    if int(med_filt) and verbose:
        print("  unfiltered rms=%.3e" % osigm)
    # return continuum
    return cont


def continuum_polarization(x, y, binsize=200, overlap=100,
                           mode="median", use_polyfit=True,
                           deg_polyfit=3, excl_bands=None):
    """
    Function to calculate continuum polarization
    :param x,y: numpy array (1D), input data (x and y must be of the same size)
    :param binsize: int, number of points in each bin
    :param overlap: int, number of points to overlap with adjacent bins
    :param sigmaclip: int, number of times sigma to cut-off points
    :param mode: string, set combine mode, where mode accepts "median", "mean",
                 "max"
    :param use_linear_fit: bool, whether to use the linar fit
    :param excl_bands: list of pairs of float, list of wavelength ranges
                        ([wl0,wlf]) to exclude data for continuum detection

    :return continuum, xbin, ybin
        continuum: numpy array (1D) of the same size as input arrays containing
                   the continuum data already interpolated to the same points
                   as input data.
        xbin,ybin: numpy arrays (1D) containing the bins used to interpolate
                   data for obtaining the continuum
    """
    # set function name
    func_name = display_func(None, 'continuum_polarization', __NAME__)
    # set number of bins given the input array length and the bin size
    nbins = int(np.floor(len(x) / binsize)) + 1

    # initialize arrays to store binned data
    xbin, ybin = [], []

    for i in range(nbins):
        # get first and last index within the bin
        idx0 = i * binsize - overlap
        idxf = (i + 1) * binsize + overlap
        # if it reaches the edges then reset indexes
        if idx0 < 0:
            idx0 = 0
        if idxf >= len(x):
            idxf = len(x) - 1
        # get data within the bin
        xbin_tmp = np.array(x[idx0:idxf])
        ybin_tmp = np.array(y[idx0:idxf])

        # create mask of exclusion bands
        excl_mask = np.full(np.shape(xbin_tmp), False, dtype=bool)
        for band in excl_bands:
            excl_mask += (xbin_tmp > band[0]) & (xbin_tmp < band[1])

        # mask data within telluric bands
        xtmp = xbin_tmp[~excl_mask]
        ytmp = ybin_tmp[~excl_mask]

        # create mask to get rid of NaNs
        nanmask = ~np.isnan(ytmp)

        if i == 0:
            xbin.append(x[0] - np.abs(x[1] - x[0]))
            # create mask to get rid of NaNs
            localnanmask = np.logical_not(np.isnan(y))
            ybin.append(np.median(y[localnanmask][:binsize]))

        if len(xtmp[nanmask]) > 2:
            # calculate mean x within the bin
            xmean = np.mean(xtmp[nanmask])

            # save mean x wihthin bin
            xbin.append(xmean)

            if mode == 'median':
                # save median y of filtered data
                ybin.append(np.median(ytmp[nanmask]))
            elif mode == 'mean':
                # save mean y of filtered data
                ybin.append(np.mean(ytmp[nanmask]))
            else:
                raise DrsCodedException('00-009-10001', 'error',
                                        targs=[mode], func_name=func_name)
        if i == nbins - 1:
            xbin.append(x[-1] + np.abs(x[-1] - x[-2]))
            # create mask to get rid of NaNs
            localnanmask = np.logical_not(np.isnan(y))
            ybin.append(np.median(y[localnanmask][-binsize:]))

    # the continuum may be obtained either by polynomial fit or by
    #  cubic interpolation
    if use_polyfit:
        # Option to use a polynomial fit
        # Fit polynomial function to sample points
        pfit = np.polyfit(xbin, ybin, deg_polyfit)
        # Set numpy poly1d objects
        p = np.poly1d(pfit)
        # Evaluate polynomial in the original grid
        cont = p(x)
    else:
        # option to interpolate points applying a cubic spline to the
        #     continuum data
        sfit = interp1d(xbin, ybin, kind='cubic')
        # Resample interpolation to the original grid
        cont = sfit(x)

    # return continuum polarization and x and y bins
    return cont, xbin, ybin


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
