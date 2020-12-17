#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-12-12 at 09:45

@author: cook
"""
from astropy import units as uu
from astropy.coordinates import SkyCoord, Distance
from astropy.table import Table
import numpy as np
import pandas as pd
import requests
from typing import List, Tuple, Union
import warnings

from apero.base import base
from apero.core.core import drs_text
from apero.core import constants
from apero.core import math as mp
from apero.core.core import drs_database
from apero import lang
from apero.core.core import drs_log
from apero.io import drs_fits

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'preprocessing.general.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get time
Time = base.Time
# Get Logging function
WLOG = drs_log.wlog
# Get function string
display_func = drs_log.display_func
# Get the text types
textentry = lang.textentry
# Get database
ObjectDatabase = drs_database.ObjectDatabase
# get param dict
ParamDict = constants.ParamDict
# SQL queries
QUERY_GAIA = 'SELECT {0} FROM {1} WHERE {2}'
QCOLS = ('ra as ra, dec as dec, source_id as gaiaid, parallax as plx, '
         'pmdec as pmde, pmra as pmra, radial_velocity as rv, '
         'phot_g_mean_mag as gmag, phot_bp_mean_mag as bpmag, '
         'phot_rp_mean_mag as rpmag')
QSOURCE = 'gaiadr2.gaia_source'
QCIRCLE = ('(1=CONTAINS(POINT(\'ICRS\', ra, dec), CIRCLE(\'ICRS\', {ra}, '
           '{dec}, {radius})))')

# cache for google sheet
GOOGLE_TABLES = dict()
# define standard google base url
GOOGLE_BASE_URL = ('https://docs.google.com/spreadsheets/d/{}/gviz/'
                   'tq?tqx=out:csv&sheet={}')
# unit aliases
masyr = uu.mas / uu.yr
# gaia col name in google sheet
GL_GAIA_COL_NAME = 'GAIADR2ID'
# object col name in google sheet
GL_OBJ_COL_NAME = 'OBJECT'
# alias col name in google sheet
GL_ALIAS_COL_NAME = 'ALIASES'
# rv col name in google sheet
GL_RV_COL_NAME = 'RV'
GL_RVREF_COL_NAME = 'RV_REF'
# teff col name in google sheet
GL_TEFF_COL_NAME = 'TEFF'
GL_TEFFREF_COL_NAME = 'TEFF_REF'
# Reject like google columns
GL_R_ODO_COL = 'ODOMETER'
GL_R_PP_COL = 'PP'
GL_R_RV_COL = 'RV'


# =============================================================================
# Define object resolution functions
# =============================================================================
class AstroObject(object):
    aliases: List[str]
    used: int

    def __init__(self, params: ParamDict, pconst, gaia_id: Union[str, None],
                 ra: Union[str, float], dec: Union[str, float],
                 database, objname: Union[str, None], pmra: float = np.nan,
                 pmde: float = np.nan, plx: float = np.nan,
                 rv: float = np.nan, teff: float = np.nan):
        """
        Construct an astrophysical object instance

        :param gaia_id: str or None, input gaia id - if None require ra and dec
        :param ra: float, right ascension, only required if gaia_id is None
        :param dec: float, declination, only required if gaia_id is None
        :param database:
        """
        # properties from input
        self.input_gaiaid = gaia_id
        self.input_ra = ra
        self.input_dec = dec
        self.database = database
        if objname is None:
            self.input_objname = None
        else:
            self.input_objname = pconst.DRS_OBJ_NAME(objname)
        self.input_pmra = pmra
        self.input_pmde = pmde
        self.input_plx = plx
        self.input_rv = rv
        self.input_teff = teff
        # other information
        self.params = params
        self.pconst = pconst
        self.gaia_url = params['OBJ_LIST_GAIA_URL']
        self.gaia_epoch = params['OBJ_LIST_GAIA_EPOCH']
        self.radius = params['OBJ_LIST_CROSS_MATCH_RADIUS']
        self.maglimit = params['OBJ_LIST_GAIA_MAG_CUT']
        self.plxlimit = params['OBJ_LIST_GAIA_PLX_LIM']
        self.gsheet_url = params['OBJ_LIST_GOOGLE_SHEET_URL']
        self.gsheet_wnum = params['OBJ_LIST_GOOGLE_SHEET_WNUM']
        self.resolve_from_database = params['OBJ_LIST_RESOLVE_FROM_DATABASE']
        self.resolve_from_gaia_id = params['OBJ_LIST_RESOLVE_FROM_GAIAID']
        self.resolve_from_glist = params['OBJ_LIST_RESOLVE_FROM_GLIST']
        self.resolve_from_coords = params['OBJ_LIST_RESOLVE_FROM_COORDS']
        # properties we need to find
        self.objname = None
        self.objname_source = 'None'
        self.gaia_id = None
        self.gaia_id_source = 'None'
        self.ra = np.nan
        self.ra_source = 'None'
        self.dec = np.nan
        self.dec_source = 'None'
        self.pmra = np.nan
        self.pmra_source = 'None'
        self.pmde = np.nan
        self.pmde_source = 'None'
        self.plx = np.nan
        self.plx_source = 'None'
        self.rv = np.nan
        self.rv_source = 'None'
        self.gmag = np.nan
        self.gmag_source = 'None'
        self.bpmag = np.nan
        self.bpmag_source = 'None'
        self.rpmag = np.nan
        self.rpmag_source = 'None'
        self.epoch = np.nan
        self.epoch_source = 'None'
        self.teff = np.nan
        self.teff_source = 'None'
        self.aliases = []
        self.aliases_source = 'None'
        self.used = 0
        # other properties
        self.update_database = True

    def __getstate__(self) -> dict:
        """
        For when we have to pickle the class
        :return:
        """
        # what to exclude from state
        exclude = ['database']
        # need a dictionary for pickle
        state = dict()
        for key, item in self.__dict__.items():
            if key not in exclude:
                state[key] = item
        # return dictionary state
        return state

    def __setstate__(self, state: dict):
        """
        For when we have to unpickle the class

        :param state: dictionary from pickle
        :return:
        """
        # update dict with state
        self.__dict__.update(state)
        # add in the database manually
        self.database = ObjectDatabase(self.params)
        self.database.load_db()

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        if self.input_objname is not None:
            return 'AstroObject[{0}]'.format(self.input_objname)
        elif self.input_gaiaid is not None:
            return 'AstroObject[Gaia DR2 {0}]'.format(self.input_gaiaid)
        else:
            return 'AstroObject[ra={0},dec={1}]'.format(self.input_ra,
                                                        self.input_dec)

    def resolve_target(self, mjd=None):
        # deal with database not loaded
        self.database.load_db()
        # ---------------------------------------------------------------------
        # 1. try gaia id and objname against database
        # ---------------------------------------------------------------------
        if self.resolve_from_database:
            self._resolve_from_database()
        # ---------------------------------------------------------------------
        # 2. try gaia id against gaia query (only if gaia_id is still None)
        # ---------------------------------------------------------------------
        if (self.gaia_id is None) and self.resolve_from_gaia_id:
            self._resolve_from_gaia_id()
        # ---------------------------------------------------------------------
        # 3. try to get gaia id from google sheet of gaia id (with object name)
        # ---------------------------------------------------------------------
        if (self.gaia_id is None) and self.resolve_from_glist:
            self._resolve_from_glist()
        # ---------------------------------------------------------------------
        # 4. use ra + dec to get gaia id (only if gaia_id is still None)
        # ---------------------------------------------------------------------
        if (self.gaia_id is None) and self.resolve_from_coords:
            if mjd is not None:
                self._resolve_from_coords(mjd)
        # ---------------------------------------------------------------------
        # Finally fill in any missing parameters from inputs/defaults
        # ---------------------------------------------------------------------
        self._use_inputs()

    def get_simbad_aliases(self):
        """
        Get simbad aliases

        :return:
        """
        # deal with aliases already set
        if len(self.aliases) > 0:
            return
        # storage aliases
        self.aliases = []
        # set aliases to objname and input objname if different
        if self.objname is not None:
            self.aliases += [self.objname]
        if self.input_objname is not None:
            if self.objname != self.input_objname:
                self.aliases += [self.input_objname]
        # only do this is we have a gaia-id
        if self.gaia_id is None:
            return
        obj_id = 'Gaia DR2 {0}'.format(self.gaia_id)
        # get entries for this gaia id
        entries = query_simbad_id(self.params, obj_id)
        # deal with no entries
        if entries is None:
            return
        if len(entries) == 0:
            return
        # get the aliases
        raw_aliases = entries['IDS'][0].decode('utf-8')
        # slit via the pipe (|)
        self.aliases += raw_aliases.split('|')
        self.aliases_source = 'SIMBAD'

    def _resolve_from_database(self):
        """
        Use gaia id (from input) to check if this object is already in database
        - if it is then update all parameters from here
        - if it isn't (or isn't set) check against known names in the database
        - if names aren't found and gaia id not found do not update parameters
        """
        # ---------------------------------------------------------------------
        # deal with no input_gaiaid
        if self.input_gaiaid is not None:
            # condition condition
            condition = '{0}="{1}"'.format('GAIADR2ID', self.input_gaiaid)
            # get the entries for this condition
            entries = self.database.get_entries('*', condition=condition)
            # set source
            source = 'database-gaia-id'
        else:
            entries = None
            source = 'None'
        # ---------------------------------------------------------------------
        # deal with no entries (try resolving from name in known aliases)
        if entries is None or len(entries) == 0:
            # resolve entries and get source
            entries, source = self._resolve_from_names()
        if entries is None or len(entries) == 0:
            return
        # ---------------------------------------------------------------------
        # fill out required information if available
        self.objname = str(entries['OBJNAME'].iloc[0])
        self.objname_source = 'database'
        self.gaia_id = str(entries['GAIADR2ID'].iloc[0])
        self.gaia_id_source = source
        self.ra = float(entries['RA_DEG'].iloc[0])
        self.ra_source = source
        self.dec = float(entries['DEC_DEG'].iloc[0])
        self.dec_source = source
        # assign pmra
        if not drs_text.null_text(entries['PMRA'].iloc[0], ['None']):
            self.pmra = float(entries['PMRA'].iloc[0])
            self.pmra_source = source
        # assign pmde
        if not drs_text.null_text(entries['PMDE'].iloc[0], ['None']):
            self.pmde = float(entries['PMDE'].iloc[0])
            self.pmde_source = source
        # assign pmde
        if not drs_text.null_text(entries['PLX'].iloc[0], ['None']):
            self.plx = float(entries['PLX'].iloc[0])
            self.plx_source = source
        # assign rv
        if not drs_text.null_text(entries['RV'].iloc[0], ['None']):
            self.rv = float(entries['RV'].iloc[0])
            self.rv_source = source
        # assign gmag
        if not drs_text.null_text(entries['GMAG'].iloc[0], ['None']):
            self.gmag = float(entries['GMAG'].iloc[0])
            self.gmag_source = source
        # assign bpmag
        if not drs_text.null_text(entries['BPMAG'].iloc[0], ['None']):
            self.bpmag = float(entries['BPMAG'].iloc[0])
            self.bpmag_source = source
        # assign rpmag
        if not drs_text.null_text(entries['RPMAG'].iloc[0], ['None']):
            self.rpmag = float(entries['RPMAG'].iloc[0])
            self.rpmag_source = source
        # assign epoch
        if not drs_text.null_text(entries['EPOCH'].iloc[0], ['None']):
            self.epoch = float(entries['EPOCH'].iloc[0])
            self.epoch_source = source
        # assign teff
        if not drs_text.null_text(entries['TEFF'].iloc[0], ['None']):
            self.teff = float(entries['TEFF'].iloc[0])
            self.teff_source = source
        # assign aliases
        if not drs_text.null_text(entries['ALIASES'].iloc[0], ['None']):
            self.aliases = str(entries['ALIASES'].iloc[0]).split('|')
            self.aliases_source = source
        # set used
        self.used = 1
        # we no not need to update database - if it was found in the database
        self.update_database = False

    def _resolve_from_names(self) -> Tuple[Union[pd.DataFrame, None], str]:
        """
        Search the database for a named column

        :return:
        """
        # deal with no object name (shouldn't be possible)
        if self.input_objname is None:
            return None, 'None'
        # get aliases from database
        cols = 'GAIADR2ID, OBJNAME, ALIASES'
        gaia_table = self.database.get_entries(cols)
        # extract required columns
        gaia_id = gaia_table['GAIADR2ID']
        objnames = gaia_table['OBJNAME']
        alias_sets = gaia_table['ALIASES']

        # ---------------------------------------------------------------------
        # 1. check direct object name
        # ---------------------------------------------------------------------
        for row, objname in enumerate(objnames):
            # get cleaned alias
            cobjname = self.pconst.DRS_OBJ_NAME(objname)
            # compare to input_objname
            if cobjname == self.input_objname:
                # condition condition
                condition = '{0}="{1}"'.format('GAIADR2ID', gaia_id[row])
                # set source
                source = 'database-objname'
                # return the entries for this gaia id
                entries = self.database.get_entries('*', condition=condition)
                return entries, source

        # ---------------------------------------------------------------------
        # 2. check aliases
        # ---------------------------------------------------------------------
        # loop around each set of aliases and see if
        for row, alias_set in enumerate(alias_sets):
            # split the names by a comma
            aliases = alias_set.split('|')
            # loop around aliases - if alias found return gaia id for this
            for alias in aliases:
                # ignore None
                if drs_text.null_text(alias, ['None']):
                    continue
                # get cleaned alias
                calias = self.pconst.DRS_OBJ_NAME(alias)
                # compare to input_objname
                if calias == self.input_objname:
                    # condition condition
                    condition = '{0}="{1}"'.format('GAIADR2ID', gaia_id[row])
                    # set source
                    source = 'database-aliases'
                    # return the entries for this gaia id
                    entries = self.database.get_entries('*',
                                                        condition=condition)
                    return entries, source
        # if we have reached this point we cannot match to name
        #   therefore return None
        return None, 'None'

    def _resolve_from_gaia_id(self):
        """
        Use input_gaiaid to query gaia and them update all parameters based
        on this id

        :return:
        """
        # deal with no input_gaiaid
        if self.input_gaiaid is None:
            return
        # set up ID query
        condition = 'source_id = {0}'.format(self.input_gaiaid)
        # construct sql query
        query = QUERY_GAIA.format(QCOLS, QSOURCE, condition)
        # return results
        entries = query_gaia(self.params, self.gaia_url, query)
        # deal with no entries
        if entries is None:
            return
        if len(entries) == 0:
            return
        # fill out required information if available
        self.objname = str(self.input_objname)
        self.objname_source = 'input'
        self.gaia_id = str(entries['gaiaid'][0])
        self.gaia_id_source = 'gaia-query-id-input'
        self.ra = float(entries['ra'][0])
        self.ra_source = 'gaia-query-id-input'
        self.dec = float(entries['dec'][0])
        self.dec_source = 'gaia-query-id-input'
        # assign pmra
        if not entries['pmra'].mask[0]:
            self.pmra = float(entries['pmra'][0])
            self.pmra_source = 'gaia-query-id-input'
        # assign pmde
        if not entries['pmde'].mask[0]:
            self.pmde = float(entries['pmde'][0])
            self.pmde_source = 'gaia-query-id-input'
        # assign plx
        if not entries['plx'].mask[0]:
            self.plx = float(entries['plx'][0])
            self.plx_source = 'gaia-query-id-input'
        # assign rv
        if not entries['rv'].mask[0]:
            self.rv = float(entries['rv'][0])
            self.rv_source = 'gaia-query-id-input'
        # assign gmag
        if not entries['gmag'].mask[0]:
            self.gmag = float(entries['gmag'][0])
            self.gmag_source = 'gaia-query-id-input'
        # assign bpmag
        if not entries['bpmag'].mask[0]:
            self.bpmag = float(entries['bpmag'][0])
            self.bpmag_source = 'gaia-query-id-input'
        # assign rpmag
        if not entries['rpmag'].mask[0]:
            self.rpmag = float(entries['rpmag'][0])
            self.rpmag_source = 'gaia-query-id-input'
        # assign epoch
        self.epoch = self.gaia_epoch
        self.epoch_source = 'gaia-query-id-input'
        # set used
        self.used = 1

    def _resolve_from_glist(self):
        """
        Resolve gaia id from google sheets (using object name) and then
        retry the gaia id against the gaia database

        :return:
        """
        # try to get gaia id from google sheets
        gtable = query_glist(self.input_objname, self.gsheet_url,
                             self.gsheet_wnum)
        # set some properties from gtable
        if gtable is not None:
            self.input_gaiaid = gtable[GL_GAIA_COL_NAME]
        #  try (again) gaia id against gaia query (only if gaia_id is still
        #  None)
        if self.input_gaiaid is not None:
            self._resolve_from_gaia_id()
            self.gaia_id_source = 'gaia-query-id-gsheet'

        # overwrite RV and Teff (if set in gtable)
        if gtable is not None:
            # set aliases
            if not is_null(gtable[GL_ALIAS_COL_NAME]):
                self.aliases = gtable[GL_ALIAS_COL_NAME].split('|')
            # add RV if not None
            if not is_null(gtable[GL_RV_COL_NAME]):
                self.rv = gtable[GL_RV_COL_NAME]
                self.rv_source = gtable[GL_RVREF_COL_NAME]
            # add Teff if not None
            if not is_null(gtable[GL_TEFF_COL_NAME]):
                self.teff = gtable[GL_TEFF_COL_NAME]
                self.teff_source = gtable[GL_TEFFREF_COL_NAME]

    def _resolve_from_coords(self, mjd=None):
        """
        Resolve from Gaia using coordinates (and the current date)

        :param mjd: observation modified julien date

        :return:
        """
        # deal with ra and dec (want it in degrees)
        ra, dec = parse_coords(self.input_ra, self.input_dec)
        # get radius in degrees
        radius = (self.radius * uu.arcsec).to(uu.deg).value
        # set up ra / dec crossmatch
        condition = QCIRCLE.format(ra=ra, dec=dec, radius=radius)
        # add additional criteria (to narrow search)
        condition += r' AND (phot_rp_mean_mag < {0})'.format(self.maglimit)
        # add a parallax condition
        condition += r' AND (parallax > {0})'.format(self.plxlimit)
        # construct sql query
        query = QUERY_GAIA.format(QCOLS, QSOURCE, condition)
        # return results of query
        entries = query_gaia(self.params, self.gaia_url, query)
        # deal with no entries
        if entries is None:
            return
        if len(entries) == 0:
            return
        # get closest to ra and dec (propagated)
        position = best_gaia_entry(ra, dec, mjd, entries, self.gaia_epoch)
        # fill out required information if available
        self.objname = str(self.input_objname)
        self.objname_source = 'input'
        self.gaia_id = str(entries['gaiaid'][position])
        self.gaia_id_source = 'gaia-query-coords'
        self.ra = float(entries['ra'][position])
        self.ra_source = 'gaia-query-coords'
        self.dec = float(entries['dec'][position])
        self.dec_source = 'gaia-query-coords'
        # assign pmra
        if not entries['pmra'].mask[position]:
            self.pmra = float(entries['pmra'][position])
            self.pmra_source = 'gaia-query-coords'
        # assign pmde
        if not entries['pmde'].mask[position]:
            self.pmde = float(entries['pmde'][position])
            self.pmde_source = 'gaia-query-coords'
        # assign plx
        if not entries['plx'].mask[position]:
            self.plx = float(entries['plx'][position])
            self.plx_source = 'gaia-query-coords'
        # assign rv
        if not entries['rv'].mask[position]:
            self.rv = float(entries['rv'][position])
            self.rv_source = 'gaia-query-coords'
        # assign gmag
        if not entries['gmag'].mask[position]:
            self.gmag = float(entries['gmag'][position])
            self.gmag_source = 'gaia-query-coords'
        # assign bpmag
        if not entries['bpmag'].mask[position]:
            self.bpmag = float(entries['bpmag'][position])
            self.bpmag_source = 'gaia-query-coords'
        # assign rpmag
        if not entries['rpmag'].mask[position]:
            self.rpmag = float(entries['rpmag'][position])
            self.rpmag_source = 'gaia-query-coords'
        # assign epoch
        self.epoch = self.gaia_epoch
        self.epoch_source = 'gaia-query-coords'
        # set used
        self.used = 1

    def _use_inputs(self):
        """
        If all else fails use the input values

        :return:
        """
        # fill out required information if available
        # - Gaia ID
        if is_null(self.gaia_id):
            self.gaia_id = None
            self.gaia_id_source = 'None'
        # - object name
        if is_null(self.objname):
            self.objname = self.input_objname
            self.objname_source = 'input'
        # - right ascension
        if is_null(self.ra):
            self.ra = self.input_ra
            self.ra_source = 'input'
        # - declination
        if is_null(self.dec):
            self.dec = self.input_dec
            self.dec_source = 'input'
        # - proper motion (right ascension)
        if is_null(self.pmra):
            self.pmra = self.input_pmra
            self.pmra_source = 'input'
        # - proper motion (declination)
        if is_null(self.pmde):
            self.pmde = self.input_pmde
            self.pmde_source = 'input'
        # - parallax
        if is_null(self.plx):
            self.plx = self.input_plx
            self.plx_source = 'input'
        # - radial velocity
        if is_null(self.rv):
            self.rv = self.input_rv
            self.rv_source = 'input'
        # - Gaia G magnitude
        if is_null(self.gmag):
            self.gmag = np.nan
            self.gmag_source = 'None'
        # - Gaia BP magnitude
        if is_null(self.bpmag):
            self.bpmag = np.nan
            self.bpmag_source = 'None'
        # - Gaia RP magniude
        if is_null(self.rpmag):
            self.rpmag = np.nan
            self.rpmag_source = 'None'
        # - Epoch of observation
        if is_null(self.epoch):
            self.epoch = np.nan
            self.epoch_source = 'None'
        # - Effective temperature
        if is_null(self.teff):
            self.teff = self.input_teff
            self.teff_source = 'input'
        # aliases
        if is_null(self.aliases) or len(self.aliases) == 0:
            self.aliases = []
            self.aliases_source = 'None'
        # set used
        self.used = 1

    def write_obj(self, database: ObjectDatabase, commit: bool = True):
        # do not update if we found via database
        if not self.update_database:
            return
        # write to database
        database.add_entry(objname=self.objname, objname_s=self.objname_source,
                           gaia_id=self.gaia_id, gaia_id_s=self.gaia_id_source,
                           ra=self.ra, ra_s=self.ra_source,
                           dec=self.dec, dec_s=self.dec_source,
                           pmra=self.pmra, pmra_s=self.pmra_source,
                           pmde=self.pmde, pmde_s=self.pmde_source,
                           plx=self.plx, plx_s=self.plx_source,
                           rv=self.rv, rv_s=self.rv_source,
                           gmag=self.gmag, gmag_s=self.gmag_source,
                           bpmag=self.bpmag, bpmag_s=self.bpmag_source,
                           rpmag=self.rpmag, rpmag_s=self.rpmag_source,
                           epoch=self.epoch, epoch_s=self.epoch_source,
                           teff=self.teff, teff_s=self.teff_source,
                           aliases=self.aliases, aliases_s=self.aliases_source,
                           commit=commit)

    def write_table(self, outdict: dict):
        """
        Proxy write function (used to write to dictionary --> Table)
        Only for debugging!

        :param outdict:
        :return:
        """
        columns = ['OBJNAME', 'OBJNAME_SOURCE', GL_GAIA_COL_NAME,
                   'GAIAID_SOURCE',
                   'RA_DEG', 'RA_SOURCE', 'DEC_DEG', 'DEC_SOURCE', 'PMRA',
                   'PMRA_SOURCE', 'PMDE', 'PMDE_SOURCE', 'PLX', 'PLX_SOURCE',
                   'RV', 'RV_SOURCE', 'GMAG', 'GMAG_SOURCE', 'BPMAG',
                   'BPMAG_SOURCE', 'RPMAG', 'RPMAG_SOURCE', 'EPOCH',
                   'EPOCH_SOURCE', 'TEFF', 'TEFF_SOURCE', 'ALIASES',
                   'ALIASES_SOURCE', 'USED']
        values = [self.objname, self.objname_source, self.gaia_id,
                  self.gaia_id_source, self.ra, self.ra_source, self.dec,
                  self.dec_source, self.pmra, self.pmra_source,
                  self.pmde, self.pmde_source, self.plx, self.plx_source,
                  self.rv, self.rv_source, self.gmag, self.gmag_source,
                  self.bpmag, self.bpmag_source, self.rpmag, self.rpmag_source,
                  self.epoch, self.epoch_source, self.teff, self.teff_source]
        # deal with aliases
        if isinstance(self.aliases, str):
            values.append(self.aliases)
            values.append(self.aliases_source)
        elif isinstance(self.aliases, list):
            values.append('|'.join(self.aliases))
            values.append(self.aliases_source)
        else:
            values.append('None')
            values.append(self.aliases_source)
        # add used
        values.append(self.used)
        # loop around and add to outdict
        for row in range(len(values)):
            if columns[row] in outdict:
                outdict[columns[row]].append(values[row])
            else:
                outdict[columns[row]] = [values[row]]
        # return outdict
        return outdict

    def update_header(self, params, header: drs_fits.Header) -> drs_fits.Header:
        """
        Update the header with these values

        :param header: drs_fits.Header - the fits header to update

        :return: drs_fits.Header - the updated header
        """
        # make sure header is a drs_fits.Header
        if not isinstance(header, drs_fits.Header):
            header = drs_fits.Header(header)
        # add object name and source
        header.set_key(params, 'KW_DRS_OBJNAME', value=self.objname)
        header.set_key(params, 'KW_DRS_OBJNAME_S', value=self.objname_source)
        # add gaia id and source
        header.set_key(params, 'KW_DRS_GAIAID', value=self.gaia_id)
        header.set_key(params, 'KW_DRS_GAIAID_S', value=self.gaia_id_source)
        # add the ra and source
        header.set_key(params, 'KW_DRS_RA', value=self.ra)
        header.set_key(params, 'KW_DRS_RA_S', value=self.ra_source)
        # add the dec and source
        header.set_key(params, 'KW_DRS_DEC', value=self.dec)
        header.set_key(params, 'KW_DRS_DEC_S', value=self.dec_source)
        # add the pmra
        header.set_key(params, 'KW_DRS_PMRA', value=self.pmra)
        header.set_key(params, 'KW_DRS_PMRA_S', value=self.pmra_source)
        # add the pmde
        header.set_key(params, 'KW_DRS_PMDE', value=self.pmde)
        header.set_key(params, 'KW_DRS_PMDE_S', value=self.pmde_source)
        # add the plx
        header.set_key(params, 'KW_DRS_PLX', value=self.plx)
        header.set_key(params, 'KW_DRS_PLX_S', value=self.plx_source)
        # add the rv
        header.set_key(params, 'KW_DRS_RV', value=self.rv)
        header.set_key(params, 'KW_DRS_RV_S', value=self.rv_source)
        # add the gmag
        header.set_key(params, 'KW_DRS_GMAG', value=self.gmag)
        header.set_key(params, 'KW_DRS_GMAG_S', value=self.gmag_source)
        # add the bpmag
        header.set_key(params, 'KW_DRS_BPMAG', value=self.bpmag)
        header.set_key(params, 'KW_DRS_BPMAG_S', value=self.bpmag_source)
        # add the rpmag
        header.set_key(params, 'KW_DRS_RPMAG', value=self.rpmag)
        header.set_key(params, 'KW_DRS_RPMAG_S', value=self.rpmag_source)
        # add the epoch
        header.set_key(params, 'KW_DRS_EPOCH', value=self.epoch)
        header.set_key(params, 'KW_DRS_EPOCH_S', value=self.epoch_source)
        # add the teff
        header.set_key(params, 'KW_DRS_TEFF', value=self.teff)
        header.set_key(params, 'KW_DRS_TEFF_S', value=self.teff_source)
        # return updated header
        return header


def resolve_target(params: ParamDict, pconst,
                   objname: Union[str, None] = None,
                   database: Union[ObjectDatabase, None] = None,
                   header: Union[drs_fits.Header, None] = None,
                   commit: bool = True) -> Union[drs_fits.Header, None]:
    """
    Resolve a list of object names via gaia ids (from GoogleSheet/Gaia/Simbad
    crossmatch)

    :param params: parameter dictionary of constants
    :param pconst: psuedo constants from this instrument
    :param objname: str, the object names to resolve - if you have the header
                    use header instead of objname (overrides objname any way)
    :param database: ObjectDatabase or None, object database instance so we
                     don't load more times than needed
    :param header: if objname is not set get parameters via fits header
                   (recommended over objname as fills in ra/dec/pmra/pmde for
                   targets that are not found)
    :param commit: bool, if True writes to database - else a database commit
                   is needed later

    :return: None - updates object database
    """
    # load database
    if database is None:
        database = ObjectDatabase(params)
        database.load_db()
    # deal with no objname and no header
    if objname is None and header is None:
        WLOG(params, 'error', 'Must define "objname" or "header"')
    # deal with parameters from header vs not from header
    if header is not None:
        # get objname
        objname = header[params['KW_OBJNAME'][0]]
        # set gaia id
        gaia_id = header.get(params['KW_GAIA_ID'][0], None)
        # set ra [in degrees]
        ra = header.get(params['KW_OBJRA'][0], np.nan)
        ra = (ra * params.instances['KW_OBJRA'].unit).to(uu.deg).value
        # set dec [in degrees]
        dec = header.get(params['KW_OBJDEC'][0], np.nan)
        dec = (dec * params.instances['KW_OBJDEC'].unit).to(uu.deg).value
        # set pmra [in mas/yr]
        pmra = header.get(params['KW_OBJRAPM'][0], np.nan)
        pmra = (pmra * params.instances['KW_OBJRAPM'].unit).to(masyr).value
        # set pmde [in mas/yr]
        pmde = header.get(params['KW_OBJDECPM'][0], np.nan)
        pmde = (pmde * params.instances['KW_OBJDECPM'].unit).to(masyr).value
        # set plx [in mas]
        plx = header.get(params['KW_PLX'][0], np.nan)
        plx = (plx * params.instances['KW_PLX'].unit).to(uu.mas).value
        # set rv [in km/s]
        rv = header.get(params['KW_INPUTRV'][0], np.nan)
        rv = (rv * params.instances['KW_INPUTRV'].unit).to(uu.km / uu.s).value
        # set teff [in K]
        teff = header.get(params['KW_OBJ_TEMP'][0], np.nan)
        teff = (teff * params.instances['KW_OBJ_TEMP'].unit).to(uu.K).value
        # set mjd
        mjd = header.get(params['KW_MID_OBS_TIME'][0], None)
    else:
        # set gaia id
        gaia_id = None
        # set ra and dec [in degrees]
        ra, dec = np.nan, np.nan
        # set pmra/pmde [in mas/yr]
        pmra, pmde = np.nan, np.nan
        # set plx, rv and teff [in mas, km/s, K]
        plx, rv, teff = np.nan, np.nan, np.nan
        # set mjd to None (cannot use coord match without ra/dec anyway)
        mjd = None
    # clean up object name
    cobjname = pconst.DRS_OBJ_NAME(objname)

    # Print that we are resolving object
    WLOG(params, 'info', 'Resolving OBJECT = {0}'.format(cobjname))
    # set up an astro object instance
    astro_obj = AstroObject(params, pconst, gaia_id, ra, dec,
                            database, cobjname, pmra, pmde, plx, rv, teff)
    # resolve target
    astro_obj.resolve_target(mjd=mjd)
    # get simbad aliases for this object
    astro_obj.get_simbad_aliases()
    # write to database
    astro_obj.write_obj(database, commit=commit)
    # update header
    if header is not None:
        return astro_obj.update_header(params, header)
    else:
        return None


def resolve_targets(params: ParamDict, objnames: Union[str, List[str]],
                    database: Union[ObjectDatabase, None] = None):
    """
    Resolve a list of object names via gaia ids (from GoogleSheet/Gaia/Simbad
    crossmatch)

    :param params: parameter dictionary of constants
    :param objnames: str or list of strings, the object names to resolve
    :param database: ObjectDatabase or None, object database instance so we
                     don't load more times than needed
    :return: None - updates object database
    """
    # deal with a single object name
    if isinstance(objnames, str):
        objnames = [objnames]
    # get pconst
    pconst = constants.pload(params['INSTRUMENT'])
    # load database
    if database is None:
        database = ObjectDatabase(params)
        database.load_db()
    # loop around objects
    for objname in objnames:
        resolve_target(params, pconst, objname, database, commit=False)
    # commit to database after writing all rows
    database.database.commit()


def query_gaia(params: ParamDict, url: str,
               query: str) -> Union[Table, None]:
    """
    Query Gaia via a TapPlus query

    :param params: ParamDict, parameter dictionary of constants
    :param url: str, the URL to the SQL database
    :param query: str, the SQL query to run

    :return: astropy.table.Table or None - the results of the gaia TAP query
    """
    # set fucntion name
    func_name = __NAME__ + '.query_gaia()'
    # check for astroquery and return a fail and warning if not installed
    try:
        from astroquery.utils.tap.core import TapPlus

    except Exception as e:
        eargs = [type(e), str(e), func_name]
        WLOG(params, 'warning', textentry('10-016-00009', args=eargs))
        return None
    # ------------------------------------------------------------------
    # try running gaia query
    try:
        with warnings.catch_warnings(record=True) as _:
            # create query string (for printing)
            str_query = format_sql_query(query, url, 'Gaia Tap Plus Query')
            # print query
            WLOG(params, '', str_query, wrap=False)
            # construct gaia TapPlus instance
            gaia = TapPlus(url=url)
            # launch gaia job
            job = gaia.launch_job(query=query)
            # get gaia table
            table = job.get_results()
    except Exception as e:
        wargs = [url, query, type(e), e, func_name]
        WLOG(params, 'warning', textentry('10-016-00008', args=wargs))
        # return No row and True to fail
        return None
    # ------------------------------------------------------------------
    # if we have no entries we did not find object
    if len(table) == 0:
        # return None
        return None
    # else we return result
    return table


def query_simbad_id(params: ParamDict, obj_id: str) -> Union[Table, None]:
    # set fucntion name
    _ = __NAME__ + '.query_simbad()'
    # check for astroquery and return a fail and warning if not installed
    try:
        # import astroquery
        from astroquery.simbad import Simbad
        # get results
        with warnings.catch_warnings(record=True) as _:
            # create query string (for printing)
            WLOG(params, '', 'SIMBAD QUERY: {0}'.format(obj_id))
            # add ids column
            Simbad.add_votable_fields('ids')
            # query simbad
            return Simbad.query_object(obj_id)
    # deal with all exceptions here
    except Exception as e:
        # log that there was an error with astroquery
        wargs = [obj_id, type(e), str(e)]
        WLOG(params, 'warning', textentry('10-016-00020', args=wargs))
        # return unset ra/dec
        return None


def query_glist(objname: str, sheet_id: str, worksheet: int = 0):
    # get the google sheet
    gtable = get_google_sheet(sheet_id, worksheet)

    # deal with empty table
    if gtable is None:
        return None
    if len(gtable) == 0:
        return None
    # set initial position to None
    position = None
    row = np.nan
    # loop around rows and look for aliases
    for row in range(len(gtable)):
        # set aliases as the objname
        aliases = [gtable[GL_OBJ_COL_NAME][row]]
        # get the aliases for this row
        aliases += gtable[GL_ALIAS_COL_NAME][row].split('|')
        # search for object name
        position = crossmatch_name(objname, aliases)
        # break if we have found a match
        if position is not None:
            break
    # if position is still None return None
    if position is None:
        return None
    # else we have our Gaia id so return it
    return gtable[row]


def get_google_sheet(sheet_id: str, worksheet: int = 0,
                     cached: bool = True) -> Table:
    """
    Load a google sheet from url using a sheet id (if cached = True and
    previous loaded - just loads from memory)

    :param sheet_id: str, the google sheet id
    :param worksheet: int, the worksheet id (defaults to 0)
    :param cached: bool, if True and previous loaded, loads from memory

    :return: Table, astropy table representation of google sheet
    """
    # set google cache table as global
    global GOOGLE_TABLES
    # construct url for worksheet
    url = GOOGLE_BASE_URL.format(sheet_id, worksheet)
    # deal with table existing
    if url in GOOGLE_TABLES and cached:
        return GOOGLE_TABLES[url]
    # get data using a request
    rawdata = requests.get(url)
    # convert rawdata input table
    table = Table.read(rawdata.text, format='ascii')
    # add to cached storage
    GOOGLE_TABLES[url] = table
    # return table
    return table


def crossmatch_name(name: str, namelist: List[str]) -> Union[int, None]:
    """
    Crossmatch a name with a list of names (returning position in the list of
    names)

    :param name: str, the name to search for
    :param namelist: list of strings, the list of names to search
    :return: int, the position of the name in the namelist (if found) else
             None
    """

    # clean name
    name = name.strip().upper()
    # strip namelist as char array
    namelist = np.char.array(namelist).strip().upper()
    # search for name in list
    if name in namelist:
        position = np.where(name == namelist)[0][0]
        # return position
        return position
    # if not found return None
    return None


def parse_coords(ra: float, dec: float, ra_unit='deg', dec_unit='deg'):
    """
    Convert coordinates into degrees via SkyCoord

    :param ra: right ascension (with units "ra_units")
    :param dec: declination (with units "dec_units"
    :param ra_unit: units for right ascension
    :param dec_unit: units for declination
    :return:
    """
    # get Sky Coord instances
    coord = SkyCoord(ra, dec, unit=[ra_unit, dec_unit])

    return coord.ra.value, coord.dec.value


def best_gaia_entry(ra: float, dec: float, mjd: float, entries: Table,
                    gaia_epoch: float):
    """
    Using the originally supplied ra and dec choose the closest
    entries (propagating all entries in time to match current ra and dec
    at time = 'mjd')

    :param ra: float, the right ascension in degrees
    :param dec: float, the declination in degrees
    :param mjd: float, the modified julien date for observation
    :param entries:
    :return:
    """
    # get the original coords in SkyCoord
    ocoord = SkyCoord(ra, dec, unit='deg')
    # get gaia time and observation time
    gaia_time = Time(str(gaia_epoch), format='decimalyear')
    obs_time = Time(mjd, format='mjd')
    # get entries as numpy arrays (with units)
    ra_arr = np.array(entries['ra']) * uu.deg
    dec_arr = np.array(entries['dec']) * uu.deg
    pmra_arr = np.array(entries['pmra']) * uu.mas / uu.yr
    pmde_arr = np.array(entries['pmde']) * uu.mas / uu.yr
    plx_arr = np.array(entries['plx']) * uu.mas
    # propagate all entries ra and dec to mjd
    coords0 = SkyCoord(ra_arr, dec_arr,
                       pm_ra_cosdec=pmra_arr, pm_dec=pmde_arr,
                       distance=Distance(parallax=plx_arr),
                       obstime=gaia_time)
    # apply space motion
    coords1 = coords0.apply_space_motion(obs_time)
    # crossmatch with ra and dec and keep closest
    separation = coords1.separation(ocoord)
    # find the position of the minimum separated value
    position = np.argmin(separation.value)
    # return the position
    return position


def is_null(value):
    # deal with values that can be masked
    if hasattr(value, 'mask'):
        if value.mask:
            return True
    # then deal with floats
    if isinstance(value, float):
        if np.isnan(value):
            return True
        else:
            return False
    # else push to a string and test for null strings
    else:
        return drs_text.null_text(str(value), ['None', ''])


def format_sql_query(query: str, url: Union[str, None] = None,
                     title: Union[str, None] = None) -> str:
    """
    Better format for printing SQL queries

    :param query: str, the query to print
    :param url: str (optional), add the url to the query printout

    :return: str, the newly formatted string
    """
    # copy query to another string
    str_query = str(query)
    # deal with url
    if url is not None:
        str_query = '\nURL\n\t{0}'.format(url) + str_query
    # deal with title
    if title is not None:
        str_query = title + '\n' + str_query
    # replace lines
    str_query = str_query.replace('SELECT', '\nSELECT\n\t')
    str_query = str_query.replace('FROM', '\nFROM\n\t')
    str_query = str_query.replace('WHERE', '\nWHERE\n\t')
    str_query = str_query.replace('AND', '\nAND\n\t')
    str_query = str_query.replace('OR', '\nOR\n\t')
    # return the newly formatted string
    return str_query


def get_reject_list(params: ParamDict,
                    column: str = GL_R_PP_COL) -> np.ndarray:
    """
    Query the googlesheet for rejectiong odometer codes and return
    an array of odometer codes to reject

    :param params: ParamDict, the parameter dictionary of constants
    :param column: str, the column to use for rejection (must be filled with
                   "TRUE"/"FALSE")

    :return: list of strings, the list of odometer codes for kind
    """
    # set function name
    func_name = display_func(params, 'get_reject_list', __NAME__)
    # get sheet id and worksheet number
    sheet_id = params['ODOCODE_REJECT_GSHEET_ID']
    workbook_id = params['ODOCODE_REJECT_GSHEET_NUM']
    # get reject table
    reject_table = get_google_sheet(sheet_id, workbook_id)
    # convert masks to boolean
    if GL_R_PP_COL in reject_table.colnames:
        reject_table[GL_R_PP_COL] = reject_table[GL_R_PP_COL] == 'TRUE'
    if GL_R_RV_COL in reject_table.colnames:
        reject_table[GL_R_RV_COL] = reject_table[GL_R_RV_COL] == 'TRUE'
    # deal with bad kind
    if column not in reject_table.colnames:
        # log error
        eargs = [column, func_name]
        WLOG(params, 'error', textentry('00-010-00008', args=eargs))
        # return empty array if error does not exit
        return np.array([])
    else:
        # get odocodes to be rejected
        odocodes = np.array(reject_table[GL_R_ODO_COL][reject_table[column]])
        # return rejection list
        return odocodes


# =============================================================================
# Define other functions
# =============================================================================
def quality_control(params, snr_hotpix, infile, rms_list, log=True):
    # set passed variable and fail message list
    fail_msg, qc_values, qc_names, qc_logic, qc_pass = [], [], [], [], []
    # ----------------------------------------------------------------------
    # print out SNR hotpix value
    WLOG(params, '', textentry('40-010-00006', args=[snr_hotpix]))
    # get snr_threshold
    snr_threshold = params['PP_CORRUPT_SNR_HOTPIX']
    # deal with printing corruption message
    if snr_hotpix < snr_threshold:
        # add failed message to fail message list
        fargs = [snr_hotpix, snr_threshold, infile.filename]
        fail_msg.append(textentry('40-010-00007', args=fargs))
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(snr_hotpix)
    qc_names.append('snr_hotpix')
    qc_logic.append('snr_hotpix < {0:.5e}'.format(snr_threshold))
    # ----------------------------------------------------------------------
    # get rms threshold
    rms_threshold = params['PP_CORRUPT_RMS_THRES']
    # check
    if mp.nanmax(rms_list) > rms_threshold:
        # add failed message to fail message list
        fargs = [mp.nanmax(rms_list), rms_threshold, infile.filename]
        fail_msg.append(textentry('40-010-00008', args=fargs))
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(mp.nanmax(rms_list))
    qc_names.append('max(rms_list)')
    qc_logic.append('max(rms_list) > {0:.4e}'.format(rms_threshold))
    # ----------------------------------------------------------------------
    # check required exposure time
    exptime_frac = params['PP_BAD_EXPTIME_FRACTION']
    # get required exposure time
    required_exptime = infile.get_hkey('KW_EXPREQ')
    # get exposure time
    actual_exptime = infile.get_hkey('KW_EXPTIME')
    # calculate minimum required exposure time
    min_req_exptime = required_exptime * exptime_frac
    # check if actual exptime is good
    if actual_exptime < min_req_exptime:
        # add failed message
        fargs = [actual_exptime, min_req_exptime]
        fail_msg.append(textentry('40-010-00017', args=fargs))
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(actual_exptime)
    qc_names.append('EXPTIME')
    qc_logic.append('EXPTIME < {0:.4e}'.format(min_req_exptime))
    # ----------------------------------------------------------------------
    # finally log the failed messages and set QC = 1 if we pass the
    # quality control QC = 0 if we fail quality control
    if np.sum(qc_pass) == len(qc_pass):
        if log:
            WLOG(params, 'info', textentry('40-005-10001'))
        passed = 1
    else:
        if log:
            for farg in fail_msg:
                WLOG(params, 'warning', textentry('40-005-10002') + farg)
        passed = 0
    # store in qc_params
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]
    # return qc_params and passed
    return qc_params, passed


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # debug test for AstroObject class
    _params = constants.load('SPIROU')
    _pconst = constants.pload('SPIROU')

    # load database
    _objdbm = ObjectDatabase(_params)
    _objdbm.load_db()

    # for now delete database
    _columns, _ctypes = _pconst.OBJECT_DB_COLUMNS()
    _objdbm.database.delete_table('OBJECT')
    _objdbm.database.add_table('OBJECT', _columns, _ctypes)
    _objdbm.load_db()
    _outdict = dict()

    # get a list of object names from glist
    _gtable = get_google_sheet(_params['OBJ_LIST_GOOGLE_SHEET_URL'],
                               _params['OBJ_LIST_GOOGLE_SHEET_WNUM'])
    _objnames = list(np.unique(_gtable[GL_OBJ_COL_NAME]))

    # resolve targets
    resolve_targets(_params, _objnames, database=_objdbm)

# =============================================================================
# End of code
# =============================================================================
