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
from . import spirouFITS
from . import spirouTable


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
# Get the parameter dictionary class
ParamDict = spirouConfig.ParamDict
ConfigError = spirouConfig.ConfigError
# Get Logging function
WLOG = spirouCore.wlog
# -----------------------------------------------------------------------------


# =============================================================================
# Define classes
# =============================================================================
class PathException(Exception):
    """Raised when config file is incorrect"""
    pass


class Paths:
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
        if self.root is None:
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
        if root is None:
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
# Define file functions
# =============================================================================
def get_most_recent(filelist):
    # set most recent time to None to start
    most_recent = None
    # loop around file list
    for file_it in filelist:
        # get modified time
        file_time = os.path.getctime(file_it)
        # add to most_recent if newer
        if most_recent is None:
            most_recent = file_time
        elif file_time > most_recent:
            most_recent = file_time
    # return most recent time
    return most_recent


def sort_by_name(filelist):
    # define storage for base file list
    baselist = []
    # get base list of files
    for file_it in filelist:
        basename = os.path.basename(file_it)
        baselist.append(basename)
    # get sorted base file list
    indices = np.argsort(baselist)
    # return sorted filelist
    return indices


# =============================================================================
# Define ID functions (pre-processing)
# =============================================================================
def identify_unprocessed_file(p, filename, hdr=None):
    """
    Identify a unprocessed raw file (from recipe control file), adds suffix
    and header key (DPRTYPE) accordingly

    :param p: parameter dictionary, ParamDict containing constants
            Must contain at least:
                DRS_DEBUG: int, if 0 not in debug mode else in various levels of
                           debug
                KW_DPRTYPE: list, keyword list [key, value, comment]

    :param filename: string, the filename to check
    :param hdr: dictionary or None, the HEADER dictionary to check for keys and
                associated values, if None attempt to open HEADER from filename

    :return newfn: string, the new filename with added suffix
    :return hdr: dictionary, the HEADER with added HEADER key/value pair
                 (DPRTYPE)
    """
    # ----------------------------------------------------------------------
    # load control file
    control = get_control_file(p)
    # only look at raw files
    rawmask = control['kind'] == 'RAW'
    control = control[rawmask]
    # ----------------------------------------------------------------------
    # get file header (if not passed in)
    hdr = get_header_file(p, filename, hdr)
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
        newfn, hdr = id_mode(p, control, filename, hdr, code,
                             obstype, ccas, cref)
    # else we don't have the file key and header fallback on checking filename
    else:
        newfn, hdr = fallback_id_mode(p, control, filename, hdr)
    # ----------------------------------------------------------------------
    # return filename and header
    return newfn, hdr


