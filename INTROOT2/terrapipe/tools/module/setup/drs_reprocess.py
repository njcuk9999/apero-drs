#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-08-06 at 11:57

@author: cook
"""
import numpy as np
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
    func_name = __NAME__ + '.runfile()'
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
        keys, values = np.genfromtxt(runfile, delimiter='=', comments='#',
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
    rvalues = get_rvalues(runtable)
    # check if rvalues has a run sequence
    sequences = check_for_sequences(params, rvalues)
    # if we have found sequences need to deal with them
    if sequences is not None:
        # loop around sequences
        for sequence in sequences:
            # generate new runs for sequence
            # TODO: Problem here

            newruns = generate_run_from_sequence(params, sequence, table)
            # update runtable with sequence generation
            runtable = update_run_table(params, sequence, runtable, rvalues,
                                        newruns)
            # need to update rvalues when runtable is updated (for new sequence)
            rvalues = get_rvalues(runtable)
    # return Run instances for each runtable element
    return generate_ids(params, runtable)


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
            ucpath = drs_path.get_uncommon_path(rpath, root)
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
        self.kind = None
        # sort out names
        self.runname = 'RUN_{0}'.format(self.recipe.shortname)
        self.skipname = 'SKIP_{0}'.format(self.recipe.shortname)
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


# =============================================================================
# Define "from id" functions
# =============================================================================
def generate_ids(params, runtable, **kwargs):
    func_name = __NAME__ + '.generate_ids()'
    # get keys from params
    run_key = pcheck(params, 'REPROCESS_RUN_KEY', 'run_key', kwargs, func_name)
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
        # get runid
        runid = '{0}{1:05d}'.format(run_key, keylist[it])
        # log process
        wargs = [runid, it + 1, len(runlist), run_item]
        WLOG(params, '', params['DRS_HEADER'])
        WLOG(params, '', TextEntry('40-503-00004', args=wargs))
        WLOG(params, '', params['DRS_HEADER'])
        # create run object
        run_object = Run(params, run_item, priority=keylist[it])
        # deal with skip
        skip, reason = skip_run_object(params, run_object)
        # append to list
        if not skip:
            # log that we have validated run
            wargs = [runid]
            WLOG(params, '', TextEntry('40-503-00005', args=wargs))
            # append to run_objects
            run_objects.append(run_object)
        # else log that we are skipping
        else:
            # log that we have skipped run
            wargs = [runid, reason]
            WLOG(params, 'info', TextEntry('40-503-00006', args=wargs))
    # return run objects
    return run_objects


def skip_run_object(params, runobj):

    # create text dictionary
    textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
    # get recipe and runstring
    recipe = runobj.recipe
    runstring = runobj.runstring

    # ----------------------------------------------------------------------
    # check if the user wants to run this runobj (in run list)
    if runobj.runname in params:
        # if user has set the runname to False then we want to skip
        if not params[runobj.runname]:
            return True, textdict['40-503-00007']
    # ----------------------------------------------------------------------
    # check if the user wants to skip
    if runobj.skipname in params:
        # if master in skipname do not skip
        if 'MASTER' in runobj.skipname:
            # debug log
            dargs = [runobj.skipname]
            WLOG(params, 'debug', TextEntry('90-503-00003', args=dargs))
            # return False and no reason
            return False, None
        # else if user wants to skip
        elif params[runobj.skipname]:
            # deal with adding skip to recipes
            if 'skip' in recipe.kwargs:
                if '--skip' not in runstring:
                    runobj.runstring = '{0} --skip=True'.format(runstring)
                    # debug log
                    WLOG(params, 'debug', TextEntry('90-503-00006'))
                    return False, None
                else:
                    # debug log
                    WLOG(params, 'debug', TextEntry('90-503-00007'))
                    return False, None

            # look for fits files in args
            return check_for_files(params, runobj)
        else:
            # debug log
            dargs = [runobj.skipname]
            WLOG(params, 'debug', TextEntry('90-503-00004', args=dargs))
            # return False and no reason
            return False, None
    # ----------------------------------------------------------------------
    else:
        # debug log
        dargs = [runobj.skipname]
        WLOG(params, 'debug', TextEntry('90-503-00005', args=dargs))
        # return False and no reason
        return False, None


def get_paths(params, runobj, directory):
    func_name = __NAME__ + '.get_paths()'

    recipe = runobj.recipe
    # ----------------------------------------------------------------------
    # get the night name from directory position
    nightname = runobj.args[directory.pos + 1]
    # ----------------------------------------------------------------------
    # get the input directory
    if recipe.inputdir == 'raw':
        inpath = os.path.join(params['DRS_DATA_RAW'], nightname)
    elif recipe.inputdir == 'tmp':
        inpath = os.path.join(params['DRS_DATA_WORKING'], nightname)
    elif recipe.inputdir.startswith('red'):
        inpath = os.path.join(params['DRS_DATA_REDUC'], nightname)
    else:
        eargs = [recipe.name, recipe.outputdir, func_name]
        WLOG(params, 'error', TextEntry('09-503-00007', args=eargs))
        inpath = None
    # ----------------------------------------------------------------------
    # check that path exist
    if not os.path.exists(inpath):
        eargs = [recipe.name, runobj.runstring, inpath, func_name]
        WLOG(params, 'error', TextEntry('09-503-00008', args=eargs))
    # ----------------------------------------------------------------------
    # get the output directory
    if recipe.outputdir == 'raw':
        outpath = os.path.join(params['DRS_DATA_RAW'], nightname)
    elif recipe.outputdir == 'tmp':
        outpath = os.path.join(params['DRS_DATA_WORKING'], nightname)
    elif recipe.outputdir.startswith('red'):
        outpath = os.path.join(params['DRS_DATA_REDUC'], nightname)
    else:
        eargs = [recipe.name, recipe.outputdir, func_name]
        WLOG(params, 'error', TextEntry('09-503-00005', args=eargs))
        outpath = None
    # ----------------------------------------------------------------------
    # check that path exist
    if not os.path.exists(outpath):
        eargs = [recipe.name, runobj.runstring, outpath, func_name]
        WLOG(params, 'error', TextEntry('09-503-00006', args=eargs))
    # ----------------------------------------------------------------------
    # return inpath and outpath
    return inpath, outpath, nightname


def check_for_files(params, runobj):
    func_name = __NAME__ + '.check_for_files()'
    # create text dictionary
    textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
    # get fits files from args
    files = []
    for arg in runobj.args:
        if arg.endswith('.fits'):
            files.append(arg)
    # set recipe
    recipe = runobj.recipe
    # get args and keyword args for recipe
    args, kwargs = recipe.args, recipe.kwargs
    # ----------------------------------------------------------------------
    # if we don't have a directory argument we skip this test
    if 'directory' not in args and 'directory' not in kwargs:
        WLOG(params, 'debug', TextEntry('90-503-00002'))
        return False, None
    elif 'directory' in args:
        directory = args['directory']
    else:
        directory = kwargs['directory']
    # ----------------------------------------------------------------------
    # get input and output paths
    inpath, outpath, nightname = get_paths(params, runobj, directory)
    # ----------------------------------------------------------------------
    # store outfiles (for debug)
    outfiles = []
    # ----------------------------------------------------------------------
    # get in files
    infiles = []
    # loop around file names
    for filename in files:
        # ------------------------------------------------------------------
        # make sure filename is a base filename
        basename = os.path.basename(filename)
        # make infile
        if runobj.kind == 0:
            infiledef = recipe.filemod.raw_file
        elif runobj.kind == 1:
            infiledef = recipe.filemod.pp_file
        else:
            infiledef = recipe.filemod.out_file
        # ------------------------------------------------------------------
        # add required properties to infile
        infile = infiledef.newcopy(recipe=recipe)
        infile.filename = os.path.join(inpath, filename)
        infile.basename = basename
        # append to infiles
        infiles.append(infile)

    # ----------------------------------------------------------------------
    # for each file see if we have a file that exists
    #   (if we do we skip and assume this recipe was completed)
    for infile in infiles:
        # ------------------------------------------------------------------
        # loop around output files
        for outputkey in recipe.outputs:
            # get output
            output = recipe.outputs[outputkey]
            # add the infile type from output
            infile.filetype = output.inext
            # define outfile
            outfile = output.newcopy(recipe=recipe)
            # --------------------------------------------------------------
            # check whether we need to add fibers
            if output.fibers is not None:
                # loop around fibers
                for fiber in output.fibers:
                    # construct file name
                    outfile.construct_filename(params, infile=infile,
                                               fiber=fiber, path=outpath,
                                               nightname=nightname)
                    # get outfilename absolute path
                    outfilename = outfile.filename
                    # if file is found return True
                    if os.path.exists(outfilename):
                        reason = textdict['40-503-00008'].format(outfilename)
                        return True, reason
                    else:
                        outfiles.append(outfilename)
            else:
                # construct file name
                outfile.construct_filename(params, infile=infile, path=outpath,
                                           nightname=nightname)
                # get outfilename absolute path
                outfilename = outfile.filename
                # if file is found return True
                if os.path.exists(outfilename):
                    reason = textdict['40-503-00008'].format(outfilename)
                    return True, reason
                else:
                    outfiles.append(outfilename)
    # ----------------------------------------------------------------------
    # debug print
    for outfile in outfiles:
        WLOG(params, 'debug', TextEntry('90-503-00001', args=[outfile]))
    # ----------------------------------------------------------------------
    # if all tests are passed return False
    return False, None


def setup_paths(params, nightname):
    """
    setup PATHS required for out file function

    :param params:
    :param nightname:
    :return:
    """
    params['ARG_NIGHT_NAME'] = nightname
    params['REDUCED_DIR'] = os.path.join(params['DRS_DATA_REDUC'], nightname)
    params['TMP_DIR'] = os.path.join(params['DRS_DATA_WORKING'], nightname)

    return params


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


# =============================================================================
# Define "from sequence" functions
# =============================================================================
def get_rvalues(runtable):
    return list(map(lambda x: x.upper(), runtable.values()))


def check_for_sequences(params, rvalues, **kwargs):
    func_name = __NAME__ + '.check_for_sequences()'
    # get parameters from params/kwargs
    instrument = pcheck(params, 'INSTRUMENT', 'instrument', kwargs, func_name)
    instrument_path = pcheck(params, 'DRS_MOD_INSTRUMENT_CONFIG',
                             'instrument_path', kwargs, func_name)
    core_path = pcheck(params, 'DRS_MOD_CORE_CONFIG', 'core_path', kwargs,
                       func_name)

    # deal with no instrument
    if instrument == 'None' or instrument is None:
        ipath = core_path
        instrument = None
    else:
        ipath = instrument_path

    # else we have a name and an instrument
    margs = [instrument, ['recipe_definitions.py'], ipath, core_path]
    modules = constants.getmodnames(*margs, path=False)
    # load module
    mod = constants.import_module(modules[0], full=True)

    # find sequences
    all_sequences = mod.sequences
    # get sequences names
    all_seqnames = list(map(lambda x: x.name, all_sequences))
    # convert to uppercase
    all_seqnames = list(map(lambda x: x.upper(), all_seqnames))
    # storage for found sequences
    sequences = []
    # loop around rvalues and add to sequence
    for rvalue in rvalues:
        if rvalue in all_seqnames:
            # find position of name
            pos = all_seqnames.index(rvalue)
            # append sequences
            sequences.append([rvalue, pos, all_sequences[pos]])
    # deal with return of sequences (found/not found)
    if len(sequences) == 0:
        return None
    else:
        return sequences


def generate_run_from_sequence(params, sequence, table, **kwargs):

    func_name = __NAME__ + '.generate_run_from_sequence()'
    # get parameters from params/kwargs
    night_col = pcheck(params, 'REPROCESS_NIGHTCOL', 'night_col', kwargs,
                       func_name)
    # get the sequence recipe list
    srecipelist = sequence[2].sequence
    # storage for new runs to add
    newruns = []
    # loop around recipes in new list
    for srecipe in srecipelist:
        # deal with nightname
        if srecipe.master:
            nightname = params['MASTER_NIGHT']
            # mask table by nightname
            mask = table[night_col] == nightname
            ftable = Table(table[mask])
        elif params['NIGHTNAME'] != '':
            nightname = params['NIGHTNAME']
            # mask table by nightname
            mask = table[night_col] == nightname
            ftable = Table(table[mask])
        else:
            ftable = Table(table)
        # deal with filters
        filters = dict()
        # loop around recipe filters
        for key in srecipe.filters:
            # get value
            value = srecipe.filters[key]
            # if this is in params set this value
            if value in params:
                filters[key] = params[value].split(',')
        # get runs for this recipe
        sruns = srecipe.generate_runs(params, ftable, filters=filters)
        # append runs to new runs list
        for srun in sruns:
            newruns.append(srun)
    # return all new runs
    return newruns


def update_run_table(params, sequence, runtable, rvalues, newruns):

    # TODO: ------------------------------------------
    # TODO: WORK NEEDED HERE
    # TODO: ------------------------------------------

    return runtable

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
