#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-23 at 09:29

@author: cook
"""
from __future__ import division
import numpy as np
import os
from astropy import units as uu
from astropy.time import Time, TimeDelta
from astropy.coordinates import SkyCoord

from terrapipe import core
from terrapipe import locale
from terrapipe.core import constants
from terrapipe.io import drs_fits
from terrapipe.io import drs_lock
from . import bervest

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.extract.berv.py'
__INSTRUMENT__ = 'SPIROU'
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
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict
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
mode1['epcoh'] = Property(name='epoch', datatype='jd')
mode1['pmra'] = Property(name='pmra', unit=uu.mas/uu.yr)
mode1['pmde'] = Property(name='pmdec', unit=uu.mas/uu.yr)
mode1['lat'] = Property(name='lat', unit=uu.deg)
mode1['long'] = Property(name='longi', unit=uu.deg)
mode1['alt'] = Property(name='alt', unit=uu.deg)
mode1['plx'] = Property(name='px', unit=uu.mas)

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
def get_berv(params, infile=None, header=None, props=None, **kwargs):
    func_name = __NAME__ + '.get_berv()'
    # get parameters from params and kwargs
    dprtype = pcheck(params, 'DPRTYPE', 'dprtype', kwargs, func_name,
                     paramdict=props)
    dprtypes = pcheck(params, 'EXT_ALLOWED_BERV_DPRTYPES', 'dprtypes', kwargs,
                      func_name, mapf='list', dtype=str)
    kind = pcheck(params, 'EXT_BERV_KIND', 'kind', kwargs, func_name)
    # ----------------------------------------------------------------------
    # do not try to calculate berv for specific DPRTYPES
    if (dprtype not in dprtypes) or (kind == 'None'):
        # all entries returns are empty
        return assign_properties()
    # ----------------------------------------------------------------------
    # check if we already have berv (or bervest)
    bprops = get_outputs(params, infile, header, props, kwargs)
    # if we have berv already then just return these
    if bprops is not None:
        return assign_properties(**bprops)
    # ----------------------------------------------------------------------
    # get required parameters
    bprops = get_parameters(params, kind, props, kwargs, infile, header)
    # ----------------------------------------------------------------------
    # deal with setting up time
    # ----------------------------------------------------------------------
    bprops = get_times(params, bprops, infile, header, props, kwargs)
    # ----------------------------------------------------------------------
    # try to run barcorrpy
    if kind == 'barycorrpy':
        try:
            # calculate berv/bjd
            bervs, bjds = use_barycorrpy(params, bprops['OBS_TIMES'], **bprops)
            # calculate max berv
            bervmax = np.max(np.abs(bervs))
            # push into output parameters
            return assign_properties(berv=bervs[0], bjd=bjds[0],
                                     bervmax=bervmax, source='barycorrpy',
                                     props=bprops)
        except BaryCorrpyException:
            pass
    # ----------------------------------------------------------------------
    # calculate berv/bjd
    bervs, bjds = use_pyasl(params, bprops['OBS_TIMES'], **bprops)
    # calculate max berv
    bervmax = np.max(np.abs(bervs))
    # push into output parameters
    return assign_properties(bervest=bervs[0], bjdest=bjds[0],
                             bervmaxest=bervmax, source='pyasl', props=bprops)


def use_barycorrpy(params, times, **kwargs):
    func_name = __NAME__ + '.use_barycorrpy()'
    # get estimate accuracy
    estimate = pcheck(params, 'EXT_BERV_EST_ACC', 'berv_est', kwargs, func_name)
    # get text dictionary
    tdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
    # get args
    bkwargs = dict(ra=kwargs['ra'], dec=kwargs['dec'],
                   epoch=kwargs['epoch'], px=kwargs['plx'],
                   pmra=kwargs['pmra'], pmdec=kwargs['pmde'],
                   lat=kwargs['lat'], longi=kwargs['long'],
                   alt=kwargs['alt'])
    # try to import barycorrpy
    try:
        import barycorrpy
    except Exception as _:
        wargs = [estimate, func_name]
        WLOG(params, 'warning', TextEntry('10-0016-00003', args=wargs))
        raise BaryCorrpyException(tdict['10-0016-00003'].format(*wargs))
    # must lock here (barcorrpy is not parallisable yet)
    lpath = params['DRS_DATA_REDUC']
    lfilename = os.path.join(lpath, 'barycorrpy')
    lock, lockfile = drs_lock.check_lock_file(params, lfilename)
    # try to calculate bervs and bjds
    try:
        out1 = barycorrpy.get_BC_vel(JDUTC=times, zmeas=0.0, **bkwargs)
        out2 = barycorrpy.utc_tdb.JDUTC_to_BJDTDB(times, **bkwargs)
    except Exception as e:
        # unlock barycorrpy
        drs_lock.close_lock_file(params, lock, lockfile, lfilename)
        # log error
        wargs = [type(e), str(e), estimate, func_name]
        WLOG(params, 'warning', TextEntry('10-0016-00004', args=wargs))
        raise BaryCorrpyException(tdict['10-0016-00004'].format(*wargs))
    # unlock barycorrpy
    drs_lock.close_lock_file(params, lock, lockfile, lfilename)
    # return the bervs and bjds
    bervs = out1[0] / 1000.0
    bjds = out2[0]
    return bervs, bjds


def use_pyasl(params, times, **kwargs):
    func_name = __NAME__ + '.use_pyasl()'
    # get estimate accuracy
    estimate = pcheck(params, 'EXT_BERV_EST_ACC', 'berv_est', kwargs, func_name)
    # print warning that we are using estimate
    WLOG(params, 'warning', TextEntry('10-0016-00005', args=[estimate]))
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
            berv, bjd = bervest.helcorr(jdtime, **bkwargs)
            # append to lists
            bervs.append(berv)
            bjds.append(bjd)
        except Exception as e:
            wargs = [jdtime, type(e), e, func_name]
            WLOG(params, 'error', TextEntry('00-016-00017', args=wargs))
    # convert lists to numpy arrays and return
    return np.array(bervs), np.array(bjds)


def add_berv_keys(params, infile, props):
    inputs = get_inputs(params)
    # add berv/bjd/bervmax/source
    infile.add_hkey('KW_BERV', value=props['BERV'])
    infile.add_hkey('KW_BJD', value=props['BJD'])
    infile.add_hkey('KW_BERVMAX', value=props['BERVMAX'])
    infile.add_hkey('KW_BERVSOURCE', value=props['BERVSOURCE'])
    # add berv/bjd/bervmax estimate
    infile.add_hkey('KW_BERV_EST', value=props['BERV_EST'])
    infile.add_hkey('KW_BJD_EST', value=props['BJD_EST'])
    infile.add_hkey('KW_BERVMAX_EST', value=props['BERVMAX_EST'])
    # add input keys
    for param in inputs.keys():
        # get require parameter instance
        inparam = inputs[param]
        # add key to header
        infile.add_hkey(inparam.outkey, value=props[inparam])
    # return infile
    return infile


# =============================================================================
# Define worker functions
# =============================================================================
def assign_properties(berv=None, bjd=None, bervmax=None, source=None,
                      bervest=None, bjdest=None, bervmaxest=None, props=None):
    func_name = __NAME__ + '.assign_properties()'
    # set up storage
    oprops = ParamDict()
    # assign berv
    if berv is None:
        oprops['BERV'] = np.nan
    else:
        oprops['BERV'] = berv
    # assign bjd
    if bjd is None:
        oprops['BJD'] = np.nan
    else:
        oprops['BJD'] = bjd
    # assign berv max
    if bervmax is None:
        oprops['BERV_MAX'] = np.nan
    else:
        oprops['BERV_MAX'] = bervmax
    # assign source
    if source is None:
        oprops['BERV_SOURCE'] = 'None'
    else:
        oprops['BERV_SOURCE'] = source
    # assign berv estimate
    if bervest is None:
        oprops['BERV_EST'] = np.nan
    else:
        oprops['BERV_EST'] = bervest
    # assign bjd estimate
    if bjdest is None:
        oprops['BJD_EST'] = np.nan
    else:
        oprops['BJD_EST'] = bjdest
    # assign berv max estimate
    if bervmaxest is None:
        oprops['BERV_MAX_EST'] = np.nan
    else:
        oprops['BERV_MAX_EST'] = bervmaxest
    # add source
    keys = ['BERV', 'BJD', 'BERV_MAX', 'BERV_SOURCE', 'BERV_EST', 'BJD_EST',
            'BERV_MAX_EST']
    oprops.set_sources(keys, func_name)
    # deal with current props (set value and source)
    for prop in props:
        oprops[prop] = props[prop]
        oprops.set_source(prop, props.sources[prop])
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
        # get the value of the key from infile
        if kind == 'header' and infile is not None:
            if outkey in infile.header:
                value = infile.header[outkey][0]
                datatype = params.instance[outkey].datatype
                found = True
        # get the value of the key from header
        if (kind == 'header') and (header is not None) and (value is None):
            if outkey in infile.header:
                value = infile.header[outkey][0]
                datatype = params.instance[outkey].datatype
                found = True
        # get the value from props
        if (value is None) and (key in props):
            value = props[key]
            datatype = dtype
            found = True
        # get the value from kwargs
        if (value is None) and (key in kwargs):
            value = kwargs[key]
            datatype = dtype
            found = True
        # else set the value
        if (value is None) and (key in params):
            value = params[outkey]
            datatype = dtype
            found = True
        # push values into props
        if found:
            bprops[inkey] = datatype(value)
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
    source_name = '{0} [{1}]'
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
    gprops['dec'] = coords.dec.value
    gprops.set_source('dec', source_name.format(func_name, s_dec))

    # ----------------------------------------------------------------------
    # loop around each parameter to get into the format we require
    for param in rparams.keys():
        # skip ra and dec
        if param in ['ra', 'dec']:
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
            value = str(rawvalue)
        # ------------------------------------------------------------------
        # add to output props
        gprops[param] = value
        gprops.set_source(param, source_name.format(func_name, source))

    # ----------------------------------------------------------------------
    # retyrb all gprops
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
        rawvalue = infile.get_key(inparam.hkey)
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
        if param in params:
            rawvalue = params[param]
            source = 'params'
    # ------------------------------------------------------------------
    # deal with value still being unset
    if rawvalue is None and inparam.default is not None:
        rawvalue = inparam.default
    elif rawvalue is None:
        eargs = [param, func_name]
        WLOG(params, 'error', TextEntry('00-016-00011', args=eargs))
    return rawvalue, source


def get_times(params, bprops, infile, header, props, kwargs):
    func_name = __NAME__ + '.get_times()'
    # get parameters from params/kwargs
    if 'exptime' in kwargs:
        exptime = kwargs['exptime']
        exp_timeunit = uu.s
    else:
        exp_timekey = params['KW_EXPTIME']
        exp_timeunit = params.instances['KW_EXPTIME'].unit
        exptime = pcheck(params, exp_timekey, func=func_name, paramdict=props)
    # ---------------------------------------------------------------------
    # deal with header
    if infile is not None:
        header = infile.header
    elif header is not None:
        pass
    else:
        WLOG(params, 'error', TextEntry('00-016-00019', args=[func_name]))
    # ----------------------------------------------------------------------
    # get header time
    starttime = drs_fits.header_start_time(params, header, 'jd', func=func_name)
    # get the time after start of the observation
    timedelta = TimeDelta(exptime * exp_timeunit) / 2.0
    # calculate observation time
    obstime = starttime + timedelta
    # for the maximum peak to peak need an array of times
    times = obstime + np.arange(0, 365, 5.0/3.0)
    # add to bprops
    bprops['OBS_TIME'] = obstime
    bprops['OBS_TIMES'] = times
    bprops.set_sources(['OBS_TIME', 'OBS_TIMES'], func_name)
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