# =============================================================================
# Define ID functions (main recipes)
# =============================================================================
def check_file_id(p, filename, recipe, skipcheck=False, hdr=None, pos=None,
                  **kwargs):
    """
    Checks the "filename" against the "recipe" (using recipe control)

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            IC_FORCE_PREPROCESS: bool, if True only allows pre-processed files
            PROCESSED_SUFFIX: string, the processed suffix
            DRS_DATA_RAW: string, the directory that the raw data should
                          be saved to/read from
                DRS_DATA_REDUC: string, the directory that the reduced data
                                should be saved to/read from
            ARG_NIGHT_NAME: string, the folder within data raw directory
                            containing files (also reduced directory) i.e.
                            /data/raw/20170710 would be "20170710"

    :param filename: string, the filename to check
    :param recipe: string, the recipe name to check
    :param skipcheck: bool, if True does not check file
    :param hdr: dictionary or None, if defined must be a HEADER dictionary if
                none loaded from filename
    :param pos: int or None, if not None defines the position of the file
    :param kwargs: keyword arguments. Current allowed keys are:
                    - return_path: bool, if True returns the path as well as p

    :return p: parameter dictionary, the updated parameter dictionary
            Adds the following:
                PREPROCESSED: bool, flag whether file is detected as
                              pre-processed
                DPRTYPE: string, the type from the recipe control file
                FIBER: string, if recipe control entry for this file has a
                       fiber defined, fiber is set to this
    """
    func_name = __NAME__ + '.check_file_id()'
    # remove .py from recipe (in case it is here)
    recipe = recipe.split('.py')[0]
    # load control file
    control = get_control_file(p)
    # get some needed paths
    rawpath = spirouConfig.Constants.RAW_DIR(p)
    tmppath = spirouConfig.Constants.TMP_DIR(p)
    reducedpath = spirouConfig.Constants.REDUCED_DIR(p)
    # get returns
    return_path = kwargs.get('return_path', False)
    # ---------------------------------------------------------------------
    # Check that recipe is valid
    # ---------------------------------------------------------------------
    if skipcheck:
        # log that we are skipping checks
        wmsg = 'Skipping filename check'
        WLOG(p, 'warning', [wmsg])
        # add values to p for skipped
        p['DPRTYPE'] = 'None'
        p['PREPROCESSED'] = True
        p['DRS_TYPE'] = 'None'
        p.set_sources(['DPRTYPE', 'PREPROCESSED', 'DRS_TYPE'], func_name)
        # deal with return
        if return_path:
            return p, p['ARG_FILE_DIR']
        else:
            return p
    elif recipe not in control['Recipe']:
        emsg1 = 'No recipe named {0}'.format(recipe)
        emsg2 = '    function = {0}'.format(func_name)
        WLOG(p, 'error', [emsg1, emsg2])
    # Get mask of recipe and apply it to control
    else:
        recipemask = control['Recipe'] == recipe
        control = control[recipemask]
    # ---------------------------------------------------------------------
    # file must exist to continue
    # ---------------------------------------------------------------------
    if not os.path.exists(filename):
        # get attempts at file name
        rawfile = os.path.join(rawpath, filename)
        tmpfile = os.path.join(tmppath, filename)
        reducedfile = os.path.join(reducedpath, filename)
        # if tmpfile exists we can narrow down the options
        if os.path.exists(tmpfile):
            filename = tmpfile
            # narrow down control options
            control = control[control['kind'] == 'RAW']
            kind = 'tmp'
        # if reducedfile exists we can narrow down the options
        elif os.path.exists(reducedfile):
            filename = reducedfile
            # narrow down control options
            control = control[control['kind'] == 'REDUC']
            kind = 'reduced'
        # if raw file exists we should make an error
        elif os.path.exists(rawfile):
            emsg1 = 'File {0} was found only in the RAW folder'.format(filename)
            emsg2 = ('\tFile is not pre-processed. Please run '
                     'cal_preprocess_spirou.py')
            emsg3 = '\tfunction = {0}'.format(func_name)
            WLOG(p, 'error', [emsg1, emsg2, emsg3])
            kind = 'None'
        # if neither exist we have a problem
        else:
            emsg1 = 'File {0} does not exist'.format(filename)
            emsg2 = '\tChecked raw and reduced folders.'
            emsg3 = '\tfunction = {0}'.format(func_name)
            WLOG(p, 'error', [emsg1, emsg2, emsg3])
            kind = 'None'
    else:
        kind = 'None'
    # make sure filename has no path
    basefilename = os.path.basename(filename)

    # check if we still have options
    if len(control) == 0:
        emsg1 = ('File "{0}" was found in the "{1}" directory.'
                 ''.format(basefilename, kind))
        emsg2 = 'Not a valid directory for recipe "{0}"'.format(recipe)
        WLOG(p, 'error', [emsg1, emsg2])

    # ---------------------------------------------------------------------
    # check recipe input type (raw or reduced)
    kinds = np.unique(control['kind'])
    # ---------------------------------------------------------------------
    # Need to check pre-processing
    # ---------------------------------------------------------------------
    # if we only have raw file possibilities check for pre-processing
    if len(kinds) == 1 and kinds[0] == 'RAW':
        if p['IC_FORCE_PREPROCESS']:
            check_preprocess(p, filename=filename)
            p['PREPROCESSED'] = True
        elif p['PROCESSED_SUFFIX'] in filename:
            p['PREPROCESSED'] = True
        else:
            p['PREPROCESSED'] = False
    else:
        p['PREPROCESSED'] = True
    # set preprocess source
    p.set_source('PREPROCESSED', func_name)
    # ---------------------------------------------------------------------
    # Identify file from header
    control = identify_from_header(p, control, recipe, filename, hdr)
    # ---------------------------------------------------------------------
    # check position if defined
    if pos is not None:
        basefilename = os.path.basename(filename)
        if control['number'] != (pos + 1):
            emsg1 = 'Recipe argument valid but in wrong position'
            eargs2 = [basefilename, pos + 1, control['number']]
            emsg2 = ('\tArgument "{0}" should not be in ARG{1}. '
                     'Should be ARG{2}'.format(*eargs2))
            eargs3 = [control['dprtype'], control['ocode']]
            emsg3 = '\tDPRTYPE="{0}" OCODE="{1}"'.format(*eargs3)
            emsg4 = '\t{0} [NIGHT NAME] [ARG1] [ARG2] [ARG3] [...]'
            WLOG(p, 'error', [emsg1, emsg2, emsg3,
                                         emsg4.format(recipe)])

    # ---------------------------------------------------------------------
    # now we should have 1 row in control --> get properties for this file
    p = get_properties_from_control(p, control)
    # ---------------------------------------------------------------------
    # if return recipe
    if return_path:
        # based on kind
        if control['kind'].upper() == 'RAW':
            path = tmppath
        elif control['kind'].upper() == 'REDUC':
            path = reducedpath
        else:
            emsg1 = 'Error in recipe control file'
            emsg2 = '   Bad line: "kind" must be "RAW" or "REDUC". Line:'
            line = control.__str__().split('\n')[2]
            WLOG(p, 'error', [emsg1, emsg2, line])
            path = ''
        # return p and path
        return p, path
    else:
        # return p
        return p


