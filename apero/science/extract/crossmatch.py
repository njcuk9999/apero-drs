#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-24 at 12:49

@author: cook
"""
import numpy as np
from astropy.coordinates import SkyCoord
from astropy import units as uu
from astropy.table import vstack, Table
from astropy.time import Time
import time
import os
import warnings

from apero import core
from apero import lang
from apero.core import constants
from apero.io import drs_lock
from apero.io import drs_data
from apero.io import drs_table

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.extract.crossmatch.py'
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
# master crossmatch query
QUERY_MASTER = 'SELECT {0} FROM {1} WHERE {2}'
QCOLS = ('ra as ra, dec as dec, source_id as gaiaid, parallax as plx, '
         'pmdec as pmde, pmra as pmra, radial_velocity as rv, '
         'phot_g_mean_mag as gmag, phot_bp_mean_mag as bpmag, '
         'phot_rp_mean_mag as rpmag')
QSOURCE = 'gaiadr2.gaia_source'
QWHERE1 = 'source_id = {id}'
QWHERE2 = ('1=CONTAINS(POINT(\'ICRS\', ra, dec), CIRCLE(\'ICRS\', {ra}, '
          '{dec}, {radius}))')
QWHERE3 = ('(parallax is not NULL) AND (pmdec is not NULL) AND '
           '(pmra is not NULL)')
QWHERE4 = ('(phot_rp_mean_mag < {0})')
QWHERE5 = ('(parallax > {0})')



# =============================================================================
# Define user functions
# =============================================================================
def get_params(params, _props, gaiaid=None, objname=None, ra=None, dec=None,
               hdr_objname=None):
    func_name = __NAME__ + '.get_props()'
    # get paramters from params
    mag_cut = pcheck(params, 'OBJ_LIST_GAIA_MAG_CUT', func_name)
    parallax_cut = pcheck(params, 'OBJ_LIST_GAIA_PLX_LIM', func_name)
    # ----------------------------------------------------------------------
    # get lookuptablename
    lookuptablename = drs_data.load_object_list(params, return_filename=True)
    # ----------------------------------------------------------------------
    # define a synchoronized lock for indexing (so multiple instances do not
    #  run at the same time)
    lockfile = os.path.basename(lookuptablename)
    # start a lock
    lock = drs_lock.Lock(params, lockfile)

    # make locked lookuptable function
    @drs_lock.synchronized(lock, params['PID'])
    def locked_lookuptable():

        ## TODO: remove break point
        constants.break_point(params)
        # ----------------------------------------------------------------------
        if os.path.exists(lookuptablename):
            # load lookup table from file
            lookuptable = drs_data.load_object_list(params)
            # make sure all columns are lower case
            for col in lookuptable.colnames:
                lookuptable[col].name = col.lower()
            # check if props are in lookup table
            # TODO: fix problem row is blank
            intable, row = inlookuptable(params, lookuptable, gaiaid, objname,
                                         ra, dec)
            source = 'GAIA [TABLE]'
        else:
            intable = False
            lookuptable = None
            source, row = None, None
        # ----------------------------------------------------------------------
        # if not then try to query gaia
        if not intable:
            # get row via query to gaia
            row, fail = query_gaia(params, gaiaid, objname, ra, dec,
                                   hdr_objname=hdr_objname)
            # push row into lookup table for future use
            if not fail:
                updatelookuptable(params, lookuptable, lookuptablename, row)
            # set source
            source = 'GAIA [QUERY]'
        else:
            fail = False
        # ----------------------------------------------------------------------
        # update props with row
        if not fail:
            # loop around properties
            for prop in row.colnames:
                # update each properties
                _props[prop] = row[prop]
                # set source
                sourcename = '{0} [{1}]'.format(func_name, source)
                _props.set_source(prop, sourcename)
        # ----------------------------------------------------------------------
        # set the input source
        if source is not None:
            _props['INPUTSOURCE'] = source
            _props.set_source('INPUTSOURCE', func_name)
        # ----------------------------------------------------------------------
        # set the limits used
        _props['GAIA_MAG_LIM'] = mag_cut
        _props['GAIA_PLX_LIM'] = parallax_cut
        _props.set_sources(['GAIA_MAG_LIM', 'GAIA_PLX_LIM'], func_name)
        # ----------------------------------------------------------------------
        # deal with NaN values
        unsetvalues = ['PMRA', 'PMDE', 'PLX', 'RV']
        for unsetvalue in unsetvalues:
            if np.isnan(_props[unsetvalue]):
                # debug log message
                dargs = [unsetvalue, func_name]
                WLOG(params, 'debug', TextEntry('90-016-00001', args=dargs))
                # set to zero
                _props[unsetvalue] = 0.0
        # ----------------------------------------------------------------------
        # return props and fail criteria
        return _props, fail
    # -------------------------------------------------------------------------
    # try to run locked makedirs
    try:
        return locked_lookuptable()
    except KeyboardInterrupt as e:
        lock.reset()
        raise e
    except Exception as e:
        # reset lock
        lock.reset()
        raise e


# =============================================================================
# Define worker functions
# =============================================================================
def updatelookuptable(params, lookuptable, lookuptablename, row):
    func_name = __NAME__ + '.updatelookuptable()'
    # make sure all columns are lower case
    for col in row.colnames:
        row.columns[col].name = col.lower()
    # combine tables
    try:
        if os.path.exists(lookuptablename):
            # stack row on table
            table = vstack([lookuptable, row])
        else:
            # else create table from row
            table = Table()
            with warnings.catch_warnings(record=True) as _:
                for col in row.colnames:
                    table[col] = [row[col]]
        # save table to file
        table.write(lookuptablename, overwrite=True)
    except Exception as e:
        eargs = [lookuptablename, type(e), e, func_name]
        WLOG(params, 'error', TextEntry('00-016-00022', args=eargs))


def inlookuptable(params, table, gaiaid=None, objname=None, ra=None, dec=None,
                  **kwargs):
    func_name = __NAME__ + '.inlookuptable()'
    # get parameters from params/kwargs
    radius = pcheck(params, 'OBJ_LIST_CROSS_MATCH_RADIUS', 'radius', kwargs,
                    func_name)
    # set in table to False
    intable, row = False, None
    # deal with no rows
    if len(table) == 0:
        return False, None
    # ----------------------------------------------------------------------
    # deal with having a gaia id
    if gaiaid not in [None, 'None', 'NONE']:
        # check format of table gaia id
        gaia_ids, dtype = drs_table.force_dtype_col(table['gaiaid'],
                                                    upper=True, strip=True)
        # find rows in table with valid gaia id
        try:
            # if something went wrong with the gaia col set mask to empty
            if gaia_ids is None:
                mask = []
            # else try to cast the gaia id to dtype
            else:
                mask = dtype(gaiaid) == gaia_ids
        except Exception as _:
            mask = []
        # if we have entires use the first one
        if np.sum(mask) > 0:
            # set intable to True
            intable = True
            # use the first row as our row
            row = table[mask][0]
        else:
            intable, row = False, None
    # ----------------------------------------------------------------------
    # deal with having objname
    if (objname is not None) and (not intable):
        # check format of table obj names
        objnames, dtype = drs_table.force_dtype_col(table['objname'], dtype=str,
                                                    upper=True, strip=True)
        # find rows in table with valid objname
        try:
            # if something went wrong with the gaia col set mask to empty
            if objnames is None:
                mask = []
            # else try to cast the gaia id to dtype
            else:
                mask = str(objname).upper().strip() == objnames
        except Exception as _:
            mask = []
        # if we have entires use the first one
        if np.sum(mask) > 0:
            # set intable to True
            intable = True
            # use the first row as our row
            row = table[mask][0]
        else:
            intable, row = False, None
    # ----------------------------------------------------------------------
    # deal with having ra and dec
    if (ra is not None) and (dec is not None) and (not intable):
        # get radius in degress
        radius_degrees = (radius*uu.arcsec).to(uu.deg)
        # crossmatch table
        try:
            # force ra and dec columsn to floats
            ras, _ = drs_table.force_dtype_col(table['ra'], dtype=float)
            decs, _ = drs_table.force_dtype_col(table['dec'], dtype=float)
            # deal with no ra/decs
            if ras is None or decs is None:
                mask, separation = [], []
            # else crossmatch
            else:
                mask, separation = crossmatch(ra, dec, ras, decs,
                                              radius=radius_degrees)
            # if we have entires use the first one
            if np.sum(mask) > 0:
                # set intable to True
                intable = True
                # find closest
                pos = np.argmin(np.abs(separation[mask]))
                # use closest row
                row = table[pos]
            else:
                intable, row = False, None
        except Exception as e:
            wargs = [ra, dec, radius, type(e), e, func_name]
            WLOG(params, 'warning', TextEntry('10-016-00006', args=wargs))
            intable, row = False
    # ------------------------------------------------------------------
    # return
    return intable, row


def crossmatch(ra, dec, ras, decs, radius):
    # deal with units
    if hasattr(radius, 'value'):
        radius = radius.value
    # get Sky Coord instances
    coords = SkyCoord(ras, decs, unit='deg')
    coord = SkyCoord(ra, dec, unit='deg')
    # get separation
    separation = coords.separation(coord).value
    # mask by radius
    mask = separation < radius
    # return mask and separations
    return mask, separation


def query_gaia(params, gaiaid=None, objname=None, ra=None, dec=None,
               hdr_objname=None, **kwargs):
    func_name = __NAME__ + '.inlookuptable()'
    # get parameters from params/kwargs
    radius = pcheck(params, 'OBJ_LIST_CROSS_MATCH_RADIUS', 'radius', kwargs,
                    func_name)
    query = kwargs.get('query', None)
    url = pcheck(params, 'OBJ_LIST_GAIA_URL', 'url', kwargs, func_name)
    mag_cut = pcheck(params, 'OBJ_LIST_GAIA_MAG_CUT', 'mag_cut', kwargs,
                     func_name)
    parallax_cut = pcheck(params, 'OBJ_LIST_GAIA_PLX_LIM', 'plx_lim', kwargs,
                          func_name)
    gaiaepoch = pcheck(params, 'OBJ_LIST_GAIA_EPOCH', 'gaia_epoch', kwargs,
                       func_name)
    # get gaia epoch
    epoch = Time(gaiaepoch, format='decimalyear')
    # get radius in degress
    radius_degrees = (radius * uu.arcsec).to(uu.deg)
    # ------------------------------------------------------------------
    # check for astroquery and return a fail and warning if not installed
    try:
        from astroquery.utils.tap.core import TapPlus

    except Exception as e:
        eargs = [type(e), str(e), func_name]
        WLOG(params, 'warning', TextEntry('10-016-00009', args=eargs))
        return None, True
    # ------------------------------------------------------------------
    # create TAP query based on gaia id
    if (gaiaid is not None) and (query is None):
        # set up where statement
        where = '{0} AND {1}'.format(QWHERE1, QWHERE3)
        # pipe to query
        query = QUERY_MASTER.format(QCOLS, QSOURCE, where)
        # push in gaia id
        query = query.format(id=gaiaid)
        WLOG(params, '', TextEntry('40-016-00015', args=['gaiaid']))
    # ------------------------------------------------------------------
    # create TAP query based on objname
    if (objname is not None) and (query is None):
        WLOG(params, '', TextEntry('40-016-00015', args=['objname']))
        ra, dec = query_simbad(params, objname)
    # ------------------------------------------------------------------
    # create TAP query based on ra and dec
    if (ra is not None) and (dec is not None) and (query is None):
        # log progres
        WLOG(params, '', TextEntry('40-016-00015', args=['ra/dec']))
        # mag cut
        qwhere4 = QWHERE4.format(mag_cut)
        # parallax cut
        qwhere5 = QWHERE5.format(parallax_cut)
        # set up where statement
        wargs = [QWHERE2, QWHERE3, qwhere4, qwhere5]
        where = '{0} AND {1} AND {2} AND {3}'.format(*wargs)
        # pipe to query
        query = QUERY_MASTER.format(QCOLS, QSOURCE, where)
        # push in ra/dec/radius
        query = query.format(ra=ra, dec=dec, radius=radius_degrees.value)
    # ------------------------------------------------------------------
    # deal with no query
    if query is None:
        WLOG(params, 'warning', TextEntry('10-016-00007', args=[func_name]))
        return None, True
    # ------------------------------------------------------------------
    # try running gaia query
    try:
        with warnings.catch_warnings(record=True) as _:
            # construct gaia TapPlus instance
            gaia = TapPlus(url=url)
            # launch gaia job
            job = gaia.launch_job(query=query)
            # get gaia table
            table = job.get_results()
    except Exception as e:
        wargs = [url, query, type(e), e, func_name]
        WLOG(params, 'warning', TextEntry('10-016-00008', args=wargs))
        # return No row and True to fail
        return None, True
    # ------------------------------------------------------------------
    # if we have no entries we did not find object
    if len(table) == 0:
        # warn that no rows were found
        WLOG(params, 'warning', TextEntry('10-016-00011', args=[func_name]))
        # return No row and True to fail
        return None, True
    # ------------------------------------------------------------------
    # Better format the table
    # ------------------------------------------------------------------
    # fill masked value for RV (other columns must be filled)
    table['rv'].fill_value = 0.0
    table = table.filled()
    # add objname column
    if objname is not None:
        table['objname'] = [objname] * len(table)
    else:
        table['objname'] = [hdr_objname] * len(table)
    # add epoch (in JD)
    table['epoch'] = [epoch.jd] * len(table)
    # ------------------------------------------------------------------
    # if we only have one row then we have found our value
    if len(table) == 1:
        return table[0], False
    # else crossmatch table with ra/dec (and keep closest)
    else:
        try:
            mask, separation = crossmatch(ra, dec, table['ra'], table['dec'],
                                          radius=radius_degrees)
            # if we have entires use the first one
            if np.sum(mask) > 0:
                # find closest
                pos = np.argmin(np.abs(separation[mask]))
                # use closest row
                row = table[pos]
                # return row and False to Fail
                return row, False
            else:
                # return no row and True to Fail
                return None, True
        except Exception as e:
            wargs = [ra, dec, radius, type(e), e, func_name]
            WLOG(params, 'warning', TextEntry('10-016-00010', args=wargs))
            # return no row and True to Fail
            return None, True


def query_simbad(params, object_name):
    """
    Take in object name and query simbad
    :return:
    """
    # check for astroquery and return a fail and warning if not installed
    try:
        # import astroquery
        from astroquery.simbad import Simbad
        # get results
        with warnings.catch_warnings(record=True) as _:
            # log that we are querying simbad
            WLOG(params, '', TextEntry(''))
            # wait 1 seconds (avoid IP being banned)
            time.sleep(1)
            # query simbad
            results = Simbad.query_object(object_name)
        # ------------------------------------------------------------------
        # if we have no results return ra and dec as None
        if results is None:
            # log that we have no results for object name from simbad
            wargs = [object_name]
            WLOG(params, 'warning', TextEntry('10-016-00015', args=[wargs]))
            # return unset ra/dec
            return None, None
        # ------------------------------------------------------------------
        # try to get ra from results
        if 'RA' in results.colnames:
            ra_value = results['RA'][0]
            ra_unit = results['RA'].unit
        else:
            # log that we have no RA column for object name
            wargs = [object_name, ', '.join(results.colnames)]
            WLOG(params, 'warning', TextEntry('10-016-00016', args=wargs))
            # return unset ra/dec
            return None, None
        # ------------------------------------------------------------------
        # try to get dec from results
        if 'DEC' in results.colnames:
            dec_value = results['DEC'][0]
            dec_unit = results['DEC'].unit
        else:
            # log that we have no DEC column for object name
            wargs = [object_name, ', '.join(results.colnames)]
            WLOG(params, 'warning', TextEntry('10-016-00017', args=wargs))
            # return unset ra/dec
            return None, None
        # ------------------------------------------------------------------
        # deal with ra unit
        if not isinstance(ra_unit, uu.Unit):
            if str(ra_unit) == '"h:m:s"':
                ra_unit = uu.hourangle
            else:
                # log that we have not ra unit
                wargs = [object_name, str(ra_unit)]
                WLOG(params, 'warning', TextEntry('10-016-00018', args=wargs))
                # return unset ra/dec
                return None, None
        # ------------------------------------------------------------------
        # deal with dec unit
        if not isinstance(dec_unit, uu.Unit):
            if str(dec_unit) == '"d:m:s"':
                dec_unit = uu.degree
            else:
                # log that we have not ra unit
                wargs = [object_name, str(dec_unit)]
                WLOG(params, 'warning', TextEntry('10-016-00019', args=wargs))
                # return unset ra/dec
                return None, None
        # ------------------------------------------------------------------
        # get sky coordinate
        coord = SkyCoord(ra_value, dec_value, unit=(ra_unit, dec_unit))
        # return ra and dec
        return coord.ra.value, coord.dec.value
    # deal with all exceptions here
    except Exception as e:
        # log that there was an error with astroquery
        wargs = [object_name, type(e), str(e)]
        WLOG(params, 'warning', TextEntry('10-016-00020', args=wargs))
        # return unset ra/dec
        return None, None



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
