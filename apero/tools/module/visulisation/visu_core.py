#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2022-02-22

@author: cook
"""
import numpy as np
import os
from typing import Any, Dict, List, Optional, Tuple, Union

from apero.base import base
from apero import lang
from apero.core import constants
from apero.core.core import drs_log
from apero.core.utils import drs_recipe
from apero.core.instruments.default import pseudo_const
from apero.core.core import drs_database
from apero.io import drs_fits

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'database_update.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get params
PARAMS = constants.load()
# Get Logging function
WLOG = drs_log.wlog
# get parameter dictionary
ParamDict = constants.ParamDict
DrsRecipe = drs_recipe.DrsRecipe
PseudoConstants = pseudo_const.PseudoConstants
# get display func
display_func = drs_log.display_func
# Get the text types
textentry = lang.textentry
# get tqdm (if required)
tqdm = base.tqdm_module()
# Define master prefix
MASTER_PREFIX = 'MASTER_'
# Define the gaia drs column in database
GAIA_COL = 'GAIADR2ID'

# define the bokeh python file template
PYTEMPLATE = """
from bokeh.io import curdoc
from apero.tools.module.visulisation import visu_plots

func = getattr(visu_plots, '{func}')

kwargs = dict({kwargs})

root = func(**kwargs)

curdoc().add_root(root)
curdoc().title = '{title}'
"""
# Define allowed types
ValidTypes = Union[int, float, str, bool]


# =============================================================================
# Define general functions
# =============================================================================
class BokehPlot:
    def __init__(self, params: ParamDict, func_name: str, path: str,
                 title: str):
        self.params = params
        self.func = func_name
        self.path = path
        self.title = title

    def create(self, kwargs: Optional[Dict[str, Any]] = None):
        """
        Create our proxy python code
        :param kwargs:
        :return:
        """
        # push into dictionary
        fkwargs = dict()
        fkwargs['func'] = str(self.func)
        fkwargs['title'] = str(self.title)
        fkwargs['kwargs'] = self.add_kwargs(kwargs)
        # write to file
        with open(self.path, 'w') as pyfile:
            pyfile.write(PYTEMPLATE.format(**fkwargs))

    def run(self):
        """
        Run the bokey server from our proxy python code
        :return:
        """
        # run an interactive session
        os.system('bokeh serve --show {0}'.format(self.path))

    def add_kwargs(self, kwargs: Optional[Dict[str, ValidTypes]] = None) -> str:
        """
        Add keyword arguments (int/float/bool/str) in string form - for passing
        to our script

        :param args: list of
        :return:
        """
        # deal with no keyword arguments --> empty string
        if kwargs is None:
            return ''
        # set up return storage
        strargs = []
        # loop around arguments and try to cast into string
        for key in kwargs:
            # get value
            value = kwargs[key]
            # -----------------------------------------------------------------
            # deal with strings
            if isinstance(value, str):
                strargs.append('{0}="{1}"'.format(key, kwargs[key]))
                continue
            # -----------------------------------------------------------------
            # deal with others
            try:
                strarg = '{0}={1}'.format(key, str(kwargs[key]))
                # test as dictionary entry
                _ = eval('dict({0})'.format(strarg))
                # append to str args
                strargs.append(strarg)
            except Exception as _:
                emsg = 'Cannot convert keyword {0}={1} to string'
                WLOG(self.params, 'error', emsg.format(key, str(kwargs[key])))
        # join into string string
        fullstring = ', '.join(strargs)
        # return cleaned string
        return fullstring


def check_arg(func_name, kwargs, key, dtype, required: bool = True):
    # check key exists
    if key not in kwargs and required:
        emsg = 'Function: "{0}" requires keyword "{1}"'
        eargs = [func_name, key]
        WLOG(PARAMS, 'error', emsg.format(*eargs))
    elif key not in kwargs:
        return None
    # try to return value
    try:
        return dtype(kwargs[key])
    except Exception as e:
        emsg = 'Error with key {0}={1}\n\t{2}: {3}'
        eargs = [key, kwargs[key], type(e), str(e)]
        WLOG(PARAMS, 'error', emsg.format(*eargs))


def get_file(block_kind: str,  obs_dir: str, identifier: str,
             output: str, fiber: str, hdu: int, get_data: bool = True
             ) -> Tuple[Union[np.ndarray, None], Union[str, None]]:

    # get database
    indexdbm = drs_database.IndexDatabase(PARAMS)
    indexdbm.load_db()
    # find file in database
    condition = 'BLOCK_KIND="{0}" AND OBS_DIR="{1}" AND KW_IDENTIFIER="{2}"'
    condition += ' AND KW_OUTPUT="{3}" AND KW_FIBER="{4}"'
    condition = condition.format(block_kind, obs_dir, identifier, output,
                                 fiber)
    # query database
    table = indexdbm.get_entries('ABSPATH, OBS_DIR', condition=condition)
    # deal with no entries
    if table is None or len(table) == 0:
        return None, None
    # use the first entry as the filename
    filename = table['ABSPATH'].iloc[0]
    # load file with correct extension
    if get_data:
        data = drs_fits.readfits(PARAMS, filename, ext=hdu)
    else:
        data = None
    # return file
    return np.array(data), filename


def get_header(filename: str) -> drs_fits.Header:
    # load the header of the filename
    return drs_fits.read_header(PARAMS, filename, ext=0)


def get_calib(header: drs_fits.Header, key: str) -> Tuple[np.ndarray, str]:
    """
    Get a calibration file for a speific file and get

    :param filename: str, the filename
    :param key: str, the db key for the specific type of calibration
    """
    # get database
    calibdbm = drs_database.CalibrationDatabase(PARAMS)
    calibdbm.load_db()
    # get calib file
    cout = calibdbm.get_calib_file(key=key, header=header, nentries=1)
    # extract absolute filename from calibration database
    cfilename = os.path.join(PARAMS['DRS_CALIB_DB'], cout[0])
    # get data
    cdata = drs_fits.readfits(PARAMS, cfilename, ext=1)
    # return the data and the filename
    return cdata, cfilename


def get_obs_dirs() -> List[str]:
    # get database
    indexdbm = drs_database.IndexDatabase(PARAMS)
    indexdbm.load_db()
    # return observation directories
    new_obs_dirs = indexdbm.get_unique('OBS_DIR', condition='BLOCK_KIND="raw"')

    if len(new_obs_dirs) == 0:
        return []
    else:
        return list(new_obs_dirs)


def get_identifers(block_kind='red', obs_dir=None) -> List[str]:
    # get database
    indexdbm = drs_database.IndexDatabase(PARAMS)
    indexdbm.load_db()
    # set up condition
    if obs_dir is None:
        condition = 'BLOCK_KIND="{0}"'.format(block_kind)
    else:
        condition = 'BLOCK_KIND="{0}" AND OBS_DIR="{1}"'
        condition = condition.format(block_kind, obs_dir)

    condition += ' AND KW_IDENTIFIER IS NOT NULL'
    # return identifiers which conform to these filters
    newidentifiers = indexdbm.get_unique('KW_IDENTIFIER', condition=condition)

    if len(newidentifiers) == 0:
        return []
    else:
        return list(newidentifiers)


def get_bokeh_plot_dir(params, pyfile):
    # set path to bokeh subdir
    path = os.path.join(params['DRS_DATA_PLOT'], 'bokeh')
    # create path if it doesn't exist
    if not os.path.exists(path):
        os.mkdir(path)
    # return path + python filename
    return os.path.join(path, pyfile)


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":


    # _path = os.path.join(PARAMS['DRS_DATA_PLOT'], 'test.py')
    # _bplt = BokehPlot(PARAMS, 'test_plot', _path, 'My test plot')
    # _bplt.create(kwargs=dict(power=3, xlabel='x', ylabel='x^3'))
    # _bplt.run()

    _path = os.path.join(PARAMS['DRS_DATA_PLOT'], 'e2ds_plot.py')
    _bplt = BokehPlot(PARAMS, 'e2ds_plot', _path, 'E2DS plot')
    _bplt.create()
    _bplt.run()


# =============================================================================
# End of code
# =============================================================================
