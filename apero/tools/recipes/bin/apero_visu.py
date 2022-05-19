#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2022-02-08

@author: cook
"""
import os

from apero.base import base
from apero.core import constants
from apero.core.core import drs_log
from apero.core.utils import drs_startup
from apero.tools.module.visulisation import visu_core


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_visu.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
ParamDict = constants.ParamDict


# =============================================================================
# Define functions
# =============================================================================
def main(**kwargs):
    """
    Main function for apero_explorer.py

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
    recipe, params = drs_startup.setup(__NAME__, __INSTRUMENT__, fkwargs,
                                       enable_plotter=False)
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
    Main function - using user inputs (or gui inputs) filters files and
    copies them to a new location

    :param instrument: string, the instrument name
    :type: str
    :return: returns the local namespace as a dictionary
    :rtype: dict
    """
    # deal with no mode set
    if 'MODE' not in params['INPUTS']:
        WLOG(params, '', 'Must set --mode')
        return drs_startup.return_locals(params, locals())

    # get mode
    mode = params['INPUTS']['MODE']

    # deal with options
    if mode == 'e2ds':
        # create path for tmp py file
        path = visu_core.get_bokeh_plot_dir(params, 'e2ds_plot.py')
        # get bokeh plotter instance
        bplt = visu_core.BokehPlot(params, 'e2ds_plot', path, 'E2DS plot')
        # create tmp py file
        bplt.create()
        # run bokeh server
        bplt.run()


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
