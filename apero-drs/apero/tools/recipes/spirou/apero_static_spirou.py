#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-26 at 09:40

@author: cook
"""
from aperocore import base
from aperocore import drs_lang
from aperocore.core import drs_log
from apero.utils import drs_startup
from apero.tools.module.static import static_detector
from apero.tools.module.static import static_wavelength
from apero.base import base as apero_base
from apero.tools.module.static import drs_static
from apero.tools.module.setup import drs_assets
from aperocore.core import drs_text

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_static_spirou.py'
__INSTRUMENT__ = 'SPIROU'
__PACKAGE__ = apero_base.__PACKAGE__
__version__ = apero_base.__version__
__authors__ = apero_base.__authors__
__date__ = apero_base.__date__
__release__ = apero_base.__release__
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
textentry = drs_lang.textentry


# =============================================================================
# Define functions
# =============================================================================
def main(**kwargs):
    """
    Main function for apero_changelog.py

    :param kwargs: any additional keywords

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
    # get static parmaeters from yaml file
    sparams = drs_static.load(params)
    # get mode from yaml file
    mode = sparams['mode']
    # override mode with inputs (if set)
    if not drs_text.null_text(params['INPUTS']['MODE'], ['None', '', 'Null']):
        mode = params['INPUTS']['MODE']
    # set up plotting (no plotting before this)
    recipe.plot.set_location()
    # -------------------------------------------------------------------------
    # first we must make sure our assets are up-to-date
    # -------------------------------------------------------------------------
    # now check whether we need to download the assets
    update_assets = drs_assets.check_local_assets(params)
    # if they need updating, update them now
    if update_assets:
        msg = 'Updating APERO assets'
        WLOG(None, 'info', msg)
        drs_assets.update_local_assets(params,
                                       tarfile=params.get('TARFILE', None))

    # -------------------------------------------------------------------------
    # detector static files
    # -------------------------------------------------------------------------
    #    amplifier bias model
    #    detector flat full
    #    hotpix_pp
    if mode in ['detector', 'All']:
        static_detector.main(params, recipe, sparams)
    # --------------------------------------------------------------------------
    # telluric static files
    # --------------------------------------------------------------------------
    #    excess_emissivity
    #    tapas_all_sp
    if mode in ['telluric', 'All']:
        pass

    # --------------------------------------------------------------------------
    # wavelength calibrations
    # --------------------------------------------------------------------------
    #   hollow cathode catalogue
    #   cavity length ll fit
    #   initial wave ref
    if mode in ['wavelength', 'All']:
        static_wavelength.main(params, recipe, sparams)


    # --------------------------------------------------------------------------
    # Update remote files based on changes here (if user agrees)
    # --------------------------------------------------------------------------
    drs_static.update_assets(params)

    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return locals()


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()

# =============================================================================
# End of code
# =============================================================================
