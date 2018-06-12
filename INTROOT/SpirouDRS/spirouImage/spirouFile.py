#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-04-19 at 16:16

@author: cook
"""
import numpy as np
import os
import glob

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouStartup
from SpirouDRS import spirouImage

# =============================================================================
# Define variables
# =============================================================================
# Define the name of this module
__NAME__ = 'spirouFile.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# -----------------------------------------------------------------------------


# =============================================================================
# Define classes
# =============================================================================
class PathException(Exception):
    """Raised when config file is incorrect"""
    pass


class Paths():
    def __init__(self, *args, **kwargs):
        """
        Set up a path object (to be used for file operations)

        """
        # set up storage
        self.rel_paths = []
        self.abs_paths = []
        self.root = None

        # set root from kwargs
        self.root = kwargs.get('root', None)
        if self.root is not None:
            self.root = os.path.abspath(self.root)

        # load args
        self.__load_args(args)

        # update root
        self.add_root()

        # update wildcards
        self.update_wildcards()


    def __load_args(self, args):
        # arguments are expected to be either a list of strings, a list or
        # another path object
        for ai, arg in enumerate(args):
            try:
                if type(arg) == str:
                    self.rel_paths.append(arg)
                elif type(arg) in [list, np.array]:
                    self.rel_paths += list(arg)
                elif type(arg) == Paths:
                    self.rel_paths += arg.rel_paths
                    self.abs_paths += arg.abs_paths
                    self.root = arg.root
                else:
                    raise ValueError()
            except:
                emsg = ('Argument {0}={1} format={2} not understood. Argument '
                        'must be a string, a list or another paths object')
                raise PathException(emsg.format(ai+1, arg, type(arg)))
        # copy to abs_paths
        self.abs_paths = list(self.rel_paths)

    def __add__(self, value):
        return Paths(self, value)

    def add_root(self, check=False):
        # deal with user inputted roots
        # if root is blank do nothing
        if self.root == None:
            pass
        # if root is a string
        elif type(self.root) == str:
            # if check, check that root exists
            if check:
                if not os.path.exists(self.root):
                    emsg = 'Root = {0} does not exist'
                    raise PathException(emsg)
            self.abs_paths = []
            # loop around relative paths and add root
            for rel_path in self.rel_paths:
                self.abs_paths.append(os.path.join(self.root, rel_path))
        # if root is not a string break
        else:
            emsg = 'Root = {0} not a valid python string'
            raise PathException(emsg)

    def replace_root(self, root=None, check=False):
        # deal with user inputted roots
        # if root is blank do nothing
        if root == None:
            pass
        # if root is a string
        elif type(root) == str:
            # if check, check that root exists
            if check:
                if not os.path.exists(root):
                    emsg = 'Root = {0} does not exist'
                    raise PathException(emsg)
            # change to abs_root
            root = os.path.abspath(root) + os.path.sep
            # construct the abs part of original root
            part = self.root + os.path.sep
            # loop around relative paths and replace the first old root with
            #     the new root
            for ai, abs_path in enumerate(self.abs_paths):
                # replace
                self.abs_paths[ai] = abs_path.replace(part, root, 1)
            # finally update the root
            self.root = root
        # if root is not a string break
        else:
            emsg = 'Root = {0} not a valid python string'
            raise PathException(emsg)

    def update_wildcards(self):
        # storage for new paths
        rel_paths = []
        # loop around the absolute path
        for ai, abs_path in enumerate(self.abs_paths):
            # get directory path and filename
            dirname = os.path.dirname(abs_path)
            relpath = self.rel_paths[ai]
            # check that dir exists
            if os.path.exists(dirname):
                # look for wild cards (regular expression "magic")
                if glob.has_magic(abs_path):
                    # get files using wild cards
                    absfiles = list(glob.glob(abs_path))
                    # loop around files
                    for absfile in absfiles:
                        # set abs part
                        part = self.root + os.path.sep
                        # remove the root (as we are appending rel_path)
                        relfile = absfile.replace(part, '', 1)
                        # add to rel_paths
                        rel_paths.append(relfile)
                # else just append normal file
                else:
                    rel_paths.append(relpath)
            # if dirname does not exist we can't access wildcards so skip
            else:
                rel_paths.append(relpath)
        # add rel paths to self
        self.rel_paths = rel_paths
        # finally add the root back
        self.add_root()


# =============================================================================
# Define ID functions (pre-processing)
# =============================================================================
def identify_unprocessed_file(p, filename, hdr=None, cdr=None):
    func_name = __NAME__ + '.identify_file()'
    # ----------------------------------------------------------------------
    # load control file
    control = get_control_file()
    # only look at raw files
    rawmask = control['kind'] == 'RAW'
    control = control[rawmask]
    # ----------------------------------------------------------------------
    # get file header (if not passed in)
    # get header if None
    if hdr is None or cdr is None:
        if not os.path.exists(filename):
            emsg1 = 'Cannot read header. File does not exist ({0})'
            emsg2 = '    fuction = {0}'.format(func_name)
            WLOG('error', p['LOG_OPT'], [emsg1.format(filename), emsg2])
        else:
            hdr, cdr = spirouImage.ReadHeader(p, filename, return_comments=True)
    # ----------------------------------------------------------------------
    # Step 1: Look for odometer code in filename (e.g. d.fits f.fits o.fits)
    # get check and code
    cond1, code = odometer_code(control, filename)
    # ----------------------------------------------------------------------
    # Step 2: Look for OBSTYPE, SBCCAS_P and SBCREF_P in header
    cond2, obstype, ccas, cref = odometer_header(p, hdr)
    # ----------------------------------------------------------------------
    # if step 2 succeed ID file
    if cond2:
        newfn, hdr, cdr = id_mode(p, control, filename, hdr, cdr, code,
                             obstype, ccas, cref)
    # else we don't have the file key and header fallback on checking filename
    else:
        newfn, hdr, cdr = fallback_id_mode(p, control, filename, hdr, cdr)
    # ----------------------------------------------------------------------
    # return filename and header
    return newfn, hdr, cdr


# =============================================================================
# Define ID functions (main recipes)
# =============================================================================
def check_file_id(p, filename, recipe, hdr=None, **kwargs):

    func_name = __NAME__ + '.check_file_id()'
    # remove .py from recipe (in case it is here)
    recipe = recipe.split('.py')[0]
    # make sure filename has no path
    basefilename = os.path.basename(filename)
    # get returns
    return_recipe = kwargs.get('return_recipe', False)
    return_path = kwargs.get('return_path', False)
    # load control file
    control = get_control_file()
    # Check that recipe is valid
    if recipe not in control['Recipe']:
        emsg1 = 'No recipe named {0}'.format(recipe)
        emsg2 = '    function = {0}'.format(func_name)
        WLOG('error', p['LOG_OPT'], [emsg1, emsg2])
    # Get mask of recipe and apply it to control
    else:
        recipemask = control['Recipe'] == recipe
        control = control[recipemask]
    # step 1: check filename
    cond, control = check_id_filename(p, control, basefilename, recipe)
    # step 2: if not filename check header key DPRTYPE
    if not cond:
        cond, control = check_id_header(p, control, recipe, hdr)

    # return p
    return p


def check_files_id(p, files, recipe, hdr=None, **kwargs):
    """
    Wrapper for check_file_id

    :param p:
    :param files:
    :param recipe:
    :param hdr:
    :param kwargs:
    :return:
    """
    for filename in files:
        p = check_file_id(p, filename, recipe, hdr, **kwargs)
    return p


# =============================================================================
# Define worker functions
# =============================================================================
def get_control_file():
    # get SpirouDRS data folder
    package = spirouConfig.Constants.PACKAGE()
    relfolder = spirouConfig.Constants.DATA_CONSTANT_DIR()
    datadir = spirouConfig.GetAbsFolderPath(package, relfolder)
    # construct the path for the control file
    controlfn, controlfmt = spirouConfig.Constants.RECIPE_CONTROL_FILE()
    controlfile = os.path.join(datadir, controlfn)
    # load control file
    control = spirouImage.ReadTable(controlfile, fmt=controlfmt, comment='#')
    # return control
    return control


def odometer_code(control, filename):
    # get unique codes from control
    ocodes = np.unique(control['ocode'])

    # look for "ocode.fits" in filename
    cond = False
    code = None
    for ocode in ocodes:
        if filename.endswith('{0}.fits'.format(ocode)):
            cond = True
            code = ocode
    # return cond and code
    return cond, code


def odometer_header(p, hdr):
    func_name = __NAME__ + '.odometer_header()'
    # set condition to True
    cond = True
    # get observation type
    if p['KW_OBSTYPE'][0] in hdr:
        obstype = hdr[p['KW_OBSTYPE'][0]]
    else:
        obstype = None
        cond = False
    # get science fiber type
    if p['KW_CCAS'][0] in hdr:
        ccas = hdr[p['KW_CCAS'][0]]
    else:
        ccas = None
        cond = False
    # get reference fiber type
    if p['KW_CREF'][0] in hdr:
        cref = hdr[p['KW_CREF'][0]]
    else:
        cref = None
        cond = False
    # return the cond and type values
    return cond, obstype, ccas, cref


def id_mode(p, control, filename, hdr, cdr, code, obstype, ccas, cref):
    # get base filename (no path)
    basefilename = os.path.basename(filename)
    # find a match for code, obstype, ccas, cref
    match, matchno = find_match(control, code, obstype, ccas, cref)
    # if we have a match need to update filename
    if match:
        # get dpr type
        dprtype = control['dprtype'][matchno]
        # get dstring
        dstring = control['dstring'][matchno]
        # log successful finding
        wmsg = 'File {0} identified as {1}'
        WLOG('info', p['LOG_OPT'], wmsg.format(basefilename, dprtype))
        # log mode (in debug mode)
        if p['DRS_DEBUG'] > 0:
            wmsg = '\tID via HEADER   OCODE={0} OBSTYPE={1} CCAS={2} CREF={3}'
            WLOG('', p['LOG_OPT'], wmsg.format(code, obstype, ccas, cref))
        # add key to header
        hdr[p['KW_DPRTYPE'][0]] = dprtype
        cdr[p['KW_DPRTYPE'][0]] = p['KW_DPRTYPE'][2]
        # update filename
        newext = '_{0}.fits'.format(dstring)
        newfilename = filename.replace('.fits', newext)
        # return new filename and header
        return newfilename, hdr, cdr
    else:
        # deal with no match
        emsg1 = ('File {0} not identified as a valid DRS input.'
                 ''.format(basefilename))
        emsg2 = ('\tOCODE={0} OBSTYPE={1} CCAS={2} CREF={3}'
                 ''.format(code, obstype, ccas, cref))
        WLOG('warning', p['LOG_OPT'], [emsg1, emsg2])
        return filename, hdr, cdr


def find_match(control, code, obstype, ccas, cref):
    # get obs, ccas and cref types
    codes = control['ocode']
    obs_types = control['obstype']
    ccas_types = control['ccas']
    cref_types = control['cref']
    # loop around each file to identify file
    match_number = None
    match = True
    for c_it in range(len(obs_types)):
        # skip if match number set already
        if match_number is not None:
            continue
        # check None conditions
        c0 = codes[c_it] == 'None'
        c1 = obs_types[c_it] == 'None'
        c2 = ccas_types[c_it] == 'None'
        c3 = cref_types[c_it] == 'None'
        # if all three types are None skip
        if c0 and c1 and c2 and c3:
            continue
        # set match
        match = True
        # check ocode (allowed to be None if filename changed)
        if (not c0) and (code is not None):
            match &= (code.upper() == codes[c_it].upper())
        # check obs type
        if not c1:
            match &= (obstype.upper() == obs_types[c_it].upper())
        # check ccas type
        if not c2:
            match &= (ccas.upper() == ccas_types[c_it].upper())
        # check cref type
        if not c3:
            match &= (cref.upper() == cref_types[c_it].upper())
        # set match_number
        if match:
            match_number = c_it
    # return match and match_number
    return match, match_number


def fallback_id_mode(p, control, filename, hdr, cdr):
    # get base filename (no path)
    basefilename = os.path.basename(filename)
    # get unique_strings
    ustrings = control['dstring']
    # loop around ustrings
    for u_it, ustring in enumerate(ustrings):
        # skip Nones
        if ustring == 'None':
            continue
        # search for ustring in filename (return on first found)
        if ustring in basefilename:
            # get dpr type
            dprtype = control['dprtype'][u_it]
            # log successful finding
            wmsg = 'File {0} identified as {1}'
            WLOG('info', p['LOG_OPT'], wmsg.format(basefilename, dprtype))
            # log mode (in debug mode)
            if p['DRS_DEBUG'] > 0:
                wmsg = '\tID via filename   file={0}'
                WLOG('', p['LOG_OPT'], wmsg.format(basefilename))
            # update header key 'DPRTYPE
            hdr[p['KW_DPRTYPE'][0]] = dprtype
            cdr[p['KW_DPRTYPE'][0]] = p['KW_DPRTYPE'][2]
            # return original filename and header
            return filename, hdr, cdr
    # if file not found log this
    emsg = 'File {0} not identified as a valid DRS input.'
    WLOG('warning', p['LOG_OPT'], emsg.format(basefilename))
    return filename, hdr, cdr


def check_id_filename(p, control, filename, recipe):
    func_name = __NAME__ + '.check_id_filename()'
    # set un-found initial parameters
    found = False
    found_row = None
    # loop around rows in control
    for row in range(len(control)):
        # skip if already found
        if found:
            continue
        # get this iterations values
        dstring = control['dstring'][row]
        # search for dstring in filename
        if dstring in filename:
            found = True
            found_row = int(row)
    # deal with no file found
    if not found:
        return found, control
    # if file found return row of control found in
    else:
        return found, control[found_row]


def check_id_header(p, control, recipe, hdr=None):

    cond = True

    return cond, control

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