def check_files_id(p, files, recipe, hdr=None, **kwargs):
    """
    Wrapper for spirouFile.check_file_id

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            IC_FORCE_PREPROCESS: bool, if True only allows pre-processed files
            PROCESSED_SUFFIX: string, the processed suffix
            DRS_DATA_RAW: string, the directory that the raw data should
                          be saved to/read from
                DRS_DATA_REDUC: string, the directory that the reduced data
                                should be saved to/read from
            ARG_NIGHT_NAME: string, the folder within data raw directory
                            containing files (also reduced directory) i.e.
                            /data/raw/20170710 would be "20170710"
    :param files: list of strings, the files to check with check_file_id
    :param recipe: string, the recipe name to check
    :param hdr: dictionary or None, if defined must be a HEADER dictionary if
                none loaded from filename
    :param kwargs: keyword arguments. Current allowed keys are:
                    - return_path: bool, if True returns the path as well as p
    :return p: parameter dictionary, the updated parameter dictionary
        Adds the following:
            PREPROCESSED: bool, flag whether file is detected as
                          pre-processed
            DPRTYPE: string, the type from the recipe control file
            DPRTYPES: list of stings, the DPRTYPE for each file in "files"
            FIBER: string, if recipe control entry for this file has a
                   fiber defined, fiber is set to this
    """
    func_name = __NAME__ + '.check_files_id()'
    # add new constant (for multiple files)
    p['DPRTYPES'] = []
    # loop around filenames in files
    for filename in files:
        # check id for each file
        p = check_file_id(p, filename, recipe, hdr, **kwargs)
        # append DPRTYPE to DPRTYPES
        p['DPRTYPES'].append(str(p['DPRTYPE']))
    # Need to check that all DPRTYPES are the same
    if len(p['DPRTYPES']) == 0:
        p['DPRTYPE'] = 'UNKNOWN'
        return p
    elif len(np.unique(p['DPRTYPES'])) != 1:
        # add first error message
        emsgs = ['Files are not all the same type']
        # loop around files and print types
        for it, dprtype in enumerate(p['DPRTYPES']):
            basefilename = os.path.basename(files[it])
            eargs = [basefilename, dprtype]
            emsgs.append('\tFile {0} type={1}'.format(*eargs))
        # add function name error message
        emsgs.append('\tfunction = {0}'.format(func_name))
        # log error message
        WLOG(p, 'error', emsgs)
    else:
        # return p
        return p


