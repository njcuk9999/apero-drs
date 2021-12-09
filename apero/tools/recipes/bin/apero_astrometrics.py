#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2021-12-09

@author: cook
"""
from astroquery.utils.tap.core import TapPlus
from astroquery.simbad import Simbad
from astropy.table import Table, Row
import numpy as np
from typing import Dict, List, Optional, Tuple
import warnings

from apero import lang
from apero.base import base
from apero.core import constants
from apero.core.core import drs_log
from apero.core.core import drs_database
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

    def display_properties(self):

        # print title
        print(' \n' + '='*50)
        print('\t{0}     [{1}]'.format(self.objname, self.original_name))
        print(' ' + '='*50)
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
        print(' ' + '='*50 + '\n')


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






def query_database(params, rawobjnames: List[str] ) -> List[str]:
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
    # update the database if required
    if params['UPDATE_OBJ_DATABASE']:
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
    params.set('UPDATE_OBJ_DATABASE', False)
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
    for objname in unfound_objs:

        # construct question
        question1 = 'Add OBJECT="{0}" to astrometric database?'.format(objname)
        # ask if we want to find object
        cond = drs_installation.ask(question1, dtype='YN')
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

            # ask the question
            question2 = 'Does the data for this object look correct?'

            cond = drs_installation.ask(question2, dtype='YN')

            if cond:
                msg = 'Adding {0} to database'.format(astro_obj.name)
                WLOG(params, '', msg)
            else:
                WLOG(params, '', 'Not adding object to database')



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

