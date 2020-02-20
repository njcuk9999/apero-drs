#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2020-02-19 at 09:30

@author: cook
"""
import os
import sys
import importlib


# =============================================================================
# Define variables
# =============================================================================
# set rsync command
RSYNC_COMMAND = 'rsync -avr {0} --port=8080 {1}::{2} {3}'
# set rsync server
RSYNC_SERVER = '{0}@craq-astro.ca'
# set rsync password
RSYNC_PASSWORD = dict()
RSYNC_PASSWORD['SPIROU'] = 'Zorglub007'
RSYNC_PASSWORD['NIRPS_HA'] = 'Zorglub007'
# RSYNC dir
RSYNC_DIR = '{0}'
# allowed instruments
INSTRUMENTS = ['SPIROU', 'NIRPS_HA']
RECIPE_DEFINITIONS = dict()
RECIPE_DEFINITIONS['SPIROU'] = 'apero.core.instruments.spirou.recipe_definitions'
RECIPE_DEFINITIONS['NIRPS_HA'] = 'apero.core.instruments.nirps_ha.recipe_definitions'
# default data dir
DATA_DIR = 'mini_data_0_6_037'
# set raw sub dir
RAW_DIR = 'raw'
# set tmp sub dir
TMP_DIR = 'tmp'
# set reduced sub dir
RED_DIR = 'reduced'
# set calib sub dir
CALIB_DIR = 'calibDB'
# set tellu sub dir
TELLU_DIR = 'telluDB'
# deal with unknown recipe
UNKNOWN_SHORTNAME = 'UnknownRecipe'

# help message
HELP_KWARGS = dict(INSTRUMENT=', '.join(INSTRUMENTS),
                   DATA_DIR=DATA_DIR, NAME='{NAME}')
HELP_MESSAGE = """

Montreal APERO data sync

===============================================
Options are:
===============================================

--name={NAME}       Change the directory name (i.e. {DATA_DIR})

--exclude           Night directories to exclude (separated by commas NO SPACES)
                    If spaces required use strings i.e.
                    'night 1, night 2, night 3'

--include           Night directories to include (separated by commas NO SPACES)
                    If spaces required use strings i.e.
                    'night 1, night 2, night 3'
                    Note wild cards may be used