def check_preprocess(p, filename=None):
    """
    Check "filename" for p["PREPROCESS_SUFFIX"]. If filename is None uses
    p["FITSFILENAME"]

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            PREPROCESS_SUFFIX: string, the suffix to look for and should be
                               in filename if 'IC_FORCE_PREPROCESS' is True
            IC_FORCE_PREPROCESS: bool, if True filename must have
                                 PREPROCESS_SUFFIX
            fitsfilename: string, the full path of for the main raw fits
                          file for a recipe
                          i.e. /data/raw/20170710/filename.fits

    :param filename: string or None, if defined must be a filename to check
                     if None filename = p['FITSFILENAME']

    :return checked: bool, True if file passes
                           False if IC_FORCE_PREPROCESS is  False and file
                           fails to find PREPROCESS_SUFFIX

                           or WLOG error if fails and IC_FORCE_PREPROCESS is
                           True and file fails to find PREPROCESS_SUFFIX
    """
    func_name = __NAME__ + '.check_preprocess()'
    # get the suffix
    suffix = p['PROCESSED_SUFFIX']
    # get the filename
    if filename is None:
        filename = p['FITSFILENAME']
    # make sure filename does not include a path
    filename = os.path.basename(filename)
    # check for the pre-process key
    if p['IC_FORCE_PREPROCESS']:
        # check that we have a suffix to check
        if suffix == "None":
            wmsg = 'Not checking for pre-processed file={0}'.format(filename)
            WLOG(p, '', wmsg)
            return 0
        # else check file ends with
        elif filename.endswith(suffix):
            wmsg = 'Pre-processing valid for file={0}'.format(filename)
            WLOG(p, '', wmsg)
            return 1
        # else generate helpful error
        else:
            emsgs = ['File not processed. Suffix="{0}" not '
                     'found.'.format(suffix),
                     '\tRun "cal_preprocess_spirou" or turn off '
                     '"IC_FORCE_PREPROCESS"',
                     '\t\tfile = {0}'.format(filename),
                     '\t\tfunction = {0}'.format(func_name)]
            WLOG(p, 'error', emsgs)


def fiber_params(pp, fiber, merge=False):
    """
    Takes the parameters defined in FIBER_PARAMS from parameter dictionary
    (i.e. from config files) and adds the correct parameter to a fiber
    parameter dictionary

    :param pp: parameter dictionary, ParamDict containing constants
        Must contain at least:
                log_opt: string, log option, normally the program name

    :param fiber: string, the fiber type (and suffix used in confiruation file)
                  i.e. for fiber AB fiber="AB" and nbfib_AB should be present
                  in config if "nbfib" is in FIBER_PARAMS
    :param merge: bool, if True merges with pp and returns

    :return fparam: dictionary, the fiber parameter dictionary (if merge False)
    :treun pp: dictionary, paramter dictionary (if merge True)
    """
    # get dictionary parameters for suffix _fpall
    try:
        fparams = spirouConfig.ExtractDictParams(pp, '_fpall', fiber,
                                                 merge=merge)
    except ConfigError as e:
        WLOG(pp, e.level, e.message)
        fparams = ParamDict()
    # return fiber dictionary
    return fparams


# =============================================================================
# Define worker functions
# =============================================================================
def get_control_file(p):
    # get SpirouDRS data folder
    package = spirouConfig.Constants.PACKAGE()
    relfolder = spirouConfig.Constants.DATA_CONSTANT_DIR()
    datadir = spirouConfig.GetAbsFolderPath(package, relfolder)
    # construct the path for the control file
    controlfn, controlfmt = spirouConfig.Constants.RECIPE_CONTROL_FILE()
    controlfile = os.path.join(datadir, controlfn)
    # load control file
    control = spirouTable.read_table(p, controlfile, fmt=controlfmt,
                                     comment='#')
    # return control
    return control


def get_header_file(p, filename, hdr=None):
    func_name = __NAME__ + '.get_header_file()'
    # get header if None
    if hdr is None:
        if not os.path.exists(filename):
            emsg1 = 'Cannot read header. File does not exist ({0})'
            emsg2 = '    fuction = {0}'.format(func_name)
            WLOG(p, 'error', [emsg1.format(filename), emsg2])
        else:
            hdr = spirouFITS.read_header(p, filename)
    # return header and comments
    return hdr


def get_properties_from_control(p, control):
    # ----------------------------------------------------------------------
    # Get DPRTYPE
    p['DPRTYPE'] = control['dprtype']
    # Get DRS_TYPE (RAW or REDUCED)
    p['DRS_TYPE'] = control['kind']
    # ----------------------------------------------------------------------
    # Get FIBER and fiber parameters
    if control['fiber'] != 'None':
        p['FIBER'] = control['fiber']
        p = fiber_params(p, p['FIBER'], merge=True)
        if p['DRS_DEBUG']:
            # log that fiber was identified
            wmsg = 'Identified file as {0}, fiber={1}'
            WLOG(p, '', wmsg.format(p['DPRTYPE'], p['FIBER']))
    else:
        p['FIBER'] = None
        if p['DRS_DEBUG']:
            # log that fiber was identified
            wmsg = 'Identified file as {0}'
            WLOG(p, '', wmsg.format(p['DPRTYPE']))
    # ----------------------------------------------------------------------
    # return p
    return p


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
    # func_name = __NAME__ + '.odometer_header()'
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


