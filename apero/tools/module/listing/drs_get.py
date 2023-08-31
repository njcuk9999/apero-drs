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

from apero import lang
from apero.base import base
from apero.core import constants
from apero.core.core import drs_database
from apero.core.core import drs_log
from apero.core.core import drs_text
from apero.core.utils import drs_recipe

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'drs_get.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
ParamDict = constants.ParamDict
DrsRecipe = drs_recipe.DrsRecipe
# Get the text types
textentry = lang.textentry


# =============================================================================
# Define functions
# =============================================================================
def basic_filter(params: ParamDict, kw_objnames: List[str],
                 filters: Dict[str, List[str]], user_outdir: str,
                 do_copy: bool = True, do_symlink: bool = False,
                 tarfilename: Optional[str] = None,
                 since: Optional[Time] = None, latest: Optional[Time] = None,
                 timekey: str = 'observed', nosubdir: bool = False,
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

    :return: Tuple, 1. dict, for each objname a list of input file locations
                    2. dict, for each objname a list of output file locations
    """
    # -------------------------------------------------------------------------
    # get pconst
    pconst = constants.pload()
    # get whether to filter by passing qc
    filter_qc = not params['INPUTS']['failedqc']
    # -------------------------------------------------------------------------
    # load index database
    WLOG(params, '', textentry('40-509-00001', args='file index'))
    findexdb = drs_database.FileIndexDatabase(params)
    findexdb.load_db()
    # load object database
    WLOG(params, '', textentry('40-509-00001', args='astrometric'))
    objdbm = drs_database.AstrometricDatabase(params)
    objdbm.load_db()
    # load log database
    WLOG(params, '', textentry('40-509-00001', args='log'))
    logdbm = drs_database.LogDatabase(params)
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
    # separate list for each object name
    # -------------------------------------------------------------------------
    # storage of inpaths
    database_inpaths = dict()
    # loop around input object names
    for kw_objname in kw_objnames:
        # clean object name (as best we can)
        clean_obj_name, _ = objdbm.find_objname(pconst, kw_objname)
        WLOG(params, '', textentry('40-509-00002', args=[clean_obj_name]))
        # write condition for this object
        if drs_text.null_text(kw_objname, ['None', '', 'Null']):
            obj_condition = None
        else:
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
        # get inpaths
        itable = findexdb.get_entries('ABSPATH, KW_PID', condition=condition)
        inpaths = np.array(itable['ABSPATH'])
        ipids = np.array(itable['KW_PID'])
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
            database_inpaths[clean_obj_name] = inpaths[mask]
        else:
            WLOG(params, '', textentry('40-509-00004'))
        # write that we excluded some files
        if filter_qc:
            WLOG(params, '', textentry('40-509-00005', args=[np.sum(~mask)]))
    # -------------------------------------------------------------------------
    # Now get outpaths (if infile exists)
    # -------------------------------------------------------------------------
    # storage of inpaths/outpaths
    all_inpaths = dict()
    all_outpaths = dict()
    # loop around objects with files
    for objname in database_inpaths:
        # output directory for objname
        if nosubdir:
            outdir = str(user_outdir)
        else:
            outdir = os.path.join(user_outdir, objname)
        # print progress: Adding outpaths for KW_OBJNAME={0}
        WLOG(params, '', textentry('40-509-00006', args=[objname]))
        # add object name to storage
        all_inpaths[objname] = []
        all_outpaths[objname] = []
        # loop around all files for this object
        for filename in database_inpaths[objname]:
            # if object exists
            if os.path.exists(filename):
                # get paths
                inpath = filename
                basename = os.path.basename(filename)
                outpath = os.path.join(outdir, basename)
                # add to storage
                all_inpaths[objname].append(inpath)
                all_outpaths[objname].append(outpath)
        # make a directory for this object (if it doesn't exist)
        if len(all_outpaths[objname]) != 0:
            # print progress: Added {0} outpaths'
            margs = [len(all_outpaths[objname])]
            WLOG(params, '', textentry('40-509-00007', args=margs))
            # create output directory if it doesn't exist
            if not os.path.exists(outdir) and do_copy:
                os.mkdir(outdir)
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
                WLOG(params, '', params['DRS_HEADER'])
                WLOG(params, '', textentry('40-509-00008', args=[objname]))
                WLOG(params, '', params['DRS_HEADER'])
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


def all_objects(params):
    # load index database
    WLOG(params, '', textentry('40-509-00001', args='file index'))
    findexdb = drs_database.FileIndexDatabase(params)
    findexdb.load_db()
    # return all object names
    objs =  findexdb.get_unique(column='KW_OBJNAME',
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
    pconst = constants.pload()
    filemod = pconst.FILEMOD().get()
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


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # print hello world
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
