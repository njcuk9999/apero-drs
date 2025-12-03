#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2022-02-07

@author: cook
"""
import os
import shutil
import tarfile
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
from astropy.time import Time

from aperocore.base import base
from aperocore.constants import param_functions
from aperocore.constants import load_functions
from aperocore import drs_lang
from apero.core import drs_database
from aperocore.core import drs_log
from aperocore.core import drs_text
from apero.core import drs_file
from apero.utils import drs_recipe
from apero.instruments import select
from apero.base import base as apero_base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'drs_get.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = apero_base.__PACKAGE__
__version__ = apero_base.__version__
__authors__ = apero_base.__authors__
__date__ = apero_base.__date__
__release__ = apero_base.__release__
# Get Logging function
WLOG = drs_log.wlog
# get exceptions
AperoCodedException = drs_log.AperoCodedException
ParamDict = param_functions.ParamDict

DrsRecipe = drs_recipe.DrsRecipe
# Get the text types
textentry = drs_lang.textentry
# ALLOWED NULL COLUMNS
NULL_COLS = ['KW_RUN_ID', 'KW_PI_NAME']


# =============================================================================
# Define functions
# =============================================================================
def basic_filter(params: ParamDict, recipe: DrsRecipe, kw_objnames: List[str],
                 filters: Dict[str, List[str]], user_outdir: str,
                 do_copy: bool = True, do_symlink: bool = False,
                 tarfilename: Optional[str] = None,
                 since: Optional[Time] = None, latest: Optional[Time] = None,
                 timekey: str = 'observed', nosubdir: bool = False,
                 sizelimit: int = None
                 ) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    """
    The basic filter function - copies files into OBJNAME directories
    based on the

    :param params: ParamDict, the parameter dictionary of constants
    :param kw_objnames: list of strings, the object names to filter
    :param filters: dictionary of list of strings, each entry is a specific
                    filter from the index database
                    i.e.
                    filters['KW_DPRTYPE'] = ['OBJ_FP', 'OBJ_DARK']
    :param user_outdir: str, the output directory
    :param do_copy: bool, if True copies files (else just prints)
    :param do_symlink: bool, if True creates symlink instead of copying files
    :param tarfilename: str, if not None make a tar file instead of copying files/
                    creating symlinks

    :param since: str, if not None only copy files since this date
    :param latest: str, if not None only copy up to this date
    :param timekey: str, the time key to use (observed or processed)
    :param nosubdir: bool, if True does not create subdirectories for each
                     object name
    :param sizelimit: int, if not None only copy files up to this size limit
                      in GB

    :return: Tuple, 1. dict, for each objname a list of input file locations
                    2. dict, for each objname a list of output file locations
    """
    # -------------------------------------------------------------------------
    # get pconst
    pconst = load_functions.load_pconfig(select.INSTRUMENTS)
    # get whether to filter by passing qc
    filter_qc = not params['INPUTS']['failedqc']
    # get the yamls for permissions
    perm_yaml = params['INPUTS'].get('PERMISSION_YAML', None)
    group_yaml = params['INPUTS'].get('GROUP_YAML', None)
    group_server = params['INPUTS'].get('GROUP_SERVER', None)
    if perm_yaml in ['None', 'Null', '']:
        perm_yaml = None
    if group_yaml in ['None', 'Null', '']:
        group_yaml = None
    if group_server in ['None', 'Null', '']:
        group_server = None
    # -------------------------------------------------------------------------
    # load "get" database
    WLOG(params, '', textentry('40-509-00001', args='file index'))
    findexdb = drs_database.FileIndexDatabase(params, recipe.shortname)
    findexdb.load_db()
    # load object database
    WLOG(params, '', textentry('40-509-00001', args='astrometric'))
    objdbm = drs_database.AstrometricDatabase(params, recipe.shortname)
    objdbm.load_db()
    # load log database
    WLOG(params, '', textentry('40-509-00001', args='log'))
    logdbm = drs_database.LogDatabase(params, recipe.shortname)
    logdbm.load_db()
    # -------------------------------------------------------------------------
    # deal with tar file name
    if tarfilename is not None:
        tarpath = os.path.join(user_outdir, tarfilename)
    else:
        tarpath = None
    # -------------------------------------------------------------------------
    # create reference condition
    master_condition = ''
    # loop around filters
    for _filter in filters:
        subconditions = []
        # get filter items
        filter_items = filters[_filter]
        # skip Nones
        if drs_text.null_text(filter_items, ['None', '', 'Null']):
            continue
        # loop around object names
        for item in filter_items:
            # skip Nones
            if drs_text.null_text(item, ['None', '', 'Null']):
                continue
            # add to sub conditions
            subcondition = '({0}="{1}")'.format(_filter, item)
            subconditions.append(subcondition)
        # deal with no valid sub-conditions
        if len(subconditions) == 0:
            continue
        # deal with null columns
        if _filter in NULL_COLS:
            subconditions.append('({0} IS NULL)'.format(_filter))
        # add to condition
        if len(master_condition) == 0:
            master_condition += '({0})'.format(' OR '.join(subconditions))
        else:
            master_condition += ' AND ({0})'.format(' OR '.join(subconditions))
    # -------------------------------------------------------------------------
    # deal with time key and going from iso to mjd
    if timekey == 'processed':
        time_col = 'KW_DRS_DATE_NOW'
        if since is not None:
            since = f'\'{since.iso}\''
        if latest is not None:
            latest = f'\'{latest.iso}\''
    else:
        time_col = 'KW_MJDATE'
        if since is not None:
            since = since.mjd
        if latest is not None:
            latest = latest.mjd
    # -------------------------------------------------------------------------
    if since is not None:
        subcondition = '({0} > {1})'.format(time_col, since)
        if len(master_condition) == 0:
            master_condition = subcondition
        else:
            master_condition += f' AND {subcondition}'
    # -------------------------------------------------------------------------
    if latest is not None:
        subcondition = '({0} <= {1})'.format(time_col, latest)
        if len(master_condition) == 0:
            master_condition = subcondition
        else:
            master_condition += f' AND {subcondition}'
    # -------------------------------------------------------------------------
    # deal with no objnames
    if kw_objnames is None:
        kw_objnames = ['None']
    # -------------------------------------------------------------------------
    # separate list for each object name
    # -------------------------------------------------------------------------
    # storage of inpaths and run ids
    db_entries = dict(OBJNAME=dict(), RUN_ID=dict())
    # loop around input object names
    for kw_objname in kw_objnames:
        # clean object name (as best we can)
        clean_obj_name, _ = objdbm.find_objname(pconst, kw_objname)
        WLOG(params, '', textentry('40-509-00002', args=[clean_obj_name]))
        # write condition for this object
        if drs_text.null_text(kw_objname, ['None', '', 'Null']):
            obj_condition = None
        else:
            # add the object name condition
            obj_condition = '(KW_OBJNAME="{0}")'.format(clean_obj_name)
        # deal with having an object condition
        condition = ''
        if obj_condition is not None:
            condition += str(obj_condition)
        # deal with having a reference condition
        if len(master_condition) > 0:
            # deal with not having an object condition (don't need the AND)
            if obj_condition is None:
                condition += str(master_condition)
            # deal with having an object condition (need an AND)
            else:
                condition += ' AND {0}'.format(master_condition)
        # deal with no condition still (set condition to None)
        if len(condition) == 0:
            condition = None
        # get the entries from the database
        icols = 'BLOCK_KIND, OBS_DIR, FILENAME, KW_PID, KW_RUN_ID'
        itable = findexdb.get_entries(icols, condition=condition)
        # get absolute paths
        inpaths = drs_file.DrsPath.get_abs_paths(params,
                                                 block_kinds=itable['BLOCK_KIND'],
                                                 obs_dirs=itable['OBS_DIR'],
                                                 basenames=itable['FILENAME'])
        inpaths = np.array(inpaths)
        # get APERO process ids
        ipids = np.array(itable['KW_PID'])
        # get run ids from raw files
        run_ids = np.array(itable['KW_RUN_ID'])
        # ---------------------------------------------------------------------
        # need to filter by pid in log database
        # ---------------------------------------------------------------------
        if filter_qc:
            # get all pids where passed_all_qc is PASSED_ALL_QC is True
            ltable = logdbm.get_entries('PID, PASSED_ALL_QC')
            # find all pids that are not zero (nulls, nans and 1s)
            lmask = ~(ltable['PASSED_ALL_QC'] == 0)
            # get a unique list of pids that do not fail QC
            lpids = list(set(ltable[lmask]['PID']))
            # mask out any files that fail qc
            mask = np.in1d(ipids, lpids)
        else:
            mask = np.ones(len(inpaths), dtype=bool)
        # ---------------------------------------------------------------------
        # load into file storage
        if len(inpaths[mask]) > 0:
            WLOG(params, '', textentry('40-509-00003', args=[len(inpaths)]))
            # keep files
            db_entries['OBJNAME'][clean_obj_name] = inpaths[mask]
            db_entries['RUN_ID'][clean_obj_name] = run_ids[mask]
        else:
            WLOG(params, '', textentry('40-509-00004'))
        # write that we excluded some files
        if filter_qc:
            WLOG(params, '', textentry('40-509-00005', args=[np.sum(~mask)]))
    # -------------------------------------------------------------------------
    # Now get outpaths (if infile exists)
    # -------------------------------------------------------------------------
    all_inpaths, all_outpaths = manage_outputs(params, db_entries,
                                               nosubdir, user_outdir, tarpath,
                                               do_copy, do_symlink, sizelimit,
                                               perm_yaml, group_yaml,
                                               group_server)

    return all_inpaths, all_outpaths



def manage_outputs(params: ParamDict, db_entries,
                   nosubdir: bool, user_outdir: str, tarpath: str = None,
                   do_copy: bool = True, do_symlink: bool = False,
                   sizelimit: int = None, perm_yaml: str = None,
                   group_yaml: str = None, group_server: str = None):
    """
    Manage the outputs from apero get
    """
    # storage of inpaths/outpaths
    if perm_yaml is not None and group_yaml is not None:
        gsout = get_perm_outpaths(params, nosubdir, db_entries,
                                  user_outdir, do_copy, perm_yaml, group_yaml,
                                  group_server)
    else:

        gsout = get_standard_outpaths(params, nosubdir, db_entries,
                                      user_outdir, do_copy)
    all_inpaths, all_outpaths, all_permissions = gsout
    # -------------------------------------------------------------------------
    # deal with file limit
    # -------------------------------------------------------------------------
    # first deal with checking total size of files
    if sizelimit is not None:
        check_size_limit(params, all_inpaths, sizelimit)
    # -------------------------------------------------------------------------
    # tar files
    # -------------------------------------------------------------------------
    # deal with tar
    if tarpath is not None and do_copy:
        # count files added
        nfiles = 0
        # add to tar file
        with tarfile.open(tarpath, 'w:gz') as tarfile_obj:
            # loop around objects
            for objname in all_inpaths:
                WLOG(params, '', '')
                WLOG(params, '', params['LOG.HEADER'])
                WLOG(params, '', textentry('40-509-00008', args=[objname]))
                WLOG(params, '', params['LOG.HEADER'])
                WLOG(params, '', '')
                # loop around files
                for row in range(len(all_inpaths[objname])):
                    # get in and out path
                    inpath = all_inpaths[objname][row]
                    outpath = all_outpaths[objname][row]
                    # ---------------------------------------------------------
                    # print string
                    copyargs = [row + 1, len(all_inpaths[objname]), outpath]
                    copystr = '[{0}/{1}] --> TAR[{2}]'.format(*copyargs)
                    # print copy string
                    WLOG(params, '', copystr, wrap=False)
                    tarfile_obj.add(inpath, arcname=os.path.basename(inpath))
                    # add to count
                    nfiles += 1
                    continue
        # remove tarpath if no files
        if nfiles == 0:
            if os.path.exists(tarpath):
                os.remove(tarpath)
        # return all in paths and out paths
        return all_inpaths, all_outpaths

    # -------------------------------------------------------------------------
    # Copy files
    # -------------------------------------------------------------------------
    for objname in all_inpaths:
        WLOG(params, '', '')
        WLOG(params, '', params['LOG.HEADER'])
        WLOG(params, '', textentry('40-509-00008', args=[objname]))
        WLOG(params, '', params['LOG.HEADER'])
        WLOG(params, '', '')
        # loop around files
        for row in range(len(all_inpaths[objname])):
            # get in and out path
            inpath = all_inpaths[objname][row]
            outpath = all_outpaths[objname][row]
            # -----------------------------------------------------------------
            # copy
            if do_symlink and do_copy:
                # print string
                copyargs = [row + 1, len(all_inpaths[objname]), outpath]
                copystr = '[{0}/{1}] --> SYM[{2}]'.format(*copyargs)
                # print copy string
                WLOG(params, '', copystr, wrap=False)
                # remove and symlink
                remove_previous(outpath)
                os.symlink(inpath, outpath)
            elif do_copy:
                # print string
                copyargs = [row + 1, len(all_inpaths[objname]), outpath]
                copystr = '[{0}/{1}] --> CP[{2}]'.format(*copyargs)
                # print copy string
                WLOG(params, '', copystr, wrap=False)
                # remove and copy
                remove_previous(outpath)
                shutil.copy(inpath, outpath)

    return all_inpaths, all_outpaths


def calib_filter(params: ParamDict, recipe: DrsRecipe,
                 filters: Dict[str, List[str]], user_outdir: str,
                 do_copy: bool = True, do_symlink: bool = False,
                 tarfilename: Optional[str] = None,
                 since: Optional[Time] = None, latest: Optional[Time] = None,
                 sizelimit: int = None
                 ) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    # -------------------------------------------------------------------------
    # get pconst
    pconst = load_functions.load_pconfig(select.INSTRUMENTS)
    # get the yamls for permissions
    perm_yaml = params['INPUTS'].get('PERMISSION_YAML', None)
    group_yaml = params['INPUTS'].get('GROUP_YAML', None)
    group_server = params['INPUTS'].get('GROUP_SERVER', None)
    if perm_yaml in ['None', 'Null', '']:
        perm_yaml = None
    if group_yaml in ['None', 'Null', '']:
        group_yaml = None
    if group_server in ['None', 'Null', '']:
        group_server = None
    # -------------------------------------------------------------------------
    # load index database
    WLOG(params, '', textentry('40-509-00001', args='file index'))
    calibdb = drs_database.CalibrationDatabase(params, recipe.shortname)
    calibdb.load_db()
    # load object database
    WLOG(params, '', textentry('40-509-00001', args='astrometric'))
    objdbm = drs_database.AstrometricDatabase(params, recipe.shortname)
    objdbm.load_db()
    # load log database
    WLOG(params, '', textentry('40-509-00001', args='log'))
    logdbm = drs_database.LogDatabase(params, recipe.shortname)
    logdbm.load_db()
    # -------------------------------------------------------------------------
    # deal with tar file name
    if tarfilename is not None:
        tarpath = os.path.join(user_outdir, tarfilename)
    else:
        tarpath = None
    # -------------------------------------------------------------------------
    # deal with since
    if since is not None:
        # convert to mjd
        since = since.mjd
    # deal with latest
    if latest is not None:
        # convert to mjd
        latest = latest.mjd
    # -------------------------------------------------------------------------
    # get parameters from filters
    keys = filters['KEYNAME']
    fibers = filters['KW_FIBER']

    inpaths = []
    # loop around keys
    for key in keys:
        # loop around fibers
        for fiber in fibers:
            # use standard way to get calibration filenames
            cout = calibdb.get_calib_file(key=key, header=None,
                                          filetime = None,
                                          required=False,
                                          nentries='*',
                                          no_times=True,
                                          fiber=fiber)
            # get return from get_calib_file
            infilenames, filetimes, _ = cout
            # deal with no files
            if len(infilenames) == 0:
                continue
            # make numpy arrays (so we can mask)
            infilenames = np.array(infilenames)
            filetimes = np.array(filetimes)
            # set up mask
            mask = np.ones(len(infilenames), dtype=bool)
            # deal with since and latest
            if since is not None:
                mask &= since > filetimes
            if latest is not None:
                mask &= latest < filetimes
            # apply mask and convert to strings
            _infilenames = []
            for infilename in infilenames[mask]:
                _infilenames.append(str(infilename))
            inpaths += _infilenames

    # storage of inpaths and run ids
    db_entries = dict(OBJNAME=dict(), RUN_ID=dict())
    # keep files
    db_entries['OBJNAME']['None'] = inpaths
    db_entries['RUN_ID']['None'] = ['CALIB'] * len(inpaths)

    # -------------------------------------------------------------------------
    # Now get outpaths (if infile exists)
    # -------------------------------------------------------------------------
    all_inpaths, all_outpaths = manage_outputs(params, db_entries,
                                               nosubdir=True,
                                               user_outdir=user_outdir,
                                               tarpath=tarpath,
                                               do_copy=do_copy,
                                               do_symlink=do_symlink,
                                               sizelimit=sizelimit,
                                               perm_yaml=perm_yaml,
                                               group_yaml=group_yaml,
                                               group_server=group_server)
    # return these inpaths and outpaths
    return all_inpaths, all_outpaths


def tellu_filter(params: ParamDict,  recipe: DrsRecipe,
                 kw_objnames: List[str], filters: Dict[str, List[str]],
                 user_outdir: str,
                 do_copy: bool = True, do_symlink: bool = False,
                 tarfilename: Optional[str] = None,
                 since: Optional[Time] = None, latest: Optional[Time] = None,
                 nosubdir: bool = False, sizelimit: int = None
                 ) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    # -------------------------------------------------------------------------
    # get pconst
    pconst = load_functions.load_pconfig(select.INSTRUMENTS)
    # get the yamls for permissions
    perm_yaml = params['INPUTS'].get('PERMISSION_YAML', None)
    group_yaml = params['INPUTS'].get('GROUP_YAML', None)
    group_server = params['INPUTS'].get('GROUP_SERVER', None)
    if perm_yaml in ['None', 'Null', '']:
        perm_yaml = None
    if group_yaml in ['None', 'Null', '']:
        group_yaml = None
    if group_server in ['None', 'Null', '']:
        group_server = None
    # -------------------------------------------------------------------------
    # load index database
    WLOG(params, '', textentry('40-509-00001', args='file index'))
    telludb = drs_database.TelluricDatabase(params, recipe.shortname)
    telludb.load_db()
    # load object database
    WLOG(params, '', textentry('40-509-00001', args='astrometric'))
    objdbm = drs_database.AstrometricDatabase(params, recipe.shortname)
    objdbm.load_db()
    # load log database
    WLOG(params, '', textentry('40-509-00001', args='log'))
    logdbm = drs_database.LogDatabase(params, recipe.shortname)
    logdbm.load_db()
    # -------------------------------------------------------------------------
    # deal with tar file name
    if tarfilename is not None:
        tarpath = os.path.join(user_outdir, tarfilename)
    else:
        tarpath = None
    # -------------------------------------------------------------------------
    # deal with since
    if since is not None:
        # convert to mjd
        since = since.mjd
    # deal with latest
    if latest is not None:
        # convert to mjd
        latest = latest.mjd
    # -------------------------------------------------------------------------
    # get parameters from filters
    keys = filters['KEYNAME']
    fibers = filters['KW_FIBER']
    # storage of inpaths and run ids
    db_entries = dict(OBJNAME=dict(), RUN_ID=dict())
    # loop around objects
    for objname in kw_objnames:
        # storage for inpaths
        inpaths, run_ids = [], []
        # loop around keys
        for key in keys:
            # loop around fibers
            for fiber in fibers:
                # get the table for this objname/key/fiber
                icols = 'FILENAME, UNIXTIME, RUN_ID'
                ttable = telludb.get_tellu_entry(columns=icols, key=key,
                                                 fiber=fiber, objname=objname)
                # get variables from table
                infilenames = ttable['FILENAME']
                filetimes = ttable['UNIXTIME']
                run_ids_entries = ttable['RUN_ID']
                # deal with no files
                if len(infilenames) == 0:
                    continue
                # make numpy arrays (so we can mask)
                infilenames = np.array(infilenames)
                filetimes = np.array(Time(filetimes, format='unix').mjd)
                # set up mask
                mask = np.ones(len(infilenames), dtype=bool)
                # deal with since and latest
                if since is not None:
                    mask &= since > filetimes
                if latest is not None:
                    mask &= latest < filetimes
                # apply mask and convert to strings
                _infilenames, _run_ids = [], []

                for it in np.where(mask)[0]:
                    _inbasename = str(infilenames[it])
                    _run_id = str(run_ids_entries[it])
                    # get full path
                    _infilename = os.path.join(params['PATH.TELLU'], key,
                                               objname, _inbasename)
                    # push into storage
                    if os.path.exists(_infilename):
                        _infilenames.append(str(_infilename))
                        _run_ids.append(str(_run_id))
                inpaths += _infilenames
                run_ids += _run_ids
        # ---------------------------------------------------------------------
        # keep files
        db_entries['OBJNAME']['None'] = inpaths
        db_entries['RUN_ID']['None'] = run_ids

    # -------------------------------------------------------------------------
    # Now get outpaths (if infile exists)
    # -------------------------------------------------------------------------
    all_inpaths, all_outpaths = manage_outputs(params, db_entries,
                                               nosubdir=nosubdir,
                                               user_outdir=user_outdir,
                                               tarpath=tarpath,
                                               do_copy=do_copy,
                                               do_symlink=do_symlink,
                                               sizelimit=sizelimit,
                                               perm_yaml=perm_yaml,
                                               group_yaml=group_yaml,
                                               group_server=group_server)
    # return these inpaths and outpaths
    return all_inpaths, all_outpaths


# =============================================================================
# Define helper functions
# =============================================================================
AllDict = Dict[str, List[str]]
PermDict = Dict[str, List[Union[None, Dict[str, str]]]]


def get_out_basename(params: ParamDict, infile: str) -> str:
    """
    Get the output base name for an input file based on prefix/suffix

    :param params: str, the parameter dictionary of constants
    :param infile: str, the input file name

    :return: str, the output base name with prefix/suffix applied if given
    """
    # get the prefix and suffix from inputs
    prefix = params['INPUTS'].get('OUT_PREFIX', None)
    suffix = params['INPUTS'].get('OUT_SUFFIX', None)
    # deal with null prefix/suffix
    if drs_text.null_text(prefix, ['None', '', 'Null']):
        prefix = None
    if drs_text.null_text(suffix, ['None', '', 'Null']):
        suffix = None
    # deal with no prefix or suffix --> just return base name
    if prefix is None and suffix is None:
        return os.path.basename(infile)
    # deal with only prefix (no suffix)
    if suffix is None:
        return prefix + os.path.basename(infile)
    # deal with only suffix (no prefix)
    elif prefix is None:
        base, ext = os.path.splitext(os.path.basename(infile))
        return base + suffix + ext
    # deal with both prefix and suffix
    else:
        base, ext = os.path.splitext(os.path.basename(infile))
        return prefix + base + suffix + ext


def get_standard_outpaths(params, nosubdir: bool, db_entries,
                          user_outdir, do_copy: bool = True
                          ) -> Tuple[AllDict, AllDict, PermDict]:
    # storage of inpaths/outpaths
    all_inpaths = dict()
    all_outpaths = dict()
    all_permissions = dict()
    # get just the in paths dictionary
    db_inpaths = db_entries['OBJNAME']
    # loop around objects with files
    for objname in db_inpaths:
        # output directory for objname
        if nosubdir:
            outdir = str(user_outdir)
        else:
            outdir = str(os.path.join(user_outdir, objname))
        # print progress: Adding outpaths for KW_OBJNAME={0}
        WLOG(params, '', textentry('40-509-00006', args=[objname]))
        # add object name to storage
        all_inpaths[objname] = []
        all_outpaths[objname] = []
        # loop around all files for this object
        for filename in db_inpaths[objname]:
            # if object exists
            if os.path.exists(filename):
                # get paths
                inpath = filename
                basename = get_out_basename(params, filename)
                outpath = os.path.join(outdir, basename)
                # add to storage
                all_inpaths[objname].append(inpath)
                all_outpaths[objname].append(outpath)
                all_permissions[objname].append(None)
        # make a directory for this object (if it doesn't exist)
        if len(all_outpaths[objname]) != 0:
            # print progress: Added {0} outpaths'
            margs = [len(all_outpaths[objname])]
            WLOG(params, '', textentry('40-509-00007', args=margs))
            # create output directory if it doesn't exist
            if not os.path.exists(outdir) and do_copy:
                os.mkdir(outdir)

    return all_inpaths, all_outpaths, all_permissions


def get_perm_outpaths(params, nosubdir: bool, db_entries,
                      user_outdir, do_copy: bool = True,
                      perm_yaml: str = None, group_yaml: str = None,
                      group_server: str = None
                      ) -> Tuple[AllDict, AllDict, PermDict]:

    # storage of inpaths/outpaths
    all_inpaths = dict()
    all_outpaths = dict()
    all_permissions = dict()
    # get in paths dictionary and run ids dictionary
    db_inpaths = db_entries['OBJNAME']
    db_runids = db_entries['RUN_ID']
    # -------------------------------------------------------------------------
    # load permission yaml
    if not os.path.exists(perm_yaml):
        eargs = [perm_yaml]
        emsg = 'Permission YAML file {0} does not exist'
        WLOG(params, 'error', emsg.format(*eargs))
    perm_dict = base.load_yaml(perm_yaml)
    # -------------------------------------------------------------------------
    # load group yaml
    if not os.path.exists(group_yaml):
        eargs = [group_yaml]
        emsg = 'Group YAML file {0} does not exist'
        WLOG(params, 'error', emsg.format(*eargs))
    group_dict = base.load_yaml(group_yaml)
    # -------------------------------------------------------------------------
    # user outdir needs to have an objects and a runid directory
    obj_dir = os.path.join(user_outdir, 'objects')
    runid_dir = os.path.join(user_outdir, 'runids')
    # make the object sub-directory if it doesn't exist
    if not os.path.exists(obj_dir) and do_copy:
        os.mkdir(obj_dir)
    # make the runid sub-directory if it doesn't exist
    if not os.path.exists(runid_dir) and do_copy:
        os.mkdir(runid_dir)
    # -------------------------------------------------------------------------
    # loop around objects with files
    for objname in db_inpaths:

        # output directory for objname
        if nosubdir:
            obj_outdir = str(obj_dir)
        else:
            obj_outdir = str(os.path.join(obj_dir, objname))

        # print progress: Adding outpaths for KW_OBJNAME={0}
        WLOG(params, '', textentry('40-509-00006', args=[objname]))
        # add object name to storage
        all_inpaths[objname] = []
        all_outpaths[objname] = []
        all_permissions[objname] = []
        # loop around all files for this object
        for f_it, filename in enumerate(db_inpaths[objname]):
            # if object exists
            if os.path.exists(filename):
                # get file base name
                basename = get_out_basename(params, filename)
                # get paths
                run_id_inpath = filename
                # -------------------------------------------------------------
                # manage run id files
                # -------------------------------------------------------------
                # get run id for this file
                run_id = db_runids[objname][f_it]
                # skip files we don't have permission to copy
                if run_id not in perm_dict:
                    continue
                # out run id path is runid_dir/{RUNID}/basename
                run_id_outdir = os.path.join(runid_dir, str(run_id))
                # make run id directory if it doesn't exist
                if not os.path.exists(run_id_outdir) and do_copy:
                    os.mkdir(run_id_outdir)
                # run directory permission commands (if given)
                _ = permission_commands(params, run_id, perm_dict,
                                        group_dict, group_server,
                                        ptype='dir',
                                        run=True, path=run_id_outdir)

                run_id_outpath = os.path.join(run_id_outdir, basename)
                # add obj path to storage
                all_inpaths[objname].append(run_id_inpath)
                all_outpaths[objname].append(run_id_outpath)

                # TODO: Test whether we need to add permissions per file
                #       of if per directory is enough
                # run directory permission commands (if given)
                # cmds = permission_commands(params, run_id, perm_dict,
                #                         group_dict, group_server,
                #                         ptype='file',
                #                         run=True, path=run_id_outdir)
                cmds = []
                all_permissions[objname].append(dict(CTYPE='CP', COMMANDS=cmds))
                # -------------------------------------------------------------
                # manage object files
                # -------------------------------------------------------------
                # make run id directory if it doesn't exist
                if not os.path.exists(obj_outdir) and do_copy:
                    os.mkdir(obj_outdir)
                # get the outpath for the object file
                obj_outpath = os.path.join(obj_outdir, basename)
                # add obj path to storage
                all_inpaths[objname].append(run_id_outpath)
                all_outpaths[objname].append(obj_outpath)
                all_permissions[objname].append(dict(CTYPE='SYM', COMMANDS=[]))

    # return in paths out paths and permissions
    return all_inpaths, all_outpaths, all_permissions


def copy_files(params, all_inpaths: AllDict,  all_outpaths: AllDict,
               do_symlink: bool, do_copy: bool,
               all_permissions: PermDict):
    for objname in all_inpaths:
        WLOG(params, '', '')
        WLOG(params, '', params['DRS_HEADER'])
        WLOG(params, '', textentry('40-509-00008', args=[objname]))
        WLOG(params, '', params['DRS_HEADER'])
        WLOG(params, '', '')
        # loop around files
        for row in range(len(all_inpaths[objname])):
            # get in and out path
            inpath = all_inpaths[objname][row]
            outpath = all_outpaths[objname][row]
            # -----------------------------------------------------------------
            # copy via all permissions dictionary
            # -----------------------------------------------------------------
            if all_permissions[objname][row] is not None:
                # get copy type and commands
                ctype = all_permissions[objname][row]['CTYPE']
                commands = all_permissions[objname][row]['COMMANDS']
                # print string
                copyargs = [row + 1, len(all_inpaths[objname]), ctype,
                            outpath]
                copystr = '[{0}/{1}] --> {2}[{3}]'.format(*copyargs)
                # print copy string
                WLOG(params, '', copystr, wrap=False)
                # remove previous
                remove_previous(outpath)
                # run copy commands on files
                # (usually a copy or symlink followed by some permission change)
                try:
                    if ctype == 'SYM':
                        os.symlink(inpath, outpath)
                    else:
                        shutil.copy(inpath, outpath)
                    # then run permission commands
                    for command in commands:
                        os.system(command)
                except Exception as _:
                    eargs = [ctype, inpath, outpath]
                    emsg = 'Failed to run {0} commands on {1} to {2}'
                    emsg += ' with commands: \n{2}'
                    emsg = emsg.format(*eargs, '\n'.join(commands))
                    WLOG(params, 'error', emsg.format(*eargs))
            # -----------------------------------------------------------------
            # copy via symbolic link
            # -----------------------------------------------------------------
            elif do_symlink and do_copy:
                # print string
                copyargs = [row + 1, len(all_inpaths[objname]), outpath]
                copystr = '[{0}/{1}] --> SYM[{2}]'.format(*copyargs)
                # print copy string
                WLOG(params, '', copystr, wrap=False)
                # remove and symlink
                remove_previous(outpath)
                os.symlink(inpath, outpath)
            # -----------------------------------------------------------------
            # copy via shutil copy (full copy)
            # -----------------------------------------------------------------
            elif do_copy:
                # print string
                copyargs = [row + 1, len(all_inpaths[objname]), outpath]
                copystr = '[{0}/{1}] --> CP[{2}]'.format(*copyargs)
                # print copy string
                WLOG(params, '', copystr, wrap=False)
                # remove and copy
                remove_previous(outpath)
                shutil.copy(inpath, outpath)

    return all_inpaths, all_outpaths


def permission_commands(params, run_id: str, perm_dict: dict,
                        group_dict: dict, group_server: str,
                        ptype: str = 'file',
                        run: bool = False, path: str = '') -> List[str]:
    """
    Run permission commands on a file

    :param params: ParamDict, the parameter dictionary of constants
    :param commands: list of strings, the commands to run

    :return:
    """
    # find run id in permission dictionary
    if run_id not in perm_dict:
        return []
    # get the permissions for this run id
    run_id_dict = perm_dict[run_id]
    # -------------------------------------------------------------------------
    # storage of users and their permissions
    users = dict()
    # deal with groups
    for group in run_id_dict.get('GROUPS', []):
        # make sure the group exists in our group dictionary
        if group in group_dict:
            _group_dict = group_dict[group]
            # get group parameters
            _group_users = _group_dict.get('USERS', [])
            _group_server = _group_dict.get('SERVER', None)
            _group_dir_perms = _group_dict.get('DIRECTORY_PERMISSIONS', None)
            _group_file_perms = _group_dict.get('FILE_PERMISSIONS', None)
            # if the group server is not the same as the current server skip
            #  this group
            if group_server != _group_server:
                continue
            # loop around users in this group
            for _user in _group_users:
                # make sure we don't add a user twice
                if _user not in users:
                    # deal with directory
                    if ptype == 'dir':
                        users[_user] = _group_dir_perms
                    else:
                        users[_user] = _group_file_perms
    # -------------------------------------------------------------------------
    # store commands to run
    commands = []
    # loop around users and run commands
    for _user in users:
        # get args
        _kwargs = dict(user=_user, path=path)
        # loop around commands
        for user_cmd in users[_user]:
            # skip if no command given
            if user_cmd is None:
                continue
            # push arguments into command
            command = user_cmd.format(**_kwargs)
            # add to commands (if not already there)
            if command not in commands:
                commands.append(command)
    # -------------------------------------------------------------------------
    # try to run command
    if run:
        for command in commands:
            try:
                os.system(command)
            except Exception as _:
                eargs = [command]
                emsg = 'Failed to run permission command: {0}'
                WLOG(params, 'error', emsg.format(*eargs))
    # -------------------------------------------------------------------------
    # return commands
    return commands


def remove_previous(outpath: str):
    """
    Deal with removing previous file (whether it is a hard link or symlink)
    :param outpath: str, file to check
    :return:
    """
    if os.path.islink(outpath):
        os.unlink(outpath)
    elif not os.path.exists(outpath):
        return
    else:
        os.remove(outpath)


def all_objects(params: ParamDict, recipe: DrsRecipe):
    # load index database
    WLOG(params, '', textentry('40-509-00001', args='file index'))
    findexdb = drs_database.FileIndexDatabase(params, recipe.shortname)
    findexdb.load_db()
    # return all object names
    objs = findexdb.get_unique(column='KW_OBJNAME',
                               condition='BLOCK_KIND="raw"')
    # print number of objects found
    msg = 'Found {0} raw objects in file index database'
    margs = [len(objs)]
    WLOG(params, 'info', msg.format(*margs))
    # return objects
    return objs


def fiber_by_output(kw_fibers: Union[List[str], None],
                    kw_outputs: Union[List[str], None]
                    ) -> Union[List[str], None]:
    # if we have no outputs just return the fibers
    if kw_outputs is None:
        return kw_fibers
    # if fibers is already None just return it
    if kw_fibers is None:
        return None
    # load psuedo constants
    pconst = load_functions.load_pconfig(select.INSTRUMENTS)
    filemod = pconst.FILEMOD()
    # get filesets
    filedefs = [filemod.raw_file, filemod.pp_file, filemod.red_file,
                filemod.post_file]
    # get all drs output ids that do not have fiber set
    no_fiber_drsoutids = []
    # loop around
    for filedef in filedefs:
        for drs_file in filedef.fileset:
            if drs_file.fibers is None:
                no_fiber_drsoutids.append(drs_file.name)
    # now deal with outputs that our in our list
    # if we have one output in out list return kw_fibers = None
    for kw_output in kw_outputs:
        if kw_output in no_fiber_drsoutids:
            return None
    # if we get to here we return kw_fibers
    return kw_fibers


def check_size_limit(params: ParamDict, inpaths: Dict[str, List[str]],
                     sizelimit: int):
    """
    Check that the total size of files does not exceed the size limit

    :param params: ParamDict, the parameter dictionary of constants
    :param inpaths: dictionary, for each objname a list of input file locations
    :param sizelimit: int, a file limit in GBs

    :raises: WLOG error if total size of files exceeds limit
    :return:
    """
    # deal with bad size limit
    if sizelimit in ['None', None, '', 'Null']:
        return
    # deal with bad size limit
    if sizelimit <= 0:
        return
    # store total size in bytes
    total_size = 0
    # loop around all objects and all files and add to the total size
    for key in inpaths:
        for path in inpaths[key]:
            total_size += os.path.getsize(path)
    # convert to GB
    total_size = total_size / (1024 ** 3)
    # deal with total size being too large
    if total_size > sizelimit:
        # print warning
        eargs = [total_size, sizelimit]
        emsg = 'Total size of files ({0:.3f} GB) exceeds limit ({1:.3f} GB)'
        raise AperoCodedException(params, message=emsg.format(*eargs),
                                  targs=eargs)


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # print hello world
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