def id_mode(p, control, filename, hdr, code, obstype, ccas, cref):
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
        wmsg = 'File "{0}" identified as "{1}"'
        WLOG(p, 'info', wmsg.format(basefilename, dprtype))
        # log mode (in debug mode)
        if p['DRS_DEBUG'] > 0:
            wmsg = '\tID via HEADER   OCODE={0} OBSTYPE={1} CCAS={2} CREF={3}'
            WLOG(p, '', wmsg.format(code, obstype, ccas, cref))
        # add key to header
        hdr[p['KW_DPRTYPE'][0]] = (dprtype.strip(), p['KW_DPRTYPE'][2])
        # update filename (if required)
        newfilename = str(filename)
        # now try updating filename
        if p['PP_MODE'] == 0:
            return newfilename, hdr
        elif (dstring == 'None') and (dstring not in basefilename):
            # try setting dstring to OBSTYPE
            if p['kw_OBJNAME'][0] in hdr:
                # get the name of the object
                name = spirouFITS.get_good_object_name(p, hdr)
                # need to replace do
                # if name not in filename add if
                if name not in filename:
                    newext = '_{0}.fits'.format(name)
                    newfilename = filename.replace('.fits', newext)
        elif dstring not in basefilename:
            newext = '_{0}.fits'.format(dstring)
            newfilename = filename.replace('.fits', newext)
        # return new filename and header
        return newfilename, hdr
    else:
        # deal with no match
        emsg1 = ('File {0} not identified as a valid DRS input.'
                 ''.format(basefilename))
        emsg2 = ('\tOCODE={0} OBSTYPE={1} CCAS={2} CREF={3}'
                 ''.format(code, obstype, ccas, cref))
        WLOG(p, 'warning', [emsg1, emsg2])

        # add key to header
        hdr[p['KW_DPRTYPE'][0]] = ('UNKNOWN', p['KW_DPRTYPE'][2])

        return filename, hdr


def find_match(control, code, obstype, ccas, cref):
    # get obs, ccas and cref types
    codes = control['ocode']
    obs_types = control['obstype']
    ccas_types = control['ccas']
    cref_types = control['cref']
    dprtype = control['dprtype']
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
        c4 = dprtype[c_it] == 'None'
        # if all three types are None skip
        if c0 and c1 and c2 and c3:
            continue
        # if dprtype is None skip (this is not an identification)
        if c4:
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


