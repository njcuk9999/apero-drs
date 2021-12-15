#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2021-12-09

@author: cook
"""
import pandas as pd
from astroquery.simbad import Simbad
from astropy.table import Row
import getpass
import gspread_pandas as gspd
import os
import socket
from typing import Dict, List, Optional
import warnings

from apero import lang
from apero.base import base
from apero.core import constants
from apero.core.core import drs_log
from apero.core.core import drs_database
from apero.core.core import drs_text
from apero.core.utils import drs_startup
from apero.science import preprocessing as prep
from apero.tools.module.database import manage_databases
from apero.tools.module.setup import drs_installation

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_astrometrics.py'
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
# get the databases
IndexDatabase = drs_database.IndexDatabase
ObjectDatabase = drs_database.ObjectDatabase
# simbad additional columns
SIMBAD_COLUMNS = ['ids', 'pmra', 'pmdec', 'pm_bibcode', 'plx',
                  'plx_bibcode', 'rvz_radvel', 'rvz_bibcode',
                  'sp', 'sp_bibcode', 'coo(d)', 'coo_bibcode', 'flux(J)',
                  'flux(H)', 'flux(K)']
# define relative path to google token files
PARAM1 = ('241559402076-vbo2eu8sl64ehur7'
          'n1qhqb0q9pfb5hei.apps.googleusercontent.com')
PARAM2 = ('apero-data-manag-'
          '1602517149890')
PARAM3 = ''.join(base.GSPARAM)
PARAM4 = ('1//0dBWyhNqcGHgdCgYIARAAGA0SNwF-L9IrhXoPCjWJtD4f0EDxA'
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


# =============================================================================
# Move to module
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

    def from_table_row(self, table_row: Row):
        """
        Populate attributes from astropy table row

        :param table_row: astropy.table.row.Row

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
        # TODO: Question: Is this a good assumption from SIMBAD?
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
        nargs = [Time.now().iso, getpass.getuser(), socket.gethostname(),
                 __NAME__]
        note = ' Added on {0} by {1}@{2} using {3}'
        self.notes += note.format(*nargs)

    def to_dataframe(self) -> pd.DataFrame:

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
        print('\tRA:   {0:20s} DEC:  {1}'.format(str(self.ra), str(self.dec)))
        # add pmra and pmde
        print('\tPMRA: {0:20s} PMDE: {1}'.format(str(self.pmra) + ' mas/yr', str(self.pmde) + ' mas/yr'))
        # add parallax and proper motion
        print('\tPLX:  {0:20s} RV:   {1}'.format(str(self.plx) + ' mas', str(self.rv) + ' km/s'))
        # add spectral type
        print('\tSPT:  {0:20s}'.format(str(self.sp_type)))
        # add magnitudes
        for mag in self.mags:
            print('\t{0}mag: {1}'.format(mag, self.mags[mag]))
        print(' ' + '=' * 50 + '\n')


def query_simbad(params: ParamDict, rawobjname: str) -> List[AstroObj]:
    # ---------------------------------------------------------------------
    # get results
    with warnings.catch_warnings(record=True) as _:
        # reset the votable fields (in case they have been added previously)
        Simbad.reset_votable_fields()
        # add ids column
        for simbad_column in SIMBAD_COLUMNS:
            Simbad.add_votable_fields(simbad_column)
        Simbad.remove_votable_fields('coordinates')
        # query simbad
        table = Simbad.query_object(rawobjname)
    # storage for astrometric objects
    astroobjs = []
    # deal with not having object
    if (table is None) or (len(table) == 0):
        msg = ('Object "{0}" not found in simbad. '
               'Please add it manually if requred for PRV')
        WLOG(params, '', msg.format(rawobjname), colour='red')
        return astroobjs
    # loop around rows in table and add to astro obj list
    for row in range(len(table)):
        # construct instance of AstroObj
        astroobj = AstroObj(rawobjname)
        # push in information from this row
        astroobj.from_table_row(table[row])
        # append to storage
        astroobjs.append(astroobj)
    # return the list of astrometric objects
    return astroobjs


