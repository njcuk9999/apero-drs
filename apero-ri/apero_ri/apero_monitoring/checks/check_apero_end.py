#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Reduced APERO check: APERO processing finished (APERO_END)."""

from typing import Tuple

import apero_ri.apero_monitoring.core.red_common as red_common
from apero_ri.apero_monitoring.core.core import AperoCheck
from apero_ri.apero_monitoring.core import contacts
from apero_ri.apero_monitoring.core import links


# =============================================================================
# Define variables
# =============================================================================
CHECK_NAME = 'APERO_END'
CHECK_HUMAN_NAME = 'APERO Processing Finished'
CHECK_TYPE = 'red'
INSTRUMENTS = ['NIRPS_HE', 'NIRPS_HA']

CHECK = AperoCheck(CHECK_NAME, CHECK_HUMAN_NAME, CHECK_TYPE, INSTRUMENTS)
CHECK.dependencies = ['BLANK', 'HAS_OBSDIR', 'MANUAL_START', 'APERO_START']

CHECK.description = """
If FALSE this normally means the manual trigger has crashed before APERO
processing finished.
"""

CHECK.what_to_do = f"""
If FALSE please [re-run the check]({links.RUN_CHECK}) with
--test=APERO_END.

If still FALSE please try re-running the manual trigger with
--only_apero_process=True and look for errors in the running code.

Please then locate the log file for apero_processing.py and email
<CONTACT:C1> with a copy of the log (and/or the location of the log file on
disk).
"""

clist1 = contacts.AperoCheckContactList()
clist1.add(contacts.NJC, starred=True)
clist1.add(contacts.LM)
clist1.add(contacts.EA)
CHECK.contact_list['C1'] = clist1

# Manual-trigger log status token checked by this check.
_STATUS = 'APERO_END'


# =============================================================================
# Define check function
# =============================================================================
def check_function(instrument: str, obs_dir: str,
                   aparams: dict, dbparams: dict) -> Tuple[bool, str]:
    """Return whether APERO processing finished for this obsdir."""
    _ = instrument, dbparams
    return red_common.check_manual_trigger_status(aparams, obs_dir, _STATUS)


# =============================================================================
# Must put the function to run for this check
# =============================================================================
CHECK.func = check_function


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    _instrument = 'NIRPS_HA'
    _obs_dir = '2021-01-01'
    _aparams = red_common.load_example_aparams(_instrument)
    _dbparams = dict()
    _check_dict = {dep: True for dep in CHECK.dependencies}
    CHECK(_instrument, _obs_dir, _aparams, _dbparams, check_dict=_check_dict)
    print(CHECK.report())


# =============================================================================
# End of code
# =============================================================================