def identify_from_header(p, control, recipe, filename, hdr=None):
    func_name = __NAME__ + '.identify_from_header()'
    # get base filename (no path)
    bfilename = os.path.basename(filename)
    # -----------------------------------------------------------------------
    # get header
    # -----------------------------------------------------------------------
    # make sure we have header
    hdr = get_header_file(p, filename, hdr)
    # -----------------------------------------------------------------------
    # get control values
    # -----------------------------------------------------------------------
    kinds = np.unique(control['kind'])
    dprtypes = np.array(control['dprtype'])
    ocodes = np.array(control['ocode'])

    # -----------------------------------------------------------------------
    # get KW_DPRTYPE value
    # -----------------------------------------------------------------------
    # check if we are looking for a RAW file
    if kinds[0].upper() == 'RAW':
        # check for KW_DPRTYPE in header
        if p['KW_DPRTYPE'][0] in hdr:
            dprtype = hdr[p['KW_DPRTYPE'][0]].strip()
        # if we don't have it, obtain it
        else:
            _, hdr = identify_unprocessed_file(p, filename, hdr=None)
            dprtype = hdr[p['KW_DPRTYPE'][0]].strip()
    # else check that we are looking for a REDUC file
    elif kinds[0].upper() == 'REDUC':
        # check for KW_EXT_TYPE in header
        if p['kw_EXT_TYPE'][0] in hdr:
            dprtype = hdr[p['kw_EXT_TYPE'][0]].strip()
        # if it doesn't exist set this to None
        else:
            emsg1 = ('File {0} must be the output of the extraction process'
                     ''.format(bfilename))
            emsg2 = ('\tCould not find header key "{0}"'
                     ''.format(p['kw_EXT_TYPE'][0]))
            emsg3 = ('\tPlease re-run extraction OR use a valid extraction '
                     'output')
            WLOG(p, 'error', [emsg1, emsg2, emsg3])
            dprtype = None
    # else crash
    else:
        emsg1 = 'Error in recipe control file. Kind must be "RAW" or "REDUC"'
        emsg2 = '\tfunction = {0}'.format(func_name)
        WLOG(p, 'error', [emsg1, emsg2])
        dprtype = None
    # -----------------------------------------------------------------------
    # get KW_OUTPUT value
    # -----------------------------------------------------------------------
    # check for kw_OUTPUT
    if p['kw_OUTPUT'][0] in hdr:
        output = hdr[p['kw_OUTPUT'][0]]
    else:
        output = None

    # -----------------------------------------------------------------------
    # Identify based on output and dprtype
    # -----------------------------------------------------------------------
    # if None in dprtypes and we expect a RAW file: do not check
    if ('None' in dprtypes) and (kinds[0].upper() == 'RAW'):
        # get the first row in control where dprtype == 'None'
        row = np.where(dprtypes == 'None')[0][0]
        # filter control by this row
        control = control[row]
        # print warning
        wmsg = 'DPRTYPE not checked for recipe="{0}"'.format(recipe)
        WLOG(p, 'warning', wmsg)
    # -----------------------------------------------------------------------
    # if output is None and dprtype exists: we have a raw file
    elif (output is None) and (dprtype in dprtypes):
        # get the first row in control where dprtype is valid
        row = np.where(dprtypes == dprtype)[0][0]
        # filter control by this row
        control = control[row]
        # log identification
        wmsg = 'Input identification: {0} (TYPE={1})'.format('RAW', dprtype)
        WLOG(p, '', wmsg)

    # -----------------------------------------------------------------------
    # if output is None and we expect a RAW file: we have the wrong file
    elif (output is None) and (kinds[0].upper() == 'RAW'):
        emsg1 = 'File "{0}" identified as "{1}"'.format(bfilename, dprtype)
        emsg2 = '\tNot valid for recipe "{0}"'.format(recipe)
        emsg3 = '\tError was: WRONG DPRTYPE'
        WLOG(p, 'error', [emsg1, emsg2, emsg3])
    # -----------------------------------------------------------------------
    # if output is None and we expect a REDUC file: we are missing the
    #     header key
    elif (output is None) and (kinds[0].upper() == 'REDUC'):
        emsg1 = 'File "{0}" identified as "{1}"'.format(bfilename, dprtype)
        emsg2 = ('\tHeader key "{0}" missing! Please re-run extraction'
                 '').format(p['kw_OUTPUT'][0])
        emsg3 = '\tError was: OUTPUT HEADER KEY MISSING'
        WLOG(p, 'error', [emsg1, emsg2, emsg3])
    # -----------------------------------------------------------------------
    # if we have an output and expect a REDUCE file: then we have a reduc file
    elif (output is not None) and (kinds[0].upper() == 'REDUC'):
        # ++++++++++++++++++++++++++
        # Cond1: Check output
        # ++++++++++++++++++++++++++
        # if we have a None in ocodes: skip ocode check
        if 'None' in ocodes:
            cond1 = np.ones(len(ocodes), dtype=bool)
            # print warning
            wargs = [p['kw_OUTPUT'][0], recipe]
            wmsg = 'ID ({0}) not checked for recipe="{1}"'
            WLOG(p, 'warning', wmsg.format(*wargs))
        # else if we have the output in ocodes use this
        elif output in ocodes:
            # condition 1:
            cond1 = output == ocodes
        # else we have not found the right code
        else:
            emsg1 = 'File "{0}" output="{1}"'.format(bfilename, output)
            emsg2 = '\tNot valid for recipe "{0}"'.format(recipe)
            emsg3 = '\tError was: WRONG ID ({0})'.format(output)
            WLOG(p, 'error', [emsg1, emsg2, emsg3])
            cond1 = False
        # ++++++++++++++++++++++++++
        # Cond2: Check DPRTYPE
        # ++++++++++++++++++++++++++
        # if we have a None in dprtypes: skip dprtype check
        if 'None' in dprtypes:
            cond2 = np.ones(len(dprtypes), dtype=bool)
            # print warning
            wargs = [p['kw_EXT_TYPE'][0], recipe]
            wmsg = 'TYPE ({0}) not checked for recipe="{1}"'
            WLOG(p, 'warning', wmsg.format(*wargs))

        # if we didn't find a dprtype due to missing header key skip
        elif (dprtype is None) or (dprtype == 'None'):
            cond2 = np.ones(len(dprtypes), dtype=bool)
            # print warning
            wargs = [p['kw_EXT_TYPE'][0], recipe]
            wmsg = 'TYPE ({0}) not checked for recipe="{1}"'
            WLOG(p, 'warning', wmsg.format(*wargs))
        elif dprtype in dprtypes:
            # condition 2:
            cond2 = dprtype == dprtypes
        else:
            emsg1 = 'File "{0}" TYPE="{1}"'.format(bfilename, dprtype)
            emsg2 = '\tNot valid for recipe "{0}"'.format(recipe)
            emsg3 = '\tError was: WRONG TYPE ({0})'.format(p['kw_EXT_TYPE'][0])
            WLOG(p, 'error', [emsg1, emsg2, emsg3])
            cond2 = False
        # ++++++++++++++++++++++++++
        # Check we still have rows
        # ++++++++++++++++++++++++++
        if np.sum(cond1 & cond2) == 0:
            emsg1 = 'File "{0}" ID="{1}"'.format(bfilename, dprtype)
            emsg2 = '\tNot valid for recipe "{0}"'.format(recipe)
            emsg3 = '\tError was: NONE FOUND ({0})'.format(output)
            WLOG(p, 'error', [emsg1, emsg2, emsg3])

        # ++++++++++++++++++++++++++
        # Filter by cond1 and cond2
        # ++++++++++++++++++++++++++
        # filter by row
        row = np.where(cond1 & cond2)[0][0]
        # filter control by this row
        control = control[row]

        # log identification
        wmsg = 'Input identification: {0} (ID={1}, TYPE={2})'
        WLOG(p, '', wmsg.format('REDUC', output, dprtype))
    # -----------------------------------------------------------------------
    # else we have hit an unexpected error
    else:
        emsg1 = 'File "{0}" identified as "{1}"'.format(bfilename, dprtype)
        emsg2 = '\tOutput type = {0}'.format(output)
        emsg3 = '\tUnknown error occurred'
        WLOG(p, 'error', [emsg1, emsg2, emsg3])

    return control


