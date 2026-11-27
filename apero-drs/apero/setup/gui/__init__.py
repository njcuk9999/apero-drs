#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
apero.setup.gui - the APERO setup browser gui (apero_setup.py --gui)

Built on the generic aperocore.gui framework (like pogos_gui):

    - app: SetupGuiApp (the routes) and main()
    - commands: setup choices, form checks, the commands the gui runs
      (apero_setup.py, --update, --install_sh, apero_validate.py) and
      profile / config file helpers
    - probe: helpers run in a sub process with DRS_UCONFIG set (constants
      for the Docs tab, the state report for the Validate tab)
    - static/: the page, its css / js and the icon

The Info tab and the Docs guides are the apero-ri documentation pages
(documentation/ari/{version}/home/docs), so both share one source.

Created on 2026-11-27

@author: cook
"""

# =============================================================================
# End of code
# =============================================================================
