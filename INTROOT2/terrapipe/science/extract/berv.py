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
from astropy import units as uu
from astropy.time import Time, TimeDelta

from terrapipe import core
from terrapipe import locale
from terrapipe.core import constants
from terrapipe.io import drs_fits
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
                 outkey=None, default=None, dtype=None):
        self.name = name
        self.unit = unit
        self.hkey = headerkey
        self.pkey = paramkey
        self.default = default
        self.outkey = outkey
        self.dtype = dtype


# =============================================================================
# Define user functions
# =============================================================================
# define input properties (the value expected to be inputed)
inputs = dict()
inputs['ra'] = Property(unit=uu.deg, headerkey='KW_OBJRA',
                        outkey='KW_BERVRA')
inputs['dec'] = Property(unit=uu.deg, headerkey='KW_OBJDEC',
                         outkey='KW_BERVDEC')
inputs['epoch'] = Property(dtype='decimalyear', headerkey='KW_OBJEQUIN',
                           outkey='KW_BERVEPOCH')
inputs['pmra'] = Property(unit=uu.mas/uu.yr, headerkey='KW_OBJRAPM',
                           outkey='KW_BERVPMRA')
inputs['pmde'] = Property(unit=uu.mas/uu.yr, headerkey='KW_OBJDECPM',
                          outkey='KW_BERVPMDE')
inputs['lat'] = Property(unit=uu.deg, paramkey='OBS_LAT',
                          outkey='KW_BERVLAT')
inputs['long'] = Property(unit=uu.deg, paramkey='OBS_LONG',
                          outkey='KW_BERVLONG')
inputs['alt'] = Property(unit=uu.deg, paramkey='OBS_ALT',
                          outkey='KW_BERVALT')
inputs['plx'] = Property(unit=uu.mas, outkey='KW_BERVPLX', default=0.0)

# define the properties for barycorrpy
mode1 = dict()
mode1['ra'] = Property(name='ra', unit=uu.deg)
mode1['dec'] = Property(name='dec', unit=uu.deg)
mode1['epcoh'] = Property(name='epoch', dtype='jd')
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
    if dprtype not in dprtypes:
        # all entries returns are empty
        return assign_properties()
    # ----------------------------------------------------------------------
    # get required parameters
    bprops = get_parameters(kind, props, kwargs, infile, header)
    # ----------------------------------------------------------------------
    # deal with setting up time
    # ----------------------------------------------------------------------
    bprops = get_times(params, bprops, infile, header, props, kwargs)
    # ----------------------------------------------------------------------
    # try to run barcorrpy
    try:
        # calculate berv/bjd
        bervs, bjds = use_barycorrpy(params, bprops['OBS_TIMES'], **bprops)
        # calculate max berv
        bervmax = np.max(np.abs(bervs))
        # push into output parameters
        return assign_properties(berv=bervs[0], bjd=bjds[0], bervmax=bervmax,
                                 source='barycorrpy', props=bprops)
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
    # try to calculate bervs and bjds
    try:
        out1 = barycorrpy.get_BC_vel(JDUTC=times, zmeas=0.0, **bkwargs)
        out2 = barycorrpy.utc_tdb.JDUTC_to_BJDTDB(times, **bkwargs)
    except Exception as e:
        wargs = [type(e), str(e), estimate, func_name]
        WLOG(params, 'warning', TextEntry('10-0016-00004', args=wargs))
        raise BaryCorrpyException(tdict['10-0016-00004'].format(*wargs))
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


def add_berv_keys(infile, props):
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
        oprops['SOURCE'] = 'None'
    else:
        oprops['SOURCE'] = source
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
    keys = ['BERV', 'BJD', 'BERV_MAX', 'SOURCE', 'BERV_EST', 'BJD_EST',
            'BERV_MAX_EST']
    oprops.set_sources(keys, func_name)
    # deal with current props (set value and source)
    for prop in props:
        oprops[prop] = props[prop]
        oprops.set_source(prop, props.sources[prop])
    # return properties
    return oprops


def get_parameters(params, kind, props=None, kwargs=None, infile=None,
                   header=None):
    func_name = __NAME__ + '.get_parameters()'
    source_name = '{0} [{1}]'
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
     # loop around each parameter to get into the format we require
    for param in rparams.keys():
        # get require parameter instance
        rparam = rparams[param]
        inparam = inputs[param]
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
                rawvalue = infile.get_key
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
        # case 2: have dtype
        elif inparam.dtype is not None:
            # case 2a: is a time
            if inparam in Time.FORMATS.keys():
                # apply
                try:
                    unitvalue = Time(float(rawvalue), format=inparam.dtype)
                except Exception as e:
                    eargs = [param, rawvalue, inparam.dtype, type(e), e,
                             func_name]
                    WLOG(params, 'error', TextEntry('00-016-00013', args=eargs))
                    unitvalue = None
                # convert:
                try:
                    value = getattr(unitvalue, rparam.dtype)
                except Exception as e:
                    eargs = [param, rawvalue, inparam.dtype, rparam.dtype,
                             type(e), e, func_name]
                    WLOG(params, 'error', TextEntry('00-016-00016', args=eargs))
                    value = None
            # case 2b: is another dtype
            else:
                try:
                    value = inparam.dtype(rawvalue)
                except Exception as e:
                    eargs = [param, rawvalue, inparam.dtype, type(e), e,
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
    # retyrb all gprops
    return gprops


def get_times(params, bprops, infile, header, props, kwargs):
    func_name = __NAME__ + '.get_times()'
    # get parameters from params/kwargs
    exptime = pcheck(params, 'EXPTIME', 'exptime', kwargs, func_name,
                     paramdict=props)
    exptime_units = pcheck(params, 'EXPTIME_UNITS', 'expunits', kwargs,
                           func_name)
    # convert units to astorpy units
    if exptime_units == 's':
        eunits = uu.s
    elif exptime_units == 'min':
        eunits = uu.min
    elif exptime_units == 'hr':
        eunits = uu.hr
    elif exptime_units == 'day':
        eunits = uu.day
    else:
        types = ['s', 'min', 'hr', 'day']
        eargs = [exptime_units, ' or '.join(types), func_name]
        WLOG(params, 'error', TextEntry('', args=eargs))
        eunits = None
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
    timedelta = TimeDelta(exptime * eunits) / 2.0
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
