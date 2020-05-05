#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-23 at 09:29

@author: cook
"""
import numpy as np
import os
import warnings
from astropy import units as uu
from astropy.time import Time
from astropy.coordinates import SkyCoord

from apero import core
from apero import lang
from apero.core import constants
from apero.core import math as mp
from apero.io import drs_fits
from apero.io import drs_lock
from apero.io import drs_path
from apero.science.extract import bervest
from apero.science.extract import crossmatch

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.extract.berv.py'
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
# Get Logging function
WLOG = core.wlog
# Get the text types
TextEntry = lang.drs_text.TextEntry
TextDict = lang.drs_text.TextDict
# alias pcheck
pcheck = core.pcheck


# =============================================================================
# Define property class
# =============================================================================
class BaryCorrpyException(Exception):
    """Raised when config file is incorrect"""
    pass


class Property:
    def __init__(self, name=None, unit=None, headerkey=None, paramkey=None,
                 outkey=None, default=None, datatype=None):
        self.name = name
        self.unit = unit
        self.hkey = headerkey
        self.pkey = paramkey
        self.default = default
        self.outkey = outkey
        self.datatype = datatype


# =============================================================================
# Define user functions
# =============================================================================
# define the properties for barycorrpy
mode1 = dict()
mode1['ra'] = Property(name='ra', unit=uu.deg)
mode1['dec'] = Property(name='dec', unit=uu.deg)
mode1['epoch'] = Property(name='epoch', datatype='jd')
mode1['pmra'] = Property(name='pmra', unit=uu.mas/uu.yr)
mode1['pmde'] = Property(name='pmdec', unit=uu.mas/uu.yr)
mode1['lat'] = Property(name='lat', unit=uu.deg)
mode1['long'] = Property(name='longi', unit=uu.deg)
mode1['alt'] = Property(name='alt', unit=uu.deg)
mode1['plx'] = Property(name='px', unit=uu.mas)
mode1['rv'] = Property(name='rv', unit=uu.km/uu.s)

# define the properties for pyastronomy measurement
mode2 = dict()
mode2['ra'] = Property(name='ra2000', unit=uu.deg)
mode2['dec'] = Property(name='dec2000', unit=uu.deg)
mode2['lat'] = Property(name='obs_lat', unit=uu.deg)
mode2['long'] = Property(name='obs_long', unit=uu.deg)
mode2['alt'] = Property(name='obs_alt', unit=uu.deg)


# =============================================================================
# Define user functions
# =============================================================================
def get_berv(params, infile=None, header=None, props=None, log=True,
             warn=False, force=False, **kwargs):
    func_name = __NAME__ + '.get_berv()'
    # log progress
    if log:
        WLOG(params, 'info', TextEntry('40-016-00017'))
    # get parameters from params and kwargs
    dprtype = pcheck(params, 'DPRTYPE', 'dprtype', kwargs, func_name,
                     paramdict=props)
    dprtypes = pcheck(params, 'EXT_ALLOWED_BERV_DPRTYPES', 'dprtypes', kwargs,
                      func_name, mapf='list', dtype=str)
    kind = pcheck(params, 'EXT_BERV_KIND', 'kind', kwargs, func_name)
    # ----------------------------------------------------------------------
    # do not try to calculate berv for specific DPRTYPES
    if (dprtype not in dprtypes):
        # log that we are skipping due to dprtype
        WLOG(params, '', TextEntry('40-016-00018', args=[dprtype]))
        # all entries returns are empty
        return assign_properties(params, use=False)
    if kind == 'None':
        # log that we are skipping due to user
        WLOG(params, '', TextEntry('40-016-00019'))
        # all entries returns are empty
        return assign_properties(params, use=False)
    # ----------------------------------------------------------------------
    # check if we already have berv (or bervest) if not forced
    if force:
        bprops = None
    else:
        bprops = get_outputs(params, infile, header, props, kwargs)
    # if we have berv already then just return these
    if bprops is not None:
        # log that we are skipping due to user
        WLOG(params, '', TextEntry('40-016-00020'))
        # return entries
        return assign_properties(params, **bprops)
    # ----------------------------------------------------------------------
    # get required parameters
    bprops = get_parameters(params, kind, props, kwargs, infile, header)
    # ----------------------------------------------------------------------
    # deal with setting up time
    # ----------------------------------------------------------------------
    bprops = get_times(params, bprops, infile, header)
    # ----------------------------------------------------------------------
    # try to run barcorrpy
    if kind == 'barycorrpy':
        try:
            # --------------------------------------------------------------
            # calculate berv/bjd
            bervs, bjds = use_barycorrpy(params, bprops['OBS_TIME'],
                                         iteration=0, **bprops)
            # --------------------------------------------------------------
            # calculate max berv (using pyasl as it is faster)
            bervs_, bjds_ = use_pyasl(params, bprops['OBS_TIMES'],
                                      quiet=True, **bprops)
            bervmax = mp.nanmax(np.abs(bervs_))
            # --------------------------------------------------------------
            # calculate berv derivative (add 1 second)
            deltat = (1*uu.s).to(uu.day).value
            berv1, bjd1 = use_barycorrpy(params, bprops['OBS_TIME'] + deltat,
                                         iteration=1, **bprops)
            dberv = np.abs(berv1[0] - bervs[0])
            # --------------------------------------------------------------
            # push into output parameters
            return assign_properties(params, berv=bervs[0], bjd=bjds[0],
                                     bervmax=bervmax, source='barycorrpy',
                                     props=bprops, dberv=dberv)
        except BaryCorrpyException as bce:
            if warn:
                WLOG(params, 'warning', str(bce))
            else:
                pass
    # --------------------------------------------------------------
    # if we are still here must use pyasl BERV estimate
    # ----------------------------------------------------------------------
    # calculate berv/bjd
    bervs, bjds = use_pyasl(params, bprops['OBS_TIMES'], **bprops)
    # --------------------------------------------------------------
    # calculate max berv
    bervmax = mp.nanmax(np.abs(bervs))
    # --------------------------------------------------------------
    # calculate berv derivative (add 1 second)
    deltat = (1 * uu.s).to(uu.day).value
    berv1, bjd1 = use_pyasl(params, [bprops['OBS_TIME'] + deltat], **bprops)
    dberv = np.abs(berv1[0] - bervs[0])
    # --------------------------------------------------------------
    # push into output parameters
    return assign_properties(params, bervest=bervs[0], bjdest=bjds[0],
                             dbervest=dberv,
                             bervmaxest=bervmax, source='pyasl', props=bprops)


def use_barycorrpy(params, times, iteration=0, **kwargs):
    func_name = __NAME__ + '.use_barycorrpy()'
    # get estimate accuracy
    estimate = pcheck(params, 'EXT_BERV_EST_ACC', 'berv_est', kwargs, func_name)
    # get barycorrpy directory
    bc_dir = pcheck(params, 'EXT_BERV_BARYCORRPY_DIR', 'bc_dir', kwargs,
                    func_name)
    iersfile = pcheck(params, 'EXT_BERV_IERSFILE', 'iersfile', kwargs,
                      func_name)
    # iers_a_url = pcheck(params, 'EXT_BERV_IERS_A_URL', 'iers_a_url', kwargs,
    #                     func_name)
    leap_dir = pcheck(params, 'EXT_BERV_LEAPDIR', 'leap_dir', kwargs, func_name)
    leap_update = pcheck(params, 'EXT_BERV_LEAPUPDATE', 'leap_update', kwargs,
                         func_name)
    package = pcheck(params, 'DRS_PACKAGE', 'package', kwargs, func_name)
    # get text dictionary
    tdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])

    # convert kwargs to paramdict (just to be able to use capitals/non-capitals)
    kwargs = ParamDict(kwargs)
    # make leap_dir an absolute path
    leap_dir = drs_path.get_relative_folder(params, package, leap_dir)
    # make barycorrpy directory an absolute path
    bc_dir = drs_path.get_relative_folder(params, package, bc_dir)

    # get args
    # TODO: Add back in leap seconds (when barycorrpy works)
    bkwargs = dict(ra=kwargs['ra'], dec=kwargs['dec'],
                   epoch=kwargs['epoch'], px=kwargs['plx'],
                   pmra=kwargs['pmra'], pmdec=kwargs['pmde'],
                   lat=kwargs['lat'], longi=kwargs['long'],
                   alt=kwargs['alt'], rv=kwargs['rv'] * 1000,
                   leap_update=False)
    # bkwargs = dict(ra=kwargs['ra'], dec=kwargs['dec'],
    #                epoch=kwargs['epoch'], px=kwargs['plx'],
    #                pmra=kwargs['pmra'], pmdec=kwargs['pmde'],
    #                lat=kwargs['lat'], longi=kwargs['long'],
    #                alt=kwargs['alt'], rv=kwargs['rv'] * 1000,
    #                leap_dir=leap_dir, leap_update=leap_update)
    # try to set iers file
    try:
        from astropy.utils import iers
        # iers.IERS_A_URL = iers_a_url
        iers_a_file = os.path.join(bc_dir, iersfile)
        iers.IERS.iers_table = iers.IERS_A.open(iers_a_file)
    except Exception as e:
        WLOG(params, 'warning', 'IERS_A_FILE Warning:' + str(e))
    # try to import barycorrpy
    try:
        with warnings.catch_warnings(record=True) as _:
            import barycorrpy
    except Exception as _:
        wargs = [estimate, func_name]
        WLOG(params, 'warning', TextEntry('10-016-00003', args=wargs))
        raise BaryCorrpyException(tdict['10-016-00003'].format(*wargs))
    # must lock here (barcorrpy is not parallisable yet)
    lpath = params['DRS_DATA_REDUC']
    lfilename = os.path.join(lpath, 'barycorrpy')
    # ----------------------------------------------------------------------
    # define a synchoronized lock for indexing (so multiple instances do not
    #  run at the same time)
    lockfile = os.path.basename('{0}_{1}'.format(lfilename, iteration))
    # start a lock
    lock = drs_lock.Lock(params, lockfile)

    # make locked bervcalc function
    @drs_lock.synchronized(lock, params['PID'])
    def locked_bervcalc():
        # try to calculate bervs and bjds
        try:
            out1 = barycorrpy.get_BC_vel(JDUTC=times, zmeas=0.0, **bkwargs)
            out2 = barycorrpy.utc_tdb.JDUTC_to_BJDTDB(times, **bkwargs)
        except Exception as e:
            # log error
            wargs = [type(e), str(e), estimate, func_name]
            WLOG(params, 'warning', TextEntry('10-016-00004', args=wargs))
            raise BaryCorrpyException(tdict['10-016-00004'].format(*wargs))
        # return the bervs and bjds
        bervs = out1[0] / 1000.0
        bjds = out2[0]
        return bervs, bjds
    # -------------------------------------------------------------------------
    # try to run locked makedirs
    try:
        return locked_bervcalc()
    except KeyboardInterrupt as e:
        lock.reset()
        raise e
    except Exception as e:
        # reset lock
        lock.reset()
        raise e


def use_pyasl(params, times, quiet=False, **kwargs):
    func_name = __NAME__ + '.use_pyasl()'
    # get estimate accuracy
    estimate = pcheck(params, 'EXT_BERV_EST_ACC', 'berv_est', kwargs, func_name)
    # print warning that we are using estimate
    if not quiet:
        WLOG(params, 'warning', TextEntry('10-016-00005', args=[estimate]))
    # convert kwargs to paramdict (just to be able to use capitals/non-capitals)
    kwargs = ParamDict(kwargs)
    # get args
    bkwargs = dict(ra2000=kwargs['ra'], dec2000=kwargs['dec'],
                   obs_long=kwargs['long'], obs_lat=kwargs['lat'],
                   obs_alt=kwargs['alt'])
    # set up storage
    bervs, bjds = [], []

    # loop around each time
    for jdtime in times:
        try:
            # calculate estimate of berv
            berv, bjd = bervest.helcorr(jd=jdtime, **bkwargs)
            # append to lists
            bervs.append(berv)
            bjds.append(bjd)
        except Exception as e:
            wargs = [jdtime, type(e), e, func_name]
            WLOG(params, 'error', TextEntry('00-016-00017', args=wargs))
    # convert lists to numpy arrays and return
    return np.array(bervs), np.array(bjds)


def add_berv_keys(params, infile, props):

    # get the pseudo constants
    pconst = constants.pload(params['INSTRUMENT'])
    # get input properties
    inputs = get_inputs(params)
    # get output properties
    outputs = pconst.BERV_OUTKEYS()
    # add berv/bjd/bervmax/source (output keys)
    for key in outputs:
        # get this output
        output = outputs[key]
        # add key to header
        if output[0] in props:
            infile.add_hkey(output[1], value=props[output[0]])
        else:
            infile.add_hkey(output[1], value='None')
    # add input keys
    for param in inputs.keys():
        # get require parameter instance
        inparam = inputs[param]
        # add key to header
        if param in props:
            infile.add_hkey(inparam.outkey, value=props[param])
        else:
            infile.add_hkey(inparam.outkey, value='None')
    # return infile
    return infile


# =============================================================================
# Define worker functions
# =============================================================================
def assign_properties(params, props=None, use=True, **kwargs):
    """
    Assigns properties from input and deals with missing parameters

    Available kwargs (output keys) come from BERV_OUTKEYS()

    :param params:
    :param props:
    :param kwargs:

    :keyword berv:
    :keyword bjd:
    :keyword bervmax:
    :keyword dberv:
    :keyword source:
    :keyword bervest:
    :keyword bjdest:
    :keyword bervmaxest:
    :keyword dbervest:
    :keyword start_time:
    :keyword exp_time:
    :keyword time_delta:
    :keyword obs_time:

    :return:
    """
    func_name = __NAME__ + '.assign_properties()'
    # get the pseudo constants
    pconst = constants.pload(params['INSTRUMENT'])
    # get estimate accuracy
    estimate = pcheck(params, 'EXT_BERV_EST_ACC', 'berv_est', kwargs, func_name)
    # get parameters from kwargs
    source = kwargs.get('source', 'None')
    # get output properties
    outputs = pconst.BERV_OUTKEYS()
    # get input properties
    inputs = get_inputs(params)
    # set up storage
    oprops = ParamDict()
    # -------------------------------------------------------------------------
    # deal with no props
    if props is None:
        props = ParamDict()
        for key in inputs:
            if isinstance(inputs[key].default, str):
                props[key] = 'None'
            else:
                props[key] = np.nan
            props.set_source(key, '{0} [{1}]'.format(func_name, source))
    # -------------------------------------------------------------------------
    # add outputs
    for key in outputs:
        output = outputs[key]
        # check for the key in kwargs
        value = kwargs.get(key, None)
        # if not found (None) check for the outputs[0] key in kwargs
        if value is None:
            value = kwargs.get(output[0], None)
        if value is None:
            oprops[output[0]] = np.nan
        else:
            oprops[output[0]] = value

        oprops.set_source(output[0], '{0} [{1}]'.format(func_name, source))
    # -------------------------------------------------------------------------
    # deal with inputs (set value and source)
    for prop in props:
        oprops[prop] = props[prop]
        oprops.set_source(prop, props.sources[prop])

    # -------------------------------------------------------------------------
    # need to decide which values should be used (and report if we are using
    #   estimate)
    cond = (oprops['BERV'] is not None and np.isfinite(oprops['BERV']))
    cond &= (oprops['BJD'] is not None and np.isfinite(oprops['BJD']))
    cond &= (oprops['BERV_MAX'] is not None and np.isfinite(oprops['BERV_MAX']))

    # Case 1: Not BERV used
    if not use:
        oprops['USE_BERV'] = None
        oprops['USE_BJD'] = None
        oprops['USE_BERV_MAX'] = None
        oprops['USED_ESTIMATE'] = None
        psource = '{0} [{1}]'.format(func_name, 'None')
    # Case 2: pyasl used
    elif not cond or (source == 'pyasl'):
        # log warning that we are using an estimate
        WLOG(params, 'warning', TextEntry('10-016-00014', args=[estimate]))
        # set parameters
        oprops['USE_BERV'] = oprops['BERV_EST']
        oprops['USE_BJD'] = oprops['BJD_EST']
        oprops['USE_BERV_MAX'] = oprops['BERV_MAX_EST']
        oprops['USED_ESTIMATE'] = True
        psource = '{0} [{1}]'.format(func_name, 'pyasl')
    # Case 3: Barycorrpy used
    else:
        # set parameters
        oprops['USE_BERV'] = oprops['BERV']
        oprops['USE_BJD'] = oprops['BJD']
        oprops['USE_BERV_MAX'] = oprops['BERV_MAX']
        oprops['USED_ESTIMATE'] = False
        psource = '{0} [{1}]'.format(func_name, 'barycorrpy')
    # set source
    keys = ['USE_BERV', 'USE_BJD', 'USE_BERV_MAX', 'USED_ESTIMATE']
    oprops.set_sources(keys, psource)

    # return properties
    return oprops


def get_outputs(params, infile, header, props, kwargs):
    found = False
    # define storage
    bprops = ParamDict()
    # get the pseudo constants
    pconst = constants.pload(params['INSTRUMENT'])
    berv_keys = pconst.BERV_OUTKEYS()
    # loop around keys
    for key in berv_keys:
        inkey, outkey, kind, dtype = berv_keys[key]
        # unset value
        value, datatype = None, None
        # check for outkey in params
        if outkey in params:
            hkey = params[outkey][0]
        else:
            hkey = outkey
        # get the value of the key from infile
        if kind == 'header' and infile is not None:
            if hkey in infile.header:
                value = infile.header[hkey]
                datatype = params.instances[outkey].datatype
                found = True
        # get the value of the key from header
        elif (kind == 'header') and (header is not None) and (value is None):
            if hkey in infile.header:
                value = infile.header[hkey]
                datatype = params.instances[outkey].datatype
                found = True
        # get the value from props
        elif (value is None) and (props is not None) and (key in props):
            value = props[key]
            datatype = dtype
            found = True
        # get the value from kwargs
        elif (value is None) and (key in kwargs):
            value = kwargs[key]
            datatype = dtype
            found = True
        # else set the value
        elif (value is None) and (key in params):
            value = params[outkey]
            datatype = dtype
            found = True
        # push values into props
        if found:
            if datatype is not None:
                bprops[inkey] = datatype(value)
            else:
                bprops[inkey] = value
    # only return if we filled it
    if len(bprops) == len(berv_keys):
        return bprops
    else:
        return None


def get_inputs(params):
    func_name = __NAME__ + '.get_inputs()'
    # set up storage
    inputs = dict()
    # get the pseudo constants
    pconst = constants.pload(params['INSTRUMENT'])
    # get berv keys
    berv_keys = pconst.BERV_INKEYS()
    # loop around keys
    for key in berv_keys:
        inkey, outkey, kind, default = berv_keys[key]
        # find key in params
        if (inkey not in params) and (default is None):
            eargs = [inkey, key, func_name]
            WLOG(params, 'error', TextEntry('00-016-00020', args=eargs))
            units, datatype = None, None
        elif (inkey not in params) and (default is not None):
            datatype, units = None, None
        else:
            instance = params.instances[inkey]
            # get properties
            datatype = instance.datatype
            units = instance.unit
        # deal with kind
        if kind == 'header':
            headerkey = inkey
            paramkey = None
        else:
            headerkey = None
            paramkey = inkey
        # append to inputs
        inputs[key] = Property(unit=units, datatype=datatype,
                               headerkey=headerkey, paramkey=paramkey,
                               outkey=outkey, default=default)
    # return inputs
    return inputs


def get_parameters(params, kind, props=None, kwargs=None, infile=None,
                   header=None):
    func_name = __NAME__ + '.get_parameters()'
    inputs = get_inputs(params)
    # ----------------------------------------------------------------------
    if kind == 'barycorrpy':
        rparams = mode1
    else:
        rparams = mode2
    # ----------------------------------------------------------------------
    # set values to np.nan
    gprops = ParamDict()
    for param in inputs:
        gprops[param] = np.nan
        gprops.set_source(param, func_name)
    # ----------------------------------------------------------------------
    # first get parameters from header
    gprops = get_header_input_props(params, gprops, rparams, inputs, infile,
                                    header, props, kwargs)
    # ----------------------------------------------------------------------
    # update using gaia positions (from lookup table or gaia query)
    gprops = get_input_props_gaia(params, gprops)
    # ----------------------------------------------------------------------
    # return all gprops
    return gprops


def get_header_input_props(params, gprops, rparams, inputs, infile, header,
                           props, kwargs):
    func_name = __NAME__ + '.use_header_input_props()'
    source_name = '{0} [{1}]'
    # ----------------------------------------------------------------------
    # ra and dec have to be dealt with together
    raw_ra, s_ra = get_raw_param(params, 'ra', inputs['ra'], infile, header,
                                 props, kwargs)
    raw_dec, s_dec = get_raw_param(params, 'dec', inputs['dec'], infile, header,
                                   props, kwargs)
    raw_coord = '{0} {1}'.format(raw_ra, raw_dec)
    coords = SkyCoord(raw_coord, unit=(inputs['ra'].unit, inputs['dec'].unit))
    # add to output
    gprops['ra'] = coords.ra.value
    gprops.set_source('ra', source_name.format(func_name, s_dec))
    gprops.set_instance('ra', coords.ra)
    gprops['dec'] = coords.dec.value
    gprops.set_source('dec', source_name.format(func_name, s_dec))
    gprops.set_instance('dec', coords.dec)
    # ----------------------------------------------------------------------
    # deal with gaia id and objname
    gprops['gaiaid'], s_id = get_raw_param(params, 'gaiaid', inputs['gaiaid'],
                                           infile, header, props, kwargs)
    gprops['objname'], s_obj = get_raw_param(params, 'objname',
                                             inputs['objname'], infile, header,
                                             props, kwargs)
    gprops.set_sources(['gaiaid', 'objname'], [s_id, s_obj])
    # ----------------------------------------------------------------------
    # loop around each parameter to get into the format we require
    for param in rparams.keys():
        # skip ra and dec
        if param in ['ra', 'dec', 'gaiaid', 'objname']:
            continue
        # ------------------------------------------------------------------
        # get require parameter instance
        rparam = rparams[param]
        inparam = inputs[param]
        # get the raw parameter value
        rawvalue, source = get_raw_param(params, param, inparam, infile, header,
                                         props, kwargs)
        # ------------------------------------------------------------------
        # apply units to values and convert to expected inputs
        # ------------------------------------------------------------------
        # case 1: have units
        if inparam.unit is not None:
            # apply
            try:
                unitvalue = float(rawvalue) * inparam.unit
            except Exception as e:
                eargs = [param, rawvalue, inparam.unit, type(e), e, func_name]
                WLOG(params, 'error', TextEntry('00-016-00012', args=eargs))
                unitvalue = None
            # convert
            try:
                value = unitvalue.to(rparam.unit)
            except Exception as e:
                eargs = [param, rawvalue, inparam.unit, rparam.unit,
                         type(e), e, func_name]
                WLOG(params, 'error', TextEntry('00-016-00015', args=eargs))
                value = None
        # ------------------------------------------------------------------
        # case 2: have datatype
        elif inparam.datatype is not None:
            # case 2a: is a time
            if inparam.datatype in Time.FORMATS.keys():
                # apply
                try:
                    unitvalue = Time(float(rawvalue), format=inparam.datatype)
                except Exception as e:
                    eargs = [param, rawvalue, inparam.datatype, type(e), e,
                             func_name]
                    WLOG(params, 'error', TextEntry('00-016-00013', args=eargs))
                    unitvalue = None
                # convert:
                try:
                    value = getattr(unitvalue, rparam.datatype)
                except Exception as e:
                    eargs = [param, rawvalue, inparam.datatype, rparam.datatype,
                             type(e), e, func_name]
                    WLOG(params, 'error', TextEntry('00-016-00016', args=eargs))
                    value = None
            # case 2b: is another datatype
            else:
                try:
                    value = inparam.datatype(rawvalue)
                except Exception as e:
                    eargs = [param, rawvalue, inparam.datatype, type(e), e,
                             func_name]
                    WLOG(params, 'error', TextEntry('00-016-00014', args=eargs))
                    value = None
        # ------------------------------------------------------------------
        # case 3: keep as string
        else:
            value = rawvalue
        # ------------------------------------------------------------------
        # add to output props
        if hasattr(value, 'value'):
            gprops[param] = value.value
        else:
            gprops[param] = value
        # add source
        gprops.set_source(param, source_name.format(func_name, source))
        gprops.set_instance(param, inputs[param])
    # set the input source
    gprops['INPUTSOURCE'] = 'header'
    gprops.set_source('INPUTSOURCE', func_name)
    # return properties
    return gprops


def get_input_props_gaia(params, gprops, **kwargs):
    """
    Takes a set of properties 'gprops' and checks for 'GAIAID', 'OBJNAME'
    and 'RA'/'DEC' and tries to look in look-up table / query gaia to
    get new parameters (for all parameters in 'gprops'

    :param params: ParamDict, the constant parameter dictionary
    :param gprops: ParmDict, the properties parameter dictionary
    :param kwargs: keyword arguments

    :type params: ParamDict
    :type gprops: ParamDict

    :keyword gaiaid: string, if defined uses this gaia id
    :keyword objname: string, if defined uses this objname
    :keyword ra: float, if defined uses this right ascension
    :keyword dec: float, if defined uses this declination

    :returns: the updated set of properties (ParamDict)
    :rtype: ParamDict

    """
    func_name = __NAME__ + '.get_input_props_gaia()'
    # get parameters from gprops/kwargs
    gaia_id = pcheck(params, 'gaiaid', 'gaiaid', kwargs, func_name,
                     paramdict=gprops)
    objname = pcheck(params, 'objname', 'objname', kwargs, func_name,
                     paramdict=gprops)
    ra = pcheck(params, 'ra', 'ra', kwargs, func_name, paramdict=gprops)
    dec = pcheck(params, 'dec', 'dec', kwargs, func_name, paramdict=gprops)
    # -----------------------------------------------------------------------
    # case 1: we have gaia id
    # -----------------------------------------------------------------------
    if gaia_id is not None and gaia_id != 'None':
        props, fail = crossmatch.get_params(params, gprops, gaiaid=gaia_id,
                                            objname=objname, ra=ra, dec=dec)
        # deal with failure
        if not fail:
            WLOG(params, '', TextEntry('40-016-00016', args=['gaiaid']))
            return props
    # -----------------------------------------------------------------------
    # case 2: we have objname
    # -----------------------------------------------------------------------
    if gprops['objname'] is not None and gprops['objname'] != 'None':
        props, fail = crossmatch.get_params(params, gprops, objname=objname,
                                            ra=ra, dec=dec)
        # deal with failure
        if not fail:
            WLOG(params, '', TextEntry('40-016-00016', args=['objname']))
            return props
    # -----------------------------------------------------------------------
    # case 3: use ra and dec
    # -----------------------------------------------------------------------
    props, fail = crossmatch.get_params(params, gprops, ra=ra, dec=dec)
    # deal with failure
    if not fail:
        WLOG(params, '', TextEntry('40-016-00016', args=['ra/dec']))
        return props
    else:
        WLOG(params, '', TextEntry('40-016-00016', args=['header']))
        # return gprops
        return gprops


def get_raw_param(params, param, inparam, infile, header, props, kwargs):
    func_name = __NAME__ + '.get_raw_param()'

    # ------------------------------------------------------------------
    # get raw value from: 1. infile, 2. header, 3. props, 4. kwargs
    # ------------------------------------------------------------------
    # unset value
    rawvalue, source = None, 'None'
    # get value from infile
    if (infile is not None) and (inparam.hkey is not None):
        rawvalue = infile.get_key(inparam.hkey, required=False)
        source = str(infile)
    # if not get value from header
    useheader = (inparam.hkey is not None) and (rawvalue is None)
    if (header is not None) and useheader:
        if inparam.hkey in header:
            rawvalue = header[params[inparam.hkey][0]]
            source = 'header'
    # if not get value from props
    if (props is not None) and (rawvalue is None):
        if param in props:
            rawvalue = props[param]
            source = 'props'
    # if not get value from kwargs
    if (kwargs is not None) and (rawvalue is None):
        if param in kwargs:
            rawvalue = kwargs[param]
            source = 'kwargs'
    # if not get value from params
    if (params is not None) and (rawvalue is None):
        if inparam.pkey in params:
            rawvalue = params[inparam.pkey]
            source = 'params'
    # ------------------------------------------------------------------
    # deal with value still being unset
    if rawvalue is None and inparam.default is not None:
        rawvalue = inparam.default
        source = 'default'
    elif rawvalue is None:
        strparam = str(param)
        if inparam.hkey is not None:
            strparam += ' (hkey={0})'.format(inparam.hkey)
        if inparam.pkey is not None:
            strparam += ' (pkey={0})'.format(inparam.pkey)
        eargs = [strparam, func_name]
        WLOG(params, 'error', TextEntry('00-016-00011', args=eargs))
    return rawvalue, source


def get_times(params, bprops, infile, header):
    func_name = __NAME__ + '.get_times()'
    # ---------------------------------------------------------------------
    # deal with header
    if infile is not None:
        header = infile.header
    elif header is not None:
        pass
    else:
        WLOG(params, 'error', TextEntry('00-016-00019', args=[func_name]))
    # ---------------------------------------------------------------------
    # get obs_time
    obstime, method = drs_fits.get_mid_obs_time(params, header, func=func_name)

    # for the maximum peak to peak need an array of times
    times = obstime.jd + np.arange(0, 365, 5.0/3.0)
    # add to bprops
    bprops['OBS_TIME'] = obstime.jd
    bprops['OBS_TIME_METHOD'] = method
    bprops['OBS_TIMES'] = times
    # add source
    keys = ['OBS_TIME', 'OBS_TIMES', 'OBS_TIME_METHOD']
    bprops.set_sources(keys, func_name)
    # return bprops
    return bprops


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