def query_database(params, rawobjnames: List[str]) -> List[str]:
    """
    Find all objects in the object database and return list of unfound
    objects

    :param params:
    :param rawobjnames:
    :return:
    """
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
        # clean the object
        objname = pconst.DRS_OBJ_NAME(rawobjname)
        # find correct name in the database (via objname or aliases)
        correct_objname, found = objdbm.find_objname(pconst, objname)
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
        file1.write(TEXT1.format(PARAM1, PARAM2, PARAM3))
    with open(path2, 'w') as file2:
        file2.write(TEXT2.format(PARAM4, PARAM1, PARAM3))


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
    SHEET_ID = params['OBJ_LIST_GOOGLE_SHEET_URL']
    SHEET_NAME = 'pending_list'
    # load google sheet instance
    google_sheet = gspd.spread.Spread(SHEET_ID)
    # convert google sheet to pandas dataframe
    dataframe = google_sheet.sheet_to_df(index=0, sheet=SHEET_NAME)
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


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
# Everything else is controlled from recipe_definition
def main(**kwargs):
    """
    Main function for apero_reset.py

    :param instrument: str, the instrument name
    :param kwargs: additional keyword arguments

    :type instrument: str

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(**kwargs)
    # ----------------------------------------------------------------------
    # deal with command line inputs / function call inputs
    recipe, params = drs_startup.setup(__NAME__, __INSTRUMENT__, fkwargs)
    # solid debug mode option
    if kwargs.get('DEBUG0000', False):
        return recipe, params
    # ----------------------------------------------------------------------
    # run main bulk of code (catching all errors)
    llmain, success = drs_startup.run(__main__, recipe, params)
    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    return drs_startup.end_main(params, llmain, recipe, success, outputs='None')


def __main__(recipe, params):
    """
    Main code: should only call recipe and params (defined from main)

    :param recipe:
    :param params:
    :return:
    """
    # ----------------------------------------------------------------------
    # Main Code
    # ----------------------------------------------------------------------
    rawobjs = ['Gl699', 'Trappist1', 'Trappist-1', 'WASP107', 'M1']

    # ----------------------------------------------------------------------
    # step 1: Is object in database?
    # ----------------------------------------------------------------------
    # query local object database
    unfound_objs = query_database(params, rawobjs)
    # stop here if all objects found
    if len(unfound_objs) == 0:
        msg = 'All objects found in database'
        WLOG(params, 'info', msg)
        return drs_startup.return_locals(params, locals())

    # ----------------------------------------------------------------------
    # step 2: Can we find object automatically from simbad?
    # ----------------------------------------------------------------------
    # store astrometric objects that we need to add to database
    add_objs = []
    # loop around unfound objects
    for objname in unfound_objs:
        # construct add object question
        question1 = '\n\nAdd OBJECT="{0}" to astrometric database?'.format(objname)
        # ask if we want to find object
        cond = drs_installation.ask(question1, dtype='YN')
        print()
        # if not skip
        if not cond:
            continue
        # search in simbad for objects
        astro_objs = query_simbad(params, rawobjname=objname)
        # deal with 1 object
        if len(astro_objs) == 1:
            # get first object
            astro_obj = astro_objs[0]
            # display the properties for this object
            astro_obj.display_properties()
            # construct the object correction question
            question2 = 'Does the data for this object look correct?'
            cond = drs_installation.ask(question2, dtype='YN')
            print()
            # if correct add to add list
            if cond:
                msg = 'Adding {0} to object list'.format(astro_obj.name)
                WLOG(params, '', msg)
                # append to add list
                add_objs.append(astro_obj)
            # else print that we are not adding object to database
            else:
                WLOG(params, '', 'Not adding object to database')

    # add to google sheet
    if len(add_objs) > 0:
        # add all objects in add list to google-sheet
        add_obj_to_sheet(params, add_objs)
        # log progress
        WLOG(params, '', textentry('40-503-00039'))
        # update database
        manage_databases.update_object_database(params, log=False)

    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return drs_startup.return_locals(params, locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()

# =============================================================================
# End of code
# =============================================================================