--suffix            Define a set of characters that must be in any output
                    (can be used multiple times in one command but logic is as
                    follows: 
                        suffix1 OR suffix2 OR suffix3
                    Note: this complements individual recipes (i.e. it
                    does not filter outputs for a recipe)

--test              Perform a test (dry-run) without any actual copying
                    Recommended the first time this is run
                    Note wild cards may be used
                    
--debug             Performs a debug just printing the rsync command that will
                    be run when not in debug mode

--instrument        Change the instrument to download for (Default: SPIROU)
                    Must be one of the following {INSTRUMENT}

--help / -h         Display this help message

===============================================
Arguments are one or any of the following:
===============================================

Full data sets (warning large amount of data)

RAW                 Download all raw data
TMP                 Download all tmp data (preprocessed)
REDUCED             Download all reduced data 
CALIBDB             Download all calibration data (from calibDB)
TELLUDB             Download all telluric data (from telluDB)

Individual recipes

PP                  Download outputs for cal_preprocessing
BAD                 Download outputs for cal_badpix
DARK                Download outputs for cal_dark
DARKM               Download outputs for cal_dark_master
LOC                 Download outputs for cal_loc
SHAPEM              Download outputs for cal_shape_master
SHAPE               Download outputs for cal_shape
FF                  Download outputs for cal_ff
THERM               Download outputs for cal_thermal
EXT                 Download outputs for cal_extract
WAVE                Download outputs for cal_wave
WAVEM               Download outputs for cal_wave_master
CCF                 Download outputs for cal_ccf
MKTELL              Download outputs for obj_mk_tellu
FTELLU              Download outputs for obj_fit_tellu
MKTEMP              Download outputs for obj_mk_template
POLAR               Download outputs for pol

===============================================
Examples:
===============================================

The following example would download all calibration and telluric files
    for {DATA_DIR}  (in debug mode) - prints only rsync command
    
>> mtl_sync.py --debug --name={DATA_DIR} CALIBDB TELLUDB

--------------------------------------------------------------------------------

The following example would download all extracted and ccf outputs
    for mini_data_0_6_037 in night directories 2019-04-20 and 2019-04-19
    in test mode (runs rsync but does not copy files)
    
>> mtl_sync.py --test --name={DATA_DIR} --include='2019-04-20,2019-04-19' EXT CCF 

--------------------------------------------------------------------------------

The following example would download badpix outputs
    for {DATA_DIR} except for night directories 2019-02-20 and 2019-02-19
    in test mode (runs rsync but does not copy files)
    
>> mtl_sync.py --test --name={DATA_DIR} --exclude='2019-04-20,2019-04-19' BAD 

--------------------------------------------------------------------------------

The following example would download all raw data for 2019-04-20

>> mtl_sync.py --test --name={DATA_DIR} --include=2019-04-20 RAW

--------------------------------------------------------------------------------

The following example would download all e2ds_AB files from the reduced directory
    for {DATA_DIR} in the night directory 2019-04-20
    in test mode (runs rsync but does not copy files)

>> mtl_sync.py --test --name={DATA_DIR} --suffix=e2ds_AB --include=2019-04-20 REDUCED

--------------------------------------------------------------------------------

End of help file

""".format(**HELP_KWARGS)



# =============================================================================
# Define functions
# =============================================================================
class FileDef():
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', 'Unknown')
        self.recipe = kwargs.get('recipe', None)
        self.path = kwargs.get('path', None)
        self.data_dir = kwargs.get('datadir', None)
        self.instrument = kwargs.get('instrument', 'spirou')
        self.rsync_dir = RSYNC_DIR.format(self.instrument.upper())
        self.has_dirs = True
        self.inpath = None
        self.outpath = None
        self.relpath = None
        self.suffices = []
        # deal with no data dir
        if self.data_dir is None:
            self.data_dir = DATA_DIR
        # deal with starting from a recipe definition
        if self.recipe is not None:
            self.get_suffices()
            self.shortname = self.recipe.shortname
        else:
            self.shortname = self.name
        # deal with starting from a path
        if self.path is not None:
            self.inpath = os.path.join(self.rsync_dir, self.data_dir, self.path)
            self.outpath = os.path.join(self.data_dir, self.path)
            self.relpath = self.path

    def __str__(self):
        if self.recipe is not None:
            args = [self.recipe.shortname]
        else:
            args = [self.name]
        return 'FileDef[{0}]'.format(*args)

    def __repr__(self):
        return self.__str__()

    def get_suffices(self):
        # deal with no recipe
        if self.recipe is None:
            return None
        # check for output directory
        if self.recipe.outputdir is not None:
            if self.recipe.outputdir == 'tmp':
                self.inpath = os.path.join(self.rsync_dir, self.data_dir,
                                           TMP_DIR)
                self.outpath = os.path.join(self.data_dir, TMP_DIR)
                self.relpath = TMP_DIR
            if self.recipe.outputdir == 'reduced':
                self.inpath = os.path.join(self.rsync_dir, self.data_dir,
                                           RED_DIR)
                self.outpath = os.path.join(self.data_dir, RED_DIR)
                self.relpath = RED_DIR
        # check for outputs
        outputs = self.recipe.outputs
        # deal with no outputs
        if outputs is None:
            return None
        # loop around outputs
        for filekey in outputs:
            # get output
            output = outputs[filekey]
            # deal with having suffices
            if output.suffix is not None:
                self.suffices.append(output.suffix)


def get_args():
    # get user arguments
    args = list(sys.argv)

    # deal with to few args
    if len(args) < 2:
        print('Too few arguments')
        print_help()
        return None, None

    # deal with help
    if '--help' in args or '-h' in args:
        print_help()
        return None, None

    print('\n Processing user arguments')

    # --------------------------------------------------------------------------
    # Deal with optional arguments
    # --------------------------------------------------------------------------
    options = dict()
    options['args'] = list(args)
    # --------------------------------------------------------------------------
    # deal with instrument
    options['instrument'] = INSTRUMENTS[0]
    for arg in args:
        if '--instrument' in arg:
            options['instrument'] = arg.split('--instrument=')[-1]
    # deal with wrong instrument
    if options['instrument'].upper() not in INSTRUMENTS:
        print('Error --instrument must be one of the following:')
        print('\t {0}'.format(', '.join(INSTRUMENTS)))
        os._exit(0)
    # --------------------------------------------------------------------------
    # deal with test case
    if '--test' in args:
        options['test'] = True
    else:
        options['test'] = False
    # deal with debug case
    if '--debug' in args:
        options['debug'] = True
        options['test'] = True
    else:
        options['debug'] = False
    # --------------------------------------------------------------------------
    # deal with name
    found_name = None
    for arg in args:
        if '--name' in arg:
            found_name = arg.split('--name=')[-1]
    if found_name is not None:
        options['datadir'] = found_name
    else:
        options['datadir'] = DATA_DIR
    # --------------------------------------------------------------------------
    # deal with excluding directories
    found_ex_dir = None
    for arg in args:
        if '--exclude' in arg:
            found_ex_dir = arg.split('--exclude=')[-1]
            found_ex_dir = found_ex_dir.replace('\'', '').replace('\"', '')
            found_ex_dir = found_ex_dir.split(',')
    if found_ex_dir is not None:
        options['exclude'] = found_ex_dir
    else:
        options['exclude'] = []

    # --------------------------------------------------------------------------
    # deal with including directories
    found_in_dir = None
    for arg in args:
        if '--include' in arg:
            found_in_dir = arg.split('--include=')[-1]
            found_in_dir = found_in_dir.replace('\'', '').replace('\"', '')
            found_in_dir = found_in_dir.split(',')
    if found_in_dir is not None:
        options['include'] = found_in_dir
    else:
        options['include'] = []

    # --------------------------------------------------------------------------
    # deal with suffices
    suffices = []
    for arg in args:
        if '--suffix' in arg:
            suffix = arg.split('--suffix=')[-1]
            suffices.append(suffix)

    # --------------------------------------------------------------------------
    # get recipe definitions
    # --------------------------------------------------------------------------
    print('\n Loading APERO for instrument = {0}'.format(options['instrument']))
    rd = importlib.import_module(RECIPE_DEFINITIONS[options['instrument']])

    # --------------------------------------------------------------------------
    # File types
    # --------------------------------------------------------------------------
    # set up file types
    filetypes = []

    # deal with pre-defined suffices


    # --------------------------------------------------------------------------
    # KIND = RECIPE
    # --------------------------------------------------------------------------
    # loop around recipes
    for recipe in rd.recipes:
        if recipe.shortname in args:
            filedef = FileDef(recipe=recipe, **options)
            # deal with user suffix
            if len(suffices) > 0:
                for suffix in suffices:
                    filedef.suffices.append(suffix)
            # add file def to out put list
            filetypes.append(filedef)
    # --------------------------------------------------------------------------
    # KIND = RAW
    # --------------------------------------------------------------------------
    if 'RAW' in args:
        filetype = FileDef(name='RAW', path=RAW_DIR, **options)
        # deal with user suffix
        if len(suffices) > 0:
            for suffix in suffices:
                filetype.suffices.append(suffix)
        # add file type to out put list
        filetypes.append(filetype)

    # --------------------------------------------------------------------------
    # KIND = TMP
    # --------------------------------------------------------------------------
    if 'TMP' in args:
        filetype = FileDef(name='TMP', path=TMP_DIR, **options)
        # deal with user suffix
        if len(suffices) > 0:
            for suffix in suffices:
                filetype.suffices.append(suffix)
        # add file type to out put list
        filetypes.append(filetype)

    # --------------------------------------------------------------------------
    # KIND = REDUCED
    # --------------------------------------------------------------------------
    if 'REDUCED' in args:
        filetype = FileDef(name='REDUCED', path=RED_DIR, **options)
        # deal with user suffix
        if len(suffices) > 0:
            for suffix in suffices:
                filetype.suffices.append(suffix)
        # add file type to out put list
        filetypes.append(filetype)

    # --------------------------------------------------------------------------
    # KIND = CALIBDB
    # --------------------------------------------------------------------------
    if 'CALIBDB' in args:
        filetype = FileDef(name='CALIBDB', path=CALIB_DIR, **options)
        # calibDB does not have sub directories
        filetype.has_dirs = False
        # deal with user suffix
        if len(suffices) > 0:
            for suffix in suffices:
                filetype.suffices.append(suffix)
        # add file type to out put list
        filetypes.append(filetype)

    # --------------------------------------------------------------------------
    # KIND = TELLUDB
    # --------------------------------------------------------------------------
    if 'TELLUDB' in args:
        filetype = FileDef(name='TELLUDB', path=TELLU_DIR, **options)
        # telluDB does not have sub directories
        filetype.has_dirs = False
        # deal with user suffix
        if len(suffices) > 0:
            for suffix in suffices:
                filetype.suffices.append(suffix)
        # add file type to out put list
        filetypes.append(filetype)

    # return file types
    return filetypes, options


def print_help():
    print(HELP_MESSAGE)


def construct_command(filetypes, options):

    # get rsync folder
    rsync_server = RSYNC_SERVER.format(options['instrument'].lower())


    cmds = []

    for filetype in filetypes:
        # construct args
        args = ['', rsync_server, filetype.inpath, filetype.outpath]
        # ----------------------------------------------------------------------
        # deal with excluding nights
        if len(options['exclude']) > 0:
            for exclude in options['exclude']:
                if filetype.has_dirs:
                    args[0] += ' --exclude={1}{0}* '.format(os.sep, exclude)
        # ----------------------------------------------------------------------
        # deal with including nights
        ipaths = []
        if len(options['include']) > 0:
            for include in options['include']:
                if filetype.has_dirs:
                    ipaths.append('{0}{1}'.format(include, os.sep))
        # deal with no includes needed
        if len(ipaths) == 0:
            ipaths = ['']
        # ----------------------------------------------------------------------
        # start suffices added as false
        s_added = False
        # loop around suffixes
        for suffix in filetype.suffices:
            for ipath in ipaths:
                # if we are here change suffices added to True
                s_added = True
                # add suffix
                args[0] += ' --include="{0}*{1}*" '.format(ipath, suffix)
        # if we have added suffices we need to exclude everything else
        if s_added:
            args[0] += ' --exclude="*.*" '
        elif ipaths[0] != ['']:
            for ipath in ipaths:
                args[0] += ' --include="{0}*"'.format(ipath)
                args[0] += ' --exclude="*.*" '
        # ----------------------------------------------------------------------
        # deal with a test run (rsync dry-run)
        if options['test']:
            args[0] += ' --dry-run '
        # ----------------------------------------------------------------------
        # remove additional white spaces
        args[0] = args[0].strip()
        # populate command
        cmd = RSYNC_COMMAND.format(*args)
        # remove additional white spaces
        while '  ' in cmd:
            cmd = cmd.replace('  ', ' ')
        cmd = cmd.strip()
        # append to cmds
        cmds.append(cmd)
    # return commands
    return cmds


def run_commands(filetypes, cmds, options):
    # loop around cmds iteratively
    for row in range(len(cmds)):
        # get this iterations values
        filetype = filetypes[row]
        cmd = cmds[row]
        # check dirs
        if not os.path.exists(filetype.outpath) and not options['test']:
            os.makedirs(filetype.outpath)
        # print statements
        print('\n\n' + '='*50)
        print('\nRunning rsync for "{0}"'.format(filetype.shortname))
        print('\t Instrument = {0}'.format(options['instrument']))
        print('\t Data directory = {0}'.format(options['datadir']))
        print('\n' + '=' * 50 + '\n\n')
        # run command
        if options['debug']:
            print(cmd)
        elif options['test']:
            print(cmd)
            os.system(cmd)
        else:
            os.system(cmd)


def main():
    # get user arguments
    filedefs, opts = get_args()
    # deal with exit
    if filedefs is None or opts is None:
        return
    # set the password in the environment
    print('\n Setting environment')
    os.environ['RSYNC_PASSWORD'] = RSYNC_PASSWORD[opts['instrument']]

    print('\n Running rsync commands')
    # create command
    commands = construct_command(filedefs, opts)
    # run commands
    run_commands(filedefs, commands, opts)


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    main()



# =============================================================================
# End of code
# =============================================================================
