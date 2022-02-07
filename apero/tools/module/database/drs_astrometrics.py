#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2021-12-15

@author: cook
"""
import numpy as np
import pandas as pd
from astroquery.simbad import Simbad
from astropy.table import Row
import getpass
import gspread_pandas as gspd
import os
import socket
import sys
import time
from typing import Dict, List, Optional, Tuple
import warnings

from apero import lang
from apero.base import base
from apero.core import constants
from apero.core.core import drs_base_classes
from apero.core.core import drs_log
from apero.core.core import drs_database
from apero.core.core import drs_text
from apero.core.utils import drs_startup
from apero.io import drs_fits
from apero.science import preprocessing as prep
from apero.tools.module.database import manage_databases
from apero.tools.module.setup import drs_installation


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'drs_astrometrics.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get time instance
Time = base.Time
# get text entry instance
textentry = lang.textentry
# get the parmeter dictionary instance
ParamDict = constants.ParamDict
# Get Logging function
WLOG = drs_log.wlog
# Get function string
display_func = drs_log.display_func
# get the databases
IndexDatabase = drs_database.IndexDatabase
ObjectDatabase = drs_database.ObjectDatabase
# simbad additional columns
SIMBAD_COLUMNS = ['ids', 'pmra', 'pmdec', 'pm_bibcode', 'plx',
                  'plx_bibcode', 'rvz_radvel', 'rvz_bibcode',
                  'sp', 'sp_bibcode', 'coo(d)',
                  'coo_bibcode', 'flux(J)', 'flux(H)', 'flux(K)']
# define sheet name
GSHEET_NAME = 'pending_list'
# define relative path to google token files
PARAM1 = ('241559402076-vbo2eu8sl64ehur7'
          'n1qhqb0q9pfb5hei.apps.googleusercontent.com')
PARAM2 = ('apero-data-manag-', '1602517149890')
PARAM3 = ''.join(base.GSPARAM)
PARAM4 = ('1//0dBWyhNqcGHgdCgYIARAAGA0SNwF-L9IrhXoPCjWJtD4f0EDxA',
          'gFX75Q-f5TOfO1VQNFgSFQ_89IW7trN3B4I0UYvvbVfrGRXZZg')
PATH1 = 'gspread_pandas/google_secret.json'
PATH2 = 'gspread_pandas/creds/default'
TEXT1 = ('{{"installed":{{"client_id":"{0}","project_id":"{1}","auth_uri":'
         '"https://accounts.google.com/o/oauth2/auth","token_uri":'
         '"https://oauth2.googleapis.com/token","auth_provider_x509_cert'
         '_url":"https://www.googleapis.com/oauth2/v1/certs","client_'
         'secret":"{2}","redirect_uris":["urn:ietf:wg:oauth:2.0:oob",'
         '"http://localhost"]}}}}')
TEXT2 = ('{{"refresh_token": "{0}", "token_uri": "https://oauth2.googleap'
         'is.com/token", "client_id": "{1}", "client_secret": "{2}", '
         '"scopes": ["openid", "https://www.googleapis.com/auth/drive", '
         '"https://www.googleapis.com/auth/userinfo.email", '
         '"https://www.googleapis.com/auth/spreadsheets"]}}')
# treat these as null values
NULL_TEXT = ['None', '--', 'None', '']


# =============================================================================
# Define functions
# =============================================================================
class AstroObj:
    objname: str = None
    original_name: str = None
    aliases: str = None
    ra: float = None
    ra_source: str = None
    dec: float = None
    dec_source: str = None
    epoch: float = None
    pmra: float = None
    pmra_source: str = None
    pmde: float = None
    pmde_source: str = None
    plx: Optional[float] = None
    plx_source: str = ''
    rv: Optional[float] = None
    rv_source: str = ''
    sp_type: Optional[str] = ''
    sp_source: str = ''
    teff: Optional[float] = None
    teff_source: str = ''
    mags: Dict[str, float] = dict()
    notes: str = ''

    def __init__(self, name: str):
        """
        Set up the name of the object

        :param name: str, the name of the object
        """
        self.name = name

    def __str__(self) -> str:
        return 'AstroObj[{0}]'.format(self.name)

    def __repr__(self) -> str:
        return self.__str__()

    def from_table_row(self, table_row: Row, update: bool = False):
        """
        Populate attributes from astropy table row

        :param table_row: astropy.table.row.Row
        :param update: bool, whether we are running new or updating all rows

        :return: None populates attributes
        """
        pconst = constants.pload()
        # set objname as cleaned version of name
        self.objname = pconst.DRS_OBJ_NAME(self.name)
        # store the original name
        self.original_name = self.name
        # get the aliases from table row
        self.aliases = table_row['IDS']
        # get the ra and source from table row
        self.ra = table_row['RA_d']
        self.ra_source = table_row['COO_BIBCODE']
        # get the dec and source from table row
        self.dec = table_row['DEC_d']
        self.dec_source = table_row['COO_BIBCODE']
        # assume the epoch is J2000.0
        # Question: Is this a good assumption from SIMBAD?
        self.epoch = 2451545.0
        # set the pmra and source from table row
        self.pmra = table_row['PMRA']
        self.pmra_source = table_row['PM_BIBCODE']
        # set the pmdec and source from table row
        self.pmde = table_row['PMDEC']
        self.pmde_source = table_row['PM_BIBCODE']
        # set the parallax and source from table row
        self.plx = table_row['PLX_VALUE']
        self.plx_source = table_row['PLX_BIBCODE']
        # set the radial velocity and source from table row
        self.rv = table_row['RVZ_RADVEL']
        self.rv_source = table_row['RVZ_BIBCODE']
        # set the spectral type from table row
        self.sp_type = table_row['SP_TYPE']
        self.sp_source = table_row['SP_BIBCODE']
        # no temperature information
        self.teff = None
        self.teff_source = ''
        # add magnitudes
        self.mags['J'] = table_row['FLUX_J']
        self.mags['H'] = table_row['FLUX_H']
        self.mags['K'] = table_row['FLUX_K']
        # deal with notes
        if not update:
            nargs = [Time.now().iso, getpass.getuser(), socket.gethostname(),
                     __NAME__]
            note = ' Added on {0} by {1}@{2} using {3}'
            self.notes += note.format(*nargs)

    def to_dataframe(self) -> pd.DataFrame:
        """
        Push table into dataframe
        :return:
        """
        dataframe = pd.DataFrame()
        dataframe['OBJNAME'] = [self.objname]
        dataframe['ORIGINAL_NAME'] = [self.original_name]
        dataframe['ALIASES'] = [self.aliases]
        dataframe['RA_DEG'] = [self.ra]
        dataframe['RA_SOURCE'] = [self.ra_source]
        dataframe['DEC_DEG'] = [self.dec]
        dataframe['DEC_SOURCE'] = [self.dec_source]
        dataframe['EPOCH'] = [self.epoch]
        dataframe['PMRA'] = [self.pmra]
        dataframe['PMRA_SOURCE'] = [self.pmra_source]
        dataframe['PMDE'] = [self.pmde]
        dataframe['PMDE_SOURCE'] = [self.pmde_source]
        # deal with no parallax
        if drs_text.null_text(self.plx, ['None', 'Null', '']):
            dataframe['PLX'] = ['']
            dataframe['PLX_SOURCE'] = ['']
        else:
            dataframe['PLX'] = [self.plx]
            dataframe['PLX_SOURCE'] = [self.plx_source]
        # deal with no rv
        if drs_text.null_text(self.rv, ['None', 'Null', '']):
            dataframe['RV'] = ['']
            dataframe['RV_SOURCE'] = ['']
        else:
            dataframe['RV'] = [self.rv]
            dataframe['RV_SOURCE'] = [self.rv_source]
        # deal with no teff
        if drs_text.null_text(self.teff, ['None', 'Null', '']):
            dataframe['TEFF'] = ['']
            dataframe['TEFF_SOURCE'] = ['']
        else:
            dataframe['TEFF'] = [self.teff]
            dataframe['TEFF_SOURCE'] = [self.teff_source]
        # deal with no spt
        if drs_text.null_text(self.sp_type, ['None', 'Null', '']):
            dataframe['SP_TYPE'] = ['']
            dataframe['SP_SOURCE'] = ['']
        else:
            dataframe['SP_TYPE'] = [self.sp_type]
            dataframe['SP_SOURCE'] = [self.sp_source]
        # add to the notes and used column
        dataframe['NOTES'] = self.notes
        dataframe['USED'] = 1
        # return the populated dataframe
        return dataframe

    def display_properties(self):
        """
        Display the astrometric object in a human readible way

        :return:
        """
        # print title
        print(' \n' + '=' * 50)
        print('\t{0}     [{1}]'.format(self.objname, self.original_name))
        print(' ' + '=' * 50)
        # loop around aliases
        aliases = self.aliases.split('|')
        print('\tAliases:')
        for alias in aliases:
            print('\t\t - {0}'.format(alias))
        print('\n')
        # add RA and Dec
        ra_args = [str(self.ra), self.ra_source]
        print('\tRA:    {0:30s} ({1})'.format(*ra_args))
        dec_args = [str(self.dec), self.dec_source]
        print('\tDEC:   {0:30s} ({1})'.format(*dec_args))
        # add pmra and pmde
        pmra_args = [str(self.pmra) + ' mas/yr', self.pmra_source]
        print('\tPMRA:  {0:30s} ({1})'.format(*pmra_args))
        pmde_args = [str(self.pmde) + ' mas/yr', self.pmde_source]
        print('\tPMDE:  {0:30s} ({1})'.format(*pmde_args))
        # add parallax and proper motion
        plx_args = [str(self.plx) + ' mas', self.plx_source]
        print('\tPLX:   {0:30s} ({1})'.format(*plx_args))
        rv_args = [str(self.rv) + ' km/s', self.rv_source]
        print('\tRV:    {0:30s} ({1})'.format(*rv_args))
        # add spectral type
        sp_args = [self.sp_type, self.sp_source]
        print('\tSPT:   {0:30s} ({1})'.format(*sp_args))
        # add epoch
        dyear = Time(self.epoch, format='jd').decimalyear
        print('\tEPOCH: {0}'.format(str(dyear)))
        # add magnitudes
        for mag in self.mags:
            print('\t{0}mag: {1}'.format(mag, self.mags[mag]))
        print(' ' + '=' * 50 + '\n')

    def consistent_astrometrics(self, params: ParamDict) -> Tuple[bool, str]:
        """
        Assuming we have some ids we can update the ra/dec/pmra/pmde/plx
        most importantly these astrometrics should be at the same observation
        time (epoch)

        :return:
        """
        # set function name
        func_name = display_func('consistent_astrometrics', __NAME__,
                                 'AstroObj')
        # get pconst (we need it for tap urls
        pconst = constants.pload()
        # get the tap dictionaries
        pm_tap_dict = pconst.PM_TAP_DICT(params)
        # ---------------------------------------------------------------------
        # storage for the catalogue to use
        cats = []
        pm_ids = []
        # find whether this object is in any of the proper motion catalogues
        for pm_cat in list(pm_tap_dict.keys()):
            for alias in self.aliases.split('|'):
                if alias.upper().startswith(pm_cat.upper()):
                    pm_ids.append(str(alias[len(pm_cat):]))
                    cats.append(pm_cat)
        # ---------------------------------------------------------------------
        # deal with not finding object
        if len(cats) == 0:
            wmsg = 'Cannot find an alias in PM catalog. Skipping'
            WLOG(params, 'warning', wmsg)
            return False, wmsg
        # ---------------------------------------------------------------------
        # check for astroquery and return
        try:
            from astroquery.utils.tap.core import TapPlus
        except Exception as e:
            eargs = [type(e), str(e), func_name]
            WLOG(params, 'warning', textentry('10-016-00009', args=eargs))
            return False, str(textentry('10-016-00009', args=eargs))
        # ---------------------------------------------------------------------
        # set up reason
        reason = ''
        # loop around all catalogues found
        for c_it, cat in enumerate(cats):
            # get url for this catalog
            url = pm_tap_dict[cat]['URL']
            # make the query -- the only argument should be an ID string
            query = pm_tap_dict[cat]['QUERY'].format(pm_ids[c_it])
            # ---------------------------------------------------------------------
            # try running proper motion query
            try:
                with warnings.catch_warnings(record=True) as _:
                    with drs_base_classes.HiddenPrints():
                        # construct gaia TapPlus instance
                        catalog = TapPlus(url=url)
                        # launch gaia job
                        job = catalog.launch_job(query=query)
                        # get gaia table
                        qtable = job.get_results()
                        # wait 1 second to avoid spamming servers
                        time.sleep(1)
            except Exception as e:
                wargs = [url, query, type(e), e, func_name]
                WLOG(params, 'warning', textentry('10-016-00008', args=wargs))
                # return No row and True to fail
                reason = str(textentry('10-016-00008', args=wargs))
                continue
            # ---------------------------------------------------------------------
            # deal with no pmde/pmra/plx
            cond1 = drs_text.null_text(str(qtable['pmra'][0]), NULL_TEXT)
            cond2 = drs_text.null_text(str(qtable['pmde'][0]), NULL_TEXT)
            cond3 = drs_text.null_text(str(qtable['plx'][0]), NULL_TEXT)
            # ---------------------------------------------------------------------
            if cond1 or cond2:
                reason = 'No pm value from {0}'.format(cat)
                continue
            # ---------------------------------------------------------------------
            # finally if this is successful we need to update some parameters
            self.ra = qtable['ra'][0]
            self.ra_source = cat.strip()
            self.dec = qtable['dec'][0]
            self.dec_source = cat.strip()
            self.epoch = Time(qtable['epoch'][0], format='decimalyear').jd
            self.pmra = qtable['pmra'][0]
            self.pmra_source = cat.strip()
            self.pmde = qtable['pmde'][0]
            self.pmde_source = cat.strip()
            # deal with parallax
            if cond3:
                self.plx = 0
                self.plx_source = ''
            else:
                self.plx = qtable['plx'][0]
                self.plx_source = cat.strip()
            # print that object astrometrics updated by pm catalogue
            msg = '\tObject = {0} astrometrics updated using {1}'
            WLOG(params, '', msg.format(self.objname, cat.strip()),
                 colour='magenta')
            # if we get to here we have updated and don't need to continue the
            # loop
            return True, ''
        # ---------------------------------------------------------------------
        # return False and the reason
        return False, reason

    def combine_aliases(self, params: ParamDict, old_aliases: List[str]):
        """
        Combine two sets of aliases and print out those added from new / old

        :param params: ParamDict, parameter dictionary of constants
        :param old_aliases: list of strings, the original (old) list of aliases

        :return:
        """
        # get the new aliases as a list
        new_aliases = self.aliases.split('|')
        # storage for updated aliases
        update_aliases = list(np.unique(new_aliases))
        # make sure old aliases are unique
        old_aliases = list(np.unique(old_aliases))
        # add new aliases
        new_new_aliases = []
        for alias in new_aliases:
            if alias not in old_aliases:
                new_new_aliases.append(alias)
        # log new new aliases
        msg = '\tAdding new-list aliases: {0}'.format(','.join(new_new_aliases))
        WLOG(params, '', msg)
        # add old aliases not in new aliases
        old_new_aliases = []
        for alias in old_aliases:
            if alias not in new_aliases and alias not in update_aliases:
                old_new_aliases.append(alias)
                update_aliases.append(alias)
        # log old new aliases
        msg = '\tAdding old-list aliases: {0}'.format(','.join(old_new_aliases))
        WLOG(params, '', msg)
        # update aliases in class
        self.aliases = '|'.join(update_aliases)

    def check_teff(self, params: ParamDict,
                   indexdbm: drs_database.IndexDatabase):

        # get teff header key
        teff_hkey = params['KW_OBJ_TEMP'][0]
        # ---------------------------------------------------------------------
        # load database if required
        if indexdbm.database is None:
            indexdbm.load_db()
        # ---------------------------------------------------------------------
        # get all possible object names
        objnames = [self.objname, self.original_name]  + self.aliases.split('|')
        # check for objname in raw files only
        mcondition = 'BLOCK_KIND="raw"'
        # add obj conditions
        subcondition = []
        for objname in objnames:
            subcondition.append(f'KW_OBJECTNAME="{objname}"')
        # add master condition + obj conditions
        condition = mcondition + ' AND ({0})'.format(' OR '.join(subcondition))
        # ---------------------------------------------------------------------
        # get paths from database
        otable = indexdbm.get_entries('ABSPATH, OBS_DIR', condition=condition)
        # get the absolute path column
        paths = np.array(otable['ABSPATH'])
        obs_dirs = np.array(otable['OBS_DIR'])
        # ---------------------------------------------------------------------
        # deal with no paths
        if len(paths) == 0:
            msg = 'No files found for {0}. Cannot allocate Teff from header'
            WLOG(params, '', msg.format(self.objname))
            return
        # ---------------------------------------------------------------------
        # get Teffs from headers of files (not in the database) - one per
        #   obs_dir (no need to repeat for each file)
        teffs = []
        used_obs_dirs = []
        # loop around all paths
        for o_it, filename in enumerate(paths):
            # skip obs_dirs already present
            if obs_dirs[o_it] in used_obs_dirs:
                continue
            # get the header
            objhdr = drs_fits.read_header(params, filename)
            # only add teff if key present
            if teff_hkey in objhdr:
                # add the teff
                teffs.append(objhdr[teff_hkey])
                # add obs dir to used obs dirs
                used_obs_dirs.append(obs_dirs[o_it])
        # ---------------------------------------------------------------------
        # find unique teff values
        uteffs = np.unique(teffs)
        # if we only have one great we use it
        if len(uteffs) == 1:
            self.teff = uteffs[0]
            self.teff_source = 'Header'
        else:
            # work out median teff value
            medteff = np.median(uteffs)
            # Choose a teff from the headers
            question = 'Multiple Teffs found. Choose from the following:'
            # construct the question (with options)
            count, options, values = 0, [], []
            for count in uteffs:
                question += '\n\t{0}:   {1} K'.format(count + 1, uteffs[count])
                options.append(count + 1)
                values.append(uteffs[count])
            # Add the median value as an option
            question += '\n\t {0} [Median]:    {1} K'.format(count + 1, medteff)
            options.append(count + 1)
            values.append(medteff)
            # ask user the question
            uinput = drs_installation.ask(question, dtype=int, options=options)
            # set Teff value
            self.teff = values[uinput]
            # deal with user chosing median
            if uinput == options[-1]:
                self.teff_source = 'Header [Multi:Median]'
            else:
                self.teff_source = 'Header [Multi:user]'
        # ---------------------------------------------------------------------
        # log teff update
        msg = 'Teff updated from files on disk. \n\tTeff = {0}\n\tSource = {1}'
        margs = [self.teff, self.teff_source]
        WLOG(params, 'info', msg.format(*margs))



def query_simbad(params: ParamDict, rawobjname: str,
                 report: bool = True, update: bool = False
                 ) -> Tuple[List[AstroObj], str]:
    # ---------------------------------------------------------------------
    # get results
    with warnings.catch_warnings(record=True) as _:
        # reset the votable fields (in case they have been added previously)
        Simbad.reset_votable_fields()
        # add ids column
        for simbad_column in SIMBAD_COLUMNS:
            Simbad.add_votable_fields(simbad_column)
        Simbad.remove_votable_fields('coordinates')
        # query simbad - try a few times
        attempts, error = 0, ''
        while attempts < 10:
            try:
                table = Simbad.query_object(rawobjname)
                break
            except Exception as e:
                msg = 'Error in Simbad.query_object. Trying again {0}/{1}'
                WLOG(params, 'warning', msg.format(attempts + 1, 10))
                # error message
                error = str(e)
                # wait 5 seconds
                time.sleep(1)
                # add to attempts
                attempts += 1
    # deal with max attempts
    if attempts == 10:
        emsg = 'Cannot run simbad query objects. \n\t Error {0}'
        WLOG(params, 'error', emsg.format(error))
    # storage for astrometric objects
    astroobjs = []
    # deal with not having object
    if (table is None) or (len(table) == 0):
        msg = ('Object "{0}" not found in simbad. '
               'Please add it manually if requred for PRV')
        if report:
            WLOG(params, '', msg.format(rawobjname), colour='red')
        return astroobjs, msg.format(rawobjname)
    # set up reason
    reason = ''
    # loop around rows in table and add to astro obj list
    for row in range(len(table)):
        # construct instance of AstroObj
        astroobj = AstroObj(rawobjname)
        # push in information from this row
        astroobj.from_table_row(table[row], update=update)
        # try to get consistent ra/dec/pmra/pmde/plx (i.e. at same epoch)
        updated, reason = astroobj.consistent_astrometrics(params)
        # append to storage
        if updated:
            astroobjs.append(astroobj)
    # return the list of astrometric objects
    return astroobjs, reason


def query_database(params, rawobjnames: List[str],
                   overwrite: bool = False) -> List[str]:
    """
    Find all objects in the object database and return list of unfound
    objects

    :param params: ParamDict, the parameter dictionary of constants
    :param rawobjnames: list of strings, the list of raw (uncleaned) object
                        names
    :param overwrite: bool, if True does not check whether object already
                      exists in database

    :return: list of strings, the raw (uncleaned) objects names we want to
             process
    """

    # deal with overwrite
    if overwrite:
        return rawobjnames
    # ---------------------------------------------------------------------
    # get psuedo constants
    pconst = constants.pload()
    # ---------------------------------------------------------------------
    # Update the object database (recommended only for full reprocessing)
    # check that we have entries in the object database
    manage_databases.object_db_populated(params)
    # log progress
    WLOG(params, '', textentry('40-503-00039'))
    # update database
    manage_databases.update_object_database(params, log=False)
    # ---------------------------------------------------------------------
    # print progress
    WLOG(params, '', 'Searching local object database for object names...')
    # load the object database after updating
    objdbm = ObjectDatabase(params)
    objdbm.load_db()
    # storage for output - assume none are found
    unfound = []
    # get the object rejection list
    reject_list = prep.get_obj_reject_list(params)
    # loop around objects and find them in database
    for rawobjname in rawobjnames:
        # find correct name in the database (via objname or aliases)
        correct_objname, found = objdbm.find_objname(pconst, rawobjname)
        # deal with found / not found
        if found:
            msg = '\t - Object: "{0}" found in database as "{1}"'
            margs = [rawobjname, correct_objname]
            WLOG(params, '', msg.format(*margs))
        elif correct_objname in reject_list:
            msg = '\t - Object: "{0}" in reject list database as "{1}"'
            msg += ('\n\t\t - remove manually from reject list if '
                    'required for PRV')
            margs = [rawobjname, correct_objname]
            WLOG(params, '', msg.format(*margs), colour='magenta')
        else:
            msg = '\t - Object: "{0}" not found in database'
            margs = [rawobjname]
            WLOG(params, '', msg.format(*margs), colour='yellow')
            # add to unfound list
            unfound.append(rawobjname)
    # return the entry names and the found dictionary
    return unfound


def gsp_setup():
    # make sure token is in correct directory
    outpath = os.path.join(os.path.expanduser('~'), '.config/')
    # make sure .config exists
    if not os.path.exists(outpath):
        os.makedirs(outpath)
    # construct paths
    path1 = os.path.join(outpath, PATH1)
    path2 = os.path.join(outpath, PATH2)
    # make sure paths exist
    if not os.path.exists(os.path.dirname(path1)):
        os.makedirs(os.path.dirname(path1))
    if not os.path.exists(os.path.dirname(path2)):
        os.makedirs(os.path.dirname(path2))
    # make file
    with open(path1, 'w') as file1:
        file1.write(TEXT1.format(PARAM1, ''.join(PARAM2), PARAM3))
    with open(path2, 'w') as file2:
        file2.write(TEXT2.format(''.join(PARAM4), PARAM1, PARAM3))


def add_obj_to_sheet(params: ParamDict, astro_objs: List[AstroObj]):
    """
    Add all listed astrometrics objects to the sheet

    :param params:
    :param astro_objs:
    :return:
    """
    # add gspread directory and auth files
    gsp_setup()
    # define the sheet id and sheet name (pending)
    sheet_id = params['OBJ_LIST_GOOGLE_SHEET_URL']
    # load google sheet instance
    google_sheet = gspd.spread.Spread(sheet_id)
    # convert google sheet to pandas dataframe
    dataframe = google_sheet.sheet_to_df(index=0, sheet=GSHEET_NAME)
    # add the astro_obj
    for astro_obj in astro_objs:
        # print progress
        msg = 'Adding OBJECT={0} to dataframe'
        margs = [astro_obj.objname]
        WLOG(params, '', msg.format(*margs))
        # add to dataframe
        dataframe = dataframe.append(astro_obj.to_dataframe())
    # -------------------------------------------------------------------------
    # add a few empty rows
    empty_dataframe = pd.DataFrame()
    # loop around columns
    for col in dataframe.columns:
        # fill empty
        empty_dataframe[col] = [''] * 10
    # append empty rows to dataframe
    dataframe = dataframe.append(empty_dataframe)
    # -------------------------------------------------------------------------
    # print progress
    msg = 'Pushing all objects to google-sheet'
    WLOG(params, '', msg)
    # push dataframe back to server
    google_sheet.df_to_sheet(dataframe, index=False, replace=True)
    # print progress
    msg = 'All objects added to google-sheet'
    WLOG(params, '', msg)


def update_astrometrics(params):
    # get pconst
    pconst = constants.pload()
    # load table
    table = manage_databases.get_object_database(params)
    # store astrometric objects that we need to add to database
    add_objs = []
    removed_objs = []
    possible_mismatched_objects = []
    # loop around unfound objects
    for row in range(len(table)):
        # get object name for simbad search
        objname = str(table[row]['ORIGINAL_NAME'])
        # update
        margs = [objname, row+1, len(table)]
        msg = 'Processing original name = {0}  ({1}/{2})'.format(*margs)
        WLOG(params, 'info', params['DRS_HEADER'])
        WLOG(params, 'info', msg)
        WLOG(params, 'info', params['DRS_HEADER'])
        # ---------------------------------------------------------------------
        astro_objs, alias = [], str(objname)
        # search in simbad for objects (loop around aliases)
        for alias in table[row]['ALIASES'].split('|'):
            astro_objs, reason = query_simbad(params, rawobjname=alias,
                                              report=False)
            if len(astro_objs) > 0:
                break
        # ---------------------------------------------------------------------
        WLOG(params, '', '\tUsing objname={0}'.format(alias), colour='magenta')
        # ---------------------------------------------------------------------
        # deal with bad object
        if len(astro_objs) == 0:
            WLOG(params, 'warning', 'Cannot process {0}'.format(objname))
            removed_objs.append(objname)
            continue
        else:
            astro_obj = astro_objs[0]
        # ---------------------------------------------------------------------
        # update original name to alias
        astro_obj.original_name = str(alias)
        # check if object names are basically the same (cleaned + no underscore)
        if not very_similar_obj_names(pconst, objname, alias):
            msg = 'Not using original name = "{0}". "{1}" may be incorrect. '
            astro_obj.notes += msg.format(objname, alias)
            WLOG(params, 'warning', msg.format(objname, alias))
            possible_mismatched_objects.append(msg.format(objname, alias))
        # ---------------------------------------------------------------------
        # add notes from original table
        if not drs_text.null_text(str(table[row]['NOTES']), NULL_TEXT):
            # add a space between notes
            if len(astro_obj.notes) != 0:
                astro_obj.notes += ' '
            elif astro_obj.notes[-1] == ' ':
                astro_obj.notes += table[row]['NOTES']
            else:
                # add old note
                astro_obj.notes += ' ' + table[row]['NOTES']
        # ---------------------------------------------------------------------
        # set PLX from table if not present
        if drs_text.null_text(str(astro_obj.plx), NULL_TEXT):
            astro_obj.plx = table[row]['PLX']
            astro_obj.plx_source = table[row]['PLX_SOURCE']
        # set RV from table if not present
        if drs_text.null_text(str(astro_obj.rv), NULL_TEXT):
            astro_obj.rv = table[row]['RV']
            astro_obj.rv_source = table[row]['RV_SOURCE']
        # set SpT from table if not present
        if drs_text.null_text(str(astro_obj.sp_type), NULL_TEXT):
            astro_obj.sp_type = table[row]['SP_TYPE']
            astro_obj.sp_source = table[row]['SP_SOURCE']
        # set Teff from table if not present
        if drs_text.null_text(str(astro_obj.teff), NULL_TEXT):
            astro_obj.teff = table[row]['TEFF']
            astro_obj.teff_source = table[row]['TEFF_SOURCE']
        # ---------------------------------------------------------------------
        # keep OBJNAME from original table
        astro_obj.name = str(table[row]['OBJNAME'])
        astro_obj.objname = str(table[row]['OBJNAME'])
        # deal with combining aliases
        orignal_names = [table[row]['OBJNAME'], table[row]['ORIGINAL_NAME']]
        old_aliases = table[row]['ALIASES'].split('|') + orignal_names
        astro_obj.combine_aliases(params, old_aliases)
        # -------------------------------------------------------------
        # now add object to database
        msg = '\tAdding {0} to object list'.format(astro_obj.name)
        WLOG(params, '', msg)
        # append to add list
        add_objs.append(astro_obj)
    # -------------------------------------------------------------------------
    # add to google sheet
    if len(add_objs) > 0:
        WLOG(params, '', params['DRS_HEADER'], colour='magenta')
        msg = 'Adding {0} objects to the object database'
        WLOG(params, '', msg.format(len(add_objs)), colour='magenta')
        WLOG(params, '', params['DRS_HEADER'], colour='magenta')
        # add all objects in add list to google-sheet
        add_obj_to_sheet(params, add_objs)
        # log progress
        WLOG(params, '', textentry('40-503-00039'))
        # update database
        manage_databases.update_object_database(params, log=False)
    # -------------------------------------------------------------------------
    WLOG(params, '', params['DRS_HEADER'], colour='yellow')
    msg = 'There were {0} possible mismatched objects'
    margs = [len(possible_mismatched_objects)]
    WLOG(params, '', msg.format(*margs), colour='yellow')
    WLOG(params, '', params['DRS_HEADER'], colour='yellow')
    # print possible mismatched objects
    for mismatch in possible_mismatched_objects:
        WLOG(params, '', mismatch, colour='yellow')
    # -------------------------------------------------------------------------
    WLOG(params, '', params['DRS_HEADER'], colour='red')
    msg = 'There were {0} objects remove from the database'
    WLOG(params, '', msg.format(len(removed_objs)), colour='red')
    WLOG(params, '', params['DRS_HEADER'], colour='red')
    # print object removed (not found)
    for robjname in removed_objs:
        msg = 'Could not find "{0}". Removed from database'
        WLOG(params, '', msg.format(robjname), colour='red')
    # -------------------------------------------------------------------------
    # log finishing of code
    iargs = ['update_astrometrics']
    WLOG(params, 'info', params['DRS_HEADER'])
    WLOG(params, 'info', textentry('40-003-00001', args=iargs))
    WLOG(params, 'info', params['DRS_HEADER'])


def update_teffs(params):
    # get pconst
    pconst = constants.pload()
    # load table
    table = manage_databases.get_object_database(params)
    # filter rows without teff
    mask = np.array(table['TEFF'].mask).astype(bool)
    table = table[mask]



def very_similar_obj_names(pconst, objname1: str, objname2: str) -> bool:
    """
    Check if two objects are the same just with underscores differing them
    (after the usual cleaning of object names - all caps + no punctuation or
     white space)
    """
    # clean and remove underscores (just for comparison)
    cobjname1 = pconst.DRS_OBJ_NAME(objname1).replace('_', '')
    cobjname2 = pconst.DRS_OBJ_NAME(objname2).replace('_', '')
    # if they are the same return True
    if cobjname1 == cobjname2:
        return True
    else:
        return False


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # TODO: should this be a dev recipe?
    args = sys.argv
    # get params
    _params = constants.load()
    # assign a PID
    _params['PID'], _ = drs_startup.assign_pid()
    # set shortname
    _params['RECIPE'] = __NAME__
    _params['RECIPE_SHORT'] = str('ASTRO-UP')
    # deal with a coordinates update
    if '--update_coords' in args:
        update_astrometrics(_params)
    # deal with teff update
    elif '--update_teffs' in args:
        update_teffs(_params)


# =============================================================================
# End of code
# =============================================================================
