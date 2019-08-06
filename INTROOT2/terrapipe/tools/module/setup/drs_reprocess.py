#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-08-06 at 11:57

@author: cook
"""
import numpy as np
import sys
import os
from astropy.table import Table
from collections import OrderedDict

from terrapipe import core
from terrapipe.core.core import drs_startup
from terrapipe import locale
from terrapipe.core import constants
from terrapipe.io import drs_table
from terrapipe.io import drs_path
from terrapipe.io import drs_fits
from terrapipe.tools.module.setup import drs_reset



# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tools.module.setup.drs_reprocess.py'
__INSTRUMENT__ = None
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# Get Logging function
WLOG = core.wlog
# get the parameter dictionary
ParamDict = constants.ParamDict
# Get the text types
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict
# alias pcheck
pcheck = core.pcheck


# =============================================================================
# Define user functions
# =============================================================================
def runfile(params, runfile, **kwargs):
    func_name = __NAME__ + '.read_run_file()'
    # ----------------------------------------------------------------------
    # get properties from params
    run_key = pcheck(params, 'REPROCESS_RUN_KEY', 'run_key', kwargs, func_name)
    run_dir = pcheck(params, 'DRS_DATA_RUN', 'run_dir', kwargs, func_name)
    # ----------------------------------------------------------------------
    # check if run file exists
    if not os.path.exists(runfile):
        # construct run file
        runfile = os.path.join(run_dir, runfile)
        # check that it exists
        if not os.path.exists(runfile):
            WLOG(params, 'error', TextEntry('09-503-00002', args=[runfile]))
    # ----------------------------------------------------------------------
    # now try to load run file
    try:
        keys, values = np.loadtxt(runfile, delimiter='=', comments='#',
                                  unpack=True, dtype=str)
    except Exception as e:
        # log error
        eargs = [runfile, type(e), e, func_name]
        WLOG(params, 'error', TextEntry('09-503-00003', args=eargs))
        keys, values = [], []
    # ----------------------------------------------------------------------
    # table storage
    runtable = OrderedDict()
    keytable = OrderedDict()
    # sort out keys into id keys and values for p
    for it in range(len(keys)):
        # get this iterations values
        key = keys[it].upper().strip()
        value = values[it].strip()
        # find the id keys
        if key.startswith(run_key):
            # attempt to read id string
            try:
                runid = int(key.replace(run_key, ''))
            except Exception as e:
                eargs = [key, value, run_key, type(e), e, func_name]
                WLOG(params, 'error', TextEntry('09-503-00004', args=eargs))
                runid = None
            # check if we already have this column
            if runid in runtable:
                wargs = [runid, keytable[runid], runtable[runid],
                         keys[it], values[it][:40] + '...']
                WLOG(params, 'warning', TextEntry('10-503-00001', args=wargs))
            # add to table
            runtable[runid] = value
            keytable[runid] = key
        # else add to parameter dictionary
        else:
            # deal with special strings
            if value.upper() == 'TRUE':
                value = True
            elif value.upper() == 'FALSE':
                value = False
            elif value.upper() == 'NONE':
                value = None
            # log if we are overwriting value
            if key in params:
                wargs = [key, params[key], value]
                WLOG(params, 'warning', TextEntry('10-503-00002', args=wargs))
            # add to params
            params[key] = value
            params.set_source(key, func_name)
    # ----------------------------------------------------------------------
    # return parameter dictionary and runtable
    return params, runtable


def send_email(params, kind):
    func_name = __NAME__ + '.send_email()'
    # ----------------------------------------------------------------------
    # get text dict
    textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
    # ----------------------------------------------------------------------
    # check whether send email
    if not params['SEND_EMAIL']:
        return 0
    # ----------------------------------------------------------------------
    # try to import yagmail
    try:
        import yagmail
        YAG = yagmail.SMTP(params['EMAIL_ADDRESS'])
    except ImportError:
        WLOG(params, 'error', TextEntry('00-503-00001'))
        YAG = None
    except Exception as e:
        eargs = [type(e), e, func_name]
        WLOG(params, 'error', TextEntry('00-503-00002', args=eargs))
        YAG = None
    # ----------------------------------------------------------------------
    # deal with kind = start
    if kind == 'start':
        receiver = params['EMAIL_ADDRESS']
        iname = '{0}-DRS'.format(params['INSTRUMENT'])
        sargs = [iname, __NAME__, params['PID']]
        subject = textdict['40-503-00001'].format(*sargs)
        body = ''
        for logmsg in WLOG.pout['LOGGER_ALL']:
            body += '{0}\t{1}\n'.format(*logmsg)
    # ----------------------------------------------------------------------
    # deal with kind = end
    elif kind == 'end':
        receiver = params['EMAIL_ADDRESS']
        iname = '{0}-DRS'.format(params['INSTRUMENT'])
        sargs = [iname, __NAME__, params['PID']]
        subject = textdict['40-503-00002'].format(*sargs)
        body = ''
        for logmsg in params['LOGGER_FULL']:
            for log in logmsg:
                body += '{0}\t{1}\n'.format(*log)
    # ----------------------------------------------------------------------
    # else do not send email
    else:
        return 0
    # ----------------------------------------------------------------------
    # send via YAG
    YAG.send(to=receiver, subject=subject, contents=body)


def reset(params):
    """
    Resets based on reset parameters

    :param params: ParamDict, the parameter dictionary

    :type params: ParamDict

    :returns: None
    """
    if not params['RESET_ALLOWED']:
        return 0
    if params['RESET_TMP']:
        reset = drs_reset.reset_confirmation(params, 'tmp')
        if reset:
            drs_reset.reset_tmp_folders(params, log=True)
    if params['RESET_REDUCED']:
        reset = drs_reset.reset_confirmation(params, 'reduced')
        if reset:
            drs_reset.reset_reduced_folders(params, log=True)
    if params['RESET_CALIB']:
        reset = drs_reset.reset_confirmation(params, 'calibration')
        if reset:
            drs_reset.reset_calibdb(params, log=True)
    if params['RESET_TELLU']:
        reset = drs_reset.reset_confirmation(params, 'telluric')
        if reset:
            drs_reset.reset_telludb(params, log=True)
    if params['RESET_LOG']:
        reset = drs_reset.reset_confirmation(params, 'log')
        if reset:
            drs_reset.reset_log(params)
    if params['RESET_PLOT']:
        reset = drs_reset.reset_confirmation(params, 'plot')
        if reset:
            drs_reset.reset_plot(params)


def find_raw_files(params, **kwargs):
    func_name = __NAME__ + '.find_raw_files()'
    # get properties from params
    night_col = pcheck(params, 'REPROCESS_NIGHTCOL', 'night_col', kwargs,
                       func_name)
    absfile_col = pcheck(params, 'REPROCESS_ABSFILECOL', 'absfile_col', kwargs,
                         func_name)
    modified_col = pcheck(params, 'REPROCESS_MODIFIEDCOL', 'modified_col',
                          kwargs, func_name)
    sortcol = pcheck(params, 'REPROCESS_SORTCOL_HDRKEY', 'sortcol', kwargs,
                     func_name)
    raw_index_file = pcheck(params, 'REPROCESS_RAWINDEXFILE', 'raw_index_file',
                            kwargs, func_name)
    itable_filecol = pcheck(params, 'DRS_INDEX_FILENAME', 'itable_filecol',
                            kwargs, func_name)
    # get path
    path, rpath = get_path_and_check(params, 'DRS_DATA_RAW')
    # get files
    gfout = get_files(params, path, rpath)
    nightnames, filelist, basenames, mod_times, kwargs = gfout
    # construct a table
    mastertable = Table()
    mastertable[night_col] = nightnames
    mastertable[itable_filecol] = basenames
    mastertable[absfile_col] = filelist
    mastertable[modified_col] = mod_times
    for kwarg in kwargs:
        mastertable[kwarg] = kwargs[kwarg]
    # sort by sortcol
    sortmask = np.argsort(mastertable[sortcol])
    mastertable = mastertable[sortmask]
    # save master table
    mpath = os.path.join(params['DRS_DATA_RUN'], raw_index_file)
    mastertable.write(mpath, overwrite=True)
    # return the file list
    return mastertable, rpath


def generate_run_list(params, table, path, runtable):
    # get all values (upper case) using map function
    rvalues = list(map(lambda x: x.upper(), runtable.values()))
    # sort out which mode we are in
    if 'ALL' in rvalues:
        return generate_all(params, table, path)
    else:
        return generate_ids(params, table, path, runtable)


# =============================================================================
# Define working functions
# =============================================================================
def get_path_and_check(params, key):
    # check key in params
    if key not in params:
        WLOG(params, 'error', '{0} not found in params'.format(key))
    # get top level path to search
    rpath = params[key]
    if params['NIGHT_NAME'] is not None and params['NIGHT_NAME'] != '':
        path = os.path.join(rpath, params['NIGHT_NAME'])
    else:
        path = str(rpath)
    # check if path exists
    if not os.path.exists(path):
        WLOG(params, 'error', 'Path {0} does not exist'.format(path))
    else:
        return path, rpath


def get_files(params, path, rpath, **kwargs):
    func_name = __NAME__ + '.get_files()'
    # get properties from params
    absfile_col = pcheck(params, 'REPROCESS_ABSFILECOL', 'absfile_col', kwargs,
                         func_name)
    modified_col = pcheck(params, 'REPROCESS_MODIFIEDCOL', 'modified_col',
                          kwargs, func_name)
    raw_index_file = pcheck(params, 'REPROCESS_RAWINDEXFILE', 'raw_index_file',
                            kwargs, func_name)
    # ----------------------------------------------------------------------
    # get the pseudo constant object
    pconst = constants.pload(params['INSTRUMENT'])
    # get header keys
    headerkeys = pconst.RAW_OUTPUT_KEYS()
    # get raw valid files
    raw_valid = pconst.VALID_RAW_FILES()
    # ----------------------------------------------------------------------
    # storage list
    filelist, basenames, nightnames, mod_times = [], [], [], []
    # load raw index
    rawindexfile = os.path.join(params['DRS_DATA_RUN'], raw_index_file)
    if os.path.exists(rawindexfile):
        rawindex = drs_table.read_table(params, rawindexfile, fmt='fits')
    else:
        rawindex = None
    # ----------------------------------------------------------------------
    # populate the storage dictionary
    kwargs = dict()
    for key in headerkeys:
        kwargs[key] = []
    # ----------------------------------------------------------------------
    # get files (walk through path)
    for root, dirs, files in os.walk(path):
        # loop around files in this root directory
        for filename in files:
            # --------------------------------------------------------------
            # get night name
            ucpath = drs_path.get_uncommon_path(root, rpath)
            if ucpath is None:
                eargs = [path, rpath, func_name]
                WLOG(params, 'error', TextEntry('00-503-00003', args=eargs))
            # --------------------------------------------------------------
            # make sure file is valid
            isvalid = False
            for suffix in raw_valid:
                if filename.endswith(suffix):
                    isvalid = True
            # --------------------------------------------------------------
            # do not scan empty ucpath
            if len(ucpath) == 0:
                continue
            # --------------------------------------------------------------
            # log the night directory
            if ucpath not in nightnames:
                WLOG(params, '', TextEntry('40-503-00003', args=[ucpath]))
            # --------------------------------------------------------------
            # get absolute path
            abspath = os.path.join(root, filename)
            modified = os.path.getmtime(abspath)
            # --------------------------------------------------------------
            # if not valid skip
            if not isvalid:
                continue
            # --------------------------------------------------------------
            # else append to list
            else:
                nightnames.append(ucpath)
                filelist.append(abspath)
                basenames.append(filename)
                mod_times.append(modified)
            # --------------------------------------------------------------
            # see if file in raw index and has correct modified date
            if rawindex is not None:
                # find file
                rowmask = (rawindex[absfile_col] == abspath)
                # find match date
                rowmask &= modified == rawindex[modified_col]
                # only continue if both conditions found
                if np.sum(rowmask) > 0:
                    # locate file
                    row = np.where(rowmask)[0][0]
                    # if both conditions met load from raw fits file
                    for key in headerkeys:
                        kwargs[key].append(rawindex[key][row])
                    # file was found
                    rfound = True
                else:
                    rfound = False
            else:
                rfound = False
            # --------------------------------------------------------------
            # deal with header
            if filename.endswith('.fits') and not rfound:
                # read the header
                header = drs_fits.read_header(params, abspath)
                # loop around header keys
                for key in headerkeys:
                    rkey = params[key][0]
                    if rkey in header:
                        kwargs[key].append(header[rkey])
                    else:
                        kwargs[key].append('')
    # ----------------------------------------------------------------------
    # return filelist
    return nightnames, filelist, basenames, mod_times, kwargs


# =============================================================================
# Define classes
# =============================================================================
class Run:
    def __init__(self, params, runstring, priority=0):
        self.params = params
        self.runstring = runstring
        self.priority = priority
        # get args
        self.args = runstring.split(' ')
        # the first argument must be the recipe name
        self.recipename = self.args[0]
        # find the recipe
        self.recipe = self.find_recipe()
        # import the recipe module
        self.recipemod = self.recipe.main
        # turn off the input validation
        self.recipe.input_validation = False
        # run parser with arguments
        self.kwargs = self.recipe.recipe_setup(inargs=self.args)
        # turn on the input validation
        self.recipe.input_validation = True
        # set parameters
        self.nightname = self.kwargs['directory']
        self.argstart = None
        self.kind = None
        # get properties
        self.get_recipe_kind()

    def find_recipe(self):
        # find the recipe definition
        recipe = drs_startup.find_recipe(self.recipename,
                                         self.params['INSTRUMENT'])
        # deal with an empty recipe return
        if recipe.name == 'Empty':
            eargs = [self.recipename]
            WLOG(None, 'error', TextEntry('00-007-00001', args=eargs))
        # else return
        return recipe

    def get_recipe_kind(self):
        # the first argument must be the recipe name
        self.recipename = self.args[0]
        # make sure recipe does not have .py on the end
        self.recipename = remove_py(self.recipename)
        # get recipe type (raw/tmp/reduced)
        if self.recipe.inputdir == 'raw':
            self.kind = 0
        elif self.recipe.inputdir == 'tmp':
            self.kind = 1
        elif self.recipe.inputdir == 'reduced':
            self.kind = 2
        else:
            emsg1 = ('RunList Error: Recipe = "{0}" invalid'
                     ''.format(self.recipename))
            emsg2 = '\t Line: {0} {1}'.format(self.priority, self.runstring)
            WLOG(self.params, 'error', [emsg1, emsg2])
            self.kind = -1

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return 'Run[{0}]'.format(self.runstring)



# TODO: ----------------------------------
# TODO:  Continue here
# TODO: ----------------------------------


# =============================================================================
# Define "from id" functions
# =============================================================================
def generate_ids(params, tables, paths, runtable):
    # should just need to sort these
    numbers = np.array(list(runtable.keys()))
    commands = np.array(list(runtable.values()))
    # sort by number
    sortmask = np.argsort(numbers)
    # get sorted run list
    runlist = list(commands[sortmask])
    keylist = list(numbers[sortmask])
    # iterate through and make run objects
    run_objects = []
    for it, run_item in enumerate(runlist):
        # create run object
        run_object = Run(params, run_item, priority=keylist[it])
        # append to list
        run_objects.append(run_object)
    # check list files against tables and assign a group
    run_objects = check_runlist(params, run_objects)

    # return run objects
    return run_objects


def check_runlist(params, runlist):
    # ------------------------------------------------------------------
    # storage of outlist
    out_runlist = []
    # ------------------------------------------------------------------
    for it, run_item in enumerate(runlist):
        # check that we want to run this recipe
        check1 = False
        # ------------------------------------------------------------------
        # find run_item in MOD_LIST
        for key in MOD_LIST:
            # get run_key
            runkey = 'RUN_{0}'.format(key)
            rl_item = MOD_LIST[key][0]
            # check if recipe names agree
            cond1 = run_item.recipename == remove_py(rl_item.__NAME__)
            # check if key in params
            cond2 = runkey in params
            # if both conditions met then we take the condition from params
            if cond1 and cond2:
                check1 = params[runkey]
                break
            # if we don't have key in params and key isn't in MOD_LIST we should
            #   just pass
            elif not (cond1 and cond2):
                check1 = True
                break
        # ------------------------------------------------------------------
        # check that we have files and if we want to skip them
        check2 = True
        # find run_item in MOD_LIST
        for key in MOD_LIST:
            # get run_key
            runkey = 'SKIP_{0}'.format(key)
            sl_item = SKIP_LIST[key][0]
            sl_func = SKIP_LIST[key][1]
            if len(SKIP_LIST[key]) == 3:
                kwargs = SKIP_LIST[key][2]
            else:
                kwargs = dict()
            # check if recipe names agree
            cond1 = run_item.recipename == remove_py(sl_item.__NAME__)
            # check if key in params
            cond2 = runkey in params
            # if both conditions met then we must check filename
            if cond1 and cond2:
                if 'MASTER' in key and params[runkey]:
                    check2 = False
                elif params[runkey]:
                    check2 = check_skip(params, run_item, sl_func, kwargs)
                else:
                    check2 = True

        # append to output
        if check1 and check2:
            out_runlist.append(run_item)
        elif not check1:
            print('Not running {0}: {1}'.format(it, run_item))
        elif not check2:
            print('Skipping {0}: {1}'.format(it, run_item))
    # return out list
    return out_runlist


def check_skip(params, run_object, file_func, kwargs):
    # look for fits files
    files = []
    for arg in run_object.args:
        if arg.endswith('.fits'):
            files.append(arg)
    # run all files through the file function
    for filename in files:
        # make sure filename is a base filename
        basename = os.path.basename(filename)
        # loop through fiber types
        for fiber in params['FIBER_TYPES']:
            kwargs['FIBER'] = fiber
            params['FIBER'] = fiber
            params = setup_paths(params, run_object.nightname)
            # try the outpath
            outs = file_func(params, filename=basename, **kwargs)
            # depends on output
            if isinstance(outs, str):
                outpath = outs
            else:
                outpath = outs[0]
            # if this file is found then break
            if os.path.exists(outpath):
                return False
    # if we get to here there are no skips
    return True


def setup_paths(params, nightname):

    params['ARG_NIGHT_NAME'] = nightname
    params['REDUCED_DIR'] = os.path.join(params['DRS_DATA_REDUC'], nightname)
    params['TMP_DIR'] = os.path.join(params['DRS_DATA_WORKING'], nightname)

    return params


# =============================================================================
# Define classes
# =============================================================================
class Reprocesser:
    def __init__(self, params, name, args):
        self.params = params
        self.name = remove_py(name)
        self.arglist = args
        # this stores how many drs files there are per file arg
        self.kinds = OrderedDict()
        self.limit = None
        # this stores the drs files themselves for each file arg
        self.file_args = OrderedDict()
        # get the recipe
        self.recipe = self.find_recipe()
        # fill self.kinds and self.file_args
        self.find_file_arguments()
        # storage for the file groups
        self.file_groups = OrderedDict()
        # storage of the commands (and iteration number)
        self.command_number = 0
        self.commands = OrderedDict()

    def find_recipe(self):
        return drs_startup.find_recipe(self.name, self.params['INSTRUMENT'])

    def find_file_arguments(self):
        """
        # get associated file type arguments
        :return:
        """
        if self.recipe is None:
            return []
        # get recipe arg list without '-'
        recipearglist = list(map(lambda x: x.replace('-', ''),
                                 self.recipe.args.keys()))
        oarglist = list(self.recipe.args.keys())
        for rarg in self.arglist:
            if rarg in recipearglist:
                pos = recipearglist.index(rarg)
                oarg = oarglist[pos]
                drsfiles = self.recipe.args[oarg]['files']
                self.file_args[oarg] = drsfiles
                self.kinds[oarg] = len(drsfiles)
        # set the limit
        for oarg in self.kinds:
            if self.limit is not None:
                if self.kinds[oarg] > self.limit:
                    self.limit = self.kinds[oarg]
            else:
                self.limit = self.kinds[oarg]

    def get_file_groups(self, table, filters, night=None):
        if self.recipe is None:
            return []

        # get lengths of all files
        lengths = map(lambda x: len(x), table[ITABLE_FILECOL])
        maxlen = np.max(list(lengths))

        # for every file argument
        for argname in self.file_args:
            # add empty list for file argument
            self.file_groups[argname] = []
            # get this file argument's drs files
            drsfiles = self.file_args[argname]
            # create a table for this drs file
            drstable = Table()
            # add all columns
            for col in table.colnames:
                drstable[col] = table[col]
            # add new file cols
            for d_it in range(len(drsfiles)):
                empty = [' '*maxlen*2]*len(drstable)
                drstable['NEWFILES{0}'.format(d_it)] = empty
            # full mask
            mask_full = np.zeros((len(drstable)), dtype=bool)
            # for every type of file in file arguement
            for d_it, drsfile in enumerate(drsfiles):
                # need to find all files that below in this group
                dargs = [drsfile, table, filters, night]
                mask_it, newfiles = self.get_drsfile_mask(*dargs)
                # add new files column
                drstable['NEWFILES{0}'.format(d_it)][mask_it] = newfiles
                # change the full mask
                mask_full |= mask_it
            # mask the catalogue by full mask
            drstable = drstable[mask_full]
            # need to group files
            drstable['GROUPS'], nightmask = group_drs_files(self.params,
                                                            drstable)
            # mask by night mask
            drstable = drstable[nightmask]
            # need to get each groups mean
            drstable['MEANDATE'] = get_group_mean(drstable)
            # loop around groups and add to outargs
            for g_it in range(1, int(max(drstable['GROUPS'])) + 1):
                # get group table
                grouptable = drstable[drstable['GROUPS'] == g_it].copy()
                # add to file_groups
                self.file_groups[argname].append(grouptable)

    def get_drsfile_mask(self, drsfile, table, filters, night=None):
        # get in filenames
        infilenames = table[ITABLE_FILECOL]
        # ------------------------------------------------------------------
        # get output extension
        outext = drsfile.args['ext']
        # get input extension
        while 'intype' in drsfile.args:
            drsfile = drsfile.args['intype']
        inext = drsfile.args['ext']
        # ------------------------------------------------------------------
        # get required header keys
        rkeys = dict()
        for arg in drsfile.args:
            if arg.startswith('KW_'):
                rkeys[arg] = drsfile.args[arg]
        # maask by the required header keys
        mask = np.ones_like(infilenames, dtype=bool)
        for key in rkeys:
            mask &= table[key] == rkeys[key]
        # check for empty mask
        if np.sum(mask) == 0:
            return mask, []
        # ------------------------------------------------------------------
        # deal with a night filter
        if night is not None:
            mask &= (table[NIGHT_COL] == night)
        # check for empty mask
        if np.sum(mask) == 0:
            return mask, []

        # ------------------------------------------------------------------
        # deal with filters
        if filters is not None:
            # --------------------------------------------------------------
            # KW_OBJECT filters
            # --------------------------------------------------------------
            # deal with science filter
            if self.params[SFILTER] is not None and SFILTER in filters:
                objectnames = self.params[SFILTER].split(' ')
                # apply object names to mask
                mask &= np.in1d(table['KW_OBJECT'], objectnames)
            # deal with telluric filter
            if TFILTER in filters:
                if self.params[TFILTER] is None:
                    objectnames = spirouTelluric.GetWhiteList()
                else:
                    objectnames = self.params[TFILTER].split(' ')
                # apply object names to mask
                mask &= np.in1d(table['KW_OBJECT'], objectnames)
            # ------------------------------------------------------------------
            # type filters
            # ------------------------------------------------------------------
            # type mask is initially all False
            typemask = np.zeros(len(table), dtype=bool)
            do_mask = False
            # deal with an FP filter
            if FP_FILTER in filters:
                # conditions to be FP_FP
                cond1 = table['KW_CCAS'] == 'pos_fp'
                cond2 = table['KW_CREF'] == 'pos_fp'
                # apply to mask
                typemask |= (cond1 & cond2)
                do_mask = True

            # deal with an HC filter
            if HC_FILTER in filters:
                # conditions to be FP_FP
                cond1 = table['KW_CCAS'] == 'pos_hc1'
                cond2 = table['KW_CREF'] == 'pos_hc1'
                # apply to mask
                typemask |= (cond1 & cond2)
                do_mask = True

            # apply type mask to mask (only if we need to)
            if do_mask:
                mask &= typemask
        # -------------------------------------------------------------------------
        # construct new filenames
        outfilenames = []
        for it, filename in enumerate(infilenames):
            if not filename.endswith(inext):
                mask[it] = False
            if mask[it]:
                outfilenames.append(filename.replace(inext, outext))
        # -------------------------------------------------------------------------
        # return the mask
        return mask, outfilenames

    def generate_run_commands(self):
        # case 1: deal with no argument list
        if len(self.arglist) == 0:
            self.commands[0] = '{0}'.format(self.name)
        # case 2: we have one file argument group
        elif len(self.file_groups) == 1:
            # get primary arg name
            argname1 = list(self.file_args.keys())[0]
            # get limit for primary arg
            limit = self.recipe.args[argname1].get('limit', None)
            # set other args
            other_args = []
            # get filelist
            arglist = self.get_filelist(argname1, other_args, limit)
            # create commands
            self.generate_commands(arglist)
        # case 3: we have more than one file argument group
        #    --> we must match files from each file argumentgroup
        else:
            # get primary arg name
            argname1, other_args = self.get_minimum_file_argument()
            # get limit for primary arg
            limit = 1
            # get filelist
            arglist = self.get_filelist(argname1, other_args, limit)
            # create commands
            self.generate_commands(arglist)

    def get_minimum_file_argument(self):
        # start the minimum length of at infinite size
        min_len = np.inf
        # start the minimum file argument as None
        min_arg = None
        # loop around the arguments in file_gruops
        for argname in self.file_groups:
            # get the table for this file argument
            argtable = self.file_groups[argname][0]
            # if argtable is smaller in length this is the minim
            if len(argtable) < min_len:
                min_len = len(argtable)
                min_arg = argname
        # get list of other arguments
        other_args = []
        for argname in self.file_groups:
            if argname != min_arg:
                other_args.append(argname)
        # return the minimum group
        return min_arg, other_args

    def get_filelist(self, arg1, args, limit=None):
        if self.recipe is None:
            return [], []
        # set up storage
        arglist = OrderedDict()
        for rarg in self.arglist:
            arglist[rarg] = []

        # set up used groups (for each argument)
        used_groups = dict()
        for arg in args:
            used_groups[arg] = []
        # loop around the groups in arg1
        for table1 in self.file_groups[arg1]:
            # get the individual group values
            night1 = table1[NIGHT_COL][0]
            date1 = table1['MEANDATE'][0]
            # get number of drsfiles
            ntypes = len(self.file_args[arg1])
            for ntype in range(ntypes):
                newfiles1 = table1['NEWFILES{0}'.format(ntype)]
                # --------------------------------------------------------------
                #filter out empty files
                fileslen1 = list(map(lambda x: len(x.strip()), newfiles1))
                lenmask1 = np.array(fileslen1) > 0
                newfiles1 = np.array(newfiles1)[lenmask1]
                # if empty skip
                if len(newfiles1) == 0:
                    continue
                # --------------------------------------------------------------
                # case a: no additional files args and want each file separate
                if len(args) == 0 and limit == 1:
                    for nfile1 in newfiles1:
                        # add night name if in arguments
                        if 'night_name' in self.arglist:
                            arglist['night_name'].append(night1)
                        # add other args (without dashes)
                        arg1i = remove_dash(arg1)
                        arglist[arg1i].append([nfile1])
                # --------------------------------------------------------------
                # case b: no additional files args and want all files together
                elif len(args) == 0:
                    # add night name if in arguments
                    if 'night_name' in self.arglist:
                        arglist['night_name'].append(night1)
                    # add other args (without dashes)
                    arg1i = remove_dash(arg1)
                    arglist[arg1i].append(list(newfiles1))
                # --------------------------------------------------------------
                # case c: additional file args and want one from each group
                else:
                    # set up files2 storage (will have one file from each
                    #   file argument
                    files2 = OrderedDict()
                    # loop around arguments and add one file to files2
                    for arg2 in args:
                        # used_groups is updated
                        margs = [used_groups, night1, date1, arg2, ntype]
                        nfiles, used_groups = self.match_groups(*margs)
                        if nfiles is not None:
                            files2[arg2] = nfiles
                    # if files2 is not empty append it to filelist
                    #     with files1[0]
                    if len(files2) != 0:
                        # add night name if in arguments
                        if 'night_name' in self.arglist:
                            arglist['night_name'].append(night1)
                        # add other args (without dashes)
                        arg1i = remove_dash(arg1)
                        arglist[arg1i].append(list(newfiles1)[0])
                        for arg2 in args:
                            # add other args (without dashes)
                            arg2i = remove_dash(arg2)
                            arglist[arg2i].append(list(files2[arg2])[0])
        # finally return night and file list
        return arglist

    def match_groups(self, used_groups, night1, date1, arg, ntype):
        # set up storage
        dates2, files2 = [], []
        # loop around the groups in this argument
        for table2 in self.file_groups[arg]:
            # get the individual group values
            files2i = table2['NEWFILES{0}'.format(ntype)]
            # deal with no filename (i.e. not in this group)
            fileslen2 = list(map(lambda x: len(x.strip()), files2i))
            lenmask2 = np.array(fileslen2) > 0
            files2i = np.array(files2i)[lenmask2]
            # deal with no groups members left
            if len(files2i) == 0:
                continue
            # these properties are the same for all group members
            group2i = table2['GROUPS'][0]
            night2i = table2[NIGHT_COL][0]
            date2i = table2['MEANDATE'][0]
            # do not use groups we already have used
            if group2i in used_groups[arg]:
                date2i = np.inf
            # do not use if nights are different
            if night1 != night2i:
                date2 = np.inf
            # if we have reached here append to dates2
            dates2.append(date2i)
            files2.append(files2i)
        # deal with no members
        if len(files2) == 0 :
            return None, used_groups
        # make dates a numpy array
        dates2 = np.array(dates2)
        # if we have no dates return None
        if np.sum(np.isfinite(dates2)) == 0:
            return None, used_groups
        # now find the closest date
        diff = np.abs(dates2 - date1)
        pos = int(np.argmin(diff))
        # add position to used_group
        used_groups[arg].append(pos)
        # return the filename in the correct position
        return files2[pos], used_groups

    def generate_commands(self, arglist):
        if self.recipe is None:
            return 0
        # get the number of arguments expected
        number = len(list(arglist.values())[0])
        # loop around the number of arguments expected
        for it in range(number):
            command = '{0} '.format(self.name)
            # loop around expected keys
            for key in self.arglist:
                value = arglist[key][it]
                if isinstance(value, list):
                    command += '{0} '.format(' '.join(value))
                else:
                    command += '{0} '.format(value)
            # add to command list
            self.commands[self.command_number] = command.strip()
            # iterate the command number
            self.command_number += 1


# =============================================================================
# Define "from automated" functions
# =============================================================================
def generate_all(params, table, path):

    # get pseudo constants
    pconst = constants.pload(params['INSTRUMENT'])

    # get mod list
    modlist = pconst.MOD_LIST

    # storage of runlist
    runtable = OrderedDict()
    runkey = 0
    # loop around each module and find arguments
    for m_it, modname in enumerate(modlist):
        # log progress
        WLOG(params, '', 'Checking run {0}'.format(modname))
        # get recipe name
        r_name = modlist[modname][0].__NAME__
        r_args = np.array(modlist[modname][0].__args__)
        r_reqs = np.array(modlist[modname][0].__required__)
        r_filter = modlist[modname][1]
        if len(r_args) > 0 and len(r_reqs) > 0:
            r_args = list(r_args[r_reqs])
        # get run name
        runname = 'RUN_{0}'.format(modname)

        # deal with master night
        if 'MASTER' in modname.upper():
            # check that night name exists else break
            night = check_nightname(params, params['MASTER_NIGHT'],
                                    'Master night name')
        else:
            night = None
        # make sure item in params - skip if it isn't
        if runname not in params:
            continue
        # make sure run list item is True in params
        if params[runname]:
            # log progress
            wmsg = '\tGenerating runs for {0} [{1}]'
            WLOG(params, '', wmsg.format(modname, remove_py(r_name)))
            # get reprocesser
            prog = Reprocesser(params, r_name, r_args)

            # update limit (for master sometimes need 1)
            if 'MASTER' in modname.upper():
                limit = prog.limit
            else:
                limit = None
            # find file groups using raw table (tables[0])
            prog.get_file_groups(table, r_filter, night)
            # generate run commands
            prog.generate_run_commands()
            # --------------------------------------------------------------
            # add this to runlist
            for key in list(prog.commands.keys())[:limit]:
                cargs = [runkey, prog.commands[key]]
                print('Adding {0}: {1}'.format(*cargs))
                runtable[runkey] = prog.commands[key]
                # iterate runkey
                runkey += 1
        # else print that we are skipping
        else:
            # log progress
            wmsg = '\t\tSkipping runs for {0} [{1}]'
            WLOG(params, '', wmsg.format(modname, remove_py(r_name)))

    # return run objects (via generate ids)
    return generate_ids(params, table, path, runtable)


def group_drs_files(params, drstable, **kwargs):

    func_name = __NAME__ + '.group_drs_files()'
    # get properties from params
    night_col = pcheck(params, 'REPROCESS_NIGHTCOL', 'night_col', kwargs,
                       func_name)
    # st up empty groups
    groups = np.zeros(len(drstable))
    # get the sequence column
    sequence_col = drstable['KW_CMPLTEXP']
    # start the group number at 1
    group_number = 1
    # set up night mask
    valid = np.zeros(len(drstable), dtype=bool)
    # by night name
    for night in np.unique(drstable[night_col]):
        # deal with just this night name
        nightmask = drstable[night_col] == night
        # deal with only one file in nightmask
        if np.sum(nightmask) == 1:
            groups[nightmask] = group_number
            group_number += 1
            valid |= nightmask
            continue
        # set invalid sequence numbers to 1
        sequence_mask = sequence_col == ''
        sequence_col[sequence_mask] = 1
        # get the sequence number
        sequences = sequence_col[nightmask].astype(int)
        indices = np.arange(len(sequences))
        # get the raw groups
        rawgroups = np.array(-(sequences - indices) + 1)

        nightgroup = np.zeros(np.sum(nightmask))
        # loop around the unique groups and assign group number
        for rgroup in np.unique(rawgroups):
            # get group mask
            groupmask = rawgroups == rgroup
            # push the group number into night group
            nightgroup[groupmask] = group_number
            # add to the group number
            group_number += 1
        # add the night group to the full group
        groups[nightmask] = nightgroup
        # add to the valid mask
        valid |= nightmask
    # return the group
    return groups, valid


def get_group_mean(table):
    # start of mean dates as zeros
    meandate = np.zeros(len(table))
    # get groups from table
    groups = table['GROUPS']
    # loop around each group and change the mean date for the files
    for g_it in range(1, int(max(groups)) + 1):
        # group mask
        groupmask = (groups == g_it)
        # group mean
        groupmean = np.mean(table['KW_ACQTIME'][groupmask])
        # save group mean
        meandate[groupmask] = groupmean
    # return mean date
    return meandate


def remove_py(innames):
    if isinstance(innames, str):
        names = [innames]
    else:
        names = innames
    outnames = []
    for name in names:
        while name.endswith('.py'):
            name = name[:-3]
        outnames.append(name)
    if isinstance(innames, str):
        return outnames[0]
    else:
        return outnames


def remove_dash(instring):
    while instring.startswith('-'):
        instring = instring[1:]
    return instring


def check_nightname(params, nightname, description):

    paths = [params['DRS_DATA_RAW']]

    for path in paths:
        abspath = os.path.join(path, nightname)

        if not os.path.exists(abspath):
            emsg = 'Night name ({0}) = {1} does not exist'
            eargs = [description, abspath]
            WLOG(params, 'error', emsg.format(*eargs))

    return nightname


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