def strip_string_list(string_list):
    new_list = []
    # make sure list is list
    if type(string_list) in [str, int, float, complex, bool]:
        string_list = [string_list]

    # strip elements in list
    for list_item in string_list:
        new_list.append(list_item.strip())
    # return new list
    return new_list


def fallback_id_mode(p, control, filename, hdr):
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
            wmsg = 'File "{0}" identified as "{1}"'
            WLOG(p, 'info', wmsg.format(basefilename, dprtype))
            # log mode (in debug mode)
            if p['DRS_DEBUG'] > 0:
                wmsg = '\tID via filename   file={0}'
                WLOG(p, '', wmsg.format(basefilename))
            # update header key 'DPRTYPE
            hdr[p['KW_DPRTYPE'][0]] = (dprtype.strip(), p['KW_DPRTYPE'][2])
            # return original filename and header
            return filename, hdr
    # if file not found log this
    emsg = 'File "{0}" not identified as a valid DRS input.'
    WLOG(p, 'warning', emsg.format(basefilename))
    # update header key 'DPRTYPE
    hdr[p['KW_DPRTYPE'][0]] = ('UNKNOWN', p['KW_DPRTYPE'][2])
    return filename, hdr


# TODO: Not used
def check_id_filename(p, control, recipe, filename):
    # func_name = __NAME__ + '.check_id_filename()'
    # set un-found initial parameters
    found = False
    found_row = None

    dprtypes = list(control['dprtype'])

    # loop around rows in control
    for row in range(len(control)):
        # skip if already found
        if found:
            continue
        # get this iterations values
        kind = control['kind'][row]
        # ------------------------------------------------------------------
        # deal with reduced files
        if kind.upper() == 'REDUC':
            found, dprtype = check_reduced_filename(p, filename, recipe,
                                                    control[row])
            # Need to set a new dprtype if reduced file
            if found:
                dprtypes[row] = dprtype
        # ------------------------------------------------------------------
        # deal with None
        elif kind.upper() == 'RAW':
            found = check_raw_filename(p, filename, recipe, control[row])
        # ------------------------------------------------------------------
        # if filename is found remember row
        if found:
            found_row = int(row)

    # reassign control['dprtype'] to dprtypes
    #     (needed as list before due to strings changing size)
    control['dprtype'] = dprtypes
    # deal with no file found
    if not found:
        return found, control
    # if file found return row of control found in
    else:
        return found, control[found_row]


