#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-11-14 at 10:52

@author: cook
"""




def __main__(recipe, params):
    # ----------------------------------------------------------------------
    # Main Code
    # ----------------------------------------------------------------------
    mainname = __NAME__ + '._main()'
    # get database type
    db_type = params['INPUTS']['KIND']
    assetdir = params['DRS_DATA_ASSETS']
    # get the pseudo constants
    pconst = constants.pload()


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