# TODO: Not used?
def check_id_header(p, control, recipe, filename, hdr=None):
    # get base filename (no path)
    basefilename = os.path.basename(filename)
    # load header
    hdr = get_header_file(p, filename, hdr)
    # check for DPRTYPE in header
    if p['KW_DPRTYPE'][0] in hdr:
        dprtype = hdr[p['KW_DPRTYPE'][0]]
    # if we don't have it, obtain it
    else:
        _, hdr = identify_unprocessed_file(p, filename, hdr=None)
        dprtype = hdr[p['KW_DPRTYPE'][0]]
    # -----------------------------------------------------------------------
    # Only should be looking at the raw file for header info
    # -----------------------------------------------------------------------
    # we should not be here with anything but raw files
    kinds = np.unique(control['kind'])
    if (len(kinds) != 1) and (kinds[0].upper() != 'RAW'):
        emsg1 = 'File "{0}" not identified (not a raw file)'
        emsg2 = 'Only raw files valid for recipe "{0}"'.format(recipe)
        WLOG(p, 'error', [emsg1, emsg2])
    # -----------------------------------------------------------------------
    # use dprtype to select a single control setting
    # -----------------------------------------------------------------------
    # if DPRTYPE is None then let all files through
    if 'None' in control['dprtype'] and kinds[0].upper() == 'RAW':
        # get the first row in control where dprtype == 'None'
        row = np.where(control['dprtype'] == 'None')[0][0]
        # filter control by this row
        control = control[row]
        # print warning
        wmsg = 'DPRTYPE not checked for recipe="{0}"'.format(recipe)
        WLOG(p, 'warning', wmsg)
    # else if DPRTYPE not in dprtypes then give error
    elif dprtype not in control['dprtype']:
        emsg1 = 'File "{0}" identified as "{1}"'.format(basefilename, dprtype)
        emsg2 = 'Not valid for recipe "{0}"'.format(recipe)
        WLOG(p, 'error', [emsg1, emsg2])
    # else we have the correct DPRTYPE --> select correct row of control
    else:
        # get the first row in control where dprtype is valid
        row = np.where(control['dprtype'] == dprtype)[0][0]
        # filter control by this row
        control = control[row]
    # return control
    return control


# TODO: Not used?
def check_reduced_filename(p, filename, recipe, control):
    # get variables from control
    dstring = control['dstring']
    ocode = control['ocode']
    dprtype = control['dprtype']
    desc = control['desc'].replace(' ', '_')
    # check for None
    c0 = dprtype == 'None'
    c1 = dstring == 'None'
    c2 = ocode == 'None'
    # if both are None log warning
    if c1 and c2:
        wmsg = 'Filename not checked for recipe="{0}" (reduced file)'
        WLOG(p, 'warning', wmsg.format(recipe))
    # check dstring in filename
    if not c1:
        cond1 = dstring in filename
    else:
        cond1 = True
    # check ocode in filename
    if not c2:
        cond2 = ocode in filename
    else:
        cond2 = True
    # are conditions met?
    found = cond1 and cond2

    # set dprtype if we don't have one
    if c0:
        # add desc
        dprtype = desc
        # add dstring (if we have it)
        if not c1:
            dprtype += '_{0}'.format(dstring)
        # add ocode (if we have it)
        if not c2:
            dprtype += '_{0}'.format(ocode)

    # return found
    return found, dprtype


# TODO: Not used?
def check_raw_filename(p, filename, recipe, control):
    # get variables from control
    dstring = control['dstring']
    # check for None
    c1 = dstring == 'None'
    # if both are None log warning
    if c1:
        wmsg = 'Filename not checked for recipe="{0}" (raw file)'
        WLOG(p, 'warning', wmsg.format(recipe))
    # check dstring in filename
    if not c1:
        cond1 = dstring in filename
    else:
        cond1 = True
    # are conditions met?
    found = cond1
    # return found
    return found


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
